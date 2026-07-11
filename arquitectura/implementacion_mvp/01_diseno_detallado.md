# Hito 4 — Diseño Técnico Detallado (previo al código)

Este documento define **todo lo necesario para escribir el código y el IaC sin ambigüedad**: stack, contratos, esquemas de eventos, modelo de datos, la Saga paso a paso, parámetros de resiliencia, mocks e interfaces de los módulos Terraform.

---

## 1. Decisiones técnicas
| Tema | Decisión | Por qué |
|---|---|---|
| Lenguaje de apps | **Python** (FastAPI para OMS y mocks; función Python para AWS) | La clase usa Python en CI (flake8/pytest); rápido para contenedor + Lambda |
| OMS | **Azure Kubernetes Service (AKS)** — microservicio en contenedor | **Alinea con el C4 (Alternativa A, N2 dice AKS)** |
| Registro de imágenes | **Azure Container Registry (ACR)** Basic | AKS necesita un registry para las imágenes del OMS/mocks/bridge |
| Bus | **Azure Service Bus** (namespace Standard): 1 topic `orders-events` + suscripciones, DLQ nativa | Colas + DLQ + topics para EDA; DLQ integrada |
| Datos transaccionales | **Azure SQL** (Basic) | ACID para reserva atómica y patrón Outbox; relacional canónico |
| Read model (CQRS) | Tabla de proyección en la misma Azure SQL | Simplicidad del MVP; se lee, no se comanda |
| Observabilidad | **Azure Log Analytics** (Container Insights de AKS) + correlation ID | Observabilidad del clúster y de la app |
| Última milla | **AWS Lambda** (Python) disparada por el evento | Serverless, free tier |
| Sync móvil | **AWS DynamoDB** (on-demand) | NoSQL para estado de entrega |
| Mocks WMS/ERP + bridge | **Deployments en el mismo AKS** (FastAPI stub + worker) con parámetro de "modo" | Comparten el node pool → coherente con AKS y más barato que servicios sueltos |
| Puente Azure→AWS | **Bridge worker (deployment en AKS) → SQS (AWS) → Lambda** — ver `02_afinamiento_tecnico.md §1` | Durable (SQS + DLQ), barato, 100% IaC |

> **Nota de coherencia:** el OMS, los mocks WMS/ERP y el bridge corren como **deployments/services dentro de un mismo clúster AKS** (un solo node pool pequeño). Así se respeta el C4 (que dice AKS) y se mantiene el costo bajo.

> **Bridge intercloud (decidido en 02 §1):** un worker liviano en Azure lee del Service Bus y reenvía a una cola **SQS**; la Lambda se dispara por SQS (con DLQ). En local, el `ConsolePublisher` del OMS imprime el evento y el bridge queda listo en IaC.

## 2. Contrato de API del OMS (REST)
| Método | Ruta | Cuerpo / Params | Respuesta | RF |
|---|---|---|---|---|
| `POST` | `/v1/ordenes` | `Idempotency-Key` (header) + orden (cliente, líneas, ventana, SLA) | `201` con `orderId` interno | RF-01, RF-04 |
| `GET` | `/v1/ordenes/{orderId}` | — | Estado canónico + inventario (read model) | RF-10 |
| `POST` | `/v1/ordenes/{orderId}/cancelar` | `Idempotency-Key` | `200` cancelada (idempotente) | RF-04 |
| `GET` | `/health` | — | `200` liveness | — |

Reglas: toda escritura exige `Idempotency-Key`; si se repite la misma key → devuelve el resultado original sin re-ejecutar (RF-04). Dedup adicional por **hash de contenido** (cliente+líneas+ventana) → detecta duplicado con otra key (RF-03).

## 3. Esquemas de eventos canónicos (publicados al bus)
Todos llevan `eventId` (para idempotencia del consumidor), `correlationId`, `timestamp`, `type`, `version`, `payload`.

| Evento | Cuándo | Payload clave | Consumidores |
|---|---|---|---|
| `OrdenValidada` | tras validar/dedup | orderId, cliente, líneas | (interno Saga) |
| `InventarioReservado` | reserva OK | orderId, sku, cantidad | última milla |
| `InventarioLiberado` | compensación | orderId, motivo | (auditoría) |
| `OrdenLista` | valorización OK | orderId, estado="Lista" | última milla, portal |
| `OrdenFallida` | Saga aborta | orderId, causa | portal/CRM |
| `OrdenCancelada` | cancelación del cliente | orderId, causa | portal/CRM, última milla |

## 4. Modelo de datos (Azure SQL)
```
orders(order_id PK, client_id, channel, status, sla, window, content_hash, created_at)
order_lines(id PK, order_id FK, sku, qty)
idempotency_keys(key PK, order_id, response_json, created_at)
inventory(sku PK, available_qty, reserved_qty)
reservations(id PK, order_id FK, sku, qty, status)   -- status: Reservado|Liberado
outbox(id PK, event_id, type, payload_json, published bit, created_at)
audit_movements(id PK, order_id, type, actor, reason, correlation_id, at)
read_model_orders(order_id PK, status, inventory_state, updated_at)  -- CQRS
```
- **Dedup:** `content_hash` (cliente + destinatario + ventana + líneas) con índice; la búsqueda de duplicados **excluye órdenes en estado terminal** (Cancelada/Fallida/Rechazada) para no bloquear al cliente.
- **Idempotencia:** tabla `idempotency_keys` guarda la respuesta original; el `commit` maneja el conflicto de clave (condición de carrera) devolviendo la respuesta del ganador.
- **Outbox:** el evento se escribe en `outbox` en la **misma transacción** que el estado; un publicador lo envía al bus y marca `published`.

## 5. Máquina de estados de la orden
```
Recibida → Validada → Reservando → Reservada → Lista
                          │            │
                          └→ Rechazada └→ (compensación) → Fallida
Entregada  (la reporta última milla)
Cancelada  (desde Validada/Reservando/Reservada/Lista, idempotente; compensa reservas)
```
Transiciones inválidas se rechazan (p. ej. Entregada→Reservada) — RF-05.

## 6. La Saga orquestada, paso a paso (con compensación)
```
1. POST /v1/ordenes  →  dedup + idempotencia  →  Validada  (publica OrdenValidada, vía outbox)
2. Saga: reservar inventario local (tabla inventory/reservations)  →  Reservando
3. Saga → WMS mock: reservar físico
      3a. WMS 'ok'    → continúa
      3b. WMS 'slow'  → Timeout → Circuit Breaker → Retry(backoff+jitter)
      3c. WMS 'down'  → agota retries → orden queda 'Reservando' encolada (no se pierde) → RF-11
4. Saga → ERP mock: valorizar
      4a. ERP 'accept' → Reservada → Lista (publica InventarioReservado + OrdenLista)
      4b. ERP 'reject' → COMPENSACIÓN: liberar reserva (inventory/reservations),
                          publica InventarioLiberado, estado → Fallida
5. Toda transición escribe en audit_movements con correlation_id.
```

## 7. Parámetros de resiliencia (config, no hardcode)
| Parámetro | Valor MVP | Aplica a |
|---|---|---|
| Timeout llamada WMS/ERP | 2 s | Saga → mocks |
| Circuit Breaker: umbral | 3 fallos consecutivos → abre | Saga → WMS |
| Circuit Breaker: half-open | tras 30 s prueba 1 llamada | Saga → WMS |
| Retry: intentos | 3 | WMS/ERP |
| Retry: backoff | exponencial 1s→2s→4s + jitter | WMS/ERP |
| DLQ | Service Bus DLQ nativa; alerta si backlog > 0 | bus |
| Idempotencia consumidor | descarta `eventId` ya procesado (tabla en DynamoDB) | Lambda |

## 8. Comportamiento de los mocks
- **WMS mock** `POST /reservar?modo=ok|slow|down`: `ok`=200 reserva; `slow`=responde a los 5 s (dispara timeout); `down`=503.
- **ERP mock** `POST /valorizar?modo=accept|reject`: `accept`=200; `reject`=422 (dispara compensación).
- El modo se pasa por variable de entorno o query, para demostrar cada escenario en vivo.

## 9. Interfaces de los módulos Terraform (inputs → outputs)
| Módulo | Inputs clave | Outputs |
|---|---|---|
| `azure-aks` | cluster_name, node_vm_size, node_count, log_analytics_id (Container Insights) | kube_host, kube_config (sensitive), cluster_id, kubelet_identity |
| `azure-acr` | registry_name, sku=Basic, aks_kubelet_identity (AcrPull) | login_server, acr_id |
| `azure-servicebus` | namespace_name, topic_name, sku=Standard | connection_string (sensitive), topic_id, dlq |
| `azure-sql` | server_name, db_name, sku=Basic, admin_login | sql_connection_string (sensitive) |
| `azure-observability` | workspace_name, retention_days | workspace_id, workspace_key (sensitive) |
| `azure-keyvault` | vault_name, secrets{}, aks_identity (get/list) | vault_uri, vault_id |
| `k8s-workloads` (kubernetes/helm provider) | kube_config, acr_login_server, image_tag, env/secret refs | deployments: oms, wms-mock, erp-mock, bridge |
| `aws-lambda` | function_name, handler, runtime=python3.12, sqs_arn (event source), dynamodb_arn | function_arn |
| `aws-dynamodb` | table_name, hash_key, billing=PAY_PER_REQUEST | table_arn, table_name |
| `aws-sqs` | queue_name, dlq (redrive maxReceiveCount=3) | queue_url, queue_arn, dlq_arn |

`environments/dev/main.tf` compone los módulos: crea AKS + ACR (con AcrPull a la identidad del kubelet), despliega los workloads en AKS, y en AWS crea SQS→Lambda→DynamoDB. El **bridge** (deployment en AKS) recibe por Key Vault la URL de la `aws-sqs` (output cross-cloud) y las credenciales de envío.

## 10. Variables y tfvars (parametrización, sin tocar módulos)
```hcl
# terraform.tfvars (ejemplo)
owner_alias  = "grupo6"
environment  = "dev"
location     = "eastus2"
cost_center  = "CC-UTEC-M04"
aws_region   = "us-east-1"
```
El naming de recursos incorpora `owner_alias` + `environment` para no colisionar (patrón del profe).

## 11. Políticas OPA/Rego (validadas con conftest antes del apply)
| Política | Qué exige |
|---|---|
| `required_tags.rego` | Todo recurso con tags `Environment, ManagedBy, Owner, CostCenter` |
| `storage_secure.rego` | Storage/SQL sin acceso público, TLS 1.2+ |
| `resource_limits.rego` | Node pool AKS con `node_count` acotado (≤ 3, evita sobredimensionar) |
| `allowed_location.rego` | Región en {eastus, eastus2} (Azure) |

## 12. CI (GitHub Actions — Módulo 5, mínimo de validación)
`.github/workflows/ci.yml`, dispara en `push` y `pull_request`:
1. `terraform fmt -check`
2. `terraform init -backend=false`
3. `terraform validate`
4. (apps) `flake8` + `pytest` del OMS

> No hace `plan` ni `apply` ni `conftest` en CI (requieren credenciales de nube). El gate `conftest` contra el `plan.json` se corre **en el momento del despliegue** (ver runbook del README). Coherente con "todo listo para desplegar, deploy al final".

---

## Orden de construcción propuesto
1. **Apps** (OMS con dedup/idempotencia/Saga/CQRS · mocks WMS/ERP · Lambda) + tests unitarios.
2. **Terraform** (módulos → environments/dev → policy).
3. **CI** (.github/workflows/ci.yml).
4. **Costos** (`costos_estimados.md`) + **README** de despliegue (paso a paso para el `apply` final).
5. **Revisión final** contra el enunciado, y recién ahí el `terraform apply`.

*Diseño detallado — Hito 4 · Grupo 6 RutaExpress*

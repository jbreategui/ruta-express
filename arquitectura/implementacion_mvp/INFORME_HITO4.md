# Informe — Hito 4: TO BE Implementación
**Proyecto:** RutaExpress Fulfillment & Transporte · **Grupo 6** · Programa de Arquitectura de Soluciones Multinube (UTEC)
**Elaboración:** equipo Grupo 6

---

## 1. Resumen ejecutivo
Se implementó un **MVP** de la **Alternativa A (orquestada)** recomendada en el Hito 3: una plataforma logística **multinube (Azure + AWS)**, desplegable **100% con IaC (Terraform)**, que demuestra **5 patrones de arquitectura** sobre la ruta crítica del caso (los duplicados de Cyber Days y la caída del WMS). Se usan **API mock** para simular los sistemas externos (WMS/ERP), como permite el enunciado.

El MVP está **completo y validado localmente** (tests + `terraform validate`). El despliegue a la nube es el paso final, a ejecutar con credenciales de estudiante (Azure for Students + AWS propia), sin gasto real gracias a la disciplina de `terraform destroy`.

## 2. Cumplimiento del enunciado
| Requisito del Hito 4 | Cómo se cumple |
|---|---|
| MVP del diseño TO-BE recomendado | Alternativa A (orquestada) — código + IaC |
| **Mínimo 2 nubes** | **Azure** (AKS, Service Bus, SQL, Log Analytics, Key Vault) + **AWS** (Lambda, DynamoDB, SQS) |
| **Mínimo 3 patrones** | **5**: Microservicios, EDA, Saga, CQRS, Resiliencia |
| **Despliegue 100% con IaC** | Terraform: 12 módulos + `environments/dev` + `policy` (OPA/Rego) |
| **Costos por nube al mes** | Ver §7 y `costos_estimados.md` |
| **API mock permitido** | Mocks WMS/ERP (modos ok/slow/down · accept/reject) |

## 3. Alcance del MVP
El MVP implementa un **subconjunto** de los 29 RF: la **ruta crítica** (~14 RF: RF-01…08, RF-10, RF-11, RF-14, RF-16, RF-22, RF-23). El resto queda cubierto **en el diseño (Hito 3)** y como trabajo futuro. Precisiones honestas: **RF-09 (reconciliación de inventario) NO está implementado** en el MVP (solo en el diseño); **RF-02** es validación básica (tipado, cantidades) sin catálogo de SKU ni cobertura de ventana; **RF-05** valida transiciones en cancelación. Esto es lo esperado en un prototipo/MVP.

- **Dentro:** OMS (dedup, idempotencia, Saga, CQRS, resiliencia) · bus con DLQ · última milla en AWS · mocks WMS/ERP · IaC de ambas nubes · CI de validación.
- **Fuera (trabajo futuro):** GCP/analítica · portal/CRM/TMS reales · GitOps · multi-región/DR · API Management/WAF · Event Sourcing completo (Alternativa B).

## 4. Arquitectura implementada
Ruta crítica: **crear orden → dedup + idempotencia → Saga (reserva) → WMS "caído" → Circuit Breaker/Retry → evento al bus → bridge → SQS → Lambda última milla**, con **compensación** si el ERP rechaza y **DLQ** si el consumidor falla.

| Componente | Nube / Tecnología | Responsabilidad |
|---|---|---|
| OMS | Azure AKS (deployment) | Órdenes, dedup, idempotencia, Saga, CQRS, resiliencia |
| Bus de Eventos | Azure Service Bus (+DLQ) | EDA, cola, DLQ |
| BD + read model | Azure SQL (private endpoint) | Estado, outbox, proyección CQRS |
| Observabilidad | Azure Log Analytics | Logs, correlation ID |
| Mocks WMS/ERP | AKS (deployments) | Simulan sistemas on-prem |
| Bridge | AKS (deployment) → AWS SQS | Puente intercloud durable |
| Última milla | AWS Lambda | Consume SQS, dedup por eventId, DynamoDB |
| Sync móvil | AWS DynamoDB | Estado de entrega |

*(Diagramas C4 niveles 1-2-3 y de secuencia: ver `../diseno_solucion/`.)*

## 5. Patrones de arquitectura aplicados (5)
| Patrón | Dónde |
|---|---|
| **Microservicios** | OMS, última milla, mocks y bridge como servicios independientes |
| **EDA** | Eventos por Service Bus (patrón Outbox desde el OMS) |
| **Saga (orquestada)** | Reserva + valorización con **compensación** al rechazo del ERP |
| **CQRS** | Comando (crear orden) separado de la consulta (read model) |
| **Resiliencia** | Circuit Breaker + Timeout + Retry (backoff+jitter) hacia el WMS; DLQ + retry en el bus y en SQS |

## 6. Infraestructura como código (100% IaC)
**Terraform**, siguiendo el lab del profe (Módulo 4): `modules/` reutilizables + `environments/dev` + `policy/`.
- **12 módulos:** azure-network, azure-aks, azure-acr, azure-servicebus, azure-sql, azure-observability, azure-keyvault, aws-sqs, aws-dynamodb, aws-lambda, aws-bridge-identity, k8s-workloads.
- **4 políticas OPA/Rego** (gate antes del apply): tags obligatorios, región permitida, SQL sin acceso público + TLS 1.2, límite de node pool.
- **Apply en 2 etapas** (infra → build/push de imágenes → workloads), documentado en el `README.md`.

## 7. Costos estimados por nube (nivel dev)
Precios de lista aprox. (a confirmar en calculadoras oficiales). Detalle en `costos_estimados.md`.

| Nube | USD/mes (encendido el mes completo) |
|---|---|
| Azure (AKS node pool + ACR + Service Bus + SQL + Log Analytics + Key Vault + Private Endpoint + IP pública LB) | ~60 – 76 |
| AWS (Lambda + DynamoDB + SQS, free tier) | ~0 – 1 |
| **Total** | **~60 – 77** |

> **Costo real con `terraform destroy` al terminar cada sesión: pocos dólares.** Con **Azure for Students** ($100 crédito, sin tarjeta) y **AWS propia** (free tier), **no hay gasto de dinero real**.

## 8. Seguridad (Módulo 6 · lineamientos SEG)
- **Cero secretos hardcodeados:** cadenas de SQL/Service Bus/SQS inyectadas por `kubernetes_secret` desde Terraform; `sensitive=true`; `sql_admin_password` fuera del repo (variable de entorno).
- **Mínimo privilegio:** Lambda con rol IAM acotado; usuario IAM del bridge solo `sqs:SendMessage`; AKS jala del ACR por identidad (AcrPull), sin llaves; **Service Bus con reglas Send (OMS) y Listen (bridge)** por topic, sin la Root manage key.
- **Red:** Azure SQL **sin acceso público**, accesible solo por **private endpoint** dentro de la VNet (AKS en Azure CNI); TLS 1.2.

## 9. Verificación (lo que está probado)
| Qué | Resultado |
|---|---|
| OMS — lint (flake8) | Limpio |
| OMS — tests (pytest) | **20/20 pasan** (dedup con ventana, idempotencia sin reserva huérfana, Saga feliz, compensación con liberación del WMS, orden multilínea, cancelación con compensación, reserva atómica sin sobreventa, WMS caído, stock insuficiente, resiliencia) |
| Terraform — `validate` | **Success** (12 módulos, 2 nubes) |
| CI (GitHub Actions) | Valida IaC + apps en cada push/PR (no despliega) |

## 10. Limitaciones y trabajo futuro (honesto)
- **Revisión crítica aplicada:** una revisión adversarial detectó bugs de lógica en la Saga (compensación incompleta, orden multilínea que dejaba stock colgado, cancelación sin compensar) y afirmaciones exageradas en la doc; **se corrigieron** y se agregaron tests que los cubren (17 en total). Este informe refleja el estado ya corregido.
- **No desplegado aún**: el `apply` es el paso final; requiere credenciales y probablemente depuración de integración (cuota de vCPU en cuenta de estudiante, build de imágenes, apply de dos etapas).
- **Runtime no probado** para mocks, bridge y Lambda (solo el OMS tiene suite de tests). Se validan al desplegar.
- **No implementado en el MVP:** RF-09 (reconciliación de inventario) — solo en el diseño; validación de reglas logísticas de RF-02 es básica.
- **Trabajo futuro (bloque C):** Key Vault CSI + Workload Identity (en vez de kubernetes_secret), API Management/WAF delante del OMS, GitOps con Argo CD, GCP/analítica, DR multi-región.

## 11. Cómo desplegar y evidenciar
- **Despliegue:** runbook paso a paso en `README.md` (apply 2 etapas + build de imágenes + destroy).
- **Evidencia:** qué capturar en cada paso y qué prueba, en `guia_evidencia.md`.

---
*Informe Hito 4 — Grupo 6 RutaExpress*

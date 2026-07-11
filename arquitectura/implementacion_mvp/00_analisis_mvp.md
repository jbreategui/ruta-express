# Hito 4 — Análisis y Alcance del MVP

> **Nota:** este es el documento de **análisis inicial** del alcance. Para las cifras **finales** de
> **costos** ver `costos_estimados.md`, y para el **alcance final de RF** ver `INFORME_HITO4.md` §3
> (fuente de verdad). La decisión final de cómputo fue **AKS** (no Container Apps).

**Base:** Alternativa A (orquestada) recomendada en el Hito 3. Lineamiento de implementación tomado de las clases: **Terraform + HCL** (Módulo 4), estructura `modules/ + environments/ + policy/`, y **GitHub Actions** para un CI de validación (Módulo 5).
**Regla del enunciado:** prototipo/MVP · **mínimo 2 nubes** · **mínimo 3 patrones** · **100% IaC** · **costos por nube al mes** · API mock permitido.

---

## 1. Qué demuestra el MVP (la ruta crítica del caso)
El MVP reproduce el flujo donde RutaExpress más sufrió — **duplicados de Cyber Days + caída del WMS de 6 h** — de punta a punta:

1. **Cliente crea una orden** → API del OMS (Azure AKS).
2. **Deduplicación + idempotencia** (hash de contenido + idempotency key) → ataca los **32k duplicados** *(RF-03, RF-04)*.
3. **Validación** y **estado canónico** "Validada" *(RF-02, RF-05)*.
4. **Saga: reserva de inventario** → llama al **WMS mock**.
5. El WMS mock **simula lentitud/caída** → el OMS aplica **Circuit Breaker + Timeout + Retry (backoff+jitter)** → ataca el incidente de **6 h** *(RF-11)*.
6. Reserva OK → **publica evento (patrón Outbox) al bus** (Service Bus/Event Hubs) *(RF-14, EDA)*.
7. Si el **ERP mock rechaza** la valorización → la **Saga compensa** (libera la reserva) *(RF-08)*.
8. **AWS Lambda "última milla"** consume el evento del bus → registra en **DynamoDB** *(RF-22, RF-23)*.
9. **Consulta CQRS**: read model del estado de la orden *(RF-10)*.
10. Si el consumidor falla → **DLQ + retry** (sin descartar) *(RF-16, resiliencia)*.

> Con este único flujo se tocan los 3 riesgos del anexo (disponibilidad, integridad, operación) y se demuestran 5 patrones.

## 2. Alcance IN / OUT
> **El MVP implementa un SUBCONJUNTO de los 29 RF** — la **ruta crítica** del caso (**~14 RF**: RF-01…08, RF-10, RF-11, RF-14, RF-16, RF-22, RF-23; **RF-09 queda solo en diseño**). El resto queda cubierto **en el diseño** (Hito 3) y como trabajo futuro, según corresponde a un prototipo/MVP. (Alcance final en `INFORME_HITO4.md` §3.)

**Dentro (MVP):** OMS con dedup/idempotencia/Saga/estado/CQRS · bus con DLQ · última milla en AWS · mocks WMS/ERP · IaC completo de ambas nubes · CI de validación · tabla de costos.
**Fuera (queda como "trabajo futuro"):** GCP/analítica · portal/CRM/TMS reales · GitOps con Argo CD · Canary/Blue-Green · Feature Flags · Event Sourcing completo (eso es la Alternativa B) · multi-región/DR real.

## 3. Componentes (responsabilidad · nube · patrón · RF)
| Componente | Nube / Tecnología | Responsabilidad | Patrón | RF |
|---|---|---|---|---|
| **OMS** | Azure **AKS** (deployment) | API de órdenes, dedup, idempotencia, estado, Saga, CQRS | Microservicio, Saga, CQRS | RF-01…08, 10 (RF-09 solo diseño) |
| **Bus de Eventos** | Azure Service Bus (+DLQ) | Eventos canónicos, cola, DLQ, retry | EDA, resiliencia | RF-14, RF-16 |
| **BD transaccional + read model** | Azure SQL | Estado, outbox, proyección de consulta | CQRS | RF-05, RF-10 |
| **Observabilidad** | Azure Log Analytics (Container Insights) | Logs, correlation ID | — | RNF-05, RNF-15 |
| **Bridge intercloud** | AKS (deployment) → AWS SQS | Reenvía eventos del bus a AWS (durable) | Adaptador, store-and-forward | RF-14 |
| **Última milla** | AWS Lambda | Consume evento (por SQS), dedup por eventId, store-and-forward **del borde backend** | Microservicio, EDA | RF-22/23 *(lado backend; el offline móvil queda en diseño)* |
| **Sync móvil** | AWS DynamoDB | Estado de entrega/sincronización | — | RF-22/23 *(backend)* |
| **Mock WMS** | AKS (deployment, stub) | Simula reserva física; modo éxito/lento/caído | (habilita probar resiliencia) | RF-11 |
| **Mock ERP** | AKS (deployment, stub) | Simula valorización; modo aceptar/rechazar | (habilita probar Saga) | RF-08 |

## 4. Patrones demostrados (≥3 — tenemos 5)
1. **Microservicios** — OMS, última milla y mocks como servicios independientes.
2. **EDA** — comunicación por eventos vía Service Bus.
3. **Saga (orquestada)** — reserva + valorización con **compensación** al fallar.
4. **CQRS** — comando (crear orden) separado de la consulta (read model).
5. **Patrones de Resiliencia** — Circuit Breaker + Timeout + Retry (backoff+jitter) hacia el WMS, y DLQ+retry en el bus.

## 5. Estrategia de mocks (API mock, permitido por el enunciado)
- **WMS mock** y **ERP mock** son endpoints mínimos con un parámetro de "modo" para forzar escenarios:
  - WMS: `ok` (reserva), `slow` (dispara Timeout/Circuit Breaker), `down` (dispara Retry + encolado).
  - ERP: `accept` (valorización OK) / `reject` (dispara la **compensación** de la Saga).
- Así la demo prueba en vivo la resiliencia y la Saga sin depender de sistemas reales.

## 6. Estructura IaC (fiel al lab del profe — Módulo 4 Sesión 3)
```
implementacion_mvp/
├── terraform/
│   ├── modules/
│   │   ├── azure-aks/              # clúster (OMS, mocks y bridge como deployments)
│   │   ├── azure-acr/             # registro de imágenes
│   │   ├── azure-servicebus/      # topic + DLQ
│   │   ├── azure-sql/            # Azure SQL (estado + read model)
│   │   ├── azure-network/        # VNet, subredes, private endpoints
│   │   ├── azure-observability/   # Log Analytics / Container Insights
│   │   ├── azure-keyvault/        # secretos
│   │   ├── k8s-workloads/         # deployments en AKS (provider kubernetes/helm)
│   │   ├── aws-sqs/              # cola intercloud + DLQ
│   │   ├── aws-lambda/           # última milla
│   │   ├── aws-dynamodb/
│   │   └── aws-bridge-identity/  # rol IAM del bridge (mínimo privilegio)
│   ├── environments/dev/
│   │   ├── providers.tf             # azurerm ~> 4.66, aws ~> 6.39
│   │   ├── main.tf                  # compone los módulos
│   │   ├── variables.tf
│   │   ├── terraform.tfvars         # owner_alias, location, cost_center
│   │   └── outputs.tf
│   └── policy/                      # OPA/Rego + conftest (diferenciador)
│       ├── required_tags.rego       # Environment, ManagedBy, Owner, CostCenter
│       ├── storage_secure.rego      # sin acceso público, TLS 1.2+
│       ├── resource_limits.rego     # node_count acotado (≤ 3)
│       └── allowed_location.rego
├── apps/
│   ├── oms/                         # microservicio OMS
│   ├── ultima-milla/               # función AWS
│   └── mocks/                       # WMS / ERP
├── .github/workflows/ci.yml         # terraform fmt/validate/plan (Módulo 5)
├── costos_estimados.md
└── README.md
```
**Flujo (mantra del profe):** `init → validate → plan -out → conftest test → apply → verificar → destroy`.
**Limpieza:** siempre `terraform destroy` acotado — nunca `az group delete` a ciegas.

## 7. Estimación de costos (enfoque)
SKUs de nivel **dev**, con scale-to-zero donde se pueda. Estimación preliminar (a confirmar con las calculadoras oficiales al construir):

> **La tabla final y detallada de costos está en `costos_estimados.md`** (fuente de verdad,
> ~60–77 USD/mes por la elección de **AKS**). Este resumen se mantiene solo como orientación.

| Recurso | Nube | SKU dev | Costo aprox. USD/mes |
|---|---|---|---|
| AKS (OMS + 2 mocks + bridge como deployments) | Azure | 1 nodo B-series | ~30 – 40 |
| Service Bus | Azure | Standard | ~10 |
| Azure SQL | Azure | Basic / serverless | 5 – 10 |
| Log Analytics | Azure | Pago por GB (poco volumen) | 2 – 5 |
| Lambda | AWS | Free tier / on-demand | ~0 – 1 |
| DynamoDB | AWS | On-demand | ~0 – 1 |
| **Total estimado (dev)** | | | **~60 – 77 USD/mes** |

> El costo real en un lab con `destroy` al terminar cada sesión es casi nulo; la tabla es el "costo si quedara encendido un mes".

## 8. Decisiones tomadas
| # | Decisión | Resuelto |
|---|---|---|
| 1 | **Nubes del MVP** | **Azure + AWS** (hay suscripciones en ambas). |
| 2 | **Nivel de entrega** | **Todo listo para desplegar** (IaC + código completos, `terraform validate/plan` en verde). El `terraform apply` a la nube es el **paso final**, se hará al cierre, no durante la construcción. |

> Consecuencia: construimos y validamos localmente (fmt, validate, plan, conftest) sin gastar en nube. El despliegue queda como último paso, controlado y con confirmación.

---
*Análisis del alcance — Hito 4 · Grupo 6 RutaExpress*

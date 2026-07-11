## Stack Tecnológico Multinube para RutaExpress

> Nota: el nombre del archivo se conserva por compatibilidad con la carpeta original, pero el contenido aplica a una arquitectura multinube Azure + AWS + GCP alineada al caso RutaExpress.

## Principio general

- Azure se prioriza para APIs, OMS, TMS y gobierno de integración porque el caso ya ubica Azure API Management, AKS y TMS en Azure.
- AWS se prioriza para última milla móvil, evidencias, IoT y almacenamiento de objetos porque el caso ya ubica App de Conductores (APP-15), DynamoDB, S3 e IoT Core en AWS.
- GCP se prioriza para optimización de rutas, analítica, datos y ML porque el caso ya ubica optimizador y analítica en GCP.
- On premises se mantiene durante transición para WMS Principal (On Premises) (APP-06), WMS Satélite (On Premises local) (APP-07) y ERP Financiero (On Premises) (APP-25), con integración segura.

## Azure

### Cómputo y contenedores

- Azure Kubernetes Service (AKS): OMS centralizado / Orquestador de Pedidos (APP-02), servicios de validación, APIs de dominio y componentes de integración.
- Azure Container Registry: repositorio de imágenes para servicios desplegados en AKS.
- Azure Functions: tareas event-driven ligeras o automatizaciones puntuales.

### Integración

- Azure API Management: gateway de APIs, políticas, rate limiting, OAuth, versionamiento y publicación de contratos.
- Azure Event Hubs: hub principal para Bus de Eventos Central (PLT-03), especialmente para eventos de orden, inventario, tracking y liquidación.
- Azure Service Bus: colas, DLQ y patrones request/command cuando se requiera control transaccional.

### Datos

- Azure SQL Database / SQL Managed Instance: datos transaccionales del OMS, catálogos operativos y estados canónicos.
- Azure Cache for Redis: caché de lecturas frecuentes, catálogos y configuraciones de SLA.

### Seguridad y gobierno

- Microsoft Entra ID: identidad federada y OAuth/OIDC.
- Azure Key Vault: secretos, certificados y llaves.
- Azure Monitor, Application Insights y Log Analytics: observabilidad base de servicios Azure.
- Azure Policy y Terraform: gobierno e infraestructura como código.

## AWS

### Cómputo y móvil

- ECS Fargate: backend de App de Conductores (APP-15) cuando se requieran servicios siempre activos.
- Lambda: procesamiento puntual de eventos, validaciones ligeras y automatización.

### Datos y evidencias

- DynamoDB: eventos móviles, estado local sincronizado y datos de baja latencia para la app.
- Amazon S3: Almacenamiento Evidencias (S3) (APP-16) para fotos, firmas y documentos.
- KMS: cifrado de evidencias y datos sensibles.

### Integración

- EventBridge: integración de eventos AWS con Bus de Eventos Central (PLT-03).
- SQS: colas de reintento, buffering y DLQ para backend móvil.
- SNS: notificaciones internas o fan-out.
- Kinesis: streaming de eventos móviles o tracking cuando aplique.

### Observabilidad y seguridad

- CloudWatch: métricas, logs y alarmas.
- X-Ray: trazas de servicios AWS.
- IAM: roles y políticas de mínimo privilegio.
- Secrets Manager / Systems Manager Parameter Store: secretos y configuración segura.
- AWS WAF: protección de endpoints públicos si se exponen en AWS.

## GCP

### Optimización, analítica y ML

- GKE Autopilot o Cloud Run: servicios de optimización dinámica de rutas.
- Pub/Sub: eventos para optimización y analítica.
- Dataflow: procesamiento streaming.
- BigQuery: analítica operacional, SLA, rutas, entregas, excepciones y liquidación.
- Vertex AI: modelos predictivos para rutas, excepciones y demanda.

### Observabilidad y gobierno

- Cloud Logging y Cloud Trace: logs y trazas de servicios GCP.
- Cloud Monitoring: métricas y alertas.
- Secret Manager: secretos de servicios GCP.

## On premises y conectividad

- WMS Principal (On Premises) (APP-06): integración transicional mediante APIs/eventos, backpressure y circuit breaker.
- WMS Satélite (On Premises local) (APP-07): modo local con reconciliación al reconectar.
- ERP Financiero (On Premises) (APP-25): integración segura para inventario valorizado y liquidación.
- VPN site-to-site o conectividad privada equivalente: conexión segura entre Azure, AWS, GCP y on premises.

## Patrones recomendados

- Microservicios por dominio.
- Domain-Driven Design.
- Event-Driven Architecture.
- API Gateway.
- Outbox/Inbox para publicación confiable de eventos.
- Idempotency Key para órdenes, reservas y tracking.
- Saga para procesos largos de orden-inventario-despacho-liquidación.
- Circuit Breaker, Retry, Timeout y Backpressure.
- Dead-letter Queue para mensajes no procesables.
- Store-and-forward para App de Conductores (APP-15).
- CQRS cuando las consultas operativas y tableros requieran modelos de lectura separados.

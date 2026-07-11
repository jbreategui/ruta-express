# Lineamientos de Arquitectura Aplicados — Matriz de Trazabilidad

**Fuente:** `../carpetas_adicionales/lineamientos/` (ARQ, ESC, INT, OBS, SEG).
**Cómo leer:** cada lineamiento → dónde está aplicado en el diseño. "A" = `alternativa_A_orquestada/`, "B" = `alternativa_B_coreografiada/`, "Anexo" = `anexos/despliegue_red_seguridad.md`. Aplica a **ambas alternativas** salvo indicación.

## ARQ — Arquitectura
| Código | Lineamiento (resumen) | Dónde se aplica |
|---|---|---|
| ARQ-01 | Separación por dominios logísticos | N2 de A y B: contenedores por dominio (órdenes, inventario, integración, última milla, evidencias, analítica) |
| ARQ-02 | APP-02 evoluciona a OMS sin nuevo ID | N2: OMS/Servicio de Órdenes = APP-02 (tabla de trazabilidad) |
| ARQ-03 | Reglas de negocio fuera de canales/portales | N2-A: el OMS concentra validación, estado y la Saga (RF-01…08); el portal y la app solo consumen. N3-A muestra la Saga orquestando la reserva |
| ARQ-04 | Responsabilidad única y ownership | Tablas "responsabilidad" de cada N2/N3 |
| ARQ-05 | Contratos explícitos sobre dependencias implícitas | ADR-05 (API-First); RF-12; contratos de evento versionados |
| ARQ-06 | Evitar acoplamiento fuerte entre sistemas | Bus de eventos desacopla (N2); ADR-03; el evento elimina el acoplamiento temporal |
| ARQ-07 | Evolución con versionamiento de APIs/eventos | apim /v1 (N2); RF-12; tolerancia al cambio en eventos |
| ARQ-08 | Core vs transversales (obs, IAM, secretos, IaC) | N2: IAM y Observabilidad como contenedores transversales (cajas grises) |
| ARQ-09 | Operación transicional con WMS/ERP AS-IS | N3-A: Adaptador de Transición WMS (RF-11); N2-B: Adaptadores WMS/ERP; RF-21 |
| ARQ-10 | Decisiones documentadas con ADR | `decisiones_diseño.md` (ADR-01…09, con opciones descartadas) |

## ESC — Escalabilidad
| Código | Lineamiento (resumen) | Dónde se aplica |
|---|---|---|
| ESC-01 | Dimensionar con la volumetría del caso (68k/180k/210k/130k) | RNF-02, RNF-04, RNF-16, RNF-27 |
| ESC-02 | Objetivos de latencia por proceso crítico | RNF-02 (<500 ms), RNF-03 (<2 s), RNF-11 (<1 s), RNF-22 (<5 min) |
| ESC-03 | Stateless escala horizontal | N2: servicios en AKS/ECS/Lambda; el estado vive en SQL/DynamoDB/log |
| ESC-04 | Lo pesado/diferible va asíncrono | N2: todo flujo no interactivo pasa por el bus/log (AMQP) |
| ESC-05 | Concurrencia, cuotas y backpressure | RF-13 (cuotas/rate limiting en apim), RF-17 (backpressure) |
| ESC-06 | Prevenir cuellos de botella | Colas durables + DLQ (N2); private endpoints; RF-17 |
| ESC-07 | Proteger el WMS de sobrecarga | RF-11 (regular envío), N3-A: Circuit Breaker + Timeout + Retry en el adaptador |
| ESC-08 | Pruebas de carga de picos | Criterios de aceptación de RNF-04 y RNF-16 ("pruebas de carga demuestran…") |
| ESC-09 | Degradación controlada | RF-18 (priorización por SLA), RF-16 (DLQ sin descarte), store-and-forward (RF-22/23) |
| ESC-10 | Crecimiento futuro | Escalado horizontal + particiones del bus por agregado (RF-20) |

## INT — Integración
| Código | Lineamiento (resumen) | Dónde se aplica |
|---|---|---|
| INT-01 | APIs versionadas, documentadas, protegidas | N2: apim (OpenAPI, /v1, OAuth2); RF-12, RF-13 |
| INT-02 | Asíncrono vía Bus de Eventos Central | N2: Bus (A) / Log de Eventos (B) = PLT-03; RF-14 |
| INT-03 | Contratos con entrada/salida/errores | ADR-05; errores RFC 7807 en el gateway |
| INT-04 | Evento con esquema, correlation ID, idempotencia | RF-14, RF-15; Outbox publica con correlation ID (N3) |
| INT-05 | Timeouts, reintentos, circuit breaker, backpressure, DLQ | N3-A: adaptador WMS; RF-16, RF-17 |
| INT-06 | Integraciones críticas idempotentes | RF-04 (API), RF-16 (consumidor), RF-23 (móvil); patrón Inbox en N3-B |
| INT-07 | Cambio incompatible = versión nueva | RF-12 (escenario de rechazo de cambio incompatible) |
| INT-08 | Mínimo acoplamiento directo entre sistemas | Todos los cruces pasan por bus o apim (N2 de A y B) |
| INT-09 | Replay controlado sin duplicar efectos | RF-19; en B es nativo (Event Sourcing, ADR-09) |
| INT-10 | Evidencia de intercambio para auditoría | RF-07; RNF-08; OBS vía correlation ID |
| INT-11 | Adaptadores AS-IS + contratos TO-BE en transición | RF-11, RF-21; adaptadores en N2/N3 |
| INT-12 | Secuencia lógica por agregado | RF-20; particiones por orden/paquete/ruta en el bus |

## OBS — Observabilidad
| Código | Lineamiento (resumen) | Dónde se aplica |
|---|---|---|
| OBS-01 | Logs estructurados | Contenedor Observabilidad (OTel) en N2 |
| OBS-02 / OBS-03 | Correlation ID rastreable y propagado | RNF-05, RNF-15; obligatorio en el Outbox (N3) |
| OBS-04 | Métricas técnicas y de negocio | RNF-24; salud de colas/DLQ exportada a obs (N2) |
| OBS-05 | Alertas (colas, DLQ, tracking >20 min) | RF-16 (alerta DLQ), RF-17 (saturación), RNF-27 (20 min) |
| OBS-06 | Logs sin datos personales | **Política transversal declarada aquí:** los logs enmascaran direcciones, teléfonos y no incluyen firmas/fotos; se valida en revisión de código |
| OBS-07 | Trazas end-to-end orden→entrega→liquidación | RNF-05; correlation ID a través de las 3 nubes (Anexo) |
| OBS-08 | Dashboards operativos | RNF-24 (pendientes, fallidos, DLQ por conductor/ruta) |
| OBS-09 | Auditoría de cambios manuales y reintentos | RF-07, RF-19 (replay auditado), RNF-08 |
| OBS-10 | Cobertura Azure + AWS + GCP + on-prem | Anexo: CloudTrail / Azure Monitor / Cloud Audit Logs + OTel |

## SEG — Seguridad
| Código | Lineamiento (resumen) | Dónde se aplica |
|---|---|---|
| SEG-01 | Cifrado en tránsito | TLS en toda relación de N2/N3 (protocolos en cada flecha); RNF-06 |
| SEG-02 | Cifrado en reposo (evidencias, offline, PII) | S3+KMS (N2), RNF-06, RNF-20 (AES-256 local) |
| SEG-03 | AuthN centralizada (OAuth2/OIDC/federada) | apim + Entra ID (N2); federación hacia AWS/GCP (Anexo) |
| SEG-04 | Mínimo privilegio por rol | Anexo (PoLP, deny by default); RNF-13 |
| SEG-05 / SEG-06 | Secretos fuera del código, en gestor administrado | Key Vault / Secrets Manager (N2, N3, ADR-08); RNF-06 |
| SEG-07 | Auditoría de operaciones críticas | RF-07 (movimientos), RF-24 (excepciones), RNF-08 |
| SEG-08 | WAF, rate limiting, validación, cuotas | apim (N2) + WAF/Front Door (Anexo); RF-13 |
| SEG-09 | App móvil: cifrado local, sesión, cambio de dispositivo | RF-22 (sesión), RF-27 (dispositivo), RNF-20 (cifrado) |
| SEG-10 | Evidencias con hash, acceso y retención | RF-26 (hash), RNF-25, RNF-08 (retención) |
| SEG-11 | Desarrollo seguro y análisis de vulnerabilidades | **Se aplica en el pipeline CI/CD del MVP (siguiente hito, IaC)** — fuera del alcance de los diagramas C4; queda declarado aquí |
| SEG-12 | Conectividad intercloud segura y segmentada | Anexo: VPN IPsec, subredes por capa, NSG deny-by-default, CIDR sin solapamiento |

---
**Cobertura: 54/54.** Dos lineamientos (OBS-06, SEG-11) se cumplen por política/pipeline y no por un elemento de diagrama — se declara explícitamente en vez de forzar una caja que no corresponde.

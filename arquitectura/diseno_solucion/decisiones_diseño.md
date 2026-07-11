# Decisiones de Diseño — Architectural Decision Records (ADR)

**Proyecto:** RutaExpress TO-BE · Grupo 6 · Hito "TO BE: Diseño de Arquitectura de Solución"
**Elaboración:** análisis del equipo con apoyo de IA (Claude — Anthropic) · **Fecha:** 2026-07-09
**Formato:** Contexto → Opciones → Decisión → Consecuencias. Estado: todas **Aceptadas** salvo indicación.

---

## ADR-01 · Multicloud best-of-breed, no forzado
- **Contexto:** el enunciado exige mínimo 2 nubes en el MVP y el programa es de arquitectura **multinube**. RutaExpress **ya opera** en Azure (TMS, integración), AWS (app móvil, evidencias) y GCP (optimización de rutas) + on-premises (WMS, ERP).
- **Opciones:** (a) consolidar en una nube y forzar una segunda para cumplir; (b) best-of-breed manteniendo cada dominio donde ya opera y donde el proveedor es más fuerte.
- **Decisión:** **(b) best-of-breed** — Azure para núcleo transaccional/integración ("líder empresarial", Entra ID), AWS para última milla/evidencias ("líder de mercado", ya en producción), GCP para analítica/ML ("innovador en datos e IA", BigQuery/Vertex).
- **Consecuencias:** + sin migraciones innecesarias, cada dominio en su mejor nube; − requiere conectividad intercloud (ADR-08), observabilidad federada y disciplina de contratos (RNF-18).

## ADR-02 · Hub de integración y gobierno en Azure
- **Contexto:** el bus de eventos (PLT-03), el API governance y la identidad necesitan un "centro de gravedad". El OMS (APP-02) evoluciona en Azure y el TMS ya vive en Azure.
- **Opciones:** (a) hub en Azure; (b) hub en AWS; (c) doble hub.
- **Decisión:** **(a) Azure** — minimiza saltos intercloud del flujo transaccional (orden→reserva→despacho ocurre entre servicios Azure y on-prem), un solo plano de gobierno de APIs y de identidad (Entra ID federando a AWS/GCP).
- **Consecuencias:** + menor latencia y menor costo de transferencia en la ruta crítica, un solo catálogo de contratos; − AWS/GCP consumen eventos vía bridges. **Nota:** esto es una **decisión dentro de ambas alternativas**, no una alternativa en sí misma — mover el hub de nube no cambia la arquitectura.

## ADR-03 · Estilo de coordinación: Orquestación (Alt. A) vs Coreografía (Alt. B) — la bifurcación
- **Contexto:** la reserva de una orden toca OMS, WMS on-prem y ERP on-prem, con compensación si algo falla (Saga). El caso exige que nada se pierda ni se duplique (Cyber Days, 32k duplicados).
- **Opciones:** (a) **Saga Orquestada** — un coordinador central comanda cada paso y ejecuta la compensación; (b) **Saga Coreografiada** — cada servicio reacciona a eventos y publica el siguiente, la compensación también es un evento, con Event Sourcing + CQRS.
- **Decisión:** **se modelan ambas como las dos alternativas del hito** (es un trade-off genuino, no hay respuesta única): A = orquestada, B = coreografiada. La recomendación se sustenta en el cuadro comparativo.
- **Consecuencias:** A: + visibilidad y compensación simples, − el orquestador concentra lógica. B: + autonomía, desacoplamiento y auditoría nativa por el log, − flujo difícil de seguir y consistencia eventual en todas las lecturas.

## ADR-04 · Patrón Outbox para publicación confiable
- **Contexto:** si un servicio guarda en BD y luego el bus no está disponible, el evento se pierde (RF-14 exige no perderlo).
- **Opciones:** (a) publicar directo al bus tras guardar (riesgo de pérdida entre ambas operaciones); (b) transacción distribuida BD+bus (2PC — frágil y no soportado entre servicios administrados); (c) **Outbox**: evento y estado en la misma transacción local, publicación asíncrona con reintento.
- **Decisión:** **(c) Outbox** en todo productor. Aplica en ambas alternativas.
- **Consecuencias:** + cero eventos perdidos aunque el bus caiga; − entrega al menos una vez → exige deduplicación del consumidor (RF-16; en B, patrón Inbox).

## ADR-05 · API-First con OpenAPI en el gateway
- **Contexto:** integraciones punto a punto frágiles; el cambio de un cliente rompía a los demás.
- **Opciones:** (a) code-first (el contrato se genera del código: el consumidor depende de la implementación); (b) **contract-first (API-First)**: el contrato se diseña, revisa y aprueba antes de programar.
- **Decisión:** **(b)** — el contrato **OpenAPI se diseña antes del código** y se importa a API Management; el gateway valida esquemas, aplica validate-jwt (OIDC), rate limiting + quota y versiona por URI (/v1); errores normalizados RFC 7807. Los **eventos también son contratos** (versionados, tolerancia al cambio; documentados con AsyncAPI como extensión).
- **Consecuencias:** + el contrato es la fuente de verdad, consumidores desacoplados; − disciplina de gobernanza (lint del contrato en el pipeline).

## ADR-06 · GCP para optimización de rutas y analítica
- **Contexto:** objeción esperable del comité: "¿por qué una tercera nube?".
- **Opciones:** (a) llevar analítica a Azure (Synapse); (b) mantener GCP.
- **Decisión:** **(b)** — la optimización de rutas **ya corre en GCP** (Hito 1); migrarla sería costo sin beneficio, y BigQuery/Vertex AI son la fortaleza reconocida de GCP para el objetivo de reducir 12.5%→7% de fallas con predicción.
- **Consecuencias:** + continuidad y mejor herramienta por dominio; − un bridge de eventos adicional (Pub/Sub) y observabilidad en tres planos.

## ADR-07 · DR por criticidad (no una sola estrategia)
- **Contexto:** el caso nace de 6 h de caída (USD 1.1M). El trade-off RTO/RPO/costo se decide por ámbito.
- **Opciones:** (a) una sola estrategia para toda la plataforma — Multi-Site Active/Active (sobrecosto en lo no crítico) o Backup/Restore (RTO de horas en la ruta crítica); (b) **estrategia por criticidad** de cada ámbito.
- **Decisión:** **(b)** — **Warm Standby** para el núcleo Azure (RTO minutos), **replicación cross-region** para evidencias (sustentan USD 2.4M), **PITR** para DynamoDB, **Backup and Restore** para analítica, **store-and-forward** en el dispositivo del conductor.
- **Consecuencias:** + costo proporcional a la criticidad; − runbooks y pruebas de conmutación por ámbito.

## ADR-08 · Conectividad intercloud: VPN IPsec primero, líneas dedicadas después; mTLS como capa adicional
- **Contexto:** tres nubes + on-prem deben hablar por red privada; los CIDR no se solapan (10.0/10.1/10.2).
- **Decisión:** fase inicial con **VPN site-to-site (IPsec)**; evolución a **ExpressRoute / Direct Connect / Cloud Interconnect** cuando el volumen lo justifique. **mTLS** entre servicios que cruzan nubes como extensión de industria, justificada por **defensa en profundidad**.
- **Consecuencias:** + arranque barato y seguro, camino de crecimiento claro; − gestión de certificados (rotación vía Key Vault/KMS).

## ADR-09 · Event Sourcing + CQRS completo solo en la Alternativa B
- **Contexto:** el log como fuente de verdad da auditoría y replay nativos, pero exige madurez (proyecciones, versionado de eventos, reconstrucción).
- **Opciones:** (a) Event Sourcing en ambas alternativas (elimina el contraste y encarece la A sin necesidad); (b) en ninguna (B perdería su ventaja diferencial de auditoría/replay); (c) **solo en B**, donde es coherente con la coreografía.
- **Decisión:** **(c)** — en **A**, el estado vive en la BD del OMS y CQRS es liviano (read model de consulta); en **B**, el **log es la fuente de verdad** y todas las vistas son proyecciones.
- **Consecuencias:** A: + simplicidad operativa; B: + auditoría/replay totales (RF-07, RF-19 nativos), − curva de equipo y consistencia eventual en todo.

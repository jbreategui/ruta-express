# Diseño de Solución TO-BE — C4 Model · RutaExpress (Grupo 6)

Modelo C4 de la solución TO-BE, **anclado en los 29 RF y 27 RNF** de `../requerimientos/`.
Esta carpeta contiene el **modelo** (fuente de verdad). El renderizado a imágenes (Python/DaC u otro) se hace **después**, a partir de este modelo.

## Las dos alternativas (mismo alcance, arquitecturas genuinamente distintas)
Ambas son multinube best-of-breed con la **misma huella** (Azure núcleo, AWS última milla, GCP analítica — ADR-01/02): así el comité compara **arquitecturas, no proveedores**. La bifurcación real es el **estilo de coordinación** (ADR-03, enseñado en Módulo 3 S3):

| | `alternativa_A_orquestada/` | `alternativa_B_coreografiada/` |
|---|---|---|
| Coordinación | **Saga Orquestada**: el OMS comanda reserva y valorización y compensa centralmente | **Saga Coreografiada**: cada servicio reacciona a eventos; la compensación también es un evento |
| Fuente de verdad | Estado en BD del OMS | **Log de eventos** (Event Sourcing) + CQRS completo |
| N3 abre | El OMS (orquestador) | El Servicio de Inventario (consumidor coreografiado) |

**Recomendada: A** — ver `cuadro_comparativo_recomendacion.md`.

## Disciplina C4 aplicada (lo que se corrigió del intento anterior)
| Nivel | Qué muestra | Qué NO debe mostrar |
|---|---|---|
| **1 Contexto** | Sistema + personas + sistemas externos | Tecnología, contenedores, componentes |
| **2 Contenedores** | Unidades **desplegables** gruesas + tecnología + **protocolo** en cada relación | El **interior** de un contenedor (eso es Nivel 3) |
| **3 Componentes** | Interior de **UN** contenedor con interfaces, protocolos y seguridad (ambas alternativas abren el dominio Reserva de Inventario para comparar) | Varios contenedores a la vez |
| **Despliegue** | Red, conectividad, zonas de seguridad, private endpoints, secretos | Lógica de negocio |

**Errores del diseño previo que este corrige:**
1. El Nivel 2 estaba **sobre-descompuesto** (partía el bus, abría la analítica en 5 cajas) → parecía Nivel 3. Aquí el N2 es **grueso** (10 contenedores) con **protocolos** en las flechas.
2. El Nivel 3 no tenía interfaces/seguridad → aquí el N3 del OMS muestra **componentes, contratos, protocolos y controles de seguridad**.
3. **No existía diagrama de despliegue/red** → se agrega como anexo (`anexos/despliegue_red_seguridad.md`), fuera de los niveles C4 del entregable.

## Estructura
| Archivo | Contenido |
|---|---|
| `alternativa_A_orquestada/01…03_*.md` | C4 L1-L2-L3 de la Alternativa A |
| `alternativa_B_coreografiada/01…03_*.md` | C4 L1-L2-L3 de la Alternativa B |
| `diagramas_secuencia/` | **Vista dinámica** (complementa al C4 estático): recepción/dedup, Saga A orquestada, Saga B coreografiada y resiliencia del WMS — muestra el comportamiento en el tiempo y el contraste A vs B |
| `anexos/despliegue_red_seguridad.md` | **Anexo (no es un nivel C4 del entregable):** vista de despliegue/red/seguridad de la alternativa recomendada — responde el feedback del profesor ("ver la red, cómo se conectan, seguridad") |
| `decisiones_diseño.md` | ADR-01 … ADR-09 (incluye la bifurcación A/B y por qué el hub en Azure es un ADR, no una alternativa) |
| `cuadro_comparativo_recomendacion.md` | Evaluación ponderada + recomendación (A) |
| `lineamientos_aplicados.md` | Matriz de trazabilidad de los 54 lineamientos (ARQ/ESC/INT/OBS/SEG) → dónde se aplica cada uno |

> El curso trabaja los **3 primeros niveles** del C4 (Módulo 2, Taller 3, pasos 6-9) y remite a **c4model.com** para la definición formal. El diagrama de despliegue es la **vista complementaria oficial** del C4 Model (Deployment diagram) y responde directamente al feedback del profesor: *"ver la red, cómo se conectan, seguridad"*.

## Base teórica — dónde está cada decisión en las clases
Cada decisión de este diseño es defendible con una lámina del curso. Mapa para estudiar:

| Decisión del diseño | Base teórica (módulo · sesión · página) | Dónde se aplica |
|---|---|---|
| C4 en 3 niveles, un archivo por nivel, Diagram-as-Code versionable | M2 Taller 3 (S3), diap. 3, 19-24; c4model.com | Toda la carpeta |
| Servicios cloud concretos (no cajas abstractas) en N2/N3 | M2 Taller 3, ejemplo core bancario | 02, 03, 04 |
| API-First: contrato OpenAPI antes del código, importado al gateway | M7 S1 p.22; S2 p.15-19 | `apim` en 02 |
| Gateway = único punto de entrada; backends nunca expuestos a Internet | M7 S3 p.6, 9 | 02, 04 |
| validate-jwt (OIDC/JWKS), rate limiting (429) + quota, errores RFC 7807 | M7 S3 p.20-23; S2 p.13-14 | `apim` en 02 |
| OAuth2 Client Credentials (sistema-a-sistema) y Authorization Code + PKCE (apps con usuario) | M7 S3 p.19 | 02, 04 |
| Eventos = solución al **acoplamiento temporal**; el evento también es contrato (tolerancia al cambio) | M7 S1 p.20-21 | 02 |
| EDA, CQRS, Saga orquestada, Outbox, Event Sourcing | M3 S3 | 02, 03 |
| Idempotencia con Idempotency-Key en POST críticos | M7 S2 p.12; M3 S3 | 03 (`dedup`) |
| Circuit Breaker, Timeout, Retry con backoff exponencial + jitter (hacia el WMS que se cayó 6 h) | M3 S4 p.14-17, 22-23 | 03 (`wmsad`) |
| Queue-Based Load Leveling + DLQ (con reproceso, nunca descarte) | M3 S4 p.26-27 | 02 (`bus`) |
| DR elegido por trade-off RTO/RPO/costo: Warm Standby, Backup and Restore, PITR | M3 S4 p.30-32 | 04 |
| Multicloud **best-of-breed**: Azure "líder empresarial", AWS "líder de mercado", GCP "innovador en datos e IA" | M3 S4 p.33-34 | Ubicación de contenedores (02, 04) |
| Zero Trust ("nunca confiar, siempre verificar"), identidad = nuevo perímetro, federación Entra ID → AWS/GCP | M6 S1 p.15-17 | 04 |
| Mínimo privilegio (PoLP), deny by default, segmentación web/app/datos, Flow Logs, CIDR sin solapamiento | M6 S1 p.23; S3 p.12, 21-24, 30 | 04 |
| Cifrado en tránsito (TLS 1.2+) y en reposo (KMS/Key Vault), secretos en bóveda con rotación | M6 S2 p.13-19 | 02, 03, 04 |
| Conectividad híbrida/intercloud: VPN site-to-site (IPsec) → ExpressRoute / Direct Connect / Cloud Interconnect | M6 S3 p.26 | 04 |
| Auditoría multinube: CloudTrail / Azure Monitor / Cloud Audit Logs | M6 S2 p.22 | 04 |
| Defensa en profundidad: nunca un único mecanismo | M6 S3 p.30 | 04 |

**Criterio de equilibrio:** la base terminológica es la del curso (todo lo de la tabla se defiende con una lámina). Sobre esa base, el diseño agrega prácticas de industria **donde el caso lo amerita**, siempre marcadas como *(extensión)* y justificadas con un principio que el curso sí enseña:
- **mTLS entre nubes y hacia on-prem** *(extensión)* — capa adicional sobre la VPN IPsec, justificada por **defensa en profundidad** (M6 S3 p.30): si el túnel se compromete, los servicios igual se autentican mutuamente.
- **AsyncAPI para documentar los eventos** *(extensión)* — el curso enseña que "el contrato es la fuente de verdad" y que el evento también es un contrato (M7 S1 p.20-22); AsyncAPI es al evento lo que OpenAPI es al REST.

## Pendientes según el método del curso
- `decisiones_diseño.md` (criterios de decisión + modelo LLM usado + fecha) — lo exige la estructura del Taller 2/3.
- Renderizado con **diagrams de Python** (íconos de nube, un `.py` por nivel) — Taller 3, pasos 6-7; se genera **desde** este modelo.
- Alternativa B (coreografiada) con su propio C4.

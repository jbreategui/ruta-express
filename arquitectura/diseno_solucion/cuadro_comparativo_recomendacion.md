# Cuadro Comparativo y Recomendación — Alternativas A y B

**Nota:** ambas alternativas cubren el 100% de los 29 RF y 27 RNF y comparten la misma huella multinube (ADR-01, ADR-02). Se compara **arquitectura** (cómo se coordinan los servicios), no proveedores. Ninguna fue diseñada para perder: cada una gana en criterios distintos.

| | **Alternativa A — Orquestada** | **Alternativa B — Coreografiada** |
|---|---|---|
| Coordinación | Orquestador Saga en el OMS comanda reserva y valorización | Cada servicio reacciona a eventos; nadie comanda |
| Compensación | Centralizada en el orquestador | Distribuida: cada servicio se compensa al escuchar el evento |
| Fuente de verdad | Estado en BD del OMS | **Log de eventos** (Event Sourcing) |
| Consultas | API de consulta + read model liviano | CQRS completo: todo se lee de proyecciones |
| Patrones protagonistas | Saga orquestada, Outbox, CQRS liviano, Circuit Breaker | Saga coreografiada, Event Sourcing, CQRS, Inbox/Outbox |

## Evaluación ponderada
Escala 1–5 · el peso refleja la prioridad del caso (recuperarse de Cyber Days, entregar MVP del siguiente hito en una semana, operar con el equipo actual).

| Criterio | Peso | A | B | Sustento |
|---|---:|---:|---:|---|
| Cobertura RF/RNF (29 + 27) | 3 | 5 | 5 | Ambas trazan el 100%; ver tablas RF por contenedor en cada `02_nivel2` |
| Factibilidad del MVP (Hito 4: 1 semana, 2 nubes, 3 patrones, IaC) | 3 | 5 | 3 | A se demuestra con orden→reserva→compensación visible; B exige event store, proyecciones y versionado de eventos desde el día 1 |
| Operabilidad y trazabilidad del flujo | 2 | 5 | 3 | En A la Saga se consulta en un punto; en B se reconstruye por correlation ID a través del log |
| Desacoplamiento y evolución a largo plazo | 2 | 3 | 5 | En B agregar un consumidor no toca a nadie; en A el orquestador concentra cambios |
| Resiliencia (sin punto único de coordinación) | 2 | 4 | 5 | En B no existe coordinador que caer; en A el orquestador es HA pero existe |
| Auditoría y reconstrucción histórica | 1 | 4 | 5 | En B el log ES la historia (RF-07, RF-19 nativos); en A se audita por eventos + BD |
| Curva del equipo / complejidad cognitiva | 2 | 4 | 2 | Saga orquestada es el patrón más enseñable y depurable; Event Sourcing exige madurez |
| Costo relativo de operación | 1 | 4 | 3 | B paga retención larga del log, proyectores y más servicios desplegados |
| **Total ponderado (máx. 80)** | | **70** | **62** | |

## Recomendación: **Alternativa A (orquestada)** para este TO-BE y el MVP
1. **El caso pide control, no autonomía:** el dolor de RutaExpress es la falta de **una sola verdad** y de visibilidad (240k pedidos encolados sin que nadie supiera el estado). El orquestador da exactamente eso: un punto donde toda orden se ve, se compensa y se explica.
2. **El siguiente hito la favorece:** el MVP exige 2 nubes + 3 patrones + IaC en una semana. A demuestra Microservicios + EDA + Saga + resiliencia con menos piezas móviles.
3. **B no se descarta, se pospone:** el diseño de A ya publica todos los eventos canónicos por Outbox; migrar dominios puntuales a coreografía (p. ej. tracking y analítica, que ya son reactivos) es una evolución natural sin rehacer la plataforma.

**Cuándo elegir B:** si el comité prioriza la escala de equipos autónomos y la auditoría regulatoria por encima de la velocidad del MVP, B es la mejor arquitectura — y este cuadro lo dice con puntajes reales, no con un espantapájaros.

---
*Elaboración: equipo Grupo 6 · 2026-07-09*

# Diagramas de Secuencia — Vista Dinámica

El C4 (niveles 1-2-3) muestra **estructura estática** (qué contenedores/componentes hay y cómo se conectan). Estos diagramas de secuencia muestran el **comportamiento dinámico** — cómo fluye una orden en el tiempo — que es donde mejor se ve la diferencia entre las dos alternativas.

| Archivo | Flujo | Para qué |
|---|---|---|
| `01_recepcion_orden.md` | Recepción: deduplicación + idempotencia | Cómo se evitan los 32k duplicados (RF-01…05) |
| `02_saga_A_orquestada.md` | Reserva en A (orquestada): éxito y compensación | La Saga **comanda** cada paso (RF-06…08) |
| `03_saga_B_coreografiada.md` | Reserva en B (coreografiada): éxito y compensación | Cada servicio **reacciona a eventos**, sin comandante |
| `04_resiliencia_wms.md` | WMS lento/caído: Circuit Breaker + Retry + DLQ | La lección de Cyber Days (RF-11, RF-16) |

**Contraste clave (02 vs 03):** el **mismo escenario** (reservar una orden y compensar si el ERP rechaza) resuelto de dos formas — en A todas las flechas salen de la Saga; en B es una cadena de eventos donde nadie manda. Es la prueba visual de que A y B son arquitecturas genuinamente distintas.

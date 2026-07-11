# Alternativa B (Coreografiada) · C4 Nivel 3 — Componentes del Log de Eventos (fuente de verdad)

**Pregunta:** ¿cómo funciona por dentro el **Log de Eventos** cuando **ES la fuente de verdad** (Event Sourcing), no solo un transporte? ¿Con qué componentes garantiza retención, orden, no-pérdida y reconstrucción por replay?
**Regla:** se abre **UN** contenedor (el Log). Es el corazón de INI-02 (RF-14…21) en la Alternativa B. Los demás aparecen como cajas externas de borde.

> **Diferencia clave con A:** en A (`../alternativa_A_orquestada/03b_nivel3_componentes_bus_eventos.md`) el bus **transporta** eventos y el estado vive en la BD del OMS. Aquí el log **retiene los eventos de forma inmutable** y el estado de cualquier servicio se **reconstruye reproduciéndolos** (Event Sourcing). Por eso aparecen el **Almacén de Eventos append-only** y el **Motor de Replay** como piezas centrales, no accesorias.

```mermaid
C4Component
    title Componentes — Log de Eventos como Event Store (Azure Event Hubs + Service Bus · Alternativa B)

    Container_Ext(prod, "Productores", "Órdenes, Inventario, Adaptadores, última milla", "publican eventos")
    Container_Ext(proy, "Proyectores / CQRS", "Servicio de Consultas", "construyen read models")
    Container_Ext(cons, "Consumidores", "portal, TMS, analítica", "suscritos")
    ContainerDb_Ext(dlq, "DLQ", "mensajes muertos", "reproceso")
    Container_Ext(obs, "Observabilidad", "Azure Monitor", "salud de colas y lag")

    Container_Boundary(log, "Log de Eventos (fuente de verdad)") {
        Component(append, "Ingesta Append-Only", "Servicio", "Escribe cada evento de forma inmutable con correlation ID (RF-14)")
        Component(schema, "Validador y Versionado de Esquemas", "Servicio", "Valida el esquema versionado; cambios non-breaking (RF-15)")
        Component(store, "Almacén de Eventos", "Event Store", "Retención larga e inmutable: el log ES la historia (RF-07, RF-19)")
        Component(router, "Enrutador / Suscripciones", "Servicio", "Entrega por topic a cada suscriptor autónomo (RF-14)")
        Component(retry, "Reintentos + DLQ", "Servicio", "Backoff y dead-letter sin descartar (RF-16)")
        Component(backp, "Control de Backpressure", "Servicio", "Regula el flujo ante saturación (RF-17)")
        Component(prio, "Priorizador por SLA", "Servicio", "Eventos críticos primero (RF-18)")
        Component(replay, "Motor de Replay", "Servicio", "Reconstruye estado reproduciendo por rango, sin doble efecto (RF-19)")
        Component(seq, "Secuenciador por Agregado", "Servicio", "Orden lógico por orden/paquete/ruta (RF-20)")
        Component(p2p, "Adaptador Punto-a-Punto", "Servicio", "Convivencia transicional con integraciones AS-IS (RF-21)")
    }

    Rel(prod, append, "Publica evento", "AMQP (TLS) + correlation ID")
    Rel(append, schema, "Valida antes de persistir", "in-proc")
    Rel(schema, store, "Persiste inmutable", "in-proc")
    Rel(store, router, "Entrega a suscriptores", "in-proc")
    Rel(router, seq, "Ordena por agregado", "in-proc")
    Rel(seq, prio, "Aplica prioridad", "in-proc")
    Rel(prio, cons, "Entrega a consumidores", "AMQP (TLS)")
    Rel(router, proy, "Alimenta las proyecciones (CQRS)", "AMQP (TLS)")
    Rel(router, backp, "Regula ingesta", "in-proc")
    Rel(retry, dlq, "Mueve tras agotar reintentos", "AMQP")
    Rel(prio, retry, "Reintenta si el consumidor falla", "in-proc")
    Rel(replay, store, "Lee rango histórico", "in-proc")
    Rel(replay, router, "Reinyecta eventos históricos", "in-proc")
    Rel(p2p, cons, "Flujo transicional", "API")
    Rel(log, obs, "Exporta salud de colas, DLQ y lag", "OTLP")

    UpdateElementStyle(store, $bgColor="#4B9CE2")
    UpdateElementStyle(obs, $bgColor="grey")
```

## Componentes (responsabilidad · RF)
| Componente | Responsabilidad | RF |
|---|---|---|
| Ingesta Append-Only | Escritura inmutable con correlation ID | RF-14 |
| Validador y Versionado de Esquemas | Conformidad + versionado non-breaking | RF-15 |
| **Almacén de Eventos** | **Retención inmutable: el log ES la fuente de verdad** | RF-07, RF-19 |
| Enrutador / Suscripciones | Entrega por topic a consumidores autónomos | RF-14 |
| Reintentos + DLQ | Backoff y dead-letter sin descarte | RF-16 |
| Control de Backpressure | Regula el flujo ante saturación (Cyber Days) | RF-17 |
| Priorizador por SLA | Reserva/entrega/liquidación antes que informativos | RF-18 |
| **Motor de Replay** | **Reconstruye el estado reproduciendo el log** | RF-19 |
| Secuenciador por Agregado | Orden lógico por orden/paquete/ruta | RF-20 |
| Adaptador Punto-a-Punto | Convivencia con integraciones AS-IS | RF-21 |

## Contraste con el Nivel 3 de la Alternativa A (mismo dominio: bus/log)
| Aspecto | A — Bus de Eventos | B — Log de Eventos (este) |
|---|---|---|
| Rol del componente | **Transporta** eventos entre servicios | **Retiene** eventos como fuente de verdad |
| Dónde vive el estado | En la BD del OMS | **En el propio log** (Event Sourcing) |
| Replay | Reproceso de mensajes | **Reconstrucción de estado** (nativo) |
| Piezas centrales | Ingesta, enrutador, DLQ | **Almacén append-only + Motor de Replay** |

**Lo que demuestra:** en B el log no es tubería, es memoria. Nada se pierde (DLQ), nada se duplica (replay idempotente), nada llega fuera de orden (secuenciador) — y además **cualquier estado se reconstruye** reproduciendo la historia (respuesta nativa a auditoría y a los 240k mensajes de Cyber Days).

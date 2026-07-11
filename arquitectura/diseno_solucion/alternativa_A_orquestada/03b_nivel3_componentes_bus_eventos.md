# Alternativa A (Orquestada) · C4 Nivel 3 — Componentes del Bus de Eventos

**Pregunta:** ¿cómo funciona por dentro el **Bus de Eventos** (integración API-First / Event-Driven), con qué componentes garantiza entrega confiable, orden y no-pérdida?
**Regla:** se abre **UN** contenedor (el Bus). Es el corazón de INI-02 (RF-14…21). Los demás aparecen como cajas externas de borde.

```mermaid
C4Component
    title Componentes — Bus de Eventos Central (Azure Event Hubs + Service Bus)

    Container_Ext(prod, "Productores", "OMS, WMS, TMS, app, ERP", "publican eventos")
    Container_Ext(cons, "Consumidores", "última milla, portal, TMS, analítica", "suscritos")
    ContainerDb_Ext(dlq, "DLQ", "mensajes muertos", "reproceso")
    Container_Ext(obs, "Observabilidad", "Azure Monitor", "salud de colas")

    Container_Boundary(bus, "Bus de Eventos Central") {
        Component(ingesta, "Ingesta / Publicador", "Servicio", "Recibe eventos con correlation ID (RF-14)")
        Component(schema, "Validador de Esquemas", "Servicio", "Valida el esquema versionado del evento (RF-15)")
        Component(router, "Enrutador (Topics/Colas)", "Servicio", "Distribuye a los suscriptores (RF-14)")
        Component(retry, "Reintentos + DLQ", "Servicio", "Backoff y dead-letter sin descartar (RF-16)")
        Component(backp, "Control de Backpressure", "Servicio", "Regula el flujo ante saturación (RF-17)")
        Component(prio, "Priorizador por SLA", "Servicio", "Eventos críticos primero (RF-18)")
        Component(replay, "Motor de Replay", "Servicio", "Reprocesa por rango sin duplicar (RF-19)")
        Component(seq, "Secuenciador por Agregado", "Servicio", "Orden lógico por orden/paquete/ruta (RF-20)")
        Component(p2p, "Adaptador Punto-a-Punto", "Servicio", "Convivencia transicional (RF-21)")
    }

    Rel(prod, ingesta, "Publica evento", "AMQP + correlation ID")
    Rel(ingesta, schema, "Valida esquema", "in-proc")
    Rel(schema, router, "Evento válido", "in-proc")
    Rel(router, seq, "Ordena por agregado", "in-proc")
    Rel(seq, prio, "Aplica prioridad", "in-proc")
    Rel(prio, cons, "Entrega a suscriptores", "AMQP")
    Rel(router, backp, "Regula ingesta", "in-proc")
    Rel(retry, dlq, "Mueve tras agotar reintentos", "AMQP")
    Rel(prio, retry, "Reintenta si el consumidor falla", "in-proc")
    Rel(replay, router, "Reinyecta eventos históricos", "in-proc")
    Rel(p2p, cons, "Flujo transicional", "API")
    Rel(bus, obs, "Exporta salud de colas y DLQ", "OTLP")

    UpdateElementStyle(obs, $bgColor="grey")
```

## Componentes (responsabilidad · RF)
| Componente | Responsabilidad | RF |
|---|---|---|
| Ingesta / Publicador | Recepción confiable con correlation ID | RF-14 |
| Validador de Esquemas | Conformidad del payload contra el esquema versionado | RF-15 |
| Enrutador (Topics/Colas) | Distribución a suscriptores | RF-14 |
| Reintentos + DLQ | Backoff y dead-letter sin descarte | RF-16 |
| Control de Backpressure | Regula el flujo ante saturación (Cyber Days) | RF-17 |
| Priorizador por SLA | Reserva/entrega/liquidación antes que informativos | RF-18 |
| Motor de Replay | Reproceso controlado por rango, sin doble efecto | RF-19 |
| Secuenciador por Agregado | Orden lógico por orden/paquete/ruta | RF-20 |
| Adaptador Punto-a-Punto | Convivencia con integraciones AS-IS | RF-21 |

**Lo que demuestra:** la entrega confiable end-to-end — nada se pierde (DLQ), nada se duplica (replay idempotente), nada llega fuera de orden (secuenciador) — la respuesta directa a los 240k mensajes encolados de Cyber Days.

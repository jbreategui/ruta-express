# Alternativa B (Coreografiada) · C4 Nivel 3 — Componentes del Servicio de Inventario

**Pregunta:** ¿cómo funciona por dentro un servicio **coreografiado**, con qué **interfaces, protocolos y controles**?
**Regla:** se abre **UN** contenedor. Se elige el **Servicio de Inventario** porque es donde la coreografía se ve completa: reacciona a eventos, decide solo, publica el resultado y **se compensa a sí mismo** — el contraste directo con el orquestador de la Alternativa A.

```mermaid
C4Component
    title Componentes — Servicio de Inventario (Azure AKS · Alternativa B)

    Container_Ext(eventlog, "Log de Eventos", "Event Hubs + Service Bus", "fuente de verdad")
    ContainerDb_Ext(invdb, "BD de Inventario", "Azure SQL", "estado propio + inbox/outbox")
    Container_Ext(readmodels, "Servicio de Consultas (CQRS)", "Azure AKS + Azure SQL", "proyecciones de lectura")
    Container_Ext(iam, "Identidad y Secretos", "Entra ID + Key Vault", "")
    Container_Ext(obs, "Observabilidad", "Azure Monitor + OTel", "")

    Container_Boundary(inv, "Servicio de Inventario") {
        Component(inbox, "Consumidor de Eventos (Inbox)", "Suscriptor AMQP", "Recibe OrdenValidada y ValorizacionRechazada; deduplica por identificador de evento")
        Component(reserva, "Manejador de Reserva", "Servicio", "Verifica elegibilidad y reserva atómicamente; decide Reservado o Insuficiente")
        Component(compensa, "Manejador de Compensación", "Servicio", "Al escuchar ValorizacionRechazada libera la reserva y lo registra")
        Component(auditoria, "Registro Auditable de Movimientos", "Servicio", "Cada reserva y liberación queda como evento con actor, motivo y correlation ID")
        Component(recon, "Reconciliador", "Servicio", "Detecta y resuelve conflictos con almacenes al reconectar")
        Component(outbox, "Publicador Outbox", "Servicio", "Publica InventarioReservado/Insuficiente/Liberado de forma confiable")
        Component(proyector, "Proyector de Disponibilidad", "Servicio", "Actualiza la proyección de disponibilidad desde los eventos confirmados")
    }

    Rel(eventlog, inbox, "OrdenValidada / ValorizacionRechazada", "AMQP (TLS) + correlation ID")
    Rel(inbox, reserva, "Orden validada nueva", "in-proc")
    Rel(inbox, compensa, "Valorización rechazada", "in-proc")
    Rel(reserva, invdb, "Reserva atómica + inbox/outbox", "TDS · private endpoint (TLS)")
    Rel(compensa, invdb, "Libera la reserva", "TDS · private endpoint (TLS)")
    Rel(reserva, auditoria, "Registra el movimiento", "in-proc")
    Rel(compensa, auditoria, "Registra la liberación", "in-proc")
    Rel(recon, invdb, "Concilia saldos en conflicto", "TDS")
    Rel(outbox, invdb, "Lee outbox", "TDS")
    Rel(outbox, eventlog, "Publica el resultado como evento", "AMQP (TLS)")
    Rel(eventlog, proyector, "Eventos confirmados", "AMQP")
    Rel(proyector, readmodels, "Actualiza proyección de disponibilidad", "TDS")
    Rel(outbox, iam, "Obtiene secretos", "Key Vault")
    Rel(inbox, obs, "Trazas de consumo y lag", "OTLP")

    UpdateElementStyle(iam, $bgColor="grey")
    UpdateElementStyle(obs, $bgColor="grey")
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```
> Los adaptadores WMS/ERP reciben los eventos de reserva directamente del log (se ve en el Nivel 2); aquí se omite esa relación porque no involucra al contenedor abierto. Los códigos RF de cada componente están en la tabla de abajo.

## Componentes (interfaz · responsabilidad · control · RF)
| Componente | Interfaz / Protocolo | Responsabilidad | Control | RF |
|---|---|---|---|---|
| Consumidor de Eventos (Inbox) | AMQP · TLS | Suscripción y **deduplicación por identificador de evento** | Idempotencia del consumidor (patrón Inbox) | RF-16 |
| Manejador de Reserva | in-proc | Reserva atómica: solo una gana ante concurrencia | Transacción sobre BD propia | RF-06 |
| Manejador de Compensación | in-proc | Libera al escuchar el rechazo — **compensación sin orquestador** | Auditoría obligatoria | RF-08 |
| Registro Auditable | in-proc | Todo movimiento con actor, motivo, correlation ID | Sin borrado, solo apéndice | RF-07 |
| Reconciliador | in-proc | Conflictos al reconectar almacenes | Trazabilidad | RF-09 |
| Publicador Outbox | AMQP · TLS | Publicación confiable del resultado | Secretos en Key Vault | RF-14 |
| Proyector (CQRS) | AMQP → TDS | Read model de disponibilidad | Solo lectura para consultas | RF-10 |

## Contraste con el Nivel 3 de la Alternativa A (lo que el comité debe ver)
| Aspecto | A — OMS orquestador | B — Inventario coreografiado |
|---|---|---|
| ¿Quién coordina la reserva? | El **Orquestador Saga** dentro del OMS comanda WMS y ERP | **Nadie**: cada servicio reacciona al evento anterior |
| Compensación | El orquestador la ejecuta y la ve completa | El propio servicio se compensa al escuchar el rechazo |
| Fuente de verdad | Estado en Azure SQL del OMS | **El log de eventos** (Event Sourcing); el estado se reconstruye |
| Seguimiento de un pedido | Consultar al orquestador | Reconstruir por **correlation ID** a través del log |
| Idempotencia | Idempotency key en la API | **Inbox** por identificador de evento en cada consumidor |

# Secuencia — Reserva en Alternativa A (Saga ORQUESTADA)

El **Orquestador (Saga)** comanda cada paso y ejecuta la compensación. Fíjate que todas las flechas de decisión **salen de la Saga**: hay un punto único de control. RF-06, RF-07, RF-08.

## Caso 1 — Éxito (reserva completa)
```mermaid
sequenceDiagram
    autonumber
    participant SAGA as Orquestador (Saga)
    participant INV as Inventario y Reservas
    participant WMS as WMS (mock/on-prem)
    participant ERP as ERP (mock/on-prem)
    participant OUT as Outbox → Bus

    Note over SAGA: orden en estado "Validada"
    SAGA->>INV: 1. reservar local (comando)
    INV-->>SAGA: reservado (stock elegible)
    SAGA->>WMS: 2. reserva física (comando)
    WMS-->>SAGA: OK
    SAGA->>ERP: 3. valorizar (comando)
    ERP-->>SAGA: aceptado
    SAGA->>OUT: publica InventarioReservado + OrdenLista
    Note over SAGA: estado → "Lista"
```

## Caso 2 — Compensación (el ERP rechaza)
```mermaid
sequenceDiagram
    autonumber
    participant SAGA as Orquestador (Saga)
    participant INV as Inventario y Reservas
    participant WMS as WMS (mock/on-prem)
    participant ERP as ERP (mock/on-prem)
    participant OUT as Outbox → Bus

    SAGA->>INV: 1. reservar local (comando)
    INV-->>SAGA: reservado
    SAGA->>WMS: 2. reserva física (comando)
    WMS-->>SAGA: OK
    SAGA->>ERP: 3. valorizar (comando)
    ERP-->>SAGA: RECHAZADO (422)
    Note over SAGA: la Saga DECIDE compensar
    SAGA->>INV: 4. liberar reserva (comando de COMPENSACIÓN)
    INV-->>SAGA: liberado
    SAGA->>OUT: publica InventarioLiberado + OrdenFallida
    Note over SAGA: estado → "Fallida" · todo auditado con correlationId
```

**Lo que demuestra:** en A la coordinación y la compensación son **centralizadas** — la Saga ve el flujo completo y ordena el "liberar". Ventaja: control y visibilidad en un solo lugar (RF-08).

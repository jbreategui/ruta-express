# Secuencia — Reserva en Alternativa B (Saga COREOGRAFIADA)

**Mismo escenario que en A**, pero **no hay orquestador**: cada servicio reacciona a un evento del **Log de Eventos** y publica el siguiente. La compensación también es un **evento**, no un comando. Compárese caja por caja con `02_saga_A_orquestada.md`.

## Caso 1 — Éxito (por eventos)
```mermaid
sequenceDiagram
    autonumber
    participant OMS as Servicio de Órdenes
    participant LOG as Log de Eventos
    participant INV as Servicio de Inventario
    participant ADE as Adaptador ERP
    participant ERP as ERP (mock/on-prem)
    participant PRO as Proyector (CQRS)

    OMS->>LOG: publica OrdenValidada
    LOG-->>INV: entrega OrdenValidada
    INV->>INV: reserva atómica
    INV->>LOG: publica InventarioReservado
    LOG-->>ADE: entrega InventarioReservado
    ADE->>ERP: valorizar
    ERP-->>ADE: aceptado
    ADE->>LOG: publica ValorizacionConfirmada
    LOG-->>PRO: eventos confirmados
    PRO->>PRO: actualiza read model → "Lista"
    Note over OMS,PRO: nadie comanda: cada paso REACCIONA al evento anterior
```

## Caso 2 — Compensación (el ERP rechaza)
```mermaid
sequenceDiagram
    autonumber
    participant LOG as Log de Eventos
    participant INV as Servicio de Inventario
    participant ADE as Adaptador ERP
    participant ERP as ERP (mock/on-prem)

    INV->>LOG: publica InventarioReservado
    LOG-->>ADE: entrega InventarioReservado
    ADE->>ERP: valorizar
    ERP-->>ADE: RECHAZADO (422)
    ADE->>LOG: publica ValorizacionRechazada
    LOG-->>INV: entrega ValorizacionRechazada
    Note over INV: el propio Inventario REACCIONA al evento<br/>(Manejador de Compensación) — nadie se lo ordena
    INV->>INV: libera la reserva
    INV->>LOG: publica InventarioLiberado
```

**Lo que demuestra:** en B la compensación **la dispara un evento** (`ValorizacionRechazada`), no un comando central. Ventaja: autonomía y desacoplamiento; costo: el flujo hay que reconstruirlo con el `correlationId` porque **nadie lo ve completo**.

---
### El contraste, en una línea
- **A (02):** `Saga → INV → WMS → ERP`, y la Saga **ordena** liberar. Estrella = la Saga.
- **B (03):** `evento → INV → evento → ERP → evento`, y el rechazo **gatilla** la liberación. Estrella = el Log de Eventos.

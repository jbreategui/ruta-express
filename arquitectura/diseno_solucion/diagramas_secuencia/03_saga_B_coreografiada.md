# Secuencia — Reserva en Alternativa B (Saga COREOGRAFIADA)

**Mismo escenario que en A**, pero **no hay orquestador**: cada servicio reacciona a un evento del **Log de Eventos** y publica el siguiente. La compensación también es un **evento**, no un comando. Compárese caja por caja con `02_saga_A_orquestada.md`.

## Caso 1 — Éxito (por eventos)
```mermaid
sequenceDiagram
    autonumber
    participant OMS as Servicio de Órdenes
    participant LOG as Log de Eventos
    participant INV as Servicio de Inventario
    participant ADW as Adaptador WMS
    participant WMS as WMS (mock/on-prem)
    participant ADE as Adaptador ERP
    participant ERP as ERP (mock/on-prem)
    participant PRO as Proyector (CQRS)

    OMS->>LOG: publica OrdenValidada
    LOG-->>INV: entrega OrdenValidada
    INV->>INV: reserva atómica (local)
    INV->>LOG: publica InventarioReservado
    LOG-->>ADW: entrega InventarioReservado
    ADW->>WMS: reserva física
    WMS-->>ADW: OK
    ADW->>LOG: publica ReservaFisicaConfirmada
    LOG-->>ADE: entrega ReservaFisicaConfirmada
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
    participant ADW as Adaptador WMS
    participant WMS as WMS (mock/on-prem)
    participant ADE as Adaptador ERP
    participant ERP as ERP (mock/on-prem)

    ADW->>LOG: publica ReservaFisicaConfirmada
    LOG-->>ADE: entrega ReservaFisicaConfirmada
    ADE->>ERP: valorizar
    ERP-->>ADE: RECHAZADO (422)
    ADE->>LOG: publica ValorizacionRechazada
    par Cada servicio REACCIONA al mismo evento — nadie lo ordena
        LOG-->>INV: entrega ValorizacionRechazada
        Note over INV: Manejador de Compensación libera lo local
        INV->>INV: libera la reserva local
        INV->>LOG: publica InventarioLiberado
    and
        LOG-->>ADW: entrega ValorizacionRechazada
        Note over ADW: el Adaptador WMS libera lo FÍSICO
        ADW->>WMS: liberar reserva física
        ADW->>LOG: publica ReservaFisicaLiberada
    end
```

**Lo que demuestra:** en B la compensación **la dispara un evento** (`ValorizacionRechazada`), no un comando central. Tanto lo local (Servicio de Inventario) como lo físico (Adaptador WMS) se liberan porque **ambos reaccionan al mismo evento de rechazo** — sin orquestador. Ventaja: autonomía y desacoplamiento; costo: el flujo hay que reconstruirlo con el `correlationId` porque **nadie lo ve completo**.

---
### El contraste, en una línea
- **A (02):** `Saga → INV → WMS → ERP`, y la Saga **ordena** liberar (físico + local, en orden inverso). Estrella = la Saga.
- **B (03):** `evento → INV → evento → WMS → evento → ERP → evento`, y el rechazo **gatilla** que Inventario y Adaptador WMS liberen cada uno lo suyo. Estrella = el Log de Eventos.

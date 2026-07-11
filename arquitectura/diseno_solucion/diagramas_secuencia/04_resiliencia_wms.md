# Secuencia — Resiliencia hacia el WMS (la lección de Cyber Days)

El WMS es el sistema que se cayó **6 h** en Cyber Days (240k órdenes encoladas). El adaptador aplica **Timeout + Retry (backoff+jitter) + Circuit Breaker**, y garantiza que **la orden no se pierde**. RF-11, RF-16.

## Caso — WMS caído: reintentos, circuito abierto y no-pérdida
```mermaid
sequenceDiagram
    autonumber
    participant SAGA as Orquestador (Saga)
    participant ADP as Adaptador WMS (Circuit Breaker)
    participant WMS as WMS (degradado)
    participant INV as Inventario
    participant Q as Cola de reintento

    SAGA->>ADP: reserva física
    loop Retry con backoff (1s→2s→4s + jitter)
        ADP->>WMS: intentar reserva
        WMS--xADP: timeout / 503
    end
    Note over ADP: 3 fallos consecutivos → Circuit Breaker ABRE<br/>(fail-fast: deja de golpear al WMS)
    ADP-->>SAGA: no disponible
    SAGA->>INV: compensa la reserva local (no confirma estado sin WMS)
    SAGA->>Q: encola la orden para reintento posterior
    Note over SAGA,Q: la orden NO se pierde ni se marca reservada<br/>(exactamente lo que faltó en Cyber Days)

    rect rgb(235,245,235)
    Note over ADP,WMS: ...tras 30 s el breaker pasa a HALF-OPEN...
    ADP->>WMS: 1 llamada de prueba
    WMS-->>ADP: OK (recuperado)
    Note over ADP: breaker CIERRA → se drena la cola de reintento
    end
```

**Lo que demuestra:**
- **Fail-fast:** tras 3 fallos el circuito abre y deja de saturar al WMS ya degradado (evita el efecto cascada).
- **No-pérdida:** la orden se encola, no se descarta ni se confirma en falso (RF-11).
- **Auto-recuperación:** el breaker prueba en *half-open* y, al recuperarse el WMS, se procesa el backlog — lo contrario de las 240k órdenes atascadas del caso.

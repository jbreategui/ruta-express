# Secuencia — Recepción de orden: deduplicación + idempotencia

Cómo el OMS evita el doble procesamiento (los **32k pedidos duplicados** del caso). Aplica a ambas alternativas (ocurre en el Servicio de Órdenes / OMS). RF-01, RF-03, RF-04, RF-05.

```mermaid
sequenceDiagram
    autonumber
    actor C as Cliente B2B
    participant API as API Gateway
    participant OMS as OMS / Servicio de Órdenes
    participant DB as BD (idempotency, orders)
    participant BUS as Bus de Eventos

    C->>API: POST /v1/ordenes (Idempotency-Key)
    API->>OMS: crear orden (autenticado)

    OMS->>DB: ¿existe Idempotency-Key?
    alt Key ya usada (reintento exacto)
        DB-->>OMS: respuesta original
        OMS-->>C: 200 mismo orderId (sin re-procesar)
    else Key nueva
        OMS->>OMS: calcula content_hash (cliente + líneas + ventana)
        OMS->>DB: ¿existe orden con ese hash?
        alt Duplicado (mismo pedido, otra key)
            DB-->>OMS: orden previa
            OMS-->>C: 200 duplicate=true (orderId original)
        else Pedido nuevo
            OMS->>DB: crea orden estado "Validada" + content_hash
            OMS->>DB: guarda evento OrdenValidada en outbox (misma tx)
            Note over OMS,DB: dedup por hash (RF-03) + idempotencia por key (RF-04)<br/>en la misma transacción que el estado
            OMS-->>C: 201 orderId (inicia la Saga de reserva)
            OMS->>BUS: publica OrdenValidada (patrón Outbox)
        end
    end
```

**Lo que demuestra:** un reintento con la **misma key** no crea nada nuevo (idempotencia); el **mismo pedido con otra key** se detecta por **hash de contenido** (deduplicación). Los dos mecanismos juntos cierran la puerta a los duplicados del caso.

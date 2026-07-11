# INI-02 · Integración API-First y Event-Driven — Contexto y problema que resuelve

## Rol de esta iniciativa
INI-02 es la **columna vertebral (sistema nervioso)** de la solución. No entrega una capacidad de negocio visible por sí sola: **hace confiables a INI-01 e INI-03**. Sin un bus de eventos con backpressure, DLQ, secuenciación y replay, la deduplicación del OMS y el store-and-forward móvil **no sobreviven a un pico de campaña**.

## Problema (AS-IS)
Las integraciones son **punto a punto (spaghetti)** entre WMS, TMS, app, portales, ERP y optimizador, sin contratos gobernados ni desacople. Consecuencias del caso:

- **Cyber Days: 240,000 pedidos en cola, WMS caído 6 h, USD 1.1M en penalidades** — la cola hacia el WMS creció sin backpressure ni prioridad por SLA.
- El portal muestra **"intento fallido" después de una entrega exitosa** (eventos fuera de orden, duplicados o perdidos) → el cliente retiene el pago.
- Un cambio de contrato de un cliente **rompe la recepción de órdenes de los demás** (sin versionado).

## Riesgo del anexo que ataca
**Riesgo 1 — Disponibilidad** (y refuerza el Riesgo 2 — Integridad).

## Qué resuelve (TO-BE)
Una capa **API-first + event-driven**: contratos versionados y gobernados, API Management con cuotas/rate limiting, **Bus de Eventos Central**, **backpressure**, **priorización por SLA**, **DLQ**, **secuencia lógica por agregado** y **replay controlado**.

## Metas del Hito 1 que habilita
**99.9% de disponibilidad** en campaña, **98% de tracking confiable**, y **evitar la repetición del USD 1.1M** en penalidades.

## Requerimientos que la componen
- **Funcionales:** RF-12 … RF-21 (10 HDU).
- **No funcionales:** RNF-10 … RNF-18 (`RNF-INI-02.md`).

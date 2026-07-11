# Fase 5b · Nivel 3 — Componentes (Alternativa B)

> **Meta:** entender los 3 diagramas de Nivel 3 de B (Inventario, Log de Eventos, Última Milla) y
> su forma de **cadena/reacción** (vs el hub de A). Fuentes:
> `alternativa_B_coreografiada/03_*.md`, `03b_*.md`, `03c_*.md` y los PNG `B_n3*`.

---

## 1. Recordatorio: qué es el Nivel 3
Abre **UN** contenedor y muestra sus **componentes** internos (piezas lógicas). **Sin íconos de
nube** (se hablan `in-proc`). En B hay **tres** diagramas N3, uno por iniciativa — igual que A.

---

## 2. N3 principal — Servicio de Inventario (INI-01) · forma de CADENA

Abre el **Servicio de Inventario**. La diferencia con A salta a la vista: **no hay una Saga central
(hub)**; los componentes forman una **cadena de reacciones**.

### Componentes, uno por uno (todos 🟢 [NUEVO])
- **Consumidor de Eventos (Inbox)** — *la oreja*
  - Escucha `OrdenValidada` y `ValorizaciónRechazada` del log; **deduplica por identificador de
    evento** (patrón Inbox = idempotencia del consumidor). → RF-16.
- **Manejador de Reserva** — *el que aparta*
  - Reserva **atómica**: solo una gana ante concurrencia (transacción sobre su BD propia). → RF-06.
- **Manejador de Compensación** — *el que se deshace solo*
  - Al escuchar `ValorizaciónRechazada`, **libera la reserva** — **compensación sin orquestador**.
    Esta es la pieza que en A no existe (en A compensa la Saga). → RF-08.
- **Registro Auditable de Movimientos** — cada reserva/liberación con actor, motivo, correlation
  ID; append-only. → RF-07.
- **Reconciliador** — conflictos con almacenes al reconectar. → RF-09.
- **Publicador Outbox** — publica `InventarioReservado/Insuficiente/Liberado` de forma confiable;
  secretos en Key Vault. → RF-14.
- **Proyector de Disponibilidad (CQRS)** — actualiza la proyección de lectura desde los eventos
  confirmados. → RF-10.

### El flujo interno (mira el diagrama `B_n3_inventario.png`)
```
[LOG] ──OrdenValidada──▶ Inbox ──▶ Manejador de Reserva ──▶ reserva en BD ──▶ Outbox ──▶ [LOG]
[LOG] ──Rechazo────────▶ Inbox ──▶ Manejador de Compensación ──▶ libera en BD ──▶ (registra)
[LOG] ──eventos confirmados──▶ Proyector ──▶ read model ──▶ Servicio de Consultas
```
**No hay centro**: entra un evento, un componente reacciona, sale otro evento. Eso es la coreografía.

### Seguridad por conexión (igual de explícita que A)
- Inbox ← Log: `AMQP (TLS)` + correlation ID
- Reserva/Compensación → BD: `TDS · private endpoint (TLS)`
- Outbox → Log: `AMQP (TLS)`; Outbox → Identidad: `Key Vault`

---

## 3. N3 — Log de Eventos (INI-02) · el Event Store

Abre el **Log de Eventos**. La diferencia con el "Bus" de A: aquí el log **retiene** (no solo
transporta). Piezas centrales que A no tiene:
- **Ingesta Append-Only** — escritura inmutable con correlation ID.
- **Almacén de Eventos (Event Store)** — retención larga e inmutable: *el log ES la historia*.
- **Motor de Replay** — **reconstruye estado** reproduciendo el log (no solo reprocesa mensajes).

El resto es como el bus de A: Validador+Versionado de esquemas, Enrutador/Suscripciones,
Reintentos+DLQ, Backpressure, Priorizador por SLA, Secuenciador. Y alimenta a los **Proyectores
(CQRS)**. → RF-14…21.

**Frase clave:** *"En B el log no es tubería, es memoria: nada se pierde (DLQ), nada se duplica
(replay idempotente), nada llega fuera de orden (secuenciador), y cualquier estado se reconstruye
reproduciendo la historia."*

---

## 4. N3 — Backend de Última Milla (INI-03) · casi igual que A

Abre el **Backend de Última Milla**. Los componentes internos son **prácticamente idénticos a A**
(API Móvil, Inbox, Store-and-Forward, Gestor de Evidencias, Taxonomía de Excepciones, Acciones
Automáticas, Acciones Preventivas, Tracking) — porque la última milla ya es reactiva por naturaleza
(offline, store-and-forward).

**Lo que cambia en B está en el borde:** agrega un **Publicador Outbox** explícito que **publica
entrega/excepción/tracking como evento al Log** (fuente de verdad), en lugar de reportar a un bus de
transporte. Es un participante autónomo de la coreografía. → RF-22…29.

---

## 5. El contraste que resume todo: A = hub, B = cadena

| | **A — Orquestada** | **B — Coreografiada** |
|---|---|---|
| Forma del N3 de inventario | **Hub** (flechas salen de la Saga) | **Cadena** (evento→componente→evento) |
| Quién compensa | La Saga lo ordena | Un **Manejador de Compensación** que reacciona solo |
| El bus/log | transporta | **retiene** (Event Store + Replay) |
| Última milla | reporta al bus | publica hechos al log (Outbox explícito) |

---

## Cómo defenderlo ante el comité
1. *"Los tres N3 de B tienen forma de cadena: no hay orquestador; cada componente reacciona a un
   evento y publica el suyo."*
2. *"La compensación es un componente autónomo (Manejador de Compensación), no una orden central."*
3. *"El Log de Eventos es un Event Store: retiene y reconstruye por replay; el bus de A solo
   transportaba."*
4. *"La última milla es casi igual a la de A, más un Outbox que publica hechos al log."*

---

## Archivos fuente
- `alternativa_B_coreografiada/03_nivel3_componentes_inventario.md` → `B_n3_inventario.png`
- `alternativa_B_coreografiada/03b_nivel3_componentes_log_eventos.md` → `B_n3b_log_eventos.png`
- `alternativa_B_coreografiada/03c_nivel3_componentes_ultima_milla.md` → `B_n3c_ultima_milla.png`
- Contraste con A: [fase_4_c4_nivel3_componentes.md](fase_4_c4_nivel3_componentes.md)

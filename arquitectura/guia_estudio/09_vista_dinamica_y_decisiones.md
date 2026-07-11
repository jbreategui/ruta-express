# 09 — Vista dinámica (secuencia) + Decisiones (ADRs)

> **Meta:** entender la vista que **complementa** al C4 estático (los diagramas de secuencia — el
> comportamiento en el tiempo) y las decisiones de arquitectura (ADRs) que sostienen todo el
> diseño. Fuentes: `diagramas_secuencia/01…04_*.md`, `decisiones_diseño.md`.

---

## PARTE A — La vista dinámica (diagramas de secuencia)

### ¿Por qué otra vista si ya tengo el C4?
El C4 es **estático**: muestra las piezas y cómo se conectan, pero no el **orden en el tiempo** ni
las **decisiones** (¿qué pasa si el ERP rechaza? ¿si el WMS se cae?). El diagrama de secuencia
muestra **el comportamiento**: quién llama a quién, en qué orden, y qué pasa en cada `alt`
(alternativa/decisión). Es la película; el C4 es la foto.

Hay **4 diagramas de secuencia**, y juntos cuentan la ruta crítica del caso:

### 1. Recepción de orden — dedup + idempotencia (aplica a A y B)
Cómo el OMS evita los **32,000 duplicados** del caso. Dos mecanismos juntos:
- **Idempotency-Key:** si llega un reintento con la **misma key** → devuelve el mismo `orderId`, no
  reprocesa (idempotencia, RF-04).
- **Content-hash:** si es el **mismo pedido con otra key** → lo detecta por hash de contenido
  (cliente + líneas + ventana) y responde `duplicate=true` (deduplicación, RF-03).
- Clave técnica: el estado y el evento (en el **outbox**) se guardan en la **misma transacción**.

### 2. Saga A — ORQUESTADA (éxito y compensación)
La reserva con un **director**. Todas las flechas de decisión **salen de la Saga**:
- **Éxito:** Saga → reserva local → WMS (reserva física) → ERP (valorizar) → publica `OrdenLista`.
- **Compensación:** si el ERP **rechaza (422)** → la Saga **decide** y ordena `liberar` → publica
  `OrdenFallida`. Todo con correlationId.
- Lo que demuestra: coordinación y compensación **centralizadas** (control y visibilidad). RF-08.

### 3. Saga B — COREOGRAFIADA (mismo caso, sin director)
Idéntico escenario, pero **nadie orquesta**: cada servicio reacciona a un evento del Log:
- **Éxito:** OMS publica `OrdenValidada` → Inventario reacciona y reserva → publica
  `InventarioReservado` → Adaptador ERP reacciona y valoriza → publica `ValorizaciónConfirmada` →
  el Proyector actualiza el read model.
- **Compensación:** el Adaptador publica `ValorizaciónRechazada` → el **propio Inventario reacciona**
  (Manejador de Compensación) y libera. **Nadie se lo ordena.**
- El contraste en una línea:
  - **A:** `Saga → INV → WMS → ERP`, la Saga **ordena** liberar. Estrella = la Saga.
  - **B:** `evento → INV → evento → ERP → evento`, el rechazo **gatilla** la liberación. Estrella =
    el Log de Eventos.

### 4. Resiliencia del WMS — la lección de Cyber Days
Qué pasa cuando el WMS (que cayó 6h) falla. El **Adaptador WMS** aplica **Timeout + Retry
(backoff+jitter) + Circuit Breaker**:
- Reintenta 1s → 2s → 4s. Tras **3 fallos**, el **Circuit Breaker ABRE** (fail-fast: deja de
  golpear al WMS degradado).
- La orden **no se pierde**: se encola para reintento y se **compensa la reserva local** (no se
  marca reservada en falso).
- Tras 30s el breaker pasa a **half-open**, prueba una llamada; si el WMS revive, **CIERRA** y se
  drena la cola. Lo contrario de las 240k órdenes atascadas del caso.
- **Ojo (fundamento):** al WMS lo protege este **Adaptador con Circuit Breaker**, NO el bus. El bus
  amortigua la propagación de *eventos*; la reserva física es una llamada directa protegida aquí.

---

## PARTE B — Las decisiones de arquitectura (ADRs)

Un ADR (Architectural Decision Record) documenta **una decisión importante**: contexto → opciones →
decisión → consecuencias. Es lo que te permite responder *"¿por qué elegiste esto y no aquello?"*
ante el comité. Hay **9 ADRs**:

| ADR | Decisión | En una frase |
|---|---|---|
| **01** | Multicloud **best-of-breed** | Cada dominio en su mejor nube (Azure núcleo, AWS última milla, GCP analítica), sin migraciones forzadas |
| **02** | **Hub en Azure** | El centro de gravedad (bus, gobierno de API, identidad) va en Azure para minimizar saltos intercloud. Es decisión **dentro de ambas** alternativas, no una alternativa |
| **03** | **Orquestación (A) vs Coreografía (B)** | La bifurcación real del hito: es un trade-off genuino, por eso se modelan las dos |
| **04** | **Patrón Outbox** | Evento + estado en la misma transacción local → cero eventos perdidos aunque el bus caiga (a costa de entrega "al menos una vez" → exige dedup) |
| **05** | **API-First** con OpenAPI | El contrato se diseña antes del código y se importa al gateway; el contrato es la fuente de verdad |
| **06** | **GCP** para analítica | Ya corre ahí (Hito 1); BigQuery/Vertex son su fortaleza; migrar sería costo sin beneficio |
| **07** | **DR por criticidad** | No una sola estrategia: Warm Standby al núcleo, cross-region a evidencias, PITR a DynamoDB, etc. |
| **08** | **VPN IPsec** primero, líneas dedicadas después; **mTLS** como capa extra | Arranque barato y seguro, con camino de crecimiento; defensa en profundidad |
| **09** | **Event Sourcing + CQRS completo solo en B** | En A el estado vive en la BD y CQRS es liviano; en B el log es la fuente de verdad |

**El patrón que verás repetido:** cada ADR ofrece **opciones reales** y explica por qué se
descartaron las otras — no "elegí X porque sí". Eso es lo que un comité valora.

---

## Cómo defenderlo ante el comité
1. *"El C4 muestra la estructura; los diagramas de secuencia muestran el comportamiento — qué pasa
   cuando el ERP rechaza o el WMS se cae."*
2. *"La dedup+idempotencia cierra los 32k duplicados; la Saga (A ordena / B reacciona) resuelve la
   consistencia; el Circuit Breaker protege al WMS que cayó en Cyber Days."*
3. *"Cada decisión importante está en un ADR con sus opciones y consecuencias — puedo justificar por
   qué elegí cada camino y por qué descarté los otros."*

---

## Archivos fuente
- `diagramas_secuencia/01_recepcion_orden.md` — dedup + idempotencia
- `diagramas_secuencia/02_saga_A_orquestada.md` — Saga con director
- `diagramas_secuencia/03_saga_B_coreografiada.md` — Saga por eventos
- `diagramas_secuencia/04_resiliencia_wms.md` — Circuit Breaker (lección de Cyber Days)
- `decisiones_diseño.md` — ADR-01 … ADR-09
- `lineamientos_aplicados.md` — matriz de los 54 lineamientos (ARQ/ESC/INT/OBS/SEG)

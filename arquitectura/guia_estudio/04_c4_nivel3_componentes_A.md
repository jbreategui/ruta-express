# Fase 4 — C4 Nivel 3: Componentes

> **Meta de la fase:** entender cómo se abre UN contenedor del Nivel 2 en sus piezas internas
> (componentes), por qué aquí NO van íconos de nube, y cómo cada componente muestra sus protocolos
> y seguridad. Fuente: `alternativa_A_orquestada/03_nivel3_componentes_inventario.md`.

---

## 1. Qué es el Nivel 3 (vs el Nivel 2)

Responde: **"¿Qué hay DENTRO de UN contenedor y cómo colaboran sus piezas?"** En el Nivel 2 el OMS
era una caja; aquí la **abrimos**.

| | Nivel 2 | Nivel 3 |
|---|---|---|
| Unidad | contenedor (app/BD/bus) | **componente** (pieza lógica dentro de un contenedor) |
| Cuántos abre | todos | **UNO solo** por diagrama |
| Íconos de nube | sí | **NO** |
| Comunicación | protocolos de red | mayormente **`in-proc`** (mismo proceso) |

**Regla de oro:** un diagrama = un contenedor abierto. Aquí abrimos el **mismo dominio
(Inventario/Reserva) que la Alternativa B**, para compararlas caja por caja.

---

## 2. ¿Por qué el Nivel 3 NO lleva íconos de nube?

Porque los componentes son **piezas lógicas de código dentro del mismo contenedor**, no servicios
de nube desplegables por separado. La "Saga" y el "Manejador de Reserva" viven en el **mismo pod de
AKS** y se hablan `in-proc` (llamadas de función), no por la red. Un ícono de Azure/AWS representa
un servicio desplegable; un componente no lo es. Por eso el N3 se dibuja con **cajas limpias con
texto** (notación C4 pura), no con logos de nube.

---

## 3. Qué contenedor abre este diagrama

Abre el **OMS**, y dentro de él el **sub-dominio de reserva de inventario** (corazón de INI-01,
RF-06/08/09). La validación/deduplicación/idempotencia (RF-01…05) están aguas arriba en el mismo
OMS; aquí se enfoca solo la reserva para contrastarla con la Alternativa B.

---

## 4. Los componentes, uno por uno (todos 🟢 [NUEVO], dentro del OMS)

- **Orquestador de Reserva (Saga)** — *el director*
  - COMANDA cada paso: reserva física, valorización y la **compensación** si algo falla. Punto
    único de control; casi todas las flechas salen de él (forma de **hub**). → RF-08.
- **Manejador de Reserva** — *el que aparta el stock*
  - Al recibir el comando, hace la **reserva atómica**; decide Reservado/Insuficiente. Control:
    *solo una gana ante concurrencia* (transacción sobre la BD — el oversell probado en el MVP). → RF-06.
- **Inventario y Reservas** — disponibilidad y estado del stock. → RF-06.
- **Registro Auditable de Movimientos** — cada reserva/liberación con **actor, motivo, correlation
  ID**; append-only (sin borrado). → RF-07.
- **Reconciliador** — conflictos entre WMS central y almacenes locales (los 4,900 del caso). → RF-09.
- **Adaptador de Transición WMS** — *el escudo del WMS*
  - Habla con el WMS on-premises y lo protege con **Circuit Breaker + Timeout + Retry
    (backoff+jitter)**. **Este** es el componente que evita que el WMS caiga ante un pico (NO el
    Bus). → RF-11.
- **Publicador Outbox** — *el mensajero confiable*
  - Lee el outbox de la BD y publica el resultado al Bus de forma confiable. Secretos en **Key
    Vault**. → RF-14.

---

## 5. Las conexiones y su seguridad

- **Internas (`in-proc`):** Saga→Manejador, Manejador→Inventario, etc. (mismo proceso, sin red).
- **Hacia afuera (seguridad explícita):**
  - Adaptador → WMS: `API · VPN (IPsec)`
  - Saga → ERP: `API · VPN (IPsec)`
  - Manejador → Azure SQL: `TDS · private endpoint (TLS)`
  - Outbox → Bus: `AMQP (TLS)`
  - Outbox → Identidad: `Key Vault` (secretos)

Esto responde el pedido del profe ("secretos, conexiones, seguridad a nivel de componente"): el N3
muestra exactamente cómo y con qué protección cada componente cruza un límite de confianza.

---

## 6. El contraste A vs B (por qué este diagrama es un hub)

| | **A — Orquestada (este)** | **B — Coreografiada** |
|---|---|---|
| ¿Quién dispara la reserva? | La **Saga comanda** | Un **evento** (OrdenValidada) por el Inbox |
| Compensación | La Saga la **ordena** | El servicio **reacciona** a un evento de rechazo |
| Forma del diagrama | **Hub**: flechas salen de la Saga | **Cadena**: evento→manejador→evento |
| Ventaja | Control y visibilidad centrales | Autonomía y desacoplamiento |

Se profundiza en la Fase 5. Idea corta: en A hay un **director** (la Saga); en B, una **coreografía**
(cada uno reacciona solo).

---

## 7. Los otros dos diagramas de Nivel 3
Además del de inventario, hay N3 para las otras dos iniciativas (mismo criterio: abrir UN
contenedor):
- **Bus de Eventos** (`03b_...bus_eventos.md`, INI-02): ingesta, validador de esquemas, enrutador,
  reintentos+DLQ, backpressure, priorizador, replay, secuenciador.
- **Backend de Última Milla** (`03c_...ultima_milla.md`, INI-03): API móvil, inbox (dedup), sync
  store-and-forward, gestor de evidencias, taxonomía de excepciones, tracking.

---

## Cómo defenderlo ante el comité
1. *"El Nivel 3 abre UN contenedor —el OMS— y muestra sus componentes internos."*
2. *"No hay íconos de nube porque son piezas lógicas dentro del mismo proceso; se hablan in-proc."*
3. *"La Saga es el director (hub); el Adaptador WMS con Circuit Breaker protege al on-prem; el
   Outbox publica confiablemente."*
4. *"Cada cruce de límite muestra su seguridad: VPN IPsec al on-prem, private endpoint+TLS a la BD,
   Key Vault para secretos."*

---

## Archivos fuente de esta fase
- `diseno_solucion/alternativa_A_orquestada/03_nivel3_componentes_inventario.md` — diagrama +
  tabla de componentes + contraste A/B
- `03b_nivel3_componentes_bus_eventos.md` y `03c_nivel3_componentes_ultima_milla.md` — los otros
  dos dominios
- `diseno_solucion/diagramas_python/A_n3_reserva_inventario.png` (y `A_n3b_*`, `A_n3c_*`)
- Resiliencia del WMS (vista dinámica): `diagramas_secuencia/04_resiliencia_wms.md`

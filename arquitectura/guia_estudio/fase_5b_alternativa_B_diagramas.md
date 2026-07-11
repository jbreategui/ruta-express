# Fase 5b — La Alternativa B (Coreografiada) por niveles

> **Meta:** entender la Alternativa B con sus propios diagramas (N1, N2, N3), contrastando con A.
> Fuentes: `alternativa_B_coreografiada/01…03_*.md` y `diagramas_python/B_n*.png`.

---

## Nivel 1 — Contexto: idéntico a A

El N1 de B es **exactamente el mismo** que el de A (mismo sistema central, mismas 4 personas,
mismos 6 sistemas externos). Es correcto, no pereza: ambas resuelven el **mismo alcance** con los
**mismos actores**. Lo que cambia (orquestación vs coreografía) recién se ve en N2 y N3. Regla: el
contexto no depende de la arquitectura interna.

---

## Nivel 2 — Contenedores: aquí empieza la diferencia

Fuera de Azure, A y B son **iguales** (AWS última milla y GCP analítica no cambian). Toda la
diferencia está en el núcleo Azure:

| Núcleo Azure | **A (orquestada)** | **B (coreografiada)** |
|---|---|---|
| El "cerebro" | **1 OMS monolítico** que orquesta | **se parte en servicios autónomos** |
| Órdenes | dentro del OMS | **Servicio de Órdenes** (separado) |
| Inventario | dentro del OMS | **Servicio de Inventario** (separado, autónomo) |
| WMS/ERP | el OMS los llama **directo** | **Adaptadores WMS/ERP** que reaccionan a eventos |
| Consultas | API + read model liviano | **Servicio de Consultas (CQRS)** dedicado |
| El bus | "Bus de Eventos" (transporte) | **"Log de Eventos" = fuente de verdad** (Event Sourcing) |

**Lo que salta a la vista en el diagrama de B:**
1. **No hay orquestador central** — varios servicios chicos e independientes en vez de un OMS gordo.
2. **El "Log de Eventos" es el corazón**, no un mensajero: es la **fuente de verdad** (Event
   Sourcing); el estado se reconstruye reproduciendo el log.
3. **Hasta el WMS/ERP se hablan por eventos:** los Adaptadores escuchan eventos, traducen al
   on-prem y publican el resultado como evento. Nadie llama directo.
4. **CQRS explícito:** un Servicio de Consultas separado que solo lee de proyecciones (comandos por
   un lado, lecturas por otro).

### El flujo de B: la "Saga coreografiada" (nadie manda, todo es reacción)
```
1. Servicio de Órdenes  ──publica──▶ "OrdenValidada" ──▶ [LOG DE EVENTOS]
2. [LOG] ──▶ Servicio de Inventario ──reserva──▶ publica "InventarioReservado" ──▶ [LOG]
3. [LOG] ──▶ Adaptador ERP ──valoriza──▶ publica "ValorizaciónConfirmada"/"Rechazada" ──▶ [LOG]
4. Si "Rechazada": [LOG] ──▶ Servicio de Inventario ──▶ publica "InventarioLiberado" (SE COMPENSA SOLO)
5. Los proyectores ──▶ read models ──▶ Portal/TMS ven el estado final
```
En A la Saga *ordenaba* cada paso; en B **nadie ordena** — cada servicio escucha un evento y
reacciona. La compensación no es una orden del jefe, es *"escuché el rechazo, me libero solo"*.

---

## Nivel 3 — Componentes: cadena, no hub

El N3 de B abre el **Servicio de Inventario** (forma de **cadena/reacción**):
- **Inbox** (escucha eventos y deduplica por identificador de evento) → **Manejador de Reserva**
  (reserva atómica) → **Publicador Outbox** (publica el resultado).
- **Manejador de Compensación** que reacciona a `ValorizaciónRechazada` y **se libera solo** — sin
  orquestador.
- **Proyector (CQRS)** que actualiza el read model desde los eventos confirmados.

Contraste visual: **A = hub** (flechas salen de la Saga central); **B = cadena** (evento→servicio→
evento, sin centro).

---

## El trade-off de B (lo que el comité debe oír)

| | B **gana** | B **paga** |
|---|---|---|
| Autonomía | agregar un consumidor no toca a nadie | — |
| Auditoría | el log **ES** la historia (RF-07/19 nativos) | retención larga del log (costo) |
| Resiliencia | no hay orquestador que caer | — |
| Seguimiento | — | nadie "ve" la Saga completa → reconstruir por correlation ID |
| Consistencia | — | **eventual** en todas las lecturas (CQRS) |
| Equipo | — | Event Sourcing exige madurez |

Por eso, aunque B es más elegante a largo plazo, **se recomienda A** para este caso y el MVP:
RutaExpress necesita **ver y controlar** cada orden (lo que faltó en Cyber Days), y B lo dificulta.

---

## Archivos fuente
- `alternativa_B_coreografiada/01_nivel1_contexto.md` (idéntico a A)
- `alternativa_B_coreografiada/02_nivel2_contenedores.md` (+ sección "La Saga coreografiada")
- `alternativa_B_coreografiada/03_nivel3_componentes_inventario.md`
- `diagramas_python/B_n1_contexto.png`, `B_n2_contenedores.png`, `B_n3_inventario.png`

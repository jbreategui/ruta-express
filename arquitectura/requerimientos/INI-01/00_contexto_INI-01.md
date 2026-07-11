# INI-01 · Gestión unificada de órdenes e inventario — Contexto y problema que resuelve

## Problema (AS-IS)
Hoy no existe **una sola verdad** del pedido ni del inventario. Los datos viven en islas (WMS on-premises, TMS en Azure, app en AWS, ERP on-premises) que no se hablan bien. Esto produce, según el caso:

- **Cyber Days:** el WMS se degradó **6 horas** → **240,000 pedidos en cola**, 19% de entregas tardías y **USD 1.1M en penalidades** — el detonante del rediseño.
- **32,000 pedidos duplicados** por reintento de API con identificador externo cambiado → doble reserva de inventario y rutas fantasma.
- **6% de órdenes con defectos** de datos (dirección, SKU) que explotan aguas abajo.
- **4,900 movimientos en conflicto** al reconectar un almacén y **18,000 pedidos retrasados** por sincronización.
- **2.8% de movimientos de inventario** genera ajuste.

## Riesgo del anexo que ataca
**Riesgo 2 — Integridad** (y mitiga parte del Riesgo 1 — Disponibilidad).

## Qué resuelve (TO-BE)
Evolucionar el Orquestador de Pedidos (APP-02) a un **OMS centralizado** que gobierna el ciclo de vida de la orden: validación, **deduplicación por hash + idempotencia**, **estado canónico**, **vista única de inventario**, **reserva/liberación coordinada** entre WMS y ERP (Saga con compensación) y **reconciliación** de conflictos.

## Metas del Hito 1 que habilita
Reducir el ciclo orden→despacho de **9.5 h a 4 h**; base para subir el cumplimiento de promesa de **82% a 94%**.

## Requerimientos que la componen
- **Funcionales:** RF-01 … RF-11 (11 HDU).
- **No funcionales:** RNF-01 … RNF-09 (`RNF-INI-01.md`).

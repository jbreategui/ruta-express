# INI-03 · Modernización de última milla y gestión de excepciones — Contexto y problema que resuelve

## Problema (AS-IS)
La última milla depende de conductores con **conectividad variable** y de excepciones sin normalizar. Consecuencias del caso:

- **1,200 entregas quedaron sin firma digital** por pérdida de evidencias offline (reinstalación/cambio de equipo) → el cliente **retuvo el pago hasta una conciliación manual** por falta de sustento.
- **Una cadena de retail retuvo USD 2.4M** (incidente distinto): sus reportes indicaban menos entregas exitosas que las reales, y la **conciliación tomó 23 días** por la falta de trazabilidad y evidencias íntegras.
- Excepciones con **texto libre y categorías distintas** entre app, TMS y CRM → el algoritmo de rutas no aprende y no se puede conciliar.
- **12.5% de entregas fallidas** (≈ 8,500 paquetes/día), de las cuales el **34% se relaciona con dirección o ausencia** — prevenibles antes de salir a ruta.
- **18,000 pedidos retrasados** por sincronización deficiente entre sistemas y **8% de eventos de tracking** llega con más de 20 minutos de retraso.

## Riesgo del anexo que ataca
**Riesgo 3 — Operación** (errores humanos y datos de excepción poco normalizados).

## Qué resuelve (TO-BE)
Fortalecer la App de Conductores (APP-15) con **operación offline-first**, **almacenamiento local cifrado**, **sincronización store-and-forward con confirmación backend**, **taxonomía única de excepciones**, **acciones automáticas y preventivas**, **evidencias con hash de integridad** y **preservación ante cambio de dispositivo**.

## Metas del Hito 1 que habilita
Reducir las entregas fallidas de **12.5% a 7%** y alcanzar **tracking confiable del 98%**.

## Requerimientos que la componen
- **Funcionales:** RF-22 … RF-29 (8 HDU).
- **No funcionales:** RNF-19 … RNF-27 (`RNF-INI-03.md`).

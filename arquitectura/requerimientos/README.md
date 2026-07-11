# Requerimientos TO-BE — Hito 2 · RutaExpress (Grupo 6)

Requerimientos Funcionales (HDU en Gherkin) y No Funcionales para las 3 iniciativas priorizadas del ADM-F. Un `.md` por HDU. **Set consolidado: 29 RF únicos (RF-01…29)**, sin redundancias (ver nota de consolidación al final).

| Iniciativa | Riesgo del anexo | RF | RNF | Contexto |
|---|---|---|---|---|
| **INI-01** · Gestión unificada de órdenes e inventario | Riesgo 2 — Integridad | RF-01…11 | RNF-01…09 | [00_contexto_INI-01](INI-01/00_contexto_INI-01.md) |
| **INI-02** · Integración API-First y Event-Driven | Riesgo 1 — Disponibilidad | RF-12…21 | RNF-10…18 | [00_contexto_INI-02](INI-02/00_contexto_INI-02.md) |
| **INI-03** · Última milla y gestión de excepciones | Riesgo 3 — Operación | RF-22…29 | RNF-19…27 | [00_contexto_INI-03](INI-03/00_contexto_INI-03.md) |

---

## INI-01 · Gestión unificada de órdenes e inventario (RF-01…11)

| RF | HDU | Valor (para…) |
|---|---|---|
| RF-01 | Registrar orden con identificador interno único | Trazabilidad desde el ingreso sin depender del ID del cliente |
| RF-02 | Validar datos obligatorios y reglas logísticas | Que un error de datos no explote en almacén/ruta/entrega |
| RF-03 | Deduplicar pedidos | Evitar el doble procesamiento (lote de 32,000) |
| RF-04 | Garantizar idempotencia en reintentos | Que un reintento no genere doble orden/reserva/movimiento |
| RF-05 | Mantener estado canónico de la orden | Que todos consulten la misma verdad operativa |
| RF-06 | Consultar disponibilidad antes de reservar | Comprometer solo stock elegible |
| RF-07 | Registrar eventos auditables de inventario | Reconstruir cada cambio con responsable y motivo |
| RF-08 | Coordinar reserva física (WMS) y valorización (ERP) | Operación y liquidación con datos consistentes |
| RF-09 | Reconciliar conflictos de inventario | Reducir los 18,000 pedidos retrasados |
| RF-10 | Exponer APIs de consulta de orden e inventario | Operar con información confiable |
| RF-11 | Compatibilidad transicional con WMS on-premises | No interrumpir la operación durante la transición |

## INI-02 · Integración API-First y Event-Driven (RF-12…21)

| RF | HDU | Valor (para…) |
|---|---|---|
| RF-12 | Registrar y publicar contratos de API y eventos | Que el cambio de un cliente no rompa a los demás |
| RF-13 | Aplicar seguridad, cuotas y rate limiting | Que un cliente que abusa no degrade el servicio |
| RF-14 | Publicar eventos canónicos | Que si un sistema cae, los eventos no se pierdan ni se apilen |
| RF-15 | Validar esquemas de eventos | Evitar datos incompatibles aguas abajo |
| RF-16 | Entrega confiable de eventos: reintentos con DLQ | No perder ningún evento aunque un consumidor esté caído |
| RF-17 | Aplicar backpressure ante degradación | No repetir el colapso de Cyber Days (240k en cola) |
| RF-18 | Priorizar eventos por criticidad y SLA | Que en un pico lo crítico se procese primero |
| RF-19 | Ejecutar replay controlado | Recuperar un consumidor sin duplicar efectos |
| RF-20 | Conservar la secuencia lógica por agregado | Que nunca se vea "fallido" tras una entrega exitosa |
| RF-21 | Convivir con integraciones punto a punto | Migrar sin romper la operación |

## INI-03 · Última milla y gestión de excepciones (RF-22…29)

| RF | HDU | Valor (para…) |
|---|---|---|
| RF-22 | Operar entregas offline con persistencia local | Continuar la ruta en zonas sin señal sin perder lo capturado |
| RF-23 | Sincronización confiable store-and-forward | Enviar pendientes en orden, con ACK y reintento, sin perder ni duplicar |
| RF-24 | Taxonomía única de excepciones con motivo obligatorio | Mismos códigos en app/TMS/CRM/portal, sin texto libre |
| RF-25 | Automatizar acciones por excepción | Reintento/devolución/escalamiento sin gestión manual |
| RF-26 | Gestión de evidencias con referencia a la orden | Demostrar cumplimiento y resolver observaciones |
| RF-27 | Preservar evidencias ante cambio de dispositivo | Evitar entregas sin firma (las 1,200 del caso) |
| RF-28 | Registrar y sincronizar ubicación cada 2 min | Tracking confiable y trazabilidad de ruta |
| RF-29 | Ejecutar acciones preventivas por riesgo | Reducir el 34% de fallas por dirección/ausencia |

---

## Nota de consolidación (37 → 29 RF)

Se depuró el set original para dejar **solo lo necesario**, sin redundancias:

- **Fusiones (mismo mecanismo):** *reintentos + DLQ* → RF-16 · *offline + persistencia local* → RF-22 · *store-and-forward + confirmación backend + reintento* → RF-23 · *taxonomía + motivo obligatorio* → RF-24.
- **Quitados por ser NFR o redundantes:** *tableros de salud* (observabilidad → RNF/lineamiento) · *estado consistente portal/CRM* (lo garantiza la taxonomía RF-24 + la secuencia RF-20) · *priorización de órdenes en el OMS* (se consolida en la del bus, RF-18; el OMS solo etiqueta el SLA en RF-02).
- **Atributos de calidad movidos a RNF:** cifrado local (RNF-20) e integridad por hash de evidencias (RNF-25).

---
*Proyecto Integrador Final — Arquitectura de Soluciones Multinube — UTEC · Grupo 6 RutaExpress · Hito 2*

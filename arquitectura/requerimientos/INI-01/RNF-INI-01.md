# Requerimientos No Funcionales (RNF) — INI-01

**Iniciativa:** INI-01 · Gestión unificada de órdenes e inventario end-to-end
**Total RNF:** 9 · **Rango de códigos:** RNF-01 … RNF-09

| ID | Requerimiento no funcional | Criterio de aceptación |
|---|---|---|
| RNF-01 | Disponibilidad del OMS de al menos 99.9% en ventanas críticas de campaña. | Monitoreo mensual evidencia disponibilidad ≥ 99.9%, excluyendo ventanas aprobadas de mantenimiento. |
| RNF-02 | Tiempo de respuesta para validación sin reserva menor a 500 ms p95. | Pruebas de rendimiento validan p95 < 500 ms con el volumen nominal del caso (68,000 órdenes/día). |
| RNF-03 | Tiempo de respuesta para reserva de inventario menor a 2 s p95. | Pruebas integradas OMS–WMS Cloud validan p95 < 2 s. |
| RNF-04 | Escalabilidad para soportar el pico de campaña del caso (~2.6× el promedio). | Pruebas de carga demuestran hasta 180,000 órdenes/día y 210,000 movimientos de inventario/día sin pérdida de eventos. |
| RNF-05 | Trazabilidad end-to-end con correlation ID obligatorio. | El 100% de órdenes, reservas, liberaciones y movimientos se rastrea en logs, métricas y eventos con correlation ID presente. |
| RNF-06 | Seguridad por mínimo privilegio y cifrado en tránsito y reposo. | Las APIs usan autenticación/autorización, TLS y secretos gestionados centralmente. |
| RNF-07 | Recuperabilidad ante fallas de integración (escenario Cyber Days). | Tras una indisponibilidad de hasta 6 h de un sistema integrado, el backlog acumulado se procesa en ≤ 2 h con 0 órdenes perdidas y 0 duplicadas. |
| RNF-08 | Auditoría completa para orden e inventario según política contractual y regulatoria. | Las consultas históricas muestran cambios, responsables y motivos sin alteración manual no auditada, con retención mínima de 5 años (propuesta, sujeta a política contractual). |
| RNF-09 | Consistencia eventual controlada entre OMS, WMS Cloud, TMS y ERP. | Convergencia entre sistemas en ≤ 5 minutos p95; toda diferencia queda visible con estado de sincronización y mecanismo de compensación. |

---
*Proyecto Integrador Final — Arquitectura de Soluciones Multinube — UTEC · Grupo 6 RutaExpress*

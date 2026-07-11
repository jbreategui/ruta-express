# Requerimientos No Funcionales (RNF) — INI-02

**Iniciativa:** INI-02 · Integración API-First y Event-Driven
**Total RNF:** 9 · **Rango de códigos:** RNF-10 … RNF-18

| ID | Requerimiento no funcional | Criterio de aceptación |
|---|---|---|
| RNF-10 | Disponibilidad de la capa de integración de al menos 99.9%. | Monitoreo mensual evidencia cumplimiento del objetivo. |
| RNF-11 | Latencia de publicación de eventos menor a 1 s p95 para eventos críticos. | Pruebas de rendimiento validan p95 < 1 s tanto en volumen nominal (68,000 órdenes/día) como en el pico de campaña de RNF-16. |
| RNF-12 | Durabilidad de mensajes críticos. | Ningún evento aceptado se pierde ante falla de consumidor o reinicio de la plataforma. |
| RNF-13 | Seguridad de APIs y eventos con cifrado en tránsito y control de acceso. | Todo endpoint usa TLS, autenticación y autorización por rol/cliente. |
| RNF-14 | Compatibilidad hacia atrás por al menos dos versiones de contrato activas. | Los consumidores existentes siguen operando durante la ventana de migración (mínimo 90 días o un ciclo de campaña completo, lo que sea mayor). |
| RNF-15 | Observabilidad con correlation ID en el 100% de eventos y solicitudes. | Las trazas permiten reconstruir el flujo completo de una orden o entrega. |
| RNF-16 | Escalabilidad elástica para picos de campaña. | La plataforma procesa 180,000 órdenes/día y más de 130,000 eventos de tracking en campaña sin pérdida de mensajes y sin exceder los umbrales de RNF-10 y RNF-11. |
| RNF-17 | Gobernanza de cambios. | Ningún contrato productivo se modifica sin aprobación, versionado y pruebas de contrato. |
| RNF-18 | Portabilidad de contratos entre nubes (evitar lock-in de integración). | Los contratos de API y eventos se definen con estándares abiertos (OpenAPI, JSON Schema) y las políticas de integración son reproducibles en cualquiera de las nubes candidatas sin reescritura de los consumidores. |

---
*Proyecto Integrador Final — Arquitectura de Soluciones Multinube — UTEC · Grupo 6 RutaExpress*

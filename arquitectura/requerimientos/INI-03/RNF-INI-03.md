# Requerimientos No Funcionales (RNF) — INI-03

**Iniciativa:** INI-03 · Modernización de última milla y gestión de excepciones
**Total RNF:** 9 · **Rango de códigos:** RNF-19 … RNF-27

| ID | Requerimiento no funcional | Criterio de aceptación |
|---|---|---|
| RNF-19 | La app debe funcionar offline durante una jornada de ruta, con mínimo 8 horas de captura. | Pruebas de campo validan captura y consulta sin conectividad durante la jornada objetivo. |
| RNF-20 | El almacenamiento local debe estar cifrado. | Cifrado en reposo con algoritmo estándar de la industria (AES-256 o equivalente), verificado en auditoría de seguridad. |
| RNF-21 | Sincronización con garantía de no pérdida funcional de datos. | Los eventos y evidencias capturados offline se sincronizan o quedan pendientes con causa visible. |
| RNF-22 | Tiempo de sincronización menor a 5 min para el backlog de una jornada al recuperar conectividad. | Pruebas de campo con el backlog de una jornada de ruta (8 h de eventos y evidencias) validan sincronización p95 < 5 min y reducción de eventos con retraso > 20 min. |
| RNF-23 | Usabilidad para operación en ruta. | El conductor registra una entrega o excepción en menos de 5 pasos operativos. |
| RNF-24 | Observabilidad de eventos offline y reintentos. | La operación puede ver pendientes, fallidos, confirmados y DLQ por conductor/ruta. |
| RNF-25 | Integridad de evidencias. | Toda firma/foto/GPS tiene hash, timestamp, usuario/dispositivo y correlation ID. |
| RNF-26 | Compatibilidad con dispositivos definidos por la operación. | La solución funciona en las versiones Android/iOS y modelos de la lista de homologación vigente de la operación. |
| RNF-27 | Capacidad para picos de tracking en campaña. | El backend procesa más de 130,000 eventos de tracking diarios sin pérdida, con alertas cuando un evento supera 20 minutos de retraso. |

---
*Proyecto Integrador Final — Arquitectura de Soluciones Multinube — UTEC · Grupo 6 RutaExpress*

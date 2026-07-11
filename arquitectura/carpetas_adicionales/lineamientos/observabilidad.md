## Lineamientos de Observabilidad

Objetivos:

- Permitir diagnóstico end-to-end de pedidos, inventario, rutas, tracking, evidencias, excepciones y SLA.
- Reducir el tiempo de detección ante degradaciones en campañas.
- Dar soporte a conciliación, atención al cliente y auditoría operativa.

Lineamientos:

- OBS-01: Todo componente debe emitir logs estructurados.
- OBS-02: Toda transacción crítica debe poder rastrearse mediante correlation ID o trace ID.
- OBS-03: El correlation ID debe propagarse entre OMS, WMS, TMS, App de Conductores, portales, ERP y bus de eventos.
- OBS-04: Deben capturarse métricas técnicas y de negocio: órdenes recibidas, duplicadas, rechazadas, reservas, conflictos de inventario, eventos de tracking, evidencias pendientes, DLQ, entregas fallidas y SLA.
- OBS-05: Deben definirse alertas para disponibilidad, errores, latencia, saturación, colas, backpressure, eventos fuera de orden y retrasos de tracking mayores a 20 minutos.
- OBS-06: Los logs no deben exponer datos personales de destinatarios, evidencias, firmas, teléfonos ni direcciones completas.
- OBS-07: Las trazas distribuidas deben cubrir el flujo desde recepción de orden hasta entrega, devolución, incidencia o liquidación.
- OBS-08: Deben existir dashboards operativos para soporte, almacén, transporte, última milla, atención al cliente y finanzas.
- OBS-09: Deben conservarse evidencias de auditoría para cambios manuales de ruta, conciliaciones de inventario, reintentos y excepciones.
- OBS-10: La observabilidad debe cubrir Azure, AWS, GCP, SaaS y on premises.

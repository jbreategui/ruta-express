## Lineamientos de Escalabilidad

Objetivos:

- Soportar la operación diaria y los picos de campaña de RutaExpress.
- Evitar degradaciones como la acumulación de 240,000 pedidos en cola durante Cyber Days.
- Definir objetivos de capacidad, latencia y resiliencia medibles.

Lineamientos:

- ESC-01: La solución debe dimensionarse con la volumetría del caso: 68,000 órdenes diarias, 180,000 en campaña, 210,000 movimientos de inventario diarios y más de 130,000 eventos de tracking en campaña.
- ESC-02: Deben definirse objetivos de latencia para procesos críticos: recepción/validación de orden, reserva de inventario, publicación de eventos, sincronización offline y consulta de tracking.
- ESC-03: Los componentes stateless deben escalar horizontalmente.
- ESC-04: Las operaciones pesadas o diferibles deben ejecutarse de forma asíncrona mediante colas, eventos o procesamiento batch/streaming.
- ESC-05: Deben establecerse límites de concurrencia, cuotas por cliente y estrategias de backpressure.
- ESC-06: Deben prevenirse cuellos de botella en WMS, bases de datos, APIs, colas, red y conectividad con on premises.
- ESC-07: Debe protegerse WMS Principal (On Premises) (APP-06) durante la transición y WMS Cloud en TO BE frente a sobrecarga de reservas.
- ESC-08: Deben ejecutarse pruebas de carga para validar picos de campaña, eventos de tracking y sincronización masiva.
- ESC-09: Debe existir degradación controlada: priorización por SLA, colas durables, reintentos y DLQ.
- ESC-10: La arquitectura debe soportar crecimiento futuro de centros, vehículos, clientes B2B y canales de integración.

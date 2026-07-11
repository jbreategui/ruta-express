## Lineamientos de Integración

Objetivos:

- Reemplazar progresivamente integraciones punto a punto por APIs gobernadas y eventos.
- Asegurar consistencia entre OMS, WMS, TMS, App de Conductores, portales, ERP y analítica.
- Reducir eventos perdidos, duplicados, fuera de orden o no trazables.

Lineamientos:

- INT-01: Las integraciones síncronas deben exponerse mediante APIs versionadas, documentadas y protegidas.
- INT-02: Las integraciones asíncronas deben desacoplarse mediante Bus de Eventos Central (PLT-03), colas o mensajería.
- INT-03: Toda API debe tener contratos claros de entrada, salida, errores y códigos funcionales.
- INT-04: Todo evento debe tener esquema versionado, productor, consumidor esperado, timestamp, correlation ID y clave de idempotencia.
- INT-05: Deben manejarse timeouts, reintentos, circuit breaker, backpressure y DLQ en llamadas remotas o procesamiento asíncrono.
- INT-06: Las integraciones críticas deben ser idempotentes, especialmente creación de órdenes, reservas, liberaciones, tracking y evidencias.
- INT-07: Los cambios incompatibles deben publicarse como nuevas versiones.
- INT-08: Debe minimizarse el acoplamiento directo entre WMS, TMS, app móvil, portales y ERP.
- INT-09: Debe existir estrategia de replay controlado para reconstruir historial o reprocesar eventos sin duplicar efectos de negocio.
- INT-10: Deben registrarse evidencias de intercambio para auditoría, soporte y conciliación financiera.
- INT-11: Durante la transición deben coexistir adaptadores para sistemas AS IS y contratos TO BE sin romper operación.
- INT-12: Debe definirse secuencia lógica por agregado de negocio: orden, paquete, ruta, entrega, evidencia y liquidación.

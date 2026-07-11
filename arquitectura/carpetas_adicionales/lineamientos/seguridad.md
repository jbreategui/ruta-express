## Lineamientos de Seguridad

Objetivos:

- Proteger datos personales de destinatarios, clientes B2B, conductores, evidencias de entrega e integraciones.
- Reducir exposición de APIs y accesos entre nubes.
- Asegurar trazabilidad y control de operaciones críticas.

Lineamientos:

- SEG-01: Toda comunicación entre componentes debe usar cifrado en tránsito.
- SEG-02: La información sensible debe almacenarse con cifrado en reposo, incluyendo evidencias, datos móviles offline, direcciones, teléfonos, firmas y fotos.
- SEG-03: La autenticación debe centralizarse usando mecanismos estándar como OAuth2, OpenID Connect o identidad federada.
- SEG-04: La autorización debe aplicar mínimo privilegio por rol, sistema, cliente, conductor, operador y servicio.
- SEG-05: No se deben almacenar secretos en código fuente ni en archivos de configuración planos.
- SEG-06: Deben usarse gestores de secretos y llaves administradas por nube o plataforma corporativa.
- SEG-07: Todas las operaciones críticas deben dejar registro de auditoría: creación/cancelación de orden, reserva/liberación de inventario, cambio manual de ruta, excepción, evidencia y liquidación.
- SEG-08: Las APIs públicas deben protegerse con WAF, rate limiting, validación de entrada, cuotas por cliente y detección de abuso.
- SEG-09: La App de Conductores (APP-15) debe proteger datos offline con cifrado local, bloqueo de sesión y controles ante pérdida/cambio de dispositivo.
- SEG-10: Las evidencias en Almacenamiento Evidencias (S3) (APP-16) deben tener hash de integridad, control de acceso y retención según política.
- SEG-11: Deben aplicarse prácticas de desarrollo seguro y análisis de vulnerabilidades sobre dependencias, contenedores e imágenes.
- SEG-12: La conectividad entre Azure, AWS, GCP y on premises debe usar canales seguros y segmentación de red.

## Lineamientos de Arquitectura

Objetivos:

- Construir una solución logística mantenible, modular y evolutiva.
- Separar responsabilidades entre OMS, inventario, integración, rutas, última milla, evidencias, excepciones y liquidación.
- Preparar una arquitectura TO BE que pueda representarse en C4 Model y justificarse mediante ADR.

Lineamientos:

- ARQ-01: La solución debe separarse por dominios logísticos con responsabilidades claras.
- ARQ-02: Orquestador de Pedidos (APP-02) debe evolucionar a OMS centralizado sin crear un nuevo ID de aplicación en el Hito 1.
- ARQ-03: Las reglas de negocio de orden, inventario, reservas, excepciones y SLA no deben quedar embebidas en canales, portales o app móvil.
- ARQ-04: Cada microservicio debe tener una responsabilidad definida y ownership claro.
- ARQ-05: Deben preferirse contratos explícitos entre componentes sobre dependencias implícitas.
- ARQ-06: Debe evitarse el acoplamiento fuerte entre OMS, WMS Cloud, TMS, App de Conductores (APP-15), ERP y portales.
- ARQ-07: Los componentes deben poder evolucionar con mínimo impacto lateral mediante versionamiento de APIs/eventos.
- ARQ-08: El diseño debe diferenciar capacidades core de negocio frente a capacidades transversales como observabilidad, IAM, secretos e IaC.
- ARQ-09: La arquitectura debe soportar operación transicional con sistemas AS IS, especialmente WMS Principal (On Premises) (APP-06) y ERP Financiero (On Premises) (APP-25).
- ARQ-10: El diseño debe documentar decisiones con ADR, incluyendo alternativas descartadas y criterios de selección.

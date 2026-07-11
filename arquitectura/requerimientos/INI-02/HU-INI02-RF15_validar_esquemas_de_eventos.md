```gherkin
# HU-INI02-RF15 — Validar esquemas de eventos
Feature: Validación de esquema de eventos
  Como responsable de calidad de integración
  Quiero validar el esquema de cada evento antes de aceptarlo
  Para evitar que datos incompletos o incompatibles contaminen a los consumidores aguas abajo

  # Escenarios positivos

  Scenario: Aceptar un evento con esquema válido
    Given un evento que cumple el esquema versionado de su tipo
    When el bus lo valida
    Then debe aceptarlo y ponerlo a disposición de los consumidores

  # Escenarios negativos

  Scenario: Enviar un evento con esquema inválido a la cola de errores
    Given un evento que no cumple su esquema declarado
    When el bus lo valida
    Then debe enviarlo a la cola de errores sin entregarlo a los consumidores
    And debe registrar el motivo del rechazo

  # Nota: RF-14 valida la presencia de metadatos obligatorios (tipo, esquema, correlation ID);
  # RF-15 valida la conformidad del payload contra el esquema versionado.

  Scenario: Rechazar un evento con versión de esquema no soportada
    Given un evento cuyo esquema declara una versión ya no soportada
    When el bus lo valida
    Then debe rechazarlo
    And debe indicar la versión de esquema vigente
```

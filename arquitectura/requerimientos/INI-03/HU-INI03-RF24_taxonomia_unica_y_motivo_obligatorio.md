```gherkin
# HU-INI03-RF24 — Taxonomía única de excepciones con motivo obligatorio
Feature: Taxonomía única de excepciones y motivo obligatorio
  Como responsable de atención y transporte
  Quiero una taxonomía única de excepciones y exigir un motivo canónico al cerrar una entrega fallida
  Para que app, TMS, CRM y portal usen los mismos códigos y no exista texto libre no clasificable

  # Escenarios positivos

  Scenario: Registrar una excepción con código canónico y propagarla
    Given la lista oficial de códigos de excepción
    When el conductor registra una entrega fallida con un código canónico
    Then el sistema debe aceptarla
    And el mismo código y descripción deben propagarse a TMS, CRM y portal

  Scenario: Cerrar una entrega fallida con motivo canónico
    Given una entrega que no pudo completarse
    When el conductor selecciona un motivo de la taxonomía
    Then el sistema debe permitir cerrar la entrega fallida
    And debe dejar el motivo disponible para el análisis de causas

  # Escenarios negativos

  Scenario: Bloquear el cierre sin motivo
    Given una entrega fallida sin motivo seleccionado
    When el conductor intenta cerrarla
    Then el sistema no debe permitir el cierre
    And debe exigir un motivo canónico

  Scenario: Rechazar un código de excepción no vigente
    Given un código que ya no está vigente en la taxonomía
    When se intenta registrar con ese código
    Then el sistema debe rechazarlo
    And debe ofrecer los códigos vigentes
```

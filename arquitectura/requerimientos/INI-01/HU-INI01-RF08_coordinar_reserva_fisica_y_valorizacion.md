```gherkin
# HU-INI01-RF08 — Coordinar reserva física (WMS) y valorización financiera (ERP)
Feature: Coordinación de reserva física y valorización financiera
  Como responsable de operaciones
  Quiero coordinar con el WMS la reserva física y con el ERP el inventario valorizado
  Para que la operación y la liquidación usen datos consistentes y sin doble contabilidad

  # Escenarios positivos

  Scenario: Notificar al ERP una reserva confirmada por el WMS
    Given que el WMS confirma la reserva física de una orden
    When el OMS coordina la valorización
    Then debe notificar la reserva al ERP mediante API o evento
    And el inventario valorizado debe quedar disponible para liquidación

  # Escenarios negativos

  Scenario: No valorizar sin reserva física confirmada
    Given que la reserva física en el WMS no fue confirmada
    When el OMS evalúa la valorización
    Then no debe notificar la valorización al ERP

  Scenario: Compensar la reserva física si el ERP rechaza la valorización
    Given que el WMS confirmó la reserva física
    And el ERP rechaza la valorización
    When el OMS detecta el fallo
    Then debe liberar (compensar) la reserva física en el WMS
    And debe registrar la compensación con su motivo
```

```gherkin
# HU-INI03-RF25 — Automatizar acciones por tipo de excepción
Feature: Automatización de acciones por tipo de excepción
  Como planner de última milla
  Quiero automatizar la acción según el tipo de excepción
  Para generar reintentos, devoluciones, reasignaciones o escalamiento sin gestión manual innecesaria

  # Escenarios positivos

  Scenario: Crear un reintento por destinatario ausente
    Given una entrega fallida con motivo "destinatario ausente"
    When el sistema procesa la excepción
    Then debe generar automáticamente un reintento según la regla configurada

  Scenario: Iniciar una devolución por dirección inexistente
    Given una entrega fallida con motivo "dirección inexistente" verificado
    When el sistema procesa la excepción
    Then debe iniciar automáticamente el flujo de devolución
    And debe notificar al cliente el motivo y el estado del paquete

  # Escenarios negativos

  Scenario: Escalar cuando no hay regla automática aplicable
    Given una excepción sin regla de automatización definida
    When el sistema la procesa
    Then debe escalarla a un responsable
    And no debe dejar la excepción sin acción

  Scenario: No ejecutar una acción no permitida por la regla
    Given una excepción cuyo tipo no permite devolución automática
    When el sistema evalúa las acciones
    Then no debe ejecutar la devolución
    And debe aplicar la acción permitida o escalar
```

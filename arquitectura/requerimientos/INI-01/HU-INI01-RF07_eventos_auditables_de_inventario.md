```gherkin
# HU-INI01-RF07 — Registrar eventos auditables de inventario
Feature: Registro auditable de movimientos de inventario
  Como auditor operativo
  Quiero que reservas, liberaciones, cancelaciones y movimientos queden como eventos auditables
  Para reconstruir cada cambio con responsable, motivo y correlation ID

  # Escenarios positivos

  Scenario: Registrar una reserva como evento auditable
    Given que el OMS confirma una reserva de inventario
    When se genera el movimiento
    Then debe registrarlo como evento con orden asociada, actor o sistema, timestamp, motivo y correlation ID

  Scenario: Registrar la liberación de una reserva compensada
    Given una reserva liberada por compensación de una orden no completada
    When se genera el movimiento de liberación
    Then debe registrarlo como evento auditable vinculado a la reserva original y su motivo

  # Escenarios negativos

  Scenario: Rechazar un movimiento sin motivo
    Given que se intenta registrar un ajuste de inventario sin motivo
    When el OMS valida el movimiento
    Then debe rechazarlo
    And debe exigir un motivo

  Scenario: Rechazar un movimiento sin correlation ID
    Given que llega un movimiento de inventario sin correlation ID
    When el OMS lo valida
    Then debe derivarlo a remediación con el error identificado
    And no debe publicarlo como movimiento confirmado
```

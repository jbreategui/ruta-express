```gherkin
# HU-INI02-RF18 — Priorizar eventos por criticidad y SLA
Feature: Priorización de eventos por criticidad y SLA
  Como operador de campaña
  Quiero priorizar los eventos críticos (reserva, entrega, liquidación) sobre los informativos
  Para que en un pico las operaciones con SLA ajustado se procesen primero

  # Escenarios positivos

  Scenario: Procesar una reserva crítica antes que un evento informativo
    Given una cola con un evento de reserva crítico y eventos informativos
    When la plataforma aplica la política de prioridad
    Then debe procesar la reserva crítica antes que los informativos

  # Escenarios negativos

  Scenario: Evitar el bloqueo permanente de los eventos de baja prioridad
    Given un flujo continuo de eventos críticos
    When la plataforma prioriza
    Then ningún evento de baja prioridad debe esperar más del tiempo máximo configurado
    And debe reservarse una fracción de la capacidad para procesarlos

  Scenario: Rechazar una asignación de prioridad no autorizada
    Given un productor que marca como crítico un evento informativo sin corresponderle
    When la plataforma evalúa la prioridad
    Then debe rechazar la prioridad no autorizada
    And debe procesarlo con su prioridad real
```

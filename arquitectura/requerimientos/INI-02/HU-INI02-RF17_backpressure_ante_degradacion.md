```gherkin
# HU-INI02-RF17 — Aplicar backpressure ante degradación
Feature: Backpressure ante la degradación de un destino
  Como administrador de la plataforma
  Quiero regular el flujo de mensajes hacia un sistema degradado (WMS o ERP)
  Para no repetir el colapso de Cyber Days, donde se acumularon 240,000 pedidos en cola, ni perder mensajes

  # Escenarios positivos

  Scenario: Regular el envío hacia un WMS degradado
    Given que el WMS reporta latencia alta o bloqueo
    And existen eventos de reserva pendientes
    When la plataforma detecta el umbral de degradación
    Then debe reducir la tasa de envío hacia el WMS
    And debe mantener los mensajes en una cola priorizada

  Scenario: Recuperar la tasa normal al restablecerse el destino
    Given que el WMS vuelve a operar con normalidad
    When la plataforma detecta la recuperación
    Then debe restablecer progresivamente la tasa de envío

  # Escenarios negativos

  Scenario: No descartar mensajes aceptados durante la saturación
    Given que la cola de reservas crece durante la campaña
    When se activa el backpressure
    Then la plataforma no debe descartar mensajes ya aceptados

  Scenario: Alertar por saturación sostenida
    Given un backlog en crecimiento con backpressure activo
    When el backlog supera el umbral durante el periodo definido
    Then la plataforma debe emitir una alerta de saturación con el tamaño del backlog
```

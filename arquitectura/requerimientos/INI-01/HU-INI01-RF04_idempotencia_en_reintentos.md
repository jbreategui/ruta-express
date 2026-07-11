```gherkin
# HU-INI01-RF04 — Garantizar idempotencia en reintentos
Feature: Idempotencia de operaciones de orden e inventario
  Como cliente integrador
  Quiero que los reintentos de creación, reserva y cancelación sean idempotentes
  Para que un error temporal no genere doble orden, doble reserva ni doble movimiento

  # Escenarios positivos

  Scenario: Reintentar creación con la misma idempotency key
    Given que una solicitud de creación fue procesada correctamente
    And el cliente reenvía la misma solicitud con la misma idempotency key
    When el OMS recibe el reintento
    Then debe devolver el mismo orderId original
    And no debe crear una orden adicional

  # Escenarios negativos

  Scenario: Rechazar reuso de idempotency key con contenido distinto
    Given que existe una idempotency key asociada a una orden previa
    When el cliente envía otra orden con la misma clave pero distinto contenido
    Then el OMS debe rechazar la solicitud por conflicto de idempotencia
    And no debe modificar la orden original

  Scenario: No aplicar dos veces la misma cancelación
    Given que una orden ya fue cancelada con una idempotency key
    When llega el mismo comando de cancelación reintentado
    Then el OMS debe responder que ya está cancelada
    And no debe liberar inventario por segunda vez
```

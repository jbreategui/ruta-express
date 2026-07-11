```gherkin
# HU-INI01-RF11 — Compatibilidad transicional con WMS Principal (On Premises)
Feature: Compatibilidad transicional con el WMS Principal on premises
  Como arquitecto de transición
  Quiero que las reservas hechas por el WMS on premises usen el mismo modelo canónico y correlation ID
  Para no interrumpir la operación mientras el WMS Cloud no esté completamente desplegado

  # Escenarios positivos

  Scenario: Procesar una reserva mediante el WMS Principal
    Given que el WMS Cloud aún no está desplegado para un almacén
    When una orden reserva inventario a través del WMS Principal on premises
    Then el OMS debe publicar la reserva con el modelo canónico y correlation ID
    And el estado debe ser consistente con el resto de sistemas

  # Escenarios negativos

  Scenario: Regular el envío cuando el WMS Principal se degrada
    Given que el WMS Principal reporta lentitud y las reservas pendientes superan el umbral definido
    When el OMS evalúa la salud del canal hacia el WMS
    Then debe pausar el envío de nuevas reservas y encolarlas para reintento
    And no debe confirmar estados sin respuesta del inventario

  Scenario: No perder la orden si el WMS on premises no responde
    Given que el WMS Principal no responde a una solicitud de reserva
    When se agota el tiempo de espera
    Then el OMS debe encolar la orden para reintento
    And no debe descartarla ni marcarla como reservada
```

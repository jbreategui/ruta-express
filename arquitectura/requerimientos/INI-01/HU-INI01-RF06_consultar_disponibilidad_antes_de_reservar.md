```gherkin
# HU-INI01-RF06 — Consultar disponibilidad de inventario antes de reservar
Feature: Consulta de disponibilidad de inventario previa a la reserva
  Como planificador de almacén
  Quiero consultar disponibilidad por SKU, almacén, ubicación, lote y estado antes de confirmar la reserva
  Para comprometer solo stock elegible y no generar cancelaciones aguas abajo

  # Escenarios positivos

  Scenario: Consultar disponibilidad antes de reservar
    Given que existe stock registrado para un SKU en varios almacenes
    When el planificador consulta la disponibilidad
    Then debe recibir las cantidades disponibles y elegibles por almacén, ubicación, lote y estado

  Scenario: Confirmar reserva cuando hay stock elegible
    Given que existe stock disponible y elegible para el SKU y la ubicación de la orden
    When el OMS solicita la reserva
    Then debe confirmar la reserva sobre ese inventario

  Scenario: Confirmar solo una de dos reservas concurrentes sobre el mismo stock
    Given que dos órdenes solicitan al mismo tiempo las últimas unidades del mismo SKU
    When el OMS procesa ambas reservas
    Then solo una orden debe obtener la reserva
    And la otra debe recibir stock insuficiente sin quedar reservada

  # Escenarios negativos

  Scenario: Bloquear reserva con inventario no elegible
    Given que el stock del SKU está marcado como vencido o dañado
    When el OMS intenta reservar
    Then no debe confirmar la reserva
    And debe indicar que el inventario no es elegible

  Scenario: Bloquear reserva con stock insuficiente
    Given que la cantidad disponible es menor a la solicitada
    When el OMS intenta reservar
    Then no debe confirmar la reserva
    And debe informar la cantidad faltante
```

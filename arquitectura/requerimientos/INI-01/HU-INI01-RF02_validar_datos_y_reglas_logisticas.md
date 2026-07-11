```gherkin
# HU-INI01-RF02 — Validar datos obligatorios y reglas logísticas
Feature: Validación de datos y reglas logísticas de la orden
  Como analista de mesa B2B
  Quiero validar dirección, SKU, cliente, promesa SLA y ventana horaria antes de aceptar la orden
  Para evitar que un error de datos explote después en almacén, ruta o entrega

  # Escenarios positivos

  Scenario: Aceptar orden con todos los datos válidos
    Given que la orden trae dirección, SKU, cliente, SLA y ventana horaria válidos
    When el OMS ejecuta la validación
    Then debe aceptar la orden y pasarla a estado "Validada"
    And debe registrar el SLA y la prioridad de la orden para su procesamiento

  # Escenarios negativos

  Scenario: Marcar orden pendiente por dirección incompleta
    Given que la orden trae una dirección incompleta
    When el OMS ejecuta la validación
    Then debe dejar la orden en estado "Pendiente de corrección"
    And no debe reservar inventario

  Scenario: Rechazar la línea con SKU inexistente sin descartar la orden
    Given que la orden incluye un SKU que no existe en el catálogo
    When el OMS ejecuta la validación
    Then debe rechazar la línea con SKU inválido indicando el SKU no reconocido
    And debe dejar la orden en estado "Pendiente de corrección" sin reservar inventario

  Scenario: Rechazar orden con ventana horaria fuera de cobertura
    Given que la orden pide una ventana horaria no cubierta por la operación
    When el OMS ejecuta la validación
    Then no debe aceptar la orden
    And debe indicar que la ventana no está disponible

  Scenario: Rechazar orden con promesa SLA imposible de cumplir
    Given que la orden exige una promesa SLA que la operación no puede cumplir para la ventana solicitada
    When el OMS ejecuta la validación
    Then no debe aceptar la orden
    And debe indicar el plazo mínimo alcanzable para esa ventana
```

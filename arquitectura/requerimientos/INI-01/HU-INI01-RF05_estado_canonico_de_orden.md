```gherkin
# HU-INI01-RF05 — Mantener el estado canónico de la orden
Feature: Estado canónico de la orden
  Como operador logístico
  Quiero un único modelo de estados para toda la vida de la orden
  Para que OMS, WMS, TMS, portal y ERP consulten la misma verdad operativa

  # Escenarios positivos

  Scenario: Publicar una transición de estado válida
    Given que una orden está en estado "Reservada"
    When el WMS confirma el picking
    Then el OMS debe transicionar la orden a "Preparada"
    And debe publicar el nuevo estado a los sistemas suscritos

  Scenario: Consultar el mismo estado desde dos sistemas distintos
    Given que una orden transicionó a "Despachada"
    When el portal B2B y el ERP consultan la orden
    Then ambos deben recibir el estado "Despachada" con el mismo timestamp de transición

  # Escenarios negativos

  Scenario: Bloquear una transición de estado inválida
    Given que una orden está en estado "Entregada"
    When un sistema intenta pasarla a "Reservada"
    Then el OMS debe rechazar la transición
    And debe conservar el estado "Entregada"

  Scenario: Rechazar un estado no definido en el modelo canónico
    Given que un sistema publica un estado que no existe en el modelo
    When el OMS lo recibe
    Then debe rechazarlo
    And debe registrar el intento para revisión
```

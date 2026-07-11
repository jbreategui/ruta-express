```gherkin
# HU-INI01-RF10 — Exponer APIs de consulta de orden e inventario
Feature: APIs de consulta de orden e inventario (lado de lectura del OMS)
  Como consumidor autorizado (TMS, portal B2B o liquidación)
  Quiero consultar estado de orden, reserva e inventario mediante APIs versionadas
  Para operar con información confiable y consistente entre sistemas

  # Escenarios positivos

  Scenario: Consultar el estado de una orden con autorización válida
    Given un consumidor autorizado con credenciales vigentes
    When consulta el estado de una orden por su identificador
    Then el OMS debe responder con el estado canónico y su reserva asociada

  # Escenarios negativos

  Scenario: Rechazar una consulta sin autorización
    Given un consumidor sin credenciales válidas
    When intenta consultar una orden
    Then el OMS debe denegar el acceso
    And debe registrar el intento

  Scenario: Rechazar una consulta contra una versión de contrato retirada
    Given que un consumidor invoca una versión de API ya retirada
    When realiza la consulta
    Then el OMS debe rechazarla
    And debe indicar la versión vigente disponible
```

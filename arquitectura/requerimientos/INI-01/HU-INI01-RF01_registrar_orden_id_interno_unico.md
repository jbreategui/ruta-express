```gherkin
# HU-INI01-RF01 — Registrar orden con identificador interno único
Feature: Registro de órdenes con identificador interno único
  Como operador de recepción B2B
  Quiero que toda orden recibida por API, portal o carga masiva quede registrada con un identificador interno único
  Para tener trazabilidad desde el ingreso sin depender del identificador que envía el cliente

  # Escenarios positivos

  Scenario: Registrar orden válida recibida por API
    Given una orden recibida con cliente, canal y líneas de pedido
    When el OMS la procesa
    Then debe asignarle un identificador interno único
    And debe registrar canal de origen, cliente, timestamp y estado inicial "Recibida"

  Scenario: Registrar órdenes de una carga masiva
    Given que un cliente carga un archivo de carga masiva con varias órdenes
    When el OMS procesa la carga
    Then debe asignar un identificador interno único a cada orden
    And debe conservar la referencia externa original de cada línea

  # Escenarios negativos

  Scenario: Rechazar registro sin cliente identificado
    Given que llega una orden sin cliente asociado
    When el OMS intenta registrarla
    Then no debe registrar la orden
    And debe indicar que el cliente es obligatorio

  Scenario: Rechazar registro sin canal de origen
    Given que llega una orden sin canal de origen declarado
    When el OMS intenta registrarla
    Then no debe registrar la orden
    And debe indicar que el canal de origen es obligatorio
```

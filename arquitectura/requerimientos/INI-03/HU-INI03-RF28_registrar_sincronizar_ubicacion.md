```gherkin
# HU-INI03-RF28 — Registrar y sincronizar ubicación cada 2 minutos
Feature: Registro y sincronización de ubicación
  Como supervisor de transporte
  Quiero que la app registre y sincronice la ubicación cada 2 minutos con su timestamp original
  Para mejorar el tracking confiable y la trazabilidad de la ruta

  # Escenarios positivos

  Scenario: Enviar la ubicación periódica con conectividad
    Given un conductor en ruta con conectividad
    When transcurren 2 minutos
    Then la app debe registrar y enviar la ubicación con su timestamp
    And el TMS y el portal deben recibir el evento con secuencia y estado de sincronización

  Scenario: No perder ubicaciones durante la pérdida de red
    Given un conductor en una zona sin señal
    When la app captura una ubicación al cumplirse el intervalo
    Then debe encolarla localmente con su timestamp original
    And debe enviarlas en orden al recuperar la conectividad

  # Escenarios negativos

  Scenario: No duplicar ubicaciones al reenviar la cola
    Given ubicaciones encoladas que se reenvían al reconectar
    When algunas ya habían sido recibidas por el backend
    Then el backend debe descartar las duplicadas por dispositivo y timestamp
    And debe conservar una sola por instante y dispositivo
```

```gherkin
# HU-INI03-RF27 — Preservar evidencias ante cambio de dispositivo
Feature: Preservación de evidencias ante cambio de dispositivo
  Como supervisor de conductores
  Quiero preservar las evidencias pendientes ante cierre de sesión, reinicio, reinstalación o cambio de dispositivo
  Para evitar entregas sin firma o foto, como las 1,200 que quedaron sin evidencia en el caso

  # Escenarios positivos

  Scenario: Bloquear el cambio de dispositivo con evidencias pendientes
    Given un conductor con evidencias sin sincronizar
    When intenta cambiar de dispositivo o reinstalar la app
    Then el sistema debe bloquear la operación hasta sincronizar o respaldar las evidencias
    And debe indicar cuántas evidencias están pendientes

  Scenario: Recuperar evidencias tras una reinstalación controlada
    Given que la app respaldó las evidencias pendientes en el almacenamiento seguro del dispositivo antes de autorizar la reinstalación
    When el conductor inicia sesión nuevamente
    Then la app debe recuperar las evidencias respaldadas
    And debe continuar su sincronización

  # Escenarios negativos

  Scenario: Registrar remediación si la evidencia no puede recuperarse
    Given una evidencia pendiente que no puede recuperarse del dispositivo
    When se confirma la pérdida
    Then el sistema debe registrar un caso de remediación con su motivo
    And debe notificar a liquidación para su tratamiento
```

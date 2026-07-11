```gherkin
# HU-INI03-RF26 — Gestión de evidencias con referencia a la orden/entrega
Feature: Gestión de evidencias vinculadas a la orden/entrega
  Como responsable de liquidación
  Quiero que cada evidencia se conserve vinculada a su orden/entrega y verificable por su hash
  Para demostrar el cumplimiento y resolver observaciones de facturación
  # Nota: la integridad por hash como atributo de calidad se especifica en RNF-25.

  # Escenarios positivos

  Scenario: Guardar una evidencia vinculada y verificable
    Given una firma o foto capturada en la entrega
    When se almacena la evidencia
    Then debe quedar vinculada a la orden/entrega y al correlation ID
    And debe registrarse con su hash de integridad

  Scenario: Verificar el hash al recuperar la evidencia para liquidación
    Given una evidencia almacenada con su hash
    When el responsable de liquidación la recupera para sustentar una factura
    Then el sistema debe recomputar y comparar el hash
    And debe confirmar que la evidencia no fue alterada

  # Escenarios negativos

  Scenario: Bloquear una evidencia corrupta
    Given una evidencia cuyo hash no coincide con su contenido
    When el backend la valida
    Then debe rechazarla como corrupta
    And debe solicitar recaptura o remediación
```

```gherkin
# HU-INI01-RF09 — Reconciliar conflictos de inventario
Feature: Reconciliación de conflictos de inventario
  Como jefe de inventario
  Quiero reconciliar los conflictos entre el WMS central y los almacenes locales
  Para evitar liberar pedidos con inventario dudoso y reducir los 18,000 pedidos retrasados por sincronización

  # Escenarios positivos

  Scenario: Resolver un conflicto por regla automática al reconectar un almacén
    Given que un almacén local reconecta tras una caída y trae movimientos en conflicto
    When el OMS ejecuta la reconciliación
    Then debe resolver por regla automática los conflictos elegibles (por ejemplo, el conteo físico del almacén prevalece sobre el saldo teórico)
    And debe dejar trazabilidad de la resolución

  # Escenarios negativos

  Scenario: Derivar a operador un conflicto severo
    Given un conflicto con datos contradictorios entre el WMS central y el almacén local
    When el OMS ejecuta la reconciliación y ninguna regla automática aplica
    Then debe clasificarlo, priorizarlo y derivarlo a un operador
    And debe conservar la evidencia del conflicto

  Scenario: No autoconfirmar un conflicto sin regla aplicable
    Given que existe un conflicto sin regla de resolución definida
    When el OMS lo procesa
    Then no debe confirmar inventario automáticamente
    And debe mantenerlo en estado "En conciliación"
```

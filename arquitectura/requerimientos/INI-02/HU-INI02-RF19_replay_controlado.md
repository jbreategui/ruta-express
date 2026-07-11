```gherkin
# HU-INI02-RF19 — Ejecutar replay controlado de eventos
Feature: Replay controlado de eventos
  Como operador autorizado
  Quiero reprocesar eventos por rango, tipo o correlation ID
  Para reconstruir el historial o recuperar un consumidor sin duplicar efectos de negocio

  # Escenarios positivos

  Scenario: Reprocesar eventos por rango sin duplicar efectos
    Given un consumidor que perdió una serie de eventos
    When un operador autorizado ejecuta el replay por rango, tipo o correlation ID
    Then la plataforma debe reenviar los eventos solicitados con sus identificadores originales
    And los consumidores deben descartar los ya procesados sin duplicar reservas ni movimientos

  # Escenarios negativos

  Scenario: Rechazar un replay sin aprobación
    Given un usuario sin aprobación para ejecutar replay
    When solicita reprocesar un rango de eventos
    Then la plataforma debe rechazar la operación

  Scenario: Advertir antes de un replay sobre consumidores no idempotentes
    Given un replay que impactaría a un consumidor no idempotente
    When se solicita la operación
    Then la plataforma debe advertir el riesgo de doble efecto
    And debe requerir confirmación explícita antes de ejecutarlo
```

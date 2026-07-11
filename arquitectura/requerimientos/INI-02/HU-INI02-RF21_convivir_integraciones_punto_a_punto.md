```gherkin
# HU-INI02-RF21 — Convivir con integraciones punto a punto
Feature: Convivencia transicional con integraciones punto a punto
  Como arquitecto de migración
  Quiero que las integraciones punto a punto y los flujos event-driven coexistan durante la transición
  Para migrar sin romper la operación y con la posibilidad de revertir

  # Escenarios positivos

  Scenario: Migrar una integración con adaptador monitoreado
    Given una integración punto a punto con adaptador, contrato documentado y monitoreo definidos
    When se activa la migración al flujo event-driven
    Then ambos flujos deben operar en paralelo durante la ventana de migración
    And el tráfico debe procesarse sin pérdida en ninguno de los dos

  # Escenarios negativos

  Scenario: Bloquear una migración sin contrato ni plan de rollback
    Given una migración propuesta sin contrato documentado ni plan de rollback
    When se intenta activarla
    Then la plataforma debe bloquear la migración
    And debe exigir el contrato y el plan de rollback

  Scenario: Revertir a punto a punto si el flujo event-driven falla
    Given una integración migrada que falla en producción
    When se ejecuta el rollback
    Then el tráfico debe volver al flujo punto a punto sin pérdida
    And debe registrarse el rollback con su motivo
```

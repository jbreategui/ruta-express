```gherkin
# HU-INI03-RF29 — Ejecutar acciones preventivas por riesgo de excepción
Feature: Acciones preventivas por riesgo de excepción
  Como equipo de atención preventiva
  Quiero generar acciones preventivas por dirección o ausencia antes del siguiente intento
  Para reducir las fallas prevenibles, ya que el 34% se relaciona con dirección o ausencia del destinatario

  # Escenarios positivos

  Scenario: Crear una tarea preventiva por dirección riesgosa
    Given una entrega con antecedentes de dirección incorrecta
    When el sistema detecta el riesgo antes del intento
    Then debe generar una tarea de validación de dirección con el cliente

  Scenario: Crear una tarea preventiva por riesgo de ausencia
    Given una entrega con antecedentes de destinatario ausente
    When el sistema detecta el riesgo antes del intento
    Then debe generar una tarea de contacto para confirmar o ajustar la ventana de entrega

  Scenario: Priorizar el contacto en entregas de alto riesgo
    Given varias entregas con riesgo de dirección o ausencia
    When se generan las acciones preventivas
    Then debe priorizar el contacto de las de mayor riesgo antes del siguiente intento

  # Escenarios negativos

  Scenario: No crear una acción preventiva sin evidencia de riesgo
    Given una entrega sin antecedentes ni señales de riesgo
    When el sistema evalúa la entrega
    Then no debe generar una acción preventiva
    And debe continuar con el flujo normal
```

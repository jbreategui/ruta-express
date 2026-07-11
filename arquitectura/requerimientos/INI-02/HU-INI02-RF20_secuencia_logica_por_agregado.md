```gherkin
# HU-INI02-RF20 — Conservar la secuencia lógica por agregado
Feature: Secuencia lógica por agregado de negocio
  Como responsable de integridad
  Quiero conservar el orden lógico de los eventos por orden, paquete, ruta o liquidación
  Para que el cliente nunca vea "intento fallido" después de una entrega exitosa

  # Escenarios positivos

  Scenario: Procesar los eventos de un paquete en su orden lógico
    Given varios eventos del mismo paquete que llegan casi simultáneamente
    When la plataforma los procesa
    Then debe respetar la secuencia lógica del paquete
    And debe exponer estados coherentes a los consumidores

  # Escenarios negativos

  Scenario: Retener un intento fallido que llega después del entregado
    Given que un paquete ya tiene el evento "Entregado"
    And llega un evento "Intento fallido" con timestamp anterior, fuera de orden
    When la plataforma lo evalúa
    Then no debe exponer el estado "Intento fallido"
    And debe conservar "Entregado" como estado visible

  Scenario: Marcar para remediación una secuencia incompleta
    Given que falta un evento anterior de la misma orden
    When llega un evento posterior
    Then la plataforma debe retenerlo durante la ventana de espera configurada
    And si el evento faltante no llega debe marcar la secuencia para remediación
    And no debe publicar un estado contradictorio
```

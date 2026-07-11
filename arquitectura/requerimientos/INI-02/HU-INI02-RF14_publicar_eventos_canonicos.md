```gherkin
# HU-INI02-RF14 — Publicar eventos canónicos en el Bus de Eventos Central
Feature: Publicación de eventos canónicos
  Como productor de eventos (OMS, WMS, TMS, app de conductores, ERP)
  Quiero publicar eventos canónicos con esquema y correlation ID en el Bus de Eventos Central
  Para desacoplar los sistemas y que, si uno cae, los eventos no se pierdan ni se apilen sin control como en Cyber Days

  # Escenarios positivos

  Scenario: Publicar un evento OrdenValidada válido
    Given una orden validada por el OMS
    When el OMS publica el evento "OrdenValidada" con esquema y correlation ID
    Then el bus debe aceptarlo y confirmar la publicación al productor
    And debe ponerlo a disposición de los consumidores suscritos

  Scenario: No perder el evento si el bus no está disponible al publicar
    Given que el bus no responde en el momento de la publicación
    When el productor intenta publicar un evento
    Then el evento debe conservarse pendiente en el productor
    And debe publicarse cuando el bus se recupere, sin pérdida

  Scenario: Entregar el mismo evento a consumidores independientes
    Given un evento aceptado con varios consumidores suscritos
    When el bus lo distribuye
    Then cada consumidor debe recibir el evento de forma independiente
    And la caída de un consumidor no debe afectar a los demás

  # Escenarios negativos

  Scenario: Rechazar un evento sin correlation ID
    Given un productor que publica un evento sin correlation ID
    When el bus lo recibe
    Then debe rechazarlo
    And debe indicar que el correlation ID es obligatorio

  Scenario: Derivar a la cola de errores un evento sin tipo o esquema declarado
    Given un evento sin tipo canónico ni esquema asociado
    When el bus lo recibe
    Then debe enviarlo a la cola de errores con el motivo
    And no debe entregarlo a ningún consumidor
```

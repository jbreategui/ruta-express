```gherkin
# HU-INI03-RF23 — Sincronización confiable store-and-forward
Feature: Sincronización confiable store-and-forward (orden, confirmación y reintento)
  Como operador de última milla
  Quiero que la app sincronice los eventos pendientes en orden, con confirmación del backend y reintento automático
  Para no perder evidencias ni duplicarlas al recuperar la conectividad

  # Escenarios positivos

  Scenario: Sincronizar los eventos pendientes al recuperar la red
    Given que existen eventos offline encolados
    And el dispositivo recupera conectividad
    When la app inicia la sincronización
    Then debe enviar los eventos en orden por entrega
    And debe conservar el timestamp original y el correlation ID

  Scenario: Liberar la evidencia local solo tras la confirmación del backend
    Given un evento sincronizado al backend
    When el backend confirma su persistencia (ACK)
    Then la app debe liberar la copia local del evento

  Scenario: Descartar un evento reenviado que el backend ya había persistido
    Given un evento persistido por el backend cuya confirmación (ACK) se perdió
    When la app lo reenvía con el mismo correlation ID
    Then el backend debe detectarlo como ya persistido y responder la confirmación
    And no debe duplicar la entrega ni la evidencia registrada

  Scenario: Reintentar automáticamente tras un error temporal
    Given un envío que falló por un error de red temporal
    When se restablece la conectividad
    Then la app debe reintentar el envío automáticamente
    And no debe pedir al conductor recapturar la evidencia

  # Escenarios negativos

  Scenario: Retener un evento fuera de secuencia
    Given que falta un evento anterior de la misma entrega
    When la app prepara el lote de sincronización
    Then debe retener el evento posterior hasta completar la secuencia
    And no debe generar un estado contradictorio en el backend

  Scenario: Conservar la evidencia si no llega la confirmación
    Given un evento enviado al backend
    When no se recibe la confirmación de persistencia
    Then la app debe conservar la copia local
    And debe reintentar el envío

  Scenario: Derivar a remediación tras agotar los reintentos
    Given un envío que sigue fallando tras varios reintentos
    When se agota el máximo configurado
    Then la app debe marcar el evento para remediación
    And debe conservar la evidencia local hasta resolverlo
```

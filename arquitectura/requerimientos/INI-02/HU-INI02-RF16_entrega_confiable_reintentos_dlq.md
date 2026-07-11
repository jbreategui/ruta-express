```gherkin
# HU-INI02-RF16 — Entrega confiable de eventos: reintentos con DLQ
Feature: Entrega confiable de eventos con reintentos y dead-letter queue
  Como operador de integración
  Quiero reintentar automáticamente la entrega, deduplicar por identificador de evento y enviar a una DLQ lo que agote los reintentos
  Para no perder ningún evento ni aplicarlo dos veces aunque un consumidor esté caído

  # Escenarios positivos

  Scenario: Reentregar un evento a un consumidor caído mediante reintentos con backoff
    Given un consumidor temporalmente no disponible y un evento pendiente
    When la plataforma intenta entregar el evento
    Then debe reintentar automáticamente con espera creciente (backoff)
    And al recuperarse el consumidor debe recibir el evento pendiente

  Scenario: Enviar a la DLQ con contexto tras agotar los reintentos
    Given un evento cuyos reintentos se agotaron
    When se supera el máximo configurado
    Then la plataforma debe moverlo a la DLQ con payload, error, timestamp y responsable
    And no debe descartarlo silenciosamente

  Scenario: Aplicar una sola vez un evento entregado dos veces
    Given un evento ya procesado por un consumidor cuya confirmación de entrega se perdió
    When la plataforma reentrega el mismo evento con el mismo identificador
    Then el consumidor debe detectarlo como ya procesado por su identificador de evento
    And el efecto de negocio debe aplicarse una sola vez

  Scenario: Reprocesar un mensaje desde la DLQ tras corregir la causa
    Given un mensaje en la DLQ cuya causa ya fue corregida
    When un operador autorizado lo reprocesa
    Then la plataforma debe reinyectarlo al flujo
    And el consumidor debe descartar el duplicado si ya lo había procesado

  # Nota: la reinyección desde la DLQ repara un mensaje fallido puntual;
  # el replay histórico de rangos de eventos se cubre en HU-INI02-RF19.

  # Escenarios negativos

  Scenario: Bloquear el reproceso desde la DLQ sin autorización
    Given un usuario sin permiso de remediación
    When intenta reprocesar un mensaje de la DLQ
    Then la plataforma debe denegar la acción

  Scenario: No descartar automáticamente los mensajes de la DLQ
    Given mensajes acumulados en la DLQ
    When se supera el periodo de retención configurado
    Then la plataforma no debe borrarlos automáticamente
    And debe alertar sobre el backlog de la DLQ para su remediación
```

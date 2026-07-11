```gherkin
# HU-INI02-RF12 — Registrar y publicar contratos de API y eventos
Feature: Gobierno de contratos de API y eventos
  Como arquitecto de integración
  Quiero registrar, versionar y publicar los contratos de API y de eventos de cada dominio
  Para que el cambio de un cliente no rompa la recepción de órdenes de los demás

  # Escenarios positivos

  Scenario: Publicar un contrato nuevo con versión
    Given un contrato definido con esquema, versión y consumidores autorizados
    When el arquitecto lo registra en la plataforma
    Then debe publicarse el contrato en estado "Activo"
    And debe registrar responsable, ambiente y política de seguridad
    And debe quedar disponible en el catálogo para los consumidores autorizados

  Scenario: Convivencia de dos versiones sin romper consumidores
    Given que existe el contrato "orden" en versión v1 con consumidores activos
    When se publica la versión v2 del mismo contrato
    Then el sistema debe mantener v1 y v2 activas simultáneamente
    And los consumidores de v1 deben seguir operando sin cambios

  # Escenarios negativos

  Scenario: Rechazar contrato sin versión
    Given que se intenta registrar un contrato sin número de versión
    When la plataforma valida los metadatos
    Then debe rechazar el registro
    And debe indicar que la versión es obligatoria

  Scenario: Rechazar cambio incompatible sobre una versión publicada
    Given que existe el contrato "orden" v1 publicado
    When un publicador intenta modificar su esquema de forma incompatible sin crear una versión nueva
    Then el sistema debe rechazar el cambio
    And debe exigir publicarlo como una versión nueva

  Scenario: Rechazar consumidor no autorizado
    Given un consumidor sin permiso sobre el contrato "liquidación"
    When solicita suscribirse al contrato
    Then la plataforma debe denegar el acceso
    And debe registrar el intento para auditoría
```

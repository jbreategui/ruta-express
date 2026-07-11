```gherkin
# HU-INI02-RF13 — Aplicar seguridad, cuotas y rate limiting
Feature: Protección y cuotas de las APIs de integración
  Como administrador de APIs
  Quiero que el API Management aplique autenticación, autorización, cuotas y rate limiting por cliente
  Para que un cliente que abusa o falla no degrade el servicio de los demás

  # Escenarios positivos

  Scenario: Permitir una solicitud autenticada dentro de su cuota
    Given un cliente autenticado con cuota disponible
    When realiza una solicitud a una API publicada
    Then el gateway debe permitir la solicitud
    And debe descontar el consumo de su cuota

  Scenario: Regular una ráfaga sin afectar a los demás clientes
    Given un cliente dentro de su cuota que envía solicitudes por encima de la tasa permitida por segundo
    When el gateway detecta el exceso de tasa
    Then debe limitar las solicitudes excedentes indicando el exceso de tasa
    And los demás clientes deben seguir siendo atendidos con normalidad

  # Escenarios negativos

  Scenario: Rechazar una solicitud sin credenciales
    Given una solicitud sin token de autenticación
    When llega al gateway
    Then debe rechazarla indicando que la autenticación es obligatoria

  Scenario: Denegar una API para la que el cliente no está autorizado
    Given un cliente autenticado sin permiso sobre una API publicada
    When intenta invocarla
    Then el gateway debe denegar el acceso por falta de autorización
    And debe registrar el intento

  Scenario: Rechazar una solicitud que excede la cuota
    Given un cliente que superó su límite de peticiones
    When realiza otra solicitud
    Then el gateway debe rechazarla por exceso de cuota
    And no debe afectar la cuota de otros clientes

  Scenario: Bloquear un consumidor con token expirado
    Given un consumidor con token vencido
    When invoca una API
    Then el gateway debe denegar el acceso
    And debe indicar que debe renovar sus credenciales
```

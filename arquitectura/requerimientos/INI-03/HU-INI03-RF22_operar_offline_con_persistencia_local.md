```gherkin
# HU-INI03-RF22 — Operar entregas offline con persistencia local
Feature: Operación de entregas sin conectividad con persistencia local
  Como conductor
  Quiero operar las entregas asignadas sin conexión y que lo capturado quede persistido localmente
  Para continuar la ruta en zonas sin señal sin perder evidencias ni eventos
  # Nota: el cifrado del almacenamiento local se especifica en RNF-20.

  # Escenarios positivos

  Scenario: Consultar la ruta descargada sin conexión
    Given que la ruta y sus paquetes fueron descargados antes de perder señal
    When el conductor consulta la ruta sin conectividad
    Then la app debe mostrar ruta, paquetes, destinatario y datos de contacto

  Scenario: Registrar y persistir una entrega estando offline
    Given que el conductor está en una zona sin señal
    When el conductor registra una entrega con firma y foto
    Then la app debe guardar el evento y las evidencias localmente
    And deben seguir disponibles tras cerrar y reabrir la app

  # Escenarios negativos

  Scenario: Bloquear una ruta no descargada
    Given que la ruta no fue descargada previamente
    When el conductor intenta abrirla sin conexión
    Then la app no debe mostrar la ruta
    And debe indicar que requiere descargarla con conectividad

  Scenario: Impedir el acceso local sin sesión válida
    Given un equipo con datos locales
    When un usuario sin sesión válida intenta acceder a la app
    Then la app no debe mostrar los datos de ruta ni las evidencias
```

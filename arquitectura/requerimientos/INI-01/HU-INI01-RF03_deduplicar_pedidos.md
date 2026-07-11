```gherkin
# HU-INI01-RF03 — Deduplicar pedidos
Feature: Deduplicación de pedidos
  Como responsable de integración
  Quiero detectar pedidos duplicados por hash de contenido aunque cambie el identificador externo
  Para evitar el doble procesamiento por reintentos de clientes, como el lote de 32,000 pedidos reenviado en campaña

  # Escenarios positivos

  Scenario: Detectar duplicado con identificador externo diferente
    Given que existe una orden previa con mismo cliente, destinatario, SKU, cantidad y ventana
    When el cliente reenvía la orden con otro identificador externo
    Then el OMS debe detectarla como duplicada por su contenido
    And debe devolver el identificador de la orden original
    And no debe crear una nueva reserva

  Scenario: Detectar duplicado entre canales distintos
    Given que existe una orden registrada recibida por API
    When el mismo pedido llega por carga masiva con otro identificador externo
    Then el OMS debe detectarlo como duplicado por su contenido
    And no debe crear una nueva orden ni una nueva reserva

  # Escenarios negativos

  Scenario: No marcar como duplicada una orden fuera de ventana
    Given que existe una orden similar del mismo cliente y destinatario
    And la nueva orden corresponde a una ventana temporal distinta
    When el OMS ejecuta la regla de deduplicación
    Then no debe clasificarla como duplicada
    And debe continuar con la validación normal

  # Nota: el reintento exacto de la misma solicitud se cubre en HU-INI01-RF04 (idempotencia).
```

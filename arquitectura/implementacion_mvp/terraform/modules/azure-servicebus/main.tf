variable "namespace_name" { type = string }
variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "topic_name" { type = string }
variable "tags" { type = map(string) }

resource "azurerm_servicebus_namespace" "this" {
  name                = var.namespace_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Standard"
  tags                = var.tags
}

resource "azurerm_servicebus_topic" "orders" {
  name         = var.topic_name
  namespace_id = azurerm_servicebus_namespace.this.id
}

# Suscripción para el bridge hacia AWS, con dead-lettering nativo (DLQ)
resource "azurerm_servicebus_subscription" "bridge" {
  name                                 = "bridge-aws"
  topic_id                             = azurerm_servicebus_topic.orders.id
  max_delivery_count                   = 3
  dead_lettering_on_message_expiration = true
}

# Mínimo privilegio: SEND para productores (OMS), LISTEN para consumidores (bridge).
# No se expone la RootManageSharedAccessKey del namespace.
resource "azurerm_servicebus_topic_authorization_rule" "send" {
  name     = "send"
  topic_id = azurerm_servicebus_topic.orders.id
  listen   = false
  send     = true
  manage   = false
}

resource "azurerm_servicebus_topic_authorization_rule" "listen" {
  name     = "listen"
  topic_id = azurerm_servicebus_topic.orders.id
  listen   = true
  send     = false
  manage   = false
}

output "send_connection_string" {
  value     = azurerm_servicebus_topic_authorization_rule.send.primary_connection_string
  sensitive = true
}

output "listen_connection_string" {
  value     = azurerm_servicebus_topic_authorization_rule.listen.primary_connection_string
  sensitive = true
}

output "topic_id" {
  value = azurerm_servicebus_topic.orders.id
}

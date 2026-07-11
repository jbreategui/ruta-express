variable "name" { type = string }
variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "retention_days" {
  type    = number
  default = 30
}
variable "tags" { type = map(string) }

resource "azurerm_log_analytics_workspace" "this" {
  name                = var.name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "PerGB2018"
  retention_in_days   = var.retention_days
  tags                = var.tags
}

output "workspace_id" {
  value = azurerm_log_analytics_workspace.this.id
}

output "primary_shared_key" {
  value     = azurerm_log_analytics_workspace.this.primary_shared_key
  sensitive = true
}

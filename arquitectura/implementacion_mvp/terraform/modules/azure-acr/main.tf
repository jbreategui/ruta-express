variable "registry_name" { type = string }
variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "aks_kubelet_object_id" { type = string }
variable "tags" { type = map(string) }

resource "azurerm_container_registry" "this" {
  name                = var.registry_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Basic"
  admin_enabled       = false
  tags                = var.tags
}

# AKS puede jalar imágenes del ACR (AcrPull) vía la identidad del kubelet (sin llaves)
resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.this.id
  role_definition_name = "AcrPull"
  principal_id         = var.aks_kubelet_object_id
}

output "login_server" {
  value = azurerm_container_registry.this.login_server
}

output "acr_id" {
  value = azurerm_container_registry.this.id
}

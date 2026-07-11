variable "vault_name" { type = string }
variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "aks_principal_id" { type = string }
variable "secrets" {
  type      = map(string)
  sensitive = true
}
variable "tags" { type = map(string) }

data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "this" {
  name                       = var.vault_name
  resource_group_name        = var.resource_group_name
  location                   = var.location
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  rbac_authorization_enabled = true
  tags                       = var.tags
}

# AKS lee secretos (get/list) vía su identidad — sin secretos en el código
resource "azurerm_role_assignment" "aks_secrets" {
  scope                = azurerm_key_vault.this.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = var.aks_principal_id
}

# Quien aplica el Terraform necesita poder escribir los secretos
resource "azurerm_role_assignment" "deployer_secrets" {
  scope                = azurerm_key_vault.this.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_key_vault_secret" "items" {
  # los nombres de secreto no son sensibles (sí sus valores) -> nonsensitive para el for_each
  for_each     = nonsensitive(toset(keys(var.secrets)))
  name         = each.value
  value        = var.secrets[each.value]
  key_vault_id = azurerm_key_vault.this.id
  depends_on   = [azurerm_role_assignment.deployer_secrets]
}

output "vault_uri" {
  value = azurerm_key_vault.this.vault_uri
}

output "vault_id" {
  value = azurerm_key_vault.this.id
}

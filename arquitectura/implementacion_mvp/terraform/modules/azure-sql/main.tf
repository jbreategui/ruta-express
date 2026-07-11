variable "server_name" { type = string }
variable "db_name" { type = string }
variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "admin_login" { type = string }
variable "admin_password" {
  type      = string
  sensitive = true
}
variable "pe_subnet_id" { type = string }
variable "vnet_id" { type = string }
variable "tags" { type = map(string) }

resource "azurerm_mssql_server" "this" {
  name                          = var.server_name
  resource_group_name           = var.resource_group_name
  location                      = var.location
  version                       = "12.0"
  administrator_login           = var.admin_login
  administrator_login_password  = var.admin_password
  minimum_tls_version           = "1.2"
  public_network_access_enabled = false
  tags                          = var.tags
}

resource "azurerm_mssql_database" "this" {
  name      = var.db_name
  server_id = azurerm_mssql_server.this.id
  sku_name  = "Basic"
  tags      = var.tags
}

# --- Private endpoint: la SQL obtiene una IP privada en la subred de PE ---
resource "azurerm_private_dns_zone" "sql" {
  name                = "privatelink.database.windows.net"
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

# Vincula la zona DNS privada a la VNet -> los pods resuelven el FQDN a la IP privada
resource "azurerm_private_dns_zone_virtual_network_link" "sql" {
  name                  = "link-sql"
  resource_group_name   = var.resource_group_name
  private_dns_zone_name = azurerm_private_dns_zone.sql.name
  virtual_network_id    = var.vnet_id
  tags                  = var.tags
}

resource "azurerm_private_endpoint" "sql" {
  name                = "pe-${var.server_name}"
  resource_group_name = var.resource_group_name
  location            = var.location
  subnet_id           = var.pe_subnet_id

  private_service_connection {
    name                           = "psc-sql"
    private_connection_resource_id = azurerm_mssql_server.this.id
    subresource_names              = ["sqlServer"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "dns-sql"
    private_dns_zone_ids = [azurerm_private_dns_zone.sql.id]
  }

  tags = var.tags
}

output "connection_string" {
  value     = "Server=tcp:${azurerm_mssql_server.this.fully_qualified_domain_name},1433;Database=${var.db_name};"
  sensitive = true
}

output "server_fqdn" {
  value = azurerm_mssql_server.this.fully_qualified_domain_name
}

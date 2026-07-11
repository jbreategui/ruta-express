package main

import rego.v1

# El SQL Server no debe exponer acceso público y debe exigir TLS 1.2+.

deny contains msg if {
	some rc in input.resource_changes
	rc.type == "azurerm_mssql_server"
	rc.change.after.public_network_access_enabled == true
	msg := sprintf("%s: el SQL Server no debe tener acceso público", [rc.address])
}

deny contains msg if {
	some rc in input.resource_changes
	rc.type == "azurerm_mssql_server"
	rc.change.after.minimum_tls_version != "1.2"
	msg := sprintf("%s: el SQL Server debe exigir TLS 1.2", [rc.address])
}

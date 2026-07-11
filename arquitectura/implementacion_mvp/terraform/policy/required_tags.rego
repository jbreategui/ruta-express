package main

import rego.v1

# Exige tags de gobierno SOLO en los recursos que soportan tags
# (no en subnets, role assignments, secrets, topics, links... que no los tienen).

taggable := {
	"azurerm_resource_group",
	"azurerm_kubernetes_cluster",
	"azurerm_container_registry",
	"azurerm_servicebus_namespace",
	"azurerm_mssql_server",
	"azurerm_mssql_database",
	"azurerm_log_analytics_workspace",
	"azurerm_key_vault",
	"azurerm_virtual_network",
	"azurerm_private_endpoint",
	"azurerm_private_dns_zone",
}

required := {"Environment", "ManagedBy", "Owner", "CostCenter"}

# Claves de tags de forma segura: si 'tags' es null o no-objeto, devuelve set vacío
# (así un recurso con "tags": null también se deniega en vez de escapar).
tag_keys(after) := object.keys(t) if {
	t := object.get(after, "tags", {})
	is_object(t)
}

tag_keys(after) := set() if {
	not is_object(object.get(after, "tags", {}))
}

deny contains msg if {
	some rc in input.resource_changes
	taggable[rc.type]
	missing := required - tag_keys(rc.change.after)
	count(missing) > 0
	msg := sprintf("%s: faltan tags de gobierno %v", [rc.address, missing])
}

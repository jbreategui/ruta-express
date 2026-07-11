package main

import rego.v1

# Evita sobredimensionar el clúster: node pool con conteo acotado (control de costo).

max_node_count := 3

deny contains msg if {
	some rc in input.resource_changes
	rc.type == "azurerm_kubernetes_cluster"
	some pool in rc.change.after.default_node_pool
	pool.node_count > max_node_count
	msg := sprintf("%s: node_count %d supera el máximo permitido %d", [rc.address, pool.node_count, max_node_count])
}

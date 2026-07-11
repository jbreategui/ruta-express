package main

import rego.v1

# Restringe la región de Azure a las permitidas por gobierno.

allowed := {"eastus", "eastus2"}

deny contains msg if {
	some rc in input.resource_changes
	loc := rc.change.after.location
	loc != null
	not allowed[loc]
	msg := sprintf("%s: región '%s' no permitida (permitidas: %v)", [rc.address, loc, allowed])
}

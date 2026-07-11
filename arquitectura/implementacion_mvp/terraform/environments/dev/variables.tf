variable "owner_alias" {
  type        = string
  description = "Identificador del grupo/alumno para el naming (evita colisiones)."
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "location" {
  type        = string
  default     = "eastus2"
  description = "Región de Azure (restringida por policy allowed_location.rego)."
}

variable "cost_center" {
  type    = string
  default = "CC-UTEC-M04"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "sql_admin_login" {
  type    = string
  default = "omsadmin"
}

variable "sql_admin_password" {
  type        = string
  sensitive   = true
  description = "Password del SQL admin. Se pasa por variable de entorno TF_VAR_sql_admin_password, NUNCA en el repo."
}

variable "node_vm_size" {
  type    = string
  default = "Standard_B2s"
}

variable "node_count" {
  type    = number
  default = 1
}

locals {
  prefix = "${var.owner_alias}-${var.environment}"
  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = var.owner_alias
    CostCenter  = var.cost_center
  }
  suffix = random_string.suffix.result
  # URL SQLAlchemy para el OMS contra Azure SQL (driver pymssql).
  # urlencode del password: evita que caracteres como @ : / # rompan el parseo.
  oms_database_url = "mssql+pymssql://${var.sql_admin_login}:${urlencode(var.sql_admin_password)}@${module.sql.server_fqdn}:1433/omsdb"
}

# Sufijo aleatorio para garantizar unicidad global (ACR, Key Vault, SQL, Service Bus)
resource "random_string" "suffix" {
  length  = 5
  upper   = false
  special = false
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-${local.prefix}-oms"
  location = var.location
  tags     = local.tags
}

# --- Red: VNet con subredes para AKS y private endpoints ---
module "network" {
  source              = "../../modules/azure-network"
  name                = local.prefix
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  tags                = local.tags
}

# --- Azure: observabilidad, clúster, registro, bus, datos, secretos ---
module "observability" {
  source              = "../../modules/azure-observability"
  name                = "log-${local.prefix}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  tags                = local.tags
}

module "aks" {
  source              = "../../modules/azure-aks"
  cluster_name        = "aks-${local.prefix}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  node_vm_size        = var.node_vm_size
  node_count          = var.node_count
  log_analytics_id    = module.observability.workspace_id
  vnet_subnet_id      = module.network.aks_subnet_id
  tags                = local.tags
}

module "acr" {
  source                = "../../modules/azure-acr"
  registry_name         = replace("acr${local.prefix}${local.suffix}", "-", "")
  resource_group_name   = azurerm_resource_group.rg.name
  location              = var.location
  aks_kubelet_object_id = module.aks.kubelet_object_id
  tags                  = local.tags
}

module "servicebus" {
  source              = "../../modules/azure-servicebus"
  namespace_name      = "sb-${local.prefix}-${local.suffix}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  topic_name          = "orders-events"
  tags                = local.tags
}

module "sql" {
  source              = "../../modules/azure-sql"
  server_name         = "sql-${local.prefix}-${local.suffix}"
  db_name             = "omsdb"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  admin_login         = var.sql_admin_login
  admin_password      = var.sql_admin_password
  pe_subnet_id        = module.network.pe_subnet_id
  vnet_id             = module.network.vnet_id
  tags                = local.tags
}

module "keyvault" {
  source              = "../../modules/azure-keyvault"
  vault_name          = replace("kv${local.prefix}${local.suffix}", "-", "")
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  aks_principal_id    = module.aks.kubelet_object_id
  secrets = {
    "servicebus-send"   = module.servicebus.send_connection_string
    "servicebus-listen" = module.servicebus.listen_connection_string
    "database-url"      = local.oms_database_url
    "sqs-queue-url"     = module.sqs.queue_url
    "bridge-aws-key-id" = module.bridge_identity.access_key_id
    "bridge-aws-secret" = module.bridge_identity.secret_access_key
  }
  tags = local.tags
}

# --- AWS: cola intercloud, tabla, función de última milla, identidad del bridge ---
module "sqs" {
  source     = "../../modules/aws-sqs"
  queue_name = "${local.prefix}-ultima-milla"
  tags       = local.tags
}

module "dynamodb" {
  source     = "../../modules/aws-dynamodb"
  table_name = "${local.prefix}-deliveries"
  tags       = local.tags
}

module "lambda" {
  source        = "../../modules/aws-lambda"
  function_name = "${local.prefix}-ultima-milla"
  source_dir    = "${path.module}/../../../apps/ultima-milla"
  sqs_arn       = module.sqs.queue_arn
  dynamodb_arn  = module.dynamodb.table_arn
  dynamodb_name = module.dynamodb.table_name
  tags          = local.tags
}

module "bridge_identity" {
  source    = "../../modules/aws-bridge-identity"
  name      = local.prefix
  queue_arn = module.sqs.queue_arn
  tags      = local.tags
}

# --- Workloads en AKS (OMS, mocks, bridge) ---
module "workloads" {
  source                       = "../../modules/k8s-workloads"
  acr_login_server             = module.acr.login_server
  image_tag                    = "latest"
  keyvault_uri                 = module.keyvault.vault_uri
  database_url                 = local.oms_database_url
  servicebus_send_connection   = module.servicebus.send_connection_string
  servicebus_listen_connection = module.servicebus.listen_connection_string
  sqs_queue_url                = module.sqs.queue_url
  aws_region                   = var.aws_region
  bridge_aws_key_id            = module.bridge_identity.access_key_id
  bridge_aws_secret            = module.bridge_identity.secret_access_key
  depends_on                   = [module.aks, module.acr]
}

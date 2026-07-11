output "resource_group" {
  value = azurerm_resource_group.rg.name
}

output "aks_cluster" {
  value = module.aks.cluster_name
}

output "acr_login_server" {
  value = module.acr.login_server
}

output "servicebus_topic" {
  value = module.servicebus.topic_id
}

output "sqs_queue_url" {
  value = module.sqs.queue_url
}

output "dynamodb_table" {
  value = module.dynamodb.table_name
}

output "lambda_function" {
  value = module.lambda.function_arn
}

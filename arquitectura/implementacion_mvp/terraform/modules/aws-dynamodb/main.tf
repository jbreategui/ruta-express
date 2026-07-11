variable "table_name" { type = string }
variable "tags" { type = map(string) }

resource "aws_dynamodb_table" "this" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "event_id"

  attribute {
    name = "event_id"
    type = "S"
  }
  attribute {
    name = "order_id"
    type = "S"
  }

  # Índice secundario para consultar el estado de entrega POR ORDEN (RF-22)
  global_secondary_index {
    name            = "by-order"
    hash_key        = "order_id"
    projection_type = "ALL"
  }

  tags = var.tags
}

output "table_arn" {
  value = aws_dynamodb_table.this.arn
}

output "table_name" {
  value = aws_dynamodb_table.this.name
}

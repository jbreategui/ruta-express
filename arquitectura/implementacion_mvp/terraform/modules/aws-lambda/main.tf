variable "function_name" { type = string }
variable "source_dir" { type = string }
variable "sqs_arn" { type = string }
variable "dynamodb_arn" { type = string }
variable "dynamodb_name" { type = string }
variable "tags" { type = map(string) }

# Empaqueta el código de apps/ultima-milla en un zip (100% IaC)
data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = var.source_dir
  output_path = "${path.module}/ultima-milla.zip"
}

# Rol de ejecución (sin llaves): logs + leer SQS + escribir DynamoDB — mínimo privilegio
resource "aws_iam_role" "lambda" {
  name = "${var.function_name}-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
  tags = var.tags
}

resource "aws_iam_role_policy" "lambda" {
  name = "${var.function_name}-policy"
  role = aws_iam_role.lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect   = "Allow"
        Action   = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
        Resource = var.sqs_arn
      },
      {
        Effect   = "Allow"
        Action   = ["dynamodb:PutItem", "dynamodb:GetItem"]
        Resource = var.dynamodb_arn
      }
    ]
  })
}

resource "aws_lambda_function" "this" {
  function_name    = var.function_name
  role             = aws_iam_role.lambda.arn
  handler          = "handler.handler"
  runtime          = "python3.12"
  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256

  environment {
    variables = {
      DELIVERIES_TABLE = var.dynamodb_name
    }
  }

  tags = var.tags
}

# SQS dispara la Lambda (event source mapping)
resource "aws_lambda_event_source_mapping" "sqs" {
  event_source_arn = var.sqs_arn
  function_name    = aws_lambda_function.this.arn
  batch_size       = 10
}

output "function_arn" {
  value = aws_lambda_function.this.arn
}

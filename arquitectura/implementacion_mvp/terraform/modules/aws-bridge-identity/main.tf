variable "name" { type = string }
variable "queue_arn" { type = string }
variable "tags" { type = map(string) }

# Usuario IAM de MÍNIMO PRIVILEGIO: solo enviar mensajes a esa cola SQS.
resource "aws_iam_user" "bridge" {
  name = "${var.name}-bridge"
  tags = var.tags
}

resource "aws_iam_user_policy" "bridge" {
  name = "${var.name}-bridge-send"
  user = aws_iam_user.bridge.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["sqs:SendMessage"]
      Resource = var.queue_arn
    }]
  })
}

resource "aws_iam_access_key" "bridge" {
  user = aws_iam_user.bridge.name
}

output "access_key_id" {
  value = aws_iam_access_key.bridge.id
}

output "secret_access_key" {
  value     = aws_iam_access_key.bridge.secret
  sensitive = true
}

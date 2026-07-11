variable "queue_name" { type = string }
variable "tags" { type = map(string) }

# Cola de dead-letter: los mensajes que fallan 3 veces se apartan (no se pierden)
resource "aws_sqs_queue" "dlq" {
  name = "${var.queue_name}-dlq"
  tags = var.tags
}

resource "aws_sqs_queue" "this" {
  name = var.queue_name
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })
  tags = var.tags
}

output "queue_url" {
  value = aws_sqs_queue.this.url
}

output "queue_arn" {
  value = aws_sqs_queue.this.arn
}

output "dlq_arn" {
  value = aws_sqs_queue.dlq.arn
}

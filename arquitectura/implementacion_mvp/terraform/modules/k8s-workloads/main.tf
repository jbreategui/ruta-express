variable "acr_login_server" { type = string }
variable "image_tag" {
  type    = string
  default = "latest"
}
variable "keyvault_uri" { type = string }

# Secretos inyectados como env (vía kubernetes_secret). En producción se migra a
# Key Vault CSI + Workload Identity (ver 03_gaps_para_despliegue.md, bloque C).
variable "database_url" {
  type      = string
  sensitive = true
}
variable "servicebus_send_connection" {
  type      = string
  sensitive = true
}
variable "servicebus_listen_connection" {
  type      = string
  sensitive = true
}
variable "sqs_queue_url" { type = string }
variable "aws_region" { type = string }
variable "bridge_aws_key_id" {
  type      = string
  sensitive = true
}
variable "bridge_aws_secret" {
  type      = string
  sensitive = true
}

locals {
  oms_image    = "${var.acr_login_server}/oms:${var.image_tag}"
  mocks_image  = "${var.acr_login_server}/mocks:${var.image_tag}"
  bridge_image = "${var.acr_login_server}/bridge:${var.image_tag}"
}

# Secretos de la app (sourced desde Terraform, no hardcodeados en la imagen)
resource "kubernetes_secret" "app" {
  metadata { name = "app-secrets" }
  data = {
    DATABASE_URL                 = var.database_url
    SERVICEBUS_SEND_CONNECTION   = var.servicebus_send_connection   # OMS (producer)
    SERVICEBUS_LISTEN_CONNECTION = var.servicebus_listen_connection # bridge (consumer)
    SQS_QUEUE_URL                = var.sqs_queue_url
    AWS_ACCESS_KEY_ID            = var.bridge_aws_key_id
    AWS_SECRET_ACCESS_KEY        = var.bridge_aws_secret
  }
}

# ---------- OMS ----------
resource "kubernetes_deployment" "oms" {
  metadata {
    name   = "oms"
    labels = { app = "oms" }
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "oms" } }
    template {
      metadata { labels = { app = "oms" } }
      spec {
        container {
          name  = "oms"
          image = local.oms_image
          port { container_port = 8080 }
          env {
            name  = "WMS_URL"
            value = "http://wms-mock"
          }
          env {
            name  = "ERP_URL"
            value = "http://erp-mock"
          }
          env {
            name = "DATABASE_URL"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.app.metadata[0].name
                key  = "DATABASE_URL"
              }
            }
          }
          env {
            name = "SERVICEBUS_CONNECTION"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.app.metadata[0].name
                key  = "SERVICEBUS_SEND_CONNECTION" # OMS solo publica -> SEND
              }
            }
          }
          resources {
            requests = { cpu = "100m", memory = "128Mi" }
            limits   = { cpu = "500m", memory = "512Mi" }
          }
          liveness_probe {
            http_get {
              path = "/health"
              port = 8080
            }
            initial_delay_seconds = 15
            period_seconds        = 20
          }
          readiness_probe {
            http_get {
              path = "/health"
              port = 8080
            }
            initial_delay_seconds = 10
            period_seconds        = 10
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "oms" {
  metadata { name = "oms" }
  spec {
    selector = { app = "oms" }
    port {
      port        = 80
      target_port = 8080
    }
    type = "LoadBalancer"
  }
}

# ---------- WMS mock ----------
resource "kubernetes_deployment" "wms_mock" {
  metadata {
    name   = "wms-mock"
    labels = { app = "wms-mock" }
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "wms-mock" } }
    template {
      metadata { labels = { app = "wms-mock" } }
      spec {
        container {
          name  = "wms-mock"
          image = local.mocks_image
          port { container_port = 8080 }
          env {
            name  = "WMS_MODE"
            value = "ok"
          }
          resources {
            requests = { cpu = "50m", memory = "64Mi" }
            limits   = { cpu = "250m", memory = "256Mi" }
          }
          readiness_probe {
            http_get {
              path = "/health"
              port = 8080
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "wms_mock" {
  metadata { name = "wms-mock" }
  spec {
    selector = { app = "wms-mock" }
    port {
      port        = 80
      target_port = 8080
    }
  }
}

# ---------- ERP mock ----------
resource "kubernetes_deployment" "erp_mock" {
  metadata {
    name   = "erp-mock"
    labels = { app = "erp-mock" }
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "erp-mock" } }
    template {
      metadata { labels = { app = "erp-mock" } }
      spec {
        container {
          name  = "erp-mock"
          image = local.mocks_image
          port { container_port = 8080 }
          env {
            name  = "ERP_MODE"
            value = "accept"
          }
          resources {
            requests = { cpu = "50m", memory = "64Mi" }
            limits   = { cpu = "250m", memory = "256Mi" }
          }
          readiness_probe {
            http_get {
              path = "/health"
              port = 8080
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "erp_mock" {
  metadata { name = "erp-mock" }
  spec {
    selector = { app = "erp-mock" }
    port {
      port        = 80
      target_port = 8080
    }
  }
}

# ---------- Bridge (Service Bus -> SQS) ----------
resource "kubernetes_deployment" "bridge" {
  metadata {
    name   = "bridge"
    labels = { app = "bridge" }
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "bridge" } }
    template {
      metadata { labels = { app = "bridge" } }
      spec {
        container {
          name  = "bridge"
          image = local.bridge_image
          env {
            name  = "AWS_REGION"
            value = var.aws_region
          }
          env {
            name = "SERVICEBUS_CONNECTION"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.app.metadata[0].name
                key  = "SERVICEBUS_LISTEN_CONNECTION" # bridge solo consume -> LISTEN
              }
            }
          }
          env {
            name = "SQS_QUEUE_URL"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.app.metadata[0].name
                key  = "SQS_QUEUE_URL"
              }
            }
          }
          env {
            name = "AWS_ACCESS_KEY_ID"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.app.metadata[0].name
                key  = "AWS_ACCESS_KEY_ID"
              }
            }
          }
          env {
            name = "AWS_SECRET_ACCESS_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.app.metadata[0].name
                key  = "AWS_SECRET_ACCESS_KEY"
              }
            }
          }
          resources {
            requests = { cpu = "50m", memory = "64Mi" }
            limits   = { cpu = "250m", memory = "256Mi" }
          }
        }
      }
    }
  }
}

provider "azurerm" {
  features {}
}

provider "aws" {
  region = var.aws_region
}

# El provider de Kubernetes se autentica con el kubeconfig que emite AKS.
# Nota: en la práctica se aplica en dos etapas (infra AKS primero, luego workloads)
# para evitar la dependencia del provider sobre un clúster aún no creado.
provider "kubernetes" {
  host                   = module.aks.kube_host
  client_certificate     = base64decode(module.aks.client_certificate)
  client_key             = base64decode(module.aks.client_key)
  cluster_ca_certificate = base64decode(module.aks.cluster_ca_certificate)
}

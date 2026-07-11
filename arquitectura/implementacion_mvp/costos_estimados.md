# Costos Estimados por Nube — MVP (nivel dev)

**Región referencia:** Azure East US 2 / AWS us-east-1. SKUs de nivel **dev**. Son **precios de lista aproximados** — confirmar en Azure Pricing Calculator y AWS Pricing Calculator (varían por región y cambian con el tiempo).

## Azure
| Recurso | SKU | USD/mes (dev) |
|---|---|---|
| AKS — plano de control | Free tier | 0 |
| AKS — node pool (OMS + 2 mocks + bridge como pods) | 1× Standard_B2s | ~30 – 40 |
| Container Registry (ACR) | Basic | ~5 |
| Service Bus | Standard | ~10 |
| Azure SQL Database | Basic (5 DTU, 2 GB) | ~5 |
| Log Analytics | Pay-as-you-go (poco volumen) | 0 – 3 |
| Key Vault | Standard | <1 |
| Private Endpoint (SQL) | por hora + datos | ~7 – 8 |
| IP pública estándar (LoadBalancer del OMS) | por hora | ~3 – 4 |
| **Subtotal Azure** | | **~60 – 76** |

## AWS
| Recurso | SKU | USD/mes (dev) |
|---|---|---|
| Lambda | On-demand (free tier) | ~0 |
| DynamoDB | On-demand | 0 – 1 |
| SQS (cola + DLQ) | Estándar (1M req/mes gratis) | ~0 |
| **Subtotal AWS** | | **~0 – 1** |

## Total
| Nube | USD/mes (encendido el mes completo) |
|---|---|
| Azure | ~60 – 76 |
| AWS | ~0 – 1 |
| **Total** | **~60 – 77** |

> **Costo real:** con la práctica del profe de `terraform destroy` al terminar cada sesión, el gasto tiende a **pocos dólares**. La tabla es "si quedara encendido un mes". Drivers: el **node pool de AKS** (se apaga con destroy) y el **Service Bus Standard** (se puede bajar a Basic con colas en vez de topic).

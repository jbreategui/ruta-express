# Hito 4 — Afinamiento Técnico (decisiones finas antes de construir)

Cierra los cuatro puntos que quedaban flojos: bridge intercloud, secretos/identidad, runbook + evidencia y costos reales.

---

## 1. Bridge intercloud (Azure Service Bus → AWS Lambda)
El evento nace en Azure (bus) y lo consume la última milla en AWS. Cómo cruza la nube:

| Opción | Cómo | Trade-off |
|---|---|---|
| A. Event Grid → webhook | Service Bus emite a Event Grid; una suscripción webhook llama a la Lambda URL (HTTPS) | Nativo, pero Service Bus→Event Grid pide tier Premium (caro para dev) |
| **B. Bridge worker → SQS → Lambda** | Un worker liviano en Azure lee del Service Bus y **reenvía a una cola AWS SQS**; la Lambda se dispara por SQS | **Durable** (SQS retiene + DLQ + retry), barato, 100% IaC, y el bridge es en sí el patrón "adaptador" del caso |
| C. HTTP directo a Lambda URL | El publicador llama la Function URL por HTTPS | Simplísimo pero sin durabilidad (si la Lambda cae, se pierde) |
| D. PrivateLink / VPN intercloud | Conectividad privada real | Producción; overkill para el MVP dev |

**Decisión: Opción B (bridge → SQS → Lambda).** Es coherente con el C4 ("AMQP → bridge"), con el tema *store-and-forward* del caso, y con lo enseñado (colas SQS como desacople, Módulo 3). El bridge worker se despliega como otra Container App; la SQS + el *event source mapping* de la Lambda son Terraform puro.

- **Flujo:** `Service Bus (topic) → bridge worker (Azure) → SQS (AWS) → Lambda (AWS) → DynamoDB`.
- **Durabilidad:** SQS con **DLQ** (redrive policy, maxReceiveCount=3) — nada se pierde si la Lambda falla (RF-16 replicado en el borde AWS).
- **Credencial del salto:** el bridge necesita permiso `sqs:SendMessage` **solo** a esa cola → usuario IAM de mínimo privilegio, con la key guardada en **Key Vault** (ver §2). *(Alternativa producción: rol IAM cross-account con OIDC, sin llaves — se anota como mejora.)*
- **En local (sin desplegar):** el `ConsolePublisher` del OMS ya imprime el evento; el bridge y la SQS quedan listos en IaC. La simplificación queda declarada.

## 2. Secretos e identidad (SEG-03/04/05/06 · Módulo 6 Zero Trust)
Principio: **cero secretos hardcodeados**, identidad como perímetro, mínimo privilegio.

| Componente | Cómo se autentica / guarda secretos |
|---|---|
| **OMS / mocks / bridge (pods en AKS)** | **En el MVP:** las cadenas se inyectan como `kubernetes_secret` (creado por Terraform desde los outputs de SQL/bus/SQS), montadas como env por `secret_key_ref` — **no van en la imagen ni en `tfvars`**. **Futuro (bloque C):** migrar a **Key Vault CSI + Workload Identity** para no tener el secreto en el clúster. |
| **OMS → Azure SQL** | Ideal: **Managed Identity + Azure AD auth** (sin password). Baseline MVP: cadena en Key Vault. |
| **OMS → Service Bus** | Reglas de autorización **Send** (OMS) y **Listen** (bridge) por *topic* — mínimo privilegio, sin la RootManageSharedAccessKey. *(Futuro: Managed Identity + RBAC.)* |
| **Bridge → SQS (AWS)** | Usuario IAM de mínimo privilegio (`sqs:SendMessage` a una cola); access key en **Key Vault**. |
| **Lambda → DynamoDB / SQS** | **Rol de ejecución IAM** (sin llaves): `dynamodb:PutItem/GetItem` a una tabla + lectura de la SQS. |
| **CI (GitHub Actions)** | **GitHub Secrets** para credenciales; el CI solo hace `validate/plan` (sin secretos de runtime). El `apply` final se corre local con `az login` / `aws sso login`. |
| **Terraform** | Variables sensibles con `sensitive = true`; **ningún secreto en el repo**; el state (si es local) no se commitea (`.gitignore`). |

Regla de oro: lo único que cruza nubes con "llave" es el bridge→SQS, y esa llave vive en Key Vault con permiso a una sola cola. Todo lo demás usa identidad gestionada o rol.

## 3. Runbook de despliegue + plan de evidencia
### Secuencia de despliegue (el `apply` final)
Todo vive en un solo root module `environments/dev/` con los dos providers, así que **un `terraform apply` resuelve el orden** por dependencias (el bridge de Azure referencia el output `sqs_url` de AWS → Terraform crea AWS primero). Flujo disciplinado (mantra del profe):
```
1. terraform fmt -check
2. terraform init
3. terraform validate
4. terraform plan -out=plan.tfplan
5. terraform show -json plan.tfplan > plan.json
6. conftest test plan.json -p ../../policy/     # gate de políticas
7. terraform apply plan.tfplan                  # PASO FINAL (con confirmación)
8. (verificar — ver evidencia)
9. terraform destroy                             # limpieza acotada al terminar
```
> Nada de `az group delete`: la limpieza es `terraform destroy` del propio stack.

### Evidencia por patrón y por requisito (para el informe)
| Qué demostrar | Escenario / comando | Evidencia |
|---|---|---|
| **Idempotencia** (RF-04) | `POST /v1/ordenes` 2× con misma `Idempotency-Key` | mismo `orderId`, sin doble reserva |
| **Deduplicación** (RF-03) | mismo pedido, otra key | respuesta `duplicate: true` |
| **Saga + compensación** (RF-08) | ERP mock en modo `reject` | `audit_movements`: Compensacion + evento InventarioLiberado + estado `Fallida` |
| **Resiliencia** (RF-11) | WMS mock en modo `slow`/`down` | logs: Circuit Breaker abre + reintentos; orden no se pierde |
| **EDA** | crear orden OK | evento en Service Bus / outbox; log de la Lambda por SQS |
| **CQRS** (RF-10) | `GET /v1/ordenes/{id}` | read model con estado e inventario |
| **2 nubes** | `terraform output` | recursos en Azure + AWS |
| **100% IaC** | árbol `terraform/` + `plan` + `conftest` en verde | plan.json + salida conftest |
| **Costos** | `costos_estimados.md` | tabla por nube/mes |

## 4. Costos estimados por nube (precios de lista, a confirmar en calculadora)
Región referencia: Azure **East US 2** / AWS **us-east-1**. SKUs de nivel **dev**, con scale-to-zero. Son **precios de lista aproximados** — confírmalos en Azure Pricing Calculator y AWS Pricing Calculator (varían por región y cambian con el tiempo).

### Azure
| Recurso | SKU | Precio lista aprox. | USD/mes (dev) |
|---|---|---|---|
| **AKS — plano de control** | Free tier | $0 (Free) / ~$0.10/h (Standard) | 0 |
| **AKS — node pool** (OMS + 2 mocks + bridge como pods) | 1× `Standard_B2s` (2 vCPU, 4GB) | ~$30/mes (o `B2pls_v2` más barata) | ~30 – 40 |
| Container Registry (ACR) | Basic | ~$0.167/día | ~5 |
| Service Bus | Standard | ~$0.0135/h base + $0.80/M ops | ~10 |
| Azure SQL Database | Basic (5 DTU, 2GB) | ~$4.90/mes | ~5 |
| Log Analytics | Pay-as-you-go | ~$2.30/GB (primeros GB con free grant) | 0 – 3 |
| Key Vault | Standard | ~$0.03/10k operaciones | <1 |
| **Subtotal Azure** | | | **~50 – 64** |

> **Cambio vs. Container Apps:** al usar **AKS** (por coherencia con el C4) el costo sube ~$35/mes respecto a Container Apps, por el **node pool + ACR**. Es el precio de mantener el diseño; se mitiga con una VM Burstable pequeña y **`terraform destroy` al terminar** (el node pool es el driver, y apagado no cuesta).

### AWS
| Recurso | SKU | Precio lista aprox. | USD/mes (dev) |
|---|---|---|---|
| Lambda | On-demand | Free tier: 1M req + 400k GB-s/mes | ~0 |
| DynamoDB | On-demand | $1.25/M escrituras, $0.25/M lecturas; 25GB gratis | 0 – 1 |
| SQS | Estándar | Primer 1M req/mes gratis | ~0 |
| **Subtotal AWS** | | | **~0 – 1** |

### Total
| Nube | USD/mes (dev, encendido todo el mes) |
|---|---|
| Azure | ~50 – 64 |
| AWS | ~0 – 1 |
| **Total** | **~50 – 65** |

> Con la práctica del profe (`terraform destroy` al terminar cada sesión), el costo real tiende a **centavos/pocos dólares**. La tabla es "si quedara encendido un mes completo". Los drivers de costo son el **node pool de AKS** y el **Service Bus Standard**; el node pool se apaga con `destroy`, y Service Bus se puede bajar a Basic (colas en vez de topic).

---
*Afinamiento técnico — Hito 4 · Grupo 6 RutaExpress*

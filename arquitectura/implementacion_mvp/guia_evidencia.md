# Guía de Evidencia — Hito 4 (qué capturar en el despliegue)

Paso a paso de qué ejecutar, **qué capturar** (captura/log/salida) y **qué demuestra** — mapeado al enunciado. Se ejecuta durante el deploy (bloque B), con tus credenciales.

> Prep: `az login` (Azure for Students) · credenciales de tu cuenta AWS · `az aks get-credentials` para tener `kubectl`.

---

## 0. Evidencia de IaC (antes de aplicar)
| Acción | Capturar | Demuestra |
|---|---|---|
| `terraform validate` | salida "Success" | IaC válido |
| `terraform plan -out=plan.tfplan` | resumen del plan (recursos a crear en Azure **y** AWS) | 100% IaC, 2 nubes |
| `conftest test plan.json -p ../../policy/` | salida sin violaciones | gate de políticas (tags, región, SQL privada) |

## 1. Evidencia de despliegue (2 nubes)
| Acción | Capturar | Demuestra |
|---|---|---|
| `terraform output` | outputs: `aks_cluster`, `acr_login_server`, `servicebus_topic`, `sqs_queue_url`, `dynamodb_table`, `lambda_function` | recursos en **Azure + AWS** creados por IaC |
| Portal Azure → grupo de recursos | captura con AKS, Service Bus, SQL, Key Vault, Log Analytics | nube 1 (Azure) |
| Consola AWS → Lambda / DynamoDB / SQS | captura de los 3 recursos | nube 2 (AWS) |
| `kubectl get pods,svc` | oms, wms-mock, erp-mock, bridge Running + IP pública del OMS | workloads desplegados |

> Guarda la IP pública del OMS: `OMS=$(kubectl get svc oms -o jsonpath='{.status.loadBalancer.ingress[0].ip}')`

## 2. Evidencia por patrón / escenario

### 2.1 Orden feliz — EDA + Saga + CQRS + intercloud
```bash
curl -X POST http://$OMS/v1/ordenes -H "Idempotency-Key: k1" \
  -H "Content-Type: application/json" \
  -d '{"client_id":"C1","lines":[{"sku":"SKU-001","qty":2}]}'
```
| Capturar | Demuestra |
|---|---|
| Respuesta `201 {"status":"Lista"}` | Saga completa OK |
| `curl http://$OMS/v1/ordenes/<orderId>` → estado del read model | **CQRS** (RF-10) |
| Logs de la Lambda (CloudWatch) mostrando el evento recibido | **EDA + bridge intercloud** (RF-14) |
| Ítem en **DynamoDB** con ese order | última milla registró la entrega (RF-22) |

### 2.2 Idempotencia (RF-04)
```bash
# repetir el POST con la MISMA Idempotency-Key k1
curl -X POST http://$OMS/v1/ordenes -H "Idempotency-Key: k1" ... (mismo body)
```
| Capturar | Demuestra |
|---|---|
| Devuelve el **mismo orderId**, sin crear otra orden ni reservar de nuevo | idempotencia por key |

### 2.3 Deduplicación (RF-03)
```bash
# mismo pedido, key distinta
curl -X POST http://$OMS/v1/ordenes -H "Idempotency-Key: k2" ... (mismo body que k1)
```
| Capturar | Demuestra |
|---|---|
| Respuesta con `"duplicate": true` y el orderId original | dedup por hash de contenido |

### 2.4 Compensación de la Saga (RF-08)
```bash
kubectl set env deployment/erp-mock ERP_MODE=reject   # el ERP ahora rechaza
# esperar el rollout y crear una orden nueva:
curl -X POST http://$OMS/v1/ordenes -H "Idempotency-Key: k3" \
  -d '{"client_id":"C2","lines":[{"sku":"SKU-001","qty":1}]}'
```
| Capturar | Demuestra |
|---|---|
| Respuesta con `status: "Fallida"` | la Saga abortó |
| Logs del OMS con `Compensacion` / evento `InventarioLiberado` | **compensación** ejecutada |
| El inventario reservado volvió a su valor | rollback correcto |

### 2.5 Resiliencia — WMS caído (RF-11)
```bash
kubectl set env deployment/wms-mock WMS_MODE=down    # el WMS falla
curl -X POST http://$OMS/v1/ordenes -H "Idempotency-Key: k4" \
  -d '{"client_id":"C3","lines":[{"sku":"SKU-001","qty":1}]}'
```
| Capturar | Demuestra |
|---|---|
| Logs del OMS con **reintentos** y **Circuit Breaker** abriendo | Retry + Circuit Breaker |
| Respuesta con `status: "Reservando"` (no marcada reservada, no perdida) | no-pérdida (lección Cyber Days) |

Recuperación (el WMS vuelve y se reprocesa la orden):
```bash
kubectl set env deployment/wms-mock WMS_MODE=ok           # WMS recuperado
curl -X POST http://$OMS/v1/ordenes/<orderId>/reintentar  # reprocesa la orden
```
| Capturar | Demuestra |
|---|---|
| Respuesta con `status: "Lista", reintentado: true` | la orden **se reprocesa**, no se perdió (RF-11) |

### 2.6 DLQ y durabilidad (RF-16)
| Capturar | Demuestra |
|---|---|
| Config de **DLQ** en la suscripción del Service Bus (portal) | dead-letter en el bus |
| Config de **redrive policy** (maxReceiveCount=3) en la SQS (consola) | DLQ en el salto intercloud |

## 3. Evidencia de seguridad
| Acción | Capturar | Demuestra |
|---|---|---|
| Portal Azure → SQL → Networking | "Public network access: Disabled" + private endpoint | SQL solo por red privada |
| `kubectl get secret app-secrets` | existe (sin mostrar valores) | secretos inyectados, no hardcodeados |

## 4. Evidencia de costos
| Capturar | Demuestra |
|---|---|
| `costos_estimados.md` | tabla de costos por nube al mes |
| Azure → Cost Management (tras unas horas) | gasto real ínfimo desde el crédito de estudiante |

## 5. Limpieza (mostrar disciplina de costos)
```bash
terraform destroy    # elimina todo el stack (NUNCA az group delete)
```
| Capturar | Demuestra |
|---|---|
| Salida de `destroy` completada | limpieza controlada, sin recursos huérfanos |

---

## Checklist final (enunciado → evidencia)
- [ ] **2 nubes** → §1 (outputs + capturas Azure y AWS)
- [ ] **3+ patrones** → §2.1 (EDA/Saga/CQRS), §2.4 (Saga/compensación), §2.5 (Resiliencia), Microservicios (§1 pods)
- [ ] **100% IaC** → §0 (plan) + §1 (outputs)
- [ ] **Costos por nube** → §4
- [ ] **API mock** → §2.4 y §2.5 (mocks WMS/ERP en distintos modos)

*Guía de evidencia — Hito 4 · Grupo 6 RutaExpress · con apoyo de IA (Claude — Anthropic)*

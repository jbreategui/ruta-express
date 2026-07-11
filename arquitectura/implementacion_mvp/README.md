# MVP — RutaExpress (Hito 4: Implementación)

Prototipo de la **Alternativa A (orquestada)** recomendada en el Hito 3. Multinube **Azure + AWS**, **100% IaC** (Terraform), con 5 patrones demostrables. Está **listo para desplegar**; el `terraform apply` es el paso final (no se ejecuta durante el desarrollo).

## Qué demuestra
Ruta crítica del caso: orden → **dedup + idempotencia** → **Saga** (reserva) → WMS "caído" → **Circuit Breaker/Retry** → evento al bus → **bridge → SQS** → **Lambda** última milla. Con **compensación** si el ERP rechaza y **DLQ** si el consumidor falla.

Patrones: **Microservicios, EDA, Saga, CQRS, Resiliencia** (≥3 exigidos).

## Estructura
```
apps/
  oms/            Microservicio OMS (FastAPI): dedup, idempotencia, Saga, CQRS, resiliencia  + tests
  mocks/          WMS/ERP simulados (modos ok/slow/down · accept/reject)
  ultima-milla/   Lambda AWS: consume SQS, dedup por eventId (Inbox), DynamoDB
  bridge/         Worker Service Bus → SQS
terraform/
  environments/dev/   Composición (providers, main, variables, tfvars, outputs)
  modules/            azure-network, azure-aks, azure-acr, azure-servicebus, azure-sql,
                      azure-observability, azure-keyvault, aws-sqs, aws-dynamodb, aws-lambda,
                      aws-bridge-identity, k8s-workloads
  policy/             OPA/Rego (tags, región, seguridad, límites)
.github/workflows/ci.yml   Valida IaC + apps (NO despliega)
costos_estimados.md
```

## Verificación local (sin nube)
```bash
# Apps
cd apps/oms && pip install -r requirements.txt
flake8 app tests && python -m pytest tests/ -q      # 20 tests

# IaC (sin backend ni credenciales)
cd terraform/environments/dev
terraform init -backend=false && terraform validate
```

## Despliegue (PASO FINAL — solo cuando se decida desplegar)
> Requiere credenciales: `az login` y `aws sso login` / `aws configure`.
> La limpieza es `terraform destroy` acotado — **nunca** `az group delete`.

```bash
cd terraform/environments/dev
export TF_VAR_sql_admin_password='<password-fuerte>'   # NUNCA en el repo
terraform init

# --- ETAPA 1: infraestructura (todo menos los workloads de K8s) ---
terraform plan -out=plan.tfplan
terraform show -json plan.tfplan > plan.json
conftest test plan.json -p ../../policy/               # gate de políticas
terraform apply -target=module.network -target=module.observability -target=module.aks \
  -target=module.acr -target=module.servicebus -target=module.sql -target=module.keyvault \
  -target=module.sqs -target=module.dynamodb -target=module.lambda \
  -target=module.bridge_identity

# --- Construir y subir imágenes al ACR (ya existe tras la etapa 1) ---
ACR=$(terraform output -raw acr_login_server)
az acr build -r ${ACR%%.*} -t oms:latest    ../../../apps/oms
az acr build -r ${ACR%%.*} -t mocks:latest  ../../../apps/mocks
az acr build -r ${ACR%%.*} -t bridge:latest ../../../apps/bridge

# --- ETAPA 2: workloads en AKS (con las imágenes ya presentes) ---
terraform apply                                        # crea deployments/services

# --- Verificar (evidencia) y limpiar ---
# probar escenarios; luego:
terraform destroy                                      # limpieza acotada (NUNCA az group delete)
```
> **Por qué dos etapas:** el provider de Kubernetes se autentica contra el clúster que crea AKS,
> y los deployments referencian imágenes del ACR — ambos deben existir antes. La etapa 1 crea la
> infra, se suben las imágenes, y la etapa 2 despliega los workloads.

## Alcance (recordatorio)
El MVP implementa un **subconjunto** de los 29 RF (la ruta crítica ~15 RF). El resto queda cubierto en el diseño (Hito 3). GCP/analítica, portal/CRM/TMS reales, GitOps y multi-región son **trabajo futuro**.

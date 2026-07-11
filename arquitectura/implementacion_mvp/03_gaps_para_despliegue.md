# Hito 4 — Gaps para un despliegue funcional

Qué falta entre "valida en local" y "corre end-to-end en la nube". Ordenado por: **(A) lo que se puede cerrar YA sin desplegar** y **(B) lo que necesita credenciales en el momento del deploy**.

Leyenda esfuerzo: **S** = corto (<30 min) · **M** = medio (30-90 min) · **L** = largo (>90 min).

---

## A. Gaps que se cierran AHORA (código/IaC, sin desplegar)

| # | Gap | Estado | Qué se hizo |
|---|---|---|---|
| A1 | OMS sin driver para Azure SQL | ✅ **Cerrado** | `pymssql` en requirements; `DATABASE_URL` de despliegue documentada (mssql+pymssql) e inyectada por Terraform |
| A2 | Inyección de secretos a los pods | ✅ **Cerrado** | `kubernetes_secret` desde Terraform (SQL/bus/SQS/AWS) inyectado como env por `secret_key_ref` en OMS y bridge |
| A3 | Bridge sin Dockerfile/requirements | ✅ **Cerrado** | `apps/bridge/{requirements.txt, Dockerfile}` (azure-servicebus + boto3) |
| A4 | Credencial cross-cloud del bridge | ✅ **Cerrado** | Módulo `aws-bridge-identity`: usuario IAM con `sqs:SendMessage`; key en Key Vault + secret del pod |
| A5 | Apply de dos etapas no formalizado | ✅ **Cerrado** | Runbook del README con la secuencia `-target` (etapa 1 infra → build/push → etapa 2 workloads) |
| A6 | Pods sin probes ni límites | ✅ **Cerrado** | liveness/readiness (`/health`) + requests/limits en los deployments |
| A7 | Nombres globalmente únicos | ✅ **Cerrado** | `random_string` sufijo en ACR, Key Vault, SQL y Service Bus |
| A8 | Red del OMS → Azure SQL | ✅ **Cerrado (private endpoint)** | Módulo `azure-network` (VNet + subredes); AKS con **Azure CNI** en la VNet; **private endpoint** de la SQL + **zona DNS privada** vinculada a la VNet. La SQL sigue sin acceso público (cumple la policy) y los pods la resuelven por IP privada. |

## B. Pasos que requieren TUS credenciales (en el momento del deploy)

| # | Paso | Qué es |
|---|---|---|
| B1 | `terraform plan` real | Con `az login` + `aws` configurados; confirma nombres únicos, cuotas y que el plan esté limpio |
| B2 | **Build + push de imágenes** al ACR | `az acr build` (o docker build+push) para OMS, mocks y bridge — la infra debe existir primero (ACR) |
| B3 | `terraform apply` etapa 1 (infra) | Crea AKS, ACR, Service Bus, SQL, Key Vault, y en AWS SQS/DynamoDB/Lambda |
| B4 | `terraform apply` etapa 2 (workloads) | Despliega OMS/mocks/bridge en AKS (con las imágenes ya en ACR) |
| B5 | Verificación (evidencia) | Probar los escenarios (dedup, Saga, compensación, WMS caído) y capturar evidencia para el informe |
| B6 | `terraform destroy` | Limpieza acotada al terminar (nunca `az group delete`) |

## C. "Pro" — opcional, el diseño lo pide pero el MVP puede diferir
- **Key Vault CSI + Workload Identity** para secretos (en vez del `kubernetes_secret` de A2). Más seguro, más complejo. **L**
- **API Management / WAF** delante del OMS (el MVP expone el OMS por LoadBalancer directo). **L**
- **Private endpoint "propio"** (vs firewall) para SQL/bus. **M-L**

---

## Estimación honesta
- **Cerrar todo el bloque A** (sin desplegar): ~**medio día** de trabajo de código/IaC. Deja el MVP realmente listo para un `apply` con alta probabilidad de éxito.
- **Bloque B** (con tus credenciales): ~**2-4 horas** incluyendo el primer `apply`, build de imágenes y **depurar la integración** (siempre aparece algo en el primer deploy real).
- **Bloque C**: solo si el profe exige el nivel "producción"; para un MVP se declara como trabajo futuro.

## Ruta recomendada
1. ✅ **Bloque A cerrado (A1-A8)** — todo escrito y validado sin desplegar. El `terraform validate` pasa con private endpoint incluido.
2. Cuando estés listo, tú corres **B1-B6** con tus credenciales (Azure for Students + AWS propia); yo te acompaño depurando lo que salga.
3. **C** queda como trabajo futuro en el informe.

## Cuentas a usar (sin gastar dinero real)
- **Azure:** Azure for Students ($100 crédito, sin tarjeta) — cubre AKS/bus/SQL por unas horas (~$1-3).
- **AWS:** cuenta propia (IAM funciona → el bridge va sin cambios; uso en free tier ≈ $0). **No** usar AWS Academy.
- Disciplina: **desplegar → evidencia → `terraform destroy`**.

*Gaps de despliegue — Hito 4 · Grupo 6 RutaExpress*

# 10 — El despliegue: cómo el diseño se vuelve infraestructura

> **Meta:** entender dónde se despliega cada contenedor, cómo se conectan las nubes y con
> on-premises, qué zonas y controles de seguridad aplican, y cómo todo esto se construye con código
> (IaC/Terraform). Fuentes: `anexos/despliegue_red_seguridad.md`, `implementacion_mvp/`.

---

## 1. Qué es el diagrama de despliegue (y por qué faltaba)

El C4 tiene una **cuarta vista** además de los 3 niveles: el **diagrama de despliegue**. Responde:
*"¿en qué máquina/nube/red vive físicamente cada contenedor, y cómo se conectan?"* Aquí **sí** se
muestra infraestructura: regiones, redes (VNet/VPC), subredes, private endpoints, VPN, zonas de
seguridad. **Es el nivel que el profesor pidió** — *"ver la red, cómo se conectan y la seguridad"*.

> No es un nivel C4 numerado (1/2/3); es la **vista complementaria oficial** (Deployment diagram).
> Por eso vive en `anexos/`, no dentro de las alternativas.

---

## 2. Dónde vive cada cosa (las 4 zonas físicas)

```
   INTERNET ──HTTPS/TLS 443──▶ [WAF / Front Door]  ← única puerta pública
                                      │
   ┌── AZURE (hub principal) ─────────┼──────────────────────────────┐
   │  DMZ:      API Management (OAuth2/OIDC, cuotas)                  │
   │  Apps:     OMS (AKS) — sin IP pública                           │
   │  Datos:    Azure SQL + Bus (Event Hubs/Service Bus) — Priv.End. │
   │  Transv.:  Entra ID + Key Vault + Azure Monitor                 │
   └──────────┬───────────────────────┬──────────────────────────────┘
        VPN IPsec                 bridge IPsec / PrivateLink
              │                        │
      ┌── ON-PREMISES ──┐     ┌── AWS (última milla) ──┐   ┌── GCP (analítica) ──┐
      │  WMS   ERP      │     │  Backend móvil (ECS)   │   │  Pub/Sub, Dataflow  │
      │  (VPN IPsec)    │     │  DynamoDB, S3+KMS      │   │  BigQuery, Vertex   │
      └─────────────────┘     └────────────────────────┘   └─────────────────────┘
```

| Contenedor | Nube / Nodo | Por qué ahí |
|---|---|---|
| WAF + API Management | Azure (borde) | Gobierno de API ya en Azure; punto único de entrada |
| OMS + SQL + Bus + IAM + Obs | Azure (privada) | Núcleo transaccional; menor latencia entre ellos |
| Backend móvil + DynamoDB + S3 | AWS | Última milla y evidencias ya operan en AWS |
| Analítica y rutas | GCP | BigQuery/Vertex para optimización y predicción |
| WMS + ERP | On-premises | Legados que se integran, no se migran |

---

## 3. Las zonas de seguridad (defensa en capas)

| Zona | Qué contiene | Controles |
|---|---|---|
| **Borde (capa 7)** | Front Door + WAF + APIM | TLS, WAF, DDoS, rate limiting, OAuth2/OIDC |
| **Apps (privada)** | OMS (AKS), backend móvil | Sin IP pública, NSG/SG **deny by default**, TLS intra-red |
| **Datos (privada)** | SQL, bus, DynamoDB, S3 | **Private Endpoints**, cifrado en reposo, nunca en subred pública |
| **Transversal** | Entra ID, Key Vault, Obs | IAM federada, secretos gestionados, trazabilidad |
| **On-premises** | WMS, ERP | Solo por **VPN site-to-site (IPsec)** |

**Principio rector: Zero Trust** ("nunca confiar, siempre verificar") + **defensa en profundidad**
(ninguna protección depende de un solo mecanismo).

---

## 4. Cómo se conectan las nubes (conectividad intercloud)

| Enlace | Fase inicial | Evolución | Cifrado |
|---|---|---|---|
| Azure ↔ AWS | VPN IPsec | ExpressRoute + Direct Connect | IPsec + mTLS |
| Azure ↔ GCP | VPN IPsec | ExpressRoute + Cloud Interconnect | IPsec + mTLS |
| Azure ↔ On-prem | VPN IPsec | ExpressRoute | IPsec + mTLS |
| Móvil ↔ AWS | HTTPS + OAuth2 (Auth Code + PKCE) | — | TLS + KMS |

- **CIDR sin solapamiento** (Azure 10.0/16, AWS 10.1/16, GCP 10.2/16) — requisito para enrutar
  entre nubes sin colisiones.
- **mTLS** *(extensión)*: además del túnel IPsec, los servicios que cruzan de nube se autentican
  con certificados — si el túnel se compromete, igual no pueden hablar con los nuestros.

---

## 5. Recuperación ante desastres (DR por criticidad)

El caso nace de 6h de caída (USD 1.1M). Por eso la estrategia DR se elige **por ámbito**, según el
trade-off RTO (cuánto tiempo inactivo) / RPO (cuántos datos se pierden) / costo:

| Ámbito | Estrategia | RTO / RPO | Por qué |
|---|---|---|---|
| Núcleo Azure (OMS/SQL/bus) | **Warm Standby** | Minutos / seg–min | Ruta crítica; Backup/Restore tardaría horas |
| Evidencias (S3) | **Cross-region + versionado** | Minutos / ≈0 | Sostienen USD 2.4M; sin reproceso posible |
| Sync móvil (DynamoDB) | PITR | Decenas min / min | Se reconstruye desde eventos |
| Analítica GCP | Backup and Restore | Horas / horas | No es ruta crítica |
| Última milla | **Store-and-forward** en el equipo | opera degradado | Resiliencia en el borde |

> Lectura clave: la caída de **una** nube no tumba a las otras — el bus desacopla y el móvil opera
> offline. Es exactamente lo que faltó en Cyber Days.

---

## 6. Cómo se construye de verdad: IaC con Terraform (el MVP del Hito 4)

El diseño no se despliega a mano — se declara en **código (Infraestructura como Código)**. El MVP
implementa la **Alternativa A** en **Azure + AWS**, 100% Terraform, con 5 patrones demostrables.

**Estructura Terraform:**
- `environments/dev/` — la composición (providers, main, variables, tfvars).
- `modules/` — 12 módulos: azure-network, azure-aks, azure-acr, azure-servicebus, azure-sql,
  azure-observability, azure-keyvault, aws-sqs, aws-dynamodb, aws-lambda, aws-bridge-identity,
  k8s-workloads.
- `policy/` — OPA/Rego: valida tags, región, seguridad y límites **antes** de aplicar (gate).

**El despliegue es en DOS etapas** (y hay una razón):
1. **Etapa 1 — infraestructura:** crea red, AKS, ACR, Service Bus, SQL, Key Vault, SQS, DynamoDB,
   Lambda. Luego se **construyen y suben las imágenes** al ACR.
2. **Etapa 2 — workloads:** despliega los deployments/services en AKS (que ya referencian las
   imágenes del ACR).
- **Por qué dos etapas:** el provider de Kubernetes se autentica contra el clúster que crea AKS, y
  los deployments necesitan las imágenes ya presentes. Primero la infra, luego los workloads.

**Estado actual:** está **listo para desplegar** — `terraform validate` pasa y 20 tests pasan. El
`terraform apply` es el **paso final**, con credenciales (`az login` + `aws sso login`), y **no se
ejecuta durante el desarrollo**.

> Limpieza: `terraform destroy` **acotado** — nunca `az group delete` (borraría recursos ajenos).

---

## 7. Los patrones que el MVP demuestra
Ruta crítica: orden → **dedup + idempotencia** → **Saga** (reserva) → WMS "caído" → **Circuit
Breaker/Retry** → evento al bus → **bridge → SQS** → **Lambda** última milla, con **compensación**
si el ERP rechaza y **DLQ** si el consumidor falla. Patrones: **Microservicios, EDA, Saga, CQRS,
Resiliencia** (≥3 exigidos).

---

## Cómo defenderlo ante el comité
1. *"Cada contenedor vive donde mejor rinde: núcleo en Azure, última milla en AWS, analítica en
   GCP, legados on-premises."*
2. *"Seguridad en capas con Zero Trust: única entrada por WAF, backends sin IP pública, datos con
   private endpoint, on-prem solo por VPN IPsec, y mTLS entre nubes."*
3. *"DR por criticidad, no una sola estrategia — Warm Standby en la ruta crítica porque Backup/
   Restore tardaría horas, lo inaceptable tras Cyber Days."*
4. *"Todo es Infraestructura como Código (Terraform, 12 módulos + políticas OPA); está listo para
   desplegar en dos etapas, el apply es el paso final con credenciales."*

---

## Archivos fuente
- `diseno_solucion/anexos/despliegue_red_seguridad.md` — diagrama de despliegue, zonas, DR
- `implementacion_mvp/README.md` — estructura y despliegue en dos etapas
- `implementacion_mvp/terraform/` — módulos + environments/dev + policy (OPA/Rego)
- `implementacion_mvp/costos_estimados.md` — estimación de costos
- `implementacion_mvp/INFORME_HITO4.md` — informe consolidado del MVP

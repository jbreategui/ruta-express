# Fase 5b · Nivel 2 — Contenedores (Alternativa B)

> **Meta:** entender los contenedores de B y por qué se diferencian de A **solo en el núcleo
> Azure**. Fuente: `alternativa_B_coreografiada/02_nivel2_contenedores.md` · `B_n2_contenedores.png`.

---

## 1. Lo que NO cambia respecto a A

Fuera de Azure, A y B son **iguales**: AWS (Backend Última Milla + DynamoDB + S3/KMS) y GCP
(Pub/Sub, BigQuery, Vertex AI) son idénticos, y los 6 sistemas externos también. **Toda la
diferencia está en el núcleo Azure.** Es a propósito: así el comité compara arquitecturas, no
proveedores.

---

## 2. Lo que SÍ cambia: el núcleo Azure se reorganiza

| Núcleo Azure | **A (orquestada)** | **B (coreografiada)** |
|---|---|---|
| El "cerebro" | **1 OMS monolítico** que orquesta | **se parte en servicios autónomos** |
| Órdenes | dentro del OMS | **Servicio de Órdenes** (separado) |
| Inventario | dentro del OMS | **Servicio de Inventario** (separado, autónomo) |
| WMS/ERP | el OMS los llama **directo** | **Adaptadores WMS/ERP** que reaccionan a eventos |
| Consultas | API + read model liviano | **Servicio de Consultas (CQRS)** dedicado |
| El bus | "Bus de Eventos" (transporte) | **"Log de Eventos" = fuente de verdad** (Event Sourcing) |

---

## 3. Los contenedores de B, uno por uno (todos 🟢 [NUEVO])

### Núcleo Azure
- **API Gateway y Gobierno** · Azure API Management
  - Igual que en A: puerta única, OAuth2/OIDC, rate limiting. → RF-12, RF-13.
- **Servicio de Órdenes** · Azure AKS
  - Recibe, valida, deduplica y da idempotencia; **publica eventos de orden**. Ya **no orquesta**
    nada — solo emite `OrdenValidada`. → RF-01…05.
- **Servicio de Inventario** · Azure AKS · *autónomo*
  - Escucha `OrdenValidada`, **reserva solo**, publica el resultado, y **se compensa por eventos**
    (escucha el rechazo y libera). Nadie le ordena. → RF-06…09.
- **Log de Eventos (fuente de verdad)** · Event Hubs + Service Bus
  - **El corazón.** No es un mensajero: es **Event Sourcing** — retiene los eventos de forma
    inmutable y el estado se reconstruye reproduciéndolos. Incluye colas, DLQ y replay. → RF-14…21.
- **Servicio de Consultas (CQRS)** · Azure AKS + Azure SQL
  - API de **solo lectura** sobre **proyecciones**. Las escrituras (comandos) van por un lado y las
    lecturas por otro. → RF-10.
- **Adaptadores WMS/ERP** · Azure AKS
  - Escuchan eventos del log, **traducen** al WMS/ERP on-premises y **publican el resultado como
    evento**. Ni siquiera el on-prem se llama directo. → RF-11.

### AWS, GCP y transversales — iguales que A
Backend Última Milla, DynamoDB, S3+KMS (AWS); Pub/Sub, BigQuery, Vertex AI (GCP); Observabilidad e
Identidad. Sin cambios.

### Externos ⚪ [EXISTENTE]
WMS y ERP (on-premises, vía VPN), TMS, Portal/CRM, Canales legados, Mapas.

---

## 4. El flujo de B: la "Saga coreografiada" (nadie manda, todo es reacción)

```
1. Servicio de Órdenes  ──publica──▶ "OrdenValidada" ──▶ [LOG DE EVENTOS]
2. [LOG] ──▶ Servicio de Inventario ──reserva──▶ publica "InventarioReservado" ──▶ [LOG]
3. [LOG] ──▶ Adaptador ERP ──valoriza──▶ publica "ValorizaciónConfirmada"/"Rechazada" ──▶ [LOG]
4. Si "Rechazada": [LOG] ──▶ Servicio de Inventario ──▶ publica "InventarioLiberado" (SE COMPENSA SOLO)
5. Los proyectores ──▶ read models ──▶ Portal/TMS ven el estado final
```

En A la Saga *ordenaba* cada paso (síncrono, hub). En B **nadie ordena**: cada servicio escucha un
evento y reacciona. La compensación no es una orden del jefe, es *"escuché el rechazo, me libero
solo"*. El replay del log reconstruye cualquier estado (RF-19).

---

## 5. El trade-off (de la nota del archivo)
Se **gana** autonomía, desacoplamiento y auditoría nativa (el log ES la historia). Se **paga** con:
un flujo más difícil de seguir —nadie "ve" la Saga completa, hay que reconstruirla por correlation
ID— y **consistencia eventual** en todas las lecturas (CQRS).

---

## Cómo defenderlo ante el comité
1. *"En B el OMS monolítico de A se parte en servicios autónomos; el bus se convierte en un Log de
   Eventos que es la fuente de verdad (Event Sourcing)."*
2. *"El flujo es una Saga coreografiada: nadie orquesta, cada servicio reacciona a eventos y
   publica los suyos; hasta el WMS/ERP se integran por eventos vía adaptadores."*
3. *"La misma huella multinube que A — solo cambia el núcleo Azure — para comparar arquitecturas,
   no proveedores."*

---

## Archivos fuente
- `alternativa_B_coreografiada/02_nivel2_contenedores.md` (+ sección "La Saga coreografiada")
- `diagramas_python/B_n2_contenedores.png`
- Contraste directo con A: [03_c4_nivel2_contenedores_A.md](03_c4_nivel2_contenedores_A.md)

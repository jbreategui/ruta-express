# Fase 3 — C4 Nivel 2: Contenedores

> **Meta de la fase:** entender cómo se abre la caja central del Nivel 1 en piezas desplegables
> (contenedores), con qué tecnología, en qué nube, y con qué protocolos se comunican.
> Convención: 🟢 **[NUEVO]** = lo que construimos · ⚪ **[EXISTENTE]** = AS-IS con lo que integramos.

---

## 1. Qué es el Nivel 2 y en qué se diferencia del Nivel 1

Responde: **"¿De qué piezas desplegables se compone mi plataforma, con qué tecnología, y cómo se
comunican?"** En el Nivel 1 la plataforma era una caja negra; aquí la **abrimos**.

| | Nivel 1 | Nivel 2 |
|---|---|---|
| Tu sistema | 1 caja negra | **se abre** en contenedores |
| Tecnología | prohibida | **obligatoria** (Azure SQL, AKS, DynamoDB…) |
| Íconos de nube | no | **sí** |
| Protocolos | pista ligera | **en cada flecha** (HTTPS, AMQP, TDS…) |

**¿Qué es un "contenedor" en C4?** NO es un contenedor Docker. Es **una unidad desplegable
independiente**: una app, una base de datos, un bus. Regla: **gruesos** (una app = una caja). No
se abre su interior — eso es Nivel 3.

---

## 2. La gran historia: huella multinube "best-of-breed"

La plataforma vive en **3 nubes**, cada una por lo que hace mejor (decisión de arquitectura, ADR):

```
   ┌─── AZURE (el núcleo) ──────┐   ┌─ AWS (última milla) ─┐   ┌─ GCP (analítica) ─┐
   │  API Gateway               │   │  Backend móvil       │   │  Pub/Sub          │
   │  OMS (orquestador)         │   │  DynamoDB (sync)     │   │  Dataflow         │
   │  Bus de Eventos            │   │  S3+KMS (evidencias) │   │  BigQuery         │
   │  Azure SQL                 │   │                      │   │  Vertex AI        │
   │  Observabilidad + Identidad│   └──────────────────────┘   └───────────────────┘
   └────────────────────────────┘
        [ON-PREMISES: WMS, ERP]  ← existentes, vía VPN
```

**Defensa:** *"No metemos todo en una nube. Best-of-breed: Azure líder empresarial (núcleo), AWS
última milla móvil, GCP innovador en datos/IA (analítica). La misma huella en ambas alternativas,
para que el comité compare arquitecturas, no proveedores."*

---

## 2b. ¿Qué estilo de arquitectura es este? (no son "cajas sueltas")

El Nivel 2 combina **4 estilos/patrones** trabajando juntos. Un comité quiere oír esto, no "tengo
un OMS y un bus":

| Estilo | Qué significa | Dónde se ve |
|---|---|---|
| **API-First** | El contrato (OpenAPI) antes del código; todo entra por un gateway | API Management = único punto de entrada |
| **Event-Driven (EDA)** | Comunicación por **eventos**, no llamadas directas | Bus de Eventos en el centro |
| **Saga Orquestada** | Una transacción larga (reservar+valorizar) la coordina un **director** que compensa si algo falla | OMS orquesta WMS → ERP |
| **Segmentación por nube** | Cada capa vive donde mejor rinde | Azure / AWS / GCP separados |

**Frase de oro:** *"Es API-First en el borde y Event-Driven en el corazón: síncrono para pedir,
asíncrono para propagar. Sobre eso, una Saga orquestada mantiene la consistencia entre sistemas
que no comparten base de datos."*

---

## 2c. Cómo se conectan: EL VIAJE DE UNA ORDEN (detallado)

Seguimos **UN pedido** desde que el cliente lo manda hasta que se entrega. En cada paso:
**de dónde sale → a dónde va → qué pasa ahí → en qué idioma (protocolo) se hablan**.

### FASE A — El pedido entra al sistema (todo en Azure)

**Paso 1 — El cliente manda la orden**
- **De:** Cliente B2B → **A:** API Gateway
- **Qué pasa:** una tienda quiere que RutaExpress reparta 100 paquetes; envía la orden por internet.
- **Idioma:** `HTTPS/REST` (llamada web cifrada) con `OAuth2` (adjunta un token = carnet que
  prueba quién es).
- **Clave:** el cliente NO habla con el OMS ni con la BD directamente. Solo conoce la puerta.

**Paso 2 — El portero revisa el carnet**
- **De:** API Gateway → **A:** Identidad (Entra ID)
- **Qué pasa:** el Gateway pregunta *"¿este token es real y vigente?"*
- **Idioma:** `OIDC`.
- **Clave:** si el token es falso o venció, el pedido **rebota aquí**. Primer filtro de seguridad.

**Paso 3 — El portero pasa el pedido al jefe**
- **De:** API Gateway → **A:** OMS
- **Qué pasa:** token válido → reenvía la orden ("crear pedido") al cerebro.
- **Idioma:** `HTTPS/REST` interno.

**Paso 4 — El jefe registra el pedido**
- **De:** OMS → **A:** Azure SQL
- **Qué pasa (4 cosas):** (1) **deduplica** (*¿ya recibí este pedido?* — los 32,000 duplicados del
  caso); (2) le da un **ID interno único**; (3) fija el **estado canónico** ("Validada" = la única
  verdad; la máquina de estados es `Recibida → Validada → Reservando → Reservada → Lista`, o
  `Fallida/Cancelada`); (4) escribe en el **outbox** ("tengo que avisar que se creó" — clave para la
  Fase C).
- **Idioma:** `TDS` por **private endpoint** (cable privado; la BD no está en internet).

### FASE B — La Saga: apartar y valorizar (corazón de INI-01)

El jefe debe hacer **dos cosas que van juntas o ninguna**: apartar el producto Y ponerle precio.

**Paso 5 — Aparta el producto en el almacén**
- **De:** OMS → **A:** WMS (on-premises)
- **Qué pasa:** ordena *"aparta 100 unidades del SKU X"*; el WMS reserva stock real.
- **Idioma:** `API/eventos` por `VPN` (túnel privado hasta el almacén físico).

**Paso 6 — Le pone precio en contabilidad**
- **De:** OMS → **A:** ERP (on-premises)
- **Qué pasa:** ordena *"valoriza este movimiento"* (cuánto vale, para la factura).
- **Idioma:** `API/eventos` por `VPN`.

**¿Qué es la Saga y por qué importa?** El WMS y el ERP son **dos sistemas separados con bases de
datos distintas**; no puedes hacer una transacción única que abrace a los dos. El OMS actúa como
**director de orquesta**: si el paso 5 sale bien pero el paso 6 falla, el OMS **deshace** el paso 5
(le dice al WMS *"libera lo apartado"*) — eso es **compensar**. Así nunca queda producto apartado
sin factura ni factura sin producto. Evita las dobles reservas y conflictos del caso.

### FASE C — El aviso se propaga (asíncrono = el desacople)

**Paso 7 — El jefe suelta un aviso y sigue con lo suyo**
- **De:** OMS → **A:** Bus de Eventos
- **Qué pasa:** publica el evento *"pedido 123 confirmado"* y **se olvida** — no espera respuesta.
- **Idioma:** `AMQP` con el **patrón Outbox**.
- **¿Qué es el Outbox?** Es la lista que se escribió en el paso 4. Garantiza que el aviso salga
  **sí o sí**, aunque el Bus esté caído en ese segundo: cuando vuelva, el pendiente se envía. Nada
  se pierde.
- **Desacople temporal (lo más importante):** desde aquí **nadie necesita que el OMS esté vivo**;
  el aviso espera en el Bus. Es exactamente lo que faltó en Cyber Days: sin bus, cuando el WMS cayó
  6 h todo se apilaba y se perdía. Con bus, los avisos esperan pacientes.

### FASE D — El Bus reparte el aviso a todos

**Pasos 8, 9, 10 — El mismo aviso llega a varios destinos a la vez**
- **De:** Bus → **A:** (8) Backend Última Milla AWS `bridge→AMQP`; (9) TMS (despacho) y Portal/CRM
  (el cliente ve el estado); (10) Analítica GCP `bridge→Pub/Sub`.
- **Un evento, muchos consumidores:** el OMS publicó **una vez** (paso 7) y el Bus lo entregó a
  **4 destinos**. Un 5º interesado se suscribe al Bus y **no se toca el OMS**. Es lo contrario del
  AS-IS, donde cada sistema se conectaba con cada otro (spaghetti punto-a-punto) y cambiar uno
  rompía a los demás.

### FASE E — La última milla: el conductor entrega (AWS, INI-03)

**Paso 11 — El conductor hace la entrega**
- **De:** Conductor (app) → **A:** Backend Última Milla
- **Qué pasa:** marca "entregado", registra ubicación y sube evidencia (foto+firma). A veces sin
  señal → captura offline.
- **Idioma:** `HTTPS · OAuth2+PKCE` (PKCE = variante de OAuth2 más segura para móviles).

**Paso 12 — Se guarda lo capturado**
- **De:** Backend → **A:** (a) **DynamoDB** `SDK`: guarda el **estado de sincronización**. El patrón
  **store-and-forward** ("guarda y reenvía") vive en la **app del conductor** (que retiene lo
  capturado sin señal); DynamoDB es donde el backend registra ese estado al sincronizar. (b) **S3 +
  KMS** `HTTPS·KMS`: foto/firma **cifrada** y con **hash** (huella que prueba que no se alteró) —
  las evidencias de los USD 2.4M.

**Paso 13 — Se avisa que se entregó**
- **De:** Backend → **A:** Bus (de vuelta por el puente)
- **Qué pasa:** publica *"pedido 123 entregado"* → el Bus lo lleva al **Portal** (cliente ve
  "Entregado") y a **Finanzas** (ya puede cobrar, tiene la firma como prueba).
- **Idioma:** `bridge→AMQP`.

### FASE F — Los analistas mejoran las rutas (GCP)

**Paso 14 — Optimización**
- **De:** Analítica → **A:** TMS (rutas mejores) y Mapas (tráfico/ETA).
- **Qué pasa:** con los datos que le llegaron por el Bus, GCP calcula rutas óptimas y las devuelve.

### TRANSVERSAL — Vigilancia todo el tiempo

**Paso 15 — Todo se registra para auditar**
- **De:** OMS y Bus (y todos) → **A:** Observabilidad (Azure Monitor)
- **Qué pasa:** cada paso deja una traza con un **correlation ID** (mismo código pegado al pedido
  123 en todo su viaje). Buscas "123" y ves su recorrido completo cruzando las 3 nubes en un
  tablero.
- **Idioma:** `OTLP`.

### Imagen mental del viaje
```
  Cliente → [Portero Gateway] → [Jefe OMS] → apunta en la BD
                                    │
                                    ├─→ aparta en Almacén (WMS)   ┐ = la SAGA
                                    ├─→ precio en Contabilidad(ERP)┘
                                    │
                                    └─→ suelta 1 aviso al MENSAJERO (Bus)
                                                │
                            ┌───────────────────┼───────────────────┐
                            ▼                   ▼                   ▼
                      Repartidores(AWS)     Portal (cliente)     Analítica(GCP)
                            │
                      Conductor entrega → guarda foto/firma → avisa "entregado"
                            │
                            └─→ vuelve al Bus → Portal + Finanzas (ya cobra)
```

**Regla de oro del Nivel 2:** para **PEDIR algo urgente** (crear orden, apartar stock) → llamada
**directa y síncrona** (esperas respuesta). Para **AVISAR que algo pasó** (creado, entregado) →
**aviso al Bus** que reparte a todos (no esperas a nadie).

---

## 2d. Por qué las conexiones son ASÍ (reglas deliberadas)
- **El núcleo (B2B, operación, legados) entra por el Gateway** → los backends de Azure nunca se
  exponen a Internet. La app del conductor tiene su **propio borde autenticado en AWS**
  (HTTPS · OAuth2+PKCE) — es una segunda puerta, también controlada, no una excepción sin control.
- **El OMS es el único que escribe la verdad** (Azure SQL) → una sola fuente de verdad.
- **Nadie se integra punto-a-punto; todo pasa por el Bus** → mata el spaghetti. El OMS orquesta
  síncronamente **solo** la Saga (WMS+ERP), donde necesita consistencia inmediata.
- **On-premises solo por VPN**; **entre nubes, bridges privados** (nada por Internet público).

### AS-IS vs TO-BE (lo que hace válida la arquitectura)
| | AS-IS (problema) | TO-BE (tu Nivel 2) |
|---|---|---|
| Integración | punto-a-punto (spaghetti) | **bus central** (EDA) |
| Consistencia WMS+ERP | nadie coordina → conflictos | **Saga orquestada** + compensación |
| Pico sobre el WMS | todos lo siguen llamando → cae 6h | **Circuit Breaker + Retry** en el Adaptador WMS deja de llamarlo (fail-fast) + cola de reintento (ver N3, Fase 4) |
| Propagación de eventos | se pierde / desordena | **bus + Outbox** desacoplan en el tiempo |
| Entrada | cada sistema expone lo suyo | **un gateway** con OAuth2 |
| Datos | islas | **OMS = única verdad** |

---

## 3. Los contenedores, uno por uno

Todos los de adentro de la plataforma son 🟢 **[NUEVO]**. Los de afuera, ⚪ **[EXISTENTE]**.

### AZURE — el núcleo
- **API Gateway y Gobierno** · Azure API Management · 🟢 [NUEVO]
  - Puerta de entrada única. Contratos OpenAPI versionados, OAuth2/OIDC, rate limiting, cuotas.
    Nadie entra a los backends directo. → RF-12, RF-13.
- **OMS — Orquestador de Pedidos** · Azure AKS · 🟢 [NUEVO] *(evoluciona APP-02)*
  - El **cerebro** (INI-01): validación, deduplicación, idempotencia, estado canónico, **Saga**
    (coordina WMS+ERP) y conciliación. La "única verdad". → RF-01…11. AKS = escala en picos.
- **BD Transaccional** · Azure SQL · 🟢 [NUEVO]
  - Órdenes, inventario, **outbox** y auditoría. → RF-05, RF-07.
- **Bus de Eventos Central** · Azure Event Hubs + Service Bus · 🟢 [NUEVO]
  - El **sistema nervioso** (INI-02): eventos canónicos, colas, **DLQ**, replay, secuencia. Lo que
    faltó en Cyber Days. → RF-14…21.

### AWS — la última milla
- **Backend de Última Milla** · AWS ECS/Lambda · 🟢 [NUEVO] *(evoluciona APP-15)*
  - Backend de la app de conductores (INI-03): store-and-forward, tracking, taxonomía de
    excepciones, acciones automáticas. → RF-22…25, 28, 29.
- **Sincronización Móvil** · AWS DynamoDB · 🟢 [NUEVO]
  - Estado offline capturado sin señal + estado de sync. NoSQL = escritura rápida, HA, esquema
    flexible. → RF-22, RF-23.
- **Evidencias** · AWS S3 + KMS · 🟢 [NUEVO]
  - Fotos y firmas **cifradas (KMS)** con hash de integridad — sustentan los USD 2.4M. → RF-26/27.

### GCP — analítica
- **Optimización de Rutas y Analítica** · GCP (Pub/Sub, Dataflow, BigQuery, Vertex AI) · 🟢 [NUEVO]
  - Rutas dinámicas, SLA, predicción, tableros. GCP = innovador en datos/IA. Habilita las metas.

### Transversales
- **Observabilidad Unificada** · Azure Monitor + OpenTelemetry · 🟢 [NUEVO]
  - Trazas, métricas y **correlation ID end-to-end** (ver un pedido cruzar las 3 nubes). → RNF-05/15.
- **Identidad y Secretos** · Entra ID + Key Vault / KMS · 🟢 [NUEVO]
  - AuthN/Z federada + secretos. Perímetro de identidad (Zero Trust). → RNF-06/13.

### Externos ⚪ [EXISTENTE]
WMS y ERP (**on-premises**, vía VPN), TMS, Portal/CRM, Canales legados, Mapas — los mismos 6 del
Nivel 1. Ninguno aparece o desaparece entre niveles (coherencia N1↔N2).

---

## 4. Los protocolos (lo que va en cada flecha)

| Tipo | Cuándo | Protocolo | Ejemplo |
|---|---|---|---|
| **Síncrono** (comando/consulta) | necesito respuesta ya | HTTPS/REST + OAuth2 | Cliente → Gateway → OMS |
| **Asíncrono** (integración) | desacoplo en el tiempo | **AMQP** (eventos) | OMS → Bus (Outbox), Bus → móvil |
| **Base de datos** | | **TDS** · private endpoint | OMS → Azure SQL |
| **Hacia on-premises** | | API/eventos · **VPN** | OMS → WMS / ERP |
| **Entre nubes** | | **bridge intercloud** | Bus → AWS, Bus → GCP |

**La joya conceptual:** el asíncrono (AMQP + **Outbox**) elimina el **acoplamiento temporal** —
productor y consumidor no necesitan estar vivos a la vez. Es exactamente lo que falló en Cyber
Days: sin bus, cuando el WMS cayó 6h todo se apiló; con bus, los eventos esperan y se procesan al
reconectar.

- **Síncrono con OAuth2:** Client Credentials (sistema-a-sistema: portal, legados) y Authorization
  Code + PKCE (apps con usuario: conductores).
- **El evento también es contrato:** esquema versionado, cambios non-breaking, tolerancia al
  cambio. Se documenta con AsyncAPI *(extensión: es al evento lo que OpenAPI es al REST)*.

---

## 5. Detalles que el profe valora
- **Dirección de flechas = quién usa a quién:** el OMS *pide* tokens a IAM y *envía* telemetría a
  Observabilidad (no al revés).
- **Contenedores gruesos:** el bus NO se parte en "bus + colas"; la analítica NO se abre en 5
  cajas. Eso sería sobre-descomponer (parecería Nivel 3). Son 10 contenedores gruesos.
- **Sin códigos APP-XX en el diagrama:** APP-02, PLT-03 viven solo en la tabla de trazabilidad.

---

## Cómo defenderlo ante el comité
1. *"Abrí la plataforma en 10 contenedores desplegables, cada uno con su tecnología concreta."*
2. *"Huella multinube best-of-breed: Azure núcleo, AWS última milla, GCP analítica — igual en
   ambas alternativas."*
3. *"Cada relación lleva protocolo: síncrono HTTPS/OAuth2 para comandos, asíncrono AMQP con Outbox
   para desacoplar en el tiempo — lo que faltó en Cyber Days."*
4. *"Los externos son los mismos del Nivel 1; WMS y ERP siguen on-premises vía VPN."*

---

## Archivos fuente de esta fase
- `diseno_solucion/alternativa_A_orquestada/02_nivel2_contenedores.md` — diagrama + tabla de
  contenedores + decisiones de protocolo
- `diseno_solucion/diagramas_python/A_n2_contenedores.png` — render con íconos de nube
- `alternativa_B_coreografiada/02_nivel2_contenedores.md` — misma huella, coordinación distinta
  (se compara en la Fase 5)

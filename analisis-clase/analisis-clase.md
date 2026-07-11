# Análisis de Clases — Módulo 1: Fundamentos de Arquitectura Empresarial

> **Material de estudio analizado** (no solo transcripción).
> Curso: *Programa de Arquitectura de Soluciones Multinube* — UTEC. Docente: Geraldo Colchado.
> Fuentes analizadas:
> - `clase/Módulo 1 - Teoría 1 V1.00.pptx.pdf` (38 slides) → **Qué es AE, las 4 capas y el AS-IS**
> - `clase/Módulo 1 - Teoría 2 V1.00.pptx (1).pdf` (33 slides) → **El método ADM de TOGAF y el TO-BE**
> - `clase/Arquitectura Empresarial - Empresa de Seguros (Sesión 1).drawio` (11 páginas) → ejemplos de las 4 capas + AS-IS
> - `clase/Arquitectura Empresarial - Empresa de Seguros (Sesión 2).drawio` (17 páginas) → **ejemplo trabajado COMPLETO** de todos los entregables (capas + AS-IS + ADM completo + TO-BE)
>
> 💡 **Idea central:** las dos teorías te enseñan el *qué* y el *cómo*; los dos `.drawio` son la **plantilla resuelta** con una aseguradora ficticia. Tu proyecto (RutaExpress) consiste en **rehacer exactamente ese mismo conjunto de artefactos**, pero para tu caso.

---

## Índice

- [0. El mapa mental: cómo encaja todo](#0-el-mapa-mental-cómo-encaja-todo)
- [1. ¿Qué es Arquitectura Empresarial (AE)?](#1-qué-es-arquitectura-empresarial-ae)
- [2. Las 4 capas de la Arquitectura Empresarial](#2-las-4-capas-de-la-arquitectura-empresarial)
  - [2.1 Arquitectura de Negocio](#21-arquitectura-de-negocio)
  - [2.2 Arquitectura de Datos](#22-arquitectura-de-datos)
  - [2.3 Arquitectura de Aplicaciones](#23-arquitectura-de-aplicaciones)
  - [2.4 Arquitectura Tecnológica](#24-arquitectura-tecnológica)
- [3. El AS-IS (Situación Actual)](#3-el-as-is-situación-actual)
- [4. TOGAF y el método ADM](#4-togaf-y-el-método-adm)
  - [Las fases del ADM, una por una](#las-fases-del-adm-una-por-una)
- [5. El TO-BE, los gaps y la planificación](#5-el-to-be-los-gaps-y-la-planificación)
- [6. El ejemplo guía completo (drawio "Empresa de Seguros")](#6-el-ejemplo-guía-completo-drawio-empresa-de-seguros)
- [7. Cómo aplico esto a mi proyecto (RutaExpress)](#7-cómo-aplico-esto-a-mi-proyecto-rutaexpress)
- [8. Glosario rápido](#8-glosario-rápido)
- [9. Preguntas de repaso (las del docente)](#9-preguntas-de-repaso-las-del-docente)

---

## 0. El mapa mental: cómo encaja todo

Antes de los detalles, la foto grande. Todo el módulo gira alrededor de **TOGAF**, un estándar de arquitectura empresarial. TOGAF aporta dos cosas que se enseñan en orden:

| Lo que aprendes | En qué teoría | Pregunta que responde |
|---|---|---|
| Las **4 capas** de la arquitectura y sus artefactos | Teoría 1 | *¿De qué está hecha una empresa, vista como arquitectura?* |
| El **AS-IS** (foto del presente) | Teoría 1 (cierre) | *¿Cómo está la empresa HOY?* |
| El **método ADM** (8 fases) | Teoría 2 | *¿Cómo paso del HOY (AS-IS) al FUTURO (TO-BE) de forma ordenada?* |
| El **TO-BE** + gaps + iniciativas + roadmap | Teoría 2 | *¿Cómo quiero estar y qué proyectos me llevan ahí?* |

Y el flujo lógico que conecta las dos clases es este:

```
              ┌──────────────── ADM (método de TOGAF) ────────────────┐
   Preliminary → A.Vision → Req.Mgmt → B/C/D (AS-IS y TO-BE) → E.Oportunidades → F.Migración → G.Gobierno → H.Cambio
   (reglas)     (qué/por qué) (requisitos)  (las 4 capas hoy/mañana)   (iniciativas)  (roadmap)   (ejecución) (mejora)
```

> **Regla de oro del curso (la repite el docente):**
> *AS-IS = la fotografía del presente. TO-BE = cómo queremos estar. El ADM es la guía paso a paso para ir de uno al otro.*

---

## 1. ¿Qué es Arquitectura Empresarial (AE)?

**Definición breve (TOGAF):** la AE es la disciplina que **organiza y alinea estrategia, procesos, información, aplicaciones y tecnología** para que la empresa funcione de manera coherente y evolucione con control y gobierno.

**Definición formal (TOGAF):** un enfoque **estándar, iterativo y basado en mejores prácticas** para diseñar, gobernar y evolucionar la arquitectura de una organización, dando una **visión holística** que habilita decisiones estratégicas y la gestión del cambio.

**La analogía del docente (clave para entenderlo):** una empresa **sin** AE es como…
- una **ciudad que crece sin planificación**,
- una **casa construida sin plano**,
- una aseguradora donde **cada área compra su propio sistema sin coordinación**.
- 👉 Resultado: **caos, duplicidad de funcionalidades y alto costo de mantenimiento.**

> 📌 **Por qué importa para tu caso:** RutaExpress es exactamente ese escenario — WMS on-prem, TMS en Azure, app en AWS, optimizador en GCP, portales SaaS, integraciones punto a punto. Es la "ciudad sin planificación". La AE es lo que vas a usar para ordenarla.

---

## 2. Las 4 capas de la Arquitectura Empresarial

TOGAF divide la arquitectura en 4 capas. Las dos del medio (Datos + Aplicaciones) se agrupan como **"Arquitectura de Sistemas de Información"**.

| Capa | Responde a… | Incluye |
|---|---|---|
| **1. Negocio** | ¿Qué **hace** el negocio? | Capacidades, Procesos, Cadenas de Valor |
| **2. Datos** | ¿Qué **información** soporta al negocio? | Entidades de datos, Modelos de información |
| **3. Aplicaciones** | ¿Qué **aplicaciones** soportan las capacidades? | Portafolio de aplicaciones |
| **4. Tecnológica** | ¿Qué **infraestructura** habilita las aplicaciones? | Infra (on-prem/cloud), plataformas, redes, middleware, BD, seguridad |

> Las capas 2 y 3 juntas = **Arquitectura de Sistemas de Información**.

Cada capa tiene **artefactos** (diagramas/modelos) concretos que debes producir. Esto es lo más importante de Teoría 1, porque **cada artefacto es un entregable del proyecto.**

### 2.1 Arquitectura de Negocio

> *Define **qué hace** el negocio.* Artefactos: **Business Model Canvas, Mapa de Capacidades, Mapa de Procesos, Cadenas de Valor.**

**a) Business Model Canvas (BMC)** — marco visual que describe cómo el negocio **crea, entrega y captura valor** en una sola página, con **9 bloques**:
1. Propuesta de valor
2. Segmentos de clientes
3. Canales
4. Relación con clientes
5. Fuentes de ingreso
6. Recursos clave
7. Actividades clave
8. Socios clave
9. Estructura de costos

*Ejemplo (seguros):* propuesta = "emisión de pólizas en minutos, cobertura personalizada, atención 24/7"; segmentos = conductores urbanos, familias clase media, pymes; canales = portal web, app, brokers, bancaseguros, call center, WhatsApp; ingresos = primas anuales, endosos, comisiones; etc.

**b) Mapa de Capacidades** (*Business Capability Map*) — representación **jerárquica de lo que el negocio debe ser capaz de hacer** para ejecutar su estrategia, **independiente** de personas, procesos o tecnología.
- Es el modelo del **"qué hace"**, no del "cómo lo hace".
- Se organiza por niveles (Nivel 1 = capacidades core; Nivel 2 = desglose por dominio).
- *Ejemplo (seguros), Nivel 1:* Gestión Comercial · Suscripción y Emisión · Gestión de Siniestros · Gestión Actuarial · Gestión de Clientes · Gestión de Reaseguro · Gestión Financiera · Gobierno, Riesgo y Cumplimiento.

**c) Mapa de Procesos** — representación jerárquica de los procesos de negocio, mostrando **cómo se organizan y relacionan** para entregar valor (vista end-to-end).
- Es el modelo del **"cómo opera"** el negocio para ejecutar sus capacidades.
- Niveles: Nivel 1 = macroprocesos; Nivel 2 = subprocesos.
- *Ejemplo (seguros):* macroprocesos = Gestión Comercial → Emisión de Pólizas → Administración de Pólizas → Gestión de Siniestros → Gestión Financiera → Gestión Regulatoria; cada uno con objetivo + lista de subprocesos numerados (1.1, 1.2, …).

**d) Cadenas de Valor** (*Value Streams*) — la **secuencia end-to-end de etapas** que la organización ejecuta para entregar valor a un cliente/stakeholder, desde la necesidad inicial hasta el resultado final.
- Es el modelo de **"cómo fluye el valor"**.
- *Ejemplo (seguros):* "Emitir Póliza Digital" = Descubrir producto → Cotizar → Evaluar riesgo → Emitir póliza → Activar cobertura. Otros value streams: Gestionar Siniestro, Renovación y Fidelización, Venta vía Bancaseguros.

> 🔑 **Diferencia que cae en examen:** **Capacidad = QUÉ hace** (estable, no cambia seguido). **Proceso = CÓMO lo hace** (puede cambiar). **Value Stream = CÓMO FLUYE el valor** end-to-end hacia el cliente.

### 2.2 Arquitectura de Datos

> *Define **qué información** soporta al negocio.* Artefactos: **Mapa de Dominios de Datos** y **Modelo Conceptual de Datos**.

**a) Mapa de Dominios de Datos** (*Data Domain Map*) — responde: *¿qué información o entidades son **críticas** para el negocio?* Agrupa los datos en dominios.
- *Ejemplo (seguros):* Clientes · Pólizas · Siniestros · Pagos · Productos · Cotizaciones.

**b) Modelo Conceptual de Datos** — responde: *¿cuáles son las **entidades principales** y **cómo se relacionan**?* Es un diagrama de entidades con relaciones (no es el modelo físico de BD, es conceptual).
- *Ejemplo (seguros):* Cliente *posee* Póliza; Póliza *genera* Siniestro; Cliente *solicita* Cotización; Cotización *genera* Póliza; Pago *pertenece a* Póliza; etc.

### 2.3 Arquitectura de Aplicaciones

> *Define **qué aplicaciones** soportan las capacidades.* Artefactos: **Mapa de Portafolio de Aplicaciones** y **Application Capability Mapping**.

**a) Mapa de Portafolio de Aplicaciones** (*Application Portfolio Map*) — **vista del inventario completo** de aplicaciones, clasificadas por dominio/capacidad/unidad de negocio. Permite **identificar redundancias, obsolescencia y riesgos**.
- *Ejemplo (seguros):* se agrupa por capas → **Canales** (Portal Público, Portal Privado, App, Portal Brokers, IVR, WhatsApp), **Integración** (APIs de Cotización/Emisión/Endosos/Renovación/Siniestros/Pagos), **Core** (Core de Seguros, Core de Pagos, CRM, ERP), **Soporte/Transversal** (BPMN, Data lakehouse, Notificaciones, IoT, GenAI, ECM).

**b) Application Capability Mapping** (Mapeo de Aplicaciones con Capacidades) — cruza **qué aplicación soporta qué capacidad de negocio**.
- Truco visual del ejemplo: usa un **semáforo** para evaluar cada capacidad → 🔴 Rojo = gran parte es manual · 🟡 Ámbar = está regular · 🟢 Verde = está bien. Sirve para detectar dónde duele.

### 2.4 Arquitectura Tecnológica

> *Define **qué infraestructura** habilita las aplicaciones.* Artefactos: **Mapa de Infraestructura** y **Application Technology Mapping**.

**a) Mapa de Infraestructura** (*Technology Portfolio*) — muestra los entornos (on-premises, nubes, SaaS) y su stack.
- *Ejemplo (seguros):* **On-Premises (Lima)** con VMs, balanceadores, firewalls, Linux, Oracle, JBoss, Java; **AWS (EEUU)** con un stack serverless completo (CloudFront, S3, API Gateway, Lambda, DynamoDB, Step Functions, SNS/SQS/EventBridge, Glue/Athena/Redshift, Bedrock, IAM/Cognito, CloudWatch/X-Ray, RDS Aurora); **Azure (EEUU)** con Entra ID y VPN Gateway; conectados por **enlace dedicado** y **VPN**.

**b) Application Technology Mapping** (Mapeo de Aplicaciones con Tecnología) — cruza **qué aplicación corre sobre qué infraestructura/nube** (On-Prem vs AWS vs Azure vs SaaS).

---

## 3. El AS-IS (Situación Actual)

**AS-IS** = descripción estructurada de **cómo funciona HOY** la organización. Es la **"fotografía del presente"**. Incluye:
- Procesos actuales
- Capacidades existentes
- Sistemas y aplicaciones
- Infraestructura tecnológica
- Datos y flujos de información
- **Problemas y limitaciones** ← lo más valioso

**Cómo se representa el AS-IS en el ejemplo:** se toma **un Value Stream** (p. ej. "Emitir Póliza Digital") y, para cada etapa de la cadena, se documenta en filas paralelas:

| Fila | Qué contiene |
|---|---|
| **Pains** (puntos de dolor) | Ej.: "40% de evaluación de riesgo es manual, tarda hasta 2h"; "productos son texto estático, requiere redesplegar la web"; "20% de emisión tarda hasta 1h y a veces reprocesa". |
| **Roles** (internos) | Analista de Riesgo, Administrador Web, Analista TI… |
| **Aplicaciones** | Qué app interviene en cada etapa (Portal Público, Core de Seguros, CRM Venta…). |
| **Datos (Entidades)** | Qué entidades se tocan (Producto, Cliente, Cotización, Póliza, Pago…). |
| **Infraestructura** | Dónde corre (Cloud AWS, On-Premises Lima, Cloud SaaS…). |

> 📌 El AS-IS **integra las 4 capas** sobre una misma cadena de valor: por cada etapa ves negocio (roles/pains), datos (entidades), aplicaciones y tecnología juntos. Esa es la respuesta a la pregunta de cierre del docente: *"¿cómo el AS-IS une las 4 capas?"*

---

## 4. TOGAF y el método ADM

El **ADM (Architecture Development Method)** es el **método de trabajo de TOGAF** para diseñar y transformar la arquitectura. Es la **guía paso a paso** para pasar del *"cómo estamos hoy" (AS-IS)* al *"cómo queremos estar" (TO-BE)*.

Se dibuja como un ciclo iterativo. **Requirements Management** está en el centro porque alimenta a todas las fases.

```
        Preliminary
            │
            A. Architecture Vision
            │
   ┌────────┼─────────┐
   B. Business         │
   C. Information Sys.  │   (Requirements Management
   D. Technology       │        en el centro de todo)
   ┌────────┼─────────┘
            E. Opportunities & Solutions
            │
            F. Migration Planning
            │
            G. Implementation Governance
            │
            H. Architecture Change Management
            │
        (vuelve a iterar)
```

### Las fases del ADM, una por una

Cada fase responde una pregunta. Aquí está la pregunta + qué se hace + el ejemplo de la aseguradora.

#### Preliminary — *¿Cómo nos organizamos y bajo qué reglas hacemos AE?*
Define el **gobierno** y los **principios/lineamientos** de arquitectura.
- *Gobierno (ejemplo):* Comité de Arquitectura semanal (Gerente de Arquitectura, Arquitectos Empresariales, Arquitectos de Dominio, Jefe de Arq. de Solución) con acta; toda iniciativa se revisa ahí; se usa TOGAF/ADM; se documenta en Word (plantilla) en SharePoint; diagramas en draw.io.
- *Principios/Lineamientos (ejemplo), por capa:*
  - **Negocio:** Digital-first · Experiencia centrada en cliente · Cumplimiento regulatorio prioritario.
  - **Datos:** Single source of truth · Arquitectura Medallion para el Data lakehouse.
  - **Aplicaciones:** API-First · Evitar punto a punto · Preferir SaaS cuando sea viable.
  - **Tecnología:** Cloud-First · IaC (infraestructura como código) · Security by design.

> 📌 Estos **lineamientos** son los mismos que el enunciado del proyecto pide aplicar en el diseño TO-BE (Integración, Seguridad, Observabilidad, etc.).

#### A. Architecture Vision — *¿Qué queremos lograr y por qué?*
Se **alinea dirección y se justifica el cambio**. Aún **no** se diseñan apps ni tecnología. Contiene:
- **Situación** (ej.: "la aseguradora tarda 48h en emitir pólizas").
- **Drivers** (ej.: competencia insurtech, mala experiencia digital).
- **Objetivo** (ej.: emitir pólizas en < 5 minutos).
- **Alcance** (ej.: productos vehiculares, canal digital).
- **KPI** (ej.: tiempo de emisión, % de emisión automática).

#### Requirements Management — *¿Qué requisitos gestionamos y cómo aseguramos su trazabilidad?*
Es **transversal** a todas las fases.
- **Capturar** requisitos (de estrategia, regulación, stakeholders, auditoría, proyectos, cambios externos).
- **Clasificar:** Funcionales (RF) y No Funcionales (RNF).
- **Trazabilidad** en todas las fases del ADM.
- *Ejemplo:* se organiza en **Épicas** y dentro de cada una RF/RNF en formato historia de usuario ("Como… quiero… para…"). P.ej. Épica "Evaluación de Riesgo (95% automática)" → RF-2.1 "Evaluación automática de riesgo", RNF-2.1 "Trazabilidad y auditabilidad".

#### B. Business / C. Information Systems / D. Technology Architecture — *AS-IS y TO-BE de las 4 capas*
Aquí se diseñan las arquitecturas **objetivo (TO-BE)** de Negocio (B), Datos + Aplicaciones (C) y Tecnología (D), **comparándolas con el AS-IS**. Pasos numerados en el ejemplo:
1. Se parte del Architecture Vision (objetivo/drivers/alcance/KPI).
2. Se dibuja el **AS-IS** (las 4 capas sobre el value stream).
3. Se dibuja el **TO-BE** (las 4 capas objetivo sobre el mismo value stream).
4. Se identifican los **Gaps o brechas** (diferencias AS-IS → TO-BE) y de ahí salen RF/RNF.
- *Leyenda visual del TO-BE:* 🟢 Nuevo · 🟡 Modificar · 🔴 Eliminar (se marca cada app/componente según qué hay que hacer con él).
- *Ejemplo de gaps (seguros):* crear "APIs Productos Digitales", crear módulo de gestión de productos en el BackOffice, crear "API Motor de Riesgo (con Agente IA)" con auditoría, agregar Observabilidad (métricas/logs/trazas) a la API de emisión + dashboard tipo Grafana.

#### E. Opportunities and Solutions — *¿Qué iniciativas o proyectos debemos ejecutar?*
- **Consolidar los gaps** (de Negocio, Datos, Aplicaciones, Tecnología).
- **Agrupar gaps en iniciativas/proyectos.**
- Identificar **Arquitecturas de Transición** (estados intermedios cuando no puedes saltar directo del AS-IS al TO-BE).
  - *Ejemplo de transiciones:* AS-IS monolito on-prem → Transición 1: APIs sobre el monolito con BD centralizada → Transición 2: microservicios con su propia BD en Docker/Kubernetes on-prem → TO-BE: migración a nube pública.
- *Ejemplo de iniciativas (seguros):* "Módulo de Gestión de Productos Digitales", "Integración de Canales con APIs de Productos", "Motor de Riesgo con IA", "Observabilidad de Emisión de Pólizas", "Correcciones en el Core".

#### F. Migration Planning — *¿En qué orden y etapas lo implementamos?*
- Por cada iniciativa, **estimar tiempo y costo** según alcance.
- **Priorizar** por valor que generan al negocio.
- Elaborar un **roadmap/cronograma** considerando **dependencias** entre iniciativas.
- *Ejemplo:* tabla con Iniciativa · Costo aprox. (USD) · Tiempo (meses) · Gantt por mes (Mes 1…12). Costos del ejemplo: 60K, 50K, 100K, 80K, 80K, TBD… con duraciones de 2.5 a 4 meses.

> 📌 **Esta fase F es la bisagra con el resto del proyecto:** el enunciado pide tomar **≥3 iniciativas de la Migration Planning** y desarrollarlas como requerimientos y diseño de solución.

#### G. Implementation Governance — *¿Se está implementando conforme a la arquitectura definida?*
- Al aprobarse el presupuesto, se asigna un **Arquitecto de Solución** para el diseño detallado.
- El **Arquitecto Empresarial** participa a demanda (p.ej. reunión semanal) para garantizar que se respete la Transición/TO-BE.
- Al terminar, se verifica contra la "Fase A. Vision": ¿se logró el objetivo? ¿se cumplieron los KPIs? ¿se respetó la arquitectura? ¿se generó deuda técnica?

#### H. Architecture Change Management — *¿Cómo adaptamos la arquitectura cuando cambian las necesidades?*
- **Detectar cambios** del entorno (nueva regulación, nueva tecnología como IA generativa/agentes, nueva competencia, fusiones/adquisiciones, cambios estratégicos, nuevos requerimientos).
- **Clasificar el cambio:**
  - **Menor:** se ajusta dentro de la arquitectura actual.
  - **Significativo:** requiere nueva iteración en algunas fases del ADM.
  - **Disruptivo:** requiere redefinir la visión completa (volver a Fase A).

---

## 5. El TO-BE, los gaps y la planificación

- **TO-BE** = cómo **queremos estar** (situación futura objetivo). Es el espejo del AS-IS pero con la solución aplicada, sobre el **mismo value stream** y las **mismas 4 capas**.
- **Gap / brecha** = la **diferencia** entre el AS-IS y el TO-BE. Cada gap es algo que hay que **crear, modificar o eliminar**.
- Los gaps se **agrupan en iniciativas** (Fase E) y las iniciativas se **priorizan y agendan** en un roadmap con costos y dependencias (Fase F).

**Cadena conceptual completa (memorízala):**
```
Vision (objetivo) → AS-IS → TO-BE → Gaps → Requisitos (RF/RNF) → Iniciativas → Roadmap (costo/tiempo) → Ejecución → Verificación
```

---

## 6. El ejemplo guía completo (drawio "Empresa de Seguros")

El `.drawio` de **Sesión 2** es, literalmente, **la plantilla resuelta de TODO el Hito 1** del proyecto. Cada página del diagrama = un entregable. Úsalo como molde:

| # | Página del drawio | Capa / Fase ADM | Entregable equivalente del proyecto |
|---|---|---|---|
| 1 | Arq. Neg. - Business Model Canvas | Negocio | Business Model Canvas |
| 2 | Arq. Neg. - Mapa Capacidades | Negocio | Mapa de Capacidades |
| 3 | Arq. Neg. - Mapa Procesos | Negocio | (apoya Business Architecture) |
| 4 | Arq. Neg. - Cadenas Valor | Negocio | Cadenas de valor (AS-IS/TO-BE) |
| 5 | Arq. Dat. - Mapa Dominios Datos | Datos | (apoya Modelo Conceptual) |
| 6 | Arq. Dat. - Modelo Conceptual Datos | Datos | Modelo Conceptual de Datos |
| 7 | Arq. Apl. - Mapa Portafolio Aplicaciones | Aplicaciones | Mapa Portafolio de Aplicaciones |
| 8 | Arq. Apl. - Mapeo Aplicaciones Capacidades | Aplicaciones | Mapeo de Aplicaciones con capacidades |
| 9 | Arq. Tec. - Mapa de Infraestructura | Tecnología | Mapa de Infraestructura |
| 10 | Arq. Tec. - Mapeo Aplicaciones Tecnología | Tecnología | Mapeo de Aplicaciones con Tecnología |
| 11 | AS IS - Value Stream 1 | AS-IS | AS-IS con cadena de valor |
| 12 | ADM - Preliminary | ADM Preliminary | ADM - Preliminary |
| 13 | ADM - A. Architecture Vision | ADM A | ADM - A. Architecture Vision |
| 14 | ADM - Requirements Management | ADM Req. Mgmt | ADM - Requirements Management |
| 15 | ADM - Fase B, C y D (AS IS y TO BE) | ADM B/C/D | AS-IS y TO-BE de las 4 capas |
| 16 | ADM - E. Opportunities and Solutions | ADM E | ADM - E. Opportunities and Solutions |
| 17 | ADM - F. Migration Planning | ADM F | ADM - F. Migration Planning |

> El `.drawio` de **Sesión 1** es un subconjunto (páginas 1–11: las 4 capas + el primer AS-IS), sin las fases ADM. Es decir, **Sesión 2 contiene todo lo de Sesión 1 y además el ADM completo**. Para estudiar, usa Sesión 2.

**Caso del ejemplo:** "Empresa de Seguros (Vehicular + Hogar)". El value stream que desarrollan a fondo es **"Emitir Póliza Digital (autogestión por cliente)"**, con su AS-IS, TO-BE, gaps, requisitos, iniciativas y roadmap.

---

## 7. Cómo aplico esto a mi proyecto (RutaExpress)

Tu caso es **RutaExpress Fulfillment & Transporte** (operador logístico multinube: WMS on-prem, TMS Azure, app AWS/DynamoDB, optimizador GCP, portales SaaS). El trabajo es **replicar el ejemplo de la aseguradora, pero con RutaExpress**. Traducción directa:

| Concepto del ejemplo (seguros) | Equivalente en tu caso (RutaExpress) |
|---|---|
| Value stream "Emitir Póliza Digital" | Cadena de valor logística: **Recepción de órdenes → Preparación → Despacho → Entrega → Excepciones → Liquidación** (las 6 fases del caso) |
| Capacidades (Suscripción, Siniestros…) | Gestión de Pedidos, Gestión de Almacén/WMS, Gestión de Transporte/TMS, Última Milla, Devoluciones/Logística Inversa, Facturación/Liquidación, Atención al Cliente |
| Dominios de datos (Clientes, Pólizas…) | Orden, Inventario/SKU, Ruta/Manifiesto, Paquete, Evento de tracking, Evidencia, Devolución, Factura/Liquidación |
| Apps (Core Seguros, CRM…) | WMS (SQL Server), TMS (Azure), Orquestador (AKS), App Conductores (AWS/DynamoDB), Optimizador (GCP), Portal SaaS, CRM SaaS, ERP, API Management |
| Infra (On-prem + AWS + Azure) | On-premises + **Azure + AWS + GCP + SaaS** (es multinube real) |
| Drivers (insurtech, mala UX) | Marketplaces con red propia, presión de costos, SLA de entrega, clientes impacientes |
| Pains del AS-IS | WMS se degrada en campañas (6h, 240K pedidos en cola), pedidos duplicados por API, inventario desalineado, 17% de rutas corregidas a mano, 12.5% de entregas fallidas, conciliación de 23 días |
| Gaps → iniciativas | Backpressure/colas por SLA, deduplicación con clave idempotente, modelo canónico de estados, normalización de excepciones, observabilidad end-to-end, resiliencia en campañas |

**Tu hoja de ruta por hitos** (del enunciado — ver `transcripcion/enunciado-proyecto-integrador-final.md`):

1. **Hito 1 — Arquitectura Empresarial (lun 29-jun):** produce los 17 artefactos del ejemplo, pero para RutaExpress (BMC, mapas de las 4 capas, AS-IS/TO-BE, y las fases ADM Preliminary → F). **Aquí aplicas TODO lo de este documento.**
2. **Hito 2 — TO-BE Requerimientos (dom 05-jul):** toma ≥3 iniciativas de tu Migration Planning (Fase F) y escribe RF/RNF + criterios de aceptación.
3. **Hito 3 — TO-BE Diseño (dom 05-jul):** 2 alternativas de solución en C4 (niveles 1–3) con íconos AWS/Azure/GCP, lineamientos, patrones y ADRs + cuadro comparativo.
4. **Hito 4 — TO-BE Implementación (dom 12-jul):** MVP con ≥2 nubes y ≥3 patrones (Microservicios, DDD, EDA, CQRS, SAGA, Resiliencia), 100% IaC, costos por nube.

> ⚠️ **El más cercano es el Hito 1 (29-jun)** y es justamente el que cubren estas dos clases. Domina los 17 artefactos del `.drawio` de Sesión 2 y tendrás el molde exacto.

---

## 8. Glosario rápido

| Término | Qué es |
|---|---|
| **AE** | Arquitectura Empresarial: alinea estrategia, procesos, datos, apps y tecnología. |
| **TOGAF** | Estándar de arquitectura empresarial de The Open Group. |
| **ADM** | Architecture Development Method: las 8 fases de TOGAF para ir de AS-IS a TO-BE. |
| **AS-IS** | Situación actual ("foto del presente"), incluye procesos, apps, infra, datos y **problemas**. |
| **TO-BE** | Situación futura objetivo. |
| **Gap / brecha** | Diferencia entre AS-IS y TO-BE; se resuelve creando/modificando/eliminando. |
| **Capacidad** | QUÉ debe poder hacer el negocio (estable, independiente de cómo). |
| **Proceso** | CÓMO opera el negocio para ejecutar capacidades. |
| **Value Stream** | Secuencia end-to-end de cómo fluye el valor al cliente. |
| **BMC** | Business Model Canvas: modelo de negocio en 9 bloques. |
| **RF / RNF** | Requisito Funcional / No Funcional. |
| **Iniciativa** | Agrupación de gaps en un proyecto ejecutable. |
| **Arquitectura de Transición** | Estado intermedio entre AS-IS y TO-BE. |
| **C4 Model** | Notación de diagramas de software en 4 niveles (Contexto, Contenedores, Componentes, Código). |
| **ADR** | Architectural Decision Record: registro de una decisión de diseño. |
| **IaC** | Infraestructura como Código. |
| **Patrones (proyecto)** | Microservicios, DDD, EDA, CQRS, SAGA, Resiliencia. |
| **Principios de arquitectura** | Digital-first, Single source of truth, API-First, Cloud-First, Security by design, etc. |

---

## 9. Preguntas de repaso (las del docente)

**De Teoría 1 (capas + AS-IS):**
1. ¿Qué pasa si una empresa no tiene Arquitectura Empresarial?
2. ¿Para qué sirve la capa de Arquitectura de Negocio?
3. ¿Para qué sirve la capa de Arquitectura de Datos?
4. ¿Para qué sirve la capa de Arquitectura de Aplicaciones?
5. ¿Para qué sirve la capa de Arquitectura Tecnológica?
6. ¿Cómo une el AS-IS las 4 capas y para qué sirve?

**De Teoría 2 (ADM + TO-BE):**
1. Indica una fase del ADM y para qué sirve.
2. ¿Qué es un gap o brecha?
3. ¿Qué es una Situación Futura - TO-BE y para qué sirve?

> 💬 *Tip de estudio:* responde estas 9 preguntas usando RutaExpress como ejemplo en vez de la aseguradora. Si puedes hacerlo de memoria, dominas el Hito 1.

# Fase 5 — Las dos alternativas: A vs B

> **Meta de la fase:** entender por qué hay dos alternativas, en qué se diferencian de verdad
> (orquestación vs coreografía), y por qué se recomienda A — con puntajes, no "a ojo".
> Fuentes: `00_README.md`, `cuadro_comparativo_recomendacion.md`, ambos `03_nivel3_*`.

---

## 1. ¿Por qué DOS alternativas?

Un comité exige comparar **al menos dos caminos válidos** y justificar cuál eliges — sin
"espantapájaros" (una mala a propósito). El cuadro es explícito: *"Ninguna fue diseñada para
perder: cada una gana en criterios distintos."*

Regla que se siguió: ambas alternativas...
- Cubren el **100% de los 29 RF + 27 RNF**.
- Comparten la **misma huella multinube** (Azure/AWS/GCP).
- Se diferencian **solo en UNA cosa**: **cómo se coordinan los servicios.**

Así el comité compara **arquitecturas, no proveedores**.

---

## 2. La única diferencia real: Orquestación vs Coreografía

| | **A — Orquestada** | **B — Coreografiada** |
|---|---|---|
| Analogía | Orquesta con **director** | Grupo de baile **sin director** |
| Cómo funciona | El director (Saga) dice a cada uno cuándo actuar | Cada uno conoce su parte y **reacciona** a los eventos |
| ¿Quién coordina? | Un **orquestador central** (Saga en el OMS) | **Nadie**: cada servicio reacciona al evento anterior |
| Forma del diagrama N3 | **Hub** (flechas salen de la Saga) | **Cadena** (evento→servicio→evento) |

---

## 3. El mismo caso, dos formas (reservar y compensar)

**En A (orquestada) — hay un jefe:**
1. La Saga ordena "reserva" → reservado.
2. La Saga ordena "valoriza (ERP)" → falla.
3. La Saga ve el fallo y ordena "**libera**" (compensa).
- El jefe **ve todo y decide todo**: un solo lugar para entender qué pasó.

**En B (coreografiada) — cada uno reacciona solo:**
1. Llega `OrdenValidada` → el Manejador de Reserva reserva solo → publica `InventarioReservado`.
2. Si el ERP publica `ValorizaciónRechazada` → el Manejador de Compensación lo oye y **se libera a
   sí mismo**.
- **Nadie manda.** Cada servicio escucha eventos y actúa.

**Diferencia técnica (de los archivos):**
- **A:** fuente de verdad = **estado en Azure SQL** del OMS.
- **B:** fuente de verdad = **log de eventos** (Event Sourcing); el estado se reconstruye. Usa
  **CQRS completo** (proyecciones de lectura) + **Inbox** (idempotencia por evento).

---

## 4. Recomendación con puntajes reales

Evaluación ponderada (pesos según lo que el caso prioriza):

| Criterio (peso) | A | B |
|---|---|---|
| Cobertura RF/RNF (3) | 5 | 5 |
| **Factibilidad del MVP (3)** | **5** | 3 |
| Operabilidad y trazabilidad (2) | 5 | 3 |
| Desacoplamiento a largo plazo (2) | 3 | **5** |
| Resiliencia sin punto único (2) | 4 | 5 |
| Auditoría histórica (1) | 4 | 5 |
| **Curva del equipo (2)** | **4** | 2 |
| Costo de operación (1) | 4 | 3 |
| **TOTAL (máx. 80)** | **70** | **62** |

**Se recomienda A (orquestada).** Tres razones:
1. **El caso pide CONTROL, no autonomía:** el dolor fue la falta de "una sola verdad" y visibilidad
   (240k encolados sin que nadie supiera el estado). El orquestador da un punto donde toda orden se
   ve, se compensa y se explica.
2. **El MVP la favorece:** 2 nubes + 3 patrones + IaC en una semana; A lo demuestra con menos
   piezas. B exigiría event store, proyecciones y versionado de eventos desde el día 1.
3. **B no se descarta, se pospone:** A ya publica todos los eventos por Outbox; migrar dominios
   puntuales (tracking, analítica) a coreografía es evolución natural, sin rehacer la plataforma.

---

## 5. La honestidad que suma puntos

**B gana en varios criterios** (desacoplamiento, resiliencia, auditoría) — no se pintó mal. Y se
dice cuándo elegir B: *"si el comité prioriza la escala de equipos autónomos y la auditoría
regulatoria por encima de la velocidad del MVP, B es la mejor arquitectura."* Un arquitecto senior
no dice "mi opción es perfecta", sino "**para ESTE contexto**, gana A — y aquí está el puntaje".

---

## Cómo defenderlo ante el comité
1. *"Dos arquitecturas válidas, 100% de requisitos, misma huella; se diferencian solo en cómo
   coordinan: A con orquestador, B con coreografía."*
2. *"Las evalué con pesos según el caso: A saca 70, B saca 62."*
3. *"Recomiendo A porque el caso pide control y visibilidad —lo que faltó en Cyber Days— y el MVP
   de una semana la favorece."*
4. *"B no es mala: gana en desacoplamiento y resiliencia. La pospongo, no la descarto."*

---

## Archivos fuente de esta fase
- `diseno_solucion/00_README.md` — la bifurcación A/B y la disciplina C4
- `diseno_solucion/cuadro_comparativo_recomendacion.md` — evaluación ponderada + recomendación
- `alternativa_A_orquestada/03_nivel3_componentes_inventario.md` — el hub (director)
- `alternativa_B_coreografiada/03_nivel3_componentes_inventario.md` — la cadena (coreografía)
- `decisiones_diseño.md` — ADR-03 (por qué la bifurcación es orquestación vs coreografía)

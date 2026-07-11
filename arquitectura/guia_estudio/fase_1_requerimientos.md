# Fase 1 — El caso y los requerimientos (nivel general)

> **Meta de la fase:** entender *qué problema resuelve el proyecto* y *cómo se organizan los
> requerimientos*, sin memorizar los 29 RF uno por uno. Es la base para todo lo demás: cada
> diagrama y cada decisión de arquitectura existe para atacar algo de aquí.

---

## 1. El problema de negocio en una frase

> **RutaExpress no tiene una sola verdad.** Los datos del pedido y del inventario viven en
> *islas* que no se hablan bien (WMS on-premises, TMS en Azure, app en AWS, ERP on-premises), y
> las integraciones entre ellas son *spaghetti punto a punto*. Cuando llega un pico (Cyber Days),
> todo se cae.

El caso lo cuantifica en dinero — esa es tu munición ante el comité:

| Dolor real del caso | Cifra | La ataca… |
|---|---|---|
| WMS caído 6 h en Cyber Days → cola gigante | **240,000 pedidos**, USD **1.1M** en multas | INI-01 + INI-02 |
| Pedidos duplicados por reintentos mal hechos | **32,000** dobles | INI-01 |
| Entregas sin firma digital (evidencia offline perdida) | **1,200**, USD **2.4M** retenidos | INI-03 |
| Entregas fallidas, 34% por dirección/ausencia | **12.5%** (~8,500/día) | INI-03 |
| "Intento fallido" mostrado *después* de una entrega exitosa | eventos fuera de orden | INI-02 |

**Regla mental:** cada requisito existe para tapar uno de estos huecos. Si no sabes "¿para qué
sirve este RF?", la respuesta está en una de estas cifras.

---

## 2. Las 3 iniciativas — el corazón de todo

El proyecto se organiza en **3 iniciativas** (INI). Son **3 capas que se apoyan entre sí**:

```
   INI-03  ÚLTIMA MILLA        ← lo que ve el cliente (entregas, evidencias)
   ─────────────────────
   INI-01  ÓRDENES/INVENTARIO  ← el cerebro (la "única verdad" del pedido)
   ─────────────────────
   INI-02  BUS DE EVENTOS      ← el sistema nervioso (conecta todo, sin perder nada)
```

| | Qué hace | Metáfora | Riesgo del anexo | RF |
|---|---|---|---|---|
| **INI-01** · Gestión unificada de órdenes e inventario | Un **OMS centralizado** que gobierna el pedido: valida, deduplica, mantiene el estado único, coordina reserva (WMS) + valorización (ERP) y reconcilia conflictos | **El cerebro** | Riesgo 2 — Integridad | RF-01…11 |
| **INI-02** · Integración API-First y Event-Driven | Un **bus de eventos** con contratos versionados, backpressure, DLQ, prioridad por SLA, replay y orden lógico | **El sistema nervioso** | Riesgo 1 — Disponibilidad | RF-12…21 |
| **INI-03** · Última milla y excepciones | App de conductores **offline-first**, store-and-forward, taxonomía única de excepciones, evidencias con hash | **Las manos y los ojos** | Riesgo 3 — Operación | RF-22…29 |

**Frase clave de INI-02** (la que más impresiona a un comité): *"INI-02 no entrega una capacidad
de negocio visible por sí sola: hace **confiables** a INI-01 e INI-03. Sin el bus con backpressure
y DLQ, la deduplicación del OMS y el store-and-forward móvil no sobreviven a un pico."*

---

## 3. Los requerimientos — cómo leerlos sin ahogarte

Tienes **29 RF** (funcionales: "qué hace el sistema") + **27 RNF** (no funcionales: "qué tan bien
lo hace" — seguridad, rendimiento, disponibilidad). **No los memorices**; agrúpalos por *idea*:

**INI-01 (RF-01…11) → "una sola verdad, sin duplicados":**
- Identidad / anti-duplicados: RF-01 (ID interno único), RF-03 (deduplicar), RF-04 (idempotencia)
- La verdad única: RF-05 (estado canónico), RF-07 (eventos auditables)
- Coordinación crítica: RF-08 (reserva física WMS + valorización ERP → **esto es la Saga**), RF-09 (reconciliar conflictos)
- Convivencia: RF-11 (compatibilidad con el WMS viejo mientras migras)

**INI-02 (RF-12…21) → "ningún evento se pierde, se duplica o llega desordenado":**
- No perder: RF-16 (reintentos + **DLQ**), RF-14 (publicar eventos canónicos)
- No colapsar: RF-17 (**backpressure**), RF-18 (prioridad por SLA)
- No desordenar / no duplicar: RF-20 (secuencia por agregado), RF-19 (**replay** sin doble efecto)
- Gobierno: RF-12 (contratos versionados), RF-13 (rate limiting)

**INI-03 (RF-22…29) → "el conductor trabaja sin señal y nada se pierde":**
- Offline: RF-22 (operar offline), RF-23 (**store-and-forward**)
- Normalizar: RF-24 (taxonomía única de excepciones), RF-25 (acciones automáticas)
- Evidencias: RF-26 (referencia a la orden), RF-27 (preservar ante cambio de equipo → las 1,200 firmas perdidas)

> **RF vs RNF en una línea:** el RF dice *"el sistema deduplica pedidos"*; el RNF dice *"y lo hace
> con 99.9% de disponibilidad, cifrando en tránsito con TLS 1.2+"*. El RF es la función; el RNF es
> la calidad con la que se entrega.

---

## 4. Un detalle que da puntos: la consolidación 37 → 29

El set original tenía 37 RF; se depuró a **29** quitando redundancias y moviendo atributos de
calidad a los RNF. Eso es lo que hace un arquitecto senior y **es defendible**: *"No inflamos
requisitos; fusionamos los que comparten mecanismo (reintentos + DLQ → RF-16) y movimos los
atributos de calidad —cifrado, hash— a RNF, donde corresponden."*

---

## Cómo defenderlo ante el comité

Si te preguntan *"¿de qué trata tu proyecto?"*, respondes en 3 frases:

1. *"RutaExpress pierde dinero porque sus sistemas no comparten una sola verdad y sus
   integraciones son punto a punto; en Cyber Days eso costó USD 1.1M."*
2. *"Lo resolvemos con 3 iniciativas: un OMS que centraliza la orden (INI-01), un bus de eventos
   que hace confiable la comunicación (INI-02) y una última milla offline-first con evidencias
   íntegras (INI-03)."*
3. *"Cada una ataca uno de los 3 riesgos del anexo: integridad, disponibilidad y operación."*

---

## Archivos fuente de esta fase
- `requerimientos/README.md` — el set consolidado de los 29 RF con su valor de negocio
- `requerimientos/INI-01/00_contexto_INI-01.md` — problema AS-IS y TO-BE de órdenes/inventario
- `requerimientos/INI-02/00_contexto_INI-02.md` — el bus como "sistema nervioso"
- `requerimientos/INI-03/00_contexto_INI-03.md` — última milla offline-first
- Detalle por RF (HDU en Gherkin): `requerimientos/INI-0X/HU-*.md`
- RNF por iniciativa: `requerimientos/INI-0X/RNF-INI-0X.md`

# Fase 2 — C4 Nivel 1: Contexto

> **Meta de la fase:** entender qué es el Modelo C4 y qué muestra su nivel más alto (Contexto):
> el sistema como una caja, quién lo usa y con qué sistemas externos se integra. Sin tecnología,
> sin piezas internas. Aquí explicamos **cada componente: qué es y por qué está**.

---

## 1. Primero: ¿qué es el "Modelo C4"?

C4 (de Simon Brown) dibuja arquitectura con **4 niveles de zoom**, como un mapa: país → ciudad →
barrio → calle.

```
   Nivel 1  CONTEXTO      →  el país      (¿qué sistema es y con quién habla?)
   Nivel 2  CONTENEDORES  →  la ciudad    (¿de qué piezas desplegables se compone?)
   Nivel 3  COMPONENTES   →  el barrio    (¿qué hay DENTRO de una pieza?)
   Nivel 4  CÓDIGO        →  la calle     (clases; casi nunca se dibuja)
```

**Regla de oro:** cada nivel hace zoom sobre el anterior y agrega detalle. No se mezclan niveles.
El error más castigado es meter tecnología o cajas internas en el Nivel 1.

El Nivel 1 responde: **"¿Qué construimos y con quién/qué se relaciona?"** Tiene 3 tipos de piezas:
un **sistema central** (lo nuestro), **personas** (quién lo usa) y **sistemas externos** (con qué
se integra). Lo importante es entender **por qué cada pieza está ahí**.

### Convención de esta guía: NUEVO vs EXISTENTE
Para distinguir lo que **construimos** de lo que **ya existía** (AS-IS), marcamos cada pieza:
- 🟢 **[NUEVO]** — lo que estamos agregando/construyendo.
- ⚪ **[EXISTENTE]** — lo que ya existe y con lo que nos integramos (no lo reemplazamos).

En el Nivel 1 casi todo es EXISTENTE — solo la caja central es nueva. La distinción se vuelve muy
visible en el **Nivel 2**, donde agregamos piezas nuevas (OMS, Bus de eventos, API Gateway,
backend de última milla) junto a las existentes (WMS, ERP).

---

## 2. El sistema central (caja azul del medio)

### Plataforma Logística RutaExpress — 🟢 **[NUEVO]**
- **Qué es:** el sistema que construimos. Es la evolución del viejo "Orquestador de Pedidos"
  (APP-02) hacia una plataforma que gobierna todo el ciclo: orden → inventario → despacho →
  última milla → liquidación.
- **Por qué es UNA sola caja:** en Nivel 1 no importa cómo está hecha por dentro (OMS, bus, bases
  de datos). Eso es Nivel 2 y 3. Aquí es una **caja negra** = "la solución completa".
- **Por qué existe:** hoy no hay "una sola verdad" — los datos viven en islas. Esta plataforma las
  unifica.

---

## 3. Las personas (quién la usa — arriba, en azul) — ⚪ **[EXISTENTE]** (roles actuales)

Cada persona está porque **inicia o consume** algo de la plataforma. Si no interactúa con ella, no
va en el diagrama.

### Cliente B2B / Retail
- **Qué es:** las empresas/retailers que envían pedidos a RutaExpress.
- **Por qué está:** **origina la demanda** — crea órdenes y consulta trazabilidad. Sin él no hay
  pedidos que procesar.
- **Relación:** "Crea órdenes / consulta estado".

### Conductor
- **Qué es:** el repartidor de última milla, en la calle con su app móvil.
- **Por qué está:** actor de **INI-03**. Ejecuta la entrega física y registra evidencias (foto,
  firma) que sustentan la liquidación — las 1,200 firmas perdidas / USD 2.4M retenidos.
- **Relación:** "Entregas, tracking y evidencias" (a veces sin señal → offline).

### Operación RutaExpress
- **Qué es:** el equipo interno que vigila que todo fluya.
- **Por qué está:** necesita **visibilidad y control** — supervisa pedidos, inventario, rutas y
  SLA. Detecta y gestiona los problemas.
- **Relación:** "Monitoreo y gestión operativa".

### Finanzas
- **Qué es:** el área que cobra y concilia.
- **Por qué está:** el dinero **solo se libera** con evidencia de entrega. Concilia estados y
  evidencias para liquidar — conecta con los USD 2.4M retenidos.
- **Relación:** "Consulta soportes de liquidación".

> **Por qué exactamente estos 4:** cubren el ciclo de valor completo — quien **pide** (Cliente),
> quien **entrega** (Conductor), quien **controla** (Operación) y quien **cobra** (Finanzas).

---

## 4. Los sistemas externos (con qué se integra — en gris) — ⚪ **[EXISTENTE]**

Grises porque **ya existen y NO los construimos** — nos integramos. Cada uno está porque la
plataforma necesita algo de él o le envía algo. Todos son **[EXISTENTE]** (AS-IS).

### WMS — Almacenes (on-premises)
- **Qué es:** Warehouse Management System — controla el stock físico y el picking en almacenes.
- **Por qué está:** la plataforma debe **reservar inventario real** ahí antes de comprometer un
  pedido. Es el sistema que se cayó 6 h en Cyber Days.
- **Relación:** "Reserva y concilia inventario". Sigue **on-premises** → convivencia (RF-11).

### TMS — Transporte
- **Qué es:** Transportation Management System — planifica rutas y transporte.
- **Por qué está:** la plataforma le **sincroniza el despacho** y recibe el avance de rutas y
  entregas.
- **Relación:** "Sincroniza despacho, rutas y entregas".

### ERP Financiero (on-premises)
- **Qué es:** el sistema contable — inventario **valorizado** (en dinero) y facturación.
- **Por qué está:** reservar físico en el WMS no basta; hay que **valorizar** contablemente. Por
  eso RF-08 coordina WMS **y** ERP juntos (el corazón de la Saga).
- **Relación:** "Envía valorización y estados". También on-premises.

### Portal B2B / CRM
- **Qué es:** el canal donde el cliente ve el estado del envío y levanta reclamos.
- **Por qué está:** donde el cliente **percibe** la trazabilidad. El bug del caso —"intento
  fallido" tras entrega exitosa— se ve aquí; por eso importa el orden de eventos (INI-02).
- **Relación:** "Publica trazabilidad e incidencias".

### Canales legados
- **Qué es:** las formas viejas de mandar órdenes — CSV, Excel, archivos en S3.
- **Por qué está:** no todos los clientes migran de golpe a la API nueva. La plataforma debe
  **seguir aceptando** el canal viejo durante la transición.
- **Relación:** "Envía órdenes (transicional)" — la flecha apunta **hacia** la plataforma.

### Servicios de mapas y tráfico
- **Qué es:** proveedores externos (tipo Google Maps) de geocodificación, tráfico y ETA.
- **Por qué está:** la plataforma **consume** estos datos para rutas y tiempos estimados. No los
  construimos — los consultamos.
- **Relación:** "Consulta tráfico y ETA".

---

## 5. La dirección de las flechas (detalle que el profe mira)

Quién apunta a quién dice **quién inicia**:
- **Persona → plataforma:** el actor inicia (el cliente crea la orden).
- **Plataforma → sistema externo:** la plataforma pide algo (reserva al WMS, valorización al ERP).
- **Canal legado → plataforma:** va **al revés** que las otras externas, porque el legado *empuja*
  órdenes hacia adentro.

---

## 6. El color y la convivencia
Azul = nuestro / actores; gris = externo. Que WMS, TMS y ERP sigan **on-premises** dice al comité:
*"no hacemos big-bang; convivimos con los sistemas actuales durante la transición"* (RF-11).

---

## 7. Puente con la Fase 1: trazabilidad
Cada relación del contexto se mapea a una iniciativa — el diagrama nace de los requisitos:

| Relación en el contexto | Iniciativa |
|---|---|
| Crear órdenes / inventario / conciliación WMS·ERP | **INI-01** (RF-01…11) |
| Integración por API y eventos con TMS, portal, legados | **INI-02** (RF-12…21) |
| Entregas, tracking y evidencias del conductor | **INI-03** (RF-22…29) |

Los códigos del portafolio (WMS = APP-06/07, ERP = APP-25, etc.) van **fuera** del diagrama: un
"APP-25" dentro de una caja confunde a un comité.

---

## Cómo defenderlo ante el comité
1. *"Una caja: la plataforma que unifica orden → entrega → liquidación."*
2. *"Cuatro actores que cierran el ciclo de valor: quien pide, quien entrega, quien controla y
   quien cobra."*
3. *"Seis sistemas externos con los que convivo, no reemplazo — WMS y ERP siguen on-premises."*
4. *"Sin tecnología: el cómo es Nivel 2."*

---

## Archivos fuente de esta fase
- `diseno_solucion/alternativa_A_orquestada/01_nivel1_contexto.md` — diagrama Mermaid + lectura
- `diseno_solucion/diagramas_python/A_n1_contexto.png` — render con la librería `diagrams`
- La Alternativa B comparte el mismo Nivel 1: `alternativa_B_coreografiada/01_nivel1_contexto.md`
  (el contexto no cambia entre alternativas; lo que cambia es el interior — Nivel 2 y 3).

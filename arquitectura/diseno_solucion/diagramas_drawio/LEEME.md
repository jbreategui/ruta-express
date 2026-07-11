# Diagramas C4 en draw.io — RutaExpress

> **Nota:** el conjunto **completo y actualizado** de diagramas renderizados son los **10 PNG** de
> `../diagramas_python/` (N1/N2/N3 de A y B, con los 3 diagramas N3 por alternativa). Este `.drawio`
> cubre los **6 diagramas núcleo** (N1/N2/N3 de A y B, dominio inventario) como versión editable a
> mano; los N3 adicionales (bus/log de eventos y última milla) están solo en los PNG de Python.

**Archivo:** `RutaExpress_C4.drawio` — un solo documento con **6 pestañas** (una por nivel y alternativa):

| Pestaña | Contenido |
|---|---|
| A · Nivel 1 Contexto | Alternativa A — actores + sistema + externos (sin tecnología) |
| A · Nivel 2 Contenedores | Alternativa A — contenedores con **íconos de nube** agrupados por Azure / AWS / GCP / on-premises |
| A · Nivel 3 Reserva Inventario | Alternativa A — reserva de inventario **orquestada** (la Saga comanda) |
| B · Nivel 1 Contexto | Alternativa B — mismo alcance que A |
| B · Nivel 2 Contenedores | Alternativa B — coreografiada: log de eventos como fuente de verdad |
| B · Nivel 3 Componentes Inventario | Alternativa B — misma reserva de inventario, pero **coreografiada** (por eventos, sin comandante) |

## Cómo abrirlo
1. Ir a **https://app.diagrams.net** (o la app de escritorio de draw.io) → **Open Existing Diagram** → seleccionar `RutaExpress_C4.drawio`.
2. Las 6 pestañas aparecen abajo. Se navega entre ellas como en Excel.

## Sobre los íconos de nube (importante)
Cada contenedor usa el **stencil oficial** de su nube (Azure, AWS aws4, GCP gcp2). Si al abrir **algún ícono aparece en blanco**, es porque el nombre del stencil difiere en tu versión de draw.io. Se arregla en 10 segundos:
1. Habilitar las librerías: **More Shapes** (abajo a la izquierda) → marcar **Azure**, **AWS / AWS 17-19**, **GCP** → Apply.
2. Buscar el servicio en el panel de formas (ej. "API Management", "DynamoDB", "BigQuery") y **arrastrarlo** encima de la caja en blanco, o
3. Click derecho en la caja → **Edit Style** y corregir el nombre del `shape=`.

El **texto de cada caja siempre se ve** (nombre + tecnología), así que el diagrama es legible aunque un ícono no cargue.

## Exportar para el entregable
**File → Export as → PNG** (o PDF), pestaña por pestaña, con "Transparent Background" desmarcado y buen zoom. Esos PNG son los que van al informe del Hito.

## Fuente de verdad
Estos diagramas son la versión visual (con íconos) de los modelos en `../alternativa_A_orquestada/` y `../alternativa_B_coreografiada/`. Si cambias el diseño, actualiza primero esos `.md` (Mermaid) y luego reflédjalo aquí.

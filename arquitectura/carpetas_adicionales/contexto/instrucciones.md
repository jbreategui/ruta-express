> **Ubicación:** este documento y sus insumos viven en `utec/arquitectura/`. Todas las rutas de este spec son relativas a esa carpeta (p. ej. `INI-01_*`, `carpetas_adicionales/lineamientos`, `ARQUITECTURA_SOLUCION_TO_BE/`). La casuística y el enunciado están en `utec/transcripcion/` (`proyecto-rutaexpress.md` cubre Caso 6a + Anexo 6b; `enunciado-proyecto-integrador-final.md`).

## Rol / Persona

Actúa como un Arquitecto de Solución Multinube experto en logística, integración API-first, arquitectura event-driven, resiliencia operativa, seguridad, observabilidad e infraestructura como código.

## Contexto

RutaExpress Fulfillment & Transporte es un operador logístico que atiende comercio electrónico, retail, farmacéuticas y consumo masivo. Opera 14 centros de distribución, 2,700 vehículos propios y tercerizados, 68,000 entregas diarias promedio y picos de 180,000 entregas en campañas. Su arquitectura actual está fragmentada:

- WMS principal on premises sobre SQL Server.
- TMS en Azure.
- App de conductores en AWS con DynamoDB y evidencias en S3.
- Optimización de rutas y analítica en GCP.
- Portales SaaS para clientes.
- Integraciones punto a punto y canales legados por CSV/Excel/S3.

El objetivo del Hito 2 es elaborar requerimientos y diseño de arquitectura de solución TO BE para iniciativas priorizadas del ADM F. En esta carpeta se trabaja sobre las siguientes iniciativas:

- INI-01: Gestión unificada de órdenes e inventario end-to-end.
- INI-02: Integración API-First y Event-Driven.
- INI-03: Modernización de última milla y gestión de excepciones.

## Tarea / Objetivo

Diseñar una solución TO BE multinube para RutaExpress considerando:

- Todos los requerimientos de las carpetas `NEO_HITO2/INI-01_*`, `NEO_HITO2/INI-02_*` y `NEO_HITO2/INI-03_*`.
- Todos los lineamientos de la carpeta `carpetas_adicionales/lineamientos`.
- La volumetría del archivo `carpetas_adicionales/contexto/volumetria.md`.
- La casuística de `../transcripcion/proyecto-rutaexpress.md` (Caso 6a + Anexo 6b).
- Los entregables solicitados en `../transcripcion/enunciado-proyecto-integrador-final.md`.

Realiza estos pasos diferenciando fuentes existentes y entregables nuevos:

- Fuentes por iniciativa: requerimientos, criterios de aceptación e historias Gherkin ya existentes en cada `INI-XX_*`.
- Artefactos nuevos por iniciativa: microservicios específicos y diagramas de secuencia propios de cada `INI-XX_*`.
- Artefactos transversales de arquitectura de solución: dos alternativas TO BE, C4 Model, diagrama cloud, ADRs, cuadro comparativo y recomendación. Estos artefactos deben basarse en el conjunto completo de requerimientos y criterios de aceptación de `INI-01`, `INI-02` e `INI-03`.

Importante: no generes dos alternativas por cada iniciativa. Deben existir solo dos alternativas de solución TO BE para todo el alcance Hito 2, y cada alternativa debe cubrir integradamente las tres iniciativas.

## Fuentes obligatorias por iniciativa

Para cada una de estas carpetas:

- `NEO_HITO2/INI-01_*`
- `NEO_HITO2/INI-02_*`
- `NEO_HITO2/INI-03_*`

lee y usa como insumo los archivos ya existentes:

```text
INI-XX_*/
  01_Requerimientos_y_Criterios_Aceptacion.md
  historias_gherkin/
    HU-INIXX-RFYY_*.md
```

No generes, modifiques ni reescribas `01_Requerimientos_y_Criterios_Aceptacion.md` ni los archivos dentro de `historias_gherkin/`; estos documentos son la fuente funcional ya aprobada para el diseño.

## Estructura obligatoria de salida por iniciativa

Para cada carpeta `INI-XX_*`, genera únicamente los artefactos de diseño propios de esa iniciativa:

```text
INI-XX_*/
  diseño/
    alto_nivel/
      microservicios/
      diagramas_secuencia/
```

## Estructura obligatoria de salida transversal

Los artefactos de arquitectura de solución que integran las tres iniciativas deben generarse en:

```text
arquitectura/            (raíz de trabajo)
  INI-01_*/
  INI-02_*/
  INI-03_*/
  ARQUITECTURA_SOLUCION_TO_BE/
    alternativa_A.md
    alternativa_B.md
    diagrama_arquitectura.md
    cuadro_comparativo_recomendacion.md
    decisiones_diseño.md
```

La carpeta `ARQUITECTURA_SOLUCION_TO_BE/` debe estar al mismo nivel que `INI-01_*`, `INI-02_*` e `INI-03_*`.

Estos archivos no deben duplicarse dentro de cada carpeta `INI-XX_*` ni dentro de una carpeta global `diseño/alto_nivel`. Dentro de cada iniciativa solo se deben generar los artefactos propios de esa iniciativa y referencias de trazabilidad hacia la arquitectura transversal cuando corresponda.

## Entregables por iniciativa

1. Diseño de microservicios y dominios:
   - Crea `diseño/alto_nivel/microservicios/` dentro de cada carpeta `INI-XX_*`.
   - Diseña solo los microservicios necesarios para esa iniciativa, evitando duplicidad innecesaria.
   - Basa el diseño en `01_Requerimientos_y_Criterios_Aceptacion.md` y en los escenarios completos de `historias_gherkin/*.md`.
   - Por cada microservicio incluye: nombre, responsabilidades, funcionalidades, estructura de base de datos con sentencias SQL o modelo NoSQL cuando aplique.
   - Para cada funcionalidad incluye contrato de entrada/salida, algoritmo en pseudocódigo, features y escenarios cubiertos, y lineamientos cubiertos.
   - Genera un archivo Markdown por cada microservicio dentro de la carpeta de la iniciativa.

2. Diagramas de secuencia:
   - Crea `diseño/alto_nivel/diagramas_secuencia/` dentro de cada carpeta `INI-XX_*`.
   - Elabora diagramas de secuencia en Mermaid para la iniciativa correspondiente.
   - Basa los diagramas en los RF/RNF, criterios y escenarios Gherkin ya existentes en `01_Requerimientos_y_Criterios_Aceptacion.md` y `historias_gherkin/*.md`.
   - Los diagramas deben cubrir escenarios positivos y negativos relevantes de esa iniciativa:
     - INI-01: orden válida, pedido duplicado, reserva de inventario, inventario insuficiente, degradación de WMS y conciliación de inventario.
     - INI-02: contrato API, publicación de evento, validación de esquema, DLQ, backpressure, replay y evento fuera de orden.
     - INI-03: entrega offline, sincronización store-and-forward, evidencia corrupta, excepción de última milla, cambio de dispositivo y tracking retrasado.
   - Genera un archivo Markdown por cada diagrama o grupo de escenarios dentro de la carpeta de la iniciativa.

## Entregables transversales de arquitectura de solución

3. Alternativas de arquitectura de solución TO BE:
   - Usa como entrada principal todos los RF/RNF, historias y criterios de aceptación consolidados en:
     - `NEO_HITO2/INI-01_*/01_Requerimientos_y_Criterios_Aceptacion.md`
     - `NEO_HITO2/INI-02_*/01_Requerimientos_y_Criterios_Aceptacion.md`
     - `NEO_HITO2/INI-03_*/01_Requerimientos_y_Criterios_Aceptacion.md`
   - Usa además las historias detalladas y escenarios Gherkin completos desde:
     - `NEO_HITO2/INI-01_*/historias_gherkin/*.md`
     - `NEO_HITO2/INI-02_*/historias_gherkin/*.md`
     - `NEO_HITO2/INI-03_*/historias_gherkin/*.md`
   - No uses `requerimientos.md` ni `criterios_aceptacion_gherkin.md` como respaldo; la fuente vigente es el consolidado `01_Requerimientos_y_Criterios_Aceptacion.md` más los archivos independientes de `historias_gherkin/`.
   - Elabora exactamente dos alternativas de solución TO BE para el alcance completo de Hito 2:
     - Alternativa A: Azure como hub central de integración y gobierno, AWS para última milla/evidencias, GCP para analítica/rutas.
     - Alternativa B: AWS como hub principal de eventos y backend móvil, Azure para APIs/TMS/OMS, GCP para optimización y analítica.
   - Cada alternativa debe cubrir integradamente las capacidades de órdenes/OMS, inventario, integración API-first/event-driven, última milla, evidencias, tracking, excepciones, observabilidad, seguridad y gobierno multinube.
   - Para cada alternativa presenta un Diagrama de Arquitectura de Solución en C4 Model hasta nivel 3:
     - Nivel 1: Contexto.
     - Nivel 2: Contenedores.
     - Nivel 3: Componentes.
   - Los diagramas deben incluir íconos, etiquetas o leyenda de AWS, Azure y GCP. Si el formato Mermaid/C4 usado no soporta íconos gráficos reales, usa nombres oficiales de servicios y marcadores visuales claros por nube.
   - Aplica los lineamientos de arquitectura, integración, seguridad, observabilidad, escalabilidad y stack tecnológico definidos en `carpetas_adicionales/lineamientos`.
   - Aplica patrones de arquitectura: Microservicios, DDD, Event-Driven Architecture, Event Sourcing cuando aplique, Saga, Outbox/Inbox, CQRS cuando aporte valor, Circuit Breaker, Retry con Backoff + Jitter, Bulkhead, Backpressure, DLQ, idempotencia y store-and-forward.
   - Genera:
     - `NEO_HITO2/ARQUITECTURA_SOLUCION_TO_BE/alternativa_A.md`
     - `NEO_HITO2/ARQUITECTURA_SOLUCION_TO_BE/alternativa_B.md`

4. Cuadro comparativo y recomendación:
   - Genera `NEO_HITO2/ARQUITECTURA_SOLUCION_TO_BE/cuadro_comparativo_recomendacion.md`.
   - Compara ambas alternativas con criterios explícitos: alineamiento con Hito 1, cobertura de RF/RNF, complejidad, costo estimado relativo, seguridad, observabilidad, resiliencia, escalabilidad, impacto en aplicaciones existentes, riesgo de migración y facilidad de implementación.
   - Indica una alternativa recomendada. No dejes la decisión abierta al usuario.
   - Justifica la recomendación con base en el caso RutaExpress, el Hito 1, las tres iniciativas y los lineamientos.

5. Diagrama de arquitectura cloud transversal:
   - Genera `NEO_HITO2/ARQUITECTURA_SOLUCION_TO_BE/diagrama_arquitectura.md`.
   - El diagrama debe estar en Mermaid y representar la alternativa recomendada.
   - Debe incluir, cuando aplique: OMS centralizado / Orquestador de Pedidos (APP-02), WMS Cloud, Bus de Eventos Central (PLT-03), App de Conductores (APP-15), Almacenamiento Evidencias (S3) (APP-16), TMS (Transportation Management) (APP-11), ERP Financiero (On Premises) (APP-25), Portal B2B (Trazabilidad) (APP-18), Plataforma de Observabilidad Unificada (PLT-01), Plataforma de Identidad y Accesos (IAM) (PLT-02), Plataforma IaC (PLT-04), secretos, colas, DLQ, conectividad segura y servicios relevantes de Azure, AWS y GCP.

6. Decisiones de diseño:
   - Genera `NEO_HITO2/ARQUITECTURA_SOLUCION_TO_BE/decisiones_diseño.md`.
   - Incluye todas las decisiones de diseño tomadas como Architectural Decision Records (ADR).
   - Incluye ADR principales sobre: hub de eventos, estrategia OMS, idempotencia, patrón store-and-forward, DLQ, observabilidad, seguridad, datos de inventario, sincronización móvil, gobierno multinube, C4 seleccionado, integración con sistemas on premises, gestión de secretos, trazabilidad, costos y FinOps.
   - Para cada ADR indica: estado, contexto, decisión, alternativas consideradas, criterios usados, consecuencias, riesgos y trazabilidad hacia RF/RNF/INI.
   - Indica fecha, supuestos, criterios utilizados y relación con la alternativa recomendada.

## Requisitos de la respuesta

- Los entregables deben estar escritos en español.
- Mantén trazabilidad explícita entre requerimientos, lineamientos, escenarios y decisiones.
- Usa nombres oficiales de aplicaciones/plataformas del Hito 1 cuando existan: Orquestador de Pedidos (APP-02), TMS (Transportation Management) (APP-11), App de Conductores (APP-15), Almacenamiento Evidencias (S3) (APP-16), ERP Financiero (On Premises) (APP-25), Bus de Eventos Central (PLT-03), Plataforma de Observabilidad Unificada (PLT-01), Plataforma de Identidad y Accesos (IAM) (PLT-02) y Plataforma IaC (PLT-04).
- Si propones un componente nuevo, indica si es una evolución de una APP existente o un componente TO BE de solución.

## Elementos adicionales

- El diseño debe aplicar como mínimo patrones de arquitectura: Microservicios, Domain-Driven Design, Event-Driven Architecture,Event Sourcing , Saga Pattern,resiliencia, idempotencia y store-and-forward.
- Cuando sea útil, puede incluir CQRS, Saga, Outbox/Inbox, Circuit Breaker, Patrón Retry con Backoff + Jitter,Patrón Bulkhead ,Backpressure y Retry with DLQ.
- Si algún lineamiento relevante no está en la carpeta `lineamientos`, inclúyelo y explica el criterio en `decisiones_diseño.md`.
- Además, los servicios usados no deben ser muy caros, deben ser de nivel intermedio y deben poder implementarse con API MOCK para implementacion de MVP.
- recuerda que tampoco debes dar opciones para que yo elija tu debes elegir en base a todo el HITO1.

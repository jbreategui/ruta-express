# Proyecto — RutaExpress Fulfillment & Transporte

> Transcripción consolidada del material del proyecto (carpeta `proyecto/`).
> Fuentes:
> - `Caso 6a - Ruta Express_Logistica.pdf` (7 páginas)
> - `Caso 6b - Ruta Express_Logistica - Anexo.pdf` (4 páginas)
>
> Curso: Arquitectura Empresarial — UTEC. Documento de referencia para el diseño de la solución.

---

## Índice

- [Parte 1 — Caso 6a: RutaExpress Fulfillment & Transporte](#parte-1--caso-6a-rutaexpress-fulfillment--transporte)
  - [Sector económico](#sector-económico)
  - [Resumen ejecutivo](#resumen-ejecutivo)
  - [Contexto de la organización](#contexto-de-la-organización)
  - [Objetivos estratégicos](#objetivos-estratégicos)
  - [Cadena de valor](#cadena-de-valor)
    - [Fase 1: Recepción de órdenes](#fase-1-recepción-de-órdenes)
    - [Fase 2: Preparación de pedidos](#fase-2-preparación-de-pedidos)
    - [Fase 3: Despacho de pedidos](#fase-3-despacho-de-pedidos)
    - [Fase 4: Entrega del pedido](#fase-4-entrega-del-pedido)
    - [Fase 5: Gestión de excepciones](#fase-5-gestión-de-excepciones)
    - [Fase 6: Liquidación y devoluciones](#fase-6-liquidación-y-devoluciones)
- [Parte 2 — Caso 6b: Anexo de Riesgos Tecnológicos](#parte-2--caso-6b-anexo-de-riesgos-tecnológicos)
  - [Tabla de riesgos priorizados](#tabla-de-riesgos-priorizados)
  - [Riesgo 1 — Disponibilidad](#riesgo-1--disponibilidad-sistemas-logísticos-no-resilientes-a-picos-de-campaña)
  - [Riesgo 2 — Integridad](#riesgo-2--integridad-datos-logísticos-inconsistentes-y-conciliación-costosa)
  - [Riesgo 3 — Operación](#riesgo-3--operación-errores-humanos-y-datos-de-excepción-poco-normalizados)
- [Anexo de referencia rápida](#anexo-de-referencia-rápida-extraído-del-caso)

---

# Parte 1 — Caso 6a: RutaExpress Fulfillment & Transporte

**Empresa:** RutaExpress Fulfillment & Transporte (Ficticia)

## Sector económico

Logística y Transporte.

## Resumen ejecutivo

RutaExpress Fulfillment & Transporte es un operador logístico que atiende comercio electrónico, retail, farmacéuticas y consumo masivo. Administra **14 centros de distribución**, **2,700 vehículos** propios y tercerizados, **9,500 colaboradores**, **68,000 entregas diarias promedio** y picos de **180,000 durante campañas**. Sus servicios incluyen almacenamiento, preparación de pedidos, última milla, logística inversa, entregas refrigeradas y visibilidad para clientes empresariales.

La empresa compite en un sector marcado por promesas de entrega cada vez más cortas, presión de costos, clientes finales impacientes y grandes marketplaces con capacidades logísticas propias. RutaExpress creció rápido, integrando clientes por APIs, portales y archivos, pero su arquitectura quedó fragmentada: **WMS** (Warehouse Management System) on premises, **TMS** (Transportation Management System) en Azure, app de conductores en AWS, analítica de rutas en GCP, portales de clientes SaaS, bases de datos por almacén y múltiples integraciones punto a punto.

La organización busca en **tres años** convertirse en un operador logístico digital, predictivo y escalable. Necesita mejorar cumplimiento de promesa, reducir entregas fallidas, optimizar rutas, integrar inventario y ofrecer trazabilidad confiable. Los problemas actuales son severos: pedidos duplicados, inventario desalineado, congestión en centros de distribución, asignación manual de rutas, baja visibilidad de última milla, costos crecientes de combustible, reclamos masivos y baja resiliencia tecnológica en campañas.

El caso describe la cadena de valor desde la recepción de órdenes hasta la devolución y liquidación. En cada fase se detallan roles, aplicaciones, datos, infraestructura y problemas con volumetría. La narrativa ofrece un escenario integral para analizar arquitectura empresarial, solución multinube, APIs, eventos, dominios, resiliencia, observabilidad, seguridad, IaC y optimización de costos en logística moderna.

## Contexto de la organización

RutaExpress nació como una empresa de transporte urbano para tiendas por departamento. Su ventaja era conocer la ciudad, tener conductores confiables y entregar en zonas donde otros operadores fallaban. Con el auge del comercio electrónico, la empresa se transformó en un operador logístico integral. Abrió centros de distribución, integró marketplaces, adquirió una flota refrigerada y ofreció servicios de fulfillment para marcas que no querían construir su propia operación.

El modelo de negocio combina contratos por volumen, tarifas por almacenamiento, picking, packing, transporte, entrega, devolución, servicios premium y penalidades o bonificaciones por cumplimiento de SLA. Sus clientes son retailers, marketplaces, farmacias, supermercados, fabricantes y empresas de venta directa. Su propuesta de valor se basa en cobertura, velocidad, trazabilidad, flexibilidad operativa y capacidad de absorber picos.

La empresa procesa diariamente **68,000 entregas promedio**, **210,000 movimientos de inventario**, **44,000 eventos de tracking** y **18,000 contactos de atención**. En campañas como Cyber Days, Navidad o vuelta a clases, el volumen se triplica. La operación depende de almacenes, transportistas, conductores, planificadores, atención al cliente, tecnología, seguridad, clientes empresariales y destinatarios finales.

El sector logístico se volvió una carrera de promesas. Entrega al día siguiente dejó de ser diferencial; ahora se exige entrega el mismo día, ventanas horarias precisas, trazabilidad en vivo, devoluciones simples y atención inmediata. Los marketplaces más grandes construyen redes propias y presionan a operadores externos con tarifas bajas y penalidades. El costo de combustible, seguridad y mano de obra sube, mientras los clientes esperan pagar menos.

RutaExpress tiene sistemas fuertes en partes de la operación, pero **no una arquitectura integrada**. El WMS principal corre on premises en el centro de distribución central. El TMS está en Azure. La app de conductores corre en AWS y usa DynamoDB. La optimización de rutas se ejecuta en GCP con cargas batch. El portal de clientes es SaaS. Los clientes grandes envían órdenes por APIs, pero clientes medianos aún envían archivos CSV o Excel. Cada centro de distribución conserva bases locales para contingencia.

Los problemas se manifiestan en los momentos de mayor presión. En el último Cyber Days, el WMS se degradó durante **seis horas**. Se acumularon **240,000 pedidos en cola**. El TMS recibió órdenes incompletas, la app de conductores mostró rutas con paquetes faltantes y atención al cliente no pudo responder con certeza. Se entregó tarde el **19% de pedidos** de la campaña y se pagaron penalidades por **USD 1.1 millones**.

La aspiración del directorio es que RutaExpress deje de operar como una suma de centros y sistemas, y actúe como una **plataforma logística digital**. Para lograrlo debe integrar pedidos, inventario, almacén, transporte, tracking, devoluciones, facturación y analítica bajo una arquitectura resiliente, observable y segura.

## Objetivos estratégicos

1. **Incrementar el cumplimiento de promesa de entrega de 82% a 94%** en tres años, considerando fecha, ventana horaria, producto correcto y evidencia de entrega.
2. **Reducir entregas fallidas de 12.5% a 7%** mediante mejor validación de dirección, comunicación con destinatario, optimización de rutas y gestión de excepciones.
3. **Disminuir el tiempo de ciclo desde orden recibida hasta despacho de 9.5 horas a 4 horas** para pedidos fulfillment estándar.
4. **Alcanzar visibilidad de tracking confiable para el 98% de pedidos**, desde recepción hasta entrega, devolución o incidencia.
5. **Reducir costos de transporte por entrega en 15%** mediante consolidación, rutas dinámicas, mejor utilización de flota y control de combustible.
6. **Lograr disponibilidad de 99.9% para sistemas críticos en campañas**, incluyendo recepción de órdenes, WMS, TMS, app de conductores y tracking.
7. **Fortalecer la seguridad** de integraciones con clientes, datos personales de destinatarios, evidencia de entrega y operación móvil de conductores.

## Cadena de valor

### Fase 1: Recepción de órdenes

La cadena comienza cuando un cliente empresarial envía órdenes de venta a RutaExpress. Un marketplace transmite miles de pedidos por API; una cadena de farmacias envía órdenes cada quince minutos; una marca mediana carga un Excel en el portal. Para el cliente, la promesa ya fue hecha al comprador final. Para RutaExpress, cada orden es un compromiso que debe convertirse en inventario reservado, picking, transporte, entrega y evidencia.

Las APIs de clientes se exponen en **Azure API Management**. El portal SaaS permite carga manual. Algunos archivos llegan a un **bucket S3 en AWS** por integración histórica. El sistema de orquestación de pedidos corre en **Azure Kubernetes Service (AKS)**. El WMS on premises recibe las órdenes para preparación. Las bases de datos incluyen pedidos, clientes, destinatarios, SKUs, direcciones, SLA y ventanas.

- **Roles / participantes:** cliente empresarial, integración TI, mesa B2B, planeamiento, almacén y atención.
- **Entidades de datos:** orden, línea de pedido, SKU, destinatario, dirección, promesa, SLA, cliente, canal y prioridad.
- **Problema grave:** no todas las órdenes se validan igual. Direcciones incompletas, SKUs inexistentes o pedidos duplicados entran al flujo y explotan más adelante.

**Volumetría e incidente:** En un día regular se reciben **68,000 órdenes**; en campaña, **180,000**. El **6%** presenta algún defecto de datos. Aunque parece manejable, significa miles de excepciones diarias. En una campaña, un cliente envió dos veces el mismo lote de **32,000 pedidos** por reintento de API. La deduplicación falló porque el identificador externo cambió. Se separó inventario innecesariamente, se generaron rutas fantasma y se consumieron horas de operación corrigiendo el problema.

### Fase 2: Preparación de pedidos

Una vez aceptada la orden, el almacén debe preparar el pedido. En los centros de distribución, montacargas, bandas transportadoras, handhelds y operarios se mueven con ritmo intenso. El WMS indica ubicación, cantidad, lote, vencimiento y secuencia de picking. Para productos farmacéuticos se controla temperatura y cadena de custodia.

El WMS principal corre on premises sobre **SQL Server**. Algunos almacenes pequeños usan una versión local con sincronización cada hora. Los handhelds se conectan por Wi-Fi interno. El inventario maestro se replica hacia el portal de clientes y hacia el TMS. Los sensores de temperatura de cámaras refrigeradas envían datos a **AWS IoT Core**. El ERP financiero conserva inventario valorizado, pero no siempre actualizado en tiempo real.

- **Roles:** jefe de almacén, picker, verificador, control de calidad, supervisor de frío, inventario, seguridad y cliente.
- **Entidades de datos:** SKU, ubicación, lote, vencimiento, pedido, ola de picking, caja, contenedor, temperatura, inventario y excepción.
- **Dificultad:** el inventario físico se mueve más rápido que las sincronizaciones.

**Volumetría e incidente:** RutaExpress realiza **210,000 movimientos de inventario diarios**. El **2.8%** genera ajuste por diferencia, daño, vencimiento, ubicación incorrecta o conteo tardío. En productos de alta rotación, una diferencia pequeña provoca cancelaciones. Durante un pico, el WMS local de un almacén perdió conectividad con el centro durante **74 minutos**. Se siguió operando con contingencia, pero al sincronizar aparecieron **4,900 movimientos en conflicto** y se retrasaron **18,000 pedidos**.

### Fase 3: Despacho de pedidos

El pedido preparado pasa a consolidación y despacho. Las cajas se agrupan por zona, ruta, transportista, ventana horaria y tipo de servicio. Un pedido de farmacia refrigerada no puede viajar con cualquier carga; un producto de alto valor requiere validación de seguridad; una entrega express tiene prioridad. La operación parece un rompecabezas que cambia cada hora.

El **TMS alojado en Azure** recibe pedidos liberados por el WMS. La optimización de rutas se ejecuta en **GCP** con datos de tráfico, capacidad, restricciones y ubicación. Las rutas resultantes se envían a la **app de conductores en AWS**. Los transportistas tercerizados acceden por portal. Los manifiestos se imprimen localmente en cada centro.

- **Roles:** planner de transporte, supervisor de despacho, transportista, conductor, seguridad, cliente y atención.
- **Entidades de datos:** ruta, manifiesto, vehículo, conductor, capacidad, zona, paquete, ventana, prioridad y restricción.
- **Problema:** la asignación aún requiere intervención manual porque los datos de volumen, disponibilidad de flota y restricciones no siempre son confiables.

**Volumetría e incidente:** En un día normal salen **2,700 vehículos**. En campaña se suman **1,400 unidades tercerizadas**. El **17% de rutas se modifica manualmente** después de generarse. Cada modificación puede afectar promesa, costo y tracking. En una jornada de lluvias, el optimizador recibió datos de tráfico con retraso y generó rutas inviables. Los planners corrigieron a mano **380 rutas**. Aun así, **24,000 entregas** llegaron fuera de ventana.

### Fase 4: Entrega del pedido

La última milla es donde RutaExpress se encuentra con el destinatario. El conductor recibe ruta, paquetes, evidencias requeridas y contacto del cliente final. Debe navegar tráfico, edificios sin recepción, direcciones ambiguas, zonas inseguras, pagos contra entrega y cambios de última hora. Una entrega exitosa depende de tecnología, criterio y contexto urbano.

La app de conductores corre en **AWS**, usa **DynamoDB** para eventos y sincronización offline, y envía ubicación cada dos minutos. Los eventos de tracking se publican hacia el portal SaaS de clientes y hacia el centro de atención. El TMS actualiza estados en Azure. Las evidencias de entrega, fotos y firmas se almacenan en **S3**. Los pagos contra entrega se integran con una pasarela SaaS.

- **Roles:** conductor, destinatario, supervisor de ruta, atención al cliente, seguridad y cliente empresarial.
- **Entidades de datos:** paquete, evento, ubicación, evidencia, firma, foto, intento, motivo de fallo, pago y contacto.
- **Problema:** la operación móvil enfrenta conectividad variable, errores humanos y excepciones no estandarizadas.

**Volumetría e incidente:** Se generan **44,000 eventos de tracking diarios** en promedio, pero en campañas superan **130,000**. El **8% de eventos** llega con retraso mayor a 20 minutos. Los clientes llaman preguntando por paquetes que ya fueron entregados o que aún figuran en ruta. En zonas con mala señal, la app guarda eventos offline, pero si el conductor reinstala la aplicación o cambia de equipo se pierden evidencias. En un caso, **1,200 entregas** aparecieron sin firma digital y el cliente retuvo el pago del servicio hasta recibir conciliación manual.

### Fase 5: Gestión de excepciones

Cuando una entrega falla, empieza la gestión de excepciones. El destinatario no estaba, la dirección era incorrecta, el paquete se dañó, el edificio no permitió ingreso, faltó documentación o hubo riesgo de seguridad. Cada excepción requiere decisión: reintentar, devolver, llamar, cambiar dirección, cobrar penalidad o escalar al cliente.

Las excepciones se registran en la app de conductores, se visualizan en TMS y se notifican al portal de clientes. Atención usa un **CRM SaaS**. Los reintentos se planifican en el TMS. Las devoluciones vuelven al WMS. La información sobre motivos no está normalizada; cada conductor puede seleccionar categorías distintas o escribir texto libre.

- **Roles:** conductor, destinatario, atención, cliente empresarial, planner, almacén y finanzas.
- **Entidades de datos:** intento, excepción, motivo, reintento, devolución, autorización, costo y reclamo.
- **Problema:** la falta de datos consistentes impide aprender de las fallas.

**Volumetría e incidente:** La tasa de entrega fallida es **12.5%**. En volumen promedio equivale a **8,500 paquetes diarios**. Cada reintento cuesta entre **USD 1.20 y USD 2.80** según zona. El **34% de fallas** se relaciona con dirección o ausencia, problemas que podrían mitigarse antes de salir a ruta. Sin embargo, validación de dirección, comunicación previa y ajuste de ventanas no están integrados. La empresa gasta millones moviendo paquetes que no estaban listos para ser entregados.

### Fase 6: Liquidación y devoluciones

El ciclo cierra con liquidación, reportes y devoluciones. RutaExpress debe informar al cliente qué se entregó, qué falló, qué se devolvió, qué penalidades aplican y cuánto se factura. Los clientes grandes exigen reportes diarios y APIs de trazabilidad. Finanzas necesita facturar con evidencia. Operaciones necesita aprender de errores.

La facturación se realiza en el **ERP on premises**. Los eventos de entrega están en AWS. El TMS en Azure conserva rutas y costos. El WMS contiene devoluciones. El portal SaaS muestra reportes para clientes. Analítica en **GCP** consolida información semanalmente. Las notas de crédito por penalidades se calculan con hojas Excel cuando el contrato tiene reglas especiales.

- **Roles:** finanzas, operaciones, cliente empresarial, atención, legal, analítica y almacén.
- **Entidades de datos:** entrega, evidencia, SLA, penalidad, factura, devolución, reclamo, costo, liquidación y reporte.
- **Problema:** el cierre económico depende de conciliar datos entre nubes y sistemas locales.

**Volumetría e incidente:** Mensualmente se facturan más de **2 millones de servicios logísticos**. El **7%** queda observado por clientes debido a diferencias de estado, evidencia, tarifa o penalidad. Una cadena de retail retuvo **USD 2.4 millones** porque sus reportes internos indicaban menos entregas exitosas que RutaExpress. La conciliación tomó **23 días** e involucró archivos de AWS, reportes del TMS, capturas del portal y registros del WMS. La operación había cumplido mejor de lo que el sistema podía demostrar.

---

# Parte 2 — Caso 6b: Anexo de Riesgos Tecnológicos

**Caso asociado:** RutaExpress Fulfillment & Transporte

**Propósito del anexo:** Identifica los **3 principales riesgos tecnológicos** del caso.

## Tabla de riesgos priorizados

| Prioridad | Categoría | Riesgo tecnológico | Aplicaciones e infraestructura involucradas |
|:--:|---|---|---|
| 1 | **Disponibilidad** | Degradación de sistemas críticos en campañas, provocando colas de pedidos, rutas incompletas, tracking incierto y penalidades. | WMS SQL Server on premises, TMS Azure, AKS de orquestación, app AWS/DynamoDB, GCP optimizador, portal SaaS, redes de almacenes. |
| 2 | **Integridad** | Pedidos, inventario, rutas, eventos y evidencias inconsistentes entre WMS, TMS, app móvil, portales y ERP. | Azure API Management, S3, AKS, WMS, TMS, DynamoDB, ERP on premises, portal SaaS, GCP analítica. |
| 3 | **Operación** | Errores humanos y mala configuración en excepciones, datos de dirección, categorías de fallo y operación offline móvil. | App de conductores AWS, CRM SaaS, TMS, WMS, validadores de dirección, portales de clientes, integraciones con clientes. |

## Riesgo 1 — Disponibilidad: sistemas logísticos no resilientes a picos de campaña

**Descripción del riesgo**

RutaExpress triplica volumen en campañas. La recepción de órdenes, WMS, TMS, optimizador de rutas, app de conductores y tracking deben operar coordinados. Una degradación de WMS o integraciones genera acumulación de pedidos, rutas incompletas y reclamos masivos.

**Problemática técnica crítica**

El orquestador de pedidos en AKS recibe órdenes desde APIs en Azure API Management, portal SaaS y buckets S3 históricos. El WMS on premises confirma reserva y liberación de picking. Durante Cyber Days, el WMS se degrada por **bloqueo de tablas de inventario** y lentitud en consultas de ubicación. AKS sigue recibiendo órdenes, pero la cola hacia WMS crece sin control porque **no hay backpressure por cliente ni prioridad por SLA**.

El TMS en Azure recibe pedidos liberados incompletos y solicita rutas al optimizador en GCP. Algunas rutas se generan sin todos los paquetes porque la confirmación de picking llega tarde. La app de conductores en AWS sincroniza manifiestos parciales. Cuando el WMS se recupera, aparecen pedidos listos que ya no calzan con rutas cerradas. Atención al cliente ve estados contradictorios en el portal.

**Evidencias AS IS a relevar**

- Arquitectura de recepción, orquestación, WMS, TMS, optimizador, app móvil y tracking.
- Límites de capacidad por componente, colas, timeouts, reintentos y políticas de prioridad.
- Comportamiento ante degradación de WMS y desconexión de almacenes.
- RTO/RPO por proceso crítico en campaña.
- Monitoreo de flujo end to end: orden recibida, inventario reservado, picking, despacho, ruta y entrega.

## Riesgo 2 — Integridad: datos logísticos inconsistentes y conciliación costosa

**Descripción del riesgo**

El negocio se cobra y se defiende con evidencia: orden, inventario, ruta, evento, firma, foto, SLA, penalidad y factura. Si esos datos difieren entre WMS, TMS, app, portal y ERP, RutaExpress puede haber cumplido la operación, pero no demostrarlo, o facturar incorrectamente.

**Problemática técnica crítica**

Un cliente envía **32,000 pedidos por API**. Por reintento, cambia el identificador externo y falla la deduplicación. El orquestador crea órdenes duplicadas, el WMS reserva inventario dos veces y el TMS genera rutas fantasma. La app de conductores recibe algunos manifiestos, pero el portal SaaS muestra estados a partir de eventos de tracking y no de la reserva real.

En entrega, las evidencias se guardan en S3 y los eventos en DynamoDB. El TMS actualiza estado en Azure y el ERP factura desde un reporte mensual. Si un conductor opera offline y luego sincroniza eventos **fuera de orden**, el portal puede mostrar intento fallido después de entrega exitosa. El cliente observa la liquidación porque su sistema recibió otro estado.

**Evidencias AS IS a relevar**

- Claves únicas y reglas de duplicación por cliente, canal y orden.
- Modelo canónico de estados: recibido, validado, reservado, pickeado, despachado, en ruta, entregado, fallido, devuelto y liquidado.
- Flujos de evidencias: fotos, firmas, geolocalización, pagos contra entrega y custodia.
- Conciliaciones mensuales entre WMS, TMS, app, portal y ERP.
- Casos de mensajes fuera de orden, duplicados o perdidos.

## Riesgo 3 — Operación: errores humanos y datos de excepción poco normalizados

**Descripción del riesgo**

La última milla depende de conductores, destinatarios, planners y atención. Direcciones incompletas, excepciones mal categorizadas, evidencias perdidas y cambios manuales de ruta elevan entregas fallidas y costos. El riesgo tecnológico se manifiesta como operación difícil de controlar.

**Problemática técnica crítica**

La app de conductores permite seleccionar motivos de fallo y escribir texto libre. Algunos conductores usan "destinatario ausente", otros "no contesta", otros "dirección mala" para un mismo problema. El TMS recibe categorías distintas y el CRM SaaS abre reclamos con otra taxonomía. El algoritmo de rutas en GCP **no aprende correctamente** porque los motivos históricos no son comparables.

En zonas con mala señal, la app guarda eventos offline. Si el conductor reinstala la app o cambia de equipo antes de sincronizar, se pierden firmas y fotos. En entregas de alto valor o farmacéuticas, esa pérdida bloquea liquidación y puede abrir reclamos de custodia. Además, planners modifican rutas manualmente sin registrar causa estructurada, por lo que no se sabe si el problema fue clima, capacidad, tráfico, restricción de cliente o mala planificación.

**Evidencias AS IS a relevar**

- Taxonomía actual de excepciones en app, TMS, CRM y portal de clientes.
- Controles de obligatoriedad para firma, foto, geolocalización, hora, motivo y comentarios.
- Manejo offline de la app: cifrado local, reintentos, retención y recuperación ante reinstalación.
- Reglas de modificación manual de rutas y trazabilidad de aprobaciones.
- Análisis de causas de entrega fallida por dirección, ausencia, seguridad, daño, clima y cliente.

---

## Anexo de referencia rápida (extraído del caso)

### Mapa tecnológico AS-IS (dónde corre cada cosa)

| Sistema / componente | Ubicación / nube | Tecnología | Función |
|---|---|---|---|
| Recepción de APIs de clientes | Azure | Azure API Management | Exposición de APIs B2B |
| Orquestación de pedidos | Azure | Azure Kubernetes Service (AKS) | Orquestador de órdenes |
| WMS principal | On premises (CD central) | SQL Server | Gestión de almacén / picking |
| WMS almacenes pequeños | On premises (local) | Versión local, sync c/hora | Contingencia por almacén |
| TMS | Azure | — | Gestión de transporte / rutas |
| Optimización de rutas | GCP | Cargas batch | Optimizador de rutas |
| App de conductores | AWS | DynamoDB (eventos + offline) | Última milla / tracking |
| Sensores de frío | AWS | AWS IoT Core | Temperatura cámaras refrigeradas |
| Evidencias (fotos/firmas) | AWS | S3 | Almacenamiento de evidencia |
| Archivos históricos de órdenes | AWS | Bucket S3 | Integración histórica (CSV/Excel) |
| Portal de clientes | SaaS | — | Carga manual + reportes/tracking |
| CRM de atención | SaaS | — | Gestión de reclamos |
| Pasarela de pagos contra entrega | SaaS | — | Cobro en entrega |
| ERP financiero | On premises | — | Inventario valorizado / facturación |
| Analítica | GCP | Consolidación semanal | Reportes / analítica de rutas |

### Volumetría clave

| Métrica | Día regular | Campaña / pico |
|---|--:|--:|
| Entregas | 68,000 | 180,000 |
| Movimientos de inventario | 210,000 | — |
| Eventos de tracking | 44,000 | > 130,000 |
| Contactos de atención | 18,000 | — |
| Vehículos | 2,700 propios | + 1,400 tercerizados |
| Órdenes recibidas | 68,000 | 180,000 |

### Indicadores y metas (línea base → objetivo a 3 años)

| Indicador | Actual | Meta |
|---|--:|--:|
| Cumplimiento de promesa de entrega | 82% | 94% |
| Entregas fallidas | 12.5% | 7% |
| Tiempo de ciclo orden → despacho | 9.5 h | 4 h |
| Visibilidad de tracking confiable | — | 98% |
| Costo de transporte por entrega | — | −15% |
| Disponibilidad sistemas críticos (campaña) | — | 99.9% |

### Incidentes documentados (evidencia de dolor)

- **Cyber Days:** WMS degradado 6 h, 240,000 pedidos en cola, 19% de entregas tardías, penalidades por **USD 1.1 M**.
- **Duplicación de API:** lote de 32,000 pedidos enviado dos veces; falló deduplicación por cambio de ID externo → inventario doble reservado y rutas fantasma.
- **Pérdida de conectividad WMS local:** 74 min sin conexión → 4,900 movimientos en conflicto, 18,000 pedidos retrasados.
- **Optimizador con datos de tráfico tardíos (día de lluvias):** 380 rutas corregidas a mano, 24,000 entregas fuera de ventana.
- **Evidencias offline perdidas:** 1,200 entregas sin firma digital → pago retenido por el cliente.
- **Conciliación de facturación:** cadena de retail retuvo **USD 2.4 M**, conciliación de 23 días entre AWS, TMS, portal y WMS.

### Temas de arquitectura que el caso invita a analizar

Arquitectura empresarial · solución multinube (Azure + AWS + GCP + on premises + SaaS) · APIs · eventos · dominios · resiliencia · observabilidad · seguridad · IaC · optimización de costos.

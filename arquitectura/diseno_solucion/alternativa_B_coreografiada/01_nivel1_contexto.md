# Alternativa B (Coreografiada) · C4 Nivel 1 — Contexto

**Pregunta que responde:** ¿qué sistema construimos y con quién/qué se relaciona?
**Regla:** solo sistema en alcance + personas + sistemas externos. **Sin tecnología ni contenedores.**

> **Nota de diseño:** el contexto de la Alternativa B es **idéntico** al de la Alternativa A — y eso es correcto, no una copia descuidada: ambas alternativas resuelven el **mismo alcance** con los **mismos actores y sistemas externos**. Lo que cambia entre A y B es **cómo se coordinan los servicios por dentro** (orquestación vs coreografía), y eso recién es visible en los Niveles 2 y 3.

```mermaid
C4Context
    title Contexto — Plataforma Logística RutaExpress TO-BE (Alternativa B)

    Person(cliente, "Cliente B2B / Retail", "Envía órdenes y consulta trazabilidad")
    Person(conductor, "Conductor", "Ejecuta entregas y registra evidencias")
    Person(operacion, "Operación RutaExpress", "Supervisa pedidos, inventario, rutas y SLA")
    Person(finanzas, "Finanzas", "Concilia estados, evidencias y liquidación")

    System(plataforma, "Plataforma Logística RutaExpress TO-BE", "Coordina orden, inventario, despacho, última milla, evidencias y trazabilidad end-to-end")

    System_Ext(wms, "WMS — Almacenes", "Gestión de almacén y picking — on-premises")
    System_Ext(tms, "TMS — Transporte", "Gestión de transporte y rutas")
    System_Ext(erp, "ERP Financiero", "Inventario valorizado y facturación — on-premises")
    System_Ext(portal, "Portal B2B / CRM", "Trazabilidad al cliente y gestión de reclamos")
    System_Ext(legado, "Canales legados", "Órdenes por CSV / Excel / S3")
    System_Ext(mapas, "Servicios de mapas y tráfico", "Geocodificación, tráfico y ETA")

    Rel(cliente, plataforma, "Crea órdenes / consulta estado", "HTTPS / REST")
    Rel(conductor, plataforma, "Entregas, tracking y evidencias", "App móvil / HTTPS")
    Rel(operacion, plataforma, "Monitoreo y gestión operativa", "HTTPS")
    Rel(finanzas, plataforma, "Consulta soportes de liquidación", "HTTPS")

    Rel(plataforma, wms, "Reserva y concilia inventario", "API / eventos")
    Rel(plataforma, tms, "Sincroniza despacho, rutas y entregas", "API / eventos")
    Rel(plataforma, erp, "Envía valorización y estados", "API / eventos")
    Rel(plataforma, portal, "Publica trazabilidad e incidencias", "API / eventos")
    Rel(legado, plataforma, "Envía órdenes (transicional)", "Archivos / API")
    Rel(plataforma, mapas, "Consulta tráfico y ETA", "HTTPS / REST")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="2")
```

## Trazabilidad a iniciativas
| Relación del contexto | Iniciativa |
|---|---|
| Crear órdenes / inventario / conciliación WMS·ERP | INI-01 (RF-01…11) |
| Integración por API y eventos con TMS, portal, legados | INI-02 (RF-12…21) |
| Entregas, tracking y evidencias del conductor | INI-03 (RF-22…29) |

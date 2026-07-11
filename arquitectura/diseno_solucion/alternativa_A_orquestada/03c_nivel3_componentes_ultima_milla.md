# Alternativa A (Orquestada) · C4 Nivel 3 — Componentes del Backend de Última Milla

**Pregunta:** ¿cómo funciona por dentro el **Backend de Última Milla** (AWS), que da soporte a la operación offline, la sincronización confiable y las evidencias?
**Regla:** se abre **UN** contenedor (Última Milla). Es el corazón de INI-03 (RF-22…29). Los demás aparecen como cajas externas de borde.

```mermaid
C4Component
    title Componentes — Backend de Última Milla (AWS ECS/Lambda)

    Container_Ext(app, "App de Conductores", "móvil", "opera offline")
    Container_Ext(bus, "Bus de Eventos", "Event Hubs + Service Bus", "eventos de despacho")
    ContainerDb_Ext(ddb, "Sincronización móvil", "DynamoDB", "estado offline")
    ContainerDb_Ext(s3, "Evidencias", "S3 + KMS", "fotos/firmas + hash")
    Container_Ext(portal, "Portal / CRM", "APP-18/20", "excepciones")

    Container_Boundary(um, "Backend de Última Milla") {
        Component(apimov, "API Móvil", "REST", "Entrada del conductor con OAuth2+PKCE")
        Component(inbox, "Consumidor de Eventos (Inbox)", "Servicio", "Deduplica por eventId (RF-16/23)")
        Component(sync, "Sincronización Store-and-Forward", "Servicio", "Confirma y reintenta lo capturado offline (RF-22, RF-23)")
        Component(evid, "Gestor de Evidencias", "Servicio", "Vincula a la orden y calcula hash (RF-26, RF-27)")
        Component(tax, "Taxonomía de Excepciones", "Servicio", "Código canónico + motivo obligatorio (RF-24)")
        Component(acc, "Motor de Acciones Automáticas", "Servicio", "Reintento, devolución, escalamiento (RF-25)")
        Component(prev, "Acciones Preventivas por Riesgo", "Servicio", "Dirección/ausencia antes del intento (RF-29)")
        Component(track, "Registro de Tracking", "Servicio", "Ubicación cada 2 min, deduplicada (RF-28)")
    }

    Rel(app, apimov, "Entregas, tracking, evidencias", "HTTPS · OAuth2+PKCE")
    Rel(apimov, sync, "Envía lo capturado offline", "in-proc")
    Rel(bus, inbox, "Eventos de despacho/ruta", "AMQP → HTTPS bridge")
    Rel(sync, evid, "Persiste evidencia", "in-proc")
    Rel(evid, s3, "Almacena cifrada + hash", "HTTPS · KMS")
    Rel(sync, ddb, "Estado de sincronización", "SDK")
    Rel(apimov, tax, "Clasifica la excepción", "in-proc")
    Rel(tax, acc, "Dispara acción", "in-proc")
    Rel(tax, portal, "Propaga estado/excepción", "AMQP/HTTPS")
    Rel(inbox, prev, "Evalúa riesgo antes del intento", "in-proc")
    Rel(apimov, track, "Ubicación periódica", "in-proc")
    Rel(track, ddb, "Persiste tracking", "SDK")

    UpdateElementStyle(portal, $bgColor="grey")
```

## Componentes (responsabilidad · RF)
| Componente | Responsabilidad | RF |
|---|---|---|
| API Móvil | Entrada del conductor (OAuth2+PKCE) | RF-22 |
| Consumidor de Eventos (Inbox) | Dedup por eventId (idempotencia) | RF-16, RF-23 |
| Sincronización Store-and-Forward | Confirmación backend + reintento de lo offline | RF-22, RF-23 |
| Gestor de Evidencias | Vínculo a la orden + hash de integridad | RF-26, RF-27 |
| Taxonomía de Excepciones | Código canónico + motivo obligatorio | RF-24 |
| Motor de Acciones Automáticas | Reintento / devolución / escalamiento | RF-25 |
| Acciones Preventivas por Riesgo | Prevención por dirección/ausencia | RF-29 |
| Registro de Tracking | Ubicación cada 2 min, deduplicada | RF-28 |

**Lo que demuestra:** la última milla resiliente — el conductor opera sin señal, nada se pierde al sincronizar (store-and-forward), y las evidencias con hash sostienen la liquidación (los USD 2.4M retenidos del caso).

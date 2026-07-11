# Proyecto Integrador Final — RutaExpress Fulfillment & Transporte
**Grupo 6** · Programa de Arquitectura de Soluciones Multinube (UTEC)

Repositorio del proyecto integrador: de la Arquitectura Empresarial (TOGAF/ADM) al diseño e implementación de una solución logística **multinube**. Elaborado con apoyo de IA (Claude — Anthropic).

---

## El caso
**RutaExpress** es un operador logístico multinube (Azure + AWS + GCP + on-premises) con problemas de **disponibilidad, integridad y operación**: en Cyber Days el WMS se cayó 6 h (240k pedidos en cola, USD 1.1M en penalidades), 32k órdenes duplicadas, 12.5% de entregas fallidas y USD 2.4M retenidos por evidencias faltantes.
📄 Caso y enunciado (transcripción): [`transcripcion/`](transcripcion/)

## Mapa de los 4 hitos
| Hito | Qué pide | Dónde está | Estado |
|---|---|---|---|
| **1 · Arquitectura Empresarial** | BMC, modelo de datos, portafolio de apps, ADM/TOGAF | Base de las 3 iniciativas | ✅ |
| **2 · TO-BE Requerimientos** | ≥3 iniciativas, RF, RNF, criterios de aceptación | [`arquitectura/requerimientos/`](arquitectura/requerimientos/) | ✅ 29 RF + 27 RNF |
| **3 · TO-BE Diseño de Solución** | 2 alternativas, C4 niveles 1-2-3, ADR, comparativo | [`arquitectura/diseno_solucion/`](arquitectura/diseno_solucion/) | ✅ |
| **4 · TO-BE Implementación** | MVP, ≥2 nubes, ≥3 patrones, 100% IaC, costos | [`arquitectura/implementacion_mvp/`](arquitectura/implementacion_mvp/) | ✅ código + IaC listos |

## Navegación
- **Portada detallada con enlaces:** [`arquitectura/README.md`](arquitectura/README.md)
- **Requerimientos** (INI-01/02/03, 29 RF + 27 RNF): [`arquitectura/requerimientos/`](arquitectura/requerimientos/)
- **Diseño** (Alternativa A orquestada / B coreografiada, C4, ADR, comparativo, diagramas): [`arquitectura/diseno_solucion/`](arquitectura/diseno_solucion/)
- **Implementación MVP** (Azure + AWS, Terraform, apps, tests): [`arquitectura/implementacion_mvp/`](arquitectura/implementacion_mvp/) · Informe: [`INFORME_HITO4.md`](arquitectura/implementacion_mvp/INFORME_HITO4.md)

## Notas de alcance (honestidad)
- El **MVP** implementa un **subconjunto** de los 29 RF (la ruta crítica del caso); el resto queda cubierto en el diseño.
- El MVP está **listo para desplegar pero no desplegado**: el `terraform apply` es el paso final.
- **Multinube no forzado:** se usan las nubes que el caso justifica (Azure núcleo, AWS última milla, GCP analítica); el MVP usa 2 (Azure + AWS).

## Estructura del repositorio
```
├── README.md                 ← este archivo (portada)
├── transcripcion/            ← caso y enunciado (transcripción en Markdown)
├── analisis-clase/           ← notas de estudio
└── arquitectura/             ← ENTREGABLE de los 4 hitos
    ├── requerimientos/       (Hito 2)
    ├── diseno_solucion/      (Hito 3: 2 alternativas C4, ADR, comparativo, diagramas)
    ├── implementacion_mvp/   (Hito 4: apps, terraform, informe, costos, guía de evidencia)
    └── carpetas_adicionales/ (lineamientos y contexto)
```

*Grupo 6 RutaExpress · Programa de Arquitectura de Soluciones Multinube — UTEC · con apoyo de IA (Claude — Anthropic)*

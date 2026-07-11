# Proyecto Integrador Final — RutaExpress Fulfillment & Transporte
**Grupo 6** · Programa de Arquitectura de Soluciones Multinube (UTEC)

Portada e índice general de los entregables.

---

## El caso
**RutaExpress** es un operador logístico multinube (Azure + AWS + GCP + on-premises) con dolores de **disponibilidad, integridad y operación**: en Cyber Days el WMS se cayó 6 h (240k pedidos en cola, USD 1.1M en penalidades), 32k órdenes duplicadas, conflictos de inventario, 12.5% de entregas fallidas y USD 2.4M retenidos por evidencias faltantes.
📄 Caso y anexo: [`../transcripcion/proyecto-rutaexpress.md`](../transcripcion/proyecto-rutaexpress.md) · Enunciado: [`../transcripcion/enunciado-proyecto-integrador-final.md`](../transcripcion/enunciado-proyecto-integrador-final.md)

## Mapa de los 4 hitos
| Hito | Qué pide | Dónde está | Estado |
|---|---|---|---|
| **1 · Arquitectura Empresarial** | BMC, modelo de datos, portafolio de apps, ADM/TOGAF (AS-IS/TO-BE, Migration Planning) | Entrega original (TOGAF/ADM) | ✅ Base de las 3 iniciativas |
| **2 · TO-BE Requerimientos** | ≥3 iniciativas, RF, RNF, criterios de aceptación | [`requerimientos/`](requerimientos/) | ✅ 29 RF + 27 RNF, validados |
| **3 · TO-BE Diseño de Solución** | 2 alternativas, C4 nivel 1-2-3, íconos cloud, lineamientos, patrones, ADR, comparativo | [`diseno_solucion/`](diseno_solucion/) | ✅ Completo |
| **4 · TO-BE Implementación** | MVP, ≥2 nubes, ≥3 patrones, 100% IaC, costos, API mock | [`implementacion_mvp/`](implementacion_mvp/) | ✅ Código + IaC listos para desplegar |

---

## Hito 2 — Requerimientos → [`requerimientos/`](requerimientos/)
3 iniciativas del Migration Planning, con sus HDU en Gherkin (formato del profe) y RNF medibles.
- **INI-01** Gestión unificada de órdenes e inventario (RF-01…11 · RNF-01…09)
- **INI-02** Integración API-First y Event-Driven (RF-12…21 · RNF-10…18)
- **INI-03** Última milla y gestión de excepciones (RF-22…29 · RNF-19…27)
- Índice: [`requerimientos/README.md`](requerimientos/README.md) · **29 RF + 27 RNF**, códigos únicos, doblemente validados.

## Hito 3 — Diseño de Solución → [`diseno_solucion/`](diseno_solucion/)
Dos alternativas **genuinamente distintas**, ambas multinube best-of-breed:
- **Alternativa A — Orquestada** (Saga central): [`diseno_solucion/alternativa_A_orquestada/`](diseno_solucion/alternativa_A_orquestada/) — C4 niveles 1, 2, 3.
- **Alternativa B — Coreografiada** (Event Sourcing + CQRS): [`diseno_solucion/alternativa_B_coreografiada/`](diseno_solucion/alternativa_B_coreografiada/) — C4 niveles 1, 2, 3.
- **ADRs**: [`decisiones_diseño.md`](diseno_solucion/decisiones_diseño.md) (9 decisiones) · **Comparativo + recomendación (A)**: [`cuadro_comparativo_recomendacion.md`](diseno_solucion/cuadro_comparativo_recomendacion.md)
- **Lineamientos aplicados** (54/54): [`lineamientos_aplicados.md`](diseno_solucion/lineamientos_aplicados.md)
- **Vista dinámica** (secuencia): [`diagramas_secuencia/`](diseno_solucion/diagramas_secuencia/) · **Diagramas con íconos cloud**: [`diagramas_python/`](diseno_solucion/diagramas_python/) (PNG) y [`diagramas_drawio/`](diseno_solucion/diagramas_drawio/) (editable)
- **Anexo despliegue/red/seguridad**: [`anexos/`](diseno_solucion/anexos/)
- Índice del diseño: [`diseno_solucion/00_README.md`](diseno_solucion/00_README.md)

## Hito 4 — Implementación → [`implementacion_mvp/`](implementacion_mvp/)
MVP de la Alternativa A, **Azure + AWS**, 100% Terraform, con 5 patrones (Microservicios, EDA, Saga, CQRS, Resiliencia).
- **Informe consolidado**: [`INFORME_HITO4.md`](implementacion_mvp/INFORME_HITO4.md)
- **Análisis y diseño**: [`00_analisis_mvp.md`](implementacion_mvp/00_analisis_mvp.md) · [`01_diseno_detallado.md`](implementacion_mvp/01_diseno_detallado.md) · [`02_afinamiento_tecnico.md`](implementacion_mvp/02_afinamiento_tecnico.md)
- **Runbook de despliegue**: [`README.md`](implementacion_mvp/README.md) · **Guía de evidencia**: [`guia_evidencia.md`](implementacion_mvp/guia_evidencia.md) · **Costos por nube**: [`costos_estimados.md`](implementacion_mvp/costos_estimados.md) · **Gaps de despliegue**: [`03_gaps_para_despliegue.md`](implementacion_mvp/03_gaps_para_despliegue.md)
- **Código**: `apps/` (OMS + mocks + Lambda + bridge) · **IaC**: `terraform/` (12 módulos + policy OPA/Rego)
- Verificación: **20 tests** pasan · `terraform validate` Success · revisión crítica adversarial aplicada.

---

## Orden de lectura sugerido
1. El **caso** (`../transcripcion/`) → 2. **Requerimientos** (`requerimientos/README.md`) → 3. **Diseño** (`diseno_solucion/00_README.md` → alternativas → comparativo/ADR) → 4. **Implementación** (`implementacion_mvp/INFORME_HITO4.md`).

## Notas de alcance (honestidad)
- El **MVP** implementa un **subconjunto** de los 29 RF (la ruta crítica); el resto queda cubierto en el diseño. RF-09 (reconciliación) es solo de diseño.
- El MVP está **listo para desplegar pero no desplegado**: el `terraform apply` es el paso final, con credenciales de estudiante (Azure for Students + AWS propia), sin gasto real.
- **Multinube no forzado**: se usan las nubes que el caso ya justifica (Azure núcleo, AWS última milla, GCP analítica); el MVP usa 2 (Azure + AWS) como pide el mínimo.

*Grupo 6 RutaExpress · Programa de Arquitectura de Soluciones Multinube — UTEC*

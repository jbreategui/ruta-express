# Guía de estudio — RutaExpress (Grupo 6)

Ruta para **entender** el proyecto de lo general a lo concreto: primero el problema y los
requerimientos, luego el modelo C4 (Nivel 1 → 2 → 3) con la alternativa recomendada (A), después la
Alternativa B nivel por nivel, y al final la vista dinámica y el despliegue. No es para memorizar
cada requisito, sino para entender la lógica y poder defenderla ante el comité.

## Orden de estudio

| # | Archivo | Qué vas a entender |
|---|---|---|
| 01 | [01_requerimientos.md](01_requerimientos.md) | El caso, las 3 iniciativas y el panorama de los 29 RF + 27 RNF |
| 02 | [02_c4_nivel1_contexto.md](02_c4_nivel1_contexto.md) | C4 Nivel 1: el sistema, las personas y los sistemas externos (compartido A y B) |
| 03 | [03_c4_nivel2_contenedores_A.md](03_c4_nivel2_contenedores_A.md) | C4 Nivel 2 (Alternativa A): contenedores, tecnología, protocolos, huella multinube |
| 04 | [04_c4_nivel3_componentes_A.md](04_c4_nivel3_componentes_A.md) | C4 Nivel 3 (Alternativa A): interior de un contenedor, sin íconos cloud, con seguridad |
| 05 | [05_alternativas_A_vs_B.md](05_alternativas_A_vs_B.md) | Las dos alternativas: orquestada (A) vs coreografiada (B) y por qué se recomienda A |
| 06 | [06_c4_nivel1_contexto_B.md](06_c4_nivel1_contexto_B.md) | C4 Nivel 1 (Alternativa B): idéntico a A y por qué |
| 07 | [07_c4_nivel2_contenedores_B.md](07_c4_nivel2_contenedores_B.md) | C4 Nivel 2 (Alternativa B): servicios autónomos, Log = fuente de verdad |
| 08 | [08_c4_nivel3_componentes_B.md](08_c4_nivel3_componentes_B.md) | C4 Nivel 3 (Alternativa B): los 3 diagramas (inventario, log, última milla) |
| 09 | [09_vista_dinamica_y_decisiones.md](09_vista_dinamica_y_decisiones.md) | Diagramas de secuencia (comportamiento) + los 9 ADRs: cómo defender cada decisión |
| 10 | [10_despliegue.md](10_despliegue.md) | Cómo el diseño se vuelve infraestructura: despliegue, red, seguridad, DR y Terraform |

## Cómo usar cada ficha
Cada ficha tiene la misma estructura: **el concepto → cómo está aplicado en nuestros archivos → la
frase de defensa** (cómo lo dirías ante el profe). Al final de cada una, un bloque "Cómo defenderlo
ante el comité" y los archivos fuente.

## Estructura
- **01** — fundamentos (requerimientos).
- **02–04** — el modelo C4 explicado con la alternativa recomendada (A). El Nivel 1 (02) es
  compartido por ambas alternativas.
- **05** — comparación A vs B y recomendación.
- **06–08** — la Alternativa B nivel por nivel (para el contraste completo).
- **09–10** — vista dinámica (secuencia + decisiones) y despliegue.

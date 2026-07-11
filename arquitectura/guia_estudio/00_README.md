# Guía de estudio — RutaExpress (Grupo 6)

Ruta para **entender** el proyecto de lo general a lo concreto: primero el problema y los
requerimientos, luego los diagramas C4 (Nivel 1 → 2 → 3), después las dos alternativas de
arquitectura, y al final cómo se despliega. No es para memorizar cada requisito, sino para
entender la lógica y poder defenderla ante el comité.

## Fases

| Fase | Archivo | Qué vas a entender |
|---|---|---|
| **1** | [fase_1_requerimientos.md](fase_1_requerimientos.md) | El caso, las 3 iniciativas y el panorama de los 29 RF + 27 RNF |
| **2** | [fase_2_c4_nivel1_contexto.md](fase_2_c4_nivel1_contexto.md) | C4 Nivel 1: el sistema, las personas y los sistemas externos |
| **3** | [fase_3_c4_nivel2_contenedores.md](fase_3_c4_nivel2_contenedores.md) | C4 Nivel 2: contenedores desplegables, tecnología, protocolos y huella multinube |
| **4** | [fase_4_c4_nivel3_componentes.md](fase_4_c4_nivel3_componentes.md) | C4 Nivel 3: el interior de un contenedor, sin íconos cloud, con seguridad |
| **5** | [fase_5_alternativas_A_B.md](fase_5_alternativas_A_B.md) | Las dos alternativas: Saga orquestada (A) vs coreografiada (B) y por qué se recomienda A |
| **5b** | [fase_5b_alternativa_B_diagramas.md](fase_5b_alternativa_B_diagramas.md) | La Alternativa B por niveles (resumen/contraste con A) |
| **5b·N1** | [fase_5b_nivel1_contexto_B.md](fase_5b_nivel1_contexto_B.md) | Nivel 1 de B (idéntico a A y por qué) |
| **5b·N2** | [fase_5b_nivel2_contenedores_B.md](fase_5b_nivel2_contenedores_B.md) | Nivel 2 de B (servicios autónomos, Log = fuente de verdad) |
| **5b·N3** | [fase_5b_nivel3_componentes_B.md](fase_5b_nivel3_componentes_B.md) | Nivel 3 de B (los 3 diagramas: inventario, log, última milla) |
| **6** | [fase_6_secuencia_decisiones.md](fase_6_secuencia_decisiones.md) | Vista dinámica (secuencia) + ADRs: cómo defender cada decisión |
| **7** | [fase_7_despliegue.md](fase_7_despliegue.md) | Cómo el diseño se vuelve infraestructura: Terraform, red y seguridad |

## Cómo usar cada ficha
Cada fase tiene la misma estructura: **el concepto → cómo está aplicado en nuestros archivos →
la frase de defensa** (cómo lo dirías ante el profe). Al final de cada una, un bloque
"Cómo defenderlo ante el comité".

# Diagramas C4 con íconos de nube — generados con Python (diagrams)

Estos PNG son la **versión visual con íconos oficiales** de AWS/Azure/GCP, generados con la librería `diagrams` (la que enseña el profe en el Taller 3). Fuente de verdad: los modelos Mermaid en `../alternativa_A_orquestada/` y `../alternativa_B_coreografiada/`.

## Archivos generados (10 PNG)
| PNG | Nivel |
|---|---|
| `A_n1_contexto.png` | A · Contexto |
| `A_n2_contenedores.png` | A · Contenedores (íconos de nube) |
| `A_n3_reserva_inventario.png` | A · N3 Reserva de Inventario — INI-01 (orquestada) |
| `A_n3b_bus_eventos.png` | A · N3 Bus de Eventos — INI-02 |
| `A_n3c_ultima_milla.png` | A · N3 Backend de Última Milla — INI-03 |
| `B_n1_contexto.png` | B · Contexto |
| `B_n2_contenedores.png` | B · Contenedores (íconos de nube) |
| `B_n3_inventario.png` | B · N3 Servicio de Inventario — INI-01 (coreografiado) |
| `B_n3b_log_eventos.png` | B · N3 Log de Eventos — INI-02 (Event Sourcing) |
| `B_n3c_ultima_milla.png` | B · N3 Backend de Última Milla — INI-03 |

## Cómo regenerarlos
```
python generar_diagramas.py
```
Requiere `diagrams` (ya instalado) y graphviz (ya instalado en `C:\Program Files\Graphviz\bin`; el script lo agrega al PATH solo).

## Íconos verificados (corrige los errores del GIT)
Cada clase de ícono fue comprobada contra la librería instalada antes de usarla. En contraste con la versión anterior del GIT:
- **DynamoDB** usa el ícono real de DynamoDB (antes era PostgreSQL).
- **BigQuery** usa el ícono real de BigQuery (antes era Storage Accounts).
- **S3** el balde verde, **Event Hubs** el ícono de integración, **Vertex AI** el suyo.

Mapa nombre → clase usada: API Management→`azure.integration.APIManagement` · OMS/servicios→`azure.compute.AKS` · Azure SQL→`azure.database.SQLDatabases` · Bus/Log→`azure.analytics.EventHubs` · IAM→`azure.identity.ActiveDirectory` · Obs→`azure.devops.ApplicationInsights` · Backend móvil→`aws.compute.ECS` · DynamoDB→`aws.database.Dynamodb` · Evidencias→`aws.storage.S3` · GCP→`gcp.analytics.Pubsub/Dataflow/Bigquery` + `gcp.ml.AIPlatform` · WMS/ERP/TMS/Portal→`onprem.compute.Server`.

## Nota sobre el layout
El posicionamiento lo calcula graphviz automáticamente. Si quieres mover una caja concreta o acortar una flecha larga, se ajusta editando el orden de los nodos/clusters en `generar_diagramas.py` y volviendo a ejecutar. Para exponer al comité, exporta o inserta el PNG directamente en el informe.

# -*- coding: utf-8 -*-
"""
Genera los 6 diagramas C4 (Nivel 1-2-3 x Alternativa A y B) con iconos de nube.
Fuente de verdad: los modelos Mermaid en ../alternativa_A_orquestada y ../alternativa_B_coreografiada.
Librería: diagrams (mingrammer) + graphviz. Todos los iconos fueron verificados contra la librería instalada.
Ejecutar:  python generar_diagramas.py   ->  genera 6 PNG en esta carpeta.
"""
import os
# graphviz está instalado pero no en el PATH: lo agregamos aquí para que el script sea autónomo
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

from diagrams import Diagram, Cluster, Edge
from diagrams.azure.integration import APIManagement, ServiceBus
from diagrams.azure.compute import AKS
from diagrams.azure.database import SQLDatabases
from diagrams.azure.analytics import EventHubs
from diagrams.azure.security import KeyVaults
from diagrams.azure.identity import ActiveDirectory
from diagrams.azure.devops import ApplicationInsights
from diagrams.aws.compute import ECS
from diagrams.aws.database import Dynamodb
from diagrams.aws.storage import S3
from diagrams.gcp.analytics import Pubsub, Dataflow, Bigquery
from diagrams.gcp.ml import AIPlatform
from diagrams.onprem.client import Users, User
from diagrams.onprem.compute import Server
from diagrams.generic.device import Mobile
from diagrams.generic.blank import Blank
from diagrams.programming.flowchart import Action

# --- estilo común para que queden ordenados y bonitos ---
GRAPH = {
    "fontsize": "24", "fontname": "Segoe UI", "bgcolor": "white",
    "pad": "0.7", "nodesep": "0.55", "ranksep": "1.1", "splines": "spline",
    "labelloc": "t",
}
EDGE = {"fontsize": "10", "fontname": "Segoe UI", "color": "#4A4A4A"}
NODE = {"fontsize": "11", "fontname": "Segoe UI"}
DASH = {"style": "dashed", "color": "#8A8A8A", "fontsize": "9"}
CMD  = {"color": "#0B4884", "penwidth": "2", "fontsize": "10"}   # comando (orquestación)
COMP = {"color": "#B85450", "penwidth": "2", "style": "dashed", "fontsize": "10"}  # compensación


def a_n1():
    with Diagram("Alternativa A - Nivel 1: Contexto", filename="A_n1_contexto", show=False,
                 direction="TB", graph_attr=GRAPH, edge_attr=EDGE, node_attr=NODE, outformat="png"):
        cli = Users("Cliente B2B / Retail")
        con = Mobile("Conductor")
        ope = User("Operacion RutaExpress")
        fin = User("Finanzas")
        with Cluster("Plataforma Logistica RutaExpress TO-BE"):
            plat = Blank("Coordina orden, inventario, despacho,\nultima milla, evidencias y trazabilidad")
        wms = Server("WMS - Almacenes\n(on-premises)")
        tms = Server("TMS - Transporte")
        erp = Server("ERP Financiero\n(on-premises)")
        por = Server("Portal B2B / CRM")
        leg = Server("Canales legados")
        mapa = Server("Mapas y trafico")

        cli >> Edge(label="Crea ordenes / estado") >> plat
        con >> Edge(label="Entregas y evidencias") >> plat
        ope >> Edge(label="Monitoreo") >> plat
        fin >> Edge(label="Liquidacion") >> plat
        plat >> Edge(label="Reserva / concilia") >> wms
        plat >> Edge(label="Despacho y rutas") >> tms
        plat >> Edge(label="Valorizacion") >> erp
        plat >> Edge(label="Trazabilidad") >> por
        leg >> Edge(label="Ordenes (transicional)") >> plat
        plat >> Edge(label="Trafico y ETA") >> mapa


def a_n2():
    with Diagram("Alternativa A (Orquestada) - Nivel 2: Contenedores", filename="A_n2_contenedores", show=False,
                 direction="LR", graph_attr=GRAPH, edge_attr=EDGE, node_attr=NODE, outformat="png"):
        cli = Users("Cliente B2B")
        ope = User("Operacion / Finanzas")
        con = Mobile("Conductor")

        with Cluster("Azure - Nucleo e Integracion"):
            apim = APIManagement("API Management\n(Gateway OpenAPI, OAuth2)")
            oms = AKS("OMS - Orquestador\n(AKS): orden, inventario, Saga")
            sql = SQLDatabases("Azure SQL\n(orden, inventario, outbox)")
            bus = EventHubs("Bus de Eventos\n(Event Hubs + Service Bus)")
            with Cluster("Transversal"):
                iam = ActiveDirectory("Entra ID + Key Vault")
                obs = ApplicationInsights("Azure Monitor")

        with Cluster("AWS - Ultima Milla"):
            mob = ECS("Backend Ultima Milla\n(ECS/Lambda)")
            ddb = Dynamodb("DynamoDB\n(sync offline)")
            s3 = S3("S3 + KMS\n(evidencias)")

        with Cluster("GCP - Analitica"):
            gpub = Pubsub("Pub/Sub")
            gflow = Dataflow("Dataflow")
            gbq = Bigquery("BigQuery")
            gai = AIPlatform("Vertex AI")

        with Cluster("On-premises"):
            wms = Server("WMS - Almacenes")
            erp = Server("ERP Financiero")

        tms = Server("TMS - Transporte")
        por = Server("Portal B2B / CRM")
        mapa = Server("Mapas y trafico")

        cli >> Edge(label="HTTPS/REST OAuth2") >> apim
        ope >> Edge(label="Consultas HTTPS") >> apim
        con >> Edge(label="HTTPS OAuth2+PKCE") >> mob
        apim >> Edge(label="Comandos/consultas") >> oms
        oms >> Edge(label="TDS private endpoint") >> sql
        oms >> Edge(label="Publica eventos (Outbox) AMQP") >> bus
        oms >> Edge(label="Reserva fisica VPN") >> wms
        oms >> Edge(label="Valorizacion VPN") >> erp
        oms >> Edge(label="OIDC / Key Vault", **DASH) >> iam
        oms >> Edge(label="OTLP", **DASH) >> obs
        bus >> Edge(label="Eventos despacho AMQP->HTTPS") >> mob
        mob >> Edge(label="sync") >> ddb
        mob >> Edge(label="evidencias KMS") >> s3
        mob >> Edge(label="tracking HTTPS->AMQP") >> bus
        bus >> Edge(label="Stream AMQP->Pub/Sub") >> gpub
        gpub >> gflow >> gbq
        gflow >> gai
        bus >> Edge(label="Estados y excepciones") >> por
        bus >> Edge(label="Despacho y entregas") >> tms
        gbq >> Edge(label="Rutas optimizadas") >> tms
        gai >> Edge(label="Trafico y ETA") >> mapa


def a_n3():
    with Diagram("Alternativa A (Orquestada) - Nivel 3: Reserva de Inventario (dentro del OMS)",
                 filename="A_n3_reserva_inventario", show=False, direction="LR",
                 graph_attr=GRAPH, edge_attr=EDGE, node_attr=NODE, outformat="png"):
        bus = EventHubs("Bus de Eventos")
        sql = SQLDatabases("Azure SQL\n(estado + outbox)")
        wms = Server("WMS - Almacenes\n(on-premises)")
        erp = Server("ERP Financiero\n(on-premises)")
        iam = ActiveDirectory("Entra ID + Key Vault")

        with Cluster("OMS - Reserva de Inventario (orquestada por la Saga)"):
            saga = Action("Orquestador de Reserva\n(Saga): COMANDA y compensa")
            res = Action("Manejador de Reserva\n(reserva atomica)")
            inv = Action("Inventario y Reservas")
            aud = Action("Registro Auditable")
            recon = Action("Reconciliador")
            adapt = Action("Adaptador WMS\n(Circuit Breaker + Retry)")
            outbox = Action("Publicador Outbox")

        saga >> Edge(label="Reservar (comando)", **CMD) >> res
        saga >> Edge(label="Liberar - COMPENSACION", **COMP) >> res
        saga >> Edge(label="Reserva fisica (comando)", **CMD) >> adapt
        saga >> Edge(label="Valorizacion (comando) VPN", **CMD) >> erp
        res >> Edge(label="verifica y reserva") >> inv
        res >> Edge(label="registra") >> aud
        adapt >> Edge(label="reserva/consulta VPN") >> wms
        inv >> Edge(label="deriva conflictos") >> recon
        res >> Edge(label="persiste + outbox TDS") >> sql
        outbox >> Edge(label="lee outbox") >> sql
        outbox >> Edge(label="publica resultado AMQP") >> bus
        outbox >> Edge(label="secretos", **DASH) >> iam


def b_n1():
    with Diagram("Alternativa B - Nivel 1: Contexto", filename="B_n1_contexto", show=False,
                 direction="TB", graph_attr=GRAPH, edge_attr=EDGE, node_attr=NODE, outformat="png"):
        cli = Users("Cliente B2B / Retail")
        con = Mobile("Conductor")
        ope = User("Operacion RutaExpress")
        fin = User("Finanzas")
        with Cluster("Plataforma Logistica RutaExpress TO-BE"):
            plat = Blank("Mismo alcance y actores que A;\nla diferencia aparece en N2/N3")
        wms = Server("WMS - Almacenes")
        tms = Server("TMS - Transporte")
        erp = Server("ERP Financiero")
        por = Server("Portal B2B / CRM")
        leg = Server("Canales legados")
        mapa = Server("Mapas y trafico")

        cli >> Edge(label="Crea ordenes / estado") >> plat
        con >> Edge(label="Entregas y evidencias") >> plat
        ope >> Edge(label="Monitoreo") >> plat
        fin >> Edge(label="Liquidacion") >> plat
        plat >> Edge(label="Reserva / concilia") >> wms
        plat >> Edge(label="Despacho y rutas") >> tms
        plat >> Edge(label="Valorizacion") >> erp
        plat >> Edge(label="Trazabilidad") >> por
        leg >> Edge(label="Ordenes (transicional)") >> plat
        plat >> Edge(label="Trafico y ETA") >> mapa


def b_n2():
    with Diagram("Alternativa B (Coreografiada) - Nivel 2: Contenedores", filename="B_n2_contenedores", show=False,
                 direction="LR", graph_attr=GRAPH, edge_attr=EDGE, node_attr=NODE, outformat="png"):
        cli = Users("Cliente B2B")
        ope = User("Operacion / Finanzas")
        con = Mobile("Conductor")

        with Cluster("Azure - Nucleo e Integracion (coreografiado)"):
            apim = APIManagement("API Management\n(Gateway)")
            oms = AKS("Servicio de Ordenes\n(AKS): valida y publica eventos")
            inv = AKS("Servicio de Inventario\n(AKS): autonomo por eventos")
            log = EventHubs("Log de Eventos - fuente de verdad\n(Event Hubs + Service Bus)")
            query = SQLDatabases("Servicio de Consultas\n(CQRS: proyecciones)")
            adap = AKS("Adaptadores WMS/ERP")
            with Cluster("Transversal"):
                iam = ActiveDirectory("Entra ID + Key Vault")
                obs = ApplicationInsights("Azure Monitor")

        with Cluster("AWS - Ultima Milla"):
            mob = ECS("Backend Ultima Milla")
            ddb = Dynamodb("DynamoDB")
            s3 = S3("S3 + KMS (evidencias)")

        with Cluster("GCP - Analitica"):
            gpub = Pubsub("Pub/Sub")
            gbq = Bigquery("BigQuery")
            gai = AIPlatform("Vertex AI")

        with Cluster("On-premises"):
            wms = Server("WMS - Almacenes")
            erp = Server("ERP Financiero")

        tms = Server("TMS - Transporte")
        por = Server("Portal B2B / CRM")
        mapa = Server("Mapas y trafico")

        cli >> Edge(label="Comandos HTTPS/REST") >> apim
        ope >> Edge(label="Consultas (CQRS) solo lectura") >> query
        con >> Edge(label="HTTPS OAuth2+PKCE") >> mob
        apim >> Edge(label="Comandos de orden") >> oms
        oms >> Edge(label="Publica OrdenValidada AMQP") >> log
        log >> Edge(label="Entrega OrdenValidada") >> inv
        inv >> Edge(label="Publica InventarioReservado/Liberado") >> log
        log >> Edge(label="Eventos de reserva/valorizacion") >> adap
        adap >> Edge(label="Reserva fisica VPN") >> wms
        adap >> Edge(label="Valorizacion VPN") >> erp
        adap >> Edge(label="Publica resultado AMQP") >> log
        log >> Edge(label="Proyecta estados/disponibilidad") >> query
        log >> Edge(label="Eventos despacho AMQP->HTTPS") >> mob
        mob >> Edge(label="sync") >> ddb
        mob >> Edge(label="evidencias KMS") >> s3
        mob >> Edge(label="tracking HTTPS->AMQP") >> log
        log >> Edge(label="Stream AMQP->Pub/Sub") >> gpub
        gpub >> gbq
        gpub >> gai
        log >> Edge(label="Estados y excepciones") >> por
        log >> Edge(label="Despacho y entregas") >> tms
        gbq >> Edge(label="Rutas optimizadas") >> tms
        gai >> Edge(label="Trafico y ETA") >> mapa
        oms >> Edge(label="OIDC / Key Vault", **DASH) >> iam
        oms >> Edge(label="OTLP", **DASH) >> obs


def b_n3():
    with Diagram("Alternativa B (Coreografiada) - Nivel 3: Servicio de Inventario",
                 filename="B_n3_inventario", show=False, direction="LR",
                 graph_attr=GRAPH, edge_attr=EDGE, node_attr=NODE, outformat="png"):
        log = EventHubs("Log de Eventos\n(fuente de verdad)")
        invdb = SQLDatabases("BD de Inventario\n(estado + inbox/outbox)")
        query = SQLDatabases("Servicio de Consultas\n(CQRS)")
        iam = ActiveDirectory("Entra ID + Key Vault")

        with Cluster("Servicio de Inventario (coreografiado por eventos)"):
            inbox = Action("Consumidor (Inbox)\ndeduplica por id de evento")
            res = Action("Manejador de Reserva\n(reserva atomica)")
            comp = Action("Manejador de Compensacion\n(reacciona al rechazo)")
            aud = Action("Registro Auditable")
            recon = Action("Reconciliador")
            outbox = Action("Publicador Outbox")
            proj = Action("Proyector de Disponibilidad")

        log >> Edge(label="OrdenValidada / ValorizacionRechazada AMQP") >> inbox
        inbox >> Edge(label="orden nueva") >> res
        inbox >> Edge(label="valorizacion rechazada") >> comp
        res >> Edge(label="registra") >> aud
        comp >> Edge(label="registra") >> aud
        res >> Edge(label="reserva atomica TDS") >> invdb
        comp >> Edge(label="libera TDS") >> invdb
        recon >> Edge(label="concilia TDS") >> invdb
        outbox >> Edge(label="lee outbox TDS") >> invdb
        outbox >> Edge(label="publica resultado AMQP") >> log
        log >> Edge(label="eventos confirmados") >> proj
        proj >> Edge(label="actualiza proyeccion TDS") >> query
        outbox >> Edge(label="secretos", **DASH) >> iam


if __name__ == "__main__":
    a_n1(); a_n2(); a_n3()
    b_n1(); b_n2(); b_n3()
    print("Listo: 6 PNG generados en", os.getcwd())

# -*- coding: utf-8 -*-
"""
Genera los 6 diagramas C4 (Nivel 1-2-3 x Alternativa A y B).
- Nivel 1 y 3: notacion C4 nativa (cajas con texto adentro, limpias).
- Nivel 2: iconos oficiales de nube (Azure/AWS/GCP), como pide el enunciado.
Ejecutar:  python generar_diagramas.py   ->  6 PNG en esta carpeta.
"""
import os
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

from diagrams import Diagram, Cluster, Edge
from diagrams.c4 import Person, System, Container, Database, SystemBoundary, Relationship
# Iconos de nube (solo Nivel 2)
from diagrams.azure.integration import APIManagement
from diagrams.azure.compute import AKS
from diagrams.azure.database import SQLDatabases
from diagrams.azure.analytics import EventHubs
from diagrams.azure.identity import ActiveDirectory
from diagrams.azure.devops import ApplicationInsights
from diagrams.aws.compute import ECS
from diagrams.aws.database import Dynamodb
from diagrams.aws.storage import S3
from diagrams.gcp.analytics import Pubsub, Dataflow, Bigquery
from diagrams.gcp.ml import AIPlatform
from diagrams.onprem.compute import Server
from diagrams.generic.device import Mobile

# --- estilos de layout ---
C4 = {"fontsize": "20", "fontname": "Segoe UI", "bgcolor": "white",
      "pad": "0.8", "nodesep": "0.75", "ranksep": "1.2", "splines": "spline"}
N2 = {"fontsize": "22", "fontname": "Segoe UI", "bgcolor": "white",
      "pad": "1.2", "nodesep": "1.1", "ranksep": "1.9", "splines": "spline"}
EDGE = {"fontsize": "11", "fontname": "Segoe UI", "color": "#4A4A4A"}
NODE = {"fontsize": "11", "fontname": "Segoe UI"}


# ===================== NIVEL 1 — CONTEXTO (C4) =====================
def _contexto(titulo, filename, nota_plataforma):
    with Diagram(titulo, filename=filename, show=False, direction="TB",
                 graph_attr=C4, edge_attr=EDGE, node_attr=NODE, outformat="png"):
        cli = Person("Cliente B2B / Retail", "Envía órdenes y consulta trazabilidad")
        con = Person("Conductor", "Entregas y evidencias")
        ope = Person("Operación RutaExpress", "Supervisa pedidos, rutas y SLA")
        fin = Person("Finanzas", "Concilia estados y liquidación")

        plat = System("Plataforma Logística RutaExpress", nota_plataforma)

        wms = System("WMS - Almacenes", "Picking (on-premises)", external=True)
        tms = System("TMS - Transporte", "Rutas y entregas", external=True)
        erp = System("ERP Financiero", "Inventario valorizado (on-premises)", external=True)
        portal = System("Portal B2B / CRM", "Trazabilidad y reclamos", external=True)
        legado = System("Canales legados", "Órdenes CSV / Excel", external=True)
        mapas = System("Mapas y tráfico", "Geocodificación y ETA", external=True)

        cli >> Relationship("Crea órdenes / estado") >> plat
        con >> Relationship("Entregas y evidencias") >> plat
        ope >> Relationship("Monitoreo") >> plat
        fin >> Relationship("Liquidación") >> plat
        plat >> Relationship("Reserva / concilia") >> wms
        plat >> Relationship("Despacho y rutas") >> tms
        plat >> Relationship("Valorización") >> erp
        plat >> Relationship("Trazabilidad") >> portal
        legado >> Relationship("Órdenes (transicional)") >> plat
        plat >> Relationship("Tráfico y ETA") >> mapas


def a_n1():
    _contexto("Alternativa A - Nivel 1: Contexto", "A_n1_contexto",
              "Coordina orden, inventario, despacho, última milla y trazabilidad")


def b_n1():
    _contexto("Alternativa B - Nivel 1: Contexto", "B_n1_contexto",
              "Mismo alcance y actores que A; la diferencia aparece en N2/N3")


# ===================== NIVEL 2 — CONTENEDORES (iconos) =====================
def a_n2():
    with Diagram("Alternativa A (Orquestada) - Nivel 2: Contenedores", filename="A_n2_contenedores",
                 show=False, direction="LR", graph_attr=N2, edge_attr=EDGE, node_attr=NODE, outformat="png"):
        cli = Person("Cliente B2B", "")
        ope = Person("Operación / Finanzas", "")
        con = Mobile("Conductor")

        with Cluster("Azure - Núcleo e Integración"):
            apim = APIManagement("API Management\n(Gateway)")
            oms = AKS("OMS - Orquestador\n(AKS)")
            sql = SQLDatabases("Azure SQL")
            bus = EventHubs("Bus de Eventos\n(Event Hubs + Service Bus)")
            with Cluster("Transversal"):
                iam = ActiveDirectory("Entra ID + Key Vault")
                obs = ApplicationInsights("Azure Monitor")

        with Cluster("On-premises"):
            wms = Server("WMS - Almacenes")
            erp = Server("ERP Financiero")

        with Cluster("AWS - Última Milla"):
            mob = ECS("Backend Última Milla\n(ECS/Lambda)")
            ddb = Dynamodb("DynamoDB\n(sync offline)")
            s3 = S3("S3 + KMS\n(evidencias)")

        with Cluster("GCP - Analítica"):
            gpub = Pubsub("Pub/Sub")
            gflow = Dataflow("Dataflow")
            gbq = Bigquery("BigQuery")
            gai = AIPlatform("Vertex AI")

        tms = Server("TMS - Transporte")
        por = Server("Portal B2B / CRM")
        mapa = Server("Mapas y tráfico")

        cli >> Edge(label="HTTPS/REST") >> apim
        ope >> Edge(label="consultas") >> apim
        con >> Edge(label="HTTPS · PKCE") >> mob
        apim >> Edge(label="comandos") >> oms
        oms >> Edge(label="TDS") >> sql
        oms >> Edge(label="Outbox · AMQP") >> bus
        oms >> Edge(label="reserva · VPN") >> wms
        oms >> Edge(label="valorización · VPN") >> erp
        oms >> Edge(label="OIDC", style="dashed") >> iam
        oms >> Edge(label="OTLP", style="dashed") >> obs
        bus >> Edge(label="eventos · AMQP") >> mob
        mob >> Edge(label="sync") >> ddb
        mob >> Edge(label="evidencias · KMS") >> s3
        mob >> Edge(label="tracking") >> bus
        bus >> Edge(label="stream") >> gpub
        gpub >> gflow >> gbq
        gflow >> gai
        bus >> Edge(label="estados") >> por
        bus >> Edge(label="despacho") >> tms
        gbq >> Edge(label="rutas") >> tms
        gai >> Edge(label="tráfico / ETA") >> mapa


def b_n2():
    with Diagram("Alternativa B (Coreografiada) - Nivel 2: Contenedores", filename="B_n2_contenedores",
                 show=False, direction="LR", graph_attr=N2, edge_attr=EDGE, node_attr=NODE, outformat="png"):
        cli = Person("Cliente B2B", "")
        ope = Person("Operación / Finanzas", "")
        con = Mobile("Conductor")

        with Cluster("Azure - Núcleo e Integración (coreografiado)"):
            apim = APIManagement("API Management\n(Gateway)")
            oms = AKS("Servicio de Órdenes\n(AKS)")
            inv = AKS("Servicio de Inventario\n(AKS, autónomo)")
            log = EventHubs("Log de Eventos\n(fuente de verdad)")
            query = SQLDatabases("Servicio de Consultas\n(CQRS)")
            adap = AKS("Adaptadores WMS/ERP")
            with Cluster("Transversal"):
                iam = ActiveDirectory("Entra ID + Key Vault")
                obs = ApplicationInsights("Azure Monitor")

        with Cluster("On-premises"):
            wms = Server("WMS - Almacenes")
            erp = Server("ERP Financiero")

        with Cluster("AWS - Última Milla"):
            mob = ECS("Backend Última Milla")
            ddb = Dynamodb("DynamoDB")
            s3 = S3("S3 + KMS")

        with Cluster("GCP - Analítica"):
            gpub = Pubsub("Pub/Sub")
            gbq = Bigquery("BigQuery")
            gai = AIPlatform("Vertex AI")

        tms = Server("TMS - Transporte")
        por = Server("Portal B2B / CRM")
        mapa = Server("Mapas y tráfico")

        cli >> Edge(label="comandos") >> apim
        ope >> Edge(label="consultas (CQRS)") >> query
        con >> Edge(label="HTTPS · PKCE") >> mob
        apim >> Edge(label="comandos") >> oms
        oms >> Edge(label="OrdenValidada") >> log
        log >> Edge(label="entrega evento") >> inv
        inv >> Edge(label="InventarioReservado") >> log
        log >> Edge(label="eventos reserva") >> adap
        adap >> Edge(label="reserva · VPN") >> wms
        adap >> Edge(label="valorización · VPN") >> erp
        adap >> Edge(label="resultado") >> log
        log >> Edge(label="proyecta") >> query
        log >> Edge(label="eventos") >> mob
        mob >> Edge(label="sync") >> ddb
        mob >> Edge(label="evidencias · KMS") >> s3
        mob >> Edge(label="tracking") >> log
        log >> Edge(label="stream") >> gpub
        gpub >> gbq
        gpub >> gai
        log >> Edge(label="estados") >> por
        log >> Edge(label="despacho") >> tms
        gbq >> Edge(label="rutas") >> tms
        gai >> Edge(label="tráfico / ETA") >> mapa
        oms >> Edge(label="OIDC", style="dashed") >> iam
        oms >> Edge(label="OTLP", style="dashed") >> obs


# ===================== NIVEL 3 — COMPONENTES (C4) =====================
def a_n3():
    with Diagram("Alternativa A (Orquestada) - Nivel 3: Reserva de Inventario", filename="A_n3_reserva_inventario",
                 show=False, direction="LR", graph_attr=C4, edge_attr=EDGE, node_attr=NODE, outformat="png"):
        bus = System("Bus de Eventos", "Event Hubs + Service Bus", external=True)
        sql = Database("BD Transaccional", "Azure SQL")
        wms = System("WMS - Almacenes", "on-premises", external=True)
        erp = System("ERP Financiero", "on-premises", external=True)
        iam = System("Identidad y Secretos", "Entra ID + Key Vault", external=True)

        with SystemBoundary("OMS - Reserva de Inventario (orquestada por la Saga)"):
            saga = Container("Orquestador de Reserva (Saga)", "Servicio", "Comanda cada paso y compensa")
            reserva = Container("Manejador de Reserva", "Servicio", "Reserva atómica")
            inv = Container("Inventario y Reservas", "Servicio", "Disponibilidad y estado")
            aud = Container("Registro Auditable", "Servicio", "Actor, motivo, correlationId")
            recon = Container("Reconciliador", "Servicio", "Conflictos WMS / locales")
            adapt = Container("Adaptador WMS", "Servicio", "Circuit Breaker + Retry")
            outbox = Container("Publicador Outbox", "Servicio", "Publicación confiable")

        saga >> Relationship("reservar (comando)") >> reserva
        saga >> Relationship("liberar - COMPENSACIÓN") >> reserva
        saga >> Relationship("reserva física (comando)") >> adapt
        saga >> Relationship("valorización (comando) · VPN") >> erp
        reserva >> Relationship("verifica y reserva") >> inv
        reserva >> Relationship("registra") >> aud
        adapt >> Relationship("reserva/consulta · VPN") >> wms
        inv >> Relationship("deriva conflictos") >> recon
        reserva >> Relationship("persiste + outbox") >> sql
        outbox >> Relationship("lee outbox") >> sql
        outbox >> Relationship("publica resultado · AMQP") >> bus
        outbox >> Relationship("secretos") >> iam


def b_n3():
    with Diagram("Alternativa B (Coreografiada) - Nivel 3: Servicio de Inventario", filename="B_n3_inventario",
                 show=False, direction="LR", graph_attr=C4, edge_attr=EDGE, node_attr=NODE, outformat="png"):
        log = System("Log de Eventos", "fuente de verdad", external=True)
        invdb = Database("BD de Inventario", "Azure SQL")
        query = System("Servicio de Consultas", "CQRS", external=True)
        iam = System("Identidad y Secretos", "Entra ID + Key Vault", external=True)

        with SystemBoundary("Servicio de Inventario (coreografiado por eventos)"):
            inbox = Container("Consumidor (Inbox)", "Suscriptor", "Deduplica por eventId")
            reserva = Container("Manejador de Reserva", "Servicio", "Reserva atómica")
            comp = Container("Manejador de Compensación", "Servicio", "Reacciona al rechazo")
            aud = Container("Registro Auditable", "Servicio", "Actor, motivo, correlationId")
            recon = Container("Reconciliador", "Servicio", "Conflictos con almacenes")
            outbox = Container("Publicador Outbox", "Servicio", "Publica el resultado")
            proj = Container("Proyector", "Servicio", "Actualiza la proyección")

        log >> Relationship("OrdenValidada / Rechazo") >> inbox
        inbox >> Relationship("orden nueva") >> reserva
        inbox >> Relationship("valorización rechazada") >> comp
        reserva >> Relationship("registra") >> aud
        comp >> Relationship("registra") >> aud
        reserva >> Relationship("reserva atómica") >> invdb
        comp >> Relationship("libera") >> invdb
        recon >> Relationship("concilia") >> invdb
        outbox >> Relationship("lee outbox") >> invdb
        outbox >> Relationship("publica resultado · AMQP") >> log
        log >> Relationship("eventos confirmados") >> proj
        proj >> Relationship("actualiza proyección") >> query
        outbox >> Relationship("secretos") >> iam


if __name__ == "__main__":
    a_n1(); a_n2(); a_n3()
    b_n1(); b_n2(); b_n3()
    print("Listo: 6 PNG generados en", os.getcwd())

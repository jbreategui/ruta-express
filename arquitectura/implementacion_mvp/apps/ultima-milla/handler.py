"""Backend de Última Milla (AWS Lambda). Disparada por SQS (bridge desde el bus de Azure).
Consume eventos de despacho, deduplica por eventId (patrón Inbox) y registra el estado
de entrega en DynamoDB. RF-22, RF-23, RF-16 (idempotencia del consumidor).

No se ejecuta localmente (requiere runtime AWS + boto3). El código queda listo para desplegar.
"""
import json
import os

import boto3
from botocore.exceptions import ClientError

TABLE = os.getenv("DELIVERIES_TABLE", "ultima-milla-deliveries")
_dynamo = boto3.resource("dynamodb")

# La última milla solo actúa sobre órdenes listas para despacho (A6): ignora
# OrdenFallida, InventarioLiberado, OrdenCancelada, etc.
TIPOS_DESPACHABLES = {"InventarioReservado", "OrdenLista"}


def _procesar_evento(evento: dict):
    """Idempotente: si el eventId ya se procesó, se descarta (Inbox)."""
    tipo = evento.get("type")
    if tipo not in TIPOS_DESPACHABLES:
        print(f"[ULTIMA-MILLA] ignorado evento no despachable: {tipo}")
        return
    table = _dynamo.Table(TABLE)
    event_id = evento.get("eventId")
    order_id = (evento.get("payload") or {}).get("orderId")
    try:
        table.put_item(
            Item={"event_id": event_id, "order_id": order_id, "type": tipo,
                  "estado": "recibido_para_entrega"},
            ConditionExpression="attribute_not_exists(event_id)",  # dedup por eventId
        )
        print(f"[ULTIMA-MILLA] procesado {tipo} order={order_id} event={event_id}")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            print(f"[ULTIMA-MILLA] duplicado descartado event={event_id}")  # idempotencia
        else:
            raise


def handler(event, context):
    """Entrada Lambda: registros SQS. Cada record trae el evento canónico del bus."""
    procesados = 0
    for record in event.get("Records", []):
        cuerpo = json.loads(record["body"])
        _procesar_evento(cuerpo)
        procesados += 1
    return {"procesados": procesados}

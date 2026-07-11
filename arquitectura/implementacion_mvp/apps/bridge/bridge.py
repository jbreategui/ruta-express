"""Bridge intercloud (deployment en AKS). Lee eventos del Service Bus de Azure y los
reenvía a una cola SQS de AWS, que dispara la Lambda de última milla.
Ver 02_afinamiento_tecnico.md §1. Durable: si la Lambda falla, SQS reintenta + DLQ.

No se ejecuta localmente (requiere Service Bus + SQS reales). Código listo para desplegar.
Credenciales: SB por Workload Identity (o cadena de Key Vault); AWS por key de mínimo
privilegio (sqs:SendMessage) inyectada desde Key Vault.
"""
import os

import boto3
from azure.servicebus import ServiceBusClient

SB_CONNECTION = os.environ["SERVICEBUS_CONNECTION"]
SB_TOPIC = os.getenv("SERVICEBUS_TOPIC", "orders-events")
SB_SUBSCRIPTION = os.getenv("SERVICEBUS_SUBSCRIPTION", "bridge-aws")
SQS_URL = os.environ["SQS_QUEUE_URL"]

_sqs = boto3.client("sqs", region_name=os.getenv("AWS_REGION", "us-east-1"))


def run():
    with ServiceBusClient.from_connection_string(SB_CONNECTION) as client:
        receiver = client.get_subscription_receiver(SB_TOPIC, SB_SUBSCRIPTION)
        with receiver:
            for msg in receiver:
                try:
                    _sqs.send_message(QueueUrl=SQS_URL, MessageBody=str(msg))
                    receiver.complete_message(msg)   # solo se completa si SQS aceptó
                    print(f"[BRIDGE] reenviado a SQS: {msg.subject}")
                except Exception as e:                # noqa: BLE001 — reintento por el bus
                    print(f"[BRIDGE] error, se reintenta: {e}")
                    receiver.abandon_message(msg)


if __name__ == "__main__":
    run()

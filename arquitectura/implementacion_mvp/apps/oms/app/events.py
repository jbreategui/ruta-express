"""Publicación de eventos (patrón Outbox). Ver 01_diseno_detallado §3.
El evento se escribe en la tabla outbox (misma transacción que el estado);
un publicador lo envía al bus. Consola en local; Service Bus al desplegar.
"""
import json
import uuid
from datetime import datetime, timezone

from .config import settings
from .db import Outbox


def enqueue_event(session, event_type, payload, correlation_id):
    """Encola un evento canónico en la outbox dentro de la transacción actual."""
    event_id = str(uuid.uuid4())
    body = {
        "eventId": event_id,
        "type": event_type,
        "version": 1,
        "correlationId": correlation_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
    ev = Outbox(event_id=event_id, type=event_type, payload_json=json.dumps(body), published=False)
    session.add(ev)
    return ev


class ConsolePublisher:
    def publish(self, event_type, body):
        print(f"[EVENT] {event_type}: {body}")


class ServiceBusPublisher:  # se usa solo en despliegue
    def __init__(self, connection, topic):
        from azure.servicebus import ServiceBusClient, ServiceBusMessage
        self._Message = ServiceBusMessage
        self._client = ServiceBusClient.from_connection_string(connection)
        self._topic = topic

    def publish(self, event_type, body):
        with self._client.get_topic_sender(self._topic) as sender:
            sender.send_messages(self._Message(body, subject=event_type))


def get_publisher():
    if settings.SERVICEBUS_CONNECTION:
        return ServiceBusPublisher(settings.SERVICEBUS_CONNECTION, settings.SERVICEBUS_TOPIC)
    return ConsolePublisher()


def drain_outbox(session, publisher=None):
    """Publica los eventos pendientes de la outbox y los marca como publicados."""
    publisher = publisher or get_publisher()
    pending = session.query(Outbox).filter_by(published=False).order_by(Outbox.id).all()
    for ev in pending:
        publisher.publish(ev.type, ev.payload_json)
        ev.published = True
    session.commit()
    return len(pending)

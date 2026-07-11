"""Servicio de órdenes: deduplicación, idempotencia, validación, estado canónico,
disparo de la Saga, compensación en cancelación, reintento y read model (CQRS).
Ver 01_diseno_detallado §2,§4,§5.
"""
import hashlib
import json
import uuid

from sqlalchemy.exc import IntegrityError

from .db import IdempotencyKey, Order, OrderLine, ReadModelOrder
from .events import enqueue_event
from .saga import ReservationSaga

# Estados terminales: una orden aquí NO bloquea un nuevo pedido igual (dedup) ni se cancela.
TERMINAL_STATES = ("Cancelada", "Fallida", "Rechazada")
# Desde qué estados se puede cancelar (RF-05).
CANCELABLE_STATES = ("Validada", "Reservando", "Reservada", "Lista")


class IdempotencyConflict(Exception):
    """Misma Idempotency-Key reusada con contenido DISTINTO (RF-04, escenario negativo).
    El contrato responde 409: la key no se puede reutilizar para otro pedido."""

    def __init__(self, key):
        self.key = key
        super().__init__(f"Idempotency-Key reusada con contenido distinto: {key}")


def content_hash(client_id, destinatario, window, lines):
    """Hash de contenido para deduplicación (RF-03): cliente + destinatario + ventana + líneas.
    Incluir la ventana evita el falso duplicado del escenario negativo de RF-03."""
    parts = [client_id, destinatario or "", window or ""]
    parts.append(";".join(sorted(f"{ln.sku}x{ln.qty}" for ln in lines)))
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


def _update_read_model(session, order):
    rm = session.get(ReadModelOrder, order.order_id)
    inv_state = "reservado" if order.status in ("Reservada", "Lista") else order.status.lower()
    if rm is None:
        session.add(ReadModelOrder(order_id=order.order_id, status=order.status,
                                   inventory_state=inv_state))
    else:
        rm.status = order.status
        rm.inventory_state = inv_state


class OrderService:
    def __init__(self, saga=None):
        self.saga = saga or ReservationSaga()

    def _idem_hit(self, session, key):
        """Si la key ya existe: devuelve (resp, True) — respuesta original o 'Procesando'."""
        existing = session.get(IdempotencyKey, key)
        if existing is None:
            return None
        if existing.response_json:
            return json.loads(existing.response_json), True
        return {"order_id": existing.order_id, "status": "Procesando", "duplicate": True}, True

    def create_order(self, session, data, idempotency_key, correlation_id=None):
        correlation_id = correlation_id or str(uuid.uuid4())

        # 0. Hash de contenido (sirve para dedup y para detectar el conflicto de idempotencia)
        chash = content_hash(data.client_id, getattr(data, "destinatario", None),
                             data.window, data.lines)

        # 1. Idempotencia: misma key (RF-04)
        existing = session.get(IdempotencyKey, idempotency_key)
        if existing is not None:
            # RF-04 (escenario negativo): misma key + contenido DISTINTO -> conflicto 409.
            prior = session.get(Order, existing.order_id) if existing.order_id else None
            if prior is not None and prior.content_hash != chash:
                raise IdempotencyConflict(idempotency_key)
            return self._idem_hit(session, idempotency_key)

        # 2. Dedup por contenido, EXCLUYENDO órdenes terminales (A2: no bloquear al cliente)
        dup = (session.query(Order)
               .filter(Order.content_hash == chash)
               .filter(Order.status.notin_(TERMINAL_STATES))
               .first())
        if dup:
            resp = {"order_id": dup.order_id, "status": dup.status, "duplicate": True}
            return self._claim_and_finish(session, idempotency_key, dup.order_id, resp, dup=True)

        # 3. Reclamar la key ANTES de la Saga (el perdedor de la carrera no toca el WMS)
        order_id = "ORD-" + uuid.uuid4().hex[:10].upper()
        try:
            session.add(IdempotencyKey(key=idempotency_key, order_id=order_id, response_json=""))
            session.commit()
        except IntegrityError:
            session.rollback()
            return self._idem_hit(session, idempotency_key)

        # 4. Somos dueños de la key -> crear orden + estado canónico "Validada" + Saga
        order = Order(order_id=order_id, client_id=data.client_id, channel=data.channel,
                      status="Validada", sla=data.sla, window=data.window, content_hash=chash)
        order.lines = [OrderLine(sku=ln.sku, qty=ln.qty) for ln in data.lines]
        session.add(order)
        enqueue_event(session, "OrdenValidada",
                      {"orderId": order_id, "clientId": data.client_id}, correlation_id)
        self.saga.run(session, order, correlation_id)
        _update_read_model(session, order)

        resp = {"order_id": order_id, "status": order.status, "duplicate": False}
        keyrow = session.get(IdempotencyKey, idempotency_key)
        keyrow.response_json = json.dumps(resp)
        session.commit()
        return resp, False

    def _claim_and_finish(self, session, key, order_id, resp, dup):
        """Guarda la respuesta bajo la key y commitea (para el camino de duplicado)."""
        session.add(IdempotencyKey(key=key, order_id=order_id, response_json=json.dumps(resp)))
        try:
            session.commit()
            return resp, dup
        except IntegrityError:
            session.rollback()
            return self._idem_hit(session, key)

    def get_state(self, session, order_id):
        rm = session.get(ReadModelOrder, order_id)
        if rm is None:
            return None
        return {"order_id": rm.order_id, "status": rm.status, "inventory_state": rm.inventory_state}

    def cancel(self, session, order_id, idempotency_key, correlation_id=None):
        correlation_id = correlation_id or str(uuid.uuid4())
        hit = self._idem_hit(session, idempotency_key)
        if hit:
            return hit[0], hit[1], None
        order = session.get(Order, order_id)
        if order is None:
            return None, False, None
        if order.status not in CANCELABLE_STATES:
            return None, False, f"no se puede cancelar una orden en estado {order.status}"
        # C3: compensar (liberar reservas locales + físicas en el WMS) antes de cancelar
        self.saga.compensate_order(session, order, "cancelada por cliente", correlation_id)
        order.status = "Cancelada"
        enqueue_event(session, "OrdenCancelada",
                      {"orderId": order_id, "causa": "cancelada por cliente"}, correlation_id)
        _update_read_model(session, order)
        resp = {"order_id": order_id, "status": order.status, "duplicate": False}
        r, dup = self._claim_and_finish(session, idempotency_key, order_id, resp, dup=False)
        return r, dup, None

    def retry_order(self, session, order_id, correlation_id=None):
        """A3: reintenta la reserva de una orden atascada en 'Reservando' (WMS recuperado)."""
        correlation_id = correlation_id or str(uuid.uuid4())
        order = session.get(Order, order_id)
        if order is None:
            return None
        if order.status != "Reservando":
            return {"order_id": order_id, "status": order.status, "reintentado": False}
        self.saga.run(session, order, correlation_id)
        _update_read_model(session, order)
        session.commit()
        return {"order_id": order_id, "status": order.status, "reintentado": True}

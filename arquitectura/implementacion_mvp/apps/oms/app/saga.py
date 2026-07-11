"""Saga orquestada de reserva (Alternativa A). Ver 01_diseno_detallado §6.
La Saga COMANDA cada paso y ejecuta la compensación (local + física en el WMS)
si algo falla. Los clientes WMS/ERP se inyectan (en tests se usan dobles, sin red).
"""
from sqlalchemy import update

from .clients import ErpClient, ErpRejected, WmsClient
from .db import AuditMovement, Inventory, Order, Reservation
from .events import enqueue_event


class ReservationResult:
    def __init__(self, status, reason=""):
        self.status = status
        self.reason = reason


def _audit(session, order_id, type_, reason, correlation_id, actor="oms-saga"):
    session.add(AuditMovement(order_id=order_id, type=type_, actor=actor,
                              reason=reason, correlation_id=correlation_id))


def _reserve_atomic(session, sku, qty):
    """Reserva atómica de stock: UPDATE ... WHERE disponible >= qty. Devuelve True si
    reservó. Es una sola sentencia SQL -> sin sobreventa aunque haya concurrencia
    (portable: funciona en SQLite y Azure SQL, a diferencia de SELECT FOR UPDATE)."""
    res = session.execute(
        update(Inventory)
        .where(Inventory.sku == sku)
        .where(Inventory.available_qty - Inventory.reserved_qty >= qty)
        .values(reserved_qty=Inventory.reserved_qty + qty)
        .execution_options(synchronize_session="fetch")
    )
    return res.rowcount == 1


def _release_atomic(session, sku, qty):
    session.execute(
        update(Inventory)
        .where(Inventory.sku == sku)
        .values(reserved_qty=Inventory.reserved_qty - qty)
        .execution_options(synchronize_session="fetch")
    )


class ReservationSaga:
    def __init__(self, wms=None, erp=None):
        self.wms = wms or WmsClient()
        self.erp = erp or ErpClient()

    def run(self, session, order: Order, correlation_id: str) -> ReservationResult:
        order.status = "Reservando"
        reservations = []   # reservas locales hechas
        wms_reserved = []   # (sku, qty) reservadas FÍSICAMENTE en el WMS

        # 1. Reserva local ATÓMICA (RF-06). Si no alcanza, compensa lo ya reservado (C1).
        for line in order.lines:
            if not _reserve_atomic(session, line.sku, line.qty):
                self._compensate(session, order, reservations, wms_reserved,
                                 f"stock insuficiente {line.sku}", correlation_id)
                order.status = "Rechazada"
                _audit(session, order.order_id, "ReservaRechazada",
                       f"stock insuficiente {line.sku}", correlation_id)
                return ReservationResult("Rechazada", "stock insuficiente")
            r = Reservation(order_id=order.order_id, sku=line.sku, qty=line.qty, status="Reservado")
            session.add(r)
            reservations.append(r)

        # 2. Reserva física en el WMS (resiliente). Si falla (incluso a mitad),
        #    se compensa lo local Y lo físico ya hecho (C2); la orden no se pierde (RF-11).
        try:
            for line in order.lines:
                self.wms.reservar_fisico(order.order_id, line.sku, line.qty)
                wms_reserved.append((line.sku, line.qty))
        except Exception as e:  # WmsError, CircuitOpenError, timeout...
            self._compensate(session, order, reservations, wms_reserved,
                             f"WMS no disponible: {e}", correlation_id)
            order.status = "Reservando"  # queda para reintento (endpoint /reintentar)
            _audit(session, order.order_id, "WmsNoDisponible", str(e), correlation_id)
            return ReservationResult("Reintentar", "WMS no disponible")

        # 3. Valorización en el ERP. Si rechaza -> COMPENSACIÓN local + física (RF-08).
        try:
            self.erp.valorizar(order.order_id, len(order.lines))
        except ErpRejected as e:
            self._compensate(session, order, reservations, wms_reserved,
                             "ERP rechazó valorización", correlation_id)
            order.status = "Fallida"
            enqueue_event(session, "OrdenFallida",
                          {"orderId": order.order_id, "causa": str(e)}, correlation_id)
            return ReservationResult("Fallida", "ERP rechazó")

        # 4. Éxito: Reservada -> Lista, publica eventos (vía outbox)
        order.status = "Reservada"
        for r in reservations:
            enqueue_event(session, "InventarioReservado",
                          {"orderId": order.order_id, "sku": r.sku, "qty": r.qty}, correlation_id)
        order.status = "Lista"
        enqueue_event(session, "OrdenLista", {"orderId": order.order_id}, correlation_id)
        _audit(session, order.order_id, "Reservada", "reserva y valorización OK", correlation_id)
        return ReservationResult("Lista")

    def _release_wms(self, session, order_id, wms_reserved, correlation_id):
        """Libera físicamente en el WMS lo ya reservado (tolerante a fallos)."""
        for sku, qty in wms_reserved:
            try:
                self.wms.liberar_fisico(order_id, sku, qty)
            except Exception as e:  # no romper la compensación si el WMS no responde
                _audit(session, order_id, "CompensacionWmsFallo", str(e), correlation_id)

    def _compensate(self, session, order, reservations, wms_reserved, reason, correlation_id):
        """Compensación completa: libera lo físico (WMS) y lo local, y audita."""
        self._release_wms(session, order.order_id, wms_reserved, correlation_id)
        for r in reservations:
            if r.status == "Reservado":
                _release_atomic(session, r.sku, r.qty)
                r.status = "Liberado"
        enqueue_event(session, "InventarioLiberado",
                      {"orderId": order.order_id, "motivo": reason}, correlation_id)
        _audit(session, order.order_id, "Compensacion", reason, correlation_id)

    def compensate_order(self, session, order, reason, correlation_id):
        """Compensa una orden EXISTENTE (usado por cancelación): libera sus reservas
        activas (local + WMS) consultando la BD."""
        reservations = session.query(Reservation).filter_by(
            order_id=order.order_id, status="Reservado").all()
        wms_reserved = [(r.sku, r.qty) for r in reservations]
        self._compensate(session, order, reservations, wms_reserved, reason, correlation_id)

    def release_order_wms(self, order_id, lines):
        """Libera en el WMS las reservas de una orden (compensación externa, sin sesión).
        Se usa al abortar por conflicto de idempotencia (evita reserva física huérfana)."""
        for sku, qty in lines:
            try:
                self.wms.liberar_fisico(order_id, sku, qty)
            except Exception:  # noqa: BLE001 — best-effort, el WMS es idempotente
                pass

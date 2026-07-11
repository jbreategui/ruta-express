"""Saga orquestada: éxito, compensación (ERP rechaza), WMS caído y stock insuficiente.
RF-06, RF-07, RF-08, RF-11.
"""
from app.db import AuditMovement, Inventory, Order, OrderLine, Outbox
from app.saga import ReservationSaga
from tests.conftest import FakeErpAccept, FakeErpReject, FakeWmsDown, FakeWmsOk


def _nueva_orden(session, sku="SKU-001", qty=2):
    o = Order(order_id="ORD-TEST", client_id="C1", channel="api", status="Validada",
              content_hash="h")
    o.lines = [OrderLine(sku=sku, qty=qty)]
    session.add(o)
    session.flush()
    return o


def _tipos_outbox(session):
    session.flush()  # la Saga encola en outbox; el commit real lo hace el servicio
    return {e.type for e in session.query(Outbox).all()}


def test_saga_exito(session):
    o = _nueva_orden(session)
    res = ReservationSaga(wms=FakeWmsOk(), erp=FakeErpAccept()).run(session, o, "corr-1")
    assert res.status == "Lista"
    assert session.get(Inventory, "SKU-001").reserved_qty == 2
    assert {"InventarioReservado", "OrdenLista"} <= _tipos_outbox(session)


def test_saga_compensa_si_erp_rechaza(session):
    o = _nueva_orden(session)
    res = ReservationSaga(wms=FakeWmsOk(), erp=FakeErpReject()).run(session, o, "corr-2")
    assert res.status == "Fallida"
    # compensación: el stock reservado se liberó
    assert session.get(Inventory, "SKU-001").reserved_qty == 0
    assert "InventarioLiberado" in _tipos_outbox(session)
    tipos_audit = {a.type for a in session.query(AuditMovement).all()}
    assert "Compensacion" in tipos_audit


def test_saga_wms_caido_no_pierde_orden(session):
    o = _nueva_orden(session)
    res = ReservationSaga(wms=FakeWmsDown(), erp=FakeErpAccept()).run(session, o, "corr-3")
    assert res.status == "Reintentar"
    assert o.status == "Reservando"          # queda encolada, no se pierde ni se confirma
    assert session.get(Inventory, "SKU-001").reserved_qty == 0  # compensada


def test_saga_stock_insuficiente(session):
    o = _nueva_orden(session, sku="SKU-002", qty=10)  # solo hay 5
    res = ReservationSaga(wms=FakeWmsOk(), erp=FakeErpAccept()).run(session, o, "corr-4")
    assert res.status == "Rechazada"
    assert session.get(Inventory, "SKU-002").reserved_qty == 0


def test_saga_multilinea_rechazo_compensa_lineas_previas(session):
    # C1: [SKU-001 x2 OK, SKU-002 x99 sin stock] -> rechaza y NO deja SKU-001 colgado
    o = Order(order_id="ORD-ML", client_id="C1", channel="api", status="Validada", content_hash="h2")
    o.lines = [OrderLine(sku="SKU-001", qty=2), OrderLine(sku="SKU-002", qty=99)]
    session.add(o)
    session.flush()
    res = ReservationSaga(wms=FakeWmsOk(), erp=FakeErpAccept()).run(session, o, "corr-ml")
    assert res.status == "Rechazada"
    assert session.get(Inventory, "SKU-001").reserved_qty == 0   # compensada, no colgada
    assert session.get(Inventory, "SKU-002").reserved_qty == 0


def test_saga_compensacion_libera_wms(session):
    # C2: si el ERP rechaza, la compensación libera la reserva FÍSICA en el WMS
    o = _nueva_orden(session)
    wms = FakeWmsOk()
    ReservationSaga(wms=wms, erp=FakeErpReject()).run(session, o, "corr-c2")
    assert ("SKU-001", 2) in wms.reservados
    assert ("SKU-001", 2) in wms.liberados   # se liberó físicamente

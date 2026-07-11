"""RF-03 (deduplicación por hash) y RF-04 (idempotencia por key)."""
from app.saga import ReservationSaga
from app.schemas import LineIn, OrderIn
from app.service import OrderService
from tests.conftest import FakeErpAccept, FakeWmsOk


def _service():
    return OrderService(saga=ReservationSaga(wms=FakeWmsOk(), erp=FakeErpAccept()))


def _orden(client="C1", sku="SKU-001", qty=2):
    return OrderIn(client_id=client, lines=[LineIn(sku=sku, qty=qty)])


def test_idempotencia_misma_key_no_duplica(session):
    svc = _service()
    r1, dup1 = svc.create_order(session, _orden(), "key-1")
    r2, dup2 = svc.create_order(session, _orden(), "key-1")  # misma key
    assert dup1 is False and r1["status"] == "Lista"
    assert dup2 is True                      # reconoce el reintento
    assert r2["order_id"] == r1["order_id"]  # devuelve el mismo orderId


def test_dedup_mismo_contenido_otra_key(session):
    svc = _service()
    r1, _ = svc.create_order(session, _orden(), "key-1")
    r2, dup2 = svc.create_order(session, _orden(), "key-2")  # otra key, mismo pedido
    assert dup2 is True                      # detecta duplicado por hash de contenido
    assert r2["order_id"] == r1["order_id"]


def test_pedido_distinto_es_nuevo(session):
    svc = _service()
    r1, _ = svc.create_order(session, _orden(qty=2), "key-1")
    r2, dup2 = svc.create_order(session, _orden(qty=3), "key-2")  # distinto contenido
    assert dup2 is False
    assert r2["order_id"] != r1["order_id"]

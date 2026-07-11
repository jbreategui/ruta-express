"""Cancelación con compensación (C3), dedup con ventana (A1) y dedup que no bloquea
tras estados terminales (A2)."""
from app.db import Inventory
from app.saga import ReservationSaga
from app.schemas import LineIn, OrderIn
from app.service import OrderService
from tests.conftest import FakeErpAccept, FakeWmsOk


def _svc():
    return OrderService(saga=ReservationSaga(wms=FakeWmsOk(), erp=FakeErpAccept()))


def _orden(client="C1", sku="SKU-001", qty=2, window=None):
    return OrderIn(client_id=client, window=window, lines=[LineIn(sku=sku, qty=qty)])


def test_cancelar_compensa_inventario(session):
    # C3: cancelar una orden Lista libera el inventario reservado
    svc = _svc()
    r, _ = svc.create_order(session, _orden(), "k1")
    assert r["status"] == "Lista"
    assert session.get(Inventory, "SKU-001").reserved_qty == 2
    resp, _dup, err = svc.cancel(session, r["order_id"], "k-cancel")
    assert err is None and resp["status"] == "Cancelada"
    assert session.get(Inventory, "SKU-001").reserved_qty == 0   # compensado


def test_cancelar_estado_invalido_se_rechaza(session):
    # C3/RF-05: no se puede cancelar dos veces (transición inválida)
    svc = _svc()
    r, _ = svc.create_order(session, _orden(), "k2")
    svc.cancel(session, r["order_id"], "k-c1")
    _resp, _dup, err = svc.cancel(session, r["order_id"], "k-c2")
    assert err is not None            # ya está Cancelada -> rechazado


def test_dedup_respeta_ventana(session):
    # A1: mismo cliente y líneas pero ventana distinta -> NO es duplicado (RF-03 negativo)
    svc = _svc()
    r1, _ = svc.create_order(session, _orden(window="10:00-12:00"), "k3")
    r2, dup = svc.create_order(session, _orden(window="16:00-18:00"), "k4")
    assert dup is False
    assert r2["order_id"] != r1["order_id"]


def test_dedup_no_bloquea_tras_cancelar(session):
    # A2: tras cancelar, el cliente puede volver a pedir lo mismo
    svc = _svc()
    r1, _ = svc.create_order(session, _orden(), "k5")
    svc.cancel(session, r1["order_id"], "k-c")
    r2, dup = svc.create_order(session, _orden(), "k6")   # mismo contenido, orden cancelada
    assert dup is False                                   # no lo bloquea
    assert r2["order_id"] != r1["order_id"]

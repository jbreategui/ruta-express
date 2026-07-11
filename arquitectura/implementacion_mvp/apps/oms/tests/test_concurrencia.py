"""Reserva atómica sin sobreventa (ALTO 1) y carrera de idempotencia sin reserva
física huérfana (MEDIO 2)."""
from app.db import Inventory
from app.saga import _reserve_atomic
from app.schemas import LineIn, OrderIn
from app.saga import ReservationSaga
from app.service import OrderService
from tests.conftest import FakeErpAccept, FakeWmsOk


def test_reserva_atomica_no_sobrevende(session):
    # SKU-002 tiene 5. Dos reservas de 3 -> solo una debe pasar (no 6 sobre 5).
    ok1 = _reserve_atomic(session, "SKU-002", 3)
    ok2 = _reserve_atomic(session, "SKU-002", 3)
    assert ok1 is True
    assert ok2 is False                                  # la segunda NO sobrevende
    assert session.get(Inventory, "SKU-002").reserved_qty == 3


def test_reserva_atomica_justo_al_limite(session):
    assert _reserve_atomic(session, "SKU-002", 5) is True
    assert _reserve_atomic(session, "SKU-002", 1) is False
    assert session.get(Inventory, "SKU-002").reserved_qty == 5


def test_idempotencia_no_deja_reserva_huerfana_en_wms(session):
    # El perdedor de la carrera de key no debe dejar reservas físicas colgadas:
    # con claim-early, sólo el ganador ejecuta la Saga.
    wms = FakeWmsOk()
    svc = OrderService(saga=ReservationSaga(wms=wms, erp=FakeErpAccept()))
    data = OrderIn(client_id="C1", lines=[LineIn(sku="SKU-001", qty=2)])
    r1, _ = svc.create_order(session, data, "k-race")
    # segunda llamada con la MISMA key: es idempotente, NO vuelve a reservar en el WMS
    r2, dup = svc.create_order(session, data, "k-race")
    assert dup is True and r2["order_id"] == r1["order_id"]
    assert wms.reservados.count(("SKU-001", 2)) == 1     # una sola reserva física

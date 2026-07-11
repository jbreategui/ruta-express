"""Fixtures de test. BD SQLite aislada por test (sin red, sin nube)."""
import os

import pytest

# BD por defecto en memoria para no crear archivos durante los tests
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app.db import build_session_factory  # noqa: E402
from app.clients import WmsError, ErpRejected  # noqa: E402


@pytest.fixture
def session(tmp_path):
    url = f"sqlite:///{tmp_path}/test.db"
    _engine, factory = build_session_factory(url, seed=True)
    with factory() as s:
        yield s


# --- Dobles de prueba (fakes) para WMS/ERP: no tocan la red ---
class FakeWmsOk:
    """Registra las reservas y liberaciones físicas para poder verificarlas."""
    def __init__(self):
        self.reservados = []
        self.liberados = []

    def reservar_fisico(self, order_id, sku, qty):
        self.reservados.append((sku, qty))
        return {"ok": True}

    def liberar_fisico(self, order_id, sku, qty):
        self.liberados.append((sku, qty))
        return {"liberado": True}


class FakeWmsDown:
    def reservar_fisico(self, order_id, sku, qty):
        raise WmsError("WMS 503")

    def liberar_fisico(self, order_id, sku, qty):
        return {"liberado": True}


class FakeErpAccept:
    def valorizar(self, order_id, total_lines):
        return {"valorizado": True}


class FakeErpReject:
    def valorizar(self, order_id, total_lines):
        raise ErpRejected("rechazado")

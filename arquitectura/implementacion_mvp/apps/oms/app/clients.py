"""Clientes hacia los sistemas simulados (WMS/ERP), con resiliencia.
Se definen interfaces simples para poder inyectar dobles (fakes) en los tests
sin tocar la red. Ver 01_diseno_detallado §6-§7.
"""
import httpx

from .config import settings
from .resilience import CircuitBreaker, retry_with_backoff


class WmsError(Exception):
    pass


class ErpRejected(Exception):
    """El ERP rechaza la valorización -> dispara la compensación de la Saga."""


class WmsClient:
    """Adaptador de transición hacia el WMS on-prem (aquí, el mock).
    Aplica Circuit Breaker + Timeout + Retry(backoff+jitter)."""

    def __init__(self, base_url=None, timeout=None, breaker=None):
        self.base_url = base_url or settings.WMS_URL
        self.timeout = timeout or settings.CALL_TIMEOUT_S
        self.breaker = breaker or CircuitBreaker(
            fail_threshold=settings.CB_FAIL_THRESHOLD, reset_s=settings.CB_RESET_S, name="wms")

    def _post(self, order_id, sku, qty):
        r = httpx.post(f"{self.base_url}/reservar",
                       json={"order_id": order_id, "sku": sku, "qty": qty}, timeout=self.timeout)
        if r.status_code >= 500:
            raise WmsError(f"WMS {r.status_code}")
        return r.json()

    def reservar_fisico(self, order_id, sku, qty):
        return retry_with_backoff(
            lambda: self._post(order_id, sku, qty),
            attempts=settings.RETRY_ATTEMPTS, base_s=settings.RETRY_BASE_S,
            breaker=self.breaker, retry_on=(WmsError, httpx.TimeoutException, httpx.HTTPError))

    def liberar_fisico(self, order_id, sku, qty):
        """Compensación: libera una reserva física en el WMS. Tolerante a fallos."""
        r = httpx.post(f"{self.base_url}/liberar",
                       json={"order_id": order_id, "sku": sku, "qty": qty}, timeout=self.timeout)
        r.raise_for_status()
        return r.json()


class ErpClient:
    """Valorización financiera (mock ERP). Lanza ErpRejected si el ERP rechaza."""

    def __init__(self, base_url=None, timeout=None):
        self.base_url = base_url or settings.ERP_URL
        self.timeout = timeout or settings.CALL_TIMEOUT_S

    def valorizar(self, order_id, total_lines):
        r = httpx.post(f"{self.base_url}/valorizar",
                       json={"order_id": order_id, "lines": total_lines}, timeout=self.timeout)
        if r.status_code == 422:
            raise ErpRejected(f"ERP rechazó la valorización de {order_id}")
        r.raise_for_status()
        return r.json()

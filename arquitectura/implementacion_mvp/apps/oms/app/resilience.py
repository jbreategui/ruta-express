"""Patrones de resiliencia (Módulo 3 S4): Circuit Breaker + Retry con backoff y jitter.
Sin dependencias externas; `now`, `sleep` y `jitter` son inyectables para tests deterministas.
Ver 01_diseno_detallado §7.
"""
import threading
import time


class CircuitOpenError(Exception):
    """El circuito está abierto: se falla rápido sin llamar al servicio."""


class CircuitBreaker:
    """Estados: closed -> (fallos >= umbral) -> open -> (tras reset_s) -> half-open.
    Thread-safe: el estado se protege con un lock (varios workers comparten el breaker)."""

    def __init__(self, fail_threshold=3, reset_s=30.0, name="cb", now=time.monotonic):
        self.fail_threshold = fail_threshold
        self.reset_s = reset_s
        self.name = name
        self.now = now
        self._fails = 0
        self._opened_at = 0.0
        self._state = "closed"
        self._lock = threading.Lock()

    def before_call(self):
        with self._lock:
            if self._state == "open":
                if (self.now() - self._opened_at) >= self.reset_s:
                    self._state = "half-open"
                else:
                    raise CircuitOpenError(f"{self.name} abierto")

    def on_success(self):
        with self._lock:
            self._fails = 0
            self._state = "closed"

    def on_failure(self):
        with self._lock:
            self._fails += 1
            if self._state == "half-open" or self._fails >= self.fail_threshold:
                self._state = "open"
                self._opened_at = self.now()

    @property
    def state(self):
        return self._state


def retry_with_backoff(fn, attempts=3, base_s=1.0, breaker=None,
                       sleep=time.sleep, jitter=lambda: 0.0, retry_on=Exception):
    """Ejecuta fn() con reintentos, backoff exponencial + jitter y circuit breaker."""
    last = None
    for i in range(attempts):
        if breaker:
            breaker.before_call()  # puede lanzar CircuitOpenError (fallo rápido)
        try:
            result = fn()
            if breaker:
                breaker.on_success()
            return result
        except retry_on as e:
            last = e
            if breaker:
                breaker.on_failure()
            if i < attempts - 1:
                sleep(base_s * (2 ** i) + jitter())
    raise last

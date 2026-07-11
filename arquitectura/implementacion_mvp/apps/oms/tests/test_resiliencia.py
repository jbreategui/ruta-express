"""Circuit Breaker + Retry con backoff. RF-11, RF-16 (patrones Módulo 3 S4)."""
import pytest

from app.resilience import CircuitBreaker, CircuitOpenError, retry_with_backoff


def test_circuit_breaker_abre_tras_umbral():
    reloj = [0.0]
    cb = CircuitBreaker(fail_threshold=3, reset_s=30, now=lambda: reloj[0])
    for _ in range(3):
        cb.before_call()
        cb.on_failure()
    assert cb.state == "open"
    with pytest.raises(CircuitOpenError):   # fail-fast: no deja llamar
        cb.before_call()


def test_circuit_breaker_half_open_y_cierra():
    reloj = [0.0]
    cb = CircuitBreaker(fail_threshold=3, reset_s=30, now=lambda: reloj[0])
    for _ in range(3):
        cb.before_call()
        cb.on_failure()
    reloj[0] = 31            # pasa el tiempo de reset
    cb.before_call()          # -> half-open
    assert cb.state == "half-open"
    cb.on_success()           # prueba OK -> cierra
    assert cb.state == "closed"


def test_retry_reintenta_y_luego_exito():
    intentos = {"n": 0}

    def flaky():
        intentos["n"] += 1
        if intentos["n"] < 3:
            raise ValueError("temporal")
        return "ok"

    r = retry_with_backoff(flaky, attempts=3, base_s=0, sleep=lambda s: None, retry_on=ValueError)
    assert r == "ok" and intentos["n"] == 3


def test_retry_agota_y_propaga():
    def siempre_falla():
        raise ValueError("persistente")

    with pytest.raises(ValueError):
        retry_with_backoff(siempre_falla, attempts=3, base_s=0, sleep=lambda s: None,
                           retry_on=ValueError)

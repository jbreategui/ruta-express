"""Mocks WMS/ERP (API mock permitido por el enunciado).
Una sola imagen expone ambos endpoints; se despliega como dos deployments
(wms-mock y erp-mock). El "modo" fuerza escenarios para la demo:
  WMS /reservar  → modo ok | slow | down
  ERP /valorizar → modo accept | reject
El modo viene por env MODE (default) y puede sobreescribirse por query ?modo=.
"""
import os
import time

from fastapi import FastAPI, Query, Response

app = FastAPI(title="Mocks WMS/ERP", version="1.0")

WMS_MODE = os.getenv("WMS_MODE", "ok")
ERP_MODE = os.getenv("ERP_MODE", "accept")
SLOW_SECONDS = float(os.getenv("SLOW_SECONDS", "5"))  # supera el timeout del OMS (2s)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reservar")
def reservar(payload: dict, response: Response, modo: str = Query(default=None)):
    modo = modo or WMS_MODE
    if modo == "down":
        response.status_code = 503           # dispara Retry + Circuit Breaker en el OMS
        return {"error": "WMS no disponible"}
    if modo == "slow":
        time.sleep(SLOW_SECONDS)             # dispara Timeout en el OMS
    return {"reservado": True, "order_id": payload.get("order_id")}


@app.post("/liberar")
def liberar(payload: dict):
    # Compensación física: liberar una reserva previa en el WMS (idempotente).
    return {"liberado": True, "order_id": payload.get("order_id")}


@app.post("/valorizar")
def valorizar(payload: dict, response: Response, modo: str = Query(default=None)):
    modo = modo or ERP_MODE
    if modo == "reject":
        response.status_code = 422           # dispara la compensación de la Saga
        return {"error": "valorización rechazada"}
    return {"valorizado": True, "order_id": payload.get("order_id")}

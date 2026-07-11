"""API HTTP del OMS (FastAPI). Contratos de 01_diseno_detallado §2.
Toda escritura exige el header Idempotency-Key. El bus publica vía outbox.
"""
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from sqlalchemy.orm import Session

from .db import SessionLocal, engine, init_schema
from .events import drain_outbox
from .schemas import OrderIn, OrderOut, OrderStateOut
from .service import IdempotencyConflict, OrderService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crea el esquema y siembra inventario al ARRANCAR (no en el import): si la BD
    # no responde, falla el arranque de forma controlada, no en tiempo de import.
    init_schema(engine, seed=True)
    yield


app = FastAPI(title="OMS - Orquestador de Pedidos", version="1.0", lifespan=lifespan)
service = OrderService()


def get_session():
    with SessionLocal() as s:
        yield s


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/ordenes", response_model=OrderOut, status_code=201)
def crear_orden(data: OrderIn, session: Session = Depends(get_session),
                idempotency_key: str = Header(default=None, alias="Idempotency-Key"),
                correlation_id: str = Header(default=None, alias="X-Correlation-Id")):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Falta el header Idempotency-Key")
    try:
        resp, _dup = service.create_order(session, data, idempotency_key,
                                          correlation_id or str(uuid.uuid4()))
    except IdempotencyConflict:
        # RF-04 (escenario negativo): la key ya se usó para un pedido distinto.
        raise HTTPException(status_code=409,
                            detail="Idempotency-Key ya usada con un contenido distinto")
    drain_outbox(session)  # publica los eventos encolados (consola en local, bus al desplegar)
    return resp


@app.get("/v1/ordenes/{order_id}", response_model=OrderStateOut)
def consultar_orden(order_id: str, session: Session = Depends(get_session)):
    state = service.get_state(session, order_id)
    if state is None:
        raise HTTPException(status_code=404, detail="orden no encontrada")
    return state


@app.post("/v1/ordenes/{order_id}/cancelar", response_model=OrderOut)
def cancelar_orden(order_id: str, session: Session = Depends(get_session),
                   idempotency_key: str = Header(default=None, alias="Idempotency-Key")):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Falta el header Idempotency-Key")
    resp, _dup, error = service.cancel(session, order_id, idempotency_key)
    if error:
        raise HTTPException(status_code=409, detail=error)   # transición inválida (RF-05)
    if resp is None:
        raise HTTPException(status_code=404, detail="orden no encontrada")
    drain_outbox(session)
    return resp


@app.post("/v1/ordenes/{order_id}/reintentar")
def reintentar_orden(order_id: str, session: Session = Depends(get_session)):
    """Reprocesa una orden atascada en 'Reservando' (WMS recuperado). RF-11."""
    result = service.retry_order(session, order_id)
    if result is None:
        raise HTTPException(status_code=404, detail="orden no encontrada")
    drain_outbox(session)
    return result

"""Contratos de la API (Pydantic). Ver 01_diseno_detallado §2."""
from typing import List, Optional

from pydantic import BaseModel, Field


class LineIn(BaseModel):
    sku: str
    qty: int = Field(gt=0)


class OrderIn(BaseModel):
    client_id: str
    destinatario: Optional[str] = None
    channel: str = "api"
    sla: Optional[str] = None
    window: Optional[str] = None
    lines: List[LineIn] = Field(min_length=1)


class OrderOut(BaseModel):
    order_id: str
    status: str
    duplicate: bool = False


class OrderStateOut(BaseModel):
    order_id: str
    status: str
    inventory_state: Optional[str] = None

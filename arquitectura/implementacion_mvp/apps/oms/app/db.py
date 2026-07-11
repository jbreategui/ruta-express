"""Capa de datos (SQLAlchemy). Modelo de 01_diseno_detallado §4.
Funciona con SQLite (local/test) o Azure SQL (despliegue) según DATABASE_URL.
`build_session_factory` permite crear una BD aislada por test.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text, create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from .config import settings

Base = declarative_base()


def _now():
    return datetime.now(timezone.utc)


class Order(Base):
    __tablename__ = "orders"
    order_id = Column(String(40), primary_key=True)
    client_id = Column(String(60), nullable=False)
    channel = Column(String(30), nullable=False)
    status = Column(String(20), nullable=False, default="Recibida")
    sla = Column(String(30))
    window = Column(String(40))
    content_hash = Column(String(64), index=True)
    created_at = Column(DateTime, default=_now)
    lines = relationship("OrderLine", cascade="all, delete-orphan", backref="order")


class OrderLine(Base):
    __tablename__ = "order_lines"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(40), ForeignKey("orders.order_id"))
    sku = Column(String(40), nullable=False)
    qty = Column(Integer, nullable=False)


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"
    key = Column(String(80), primary_key=True)
    order_id = Column(String(40))
    response_json = Column(Text)
    created_at = Column(DateTime, default=_now)


class Inventory(Base):
    __tablename__ = "inventory"
    sku = Column(String(40), primary_key=True)
    available_qty = Column(Integer, nullable=False, default=0)
    reserved_qty = Column(Integer, nullable=False, default=0)


class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(40), index=True)
    sku = Column(String(40))
    qty = Column(Integer)
    status = Column(String(20), default="Reservado")  # Reservado | Liberado


class Outbox(Base):
    __tablename__ = "outbox"
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(40), unique=True)
    type = Column(String(40))
    payload_json = Column(Text)
    published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_now)


class AuditMovement(Base):
    __tablename__ = "audit_movements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(40), index=True)
    type = Column(String(40))
    actor = Column(String(40))
    reason = Column(String(200))
    correlation_id = Column(String(40))
    at = Column(DateTime, default=_now)


class ReadModelOrder(Base):
    __tablename__ = "read_model_orders"
    order_id = Column(String(40), primary_key=True)
    status = Column(String(20))
    inventory_state = Column(String(40))
    updated_at = Column(DateTime, default=_now, onupdate=_now)


def _make_engine(url: str):
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, future=True)


def init_schema(engine, seed: bool = True):
    """Crea el esquema y (opcional) siembra inventario de demo. Se llama explícitamente
    al ARRANCAR la app (no en el import) para no romper si la BD aún no responde."""
    Base.metadata.create_all(engine)
    if seed:
        factory = sessionmaker(bind=engine, future=True)
        with factory() as s:
            if not s.get(Inventory, "SKU-001"):
                s.add_all([
                    Inventory(sku="SKU-001", available_qty=100, reserved_qty=0),
                    Inventory(sku="SKU-002", available_qty=5, reserved_qty=0),
                ])
                s.commit()


def build_session_factory(url: str = None, seed: bool = True):
    """Helper de tests: engine + SessionLocal con esquema creado (BD aislada)."""
    url = url or settings.DATABASE_URL
    engine = _make_engine(url)
    init_schema(engine, seed=seed)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)
    return engine, factory


# Fábrica por defecto de la app: SOLO crea engine + sessionmaker (sin tocar la BD en el import)
engine = _make_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)

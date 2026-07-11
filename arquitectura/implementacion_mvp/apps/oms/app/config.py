"""Configuración por variables de entorno (12-factor).
Local/test: SQLite + publicador de eventos en consola.
Despliegue: DATABASE_URL (Azure SQL) y SERVICEBUS_CONNECTION se inyectan por Key Vault.
"""
import os


class Settings:
    # Local/test: SQLite. Despliegue (Azure SQL): se inyecta como
    #   mssql+pymssql://<login>:<pass>@<server>.database.windows.net:1433/<db>
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./oms_dev.db")

    SERVICEBUS_CONNECTION: str = os.getenv("SERVICEBUS_CONNECTION", "")
    SERVICEBUS_TOPIC: str = os.getenv("SERVICEBUS_TOPIC", "orders-events")

    WMS_URL: str = os.getenv("WMS_URL", "http://localhost:8081")
    ERP_URL: str = os.getenv("ERP_URL", "http://localhost:8082")

    # Resiliencia (config, no hardcode) — 01_diseno_detallado §7
    CALL_TIMEOUT_S: float = float(os.getenv("CALL_TIMEOUT_S", "2"))
    CB_FAIL_THRESHOLD: int = int(os.getenv("CB_FAIL_THRESHOLD", "3"))
    CB_RESET_S: float = float(os.getenv("CB_RESET_S", "30"))
    RETRY_ATTEMPTS: int = int(os.getenv("RETRY_ATTEMPTS", "3"))
    RETRY_BASE_S: float = float(os.getenv("RETRY_BASE_S", "1"))


settings = Settings()

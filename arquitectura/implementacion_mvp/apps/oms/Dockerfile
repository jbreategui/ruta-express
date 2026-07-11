# Imagen del OMS — se construye y se sube a ACR al desplegar (no ahora)
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8080
# Al desplegar, DATABASE_URL / SERVICEBUS_CONNECTION se inyectan por Key Vault
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

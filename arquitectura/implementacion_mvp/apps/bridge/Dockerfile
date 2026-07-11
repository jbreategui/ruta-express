FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bridge.py .
# Worker sin puerto: consume del Service Bus y reenvía a SQS
CMD ["python", "bridge.py"]

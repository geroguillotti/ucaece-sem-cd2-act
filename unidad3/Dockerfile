FROM python:3.11-slim

WORKDIR /app

ENV MLFLOW_DISABLE_AGENT_HINT=1

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY src/ src/
COPY modelo_exportado/ modelo_exportado/

EXPOSE 8000

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]

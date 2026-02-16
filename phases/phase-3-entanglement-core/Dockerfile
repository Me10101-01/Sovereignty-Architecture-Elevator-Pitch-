# Phase 3: Entanglement Core (stub) - Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir numpy

COPY src/ ./src/

ENV PYTHONPATH=/app/src:$PYTHONPATH

CMD ["python", "src/qubit_entangle.py"]

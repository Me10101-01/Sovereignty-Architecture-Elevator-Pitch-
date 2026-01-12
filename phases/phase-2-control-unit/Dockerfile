# Phase 2: Control Unit - Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir sympy

COPY src/ ./src/

ENV PYTHONPATH=/app/src:$PYTHONPATH

CMD ["python", "src/control_flow.py"]

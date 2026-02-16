# Phase 4: Register Memory - Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir numpy sympy

COPY src/ ./src/

ENV PYTHONPATH=/app/src:$PYTHONPATH

CMD ["python", "src/quantum_regs.py"]

# Phase 1: Symbolic ALU - Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir sympy mpmath

COPY src/ ./src/

ENV PYTHONPATH=/app/src:$PYTHONPATH

CMD ["python", "src/alu_core.py"]

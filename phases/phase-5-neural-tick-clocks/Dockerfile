# Phase 5: Neural Tick Clocks - Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir numpy

COPY src/ ./src/

ENV PYTHONPATH=/app/src:$PYTHONPATH

CMD ["python", "src/tick_scheduler.py"]

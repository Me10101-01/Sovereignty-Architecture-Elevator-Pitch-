# Phase 2: Prior Art Guards
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pyyaml

COPY phase2/*.py ./

CMD ["python", "guards.py"]

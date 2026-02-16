# Phase 1: Bootstrap Tree Initialization
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pyyaml

COPY phase1/*.py ./

CMD ["python", "bootstrap.py"]

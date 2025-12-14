# Phase 5: Full Integration and Recursive Evolution
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pyyaml numpy sympy networkx

COPY phase5/*.py ./
COPY docs ./docs
COPY src/swarm_bots ./swarm_bots

CMD ["python", "integrate.py"]

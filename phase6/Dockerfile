# Phase 6: Superposition Expansion and Ripley Gates Exploration
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pyyaml numpy sympy networkx

COPY phase6/*.py ./
COPY docs ./docs
COPY feps ./feps

CMD ["python", "expand_claim8.py"]

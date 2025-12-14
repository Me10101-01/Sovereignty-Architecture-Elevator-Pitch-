# Phase 7: Ripley 12 Gates Deepening, SAGCO Evolution, and Benchmarks
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pyyaml numpy sympy networkx

COPY phase7/*.py ./
COPY docs ./docs
COPY benchmarks ./benchmarks

CMD ["python", "deepen_ripley_explore_sagco.py"]

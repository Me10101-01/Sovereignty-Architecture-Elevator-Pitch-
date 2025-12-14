FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for Phase 13
RUN pip install --no-cache-dir \
    numpy==1.24.3 \
    mpmath==1.3.0 \
    sympy==1.12 \
    statsmodels==0.14.0 \
    qutip==4.7.3 \
    biopython==1.81 \
    rdkit==2023.9.1 \
    networkx==3.1 \
    scipy==1.11.3 \
    pandas==2.0.3 \
    pyyaml==6.0.1

# Copy application files
COPY . /app

# Set entrypoint
ENTRYPOINT ["python", "extract_tria_quotes_deepen_hermes.py"]

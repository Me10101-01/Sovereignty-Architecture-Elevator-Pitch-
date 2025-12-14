FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for rdkit and biopython
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for Phase 9
RUN pip install --no-cache-dir \
    numpy==1.24.3 \
    scipy==1.11.4 \
    mpmath==1.3.0 \
    sympy==1.12 \
    statsmodels==0.14.0 \
    qutip==4.7.3 \
    networkx==3.2.1 \
    pyyaml==6.0.1 \
    rdkit==2023.9.2 \
    biopython==1.81

# Copy application files
COPY . /app

# Default entrypoint
CMD ["python", "deepen_tria_explore_hermetic.py"]

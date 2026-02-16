FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for scientific computing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY phase12/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY phase12/ /app/phase12/
COPY docs/ /app/docs/
COPY benchmarks/ /app/benchmarks/

# Make script executable
RUN chmod +x /app/phase12/extract_tria_quotes_deepen_principles.py

# Set the entrypoint
ENTRYPOINT ["python3", "/app/phase12/extract_tria_quotes_deepen_principles.py"]

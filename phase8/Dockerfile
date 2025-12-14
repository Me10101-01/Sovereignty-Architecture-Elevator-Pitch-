FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Copy and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    -r /tmp/requirements.txt || \
    (echo "Warning: Some dependencies failed to install, attempting core packages..." && \
     pip install --no-cache-dir numpy scipy mpmath sympy statsmodels networkx pyyaml)

# Application files will be mounted via volume

# Set entrypoint
CMD ["python", "deepen_paracelsus_explore_alchemy.py"]

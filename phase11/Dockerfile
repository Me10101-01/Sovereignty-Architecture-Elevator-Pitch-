FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for scientific computing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY phase11/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt || \
    (echo "Warning: Installation with trusted hosts failed, attempting standard install..." && \
     pip install --no-cache-dir -r requirements.txt || \
     echo "Warning: Some packages may not be installed - check logs above")

# Copy application files
COPY . /app

# Set Python path
ENV PYTHONPATH=/app

CMD ["python", "integrate_signatures_explore_enochian.py"]

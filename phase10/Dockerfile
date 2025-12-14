FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for rdkit and scientific computing
RUN apt-get update && apt-get install -y \
    build-essential \
    libboost-all-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY phase10/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app

# Set entrypoint
CMD ["python", "deepen_tria_applications_explore_qabala.py"]

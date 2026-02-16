FROM python:3.11-slim

LABEL maintainer="Strategickhaos DAO LLC"
LABEL description="Moonlight Telemetry Agent - Session Intelligence Tracker"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY moonlight_agent.py .
COPY telemetry_schema.yaml .

# Create telemetry data directory
RUN mkdir -p /data/telemetry && \
    chmod 755 /data/telemetry

# Create non-root user
RUN useradd -m -u 1001 -s /bin/bash moonlight && \
    chown -R moonlight:moonlight /app /data

# Switch to non-root user
USER moonlight

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV TELEMETRY_DIR=/data/telemetry
ENV OBSIDIAN_VAULT=Athena
ENV BOARD_MEMBER="Claude Opus 4.5"
ENV KHAOSBASE_URL=http://khaosbase:8080
ENV AUTO_PUSH_TELEMETRY=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os; exit(0 if os.path.exists('/data/telemetry') else 1)"

# Run the agent
CMD ["python", "moonlight_agent.py"]

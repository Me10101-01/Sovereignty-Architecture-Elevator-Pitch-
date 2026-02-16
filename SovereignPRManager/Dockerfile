# SovereignPRManager Dockerfile
# Autonomous PR Review, Validation, and Merge Orchestration

FROM python:3.12-slim

# Labels
LABEL org.opencontainers.image.title="SovereignPRManager"
LABEL org.opencontainers.image.description="Autonomous PR orchestration with multi-AI review"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="Strategickhaos Swarm Intelligence"

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME=/app

# Create non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home appuser

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR ${APP_HOME}

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create log directory
RUN mkdir -p /var/log/sovereignprmanager && \
    chown -R appuser:appuser /var/log/sovereignprmanager

# Change ownership
RUN chown -R appuser:appuser ${APP_HOME}

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Default command: run the PR monitor
CMD ["python", "-m", "pr_monitor"]

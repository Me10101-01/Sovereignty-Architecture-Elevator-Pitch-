# GlyphSonix Resonance Core - Docker Image
# ===========================================
# 
# A containerized FlameLang audio synthesis engine for ancient text sonification
#
# Build: docker build -t strategickhaos/glyphsonix:latest .
# Run:   docker run -p 8080:8080 strategickhaos/glyphsonix:latest

FROM ubuntu:22.04

LABEL maintainer="Domenic Gabriel Garza <security@strategickhaos.ai>"
LABEL description="GlyphSonix Resonance Core - Ancient text to sonic DNA"
LABEL version="1.0.0"
LABEL org.strategickhaos.component="aetherforge"

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    python3 \
    python3-pip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Mojo (when available in container environment)
# Note: This requires Modular SDK access
# For now, this is a placeholder - actual Mojo installation
# will be added when containerized Mojo is available

# Create app directory
WORKDIR /app/glyphsonix

# Copy source files
COPY gsrc.mojo .
COPY examples.mojo .
COPY README.md .
COPY INTEGRATION.md .

# Create output directory for WAV files
RUN mkdir -p /app/output

# Environment variables
ENV GLYPHSONIX_CARRIER=432.0
ENV GLYPHSONIX_SAMPLE_RATE=48000
ENV GLYPHSONIX_OUTPUT_DIR=/app/output

# Expose port for API (future)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Volume for output files
VOLUME ["/app/output"]

# Note: The actual CMD will be added once Mojo containerization is available
# For now, this serves as the blueprint for deployment

CMD ["echo", "GlyphSonix Resonance Core - Container ready. Awaiting Mojo runtime integration."]

# Future CMD (when Mojo is containerized):
# CMD ["mojo", "run", "gsrc.mojo"]

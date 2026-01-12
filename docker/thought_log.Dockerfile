FROM python:3.12-slim

WORKDIR /app

# Copy necessary files
COPY src/cube_simulator/ ./cube_simulator/
COPY src/register_memory/ ./register_memory/
COPY src/entanglement_core/ ./entanglement_core/
COPY src/alu/ ./alu/
COPY configs/thought_log.yaml ./configs/

# Install dependencies (with fallback for certificate issues)
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    networkx matplotlib pyyaml numpy || \
    echo "Warning: Package installation may have failed. Container will use pre-installed packages if available."

# Set Python path
ENV PYTHONPATH=/app

# Default command: replay thought-log session
CMD ["python", "cube_simulator/type_promotion_cube.py"]

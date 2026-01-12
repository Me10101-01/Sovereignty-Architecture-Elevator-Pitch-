FROM python:3.12-slim

WORKDIR /app

# Copy cube simulator and dependencies
COPY src/cube_simulator/ ./cube_simulator/
COPY src/register_memory/ ./register_memory/
COPY src/entanglement_core/ ./entanglement_core/
COPY src/alu/ ./alu/
COPY configs/ ./configs/

# Install dependencies
RUN pip install --no-cache-dir networkx matplotlib pyyaml numpy

# Default command: replay thought-log session
CMD ["python", "-m", "register_memory.thought_log_overlay"]

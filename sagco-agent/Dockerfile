FROM python:3.12-slim

# Install sagco organism build deps
RUN apt-get update && apt-get install -y gcc make libm-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Build organism binary
COPY sagco-organism/ ./sagco-organism/
RUN make -C sagco-organism sagco

# Install agent deps
COPY sagco-agent/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY sagco-agent/ ./sagco-agent/

ENV SAGCO_BIN=/app/sagco-organism/sagco
ENV SAGCO_DATA=/app/sagco-organism/data

EXPOSE 8080
CMD ["python", "sagco-agent/sagco_agent.py", "--serve", "8080"]

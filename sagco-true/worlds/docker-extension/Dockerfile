# SAGCO-ORGANISM Docker Desktop Extension
# Builds the GTA dashboard as a native Docker Desktop extension.
# Copy contents of this directory into C:\Users\garza\my-extension\ and run:
#   docker build -t sagco/openworld:latest .
#   docker extension install sagco/openworld:latest

FROM --platform=$BUILDPLATFORM node:18-alpine AS ui-builder
WORKDIR /app/ui
COPY ui/ .
RUN if [ -f package.json ]; then npm install && npm run build 2>/dev/null || true; fi

FROM alpine:3.20
LABEL org.opencontainers.image.title="SAGCO Organism" \
      org.opencontainers.image.description="Fleet Dashboard — A place where the tools can find each other." \
      org.opencontainers.image.vendor="Strategickhaos DAO LLC" \
      com.docker.desktop.extension.api.version="0.3.3" \
      com.docker.desktop.extension.icon="https://raw.githubusercontent.com/Me10101-01/Sovereignty-Architecture-Elevator-Pitch-/main/sagco-true/worlds/docker-extension/sagco.svg" \
      com.docker.extension.screenshots='[{"alt":"SAGCO Fleet Dashboard","url":""}]' \
      com.docker.extension.detailed-description="SAGCO (Sovereignty Architecture Graph Command Orchestrator) fleet dashboard. Shows all nodes, wafer truth tests, PXE boot status, and the signal bus. No vendor owns the organism." \
      com.docker.extension.changelog="v0.1.0 — Initial organism deployment"

# Copy UI
COPY --from=ui-builder /app/ui/ /ui/
COPY ui/ /ui/
COPY metadata.json /metadata.json
COPY sagco.svg /sagco.svg

# The extension runs as a static UI — no backend process needed for v0.1.0
CMD ["/bin/sh", "-c", "echo 'SAGCO-ORGANISM v0.1.0 — fleet dashboard loaded'"]

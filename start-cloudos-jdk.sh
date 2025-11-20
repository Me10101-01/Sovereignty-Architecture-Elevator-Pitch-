#!/usr/bin/env bash
set -euo pipefail

case "${1:-}" in
  start)
    echo "Starting CloudOS JDK workspace (OpenJDK 21)..."
    docker compose up -d jdk-workspace
    docker compose logs -f jdk-workspace | grep -m 1 "Started" || true
    echo "Ready! http://java.localhost → app, :5005 → debug"
    ;;
  shell)
    docker exec -it cloudos-jdk bash
    ;;
  stop)
    docker compose down jdk-workspace
    ;;
  *)
    echo "Usage: $0 start|shell|stop"
    ;;
esac

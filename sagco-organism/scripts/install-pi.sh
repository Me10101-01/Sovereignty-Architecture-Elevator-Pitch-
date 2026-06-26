#!/usr/bin/env bash
# install-pi.sh — SAGCO Organism headless systemd install for Raspberry Pi
#
# Run this on the Pi after extracting the hydra tar.gz:
#   tar -xzf sagco-hydra-v1.0.tar.gz
#   cd sagco-hydra-v1.0
#   sudo ./scripts/install-pi.sh

set -euo pipefail

INSTALL_DIR="/opt/sagco-organism"
SERVICE_NAME="sagco-organism"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo ""
echo "  SAGCO Organism — Raspberry Pi Install"
echo "  ──────────────────────────────────────"

# Copy files
echo "  [1] Installing to ${INSTALL_DIR}..."
mkdir -p "${INSTALL_DIR}"/{data,logs}
cp "${REPO_DIR}/sagco"             "${INSTALL_DIR}/"
cp "${REPO_DIR}/exchanger_locator" "${INSTALL_DIR}/"
cp "${REPO_DIR}/run-hydra.sh"      "${INSTALL_DIR}/"
cp -r "${REPO_DIR}/data/"          "${INSTALL_DIR}/data/"

# Systemd service
echo "  [2] Installing systemd service..."
cat > /etc/systemd/system/${SERVICE_NAME}.service << SERVICE
[Unit]
Description=SAGCO Organism — Headless Field Dispatcher
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${INSTALL_DIR}
ExecStart=${INSTALL_DIR}/run-hydra.sh
StandardOutput=journal
StandardError=journal
User=pi

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable ${SERVICE_NAME}

echo "  [3] Done."
echo ""
echo "  Start:   sudo systemctl start ${SERVICE_NAME}"
echo "  Status:  sudo systemctl status ${SERVICE_NAME}"
echo "  Logs:    journalctl -u ${SERVICE_NAME} -f"
echo ""

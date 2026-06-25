#!/usr/bin/env bash
# tarbol.sh — SAGCO-Organism RPi / ARM64 package builder
# Usage: ./tarbol.sh [version] [target-triple]
# Example: ./tarbol.sh 0.2.0 aarch64-unknown-linux-gnu

set -euo pipefail

ORGANISM_VERSION="${1:-0.2.0}"
TARGET_ARCH="${2:-aarch64-unknown-linux-gnu}"
OUT_DIR="dist"
PKG="sagco-organism-${ORGANISM_VERSION}-${TARGET_ARCH}"
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🔥 tarbol: building ${PKG}"
echo "   workspace: ${WORKSPACE_ROOT}"
echo "   target:    ${TARGET_ARCH}"

# ── Cross-compilation check ──────────────────────────────────────────────────
if ! rustup target list --installed | grep -q "${TARGET_ARCH}"; then
    echo "   Installing Rust target ${TARGET_ARCH}..."
    rustup target add "${TARGET_ARCH}"
fi

# ── Build ────────────────────────────────────────────────────────────────────
cd "${WORKSPACE_ROOT}"

cargo build --release \
    --target "${TARGET_ARCH}" \
    -p sagco-organism \
    -p flame-ffi

# ── Package layout ───────────────────────────────────────────────────────────
mkdir -p "${OUT_DIR}/${PKG}"/{bin,config,k8s,drivers,systemd}

# Binaries
cp "target/${TARGET_ARCH}/release/sagco-organism" "${OUT_DIR}/${PKG}/bin/"

# Shared library (if built)
SO="target/${TARGET_ARCH}/release/libflamelang.so"
if [[ -f "${SO}" ]]; then
    cp "${SO}" "${OUT_DIR}/${PKG}/bin/"
    ln -sf libflamelang.so "${OUT_DIR}/${PKG}/bin/libflamelang.so.0"
fi

# Static library (if built)
A="target/${TARGET_ARCH}/release/libflamelang.a"
[[ -f "${A}" ]] && cp "${A}" "${OUT_DIR}/${PKG}/bin/"

# C header
cp "flame-ffi/include/flamelang.h" "${OUT_DIR}/${PKG}/bin/"

# K8s manifests
cp packaging/k8s/*.yaml "${OUT_DIR}/${PKG}/k8s/"

# systemd unit
cat > "${OUT_DIR}/${PKG}/systemd/sagco-organism.service" <<'UNIT'
[Unit]
Description=SAGCO-Organism sovereign compute daemon
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/sagco-organism
Restart=on-failure
RestartSec=5s
EnvironmentFile=/etc/sagco/organism.env
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
UNIT

# ── Genesis-signed SHA256 manifest ───────────────────────────────────────────
(cd "${OUT_DIR}/${PKG}/bin" && sha256sum *) > "${OUT_DIR}/${PKG}/SHA256SUMS"
echo "genesis|increment=3449|origin=2023-01-27T21:00:49Z" >> "${OUT_DIR}/${PKG}/SHA256SUMS"

# ── Bundle ───────────────────────────────────────────────────────────────────
tar -czf "${OUT_DIR}/${PKG}.tar.gz" -C "${OUT_DIR}" "${PKG}"

echo "✅ tarbol: ${OUT_DIR}/${PKG}.tar.gz"
sha256sum "${OUT_DIR}/${PKG}.tar.gz"

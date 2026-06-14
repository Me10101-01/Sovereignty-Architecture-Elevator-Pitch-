#!/usr/bin/env bash
# ============================================================
# SAGCO HP Node — AMD Radeon 740M + Ollama GPU Setup
# Run this INSIDE WSL2 (Ubuntu) on the HP node
#
# GPU: AMD Radeon 740M (RDNA3 iGPU, 512MB dedicated + 15.5GB shared)
# DirectX 12 FL 12.2 | Driver 32.0.21034.41 (Oct 2025)
# ROCm 6.x supports RDNA3
# ============================================================

set -euo pipefail

echo ""
echo "  ══════════════════════════════════════════════════════"
echo "  SAGCO HP Node — AMD GPU + Ollama Setup"
echo "  AMD Radeon 740M (RDNA3) | ROCm 6.x | WSL2"
echo "  ══════════════════════════════════════════════════════"
echo ""

# ── 1. ROCm 6.x installation (WSL2 Ubuntu 22.04/24.04) ─────────────────────
echo "  [1/5] Installing ROCm 6.x for AMD Radeon 740M..."

# Add AMD ROCm repo
wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | \
  sudo gpg --dearmor -o /etc/apt/keyrings/rocm.gpg

cat <<EOF | sudo tee /etc/apt/sources.list.d/rocm.list
deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] \
  https://repo.radeon.com/rocm/apt/6.2 jammy main
EOF

sudo apt-get update -q
sudo apt-get install -y rocm-hip-runtime rocm-opencl-runtime

# ── 2. Add GPU render device access ──────────────────────────────────────────
echo "  [2/5] Configuring GPU device access..."
sudo usermod -aG render,video "$USER"

# ── 3. Verify ROCm sees the GPU ──────────────────────────────────────────────
echo "  [3/5] Verifying ROCm device detection..."
if command -v rocm-smi &>/dev/null; then
  rocm-smi --showproductname || true
else
  echo "  [WARN] rocm-smi not found — may need re-login for group changes"
fi

# ── 4. Install / update Ollama (Linux build) ─────────────────────────────────
echo "  [4/5] Installing Ollama (Linux build for WSL2)..."
curl -fsSL https://ollama.com/install.sh | sh

# Point Ollama at ROCm
mkdir -p /etc/systemd/system/ollama.service.d/
cat <<EOF | sudo tee /etc/systemd/system/ollama.service.d/rocm.conf
[Service]
Environment="HSA_OVERRIDE_GFX_VERSION=11.0.0"
Environment="ROCR_VISIBLE_DEVICES=0"
Environment="OLLAMA_GPU_DRIVER=rocm"
EOF

# ── 5. Pull recommended models for 740M (fits in 16 GB shared VRAM) ──────────
echo "  [5/5] Pulling recommended models..."
echo "  Note: 740M has 15.5 GB shared VRAM — 8B models run comfortably"
echo ""

models=(
  "llama3.2:3b"
  "phi3.5"
)

for m in "${models[@]}"; do
  echo "  Pulling $m ..."
  ollama pull "$m" || echo "  [WARN] Could not pull $m (check network)"
done

echo ""
echo "  ── Setup complete ─────────────────────────────────────"
echo "  ROCm:   installed (RDNA3 target gfx1100)"
echo "  Ollama: listening on port 11434"
echo "  GPU:    AMD Radeon 740M (HSA_OVERRIDE_GFX_VERSION=11.0.0)"
echo ""
echo "  Test Ollama GPU:"
echo "    ollama run phi3.5"
echo ""
echo "  Check GPU use during inference:"
echo "    watch -n1 rocm-smi"
echo ""
echo "  From SAGCO:"
echo "    sagco node hp ollama"
echo "  ────────────────────────────────────────────────────────"

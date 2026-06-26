#!/usr/bin/env bash
# build-hydra.sh — SAGCO Organism Hydra Packager
#
# Builds the organism from source, then packages everything into
# sagco-hydra-v1.0.tar.gz for headless deployment (Raspberry Pi / Docker / bare metal)
#
# Usage:
#   ./scripts/build-hydra.sh             — build + package
#   ./scripts/build-hydra.sh --no-build  — package only (assumes already compiled)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VERSION="1.0"
TARNAME="sagco-hydra-v${VERSION}.tar.gz"
STAGEDIR="${REPO_ROOT}/sagco-hydra-v${VERSION}"

cd "${REPO_ROOT}"

# ── Build ──────────────────────────────────────────────────────────────────────
if [[ "${1:-}" != "--no-build" ]]; then
    echo ""
    echo "  [BUILD] Compiling SAGCO organism..."
    make -j"$(nproc)" all
    echo "  [BUILD] OK — sagco + exchanger_locator"
fi

# ── Stage ─────────────────────────────────────────────────────────────────────
echo "  [STAGE] Creating ${STAGEDIR}..."
rm -rf "${STAGEDIR}"
mkdir -p "${STAGEDIR}"/{src,data,scripts,logs,docs}

# Source
cp -r src/ "${STAGEDIR}/src/"

# Binaries
cp sagco                "${STAGEDIR}/"
cp exchanger_locator    "${STAGEDIR}/"

# Field data
cp data/sample_readings.csv         "${STAGEDIR}/data/"
cp data/asset_fingerprints.json     "${STAGEDIR}/data/"
cp data/pipe_survey_ca1648j.csv     "${STAGEDIR}/data/"
cp data/insulation_survey_ca1648j.csv "${STAGEDIR}/data/"

# Build artifacts
cp Makefile             "${STAGEDIR}/"
cp sagco-brick.toml     "${STAGEDIR}/"

# Install script
cp scripts/install-pi.sh "${STAGEDIR}/scripts/"

# Headless launcher
cat > "${STAGEDIR}/run-hydra.sh" << 'LAUNCHER'
#!/usr/bin/env bash
# run-hydra.sh — execute all organism heads in sequence
# Safe to run headless: no interactive prompts, all output to stdout

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"
mkdir -p logs

echo ""
echo "  ╔══════════════════════════════════════════════════════════╗"
echo "  ║   SAGCO ORGANISM v1.0 — HYDRA MODE                       ║"
echo "  ║   Dispatch: INPUT→lexer→parser→AST→router→subsystem→seal  ║"
echo "  ╚══════════════════════════════════════════════════════════╝"
echo ""

# HEAD 1 — GPS magnetic fingerprint
echo "  ── HEAD 1: exchanger_locator (ML-ORGANISM-005) ──"
./exchanger_locator data/sample_readings.csv data/asset_fingerprints.json

# HEAD 2 — Insulation coverage
echo "  ── HEAD 2: field insulation (ML-ORGANISM-003) ──"
./sagco field insulation --csv data/insulation_survey_ca1648j.csv

# HEAD 3 — Pipe weld survey
echo "  ── HEAD 3: field pipe-survey ──"
./sagco field pipe-survey --csv data/pipe_survey_ca1648j.csv

# HEAD 4 — GPS bearing (node A → node B on CA-1648 J run)
echo "  ── HEAD 4: gps bearing ──"
./sagco gps bearing \
    --lat1 27.810164 --lon1 -97.593503 \
    --lat2 27.810203 --lon2 -97.593470

# Seal invocation log with SHA-256
echo "  ── SEAL: signing invocation log ──"
if command -v sha256sum &>/dev/null; then
    sha256sum logs/invocations.log 2>/dev/null && echo "  [SEALED]" || echo "  [LOG EMPTY — first run]"
fi

echo ""
echo "  SAGCO HYDRA COMPLETE"
echo ""
LAUNCHER
chmod +x "${STAGEDIR}/run-hydra.sh"

# ── Manifest ───────────────────────────────────────────────────────────────────
MANIFEST="${STAGEDIR}/MANIFEST.txt"
{
    echo "SAGCO Organism Hydra v${VERSION}"
    echo "Built: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "BRICK: BRICK-020"
    echo ""
    echo "Binaries:"
    echo "  sagco                — main organism dispatcher"
    echo "  exchanger_locator    — standalone magnetic fingerprint tool"
    echo ""
    echo "Heads (all pass ERU PROVEN):"
    echo "  HEAD 1  ML-ORGANISM-005  exchanger_locator  — asset ID from µT fingerprint"
    echo "  HEAD 2  ML-ORGANISM-003  field insulation   — insulation coverage ERU"
    echo "  HEAD 3  ML-ORGANISM-003  field pipe-survey  — GPS-tagged weld inventory"
    echo "  HEAD 4  ML-ORGANISM-005  gps bearing        — haversine node-to-node"
    echo ""
    echo "Field data (validated CA-1648 J, LyondellBasell, 2026-06-26):"
    echo "  data/sample_readings.csv          — 9 compass readings, same GPS anchor"
    echo "  data/asset_fingerprints.json      — PO-HDRFE-1B fingerprint"
    echo "  data/pipe_survey_ca1648j.csv      — W1-W9 + flary/reducer/LB weld inventory"
    echo "  data/insulation_survey_ca1648j.csv — 3 insulation zones, all PROVEN"
    echo ""
    echo "Run:  ./run-hydra.sh"
    echo ""
    echo "Files:"
    find . -type f | sort
} > "${MANIFEST}"

# ── Pack ───────────────────────────────────────────────────────────────────────
echo "  [PACK] Creating ${TARNAME}..."
cd "$(dirname "${STAGEDIR}")"
tar -czf "${REPO_ROOT}/${TARNAME}" "$(basename "${STAGEDIR}")"
rm -rf "${STAGEDIR}"

SHA=$(sha256sum "${REPO_ROOT}/${TARNAME}" | cut -d' ' -f1)
SIZE=$(du -sh "${REPO_ROOT}/${TARNAME}" | cut -f1)

echo ""
echo "  ╔══════════════════════════════════════════════════════════╗"
echo "  ║   SAGCO HYDRA PACKAGED                                    ║"
echo "  ╠══════════════════════════════════════════════════════════╣"
echo "  ║  File:    ${TARNAME}"
echo "  ║  Size:    ${SIZE}"
echo "  ║  SHA-256: ${SHA}"
echo "  ╚══════════════════════════════════════════════════════════╝"
echo ""
echo "  Deploy to Pi:"
echo "    scp ${TARNAME} pi@<host>:~/"
echo "    ssh pi@<host> 'tar -xzf ${TARNAME} && ./sagco-hydra-v${VERSION}/run-hydra.sh'"
echo ""

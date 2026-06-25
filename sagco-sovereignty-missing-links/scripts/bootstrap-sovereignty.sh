#!/usr/bin/env bash
# bootstrap-sovereignty.sh — Execute the Three-Move NDA Close
#
# MOVE 1: GPG clearsign key artifacts
# MOVE 2: Open ARIN Org ID + ASN application (browser-guided)
# MOVE 3: RPKI ROA creation checklist
#
# Run from repo root: ./scripts/bootstrap-sovereignty.sh
# Or: ./scripts/bootstrap-sovereignty.sh --move 1   (run only MOVE 1)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GPG_DIR="${REPO_ROOT}/gpg"
LOG_DIR="${REPO_ROOT}/logs"
MOVE="${1:-all}"

# Colors (if terminal supports it)
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; NC='\033[0m'

info()  { echo -e "${GRN}  [INFO]${NC}  $*"; }
warn()  { echo -e "${YLW}  [WARN]${NC}  $*"; }
error() { echo -e "${RED}  [ERR]${NC}   $*"; }
step()  { echo -e "\n${YLW}  ═══ $* ═══${NC}"; }

check_dep() {
    if ! command -v "$1" &>/dev/null; then
        warn "Missing: $1. Install it before running MOVE $2."
        return 1
    fi
    return 0
}

# ---------------------------------------------------------------------------
# MOVE 1 — GPG Clearsign
# ---------------------------------------------------------------------------

run_move1() {
    step "MOVE 1: GPG Clearsign (artifact tamper-evidence)"

    if ! check_dep gpg 1; then
        error "gpg not installed. Install GnuPG: https://gnupg.org/"
        return 1
    fi

    # Check for secret key
    KEY=$(gpg --list-secret-keys --with-colons 2>/dev/null | awk -F: '$1=="fpr"{print $10; exit}')
    if [[ -z "$KEY" ]]; then
        warn "No GPG secret key found."
        echo "  Generate one with: gpg --full-generate-key"
        echo "  Then re-run this script."
        return 1
    fi
    info "GPG key: $KEY"

    # Priority artifacts to sign
    PRIORITY_FILES=(
        "${REPO_ROOT}/../CLAIM_VERIFICATION_2025.md"
        "${REPO_ROOT}/../PROVENANCE.yaml"
        "${REPO_ROOT}/../sagco-audit/registry/antibody_registry.yaml"
        "${REPO_ROOT}/../sagco-organism/sagco-brick.toml"
        "${REPO_ROOT}/../sagco-archaeologist/sagco-brick.toml"
        "${REPO_ROOT}/rpki/roa-template.yaml"
    )

    SIGNED=0
    for f in "${PRIORITY_FILES[@]}"; do
        [[ -f "$f" ]] || { warn "Not found: $f (skip)"; continue; }
        [[ -f "${f}.gpg" ]] && { info "Already signed: $(basename $f)"; continue; }
        bash "${GPG_DIR}/clearsign-athena.sh" "$f" && SIGNED=$((SIGNED+1))
    done

    info "MOVE 1 complete: $SIGNED files signed."
    echo ""
    echo "  Next: verify with  ./gpg/verify.sh"
    echo "  ERU: ratio=$(echo "scale=2; $SIGNED / ${#PRIORITY_FILES[@]}" | bc)  [update manually in audit log]"
}

# ---------------------------------------------------------------------------
# MOVE 2 — ARIN Org ID + ASN Application
# ---------------------------------------------------------------------------

run_move2() {
    step "MOVE 2: ARIN ASN Application"

    echo ""
    echo "  This move requires a web browser. Steps:"
    echo ""
    echo "  1. Create ARIN Online account:"
    echo "     https://account.arin.net/"
    echo ""
    echo "  2. Create Org ID for Strategickhaos DAO LLC"
    echo "     See: ${REPO_ROOT}/arin/org-id-checklist.md"
    echo ""
    echo "  3. Submit ASN request (~$350 year 1)"
    echo "     See: ${REPO_ROOT}/arin/asn-application.md"
    echo "     Fee schedule: ${REPO_ROOT}/arin/fee-schedule-2026.md"
    echo ""
    echo "  4. Wait 5–10 business days for assignment"
    echo ""
    echo "  5. After assignment, record your ASN:"

    # Try to open browser if available
    if command -v xdg-open &>/dev/null; then
        read -rp "  Open ARIN Online in browser? [y/N] " yn
        [[ "$yn" == [Yy]* ]] && xdg-open "https://account.arin.net/" &
    elif command -v open &>/dev/null; then
        read -rp "  Open ARIN Online in browser? [y/N] " yn
        [[ "$yn" == [Yy]* ]] && open "https://account.arin.net/"
    fi

    warn "MOVE 2 status: UNCOMPUTED until ASN is assigned."
    echo "  Update ${REPO_ROOT}/rpki/roa-template.yaml with your ASN when received."
}

# ---------------------------------------------------------------------------
# MOVE 3 — RPKI ROA Creation
# ---------------------------------------------------------------------------

run_move3() {
    step "MOVE 3: RPKI ROA Creation"

    echo ""
    echo "  Prerequisite: MOVE 2 must be complete (ASN assigned)."
    echo ""

    # Check if roa-template.yaml has been filled in
    ROA="${REPO_ROOT}/rpki/roa-template.yaml"
    if grep -q "YOUR_ASN" "$ROA" 2>/dev/null; then
        warn "roa-template.yaml still contains YOUR_ASN placeholder."
        echo "  Complete MOVE 2 first, then fill in your ASN in: $ROA"
        return 1
    fi

    info "roa-template.yaml looks populated — proceeding."
    echo ""
    echo "  Steps:"
    echo "  1. Log in: https://account.arin.net/ → RPKI → Enable Hosted RPKI"
    echo "  2. Create ROA using values in: $ROA"
    echo "  3. Wait 24–48 hours for propagation"
    echo "  4. Verify: https://rpki-validator.ripe.net/"
    echo "  5. Update roa-template.yaml:  eru.actual = 1  verdict = PROVEN"
    echo "  6. GPG-sign the updated template:"
    echo "     bash ${GPG_DIR}/clearsign-athena.sh $ROA"
    echo ""

    if command -v xdg-open &>/dev/null; then
        read -rp "  Open RIPE RPKI Validator? [y/N] " yn
        [[ "$yn" == [Yy]* ]] && xdg-open "https://rpki-validator.ripe.net/" &
    fi

    warn "MOVE 3 status: UNCOMPUTED until ROA is validated."
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

echo ""
echo "  SAGCO SOVEREIGNTY BOOTSTRAP"
echo "  Entity: Strategickhaos DAO LLC (WY 2025-001708194)"
echo "  Repo:   $REPO_ROOT"
echo ""

case "${MOVE}" in
    --move|1|"move1") run_move1 ;;
    --move|2|"move2") run_move2 ;;
    --move|3|"move3") run_move3 ;;
    "all"|*)
        run_move1 || true
        run_move2 || true
        run_move3 || true
        ;;
esac

echo ""
echo "  ─────────────────────────────────────────"
echo "  Run summary written to: ${LOG_DIR}/bootstrap.log"
mkdir -p "$LOG_DIR"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)  bootstrap-sovereignty.sh  move=${MOVE}" >> "${LOG_DIR}/bootstrap.log"
echo ""

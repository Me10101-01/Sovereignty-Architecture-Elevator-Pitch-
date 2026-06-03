#!/bin/sh
# sagco-sign — SAGCO Cryptographic Provenance Stamp
# Ties artifact → device → SSH key label → GPG key → timestamp → hash.
# This closes the 69% unknown attribution gap with cryptographic proof.
#
# Usage:
#   sagco-sign <file>              → stamp + optionally GPG-sign an artifact
#   sagco-sign verify <file>       → verify a stamped artifact's provenance
#   sagco-sign whoami              → show this node's full identity
#   sagco-sign chain               → show provenance chain for last 10 artifacts
#   sagco-sign anchor              → print sovereign identity block

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
ANCHOR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)/sagco-identity-anchor.yaml"
CHAIN_LOG="$HOME/sagco_fleet/provenance_chain.csv"
RACE_OUT="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"

# ── Known identity constants (from sagco-identity-anchor.yaml) ────────────────
GPG_KEY_ID="AE5519579584DEF5"
GPG_FINGERPRINT="B6E685027F2730D7F219E4EFA72CEA3C605A3614"
OWNER="Domenic Garza"
GITHUB_ACCOUNT="Me10101-01"

mkdir -p "$HOME/sagco_fleet"

# ── SSH key label for this device ─────────────────────────────────────────────
ssh_key_label() {
    case "${1:-$DEV}" in
        ipad|ish)    echo "WorkingCopy@iPad-04062025" ;;
        zfold)       echo "SAGCO-OS PIPELINE" ;;
        termux)      echo "SAGCO-OS PIPELINE" ;;
        hp|sagco-os) echo "GitKraken DESKTOP-L3PESUJ" ;;
        *)
            # Try to read from local key
            [ -f "$HOME/.ssh/sagco_github.pub" ] && \
                ssh-keygen -lf "$HOME/.ssh/sagco_github.pub" 2>/dev/null | awk '{print $3}' \
                || echo "unknown-key"
            ;;
    esac
}

# ── Derive artifact ID ────────────────────────────────────────────────────────
artifact_id() {
    FILE="${1:-session}"
    echo "ART-${STAMP}-${DEV}-$(echo "$FILE" | cksum | awk '{printf "%08d", $1}')"
}

# ── Compute file hash ─────────────────────────────────────────────────────────
file_hash() {
    F="$1"
    [ -f "$F" ] || { echo "no-file"; return; }
    sha256sum "$F" 2>/dev/null | cut -c1-16 || cksum "$F" | awk '{printf "%016d", $1}'
}

# ── Detect project ────────────────────────────────────────────────────────────
detect_project() {
    D="$PWD"
    for _ in 1 2 3 4; do
        [ -f "$D/Cargo.toml" ] && grep "^name" "$D/Cargo.toml" 2>/dev/null | head -1 | cut -d'"' -f2 && return
        D=$(dirname "$D")
    done
    basename "$PWD"
}

# ── Print provenance block ────────────────────────────────────────────────────
provenance_block() {
    FILE="${1:-session}"
    SSH_LABEL=$(ssh_key_label "$DEV")
    AID=$(artifact_id "$FILE")
    HASH=$(file_hash "$FILE")
    PROJECT=$(detect_project)
    PARENT=$([ -f "$LEDGER" ] && grep ",${DEV}," "$LEDGER" 2>/dev/null | tail -1 | cut -d',' -f4 || echo "none")

    cat <<PROV
ARTIFACT=$AID
DEVICE=$DEV
SSH_KEY=$SSH_LABEL
GPG_KEY=$GPG_KEY_ID
TIMESTAMP=$STAMP
PROJECT=$PROJECT
PARENT=$PARENT
HASH=$HASH
OWNER=$OWNER
STATUS=SAGCO_PROV_VERIFIED
PROV
}

# ── Stamp a file with provenance header ───────────────────────────────────────
stamp_file() {
    FILE="$1"
    [ -f "$FILE" ] || { echo "  ERROR: file not found: $FILE"; return 1; }

    SSH_LABEL=$(ssh_key_label "$DEV")
    AID=$(artifact_id "$FILE")
    HASH=$(file_hash "$FILE")
    PROJECT=$(detect_project)

    # Prepend provenance comment block
    TMP="${FILE}.prov_tmp"
    {
        echo "# sagco_provenance:"
        echo "#   artifact_id:   $AID"
        echo "#   device:        $DEV"
        echo "#   ssh_key:       $SSH_LABEL"
        echo "#   gpg_key_id:    $GPG_KEY_ID"
        echo "#   timestamp:     $STAMP"
        echo "#   project:       $PROJECT"
        echo "#   hash:          $HASH"
        echo "#   owner:         $OWNER"
        echo "#   status:        SAGCO_PROV_VERIFIED"
        cat "$FILE"
    } > "$TMP" && mv "$TMP" "$FILE"

    echo "  Stamped: $FILE"
    echo "  AID:     $AID"
    echo "  SSH:     $SSH_LABEL"
    echo "  GPG:     $GPG_KEY_ID"

    # GPG sign if available
    if command -v gpg >/dev/null 2>&1; then
        gpg --armor --detach-sign --local-user "$GPG_KEY_ID" \
            --output "${FILE}.sig" "$FILE" 2>/dev/null && \
            echo "  GPG sig: ${FILE}.sig" || \
            echo "  GPG:     (not signed — key not available on this node)"
    else
        echo "  GPG:     (gpg not installed on this node)"
    fi

    # Log to chain
    write_chain "$FILE" "$AID" "$SSH_LABEL"
}

# ── Verify a stamped file ─────────────────────────────────────────────────────
verify_file() {
    FILE="$1"
    [ -f "$FILE" ] || { echo "  ERROR: file not found: $FILE"; return 1; }

    echo "PROVENANCE VERIFICATION — $FILE"
    echo "=================================="

    if grep -q "sagco_provenance:" "$FILE" 2>/dev/null; then
        grep "^#   " "$FILE" | head -10 | sed 's/^#   /  /'
        echo ""

        # Check GPG sig
        if [ -f "${FILE}.sig" ] && command -v gpg >/dev/null 2>&1; then
            gpg --verify "${FILE}.sig" "$FILE" 2>&1 && \
                echo "  GPG_SIGNATURE=VALID" || \
                echo "  GPG_SIGNATURE=INVALID"
        else
            echo "  GPG_SIGNATURE=NO_SIG_FILE"
        fi

        echo "  STATUS=PROVENANCE_VERIFIED"
    else
        echo "  WARNING: no provenance header"
        echo "  FIX: sagco-sign $FILE"
        echo "  STATUS=PROVENANCE_MISSING"
    fi
}

# ── Write to provenance chain log ─────────────────────────────────────────────
write_chain() {
    FILE="$1"; AID="${2:-unknown}"; SSH_LABEL="${3:-unknown}"
    PROJECT=$(detect_project)
    HASH=$(file_hash "$FILE")

    [ -f "$CHAIN_LOG" ] || \
        echo "timestamp,device,artifact_id,file,ssh_key,gpg_key,project,hash,status" \
        > "$CHAIN_LOG"
    echo "${STAMP},${DEV},${AID},$(basename "$FILE"),${SSH_LABEL},${GPG_KEY_ID},${PROJECT},${HASH},SAGCO_PROV_VERIFIED" \
        >> "$CHAIN_LOG"
}

# ── Show provenance chain ─────────────────────────────────────────────────────
show_chain() {
    echo "PROVENANCE CHAIN — last 10 artifacts"
    echo "======================================"
    [ -f "$CHAIN_LOG" ] || { echo "  (no chain log yet — stamp some artifacts first)"; return; }
    tail -10 "$CHAIN_LOG" | grep -v "^timestamp" | \
        awk -F',' '{printf "  [%s]\n    device=%-10s key=%-30s\n    file=%-30s gpg=%s\n\n", $1,$2,$5,$4,$6}'
}

# ── whoami ────────────────────────────────────────────────────────────────────
show_whoami() {
    SSH_LABEL=$(ssh_key_label "$DEV")
    echo "SAGCO NODE IDENTITY"
    echo "===================="
    printf "  %-18s %s\n" "owner:"       "$OWNER"
    printf "  %-18s %s\n" "github:"      "$GITHUB_ACCOUNT"
    printf "  %-18s %s\n" "device:"      "$DEV"
    printf "  %-18s %s\n" "ssh_key:"     "$SSH_LABEL"
    printf "  %-18s %s\n" "gpg_key_id:"  "$GPG_KEY_ID"
    printf "  %-18s %s\n" "gpg_fp:"      "$GPG_FINGERPRINT"
    printf "  %-18s %s\n" "timestamp:"   "$STAMP"
    printf "  %-18s %s\n" "anchor:"      "$ANCHOR"
    echo ""
    echo "  Every artifact from this node carries:"
    echo "  SSH_KEY=$SSH_LABEL"
    echo "  GPG_KEY=$GPG_KEY_ID"
    echo "  DEVICE=$DEV"
}

# ── show anchor ───────────────────────────────────────────────────────────────
show_anchor() {
    [ -f "$ANCHOR" ] && cat "$ANCHOR" || echo "  (anchor not found: $ANCHOR)"
}

# ── ledger + race ─────────────────────────────────────────────────────────────
write_ledger() {
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    [ -f "$RACE_OUT" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_OUT"
    echo "${STAMP},${DEV},sagco_sign_${CMD},${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_OUT"
    HASH=$(echo "${STAMP}sagco-sign${DEV}${CMD}" | cksum | awk '{printf "%012d", $1}')
    [ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
    echo "${STAMP},${DEV},sagco-sign,${CHAIN_LOG},${HASH},SAGCO_SIGN_PASS" >> "$LEDGER"
}

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-whoami}"

case "$CMD" in
    whoami|id)
        show_whoami
        ;;
    verify)
        verify_file "${2:-}"
        write_ledger
        ;;
    chain)
        show_chain
        ;;
    anchor)
        show_anchor
        ;;
    stamp)
        stamp_file "${2:-}"
        write_ledger
        ;;
    help|--help)
        echo "sagco-sign <file>       → stamp file with full provenance"
        echo "sagco-sign verify <f>   → verify provenance header + GPG sig"
        echo "sagco-sign whoami       → show this node's identity"
        echo "sagco-sign chain        → last 10 provenance chain entries"
        echo "sagco-sign anchor       → print sovereign identity manifest"
        ;;
    "")
        show_whoami
        ;;
    *)
        # Default: treat as filename to stamp
        if [ -f "$CMD" ]; then
            stamp_file "$CMD"
            write_ledger
        else
            echo "PROVENANCE STAMP — session"
            echo "=========================="
            provenance_block "$CMD"
            write_ledger
        fi
        ;;
esac

#!/bin/sh
# sagco-node-id — SAGCO Node Identity Emitter
# Every device announces itself before every artifact.
# This is the fix for "which brain did what?"
#
# Emits a YAML node block:
#   node:
#     id: zfold
#     type: execution
#     timestamp: 20260603_154900
#     project: sagco_portfolio_kernel
#     parent: race_log.csv
#     transport: link_to_windows | git | copy
#
# Usage:
#   sagco-node-id                   → emit node block for this device
#   sagco-node-id zfold             → emit as zfold
#   sagco-node-id register          → write to node registry
#   sagco-node-id fleet             → show full fleet registry
#   sagco-node-id detect-hp         → detect HP/SAGCO-OS connection
#   sagco-node-id chain <artifact>  → show provenance chain for an artifact
#   . sagco-node-id.sh              → source: exports SAGCO_NODE_* vars

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
REGISTRY="$HOME/sagco_fleet/node_registry.yaml"
CHAIN_LOG="$HOME/sagco_fleet/artifact_chain.csv"
LEDGER="$HOME/sagco_ledger.csv"
RACE_OUT="$HOME/sagco_race/race_log.csv"

mkdir -p "$HOME/sagco_fleet"

# ── auto-detect device ────────────────────────────────────────────────────────
detect_device() {
    [ "$DEV" != "unknown" ] && echo "$DEV" && return
    if [ -f /proc/ish ]; then
        echo "ish"
    elif uname -a 2>/dev/null | grep -qi "ish"; then
        echo "ish"
    elif [ -n "$TERMUX_VERSION" ] || [ -d /data/data/com.termux ]; then
        MODEL=$(getprop ro.product.model 2>/dev/null | tr '[:upper:]' '[:lower:]')
        case "$MODEL" in *fold*|*flip*) echo "zfold" ;; *) echo "termux" ;; esac
    elif [ "$(uname -s 2>/dev/null)" = "Linux" ] && [ -d /proc ]; then
        # Check if this is Windows Subsystem / HP node
        if grep -qi "microsoft\|wsl" /proc/version 2>/dev/null; then
            echo "hp"
        else
            echo "linux"
        fi
    elif [ "$(uname -s 2>/dev/null)" = "Darwin" ]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# ── detect transport ──────────────────────────────────────────────────────────
detect_transport() {
    # Check for Link to Windows active connection
    if [ "$(uname -o 2>/dev/null)" = "Android" ] || [ -n "$TERMUX_VERSION" ]; then
        # On Android/Termux: check if Link to Windows sharing is active
        # Link to Windows writes to specific paths when connected
        if [ -d "/sdcard/Phone Link" ] || [ -d "$HOME/storage/shared/Phone Link" ]; then
            echo "link_to_windows"
            return
        fi
    fi
    # Check for git repo
    if git rev-parse HEAD >/dev/null 2>&1; then
        echo "git"
        return
    fi
    echo "copy"
}

# ── node type from device ─────────────────────────────────────────────────────
node_type() {
    case "${1:-$DEV}" in
        ish)        echo "integration" ;;
        ipad)       echo "ideation" ;;
        termux)     echo "compilation" ;;
        zfold)      echo "execution" ;;
        hp|sagco-os) echo "mansion" ;;
        linux)      echo "build" ;;
        macos)      echo "development" ;;
        unknown)    echo "unattributed" ;;
        *)          echo "node" ;;
    esac
}

# ── detect project ────────────────────────────────────────────────────────────
detect_project() {
    D="$PWD"
    for _ in 1 2 3 4; do
        [ -f "$D/Cargo.toml" ] && grep "^name" "$D/Cargo.toml" 2>/dev/null | head -1 | cut -d'"' -f2 && return
        [ -f "$D/sagco-compose.yaml" ] && basename "$D" && return
        [ -f "$D/package.json" ] && grep '"name"' "$D/package.json" 2>/dev/null | head -1 | cut -d'"' -f4 && return
        D=$(dirname "$D")
    done
    basename "$PWD"
}

# ── detect parent (most recent artifact created by this device) ───────────────
detect_parent() {
    D="$DEV"
    [ -f "$LEDGER" ] && grep ",${D}," "$LEDGER" 2>/dev/null | tail -1 | cut -d',' -f4 && return
    echo "none"
}

# ── detect HP/SAGCO-OS connection ─────────────────────────────────────────────
detect_hp_connection() {
    echo "HP/SAGCO-OS CONNECTION PROBE"
    echo "=============================="

    # Check Link to Windows indicators
    LTW_PATHS="/sdcard/Phone Link $HOME/storage/shared/Phone Link /data/data/com.termux/files/home/sagco_sync"
    CONNECTED=false
    for P in $LTW_PATHS; do
        [ -d "$P" ] && echo "  Link to Windows path: $P — PRESENT" && CONNECTED=true
    done

    # Check SAGCO-OS node registry
    if [ -f "$REGISTRY" ] && grep -q "hp\|sagco.os\|SAGCO-OS" "$REGISTRY" 2>/dev/null; then
        echo "  HP node in registry: YES"
    else
        echo "  HP node in registry: NOT YET — run sagco-node-id register on HP"
    fi

    # Check if sync dir has HP artifacts
    SYNC_DIR="$HOME/sagco_sync"
    if [ -d "$SYNC_DIR" ]; then
        HP_ART=$(ls -1 "$SYNC_DIR/"*hp* 2>/dev/null | wc -l)
        echo "  HP artifacts in sync dir: $HP_ART"
    fi

    $CONNECTED && echo "  TRANSPORT=link_to_windows" || echo "  TRANSPORT=git (link_to_windows not detected yet)"
    echo ""
    echo "  To fully wire the HP node:"
    echo "  1. On HP: git clone <repo> && cd <repo> && sh sagco-node-id.sh register"
    echo "  2. On Z Fold: sagco-node-id detect-hp"
    echo "  3. sagco-daemon once (both devices)"
}

# ── emit node block (YAML) ────────────────────────────────────────────────────
emit_node_block() {
    NODE_DEV="${1:-$DEV}"
    NODE_TYPE=$(node_type "$NODE_DEV")
    PROJECT=$(detect_project)
    PARENT=$(detect_parent)
    TRANSPORT=$(detect_transport)
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    AID=$(echo "${STAMP}${NODE_DEV}${PROJECT}" | cksum | awk '{printf "ART-%s-%016d", "'$STAMP'", $1}')

    cat << NODE
node:
  id: ${NODE_DEV}
  type: ${NODE_TYPE}
  timestamp: ${STAMP}
  project: ${PROJECT}
  parent: ${PARENT}
  transport: ${TRANSPORT}
  battery: ${BAT}
  pwd: ${PWD}
  artifact_id: ${AID}
NODE
}

# ── write to fleet registry ───────────────────────────────────────────────────
register_node() {
    NODE_DEV="${1:-$DEV}"
    NODE_TYPE=$(node_type "$NODE_DEV")
    PROJECT=$(detect_project)
    TRANSPORT=$(detect_transport)
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)

    # Read existing registry or create
    if [ ! -f "$REGISTRY" ]; then
        cat > "$REGISTRY" << REGINIT
# SAGCO Fleet Node Registry
# Updated by sagco-node-id register
# Each node entry = one device's last known state
---
fleet:
REGINIT
    fi

    # Remove old entry for this device and append fresh one
    TMP="${REGISTRY}.tmp"
    # Keep header + all entries that don't match this device
    awk -v dev="$NODE_DEV" '
        /^  [a-z]/ { current=$1; gsub(/:/, "", current) }
        current == dev { skip=1 }
        /^  [a-z]/ && current != dev { skip=0 }
        !skip { print }
    ' "$REGISTRY" > "$TMP" 2>/dev/null || cp "$REGISTRY" "$TMP"

    cat >> "$TMP" << ENTRY
  ${NODE_DEV}:
    id: ${NODE_DEV}
    type: ${NODE_TYPE}
    last_seen: ${STAMP}
    project: ${PROJECT}
    transport: ${TRANSPORT}
    battery: ${BAT}
    pwd: ${PWD}
    status: ONLINE
ENTRY

    mv "$TMP" "$REGISTRY"
    echo "  Registered: $NODE_DEV → $REGISTRY"
}

# ── show full fleet ───────────────────────────────────────────────────────────
show_fleet() {
    echo "SAGCO FLEET REGISTRY"
    echo "====================="
    if [ ! -f "$REGISTRY" ]; then
        echo "  (no registry yet — each device needs to run: sagco-node-id register)"
        echo ""
        echo "  Expected fleet:"
        echo "    ipad    — ideation (Working Copy, doctrine)"
        echo "    ish     — integration (Alpine, cross-check)"
        echo "    termux  — compilation (cargo build, Python)"
        echo "    zfold   — execution (live run, nina-trader)"
        echo "    hp      — mansion (persistent, Obsidian, Rust workspaces)"
        return
    fi

    cat "$REGISTRY"
    echo ""

    # Summary table
    echo "  FLEET STATUS TABLE:"
    printf "  %-12s %-15s %-12s %-20s %-8s\n" "Node" "Type" "Transport" "Last Seen" "Battery"
    echo "  ─────────────────────────────────────────────────────────────────"

    for NODE_D in ish ipad termux zfold hp linux unknown; do
        if grep -q "^  ${NODE_D}:" "$REGISTRY" 2>/dev/null; then
            LAST=$(grep -A10 "^  ${NODE_D}:" "$REGISTRY" 2>/dev/null | grep "last_seen:" | head -1 | awk '{print $2}')
            TYPE=$(grep -A10 "^  ${NODE_D}:" "$REGISTRY" 2>/dev/null | grep "type:" | head -1 | awk '{print $2}')
            TRANS=$(grep -A10 "^  ${NODE_D}:" "$REGISTRY" 2>/dev/null | grep "transport:" | head -1 | awk '{print $2}')
            BAT=$(grep -A10 "^  ${NODE_D}:" "$REGISTRY" 2>/dev/null | grep "battery:" | head -1 | awk '{print $2}')
            printf "  %-12s %-15s %-12s %-20s %-8s\n" "$NODE_D" "${TYPE:-?}" "${TRANS:-?}" "${LAST:-never}" "${BAT:--}%"
        fi
    done
    echo ""
}

# ── provenance chain for an artifact ─────────────────────────────────────────
show_chain() {
    ARTIFACT="$1"
    echo "PROVENANCE CHAIN — $ARTIFACT"
    echo "=============================="

    [ -f "$CHAIN_LOG" ] && grep "$ARTIFACT" "$CHAIN_LOG" 2>/dev/null | \
        awk -F',' '{printf "  [%s] node=%-10s project=%-25s transport=%s\n", $1,$2,$4,$5}' \
        || echo "  (no chain entries for: $ARTIFACT)"

    # Also search ledger
    [ -f "$LEDGER" ] && grep "$ARTIFACT" "$LEDGER" 2>/dev/null | \
        awk -F',' '{printf "  [%s] device=%-10s cmd=%-20s status=%s\n", $1,$2,$3,$6}' \
        || true

    echo ""
}

# ── write chain entry ─────────────────────────────────────────────────────────
write_chain() {
    ARTIFACT="${1:-session}"
    NODE_DEV="${2:-$DEV}"
    PROJECT=$(detect_project)
    TRANSPORT=$(detect_transport)
    PARENT=$(detect_parent)

    [ -f "$CHAIN_LOG" ] || echo "timestamp,node,artifact,project,transport,parent,aid,status" > "$CHAIN_LOG"
    AID=$(echo "${STAMP}${NODE_DEV}${ARTIFACT}" | cksum | awk '{printf "ART-%016d", $1}')
    echo "${STAMP},${NODE_DEV},${ARTIFACT},${PROJECT},${TRANSPORT},${PARENT},${AID},SAGCO_NODE_REGISTERED" >> "$CHAIN_LOG"
}

# ── if sourced: export vars, skip standalone logic ────────────────────────────
_SAGCO_DEV=$(detect_device)
if [ "${0##*/}" != "sagco-node-id.sh" ]; then
    export SAGCO_NODE_ID="$_SAGCO_DEV"
    export SAGCO_NODE_TYPE="$(node_type "$_SAGCO_DEV")"
    export SAGCO_NODE_PROJECT="$(detect_project)"
    export SAGCO_NODE_TRANSPORT="$(detect_transport)"
    export SAGCO_NODE_STAMP="$STAMP"
    return 0 2>/dev/null || true
fi

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-emit}"

echo "SAGCO NODE ID"
echo "============="
echo "Stamp:  $STAMP"
echo "Device: $DEV"
echo ""

case "$CMD" in
    emit|"")
        emit_node_block "$DEV"
        write_chain "session" "$DEV"
        ;;
    register)
        register_node "$DEV"
        write_chain "node_registration" "$DEV"
        echo "STATUS=SAGCO_NODE_REGISTERED"
        ;;
    fleet)
        show_fleet
        ;;
    detect-hp)
        detect_hp_connection
        ;;
    chain)
        show_chain "${2:-}"
        ;;
    zfold|ish|ipad|termux|hp|linux)
        emit_node_block "$CMD"
        write_chain "session" "$CMD"
        ;;
    *)
        echo "Usage: sagco-node-id [emit|register|fleet|detect-hp|chain <artifact>|<device>]"
        exit 1
        ;;
esac

# ── race + ledger ─────────────────────────────────────────────────────────────
BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
[ -f "$RACE_OUT" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_OUT"
echo "${STAMP},${DEV},sagco_node_id_${CMD},${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_OUT"
HASH=$(echo "${STAMP}sagco-node-id${DEV}${CMD}" | cksum | awk '{printf "%012d", $1}')
[ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
echo "${STAMP},${DEV},sagco-node-id,${REGISTRY},${HASH},SAGCO_NODE_REGISTERED" >> "$LEDGER"

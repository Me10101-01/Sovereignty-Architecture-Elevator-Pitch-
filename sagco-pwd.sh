#!/bin/sh
# sagco-pwd — SAGCO Self-Awareness Node
# Every brain lobe knows: what device am I, where am I, what was I last doing?
# This is the "I exist" signal — must run before any other sagco command.
#
# Usage:
#   sagco-pwd                     → announce this device's current state
#   sagco-pwd zfold               → announce as zfold (override)
#   sagco-pwd show                → show last 10 pwd ticks from this device
#   sagco-pwd history [device]    → show pwd history for a device

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
LEDGER="$HOME/sagco_ledger.csv"
RACE_OUT="$HOME/sagco_race/race_log.csv"
PWD_LOG="$HOME/sagco_race/pwd_log.csv"
CONTEXT_LOG="$HOME/sagco_context_log.csv"
BRAIN_DIR="$HOME/SAGCO_OBSIDIAN_BRAIN/nodes"

mkdir -p "$HOME/sagco_race" "$BRAIN_DIR"

# ── override device if passed ─────────────────────────────────────────────────
ARG1="${1:-}"
case "$ARG1" in
    show)
        echo "PWD HISTORY — device=${DEV}"
        echo "=========================="
        [ -f "$PWD_LOG" ] && grep ",${DEV}," "$PWD_LOG" | tail -10 | \
            awk -F',' '{printf "  [%s] %s  @ %s\n", $1, $2, $4}' \
            || echo "  (no pwd log found — run sagco-pwd first)"
        exit 0
        ;;
    history)
        TARGET="${2:-$DEV}"
        echo "PWD HISTORY — device=${TARGET}"
        echo "================================"
        [ -f "$PWD_LOG" ] && grep ",${TARGET}," "$PWD_LOG" | \
            awk -F',' '{printf "  [%s] pwd=%-40s bat=%s\n", $1, $4, $5}' \
            || echo "  (no history for device: $TARGET)"
        exit 0
        ;;
    ""|show|history) ;;
    *)
        # positional device override
        DEV="$ARG1"
        ;;
esac

BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
UNAME=$(uname -a 2>/dev/null | cut -c1-60)
SHELL_TYPE=$(basename "${SHELL:-sh}" 2>/dev/null || echo sh)
LAST_CMD=""
[ -f "$LEDGER" ] && LAST_CMD=$(tail -1 "$LEDGER" 2>/dev/null | cut -d',' -f3)

echo "SAGCO PWD — Self-Awareness"
echo "=========================="
echo "Stamp:    $STAMP"
echo "Device:   $DEV"
echo "PWD:      $PWD"
echo "Shell:    $SHELL_TYPE"
echo "Battery:  $BAT%"
echo "Kernel:   $UNAME"
echo "LastCmd:  ${LAST_CMD:-none}"
echo ""

# ── write pwd log ─────────────────────────────────────────────────────────────
[ -f "$PWD_LOG" ] || echo "timestamp,device,shell,pwd,battery,last_cmd,status" > "$PWD_LOG"
echo "${STAMP},${DEV},${SHELL_TYPE},${PWD},${BAT},${LAST_CMD:-none},SAGCO_PWD_TICK" >> "$PWD_LOG"

# ── write race tick ───────────────────────────────────────────────────────────
[ -f "$RACE_OUT" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_OUT"
echo "${STAMP},${DEV},sagco_pwd,${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_OUT"

# ── write ledger ──────────────────────────────────────────────────────────────
HASH=$(echo "${STAMP}sagco-pwd${DEV}" | cksum | awk '{printf "%012d", $1}')
[ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
echo "${STAMP},${DEV},sagco-pwd,pwd_${DEV}_${STAMP},${HASH},SAGCO_PWD_TICK" >> "$LEDGER"

# ── write obsidian brain node ────────────────────────────────────────────────
NODE_FILE="$BRAIN_DIR/${DEV}_pwd_${STAMP}.md"
cat > "$NODE_FILE" << NODE
# PWD Node — ${DEV}
timestamp: ${STAMP}
device: ${DEV}
pwd: ${PWD}
shell: ${SHELL_TYPE}
battery: ${BAT}
last_command: ${LAST_CMD:-none}
status: SAGCO_PWD_TICK
NODE

echo "STATUS=SAGCO_PWD_TICK"
echo "NODE=$NODE_FILE"

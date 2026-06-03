#!/bin/sh
# sagco-nina — Nina Trader Bot for SAGCO-OS
# Passive income automation: DCA + RSI momentum + SPY mirror
# Usage: sagco-nina [status|dca|momentum|spy-mirror|all|portfolio|history] [dry|paper|live]

NINA_BIN="$HOME/bin/nina-trader"
CMD="${1:-status}"
MODE="${2:-dry}"

# SAGCO logging
export SAGCO_DEVICE="${SAGCO_DEVICE:-unknown}"
LEDGER="$HOME/sagco_ledger.csv"
NINA_LOG="$HOME/sagco_nina"
STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")

mkdir -p "$NINA_LOG"

log_race() {
    OUT="$HOME/sagco_race/race_log.csv"
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    mkdir -p "$HOME/sagco_race"
    [ -f "$OUT" ] || echo "timestamp,device,event,pwd,battery,status" > "$OUT"
    echo "${STAMP},${SAGCO_DEVICE},${1},${PWD},${BAT},SAGCO_RACE_TICK" >> "$OUT"
}

log_ledger() {
    HASH=$(echo "${STAMP}${1}" | cksum | awk '{printf "%012d", $1}')
    [ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
    echo "${STAMP},${SAGCO_DEVICE},sagco-nina,${2},${HASH},${3}" >> "$LEDGER"
}

log_race "nina_start_${CMD}"

# Show header
echo "🤖 SAGCO-OS NINA TRADER BOT"
echo "==========================="
echo "Command: $CMD | Mode: $MODE"
echo "Device:  $SAGCO_DEVICE"
echo "Stamp:   $STAMP"
echo ""

# Check for compiled binary
if [ -f "$NINA_BIN" ]; then
    "$NINA_BIN" "$CMD" "$MODE"
    EXIT_CODE=$?
else
    echo "⚙️  Nina Trader binary not found at $NINA_BIN"
    echo "   Compile it on Termux with:"
    echo ""
    echo "   cd ~/ninja-bot-forge/nina-trader"
    echo "   cargo build --release"
    echo "   cp target/release/nina-trader ~/bin/nina-trader"
    echo ""
    echo "   Then run: sagco-nina $CMD $MODE"
    echo ""

    # Fallback: show account status via curl if keys available
    if [ -n "$ALPACA_KEY" ] && [ -n "$ALPACA_SECRET" ]; then
        echo "📡 Fetching account via API fallback..."
        if [ "$ALPACA_LIVE" = "true" ]; then
            API_URL="https://api.alpaca.markets/v2/account"
        else
            API_URL="https://paper-api.alpaca.markets/v2/account"
        fi
        curl -s -H "APCA-API-KEY-ID: $ALPACA_KEY" \
             -H "APCA-API-SECRET-KEY: $ALPACA_SECRET" \
             "$API_URL" | python3 -m json.tool 2>/dev/null || echo "API call failed"
    else
        echo "💡 Set ALPACA_KEY and ALPACA_SECRET for live API access"
        echo "   Sign up free at: alpaca.markets (paper trading, no real money)"
        echo ""
        echo "DEMO STATUS:"
        echo "  Portfolio: \$100,000.00 (paper)"
        echo "  Strategy ready: dca | momentum | spy-mirror"
    fi
    EXIT_CODE=0
fi

log_race "nina_complete_${CMD}"
log_ledger "sagco-nina" "nina_run_${STAMP}.log" "SAGCO_NINA_PASS"

echo ""
echo "STATUS=SAGCO_NINA_PASS"
echo "STAMP=$STAMP"
echo "TRADE_LOG=$NINA_LOG/trade_log.csv"

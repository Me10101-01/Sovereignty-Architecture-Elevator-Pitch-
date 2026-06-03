#!/bin/sh
# sagco-identity — Universal Device Identity for SAGCO-OS
# Auto-detects device, writes ~/.sagco_device, exports SAGCO_DEVICE
# Run once per device to permanently eliminate unknown attribution
#
# Usage:
#   sagco-identity              → detect and register
#   sagco-identity show         → show current identity
#   sagco-identity set <name>   → manually override (ipad|zfold|ish|termux|custom)
#   sagco-identity install      → add to ~/.bashrc permanently

IDENTITY_FILE="$HOME/.sagco_device"
REGISTRY="$HOME/sagco_device_registry.csv"
STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "unknown")

# ── auto-detect ──────────────────────────────────────────────────────────────
detect_device() {
    # iSH: iOS shell emulator — check /proc/ish or ish-specific kernel string
    if [ -f /proc/ish ] || (uname -r 2>/dev/null | grep -qi "ish"); then
        echo "ish"
        return
    fi

    # Termux on Android
    if [ -n "$TERMUX_VERSION" ] || [ -d "/data/data/com.termux" ]; then
        # Check if Z Fold model
        MODEL=$(getprop ro.product.model 2>/dev/null || echo "")
        if echo "$MODEL" | grep -qi "fold\|SM-F"; then
            echo "zfold"
        else
            echo "termux"
        fi
        return
    fi

    # Android without Termux env (rare)
    if uname -o 2>/dev/null | grep -qi "android"; then
        MODEL=$(getprop ro.product.model 2>/dev/null || echo "")
        if echo "$MODEL" | grep -qi "fold\|SM-F"; then
            echo "zfold"
        else
            echo "android"
        fi
        return
    fi

    # macOS
    if [ "$(uname -s 2>/dev/null)" = "Darwin" ]; then
        echo "macos"
        return
    fi

    # Linux: check hostname hints
    HOST=$(hostname 2>/dev/null || echo "")
    if echo "$HOST" | grep -qi "ipad\|ios"; then
        echo "ipad"
        return
    fi

    # Fallback: use hostname slug
    echo "$HOST" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g' | cut -c1-12
}

# ── subcommands ───────────────────────────────────────────────────────────────
CMD="${1:-detect}"

case "$CMD" in

    show)
        if [ -f "$IDENTITY_FILE" ]; then
            CURRENT=$(cat "$IDENTITY_FILE")
            echo "SAGCO_DEVICE=$CURRENT"
            echo "Identity file: $IDENTITY_FILE"
        else
            echo "No identity registered — run: sagco-identity"
        fi
        exit 0
        ;;

    set)
        MANUAL="${2:-}"
        if [ -z "$MANUAL" ]; then
            echo "Usage: sagco-identity set <name>"
            exit 1
        fi
        echo "$MANUAL" > "$IDENTITY_FILE"
        echo "SAGCO_DEVICE=$MANUAL (manually set)"
        ;;

    install)
        # Add to ~/.bashrc and ~/.profile for permanent export
        SNIPPET='
# SAGCO-OS Device Identity
if [ -f "$HOME/.sagco_device" ]; then
  export SAGCO_DEVICE=$(cat "$HOME/.sagco_device")
fi
export PATH="$HOME/bin:$PATH"
'
        for RC in "$HOME/.bashrc" "$HOME/.profile" "$HOME/.zshrc"; do
            if [ -f "$RC" ] && ! grep -q "sagco_device" "$RC"; then
                printf '%s' "$SNIPPET" >> "$RC"
                echo "Installed into $RC"
            fi
        done
        echo "STATUS=SAGCO_IDENTITY_INSTALL_PASS"
        exit 0
        ;;

    detect|*)
        DETECTED=$(detect_device)
        echo "$DETECTED" > "$IDENTITY_FILE"
        export SAGCO_DEVICE="$DETECTED"

        echo "SAGCO UNIVERSAL DEVICE IDENTITY"
        echo "================================"
        echo "Detected:  $DETECTED"
        echo "Written:   $IDENTITY_FILE"
        echo ""

        # Write to device registry
        [ -f "$REGISTRY" ] || echo "timestamp,device,hostname,uname,termux_ver,identity_file" > "$REGISTRY"
        HOST=$(hostname 2>/dev/null || echo "unknown")
        UNAME=$(uname -r 2>/dev/null || echo "unknown")
        TV="${TERMUX_VERSION:-none}"
        echo "${STAMP},${DETECTED},${HOST},${UNAME},${TV},${IDENTITY_FILE}" >> "$REGISTRY"

        echo "Device registry: $REGISTRY"
        echo ""
        echo "To make permanent, run:"
        echo "  sagco-identity install"
        echo ""
        echo "Current shell (run this now):"
        echo "  export SAGCO_DEVICE=$DETECTED"
        echo ""
        echo "STATUS=SAGCO_IDENTITY_PASS"
        echo "SAGCO_DEVICE=$DETECTED"
        ;;

esac

#!/bin/sh
# sagco-vim-install — iSH/ash safe script installer via vim paste method
# Solves the heredoc-executes-as-commands problem on iSH Alpine ash.
# Generates exact vim keystrokes needed to paste any script from the repo.
#
# Usage:
#   sagco-vim-install sagco-360.sh           → print vim paste steps
#   sagco-vim-install sagco-360.sh ~/bin/sagco-360  → custom dest
#   sagco-vim-install list                   → show all installable scripts
#   sagco-vim-install all                    → install all sagco-*.sh to ~/bin/

REPO_ROOT="$(cd "$(dirname "$0")" 2>/dev/null && pwd || echo "$HOME")"

case "${1:-list}" in

    list)
        echo "SAGCO INSTALLABLE SCRIPTS"
        echo "=========================="
        ls -1 "$REPO_ROOT"/sagco-*.sh 2>/dev/null | while read -r F; do
            BASE=$(basename "$F" .sh)
            printf "  %-30s  sagco-vim-install %s\n" "$BASE" "$(basename "$F")"
        done
        echo ""
        echo "  Install all: sagco-vim-install all"
        ;;

    all)
        echo "INSTALLING ALL — copying to ~/bin/"
        mkdir -p "$HOME/bin"
        INSTALLED=0
        for F in "$REPO_ROOT"/sagco-*.sh; do
            BASE=$(basename "$F" .sh)
            cp "$F" "$HOME/bin/$BASE" && chmod +x "$HOME/bin/$BASE" \
                && echo "  ✓ $BASE" && INSTALLED=$((INSTALLED + 1))
        done
        echo ""
        echo "Installed: $INSTALLED scripts to ~/bin/"
        echo ""
        echo "Make sure ~/bin is in PATH:"
        echo "  grep -q 'HOME/bin' ~/.profile || echo 'export PATH=\"\$HOME/bin:\$PATH\"' >> ~/.profile"
        echo "  export PATH=\"\$HOME/bin:\$PATH\""
        ;;

    *)
        SCRIPT="$1"
        SRC="$REPO_ROOT/$SCRIPT"
        [ -f "$SRC" ] || SRC="$REPO_ROOT/${SCRIPT}.sh"
        [ -f "$SRC" ] || { echo "Not found: $SCRIPT"; exit 1; }

        DEST="${2:-$HOME/bin/$(basename "$SRC" .sh)}"
        mkdir -p "$(dirname "$DEST")"

        # Direct copy if we can
        cp "$SRC" "$DEST" && chmod +x "$DEST" && {
            echo "Installed: $DEST"
            echo "Run: $(basename "$DEST")"
            exit 0
        }

        # Fallback: print vim paste instructions for iSH
        echo "VIM PASTE INSTALL — for iSH ash (heredoc workaround)"
        echo "======================================================="
        echo ""
        echo "1. Open vim:"
        echo "   vim $DEST"
        echo ""
        echo "2. In vim, type exactly:"
        echo "   :set paste"
        echo "   Enter"
        echo "   i"
        echo ""
        echo "3. Paste the contents of: $SRC"
        echo ""
        echo "4. Press Esc, then type:"
        echo "   :wq"
        echo "   Enter"
        echo ""
        echo "5. Then:"
        echo "   chmod +x $DEST"
        echo ""
        echo "Script content to paste:"
        echo "─────────────────────────"
        cat "$SRC"
        echo "─────────────────────────"
        ;;

esac

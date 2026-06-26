#!/bin/sh
# Package SAGCO organism tools into a self-contained tarball.
# Works on Alpine, iOS (a-Shell), Raspberry Pi, any POSIX system with Python 3.
# No internet required after download. No API keys. No external models.

VERSION="1.0.0"
TARBALL="sagco-organism-v${VERSION}.tar.gz"
STAGING="/tmp/sagco-package-$$"

mkdir -p "$STAGING/sagco-organism"

# ── Core tools ────────────────────────────────────────────────────────────────
cp sagco_priority.py         "$STAGING/sagco-organism/"
cp sagco_organ.py            "$STAGING/sagco-organism/" 2>/dev/null || true
cp sagco_subsystem_graph.py  "$STAGING/sagco-organism/"
cp sagco_blueprint.py        "$STAGING/sagco-organism/"
cp sagco_eru_recover.py      "$STAGING/sagco-organism/"
cp sagco                     "$STAGING/sagco-organism/sagco-dispatcher"

# ── Install script ────────────────────────────────────────────────────────────
cat > "$STAGING/sagco-organism/install.sh" << 'INSTALLEOF'
#!/bin/sh
# SAGCO Organism Installer — no internet, no API keys, no external models.
# Works on Alpine Linux, iOS a-Shell, Raspberry Pi, any Python 3 system.

INSTALL_DIR="${SAGCO_INSTALL:-/root}"
BIN_DIR="${SAGCO_BIN:-/usr/local/bin}"
WORK_DIR="$INSTALL_DIR/sagco_workspace"

echo "SAGCO ORGANISM INSTALLER"
echo "========================"
echo "workspace : $WORK_DIR"
echo "bin       : $BIN_DIR"
echo ""

# Create workspace
mkdir -p "$WORK_DIR"
mkdir -p "$BIN_DIR"

# Copy tools
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
for f in sagco_priority.py sagco_subsystem_graph.py sagco_blueprint.py sagco_eru_recover.py; do
    if [ -f "$SCRIPT_DIR/$f" ]; then
        cp "$SCRIPT_DIR/$f" "$WORK_DIR/$f"
        echo "  installed: $f"
    fi
done

# Wire the dispatcher
cp "$SCRIPT_DIR/sagco-dispatcher" "$BIN_DIR/sagco"
chmod +x "$BIN_DIR/sagco"
echo "  installed: sagco → $BIN_DIR/sagco"

# Fix PATH in profile if needed
if ! echo "$PATH" | grep -q "$BIN_DIR"; then
    echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$INSTALL_DIR/.profile"
    echo "  added $BIN_DIR to PATH in .profile"
fi

echo ""
echo "DONE. Run:"
echo "  export PATH=\"$BIN_DIR:\$PATH\""
echo "  sagco help"
INSTALLEOF
chmod +x "$STAGING/sagco-organism/install.sh"

# ── README ────────────────────────────────────────────────────────────────────
cat > "$STAGING/sagco-organism/README.txt" << 'READMEEOF'
SAGCO ORGANISM v1.0.0
=====================
Self-contained cognition stack. No internet. No API keys. No external models.

INSTALL:
  tar -xzf sagco-organism-v1.0.0.tar.gz
  cd sagco-organism
  sh install.sh

COMMANDS:
  sagco help
  sagco priority [N]              — rank organs by weight
  sagco organ <name>              — inspect a single organ
  sagco subsystem <organ>         — dependency graph
  sagco blueprint                 — full organism summary
  sagco recover                   — forensic ERU rebuild
  sagco status                    — health check

POINT TO YOUR TREE:
  export SAGCO_TREE=/path/to/sagco_first_party_tree.json
  sagco blueprint

iOS (a-Shell):
  Same commands. Set SAGCO_BIN=~/Documents/bin in install.sh first.

No LLM required. The organism reads its own memory.
READMEEOF

# ── Build tarball ─────────────────────────────────────────────────────────────
cd "$STAGING"
tar -czf "$OLDPWD/$TARBALL" sagco-organism/
cd "$OLDPWD"
rm -rf "$STAGING"

SIZE=$(du -h "$TARBALL" | cut -f1)
echo "PACKAGED: $TARBALL ($SIZE)"
echo ""
echo "Install on any device:"
echo "  tar -xzf $TARBALL"
echo "  cd sagco-organism"
echo "  sh install.sh"

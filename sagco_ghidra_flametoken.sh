#!/usr/bin/env bash
# SAGCO Ghidra + FlameToken extraction pipeline
# Run from: ~/downloads/sagco_rust_command_compiler
# Prereqs: pkg install openjdk-21 && pkg install ghidra OR manual ghidra install
set -eu

BINARY="target/release/sagco"
REPORT_DIR="${HOME}/sagco_pr_lab/repo/reports/ghidra"
GHIDRA_HOME="${GHIDRA_HOME:-${HOME}/downloads/ghidra_12.1_PUBLIC}"
JAVA_HOME="${JAVA_HOME:-/data/data/com.termux/files/usr/lib/jvm/java-21-openjdk}"
GHIDRA_PROJ="${HOME}/ghidra_projects"

mkdir -p "$REPORT_DIR"

echo "[SAGCO] ── FlameToken Extraction Pipeline ──"
echo "[SAGCO] target: $BINARY"
echo "[SAGCO] report: $REPORT_DIR"
echo ""

# ── Step 0: verify binary exists ────────────────────────────────────────────
if [ ! -f "$BINARY" ]; then
  echo "[SAGCO] binary not found at $BINARY"
  echo "[SAGCO] searching..."
  FOUND=$(find "${HOME}/downloads" -name sagco -type f 2>/dev/null | head -1)
  if [ -n "$FOUND" ]; then
    echo "[SAGCO] found at: $FOUND"
    BINARY="$FOUND"
  else
    echo "[SAGCO] not found — rebuilding with cargo..."
    cargo build --release
    BINARY="target/release/sagco"
  fi
fi

# ── Step 1: ELF headers ──────────────────────────────────────────────────────
echo "[SAGCO] readelf headers..."
{
  echo "# ELF Header — $(date)"
  echo "# Binary: $BINARY"
  echo ""
  readelf -h "$BINARY" 2>&1
  echo ""
  echo "# Section headers:"
  readelf -S "$BINARY" 2>&1 | head -60
} > "$REPORT_DIR/elf_headers.txt"
echo "  -> elf_headers.txt ($(wc -l < "$REPORT_DIR/elf_headers.txt") lines)"

# ── Step 2: Symbol table ─────────────────────────────────────────────────────
echo "[SAGCO] nm symbol table..."
{
  echo "# Symbol Table — $(date)"
  echo ""
  nm -D "$BINARY" 2>/dev/null || nm "$BINARY" 2>/dev/null || echo "nm: no symbols (stripped binary)"
} > "$REPORT_DIR/elf_symbols.txt"
echo "  -> elf_symbols.txt ($(wc -l < "$REPORT_DIR/elf_symbols.txt") lines)"

# ── Step 3: llvm-strings FlameToken extraction ───────────────────────────────
echo "[SAGCO] llvm-strings FlameToken pass..."
STRINGS_CMD="llvm-strings"
if ! command -v llvm-strings > /dev/null 2>&1; then
  if command -v strings > /dev/null 2>&1; then
    STRINGS_CMD="strings"
  elif command -v gstrings > /dev/null 2>&1; then
    STRINGS_CMD="gstrings"
  else
    echo "[SAGCO] WARNING: no strings tool found — skipping FlameToken pass"
    STRINGS_CMD=""
  fi
fi

if [ -n "$STRINGS_CMD" ]; then
  $STRINGS_CMD "$BINARY" \
    | grep -iE "sagco|past|wave|weather|agent|flame|treasure|cmd|dna|evolution|matrix|deploy|swarm|empire|genome|ratio|constitution|flamelang" \
    | sort -u \
    > "$REPORT_DIR/flametokens.txt"
  TOKEN_COUNT=$(wc -l < "$REPORT_DIR/flametokens.txt")
  TOKEN_SHA=$(sha256sum "$REPORT_DIR/flametokens.txt" | awk '{print $1}')
  echo "  -> flametokens.txt: $TOKEN_COUNT tokens, sha256=$TOKEN_SHA"

  # ── Step 3b: Command DNA presence check ─────────────────────────────────
  echo "[SAGCO] Command DNA cross-reference (23 commands)..."
  COMMANDS="sagco-status sagco-info sagco-help sagco-manifest sagco-verify
    sagco-memmon sagco-cpumon sagco-net sagco-tcpmon sagco-diskmon
    sagco-procs sagco-ports sagco-load sagco-dmesg sagco-debug
    sagco-handles sagco-svcmon sagco-retmon sagco-matrix sagco-dash
    sagco-evolution sagco-dna sagco-deploy sagco-one"
  FOUND_COUNT=0
  MISS_COUNT=0
  {
    echo "# Command DNA Presence — $(date)"
    echo ""
    for CMD in $COMMANDS; do
      if $STRINGS_CMD "$BINARY" | grep -q "$CMD"; then
        echo "FOUND:   $CMD"
        FOUND_COUNT=$((FOUND_COUNT + 1))
      else
        echo "MISSING: $CMD"
        MISS_COUNT=$((MISS_COUNT + 1))
      fi
    done
    echo ""
    echo "found=$FOUND_COUNT missing=$MISS_COUNT"
  } > "$REPORT_DIR/command_dna_check.txt"
  echo "  -> command_dna_check.txt: $FOUND_COUNT/23 found"
fi

# ── Step 4: Ghidra headless analysis ─────────────────────────────────────────
echo "[SAGCO] Ghidra headless analysis..."
if [ ! -d "$GHIDRA_HOME" ]; then
  echo "[SAGCO] Ghidra not found at $GHIDRA_HOME — skipping"
  echo "[SAGCO] Download: https://github.com/NationalSecurityAgency/ghidra/releases"
else
  export JAVA_HOME
  export PATH="$JAVA_HOME/bin:$PATH"

  JAVA_VER=$(java -version 2>&1 | head -1)
  echo "[SAGCO] Java: $JAVA_VER"

  mkdir -p "$GHIDRA_PROJ"
  "$GHIDRA_HOME/support/analyzeHeadless" \
    "$GHIDRA_PROJ" SAGCO_FLAMETOKEN \
    -import "$BINARY" \
    -overwrite \
    2>&1 | tee "$REPORT_DIR/ghidra_sagco.log"

  echo "[SAGCO] Ghidra log: $REPORT_DIR/ghidra_sagco.log"
fi

# ── Final seal ───────────────────────────────────────────────────────────────
echo ""
echo "[SAGCO] ── FlameToken Pipeline Complete ──"
echo "reports at: $REPORT_DIR"
ls -lh "$REPORT_DIR"

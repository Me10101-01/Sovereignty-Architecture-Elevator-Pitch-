#!/data/data/com.termux/files/usr/bin/bash
# SAGCO Status Archeologist — OCR + log parser + evidence ledger
# Run from: ~/downloads/sagco_rust_command_compiler
# Prereqs: pkg install tesseract poppler binutils
set -e

IN="${1:-}"
OUT="reports/status_archeologist"
mkdir -p "$OUT"

if [ -z "$IN" ]; then
  echo "USE: bash sagco_status_archeologist.sh <image.jpg|file.pdf|file.txt|file.log>"
  echo ""
  echo "Examples:"
  echo "  bash sagco_status_archeologist.sh /sdcard/DCIM/screenshot.jpg"
  echo "  bash sagco_status_archeologist.sh reports/ghidra/ghidra_sagco.log"
  exit 1
fi

BASE="$(basename "$IN")"
STAMP="$(date +%Y%m%d_%H%M%S)"
RAW="$OUT/${STAMP}.raw.txt"

echo "===== SAGCO STATUS ARCHEOLOGIST ====="
echo "INPUT=$IN"
echo "STAMP=$STAMP"

cp "$IN" "$OUT/${STAMP}-${BASE}" 2>/dev/null || true
sha256sum "$IN" > "$OUT/${STAMP}.sha256" 2>/dev/null || true

# ── text extraction layer ────────────────────────────────────────────────────
EXT="${IN##*.}"
case "$EXT" in
  pdf|PDF)
    if command -v pdftotext > /dev/null 2>&1; then
      pdftotext "$IN" "$RAW" && echo "[+] pdftotext OK"
    else
      echo "[-] pdftotext missing — run: pkg install poppler"
      touch "$RAW"
    fi
    ;;
  jpg|jpeg|png|JPG|JPEG|PNG)
    if command -v tesseract > /dev/null 2>&1; then
      # tesseract needs eng data; install with: pkg install tesseract-lang
      tesseract "$IN" "${OUT}/${STAMP}" 2>/dev/null && mv "${OUT}/${STAMP}.txt" "$RAW" && echo "[+] tesseract OK" || {
        echo "[-] tesseract failed (may need: pkg install tesseract-lang)"
        touch "$RAW"
      }
    else
      echo "[-] tesseract missing — run: pkg install tesseract"
      touch "$RAW"
    fi
    ;;
  *)
    # plain text, log files, or binary extraction fallback
    if [ -f "$IN" ]; then
      cp "$IN" "$RAW" 2>/dev/null || true
      # also try strings for binary files
      if command -v strings > /dev/null 2>&1; then
        strings "$IN" >> "$RAW" 2>/dev/null || true
      elif command -v llvm-strings > /dev/null 2>&1; then
        llvm-strings "$IN" >> "$RAW" 2>/dev/null || true
      elif command -v gstrings > /dev/null 2>&1; then
        gstrings "$IN" >> "$RAW" 2>/dev/null || true
      fi
    fi
    ;;
esac

# ── signal extraction ────────────────────────────────────────────────────────
grep -Ei \
  "error|fail|missing|not found|jdk|ghidra|cargo|rust|sagco|pass|status|report|sha|token|flame|target|release|binary|blocke" \
  "$RAW" > "$OUT/${STAMP}.signals.txt" 2>/dev/null || true

SIG_COUNT=$(wc -l < "$OUT/${STAMP}.signals.txt")
echo "SIGNALS=$SIG_COUNT"

# ── report ───────────────────────────────────────────────────────────────────
REPORT="$OUT/${STAMP}.report.md"
cat > "$REPORT" <<REPORTEOF
# SAGCO STATUS ARCHEOLOGIST REPORT

**INPUT:** $IN
**STAMP:** $STAMP
**SHA256:** $(sha256sum "$IN" 2>/dev/null | awk '{print $1}')

## Pipeline

\`\`\`
artifact -> extraction -> signal grep -> FlameToken status map
\`\`\`

## Signal Summary ($SIG_COUNT lines)

\`\`\`
$(head -120 "$OUT/${STAMP}.signals.txt" 2>/dev/null)
\`\`\`

## FlameToken Hit Scan

\`\`\`
$(grep -iE "sagco|flame|past|wave|agent|dna|evolution|treasure|bottleneck" "$RAW" 2>/dev/null | sort -u | head -60 || echo "(none)")
\`\`\`

## Verdict

STATUS=SAGCO_STATUS_ARCHEOLOGIST_PASS
REPORTEOF

echo "REPORT=$REPORT"
echo ""
cat "$REPORT"

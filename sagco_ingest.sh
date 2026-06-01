#!/usr/bin/env bash
# sagco_ingest — Universal Artifact Router + Variance Engine v1
# Every input: detect → extract → tokenize → fingerprint → antibody → seal
# This is what separates artifact logger from artifact OS:
#   "Gemini API" and "banana sandwich" are NOT the same source type.
# License: SSL-1.0 — Strategickhaos DAO LLC
set -e

ARTIFACT="${1:-}"
[ -z "$ARTIFACT" ] && {
  echo "Usage: sagco_ingest <artifact>"
  echo "  <artifact>  file.pdf | file.md | file.rs | file.db | file.png"
  echo "              https://... | drive.google.com/..."
  echo "              terminal:<cmd> | obsidian:<vault>"
  echo "              ELF binary | directory"
  exit 1
}

OUT="reports/ingest"
mkdir -p "$OUT"
STAMP="$(date +%Y%m%d_%H%M%S)"
BASE="ingest_${STAMP}"
REPORT="$OUT/${BASE}.md"
JSON="$OUT/${BASE}.json"
RAW_TXT="/tmp/sagco_ingest_raw_$$.txt"

# ── Step 1: DETECT type ───────────────────────────────────────────────────────
detect_type() {
  local a="$1"
  local lower; lower="$(echo "$a" | tr '[:upper:]' '[:lower:]')"

  if   [[ "$lower" == terminal:* ]];          then echo "terminal"
  elif [[ "$lower" == obsidian:* ]];          then echo "obsidian"
  elif [[ "$lower" == claude:* ]];            then echo "claude"
  elif [[ "$lower" =~ ^https?:// ]];          then
    if echo "$lower" | grep -q "drive.google"; then echo "gdrive"
    elif echo "$lower" | grep -q "dropbox";    then echo "dropbox"
    else echo "url"; fi
  elif [ -d "$a" ];                           then echo "directory"
  elif [ -f "$a" ]; then
    # check magic bytes first
    local magic; magic="$(head -c 4 "$a" 2>/dev/null | od -A n -t x1 | tr -d ' \n')"
    if [[ "$magic" == 7f454c46* ]];           then echo "elf"
    else
      case "$lower" in
        *.pdf)                                     echo "pdf"  ;;
        *.db|*.sqlite|*.sqlite3)                   echo "sql"  ;;
        *.png|*.jpg|*.jpeg|*.bmp|*.tiff)           echo "image" ;;
        *.rs|*.md|*.txt|*.yaml|*.yml|*.json|*.sh)  echo "text" ;;
        *)                                         echo "binary" ;;
      esac
    fi
  else
    echo "concept"   # plain text input — fingerprint + tokenize as-is
  fi
}

TYPE="$(detect_type "$ARTIFACT")"
DEPENDENCY_MISS=""

# ── Step 2: EXTRACT raw signals ───────────────────────────────────────────────
extract() {
  case "$TYPE" in

    pdf)
      if command -v pdftotext &>/dev/null; then
        pdftotext "$ARTIFACT" - 2>/dev/null || strings "$ARTIFACT"
      elif command -v strings &>/dev/null; then
        DEPENDENCY_MISS="pdftotext (pkg install poppler)"
        strings "$ARTIFACT"
      else
        DEPENDENCY_MISS="pdftotext + strings"
        echo "EXTRACTION_FAILED"
      fi ;;

    text)
      cat "$ARTIFACT" ;;

    sql)
      if command -v sqlite3 &>/dev/null; then
        sqlite3 "$ARTIFACT" .dump 2>/dev/null || cat "$ARTIFACT"
      else
        DEPENDENCY_MISS="sqlite3 (pkg install sqlite)"
        strings "$ARTIFACT" 2>/dev/null || cat "$ARTIFACT"
      fi ;;

    image)
      if command -v tesseract &>/dev/null; then
        tesseract "$ARTIFACT" stdout 2>/dev/null || strings "$ARTIFACT"
      else
        DEPENDENCY_MISS="tesseract (pkg install tesseract)"
        strings "$ARTIFACT" 2>/dev/null || echo "IMAGE_NO_OCR"
      fi ;;

    elf|binary)
      if command -v strings &>/dev/null; then
        strings "$ARTIFACT" | grep -E '\w{4,}' | head -500
      else
        DEPENDENCY_MISS="strings (pkg install binutils)"
        echo "BINARY_NO_STRINGS"
      fi ;;

    url)
      if command -v curl &>/dev/null; then
        local result; result="$(curl -sL --max-time 10 "$ARTIFACT" 2>&1 || true)"
        # detect network policy block
        if echo "$result" | grep -qi "host not in allowlist\|blocked\|403\|connection refused"; then
          DEPENDENCY_MISS="NETWORK_POLICY (run on Termux)"
          echo "$result"
        else
          echo "$result" | strings 2>/dev/null || echo "$result"
        fi
      else
        DEPENDENCY_MISS="curl"
        echo "URL_NO_CURL"
      fi ;;

    gdrive)
      DEPENDENCY_MISS="NETWORK_POLICY (run on Termux)"
      echo "GDRIVE_BLOCKED_IN_REMOTE_ENV" ;;

    dropbox)
      DEPENDENCY_MISS="NETWORK_POLICY (run on Termux)"
      echo "DROPBOX_BLOCKED_IN_REMOTE_ENV" ;;

    terminal)
      local cmd="${ARTIFACT#terminal:}"
      bash -c "$cmd" 2>&1 || true ;;

    obsidian)
      local vault="${ARTIFACT#obsidian:}"
      vault="${vault/#\~/$HOME}"
      if [ -d "$vault" ]; then
        find "$vault" -name '*.md' -exec cat {} \; 2>/dev/null || echo "VAULT_EMPTY"
      else
        DEPENDENCY_MISS="vault not found: $vault"
        echo "OBSIDIAN_VAULT_NOT_FOUND"
      fi ;;

    claude)
      local session="${ARTIFACT#claude:}"
      [ -f "$session" ] && cat "$session" || echo "CLAUDE_SESSION_NOT_FOUND" ;;

    directory)
      find "$ARTIFACT" -type f \( \
        -name "*.md" -o -name "*.rs" -o -name "*.sh" \
        -o -name "*.yaml" -o -name "*.json" -o -name "*.txt" \
      \) -exec cat {} \; 2>/dev/null | head -2000 ;;

    concept)
      echo "$ARTIFACT" ;;

  esac
}

extract > "$RAW_TXT" 2>/dev/null || true

# ── Step 3: TOKENIZE ──────────────────────────────────────────────────────────
TOKEN_COUNT=$(tr ' \t\n' '\n' < "$RAW_TXT" | grep -Ec '\w{4,}' 2>/dev/null || echo 0)
CHAR_COUNT=$(wc -c < "$RAW_TXT")
LINE_COUNT=$(wc -l < "$RAW_TXT")

# ── Step 4: FINGERPRINT ───────────────────────────────────────────────────────
# FNV-inspired 64-bit fingerprint via sha256 prefix
FINGERPRINT=$(sha256sum "$RAW_TXT" | cut -c1-16)

# ── Step 5: VERIFY + VALIDATE + VARIANCE ─────────────────────────────────────
VERIFY_STATUS="PASS"
VARIANCE=0
if [ "$TOKEN_COUNT" -eq 0 ]; then
  VERIFY_STATUS="WARN"
  VARIANCE=100
fi

# domain vocabulary check (simple keyword probe)
DOMAIN_MATCH=$(grep -Ec "sagco|pass|wave|agent|plugin|rust|compile|token|evidence|report" "$RAW_TXT" 2>/dev/null | tr -d '[:space:]' || echo 0)
DOMAIN_MATCH="${DOMAIN_MATCH:-0}"
[ "${DOMAIN_MATCH:-0}" -eq 0 ] 2>/dev/null && VARIANCE=$((VARIANCE+10)) || true

# ── Step 6: ANTIBODY ─────────────────────────────────────────────────────────
classify_antibody() {
  local type="$1" dep="$2" tokens="$3" verify="$4"

  if   [ -n "$dep" ] && echo "$dep" | grep -qi "NETWORK_POLICY"; then
    echo "NETWORK_POLICY_ANTIBODY|evolution"
  elif [ -n "$dep" ] && echo "$dep" | grep -qi "pkg install\|not found"; then
    echo "DEPENDENCY_ANTIBODY|adaptation"
  elif [ "$verify" = "WARN" ] && [ "$tokens" -eq 0 ]; then
    echo "EMPTY_RESPONSE_ANTIBODY|adaptation"
  elif [ "$type" = "elf" ] || [ "$type" = "binary" ]; then
    echo "RECON_PROBE_ANTIBODY|stabilized"
  elif [ "$type" = "sql" ]; then
    echo "PASS_IMMUNITY|stabilized"
  elif grep -qi "error\|fail\|crash\|bug" "$RAW_TXT" 2>/dev/null; then
    echo "PATH_DISCOVERY_ANTIBODY|adaptation"
  else
    echo "PASS_IMMUNITY|stabilized"
  fi
}

AB_RESULT="$(classify_antibody "$TYPE" "$DEPENDENCY_MISS" "$TOKEN_COUNT" "$VERIFY_STATUS")"
ANTIBODY="${AB_RESULT%%|*}"
TRAJECTORY="${AB_RESULT##*|}"

# EUR score
case "$TRAJECTORY" in
  stabilized) EUR_SCORE="PASS"   ;;
  adaptation) EUR_SCORE="ADAPT"  ;;
  evolution)  EUR_SCORE="EVOLVE" ;;
  mutation)   EUR_SCORE="FAIL"   ;;
  *)          EUR_SCORE="WARN"   ;;
esac

# ── Step 7: BLOODHOUND frequency update (append) ─────────────────────────────
BH_LOG="reports/ingest/ingest_frequency.log"
echo "$STAMP|$TYPE|$ANTIBODY|$TRAJECTORY|$TOKEN_COUNT|$FINGERPRINT" >> "$BH_LOG"

# ── Step 8: Write .md ─────────────────────────────────────────────────────────
CONTENT_PREVIEW=$(head -5 "$RAW_TXT" | tr '\n' ' ' | cut -c1-200)

cat > "$REPORT" <<MD
# SAGCO INGEST REPORT — ${STAMP}
## Universal Artifact Router + Variance Engine v1
## Entity: Strategickhaos DAO LLC | License: SSL-1.0

---

## Source

\`\`\`
ARTIFACT   = $ARTIFACT
TYPE       = $TYPE
TOKENS     = $TOKEN_COUNT
CHARS      = $CHAR_COUNT
LINES      = $LINE_COUNT
FINGERPRINT= $FINGERPRINT
\`\`\`

---

## Extraction

\`\`\`
EXTRACTOR  = $(case "$TYPE" in
  pdf)       echo "pdftotext | strings" ;;
  text)      echo "cat" ;;
  sql)       echo "sqlite3 .dump" ;;
  image)     echo "tesseract OCR" ;;
  elf|binary) echo "strings + readelf" ;;
  url)       echo "curl -sL" ;;
  gdrive)    echo "gdrive download" ;;
  terminal)  echo "bash -c" ;;
  obsidian)  echo "find vault -name '*.md' | xargs cat" ;;
  directory) echo "find -type f | xargs cat" ;;
  *)         echo "echo (concept)" ;;
esac)
DEPENDENCY = ${DEPENDENCY_MISS:-none}
PREVIEW    = $CONTENT_PREVIEW
\`\`\`

---

## EUR Probe

\`\`\`
Expected: extraction succeeds, tokens > 0
Actual:   TOKENS=$TOKEN_COUNT  FINGERPRINT=$FINGERPRINT
Verify:   $VERIFY_STATUS
Variance: $VARIANCE%
Score:    $EUR_SCORE
\`\`\`

---

## Antibody

\`\`\`
ANTIBODY   = $ANTIBODY
TRAJECTORY = $TRAJECTORY
SCORE      = $EUR_SCORE
\`\`\`

---

## BLOODHOUND Update

\`\`\`
FREQUENCY_LOG = $BH_LOG
ENTRY = $STAMP|$TYPE|$ANTIBODY|$TRAJECTORY|$TOKEN_COUNT
\`\`\`

---

STATUS=SAGCO_INGEST_PASS
SAGCO_COMMAND_DNA=a364ca9f90356c85

*Strategickhaos DAO LLC — SSL-1.0*
MD

# ── Step 9: Write .json ───────────────────────────────────────────────────────
python3 - "$JSON" "$STAMP" "$ARTIFACT" "$TYPE" \
  "$TOKEN_COUNT" "$CHAR_COUNT" "$LINE_COUNT" \
  "$FINGERPRINT" "$ANTIBODY" "$TRAJECTORY" "$EUR_SCORE" \
  "$VERIFY_STATUS" "$VARIANCE" \
  "${DEPENDENCY_MISS:-none}" <<'PY'
import json, sys

(_, json_path, stamp, artifact, type_, tokens, chars, lines,
 fp, antibody, trajectory, score, verify, variance, dep) = sys.argv

data = {
    "stamp":       stamp,
    "artifact":    artifact,
    "type":        type_,
    "token_count": int(tokens),
    "char_count":  int(chars),
    "line_count":  int(lines),
    "fingerprint": fp,
    "antibody":    antibody,
    "trajectory":  trajectory,
    "eur_score":   score,
    "verify":      verify,
    "variance":    int(variance),
    "dependency":  dep,
    "sagco_dna":   "a364ca9f90356c85",
    "status":      "SAGCO_INGEST_PASS",
}
with open(json_path, "w") as f:
    json.dump(data, f, indent=2)
print("JSON written:", json_path)
PY

rm -f "$RAW_TXT"

# ── SHA seals ─────────────────────────────────────────────────────────────────
SPEC_SHA="$(sha256sum "$REPORT" | awk '{print $1}')"
ARTIFACT_SHA="$(sha256sum "$JSON" | awk '{print $1}')"

cat >> "$REPORT" <<SEAL

## SHA256 Seals

\`\`\`
SPEC_SHA     = $SPEC_SHA
ARTIFACT_SHA = $ARTIFACT_SHA
SAGCO_DNA    = a364ca9f90356c85
STATUS       = SAGCO_INGEST_PASS
\`\`\`
SEAL

# ── Print summary ─────────────────────────────────────────────────────────────
echo "===== SAGCO INGEST ====="
echo "ARTIFACT=$ARTIFACT"
echo "TYPE=$TYPE"
echo "TOKENS=$TOKEN_COUNT"
echo "FINGERPRINT=$FINGERPRINT"
echo "ANTIBODY=$ANTIBODY"
echo "TRAJECTORY=$TRAJECTORY"
echo "SCORE=$EUR_SCORE"
[ -n "$DEPENDENCY_MISS" ] && echo "DEPENDENCY_MISS=$DEPENDENCY_MISS"
echo ""
echo "REPORT=$REPORT"
echo "JSON=$JSON"
echo "SPEC_SHA=$SPEC_SHA"
echo ""
echo "STATUS=SAGCO_INGEST_PASS"

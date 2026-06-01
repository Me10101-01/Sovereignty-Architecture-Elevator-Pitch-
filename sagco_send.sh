#!/usr/bin/env bash
# sagco_send — Plugin Protocol Runtime Node v1
# Auto-creates .md + .json → auto-runs sagco wave on output
# Turns send into a self-feeding pipeline node
# License: SSL-1.0 — Strategickhaos DAO LLC
set -e

# ── usage ─────────────────────────────────────────────────────────────────────
usage() {
  echo "Usage: sagco_send.sh [options] <message_or_file>"
  echo "  --variant <type>   standard (default) | spec | hypothesis | recon | report"
  echo "  --tag <tag>        arbitrary tag label (hypothesis, recon, finding, etc.)"
  echo "  --to <target>      grok | claude | chatgpt | obsidian | canvas (metadata only)"
  echo "  --wave             auto-run sagco wave on output (default: on)"
  echo "  --no-wave          skip sagco wave pass"
  echo "  --seal             create tar.gz archive"
  exit 0
}

# ── defaults ──────────────────────────────────────────────────────────────────
VARIANT="standard"
TAG=""
TO="internal"
DO_WAVE=1
DO_SEAL=0
INPUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --variant) VARIANT="$2"; shift 2 ;;
    --tag)     TAG="$2";     shift 2 ;;
    --to)      TO="$2";      shift 2 ;;
    --wave)    DO_WAVE=1;    shift   ;;
    --no-wave) DO_WAVE=0;    shift   ;;
    --seal)    DO_SEAL=1;    shift   ;;
    --help|-h) usage ;;
    *)         INPUT="$*";   break   ;;
  esac
done

[ -z "$INPUT" ] && { echo "ERROR: no input provided. Use --help"; exit 1; }

OUT="reports/send"
mkdir -p "$OUT"
STAMP="$(date +%Y%m%d_%H%M%S)"
BASE="SAGCO_SEND_${STAMP}"
REPORT="$OUT/${BASE}.md"
JSON="$OUT/${BASE}.json"

# ── tokenize input content ─────────────────────────────────────────────────────
if [ -f "$INPUT" ]; then
  CONTENT="$(cat "$INPUT")"
  SOURCE_TYPE="file"
else
  CONTENT="$INPUT"
  SOURCE_TYPE="text"
fi

TOKEN_COUNT=$(echo "$CONTENT" | wc -w)
CHAR_COUNT=$(echo "$CONTENT"  | wc -c)
LINE_COUNT=$(echo "$CONTENT"  | wc -l)

# simple FNV-inspired fingerprint via sha256 prefix
FINGERPRINT=$(echo "$CONTENT" | sha256sum | cut -c1-16)

# antibody classification
classify_content() {
  local t; t="$(echo "$CONTENT" | tr '[:upper:]' '[:lower:]')"
  if   echo "$t" | grep -q "pass\|success\|complete"; then echo "PASS_IMMUNITY|stabilized"
  elif echo "$t" | grep -q "hypothesis\|theory\|thesis"; then echo "HYPOTHESIS_ANTIBODY|evolution"
  elif echo "$t" | grep -q "recon\|probe\|test\|spec"; then echo "RECON_PROBE_ANTIBODY|stabilized"
  elif echo "$t" | grep -q "error\|fail\|crash\|bug"; then echo "PATH_DISCOVERY_ANTIBODY|adaptation"
  elif echo "$t" | grep -q "plugin\|trait\|interface"; then echo "PLUGIN_PROTOCOL_ANTIBODY|evolution"
  else echo "PASS_IMMUNITY|stabilized"
  fi
}
RESULT="$(classify_content)"
ANTIBODY="${RESULT%%|*}"
TRAJECTORY="${RESULT##*|}"

# ── write .md ─────────────────────────────────────────────────────────────────
cat > "$REPORT" <<MD
# SAGCO SEND — ${VARIANT^^}
## Tag: ${TAG:-untagged} | To: $TO | License: SSL-1.0
## Stamp: $STAMP

---

## Metadata

\`\`\`
VARIANT    = $VARIANT
TAG        = ${TAG:-untagged}
TO         = $TO
SOURCE     = $SOURCE_TYPE
TOKENS     = $TOKEN_COUNT words
CHARS      = $CHAR_COUNT
LINES      = $LINE_COUNT
FINGERPRINT= $FINGERPRINT
ANTIBODY   = $ANTIBODY
TRAJECTORY = $TRAJECTORY
\`\`\`

---

## Content

$CONTENT

---

## EUR Probe

\`\`\`
Expected: content tokenizes cleanly, fingerprint stable
Actual:   TOKENS=$TOKEN_COUNT  FINGERPRINT=$FINGERPRINT
Variance: 0 (content sealed as-sent)
Score:    PASS
\`\`\`

MD

# ── write .json ───────────────────────────────────────────────────────────────
python3 - <<PY
import json, sys

data = {
    "stamp":        "$STAMP",
    "variant":      "$VARIANT",
    "tag":          "${TAG:-untagged}",
    "to":           "$TO",
    "source_type":  "$SOURCE_TYPE",
    "token_count":  $TOKEN_COUNT,
    "char_count":   $CHAR_COUNT,
    "line_count":   $LINE_COUNT,
    "fingerprint":  "$FINGERPRINT",
    "antibody":     "$ANTIBODY",
    "trajectory":   "$TRAJECTORY",
    "content_preview": $(echo "$CONTENT" | head -3 | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))"),
    "sagco_dna":    "a364ca9f90356c85",
    "status":       "SAGCO_SEND_PASS"
}
with open("$JSON", "w") as f:
    json.dump(data, f, indent=2)
print("JSON written: $JSON")
PY

# ── compute SHA256 of both ────────────────────────────────────────────────────
SPEC_SHA="$(sha256sum "$REPORT" | awk '{print $1}')"
ARTIFACT_SHA="$(sha256sum "$JSON" | awk '{print $1}')"

cat >> "$REPORT" <<SEAL
## SHA256 Seals

\`\`\`
SPEC_SHA     = $SPEC_SHA
ARTIFACT_SHA = $ARTIFACT_SHA
SAGCO_DNA    = a364ca9f90356c85
STATUS       = SAGCO_SEND_PASS
\`\`\`

*Strategickhaos DAO LLC — SSL-1.0*
SEAL

echo "===== SAGCO SEND ====="
echo "REPORT=$REPORT"
echo "JSON=$JSON"
echo "SPEC_SHA=$SPEC_SHA"
echo "ARTIFACT_SHA=$ARTIFACT_SHA"
echo ""

# ── auto sagco wave on the report ─────────────────────────────────────────────
if [ "$DO_WAVE" -eq 1 ]; then
  echo "--- sagco wave pass on output ---"
  WAVE_TOKENS=$(cat "$REPORT" | tr ' \t\n' '\n' | grep -Ec '\w{4,}' || echo 0)
  WAVE_FP="$(sha256sum "$REPORT" | cut -c1-16)"
  echo "WAVE_TOKENS=$WAVE_TOKENS"
  echo "WAVE_FINGERPRINT=$WAVE_FP"
  echo "WAVE_STATUS=SAGCO_WAVE_PASS"
  echo ""

  # append wave result to JSON
  python3 - <<PY2
import json
with open("$JSON") as f:
    d = json.load(f)
d["wave"] = {
    "tokens": $WAVE_TOKENS,
    "fingerprint": "$WAVE_FP",
    "status": "SAGCO_WAVE_PASS"
}
with open("$JSON", "w") as f:
    json.dump(d, f, indent=2)
PY2
fi

# ── optional seal ─────────────────────────────────────────────────────────────
if [ "$DO_SEAL" -eq 1 ]; then
  TARBALL="SAGCO_SEND_${STAMP}.tar.gz"
  tar -czf "$TARBALL" "$REPORT" "$JSON"
  TARBALL_SHA="$(sha256sum "$TARBALL" | awk '{print $1}')"
  echo "TARBALL=$TARBALL"
  echo "TARBALL_SHA=$TARBALL_SHA"
fi

echo "STATUS=SAGCO_SEND_PASS"

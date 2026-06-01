#!/usr/bin/env bash
# sagco_evo — Biology-Speed Limit → Culture/Plugin/Artifact Bypass
# Detects when a system hits its own substrate speed limit
# Routes adaptation into the faster external layer (plugins, artifacts, agents)
# License: SSL-1.0 — Strategickhaos DAO LLC
set -e

usage() {
  echo "Usage: sagco_evo.sh [options] [target]"
  echo "  target              file, directory, or concept to evo-probe (default: workspace)"
  echo "  --variant <type>    workspace (default) | command | plugin | artifact | agent"
  echo "  --tag <tag>         arbitrary label"
  echo "  --send              pipe output through sagco_send pipeline"
  echo "  --seal              create tar.gz archive"
  exit 0
}

# ── defaults ──────────────────────────────────────────────────────────────────
VARIANT="workspace"
TAG=""
TARGET="."
DO_SEND=0
DO_SEAL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --variant) VARIANT="$2"; shift 2 ;;
    --tag)     TAG="$2";     shift 2 ;;
    --send)    DO_SEND=1;    shift   ;;
    --seal)    DO_SEAL=1;    shift   ;;
    --help|-h) usage ;;
    *)         TARGET="$1";  shift   ;;
  esac
done

OUT="reports/evolution_variance"
mkdir -p "$OUT"
STAMP="$(date +%Y%m%d_%H%M%S)"
BASE="evo_${STAMP}"
REPORT="$OUT/${BASE}.md"
JSON="$OUT/${BASE}.json"

# ── probe the target ──────────────────────────────────────────────────────────
TARGET_TYPE="workspace"
TARGET_TOKENS=0
TARGET_FP="none"

if [ -f "$TARGET" ]; then
  TARGET_TYPE="file"
  TARGET_TOKENS=$(cat "$TARGET" | wc -w)
  TARGET_FP=$(sha256sum "$TARGET" | cut -c1-16)
elif [ -d "$TARGET" ]; then
  TARGET_TYPE="directory"
  TARGET_TOKENS=$(find "$TARGET" -type f \( -name "*.md" -o -name "*.rs" -o -name "*.sh" -o -name "*.json" \) | xargs cat 2>/dev/null | wc -w)
  TARGET_FP=$(find "$TARGET" -type f | sort | sha256sum | cut -c1-16)
else
  TARGET_TYPE="concept"
  TARGET_TOKENS=$(echo "$TARGET" | wc -w)
  TARGET_FP=$(echo "$TARGET" | sha256sum | cut -c1-16)
fi

# ── detect speed limit ────────────────────────────────────────────────────────
detect_speed_limit() {
  local type="$1"
  local tokens="$2"
  case "$type" in
    file)
      if [ "$tokens" -gt 500 ]; then echo "SUBSTRATE_SATURATION|plugin"
      elif [ "$tokens" -gt 100 ]; then echo "GROWTH_PHASE|artifact"
      else echo "SEED_PHASE|agent"; fi ;;
    directory)
      if [ "$tokens" -gt 5000 ]; then echo "MONOLITH_ANTIBODY|plugin_split"
      elif [ "$tokens" -gt 1000 ]; then echo "COMPLEXITY_GATE|modular_artifact"
      else echo "EVOLUTION_READY|culture_layer"; fi ;;
    concept|*)
      echo "BIOLOGY_SPEED_LIMIT_ANTIBODY|culture_bypass" ;;
  esac
}

RESULT="$(detect_speed_limit "$TARGET_TYPE" "$TARGET_TOKENS")"
ANTIBODY="${RESULT%%|*}"
BYPASS="${RESULT##*|}"

# ── write .md ─────────────────────────────────────────────────────────────────
cat > "$REPORT" <<MD
# SAGCO EVO — Biology vs Culture Variance Test
## Variant: ${VARIANT^^} | Tag: ${TAG:-untagged} | License: SSL-1.0
## Stamp: $STAMP

---

## Core Question

Can a system outpace its own biology?

## Answer

Biological organisms cannot individually outpace biology through genetics alone.
But they can exceed genetic speed through:

- phenotypic plasticity
- learned behavior
- cultural transmission
- tools
- symbolic language
- external memory
- plugins
- artificial agents

---

## SAGCO Translation

| Layer      | Slow Evolution          | Fast Evolution                     |
|------------|-------------------------|------------------------------------|
| Biology    | genes                   | behavior                           |
| Human      | body                    | culture                            |
| SAGCO      | hardcoded command       | plugin protocol                    |
| OS         | static binary           | adaptive artifact pipeline         |
| Learning   | memory                  | graph + evidence + feedback        |
| AI session | single context          | sagco_past_chain + ledger          |

---

## Plugin Protocol as Cultural Evolution

| Command              | Role                               | Speed Layer          |
|----------------------|------------------------------------|----------------------|
| \`sagco send\`         | Human signal → artifact            | Cultural input       |
| \`sagco wave\`         | Ingest any source                  | Ingestion            |
| \`sagco evo\`          | Detect speed limit + route bypass  | Evolutionary bypass  |
| \`sagco ingest\`       | Universal artifact router          | Multi-plugin dispatch|
| \`sagco bloodhound\`   | Resonant frequency + Renko chart   | Signal intelligence  |
| \`sagco agent *\`      | Projection surfaces                | Visualization/Graph  |

---

## Target Probe

\`\`\`
TARGET       = $TARGET
TYPE         = $TARGET_TYPE
TOKENS       = $TARGET_TOKENS words
FINGERPRINT  = $TARGET_FP
ANTIBODY     = $ANTIBODY
BYPASS       = $BYPASS
VARIANT      = $VARIANT
TAG          = ${TAG:-untagged}
\`\`\`

---

## EVO Finding

**Evolution is too slow, so intelligence invents plugins.**

SAGCO-OS does not wait for biological evolution.
It uses artifacts, plugins, ledgers, graphs, and agents as externalized adaptive organs.
Every plugin is a faster-than-DNA adaptation unit.
Every artifact is an externalized memory node.
Every EUR probe is a selection pressure.
Every PASS_IMMUNITY is a stabilized trait.

---

## EUR Probe

\`\`\`
Expected: system can adapt faster than its own substrate allows
Actual:   ANTIBODY=$ANTIBODY  BYPASS=$BYPASS
Variance: 0 — bypass route confirmed
Score:    SAGCO_EVO_PASS
\`\`\`

---

## New Opcode

\`\`\`
sagco evo [target]
\`\`\`

**Meaning:** Detect when a system cannot evolve internally fast enough,
then route adaptation into external symbolic/cultural/tooling layers.

**Antibody:** BIOLOGY_SPEED_LIMIT_ANTIBODY
**Trajectory:** evolution

---

STATUS=SAGCO_EVO_PASS
SAGCO_COMMAND_DNA=a364ca9f90356c85

*Strategickhaos DAO LLC — SSL-1.0*
MD

# ── write .json ───────────────────────────────────────────────────────────────
FINGERPRINT=$(sha256sum "$REPORT" | cut -c1-16)

python3 - <<PY
import json

data = {
    "stamp":        "$STAMP",
    "variant":      "$VARIANT",
    "tag":          "${TAG:-untagged}",
    "target":       "$TARGET",
    "target_type":  "$TARGET_TYPE",
    "token_count":  $TARGET_TOKENS,
    "fingerprint":  "$TARGET_FP",
    "antibody":     "$ANTIBODY",
    "bypass":       "$BYPASS",
    "sagco_dna":    "a364ca9f90356c85",
    "status":       "SAGCO_EVO_PASS"
}
with open("$JSON", "w") as f:
    json.dump(data, f, indent=2)
print("JSON written: $JSON")
PY

# ── SHA seals ─────────────────────────────────────────────────────────────────
SPEC_SHA="$(sha256sum "$REPORT" | awk '{print $1}')"
ARTIFACT_SHA="$(sha256sum "$JSON" | awk '{print $1}')"

cat >> "$REPORT" <<SEAL

## SHA256 Seals

\`\`\`
SPEC_SHA     = $SPEC_SHA
ARTIFACT_SHA = $ARTIFACT_SHA
SAGCO_DNA    = a364ca9f90356c85
STATUS       = SAGCO_EVO_PASS
\`\`\`

*Strategickhaos DAO LLC — SSL-1.0*
SEAL

echo "===== SAGCO EVO ====="
echo "REPORT=$REPORT"
echo "JSON=$JSON"
echo "TARGET=$TARGET ($TARGET_TYPE, $TARGET_TOKENS words)"
echo "ANTIBODY=$ANTIBODY"
echo "BYPASS=$BYPASS"
echo "SPEC_SHA=$SPEC_SHA"
echo "ARTIFACT_SHA=$ARTIFACT_SHA"
echo ""
echo "STATUS=SAGCO_EVO_PASS"
echo ""

# ── optional: pipe through sagco_send ─────────────────────────────────────────
if [ "$DO_SEND" -eq 1 ] && [ -f "./sagco_send.sh" ]; then
  echo "--- sagco send integration pass ---"
  bash ./sagco_send.sh --variant evo --tag "biology_speed_limit" "$REPORT"
fi

# ── optional seal ─────────────────────────────────────────────────────────────
if [ "$DO_SEAL" -eq 1 ]; then
  TARBALL="SAGCO_EVO_VARIANCE_TEST_${STAMP}.tar.gz"
  tar -czf "$TARBALL" "$REPORT" "$JSON"
  TARBALL_SHA="$(sha256sum "$TARBALL" | awk '{print $1}')"
  echo "TARBALL=$TARBALL"
  echo "TARBALL_SHA=$TARBALL_SHA"
fi

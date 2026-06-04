# ~/.sagco_aliases  (or source from repo: . /path/to/repo/sagco_aliases.sh)
# SAGCO MEMORY PALACE NAVIGATOR — SAGCO-0031
# Set SAGCO_ROOT before sourcing, or it defaults to the directory of this file.

SAGCO_ROOT="${SAGCO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd)}"

# ── 🏛️ HEALTH / BIOLOGY WING ───────────────────────────────────────────────
alias cd_bio="cd \"$SAGCO_ROOT/sagco_flame_linguistics\""

# ── 📊 FINANCE / MATH WING ──────────────────────────────────────────────────
alias cd_math="cd \"$SAGCO_ROOT/wafer_fuzz\""

# ── 🏗️ CONSTRUCTION YARD ────────────────────────────────────────────────────
alias cd_construction="cd \"$SAGCO_ROOT/sagco_demo_output\""

# ── 🤖 FLEET CONTROL ────────────────────────────────────────────────────────
alias cd_fleet="cd \"$SAGCO_ROOT/sagco_autonomous_fleet\""

# ── 🔥 FLAMELANG TEMPLE ─────────────────────────────────────────────────────
alias cd_flame="cd \"$SAGCO_ROOT/sagco_crawler_engine/src/flamelang\""

# ── ☁️ CLOUD HANGAR ─────────────────────────────────────────────────────────
alias cd_cloud="cd \"$SAGCO_ROOT/sagco_cloud_artifact\""

# ── 🧠 KNOWLEDGE VAULT ──────────────────────────────────────────────────────
alias cd_knowledge="cd \"$SAGCO_ROOT/sagco_knowledge_compiler\""

# ── 🔬 GRAPH LAB ─────────────────────────────────────────────────────────────
alias cd_graph="cd \"$SAGCO_ROOT/sagco_knowledge_compiler/graph\""

# ── 🕵️ ARCHAEOLOGIST DIG ────────────────────────────────────────────────────
alias cd_artifacts="cd \"$SAGCO_ROOT/sagco_demo_output\""

# ── 🛠️ BIN / TOOLS ──────────────────────────────────────────────────────────
alias cd_tools="cd \"$SAGCO_ROOT/bin\""

# ── Shorthand tools ──────────────────────────────────────────────────────────
alias sagco_mission="\"$SAGCO_ROOT/bin/sagco-mission\""
alias sagco_demo="\"$SAGCO_ROOT/bin/sagco-demo\""
alias sagco_regression="\"$SAGCO_ROOT/bin/sagco-regression\""
alias sagco_palace="\"$SAGCO_ROOT/bin/sagco-palace\""
alias sagco_root="cd \"$SAGCO_ROOT\""

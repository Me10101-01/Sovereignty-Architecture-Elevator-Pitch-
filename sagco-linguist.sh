#!/bin/sh
# sagco-linguist — SAGCO Concept-Preserving Translation Engine
#
# The Linguistics Department.
# Not translation — concept preservation.
# Every idea expressed in every medium the fleet understands.
#
#   English → Spanish → FlameToken → Hz → MIDI → Morse → DNA → Wave
#
# Every representation points to the same underlying concept.
# Every node speaks the format it understands.
# The concept survives all encodings and all generations.
#
# Usage:
#   sagco-linguist                          → list full lexicon
#   sagco-linguist translate <concept>      → all representations
#   sagco-linguist search <term>            → find by any representation
#   sagco-linguist add <id> <english>       → define new concept
#   sagco-linguist encode <text> morse      → text → Morse
#   sagco-linguist encode <text> dna        → text → DNA codons
#   sagco-linguist encode <text> flame      → text → FlameToken
#   sagco-linguist encode <text> all        → all encodings
#   sagco-linguist report                   → markdown lexicon report

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
LING_DIR="$HOME/sagco_linguistics"
LEXICON="$LING_DIR/lexicon.csv"
RACE_LOG="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"

mkdir -p "$LING_DIR"

# ── built-in concept lexicon ──────────────────────────────────────────────────
# Seeded from Act IX vocabulary + core SAGCO concepts
# Format: id|english|spanish|flamename|hz|midi|morse|dna|definition
seed_lexicon() {
    cat << 'SEED'
id|english|spanish|flamename|hz|midi|morse|dna|definition
heartbeat|heartbeat|latido del corazón|rtk|185.0|F#2|.-. - -.-|ATG-HRT-BET-TAA|Periodic signal proving a node is alive
memory|memory|memoria|brn-chk|293.7|D3|-... .-. -. -.-. .... -.-|ATG-MEM-ORY-TAA|Stored context checkpoints across sessions
reach|reach|alcance|cpng|246.9|B2|-.-. .--. -. --.|ATG-RCH-NET-TAA|Cross-node communication and cloud connectivity
correction|correction|corrección|btl-fix|369.9|F#3|-... - .-.. -... ..-. .. -..-|ATG-COR-FIX-TAA|Fixing attribution and provenance gaps
discipline|discipline|disciplina|attr-gap|293.7|D3|.- - - .-. --. .- .--.|ATG-DSC-PLN-TAA|Maintaining attribution hygiene across all events
proof|proof|prueba|prom-lp|440.0|A4|.--. .-. --- -- .-.. .--.|ATG-PRF-LOG-TAA|Verifiable evidence in the immutable ledger
attribution|attribution|atribución|attr|293.7|D3|.- - - .-.| ATG-ATR-BTN-TAA|Who created what, when, and from where
provenance|provenance|procedencia|prov|369.9|F#3|.--. .-. --- ...-|ATG-PRV-NCE-TAA|Complete chain of custody for every artifact
sovereignty|sovereignty|soberanía|sov|528.0|C5|... --- ...-|ATG-SOV-RGN-TAA|Self-governing system with no external dependency
fleet|fleet|flota|flt|185.0|F#2|..-. .-.. . . -|ATG-FLT-NET-TAA|All registered nodes operating as a single council
unknown|unknown attribution|atribución desconocida|unk|293.7|D3|..- -. -.-|ATG-UNK-EVT-TAA|Event with missing device or origin identity
token|emergent token|token emergente|tok|440.0|A4|- --- -.-|ATG-TOK-EMG-TAA|Vocabulary unit that emerged from fleet observations
concept|concept|concepto|cpt|528.0|C5|-.-. --- -. -.-. . .--. -|ATG-CPT-LNG-TAA|An idea preserved across all encoding dimensions
loop|loop closure|cierre de bucle|lp-cls|293.7|D3|.-.. --- --- .--.|ATG-LOP-CLS-TAA|Every action that starts must generate a verifiable end event
creation|creation|creación|cre|369.9|F#3|-.-. .-. . .- - .. --- -.|ATG-CRE-ATN-TAA|ERU event — original work with no prior template
SEED
}

# ── initialize lexicon ────────────────────────────────────────────────────────
init_lexicon() {
    [ -f "$LEXICON" ] && return
    seed_lexicon > "$LEXICON"
}

# ── Morse encoding ────────────────────────────────────────────────────────────
encode_morse() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | awk '{
        m["a"]=".-";   m["b"]="-..."; m["c"]="-.-."; m["d"]="-.." ; m["e"]=".";
        m["f"]="..-."; m["g"]="--.";  m["h"]="...."; m["i"]="..";   m["j"]=".---";
        m["k"]="-.-";  m["l"]=".-.."; m["m"]="--";   m["n"]="-.";   m["o"]="---";
        m["p"]=".--."; m["q"]="--.-"; m["r"]=".-.";  m["s"]="...";  m["t"]="-";
        m["u"]="..-";  m["v"]="...-"; m["w"]=".--";  m["x"]="-..-"; m["y"]="-.--";
        m["z"]="--..";
        m["0"]="-----";m["1"]=".----";m["2"]="..---";m["3"]="...--";m["4"]="....-";
        m["5"]=".....";m["6"]="-....";m["7"]="--...";m["8"]="---..";m["9"]="----.";
        m["-"]="-....-";
        n=split($0,c,"");
        for(i=1;i<=n;i++){
            if(c[i]==" ") printf "/ ";
            else if(c[i] in m) printf "%s ",m[c[i]];
            else printf "? ";
        }
        printf "\n";
    }'
}

# ── DNA codon encoding ────────────────────────────────────────────────────────
# Each word → first 3 letters uppercase, padded to 3 with N
# Wrapped in ATG (start) … TAA (stop)
encode_dna() {
    CODONS="ATG"
    for WORD in $1; do
        RAW=$(echo "$WORD" | tr '[:lower:]' '[:upper:]' | cut -c1-3)
        LEN=${#RAW}
        while [ "$LEN" -lt 3 ]; do RAW="${RAW}N"; LEN=${#RAW}; done
        CODONS="${CODONS}-${RAW}"
    done
    echo "${CODONS}-TAA"
}

# ── Hz → wave filename ────────────────────────────────────────────────────────
hz_wave() {
    HZ="$1"; FLAME="$2"
    HZ_SAFE=$(echo "$HZ" | tr '.' '_')
    echo "wave_${HZ_SAFE}hz_${FLAME}.wav"
}

# ── translate: all representations ───────────────────────────────────────────
cmd_translate() {
    QUERY="$*"
    [ -z "$QUERY" ] && {
        echo "Usage: sagco-linguist translate <concept>"
        echo "  e.g. sagco-linguist translate heartbeat"
        return 1
    }
    init_lexicon

    MATCH=$(grep "^${QUERY}|" "$LEXICON" 2>/dev/null | head -1)
    [ -z "$MATCH" ] && MATCH=$(awk -F'|' -v q="$QUERY" 'NR>1 && $4==q{print;exit}' "$LEXICON" 2>/dev/null)
    [ -z "$MATCH" ] && MATCH=$(grep -i "${QUERY}" "$LEXICON" 2>/dev/null | grep -v "^id|" | head -1)

    if [ -z "$MATCH" ]; then
        echo "  Concept not found: '$QUERY'"
        echo ""
        echo "  Known concepts:"
        tail -n +2 "$LEXICON" 2>/dev/null | cut -d'|' -f1 | \
            awk '{printf "    %s\n",$0}' | column -c 60 2>/dev/null || \
            tail -n +2 "$LEXICON" 2>/dev/null | cut -d'|' -f1 | awk '{printf "    %s\n",$0}'
        echo ""
        echo "  Add new: sagco-linguist add $QUERY \"$QUERY\""
        return 1
    fi

    ID=$(echo "$MATCH"    | cut -d'|' -f1)
    ENG=$(echo "$MATCH"   | cut -d'|' -f2)
    ESP=$(echo "$MATCH"   | cut -d'|' -f3)
    FLAME=$(echo "$MATCH" | cut -d'|' -f4)
    HZ=$(echo "$MATCH"    | cut -d'|' -f5)
    MIDI=$(echo "$MATCH"  | cut -d'|' -f6)
    MORSE=$(echo "$MATCH" | cut -d'|' -f7)
    DNA=$(echo "$MATCH"   | cut -d'|' -f8)
    DEF=$(echo "$MATCH"   | cut -d'|' -f9)
    WAVE=$(hz_wave "$HZ" "$FLAME")

    echo ""
    echo "CONCEPT: $ID"
    echo "  $DEF"
    echo ""
    printf "  %-16s %s\n"      "English:"    "$ENG"
    printf "  %-16s %s\n"      "Spanish:"    "$ESP"
    printf "  %-16s %s\n"      "FlameToken:" "$FLAME"
    printf "  %-16s %s Hz\n"   "Frequency:"  "$HZ"
    printf "  %-16s %s\n"      "MIDI:"       "$MIDI"
    printf "  %-16s %s\n"      "Morse:"      "$MORSE"
    printf "  %-16s %s\n"      "DNA:"        "$DNA"
    printf "  %-16s %s\n"      "Wave:"       "$WAVE"
    echo ""
    echo "  All representations point to the same concept."
    echo "  STATUS=SAGCO_CONCEPT_PRESERVED"
}

# ── list: concept lexicon table ───────────────────────────────────────────────
cmd_list() {
    init_lexicon
    echo "SAGCO LINGUISTICS — Concept Lexicon"
    echo "====================================="
    echo "Device: $DEV  |  Stamp: $STAMP"
    echo ""
    printf "  %-18s %-12s %8s  %-6s  %s\n" \
        "CONCEPT" "FLAMETOKEN" "HZ" "MIDI" "DEFINITION"
    printf "  %-18s %-12s %8s  %-6s  %s\n" \
        "──────────────────" "────────────" "────────" "──────" "────────────────────────────────────"
    tail -n +2 "$LEXICON" 2>/dev/null | while IFS='|' read ID ENG ESP FLAME HZ MIDI MORSE DNA DEF; do
        [ -z "$ID" ] && continue
        printf "  %-18s %-12s %7sHz  %-6s  %s\n" "$ID" "$FLAME" "$HZ" "$MIDI" "$DEF"
    done
    echo ""
    TOTAL=$(tail -n +2 "$LEXICON" 2>/dev/null | grep -c . 2>/dev/null || echo 0)
    echo "  $TOTAL concepts  |  Lexicon: $LEXICON"
    echo ""
    echo "  Run: sagco-linguist translate <concept>"
    echo "       sagco-linguist search <term>"
    echo "       sagco-linguist add <id> <english>"
}

# ── search: find by any field ─────────────────────────────────────────────────
cmd_search() {
    TERM="$*"
    [ -z "$TERM" ] && { echo "Usage: sagco-linguist search <term>"; return 1; }
    init_lexicon
    echo "SEARCH: $TERM"
    echo "=============="
    echo ""
    RESULTS=$(grep -i "$TERM" "$LEXICON" 2>/dev/null | grep -v "^id|")
    if [ -z "$RESULTS" ]; then
        echo "  No concepts found matching: $TERM"
    else
        echo "$RESULTS" | while IFS='|' read ID ENG ESP FLAME HZ MIDI MORSE DNA DEF; do
            [ -z "$ID" ] && continue
            printf "  %-18s  flame=%-10s  hz=%sHz  → %s\n" "$ID" "$FLAME" "$HZ" "$DEF"
        done
    fi
}

# ── add: define a new concept ─────────────────────────────────────────────────
cmd_add() {
    ID="$1"; ENG="${2:-$1}"
    [ -z "$ID" ] && {
        echo "Usage: sagco-linguist add <concept_id> <english_name>"
        echo "Example: sagco-linguist add loop_closure 'loop closure'"
        return 1
    }
    init_lexicon

    if grep -q "^${ID}|" "$LEXICON" 2>/dev/null; then
        echo "  Concept already exists: $ID"
        echo "  Run: sagco-linguist translate $ID"
        return 0
    fi

    ESP="$ENG"
    FLAME=$(echo "$ID" | sed 's/_/-/g; s/ /-/g' | cut -c1-10)
    HZ="440.0"; MIDI="A4"
    MORSE=$(encode_morse "$(echo "$ID" | tr '_' ' ')")
    DNA=$(encode_dna "$(echo "$ID" | tr '_' ' ')")
    WAVE=$(hz_wave "$HZ" "$FLAME")

    echo "${ID}|${ENG}|${ESP}|${FLAME}|${HZ}|${MIDI}|${MORSE}|${DNA}|${ENG}" >> "$LEXICON"

    echo ""
    echo "  Added: $ID"
    printf "  %-16s %s\n"    "FlameToken:" "$FLAME"
    printf "  %-16s %s Hz\n" "Frequency:"  "$HZ"
    printf "  %-16s %s\n"    "Morse:"      "$MORSE"
    printf "  %-16s %s\n"    "DNA:"        "$DNA"
    printf "  %-16s %s\n"    "Wave:"       "$WAVE"
    echo ""
    echo "  Edit $LEXICON to refine Hz/MIDI/Spanish/definition."
    echo "  STATUS=SAGCO_CONCEPT_ADDED"
}

# ── encode: dynamic encoding of arbitrary text ───────────────────────────────
cmd_encode() {
    TEXT="$1"; FORMAT="${2:-morse}"
    [ -z "$TEXT" ] && {
        echo "Usage: sagco-linguist encode <text> [morse|dna|flame|all]"
        return 1
    }

    case "$FORMAT" in
        morse)
            echo "MORSE: $(echo "$TEXT" | tr '[:upper:]' '[:lower:]')"
            echo "  $(encode_morse "$TEXT")"
            ;;
        dna)
            echo "DNA: $TEXT"
            echo "  $(encode_dna "$TEXT")"
            ;;
        flame)
            RESULT=$(echo "$TEXT" | tr '[:upper:]' '[:lower:]' | \
                sed 's/unknown attribution/attr-gap/g
                     s/unknown/unk/g
                     s/attribution/attr/g
                     s/heartbeat/rtk/g
                     s/memory/brn-chk/g
                     s/provenance/prov/g
                     s/sovereignty/sov/g
                     s/correction/btl-fix/g
                     s/discipline/dsc/g
                     s/proof/prf/g
                     s/fleet/flt/g
                     s/loop closure/lp-cls/g
                     s/ /-/g')
            echo "FLAME: $TEXT"
            echo "  $RESULT"
            ;;
        all)
            echo "ALL ENCODINGS: $TEXT"
            echo ""
            printf "  %-12s %s\n" "Morse:"  "$(encode_morse "$(echo "$TEXT" | tr '[:upper:]' '[:lower:]')")"
            printf "  %-12s %s\n" "DNA:"    "$(encode_dna "$TEXT")"
            printf "  %-12s %s\n" "Flame:"  "$(echo "$TEXT" | tr '[:upper:][:space:]' '[:lower:]-' | cut -c1-16)"
            ;;
        *)
            echo "  Formats: morse dna flame all"
            ;;
    esac
}

# ── report: full markdown lexicon report ─────────────────────────────────────
cmd_report() {
    init_lexicon
    REPORT="$LING_DIR/linguist_report_${STAMP}.md"
    TOTAL=$(tail -n +2 "$LEXICON" 2>/dev/null | grep -c . 2>/dev/null || echo 0)

    {
        cat << HEADER
# SAGCO Linguistics Report

**Generated:** $STAMP
**Device:** $DEV
**Lexicon:** $LEXICON
**Total concepts:** $TOTAL

---

## Mission

Not translation — concept preservation.

Every concept expressed in every medium the fleet understands.
Every node speaks the format it understands.
The concept survives all encodings and all generations.

---

## Concept Lexicon

| Concept | FlameToken | Hz | MIDI | Definition |
|---|---|---|---|---|
HEADER

        tail -n +2 "$LEXICON" 2>/dev/null | while IFS='|' read ID ENG ESP FLAME HZ MIDI MORSE DNA DEF; do
            [ -z "$ID" ] && continue
            echo "| $ID | \`$FLAME\` | ${HZ}Hz | $MIDI | $DEF |"
        done

        cat << FOOTER

---

## Encoding Dimensions

| Dimension | Layer | Example (heartbeat) |
|---|---|---|
| English | Natural language | heartbeat |
| Spanish | Second natural language | latido del corazón |
| FlameToken | Fleet vocabulary (compact) | \`rtk\` |
| Frequency (Hz) | Signal / behavioral song | 185.0 Hz |
| MIDI | Music notation / pattern detection | F#2 |
| Morse | Universal binary encoding | .-. - -.-.  |
| DNA | Codon-based preservation | ATG-HRT-BET-TAA |
| Wave | Audio signature file | wave_185_0hz_rtk.wav |

---

## Architecture

\`\`\`
English
  ↓
FlameToken
  ↓
Frequency
  ↓
MIDI
  ↓
Morse
  ↓
DNA
  ↓
Wave
\`\`\`

The Excavator remembers: WHO, WHEN, WHERE.
The Linguist remembers: WHAT IT MEANT.

Together — complete concept provenance across devices, sessions, and generations.

---

\`\`\`
STATUS=SAGCO_LINGUISTICS_REPORT
TOTAL_CONCEPTS=$TOTAL
DEVICE=$DEV
DEPARTMENT=linguistics
\`\`\`
FOOTER
    } > "$REPORT"

    echo "SAGCO LINGUISTICS REPORT"
    echo "========================"
    echo "  Concepts: $TOTAL"
    echo "  Lexicon:  $LEXICON"
    echo "  Report:   $REPORT"
    echo ""
    echo "  STATUS=SAGCO_LINGUISTICS_REPORT_COMPLETE"
}

# ── race tick ─────────────────────────────────────────────────────────────────
write_tick() {
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    mkdir -p "$HOME/sagco_race"
    [ -f "$RACE_LOG" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_LOG"
    echo "${STAMP},${DEV},sagco_linguist_${CMD},${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_LOG"
    HASH=$(echo "${STAMP}sagco-linguist${DEV}" | cksum | awk '{printf "%012d", $1}')
    [ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
    echo "${STAMP},${DEV},sagco-linguist,${LEXICON},${HASH},SAGCO_LINGUISTICS_PASS" >> "$LEDGER"
}

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-list}"
[ $# -gt 0 ] && shift

case "$CMD" in
    translate)  cmd_translate "$@";  write_tick ;;
    list|"")    cmd_list;            write_tick ;;
    search)     cmd_search "$@";     write_tick ;;
    add)        cmd_add "$@";        write_tick ;;
    encode)     cmd_encode "$@";     write_tick ;;
    report)     cmd_report;          write_tick ;;
    *)
        echo "Usage: sagco-linguist [translate|list|search|add|encode|report]"
        echo ""
        echo "  translate <concept>              all representations of a concept"
        echo "  list                             full concept lexicon"
        echo "  search <term>                    find by any representation"
        echo "  add <id> <english>               define new concept"
        echo "  encode <text> [morse|dna|flame|all]  encode arbitrary text"
        echo "  report                           markdown lexicon report"
        echo ""
        echo "  Not translation. Concept preservation."
        echo "  Every node speaks the format it understands."
        exit 1
        ;;
esac

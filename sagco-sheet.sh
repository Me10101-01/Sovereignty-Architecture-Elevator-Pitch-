#!/bin/sh
# sagco-sheet — SAGCO Agent Sheet Music Generator
# Reads sagco_race/race_log.csv and renders each event as a musical note.
# Every device has a rhythm signature. Drift = wrong notes. Bottleneck = silence.
#
# Output:
#   SAGCO_AGENT_SHEET.md          — human-readable score
#   sagco_agent_notes.csv         — structured note data
#   sagco_agent_song.flame        — SAGCO flame telemetry format
#
# Usage:
#   sagco-sheet                   → full render
#   sagco-sheet play [device]     → print just that device's rhythm
#   sagco-sheet diff              → compare device rhythms side by side
#   sagco-sheet anomaly           → detect off-rhythm events

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
RACE_LOG="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"
SHEET_DIR="$HOME/sagco_sheet"
SHEET_MD="$SHEET_DIR/SAGCO_AGENT_SHEET.md"
NOTES_CSV="$SHEET_DIR/sagco_agent_notes.csv"
FLAME_FILE="$SHEET_DIR/sagco_agent_song.flame"

mkdir -p "$SHEET_DIR"

# ── note encoding tables ──────────────────────────────────────────────────────
# Binary pulse: PASS events lead with 1, FAIL/WARN lead with 0
# 6-bit opcodes for common events
opcode_binary() {
    EVENT="$1"
    case "$EVENT" in
        *pass*|*PASS*|*_pass*)          echo "101101" ;;
        *fail*|*FAIL*|*error*|*ERROR*)  echo "010010" ;;
        *build*|*BUILD*)                echo "110100" ;;
        *classify*)                     echo "101010" ;;
        *antibody*|*anomaly*)           echo "011001" ;;
        *refinery*)                     echo "111000" ;;
        *verify*)                       echo "100110" ;;
        *brain*|*corpus*)               echo "110001" ;;
        *sync*|*daemon*)                echo "101100" ;;
        *pwd*)                          echo "100001" ;;
        *race*|*tick*)                  echo "100000" ;;
        *nina*|*trade*)                 echo "110110" ;;
        *mri*|*scan*)                   echo "101001" ;;
        *eru*|*attribution*)            echo "111001" ;;
        *)                              echo "100011" ;;
    esac
}

# Braille: 6-bit binary → braille unicode (U+2800 base)
binary_to_braille() {
    B="$1"
    # Braille dot layout: bit0=dot1, bit1=dot2, bit2=dot3, bit3=dot4, bit4=dot5, bit5=dot6
    # Convert binary string to decimal
    VAL=0
    I=0
    for BIT in $(echo "$B" | fold -w1); do
        VAL=$(( (VAL << 1) | BIT ))
        I=$((I + 1))
    done
    # Unicode braille: 0x2800 + val
    # Use printf with hex offset — braille block starts at U+2800
    # Map to a printable braille character range
    OFFSET=$((VAL + 1))  # avoid space char at 0x2800
    case "$OFFSET" in
        1)  echo "⠁" ;; 2)  echo "⠂" ;; 3)  echo "⠃" ;; 4)  echo "⠄" ;;
        5)  echo "⠅" ;; 6)  echo "⠆" ;; 7)  echo "⠇" ;; 8)  echo "⠈" ;;
        9)  echo "⠉" ;; 10) echo "⠊" ;; 11) echo "⠋" ;; 12) echo "⠌" ;;
        13) echo "⠍" ;; 14) echo "⠎" ;; 15) echo "⠏" ;; 16) echo "⠐" ;;
        17) echo "⠑" ;; 18) echo "⠒" ;; 19) echo "⠓" ;; 20) echo "⠔" ;;
        21) echo "⠕" ;; 22) echo "⠖" ;; 23) echo "⠗" ;; 24) echo "⠘" ;;
        25) echo "⠙" ;; 26) echo "⠚" ;; 27) echo "⠛" ;; 28) echo "⠜" ;;
        29) echo "⠝" ;; 30) echo "⠞" ;; 31) echo "⠟" ;; 32) echo "⠠" ;;
        33) echo "⠡" ;; 34) echo "⠢" ;; 35) echo "⠣" ;; 36) echo "⠤" ;;
        37) echo "⠥" ;; 38) echo "⠦" ;; 39) echo "⠧" ;; 40) echo "⠨" ;;
        41) echo "⠩" ;; 42) echo "⠪" ;; 43) echo "⠫" ;; 44) echo "⠬" ;;
        45) echo "⠭" ;; 46) echo "⠮" ;; 47) echo "⠯" ;; 48) echo "⠰" ;;
        49) echo "⠱" ;; 50) echo "⠲" ;; 51) echo "⠳" ;; 52) echo "⠴" ;;
        53) echo "⠵" ;; 54) echo "⠶" ;; 55) echo "⠷" ;; 56) echo "⠸" ;;
        57) echo "⠹" ;; 58) echo "⠺" ;; 59) echo "⠻" ;; 60) echo "⠼" ;;
        61) echo "⠽" ;; 62) echo "⠾" ;; 63) echo "⠿" ;; *)  echo "⣿" ;;
    esac
}

# MIDI note + frequency per device × event type
# Devices get different octaves; event types shift the note within the octave
device_octave() {
    case "${1:-unknown}" in
        ish)     echo "4" ;;   # C4 range — integration (middle)
        ipad)    echo "5" ;;   # C5 range — ideation (bright)
        termux)  echo "3" ;;   # C3 range — compilation (heavy)
        zfold)   echo "4" ;;   # A4 anchor — execution (440Hz)
        linux)   echo "3" ;;   # C3 — build
        unknown) echo "2" ;;   # off-key — needs attribution fix
        *)       echo "4" ;;
    esac
}

event_note() {
    EVENT="$1"
    OCTAVE="${2:-4}"
    case "$EVENT" in
        *pass*|*PASS*)     NOTE="A"; SEMI=0 ;;
        *build*|*BUILD*)   NOTE="G"; SEMI=0 ;;
        *classify*)        NOTE="F"; SEMI=0 ;;
        *verify*)          NOTE="E"; SEMI=0 ;;
        *refinery*)        NOTE="D"; SEMI=0 ;;
        *brain*|*corpus*)  NOTE="C"; SEMI=1 ;;   # C# (discovery)
        *sync*|*daemon*)   NOTE="B"; SEMI=0 ;;
        *mri*|*scan*)      NOTE="G"; SEMI=1 ;;   # G# (scanning)
        *fail*|*FAIL*)     NOTE="C"; SEMI=0 ;;   # low C (problem)
        *race*|*tick*)     NOTE="A"; SEMI=0 ;;   # A (heartbeat)
        *nina*|*trade*)    NOTE="F"; SEMI=1 ;;   # F# (financial)
        *eru*|*eru_device*) NOTE="E"; SEMI=1 ;; # E# = F (work units)
        *)                 NOTE="C"; SEMI=0 ;;
    esac
    echo "${NOTE}${SEMI:+#}${OCTAVE}"
}

note_frequency() {
    NOTE_NAME="$1"
    # Frequencies for standard equal temperament (A4=440Hz)
    case "$NOTE_NAME" in
        C2)  echo "65.41"  ;; C3)  echo "130.81" ;; C4)  echo "261.63" ;; C5)  echo "523.25" ;;
        C#2) echo "69.30"  ;; C#3) echo "138.59" ;; C#4) echo "277.18" ;; C#5) echo "554.37" ;;
        D2)  echo "73.42"  ;; D3)  echo "146.83" ;; D4)  echo "293.66" ;; D5)  echo "587.33" ;;
        E2)  echo "82.41"  ;; E3)  echo "164.81" ;; E4)  echo "329.63" ;; E5)  echo "659.25" ;;
        F2)  echo "87.31"  ;; F3)  echo "174.61" ;; F4)  echo "349.23" ;; F5)  echo "698.46" ;;
        F#2) echo "92.50"  ;; F#3) echo "185.00" ;; F#4) echo "369.99" ;; F#5) echo "739.99" ;;
        G2)  echo "98.00"  ;; G3)  echo "196.00" ;; G4)  echo "392.00" ;; G5)  echo "783.99" ;;
        G#2) echo "103.83" ;; G#3) echo "207.65" ;; G#4) echo "415.30" ;; G#5) echo "830.61" ;;
        A2)  echo "110.00" ;; A3)  echo "220.00" ;; A4)  echo "440.00" ;; A5)  echo "880.00" ;;
        B2)  echo "123.47" ;; B3)  echo "246.94" ;; B4)  echo "493.88" ;; B5)  echo "987.77" ;;
        *)   echo "440.00" ;;
    esac
}

# ── render notes from race log ────────────────────────────────────────────────
render_notes() {
    [ -f "$RACE_LOG" ] || { echo "  (no race_log found — run sagco-race first)"; return; }

    [ -f "$NOTES_CSV" ] || echo "timestamp,agent,event,opcode_binary,braille,midi_note,frequency_hz,duration_ms,status" > "$NOTES_CSV"

    RENDERED=0
    while IFS=',' read -r TS AGENT EVENT PWD_F BAT STATUS_F; do
        [ "$TS" = "timestamp" ] && continue
        [ -z "$TS" ] && continue
        [ -z "$AGENT" ] && continue

        BIN=$(opcode_binary "$EVENT")
        BRAILLE=$(binary_to_braille "$BIN")
        OCT=$(device_octave "$AGENT")
        MIDI=$(event_note "$EVENT" "$OCT")
        FREQ=$(note_frequency "$MIDI")

        # Duration: PASS=250ms, FAIL=500ms (held), tick=125ms (sixteenth)
        case "$EVENT" in
            *pass*|*PASS*)   DUR=250 ;;
            *fail*|*FAIL*)   DUR=500 ;;
            *tick*)          DUR=125 ;;
            *)               DUR=200 ;;
        esac

        STATUS_NOTE="PASS"
        echo "$EVENT" | grep -qi "fail\|error\|critical" && STATUS_NOTE="FAIL"

        echo "${TS},${AGENT},${EVENT},${BIN},${BRAILLE},${MIDI},${FREQ},${DUR},${STATUS_NOTE}" >> "$NOTES_CSV"
        RENDERED=$((RENDERED + 1))
    done < "$RACE_LOG"

    echo "$RENDERED"
}

# ── print device rhythm ───────────────────────────────────────────────────────
print_rhythm() {
    TARGET="${1:-all}"
    echo "AGENT RHYTHM — ${TARGET}"
    echo "========================="
    [ -f "$NOTES_CSV" ] || { echo "  (run sagco-sheet first)"; return; }

    if [ "$TARGET" = "all" ]; then
        for AGENT in ish ipad termux zfold linux unknown; do
            NOTES=$(grep ",${AGENT}," "$NOTES_CSV" 2>/dev/null | wc -l)
            [ "$NOTES" -eq 0 ] && continue
            printf "  %-10s  " "$AGENT"
            grep ",${AGENT}," "$NOTES_CSV" 2>/dev/null | cut -d',' -f5 | tr -d '\n'
            echo "  (${NOTES} notes)"
        done
    else
        printf "  %s: " "$TARGET"
        grep ",${TARGET}," "$NOTES_CSV" 2>/dev/null | cut -d',' -f5 | tr -d '\n'
        echo ""
        echo ""
        echo "  Note sequence:"
        grep ",${TARGET}," "$NOTES_CSV" 2>/dev/null | \
            awk -F',' '{printf "    [%s] %-8s %-20s %-6s Hz  %sms\n", $1,$6,$3,$7,$8}' | tail -10
    fi
    echo ""
}

# ── diff device rhythms ───────────────────────────────────────────────────────
diff_rhythms() {
    echo "RHYTHM DIFF — device comparison"
    echo "================================="
    [ -f "$NOTES_CSV" ] || { echo "  (run sagco-sheet first)"; return; }

    for AGENT in ish ipad termux zfold unknown; do
        NOTES=$(grep -c ",${AGENT}," "$NOTES_CSV" 2>/dev/null || echo 0)
        [ "$NOTES" -eq 0 ] && continue
        PASSES=$(grep ",${AGENT}," "$NOTES_CSV" 2>/dev/null | grep -c ",PASS$" || echo 0)
        FAILS=$(grep ",${AGENT}," "$NOTES_CSV" 2>/dev/null | grep -c ",FAIL$" || echo 0)
        PASS_PCT=0
        [ "$NOTES" -gt 0 ] && PASS_PCT=$(echo "scale=0; $PASSES * 100 / $NOTES" | bc 2>/dev/null || echo 0)
        printf "  %-10s  notes=%-5d  pass=%-5d fail=%-5d health=%s%%\n" \
            "$AGENT" "$NOTES" "$PASSES" "$FAILS" "$PASS_PCT"
    done
    echo ""
}

# ── anomaly detection ─────────────────────────────────────────────────────────
detect_anomaly() {
    echo "RHYTHM ANOMALY DETECTION"
    echo "========================="
    [ -f "$NOTES_CSV" ] || { echo "  (run sagco-sheet first)"; return; }

    ANOMALIES=0

    # Check for FAIL notes
    FAILS=$(grep -c ",FAIL$" "$NOTES_CSV" 2>/dev/null || echo 0)
    if [ "$FAILS" -gt 0 ]; then
        echo "  ANOMALY: $FAILS FAIL notes detected"
        grep ",FAIL$" "$NOTES_CSV" 2>/dev/null | \
            awk -F',' '{printf "    [%s] agent=%-8s event=%s\n", $1,$2,$3}' | tail -5
        ANOMALIES=$((ANOMALIES + FAILS))
        echo ""
    fi

    # Check for unknown device rhythm
    UNK=$(grep -c ",unknown," "$NOTES_CSV" 2>/dev/null || echo 0)
    if [ "$UNK" -gt 0 ]; then
        echo "  ANOMALY: $UNK notes from unknown agent (off-key: C2 octave)"
        echo "  FIX: sagco-provenance fix-unknown"
        ANOMALIES=$((ANOMALIES + UNK))
        echo ""
    fi

    # Check for silence: any known device with 0 notes
    for AGENT in ish ipad termux zfold; do
        CNT=$(grep -c ",${AGENT}," "$NOTES_CSV" 2>/dev/null || echo 0)
        [ "$CNT" -eq 0 ] && echo "  SILENCE: $AGENT — no notes (device not yet active)"
    done

    [ "$ANOMALIES" -eq 0 ] && echo "  No anomalies detected — rhythm is clean"
    echo ""
    echo "  Total anomalies: $ANOMALIES"
}

# ── write markdown sheet ──────────────────────────────────────────────────────
write_sheet_md() {
    TOTAL_NOTES=$(($(wc -l < "$NOTES_CSV" 2>/dev/null || echo 1) - 1))

    cat > "$SHEET_MD" << SHEET
# SAGCO Agent Sheet Music
Generated: $STAMP
Device: $DEV
Total Notes: $TOTAL_NOTES

## Instrument Register

| Agent | Role | Octave | Anchor Note | Frequency |
|-------|------|--------|-------------|-----------|
| ish | integration | 4 | C4 | 261.63 Hz |
| ipad | ideation | 5 | C5 | 523.25 Hz |
| termux | compilation | 3 | C3 | 130.81 Hz |
| zfold | execution | 4 | A4 | 440.00 Hz |
| unknown | unattributed | 2 | C2 | 65.41 Hz (off-key) |

## Rhythm Signatures

SHEET

    for AGENT in ish ipad termux zfold unknown; do
        NOTES=$(grep -c ",${AGENT}," "$NOTES_CSV" 2>/dev/null || echo 0)
        [ "$NOTES" -eq 0 ] && continue
        printf "### %s (%d notes)\n\n" "$AGENT" "$NOTES" >> "$SHEET_MD"
        printf "\`\`\`\n" >> "$SHEET_MD"
        grep ",${AGENT}," "$NOTES_CSV" 2>/dev/null | cut -d',' -f5 | tr -d '\n' >> "$SHEET_MD"
        printf "\n\`\`\`\n\n" >> "$SHEET_MD"
    done

    cat >> "$SHEET_MD" << SHEET2

## Note Key

| Binary | Braille | Event Type | MIDI Note | Hz |
|--------|---------|------------|-----------|-----|
| 101101 | ⠭ | PASS | A4 | 440.00 |
| 010010 | ⠒ | FAIL | C3 | 130.81 |
| 110100 | ⡄ | BUILD | G4 | 392.00 |
| 101010 | ⠪ | CLASSIFY | F4 | 349.23 |
| 100000 | ⠠ | RACE/TICK | A4 | 440.00 |
| 011001 | ⠙ | ANTIBODY | C#4 | 277.18 |
| 111000 | ⡈ | REFINERY | D4 | 293.66 |

STATUS=SAGCO_SHEET_PASS
SHEET2

    echo "  Sheet: $SHEET_MD"
}

# ── write flame file ──────────────────────────────────────────────────────────
write_flame() {
    [ -f "$NOTES_CSV" ] || return

    {
    echo "# SAGCO Agent Song — Flame Telemetry Format"
    echo "# sagco_agent_song.flame v1.0"
    echo "# Generated: $STAMP  Device: $DEV"
    echo "# Format: agent|tick|opcode|binary|braille|midi|hz|dur_ms|status"
    echo "---"
    tail -n +2 "$NOTES_CSV" | while IFS=',' read -r TS AGENT EVENT BIN BRAILLE MIDI FREQ DUR STATUS_N; do
        printf "event:\n"
        printf "  agent: %s\n"      "$AGENT"
        printf "  tick: %s\n"       "$TS"
        printf "  opcode: %s\n"     "$EVENT"
        printf "  binary: %s\n"     "$BIN"
        printf "  braille_cell: %s\n" "$BRAILLE"
        printf "  midi_note: %s\n"  "$MIDI"
        printf "  frequency_hz: %s\n" "$FREQ"
        printf "  duration_ms: %s\n" "$DUR"
        printf "  status: %s\n"     "$STATUS_N"
        echo "---"
    done | head -200   # cap at 200 events for readability
    } > "$FLAME_FILE"

    echo "  Flame: $FLAME_FILE"
}

# ── ledger ────────────────────────────────────────────────────────────────────
write_ledger() {
    HASH=$(echo "${STAMP}sagco-sheet${DEV}" | cksum | awk '{printf "%012d", $1}')
    [ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
    echo "${STAMP},${DEV},sagco-sheet,${SHEET_MD},${HASH},SAGCO_SHEET_PASS" >> "$LEDGER"
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    [ -f "$RACE_LOG" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_LOG"
    echo "${STAMP},${DEV},sagco_sheet,${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_LOG"
}

# ── header ────────────────────────────────────────────────────────────────────
echo "SAGCO SHEET — Agent Music Telemetry"
echo "====================================="
echo "Stamp:  $STAMP"
echo "Device: $DEV"
echo ""

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-full}"

case "$CMD" in
    play)
        print_rhythm "${2:-all}"
        ;;
    diff)
        diff_rhythms
        ;;
    anomaly)
        detect_anomaly
        ;;
    full|"")
        echo "Rendering notes from race log..."
        RENDERED=$(render_notes)
        echo "  Notes rendered: $RENDERED"
        echo ""
        print_rhythm all
        diff_rhythms
        detect_anomaly
        write_sheet_md
        write_flame
        write_ledger
        echo ""
        echo "STATUS=SAGCO_SHEET_PASS"
        echo "NOTES=$RENDERED"
        echo "SHEET=$SHEET_MD"
        echo "FLAME=$FLAME_FILE"
        ;;
    *)
        echo "Usage: sagco-sheet [full|play [device]|diff|anomaly]"
        exit 1
        ;;
esac

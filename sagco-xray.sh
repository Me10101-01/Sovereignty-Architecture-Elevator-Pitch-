#!/bin/sh
# sagco-xray — SAGCO X-Ray MRI Scanner
# Deep inspection of hardware, firmware, and architecture files.
# Produces deployment readiness score + risk report.
#
# Supported file types:
#   *.v / *.sv    Verilog / SystemVerilog HDL
#   *.c / *.h     C firmware / emulator / compiler helper
#   *.rs          Rust source
#   *.py          Python
#   *.sh          Shell scripts
#   *.pdf         Architecture documents (metadata + filename parse)
#   *.yaml / *.yml YAML manifests
#
# Output format:
#   modules:       N
#   clock_domains: N
#   latches:       N (risk)
#   testbench:     found/missing
#   functions:     N
#   sagco_refs:    N
#   deploy_score:  N%
#   STATUS=SAGCO_XRAY_PASS / WARN / FAIL
#
# Usage:
#   sagco-xray <file>              → scan one file
#   sagco-xray <dir>               → scan all supported files in directory
#   sagco-xray report              → aggregate report from last scan
#   sagco-xray fleet               → scan entire SAGCO repo

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
RACE_LOG="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"
XRAY_DIR="$HOME/sagco_fleet/xray"
XRAY_CACHE="$XRAY_DIR/xray_cache.csv"

mkdir -p "$XRAY_DIR"

# ── Verilog / SystemVerilog scanner ──────────────────────────────────────────
scan_verilog() {
    FILE="$1"
    echo "  [VERILOG/HDL] $(basename "$FILE")"

    MODULES=$(grep -c "^module\b\|^module " "$FILE" 2>/dev/null || echo 0)
    ENDMODULES=$(grep -c "^endmodule" "$FILE" 2>/dev/null || echo 0)
    PORTS_IN=$(grep -c "\binput\b" "$FILE" 2>/dev/null || echo 0)
    PORTS_OUT=$(grep -c "\boutput\b" "$FILE" 2>/dev/null || echo 0)
    PORTS_INOUT=$(grep -c "\binout\b" "$FILE" 2>/dev/null || echo 0)
    ALWAYS_BLOCKS=$(grep -c "always\s*@" "$FILE" 2>/dev/null || echo 0)
    ASSIGNS=$(grep -c "^\s*assign\b" "$FILE" 2>/dev/null || echo 0)
    CASE_STMTS=$(grep -c "\bcase[xz]\?\b" "$FILE" 2>/dev/null || echo 0)
    PARAMETERS=$(grep -c "\bparameter\b\|\blocalparam\b" "$FILE" 2>/dev/null || echo 0)
    WIRES=$(grep -c "^\s*wire\b" "$FILE" 2>/dev/null || echo 0)
    REGS=$(grep -c "^\s*reg\b" "$FILE" 2>/dev/null || echo 0)

    # Clock domains: unique clock signals in always @(posedge/negedge ...)
    CLOCK_DOMAINS=$(grep -o "posedge\s\+[a-zA-Z_][a-zA-Z0-9_]*\|negedge\s\+[a-zA-Z_][a-zA-Z0-9_]*" \
        "$FILE" 2>/dev/null | awk '{print $2}' | sort -u | wc -l)

    # Latch risk: always @ without edge trigger
    LATCH_RISK=$(grep -c "always\s*@\s*(" "$FILE" 2>/dev/null || echo 0)
    EDGE_COUNT=$(grep -c "posedge\|negedge" "$FILE" 2>/dev/null || echo 0)
    POTENTIAL_LATCHES=$((LATCH_RISK - EDGE_COUNT))
    [ "$POTENTIAL_LATCHES" -lt 0 ] && POTENTIAL_LATCHES=0

    # Testbench detection
    BASENAME=$(basename "$FILE" .v); BASENAME=$(basename "$BASENAME" .sv)
    TB_STATUS="missing"
    echo "$BASENAME" | grep -qi "tb_\|_tb\|testbench\|test_" && TB_STATUS="IS_TESTBENCH"
    [ "$TB_STATUS" = "missing" ] && grep -q "initial\s*begin\|$dumpfile\|\$finish" \
        "$FILE" 2>/dev/null && TB_STATUS="contains_sim"

    # Top module name
    TOP_MODULE=$(grep "^module\b\|^module " "$FILE" 2>/dev/null | head -1 | \
        awk '{print $2}' | tr -d '(;')

    # FSM detection
    FSM=""
    [ "$CASE_STMTS" -gt 0 ] && [ "$REGS" -gt 0 ] && FSM="likely"

    # Syntax sanity: module count should match endmodule count
    SYNTAX_WARN=""
    [ "$MODULES" -ne "$ENDMODULES" ] && \
        SYNTAX_WARN="⚠️  module/endmodule mismatch ($MODULES vs $ENDMODULES)"

    # Deployment score for this file
    SCORE=50
    [ "$MODULES" -gt 0 ] && SCORE=$((SCORE + 10))
    [ "$CLOCK_DOMAINS" -gt 0 ] && SCORE=$((SCORE + 10))
    [ "$TB_STATUS" != "missing" ] && SCORE=$((SCORE + 15))
    [ "$POTENTIAL_LATCHES" -eq 0 ] && SCORE=$((SCORE + 10))
    [ -z "$SYNTAX_WARN" ] && SCORE=$((SCORE + 15))
    [ "$SCORE" -gt 100 ] && SCORE=100

    printf "    top_module:     %s\n"   "${TOP_MODULE:-?}"
    printf "    modules:        %d\n"   "$MODULES"
    printf "    clock_domains:  %d\n"   "$CLOCK_DOMAINS"
    printf "    always_blocks:  %d\n"   "$ALWAYS_BLOCKS"
    printf "    assigns:        %d\n"   "$ASSIGNS"
    printf "    case_stmts:     %d\n"   "$CASE_STMTS"
    printf "    wires:          %d\n"   "$WIRES"
    printf "    regs:           %d\n"   "$REGS"
    printf "    parameters:     %d\n"   "$PARAMETERS"
    printf "    ports_in:       %d\n"   "$PORTS_IN"
    printf "    ports_out:      %d\n"   "$PORTS_OUT"
    printf "    potential_latch:%d\n"   "$POTENTIAL_LATCHES"
    printf "    fsm_detected:   %s\n"   "${FSM:-none}"
    printf "    testbench:      %s\n"   "$TB_STATUS"
    [ -n "$SYNTAX_WARN" ] && printf "    syntax:         %s\n" "$SYNTAX_WARN"
    printf "    deploy_score:   %d%%\n" "$SCORE"

    # Cache result
    [ -f "$XRAY_CACHE" ] || echo "timestamp,device,file,type,score,modules,clocks,latches,tb,status" \
        > "$XRAY_CACHE"
    STATUS_VAL="PASS"; [ "$SCORE" -lt 70 ] && STATUS_VAL="WARN"; \
        [ "$SCORE" -lt 40 ] && STATUS_VAL="FAIL"
    echo "${STAMP},${DEV},$(basename "$FILE"),verilog,${SCORE},${MODULES},${CLOCK_DOMAINS},${POTENTIAL_LATCHES},${TB_STATUS},SAGCO_XRAY_${STATUS_VAL}" \
        >> "$XRAY_CACHE"

    echo ""
    return $((100 - SCORE))
}

# ── C / header scanner ────────────────────────────────────────────────────────
scan_c() {
    FILE="$1"
    EXT="${FILE##*.}"
    echo "  [C/${EXT}] $(basename "$FILE")"

    LINES=$(wc -l < "$FILE" 2>/dev/null || echo 0)
    INCLUDES=$(grep -c "^#include" "$FILE" 2>/dev/null || echo 0)
    DEFINES=$(grep -c "^#define" "$FILE" 2>/dev/null || echo 0)
    FUNCTIONS=$(grep -c "^[a-zA-Z_][a-zA-Z0-9_ \*]*([^;]*)" "$FILE" 2>/dev/null || echo 0)
    SAGCO_REFS=$(grep -c "SAGCO\|sagco_" "$FILE" 2>/dev/null || echo 0)
    MALLOCS=$(grep -c "\bmalloc\b\|\bcalloc\b\|\brealloc\b" "$FILE" 2>/dev/null || echo 0)
    FREES=$(grep -c "\bfree\b" "$FILE" 2>/dev/null || echo 0)
    STRUCTS=$(grep -c "^typedef\s\+struct\|^struct\s" "$FILE" 2>/dev/null || echo 0)
    ENUMS=$(grep -c "^typedef\s\+enum\|^enum\s" "$FILE" 2>/dev/null || echo 0)

    # Entry point
    ENTRY="library"
    grep -q "^int main\b\|^void main\b\|^main\b" "$FILE" 2>/dev/null && ENTRY="main"

    # Memory safety check
    MEM_WARN=""
    [ "$MALLOCS" -gt "$FREES" ] && \
        MEM_WARN="⚠️  malloc($MALLOCS) > free($FREES) — possible leak"

    # SAGCO integration level
    SAGCO_LEVEL="none"
    [ "$SAGCO_REFS" -gt 0 ] && SAGCO_LEVEL="referenced"
    [ "$SAGCO_REFS" -gt 5 ] && SAGCO_LEVEL="integrated"

    SCORE=50
    [ "$FUNCTIONS" -gt 0 ] && SCORE=$((SCORE + 10))
    [ "$ENTRY" = "main" ] && SCORE=$((SCORE + 10))
    [ "$SAGCO_REFS" -gt 0 ] && SCORE=$((SCORE + 10))
    [ "$MALLOCS" -le "$FREES" ] && SCORE=$((SCORE + 15))
    [ "$LINES" -gt 50 ] && SCORE=$((SCORE + 15))
    [ "$SCORE" -gt 100 ] && SCORE=100

    printf "    lines:          %d\n"   "$LINES"
    printf "    functions:      %d\n"   "$FUNCTIONS"
    printf "    includes:       %d\n"   "$INCLUDES"
    printf "    defines:        %d\n"   "$DEFINES"
    printf "    structs:        %d\n"   "$STRUCTS"
    printf "    enums:          %d\n"   "$ENUMS"
    printf "    entry_point:    %s\n"   "$ENTRY"
    printf "    sagco_refs:     %d (%s)\n" "$SAGCO_REFS" "$SAGCO_LEVEL"
    printf "    malloc/free:    %d/%d\n"   "$MALLOCS" "$FREES"
    [ -n "$MEM_WARN" ] && printf "    memory:         %s\n" "$MEM_WARN"
    printf "    deploy_score:   %d%%\n" "$SCORE"

    [ -f "$XRAY_CACHE" ] || echo "timestamp,device,file,type,score,modules,clocks,latches,tb,status" \
        > "$XRAY_CACHE"
    STATUS_VAL="PASS"; [ "$SCORE" -lt 70 ] && STATUS_VAL="WARN"
    echo "${STAMP},${DEV},$(basename "$FILE"),c_firmware,${SCORE},0,0,0,${ENTRY},SAGCO_XRAY_${STATUS_VAL}" \
        >> "$XRAY_CACHE"

    echo ""
}

# ── Rust scanner ──────────────────────────────────────────────────────────────
scan_rust() {
    FILE="$1"
    echo "  [RUST] $(basename "$FILE")"
    LINES=$(wc -l < "$FILE" 2>/dev/null || echo 0)
    FUNS=$(grep -c "^\s*\(pub\s\+\)\?fn\b" "$FILE" 2>/dev/null || echo 0)
    STRUCTS=$(grep -c "^\s*\(pub\s\+\)\?struct\b" "$FILE" 2>/dev/null || echo 0)
    ENUMS=$(grep -c "^\s*\(pub\s\+\)\?enum\b" "$FILE" 2>/dev/null || echo 0)
    TRAITS=$(grep -c "^\s*\(pub\s\+\)\?trait\b" "$FILE" 2>/dev/null || echo 0)
    UNSAFE=$(grep -c "\bunsafe\b" "$FILE" 2>/dev/null || echo 0)
    SAGCO_REFS=$(grep -c "SAGCO\|sagco_" "$FILE" 2>/dev/null || echo 0)
    TESTS=$(grep -c "#\[test\]\|#\[cfg(test)\]" "$FILE" 2>/dev/null || echo 0)
    SCORE=60
    [ "$FUNS" -gt 0 ] && SCORE=$((SCORE + 10))
    [ "$TESTS" -gt 0 ] && SCORE=$((SCORE + 15))
    [ "$UNSAFE" -eq 0 ] && SCORE=$((SCORE + 15))
    [ "$SCORE" -gt 100 ] && SCORE=100
    printf "    lines:      %d  fns:    %d  structs: %d\n" "$LINES" "$FUNS" "$STRUCTS"
    printf "    enums:      %d  traits: %d  unsafe:  %d\n" "$ENUMS" "$TRAITS" "$UNSAFE"
    printf "    tests:      %d  sagco:  %d\n" "$TESTS" "$SAGCO_REFS"
    printf "    deploy_score: %d%%\n" "$SCORE"
    echo ""
}

# ── PDF scanner (filename + size heuristics) ──────────────────────────────────
scan_pdf() {
    FILE="$1"
    echo "  [PDF/ARCH DOC] $(basename "$FILE")"

    FNAME=$(basename "$FILE")
    SIZE=$(wc -c < "$FILE" 2>/dev/null || echo 0)
    SIZE_KB=$((SIZE / 1024))

    # Parse architecture hints from filename
    ARCH_HINTS=""
    echo "$FNAME" | grep -qi "cpu\|processor\|alu\|pipeline" && \
        ARCH_HINTS="${ARCH_HINTS}cpu_architecture "
    echo "$FNAME" | grep -qi "compiler\|junction\|piecewise" && \
        ARCH_HINTS="${ARCH_HINTS}compiler_design "
    echo "$FNAME" | grep -qi "reality\|engine\|computable" && \
        ARCH_HINTS="${ARCH_HINTS}compute_engine "
    echo "$FNAME" | grep -qi "memory\|cache\|bus" && \
        ARCH_HINTS="${ARCH_HINTS}memory_arch "
    echo "$FNAME" | grep -qi "sagco" && ARCH_HINTS="${ARCH_HINTS}sagco_native "

    # Minimum viable doc check
    SCORE=40
    [ "$SIZE_KB" -gt 10 ] && SCORE=$((SCORE + 20))
    [ "$SIZE_KB" -gt 50 ] && SCORE=$((SCORE + 20))
    [ -n "$ARCH_HINTS" ] && SCORE=$((SCORE + 20))

    printf "    size:           %dKB\n"      "$SIZE_KB"
    printf "    arch_hints:     %s\n"         "${ARCH_HINTS:-unknown}"
    printf "    content_scan:   filename_only (cannot read PDF binary)\n"
    printf "    deploy_score:   %d%% (pre-inspect estimate)\n" "$SCORE"
    printf "    next_step:      extract text with pdftotext, run sagco-xray on .txt\n"
    echo ""
}

# ── generic shell/python/yaml ─────────────────────────────────────────────────
scan_generic() {
    FILE="$1"; TYPE="$2"
    LINES=$(wc -l < "$FILE" 2>/dev/null || echo 0)
    SAGCO_REFS=$(grep -c "SAGCO\|sagco_\|sagco-" "$FILE" 2>/dev/null || echo 0)
    STATUS_LINES=$(grep -c "STATUS=SAGCO_" "$FILE" 2>/dev/null || echo 0)
    GEN=$([ "$STATUS_LINES" -gt 0 ] && echo "Gen3" || \
          [ "$SAGCO_REFS" -gt 0 ] && echo "Gen2" || echo "Gen1")
    printf "  [%s] %-35s  lines=%-6d sagco_refs=%-4d gen=%s\n" \
        "$TYPE" "$(basename "$FILE")" "$LINES" "$SAGCO_REFS" "$GEN"
}

# ── dispatch single file ──────────────────────────────────────────────────────
scan_file() {
    FILE="$1"
    [ -f "$FILE" ] || { echo "  ERROR: not found: $FILE"; return 1; }
    EXT="${FILE##*.}"
    case "$EXT" in
        v|sv)     scan_verilog "$FILE" ;;
        c|h)      scan_c "$FILE" ;;
        rs)       scan_rust "$FILE" ;;
        pdf|PDF)  scan_pdf "$FILE" ;;
        sh)       scan_generic "$FILE" "SHELL" ;;
        py)       scan_generic "$FILE" "PYTHON" ;;
        yaml|yml) scan_generic "$FILE" "YAML" ;;
        *)        scan_generic "$FILE" "OTHER" ;;
    esac
}

# ── scan a directory ──────────────────────────────────────────────────────────
scan_dir() {
    DIR="$1"
    echo "SAGCO X-RAY — Directory Scan"
    echo "================================"
    echo "Path:  $DIR"
    echo "Stamp: $STAMP"
    echo ""
    find "$DIR" -maxdepth 3 -type f \( \
        -name "*.v" -o -name "*.sv" -o -name "*.c" -o -name "*.h" \
        -o -name "*.rs" -o -name "*.pdf" -o -name "*.py" \
        -o -name "sagco-*.sh" -o -name "sagco-*.yaml" \) \
        -not -path '*/.git/*' 2>/dev/null | sort | while read F; do
        scan_file "$F"
    done
}

# ── aggregate report ──────────────────────────────────────────────────────────
cmd_report() {
    echo "SAGCO X-RAY AGGREGATE REPORT"
    echo "=============================="
    echo "Stamp:  $STAMP"
    echo "Device: $DEV"
    echo ""

    [ -f "$XRAY_CACHE" ] || { echo "  No scan data — run: sagco-xray <file_or_dir>"; return; }

    TOTAL=$(tail -n +2 "$XRAY_CACHE" 2>/dev/null | wc -l)
    PASS=$(grep "XRAY_PASS" "$XRAY_CACHE" 2>/dev/null | wc -l)
    WARN=$(grep "XRAY_WARN" "$XRAY_CACHE" 2>/dev/null | wc -l)
    FAIL=$(grep "XRAY_FAIL" "$XRAY_CACHE" 2>/dev/null | wc -l)

    AVG_SCORE=0
    if [ "$TOTAL" -gt 0 ]; then
        AVG_SCORE=$(tail -n +2 "$XRAY_CACHE" 2>/dev/null | \
            awk -F',' '{sum += $5; n++} END {print int(sum/n)}')
    fi

    printf "  Files scanned:   %d\n" "$TOTAL"
    printf "  Pass:            %d\n" "$PASS"
    printf "  Warn:            %d\n" "$WARN"
    printf "  Fail:            %d\n" "$FAIL"
    printf "  Avg score:       %d%%\n" "$AVG_SCORE"
    echo ""
    echo "  Recent scans:"
    printf "  %-35s %-12s %-8s %s\n" "FILE" "TYPE" "SCORE" "STATUS"
    echo "  ──────────────────────────────────────────────────────────"
    tail -n +2 "$XRAY_CACHE" 2>/dev/null | tail -10 | \
        awk -F',' '{printf "  %-35s %-12s %-8s %s\n", $3, $4, $5"%", $10}'
    echo ""

    if [ "$AVG_SCORE" -ge 80 ]; then
        echo "  DEPLOYMENT_SCORE=${AVG_SCORE}%  STATUS=SAGCO_XRAY_PASS"
        echo "  ✅ Fleet is deployment-ready"
    elif [ "$AVG_SCORE" -ge 60 ]; then
        echo "  DEPLOYMENT_SCORE=${AVG_SCORE}%  STATUS=SAGCO_XRAY_WARN"
        echo "  🟡 Address warnings before deployment"
    else
        echo "  DEPLOYMENT_SCORE=${AVG_SCORE}%  STATUS=SAGCO_XRAY_FAIL"
        echo "  ❌ Significant issues — review scan output"
    fi
}

# ── fleet: scan entire SAGCO repo ─────────────────────────────────────────────
cmd_fleet() {
    TARGET="${1:-$PWD}"
    echo "SAGCO X-RAY FLEET SCAN"
    echo "========================"
    echo "Root: $TARGET"
    echo ""

    # Verilog files
    VF=$(find "$TARGET" -name "*.v" -o -name "*.sv" 2>/dev/null | grep -v ".git" | wc -l)
    CF=$(find "$TARGET" -name "*.c" -o -name "*.h" 2>/dev/null | grep -v ".git" | wc -l)
    RF=$(find "$TARGET" -name "*.rs" 2>/dev/null | grep -v ".git" | wc -l)
    PF=$(find "$TARGET" -name "*.pdf" 2>/dev/null | grep -v ".git" | wc -l)

    printf "  Verilog/SV files: %d\n" "$VF"
    printf "  C/H files:        %d\n" "$CF"
    printf "  Rust files:       %d\n" "$RF"
    printf "  PDF docs:         %d\n" "$PF"
    echo ""

    [ "$((VF + CF + RF + PF))" -eq 0 ] && {
        echo "  No hardware/firmware files found in: $TARGET"
        echo "  Upload .v .c .pdf files, then: sagco-xray <file>"
        echo ""
        echo "  Waiting for:"
        echo "    sagco_cpu*.v           Verilog HDL"
        echo "    sagco_cpu_mod*.c       C firmware/emulator"
        echo "    SAGCO_*_Compiler.pdf   Architecture docs"
        return
    }

    scan_dir "$TARGET"
    cmd_report
}

# ── race tick ─────────────────────────────────────────────────────────────────
write_tick() {
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    [ -f "$RACE_LOG" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_LOG"
    echo "${STAMP},${DEV},sagco_xray_${CMD},${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_LOG"
    HASH=$(echo "${STAMP}sagco-xray${DEV}" | cksum | awk '{printf "%012d", $1}')
    [ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
    echo "${STAMP},${DEV},sagco-xray,${XRAY_CACHE},${HASH},SAGCO_XRAY_PASS" >> "$LEDGER"
}

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-fleet}"

case "$CMD" in
    report)     cmd_report; write_tick ;;
    fleet)      cmd_fleet "${2:-$PWD}"; write_tick ;;
    *)
        if [ -f "$CMD" ]; then
            # Direct file scan
            echo "SAGCO X-RAY — $(basename "$CMD")"
            echo "=============================="
            scan_file "$CMD"
            write_tick
        elif [ -d "$CMD" ]; then
            scan_dir "$CMD"
            cmd_report
            write_tick
        else
            echo "Usage: sagco-xray <file|dir|report|fleet>"
            echo ""
            echo "  sagco-xray sagco_cpu.v              scan Verilog HDL"
            echo "  sagco-xray sagco_cpu_mod.c          scan C firmware"
            echo "  sagco-xray SAGCO_Compiler.pdf       scan arch doc"
            echo "  sagco-xray ~/downloads/             scan directory"
            echo "  sagco-xray report                   aggregate report"
            echo "  sagco-xray fleet                    scan SAGCO repo"
            echo ""
            echo "  Output: modules, clock_domains, latches, testbench,"
            echo "          functions, sagco_refs, deploy_score, STATUS"
            exit 1
        fi
        ;;
esac

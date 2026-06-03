#!/bin/sh
# sagco-gta6 — SAGCO Civilization Simulator City Dashboard
#
# The city IS the mansion.
# Every node is a district on the BGA chessboard.
# Every pod is an NPC.
# Every brick is a callable function.
# When they're lost, they go to the Library.
#
# BGA 8×8 District Map:
#   Row 1: Mobile      (zfold, ish, gcp)
#   Row 2: Laptop      (hp-sagco-os)
#   Row 3: Workstation (athena, nova, lyra)
#   Row 4: Edge        (6× RPi nodes)
#   Row 5: Services    (forge, library, council, linguist, eru, provenance)
#   Row 6-8: Undiscovered
#
# Usage:
#   sagco-gta6                → city overview
#   sagco-gta6 map            → BGA 8×8 district grid
#   sagco-gta6 district       → full district inventory
#   sagco-gta6 lost           → where am I + nearest services
#   sagco-gta6 council        → government session + agenda
#   sagco-gta6 power          → ERU power grid status
#   sagco-gta6 npc            → NPC/pod scheduler status
#   sagco-gta6 mission        → current missions from corpus

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
RACE_LOG="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"
CORPUS="${SAGCO_CORPUS:-$PWD}"
TODO_CACHE="$HOME/sagco_fleet/sagco_todo_cache.csv"

# ── district registry ─────────────────────────────────────────────────────────
# Format: id|coord|role|type|abbrev
district_registry() {
    cat << 'DISTRICTS'
zfold|A1|Scout|mobile|Z-FOLD
ish|B1|Archive|mobile|ISH
gcp|C1|Cloud Brain|cloud|GCP
hp|A2|Command|laptop|HP
hp-sagco-os|A2|Command|laptop|HP
athena|A3|Verification|workstation|ATHENA
nova|B3|Exploration|workstation|NOVA
lyra|C3|Synthesis|workstation|LYRA
rpi-telemetry-01|A4|Telemetry|edge|RPi-T
rpi-camera-01|B4|Vision|edge|RPi-C
rpi-weather-01|C4|Weather|edge|RPi-W
rpi-qr-01|D4|QR Scanner|edge|RPi-Q
rpi-inventory-01|E4|Inventory|edge|RPi-I
rpi-inference-01|F4|AI Inference|edge|RPi-AI
forge|A5|Rust Compiler|service|FORGE
library|B5|Knowledge Hub|service|LIBRARY
council|C5|Government|service|COUNCIL
linguist|D5|Translation|service|LING
eru|E5|Power Grid|service|ERU
provenance|F5|Archive|service|PROV
DISTRICTS
}

# ── coord lookup ──────────────────────────────────────────────────────────────
find_district() {
    district_registry | awk -F'|' -v id="$1" '$1==id{print;exit}'
}

coord_at() {
    # Returns the node at a given coord
    district_registry | awk -F'|' -v c="$1" '$2==c{print $1;exit}'
}

# ── BGA district map ──────────────────────────────────────────────────────────
cmd_map() {
    echo "SAGCO CIVILIZATION — BGA District Map (8×8)"
    echo "=============================================="
    echo "Current node: $DEV (◉)"
    echo ""
    echo "       A         B         C         D         E         F         G         H"
    echo "  ┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐"

    ROW=1
    while [ $ROW -le 8 ]; do
        case $ROW in
            1) LABEL="  MOBILE" ;;
            2) LABEL="  LAPTOP" ;;
            3) LABEL="WRKSTN  " ;;
            4) LABEL="  EDGE  " ;;
            5) LABEL="SERVICES" ;;
            *) LABEL="UNDSSCVR" ;;
        esac

        printf "%d |" $ROW
        for COL in A B C D E F G H; do
            COORD="${COL}${ROW}"
            MATCH=$(district_registry | awk -F'|' -v c="$COORD" '$2==c && NR>0{print $5;exit}')
            MATCHID=$(district_registry | awk -F'|' -v c="$COORD" '$2==c && NR>0{print $1;exit}')
            if [ -n "$MATCH" ]; then
                if [ "$MATCHID" = "$DEV" ]; then
                    printf "◉%-8s|" "$MATCH"
                else
                    printf " %-8s|" "$MATCH"
                fi
            else
                printf " ·       |"
            fi
        done
        printf " %s\n" "$LABEL"

        if [ $ROW -lt 8 ]; then
            echo "  ├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤"
        fi
        ROW=$((ROW+1))
    done
    echo "  └─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘"
    echo ""

    REGISTERED=$(district_registry | grep -v "^$" | wc -l)
    TOTAL=64
    UNDISCOVERED=$((TOTAL - REGISTERED))
    echo "  Registered: $REGISTERED / $TOTAL districts"
    echo "  Undiscovered: $UNDISCOVERED"
    echo "  ◉ = current node"
    echo ""
    echo "  Run: sagco-gta6 lost      → full location report"
    echo "       sagco-gta6 district  → district details"
}

# ── district inventory ────────────────────────────────────────────────────────
cmd_district() {
    echo "SAGCO DISTRICTS — Registry"
    echo "==========================="
    echo ""
    printf "  %-22s %-6s %-16s %-12s %s\n" "NODE" "COORD" "ROLE" "TYPE" ""
    printf "  %-22s %-6s %-16s %-12s\n" "──────────────────────" "──────" "────────────────" "────────────"
    SEEN=""
    district_registry | grep -v "^$" | while IFS='|' read ID COORD ROLE TYPE ABBREV; do
        [ -z "$ID" ] && continue
        # Skip duplicate coords (hp/hp-sagco-os both at A2)
        echo "$SEEN" | grep -q "|${COORD}|" && continue
        SEEN="${SEEN}|${COORD}|"
        MARKER="  "; [ "$ID" = "$DEV" ] && MARKER="◉ "
        printf "  %s%-20s %-6s %-16s %s\n" "$MARKER" "$ID" "$COORD" "$ROLE" "$TYPE"
    done
    echo ""
    REGISTERED=$(district_registry | grep -v "^$" | wc -l)
    echo "  $REGISTERED registered  |  $((64 - REGISTERED)) undiscovered  |  ◉ = current node ($DEV)"
}

# ── lost: where am I ─────────────────────────────────────────────────────────
cmd_lost() {
    FOUND=$(find_district "$DEV")

    echo "SAGCO GTA6 — LOCATION"
    echo "======================"
    echo ""

    if [ -z "$FOUND" ]; then
        echo "  ⚠️  Device '$DEV' not in district registry"
        echo ""
        echo "  Fix: echo <device_name> > ~/.sagco_device"
        echo "       sagco-node-register"
        echo ""
        echo "  Defaulting to District H8 (Undiscovered Territory)"
        COORD="H8"; ROLE="Unregistered"; TYPE="unknown"
    else
        COORD=$(echo "$FOUND"  | cut -d'|' -f2)
        ROLE=$(echo "$FOUND"   | cut -d'|' -f3)
        TYPE=$(echo "$FOUND"   | cut -d'|' -f4)
    fi

    printf "  You are in District %-6s (%s)\n" "$COORD" "$DEV"
    printf "  Role: %-16s  Type: %s\n" "$ROLE" "$TYPE"
    echo ""

    echo "  Nearest services:"
    printf "  %-14s B5  Knowledge Hub   (brain, linguist, excavate)\n"  "Library:"
    printf "  %-14s C5  Government       (vote, governance, DAO)\n"       "Council:"
    printf "  %-14s A5  Rust Compiler    (compile, build, forge)\n"       "Forge:"
    printf "  %-14s D5  Translation      (translate, encode, concept)\n"  "Linguist:"
    printf "  %-14s E5  Power Grid       (attribution, ERU, work units)\n" "Power Grid:"
    printf "  %-14s F5  Archive          (sign, verify, provenance)\n"    "Provenance:"
    echo ""

    echo "  Current mission:"
    if [ -f "$TODO_CACHE" ]; then
        NEXT=$(grep "|partial|" "$TODO_CACHE" 2>/dev/null | head -1)
        [ -z "$NEXT" ] && NEXT=$(grep "|missing|" "$TODO_CACHE" 2>/dev/null | head -1)
        if [ -n "$NEXT" ]; then
            MSRC=$(echo "$NEXT"   | cut -d'|' -f1)
            MBRICK=$(echo "$NEXT" | cut -d'|' -f2)
            printf "  %-14s %s\n" "  Task:"   "$MBRICK"
            printf "  %-14s %s\n" "  Source:" "$MSRC"
        else
            echo "    Mission queue empty — run: sagco-todo"
        fi
    else
        echo "    Run: sagco-todo  → load mission queue"
    fi

    echo ""

    if [ -f "$RACE_LOG" ]; then
        TICKS=$(grep ",${DEV}," "$RACE_LOG" 2>/dev/null | wc -l || echo 0)
        printf "  Race ticks from this node: %d\n" "$TICKS"
    fi

    REGISTERED=$(district_registry | grep -v "^$" | wc -l)
    printf "  Undiscovered districts: %d / 64\n" "$((64 - REGISTERED))"
    echo ""
    echo "  STATUS=SAGCO_GTA6_LOCATED"
}

# ── council: government session ───────────────────────────────────────────────
cmd_council() {
    echo "SAGCO GOVERNMENT — Council Session"
    echo "===================================="
    echo "Stamp: $STAMP  |  Device: $DEV"
    echo ""
    echo "  COUNCIL SEATS:"
    printf "  %-20s %-16s %s\n" "Mayor"          "The Builder"        "Domenic Garza — GPG AE5519579584DEF5"
    printf "  %-20s %-16s %s\n" "Witness"         "Prometheus"         "sagco-prometheus.sh — immutable ledger"
    printf "  %-20s %-16s %s\n" "Verification"    "Athena (A3)"        "Keeper of Verification"
    printf "  %-20s %-16s %s\n" "Exploration"     "Nova (B3)"          "Scout of Possibilities"
    printf "  %-20s %-16s %s\n" "Synthesis"       "Lyra (C3)"          "Weaver of Patterns"
    printf "  %-20s %-16s %s\n" "Cloud Consul"    "GCP (C1)"           "SAGCO-OSComputConsciousness"
    printf "  %-20s %-16s %s\n" "Fleet Marshall"  "rpi-telemetry (A4)" "First edge node"
    printf "  %-20s %-16s %s\n" "Linguist"        "sagco-linguist (D5)" "Concept preservation"
    printf "  %-20s %-16s %s\n" "Power Grid"      "ERU Engine (E5)"    "Attribution / work units"
    printf "  %-20s %-16s %s\n" "Archivist"       "Excavator (F5)"     "Provenance archaeologist"
    echo ""

    echo "  PENDING MOTIONS:"
    if [ -f "$TODO_CACHE" ]; then
        grep "|missing|" "$TODO_CACHE" 2>/dev/null | head -5 | \
            while IFS='|' read DOC BRICK STATUS DEPENDS CLASS TS; do
                printf "  ⬜ [%-12s] %s\n" "$DOC" "$BRICK"
            done
        grep "|partial|" "$TODO_CACHE" 2>/dev/null | head -3 | \
            while IFS='|' read DOC BRICK STATUS DEPENDS CLASS TS; do
                printf "  🟡 [%-12s] %s\n" "$DOC" "$BRICK"
            done
    else
        echo "    Run: sagco-todo  → load council agenda"
    fi
    echo ""

    echo "  PASSED MOTIONS (this session):"
    echo "  ✅ sagco-linguist     — Linguistics Department open"
    echo "  ✅ sagco-gta6         — City Dashboard built"
    echo "  ✅ bootstrap fallback — agent bootstrap PASS"
    echo "  ✅ sagco-excavate     — Provenance Archaeologist"
    echo "  ✅ sagco-flamegen     — FlameLang v1 vocabulary"
    echo "  ✅ Act X complete     — Language Compiles Itself"
    echo ""
    echo "  Run: sagco-todo next  → next unblocked motion"
    echo "  STATUS=SAGCO_COUNCIL_SESSION_COMPLETE"
}

# ── power: ERU power grid ─────────────────────────────────────────────────────
cmd_power() {
    echo "SAGCO POWER GRID — ERU Status"
    echo "================================"
    echo ""

    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo "unknown")
    CHARGING=$(cat /sys/class/power_supply/battery/status 2>/dev/null || echo "unknown")

    printf "  Current node:  %-14s  Battery: %-6s  Status: %s\n" "$DEV" "${BAT}%" "$CHARGING"
    echo ""

    if [ -f "$RACE_LOG" ]; then
        TOTAL_TICKS=$(( $(wc -l < "$RACE_LOG" 2>/dev/null || echo 1) - 1 ))
        DEV_TICKS=$(grep ",${DEV}," "$RACE_LOG" 2>/dev/null | wc -l || echo 0)
        FLEET_TICKS=$((TOTAL_TICKS - DEV_TICKS))

        echo "  FLEET POWER CONSUMPTION:"
        printf "  %-24s %d ticks\n" "This node ($DEV):" "$DEV_TICKS"
        printf "  %-24s %d ticks\n" "Other nodes:" "$FLEET_TICKS"
        printf "  %-24s %d ticks total\n" "Fleet total:" "$TOTAL_TICKS"
        echo ""
    fi

    if [ -f "$LEDGER" ]; then
        LEDGER_TOTAL=$(( $(wc -l < "$LEDGER" 2>/dev/null || echo 1) - 1 ))
        echo "  ERU WORK UNITS (ledger attribution):"
        printf "  %-24s %d entries\n" "Total:" "$LEDGER_TOTAL"
        awk -F',' 'NR>1 && $2!="device" && $2!="" {c[$2]++}
            END {for(d in c) printf "  %-24s %d\n",d":",c[d]}' \
            "$LEDGER" 2>/dev/null | sort -t':' -k2 -rn | head -6
        echo ""
    fi

    echo "  SERVICE SUBSTATIONS:"
    printf "  %-18s A5  forge      compile, build\n"       "Forge:"
    printf "  %-18s B5  library    brain, linguist\n"      "Library:"
    printf "  %-18s C5  council    governance\n"           "Council:"
    printf "  %-18s E5  eru        attribution, ERU\n"     "ERU Grid:"
    printf "  %-18s F5  provenance sign, verify, chain\n"  "Provenance:"
    echo ""
    echo "  Run: sagco-eru-device  → detailed ERU per node"
    echo "  STATUS=SAGCO_POWER_GRID_NOMINAL"
}

# ── npc: pod/agent status ─────────────────────────────────────────────────────
cmd_npc() {
    echo "SAGCO NPC SCHEDULER"
    echo "===================="
    echo ""

    echo "  COUNCIL MIND NPCs:"
    district_registry | grep -v "service\|^$" | awk -F'|' '!seen[$2]++' | \
        while IFS='|' read ID COORD ROLE TYPE ABBREV; do
            [ -z "$ID" ] && continue
            STATUS="⬜ no ticks"
            [ "$ID" = "$DEV" ] && STATUS="✅ active (this node)"
            if [ -f "$RACE_LOG" ] && grep -q ",${ID}," "$RACE_LOG" 2>/dev/null; then
                STATUS="✅ has race ticks"
                [ "$ID" = "$DEV" ] && STATUS="✅ active (this node)"
            fi
            printf "  %-22s %-6s %-16s %s\n" "$ID" "$COORD" "$ROLE" "$STATUS"
        done
    echo ""

    echo "  SERVICE NPCs:"
    for SVC in forge library council linguist eru provenance; do
        SCRIPT_PATH=""
        case $SVC in
            forge)      SCRIPT_PATH="$CORPUS/nina-trader/src/main.rs" ;;
            library)    SCRIPT_PATH="$CORPUS/sagco-sync-brain.sh" ;;
            council)    SCRIPT_PATH="$CORPUS/SAGCO_LEGIONS_OF_MINDS_COUNCIL.md" ;;
            linguist)   SCRIPT_PATH="$CORPUS/sagco-linguist.sh" ;;
            eru)        SCRIPT_PATH="$CORPUS/sagco-eru-device.sh" ;;
            provenance) SCRIPT_PATH="$CORPUS/sagco-excavate.sh" ;;
        esac
        COORD=$(district_registry | awk -F'|' -v id="$SVC" '$1==id{print $2;exit}')
        STATUS="⬜ script missing"
        [ -f "$SCRIPT_PATH" ] && STATUS="✅ deployed"
        printf "  %-22s %-6s %s\n" "$SVC" "$COORD" "$STATUS"
    done
    echo ""

    if command -v docker >/dev/null 2>&1; then
        RUNNING=$(docker ps --format "{{.Names}}" 2>/dev/null | wc -l)
        echo "  DOCKER NPCs: $RUNNING containers running"
        docker ps --format "    {{.Names}}  {{.Status}}" 2>/dev/null | head -8
    elif command -v kubectl >/dev/null 2>&1; then
        echo "  K8s NPCs (ops namespace):"
        kubectl get pods -n ops --no-headers 2>/dev/null | \
            awk '{printf "    %-30s %s\n", $1, $3}' | head -8
    else
        echo "  Docker/k8s: not available on $DEV"
        echo "    Compose NPCs: run 'docker compose ps' on HP"
    fi
}

# ── mission: current missions ─────────────────────────────────────────────────
cmd_mission() {
    echo "SAGCO ACTIVE MISSIONS"
    echo "======================"
    echo ""

    NEXT=""
    if [ -f "$TODO_CACHE" ]; then
        NEXT=$(grep "|partial|" "$TODO_CACHE" 2>/dev/null | head -1)
        [ -z "$NEXT" ] && NEXT=$(grep "|missing|" "$TODO_CACHE" 2>/dev/null | \
            grep -v "pending\|blocked\|hardware\|acquisition" | head -1)
    fi

    if [ -n "$NEXT" ]; then
        DOC=$(echo "$NEXT"    | cut -d'|' -f1)
        BRICK=$(echo "$NEXT"  | cut -d'|' -f2)
        STATUS=$(echo "$NEXT" | cut -d'|' -f3)
        DEPENDS=$(echo "$NEXT"| cut -d'|' -f4)
        echo "  PRIMARY MISSION:"
        printf "  %-12s %s\n" "Source:"  "$DOC"
        printf "  %-12s %s\n" "Mission:" "$BRICK"
        printf "  %-12s %s\n" "Status:"  "$STATUS"
        [ -n "$DEPENDS" ] && printf "  %-12s %s\n" "Requires:" "$DEPENDS"
        echo ""
    else
        echo "  Mission queue not loaded."
        echo "  Run: sagco-todo  → rebuild cache"
        echo "       sagco-todo next  → single highest-priority"
        echo ""
    fi

    echo "  DISTRICTS WITH OPEN MISSIONS:"
    if [ -f "$TODO_CACHE" ]; then
        grep "|missing|\||partial|" "$TODO_CACHE" 2>/dev/null | \
            cut -d'|' -f1 | sort -u | \
            while read DOC; do
                COUNT=$(grep "^${DOC}|" "$TODO_CACHE" 2>/dev/null | \
                    grep "|missing|\||partial|" | wc -l)
                printf "  %-35s %d open\n" "$DOC" "$COUNT"
            done
    fi

    echo ""
    echo "  Run: sagco-todo unfinished  → all open missions"
    echo "       sagco-todo ready       → unblocked missions"
    echo "  STATUS=SAGCO_MISSION_BRIEFING_COMPLETE"
}

# ── city overview ─────────────────────────────────────────────────────────────
cmd_full() {
    echo "SAGCO CIVILIZATION SIMULATOR"
    echo "============================="
    echo "Stamp: $STAMP  |  Node: $DEV"
    echo ""

    REGISTERED=$(district_registry | grep -v "^$" | wc -l)
    TOTAL=64
    FLEET_TICKS=0; ARTIFACTS=0
    [ -f "$RACE_LOG" ] && FLEET_TICKS=$(( $(wc -l < "$RACE_LOG" 2>/dev/null || echo 1) - 1 ))
    [ -f "$LEDGER" ]   && ARTIFACTS=$(( $(wc -l < "$LEDGER" 2>/dev/null || echo 1) - 1 ))

    printf "  %-24s %d / %d active (%d undiscovered)\n" \
        "Districts:" "$REGISTERED" "$TOTAL" "$((TOTAL - REGISTERED))"
    printf "  %-24s %d\n" "Fleet ticks:" "$FLEET_TICKS"
    printf "  %-24s %d\n" "Ledger entries:" "$ARTIFACTS"
    echo ""

    FOUND=$(find_district "$DEV")
    if [ -n "$FOUND" ]; then
        COORD=$(echo "$FOUND" | cut -d'|' -f2)
        ROLE=$(echo "$FOUND"  | cut -d'|' -f3)
        echo "  You are in District $COORD — $ROLE ($DEV)"
    else
        echo "  Location: unregistered — run: sagco-node-register"
    fi
    echo ""

    echo "  Commands:"
    printf "  %-30s BGA 8×8 district grid\n"          "sagco-gta6 map"
    printf "  %-30s where am I + nearest services\n"  "sagco-gta6 lost"
    printf "  %-30s government session + agenda\n"    "sagco-gta6 council"
    printf "  %-30s ERU power grid status\n"          "sagco-gta6 power"
    printf "  %-30s NPC/pod scheduler status\n"       "sagco-gta6 npc"
    printf "  %-30s current missions\n"               "sagco-gta6 mission"
    printf "  %-30s full district inventory\n"        "sagco-gta6 district"
    echo ""
    echo "  The city IS the mansion."
    echo "  When they're lost, they go to the Library."
    echo ""
    echo "  STATUS=SAGCO_CIVILIZATION_ONLINE"
}

# ── race tick ─────────────────────────────────────────────────────────────────
write_tick() {
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    mkdir -p "$HOME/sagco_race"
    [ -f "$RACE_LOG" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_LOG"
    echo "${STAMP},${DEV},sagco_gta6_${CMD},${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_LOG"
    HASH=$(echo "${STAMP}sagco-gta6${DEV}" | cksum | awk '{printf "%012d", $1}')
    [ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
    echo "${STAMP},${DEV},sagco-gta6,${CORPUS},${HASH},SAGCO_GTA6_PASS" >> "$LEDGER"
}

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-full}"
[ $# -gt 0 ] && shift

case "$CMD" in
    map)        cmd_map;      write_tick ;;
    district)   cmd_district; write_tick ;;
    lost)       cmd_lost;     write_tick ;;
    council)    cmd_council;  write_tick ;;
    power)      cmd_power;    write_tick ;;
    npc)        cmd_npc;      write_tick ;;
    mission)    cmd_mission;  write_tick ;;
    full|"")    cmd_full;     write_tick ;;
    *)
        echo "Usage: sagco-gta6 [map|district|lost|council|power|npc|mission]"
        echo ""
        echo "  map        BGA 8×8 district grid"
        echo "  district   full district inventory"
        echo "  lost       where am I + nearest services"
        echo "  council    government session + agenda"
        echo "  power      ERU power grid status"
        echo "  npc        NPC/pod scheduler status"
        echo "  mission    current missions from corpus"
        echo ""
        echo "  The city IS the mansion."
        echo "  When they're lost, they go to the Library."
        exit 1
        ;;
esac

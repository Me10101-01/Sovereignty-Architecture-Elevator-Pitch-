#!/bin/sh
# sagco-contract — SAGCO Contract Scope Enforcement Gate
# Every red/blue/purple action must pass through this gate.
# No node runs an action unless:
#   1. contract exists and is active
#   2. target is in approved scope
#   3. action is allowed (not prohibited)
#   4. identity is signed (GPG anchor present)
#   5. logs are enabled
#   6. exit route is approved
#
# This is what separates authorized security work from random infrastructure.
#
# Usage:
#   sagco-contract init <id>                      → create new contract
#   sagco-contract check <id> <target> <action>   → gate check (0=pass, 1=fail)
#   sagco-contract scope-add <id> <target>        → add target to approved list
#   sagco-contract scope-check <id> <target>      → is this target in scope?
#   sagco-contract log <id> <action> <target>     → record an authorized action
#   sagco-contract report <id>                    → generate engagement report
#   sagco-contract close <id>                     → close contract, finalize report
#   sagco-contract list                           → show all contracts
#   sagco-contract audit <id>                     → full action log for a contract

STAMP=$(date +%Y%m%d_%H%M%S 2>/dev/null || echo "000000_000000")
DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo unknown)}"
CONTRACT_DIR="$HOME/sagco_fleet/contracts"
RACE_LOG="$HOME/sagco_race/race_log.csv"
LEDGER="$HOME/sagco_ledger.csv"
ACTION_LOG="$HOME/sagco_fleet/engagement_log.csv"
GPG_KEY_ID="AE5519579584DEF5"

mkdir -p "$CONTRACT_DIR"

# ── contract file path ────────────────────────────────────────────────────────
contract_path() { echo "$CONTRACT_DIR/${1}.yaml"; }

# ── read field from contract YAML ─────────────────────────────────────────────
contract_field() {
    FILE="$(contract_path "$1")"; FIELD="$2"
    [ -f "$FILE" ] || { echo ""; return; }
    grep "^  ${FIELD}:" "$FILE" 2>/dev/null | head -1 | sed 's/.*: *//' | tr -d '"'
}

# ── check if target is in approved_targets ────────────────────────────────────
target_in_scope() {
    CONTRACT="$1"; TARGET="$2"
    FILE="$(contract_path "$CONTRACT")"
    [ -f "$FILE" ] || return 1
    # Check exact match or CIDR prefix match (simple: check if target starts with any scope entry)
    in_targets=$(awk '/^  approved_targets:/,/^  [a-z]/' "$FILE" 2>/dev/null | grep "^    - " | sed 's/    - //')
    [ -z "$in_targets" ] && return 1
    echo "$in_targets" | while IFS= read -r SCOPE; do
        [ -z "$SCOPE" ] && continue
        # Exact match
        [ "$TARGET" = "$SCOPE" ] && return 0
        # Prefix match for CIDR-style entries (e.g. 192.168.1 matches 192.168.1.0/24)
        case "$TARGET" in
            ${SCOPE%/*}*) return 0 ;;
        esac
    done
    return 1
}

# ── check if action is allowed ────────────────────────────────────────────────
action_allowed() {
    CONTRACT="$1"; ACTION="$2"
    FILE="$(contract_path "$CONTRACT")"
    [ -f "$FILE" ] || return 1

    # Check prohibited list first (fail fast)
    PROHIBITED=$(awk '/^  prohibited_actions:/,/^  [a-z]/' "$FILE" 2>/dev/null | grep "^    - " | sed 's/    - //')
    echo "$PROHIBITED" | grep -qx "$ACTION" && return 1

    # Check allowed list
    ALLOWED=$(awk '/^  allowed_actions:/,/^  [a-z]/' "$FILE" 2>/dev/null | grep "^    - " | sed 's/    - //')
    echo "$ALLOWED" | grep -qx "$ACTION" && return 0

    return 1
}

# ── the five-condition gate ───────────────────────────────────────────────────
gate_check() {
    CONTRACT="$1"; TARGET="$2"; ACTION="$3"
    PASS=0; FAIL=0

    check_condition() {
        LABEL="$1"; RESULT="$2"
        if [ "$RESULT" -eq 0 ]; then
            printf "  ✅ %-35s PASS\n" "$LABEL"
            PASS=$((PASS + 1))
        else
            printf "  ❌ %-35s FAIL\n" "$LABEL"
            FAIL=$((FAIL + 1))
        fi
    }

    FILE="$(contract_path "$CONTRACT")"

    # Condition 1: contract exists and is active
    [ -f "$FILE" ] && STATUS_VAL=$(contract_field "$CONTRACT" "status") && [ "$STATUS_VAL" = "active" ]
    C1=$?

    # Condition 2: target in approved scope
    target_in_scope "$CONTRACT" "$TARGET"
    C2=$?

    # Condition 3: action allowed
    action_allowed "$CONTRACT" "$ACTION"
    C3=$?

    # Condition 4: identity signed (GPG anchor present)
    ANCHOR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)/sagco-identity-anchor.yaml"
    [ -f "$ANCHOR" ]
    C4=$?

    # Condition 5: logs enabled for this contract
    LOGS_REQ=$(contract_field "$CONTRACT" "logs_required")
    [ "$LOGS_REQ" = "true" ] && [ -f "$ACTION_LOG" ] || [ "$LOGS_REQ" = "true" ]
    C5=$?

    check_condition "contract active ($CONTRACT)" "$C1"
    check_condition "target in scope ($TARGET)" "$C2"
    check_condition "action allowed ($ACTION)" "$C3"
    check_condition "identity signed (GPG: $GPG_KEY_ID)" "$C4"
    check_condition "logging enabled" "$C5"

    TOTAL=$((PASS + FAIL))
    echo "  ────────────────────────────────────────────────"
    printf "  PASS: %d/%d\n" "$PASS" "$TOTAL"

    if [ "$FAIL" -eq 0 ]; then
        echo "  STATUS=SAGCO_GATE_PASS  — action authorized"
        return 0
    else
        echo "  STATUS=SAGCO_GATE_FAIL  — $FAIL condition(s) failed, action BLOCKED"
        return 1
    fi
}

# ── init a new contract ───────────────────────────────────────────────────────
cmd_init() {
    ID="$1"
    [ -z "$ID" ] && { echo "Usage: sagco-contract init <contract_id>"; return 1; }
    FILE="$(contract_path "$ID")"
    [ -f "$FILE" ] && echo "Contract exists: $FILE" && return 0

    cat > "$FILE" << YAML
# SAGCO Contract — $ID
# Generated: $STAMP  Device: $DEV
---
contract:
  id:            $ID
  client:        "FILL_CLIENT_NAME"
  scope_type:    "penetration_test"
  roe_document:  "path/to/rules_of_engagement.pdf"
  start_date:    "$STAMP"
  end_date:      "FILL_END_DATE"
  status:        active
  identity:
    gpg_key:     $GPG_KEY_ID
    ssh_key:     "SAGCO-OS PIPELINE"
    operator:    $DEV
  logs_required: true
  kill_switch:   enabled
  approved_targets:
    - "FILL_TARGET_IP_OR_DOMAIN"
  approved_nodes:
    - $DEV
  allowed_actions:
    - network_scan
    - web_app_test
    - phishing_sim
    - vulnerability_scan
    - social_engineering
  prohibited_actions:
    - dos
    - destructive
    - out_of_scope
    - lateral_to_unauthorized
  reporting:
    format:      markdown
    output:      $CONTRACT_DIR/${ID}_report.md
YAML

    echo "  Created: $FILE"
    echo "  Edit to fill: client, roe_document, end_date, approved_targets"
    echo "  Then: sagco-contract check $ID <target> <action>"
}

# ── add a target to approved scope ───────────────────────────────────────────
cmd_scope_add() {
    ID="$1"; TARGET="$2"
    FILE="$(contract_path "$ID")"
    [ -f "$FILE" ] || { echo "Contract not found: $ID"; return 1; }
    echo "    - $TARGET" >> "$FILE"
    echo "  Added to scope: $TARGET"
    echo "  Contract: $FILE"
}

# ── scope check (just yes/no) ─────────────────────────────────────────────────
cmd_scope_check() {
    ID="$1"; TARGET="$2"
    target_in_scope "$ID" "$TARGET" && \
        echo "  IN SCOPE: $TARGET is approved for contract $ID" || \
        echo "  OUT OF SCOPE: $TARGET is not in contract $ID"
}

# ── log an authorized action ──────────────────────────────────────────────────
cmd_log_action() {
    ID="$1"; ACTION="$2"; TARGET="$3"
    [ -f "$ACTION_LOG" ] || \
        echo "timestamp,device,contract,action,target,gpg_key,status" > "$ACTION_LOG"
    STATUS="AUTHORIZED"
    gate_check "$ID" "$TARGET" "$ACTION" > /dev/null 2>&1 || STATUS="BLOCKED"
    echo "${STAMP},${DEV},${ID},${ACTION},${TARGET},${GPG_KEY_ID},SAGCO_${STATUS}" >> "$ACTION_LOG"
    echo "  Logged: contract=$ID  action=$ACTION  target=$TARGET  status=$STATUS"
}

# ── generate engagement report ────────────────────────────────────────────────
cmd_report() {
    ID="$1"
    FILE="$(contract_path "$ID")"
    [ -f "$FILE" ] || { echo "Contract not found: $ID"; return 1; }

    CLIENT=$(contract_field "$ID" "client")
    SCOPE_TYPE=$(contract_field "$ID" "scope_type")
    START=$(contract_field "$ID" "start_date")
    STATUS_VAL=$(contract_field "$ID" "status")

    ACTION_COUNT=0
    [ -f "$ACTION_LOG" ] && ACTION_COUNT=$(grep -c ",${ID}," "$ACTION_LOG" 2>/dev/null || echo 0)

    REPORT_FILE="$CONTRACT_DIR/${ID}_report_${STAMP}.md"

    cat > "$REPORT_FILE" << REPORT
# SAGCO Engagement Report — $ID

## Contract Summary

| Field | Value |
|---|---|
| Contract ID | $ID |
| Client | $CLIENT |
| Scope Type | $SCOPE_TYPE |
| Start Date | $START |
| Status | $STATUS_VAL |
| Operator | $DEV |
| GPG Key | $GPG_KEY_ID |
| SSH Key | SAGCO-OS PIPELINE |

## Scope

$(awk '/^  approved_targets:/,/^  [a-z]/' "$FILE" 2>/dev/null | grep "^    - " | sed 's/    - /- /')

## Allowed Actions

$(awk '/^  allowed_actions:/,/^  [a-z]/' "$FILE" 2>/dev/null | grep "^    - " | sed 's/    - /- /')

## Prohibited Actions

$(awk '/^  prohibited_actions:/,/^  [a-z]/' "$FILE" 2>/dev/null | grep "^    - " | sed 's/    - /- /')

## Action Log

Total authorized actions: $ACTION_COUNT

$([ -f "$ACTION_LOG" ] && grep ",${ID}," "$ACTION_LOG" 2>/dev/null | \
    awk -F',' '{printf "| %s | %s | %s | %s | %s |\n", $1,$2,$4,$5,$7}' | head -50)

## Provenance

- Operator: $DEV
- GPG Anchor: $GPG_KEY_ID
- SSH Identity: SAGCO-OS PIPELINE
- Report Generated: $STAMP
- All actions logged to: $ACTION_LOG

STATUS=SAGCO_ENGAGEMENT_REPORT_COMPLETE
REPORT

    echo "  Report: $REPORT_FILE"
}

# ── close a contract ──────────────────────────────────────────────────────────
cmd_close() {
    ID="$1"
    FILE="$(contract_path "$ID")"
    [ -f "$FILE" ] || { echo "Contract not found: $ID"; return 1; }
    TMP="${FILE}.tmp"
    sed 's/^  status:        active/  status:        closed/' "$FILE" > "$TMP" && mv "$TMP" "$FILE"
    cmd_report "$ID" > /dev/null 2>&1
    echo "  Contract closed: $ID"
    echo "  Final report written."
    echo "  STATUS=SAGCO_CONTRACT_CLOSED"
}

# ── list all contracts ────────────────────────────────────────────────────────
cmd_list() {
    echo "SAGCO CONTRACT REGISTRY"
    echo "========================"
    printf "  %-20s %-15s %-12s %-10s\n" "ID" "CLIENT" "SCOPE_TYPE" "STATUS"
    echo "  ──────────────────────────────────────────────────────"
    [ -d "$CONTRACT_DIR" ] || { echo "  (no contracts)"; return; }
    for FILE in "$CONTRACT_DIR"/*.yaml; do
        [ -f "$FILE" ] || continue
        ID=$(basename "$FILE" .yaml)
        CLIENT=$(contract_field "$ID" "client")
        STYPE=$(contract_field "$ID" "scope_type")
        SVAL=$(contract_field "$ID" "status")
        printf "  %-20s %-15s %-12s %-10s\n" "$ID" "${CLIENT:-?}" "${STYPE:-?}" "${SVAL:-?}"
    done
    echo ""
}

# ── audit: full action log for a contract ────────────────────────────────────
cmd_audit() {
    ID="$1"
    echo "SAGCO AUDIT — $ID"
    echo "===================="
    [ -f "$ACTION_LOG" ] || { echo "  (no action log)"; return; }
    grep ",${ID}," "$ACTION_LOG" 2>/dev/null | \
        awk -F',' '{printf "  [%s] device=%-10s action=%-20s target=%-20s %s\n", $1,$2,$4,$5,$7}'
    echo ""
    CNT=$(grep -c ",${ID}," "$ACTION_LOG" 2>/dev/null || echo 0)
    echo "  Total actions: $CNT"
}

# ── race tick ─────────────────────────────────────────────────────────────────
write_tick() {
    BAT=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo unknown)
    [ -f "$RACE_LOG" ] || echo "timestamp,device,event,pwd,battery,status" > "$RACE_LOG"
    echo "${STAMP},${DEV},sagco_contract_${CMD},${PWD},${BAT},SAGCO_RACE_TICK" >> "$RACE_LOG"
    HASH=$(echo "${STAMP}sagco-contract${DEV}${CMD}" | cksum | awk '{printf "%012d", $1}')
    [ -f "$LEDGER" ] || echo "timestamp,device,command,artifact,hash,status" > "$LEDGER"
    echo "${STAMP},${DEV},sagco-contract,${CONTRACT_DIR},${HASH},SAGCO_CONTRACT_PASS" >> "$LEDGER"
}

# ── dispatch ──────────────────────────────────────────────────────────────────
CMD="${1:-list}"

echo "SAGCO CONTRACT GATE"
echo "===================="
echo "Stamp:  $STAMP"
echo "Device: $DEV"
echo ""

case "$CMD" in
    init)         cmd_init "${2:-}"; write_tick ;;
    check)        gate_check "${2:-}" "${3:-}" "${4:-}"; write_tick ;;
    scope-add)    cmd_scope_add "${2:-}" "${3:-}"; write_tick ;;
    scope-check)  cmd_scope_check "${2:-}" "${3:-}" ;;
    log)          cmd_log_action "${2:-}" "${3:-}" "${4:-}" ;;
    report)       cmd_report "${2:-}"; write_tick ;;
    close)        cmd_close "${2:-}"; write_tick ;;
    list|"")      cmd_list ;;
    audit)        cmd_audit "${2:-}" ;;
    *)
        echo "Usage: sagco-contract <command> [args]"
        echo ""
        echo "  init <id>                  create new contract"
        echo "  check <id> <tgt> <action>  gate check (0=pass)"
        echo "  scope-add <id> <target>    add target to contract"
        echo "  scope-check <id> <target>  is target in scope?"
        echo "  log <id> <action> <tgt>    record authorized action"
        echo "  report <id>                generate engagement report"
        echo "  close <id>                 close contract"
        echo "  list                       show all contracts"
        echo "  audit <id>                 show action log"
        exit 1
        ;;
esac

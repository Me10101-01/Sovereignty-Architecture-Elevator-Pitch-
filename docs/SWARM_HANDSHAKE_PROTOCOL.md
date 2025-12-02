# Swarm Handshake Protocol (SWARM-HS)

A TCP-like specification for human-AI collaboration in the Strategickhaos ecosystem.

---

## Overview

SWARM-HS defines a structured loop for coordinating between:
- **Humans** (strategists, developers, operators)
- **AI Agents** (GPT, Claude, Copilot, specialized models)
- **Systems** (clusters, repositories, pipelines)

Like TCP establishes reliable communication between nodes, SWARM-HS establishes reliable collaboration between cognitive entities.

---

## Protocol Phases

### 1. SYN – Synchronization (Capture)

**Purpose**: Establish shared context between human and agent.

**Actions**:
- Capture current state (logs, code, configs, screenshots)
- Define intent in natural language
- Set boundaries (what's in-scope, what's off-limits)

**Artifacts**:
- `context.md` – Current situation and goals
- Raw telemetry (logs, metrics, traces)
- Constraints and guardrails

---

### 2. SYN-ACK – Acknowledgment (Proposal)

**Purpose**: Agent confirms understanding and proposes action.

**Actions**:
- Agent parses context and restates understanding
- Agent proposes specific changes (code, config, docs)
- Agent flags uncertainties or risks

**Artifacts**:
- Proposal summary
- Draft implementation or pseudocode
- Risk assessment

---

### 3. ACK – Application (Execute)

**Purpose**: Human approves and agent executes changes.

**Actions**:
- Human reviews proposal
- Human grants execution permission
- Agent applies changes to target system
- Changes are logged and versioned

**Artifacts**:
- Applied diffs
- Commit hashes
- Deployment manifests

---

### 4. FIN – Finalization (Observe)

**Purpose**: Confirm changes achieved intended effect.

**Actions**:
- Collect new telemetry post-change
- Compare against baseline
- Document outcomes

**Artifacts**:
- `findings.md` – What we learned
- Updated metrics/dashboards
- Next iteration triggers

---

## Message Format

Each SWARM-HS message includes:

```yaml
swarm_hs_message:
  phase: SYN | SYN-ACK | ACK | FIN
  timestamp: ISO-8601
  sender: human | agent-name
  intent: |
    Clear description of what this message accomplishes
  payload:
    # Phase-specific content
  trace_id: uuid-v4  # Links all messages in one handshake
```

---

## Error Handling

### RST – Reset

When handshake fails:
- Log failure reason
- Preserve all context for debugging
- Human decides: retry, modify, or abandon

### Timeout

If no response within defined window:
- Auto-escalate to human
- Log for pattern analysis

---

## Implementation Notes

1. **Idempotency**: Re-sending a phase message should be safe
2. **Auditability**: Every handshake is logged end-to-end
3. **Isolation**: Lab experiments run in dedicated namespaces
4. **Reversibility**: All changes can be rolled back

---

## Example Handshake

```text
[HUMAN → GPT] SYN
  Intent: Parse GKE audit logs for lease churn patterns
  Context: 24h of raw audit logs attached
  Constraints: No external API calls, output as CSV

[GPT → HUMAN] SYN-ACK
  Understanding: You want to identify abnormal lease activity
  Proposal: Python script using pandas, output lease_activity.csv
  Risks: Large log files may need chunking

[HUMAN → GPT] ACK
  Approved: Proceed with implementation
  Target: src/parsers/lease_parser.py

[GPT → HUMAN] FIN
  Applied: src/parsers/lease_parser.py (commit abc123)
  Result: 2,847 lease events parsed, 12 anomalies flagged
  Next: Review anomaly_reports.json
```

---

## References

- [BLACK_OPS_LAB.md](./BLACK_OPS_LAB.md) – Lab charter
- [EXPERIMENT_TEMPLATE.md](./EXPERIMENT_TEMPLATE.md) – Experiment documentation

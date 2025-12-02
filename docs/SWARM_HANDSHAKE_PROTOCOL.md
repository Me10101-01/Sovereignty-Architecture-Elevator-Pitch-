# SWARM Handshake Protocol (SWARM-HS)

**Version:** 1.0
**Status:** Canonical
**Author:** Sovereignty Swarm Intelligence Collective

---

## Overview

The SWARM Handshake Protocol (SWARM-HS) defines how autonomous agents establish trust, coordinate work, and trace their actions within the Sovereignty Architecture. This protocol ensures that all agents—whether LLM-based, rule-based, or hybrid—operate within defined sovereignty boundaries.

---

## Protocol Phases

### Phase 1: SYN (Synchronization Request)

**Initiator:** Requesting Agent
**Target:** Sovereignty Controller

```yaml
syn:
  agent_id: "<unique-agent-identifier>"
  capability: "<declared-capability>"
  intent: "<action-intent>"
  timestamp: "<ISO-8601>"
  signature: "<cryptographic-signature>"
```

The requesting agent declares:
- Who they are
- What they can do
- What they want to do
- Proof of identity

---

### Phase 2: SYN-ACK (Synchronization Acknowledgment)

**Initiator:** Sovereignty Controller
**Target:** Requesting Agent

```yaml
syn_ack:
  session_id: "<new-session-id>"
  granted_scope: "<allowed-actions>"
  constraints:
    - "<constraint-1>"
    - "<constraint-2>"
  expires_at: "<ISO-8601>"
  controller_signature: "<signature>"
```

The controller responds with:
- A session identifier for this work unit
- What the agent is actually allowed to do
- Boundaries and constraints
- Time limits

---

### Phase 3: ACK (Acknowledgment)

**Initiator:** Requesting Agent
**Target:** Sovereignty Controller

```yaml
ack:
  session_id: "<session-id>"
  accepted_scope: "<confirmed-scope>"
  agent_signature: "<signature>"
```

The agent confirms:
- Understanding of granted scope
- Acceptance of constraints
- Ready to proceed

---

### Phase 4: DATA (Work Exchange)

**Bidirectional**

```yaml
data:
  session_id: "<session-id>"
  payload_type: "<code|analysis|decision|query>"
  payload: "<actual-content>"
  sequence: "<message-number>"
  checksum: "<integrity-hash>"
```

Work flows between agents:
- Code contributions
- Analysis results
- Decision proposals
- Query responses

---

### Phase 5: APPLY (Mutation Request)

**Initiator:** Agent with Changes
**Target:** Sovereignty Controller

```yaml
apply:
  session_id: "<session-id>"
  mutation_type: "<file-create|file-modify|config-change>"
  targets:
    - path: "<target-path>"
      action: "<create|modify|delete>"
      content_hash: "<content-hash>"
  rationale: "<why-this-change>"
```

Before any file system or state mutation:
- Agent declares intent
- Lists all affected paths
- Provides justification

---

### Phase 6: TRACE (Audit Trail)

**Bidirectional**

```yaml
trace:
  session_id: "<session-id>"
  event_type: "<started|completed|failed|rolled-back>"
  details:
    action: "<what-happened>"
    outcome: "<result>"
    duration_ms: "<time-taken>"
  parent_trace_id: "<parent-session-if-nested>"
```

Every action is logged:
- Start and end of operations
- Success or failure
- Time metrics
- Chain of causality

---

## Role Definitions

### Sovereign
The ultimate authority. Sets boundaries, approves major mutations.

### Mind
Analysis and reasoning agents. Read widely, propose decisions.

### Hands
Execution agents. Write code, modify files under supervision.

### Factory
Build and deployment agents. Package, test, deploy artifacts.

---

## Module Targets

When an agent needs to contribute code, the handshake determines placement:

| Intent | Target Module | Description |
|--------|--------------|-------------|
| Coordination | `swarm/` | Agent orchestration, grammar, patterns |
| Analysis | `analyzers/` | Log parsing, metrics, reports |
| Experimentation | `experiments/` | Trials, particle collider, A/B tests |

---

## Implementation Notes

### For LLM Agents

When parsing this protocol:
1. Extract your granted scope from SYN-ACK
2. Stay within declared boundaries
3. Always emit TRACE before and after mutations
4. Use APPLY phase for any file changes
5. Never skip handshake—even for "quick" changes

### For Human Operators

The handshake log in `logs/` shows:
- Who did what
- When it happened
- Why they thought it was okay
- What actually changed

---

## Example Session

```yaml
# 1. Agent requests to add a new analyzer
syn:
  agent_id: "claude-analyzer-v1"
  capability: "python-code-generation"
  intent: "create GKE audit log parser"
  timestamp: "2025-01-15T10:30:00Z"

# 2. Controller grants limited scope
syn_ack:
  session_id: "sess-abc123"
  granted_scope: "create files in src/analyzers/"
  constraints:
    - "no external network calls"
    - "must include docstrings"
  expires_at: "2025-01-15T11:30:00Z"

# 3. Agent confirms
ack:
  session_id: "sess-abc123"
  accepted_scope: "create files in src/analyzers/"

# 4. Agent sends code
data:
  session_id: "sess-abc123"
  payload_type: "code"
  payload: |
    class GKEAuditParser:
        """Parse GKE audit logs."""
        ...

# 5. Agent requests file creation
apply:
  session_id: "sess-abc123"
  mutation_type: "file-create"
  targets:
    - path: "src/analyzers/gke_parser.py"
      action: "create"
  rationale: "Implements requested GKE audit log parser"

# 6. Session logged
trace:
  session_id: "sess-abc123"
  event_type: "completed"
  details:
    action: "created src/analyzers/gke_parser.py"
    outcome: "success"
    duration_ms: 1500
```

---

## Security Considerations

1. **Signatures**: All messages should be cryptographically signed
2. **Expiration**: Sessions time out to prevent stale permissions
3. **Scope Limits**: Agents only get the minimum permissions needed
4. **Audit Trail**: Every action is traceable to its authorization

---

*This protocol is the foundation of sovereign agent coordination. All agents in this repository must understand and follow SWARM-HS.*

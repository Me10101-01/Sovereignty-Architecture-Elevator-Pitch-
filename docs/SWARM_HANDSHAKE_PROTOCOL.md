# SWARM HANDSHAKE PROTOCOL v1.0

> "TCP for AIs - A 6-phase multi-agent synchronization protocol"

## Overview

The Swarm Handshake Protocol defines how the sovereign (human operator) coordinates with multiple AI agents (GPT, Claude, Copilot) in a structured, repeatable loop. This is the communication backbone of the sovereignty architecture.

Just as TCP ensures reliable delivery between networked computers, this protocol ensures reliable coordination between human and AI agents operating on shared codebases and infrastructure.

## Protocol Phases

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SWARM HANDSHAKE PROTOCOL                              │
│                                                                             │
│   SOVEREIGN ──SYN──> MIND ──SYN-ACK──> CLAUDE ──ACK──>                     │
│                                                                             │
│   ──DATA──> SOVEREIGN ──APPLY──> CLUSTER ──TRACE──> [LOOP]                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Phase 1: SYN (Synchronize)

**Actor**: Sovereign (Human)
**Action**: Initiate request with context and goal

```
SOVEREIGN -> AGENT:
{
    "phase": "SYN",
    "context": "Current system state and relevant history",
    "goal": "Clear statement of desired outcome",
    "constraints": ["time", "resources", "security requirements"],
    "session_id": "unique_session_identifier"
}
```

**Key Principle**: The sovereign always initiates. Context is king.

### Phase 2: SYN-ACK (Synchronize-Acknowledge)

**Actor**: First Agent (e.g., GPT-4)
**Action**: Acknowledge receipt, add perspective, propose approach

```
AGENT_1 -> SOVEREIGN:
{
    "phase": "SYN-ACK",
    "understanding": "Restated goal in agent's words",
    "perspective": "Agent's analysis and insights",
    "proposed_approach": "Suggested path forward",
    "questions": ["Clarifying questions if any"],
    "session_id": "same_session_identifier"
}
```

**Key Principle**: Verify understanding before proceeding.

### Phase 3: ACK (Acknowledge)

**Actor**: Second Agent (e.g., Claude)
**Action**: Confirm synthesis, add complementary perspective

```
AGENT_2 -> SOVEREIGN:
{
    "phase": "ACK",
    "synthesis": "Combined understanding from all perspectives",
    "additions": "Complementary insights or concerns",
    "alignment": "Confirmation of approach or suggested modifications",
    "session_id": "same_session_identifier"
}
```

**Key Principle**: Multiple perspectives strengthen the solution.

### Phase 4: DATA (Data Transfer)

**Actor**: All Agents
**Action**: Produce structured outputs

```
AGENTS -> SOVEREIGN:
{
    "phase": "DATA",
    "artifacts": [
        {
            "type": "code|config|documentation|analysis",
            "content": "The actual artifact",
            "rationale": "Why this approach was chosen",
            "agent": "Which agent produced this"
        }
    ],
    "session_id": "same_session_identifier"
}
```

**Key Principle**: All outputs are attributable and justified.

### Phase 5: APPLY (Apply Changes)

**Actor**: Sovereign (Human)
**Action**: Apply changes to systems

```
SOVEREIGN -> SYSTEMS:
{
    "phase": "APPLY",
    "actions": [
        {
            "type": "git_commit|kubectl_apply|file_edit|script_run",
            "target": "Where the change is applied",
            "content": "What was changed",
            "verification": "How to verify success"
        }
    ],
    "session_id": "same_session_identifier"
}
```

**Key Principle**: The sovereign controls all mutations.

### Phase 6: TRACE (Trace and Log)

**Actor**: System + Sovereign
**Action**: Log everything for observability

```
SYSTEM -> LOGS:
{
    "phase": "TRACE",
    "session_id": "same_session_identifier",
    "duration_ms": 45000,
    "phases_completed": ["SYN", "SYN-ACK", "ACK", "DATA", "APPLY"],
    "artifacts_produced": 3,
    "changes_applied": 2,
    "success": true,
    "next_action": "Description of recommended next step"
}
```

**Key Principle**: What isn't logged didn't happen.

## Protocol Rules

### 1. Session Continuity
- Each handshake has a unique session_id
- All phases reference the same session_id
- Sessions can be resumed from any phase

### 2. Sovereign Authority
- Only the sovereign initiates (SYN phase)
- Only the sovereign applies changes (APPLY phase)
- Agents propose, sovereign disposes

### 3. Traceability
- Every phase is logged
- Every artifact is attributed
- Every decision has rationale

### 4. Graceful Degradation
- If an agent is unavailable, proceed with remaining agents
- If DATA is insufficient, loop back to SYN-ACK
- If APPLY fails, TRACE captures failure for debugging

## Implementation

```python
from swarm import handshake_protocol

# Execute the full handshake
result = handshake_protocol(
    input_path="/abs/path/to/context.md",
    agents=["gpt-4", "claude", "copilot"]
)

# Check phase completion
for phase, status in result["phases"].items():
    print(f"{phase}: {status}")
```

## Integration with Swarm Orchestrator

The handshake protocol is invoked via:

```bash
python src/main.py handshake \
    --input /abs/path/to/context.md \
    --name "swarm_sync" \
    --agents "claude,copilot,gpt-4"
```

## Protocol Extensions

### Multi-Round Handshakes
For complex tasks, multiple handshakes can be chained:

```
[Handshake 1: Discovery] -> [Handshake 2: Design] -> [Handshake 3: Implementation]
```

### Parallel Handshakes
Independent tasks can run parallel handshakes:

```
[Handshake A: Frontend] ─┬─> [Merge Point]
[Handshake B: Backend]  ─┘
```

### Checkpoint Recovery
Failed handshakes can resume from checkpoint:

```
[SYN] -> [SYN-ACK] -> [FAIL] -> [RECOVER from SYN-ACK] -> [ACK] -> ...
```

## Version History

- **v1.0** - Initial protocol specification
  - 6-phase synchronization model
  - Session-based continuity
  - Sovereign authority model

---

*"TCP for AIs - Because coordination is not optional."*

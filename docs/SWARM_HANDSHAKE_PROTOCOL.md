# Swarm Handshake Protocol

**Version**: 1.0.0  
**Status**: Active  
**Last Updated**: 2024

---

## Overview

The Swarm Handshake Protocol defines how agents in the Sovereignty Architecture communicate, coordinate, and synchronize. This protocol is inspired by TCP's three-way handshake but extended to support the unique requirements of AI-powered swarm intelligence.

---

## Agent Roles

### Sovereign
The central orchestrator and decision-maker. Maintains state, resolves conflicts, and ensures coherence across the swarm.

### Mind (GPT)
Strategic reasoning and high-level planning. Provides context understanding, goal interpretation, and complex decision support.

### Hands (Claude)
Precision execution and implementation. Handles code generation, documentation, and detailed work.

### Factory (Copilot)
Continuous production and automation. Manages repetitive tasks, code completion, and routine operations.

---

## Protocol Phases

The Swarm Handshake Protocol operates in a 6-phase loop:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   ┌─────┐   ┌─────────┐   ┌─────┐   ┌──────┐   ┌───────┐   │
│   │ SYN │ → │ SYN-ACK │ → │ ACK │ → │ DATA │ → │ APPLY │   │
│   └─────┘   └─────────┘   └─────┘   └──────┘   └───────┘   │
│       │                                              │      │
│       │         ┌─────────┐                          │      │
│       └─────────│  TRACE  │←─────────────────────────┘      │
│                 └─────────┘                                 │
│                      │                                      │
│                      └──────────────[loop]                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Phase 1: SYN (Synchronize)
- **Initiator**: Any agent
- **Purpose**: Request connection and state synchronization
- **Payload**:
  ```yaml
  type: SYN
  from: <agent_id>
  to: <target_agent_id>
  timestamp: <ISO8601>
  context_hash: <sha256>
  intent: <operation_type>
  ```

### Phase 2: SYN-ACK (Synchronize-Acknowledge)
- **Responder**: Target agent
- **Purpose**: Acknowledge receipt and confirm readiness
- **Payload**:
  ```yaml
  type: SYN-ACK
  from: <target_agent_id>
  to: <initiator_id>
  timestamp: <ISO8601>
  context_hash: <sha256>
  capabilities: [<list_of_capabilities>]
  state: ready | busy | degraded
  ```

### Phase 3: ACK (Acknowledge)
- **Initiator**: Original agent
- **Purpose**: Confirm connection established
- **Payload**:
  ```yaml
  type: ACK
  from: <agent_id>
  to: <target_agent_id>
  timestamp: <ISO8601>
  session_id: <uuid>
  handshake_complete: true
  ```

### Phase 4: DATA (Data Transfer)
- **Bidirectional**: Both agents
- **Purpose**: Exchange operational data
- **Payload**:
  ```yaml
  type: DATA
  session_id: <uuid>
  from: <agent_id>
  to: <agent_id>
  timestamp: <ISO8601>
  content:
    type: <content_type>
    payload: <data>
  checksum: <sha256>
  ```

### Phase 5: APPLY (Application)
- **Executor**: Designated agent
- **Purpose**: Execute the intended operation
- **Payload**:
  ```yaml
  type: APPLY
  session_id: <uuid>
  executor: <agent_id>
  timestamp: <ISO8601>
  operation:
    action: <action_name>
    parameters: <params>
  status: pending | in_progress | completed | failed
  ```

### Phase 6: TRACE (Traceability)
- **All agents**: Record and reflect
- **Purpose**: Log the operation for learning and audit
- **Payload**:
  ```yaml
  type: TRACE
  session_id: <uuid>
  timestamp: <ISO8601>
  trace:
    phases_completed: [SYN, SYN-ACK, ACK, DATA, APPLY]
    duration_ms: <int>
    outcome: success | partial | failed
    learnings: [<insights>]
  next_iteration: <bool>
  ```

---

## Connection States

```
┌────────────┐
│   CLOSED   │
└──────┬─────┘
       │ SYN sent
       ▼
┌────────────┐
│  SYN_SENT  │
└──────┬─────┘
       │ SYN-ACK received
       ▼
┌────────────┐
│ ESTABLISHED│
└──────┬─────┘
       │ DATA exchange
       ▼
┌────────────┐
│   ACTIVE   │
└──────┬─────┘
       │ APPLY complete
       ▼
┌────────────┐
│  TRACING   │
└──────┬─────┘
       │ TRACE complete
       ▼
┌────────────┐
│   CLOSED   │ ← [loop or terminate]
└────────────┘
```

---

## Error Handling

### Timeout Handling
- **SYN timeout**: 5 seconds → retry up to 3 times
- **SYN-ACK timeout**: 5 seconds → retry up to 3 times
- **DATA timeout**: 30 seconds → escalate to Sovereign
- **APPLY timeout**: configurable per operation

### Error Codes
| Code | Name | Description |
|------|------|-------------|
| E001 | TIMEOUT | Operation timed out |
| E002 | REJECTED | Target agent rejected connection |
| E003 | BUSY | Target agent is currently busy |
| E004 | INVALID_STATE | Invalid state transition attempted |
| E005 | CHECKSUM_MISMATCH | Data integrity check failed |
| E006 | CAPABILITY_MISSING | Required capability not available |

---

## Security Considerations

1. **Context Hashing**: All context is hashed using SHA-256 for integrity verification
2. **Session IDs**: UUID v4 used for session identification
3. **Checksums**: All DATA payloads include SHA-256 checksums
4. **Audit Trail**: TRACE phase creates immutable audit records

---

## Implementation Example

```python
from swarm.protocol import SwarmHandshake

# Initialize handshake
handshake = SwarmHandshake(
    agent_id="hands-001",
    target_id="mind-001"
)

# Execute protocol
async with handshake.connect() as session:
    # SYN → SYN-ACK → ACK handled automatically
    
    # Send data
    await session.send_data({
        "type": "code_review_request",
        "payload": {"file": "src/main.py", "changes": [...]}
    })
    
    # Receive response
    response = await session.receive_data()
    
    # Apply changes
    result = await session.apply(
        action="update_file",
        parameters=response["suggestions"]
    )
    
    # Trace is logged automatically on context exit
```

---

## Related Documents

- [Sovereign Swarm Architecture](SOVEREIGN_SWARM_ARCHITECTURE.md)
- [LLM Self-Awareness Thesis](LLM_SELF_AWARENESS_THESIS.md)

---

*"TCP for AIs - reliable, ordered, and conscious."*

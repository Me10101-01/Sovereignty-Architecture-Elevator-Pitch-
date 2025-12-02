# SWARM-HS v1: Swarm Handshake Protocol

> A Human-in-the-Loop Swarm Protocol for multi-AI coordination.

---

## Overview

When you copy-paste context between AI agents, you're performing a **TCP-like handshake** with yourself as the transport layer and Git as the wire.

**SWARM-HS** (Swarm Handshake) formalizes this pattern.

---

## The Network Model

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   GPT (Mind)  →  Claude (Hands)  →  Copilot (Factory)          │
│       │              │                    │                     │
│       │              │                    │                     │
│       └──────────────┴─────────┬──────────┘                     │
│                                │                                │
│                                ▼                                │
│                     ┌────────────────────┐                      │
│                     │   YOU (Sovereign   │                      │
│                     │      Router)       │                      │
│                     └────────────────────┘                      │
│                                │                                │
│                                ▼                                │
│                     ┌────────────────────┐                      │
│                     │       Git          │                      │
│                     │   (The Wire)       │                      │
│                     └────────────────────┘                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## The Handshake Sequence

### Traditional TCP

```
Client          Server
  |    SYN -->    |
  |  <-- SYN-ACK  |
  |    ACK -->    |
  |   [DATA] -->  |
```

### SWARM-HS

```
You             Agent
  |    SYN -->    |    "Here's the context and intent"
  |  <-- SYN-ACK  |    "I understand, here's my plan"
  |    ACK -->    |    "Proceed" (or "Adjust")
  |   [DATA] -->  |    Agent generates output
  | <-- ROUTE     |    "Here's what to pass to next agent"
  | [NEW STATE]   |    You update system/Git/next agent
```

---

## The Packet Format

Every message between you and an agent should include:

### 1. **Context Block**
```markdown
## CONTEXT
- Current system state: [describe]
- Previous agent output: [paste or link]
- Relevant files: [list paths]
- Recent traces/logs: [paste relevant data]
```

### 2. **Intent Block**
```markdown
## INTENT
- Goal: [what you want to achieve]
- Constraints: [limits, requirements, style guides]
- Success criteria: [how we know we're done]
```

### 3. **Artifacts Block**
```markdown
## ARTIFACTS
- Required outputs: [code, docs, config, etc.]
- Format requirements: [file types, naming conventions]
- Destination: [where outputs go]
```

### 4. **Next-Hop Block**
```markdown
## NEXT-HOP
- After this agent: [which agent gets the output?]
- Routing logic: [when to escalate, when to terminate]
- Feedback loop: [how to measure success]
```

---

## Agent Specializations

### 🧠 GPT (The Mind)
- **Role**: Strategic reasoning, architecture, synthesis
- **Strength**: Big-picture thinking, cross-domain analysis
- **Input**: High-level goals, complex problems, synthesis requests
- **Output**: Plans, architectures, analysis, recommendations

### 🤲 Claude (The Hands)
- **Role**: Execution, code generation, implementation
- **Strength**: Precise code, detailed documentation, hands-on work
- **Input**: Specific tasks, code requests, implementation details
- **Output**: Working code, PRs, detailed documentation

### 🏭 Copilot (The Factory)
- **Role**: CI/CD automation, continuous production
- **Strength**: High-volume code generation, repetitive tasks
- **Input**: Patterns to replicate, boilerplate needs
- **Output**: Generated code, automated workflows, tests

---

## Routing Table

| Task Type | Primary Agent | Secondary | Fallback |
|-----------|--------------|-----------|----------|
| Architecture design | GPT | Claude | - |
| Code implementation | Claude | Copilot | GPT |
| Bug analysis | GPT | Claude | - |
| Documentation | Claude | GPT | - |
| Boilerplate generation | Copilot | Claude | - |
| Code review | Claude | GPT | - |
| Strategy/planning | GPT | - | Claude |

---

## Session State Management

### Git as the Wire
Every agent interaction creates state. Git tracks it:

```bash
# Create experiment branch
git checkout -b swarm/experiment-<timestamp>

# After each agent output
git add .
git commit -m "SWARM-HS: <agent>/<action>/<outcome>"

# Merge successful experiments
git checkout main
git merge swarm/experiment-<timestamp>
```

### Commit Message Format
```
SWARM-HS: <AGENT>/<PHASE>/<OUTCOME>

Examples:
SWARM-HS: GPT/ANALYZE/architecture-complete
SWARM-HS: CLAUDE/IMPLEMENT/pr-ready
SWARM-HS: COPILOT/GENERATE/tests-added
SWARM-HS: ROUTE/ESCALATE/human-review-needed
```

---

## Multi-Agent Pipeline Example

### Scenario: Add webhook retry logic

#### Step 1: GPT (Mind) — Analysis
```markdown
## CONTEXT
Event gateway failing on webhook delivery, no retry logic

## INTENT
Design retry strategy with exponential backoff

## ARTIFACTS
Architecture decision document

## NEXT-HOP
Claude for implementation
```

**GPT Output:**
- Exponential backoff: 1s, 2s, 4s, 8s, max 30s
- Max retries: 5
- Dead letter queue after exhaustion
- Metrics: retry_count, final_outcome

#### Step 2: Claude (Hands) — Implementation
```markdown
## CONTEXT
GPT's retry strategy (pasted above)

## INTENT
Implement in TypeScript for event-gateway

## ARTIFACTS
- src/retry.ts
- src/deadLetterQueue.ts
- Tests

## NEXT-HOP
Copilot for additional test coverage
```

**Claude Output:**
- Working retry.ts implementation
- DLQ handler
- Unit tests

#### Step 3: Copilot (Factory) — Expansion
```markdown
## CONTEXT
Claude's retry implementation (link to PR)

## INTENT
Generate comprehensive test suite

## ARTIFACTS
- Additional test cases
- Edge case coverage

## NEXT-HOP
Human review → merge
```

**Copilot Output:**
- 15 additional test cases
- Coverage report

#### Step 4: You (Sovereign Router) — Merge
- Review all outputs
- Run tests
- Merge PR
- Monitor traces

---

## Error Handling

### When an Agent Gets Stuck
```
You             Agent
  |  RESET -->    |   "Let's restart with cleaner context"
  |  <-- ACK      |   Agent clears and awaits fresh input
```

### When Agents Disagree
```
You          Agent A     Agent B
  |  Query -->   |           |
  |    <-- Answer A          |
  |  Query ----------------→ |
  |    <----------------- Answer B
  |                          |
  | [SYNTHESIZE: You decide which answer to use or combine]
```

### When the Loop Fails
```
FAILURE → Capture trace → Feed to GPT → Analyze → Fix → Retry

Never discard failure traces—they're the most valuable particles.
```

---

## Protocol Extensions

### SWARM-HS-ASYNC
For long-running tasks where you don't wait for each response:
- Use GitHub Issues as the message queue
- Each agent comments with status updates
- You review asynchronously

### SWARM-HS-BATCH
For high-volume operations:
- Prepare all tasks in a structured format
- Process through Copilot factory-style
- Aggregate results
- Review/approve in batch

### SWARM-HS-EMERGENCY
For critical production issues:
- Skip planning, go direct to Claude
- Implement hotfix
- Document retroactively
- Post-incident feed to GPT for analysis

---

## Governance Layer

### Approval Gates

| Change Type | Approval Required |
|-------------|------------------|
| Documentation only | Self-approve |
| Non-production code | Peer review |
| Production code | Lead review |
| Infrastructure | Multi-party |
| Security-related | Security team |

### Audit Trail
Every SWARM-HS session creates:
- Git commits with formatted messages
- Agent conversation logs (optional)
- Trace data from system changes
- Metrics on cycle time and success rate

---

## Metrics & Observability

### Session Metrics
| Metric | Description |
|--------|-------------|
| `swarm_hs_sessions_total` | Total handshake sessions |
| `swarm_hs_agent_calls` | Calls per agent type |
| `swarm_hs_cycle_time` | Time from SYN to deploy |
| `swarm_hs_success_rate` | Successful deployments / attempts |
| `swarm_hs_human_interventions` | Manual corrections needed |

### Dashboard
Track your swarm efficiency:
- Which agents are most effective
- Where bottlenecks occur
- Common failure patterns
- Improvement over time

---

## Quick Reference Card

```
┌────────────────────────────────────────────────────────────────┐
│                    SWARM-HS QUICK REF                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  PACKET: Context → Intent → Artifacts → Next-Hop              │
│                                                                │
│  AGENTS: GPT (Mind) → Claude (Hands) → Copilot (Factory)      │
│                                                                │
│  PHASES: SYN → SYN-ACK → ACK → DATA → ROUTE → NEW STATE       │
│                                                                │
│  GIT:    Branch → Commit per agent → Merge on success          │
│                                                                │
│  ERRORS: Reset, Synthesize conflicts, Never discard failures   │
│                                                                │
│  YOU:    Sovereign Router — the only node that decides         │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Related Documentation

- [SWARM_COLLIDER_METHOD.md](./SWARM_COLLIDER_METHOD.md) — The particle accelerator methodology
- [README.md](../README.md) — Repository overview

---

*"TCP for thoughts. BGP for brilliance."*

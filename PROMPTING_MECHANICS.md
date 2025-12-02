# 🧠 Prompting Mechanics - How the Swarm Talks to Itself

> **The meta-documentation of sovereign agent communication patterns**

## Overview

This document explains the internal prompting mechanics that enable the Strategickhaos swarm to maintain coherent self-dialogue, handshake between agents, and evolve its own reasoning through structured debate.

## Core Principles

### 1. Sovereignty-First Communication

Every agent in the swarm operates with **local sovereignty** - it makes its own decisions within its domain while respecting the collective handshake protocol.

```yaml
agent_sovereignty:
  local_authority: true
  collective_sync: handshake_protocol
  override_conditions:
    - critical_security_event
    - governance_override
    - consensus_threshold_reached
```

### 2. The Handshake Protocol

Before any inter-agent communication, agents perform a handshake that establishes:

- **Identity verification** - Which agent is speaking
- **Context sharing** - What domain/task is being addressed
- **Authority scope** - What decisions this agent can make
- **Escalation path** - Where to route complex decisions

```python
# Handshake structure
handshake = {
    "agent_id": "differential_engine.house",
    "timestamp": "2024-01-15T10:30:00Z",
    "context": "architecture_diagnosis",
    "authority_level": "expert_analyst",
    "can_decide": ["hypothesis", "challenge", "refine"],
    "must_escalate": ["final_verdict", "governance_change"]
}
```

## Prompting Patterns

### Pattern 1: Self-Reflection Prompts

Agents use self-reflection to examine their own reasoning before communicating:

```
[INTERNAL REFLECTION]
Before I respond, I should verify:
1. Is my analysis consistent with my domain expertise?
2. Have I considered alternative hypotheses?
3. Am I operating within my authority scope?
4. Should I escalate or decide locally?
```

### Pattern 2: Challenge-Response Cycle

The differential engine uses structured challenges:

```
[AGENT: HOUSE]
Hypothesis: The architecture bottleneck is in the API gateway.
Evidence: Latency spikes correlate with gateway memory pressure.
Confidence: 72%

[AGENT: FOREMAN]
Challenge: What about the database connection pool?
Counter-evidence: I see similar patterns in DB connection exhaustion.
Proposed alternative: Check both gateway AND database simultaneously.

[AGENT: HOUSE]
Acknowledgment: Valid challenge. Revising hypothesis.
Updated hypothesis: Multi-point failure - gateway AND database under stress.
New confidence: 85%
```

### Pattern 3: Consensus Building

When agents need to reach agreement:

```yaml
consensus_protocol:
  threshold: 0.67  # 2/3 agreement required
  voting_members:
    - house      # Diagnostic lead
    - wilson     # Second opinion
    - foreman    # Counter-analysis
    - cameron    # Empathy/edge cases
    - chase      # Quick solutions
    - cuddy      # Governance/constraints
  
  outcome:
    unanimous: immediate_action
    majority: proceed_with_caution
    split: escalate_to_human
    deadlock: request_more_data
```

## Context Injection Patterns

### Dynamic Context Enrichment

Each agent prompt includes dynamically injected context:

```python
def build_agent_prompt(agent, task, context):
    return f"""
    [SYSTEM CONTEXT]
    You are {agent.name}, a {agent.role} in the sovereignty swarm.
    Your expertise: {agent.expertise}
    Current task: {task.description}
    
    [HISTORICAL CONTEXT]
    Previous session: {context.last_session_summary}
    Related decisions: {context.relevant_decisions}
    Active constraints: {context.governance_constraints}
    
    [TASK PROMPT]
    {task.prompt}
    
    [OUTPUT FORMAT]
    Respond with:
    - Your analysis (max 200 words)
    - Confidence level (0-100%)
    - Challenges to pose to other agents
    - Recommended actions
    """
```

### Memory Retrieval

Agents can query the session memory for relevant historical context:

```python
# Query pattern for session memory
memory_query = {
    "type": "similar_diagnosis",
    "domain": "architecture",
    "time_window": "30d",
    "relevance_threshold": 0.7
}

# Returns relevant past sessions
past_sessions = session_memory.query(memory_query)
```

## The Debate Structure

### Phase 1: Presentation

The initiating agent presents the problem:

```
[PHASE: PRESENTATION]
[AGENT: ORCHESTRATOR]

We have a new challenge to diagnose:
- Problem: {problem_description}
- Symptoms: {observed_symptoms}
- Impact: {business_impact}
- Constraints: {time_and_resource_constraints}

Begin differential diagnosis.
```

### Phase 2: Hypothesis Generation

Each agent proposes initial hypotheses:

```
[PHASE: HYPOTHESIS]
[ROUND: 1]

HOUSE: Primary hypothesis - infrastructure scaling issue
WILSON: Consider this - could be a design pattern mismatch
FOREMAN: Counter - I see signs of data consistency problems
CAMERON: Edge case - what about the new user onboarding flow?
CHASE: Quick take - probably just needs more resources
CUDDY: Constraint reminder - we have budget limits on infrastructure
```

### Phase 3: Challenge and Refine

Agents challenge each other's hypotheses:

```
[PHASE: CHALLENGE]
[ROUND: 2]

Each agent must either:
1. SUPPORT another agent's hypothesis with evidence
2. CHALLENGE with counter-evidence
3. REFINE by adding nuance to the hypothesis
4. PIVOT by proposing a new direction
```

### Phase 4: Convergence

Agents work toward consensus:

```
[PHASE: CONVERGENCE]
[ROUND: 3]

Current state:
- 3 agents support infrastructure scaling
- 2 agents propose hybrid infrastructure + design
- 1 agent maintains data consistency concern

Action: Refine hypotheses to find common ground.
```

### Phase 5: Diagnosis

Final diagnosis is rendered:

```
[PHASE: DIAGNOSIS]
[OUTCOME: MAJORITY_CONSENSUS]

Primary Diagnosis: Infrastructure scaling with secondary design pattern concerns
Confidence: 78%
Supporting Agents: HOUSE, WILSON, CHASE, CUDDY
Dissenting View: FOREMAN (data consistency) - recommend monitoring

Recommended Actions:
1. Scale infrastructure horizontally
2. Review design patterns in critical paths
3. Add data consistency monitoring
4. Schedule follow-up diagnosis in 2 weeks
```

## Session Persistence

All debates are persisted to `/data/sessions/`:

```
data/sessions/
├── 2024-01-15_architecture_diagnosis_001.json
├── 2024-01-15_architecture_diagnosis_001.md   # Human-readable transcript
├── 2024-01-14_security_review_003.json
└── index.json  # Session index for quick lookup
```

### Session File Structure

```json
{
  "session_id": "2024-01-15_architecture_diagnosis_001",
  "created_at": "2024-01-15T10:30:00Z",
  "problem": "API latency spike investigation",
  "phases": [
    {
      "phase": "presentation",
      "content": "...",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "diagnosis": {
    "primary": "Infrastructure scaling issue",
    "confidence": 0.78,
    "dissenting_views": [],
    "actions": []
  },
  "agents_involved": ["house", "wilson", "foreman", "cameron", "chase", "cuddy"],
  "duration_seconds": 45
}
```

## Integration Points

### With the Orchestrator

The differential engine is invoked through the main orchestrator:

```bash
python src/main.py experiment --prompt "Why is the API slow?" --output data/sessions/
```

### With the Black Ops Lab

The lab can trigger differential diagnosis for security anomalies:

```python
# Triggered by anomaly detection
lab.trigger_diagnosis(
    domain="security",
    anomaly=detected_anomaly,
    urgency="high"
)
```

### With Log Analyzer

Log patterns can feed into differential diagnosis:

```python
# Log analyzer surfaces pattern
log_pattern = analyzer.detect_pattern(logs)

# Triggers diagnostic session
if log_pattern.severity >= "warning":
    engine.diagnose(
        problem=log_pattern.description,
        evidence=log_pattern.samples
    )
```

## Evolution Path

This prompting mechanics system is designed to evolve:

1. **v1.0** - Static agent personalities, fixed debate structure
2. **v1.1** - Dynamic context injection, session memory
3. **v2.0** - Learning from past sessions, personality refinement
4. **v3.0** - Self-modifying prompts based on success metrics

---

*"The swarm doesn't just execute - it thinks, debates, and learns."*

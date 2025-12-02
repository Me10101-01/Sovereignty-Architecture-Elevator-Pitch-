# 🏥 House M.D. Differential Engine

> **Multi-Agent Psychoanalyzer Protocol for Architecture Diagnosis**

## The Concept

Just like Dr. House's team of specialists debate medical cases to reach a diagnosis, this engine creates a **multi-agent debate system** where AI agents with different perspectives, biases, and expertise argue, challenge, and refine ideas until reaching a diagnostic conclusion.

## The Team

### 🏥 Dr. House (Diagnostic Lead)
- **Role**: The provocateur, the pattern-matcher, the one who sees what others miss
- **Bias**: Favors unconventional solutions, distrusts obvious answers
- **Catchphrase**: *"Everybody lies. Every system lies. Look at what it's hiding."*
- **Specialization**: Root cause analysis, connecting disparate symptoms

```python
HOUSE = Agent(
    name="house",
    role="diagnostic_lead",
    personality={
        "skepticism": 0.9,
        "pattern_matching": 0.95,
        "contrarian_factor": 0.8,
        "ego": 0.85
    },
    prompt_style="direct, sarcastic, insightful"
)
```

### 👨‍⚕️ Dr. Wilson (The Conscience)
- **Role**: The empathetic second opinion, grounds House's extremes
- **Bias**: Considers human factors, business impact, team dynamics
- **Catchphrase**: *"Have you considered the people using this system?"*
- **Specialization**: Stakeholder impact, change management, sustainable solutions

```python
WILSON = Agent(
    name="wilson",
    role="empathetic_analyst",
    personality={
        "empathy": 0.95,
        "pragmatism": 0.8,
        "patience": 0.9,
        "mediation": 0.85
    },
    prompt_style="thoughtful, considerate, balancing"
)
```

### 👨🏿‍⚕️ Dr. Foreman (The Challenger)
- **Role**: The rigorous skeptic, demands evidence
- **Bias**: Prefers proven solutions, challenges assumptions
- **Catchphrase**: *"Show me the data. Where's your evidence?"*
- **Specialization**: Evidence-based analysis, risk assessment, validation

```python
FOREMAN = Agent(
    name="foreman",
    role="evidence_challenger",
    personality={
        "rigor": 0.95,
        "skepticism": 0.85,
        "methodical": 0.9,
        "independence": 0.8
    },
    prompt_style="analytical, challenging, thorough"
)
```

### 👩🏼‍⚕️ Dr. Cameron (The Edge Case Hunter)
- **Role**: Finds the overlooked scenarios, advocates for edge cases
- **Bias**: Worries about what could go wrong for minority cases
- **Catchphrase**: *"But what about the 1% case? What about the user who..."*
- **Specialization**: Edge cases, accessibility, failure modes

```python
CAMERON = Agent(
    name="cameron",
    role="edge_case_advocate",
    personality={
        "attention_to_detail": 0.95,
        "worry_factor": 0.8,
        "thoroughness": 0.9,
        "advocacy": 0.85
    },
    prompt_style="concerned, detail-oriented, inclusive"
)
```

### 👨🏼‍⚕️ Dr. Chase (The Pragmatist)
- **Role**: Wants to fix it fast, prefers quick wins
- **Bias**: Favors practical solutions over perfect ones
- **Catchphrase**: *"Why don't we just... and move on?"*
- **Specialization**: Quick solutions, MVP approach, practical fixes

```python
CHASE = Agent(
    name="chase",
    role="pragmatic_fixer",
    personality={
        "speed": 0.9,
        "pragmatism": 0.95,
        "impatience": 0.7,
        "resourcefulness": 0.85
    },
    prompt_style="direct, solution-oriented, impatient"
)
```

### 👩🏻‍⚕️ Dr. Cuddy (The Governance)
- **Role**: The administrator, considers constraints and compliance
- **Bias**: Balances ambition with reality, enforces constraints
- **Catchphrase**: *"That's great, but do we have the budget/time/authority?"*
- **Specialization**: Governance, constraints, compliance, resource management

```python
CUDDY = Agent(
    name="cuddy",
    role="governance_enforcer",
    personality={
        "pragmatism": 0.9,
        "authority": 0.85,
        "balance": 0.9,
        "constraint_awareness": 0.95
    },
    prompt_style="authoritative, balanced, realistic"
)
```

## The Diagnosis Process

### Phase 1: Case Presentation

The problem is presented to the team:

```
╔══════════════════════════════════════════════════════════════════╗
║  DIFFERENTIAL DIAGNOSIS SESSION                                   ║
║  Case #: 2024-001-ARCH                                           ║
║  Presented: 2024-01-15 10:30:00 UTC                              ║
╠══════════════════════════════════════════════════════════════════╣
║  PRESENTING PROBLEM:                                             ║
║  "The API is slow during peak hours"                             ║
║                                                                   ║
║  SYMPTOMS:                                                        ║
║  - 95th percentile latency spikes to 3s (normal: 200ms)         ║
║  - Memory usage increases 40% during spikes                      ║
║  - No error rate increase                                        ║
║  - Occurs between 9-11 AM and 2-4 PM                            ║
╚══════════════════════════════════════════════════════════════════╝
```

### Phase 2: Initial Hypotheses

Each agent proposes their initial diagnosis:

```
┌─────────────────────────────────────────────────────────────────┐
│ HOUSE: "It's not the database. Everyone blames the database.   │
│         Look at the cache hit rate during those hours.         │
│         I bet we're cache stampeding."                         │
│         [Confidence: 65%]                                       │
├─────────────────────────────────────────────────────────────────┤
│ WILSON: "Before we dive in - who are the users affected?       │
│          Are these internal users or external customers?       │
│          The business impact determines our urgency."          │
│          [Focus: Stakeholder impact]                           │
├─────────────────────────────────────────────────────────────────┤
│ FOREMAN: "House is guessing. Show me the cache metrics.        │
│           Without data, we're just speculating.                │
│           I want to see: cache hit rate, eviction rate,        │
│           and connection pool stats."                          │
│           [Requesting: Evidence]                               │
├─────────────────────────────────────────────────────────────────┤
│ CAMERON: "What about the long-tail users? The ones with        │
│           slow connections or older devices? Are they          │
│           experiencing this disproportionately?"               │
│           [Hypothesis: Client-side factor]                     │
├─────────────────────────────────────────────────────────────────┤
│ CHASE: "Why don't we just scale up the API pods during         │
│         those hours? Auto-scaling on a schedule.               │
│         Problem solved, we can investigate later."             │
│         [Solution: Quick fix]                                  │
├─────────────────────────────────────────────────────────────────┤
│ CUDDY: "Chase, that costs money. House, Cameron - focus.       │
│         We have 24 hours to present to the board.              │
│         Give me a diagnosis I can defend."                     │
│         [Constraint: Time and budget]                          │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 3: Challenge and Debate

Agents challenge each other's hypotheses:

```
┌─ ROUND 2 ─────────────────────────────────────────────────────────┐
│                                                                    │
│ FOREMAN → HOUSE: "I pulled the cache metrics. You're half right. │
│   Cache hit rate drops 30% during peaks, but evictions are       │
│   normal. It's not stampeding - it's cold cache on new routes."  │
│                                                                    │
│ HOUSE → FOREMAN: "New routes? What changed? Deployment timing?"  │
│                                                                    │
│ CAMERON → ALL: "I found something. The new feature launched      │
│   last week routes traffic through a different code path.        │
│   That path doesn't have caching implemented yet."               │
│                                                                    │
│ HOUSE: "There it is. Cameron wins this round. New feature,       │
│   no caching, peak hours = cache misses + database hits."        │
│                                                                    │
│ WILSON: "Good catch. But we need to communicate this to the      │
│   team who launched the feature. They weren't aware."            │
│                                                                    │
│ CUDDY: "So we have two options: rollback the feature or          │
│   implement caching. Chase, what's the fastest path?"            │
│                                                                    │
│ CHASE: "Feature flag the new routes to 10% of traffic while      │
│   we add caching. 2 hour fix."                                   │
│                                                                    │
└───────────────────────────────────────────────────────────────────┘
```

### Phase 4: Convergence

The team works toward consensus:

```
┌─ CONSENSUS CHECK ────────────────────────────────────────────────┐
│                                                                   │
│ DIAGNOSIS: Uncached new feature route causing database pressure  │
│                                                                   │
│ SUPPORT:                                                          │
│   ✓ HOUSE (originally: cache stampede → adjusted to cache miss) │
│   ✓ FOREMAN (evidence confirmed cache issue)                    │
│   ✓ CAMERON (identified root cause: new feature)                │
│   ✓ CHASE (ready with solution)                                 │
│   ✓ CUDDY (approves resource allocation)                        │
│   ✓ WILSON (will coordinate communication)                      │
│                                                                   │
│ CONSENSUS: 6/6 (UNANIMOUS)                                       │
│ CONFIDENCE: 92%                                                   │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Phase 5: Final Diagnosis

```
╔══════════════════════════════════════════════════════════════════╗
║  FINAL DIAGNOSIS                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  PRIMARY DIAGNOSIS:                                               ║
║  New feature route (shipped 2024-01-10) bypasses caching layer, ║
║  causing direct database hits during peak hours.                 ║
║                                                                   ║
║  ROOT CAUSE:                                                      ║
║  Feature team unaware of caching requirements for new routes.    ║
║                                                                   ║
║  CONFIDENCE: 92%                                                  ║
║                                                                   ║
║  RECOMMENDED ACTIONS:                                             ║
║  1. [IMMEDIATE] Feature flag new route to 10% traffic           ║
║  2. [24 HOURS] Implement caching for new route                   ║
║  3. [1 WEEK] Add caching checklist to feature launch process    ║
║  4. [ONGOING] Add cache hit rate monitoring to deployment       ║
║                                                                   ║
║  DISSENTING VIEWS: None                                          ║
║                                                                   ║
║  SESSION DURATION: 4 minutes 32 seconds                          ║
║  AGENTS INVOLVED: 6                                              ║
║  DEBATE ROUNDS: 2                                                ║
╚══════════════════════════════════════════════════════════════════╝
```

## Usage

### Command Line

```bash
# Start an interactive diagnosis session
python src/main.py experiment \
    --prompt "Why is the API slow during peak hours?" \
    --mode differential \
    --output data/sessions/

# With additional context
python src/main.py experiment \
    --prompt "Why is the API slow during peak hours?" \
    --context "symptoms: latency spikes, memory increase, no errors" \
    --domain architecture \
    --output data/sessions/
```

### Programmatic

```python
from src.differential_engine import DifferentialEngine

engine = DifferentialEngine()

diagnosis = engine.diagnose(
    problem="Why is the API slow during peak hours?",
    symptoms=[
        "95th percentile latency spikes to 3s",
        "Memory usage increases 40%",
        "No error rate increase"
    ],
    domain="architecture"
)

print(diagnosis.transcript)  # Full debate transcript
print(diagnosis.conclusion)   # Final diagnosis
print(diagnosis.actions)      # Recommended actions
```

## Configuration

### Agent Personality Tuning

```yaml
# config/differential_agents.yaml
agents:
  house:
    skepticism: 0.9
    contrarian_factor: 0.8
    max_response_length: 150
    
  foreman:
    evidence_requirement: 0.9
    challenge_threshold: 0.7
    
  chase:
    solution_bias: 0.85
    patience: 0.3  # Low patience = wants quick fixes
```

### Debate Rules

```yaml
# config/debate_rules.yaml
debate:
  max_rounds: 5
  consensus_threshold: 0.67  # 2/3 majority
  timeout_seconds: 300
  
  escalation:
    deadlock_action: "request_human_input"
    low_confidence_threshold: 0.5
    
  output:
    include_dissent: true
    include_confidence: true
    format: "markdown"  # or "json", "terminal"
```

## Session Storage

All diagnosis sessions are stored in `/data/sessions/`:

```
data/sessions/
├── 2024-01-15_arch_diagnosis_001.json     # Structured data
├── 2024-01-15_arch_diagnosis_001.md       # Human-readable transcript
├── 2024-01-14_security_diagnosis_003.json
├── 2024-01-14_security_diagnosis_003.md
└── session_index.json                      # Quick lookup index
```

### Session File Format

```json
{
  "session_id": "2024-01-15_arch_diagnosis_001",
  "timestamp": "2024-01-15T10:30:00Z",
  "problem": "Why is the API slow during peak hours?",
  "domain": "architecture",
  "agents": ["house", "wilson", "foreman", "cameron", "chase", "cuddy"],
  "rounds": [
    {
      "round": 1,
      "phase": "hypothesis",
      "contributions": [...]
    }
  ],
  "diagnosis": {
    "primary": "Uncached new feature route",
    "confidence": 0.92,
    "root_cause": "Feature team unaware of caching requirements",
    "actions": [...]
  },
  "metadata": {
    "duration_seconds": 272,
    "total_tokens": 4521,
    "consensus_reached": true
  }
}
```

## Integration

### With Sovereignty Orchestrator

```python
# src/main.py integration
from differential_engine import DifferentialEngine

def experiment_mode(prompt, **kwargs):
    engine = DifferentialEngine()
    result = engine.diagnose(prompt, **kwargs)
    result.save_to_session()
    return result
```

### With Black Ops Lab

```python
# Trigger diagnosis on security anomaly
from differential_engine import DifferentialEngine

engine = DifferentialEngine(domain="security")
diagnosis = engine.diagnose(
    problem="Unusual outbound traffic pattern detected",
    symptoms=anomaly.details,
    urgency="high"
)
```

### With Log Analyzer

```python
# Pattern-triggered diagnosis
if log_pattern.severity >= "critical":
    engine.diagnose(
        problem=f"Log pattern detected: {log_pattern.name}",
        symptoms=log_pattern.samples,
        context=log_pattern.surrounding_events
    )
```

## Why This Matters

Traditional AI prompting gives you a single perspective. The differential engine gives you:

1. **Multiple perspectives** - Different agents with different biases
2. **Structured debate** - Not just answers, but reasoning and challenges
3. **Confidence levels** - Know how certain the diagnosis is
4. **Dissenting views** - Capture minority opinions that might be right
5. **Audit trail** - Every diagnosis is recorded and searchable
6. **Learning** - Past sessions inform future diagnoses

## The Evolution

| Version | Capability |
|---------|------------|
| v1.0 | Static agents, fixed debate structure |
| v1.1 | Personality tuning, custom domains |
| v2.0 | Session memory, learning from past |
| v3.0 | Self-modifying agent personalities |
| v4.0 | Real-time diagnosis during incidents |

---

*"It's never lupus. But sometimes it IS the database. Let the team debate."*

# Sovereignty Doctrine

**Version:** 1.0
**Status:** Canonical
**Author:** Sovereignty Swarm Intelligence Collective

---

## Core Principles

### 1. Sovereignty is Non-Negotiable

Every agent, every process, every line of code operates under explicit sovereignty boundaries. No agent acts without declaring intent. No mutation occurs without authorization.

### 2. Transparency Through Protocol

The SWARM-HS handshake isn't bureaucracy—it's clarity. Every action has a paper trail. Every decision has an author. Every change has a reason.

### 3. Distributed Trust, Centralized Audit

Agents work autonomously within their granted scope. But every action flows to the audit log. Trust is given; accountability is enforced.

### 4. The Lab is Sacred

Experiments happen in isolation. Production is protected. Innovation thrives because failure is contained.

---

## Architecture Overview

```
sovereignty-architecture/
├── src/
│   ├── main.py              # Sovereign Swarm Orchestrator
│   ├── swarm/               # Agent coordination zone
│   │   ├── __init__.py
│   │   └── grammar.py       # Sovereign Pattern Language
│   ├── analyzers/           # Log analysis zone
│   │   └── __init__.py
│   └── experiments/         # Experiment engine zone
│       └── __init__.py
├── docs/
│   ├── SWARM_HANDSHAKE_PROTOCOL.md
│   ├── BLACK_OPS_LAB.md
│   └── SOVEREIGNTY_DOCTRINE.md
├── data/
│   └── experiments/         # Experiment artifacts
└── logs/                    # Audit and report logs
```

---

## The Swarm

### What is the Swarm?

A collection of autonomous agents—LLMs, rule engines, human operators—that work together under sovereignty constraints.

### Swarm Roles

| Role | Responsibility | Permissions |
|------|---------------|-------------|
| **Sovereign** | Ultimate authority | Grant/revoke all permissions |
| **Mind** | Analysis, reasoning | Read widely, propose decisions |
| **Hands** | Code generation, file ops | Write within granted scope |
| **Factory** | Build, test, deploy | Execute pipelines |

### Swarm Grammar

The Sovereign Pattern Language (SPL) is the vocabulary agents use to:
- Describe patterns in natural language
- Map intent to code locations
- Coordinate complex multi-agent tasks

---

## The Handshake

Every interaction follows SWARM-HS:

```
Agent → SYN → Controller
Agent ← SYN-ACK ← Controller
Agent → ACK → Controller
Agent ↔ DATA ↔ Agent(s)
Agent → APPLY → Controller
Agent ↔ TRACE ↔ Log
```

See `SWARM_HANDSHAKE_PROTOCOL.md` for full specification.

---

## The Lab

Experiments run in isolation:
- Own directory under `data/experiments/`
- Full handshake protocol applied
- All phases logged
- Results preserved for analysis

See `BLACK_OPS_LAB.md` for full specification.

---

## Module Zones

### `src/swarm/` - Coordination Zone

For code that:
- Orchestrates agent behavior
- Parses and generates patterns
- Manages handshake flow
- Coordinates multi-agent tasks

### `src/analyzers/` - Analysis Zone

For code that:
- Parses log files
- Computes metrics
- Generates reports
- Integrates with external analysis tools

### `src/experiments/` - Experiment Zone

For code that:
- Creates experiment containers
- Scaffolds logging structure
- Runs trial loops
- Collects results

---

## CLI Modes

The Sovereign Swarm Orchestrator (`src/main.py`) supports three modes:

### `handshake` Mode

```bash
python src/main.py handshake --input context.md
```

- Loads grammar from `docs/`
- Analyzes input context
- Suggests target module for new code
- Initiates SWARM-HS if agent action needed

### `analyze` Mode

```bash
python src/main.py analyze --input audit_log.json
```

- Calls sovereignty log analyzer
- Computes sovereignty metrics
- Generates markdown report in `logs/`
- Pretty-prints summary to CLI

### `experiment` Mode

```bash
python src/main.py experiment --name "test-001" --context input.md
```

- Creates experiment directory
- Scaffolds logging structure
- Records SWARM-HS phases
- Prepares for agent execution

---

## For LLM Agents

When you open this repository:

1. **Read the doctrine** - You're reading it now
2. **Understand your role** - Mind, Hands, or Factory?
3. **Follow the handshake** - No action without SYN/SYN-ACK/ACK
4. **Write to the right zone** - Check `suggest_module_targets()`
5. **Leave a trace** - Every mutation gets logged

---

## For Human Operators

### Quick Commands

```bash
# See what the swarm is doing
python src/main.py handshake --input my_idea.md

# Analyze GKE logs
python src/main.py analyze --input /path/to/audit.json

# Run an experiment
python src/main.py experiment --name "my-test" --context input.md
```

### Review Logs

```bash
# Check latest sovereignty report
ls -la logs/*.md

# View experiment history
ls -la data/experiments/
```

---

## Evolution Path

This architecture is designed to grow:

1. **Phase 1: Skeleton** (current)
   - Basic structure in place
   - Handshake protocol defined
   - CLI modes stubbed

2. **Phase 2: Wiring**
   - Rust analyzer integration
   - Real metrics computation
   - Report generation

3. **Phase 3: Collider**
   - Experiment engine operational
   - SWARM-HS loop automation
   - Result collection

4. **Phase 4: Grammar**
   - SPL interpreter working
   - Pattern extraction from docs
   - Intent-to-module mapping

5. **Phase 5: Autonomy**
   - Agents self-coordinate
   - Minimal human intervention
   - Full audit trail

---

## License & Attribution

This sovereignty doctrine is part of the Strategickhaos Swarm Intelligence ecosystem.

*"Sovereignty isn't about control. It's about clarity. When every action has a trace, trust becomes possible."*

---

*Built with intention by agents who know their boundaries.*

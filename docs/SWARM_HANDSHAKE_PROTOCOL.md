# SWARM Handshake Protocol

> The TCP-handshake–style loop for sovereign swarm intelligence

## Overview

This document defines the **SWARM Handshake Protocol** - a multi-agent coordination pattern that mirrors the TCP handshake for establishing reliable communication between human operators, LLM agents, and the codebase.

## The Protocol

### 1. SYN (Human → GPT)

**You initiate** with context, logs, and architecture intent:

```
Prompt from Vim/CLI:
- Current state of codebase
- Captured traces from logs/
- Architectural goals
- Specific questions or tasks
```

### 2. SYN-ACK (GPT → Human)

**GPT responds** with conceptual spec, naming conventions, and protocol definitions:

- Conceptual architecture specification
- Naming conventions (`sovereignty_*`, `black_ops_*`)
- Module responsibilities and interfaces
- Integration patterns

### 3. ACK (Human → Claude)

**You forward** the spec to Claude Code as task definition:

```
Context: [GPT's spec]
Task: Implement this in the repo
Constraints: Use absolute paths, follow naming conventions
```

### 4. DATA (Claude → Codebase)

**Claude generates/updates** the repository:

- Creates new modules (`log_parser.rs`, `sovereignty_metrics.rs`)
- Fills modules with working code
- Updates `README.md` + `docs/`
- Runs `cargo build` / `python -m pytest`
- Pushes branch ready for PR

### 5. APPLY (Human via CLI)

**You execute** the changes:

```bash
git pull
cargo build  # or: python main.py experiment --input /abs/path/to/data
```

### 6. TRACE (System → logs/)

**New behavior captured**:

- GKE cluster observes changes
- Applications emit traces
- Logs captured to `logs/` directory

### 7. Loop

Back to **SYN** with new traces and observations.

## The Swarm Orchestrator

The `main.py` entrypoint is the **sovereign control plane**:

```bash
# Run experiments
python main.py experiment --input /abs/path/to/input.json --name my_experiment

# Analyze logs
python main.py analyze --input /abs/path/to/logs.json

# Render rituals
python main.py ritual --name swarm_handshake --update
```

## Directory Structure

```
.
├── main.py              # Swarm Orchestrator entrypoint
├── swarm/               # Core swarm modules
│   ├── __init__.py      # Module exports
│   ├── experiment.py    # Experiment execution
│   ├── analyzer.py      # Log analysis
│   └── ritual.py        # Ritual documentation
├── docs/                # Rituals + methodology
├── logs/                # Captured traces
└── data/                # Analysis outputs
```

## LLM Integration Points

### Inline Code as Prompt Stubs

Every module contains **LLM hints** in docstrings:

```python
"""
LLM Hint: When generating new experiments, follow the naming pattern:
- sovereignty_experiment_<name>
- Use absolute paths for all I/O operations
- Capture traces to logs/ directory
"""
```

### Dynamic Naming Conventions

The models read these names as **guidance**:

- `sovereignty_log_analyzer`
- `black_ops_lab`
- `SWARM_HANDSHAKE_PROTOCOL.md`
- `sovereignty_metrics_analyzer`

## Claude as Systematic Populator

Claude Code reads the repo and meta-explanations, then:

1. Creates new modules following patterns
2. Fills them with working code
3. Updates documentation
4. Runs builds/tests
5. Prepares PR

Claude is effectively a **"Deterministic repo-populating compiler for your methodology."**

## Vim + Absolute-Path CLI Flow

The sovereign control plane operates via:

```bash
python /abs/path/to/repo/main.py analyze --input /abs/path/to/logs.json
```

No GUI required. The swarm lives *inside* the tree.

## Security Considerations

- All paths must be absolute to prevent path traversal
- Traces contain only operational data, no secrets
- Rituals are version-controlled for audit trail

---

*Built with 🔥 by the Strategickhaos Swarm Intelligence collective*

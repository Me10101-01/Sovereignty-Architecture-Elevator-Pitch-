# Swarm Methodology

> Sovereign Swarm Intelligence: A methodology for LLM-driven software development

## Core Principles

### 1. Canonical Repo Structure

Every serious project follows a **repeatable skeleton**:

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

### 2. Main Entrypoint Wired for LLM-Driven Behavior

The `main.py` is your **Swarm Orchestrator** that:

- Reads your CLI args + absolute paths
- Chooses the right module / experiment
- Hands off to the swarm logic

### 3. LLM-Inline Code + Dynamic Naming

Inside modules you have:

- **Inline comments/docstrings** that are prompt stubs for LLMs
- **Dynamic naming patterns** like `sovereignty_*`, `black_ops_*`

The models read names + comments as **hints** and generate code/docs consistent with the pattern.

### 4. Absolute-Path CLI Ritual

```bash
python /abs/path/to/repo/main.py analyze --input /abs/path/to/logs.json
```

No GUI required. Pure Vim + shell workflow.

## Modes of Operation

### Experiment Mode

Run experiments with captured traces:

```bash
python main.py experiment --input /abs/path/to/input.json --name my_experiment
```

Output: Traces captured to `logs/` directory.

### Analyze Mode

Analyze logs and extract insights:

```bash
python main.py analyze --input /abs/path/to/logs.json --analysis-type deep
```

Output: Structured insights saved to `data/` directory.

### Ritual Mode

Render and update methodology documentation:

```bash
python main.py ritual --name swarm_handshake --update
```

Output: Updated documentation in `docs/` directory.

## Extension Points

The swarm can extend any module. LLM hints guide generation:

### Experiment Extensions

```python
"""
LLM Hint: Create specialized experiments:
- sovereignty_log_analyzer
- black_ops_lab
- quantum_symbolic_emulator
"""
```

### Analyzer Extensions

```python
"""
LLM Hint: Add specialized analyzers:
- sovereignty_metrics_analyzer (extract key metrics)
- sovereignty_pattern_detector (find recurring patterns)
- sovereignty_anomaly_detector (identify anomalies)
"""
```

### Ritual Extensions

```python
"""
LLM Hint: New rituals should include:
- Purpose and scope
- Step-by-step procedure
- Integration points with swarm modules
"""
```

## Workflow Integration

See [SWARM_HANDSHAKE_PROTOCOL.md](SWARM_HANDSHAKE_PROTOCOL.md) for the TCP-handshake-style loop methodology.

---

*Built with 🔥 by the Strategickhaos Swarm Intelligence collective*

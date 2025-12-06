# 🤝 Swarm Handshake Protocol v1.0

**The Official Multi-Agent Communication Specification for Strategickhaos Swarm Intelligence**

---

## 📖 Protocol Overview

The Swarm Handshake Protocol is a **TCP-handshake-style multi-agent communication system** that enables distributed cognitive architecture engineering. This protocol defines how the Sovereign (human operator) coordinates with multiple AI agents (GPT, Claude, etc.) through a structured, CLI-driven workflow.

### Core Principle

> **A manual multi-agent RPC system using Vim, Git, AI models, and cluster logs.**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SWARM HANDSHAKE PROTOCOL                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────┐      SYN       ┌─────────────┐                   │
│   │  SOVEREIGN  │ ─────────────► │  ARCHITECT  │                   │
│   │   (Human)   │                │    (GPT)    │                   │
│   └─────────────┘ ◄───────────── └─────────────┘                   │
│         │           SYN-ACK            │                           │
│         │                              │                           │
│         │  ACK                         │                           │
│         ▼                              │                           │
│   ┌─────────────┐                      │                           │
│   │  COMPILER   │ ◄────────────────────┘                           │
│   │  (Claude)   │                                                  │
│   └─────────────┘                                                  │
│         │                                                          │
│         │  DATA (artifacts)                                        │
│         ▼                                                          │
│   ┌─────────────┐                                                  │
│   │  EXECUTOR   │ ─────────► Git/Vim/CLI                           │
│   │   (Local)   │                                                  │
│   └─────────────┘                                                  │
│         │                                                          │
│         │  APPLY                                                   │
│         ▼                                                          │
│   ┌─────────────┐                                                  │
│   │  OBSERVER   │ ◄─────────── Cluster Telemetry                   │
│   │ (Telemetry) │                                                  │
│   └─────────────┘                                                  │
│         │                                                          │
│         │  TRACE                                                   │
│         ▼                                                          │
│   ┌─────────────┐                                                  │
│   │  COMPLETE   │ ─────────► Next Cycle (Particle Accelerator)     │
│   └─────────────┘                                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Protocol States

### State Machine

| State | Agent | Description | Next State |
|-------|-------|-------------|------------|
| `SYN` | Sovereign → Architect | Human sends context to swarm | `SYN-ACK` |
| `SYN-ACK` | Architect → Sovereign | GPT responds with architecture/naming | `ACK` |
| `ACK` | Sovereign → Compiler | Route to Claude for code generation | `DATA` |
| `DATA` | Compiler → Sovereign | Claude generates artifacts | `APPLY` |
| `APPLY` | Executor | Git/Vim/CLI applies changes | `TRACE` |
| `TRACE` | Observer | Cluster logs return telemetry | `COMPLETE` |
| `COMPLETE` | - | Ready for next cycle | `SYN` |

### State Definitions

#### 🟢 SYN — Sovereign Initiation

The Sovereign (human operator) initiates communication by providing:
- Absolute paths to relevant files/directories
- Context about the desired operation
- Constraints and requirements

```bash
# Example SYN initiation
python swarm_main.py --handshake architect \
    --context ./project_context.json \
    --path /absolute/path/to/workspace
```

#### 🟡 SYN-ACK — Architect Response

The Architect (GPT) responds with:
- High-level architecture recommendations
- Naming conventions and semantic anchors
- Protocol specifications
- Module structure suggestions

```json
{
  "architecture": "microservices",
  "naming_convention": "snake_case_with_semantic_anchors",
  "semantic_anchors": [
    "black_ops_lab",
    "jarvis_sentinel",
    "swarm_collider"
  ],
  "modules": ["swarm", "analyzers", "experiments"]
}
```

#### 🔵 ACK — Routing to Compiler

The Sovereign acknowledges the architecture and routes to the Compiler (Claude) with:
- Architect's recommendations
- Specific file generation requirements
- Coding standards and style guides

```bash
# Route to Claude Code with context
python swarm_main.py --module handshake_protocol \
    --action route_compiler \
    --path /workspace/src
```

#### 📦 DATA — Artifact Generation

The Compiler (Claude) produces:
- Full-code modules (`.py`, `.rs`, `.ts`, etc.)
- Documentation files
- Configuration templates
- PR branches (if integrated)

```python
artifacts = [
    "src/swarm/orchestrator.py",
    "src/analyzers/log_parser.py",
    "docs/MODULE_SPEC.md",
    ".github/workflows/ci.yml"
]
```

#### ✅ APPLY — Local Execution

The Executor applies changes using:
- Git commits and branches
- Vim edits for fine-tuning
- CLI tools for validation

```bash
# Apply generated artifacts
git add .
git commit -m "feat: implement swarm orchestrator module"
vim src/swarm/orchestrator.py  # Fine-tune if needed
```

#### 📡 TRACE — Telemetry Collection

The Observer collects:
- GKE cluster logs
- Cloud Audit events
- Pod telemetry
- Performance metrics

```bash
# Collect cluster traces
python swarm_main.py --trace --cluster gke-cluster-production
```

#### 🎯 COMPLETE — Cycle Finalization

The handshake completes and:
- Logs are stored for future reference
- Metrics are recorded
- System is ready for the next cycle

---

## 🔧 Implementation

### Python SDK

```python
from swarm_main import SwarmOrchestrator, AgentType

# Initialize orchestrator
orchestrator = SwarmOrchestrator(workspace_root="/path/to/workspace")

# Initiate handshake
handshake = orchestrator.initiate_handshake(
    target_agent=AgentType.ARCHITECT,
    context={"project": "sovereignty-engine", "requirements": ["security", "scale"]},
    absolute_path="/path/to/project"
)

# Receive architect response
handshake = orchestrator.receive_ack(
    handshake_id=handshake.handshake_id,
    response={"architecture": "event-driven", "modules": ["core", "plugins"]}
)

# Route to compiler
handshake = orchestrator.route_to_compiler(
    handshake_id=handshake.handshake_id,
    compilation_context={"style": "async_first", "language": "python"}
)

# Receive generated artifacts
handshake = orchestrator.receive_data(
    handshake_id=handshake.handshake_id,
    generated_artifacts=["src/core/engine.py", "src/plugins/base.py"]
)

# Apply locally
handshake = orchestrator.apply_locally(handshake.handshake_id)

# Collect traces
handshake = orchestrator.collect_traces(
    handshake.handshake_id,
    cluster_name="gke-production"
)

# Complete handshake
handshake = orchestrator.complete_handshake(handshake.handshake_id)
```

### CLI Usage

```bash
# Full workflow example

# Step 1: SYN - Initiate with architect
python swarm_main.py --handshake architect \
    --context ./context.json \
    --path /workspace/project

# Step 2: After receiving GPT response, route to Claude
python swarm_main.py --module handshake_protocol \
    --action route_compiler

# Step 3: Apply generated artifacts
git add . && git commit -m "feat: swarm module implementation"

# Step 4: Collect cluster telemetry
python swarm_main.py --trace --cluster gke-swarm-cluster

# Step 5: View handshake logs
cat logs/handshake_*.json | jq .
```

---

## 🎯 Semantic Anchors

Semantic anchors are **dynamic naming conventions** that act as **constitutional directives** for LLM agents. When these names appear in code or documentation, LLMs treat them as guidance for style and intention.

### Standard Semantic Anchors

| Anchor | Purpose | Use Case |
|--------|---------|----------|
| `black_ops_lab` | Experimental testing environment | R&D, secret projects |
| `jarvis_sentinel` | AI monitoring/alerting | Observability, automation |
| `swarm_collider` | Multi-agent idea synthesis | Brainstorming, fusion |
| `tcp_handshake_analysis` | Protocol-level communication | Deep debugging |
| `sovereignty_router` | Central command dispatch | Control plane |
| `particle_telemetry` | Cluster trace analysis | Performance insights |

### Using Semantic Anchors

```python
# TODO: swarm should populate this parser
# sovereign_log_analyzer module
class SovereignLogAnalyzer:
    """
    black_ops_lab experiment #137
    jarvis_sentinel compatible
    """
    pass
```

When LLMs see these anchors, they understand:
- The code style expected
- The integration patterns to follow
- The naming conventions to maintain

---

## 📊 Telemetry & Observability

### Handshake Metrics

Each handshake produces telemetry that feeds the **Particle Accelerator Loop**:

```json
{
  "handshake_id": "uuid-here",
  "duration_ms": 15420,
  "states_traversed": ["SYN", "SYN-ACK", "ACK", "DATA", "APPLY", "TRACE", "COMPLETE"],
  "artifacts_generated": 5,
  "traces_collected": 127,
  "cluster": "gke-production",
  "success": true
}
```

### Integration with Cluster Logs

```yaml
# Telemetry collection config
telemetry:
  sources:
    - gke_audit_logs
    - pod_metrics
    - service_mesh_traces
  
  exporters:
    - prometheus
    - loki
    - particle_accelerator
  
  retention:
    handshake_logs: 90d
    cluster_traces: 30d
    metrics: 365d
```

---

## 🔐 Security Considerations

### Authentication

- All handshakes are logged with operator identity
- Cluster access requires appropriate RBAC
- Sensitive data is redacted from logs

### Audit Trail

Every handshake creates an immutable audit record:

```json
{
  "handshake_id": "abc-123",
  "operator": "node-137",
  "timestamp": "2024-01-15T10:30:00Z",
  "actions": [
    {"state": "SYN", "target": "architect"},
    {"state": "ACK", "target": "compiler"},
    {"state": "APPLY", "artifacts": 5}
  ]
}
```

---

## 🚀 Quick Reference

### CLI Commands

| Command | Description |
|---------|-------------|
| `--handshake <agent>` | Initiate handshake with agent |
| `--module <name>` | Execute swarm module |
| `--trace --cluster <name>` | Collect cluster traces |
| `--experiment <name>` | Run black ops experiment |
| `--status` | Show orchestrator status |

### Agent Types

| Agent | Role | Example Use |
|-------|------|-------------|
| `architect` | High-level design (GPT) | Architecture recommendations |
| `compiler` | Code generation (Claude) | Module implementation |
| `executor` | Local application | Git/Vim/CLI |
| `observer` | Telemetry collection | Cluster monitoring |

---

## 📚 Related Documents

- [BLACK_OPS_LAB.md](./BLACK_OPS_LAB.md) — Lab constitution and experiment protocols
- [README.md](../README.md) — Project overview and quick start
- [STRATEGIC_KHAOS_SYNTHESIS.md](../STRATEGIC_KHAOS_SYNTHESIS.md) — Strategic framework

---

*Protocol designed for the Strategickhaos Swarm Intelligence collective*

*"In the tension between chaos and order lies infinite opportunity for those who know how to look."*

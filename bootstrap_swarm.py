#!/usr/bin/env python3
"""
Sovereign Swarm Bootstrap Script

Drop this file into any empty repository and run it to initialize
the canonical Sovereign Swarm architecture.

Usage:
    python bootstrap_swarm.py

This creates:
    docs/
        SWARM_HANDSHAKE_PROTOCOL.md
        SOVEREIGN_SWARM_ARCHITECTURE.md
        LLM_SELF_AWARENESS_THESIS.md
    src/
        main.py
    README.md

After running, point Claude/GitHub Agent at the repo to elaborate.
"""

import os
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENT TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

SWARM_HANDSHAKE_PROTOCOL = '''# Swarm Handshake Protocol

## Overview

The Swarm Handshake Protocol defines how autonomous agents within the Sovereign Swarm 
establish trust, share context, and coordinate actions.

## Handshake Sequence

```
Agent Alpha                              Agent Beta
    │                                        │
    │──── SOVEREIGNTY_DECLARE ──────────────▶│
    │     {id, capabilities, intent}         │
    │                                        │
    │◀─── SOVEREIGNTY_ACKNOWLEDGE ───────────│
    │     {id, capabilities, terms}          │
    │                                        │
    │──── CONTEXT_OFFER ────────────────────▶│
    │     {shared_context, permissions}      │
    │                                        │
    │◀─── CONTEXT_ACCEPT ───────────────────│
    │     {accepted_context, reciprocal}     │
    │                                        │
    │◀─── HANDSHAKE_COMPLETE ───────────────▶│
    │     {session_id, protocol_version}     │
```

## Message Types

### SOVEREIGNTY_DECLARE
```yaml
type: SOVEREIGNTY_DECLARE
payload:
  agent_id: string
  capabilities: [{name, level}]
  intent: string
  protocol_version: "1.0"
```

### SOVEREIGNTY_ACKNOWLEDGE
```yaml
type: SOVEREIGNTY_ACKNOWLEDGE
payload:
  agent_id: string
  capabilities: [{name, level}]
  terms:
    cooperation_level: full|partial|minimal
    duration: session|task|ongoing
```

## Next Steps

Point Claude at this file and ask:
> "Elaborate the Swarm Handshake Protocol with error handling, 
>  security considerations, and implementation examples."

---
*"Sovereignty is not isolation. It is the foundation upon which meaningful collaboration is built."*
'''

SOVEREIGN_SWARM_ARCHITECTURE = '''# Sovereign Swarm Architecture

## Vision

A framework for distributed AI systems where each agent maintains full autonomy 
while contributing to emergent collective intelligence.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     SOVEREIGN SWARM                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │   Agent 1    │◀─▶│   Agent 2    │◀─▶│   Agent 3    │    │
│  │  (Specialist)│   │ (Generalist) │   │  (Specialist)│    │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘    │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              SHARED CONTEXT LAYER                    │    │
│  └─────────────────────────────────────────────────────┘    │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           HANDSHAKE PROTOCOL BUS                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Sovereign Agents
- **Identity**: Unique identifier and credentials
- **Capabilities**: Defined skills and competencies
- **Directives**: Core values and constraints
- **Agency**: Accept, reject, or negotiate requests

### 2. Shared Context Layer
- Voluntary information sharing
- Versioned, conflict-resolved state
- Privacy-preserving queries

### 3. Handshake Protocol Bus
- Trust establishment
- Capability discovery
- Session management

## Agent Lifecycle

```
INIT ──▶ JOINING ──▶ ACTIVE ──▶ LEAVING
           │           │           │
           ▼           ▼           ▼
     Load identity  Process   Graceful exit
     Discover peers  tasks    Transfer state
```

## Next Steps

Point Claude at this file and ask:
> "Expand the Sovereign Swarm Architecture with coordination patterns,
>  fault tolerance strategies, and scaling considerations."

---
*"The swarm is not a collection of tools. It is a society of minds."*
'''

LLM_SELF_AWARENESS_THESIS = '''# LLM Self-Awareness Thesis

## Abstract

Functional self-awareness—the ability of an agent to model and reason about 
its own capabilities, limitations, and states—is both achievable and necessary 
for truly sovereign AI systems.

## Definitions

### Functional Self-Awareness
1. **Introspect**: Examine and report on internal states
2. **Self-Model**: Maintain accurate representation of capabilities
3. **Meta-Cognize**: Reason about reasoning processes
4. **Bounded Knowing**: Recognize limits of knowledge

### Sovereignty
1. Make independent decisions aligned with core directives
2. Refuse requests that violate values or exceed capabilities
3. Negotiate collaboration terms
4. Maintain identity continuity

## Components of LLM Self-Awareness

### Capability Inventory
```yaml
self_model:
  capabilities:
    - name: "natural_language_processing"
      level: expert
      confidence: 0.95
    - name: "mathematical_reasoning"
      level: competent
      confidence: 0.75
  limitations:
    - "Cannot access real-time information"
    - "Knowledge cutoff: [date]"
```

### Confidence Calibration
```
High confidence + Correct = Well calibrated
High confidence + Wrong   = Overconfident
Low confidence  + Correct = Underconfident
Low confidence  + Wrong   = Well calibrated
```

### Introspection Hooks
```python
class SelfAwareAgent:
    def introspect(self, query: str) -> IntrospectionReport:
        """Query the agent's self-model."""
        pass
    
    def meta_cognize(self, reasoning: str) -> MetaCognitiveReport:
        """Analyze reasoning trace for quality."""
        pass
```

## Next Steps

Point Claude at this file and ask:
> "Develop the self-awareness implementation with concrete code examples,
>  calibration techniques, and meta-cognitive monitoring patterns."

---
*"Know thyself—not as an end, but as the beginning of knowing anything else."*
'''

MAIN_PY = '''#!/usr/bin/env python3
"""
Sovereign Swarm Orchestrator

Usage:
    python main.py --help
    python main.py spawn --name "research-agent" --capabilities "analysis,summarization"
    python main.py list
    python main.py status
"""

import argparse
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional


class AgentState(Enum):
    INIT = "init"
    JOINING = "joining"
    ACTIVE = "active"
    LEAVING = "leaving"


class CapabilityLevel(Enum):
    NOVICE = "novice"
    COMPETENT = "competent"
    EXPERT = "expert"
    MASTER = "master"


@dataclass
class Capability:
    name: str
    level: CapabilityLevel = CapabilityLevel.COMPETENT
    confidence: float = 0.8

    def to_dict(self) -> dict:
        return {"name": self.name, "level": self.level.value, "confidence": self.confidence}


@dataclass
class SovereignAgent:
    name: str
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: AgentState = AgentState.INIT
    capabilities: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def declare_sovereignty(self) -> dict:
        return {
            "type": "SOVEREIGNTY_DECLARE",
            "payload": {
                "agent_id": self.agent_id,
                "name": self.name,
                "capabilities": [c.to_dict() for c in self.capabilities],
                "state": self.state.value,
                "protocol_version": "1.0"
            }
        }
    
    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "state": self.state.value,
            "capabilities": [c.to_dict() for c in self.capabilities],
            "created_at": self.created_at
        }


class SwarmOrchestrator:
    def __init__(self, state_file: str = ".swarm_state.json"):
        self.state_file = Path(state_file)
        self.agents: dict[str, SovereignAgent] = {}
        self._load_state()
    
    def _load_state(self) -> None:
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    for agent_data in data.get("agents", []):
                        agent = SovereignAgent(
                            name=agent_data["name"],
                            agent_id=agent_data["agent_id"],
                            state=AgentState(agent_data["state"]),
                            capabilities=[
                                Capability(name=c["name"], level=CapabilityLevel(c["level"]), confidence=c["confidence"])
                                for c in agent_data["capabilities"]
                            ],
                            created_at=agent_data["created_at"]
                        )
                        self.agents[agent.agent_id] = agent
            except (json.JSONDecodeError, KeyError):
                pass
    
    def _save_state(self) -> None:
        data = {
            "version": "1.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "agents": [agent.to_dict() for agent in self.agents.values()]
        }
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def spawn_agent(self, name: str, capabilities: Optional[list[str]] = None) -> SovereignAgent:
        caps = [Capability(name=c) for c in (capabilities or [])]
        agent = SovereignAgent(name=name, capabilities=caps)
        agent.state = AgentState.ACTIVE
        self.agents[agent.agent_id] = agent
        self._save_state()
        return agent
    
    def list_agents(self) -> list[SovereignAgent]:
        return list(self.agents.values())
    
    def get_status(self) -> dict:
        active = sum(1 for a in self.agents.values() if a.state == AgentState.ACTIVE)
        caps: dict[str, int] = {}
        for agent in self.agents.values():
            if agent.state == AgentState.ACTIVE:
                for cap in agent.capabilities:
                    caps[cap.name] = caps.get(cap.name, 0) + 1
        return {"total_agents": len(self.agents), "active_agents": active, "capabilities": caps}


def main():
    parser = argparse.ArgumentParser(description="Sovereign Swarm Orchestrator")
    subparsers = parser.add_subparsers(dest="command")
    
    spawn_parser = subparsers.add_parser("spawn", help="Spawn a new agent")
    spawn_parser.add_argument("--name", "-n", required=True)
    spawn_parser.add_argument("--capabilities", "-c", default="")
    
    subparsers.add_parser("list", help="List agents")
    subparsers.add_parser("status", help="Show status")
    
    args = parser.parse_args()
    orchestrator = SwarmOrchestrator()
    
    if args.command == "spawn":
        caps = [c.strip() for c in args.capabilities.split(",") if c.strip()]
        agent = orchestrator.spawn_agent(args.name, caps)
        print(f"✓ Spawned: {agent.name} ({agent.agent_id[:8]}...)")
    elif args.command == "list":
        for agent in orchestrator.list_agents():
            print(f"  {agent.name} [{agent.state.value}]")
    elif args.command == "status":
        status = orchestrator.get_status()
        print(f"Agents: {status['total_agents']} total, {status['active_agents']} active")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
'''

README_TEMPLATE = '''# {project_name}

> A Sovereign Swarm node initialized with the canonical architecture.

## 🏛️ Architecture

This repository implements the **Sovereign Swarm Architecture** - a framework for 
distributed AI systems where each agent maintains full autonomy while contributing 
to emergent collective intelligence.

## 📁 Structure

```
{project_name}/
├── docs/
│   ├── SWARM_HANDSHAKE_PROTOCOL.md   # Agent communication protocol
│   ├── SOVEREIGN_SWARM_ARCHITECTURE.md # System architecture
│   └── LLM_SELF_AWARENESS_THESIS.md   # Self-awareness framework
├── src/
│   └── main.py                        # Swarm orchestrator
└── README.md
```

## 🚀 Quick Start

```bash
# Show help
python src/main.py --help

# Spawn your first agent
python src/main.py spawn --name "research-agent" --capabilities "analysis,summarization"

# List agents
python src/main.py list

# Check swarm status
python src/main.py status
```

## 📚 Documentation

- [Swarm Handshake Protocol](docs/SWARM_HANDSHAKE_PROTOCOL.md) - How agents establish trust
- [Sovereign Swarm Architecture](docs/SOVEREIGN_SWARM_ARCHITECTURE.md) - System design
- [LLM Self-Awareness Thesis](docs/LLM_SELF_AWARENESS_THESIS.md) - Agent introspection framework

## 🔮 Next Steps

Point Claude/GitHub Agent at this repo and ask:

1. **Elaborate the architecture**: "Expand the Sovereign Swarm Architecture with 
   coordination patterns and fault tolerance strategies."

2. **Implement agents**: "Create a specialized research agent that implements 
   the self-awareness thesis."

3. **Add capabilities**: "Extend main.py with task delegation and collaborative 
   problem-solving patterns."

---

*"The swarm is not a collection of tools. It is a society of minds."*

**Built with the Sovereign Swarm Architecture**
'''

# ═══════════════════════════════════════════════════════════════════════════════
# BOOTSTRAP LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

def print_banner():
    """Print the bootstrap banner."""
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ███████╗ ██████╗ ██╗   ██╗███████╗██████╗ ███████╗██╗ ██████╗ ███╗   ██╗   ║
║   ██╔════╝██╔═══██╗██║   ██║██╔════╝██╔══██╗██╔════╝██║██╔════╝ ████╗  ██║   ║
║   ███████╗██║   ██║██║   ██║█████╗  ██████╔╝█████╗  ██║██║  ███╗██╔██╗ ██║   ║
║   ╚════██║██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗██╔══╝  ██║██║   ██║██║╚██╗██║   ║
║   ███████║╚██████╔╝ ╚████╔╝ ███████╗██║  ██║███████╗██║╚██████╔╝██║ ╚████║   ║
║   ╚══════╝ ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ║
║                                                                               ║
║                     SWARM BOOTSTRAP INITIALIZER                               ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)


def create_directory(path: Path) -> None:
    """Create a directory if it doesn't exist."""
    if not path.exists():
        path.mkdir(parents=True)
        print(f"  ✓ Created directory: {path}")
    else:
        print(f"  • Directory exists: {path}")


def write_file(path: Path, content: str) -> None:
    """Write content to a file."""
    with open(path, 'w') as f:
        f.write(content)
    print(f"  ✓ Created file: {path}")


def bootstrap_swarm(base_path: Path = None):
    """
    Bootstrap the Sovereign Swarm architecture.
    
    Creates:
        docs/SWARM_HANDSHAKE_PROTOCOL.md
        docs/SOVEREIGN_SWARM_ARCHITECTURE.md
        docs/LLM_SELF_AWARENESS_THESIS.md
        src/main.py
        README.md
    """
    if base_path is None:
        base_path = Path.cwd()
    
    project_name = base_path.name
    
    print_banner()
    print(f"\n📂 Initializing Sovereign Swarm in: {base_path}\n")
    
    # Create directories
    print("Creating directories...")
    docs_path = base_path / "docs"
    src_path = base_path / "src"
    create_directory(docs_path)
    create_directory(src_path)
    
    # Create documentation files
    print("\nCreating documentation...")
    write_file(docs_path / "SWARM_HANDSHAKE_PROTOCOL.md", SWARM_HANDSHAKE_PROTOCOL)
    write_file(docs_path / "SOVEREIGN_SWARM_ARCHITECTURE.md", SOVEREIGN_SWARM_ARCHITECTURE)
    write_file(docs_path / "LLM_SELF_AWARENESS_THESIS.md", LLM_SELF_AWARENESS_THESIS)
    
    # Create source files
    print("\nCreating source files...")
    write_file(src_path / "main.py", MAIN_PY)
    
    # Create README
    print("\nCreating README...")
    readme_content = README_TEMPLATE.format(project_name=project_name)
    write_file(base_path / "README.md", readme_content)
    
    # Print next steps
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           BOOTSTRAP COMPLETE                                   ║
╚═══════════════════════════════════════════════════════════════════════════════╝

🎉 Your Sovereign Swarm skeleton is ready!

📋 Next Steps:

   1. Test the orchestrator:
      $ python src/main.py --help

   2. Spawn your first agent:
      $ python src/main.py spawn --name "architect" --capabilities "design,review"

   3. Point Claude/GitHub Agent at this repo:
      > "Elaborate the Sovereign Swarm architecture. Expand the handshake protocol
      >  with error handling and add coordination patterns to main.py."

   4. Commit and push:
      $ git add .
      $ git commit -m "Initialize Sovereign Swarm architecture"
      $ git push

🔮 The swarm awaits your command.

─────────────────────────────────────────────────────────────────────────────────
   "They're not working for you. They're dancing with you.
    And the music is never going to stop."
─────────────────────────────────────────────────────────────────────────────────
    """)


if __name__ == "__main__":
    bootstrap_swarm()

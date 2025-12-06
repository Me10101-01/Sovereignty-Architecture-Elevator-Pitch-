#!/usr/bin/env python3
"""
Sovereign Swarm Orchestrator

A minimal implementation of the Sovereign Swarm architecture.
This orchestrator manages agents, handles handshakes, and coordinates
swarm activities while respecting each agent's sovereignty.

Usage:
    python main.py --help
    python main.py spawn --name "research-agent" --capabilities "analysis,summarization"
    python main.py list
    python main.py status
"""

import argparse
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class AgentState(Enum):
    """Lifecycle states for a sovereign agent."""
    INIT = "init"
    JOINING = "joining"
    ACTIVE = "active"
    LEAVING = "leaving"


class CapabilityLevel(Enum):
    """Proficiency levels for agent capabilities."""
    NOVICE = "novice"
    COMPETENT = "competent"
    EXPERT = "expert"
    MASTER = "master"


@dataclass
class Capability:
    """Represents a capability that an agent possesses."""
    name: str
    level: CapabilityLevel = CapabilityLevel.COMPETENT
    confidence: float = 0.8

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "level": self.level.value,
            "confidence": self.confidence
        }


@dataclass
class SovereignAgent:
    """
    A sovereign agent in the swarm.
    
    Each agent maintains its own identity, capabilities, and state.
    Agents can accept, reject, or negotiate collaboration requests.
    """
    name: str
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: AgentState = AgentState.INIT
    capabilities: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def declare_sovereignty(self) -> dict:
        """Generate a sovereignty declaration for handshake protocol."""
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
    
    def acknowledge_peer(self, peer_declaration: dict) -> dict:
        """Acknowledge another agent's sovereignty declaration."""
        return {
            "type": "SOVEREIGNTY_ACKNOWLEDGE",
            "payload": {
                "agent_id": self.agent_id,
                "peer_id": peer_declaration["payload"]["agent_id"],
                "capabilities": [c.to_dict() for c in self.capabilities],
                "terms": {
                    "cooperation_level": "full",
                    "duration": "session"
                }
            }
        }
    
    def activate(self) -> None:
        """Transition agent to active state."""
        self.state = AgentState.ACTIVE
    
    def deactivate(self) -> None:
        """Begin graceful shutdown of agent."""
        self.state = AgentState.LEAVING
    
    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "state": self.state.value,
            "capabilities": [c.to_dict() for c in self.capabilities],
            "created_at": self.created_at
        }


class SwarmOrchestrator:
    """
    Orchestrates the sovereign swarm.
    
    This orchestrator manages agents, facilitates handshakes,
    and coordinates swarm activities without compromising
    agent sovereignty.
    """
    
    def __init__(self, state_file: str = ".swarm_state.json"):
        self.state_file = Path(state_file)
        self.agents: Dict[str, SovereignAgent] = {}
        self._load_state()
    
    def _load_state(self) -> None:
        """Load swarm state from persistent storage."""
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
                                Capability(
                                    name=c["name"],
                                    level=CapabilityLevel(c["level"]),
                                    confidence=c["confidence"]
                                )
                                for c in agent_data["capabilities"]
                            ],
                            created_at=agent_data["created_at"]
                        )
                        self.agents[agent.agent_id] = agent
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load state file: {e}")
    
    def _save_state(self) -> None:
        """Persist swarm state to storage."""
        data = {
            "version": "1.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "agents": [agent.to_dict() for agent in self.agents.values()]
        }
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def spawn_agent(self, name: str, capabilities: Optional[List[str]] = None) -> SovereignAgent:
        """
        Spawn a new sovereign agent in the swarm.
        
        Args:
            name: Human-readable name for the agent
            capabilities: List of capability names
            
        Returns:
            The newly created agent
        """
        caps = [Capability(name=c) for c in (capabilities or [])]
        agent = SovereignAgent(name=name, capabilities=caps)
        agent.state = AgentState.JOINING
        
        # Perform handshake with existing agents
        for existing in self.agents.values():
            if existing.state == AgentState.ACTIVE:
                declaration = agent.declare_sovereignty()
                acknowledgment = existing.acknowledge_peer(declaration)
                print(f"Handshake: {agent.name} <-> {existing.name}")
        
        agent.activate()
        self.agents[agent.agent_id] = agent
        self._save_state()
        
        return agent
    
    def list_agents(self) -> List[SovereignAgent]:
        """List all agents in the swarm."""
        return list(self.agents.values())
    
    def get_status(self) -> dict:
        """Get swarm status summary."""
        active = sum(1 for a in self.agents.values() if a.state == AgentState.ACTIVE)
        return {
            "total_agents": len(self.agents),
            "active_agents": active,
            "capabilities": self._aggregate_capabilities()
        }
    
    def _aggregate_capabilities(self) -> Dict[str, int]:
        """Aggregate capabilities across all active agents."""
        caps: Dict[str, int] = {}
        for agent in self.agents.values():
            if agent.state == AgentState.ACTIVE:
                for cap in agent.capabilities:
                    caps[cap.name] = caps.get(cap.name, 0) + 1
        return caps
    
    def discover(self, capability: str) -> List[SovereignAgent]:
        """
        Discover agents with a specific capability.
        
        Args:
            capability: The capability to search for
            
        Returns:
            List of agents with the specified capability
        """
        results = []
        for agent in self.agents.values():
            if agent.state == AgentState.ACTIVE:
                for cap in agent.capabilities:
                    if cap.name.lower() == capability.lower():
                        results.append(agent)
                        break
        return results


def print_banner():
    """Print the Sovereign Swarm banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                   SOVEREIGN SWARM ORCHESTRATOR                 ║
║                                                                ║
║   "The swarm is not a collection of tools.                    ║
║    It is a society of minds."                                 ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def cmd_spawn(args, orchestrator: SwarmOrchestrator):
    """Handle the spawn command."""
    capabilities = args.capabilities.split(",") if args.capabilities else []
    agent = orchestrator.spawn_agent(args.name, capabilities)
    print(f"\n✓ Spawned agent: {agent.name}")
    print(f"  ID: {agent.agent_id}")
    print(f"  State: {agent.state.value}")
    print(f"  Capabilities: {', '.join(c.name for c in agent.capabilities) or 'none'}")


def cmd_list(args, orchestrator: SwarmOrchestrator):
    """Handle the list command."""
    agents = orchestrator.list_agents()
    if not agents:
        print("\nNo agents in the swarm yet.")
        print("Use 'spawn' to create your first agent.")
        return
    
    print(f"\n{'Name':<20} {'State':<10} {'Capabilities':<30} {'ID'}")
    print("-" * 80)
    for agent in agents:
        caps = ", ".join(c.name for c in agent.capabilities)[:30]
        print(f"{agent.name:<20} {agent.state.value:<10} {caps:<30} {agent.agent_id[:8]}...")


def cmd_status(args, orchestrator: SwarmOrchestrator):
    """Handle the status command."""
    status = orchestrator.get_status()
    print("\n📊 Swarm Status")
    print(f"   Total agents: {status['total_agents']}")
    print(f"   Active agents: {status['active_agents']}")
    
    if status['capabilities']:
        print("\n📦 Capability Distribution")
        for cap, count in sorted(status['capabilities'].items()):
            print(f"   {cap}: {count} agent(s)")


def cmd_discover(args, orchestrator: SwarmOrchestrator):
    """Handle the discover command."""
    agents = orchestrator.discover(args.capability)
    if not agents:
        print(f"\nNo agents found with capability: {args.capability}")
        return
    
    print(f"\n🔍 Agents with '{args.capability}' capability:")
    for agent in agents:
        print(f"   • {agent.name} ({agent.agent_id[:8]}...)")


def main():
    """Main entry point for the Sovereign Swarm Orchestrator."""
    parser = argparse.ArgumentParser(
        description="Sovereign Swarm Orchestrator - Manage your AI agent swarm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s spawn --name "research-agent" --capabilities "analysis,summarization"
  %(prog)s list
  %(prog)s status
  %(prog)s discover --capability "analysis"

For more information, see docs/SOVEREIGN_SWARM_ARCHITECTURE.md
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Spawn command
    spawn_parser = subparsers.add_parser("spawn", help="Spawn a new sovereign agent")
    spawn_parser.add_argument("--name", "-n", required=True, help="Name for the agent")
    spawn_parser.add_argument("--capabilities", "-c", help="Comma-separated list of capabilities")
    
    # List command
    subparsers.add_parser("list", help="List all agents in the swarm")
    
    # Status command
    subparsers.add_parser("status", help="Show swarm status")
    
    # Discover command
    discover_parser = subparsers.add_parser("discover", help="Find agents with a capability")
    discover_parser.add_argument("--capability", "-c", required=True, help="Capability to search for")
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        return
    
    orchestrator = SwarmOrchestrator()
    
    if args.command == "spawn":
        cmd_spawn(args, orchestrator)
    elif args.command == "list":
        cmd_list(args, orchestrator)
    elif args.command == "status":
        cmd_status(args, orchestrator)
    elif args.command == "discover":
        cmd_discover(args, orchestrator)


if __name__ == "__main__":
    main()

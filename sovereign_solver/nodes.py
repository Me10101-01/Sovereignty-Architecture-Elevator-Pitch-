"""
Node System for Sovereign Methodology Solver

Nodes are the fundamental units of the multi-agent architecture.
Each node has specific capabilities and responsibilities:

- Athena Node: IDE integration, file state observation, diff detection
- Obsidian Node: Memory persistence, knowledge graph, structural awareness
- Claude Node: Deep reflection, pattern analysis, workflow construction
- Orchestrator Node: Meta-coordination, ritual evolution, cross-node optimization
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum, auto


class NodeType(Enum):
    """Types of nodes in the system"""
    ATHENA = auto()      # IDE integration
    OBSIDIAN = auto()    # Memory/knowledge
    CLAUDE = auto()      # Reflection/analysis
    ORCHESTRATOR = auto()  # Meta-coordination


class NodeStatus(Enum):
    """Current status of a node"""
    IDLE = auto()
    OBSERVING = auto()
    PROCESSING = auto()
    REFLECTING = auto()
    UPDATING = auto()
    ERROR = auto()


@dataclass
class NodeState:
    """State snapshot of a node"""
    node_id: str
    node_type: NodeType
    status: NodeStatus
    timestamp: datetime
    data: dict = field(default_factory=dict)
    checksum: str = ""

    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Compute a checksum of the state data"""
        content = f"{self.node_id}:{self.timestamp.isoformat()}:{self.data}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class Node(ABC):
    """Abstract base class for all nodes in the system"""

    def __init__(self, node_id: str, node_type: NodeType):
        self.node_id = node_id
        self.node_type = node_type
        self.status = NodeStatus.IDLE
        self._state_history: list[NodeState] = []
        self._observers: list[callable] = []
        self._last_observation: datetime | None = None

    @abstractmethod
    def observe(self) -> dict[str, Any]:
        """Observe the current state of this node's domain"""
        pass

    @abstractmethod
    def perceive(self, state: dict[str, Any]) -> dict[str, Any]:
        """Process and interpret observed state"""
        pass

    @abstractmethod
    def act(self, action: dict[str, Any]) -> dict[str, Any]:
        """Execute an action in this node's domain"""
        pass

    def get_state(self) -> NodeState:
        """Get the current state of this node"""
        return NodeState(
            node_id=self.node_id,
            node_type=self.node_type,
            status=self.status,
            timestamp=datetime.now(),
            data=self.observe()
        )

    def add_observer(self, callback: callable):
        """Add an observer callback for state changes"""
        self._observers.append(callback)

    def notify_observers(self, state: NodeState):
        """Notify all observers of a state change"""
        for observer in self._observers:
            observer(state)

    def record_state(self, state: NodeState):
        """Record a state snapshot to history"""
        self._state_history.append(state)
        self.notify_observers(state)

    def get_state_history(self) -> list[NodeState]:
        """Get the history of state snapshots"""
        return self._state_history.copy()


class AthenaNode(Node):
    """
    Athena Node - IDE Integration

    Responsible for:
    - File system observation
    - Diff detection and tracking
    - Code change awareness
    - Development environment state
    """

    def __init__(self, workspace_root: Path | None = None):
        super().__init__("athena", NodeType.ATHENA)
        self.workspace_root = workspace_root or Path.cwd()
        self._file_cache: dict[str, str] = {}
        self._change_log: list[dict] = []

    def observe(self) -> dict[str, Any]:
        """Observe the current state of the IDE/workspace"""
        self.status = NodeStatus.OBSERVING
        self._last_observation = datetime.now()

        files_state = {}
        if self.workspace_root.exists():
            for file_path in self.workspace_root.rglob("*"):
                if file_path.is_file() and not self._should_ignore(file_path):
                    rel_path = str(file_path.relative_to(self.workspace_root))
                    files_state[rel_path] = {
                        "modified": file_path.stat().st_mtime,
                        "size": file_path.stat().st_size,
                        "checksum": self._file_checksum(file_path)
                    }

        self.status = NodeStatus.IDLE
        return {
            "workspace": str(self.workspace_root),
            "files": files_state,
            "observation_time": self._last_observation.isoformat()
        }

    def perceive(self, state: dict[str, Any]) -> dict[str, Any]:
        """Detect changes from observed state"""
        self.status = NodeStatus.PROCESSING
        changes = {"added": [], "modified": [], "removed": []}

        current_files = state.get("files", {})

        # Detect changes
        for path, info in current_files.items():
            if path not in self._file_cache:
                changes["added"].append(path)
            elif self._file_cache[path] != info.get("checksum"):
                changes["modified"].append(path)

        for path in self._file_cache:
            if path not in current_files:
                changes["removed"].append(path)

        # Update cache
        self._file_cache = {
            path: info.get("checksum", "")
            for path, info in current_files.items()
        }

        if any(changes.values()):
            self._change_log.append({
                "timestamp": datetime.now().isoformat(),
                "changes": changes
            })

        self.status = NodeStatus.IDLE
        return changes

    def act(self, action: dict[str, Any]) -> dict[str, Any]:
        """Execute an action in the workspace"""
        action_type = action.get("type")
        result = {"success": False, "action": action_type}

        if action_type == "read_file":
            path = self.workspace_root / action.get("path", "")
            if path.exists():
                result["content"] = path.read_text()
                result["success"] = True

        elif action_type == "get_changes":
            result["changes"] = self._change_log
            result["success"] = True

        return result

    def _should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored"""
        ignore_patterns = {".git", "__pycache__", "node_modules", ".venv", "venv"}
        return any(pattern in str(path) for pattern in ignore_patterns)

    def _file_checksum(self, path: Path) -> str:
        """Compute checksum of a file"""
        try:
            content = path.read_bytes()
            return hashlib.sha256(content).hexdigest()[:16]
        except (OSError, PermissionError):
            return ""


class ObsidianNode(Node):
    """
    Obsidian Node - Memory and Knowledge

    Responsible for:
    - Persistent memory storage
    - Knowledge graph management
    - Pattern recognition from history
    - Structural awareness
    """

    def __init__(self, vault_path: Path | None = None):
        super().__init__("obsidian", NodeType.OBSIDIAN)
        self.vault_path = vault_path or Path.cwd() / ".sovereign" / "vault"
        self._knowledge_base: dict[str, Any] = {}
        self._patterns: list[dict] = []

    def observe(self) -> dict[str, Any]:
        """Observe the current state of the knowledge vault"""
        self.status = NodeStatus.OBSERVING
        self._last_observation = datetime.now()

        vault_state = {
            "entries": len(self._knowledge_base),
            "patterns": len(self._patterns),
            "vault_path": str(self.vault_path)
        }

        self.status = NodeStatus.IDLE
        return vault_state

    def perceive(self, state: dict[str, Any]) -> dict[str, Any]:
        """Analyze patterns in the knowledge base"""
        self.status = NodeStatus.PROCESSING
        analysis = {
            "new_patterns": [],
            "reinforced_patterns": [],
            "knowledge_gaps": []
        }
        self.status = NodeStatus.IDLE
        return analysis

    def act(self, action: dict[str, Any]) -> dict[str, Any]:
        """Execute an action on the knowledge base"""
        action_type = action.get("type")
        result = {"success": False, "action": action_type}

        if action_type == "store":
            key = action.get("key", "")
            value = action.get("value")
            if key:
                self._knowledge_base[key] = {
                    "value": value,
                    "timestamp": datetime.now().isoformat(),
                    "version": self._knowledge_base.get(key, {}).get("version", 0) + 1
                }
                result["success"] = True

        elif action_type == "retrieve":
            key = action.get("key", "")
            if key in self._knowledge_base:
                result["value"] = self._knowledge_base[key]
                result["success"] = True

        elif action_type == "add_pattern":
            pattern = action.get("pattern")
            if pattern:
                self._patterns.append({
                    "pattern": pattern,
                    "timestamp": datetime.now().isoformat(),
                    "occurrences": 1
                })
                result["success"] = True

        elif action_type == "list_all":
            result["knowledge_base"] = self._knowledge_base
            result["patterns"] = self._patterns
            result["success"] = True

        return result

    def store_knowledge(self, key: str, value: Any) -> bool:
        """Helper method to store knowledge"""
        result = self.act({"type": "store", "key": key, "value": value})
        return result["success"]

    def retrieve_knowledge(self, key: str) -> Any:
        """Helper method to retrieve knowledge"""
        result = self.act({"type": "retrieve", "key": key})
        return result.get("value") if result["success"] else None


class ClaudeNode(Node):
    """
    Claude Node - Reflection and Analysis

    Responsible for:
    - Deep pattern analysis
    - Workflow construction
    - Cross-node synthesis
    - Strategy optimization
    """

    def __init__(self):
        super().__init__("claude", NodeType.CLAUDE)
        self._reflections: list[dict] = []
        self._insights: list[dict] = []

    def observe(self) -> dict[str, Any]:
        """Observe the current reflection state"""
        self.status = NodeStatus.OBSERVING
        self._last_observation = datetime.now()

        reflection_state = {
            "total_reflections": len(self._reflections),
            "total_insights": len(self._insights),
            "last_reflection": self._reflections[-1] if self._reflections else None
        }

        self.status = NodeStatus.IDLE
        return reflection_state

    def perceive(self, state: dict[str, Any]) -> dict[str, Any]:
        """Analyze input state and generate insights"""
        self.status = NodeStatus.REFLECTING
        insights = self._analyze_state(state)
        self.status = NodeStatus.IDLE
        return insights

    def act(self, action: dict[str, Any]) -> dict[str, Any]:
        """Execute a reflection action"""
        action_type = action.get("type")
        result = {"success": False, "action": action_type}

        if action_type == "reflect":
            context = action.get("context", {})
            reflection = self._generate_reflection(context)
            self._reflections.append(reflection)
            result["reflection"] = reflection
            result["success"] = True

        elif action_type == "synthesize":
            inputs = action.get("inputs", [])
            synthesis = self._synthesize(inputs)
            result["synthesis"] = synthesis
            result["success"] = True

        elif action_type == "get_insights":
            result["insights"] = self._insights
            result["success"] = True

        return result

    def _analyze_state(self, state: dict[str, Any]) -> dict[str, Any]:
        """Analyze state and generate insights"""
        patterns = []
        recommendations = []

        # Pattern detection (simplified)
        if "changes" in state:
            changes = state["changes"]
            if len(changes.get("modified", [])) > 5:
                patterns.append("high_modification_rate")
                recommendations.append("Consider smaller, focused changes")

        insight = {
            "timestamp": datetime.now().isoformat(),
            "patterns": patterns,
            "recommendations": recommendations,
            "input_state": state
        }

        if patterns:
            self._insights.append(insight)

        return insight

    def _generate_reflection(self, context: dict[str, Any]) -> dict:
        """Generate a reflection from context"""
        return {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "observations": [],
            "conclusions": []
        }

    def _synthesize(self, inputs: list[dict]) -> dict:
        """Synthesize multiple inputs into a unified understanding"""
        return {
            "timestamp": datetime.now().isoformat(),
            "input_count": len(inputs),
            "unified_patterns": [],
            "action_plan": []
        }


class OrchestratorNode(Node):
    """
    Orchestrator Node - Meta-Coordination

    Responsible for:
    - Cross-node coordination
    - Ritual evolution
    - System-wide optimization
    - Emergent behavior management
    """

    def __init__(self):
        super().__init__("orchestrator", NodeType.ORCHESTRATOR)
        self._nodes: dict[str, Node] = {}
        self._coordination_log: list[dict] = []
        self._system_state: dict[str, Any] = {}

    def register_node(self, node: Node):
        """Register a node for coordination"""
        self._nodes[node.node_id] = node

    def observe(self) -> dict[str, Any]:
        """Observe the overall system state"""
        self.status = NodeStatus.OBSERVING
        self._last_observation = datetime.now()

        node_states = {}
        for node_id, node in self._nodes.items():
            node_states[node_id] = {
                "type": node.node_type.name,
                "status": node.status.name
            }

        self._system_state = {
            "nodes": node_states,
            "total_nodes": len(self._nodes),
            "coordination_events": len(self._coordination_log)
        }

        self.status = NodeStatus.IDLE
        return self._system_state

    def perceive(self, state: dict[str, Any]) -> dict[str, Any]:
        """Analyze system-wide patterns"""
        self.status = NodeStatus.PROCESSING

        analysis = {
            "bottlenecks": [],
            "optimization_opportunities": [],
            "emergent_patterns": []
        }

        self.status = NodeStatus.IDLE
        return analysis

    def act(self, action: dict[str, Any]) -> dict[str, Any]:
        """Execute a coordination action"""
        action_type = action.get("type")
        result = {"success": False, "action": action_type}

        if action_type == "broadcast":
            message = action.get("message", {})
            for node in self._nodes.values():
                node.perceive(message)
            result["success"] = True
            result["reached_nodes"] = list(self._nodes.keys())

        elif action_type == "coordinate":
            coordination = self._coordinate_nodes(action.get("plan", {}))
            self._coordination_log.append(coordination)
            result["coordination"] = coordination
            result["success"] = True

        elif action_type == "get_system_state":
            result["state"] = self._system_state
            result["success"] = True

        return result

    def _coordinate_nodes(self, plan: dict[str, Any]) -> dict:
        """Coordinate nodes according to a plan"""
        return {
            "timestamp": datetime.now().isoformat(),
            "plan": plan,
            "node_results": {},
            "success": True
        }

    def coordinate_observation(self) -> dict[str, dict[str, Any]]:
        """Coordinate observation across all registered nodes"""
        observations = {}
        for node_id, node in self._nodes.items():
            observations[node_id] = node.observe()
        return observations

    def coordinate_perception(self, observations: dict[str, dict]) -> dict[str, dict]:
        """Coordinate perception across all registered nodes"""
        perceptions = {}
        for node_id, node in self._nodes.items():
            if node_id in observations:
                perceptions[node_id] = node.perceive(observations[node_id])
        return perceptions

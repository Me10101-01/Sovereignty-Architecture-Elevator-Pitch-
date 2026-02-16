"""
Core Sovereign Methodology Solver

The central orchestration engine that coordinates all nodes, manages state
awareness, generates rituals, and maintains the autonomous feedback loop.
"""

from __future__ import annotations

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum, auto

from .nodes import Node, AthenaNode, ObsidianNode, ClaudeNode, OrchestratorNode
from .state import StateAwareness, EnvironmentState
from .rituals import RitualGenerator, Ritual
from .reflex import ToolchainReflex
from .loop import AutonomousFeedbackLoop


class SolverMode(Enum):
    """Operating modes for the solver"""
    MANUAL = auto()      # User-driven operations
    SUPERVISED = auto()  # Suggestions require approval
    AUTONOMOUS = auto()  # Fully autonomous operation


@dataclass
class SolverConfig:
    """Configuration for the Sovereign Solver"""
    workspace_root: Path = field(default_factory=Path.cwd)
    vault_path: Path | None = None
    mode: SolverMode = SolverMode.SUPERVISED
    auto_evolve: bool = True
    max_iterations: int = 100
    observation_interval: float = 5.0  # seconds
    enable_reflexes: bool = True
    enable_rituals: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "workspace_root": str(self.workspace_root),
            "vault_path": str(self.vault_path) if self.vault_path else None,
            "mode": self.mode.name,
            "auto_evolve": self.auto_evolve,
            "max_iterations": self.max_iterations,
            "observation_interval": self.observation_interval,
            "enable_reflexes": self.enable_reflexes,
            "enable_rituals": self.enable_rituals
        }


class SovereignSolver:
    """
    The Sovereign Methodology Solver

    Orchestrates multi-agent coordination, state awareness, ritual generation,
    and autonomous feedback loops for single-operator sovereignty.
    """

    def __init__(self, config: SolverConfig | None = None):
        self.config = config or SolverConfig()
        self._initialized = False
        self._running = False

        # Initialize core components
        self._state_awareness = StateAwareness()
        self._ritual_generator = RitualGenerator()
        self._reflex_system = ToolchainReflex()
        self._feedback_loop = AutonomousFeedbackLoop()

        # Initialize nodes
        self._athena = AthenaNode(self.config.workspace_root)
        self._obsidian = ObsidianNode(self.config.vault_path)
        self._claude = ClaudeNode()
        self._orchestrator = OrchestratorNode()

        # Register nodes with orchestrator
        self._orchestrator.register_node(self._athena)
        self._orchestrator.register_node(self._obsidian)
        self._orchestrator.register_node(self._claude)

        # Metrics
        self._metrics: dict[str, Any] = {
            "observations": 0,
            "rituals_executed": 0,
            "reflexes_triggered": 0,
            "feedback_iterations": 0
        }

        self._session_id = self._generate_session_id()

    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        content = f"session:{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @property
    def session_id(self) -> str:
        """Get the current session ID"""
        return self._session_id

    @property
    def is_running(self) -> bool:
        """Check if the solver is running"""
        return self._running

    def initialize(self):
        """Initialize the solver and all components"""
        if self._initialized:
            return

        # Set up default reflexes
        self._setup_default_reflexes()

        # Set up default rituals
        self._setup_default_rituals()

        self._initialized = True

    def _setup_default_reflexes(self):
        """Set up default reflexes for common patterns"""
        self._reflex_system.create_reflex(
            name="File Change Logger",
            trigger_pattern="file_change",
            trigger_category="file_system",
            action_type="log",
            action_params={"message": "File change detected", "level": "info"},
            priority="normal"
        )

        self._reflex_system.create_reflex(
            name="Error Alert",
            trigger_pattern="error",
            trigger_category="workflow",
            action_type="notify",
            action_params={"channel": "alerts", "message": "Error occurred"},
            priority="high"
        )

    def _setup_default_rituals(self):
        """Set up default rituals"""
        self._ritual_generator.create_ritual(
            name="Daily Observation",
            trigger="manual",
            description="Comprehensive daily observation of system state",
            template="observe_analyze_act",
            tags=["daily", "observation"]
        )

    def observe(self) -> dict[str, Any]:
        """Perform observation across all nodes"""
        self._metrics["observations"] += 1

        # Collect observations from all nodes
        observations = self._orchestrator.coordinate_observation()

        # Capture states
        for node_name, state_data in observations.items():
            self._state_awareness.capture_state(node_name, state_data)

        return observations

    def perceive(self, observations: dict[str, Any] | None = None) -> dict[str, Any]:
        """Process observations and detect patterns"""
        if observations is None:
            observations = self.observe()

        # Coordinate perception across nodes
        perceptions = self._orchestrator.coordinate_perception(observations)

        # Detect patterns
        patterns = {}
        for node_name in observations:
            node_patterns = self._state_awareness.detect_patterns(node_name)
            if node_patterns:
                patterns[node_name] = node_patterns

        return {
            "perceptions": perceptions,
            "patterns": patterns
        }

    def analyze(self) -> dict[str, Any]:
        """Analyze current state and patterns"""
        observations = self.observe()
        perception_result = self.perceive(observations)

        # Get Claude node's analysis
        analysis = self._claude.perceive(perception_result)

        return {
            "observations": observations,
            "perceptions": perception_result["perceptions"],
            "patterns": perception_result["patterns"],
            "analysis": analysis
        }

    def reflect(self, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Generate reflections on current state"""
        if context is None:
            context = self.analyze()

        result = self._claude.act({
            "type": "reflect",
            "context": context
        })

        return result.get("reflection", {})

    def generate_ritual(
        self,
        name: str,
        trigger: str,
        description: str = "",
        steps: list[dict] | None = None,
        template: str | None = None,
        tags: list[str] | None = None
    ) -> Ritual:
        """Generate a new ritual"""
        return self._ritual_generator.create_ritual(
            name=name,
            trigger=trigger,
            description=description,
            steps=steps,
            template=template,
            tags=tags
        )

    def run_ritual(
        self,
        ritual_id: str,
        context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Execute a ritual"""
        self._metrics["rituals_executed"] += 1

        execution = self._ritual_generator.execute_ritual(ritual_id, context)
        return {
            "ritual_id": ritual_id,
            "status": execution.status,
            "duration": execution.duration_seconds,
            "step_results": execution.step_results,
            "error": execution.error
        }

    def trigger_reflex(self, event: dict[str, Any]) -> list[dict]:
        """Process an event through the reflex system"""
        self._metrics["reflexes_triggered"] += 1

        executions = self._reflex_system.process_event(event)
        return [
            {
                "reflex_id": e.reflex_id,
                "success": e.success,
                "result": e.result,
                "error": e.error
            }
            for e in executions
        ]

    def evolve(self) -> dict[str, Any]:
        """Run a feedback loop iteration for self-improvement"""
        self._metrics["feedback_iterations"] += 1

        # Gather data
        observations = self.observe()
        perception_result = self.perceive(observations)

        # Get execution histories
        ritual_executions = [
            {
                "ritual_id": e.ritual_id,
                "success": e.status == "completed",
                "duration_seconds": e.duration_seconds
            }
            for e in self._ritual_generator.get_execution_history(limit=50)
        ]

        reflex_executions = [
            {
                "reflex_id": e.reflex_id,
                "success": e.success,
                "duration_seconds": (e.completed_at - e.started_at).total_seconds()
                if e.completed_at else None
            }
            for e in self._reflex_system.get_execution_history(limit=50)
        ]

        # Run feedback loop
        iteration = self._feedback_loop.run_full_cycle(
            observations=observations,
            perceptions=perception_result["perceptions"],
            ritual_executions=ritual_executions,
            reflex_executions=reflex_executions,
            apply_callback=self._apply_optimization if self.config.auto_evolve else None
        )

        return {
            "iteration_id": iteration.iteration_id,
            "reflections": iteration.reflections,
            "optimizations": iteration.optimizations,
            "updates": iteration.updates,
            "duration": iteration.duration_seconds
        }

    def _apply_optimization(self, optimization):
        """Apply an optimization to a ritual or reflex"""
        if optimization.target_type == "ritual":
            self._ritual_generator.evolve_ritual(
                optimization.target_id,
                optimization.changes
            )
        # Add reflex optimization logic as needed

    def get_status(self) -> dict[str, Any]:
        """Get the current status of the solver"""
        return {
            "session_id": self._session_id,
            "mode": self.config.mode.name,
            "initialized": self._initialized,
            "running": self._running,
            "metrics": self._metrics,
            "nodes": {
                "athena": self._athena.status.name,
                "obsidian": self._obsidian.status.name,
                "claude": self._claude.status.name,
                "orchestrator": self._orchestrator.status.name
            },
            "rituals": len(self._ritual_generator.list_rituals()),
            "reflexes": len(self._reflex_system.list_reflexes()),
            "feedback_loop": self._feedback_loop.export_state()
        }

    def get_rituals(self) -> list[dict]:
        """Get all rituals"""
        return self._ritual_generator.export_rituals()

    def get_reflexes(self) -> list[dict]:
        """Get all reflexes"""
        return self._reflex_system.export_reflexes()

    def store_knowledge(self, key: str, value: Any) -> bool:
        """Store knowledge in the Obsidian node"""
        return self._obsidian.store_knowledge(key, value)

    def retrieve_knowledge(self, key: str) -> Any:
        """Retrieve knowledge from the Obsidian node"""
        return self._obsidian.retrieve_knowledge(key)

    def export_state(self) -> dict[str, Any]:
        """Export the complete solver state"""
        return {
            "session_id": self._session_id,
            "config": self.config.to_dict(),
            "status": self.get_status(),
            "state_awareness": self._state_awareness.export_state(),
            "rituals": self.get_rituals(),
            "reflexes": self.get_reflexes(),
            "feedback_loop": self._feedback_loop.export_state()
        }

    def save_state(self, path: Path):
        """Save solver state to a file"""
        state = self.export_state()
        path.write_text(json.dumps(state, indent=2, default=str))

    def load_state(self, path: Path):
        """Load solver state from a file"""
        if path.exists():
            state = json.loads(path.read_text())
            # Restore rituals
            for ritual_data in state.get("rituals", []):
                self._ritual_generator.import_ritual(ritual_data)

    def __repr__(self) -> str:
        return f"SovereignSolver(session={self._session_id[:8]}, mode={self.config.mode.name})"

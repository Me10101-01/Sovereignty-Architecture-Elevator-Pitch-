"""
Sovereign Methodology Solver
============================

An autonomous multi-agent orchestration system for the Strategickhaos
Sovereignty Architecture. This system enables single-operator sovereignty
through intelligent cross-environment state awareness and ritual generation.

Core Components:
- Nodes: Athena (IDE), Obsidian (Memory), Claude (Reflection), Orchestrator (Meta)
- State Awareness: Cross-environment perception and diff detection
- Ritual Generator: Automatic workflow and procedure creation
- Toolchain Reflex: Autonomous response to environment changes
- Feedback Loop: Continuous self-improvement cycle

Architecture Pattern:
    Node → Perception → Reflection → Optimization → Updated Ritual → Node
"""

__version__ = "0.1.0"

from .core import SovereignSolver, SolverConfig, SolverMode
from .nodes import Node, AthenaNode, ObsidianNode, ClaudeNode, OrchestratorNode
from .state import StateAwareness, EnvironmentState
from .rituals import RitualGenerator, Ritual, RitualStatus
from .reflex import ToolchainReflex, Reflex, ReflexPriority
from .loop import AutonomousFeedbackLoop, LoopPhase

__all__ = [
    # Core
    "SovereignSolver",
    "SolverConfig",
    "SolverMode",
    # Nodes
    "Node",
    "AthenaNode",
    "ObsidianNode",
    "ClaudeNode",
    "OrchestratorNode",
    # State
    "StateAwareness",
    "EnvironmentState",
    # Rituals
    "RitualGenerator",
    "Ritual",
    "RitualStatus",
    # Reflex
    "ToolchainReflex",
    "Reflex",
    "ReflexPriority",
    # Loop
    "AutonomousFeedbackLoop",
    "LoopPhase",
]

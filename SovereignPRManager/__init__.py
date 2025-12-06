"""
SovereignPRManager - Autonomous PR Orchestration System.

This package provides automated pull request review, validation,
and merge orchestration using multi-AI code review.

Components:
- PRMonitor: Detect new PRs via GitHub API
- LegionReviewer: Multi-AI parallel code review
- ConflictDetector: Detect merge and semantic conflicts
- SynthesisEngine: Dialectical merge decision making
- AutoMerger: Execute merges with cryptographic provenance
"""

__version__ = "1.0.0"
__author__ = "Strategickhaos Swarm Intelligence"

from .pr_monitor import PRMonitor
from .legion_reviewer import LegionReviewer, ReviewResult
from .conflict_detector import ConflictDetector, ConflictReport
from .synthesis_engine import MergeDecisionEngine, MergeDecision, DialecticalEngine
from .auto_merger import AutoMerger, MergeResult, ProvenanceRecord

__all__ = [
    "PRMonitor",
    "LegionReviewer",
    "ReviewResult",
    "ConflictDetector",
    "ConflictReport",
    "MergeDecisionEngine",
    "MergeDecision",
    "DialecticalEngine",
    "AutoMerger",
    "MergeResult",
    "ProvenanceRecord",
]

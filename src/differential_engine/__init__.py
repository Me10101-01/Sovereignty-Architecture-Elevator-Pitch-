"""
Differential Engine: House M.D. Style Multi-Agent Psychoanalysis

This module implements a debate-synthesis system where multiple AI "specialists"
analyze input from different perspectives, challenge each other, and produce
evolved understanding through structured dialectic.

The Team:
- House (Synthesizer): Pattern recognition, contrarian insights
- Foreman (Structuralist): Systematic categorization
- Cameron (Humanist): Intent and values analysis
- Chase (Pragmatist): Actionable translation
- Wilson (Devil's Advocate): Risk assessment and counterpoints
"""

from .specialists import Specialist, TEAM
from .debate import DebateOrchestrator, DebateRound
from .engine import DifferentialEngine

__all__ = [
    "Specialist",
    "TEAM",
    "DebateOrchestrator",
    "DebateRound",
    "DifferentialEngine",
]

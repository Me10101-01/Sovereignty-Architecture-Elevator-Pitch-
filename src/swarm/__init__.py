"""
Swarm Module - Agent Coordination Zone

This module contains code for orchestrating agent behavior, parsing and generating
patterns using the Sovereign Pattern Language, and coordinating multi-agent tasks.

Key components:
- SwarmGrammar: Parses docs/ and extracts pattern definitions
- SovereignPattern: Dataclass representing a sovereignty pattern

See docs/SWARM_HANDSHAKE_PROTOCOL.md for the full handshake specification.
"""

from .grammar import SwarmGrammar, SovereignPattern

__all__ = ["SwarmGrammar", "SovereignPattern"]

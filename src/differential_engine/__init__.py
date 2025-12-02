"""
Differential Engine - Multi-Agent Debate System for Architecture Diagnosis
House M.D. style differential diagnosis for ideas and designs
"""

from .engine import DifferentialEngine
from .agents import Agent, HOUSE, WILSON, FOREMAN, CAMERON, CHASE, CUDDY
from .session import Session, SessionManager

__all__ = [
    'DifferentialEngine',
    'Agent',
    'HOUSE',
    'WILSON',
    'FOREMAN',
    'CAMERON',
    'CHASE',
    'CUDDY',
    'Session',
    'SessionManager'
]

__version__ = '1.0.0'

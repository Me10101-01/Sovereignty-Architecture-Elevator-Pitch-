"""
Swarm Module - Sovereign Swarm Intelligence Core
=================================================

This module provides the core swarm logic for LLM-driven behavior orchestration.
It follows the "Vim + absolute-path CLI ritual" pattern where modules are
designed to be extended and evolved by LLM agents.

Core Components:
- run_experiment: Execute experiments with captured traces
- analyze_logs: Process and analyze log data
- render_ritual: Render and update ritual documentation

The naming conventions and inline comments serve as **prompt stubs** for LLMs
to understand module responsibilities and generate consistent code/docs.
"""

from swarm.experiment import run_experiment
from swarm.analyzer import analyze_logs
from swarm.ritual import render_ritual

__all__ = [
    "run_experiment",
    "analyze_logs",
    "render_ritual",
]

__version__ = "0.1.0"

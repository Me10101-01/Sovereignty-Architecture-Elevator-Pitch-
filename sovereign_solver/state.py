"""
State Awareness Engine for Sovereign Methodology Solver

Cross-environment perception and diff detection system.
Tracks state across all nodes and detects patterns over time.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any, List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class EnvironmentState:
    """Represents the state of an environment at a point in time"""
    node_name: str
    timestamp: datetime
    data: dict = field(default_factory=dict)
    checksum: str = ""
    parent_checksum: str = ""

    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Compute a checksum of the state"""
        content = f"{self.node_name}:{self.timestamp.isoformat()}:{self.data}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class StateDiff:
    """Represents the difference between two states"""
    from_state: EnvironmentState
    to_state: EnvironmentState
    added: dict = field(default_factory=dict)
    removed: dict = field(default_factory=dict)
    modified: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def has_changes(self) -> bool:
        """Check if there are any changes"""
        return bool(self.added or self.removed or self.modified)


class StateAwareness:
    """
    Cross-environment state awareness engine.

    Tracks state across all nodes and environments, detecting changes
    and patterns over time.
    """

    def __init__(self):
        self._states: dict[str, list[EnvironmentState]] = defaultdict(list)
        self._diffs: list[StateDiff] = []
        self._patterns: list[dict] = []
        self._subscriptions: dict[str, list[callable]] = defaultdict(list)

    def capture_state(self, node_name: str, data: dict[str, Any]) -> EnvironmentState:
        """Capture the current state of a node"""
        previous_checksum = ""
        if self._states[node_name]:
            previous_checksum = self._states[node_name][-1].checksum

        state = EnvironmentState(
            node_name=node_name,
            timestamp=datetime.now(),
            data=data,
            parent_checksum=previous_checksum
        )

        self._states[node_name].append(state)
        self._notify_subscribers(node_name, state)

        return state

    def get_latest_state(self, node_name: str) -> EnvironmentState | None:
        """Get the latest state for a node"""
        states = self._states.get(node_name, [])
        return states[-1] if states else None

    def get_state_history(self, node_name: str, limit: int = 10) -> list[EnvironmentState]:
        """Get the state history for a node"""
        states = self._states.get(node_name, [])
        return states[-limit:] if limit else states

    def compute_diff(
        self,
        from_state: EnvironmentState,
        to_state: EnvironmentState
    ) -> StateDiff:
        """Compute the difference between two states"""
        added = {}
        removed = {}
        modified = {}

        from_data = from_state.data
        to_data = to_state.data

        # Find added and modified keys
        for key, value in to_data.items():
            if key not in from_data:
                added[key] = value
            elif from_data[key] != value:
                modified[key] = {"from": from_data[key], "to": value}

        # Find removed keys
        for key in from_data:
            if key not in to_data:
                removed[key] = from_data[key]

        diff = StateDiff(
            from_state=from_state,
            to_state=to_state,
            added=added,
            removed=removed,
            modified=modified
        )

        if diff.has_changes:
            self._diffs.append(diff)

        return diff

    def detect_patterns(self, node_name: str) -> list[dict]:
        """Detect patterns in the state history of a node"""
        history = self.get_state_history(node_name, limit=50)
        patterns = []

        if len(history) < 2:
            return patterns

        # Detect rapid change pattern
        rapid_changes = self._detect_rapid_changes(history)
        if rapid_changes:
            patterns.append({
                "type": "rapid_changes",
                "description": "Rapid succession of state changes detected",
                "occurrences": rapid_changes
            })

        # Detect cyclical pattern
        cycles = self._detect_cycles(history)
        if cycles:
            patterns.append({
                "type": "cyclical",
                "description": "Repeating state pattern detected",
                "pattern": cycles
            })

        self._patterns.extend(patterns)
        return patterns

    def _detect_rapid_changes(self, history: list[EnvironmentState]) -> list[dict]:
        """Detect rapid succession of changes"""
        rapid_changes = []
        threshold_seconds = 5

        for i in range(1, len(history)):
            delta = (history[i].timestamp - history[i-1].timestamp).total_seconds()
            if delta < threshold_seconds:
                rapid_changes.append({
                    "from": history[i-1].checksum,
                    "to": history[i].checksum,
                    "delta_seconds": delta
                })

        return rapid_changes

    def _detect_cycles(self, history: list[EnvironmentState]) -> list[str]:
        """Detect cyclical patterns in state checksums"""
        checksums = [state.checksum for state in history]
        cycles = []

        # Simple cycle detection - look for repeated checksums
        seen = {}
        for i, checksum in enumerate(checksums):
            if checksum in seen:
                cycle = checksums[seen[checksum]:i+1]
                if len(cycle) > 1:
                    cycles.append(cycle)
            seen[checksum] = i

        return cycles

    def subscribe(self, node_name: str, callback: callable):
        """Subscribe to state changes for a node"""
        self._subscriptions[node_name].append(callback)

    def unsubscribe(self, node_name: str, callback: callable):
        """Unsubscribe from state changes"""
        if callback in self._subscriptions[node_name]:
            self._subscriptions[node_name].remove(callback)

    def _notify_subscribers(self, node_name: str, state: EnvironmentState):
        """Notify subscribers of a state change"""
        for callback in self._subscriptions[node_name]:
            callback(state)

    def get_all_patterns(self) -> list[dict]:
        """Get all detected patterns"""
        return self._patterns.copy()

    def get_all_diffs(self) -> list[StateDiff]:
        """Get all computed diffs"""
        return self._diffs.copy()

    def get_cross_node_correlation(self) -> dict[str, list[str]]:
        """Find correlations between state changes across nodes"""
        correlations: dict[str, list[str]] = defaultdict(list)

        # Group states by timestamp (within threshold)
        time_groups: dict[str, list[tuple[str, EnvironmentState]]] = defaultdict(list)
        threshold_seconds = 2

        for node_name, states in self._states.items():
            for state in states:
                # Round to threshold window
                window_key = str(
                    int(state.timestamp.timestamp() / threshold_seconds)
                )
                time_groups[window_key].append((node_name, state))

        # Find groups with multiple nodes
        for window_key, group in time_groups.items():
            if len(group) > 1:
                nodes = [node_name for node_name, _ in group]
                for node in nodes:
                    correlations[node].extend([n for n in nodes if n != node])

        return dict(correlations)

    def export_state(self) -> dict[str, Any]:
        """Export the current state awareness data"""
        return {
            "states": {
                node: [
                    {
                        "timestamp": s.timestamp.isoformat(),
                        "checksum": s.checksum,
                        "data": s.data
                    }
                    for s in states
                ]
                for node, states in self._states.items()
            },
            "patterns": self._patterns,
            "diff_count": len(self._diffs)
        }

    def clear(self, node_name: str | None = None):
        """Clear state history for a node or all nodes"""
        if node_name:
            self._states[node_name] = []
        else:
            self._states.clear()
            self._diffs.clear()
            self._patterns.clear()

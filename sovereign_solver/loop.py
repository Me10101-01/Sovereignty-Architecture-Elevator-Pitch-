"""
Autonomous Feedback Loop for Sovereign Methodology Solver

The feedback loop is the self-improvement engine that enables
continuous evolution of the system's rituals and workflows.

Pattern:
    Node → Perception → Reflection → Optimization → Updated Ritual → Node
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
from typing import Any, Callable, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum, auto


class LoopPhase(Enum):
    """Phases of the feedback loop"""
    IDLE = auto()
    OBSERVING = auto()
    PERCEIVING = auto()
    REFLECTING = auto()
    OPTIMIZING = auto()
    UPDATING = auto()
    VALIDATING = auto()


class OptimizationType(Enum):
    """Types of optimizations"""
    PERFORMANCE = auto()      # Speed up execution
    RELIABILITY = auto()      # Reduce failures
    EFFICIENCY = auto()       # Reduce resource usage
    QUALITY = auto()          # Improve output quality
    CONSOLIDATION = auto()    # Merge similar patterns


@dataclass
class LoopIteration:
    """Record of a single feedback loop iteration"""
    iteration_id: str
    started_at: datetime
    completed_at: datetime | None = None
    phase: LoopPhase = LoopPhase.IDLE
    observations: dict = field(default_factory=dict)
    perceptions: dict = field(default_factory=dict)
    reflections: list[dict] = field(default_factory=list)
    optimizations: list[dict] = field(default_factory=list)
    updates: list[dict] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)

    @property
    def duration_seconds(self) -> float | None:
        """Get iteration duration"""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


@dataclass
class Optimization:
    """A recommended optimization"""
    optimization_id: str
    target_id: str  # ID of ritual/reflex to optimize
    target_type: str  # "ritual" or "reflex"
    optimization_type: OptimizationType
    description: str
    changes: dict = field(default_factory=dict)
    expected_improvement: float = 0.0
    confidence: float = 0.0
    applied: bool = False
    created_at: datetime = field(default_factory=datetime.now)


class AutonomousFeedbackLoop:
    """
    The self-improvement engine.

    Continuously monitors system execution, analyzes patterns,
    and generates optimizations for rituals and reflexes.
    """

    def __init__(self):
        self._iterations: list[LoopIteration] = []
        self._optimizations: list[Optimization] = []
        self._metrics_history: list[dict] = []
        self._phase = LoopPhase.IDLE
        self._current_iteration: LoopIteration | None = None
        self._optimization_thresholds = {
            "min_executions": 5,
            "failure_rate_threshold": 0.2,
            "slow_execution_threshold": 10.0,  # seconds
            "improvement_confidence": 0.7
        }

    @property
    def current_phase(self) -> LoopPhase:
        """Get current loop phase"""
        return self._phase

    def begin_iteration(self) -> LoopIteration:
        """Begin a new feedback loop iteration"""
        iteration_id = hashlib.sha256(
            f"iter:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        self._current_iteration = LoopIteration(
            iteration_id=iteration_id,
            started_at=datetime.now()
        )

        self._phase = LoopPhase.OBSERVING
        self._current_iteration.phase = self._phase

        return self._current_iteration

    def observe(self, observations: dict[str, Any]) -> dict[str, Any]:
        """Observation phase: collect system state"""
        if not self._current_iteration:
            self.begin_iteration()

        self._phase = LoopPhase.OBSERVING
        if self._current_iteration:
            self._current_iteration.phase = self._phase
            self._current_iteration.observations = observations

        return {
            "phase": "observe",
            "observation_count": len(observations),
            "nodes_observed": list(observations.keys())
        }

    def perceive(self, perceptions: dict[str, Any]) -> dict[str, Any]:
        """Perception phase: interpret observations"""
        self._phase = LoopPhase.PERCEIVING
        if self._current_iteration:
            self._current_iteration.phase = self._phase
            self._current_iteration.perceptions = perceptions

        return {
            "phase": "perceive",
            "perception_count": len(perceptions),
            "patterns_detected": sum(
                len(p.get("patterns", []))
                for p in perceptions.values()
            )
        }

    def reflect(
        self,
        ritual_executions: list[dict],
        reflex_executions: list[dict]
    ) -> list[dict]:
        """Reflection phase: analyze execution patterns"""
        self._phase = LoopPhase.REFLECTING
        if self._current_iteration:
            self._current_iteration.phase = self._phase

        reflections = []

        # Analyze ritual executions
        ritual_analysis = self._analyze_executions(ritual_executions, "ritual")
        reflections.extend(ritual_analysis)

        # Analyze reflex executions
        reflex_analysis = self._analyze_executions(reflex_executions, "reflex")
        reflections.extend(reflex_analysis)

        if self._current_iteration:
            self._current_iteration.reflections = reflections

        return reflections

    def _analyze_executions(
        self,
        executions: list[dict],
        exec_type: str
    ) -> list[dict]:
        """Analyze execution patterns"""
        reflections = []

        # Group by ID
        by_id: dict[str, list[dict]] = defaultdict(list)
        for execution in executions:
            exec_id = execution.get(f"{exec_type}_id", "unknown")
            by_id[exec_id].append(execution)

        for exec_id, group in by_id.items():
            if len(group) < self._optimization_thresholds["min_executions"]:
                continue

            # Calculate metrics
            total = len(group)
            failures = len([e for e in group if not e.get("success", True)])
            failure_rate = failures / total

            durations = [
                e.get("duration_seconds", 0)
                for e in group if e.get("duration_seconds")
            ]
            avg_duration = sum(durations) / len(durations) if durations else 0

            reflection = {
                "id": exec_id,
                "type": exec_type,
                "total_executions": total,
                "failure_rate": failure_rate,
                "average_duration": avg_duration,
                "issues": []
            }

            # Identify issues
            threshold = self._optimization_thresholds["failure_rate_threshold"]
            if failure_rate > threshold:
                reflection["issues"].append({
                    "type": "high_failure_rate",
                    "value": failure_rate,
                    "threshold": threshold
                })

            slow_threshold = self._optimization_thresholds["slow_execution_threshold"]
            if avg_duration > slow_threshold:
                reflection["issues"].append({
                    "type": "slow_execution",
                    "value": avg_duration,
                    "threshold": slow_threshold
                })

            if reflection["issues"]:
                reflections.append(reflection)

        return reflections

    def optimize(self, reflections: list[dict]) -> list[Optimization]:
        """Optimization phase: generate improvements"""
        self._phase = LoopPhase.OPTIMIZING
        if self._current_iteration:
            self._current_iteration.phase = self._phase

        optimizations = []

        for reflection in reflections:
            for issue in reflection.get("issues", []):
                optimization = self._generate_optimization(reflection, issue)
                if optimization:
                    optimizations.append(optimization)
                    self._optimizations.append(optimization)

        if self._current_iteration:
            self._current_iteration.optimizations = [
                {
                    "id": o.optimization_id,
                    "type": o.optimization_type.name,
                    "target": o.target_id
                }
                for o in optimizations
            ]

        return optimizations

    def _generate_optimization(
        self,
        reflection: dict,
        issue: dict
    ) -> Optimization | None:
        """Generate an optimization recommendation"""
        optimization_id = hashlib.sha256(
            f"opt:{reflection['id']}:{issue['type']}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        issue_type = issue["type"]

        if issue_type == "high_failure_rate":
            return Optimization(
                optimization_id=optimization_id,
                target_id=reflection["id"],
                target_type=reflection["type"],
                optimization_type=OptimizationType.RELIABILITY,
                description=f"Reduce failure rate from {issue['value']:.1%} to below {issue['threshold']:.1%}",
                changes={
                    "add_retry": True,
                    "add_validation": True,
                    "simplify_steps": True
                },
                expected_improvement=(issue["value"] - issue["threshold"]) / issue["value"],
                confidence=0.7
            )

        elif issue_type == "slow_execution":
            return Optimization(
                optimization_id=optimization_id,
                target_id=reflection["id"],
                target_type=reflection["type"],
                optimization_type=OptimizationType.PERFORMANCE,
                description=f"Reduce execution time from {issue['value']:.1f}s to below {issue['threshold']:.1f}s",
                changes={
                    "parallelize": True,
                    "cache_results": True,
                    "remove_redundancy": True
                },
                expected_improvement=(issue["value"] - issue["threshold"]) / issue["value"],
                confidence=0.6
            )

        return None

    def update(
        self,
        optimizations: list[Optimization],
        apply_callback: Optional[Callable] = None
    ) -> list[dict]:
        """Update phase: apply optimizations"""
        self._phase = LoopPhase.UPDATING
        if self._current_iteration:
            self._current_iteration.phase = self._phase

        updates = []

        for optimization in optimizations:
            if optimization.confidence < self._optimization_thresholds["improvement_confidence"]:
                continue

            update = {
                "optimization_id": optimization.optimization_id,
                "target_id": optimization.target_id,
                "applied": False,
                "timestamp": datetime.now().isoformat()
            }

            if apply_callback:
                try:
                    apply_callback(optimization)
                    optimization.applied = True
                    update["applied"] = True
                except Exception as e:
                    update["error"] = str(e)

            updates.append(update)

        if self._current_iteration:
            self._current_iteration.updates = updates

        return updates

    def validate(self) -> dict[str, Any]:
        """Validation phase: verify improvements"""
        self._phase = LoopPhase.VALIDATING
        if self._current_iteration:
            self._current_iteration.phase = self._phase

        validation = {
            "phase": "validate",
            "optimizations_applied": len([
                o for o in self._optimizations if o.applied
            ]),
            "pending_validation": []
        }

        return validation

    def complete_iteration(self) -> LoopIteration | None:
        """Complete the current iteration"""
        if not self._current_iteration:
            return None

        self._current_iteration.completed_at = datetime.now()
        self._current_iteration.phase = LoopPhase.IDLE

        # Calculate iteration metrics
        self._current_iteration.metrics = {
            "duration_seconds": self._current_iteration.duration_seconds,
            "observations_count": len(self._current_iteration.observations),
            "reflections_count": len(self._current_iteration.reflections),
            "optimizations_count": len(self._current_iteration.optimizations),
            "updates_count": len(self._current_iteration.updates)
        }

        self._iterations.append(self._current_iteration)
        self._metrics_history.append(self._current_iteration.metrics)

        completed = self._current_iteration
        self._current_iteration = None
        self._phase = LoopPhase.IDLE

        return completed

    def run_full_cycle(
        self,
        observations: dict[str, Any],
        perceptions: dict[str, Any],
        ritual_executions: list[dict],
        reflex_executions: list[dict],
        apply_callback: Optional[Callable] = None
    ) -> LoopIteration:
        """Run a complete feedback loop cycle"""
        self.begin_iteration()
        self.observe(observations)
        self.perceive(perceptions)
        reflections = self.reflect(ritual_executions, reflex_executions)
        optimizations = self.optimize(reflections)
        self.update(optimizations, apply_callback)
        self.validate()
        iteration = self.complete_iteration()

        if iteration is None:
            # This shouldn't happen if begin_iteration was called, but handle gracefully
            fallback_id = hashlib.sha256(
                f"fallback:{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]
            start_time = datetime.now()
            return LoopIteration(
                iteration_id=fallback_id,
                started_at=start_time,
                completed_at=start_time,
                phase=LoopPhase.IDLE,
                metrics={"error": "iteration_not_started"}
            )
        return iteration

    def get_pending_optimizations(self) -> list[Optimization]:
        """Get optimizations that haven't been applied"""
        return [o for o in self._optimizations if not o.applied]

    def get_applied_optimizations(self) -> list[Optimization]:
        """Get optimizations that have been applied"""
        return [o for o in self._optimizations if o.applied]

    def get_iteration_history(self, limit: int = 10) -> list[LoopIteration]:
        """Get iteration history"""
        return self._iterations[-limit:]

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of loop metrics"""
        if not self._metrics_history:
            return {"iterations": 0}

        total_iterations = len(self._metrics_history)
        total_observations = sum(m.get("observations_count", 0) for m in self._metrics_history)
        total_optimizations = sum(m.get("optimizations_count", 0) for m in self._metrics_history)

        durations = [m.get("duration_seconds", 0) for m in self._metrics_history if m.get("duration_seconds")]
        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            "iterations": total_iterations,
            "total_observations": total_observations,
            "total_optimizations": total_optimizations,
            "average_iteration_duration": avg_duration,
            "applied_optimizations": len(self.get_applied_optimizations()),
            "pending_optimizations": len(self.get_pending_optimizations())
        }

    def set_threshold(self, threshold_name: str, value: float):
        """Set an optimization threshold"""
        if threshold_name in self._optimization_thresholds:
            self._optimization_thresholds[threshold_name] = value

    def get_thresholds(self) -> dict[str, float]:
        """Get current optimization thresholds"""
        return self._optimization_thresholds.copy()

    def clear_history(self, before: datetime | None = None):
        """Clear iteration history"""
        if before:
            self._iterations = [
                i for i in self._iterations
                if i.started_at >= before
            ]
            self._optimizations = [
                o for o in self._optimizations
                if o.created_at >= before
            ]
        else:
            self._iterations.clear()
            self._optimizations.clear()
            self._metrics_history.clear()

    def export_state(self) -> dict[str, Any]:
        """Export the current state of the feedback loop"""
        return {
            "phase": self._phase.name,
            "iterations_count": len(self._iterations),
            "optimizations_count": len(self._optimizations),
            "thresholds": self._optimization_thresholds,
            "metrics_summary": self.get_metrics_summary()
        }

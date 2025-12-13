"""
Ritual Generator for Sovereign Methodology Solver

Rituals are reusable, evolvable workflows that encode best practices
and automate recurring patterns in the development process.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any, Callable, List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum, auto


class RitualStatus(Enum):
    """Status of a ritual"""
    DRAFT = auto()
    ACTIVE = auto()
    PAUSED = auto()
    DEPRECATED = auto()
    ARCHIVED = auto()


class RitualTrigger(Enum):
    """Types of triggers that can activate a ritual"""
    MANUAL = auto()
    FILE_CHANGE = auto()
    TIME_BASED = auto()
    STATE_CHANGE = auto()
    PATTERN_DETECTED = auto()
    NODE_EVENT = auto()


@dataclass
class RitualStep:
    """A single step in a ritual workflow"""
    name: str
    action: str
    params: dict = field(default_factory=dict)
    condition: str | None = None
    on_failure: str = "abort"  # abort, continue, retry
    max_retries: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "action": self.action,
            "params": self.params,
            "condition": self.condition,
            "on_failure": self.on_failure,
            "max_retries": self.max_retries
        }


@dataclass
class RitualExecution:
    """Record of a ritual execution"""
    ritual_id: str
    started_at: datetime
    completed_at: datetime | None = None
    status: str = "running"
    step_results: list[dict] = field(default_factory=list)
    error: str | None = None

    @property
    def duration_seconds(self) -> float | None:
        """Get the execution duration in seconds"""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


@dataclass
class Ritual:
    """A reusable, evolvable workflow"""
    ritual_id: str
    name: str
    description: str
    trigger: RitualTrigger
    trigger_config: dict = field(default_factory=dict)
    steps: list[RitualStep] = field(default_factory=list)
    status: RitualStatus = RitualStatus.DRAFT
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    execution_count: int = 0
    success_count: int = 0
    tags: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate the success rate"""
        if self.execution_count == 0:
            return 0.0
        return self.success_count / self.execution_count

    @property
    def checksum(self) -> str:
        """Compute a checksum of the ritual definition"""
        content = f"{self.name}:{self.version}:{[s.to_dict() for s in self.steps]}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "ritual_id": self.ritual_id,
            "name": self.name,
            "description": self.description,
            "trigger": self.trigger.name,
            "trigger_config": self.trigger_config,
            "steps": [s.to_dict() for s in self.steps],
            "status": self.status.name,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "success_rate": self.success_rate,
            "tags": self.tags
        }


class RitualGenerator:
    """
    Generates and manages rituals from detected patterns.

    Rituals are workflows that:
    - Encode best practices
    - Automate recurring patterns
    - Evolve based on execution feedback
    """

    def __init__(self):
        self._rituals: dict[str, Ritual] = {}
        self._executions: list[RitualExecution] = []
        self._action_handlers: dict[str, Callable] = {}
        self._templates: dict[str, dict] = self._load_templates()

    def _load_templates(self) -> dict[str, dict]:
        """Load built-in ritual templates"""
        return {
            "observe_analyze_act": {
                "name": "Observe-Analyze-Act",
                "description": "Standard pattern for state observation and response",
                "steps": [
                    {"name": "Observe", "action": "observe_state"},
                    {"name": "Analyze", "action": "analyze_patterns"},
                    {"name": "Act", "action": "execute_response"}
                ]
            },
            "file_change_response": {
                "name": "File Change Response",
                "description": "Respond to file system changes",
                "steps": [
                    {"name": "Detect", "action": "detect_changes"},
                    {"name": "Classify", "action": "classify_change"},
                    {"name": "Respond", "action": "apply_response"}
                ]
            },
            "knowledge_capture": {
                "name": "Knowledge Capture",
                "description": "Capture and persist new knowledge",
                "steps": [
                    {"name": "Extract", "action": "extract_knowledge"},
                    {"name": "Validate", "action": "validate_knowledge"},
                    {"name": "Store", "action": "store_knowledge"}
                ]
            },
            "reflection_cycle": {
                "name": "Reflection Cycle",
                "description": "Deep analysis and insight generation",
                "steps": [
                    {"name": "Gather", "action": "gather_context"},
                    {"name": "Reflect", "action": "deep_reflect"},
                    {"name": "Synthesize", "action": "synthesize_insights"},
                    {"name": "Apply", "action": "apply_learnings"}
                ]
            }
        }

    def create_ritual(
        self,
        name: str,
        trigger: RitualTrigger | str,
        description: str = "",
        steps: list[dict] | None = None,
        trigger_config: dict | None = None,
        template: str | None = None,
        tags: list[str] | None = None
    ) -> Ritual:
        """Create a new ritual"""
        # Handle string trigger
        if isinstance(trigger, str):
            trigger = RitualTrigger[trigger.upper()]

        # Generate ritual ID
        ritual_id = hashlib.sha256(
            f"{name}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        # Use template if specified
        ritual_steps = []
        if template and template in self._templates:
            template_data = self._templates[template]
            if not description:
                description = template_data.get("description", "")
            for step_data in template_data.get("steps", []):
                ritual_steps.append(RitualStep(**step_data))
        elif steps:
            for step_data in steps:
                ritual_steps.append(RitualStep(**step_data))

        ritual = Ritual(
            ritual_id=ritual_id,
            name=name,
            description=description,
            trigger=trigger,
            trigger_config=trigger_config or {},
            steps=ritual_steps,
            tags=tags or []
        )

        self._rituals[ritual_id] = ritual
        return ritual

    def get_ritual(self, ritual_id: str) -> Ritual | None:
        """Get a ritual by ID"""
        return self._rituals.get(ritual_id)

    def list_rituals(
        self,
        status: RitualStatus | None = None,
        trigger: RitualTrigger | None = None,
        tags: list[str] | None = None
    ) -> list[Ritual]:
        """List rituals with optional filtering"""
        rituals = list(self._rituals.values())

        if status:
            rituals = [r for r in rituals if r.status == status]

        if trigger:
            rituals = [r for r in rituals if r.trigger == trigger]

        if tags:
            rituals = [
                r for r in rituals
                if any(tag in r.tags for tag in tags)
            ]

        return rituals

    def activate_ritual(self, ritual_id: str) -> bool:
        """Activate a ritual for execution"""
        ritual = self._rituals.get(ritual_id)
        if ritual:
            ritual.status = RitualStatus.ACTIVE
            ritual.updated_at = datetime.now()
            return True
        return False

    def pause_ritual(self, ritual_id: str) -> bool:
        """Pause a ritual"""
        ritual = self._rituals.get(ritual_id)
        if ritual:
            ritual.status = RitualStatus.PAUSED
            ritual.updated_at = datetime.now()
            return True
        return False

    def deprecate_ritual(self, ritual_id: str) -> bool:
        """Mark a ritual as deprecated"""
        ritual = self._rituals.get(ritual_id)
        if ritual:
            ritual.status = RitualStatus.DEPRECATED
            ritual.updated_at = datetime.now()
            return True
        return False

    def register_action(self, action_name: str, handler: Callable):
        """Register an action handler for ritual steps"""
        self._action_handlers[action_name] = handler

    def execute_ritual(
        self,
        ritual_id: str,
        context: dict[str, Any] | None = None
    ) -> RitualExecution:
        """Execute a ritual"""
        ritual = self._rituals.get(ritual_id)
        if not ritual:
            return RitualExecution(
                ritual_id=ritual_id,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                status="error",
                error="Ritual not found"
            )

        execution = RitualExecution(
            ritual_id=ritual_id,
            started_at=datetime.now()
        )

        ritual.execution_count += 1
        ctx = context or {}

        try:
            for step in ritual.steps:
                step_result = self._execute_step(step, ctx)
                execution.step_results.append(step_result)

                if not step_result.get("success", False):
                    if step.on_failure == "abort":
                        execution.status = "failed"
                        execution.error = step_result.get("error", "Step failed")
                        break
                    elif step.on_failure == "retry":
                        for attempt in range(step.max_retries):
                            step_result = self._execute_step(step, ctx)
                            if step_result.get("success", False):
                                break
                        if not step_result.get("success", False):
                            execution.status = "failed"
                            execution.error = f"Step failed after {step.max_retries} retries"
                            break
                # Continue on 'continue' failure mode

                # Update context with step results
                if "output" in step_result:
                    ctx[step.name] = step_result["output"]
            else:
                execution.status = "completed"
                ritual.success_count += 1

        except Exception as e:
            execution.status = "error"
            execution.error = str(e)

        execution.completed_at = datetime.now()
        self._executions.append(execution)

        return execution

    def _execute_step(
        self,
        step: RitualStep,
        context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a single ritual step"""
        result = {
            "step": step.name,
            "action": step.action,
            "success": False
        }

        # Check condition - use safe evaluation (only simple boolean checks)
        if step.condition:
            try:
                if not self._evaluate_condition(step.condition, context):
                    result["success"] = True
                    result["skipped"] = True
                    return result
            except Exception as e:
                result["error"] = f"Condition evaluation failed: {e}"
                return result

        # Execute action
        handler = self._action_handlers.get(step.action)
        if handler:
            try:
                output = handler(step.params, context)
                result["success"] = True
                result["output"] = output
            except Exception as e:
                result["error"] = str(e)
        else:
            # No handler - treat as success with logged action
            result["success"] = True
            result["note"] = f"No handler for action '{step.action}'"

        return result

    def _evaluate_condition(self, condition: str, context: dict[str, Any]) -> bool:
        """
        Safely evaluate a condition string.

        Only supports simple boolean expressions like:
        - "key" (checks if key exists and is truthy in context)
        - "key == value" (equality check)
        - "key != value" (inequality check)
        - "key in list" (membership check)
        """
        condition = condition.strip()

        # Check for equality
        if "==" in condition:
            parts = condition.split("==", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip().strip("'\"")
                return str(context.get(key, "")) == value

        # Check for inequality
        if "!=" in condition:
            parts = condition.split("!=", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip().strip("'\"")
                return str(context.get(key, "")) != value

        # Check for membership
        if " in " in condition:
            parts = condition.split(" in ", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                list_key = parts[1].strip()
                list_val = context.get(list_key, [])
                return context.get(key) in list_val

        # Simple truthy check
        return bool(context.get(condition))

    def evolve_ritual(
        self,
        ritual_id: str,
        changes: dict[str, Any]
    ) -> Ritual | None:
        """Evolve a ritual based on execution feedback"""
        ritual = self._rituals.get(ritual_id)
        if not ritual:
            return None

        # Create new version
        ritual.version += 1
        ritual.updated_at = datetime.now()

        # Apply changes
        if "steps" in changes:
            new_steps = []
            for step_data in changes["steps"]:
                new_steps.append(RitualStep(**step_data))
            ritual.steps = new_steps

        if "trigger_config" in changes:
            ritual.trigger_config.update(changes["trigger_config"])

        if "tags" in changes:
            ritual.tags = changes["tags"]

        if "description" in changes:
            ritual.description = changes["description"]

        return ritual

    def get_execution_history(
        self,
        ritual_id: str | None = None,
        limit: int = 10
    ) -> list[RitualExecution]:
        """Get execution history"""
        executions = self._executions
        if ritual_id:
            executions = [e for e in executions if e.ritual_id == ritual_id]
        return executions[-limit:]

    def get_templates(self) -> dict[str, dict]:
        """Get available ritual templates"""
        return self._templates.copy()

    def analyze_executions(self, ritual_id: str) -> dict[str, Any]:
        """Analyze execution patterns for a ritual"""
        executions = [e for e in self._executions if e.ritual_id == ritual_id]

        if not executions:
            return {"error": "No executions found"}

        total = len(executions)
        successful = len([e for e in executions if e.status == "completed"])
        failed = len([e for e in executions if e.status in ["failed", "error"]])

        durations = [
            e.duration_seconds for e in executions
            if e.duration_seconds is not None
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            "ritual_id": ritual_id,
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "average_duration_seconds": avg_duration,
            "common_errors": self._get_common_errors(executions)
        }

    def _get_common_errors(
        self,
        executions: list[RitualExecution]
    ) -> list[dict]:
        """Get common errors from executions"""
        error_counts: dict[str, int] = {}
        for execution in executions:
            if execution.error:
                error_counts[execution.error] = error_counts.get(
                    execution.error, 0
                ) + 1

        return [
            {"error": error, "count": count}
            for error, count in sorted(
                error_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        ]

    def export_rituals(self) -> list[dict]:
        """Export all rituals as dictionaries"""
        return [r.to_dict() for r in self._rituals.values()]

    def import_ritual(self, ritual_data: dict) -> Ritual:
        """Import a ritual from dictionary data"""
        return self.create_ritual(
            name=ritual_data["name"],
            trigger=ritual_data.get("trigger", "manual"),
            description=ritual_data.get("description", ""),
            steps=ritual_data.get("steps", []),
            trigger_config=ritual_data.get("trigger_config", {}),
            tags=ritual_data.get("tags", [])
        )

"""
Toolchain Reflex Module for Sovereign Methodology Solver

Reflexes are automatic, immediate responses to specific triggers.
They execute without manual intervention and provide rapid feedback.
"""

from __future__ import annotations

import re
import hashlib
from datetime import datetime
from typing import Any, Callable, Pattern, List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum, auto


class ReflexPriority(Enum):
    """Priority levels for reflexes"""
    CRITICAL = 1    # Execute immediately, block other reflexes
    HIGH = 2        # Execute before normal reflexes
    NORMAL = 3      # Standard priority
    LOW = 4         # Execute after higher priority reflexes
    BACKGROUND = 5  # Execute only when system is idle


class ReflexCategory(Enum):
    """Categories of reflexes"""
    FILE_SYSTEM = auto()    # File and directory changes
    CODE_QUALITY = auto()   # Linting, formatting, validation
    SECURITY = auto()       # Security-related triggers
    PERFORMANCE = auto()    # Performance monitoring
    WORKFLOW = auto()       # Workflow automation
    NOTIFICATION = auto()   # Alerts and notifications
    RECOVERY = auto()       # Error recovery and healing


@dataclass
class ReflexTrigger:
    """Defines what activates a reflex"""
    pattern: str | Pattern
    category: ReflexCategory
    description: str = ""
    node_filter: list[str] | None = None  # Only trigger for specific nodes

    def matches(self, event: dict[str, Any]) -> bool:
        """Check if an event matches this trigger"""
        event_type = event.get("type", "")

        # Check node filter
        if self.node_filter:
            event_node = event.get("node", "")
            if event_node and event_node not in self.node_filter:
                return False

        # Check pattern match
        if isinstance(self.pattern, Pattern):
            return bool(self.pattern.match(event_type))
        else:
            return self.pattern == event_type or re.match(self.pattern, event_type)


@dataclass
class ReflexAction:
    """Defines what a reflex does when triggered"""
    action_type: str
    params: dict = field(default_factory=dict)
    timeout_seconds: float = 30.0
    retry_on_failure: bool = False
    max_retries: int = 3


@dataclass
class ReflexExecution:
    """Record of a reflex execution"""
    reflex_id: str
    trigger_event: dict
    started_at: datetime
    completed_at: datetime | None = None
    success: bool = False
    result: Any = None
    error: str | None = None


@dataclass
class Reflex:
    """An automatic response to a specific trigger"""
    reflex_id: str
    name: str
    trigger: ReflexTrigger
    action: ReflexAction
    priority: ReflexPriority = ReflexPriority.NORMAL
    enabled: bool = True
    cooldown_seconds: float = 0.0
    last_executed: datetime | None = None
    execution_count: int = 0
    success_count: int = 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.execution_count == 0:
            return 0.0
        return self.success_count / self.execution_count

    def is_on_cooldown(self) -> bool:
        """Check if reflex is on cooldown"""
        if not self.last_executed or self.cooldown_seconds <= 0:
            return False
        elapsed = (datetime.now() - self.last_executed).total_seconds()
        return elapsed < self.cooldown_seconds


class ToolchainReflex:
    """
    Manages automatic reflexes in the toolchain.

    Reflexes provide immediate, automatic responses to specific
    triggers without requiring manual intervention.
    """

    def __init__(self):
        self._reflexes: dict[str, Reflex] = {}
        self._executions: list[ReflexExecution] = []
        self._handlers: dict[str, Callable] = {}
        self._event_queue: list[dict] = []
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register built-in action handlers"""
        self._handlers["log"] = self._handle_log
        self._handlers["notify"] = self._handle_notify
        self._handlers["store"] = self._handle_store
        self._handlers["execute"] = self._handle_execute

    def create_reflex(
        self,
        name: str,
        trigger_pattern: str,
        trigger_category: ReflexCategory | str,
        action_type: str,
        action_params: dict | None = None,
        priority: ReflexPriority | str = ReflexPriority.NORMAL,
        cooldown_seconds: float = 0.0,
        node_filter: list[str] | None = None
    ) -> Reflex:
        """Create a new reflex"""
        # Handle string enums
        if isinstance(trigger_category, str):
            trigger_category = ReflexCategory[trigger_category.upper()]
        if isinstance(priority, str):
            priority = ReflexPriority[priority.upper()]

        reflex_id = hashlib.sha256(
            f"{name}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        trigger = ReflexTrigger(
            pattern=trigger_pattern,
            category=trigger_category,
            node_filter=node_filter
        )

        action = ReflexAction(
            action_type=action_type,
            params=action_params or {}
        )

        reflex = Reflex(
            reflex_id=reflex_id,
            name=name,
            trigger=trigger,
            action=action,
            priority=priority,
            cooldown_seconds=cooldown_seconds
        )

        self._reflexes[reflex_id] = reflex
        return reflex

    def register_handler(self, action_type: str, handler: Callable):
        """Register a custom action handler"""
        self._handlers[action_type] = handler

    def process_event(self, event: dict[str, Any]) -> list[ReflexExecution]:
        """Process an event and trigger matching reflexes"""
        executions = []

        # Find matching reflexes
        matching = [
            reflex for reflex in self._reflexes.values()
            if reflex.enabled
            and reflex.trigger.matches(event)
            and not reflex.is_on_cooldown()
        ]

        # Sort by priority
        matching.sort(key=lambda r: r.priority.value)

        # Execute reflexes
        for reflex in matching:
            execution = self._execute_reflex(reflex, event)
            executions.append(execution)

            # Stop if critical reflex blocks
            if (
                reflex.priority == ReflexPriority.CRITICAL
                and not execution.success
            ):
                break

        return executions

    def _execute_reflex(
        self,
        reflex: Reflex,
        event: dict[str, Any]
    ) -> ReflexExecution:
        """Execute a single reflex"""
        execution = ReflexExecution(
            reflex_id=reflex.reflex_id,
            trigger_event=event,
            started_at=datetime.now()
        )

        reflex.execution_count += 1
        reflex.last_executed = datetime.now()

        handler = self._handlers.get(reflex.action.action_type)
        if not handler:
            execution.completed_at = datetime.now()
            execution.error = f"No handler for action: {reflex.action.action_type}"
            return execution

        try:
            result = handler(reflex.action.params, event)
            execution.success = True
            execution.result = result
            reflex.success_count += 1
        except Exception as e:
            execution.error = str(e)
            if reflex.action.retry_on_failure:
                for _ in range(reflex.action.max_retries):
                    try:
                        result = handler(reflex.action.params, event)
                        execution.success = True
                        execution.result = result
                        reflex.success_count += 1
                        break
                    except Exception:
                        continue

        execution.completed_at = datetime.now()
        self._executions.append(execution)
        return execution

    def _handle_log(
        self,
        params: dict[str, Any],
        event: dict[str, Any]
    ) -> dict:
        """Built-in log handler"""
        message = params.get("message", "Event triggered")
        level = params.get("level", "info")
        return {
            "logged": True,
            "level": level,
            "message": message,
            "event": event.get("type", "unknown")
        }

    def _handle_notify(
        self,
        params: dict[str, Any],
        event: dict[str, Any]
    ) -> dict:
        """Built-in notify handler"""
        channel = params.get("channel", "default")
        message = params.get("message", f"Event: {event.get('type', 'unknown')}")
        return {
            "notified": True,
            "channel": channel,
            "message": message
        }

    def _handle_store(
        self,
        params: dict[str, Any],
        event: dict[str, Any]
    ) -> dict:
        """Built-in store handler"""
        key = params.get("key", f"event_{datetime.now().timestamp()}")
        return {
            "stored": True,
            "key": key,
            "event": event
        }

    def _handle_execute(
        self,
        params: dict[str, Any],
        event: dict[str, Any]
    ) -> dict:
        """Built-in execute handler"""
        command = params.get("command", "")
        return {
            "executed": True,
            "command": command,
            "event_type": event.get("type", "unknown")
        }

    def enable_reflex(self, reflex_id: str) -> bool:
        """Enable a reflex"""
        if reflex_id in self._reflexes:
            self._reflexes[reflex_id].enabled = True
            return True
        return False

    def disable_reflex(self, reflex_id: str) -> bool:
        """Disable a reflex"""
        if reflex_id in self._reflexes:
            self._reflexes[reflex_id].enabled = False
            return True
        return False

    def get_reflex(self, reflex_id: str) -> Reflex | None:
        """Get a reflex by ID"""
        return self._reflexes.get(reflex_id)

    def list_reflexes(
        self,
        category: ReflexCategory | None = None,
        enabled_only: bool = False
    ) -> list[Reflex]:
        """List reflexes with optional filtering"""
        reflexes = list(self._reflexes.values())

        if category:
            reflexes = [
                r for r in reflexes
                if r.trigger.category == category
            ]

        if enabled_only:
            reflexes = [r for r in reflexes if r.enabled]

        return reflexes

    def get_execution_history(
        self,
        reflex_id: str | None = None,
        limit: int = 50
    ) -> list[ReflexExecution]:
        """Get execution history"""
        executions = self._executions
        if reflex_id:
            executions = [
                e for e in executions
                if e.reflex_id == reflex_id
            ]
        return executions[-limit:]

    def analyze_reflexes(self) -> dict[str, Any]:
        """Analyze reflex performance"""
        total_reflexes = len(self._reflexes)
        enabled = len([r for r in self._reflexes.values() if r.enabled])
        total_executions = len(self._executions)
        successful = len([e for e in self._executions if e.success])

        by_category: dict[str, int] = {}
        for reflex in self._reflexes.values():
            cat = reflex.trigger.category.name
            by_category[cat] = by_category.get(cat, 0) + 1

        return {
            "total_reflexes": total_reflexes,
            "enabled_reflexes": enabled,
            "disabled_reflexes": total_reflexes - enabled,
            "total_executions": total_executions,
            "successful_executions": successful,
            "failed_executions": total_executions - successful,
            "success_rate": successful / total_executions if total_executions > 0 else 0,
            "by_category": by_category
        }

    def delete_reflex(self, reflex_id: str) -> bool:
        """Delete a reflex"""
        if reflex_id in self._reflexes:
            del self._reflexes[reflex_id]
            return True
        return False

    def _get_pattern_string(self, trigger: ReflexTrigger) -> str:
        """Extract pattern string from a trigger for export"""
        if isinstance(trigger.pattern, str):
            return trigger.pattern
        return trigger.pattern.pattern

    def export_reflexes(self) -> list[dict]:
        """Export all reflexes as dictionaries"""
        return [
            {
                "reflex_id": r.reflex_id,
                "name": r.name,
                "trigger_pattern": self._get_pattern_string(r.trigger),
                "trigger_category": r.trigger.category.name,
                "action_type": r.action.action_type,
                "action_params": r.action.params,
                "priority": r.priority.name,
                "enabled": r.enabled,
                "cooldown_seconds": r.cooldown_seconds,
                "execution_count": r.execution_count,
                "success_count": r.success_count
            }
            for r in self._reflexes.values()
        ]

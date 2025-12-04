"""
Data models for SovereignPRManager.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


def utcnow() -> datetime:
    """Get current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


class ReviewType(Enum):
    """Types of code review."""

    SECURITY = "security"
    ARCHITECTURE = "architecture"
    SOVEREIGNTY = "sovereignty"
    PERFORMANCE = "performance"


class Severity(Enum):
    """Severity levels for issues."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class MergeAction(Enum):
    """Possible merge actions."""

    MERGE = "merge"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"


@dataclass
class PRData:
    """Pull request data."""

    number: int
    title: str
    author: str
    created_at: datetime
    url: str
    diff_url: str
    head_sha: str
    base_branch: str = "main"
    is_draft: bool = False
    labels: list[str] = field(default_factory=list)


@dataclass
class ReviewResult:
    """Result of a single code review."""

    review_type: ReviewType
    severity: Severity
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    confidence: float = 0.0
    approve: bool = False
    timestamp: datetime = field(default_factory=utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "review_type": self.review_type.value,
            "severity": self.severity.value,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "confidence": self.confidence,
            "approve": self.approve,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ConflictResult:
    """Result of conflict detection."""

    has_conflicts: bool = False
    git_conflicts: list[str] = field(default_factory=list)
    semantic_conflicts: list[str] = field(default_factory=list)
    dependency_conflicts: list[str] = field(default_factory=list)
    can_auto_resolve: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "has_conflicts": self.has_conflicts,
            "git_conflicts": self.git_conflicts,
            "semantic_conflicts": self.semantic_conflicts,
            "dependency_conflicts": self.dependency_conflicts,
            "can_auto_resolve": self.can_auto_resolve,
        }


@dataclass
class MergeDecision:
    """Final merge decision with reasoning."""

    action: MergeAction
    confidence: float
    reasoning: str
    reviews: list[ReviewResult] = field(default_factory=list)
    conflicts: Optional[ConflictResult] = None
    timestamp: datetime = field(default_factory=utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "action": self.action.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "reviews": [r.to_dict() for r in self.reviews],
            "conflicts": self.conflicts.to_dict() if self.conflicts else None,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class MergeProvenance:
    """Provenance record for a merge operation."""

    pr_number: int
    pr_title: str
    decision: MergeDecision
    merged_by: str = "SovereignPRManager v1.0"
    git_sha: str = ""
    signature: str = ""
    timestamp: datetime = field(default_factory=utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "pr_number": self.pr_number,
            "pr_title": self.pr_title,
            "decision": self.decision.to_dict(),
            "merged_by": self.merged_by,
            "git_sha": self.git_sha,
            "signature": self.signature,
            "timestamp": self.timestamp.isoformat(),
        }

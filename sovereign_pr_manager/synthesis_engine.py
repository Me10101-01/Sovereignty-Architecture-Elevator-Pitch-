"""
Synthesis Engine: Dialectical synthesis for merge decisions.

Applies the dialectical method (thesis → antithesis → synthesis)
to combine multiple review results into a final merge decision.
"""

import logging
from typing import Optional

from .config import Config
from .models import (
    ConflictResult,
    MergeAction,
    MergeDecision,
    ReviewResult,
    ReviewType,
    Severity,
)

logger = logging.getLogger(__name__)

# Synthesis constants
SOVEREIGNTY_BONUS_THRESHOLD = 0.80  # Minimum sovereignty confidence for bonus
SOVEREIGNTY_BONUS_VALUE = 0.1  # Bonus added for high sovereignty compliance
CONFLICT_PENALTY_VALUE = 0.2  # Penalty for detected conflicts


class SynthesisEngine:
    """
    Synthesize Legion reviews into final merge decision.

    Uses dialectical synthesis to resolve contradictions between
    different review perspectives and produce a unified decision.
    """

    def __init__(self, config: Config):
        """Initialize the synthesis engine."""
        self.config = config
        self.thresholds = config.thresholds

    def synthesize(
        self,
        reviews: list[ReviewResult],
        conflicts: Optional[ConflictResult] = None,
    ) -> MergeDecision:
        """
        Apply dialectical synthesis to reach merge decision.

        The synthesis process:
        1. Extract contradictions from reviews
        2. Apply dialectical resolution
        3. Calculate final confidence
        4. Determine merge action

        Args:
            reviews: List of review results from different perspectives
            conflicts: Optional conflict detection results

        Returns:
            MergeDecision with action, confidence, and reasoning
        """
        # Check for blocking conditions first
        if conflicts and not conflicts.can_auto_resolve:
            return MergeDecision(
                action=MergeAction.BLOCKED,
                confidence=0.0,
                reasoning="Unresolvable conflicts detected",
                reviews=reviews,
                conflicts=conflicts,
            )

        # Check security veto
        security_review = self._get_review_by_type(reviews, ReviewType.SECURITY)
        if security_review and security_review.severity == Severity.CRITICAL:
            return MergeDecision(
                action=MergeAction.BLOCKED,
                confidence=security_review.confidence,
                reasoning="Critical security vulnerability detected",
                reviews=reviews,
                conflicts=conflicts,
            )

        # Calculate synthesis
        confidence = self._calculate_confidence(reviews, conflicts)
        contradictions = self._extract_contradictions(reviews)

        # Determine action based on confidence
        if confidence >= self.thresholds.auto_merge:
            action = MergeAction.MERGE
            reasoning = self._generate_merge_reasoning(reviews, confidence)
        else:
            action = MergeAction.REVIEW_REQUIRED
            reasoning = self._generate_review_reasoning(
                reviews, confidence, contradictions
            )

        return MergeDecision(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            reviews=reviews,
            conflicts=conflicts,
        )

    def _get_review_by_type(
        self, reviews: list[ReviewResult], review_type: ReviewType
    ) -> Optional[ReviewResult]:
        """Get a specific review by type."""
        for review in reviews:
            if review.review_type == review_type:
                return review
        return None

    def _calculate_confidence(
        self,
        reviews: list[ReviewResult],
        conflicts: Optional[ConflictResult],
    ) -> float:
        """
        Calculate merge confidence based on review consensus.

        Factors:
        - All reviews must approve
        - Average confidence across reviews
        - Penalty for conflicts
        - Bonus for sovereignty alignment
        """
        if not reviews:
            return 0.0

        # All reviews must approve for base confidence
        all_approve = all(r.approve for r in reviews)
        if not all_approve:
            # Reduce confidence significantly if any review rejects
            rejecting = [r for r in reviews if not r.approve]
            min_confidence = min(r.confidence for r in rejecting)
            return min_confidence * 0.5

        # Average confidence across reviews
        avg_confidence = sum(r.confidence for r in reviews) / len(reviews)

        # Penalty for conflicts
        conflict_penalty = 0.0
        if conflicts and conflicts.has_conflicts:
            conflict_penalty = CONFLICT_PENALTY_VALUE

        # Bonus for sovereignty alignment
        sovereignty_review = self._get_review_by_type(
            reviews, ReviewType.SOVEREIGNTY
        )
        sovereignty_bonus = 0.0
        if sovereignty_review and sovereignty_review.confidence > SOVEREIGNTY_BONUS_THRESHOLD:
            sovereignty_bonus = SOVEREIGNTY_BONUS_VALUE

        final_confidence = avg_confidence - conflict_penalty + sovereignty_bonus
        return max(0.0, min(1.0, final_confidence))

    def _extract_contradictions(
        self, reviews: list[ReviewResult]
    ) -> list[str]:
        """Extract contradictions between reviews."""
        contradictions = []

        # Check for approval contradictions
        approving = [r for r in reviews if r.approve]
        rejecting = [r for r in reviews if not r.approve]

        if approving and rejecting:
            for approve_review in approving:
                for reject_review in rejecting:
                    contradictions.append(
                        f"{approve_review.review_type.value} approves "
                        f"but {reject_review.review_type.value} rejects"
                    )

        # Check for severity contradictions
        severities = {r.review_type: r.severity for r in reviews}
        if Severity.CRITICAL in severities.values():
            if Severity.NONE in severities.values():
                contradictions.append(
                    "Critical and None severity ratings coexist"
                )

        return contradictions

    def _generate_merge_reasoning(
        self, reviews: list[ReviewResult], confidence: float
    ) -> str:
        """Generate reasoning for merge approval."""
        parts = [
            f"All {len(reviews)} review(s) approved",
            f"Confidence: {confidence:.1%}",
        ]

        # Add positive notes
        for review in reviews:
            if review.severity == Severity.NONE:
                parts.append(f"✓ {review.review_type.value}: No issues")

        return ". ".join(parts)

    def _generate_review_reasoning(
        self,
        reviews: list[ReviewResult],
        confidence: float,
        contradictions: list[str],
    ) -> str:
        """Generate reasoning for requiring human review."""
        parts = [f"Confidence ({confidence:.1%}) below threshold"]

        # Add issues found
        for review in reviews:
            if not review.approve:
                parts.append(
                    f"✗ {review.review_type.value}: {len(review.issues)} issue(s)"
                )

        if contradictions:
            parts.append(f"Contradictions: {len(contradictions)}")

        return ". ".join(parts)

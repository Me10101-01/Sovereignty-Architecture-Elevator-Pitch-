"""
Synthesis Engine - Dialectical synthesis for merge decisions.

Part of SovereignPRManager v1.0
Purpose: Synthesize Legion reviews into final merge decision
Philosophy: Dialectical reasoning for optimal decision-making
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class MergeDecision:
    """Final merge decision with reasoning."""

    action: str  # "merge", "review_required", "reject"
    confidence: float
    reasoning: str
    synthesis: dict[str, Any] = field(default_factory=dict)
    reviews_summary: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class DialecticalEngine:
    """
    Engine for dialectical synthesis of contradictory views.

    Implements thesis-antithesis-synthesis methodology for
    resolving conflicting code review opinions.
    """

    def synthesize(
        self,
        thesis: dict[str, Any],
        antithesis: dict[str, Any],
        context: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """
        Apply dialectical synthesis to opposing reviews.

        Args:
            thesis: Primary review perspective
            antithesis: Opposing review perspective
            context: Additional context (other reviews, conflicts)

        Returns:
            Synthesized perspective resolving contradictions
        """
        context = context or {}

        # Identify contradictions
        contradictions = self._find_contradictions(thesis, antithesis)

        # Resolve contradictions through synthesis
        resolutions = self._resolve_contradictions(contradictions, context)

        # Build synthesis
        synthesis = {
            "thesis_reviewer": thesis.get("reviewer", "unknown"),
            "antithesis_reviewer": antithesis.get("reviewer", "unknown"),
            "contradictions_found": len(contradictions),
            "contradictions_resolved": len(resolutions),
            "contradictions": contradictions,
            "resolutions": resolutions,
            "combined_issues": self._merge_issues(thesis, antithesis),
            "combined_recommendations": self._merge_recommendations(thesis, antithesis),
            "overall_approve": self._synthesize_approval(thesis, antithesis, context),
            "combined_confidence": self._calculate_combined_confidence(
                thesis, antithesis
            ),
            "timestamp": datetime.utcnow().isoformat(),
        }

        return synthesis

    def _find_contradictions(
        self, thesis: dict[str, Any], antithesis: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Find contradictions between two review perspectives."""
        contradictions = []

        # Check for approval contradiction
        thesis_approve = thesis.get("approve", False)
        antithesis_approve = antithesis.get("approve", False)

        if thesis_approve != antithesis_approve:
            contradictions.append({
                "type": "approval_conflict",
                "thesis": f"{thesis.get('reviewer')}: approve={thesis_approve}",
                "antithesis": f"{antithesis.get('reviewer')}: approve={antithesis_approve}",
                "weight": 1.0,
            })

        # Check for severity contradiction
        thesis_severity = thesis.get("severity", "none")
        antithesis_severity = antithesis.get("severity", "none")
        severity_levels = ["none", "low", "medium", "high", "critical"]

        if thesis_severity != antithesis_severity:
            thesis_level = severity_levels.index(thesis_severity) if thesis_severity in severity_levels else 0
            antithesis_level = severity_levels.index(antithesis_severity) if antithesis_severity in severity_levels else 0

            if abs(thesis_level - antithesis_level) >= 2:
                contradictions.append({
                    "type": "severity_conflict",
                    "thesis": f"{thesis.get('reviewer')}: severity={thesis_severity}",
                    "antithesis": f"{antithesis.get('reviewer')}: severity={antithesis_severity}",
                    "weight": 0.5,
                })

        # Check for confidence disparity
        thesis_conf = thesis.get("confidence", 0.0)
        antithesis_conf = antithesis.get("confidence", 0.0)

        if abs(thesis_conf - antithesis_conf) > 0.4:
            contradictions.append({
                "type": "confidence_disparity",
                "thesis": f"{thesis.get('reviewer')}: confidence={thesis_conf:.2f}",
                "antithesis": f"{antithesis.get('reviewer')}: confidence={antithesis_conf:.2f}",
                "weight": 0.3,
            })

        return contradictions

    def _resolve_contradictions(
        self, contradictions: list[dict[str, Any]], context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Resolve contradictions through synthesis logic."""
        resolutions = []

        for contradiction in contradictions:
            if contradiction["type"] == "approval_conflict":
                # Security veto: if security review disapproves, follow it
                if "security" in contradiction["thesis"].lower():
                    resolutions.append({
                        "contradiction": contradiction,
                        "resolution": "Security review takes precedence",
                        "decision": "Follow thesis (security veto)",
                    })
                elif "security" in contradiction["antithesis"].lower():
                    resolutions.append({
                        "contradiction": contradiction,
                        "resolution": "Security review takes precedence",
                        "decision": "Follow antithesis (security veto)",
                    })
                else:
                    # Default: require human review for approval conflicts
                    resolutions.append({
                        "contradiction": contradiction,
                        "resolution": "Approval conflict requires human review",
                        "decision": "Escalate to human",
                    })

            elif contradiction["type"] == "severity_conflict":
                # Take the higher severity
                resolutions.append({
                    "contradiction": contradiction,
                    "resolution": "Apply precautionary principle",
                    "decision": "Use higher severity rating",
                })

            elif contradiction["type"] == "confidence_disparity":
                # Weight by confidence
                resolutions.append({
                    "contradiction": contradiction,
                    "resolution": "Weight by confidence levels",
                    "decision": "Prefer higher-confidence review",
                })

        return resolutions

    def _merge_issues(
        self, thesis: dict[str, Any], antithesis: dict[str, Any]
    ) -> list[str]:
        """Merge issues from both reviews, removing duplicates."""
        thesis_issues = set(thesis.get("issues", []))
        antithesis_issues = set(antithesis.get("issues", []))
        return list(thesis_issues | antithesis_issues)

    def _merge_recommendations(
        self, thesis: dict[str, Any], antithesis: dict[str, Any]
    ) -> list[str]:
        """Merge recommendations from both reviews."""
        thesis_recs = set(thesis.get("recommendations", []))
        antithesis_recs = set(antithesis.get("recommendations", []))
        return list(thesis_recs | antithesis_recs)

    def _synthesize_approval(
        self,
        thesis: dict[str, Any],
        antithesis: dict[str, Any],
        context: dict[str, Any],
    ) -> bool:
        """
        Synthesize final approval decision.

        Logic:
        - If any security review disapproves: reject
        - If all reviews approve: approve
        - Otherwise: require human review (treated as non-approval)
        """
        thesis_approve = thesis.get("approve", False)
        antithesis_approve = antithesis.get("approve", False)

        # Check for security veto
        if "security" in thesis.get("category", "").lower():
            if not thesis_approve:
                return False

        if "security" in antithesis.get("category", "").lower():
            if not antithesis_approve:
                return False

        # Check additional reviews in context
        for review in context.get("additional_reviews", []):
            if "security" in review.get("category", "").lower():
                if not review.get("approve", False):
                    return False

        # All must approve
        return thesis_approve and antithesis_approve

    def _calculate_combined_confidence(
        self, thesis: dict[str, Any], antithesis: dict[str, Any]
    ) -> float:
        """Calculate combined confidence score."""
        thesis_conf = thesis.get("confidence", 0.0)
        antithesis_conf = antithesis.get("confidence", 0.0)

        # Geometric mean to penalize low confidence
        if thesis_conf > 0 and antithesis_conf > 0:
            return (thesis_conf * antithesis_conf) ** 0.5
        return (thesis_conf + antithesis_conf) / 2


class MergeDecisionEngine:
    """Synthesize Legion reviews into final merge decision."""

    def __init__(
        self,
        auto_merge_threshold: float = 0.90,
        security_veto_threshold: float = 0.80,
        sovereignty_minimum: float = 0.70,
    ):
        """
        Initialize Merge Decision Engine.

        Args:
            auto_merge_threshold: Minimum confidence for auto-merge (default 90%)
            security_veto_threshold: Security confidence below this vetoes merge
            sovereignty_minimum: Minimum sovereignty score required
        """
        self.dialectical = DialecticalEngine()
        self.auto_merge_threshold = auto_merge_threshold
        self.security_veto_threshold = security_veto_threshold
        self.sovereignty_minimum = sovereignty_minimum

    def synthesize(
        self,
        reviews: list[dict[str, Any]],
        conflicts: dict[str, Any] = None,
    ) -> MergeDecision:
        """
        Synthesize all reviews into final merge decision.

        Args:
            reviews: List of review results from Legion reviewers
            conflicts: Conflict detection results

        Returns:
            MergeDecision with action, confidence, and reasoning
        """
        conflicts = conflicts or {}

        if not reviews:
            return MergeDecision(
                action="review_required",
                confidence=0.0,
                reasoning="No reviews available",
            )

        # Group reviews by category
        categorized_reviews = self._categorize_reviews(reviews)

        # Apply dialectical synthesis between security and architecture
        synthesis = None
        if (
            categorized_reviews.get("security")
            and categorized_reviews.get("architecture")
        ):
            synthesis = self.dialectical.synthesize(
                thesis=categorized_reviews["security"][0],
                antithesis=categorized_reviews["architecture"][0],
                context={
                    "sovereignty_review": categorized_reviews.get("sovereignty", [{}])[0],
                    "performance_review": categorized_reviews.get("performance", [{}])[0],
                    "conflicts": conflicts,
                },
            )

        # Calculate confidence score
        confidence = self._calculate_confidence(reviews, synthesis, conflicts)

        # Check for automatic vetoes
        vetoes = self._check_vetoes(reviews, categorized_reviews, conflicts)

        # Determine action
        if vetoes:
            action = "reject"
            reasoning = f"Vetoed: {'; '.join(vetoes)}"
        elif confidence >= self.auto_merge_threshold:
            action = "merge"
            reasoning = self._generate_approval_reasoning(reviews, confidence)
        else:
            action = "review_required"
            reasoning = self._generate_review_reasoning(reviews, confidence)

        return MergeDecision(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            synthesis=synthesis or {},
            reviews_summary={
                "total_reviews": len(reviews),
                "all_approve": all(r.get("approve", False) for r in reviews),
                "categories_reviewed": list(categorized_reviews.keys()),
                "total_issues": sum(len(r.get("issues", [])) for r in reviews),
            },
        )

    def _categorize_reviews(
        self, reviews: list[dict[str, Any]]
    ) -> dict[str, list[dict[str, Any]]]:
        """Group reviews by category."""
        categorized: dict[str, list[dict[str, Any]]] = {}

        for review in reviews:
            category = review.get("category", "other")
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(review)

        return categorized

    def _calculate_confidence(
        self,
        reviews: list[dict[str, Any]],
        synthesis: dict[str, Any] = None,
        conflicts: dict[str, Any] = None,
    ) -> float:
        """Calculate overall merge confidence."""
        if not reviews:
            return 0.0

        # All reviews must approve
        all_approve = all(r.get("approve", False) for r in reviews)
        if not all_approve:
            return 0.0

        # Average confidence across reviews
        confidences = [r.get("confidence", 0.0) for r in reviews]
        avg_confidence = sum(confidences) / len(confidences)

        # Conflict penalty
        conflict_penalty = 0.0
        if conflicts:
            if conflicts.get("has_conflicts"):
                conflict_penalty = 0.2
                if not conflicts.get("can_auto_resolve"):
                    conflict_penalty = 0.4

        # Sovereignty bonus
        sovereignty_bonus = 0.0
        for review in reviews:
            if review.get("category") == "sovereignty":
                sovereignty_score = review.get("details", {}).get("sovereignty_score", 0.0)
                if sovereignty_score > 0.8:
                    sovereignty_bonus = 0.05

        # Synthesis penalty for unresolved contradictions
        synthesis_penalty = 0.0
        if synthesis:
            unresolved = synthesis.get("contradictions_found", 0) - synthesis.get(
                "contradictions_resolved", 0
            )
            synthesis_penalty = unresolved * 0.1

        final_confidence = max(
            0.0,
            min(
                1.0,
                avg_confidence - conflict_penalty + sovereignty_bonus - synthesis_penalty,
            ),
        )

        return final_confidence

    def _check_vetoes(
        self,
        reviews: list[dict[str, Any]],
        categorized_reviews: dict[str, list[dict[str, Any]]],
        conflicts: dict[str, Any],
    ) -> list[str]:
        """Check for conditions that automatically veto merge."""
        vetoes = []

        # Security veto
        for review in categorized_reviews.get("security", []):
            if review.get("severity") in ["critical", "high"]:
                vetoes.append(f"Security: {review.get('severity')} severity issues found")
            if review.get("confidence", 1.0) < self.security_veto_threshold:
                vetoes.append(
                    f"Security review confidence too low: {review.get('confidence', 0):.2%}"
                )

        # Sovereignty minimum
        for review in categorized_reviews.get("sovereignty", []):
            sovereignty_score = review.get("details", {}).get("sovereignty_score", 1.0)
            if sovereignty_score < self.sovereignty_minimum:
                vetoes.append(
                    f"Sovereignty score below minimum: {sovereignty_score:.2%}"
                )

        # Unresolvable conflicts
        if conflicts.get("has_conflicts") and not conflicts.get("can_auto_resolve"):
            vetoes.append("Unresolvable conflicts detected")

        # Git conflicts
        if conflicts.get("git_conflicts"):
            vetoes.append(f"Git merge conflicts in: {', '.join(conflicts['git_conflicts'])}")

        return vetoes

    def _generate_approval_reasoning(
        self, reviews: list[dict[str, Any]], confidence: float
    ) -> str:
        """Generate reasoning for approval decision."""
        parts = [
            f"Confidence: {confidence:.1%}",
            f"Reviews: {len(reviews)} AI agents all approved",
        ]

        # Add category-specific highlights
        for review in reviews:
            category = review.get("category", "other")
            score_key = f"{category}_score"
            if review.get("details", {}).get(score_key):
                parts.append(
                    f"{category.title()}: {review['details'][score_key]:.1%}"
                )

        return " | ".join(parts)

    def _generate_review_reasoning(
        self, reviews: list[dict[str, Any]], confidence: float
    ) -> str:
        """Generate reasoning for requiring human review."""
        parts = [f"Confidence: {confidence:.1%} (below {self.auto_merge_threshold:.1%} threshold)"]

        # List issues requiring attention
        all_issues = []
        for review in reviews:
            all_issues.extend(review.get("issues", []))

        if all_issues:
            parts.append(f"Issues: {len(all_issues)} items require attention")

        # Note non-approvals
        non_approvals = [r for r in reviews if not r.get("approve", False)]
        if non_approvals:
            reviewers = [r.get("reviewer", "Unknown") for r in non_approvals]
            parts.append(f"Non-approvals from: {', '.join(reviewers)}")

        return " | ".join(parts)


def main():
    """Test the Synthesis Engine."""
    logging.basicConfig(level=logging.INFO)

    engine = MergeDecisionEngine()

    # Example reviews
    reviews = [
        {
            "reviewer": "Claude Security Reviewer",
            "category": "security",
            "severity": "none",
            "issues": [],
            "recommendations": ["Consider adding rate limiting"],
            "confidence": 0.92,
            "approve": True,
        },
        {
            "reviewer": "GPT Architecture Reviewer",
            "category": "architecture",
            "severity": "low",
            "issues": ["Consider using dependency injection"],
            "recommendations": ["Refactor for better testability"],
            "confidence": 0.88,
            "approve": True,
            "details": {"architecture_score": 0.85},
        },
        {
            "reviewer": "Claude Sovereignty Reviewer",
            "category": "sovereignty",
            "severity": "none",
            "issues": [],
            "recommendations": [],
            "confidence": 0.95,
            "approve": True,
            "details": {"sovereignty_score": 0.90},
        },
        {
            "reviewer": "GPT Performance Reviewer",
            "category": "performance",
            "severity": "none",
            "issues": [],
            "recommendations": ["Consider caching for repeated queries"],
            "confidence": 0.90,
            "approve": True,
            "details": {"performance_score": 0.88},
        },
    ]

    conflicts = {"has_conflicts": False, "can_auto_resolve": True}

    decision = engine.synthesize(reviews, conflicts)

    print(f"Action: {decision.action}")
    print(f"Confidence: {decision.confidence:.2%}")
    print(f"Reasoning: {decision.reasoning}")
    print(f"Reviews summary: {decision.reviews_summary}")


if __name__ == "__main__":
    main()

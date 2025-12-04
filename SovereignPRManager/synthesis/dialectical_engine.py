"""
Dialectical Synthesis Engine - Synthesizes multiple review perspectives
Author: SovereignPRManager Legion
"""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Any

from ..core.config import SovereignPRManagerConfig

logger = logging.getLogger(__name__)


# Named constants
THESIS_WEIGHT = 0.4
ANTITHESIS_WEIGHT = 0.3
SYNTHESIS_WEIGHT = 0.3


class DialecticalEngine:
    """
    Synthesizes multiple review perspectives using dialectical reasoning.
    
    The engine applies Hegelian dialectics to code review:
    - Thesis: Primary review findings (what the code does)
    - Antithesis: Counter-perspectives and concerns (what could go wrong)
    - Synthesis: Unified decision (what action to take)
    """
    
    def __init__(self, config: SovereignPRManagerConfig):
        """Initialize Dialectical Engine with configuration."""
        self.config = config
    
    def synthesize(self, reviews: list[dict]) -> dict:
        """
        Synthesize multiple review perspectives into a final decision.
        
        Args:
            reviews: List of review dictionaries from different reviewers
            
        Returns:
            Synthesis result with final decision and reasoning
        """
        if not reviews:
            return self._create_empty_synthesis()
        
        # Phase 1: Extract thesis (primary findings)
        thesis = self._extract_thesis(reviews)
        
        # Phase 2: Generate antithesis (concerns and counter-arguments)
        antithesis = self._extract_antithesis(reviews)
        
        # Phase 3: Synthesize final decision
        synthesis = self._synthesize_decision(thesis, antithesis, reviews)
        
        now = datetime.now(timezone.utc)
        return {
            "thesis": thesis,
            "antithesis": antithesis,
            "synthesis": synthesis,
            "final_decision": synthesis.get("decision", "review"),
            "confidence": synthesis.get("confidence", 0.0),
            "reasoning": synthesis.get("reasoning", ""),
            "timestamp": now.isoformat()
        }
    
    def _create_empty_synthesis(self) -> dict:
        """Create an empty synthesis result when no reviews are available."""
        now = datetime.now(timezone.utc)
        return {
            "thesis": {},
            "antithesis": {},
            "synthesis": {},
            "final_decision": "review",
            "confidence": 0.0,
            "reasoning": "No reviews available for synthesis",
            "timestamp": now.isoformat()
        }
    
    def _extract_thesis(self, reviews: list[dict]) -> dict:
        """Extract primary findings (thesis) from reviews."""
        approvals = []
        recommendations = []
        
        for review in reviews:
            if review.get("approve", False):
                approvals.append(review.get("reviewer", "Unknown"))
            
            # Collect recommendations from various review types
            recs = review.get("recommendations", [])
            if isinstance(recs, list):
                recommendations.extend(recs)
            
            enhancements = review.get("enhancements", [])
            if isinstance(enhancements, list):
                recommendations.extend(enhancements)
            
            suggestions = review.get("suggestions", [])
            if isinstance(suggestions, list):
                recommendations.extend(suggestions)
        
        return {
            "approvals": approvals,
            "approval_count": len(approvals),
            "total_reviews": len(reviews),
            "recommendations": list(set(recommendations))
        }
    
    def _extract_antithesis(self, reviews: list[dict]) -> dict:
        """Extract concerns and counter-arguments (antithesis) from reviews."""
        concerns = []
        vulnerabilities = []
        violations = []
        
        for review in reviews:
            # Collect vulnerabilities
            vulns = review.get("vulnerabilities", [])
            if isinstance(vulns, list):
                vulnerabilities.extend(vulns)
            
            # Collect violations
            viols = review.get("violations", [])
            if isinstance(viols, list):
                violations.extend(viols)
            
            # Collect concerns
            cncns = review.get("concerns", [])
            if isinstance(cncns, list):
                concerns.extend(cncns)
            
            # Non-approvals are concerns
            if not review.get("approve", False):
                reasoning = review.get("reasoning", "")
                if reasoning:
                    concerns.append(
                        f"{review.get('reviewer', 'Unknown')}: {reasoning}"
                    )
        
        return {
            "concerns": list(set(concerns)),
            "vulnerabilities": list(set(vulnerabilities)),
            "violations": list(set(violations)),
            "has_blockers": len(vulnerabilities) > 0 or len(violations) > 0
        }
    
    def _synthesize_decision(
        self, 
        thesis: dict, 
        antithesis: dict, 
        reviews: list[dict]
    ) -> dict:
        """Synthesize final decision from thesis and antithesis."""
        # Calculate approval rate
        total = thesis.get("total_reviews", 0)
        approvals = thesis.get("approval_count", 0)
        
        if total == 0:
            return {
                "decision": "review",
                "confidence": 0.0,
                "reasoning": "No reviews to synthesize"
            }
        
        approval_rate = approvals / total
        
        # Check for blockers
        has_blockers = antithesis.get("has_blockers", False)
        vulnerabilities = antithesis.get("vulnerabilities", [])
        
        # Calculate aggregate confidence from reviews
        confidences = [r.get("confidence", 0.5) for r in reviews]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Decision logic
        if has_blockers:
            return {
                "decision": "block",
                "confidence": 0.9,
                "reasoning": (
                    f"Blocked due to {len(vulnerabilities)} vulnerabilities "
                    "or violations"
                )
            }
        
        threshold = self.config.confidence_threshold
        
        if approval_rate >= 0.8 and avg_confidence >= threshold:
            return {
                "decision": "approve",
                "confidence": avg_confidence,
                "reasoning": (
                    f"All criteria met: {approval_rate:.0%} approval rate, "
                    f"{avg_confidence:.0%} confidence"
                )
            }
        
        if approval_rate >= 0.5:
            return {
                "decision": "review",
                "confidence": avg_confidence,
                "reasoning": (
                    f"Partial approval: {approval_rate:.0%} approval rate. "
                    "Manual review recommended."
                )
            }
        
        return {
            "decision": "reject",
            "confidence": avg_confidence,
            "reasoning": (
                f"Low approval rate: {approval_rate:.0%}. "
                "Significant concerns raised."
            )
        }
    
    def generate_provenance(self, synthesis: dict, pr_number: int) -> dict:
        """Generate cryptographic provenance for the synthesis decision."""
        now = datetime.now(timezone.utc)
        
        # Create deterministic hash of the synthesis
        content = f"{pr_number}:{synthesis.get('final_decision', '')}:"
        content += f"{synthesis.get('timestamp', '')}:"
        content += f"{synthesis.get('confidence', 0)}"
        
        # Use full SHA-256 hash for cryptographic integrity
        hash_value = hashlib.sha256(content.encode()).hexdigest()
        
        return {
            "pr_number": pr_number,
            "decision": synthesis.get("final_decision", "review"),
            "confidence": synthesis.get("confidence", 0.0),
            "hash": hash_value,
            "algorithm": "sha256",
            "timestamp": now.isoformat(),
            "reasoning": synthesis.get("reasoning", "")
        }

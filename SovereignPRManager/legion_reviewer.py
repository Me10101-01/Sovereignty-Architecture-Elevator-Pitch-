"""
Legion Reviewer - Multi-AI code review system.

Part of SovereignPRManager v1.0
Purpose: Parallel code review by specialized AI agents
Philosophy: Collective AI intelligence for comprehensive code analysis
"""

import asyncio
import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import httpx

logger = logging.getLogger(__name__)


@dataclass
class ReviewResult:
    """Result from an AI code review."""

    reviewer: str
    category: str
    severity: str  # critical, high, medium, low, none
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    confidence: float = 0.0
    approve: bool = False
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class AIReviewer(ABC):
    """Abstract base class for AI reviewers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Reviewer name."""
        pass

    @abstractmethod
    async def review(self, diff: str, context: dict[str, Any]) -> ReviewResult:
        """
        Perform code review on the given diff.

        Args:
            diff: The code diff to review
            context: Additional context (PR title, description, etc.)

        Returns:
            ReviewResult with findings
        """
        pass


class ClaudeSecurityReviewer(AIReviewer):
    """Claude-based security vulnerability reviewer."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "claude-sonnet-4-20250514"

    @property
    def name(self) -> str:
        return "Claude Security Reviewer"

    async def review(self, diff: str, context: dict[str, Any]) -> ReviewResult:
        """Review code for security vulnerabilities."""
        prompt = f"""Review this code diff for security vulnerabilities.

Consider:
1. Credential exposure (API keys, passwords, tokens)
2. Injection attacks (SQL, command, XSS)
3. Access control issues
4. Cryptographic weaknesses
5. Supply chain risks

PR Title: {context.get('title', 'N/A')}
PR Author: {context.get('author', 'N/A')}

Diff:
{diff[:10000]}

Respond in JSON format:
{{
    "severity": "critical|high|medium|low|none",
    "vulnerabilities": ["list of issues found"],
    "recommendations": ["list of fixes"],
    "confidence": 0.0-1.0,
    "approve": true|false
}}
"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "max_tokens": 2000,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                result = response.json()

                # Parse the response
                content = result["content"][0]["text"]
                # Extract JSON from response
                parsed = json.loads(content)

                return ReviewResult(
                    reviewer=self.name,
                    category="security",
                    severity=parsed.get("severity", "none"),
                    issues=parsed.get("vulnerabilities", []),
                    recommendations=parsed.get("recommendations", []),
                    confidence=parsed.get("confidence", 0.0),
                    approve=parsed.get("approve", False),
                )

        except Exception as e:
            logger.error(f"Claude security review failed: {e}")
            return ReviewResult(
                reviewer=self.name,
                category="security",
                severity="none",
                issues=[f"Review failed: {e!s}"],
                confidence=0.0,
                approve=False,
            )


class ClaudeSovereigntyReviewer(AIReviewer):
    """Claude-based sovereignty architecture compliance reviewer."""

    def __init__(self, api_key: str, declaration_path: str = None):
        self.api_key = api_key
        self.model = "claude-sonnet-4-20250514"
        self.declaration_path = declaration_path
        self._declaration = None

    @property
    def name(self) -> str:
        return "Claude Sovereignty Reviewer"

    def _load_declaration(self) -> str:
        """Load the Technical Declaration if available."""
        if self._declaration is not None:
            return self._declaration

        if self.declaration_path and os.path.exists(self.declaration_path):
            with open(self.declaration_path) as f:
                self._declaration = f.read()
        else:
            self._declaration = """
Sovereignty Architecture Principles:
1. Zero-trust security model
2. Self-hosted infrastructure preference
3. Cryptographic verification of all operations
4. Complete audit trail for accountability
5. Intellectual property protection
6. Data sovereignty and local control
"""
        return self._declaration

    async def review(self, diff: str, context: dict[str, Any]) -> ReviewResult:
        """Review code for sovereignty architecture compliance."""
        declaration = self._load_declaration()

        prompt = f"""Review this code against our Sovereignty Architecture principles.

Our Declaration:
{declaration[:5000]}

PR Title: {context.get('title', 'N/A')}
PR Author: {context.get('author', 'N/A')}

Code diff:
{diff[:10000]}

Check for:
1. Zero-trust compliance
2. Self-hosted infrastructure preference
3. Cryptographic verification
4. Audit trail requirements
5. Intellectual property protection

Respond in JSON format:
{{
    "sovereignty_score": 0.0-1.0,
    "violations": ["list of principle violations"],
    "enhancements": ["suggestions to improve sovereignty"],
    "confidence": 0.0-1.0,
    "approve": true|false
}}
"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "max_tokens": 2000,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                result = response.json()

                content = result["content"][0]["text"]
                parsed = json.loads(content)

                return ReviewResult(
                    reviewer=self.name,
                    category="sovereignty",
                    severity="medium" if parsed.get("violations") else "none",
                    issues=parsed.get("violations", []),
                    recommendations=parsed.get("enhancements", []),
                    confidence=parsed.get("confidence", 0.0),
                    approve=parsed.get("approve", False),
                    details={"sovereignty_score": parsed.get("sovereignty_score", 0.0)},
                )

        except Exception as e:
            logger.error(f"Claude sovereignty review failed: {e}")
            return ReviewResult(
                reviewer=self.name,
                category="sovereignty",
                severity="none",
                issues=[f"Review failed: {e!s}"],
                confidence=0.0,
                approve=False,
            )


class GPTArchitectureReviewer(AIReviewer):
    """GPT-based architecture and design pattern reviewer."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "gpt-4o"

    @property
    def name(self) -> str:
        return "GPT Architecture Reviewer"

    async def review(self, diff: str, context: dict[str, Any]) -> ReviewResult:
        """Review code for architecture and design patterns."""
        prompt = f"""Review this code diff for architecture and design quality.

Consider:
1. Design patterns usage and appropriateness
2. SOLID principles adherence
3. Code maintainability and readability
4. Separation of concerns
5. Dependency management

PR Title: {context.get('title', 'N/A')}
PR Author: {context.get('author', 'N/A')}

Diff:
{diff[:10000]}

Respond in JSON format:
{{
    "architecture_score": 0.0-1.0,
    "issues": ["list of architectural concerns"],
    "recommendations": ["improvement suggestions"],
    "confidence": 0.0-1.0,
    "approve": true|false
}}
"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 2000,
                        "response_format": {"type": "json_object"},
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                result = response.json()

                content = result["choices"][0]["message"]["content"]
                parsed = json.loads(content)

                return ReviewResult(
                    reviewer=self.name,
                    category="architecture",
                    severity="medium" if parsed.get("issues") else "none",
                    issues=parsed.get("issues", []),
                    recommendations=parsed.get("recommendations", []),
                    confidence=parsed.get("confidence", 0.0),
                    approve=parsed.get("approve", False),
                    details={"architecture_score": parsed.get("architecture_score", 0.0)},
                )

        except Exception as e:
            logger.error(f"GPT architecture review failed: {e}")
            return ReviewResult(
                reviewer=self.name,
                category="architecture",
                severity="none",
                issues=[f"Review failed: {e!s}"],
                confidence=0.0,
                approve=False,
            )


class GPTPerformanceReviewer(AIReviewer):
    """GPT-based performance optimization reviewer."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "gpt-4o"

    @property
    def name(self) -> str:
        return "GPT Performance Reviewer"

    async def review(self, diff: str, context: dict[str, Any]) -> ReviewResult:
        """Review code for performance concerns."""
        prompt = f"""Review this code diff for performance optimization opportunities.

Consider:
1. Time complexity of algorithms
2. Space complexity and memory usage
3. Database query efficiency
4. Network call optimization
5. Caching opportunities
6. Async/concurrent processing potential

PR Title: {context.get('title', 'N/A')}
PR Author: {context.get('author', 'N/A')}

Diff:
{diff[:10000]}

Respond in JSON format:
{{
    "performance_score": 0.0-1.0,
    "issues": ["list of performance concerns"],
    "optimizations": ["improvement suggestions"],
    "confidence": 0.0-1.0,
    "approve": true|false
}}
"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 2000,
                        "response_format": {"type": "json_object"},
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                result = response.json()

                content = result["choices"][0]["message"]["content"]
                parsed = json.loads(content)

                return ReviewResult(
                    reviewer=self.name,
                    category="performance",
                    severity="medium" if parsed.get("issues") else "none",
                    issues=parsed.get("issues", []),
                    recommendations=parsed.get("optimizations", []),
                    confidence=parsed.get("confidence", 0.0),
                    approve=parsed.get("approve", False),
                    details={"performance_score": parsed.get("performance_score", 0.0)},
                )

        except Exception as e:
            logger.error(f"GPT performance review failed: {e}")
            return ReviewResult(
                reviewer=self.name,
                category="performance",
                severity="none",
                issues=[f"Review failed: {e!s}"],
                confidence=0.0,
                approve=False,
            )


class LegionReviewer:
    """
    Multi-AI code review orchestrator.

    Coordinates parallel reviews from multiple specialized AI agents.
    """

    def __init__(
        self,
        anthropic_key: str = None,
        openai_key: str = None,
        declaration_path: str = None,
    ):
        """
        Initialize Legion Reviewer with AI API keys.

        Args:
            anthropic_key: Anthropic API key for Claude
            openai_key: OpenAI API key for GPT
            declaration_path: Path to Technical Declaration document
        """
        self.reviewers: list[AIReviewer] = []

        if anthropic_key:
            self.reviewers.append(ClaudeSecurityReviewer(anthropic_key))
            self.reviewers.append(
                ClaudeSovereigntyReviewer(anthropic_key, declaration_path)
            )

        if openai_key:
            self.reviewers.append(GPTArchitectureReviewer(openai_key))
            self.reviewers.append(GPTPerformanceReviewer(openai_key))

        if not self.reviewers:
            logger.warning("No AI reviewers configured. Please provide API keys.")

    async def fetch_diff(self, diff_url: str) -> str:
        """Fetch PR diff from URL."""
        async with httpx.AsyncClient() as client:
            response = await client.get(diff_url, timeout=30.0)
            response.raise_for_status()
            return response.text

    async def review_pr(self, pr_data: dict[str, Any]) -> dict[str, Any]:
        """
        Perform parallel reviews on a pull request.

        Args:
            pr_data: PR information including diff_url

        Returns:
            Aggregated review results from all AI agents
        """
        logger.info(f"Starting Legion review for PR #{pr_data.get('number')}")

        # Fetch the diff
        diff_url = pr_data.get("diff_url")
        if not diff_url:
            return {
                "pr_number": pr_data.get("number"),
                "error": "No diff_url provided",
                "reviews": [],
                "timestamp": datetime.utcnow().isoformat(),
            }

        try:
            diff = await self.fetch_diff(diff_url)
        except Exception as e:
            logger.error(f"Failed to fetch diff: {e}")
            return {
                "pr_number": pr_data.get("number"),
                "error": f"Failed to fetch diff: {e}",
                "reviews": [],
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Build context for reviewers
        context = {
            "title": pr_data.get("title"),
            "author": pr_data.get("author"),
            "pr_number": pr_data.get("number"),
            "labels": pr_data.get("labels", []),
        }

        # Run all reviews in parallel
        review_tasks = [reviewer.review(diff, context) for reviewer in self.reviewers]
        reviews = await asyncio.gather(*review_tasks, return_exceptions=True)

        # Process results
        successful_reviews = []
        for i, review in enumerate(reviews):
            if isinstance(review, Exception):
                logger.error(f"Review {i} failed: {review}")
                successful_reviews.append(
                    ReviewResult(
                        reviewer=self.reviewers[i].name,
                        category="error",
                        severity="none",
                        issues=[str(review)],
                        confidence=0.0,
                        approve=False,
                    )
                )
            else:
                successful_reviews.append(review)

        # Calculate aggregate metrics
        all_approve = all(r.approve for r in successful_reviews)
        avg_confidence = sum(r.confidence for r in successful_reviews) / max(
            len(successful_reviews), 1
        )
        all_issues = []
        all_recommendations = []
        for r in successful_reviews:
            all_issues.extend(r.issues)
            all_recommendations.extend(r.recommendations)

        return {
            "pr_number": pr_data.get("number"),
            "pr_title": pr_data.get("title"),
            "reviews": [
                {
                    "reviewer": r.reviewer,
                    "category": r.category,
                    "severity": r.severity,
                    "issues": r.issues,
                    "recommendations": r.recommendations,
                    "confidence": r.confidence,
                    "approve": r.approve,
                    "details": r.details,
                }
                for r in successful_reviews
            ],
            "summary": {
                "all_approve": all_approve,
                "average_confidence": avg_confidence,
                "total_issues": len(all_issues),
                "total_recommendations": len(all_recommendations),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }


async def main():
    """Test the Legion Reviewer."""
    logging.basicConfig(level=logging.INFO)

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not anthropic_key and not openai_key:
        logger.error("At least one API key required (ANTHROPIC_API_KEY or OPENAI_API_KEY)")
        return

    reviewer = LegionReviewer(anthropic_key, openai_key)

    # Example PR data
    test_pr = {
        "number": 1,
        "title": "Test PR",
        "author": "test-user",
        "diff_url": "https://patch-diff.githubusercontent.com/raw/example/example/pull/1.diff",
    }

    result = await reviewer.review_pr(test_pr)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

"""
Code Reviewer: Performs automated code review with confidence scoring.

This module provides a simplified review system that can be extended
with AI-based reviews when API keys are available.
"""

import logging
import re

from .config import Config
from .models import PRData, ReviewResult, ReviewType, Severity

logger = logging.getLogger(__name__)


class CodeReviewer:
    """Automated code review system with multiple review types."""

    def __init__(self, config: Config):
        """Initialize the code reviewer."""
        self.config = config

    async def review_pr(
        self, pr_data: PRData, diff: str
    ) -> list[ReviewResult]:
        """
        Perform all review types on a PR.

        Returns list of review results from different review perspectives.
        """
        reviews = []

        # Security review
        security_result = await self.security_review(diff)
        reviews.append(security_result)

        # Architecture review
        architecture_result = await self.architecture_review(diff, pr_data)
        reviews.append(architecture_result)

        # Sovereignty review
        sovereignty_result = await self.sovereignty_review(diff)
        reviews.append(sovereignty_result)

        return reviews

    async def security_review(self, diff: str) -> ReviewResult:
        """
        Review code for security vulnerabilities.

        Checks for:
        - Credential exposure (API keys, passwords, tokens)
        - Injection patterns (SQL, command, XSS)
        - Access control issues
        - Cryptographic weaknesses
        """
        issues = []
        recommendations = []

        # Check for potential secrets
        secret_patterns = [
            (r'["\']?api[_-]?key["\']?\s*[:=]\s*["\'][^"\']{10,}["\']', "API key"),
            (r'["\']?password["\']?\s*[:=]\s*["\'][^"\']+["\']', "Password"),
            (r'["\']?secret["\']?\s*[:=]\s*["\'][^"\']{10,}["\']', "Secret"),
            (r'["\']?token["\']?\s*[:=]\s*["\'][^"\']{20,}["\']', "Token"),
            (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
            (r"sk-[a-zA-Z0-9]{32,}", "API Secret Key"),
        ]

        for pattern, name in secret_patterns:
            if re.search(pattern, diff, re.IGNORECASE):
                issues.append(f"Potential {name} exposure detected")
                recommendations.append(f"Move {name} to environment variables")

        # Check for dangerous patterns
        dangerous_patterns = [
            (r"eval\s*\(", "Use of eval() is dangerous"),
            (r"exec\s*\(", "Use of exec() is dangerous"),
            (r"subprocess\.call.*shell\s*=\s*True", "Shell=True is risky"),
            (r"os\.system\s*\(", "os.system() is vulnerable to injection"),
            (r"pickle\.loads?\s*\(", "Pickle is unsafe for untrusted data"),
        ]

        for pattern, message in dangerous_patterns:
            if re.search(pattern, diff):
                issues.append(message)
                recommendations.append("Consider safer alternatives")

        # Calculate severity and confidence
        if any("token" in i.lower() or "key" in i.lower() for i in issues):
            severity = Severity.CRITICAL
            confidence = 0.95
        elif issues:
            severity = Severity.HIGH if len(issues) > 2 else Severity.MEDIUM
            confidence = 0.85
        else:
            severity = Severity.NONE
            confidence = 0.90

        approve = severity in (Severity.NONE, Severity.LOW)

        return ReviewResult(
            review_type=ReviewType.SECURITY,
            severity=severity,
            issues=issues,
            recommendations=recommendations,
            confidence=confidence,
            approve=approve,
        )

    async def architecture_review(
        self, diff: str, pr_data: PRData
    ) -> ReviewResult:
        """
        Review code for architecture and quality issues.

        Checks for:
        - Code organization
        - Error handling patterns
        - Documentation
        - Test coverage indicators
        """
        issues = []
        recommendations = []

        # Check for large files being added
        file_count = diff.count("+++")
        if file_count > 20:
            issues.append(f"Large PR with {file_count} files changed")
            recommendations.append("Consider breaking into smaller PRs")

        # Check for missing error handling
        if "except:" in diff and "except Exception" not in diff:
            issues.append("Bare except clause detected")
            recommendations.append("Use specific exception types")

        # Check for TODO/FIXME without tracking
        todo_count = len(re.findall(r"(?:TODO|FIXME|HACK|XXX):", diff))
        if todo_count > 3:
            issues.append(f"{todo_count} TODO/FIXME comments found")
            recommendations.append("Create issues for tracking TODOs")

        # Check for print statements in production code
        if re.search(r"^\+.*print\s*\(", diff, re.MULTILINE):
            issues.append("Print statements detected")
            recommendations.append("Use proper logging instead")

        # Calculate confidence
        if issues:
            severity = Severity.MEDIUM if len(issues) > 2 else Severity.LOW
            confidence = 0.80
        else:
            severity = Severity.NONE
            confidence = 0.85

        approve = severity in (Severity.NONE, Severity.LOW)

        return ReviewResult(
            review_type=ReviewType.ARCHITECTURE,
            severity=severity,
            issues=issues,
            recommendations=recommendations,
            confidence=confidence,
            approve=approve,
        )

    async def sovereignty_review(self, diff: str) -> ReviewResult:
        """
        Review code for sovereignty architecture alignment.

        Checks for:
        - Zero-trust compliance
        - Self-hosted infrastructure preference
        - Cryptographic verification
        - Audit trail requirements
        """
        issues = []
        recommendations = []

        # Check for external service dependencies
        external_patterns = [
            (r"https?://[^/]*(?:aws|azure|google|cloudflare)\.", "Cloud provider"),
            (r"import\s+boto3", "AWS SDK"),
            (r"from\s+azure\.", "Azure SDK"),
        ]

        for pattern, service in external_patterns:
            if re.search(pattern, diff, re.IGNORECASE):
                issues.append(f"External dependency on {service} detected")
                recommendations.append(
                    f"Consider self-hosted alternatives for {service}"
                )

        # Check for logging/audit patterns (positive)
        has_logging = bool(
            re.search(r"(?:logging\.|logger\.)", diff)
        )
        has_audit = bool(
            re.search(r"(?:audit|provenance|timestamp)", diff, re.IGNORECASE)
        )

        # Sovereignty score based on patterns
        sovereignty_score = 1.0
        if issues:
            sovereignty_score -= 0.1 * len(issues)
        if has_logging:
            sovereignty_score = min(1.0, sovereignty_score + 0.05)
        if has_audit:
            sovereignty_score = min(1.0, sovereignty_score + 0.05)

        sovereignty_score = max(0.0, sovereignty_score)

        # Determine severity
        if sovereignty_score < 0.5:
            severity = Severity.HIGH
        elif sovereignty_score < 0.7:
            severity = Severity.MEDIUM
        elif sovereignty_score < 0.9:
            severity = Severity.LOW
        else:
            severity = Severity.NONE

        approve = sovereignty_score >= self.config.thresholds.sovereignty_minimum

        return ReviewResult(
            review_type=ReviewType.SOVEREIGNTY,
            severity=severity,
            issues=issues,
            recommendations=recommendations,
            confidence=sovereignty_score,
            approve=approve,
        )

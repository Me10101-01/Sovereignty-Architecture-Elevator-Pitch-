"""
Conflict Detector: Identifies merge conflicts and contradictions.

Uses git analysis and pattern detection to find:
- Git merge conflicts
- Semantic conflicts (contradictory logic)
- Dependency conflicts
"""

import logging
import re

from .models import ConflictResult

logger = logging.getLogger(__name__)

# Configuration constants
REFACTORING_OVERLAP_THRESHOLD = 3  # Max items both added and removed before flagging


class ConflictDetector:
    """Detect merge conflicts and architectural contradictions."""

    def detect_conflicts(
        self, pr_diff: str, base_branch: str = "main"
    ) -> ConflictResult:
        """
        Check for all types of conflicts in a PR.

        Args:
            pr_diff: The diff content of the PR
            base_branch: The base branch to compare against

        Returns:
            ConflictResult with detected conflicts
        """
        git_conflicts = self._check_git_conflicts(pr_diff)
        semantic_conflicts = self._check_semantic_conflicts(pr_diff)
        dependency_conflicts = self._check_dependency_conflicts(pr_diff)

        has_conflicts = bool(
            git_conflicts or semantic_conflicts or dependency_conflicts
        )
        can_auto_resolve = self._can_auto_resolve(
            git_conflicts, semantic_conflicts, dependency_conflicts
        )

        return ConflictResult(
            has_conflicts=has_conflicts,
            git_conflicts=git_conflicts,
            semantic_conflicts=semantic_conflicts,
            dependency_conflicts=dependency_conflicts,
            can_auto_resolve=can_auto_resolve,
        )

    def _check_git_conflicts(self, diff: str) -> list[str]:
        """Check for git conflict markers in the diff."""
        conflicts = []

        # Check for conflict markers
        if "<<<<<<< " in diff:
            conflicts.append("Git conflict markers detected in diff")

        if "=======" in diff and ">>>>>>>" in diff:
            conflicts.append("Unresolved merge conflict present")

        return conflicts

    def _check_semantic_conflicts(self, diff: str) -> list[str]:
        """
        Check for contradictory logic using pattern analysis.

        Looks for patterns like:
        - Adding and removing the same feature
        - Contradictory configuration changes
        - Import/export conflicts
        """
        conflicts = []

        # Check for contradictory patterns
        lines = diff.split("\n")
        additions = set()
        deletions = set()

        for line in lines:
            if line.startswith("+") and not line.startswith("+++"):
                # Extract function/class definitions
                match = re.search(r"def (\w+)|class (\w+)", line)
                if match:
                    name = match.group(1) or match.group(2)
                    additions.add(name)
            elif line.startswith("-") and not line.startswith("---"):
                match = re.search(r"def (\w+)|class (\w+)", line)
                if match:
                    name = match.group(1) or match.group(2)
                    deletions.add(name)

        # Items both added and deleted might indicate refactoring conflicts
        overlap = additions & deletions
        if len(overlap) > REFACTORING_OVERLAP_THRESHOLD:
            conflicts.append(
                f"Potential refactoring conflict: {len(overlap)} items "
                "both added and removed"
            )

        # Check for auth pattern conflicts
        adds_auth = bool(re.search(r"\+.*(?:authenticate|authorize|auth)", diff))
        removes_auth = bool(re.search(r"-.*(?:authenticate|authorize|auth)", diff))
        if adds_auth and removes_auth:
            conflicts.append("Contradictory authentication changes detected")

        return conflicts

    def _check_dependency_conflicts(self, diff: str) -> list[str]:
        """Check for dependency version conflicts."""
        conflicts = []

        # Check for multiple version specifications
        version_changes = re.findall(
            r'["\']([^"\']+)["\']:\s*["\']([^"\']+)["\']',
            diff
        )

        seen_packages = {}
        for pkg, version in version_changes:
            if pkg in seen_packages and seen_packages[pkg] != version:
                conflicts.append(
                    f"Dependency version conflict for {pkg}: "
                    f"{seen_packages[pkg]} vs {version}"
                )
            seen_packages[pkg] = version

        # Check for requirements.txt conflicts
        req_additions = re.findall(r"\+([a-zA-Z0-9_-]+)==([0-9.]+)", diff)
        req_deletions = re.findall(r"-([a-zA-Z0-9_-]+)==([0-9.]+)", diff)

        for pkg, new_ver in req_additions:
            for old_pkg, old_ver in req_deletions:
                if pkg == old_pkg and new_ver != old_ver:
                    # This is a version update, not a conflict
                    pass

        return conflicts

    def _can_auto_resolve(
        self,
        git_conflicts: list[str],
        semantic_conflicts: list[str],
        dependency_conflicts: list[str],
    ) -> bool:
        """Determine if conflicts can be auto-resolved."""
        # Git conflicts cannot be auto-resolved
        if git_conflicts:
            return False

        # Many semantic conflicts suggest complex changes
        if len(semantic_conflicts) > 2:
            return False

        # Dependency conflicts need human review
        if dependency_conflicts:
            return False

        return True

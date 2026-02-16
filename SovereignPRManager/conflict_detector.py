"""
Conflict Detector - Detect merge conflicts and semantic contradictions.

Part of SovereignPRManager v1.0
Purpose: Identify merge conflicts and architectural contradictions
Philosophy: Proactive conflict resolution before merge
"""

import ast
import logging
import re
import subprocess
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class FileDiff:
    """Represents changes to a single file."""

    filename: str
    old_content: str = ""
    new_content: str = ""
    additions: list[str] = field(default_factory=list)
    deletions: list[str] = field(default_factory=list)
    hunks: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ConflictReport:
    """Report of detected conflicts."""

    has_conflicts: bool
    git_conflicts: list[str] = field(default_factory=list)
    semantic_conflicts: list[str] = field(default_factory=list)
    dependency_conflicts: list[str] = field(default_factory=list)
    architectural_conflicts: list[str] = field(default_factory=list)
    can_auto_resolve: bool = True
    details: dict[str, Any] = field(default_factory=dict)


class ConflictDetector:
    """Detect merge conflicts and architectural contradictions."""

    def __init__(self, repo_path: str = "."):
        """
        Initialize Conflict Detector.

        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = repo_path

    def parse_diff(self, diff_text: str) -> list[FileDiff]:
        """
        Parse a unified diff into structured file diffs.

        Args:
            diff_text: Unified diff string

        Returns:
            List of FileDiff objects
        """
        files = []
        current_file = None
        current_hunks = []

        lines = diff_text.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]

            # New file header
            if line.startswith("diff --git"):
                if current_file:
                    current_file.hunks = current_hunks
                    files.append(current_file)
                    current_hunks = []

                # Extract filename from diff header
                match = re.search(r"diff --git a/(.+?) b/(.+)", line)
                if match:
                    current_file = FileDiff(filename=match.group(2))

            # Hunk header
            elif line.startswith("@@"):
                match = re.search(r"@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@", line)
                if match and current_file:
                    current_hunks.append({
                        "old_start": int(match.group(1)),
                        "old_lines": int(match.group(2)) if match.group(2) else 1,
                        "new_start": int(match.group(3)),
                        "new_lines": int(match.group(4)) if match.group(4) else 1,
                        "content": [],
                    })

            # Content lines
            elif current_file and current_hunks:
                if line.startswith("+") and not line.startswith("+++"):
                    current_file.additions.append(line[1:])
                    if current_hunks:
                        current_hunks[-1]["content"].append(line)
                elif line.startswith("-") and not line.startswith("---"):
                    current_file.deletions.append(line[1:])
                    if current_hunks:
                        current_hunks[-1]["content"].append(line)

            i += 1

        # Don't forget the last file
        if current_file:
            current_file.hunks = current_hunks
            files.append(current_file)

        return files

    def check_git_conflicts(self, head_branch: str, base_branch: str) -> list[str]:
        """
        Check for git merge conflicts using git merge-tree.

        Args:
            head_branch: Branch with changes
            base_branch: Target branch to merge into

        Returns:
            List of conflicting files
        """
        conflicts = []

        try:
            # Find merge base
            result = subprocess.run(
                ["git", "merge-base", base_branch, head_branch],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            merge_base = result.stdout.strip()

            # Check for conflicts using merge-tree
            result = subprocess.run(
                ["git", "merge-tree", merge_base, base_branch, head_branch],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )

            # Parse merge-tree output for conflicts
            if "<<<<<<" in result.stdout or "changed in both" in result.stdout:
                # Extract conflicting file names
                for line in result.stdout.split("\n"):
                    if "changed in both" in line:
                        # Extract filename from the line
                        parts = line.split()
                        if len(parts) >= 2:
                            conflicts.append(parts[-1])

        except subprocess.CalledProcessError as e:
            logger.warning(f"Git conflict check failed: {e}")
        except FileNotFoundError:
            logger.warning("Git not available for conflict detection")

        return conflicts

    def check_semantic_conflicts(self, file_diffs: list[FileDiff]) -> list[str]:
        """
        Check for semantic/logical contradictions in code changes.

        Args:
            file_diffs: Parsed file diffs

        Returns:
            List of semantic conflict descriptions
        """
        conflicts = []

        for file_diff in file_diffs:
            if not file_diff.filename.endswith(".py"):
                continue

            try:
                # Analyze additions and deletions for contradictory patterns
                additions_text = "\n".join(file_diff.additions)
                deletions_text = "\n".join(file_diff.deletions)

                # Check for auth-related contradictions
                auth_added = self._check_auth_pattern(additions_text)
                auth_removed = self._check_auth_pattern(deletions_text)
                if auth_added and auth_removed:
                    conflicts.append(
                        f"Contradictory authentication changes in {file_diff.filename}"
                    )

                # Check for logging contradictions
                logging_added = self._check_logging_pattern(additions_text)
                logging_removed = self._check_logging_pattern(deletions_text)
                if logging_added and logging_removed:
                    conflicts.append(
                        f"Contradictory logging changes in {file_diff.filename}"
                    )

                # Check for error handling contradictions
                error_added = self._check_error_handling(additions_text)
                error_removed = self._check_error_handling(deletions_text)
                if error_added and error_removed:
                    conflicts.append(
                        f"Contradictory error handling in {file_diff.filename}"
                    )

                # Check for encryption contradictions
                encryption_added = self._check_encryption_pattern(additions_text)
                encryption_removed = self._check_encryption_pattern(deletions_text)
                if encryption_added and encryption_removed:
                    conflicts.append(
                        f"Contradictory encryption changes in {file_diff.filename}"
                    )

            except Exception as e:
                logger.warning(f"Semantic analysis failed for {file_diff.filename}: {e}")

        return conflicts

    def _check_auth_pattern(self, code: str) -> bool:
        """Check if code contains authentication patterns."""
        patterns = [
            r"@login_required",
            r"@authenticated",
            r"authenticate\(",
            r"verify_token\(",
            r"check_auth\(",
            r"requires_auth",
        ]
        return any(re.search(p, code) for p in patterns)

    def _check_logging_pattern(self, code: str) -> bool:
        """Check if code contains logging patterns."""
        patterns = [
            r"logger\.",
            r"logging\.",
            r"\.info\(",
            r"\.debug\(",
            r"\.error\(",
            r"\.warning\(",
        ]
        return any(re.search(p, code) for p in patterns)

    def _check_error_handling(self, code: str) -> bool:
        """Check if code contains error handling patterns."""
        patterns = [
            r"try:",
            r"except\s+\w+:",
            r"raise\s+\w+",
            r"\.raise_for_status\(",
        ]
        return any(re.search(p, code) for p in patterns)

    def _check_encryption_pattern(self, code: str) -> bool:
        """Check if code contains encryption patterns."""
        patterns = [
            r"encrypt\(",
            r"decrypt\(",
            r"hashlib\.",
            r"cryptography\.",
            r"Fernet\(",
            r"hmac\.",
        ]
        return any(re.search(p, code) for p in patterns)

    def check_dependency_conflicts(self, file_diffs: list[FileDiff]) -> list[str]:
        """
        Check for dependency conflicts in package files.

        Args:
            file_diffs: Parsed file diffs

        Returns:
            List of dependency conflict descriptions
        """
        conflicts = []

        for file_diff in file_diffs:
            filename = file_diff.filename

            # Check Python requirements
            if filename in ["requirements.txt", "requirements.in", "Pipfile"]:
                version_changes = self._check_version_changes(
                    file_diff.additions, file_diff.deletions
                )
                if version_changes:
                    conflicts.extend(version_changes)

            # Check npm packages
            if filename in ["package.json", "package-lock.json"]:
                # Check for significant version changes
                for add in file_diff.additions:
                    if '"version"' in add:
                        conflicts.append(
                            f"Version change detected in {filename}: {add.strip()}"
                        )

        return conflicts

    def _check_version_changes(
        self, additions: list[str], deletions: list[str]
    ) -> list[str]:
        """Check for conflicting version changes in requirements."""
        conflicts = []

        # Extract package names and versions
        add_packages = {}
        del_packages = {}

        for line in additions:
            match = re.match(r"([\w-]+)\s*([<>=!~]+)\s*([\d.]+)", line)
            if match:
                add_packages[match.group(1)] = (match.group(2), match.group(3))

        for line in deletions:
            match = re.match(r"([\w-]+)\s*([<>=!~]+)\s*([\d.]+)", line)
            if match:
                del_packages[match.group(1)] = (match.group(2), match.group(3))

        # Check for conflicting constraints
        for pkg, (op, ver) in add_packages.items():
            if pkg in del_packages:
                old_op, old_ver = del_packages[pkg]
                if ver != old_ver:
                    conflicts.append(f"Version conflict for {pkg}: {old_ver} → {ver}")

        return conflicts

    def check_architectural_conflicts(self, file_diffs: list[FileDiff]) -> list[str]:
        """
        Check for architectural conflicts using AST analysis.

        Args:
            file_diffs: Parsed file diffs

        Returns:
            List of architectural conflict descriptions
        """
        conflicts = []

        for file_diff in file_diffs:
            if not file_diff.filename.endswith(".py"):
                continue

            try:
                # Analyze new content for architectural patterns
                if file_diff.new_content:
                    tree = ast.parse(file_diff.new_content)

                    # Check for mixed sync/async patterns
                    has_async = any(
                        isinstance(node, ast.AsyncFunctionDef)
                        for node in ast.walk(tree)
                    )
                    has_sync_blocking = self._has_blocking_calls(tree)

                    if has_async and has_sync_blocking:
                        conflicts.append(
                            f"Mixed sync/async patterns in {file_diff.filename}"
                        )

            except SyntaxError:
                pass  # Skip files with syntax errors
            except Exception as e:
                logger.debug(f"AST analysis failed for {file_diff.filename}: {e}")

        return conflicts

    def _has_blocking_calls(self, tree: ast.AST) -> bool:
        """Check if AST contains blocking calls in async context."""
        blocking_funcs = {"time.sleep", "requests.get", "requests.post", "input"}

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    full_name = f"{self._get_full_name(node.func)}"
                    if full_name in blocking_funcs:
                        return True
                elif isinstance(node.func, ast.Name):
                    if node.func.id in {"input", "sleep"}:
                        return True

        return False

    def _get_full_name(self, node: ast.Attribute) -> str:
        """Get the full dotted name from an Attribute node."""
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))

    def detect_conflicts(
        self,
        diff_text: str,
        head_branch: str = None,
        base_branch: str = None,
    ) -> ConflictReport:
        """
        Perform comprehensive conflict detection.

        Args:
            diff_text: Unified diff text
            head_branch: Optional head branch name for git conflict check
            base_branch: Optional base branch name for git conflict check

        Returns:
            ConflictReport with all detected conflicts
        """
        file_diffs = self.parse_diff(diff_text)

        # Check different types of conflicts
        git_conflicts = []
        if head_branch and base_branch:
            git_conflicts = self.check_git_conflicts(head_branch, base_branch)

        semantic_conflicts = self.check_semantic_conflicts(file_diffs)
        dependency_conflicts = self.check_dependency_conflicts(file_diffs)
        architectural_conflicts = self.check_architectural_conflicts(file_diffs)

        # Determine if conflicts can be auto-resolved
        has_any_conflict = any([
            git_conflicts,
            semantic_conflicts,
            dependency_conflicts,
            architectural_conflicts,
        ])

        can_auto_resolve = (
            not git_conflicts
            and not architectural_conflicts
            and len(semantic_conflicts) <= 1
        )

        return ConflictReport(
            has_conflicts=has_any_conflict,
            git_conflicts=git_conflicts,
            semantic_conflicts=semantic_conflicts,
            dependency_conflicts=dependency_conflicts,
            architectural_conflicts=architectural_conflicts,
            can_auto_resolve=can_auto_resolve,
            details={
                "files_analyzed": len(file_diffs),
                "total_additions": sum(len(f.additions) for f in file_diffs),
                "total_deletions": sum(len(f.deletions) for f in file_diffs),
            },
        )


def main():
    """Test the Conflict Detector."""
    logging.basicConfig(level=logging.INFO)

    detector = ConflictDetector()

    # Example diff
    test_diff = """diff --git a/example.py b/example.py
index abc123..def456 100644
--- a/example.py
+++ b/example.py
@@ -1,5 +1,8 @@
+import logging
+
 def authenticate(user):
-    return check_auth(user)
+    logger.info(f"Authenticating {user}")
+    return verify_token(user.token)

 def process_data(data):
-    return data
+    return encrypt(data)
"""

    report = detector.detect_conflicts(test_diff)

    print(f"Has conflicts: {report.has_conflicts}")
    print(f"Git conflicts: {report.git_conflicts}")
    print(f"Semantic conflicts: {report.semantic_conflicts}")
    print(f"Dependency conflicts: {report.dependency_conflicts}")
    print(f"Architectural conflicts: {report.architectural_conflicts}")
    print(f"Can auto-resolve: {report.can_auto_resolve}")
    print(f"Details: {report.details}")


if __name__ == "__main__":
    main()

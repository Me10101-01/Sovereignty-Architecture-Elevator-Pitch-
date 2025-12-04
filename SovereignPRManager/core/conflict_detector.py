"""
Conflict Detector - Detects various types of conflicts in PRs
Author: SovereignPRManager Legion
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


# Regex patterns for conflict detection (compiled for efficiency)
GIT_CONFLICT_PATTERN = re.compile(r'^<{7}\s|\|{7}\s|={7}$|>{7}\s', re.MULTILINE)
DEPENDENCY_PATTERN = re.compile(
    r'(package\.json|requirements\.txt|go\.mod|Cargo\.toml|pom\.xml|'
    r'build\.gradle|Gemfile)',
    re.IGNORECASE
)


class ConflictDetector:
    """Detects git, semantic, and dependency conflicts in PRs."""
    
    def __init__(self) -> None:
        """Initialize Conflict Detector."""
        self.git_conflict_pattern = GIT_CONFLICT_PATTERN
        self.dependency_pattern = DEPENDENCY_PATTERN
    
    def detect_all_conflicts(
        self, 
        diff: str, 
        files_changed: Optional[list[str]] = None
    ) -> dict:
        """
        Detect all types of conflicts in a PR.
        
        Args:
            diff: The diff content to analyze
            files_changed: List of changed file paths
            
        Returns:
            Dictionary containing detected conflicts
        """
        conflicts = {
            "git_conflicts": self.detect_git_conflicts(diff),
            "semantic_conflicts": self.detect_semantic_conflicts(diff),
            "dependency_conflicts": self.detect_dependency_conflicts(
                files_changed or []
            ),
            "has_conflicts": False
        }
        
        # Check if any conflicts were found
        conflicts["has_conflicts"] = (
            len(conflicts["git_conflicts"]) > 0 or
            len(conflicts["semantic_conflicts"]) > 0 or
            len(conflicts["dependency_conflicts"]) > 0
        )
        
        return conflicts
    
    def detect_git_conflicts(self, diff: str) -> list[dict]:
        """Detect git merge conflict markers in diff."""
        conflicts = []
        
        if not diff:
            return conflicts
        
        # Look for conflict markers
        matches = self.git_conflict_pattern.finditer(diff)
        
        for match in matches:
            conflicts.append({
                "type": "git_conflict",
                "position": match.start(),
                "marker": match.group().strip()
            })
        
        if conflicts:
            logger.warning("Detected %d git conflicts", len(conflicts))
        
        return conflicts
    
    def detect_semantic_conflicts(self, diff: str) -> list[dict]:
        """Detect potential semantic conflicts in code changes."""
        conflicts = []
        
        if not diff:
            return conflicts
        
        # Pattern: Function redefinition
        func_def_pattern = re.compile(
            r'^[+-]\s*(?:def|function|func|fn)\s+(\w+)',
            re.MULTILINE
        )
        
        functions_modified = {}
        for match in func_def_pattern.finditer(diff):
            func_name = match.group(1)
            if func_name in functions_modified:
                conflicts.append({
                    "type": "semantic_conflict",
                    "description": f"Function '{func_name}' modified multiple times",
                    "function": func_name
                })
            functions_modified[func_name] = True
        
        # Pattern: Import conflicts
        import_pattern = re.compile(
            r'^[+-]\s*(?:import|from\s+\S+\s+import)\s+',
            re.MULTILINE
        )
        import_count = len(import_pattern.findall(diff))
        
        if import_count > 20:
            conflicts.append({
                "type": "semantic_conflict",
                "description": "Large number of import changes detected",
                "import_changes": import_count
            })
        
        return conflicts
    
    def detect_dependency_conflicts(
        self, 
        files_changed: list[str]
    ) -> list[dict]:
        """Detect potential dependency conflicts."""
        conflicts = []
        
        dependency_files = []
        for file in files_changed:
            if self.dependency_pattern.search(file):
                dependency_files.append(file)
        
        if len(dependency_files) > 1:
            conflicts.append({
                "type": "dependency_conflict",
                "description": "Multiple dependency files modified",
                "files": dependency_files
            })
        
        return conflicts
    
    def get_conflict_summary(self, conflicts: dict) -> str:
        """Generate a human-readable conflict summary."""
        if not conflicts.get("has_conflicts", False):
            return "No conflicts detected"
        
        parts = []
        
        git_conflicts = conflicts.get("git_conflicts", [])
        if git_conflicts:
            parts.append(f"- {len(git_conflicts)} git merge conflicts")
        
        semantic_conflicts = conflicts.get("semantic_conflicts", [])
        if semantic_conflicts:
            parts.append(f"- {len(semantic_conflicts)} semantic conflicts")
        
        dependency_conflicts = conflicts.get("dependency_conflicts", [])
        if dependency_conflicts:
            parts.append(f"- {len(dependency_conflicts)} dependency conflicts")
        
        return "Conflicts detected:\n" + "\n".join(parts)

"""
Sovereign Pattern Language (SPL) Grammar

This module implements the SPL interpreter that reads documentation from docs/
and uses it to understand and route agent intentions to appropriate modules.

The grammar is intentionally rule-based and rough - designed to be refined
by future LLM passes that can add more sophisticated pattern matching.

Classes:
    SovereignPattern: A dataclass representing a single sovereignty pattern
    SwarmGrammar: The main grammar parser and intent router

Example:
    >>> grammar = SwarmGrammar.from_markdown(Path("docs/"))
    >>> suggestions = grammar.suggest_module_targets("I want to analyze GKE logs")
    >>> print(suggestions)
    [("analyzers", 0.9, "Content mentions log analysis")]
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Optional
import re


@dataclass
class SovereignPattern:
    """
    A sovereignty pattern that describes a concept, role, or capability.
    
    Patterns are extracted from documentation and used to route intentions
    to appropriate modules. Each pattern knows which roles are involved
    and can provide token examples for matching.
    
    Attributes:
        name: Human-readable pattern name (e.g., "Log Analysis")
        description: Full description of the pattern
        roles: List of roles involved (sovereign, mind, hands, factory)
        token_examples: Example phrases/words that trigger this pattern
        source_file: Path to the documentation file this was extracted from
        
    Example:
        >>> pattern = SovereignPattern(
        ...     name="Code Generation",
        ...     description="Agents that write code",
        ...     roles=["hands"],
        ...     token_examples=["create", "implement", "write code"]
        ... )
    """
    name: str
    description: str
    roles: List[str] = field(default_factory=list)
    token_examples: List[str] = field(default_factory=list)
    source_file: Optional[Path] = None
    
    def matches(self, text: str) -> float:
        """
        Calculate how strongly this pattern matches the given text.
        
        Uses simple token matching - counts how many token examples
        appear in the text and normalizes by total examples.
        
        Args:
            text: The text to match against
            
        Returns:
            Match score from 0.0 (no match) to 1.0 (perfect match)
        """
        if not self.token_examples:
            return 0.0
        
        text_lower = text.lower()
        matches = sum(1 for token in self.token_examples if token.lower() in text_lower)
        
        return min(1.0, matches / len(self.token_examples))


class SwarmGrammar:
    """
    The Sovereign Pattern Language grammar parser and intent router.
    
    This class loads patterns from documentation files and uses them to
    analyze text and suggest which module should receive new code based
    on the content's intent.
    
    The grammar includes built-in patterns for the core modules (swarm,
    analyzers, experiments) and can be extended with patterns extracted
    from docs/ files.
    
    Attributes:
        patterns: List of loaded SovereignPattern instances
        
    Example:
        >>> grammar = SwarmGrammar.from_markdown(Path("docs/"))
        >>> suggestions = grammar.suggest_module_targets("Create an experiment")
        >>> for module, confidence, reason in suggestions:
        ...     print(f"{module}: {confidence:.0%}")
        experiments: 80%
    """
    
    # Built-in patterns for core modules
    BUILTIN_PATTERNS = [
        SovereignPattern(
            name="Agent Coordination",
            description="Code that orchestrates agent behavior and manages handshakes",
            roles=["sovereign", "mind"],
            token_examples=[
                "coordinate", "orchestrate", "handshake", "protocol",
                "agent", "swarm", "grammar", "pattern", "syn", "ack",
                "session", "scope", "permission", "role"
            ]
        ),
        SovereignPattern(
            name="Log Analysis",
            description="Code that parses logs, computes metrics, and generates reports",
            roles=["hands", "factory"],
            token_examples=[
                "analyze", "log", "metrics", "report", "parse",
                "audit", "gke", "kubernetes", "sovereignty", "json",
                "csv", "data", "statistics", "aggregate"
            ]
        ),
        SovereignPattern(
            name="Experimentation",
            description="Code that creates experiments, runs trials, and collects results",
            roles=["mind", "factory"],
            token_examples=[
                "experiment", "test", "trial", "collider", "lab",
                "hypothesis", "result", "artifact", "conclusion",
                "scaffold", "isolate", "measure"
            ]
        ),
    ]
    
    # Module mapping based on pattern names
    PATTERN_TO_MODULE = {
        "Agent Coordination": "swarm",
        "Log Analysis": "analyzers",
        "Experimentation": "experiments",
    }
    
    def __init__(self, patterns: Optional[List[SovereignPattern]] = None):
        """
        Initialize the grammar with a list of patterns.
        
        Args:
            patterns: Optional list of patterns. If None, uses built-in patterns.
        """
        self.patterns = patterns if patterns is not None else list(self.BUILTIN_PATTERNS)
    
    @classmethod
    def from_markdown(cls, docs_dir: Path) -> "SwarmGrammar":
        """
        Load grammar patterns from markdown files in the given directory.
        
        Scans all .md files in the directory and extracts patterns from:
        - Headers (## Role Definitions, etc.)
        - Code blocks with yaml/pattern definitions
        - Lists of keywords and examples
        
        Args:
            docs_dir: Path to the docs/ directory
            
        Returns:
            A SwarmGrammar instance with extracted patterns
            
        Example:
            >>> grammar = SwarmGrammar.from_markdown(Path("docs/"))
            >>> len(grammar.patterns) > 0
            True
        """
        patterns = list(cls.BUILTIN_PATTERNS)
        
        if not docs_dir.exists():
            return cls(patterns)
        
        for md_file in docs_dir.glob("*.md"):
            try:
                content = md_file.read_text()
                extracted = cls._extract_patterns_from_markdown(content, md_file)
                patterns.extend(extracted)
            except Exception:
                # Skip files we can't read
                continue
        
        return cls(patterns)
    
    @classmethod
    def _extract_patterns_from_markdown(cls, content: str, source: Path) -> List[SovereignPattern]:
        """
        Extract pattern definitions from markdown content.
        
        Looks for patterns in:
        - Role definition sections
        - Module target tables
        - Protocol phase descriptions
        
        Args:
            content: Markdown file content
            source: Source file path for attribution
            
        Returns:
            List of extracted patterns
        """
        patterns = []
        
        # Extract role definitions
        role_pattern = r"### (\w+)\n([^\n]+)"
        for match in re.finditer(role_pattern, content):
            role_name = match.group(1)
            role_desc = match.group(2).strip()
            
            if role_name.lower() in ["sovereign", "mind", "hands", "factory"]:
                patterns.append(SovereignPattern(
                    name=f"Role: {role_name}",
                    description=role_desc,
                    roles=[role_name.lower()],
                    token_examples=[role_name.lower()],
                    source_file=source
                ))
        
        # Extract module targets from tables
        table_pattern = r"\| (\w+)\s*\|\s*`(\w+)/`\s*\|\s*([^|]+)\|"
        for match in re.finditer(table_pattern, content):
            intent = match.group(1)
            module = match.group(2)
            desc = match.group(3).strip()
            
            patterns.append(SovereignPattern(
                name=f"Intent: {intent}",
                description=desc,
                roles=[],
                token_examples=[intent.lower(), module.lower()],
                source_file=source
            ))
        
        return patterns
    
    def suggest_module_targets(self, text: str) -> List[Tuple[str, float, str]]:
        """
        Suggest which module(s) should receive code based on text content.
        
        Analyzes the given text against all patterns and returns ranked
        suggestions for target modules.
        
        Args:
            text: The text to analyze (description, idea, or requirements)
            
        Returns:
            List of (module_name, confidence, reason) tuples, sorted by confidence
            
        Example:
            >>> grammar = SwarmGrammar()
            >>> suggestions = grammar.suggest_module_targets("analyze GKE logs")
            >>> suggestions[0][0]
            'analyzers'
        """
        # Calculate scores for each module
        module_scores = {
            "swarm": (0.0, "No strong indicators"),
            "analyzers": (0.0, "No strong indicators"),
            "experiments": (0.0, "No strong indicators"),
        }
        
        for pattern in self.patterns:
            score = pattern.matches(text)
            
            if score <= 0:
                continue
            
            # Determine target module
            module = self.PATTERN_TO_MODULE.get(pattern.name)
            
            # Handle patterns extracted from docs
            if module is None:
                if "log" in pattern.name.lower() or "analy" in pattern.name.lower():
                    module = "analyzers"
                elif "experiment" in pattern.name.lower() or "test" in pattern.name.lower():
                    module = "experiments"
                else:
                    module = "swarm"
            
            # Update score if higher
            current_score, _ = module_scores[module]
            if score > current_score:
                module_scores[module] = (score, f"Matched pattern: {pattern.name}")
        
        # Sort by score and return
        results = [
            (module, score, reason)
            for module, (score, reason) in module_scores.items()
            if score > 0
        ]
        
        # If no matches, return all with low confidence
        if not results:
            results = [
                ("swarm", 0.3, "Default for coordination/patterns"),
                ("analyzers", 0.2, "Default for data processing"),
                ("experiments", 0.2, "Default for trials"),
            ]
        
        return sorted(results, key=lambda x: -x[1])

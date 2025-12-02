"""
Swarm Ritual Module
===================

This module owns ritual rendering and documentation updates.
Rituals are the methodology documentation that guides swarm behavior.

LLM Hint: When generating ritual updates:
- Follow SWARM_HANDSHAKE_PROTOCOL.md conventions
- Update docs/ with new methodologies
- Use clear, action-oriented language
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def render_ritual(
    ritual_name: Optional[str] = None,
    docs_dir: Optional[Path] = None,
    update: bool = False,
) -> Dict[str, Any]:
    """
    Render or update ritual documentation.

    This function should:
    - Read existing rituals from docs/
    - Optionally update with new content
    - Return ritual metadata and paths

    Args:
        ritual_name: Specific ritual to render (or all if None)
        docs_dir: Directory containing ritual docs
        update: Whether to update rituals based on latest state

    Returns:
        Dict containing ritual metadata and file paths
    """
    logger.info(f"Rendering rituals: {ritual_name or 'all'}")

    # Determine docs directory
    if docs_dir is None:
        docs_dir = Path(__file__).parent.parent / "docs"

    docs_dir.mkdir(parents=True, exist_ok=True)

    # List available rituals
    rituals = _discover_rituals(docs_dir)

    if ritual_name:
        # Render specific ritual
        if ritual_name in rituals:
            return _render_single_ritual(docs_dir, ritual_name, rituals[ritual_name])
        else:
            # Create new ritual
            return _create_ritual(docs_dir, ritual_name)
    else:
        # Render all rituals
        return _render_all_rituals(docs_dir, rituals, update)


def _discover_rituals(docs_dir: Path) -> Dict[str, Path]:
    """
    Discover existing ritual documentation files.

    LLM Hint: Ritual files follow naming convention:
    - RITUAL_<NAME>.md for primary rituals
    - PROTOCOL_<NAME>.md for protocols
    - <NAME>_methodology.md for detailed guides
    """
    rituals = {}
    for md_file in docs_dir.glob("*.md"):
        name = md_file.stem.lower()
        rituals[name] = md_file
    return rituals


def _render_single_ritual(
    docs_dir: Path,
    ritual_name: str,
    ritual_path: Path,
) -> Dict[str, Any]:
    """Render a single ritual document."""
    with open(ritual_path, "r") as f:
        content = f.read()

    return {
        "ritual_name": ritual_name,
        "path": str(ritual_path),
        "content_length": len(content),
        "exists": True,
        "rendered_at": datetime.now().isoformat(),
    }


def _create_ritual(docs_dir: Path, ritual_name: str) -> Dict[str, Any]:
    """
    Create a new ritual document.

    LLM Hint: New rituals should include:
    - Purpose and scope
    - Step-by-step procedure
    - Integration points with swarm modules
    - Version history
    """
    safe_name = ritual_name.replace(" ", "_").upper()
    ritual_path = docs_dir / f"RITUAL_{safe_name}.md"

    template = f"""# {ritual_name.replace('_', ' ').title()} Ritual

## Purpose

This ritual defines...

> LLM Hint: Extend this ritual with specific procedures and integration points.

## Procedure

1. **Prepare**: ...
2. **Execute**: ...
3. **Verify**: ...

## Integration Points

- `swarm.experiment.run_experiment` - For experiment execution
- `swarm.analyzer.analyze_logs` - For log analysis
- `swarm.ritual.render_ritual` - For documentation updates

## Version History

- {datetime.now().strftime('%Y-%m-%d')}: Initial creation by swarm
"""

    with open(ritual_path, "w") as f:
        f.write(template)

    logger.info(f"Created new ritual: {ritual_path}")

    return {
        "ritual_name": ritual_name,
        "path": str(ritual_path),
        "created": True,
        "rendered_at": datetime.now().isoformat(),
    }


def _render_all_rituals(
    docs_dir: Path,
    rituals: Dict[str, Path],
    update: bool,
) -> Dict[str, Any]:
    """Render summary of all rituals."""
    ritual_summaries = []

    for name, path in rituals.items():
        with open(path, "r") as f:
            content = f.read()
        ritual_summaries.append({
            "name": name,
            "path": str(path),
            "content_length": len(content),
            "lines": content.count("\n") + 1,
        })

    result = {
        "total_rituals": len(rituals),
        "rituals": ritual_summaries,
        "docs_dir": str(docs_dir),
        "rendered_at": datetime.now().isoformat(),
    }

    if update:
        # Update ritual index if needed
        result["updated"] = _update_ritual_index(docs_dir, rituals)

    return result


def _update_ritual_index(docs_dir: Path, rituals: Dict[str, Path]) -> bool:
    """
    Update the ritual index document.

    LLM Hint: The index should:
    - List all available rituals
    - Provide quick navigation
    - Include last-updated timestamps
    """
    index_path = docs_dir / "RITUAL_INDEX.md"

    index_content = f"""# Swarm Ritual Index

> Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Available Rituals

"""
    for name, path in sorted(rituals.items()):
        index_content += f"- [{name}]({path.name})\n"

    index_content += """
## Usage

Use the swarm CLI to render or update rituals:

```bash
python main.py ritual --name <ritual_name>
```

## Integration

Rituals integrate with the swarm module via:
- `swarm.ritual.render_ritual()` - Render documentation
- `swarm.experiment.run_experiment()` - Execute experiments
- `swarm.analyzer.analyze_logs()` - Analyze captured traces
"""

    with open(index_path, "w") as f:
        f.write(index_content)

    return True

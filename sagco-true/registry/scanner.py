"""
SAGCO Registry Scanner — finds all sagco-brick.toml manifests in the repo.
"""

from __future__ import annotations
from pathlib import Path
from typing import Iterator
from .manifest import Brick, parse_manifest

# Directories to skip during scan
_SKIP_DIRS = {
    "target", ".git", "__pycache__", ".claude", "node_modules",
    ".vscode", ".devcontainer", "venv", ".venv", "dist", "build",
}


def find_manifests(root: str | Path) -> Iterator[Path]:
    """Yield every sagco-brick.toml under root."""
    root = Path(root)
    for p in root.rglob("sagco-brick.toml"):
        # Skip if any parent segment is in skip list
        parts = set(p.parts)
        if parts & _SKIP_DIRS:
            continue
        yield p


def scan_bricks(root: str | Path) -> list[Brick]:
    """Scan root for all sagco-brick.toml files and return parsed Brick list."""
    bricks: list[Brick] = []
    for manifest_path in find_manifests(root):
        brick = parse_manifest(manifest_path)
        if brick is not None:
            bricks.append(brick)

    # Sort: kernel first, then core, then platform, then extension
    layer_order = {"kernel": 0, "core": 1, "platform": 2, "extension": 3}
    bricks.sort(key=lambda b: (layer_order.get(b.layer, 9), b.id))
    return bricks

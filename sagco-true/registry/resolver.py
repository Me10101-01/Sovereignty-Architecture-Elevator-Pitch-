"""
SAGCO Dependency Resolver — topological sort, cycle detection, dep tree.
"""

from __future__ import annotations
from .manifest import Brick


def _build_index(bricks: list[Brick]) -> dict[str, Brick]:
    return {b.id: b for b in bricks}


def topological_order(bricks: list[Brick]) -> list[Brick]:
    """
    Kahn's algorithm — returns bricks in build order (deps before dependents).
    Raises ValueError on circular dependency.
    """
    index = _build_index(bricks)
    in_degree: dict[str, int] = {b.id: 0 for b in bricks}

    for b in bricks:
        for dep_id in b.depends_on:
            if dep_id in in_degree:
                in_degree[b.id] += 1

    queue = [b for b in bricks if in_degree[b.id] == 0]
    result: list[Brick] = []

    while queue:
        node = queue.pop(0)
        result.append(node)
        # Find all bricks that depend on this node
        for other in bricks:
            if node.id in other.depends_on:
                in_degree[other.id] -= 1
                if in_degree[other.id] == 0:
                    queue.append(other)

    if len(result) != len(bricks):
        remaining = [b.id for b in bricks if b not in result]
        raise ValueError(f"Circular dependency detected among: {remaining}")

    return result


def resolve_deps(brick_id: str, bricks: list[Brick]) -> list[Brick]:
    """Return all transitive dependencies of brick_id, in build order."""
    index = _build_index(bricks)
    visited: set[str] = set()
    order: list[Brick] = []

    def _visit(bid: str) -> None:
        if bid in visited:
            return
        visited.add(bid)
        brick = index.get(bid)
        if brick is None:
            return
        for dep_id in brick.depends_on:
            _visit(dep_id)
        order.append(brick)

    _visit(brick_id)
    return order


def dep_tree_str(brick_id: str, bricks: list[Brick], indent: int = 0) -> str:
    """Return a formatted dependency tree string."""
    index = _build_index(bricks)
    lines: list[str] = []

    def _render(bid: str, depth: int, seen: set[str]) -> None:
        prefix = "  " * depth + ("└─ " if depth > 0 else "")
        brick = index.get(bid)
        if brick is None:
            lines.append(f"{prefix}{bid}  [NOT FOUND]")
            return

        marker = " (↺)" if bid in seen else ""
        lines.append(f"{prefix}{brick.layer_icon} {brick.id}  v{brick.version}  [{brick.layer}]{marker}")

        if bid not in seen:
            new_seen = seen | {bid}
            for dep_id in brick.depends_on:
                _render(dep_id, depth + 1, new_seen)

    _render(brick_id, 0, set())
    return "\n".join(lines)

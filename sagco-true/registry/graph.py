"""
SAGCO Registry — ASCII dependency graph generator.
"""

from __future__ import annotations
from .manifest import Brick


def ascii_graph(bricks: list[Brick]) -> str:
    """
    Generate a full ASCII dependency graph of all bricks.
    Shows: layer → brick → provides → depends_on
    """
    index = {b.id: b for b in bricks}
    layers = ["kernel", "core", "platform", "extension"]

    lines: list[str] = []
    lines.append("  SAGCO BRICK DEPENDENCY GRAPH")
    lines.append("  Strategickhaos DAO LLC")
    lines.append("")
    lines.append("  Legend: ⬡=kernel  ■=core  ▲=platform  ◆=extension")
    lines.append("          ─── depends_on  ═══ provides")
    lines.append("")

    for layer in layers:
        layer_bricks = [b for b in bricks if b.layer == layer]
        if not layer_bricks:
            continue

        icon = {"kernel": "⬡", "core": "■", "platform": "▲", "extension": "◆"}[layer]
        lines.append(f"  {'─'*60}")
        lines.append(f"  {icon}  LAYER: {layer.upper()}")
        lines.append(f"  {'─'*60}")

        for brick in layer_bricks:
            lines.append(f"")
            lines.append(f"    [{brick.id}]  v{brick.version}  ({brick.language})")
            lines.append(f"    {brick.description[:70]}")

            if brick.depends_on:
                lines.append(f"    Depends on:")
                for dep_id, ver in brick.depends_on.items():
                    dep = index.get(dep_id)
                    dep_layer = f"[{dep.layer}]" if dep else "[EXTERNAL]"
                    lines.append(f"      ─── {dep_id} {ver} {dep_layer}")

            if brick.capabilities:
                cap_str = ", ".join(brick.capabilities[:4])
                if len(brick.capabilities) > 4:
                    cap_str += f" (+{len(brick.capabilities)-4} more)"
                lines.append(f"    Provides: {cap_str}")

            lines.append(f"    Wafers: {brick.wafer_status}  {brick.coverage}")

    lines.append("")
    lines.append(f"  {'─'*60}")
    lines.append(f"  Total bricks: {len(bricks)}")

    # Count edges
    edge_count = sum(len(b.depends_on) for b in bricks)
    lines.append(f"  Total edges:  {edge_count}")
    lines.append(f"  {'─'*60}")

    return "\n".join(lines)


def capability_index(bricks: list[Brick]) -> str:
    """Print all capabilities across all bricks, sorted."""
    all_caps: dict[str, list[str]] = {}
    for brick in bricks:
        for cap in brick.capabilities:
            all_caps.setdefault(cap, []).append(brick.id)

    lines = ["  CAPABILITY INDEX", "  ─" * 30, ""]
    for cap in sorted(all_caps):
        providers = ", ".join(all_caps[cap])
        lines.append(f"  {cap:<35} ← {providers}")

    return "\n".join(lines)

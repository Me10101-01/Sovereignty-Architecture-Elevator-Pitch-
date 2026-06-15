"""
SAGCO Knowledge Graph Builder

Converts the SAGCO registry + claims into a traversable graph.
Exports to:
  - adjacency dict (in-memory, no deps)
  - Cypher (Neo4j)
  - Obsidian canvas JSON

"The graph is the asset."
"""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_ROOT = Path(__file__).parent.parent.parent


# ── Graph primitives ────────────────────────────────────────────────────────

@dataclass
class Node:
    id:       str
    label:    str
    kind:     str      # brick | claim | antibody | lineage | verdict
    layer:    str = ""
    color:    str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class Edge:
    from_id: str
    to_id:   str
    rel:     str       # depends_on | proves | fires | derived_from | variant_of


@dataclass
class KGraph:
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)

    def add_node(self, n: Node) -> None:
        if not any(x.id == n.id for x in self.nodes):
            self.nodes.append(n)

    def add_edge(self, e: Edge) -> None:
        self.edges.append(e)

    def neighbors(self, node_id: str) -> list[str]:
        return [e.to_id for e in self.edges if e.from_id == node_id]

    def summary(self) -> str:
        return f"{len(self.nodes)} nodes | {len(self.edges)} edges"


# ── Layer colors ────────────────────────────────────────────────────────────

LAYER_COLORS = {
    "kernel":    "#8B0000",
    "core":      "#1a1a8c",
    "platform":  "#1a5c1a",
    "extension": "#5c4a00",
    "claim":     "#4a0080",
    "antibody":  "#cc0000",
    "verdict":   "#005c5c",
}


# ── Build from registry ─────────────────────────────────────────────────────

def build_from_registry(registry_path: Optional[Path] = None) -> KGraph:
    """Build KGraph from registry.sagco.json."""
    path = registry_path or (_ROOT / "registry.sagco.json")
    if not path.exists():
        print(f"  [warn] registry not found at {path}")
        return KGraph()

    data   = json.loads(path.read_text())
    bricks = data.get("bricks", [])
    g      = KGraph()

    for b in bricks:
        bid   = b["id"]
        layer = b.get("layer", "extension")
        node  = Node(
            id    = bid,
            label = b.get("name", bid),
            kind  = "brick",
            layer = layer,
            color = LAYER_COLORS.get(layer, "#333"),
            metadata = {
                "version":  b.get("version", ""),
                "language": b.get("language", ""),
                "wafer":    b.get("wafer_status", ""),
            },
        )
        g.add_node(node)

        deps = b.get("depends_on", {})
        if isinstance(deps, dict):
            for dep_id in deps.values():
                g.add_edge(Edge(from_id=bid, to_id=dep_id, rel="depends_on"))
        elif isinstance(deps, list):
            for dep_id in deps:
                g.add_edge(Edge(from_id=bid, to_id=dep_id, rel="depends_on"))

    return g


def add_claims_to_graph(g: KGraph) -> None:
    """Add claim nodes from claims.yaml if available."""
    claims_path = _ROOT / "sagco-missing-links" / "registry" / "claims.yaml"
    if not claims_path.exists():
        return

    try:
        import re
        text = claims_path.read_text()
        # Extract IDs simply — no external yaml dep
        ids = re.findall(r"id:\s+\"([A-Z]+-[A-Z0-9]+-[0-9]+)\"", text)
        verdicts = re.findall(r"verdict:\s+\"([A-Z]+)\"", text)

        for i, cid in enumerate(ids):
            v = verdicts[i] if i < len(verdicts) else "OPEN"
            g.add_node(Node(
                id    = cid,
                label = cid,
                kind  = "claim",
                color = LAYER_COLORS["claim"],
                metadata = {"verdict": v},
            ))
    except Exception:
        pass


# ── Export: Cypher (Neo4j) ──────────────────────────────────────────────────

def to_cypher(g: KGraph) -> str:
    lines = []
    lines.append("// SAGCO Knowledge Graph — Cypher export")
    lines.append("// Load into Neo4j: :play or paste in Neo4j Browser")
    lines.append("")

    for n in g.nodes:
        safe_id = n.id.replace("-", "_")
        props   = json.dumps({"id": n.id, "label": n.label, "layer": n.layer, "kind": n.kind})
        lines.append(f"CREATE (n_{safe_id}:{n.kind.capitalize()} {props})")

    lines.append("")
    for e in g.edges:
        f = e.from_id.replace("-", "_")
        t = e.to_id.replace("-", "_")
        lines.append(f"CREATE (n_{f})-[:{e.rel.upper()}]->(n_{t})")

    return "\n".join(lines)


# ── Export: Obsidian Canvas ─────────────────────────────────────────────────

def to_obsidian_canvas(g: KGraph) -> dict:
    """
    Obsidian Canvas JSON format.
    Drop the output as a .canvas file in your Obsidian vault.
    """
    nodes  = []
    edges  = []
    x, y   = 0, 0
    spacing_x, spacing_y = 250, 180

    layer_order = ["kernel", "core", "platform", "extension", "claim", "antibody"]
    by_layer: dict[str, list[Node]] = {}
    for n in g.nodes:
        by_layer.setdefault(n.kind if n.kind != "brick" else n.layer, []).append(n)

    for li, layer_key in enumerate(layer_order):
        layer_nodes = by_layer.get(layer_key, [])
        for ni, n in enumerate(layer_nodes):
            nodes.append({
                "id":     hashlib.md5(n.id.encode()).hexdigest()[:8],
                "type":   "text",
                "text":   f"**{n.label}**\n{n.kind} | {n.layer}\n{n.metadata.get('verdict', '')}",
                "x":      li * spacing_x,
                "y":      ni * spacing_y,
                "width":  220,
                "height": 80,
                "color":  n.color.lstrip("#") if n.color else "1",
            })

    node_id_map = {n.id: hashlib.md5(n.id.encode()).hexdigest()[:8] for n in g.nodes}
    for e in g.edges:
        if e.from_id in node_id_map and e.to_id in node_id_map:
            edges.append({
                "id":        hashlib.md5((e.from_id + e.to_id + e.rel).encode()).hexdigest()[:8],
                "fromNode":  node_id_map[e.from_id],
                "fromSide":  "right",
                "toNode":    node_id_map[e.to_id],
                "toSide":    "left",
                "label":     e.rel,
            })

    return {"nodes": nodes, "edges": edges}


# ── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    p = argparse.ArgumentParser(description="SAGCO KG Builder")
    p.add_argument("--cypher",  action="store_true", help="Export Cypher for Neo4j")
    p.add_argument("--canvas",  action="store_true", help="Export Obsidian canvas JSON")
    p.add_argument("--summary", action="store_true", help="Print graph summary")
    p.add_argument("--out",     default=None,        help="Output file path")
    args = p.parse_args()

    g = build_from_registry()
    add_claims_to_graph(g)

    if args.summary or not (args.cypher or args.canvas):
        print(f"\n  SAGCO Knowledge Graph: {g.summary()}")
        print()
        for layer in ["kernel", "core", "platform", "extension"]:
            nodes = [n for n in g.nodes if n.layer == layer]
            if nodes:
                print(f"  [{layer}] {len(nodes)} nodes")
                for n in nodes:
                    nbrs = g.neighbors(n.id)
                    dep_str = f" → {', '.join(nbrs)}" if nbrs else ""
                    print(f"    • {n.id}{dep_str}")
        claim_nodes = [n for n in g.nodes if n.kind == "claim"]
        if claim_nodes:
            print(f"\n  [claims] {len(claim_nodes)} nodes")
            for n in claim_nodes:
                print(f"    • {n.id}  [{n.metadata.get('verdict', '?')}]")
        print()

    if args.cypher:
        out = to_cypher(g)
        if args.out:
            Path(args.out).write_text(out)
            print(f"  Cypher written → {args.out}")
        else:
            print(out)

    if args.canvas:
        canvas = to_obsidian_canvas(g)
        out_str = json.dumps(canvas, indent=2)
        out_path = args.out or "sagco-missing-links/graph/sagco.canvas"
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_text(out_str)
        print(f"  Canvas written → {out_path}")
        print(f"  Drop {out_path} into your Obsidian vault /.obsidian/ or notes/ folder")


if __name__ == "__main__":
    main()

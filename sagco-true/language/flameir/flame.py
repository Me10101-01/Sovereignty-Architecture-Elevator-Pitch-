"""
FlameLang IR — the sheet music between organic discovery and bytecode.

Position in domino chain:
  CONCERT → FlameLang IR → compiler → BYTECODE

A FlameLang IR document encodes:
  - What the transform wants to be (intent)
  - Where it came from (provenance: stepper/crawler output)
  - What inputs it expects (typed, with units)
  - What transforms it applies (steps with catalysts)
  - What outputs it produces (typed, with units)
  - What truth tests seal it (wafer references)
  - A tick seal proving it hasn't been tampered with

Inspired by:
  - Alchemical Process Compiler: input + catalyst(wafer) + heat → output
  - Rolling Offset: each step output = next step input at offset angle
  - Frequency: each transform has a period (how often it fires)
  - Spherical Coordinates: transforms can have 3D positional context
  - Electronegativity: inputs/outputs have binding strength to each other
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any


class FlameNodeKind(Enum):
    SOURCE    = "source"     # raw discovery input (stepper output)
    TRANSFORM = "transform"  # a processing step (crawler/ticks output)
    CATALYST  = "catalyst"   # wafer truth test enabling a transform
    BOND      = "bond"       # dependency link between nodes (electronegativity)
    SINK      = "sink"       # final output / result
    TICK      = "tick"       # temporal seal checkpoint


@dataclass
class FlamePort:
    name: str
    type_hint: str = "any"      # int, float, str, bool, bytes, any
    unit: str = ""              # hz, m, deg, rad, nm, etc.
    required: bool = True


@dataclass
class FlameNode:
    id: str
    kind: FlameNodeKind
    label: str
    intent: str = ""            # what this node wants to accomplish
    inputs: list[FlamePort] = field(default_factory=list)
    outputs: list[FlamePort] = field(default_factory=list)
    catalyst: str = ""          # wafer name that must pass for this to fire
    period: float = 0.0         # 0 = one-shot; >0 = oscillatory (seconds)
    phase: float = 0.0          # 0.0–1.0 position in cycle
    provenance: str = ""        # origin: file path, url, stepper-id
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": self.kind.value,
            "label": self.label,
            "intent": self.intent,
            "inputs": [{"name": p.name, "type": p.type_hint, "unit": p.unit,
                        "required": p.required} for p in self.inputs],
            "outputs": [{"name": p.name, "type": p.type_hint, "unit": p.unit,
                         "required": p.required} for p in self.outputs],
            "catalyst": self.catalyst,
            "period": self.period,
            "phase": self.phase,
            "provenance": self.provenance,
            "meta": self.meta,
        }

    @staticmethod
    def from_dict(d: dict) -> "FlameNode":
        def _port(p: dict) -> FlamePort:
            return FlamePort(p["name"], p.get("type", "any"),
                             p.get("unit", ""), p.get("required", True))
        return FlameNode(
            id=d["id"],
            kind=FlameNodeKind(d["kind"]),
            label=d["label"],
            intent=d.get("intent", ""),
            inputs=[_port(p) for p in d.get("inputs", [])],
            outputs=[_port(p) for p in d.get("outputs", [])],
            catalyst=d.get("catalyst", ""),
            period=d.get("period", 0.0),
            phase=d.get("phase", 0.0),
            provenance=d.get("provenance", ""),
            meta=d.get("meta", {}),
        )


@dataclass
class FlameEdge:
    from_id: str
    from_port: str
    to_id: str
    to_port: str
    bond_strength: str = "required"  # required | optional


@dataclass
class FlameGraph:
    nodes: list[FlameNode] = field(default_factory=list)
    edges: list[FlameEdge] = field(default_factory=list)

    def add_node(self, node: FlameNode) -> "FlameGraph":
        self.nodes.append(node)
        return self

    def connect(self, from_id: str, from_port: str,
                to_id: str, to_port: str,
                bond_strength: str = "required") -> "FlameGraph":
        self.edges.append(FlameEdge(from_id, from_port, to_id, to_port, bond_strength))
        return self

    def topological_order(self) -> list[FlameNode]:
        """Kahn's algorithm — rolling offset: each step feeds the next."""
        from collections import defaultdict, deque
        in_degree: dict[str, int] = defaultdict(int)
        adj: dict[str, list[str]] = defaultdict(list)
        node_map = {n.id: n for n in self.nodes}

        for e in self.edges:
            adj[e.from_id].append(e.to_id)
            in_degree[e.to_id] += 1

        queue: deque[str] = deque(
            nid for nid in node_map if in_degree[nid] == 0
        )
        order: list[FlameNode] = []
        while queue:
            nid = queue.popleft()
            if nid in node_map:
                order.append(node_map[nid])
            for nxt in adj[nid]:
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)

        return order

    def to_dict(self) -> dict:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [
                {"from": e.from_id, "from_port": e.from_port,
                 "to": e.to_id, "to_port": e.to_port,
                 "bond": e.bond_strength}
                for e in self.edges
            ],
        }


@dataclass
class FlameIR:
    """
    Top-level FlameLang IR document.
    One document = one Concert output = one domino tick in the chain.
    """
    title: str
    intent: str              # what this IR block wants to be
    source: str              # provenance: stepper/crawler run id or path
    graph: FlameGraph = field(default_factory=FlameGraph)
    wafers: list[str] = field(default_factory=list)     # wafer names sealing this IR
    tick_seal: str = ""      # SHA-256 seal from TICK opcode
    generated_at: float = field(default_factory=time.time)
    version: str = "0.1.0"

    def seal(self) -> str:
        """Produce a tick seal over the IR content."""
        content = json.dumps(self.graph.to_dict(), sort_keys=True).encode()
        h = hashlib.sha256(content + self.title.encode() + self.intent.encode())
        self.tick_seal = h.hexdigest()
        return self.tick_seal

    def validate(self) -> list[str]:
        """Check structural integrity. Returns list of violations."""
        issues: list[str] = []
        ids = {n.id for n in self.graph.nodes}
        for e in self.graph.edges:
            if e.from_id not in ids:
                issues.append(f"edge from unknown node: {e.from_id}")
            if e.to_id not in ids:
                issues.append(f"edge to unknown node: {e.to_id}")
        # every TRANSFORM must have a catalyst or be explicitly uncatalyzed
        for n in self.graph.nodes:
            if n.kind == FlameNodeKind.TRANSFORM and not n.catalyst:
                issues.append(f"transform '{n.id}' has no catalyst wafer — uncatalyzed transmutation")
        return issues

    def to_dict(self) -> dict:
        return {
            "flame_ir": True,
            "version": self.version,
            "title": self.title,
            "intent": self.intent,
            "source": self.source,
            "graph": self.graph.to_dict(),
            "wafers": self.wafers,
            "tick_seal": self.tick_seal,
            "generated_at": self.generated_at,
        }

    def to_sagco_bytecode_hints(self) -> list[str]:
        """
        Emit bytecode comment hints for each graph node in topological order.
        Used by the Concert layer to drive SAGCO compilation.
        """
        lines: list[str] = [
            f"; FlameLang IR — {self.title}",
            f"; Intent: {self.intent}",
            f"; Seal: {self.tick_seal or '(unsealed)'}",
            "",
        ]
        for node in self.graph.topological_order():
            lines.append(f"; [{node.kind.value.upper()}] {node.id} — {node.label}")
            if node.intent:
                lines.append(f";   intent: {node.intent}")
            if node.catalyst:
                lines.append(f";   catalyst (wafer): {node.catalyst}")
                lines.append(f"  MEASURE {node.catalyst!r}")
            for inp in node.inputs:
                hint = f"{inp.name}: {inp.type_hint}"
                if inp.unit:
                    hint += f" [{inp.unit}]"
                lines.append(f";   in:  {hint}")
            for out in node.outputs:
                hint = f"{out.name}: {out.type_hint}"
                if out.unit:
                    hint += f" [{out.unit}]"
                lines.append(f";   out: {hint}")
            if node.period > 0:
                lines.append(f"  PUSH {node.period}")
                lines.append(f"  PERIOD {node.id!r}")
            lines.append("")
        if self.tick_seal:
            lines.append(f"  PUSH {self.tick_seal!r}")
            lines.append(f"  STORE flame.seal")
        return lines


def save_flame(ir: FlameIR, path: str | Path) -> None:
    ir.seal()
    Path(path).write_text(json.dumps(ir.to_dict(), indent=2))


def load_flame(path: str | Path) -> FlameIR:
    d = json.loads(Path(path).read_text())
    graph = FlameGraph()
    for nd in d["graph"]["nodes"]:
        graph.add_node(FlameNode.from_dict(nd))
    for ed in d["graph"]["edges"]:
        graph.connect(ed["from"], ed["from_port"], ed["to"], ed["to_port"],
                      ed.get("bond", "required"))
    return FlameIR(
        title=d["title"],
        intent=d["intent"],
        source=d["source"],
        graph=graph,
        wafers=d.get("wafers", []),
        tick_seal=d.get("tick_seal", ""),
        generated_at=d.get("generated_at", 0),
        version=d.get("version", "0.1.0"),
    )

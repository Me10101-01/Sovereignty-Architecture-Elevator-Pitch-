"""
SAGCO Registry Store — scan, hold, query, and persist the full brick registry.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .manifest  import Brick
from .scanner   import scan_bricks
from .resolver  import topological_order, resolve_deps, dep_tree_str
from .graph     import ascii_graph, capability_index

# Default registry snapshot file location
_DEFAULT_REGISTRY_PATH = Path(__file__).parent.parent.parent / "registry.sagco.json"


@dataclass
class AuditResult:
    brick_id:    str
    status:      str     # PASS | FAIL | UNKNOWN
    wafer_status: str
    notes:       str


class Registry:
    """
    The SAGCO Brick Registry.
    Load from disk, scan from repo, or build programmatically.
    """

    def __init__(self, bricks: list[Brick], scanned_at: float | None = None) -> None:
        self.bricks     = bricks
        self.scanned_at = scanned_at or time.time()
        self._index     = {b.id: b for b in bricks}

    # ── Factory methods ────────────────────────────────────────────────────

    @classmethod
    def scan(cls, root: str | Path | None = None) -> "Registry":
        """Scan the repo for all sagco-brick.toml files and build registry."""
        if root is None:
            root = Path(__file__).parent.parent.parent
        bricks = scan_bricks(root)
        return cls(bricks)

    @classmethod
    def load(cls, path: str | Path | None = None) -> "Registry":
        """Load registry from a JSON snapshot file."""
        p = Path(path) if path else _DEFAULT_REGISTRY_PATH
        if not p.exists():
            return cls([])
        data = json.loads(p.read_text(encoding="utf-8"))
        bricks = [_brick_from_dict(b) for b in data.get("bricks", [])]
        return cls(bricks, scanned_at=data.get("scanned_at"))

    # ── Queries ────────────────────────────────────────────────────────────

    def get(self, brick_id: str) -> Optional[Brick]:
        return self._index.get(brick_id)

    def by_layer(self, layer: str) -> list[Brick]:
        return [b for b in self.bricks if b.layer == layer]

    def by_capability(self, cap: str) -> list[Brick]:
        return [b for b in self.bricks if cap in b.capabilities]

    def dependents_of(self, brick_id: str) -> list[Brick]:
        """Return all bricks that depend on brick_id (direct only)."""
        return [b for b in self.bricks if brick_id in b.depends_on]

    def build_order(self) -> list[Brick]:
        try:
            return topological_order(self.bricks)
        except ValueError as e:
            print(f"  [WARN] {e}")
            return self.bricks

    def dep_tree(self, brick_id: str) -> str:
        return dep_tree_str(brick_id, self.bricks)

    def dep_chain(self, brick_id: str) -> list[Brick]:
        return resolve_deps(brick_id, self.bricks)

    # ── Audit ──────────────────────────────────────────────────────────────

    def audit(self) -> list[AuditResult]:
        results = []
        for brick in self.bricks:
            status = "PASS" if "PASS" in brick.wafer_status.upper() else (
                "UNKNOWN" if brick.wafer_status == "UNKNOWN" else "FAIL"
            )
            results.append(AuditResult(
                brick_id=brick.id,
                status=status,
                wafer_status=brick.wafer_status,
                notes=brick.notes[:80] if brick.notes else "",
            ))
        return results

    # ── Reports ────────────────────────────────────────────────────────────

    def summary(self) -> str:
        lines = []
        lines.append("")
        lines.append("  ══════════════════════════════════════════════════════════")
        lines.append("  SAGCO BRICK REGISTRY")
        lines.append("  Strategickhaos DAO LLC")
        lines.append("  ══════════════════════════════════════════════════════════")
        lines.append(f"  Bricks registered: {len(self.bricks)}")
        lines.append(f"  Scanned at:        {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(self.scanned_at))}")
        lines.append("")

        layer_order = ["kernel", "core", "platform", "extension"]
        icon_map = {"kernel": "⬡", "core": "■", "platform": "▲", "extension": "◆"}

        for layer in layer_order:
            lb = self.by_layer(layer)
            if not lb:
                continue
            icon = icon_map[layer]
            lines.append(f"  {icon}  {layer.upper()} ({len(lb)} bricks)")
            for b in lb:
                dep_str = f"  deps: {', '.join(b.depends_on)}" if b.depends_on else ""
                lines.append(f"     {b.status_icon}  {b.id:<25} v{b.version:<8} [{b.language}]{dep_str}")
        lines.append("")
        lines.append("  ══════════════════════════════════════════════════════════")
        return "\n".join(lines)

    def print_audit(self) -> None:
        print()
        print("  ── REGISTRY AUDIT ──────────────────────────────────────────")
        results = self.audit()
        passed = sum(1 for r in results if r.status == "PASS")
        for r in results:
            icon = "✓" if r.status == "PASS" else ("?" if r.status == "UNKNOWN" else "✗")
            print(f"  [{icon}] {r.brick_id:<28} {r.wafer_status}")
        print()
        print(f"  {passed}/{len(results)} bricks PASS")
        print("  ────────────────────────────────────────────────────────────")

    def print_graph(self) -> None:
        print(ascii_graph(self.bricks))

    def print_capabilities(self) -> None:
        print(capability_index(self.bricks))

    # ── Persistence ────────────────────────────────────────────────────────

    def save(self, path: str | Path | None = None) -> str:
        p = Path(path) if path else _DEFAULT_REGISTRY_PATH
        payload = {
            "sagco_registry_version": "1.0.0",
            "scanned_at":  self.scanned_at,
            "brick_count": len(self.bricks),
            "seal":        _seal(self.bricks),
            "bricks":      [b.to_dict() for b in self.bricks],
        }
        p.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(p)


# ── Helpers ────────────────────────────────────────────────────────────────

def _brick_from_dict(d: dict) -> Brick:
    from .manifest import Brick
    return Brick(
        id           = d.get("id", ""),
        name         = d.get("name", ""),
        version      = d.get("version", "0.0.0"),
        description  = d.get("description", ""),
        language     = d.get("language", "unknown"),
        layer        = d.get("layer", "extension"),
        owner        = d.get("owner", ""),
        path         = d.get("path", ""),
        capabilities = d.get("capabilities", []),
        apis         = d.get("apis", []),
        ports        = d.get("ports", []),
        depends_on   = d.get("depends_on", {}),
        test_command = d.get("test_command", ""),
        wafer_status = d.get("wafer_status", "UNKNOWN"),
        coverage     = d.get("coverage", ""),
        seal         = d.get("seal", ""),
        audit_status = d.get("audit_status", "UNKNOWN"),
        notes        = d.get("notes", ""),
    )


def _seal(bricks: list[Brick]) -> str:
    content = json.dumps(
        sorted([b.id + "@" + b.version for b in bricks])
    ).encode()
    return hashlib.sha256(content).hexdigest()[:16]


def save_registry(registry: Registry, path: str | Path | None = None) -> str:
    return registry.save(path)


def load_registry(path: str | Path | None = None) -> Registry:
    return Registry.load(path)

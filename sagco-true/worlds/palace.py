"""
SAGCO Memory Palace — Sovereign Index
The map of all maps. Knows what exists, where it lives, how it all connects.

Not a database. Not a daemon. A scan-and-index engine that walks every known
node root and assembles the organism's self-portrait.

sagco palace scan
sagco palace status
sagco palace locate <name>
sagco palace register
sagco palace diff <node-a> <node-b>
"""

from __future__ import annotations
import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ── Component discovery globs ────────────────────────────────────────────────

COMPONENT_GLOBS: dict[str, list[str]] = {
    "boards":    [
        "boards/**/*.sagco", "boards/**/*.yaml", "boards/**/*.md",
        "boards/**/BOARD.json",
        "sagco-true/boards/**/__init__.py",   # BOARD-*/  Python boards
        "sagco-true/boards/**/*.sagco",
    ],
    "agents":    [
        "agents/**/*.sagco", "agents/**/*.py", "agents/**/*.yaml",
        "sagco-true/agents/**/*.py",
    ],
    "wafers":    [
        "wafers/**/*.txt",   "wafers/**/*.csv", "wafers/**/*.sagco",
        "wafers/**/*.json",
        "sagco-true/wafers/**/*.csv", "sagco-true/wafers/**/*.txt",
        "sagco-true/wafers/**/*.sagco",
    ],
    "citizens":  ["citizens/**/*.yaml","citizens/**/*.json","citizens/**/*.sagco"],
    "manifests": [
        "SAGCO_MANIFEST.json", "DIVISION_MANIFEST.json", "PROVENANCE.yaml",
        "palace.json",
    ],
    "kernels":   [
        "kernel/**/*.sagco",
        "sagco-true/kernel/**/*.sagco",
    ],
    "dna":       ["dna_cells/**/*.json", "dna/**/*.json", "data/**/*.json"],
    "logs":      ["data/**/*.log", "var/**/*.log"],
    "language":  [
        "sagco-true/language/**/*.py",
        "sagco-true/language/**/*.sagco",
    ],
}

KNOWN_NODE_HINTS: list[dict] = [
    {
        "id":   "local",
        "role": "source-of-truth",
        "paths": [],          # populated at runtime from __file__
    },
    {
        "id":   "wd-black",
        "role": "primary-memory",
        "paths": [
            r"E:\SAGCO-WORLD",
            r"E:/SAGCO-WORLD",
            "/mnt/e/SAGCO-WORLD",
        ],
    },
    {
        "id":   "docker",
        "role": "containerized-body",
        "paths": [
            "/var/sagco",
            "/sagco-world",
        ],
    },
    {
        "id":   "zfold",
        "role": "mobile-node",
        "paths": [
            "/data/data/com.termux/files/home/sagco-world",
            "~/sagco-world",
        ],
    },
    {
        "id":   "pi",
        "role": "edge-node",
        "paths": [
            "/home/pi/sagco-world",
            "~/sagco-world",
        ],
    },
]


# ── Data structures ──────────────────────────────────────────────────────────

@dataclass
class PalaceEntry:
    name: str
    kind: str           # board | agent | wafer | citizen | manifest | kernel | dna
    node: str
    path: str
    size: int = 0
    mtime: float = 0.0
    checksum: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name, "kind": self.kind,
            "node": self.node, "path": self.path,
            "size": self.size, "mtime": self.mtime,
            "checksum": self.checksum,
        }


@dataclass
class PalaceNode:
    id: str
    role: str
    root: str
    online: bool = False
    component_counts: dict[str, int] = field(default_factory=dict)
    last_scan: float = 0.0

    def to_dict(self) -> dict:
        return {
            "id": self.id, "role": self.role, "root": self.root,
            "online": self.online,
            "component_counts": self.component_counts,
            "last_scan": self.last_scan,
        }


@dataclass
class PalaceIndex:
    organism: str = "SAGCO"
    version: str = "0.1.0"
    cell_id: str = ""
    generated_at: float = field(default_factory=time.time)
    nodes: dict[str, PalaceNode] = field(default_factory=dict)
    entries: list[PalaceEntry] = field(default_factory=list)

    # fast-lookup maps built after scan
    _by_name: dict[str, list[PalaceEntry]] = field(default_factory=dict, repr=False)
    _by_kind: dict[str, list[PalaceEntry]] = field(default_factory=dict, repr=False)

    def _rebuild_lookups(self) -> None:
        self._by_name = {}
        self._by_kind = {}
        for e in self.entries:
            self._by_name.setdefault(e.name.lower(), []).append(e)
            self._by_kind.setdefault(e.kind, []).append(e)

    def locate(self, name: str) -> list[PalaceEntry]:
        self._rebuild_lookups()
        key = name.lower()
        exact = self._by_name.get(key, [])
        if exact:
            return exact
        # fuzzy: any entry whose name contains the query
        return [e for e in self.entries if key in e.name.lower()]

    def by_kind(self, kind: str) -> list[PalaceEntry]:
        self._rebuild_lookups()
        return self._by_kind.get(kind, [])

    def total_size_kb(self) -> float:
        return sum(e.size for e in self.entries) / 1024

    def to_dict(self) -> dict:
        return {
            "palace": {
                "organism": self.organism,
                "version": self.version,
                "cell_id": self.cell_id,
                "generated_at": self.generated_at,
            },
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "index": {
                kind: [e.to_dict() for e in entries]
                for kind, entries in self._by_kind.items()
            },
            "locator": {
                f"{e.kind}.{e.name}": {"node": e.node, "path": e.path}
                for e in self.entries
            },
            "summary": {
                "total_entries": len(self.entries),
                "total_size_kb": round(self.total_size_kb(), 1),
                "nodes_online": sum(1 for n in self.nodes.values() if n.online),
                "kinds": {k: len(v) for k, v in self._by_kind.items()},
            },
        }

    def save(self, path: str | Path) -> None:
        self._rebuild_lookups()
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))

    @staticmethod
    def load(path: str | Path) -> "PalaceIndex":
        raw = json.loads(Path(path).read_text())
        idx = PalaceIndex(
            organism=raw["palace"].get("organism", "SAGCO"),
            version=raw["palace"].get("version", "0.1.0"),
            cell_id=raw["palace"].get("cell_id", ""),
            generated_at=raw["palace"].get("generated_at", 0),
        )
        for nid, nd in raw.get("nodes", {}).items():
            idx.nodes[nid] = PalaceNode(
                id=nd["id"], role=nd["role"], root=nd["root"],
                online=nd.get("online", False),
                component_counts=nd.get("component_counts", {}),
                last_scan=nd.get("last_scan", 0),
            )
        for kind, entries in raw.get("index", {}).items():
            for ed in entries:
                idx.entries.append(PalaceEntry(**ed))
        idx._rebuild_lookups()
        return idx


# ── Scanner ──────────────────────────────────────────────────────────────────

def _sha256_fast(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)      # first 8KB only — palace is for discovery, not integrity
            h.update(chunk)
    except (PermissionError, OSError):
        pass
    return h.hexdigest()[:16]


def _scan_root(root: Path, node_id: str) -> list[PalaceEntry]:
    entries: list[PalaceEntry] = []
    if not root.exists() or not root.is_dir():
        return entries

    for kind, globs in COMPONENT_GLOBS.items():
        for pattern in globs:
            for fpath in root.glob(pattern):
                if not fpath.is_file():
                    continue
                try:
                    stat = fpath.stat()
                    rel = str(fpath.relative_to(root))
                    name = fpath.stem
                    entries.append(PalaceEntry(
                        name=name,
                        kind=kind,
                        node=node_id,
                        path=rel,
                        size=stat.st_size,
                        mtime=stat.st_mtime,
                        checksum=_sha256_fast(fpath),
                    ))
                except (PermissionError, OSError):
                    continue

    return entries


def _probe_node(hint: dict, local_root: Path) -> PalaceNode | None:
    node_id = hint["id"]
    paths = hint["paths"]

    if node_id == "local":
        paths = [str(local_root)]

    for raw_path in paths:
        p = Path(raw_path).expanduser()
        if p.exists():
            return PalaceNode(
                id=node_id,
                role=hint["role"],
                root=str(p),
                online=True,
            )

    # node not found locally — record as offline
    return PalaceNode(
        id=node_id,
        role=hint["role"],
        root=paths[0] if paths else "",
        online=False,
    )


def scan(
    organism_root: str | Path | None = None,
    include_offline_nodes: bool = True,
    verbose: bool = False,
) -> PalaceIndex:
    if organism_root is None:
        organism_root = Path(__file__).parent.parent.parent.resolve()
    local_root = Path(organism_root).resolve()

    idx = PalaceIndex(
        cell_id=hashlib.sha256(
            f"{local_root}:{time.time()}".encode()
        ).hexdigest()[:16],
        generated_at=time.time(),
    )

    # Patch local hint
    hints = [dict(h) for h in KNOWN_NODE_HINTS]
    for h in hints:
        if h["id"] == "local":
            h["paths"] = [str(local_root)]

    for hint in hints:
        node = _probe_node(hint, local_root)
        if node is None:
            continue
        if not node.online and not include_offline_nodes:
            continue

        idx.nodes[node.id] = node

        if node.online:
            if verbose:
                print(f"  Scanning {node.id} @ {node.root} ...")
            entries = _scan_root(Path(node.root), node.id)
            idx.entries.extend(entries)

            # Update node component counts
            counts: dict[str, int] = {}
            for e in entries:
                counts[e.kind] = counts.get(e.kind, 0) + 1
            node.component_counts = counts
            node.last_scan = time.time()

    idx._rebuild_lookups()
    return idx


# ── Diff ──────────────────────────────────────────────────────────────────────

@dataclass
class PalaceDiffEntry:
    kind: str
    name: str
    path: str
    status: str     # only-in-a | only-in-b | checksum-differs | identical


def diff_nodes(
    idx: PalaceIndex,
    node_a: str,
    node_b: str,
) -> list[PalaceDiffEntry]:
    a_entries = {(e.kind, e.name): e for e in idx.entries if e.node == node_a}
    b_entries = {(e.kind, e.name): e for e in idx.entries if e.node == node_b}

    result: list[PalaceDiffEntry] = []
    all_keys = set(a_entries) | set(b_entries)

    for key in sorted(all_keys):
        kind, name = key
        if key in a_entries and key not in b_entries:
            result.append(PalaceDiffEntry(
                kind=kind, name=name,
                path=a_entries[key].path, status="only-in-a"
            ))
        elif key not in a_entries and key in b_entries:
            result.append(PalaceDiffEntry(
                kind=kind, name=name,
                path=b_entries[key].path, status="only-in-b"
            ))
        else:
            ea, eb = a_entries[key], b_entries[key]
            status = "identical" if ea.checksum == eb.checksum else "checksum-differs"
            result.append(PalaceDiffEntry(
                kind=kind, name=name,
                path=ea.path, status=status
            ))

    return result


# ── Status printer ───────────────────────────────────────────────────────────

def print_status(idx: PalaceIndex) -> None:
    print(f"\n{'═'*56}")
    print(f"  SAGCO Memory Palace — Sovereign Index")
    print(f"  Cell: {idx.cell_id}   v{idx.version}")
    print(f"{'═'*56}")

    print(f"\n  Nodes ({len(idx.nodes)}):")
    for node in idx.nodes.values():
        icon = "●" if node.online else "○"
        counts = "  ".join(
            f"{k}:{v}" for k, v in sorted(node.component_counts.items())
        )
        print(f"  {icon} {node.id:12s}  {node.role:20s}  {counts or '(empty)'}")

    idx._rebuild_lookups()
    print(f"\n  Index ({len(idx.entries)} entries  {idx.total_size_kb():.1f} KB):")
    for kind in sorted(idx._by_kind):
        entries = idx._by_kind[kind]
        print(f"    {kind:12s}: {len(entries):4d}")

    print(f"\n  Status: {'PALACE_MAPPED' if idx.entries else 'PALACE_EMPTY'}")
    print(f"{'═'*56}\n")


PALACE_FILE = "palace.yaml"   # conventional name; saved as JSON internally

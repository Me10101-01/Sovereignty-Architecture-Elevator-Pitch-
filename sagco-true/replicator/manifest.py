"""
SAGCO Organism Manifest
The manifest IS the DNA of a deployed organism instance.
It knows every file, its checksum, its component role, and its generation.

Manifest chain:
  Genesis cell (generation 0) → Pi clone (generation 1) → HP fork (generation 2)

A manifest on the target is how the replicator knows what already exists.
If there's no manifest, it's a fresh replicate. If there is one, it diffs.
"""

from __future__ import annotations
import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ── Component registry — what parts the organism has ─────────────────────

MANIFEST_FILENAME = "SAGCO_MANIFEST.json"


COMPONENT_REGISTRY: dict[str, dict] = {
    "kernel":      {"required": True,  "path": "kernel/",      "role": "boot sequence"},
    "language":    {"required": True,  "path": "language/",    "role": "lexer/parser/vm"},
    "wafers":      {"required": True,  "path": "wafers/",      "role": "truth tests"},
    "antibodies":  {"required": True,  "path": "antibodies/",  "role": "self-healing"},
    "worlds":      {"required": False, "path": "worlds/",      "role": "environment adapters"},
    "replicator":  {"required": False, "path": "replicator/",  "role": "self-replication"},
    "boards":      {"required": False, "path": "boards/",      "role": "project containers"},
    "apps":        {"required": False, "path": "apps/",        "role": "user applications"},
    "data":        {"required": False, "path": "data/",        "role": "knowledge store"},
    "drivers":     {"required": False, "path": "drivers/",     "role": "hardware interfaces"},
    "tests":       {"required": False, "path": "tests/",       "role": "test suite"},
}

MODES = {
    "full":    "complete organism clone — all components",
    "smart":   "differential — only what changed since last replicate",
    "minimal": "core only — kernel + language + wafers + antibodies",
    "verify":  "integrity check only — no writes",
}


@dataclass
class FileRecord:
    path: str           # relative to organism root
    checksum: str       # sha256 hex
    size: int
    mtime: float
    component: str


@dataclass
class ManifestComponent:
    name: str
    required: bool
    role: str
    checksum: str       # hash of all file hashes in component
    file_count: int
    total_size: int


@dataclass
class OrganismManifest:
    cell_id: str
    organism: str = "SAGCO"
    version: str = "0.1.0"
    generation: int = 1
    parent_cell: str | None = None
    source_root: str = ""
    target_name: str = ""
    created_at: float = field(default_factory=time.time)
    components: dict[str, ManifestComponent] = field(default_factory=dict)
    files: dict[str, FileRecord] = field(default_factory=dict)
    mode: str = "full"
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "cell_id":     self.cell_id,
            "organism":    self.organism,
            "version":     self.version,
            "generation":  self.generation,
            "parent_cell": self.parent_cell,
            "source_root": self.source_root,
            "target_name": self.target_name,
            "created_at":  self.created_at,
            "mode":        self.mode,
            "components": {
                k: {
                    "required": v.required, "role": v.role,
                    "checksum": v.checksum, "file_count": v.file_count,
                    "total_size": v.total_size,
                }
                for k, v in self.components.items()
            },
            "file_count":  len(self.files),
            "total_size":  sum(f.size for f in self.files.values()),
            "extra":       self.extra,
        }

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))

    @staticmethod
    def load(path: str | Path) -> "OrganismManifest":
        raw = json.loads(Path(path).read_text())
        m = OrganismManifest(
            cell_id=raw["cell_id"],
            organism=raw.get("organism", "SAGCO"),
            version=raw.get("version", "0.1.0"),
            generation=raw.get("generation", 1),
            parent_cell=raw.get("parent_cell"),
            source_root=raw.get("source_root", ""),
            target_name=raw.get("target_name", ""),
            created_at=raw.get("created_at", 0),
            mode=raw.get("mode", "full"),
            extra=raw.get("extra", {}),
        )
        for name, c in raw.get("components", {}).items():
            m.components[name] = ManifestComponent(
                name=name, required=c["required"], role=c["role"],
                checksum=c["checksum"], file_count=c["file_count"],
                total_size=c["total_size"],
            )
        return m


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
    except (PermissionError, OSError):
        pass
    return h.hexdigest()


def _component_checksum(records: list[FileRecord]) -> str:
    h = hashlib.sha256()
    for r in sorted(records, key=lambda x: x.path):
        h.update(r.checksum.encode())
    return h.hexdigest()[:16]


def build_manifest(
    organism_root: str | Path,
    mode: str = "full",
    target_name: str = "",
    parent_manifest: "OrganismManifest | None" = None,
    extra: dict | None = None,
) -> OrganismManifest:
    root = Path(organism_root)
    cell_id = hashlib.sha256(
        f"{target_name}:{mode}:{time.time()}:{uuid.uuid4()}".encode()
    ).hexdigest()[:16]

    generation = (parent_manifest.generation + 1) if parent_manifest else 1
    parent_cell = parent_manifest.cell_id if parent_manifest else None

    # which components to include based on mode
    if mode == "minimal":
        include = {k for k, v in COMPONENT_REGISTRY.items() if v["required"]}
    else:
        include = set(COMPONENT_REGISTRY.keys())

    manifest = OrganismManifest(
        cell_id=cell_id,
        generation=generation,
        parent_cell=parent_cell,
        source_root=str(root),
        target_name=target_name,
        mode=mode,
        extra=extra or {},
    )

    for comp_name in include:
        comp_info = COMPONENT_REGISTRY[comp_name]
        comp_path = root / comp_info["path"]
        if not comp_path.exists():
            continue

        records: list[FileRecord] = []
        for fpath in sorted(comp_path.rglob("*")):
            if fpath.is_file() and not any(
                p in fpath.parts for p in (".git", "__pycache__", ".sagcob")
            ):
                rel = str(fpath.relative_to(root))
                stat = fpath.stat()
                rec = FileRecord(
                    path=rel,
                    checksum=_sha256(fpath),
                    size=stat.st_size,
                    mtime=stat.st_mtime,
                    component=comp_name,
                )
                records.append(rec)
                manifest.files[rel] = rec

        manifest.components[comp_name] = ManifestComponent(
            name=comp_name,
            required=comp_info["required"],
            role=comp_info["role"],
            checksum=_component_checksum(records),
            file_count=len(records),
            total_size=sum(r.size for r in records),
        )

    return manifest


if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    m = build_manifest(root, mode="full", target_name="test")
    print(json.dumps(m.to_dict(), indent=2))
    print(f"\nTotal files: {len(m.files)}")
    print(f"Components:  {list(m.components.keys())}")

"""
SAGCO DNA Cell Engine
Ingests any README (or text document) and converts it to a DNA Cell —
a self-describing, hash-chained, generation-aware data structure that
acts as the atomic unit of SAGCO's knowledge fabric.

DNA Cell anatomy (biological metaphor → system mapping):
  Nucleus       → identity: name, version, purpose
  Membrane      → interfaces: APIs, ports, entry points
  Mitochondria  → executors: scripts, workflows, commands
  Ribosomes     → token generators: config vars, env keys
  Cytoplasm     → raw content blob (compressed fingerprint)
  DNA Strand    → base64 hash chain linking generations
"""

from __future__ import annotations
import base64
import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ── Codon table — maps README section headings to organelles ───────────────

CODON_MAP: dict[str, str] = {
    # nucleus codons
    "overview": "nucleus", "about": "nucleus", "description": "nucleus",
    "introduction": "nucleus", "what": "nucleus", "summary": "nucleus",
    # membrane codons
    "api": "membrane", "interface": "membrane", "port": "membrane",
    "endpoint": "membrane", "route": "membrane", "usage": "membrane",
    "command": "membrane",
    # mitochondria codons
    "install": "mitochondria", "deploy": "mitochondria", "run": "mitochondria",
    "script": "mitochondria", "workflow": "mitochondria", "pipeline": "mitochondria",
    "build": "mitochondria", "setup": "mitochondria", "getting started": "mitochondria",
    # ribosome codons
    "config": "ribosomes", "environment": "ribosomes", "variable": "ribosomes",
    "setting": "ribosomes", "option": "ribosomes", "parameter": "ribosomes",
    "env": "ribosomes",
    # cytoplasm (catch-all)
    "license": "cytoplasm", "changelog": "cytoplasm", "history": "cytoplasm",
    "credits": "cytoplasm", "author": "cytoplasm", "contact": "cytoplasm",
}


@dataclass
class Organelle:
    name: str
    fragments: list[str] = field(default_factory=list)

    def digest(self) -> str:
        blob = "\n".join(self.fragments)
        return hashlib.sha256(blob.encode()).hexdigest()[:12]

    def to_dict(self) -> dict:
        return {"organelle": self.name, "digest": self.digest(),
                "fragment_count": len(self.fragments),
                "preview": self.fragments[0][:120] if self.fragments else ""}


@dataclass
class DNACell:
    cell_id: str
    generation: int
    parent_id: str | None
    name: str
    source_path: str
    created_at: float

    nucleus: Organelle = field(default_factory=lambda: Organelle("nucleus"))
    membrane: Organelle = field(default_factory=lambda: Organelle("membrane"))
    mitochondria: Organelle = field(default_factory=lambda: Organelle("mitochondria"))
    ribosomes: Organelle = field(default_factory=lambda: Organelle("ribosomes"))
    cytoplasm: Organelle = field(default_factory=lambda: Organelle("cytoplasm"))

    dna_strand: str = ""        # base64 hash chain
    metadata: dict = field(default_factory=dict)

    def organelles(self) -> list[Organelle]:
        return [self.nucleus, self.membrane, self.mitochondria,
                self.ribosomes, self.cytoplasm]

    def _weave_strand(self) -> str:
        chain = ":".join(o.digest() for o in self.organelles())
        chain_bytes = f"{self.cell_id}:{self.generation}:{chain}".encode()
        return base64.b64encode(hashlib.sha256(chain_bytes).digest()).decode()

    def finalize(self) -> "DNACell":
        self.dna_strand = self._weave_strand()
        return self

    def to_dict(self) -> dict:
        return {
            "cell_id":     self.cell_id,
            "generation":  self.generation,
            "parent_id":   self.parent_id,
            "name":        self.name,
            "source_path": self.source_path,
            "created_at":  self.created_at,
            "dna_strand":  self.dna_strand,
            "organelles": {
                o.name: o.to_dict() for o in self.organelles()
            },
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


# ── Ribosomes extractor — pulls env vars, config keys from content ─────────

_ENV_PATTERN = re.compile(r'\b([A-Z][A-Z0-9_]{2,})\b')
_CODE_BLOCK   = re.compile(r'```[^\n]*\n(.*?)```', re.DOTALL)


def _extract_ribosomes(content: str) -> list[str]:
    tokens: list[str] = []
    # pull from code blocks first
    for block in _CODE_BLOCK.findall(content):
        tokens.extend(_ENV_PATTERN.findall(block))
    # deduplicate while preserving order
    seen: set[str] = set()
    result: list[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            result.append(t)
    return result


# ── Main ingestion function ────────────────────────────────────────────────

_SECTION_RE = re.compile(r'^#{1,4}\s+(.+)$', re.MULTILINE)


def ingest_to_dna(
    name: str,
    content: str,
    source_path: str = "",
    parent_id: str | None = None,
    generation: int = 1,
    extra_meta: dict | None = None,
) -> dict:
    cell_id = hashlib.sha256(
        f"{name}:{source_path}:{time.time()}".encode()
    ).hexdigest()[:16]

    cell = DNACell(
        cell_id=cell_id,
        generation=generation,
        parent_id=parent_id,
        name=name,
        source_path=source_path,
        created_at=time.time(),
    )

    # ── split content at section headings ──────────────────────────────────
    sections: list[tuple[str, str]] = []
    positions = [(m.start(), m.group(1)) for m in _SECTION_RE.finditer(content)]
    positions.append((len(content), "__END__"))

    if not positions or positions[0][0] > 0:
        preamble = content[:positions[0][0]] if positions else content
        sections.append(("__preamble__", preamble.strip()))

    for i, (start, heading) in enumerate(positions[:-1]):
        end = positions[i + 1][0]
        body = content[start:end].strip()
        sections.append((heading.lower(), body))

    # ── distribute sections into organelles via codon map ─────────────────
    for heading, body in sections:
        if not body:
            continue
        organelle_name = "cytoplasm"  # default
        for codon, target in CODON_MAP.items():
            if codon in heading:
                organelle_name = target
                break
        getattr(cell, organelle_name).fragments.append(body)

    # ── preamble always seeds nucleus ──────────────────────────────────────
    for heading, body in sections:
        if heading == "__preamble__" and body:
            cell.nucleus.fragments.insert(0, body)
            break

    # ── ribosomes: harvest env tokens ─────────────────────────────────────
    env_tokens = _extract_ribosomes(content)
    if env_tokens:
        cell.ribosomes.fragments.append(f"ENV_TOKENS: {', '.join(env_tokens[:64])}")

    # ── metadata ──────────────────────────────────────────────────────────
    cell.metadata = {
        "word_count": len(content.split()),
        "section_count": len(sections),
        "env_token_count": len(env_tokens),
        "has_code_blocks": bool(_CODE_BLOCK.search(content)),
        **(extra_meta or {}),
    }

    cell.finalize()
    return cell.to_dict()


# ── Folder-level batch ingest ──────────────────────────────────────────────

def ingest_folder(root: str | Path, pattern: str = "README*") -> list[dict]:
    root = Path(root)
    cells: list[dict] = []
    parent_id: str | None = None

    for path in sorted(root.rglob(pattern)):
        if path.name.startswith("."):
            continue
        content = path.read_text(errors="replace")
        cell = ingest_to_dna(
            name=path.name,
            content=content,
            source_path=str(path),
            parent_id=parent_id,
            generation=len(cells) + 1,
        )
        parent_id = cell["cell_id"]
        cells.append(cell)

    return cells


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "README.md"
    path = Path(target)
    if path.exists():
        content = path.read_text()
        result = ingest_to_dna(path.name, content, str(path))
        print(json.dumps(result, indent=2))
    else:
        print(f"[dna_cell] File not found: {target}")

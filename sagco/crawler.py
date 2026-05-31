"""
SAGCO Stepper Crawler Pipeline
Autonomous token creation: walks every folder, mints a SAGCOToken for each,
then links them into a directed pipeline graph. Optionally ingests READMEs
as DNA cells per folder.

Stepper model:
  Each directory = one step.
  Each step emits: folder token + optional DNA cell.
  Steps are linked in walk order → forms a pipeline chain.
  The chain is registered in the VM's token bus.
"""

from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .vm import VM


@dataclass
class FolderToken:
    token_id: str
    path: str
    depth: int
    file_count: int
    subdir_count: int
    readme_path: str | None
    dna_cell: dict | None
    tags: list[str]
    created_at: float = field(default_factory=time.time)
    next_token_id: str | None = None    # linked-list pointer

    def to_dict(self) -> dict:
        return {
            "token_id":      self.token_id,
            "path":          self.path,
            "depth":         self.depth,
            "file_count":    self.file_count,
            "subdir_count":  self.subdir_count,
            "readme_path":   self.readme_path,
            "dna_cell_id":   self.dna_cell["cell_id"] if self.dna_cell else None,
            "tags":          self.tags,
            "created_at":    self.created_at,
            "next_token_id": self.next_token_id,
        }


def _folder_token_id(path: str, depth: int) -> str:
    return hashlib.sha256(f"{path}:{depth}:{time.time()}".encode()).hexdigest()[:12]


@dataclass
class PipelineGraph:
    tokens: list[FolderToken] = field(default_factory=list)
    edges: list[tuple[str, str]] = field(default_factory=list)

    def append(self, token: FolderToken) -> None:
        if self.tokens:
            prev = self.tokens[-1]
            prev.next_token_id = token.token_id
            self.edges.append((prev.token_id, token.token_id))
        self.tokens.append(token)

    def to_summary(self) -> dict:
        return {
            "total_steps":   len(self.tokens),
            "total_edges":   len(self.edges),
            "total_files":   sum(t.file_count for t in self.tokens),
            "dna_cells":     sum(1 for t in self.tokens if t.dna_cell),
            "chain_head":    self.tokens[0].token_id if self.tokens else None,
            "chain_tail":    self.tokens[-1].token_id if self.tokens else None,
        }

    def to_dict(self) -> dict:
        return {
            "summary": self.to_summary(),
            "pipeline": [t.to_dict() for t in self.tokens],
            "edges":    self.edges,
        }


class StepperCrawler:
    """
    Walks a directory tree step-by-step.
    Each folder is one pipeline step.
    Emits FolderTokens and optionally DNA cells for README files.
    """

    def __init__(
        self,
        root: str | Path,
        vm: "VM | None" = None,
        max_depth: int = 6,
        ingest_readmes: bool = True,
        skip_hidden: bool = True,
    ) -> None:
        self.root = Path(root)
        self.vm = vm
        self.max_depth = max_depth
        self.ingest_readmes = ingest_readmes
        self.skip_hidden = skip_hidden

    def run(self) -> dict:
        graph = PipelineGraph()
        self._step(self.root, depth=0, graph=graph)

        # push all tokens onto the VM bus if attached
        if self.vm is not None:
            from .vm import _make_token
            for folder_tok in graph.tokens:
                bus_tok = _make_token(
                    "crawler",
                    folder_tok.to_dict(),
                    tags=folder_tok.tags,
                )
                self.vm.bus.append(bus_tok)

        return graph.to_dict()

    def _step(self, path: Path, depth: int, graph: PipelineGraph) -> None:
        if depth > self.max_depth:
            return
        if self.skip_hidden and path.name.startswith("."):
            return
        if not path.is_dir():
            return

        entries = list(path.iterdir())
        files = [e for e in entries if e.is_file() and not e.name.startswith(".")]
        subdirs = [e for e in entries if e.is_dir() and not e.name.startswith(".")]

        # README detection
        readme: Path | None = None
        for candidate in ("README.md", "README.txt", "README.rst", "README"):
            maybe = path / candidate
            if maybe.exists():
                readme = maybe
                break

        # DNA cell generation
        dna_cell: dict | None = None
        if self.ingest_readmes and readme is not None:
            from .dna_cell import ingest_to_dna
            try:
                content = readme.read_text(errors="replace")
                dna_cell = ingest_to_dna(
                    name=readme.name,
                    content=content,
                    source_path=str(readme),
                    generation=depth + 1,
                )
            except Exception:
                pass

        # tags
        tags = ["folder", f"depth:{depth}"]
        if readme:
            tags.append("has_readme")
        if dna_cell:
            tags.append("has_dna")
        if depth == 0:
            tags.append("root")

        token = FolderToken(
            token_id=_folder_token_id(str(path), depth),
            path=str(path.relative_to(self.root)) if path != self.root else ".",
            depth=depth,
            file_count=len(files),
            subdir_count=len(subdirs),
            readme_path=str(readme.relative_to(self.root)) if readme else None,
            dna_cell=dna_cell,
            tags=tags,
        )
        graph.append(token)

        # recurse
        for sub in sorted(subdirs):
            self._step(sub, depth + 1, graph)


def crawl_to_pipeline(
    root: str | Path,
    max_depth: int = 6,
    ingest_readmes: bool = True,
    output_path: str | Path | None = None,
) -> dict:
    crawler = StepperCrawler(root, max_depth=max_depth, ingest_readmes=ingest_readmes)
    result = crawler.run()

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2))

    return result


if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    result = crawl_to_pipeline(root, max_depth=depth)
    summary = result["summary"]
    print(f"Steps:  {summary['total_steps']}")
    print(f"Files:  {summary['total_files']}")
    print(f"DNA:    {summary['dna_cells']}")
    print(f"Head:   {summary['chain_head']}")
    print(f"Tail:   {summary['chain_tail']}")
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))

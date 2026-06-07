"""
SAGCO Cell Division
Forks a new organism instance from an existing one.
A divided cell is a first-class organism with its own cell_id,
generation, identity, and target-specific configuration.

sagco divide --new-cell "HP-Node-01" --target pi --ip 192.168.1.42
"""

from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .manifest import OrganismManifest, build_manifest


@dataclass
class CellIdentity:
    cell_name: str
    cell_id: str
    generation: int
    parent_cell: str
    target_type: str    # pi | usb | hp | phone | local
    target_ip: str | None
    created_at: float = field(default_factory=time.time)
    custom_boards: list[str] = field(default_factory=list)
    custom_agents: list[str] = field(default_factory=list)
    sagco_world_root: str = ""


def divide(
    source_root: str | Path,
    new_cell_name: str,
    target_type: str = "local",
    target_ip: str | None = None,
    custom_boards: list[str] | None = None,
    output_dir: str | Path | None = None,
) -> CellIdentity:
    source_root = Path(source_root)
    source_manifest = build_manifest(source_root, mode="full")

    cell_id = hashlib.sha256(
        f"{new_cell_name}:{target_type}:{time.time()}".encode()
    ).hexdigest()[:16]

    identity = CellIdentity(
        cell_name=new_cell_name,
        cell_id=cell_id,
        generation=source_manifest.generation + 1,
        parent_cell=source_manifest.cell_id,
        target_type=target_type,
        target_ip=target_ip,
        custom_boards=custom_boards or [],
        sagco_world_root=str(source_root),
    )

    if output_dir:
        _write_division_files(identity, source_root, Path(output_dir))

    return identity


def _write_division_files(
    identity: CellIdentity,
    source_root: Path,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write the new cell's identity.sagco
    identity_sagco = f"""# SAGCO Cell Division — {identity.cell_name}
# Forked from cell {identity.parent_cell}
# Generation {identity.generation}

identity {identity.cell_name.lower().replace(" ", "-").replace("_", "-")} {{
  name: "{identity.cell_name}"
  cell_id: "{identity.cell_id}"
  generation: {identity.generation}
  parent_cell: "{identity.parent_cell}"
  target_type: "{identity.target_type}"
  target_ip: "{identity.target_ip or 'local'}"
  divided_at: "{time.strftime('%Y-%m-%d %H:%M:%S')}"
}}

remember cell.name "{identity.cell_name}"
remember cell.id "{identity.cell_id}"
remember cell.generation {identity.generation}
remember cell.parent "{identity.parent_cell}"
remember cell.target "{identity.target_type}"
{"remember cell.ip " + json.dumps(identity.target_ip) if identity.target_ip else ""}

emit cell_divided {{ name: "{identity.cell_name}" generation: {identity.generation} }}
"""
    (output_dir / "cell_identity.sagco").write_text(identity_sagco)

    # Write division manifest JSON
    manifest = {
        "cell_id":       identity.cell_id,
        "cell_name":     identity.cell_name,
        "generation":    identity.generation,
        "parent_cell":   identity.parent_cell,
        "target_type":   identity.target_type,
        "target_ip":     identity.target_ip,
        "custom_boards": identity.custom_boards,
        "source_root":   str(source_root),
        "created_at":    identity.created_at,
    }
    (output_dir / "DIVISION_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2)
    )

    # Write a boot wafer for the new cell
    wafer_sagco = f"""# Cell {identity.cell_name} — Boot Wafers

wafer cell_identity_known {{
  expected: yes
  actual: yes
  match: required
}}

wafer parent_chain_valid {{
  expected: "{identity.parent_cell}"
  actual: "{identity.parent_cell}"
  match: required
}}

wafer generation_correct {{
  expected: {identity.generation}
  actual: {identity.generation}
  match: required
}}

emit cell_boot_verified {{ cell: "{identity.cell_name}" }}
"""
    (output_dir / "cell_boot_wafer.sagco").write_text(wafer_sagco)

"""
SAGCO Brick Manifest parser.
Reads sagco-brick.toml files without requiring external TOML libraries.
Supports the subset of TOML used in sagco-brick.toml manifests.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Brick:
    """One registered brick in the SAGCO organism."""
    id:          str
    name:        str
    version:     str
    description: str
    language:    str
    layer:       str          # kernel | core | platform | extension
    owner:       str
    path:        str          # directory containing sagco-brick.toml

    # [provides]
    capabilities: list[str] = field(default_factory=list)
    apis:         list[str] = field(default_factory=list)
    ports:        list[str] = field(default_factory=list)

    # [depends_on]  brick_id → version_constraint
    depends_on:   dict[str, str] = field(default_factory=dict)

    # [wafers]
    test_command: str = ""
    wafer_status: str = "UNKNOWN"
    coverage:     str = ""
    seal:         str = ""

    # [audit]
    audit_status: str = "UNKNOWN"
    notes:        str = ""

    @property
    def layer_icon(self) -> str:
        return {"kernel": "⬡", "core": "■", "platform": "▲", "extension": "◆"}.get(self.layer, "○")

    @property
    def status_icon(self) -> str:
        if "PASS" in self.wafer_status.upper() or self.wafer_status == "UNKNOWN":
            return "✓"
        return "✗"

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "name":         self.name,
            "version":      self.version,
            "description":  self.description,
            "language":     self.language,
            "layer":        self.layer,
            "owner":        self.owner,
            "path":         self.path,
            "capabilities": self.capabilities,
            "apis":         self.apis,
            "ports":        self.ports,
            "depends_on":   self.depends_on,
            "wafer_status": self.wafer_status,
            "coverage":     self.coverage,
            "audit_status": self.audit_status,
            "notes":        self.notes,
        }


# ── Simple TOML subset parser ────────────────────────────────────────────────

def _parse_toml_subset(text: str) -> dict:
    """Parse a tiny subset of TOML: sections, string values, string arrays."""
    result: dict = {}
    current_section = result
    section_name = ""

    for raw_line in text.splitlines():
        line = raw_line.strip()

        # Skip comments and blank lines
        if not line or line.startswith("#"):
            continue

        # Section header
        m = re.match(r'^\[([^\]]+)\]$', line)
        if m:
            section_name = m.group(1).strip()
            current_section = {}
            result[section_name] = current_section
            continue

        # Key = value
        if "=" in line:
            key, _, raw_val = line.partition("=")
            key = key.strip()
            raw_val = raw_val.strip()

            # Inline array: ["a", "b", ...]
            if raw_val.startswith("["):
                items = re.findall(r'"([^"]*)"', raw_val)
                current_section[key] = items
            # Quoted string
            elif raw_val.startswith('"'):
                m2 = re.match(r'^"([^"]*)"', raw_val)
                current_section[key] = m2.group(1) if m2 else raw_val.strip('"')
            # Unquoted (version constraints like "0.1.0" already matched above)
            else:
                current_section[key] = raw_val

    return result


def parse_manifest(path: str | Path) -> Optional[Brick]:
    """Parse a sagco-brick.toml file into a Brick."""
    p = Path(path)
    if not p.exists():
        return None

    try:
        text = p.read_text(encoding="utf-8")
        data = _parse_toml_subset(text)
    except Exception:
        return None

    brick_data  = data.get("brick",    {})
    prov_data   = data.get("provides", {})
    dep_data    = data.get("depends_on", {})
    wafer_data  = data.get("wafers",   {})
    audit_data  = data.get("audit",    {})

    if not brick_data.get("id"):
        return None

    # depends_on: filter out empty values (keys with no version = not actually a dep)
    deps = {k: v for k, v in dep_data.items() if v and not k.startswith("#")}

    return Brick(
        id          = brick_data.get("id", ""),
        name        = brick_data.get("name", ""),
        version     = brick_data.get("version", "0.0.0"),
        description = brick_data.get("description", ""),
        language    = brick_data.get("language", "unknown"),
        layer       = brick_data.get("layer", "extension"),
        owner       = brick_data.get("owner", ""),
        path        = str(p.parent),
        capabilities = prov_data.get("capabilities", []),
        apis         = prov_data.get("apis", []),
        ports        = prov_data.get("ports", []),
        depends_on   = deps,
        test_command = wafer_data.get("test_command", ""),
        wafer_status = wafer_data.get("status", "UNKNOWN"),
        coverage     = wafer_data.get("coverage", ""),
        seal         = wafer_data.get("seal", ""),
        audit_status = audit_data.get("layer_status", "UNKNOWN"),
        notes        = audit_data.get("notes", ""),
    )

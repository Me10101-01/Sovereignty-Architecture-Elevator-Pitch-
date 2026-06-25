#!/usr/bin/env python3
"""
antibody_registry.py — Central antibody registry for the SAGCO organism

Single source of truth for all known antibodies.
sagco-graph/ and sagco-security/ inherit from here — never define antibodies inline.

Registry file: registry/antibody_registry.yaml
"""

import yaml
from pathlib import Path


DEFAULT_REGISTRY = Path(__file__).parent.parent / "registry" / "antibody_registry.yaml"


def load_registry(path: Path = DEFAULT_REGISTRY) -> dict:
    if not path.exists():
        return {"antibodies": [], "total": 0}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def print_registry(registry: dict) -> None:
    antibodies = registry.get("antibodies", [])
    total = registry.get("total", len(antibodies))
    print(f"\n  SAGCO Antibody Registry — {total} entries")
    print(f"  {'─'*70}")
    for ab in antibodies:
        sev = ab.get("severity", "?")
        ab_id = ab.get("id", "?")
        trigger = ab.get("trigger", "")[:55]
        domain = ab.get("domain", "sagco")
        print(f"  [{sev:6s}] {ab_id:35s} [{domain:10s}] {trigger}")


def get_by_id(ab_id: str, path: Path = DEFAULT_REGISTRY) -> dict | None:
    registry = load_registry(path)
    for ab in registry.get("antibodies", []):
        if ab.get("id") == ab_id:
            return ab
    return None


def get_by_domain(domain: str, path: Path = DEFAULT_REGISTRY) -> list[dict]:
    registry = load_registry(path)
    return [ab for ab in registry.get("antibodies", []) if ab.get("domain") == domain]

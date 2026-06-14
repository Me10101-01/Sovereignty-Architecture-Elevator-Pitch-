"""
SAGCO Brick Registry
Strategickhaos DAO LLC

Tracks every brick in the organism:
  what exists · where it lives · what it provides · what it needs · its health

Usage:
  from sagco_true.registry import Registry
  r = Registry.scan()
  print(r.summary())
"""

from .manifest import Brick, parse_manifest
from .scanner  import scan_bricks, find_manifests
from .resolver import resolve_deps, topological_order, dep_tree_str
from .graph    import ascii_graph
from .store    import Registry, save_registry, load_registry

__all__ = [
    "Brick", "parse_manifest",
    "scan_bricks", "find_manifests",
    "resolve_deps", "topological_order", "dep_tree_str",
    "ascii_graph",
    "Registry", "save_registry", "load_registry",
]

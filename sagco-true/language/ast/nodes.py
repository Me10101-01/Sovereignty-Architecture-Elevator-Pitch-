"""
SAGCO True Language — AST Node Types
Every .sagco construct maps to exactly one node type.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


# ── Value nodes ───────────────────────────────────────────────────────────

@dataclass
class StringVal:
    value: str
    def __repr__(self): return f'"{self.value}"'

@dataclass
class NumberVal:
    value: int | float
    def __repr__(self): return str(self.value)

@dataclass
class BoolVal:
    value: bool
    def __repr__(self): return "yes" if self.value else "no"

@dataclass
class IdentVal:
    name: str
    def __repr__(self): return self.name

@dataclass
class ListVal:
    items: list[Any]
    def __repr__(self): return f"[{', '.join(repr(i) for i in self.items)}]"

@dataclass
class CallVal:
    func: str
    args: list[Any] = field(default_factory=list)
    def __repr__(self): return f"{self.func}({', '.join(repr(a) for a in self.args)})"


# ── Field (key: value pair inside a block) ────────────────────────────────

@dataclass
class Field:
    key: str
    value: Any


# ── Statement nodes ───────────────────────────────────────────────────────

@dataclass
class IdentityDecl:
    name: str
    fields: list[Field] = field(default_factory=list)


@dataclass
class BootDecl:
    steps: list[str] = field(default_factory=list)


@dataclass
class RememberStmt:
    key: str                  # dotpath or ident
    value: Any


@dataclass
class ForgetStmt:
    key: str


@dataclass
class LetStmt:
    name: str
    value: Any


@dataclass
class DoBlock:
    name: str
    body: list[Any] = field(default_factory=list)


@dataclass
class EmitStmt:
    signal: str
    payload: dict = field(default_factory=dict)


@dataclass
class MeasureStmt:
    target: str               # wafer name or "all_wafers"


@dataclass
class WaferDecl:
    name: str
    expected: Any = None
    actual: Any = None
    match_mode: str = "required"    # required | optional


@dataclass
class AntibodyDecl:
    name: str
    trigger: Any = None
    detect: Any = None
    response: Any = None
    heal: Any = None


@dataclass
class WorldBlock:
    name: str                 # windows | linux | termux | docker | kubernetes
    body: list[Any] = field(default_factory=list)


@dataclass
class ImportStmt:
    path: str
    alias: str | None = None


@dataclass
class ExportStmt:
    name: str


@dataclass
class SpawnStmt:
    agent: str
    config: dict = field(default_factory=dict)


@dataclass
class HaltStmt:
    target: str | None = None


# ── Top-level ─────────────────────────────────────────────────────────────

@dataclass
class Module:
    filename: str
    body: list[Any] = field(default_factory=list)

    def statements_of(self, *types) -> list[Any]:
        return [s for s in self.body if isinstance(s, types)]

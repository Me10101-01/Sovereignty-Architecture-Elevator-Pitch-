"""
SAGCO True Language — Bytecode Compiler
Walks the AST and emits Bytecode.
"""

from __future__ import annotations
from typing import Any
from ..ast.nodes import *
from .opcodes import Instruction, Op, Bytecode


def _val_to_python(val: Any) -> Any:
    if isinstance(val, StringVal):
        return val.value
    if isinstance(val, NumberVal):
        return val.value
    if isinstance(val, BoolVal):
        return val.value
    if isinstance(val, IdentVal):
        return val.name
    if isinstance(val, ListVal):
        return [_val_to_python(i) for i in val.items]
    if isinstance(val, CallVal):
        return f"__call__{val.func}"
    return val


class Compiler:
    def __init__(self) -> None:
        self._instructions: list[Instruction] = []
        self._label_counter = 0

    def _emit(self, op: Op, operand: Any = None, line: int = 0) -> None:
        self._instructions.append(Instruction(op, operand, line))

    def _new_label(self, prefix: str = "L") -> str:
        self._label_counter += 1
        return f"{prefix}_{self._label_counter}"

    def compile(self, mod: Module) -> Bytecode:
        self._emit(Op.LABEL, f"__module__{mod.filename}")
        for stmt in mod.body:
            self._compile_stmt(stmt)
        self._emit(Op.HALT)
        return Bytecode(self._instructions, mod.filename)

    def _compile_stmt(self, stmt: Any) -> None:
        if isinstance(stmt, IdentityDecl):
            for f in stmt.fields:
                self._emit(Op.PUSH, _val_to_python(f.value))
                self._emit(Op.STORE, f"{stmt.name}.{f.key}")

        elif isinstance(stmt, BootDecl):
            self._emit(Op.LABEL, "__boot__")
            for step in stmt.steps:
                self._emit(Op.CALL, step)

        elif isinstance(stmt, RememberStmt):
            self._emit(Op.PUSH, _val_to_python(stmt.value))
            self._emit(Op.STORE, stmt.key)

        elif isinstance(stmt, ForgetStmt):
            self._emit(Op.FORGET, stmt.key)

        elif isinstance(stmt, LetStmt):
            if isinstance(stmt.value, CallVal):
                self._emit(Op.DETECT, stmt.value.func)
            else:
                self._emit(Op.PUSH, _val_to_python(stmt.value))
            self._emit(Op.STORE, stmt.name)

        elif isinstance(stmt, DoBlock):
            label = f"__do__{stmt.name}"
            # emit procedure body as a labelled block
            self._emit(Op.LABEL, label)
            for s in stmt.body:
                self._compile_stmt(s)
            self._emit(Op.RETURN)

        elif isinstance(stmt, EmitStmt):
            for k, v in stmt.payload.items():
                self._emit(Op.PUSH, f"{k}={_val_to_python(v)}")
            self._emit(Op.EMIT, stmt.signal)

        elif isinstance(stmt, MeasureStmt):
            self._emit(Op.MEASURE, stmt.target)

        elif isinstance(stmt, WaferDecl):
            # wafer compiles to: push expected, push actual, MATCH, store result
            exp_label = f"__wafer__{stmt.name}"
            self._emit(Op.LABEL, exp_label)
            self._emit(Op.PUSH, _val_to_python(stmt.expected))
            if isinstance(stmt.actual, CallVal):
                self._emit(Op.DETECT, stmt.actual.func)
            else:
                self._emit(Op.PUSH, _val_to_python(stmt.actual))
            self._emit(Op.MATCH)
            self._emit(Op.STORE, f"wafer.{stmt.name}.result")
            self._emit(Op.PUSH, stmt.match_mode)
            self._emit(Op.STORE, f"wafer.{stmt.name}.mode")

        elif isinstance(stmt, AntibodyDecl):
            self._emit(Op.LABEL, f"__antibody__{stmt.name}")
            if stmt.detect is not None:
                self._emit(Op.DETECT, _val_to_python(stmt.detect))
                self._emit(Op.STORE, f"antibody.{stmt.name}.detected")
            if stmt.response is not None:
                self._emit(Op.PUSH, _val_to_python(stmt.response))
                self._emit(Op.STORE, f"antibody.{stmt.name}.response")
            if stmt.heal is not None:
                self._emit(Op.PUSH, _val_to_python(stmt.heal))
                self._emit(Op.STORE, f"antibody.{stmt.name}.heal")

        elif isinstance(stmt, WorldBlock):
            self._emit(Op.WORLD)
            self._emit(Op.PUSH, stmt.name)
            self._emit(Op.EQ)
            skip_label = self._new_label("world_skip")
            self._emit(Op.JUMP_NOT, skip_label)
            for s in stmt.body:
                self._compile_stmt(s)
            self._emit(Op.LABEL, skip_label)

        elif isinstance(stmt, SpawnStmt):
            for k, v in stmt.config.items():
                self._emit(Op.PUSH, f"{k}={_val_to_python(v)}")
            self._emit(Op.SPAWN, stmt.agent)

        elif isinstance(stmt, HaltStmt):
            self._emit(Op.HALT, stmt.target)

        elif isinstance(stmt, ImportStmt):
            self._emit(Op.READ, stmt.path)
            if stmt.alias:
                self._emit(Op.STORE, stmt.alias)


def compile_module(mod: Module) -> Bytecode:
    return Compiler().compile(mod)


def compile_source(source: str, filename: str = "<sagco>") -> Bytecode:
    from ..parser.parser import parse
    mod = parse(source, filename)
    return compile_module(mod)


if __name__ == "__main__":
    import sys
    src = open(sys.argv[1]).read() if len(sys.argv) > 1 else ""
    bc = compile_source(src, sys.argv[1] if len(sys.argv) > 1 else "<stdin>")
    print(bc.dump())

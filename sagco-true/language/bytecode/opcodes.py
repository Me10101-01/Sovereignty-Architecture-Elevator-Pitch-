"""
SAGCO True Language — Bytecode Opcodes
Stack-based instruction set. Text format for portability and readability.
Binary encoding reserved for v2.

Instruction format:
  OPCODE [operand]

Example:
  PUSH "SAGCO Kernel"
  STORE identity.name
  CALL detect_world
  EMIT kernel_ready
  HALT
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class Op(Enum):
    # Stack
    PUSH     = "PUSH"     # PUSH <value>     — push literal onto stack
    POP      = "POP"      # POP              — discard top of stack
    DUP      = "DUP"      # DUP              — duplicate top
    SWAP     = "SWAP"     # SWAP             — swap top two

    # Memory
    LOAD     = "LOAD"     # LOAD <key>       — push memory[key] onto stack
    STORE    = "STORE"    # STORE <key>      — pop stack, write to memory[key]
    FORGET   = "FORGET"   # FORGET <key>     — delete memory[key]

    # Control
    CALL     = "CALL"     # CALL <label>     — invoke named procedure
    RETURN   = "RETURN"   # RETURN           — return from procedure
    JUMP     = "JUMP"     # JUMP <offset>    — unconditional jump
    JUMP_IF  = "JUMP_IF"  # JUMP_IF <offset> — jump if top of stack is truthy
    JUMP_NOT = "JUMP_NOT" # JUMP_NOT <offset>— jump if top is falsy

    # SAGCO primitives
    EMIT     = "EMIT"     # EMIT <signal>    — broadcast signal on bus
    SPAWN    = "SPAWN"    # SPAWN <agent>    — create child process
    HALT     = "HALT"     # HALT             — stop execution
    MEASURE  = "MEASURE"  # MEASURE <wafer>  — run truth test
    DETECT   = "DETECT"   # DETECT <query>   — probe environment
    MATCH    = "MATCH"    # MATCH            — compare top two stack values

    # World
    WORLD    = "WORLD"    # WORLD            — push detected world name

    # I/O
    READ     = "READ"     # READ <path>      — read file to stack
    WRITE    = "WRITE"    # WRITE <path>     — write top of stack to file

    # Comparisons (leave bool on stack)
    EQ       = "EQ"
    NEQ      = "NEQ"
    LT       = "LT"
    GT       = "GT"

    # No-op / debug
    NOP      = "NOP"
    DEBUG    = "DEBUG"    # DEBUG <msg>      — log message without side effects
    LABEL    = "LABEL"    # LABEL <name>     — jump target (not executed)


@dataclass
class Instruction:
    op: Op
    operand: Any = None
    line: int = 0          # source line for error reporting

    def __str__(self) -> str:
        if self.operand is None:
            return self.op.value
        return f"{self.op.value} {self.operand!r}"

    def encode(self) -> str:
        """Text encoding — one instruction per line."""
        return str(self)

    @staticmethod
    def decode(line: str) -> "Instruction":
        parts = line.strip().split(None, 1)
        if not parts:
            return Instruction(Op.NOP)
        op_name = parts[0].upper()
        operand_raw = parts[1] if len(parts) > 1 else None
        op = Op(op_name) if op_name in Op._value2member_map_ else Op.NOP
        # parse operand
        operand: Any = None
        if operand_raw is not None:
            if operand_raw.startswith('"') and operand_raw.endswith('"'):
                operand = operand_raw[1:-1]
            elif operand_raw in ("True", "False", "yes", "no"):
                operand = operand_raw in ("True", "yes")
            else:
                try:
                    operand = int(operand_raw)
                except ValueError:
                    try:
                        operand = float(operand_raw)
                    except ValueError:
                        operand = operand_raw
        return Instruction(op, operand)


@dataclass
class Bytecode:
    instructions: list[Instruction]
    source_file: str = "<sagco>"

    def dump(self) -> str:
        lines = [f"; SAGCO Bytecode — {self.source_file}"]
        for i, instr in enumerate(self.instructions):
            lines.append(f"{i:04d}  {instr}")
        return "\n".join(lines)

    def save(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.dump())

    @staticmethod
    def load(path: str) -> "Bytecode":
        instructions: list[Instruction] = []
        with open(path) as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith(";"):
                    continue
                # strip leading index "0000  OPCODE ..."
                if line[:4].isdigit():
                    line = line[6:].strip()
                instructions.append(Instruction.decode(line))
        return Bytecode(instructions)

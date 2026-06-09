"""SAGCO FlameIR Compiler — FlameIR → Bytecode → VM"""

from .flame_compiler import compile_ir, compile_ir_file, disassemble

__all__ = ["compile_ir", "compile_ir_file", "disassemble"]

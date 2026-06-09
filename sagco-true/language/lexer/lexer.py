"""
SAGCO True Language — Lexer
Tokenizes native .sagco source files.

SAGCO is a declarative-imperative hybrid.
Everything is either a declaration, a measurement, or a signal.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Iterator
import re


class TT(Enum):
    # keywords
    IDENTITY  = auto()
    BOOT      = auto()
    STEP      = auto()
    REMEMBER  = auto()
    FORGET    = auto()
    LET       = auto()
    DO        = auto()
    EMIT      = auto()
    MEASURE   = auto()
    WAFER     = auto()
    ANTIBODY  = auto()
    WORLD     = auto()
    DRIVER    = auto()
    BOARD     = auto()
    SPAWN     = auto()
    HALT      = auto()
    DETECT    = auto()
    MATCH     = auto()
    TRIGGER   = auto()
    RESPONSE  = auto()
    HEAL      = auto()
    IMPORT    = auto()
    EXPORT    = auto()
    # missing-link keywords
    PROOF     = auto()   # continuous invariant block (sorcery = intent = will)
    BIND      = auto()   # dependency bond (electronegativity)
    RELEASE   = auto()   # dissolve bond
    TICK      = auto()   # hash-sealed timestamp (temporal sovereignty)
    CAST      = auto()   # alchemical transmutation (type coercion)
    UNIT      = auto()   # measurement unit annotation
    ASSERT    = auto()   # hard invariant assertion
    PIPE      = auto()   # explicit transform pipeline
    PERIOD    = auto()   # oscillatory interval declaration
    FREQUENCY = auto()   # 1/period
    PHASE     = auto()   # position in oscillation cycle
    QED       = auto()   # close proof scope
    # values
    YES       = auto()
    NO        = auto()
    REQUIRED  = auto()
    OPTIONAL  = auto()
    # structure
    LBRACE    = auto()
    RBRACE    = auto()
    LPAREN    = auto()
    RPAREN    = auto()
    LBRACKET  = auto()
    RBRACKET  = auto()
    COLON     = auto()
    DOT       = auto()
    COMMA     = auto()
    EQ        = auto()
    ARROW     = auto()
    PIPE      = auto()
    BANG      = auto()
    AT        = auto()
    # primitives
    STRING    = auto()
    NUMBER    = auto()
    IDENT     = auto()
    DOTPATH   = auto()   # kernel.name, world.os, etc.
    COMMENT   = auto()
    NEWLINE   = auto()
    EOF       = auto()


KEYWORDS: dict[str, TT] = {
    "identity": TT.IDENTITY, "boot": TT.BOOT,     "step": TT.STEP,
    "remember": TT.REMEMBER, "forget": TT.FORGET,  "let": TT.LET,
    "do": TT.DO,             "emit": TT.EMIT,      "measure": TT.MEASURE,
    "wafer": TT.WAFER,       "antibody": TT.ANTIBODY, "world": TT.WORLD,
    "driver": TT.DRIVER,     "board": TT.BOARD,    "spawn": TT.SPAWN,
    "halt": TT.HALT,         "detect": TT.DETECT,  "match": TT.MATCH,
    "trigger": TT.TRIGGER,   "response": TT.RESPONSE, "heal": TT.HEAL,
    "import": TT.IMPORT,     "export": TT.EXPORT,
    "proof": TT.PROOF,       "bind": TT.BIND,
    "release": TT.RELEASE,   "tick": TT.TICK,
    "cast": TT.CAST,         "unit": TT.UNIT,
    "assert": TT.ASSERT,     "pipe": TT.PIPE,
    "period": TT.PERIOD,     "frequency": TT.FREQUENCY,
    "phase": TT.PHASE,       "qed": TT.QED,
    "yes": TT.YES,           "no": TT.NO,
    "required": TT.REQUIRED, "optional": TT.OPTIONAL,
}


@dataclass
class Token:
    type: TT
    value: str
    line: int
    col: int
    meta: dict = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"Token({self.type.name:<12} {self.value!r:<24} L{self.line}:C{self.col})"

    @property
    def is_value(self) -> bool:
        return self.type in (TT.STRING, TT.NUMBER, TT.YES, TT.NO, TT.IDENT, TT.DOTPATH)


def lex(source: str, filename: str = "<sagco>") -> list[Token]:
    tokens: list[Token] = []
    pos = 0
    line = 1
    col = 1
    n = len(source)

    def _tok(tt: TT, val: str, extra: dict | None = None) -> Token:
        return Token(tt, val, line, col, extra or {})

    while pos < n:
        ch = source[pos]

        # newline
        if ch == "\n":
            tokens.append(_tok(TT.NEWLINE, "\n"))
            line += 1
            col = 1
            pos += 1
            continue

        # whitespace
        if ch in " \t\r":
            col += 1
            pos += 1
            continue

        # comment
        if ch == "#":
            end = source.find("\n", pos)
            end = end if end != -1 else n
            tokens.append(_tok(TT.COMMENT, source[pos:end]))
            col += end - pos
            pos = end
            continue

        # string
        if ch == '"' or ch == "'":
            q = ch
            pos += 1; col += 1
            start = pos
            while pos < n and source[pos] != q:
                if source[pos] == "\n":
                    break
                pos += 1
            val = source[start:pos]
            tokens.append(_tok(TT.STRING, val))
            if pos < n and source[pos] == q:
                pos += 1; col += 1
            continue

        # numbers
        if ch.isdigit() or (ch == "-" and pos + 1 < n and source[pos + 1].isdigit()):
            start = pos
            if ch == "-":
                pos += 1
            while pos < n and (source[pos].isdigit() or source[pos] == "."):
                pos += 1
            val = source[start:pos]
            tokens.append(_tok(TT.NUMBER, val, {"num": float(val) if "." in val else int(val)}))
            col += len(val)
            continue

        # identifiers, dotpaths, keywords
        if ch.isalpha() or ch == "_":
            start = pos
            while pos < n and (source[pos].isalnum() or source[pos] in "_-"):
                pos += 1
            # check for dotpath: word.word.word
            if pos < n and source[pos] == "." and (pos + 1 < n and (source[pos + 1].isalpha() or source[pos + 1] == "_")):
                while pos < n and (source[pos].isalnum() or source[pos] in "_-."):
                    pos += 1
                val = source[start:pos]
                tokens.append(_tok(TT.DOTPATH, val))
            else:
                val = source[start:pos]
                tt = KEYWORDS.get(val.lower(), TT.IDENT)
                tokens.append(_tok(tt, val))
            col += pos - start
            continue

        # single-char tokens
        single: dict[str, TT] = {
            "{": TT.LBRACE, "}": TT.RBRACE,
            "(": TT.LPAREN, ")": TT.RPAREN,
            "[": TT.LBRACKET, "]": TT.RBRACKET,
            ":": TT.COLON,  ".": TT.DOT,
            ",": TT.COMMA,  "=": TT.EQ,
            "|": TT.PIPE,   "!": TT.BANG,
            "@": TT.AT,
        }
        if source[pos:pos+2] == "->":
            tokens.append(_tok(TT.ARROW, "->"))
            pos += 2; col += 2
            continue
        if ch in single:
            tokens.append(_tok(single[ch], ch))
            pos += 1; col += 1
            continue

        # unknown — skip
        pos += 1; col += 1

    tokens.append(Token(TT.EOF, "", line, col))
    return [t for t in tokens if t.type not in (TT.COMMENT, TT.NEWLINE)]


def token_stream(source: str) -> Iterator[Token]:
    yield from lex(source)


if __name__ == "__main__":
    import sys
    src = open(sys.argv[1]).read() if len(sys.argv) > 1 else """
identity sagco-kernel {
  name: "SAGCO Kernel"
  version: "0.1.0"
}
boot {
  step detect_world
  step load_identity
  step emit_ready
}
wafer can_boot {
  expected: yes
  actual: yes
  match: required
}
"""
    for tok in lex(src):
        print(tok)

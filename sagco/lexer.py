"""
SAGCO Headless Lexer
Tokenizes SAGCO command strings without requiring a TTY.
Token stream feeds directly into the parser.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Iterator
import re


class TT(Enum):
    CMD       = auto()   # sagco
    VERB      = auto()   # crawl | ingest | vm | deploy | pipeline | link | emit | spawn | halt
    PATH      = auto()   # ./foo | /absolute/path
    FLAG      = auto()   # --name=value
    FLAG_BOOL = auto()   # --name  (bare flag, no value)
    IDENT     = auto()   # bare identifier
    STRING    = auto()   # "quoted string"
    NUMBER    = auto()   # integer or float
    PIPE      = auto()   # |
    ARROW     = auto()   # ->
    COMMA     = auto()   # ,
    COLON     = auto()   # :
    AT        = auto()   # @  (agent address)
    HASH      = auto()   # #  (cell ref / comment stripped already)
    EOF       = auto()


VERBS = frozenset({
    "crawl", "ingest", "vm", "deploy", "pipeline",
    "link", "emit", "spawn", "halt", "run", "status",
    "convert", "audit", "sync", "boot", "dna",
})

# ordered: longest match first
_PATTERNS: list[tuple[TT, re.Pattern[str]]] = [
    (TT.CMD,       re.compile(r'\bsagco\b')),
    (TT.ARROW,     re.compile(r'->')),
    (TT.FLAG,      re.compile(r'--([A-Za-z][A-Za-z0-9_-]*)=([^\s]+)')),
    (TT.FLAG_BOOL, re.compile(r'--([A-Za-z][A-Za-z0-9_-]*)')),
    (TT.PIPE,      re.compile(r'\|')),
    (TT.AT,        re.compile(r'@')),
    (TT.HASH,      re.compile(r'#[^\n]*')),       # strip comments
    (TT.PATH,      re.compile(r'\.{0,2}/[^\s]*')),
    (TT.STRING,    re.compile(r'"([^"\\]|\\.)*"')),
    (TT.NUMBER,    re.compile(r'\b\d+(\.\d+)?\b')),
    (TT.COMMA,     re.compile(r',')),
    (TT.COLON,     re.compile(r':')),
    (TT.IDENT,     re.compile(r'[A-Za-z_][A-Za-z0-9_\-\.]*')),
]


@dataclass
class Token:
    type: TT
    value: str
    pos: int
    meta: dict = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, @{self.pos})"


def lex(source: str) -> list[Token]:
    tokens: list[Token] = []
    pos = 0
    length = len(source)

    while pos < length:
        # skip whitespace
        if source[pos] in (' ', '\t', '\n', '\r'):
            pos += 1
            continue

        matched = False
        for tt, pattern in _PATTERNS:
            m = pattern.match(source, pos)
            if m is None:
                continue

            raw = m.group(0)

            if tt == TT.HASH:
                # discard comment, advance past it
                pos = m.end()
                matched = True
                break

            if tt == TT.CMD:
                tok = Token(TT.CMD, raw, pos)

            elif tt == TT.FLAG:
                tok = Token(TT.FLAG, raw, pos,
                            meta={"key": m.group(1), "val": m.group(2)})

            elif tt == TT.FLAG_BOOL:
                tok = Token(TT.FLAG_BOOL, raw, pos,
                            meta={"key": m.group(1)})

            elif tt == TT.IDENT:
                # promote to VERB if known
                word = raw.lower()
                tok = Token(TT.VERB if word in VERBS else TT.IDENT, raw, pos)

            elif tt == TT.NUMBER:
                tok = Token(TT.NUMBER, raw, pos,
                            meta={"num": float(raw) if '.' in raw else int(raw)})

            elif tt == TT.STRING:
                tok = Token(TT.STRING, raw[1:-1], pos)   # strip quotes

            else:
                tok = Token(tt, raw, pos)

            tokens.append(tok)
            pos = m.end()
            matched = True
            break

        if not matched:
            # skip unknown char (lenient mode — headless never crashes)
            pos += 1

    tokens.append(Token(TT.EOF, "", pos))
    return tokens


def token_stream(source: str) -> Iterator[Token]:
    yield from lex(source)


if __name__ == "__main__":
    import sys
    src = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else \
          'sagco crawl ./src --depth=3 --emit=tokens | sagco ingest README.md --convert=dna'
    for tok in lex(src):
        print(tok)

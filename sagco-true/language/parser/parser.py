"""
SAGCO True Language — Parser
Converts token stream into a typed Module AST.
"""

from __future__ import annotations
from typing import Any
from ..lexer.lexer import Token, TT, lex
from ..ast.nodes import *


class ParseError(Exception):
    def __init__(self, msg: str, tok: Token):
        super().__init__(f"{msg} at L{tok.line}:C{tok.col} ({tok.value!r})")
        self.tok = tok


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self._t = [t for t in tokens if t.type != TT.EOF]
        self._t.append(Token(TT.EOF, "", 0, 0))
        self._pos = 0

    def _peek(self, offset: int = 0) -> Token:
        idx = self._pos + offset
        return self._t[idx] if idx < len(self._t) else self._t[-1]

    def _consume(self) -> Token:
        tok = self._t[self._pos]
        self._pos += 1
        return tok

    def _expect(self, *types: TT) -> Token:
        tok = self._peek()
        if tok.type not in types:
            raise ParseError(f"Expected {[t.name for t in types]}, got {tok.type.name}", tok)
        return self._consume()

    def _at(self, *types: TT) -> bool:
        return self._peek().type in types

    def _at_end(self) -> bool:
        return self._peek().type == TT.EOF

    # ── value parsing ─────────────────────────────────────────────────────

    def _parse_value(self) -> Any:
        tok = self._peek()

        if tok.type == TT.STRING:
            self._consume()
            return StringVal(tok.value)

        if tok.type == TT.NUMBER:
            self._consume()
            return NumberVal(tok.meta["num"])

        if tok.type in (TT.YES,):
            self._consume()
            return BoolVal(True)

        if tok.type in (TT.NO,):
            self._consume()
            return BoolVal(False)

        if tok.type in (TT.REQUIRED, TT.OPTIONAL):
            self._consume()
            return IdentVal(tok.value)

        if tok.type == TT.LBRACKET:
            self._consume()
            items: list[Any] = []
            while not self._at(TT.RBRACKET) and not self._at_end():
                items.append(self._parse_value())
                if self._at(TT.COMMA):
                    self._consume()
            self._expect(TT.RBRACKET)
            return ListVal(items)

        if tok.type in (TT.IDENT, TT.DOTPATH):
            self._consume()
            # function call: ident(args)
            if self._at(TT.LPAREN):
                self._consume()
                args: list[Any] = []
                while not self._at(TT.RPAREN) and not self._at_end():
                    args.append(self._parse_value())
                    if self._at(TT.COMMA):
                        self._consume()
                self._expect(TT.RPAREN)
                return CallVal(tok.value, args)
            return IdentVal(tok.value)

        if tok.type == TT.DETECT:
            self._consume()
            if self._at(TT.LPAREN):
                self._consume()
                args = []
                while not self._at(TT.RPAREN) and not self._at_end():
                    args.append(self._parse_value())
                    if self._at(TT.COMMA):
                        self._consume()
                self._expect(TT.RPAREN)
                return CallVal("detect", args)
            return IdentVal("detect")

        # fallback: return raw ident token value
        self._consume()
        return IdentVal(tok.value)

    def _parse_fields(self) -> list[Field]:
        fields: list[Field] = []
        while not self._at(TT.RBRACE) and not self._at_end():
            key_tok = self._peek()
            if key_tok.type in (TT.IDENT, TT.DOTPATH) or key_tok.type in KEYWORDS_SET:
                key = self._consume().value
            else:
                break
            self._expect(TT.COLON)
            val = self._parse_value()
            fields.append(Field(key, val))
        return fields

    # ── statement parsers ─────────────────────────────────────────────────

    def _parse_identity(self) -> IdentityDecl:
        self._consume()  # identity
        name = self._expect(TT.IDENT, TT.DOTPATH).value
        self._expect(TT.LBRACE)
        fields = self._parse_fields()
        self._expect(TT.RBRACE)
        return IdentityDecl(name, fields)

    def _parse_boot(self) -> BootDecl:
        self._consume()  # boot
        self._expect(TT.LBRACE)
        steps: list[str] = []
        while not self._at(TT.RBRACE) and not self._at_end():
            self._expect(TT.STEP)
            steps.append(self._expect(TT.IDENT, TT.DOTPATH).value)
        self._expect(TT.RBRACE)
        return BootDecl(steps)

    def _parse_remember(self) -> RememberStmt:
        self._consume()  # remember
        key = self._expect(TT.IDENT, TT.DOTPATH, TT.STRING).value
        val = self._parse_value()
        return RememberStmt(key, val)

    def _parse_forget(self) -> ForgetStmt:
        self._consume()
        key = self._expect(TT.IDENT, TT.DOTPATH).value
        return ForgetStmt(key)

    def _parse_let(self) -> LetStmt:
        self._consume()  # let
        # allow keywords as variable names (world, boot, etc.)
        name = self._consume().value
        self._expect(TT.EQ)
        val = self._parse_value()
        return LetStmt(name, val)

    def _parse_do(self) -> DoBlock:
        self._consume()  # do
        name = self._expect(TT.IDENT, TT.DOTPATH).value
        self._expect(TT.LBRACE)
        body: list[Any] = []
        while not self._at(TT.RBRACE) and not self._at_end():
            stmt = self._parse_statement()
            if stmt is not None:
                body.append(stmt)
        self._expect(TT.RBRACE)
        return DoBlock(name, body)

    def _parse_emit(self) -> EmitStmt:
        self._consume()  # emit
        signal = self._expect(TT.IDENT, TT.DOTPATH).value
        payload: dict = {}
        if self._at(TT.LBRACE):
            self._consume()
            for f in self._parse_fields():
                payload[f.key] = f.value
            self._expect(TT.RBRACE)
        return EmitStmt(signal, payload)

    def _parse_measure(self) -> MeasureStmt:
        self._consume()  # measure
        target = self._expect(TT.IDENT, TT.DOTPATH).value
        return MeasureStmt(target)

    def _parse_wafer(self) -> WaferDecl:
        self._consume()  # wafer
        name = self._expect(TT.IDENT, TT.DOTPATH).value
        self._expect(TT.LBRACE)
        w = WaferDecl(name=name)
        for f in self._parse_fields():
            if f.key == "expected":
                w.expected = f.value
            elif f.key == "actual":
                w.actual = f.value
            elif f.key == "match":
                w.match_mode = f.value.name if isinstance(f.value, IdentVal) else str(f.value)
        self._expect(TT.RBRACE)
        return w

    def _parse_antibody(self) -> AntibodyDecl:
        self._consume()  # antibody
        name = self._expect(TT.IDENT, TT.DOTPATH).value
        self._expect(TT.LBRACE)
        ab = AntibodyDecl(name=name)
        for f in self._parse_fields():
            setattr(ab, f.key if hasattr(ab, f.key) else f.key, f.value)
        self._expect(TT.RBRACE)
        return ab

    def _parse_world(self) -> WorldBlock:
        self._consume()  # world
        name = self._expect(TT.IDENT).value
        self._expect(TT.LBRACE)
        body: list[Any] = []
        while not self._at(TT.RBRACE) and not self._at_end():
            stmt = self._parse_statement()
            if stmt is not None:
                body.append(stmt)
        self._expect(TT.RBRACE)
        return WorldBlock(name, body)

    def _parse_import(self) -> ImportStmt:
        self._consume()  # import
        path = self._expect(TT.STRING, TT.IDENT, TT.DOTPATH).value
        alias = None
        if self._at(TT.IDENT) and self._peek().value == "as":
            self._consume()
            alias = self._expect(TT.IDENT).value
        return ImportStmt(path, alias)

    def _parse_spawn(self) -> SpawnStmt:
        self._consume()
        agent = self._expect(TT.IDENT, TT.STRING).value
        config: dict = {}
        if self._at(TT.LBRACE):
            self._consume()
            for f in self._parse_fields():
                config[f.key] = f.value
            self._expect(TT.RBRACE)
        return SpawnStmt(agent, config)

    def _parse_halt(self) -> HaltStmt:
        self._consume()
        target = None
        if self._at(TT.IDENT, TT.DOTPATH):
            target = self._consume().value
        return HaltStmt(target)

    def _parse_statement(self) -> Any:
        tok = self._peek()
        dispatch = {
            TT.IDENTITY:  self._parse_identity,
            TT.BOOT:      self._parse_boot,
            TT.REMEMBER:  self._parse_remember,
            TT.FORGET:    self._parse_forget,
            TT.LET:       self._parse_let,
            TT.DO:        self._parse_do,
            TT.EMIT:      self._parse_emit,
            TT.MEASURE:   self._parse_measure,
            TT.WAFER:     self._parse_wafer,
            TT.ANTIBODY:  self._parse_antibody,
            TT.WORLD:     self._parse_world,
            TT.IMPORT:    self._parse_import,
            TT.SPAWN:     self._parse_spawn,
            TT.HALT:      self._parse_halt,
        }
        fn = dispatch.get(tok.type)
        if fn:
            return fn()
        self._consume()   # skip unknown tokens in lenient mode
        return None

    def parse(self, filename: str = "<sagco>") -> Module:
        mod = Module(filename=filename)
        while not self._at_end():
            stmt = self._parse_statement()
            if stmt is not None:
                mod.body.append(stmt)
        return mod


# keyword token types (for field key parsing)
KEYWORDS_SET = {
    TT.IDENTITY, TT.BOOT, TT.STEP, TT.REMEMBER, TT.FORGET, TT.LET,
    TT.DO, TT.EMIT, TT.MEASURE, TT.WAFER, TT.ANTIBODY, TT.WORLD,
    TT.DRIVER, TT.BOARD, TT.SPAWN, TT.HALT, TT.DETECT, TT.MATCH,
    TT.TRIGGER, TT.RESPONSE, TT.HEAL, TT.IMPORT, TT.EXPORT,
    TT.YES, TT.NO, TT.REQUIRED, TT.OPTIONAL,
}


def parse(source: str, filename: str = "<sagco>") -> Module:
    tokens = lex(source, filename)
    return Parser(tokens).parse(filename)


if __name__ == "__main__":
    import sys, json
    src = open(sys.argv[1]).read() if len(sys.argv) > 1 else ""
    mod = parse(src)
    for stmt in mod.body:
        print(type(stmt).__name__, ":", stmt)

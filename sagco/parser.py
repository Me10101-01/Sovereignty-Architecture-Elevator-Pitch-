"""
SAGCO AST Parser
Converts token stream from lexer into a typed AST of pipeline stages.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from .lexer import Token, TT, lex


# ── AST nodes ────────────────────────────────────────────────────────────────

@dataclass
class FlagNode:
    key: str
    value: Any            # str | bool | int | float


@dataclass
class CommandNode:
    verb: str
    target: str | None
    flags: list[FlagNode] = field(default_factory=list)

    def flag(self, key: str, default: Any = None) -> Any:
        for f in self.flags:
            if f.key == key:
                return f.value
        return default


@dataclass
class PipelineNode:
    """Ordered sequence of commands joined by | or ->"""
    stages: list[CommandNode] = field(default_factory=list)

    def append(self, cmd: CommandNode) -> None:
        self.stages.append(cmd)

    def __len__(self) -> int:
        return len(self.stages)


@dataclass
class ScriptNode:
    """Top-level: one or more pipelines separated by newlines/semicolons"""
    pipelines: list[PipelineNode] = field(default_factory=list)


# ── Parser ────────────────────────────────────────────────────────────────────

class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._pos = 0

    def _peek(self) -> Token:
        return self._tokens[self._pos]

    def _consume(self) -> Token:
        tok = self._tokens[self._pos]
        self._pos += 1
        return tok

    def _expect(self, *types: TT) -> Token:
        tok = self._peek()
        if tok.type not in types:
            raise ParseError(
                f"Expected {[t.name for t in types]} but got {tok.type.name!r} "
                f"({tok.value!r}) at pos {tok.pos}"
            )
        return self._consume()

    def _at_end(self) -> bool:
        return self._peek().type == TT.EOF

    # ── grammar ──

    def parse(self) -> ScriptNode:
        script = ScriptNode()
        while not self._at_end():
            pipeline = self._parse_pipeline()
            if pipeline.stages:
                script.pipelines.append(pipeline)
        return script

    def _parse_pipeline(self) -> PipelineNode:
        pipeline = PipelineNode()
        cmd = self._parse_command()
        if cmd:
            pipeline.append(cmd)
        while self._peek().type in (TT.PIPE, TT.ARROW) and not self._at_end():
            self._consume()          # eat | or ->
            cmd = self._parse_command()
            if cmd:
                pipeline.append(cmd)
        return pipeline

    def _parse_command(self) -> CommandNode | None:
        # optional leading 'sagco'
        if self._peek().type == TT.CMD:
            self._consume()

        if self._peek().type not in (TT.VERB, TT.IDENT):
            return None

        verb_tok = self._consume()
        verb = verb_tok.value.lower()

        target: str | None = None
        if self._peek().type in (TT.PATH, TT.IDENT, TT.STRING):
            target = self._consume().value

        flags: list[FlagNode] = []
        while self._peek().type in (TT.FLAG, TT.FLAG_BOOL):
            tok = self._consume()
            if tok.type == TT.FLAG:
                raw_val = tok.meta["val"]
                # coerce numerics
                try:
                    val: Any = int(raw_val)
                except ValueError:
                    try:
                        val = float(raw_val)
                    except ValueError:
                        val = raw_val
                flags.append(FlagNode(tok.meta["key"], val))
            else:  # FLAG_BOOL
                flags.append(FlagNode(tok.meta["key"], True))

        return CommandNode(verb=verb, target=target, flags=flags)


def parse(source: str) -> ScriptNode:
    tokens = lex(source)
    return Parser(tokens).parse()


def parse_command(source: str) -> CommandNode | None:
    script = parse(source)
    if script.pipelines and script.pipelines[0].stages:
        return script.pipelines[0].stages[0]
    return None


if __name__ == "__main__":
    import sys, json

    src = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else \
          "sagco crawl ./sagco --depth=2 --emit=tokens | sagco ingest README.md --convert=dna"

    script = parse(src)
    for i, pipeline in enumerate(script.pipelines):
        print(f"Pipeline {i}:")
        for j, cmd in enumerate(pipeline.stages):
            flags = {f.key: f.value for f in cmd.flags}
            print(f"  Stage {j}: {cmd.verb} {cmd.target} flags={flags}")

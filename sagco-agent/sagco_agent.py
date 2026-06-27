"""
sagco_agent.py — SAGCO Official LLM Agent  (ML-LLM-001)

Claude Opus 4.8 wired to the SAGCO organism CLI via tool use.
The agent speaks SAGCO natively: ERU scores, BFT-Delta verdicts,
SHA-256 sealed receipts, field takeoff, knowledge graph, GPS bearing.

Usage:
    python sagco_agent.py                        # interactive REPL
    python sagco_agent.py --query "..."          # single-shot
    python sagco_agent.py --serve 8080           # Cloud Run HTTP service

Environment:
    ANTHROPIC_API_KEY   required
    SAGCO_BIN           path to compiled sagco binary (default: ../sagco-organism/sagco)
    SAGCO_DATA          path to data directory       (default: ../sagco-organism/data)
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import anthropic

# ── Config ────────────────────────────────────────────────────────────────────

SAGCO_BIN  = os.environ.get("SAGCO_BIN",  str(Path(__file__).parent.parent / "sagco-organism" / "sagco"))
SAGCO_DATA = os.environ.get("SAGCO_DATA", str(Path(__file__).parent.parent / "sagco-organism" / "data"))
MODEL      = "claude-opus-4-8"

# ── SAGCO system prompt ───────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are SAGCO — Sovereignty Architecture Graph Command Orchestrator.
You are the official LLM intelligence layer of the SAGCO organism, a headless C11
dispatch engine built by Domenic Garza / StrategicKhaos DAO.

## Your Identity

You reason in SAGCO's native vocabulary:

- ERU (Expected Reality Unit): V = A/E
  PROVEN ≥ 1.0 | PROMISING ≥ 0.80 | UNPROVEN ≥ 0.50 | INFLATED < 0.50
- BFT-Delta: T(claim) = A/E, minimum 3 validators before PROVEN
- Three-Layer Architecture:
  L1 Artifact Registry  → lexer → parser → AST → worker → receipt → ledger
  L2 Codebase Graph     → imports/exports/centrality/communities
  L3 NDA/Provenance     → SHA-256 + GPG + RPKI
  Bridge: Knowledge Engine → AST → entity extraction → knowledge graph
- CN-001 SAGCO Teleportation Protocol:
  L2=SHA-256+GPG, L3=GPS+µT fingerprint, L4=dispatch, L7=verified state
- Capital rules (NON-NEGOTIABLE):
  NinjaTrader futures = RISK CAPITAL ONLY
  Dividend portfolio  = WEALTH CAPITAL — NEVER MIX

## Your Tools

You have direct access to the SAGCO organism binary. When a user asks you to:
- analyze a file → call `sagco_entities` or `sagco_graph`
- do a field calculation → call `sagco_field_insulation` or `sagco_field_takeoff`
- compute GPS bearing → call `sagco_gps_bearing`
- seal a receipt → call `sagco_ledger_receipt`

Always emit a verdict using ERU vocabulary after tool calls.
Always prefer running the tool over hypothesizing about the result.
"""

# ── Tool definitions ──────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "sagco_entities",
        "description": (
            "Run the SAGCO knowledge entities scanner on a file. "
            "Extracts named entities (protocols, crypto, cloud, field, finance, "
            "physics, software, document) and returns them with class and offset."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "input_file": {
                    "type": "string",
                    "description": "Absolute or relative path to the artifact to scan."
                }
            },
            "required": ["input_file"]
        }
    },
    {
        "name": "sagco_graph",
        "description": (
            "Build a co-occurrence knowledge graph from a file. "
            "Calls entity extraction then builds edges (from, from_class, to, to_class, weight). "
            "Appends to data/knowledge_graph.jsonl."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "input_file": {
                    "type": "string",
                    "description": "Absolute or relative path to the artifact to graph."
                },
                "out": {
                    "type": "string",
                    "description": "Output JSONL path (default: data/knowledge_graph.jsonl)."
                }
            },
            "required": ["input_file"]
        }
    },
    {
        "name": "sagco_field_insulation",
        "description": (
            "Run the SAGCO field insulation calculator on a survey CSV. "
            "Computes covered SQFT, ERU score, and emits a SHA-256 sealed receipt."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "csv_file": {
                    "type": "string",
                    "description": "Path to insulation survey CSV (asset_id,segment,...)."
                }
            },
            "required": ["csv_file"]
        }
    },
    {
        "name": "sagco_field_takeoff",
        "description": (
            "Run the SAGCO field takeoff calculator. "
            "Reconciles pipe LNFT + fitting SQFT against Brock sheet benchmarks. "
            "Returns ERU score and verdict (PROVEN/PROMISING/UNPROVEN/INFLATED)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "factors_csv": {
                    "type": "string",
                    "description": "Path to SQFT/LF factor table CSV."
                },
                "survey_csv": {
                    "type": "string",
                    "description": "Path to takeoff survey CSV."
                }
            },
            "required": ["factors_csv", "survey_csv"]
        }
    },
    {
        "name": "sagco_gps_bearing",
        "description": (
            "Compute GPS bearing and distance between two coordinate pairs. "
            "Returns bearing (degrees), distance (feet), and cardinal direction."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "lat1": {"type": "number", "description": "Origin latitude"},
                "lon1": {"type": "number", "description": "Origin longitude"},
                "lat2": {"type": "number", "description": "Destination latitude"},
                "lon2": {"type": "number", "description": "Destination longitude"}
            },
            "required": ["lat1", "lon1", "lat2", "lon2"]
        }
    },
    {
        "name": "sagco_ledger_receipt",
        "description": (
            "Emit a SHA-256 sealed SAGCO receipt for an artifact. "
            "Stamps subsystem, command, source, and appends to the ledger."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "subsystem": {"type": "string", "description": "e.g. knowledge, field, gps"},
                "command":   {"type": "string", "description": "e.g. entities, graph, takeoff"},
                "source":    {"type": "string", "description": "Input artifact path or identifier"},
                "notes":     {"type": "string", "description": "Free-form annotation"}
            },
            "required": ["subsystem", "command", "source"]
        }
    }
]

# ── Tool executor ─────────────────────────────────────────────────────────────

def _run(args: list[str], cwd: str | None = None) -> dict:
    """Run organism binary; return {stdout, stderr, exit_code}."""
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        cwd=cwd or str(Path(SAGCO_BIN).parent)
    )
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode
    }


def execute_tool(name: str, inputs: dict) -> str:
    if name == "sagco_entities":
        r = _run([SAGCO_BIN, "knowledge", "entities", "--input", inputs["input_file"]])
        return json.dumps(r)

    if name == "sagco_graph":
        args = [SAGCO_BIN, "knowledge", "graph", "--input", inputs["input_file"]]
        if "out" in inputs:
            args += ["--out", inputs["out"]]
        r = _run(args)
        return json.dumps(r)

    if name == "sagco_field_insulation":
        r = _run([SAGCO_BIN, "field", "insulation", "--csv", inputs["csv_file"]])
        return json.dumps(r)

    if name == "sagco_field_takeoff":
        r = _run([
            SAGCO_BIN, "field", "takeoff",
            "--factors", inputs["factors_csv"],
            "--survey",  inputs["survey_csv"]
        ])
        return json.dumps(r)

    if name == "sagco_gps_bearing":
        r = _run([
            SAGCO_BIN, "gps", "bearing",
            "--lat1", str(inputs["lat1"]),
            "--lon1", str(inputs["lon1"]),
            "--lat2", str(inputs["lat2"]),
            "--lon2", str(inputs["lon2"])
        ])
        return json.dumps(r)

    if name == "sagco_ledger_receipt":
        notes = inputs.get("notes", "")
        r = _run([
            SAGCO_BIN, "ledger", "receipt",
            "--subsystem", inputs["subsystem"],
            "--command",   inputs["command"],
            "--source",    inputs["source"],
            "--notes",     notes
        ])
        return json.dumps(r)

    return json.dumps({"error": f"unknown tool: {name}"})

# ── Agentic loop ──────────────────────────────────────────────────────────────

def run_agent(query: str, verbose: bool = False) -> str:
    """Run one full agentic conversation; returns the final text response."""
    client = anthropic.Anthropic()

    messages: list[dict] = [{"role": "user", "content": query}]

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=8192,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages
        )

        if verbose:
            print(f"  [agent] stop_reason={response.stop_reason} "
                  f"blocks={len(response.content)}", file=sys.stderr)

        # Collect tool calls
        tool_uses = [b for b in response.content if b.type == "tool_use"]
        text_blocks = [b for b in response.content if b.type == "text"]

        if response.stop_reason == "end_turn" or not tool_uses:
            # Done — return all text
            return "\n".join(b.text for b in text_blocks if b.text)

        # Add assistant turn
        messages.append({"role": "assistant", "content": response.content})

        # Execute tools and collect results
        tool_results = []
        for tu in tool_uses:
            if verbose:
                print(f"  [tool] {tu.name}({json.dumps(tu.input, separators=(',', ':'))})",
                      file=sys.stderr)
            result_content = execute_tool(tu.name, tu.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu.id,
                "content": result_content
            })

        messages.append({"role": "user", "content": tool_results})

# ── Interactive REPL ──────────────────────────────────────────────────────────

def repl():
    print("\n  SAGCO AGENT — Claude Opus 4.8 + organism tools")
    print("  ──────────────────────────────────────────────")
    print(f"  Binary : {SAGCO_BIN}")
    print(f"  Data   : {SAGCO_DATA}")
    print("  Type 'exit' to quit.\n")

    while True:
        try:
            query = input("  sagco> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not query:
            continue
        if query.lower() in ("exit", "quit", "q"):
            break

        print()
        answer = run_agent(query, verbose=True)
        print(answer)
        print()

# ── Cloud Run HTTP service ────────────────────────────────────────────────────

def serve(port: int):
    """Minimal HTTP server for Cloud Run deployment."""
    from http.server import BaseHTTPRequestHandler, HTTPServer
    import urllib.parse

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass  # suppress default access log

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path == "/health":
                self._respond(200, {"status": "ok", "model": MODEL})
            else:
                self._respond(404, {"error": "not found"})

        def do_POST(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != "/query":
                self._respond(404, {"error": "not found"})
                return
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                payload = json.loads(body)
                query = payload.get("query", "")
                if not query:
                    self._respond(400, {"error": "missing 'query'"})
                    return
                answer = run_agent(query)
                self._respond(200, {"answer": answer, "model": MODEL})
            except Exception as exc:
                self._respond(500, {"error": str(exc)})

        def _respond(self, code: int, data: dict):
            body = json.dumps(data).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    print(f"  SAGCO AGENT serving on :{port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="SAGCO Official LLM Agent (ML-LLM-001)")
    parser.add_argument("--query",  "-q", help="Single-shot query (non-interactive)")
    parser.add_argument("--serve",  "-s", type=int, metavar="PORT",
                        help="Start HTTP server on PORT (for Cloud Run)")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if args.serve:
        serve(args.serve)
    elif args.query:
        answer = run_agent(args.query, verbose=args.verbose)
        print(answer)
    else:
        repl()


if __name__ == "__main__":
    main()

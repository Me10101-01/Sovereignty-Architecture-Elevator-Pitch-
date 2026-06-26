#!/usr/bin/env python3
"""SAGCO LLM Brain — natural language query over the live organism tree.
Requires: pip install anthropic
Usage:
  sagco ask "which subsystem handles retrieval?"
  sagco ask "what is the highest weight organ?"
  sagco ask "find all antibody cells and explain their role"
  sagco ask "what command should I run to inspect sagco-raspberry-pi-os-lab?"
"""
import os
import sys
import json
import collections

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed.", file=sys.stderr)
    print("  pip install anthropic", file=sys.stderr)
    sys.exit(1)

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not set.", file=sys.stderr)
    sys.exit(1)

question = " ".join(sys.argv[1:]).strip()
if not question:
    print("usage: sagco ask <question>", file=sys.stderr)
    sys.exit(1)

tree_path = os.environ.get("SAGCO_TREE", "sagco_first_party_tree.json")
eru_spec  = os.environ.get("SAGCO_ERU_SPEC", "sagco_eru_spec.json")

# ── Build organism context (compact, cache-friendly) ─────────────────────────
def build_context():
    ctx = {"organs": {}, "eru": {}, "scale": {}}

    if os.path.exists(tree_path):
        data  = json.load(open(tree_path))
        cells = data["cells"]
        organs     = collections.defaultdict(lambda: collections.defaultdict(list))
        kind_count = collections.Counter()

        for c in cells:
            parts  = c["path"].split("/")
            organ  = parts[2] if len(parts) > 2 else "root"
            subsys = parts[3] if len(parts) > 3 else "_root"
            organs[organ][subsys].append({"w": c["weight"], "k": c["kind"], "p": c["path"]})
            kind_count[c["kind"]] += 1

        ctx["scale"] = {
            "total_cells": len(cells),
            "total_organs": len(organs),
            "total_weight": sum(c["weight"] for c in cells),
            "kinds": dict(kind_count.most_common()),
        }

        # Top 20 organs with subsystems (keep context compact)
        ranked = sorted(
            organs.items(),
            key=lambda x: sum(c["w"] for cs in x[1].values() for c in cs),
            reverse=True
        )
        for organ, subsystems in ranked[:20]:
            w = sum(c["w"] for cs in subsystems.values() for c in cs)
            n = sum(len(cs) for cs in subsystems.values())
            ctx["organs"][organ] = {
                "weight": w,
                "cells": n,
                "subsystems": {
                    sub: {
                        "cells": len(cs),
                        "weight": sum(c["w"] for c in cs),
                        "kinds": list(set(c["k"] for c in cs)),
                    }
                    for sub, cs in subsystems.items()
                },
            }

    if os.path.exists(eru_spec):
        ctx["eru"] = json.load(open(eru_spec))

    return ctx

ctx = build_context()

SYSTEM = """You are the SAGCO Organism Intelligence — the LLM brain wired directly
into a live personal cognition architecture. The user asks questions about their
organism and you answer from the real data in the context.

The SAGCO organism is:
- An externalized working memory system (personal cognition stack)
- Built from first-party cells, organized into organs and subsystems
- Isomorphic to git: thought→blob, relationship→tree, provenance→commit, seal→SHA256
- Running on a live workspace with compiled Rust ERU engine

Answer with precision. Reference actual organ names, subsystem names, weights,
and cell counts from the context. When asked "what command should I run", give
the exact sagco CLI command. When asked about architecture, reason from the
real subsystem graph. Keep answers tight — this is a CLI, not a chat UI."""

user_message = f"""ORGANISM CONTEXT:
{json.dumps(ctx, indent=2)[:8000]}

QUESTION: {question}"""

client = anthropic.Anthropic(api_key=api_key)

print(f"SAGCO ASK: {question}", flush=True)
print("-" * 60)

with client.messages.stream(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    system=SYSTEM,
    messages=[{"role": "user", "content": user_message}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

print()
print("-" * 60)

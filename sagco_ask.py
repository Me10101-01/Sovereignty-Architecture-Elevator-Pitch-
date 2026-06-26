#!/usr/bin/env python3
"""SAGCO LLM Brain — stdlib only, no pip required.
Uses urllib to call Anthropic API directly.
Usage:
  sagco ask "which subsystem handles retrieval?"
  sagco ask "what is the highest weight organ?"
  sagco ask "what command should I run to inspect sagco-raspberry-pi-os-lab?"
"""
import os
import sys
import json
import collections
import urllib.request
import urllib.error

api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
if not api_key or api_key == "your-key-here":
    print("ERROR: set your real key first:")
    print('  export ANTHROPIC_API_KEY="sk-ant-..."')
    sys.exit(1)

question = " ".join(sys.argv[1:]).strip()
if not question:
    print("usage: sagco ask <question>")
    sys.exit(1)

tree_path = os.environ.get("SAGCO_TREE",
    os.path.join(os.path.dirname(__file__), "sagco_first_party_tree.json"))
eru_spec  = os.environ.get("SAGCO_ERU_SPEC",
    os.path.join(os.path.dirname(__file__), "sagco_eru_spec.json"))

def build_context():
    ctx = {"organs": {}, "eru": {}, "scale": {}}
    if not os.path.exists(tree_path):
        return ctx

    data  = json.load(open(tree_path))
    cells = data["cells"]
    organs     = collections.defaultdict(lambda: collections.defaultdict(list))
    kind_count = collections.Counter()

    for c in cells:
        parts  = c["path"].split("/")
        organ  = parts[2] if len(parts) > 2 else "root"
        subsys = parts[3] if len(parts) > 3 else "_root"
        organs[organ][subsys].append({"w": c["weight"], "k": c["kind"]})
        kind_count[c["kind"]] += 1

    ctx["scale"] = {
        "total_cells": len(cells),
        "total_organs": len(organs),
        "total_weight": sum(c["weight"] for c in cells),
        "kinds": dict(kind_count.most_common()),
    }

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
                for sub, cs in list(subsystems.items())[:12]
            },
        }

    if os.path.exists(eru_spec):
        ctx["eru"] = json.load(open(eru_spec))

    return ctx

SYSTEM = """You are the SAGCO Organism Intelligence — the LLM brain wired into a live
personal cognition architecture. Answer questions about the organism from the real
data in the context. Reference actual organ names, subsystem names, weights, and
cell counts. When asked what command to run, give the exact sagco CLI command.
Keep answers tight — this is a CLI, not a chat UI."""

ctx = build_context()

payload = {
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 1024,
    "system": SYSTEM,
    "messages": [{
        "role": "user",
        "content": f"ORGANISM CONTEXT:\n{json.dumps(ctx, indent=2)[:6000]}\n\nQUESTION: {question}"
    }]
}

print(f"SAGCO ASK: {question}")
print("-" * 60)

try:
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    print(result["content"][0]["text"])
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"API ERROR {e.code}: {body}", file=sys.stderr)
    sys.exit(1)
except urllib.error.URLError as e:
    print(f"NETWORK ERROR: {e.reason}", file=sys.stderr)
    print("Is the device connected to the internet?", file=sys.stderr)
    sys.exit(1)

print("-" * 60)

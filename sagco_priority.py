#!/usr/bin/env python3
"""BRICK-005 — SAGCO Organ Priority Map. Ranks organs by weight score, not just cell count."""
import json
import collections
import sys
import os

tree_path = os.environ.get("SAGCO_TREE", "sagco_first_party_tree.json")

if not os.path.exists(tree_path):
    print(f"ERROR: tree file not found: {tree_path}", file=sys.stderr)
    print("Set SAGCO_TREE env var or place sagco_first_party_tree.json in cwd", file=sys.stderr)
    sys.exit(1)

data = json.load(open(tree_path))
cells = data["cells"]

scores = collections.defaultdict(int)
counts = collections.defaultdict(int)
kinds  = collections.defaultdict(collections.Counter)

for c in cells:
    parts = c["path"].split("/")
    organ = parts[2] if len(parts) > 2 else "root"
    scores[organ] += c["weight"]
    counts[organ] += 1
    kinds[organ][c["kind"]] += 1

ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
top_n  = int(sys.argv[1]) if len(sys.argv) > 1 else 40

print("SAGCO ORGAN PRIORITY MAP")
print("=" * 72)
print(f"{'RANK':<5} {'SCORE':>7} {'CELLS':>6}  {'ORGAN'}")
print("-" * 72)
for i, (organ, score) in enumerate(ranked[:top_n], 1):
    print(f"{i:03d}  | score={score:>6} | cells={counts[organ]:>4} | {organ}")
    print("      " + ", ".join(f"{k}:{v}" for k, v in kinds[organ].most_common(4)))
print("-" * 72)
print(f"Total organs ranked: {len(ranked)}  |  Total cells: {len(cells)}")

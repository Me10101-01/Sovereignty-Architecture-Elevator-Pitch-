#!/usr/bin/env python3
"""SAGCO Blueprint — full organism summary: organs, subsystems, ERU status, cell counts."""
import json
import os
import collections

tree_path = os.environ.get("SAGCO_TREE", "sagco_first_party_tree.json")
eru_spec  = os.environ.get("SAGCO_ERU_SPEC", "sagco_eru_spec.json")

print("SAGCO ORGANISM BLUEPRINT")
print("=" * 72)

# ── Cell tree ─────────────────────────────────────────────────────────────────
if os.path.exists(tree_path):
    data  = json.load(open(tree_path))
    cells = data["cells"]

    organs     = collections.defaultdict(lambda: collections.defaultdict(list))
    kind_count = collections.Counter()

    for c in cells:
        parts   = c["path"].split("/")
        organ   = parts[2] if len(parts) > 2 else "root"
        subsys  = parts[3] if len(parts) > 3 else "_root"
        organs[organ][subsys].append(c)
        kind_count[c["kind"]] += 1

    total_weight = sum(c["weight"] for c in cells)

    print(f"\nORGANISM SCALE")
    print(f"  total cells   : {len(cells)}")
    print(f"  total organs  : {len(organs)}")
    print(f"  total weight  : {total_weight}")
    print()
    print("  CELL KINDS:")
    for kind, count in kind_count.most_common():
        bar = "█" * (count * 30 // len(cells))
        print(f"    {kind:<20} {count:>5}  {bar}")

    print()
    print("TOP ORGANS (by weight)")
    print("-" * 72)
    ranked = sorted(
        organs.items(),
        key=lambda x: sum(c["weight"] for cs in x[1].values() for c in cs),
        reverse=True
    )
    for organ, subsystems in ranked[:15]:
        w = sum(c["weight"] for cs in subsystems.values() for c in cs)
        n = sum(len(cs) for cs in subsystems.values())
        sub_names = list(subsystems.keys())[:6]
        print(f"  {organ:<40} weight={w:>6}  cells={n:>4}")
        print(f"    subsystems: {', '.join(sub_names)}")
else:
    print(f"\n[WARNING] tree file not found: {tree_path}")
    print("  run: sagco firstparty")

# ── ERU spec ──────────────────────────────────────────────────────────────────
print()
print("ERU STATUS")
print("-" * 72)
if os.path.exists(eru_spec):
    spec = json.load(open(eru_spec))
    paths   = spec.get("binary_paths", [])
    cmds    = spec.get("subcommands", {})
    statuses = spec.get("status_codes", {})
    eru_bin = "/root/target/release/sagco-eru"
    print(f"  binary     : {'EXISTS' if os.path.exists(eru_bin) else 'MISSING'} → {eru_bin}")
    print(f"  recovered  : {'YES' if os.path.exists('sagco-eru-recovered.sh') else 'NO'}")
    print(f"  known cmds : {len(cmds)}")
    print(f"  pass count : {statuses.get('SAGCO_ERU_PASS', 0)}")
    for code, count in statuses.items():
        print(f"    {code}: {count}")
else:
    print("  [run: sagco recover]")

print()
print("=" * 72)
print("Run 'sagco ask <question>' to query the organism via LLM.")

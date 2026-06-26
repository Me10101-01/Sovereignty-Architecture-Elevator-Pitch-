#!/usr/bin/env python3
"""WBC-008 — SAGCO Subsystem Dependency Graph.
Reveals organ → subsystem hierarchy, structural roles, and hub topology.
"""
import json
import collections
import sys
import os

tree_path = os.environ.get("SAGCO_TREE", "sagco_first_party_tree.json")
target_organ = sys.argv[1] if len(sys.argv) > 1 else None

if not os.path.exists(tree_path):
    print(f"ERROR: {tree_path} not found. Set SAGCO_TREE or run from workspace root.", file=sys.stderr)
    sys.exit(1)

data = json.load(open(tree_path))
cells = data["cells"]

# Structural weight bonuses by path role
ROLE_WEIGHTS = {
    "src":        3,   # execution core
    "pipeline":   2,   # orchestration
    "brain":      2,   # knowledge layer
    "config":     1,   # configuration
    "MANIFEST":   2,   # architecture doc
    "antibodies": 2,   # validation/health
    "binary_router": 2,
    "sync_fleet": 1,
}

# Subsystem role taxonomy (inferred from name patterns)
ROLE_TAXONOMY = {
    "pipeline":             "ORCHESTRATION",
    "binary_router":        "DISPATCH",
    "sagco_compose":        "ORCHESTRATION",
    "sagco_retriever":      "RETRIEVAL",
    "sagco_knowledge":      "INDEXING",
    "sagco_cloud":          "CLOUD",
    "sagco_crawler":        "CRAWL",
    "sagco_lang":           "RUNTIME",
    "sagco_wing":           "INTERFACE",
    "sagco_flame":          "LINGUISTICS",
    "antibodies":           "VALIDATION",
    "sync_fleet":           "SYNC",
    "brain":                "KNOWLEDGE",
    "config":               "CONFIG",
    "rust_lab":             "CORE",
    "rust_fuzz":            "TESTING",
    "rust_excel":           "COMPUTE",
    "rust_compose":         "COMPOSE",
}

def infer_role(name):
    for pattern, role in ROLE_TAXONOMY.items():
        if pattern in name:
            return role
    return "GENERAL"

# Build organ → subsystem → cells map
organs = collections.defaultdict(lambda: collections.defaultdict(list))

for c in cells:
    parts = c["path"].split("/")
    if len(parts) < 3:
        continue
    organ = parts[2]
    subsystem = parts[3] if len(parts) > 3 else "_root"
    organs[organ][subsystem].append(c)

# Filter to target organ if specified
if target_organ:
    if target_organ not in organs:
        print(f"ERROR: organ '{target_organ}' not found.", file=sys.stderr)
        print(f"Known organs: {', '.join(sorted(organs.keys()))}", file=sys.stderr)
        sys.exit(1)
    organ_list = [(target_organ, organs[target_organ])]
else:
    organ_list = sorted(organs.items(), key=lambda x: sum(
        sum(c["weight"] for c in cells) for cells in x[1].values()
    ), reverse=True)[:10]

print("SAGCO SUBSYSTEM DEPENDENCY GRAPH")
print("=" * 80)

for organ_name, subsystems in organ_list:
    total_weight = sum(sum(c["weight"] for c in cs) for cs in subsystems.values())
    total_cells  = sum(len(cs) for cs in subsystems.values())
    print(f"\nORGAN: {organ_name}")
    print(f"       weight={total_weight}  cells={total_cells}")
    print()

    # Rank subsystems by structural weight
    ranked = []
    for sub, cs in subsystems.items():
        base  = sum(c["weight"] for c in cs)
        bonus = sum(ROLE_WEIGHTS.get(seg, 0) for seg in sub.split("_") + [sub])
        role  = infer_role(sub)
        kinds = collections.Counter(c["kind"] for c in cs)
        ranked.append((base + bonus, base, len(cs), sub, role, kinds))
    ranked.sort(reverse=True)

    # Find hubs: subsystems with most cell variety (cross-cutting concerns)
    max_variety = max((len(r[5]) for r in ranked), default=1)

    for score, base, count, sub, role, kinds in ranked:
        hub = " [HUB]" if len(kinds) >= max_variety and len(kinds) > 1 else ""
        kind_str = ", ".join(f"{k}:{v}" for k, v in kinds.most_common(3))
        print(f"  ├── {sub:<36} [{role:<14}] score={score:>5}  cells={count:>3}{hub}")
        print(f"  │   {kind_str}")

    # Edge inference: subsystems that likely feed each other
    print()
    print("  INFERRED EDGES (structural)")
    sub_names = [r[3] for r in ranked]
    edges_found = False
    flow = [
        ("pipeline",      "sagco_retriever",       "feeds"),
        ("pipeline",      "sagco_knowledge",        "feeds"),
        ("sagco_compose", "sagco_cloud",            "publishes→"),
        ("sagco_crawler", "sagco_knowledge",        "indexes→"),
        ("antibodies",    "pipeline",               "validates"),
        ("binary_router", "sagco_retriever",        "dispatches→"),
        ("sync_fleet",    "sagco_cloud",            "syncs→"),
        ("brain",         "sagco_knowledge",        "writes→"),
        ("sagco_wing",    "sagco_compose",          "triggers→"),
        ("sagco_lang",    "sagco_crawler",          "parses→"),
    ]
    for src, dst, label in flow:
        src_match = next((s for s in sub_names if src in s), None)
        dst_match = next((s for s in sub_names if dst in s), None)
        if src_match and dst_match:
            print(f"  {src_match}  --{label}-->  {dst_match}")
            edges_found = True
    if not edges_found:
        print("  (no inferred edges for this organ — run on sagco-raspberry-pi-os-lab)")

print()
print("=" * 80)
print("Run with organ name to inspect a single organ:")
print(f"  {sys.argv[0]} sagco-raspberry-pi-os-lab")

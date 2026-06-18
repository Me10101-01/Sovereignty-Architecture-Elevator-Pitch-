#!/usr/bin/env python3
"""
qa_trainer.py — Generate Q/A training cards from JSON/JSONL sandbox files

JSONL line     → training card (one card per line)
JSON object    → Q/A pair from key/value structure
Schema pattern → structural question

Output: trainer/cards.jsonl (one Q/A pair per line)

Card format:
  {"q": "What is the verdict for claim X?", "a": "PROVEN", "source": "file.json", "domain": "eru"}
"""

import json
import sys
import re
from pathlib import Path
from collections import defaultdict


QUESTION_TEMPLATES = [
    # (key_pattern, question_template, answer_extractor)
    (r"verdict",      "What is the verdict?",                    lambda v: str(v)),
    (r"coverage",     "What is the coverage percentage?",        lambda v: f"{v}%"),
    (r"burnrate",     "What is the burn rate?",                  lambda v: str(v)),
    (r"status",       "What is the status?",                     lambda v: str(v)),
    (r"^id$",         "What is the identifier?",                 lambda v: str(v)),
    (r"text$",        "What does this claim state?",             lambda v: str(v)),
    (r"notes$",       "What are the notes?",                     lambda v: str(v)),
    (r"project$",     "Which project does this belong to?",      lambda v: str(v)),
    (r"category$",    "What category is this?",                  lambda v: str(v)),
    (r"layer$",       "What layer is this?",                     lambda v: str(v)),
    (r"version$",     "What version is this?",                   lambda v: str(v)),
    (r"gap$",         "What is the missing link gap?",           lambda v: str(v)),
    (r"blocks$",      "What does this block?",                   lambda v: json.dumps(v) if isinstance(v, list) else str(v)),
    (r"source$",      "What is the source?",                     lambda v: str(v)),
    (r"severity$",    "What is the severity?",                   lambda v: str(v)),
]


def match_template(key: str, val) -> tuple[str, str] | None:
    if val is None or isinstance(val, (dict, list)):
        return None
    for pattern, q_tmpl, extractor in QUESTION_TEMPLATES:
        if re.search(pattern, key, re.IGNORECASE):
            try:
                return q_tmpl, extractor(val)
            except Exception:
                return None
    return None


def obj_to_cards(obj: dict, source: str) -> list[dict]:
    cards = []
    # Try to get a context identifier
    ctx = obj.get("id") or obj.get("name") or obj.get("claim") or source

    for key, val in obj.items():
        result = match_template(key, val)
        if result:
            q_tmpl, answer = result
            question = f"[{ctx}] {q_tmpl}"
            cards.append({
                "q":      question,
                "a":      answer,
                "source": source,
                "domain": _infer_domain(source, obj),
                "key":    key,
            })

    # Structural Q/A: "What fields does this object have?"
    fields = [k for k in obj.keys() if not isinstance(obj[k], (dict, list))]
    if len(fields) >= 3:
        cards.append({
            "q":      f"[{ctx}] What are the scalar fields in this record?",
            "a":      ", ".join(fields),
            "source": source,
            "domain": _infer_domain(source, obj),
            "key":    "_structure",
        })

    return cards


def _infer_domain(filename: str, obj: dict) -> str:
    fn = filename.lower()
    if any(k in fn for k in ["eru", "claim", "verdict", "burnrate"]): return "eru"
    if any(k in fn for k in ["flamelang", "flame", "flamevm"]): return "flamelang"
    if any(k in fn for k in ["antibody", "ab-"]): return "antibody"
    if any(k in fn for k in ["renko", "trade", "sim"]): return "trading"
    if any(k in fn for k in ["node", "hp", "pi"]): return "hardware"
    if any(k in fn for k in ["mat225", "mobius", "calc"]): return "education"
    if "verdict" in obj: return "eru"
    if "opcode" in obj or "token" in obj: return "flamelang"
    return "sagco"


def run(sandbox_dir: str, out_dir: str) -> int:
    sandbox = Path(sandbox_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    files = list(sandbox.glob("*.json")) + list(sandbox.glob("*.jsonl"))
    total_cards = 0
    domain_counts: dict[str, int] = defaultdict(int)

    out_file = out / "cards.jsonl"
    with open(out_file, "w") as fout:
        for fp in files:
            try:
                if fp.suffix == ".jsonl":
                    with open(fp, encoding="utf-8", errors="ignore") as f:
                        for i, line in enumerate(f):
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                obj = json.loads(line)
                                if isinstance(obj, dict):
                                    for card in obj_to_cards(obj, f"{fp.name}:L{i+1}"):
                                        fout.write(json.dumps(card) + "\n")
                                        total_cards += 1
                                        domain_counts[card["domain"]] += 1
                            except Exception:
                                pass
                else:
                    with open(fp, encoding="utf-8", errors="ignore") as f:
                        data = json.load(f)

                    objects = []
                    if isinstance(data, dict):
                        objects = [data]
                        # Also descend one level for lists of records
                        for v in data.values():
                            if isinstance(v, list):
                                objects.extend(x for x in v if isinstance(x, dict))
                    elif isinstance(data, list):
                        objects = [x for x in data if isinstance(x, dict)]

                    for obj in objects:
                        for card in obj_to_cards(obj, fp.name):
                            fout.write(json.dumps(card) + "\n")
                            total_cards += 1
                            domain_counts[card["domain"]] += 1
            except Exception:
                pass

    print(f"  Files processed       : {len(files)}")
    print(f"  Training cards        : {total_cards:,}")
    print(f"  Domain breakdown:")
    for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
        print(f"    {domain:20s}: {count:,}")
    print(f"  Output                : {out_file}")

    return total_cards


if __name__ == "__main__":
    sandbox = sys.argv[1] if len(sys.argv) > 1 else "sandbox"
    out     = sys.argv[2] if len(sys.argv) > 2 else "trainer"
    run(sandbox, out)

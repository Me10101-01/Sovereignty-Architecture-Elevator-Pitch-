#!/usr/bin/env python3
"""
token_extractor.py — Extract SAGCO vocabulary from sandbox JSON files

JSON key     → token
JSON value   → token candidate (if high-frequency string)
JSON schema  → grammar rule seed

Output: vocabulary/tokens.json + vocabulary/sagco_vocab.yaml
"""

import json
import sys
import re
from pathlib import Path
from collections import Counter
import yaml


SAGCO_DOMAINS = {
    "sagco", "eru", "flamelang", "flamevm", "antibody", "brick", "registry",
    "verdict", "claim", "evidence", "burnrate", "lineage", "corpus", "sovereign",
    "swarm", "athena", "nova", "lyra", "qdrant", "inv", "vesta", "renko",
    "chess", "node", "hp", "mat225", "mobius", "dsa", "trig6",
}


def is_sagco_token(s: str) -> bool:
    s_lower = s.lower()
    return any(domain in s_lower for domain in SAGCO_DOMAINS)


def camel_to_tokens(s: str) -> list[str]:
    return re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)", s)


def snake_to_tokens(s: str) -> list[str]:
    return [p for p in s.split("_") if p]


def extract_tokens_from_obj(obj, depth=0) -> list[str]:
    tokens = []
    if depth > 8:
        return tokens
    if isinstance(obj, dict):
        for k, v in obj.items():
            tokens.append(k)
            tokens.extend(camel_to_tokens(k))
            tokens.extend(snake_to_tokens(k))
            tokens.extend(extract_tokens_from_obj(v, depth + 1))
    elif isinstance(obj, list):
        for item in obj[:20]:
            tokens.extend(extract_tokens_from_obj(item, depth + 1))
    elif isinstance(obj, str) and 2 < len(obj) < 80:
        tokens.append(obj)
        tokens.extend(camel_to_tokens(obj))
        tokens.extend(snake_to_tokens(obj))
    return tokens


def run(sandbox_dir: str, out_dir: str) -> dict:
    sandbox = Path(sandbox_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    files = list(sandbox.glob("*.json")) + list(sandbox.glob("*.jsonl"))
    all_tokens: list[str] = []

    for fp in files:
        try:
            if fp.suffix == ".jsonl":
                with open(fp, encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                all_tokens.extend(extract_tokens_from_obj(json.loads(line)))
                            except Exception:
                                pass
            else:
                with open(fp, encoding="utf-8", errors="ignore") as f:
                    all_tokens.extend(extract_tokens_from_obj(json.load(f)))
        except Exception:
            pass

    counter = Counter(t.lower() for t in all_tokens if len(t) >= 2)

    # Separate SAGCO domain tokens from general tokens
    sagco_tokens = {k: v for k, v in counter.items() if is_sagco_token(k)}
    general_tokens = {k: v for k, v in counter.most_common(500) if not is_sagco_token(k)}

    # Build vocabulary
    vocab = {
        "sagco_domain_tokens": dict(sorted(sagco_tokens.items(), key=lambda x: -x[1])[:200]),
        "general_tokens":      dict(list(general_tokens.items())[:200]),
        "total_tokens_seen":   len(all_tokens),
        "unique_tokens":       len(counter),
        "files_processed":     len(files),
    }

    # FlameLang type candidates from high-frequency SAGCO tokens
    fl_types = []
    for token, freq in vocab["sagco_domain_tokens"].items():
        if freq >= 5:
            fl_types.append(f"{token}: Token  // freq={freq}")

    sagco_vocab = {
        "version":            "0.1.0",
        "source":             "headless-json-trainer",
        "flamelang_type_seeds": fl_types[:50],
        "top_sagco_tokens":   list(vocab["sagco_domain_tokens"].keys())[:50],
        "top_general_tokens": list(vocab["general_tokens"].keys())[:30],
    }

    with open(out / "tokens.json", "w") as f:
        json.dump(vocab, f, indent=2)

    with open(out / "sagco_vocab.yaml", "w") as f:
        yaml.dump(sagco_vocab, f, default_flow_style=False, sort_keys=False)

    print(f"  Files processed       : {len(files)}")
    print(f"  Total tokens seen     : {len(all_tokens):,}")
    print(f"  Unique tokens         : {len(counter):,}")
    print(f"  SAGCO domain tokens   : {len(sagco_tokens)}")
    print(f"  FlameLang type seeds  : {len(fl_types)}")
    print(f"  Output                : {out}/tokens.json + sagco_vocab.yaml")

    return vocab


if __name__ == "__main__":
    sandbox = sys.argv[1] if len(sys.argv) > 1 else "sandbox"
    out     = sys.argv[2] if len(sys.argv) > 2 else "vocabulary"
    run(sandbox, out)

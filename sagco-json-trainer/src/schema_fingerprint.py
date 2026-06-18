#!/usr/bin/env python3
"""
schema_fingerprint.py — Fingerprint all JSON schemas in sandbox/

For every .json/.jsonl file:
  - Extract all keys
  - Record their value types
  - Track frequency across files
  - Emit schemas/fingerprint.yaml

FlameLang rule:
  key appears in N files with consistent type → FlameLang type candidate
  key appears with inconsistent types → antibody candidate (type ambiguity)
"""

import json
import os
import sys
import yaml
from collections import defaultdict
from pathlib import Path


def json_type(val) -> str:
    if val is None:          return "null"
    if isinstance(val, bool): return "bool"
    if isinstance(val, int):  return "int"
    if isinstance(val, float): return "float"
    if isinstance(val, str):
        if len(val) == 24 and val.endswith("Z"): return "ISO8601"
        if val.upper() in ("PROVEN","PROMISING","UNPROVEN","INFLATED"): return "Verdict"
        if val.startswith("INV-"):  return "INVRef"
        if val.startswith("ERU-"):  return "ERURef"
        if val.startswith("AB-"):   return "AntibodyRef"
        if val.startswith("SAGCO-"): return "SAGCORef"
        return "str"
    if isinstance(val, list): return f"list[{json_type(val[0]) if val else 'any'}]"
    if isinstance(val, dict): return "object"
    return "unknown"


def fingerprint_object(obj: dict, prefix: str = "") -> list[tuple[str, str]]:
    """Recursively extract (key_path, type) pairs from a JSON object."""
    results = []
    for k, v in obj.items():
        path = f"{prefix}.{k}" if prefix else k
        results.append((path, json_type(v)))
        if isinstance(v, dict):
            results.extend(fingerprint_object(v, path))
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            results.extend(fingerprint_object(v[0], f"{path}[]"))
    return results


def fingerprint_file(filepath: Path) -> list[tuple[str, str]]:
    """Fingerprint a single .json or .jsonl file."""
    results = []
    try:
        if filepath.suffix == ".jsonl":
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        if isinstance(obj, dict):
                            results.extend(fingerprint_object(obj))
                    except json.JSONDecodeError:
                        pass
        else:
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                obj = json.load(f)
            if isinstance(obj, dict):
                results.extend(fingerprint_object(obj))
            elif isinstance(obj, list) and obj and isinstance(obj[0], dict):
                results.extend(fingerprint_object(obj[0]))
    except Exception:
        pass
    return results


def run(sandbox_dir: str, out_dir: str) -> dict:
    sandbox = Path(sandbox_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    files = list(sandbox.glob("*.json")) + list(sandbox.glob("*.jsonl"))
    if not files:
        print(f"  No JSON files found in {sandbox_dir}")
        return {}

    key_types: dict[str, dict[str, set]] = defaultdict(lambda: defaultdict(set))
    key_file_count: dict[str, int] = defaultdict(int)

    for fp in files:
        pairs = fingerprint_file(fp)
        seen_keys = set()
        for key, typ in pairs:
            key_types[key][typ].add(fp.name)
            if key not in seen_keys:
                key_file_count[key] += 1
                seen_keys.add(key)

    # Build fingerprint
    fingerprint = {}
    flamelang_candidates = []
    antibody_candidates = []

    for key in sorted(key_types.keys()):
        types = {t: list(files) for t, files in key_types[key].items()}
        file_count = key_file_count[key]
        dominant_type = max(types, key=lambda t: len(types[t]))
        is_consistent = len(types) == 1

        entry = {
            "key":        key,
            "types":      {t: len(fs) for t, fs in types.items()},
            "file_count": file_count,
            "consistent": is_consistent,
            "dominant":   dominant_type,
        }
        fingerprint[key] = entry

        if file_count >= 3 and is_consistent:
            flamelang_candidates.append({
                "key":        key,
                "type":       dominant_type,
                "frequency":  file_count,
                "confidence": "HIGH" if file_count >= 10 else "MEDIUM",
            })

        if not is_consistent and file_count >= 2:
            antibody_candidates.append({
                "id":      f"AB-TYPE-MISMATCH-{key.upper().replace('.','_')}",
                "key":     key,
                "types":   list(types.keys()),
                "trigger": f"key '{key}' appears as {list(types.keys())} — type ambiguity",
                "msg":     f"FlameLang M2 type error: '{key}' has inconsistent types across files",
            })

    result = {
        "files_scanned":        len(files),
        "unique_keys":          len(fingerprint),
        "flamelang_candidates": flamelang_candidates,
        "antibody_candidates":  antibody_candidates,
        "fingerprint":          fingerprint,
    }

    with open(out / "fingerprint.yaml", "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)

    print(f"  Files scanned         : {len(files)}")
    print(f"  Unique keys found     : {len(fingerprint)}")
    print(f"  FlameLang candidates  : {len(flamelang_candidates)}")
    print(f"  Antibody candidates   : {len(antibody_candidates)}")
    print(f"  Output                : {out}/fingerprint.yaml")

    return result


if __name__ == "__main__":
    sandbox = sys.argv[1] if len(sys.argv) > 1 else "sandbox"
    out     = sys.argv[2] if len(sys.argv) > 2 else "schemas"
    run(sandbox, out)

#!/usr/bin/env python3
"""
antibody_builder.py — Build antibodies from JSON parse failures and type mismatches

Sources:
  - Parse errors from sandbox files (malformed JSON)
  - Type mismatches from schema_fingerprint output
  - Structural anomalies (missing required keys, unexpected nulls)

Output: antibodies/parse_failures.yaml
"""

import json
import sys
import yaml
from pathlib import Path
from collections import defaultdict


REQUIRED_SAGCO_KEYS = {
    "eru_claim":  ["id", "text", "verdict", "coverage"],
    "antibody":   ["id", "trigger", "msg"],
    "brick":      ["id", "name", "version", "layer"],
    "missing_link": ["id", "gap", "status"],
}


def sniff_record_type(obj: dict) -> str:
    keys = set(obj.keys())
    if {"verdict", "coverage", "expected", "actual"} & keys: return "eru_claim"
    if {"trigger", "msg"} & keys: return "antibody"
    if {"layer", "capabilities"} & keys: return "brick"
    if {"gap", "blocks"} & keys: return "missing_link"
    return "unknown"


def check_required_keys(obj: dict, record_type: str, source: str) -> list[dict]:
    antibodies = []
    required = REQUIRED_SAGCO_KEYS.get(record_type, [])
    for req_key in required:
        if req_key not in obj:
            antibodies.append({
                "id":       f"AB-MISSING-KEY-{req_key.upper()}",
                "type":     "missing_required_key",
                "key":      req_key,
                "record":   record_type,
                "source":   source,
                "trigger":  f"{record_type} record missing required key '{req_key}'",
                "msg":      f"Add '{req_key}' to all {record_type} records. Source: {source}",
                "severity": "HIGH",
            })
    return antibodies


def scan_file_for_parse_errors(filepath: Path) -> list[dict]:
    antibodies = []
    try:
        if filepath.suffix == ".jsonl":
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        json.loads(line)
                    except json.JSONDecodeError as e:
                        antibodies.append({
                            "id":       f"AB-PARSE-FAIL-{filepath.stem.upper()[:20]}-L{i+1}",
                            "type":     "json_parse_error",
                            "source":   str(filepath.name),
                            "line":     i + 1,
                            "trigger":  f"JSONDecodeError at line {i+1}: {str(e)[:120]}",
                            "msg":      f"Fix malformed JSONL in {filepath.name} at line {i+1}",
                            "severity": "MEDIUM",
                        })
        else:
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                content = f.read()
            try:
                data = json.loads(content)
                # Structural checks
                objects = []
                if isinstance(data, dict):
                    objects = [data]
                    for v in data.values():
                        if isinstance(v, list):
                            objects.extend(x for x in v if isinstance(x, dict))
                elif isinstance(data, list):
                    objects = [x for x in data if isinstance(x, dict)]

                for obj in objects:
                    rt = sniff_record_type(obj)
                    if rt != "unknown":
                        antibodies.extend(check_required_keys(obj, rt, filepath.name))

            except json.JSONDecodeError as e:
                antibodies.append({
                    "id":       f"AB-PARSE-FAIL-{filepath.stem.upper()[:20]}",
                    "type":     "json_parse_error",
                    "source":   filepath.name,
                    "trigger":  f"JSONDecodeError: {str(e)[:120]}",
                    "msg":      f"File {filepath.name} is not valid JSON",
                    "severity": "HIGH",
                })
    except Exception as ex:
        antibodies.append({
            "id":       f"AB-READ-FAIL-{filepath.stem.upper()[:20]}",
            "type":     "file_read_error",
            "source":   filepath.name,
            "trigger":  str(ex)[:120],
            "msg":      f"Could not read {filepath.name}",
            "severity": "LOW",
        })
    return antibodies


def run(sandbox_dir: str, schema_file: str, out_dir: str) -> list[dict]:
    sandbox = Path(sandbox_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    all_antibodies: list[dict] = []

    # Phase 1: Parse failure scan
    files = list(sandbox.glob("*.json")) + list(sandbox.glob("*.jsonl"))
    for fp in files:
        all_antibodies.extend(scan_file_for_parse_errors(fp))

    # Phase 2: Type mismatch antibodies from fingerprint
    schema_path = Path(schema_file)
    if schema_path.exists():
        try:
            with open(schema_path) as f:
                fingerprint = yaml.safe_load(f)
            for ab in fingerprint.get("antibody_candidates", []):
                all_antibodies.append(ab)
        except Exception:
            pass

    # Deduplicate by id
    seen_ids = set()
    deduped = []
    for ab in all_antibodies:
        ab_id = ab.get("id", "")
        if ab_id not in seen_ids:
            seen_ids.add(ab_id)
            deduped.append(ab)

    # Group by severity
    by_severity: dict[str, list] = defaultdict(list)
    for ab in deduped:
        by_severity[ab.get("severity", "UNKNOWN")].append(ab)

    output = {
        "total":          len(deduped),
        "by_severity":    {k: len(v) for k, v in by_severity.items()},
        "antibodies":     deduped,
    }

    out_file = out / "parse_failures.yaml"
    with open(out_file, "w") as f:
        yaml.dump(output, f, default_flow_style=False, sort_keys=False)

    print(f"  Files scanned         : {len(files)}")
    print(f"  Total antibodies      : {len(deduped)}")
    for sev, items in sorted(by_severity.items()):
        print(f"    {sev:8s}: {len(items)}")
    print(f"  Output                : {out_file}")

    return deduped


if __name__ == "__main__":
    sandbox     = sys.argv[1] if len(sys.argv) > 1 else "sandbox"
    schema_file = sys.argv[2] if len(sys.argv) > 2 else "schemas/fingerprint.yaml"
    out_dir     = sys.argv[3] if len(sys.argv) > 3 else "antibodies"
    run(sandbox, schema_file, out_dir)

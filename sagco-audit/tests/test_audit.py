#!/usr/bin/env python3
"""
test_audit.py — Board A audit layer tests

All tests use tmp_path (pytest fixture) — nothing written to live registry/reports.
"""

import json
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import invocation_logger
import decision_tracer
import variance_reporter
from antibody_registry import load_registry


# ── invocation_logger ──────────────────────────────────────────────────────

def test_log_writes_jsonl(tmp_path):
    log = tmp_path / "invocation_log.jsonl"
    entry = invocation_logger.log_invocation(
        command="eru compute",
        args={"config": "sagco.master.yaml"},
        result="CPI=1.39 AHEAD",
        verdict="COMPUTED",
        duration_ms=42.1,
        log_path=log,
    )
    assert log.exists()
    lines = [l for l in log.read_text().splitlines() if l.strip()]
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["command"] == "eru compute"
    assert data["verdict"] == "COMPUTED"
    assert "sha256" in data


def test_log_sha256_changes_on_diff_result(tmp_path):
    log = tmp_path / "invocation_log.jsonl"
    e1 = invocation_logger.log_invocation("cmd", {}, "result_A", log_path=log)
    e2 = invocation_logger.log_invocation("cmd", {}, "result_B", log_path=log)
    assert e1["sha256"] != e2["sha256"]


def test_log_tail_returns_n(tmp_path):
    log = tmp_path / "invocation_log.jsonl"
    for i in range(5):
        invocation_logger.log_invocation(f"cmd_{i}", {}, f"result_{i}", log_path=log)
    entries = invocation_logger.tail(3, log_path=log)
    assert len(entries) == 3
    assert entries[-1]["command"] == "cmd_4"


def test_count_by_verdict(tmp_path):
    log = tmp_path / "invocation_log.jsonl"
    invocation_logger.log_invocation("a", {}, "ok",  verdict="COMPUTED",        log_path=log)
    invocation_logger.log_invocation("b", {}, "err", verdict="FAILED_COMPUTE",  log_path=log)
    invocation_logger.log_invocation("c", {}, "ok",  verdict="COMPUTED",        log_path=log)
    counts = invocation_logger.count_by_verdict(log_path=log)
    assert counts["COMPUTED"]       == 2
    assert counts["FAILED_COMPUTE"] == 1


# ── decision_tracer ────────────────────────────────────────────────────────

def test_trace_proven(tmp_path):
    t = tmp_path / "trace.jsonl"
    e = decision_tracer.trace_decision("ERU-001", 100, 107, "eru", trace_path=t)
    assert e["verdict"] == "PROVEN"
    assert e["ratio"]   == pytest.approx(1.07, abs=1e-4)


def test_trace_promising(tmp_path):
    t = tmp_path / "trace.jsonl"
    e = decision_tracer.trace_decision("ERU-002", 100, 75, "eru", trace_path=t)
    assert e["verdict"] == "PROMISING"


def test_trace_unproven(tmp_path):
    t = tmp_path / "trace.jsonl"
    e = decision_tracer.trace_decision("ERU-003", 100, 30, "eru", trace_path=t)
    assert e["verdict"] == "UNPROVEN"


def test_trace_inflated(tmp_path):
    t = tmp_path / "trace.jsonl"
    e = decision_tracer.trace_decision("ERU-004", 10000, 1, "eru", trace_path=t)
    assert e["verdict"] == "INFLATED"


def test_trace_expected_zero_no_crash(tmp_path):
    t = tmp_path / "trace.jsonl"
    e = decision_tracer.trace_decision("ERU-005", 0, 50, "eru", trace_path=t)
    assert e["ratio"] == 0.0


def test_burn_rate_all_proven(tmp_path):
    t = tmp_path / "trace.jsonl"
    for i in range(4):
        decision_tracer.trace_decision(f"C-{i:03d}", 100, 100, trace_path=t)
    stats = decision_tracer.burn_rate(trace_path=t)
    assert stats["burn_rate"] == 1.0
    assert stats["total"] == 4


def test_burn_rate_mixed(tmp_path):
    t = tmp_path / "trace.jsonl"
    decision_tracer.trace_decision("A", 100, 100, trace_path=t)  # PROVEN
    decision_tracer.trace_decision("B", 100, 60,  trace_path=t)  # PROMISING
    stats = decision_tracer.burn_rate(trace_path=t)
    assert stats["burn_rate"] == pytest.approx(0.5)


# ── variance_reporter ──────────────────────────────────────────────────────

def test_report_empty_trace(tmp_path):
    t = tmp_path / "trace.jsonl"
    r = tmp_path / "report.json"
    report = variance_reporter.build_report(trace_path=t, out_path=r)
    assert report["total_decisions"] == 0
    assert report["global_burn_rate"] == 0.0
    assert r.exists()


def test_report_antibody_candidate_on_drift(tmp_path):
    t = tmp_path / "trace.jsonl"
    r = tmp_path / "report.json"
    # Three low-ratio traces for same claim
    for _ in range(3):
        decision_tracer.trace_decision("DRIFTING-001", 100, 20, "eru", trace_path=t)
    report = variance_reporter.build_report(trace_path=t, out_path=r)
    assert report["antibody_candidates"] >= 1
    ab_ids = [a["claim_id"] for a in report["antibodies"]]
    assert "DRIFTING-001" in ab_ids


def test_report_trend_improving(tmp_path):
    t = tmp_path / "trace.jsonl"
    r = tmp_path / "report.json"
    # Ratios improving over time (0.4, 0.6, 0.9)
    for actual in [40, 60, 90]:
        decision_tracer.trace_decision("TREND-001", 100, actual, "eru", trace_path=t)
    report = variance_reporter.build_report(trace_path=t, out_path=r)
    claim = next(c for c in report["claims"] if c["claim_id"] == "TREND-001")
    assert claim["trend"] == "IMPROVING"


# ── antibody_registry ──────────────────────────────────────────────────────

def test_registry_loads():
    registry = load_registry()
    assert registry["total"] >= 1
    assert len(registry["antibodies"]) >= 1


def test_all_antibodies_have_required_fields():
    registry = load_registry()
    for ab in registry["antibodies"]:
        for field in ["id", "domain", "severity", "trigger", "msg"]:
            assert field in ab, f"Antibody {ab.get('id', '?')} missing field '{field}'"


def test_registry_covers_all_domains():
    registry = load_registry()
    domains = {ab["domain"] for ab in registry["antibodies"]}
    assert "eru"        in domains
    assert "flamelang"  in domains
    assert "audit"      in domains
    assert "corpus"     in domains

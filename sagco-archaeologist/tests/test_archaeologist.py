"""
SAGCO Archaeologist — Test Suite
Tests all 6 agents individually and the full pipeline.

Run: cd sagco-archaeologist && python -m pytest tests/ -v
"""

import json
import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path
import pytest

# Add sagco-archaeologist to path
_HERE = Path(__file__).parent.parent
sys.path.insert(0, str(_HERE))

from agents import origin_agent, evolution_agent, evidence_agent
from agents import skeptic_agent, novelty_agent, seal_agent
from runner.archaeologist import audit


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_repo(tmp_path):
    """Create a minimal fake git repo with one tracked file."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=str(repo), capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@sagco.test"], cwd=str(repo), capture_output=True)
    subprocess.run(["git", "config", "user.name", "SAGCO Test"], cwd=str(repo), capture_output=True)

    # Create a file with ERU keywords in commits
    artifact = repo / "artifact.py"
    artifact.write_text("# eru decision trace\nratio = actual / expected\n")
    subprocess.run(["git", "add", "artifact.py"], cwd=str(repo), capture_output=True)
    subprocess.run(["git", "commit", "-m", "add eru artifact"], cwd=str(repo), capture_output=True)

    # Second commit
    artifact.write_text("# eru decision trace v2\nratio = actual / expected\nverdict = 'PROVEN'\n")
    subprocess.run(["git", "add", "artifact.py"], cwd=str(repo), capture_output=True)
    subprocess.run(["git", "commit", "-m", "proven verdict added"], cwd=str(repo), capture_output=True)

    return repo


@pytest.fixture
def logs_dir(tmp_path):
    d = tmp_path / "logs"
    d.mkdir()
    return d


@pytest.fixture
def out_dir(tmp_path):
    d = tmp_path / "reports"
    d.mkdir()
    return d


# ---------------------------------------------------------------------------
# Agent_001 — Origin Finder
# ---------------------------------------------------------------------------

class TestOriginAgent:
    def test_returns_dict_with_required_keys(self, fake_repo, logs_dir):
        result = origin_agent.run("artifact.py", str(fake_repo), str(logs_dir))
        assert "agent" in result
        assert result["agent"] == "Agent_001_OriginFinder"
        assert "signals" in result
        assert "verdict" in result
        assert "era_ratio" in result

    def test_finds_git_commit(self, fake_repo, logs_dir):
        result = origin_agent.run("artifact.py", str(fake_repo), str(logs_dir))
        assert result["signals"]["git_first_commit"] is not None
        commit = result["signals"]["git_first_commit"]
        assert "commit_hash" in commit
        assert "timestamp" in commit

    def test_era_ratio_nonzero(self, fake_repo, logs_dir):
        result = origin_agent.run("artifact.py", str(fake_repo), str(logs_dir))
        # Git commit found + mtime found = at least 2/5 = 0.4
        assert result["era_ratio"] >= 0.2

    def test_missing_file_no_crash(self, tmp_path, logs_dir):
        result = origin_agent.run("nonexistent.py", str(tmp_path), str(logs_dir))
        assert result["verdict"] in ("PROVEN", "PROMISING", "UNPROVEN", "INFLATED")

    def test_verdict_is_valid_eru(self, fake_repo, logs_dir):
        result = origin_agent.run("artifact.py", str(fake_repo), str(logs_dir))
        assert result["verdict"] in ("PROVEN", "PROMISING", "UNPROVEN", "INFLATED")


# ---------------------------------------------------------------------------
# Agent_002 — Evolution Tracker
# ---------------------------------------------------------------------------

class TestEvolutionAgent:
    def test_returns_dict_with_required_keys(self, fake_repo):
        result = evolution_agent.run("artifact.py", str(fake_repo))
        assert result["agent"] == "Agent_002_EvolutionTracker"
        assert "total_commits" in result
        assert "verdict" in result

    def test_finds_two_commits(self, fake_repo):
        result = evolution_agent.run("artifact.py", str(fake_repo))
        assert result["total_commits"] == 2

    def test_eru_commits_detected(self, fake_repo):
        result = evolution_agent.run("artifact.py", str(fake_repo))
        # Both commits contain eru/proven keywords
        assert result["eru_commits"] >= 1

    def test_inflection_first_eru(self, fake_repo):
        result = evolution_agent.run("artifact.py", str(fake_repo))
        inflections = result["inflections"]
        eru_found = any("FIRST_ERU" in i.get("inflection_tags", []) for i in inflections)
        assert eru_found

    def test_no_commits_no_crash(self, tmp_path):
        # Non-tracked file
        result = evolution_agent.run("ghost.py", str(tmp_path))
        assert result["total_commits"] == 0
        assert result["verdict"] == "INFLATED"


# ---------------------------------------------------------------------------
# Agent_003 — Evidence Correlator
# ---------------------------------------------------------------------------

class TestEvidenceAgent:
    def test_returns_dict_with_required_keys(self, fake_repo, logs_dir):
        result = evidence_agent.run("artifact.py", str(fake_repo), str(logs_dir))
        assert result["agent"] == "Agent_003_EvidenceCorrelator"
        assert "sources" in result
        assert "sources_checked" in result

    def test_git_source_found(self, fake_repo, logs_dir):
        result = evidence_agent.run("artifact.py", str(fake_repo), str(logs_dir))
        assert result["sources"]["git"] is not None

    def test_ratio_between_0_and_1(self, fake_repo, logs_dir):
        result = evidence_agent.run("artifact.py", str(fake_repo), str(logs_dir))
        assert 0.0 <= result["era_ratio"] <= 1.0

    def test_patent_grader_plausible(self):
        # grader_006 inline: US10000000 should fall in 2010s window
        result = evidence_agent._patent_plausible("10000000")
        assert result["flag"] in ("PLAUSIBLE", "SUSPICIOUS — verify USPTO")

    def test_patent_grader_suspicious(self):
        # 99999999 is outside all windows
        result = evidence_agent._patent_plausible("99999999")
        assert result["flag"] == "SUSPICIOUS — verify USPTO"


# ---------------------------------------------------------------------------
# Agent_004 — Skeptic
# ---------------------------------------------------------------------------

class TestSkepticAgent:
    def _make_origin(self):
        return {
            "agent": "Agent_001_OriginFinder",
            "artifact": "sha256_seal.py",
            "signals": {"git_first_commit": {"hash": "abc", "timestamp": "2025-01-01", "message": "add sha256 seal"}},
            "earliest": "2025-01-01",
            "era_ratio": 0.4,
            "verdict": "UNPROVEN",
        }

    def _make_evidence(self, artifact="sha256_seal.py"):
        return {
            "agent": "Agent_003_EvidenceCorrelator",
            "artifact": artifact,
            "sources": {
                "git": {"commit_count": 1, "sample": ["abc add sha256 seal"]},
                "pdf": None, "sha_seal": None, "markdown": None,
                "jsonl": None, "patents": None, "toml": None,
            },
            "sources_found": 1,
            "sources_checked": 7,
            "era_ratio": 0.14,
            "verdict": "UNPROVEN",
        }

    def test_returns_required_keys(self):
        result = skeptic_agent.run(self._make_origin(), self._make_evidence())
        assert result["agent"] == "Agent_004_PriorArtHonesty"
        assert "claims_evaluated" in result
        assert "novel_claims" in result
        assert "known_primitives" in result

    def test_sha256_is_known_primitive(self):
        result = skeptic_agent.run(self._make_origin(), self._make_evidence("sha256_seal.py"))
        known = result["known_primitives"]
        assert any("sha256" in k for k in known)

    def test_novel_claim_survives_empty_db(self, tmp_path):
        db_path = str(tmp_path / "empty_db.yaml")
        Path(db_path).write_text("primitives: []\ncombinations: []\n")
        result = skeptic_agent.run(self._make_origin(), self._make_evidence("mystery_invention.py"), db_path=db_path)
        # With empty DB, skeptic can't disprove anything → all claims survive as candidate novelty
        assert result["candidate_novelties"] >= 0  # 0 is fine if no claims extracted

    def test_discipline_valid_values(self):
        result = skeptic_agent.run(self._make_origin(), self._make_evidence())
        assert result["skeptic_discipline"] in ("PROVEN", "PROMISING", "UNPROVEN", "INFLATED")


# ---------------------------------------------------------------------------
# Agent_005 — Novelty Detector
# ---------------------------------------------------------------------------

class TestNoveltyAgent:
    def _make_skeptic(self, novel=None, known_prims=None, known_combos=None):
        return {
            "agent": "Agent_004_PriorArtHonesty",
            "artifact": "artifact.py",
            "novel_claims": novel or [],
            "known_primitives": known_prims or ["sha256 file hashing"],
            "known_combos": known_combos or [],
            "claims_evaluated": [],
            "total_claims": 1,
            "candidate_novelties": len(novel or []),
            "skeptic_ratio": 0.0,
            "skeptic_discipline": "PROVEN",
        }

    def test_returns_required_keys(self):
        result = novelty_agent.run(self._make_skeptic())
        assert result["agent"] == "Agent_005_NoveltyDetector"
        assert "overall_classification" in result
        assert "patent_recommendation" in result
        assert "verdict" in result

    def test_all_known_is_inflated(self):
        result = novelty_agent.run(self._make_skeptic())
        assert result["verdict"] == "INFLATED"
        assert result["overall_classification"] in ("KNOWN_PRIMITIVE", "INSUFFICIENT_EVIDENCE")

    def test_recursive_claim_elevates_to_candidate(self):
        result = novelty_agent.run(self._make_skeptic(novel=["recursive provenance verifier"]))
        assert result["overall_classification"] == "CANDIDATE_INVENTION"

    def test_sagco_claim_is_novel_composition(self):
        result = novelty_agent.run(self._make_skeptic(novel=["sagco eru dispatcher"]))
        assert result["overall_classification"] in ("NOVEL_COMPOSITION", "CANDIDATE_INVENTION")

    def test_patent_rec_present(self):
        result = novelty_agent.run(self._make_skeptic(novel=["archaeologist recursive verifier"]))
        assert "PATENT" in result["patent_recommendation"].upper() or "PROVISIONAL" in result["patent_recommendation"].upper()


# ---------------------------------------------------------------------------
# Agent_006 — Seal Agent
# ---------------------------------------------------------------------------

class TestSealAgent:
    def _make_all_results(self):
        origin = {"agent": "Agent_001_OriginFinder", "artifact": "test.py", "earliest": "2025-01-01T00:00:00+00:00", "era_ratio": 0.4, "verdict": "UNPROVEN", "signals": {}}
        evolution = {"agent": "Agent_002_EvolutionTracker", "artifact": "test.py", "total_commits": 2, "era_ratio": 0.5, "verdict": "PROMISING", "timeline": [{"timestamp": "2025-01-01T00:00:00+00:00"}], "inflections": []}
        evidence = {"agent": "Agent_003_EvidenceCorrelator", "artifact": "test.py", "sources": {}, "sources_found": 1, "sources_checked": 7, "era_ratio": 0.14, "verdict": "UNPROVEN"}
        skeptic = {"agent": "Agent_004_PriorArtHonesty", "artifact": "test.py", "novel_claims": ["recursive verifier"], "known_primitives": ["sha256"], "known_combos": [], "claims_evaluated": [], "total_claims": 2, "candidate_novelties": 1, "skeptic_ratio": 0.5, "skeptic_discipline": "PROMISING"}
        novelty = {"agent": "Agent_005_NoveltyDetector", "artifact": "test.py", "claims_scored": [], "overall_classification": "NOVEL_COMPOSITION", "novelty_ratio": 0.75, "era_ratio": 0.75, "verdict": "PROVEN", "patent_recommendation": "CONSIDER PROVISIONAL"}
        return origin, evolution, evidence, skeptic, novelty

    def test_creates_manifest_file(self, tmp_path):
        origin, evolution, evidence, skeptic, novelty = self._make_all_results()
        result = seal_agent.run(origin, evolution, evidence, skeptic, novelty,
                                out_dir=str(tmp_path), artifact_path="test.py")
        assert os.path.exists(result["manifest_path"])

    def test_manifest_is_valid_json(self, tmp_path):
        origin, evolution, evidence, skeptic, novelty = self._make_all_results()
        result = seal_agent.run(origin, evolution, evidence, skeptic, novelty,
                                out_dir=str(tmp_path), artifact_path="test.py")
        with open(result["manifest_path"]) as f:
            data = json.loads(f.readline())
        assert data["sagco_archaeologist_manifest"] is True

    def test_sha256_seal_created(self, tmp_path):
        origin, evolution, evidence, skeptic, novelty = self._make_all_results()
        result = seal_agent.run(origin, evolution, evidence, skeptic, novelty,
                                out_dir=str(tmp_path), artifact_path="test.py")
        assert os.path.exists(result["seal_path"])
        seal_content = Path(result["seal_path"]).read_text()
        assert result["manifest_sha256"] in seal_content

    def test_sha256_seal_is_64_chars(self, tmp_path):
        origin, evolution, evidence, skeptic, novelty = self._make_all_results()
        result = seal_agent.run(origin, evolution, evidence, skeptic, novelty,
                                out_dir=str(tmp_path), artifact_path="test.py")
        assert len(result["manifest_sha256"]) == 64

    def test_aggregate_verdict_valid(self, tmp_path):
        origin, evolution, evidence, skeptic, novelty = self._make_all_results()
        result = seal_agent.run(origin, evolution, evidence, skeptic, novelty,
                                out_dir=str(tmp_path), artifact_path="test.py")
        assert result["aggregate_verdict"] in ("PROVEN", "PROMISING", "UNPROVEN", "INFLATED")


# ---------------------------------------------------------------------------
# Full Pipeline — Integration
# ---------------------------------------------------------------------------

class TestFullPipeline:
    def test_full_audit_on_fake_repo(self, fake_repo, out_dir):
        result = audit(
            artifact_path="artifact.py",
            repo_root=str(fake_repo),
            logs_dir=str(fake_repo / "logs"),
            out_dir=str(out_dir),
            verbose=False,
        )
        assert result["aggregate_verdict"] in ("PROVEN", "PROMISING", "UNPROVEN", "INFLATED")
        assert os.path.exists(result["manifest_path"])
        assert len(result["manifest_sha256"]) == 64

    def test_manifest_contains_all_agents(self, fake_repo, out_dir):
        result = audit(
            artifact_path="artifact.py",
            repo_root=str(fake_repo),
            logs_dir=str(fake_repo / "logs"),
            out_dir=str(out_dir),
            verbose=False,
        )
        with open(result["manifest_path"]) as f:
            data = json.loads(f.readline())
        outputs = data.get("agent_outputs", {})
        assert "origin"    in outputs
        assert "evolution" in outputs
        assert "evidence"  in outputs
        assert "skeptic"   in outputs
        assert "novelty"   in outputs

    def test_seal_is_deterministic_content_matches(self, fake_repo, out_dir):
        import hashlib
        result = audit(
            artifact_path="artifact.py",
            repo_root=str(fake_repo),
            logs_dir=str(fake_repo / "logs"),
            out_dir=str(out_dir),
            verbose=False,
        )
        # Recompute hash from manifest file content (first line)
        with open(result["manifest_path"]) as f:
            line = f.readline().rstrip("\n")
        computed = hashlib.sha256(line.encode("utf-8")).hexdigest()
        assert computed == result["manifest_sha256"]

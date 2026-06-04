# SAGCO OS — Bibliography & Knowledge Lineage

**Case:** C1602_CASE_001
**Generated:** 2026-06-04T23:55:42Z
**Author:** Domenic Garza · SNHU Capstone Portfolio

---

## Overview

This bibliography documents the full knowledge lineage of the SAGCO OS project:
- **25** functional bricks with traced citation sources
- **26** prior art entries (commercial, open source, academic, standards)
- **7** original inventions with field-observation origins

The core argument: each invention listed below was *built before* its prior art was
formally identified. SAGCO follows the Observation → Build → Prior Art model
(INV-005), not the Paper → Read → Build model traditional CS curricula assume.

---

## Section 1: Brick Citation Registry

| Brick | Name | Primary Sources |
|-------|------|-----------------|
| 001 | STATE_MESH | POSIX sh,JSON state files,CSV audit log,iSH Alpine |
| 002 | WAFER_ERU | Si-14 periodic table,Excel cell variance,ERU expected reality unit,awk float math |
| 003 | SHARED_STATE_READER | JSON single source truth,grep csv history,POSIX sh state mesh |
| 004 | ERU_AGGREGATOR | awk single pass stats,min max avg,health scoring pct,ERU variance loop |
| 005 | HALLUCHECK | Jaccard similarity,comm set math,BLEU score concept,term overlap detection |
| 006 | CELLRULE | Excel cell rules,EQ LTE GTE DELTA,ERU variance log,spreadsheet audit |
| 007 | REGISTRY | command registry CSV,POSIX path check,agent fleet manifest |
| 008 | GIDRA | grep signal classifier,RUNTIME ERU EVIDENCE INGEST,regex pattern scoring |
| 009 | PORTFOLIO_GENERATE | case study markdown,evidence chain,fuzz hit aggregation,hallucheck integration |
| 010 | RUN_ALPHA | pipeline orchestrator,POSIX sh trap,EXIT code logging,gmail antibody flag |
| 011 | HEALTH_CHECK | 10 node organ check,executable test,runtime log tail,state JSON append |
| 012 | DEPS_GRAPH | dependency CSV,ASCII tree render,orphan detection,OK vs MISSING status |
| 013 | GOVERNANCE_INGEST | SHA256 chain of custody,evidence register,content addressed hash |
| 014 | REPO_MAP | repo registry CSV,REPO SIGNAL CAPTURED,multi lang note log |
| 015 | PUBLIC_CHECK | curl HTTP probe,PUBLIC OK vs BROKEN,link antibody node |
| 016 | GMAIL_ANTIBODY | runaway PID kill,disk space guard,log quarantine 500 lines |
| 017 | PDF_FORENSICS | pdfinfo,pdftotext,sha256 evidence,metadata extraction |
| 018 | SCHEDULER | cron POSIX,timestamp delta,interval enforcement,agent loop |
| 034 | PUBLIC_BUILD | dark theme HTML,7 section proof page,GitHub Pages deploy,offline first |
| 035 | CALL_GUARDIAN | CaseGuard,Microsoft Presidio,Google Cloud DLP,spam call patterns,toll free risk scoring |
| 040 | PAGES_PACK | GitHub Pages,deploy package,README auto generate,DEPLOY NODE |
| 041 | PUBLIC_VERIFY | ERU 7 checks,GREEN pass fail,verify eru CSV,VERIFY NODE |
| 042 | REDACT_NODE | NIST PII standards,sed regex redaction,gonitro,CaseGuard,Microsoft Presidio,SHA256 pre post hash,hallucheck substance verify |
| 043 | LINEAGE_READER | Wing D,citation registry,prior art tracing,memory library |
| ARCH_001 | SOVEREIGNTY_ARCHITECTURE | Discord,Kubernetes,GitLens,OpenTelemetry,VectorDB,HMAC gateway,Java21,RBAC |

## Section 2: Prior Art Registry

| Source | Type | URL | Notes |
|--------|------|-----|-------|
| CaseGuard | commercial | https://caseguard.com | AI-powered document redaction for legal/government |
| Microsoft_Presidio | open_source | https://github.com/microsoft/presidio | PII detection and anonymization framework |
| Google_Cloud_DLP | cloud | https://cloud.google.com/sensitive-data-protection | Enterprise DLP — text and image PII scanning |
| gonitro | commercial | https://www.gonitro.com | PDF productivity and redaction suite |
| NIST_PII_standards | standard | https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-122.pdf | NIST SP 800-122 — Guide to PII Protection |
| spam_call_patterns | pattern | internal | Toll-free prefix + urgency keyword patterns from field observation |
| Jaccard_similarity | academic | https://en.wikipedia.org/wiki/Jaccard_index | Set-intersection similarity metric for token overlap |
| BLEU_score_concept | academic | https://aclanthology.org/P02-1040.pdf | Bilingual Evaluation Understudy — n-gram precision scoring |
| comm_set_math | posix | https://pubs.opengroup.org/onlinepubs/9699919799/utilities/comm.html | POSIX comm utility for sorted-file set operations |
| Si14_periodic_table | reference | https://en.wikipedia.org/wiki/Silicon | Silicon element 14 — wafer metaphor for Excel cell matrix |
| awk_float_math | posix | https://pubs.opengroup.org/onlinepubs/9699919799/utilities/awk.html | POSIX awk BEGIN block for float arithmetic (no bc dependency) |
| SHA256_hash | standard | https://csrc.nist.gov/publications/detail/fips/180/4/final | FIPS 180-4 SHA-256 content-addressed hashing standard |
| iSH_Alpine | runtime | https://ish.app | iOS Alpine Linux shell — primary SAGCO field execution environment |
| POSIX_sh | standard | https://pubs.opengroup.org/onlinepubs/9699919799/ | POSIX.1-2017 shell standard — ensures multi-device portability |
| GitHub_Pages | platform | https://pages.github.com | Static site hosting from repo — SAGCO public proof deployment target |
| busybox_date | runtime | https://busybox.net | Minimal date utility available on Alpine/iSH without coreutils |
| USPTO_patent_search | reference | https://patents.google.com | Google Patents — prior art search for sovereign redaction positioning |
| arxiv_NLP | reference | https://arxiv.org | Preprint server — NLP/PII detection academic literature |
| Discord | platform | https://discord.com/developers/docs | Bot API + slash commands — command surface for team-scale DevOps |
| Kubernetes | platform | https://kubernetes.io | Container orchestration — production runtime for Sovereignty Architecture |
| GitLens | open_source | https://github.com/gitkraken/vscode-gitlens | Git supercharged — PR automation and repo intelligence layer |
| OpenTelemetry | standard | https://opentelemetry.io | Observability framework — traces |
| VectorDB_pgvector | open_source | https://github.com/pgvector/pgvector | PostgreSQL vector extension — AI agent knowledge base |
| HMAC_gateway | standard | https://datatracker.ietf.org/doc/html/rfc2104 | RFC 2104 HMAC — event gateway signature validation |
| Java21_virtual_threads | runtime | https://openjdk.org/jeps/444 | JEP 444 virtual threads — Java 21 workspace concurrency |
| RBAC_k8s | standard | https://kubernetes.io/docs/reference/access-authn-authz/rbac/ | K8s role-based access control — governance enforcement |

## Section 3: Original Inventions (CREATOR=DOM)

> These inventions originate from field observation, not academic reading.
> Prior art listed is *confirmatory*, not *causal*.

### INV-001 — Expected vs Actual Variance generalizes into a software engi

**Claim:** Expected vs Actual Variance generalizes into a software engineering observation framework

**Origin (field observation):** Industrial shutdown planning rope access field variance tracking insulation counts

**Confirmatory prior art:** Earned Value Management,Statistical Process Control,Six Sigma DPMO

**Creator:** DOM

---

### INV-002 — A single JSON file per case updated by multiple physical nod

**Claim:** A single JSON file per case updated by multiple physical nodes creates sovereign state without databases or cloud

**Origin (field observation):** Need to track iPad ZFold iSH simultaneously during field work no internet available

**Confirmatory prior art:** Event sourcing,CQRS,distributed state machines,CRDTs

**Creator:** DOM

---

### INV-003 — Term overlap between expected truth and actual output is a p

**Claim:** Term overlap between expected truth and actual output is a practical hallucination detector without ML

**Origin (field observation):** Noticing AI outputs sound right but miss key domain terms from original documents

**Confirmatory prior art:** Jaccard similarity,BLEU score,BERTScore,precision recall IR

**Creator:** DOM

---

### INV-004 — Every failure should create a defensive mechanism that preve

**Claim:** Every failure should create a defensive mechanism that prevents the same class of failure from recurring silently

**Origin (field observation):** Repeated debugging sessions where same class of error appeared no memory of previous fix

**Confirmatory prior art:** Chaos engineering,fault injection,defensive programming,circuit breaker pattern

**Creator:** DOM

---

### INV-005 — Engineering lineage flows Observation to Build to Prior Art 

**Claim:** Engineering lineage flows Observation to Build to Prior Art NOT Paper to Read to Build

**Origin (field observation):** Discovering SAGCO bricks were invented before their prior art was found backwards citation

**Confirmatory prior art:** Grounded theory methodology,field-first engineering,tacit knowledge Polanyi

**Creator:** DOM

---

### INV-006 — Private evidence must pass through redaction before becoming

**Claim:** Private evidence must pass through redaction before becoming public proof

**Origin (field observation):** IRS letters DAO filings EIN SSN on personal device need to prove work without exposing PII

**Confirmatory prior art:** NIST SP 800-122 PII guide,GDPR data minimization,HIPAA safe harbor de-identification

**Creator:** DOM

---

### INV-007 — A system that grades its own claims against its own evidence

**Claim:** A system that grades its own claims against its own evidence is more trustworthy than one that only asserts

**Origin (field observation):** Frustration that portfolios show final code not whether claims are actually proven

**Confirmatory prior art:** Formal verification,model checking,Hoare logic,audit trail standards

**Creator:** DOM

---

## Section 4: Brick Manifest (Self-Describing Registry)

| Brick | Purpose | Test Command | Success Signal |
|-------|---------|-------------|----------------|
| sagco-state | Write_node_status_to_shared_state_mesh | cat sagco_ish/shared_state/cases/C1602_CASE_001.json | last_node_field_present_in_JSON |
| sagco-wafer | ERU_variance_check_expected_vs_actual_numeric | tail -1 sagco_ish/wafer/logs/wafer_eru.csv | WAFER_GREEN_or_WAFER_VARIANCE_ALERT_in_last_row |
| sagco-hallucheck | Term_overlap_hallucination_detector_score_0-100_pct | tail -1 sagco_ish/hallucheck/logs/hallucheck_eru.csv | GREEN_or_HALLUCINATION_RISK_score_in_last_row |
| sagco-redact | Strip_PII_EIN_SSN_phone_email_log_per_pattern_count_SHA256_pre_post | cat sagco_ish/redact/logs/redact_audit.csv | REDACT_CLEAN_or_REDACT_PII_REMOVED_in_log_SHA256_in_governance |
| sagco-public-build | Generate_7-section_HTML_proof_page_from_live_state_auto_redact | ls -la sagco_ish/public/site/ | index.html_and_index_redacted.html_both_present |
| sagco-fleet-eru | Parse_Kubernetes_daemon_telemetry_compute_ERU_per_metric_detect_panics | cat sagco_ish/fleet/logs/fleet_report.txt | FLEET_ERU_GREEN_or_ALERT_score_in_report |
| sagco-claims-report | Score_each_claim_PROVEN_PARTIAL_UNPROVEN_via_evidence_checks | sagco_ish/claims/bin/sagco-claims-report | PROVEN_PARTIAL_UNPROVEN_lines_present_SAGCO_CLAIMS_REPORT_COMPLETE |
| sagco-commandments | Self_verifying_constitution_10_commandments_each_checks_own_evidence | sagco_ish/constitution/bin/sagco-commandments | 10/10_UPHELD_CONSTITUTION_EXEMPLARY |
| sagco-antibody | Archive_FAIL_LEARN_PATCH_VERIFY_cycle_permanently | sagco_ish/antibody/bin/sagco-antibody-search --list | ANTIBODY_ARCHIVED_in_output_archive_count_increases |
| sagco-portal-start | Launch_client_portal_router_8_service_routes_with_keyword_aliases | curl -s http://localhost:8080 | grep SAGCO | SAGCO_OS_Client_Command_Portal_in_response |


---

## References

All tools, frameworks, and standards referenced in this bibliography are
documented with URLs in Section 2. SAGCO is self-sovereign: all tools run
on personal devices (iPad, Z Fold, Raspberry Pi, iSH Alpine) with no
third-party API dependencies for core operations.

*Generated by `sagco-bibliography` — Brick 054 · SAGCO OS*
*Case: C1602_CASE_001 · 2026-06-04T23:55:42Z*

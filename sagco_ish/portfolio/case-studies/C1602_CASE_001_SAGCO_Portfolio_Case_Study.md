# SAGCO Portfolio Case Study: C1602_CASE_001
## Executive Summary
SAGCO is a lightweight, multi-node field software system running on iSH / mobile devices.
This case study documents a live workflow using shared state, evidence hashing, fuzz scanning, ERU variance tracking, and portfolio signal extraction.
## System Architecture
- Shared state mesh
- Gmail / PDF ingest
- Evidence registry
- ERU expected-vs-actual variance
- Portfolio GIDRA fuzz scanner
- Dashboard loop
## Current Case State
```json
{
  "case": "C1602_CASE_001",
  "last_node": "FUZZ_NODE",
  "status": "ACTIVE",
  "note": "bill_fuzz_hits_17",
  "updated": "2026-06-04T20:33:49Z"
}
```
## Portfolio Signals
```csv
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,221,RUNTIME_SIGNAL,export PATH= $SAGCO_BASE/bin:$SAGCO_BASE/agents/eru/bin:$SAGCO_BASE/shared_state/bin:$SAGCO_BASE/scheduler/bin:$SAGCO_BASE/analysis/bin:$SAGCO_BASE/dashboard/bin:$SAGCO_BASE/dispatcher/bin:$SAGCO_BASE/wafer/bin:$SAGCO_BASE/pdfscan/bin:$SAGCO_BASE/registry/bin:$PATH ,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,223,RUNTIME_SIGNAL,# sagco-loop: autonomous scheduler → analyze → dashboard cycle,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,227,ERU_SIGNAL,[ ! -f  $OUT  ] && echo  case cell label rule expected actual variance status timestamp  >  $OUT ,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,236,ERU_SIGNAL,[ ! -f  $OUT  ] && echo  case label expected_terms actual_terms matched missing extra score status timestamp  >  $OUT ,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,239,INGEST_SIGNAL,# SAGCO PDF FORENSIC EXTRACTOR v2,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,248,INGEST_SIGNAL,# usage: sagco-pdfscan PDF_PATH CASE_ID,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,251,PORTFOLIO_SIGNAL,# Usage: sagco-portfolio-fuzz <CASE_ID> <SEARCH_ROOT>,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,252,PORTFOLIO_SIGNAL,OUT= sagco_ish/portfolio/logs/portfolio_fuzz.csv ,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,253,PORTFOLIO_SIGNAL,mkdir -p sagco_ish/portfolio/logs,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,254,RUNTIME_SIGNAL,   workflow|compose|dashboard|runtime|Gmail|Dropbox|PDF|agent|command|register|case.study|portfolio|ERU|variance|expected|actual|evidence|hash|sha256  \,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,255,AGENT_SIGNAL,    /agent|command|register/             { print  AGENT_SIGNAL ;   exit },2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,256,PORTFOLIO_SIGNAL,    /case.study|portfolio/               { print  PORTFOLIO_SIGNAL ; exit },2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,257,ERU_SIGNAL,    /ERU|variance|expected|actual/       { print  ERU_SIGNAL ;     exit },2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,258,EVIDENCE_SIGNAL,    /evidence|hash|sha256/               { print  EVIDENCE_SIGNAL ; exit },2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,259,PORTFOLIO_SIGNAL,sagco_ish/shared_state/bin/sagco-state  $CASE   PORTFOLIO_GIDRA_NODE   ACTIVE   portfolio_fuzz_hits_$COUNT  2>/dev/null,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,261,AGENT_SIGNAL,# sagco-register: register a command in the mesh registry,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,262,AGENT_SIGNAL,# Usage: sagco-register <name> <path> <type>,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,264,AGENT_SIGNAL,    echo  case agent status timestamp  >  $LOG ,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,265,PORTFOLIO_SIGNAL,            demo|mission|regression|portfolio|palace),2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/source_truth/sagco_os_truth.txt,283,ERU_SIGNAL,echo  case label expected actual variance status timestamp  >  $OUT ,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/hallucheck/bin/sagco-hallucheck,11,ERU_SIGNAL,[ ! -f  $OUT  ] && echo  case label expected_terms actual_terms matched missing extra score status timestamp  >  $OUT ,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/excel/logs/cellrule_eru.csv,1,ERU_SIGNAL,case cell label rule expected actual variance status timestamp,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/excel/bin/sagco-cellrule,11,ERU_SIGNAL,[ ! -f  $OUT  ] && echo  case cell label rule expected actual variance status timestamp  >  $OUT ,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/core/env.sh,2,AGENT_SIGNAL,# SAGCO core environment — source this to get all agent bins on PATH,2026-06-04T20:33:48Z
C1602_CASE_001,sagco_ish/core/env.sh,5,RUNTIME_SIGNAL,export PATH= $SAGCO_BASE/bin:$SAGCO_BASE/agents/eru/bin:$SAGCO_BASE/shared_state/bin:$SAGCO_BASE/scheduler/bin:$SAGCO_BASE/analysis/bin:$SAGCO_BASE/dashboard/bin:$SAGCO_BASE/dispatcher/bin:$SAGCO_BASE/wafer/bin:$SAGCO_BASE/pdfscan/bin:$SAGCO_BASE/registry/bin:$PATH ,2026-06-04T20:33:48Z
```
## Evidence Registry
```csv
NO_EVIDENCE_LOG
```
## ERU / Wafer Variance
```csv
case,label,expected,actual,variance,status,timestamp
C1602_CASE_001,VLV_001_EAST_PIPE,108,106,-2,WAFER_GREEN,2026-06-04T19:49:47Z
C1602_CASE_001,ISO_PROGRESS_COUNT,54,12,-42,WAFER_VARIANCE_ALERT,2026-06-04T19:49:47Z
C1602_CASE_001,WEIGHT_PROGRESS_UNITS,31,15,-16,WAFER_VARIANCE_ALERT,2026-06-04T19:49:47Z
```
## Software Engineering Value
This project demonstrates:
- Automation
- Logging
- Command registry design
- Evidence chain-of-custody
- Multi-agent orchestration
- Field-data capture
- Expected vs actual validation
## Status
SAGCO_PORTFOLIO_CASE_STUDY_GENERATED

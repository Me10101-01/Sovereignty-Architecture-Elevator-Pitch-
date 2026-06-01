# SAGCO Circuit Ledger — Schema Documentation
## data_engineering/sagco_circuit.db
## License: SSL-1.0 — Strategickhaos DAO LLC

---

## Tables

### `sagco_circuit` — EUR probe log
Each row = one Expected/Actual/Variance probe

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto increment |
| stamp | TEXT | YYYYMMDD_HHMMSS |
| session | TEXT | e.g. sagco-rust-compiler-archive |
| command | TEXT | Probe command run |
| expected | TEXT | What should happen |
| actual | TEXT | What actually happened (first line) |
| exit_code | INTEGER | Shell exit code |
| antibody | TEXT | Immune response type |
| trajectory | TEXT | stabilized/adaptation/evolution/mutation |
| variance | INTEGER | 0=at spec, 1=deviation |
| score | TEXT | PASS/WARN/FAIL/ADAPT/EVOLVE |
| sha256 | TEXT | Report SHA if applicable |
| notes | TEXT | Free text |

### `sagco_past_chain` — Memory compiler fingerprints

| Column | Type | Description |
|--------|------|-------------|
| source_file | TEXT | Input document |
| tokens | INTEGER | Token count |
| edges | INTEGER | Edge count (tokens-1) |
| fingerprint | TEXT UNIQUE | 64-bit hex fingerprint |

### `sagco_flametoken` — String extraction log

| Column | Type | Description |
|--------|------|-------------|
| token | TEXT | Extracted string |
| source | TEXT | strings/llvm-strings/ghidra |
| binary_sha | TEXT | SHA256 of analyzed binary |

### `sagco_maturity` — Maturity score history

| Column | Type | Description |
|--------|------|-------------|
| prototype_score | INTEGER | 0-100 |
| validation_score | INTEGER | 0-100 |
| audit_score | INTEGER | 0-100 |
| analysis_score | INTEGER | 0-100 |
| evidence_score | INTEGER | 0-100 |
| production_score | INTEGER | 0-100 |
| overall_score | INTEGER | average of above |
| flametoken_count | INTEGER | FlameTokens extracted |

### `sagco_build` — Cargo build events

| Column | Type | Description |
|--------|------|-------------|
| binary_name | TEXT | Binary filename |
| binary_size | INTEGER | Size in bytes |
| binary_sha | TEXT | SHA256 of binary |
| build_time | REAL | Seconds |
| mainrs_lines | INTEGER | Lines in main.rs |

### `sagco_archive` — SHA256-sealed artifacts

| Column | Type | Description |
|--------|------|-------------|
| filename | TEXT UNIQUE | Archive filename |
| size_bytes | INTEGER | File size |
| sha256 | TEXT | SHA256 hash |
| artifact_type | TEXT | tarball/report/binary |

---

## Views (Marts)

| View | Purpose |
|------|---------|
| `mart_session_pass_rate` | Pass/fail counts per session |
| `mart_antibody_freq` | Most common antibody types |
| `mart_past_summary` | Token totals per session |
| `mart_maturity_trend` | Maturity scores over time with grade |

---

## Useful Queries

```sql
-- Current maturity grade
SELECT overall_score, maturity_grade FROM mart_maturity_trend LIMIT 1;

-- All FAIL/ADAPT probes
SELECT command, antibody, trajectory, actual
FROM sagco_circuit
WHERE score IN ('FAIL','ADAPT')
ORDER BY stamp DESC;

-- FlameToken count by session
SELECT session, COUNT(*) as tokens FROM sagco_flametoken GROUP BY session;

-- PAST chain totals
SELECT * FROM mart_past_summary;

-- Latest Darwin run
SELECT pass_count, fail_count, darwin_dna FROM sagco_darwin_run ORDER BY stamp DESC LIMIT 1;
```

---

## Install (Termux)

```sh
pkg install sqlite
sqlite3 data_engineering/sagco_circuit.db \
  < data_engineering/sql/001_sagco_circuit_ledger.sql
bash data_engineering/etl/sagco_circuit_etl.sh
```

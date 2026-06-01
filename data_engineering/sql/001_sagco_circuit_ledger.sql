-- SAGCO Circuit Ledger — SQLite schema v1
-- Entity: Strategickhaos DAO LLC | License: SSL-1.0
-- Run: sqlite3 data_engineering/sagco_circuit.db < data_engineering/sql/001_sagco_circuit_ledger.sql

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ── core circuit table ───────────────────────────────────────────────────────
-- Each row = one probe in the EUR variance engine
CREATE TABLE IF NOT EXISTS sagco_circuit (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    stamp       TEXT    NOT NULL DEFAULT (strftime('%Y%m%d_%H%M%S', 'now')),
    session     TEXT,                       -- e.g. sagco-rust-compiler-archive
    command     TEXT    NOT NULL,           -- e.g. "sagco past"
    expected    TEXT    NOT NULL,           -- e.g. "SAGCO_PAST_PASS"
    actual      TEXT,                       -- raw captured output (first line)
    exit_code   INTEGER DEFAULT 0,
    antibody    TEXT    NOT NULL,           -- PASS_IMMUNITY | PATH_DISCOVERY | ...
    trajectory  TEXT    NOT NULL,           -- stabilized | adaptation | evolution | mutation
    variance    INTEGER DEFAULT 0,          -- 0 = at spec, +1 = deviation
    score       TEXT    NOT NULL,           -- PASS | WARN | FAIL | ADAPT | EVOLVE
    sha256      TEXT,                       -- sha256 of report if applicable
    notes       TEXT
);

-- ── PAST memory chain ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sagco_past_chain (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    stamp       TEXT    NOT NULL DEFAULT (strftime('%Y%m%d_%H%M%S', 'now')),
    session     TEXT,
    source_file TEXT    NOT NULL,
    tokens      INTEGER NOT NULL,
    edges       INTEGER NOT NULL,
    fingerprint TEXT    NOT NULL UNIQUE,
    sha256      TEXT,
    notes       TEXT
);

-- ── FlameToken log ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sagco_flametoken (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    stamp       TEXT    NOT NULL DEFAULT (strftime('%Y%m%d_%H%M%S', 'now')),
    session     TEXT,
    token       TEXT    NOT NULL,
    source      TEXT,                       -- "strings" | "llvm-strings" | "ghidra"
    binary_sha  TEXT,
    UNIQUE(token, session)
);

-- ── maturity scores ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sagco_maturity (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    stamp             TEXT    NOT NULL DEFAULT (strftime('%Y%m%d_%H%M%S', 'now')),
    session           TEXT,
    prototype_score   INTEGER,
    validation_score  INTEGER,
    audit_score       INTEGER,
    analysis_score    INTEGER,
    evidence_score    INTEGER,
    production_score  INTEGER,
    overall_score     INTEGER,
    flametoken_count  INTEGER,
    command_dna       TEXT,
    trajectory        TEXT,
    notes             TEXT
);

-- ── build events ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sagco_build (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    stamp       TEXT    NOT NULL DEFAULT (strftime('%Y%m%d_%H%M%S', 'now')),
    session     TEXT,
    profile     TEXT    DEFAULT 'release',
    binary_name TEXT    NOT NULL,
    binary_size INTEGER,                    -- bytes
    binary_sha  TEXT,
    build_time  REAL,                       -- seconds
    success     INTEGER DEFAULT 1,
    mainrs_lines INTEGER,
    notes       TEXT
);

-- ── archive seals ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sagco_archive (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    stamp       TEXT    NOT NULL DEFAULT (strftime('%Y%m%d_%H%M%S', 'now')),
    session     TEXT,
    filename    TEXT    NOT NULL UNIQUE,
    size_bytes  INTEGER,
    sha256      TEXT    NOT NULL,
    artifact_type TEXT,                     -- tarball | report | binary
    notes       TEXT
);

-- ── darwin antibody runs ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sagco_darwin_run (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    stamp       TEXT    NOT NULL DEFAULT (strftime('%Y%m%d_%H%M%S', 'now')),
    session     TEXT,
    pass_count  INTEGER DEFAULT 0,
    warn_count  INTEGER DEFAULT 0,
    fail_count  INTEGER DEFAULT 0,
    adapt_count INTEGER DEFAULT 0,
    evolve_count INTEGER DEFAULT 0,
    darwin_dna  TEXT,
    report_path TEXT
);

-- ── analytical views ─────────────────────────────────────────────────────────

-- mart: pass rate per session
CREATE VIEW IF NOT EXISTS mart_session_pass_rate AS
SELECT
    session,
    COUNT(*)                                          AS total_probes,
    SUM(CASE WHEN score = 'PASS' THEN 1 ELSE 0 END) AS pass_count,
    SUM(CASE WHEN score = 'FAIL' THEN 1 ELSE 0 END) AS fail_count,
    ROUND(
        100.0 * SUM(CASE WHEN score = 'PASS' THEN 1 ELSE 0 END) / COUNT(*), 1
    )                                                 AS pass_rate_pct,
    MAX(stamp)                                        AS last_run
FROM sagco_circuit
GROUP BY session;

-- mart: antibody frequency
CREATE VIEW IF NOT EXISTS mart_antibody_freq AS
SELECT
    antibody,
    trajectory,
    COUNT(*) AS occurrences,
    MAX(stamp) AS last_seen
FROM sagco_circuit
GROUP BY antibody, trajectory
ORDER BY occurrences DESC;

-- mart: PAST chain summary
CREATE VIEW IF NOT EXISTS mart_past_summary AS
SELECT
    session,
    COUNT(*)        AS document_count,
    SUM(tokens)     AS total_tokens,
    SUM(edges)      AS total_edges,
    COUNT(DISTINCT fingerprint) AS unique_fingerprints,
    MAX(stamp)      AS last_compiled
FROM sagco_past_chain
GROUP BY session;

-- mart: maturity trend
CREATE VIEW IF NOT EXISTS mart_maturity_trend AS
SELECT
    stamp,
    session,
    overall_score,
    prototype_score,
    validation_score,
    audit_score,
    analysis_score,
    evidence_score,
    production_score,
    flametoken_count,
    CASE
        WHEN overall_score >= 95 THEN 'S'
        WHEN overall_score >= 85 THEN 'A'
        WHEN overall_score >= 70 THEN 'B'
        WHEN overall_score >= 55 THEN 'C'
        WHEN overall_score >= 40 THEN 'D'
        ELSE 'F'
    END AS maturity_grade
FROM sagco_maturity
ORDER BY stamp DESC;

-- ── seed data — known good session ───────────────────────────────────────────
INSERT OR IGNORE INTO sagco_past_chain
    (session, source_file, tokens, edges, fingerprint, stamp)
VALUES
    ('sagco-rust-compiler-archive', 'README.md',                              1049, 1048, 'f3ffe8c9e81acfdf', '20260601_054800'),
    ('sagco-rust-compiler-archive', 'FLAMELANG_SPECIFICATION.md',             1178, 1177, '76ef539efbcac668', '20260601_054800'),
    ('sagco-rust-compiler-archive', 'EMPIRE_GENOME_v1.7.yaml',               1062, 1061, '07311699b684a150', '20260601_054800'),
    ('sagco-rust-compiler-archive', 'SWARM_DNA_v12.0-born-from-the-womb.yaml', 126, 125, 'b89e9963e0315f0d', '20260601_054800'),
    ('sagco-rust-compiler-archive', 'RATIO_EX_NIHILO_CONSTITUTION_V1.PDF',   2652, 2651, '92268810debbbe60', '20260601_054800');

INSERT OR IGNORE INTO sagco_archive
    (session, filename, sha256, artifact_type, stamp)
VALUES
    ('sagco-rust-compiler-archive',
     'SAGCO_COMMAND_DNA_20260531.tar.gz',
     '6b1924a45f5c68cb2b5a6a5e3cfc83bc2413521cee69817e8267ea59095491dc',
     'tarball', '20260601_000200'),
    ('sagco-rust-compiler-archive',
     'SAGCO_HEADLESS_VM_FUZZ_CASE_STUDY.tar.gz',
     '9d95f793179bd6d8b80bb2e035aa00ca46fccd58696855d52d0ef1476926206f',
     'tarball', '20260601_062600');

INSERT OR IGNORE INTO sagco_maturity
    (session, prototype_score, validation_score, audit_score,
     analysis_score, evidence_score, production_score, overall_score,
     flametoken_count, command_dna, trajectory, stamp)
VALUES
    ('sagco-rust-compiler-archive',
     100, 100, 100, 85, 90, 30, 84,
     324, 'a364ca9f90356c85',
     'EVOLUTION_WITH_PLATFORM_SPECIALIZATION',
     '20260601_063500');

-- verify
SELECT 'SAGCO_CIRCUIT_LEDGER_INITIALIZED' AS status;
SELECT COUNT(*) AS past_chain_seeds FROM sagco_past_chain;
SELECT COUNT(*) AS archive_seeds    FROM sagco_archive;
SELECT maturity_grade, overall_score FROM mart_maturity_trend LIMIT 1;

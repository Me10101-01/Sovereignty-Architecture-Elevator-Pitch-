-- SAGCO Claims + Verdicts — PostgreSQL seed
-- Compatible with Neon Serverless PostgreSQL (strategickhaos-core project)
-- Run: psql $DATABASE_URL -f dashboards/postgres_seed.sql

-- ─────────────────────────────────────────────
-- SCHEMA
-- ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS sagco_claims (
    id              TEXT        PRIMARY KEY,
    text            TEXT        NOT NULL,
    project         TEXT,
    category        TEXT,
    status          TEXT        NOT NULL DEFAULT 'OPEN',
    verdict         TEXT,
    coverage_pct    NUMERIC(6,2),
    notes           TEXT,
    missing_link    TEXT,
    antibody        TEXT,
    created_at      DATE,
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sagco_evidence (
    id          SERIAL      PRIMARY KEY,
    claim_id    TEXT        NOT NULL REFERENCES sagco_claims(id) ON DELETE CASCADE,
    text        TEXT        NOT NULL,
    source      TEXT,
    present     BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sagco_gaps (
    id          SERIAL  PRIMARY KEY,
    claim_id    TEXT    NOT NULL REFERENCES sagco_claims(id) ON DELETE CASCADE,
    gap_text    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS sagco_verdicts (
    id          SERIAL      PRIMARY KEY,
    claim_id    TEXT        NOT NULL REFERENCES sagco_claims(id),
    verdict     TEXT        NOT NULL,
    coverage    NUMERIC(6,2),
    seal        TEXT,
    rendered_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sagco_burnrate (
    id              SERIAL      PRIMARY KEY,
    snapshot_at     TIMESTAMPTZ DEFAULT NOW(),
    claims_total    INT,
    claims_proven   INT,
    claims_promising INT,
    claims_unproven INT,
    claims_inflated INT,
    burnrate        NUMERIC(5,4),
    ev_per_claim    NUMERIC(8,4)
);

CREATE TABLE IF NOT EXISTS sagco_missing_links (
    id              TEXT    PRIMARY KEY,
    description     TEXT    NOT NULL,
    blocks_claim    TEXT    REFERENCES sagco_claims(id),
    status          TEXT    NOT NULL DEFAULT 'OPEN',
    created_at      DATE,
    closed_at       DATE
);


-- ─────────────────────────────────────────────
-- SEED DATA — Claims
-- ─────────────────────────────────────────────

INSERT INTO sagco_claims (id, text, project, category, status, verdict, coverage_pct, created_at)
VALUES
  ('SAGCO-GRAPH-001',      'The SAGCO knowledge graph exceeds the value of any single component.',     'sagco-missing-links',   'architecture',        'PROVEN',    'PROVEN',    250.0, '2025-01-01'),
  ('RENKO-VAL-001',        'SAGCO / Renko project is worth $55,000+ in market value.',                 'sagco-node-renko',      'valuation',           'INFLATED',  'INFLATED',    0.0, '2025-01-01'),
  ('RENKO-PORTFOLIO-001',  'Renko strategies improve risk-adjusted returns vs. raw candle trading.',   'sagco-node-renko',      'trading_strategy',    'PROVEN',    'PROVEN',    100.0, '2025-01-01'),
  ('ERU-FOUNDATIONAL-001', 'ERU is the universal training format for all SAGCO components.',           'sagco-true',            'methodology',         'PROVEN',    'PROVEN',    100.0, '2025-01-01'),
  ('CHESS-STACK-001',      'The chess stack 640-node grid forms a closed loop — QED proof.',           'sagco-chess-stack',     'computation',         'PROVEN',    'PROVEN',    100.0, '2025-01-01'),
  ('HP-NODE-001',          'HP AMD node is reachable and operational as a sovereign compute node.',    'sagco-node-hp',         'infrastructure',      'PROMISING', 'PROMISING',  75.0, '2025-01-01'),
  ('TRADE-SIM-001',        'Dividend Capture and Renko Trend Following produce positive EV.',          'sagco-trade-simulator', 'trading_strategy',    'PROMISING', 'PROMISING',  50.0, '2025-01-01'),
  ('TRADE-SIM-002',        'Renko Mean Reversion is a viable strategy at WR=48%.',                    'sagco-trade-simulator', 'trading_strategy',    'INFLATED',  'INFLATED',    0.0, '2025-01-01'),
  ('RENKO-SIGNAL-001',     'Renko bricks reduce false reversals by ≥20% vs raw candles on AAPL.',    'sagco-node-renko',      'signal_quality',      'OPEN',      NULL,           0.0, '2025-01-15')
ON CONFLICT (id) DO UPDATE
  SET verdict = EXCLUDED.verdict,
      coverage_pct = EXCLUDED.coverage_pct,
      updated_at = NOW();


-- ─────────────────────────────────────────────
-- SEED DATA — Evidence
-- ─────────────────────────────────────────────

INSERT INTO sagco_evidence (claim_id, text, source, present) VALUES
  ('SAGCO-GRAPH-001', 'Renko trading system',          'sagco-node-renko brick',                             TRUE),
  ('SAGCO-GRAPH-001', 'FlameLang VM',                  'lexer→parser→AST→IR→compiler→bytecode→VM',           TRUE),
  ('SAGCO-GRAPH-001', 'ERU truth compiler',            'Claim→Expected→Actual→Variance→Verdict',             TRUE),
  ('SAGCO-GRAPH-001', 'KHAOS 72-element registry',     '7 archangels, Primameria calendar, Maat',            TRUE),
  ('SAGCO-GRAPH-001', 'Chess Stack 640-node grid',     '62/62 tests, loop closer QED',                       TRUE),
  ('SAGCO-GRAPH-001', 'SAGCO brick registry',          '11 bricks, topo sort, dep tree',                     TRUE),
  ('SAGCO-GRAPH-001', 'EVM + Excel dashboards',        'sagco-sync, rust_xlsxwriter',                        TRUE),
  ('SAGCO-GRAPH-001', 'Neon PostgreSQL',               'strategickhaos-core project',                        TRUE),
  ('SAGCO-GRAPH-001', 'Trade simulator',               '100 fake trades, AB-OVERFIT-001',                    TRUE),
  ('SAGCO-GRAPH-001', 'HP sovereign node',             'AMD 740M, Ollama, Docker, WSL2',                     TRUE);


-- ─────────────────────────────────────────────
-- SEED DATA — Gaps
-- ─────────────────────────────────────────────

INSERT INTO sagco_gaps (claim_id, gap_text) VALUES
  ('RENKO-VAL-001',    'Market transaction at or above stated value'),
  ('RENKO-VAL-001',    'Comparable sales of similar trading systems at $55k+'),
  ('RENKO-VAL-001',    'Recurring revenue from deployed system'),
  ('RENKO-VAL-001',    'Institutional buyer due diligence confirmation'),
  ('TRADE-SIM-002',    'Win Rate 48% < 50% threshold for viability'),
  ('TRADE-SIM-002',    'EV = -$11.23 per trade — negative expected value'),
  ('TRADE-SIM-002',    'Profit Factor 0.76 < 1.0'),
  ('RENKO-SIGNAL-001', 'AAPL daily OHLC dataset loaded and processed'),
  ('RENKO-SIGNAL-001', 'Renko brick generator applied (ATR brick size)'),
  ('RENKO-SIGNAL-001', 'False reversal count on raw candles measured'),
  ('RENKO-SIGNAL-001', 'False reversal count on Renko bricks measured'),
  ('RENKO-SIGNAL-001', 'Reduction ≥ 20% confirmed');


-- ─────────────────────────────────────────────
-- SEED DATA — Missing Links
-- ─────────────────────────────────────────────

INSERT INTO sagco_missing_links (id, description, blocks_claim, status, created_at)
VALUES
  ('ML-GRAPH-001',   'kg_builder live Neo4j connection — graph not persisted',    'SAGCO-GRAPH-001',   'OPEN', '2025-01-15'),
  ('ML-PROBE-001',   'sagco node hp probe — live verification of HP node',         'HP-NODE-001',       'OPEN', '2025-01-15'),
  ('ML-DATASET-001', 'One real dataset through full ERU loop end-to-end',          'RENKO-SIGNAL-001',  'OPEN', '2025-01-15')
ON CONFLICT (id) DO NOTHING;


-- ─────────────────────────────────────────────
-- VIEWS
-- ─────────────────────────────────────────────

CREATE OR REPLACE VIEW sagco_burnrate_view AS
SELECT
    COUNT(*)                                    AS claims_total,
    COUNT(*) FILTER (WHERE verdict = 'PROVEN')    AS proven,
    COUNT(*) FILTER (WHERE verdict = 'PROMISING') AS promising,
    COUNT(*) FILTER (WHERE verdict = 'UNPROVEN')  AS unproven,
    COUNT(*) FILTER (WHERE verdict = 'INFLATED')  AS inflated,
    ROUND(
        COUNT(*) FILTER (WHERE verdict = 'PROVEN')::NUMERIC / NULLIF(COUNT(*), 0) * 100, 1
    )                                           AS burnrate_pct,
    ROUND((
        COUNT(*) FILTER (WHERE verdict = 'PROVEN')    * 1.0
      + COUNT(*) FILTER (WHERE verdict = 'PROMISING') * 0.5
      + COUNT(*) FILTER (WHERE verdict = 'UNPROVEN')  * 0.1
      - COUNT(*) FILTER (WHERE verdict = 'INFLATED')  * 0.5
    ) / NULLIF(COUNT(*), 0), 3)                AS ev_per_claim
FROM sagco_claims
WHERE verdict IS NOT NULL;

-- Quick health check
SELECT
    verdict,
    COUNT(*) AS count,
    ROUND(AVG(coverage_pct), 1) AS avg_coverage
FROM sagco_claims
GROUP BY verdict
ORDER BY count DESC;

-- SAGCO-OS Evidence Engineering Schema
-- License: SSL-1.0 — Strategickhaos DAO LLC
-- EIN: 39-2900295 | SAGCO_COMMAND_DNA=a364ca9f90356c85
--
-- 8-Sector Map (matches Sovereignty Architecture diagram):
--   1=Observe   2=Tokenize  3=Parse    4=Classify
--   5=Store     6=Query     7=Verify   8=Evolve
-- This schema IS sectors 5-8: Store / Query / Verify / Evolve
-- ----------------------------------------------------------------

-- Sector 5: STORE — every sealed artifact the VM or sagco-evidence writes
CREATE TABLE IF NOT EXISTS sagco_seals (
    id              BIGSERIAL PRIMARY KEY,
    target          TEXT        NOT NULL,
    sha256          TEXT        NOT NULL,
    artifact_path   TEXT        NOT NULL,
    dna             TEXT        NOT NULL DEFAULT 'a364ca9f90356c85',
    sealed_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_seals_target    ON sagco_seals(target);
CREATE INDEX IF NOT EXISTS idx_seals_sha256    ON sagco_seals(sha256);
CREATE INDEX IF NOT EXISTS idx_seals_sealed_at ON sagco_seals(sealed_at DESC);

-- Sector 5: STORE — one row per pipeline execution (chain_hash is the integrity fingerprint)
CREATE TABLE IF NOT EXISTS sagco_evidence_chains (
    id              BIGSERIAL PRIMARY KEY,
    chain_hash      TEXT        NOT NULL,
    reports_dir     TEXT,
    tokens_dir      TEXT,
    total_artifacts INTEGER     NOT NULL DEFAULT 0,
    dna             TEXT        NOT NULL DEFAULT 'a364ca9f90356c85',
    executed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_chains_hash ON sagco_evidence_chains(chain_hash);

-- Sector 4: CLASSIFY — every antibody event that fired across all tools
CREATE TABLE IF NOT EXISTS sagco_antibody_events (
    id              BIGSERIAL PRIMARY KEY,
    antibody_name   TEXT        NOT NULL,   -- e.g. MISSING_SEAL_ARTIFACT_ANTIBODY
    variant         TEXT        NOT NULL,   -- PathDiscovery | EmptyPayload | CreepAlert | etc.
    message         TEXT,
    target          TEXT,                   -- artifact implicated (if any)
    tool_source     TEXT,                   -- sagco-evidence | sagco-core | sagco-sentinel
    dna             TEXT        NOT NULL DEFAULT 'a364ca9f90356c85',
    fired_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_antibody_variant  ON sagco_antibody_events(variant);
CREATE INDEX IF NOT EXISTS idx_antibody_fired_at ON sagco_antibody_events(fired_at DESC);

-- Sector 2: TOKENIZE + Sector 1: OBSERVE — knowledge-graph nodes (one row per artifact file)
CREATE TABLE IF NOT EXISTS sagco_topology_nodes (
    id              BIGSERIAL PRIMARY KEY,
    node_id         TEXT        NOT NULL,   -- "node_0", "node_1", ...
    label           TEXT        NOT NULL,   -- human-readable artifact label
    anchors         TEXT[]      NOT NULL DEFAULT '{}',
    sha256          TEXT,
    tokens_file     TEXT,                   -- source *.tokens.txt path
    dna             TEXT        NOT NULL DEFAULT 'a364ca9f90356c85',
    indexed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_topology_node_id ON sagco_topology_nodes(node_id);
CREATE INDEX IF NOT EXISTS idx_topology_label ON sagco_topology_nodes(label);

-- Sector 3: PARSE — co-occurrence edges between knowledge-graph nodes
CREATE TABLE IF NOT EXISTS sagco_topology_edges (
    id              BIGSERIAL PRIMARY KEY,
    from_node_id    TEXT        NOT NULL REFERENCES sagco_topology_nodes(node_id) ON DELETE CASCADE,
    to_node_id      TEXT        NOT NULL REFERENCES sagco_topology_nodes(node_id) ON DELETE CASCADE,
    weight          INTEGER     NOT NULL DEFAULT 0,
    dna             TEXT        NOT NULL DEFAULT 'a364ca9f90356c85',
    indexed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(from_node_id, to_node_id)
);
CREATE INDEX IF NOT EXISTS idx_edges_weight ON sagco_topology_edges(weight DESC);

-- Sector 7: VERIFY — every CreepAlert the SentinelDaemon reports
CREATE TABLE IF NOT EXISTS sagco_sentinel_events (
    id              BIGSERIAL PRIMARY KEY,
    alert_type      TEXT        NOT NULL,   -- ArtifactMissing | HashTampered | DnaMutated | RealityHolds
    target          TEXT        NOT NULL,
    artifact_path   TEXT,
    recorded_sha256 TEXT,
    actual_sha256   TEXT,
    message         TEXT,
    dna             TEXT        NOT NULL DEFAULT 'a364ca9f90356c85',
    detected_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sentinel_alert_type  ON sagco_sentinel_events(alert_type);
CREATE INDEX IF NOT EXISTS idx_sentinel_detected_at ON sagco_sentinel_events(detected_at DESC);

-- Sector 8: EVOLVE — token-frequency ledger for recurring doctrine terms
CREATE TABLE IF NOT EXISTS sagco_token_frequencies (
    id              BIGSERIAL PRIMARY KEY,
    token           TEXT        NOT NULL,
    frequency       INTEGER     NOT NULL DEFAULT 0,
    source_file     TEXT,
    is_anchor       BOOLEAN     NOT NULL DEFAULT FALSE,
    dna             TEXT        NOT NULL DEFAULT 'a364ca9f90356c85',
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_tokens_token    ON sagco_token_frequencies(token);
CREATE INDEX IF NOT EXISTS idx_tokens_is_anchor ON sagco_token_frequencies(is_anchor);
CREATE INDEX IF NOT EXISTS idx_tokens_freq      ON sagco_token_frequencies(frequency DESC);

-- Convenience view: latest seal per target
CREATE OR REPLACE VIEW sagco_latest_seals AS
    SELECT DISTINCT ON (target)
        id, target, sha256, artifact_path, dna, sealed_at
    FROM sagco_seals
    ORDER BY target, sealed_at DESC;

-- Convenience view: all active CreepAlerts (non-RealityHolds) in last 24h
CREATE OR REPLACE VIEW sagco_active_alerts AS
    SELECT id, alert_type, target, artifact_path, recorded_sha256, actual_sha256, message, detected_at
    FROM sagco_sentinel_events
    WHERE alert_type != 'RealityHolds'
      AND detected_at > NOW() - INTERVAL '24 hours'
    ORDER BY detected_at DESC;

COMMENT ON TABLE sagco_seals           IS 'Sector 5 — every sealed artifact (SHA256 ledger)';
COMMENT ON TABLE sagco_evidence_chains IS 'Sector 5 — chain hash per execution run';
COMMENT ON TABLE sagco_antibody_events IS 'Sector 4 — classify: antibody fire log';
COMMENT ON TABLE sagco_topology_nodes  IS 'Sectors 1+2 — observe/tokenize: knowledge graph nodes';
COMMENT ON TABLE sagco_topology_edges  IS 'Sector 3 — parse: co-occurrence edge weights';
COMMENT ON TABLE sagco_sentinel_events IS 'Sector 7 — verify: CreepAlert history';
COMMENT ON TABLE sagco_token_frequencies IS 'Sector 8 — evolve: doctrine token ledger';

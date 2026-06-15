// SAGCO Knowledge Graph — Neo4j Cypher Queries
// Run against a Neo4j 5.x instance with the sagco.cypher schema loaded

// ─────────────────────────────────────────────
// SECTION 1: SCHEMA CREATION
// ─────────────────────────────────────────────

// Constraints
CREATE CONSTRAINT brick_id IF NOT EXISTS FOR (b:Brick) REQUIRE b.id IS UNIQUE;
CREATE CONSTRAINT claim_id IF NOT EXISTS FOR (c:Claim) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT antibody_id IF NOT EXISTS FOR (a:Antibody) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT missing_link_id IF NOT EXISTS FOR (m:MissingLink) REQUIRE m.id IS UNIQUE;

// Indexes for common lookups
CREATE INDEX brick_layer IF NOT EXISTS FOR (b:Brick) ON (b.layer);
CREATE INDEX claim_verdict IF NOT EXISTS FOR (c:Claim) ON (c.verdict);
CREATE INDEX claim_status IF NOT EXISTS FOR (c:Claim) ON (c.status);


// ─────────────────────────────────────────────
// SECTION 2: EXPLORATION QUERIES
// ─────────────────────────────────────────────

// Q1: All bricks with their layer and status
MATCH (b:Brick)
RETURN b.id AS id, b.name AS name, b.layer AS layer, b.status AS status
ORDER BY b.layer, b.name;

// Q2: All claims and their verdicts
MATCH (c:Claim)
RETURN c.id AS id, c.verdict AS verdict, c.coverage_pct AS coverage
ORDER BY c.verdict, c.coverage_pct DESC;

// Q3: PROVEN claims — what's been closed
MATCH (c:Claim {verdict: "PROVEN"})
RETURN c.id, c.text, c.coverage_pct
ORDER BY c.coverage_pct DESC;

// Q4: INFLATED claims — where antibodies fired
MATCH (c:Claim {verdict: "INFLATED"})-[:FIRES_ANTIBODY]->(a:Antibody)
RETURN c.id AS claim, c.text AS claim_text, a.id AS antibody, a.trigger AS why_inflated;

// Q5: Missing links — open gaps blocking claims
MATCH (m:MissingLink)-[:BLOCKS]->(c:Claim)
RETURN m.id AS missing_link, m.description AS what_is_missing, c.id AS blocks_claim, c.verdict AS current_verdict
ORDER BY m.id;

// Q6: Full dependency tree for a brick
MATCH path = (b:Brick {id: "sagco-missing-links"})-[:DEPENDS_ON*]->(dep:Brick)
RETURN [node IN nodes(path) | node.id] AS dependency_chain;

// Q7: BurnRate — proven / total across all claims
MATCH (c:Claim)
WITH count(c) AS total,
     count(CASE WHEN c.verdict = "PROVEN"    THEN 1 END) AS proven,
     count(CASE WHEN c.verdict = "PROMISING" THEN 1 END) AS promising,
     count(CASE WHEN c.verdict = "UNPROVEN"  THEN 1 END) AS unproven,
     count(CASE WHEN c.verdict = "INFLATED"  THEN 1 END) AS inflated
RETURN total, proven, promising, unproven, inflated,
       round(toFloat(proven) / total * 100, 1) AS burnrate_pct,
       round((proven * 1.0 + promising * 0.5 + unproven * 0.1 - inflated * 0.5) / total, 3) AS ev_per_claim;

// Q8: Which bricks make the most claims?
MATCH (b:Brick)-[:MAKES_CLAIM]->(c:Claim)
RETURN b.id AS brick, count(c) AS claim_count, collect(c.verdict) AS verdicts
ORDER BY claim_count DESC;

// Q9: Evidence chain for SAGCO-GRAPH-001
MATCH (c:Claim {id: "SAGCO-GRAPH-001"})-[:HAS_EVIDENCE]->(e:Evidence)
RETURN e.text AS evidence, e.source AS source, e.present AS confirmed
ORDER BY e.present DESC;

// Q10: Lineage path from raw data to verdict
MATCH path = (d:Dataset)-[:USED_BY]->(c:Claim)-[:HAS_VERDICT]->(v:Verdict)
RETURN [node IN nodes(path) | coalesce(node.id, node.text)] AS lineage_chain;


// ─────────────────────────────────────────────
// SECTION 3: GRAPH TRAVERSAL QUERIES
// ─────────────────────────────────────────────

// Q11: All nodes connected to a specific brick (1-hop neighborhood)
MATCH (b:Brick {id: "sagco-node-renko"})-[r]-(neighbor)
RETURN type(r) AS relationship, labels(neighbor) AS neighbor_type,
       coalesce(neighbor.id, neighbor.text) AS neighbor_id;

// Q12: Shortest path between two claims
MATCH path = shortestPath(
  (a:Claim {id: "SAGCO-GRAPH-001"})-[*]-(b:Claim {id: "RENKO-PORTFOLIO-001"})
)
RETURN [node IN nodes(path) | coalesce(node.id, node.text)] AS path_nodes,
       length(path) AS hops;

// Q13: All claims that share an antibody
MATCH (c1:Claim)-[:FIRES_ANTIBODY]->(a:Antibody)<-[:FIRES_ANTIBODY]-(c2:Claim)
WHERE c1.id < c2.id
RETURN c1.id, c2.id, a.id AS shared_antibody;

// Q14: Graph summary — node and edge counts
MATCH (n)
RETURN labels(n)[0] AS node_type, count(n) AS count
ORDER BY count DESC
UNION ALL
MATCH ()-[r]->()
RETURN type(r) AS node_type, count(r) AS count
ORDER BY count DESC;


// ─────────────────────────────────────────────
// SECTION 4: MUTATION QUERIES (use with care)
// ─────────────────────────────────────────────

// Q15: Upgrade a claim's verdict when new evidence arrives
// MATCH (c:Claim {id: "RENKO-SIGNAL-001"})
// SET c.verdict = "PROVEN", c.coverage_pct = 100.0, c.updated_at = datetime()
// RETURN c.id, c.verdict;

// Q16: Mark a missing link as closed
// MATCH (m:MissingLink {id: "ML-DATASET-001"})
// SET m.status = "CLOSED", m.closed_at = datetime(), m.closed_by = "eru-core v0.1.0"
// RETURN m.id, m.status;

// Q17: Add new evidence to an existing claim
// MATCH (c:Claim {id: "HP-NODE-001"})
// CREATE (e:Evidence {
//   text: "Live Ollama probe returned model list: llama3, mistral",
//   source: "sagco node hp probe — 2025-01-20 14:32 UTC",
//   present: true
// })
// CREATE (c)-[:HAS_EVIDENCE]->(e)
// RETURN c.id, e.text;

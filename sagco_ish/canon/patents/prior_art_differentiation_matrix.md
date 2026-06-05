# SAGCO Prior Art Differentiation Matrix
## Canon Register — Compute Law enforced where marked

| Concept | Prior Art | Prior Art Strength | SAGCO Difference | Computes? | Status |
|---------|-----------|-------------------|------------------|-----------|--------|
| Offline-first system | Docker, k3s, NixOS, Tails OS | Very strong | Not the claim. SAGCO's novelty is NOT offline operation. | — | NOT NOVEL ALONE |
| Lineage tracking | Git, JIRA, knowledge graphs, Prov-O ontology | Strong | SAGCO lineage is bidirectional: error→brick AND brick→prior_art. Backwards flow (INV-005) is novel. | `sagco-lineage` exits 0 | PARTIAL |
| Living documentation | DDD/Martraire 2019, Doctest, literate programming | Moderate | SAGCO adds mandatory Compute Law gate — doc must run or get antibody. Docs that fail become errors in the ledger. | `sagco-compute-law` exits 0 | STRONGER |
| Symbolic compression | CDN Green/Petre 1996, DSL research | Strong | SAGCO adds **bidirectional enforcement**: symbols must carry Compute Test. CDN describes problems; SAGCO implements a solution. | `sagco-translate --list` exits 0 | INVESTIGATE |
| Agent orchestration | LangChain, Temporal, Prefect, Airflow | Very strong | Not the claim. SAGCO's orchestration is not novel. | — | NOT NOVEL ALONE |
| MIDI / audio observability | Auralisation research, sonification tools | Weak/rare | OPCODE→note mapping with key-mood from ERU tension ratio is novel combination. No prior art found for error-rate→musical-key. | `sagco-midi` exits 0 | EXPERIMENTAL |
| Translation Engine | No direct prior art found | Weak | **Story→Engineering→Compute Test triad as enforced registry** — not found in CDN, DDD, or knowledge graph literature. | `sagco-translate --lookup` exits 0 | RESEARCH TARGET |
| Adaptation Lineage | Chaos engineering, antibody pattern (Wing G) | Moderate | Measuring CREATION vs ADAPTATION weights over time as a system health metric is novel framing. | `sagco-evo` outputs weights | PARTIAL |
| Cross-device evidence transport | ngrok, Tailscale, mDNS | Moderate | Auto-replacing localhost in evidence artifacts + provenance logging in shared state mesh is specific combination. | `sagco-link-bridge` exits 0 | PARTIAL |
| Compute Law enforcement | Formal verification, Hoare logic, model checking | Strong (academic) | SAGCO applies this at the *documentation claim* level, not code level. Every English sentence that makes a claim must pass a terminal test. | `sagco-compute-law` exits 0 | NOVEL FRAMING |

---

## Honest Assessment

### Where prior art is too strong to claim novelty alone
- Offline operation
- Agent orchestration  
- Basic lineage tracking
- Living documentation (concept)

### Where the combination may be novel
- Compute Law applied to **documentation claims** (not code verification)
- Translation Engine triad as **enforced, queryable registry** (CDN has no enforcement mechanism)
- MIDI key derived from **ERU tension ratio** (error÷resolution as musical key)
- Backwards lineage: **Observation→Build→Prior Art** (INV-005, the opposite of normal)

### The single strongest sentence in the blueprint
> *Every symbolic term must maintain Story Name, Engineering Name, and Compute Test.*

This is novel because CDN (the closest prior art) describes the **problem** of
hidden dependencies and poor role-expressiveness but proposes no enforcement mechanism.
SAGCO proposes a **running, queryable registry** that enforces the triad in real time.
That is a specific, computable, implementable solution to a known CDN problem.

### Next research step before Patent v2
Before filing, establish whether any knowledge graph / ontology system
(Prov-O, Schema.org, OWL ontologies) already enforces something similar to
the Story→Engineering→Compute triad. If not found: that is the claim to file.

---

## Research Questions to Resolve

1. Does any existing system enforce a **three-layer naming constraint** (mythic / engineering / verifiable) on knowledge objects?
2. Does any existing observability system derive **musical key from error/resolution ratio** in real time?
3. Does any documentation system create **antibodies** (defensive artifacts) automatically when a claim fails its compute test?
4. Does any lineage system explicitly model **backwards discovery** (built before prior art found)?

If the answer to all four is no: that is the patent.

---

*Generated: 2026-06-05 | Author: Domenic Gabriel Garza | ORCID: 0000-0005-2996-3526*
*Status: CANON — Research document, pre-filing analysis*

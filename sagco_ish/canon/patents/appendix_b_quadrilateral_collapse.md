# SAGCO Patent Document: Appendix B
# Quadrilateral Collapse Detection and Scoring
## Canon Register | Brick 062 | Generated: 2026-06-05

> COMPUTE LAW CERTIFICATION: Every claim in this document has a corresponding
> compute test in sagco_ish/compute_law/logs/compute_law.csv.
> Claims without a passing test SHALL NOT enter this document.

---

## Problem Statement

Modern field engineering workflows routinely fragment across four traversal domains
simultaneously. A single task that nominally requires 3 tool transitions may consume
17 or more hops across devices, environments, tools, and context-reconstruction events.
No prior system measures this structural fragmentation in real time and feeds the
measurement into a self-regulating governance scheduler.

**The Gap:** Prior art (Gloria Mark, 2005; SPACE framework, Forsgren et al., 2021;
Cognitive Dimensions of Notations, Green & Petre, 1996) measures context-switching
cost in TIME (minutes lost, error rates, cognitive load scores). SAGCO measures it
in STRUCTURAL HOPS — the actual count of domain transitions required to complete a
task — and uses that count as a first-class input to the governance weight engine.

---

## The Four Traversal Domains ("Quadrilateral")

```
┌──────────────────────────────────────────────────────────────┐
│                   QUADRILATERAL COLLAPSE                     │
│                                                              │
│  Physical   ────  Device transitions                         │
│  (iPad → ZFold → Pi → desktop → cloud node)                 │
│                                                              │
│  Logical    ────  Environment shifts                         │
│  (iSH → Docker → WSL → K8s pod → cloud shell)               │
│                                                              │
│  Tool       ────  Problem-driven tool switches               │
│  (terminal → Obsidian → Working Copy → GitHub → ChatGPT)    │
│                                                              │
│  Temporal   ────  Context-reconstruction cost                │
│  (implicit in variance between expected and actual hops)     │
└──────────────────────────────────────────────────────────────┘
```

A **Collapse Event** occurs when actual traversal distance exceeds the expected
baseline for a given task type, creating a measurable variance that propagates
into the Weight Calculator.

---

## Scoring Formula

```
ACTUAL_HOPS = physical_hops + logical_hops + tool_hops

VARIANCE    = ACTUAL_HOPS - EXPECTED_BASELINE

COLLAPSE_SCORE:
  NOMINAL   variance ≤ 0    (within expected bounds)
  LOW       variance 1–5    (slight deviation, acceptable)
  MEDIUM    variance 6–10   (moderate fragmentation)
  HIGH      variance 11–20  (governance flag)
  CRITICAL  variance > 20   (consolidation required)

COLLAPSE_WEIGHT = min(VARIANCE × 2, 40)
```

**Signal Sources:**
- Physical hops: unique LAN IP addresses in `link_bridge.csv`
- Logical hops: unique state-mesh node types in `state_updates.csv`
- Tool hops: antibody archive entries ÷ 3 (each antibody = a problem-driven switch)

---

## Integration with Wing G Weight Calculator

The Collapse Weight is the seventh component of the governance weight formula:

```
TOTAL_WEIGHT =
  W_CREATION    (manifest + citations + inventions)
  + W_ADAPTATION  (antibodies × 8 + compute-law passes × 3)
  + W_DEPENDENCY  (dependent bricks × 6)
  + W_ERU         (per-brick GREEN signals × 4)
  + W_SURVIVAL    (compute-law COMPUTABLE × 2 + trial wins × 10)
  + W_NOVELTY     (translation + blueprint + prior-art matrix)
  + W_COLLAPSE    (workflow variance × 2, cap 40)
```

**Semantic meaning:** A brick that survives inside a CRITICAL-collapse environment
(high device fragmentation, many tool switches, 20+ state-mesh nodes) has proven
resilience under harder conditions than a brick that only ever ran in a clean
single-device workspace. Collapse weight reflects environmental difficulty survived.

---

## Compute Test (COMMANDMENT XIII Compliance)

```sh
# Test 1: sagco-collapse-score binary is executable
test -x sagco_ish/collapse/bin/sagco-collapse-score
# Expected: EXIT_0

# Test 2: scorer produces COLLAPSE_SCORE in output
sagco_ish/collapse/bin/sagco-collapse-score C1602_CASE_001 3
# Expected: SAGCO_COLLAPSE_SCORE_COMPLETE

# Test 3: collapse log is created
test -f sagco_ish/collapse/logs/collapse_scores.csv
# Expected: EXIT_0

# Test 4: sagco-weight picks up collapse variance from log
sagco_ish/governance_fleet/bin/sagco-weight sagco-evo C1602_CASE_001
# Expected: FULL_FLEET (collapse pushes core methodology bricks above 100)
```

---

## Prior Art Differentiation

| Prior Art | What It Measures | Gap |
|-----------|-----------------|-----|
| Gloria Mark (2005) — interruption research | Minutes lost per context switch | Time cost only; no structural traversal count; no governance integration |
| SPACE framework (Forsgren et al., 2021) | Flow state, satisfaction, performance, efficiency, collaboration | Surveys and logs; no real-time multi-device traversal distance |
| Cognitive Dimensions of Notations (Green & Petre, 1996) | Notation usability via 13 cognitive dimensions | Applied to notation systems, not to human-device-environment traversal |
| Context collapse in LLMs (Stanford ACE, 2025) | AI context window coherence in long agentic tasks | AI context only; not multi-device human engineering workflow fragmentation |
| SAGCO Quadrilateral Collapse Score (Brick 062) | Structural hop count across 4 domains → governance weight | **No prior art found combining structural fragmentation scoring with a self-regulating review scheduler** |

---

## Novelty Statement

The specific novel combination is:

1. Measuring workflow fragmentation as **structural traversal distance** (hop count)
   rather than time cost or productivity proxy
2. Deriving a **COLLAPSE_SCORE** from Expected vs Actual path variance (ERU-style)
3. Feeding COLLAPSE_WEIGHT directly into the **governance scheduler** (Wing G)
   that determines which review gates open (PEER / TECHNICAL / PATENT / FULL_FLEET)
4. Operating **sovereign and offline-first** — no cloud dependency for measurement
5. Recording **collapse events in Adaptation Lineage** (antibody archive) so the
   recovery bricks created in response to collapse contribute to brick weight

**Single-sentence claim:**
> A method for governing engineering review allocation by computing the structural
> traversal distance of a human operator's workflow across physical, logical, and tool
> domains, comparing it to an expected baseline, and using the resulting variance to
> weight a brick's governance tier.

---

## Field Evidence (Case C1602_CASE_001)

The system was designed and built across:
- iPad (iSH terminal)
- ZFold device
- Windows + WSL
- Docker fleet
- Kubernetes nodes
- Cloud shell (GitHub Actions context)
- Multiple note-taking and version control tools

First live scoring run (2026-06-05):
```
Expected baseline  :   3
Actual hops        :  34  (1 physical + 29 logical + 4 tool)
Variance           : +31
COLLAPSE_SCORE     : CRITICAL
COLLAPSE_WEIGHT    :  40  (cap reached)
```

This CRITICAL score is accurate and expected. It reflects 62 bricks built,
29+ state-mesh node types, 12 antibodies — across a genuine multi-device,
multi-session field engineering workflow. The system did not collapse.
The bricks survived. The score proves the point the patent makes.

---

## INV-008 Connection

The Collapse Scorer is a direct instantiation of INV-008 (Survival Rule):

> A system methodology becomes more trustworthy than any individual component
> when the rule governing component survival itself computes.

The collapse score is the rule governing **how hard it was to survive.**
If a brick computes in a CRITICAL collapse environment, its survival is worth more
than a brick that only ever ran in a clean workspace. That is INV-008 applied to
the governance scheduler.

---

*SAGCO_APPENDIX_B_COMPLETE*
*Quadrilateral Collapse Detection — Brick 062 · Wing G · SAGCO OS*

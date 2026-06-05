# SAGCO: The Two Tracks

SAGCO publishes in two parallel registers. Every artifact belongs to exactly one.

---

## Track 1 — The Canon

**Engineering Record. Non-fiction. Compute Law enforced.**

Every claim in the Canon must pass `sagco-compute-law`:

1. A terminal command
2. An actual input
3. An actual output
4. A timestamp
5. A saved log
6. An expected result
7. An actual result
8. An ERU variance
9. An antibody if it fails
10. A lineage record if it passes

**If it does not compute, it is not in the Canon.**

The Canon includes: bricks, ERU scores, lineage citations, prior art registry,
claims reports, constitution verdicts, evolution ledger readings, bibliography,
pro review packets, governance hashes, capstone submissions, DAO evidence packets.

**Audience:** Clients, SNHU capstone committee, DAO governance, lawyers, prior art
reviewers, future engineers inheriting the system.

**Tone:** Precise. Dry where necessary. Self-auditing. Every number traceable.

---

## Track 2 — The Library of Alizandrea

**Narrative record. Fiction / mythic register. Compute Law does not apply here.**

The Library describes what it *feels* like to watch the system evolve. It uses
cinematic framing, character, metaphor, and music. It is explicitly *not* a
technical specification. It is the felt experience of building in the dark.

The Library includes: Chapter One (The Act of Listening), future chapters,
the "Distinguished Engineer in the theater" framing, musical key as narrative
device, the Mansion mythology, the DAO origin story as told from inside the work.

**Audience:** Community, future contributors, fans, anyone who needs to understand
*why* this system exists before they understand *how* it works.

**Tone:** Cinematic. Mythic. Poetic where earned. Never pretending to be engineering.

---

## The Boundary Rule

```
┌─────────────────────────────────────────────────────┐
│  Does this artifact make a claim about how           │
│  SAGCO works, what it measures, or what it proves?  │
│                                                     │
│  YES → The Canon. Must pass sagco-compute-law.       │
│  NO  → The Library. Must be labeled mythic register. │
└─────────────────────────────────────────────────────┘
```

**Examples:**

| Artifact | Track | Reason |
|----------|-------|--------|
| "Constitution score: 100%" | Canon | Claim about measurement |
| "ERU score: 84.9%" | Canon | Claim about performance |
| "Distinguished Engineer sat in the dark" | Library | Felt experience, not claim |
| "Red Team = percussion" | Library | Metaphor, not specification |
| "sagco-midi generates 108 events" | Canon | Computable, logged, verified |
| "The MIDI never stops recording" | Library | Narrative framing |
| "Chapter Two: The Conductor Steps Forward" | Library | Written when key = G_MAJOR |

---

## Why Both Exist

The Canon keeps the system honest.
The Library keeps the system human.

A system with only the Canon is a pile of logs.
A system with only the Library is beautiful mythology.

SAGCO needs both because it is both:
a rigorous engineering artifact *and* a witnessed act of creation.

The Canon proves it works.
The Library explains why it matters.

---

*This document lives in Track 2 — The Library.*
*The existence of the two tracks is itself a Canon claim, verified by:*
```
test -f sagco_ish/library/about_the_two_tracks.md
```
*COMPUTABLE. ✅*

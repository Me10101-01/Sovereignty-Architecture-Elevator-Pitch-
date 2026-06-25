# BFT Delta — SAGCO vs SLAAC Trust Model

> "SLAAC trusts the router. SAGCO requires 2-of-3 BFT."

---

## The Core Claim

**SLAAC (Stateless Address Autoconfiguration, RFC 4862):**
A host receives its IPv6 address from whatever router sends a Router Advertisement.
No authentication. No verification. The host trusts the first router that answers.

**SAGCO BFT Model:**
No single node's claim is accepted without corroboration from at least 2 of 3
independent validators. Trust is computed, not assumed.

---

## Why This Matters for INV-198

INV-198 (Self-Auditing Filesystem-Native Message Bus) is a **recursive verification
architecture**. The novelty is not SHA-256, not JSONL logs, not PBFT — it is the
**composition**: the verifiers verify the verifiers.

SLAAC is the control group. It represents every system that trusts its environment
without proof. SAGCO represents the alternative: every claim earns its status through
a computed ERU ratio.

This is not theoretical. SAGCO OS already implements:
- PBFT consensus driver (sagco_sandbox_v5)
- Raft log replication
- Trinity BFT (3-of-5 variant)
- WireGuard for transport isolation
- RPKI ROA for route origin proof (pending MOVE 2/3)

---

## The Mathematical Delta

```
SLAAC trust model:
  T(claim) = 1 if router_advertisement_received else 0
  (binary, unverified, attacker-controllable)

SAGCO trust model:
  T(claim) = A / E   where:
    A = validators that corroborate the claim
    E = total validators polled (minimum 3)
  
  PROVEN   : T ≥ 1.0  (all validators agree)
  PROMISING: T ≥ 0.5  (majority agree)
  UNPROVEN : T ≥ 0.01 (weak evidence)
  INFLATED : T < 0.01 (no corroboration — reject)
```

---

## Routing Application

Without RPKI:
```
BGP_ANNOUNCEMENT("203.0.113.0/24") → accepted by all routers (SLAAC-equivalent)
Attacker announces same prefix → hijack succeeds
```

With RPKI ROA:
```
BGP_ANNOUNCEMENT("203.0.113.0/24", origin=AS399999)
  → validator_1: ROA match = TRUE
  → validator_2: ROA match = TRUE  
  → validator_3: ROA match = TRUE
  T(claim) = 3/3 = 1.0  [PROVEN]

Attacker announces same prefix, origin=EVIL_ASN:
  → validator_1: ROA mismatch = INVALID
  → verdict: INFLATED → reject
```

---

## The Invention Statement

The SAGCO architecture is the SLAAC→BFT transition applied universally —
not just to routing, but to file provenance, decision tracing, trade receipts,
and artifact history. Every layer of the stack computes trust rather than assuming it.

That universal application of recursive verification is the candidate invention
in INV-198, and it is not described in any prior art reference in
`sagco-archaeologist/registry/prior_art_db.yaml`.

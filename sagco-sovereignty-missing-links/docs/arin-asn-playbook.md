# ARIN ASN Playbook — MOVE 2

**Closes:** Network sovereignty gap (sagco-organism ML-ORGANISM-004 depends on this)
**Prerequisite for:** RPKI ROA creation (MOVE 3)
**Cost:** ~$350 year 1, $250/year thereafter

---

## Why an ASN?

Without an ASN, Strategickhaos DAO LLC cannot:
- Create RPKI Route Origin Authorizations (ROAs)
- Sign BGP announcements with cryptographic proof
- Operate independent routing (multihomed resilience)
- Prove route origin in the sovereignty chain

> This is the difference between a company that *uses* the internet
> and one that *is part of* the internet's routing infrastructure.

---

## The Three-Move Sequence

```
MOVE 1: GPG clearsign Athena          → artifact tamper-evidence
MOVE 2: ARIN Org ID + ASN request     → routing identity
MOVE 3: ARIN RPKI → ROA creation      → cryptographic route signing
```

These are not sequential — MOVE 1 can happen today (10 minutes).
MOVE 2 starts MOVE 3 (must have ASN before ROA).

---

## Execution Order for MOVE 2

1. `arin/org-id-checklist.md` — create Org ID (5 min, immediate)
2. `arin/asn-application.md` — submit ASN request (15 min + 5–10 day wait)
3. `arin/fee-schedule-2026.md` — pay fees (~$350 year 1)
4. Receive ASN → immediately wire it into:
   - `sagco-organism/sagco-brick.toml` `[sovereignty]` section
   - `PROVENANCE.yaml`
5. Proceed to MOVE 3 (rpki/)

---

## Justification Language (copy-paste ready)

For the ARIN form's "Justification" field:

> Strategickhaos DAO LLC operates a distributed sovereignty computing
> infrastructure requiring BGP routing independence for resilience across
> regional failures. The organization implements SAGCO OS (Self-Auditing
> Governance and Computation Organism), a mobile-native provenance substrate,
> and requires an ASN to implement RPKI ROA-based route origin validation per
> RFC 6482. We plan to establish multihomed connectivity within 12 months.

---

## ERU Impact

```
ML-ORGANISM-004: network/ssh.c + vpn.c not built
  Status: UNCOMPUTED → becomes COMPUTED once ASN assigned + network/vpn.c wired

AB-GPG-UNSIGNED-001: GPG provenance gap
  Status: OPEN → closes on MOVE 1 (gpg/clearsign-athena.sh)

RPKI ROA:
  Status: BLOCKED on ASN → unblocks on MOVE 2 completion
```

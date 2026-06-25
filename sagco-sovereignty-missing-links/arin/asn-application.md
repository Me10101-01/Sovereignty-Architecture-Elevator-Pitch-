# ARIN ASN Application — MOVE 2

**Entity:** Strategickhaos DAO LLC
**WY File:** 2025-001708194
**EIN:** 39-2900295
**Status:** UNCOMPUTED until application submitted

---

## What You're Applying For

An **Autonomous System Number (ASN)** from ARIN (American Registry for Internet Numbers).
An ASN is a globally unique identifier issued to organizations that operate their own
BGP routing infrastructure. It is the prerequisite for RPKI ROA creation (MOVE 3).

> "SLAAC trusts the router. SAGCO requires 2-of-3 BFT."
> — docs/bft-delta.md

---

## Eligibility Requirements (confirm all before applying)

- [ ] Multihomed network (connected to 2+ upstream ISPs)
      **OR** plan to multihome within 12 months (documented)
- [ ] Unique routing policy different from your upstream(s)
- [ ] Organization has a legal presence (LLC ✓)

**Note:** If you only have one upstream provider currently, ARIN will ask for
a documented plan to multihome. Prepare a 1-paragraph justification.
Example: "Strategickhaos DAO LLC operates a distributed sovereignty infrastructure
requiring independent BGP routing to achieve resilience across regional failures."

---

## Pre-Application Checklist

- [ ] Create ARIN Online account at https://account.arin.net/
- [ ] Create an **Org ID** for Strategickhaos DAO LLC (see org-id-checklist.md)
- [ ] Have your WY Articles of Organization ready (PDF)
- [ ] Have EIN 39-2900295 ready for tax verification
- [ ] Decide: **16-bit ASN** (legacy, scarce) vs **32-bit ASN** (modern, recommended)
      → Choose 32-bit unless your upstreams require 16-bit

---

## Application Steps

### Step 1: Log in to ARIN Online

```
https://account.arin.net/
```

### Step 2: Navigate to Requests → ASN Request

Select: **Request an ASN for a New Organization**
(or for existing Org ID if you already created one)

### Step 3: Fill out the ASN Request Form

| Field | Value |
|-------|-------|
| Organization Name | Strategickhaos DAO LLC |
| Organization Type | Commercial |
| Country | United States |
| State | Wyoming |
| Justification | See template below |
| IP Space Size | N/A for ASN-only request |
| Multihomed? | Yes (or "plan to within 12 months") |

### Justification Template

```
Strategickhaos DAO LLC operates a distributed sovereignty computing infrastructure
requiring BGP routing independence. The organization maintains SAGCO OS nodes across
multiple geographic regions and requires an ASN to implement RPKI ROA-based route
origin validation per RFC 6482. We are connected to / plan to connect to two or more
upstream providers within 12 months to achieve multihoming.
```

### Step 4: Pay the Fee

See fee-schedule-2026.md for current amounts.

### Step 5: Wait for Review

ARIN typical turnaround: **5–10 business days** for ASN requests.
Watch your registered email for:
- Request confirmation
- Additional documentation request
- ASN assignment notification

---

## After Approval

You will receive:
- Your ASN (e.g., `AS399999`)
- ARIN Org ID (e.g., `STKH-1`)
- Access to ARIN's RPKI interface

**Immediately after receiving your ASN:**
1. Record it in `sagco-organism/sagco-brick.toml` under `[sovereignty]`
2. Proceed to RPKI ROA creation (MOVE 3 — see rpki/ directory)

---

## Support

- ARIN Help Desk: +1.703.227.0660
- Email: info@arin.net
- Hours: M–F 7am–7pm ET

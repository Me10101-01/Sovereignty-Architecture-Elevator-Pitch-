# RPKI ROA Playbook — MOVE 3

**Depends on:** MOVE 2 (ARIN ASN assigned)
**Closes:** Route signing active, cryptographic BGP origin proof

---

## Why This Closes the Sovereignty Stack

```
Layer 1 (File):    GPG clearsign  → artifact tamper-evidence     (MOVE 1)
Layer 2 (Identity): ARIN ASN      → routing identity              (MOVE 2)
Layer 3 (Network): RPKI ROA       → cryptographic route signing   (MOVE 3)
```

Without Layer 3, anyone can announce your IP prefix and hijack your traffic.
With Layer 3, network operators running RPKI-aware routers will drop invalid
route announcements.

This is the BFT principle applied to the internet's routing table:
no single party's claim is accepted without cryptographic proof.

---

## Quick Sequence

1. ARIN ASN confirmed → enable Hosted RPKI in ARIN Online
2. Create ROA using `rpki/roa-template.yaml` as reference
3. Wait 24–48 hours → verify with routinator or RIPE validator
4. Update `roa-template.yaml` `eru.actual = 1`
5. GPG-sign `roa-template.yaml` (closes the loop back to MOVE 1)

```bash
# Sign the ROA template (MOVE 1 + MOVE 3 combined seal)
./gpg/clearsign-athena.sh rpki/roa-template.yaml
```

---

## Long-Term Maintenance

| Action | When |
|--------|------|
| Renew ROA | 30 days before `not_after` date |
| Check validator | Monthly (routinator or RIPE web) |
| Update ARIN contact info | If address/email changes |
| Re-sign roa-template.yaml | After any update |

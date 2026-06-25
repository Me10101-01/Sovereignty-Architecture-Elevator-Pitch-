# RPKI ROA Creation — MOVE 3

**Prerequisite:** ASN assigned (MOVE 2 complete)
**Closes:** Route signing active / ML-ORGANISM-004

---

## What Is a ROA?

A **Route Origin Authorization (ROA)** is a cryptographically signed object
that states: "ASN X is authorized to originate prefix Y."

Without a ROA, any BGP router could falsely claim to originate your prefix
(BGP hijacking). With a ROA + RPKI validation, downstream routers reject
invalid origins.

This is the SAGCO sovereignty stack applied to network routing:
SHA-256 seals for files → ROA signatures for BGP routes.

---

## Steps After ASN Assignment

### Step 1: Enable RPKI Hosted in ARIN Online

1. Log in → Dashboard → Resources → RPKI
2. Select **Hosted RPKI** (ARIN manages the key — simpler, recommended for start)
3. Accept the RPKI agreement

### Step 2: Create a Trust Anchor Locator (TAL)

ARIN provides this automatically in Hosted RPKI mode.
Download and store at: `rpki/ARIN.tal`

### Step 3: Create Your ROA

1. ARIN Online → RPKI → Create ROA
2. Fill in:
   - ASN: your assigned ASN (e.g., AS399999)
   - Prefix: your allocated IP prefix
   - Max prefix length: 24 (for a /24 allocation)
   - Validity period: 2 years (renew before expiry)
3. Submit — takes effect within **24–48 hours** in global RPKI validators

### Step 4: Verify ROA is Visible

```bash
# Check RIPE NCC RPKI validator (public tool)
# https://rpki-validator.ripe.net/

# Or use routinator (install separately):
routinator vrps --asn YOUR_ASN

# Expected output: one VRP (Validated ROA Payload) entry
# {asn: "AS399999", prefix: "203.0.113.0/24", max_length: 24}
```

### Step 5: Update roa-template.yaml

```yaml
eru:
  actual: 1
  verdict: "PROVEN"
```

---

## Signing with Delegated RPKI (advanced — optional)

If you later want **Delegated RPKI** (you manage your own CA):

1. Generate a private key: `openssl genrsa -out rpki_key.pem 4096`
2. Create a CSR and submit to ARIN
3. ARIN signs your certificate — you now have your own RPKI CA
4. Use routinator or FORT validator to publish ROAs from your own CA

This requires more operational overhead. Start with Hosted RPKI.

---

## ERU After MOVE 3

```
MOVE 3 (ROA created + validated):
  Expected: 1 validated ROA visible in RPKI validators
  Actual:   0 (until you complete steps above)
  Ratio:    0.0  [INFLATED → PROVEN when routinator confirms VRP]
```

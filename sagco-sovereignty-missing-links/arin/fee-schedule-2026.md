# ARIN Fee Schedule 2026

Source: https://www.arin.net/fees/fee_schedule/
Last verified: 2025 (confirm current amounts at arin.net before applying)

---

## ASN Fees

| Category | Annual Fee |
|----------|-----------|
| ASN — End-User (small org, < /24 equivalent) | **$250/year** |
| ASN — ISP / Multihomed medium | $500/year |
| ASN — Large organization | $1,000+/year |

**For Strategickhaos DAO LLC: $250/year (End-User ASN)**

---

## One-Time Registration Fee

| Type | Amount |
|------|--------|
| ASN registration (initial) | $100 one-time |
| Org ID creation | $0 (included) |

**First year total: ~$350 ($100 registration + $250 annual)**
**Subsequent years: $250/year**

---

## Payment Methods

- Credit card (Visa, MC, Amex)
- ACH bank transfer
- Check (US only)

Pay through ARIN Online: https://account.arin.net/

---

## Budget Line

```yaml
# sovereignty budget
arin_asn:
  registration_one_time: 100.00
  annual_recurring:       250.00
  year_1_total:           350.00
  currency: USD
  source: "ARIN Fee Schedule 2026"
```

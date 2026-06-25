# RPKI Best Practices

## ROA Hygiene Rules

1. **Never create a ROA for a prefix you don't own.** ARIN rejects unauthorized prefixes.
2. **Set max_length = your actual allocation.** A /24 ROA with max_length=24 prevents
   deaggregation attacks (someone announcing /25s from your /24).
3. **Set expiry 2 years out, not forever.** ROAs with far-future expiry create
   stale objects if you lose the key. Renew annually.
4. **Keep a calendar reminder 30 days before expiry.** Expired ROAs = invalid routes.
5. **Verify with an independent validator before relying on it.**

## Validator Tools

| Tool | Command |
|------|---------|
| Routinator (RIPE NCC) | `routinator vrps --asn AS12345` |
| FORT Validator | `fort --tal ARIN.tal` |
| RIPE NCC Web UI | https://rpki-validator.ripe.net/ |
| Cloudflare RPKI | https://rpki.cloudflare.com/ |

## References

- RFC 6482: ROA Profile
- RFC 8210: RPKI-to-Router Protocol
- RFC 9319: RPKI AS 0 ROA
- ARIN RPKI Hosted: https://www.arin.net/resources/manage/rpki/hosted/

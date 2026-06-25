# GPG Clearsign Playbook — MOVE 1

**Closes:** AB-GPG-UNSIGNED-001 (sagco-audit antibody registry)
**Status:** UNCOMPUTED until first successful clearsign

---

## Why This Matters

Every artifact in the SAGCO chain — FlameLang specs, SWARM_DNA, CLAIM_VERIFICATION,
board minutes — currently exists as unsigned plaintext. Anyone can modify them
after the fact. GPG clearsign creates a tamper-evident wrapper that any third party
can verify without access to a private key.

This is MOVE 1 of the three-move NDA close.

---

## One-Time Setup (do this once)

### 1. Generate your GPG key

```bash
gpg --full-generate-key
# Choose: RSA and RSA, 4096 bits, no expiry (or 2y)
# Name:  Strategickhaos DAO LLC
# Email: domenic.garza@snhu.edu
```

### 2. Export your public key (for third-party verification)

```bash
# Get your key fingerprint
gpg --list-secret-keys --keyid-format LONG

# Export (share this publicly)
gpg --armor --export YOUR_KEY_FINGERPRINT > strategickhaos_dao_public.asc
```

### 3. Set environment variable (optional)

```bash
export SAGCO_GPG_KEY="YOUR_KEY_FINGERPRINT"
# Add to ~/.bashrc or ~/.zshrc to persist
```

---

## Signing an Artifact (MOVE 1)

```bash
# Sign one file
./gpg/clearsign-athena.sh CLAIM_VERIFICATION_2025.md

# Output: CLAIM_VERIFICATION_2025.md.gpg

# Sign all unsigned .md and .yaml in current directory
./gpg/clearsign-athena.sh
```

### What the output looks like

```
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA256

[original file content here]

-----BEGIN PGP SIGNATURE-----

[64 lines of base64 signature]
-----END PGP SIGNATURE-----
```

---

## Verifying a Signed File

```bash
# Verify one file
./gpg/verify.sh CLAIM_VERIFICATION_2025.md.gpg

# Verify all in current directory
./gpg/verify.sh
```

---

## Priority Files to Sign (in order)

| File | Why |
|------|-----|
| `CLAIM_VERIFICATION_2025.md` | Primary invention claim chain |
| `SWARM_DNA_v12.0-*.yaml` | Architecture DNA |
| `PROVENANCE.yaml` | Chain of custody |
| `sagco-audit/registry/antibody_registry.yaml` | Antibody chain |
| `sagco-organism/sagco-brick.toml` | BRICK-020 provenance |
| `sagco-archaeologist/sagco-brick.toml` | BRICK-021 provenance |
| `INV-198` PDF (if you have the source) | Patent filing anchor |

---

## Verify the Verifier (recursive)

After signing `CLAIM_VERIFICATION_2025.md`, sign the verify log:

```bash
./gpg/clearsign-athena.sh logs/gpg_receipts.log
```

This closes the recursive loop: the signing receipts are themselves signed.

---

## Troubleshooting

**"No secret key found"**
→ You haven't generated a key yet. Run `gpg --full-generate-key`.

**"gpg: can't open signed file"**
→ The `.gpg` file is missing or corrupted. Re-sign the source file.

**"BAD signature"**
→ The file was modified after signing. Compare with git history.
→ Check for line-ending conversion (LF ↔ CRLF) if cross-platform.

---

## ERU Tracking

```
MOVE 1 (GPG clearsign):
  Expected: 1 signed artifact
  Actual:   0 (until you run clearsign-athena.sh)
  Ratio:    0.0  [INFLATED → will flip to PROVEN on first sign]
```

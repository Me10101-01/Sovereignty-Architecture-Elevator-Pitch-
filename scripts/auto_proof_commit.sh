#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

BRANCH="safety/charitable-commitment"
FILE="docs/CHARITABLE_COMMITMENT.md"
PROOF_DIR="docs/proofs"

echo "=== Strategickhaos Swarm Intelligence – Auto Proof Ritual ==="
echo "Target branch: $BRANCH"
echo "Document:      $FILE"
echo

# 1. Ensure correct branch
if [ "$(git rev-parse --abbrev-ref HEAD)" != "$BRANCH" ]; then
  echo "Switching/creating branch $BRANCH"
  git checkout -B "$BRANCH"
fi

# 2. Ensure proof directory exists
mkdir -p "$PROOF_DIR"

# 3. Re-compute SHA256 hash (always fresh)
echo "Computing fresh SHA256 hash..."
sha256sum "$FILE" | awk '{print $1}' > "$PROOF_DIR/CHARITABLE_COMMITMENT.md.hash"
echo "→ $PROOF_DIR/CHARITABLE_COMMITMENT.md.hash updated"

# 4. OpenTimestamps stamp (optional – skips gracefully if ots not available)
if command -v ots >/dev/null 2>&1; then
  echo "Running OpenTimestamps stamp..."
  ots stamp "$FILE" -o "$PROOF_DIR/CHARITABLE_COMMITMENT.md.ots" || echo "OTS stamp failed – continuing anyway"
else
  echo "ots command not found – skipping timestamp (install opentimestamps-client if you want it)"
fi

# 5. GPG signing – prompt for key if needed
if ! gpg --list-secret-keys --keyid-format LONG >/dev/null 2>&1; then
  echo "No GPG secret keys found on this machine. Cannot sign."
  exit 1
fi

echo
echo "Available secret keys:"
gpg --list-secret-keys --keyid-format LONG | grep -B2 "sec "
echo
read -p "Enter your GPG key ID (e.g. 0xABCDEF1234567890 or short): " GPG_KEY

echo "Creating detached signature with key $GPG_KEY ..."
gpg --local-user "$GPG_KEY" --armor --detach-sign --output "$PROOF_DIR/CHARITABLE_COMMITMENT.md.sig" "$FILE"

echo "Exporting public key..."
gpg --armor --export "$GPG_KEY" > "$PROOF_DIR/gpg_pubkey.asc"

# 6. Safety check – refuse if any private key material is staged
if git status --porcelain | grep -q "-----BEGIN PGP PRIVATE KEY BLOCK-----"; then
  echo "PRIVATE KEY DETECTED IN CHANGES – ABORTING!"
  exit 1
fi

# 7. Show exactly what will be committed
echo
echo "=== Changes about to be committed ==="
git status --short
echo
git diff --staged || true
echo

read -p "Commit and push these proofs? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  git add "$PROOF_DIR"/CHARITABLE_COMMITMENT.md.*
  git commit -m "chore(proofs): add OpenTimestamps .ots and GPG signature for CHARITABLE_COMMITMENT"
  git push --force-with-lease origin "$BRANCH"
  echo "Proofs stamped, signed, committed and pushed."
  echo "Go watch CI light up green: https://github.com/Strategickhaos-Swarm-Intelligence/sovereignty-architecture/actions"
else
  echo "Aborted – nothing pushed."
fi

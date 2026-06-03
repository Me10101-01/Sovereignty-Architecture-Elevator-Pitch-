#!/bin/sh
# sagco-git-ssh-setup — Wire GitHub SSH auth on any SAGCO node
# Fixes: HTTPS auth failures, password prompts, token expiry.
# GitHub no longer accepts passwords for CLI git — SSH key or PAT required.
#
# Usage:
#   sagco-git-ssh-setup                → setup for current device
#   sagco-git-ssh-setup zfold          → label key as zfold
#   sagco-git-ssh-setup test           → test existing SSH connection
#   sagco-git-ssh-setup remote         → switch repo remote to SSH

DEV="${SAGCO_DEVICE:-$(cat "$HOME/.sagco_device" 2>/dev/null || echo $(hostname 2>/dev/null || echo node))}"
ARG="${1:-$DEV}"
REPO="Me10101-01/Sovereignty-Architecture-Elevator-Pitch-"
KEY_FILE="$HOME/.ssh/sagco_github"
SSH_CONFIG="$HOME/.ssh/config"

case "$ARG" in

    test)
        echo "Testing SSH connection to GitHub..."
        ssh -T git@github.com -i "$KEY_FILE" 2>&1
        exit 0
        ;;

    remote)
        echo "Switching remote to SSH..."
        git remote -v
        git remote set-url origin "git@github.com:${REPO}.git"
        echo "New remote:"
        git remote -v
        exit 0
        ;;

esac

LABEL="${ARG}-sagco-github"

echo "SAGCO GIT SSH SETUP"
echo "===================="
echo "Device:  $ARG"
echo "Key:     $KEY_FILE"
echo "Label:   $LABEL"
echo ""

# ── generate key ──────────────────────────────────────────────────────────────
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

if [ -f "$KEY_FILE" ]; then
    echo "Key already exists: $KEY_FILE"
    echo "(delete it and re-run to regenerate)"
else
    ssh-keygen -t ed25519 -C "$LABEL" -f "$KEY_FILE" -N ""
    echo "Key generated: $KEY_FILE"
fi

# ── write SSH config ──────────────────────────────────────────────────────────
if grep -q "sagco_github" "$SSH_CONFIG" 2>/dev/null; then
    echo "SSH config already has sagco_github entry"
else
    cat >> "$SSH_CONFIG" <<SSHCONF

Host github.com
  HostName github.com
  User git
  IdentityFile $KEY_FILE
  IdentitiesOnly yes
SSHCONF
    chmod 600 "$SSH_CONFIG"
    echo "SSH config updated: $SSH_CONFIG"
fi

chmod 600 "$KEY_FILE"

# ── print public key ──────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════"
echo "ADD THIS KEY TO GITHUB:"
echo "GitHub → Settings → SSH and GPG keys → New SSH key"
echo "════════════════════════════════════════════════════"
echo ""
cat "${KEY_FILE}.pub"
echo ""
echo "════════════════════════════════════════════════════"
echo ""
echo "After adding the key, run these three commands:"
echo ""
echo "  ssh -T git@github.com"
echo "  git remote set-url origin git@github.com:${REPO}.git"
echo "  git push"
echo ""
echo "STATUS=SAGCO_SSH_SETUP_PASS"
echo "KEY=$KEY_FILE"

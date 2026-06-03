#!/bin/sh
set -u

EMAIL="${1:-zfold-sagco-github}"
REPO="${2:-git@github.com:Me10101-01/Sovereignty-Architecture-Elevator-Pitch-.git}"

mkdir -p ~/.ssh
chmod 700 ~/.ssh

if [ ! -f ~/.ssh/sagco_github ]; then
  ssh-keygen -t ed25519 -C "$EMAIL" -f ~/.ssh/sagco_github -N ""
fi

cat > ~/.ssh/config <<CFG
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/sagco_github
  IdentitiesOnly yes
CFG

chmod 600 ~/.ssh/config ~/.ssh/sagco_github

echo "=== COPY THIS PUBLIC KEY TO GITHUB ==="
cat ~/.ssh/sagco_github.pub
echo
echo "GitHub -> Settings -> SSH and GPG keys -> New SSH key"
echo
echo "After adding it, run:"
echo "ssh -T git@github.com"
echo "git remote set-url origin $REPO"
echo "git pull --rebase"
echo "git push"
echo "STATUS=SAGCO_GIT_SSH_FIX_READY"

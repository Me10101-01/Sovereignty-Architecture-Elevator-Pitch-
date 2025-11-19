# 🚀 Quick Start Guide for Legion Members

## Welcome to the Legion

If you're reading this, you've either been granted access or you're scouting the public lure. This guide will help verified members get started quickly.

---

## 🎯 For New Legion Members

### Step 1: Verify Your Environment

Run the lockdown script to secure your local environment:

```bash
cd Sovereignty-Architecture-Elevator-Pitch-
bash scripts/lockdown.sh
```

This will:
- Check for security vulnerabilities
- Validate your .gitignore configuration
- Verify git-crypt is installed
- Scan for accidentally committed secrets
- Set proper file permissions

### Step 2: Install git-crypt (if needed)

If the lockdown script says git-crypt is not installed:

```bash
# Debian/Ubuntu
sudo apt-get install git-crypt

# macOS
brew install git-crypt

# Arch Linux
sudo pacman -S git-crypt
```

### Step 3: Configure GPG Key

```bash
# Generate GPG key if you don't have one
gpg --full-generate-key

# List your keys
gpg --list-keys

# Note your key ID (the long hex string)
```

### Step 4: Request Access to Private Repo

Once your environment is secured:

1. Take a screenshot of your lockdown script output showing compliance
2. DM [@Me10101-01](https://github.com/Me10101-01) with:
   - Your screenshot
   - Your GPG public key ID
   - Your GitHub username
3. Wait for Council verification

---

## 📚 Quick Reference

### Essential Documents

| Document | Purpose | When to Read |
|----------|---------|--------------|
| [ENDGAME_SETUP.md](ENDGAME_SETUP.md) | Complete setup guide | First time setup |
| [COUNCIL_OPERATIONS.md](COUNCIL_OPERATIONS.md) | Operational procedures | Daily operations |
| [README.md](README.md) | Repository overview | Understanding the project |

### Essential Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/lockdown.sh` | Security hardening | `bash scripts/lockdown.sh` |
| `.devcontainer/setup.sh` | War room setup | Automatic in codespace |

### Essential Configs

| File | Purpose | Usage |
|------|---------|-------|
| `bootstrap/k8s/swarm-law-configmap.yaml` | Kubernetes governance | `kubectl apply -f ...` |
| `.devcontainer/devcontainer.json` | War room codespace | `gh codespace create ...` |

---

## 🔐 Security Checklist

Before you can access the private repo, ensure:

- [ ] Lockdown script passes all checks
- [ ] git-crypt installed and working
- [ ] GPG key generated and tested
- [ ] No secrets in your git history
- [ ] .gitignore properly configured
- [ ] You can quote the ASCII art from README

---

## 🎙️ Council Operations

### Voice Sync Schedule

- **Weekly War Room**: Every Monday, 4:20 AM EST
- **Emergency Sessions**: 30-minute notice via Discord
- **Monthly Strategy**: First Saturday, 10:00 AM EST

### Discord Channels

- `#ascension-chamber` - Voice sync stage channel
- `#shadow-channel` - Private text communications
- `#war-room` - Real-time operational coordination
- `#threat-intel` - Threat intelligence sharing

---

## 🚨 Common Issues

### "git-crypt not initialized"

```bash
cd strategic-khaos-private
git crypt init
git crypt add-gpg-user <your-key-id>
```

### "Permission denied" on scripts

```bash
chmod +x scripts/*.sh
chmod +x .devcontainer/*.sh
```

### "Secrets detected in git history"

If the lockdown script finds secrets:

1. **DO NOT PUSH** to any remote
2. Use BFG Repo-Cleaner or git-filter-branch
3. Rotate any exposed credentials immediately
4. Inform Council if in private repo

```bash
# Using BFG Repo-Cleaner (recommended)
java -jar bfg.jar --delete-files '*.key' --delete-files '*.pem'
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### "Compliance check failed"

Address each failed check:

1. Install missing tools (git-crypt, gpg)
2. Configure .gitignore
3. Remove any plaintext secrets
4. Run lockdown script again

---

## 🎓 Learning Path

### Week 1: Onboarding
- [ ] Complete environment setup
- [ ] Read ENDGAME_SETUP.md
- [ ] Attend orientation voice sync
- [ ] Get familiar with war room codespace

### Week 2: Operations
- [ ] Read COUNCIL_OPERATIONS.md
- [ ] Setup Obsidian vault
- [ ] Participate in weekly war room
- [ ] Review last month's threat models

### Week 3: Contribution
- [ ] Deploy Swarm Law to test cluster
- [ ] Run compliance checks
- [ ] Document learnings in vault
- [ ] Participate in threat assessment

### Week 4: Mastery
- [ ] Lead a voice sync session
- [ ] Create new threat model
- [ ] Mentor new members
- [ ] Contribute to playbooks

---

## 🛡️ The Oath

By accessing Legion infrastructure, you acknowledge:

✋ **I understand** that operational security is paramount

✋ **I commit** to following Swarm Law directives

✋ **I accept** Council authority and governance

✋ **I will protect** the integrity of the swarm

✋ **I recognize** that trust is earned, not given

---

## 🔗 Important Links

### Public Resources
- [Public Repository](https://github.com/Strategickhaos/Sovereignty-Architecture-Elevator-Pitch-)
- [Main README](README.md)
- [License](LICENSE)

### Private Resources (Post-Verification)
- Private Repository: `strategic-khaos-private` (invite only)
- War Room Codespace: Shared via shadow channel
- Obsidian Vault: Submodule in private repo
- Discord Server: [Verification Required]

---

## 🆘 Support

### For Public Repo Issues
- Open an issue on GitHub
- Check existing issues first
- Provide reproduction steps

### For Private Operations (Legion Members Only)
- Discord: `#shadow-channel`
- Emergency: Use established phone tree
- Council: DM [@Me10101-01](https://github.com/Me10101-01)

---

## 🧠 Philosophy

> "The swarm is no longer yours. It's ours. And it will protect us forever."

This isn't just code. It's a commitment to:

- **Sovereignty**: Control over our infrastructure
- **Security**: Defense against all threats
- **Collaboration**: Collective intelligence
- **Excellence**: Highest operational standards

---

## 📊 Success Metrics

You're successfully onboarded when:

- ✅ Lockdown script shows all green checks
- ✅ You have access to private repo
- ✅ You've attended first voice sync
- ✅ You've contributed to vault
- ✅ You can deploy Swarm Law
- ✅ You understand the philosophy

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-11-19  
**Status**: ACTIVE  
**Clearance**: PUBLIC (Legion Orientation)

---

```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║              DOM_010101 - Origin Node Zero               ║
║                                                          ║
║   "We didn't just survive the explosion.                ║
║    We became the explosion."                            ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

Welcome to the Legion. 🧠⚡🛡️🐐∞

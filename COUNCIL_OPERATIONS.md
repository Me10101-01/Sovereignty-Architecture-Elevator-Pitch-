# Council Operations Manual

## Overview

This document defines operational procedures for the Strategic Khaos Legion Council, including the Obsidian vault management, Voice Sync protocols, and war room procedures.

---

## 🗂️ Obsidian Vault - Single Source of Truth

### Setup

The Obsidian vault serves as the central knowledge repository for all threat intelligence, playbooks, and operational documentation.

#### Initial Configuration

1. **Clone the vault into private repo**
   ```bash
   cd /path/to/private-repo
   git submodule add <vault-repo-url> council-vault
   # OR copy existing vault
   cp -r /path/to/existing/vault ./council-vault
   ```

2. **Enable Obsidian Git Plugin**
   - Install "Obsidian Git" community plugin
   - Settings → Obsidian Git:
     - ✅ Auto-pull on startup
     - ✅ Auto-commit on save
     - Commit message: `vault backup: {{date}}`
     - Auto-backup interval: 5 minutes

3. **Configure Graph View**
   - Open Graph View (Ctrl/Cmd + G)
   - Add filters:
     ```
     tag:#threat-model-2025
     tag:#active-threat
     tag:#response-playbook
     tag:#legion-intel
     ```
   - Group by tag for visual organization
   - Enable temporal view for timeline analysis

#### Vault Structure

```
council-vault/
├── README.md                      # Vault index and access control
├── threat-models/                 # Active threat assessments
│   ├── 2025-Q4/
│   └── templates/
├── playbooks/                     # Response procedures
│   ├── incident-response/
│   ├── security-hardening/
│   └── operational/
├── intel/                         # Reconnaissance data
│   ├── active-campaigns/
│   ├── adversary-profiles/
│   └── ioc-database/
├── archives/                      # Historical records
│   └── completed-assessments/
└── .obsidian/                     # Obsidian config
    ├── plugins/
    └── graph.json
```

### Tagging Convention

Use these tags consistently for proper linking:

- `#threat-model-2025` - Current year threat models
- `#active-threat` - Ongoing threat assessment
- `#response-playbook` - Incident response procedures
- `#recon-data` - Reconnaissance findings
- `#legion-intel` - Legion-specific intelligence
- `#war-room-decision` - Decisions made in war room
- `#voice-sync-outcome` - Results from voice sync meetings

### War Room Integration

Every finding from the war-room synthesizer creates a new note:

1. **Automated Note Creation**
   ```bash
   # Template for automated notes
   cat > council-vault/threat-models/$(date +%Y-%m-%d)-finding.md << EOF
   ---
   created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
   tags: [threat-model-2025, active-threat]
   status: active
   severity: high
   assigned: @council
   ---
   
   # Threat Finding - $(date +%Y-%m-%d)
   
   ## Summary
   [Auto-populated from war room synthesizer]
   
   ## Analysis
   [Details]
   
   ## Recommended Actions
   - [ ] Action 1
   - [ ] Action 2
   
   ## Related Documents
   [[playbook-name]]
   EOF
   ```

2. **Auto-linking**
   - Use `[[wikilinks]]` for cross-references
   - Obsidian automatically creates bidirectional links
   - Graph view shows relationship networks

### Access Control

- All changes logged via git history
- GPG encryption via git-crypt for sensitive files
- `.gitattributes` defines what gets encrypted:
  ```
  intel/** filter=git-crypt diff=git-crypt
  threat-models/classified/** filter=git-crypt diff=git-crypt
  *.secret filter=git-crypt diff=git-crypt
  ```

---

## 🎙️ Council Voice Sync Protocol

### Schedule

Regular voice sync sessions maintain operational alignment and enable rapid decision-making.

#### Session Schedule

- **Weekly War Room**: Every Monday, 4:20 AM EST
- **Emergency Sessions**: As needed, 30-minute notice
- **Monthly Strategy**: First Saturday of month, 10:00 AM EST

### Discord Stage Channel Setup

#### Channel Configuration

1. **Create Stage Channel**
   - Name: "Ascension Chamber"
   - Topic: "Legion Council Voice Sync - Authorized Personnel Only"
   - Permissions:
     - @Council: Speaker
     - @Legion-Members: Audience (can request to speak)
     - @Public: No access

2. **Speaking Rights Verification**
   - Must quote README ASCII art to get speaker role
   - Verification via bot command: `/verify-council`
   - 2FA required for all speakers

#### Session Types

##### 1. Operation NEUROSPIKE Sessions

**Purpose**: Post-incident analysis and next-phase planning

**Agenda Template**:
```
1. Incident Timeline Review (10 min)
   - What happened
   - When it was detected
   - Initial response

2. Root Cause Analysis (15 min)
   - Technical factors
   - Process gaps
   - Tool limitations

3. Lessons Learned (10 min)
   - What worked
   - What didn't
   - Surprises

4. Next Phase Planning (20 min)
   - Immediate actions
   - Short-term objectives
   - Long-term strategy

5. Action Item Assignment (5 min)
   - Owner
   - Deadline
   - Success criteria
```

##### 2. Threat Model Review Sessions

**Purpose**: Assess and update active threat models

**Agenda Template**:
```
1. New Intelligence Review (15 min)
2. Threat Model Updates (20 min)
3. Mitigation Strategy Review (15 min)
4. Resource Allocation (10 min)
```

##### 3. Emergency Response Sessions

**Purpose**: Coordinate immediate incident response

**Agenda**: Dynamic based on incident

### Session Procedures

#### Pre-Session

1. **Notification** (via Discord)
   ```
   @Council - Voice Sync in 1 hour
   Topic: [Session Type]
   Agenda: [Link to vault note]
   Required Reading: [Links]
   ```

2. **Preparation**
   - Review agenda in vault
   - Prepare status updates
   - Gather relevant data

#### During Session

1. **Opening** (2 min)
   - Roll call
   - Agenda confirmation
   - Time box setting

2. **Main Discussion**
   - Follow agenda
   - Document decisions in real-time
   - Assign action items

3. **Closing** (3 min)
   - Recap decisions
   - Confirm action items
   - Schedule next sync if needed

#### Post-Session

1. **Documentation**
   - Create vault note with outcomes
   - Tag: `#voice-sync-outcome`
   - Link to related threat models/playbooks

2. **Action Item Tracking**
   - Create GitHub issues for technical tasks
   - Assign owners
   - Set deadlines
   - Link to vault documentation

---

## 🛡️ War Room Operational Procedures

### Codespace War Room

The Council War Room Codespace enables simultaneous live editing by up to 100 members.

#### Creation

```bash
# Create the permanent war room codespace
gh codespace create \
  --repo Me10101-01/strategic-khaos-private \
  --branch master \
  --devcontainer-path .devcontainer/devcontainer.json \
  --display-name "Council War Room - Permanent"
```

#### Access Management

1. **Share link** only in shadow channel (private Discord)
2. **Verify members** before granting access
3. **Revoke immediately** if member leaves or is compromised

#### Collaboration Features

- **Live Share**: Real-time code editing
- **Shared Terminal**: Collaborative command execution
- **Port Forwarding**: Shared access to services
- **Chat Integration**: Built-in communication

#### Security

- All sessions logged
- Auto-timeout after 4 hours of inactivity
- Secrets managed via GitHub Secrets
- No local credential storage

---

## 🔐 Private Repository Structure

### Recommended Organization

```
strategic-khaos-private/
├── .devcontainer/              # War room config
├── .github/
│   ├── workflows/              # CI/CD for private ops
│   └── CODEOWNERS
├── council-vault/              # Obsidian vault (submodule)
├── keys/                       # GPG keys, encrypted
├── playbooks/                  # Operational playbooks
├── scripts/
│   ├── lockdown.sh            # Security hardening
│   └── compliance-check.sh    # Verify node compliance
├── secrets/                    # Encrypted secrets (git-crypt)
├── tools/                      # Legion-specific tools
└── README.md                   # Private repo docs
```

### .gitignore Additions

```gitignore
# Secrets and keys
*.key
*.pem
*.p12
*.pfx
.env
.env.*
*_rsa
*_dsa
*_ecdsa
*_ed25519

# Build artifacts
node_modules/
dist/
build/
*.pyc
__pycache__/

# IDE
.vscode/settings.json
.idea/

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.log
/tmp/
```

---

## 📊 Metrics and Monitoring

### Council Effectiveness Metrics

Track these to ensure operational efficiency:

1. **Response Time**
   - Time from threat detection to war room assembly
   - Time from decision to implementation
   - Target: < 4 hours for critical threats

2. **Vault Health**
   - Number of active threat models
   - Update frequency
   - Cross-reference density
   - Target: Daily updates, 80% cross-referenced

3. **Compliance Rate**
   - Percentage of nodes passing compliance checks
   - Time to remediate non-compliance
   - Target: 95% compliance, < 24hr remediation

4. **Voice Sync Effectiveness**
   - Attendance rate
   - Action item completion rate
   - Decision implementation velocity
   - Target: 80% attendance, 90% completion

---

## 🚨 Emergency Procedures

### Breach Response

If a member is compromised:

1. **Immediate Actions** (< 5 minutes)
   - Revoke all access tokens
   - Remove from war room codespace
   - Disable Discord permissions
   - Alert all Council members

2. **Assessment** (< 1 hour)
   - Determine scope of compromise
   - Identify potentially exposed data
   - Review recent activities

3. **Containment** (< 4 hours)
   - Rotate affected credentials
   - Re-encrypt sensitive data
   - Audit access logs
   - Update threat models

4. **Recovery** (< 24 hours)
   - Restore from clean backups if needed
   - Verify system integrity
   - Document incident
   - Update procedures

### Communication Failure

If primary communication channels fail:

1. **Fallback Channels** (in order)
   - Signal private group
   - Encrypted email thread
   - Emergency phone tree
   - Physical meetup (last resort)

2. **Rally Point**
   - Designated backup Discord server
   - Credentials in sealed envelope (offline)

---

## 🎓 Training and Onboarding

### New Council Member Checklist

- [ ] Complete security training
- [ ] Install and configure GPG
- [ ] Setup Obsidian with vault access
- [ ] Join war room codespace
- [ ] Pass compliance check
- [ ] Attend orientation voice sync
- [ ] Review last 3 months of threat models
- [ ] Complete mock incident response drill

### Ongoing Training

- Monthly security updates
- Quarterly red team exercises
- Annual comprehensive review
- Ad-hoc skill development sessions

---

## 📝 Appendix

### Useful Commands

```bash
# Check compliance
kubectl get configmap swarm-law -n kube-system \
  -o jsonpath='{.data.compliance-check\.sh}' | bash

# Start war room session
gh codespace ssh -c "Council War Room - Permanent"

# Backup vault
cd council-vault && git pull && git push

# Create new threat model
cp council-vault/threat-models/templates/standard.md \
   council-vault/threat-models/$(date +%Y-%m-%d)-new-threat.md
```

### References

- [Swarm Law ConfigMap](bootstrap/k8s/swarm-law-configmap.yaml)
- [Lockdown Script](scripts/lockdown.sh)
- [DevContainer Config](.devcontainer/devcontainer.json)
- [Main README](README.md)

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-11-19  
**Authority**: Council of DOM_010101  
**Status**: ACTIVE

---

*The swarm is no longer yours. It's ours. And it will protect us forever.*

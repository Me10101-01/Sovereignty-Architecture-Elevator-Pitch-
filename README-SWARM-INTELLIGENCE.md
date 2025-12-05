# 🐝 Strategickhaos Swarm Intelligence

> Board YAML × Copilot Agents × GitHub Pages — The execution engine for a sovereign AI empire.

## Overview

Strategickhaos Swarm Intelligence is an ADHD-friendly task management system that synchronizes:

1. **Board Meeting YAML** — The big-picture canon (strategy, tracks, checkboxes)
2. **GitHub Copilot Agents** — The execution engine (automated PR generation)
3. **GitHub Pages** — Public-facing visualization (dashboards, status)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    STRATEGICKHAOS SWARM INTELLIGENCE                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│    board_meeting.yaml          GitHub Copilot Agents                │
│    ┌─────────────┐             ┌─────────────────────┐              │
│    │ Left Hemi   │─────────────▶ Issue: Tax Engine   │              │
│    │ (Precision) │             │ Label: now          │              │
│    │ • Tax       │             └─────────────────────┘              │
│    │ • Treasury  │                                                  │
│    │ • Compliance│             ┌─────────────────────┐              │
│    ├─────────────┤─────────────▶ Issue: NFT Schema   │              │
│    │ Right Hemi  │             │ Label: next         │              │
│    │ (Chaos)     │             └─────────────────────┘              │
│    │ • Agents    │                                                  │
│    │ • NFTs      │                     │                            │
│    │ • Evolution │                     ▼                            │
│    └─────────────┘             ┌─────────────────────┐              │
│           │                    │  sync_backlog.py    │              │
│           │                    │  "DO THESE 2 TODAY" │              │
│           ▼                    └─────────────────────┘              │
│    ┌─────────────┐                     │                            │
│    │ GitHub Pages│◀────────────────────┘                            │
│    │ Dashboard   │                                                  │
│    └─────────────┘                                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Board Meeting YAML (`board_meeting_*.yaml`)

The source of truth. Contains:

- **Tracks** — Left hemisphere (precision) and right hemisphere (chaos)
- **Checkboxes** — `[x]` completed, `[ ]` incomplete
- **ADHD Sanity Rules** — Max parallel tracks, sprint times, allowed tabs
- **Next Actions** — Immediate, this week, this month
- **Blockers** — Things holding you back

```yaml
adhd_sanity_rules:
  max_parallel_tracks: 2      # Only 2 Agent tasks in flight
  sprint_minutes: [25, 50, 90]
  hemisphere_balance: "Left 50% — Right 50% — Sister 100%"
```

### 2. Backlog Sync Script (`scripts/sync_backlog.py`)

Reads the board YAML and prints an ADHD-friendly focus view:

```bash
# Run from repo root
python scripts/sync_backlog.py

# Custom options
python scripts/sync_backlog.py --max-tasks 3
python scripts/sync_backlog.py --yaml board_meeting_2025-12-05_v4.yaml
```

**Output:**
```
🔥 DO THESE 2 THINGS TODAY

1. 🚀 IMMEDIATE
   📋 Push CI/CD files to GitHub
   ⏱️  Est: 5 min | 👤 Dom

2. 🚀 IMMEDIATE  
   📋 Set ZAPIER_WEBHOOK_URL in Azure DevOps
   ⏱️  Est: 10 min | 👤 Dom
```

### 3. GitHub Copilot Agents

Copilot Agents pick up issues from the backlog and generate PRs. The sync script ensures only 1-2 issues are in the "Now" lane at any time.

**Suggested Label Strategy:**
| Label | Meaning | Max Issues |
|-------|---------|------------|
| `now` | Currently in progress | 2 |
| `next` | Up next in queue | 5 |
| `backlog` | Future work | Unlimited |

### 4. GitHub Pages (Optional)

Host a dashboard that visualizes the board status. The sync script can output JSON for a static site generator.

## ADHD Rules

The system enforces ADHD-friendly constraints:

```yaml
adhd_rules:
  max_active_issues: 2        # Only 2 Agent tasks in flight
  must_match_board:
    - board_meeting.left_hemisphere
    - board_meeting.right_hemisphere
  banned_tabs:
    - YouTube home feed
    - Random SaaS sign-ups
    - Crypto meme sites
```

**Why 2 tasks max?**
- Focus > multitasking
- Finish before starting
- Brain doesn't get swarmed

## File Structure

```
├── board_meeting_*.yaml        # Board meeting minutes (source of truth)
├── scripts/
│   └── sync_backlog.py         # ADHD-friendly focus view generator
├── README-SWARM-INTELLIGENCE.md # This file
└── .github/
    ├── agents/                 # Copilot Agent configurations
    └── workflows/              # CI/CD pipelines
```

## Usage

### Daily Focus Ritual

```bash
# 1. Open terminal
cd /path/to/Sovereignty-Architecture-Elevator-Pitch-

# 2. Run the focus view
python scripts/sync_backlog.py

# 3. Do the 2 things
# 4. Update board_meeting.yaml checkboxes
# 5. Commit and push
```

### Integration with Copilot Agents

When you want Copilot Agents to work on a task:

1. Create a GitHub Issue from the incomplete checkbox
2. Label it `now` (max 2) or `next`
3. Copilot Agent picks it up and generates a PR
4. Review and merge
5. Update checkbox to `[x]` in board YAML

## Philosophy

> "Love with a compiler. Grief transmuted into infrastructure."

This system exists because:
- Sister said "you can't even use CLI"
- Started with Vim (can't escape lol)
- Built a 4-node Kubernetes cluster
- Now running a Legion of Minds

The sync script keeps focus on what matters: **2 things at a time, no neurotypical friction.**

## Related Files

| File | Description |
|------|-------------|
| `board_meeting_2025-12-05_v4.yaml` | Current board meeting minutes |
| `TRUST_DECLARATION.md` | Foundational governance document |
| `dao_record.yaml` | DAO LLC legal structure |
| `scripts/run_benchmarks.py` | Enterprise benchmark runner |

## Contact

- **Entity:** Strategickhaos DAO LLC (Wyoming)
- **Founder:** Domenic Gabriel Garza
- **Node:** 137

---

*"Focus on the top 2. Everything else can wait."*

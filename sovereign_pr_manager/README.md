# SovereignPRManager: Autonomous PR Orchestration System

> 🤖 Zero-button operation: Copilot generates → System validates → Auto-merge with provenance

## Overview

SovereignPRManager is an autonomous PR orchestration system that eliminates manual PR management. It provides:

- **Multi-perspective code review** - Security, architecture, and sovereignty compliance
- **Conflict detection** - Git, semantic, and dependency conflicts
- **Dialectical synthesis** - Combines reviews into unified merge decisions
- **Auto-merge with provenance** - Cryptographic signing and audit trails

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  SovereignPRManager v1.0                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐  │
│  │ PR Monitor  │ → │ Code Review │ → │ Conflict Detect │  │
│  └─────────────┘   └─────────────┘   └─────────────────┘  │
│         │                                     │            │
│         │         ┌─────────────────┐         │            │
│         └────────→│ Synthesis Engine │←───────┘            │
│                   └─────────────────┘                      │
│                           │                                │
│                   ┌───────┴───────┐                       │
│                   │  Auto Merger   │                       │
│                   └───────────────┘                       │
│                           │                                │
│         ┌─────────────────┼─────────────────┐             │
│         ▼                 ▼                 ▼             │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐         │
│   │  GitHub  │     │ Provenance│     │ Discord  │         │
│   │  Merge   │     │   Log    │     │ Notify   │         │
│   └──────────┘     └──────────┘     └──────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Installation

```bash
cd sovereign_pr_manager
pip install -r requirements.txt
```

### Usage

```bash
# Dry run on all open PRs
python -m sovereign_pr_manager --dry-run

# Process a specific PR
python -m sovereign_pr_manager --pr 42 --dry-run

# Continuous monitoring mode
python -m sovereign_pr_manager --monitor

# Enable auto-merge (requires GITHUB_TOKEN with write permissions)
export DRY_RUN=false
python -m sovereign_pr_manager
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_TOKEN` | Yes | - | GitHub Personal Access Token |
| `GITHUB_REPO` | No | `Me10101-01/Sovereignty-Architecture-Elevator-Pitch-` | Target repository |
| `DRY_RUN` | No | `true` | Disable actual merges |
| `DISCORD_WEBHOOK_URL` | No | - | Discord webhook for notifications |
| `MERGE_THRESHOLD_AUTO` | No | `0.90` | Confidence threshold for auto-merge |
| `MERGE_THRESHOLD_SECURITY` | No | `0.80` | Security review veto threshold |
| `MERGE_THRESHOLD_SOVEREIGNTY` | No | `0.70` | Minimum sovereignty compliance |
| `POLL_INTERVAL_SECONDS` | No | `10` | PR poll interval in monitor mode |

## Review Types

### 1. Security Review
Checks for:
- Credential exposure (API keys, passwords, tokens)
- Dangerous patterns (eval, exec, shell injection)
- Cryptographic weaknesses

### 2. Architecture Review
Checks for:
- Large PR size
- Missing error handling
- TODO/FIXME accumulation
- Debug statements

### 3. Sovereignty Review
Checks for:
- External cloud dependencies
- Self-hosted alternatives
- Audit trail presence
- Logging patterns

## Merge Thresholds

| Threshold | Default | Description |
|-----------|---------|-------------|
| `auto_merge` | 90% | All reviews must reach this confidence |
| `security_veto` | 80% | Security below this blocks merge |
| `sovereignty_minimum` | 70% | Minimum sovereignty compliance |

## Synthesis Algorithm

The dialectical synthesis process:

1. **Thesis**: Security review perspective
2. **Antithesis**: Architecture review perspective
3. **Context**: Sovereignty review + conflict detection
4. **Synthesis**: Unified confidence score and merge decision

```python
confidence = avg_review_confidence - conflict_penalty + sovereignty_bonus
action = "merge" if confidence >= 0.90 else "review_required"
```

## Provenance

Every merge generates a provenance record:

```json
{
  "pr_number": 42,
  "pr_title": "Add feature X",
  "decision": {
    "action": "merge",
    "confidence": 0.92,
    "reasoning": "All 3 review(s) approved. Confidence: 92.0%"
  },
  "merged_by": "SovereignPRManager v1.0",
  "git_sha": "abc123...",
  "signature": "d4f5e6a7b8c9d0e1f2a3b4c5",
  "timestamp": "2025-12-04T12:00:00Z"
}
```

## GitHub Actions Integration

The workflow runs automatically on PR events:

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
```

Or trigger manually via workflow_dispatch.

## Philosophy

This system embodies the Strategickhaos "zero-button operation" philosophy:

> **Contradiction**: Manual PR review creates bottlenecks
> **Thesis**: AI can analyze code faster than humans
> **Antithesis**: AI lacks human judgment for edge cases
> **Synthesis**: High-confidence merges auto-approve; edge cases escalate to humans

## License

MIT License - Part of the Sovereignty Architecture project.

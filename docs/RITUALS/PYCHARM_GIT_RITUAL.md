# PyCharm Git Ritual

A standardized workflow for using PyCharm's Git integration within the Black Ops Lab.

---

## Purpose

Ensure consistent, traceable version control practices when developing experiments and tooling in PyCharm.

---

## Pre-Commit Checklist

1. **Review Changes**
   - Open the Git tool window (Alt+9 / Cmd+9)
   - Double-click each changed file to review diffs
   - Verify no secrets, credentials, or PII are included

2. **Run Tests**
   - Execute relevant test suite before committing
   - Ensure no regressions introduced

3. **Update Documentation**
   - If code changes affect behavior, update relevant docs
   - Add inline comments for non-obvious logic

---

## Commit Message Format

```
[SCOPE] Short description (imperative mood)

- Detail 1
- Detail 2

Refs: #issue-number or experiment-name
SWARM-HS: [phase] if part of a handshake
```

### Scopes

- `feat` – New feature or capability
- `fix` – Bug fix
- `docs` – Documentation only
- `refactor` – Code restructuring
- `test` – Adding or updating tests
- `infra` – Infrastructure changes
- `exp` – Experiment-related changes

### Example

```
[feat] Add lease churn analyzer for GKE audit logs

- Parses lease events from raw audit JSON
- Calculates churn rate over configurable windows
- Outputs to logs/derived/lease_activity.csv

Refs: 2024-01-15_lease-analysis
SWARM-HS: ACK
```

---

## Branch Naming

```
[type]/[experiment-or-feature-name]
```

- `exp/lease-churn-analysis`
- `feat/swarm-cli-init`
- `fix/parser-timeout-handling`

---

## Post-Commit Actions

1. **Push to Remote**
   - Push immediately after local commit
   - Enable "Push after commit" in PyCharm settings

2. **Link to Experiment**
   - Update experiment's `diffs.md` with commit hash
   - Note any deviations from original plan

3. **Notify Swarm**
   - Post commit summary to appropriate Discord channel
   - Use `gl2discord.sh` for automated notifications

---

## Conflict Resolution

1. **Fetch Before Push**
   - Always fetch latest before pushing
   - PyCharm: VCS → Git → Fetch

2. **Resolve Locally**
   - Use PyCharm's merge tool for conflicts
   - Test thoroughly after resolution

3. **Document Conflicts**
   - If conflict arose from parallel SWARM-HS, log it
   - Include in experiment findings

---

## Git Hooks (Recommended)

Configure in `.git/hooks/`:

- **pre-commit**: Run linters, check for secrets
- **commit-msg**: Validate message format
- **post-commit**: Log to experiment registry

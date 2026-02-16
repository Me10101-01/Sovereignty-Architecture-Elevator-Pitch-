# Experiment Template

Use this template to document each mission in the Black Ops Lab.

---

## Experiment: [EXPERIMENT-NAME]

**Date**: YYYY-MM-DD  
**Operator**: [Your name/handle]  
**Agents**: [List AI agents involved]  
**Status**: [ ] Planning | [ ] In Progress | [ ] Complete | [ ] Archived

---

## Context

### What are we testing?

[Describe the hypothesis or capability being explored]

### Why does this matter?

[Explain the strategic value or problem being solved]

### Baseline State

[Document the current state before the experiment]

---

## Inputs

### Raw Data

- [ ] Logs: `logs/raw_gke_audit/[filename]`
- [ ] Configs: [list any config files]
- [ ] Snapshots: [heap dumps, screenshots, etc.]

### Constraints

- [What's in-scope]
- [What's off-limits]
- [Resource limitations]

---

## SWARM-HS Log

### SYN (Capture)

**Timestamp**: 
**Sender**: human

```
[Paste the initial prompt/context sent to agent]
```

### SYN-ACK (Proposal)

**Timestamp**: 
**Sender**: [agent-name]

```
[Paste agent's proposal/understanding]
```

### ACK (Execute)

**Timestamp**: 
**Sender**: human

```
[Approval and any modifications]
```

### FIN (Observe)

**Timestamp**: 
**Sender**: [agent-name]

```
[Summary of changes applied and observations]
```

---

## Outputs

### Artifacts Created

- [ ] Code: `src/[path]`
- [ ] Data: `logs/derived/[filename]`
- [ ] Docs: [any documentation updates]

### Commits

| Commit Hash | Description |
|-------------|-------------|
| `abc1234`   | [Brief description] |

### Metrics

| Metric | Before | After |
|--------|--------|-------|
| [metric-name] | [value] | [value] |

---

## Findings

### What Worked

- [Success 1]
- [Success 2]

### What Didn't Work

- [Failure 1 and why]
- [Failure 2 and why]

### Unexpected Discoveries

- [Surprise finding]

---

## Next Steps

- [ ] [Follow-up task 1]
- [ ] [Follow-up task 2]
- [ ] [New experiment triggered]

---

## Notes

[Any additional context, links, or observations]

# Experiments Directory

This directory contains documentation for each experiment conducted in the Black Ops Lab.

## Structure

Each experiment gets its own folder:

```
YYYY-MM-DD_experiment-name/
├─ context.md      - What we're testing and why
├─ prompt_log.md   - Key prompts used with AI agents
├─ diffs.md        - Summary of code/infra changes
└─ findings.md     - What we learned
```

## Creating a New Experiment

1. Copy the template:
```bash
cp ../EXPERIMENT_TEMPLATE.md YYYY-MM-DD_experiment-name/context.md
```

2. Or use the CLI:
```bash
swarm_lab_cli experiment new --name "experiment-name"
```

3. Fill in the context and start the SWARM-HS loop

## Experiment Registry

All experiments should be registered in:
`src/experiments/experiment_registry.json`

## Completed Experiments

*(None yet - start your first experiment!)*

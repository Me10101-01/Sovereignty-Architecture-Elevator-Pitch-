# Black Ops Lab

**Version:** 1.0
**Status:** Canonical
**Author:** Sovereignty Swarm Intelligence Collective

---

## Purpose

The Black Ops Lab is the experimental zone within the Sovereignty Architecture. It is where new agent capabilities, coordination patterns, and analysis techniques are tested before being promoted to production.

---

## Philosophy

> "Every breakthrough starts as an experiment. Every experiment deserves a safe place to fail."

The lab exists to:
1. **Isolate Risk** - Experiments can't break production
2. **Enable Discovery** - Agents can explore without fear
3. **Preserve Evidence** - All trials are recorded
4. **Accelerate Learning** - Fast feedback loops

---

## Lab Structure

```
data/experiments/
├── <timestamp>_<experiment-name>/
│   ├── context.md           # Input context and goals
│   ├── experiment_log.md    # Phase-by-phase record
│   ├── artifacts/           # Generated files
│   ├── results.yaml         # Structured outcomes
│   └── conclusions.md       # What we learned
```

---

## Experiment Lifecycle

### 1. Hypothesis

Define what you're testing:
- What question are you answering?
- What do you expect to happen?
- How will you measure success?

```yaml
hypothesis:
  question: "Can Claude generate valid sovereignty analyzers from natural language?"
  expected: "80% of generated code passes lint and basic tests"
  metrics:
    - lint_pass_rate
    - test_coverage
    - human_approval_rate
```

### 2. Setup

Prepare the isolated environment:
- Copy relevant context files
- Initialize experiment directory
- Record starting conditions

```bash
python src/main.py experiment --name "claude-analyzer-gen" --context input.md
```

### 3. Execution

Run the SWARM-HS loop within the experiment:
- Agents operate with full handshake protocol
- All phases are logged to `experiment_log.md`
- Mutations stay within the experiment directory

### 4. Analysis

Examine what happened:
- Compare outcomes to hypothesis
- Identify unexpected behaviors
- Extract patterns

### 5. Conclusion

Document learnings:
- What worked?
- What failed?
- What should change in the architecture?

---

## The Particle Collider

The **ParticleCollider** class in `src/experiments/` is the engine that:

1. Creates experiment containers
2. Scaffolds the logging structure
3. Coordinates agent execution
4. Collects and formats results

```python
from experiments import ParticleCollider

collider = ParticleCollider()
experiment = collider.create_experiment(
    name="swarm-grammar-test",
    context_file="docs/sample_input.md"
)

# Manually run agents or automate
experiment.log_phase("SYN", agent="claude-v1", details="...")
experiment.log_phase("SYN-ACK", agent="controller", details="...")
# ...

experiment.finalize()
```

---

## Experiment Types

### Type A: Agent Capability Tests
Test what a single agent can do:
- Code generation quality
- Analysis accuracy
- Decision-making patterns

### Type B: Coordination Tests
Test how multiple agents work together:
- Handshake compliance
- Conflict resolution
- Information sharing

### Type C: Architecture Stress Tests
Test system limits:
- Many agents, one resource
- Rapid handshake churn
- Edge case inputs

### Type D: Pattern Discovery
Explore new possibilities:
- Novel grammar patterns
- Emergent behaviors
- Unexpected synergies

---

## Safety Boundaries

### Isolated File System
Experiments write to `data/experiments/` only. No access to:
- Production code
- Configuration files
- Secrets

### Time Limits
Experiments have deadlines:
- Prevent runaway processes
- Force conclusion writing
- Enable fair resource sharing

### Review Gates
Before any experiment result becomes production:
- Human review required
- Automated lint/test checks
- Security scan

---

## Recording Standards

Every experiment must record:

```yaml
# results.yaml
experiment_id: "2025-01-15_swarm-test-001"
status: "completed|failed|aborted"
duration_seconds: 3600
phases_executed:
  - name: "SYN"
    completed: true
  - name: "SYN-ACK"
    completed: true
  - name: "DATA"
    completed: true
metrics:
  code_lines_generated: 150
  tests_passed: 8
  tests_failed: 2
  human_approval: "pending"
artifacts:
  - path: "artifacts/generated_analyzer.py"
    type: "code"
  - path: "artifacts/test_results.json"
    type: "data"
```

---

## Integration with Main System

### Promoting Experiments

When an experiment succeeds and is approved:

```bash
# Move artifact to production location
cp data/experiments/2025-01-15_swarm-test-001/artifacts/generated_analyzer.py \
   src/analyzers/new_analyzer.py

# Record provenance
echo "Promoted from experiment 2025-01-15_swarm-test-001" >> src/analyzers/new_analyzer.py
```

### Learning from Failures

Failed experiments are as valuable as successful ones:
- What assumption was wrong?
- What edge case wasn't handled?
- What should the grammar include?

---

## CLI Commands

```bash
# Create a new experiment
python src/main.py experiment --name "my-test" --context input.md

# List all experiments
python src/main.py experiment --list

# View experiment status
python src/main.py experiment --status 2025-01-15_my-test

# Archive completed experiment
python src/main.py experiment --archive 2025-01-15_my-test
```

---

## For LLM Agents

When you're asked to run an experiment:

1. **Check**: Am I in experiment mode? (Look for session ID starting with `exp-`)
2. **Write**: All outputs go to the experiment directory
3. **Log**: Use the experiment_log.md, not stdout
4. **Clean**: Leave the experiment directory in a reviewable state
5. **Conclude**: Always write conclusions.md, even if you failed

---

## Example Experiment Log

```markdown
# Experiment: claude-analyzer-gen

## Hypothesis
Claude can generate a working GKE audit log analyzer from a natural language description.

## Timeline

### 2025-01-15T10:30:00Z - SYN
- Agent: claude-v1
- Intent: Generate analyzer from description

### 2025-01-15T10:30:05Z - SYN-ACK
- Controller: sovereignty-controller
- Granted: Write to experiments/artifacts/

### 2025-01-15T10:30:10Z - ACK
- Agent confirms scope

### 2025-01-15T10:35:00Z - DATA
- Agent submits 150 lines of Python code
- Includes docstrings, type hints, tests

### 2025-01-15T10:35:30Z - APPLY
- Request: Create artifacts/gke_analyzer.py
- Rationale: Implements audit log parsing

### 2025-01-15T10:35:35Z - TRACE
- Action completed
- Duration: 5 minutes 35 seconds
- Outcome: Success

## Results
- Lint: PASS
- Tests: 8/10 PASS
- Human review: PENDING

## Conclusions
The generated code is high quality but misses edge cases around malformed timestamps.
Recommend adding timestamp validation to the grammar patterns.
```

---

*The Black Ops Lab is where the future of sovereignty is forged. Experiment boldly, record faithfully, learn relentlessly.*

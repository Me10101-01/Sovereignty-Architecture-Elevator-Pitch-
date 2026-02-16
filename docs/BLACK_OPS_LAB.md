# Sovereign Black Ops Lab

A contained, high-intensity experiment environment for the Strategickhaos swarm.

This lab exists to:

- Stress-test the **Swarm Handshake (SWARM-HS)** methodology.
- Analyze real cluster telemetry (GKE audit logs, leases, autoscaler noise).
- Let AI agents (GPT, Claude, Copilot) propose, implement, and refine tooling.
- Keep everything **ethical, observable, and reversible**.

---

## Principles

1. **Containment**
   - All experiments live in their own namespace / project.
   - No production traffic, no customer data, no real targets.

2. **Total Observability**
   - Every experiment captures:
     - raw logs
     - parsed features
     - AI prompts & outputs
     - resulting diffs / PRs

3. **Swarm Handshake**
   - Experiments follow the SWARM-HS loop:

     1. Capture trace (logs, HTML, heap snapshot).
     2. Send to an AI agent with clear intent.
     3. Receive code / rituals / infra changes.
     4. Apply in lab environment.
     5. Observe new telemetry and repeat.

4. **Ethical Red Teaming Only**
   - We simulate attackers, never become them.
   - Targets are **owned by us and isolated**.
   - Anything that could be harmful outside this lab doesn't leave the lab.

---

## Experiment Lifecycle

Each experiment gets its own folder under `docs/experiments/`:

- `YYYY-MM-DD_experiment-name/`
  - `context.md` – what we're testing and why
  - `prompt_log.md` – key prompts used with agents
  - `diffs.md` – summary of code/infra changes
  - `findings.md` – what we learned

Use `docs/EXPERIMENT_TEMPLATE.md` as the baseline.

---

## Agents Involved

- **GPT-5.1** – Mind: methodology, architecture, naming, protocols.
- **Claude Code** – Hands: repo surgery, parsers, CLIs, PR branches.
- **Copilot Agents** – Factory: background PRs, build fixes, glue code.

The Black Ops Lab is where they all collide under human supervision.

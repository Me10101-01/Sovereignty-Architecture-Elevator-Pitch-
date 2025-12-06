# 🧠 Sovereign Differential Engine

A multi-agent, House M.D.-style thought refinement system for iterative cognitive externalization and conceptual architecture evolution.

## 💠 What Is This?

The **Sovereign Differential Engine** is a structured cognitive scaffolding system that:

- **Externalizes thought** — Takes raw, intuitive, symbolic ideas
- **Mirrors it back** — Multiple AI agents generate structured hypotheses
- **Challenges it** — Each agent challenges hypotheses from their domain perspective
- **Tests it** — Confidence scores are updated based on challenges
- **Refines it** — Hypotheses evolve through iterative refinement
- **Evolves it** — Final conceptual architecture emerges from convergence

This is **NOT** psychoanalysis or therapy. It's:
- ✅ Pattern recognition, not diagnosis
- ✅ Cognitive debugging, not therapy
- ✅ Architecture analysis, not psychoanalysis
- ✅ Structural cognition, not mental health treatment

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SOVEREIGN DIFFERENTIAL ENGINE                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────────────────────────────────┐  │
│  │  Raw Thought │───▶│           HYPOTHESIS BOARD                │  │
│  └──────────────┘    │                                          │  │
│                      │  ┌─────────┐ ┌─────────┐ ┌─────────┐    │  │
│                      │  │ Hypo 1  │ │ Hypo 2  │ │ Hypo 3  │    │  │
│                      │  │ (0.65)  │ │ (0.72)  │ │ (0.58)  │    │  │
│                      │  └────┬────┘ └────┬────┘ └────┬────┘    │  │
│                      └───────┼───────────┼───────────┼──────────┘  │
│                              │           │           │              │
│  ┌───────────────────────────▼───────────▼───────────▼─────────┐   │
│  │                      AGENT TEAM                              │   │
│  │                                                              │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │   │
│  │  │ Structural  │  │  Pattern    │  │   Skeptic   │         │   │
│  │  │  Analyst    │  │ Recognizer  │  │             │         │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘         │   │
│  │                                                              │   │
│  │  ┌─────────────┐  ┌─────────────┐                           │   │
│  │  │ Synthesizer │  │Implementation│                           │   │
│  │  │             │  │ Strategist  │                           │   │
│  │  └─────────────┘  └─────────────┘                           │   │
│  │                                                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  REFINED ARCHITECTURE                         │  │
│  │                                                               │  │
│  │  • Core Concepts (with confidence scores)                    │  │
│  │  • Evolution Graph                                           │  │
│  │  • Insights                                                  │  │
│  │  • Next Steps                                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 🎯 The House M.D. Differential Method

Just like House's diagnostic team, the engine operates in phases:

| House M.D. | Sovereign Differential Engine |
|------------|------------------------------|
| Present symptom | Externalize raw thought |
| Generate hypotheses | Agents generate structured hypotheses |
| Fight with hypothesis | Agents challenge each other |
| Gather new data | Track challenges, update confidence |
| Update hypothesis | Refine and evolve hypotheses |
| Converge on truth | Synthesize final architecture |

**Key difference:** The "patient" isn't you — it's your **idea architecture**.

## 🚀 Quick Start

### Using the API

```bash
# Quick one-shot differential
curl -X POST http://localhost:8086/differential \
  -H "Content-Type: application/json" \
  -d '{
    "thought": "I want to build a recursive swarm-based idea evolution engine using multi-agent cognitive externalization"
  }'
```

### Step-by-step (for complex thoughts)

```bash
# 1. Create a session
curl -X POST http://localhost:8086/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "thought": "My system feels like psychoanalysis but its actually pattern-surfacing and mental-model refinement using multiple AI agents"
  }'

# Response: { "session_id": "abc-123", "status": "created" }

# 2. Run the differential
curl -X POST http://localhost:8086/sessions/abc-123/run

# 3. Get results
curl http://localhost:8086/sessions/abc-123
```

### View hypotheses and evolution

```bash
# Get the hypothesis board
curl http://localhost:8086/sessions/abc-123/hypotheses

# Get the evolution graph
curl http://localhost:8086/sessions/abc-123/evolution
```

## 🤖 The Agent Team

### 1. Structural Analyst
- **Role:** Architect
- **Domain:** System Design
- **Focus:** Identifies patterns, structures, and architectural blueprints
- **Challenge style:** "What is the structural coherence? Does this pattern scale?"

### 2. Pattern Recognizer
- **Role:** Analyst
- **Domain:** Pattern Recognition
- **Focus:** Finds recurring themes, metaphors, and conceptual connections
- **Challenge style:** "Is this pattern consistent across contexts?"

### 3. Skeptic
- **Role:** Critic
- **Domain:** Critical Analysis
- **Focus:** Challenges assumptions, identifies potential flaws
- **Challenge style:** "What evidence contradicts this? What are we missing?"

### 4. Synthesizer
- **Role:** Integrator
- **Domain:** Synthesis
- **Focus:** Combines insights from other agents into coherent conclusions
- **Challenge style:** "How does this integrate with other perspectives?"

### 5. Implementation Strategist
- **Role:** Planner
- **Domain:** Implementation
- **Focus:** Identifies actionable implementation paths
- **Challenge style:** "Is this implementable? What are the concrete first steps?"

## 📊 Output Structure

The engine produces a rich output:

```json
{
  "session_id": "uuid",
  "status": "completed",
  "result": {
    "id": "uuid",
    "original_thought": "Your raw input",
    
    "refined_architecture": {
      "name": "Refined Conceptual Architecture",
      "domains": ["system_design", "pattern_recognition", ...],
      "core_concepts": [
        {
          "concept": "Structural pattern: Multi-Agent System",
          "confidence": 0.82,
          "domain": "system_design"
        }
      ],
      "structure": {
        "type": "multi-domain synthesis",
        "coherence_score": 0.78
      }
    },
    
    "hypotheses": {
      "total_generated": 15,
      "accepted": 5,
      "rejected": 3,
      "top_hypotheses": [...]
    },
    
    "process": {
      "rounds_completed": 2,
      "phases": [...],
      "total_duration_ms": 4523,
      "agents_participated": [...]
    },
    
    "evolution_graph": {
      "nodes": [...],
      "edges": [...]
    },
    
    "insights": [
      {
        "type": "pattern",
        "content": "Your thinking spans 3 domains: system_design, pattern_recognition, implementation"
      }
    ],
    
    "next_steps": [
      {
        "action": "Implement: Agent Orchestration",
        "complexity": "high",
        "components": ["agent framework", "message bus", "state management"]
      }
    ]
  }
}
```

## 🔧 Configuration

In `discovery.yml`:

```yaml
differential:
  enabled: true
  port: 8086
  maxRounds: 3
  convergenceThreshold: 0.8
  minConfidence: 0.5
  agents:
    team:
      - name: "Structural Analyst"
        role: "architect"
        domain: "system_design"
      # ... more agents
    orchestration:
      strategy: "parallel_challenge_reduce"
      enable_evolution: true
  discord:
    announce_channel: "#agents"
    notify_events:
      - "session_created"
      - "differential_complete"
```

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/differential` | Quick one-shot differential |
| POST | `/sessions` | Create new session |
| POST | `/sessions/:id/run` | Run differential on session |
| GET | `/sessions` | List all sessions |
| GET | `/sessions/:id` | Get session status |
| GET | `/sessions/:id/hypotheses` | Get hypothesis board |
| GET | `/sessions/:id/evolution` | Get evolution graph |
| GET | `/agents` | List available agents |
| GET | `/events` | Get event log |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

## 🚦 Running the Engine

```bash
# Development mode
npm run differential

# Or directly
node src/differential/orchestrator.js

# With custom port
DIFFERENTIAL_PORT=8090 node src/differential/orchestrator.js
```

## 🔗 Integration with Discord Bot

Add the `/differential` command to your bot:

```javascript
// In bot.ts, add command handler:
else if (i.commandName === "differential") {
  const thought = i.options.getString("thought", true);
  
  const response = await fetch("http://localhost:8086/differential", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ thought })
  }).then(r => r.json());
  
  await i.reply({
    embeds: [embed(
      "🧠 Differential Complete",
      `Analyzed across ${response.result.process.agents_participated.length} agents\n` +
      `Top insight: ${response.result.insights[0]?.content}`
    )]
  });
}
```

## 💡 Use Cases

### 1. Idea Refinement
```bash
curl -X POST http://localhost:8086/differential \
  -d '{"thought": "I want to build an AI that helps me think better"}'
```

### 2. Architecture Analysis
```bash
curl -X POST http://localhost:8086/differential \
  -d '{"thought": "Microservices vs monolith for a real-time collaboration platform"}'
```

### 3. Pattern Discovery
```bash
curl -X POST http://localhost:8086/differential \
  -d '{"thought": "The same loop appears in my code, my thinking, and my team dynamics"}'
```

### 4. Decision Making
```bash
curl -X POST http://localhost:8086/differential \
  -d '{"thought": "Should I use Kubernetes or serverless for my ML pipeline"}'
```

## 🧪 Programmatic Usage

```javascript
import { SovereignDifferentialEngine, runDifferential } from './src/differential/index.js';

// Quick usage
const result = await runDifferential(
  "Build a cognitive scaffolding system",
  { maxRounds: 2 }
);

console.log(result.insights);
console.log(result.next_steps);

// Full control
const engine = new SovereignDifferentialEngine({ maxRounds: 3 });
const sessionId = await engine.createSession("My complex thought...");
const output = await engine.runDifferential(sessionId);
```

## 📈 Observability

### Prometheus Metrics

```
differential_sessions_total{status="active"}
differential_sessions_total{status="completed"}
differential_agents_count
differential_events_total
```

### Event Log

Track all engine events:
```bash
curl http://localhost:8086/events?sessionId=abc-123
```

## 🔐 Security Notes

- The engine processes thoughts locally
- No data is sent to external services unless you configure AI agents with OpenAI
- All sessions are in-memory by default (no persistence)
- Add authentication for production deployments

## 🤝 Philosophy

> "You're not psychoanalyzing yourself —
> **you're running a recursive swarm-based idea evolution engine.**
> 
> And damn… you do it better than most research labs."

The Sovereign Differential Engine embodies:

- **Iterative Cognitive Externalization** — Make thinking visible
- **Multi-Agent Differential Refinement** — Challenge from all angles
- **Structural Cognition** — Pattern-first, architecture-aware
- **Sovereignty** — Your ideas, your engine, your evolution

---

*Built with 🔥 by the Strategickhaos Swarm Intelligence collective*

*"They're not working for you. They're dancing with you. And the music is never going to stop."*

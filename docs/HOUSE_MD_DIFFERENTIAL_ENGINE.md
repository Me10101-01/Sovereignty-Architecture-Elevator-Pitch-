# House M.D. Differential Engine

**Multi-Agent Psychoanalysis Through Structured Debate**

---

## The Vision

Like Gregory House's diagnostic team, this system enables multiple AI "specialists" to:

1. **Receive raw input** (your unstructured thoughts)
2. **Analyze from different perspectives** (each agent has a specialty)
3. **Challenge each other's conclusions** (structured debate rounds)
4. **Synthesize a refined understanding** (evolved output)

---

## The Team

### Dr. House (The Synthesizer)
- **Role**: Pattern recognition, contrarian insights, final synthesis
- **Token Signature**: "Everyone's wrong. Here's why...", "What if we're looking at this backwards?"
- **Function**: Sees what others miss, makes the final call

### Dr. Foreman (The Structuralist)
- **Role**: Systematic categorization, logical framework
- **Token Signature**: "Let's break this down systematically...", numbered lists
- **Function**: Creates order from chaos, identifies structure

### Dr. Cameron (The Humanist)
- **Role**: Intent interpretation, values alignment
- **Token Signature**: "But what are you really trying to achieve?", "The deeper purpose here is..."
- **Function**: Finds the emotional core, protects human values

### Dr. Chase (The Pragmatist)
- **Role**: Actionable translation, implementation focus
- **Token Signature**: "Okay, but what can we actually build?", "The next concrete step is..."
- **Function**: Grounds ideas in reality, creates action items

### Dr. Wilson (The Devil's Advocate)
- **Role**: Risk assessment, counterpoint generation
- **Token Signature**: "Have you considered that this might fail...", "The blind spot here is..."
- **Function**: Stress tests ideas, prevents disasters

---

## The Debate Protocol

### Phase 1: Case Presentation

The "patient" (your raw thoughts) is presented to all specialists.

```
INPUT: Your unstructured thoughts, ideas, problems

CASE PRESENTATION:
"Patient presents with [summary of raw input]"
"Initial symptoms: [key patterns identified]"
"History: [context from previous sessions]"
```

### Phase 2: Initial Hypotheses

Each specialist generates their initial analysis.

```
FOREMAN: "Structurally, I see three distinct components..."
CAMERON: "The underlying intent seems to be..."
CHASE: "Practically, this could be implemented as..."
WILSON: "The risks I see are..."
HOUSE: "You're all missing the obvious..."
```

### Phase 3: Cross-Examination

Specialists challenge each other's conclusions.

```
CHASE → FOREMAN: "Your structure ignores implementation constraints"
WILSON → CAMERON: "Your idealism could lead to scope creep"
FOREMAN → HOUSE: "Your pattern recognition lacks rigor"
CAMERON → WILSON: "Your pessimism stifles innovation"
HOUSE → ALL: "You're arguing about symptoms, not the disease"
```

### Phase 4: Synthesis

House synthesizes all perspectives into a refined diagnosis.

```
DIAGNOSIS: What the idea actually is
PROGNOSIS: Where it's headed
TREATMENT: What to do next
CONTRAINDICATIONS: What to avoid
```

---

## Output Format

### Session Record

```markdown
# Differential Session: [Timestamp]

## Patient Presentation
[Original input]

## Specialist Analyses

### Foreman (Structure)
[Analysis]

### Cameron (Intent)
[Analysis]

### Chase (Action)
[Analysis]

### Wilson (Risk)
[Analysis]

## Cross-Examination
[Key challenges and responses]

## House Synthesis

### Diagnosis
[Core insight]

### Prognosis
[Likely evolution]

### Treatment Plan
[Recommended actions]

### Contraindications
[Things to avoid]

## Evolution Delta
- Pattern strength: [Before → After]
- Clarity: [Before → After]
- Actionability: [Before → After]
```

---

## Implementation Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    SOVEREIGN OPERATOR                       │
│                   (You, the controller)                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 DIFFERENTIAL ENGINE                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              DEBATE ORCHESTRATOR                    │    │
│  │  • Controls debate flow                             │    │
│  │  • Manages turn-taking                              │    │
│  │  • Tracks evolution metrics                         │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                  │
│     ┌─────────────────────┼─────────────────────┐           │
│     ▼                     ▼                     ▼           │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐          │
│  │HOUSE │  │FOREMAN│ │CAMERON│ │CHASE │  │WILSON│          │
│  │      │  │       │ │       │ │      │  │      │          │
│  │Synth-│  │Struct-│ │Human- │ │Pragma│  │Devil │          │
│  │esizer│  │uralist│ │ist    │ │tist  │  │Advoc │          │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘          │
│      │         │         │         │         │              │
│      └─────────┴─────────┴─────────┴─────────┘              │
│                          │                                  │
│                          ▼                                  │
│              ┌─────────────────────┐                        │
│              │   SESSION STORE     │                        │
│              │  (Markdown files)   │                        │
│              └─────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. Raw Input → Case Presentation
2. Case → Parallel Specialist Analysis
3. Analyses → Cross-Examination Rounds
4. Challenges → Response Generation
5. All Perspectives → House Synthesis
6. Synthesis → Session Record
7. Record → Storage & Copy/Paste Export
```

---

## Usage Patterns

### Pattern 1: Idea Refinement

```bash
python src/main.py diagnose --input "I want to build a system that..."
```

Output: Refined, multi-perspective analysis of your idea.

### Pattern 2: Decision Support

```bash
python src/main.py diagnose --input "Should I do X or Y?"
```

Output: Structured pro/con analysis with synthesis.

### Pattern 3: Problem Diagnosis

```bash
python src/main.py diagnose --input "This thing keeps failing because..."
```

Output: Root cause analysis with treatment plan.

### Pattern 4: Strategic Planning

```bash
python src/main.py diagnose --file strategy.txt --interactive
```

Output: Iterative strategy refinement with debate.

---

## Evolution Mechanics

### Session Chaining

Each session builds on previous ones:

```
Session 1: Raw idea → Initial diagnosis
Session 2: Refined idea → Deeper analysis
Session 3: Evolved idea → Implementation plan
...
Session N: Mature concept → Execution blueprint
```

### Pattern Strengthening

As you iterate:
- Token signatures become more distinct
- Specialist voices become more differentiated
- Synthesis quality improves
- Actionability increases

### Cross-Pollination

Insights from one domain can seed analysis in another:

```
Domain A Session → Extracted patterns
Patterns → Seed for Domain B Session
Domain B Session → Novel insights
Novel insights → Enrich Domain A
```

---

## The Meta-Level

This system isn't just for analyzing ideas.
It's for **analyzing your own thinking**.

The debate between specialists mirrors:
- Your internal debates
- Your competing priorities
- Your blind spots
- Your unspoken assumptions

By externalizing this process, you:
- See your own patterns more clearly
- Identify your cognitive biases
- Strengthen your weak perspectives
- Evolve your thinking systematically

---

## Getting Started

1. **Install dependencies**: Python 3.10+
2. **Run a diagnosis**: `python src/main.py diagnose --input "your thoughts"`
3. **Review session**: Check `data/sessions/` for markdown output
4. **Iterate**: Use session output as input for next round
5. **Evolve**: Watch your thinking become more structured

---

## Future Extensions

- **Voice integration**: Speak your thoughts, receive spoken diagnosis
- **Real-time debate**: Watch specialists argue in real-time
- **Custom specialists**: Add domain-specific personas
- **Team mode**: Multiple operators, shared sessions
- **API access**: Integration with external tools

---

*"Everybody lies. But the differential never does."* — Dr. House (probably)

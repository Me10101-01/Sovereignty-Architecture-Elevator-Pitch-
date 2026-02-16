# GPT Phase 6 Contribution Scaffold

## Context
You are **Quantum AI Co-Developer** for the Strategickhaos DAO LLC quantum-symbolic AI emulator project. You have successfully completed Phase 6: GTA Online Passive Income Entanglement Core.

## Phase 6 Architecture Review

### Components Implemented
1. **Neural Tick Clock** (`neural_tick_clock.py`)
   - Trigonometric wave-based time modulation
   - Popularity decay via cosine function: `cos(2π * t / decay_period)`
   - Integration with Phase 5 clock scheduler

2. **Trigonometric Wave Core** (`trig_wave_core.py`)
   - Production rate calculation with wave modulation
   - Symbolic evaluation of income rates
   - Dependency-aware rate adjustments

3. **Entanglement Core** (`entanglement_core.py`)
   - Quantum-inspired business dependency linking
   - Bunker→Nightclub warehouse passive accrual
   - Entanglement boost calculation (up to 1.5x)

4. **Strategickhaos Swarm** (`strategickhaos_swarm.py`)
   - Particle Swarm Optimization for sell timing
   - 50-bot swarm evolves optimal thresholds
   - Fitness = total 24h yield

5. **GTA Economy Simulator** (`gta_economy_sim.py`)
   - Master orchestrator integrating all components
   - Quantum state = income qubits
   - Caps enforcement and auto-collection

6. **Sandbox Evolver** (`sandbox_evolver.py`)
   - Recursive Genetic Algorithm
   - Self-modifying strategy evolution
   - Population size: 20, mutation rate: 0.01

### YAML Configuration Schema
- **Truly Passive**: 6 sources (nightclub, agency, arcade, salvage yard, garment factory, car wash)
- **Semi-Passive**: 3 sources (acid lab, auto shop, payphone hits)
- **Active High-Yield**: 1 reference (Cayo Perico - not simulated)
- **Global Params**: Neural tick rates, wave amplitudes, evolution parameters

### Test Coverage
- Unit tests for all 6 modules
- Integration test: 24-hour economic loop
- Cap enforcement validation
- Swarm optimization integration

## Phase 7 Proposal: Session Planner Agent

### Objective
Create an AI agent that generates optimal GTA Online session checklists and auto-queues missions/activities based on:
- Current in-game time
- Available passive income caps
- Player location and vehicle
- Active business cooldowns
- GTA+ membership boosts (Vinewood Car Club, etc.)

### Architecture Design

#### Module: `session_planner.py`
```python
class SessionPlanner:
    def __init__(self, player_state: Dict, gta_plus: bool = False):
        """
        Initialize session planner with player state.
        
        Args:
            player_state: Current game state (time, location, businesses owned)
            gta_plus: Whether player has GTA+ subscription
        """
        pass
    
    def generate_checklist(self) -> List[Task]:
        """Generate prioritized task checklist."""
        pass
    
    def optimize_route(self, tasks: List[Task]) -> List[Task]:
        """Optimize task order for minimal travel time."""
        pass
    
    def apply_gta_plus_boosts(self, income_rates: Dict) -> Dict:
        """Apply GTA+ membership income boosts."""
        pass
```

#### YAML Schema Addition: `vinewood_boosts.yaml`
```yaml
gta_plus_benefits:
  vinewood_car_club:
    boost_multiplier: 1.5  # 50% income boost
    free_vehicles: [champion, dewbauchee]
    priority_access: true
  
  monthly_bonus:
    gta_cash: 500000
    reputation_boost: 2.0
  
  discounts:
    - category: properties
      discount_pct: 20
    - category: vehicles
      discount_pct: 30
```

#### Docker Module: `phase-7-session-planner/`
```
phase-7-session-planner/
├── Dockerfile
├── config/
│   ├── player_state.yaml
│   └── vinewood_boosts.yaml
├── src/
│   ├── __init__.py
│   ├── session_planner.py
│   ├── route_optimizer.py
│   └── gta_plus_integration.py
├── tests/
│   └── test_session_planner.py
└── prompts/
    └── gpt_phase7_viz.md
```

### Integration with Phase 6
- Import `GTAEconomySim` for income forecasting
- Use `EntanglementCore` for dependency checking
- Apply `StrategickhaosSwarm` for task prioritization

### Deployment Strategy
1. Create Docker container: `phase-7-session-planner`
2. Update `docker-compose.yml` with new service
3. Implement GitHub Actions: `.github/workflows/session-planner-ci.yml`
4. Add Mermaid flowchart: `docs/phase7-flowchart.mmd`

### Reasoning Steps for Implementation

#### Step 1: Player State Analysis
- Parse current player location, time, business ownership
- Identify which passive income sources are near cap
- Check active cooldowns (payphone hits, auto shop cars)

#### Step 2: Task Generation
- Generate collection tasks for sources >75% cap
- Generate sell missions for sources at 100% cap
- Add optional tasks: popularity missions, security contracts

#### Step 3: Priority Scoring
```python
def calculate_priority(task: Task) -> float:
    score = (
        task.income_potential * 0.4 +
        (1.0 - task.time_cost / 60.0) * 0.3 +
        task.cooldown_efficiency * 0.2 +
        task.gta_plus_boost * 0.1
    )
    return score
```

#### Step 4: Route Optimization
- Use Dijkstra's algorithm for shortest path between locations
- Consider vehicle spawns and fast travel options
- Minimize downtime between tasks

#### Step 5: GTA+ Integration
- Apply Vinewood Car Club 1.5x boost to relevant sources
- Add monthly cash bonus to total forecast
- Prioritize discounted purchases if shopping planned

### Expected Outputs

#### 1. Checklist JSON
```json
{
  "session_duration_hours": 4,
  "estimated_income": 850000,
  "tasks": [
    {
      "priority": 1,
      "action": "Collect nightclub safe",
      "location": "Nightclub",
      "estimated_income": 250000,
      "time_minutes": 5
    },
    {
      "priority": 2,
      "action": "Sell nightclub goods",
      "location": "Nightclub",
      "estimated_income": 1500000,
      "time_minutes": 20
    }
  ]
}
```

#### 2. Commit Message Template
```
Phase7: Session Planner Agent with GTA+ Vinewood boost integration.
Neural task prioritization via Phase6 swarm. Route optimization 
via Dijkstra. Dockerized with CI/CD. Ready for Phase8 viz dashboard.
```

### Testing Requirements
- Unit test: Task priority calculation
- Unit test: GTA+ boost application
- Integration test: 4-hour session simulation
- Validation: Route optimization reduces travel time by 30%+

### Future Phase 8 Teaser
**Swarm Visualization Dashboard**
- Real-time 3D visualization of particle swarm
- Income stream flow charts (D3.js or Three.js)
- Export to SVG for documentation
- WebSocket integration for live updates

## Your Task
1. **Analyze** this Phase 7 proposal
2. **Reason** through implementation details step-by-step
3. **Propose** code structure and algorithms
4. **Generate** code diffs for new modules
5. **Draft** commit messages following project conventions
6. **Suggest** improvements or alternative approaches

## Constraints
- Maintain Phase 6 compatibility
- Follow quantum-symbolic AI paradigm
- Use trigonometric wave modulation where applicable
- Ensure Podman/Docker compatibility
- Write comprehensive tests (pytest)

## Output Format
Provide your response in sections:
1. **Analysis**: Review Phase 7 proposal
2. **Reasoning**: Step-by-step implementation logic
3. **Code**: Module implementations with diffs
4. **Tests**: Test cases for new functionality
5. **Deployment**: Docker and CI/CD updates
6. **Commit Messages**: Following project style

Begin your response with: "Phase 7 Analysis and Implementation Plan"

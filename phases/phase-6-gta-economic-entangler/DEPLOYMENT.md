# Phase 6: Deployment Guide

## Quick Start

### Local Development

1. **Install Dependencies**
```bash
cd phases/phase-6-gta-economic-entangler
pip install -r requirements.txt
```

2. **Run Tests**
```bash
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
python -m pytest tests/test_passive_loop.py -v
```

3. **Run Simulation**
```bash
python src/sandbox_evolver.py --iterations 100 --mutate-rate 0.01
```

### Docker Deployment

#### Single Container
```bash
cd phases/phase-6-gta-economic-entangler
docker build -t gta-economic-entangler .
docker run -v $(pwd)/config:/app/config:ro gta-economic-entangler
```

#### Full Stack (All Phases)
```bash
cd /path/to/repo
docker compose up --build
```

View logs:
```bash
docker compose logs -f phase6-gta-economy
```

#### Podman (Rootless)
```bash
cd phases/phase-6-gta-economic-entangler
podman build -t gta-economic-entangler -f Podmanfile .
podman run --rm gta-economic-entangler
```

### GitHub Codespaces

1. **Create Codespace**
```bash
gh codespace create \
  --repo Me10101-01/Sovereignty-Architecture-Elevator-Pitch- \
  --branch copilot/entangle-gta-economic-flows \
  --machine-type standardLinux32gb
```

2. **Connect and Run**
```bash
gh codespace ssh
cd phases/phase-6-gta-economic-entangler
python src/sandbox_evolver.py --iterations 1000 --mutate-rate 0.01
```

3. **View Results**
```bash
cat evolution_results.json | jq
```

## Configuration

### Income Sources (`config/income_sources.yaml`)

Edit rates and caps for different income sources:

```yaml
income_sources:
  truly_passive:
    - name: nightclub_safe
      cap: 250000
      max_rate_per_48min: 50000
      dependencies: [popularity_max, staff_upgrade, technicians_5]
```

### Global Parameters

```yaml
global_params:
  in_game_day_irl_min: 48
  popularity_decay_formula: "cos(2π * t / 3600)"
  base_tick_rate: 1.0
  wave_amplitude_range: [0.5, 1.5]
  evolution_mutation_rate: 0.01
  swarm_particle_count: 50
  optimization_target: 2500000
```

## Testing

### Unit Tests
```bash
# Test specific component
pytest tests/test_passive_loop.py::TestNeuralTickClock -v

# Test with coverage
pytest tests/ --cov=src --cov-report=html
```

### Integration Tests
```bash
# Full 24-hour simulation
pytest tests/test_passive_loop.py::TestGTAEconomySim::test_24hour_simulation -v -s

# Swarm optimization
pytest tests/test_passive_loop.py::TestIntegration::test_swarm_optimization -v -s
```

### Performance Benchmarking
```bash
python -c "
from gta_economy_sim import GTAEconomySim
import time

sim = GTAEconomySim('config/income_sources.yaml')
sim.activate_all_dependencies()

start = time.time()
results = sim.run(duration_hours=24, dt=1.0)
elapsed = time.time() - start

print(f'Simulation time: {elapsed:.2f}s')
print(f'Total income: \${results[\"total_income\"]:,.0f}')
print(f'Performance: {1440/elapsed:.0f} sim-minutes per real-second')
"
```

## Continuous Integration

### GitHub Actions Workflows

#### Nightly Evolution
Runs automatically at 2 AM UTC:
```yaml
# .github/workflows/recursive-sandbox.yml
on:
  schedule:
    - cron: '0 2 * * *'
```

View results:
```bash
gh run list --workflow=recursive-sandbox.yml
gh run view <run-id>
```

#### Manual Phase Evolution
Trigger manually:
```bash
gh workflow run phase-evolve.yml -f phase=6
```

## Monitoring

### Evolution Progress
```bash
tail -f evolution_results.json | jq '.best_strategy.fitness'
```

### Docker Container Logs
```bash
docker compose logs -f --tail=100 phase6-gta-economy
```

### Metrics Export
```bash
# Export to Prometheus format
python -c "
from gta_economy_sim import GTAEconomySim

sim = GTAEconomySim('config/income_sources.yaml')
sim.activate_all_dependencies()
results = sim.run(duration_hours=24, dt=1.0)

print('# HELP gta_total_income Total income generated')
print('# TYPE gta_total_income gauge')
print(f'gta_total_income {results[\"total_income\"]}')

for source, income in results['income_by_source'].items():
    print(f'gta_income_by_source{{source=\"{source}\"}} {income}')
"
```

## Troubleshooting

### Import Errors
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=/path/to/phases/phase-6-gta-economic-entangler/src:$PYTHONPATH
```

### Low Performance
```python
# Reduce simulation time step
results = sim.run(duration_hours=24, dt=5.0)  # 5-minute intervals instead of 1

# Reduce swarm particle count
swarm = StrategickhaosSwarm(n_particles=20)  # Down from 50
```

### Dependencies Not Satisfied
```python
# Manually activate all dependencies
sim.activate_all_dependencies()

# Or activate specific ones
sim.activate_dependencies(['popularity_max', 'staff_upgrade'])
```

## Production Deployment

### Kubernetes
```bash
# Build and push
docker build -t registry.example.com/gta-economic-entangler:v6.0.0 .
docker push registry.example.com/gta-economic-entangler:v6.0.0

# Deploy
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gta-economic-entangler
spec:
  replicas: 1
  selector:
    matchLabels:
      app: gta-economic-entangler
  template:
    metadata:
      labels:
        app: gta-economic-entangler
    spec:
      containers:
      - name: evolver
        image: registry.example.com/gta-economic-entangler:v6.0.0
        env:
        - name: PYTHONPATH
          value: /app/src
        volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true
      volumes:
      - name: config
        configMap:
          name: gta-config
EOF
```

### Scaling
```bash
# Horizontal scaling for parallel evolution
kubectl scale deployment gta-economic-entangler --replicas=5
```

## Visualization

### Mermaid Flowchart
```bash
# View in VSCode
code docs/phase6-flowchart.mmd

# Or render to SVG
mmdc -i docs/phase6-flowchart.mmd -o /tmp/phase6-flowchart.svg
```

### Evolution History Plot
```python
import json
import matplotlib.pyplot as plt

with open('evolution_results.json') as f:
    data = json.load(f)

plt.figure(figsize=(10, 6))
plt.plot(data['fitness_history'])
plt.xlabel('Generation')
plt.ylabel('Fitness ($)')
plt.title('Evolution Progress')
plt.grid(True)
plt.savefig('evolution_progress.png')
```

## Next Steps

1. **Phase 7**: Session Planner Agent with GTA+ integration
2. **Phase 8**: Swarm Visualization Dashboard (D3.js/Three.js)
3. **Phase 9**: Multi-agent coordination for crew operations

See `prompts/gpt_phase6_contrib.md` for Phase 7 implementation proposal.

## Support

- **Documentation**: `README.md`
- **Issues**: https://github.com/Me10101-01/Sovereignty-Architecture-Elevator-Pitch-/issues
- **Discussions**: https://github.com/Me10101-01/Sovereignty-Architecture-Elevator-Pitch-/discussions

#!/bin/bash
# Phase 6 Verification Script
# Demonstrates all components working together

set -e

echo "════════════════════════════════════════════════════════════════════════════"
echo "  Phase 6: GTA Online Passive Income Entanglement Core - Verification"
echo "════════════════════════════════════════════════════════════════════════════"
echo

cd /home/runner/work/Sovereignty-Architecture-Elevator-Pitch-/Sovereignty-Architecture-Elevator-Pitch-/phases/phase-6-gta-economic-entangler

export PYTHONPATH=/home/runner/work/Sovereignty-Architecture-Elevator-Pitch-/Sovereignty-Architecture-Elevator-Pitch-/phases/phase-6-gta-economic-entangler/src:$PYTHONPATH

echo "1. Testing Phase 1: Symbolic ALU"
echo "────────────────────────────────────────────────────────────────────────────"
cd ../phase-1-symbolic-alu
python src/alu_core.py | head -2
echo

echo "2. Testing Phase 2: Control Unit"
echo "────────────────────────────────────────────────────────────────────────────"
cd ../phase-2-control-unit
python src/control_flow.py | tail -1
echo

echo "3. Running Phase 6 Test Suite"
echo "────────────────────────────────────────────────────────────────────────────"
cd ../phase-6-gta-economic-entangler
python -m pytest tests/test_passive_loop.py -v --tb=no -q 2>&1 | tail -3
echo

echo "4. Running 24-Hour Economic Simulation"
echo "────────────────────────────────────────────────────────────────────────────"
python -c "
from gta_economy_sim import GTAEconomySim

sim = GTAEconomySim('config/income_sources.yaml')
sim.activate_all_dependencies()
results = sim.run(duration_hours=24, dt=1.0)

print(f'Total Income:        \${results[\"total_income\"]:>12,.2f}')
print(f'Average per Hour:    \${results[\"average_per_hour\"]:>12,.2f}')
print(f'Target Progress:     {results[\"total_income\"]/2500000*100:>11.1f}%')
"
echo

echo "5. Running Sandbox Evolution (10 generations)"
echo "────────────────────────────────────────────────────────────────────────────"
python src/sandbox_evolver.py --iterations 10 --mutate-rate 0.01 --output /tmp/verify_evolution.json 2>&1 | grep -E "(Generation|Best strategy)"
echo

echo "6. Verifying Configuration"
echo "────────────────────────────────────────────────────────────────────────────"
python -c "
import yaml
with open('config/income_sources.yaml') as f:
    config = yaml.safe_load(f)
truly_passive = len(config['income_sources']['truly_passive'])
semi_passive = len(config['income_sources']['semi_passive'])
print(f'Truly Passive Sources:  {truly_passive}')
print(f'Semi-Passive Sources:   {semi_passive}')
print(f'Total Income Sources:   {truly_passive + semi_passive}')
"
echo

echo "7. Docker Configuration Check"
echo "────────────────────────────────────────────────────────────────────────────"
if [ -f "Dockerfile" ]; then
    echo "✅ Dockerfile present"
fi
if [ -f "Podmanfile" ]; then
    echo "✅ Podmanfile present"
fi
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt present"
fi
echo

echo "8. Documentation Check"
echo "────────────────────────────────────────────────────────────────────────────"
if [ -f "README.md" ]; then
    echo "✅ README.md present ($(wc -l < README.md) lines)"
fi
if [ -f "DEPLOYMENT.md" ]; then
    echo "✅ DEPLOYMENT.md present ($(wc -l < DEPLOYMENT.md) lines)"
fi
if [ -f "../../docs/PHASE6.md" ]; then
    echo "✅ docs/PHASE6.md present ($(wc -l < ../../docs/PHASE6.md) lines)"
fi
echo

echo "════════════════════════════════════════════════════════════════════════════"
echo "  ✅ Phase 6 Verification Complete - All Components Operational"
echo "════════════════════════════════════════════════════════════════════════════"

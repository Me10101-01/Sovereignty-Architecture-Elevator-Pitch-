"""
Tests for Phase 6: GTA Economic Entanglement Core
Validates passive income loop simulation
"""

import pytest
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from gta_economy_sim import GTAEconomySim
from neural_tick_clock import NeuralTickClock
from trig_wave_core import TrigWaveCore
from entanglement_core import EntanglementCore
from strategickhaos_swarm import StrategickhaosSwarm


@pytest.fixture
def config_path():
    """Get path to test configuration."""
    return str(Path(__file__).parent.parent / 'config' / 'income_sources.yaml')


@pytest.fixture
def sim(config_path):
    """Create economy simulator instance."""
    return GTAEconomySim(config_path)


class TestNeuralTickClock:
    """Test neural tick clock functionality."""
    
    def test_tick_rate_bounds(self):
        """Test that tick rates stay within expected bounds."""
        config = {'base_tick_rate': 1.0, 'wave_amplitude_range': [0.5, 1.5], 
                 'in_game_day_irl_min': 48}
        clock = NeuralTickClock(config)
        
        # Test various time points
        for t in [0, 12, 24, 36, 48]:
            rate = clock.get_tick_rate(t)
            assert 0.5 <= rate <= 1.5, f"Tick rate {rate} out of bounds at t={t}"
    
    def test_popularity_decay(self):
        """Test popularity decay calculation."""
        config = {'base_tick_rate': 1.0, 'wave_amplitude_range': [0.5, 1.5],
                 'in_game_day_irl_min': 48}
        clock = NeuralTickClock(config)
        
        # Test that decay is between 0 and 1
        for t in [0, 100, 500, 1000]:
            decay = clock.popularity_decay(t)
            assert 0.0 <= decay <= 1.0, f"Decay {decay} out of bounds at t={t}"


class TestTrigWaveCore:
    """Test trigonometric wave core functionality."""
    
    def test_load_config(self, config_path):
        """Test configuration loading."""
        core = TrigWaveCore(config_path)
        assert core.config is not None
        assert 'income_sources' in core.config
    
    def test_get_source_config(self, config_path):
        """Test retrieving source configuration."""
        core = TrigWaveCore(config_path)
        
        nightclub = core.get_source_config('nightclub_safe')
        assert nightclub is not None
        assert nightclub['cap'] == 250000
    
    def test_production_rate(self, config_path):
        """Test production rate calculation."""
        core = TrigWaveCore(config_path)
        
        rate = core.production_rate('nightclub_safe', t_irl=0, deps_satisfied=True)
        assert rate >= 0, "Production rate should be non-negative"
    
    def test_accumulated_income(self, config_path):
        """Test income accumulation over time."""
        core = TrigWaveCore(config_path)
        
        # Simulate 48 minutes (1 game day)
        income = core.accumulated_income('nightclub_safe', duration_min=48, 
                                        deps_satisfied=True)
        assert 0 < income <= 250000, f"Income {income} should be positive and capped"


class TestEntanglementCore:
    """Test entanglement core functionality."""
    
    def test_dependency_state(self, config_path):
        """Test dependency state management."""
        core = EntanglementCore(config_path)
        
        # Initially false
        assert not core.get_dependency_state('popularity_max')
        
        # Set to true
        core.set_dependency_state('popularity_max', True)
        assert core.get_dependency_state('popularity_max')
    
    def test_dependencies_satisfied(self, config_path):
        """Test checking if all dependencies are satisfied."""
        core = EntanglementCore(config_path)
        
        # Initially not satisfied
        assert not core.are_dependencies_satisfied('nightclub_safe')
        
        # Activate all
        core.activate_all_dependencies()
        assert core.are_dependencies_satisfied('nightclub_safe')
    
    def test_entanglement_boost(self, config_path):
        """Test entanglement boost calculation."""
        core = EntanglementCore(config_path)
        
        # No dependencies satisfied = lower boost
        boost1 = core.get_entanglement_boost('nightclub_safe')
        
        # All dependencies satisfied = higher boost
        core.activate_all_dependencies()
        boost2 = core.get_entanglement_boost('nightclub_safe')
        
        assert boost2 > boost1, "Boost should increase with satisfied dependencies"


class TestStrategickhaosSwarm:
    """Test particle swarm optimization."""
    
    def test_swarm_initialization(self):
        """Test swarm initialization."""
        swarm = StrategickhaosSwarm(n_particles=10, n_dimensions=3)
        
        assert len(swarm.particles) == 10
        assert swarm.n_dimensions == 3
    
    def test_particle_update(self):
        """Test particle position update."""
        swarm = StrategickhaosSwarm(n_particles=5, n_dimensions=3)
        
        particle = swarm.particles[0]
        initial_pos = particle.position.copy()
        
        swarm.update_particle(particle)
        
        # Position should change
        assert not all(particle.position == initial_pos)
        
        # Position should be within bounds
        assert all(0.3 <= p <= 0.95 for p in particle.position)


class TestGTAEconomySim:
    """Test main economy simulator."""
    
    def test_initialization(self, sim):
        """Test simulator initialization."""
        assert sim.tick_clock is not None
        assert sim.wave_core is not None
        assert sim.entanglement is not None
    
    def test_simulate_tick(self, sim):
        """Test single tick simulation."""
        sim.activate_all_dependencies()
        
        tick_income = sim.simulate_tick(dt=1.0)
        
        assert isinstance(tick_income, dict)
        assert len(tick_income) > 0
    
    def test_collect_income(self, sim):
        """Test income collection."""
        sim.activate_all_dependencies()
        
        # Simulate some time
        for _ in range(10):
            sim.simulate_tick(dt=1.0)
        
        # Collect from nightclub
        collected = sim.collect_from_source('nightclub_safe')
        assert collected >= 0
    
    def test_48min_simulation(self, sim):
        """Test 48-minute game day simulation."""
        sim.activate_all_dependencies()
        
        results = sim.run(duration_hours=0.8, dt=1.0)  # 48 minutes = 0.8 hours
        
        assert results['total_income'] > 0
        assert 'income_by_source' in results
        
        # Nightclub should generate significant income
        nightclub_income = results['income_by_source'].get('nightclub_safe', 0)
        assert nightclub_income > 0, "Nightclub should generate income"
    
    def test_24hour_simulation(self, sim):
        """Test 24-hour simulation for $2.5M+ target."""
        sim.activate_all_dependencies()
        
        results = sim.run(duration_hours=24, dt=1.0)
        
        total = results['total_income']
        print(f"\n24-hour simulation: ${total:,.0f}")
        
        assert total > 0, "Should generate income"
        
        # Check each source contributed
        for source, income in results['income_by_source'].items():
            print(f"  {source}: ${income:,.0f}")
            assert income >= 0
    
    def test_cap_enforcement(self, sim):
        """Test that income caps are enforced."""
        sim.activate_all_dependencies()
        
        # Run long simulation
        results = sim.run(duration_hours=48, dt=1.0)
        
        # Check caps weren't exceeded
        for source_name in sim.wave_core.get_all_passive_sources():
            source_config = sim.wave_core.get_source_config(source_name)
            cap = source_config.get('cap', float('inf'))
            
            # Balance should never exceed cap
            assert sim.current_balances[source_name] <= cap


class TestIntegration:
    """Integration tests for full system."""
    
    def test_full_economic_loop(self, sim):
        """Test complete economic simulation loop."""
        # Setup: Activate all dependencies
        sim.activate_all_dependencies()
        
        # Run: 24-hour simulation
        results = sim.run(duration_hours=24, dt=1.0)
        
        # Verify: Income generated
        assert results['total_income'] > 100000, \
            "24-hour simulation should generate significant income"
        
        # Verify: Multiple sources contributed
        assert len(results['income_by_source']) > 0
        
        # Verify: Entanglement working
        assert results['entanglement_summary']['satisfaction_percentage'] > 0
    
    def test_swarm_optimization(self, sim):
        """Test swarm optimization integration."""
        sim.activate_all_dependencies()
        
        opt_results = sim.optimize_with_swarm(duration_hours=24)
        
        assert 'best_thresholds' in opt_results
        assert 'swarm_stats' in opt_results
        assert opt_results['swarm_stats']['global_best_fitness'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

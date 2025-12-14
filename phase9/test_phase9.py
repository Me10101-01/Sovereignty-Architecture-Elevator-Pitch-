#!/usr/bin/env python3
"""
Integration test for Phase 9: Tria Prima Deepening and Hermetic Exploration

Validates that all Phase 9 components work correctly:
- Tria Prima principles are properly deepened
- Hermetic exploration functions correctly
- Precision metrics meet >95% target
- Benchmark results are generated correctly
"""

import os
import sys
import yaml

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

import deepen_tria_explore_hermetic as phase9


def test_tria_prima_definitions():
    """Test that Tria Prima principles are properly defined"""
    print("Testing Tria Prima definitions...")
    assert 'Sulphur' in phase9.tria_prima_deep
    assert 'Mercury' in phase9.tria_prima_deep
    assert 'Salt' in phase9.tria_prima_deep
    
    assert 'Soul/flammability' in phase9.tria_prima_deep['Sulphur']
    assert 'Spirit/volatility' in phase9.tria_prima_deep['Mercury']
    assert 'Body/solidity' in phase9.tria_prima_deep['Salt']
    print("  ✓ Tria Prima definitions valid")


def test_hermetic_unity_exploration():
    """Test hermetic unity exploration for each principle"""
    print("\nTesting hermetic unity exploration...")
    
    for principle in ['Sulphur', 'Mercury', 'Salt']:
        unified, alchemized = phase9.explore_hermetic_unity(0.1, principle=principle)
        
        # Verify results are numeric and reasonable
        assert isinstance(unified, float), f"{principle} unified should be float"
        assert isinstance(alchemized, int), f"{principle} alchemized should be int"
        assert unified > 0, f"{principle} unified should be positive"
        assert alchemized > 0, f"{principle} alchemized should be positive"
        
        print(f"  ✓ {principle}: unified={unified:.6f}, alchemized={alchemized}")


def test_hermetic_graph():
    """Test hermetic graph construction"""
    print("\nTesting hermetic graph construction...")
    
    graph = phase9.build_hermetic_graph()
    
    # Verify graph structure
    assert graph.number_of_nodes() >= 5, "Should have at least 5 nodes"
    assert graph.number_of_edges() >= 6, "Should have at least 6 edges"
    
    # Verify Tria Prima nodes exist
    assert 'Sulphur' in graph.nodes()
    assert 'Mercury' in graph.nodes()
    assert 'Salt' in graph.nodes()
    assert 'alkahest' in graph.nodes()
    assert 'macro_micro' in graph.nodes()
    
    print(f"  ✓ Graph has {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")


def test_sagco_hermetic_tie():
    """Test SAGCO hermetic evolution tie"""
    print("\nTesting SAGCO hermetic tie...")
    
    claims = phase9.load_claims()
    sagco = phase9.tie_sagco_hermetic(claims)
    
    assert 'from' in sagco
    assert 'bench' in sagco
    assert 'IBM' in sagco['from']
    assert 'GSCH' in sagco['from']
    
    print(f"  ✓ SAGCO tie: {sagco['from'][:50]}...")


def test_enhanced_precision_metrics():
    """Test enhanced precision metrics generation"""
    print("\nTesting enhanced precision metrics...")
    
    results = phase9.enhanced_precision_benchmark_wave_gen(n=1000, drift=0.05, dps=100)
    
    # Verify all expected fields exist
    assert 'speedup' in results
    assert 'stable_ci' in results
    assert 'var_power' in results
    assert 'exact_variance' in results
    assert 'samples' in results
    assert 'precision_dps' in results
    
    # Verify metrics meet targets
    assert results['speedup'] > 0, "Speedup should be positive"
    assert len(results['stable_ci']) == 2, "CI should have lower and upper bounds"
    assert results['var_power'] > 0.95, f"Variance power {results['var_power']} should be >0.95"
    assert results['samples'] == 1000, "Should have 1000 samples"
    assert results['precision_dps'] == 100, "Should use 100 decimal places"
    
    print(f"  ✓ Speedup: {results['speedup']:.2f} ops/sec")
    print(f"  ✓ Stable CI: [{results['stable_ci'][0]:.6f}, {results['stable_ci'][1]:.6f}]")
    print(f"  ✓ Variance Power: {results['var_power']:.4f} (>0.95 target met!)")
    print(f"  ✓ Exact Variance: {results['exact_variance']:.6e}")


def test_benchmark_output():
    """Test that benchmark output is generated correctly"""
    print("\nTesting benchmark output generation...")
    
    output_path = '../benchmarks/tria_hermetic_precision.yaml'
    if not os.path.exists(output_path):
        output_path = 'benchmarks/tria_hermetic_precision.yaml'
    
    # Check if output file exists
    assert os.path.exists(output_path), f"Benchmark output should exist at {output_path}"
    
    # Load and validate output
    with open(output_path, 'r') as f:
        output = yaml.safe_load(f)
    
    assert 'tria_deep' in output
    assert 'hermetic_explore' in output
    assert 'sagco_tie' in output
    assert 'enhanced_metrics' in output
    
    # Verify variance power in output
    assert output['enhanced_metrics']['var_power'] > 0.95, "Output should show >0.95 variance power"
    
    print(f"  ✓ Benchmark output exists and is valid")
    print(f"  ✓ Output variance power: {output['enhanced_metrics']['var_power']:.4f}")


def main():
    """Run all Phase 9 tests"""
    print("=" * 70)
    print("Phase 9 Integration Tests")
    print("=" * 70)
    
    try:
        test_tria_prima_definitions()
        test_hermetic_unity_exploration()
        test_hermetic_graph()
        test_sagco_hermetic_tie()
        test_enhanced_precision_metrics()
        test_benchmark_output()
        
        print("\n" + "=" * 70)
        print("All Phase 9 Tests Passed! ✓")
        print("=" * 70)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

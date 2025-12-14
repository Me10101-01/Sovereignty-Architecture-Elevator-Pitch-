#!/usr/bin/env python3
"""
Test script for Phase 14 implementation
"""

import sys
import os
import yaml

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from explore_voynich_map_enochian import (
    load_claims,
    create_incomprehensible_graph,
    tie_sagco_incomprehensible,
    enhanced_precision_benchmark_wave_gen
)


def test_load_claims():
    """Test claims loading"""
    claims = load_claims()
    assert '5' in claims or '7' in claims, "Claims should contain expected keys"
    print("✓ Claims loading test passed")


def test_create_graph():
    """Test graph creation"""
    graph, voynich, enochian, phaistos = create_incomprehensible_graph()
    
    # Verify nodes
    assert 'Voynich' in graph.nodes(), "Voynich node should exist"
    assert 'Enochian' in graph.nodes(), "Enochian node should exist"
    assert 'Phaistos' in graph.nodes(), "Phaistos node should exist"
    
    # Verify edges
    assert graph.has_edge('Voynich', 'Enochian'), "Voynich-Enochian edge should exist"
    assert graph.has_edge('Enochian', 'Phaistos'), "Enochian-Phaistos edge should exist"
    
    # Verify descriptions
    assert 'Voynich Manuscript' in voynich, "Voynich description should be complete"
    assert 'John Dee' in enochian, "Enochian description should be complete"
    assert 'Phaistos Disc' in phaistos, "Phaistos description should be complete"
    
    print("✓ Graph creation test passed")


def test_sagco_tie():
    """Test SAGCO integration"""
    claims = load_claims()
    sagco = tie_sagco_incomprehensible(claims)
    
    assert 'from' in sagco, "SAGCO tie should have 'from' key"
    assert 'bench' in sagco, "SAGCO tie should have 'bench' key"
    assert 'IBM' in sagco['from'] or 'Paracelsus' in sagco['from'], "SAGCO should reference priors"
    
    print("✓ SAGCO tie test passed")


def test_benchmarks():
    """Test enhanced precision benchmarks"""
    # Run with smaller dataset for speed
    results = enhanced_precision_benchmark_wave_gen(n=100, drift=0.05, dps=50)
    
    assert 'speedup' in results, "Results should contain speedup"
    assert 'stable_ci' in results, "Results should contain stable_ci"
    assert 'var_power' in results, "Results should contain var_power"
    assert 'anova_f' in results, "Results should contain anova_f"
    assert 'recall_stable' in results, "Results should contain recall_stable"
    
    # Verify reasonable values
    assert results['speedup'] > 0, "Speedup should be positive"
    assert results['recall_stable'] > 0.99, "Recall should be >99%"
    
    print("✓ Benchmark test passed")
    print(f"  Speedup: {results['speedup']:.2f} ops/sec")
    print(f"  Recall: {results['recall_stable']:.6f}")


def test_output_file():
    """Test output file generation"""
    output_path = 'benchmarks/voynich_enochian_incomprehensible.yaml'
    
    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            data = yaml.safe_load(f)
        
        assert 'voynich_deep' in data, "Output should contain voynich_deep"
        assert 'enochian_map' in data, "Output should contain enochian_map"
        assert 'incomprehensible_incorp' in data, "Output should contain incomprehensible_incorp"
        assert 'enhanced_metrics' in data, "Output should contain enhanced_metrics"
        
        print("✓ Output file test passed")
    else:
        print("⚠ Output file not found (run main script first)")


def main():
    """Run all tests"""
    print("Running Phase 14 Tests")
    print("=" * 60)
    
    try:
        test_load_claims()
        test_create_graph()
        test_sagco_tie()
        test_benchmarks()
        test_output_file()
        
        print("=" * 60)
        print("All tests passed! ✓")
        return 0
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

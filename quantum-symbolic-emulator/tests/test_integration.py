#!/usr/bin/env python3
"""
Integration Tests for Quantum-Symbolic Processor Emulator
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flame_sagco import FlameTranscribe
from modules import (
    WaveALU,
    LyapunovClock,
    NeuralControlUnit,
    EntanglementCore,
    DNAMemory,
    GPTAgent,
    PhaseType
)


def test_flame_transcribe():
    """Test FlameTranscribe DNA pipeline"""
    print("Testing FlameTranscribe...")
    transcribe = FlameTranscribe()
    
    # Test SAGCO to DNA
    result = transcribe.full_chain("SAGCO")
    assert result['input'] == "SAGCO"
    assert result['dna'] == "AGCGCTGGATGCTAA"
    assert len(result['nft_hash']) == 128  # blake2b produces 64-byte hash (128 hex chars)
    
    print("  ✓ FlameTranscribe tests passed")
    return True


def test_wave_alu():
    """Test Wave ALU"""
    print("Testing Wave ALU...")
    alu = WaveALU(frequency=1.0, amplitude=1.0)
    
    # Test wave operations
    result = alu.wave_add(0.5, 0.3)
    assert isinstance(result, float)
    
    result = alu.wave_multiply(0.5, 0.3)
    assert isinstance(result, float)
    
    # Test transformations
    result = alu.wave_transform(0.25, 'sin')
    assert isinstance(result, float)
    
    # Test vector operations
    vector = [0.0, 0.25, 0.5, 0.75, 1.0]
    result = alu.wave_vector_op(vector, 'sin')
    assert len(result) == len(vector)
    
    print("  ✓ Wave ALU tests passed")
    return True


def test_control_unit():
    """Test Control Unit"""
    print("Testing Control Unit...")
    
    # Test single clock
    clock = LyapunovClock(initial_state=0.1, lyapunov_param=3.9)
    ticks = clock.tick_n(10)
    assert len(ticks) == 10
    
    lyapunov = clock.estimate_lyapunov_exponent(100)
    assert isinstance(lyapunov, float)
    
    # Test neural control unit
    control = NeuralControlUnit(num_clocks=4)
    all_ticks = control.tick_all()
    assert len(all_ticks) == 4
    
    is_synced, variance = control.synchronize()
    assert isinstance(is_synced, bool)
    assert isinstance(variance, float)
    
    print("  ✓ Control Unit tests passed")
    return True


def test_entanglement_core():
    """Test Entanglement Core"""
    print("Testing Entanglement Core...")
    core = EntanglementCore(num_nodes=8)
    
    # Test entanglement
    success = core.entangle(0, 1, strength=0.9)
    assert success == True
    
    success = core.entangle(1, 2, strength=0.8)
    assert success == True
    
    # Test synchronization
    coherence = core.synchronize_phases()
    assert 0.0 <= coherence <= 1.0
    
    # Test measurement
    collapsed, prob = core.measure(0)
    assert collapsed in [0, 1]
    assert 0.0 <= prob <= 1.0
    
    # Test metrics
    swarm_coherence = core.get_swarm_coherence()
    assert 0.0 <= swarm_coherence <= 1.0
    
    degree = core.get_entanglement_degree()
    assert degree >= 0.0
    
    print("  ✓ Entanglement Core tests passed")
    return True


def test_dna_memory():
    """Test DNA Memory"""
    print("Testing DNA Memory...")
    memory = DNAMemory(capacity=256)
    
    # Test write/read
    success = memory.write(0, "HELLO")
    assert success == True
    
    data = memory.read(0)
    assert data == "HELLO"
    
    # Test DNA encoding
    dna = memory.read_dna(0)
    assert dna is not None
    assert len(dna) > 0
    
    # Test provenance
    valid = memory.verify_provenance(0)
    assert isinstance(valid, bool)
    
    # Test chain
    chain = memory.get_provenance_chain(0)
    assert isinstance(chain, list)
    
    # Test usage
    usage = memory.get_memory_usage()
    assert 0.0 <= usage <= 100.0
    
    print("  ✓ DNA Memory tests passed")
    return True


def test_gpt_agent():
    """Test GPT Agent"""
    print("Testing GPT Agent...")
    agent = GPTAgent()
    
    # Test analysis
    result = agent.analyze_phase("AGCGCTGGATGCTAA", PhaseType.ANALYSIS)
    assert result.phase_type == PhaseType.ANALYSIS
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.interpretation, str)
    
    # Test prediction
    next_phase, confidence = agent.predict_next_phase("current state")
    assert isinstance(next_phase, PhaseType)
    assert 0.0 <= confidence <= 1.0
    
    # Test synthesis
    response = agent.synthesize_response("test query")
    assert isinstance(response, str)
    
    # Test context
    summary = agent.get_context_summary()
    assert isinstance(summary, dict)
    assert 'history_length' in summary
    
    print("  ✓ GPT Agent tests passed")
    return True


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("Running Quantum-Symbolic Processor Emulator Tests")
    print("="*60)
    print()
    
    tests = [
        test_flame_transcribe,
        test_wave_alu,
        test_control_unit,
        test_entanglement_core,
        test_dna_memory,
        test_gpt_agent,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ✗ {test.__name__} failed: {e}")
            failed += 1
    
    print()
    print("-"*60)
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")
    print("-"*60)
    print()
    
    if failed == 0:
        print("✓ All tests passed!")
        return True
    else:
        print("✗ Some tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Quick Start Example - Quantum-Symbolic Processor Emulator
Demonstrates basic usage of all modules
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flame_sagco import FlameTranscribe
from modules import (
    WaveALU,
    NeuralControlUnit,
    EntanglementCore,
    DNAMemory,
    GPTAgent,
    PhaseType
)


def main():
    print("="*70)
    print("Quantum-Symbolic Processor Emulator - Quick Start Example")
    print("="*70)
    print()
    
    # 1. FlameTranscribe - DNA Transformation Pipeline
    print("1. FlameTranscribe DNA Pipeline")
    print("-"*70)
    transcribe = FlameTranscribe()
    result = transcribe.full_chain("SAGCO")
    transcribe.display_chain(result)
    print()
    
    # 2. Wave ALU - Trigonometric Computing
    print("2. Wave ALU - Trigonometric Computing")
    print("-"*70)
    alu = WaveALU(frequency=1.0, amplitude=1.0)
    wave_sum = alu.wave_add(0.5, 0.3)
    print(f"Wave Add(0.5, 0.3) = {wave_sum:.4f}")
    
    vector = [0.0, 0.25, 0.5, 0.75, 1.0]
    sin_vector = alu.wave_vector_op(vector, 'sin')
    print(f"Sin({vector}) = {[f'{x:.4f}' for x in sin_vector]}")
    print()
    
    # 3. Neural Control Unit - Chaotic Timing
    print("3. Neural Control Unit - Chaotic Timing")
    print("-"*70)
    control = NeuralControlUnit(num_clocks=4)
    ticks = control.tick_all()
    print(f"Chaotic ticks: {[f'{t:.4f}' for t in ticks]}")
    
    chaos = control.chaos_metric()
    print(f"Chaos metric (Lyapunov): {chaos:.4f}")
    print()
    
    # 4. Entanglement Core - Swarm Synchronization
    print("4. Entanglement Core - Swarm Synchronization")
    print("-"*70)
    core = EntanglementCore(num_nodes=8)
    core.entangle(0, 1, strength=0.9)
    core.entangle(1, 2, strength=0.8)
    core.entangle(2, 3, strength=0.7)
    
    coherence = core.synchronize_phases()
    print(f"Phase coherence: {coherence:.4f}")
    print(f"Entanglement degree: {core.get_entanglement_degree():.2f}")
    
    collapsed, prob = core.measure(0)
    print(f"Node 0 measured: |{collapsed}⟩ (probability: {prob:.4f})")
    print()
    
    # 5. DNA Memory - Blockchain-style Storage
    print("5. DNA Memory - Blockchain-style Storage")
    print("-"*70)
    memory = DNAMemory(capacity=256)
    
    # Store DNA from FlameTranscribe
    memory.write(0, result['dna'])
    dna_stored = memory.read_dna(0)
    print(f"DNA stored: {dna_stored[:30]}...")
    
    valid = memory.verify_provenance(0)
    print(f"Provenance valid: {valid}")
    print(f"Memory usage: {memory.get_memory_usage():.2f}%")
    
    cell = memory.export_cell(0)
    print(f"Provenance hash: {cell['provenance_hash'][:32]}...")
    print()
    
    # 6. GPT Agent - AI Phase Reasoning
    print("6. GPT Agent - AI Phase Reasoning")
    print("-"*70)
    agent = GPTAgent()
    
    analysis = agent.analyze_phase(result['dna'], PhaseType.ANALYSIS)
    print(f"Analysis: {analysis.interpretation}")
    print(f"Confidence: {analysis.confidence:.2f}")
    
    next_phase, conf = agent.predict_next_phase("SAGCO processing")
    print(f"Next predicted phase: {next_phase.value} (confidence: {conf:.2f})")
    
    response = agent.synthesize_response("What patterns do you see?")
    print(f"Synthesis: {response[:80]}...")
    print()
    
    # 7. Integration Example
    print("7. Integration Example - Full Pipeline")
    print("-"*70)
    print("Input → FlameTranscribe → Memory → GPT Analysis → Entanglement")
    print()
    
    # Transform input
    input_data = "SAGCO"
    print(f"Step 1: Input = {input_data}")
    
    # DNA transcription
    transform = transcribe.full_chain(input_data)
    print(f"Step 2: DNA = {transform['dna']}")
    
    # Store in memory
    memory.write(10, transform['dna'])
    print(f"Step 3: Stored at address 10")
    
    # Analyze with GPT agent
    analysis = agent.analyze_phase(transform['dna'], PhaseType.SYNTHESIS)
    print(f"Step 4: GPT Analysis = {analysis.interpretation[:60]}...")
    
    # Sync with entanglement
    coherence = core.synchronize_phases()
    print(f"Step 5: Synchronized swarm (coherence: {coherence:.4f})")
    print()
    
    print("="*70)
    print("✓ All modules demonstrated successfully!")
    print("="*70)


if __name__ == "__main__":
    main()

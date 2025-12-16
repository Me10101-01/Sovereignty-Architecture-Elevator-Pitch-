#!/usr/bin/env python3
"""
FlameLang Demo - Neuro-Acoustic AI System Examples

Demonstrates the usage of FlameLang for generating therapeutic soundscapes
for ADHD, anxiety, and dementia relief using hemi-sync algorithms.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from flamelang import (
    FlameLangInterpreter,
    HemiSyncGlyph,
    TimeSeriesGlyph,
    SpatialBufferGlyph,
    AIExpansionGlyph,
    GlyphParams,
    Frequency,
    calculate_five_day_cycle_ms,
    create_adhd_sound_map,
    create_dementia_relief_map,
)
from flamelang.transformer_engine import (
    TimeSeriesTransformer,
    TransformerConfig,
    SignalPredictor,
)
from flamelang.red_team import (
    RedTeamProtocol,
    AttackConfig,
    AttackType,
)
from flamelang.swarm_pulse import SwarmPulse


def demo_basic_hemi_sync():
    """Demo 1: Basic hemi-sync binaural beat generation"""
    print("\n" + "="*60)
    print("DEMO 1: Basic Hemi-Sync Binaural Beat Generation")
    print("="*60)
    
    # Create parameters for 432 Hz base with 8 Hz alpha wave beat
    params = GlyphParams(
        left_freq=Frequency(432.0),
        right_freq=Frequency(440.0),  # 8 Hz difference
        time_cycle_ms=5000  # 5 seconds
    )
    
    # Create and execute HemiSync glyph
    hemi_sync = HemiSyncGlyph(params)
    left_channel, right_channel = hemi_sync.execute()
    
    print(f"Generated binaural beat:")
    print(f"  Left frequency: {params.left_freq.value} Hz")
    print(f"  Right frequency: {params.right_freq.value} Hz")
    print(f"  Beat frequency: {hemi_sync.get_beat_frequency()} Hz (Alpha waves)")
    print(f"  Duration: {params.time_cycle_ms / 1000:.1f} seconds")
    print(f"  Left channel shape: {left_channel.shape}")
    print(f"  Right channel shape: {right_channel.shape}")


def demo_adhd_sound_map():
    """Demo 2: ADHD therapeutic sound map"""
    print("\n" + "="*60)
    print("DEMO 2: ADHD Therapeutic Sound Map")
    print("="*60)
    
    # Generate ADHD sound map with default parameters
    left, right = create_adhd_sound_map(base_frequency=432.0, beat_frequency=8.0)
    
    print(f"ADHD sound map generated:")
    print(f"  Base frequency: 432 Hz (natural tuning)")
    print(f"  Beat frequency: 8 Hz (alpha waves for focus)")
    print(f"  Left channel samples: {len(left)}")
    print(f"  Right channel samples: {len(right)}")
    print(f"  RMS energy left: {np.sqrt(np.mean(left**2)):.4f}")
    print(f"  RMS energy right: {np.sqrt(np.mean(right**2)):.4f}")


def demo_dementia_relief():
    """Demo 3: Dementia relief multi-frequency sound map"""
    print("\n" + "="*60)
    print("DEMO 3: Dementia Relief Multi-Frequency Sound Map")
    print("="*60)
    
    # Generate dementia relief map with healing frequencies
    sound_map = create_dementia_relief_map()
    
    print(f"Generated {len(sound_map)} therapeutic frequencies:")
    for freq_name, audio in sound_map.items():
        print(f"  {freq_name}: {audio.shape} (stereo)")


def demo_five_day_cycle():
    """Demo 4: Five-day cycle calculation"""
    print("\n" + "="*60)
    print("DEMO 4: Five-Day Cycle (432M milliseconds)")
    print("="*60)
    
    cycle_ms = calculate_five_day_cycle_ms()
    
    print(f"5-day cycle calculation:")
    print(f"  Total milliseconds: {cycle_ms:,} ms")
    print(f"  Connection to 432 Hz: {cycle_ms / 1_000_000} * 1000 = {cycle_ms}")
    print(f"  This aligns with sound healing frequencies")


def demo_transformer_analysis():
    """Demo 5: Transformer-based signal analysis"""
    print("\n" + "="*60)
    print("DEMO 5: Transformer-Based Signal Analysis")
    print("="*60)
    
    # Create a sample signal
    params = GlyphParams(
        left_freq=Frequency(432.0),
        right_freq=Frequency(440.0),
        time_cycle_ms=3000
    )
    hemi_sync = HemiSyncGlyph(params)
    left, right = hemi_sync.execute()
    
    # Analyze with transformer
    config = TransformerConfig(
        sequence_length=256,
        embedding_dim=32,
        num_heads=4
    )
    transformer = TimeSeriesTransformer(config)
    
    analysis = transformer.process(left)
    
    print("Transformer analysis results:")
    print(f"  Signal length: {analysis['signal_length']}")
    print(f"  Sequence length: {analysis['sequence_length']}")
    print(f"  Therapeutic score: {analysis['therapeutic_score']:.4f}")
    print(f"  Mean energy: {analysis['energy_distribution']['mean_energy']:.4f}")
    print(f"  Energy variance: {analysis['energy_distribution']['energy_variance']:.6f}")
    
    # Generate adaptive parameters
    adaptive = transformer.generate_adaptive_params(left, target_state="relaxation")
    
    print("\nAdaptive parameter recommendations:")
    print(f"  Target state: relaxation")
    print(f"  Recommended beat frequency: {adaptive['recommended_params']['target_beat_freq']} Hz")
    print(f"  Base frequency: {adaptive['recommended_params']['base_freq']} Hz")
    print(f"  Intensity: {adaptive['recommended_params']['intensity']:.2f}")


def demo_red_team_protocol():
    """Demo 6: Red team security testing"""
    print("\n" + "="*60)
    print("DEMO 6: Red Team Security Protocol")
    print("="*60)
    
    # Generate a therapeutic signal
    params = GlyphParams(
        left_freq=Frequency(432.0),
        right_freq=Frequency(440.0),
        time_cycle_ms=2000
    )
    hemi_sync = HemiSyncGlyph(params)
    left, _ = hemi_sync.execute()
    
    # Run red team tests
    red_team = RedTeamProtocol()
    
    results = red_team.run_full_protocol(left, intensity=0.3)
    
    print("Red team protocol results:")
    print(f"  Total attacks: {results['total_attacks']}")
    print(f"  Successful attacks: {results['successful_attacks']}")
    print(f"  Average resilience: {results['average_resilience']:.4f}")
    print(f"  Recommendation: {results['recommendation']}")
    
    print("\nIndividual attack results:")
    for attack in results['attack_results']:
        print(f"  {attack['attack_type']}: "
              f"success={attack['success']}, "
              f"resilience={attack['resilience_score']:.4f}")


def demo_swarm_pulse():
    """Demo 7: Swarm-based distributed processing"""
    print("\n" + "="*60)
    print("DEMO 7: SwarmPulse Distributed Processing")
    print("="*60)
    
    # Initialize swarm with 5-day cycle
    swarm = SwarmPulse(cycle_ms=calculate_five_day_cycle_ms())
    
    # Add nodes
    swarm.add_node("node_ps5", capacity=1.0, location=(0, 0, 0))
    swarm.add_node("node_ipad_1", capacity=0.6, location=(1, 0, 0))
    swarm.add_node("node_ipad_2", capacity=0.6, location=(0, 1, 0))
    swarm.add_node("node_blade", capacity=1.5, location=(1, 1, 0))
    
    print(f"Swarm initialized with {len(swarm.nodes)} nodes")
    
    # Generate test signal
    test_signal = np.sin(2 * np.pi * 432 * np.linspace(0, 1, 44100))
    
    # Submit tasks
    task_ids = []
    task_ids.append(swarm.submit_task(test_signal, task_type='generation', priority=2))
    task_ids.append(swarm.submit_task(test_signal, task_type='analysis', priority=3))
    task_ids.append(swarm.submit_task(test_signal, task_type='optimization', priority=1))
    
    print(f"Submitted {len(task_ids)} tasks")
    
    # Execute pulse
    pulse_result = swarm.pulse()
    
    print("\nPulse execution results:")
    print(f"  Pulse number: {pulse_result['pulse_number']}")
    print(f"  Active nodes: {pulse_result['nodes_active']}/{pulse_result['nodes_total']}")
    print(f"  Tasks assigned: {pulse_result['tasks_assigned']}")
    print(f"  Tasks processed: {pulse_result['tasks_processed']}")
    print(f"  Average node load: {pulse_result['average_node_load']:.4f}")
    
    # Get status
    status = swarm.get_status()
    print("\nSwarm status:")
    for node_id, node_status in status['nodes'].items():
        print(f"  {node_id}: load={node_status['current_load']:.2f}, "
              f"processed={node_status['processed_signals']}")


def demo_ai_expansion():
    """Demo 8: AI-generated channel expansions"""
    print("\n" + "="*60)
    print("DEMO 8: AI-Generated Channel Expansions")
    print("="*60)
    
    # Create base signal
    params = GlyphParams(
        left_freq=Frequency(432.0),
        right_freq=Frequency(440.0),
        time_cycle_ms=1000,
        metadata={"expansion_factor": 4, "mutation_rate": 0.1}
    )
    
    hemi_sync = HemiSyncGlyph(params)
    left, _ = hemi_sync.execute()
    
    # Generate AI expansions
    ai_expansion = AIExpansionGlyph(params)
    expansions = ai_expansion.transform(left)
    
    print(f"AI expansions generated:")
    print(f"  Original signal length: {len(left)}")
    print(f"  Number of expansions: {len(expansions)}")
    
    for i, expansion in enumerate(expansions):
        rms = np.sqrt(np.mean(expansion ** 2))
        print(f"  Expansion {i}: RMS={rms:.4f}, shape={expansion.shape}")


def demo_full_interpreter():
    """Demo 9: Full FlameLang interpreter pipeline"""
    print("\n" + "="*60)
    print("DEMO 9: Full FlameLang Interpreter Pipeline")
    print("="*60)
    
    # Create interpreter
    interpreter = FlameLangInterpreter()
    
    # Add glyphs to pipeline
    hemi_params = GlyphParams(
        left_freq=Frequency(432.0),
        right_freq=Frequency(440.0),
        time_cycle_ms=3000
    )
    interpreter.add_glyph(HemiSyncGlyph(hemi_params))
    
    time_series_params = GlyphParams(
        time_cycle_ms=calculate_five_day_cycle_ms(),
        buffer_size=2048
    )
    interpreter.add_glyph(TimeSeriesGlyph(time_series_params))
    
    spatial_params = GlyphParams(
        buffer_size=1024,
        channel_count=8
    )
    interpreter.add_glyph(SpatialBufferGlyph(spatial_params))
    
    # Execute pipeline
    results = interpreter.execute()
    
    print("Interpreter execution results:")
    for glyph_name, result in results.items():
        print(f"  {glyph_name}:")
        if isinstance(result, dict):
            for key, value in result.items():
                print(f"    {key}: {value}")
        else:
            print(f"    {result}")
    
    # Show execution log
    print("\nExecution log:")
    for log_entry in interpreter.get_log():
        print(f"  {log_entry['glyph_type']} (index {log_entry['index']}): {log_entry['status']}")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("FlameLang Neuro-Acoustic AI System Demo")
    print("Transformer-Based Time-Series Signal Processing")
    print("for ADHD, Anxiety, and Dementia Therapeutic Soundscapes")
    print("="*60)
    
    demos = [
        demo_basic_hemi_sync,
        demo_adhd_sound_map,
        demo_dementia_relief,
        demo_five_day_cycle,
        demo_transformer_analysis,
        demo_red_team_protocol,
        demo_swarm_pulse,
        demo_ai_expansion,
        demo_full_interpreter,
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\nError in {demo.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Thought-Log Overlay Module
Maps YAML thought-log schema to quantum register states.
Sessions/thoughts as timestamped qubit states with wave propagation logging.
"""

import yaml
import math
from typing import Dict, List, Optional
from datetime import datetime


class ThoughtLogOverlay:
    """
    Quantum register log overlay for cognitive states.
    Parses YAML thought-logs and maps them to quantum register states.
    """

    def __init__(self, yaml_path: Optional[str] = None):
        self.yaml_path = yaml_path or 'configs/thought_log.yaml'
        self.thought_stream = []
        self.sessions = []
        self.metadata = {}
        self.bloom_faces = {}
        self.parity_events = []
        
    def load(self) -> Dict:
        """Load thought-log from YAML file."""
        try:
            with open(self.yaml_path, 'r') as f:
                data = yaml.safe_load(f)
            
            self.metadata = data.get('metadata', {})
            self.thought_stream = data.get('thought_stream', [])
            self.sessions = data.get('sessions', [])
            self.bloom_faces = data.get('bloom_faces', {})
            self.parity_events = data.get('parity_events', [])
            
            return data
        except FileNotFoundError:
            print(f"Warning: {self.yaml_path} not found. Using empty thought log.")
            return {}
    
    def replay_session(self, session_id: str = "session-03AM") -> None:
        """
        Replay a thought session as tick sequence.
        Each thought is a quantum state transition with wave propagation.
        """
        print(f"\n=== REPLAYING SESSION: {session_id} ===\n")
        
        tick = 0
        for thought in self.thought_stream:
            # Calculate wave amplitude with damping for errors
            wave = self._calculate_wave(tick, thought.get('parity_error', False))
            
            print(f"Tick {tick:3d} | T{thought['id']}: {thought['operation']:20s} | "
                  f"Face: {thought['active_face']} ({self.bloom_faces.get(thought['active_face'], 'UNKNOWN'):10s}) | "
                  f"Wave: {wave:6.3f}")
            
            if thought.get('parity_error'):
                error_type = thought.get('error_type', 'UNKNOWN')
                print(f"         └─> PARITY ERROR DETECTED: {error_type} (damped collapse)")
            
            tick += 1
        
        # Display session summary
        session_info = next((s for s in self.sessions if s['session_id'] == session_id), None)
        if session_info:
            print(f"\n=== SESSION SUMMARY ===")
            print(f"Duration: {session_info.get('start_time')} to {session_info.get('end_time')}")
            print(f"Total Thoughts: {session_info.get('thought_count')}")
            print(f"Parity Errors: {session_info.get('parity_errors')}")
            print(f"Dominant Face: {session_info.get('dominant_face')} "
                  f"({self.bloom_faces.get(session_info.get('dominant_face'), 'UNKNOWN')})")
    
    def _calculate_wave(self, tick: int, has_error: bool = False) -> float:
        """
        Calculate wave amplitude for thought state.
        Errors cause damped oscillations (negative collapse indicators).
        """
        if has_error:
            # Damped wave for parity errors
            wave = math.cos(2 * math.pi * tick / 10) * math.exp(-tick / 4)
        else:
            # Normal oscillation
            wave = math.sin(2 * math.pi * tick / 10)
        
        return wave
    
    def get_parity_threshold(self, event_type: str) -> float:
        """Get wave threshold for a specific parity event type."""
        for event in self.parity_events:
            if event.get('type') == event_type:
                return event.get('wave_threshold', -0.5)
        return -0.5  # Default threshold
    
    def export_diff(self, output_path: str = 'thought_log_diff.yaml') -> None:
        """Export thought-log for diffable graph analysis."""
        diff_data = {
            'metadata': self.metadata,
            'thought_count': len(self.thought_stream),
            'parity_error_count': sum(1 for t in self.thought_stream if t.get('parity_error')),
            'face_distribution': self._calculate_face_distribution(),
            'timestamp': datetime.now().isoformat()
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(diff_data, f, default_flow_style=False)
        
        print(f"Exported diff to {output_path}")
    
    def _calculate_face_distribution(self) -> Dict[str, int]:
        """Calculate distribution of active faces in thought stream."""
        distribution = {}
        for thought in self.thought_stream:
            face = thought.get('active_face', 'UNKNOWN')
            distribution[face] = distribution.get(face, 0) + 1
        return distribution


def main():
    """Demo: Load and replay thought-log."""
    overlay = ThoughtLogOverlay()
    overlay.load()
    overlay.replay_session("session-03AM")
    overlay.export_diff()


if __name__ == "__main__":
    main()

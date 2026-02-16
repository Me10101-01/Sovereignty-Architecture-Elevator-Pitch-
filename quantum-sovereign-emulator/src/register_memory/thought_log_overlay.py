"""
Thought-Log Overlay Module
Maps YAML thought-log schema to quantum register log overlay
Sessions/thoughts as timestamped qubit states
"""

import yaml
import math
from pathlib import Path
from typing import Dict, List, Any, Optional


class ThoughtLogOverlay:
    """Manages thought-log YAML parsing and quantum state mapping"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "configs/thought_log.yaml"
        self.thought_stream: List[Dict[str, Any]] = []
        self.bloom_faces: Dict[str, str] = {}
        self.reference_hierarchy: Dict[str, Any] = {}
        self.parity_events: List[Dict[str, Any]] = []
        
    def load_yaml(self, yaml_path: Optional[str] = None) -> Dict[str, Any]:
        """Load thought-log YAML schema"""
        path = yaml_path or self.config_path
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
            
            self.thought_stream = data.get('thought_stream', [])
            self.bloom_faces = data.get('bloom_faces', {})
            self.reference_hierarchy = data.get('reference_hierarchy', {})
            self.parity_events = data.get('parity_events', [])
            
            return data
        except FileNotFoundError:
            print(f"Warning: {path} not found. Using empty configuration.")
            return {}
    
    def replay_session(self, session_id: Optional[str] = None) -> None:
        """Replay thought stream as quantum state sequence"""
        print(f"\n=== THOUGHT-LOG REPLAY (YAML v0.1) ===\n")
        
        if not self.thought_stream:
            print("No thought stream loaded. Call load_yaml() first.")
            return
        
        tick = 0
        for thought in self.thought_stream:
            thought_id = thought.get('id', 'N/A')
            operation = thought.get('operation', 'UNKNOWN')
            active_face = thought.get('active_face', 'N/A')
            description = thought.get('description', '')
            parity_error = thought.get('parity_error', False)
            
            print(f"Replay T{thought_id}: {operation} (Face: {active_face})")
            print(f"  Description: {description}")
            
            if parity_error:
                # Calculate damped wave for error state
                wave = math.cos(2 * math.pi * tick / 10) * math.exp(-tick / 4)
                error_type = thought.get('error_type', 'unknown')
                print(f"  ⚠️  Parity Wave: {wave:.3f} (Error if < 0)")
                print(f"  Error Type: {error_type}")
            
            print()
            tick += 1
    
    def export_to_yaml(self, output_path: str, thoughts: List[Dict[str, Any]]) -> None:
        """Export new thought stream to YAML"""
        data = {
            'thought_stream': thoughts,
            'bloom_faces': self.bloom_faces,
            'reference_hierarchy': self.reference_hierarchy,
            'parity_events': self.parity_events
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        print(f"Exported thought stream to {output_path}")
    
    def get_face_description(self, face_code: str) -> str:
        """Get Bloom taxonomy description for face code"""
        return self.bloom_faces.get(face_code, "UNKNOWN")
    
    def log_thought(self, operation: str, active_face: str, description: str, 
                   parity_error: bool = False, error_type: Optional[str] = None) -> Dict[str, Any]:
        """Create a new thought entry"""
        from datetime import datetime
        
        thought = {
            'id': len(self.thought_stream) + 1,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'operation': operation,
            'active_face': active_face,
            'description': description,
            'parity_error': parity_error
        }
        
        if error_type:
            thought['error_type'] = error_type
        
        self.thought_stream.append(thought)
        return thought


def main():
    """Demo thought-log overlay functionality"""
    overlay = ThoughtLogOverlay()
    overlay.load_yaml()
    overlay.replay_session()
    
    # Log a new thought
    print("\n=== LOGGING NEW THOUGHT ===\n")
    new_thought = overlay.log_thought(
        operation="INTEGRATION",
        active_face="B",
        description="Integrate quantum cube with thought-log system",
        parity_error=False
    )
    print(f"Logged: {new_thought}")


if __name__ == "__main__":
    main()

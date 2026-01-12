#!/usr/bin/env python3
"""
Control Unit Dispatcher
Routes YAML thought streams to appropriate subsystems.
Coordinates parity checking and wave computation.
"""

from typing import Dict, List
import yaml


class Dispatcher:
    """
    Central control unit for routing cognitive operations.
    Parses YAML thought streams and dispatches to subsystems.
    """

    def __init__(self):
        self.subsystems = {
            'thought_log': None,
            'parity_checker': None,
            'wave_cores': None,
            'sequencer': None
        }
        self.dispatch_queue = []
    
    def register_subsystem(self, name: str, subsystem) -> None:
        """Register a subsystem for dispatch."""
        if name in self.subsystems:
            self.subsystems[name] = subsystem
            print(f"✓ Registered subsystem: {name}")
        else:
            print(f"⚠ Unknown subsystem: {name}")
    
    def parse_thought_stream(self, yaml_path: str) -> List[Dict]:
        """Parse YAML thought stream into operations."""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return data.get('thought_stream', [])
    
    def dispatch_operation(self, operation: Dict) -> None:
        """Dispatch a single operation to appropriate subsystem."""
        op_type = operation.get('operation')
        
        # Route based on operation type
        if 'CHECK' in op_type:
            subsystem = self.subsystems.get('parity_checker')
            if subsystem:
                print(f"→ Dispatching {op_type} to parity_checker")
        elif 'RECALL' in op_type or 'REMEMBER' in op_type:
            subsystem = self.subsystems.get('thought_log')
            if subsystem:
                print(f"→ Dispatching {op_type} to thought_log")
        else:
            subsystem = self.subsystems.get('wave_cores')
            if subsystem:
                print(f"→ Dispatching {op_type} to wave_cores")
    
    def dispatch_all(self, yaml_path: str) -> None:
        """Dispatch all operations from YAML stream."""
        print("\n=== DISPATCHER: Processing Thought Stream ===\n")
        operations = self.parse_thought_stream(yaml_path)
        
        for op in operations:
            self.dispatch_operation(op)


def main():
    """Demo: Dispatcher routing."""
    dispatcher = Dispatcher()
    
    # Mock subsystem registration
    dispatcher.register_subsystem('thought_log', object())
    dispatcher.register_subsystem('parity_checker', object())
    dispatcher.register_subsystem('wave_cores', object())
    
    # Dispatch operations
    dispatcher.dispatch_all('configs/thought_log.yaml')


if __name__ == "__main__":
    main()

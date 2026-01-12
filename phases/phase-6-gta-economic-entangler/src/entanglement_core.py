"""
Entanglement Core
Links business dependencies (e.g., Bunker→Nightclub warehouse)
Quantum-inspired dependency state management
"""

from typing import Dict, Set, List, Any
import yaml


class EntanglementCore:
    """
    Manages quantum-inspired entanglement between income sources.
    Dependencies create entanglement links that boost production.
    """
    
    def __init__(self, yaml_config_path: str):
        """
        Initialize entanglement core with YAML configuration.
        
        Args:
            yaml_config_path: Path to income_sources.yaml
        """
        with open(yaml_config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.income_sources = self.config['income_sources']
        self.dependency_state: Dict[str, bool] = {}
        self.entanglement_links: Dict[str, Set[str]] = {}
        
        self._build_entanglement_graph()
        
    def _build_entanglement_graph(self):
        """Build the entanglement graph from dependencies."""
        for category in ['truly_passive', 'semi_passive']:
            if category not in self.income_sources:
                continue
                
            for source in self.income_sources[category]:
                source_name = source['name']
                dependencies = source.get('dependencies', [])
                
                if dependencies:
                    self.entanglement_links[source_name] = set(dependencies)
                    
                    # Initialize dependency states to False
                    for dep in dependencies:
                        if dep not in self.dependency_state:
                            self.dependency_state[dep] = False
    
    def set_dependency_state(self, dependency: str, satisfied: bool):
        """
        Set the state of a dependency.
        
        Args:
            dependency: Name of the dependency
            satisfied: Whether the dependency is satisfied
        """
        self.dependency_state[dependency] = satisfied
    
    def get_dependency_state(self, dependency: str) -> bool:
        """
        Get the state of a dependency.
        
        Args:
            dependency: Name of the dependency
            
        Returns:
            Whether the dependency is satisfied
        """
        return self.dependency_state.get(dependency, False)
    
    def are_dependencies_satisfied(self, source_name: str) -> bool:
        """
        Check if all dependencies for a source are satisfied.
        
        Args:
            source_name: Name of the income source
            
        Returns:
            True if all dependencies are satisfied
        """
        if source_name not in self.entanglement_links:
            return True  # No dependencies = always satisfied
        
        dependencies = self.entanglement_links[source_name]
        return all(self.get_dependency_state(dep) for dep in dependencies)
    
    def get_entanglement_boost(self, source_name: str) -> float:
        """
        Calculate entanglement boost multiplier.
        
        Args:
            source_name: Name of the income source
            
        Returns:
            Boost multiplier (1.0 = no boost, 1.5 = 50% boost, etc.)
        """
        if source_name not in self.entanglement_links:
            return 1.0
        
        dependencies = self.entanglement_links[source_name]
        satisfied_count = sum(1 for dep in dependencies 
                            if self.get_dependency_state(dep))
        total_count = len(dependencies)
        
        if total_count == 0:
            return 1.0
        
        # Boost scales with percentage of satisfied dependencies
        satisfaction_ratio = satisfied_count / total_count
        
        # 100% satisfaction = 1.5x boost, linear scaling
        boost = 1.0 + (0.5 * satisfaction_ratio)
        
        return boost
    
    def activate_all_dependencies(self):
        """Activate all dependencies (for testing/sandbox)."""
        for dep in self.dependency_state:
            self.dependency_state[dep] = True
    
    def deactivate_all_dependencies(self):
        """Deactivate all dependencies."""
        for dep in self.dependency_state:
            self.dependency_state[dep] = False
    
    def get_entangled_sources(self, dependency: str) -> List[str]:
        """
        Get all sources that depend on a specific dependency.
        
        Args:
            dependency: Name of the dependency
            
        Returns:
            List of source names that depend on it
        """
        entangled = []
        for source_name, deps in self.entanglement_links.items():
            if dependency in deps:
                entangled.append(source_name)
        return entangled
    
    def get_dependency_impact(self, dependency: str) -> Dict[str, Any]:
        """
        Analyze the impact of a dependency.
        
        Args:
            dependency: Name of the dependency
            
        Returns:
            Dictionary with impact analysis
        """
        entangled_sources = self.get_entangled_sources(dependency)
        current_state = self.get_dependency_state(dependency)
        
        return {
            'dependency': dependency,
            'current_state': current_state,
            'affected_sources': entangled_sources,
            'impact_count': len(entangled_sources)
        }
    
    def get_entanglement_summary(self) -> Dict[str, Any]:
        """
        Get summary of all entanglement links.
        
        Returns:
            Dictionary with entanglement summary
        """
        total_links = sum(len(deps) for deps in self.entanglement_links.values())
        satisfied_links = sum(
            sum(1 for dep in deps if self.get_dependency_state(dep))
            for deps in self.entanglement_links.values()
        )
        
        return {
            'total_sources': len(self.entanglement_links),
            'total_links': total_links,
            'satisfied_links': satisfied_links,
            'satisfaction_percentage': (satisfied_links / total_links * 100) 
                                     if total_links > 0 else 0.0,
            'source_links': {
                source: list(deps) 
                for source, deps in self.entanglement_links.items()
            }
        }

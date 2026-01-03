"""
GPT Agent - AI Interpreter for Phase Reasoning
Provides AI-based interpretation and reasoning capabilities for the processor

Uses pattern matching and symbolic reasoning for phase analysis.
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class PhaseType(Enum):
    """Types of reasoning phases"""
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    EVALUATION = "evaluation"
    PREDICTION = "prediction"
    ADAPTATION = "adaptation"


@dataclass
class PhaseResult:
    """Result of phase reasoning"""
    phase_type: PhaseType
    input_data: str
    interpretation: str
    confidence: float
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'phase_type': self.phase_type.value,
            'input_data': self.input_data,
            'interpretation': self.interpretation,
            'confidence': self.confidence,
            'metadata': self.metadata
        }


class GPTAgent:
    """
    AI interpreter for phase reasoning
    Provides symbolic reasoning and pattern interpretation
    """
    
    def __init__(self):
        """Initialize GPT Agent"""
        self.pattern_database = self._load_patterns()
        self.context_history: List[PhaseResult] = []
        self.learning_rate = 0.1
        
    def _load_patterns(self) -> Dict[str, List[str]]:
        """
        Load pattern recognition database
        
        Returns:
            Dictionary of pattern categories and patterns
        """
        return {
            'dna_sequences': [
                r'[ATCG]{3,}',
                r'(ATG|TAA|TAG|TGA)',  # Start/stop codons
            ],
            'sagco_patterns': [
                r'[SAGCO]+',
                r'S[AGC]+O',  # SAGCO bookends
            ],
            'wave_patterns': [
                r'sin|cos|tan',
                r'wave|frequency|amplitude',
            ],
            'chaos_patterns': [
                r'lyapunov|chaos|entropy',
                r'bifurcation|attractor',
            ],
            'quantum_patterns': [
                r'entangle|superposition|collapse',
                r'qubit|coherence|decoherence',
            ]
        }
    
    def analyze_phase(self, input_data: str, phase_type: PhaseType = PhaseType.ANALYSIS) -> PhaseResult:
        """
        Analyze input data and provide interpretation
        
        Args:
            input_data: Data to analyze
            phase_type: Type of reasoning phase
            
        Returns:
            Phase reasoning result
        """
        # Pattern matching
        detected_patterns = self._detect_patterns(input_data)
        
        # Generate interpretation
        interpretation = self._generate_interpretation(input_data, detected_patterns, phase_type)
        
        # Calculate confidence
        confidence = self._calculate_confidence(detected_patterns)
        
        # Create result
        result = PhaseResult(
            phase_type=phase_type,
            input_data=input_data[:100],  # Truncate for storage
            interpretation=interpretation,
            confidence=confidence,
            metadata={
                'patterns': detected_patterns,
                'pattern_count': len(detected_patterns)
            }
        )
        
        # Store in history
        self.context_history.append(result)
        
        return result
    
    def _detect_patterns(self, data: str) -> Dict[str, List[str]]:
        """
        Detect patterns in input data
        
        Args:
            data: Input data
            
        Returns:
            Dictionary of detected pattern types and matches
        """
        detected = {}
        
        for category, patterns in self.pattern_database.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, data, re.IGNORECASE)
                if found:
                    matches.extend(found)
            
            if matches:
                detected[category] = list(set(matches))  # Unique matches
        
        return detected
    
    def _generate_interpretation(self, data: str, patterns: Dict[str, List[str]], 
                                  phase_type: PhaseType) -> str:
        """
        Generate interpretation based on patterns
        
        Args:
            data: Input data
            patterns: Detected patterns
            phase_type: Phase type
            
        Returns:
            Interpretation string
        """
        interpretations = []
        
        if 'dna_sequences' in patterns:
            interpretations.append(f"DNA encoding detected: {len(patterns['dna_sequences'])} sequences")
        
        if 'sagco_patterns' in patterns:
            interpretations.append("SAGCO architecture pattern identified")
        
        if 'wave_patterns' in patterns:
            interpretations.append("Wave-based computation signatures present")
        
        if 'chaos_patterns' in patterns:
            interpretations.append("Chaotic dynamics indicators found")
        
        if 'quantum_patterns' in patterns:
            interpretations.append("Quantum-inspired operations detected")
        
        if not interpretations:
            interpretations.append("No specific patterns detected - general data processing")
        
        # Add phase-specific reasoning
        if phase_type == PhaseType.ANALYSIS:
            prefix = "Analysis: "
        elif phase_type == PhaseType.SYNTHESIS:
            prefix = "Synthesis: "
        elif phase_type == PhaseType.EVALUATION:
            prefix = "Evaluation: "
        elif phase_type == PhaseType.PREDICTION:
            prefix = "Prediction: "
        else:
            prefix = "Adaptation: "
        
        return prefix + "; ".join(interpretations)
    
    def _calculate_confidence(self, patterns: Dict[str, List[str]]) -> float:
        """
        Calculate confidence score based on pattern matches
        
        Args:
            patterns: Detected patterns
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not patterns:
            return 0.3  # Baseline confidence
        
        # More patterns = higher confidence
        pattern_score = min(len(patterns) * 0.2, 0.7)
        
        # More matches per pattern = higher confidence
        total_matches = sum(len(matches) for matches in patterns.values())
        match_score = min(total_matches * 0.05, 0.3)
        
        return min(pattern_score + match_score, 1.0)
    
    def predict_next_phase(self, current_state: str) -> Tuple[PhaseType, float]:
        """
        Predict next reasoning phase based on current state
        
        Args:
            current_state: Current system state
            
        Returns:
            Tuple of (predicted_phase, confidence)
        """
        # Simple prediction based on history
        if not self.context_history:
            return PhaseType.ANALYSIS, 0.5
        
        last_phase = self.context_history[-1].phase_type
        
        # Phase progression logic
        phase_sequence = {
            PhaseType.ANALYSIS: PhaseType.SYNTHESIS,
            PhaseType.SYNTHESIS: PhaseType.EVALUATION,
            PhaseType.EVALUATION: PhaseType.PREDICTION,
            PhaseType.PREDICTION: PhaseType.ADAPTATION,
            PhaseType.ADAPTATION: PhaseType.ANALYSIS
        }
        
        next_phase = phase_sequence.get(last_phase, PhaseType.ANALYSIS)
        confidence = 0.7 + (len(self.context_history) * 0.01)  # Increases with experience
        
        return next_phase, min(confidence, 0.95)
    
    def synthesize_response(self, query: str) -> str:
        """
        Synthesize response to query based on context
        
        Args:
            query: Query string
            
        Returns:
            Synthesized response
        """
        # Analyze query
        result = self.analyze_phase(query, PhaseType.SYNTHESIS)
        
        # Build response
        response = f"[Confidence: {result.confidence:.2f}] {result.interpretation}"
        
        # Add context if available
        if len(self.context_history) > 1:
            recent_patterns = set()
            for past_result in self.context_history[-3:]:
                recent_patterns.update(past_result.metadata.get('patterns', {}).keys())
            
            if recent_patterns:
                response += f" | Context: {', '.join(recent_patterns)}"
        
        return response
    
    def adapt_parameters(self, feedback: float) -> None:
        """
        Adapt agent parameters based on feedback
        
        Args:
            feedback: Feedback score (-1.0 to 1.0)
        """
        # Adjust learning rate based on feedback
        adjustment = feedback * self.learning_rate
        
        # Future: Adjust pattern weights, thresholds, etc.
        # For now, just track
        if self.context_history:
            self.context_history[-1].metadata['feedback'] = feedback
    
    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get summary of reasoning context
        
        Returns:
            Context summary dictionary
        """
        if not self.context_history:
            return {'history_length': 0, 'patterns_seen': {}}
        
        all_patterns = {}
        for result in self.context_history:
            for pattern_type, matches in result.metadata.get('patterns', {}).items():
                if pattern_type not in all_patterns:
                    all_patterns[pattern_type] = 0
                all_patterns[pattern_type] += len(matches)
        
        return {
            'history_length': len(self.context_history),
            'patterns_seen': all_patterns,
            'avg_confidence': sum(r.confidence for r in self.context_history) / len(self.context_history)
        }
    
    def clear_context(self) -> None:
        """Clear context history"""
        self.context_history.clear()


def main():
    """Demonstration of GPT Agent"""
    print("="*60)
    print("GPT Agent - AI Interpreter for Phase Reasoning")
    print("="*60)
    print()
    
    agent = GPTAgent()
    
    # Test different inputs
    test_inputs = [
        ("AGCGCTGGATGCTAA", PhaseType.ANALYSIS),
        ("SAGCO wave frequency modulation", PhaseType.SYNTHESIS),
        ("entanglement coherence lyapunov chaos", PhaseType.EVALUATION),
        ("sin(x) + cos(y) DNA transcription", PhaseType.PREDICTION),
    ]
    
    print("Phase Reasoning Results:")
    for data, phase_type in test_inputs:
        result = agent.analyze_phase(data, phase_type)
        print(f"\n  Input: {data}")
        print(f"  Phase: {result.phase_type.value}")
        print(f"  Interpretation: {result.interpretation}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Patterns: {list(result.metadata['patterns'].keys())}")
    
    print("\n" + "-"*60)
    
    # Test prediction
    print("\nPhase Prediction:")
    next_phase, confidence = agent.predict_next_phase("current state")
    print(f"  Next predicted phase: {next_phase.value}")
    print(f"  Confidence: {confidence:.2f}")
    
    print("\n" + "-"*60)
    
    # Test synthesis
    print("\nResponse Synthesis:")
    query = "analyze the SAGCO DNA entanglement pattern"
    response = agent.synthesize_response(query)
    print(f"  Query: {query}")
    print(f"  Response: {response}")
    
    print("\n" + "-"*60)
    
    # Context summary
    print("\nContext Summary:")
    summary = agent.get_context_summary()
    print(f"  History length: {summary['history_length']}")
    print(f"  Patterns seen: {summary['patterns_seen']}")
    print(f"  Average confidence: {summary['avg_confidence']:.2f}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()

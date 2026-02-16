"""
Red Team Protocol for FlameLang Neuro-Acoustic Systems

Implements security testing and resilience validation for therapeutic
sound systems. Tests against noise injection, signal manipulation,
and adversarial attacks on therapeutic effectiveness.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class AttackType(Enum):
    """Types of red team attacks"""
    NOISE_INJECTION = "noise_injection"
    FREQUENCY_HIJACK = "frequency_hijack"
    PHASE_CORRUPTION = "phase_corruption"
    AMPLITUDE_SPIKE = "amplitude_spike"
    HARMONIC_DISTORTION = "harmonic_distortion"
    TEMPORAL_DISRUPTION = "temporal_disruption"


@dataclass
class AttackConfig:
    """Configuration for a red team attack"""
    attack_type: AttackType
    intensity: float  # 0.0 to 1.0
    duration_ms: int
    target_frequency: Optional[float] = None
    
    def __post_init__(self):
        if not 0.0 <= self.intensity <= 1.0:
            raise ValueError("Intensity must be between 0.0 and 1.0")


@dataclass
class AttackResult:
    """Results from a red team attack"""
    attack_type: AttackType
    success: bool
    therapeutic_score_before: float
    therapeutic_score_after: float
    resilience_score: float  # 0.0 to 1.0, higher is better
    details: Dict[str, Any]


class RedTeamProtocol:
    """
    Red team testing protocol for neuro-acoustic systems
    
    Tests system resilience against various attack vectors to ensure
    therapeutic integrity under adversarial conditions.
    """
    
    def __init__(self):
        self.attack_history: List[AttackResult] = []
    
    def inject_noise(
        self,
        signal: np.ndarray,
        config: AttackConfig
    ) -> Tuple[np.ndarray, AttackResult]:
        """
        Inject noise into therapeutic signal
        
        Args:
            signal: Original signal
            config: Attack configuration
            
        Returns:
            Tuple of (attacked_signal, result)
        """
        # Generate noise
        noise = np.random.normal(0, config.intensity, len(signal))
        
        # Add to signal
        attacked = signal + noise
        
        # Clip to prevent overflow
        attacked = np.clip(attacked, -1.0, 1.0)
        
        # Calculate scores
        score_before = self._calculate_therapeutic_score(signal)
        score_after = self._calculate_therapeutic_score(attacked)
        
        resilience = 1.0 - abs(score_after - score_before)
        
        result = AttackResult(
            attack_type=AttackType.NOISE_INJECTION,
            success=score_after < score_before * 0.8,
            therapeutic_score_before=score_before,
            therapeutic_score_after=score_after,
            resilience_score=resilience,
            details={
                "noise_power": float(np.mean(noise ** 2)),
                "snr": float(10 * np.log10(np.mean(signal ** 2) / np.mean(noise ** 2))),
            }
        )
        
        self.attack_history.append(result)
        return attacked, result
    
    def hijack_frequency(
        self,
        signal: np.ndarray,
        config: AttackConfig,
        sample_rate: int = 44100
    ) -> Tuple[np.ndarray, AttackResult]:
        """
        Inject interfering frequency into signal
        
        Args:
            signal: Original signal
            config: Attack configuration with target_frequency
            sample_rate: Sample rate in Hz
            
        Returns:
            Tuple of (attacked_signal, result)
        """
        if config.target_frequency is None:
            config.target_frequency = 1000.0  # Default to 1kHz
        
        # Generate interfering tone
        t = np.arange(len(signal)) / sample_rate
        interference = config.intensity * np.sin(2 * np.pi * config.target_frequency * t)
        
        # Mix with signal
        attacked = signal + interference
        attacked = np.clip(attacked, -1.0, 1.0)
        
        score_before = self._calculate_therapeutic_score(signal)
        score_after = self._calculate_therapeutic_score(attacked)
        resilience = 1.0 - abs(score_after - score_before)
        
        result = AttackResult(
            attack_type=AttackType.FREQUENCY_HIJACK,
            success=score_after < score_before * 0.7,
            therapeutic_score_before=score_before,
            therapeutic_score_after=score_after,
            resilience_score=resilience,
            details={
                "interference_frequency": config.target_frequency,
                "interference_power": config.intensity,
            }
        )
        
        self.attack_history.append(result)
        return attacked, result
    
    def corrupt_phase(
        self,
        signal: np.ndarray,
        config: AttackConfig
    ) -> Tuple[np.ndarray, AttackResult]:
        """
        Corrupt phase relationships in signal
        
        Args:
            signal: Original signal
            config: Attack configuration
            
        Returns:
            Tuple of (attacked_signal, result)
        """
        # Apply random phase shifts to segments
        segment_size = len(signal) // 10
        attacked = signal.copy()
        
        for i in range(0, len(attacked), segment_size):
            end = min(i + segment_size, len(attacked))
            phase_shift = config.intensity * np.random.uniform(-np.pi, np.pi)
            
            # Apply phase shift via Hilbert-like transform approximation
            segment = attacked[i:end]
            attacked[i:end] = segment * np.cos(phase_shift)
        
        score_before = self._calculate_therapeutic_score(signal)
        score_after = self._calculate_therapeutic_score(attacked)
        resilience = 1.0 - abs(score_after - score_before)
        
        result = AttackResult(
            attack_type=AttackType.PHASE_CORRUPTION,
            success=score_after < score_before * 0.75,
            therapeutic_score_before=score_before,
            therapeutic_score_after=score_after,
            resilience_score=resilience,
            details={
                "segments_affected": len(attacked) // segment_size,
            }
        )
        
        self.attack_history.append(result)
        return attacked, result
    
    def inject_amplitude_spikes(
        self,
        signal: np.ndarray,
        config: AttackConfig
    ) -> Tuple[np.ndarray, AttackResult]:
        """
        Inject sudden amplitude spikes
        
        Args:
            signal: Original signal
            config: Attack configuration
            
        Returns:
            Tuple of (attacked_signal, result)
        """
        attacked = signal.copy()
        
        # Inject random spikes
        num_spikes = int(len(attacked) * config.intensity * 0.01)
        spike_positions = np.random.choice(len(attacked), num_spikes, replace=False)
        
        for pos in spike_positions:
            spike_value = np.random.choice([-1.0, 1.0]) * config.intensity
            attacked[pos] = spike_value
        
        score_before = self._calculate_therapeutic_score(signal)
        score_after = self._calculate_therapeutic_score(attacked)
        resilience = 1.0 - abs(score_after - score_before)
        
        result = AttackResult(
            attack_type=AttackType.AMPLITUDE_SPIKE,
            success=score_after < score_before * 0.6,
            therapeutic_score_before=score_before,
            therapeutic_score_after=score_after,
            resilience_score=resilience,
            details={
                "num_spikes": num_spikes,
                "spike_positions": spike_positions.tolist()[:10],
            }
        )
        
        self.attack_history.append(result)
        return attacked, result
    
    def run_full_protocol(
        self,
        signal: np.ndarray,
        intensity: float = 0.3
    ) -> Dict[str, Any]:
        """
        Run complete red team protocol with all attack types
        
        Args:
            signal: Original therapeutic signal
            intensity: Attack intensity (0.0 to 1.0)
            
        Returns:
            Summary of all attacks and overall resilience
        """
        results = []
        
        # Test each attack type
        attacks = [
            AttackConfig(AttackType.NOISE_INJECTION, intensity, 1000),
            AttackConfig(AttackType.FREQUENCY_HIJACK, intensity, 1000, target_frequency=1000.0),
            AttackConfig(AttackType.PHASE_CORRUPTION, intensity, 1000),
            AttackConfig(AttackType.AMPLITUDE_SPIKE, intensity, 1000),
        ]
        
        for attack_config in attacks:
            if attack_config.attack_type == AttackType.NOISE_INJECTION:
                _, result = self.inject_noise(signal, attack_config)
            elif attack_config.attack_type == AttackType.FREQUENCY_HIJACK:
                _, result = self.hijack_frequency(signal, attack_config)
            elif attack_config.attack_type == AttackType.PHASE_CORRUPTION:
                _, result = self.corrupt_phase(signal, attack_config)
            elif attack_config.attack_type == AttackType.AMPLITUDE_SPIKE:
                _, result = self.inject_amplitude_spikes(signal, attack_config)
            
            results.append(result)
        
        # Calculate overall resilience
        avg_resilience = np.mean([r.resilience_score for r in results])
        successful_attacks = sum(1 for r in results if r.success)
        
        return {
            "total_attacks": len(results),
            "successful_attacks": successful_attacks,
            "average_resilience": float(avg_resilience),
            "attack_results": [
                {
                    "attack_type": r.attack_type.value,
                    "success": r.success,
                    "resilience_score": r.resilience_score,
                    "score_degradation": r.therapeutic_score_before - r.therapeutic_score_after,
                }
                for r in results
            ],
            "recommendation": self._generate_recommendation(avg_resilience),
        }
    
    def _calculate_therapeutic_score(self, signal: np.ndarray) -> float:
        """
        Calculate therapeutic effectiveness score
        
        Based on signal smoothness, energy consistency, and harmonic content
        """
        # Smoothness: lower variation is better
        if len(signal) > 1:
            diff = np.diff(signal)
            smoothness = 1.0 / (1.0 + np.std(diff))
        else:
            smoothness = 1.0
        
        # Energy consistency
        energy = signal ** 2
        energy_consistency = 1.0 / (1.0 + np.std(energy))
        
        # Combined score
        score = (smoothness + energy_consistency) / 2.0
        
        return float(np.clip(score, 0.0, 1.0))
    
    def _generate_recommendation(self, resilience: float) -> str:
        """Generate recommendation based on resilience score"""
        if resilience > 0.8:
            return "EXCELLENT: System shows strong resilience to attacks"
        elif resilience > 0.6:
            return "GOOD: System is reasonably resilient, minor improvements recommended"
        elif resilience > 0.4:
            return "FAIR: System needs improvement in signal protection"
        else:
            return "POOR: System requires significant hardening against attacks"
    
    def get_history(self) -> List[AttackResult]:
        """Get all attack history"""
        return self.attack_history
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        if not self.attack_history:
            return {"status": "No attacks performed yet"}
        
        return {
            "total_attacks": len(self.attack_history),
            "attack_types": list(set(r.attack_type.value for r in self.attack_history)),
            "average_resilience": float(np.mean([r.resilience_score for r in self.attack_history])),
            "successful_attacks": sum(1 for r in self.attack_history if r.success),
            "failed_attacks": sum(1 for r in self.attack_history if not r.success),
            "worst_vulnerability": min(
                self.attack_history,
                key=lambda r: r.resilience_score
            ).attack_type.value,
            "best_defense": max(
                self.attack_history,
                key=lambda r: r.resilience_score
            ).attack_type.value,
        }

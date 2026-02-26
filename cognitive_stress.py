"""
Cognitive Stress System - Intelligence Pressure and Limits

Enables:
- Irregular time cycles
- Environmental noise
- False signals
- Cognitive overload
- Real intelligence challenges
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import random
import math


class StressType(Enum):
    TEMPORAL_CHAOS = "temporal_chaos"
    FALSE_SIGNALS = "false_signals"
    INFORMATION_OVERLOAD = "information_overload"
    ENVIRONMENTAL_NOISE = "environmental_noise"
    COGNITIVE_STRAIN = "cognitive_strain"


@dataclass
class StressEvent:
    """A cognitive stress event."""
    step: int
    stress_type: StressType
    intensity: float
    affected_tribes: List[int]
    description: str


@dataclass
class CognitiveState:
    """Cognitive state of a tribe."""
    tribe_id: int
    accuracy_baseline: float = 1.0
    accuracy_modifier: float = 0.0
    overload_level: float = 0.0
    stress_history: List[float] = field(default_factory=list)
    adaptation: float = 0.0  # How much tribe has adapted to stress


class CognitiveStressSystem:
    """
    Applies cognitive stress to civilizations.
    
    This creates real challenges that test intelligence limits:
    - Temporal chaos: Irregular time cycles
    - False signals: Misleading artifacts
    - Information overload: Too many symbols
    - Environmental noise: Random perturbations
    """
    
    def __init__(
        self,
        chaos_intensity: float = 0.1,
        noise_level: float = 0.05,
        overload_threshold: int = 200,
        adaptation_rate: float = 0.01,
    ):
        self.chaos_intensity = chaos_intensity
        self.noise_level = noise_level
        self.overload_threshold = overload_threshold
        self.adaptation_rate = adaptation_rate
        
        # Tribal cognitive states
        self.tribe_states: Dict[int, CognitiveState] = {}
        
        # Stress events
        self.events: List[StressEvent] = []
        
        # Temporal chaos state
        self.time_distortion: float = 0.0
        self.chaos_phase: int = 0
        
        # False signal artifacts
        self.false_artifacts: List[Tuple[int, int, str]] = []
        
        # Statistics
        self.total_stress_events = 0
    
    # =====================================================
    # TEMPORAL CHAOS
    # =====================================================
    
    def apply_temporal_chaos(self, step: int, world_time: int) -> Tuple[int, float]:
        """
        Apply temporal chaos to time cycles.
        
        Args:
            step: Current simulation step
            world_time: Current world time (0-3 cycle)
            
        Returns:
            (distorted_time, chaos_level)
        """
        # Chaos intensity varies over time
        self.chaos_phase = (self.chaos_phase + 1) % 100
        
        # Sinusoidal chaos pattern
        base_chaos = math.sin(self.chaos_phase * 0.1) * self.chaos_intensity
        
        # Random spikes
        if random.random() < 0.05:  # 5% chance of spike
            base_chaos += random.uniform(-0.3, 0.3)
        
        self.time_distortion = base_chaos
        
        # Apply distortion
        if abs(self.time_distortion) > 0.1:
            # High chaos: random time jumps
            if random.random() < abs(self.time_distortion):
                distorted_time = random.randint(0, 3)
            else:
                distorted_time = (world_time + 1) % 4
        else:
            # Low chaos: normal progression with noise
            if random.random() < abs(self.time_distortion):
                distorted_time = (world_time + random.choice([0, 2])) % 4
            else:
                distorted_time = (world_time + 1) % 4
        
        # Record significant chaos
        if abs(base_chaos) > 0.2:
            self.events.append(StressEvent(
                step=step,
                stress_type=StressType.TEMPORAL_CHAOS,
                intensity=abs(base_chaos),
                affected_tribes=[],
                description=f"Temporal chaos level: {abs(base_chaos):.2f}",
            ))
            self.total_stress_events += 1
        
        return distorted_time, abs(base_chaos)
    
    # =====================================================
    # FALSE SIGNALS
    # =====================================================
    
    def generate_false_signals(
        self,
        step: int,
        world_size: Tuple[int, int],
        count: int = 3,
    ) -> List[Tuple[int, int, str]]:
        """
        Generate false artifact signals.
        
        Args:
            step: Current step
            world_size: (width, height) of world
            count: Number of false signals
            
        Returns:
            List of (x, y, signal_type) tuples
        """
        self.false_artifacts = []
        
        for _ in range(count):
            x = random.randint(0, world_size[0] - 1)
            y = random.randint(0, world_size[1] - 1)
            signal_type = random.choice(["fake_food", "fake_danger", "fake_artifact"])
            
            self.false_artifacts.append((x, y, signal_type))
        
        # Record
        if self.false_artifacts:
            self.events.append(StressEvent(
                step=step,
                stress_type=StressType.FALSE_SIGNALS,
                intensity=count * 0.1,
                affected_tribes=[],
                description=f"Generated {count} false signals",
            ))
            self.total_stress_events += 1
        
        return self.false_artifacts
    
    def is_false_signal(self, x: int, y: int) -> Tuple[bool, Optional[str]]:
        """Check if a location has a false signal."""
        for fx, fy, signal_type in self.false_artifacts:
            if fx == x and fy == y:
                return True, signal_type
        return False, None
    
    # =====================================================
    # INFORMATION OVERLOAD
    # =====================================================
    
    def check_overload(
        self,
        tribe_id: int,
        symbol_count: int,
        step: int,
    ) -> float:
        """
        Check if a tribe is experiencing information overload.
        
        Args:
            tribe_id: Tribe to check
            symbol_count: Number of symbols the tribe has
            step: Current step
            
        Returns:
            Overload level (0.0 - 1.0)
        """
        if tribe_id not in self.tribe_states:
            self.tribe_states[tribe_id] = CognitiveState(tribe_id=tribe_id)
        
        state = self.tribe_states[tribe_id]
        
        # Calculate overload
        if symbol_count > self.overload_threshold:
            overload = (symbol_count - self.overload_threshold) / self.overload_threshold
            overload = min(1.0, overload)
        else:
            overload = 0.0
        
        state.overload_level = overload
        state.stress_history.append(overload)
        
        # Keep history limited
        if len(state.stress_history) > 100:
            state.stress_history = state.stress_history[-100:]
        
        # Record significant overload
        if overload > 0.5:
            self.events.append(StressEvent(
                step=step,
                stress_type=StressType.INFORMATION_OVERLOAD,
                intensity=overload,
                affected_tribes=[tribe_id],
                description=f"Tribe {tribe_id} overloaded with {symbol_count} symbols",
            ))
            self.total_stress_events += 1
        
        return overload
    
    # =====================================================
    # ENVIRONMENTAL NOISE
    # =====================================================
    
    def apply_noise(self, value: float, tribe_id: int = None) -> float:
        """
        Apply environmental noise to a value.
        
        Args:
            value: Original value
            tribe_id: Optional tribe (for adaptation)
            
        Returns:
            Noisy value
        """
        noise = random.gauss(0, self.noise_level)
        
        # Apply adaptation
        if tribe_id and tribe_id in self.tribe_states:
            state = self.tribe_states[tribe_id]
            noise *= (1 - state.adaptation)
        
        return value + noise
    
    def apply_pattern_noise(self, pattern: tuple) -> tuple:
        """
        Apply noise to a pattern tuple.
        
        Args:
            pattern: Original pattern (food, danger, artifact, time)
            
        Returns:
            Possibly modified pattern
        """
        if not pattern or len(pattern) < 4:
            return pattern
        
        food, danger, artifact, time = pattern
        
        # Randomly flip bits with low probability
        if random.random() < self.noise_level:
            food = 1 - food if random.random() < 0.5 else food
        if random.random() < self.noise_level:
            danger = 1 - danger if random.random() < 0.5 else danger
        if random.random() < self.noise_level:
            time = (time + random.choice([-1, 1])) % 4
        
        return (food, danger, artifact, time)
    
    # =====================================================
    # COGNITIVE STRAIN
    # =====================================================
    
    def calculate_accuracy_modifier(
        self,
        tribe_id: int,
        symbol_count: int,
        population: int,
    ) -> float:
        """
        Calculate the accuracy modifier for a tribe.
        
        Args:
            tribe_id: Tribe ID
            symbol_count: Number of symbols
            population: Tribe population
            
        Returns:
            Accuracy modifier (-0.3 to 0.1)
        """
        if tribe_id not in self.tribe_states:
            self.tribe_states[tribe_id] = CognitiveState(tribe_id=tribe_id)
        
        state = self.tribe_states[tribe_id]
        
        # Base from overload
        overload_penalty = -state.overload_level * 0.2
        
        # Time distortion penalty
        chaos_penalty = -abs(self.time_distortion) * 0.1
        
        # Population pressure (more agents = more coordination needed)
        pop_penalty = -min(0.1, population / 100 * 0.05)
        
        # Adaptation bonus
        adaptation_bonus = state.adaptation * 0.1
        
        # Learning bonus (tribes under stress learn to cope)
        if len(state.stress_history) > 10:
            recent_stress = sum(state.stress_history[-10:]) / 10
            if recent_stress > 0.3:
                state.adaptation = min(1.0, state.adaptation + self.adaptation_rate)
        
        total = overload_penalty + chaos_penalty + pop_penalty + adaptation_bonus
        
        # Clamp
        total = max(-0.3, min(0.1, total))
        
        state.accuracy_modifier = total
        return total
    
    # =====================================================
    # TRIBE ADAPTATION
    # =====================================================
    
    def adapt_tribe(self, tribe_id: int, stress_level: float):
        """
        Increase tribe's adaptation to stress.
        
        Args:
            tribe_id: Tribe to adapt
            stress_level: Current stress level
        """
        if tribe_id not in self.tribe_states:
            self.tribe_states[tribe_id] = CognitiveState(tribe_id=tribe_id)
        
        state = self.tribe_states[tribe_id]
        
        # Adaptation increases with stress exposure
        if stress_level > 0.3:
            state.adaptation = min(1.0, state.adaptation + self.adaptation_rate)
    
    def get_tribe_intelligence_ceiling(self, tribe_id: int) -> float:
        """
        Get the maximum achievable intelligence for a tribe.
        
        Under stress, intelligence has a ceiling.
        """
        if tribe_id not in self.tribe_states:
            return 1.0
        
        state = self.tribe_states[tribe_id]
        
        # Base ceiling
        ceiling = 1.0
        
        # Reduce by overload
        ceiling -= state.overload_level * 0.2
        
        # Reduce by time chaos
        ceiling -= abs(self.time_distortion) * 0.1
        
        # Increase by adaptation
        ceiling += state.adaptation * 0.15
        
        return max(0.5, min(1.0, ceiling))
    
    # =====================================================
    # STATUS
    # =====================================================
    
    def get_stress_level(self, tribe_id: int) -> float:
        """Get current stress level for a tribe."""
        if tribe_id not in self.tribe_states:
            return 0.0
        
        state = self.tribe_states[tribe_id]
        
        # Combine all stress factors
        overload = state.overload_level
        chaos = abs(self.time_distortion)
        
        return (overload + chaos) / 2
    
    def status(self) -> dict:
        """Get overall status."""
        return {
            'time_distortion': self.time_distortion,
            'false_signals': len(self.false_artifacts),
            'stressed_tribes': len([s for s in self.tribe_states.values() if s.overload_level > 0.5]),
            'total_stress_events': self.total_stress_events,
        }
    
    def summary(self) -> str:
        """Get human-readable summary."""
        s = self.status()
        return (
            f"🧠 Cognitive Stress\n"
            f"   Time Distortion: {s['time_distortion']:.2f}\n"
            f"   False Signals: {s['false_signals']}\n"
            f"   Stressed Tribes: {s['stressed_tribes']}\n"
            f"   Total Events: {s['total_stress_events']}\n"
        )
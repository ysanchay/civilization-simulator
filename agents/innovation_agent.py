"""
InnovationAgent

IDENTITY: "I am the spark. I create novelty and drive exploration."

ROLE: Innovation, exploration, and creativity

RESPONSIBILITIES:
- Reward novel behaviors and symbol combinations
- Detect innovation (new patterns, new strategies)
- Apply exploration bonuses
- Handle creative recombination of existing symbols
- Track innovation metrics per tribe/agent
- Balance exploitation vs exploration
"""

import random
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class InnovationType(Enum):
    NEW_PATTERN = "new_pattern"
    NEW_TRANSITION = "new_transition"
    NEW_COMPOSITION = "new_composition"
    NEW_META = "new_meta"
    NEW_STRATEGY = "new_strategy"
    NEW_BEHAVIOR = "new_behavior"


@dataclass
class Innovation:
    """Represents an innovation event."""
    innovation_type: InnovationType
    source: Any  # Pattern, symbol, or behavior that was innovative
    tribe_id: int
    agent_name: Optional[str]
    step: int
    reward: float = 0.0
    impact: float = 0.0  # How much it affected the population


class InnovationAgent:
    """
    Manages innovation, exploration, and creativity in the simulation.
    
    Encourages novel behaviors and tracks innovation metrics.
    """
    
    def __init__(
        self,
        exploration_bonus: float = 2.0,
        novelty_threshold: int = 5,
        recombination_rate: float = 0.1,
        exploitation_decay: float = 0.95,
    ):
        self.exploration_bonus = exploration_bonus
        self.novelty_threshold = novelty_threshold
        self.recombination_rate = recombination_rate
        self.exploitation_decay = exploitation_decay
        
        # Tracking
        self.seen_patterns: Set[Any] = set()
        self.seen_transitions: Set[Tuple[Any, Any]] = set()
        self.seen_compositions: Set[Any] = set()
        
        # Pattern frequency (for novelty detection)
        self.pattern_frequency: Dict[Any, int] = defaultdict(int)
        self.transition_frequency: Dict[Tuple[Any, Any], int] = defaultdict(int)
        
        # Innovation history
        self.innovations: List[Innovation] = []
        self.tribe_innovations: Dict[int, List[Innovation]] = defaultdict(list)
        
        # Exploration vs exploitation tracking
        self.exploration_counts: Dict[int, int] = defaultdict(int)  # tribe -> count
        self.exploitation_counts: Dict[int, int] = defaultdict(int)  # tribe -> count
        
        # Recombination suggestions
        self.recombination_queue: List[Tuple[int, Any, Any]] = []  # (tribe, symbol1, symbol2)
        
        # Statistics
        self.total_innovations = 0
        self.total_recombinations = 0
        self.innovation_impact_sum = 0.0
    
    # =====================================================
    # NOVELTY DETECTION
    # =====================================================
    
    def is_novel(self, pattern: Any) -> bool:
        """
        Check if a pattern is novel.
        
        Args:
            pattern: Pattern to check
            
        Returns:
            True if pattern is novel (seen fewer than threshold times)
        """
        freq = self.pattern_frequency.get(pattern, 0)
        return freq < self.novelty_threshold
    
    def detect_pattern_novelty(
        self,
        pattern: Any,
        tribe_id: int,
        agent_name: Optional[str] = None,
        step: int = 0,
    ) -> Optional[Innovation]:
        """
        Detect and record a novel pattern.
        
        Args:
            pattern: Observed pattern
            tribe_id: Tribe observing the pattern
            agent_name: Agent name (optional)
            step: Current step
            
        Returns:
            Innovation if novel, None otherwise
        """
        self.pattern_frequency[pattern] += 1
        
        if pattern not in self.seen_patterns:
            self.seen_patterns.add(pattern)
            
            innovation = Innovation(
                innovation_type=InnovationType.NEW_PATTERN,
                source=pattern,
                tribe_id=tribe_id,
                agent_name=agent_name,
                step=step,
                reward=self.exploration_bonus,
            )
            
            self._record_innovation(innovation)
            return innovation
        
        return None
    
    def detect_transition_novelty(
        self,
        from_pattern: Any,
        to_pattern: Any,
        tribe_id: int,
        step: int = 0,
    ) -> Optional[Innovation]:
        """
        Detect a novel transition between patterns.
        
        Args:
            from_pattern: Source pattern
            to_pattern: Target pattern
            tribe_id: Tribe ID
            step: Current step
            
        Returns:
            Innovation if novel, None otherwise
        """
        key = (from_pattern, to_pattern)
        self.transition_frequency[key] += 1
        
        if key not in self.seen_transitions:
            self.seen_transitions.add(key)
            
            innovation = Innovation(
                innovation_type=InnovationType.NEW_TRANSITION,
                source=key,
                tribe_id=tribe_id,
                agent_name=None,
                step=step,
                reward=self.exploration_bonus * 0.5,
            )
            
            self._record_innovation(innovation)
            return innovation
        
        return None
    
    def detect_composition_novelty(
        self,
        composition: Any,
        tribe_id: int,
        step: int = 0,
    ) -> Optional[Innovation]:
        """
        Detect a novel symbol composition.
        
        Args:
            composition: Composed symbol
            tribe_id: Tribe ID
            step: Current step
            
        Returns:
            Innovation if novel, None otherwise
        """
        if composition not in self.seen_compositions:
            self.seen_compositions.add(composition)
            
            innovation = Innovation(
                innovation_type=InnovationType.NEW_COMPOSITION,
                source=composition,
                tribe_id=tribe_id,
                agent_name=None,
                step=step,
                reward=self.exploration_bonus * 2.0,  # Higher reward for composition
            )
            
            self._record_innovation(innovation)
            return innovation
        
        return None
    
    # =====================================================
    # EXPLORATION BONUSES
    # =====================================================
    
    def get_exploration_bonus(
        self,
        pattern: Any,
        tribe_id: int,
    ) -> float:
        """
        Calculate exploration bonus for a pattern.
        
        Args:
            pattern: Pattern to evaluate
            tribe_id: Tribe ID
            
        Returns:
            Exploration bonus value
        """
        if self.is_novel(pattern):
            self.exploration_counts[tribe_id] += 1
            return self.exploration_bonus
        
        # Decay bonus based on frequency
        freq = self.pattern_frequency.get(pattern, 0)
        return self.exploration_bonus * (self.exploitation_decay ** freq)
    
    def record_exploitation(self, tribe_id: int):
        """Record an exploitation action (using known pattern)."""
        self.exploitation_counts[tribe_id] += 1
    
    def get_exploration_rate(self, tribe_id: int) -> float:
        """Get exploration rate for a tribe."""
        total = self.exploration_counts[tribe_id] + self.exploitation_counts[tribe_id]
        if total == 0:
            return 0.5
        return self.exploration_counts[tribe_id] / total
    
    # =====================================================
    # CREATIVE RECOMBINATION
    # =====================================================
    
    def suggest_recombination(
        self,
        tribe_symbols: List[Any],
        tribe_id: int,
    ) -> Optional[Tuple[Any, Any]]:
        """
        Suggest a creative recombination of existing symbols.
        
        Args:
            tribe_symbols: List of tribe's symbols
            tribe_id: Tribe ID
            
        Returns:
            Tuple of symbols to combine, or None
        """
        if len(tribe_symbols) < 2:
            return None
        
        if random.random() > self.recombination_rate:
            return None
        
        # Pick two random symbols to combine
        s1, s2 = random.sample(tribe_symbols, 2)
        
        # Check if this combination is novel
        key = frozenset([str(s1), str(s2)])
        if key in self.seen_compositions:
            return None
        
        # Add to queue
        self.recombination_queue.append((tribe_id, s1, s2))
        
        return (s1, s2)
    
    def get_recombinations(self, tribe_id: int) -> List[Tuple[Any, Any]]:
        """
        Get pending recombination suggestions for a tribe.
        
        Args:
            tribe_id: Tribe ID
            
        Returns:
            List of (symbol1, symbol2) tuples
        """
        recombinations = []
        remaining = []
        
        for tid, s1, s2 in self.recombination_queue:
            if tid == tribe_id:
                recombinations.append((s1, s2))
            else:
                remaining.append((tid, s1, s2))
        
        self.recombination_queue = remaining
        return recombinations
    
    def apply_recombination(
        self,
        s1: Any,
        s2: Any,
        tribe_id: int,
        step: int = 0,
    ) -> Innovation:
        """
        Apply a recombination and create an innovation.
        
        Args:
            s1: First symbol
            s2: Second symbol
            tribe_id: Tribe ID
            step: Current step
            
        Returns:
            Innovation record
        """
        self.total_recombinations += 1
        
        innovation = Innovation(
            innovation_type=InnovationType.NEW_STRATEGY,
            source=(s1, s2),
            tribe_id=tribe_id,
            agent_name=None,
            step=step,
            reward=self.exploration_bonus * 3.0,  # Highest reward for recombination
        )
        
        self._record_innovation(innovation)
        return innovation
    
    # =====================================================
    # INNOVATION TRACKING
    # =====================================================
    
    def _record_innovation(self, innovation: Innovation):
        """Record an innovation."""
        self.innovations.append(innovation)
        self.tribe_innovations[innovation.tribe_id].append(innovation)
        self.total_innovations += 1
    
    def update_innovation_impact(
        self,
        innovation: Innovation,
        impact: float,
    ):
        """
        Update the impact of an innovation.
        
        Args:
            innovation: Innovation to update
            impact: Impact value (e.g., population change)
        """
        innovation.impact = impact
        self.innovation_impact_sum += impact
    
    def get_tribe_innovation_score(self, tribe_id: int) -> float:
        """
        Calculate innovation score for a tribe.
        
        Args:
            tribe_id: Tribe ID
            
        Returns:
            Innovation score
        """
        innovations = self.tribe_innovations.get(tribe_id, [])
        if not innovations:
            return 0.0
        
        # Weight by recency and impact
        score = 0.0
        for inn in innovations:
            # Impact contribution
            score += inn.impact * 0.5
            # Type contribution
            type_weights = {
                InnovationType.NEW_PATTERN: 1.0,
                InnovationType.NEW_TRANSITION: 1.5,
                InnovationType.NEW_COMPOSITION: 2.0,
                InnovationType.NEW_META: 3.0,
                InnovationType.NEW_STRATEGY: 2.5,
                InnovationType.NEW_BEHAVIOR: 2.0,
            }
            score += type_weights.get(inn.innovation_type, 1.0)
        
        return score
    
    def get_most_innovative_tribes(self, n: int = 5) -> List[Tuple[int, float]]:
        """
        Get the top N most innovative tribes.
        
        Args:
            n: Number of tribes to return
            
        Returns:
            List of (tribe_id, score) tuples
        """
        scores = [
            (tribe_id, self.get_tribe_innovation_score(tribe_id))
            for tribe_id in self.tribe_innovations
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:n]
    
    # =====================================================
    # INNOVATION PRESSURE
    # =====================================================
    
    def calculate_innovation_pressure(
        self,
        tribe_id: int,
        population: int,
    ) -> float:
        """
        Calculate innovation pressure on a tribe.
        
        Higher pressure when:
        - Low exploration rate
        - Low innovation score relative to others
        - High population (crowding)
        
        Args:
            tribe_id: Tribe ID
            population: Tribe population
            
        Returns:
            Pressure value
        """
        exploration_rate = self.get_exploration_rate(tribe_id)
        
        # Pressure to explore if rate is low
        exploration_pressure = (1 - exploration_rate) * 0.5
        
        # Population pressure
        population_pressure = min(1.0, population / 50) * 0.3
        
        # Relative innovation pressure
        avg_score = self.innovation_impact_sum / max(1, len(self.tribe_innovations))
        tribe_score = self.get_tribe_innovation_score(tribe_id)
        innovation_pressure = max(0, avg_score - tribe_score) * 0.2
        
        return exploration_pressure + population_pressure + innovation_pressure
    
    # =====================================================
    # STATUS
    # =====================================================
    
    def status(self) -> Dict[str, Any]:
        """Get innovation status."""
        return {
            'total_innovations': self.total_innovations,
            'total_recombinations': self.total_recombinations,
            'unique_patterns': len(self.seen_patterns),
            'unique_transitions': len(self.seen_transitions),
            'unique_compositions': len(self.seen_compositions),
            'pending_recombinations': len(self.recombination_queue),
            'avg_exploration_rate': sum(self.exploration_counts.values()) / max(1, len(self.exploration_counts)),
            'top_innovators': self.get_most_innovative_tribes(3),
        }
    
    def summary(self) -> str:
        """Get human-readable summary."""
        s = self.status()
        return (
            f"💡 Innovation Status\n"
            f"   Innovations: {s['total_innovations']}\n"
            f"   Recombinations: {s['total_recombinations']}\n"
            f"   Unique Patterns: {s['unique_patterns']}\n"
            f"   Unique Transitions: {s['unique_transitions']}\n"
            f"   Unique Compositions: {s['unique_compositions']}\n"
            f"   Top Innovators: {s['top_innovators']}\n"
        )
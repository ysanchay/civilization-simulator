"""
Collapse System - Civilization Rise and Fall

Enables:
- Collapse cascade
- Knowledge bottleneck crisis
- Complexity crisis
- Renaissance after collapse
- Cultural debt
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random


class CollapseType(Enum):
    POPULATION_COLLAPSE = "population_collapse"
    COMPLEXITY_CRISIS = "complexity_crisis"
    KNOWLEDGE_BOTTLENECK = "knowledge_bottleneck"
    TERRITORIAL_LOSS = "territorial_loss"
    CULTURAL_DEBT = "cultural_debt"
    COORDINATION_FAILURE = "coordination_failure"


class CollapseStage(Enum):
    STABLE = "stable"
    STRESSED = "stressed"
    DECLINING = "declining"
    COLLAPSING = "collapsing"
    EXTINCT = "extinct"
    RECOVERING = "recovering"


@dataclass
class CollapseEvent:
    """Record of a collapse event."""
    step: int
    tribe_id: int
    collapse_type: CollapseType
    severity: float
    population_before: int
    population_after: int
    symbols_lost: int
    territory_lost: int
    description: str


@dataclass
class CollapseState:
    """Collapse state for a tribe."""
    tribe_id: int
    stage: CollapseStage = CollapseStage.STABLE
    stress_level: float = 0.0
    complexity_burden: float = 0.0
    cultural_debt: float = 0.0
    knowledge_bottleneck: float = 0.0
    collapse_count: int = 0
    recovery_count: int = 0
    peak_population: int = 0
    peak_symbols: int = 0
    peak_territory: int = 0


@dataclass
class RenaissanceEvent:
    """Record of a renaissance event."""
    step: int
    tribe_id: int
    golden_age_length: int
    symbols_recovered: int
    description: str


class CollapseSystem:
    """
    Manages civilization collapse and renaissance.
    
    Enables:
    - Collapse cascade
    - Knowledge bottleneck
    - Complexity crisis
    - Cultural debt
    - Renaissance recovery
    """
    
    # Collapse thresholds
    POPULATION_COLLAPSE_THRESHOLD = 0.3  # 30% population loss triggers collapse
    COMPLEXITY_THRESHOLD = 0.8  # High complexity triggers crisis
    KNOWLEDGE_THRESHOLD = 0.5  # Low knowledge retention triggers bottleneck
    CULTURAL_DEBT_THRESHOLD = 0.7  # High cultural debt triggers collapse
    
    # Recovery thresholds
    RECOVERY_POPULATION = 10  # Minimum population to recover
    RECOVERY_SYMBOLS = 20  # Minimum symbols to recover
    
    def __init__(
        self,
        enable_cascades: bool = True,
        cascade_probability: float = 0.3,
    ):
        self.enable_cascades = enable_cascades
        self.cascade_prob = cascade_probability
        
        # Tribe states
        self.states: Dict[int, CollapseState] = {}
        
        # Event history
        self.collapses: List[CollapseEvent] = []
        self.renaissances: List[RenaissanceEvent] = []
        
        # Statistics
        self.total_collapses = 0
        self.total_extinctions = 0
        self.total_renaissances = 0
    
    # =====================================================
    # STATE TRACKING
    # =====================================================
    
    def update_tribe(
        self,
        tribe_id: int,
        population: int,
        symbols: int,
        territory: int,
        efficiency: float,
        coordination_cost: float,
    ) -> CollapseState:
        """
        Update collapse state for a tribe.
        
        Args:
            tribe_id: Tribe ID
            population: Current population
            symbols: Current symbol count
            territory: Current territory size
            efficiency: Current efficiency (from scaling)
            coordination_cost: Coordination cost
            
        Returns:
            Updated collapse state
        """
        if tribe_id not in self.states:
            self.states[tribe_id] = CollapseState(tribe_id=tribe_id)
        
        state = self.states[tribe_id]
        
        # Update peaks
        state.peak_population = max(state.peak_population, population)
        state.peak_symbols = max(state.peak_symbols, symbols)
        state.peak_territory = max(state.peak_territory, territory)
        
        # Calculate complexity burden
        state.complexity_burden = self._calculate_complexity(
            population, symbols, territory, coordination_cost
        )
        
        # Calculate knowledge bottleneck
        if state.peak_symbols > 0:
            state.knowledge_bottleneck = 1.0 - (symbols / state.peak_symbols)
        else:
            state.knowledge_bottleneck = 0.0
        
        # Calculate cultural debt
        state.cultural_debt = self._calculate_cultural_debt(
            efficiency, state.collapse_count
        )
        
        # Calculate overall stress
        state.stress_level = self._calculate_stress(state)
        
        # Determine stage
        state.stage = self._determine_stage(state, population)
        
        return state
    
    def _calculate_complexity(
        self,
        population: int,
        symbols: int,
        territory: int,
        coordination_cost: float,
    ) -> float:
        """Calculate complexity burden."""
        # Complexity grows with size
        pop_complexity = population / 100
        symbol_complexity = symbols / 200
        territory_complexity = territory / 50
        
        total = (pop_complexity + symbol_complexity + territory_complexity) / 3
        total += coordination_cost * 0.5
        
        return min(1.0, total)
    
    def _calculate_cultural_debt(
        self,
        efficiency: float,
        collapse_count: int,
    ) -> float:
        """Calculate cultural debt from past collapses."""
        debt = (1.0 - efficiency) * 0.5
        debt += collapse_count * 0.1
        return min(1.0, debt)
    
    def _calculate_stress(self, state: CollapseState) -> float:
        """Calculate overall stress level."""
        stress = (
            state.complexity_burden * 0.3 +
            state.knowledge_bottleneck * 0.3 +
            state.cultural_debt * 0.2 +
            state.stress_level * 0.2  # Previous stress
        )
        return min(1.0, stress)
    
    def _determine_stage(
        self,
        state: CollapseState,
        population: int,
    ) -> CollapseStage:
        """Determine collapse stage."""
        if population == 0:
            return CollapseStage.EXTINCT
        
        if state.stress_level < 0.3:
            if state.collapse_count > 0:
                return CollapseStage.RECOVERING
            return CollapseStage.STABLE
        
        if state.stress_level < 0.5:
            return CollapseStage.STRESSED
        
        if state.stress_level < 0.7:
            return CollapseStage.DECLINING
        
        return CollapseStage.COLLAPSING
    
    # =====================================================
    # COLLAPSE CHECKING
    # =====================================================
    
    def check_collapse(
        self,
        step: int,
        tribe_id: int,
        population: int,
        symbols: int,
        territory: int,
    ) -> Optional[CollapseEvent]:
        """
        Check if a collapse should occur.
        
        Args:
            step: Current step
            tribe_id: Tribe ID
            population: Current population
            symbols: Current symbols
            territory: Current territory
            
        Returns:
            CollapseEvent if collapse occurred
        """
        if tribe_id not in self.states:
            return None
        
        state = self.states[tribe_id]
        
        # Check for extinction
        if population == 0:
            return self._record_extinction(step, tribe_id, state)
        
        # Determine collapse type
        collapse_type = self._check_collapse_conditions(state, population)
        
        if collapse_type is None:
            return None
        
        # Calculate severity
        severity = state.stress_level
        
        # Calculate losses
        pop_loss = int(population * severity * random.uniform(0.3, 0.7))
        symbols_lost = int(symbols * severity * random.uniform(0.2, 0.5))
        territory_lost = int(territory * severity * random.uniform(0.1, 0.3))
        
        # Create event
        event = CollapseEvent(
            step=step,
            tribe_id=tribe_id,
            collapse_type=collapse_type,
            severity=severity,
            population_before=population,
            population_after=max(1, population - pop_loss),
            symbols_lost=symbols_lost,
            territory_lost=territory_lost,
            description=self._get_collapse_description(collapse_type, severity),
        )
        
        self.collapses.append(event)
        self.total_collapses += 1
        state.collapse_count += 1
        
        # Trigger cascade?
        if self.enable_cascades and random.random() < self.cascade_prob * severity:
            self._trigger_cascade(tribe_id, severity)
        
        return event
    
    def _check_collapse_conditions(
        self,
        state: CollapseState,
        population: int,
    ) -> Optional[CollapseType]:
        """Check which collapse condition is met."""
        # Population collapse
        if state.peak_population > 0:
            pop_ratio = population / state.peak_population
            if pop_ratio < self.POPULATION_COLLAPSE_THRESHOLD:
                return CollapseType.POPULATION_COLLAPSE
        
        # Complexity crisis
        if state.complexity_burden > self.COMPLEXITY_THRESHOLD:
            return CollapseType.COMPLEXITY_CRISIS
        
        # Knowledge bottleneck
        if state.knowledge_bottleneck > self.KNOWLEDGE_THRESHOLD:
            return CollapseType.KNOWLEDGE_BOTTLENECK
        
        # Cultural debt
        if state.cultural_debt > self.CULTURAL_DEBT_THRESHOLD:
            return CollapseType.CULTURAL_DEBT
        
        return None
    
    def _record_extinction(
        self,
        step: int,
        tribe_id: int,
        state: CollapseState,
    ) -> CollapseEvent:
        """Record tribe extinction."""
        self.total_extinctions += 1
        state.stage = CollapseStage.EXTINCT
        
        return CollapseEvent(
            step=step,
            tribe_id=tribe_id,
            collapse_type=CollapseType.POPULATION_COLLAPSE,
            severity=1.0,
            population_before=state.peak_population,
            population_after=0,
            symbols_lost=state.peak_symbols,
            territory_lost=state.peak_territory,
            description=f"Tribe {tribe_id} went extinct",
        )
    
    def _trigger_cascade(self, tribe_id: int, severity: float):
        """Trigger cascade effects."""
        # Increase stress on neighboring tribes
        # This is called by the main simulation
        pass
    
    def _get_collapse_description(
        self,
        collapse_type: CollapseType,
        severity: float,
    ) -> str:
        """Get human-readable collapse description."""
        descriptions = {
            CollapseType.POPULATION_COLLAPSE: f"Population collapse ({severity:.0%} severity)",
            CollapseType.COMPLEXITY_CRISIS: f"Complexity crisis - system overloaded ({severity:.0%})",
            CollapseType.KNOWLEDGE_BOTTLENECK: f"Knowledge bottleneck - lost critical symbols",
            CollapseType.CULTURAL_DEBT: f"Cultural debt crisis - past burdens overwhelmed",
            CollapseType.TERRITORIAL_LOSS: "Territorial collapse - lost homeland",
            CollapseType.COORDINATION_FAILURE: "Coordination failure - communication broke down",
        }
        return descriptions.get(collapse_type, "Unknown collapse")
    
    # =====================================================
    # RECOVERY & RENAISSANCE
    # =====================================================
    
    def check_recovery(
        self,
        step: int,
        tribe_id: int,
        population: int,
        symbols: int,
    ) -> Optional[RenaissanceEvent]:
        """
        Check if a tribe is recovering/entering renaissance.
        
        Args:
            step: Current step
            tribe_id: Tribe ID
            population: Current population
            symbols: Current symbols
            
        Returns:
            RenaissanceEvent if renaissance occurred
        """
        if tribe_id not in self.states:
            return None
        
        state = self.states[tribe_id]
        
        # Must have collapsed before
        if state.collapse_count == 0:
            return None
        
        # Must be in recovering stage
        if state.stage != CollapseStage.RECOVERING:
            return None
        
        # Check recovery conditions
        if population < self.RECOVERY_POPULATION:
            return None
        
        if symbols < self.RECOVERY_SYMBOLS:
            return None
        
        # Calculate golden age length
        golden_age_length = step - (state.peak_population // 10)  # Rough estimate
        
        # Create renaissance event
        event = RenaissanceEvent(
            step=step,
            tribe_id=tribe_id,
            golden_age_length=golden_age_length,
            symbols_recovered=symbols,
            description=f"Tribe {tribe_id} experienced a renaissance after {state.collapse_count} collapse(s)",
        )
        
        self.renaissances.append(event)
        self.total_renaissances += 1
        state.recovery_count += 1
        
        # Reset state
        state.peak_population = population
        state.peak_symbols = symbols
        state.collapse_count = 0
        state.cultural_debt *= 0.5  # Reduce debt
        
        return event
    
    # =====================================================
    # GET LOSSES
    # =====================================================
    
    def get_population_loss(self, severity: float) -> int:
        """Get population loss for a collapse."""
        return int(10 * severity * random.uniform(5, 15))
    
    def get_symbol_loss(self, symbols: int, severity: float) -> int:
        """Get symbol loss for a collapse."""
        return int(symbols * severity * random.uniform(0.3, 0.6))
    
    def get_territory_loss(self, territory: int, severity: float) -> int:
        """Get territory loss for a collapse."""
        return int(territory * severity * random.uniform(0.2, 0.5))
    
    # =====================================================
    # STATUS
    # =====================================================
    
    def get_state(self, tribe_id: int) -> Optional[CollapseState]:
        """Get collapse state for a tribe."""
        return self.states.get(tribe_id)
    
    def get_stability(self, tribe_id: int) -> float:
        """Get stability score for a tribe."""
        state = self.states.get(tribe_id)
        if not state:
            return 1.0
        
        return 1.0 - state.stress_level
    
    def status(self) -> dict:
        """Get overall status."""
        stages = [s.stage for s in self.states.values()]
        
        return {
            'total_collapses': self.total_collapses,
            'total_extinctions': self.total_extinctions,
            'total_renaissances': self.total_renaissances,
            'stable_tribes': stages.count(CollapseStage.STABLE),
            'stressed_tribes': stages.count(CollapseStage.STRESSED),
            'declining_tribes': stages.count(CollapseStage.DECLINING),
            'collapsing_tribes': stages.count(CollapseStage.COLLAPSING),
            'recovering_tribes': stages.count(CollapseStage.RECOVERING),
        }
    
    def summary(self) -> str:
        """Get human-readable summary."""
        s = self.status()
        return (
            f"💥 Collapse System\n"
            f"   Total Collapses: {s['total_collapses']}\n"
            f"   Total Extinctions: {s['total_extinctions']}\n"
            f"   Renaissances: {s['total_renaissances']}\n"
            f"   Stable: {s['stable_tribes']} | Stressed: {s['stressed_tribes']}\n"
            f"   Declining: {s['declining_tribes']} | Collapsing: {s['collapsing_tribes']}\n"
            f"   Recovering: {s['recovering_tribes']}\n"
        )
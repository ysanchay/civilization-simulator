"""
Scaling Penalties System - Empire Fragility

Enables:
- Administrative load
- Coordination failure at scale
- Bureaucratic overhead
- Empire collapse from size
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import math


class FailureType(Enum):
    COORDINATION_FAILURE = "coordination_failure"
    ADMINISTRATIVE_COLLAPSE = "administrative_collapse"
    SYMBOL_OVERLOAD = "symbol_overload"
    TERRITORY_STRAIN = "territory_strain"
    COMMUNICATION_BREAKDOWN = "communication_breakdown"


@dataclass
class FailureEvent:
    """A scaling failure event."""
    step: int
    tribe_id: int
    failure_type: FailureType
    severity: float
    impact: str
    affected_agents: int = 0


@dataclass
class ScalingMetrics:
    """Scaling metrics for a tribe."""
    tribe_id: int
    population: int = 0
    territory_size: int = 0
    symbol_count: int = 0
    administrative_load: float = 0.0
    coordination_cost: float = 0.0
    efficiency: float = 1.0
    failure_risk: float = 0.0
    critical_size: bool = False


class ScalingPenaltySystem:
    """
    Applies penalties for large civilizations.
    
    Large empires face:
    - Coordination costs
    - Administrative overhead
    - Communication delays
    - Bureaucratic failure
    
    This creates realistic empire fragility.
    """
    
    # Scaling constants
    POPULATION_SCALING_FACTOR = 0.02  # Administrative cost per agent
    TERRITORY_SCALING_FACTOR = 0.01   # Coordination cost per cell
    SYMBOL_SCALING_FACTOR = 0.005     # Cognitive cost per symbol
    
    OPTIMAL_SIZE = 20  # Optimal population
    CRITICAL_SIZE = 50  # Critical population threshold
    COLLAPSE_SIZE = 100  # Near-certain collapse
    
    def __init__(
        self,
        enable_coordination_failure: bool = True,
        enable_administrative_collapse: bool = True,
        enable_symbol_overload: bool = True,
    ):
        self.enable_coordination = enable_coordination_failure
        self.enable_admin = enable_administrative_collapse
        self.enable_overload = enable_symbol_overload
        
        # Tribe metrics
        self.metrics: Dict[int, ScalingMetrics] = {}
        
        # Failure events
        self.failures: List[FailureEvent] = []
        
        # Statistics
        self.total_failures = 0
        self.total_collapses = 0
    
    # =====================================================
    # SCALING CALCULATIONS
    # =====================================================
    
    def calculate_administrative_load(
        self,
        population: int,
        territory_size: int,
    ) -> float:
        """
        Calculate administrative load for a tribe.
        
        Args:
            population: Number of agents
            territory_size: Number of controlled cells
            
        Returns:
            Administrative load (0.0 - 1.0+)
        """
        # Population creates administrative overhead
        # Diminishing returns: more efficient at small scales
        if population <= self.OPTIMAL_SIZE:
            pop_load = population * self.POPULATION_SCALING_FACTOR * 0.5
        else:
            # Quadratic growth after optimal
            excess = population - self.OPTIMAL_SIZE
            pop_load = (self.OPTIMAL_SIZE * self.POPULATION_SCALING_FACTOR * 0.5 +
                       excess * self.POPULATION_SCALING_FACTOR * (1 + excess / 50))
        
        # Territory adds coordination cost
        territory_load = territory_size * self.TERRITORY_SCALING_FACTOR
        
        return pop_load + territory_load
    
    def calculate_coordination_cost(
        self,
        population: int,
        territory_size: int,
        symbol_count: int,
    ) -> float:
        """
        Calculate coordination cost for a tribe.
        
        Args:
            population: Number of agents
            territory_size: Number of controlled cells
            symbol_count: Number of cultural symbols
            
        Returns:
            Coordination cost (0.0 - 1.0+)
        """
        # Communication distance grows with territory
        territory_cost = math.sqrt(territory_size) * 0.01
        
        # More agents = more coordination
        pop_cost = (population / 10) * 0.02
        
        # More symbols = more communication overhead
        symbol_cost = symbol_count * self.SYMBOL_SCALING_FACTOR
        
        return territory_cost + pop_cost + symbol_cost
    
    def calculate_efficiency(
        self,
        administrative_load: float,
        coordination_cost: float,
    ) -> float:
        """
        Calculate overall efficiency.
        
        Args:
            administrative_load: Administrative overhead
            coordination_cost: Coordination cost
            
        Returns:
            Efficiency (0.0 - 1.0)
        """
        total_cost = administrative_load + coordination_cost
        
        # Efficiency decreases exponentially with cost
        efficiency = math.exp(-total_cost * 0.5)
        
        return max(0.1, min(1.0, efficiency))
    
    def calculate_failure_risk(
        self,
        population: int,
        efficiency: float,
        administrative_load: float,
    ) -> float:
        """
        Calculate risk of scaling failure.
        
        Args:
            population: Number of agents
            efficiency: Current efficiency
            administrative_load: Administrative overhead
            
        Returns:
            Failure risk (0.0 - 1.0)
        """
        risk = 0.0
        
        # Size risk
        if population > self.CRITICAL_SIZE:
            risk += (population - self.CRITICAL_SIZE) / self.COLLAPSE_SIZE
        
        if population > self.COLLAPSE_SIZE:
            risk += 0.5  # Additional risk
        
        # Efficiency risk
        if efficiency < 0.5:
            risk += (0.5 - efficiency) * 2
        
        # Load risk
        if administrative_load > 1.0:
            risk += (administrative_load - 1.0) * 0.5
        
        return min(1.0, risk)
    
    # =====================================================
    # UPDATE METRICS
    # =====================================================
    
    def update_tribe(
        self,
        tribe_id: int,
        population: int,
        territory_size: int,
        symbol_count: int,
    ) -> ScalingMetrics:
        """
        Update scaling metrics for a tribe.
        
        Args:
            tribe_id: Tribe ID
            population: Number of agents
            territory_size: Number of controlled cells
            symbol_count: Number of cultural symbols
            
        Returns:
            Updated metrics
        """
        if tribe_id not in self.metrics:
            self.metrics[tribe_id] = ScalingMetrics(tribe_id=tribe_id)
        
        metrics = self.metrics[tribe_id]
        metrics.population = population
        metrics.territory_size = territory_size
        metrics.symbol_count = symbol_count
        
        # Calculate loads
        metrics.administrative_load = self.calculate_administrative_load(
            population, territory_size
        )
        metrics.coordination_cost = self.calculate_coordination_cost(
            population, territory_size, symbol_count
        )
        
        # Calculate efficiency and risk
        metrics.efficiency = self.calculate_efficiency(
            metrics.administrative_load,
            metrics.coordination_cost,
        )
        metrics.failure_risk = self.calculate_failure_risk(
            population,
            metrics.efficiency,
            metrics.administrative_load,
        )
        
        # Check critical size
        metrics.critical_size = population > self.CRITICAL_SIZE
        
        return metrics
    
    # =====================================================
    # APPLY PENALTIES
    # =====================================================
    
    def apply_scaling_penalty(
        self,
        tribe_id: int,
        step: int,
    ) -> Optional[FailureEvent]:
        """
        Apply scaling penalties to a tribe.
        
        Args:
            tribe_id: Tribe to penalize
            step: Current step
            
        Returns:
            FailureEvent if failure occurred
        """
        if tribe_id not in self.metrics:
            return None
        
        metrics = self.metrics[tribe_id]
        
        # Check for failure
        if random.random() < metrics.failure_risk * 0.1:
            return self._trigger_failure(tribe_id, step, metrics)
        
        # Apply efficiency penalty to agents
        # This is done by the caller (reducing energy gain, etc.)
        
        return None
    
    def _trigger_failure(
        self,
        tribe_id: int,
        step: int,
        metrics: ScalingMetrics,
    ) -> FailureEvent:
        """Trigger a scaling failure."""
        # Determine failure type
        failure_types = []
        
        if self.enable_coordination and metrics.coordination_cost > 0.5:
            failure_types.append(FailureType.COORDINATION_FAILURE)
        
        if self.enable_admin and metrics.administrative_load > 1.0:
            failure_types.append(FailureType.ADMINISTRATIVE_COLLAPSE)
        
        if self.enable_overload and metrics.symbol_count > 100:
            failure_types.append(FailureType.SYMBOL_OVERLOAD)
        
        if metrics.territory_size > 50:
            failure_types.append(FailureType.TERRITORY_STRAIN)
        
        if metrics.population > 40:
            failure_types.append(FailureType.COMMUNICATION_BREAKDOWN)
        
        if not failure_types:
            failure_types = [FailureType.COORDINATION_FAILURE]
        
        failure_type = random.choice(failure_types)
        
        # Calculate severity
        severity = metrics.failure_risk
        
        # Determine impact
        impacts = {
            FailureType.COORDINATION_FAILURE: "Reduced coordination efficiency",
            FailureType.ADMINISTRATIVE_COLLAPSE: "Administrative breakdown",
            FailureType.SYMBOL_OVERLOAD: "Cultural confusion",
            FailureType.TERRITORY_STRAIN: "Territory management failure",
            FailureType.COMMUNICATION_BREAKDOWN: "Communication delays",
        }
        
        # Calculate affected agents
        affected = int(metrics.population * severity * 0.3)
        
        event = FailureEvent(
            step=step,
            tribe_id=tribe_id,
            failure_type=failure_type,
            severity=severity,
            impact=impacts[failure_type],
            affected_agents=affected,
        )
        
        self.failures.append(event)
        self.total_failures += 1
        
        if severity > 0.8:
            self.total_collapses += 1
        
        return event
    
    # =====================================================
    # GET PENALTIES
    # =====================================================
    
    def get_efficiency_penalty(self, tribe_id: int) -> float:
        """Get efficiency penalty for a tribe (0.0 - 1.0)."""
        if tribe_id not in self.metrics:
            return 0.0
        
        metrics = self.metrics[tribe_id]
        return 1.0 - metrics.efficiency
    
    def get_energy_penalty(self, tribe_id: int) -> float:
        """Get energy gain penalty for a tribe."""
        if tribe_id not in self.metrics:
            return 0.0
        
        metrics = self.metrics[tribe_id]
        
        # Larger tribes need more energy but are less efficient
        penalty = metrics.administrative_load * 0.1
        
        return penalty
    
    def get_reproduction_penalty(self, tribe_id: int) -> float:
        """Get reproduction penalty for a tribe."""
        if tribe_id not in self.metrics:
            return 0.0
        
        metrics = self.metrics[tribe_id]
        
        # Larger populations reproduce less efficiently
        if metrics.population > self.OPTIMAL_SIZE:
            return (metrics.population - self.OPTIMAL_SIZE) * 0.01
        
        return 0.0
    
    def should_split(self, tribe_id: int) -> bool:
        """Check if tribe should split due to size."""
        if tribe_id not in self.metrics:
            return False
        
        metrics = self.metrics[tribe_id]
        
        # High failure risk suggests split needed
        return metrics.failure_risk > 0.7 and metrics.population > self.CRITICAL_SIZE
    
    # =====================================================
    # STATUS
    # =====================================================
    
    def get_metrics(self, tribe_id: int) -> Optional[ScalingMetrics]:
        """Get scaling metrics for a tribe."""
        return self.metrics.get(tribe_id)
    
    def status(self) -> dict:
        """Get overall status."""
        critical_tribes = [
            tid for tid, m in self.metrics.items()
            if m.critical_size
        ]
        
        return {
            'total_failures': self.total_failures,
            'total_collapses': self.total_collapses,
            'critical_size_tribes': len(critical_tribes),
            'avg_efficiency': sum(m.efficiency for m in self.metrics.values()) / max(1, len(self.metrics)),
            'avg_failure_risk': sum(m.failure_risk for m in self.metrics.values()) / max(1, len(self.metrics)),
        }
    
    def summary(self) -> str:
        """Get human-readable summary."""
        s = self.status()
        return (
            f"📊 Scaling Penalties\n"
            f"   Total Failures: {s['total_failures']}\n"
            f"   Total Collapses: {s['total_collapses']}\n"
            f"   Critical Tribes: {s['critical_size_tribes']}\n"
            f"   Avg Efficiency: {s['avg_efficiency']:.1%}\n"
            f"   Avg Failure Risk: {s['avg_failure_risk']:.1%}\n"
        )
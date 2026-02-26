"""
Cultural Schism System - Ideological Splits

Enables:
- Internal faction conflict
- Ideological divides
- Subculture formation
- Religious reformation
- Cultural fork events
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random


class SchismType(Enum):
    IDEOLOGICAL = "ideological"
    SYMBOLIC = "symbolic"
    TERRITORIAL = "territorial"
    GENERATIONAL = "generational"
    LEADERSHIP = "leadership"


@dataclass
class Faction:
    """A faction within a tribe."""
    faction_id: int
    parent_tribe: int
    name: str
    ideology: str
    symbol_focus: Set[str] = field(default_factory=set)
    member_count: int = 0
    influence: float = 0.0
    conflict_level: float = 0.0


@dataclass
class SchismEvent:
    """Record of a schism event."""
    step: int
    parent_tribe: int
    schism_type: SchismType
    new_tribe: int
    reason: str
    symbols_split: int
    members_split: int


class SchismSystem:
    """
    Manages internal faction dynamics and cultural splits.
    
    Enables:
    - Faction formation
    - Ideological conflict
    - Cultural splits
    - Reformation events
    """
    
    def __init__(
        self,
        schism_threshold: float = 0.7,
        conflict_threshold: float = 0.5,
        min_faction_size: int = 3,
    ):
        self.schism_threshold = schism_threshold
        self.conflict_threshold = conflict_threshold
        self.min_faction_size = min_faction_size
        
        # Factions within tribes
        self.tribe_factions: Dict[int, List[Faction]] = {}
        
        # Symbol conflicts
        self.symbol_conflicts: Dict[int, Dict[str, float]] = {}
        
        # Schism history
        self.schisms: List[SchismEvent] = []
        
        # Statistics
        self.total_schisms = 0
        self.total_factions = 0
    
    # =====================================================
    # FACTION MANAGEMENT
    # =====================================================
    
    def create_faction(
        self,
        tribe_id: int,
        ideology: str,
        symbol_focus: Set[str] = None,
    ) -> Faction:
        """Create a new faction within a tribe."""
        if tribe_id not in self.tribe_factions:
            self.tribe_factions[tribe_id] = []
        
        faction_id = len(self.tribe_factions[tribe_id])
        
        faction = Faction(
            faction_id=faction_id,
            parent_tribe=tribe_id,
            name=f"Faction-{tribe_id}-{faction_id}",
            ideology=ideology,
            symbol_focus=symbol_focus or set(),
            member_count=0,
            influence=0.0,
            conflict_level=0.0,
        )
        
        self.tribe_factions[tribe_id].append(faction)
        self.total_factions += 1
        
        return faction
    
    def update_faction(
        self,
        tribe_id: int,
        faction_id: int,
        member_count: int = None,
        influence: float = None,
        conflict: float = None,
    ):
        """Update faction metrics."""
        if tribe_id not in self.tribe_factions:
            return
        
        factions = self.tribe_factions[tribe_id]
        if faction_id >= len(factions):
            return
        
        faction = factions[faction_id]
        
        if member_count is not None:
            faction.member_count = member_count
        if influence is not None:
            faction.influence = influence
        if conflict is not None:
            faction.conflict_level = conflict
    
    def get_factions(self, tribe_id: int) -> List[Faction]:
        """Get all factions in a tribe."""
        return self.tribe_factions.get(tribe_id, [])
    
    # =====================================================
    # CONFLICT DETECTION
    # =====================================================
    
    def detect_symbol_conflict(
        self,
        tribe_id: int,
        symbols: Dict[str, float],
    ) -> float:
        """
        Detect internal symbol conflicts.
        
        High variance in symbol values = conflict potential.
        
        Args:
            tribe_id: Tribe ID
            symbols: Dict of symbol -> value
            
        Returns:
            Conflict level (0.0 - 1.0)
        """
        if not symbols:
            return 0.0
        
        values = list(symbols.values())
        
        # Calculate variance
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        
        # Normalize to 0-1
        conflict = min(1.0, variance / 2.0)
        
        # Store conflict
        if tribe_id not in self.symbol_conflicts:
            self.symbol_conflicts[tribe_id] = {}
        
        for symbol, value in symbols.items():
            old = self.symbol_conflicts[tribe_id].get(symbol, value)
            # Update with decay
            self.symbol_conflicts[tribe_id][symbol] = old * 0.9 + value * 0.1
        
        return conflict
    
    def calculate_schism_risk(
        self,
        tribe_id: int,
        population: int,
        symbol_conflict: float,
        territory_size: int,
    ) -> float:
        """
        Calculate risk of schism.
        
        Args:
            tribe_id: Tribe ID
            population: Number of agents
            symbol_conflict: Internal symbol conflict level
            territory_size: Size of territory
            
        Returns:
            Schism risk (0.0 - 1.0)
        """
        risk = 0.0
        
        # Symbol conflict contributes
        risk += symbol_conflict * 0.4
        
        # Large population increases schism risk
        if population > 20:
            risk += (population - 20) * 0.01
        
        # Large territory increases schism risk
        if territory_size > 30:
            risk += (territory_size - 30) * 0.005
        
        # Multiple factions increase risk
        factions = self.tribe_factions.get(tribe_id, [])
        if len(factions) > 1:
            # Check for opposing ideologies
            max_conflict = max(f.conflict_level for f in factions)
            risk += max_conflict * 0.3
        
        return min(1.0, risk)
    
    # =====================================================
    # SCHISM TRIGGERING
    # =====================================================
    
    def check_schism(
        self,
        step: int,
        tribe_id: int,
        population: int,
        symbols: Dict[str, float],
        territory_size: int,
    ) -> Optional[SchismEvent]:
        """
        Check if a schism should occur.
        
        Args:
            step: Current step
            tribe_id: Tribe to check
            population: Population
            symbols: Symbol values
            territory_size: Territory size
            
        Returns:
            SchismEvent if schism occurred
        """
        # Detect symbol conflict
        symbol_conflict = self.detect_symbol_conflict(tribe_id, symbols)
        
        # Calculate schism risk
        risk = self.calculate_schism_risk(
            tribe_id, population, symbol_conflict, territory_size
        )
        
        # Check threshold
        if risk < self.schism_threshold:
            return None
        
        # Population must be large enough
        if population < self.min_faction_size * 2:
            return None
        
        # Determine schism type
        schism_type = self._determine_schism_type(
            symbol_conflict, population, territory_size
        )
        
        # Calculate split
        members_split = population // 2
        symbols_split = len(symbols) // 2
        
        # Create schism event
        event = SchismEvent(
            step=step,
            parent_tribe=tribe_id,
            schism_type=schism_type,
            new_tribe=-1,  # Will be assigned by caller
            reason=self._get_schism_reason(schism_type),
            symbols_split=symbols_split,
            members_split=members_split,
        )
        
        self.schisms.append(event)
        self.total_schisms += 1
        
        # Clean up old factions
        if tribe_id in self.tribe_factions:
            del self.tribe_factions[tribe_id]
        
        return event
    
    def _determine_schism_type(
        self,
        symbol_conflict: float,
        population: int,
        territory_size: int,
    ) -> SchismType:
        """Determine the type of schism."""
        types = []
        weights = []
        
        # Symbol conflict leads to ideological schism
        if symbol_conflict > 0.5:
            types.append(SchismType.IDEOLOGICAL)
            weights.append(symbol_conflict)
            types.append(SchismType.SYMBOLIC)
            weights.append(symbol_conflict * 0.5)
        
        # Large territory leads to territorial schism
        if territory_size > 30:
            types.append(SchismType.TERRITORIAL)
            weights.append(territory_size / 100)
        
        # Large population leads to generational schism
        if population > 30:
            types.append(SchismType.GENERATIONAL)
            weights.append(population / 100)
        
        if not types:
            types = [SchismType.IDEOLOGICAL]
            weights = [1.0]
        
        # Weighted random selection
        total = sum(weights)
        r = random.random() * total
        
        cumulative = 0
        for t, w in zip(types, weights):
            cumulative += w
            if r <= cumulative:
                return t
        
        return types[-1]
    
    def _get_schism_reason(self, schism_type: SchismType) -> str:
        """Get human-readable schism reason."""
        reasons = {
            SchismType.IDEOLOGICAL: "Ideological disagreement over symbols",
            SchismType.SYMBOLIC: "Conflict over symbol meanings",
            SchismType.TERRITORIAL: "Territorial dispute within tribe",
            SchismType.GENERATIONAL: "Generational divide in values",
            SchismType.LEADERSHIP: "Leadership succession crisis",
        }
        return reasons.get(schism_type, "Unknown reason")
    
    # =====================================================
    # REFORMATION
    # =====================================================
    
    def check_reformation(
        self,
        tribe_id: int,
        population: int,
        dominant_symbols: Set[str],
    ) -> Optional[str]:
        """
        Check if a reformation event should occur.
        
        Reformation = internal change without split.
        
        Returns:
            Reformation description if occurred
        """
        factions = self.tribe_factions.get(tribe_id, [])
        
        if len(factions) < 2:
            return None
        
        # Find dominant faction
        dominant = max(factions, key=lambda f: f.influence)
        
        if dominant.influence > 0.6 and random.random() < 0.1:
            # Reformation occurs
            return f"Reformation: {dominant.ideology} becomes dominant ideology"
        
        return None
    
    # =====================================================
    # STATUS
    # =====================================================
    
    def get_tribe_stability(self, tribe_id: int) -> float:
        """Get stability score for a tribe (0-1, higher = more stable)."""
        factions = self.tribe_factions.get(tribe_id, [])
        
        if not factions:
            return 1.0
        
        # More factions = less stable
        stability = 1.0 - (len(factions) * 0.1)
        
        # High conflict = less stable
        max_conflict = max(f.conflict_level for f in factions)
        stability -= max_conflict * 0.5
        
        return max(0.0, min(1.0, stability))
    
    def status(self) -> dict:
        """Get overall status."""
        return {
            'total_schisms': self.total_schisms,
            'total_factions': self.total_factions,
            'active_factions': sum(len(f) for f in self.tribe_factions.values()),
            'tribes_with_factions': len(self.tribe_factions),
        }
    
    def summary(self) -> str:
        """Get human-readable summary."""
        s = self.status()
        return (
            f"⚔️ Schism System\n"
            f"   Total Schisms: {s['total_schisms']}\n"
            f"   Active Factions: {s['active_factions']}\n"
            f"   Tribes with Factions: {s['tribes_with_factions']}\n"
        )
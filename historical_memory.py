"""
Historical Memory System - Civilizational Narrative

Enables:
- Written history of events
- Golden age / dark age markers
- Myth formation from significant events
- Cultural memory across generations
- Historical reinterpretation
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import random


class EraType(Enum):
    GOLDEN_AGE = "golden_age"
    SILVER_AGE = "silver_age"
    BRONZE_AGE = "bronze_age"
    DARK_AGE = "dark_age"
    COLLAPSE = "collapse"
    RENAISSANCE = "renaissance"


class EventType(Enum):
    FOUNDING = "founding"
    WAR_VICTORY = "war_victory"
    WAR_DEFEAT = "war_defeat"
    EXPANSION = "expansion"
    COLLAPSE = "collapse"
    ALLIANCE = "alliance"
    BETRAYAL = "betrayal"
    DISCOVERY = "discovery"
    INNOVATION = "innovation"
    CULTURAL_PEAK = "cultural_peak"
    EXTINCTION = "extinction"
    RENAISSANCE = "renaissance"


@dataclass
class HistoricalEvent:
    """A significant event in history."""
    step: int
    event_type: EventType
    tribe_id: int
    description: str
    significance: float  # 0.0 - 1.0
    location: Optional[Tuple[int, int]] = None
    participants: List[int] = field(default_factory=list)
    symbols_involved: List[str] = field(default_factory=list)


@dataclass
class Myth:
    """A myth formed from historical events."""
    name: str
    origin_event: HistoricalEvent
    tribe_id: int
    power: float  # Cultural power
    age: int  # How old in steps
    retellings: int  # How many times referenced
    meaning: str  # Cultural meaning


@dataclass
class Era:
    """A historical era for a tribe."""
    start_step: int
    end_step: Optional[int]
    era_type: EraType
    peak_population: int
    peak_symbols: int
    peak_territory: int
    major_events: List[HistoricalEvent] = field(default_factory=list)


class HistoricalMemory:
    """
    Manages historical memory for civilizations.
    
    Features:
    - Event logging and significance
    - Era detection (golden age, dark age, etc.)
    - Myth formation
    - Cultural memory
    - Historical reinterpretation
    """
    
    def __init__(
        self,
        max_events: int = 1000,
        myth_threshold: float = 0.7,
        era_check_interval: int = 100,
    ):
        self.max_events = max_events
        self.myth_threshold = myth_threshold
        self.era_check_interval = era_check_interval
        
        # Event storage
        self.events: List[HistoricalEvent] = []
        self.tribe_events: Dict[int, List[HistoricalEvent]] = defaultdict(list)
        
        # Eras
        self.tribe_eras: Dict[int, List[Era]] = defaultdict(list)
        self.current_era: Dict[int, Era] = {}
        
        # Myths
        self.myths: List[Myth] = []
        self.tribe_myths: Dict[int, List[Myth]] = defaultdict(list)
        
        # Civilizational memory
        self.civilization_memory: Dict[int, Dict] = defaultdict(dict)
        
        # Statistics
        self.total_events = 0
        self.total_myths = 0
    
    # =====================================================
    # EVENT RECORDING
    # =====================================================
    
    def record_event(
        self,
        step: int,
        event_type: EventType,
        tribe_id: int,
        description: str,
        significance: float = 0.5,
        location: Tuple[int, int] = None,
        participants: List[int] = None,
        symbols_involved: List[str] = None,
    ) -> HistoricalEvent:
        """
        Record a historical event.
        
        Args:
            step: Current simulation step
            event_type: Type of event
            tribe_id: Primary tribe
            description: Human-readable description
            significance: How significant (0-1)
            location: Where it happened
            participants: Other tribes involved
            symbols_involved: Cultural symbols referenced
            
        Returns:
            The recorded event
        """
        event = HistoricalEvent(
            step=step,
            event_type=event_type,
            tribe_id=tribe_id,
            description=description,
            significance=min(1.0, max(0.0, significance)),
            location=location,
            participants=participants or [],
            symbols_involved=symbols_involved or [],
        )
        
        self.events.append(event)
        self.tribe_events[tribe_id].append(event)
        self.total_events += 1
        
        # Add to current era
        if tribe_id in self.current_era:
            self.current_era[tribe_id].major_events.append(event)
        
        # Check for myth formation
        if event.significance >= self.myth_threshold:
            self._try_form_myth(event)
        
        # Trim old events
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        return event
    
    def record_founding(self, step: int, tribe_id: int, location: Tuple[int, int]):
        """Record tribe founding."""
        self.record_event(
            step=step,
            event_type=EventType.FOUNDING,
            tribe_id=tribe_id,
            description=f"Tribe {tribe_id} founded at {location}",
            significance=1.0,
            location=location,
        )
        
        # Start first era
        self.current_era[tribe_id] = Era(
            start_step=step,
            end_step=None,
            era_type=EraType.BRONZE_AGE,
            peak_population=1,
            peak_symbols=0,
            peak_territory=1,
        )
    
    def record_war(
        self,
        step: int,
        attacker: int,
        defender: int,
        winner: int,
        casualties: Dict[int, int],
    ):
        """Record a war event."""
        loser = defender if winner == attacker else attacker
        
        # Winner event
        self.record_event(
            step=step,
            event_type=EventType.WAR_VICTORY,
            tribe_id=winner,
            description=f"Tribe {winner} defeated tribe {loser} in war",
            significance=0.8,
            participants=[loser],
        )
        
        # Loser event
        self.record_event(
            step=step,
            event_type=EventType.WAR_DEFEAT,
            tribe_id=loser,
            description=f"Tribe {loser} lost war to tribe {winner}",
            significance=0.7,
            participants=[winner],
        )
    
    def record_expansion(self, step: int, tribe_id: int, cells_gained: int):
        """Record territory expansion."""
        significance = min(1.0, 0.3 + cells_gained * 0.1)
        self.record_event(
            step=step,
            event_type=EventType.EXPANSION,
            tribe_id=tribe_id,
            description=f"Tribe {tribe_id} expanded by {cells_gained} cells",
            significance=significance,
        )
    
    def record_collapse(self, step: int, tribe_id: int, reason: str):
        """Record civilization collapse."""
        self.record_event(
            step=step,
            event_type=EventType.COLLAPSE,
            tribe_id=tribe_id,
            description=f"Tribe {tribe_id} collapsed: {reason}",
            significance=1.0,
        )
        
        # End current era
        if tribe_id in self.current_era:
            self.current_era[tribe_id].end_step = step
            self.tribe_eras[tribe_id].append(self.current_era[tribe_id])
            del self.current_era[tribe_id]
    
    def record_extinction(self, step: int, tribe_id: int):
        """Record tribe extinction."""
        self.record_event(
            step=step,
            event_type=EventType.EXTINCTION,
            tribe_id=tribe_id,
            description=f"Tribe {tribe_id} went extinct",
            significance=1.0,
        )
    
    def record_innovation(self, step: int, tribe_id: int, innovation: str):
        """Record an innovation/discovery."""
        self.record_event(
            step=step,
            event_type=EventType.INNOVATION,
            tribe_id=tribe_id,
            description=f"Tribe {tribe_id} discovered: {innovation}",
            significance=0.6,
        )
    
    def record_alliance(self, step: int, tribe_a: int, tribe_b: int):
        """Record alliance formation."""
        self.record_event(
            step=step,
            event_type=EventType.ALLIANCE,
            tribe_id=tribe_a,
            description=f"Tribe {tribe_a} allied with tribe {tribe_b}",
            significance=0.5,
            participants=[tribe_b],
        )
    
    # =====================================================
    # ERA DETECTION
    # =====================================================
    
    def update_era(
        self,
        step: int,
        tribe_id: int,
        population: int,
        symbols: int,
        territory: int,
    ):
        """
        Update era status for a tribe.
        
        Call this periodically to detect era changes.
        """
        if tribe_id not in self.current_era:
            return
        
        era = self.current_era[tribe_id]
        
        # Update peaks
        era.peak_population = max(era.peak_population, population)
        era.peak_symbols = max(era.peak_symbols, symbols)
        era.peak_territory = max(era.peak_territory, territory)
        
        # Check for era transition
        if step % self.era_check_interval != 0:
            return
        
        # Calculate current status
        current_power = population + symbols + territory
        peak_power = era.peak_population + era.peak_symbols + era.peak_territory
        
        if peak_power == 0:
            return
        
        power_ratio = current_power / peak_power
        
        # Determine era type
        new_era_type = self._classify_era(power_ratio, population, era.era_type)
        
        if new_era_type != era.era_type:
            # End current era
            era.end_step = step
            self.tribe_eras[tribe_id].append(era)
            
            # Start new era
            self.current_era[tribe_id] = Era(
                start_step=step,
                end_step=None,
                era_type=new_era_type,
                peak_population=population,
                peak_symbols=symbols,
                peak_territory=territory,
            )
            
            # Record era change
            if new_era_type == EraType.GOLDEN_AGE:
                self.record_event(
                    step=step,
                    event_type=EventType.CULTURAL_PEAK,
                    tribe_id=tribe_id,
                    description=f"Tribe {tribe_id} entered a Golden Age",
                    significance=0.9,
                )
            elif new_era_type == EraType.DARK_AGE:
                self.record_event(
                    step=step,
                    event_type=EventType.COLLAPSE,
                    tribe_id=tribe_id,
                    description=f"Tribe {tribe_id} entered a Dark Age",
                    significance=0.7,
                )
            elif new_era_type == EraType.RENAISSANCE:
                self.record_event(
                    step=step,
                    event_type=EventType.RENAISSANCE,
                    tribe_id=tribe_id,
                    description=f"Tribe {tribe_id} experienced a Renaissance",
                    significance=0.8,
                )
    
    def _classify_era(
        self,
        power_ratio: float,
        population: int,
        current_era: EraType,
    ) -> EraType:
        """Classify current era based on power metrics."""
        if power_ratio >= 0.9:
            return EraType.GOLDEN_AGE
        elif power_ratio >= 0.7:
            return EraType.SILVER_AGE
        elif power_ratio >= 0.5:
            return EraType.BRONZE_AGE
        elif power_ratio >= 0.3:
            if current_era == EraType.DARK_AGE:
                return EraType.RENAISSANCE
            return EraType.DARK_AGE
        else:
            return EraType.COLLAPSE
    
    # =====================================================
    # MYTH FORMATION
    # =====================================================
    
    def _try_form_myth(self, event: HistoricalEvent):
        """Try to form a myth from a significant event."""
        if event.significance < self.myth_threshold:
            return
        
        # Generate myth name
        myth_names = [
            f"The {event.event_type.value.replace('_', ' ').title()} of Tribe {event.tribe_id}",
            f"The Legend of Step {event.step}",
            f"The Great {event.event_type.value.replace('_', ' ').title()}",
        ]
        
        myth = Myth(
            name=random.choice(myth_names),
            origin_event=event,
            tribe_id=event.tribe_id,
            power=event.significance,
            age=0,
            retellings=1,
            meaning=event.description,
        )
        
        self.myths.append(myth)
        self.tribe_myths[event.tribe_id].append(myth)
        self.total_myths += 1
    
    def get_myths(self, tribe_id: int) -> List[Myth]:
        """Get myths for a tribe."""
        return self.tribe_myths.get(tribe_id, [])
    
    def get_myth_power(self, tribe_id: int) -> float:
        """Get total cultural power from myths."""
        myths = self.tribe_myths.get(tribe_id, [])
        if not myths:
            return 0.0
        return sum(m.power for m in myths) / len(myths)
    
    # =====================================================
    # CIVILIZATIONAL MEMORY
    # =====================================================
    
    def get_golden_ages(self, tribe_id: int) -> List[Era]:
        """Get golden ages for a tribe."""
        return [e for e in self.tribe_eras.get(tribe_id, []) 
                if e.era_type == EraType.GOLDEN_AGE]
    
    def get_dark_ages(self, tribe_id: int) -> List[Era]:
        """Get dark ages for a tribe."""
        return [e for e in self.tribe_eras.get(tribe_id, []) 
                if e.era_type == EraType.DARK_AGE]
    
    def get_history_summary(self, tribe_id: int) -> dict:
        """Get a summary of a tribe's history."""
        events = self.tribe_events.get(tribe_id, [])
        eras = self.tribe_eras.get(tribe_id, [])
        myths = self.tribe_myths.get(tribe_id, [])
        
        return {
            'total_events': len(events),
            'wars_won': len([e for e in events if e.event_type == EventType.WAR_VICTORY]),
            'wars_lost': len([e for e in events if e.event_type == EventType.WAR_DEFEAT]),
            'golden_ages': len(self.get_golden_ages(tribe_id)),
            'dark_ages': len(self.get_dark_ages(tribe_id)),
            'myths': len(myths),
            'myth_power': self.get_myth_power(tribe_id),
            'total_eras': len(eras),
            'current_era': self.current_era.get(tribe_id, Era(0, None, EraType.BRONZE_AGE, 0, 0, 0)).era_type.value if tribe_id in self.current_era else "extinct",
        }
    
    # =====================================================
    # HISTORICAL REINTERPRETATION
    # =====================================================
    
    def reinterpret_history(self, tribe_id: int, step: int):
        """
        Reinterpret history based on current status.
        
        This allows tribes to reframe past events.
        """
        events = self.tribe_events.get(tribe_id, [])
        if not events:
            return
        
        current_era = self.current_era.get(tribe_id)
        if not current_era:
            return
        
        # Golden age tribes view past defeats as learning
        if current_era.era_type == EraType.GOLDEN_AGE:
            for event in events[-10:]:
                if event.event_type == EventType.WAR_DEFEAT:
                    event.description = f"[Reinterpreted] {event.description} (became stronger)"
        
        # Dark age tribes view past victories as hollow
        elif current_era.era_type == EraType.DARK_AGE:
            for event in events[-10:]:
                if event.event_type == EventType.WAR_VICTORY:
                    event.significance *= 0.8
    
    # =====================================================
    # STATUS
    # =====================================================
    
    def status(self) -> dict:
        """Get overall status."""
        return {
            'total_events': self.total_events,
            'total_myths': self.total_myths,
            'active_tribes': len(self.current_era),
            'total_eras': sum(len(eras) for eras in self.tribe_eras.values()),
        }
    
    def summary(self) -> str:
        """Get human-readable summary."""
        s = self.status()
        return (
            f"📜 Historical Memory\n"
            f"   Events: {s['total_events']}\n"
            f"   Myths: {s['total_myths']}\n"
            f"   Active Tribes: {s['active_tribes']}\n"
            f"   Total Eras: {s['total_eras']}\n"
        )
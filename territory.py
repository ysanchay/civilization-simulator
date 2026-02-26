"""
Territory System - Geographic Ownership and Control

Enables:
- Cell ownership by tribes
- Borders and boundaries
- Territory conquest after war
- Resource monopolization
- Spatial politics
"""

from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass, field
from enum import Enum


class TerritoryType(Enum):
    UNCLAIMED = 0
    CLAIMED = 1
    CONTROLLED = 2
    CONTESTED = 3
    CORE = 4  # Homeland


@dataclass
class TerritoryCell:
    """Represents ownership of a single cell."""
    x: int
    y: int
    owner_id: Optional[int] = None
    claim_strength: float = 0.0
    control_level: float = 0.0
    influence_sources: Dict[int, float] = field(default_factory=dict)
    last_contested: int = 0
    territory_type: TerritoryType = TerritoryType.UNCLAIMED


@dataclass
class TerritoryEvent:
    """Records a territory change event."""
    step: int
    event_type: str  # 'claim', 'conquer', 'lose', 'contest'
    tribe_id: int
    x: int
    y: int
    details: str = ""


class TerritorySystem:
    """
    Manages territorial ownership and control.
    
    Territory states:
    - UNCLAIMED: No tribe has claimed
    - CLAIMED: Tribe has staked claim but not full control
    - CONTROLLED: Tribe has full control
    - CONTESTED: Multiple tribes claim
    - CORE: Homeland, high value
    """
    
    def __init__(
        self,
        width: int,
        height: int,
        claim_decay: float = 0.01,
        control_threshold: float = 0.5,
        core_radius: int = 3,
    ):
        self.width = width
        self.height = height
        self.claim_decay = claim_decay
        self.control_threshold = control_threshold
        self.core_radius = core_radius
        
        # Territory grid
        self.grid: List[List[TerritoryCell]] = [
            [TerritoryCell(x=x, y=y) for x in range(width)]
            for y in range(height)
        ]
        
        # Tribe territories
        self.tribe_territory: Dict[int, Set[Tuple[int, int]]] = {}
        
        # Event history
        self.events: List[TerritoryEvent] = []
        
        # Statistics
        self.total_claims = 0
        self.total_conquests = 0
        self.total_losses = 0
    
    # =====================================================
    # CLAIMING TERRITORY
    # =====================================================
    
    def claim_cell(self, tribe_id: int, x: int, y: int, strength: float = 1.0) -> bool:
        """
        Claim a cell for a tribe.
        
        Args:
            tribe_id: Tribe claiming
            x, y: Cell coordinates
            strength: Claim strength (based on presence, power)
            
        Returns:
            True if claim succeeded
        """
        if not self._in_bounds(x, y):
            return False
        
        cell = self.grid[y][x]
        
        # Add influence
        if tribe_id not in cell.influence_sources:
            cell.influence_sources[tribe_id] = 0.0
        cell.influence_sources[tribe_id] += strength
        
        # Update claim
        old_owner = cell.owner_id
        
        # Determine new owner based on influence
        if cell.influence_sources:
            strongest = max(cell.influence_sources.items(), key=lambda x: x[1])
            new_owner = strongest[0]
            new_strength = strongest[1]
            
            if new_owner != old_owner:
                # Territory change
                cell.owner_id = new_owner
                cell.claim_strength = new_strength
                
                # Update tribe territory sets
                if old_owner is not None:
                    if old_owner in self.tribe_territory:
                        self.tribe_territory[old_owner].discard((x, y))
                
                if new_owner not in self.tribe_territory:
                    self.tribe_territory[new_owner] = set()
                self.tribe_territory[new_owner].add((x, y))
                
                # Record event
                if old_owner is None:
                    event_type = 'claim'
                    self.total_claims += 1
                else:
                    event_type = 'conquer'
                    self.total_conquests += 1
                
                self.events.append(TerritoryEvent(
                    step=0,  # Will be set by caller
                    event_type=event_type,
                    tribe_id=new_owner,
                    x=x, y=y,
                    details=f"From tribe {old_owner}" if old_owner else "Unclaimed"
                ))
                
                return True
        
        return False
    
    def lose_cell(self, tribe_id: int, x: int, y: int) -> bool:
        """Remove tribe's claim on a cell."""
        if not self._in_bounds(x, y):
            return False
        
        cell = self.grid[y][x]
        
        if tribe_id in cell.influence_sources:
            del cell.influence_sources[tribe_id]
        
        if cell.owner_id == tribe_id:
            cell.owner_id = None
            cell.claim_strength = 0.0
            cell.territory_type = TerritoryType.UNCLAIMED
            
            if tribe_id in self.tribe_territory:
                self.tribe_territory[tribe_id].discard((x, y))
            
            self.total_losses += 1
            self.events.append(TerritoryEvent(
                step=0,
                event_type='lose',
                tribe_id=tribe_id,
                x=x, y=y,
            ))
            return True
        
        return False
    
    # =====================================================
    # TERRITORY QUERIES
    # =====================================================
    
    def get_territory(self, tribe_id: int) -> Set[Tuple[int, int]]:
        """Get all cells owned by a tribe."""
        return self.tribe_territory.get(tribe_id, set()).copy()
    
    def get_territory_size(self, tribe_id: int) -> int:
        """Get the size of a tribe's territory."""
        return len(self.tribe_territory.get(tribe_id, set()))
    
    def get_owner(self, x: int, y: int) -> Optional[int]:
        """Get the owner of a cell."""
        if self._in_bounds(x, y):
            return self.grid[y][x].owner_id
        return None
    
    def get_border(self, tribe_id: int) -> List[Tuple[int, int]]:
        """Get border cells of a tribe's territory."""
        territory = self.tribe_territory.get(tribe_id, set())
        border = []
        
        for x, y in territory:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if not self._in_bounds(nx, ny):
                    border.append((x, y))
                    break
                if self.grid[ny][nx].owner_id != tribe_id:
                    border.append((x, y))
                    break
        
        return border
    
    def get_core_territory(self, tribe_id: int) -> List[Tuple[int, int]]:
        """Get core (homeland) territory."""
        territory = self.tribe_territory.get(tribe_id, set())
        core = []
        
        for x, y in territory:
            cell = self.grid[y][x]
            if cell.territory_type == TerritoryType.CORE:
                core.append((x, y))
        
        return core
    
    def get_contested_territory(self) -> List[Tuple[int, int, Dict[int, float]]]:
        """Get all contested cells with competing claims."""
        contested = []
        
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if len(cell.influence_sources) > 1:
                    contested.append((x, y, dict(cell.influence_sources)))
        
        return contested
    
    # =====================================================
    # TERRITORY EFFECTS
    # =====================================================
    
    def get_territory_bonus(self, tribe_id: int, x: int, y: int) -> float:
        """
        Get bonus/penalty for a tribe at a location.
        
        Returns:
            Positive = bonus in own territory
            Negative = penalty in enemy territory
        """
        if not self._in_bounds(x, y):
            return 0.0
        
        cell = self.grid[y][x]
        
        if cell.owner_id == tribe_id:
            # Bonus in own territory
            if cell.territory_type == TerritoryType.CORE:
                return 0.3  # Homeland bonus
            return 0.1  # Controlled territory bonus
        elif cell.owner_id is not None:
            # Penalty in enemy territory
            return -0.2
        
        return 0.0
    
    def get_danger_modifier(self, tribe_id: int, x: int, y: int) -> float:
        """Get danger modifier based on territory."""
        bonus = self.get_territory_bonus(tribe_id, x, y)
        return -bonus  # Bonus reduces danger, penalty increases
    
    def can_claim(self, tribe_id: int, x: int, y: int) -> bool:
        """Check if a tribe can claim a cell."""
        if not self._in_bounds(x, y):
            return False
        
        cell = self.grid[y][x]
        
        # Can always claim unclaimed
        if cell.owner_id is None:
            return True
        
        # Can contest if adjacent to own territory
        territory = self.tribe_territory.get(tribe_id, set())
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if (x + dx, y + dy) in territory:
                return True
        
        return False
    
    # =====================================================
    # UPDATE & MAINTENANCE
    # =====================================================
    
    def update(self, step: int):
        """Update territory state."""
        # Decay old claims
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                
                # Decay influence
                to_remove = []
                for tribe_id in cell.influence_sources:
                    cell.influence_sources[tribe_id] *= (1 - self.claim_decay)
                    if cell.influence_sources[tribe_id] < 0.1:
                        to_remove.append(tribe_id)
                
                for tribe_id in to_remove:
                    del cell.influence_sources[tribe_id]
                
                # Update territory type
                if cell.owner_id is not None:
                    cell.control_level = cell.influence_sources.get(cell.owner_id, 0)
                    
                    if len(cell.influence_sources) > 1:
                        cell.territory_type = TerritoryType.CONTESTED
                    elif cell.control_level > self.control_threshold:
                        cell.territory_type = TerritoryType.CONTROLLED
                    else:
                        cell.territory_type = TerritoryType.CLAIMED
        
        # Update core territory
        self._update_core_territory()
    
    def _update_core_territory(self):
        """Mark cells near tribe centers as core territory."""
        for tribe_id, territory in self.tribe_territory.items():
            if not territory:
                continue
            
            # Find center of mass
            xs = [x for x, y in territory]
            ys = [y for x, y in territory]
            cx = sum(xs) // len(xs)
            cy = sum(ys) // len(ys)
            
            # Mark core territory
            for x, y in territory:
                dist = abs(x - cx) + abs(y - cy)
                if dist <= self.core_radius:
                    self.grid[y][x].territory_type = TerritoryType.CORE
    
    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height
    
    # =====================================================
    # WAR CONQUEST
    # =====================================================
    
    def conquest(self, winner_id: int, loser_id: int, cells: int = 5) -> List[Tuple[int, int]]:
        """
        Transfer territory from loser to winner after war.
        
        Args:
            winner_id: Winning tribe
            loser_id: Losing tribe
            cells: Number of cells to transfer
            
        Returns:
            List of conquered cells
        """
        loser_territory = self.tribe_territory.get(loser_id, set())
        winner_territory = self.tribe_territory.get(winner_id, set())
        
        if not loser_territory:
            return []
        
        conquered = []
        
        # Find border cells of loser adjacent to winner
        border = self.get_border(loser_id)
        adjacent = []
        
        for x, y in border:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) in winner_territory:
                    adjacent.append((x, y))
                    break
        
        # Conquer cells
        for x, y in adjacent[:cells]:
            if self.lose_cell(loser_id, x, y):
                self.claim_cell(winner_id, x, y, strength=1.0)
                conquered.append((x, y))
        
        return conquered
    
    # =====================================================
    # STATUS
    # =====================================================
    
    def status(self) -> dict:
        """Get territory status."""
        total_claimed = sum(len(t) for t in self.tribe_territory.values())
        contested = len(self.get_contested_territory())
        
        return {
            'total_claimed': total_claimed,
            'contested_cells': contested,
            'total_claims': self.total_claims,
            'total_conquests': self.total_conquests,
            'total_losses': self.total_losses,
            'tribes_with_territory': len([t for t in self.tribe_territory.values() if t]),
        }
    
    def summary(self) -> str:
        """Get human-readable summary."""
        s = self.status()
        return (
            f"🌍 Territory Status\n"
            f"   Claimed: {s['total_claimed']} cells\n"
            f"   Contested: {s['contested_cells']} cells\n"
            f"   Claims: {s['total_claims']}\n"
            f"   Conquests: {s['total_conquests']}\n"
            f"   Tribes with land: {s['tribes_with_territory']}\n"
        )
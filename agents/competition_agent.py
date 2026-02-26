"""
CompetitionAgent

IDENTITY: "I am the pressure. I drive selection and evolution."

ROLE: Tribe competition, warfare, and alliances

RESPONSIBILITIES:
- Detect tribe conflicts and resource competition
- Handle warfare mechanics (attacks, defenses, outcomes)
- Manage alliance formation and dissolution
- Track dominance hierarchies
- Apply selection pressure (winners survive, losers decline)
- Handle tribe extinction and succession
"""

import random
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class RelationType(Enum):
    NEUTRAL = "neutral"
    ALLIED = "allied"
    HOSTILE = "hostile"
    VASSAL = "vassal"  # Subordinate tribe


@dataclass
class Conflict:
    """Represents a conflict between tribes."""
    attacker_id: int
    defender_id: int
    location: Tuple[int, int]
    attacker_strength: float
    defender_strength: float
    outcome: Optional[str] = None  # 'attacker_wins', 'defender_wins', 'draw'
    casualties: Dict[int, int] = field(default_factory=dict)


@dataclass
class Alliance:
    """Represents an alliance between tribes."""
    tribe_a: int
    tribe_b: int
    formed_step: int
    strength: float = 1.0
    mutual_defense: bool = True
    knowledge_sharing: bool = True


class CompetitionAgent:
    """
    Manages tribe competition, warfare, and alliances.
    
    Drives evolutionary pressure and selection.
    """
    
    def __init__(
        self,
        conflict_threshold: float = 0.3,
        alliance_threshold: float = 0.6,
        war_cost: float = 5.0,
        victory_reward: float = 10.0,
    ):
        self.conflict_threshold = conflict_threshold
        self.alliance_threshold = alliance_threshold
        self.war_cost = war_cost
        self.victory_reward = victory_reward
        
        # Relations
        self.relations: Dict[Tuple[int, int], RelationType] = {}
        self.alliances: Dict[Tuple[int, int], Alliance] = {}
        
        # Conflict history
        self.conflicts: List[Conflict] = []
        self.active_conflicts: List[Conflict] = []
        
        # Dominance tracking
        self.dominance_scores: Dict[int, float] = {}
        self.victory_counts: Dict[int, int] = {}
        self.defeat_counts: Dict[int, int] = {}
        
        # Statistics
        self.total_wars = 0
        self.total_alliances_formed = 0
        self.total_alliances_broken = 0
        self.extinctions_caused = 0
    
    # =====================================================
    # DOMINANCE CALCULATION
    # =====================================================
    
    def calculate_dominance(
        self,
        tribe_id: int,
        population: int,
        symbols: int,
        territory: int,
        victories: int,
    ) -> float:
        """
        Calculate dominance score for a tribe.
        
        Args:
            tribe_id: Tribe identifier
            population: Tribe population
            symbols: Number of cultural symbols
            territory: Controlled territory size
            victories: Number of victories
            
        Returns:
            Dominance score
        """
        # Factors
        pop_factor = population * 1.0
        culture_factor = symbols * 0.5
        territory_factor = territory * 0.3
        victory_factor = victories * 2.0
        
        score = pop_factor + culture_factor + territory_factor + victory_factor
        
        self.dominance_scores[tribe_id] = score
        return score
    
    def get_dominance_rank(self, tribe_id: int) -> int:
        """Get dominance rank of a tribe (1 = highest)."""
        sorted_tribes = sorted(
            self.dominance_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        for i, (tid, _) in enumerate(sorted_tribes):
            if tid == tribe_id:
                return i + 1
        return len(sorted_tribes) + 1
    
    # =====================================================
    # CONFLICT DETECTION
    # =====================================================
    
    def detect_conflict(
        self,
        tribe_a: int,
        tribe_b: int,
        positions_a: List[Tuple[int, int]],
        positions_b: List[Tuple[int, int]],
        resource_positions: List[Tuple[int, int]],
    ) -> float:
        """
        Detect conflict probability between two tribes.
        
        Args:
            tribe_a: First tribe ID
            tribe_b: Second tribe ID
            positions_a: Positions of tribe a agents
            positions_b: Positions of tribe b agents
            resource_positions: Positions of valuable resources
            
        Returns:
            Conflict probability (0.0 to 1.0)
        """
        # Check existing relation
        relation = self.relations.get((min(tribe_a, tribe_b), max(tribe_a, tribe_b)), RelationType.NEUTRAL)
        
        if relation == RelationType.ALLIED:
            return 0.0  # Allies don't conflict
        
        # Calculate proximity
        min_distance = float('inf')
        for pos_a in positions_a:
            for pos_b in positions_b:
                dist = abs(pos_a[0] - pos_b[0]) + abs(pos_a[1] - pos_b[1])
                min_distance = min(min_distance, dist)
        
        if min_distance > 10:  # Far apart
            return 0.0
        
        # Resource competition
        competition = 0.0
        for res_pos in resource_positions:
            a_near = any(abs(p[0] - res_pos[0]) + abs(p[1] - res_pos[1]) < 5 for p in positions_a)
            b_near = any(abs(p[0] - res_pos[0]) + abs(p[1] - res_pos[1]) < 5 for p in positions_b)
            if a_near and b_near:
                competition += 0.1
        
        # Dominance difference
        dom_a = self.dominance_scores.get(tribe_a, 0)
        dom_b = self.dominance_scores.get(tribe_b, 0)
        dominance_gap = abs(dom_a - dom_b) / max(dom_a, dom_b, 1)
        
        # Calculate conflict probability
        proximity_factor = max(0, 1 - min_distance / 10)
        conflict_prob = proximity_factor * (competition + 0.1 + dominance_gap * 0.2)
        
        # Hostile relation increases conflict
        if relation == RelationType.HOSTILE:
            conflict_prob *= 2.0
        
        return min(1.0, conflict_prob)
    
    # =====================================================
    # WARFARE
    # =====================================================
    
    def initiate_war(
        self,
        attacker_id: int,
        defender_id: int,
        attacker_strength: float,
        defender_strength: float,
        location: Tuple[int, int],
    ) -> Conflict:
        """
        Initiate a war between two tribes.
        
        Args:
            attacker_id: Attacking tribe ID
            defender_id: Defending tribe ID
            attacker_strength: Combined strength of attacker
            defender_strength: Combined strength of defender
            location: Conflict location
            
        Returns:
            Conflict object
        """
        conflict = Conflict(
            attacker_id=attacker_id,
            defender_id=defender_id,
            location=location,
            attacker_strength=attacker_strength,
            defender_strength=defender_strength,
        )
        
        self.active_conflicts.append(conflict)
        self.total_wars += 1
        
        # Set hostile relation
        key = (min(attacker_id, defender_id), max(attacker_id, defender_id))
        self.relations[key] = RelationType.HOSTILE
        
        print(f"⚔️ WAR: Tribe {attacker_id} attacks Tribe {defender_id} at {location}")
        
        return conflict
    
    def resolve_war(self, conflict: Conflict) -> str:
        """
        Resolve a war conflict.
        
        Args:
            conflict: The conflict to resolve
            
        Returns:
            Outcome string
        """
        # Calculate outcome
        total_strength = conflict.attacker_strength + conflict.defender_strength
        
        if total_strength == 0:
            conflict.outcome = 'draw'
            return conflict.outcome
        
        attacker_chance = conflict.attacker_strength / total_strength
        
        # Add randomness
        roll = random.random()
        
        if roll < attacker_chance * 0.8:  # Attacker wins
            conflict.outcome = 'attacker_wins'
            self.victory_counts[conflict.attacker_id] = self.victory_counts.get(conflict.attacker_id, 0) + 1
            self.defeat_counts[conflict.defender_id] = self.defeat_counts.get(conflict.defender_id, 0) + 1
            
            # Casualties
            conflict.casualties[conflict.attacker_id] = int(conflict.attacker_strength * 0.1)
            conflict.casualties[conflict.defender_id] = int(conflict.defender_strength * 0.3)
            
        elif roll > (1 - (1 - attacker_chance) * 0.8):  # Defender wins
            conflict.outcome = 'defender_wins'
            self.victory_counts[conflict.defender_id] = self.victory_counts.get(conflict.defender_id, 0) + 1
            self.defeat_counts[conflict.attacker_id] = self.defeat_counts.get(conflict.attacker_id, 0) + 1
            
            conflict.casualties[conflict.attacker_id] = int(conflict.attacker_strength * 0.3)
            conflict.casualties[conflict.defender_id] = int(conflict.defender_strength * 0.1)
            
        else:  # Draw
            conflict.outcome = 'draw'
            conflict.casualties[conflict.attacker_id] = int(conflict.attacker_strength * 0.2)
            conflict.casualties[conflict.defender_id] = int(conflict.defender_strength * 0.2)
        
        # Remove from active conflicts
        self.active_conflicts.remove(conflict)
        self.conflicts.append(conflict)
        
        print(f"⚔️ WAR RESULT: {conflict.outcome} | Casualties: {conflict.casualties}")
        
        return conflict.outcome
    
    # =====================================================
    # ALLIANCES
    # =====================================================
    
    def check_alliance_opportunity(
        self,
        tribe_a: int,
        tribe_b: int,
        common_enemies: Set[int],
        trade_benefit: float,
    ) -> float:
        """
        Check if two tribes should form an alliance.
        
        Args:
            tribe_a: First tribe ID
            tribe_b: Second tribe ID
            common_enemies: Set of common enemy tribe IDs
            trade_benefit: Potential trade/knowledge benefit
            
        Returns:
            Alliance probability
        """
        key = (min(tribe_a, tribe_b), max(tribe_a, tribe_b))
        
        # Already allied or hostile
        if key in self.alliances:
            return 0.0
        if self.relations.get(key) == RelationType.HOSTILE:
            return 0.0
        
        # Factors
        enemy_factor = len(common_enemies) * 0.2
        trade_factor = trade_benefit * 0.1
        
        # Dominance similarity
        dom_a = self.dominance_scores.get(tribe_a, 0)
        dom_b = self.dominance_scores.get(tribe_b, 0)
        similarity = 1 - abs(dom_a - dom_b) / max(dom_a, dom_b, 1)
        similarity_factor = similarity * 0.3
        
        alliance_prob = enemy_factor + trade_factor + similarity_factor
        
        return min(1.0, alliance_prob)
    
    def form_alliance(
        self,
        tribe_a: int,
        tribe_b: int,
        step: int,
        mutual_defense: bool = True,
        knowledge_sharing: bool = True,
    ) -> Optional[Alliance]:
        """
        Form an alliance between two tribes.
        
        Args:
            tribe_a: First tribe ID
            tribe_b: Second tribe ID
            step: Current simulation step
            mutual_defense: Whether alliance includes mutual defense
            knowledge_sharing: Whether alliance includes knowledge sharing
            
        Returns:
            Alliance object if successful
        """
        key = (min(tribe_a, tribe_b), max(tribe_a, tribe_b))
        
        if key in self.alliances:
            return None
        
        alliance = Alliance(
            tribe_a=tribe_a,
            tribe_b=tribe_b,
            formed_step=step,
            mutual_defense=mutual_defense,
            knowledge_sharing=knowledge_sharing,
        )
        
        self.alliances[key] = alliance
        self.relations[key] = RelationType.ALLIED
        self.total_alliances_formed += 1
        
        print(f"🤝 ALLIANCE: Tribe {tribe_a} and Tribe {tribe_b} formed alliance")
        
        return alliance
    
    def break_alliance(self, tribe_a: int, tribe_b: int, reason: str = "unknown") -> bool:
        """
        Break an alliance between two tribes.
        
        Args:
            tribe_a: First tribe ID
            tribe_b: Second tribe ID
            reason: Reason for breaking
            
        Returns:
            True if alliance was broken
        """
        key = (min(tribe_a, tribe_b), max(tribe_a, tribe_b))
        
        if key not in self.alliances:
            return False
        
        del self.alliances[key]
        self.relations[key] = RelationType.NEUTRAL
        self.total_alliances_broken += 1
        
        print(f"💔 ALLIANCE BROKEN: Tribe {tribe_a} and Tribe {tribe_b} ({reason})")
        
        return True
    
    def get_allies(self, tribe_id: int) -> List[int]:
        """Get list of allied tribes."""
        allies = []
        for (a, b), alliance in self.alliances.items():
            if a == tribe_id:
                allies.append(b)
            elif b == tribe_id:
                allies.append(a)
        return allies
    
    def get_enemies(self, tribe_id: int) -> List[int]:
        """Get list of enemy tribes."""
        enemies = []
        for (a, b), relation in self.relations.items():
            if relation == RelationType.HOSTILE:
                if a == tribe_id:
                    enemies.append(b)
                elif b == tribe_id:
                    enemies.append(a)
        return enemies
    
    # =====================================================
    # EXTINCTION AND SUCCESSION
    # =====================================================
    
    def handle_extinction(
        self,
        extinct_tribe: int,
        surviving_tribes: List[int],
    ) -> Optional[int]:
        """
        Handle tribe extinction - determine succession.
        
        Args:
            extinct_tribe: ID of extinct tribe
            surviving_tribes: List of surviving tribe IDs
            
        Returns:
            Successor tribe ID if any
        """
        # Check if extinct tribe was a vassal
        for key, relation in self.relations.items():
            if relation == RelationType.VASSAL:
                if extinct_tribe in key:
                    # Vassal extinct - nothing to inherit
                    return None
        
        # Find strongest ally or conqueror to inherit
        allies = self.get_allies(extinct_tribe)
        enemies = self.get_enemies(extinct_tribe)
        
        candidates = []
        
        # Allies get priority
        for ally in allies:
            dom = self.dominance_scores.get(ally, 0)
            candidates.append((ally, dom * 1.5))  # Bonus for alliance
        
        # Enemies can claim territory
        for enemy in enemies:
            dom = self.dominance_scores.get(enemy, 0)
            # Check if enemy won recent war against extinct tribe
            for conflict in self.conflicts[-10:]:  # Recent conflicts
                if conflict.outcome == 'attacker_wins':
                    if conflict.attacker_id == enemy and conflict.defender_id == extinct_tribe:
                        candidates.append((enemy, dom * 2.0))  # Big bonus for conquest
        
        # Clean up relations
        keys_to_remove = [k for k in self.relations if extinct_tribe in k]
        for key in keys_to_remove:
            del self.relations[key]
        
        keys_to_remove = [k for k in self.alliances if extinct_tribe in k]
        for key in keys_to_remove:
            del self.alliances[key]
        
        self.extinctions_caused += 1
        
        if candidates:
            successor = max(candidates, key=lambda x: x[1])[0]
            print(f"☠️ Tribe {extinct_tribe} extinct - Tribe {successor} inherits")
            return successor
        
        print(f"☠️ Tribe {extinct_tribe} extinct - no successor")
        return None
    
    # =====================================================
    # SELECTION PRESSURE
    # =====================================================
    
    def apply_selection_pressure(
        self,
        tribes: Dict[int, Dict],
    ) -> Dict[int, float]:
        """
        Apply selection pressure to all tribes.
        
        Args:
            tribes: Dict of tribe_id -> tribe_data
            
        Returns:
            Dict of tribe_id -> pressure_score
        """
        pressures = {}
        
        # Calculate base pressure from dominance hierarchy
        ranked = sorted(self.dominance_scores.items(), key=lambda x: x[1], reverse=True)
        
        for rank, (tribe_id, dominance) in enumerate(ranked):
            # Lower rank = more pressure
            rank_pressure = (len(ranked) - rank) / len(ranked) * 0.1
            
            # Pressure from enemies
            enemies = self.get_enemies(tribe_id)
            enemy_pressure = sum(self.dominance_scores.get(e, 0) for e in enemies) * 0.01
            
            # Relief from allies
            allies = self.get_allies(tribe_id)
            ally_relief = sum(self.dominance_scores.get(a, 0) for a in allies) * 0.005
            
            total_pressure = rank_pressure + enemy_pressure - ally_relief
            pressures[tribe_id] = max(0, total_pressure)
        
        return pressures
    
    # =====================================================
    # STATUS
    # =====================================================
    
    def status(self) -> Dict[str, any]:
        """Get competition status."""
        return {
            'total_wars': self.total_wars,
            'active_conflicts': len(self.active_conflicts),
            'total_alliances': self.total_alliances_formed,
            'active_alliances': len(self.alliances),
            'alliances_broken': self.total_alliances_broken,
            'extinctions': self.extinctions_caused,
            'dominance_ranking': sorted(self.dominance_scores.items(), key=lambda x: x[1], reverse=True)[:5],
        }
    
    def summary(self) -> str:
        """Get human-readable summary."""
        s = self.status()
        return (
            f"⚔️ Competition Status\n"
            f"   Wars: {s['total_wars']} ({s['active_conflicts']} active)\n"
            f"   Alliances: {s['active_alliances']} active\n"
            f"   Extinctions: {s['extinctions']}\n"
            f"   Top Tribes: {s['dominance_ranking'][:3]}\n"
        )
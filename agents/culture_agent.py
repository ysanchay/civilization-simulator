"""
CultureAgent

IDENTITY: "I am the collective. I hold language, traditions, and knowledge."

ROLE: Tribe-level culture and knowledge management

RESPONSIBILITIES:
- Manage tribe symbols and their meanings
- Handle language emergence (composed/meta symbols)
- Facilitate inter-tribe knowledge transfer
- Maintain cultural memory vault
- Track symbol roles (predictive, causal, goal)
- Cultural compression and forgetting
"""

import random
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Symbol:
    """Represents a cultural symbol with meaning and value."""
    pattern: Any
    value: float = 0.0
    count: int = 0
    role_predictive: float = 0.0
    role_causal: float = 0.0
    role_goal: float = 0.0
    created_step: int = 0
    tribe_id: int = 0


@dataclass
class CulturalMemory:
    """Snapshot of cultural knowledge for preservation."""
    symbols: Dict[Any, Symbol]
    transitions: Dict[Any, Dict[Any, int]]
    meta_symbols: Dict[frozenset, Symbol]
    roles: Dict[Any, Dict[str, float]]
    timestamp: int = 0


class CultureAgent:
    """
    Manages tribe culture, symbols, language, and knowledge transfer.
    
    Handles symbol grounding, composition, and cultural evolution.
    """
    
    def __init__(
        self,
        tribe_id: int,
        max_symbols: int = 300,
        memory_vault_capacity: int = 50,
        composition_threshold: int = 8,
        meta_threshold: int = 10,
    ):
        self.tribe_id = tribe_id
        self.max_symbols = max_symbols
        self.memory_vault_capacity = memory_vault_capacity
        self.composition_threshold = composition_threshold
        self.meta_threshold = meta_threshold
        
        # Home biome (tribes have preferences)
        self.home_biome = random.randint(0, 2)
        
        # Symbols and their values
        self.symbols: Dict[Any, Symbol] = {}
        self.symbol_usage: Dict[Any, int] = defaultdict(int)
        
        # Symbol roles
        self.symbol_roles: Dict[Any, Dict[str, float]] = defaultdict(
            lambda: {"predictive": 0.0, "causal": 0.0, "goal": 0.0}
        )
        
        # Language transitions (symbol → symbol probabilities)
        self.transitions: Dict[Any, Dict[Any, int]] = defaultdict(lambda: defaultdict(int))
        self.total_transitions: Dict[Any, int] = defaultdict(int)
        
        # Composed symbols (depth 2)
        self.composed_symbols: Dict[Tuple[Any, Any], Any] = {}
        
        # Meta symbols (depth 3)
        self.co_occurrence: Dict[frozenset, int] = defaultdict(int)
        self.meta_symbols: Dict[frozenset, Symbol] = {}
        
        # Cultural memory vault (for near-extinction recovery)
        self.memory_vault: CulturalMemory = None
        
        # Spatial memory
        self.food_memory: Dict[Tuple[int, int], float] = defaultdict(float)
        self.danger_memory: Dict[Tuple[int, int], float] = defaultdict(float)
        
        # Cultural bias (tribe personality)
        self.preference_bias = random.uniform(0.9, 1.1)
        
        # Knowledge transfer tracking
        self.adopted_symbols: Set[Any] = set()
        self.donated_symbols: Set[Any] = set()
    
    # =====================================================
    # SYMBOL GROUNDING
    # =====================================================
    
    def observe_pattern(
        self,
        pattern: Any,
        reward: float,
        population: int = 1,
        step: int = 0,
    ) -> Symbol:
        """
        Ground a symbol from observed pattern with reward.
        
        Args:
            pattern: Observed pattern tuple
            reward: Reward value associated with pattern
            population: Current population (affects cultural load)
            step: Current simulation step
            
        Returns:
            The symbol (existing or newly created)
        """
        if pattern not in self.symbols:
            if len(self.symbols) >= self.max_symbols:
                # Forget lowest value symbol
                self._forget_lowest()
            
            self.symbols[pattern] = Symbol(
                pattern=pattern,
                created_step=step,
                tribe_id=self.tribe_id,
            )
            print(f"🔤 Tribe {self.tribe_id} created symbol for {pattern}")
        
        # Apply cultural load
        load = self._cultural_load(population)
        noise = random.uniform(-0.03, 0.03) * load
        adjusted_reward = (reward + noise) * self.preference_bias
        
        self.symbols[pattern].reinforce(adjusted_reward)
        self.symbols[pattern].count += 1
        
        # Update role
        if reward > 0:
            self.symbol_roles[pattern]["causal"] += 0.1
        elif reward < 0:
            self.symbol_roles[pattern]["causal"] -= 0.05
        
        return self.symbols[pattern]
    
    def pattern_value(self, pattern: Any, population: int = 1) -> float:
        """Get the cultural value of a pattern."""
        if pattern not in self.symbols:
            return 0.0
        return self.symbols[pattern].value / self._cultural_load(population)
    
    def _cultural_load(self, population: int) -> float:
        """Calculate cultural memory pressure."""
        memory_cost = 0.01 * len(self.symbols)
        pop_cost = 0.02 * max(0, population - 25)
        return 1.0 + memory_cost + pop_cost
    
    def _forget_lowest(self):
        """Forget the lowest value symbol."""
        if not self.symbols:
            return
        
        # Don't forget protected symbols
        protected = set(self.meta_symbols.keys())
        for composed in self.composed_symbols.values():
            protected.add(composed)
        
        candidates = [(k, v.value) for k, v in self.symbols.items() if k not in protected]
        if candidates:
            lowest = min(candidates, key=lambda x: x[1])
            self._forget_symbol(lowest[0])
    
    def _forget_symbol(self, pattern: Any):
        """Remove a symbol and associated data."""
        self.symbols.pop(pattern, None)
        self.symbol_roles.pop(pattern, None)
        self.symbol_usage.pop(pattern, None)
        self.transitions.pop(pattern, None)
    
    # =====================================================
    # LANGUAGE LEARNING
    # =====================================================
    
    def record_transition(
        self,
        from_pattern: Any,
        to_pattern: Any,
        population: int = 1,
    ):
        """
        Record a transition between patterns (language learning).
        
        Args:
            from_pattern: Previous pattern
            to_pattern: Current pattern
            population: Current population
        """
        if from_pattern is None or to_pattern is None:
            return
        
        load = self._cultural_load(population)
        
        # Probabilistic recording based on cultural load
        if random.random() < (1.0 / load):
            self.transitions[from_pattern][to_pattern] += 1
            self.total_transitions[from_pattern] += 1
            
            # Update predictive role
            self.symbol_roles[from_pattern]["predictive"] += 0.05
            
            # Check for composition
            self._maybe_compose(from_pattern, to_pattern)
            
            # Track co-occurrence for meta symbols
            self._track_co_occurrence(from_pattern, to_pattern)
    
    def predict_next(self, pattern: Any) -> Optional[Any]:
        """
        Predict the next pattern given current pattern.
        
        Args:
            pattern: Current pattern
            
        Returns:
            Most likely next pattern or None
        """
        options = self.transitions.get(pattern)
        if not options:
            return None
        return max(options, key=options.get)
    
    def surprise(
        self,
        from_pattern: Any,
        to_pattern: Any,
        population: int = 1,
    ) -> float:
        """
        Calculate surprise of a transition.
        
        Higher surprise = less expected transition.
        """
        if from_pattern not in self.transitions:
            return 1.0
        
        total = self.total_transitions[from_pattern]
        count = self.transitions[from_pattern].get(to_pattern, 0)
        
        if count == 0:
            return 1.0
        
        # Surprise is inverse of probability
        probability = count / total
        return (1.0 - probability) * self._cultural_load(population)
    
    # =====================================================
    # SYMBOL COMPOSITION (Depth 2)
    # =====================================================
    
    def _maybe_compose(self, s1: Any, s2: Any):
        """
        Check if two symbols should be composed into a higher-level symbol.
        
        Composition happens when transition count exceeds threshold.
        """
        key = (s1, s2)
        if key in self.composed_symbols:
            return
        
        if self.transitions[s1][s2] >= self.composition_threshold:
            # Create composed symbol
            new_symbol = f"C{len(self.composed_symbols)}"
            self.composed_symbols[key] = new_symbol
            
            # Create symbol entry
            self.symbols[new_symbol] = Symbol(
                pattern=key,
                value=(self.symbols.get(s1, Symbol(s1)).value + 
                       self.symbols.get(s2, Symbol(s2)).value) / 2,
                created_step=0,
                tribe_id=self.tribe_id,
            )
            
            print(f"🧠 Tribe {self.tribe_id} LANGUAGE EMERGED: {s1} → {s2} = {new_symbol}")
    
    # =====================================================
    # META SYMBOLS (Depth 3)
    # =====================================================
    
    def _track_co_occurrence(self, s1: Any, s2: Any):
        """Track symbol co-occurrence for meta symbol formation."""
        if s1 == s2:
            return
        
        key = frozenset([s1, s2])
        self.co_occurrence[key] += 1
        
        # Form meta symbol when co-occurrence exceeds threshold
        if self.co_occurrence[key] >= self.meta_threshold:
            if key not in self.meta_symbols:
                self.meta_symbols[key] = Symbol(
                    pattern=key,
                    value=0.5,  # Starting value
                    created_step=0,
                    tribe_id=self.tribe_id,
                )
                print(f"🧠 Tribe {self.tribe_id} META-SYMBOL FORMED: {key}")
    
    # =====================================================
    # INTER-TRIBE KNOWLEDGE TRANSFER
    # =====================================================
    
    def adopt_symbol(self, symbol: Any, donor: 'CultureAgent') -> bool:
        """
        Adopt a symbol from another tribe.
        
        Args:
            symbol: Symbol pattern to adopt
            donor: Source culture
            
        Returns:
            True if adoption succeeded
        """
        if symbol in self.symbols:
            return False
        
        if symbol not in donor.symbols:
            return False
        
        donor_strength = donor.symbols[symbol].value
        local_symbol = self.symbols.get(symbol)
        
        # Adoption probability based on donor strength
        adopt_prob = min(0.9, max(0.1, donor_strength / 5.0))
        
        if local_symbol is None or donor_strength > local_symbol.value:
            if random.random() < adopt_prob:
                self.symbols[symbol] = donor.symbols[symbol]
                self.symbol_usage[symbol] = 1
                self.adopted_symbols.add(symbol)
                return True
        
        return False
    
    def get_donatable_symbols(self, min_value: float = 1.0) -> List[Any]:
        """Get symbols that can be donated to other tribes."""
        return [k for k, v in self.symbols.items() if v.value >= min_value]
    
    # =====================================================
    # CULTURAL MEMORY VAULT
    # =====================================================
    
    def snapshot_memory(self, step: int = 0):
        """
        Save current cultural knowledge to memory vault.
        
        Called when tribe is near extinction.
        """
        # Get top symbols by value
        ranked = sorted(
            self.symbols.items(),
            key=lambda x: x[1].value,
            reverse=True
        )[:self.memory_vault_capacity]
        
        compressed_symbols = {k: v for k, v in ranked}
        
        # Compress transitions to best only
        compressed_transitions = {}
        for s1, targets in self.transitions.items():
            if targets:
                best = max(targets.items(), key=lambda x: x[1])
                compressed_transitions[s1] = {best[0]: best[1]}
        
        self.memory_vault = CulturalMemory(
            symbols=compressed_symbols,
            transitions=compressed_transitions,
            meta_symbols=dict(self.meta_symbols),
            roles=dict(self.symbol_roles),
            timestamp=step,
        )
        
        print(f"🏛️ Tribe {self.tribe_id} saved memory vault ({len(compressed_symbols)} symbols)")
    
    def restore_memory(self):
        """
        Restore cultural knowledge from memory vault.
        
        Called when tribe recovers from near-extinction.
        """
        if self.memory_vault is None:
            return
        
        # Restore symbols
        for sym, obj in self.memory_vault.symbols.items():
            if sym not in self.symbols:
                self.symbols[sym] = obj
        
        # Restore transitions
        for s1, targets in self.memory_vault.transitions.items():
            for s2, count in targets.items():
                self.transitions[s1][s2] += count
        
        # Restore meta symbols
        for k, v in self.memory_vault.meta_symbols.items():
            self.meta_symbols[k] = v
        
        # Restore roles
        for k, v in self.memory_vault.roles.items():
            self.symbol_roles[k] = v
        
        print(f"🏛️ Tribe {self.tribe_id} restored memory vault")
    
    # =====================================================
    # DECAY AND FORGETTING
    # =====================================================
    
    def decay_symbols(self, population: int):
        """
        Apply decay to symbols based on usage and cultural pressure.
        
        Args:
            population: Current tribe population
        """
        load = self._cultural_load(population)
        
        # Meta dominance - meta symbols suppress base symbols
        self._apply_meta_dominance()
        
        # Meta competition - remove redundant meta symbols
        self._apply_meta_competition()
        
        # Decay low-usage symbols
        for sym, obj in list(self.symbols.items()):
            usage = self.symbol_usage.get(sym, 0)
            
            if usage < 3:
                obj.value -= 0.01 * load
            
            # Forget if value drops too low
            if (obj.value < -1.5 and 
                sym not in (self.memory_vault.symbols if self.memory_vault else {}) and
                sym not in self.meta_symbols):
                self._forget_symbol(sym)
    
    def _apply_meta_dominance(self):
        """Meta symbols reduce value of their component symbols."""
        for meta_key in self.meta_symbols:
            for base in meta_key:
                if base in self.symbols:
                    self.symbols[base].value -= 0.05
    
    def _apply_meta_competition(self):
        """Remove redundant meta symbols."""
        metas = list(self.meta_symbols.items())
        
        for i in range(len(metas)):
            k1, m1 = metas[i]
            for j in range(i + 1, len(metas)):
                k2, m2 = metas[j]
                
                # If meta symbols share symbols
                if k1.intersection(k2):
                    if m1.value >= m2.value:
                        self.meta_symbols.pop(k2, None)
                    else:
                        self.meta_symbols.pop(k1, None)
                        break
    
    # =====================================================
    # GOAL SYMBOLS
    # =====================================================
    
    def goal_symbols(self) -> List[Any]:
        """Get symbols that serve as goals (high causal value)."""
        return [
            s for s, roles in self.symbol_roles.items()
            if roles["causal"] > 1.0
        ]
    
    # =====================================================
    # SPATIAL MEMORY
    # =====================================================
    
    def record_food(self, x: int, y: int, value: float = 1.0):
        """Record food location in spatial memory."""
        self.food_memory[(x, y)] = min(5.0, self.food_memory[(x, y)] + value)
    
    def record_danger(self, x: int, y: int, value: float = 1.5):
        """Record danger location in spatial memory."""
        self.danger_memory[(x, y)] = min(8.0, self.danger_memory[(x, y)] + value)
    
    # =====================================================
    # COMMUNICATION
    # =====================================================
    
    def interpret(self, symbol: Any, success: bool, population: int = 1):
        """
        Process received symbol communication.
        
        Args:
            symbol: Received symbol
            success: Whether interpretation was successful
            population: Current population
        """
        if symbol not in self.symbols:
            return
        
        delta = 0.05 if success else -0.05
        load = self._cultural_load(population)
        self.symbols[symbol].value += delta / load
        self.symbol_usage[symbol] += 1
    
    # =====================================================
    # STATUS
    # =====================================================
    
    def summary(self) -> Dict[str, Any]:
        """Get culture summary."""
        avg_value = 0.0
        if self.symbols:
            avg_value = sum(s.value for s in self.symbols.values()) / len(self.symbols)
        
        return {
            'symbols': len(self.symbols),
            'composed': len(self.composed_symbols),
            'meta': len(self.meta_symbols),
            'goals': len(self.goal_symbols()),
            'avg_value': round(avg_value, 2),
            'home_biome': self.home_biome,
            'adopted': len(self.adopted_symbols),
            'donated': len(self.donated_symbols),
        }
    
    def __repr__(self):
        return f"CultureAgent(tribe={self.tribe_id}, symbols={len(self.symbols)})"
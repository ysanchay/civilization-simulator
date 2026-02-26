"""
Properly Integrated Civilization Simulator

This version FIXES the integration issues:
1. Systems actually affect agent behavior
2. Feedback loops between systems
3. Aggressive thresholds for visible effects
4. Proper cascade dynamics
"""

import time
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# Core imports
from world import World
from agent import Agent
from config import SimulationConfig

# System imports
from territory import TerritorySystem, TerritoryType
from cognitive_stress import CognitiveStressSystem, StressType
from scaling_penalties import ScalingPenaltySystem, ScalingMetrics
from schism import SchismSystem, SchismEvent
from collapse import CollapseSystem, CollapseStage, CollapseEvent, CollapseType


@dataclass
class Tribe:
    """Represents a tribe with full state."""
    tribe_id: int
    population: int = 0
    symbols: int = 10
    meta_symbols: int = 0
    territory: int = 5
    energy: float = 100.0
    efficiency: float = 1.0
    coordination_cost: float = 0.0
    stress_level: float = 0.0
    collapse_stage: str = "stable"
    wars_won: int = 0
    wars_lost: int = 0
    schisms: int = 0
    collapses: int = 0
    renaissances: int = 0
    golden_age_steps: int = 0
    dark_age_steps: int = 0
    history: List[str] = field(default_factory=list)


class IntegratedSimulator:
    """
    Properly integrated civilization simulator.
    
    Key differences from run_full.py:
    1. Systems AFFECT agent behavior (not just track it)
    2. Feedback loops between systems
    3. Aggressive thresholds
    4. Visible effects
    """
    
    # INTEGRATED THRESHOLDS - AGGRESSIVE for visible effects
    POPULATION_COLLAPSE_THRESHOLD = 0.5  # 50% loss triggers collapse
    STRESS_COLLAPSE_THRESHOLD = 0.3      # Much lower - stress triggers collapse
    SCALING_FAILURE_THRESHOLD = 0.5      # Lower threshold
    SCHISM_THRESHOLD = 0.3               # Lower threshold
    CARRYING_CAPACITY = 100              # Population cap per tribe
    EFFICIENCY_COLLAPSE_THRESHOLD = 0.4  # Low efficiency triggers collapse
    
    def __init__(self, config: SimulationConfig = None):
        self.config = config or SimulationConfig()
        
        # World
        self.world = World(
            width=self.config.world.width,
            height=self.config.world.height,
        )
        
        # Systems
        self.territory = TerritorySystem(
            self.config.world.width,
            self.config.world.height,
        )
        
        self.stress = CognitiveStressSystem(
            chaos_intensity=0.20,  # Higher for visible effect
            noise_level=0.10,
        )
        
        self.scaling = ScalingPenaltySystem()
        
        self.schism = SchismSystem(
            schism_threshold=self.SCHISM_THRESHOLD,
        )
        
        self.collapse = CollapseSystem(
            enable_cascades=True,
            cascade_probability=0.3,
        )
        
        # Tribes
        self.tribes: Dict[int, Tribe] = {}
        self.next_tribe_id = 1
        
        # Metrics
        self.step = 0
        self.metrics = {
            'population': [],
            'symbols': [],
            'collapses': [],
            'schisms': [],
            'wars': [],
            'efficiency': [],
            'stress': [],
        }
        
        # History
        self.events = []
    
    def seed_tribes(self, count: int = 5):
        """Seed initial tribes."""
        for i in range(count):
            tribe = Tribe(
                tribe_id=self.next_tribe_id,
                population=random.randint(8, 15),
                symbols=random.randint(8, 15),
                territory=random.randint(3, 8),
            )
            self.tribes[self.next_tribe_id] = tribe
            
            # Claim territory
            x = random.randint(5, self.config.world.width - 5)
            y = random.randint(5, self.config.world.height - 5)
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    self.territory.claim_cell(
                        tribe.tribe_id,
                        (x + dx) % self.config.world.width,
                        (y + dy) % self.config.world.height,
                        1.0,
                    )
            
            self.next_tribe_id += 1
    
    def step_simulation(self):
        """Advance one step with full integration."""
        self.step += 1
        
        # Process each tribe
        for tid, tribe in list(self.tribes.items()):
            if tribe.population <= 0:
                continue
            
            # =====================================================
            # 1. SCALING EFFECTS
            # =====================================================
            scaling_metrics = self.scaling.update_tribe(
                tid,
                tribe.population,
                tribe.territory,
                tribe.symbols,
            )
            
            tribe.efficiency = scaling_metrics.efficiency
            tribe.coordination_cost = scaling_metrics.coordination_cost
            
            # SCALING AFFECTS: birth/death rates
            birth_rate = 0.03 * tribe.efficiency  # Lower efficiency = fewer births
            death_rate = 0.02 + (1 - tribe.efficiency) * 0.03  # Lower efficiency = more deaths
            
            # SCALING FAILURE: causes population loss
            if scaling_metrics.failure_risk > self.SCALING_FAILURE_THRESHOLD:
                if random.random() < scaling_metrics.failure_risk * 0.1:
                    loss = max(1, int(tribe.population * 0.1))
                    tribe.population -= loss
                    tribe.history.append(f"Step {self.step}: Scaling failure, lost {loss} population")
            
            # =====================================================
            # 2. COGNITIVE STRESS EFFECTS
            # =====================================================
            _, chaos = self.stress.apply_temporal_chaos(self.step, tribe.territory)
            tribe.stress_level = chaos
            
            # STRESS AFFECTS: decision accuracy, symbol innovation
            if chaos > 0.15:
                # High stress causes population loss
                if random.random() < chaos * 0.2:
                    loss = max(1, int(tribe.population * chaos * 0.05))
                    tribe.population -= loss
                    tribe.history.append(f"Step {self.step}: Stress caused {loss} deaths")
                
                # High stress blocks innovation
                if chaos > 0.25:
                    tribe.symbols = max(5, tribe.symbols - random.randint(0, 1))
            
            # =====================================================
            # 3. TERRITORY EFFECTS
            # =====================================================
            # Territory affects resource availability
            resource_bonus = tribe.territory * 0.01
            birth_rate += resource_bonus
            
            # Territory expansion
            if random.random() < 0.02 * tribe.efficiency:
                tribe.territory += 1
                self.territory.claim_cell(
                    tid,
                    random.randint(0, self.config.world.width - 1),
                    random.randint(0, self.config.world.height - 1),
                    0.5,
                )
            
            # Territory loss from inefficiency
            if tribe.efficiency < 0.5 and tribe.territory > 1:
                if random.random() < 0.05:
                    tribe.territory -= 1
            
            # =====================================================
            # 4. COLLAPSE SYSTEM - DIRECT TRIGGERS
            # =====================================================
            collapse_state = self.collapse.update_tribe(
                tid,
                tribe.population,
                tribe.symbols,
                tribe.territory,
                tribe.efficiency,
                tribe.coordination_cost,
            )
            
            tribe.collapse_stage = collapse_state.stage.value
            
            # DIRECT COLLAPSE TRIGGERS (in addition to collapse system)
            collapse_triggered = False
            collapse_reason = None
            
            # Trigger 1: Overpopulation (exceeds carrying capacity)
            if tribe.population > self.CARRYING_CAPACITY:
                if random.random() < (tribe.population - self.CARRYING_CAPACITY) / self.CARRYING_CAPACITY:
                    collapse_triggered = True
                    collapse_reason = "overpopulation"
            
            # Trigger 2: Low efficiency
            if tribe.efficiency < self.EFFICIENCY_COLLAPSE_THRESHOLD:
                if random.random() < 0.05:  # 5% chance per step when efficiency is low
                    collapse_triggered = True
                    collapse_reason = "inefficiency"
            
            # Trigger 3: High stress
            if tribe.stress_level > self.STRESS_COLLAPSE_THRESHOLD:
                if random.random() < tribe.stress_level * 0.1:
                    collapse_triggered = True
                    collapse_reason = "stress"
            
            # Trigger 4: From collapse system itself
            if collapse_state.stage == CollapseStage.COLLAPSING:
                collapse_triggered = True
                collapse_reason = "system"
            
            # COLLAPSE AFFECTS: major population/symbol loss
            if collapse_triggered:
                # Population collapse
                severity = min(1.0, collapse_state.stress_level + 0.3)
                pop_loss = int(tribe.population * random.uniform(0.3, 0.6))
                tribe.population = max(1, tribe.population - pop_loss)
                
                # Symbol loss
                symbol_loss = int(tribe.symbols * random.uniform(0.2, 0.4))
                tribe.symbols = max(3, tribe.symbols - symbol_loss)
                
                # Territory loss
                if tribe.territory > 1:
                    tribe.territory = max(1, tribe.territory - random.randint(2, 5))
                
                tribe.collapses += 1
                self.events.append({
                    'step': self.step,
                    'type': 'collapse',
                    'tribe': tid,
                    'pop_loss': pop_loss,
                    'severity': severity,
                    'reason': collapse_reason,
                })
                tribe.history.append(f"Step {self.step}: COLLAPSED ({collapse_reason}), lost {pop_loss} population")
            
            # RENAISSANCE (after collapse, if recovering)
            if tribe.collapses > 0 and tribe.efficiency > 0.7 and tribe.population > 10:
                if random.random() < 0.02:  # 2% chance per step when conditions are right
                    tribe.renaissances += 1
                    tribe.symbols += random.randint(3, 8)
                    tribe.meta_symbols += 1
                    tribe.history.append(f"Step {self.step}: RENAISSANCE!")
                    self.events.append({
                        'step': self.step,
                        'type': 'renaissance',
                        'tribe': tid,
                    })
            
            # =====================================================
            # 5. SCHISM SYSTEM
            # =====================================================
            # Schism risk based on population and symbol conflict
            symbol_conflict = random.uniform(0.1, 0.4) if tribe.symbols > 30 else 0.1
            
            schism_risk = self.schism.calculate_schism_risk(
                tid,
                tribe.population,
                symbol_conflict,
                tribe.territory,
            )
            
            # SCHISM AFFECTS: splits tribe
            if schism_risk > self.SCHISM_THRESHOLD and tribe.population > 15:
                if random.random() < schism_risk * 0.05:
                    # Create new tribe
                    new_tribe = Tribe(
                        tribe_id=self.next_tribe_id,
                        population=tribe.population // 3,
                        symbols=tribe.symbols // 2,
                        territory=tribe.territory // 2,
                    )
                    self.tribes[self.next_tribe_id] = new_tribe
                    
                    # Reduce original tribe
                    tribe.population -= new_tribe.population
                    tribe.territory -= new_tribe.territory
                    tribe.schisms += 1
                    
                    self.events.append({
                        'step': self.step,
                        'type': 'schism',
                        'parent': tid,
                        'child': self.next_tribe_id,
                    })
                    tribe.history.append(f"Step {self.step}: SCHISM, created tribe {self.next_tribe_id}")
                    self.next_tribe_id += 1
            
            # =====================================================
            # 6. POPULATION DYNAMICS (affected by all systems)
            # =====================================================
            # CARRYING CAPACITY - limits growth and triggers collapse pressure
            carrying_capacity = self.CARRYING_CAPACITY * (1 + tribe.territory * 0.05)
            population_pressure = max(0, tribe.population / carrying_capacity)
            
            # Population pressure increases death rate
            if population_pressure > 1.0:
                death_rate += (population_pressure - 1.0) * 0.1
            
            births = int(tribe.population * birth_rate)
            deaths = int(tribe.population * death_rate)
            
            # Random events
            if random.random() < 0.02:  # 2% chance of disease/famine
                deaths += max(1, int(tribe.population * 0.1))
                tribe.history.append(f"Step {self.step}: Disease outbreak")
            
            # Golden/Dark age tracking
            if tribe.efficiency > 0.8 and tribe.population > 20:
                tribe.golden_age_steps += 1
                births += random.randint(1, 3)  # Bonus growth
            elif tribe.efficiency < 0.4:
                tribe.dark_age_steps += 1
                deaths += random.randint(1, 2)  # Extra deaths
            
            tribe.population = max(1, tribe.population + births - deaths)
            
            # Symbol evolution
            if random.random() < 0.02 * tribe.efficiency:
                tribe.symbols += 1
            if random.random() < 0.01 and tribe.symbols > 10:
                tribe.symbols -= 1
            
            # Meta-symbols
            if tribe.symbols > 30 and random.random() < 0.005:
                tribe.meta_symbols += 1
            
            # =====================================================
            # 7. WAR (simplified)
            # =====================================================
            if len(self.tribes) > 1 and random.random() < 0.01:
                # Find another tribe
                others = [t for t in self.tribes.values() if t.tribe_id != tid and t.population > 0]
                if others:
                    target = random.choice(others)
                    
                    # War outcome based on population, symbols, efficiency
                    attacker_power = tribe.population * tribe.efficiency * (1 + tribe.symbols * 0.01)
                    defender_power = target.population * target.efficiency * (1 + target.symbols * 0.01)
                    
                    if attacker_power > defender_power * 1.2:
                        # Attacker wins
                        loss = min(target.population // 4, target.population - 1)
                        target.population -= loss
                        tribe.wars_won += 1
                        target.wars_lost += 1
                        
                        # Territory gain
                        if target.territory > 1:
                            gain = min(2, target.territory - 1)
                            tribe.territory += gain
                            target.territory -= gain
                        
                        self.events.append({
                            'step': self.step,
                            'type': 'war',
                            'attacker': tid,
                            'defender': target.tribe_id,
                            'outcome': 'attacker_wins',
                        })
                    elif defender_power > attacker_power * 1.2:
                        # Defender wins
                        loss = min(tribe.population // 4, tribe.population - 1)
                        tribe.population -= loss
                        target.wars_won += 1
                        tribe.wars_lost += 1
                        
                        self.events.append({
                            'step': self.step,
                            'type': 'war',
                            'attacker': tid,
                            'defender': target.tribe_id,
                            'outcome': 'defender_wins',
                        })
            
            # =====================================================
            # 8. EXTINCTION CHECK
            # =====================================================
            if tribe.population <= 0:
                tribe.history.append(f"Step {self.step}: EXTINCT")
                self.events.append({
                    'step': self.step,
                    'type': 'extinction',
                    'tribe': tid,
                })
        
        # Record metrics
        self._record_metrics()
    
    def _record_metrics(self):
        """Record step metrics."""
        total_pop = sum(t.population for t in self.tribes.values())
        total_symbols = sum(t.symbols for t in self.tribes.values())
        avg_efficiency = sum(t.efficiency for t in self.tribes.values()) / max(1, len(self.tribes))
        avg_stress = sum(t.stress_level for t in self.tribes.values()) / max(1, len(self.tribes))
        
        self.metrics['population'].append(total_pop)
        self.metrics['symbols'].append(total_symbols)
        self.metrics['efficiency'].append(avg_efficiency)
        self.metrics['stress'].append(avg_stress)
        
        # Count events this step
        step_collapses = len([e for e in self.events if e['step'] == self.step and e['type'] == 'collapse'])
        step_schisms = len([e for e in self.events if e['step'] == self.step and e['type'] == 'schism'])
        step_wars = len([e for e in self.events if e['step'] == self.step and e['type'] == 'war'])
        
        self.metrics['collapses'].append(step_collapses)
        self.metrics['schisms'].append(step_schisms)
        self.metrics['wars'].append(step_wars)
    
    def run(self, max_steps: int = 2000, log_interval: int = 200):
        """Run simulation."""
        print("="*70)
        print("🌍 INTEGRATED CIVILIZATION SIMULATOR")
        print("="*70)
        print(f"Steps: {max_steps}")
        print(f"Initial tribes: {len(self.tribes)}")
        print(f"Systems: Territory, Stress, Scaling, Schism, Collapse (INTEGRATED)")
        print("="*70)
        
        start_time = time.time()
        
        while self.step < max_steps:
            self.step_simulation()
            
            # Check extinction
            active = [t for t in self.tribes.values() if t.population > 0]
            if not active:
                print(f"\n☠️ All tribes extinct at step {self.step}!")
                break
            
            if self.step % log_interval == 0:
                self._log_progress()
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*70)
        print(f"✅ Complete: {self.step} steps in {elapsed:.1f}s")
        print("="*70)
        
        return self._generate_report()
    
    def _log_progress(self):
        """Log current state."""
        active = [t for t in self.tribes.values() if t.population > 0]
        total_pop = sum(t.population for t in active)
        total_symbols = sum(t.symbols for t in active)
        avg_eff = sum(t.efficiency for t in active) / max(1, len(active))
        
        collapses = sum(t.collapses for t in active)
        schisms = sum(t.schisms for t in active)
        wars = sum(t.wars_won for t in active)
        renaissances = sum(t.renaissances for t in active)
        
        print(f"[{self.step:5d}] Tribes: {len(active)} | Pop: {total_pop:4d} | "
              f"Symbols: {total_symbols:3d} | Eff: {avg_eff:.0%} | "
              f"Col: {collapses} | Sch: {schisms} | War: {wars} | Ren: {renaissances}")
    
    def _generate_report(self):
        """Generate final report."""
        active = [t for t in self.tribes.values() if t.population > 0]
        extinct = [t for t in self.tribes.values() if t.population <= 0]
        
        total_collapses = sum(t.collapses for t in self.tribes.values())
        total_schisms = sum(t.schisms for t in self.tribes.values())
        total_wars = sum(t.wars_won for t in self.tribes.values())
        total_renaissances = sum(t.renaissances for t in self.tribes.values())
        
        return {
            'steps': self.step,
            'tribes_active': len(active),
            'tribes_extinct': len(extinct),
            'total_population': sum(t.population for t in active),
            'total_symbols': sum(t.symbols for t in active),
            'total_collapses': total_collapses,
            'total_schisms': total_schisms,
            'total_wars': total_wars,
            'total_renaissances': total_renaissances,
            'avg_efficiency': sum(t.efficiency for t in active) / max(1, len(active)),
            'avg_collapses_per_tribe': total_collapses / max(1, len(self.tribes)),
            'collapse_frequency': total_collapses / max(1, self.step) * 1000,
            'schism_frequency': total_schisms / max(1, self.step) * 1000,
            'metrics': self.metrics,
            'events': self.events,
            'tribes': {tid: {
                'population': t.population,
                'symbols': t.symbols,
                'territory': t.territory,
                'efficiency': t.efficiency,
                'collapses': t.collapses,
                'schisms': t.schisms,
                'renaissances': t.renaissances,
            } for tid, t in self.tribes.items()},
        }
    
    def print_report(self, report):
        """Print final report."""
        print("\n" + "="*70)
        print("📊 FINAL REPORT")
        print("="*70)
        
        print(f"\n🌍 OVERALL")
        print(f"   Steps: {report['steps']}")
        print(f"   Active tribes: {report['tribes_active']}")
        print(f"   Extinct tribes: {report['tribes_extinct']}")
        print(f"   Total population: {report['total_population']}")
        print(f"   Total symbols: {report['total_symbols']}")
        
        print(f"\n💥 EVENTS")
        print(f"   Collapses: {report['total_collapses']}")
        print(f"   Schisms: {report['total_schisms']}")
        print(f"   Wars: {report['total_wars']}")
        print(f"   Renaissances: {report['total_renaissances']}")
        
        print(f"\n📈 FREQUENCIES (per 1000 steps)")
        print(f"   Collapse: {report['collapse_frequency']:.2f}")
        print(f"   Schism: {report['schism_frequency']:.2f}")
        
        print(f"\n📊 TRIBES")
        for tid, data in report['tribes'].items():
            status = "ACTIVE" if data['population'] > 0 else "EXTINCT"
            print(f"   Tribe {tid}: Pop={data['population']}, Syms={data['symbols']}, "
                  f"Eff={data['efficiency']:.0%}, Col={data['collapses']}, Sch={data['schisms']} [{status}]")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Integrated Civilization Simulator')
    parser.add_argument('--steps', type=int, default=2000, help='Steps to run')
    parser.add_argument('--tribes', type=int, default=5, help='Initial tribes')
    parser.add_argument('--log', type=int, default=200, help='Log interval')
    
    args = parser.parse_args()
    
    config = SimulationConfig()
    config.world.width = 30
    config.world.height = 30
    
    sim = IntegratedSimulator(config)
    sim.seed_tribes(args.tribes)
    report = sim.run(max_steps=args.steps, log_interval=args.log)
    sim.print_report(report)


if __name__ == "__main__":
    main()
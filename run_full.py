"""
Full Civilization Simulator with All 6 New Systems

Integrates:
1. Territory System - Geographic ownership
2. Historical Memory - Written history, myths, eras
3. Cognitive Stress - Intelligence challenges
4. Scaling Penalties - Empire fragility
5. Cultural Schism - Ideological splits
6. Collapse System - Rise and fall cycles
"""

import time
import random
from datetime import datetime
from pathlib import Path

from world import World
from agent import Agent
from run_enhanced import EnhancedSimulation, EnhancedKnowledgeMetrics
from config import SimulationConfig

# New systems
from territory import TerritorySystem, TerritoryType
from historical_memory import HistoricalMemory, EventType, EraType
from cognitive_stress import CognitiveStressSystem, StressType
from scaling_penalties import ScalingPenaltySystem
from schism import SchismSystem, SchismType
from collapse import CollapseSystem, CollapseStage


class FullCivilizationSimulator(EnhancedSimulation):
    """
    Complete civilization simulator with all features.
    """
    
    def __init__(self, config: SimulationConfig = None):
        super().__init__(config)
        
        # Initialize new systems
        self.territory = TerritorySystem(
            width=config.world.width if config else 20,
            height=config.world.height if config else 20,
        )
        
        self.history = HistoricalMemory(
            max_events=1000,
            myth_threshold=0.7,
        )
        
        self.cognitive_stress = CognitiveStressSystem(
            chaos_intensity=0.15,
            noise_level=0.08,
            overload_threshold=150,
        )
        
        self.scaling = ScalingPenaltySystem(
            enable_coordination_failure=True,
            enable_administrative_collapse=True,
            enable_symbol_overload=True,
        )
        
        self.schism = SchismSystem(
            schism_threshold=0.6,
            conflict_threshold=0.4,
            min_faction_size=3,
        )
        
        self.collapse = CollapseSystem(
            enable_cascades=True,
            cascade_probability=0.25,
        )
        
        # Track new metrics
        self.full_history = {
            'territory_changes': [],
            'eras': [],
            'stress_events': [],
            'scaling_failures': [],
            'schisms': [],
            'collapses': [],
            'renaissances': [],
        }
    
    def seed_agents(self, count: int = 5):
        """Seed initial agents with territory claims."""
        super().seed_agents(count)
        
        # Record tribe foundings
        for agent in self.world.agents:
            self.history.record_founding(
                step=0,
                tribe_id=agent.tribe_id,
                location=(agent.x, agent.y),
            )
            
            # Claim initial territory
            self.territory.claim_cell(
                tribe_id=agent.tribe_id,
                x=agent.x,
                y=agent.y,
                strength=1.0,
            )
    
    def step_simulation(self):
        """Advance simulation with all new systems."""
        self.step += 1
        
        # Store previous state
        self.prev_symbols.clear()
        for agent in self.world.agents:
            self.prev_symbols[agent] = agent.last_symbol
        
        # Apply cognitive stress to time
        world_time = self.world.world_time
        distorted_time, chaos_level = self.cognitive_stress.apply_temporal_chaos(
            self.step, world_time
        )
        self.world.world_time = distorted_time
        
        # Track previous knowledge
        prev_knowledge = self._capture_knowledge_state()
        
        # Generate false signals
        if random.random() < 0.05:  # 5% chance
            self.cognitive_stress.generate_false_signals(
                self.step,
                (self.world.width, self.world.height),
                count=random.randint(1, 3),
            )
        
        # Advance world
        prev_pop = len(self.world.agents)
        self.world.step()
        curr_pop = len(self.world.agents)
        
        # Update territory
        self._update_territory()
        
        # Update knowledge metrics
        self._update_knowledge_metrics()
        
        # Process competition (from parent)
        if self.config.competition_enabled:
            self._process_competition()
        
        # Process new systems
        self._process_scaling()
        self._process_schism()
        self._process_collapse()
        self._process_historical_memory()
        
        # Process knowledge transfer (from parent)
        self._process_knowledge_transfer()
        
        # Record metrics
        self.metrics_collector.record_step(
            self.step, self.world, self.world.agents, self.world.tribes
        )
        
        # Track learning
        curr_knowledge = self._capture_knowledge_state()
        learning_delta = self._calculate_learning_delta(prev_knowledge, curr_knowledge)
        self.history['knowledge_transfer'].append(learning_delta)
        
        # Update history
        self._update_history()
        
        # Update territory system
        self.territory.update(self.step)
    
    def _update_territory(self):
        """Update territory claims based on agent positions."""
        tribe_positions = {}
        
        for agent in self.world.agents:
            tid = agent.tribe_id
            if tid not in tribe_positions:
                tribe_positions[tid] = []
            tribe_positions[tid].append((agent.x, agent.y))
            
            # Claim territory where agent is
            self.territory.claim_cell(tid, agent.x, agent.y, strength=0.5)
    
    def _process_scaling(self):
        """Process scaling penalties for all tribes."""
        for tid, tribe in self.world.tribes.items():
            pop = sum(1 for a in self.world.agents if a.tribe_id == tid)
            territory = self.territory.get_territory_size(tid)
            symbols = len(tribe.symbols) if hasattr(tribe, 'symbols') else 0
            
            # Update scaling metrics
            metrics = self.scaling.update_tribe(tid, pop, territory, symbols)
            
            # Check for failure
            failure = self.scaling.apply_scaling_penalty(tid, self.step)
            if failure:
                self.full_history['scaling_failures'].append({
                    'step': self.step,
                    'tribe': tid,
                    'type': failure.failure_type.value,
                    'severity': failure.severity,
                })
                
                # Apply penalty to agents
                for agent in self.world.agents:
                    if agent.tribe_id == tid:
                        agent.energy -= failure.severity * 2
            
            # Update historical memory with era
            self.history.update_era(self.step, tid, pop, symbols, territory)
    
    def _process_schism(self):
        """Process potential schisms."""
        for tid, tribe in list(self.world.tribes.items()):
            pop = sum(1 for a in self.world.agents if a.tribe_id == tid)
            symbols = {str(k): v.value for k, v in tribe.symbols.items()} if hasattr(tribe, 'symbols') else {}
            territory = self.territory.get_territory_size(tid)
            
            # Check for schism
            schism_event = self.schism.check_schism(
                self.step, tid, pop, symbols, territory
            )
            
            if schism_event:
                self.full_history['schisms'].append({
                    'step': self.step,
                    'parent': tid,
                    'type': schism_event.schism_type.value,
                    'members_split': schism_event.members_split,
                })
                
                # Record in history
                self.history.record_event(
                    step=self.step,
                    event_type=EventType.CULTURAL_PEAK,  # Using existing type
                    tribe_id=tid,
                    description=f"Tribe {tid} experienced {schism_event.schism_type.value} schism",
                    significance=0.8,
                )
    
    def _process_collapse(self):
        """Process potential collapses."""
        for tid, tribe in list(self.world.tribes.items()):
            pop = sum(1 for a in self.world.agents if a.tribe_id == tid)
            symbols = len(tribe.symbols) if hasattr(tribe, 'symbols') else 0
            territory = self.territory.get_territory_size(tid)
            
            # Get scaling metrics
            scaling_metrics = self.scaling.get_metrics(tid)
            efficiency = scaling_metrics.efficiency if scaling_metrics else 1.0
            coord_cost = scaling_metrics.coordination_cost if scaling_metrics else 0.0
            
            # Update collapse state
            self.collapse.update_tribe(
                tid, pop, symbols, territory, efficiency, coord_cost
            )
            
            # Check for collapse
            collapse_event = self.collapse.check_collapse(
                self.step, tid, pop, symbols, territory
            )
            
            if collapse_event:
                self.full_history['collapses'].append({
                    'step': self.step,
                    'tribe': tid,
                    'type': collapse_event.collapse_type.value,
                    'severity': collapse_event.severity,
                    'pop_loss': collapse_event.population_before - collapse_event.population_after,
                })
                
                # Record in history
                self.history.record_collapse(
                    self.step, tid, collapse_event.collapse_type.value
                )
                
                # Apply collapse effects
                self._apply_collapse_effects(tid, collapse_event)
            
            # Check for recovery
            recovery = self.collapse.check_recovery(self.step, tid, pop, symbols)
            if recovery:
                self.full_history['renaissances'].append({
                    'step': self.step,
                    'tribe': tid,
                    'symbols_recovered': recovery.symbols_recovered,
                })
    
    def _apply_collapse_effects(self, tribe_id: int, event):
        """Apply collapse effects to tribe."""
        # Remove agents
        agents = [a for a in self.world.agents if a.tribe_id == tribe_id]
        loss = event.population_before - event.population_after
        
        for agent in random.sample(agents, min(loss, len(agents))):
            self.world.agents.remove(agent)
            if self.world.grid[agent.y][agent.x] == agent:
                self.world.grid[agent.y][agent.x] = None
        
        # Lose territory
        territory = list(self.territory.get_territory(tribe_id))
        territory_loss = event.territory_lost
        
        for x, y in random.sample(territory, min(territory_loss, len(territory))):
            self.territory.lose_cell(tribe_id, x, y)
    
    def _process_historical_memory(self):
        """Process historical events."""
        # Record wars
        for war in self.history.get('wars', []):
            if war.get('step') == self.step:
                self.history.record_war(
                    step=self.step,
                    attacker=war['attacker'],
                    defender=war['defender'],
                    winner=war['attacker'] if war['outcome'] == 'attacker_wins' else war['defender'],
                    casualties={},
                )
        
        # Record alliances
        for alliance in self.history.get('alliances', []):
            if alliance.get('step') == self.step:
                self.history.record_alliance(
                    self.step,
                    alliance['tribe_a'],
                    alliance['tribe_b'],
                )
    
    def run(self, max_steps: int = 5000, log_interval: int = 200):
        """Run simulation with all systems."""
        print("="*70)
        print("🌍 FULL CIVILIZATION SIMULATOR")
        print("="*70)
        print(f"World: {self.config.world.width}x{self.config.world.height}")
        print(f"Steps: {max_steps}")
        print(f"Systems: Territory, History, Stress, Scaling, Schism, Collapse")
        print("="*70)
        
        start_time = time.time()
        
        try:
            while self.step < max_steps:
                self.step_simulation()
                
                if len(self.world.agents) == 0:
                    print("\n☠️ All agents extinct!")
                    break
                
                if self.step % log_interval == 0:
                    self._log_full_progress()
                
                # Update learning history
                for tid in self.world.tribes:
                    acc = self.knowledge_metrics.temporal_accuracy(tid)
                    self.knowledge_metrics.learning_history[tid].append(acc)
                
                # Save brains periodically
                if self.step > 0 and self.step % 1000 == 0:
                    self.world.save_brains()
                
        except KeyboardInterrupt:
            print("\n⏹️ Stopped by user")
        
        elapsed = time.time() - start_time
        
        # Final save
        self.world.save_brains()
        
        print("\n" + "="*70)
        print(f"✅ Complete: {self.step} steps in {elapsed:.1f}s")
        print(f"   World expansions: {self.world.expansion_count}")
        
        return self._generate_full_report()
    
    def _log_full_progress(self):
        """Log progress with all systems."""
        pop = len(self.world.agents)
        density = self.world.get_density()
        tribes = len([t for t in self.world.tribes.values() if any(a.tribe_id == t.tribe_id for a in self.world.agents)])
        symbols = self.history['symbols'][-1] if self.history['symbols'] else 0
        meta = self.history['meta'][-1] if self.history['meta'] else 0
        acc = self.history['temporal_accuracy'][-1] if self.history['temporal_accuracy'] else 0
        wars = len(self.history['wars'])
        collapses = len(self.full_history['collapses'])
        schisms = len(self.full_history['schisms'])
        expansions = self.world.expansion_count
        
        # Get system status
        territory_status = self.territory.status()
        stress_status = self.cognitive_stress.status()
        scaling_status = self.scaling.status()
        collapse_status = self.collapse.status()
        
        print(f"[{self.step:5d}] Pop: {pop:3d} | Density: {density:.1%} | Tribes: {tribes} | "
              f"Symbols: {symbols:3d} | Meta: {meta:2d} | Acc: {acc:.2f}")
        print(f"        Wars: {wars} | Collapses: {collapses} | Schisms: {schisms} | "
              f"Expansions: {expansions} | Chaos: {stress_status['time_distortion']:.2f}")
    
    def _generate_full_report(self):
        """Generate comprehensive report."""
        report = super()._generate_report()
        
        # Add new system data
        report['territory'] = self.territory.status()
        report['historical'] = self.history.status()
        report['stress'] = self.cognitive_stress.status()
        report['scaling'] = self.scaling.status()
        report['schism'] = self.schism.status()
        report['collapse'] = self.collapse.status()
        
        report['full_history'] = self.full_history
        
        return report
    
    def print_report(self, report):
        """Print comprehensive report."""
        super().print_report(report)
        
        # Print new system summaries
        print("\n" + "="*70)
        print("📊 ADDITIONAL SYSTEMS")
        print("="*70)
        
        # Territory
        t = report['territory']
        print(f"\n🌍 TERRITORY")
        print(f"   Claimed: {t['total_claimed']} cells")
        print(f"   Contested: {t['contested_cells']} cells")
        print(f"   Conquests: {t['total_conquests']}")
        
        # Historical
        h = report['historical']
        print(f"\n📜 HISTORY")
        print(f"   Events: {h['total_events']}")
        print(f"   Myths: {h['total_myths']}")
        print(f"   Active Eras: {h['active_tribes']}")
        
        # Stress
        s = report['stress']
        print(f"\n🧠 COGNITIVE STRESS")
        print(f"   Time Distortion: {s['time_distortion']:.2f}")
        print(f"   False Signals: {s['false_signals']}")
        print(f"   Stressed Tribes: {s['stressed_tribes']}")
        
        # Scaling
        sc = report['scaling']
        print(f"\n📊 SCALING")
        print(f"   Failures: {sc['total_failures']}")
        print(f"   Collapses: {sc['total_collapses']}")
        print(f"   Avg Efficiency: {sc['avg_efficiency']:.1%}")
        
        # Schism
        sh = report['schism']
        print(f"\n⚔️ SCHISM")
        print(f"   Total Schisms: {sh['total_schisms']}")
        print(f"   Active Factions: {sh['active_factions']}")
        
        # Collapse
        co = report['collapse']
        print(f"\n💥 COLLAPSE")
        print(f"   Collapses: {co['total_collapses']}")
        print(f"   Extinctions: {co['total_extinctions']}")
        print(f"   Renaissances: {co['total_renaissances']}")
        print(f"   Stable: {co['stable_tribes']} | Collapsing: {co['collapsing_tribes']}")
        print(f"   Recovering: {co['recovering_tribes']}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Full Civilization Simulator')
    parser.add_argument('--steps', type=int, default=3000, help='Number of steps')
    parser.add_argument('--width', type=int, default=25, help='World width')
    parser.add_argument('--height', type=int, default=25, help='World height')
    parser.add_argument('--agents', type=int, default=15, help='Initial agents')
    parser.add_argument('--log', type=int, default=300, help='Log interval')
    
    args = parser.parse_args()
    
    config = SimulationConfig()
    config.world.width = args.width
    config.world.height = args.height
    config.initial_agents = args.agents
    config.competition_enabled = True
    
    sim = FullCivilizationSimulator(config)
    sim.seed_agents(config.initial_agents)
    report = sim.run(max_steps=args.steps, log_interval=args.log)
    sim.print_report(report)


if __name__ == "__main__":
    main()
"""
Run a full metrics simulation with detailed reporting.
"""

import time
import statistics
from collections import Counter, defaultdict
from datetime import datetime
import json
from pathlib import Path

# Core components
from world import World
from agent import Agent
from metrics import WorldMetrics, KnowledgeMetrics

# Agent architecture
from agents.simulation_agent import SimulationController
from agents.cognition_agent import CognitionAgent
from agents.culture_agent import CultureAgent
from agents.competition_agent import CompetitionAgent
from agents.innovation_agent import InnovationAgent

# Success metrics
from success_metrics import (
    MetricsCollector,
    EmergenceMetrics,
    SurvivalMetrics,
    IntelligenceMetrics,
    SuccessScore,
    evaluate_simulation_use_case,
)

# Configuration
from config import SimulationConfig


class MetricsSimulation:
    """Simulation with comprehensive metrics collection."""
    
    def __init__(self, config: SimulationConfig = None):
        self.config = config or SimulationConfig()
        
        # Core simulation
        self.world = World(
            width=self.config.world.width,
            height=self.config.world.height,
        )
        
        # Metrics
        self.world_metrics = WorldMetrics()
        self.knowledge_metrics = KnowledgeMetrics()
        self.metrics_collector = MetricsCollector(output_dir="metrics")
        
        # Agents
        self.culture_agents = {}
        self.competition_agent = CompetitionAgent()
        self.innovation_agent = InnovationAgent()
        
        # State
        self.step = 0
        self.prev_symbols = {}
        
        # Track events
        self.births_this_step = 0
        self.deaths_this_step = 0
        
        # History for analysis
        self.history = {
            'population': [],
            'symbols': [],
            'composed': [],
            'meta': [],
            'tribes': [],
            'mean_energy': [],
            'temporal_accuracy': [],
        }
    
    def seed_agents(self, count: int = 5):
        """Seed initial agents."""
        for i in range(count):
            agent = Agent(
                name=f"A{i}",
                world=self.world,
                energy=self.config.agent.initial_energy,
            )
            self.world.add_agent(agent)
            
            # Create culture agent for each tribe
            if agent.tribe_id not in self.culture_agents:
                self.culture_agents[agent.tribe_id] = CultureAgent(
                    tribe_id=agent.tribe_id,
                    max_symbols=self.config.culture.max_symbols,
                )
        
        print(f"🌱 Seeded {count} agents in {len(self.world.tribes)} tribes")
    
    def step_simulation(self):
        """Advance simulation by one step."""
        self.step += 1
        self.births_this_step = 0
        self.deaths_this_step = 0
        
        # Store previous symbols
        self.prev_symbols.clear()
        for agent in self.world.agents:
            self.prev_symbols[agent] = agent.last_symbol
        
        # Advance world
        prev_pop = len(self.world.agents)
        self.world.step()
        curr_pop = len(self.world.agents)
        
        # Track births/deaths
        if curr_pop > prev_pop:
            self.births_this_step = curr_pop - prev_pop
            for _ in range(self.births_this_step):
                self.metrics_collector.record_birth('unknown', 0)
        elif curr_pop < prev_pop:
            self.deaths_this_step = prev_pop - curr_pop
            for _ in range(self.deaths_this_step):
                self.metrics_collector.record_death('unknown', 0)
        
        # Update knowledge metrics
        for agent in self.world.agents:
            tribe_id = agent.tribe_id
            prev_pattern = self.prev_symbols.get(agent)
            curr_pattern = agent.last_symbol
            
            self.knowledge_metrics.record_time_transition(
                tribe_id, prev_pattern, curr_pattern
            )
            
            # Track innovations
            if curr_pattern and self.innovation_agent.is_novel(curr_pattern):
                self.metrics_collector.record_innovation('pattern', tribe_id)
        
        # Record step metrics
        self.metrics_collector.record_step(
            self.step,
            self.world,
            self.world.agents,
            self.world.tribes
        )
        
        # Update history
        self._update_history()
    
    def _update_history(self):
        """Update history for analysis."""
        pop = len(self.world.agents)
        self.history['population'].append(pop)
        
        if pop > 0:
            energies = [a.energy for a in self.world.agents]
            self.history['mean_energy'].append(statistics.mean(energies))
        else:
            self.history['mean_energy'].append(0)
        
        # Symbol counts
        total_symbols = 0
        total_composed = 0
        total_meta = 0
        
        for tribe in self.world.tribes.values():
            if hasattr(tribe, 'symbols'):
                total_symbols += len(tribe.symbols)
            if hasattr(tribe, 'composed_symbols'):
                total_composed += len(tribe.composed_symbols)
            if hasattr(tribe, 'meta_symbols'):
                total_meta += len(tribe.meta_symbols)
        
        self.history['symbols'].append(total_symbols)
        self.history['composed'].append(total_composed)
        self.history['meta'].append(total_meta)
        self.history['tribes'].append(len(self.world.tribes))
        
        # Temporal accuracy (average across tribes)
        accuracies = []
        for tid in self.world.tribes:
            acc = self.knowledge_metrics.temporal_accuracy(tid)
            accuracies.append(acc)
        self.history['temporal_accuracy'].append(
            statistics.mean(accuracies) if accuracies else 0
        )
    
    def run(self, max_steps: int = 5000, log_interval: int = 100):
        """Run simulation with metrics collection."""
        print("="*70)
        print("🌍 CIVILIZATION SIMULATOR - FULL METRICS RUN")
        print("="*70)
        print(f"World: {self.config.world.width}x{self.config.world.height}")
        print(f"Steps: {max_steps}")
        print(f"Started: {datetime.now().isoformat()}")
        print("="*70)
        
        start_time = time.time()
        
        try:
            while self.step < max_steps:
                self.step_simulation()
                
                # Check extinction
                if len(self.world.agents) == 0:
                    print("\n☠️ All agents extinct!")
                    break
                
                # Progress logging
                if self.step % log_interval == 0:
                    self._log_progress()
                
        except KeyboardInterrupt:
            print("\n⏹️ Stopped by user")
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*70)
        print("📊 SIMULATION COMPLETE")
        print("="*70)
        print(f"Steps: {self.step}")
        print(f"Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
        
        return self._generate_report()
    
    def _log_progress(self):
        """Log progress."""
        pop = len(self.world.agents)
        tribes = len(self.world.tribes)
        symbols = self.history['symbols'][-1] if self.history['symbols'] else 0
        composed = self.history['composed'][-1] if self.history['composed'] else 0
        meta = self.history['meta'][-1] if self.history['meta'] else 0
        temp_acc = self.history['temporal_accuracy'][-1] if self.history['temporal_accuracy'] else 0
        
        print(f"[{self.step:5d}] Pop: {pop:3d} | Tribes: {tribes} | "
              f"Symbols: {symbols:3d} | Composed: {composed:2d} | Meta: {meta:2d} | "
              f"Temp.Acc: {temp_acc:.2f}")
    
    def _generate_report(self) -> dict:
        """Generate comprehensive report."""
        print("\n📊 Generating metrics report...")
        
        # Calculate metrics
        emergence = self.metrics_collector.calculate_emergence_metrics(self.world.tribes)
        survival = self.metrics_collector.calculate_survival_metrics()
        intelligence = self.metrics_collector.calculate_intelligence_metrics(self.world.tribes)
        success = self.metrics_collector.calculate_success_score(emergence, survival, intelligence)
        
        # Evaluate use cases
        use_cases = {}
        for uc in ['gaming', 'ai_safety', 'education', 'robotics']:
            use_cases[uc] = evaluate_simulation_use_case(uc, emergence, survival, intelligence)
        
        report = {
            'simulation': {
                'steps': self.step,
                'world_size': (self.config.world.width, self.config.world.height),
                'initial_agents': self.config.initial_agents,
            },
            'emergence': emergence.to_dict(),
            'survival': survival.to_dict(),
            'intelligence': intelligence.to_dict(),
            'success': success.to_dict(),
            'use_cases': use_cases,
            'history': {
                'population_final': self.history['population'][-1] if self.history['population'] else 0,
                'population_max': max(self.history['population']) if self.history['population'] else 0,
                'population_min': min(self.history['population']) if self.history['population'] else 0,
                'symbols_final': self.history['symbols'][-1] if self.history['symbols'] else 0,
                'composed_final': self.history['composed'][-1] if self.history['composed'] else 0,
                'meta_final': self.history['meta'][-1] if self.history['meta'] else 0,
            },
            'tribes': self._tribe_report(),
        }
        
        # Save report
        Path("metrics").mkdir(exist_ok=True)
        path = self.metrics_collector.save_report(self.world.tribes)
        print(f"📄 Report saved to: {path}")
        
        return report
    
    def _tribe_report(self) -> dict:
        """Generate tribe-specific report."""
        tribes_data = {}
        
        for tid, tribe in self.world.tribes.items():
            pop = sum(1 for a in self.world.agents if a.tribe_id == tid)
            
            tribe_data = {
                'population': pop,
                'symbols': len(tribe.symbols) if hasattr(tribe, 'symbols') else 0,
                'composed': len(tribe.composed_symbols) if hasattr(tribe, 'composed_symbols') else 0,
                'meta': len(tribe.meta_symbols) if hasattr(tribe, 'meta_symbols') else 0,
                'home_biome': tribe.home_biome if hasattr(tribe, 'home_biome') else 0,
            }
            
            # Goal symbols
            if hasattr(tribe, 'goal_symbols'):
                tribe_data['goals'] = len(tribe.goal_symbols())
            
            # Summary
            if hasattr(tribe, 'summary'):
                summary = tribe.summary()
                tribe_data['avg_value'] = summary.get('avg_value', 0)
            
            tribes_data[tid] = tribe_data
        
        return tribes_data
    
    def print_report(self, report: dict):
        """Print formatted report."""
        print("\n" + "="*70)
        print("📊 COMPREHENSIVE METRICS REPORT")
        print("="*70)
        
        # Emergence
        e = report['emergence']
        print("\n🧬 EMERGENCE METRICS")
        print("-"*40)
        print(f"  Vocabulary Size: {e['language']['vocabulary_size']}")
        print(f"  Composed Symbols: {e['language']['composed_symbols']}")
        print(f"  Meta-Symbols: {e['language']['meta_symbols']}")
        print(f"  Abstraction Depth: {e['language']['abstraction_depth']}")
        print(f"  Tribes: {e['social']['tribe_count']}")
        print(f"  Alliances: {e['social']['alliance_count']}")
        print(f"  Wars: {e['social']['war_count']}")
        
        # Survival
        s = report['survival']
        print("\n💓 SURVIVAL METRICS")
        print("-"*40)
        print(f"  Population Final: {s['population']['final']}")
        print(f"  Population Max: {s['population']['max']}")
        print(f"  Population Mean: {s['population']['mean']:.1f}")
        print(f"  Tribes Surviving: {s['survival']['tribes_surviving']}")
        print(f"  Tribes Extinct: {s['survival']['tribes_extinct']}")
        print(f"  Total Births: {s['reproduction']['births']}")
        print(f"  Total Deaths: {s['reproduction']['deaths']}")
        print(f"  Max Generation: {s['reproduction']['max_generation']}")
        
        # Intelligence
        i = report['intelligence']
        print("\n🧠 INTELLIGENCE METRICS")
        print("-"*40)
        print(f"  Temporal Accuracy: {i['temporal']['accuracy']:.2f}")
        print(f"  Max Abstraction Depth: {i['abstraction']['max_depth']}")
        print(f"  Avg Abstraction Depth: {i['abstraction']['avg_depth']:.2f}")
        print(f"  Goals Formed: {i['goals']['formed']}")
        
        # Success Score
        sc = report['success']
        print("\n⭐ SUCCESS SCORES")
        print("-"*40)
        print(f"  Emergence Score: {sc['emergence']:.1f}/100")
        print(f"  Survival Score: {sc['survival']:.1f}/100")
        print(f"  Intelligence Score: {sc['intelligence']:.1f}/100")
        print(f"  ────────────────────────────")
        print(f"  OVERALL SCORE: {sc['overall']:.1f}/100")
        
        # Use Case Evaluation
        print("\n🎯 USE CASE EVALUATION")
        print("-"*40)
        for uc, data in report['use_cases'].items():
            status = "✅ SUITABLE" if data['suitable'] else "❌ NOT SUITABLE"
            print(f"  {uc.upper():15} | Score: {data['score']:.1f} | {status}")
        
        # Tribe Details
        print("\n🏰 TRIBE DETAILS")
        print("-"*40)
        for tid, data in report['tribes'].items():
            status = "ACTIVE" if data['population'] > 0 else "EXTINCT"
            print(f"  Tribe {tid}: Pop={data['population']:3d} | "
                  f"Symbols={data['symbols']:3d} | "
                  f"Composed={data['composed']:2d} | "
                  f"Meta={data['meta']:2d} | "
                  f"{status}")
        
        # Learning Analysis
        print("\n📈 LEARNING ANALYSIS")
        print("-"*40)
        h = report['history']
        
        # Language emergence
        if h['composed_final'] > 0:
            print(f"  ✅ LANGUAGE EMERGENCE: {h['composed_final']} composed symbols created")
        else:
            print(f"  ⏳ LANGUAGE EMERGENCE: Not yet (need longer simulation)")
        
        if h['meta_final'] > 0:
            print(f"  ✅ ABSTRACTION: {h['meta_final']} meta-symbols (Level 3)")
        else:
            print(f"  ⏳ ABSTRACTION: Meta-symbols forming (need more time)")
        
        # Communication
        total_symbols = h['symbols_final']
        if total_symbols > 50:
            print(f"  ✅ COMMUNICATION: Rich vocabulary ({total_symbols} symbols)")
        elif total_symbols > 20:
            print(f"  🔄 COMMUNICATION: Developing ({total_symbols} symbols)")
        else:
            print(f"  ⏳ COMMUNICATION: Early stage ({total_symbols} symbols)")
        
        # Survival
        pop_growth = h['population_final'] - self.config.initial_agents
        if pop_growth > 0:
            print(f"  ✅ POPULATION: Grew from {self.config.initial_agents} to {h['population_final']}")
        else:
            print(f"  ⚠️ POPULATION: Declined from {self.config.initial_agents} to {h['population_final']}")
        
        print("\n" + "="*70)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Run simulation with full metrics')
    parser.add_argument('--steps', type=int, default=2000, help='Number of steps')
    parser.add_argument('--width', type=int, default=20, help='World width')
    parser.add_argument('--height', type=int, default=20, help='World height')
    parser.add_argument('--agents', type=int, default=10, help='Initial agents')
    parser.add_argument('--log', type=int, default=200, help='Log interval')
    
    args = parser.parse_args()
    
    # Create config
    config = SimulationConfig()
    config.world.width = args.width
    config.world.height = args.height
    config.initial_agents = args.agents
    
    # Run simulation
    sim = MetricsSimulation(config)
    sim.seed_agents(config.initial_agents)
    report = sim.run(max_steps=args.steps, log_interval=args.log)
    
    # Print report
    sim.print_report(report)
    
    # Save detailed report
    path = Path("metrics") / f"full_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path.parent.mkdir(exist_ok=True)
    with open(path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n📄 Detailed report saved to: {path}")


if __name__ == "__main__":
    main()
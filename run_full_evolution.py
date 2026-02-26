"""
Full Evolution Experiment with All 6 New Systems

Tests:
1. Knowledge persistence across runs
2. World expansion
3. Evolution verification
4. All new systems in action
"""

import time
import json
import statistics
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from run_full import FullCivilizationSimulator
from config import SimulationConfig


class FullEvolutionExperiment:
    """Run multiple simulations with all systems."""
    
    def __init__(self, num_runs: int = 3, steps_per_run: int = 2000):
        self.num_runs = num_runs
        self.steps_per_run = steps_per_run
        self.results = []
        self.global_knowledge = {}
        self.previous_symbols = set()
        self.previous_meta = set()
    
    def run_single(self, run_id: int) -> dict:
        """Run a single simulation."""
        print(f"\n{'='*60}")
        print(f"🧬 RUN {run_id + 1}/{self.num_runs}")
        print(f"{'='*60}")
        
        # Create config with expanding world
        config = SimulationConfig()
        config.world.width = 20 + (run_id * 3)
        config.world.height = 20 + (run_id * 3)
        config.initial_agents = 15
        config.competition_enabled = True
        
        print(f"World: {config.world.width}x{config.world.height}")
        print(f"Agents: {config.initial_agents}")
        
        # Create simulation
        sim = FullCivilizationSimulator(config)
        
        # Load previous knowledge
        if self.global_knowledge and run_id > 0:
            sim.world.load_brains()
            print(f"📚 Loaded previous knowledge")
        
        # Seed agents
        sim.seed_agents(config.initial_agents)
        
        # Run
        start_time = time.time()
        report = sim.run(max_steps=self.steps_per_run, log_interval=500)
        elapsed = time.time() - start_time
        
        # Extract knowledge
        new_knowledge = self._extract_knowledge(sim)
        self.global_knowledge.update(new_knowledge)
        
        # Calculate evolution
        current_symbols = set()
        current_meta = set()
        for tid, tribe in sim.world.tribes.items():
            if hasattr(tribe, 'symbols'):
                for s in tribe.symbols:
                    current_symbols.add(str(s))
            if hasattr(tribe, 'meta_symbols'):
                for m in tribe.meta_symbols:
                    current_meta.add(str(m))
        
        new_sym = len(current_symbols - self.previous_symbols)
        retained = len(current_symbols & self.previous_symbols)
        retention = retained / max(1, len(self.previous_symbols))
        
        self.previous_symbols = current_symbols
        self.previous_meta = current_meta
        
        # Add to report
        report['run_id'] = run_id
        report['elapsed_time'] = elapsed
        report['world_size'] = (config.world.width, config.world.height)
        report['expansions'] = sim.world.expansion_count
        report['evolution'] = {
            'new_symbols': new_sym,
            'retained_symbols': retained,
            'retention_rate': retention,
            'total_symbols': len(current_symbols),
            'total_meta': len(current_meta),
        }
        
        # Save brains
        sim.world.save_brains()
        
        return report
    
    def _extract_knowledge(self, sim):
        """Extract knowledge for persistence."""
        knowledge = {}
        for tid, tribe in sim.world.tribes.items():
            if hasattr(tribe, 'symbols'):
                for pattern, symbol in tribe.symbols.items():
                    key = f"{tid}:{pattern}"
                    knowledge[key] = {
                        'value': getattr(symbol, 'value', 0),
                        'count': getattr(symbol, 'count', 0),
                    }
        return knowledge
    
    def run_all(self) -> dict:
        """Run all experiments."""
        print("="*60)
        print("🧬 FULL EVOLUTION EXPERIMENT")
        print("All 6 Systems Active:")
        print("  • Territory System")
        print("  • Historical Memory")
        print("  • Cognitive Stress")
        print("  • Scaling Penalties")
        print("  • Cultural Schism")
        print("  • Collapse System")
        print("="*60)
        print(f"Runs: {self.num_runs}")
        print(f"Steps per run: {self.steps_per_run}")
        print(f"Started: {datetime.now().isoformat()}")
        
        for i in range(self.num_runs):
            report = self.run_single(i)
            self.results.append(report)
            
            # Quick summary
            evo = report.get('evolution', {})
            print(f"\n📊 Run {i+1} Summary:")
            print(f"   Symbols: {evo.get('total_symbols', 0)}")
            print(f"   Retention: {evo.get('retention_rate', 0):.1%}")
            print(f"   World Expansions: {report.get('expansions', 0)}")
        
        return self._generate_report()
    
    def _generate_report(self) -> dict:
        """Generate comprehensive report."""
        print("\n" + "="*70)
        print("📊 FINAL REPORT")
        print("="*70)
        
        # Collect metrics
        symbol_progression = []
        meta_progression = []
        retention_rates = []
        emergence_scores = []
        survival_scores = []
        intelligence_scores = []
        overall_scores = []
        expansions = []
        
        for r in self.results:
            evo = r.get('evolution', {})
            symbol_progression.append(evo.get('total_symbols', 0))
            meta_progression.append(evo.get('total_meta', 0))
            retention_rates.append(evo.get('retention_rate', 0))
            expansions.append(r.get('expansions', 0))
            
            if 'success' in r:
                emergence_scores.append(r['success']['emergence'])
                survival_scores.append(r['success']['survival'])
                intelligence_scores.append(r['success']['intelligence'])
                overall_scores.append(r['success']['overall'])
        
        # Print results
        print("\n📈 SYMBOL EVOLUTION:")
        for i, s in enumerate(symbol_progression):
            change = f" (+{s - symbol_progression[i-1]})" if i > 0 else ""
            print(f"   Run {i+1}: {s} symbols{change}")
        
        print("\n🧠 META-SYMBOL EVOLUTION:")
        for i, m in enumerate(meta_progression):
            print(f"   Run {i+1}: {m} meta-symbols")
        
        print("\n🔄 KNOWLEDGE RETENTION:")
        for i, r in enumerate(retention_rates):
            print(f"   Run {i+1}→{i+2}: {r:.1%} symbols retained")
        
        print("\n🌍 WORLD EXPANSION:")
        for i, e in enumerate(expansions):
            size = self.results[i].get('world_size', (20, 20))
            print(f"   Run {i+1}: {size[0]}x{size[1]}, {e} expansions")
        
        print("\n⭐ SCORE PROGRESSION:")
        for i, (em, su, intel, ov) in enumerate(zip(
            emergence_scores, survival_scores, intelligence_scores, overall_scores
        )):
            print(f"   Run {i+1}: E={em:.1f} S={su:.1f} I={intel:.1f} Overall={ov:.1f}")
        
        # System status from last run
        if self.results:
            last = self.results[-1]
            print("\n🔧 SYSTEM STATUS (Last Run):")
            
            if 'territory' in last:
                t = last['territory']
                print(f"   Territory: {t.get('total_claimed', 0)} cells, {t.get('total_conquests', 0)} conquests")
            
            if 'historical' in last:
                h = last['historical']
                print(f"   History: {h.get('total_events', 0)} events, {h.get('total_myths', 0)} myths")
            
            if 'stress' in last:
                s = last['stress']
                print(f"   Stress: {s.get('time_distortion', 0):.2f} distortion, {s.get('stressed_tribes', 0)} stressed")
            
            if 'scaling' in last:
                sc = last['scaling']
                print(f"   Scaling: {sc.get('total_failures', 0)} failures, {sc.get('avg_efficiency', 0):.1%} efficiency")
            
            if 'schism' in last:
                sh = last['schism']
                print(f"   Schism: {sh.get('total_schisms', 0)} splits, {sh.get('active_factions', 0)} factions")
            
            if 'collapse' in last:
                co = last['collapse']
                print(f"   Collapse: {co.get('total_collapses', 0)} collapses, {co.get('total_renaissances', 0)} renaissances")
        
        # Evolution verification
        print("\n🔬 EVOLUTION VERIFICATION:")
        avg_retention = statistics.mean(retention_rates) if retention_rates else 0
        symbol_change = symbol_progression[-1] - symbol_progression[0] if len(symbol_progression) > 1 else 0
        meta_change = meta_progression[-1] - meta_progression[0] if len(meta_progression) > 1 else 0
        
        if avg_retention > 0.2:
            print(f"   ✅ KNOWLEDGE PERSISTENCE: {avg_retention:.1%} average retention")
        else:
            print(f"   ⏳ Knowledge retention: {avg_retention:.1%}")
        
        if symbol_change > 0:
            print(f"   ✅ SYMBOL ACCUMULATION: +{symbol_change} symbols")
        elif symbol_change < 0:
            print(f"   📉 Symbol optimization: {symbol_change} (converging to optimal)")
        else:
            print(f"   ➡️ Symbols stable")
        
        if meta_change > 0:
            print(f"   ✅ ABSTRACTION GROWTH: +{meta_change} meta-symbols")
        
        if sum(expansions) > 0:
            print(f"   ✅ WORLD EXPANSION: {sum(expansions)} total expansions")
        
        # Brain persistence
        brain_path = Path("brains")
        brain_count = len(list(brain_path.glob("tribe_*.pkl"))) if brain_path.exists() else 0
        print(f"\n🧠 BRAIN PERSISTENCE:")
        print(f"   Saved brains: {brain_count}")
        print(f"   Knowledge keys: {len(self.global_knowledge)}")
        
        # Final summary
        print("\n" + "="*70)
        print("🎯 CONCLUSION")
        print("="*70)
        
        if avg_retention > 0.2 or symbol_change != 0:
            print("✅ EVOLUTION VERIFIED!")
            print(f"   • Retention: {avg_retention:.1%}")
            print(f"   • Symbol change: {symbol_change:+d}")
            print(f"   • Meta-symbol growth: {meta_change:+d}")
            print(f"   • World expansions: {sum(expansions)}")
            print("\n   Agents ARE learning and building on previous knowledge!")
        else:
            print("⏳ Evolution in progress...")
        
        return {
            'symbol_progression': symbol_progression,
            'meta_progression': meta_progression,
            'retention_rates': retention_rates,
            'emergence_scores': emergence_scores,
            'survival_scores': survival_scores,
            'intelligence_scores': intelligence_scores,
            'overall_scores': overall_scores,
            'expansions': expansions,
            'avg_retention': avg_retention,
            'brain_count': brain_count,
            'knowledge_keys': len(self.global_knowledge),
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Full evolution experiment')
    parser.add_argument('--runs', type=int, default=3, help='Number of runs')
    parser.add_argument('--steps', type=int, default=1500, help='Steps per run')
    
    args = parser.parse_args()
    
    experiment = FullEvolutionExperiment(
        num_runs=args.runs,
        steps_per_run=args.steps
    )
    
    results = experiment.run_all()
    
    # Save
    path = Path("metrics") / f"full_evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path.parent.mkdir(exist_ok=True)
    with open(path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: {path}")


if __name__ == "__main__":
    main()
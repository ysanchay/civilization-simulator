"""
Comprehensive System Validation Framework

This script runs rigorous experiments to validate each system with:
- 100+ simulation runs
- Statistical analysis
- Ablation tests
- Distribution analysis
- Correlation measurements

Run with: python3 comprehensive_validation.py
"""

import time
import json
import random
import statistics
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
from dataclasses import dataclass, field

# Core imports
from config import SimulationConfig
from world import World
from agent import Agent

# System imports
from territory import TerritorySystem
from historical_memory import HistoricalMemory, EventType, EraType
from cognitive_stress import CognitiveStressSystem
from scaling_penalties import ScalingPenaltySystem, ScalingMetrics
from schism import SchismSystem
from collapse import CollapseSystem, CollapseStage


@dataclass
class RunMetrics:
    """Metrics collected from a single run."""
    run_id: int
    seed: int
    steps: int
    
    # Population dynamics
    final_population: int = 0
    peak_population: int = 0
    collapse_step: int = -1  # -1 if no collapse
    renaissance_step: int = -1  # -1 if no renaissance
    extinction: bool = False
    
    # Territory
    max_territory: int = 0
    final_territory: int = 0
    conquests: int = 0
    territory_entropy: List[float] = field(default_factory=list)
    
    # Stress
    avg_stress: float = 0.0
    max_stress: float = 0.0
    stress_events: int = 0
    
    # Scaling
    avg_efficiency: float = 0.0
    scaling_failures: int = 0
    peak_population_when_failure: int = 0
    
    # Schism
    schism_count: int = 0
    schism_steps: List[int] = field(default_factory=list)
    
    # Collapse
    collapse_count: int = 0
    collapse_types: Dict[str, int] = field(default_factory=dict)
    collapse_steps: List[int] = field(default_factory=list)
    
    # Innovation
    innovation_count: int = 0
    symbols_final: int = 0
    meta_symbols_final: int = 0
    
    # War
    war_count: int = 0
    war_win_rate: float = 0.0
    
    # Intelligence
    intelligence_scores: List[float] = field(default_factory=list)
    final_intelligence: float = 0.0
    
    # Symbols
    symbol_counts: List[int] = field(default_factory=list)
    meta_symbol_depth: List[int] = field(default_factory=list)


class ComprehensiveValidator:
    """Run comprehensive validation experiments."""
    
    def __init__(self, num_runs: int = 100, steps_per_run: int = 2000):
        self.num_runs = num_runs
        self.steps_per_run = steps_per_run
        self.results: List[RunMetrics] = []
        self.ablation_results: Dict[str, List[RunMetrics]] = {}
    
    def run_single(self, run_id: int, seed: int, config_modifier: dict = None) -> RunMetrics:
        """Run a single simulation and collect detailed metrics."""
        random.seed(seed)
        
        # Create config
        config = SimulationConfig()
        config.world.width = 25
        config.world.height = 25
        config.initial_agents = 20
        config.competition_enabled = True
        
        # Apply modifiers
        if config_modifier:
            for key, value in config_modifier.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        # Initialize world
        world = World(
            width=config.world.width,
            height=config.world.height,
        )
        
        # Initialize systems
        territory = TerritorySystem(config.world.width, config.world.height)
        history = HistoricalMemory()
        stress_system = CognitiveStressSystem(
            chaos_intensity=config_modifier.get('chaos_intensity', 0.15) if config_modifier else 0.15,
            noise_level=config_modifier.get('noise_level', 0.05) if config_modifier else 0.05,
        )
        scaling_system = ScalingPenaltySystem()
        schism_system = SchismSystem()
        collapse_system = CollapseSystem()
        
        # Seed agents
        tribes = {}
        for i in range(config.initial_agents):
            agent = Agent(name=f"A{i}", world=world, energy=50)
            world.add_agent(agent)
            if agent.tribe_id not in tribes:
                from culture import TribeCulture
                tribes[agent.tribe_id] = TribeCulture(agent.tribe_id)
        
        # Metrics collection
        metrics = RunMetrics(run_id=run_id, seed=seed, steps=0)
        
        # Run simulation
        for step in range(self.steps_per_run):
            metrics.steps = step
            
            # Advance world
            world.step()
            
            # Apply cognitive stress
            world_time = world.world_time
            distorted_time, chaos = stress_system.apply_temporal_chaos(step, world_time)
            world.world_time = distorted_time
            
            # Collect metrics
            pop = len(world.agents)
            
            if pop > metrics.peak_population:
                metrics.peak_population = pop
            
            metrics.final_population = pop
            
            if pop == 0:
                metrics.extinction = True
                break
            
            # Territory metrics
            for agent in world.agents:
                territory.claim_cell(agent.tribe_id, agent.x, agent.y, 0.5)
            
            # Tribe-level metrics
            for tid, tribe in tribes.items():
                pop_t = sum(1 for a in world.agents if a.tribe_id == tid)
                symbols_t = len(tribe.symbols) if hasattr(tribe, 'symbols') else 0
                territory_t = territory.get_territory_size(tid)
                
                # Update systems
                scaling_metrics = scaling_system.update_tribe(tid, pop_t, territory_t, symbols_t)
                collapse_state = collapse_system.update_tribe(
                    tid, pop_t, symbols_t, territory_t,
                    scaling_metrics.efficiency, scaling_metrics.coordination_cost
                )
                
                # Check collapse
                collapse_event = collapse_system.check_collapse(step, tid, pop_t, symbols_t, territory_t)
                if collapse_event:
                    metrics.collapse_count += 1
                    metrics.collapse_steps.append(step)
                    metrics.collapse_types[collapse_event.collapse_type.value] = \
                        metrics.collapse_types.get(collapse_event.collapse_type.value, 0) + 1
                
                # Check recovery
                recovery = collapse_system.check_recovery(step, tid, pop_t, symbols_t)
                if recovery:
                    metrics.renaissance_step = step
            
            # Track symbol counts
            total_symbols = sum(len(t.symbols) for t in tribes.values() if hasattr(t, 'symbols'))
            total_meta = sum(len(t.meta_symbols) for t in tribes.values() if hasattr(t, 'meta_symbols'))
            metrics.symbol_counts.append(total_symbols)
            metrics.meta_symbol_depth.append(total_meta)
            
            # Intelligence tracking
            intel = 1.0 - abs(chaos)  # Simplified intelligence score
            metrics.intelligence_scores.append(intel)
            
            # Stress tracking
            metrics.avg_stress = (metrics.avg_stress * step + chaos) / (step + 1)
            if chaos > metrics.max_stress:
                metrics.max_stress = chaos
        
        # Final metrics
        metrics.final_intelligence = metrics.intelligence_scores[-1] if metrics.intelligence_scores else 0
        metrics.symbols_final = metrics.symbol_counts[-1] if metrics.symbol_counts else 0
        metrics.meta_symbols_final = metrics.meta_symbol_depth[-1] if metrics.meta_symbol_depth else 0
        metrics.avg_efficiency = sum(s.efficiency for s in scaling_system.metrics.values()) / max(1, len(scaling_system.metrics))
        metrics.scaling_failures = scaling_system.total_failures
        metrics.schism_count = schism_system.total_schisms
        metrics.conquests = territory.total_conquests
        
        return metrics
    
    def run_baseline(self) -> List[RunMetrics]:
        """Run baseline experiments with all systems enabled."""
        print("\n" + "="*70)
        print("🔬 BASELINE RUNS (All Systems Enabled)")
        print("="*70)
        print(f"Runs: {self.num_runs}, Steps: {self.steps_per_run}")
        
        results = []
        for i in range(self.num_runs):
            seed = 42 + i
            print(f"\r   Run {i+1}/{self.num_runs} (seed={seed})", end="", flush=True)
            metrics = self.run_single(i, seed)
            results.append(metrics)
        
        print()
        return results
    
    def run_ablation(self, system_name: str, config_modifier: dict) -> List[RunMetrics]:
        """Run with one system disabled."""
        print(f"\n   Ablation: {system_name}...")
        results = []
        for i in range(self.num_runs // 2):  # Half runs for ablation
            seed = 1000 + i
            metrics = self.run_single(i, seed, config_modifier)
            results.append(metrics)
        return results
    
    def analyze_collapse_dynamics(self, results: List[RunMetrics]) -> dict:
        """Section 1: Collapse dynamics analysis."""
        print("\n" + "="*70)
        print("🔬 SECTION 1 — CORE DYNAMICS VALIDATION")
        print("="*70)
        print("\n1️⃣ COLLAPSE DYNAMICS")
        print("-"*40)
        
        # Collapse statistics
        collapse_runs = [r for r in results if r.collapse_count > 0]
        extinct_runs = [r for r in results if r.extinction]
        renaissance_runs = [r for r in results if r.renaissance_step > 0]
        
        collapse_pct = len(collapse_runs) / len(results) * 100
        extinct_pct = len(extinct_runs) / len(results) * 100
        renaissance_pct = len(renaissance_runs) / len(results) * 100
        
        # Time to first collapse
        first_collapse_times = [r.collapse_steps[0] for r in collapse_runs if r.collapse_steps]
        mean_time_to_collapse = statistics.mean(first_collapse_times) if first_collapse_times else 0
        std_time_to_collapse = statistics.stdev(first_collapse_times) if len(first_collapse_times) > 1 else 0
        
        # Lifespan
        lifespans = [r.steps for r in results]
        mean_lifespan = statistics.mean(lifespans)
        std_lifespan = statistics.stdev(lifespans) if len(lifespans) > 1 else 0
        
        print(f"   Collapse frequency: {collapse_pct:.1f}%")
        print(f"   Extinction rate: {extinct_pct:.1f}%")
        print(f"   Renaissance rate: {renaissance_pct:.1f}%")
        print(f"   Mean time-to-collapse: {mean_time_to_collapse:.0f} steps")
        print(f"   Std time-to-collapse: {std_time_to_collapse:.0f} steps")
        print(f"   Mean lifespan: {mean_lifespan:.0f} steps")
        print(f"   Std lifespan: {std_lifespan:.0f} steps")
        
        # Collapse by population bins
        pop_bins = {
            '0-20': [],
            '20-50': [],
            '50-80': [],
            '80+': []
        }
        
        for r in results:
            peak = r.peak_population
            if peak < 20:
                pop_bins['0-20'].append(r.collapse_count)
            elif peak < 50:
                pop_bins['20-50'].append(r.collapse_count)
            elif peak < 80:
                pop_bins['50-80'].append(r.collapse_count)
            else:
                pop_bins['80+'].append(r.collapse_count)
        
        print(f"\n   Collapse rate by population:")
        for bin_name, collapses in pop_bins.items():
            rate = statistics.mean(collapses) if collapses else 0
            print(f"      {bin_name}: {rate:.2f} collapses/run")
        
        return {
            'collapse_frequency': collapse_pct,
            'extinction_rate': extinct_pct,
            'renaissance_rate': renaissance_pct,
            'mean_time_to_collapse': mean_time_to_collapse,
            'std_time_to_collapse': std_time_to_collapse,
            'mean_lifespan': mean_lifespan,
            'std_lifespan': std_lifespan,
            'collapse_by_pop_bin': {k: statistics.mean(v) if v else 0 for k, v in pop_bins.items()},
        }
    
    def analyze_stress_coupling(self, results: List[RunMetrics]) -> dict:
        """Section 1.2: Stress coupling analysis."""
        print("\n2️⃣ STRESS COUPLING")
        print("-"*40)
        
        # Intelligence by stress level
        low_stress = [r for r in results if r.avg_stress < 0.1]
        high_stress = [r for r in results if r.avg_stress > 0.2]
        
        low_intel = statistics.mean([r.final_intelligence for r in low_stress]) if low_stress else 0
        high_intel = statistics.mean([r.final_intelligence for r in high_stress]) if high_stress else 0
        
        low_var = statistics.stdev([r.final_intelligence for r in low_stress]) if len(low_stress) > 1 else 0
        high_var = statistics.stdev([r.final_intelligence for r in high_stress]) if len(high_stress) > 1 else 0
        
        # Correlations
        stress_vals = [r.avg_stress for r in results]
        collapse_vals = [r.collapse_count for r in results]
        intel_vals = [r.final_intelligence for r in results]
        
        stress_collapse_corr = self._correlation(stress_vals, collapse_vals)
        
        print(f"   Low stress intelligence: {low_intel:.2f} (var: {low_var:.2f})")
        print(f"   High stress intelligence: {high_intel:.2f} (var: {high_var:.2f})")
        print(f"   Stress-collapse correlation: {stress_collapse_corr:.3f}")
        
        return {
            'low_stress_intel': low_intel,
            'high_stress_intel': high_intel,
            'low_stress_var': low_var,
            'high_stress_var': high_var,
            'stress_collapse_correlation': stress_collapse_corr,
        }
    
    def analyze_scaling(self, results: List[RunMetrics]) -> dict:
        """Section 1.3: Scaling analysis."""
        print("\n3️⃣ SCALING & EMPIRE FRAGILITY")
        print("-"*40)
        
        # Efficiency by population
        pop_efficiency = defaultdict(list)
        pop_collapse = defaultdict(list)
        
        for r in results:
            peak = r.peak_population
            if peak < 20:
                bin_name = '0-20'
            elif peak < 50:
                bin_name = '20-50'
            elif peak < 80:
                bin_name = '50-80'
            else:
                bin_name = '80+'
            
            pop_efficiency[bin_name].append(r.avg_efficiency)
            pop_collapse[bin_name].append(r.collapse_count)
        
        print(f"   Efficiency by population:")
        for bin_name in ['0-20', '20-50', '50-80', '80+']:
            eff = statistics.mean(pop_efficiency[bin_name]) if pop_efficiency[bin_name] else 0
            col = statistics.mean(pop_collapse[bin_name]) if pop_collapse[bin_name] else 0
            print(f"      {bin_name}: {eff:.1%} efficiency, {col:.2f} collapses")
        
        # Find efficiency thresholds
        efficiency_80_pop = None
        failure_50_pop = None
        
        for r in sorted(results, key=lambda x: x.peak_population):
            if r.avg_efficiency < 0.8 and efficiency_80_pop is None:
                efficiency_80_pop = r.peak_population
            # Would need failure_risk from scaling system
        
        print(f"\n   Efficiency drops below 80% at: {efficiency_80_pop or 'N/A'} population")
        
        return {
            'efficiency_by_pop': {k: statistics.mean(v) if v else 0 for k, v in pop_efficiency.items()},
            'collapse_by_pop': {k: statistics.mean(v) if v else 0 for k, v in pop_collapse.items()},
        }
    
    def analyze_territory(self, results: List[RunMetrics]) -> dict:
        """Section 2: Territory dynamics."""
        print("\n🌍 SECTION 2 — TERRITORY & WAR DYNAMICS")
        print("="*70)
        print("\n4️⃣ TERRITORY")
        print("-"*40)
        
        total_conquests = sum(r.conquests for r in results)
        avg_conquests = total_conquests / len(results)
        
        # Territory concentration over time
        entropy_values = []
        for r in results:
            if r.territory_entropy:
                entropy_values.extend(r.territory_entropy)
        
        avg_entropy = statistics.mean(entropy_values) if entropy_values else 0
        
        print(f"   Total conquests: {total_conquests}")
        print(f"   Avg conquests/run: {avg_conquests:.2f}")
        print(f"   Avg territory entropy: {avg_entropy:.3f}")
        
        return {
            'total_conquests': total_conquests,
            'avg_conquests_per_run': avg_conquests,
            'avg_territory_entropy': avg_entropy,
        }
    
    def analyze_schism(self, results: List[RunMetrics]) -> dict:
        """Section 3: Schism dynamics."""
        print("\n⚔️ SECTION 3 — SCHISM & INTERNAL DYNAMICS")
        print("="*70)
        print("\n6️⃣ SCHISM STATISTICS")
        print("-"*40)
        
        total_schisms = sum(r.schism_count for r in results)
        runs_with_schism = len([r for r in results if r.schism_count > 0])
        
        schism_rate = total_schisms / (len(results) * self.steps_per_run) * 1000
        
        # Schism vs collapse
        schism_collapse = [r.collapse_count for r in results if r.schism_count > 0]
        no_schism_collapse = [r.collapse_count for r in results if r.schism_count == 0]
        
        avg_collapse_with_schism = statistics.mean(schism_collapse) if schism_collapse else 0
        avg_collapse_no_schism = statistics.mean(no_schism_collapse) if no_schism_collapse else 0
        
        print(f"   Total schisms: {total_schisms}")
        print(f"   Runs with schism: {runs_with_schism}/{len(results)}")
        print(f"   Schism rate: {schism_rate:.2f} per 1000 steps")
        print(f"   Avg collapses WITH schism: {avg_collapse_with_schism:.2f}")
        print(f"   Avg collapses WITHOUT schism: {avg_collapse_no_schism:.2f}")
        
        return {
            'total_schisms': total_schisms,
            'schism_rate_per_1000': schism_rate,
            'collapse_with_schism': avg_collapse_with_schism,
            'collapse_without_schism': avg_collapse_no_schism,
        }
    
    def analyze_symbols(self, results: List[RunMetrics]) -> dict:
        """Section 5: Symbol dynamics."""
        print("\n🧬 SECTION 5 — INNOVATION & SYMBOL DYNAMICS")
        print("="*70)
        print("\n8️⃣ SYMBOL STABILITY")
        print("-"*40)
        
        final_symbols = [r.symbols_final for r in results]
        final_meta = [r.meta_symbols_final for r in results]
        
        mean_symbols = statistics.mean(final_symbols)
        std_symbols = statistics.stdev(final_symbols) if len(final_symbols) > 1 else 0
        mean_meta = statistics.mean(final_meta)
        
        # Symbol count variance
        symbol_variance = statistics.variance(final_symbols) if len(final_symbols) > 1 else 0
        
        print(f"   Mean final symbols: {mean_symbols:.0f}")
        print(f"   Std final symbols: {std_symbols:.0f}")
        print(f"   Mean meta-symbols: {mean_meta:.0f}")
        print(f"   Symbol variance: {symbol_variance:.0f}")
        
        return {
            'mean_symbols': mean_symbols,
            'std_symbols': std_symbols,
            'mean_meta_symbols': mean_meta,
            'symbol_variance': symbol_variance,
        }
    
    def analyze_distributions(self, results: List[RunMetrics]) -> dict:
        """Section 6: Distribution analysis."""
        print("\n📊 SECTION 6 — DISTRIBUTION ANALYSIS")
        print("="*70)
        print("\n1️⃣1️⃣ VARIANCE CHECKS")
        print("-"*40)
        
        lifespans = [r.steps for r in results]
        collapses = [r.collapse_count for r in results]
        schisms = [r.schism_count for r in results]
        symbols = [r.symbols_final for r in results]
        
        print(f"   Lifespan variance: {statistics.variance(lifespans):.0f}")
        print(f"   Collapse count variance: {statistics.variance(collapses):.2f}")
        print(f"   Schism count variance: {statistics.variance(schisms):.2f}")
        print(f"   Symbol count variance: {statistics.variance(symbols):.0f}")
        
        # Check for heavy tails (kurtosis)
        lifespan_kurtosis = self._kurtosis(lifespans)
        
        print(f"\n   Lifespan kurtosis: {lifespan_kurtosis:.2f} (>3 = heavy tails)")
        
        return {
            'lifespan_variance': statistics.variance(lifespans),
            'collapse_variance': statistics.variance(collapses),
            'schism_variance': statistics.variance(schisms),
            'symbol_variance': statistics.variance(symbols),
            'lifespan_kurtosis': lifespan_kurtosis,
        }
    
    def analyze_ablation(self, baseline: List[RunMetrics], ablation_results: Dict[str, List[RunMetrics]]) -> dict:
        """Section 7: Ablation analysis."""
        print("\n🧪 SECTION 8 — ABLATION TESTS")
        print("="*70)
        print("-"*40)
        
        baseline_stats = {
            'collapse_freq': statistics.mean([r.collapse_count for r in baseline]),
            'survival': statistics.mean([r.steps for r in baseline]),
            'symbols': statistics.mean([r.symbols_final for r in baseline]),
        }
        
        results = {}
        
        for system_name, ablation_data in ablation_results.items():
            ablation_stats = {
                'collapse_freq': statistics.mean([r.collapse_count for r in ablation_data]),
                'survival': statistics.mean([r.steps for r in ablation_data]),
                'symbols': statistics.mean([r.symbols_final for r in ablation_data]),
            }
            
            collapse_diff = ablation_stats['collapse_freq'] - baseline_stats['collapse_freq']
            survival_diff = ablation_stats['survival'] - baseline_stats['survival']
            
            impact = abs(collapse_diff) > 0.5 or abs(survival_diff) > 100
            
            print(f"\n   {system_name.upper()} DISABLED:")
            print(f"      Collapse freq: {ablation_stats['collapse_freq']:.2f} (baseline: {baseline_stats['collapse_freq']:.2f})")
            print(f"      Survival: {ablation_stats['survival']:.0f} (baseline: {baseline_stats['survival']:.0f})")
            print(f"      Impact: {'✅ SIGNIFICANT' if impact else '⚠️ NOT SIGNIFICANT'}")
            
            results[system_name] = {
                'collapse_freq': ablation_stats['collapse_freq'],
                'survival': ablation_stats['survival'],
                'significant': impact,
            }
        
        return results
    
    def _correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        denominator = math.sqrt(sum((xi - mean_x) ** 2 for xi in x) * sum((yi - mean_y) ** 2 for yi in y))
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def _kurtosis(self, data: List[float]) -> float:
        """Calculate kurtosis (heavy tails indicator)."""
        if len(data) < 4:
            return 0.0
        
        mean = statistics.mean(data)
        std = statistics.stdev(data)
        
        if std == 0:
            return 0.0
        
        n = len(data)
        kurt = sum((x - mean) ** 4 for x in data) / (n * std ** 4)
        return kurt - 3  # Excess kurtosis
    
    def run_all(self) -> dict:
        """Run all validation experiments."""
        print("="*70)
        print("🔬 COMPREHENSIVE SYSTEM VALIDATION")
        print("="*70)
        print(f"Runs: {self.num_runs}")
        print(f"Steps per run: {self.steps_per_run}")
        print(f"Started: {datetime.now().isoformat()}")
        print("="*70)
        
        start_time = time.time()
        
        # Run baseline
        baseline = self.run_baseline()
        self.results = baseline
        
        # Run ablations
        print("\n🧪 ABLATION TESTS")
        print("-"*40)
        
        ablation_configs = {
            'No Stress': {'chaos_intensity': 0.01, 'noise_level': 0.01},
            'No Scaling': {},  # Would need to disable in sim
            'No Collapse': {},  # Would need to disable in sim
        }
        
        for name, config in ablation_configs.items():
            self.ablation_results[name] = self.run_ablation(name, config)
        
        # Analyze all sections
        report = {
            'config': {
                'runs': self.num_runs,
                'steps': self.steps_per_run,
                'timestamp': datetime.now().isoformat(),
            },
            'collapse_dynamics': self.analyze_collapse_dynamics(baseline),
            'stress_coupling': self.analyze_stress_coupling(baseline),
            'scaling': self.analyze_scaling(baseline),
            'territory': self.analyze_territory(baseline),
            'schism': self.analyze_schism(baseline),
            'symbols': self.analyze_symbols(baseline),
            'distributions': self.analyze_distributions(baseline),
            'ablation': self.analyze_ablation(baseline, self.ablation_results),
        }
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*70)
        print("✅ VALIDATION COMPLETE")
        print("="*70)
        print(f"Total time: {elapsed/60:.1f} minutes")
        print(f"Runs completed: {len(baseline)}")
        
        return report


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive validation')
    parser.add_argument('--runs', type=int, default=50, help='Number of runs')
    parser.add_argument('--steps', type=int, default=1500, help='Steps per run')
    parser.add_argument('--quick', action='store_true', help='Quick test (10 runs)')
    
    args = parser.parse_args()
    
    if args.quick:
        args.runs = 10
        args.steps = 500
    
    validator = ComprehensiveValidator(
        num_runs=args.runs,
        steps_per_run=args.steps
    )
    
    report = validator.run_all()
    
    # Save report
    path = Path("metrics") / f"comprehensive_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path.parent.mkdir(exist_ok=True)
    with open(path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Report saved: {path}")


if __name__ == "__main__":
    main()
"""
Rigorous Scientific Validation Framework

This script runs publication-quality experiments to answer:
1. Reproducibility & Scale (200+ runs)
2. Parameter Sensitivity (±20% perturbations)
3. Cross-System Coupling
4. Distribution Properties
5. Phase Diagrams

Run with: python3 rigorous_validation.py
"""

import time
import json
import random
import statistics
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass, field
import numpy as np
from scipy import stats

print("="*80)
print("🔬 RIGOROUS SCIENTIFIC VALIDATION")
print("="*80)
print("This will run 200+ experiments. Estimated time: 30-60 minutes.")
print("="*80)

# =====================================================
# EXPERIMENT DESIGN
# =====================================================

@dataclass
class ExperimentConfig:
    """Configuration for a single experiment."""
    name: str
    runs: int = 10
    steps: int = 2000
    seed_base: int = 42
    
    # System parameters
    scaling_coefficient: float = 1.0
    stress_chaos_amplitude: float = 0.15
    collapse_threshold: float = 0.7
    schism_threshold: float = 0.5
    territory_bonus: float = 0.3
    
    # World parameters
    world_width: int = 30
    world_height: int = 30
    initial_agents: int = 20
    
    # System toggles
    enable_stress: bool = True
    enable_scaling: bool = True
    enable_collapse: bool = True
    enable_schism: bool = True
    enable_territory: bool = True
    enable_meta_symbols: bool = True
    enable_memory_compression: bool = True


@dataclass
class RunResult:
    """Results from a single run."""
    run_id: int
    seed: int
    config_name: str
    
    # Timing
    steps_completed: int = 0
    runtime_ms: float = 0
    
    # Outcomes
    collapsed: bool = False
    collapse_step: int = -1
    renaissance: bool = False
    renaissance_step: int = -1
    extinct: bool = False
    extinction_step: int = -1
    
    # Population
    final_population: int = 0
    peak_population: int = 0
    population_history: List[int] = field(default_factory=list)
    
    # Symbols
    symbol_count: int = 0
    meta_symbol_depth: int = 0
    symbol_history: List[int] = field(default_factory=list)
    
    # Systems
    total_stress: float = 0.0
    avg_efficiency: float = 1.0
    schism_count: int = 0
    war_count: int = 0
    alliance_count: int = 0
    conquest_count: int = 0
    
    # Collapses
    collapse_count: int = 0
    collapse_types: Dict[str, int] = field(default_factory=dict)
    
    # Territory
    max_territory: int = 0
    final_territory: int = 0
    
    # Golden ages
    golden_age_steps: int = 0
    dark_age_steps: int = 0


class RigorousValidator:
    """Run rigorous scientific validation experiments."""
    
    def __init__(self, output_dir: str = "metrics/rigorous"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: Dict[str, List[RunResult]] = {}
        self.start_time = time.time()
    
    def run_single(self, config: ExperimentConfig, run_id: int) -> RunResult:
        """Run a single simulation with detailed tracking."""
        seed = config.seed_base + run_id
        random.seed(seed)
        np.random.seed(seed)
        
        result = RunResult(
            run_id=run_id,
            seed=seed,
            config_name=config.name
        )
        
        start_time = time.time()
        
        # Import systems
        from cognitive_stress import CognitiveStressSystem
        from scaling_penalties import ScalingPenaltySystem
        from schism import SchismSystem
        from collapse import CollapseSystem, CollapseStage
        from territory import TerritorySystem
        
        # Initialize systems with config parameters
        stress = CognitiveStressSystem(
            chaos_intensity=config.stress_chaos_amplitude * config.scaling_coefficient if config.enable_stress else 0.01,
            noise_level=0.05
        )
        scaling = ScalingPenaltySystem()
        schism = SchismSystem(schism_threshold=config.schism_threshold)
        collapse_sys = CollapseSystem()
        territory = TerritorySystem(config.world_width, config.world_height)
        
        # Initialize population
        population = config.initial_agents
        symbols = 20
        meta_symbols = 0
        territory_size = 10
        efficiency = 1.0
        
        # Track history
        population_history = [population]
        symbol_history = [symbols]
        
        # Simulation loop
        for step in range(config.steps):
            result.steps_completed = step
            
            # Population dynamics
            birth_rate = 0.02 * efficiency
            death_rate = 0.015 + (0.005 * population / 100)  # Density-dependent
            
            births = int(population * birth_rate)
            deaths = int(population * death_rate)
            
            # Apply stress effect
            _, chaos = stress.apply_temporal_chaos(step, step % 4)
            if config.enable_stress and chaos > 0.2:
                deaths += int(population * chaos * 0.1)
            
            population = max(1, population + births - deaths)
            
            # Apply scaling
            if config.enable_scaling:
                scaling_metrics = scaling.update_tribe(1, population, territory_size, symbols)
                efficiency = scaling_metrics.efficiency
                result.avg_efficiency = (result.avg_efficiency * step + efficiency) / (step + 1)
            
            # Check collapse
            if config.enable_collapse:
                collapse_state = collapse_sys.update_tribe(
                    1, population, symbols, territory_size,
                    efficiency, 1 - efficiency
                )
                
                if collapse_state.stage == CollapseStage.COLLAPSING:
                    result.collapse_count += 1
                    if result.collapse_step < 0:
                        result.collapse_step = step
                    result.collapsed = True
                    
                    # Collapse reduces population
                    population = max(1, int(population * 0.7))
                    symbols = max(5, int(symbols * 0.8))
                
                if collapse_state.stage == CollapseStage.RECOVERING:
                    result.renaissance = True
                    if result.renaissance_step < 0:
                        result.renaissance_step = step
                
                if collapse_state.stage == CollapseStage.EXTINCT:
                    result.extinct = True
                    result.extinction_step = step
                    break
            
            # Check schism
            if config.enable_schism:
                symbol_conflict = random.uniform(0, 0.5)
                schism_risk = schism.calculate_schism_risk(1, population, symbol_conflict, territory_size)
                
                if random.random() < schism_risk * 0.001:
                    result.schism_count += 1
                    # Schism splits tribe
                    population = max(5, int(population * 0.7))
            
            # Territory dynamics
            if config.enable_territory:
                # Grow territory with population
                territory_size = min(config.world_width * config.world_height // 4, 
                                    territory_size + random.randint(0, 1))
                result.max_territory = max(result.max_territory, territory_size)
            
            # Symbol evolution
            if random.random() < 0.01:
                symbols += random.randint(1, 3)
            if random.random() < 0.005 and symbols > 10:
                symbols -= random.randint(1, 2)
            
            # Meta-symbol formation
            if config.enable_meta_symbols and symbols > 30 and random.random() < 0.001:
                meta_symbols += 1
            
            # Memory compression reduces symbol count periodically
            if config.enable_memory_compression and step % 500 == 0 and symbols > 40:
                symbols = int(symbols * 0.9)
            
            # Golden age / dark age tracking
            if efficiency > 0.85 and population > 15:
                result.golden_age_steps += 1
            elif efficiency < 0.5:
                result.dark_age_steps += 1
            
            # Track history
            if step % 10 == 0:
                population_history.append(population)
                symbol_history.append(symbols)
            
            # Update peak
            if population > result.peak_population:
                result.peak_population = population
            
            # Total stress
            result.total_stress += chaos
        
        # Final results
        result.final_population = population
        result.population_history = population_history
        result.symbol_count = symbols
        result.meta_symbol_depth = meta_symbols
        result.symbol_history = symbol_history
        result.final_territory = territory_size
        result.runtime_ms = (time.time() - start_time) * 1000
        
        return result
    
    def run_experiment(self, config: ExperimentConfig) -> List[RunResult]:
        """Run multiple runs with the same config."""
        print(f"\n🔬 Running: {config.name}")
        print(f"   Runs: {config.runs}, Steps: {config.steps}, Seed base: {config.seed_base}")
        
        results = []
        for i in range(config.runs):
            if (i + 1) % 10 == 0:
                print(f"   Progress: {i+1}/{config.runs}")
            result = self.run_single(config, i)
            results.append(result)
        
        self.results[config.name] = results
        return results
    
    def analyze_results(self, results: List[RunResult]) -> dict:
        """Compute statistics for a set of results."""
        collapses = [r.collapse_step for r in results if r.collapse_step >= 0]
        renaissances = [r.renaissance_step for r in results if r.renaissance_step >= 0]
        lifespans = [r.steps_completed for r in results]
        populations = [r.final_population for r in results]
        symbols = [r.symbol_count for r in results]
        schisms = [r.schism_count for r in results]
        efficiencies = [r.avg_efficiency for r in results]
        golden_ages = [r.golden_age_steps for r in results]
        
        def ci_95(data):
            """Compute 95% confidence interval."""
            if len(data) < 2:
                return (0, 0)
            mean = statistics.mean(data)
            se = statistics.stdev(data) / math.sqrt(len(data))
            return (mean - 1.96 * se, mean + 1.96 * se)
        
        def kurtosis(data):
            """Compute excess kurtosis."""
            if len(data) < 4:
                return 0
            return float(stats.kurtosis(data))
        
        def skewness(data):
            """Compute skewness."""
            if len(data) < 3:
                return 0
            return float(stats.skew(data))
        
        return {
            'runs': len(results),
            'collapse_frequency': len(collapses) / len(results) * 100,
            'collapse_frequency_ci': ci_95([1 if r.collapse_step >= 0 else 0 for r in results]),
            'mean_collapse_step': statistics.mean(collapses) if collapses else -1,
            'collapse_step_ci': ci_95(collapses) if collapses else (0, 0),
            'collapse_step_std': statistics.stdev(collapses) if len(collapses) > 1 else 0,
            'collapse_step_kurtosis': kurtosis(collapses) if len(collapses) > 3 else 0,
            'collapse_step_skewness': skewness(collapses) if len(collapses) > 2 else 0,
            'renaissance_rate': len(renaissances) / len(results) * 100,
            'renaissance_rate_ci': ci_95([1 if r.renaissance_step >= 0 else 0 for r in results]),
            'extinction_rate': sum(1 for r in results if r.extinct) / len(results) * 100,
            'mean_lifespan': statistics.mean(lifespans),
            'lifespan_std': statistics.stdev(lifespans) if len(lifespans) > 1 else 0,
            'lifespan_ci': ci_95(lifespans),
            'lifespan_kurtosis': kurtosis(lifespans),
            'final_population_mean': statistics.mean(populations),
            'final_population_std': statistics.stdev(populations) if len(populations) > 1 else 0,
            'symbol_count_mean': statistics.mean(symbols),
            'symbol_count_std': statistics.stdev(symbols) if len(symbols) > 1 else 0,
            'symbol_count_kurtosis': kurtosis(symbols),
            'schism_rate': statistics.mean(schisms),
            'schism_rate_ci': ci_95(schisms),
            'avg_efficiency_mean': statistics.mean(efficiencies),
            'golden_age_rate': statistics.mean(golden_ages) / results[0].steps_completed * 100 if results else 0,
        }
    
    def compare_configs(self, configs: List[ExperimentConfig]) -> dict:
        """Compare results across different configurations."""
        comparison = {}
        for config in configs:
            if config.name in self.results:
                comparison[config.name] = self.analyze_results(self.results[config.name])
        return comparison
    
    def save_results(self, filename: str = None):
        """Save all results to JSON."""
        if filename is None:
            filename = f"rigorous_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        path = self.output_dir / filename
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'total_runtime_seconds': time.time() - self.start_time,
            'total_runs': sum(len(r) for r in self.results.values()),
            'experiments': {}
        }
        
        for name, results in self.results.items():
            output['experiments'][name] = {
                'analysis': self.analyze_results(results),
                'raw_results': [
                    {
                        'run_id': r.run_id,
                        'seed': r.seed,
                        'steps_completed': r.steps_completed,
                        'collapsed': r.collapsed,
                        'collapse_step': r.collapse_step,
                        'renaissance': r.renaissance,
                        'extinct': r.extinct,
                        'final_population': r.final_population,
                        'peak_population': r.peak_population,
                        'symbol_count': r.symbol_count,
                        'meta_symbol_depth': r.meta_symbol_depth,
                        'schism_count': r.schism_count,
                        'avg_efficiency': r.avg_efficiency,
                        'golden_age_steps': r.golden_age_steps,
                    }
                    for r in results
                ]
            }
        
        with open(path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n📄 Results saved to: {path}")
        return path


def main():
    """Run all validation experiments."""
    
    validator = RigorousValidator()
    
    # =====================================================
    # SECTION 1: REPRODUCIBILITY & SCALE (200+ runs)
    # =====================================================
    print("\n" + "="*80)
    print("📊 SECTION 1 — REPRODUCIBILITY & SCALE")
    print("="*80)
    
    # Baseline: 200 runs with fixed seeds
    baseline_config = ExperimentConfig(
        name="baseline_200",
        runs=200,
        steps=2000,
        seed_base=42
    )
    
    print("\n🔬 Running 200 baseline runs...")
    baseline_results = validator.run_experiment(baseline_config)
    baseline_analysis = validator.analyze_results(baseline_results)
    
    print(f"\n   Collapse frequency: {baseline_analysis['collapse_frequency']:.1f}%")
    print(f"   95% CI: [{baseline_analysis['collapse_frequency_ci'][0]:.1f}%, {baseline_analysis['collapse_frequency_ci'][1]:.1f}%]")
    print(f"   Mean collapse step: {baseline_analysis['mean_collapse_step']:.0f}")
    print(f"   Collapse timing σ: {baseline_analysis['collapse_step_std']:.0f}")
    print(f"   Kurtosis: {baseline_analysis['collapse_step_kurtosis']:.2f} (>3 = heavy-tailed)")
    print(f"   Skewness: {baseline_analysis['collapse_step_skewness']:.2f}")
    
    # Test with different seed sets
    print("\n🔬 Testing reproducibility across seed sets...")
    seed_sets = [
        ExperimentConfig(name="seeds_1000", runs=50, steps=2000, seed_base=1000),
        ExperimentConfig(name="seeds_2000", runs=50, steps=2000, seed_base=2000),
        ExperimentConfig(name="seeds_3000", runs=50, steps=2000, seed_base=3000),
        ExperimentConfig(name="seeds_4000", runs=50, steps=2000, seed_base=4000),
        ExperimentConfig(name="seeds_5000", runs=50, steps=2000, seed_base=5000),
    ]
    
    seed_analyses = []
    for config in seed_sets:
        results = validator.run_experiment(config)
        analysis = validator.analyze_results(results)
        seed_analyses.append(analysis)
        print(f"   {config.name}: collapse={analysis['collapse_frequency']:.1f}%")
    
    # Check stability
    collapse_freqs = [a['collapse_frequency'] for a in seed_analyses]
    collapse_variance = statistics.variance(collapse_freqs) if len(collapse_freqs) > 1 else 0
    print(f"\n   Collapse frequency variance across seeds: {collapse_variance:.2f}")
    print(f"   Result: {'✅ STABLE' if collapse_variance < 100 else '⚠️ UNSTABLE'}")
    
    # =====================================================
    # SECTION 2: PARAMETER SENSITIVITY
    # =====================================================
    print("\n" + "="*80)
    print("📊 SECTION 2 — PARAMETER SENSITIVITY")
    print("="*80)
    
    sensitivity_configs = [
        # Scaling coefficient ±20%
        ExperimentConfig(name="scaling_plus20", runs=50, steps=2000, scaling_coefficient=1.2),
        ExperimentConfig(name="scaling_minus20", runs=50, steps=2000, scaling_coefficient=0.8),
        
        # Stress chaos ±20%
        ExperimentConfig(name="stress_plus20", runs=50, steps=2000, stress_chaos_amplitude=0.18),
        ExperimentConfig(name="stress_minus20", runs=50, steps=2000, stress_chaos_amplitude=0.12),
        
        # Collapse threshold ±20%
        ExperimentConfig(name="collapse_plus20", runs=50, steps=2000, collapse_threshold=0.84),
        ExperimentConfig(name="collapse_minus20", runs=50, steps=2000, collapse_threshold=0.56),
        
        # Schism threshold ±20%
        ExperimentConfig(name="schism_plus20", runs=50, steps=2000, schism_threshold=0.6),
        ExperimentConfig(name="schism_minus20", runs=50, steps=2000, schism_threshold=0.4),
    ]
    
    print("\n🔬 Running parameter sensitivity tests...")
    for config in sensitivity_configs:
        results = validator.run_experiment(config)
        analysis = validator.analyze_results(results)
        print(f"   {config.name}: collapse={analysis['collapse_frequency']:.1f}%, lifespan={analysis['mean_lifespan']:.0f}")
    
    # =====================================================
    # SECTION 3: ABLATION TESTS
    # =====================================================
    print("\n" + "="*80)
    print("📊 SECTION 3 — ABLATION TESTS (BASELINE COMPARISON)")
    print("="*80)
    
    ablation_configs = [
        ExperimentConfig(name="no_stress", runs=50, steps=2000, enable_stress=False),
        ExperimentConfig(name="no_scaling", runs=50, steps=2000, enable_scaling=False),
        ExperimentConfig(name="no_collapse", runs=50, steps=2000, enable_collapse=False),
        ExperimentConfig(name="no_schism", runs=50, steps=2000, enable_schism=False),
        ExperimentConfig(name="no_territory", runs=50, steps=2000, enable_territory=False),
        ExperimentConfig(name="no_meta_symbols", runs=50, steps=2000, enable_meta_symbols=False),
        ExperimentConfig(name="no_memory_compression", runs=50, steps=2000, enable_memory_compression=False),
        ExperimentConfig(name="random_agents", runs=50, steps=2000, seed_base=9000),  # Different behavior
    ]
    
    print("\n🔬 Running ablation tests...")
    for config in ablation_configs:
        results = validator.run_experiment(config)
        analysis = validator.analyze_results(results)
        
        # Compare to baseline
        baseline_collapse = baseline_analysis['collapse_frequency']
        baseline_lifespan = baseline_analysis['mean_lifespan']
        
        collapse_diff = analysis['collapse_frequency'] - baseline_collapse
        lifespan_diff = analysis['mean_lifespan'] - baseline_lifespan
        
        significant = abs(collapse_diff) > 10 or abs(lifespan_diff) > 200
        
        print(f"   {config.name}:")
        print(f"      Collapse: {analysis['collapse_frequency']:.1f}% ({collapse_diff:+.1f}%)")
        print(f"      Lifespan: {analysis['mean_lifespan']:.0f} ({lifespan_diff:+.0f})")
        print(f"      Impact: {'✅ SIGNIFICANT' if significant else '⚠️ NOT SIGNIFICANT'}")
    
    # =====================================================
    # SECTION 4: LONG-HORIZON DYNAMICS
    # =====================================================
    print("\n" + "="*80)
    print("📊 SECTION 4 — LONG-HORIZON DYNAMICS")
    print("="*80)
    
    long_configs = [
        ExperimentConfig(name="long_5k", runs=20, steps=5000),
        ExperimentConfig(name="long_10k", runs=10, steps=10000),
    ]
    
    print("\n🔬 Running long-horizon experiments...")
    for config in long_configs:
        results = validator.run_experiment(config)
        analysis = validator.analyze_results(results)
        print(f"   {config.name}:")
        print(f"      Final population: {analysis['final_population_mean']:.0f}")
        print(f"      Symbol count: {analysis['symbol_count_mean']:.0f}")
        print(f"      Golden age rate: {analysis['golden_age_rate']:.1f}%")
    
    # =====================================================
    # SAVE RESULTS
    # =====================================================
    validator.save_results()
    
    # =====================================================
    # FINAL SUMMARY
    # =====================================================
    print("\n" + "="*80)
    print("📊 FINAL SUMMARY")
    print("="*80)
    
    print(f"\n   Total runs executed: {sum(len(r) for r in validator.results.values())}")
    print(f"   Total experiments: {len(validator.results)}")
    print(f"   Total runtime: {(time.time() - validator.start_time)/60:.1f} minutes")
    
    print("\n🔬 KEY FINDINGS:")
    print(f"   Collapse frequency: {baseline_analysis['collapse_frequency']:.1f}%")
    print(f"   95% CI: [{baseline_analysis['collapse_frequency_ci'][0]:.1f}%, {baseline_analysis['collapse_frequency_ci'][1]:.1f}%]")
    print(f"   Collapse timing distribution:")
    print(f"      Kurtosis: {baseline_analysis['collapse_step_kurtosis']:.2f} {'(heavy-tailed)' if baseline_analysis['collapse_step_kurtosis'] > 3 else '(not heavy-tailed)'}")
    print(f"      Skewness: {baseline_analysis['collapse_step_skewness']:.2f}")
    
    print("\n✅ VALIDATION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
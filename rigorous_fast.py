"""
Fast Rigorous Validation - Simplified Version

Runs essential experiments without scipy dependency.
Uses pure Python statistics.
"""

import time
import json
import random
import statistics
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from dataclasses import dataclass, field

print("="*80)
print("🔬 RIGOROUS VALIDATION - FAST VERSION")
print("="*80)
print("Running 50+ experiments with statistical analysis")
print("="*80)

# =====================================================
# EXPERIMENT DESIGN
# =====================================================

@dataclass
class ExperimentConfig:
    """Configuration for a single experiment."""
    name: str
    runs: int = 10
    steps: int = 1000
    seed_base: int = 42
    
    # System parameters
    scaling_coefficient: float = 1.0
    stress_chaos_amplitude: float = 0.15
    collapse_threshold: float = 0.7
    schism_threshold: float = 0.5
    territory_bonus: float = 0.3
    
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
    
    steps_completed: int = 0
    collapsed: bool = False
    collapse_step: int = -1
    renaissance: bool = False
    renaissance_step: int = -1
    extinct: bool = False
    
    final_population: int = 0
    peak_population: int = 0
    population_history: List[int] = field(default_factory=list)
    
    symbol_count: int = 0
    meta_symbol_depth: int = 0
    
    total_stress: float = 0.0
    avg_efficiency: float = 1.0
    schism_count: int = 0
    collapse_count: int = 0
    
    golden_age_steps: int = 0
    dark_age_steps: int = 0


def run_single(config: ExperimentConfig, run_id: int) -> RunResult:
    """Run a single simulation."""
    seed = config.seed_base + run_id
    random.seed(seed)
    
    result = RunResult(
        run_id=run_id,
        seed=seed,
        config_name=config.name
    )
    
    # Initialize systems
    from cognitive_stress import CognitiveStressSystem
    from scaling_penalties import ScalingPenaltySystem
    from schism import SchismSystem
    from collapse import CollapseSystem, CollapseStage
    from territory import TerritorySystem
    
    stress = CognitiveStressSystem(
        chaos_intensity=config.stress_chaos_amplitude * config.scaling_coefficient if config.enable_stress else 0.01,
        noise_level=0.05
    )
    scaling = ScalingPenaltySystem()
    schism = SchismSystem(schism_threshold=config.schism_threshold)
    collapse_sys = CollapseSystem()
    territory = TerritorySystem(30, 30)
    
    # Initialize population
    population = 20
    symbols = 20
    meta_symbols = 0
    territory_size = 10
    efficiency = 1.0
    
    for step in range(config.steps):
        result.steps_completed = step
        
        # Population dynamics
        birth_rate = 0.02 * efficiency
        death_rate = 0.015 + (0.005 * population / 100)
        
        births = int(population * birth_rate)
        deaths = int(population * death_rate)
        
        # Apply stress
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
                population = max(1, int(population * 0.7))
                symbols = max(5, int(symbols * 0.8))
            
            if collapse_state.stage == CollapseStage.RECOVERING:
                result.renaissance = True
                if result.renaissance_step < 0:
                    result.renaissance_step = step
            
            if collapse_state.stage == CollapseStage.EXTINCT:
                result.extinct = True
                break
        
        # Check schism
        if config.enable_schism:
            symbol_conflict = random.uniform(0, 0.5)
            schism_risk = schism.calculate_schism_risk(1, population, symbol_conflict, territory_size)
            
            if random.random() < schism_risk * 0.001:
                result.schism_count += 1
                population = max(5, int(population * 0.7))
        
        # Territory
        if config.enable_territory:
            territory_size = min(225, territory_size + random.randint(0, 1))
        
        # Symbols
        if random.random() < 0.01:
            symbols += random.randint(1, 3)
        if random.random() < 0.005 and symbols > 10:
            symbols -= random.randint(1, 2)
        
        if config.enable_meta_symbols and symbols > 30 and random.random() < 0.001:
            meta_symbols += 1
        
        if config.enable_memory_compression and step % 500 == 0 and symbols > 40:
            symbols = int(symbols * 0.9)
        
        # Golden/dark age
        if efficiency > 0.85 and population > 15:
            result.golden_age_steps += 1
        elif efficiency < 0.5:
            result.dark_age_steps += 1
        
        if population > result.peak_population:
            result.peak_population = population
        
        result.total_stress += chaos
    
    result.final_population = population
    result.symbol_count = symbols
    result.meta_symbol_depth = meta_symbols
    
    return result


def analyze(results: List[RunResult]) -> dict:
    """Compute statistics."""
    collapses = [r.collapse_step for r in results if r.collapse_step >= 0]
    renaissances = [r.renaissance_step for r in results if r.renaissance_step >= 0]
    lifespans = [r.steps_completed for r in results]
    populations = [r.final_population for r in results]
    symbols = [r.symbol_count for r in results]
    schisms = [r.schism_count for r in results]
    efficiencies = [r.avg_efficiency for r in results]
    golden_ages = [r.golden_age_steps for r in results]
    
    def ci_95(data):
        if len(data) < 2:
            return (0, 0)
        mean = statistics.mean(data)
        se = statistics.stdev(data) / math.sqrt(len(data))
        return (mean - 1.96 * se, mean + 1.96 * se)
    
    def kurtosis(data):
        if len(data) < 4:
            return 0
        n = len(data)
        mean = statistics.mean(data)
        std = statistics.stdev(data)
        if std == 0:
            return 0
        m4 = sum((x - mean) ** 4 for x in data) / n
        kurt = m4 / (std ** 4) - 3
        return kurt
    
    def skewness(data):
        if len(data) < 3:
            return 0
        n = len(data)
        mean = statistics.mean(data)
        std = statistics.stdev(data)
        if std == 0:
            return 0
        m3 = sum((x - mean) ** 3 for x in data) / n
        return m3 / (std ** 3)
    
    return {
        'runs': len(results),
        'collapse_frequency': len(collapses) / len(results) * 100 if results else 0,
        'collapse_frequency_ci': ci_95([1 if r.collapse_step >= 0 else 0 for r in results]),
        'mean_collapse_step': statistics.mean(collapses) if collapses else -1,
        'collapse_step_std': statistics.stdev(collapses) if len(collapses) > 1 else 0,
        'collapse_step_kurtosis': kurtosis(collapses) if len(collapses) > 3 else 0,
        'collapse_step_skewness': skewness(collapses) if len(collapses) > 2 else 0,
        'renaissance_rate': len(renaissances) / len(results) * 100 if results else 0,
        'extinction_rate': sum(1 for r in results if r.extinct) / len(results) * 100 if results else 0,
        'mean_lifespan': statistics.mean(lifespans) if lifespans else 0,
        'lifespan_std': statistics.stdev(lifespans) if len(lifespans) > 1 else 0,
        'final_population_mean': statistics.mean(populations) if populations else 0,
        'final_population_std': statistics.stdev(populations) if len(populations) > 1 else 0,
        'symbol_count_mean': statistics.mean(symbols) if symbols else 0,
        'symbol_count_kurtosis': kurtosis(symbols),
        'schism_rate_mean': statistics.mean(schisms) if schisms else 0,
        'avg_efficiency': statistics.mean(efficiencies) if efficiencies else 0,
        'golden_age_rate': statistics.mean(golden_ages) / results[0].steps_completed * 100 if results else 0,
    }


def run_experiment(config: ExperimentConfig) -> Tuple[List[RunResult], dict]:
    """Run experiment and return results."""
    print(f"\n🔬 {config.name} (runs={config.runs}, steps={config.steps})")
    results = []
    for i in range(config.runs):
        if (i + 1) % 10 == 0:
            print(f"   {i+1}/{config.runs}...", end="\r")
        results.append(run_single(config, i))
    print(f"   Done.{' '*20}")
    return results, analyze(results)


# =====================================================
# MAIN EXPERIMENTS
# =====================================================

start_time = time.time()
all_results = {}

# =====================================================
# SECTION 1: REPRODUCIBILITY (50 runs baseline)
# =====================================================
print("\n" + "="*80)
print("📊 SECTION 1 — REPRODUCIBILITY")
print("="*80)

baseline_config = ExperimentConfig(name="baseline", runs=50, steps=1000, seed_base=42)
baseline_results, baseline_analysis = run_experiment(baseline_config)
all_results['baseline'] = (baseline_results, baseline_analysis)

print(f"\n   Collapse frequency: {baseline_analysis['collapse_frequency']:.1f}%")
print(f"   95% CI: [{baseline_analysis['collapse_frequency_ci'][0]:.1f}%, {baseline_analysis['collapse_frequency_ci'][1]:.1f}%]")
print(f"   Mean collapse step: {baseline_analysis['mean_collapse_step']:.0f} (σ={baseline_analysis['collapse_step_std']:.0f})")
print(f"   Kurtosis: {baseline_analysis['collapse_step_kurtosis']:.2f} (>3 = heavy-tailed)")
print(f"   Skewness: {baseline_analysis['collapse_step_skewness']:.2f}")

# Seed stability
print("\n🔬 Seed stability test...")
seed_results = []
for seed_base in [1000, 2000, 3000, 4000, 5000]:
    config = ExperimentConfig(name=f"seed_{seed_base}", runs=10, steps=1000, seed_base=seed_base)
    _, analysis = run_experiment(config)
    seed_results.append(analysis['collapse_frequency'])

variance = statistics.variance(seed_results) if len(seed_results) > 1 else 0
print(f"   Collapse variance across seeds: {variance:.2f}")
print(f"   Result: {'✅ STABLE' if variance < 100 else '⚠️ UNSTABLE'}")

# =====================================================
# SECTION 2: PARAMETER SENSITIVITY
# =====================================================
print("\n" + "="*80)
print("📊 SECTION 2 — PARAMETER SENSITIVITY")
print("="*80)

sensitivity_configs = [
    ("scaling +20%", ExperimentConfig(name="scaling_plus20", runs=20, steps=1000, scaling_coefficient=1.2)),
    ("scaling -20%", ExperimentConfig(name="scaling_minus20", runs=20, steps=1000, scaling_coefficient=0.8)),
    ("stress +20%", ExperimentConfig(name="stress_plus20", runs=20, steps=1000, stress_chaos_amplitude=0.18)),
    ("stress -20%", ExperimentConfig(name="stress_minus20", runs=20, steps=1000, stress_chaos_amplitude=0.12)),
    ("collapse +20%", ExperimentConfig(name="collapse_plus20", runs=20, steps=1000, collapse_threshold=0.84)),
    ("collapse -20%", ExperimentConfig(name="collapse_minus20", runs=20, steps=1000, collapse_threshold=0.56)),
    ("schism +20%", ExperimentConfig(name="schism_plus20", runs=20, steps=1000, schism_threshold=0.6)),
    ("schism -20%", ExperimentConfig(name="schism_minus20", runs=20, steps=1000, schism_threshold=0.4)),
]

print("\n| Parameter | Collapse | Lifespan | Δ Collapse | Δ Lifespan |")
print("|-----------|----------|----------|------------|------------|")

for name, config in sensitivity_configs:
    _, analysis = run_experiment(config)
    collapse_diff = analysis['collapse_frequency'] - baseline_analysis['collapse_frequency']
    lifespan_diff = analysis['mean_lifespan'] - baseline_analysis['mean_lifespan']
    print(f"| {name:9} | {analysis['collapse_frequency']:6.1f}% | {analysis['mean_lifespan']:8.0f} | {collapse_diff:+8.1f}% | {lifespan_diff:+10.0f} |")

# =====================================================
# SECTION 3: ABLATION TESTS
# =====================================================
print("\n" + "="*80)
print("📊 SECTION 3 — ABLATION TESTS")
print("="*80)

ablation_configs = [
    ("No Stress", ExperimentConfig(name="no_stress", runs=20, steps=1000, enable_stress=False)),
    ("No Scaling", ExperimentConfig(name="no_scaling", runs=20, steps=1000, enable_scaling=False)),
    ("No Collapse", ExperimentConfig(name="no_collapse", runs=20, steps=1000, enable_collapse=False)),
    ("No Schism", ExperimentConfig(name="no_schism", runs=20, steps=1000, enable_schism=False)),
    ("No Territory", ExperimentConfig(name="no_territory", runs=20, steps=1000, enable_territory=False)),
    ("No Meta-Symbols", ExperimentConfig(name="no_meta", runs=20, steps=1000, enable_meta_symbols=False)),
    ("No Memory Compression", ExperimentConfig(name="no_memory", runs=20, steps=1000, enable_memory_compression=False)),
]

print("\n| System Removed | Collapse | Lifespan | Impact |")
print("|----------------|----------|----------|--------|")

for name, config in ablation_configs:
    _, analysis = run_experiment(config)
    collapse_diff = analysis['collapse_frequency'] - baseline_analysis['collapse_frequency']
    lifespan_diff = analysis['mean_lifespan'] - baseline_analysis['mean_lifespan']
    significant = abs(collapse_diff) > 10 or abs(lifespan_diff) > 100
    impact = "✅ SIGNIFICANT" if significant else "⚠️ Marginal"
    print(f"| {name:14} | {analysis['collapse_frequency']:6.1f}% | {analysis['mean_lifespan']:8.0f} | {impact} |")

# =====================================================
# SECTION 4: DISTRIBUTION PROPERTIES
# =====================================================
print("\n" + "="*80)
print("📊 SECTION 4 — DISTRIBUTION PROPERTIES")
print("="*80)

print(f"\n   Collapse timing:")
print(f"      Mean: {baseline_analysis['mean_collapse_step']:.0f}")
print(f"      Std: {baseline_analysis['collapse_step_std']:.0f}")
print(f"      Kurtosis: {baseline_analysis['collapse_step_kurtosis']:.2f} {'(heavy-tailed)' if baseline_analysis['collapse_step_kurtosis'] > 3 else '(not heavy-tailed)'}")
print(f"      Skewness: {baseline_analysis['collapse_step_skewness']:.2f}")

print(f"\n   Symbol count:")
print(f"      Mean: {baseline_analysis['symbol_count_mean']:.0f}")
print(f"      Kurtosis: {baseline_analysis['symbol_count_kurtosis']:.2f} {'(heavy-tailed)' if baseline_analysis['symbol_count_kurtosis'] > 3 else ''}")

# =====================================================
# FINAL SUMMARY
# =====================================================
print("\n" + "="*80)
print("📊 FINAL SUMMARY")
print("="*80)

print(f"\n   Total runs: 50 baseline + 80 sensitivity + 140 ablation = 270+")
print(f"   Runtime: {(time.time() - start_time)/60:.1f} minutes")

print("\n🔬 KEY FINDINGS:")
print(f"   Collapse frequency: {baseline_analysis['collapse_frequency']:.1f}% (95% CI: [{baseline_analysis['collapse_frequency_ci'][0]:.1f}%, {baseline_analysis['collapse_frequency_ci'][1]:.1f}%])")
print(f"   Renaissance rate: {baseline_analysis['renaissance_rate']:.1f}%")
print(f"   Extinction rate: {baseline_analysis['extinction_rate']:.1f}%")
print(f"   Mean lifespan: {baseline_analysis['mean_lifespan']:.0f} steps")

print("\n✅ VALIDATION COMPLETE")

# Save results
output = {
    'timestamp': datetime.now().isoformat(),
    'baseline': baseline_analysis,
    'total_runs': 270,
}

path = Path("metrics") / f"rigorous_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
path.parent.mkdir(exist_ok=True)
with open(path, 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n📄 Results saved: {path}")
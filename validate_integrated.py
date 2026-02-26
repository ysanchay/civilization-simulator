"""
Rigorous Validation with Integrated Simulator

Now using run_integrated.py which has proper system integration.
"""

import time
import json
import random
import statistics
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, field

print("="*80)
print("🔬 RIGOROUS VALIDATION - INTEGRATED SIMULATOR")
print("="*80)

# Import the integrated simulator
import sys
sys.path.insert(0, '/home/claw/Civilization_simulator')
from run_integrated import IntegratedSimulator, Tribe
from config import SimulationConfig


@dataclass
class ExperimentConfig:
    name: str
    runs: int = 10
    steps: int = 1000
    seed_base: int = 42
    tribes: int = 5
    
    # Parameters
    scaling_coefficient: float = 1.0
    stress_amplitude: float = 0.20
    collapse_threshold: float = 0.5
    schism_threshold: float = 0.3
    carrying_capacity: int = 100
    
    # Toggles
    enable_stress: bool = True
    enable_scaling: bool = True
    enable_collapse: bool = True
    enable_schism: bool = True


@dataclass
class RunResult:
    run_id: int
    seed: int
    config_name: str
    steps_completed: int = 0
    
    collapsed: bool = False
    collapse_step: int = -1
    renaissance: bool = False
    extinct: bool = False
    
    final_population: int = 0
    peak_population: int = 0
    final_tribes: int = 0
    peak_tribes: int = 0
    
    total_collapses: int = 0
    total_schisms: int = 0
    total_wars: int = 0
    total_renaissances: int = 0
    
    symbol_count: int = 0
    avg_efficiency: float = 0.0
    
    collapse_times: List[int] = field(default_factory=list)


def run_experiment(config: ExperimentConfig) -> Tuple[List[RunResult], dict]:
    """Run experiment and return results."""
    print(f"\n🔬 {config.name} (runs={config.runs}, steps={config.steps})")
    
    results = []
    
    for i in range(config.runs):
        if (i + 1) % 5 == 0:
            print(f"   {i+1}/{config.runs}...", end="\r")
        
        seed = config.seed_base + i
        random.seed(seed)
        
        # Create simulator
        sim_config = SimulationConfig()
        sim_config.world.width = 30
        sim_config.world.height = 30
        
        sim = IntegratedSimulator(sim_config)
        
        # Apply config
        sim.CARRYING_CAPACITY = config.carrying_capacity
        sim.SCHISM_THRESHOLD = config.schism_threshold
        sim.STRESS_COLLAPSE_THRESHOLD = config.collapse_threshold
        sim.stress.chaos_intensity = config.stress_amplitude if config.enable_stress else 0.01
        
        # Seed tribes
        sim.seed_tribes(config.tribes)
        
        # Run simulation
        report = sim.run(max_steps=config.steps, log_interval=999999)
        
        # Collect results
        result = RunResult(
            run_id=i,
            seed=seed,
            config_name=config.name,
            steps_completed=report['steps'],
            final_population=report['total_population'],
            final_tribes=report['tribes_active'],
            total_collapses=report['total_collapses'],
            total_schisms=report['total_schisms'],
            total_wars=report['total_wars'],
            total_renaissances=report['total_renaissances'],
            symbol_count=report['total_symbols'],
            avg_efficiency=report['avg_efficiency'],
        )
        
        # Get collapse times from events
        for event in report['events']:
            if event['type'] == 'collapse':
                result.collapse_times.append(event['step'])
        
        result.collapsed = len(result.collapse_times) > 0
        if result.collapse_times:
            result.collapse_step = result.collapse_times[0]
        
        result.extinct = report['tribes_active'] == 0
        result.renaissance = report['total_renaissances'] > 0
        
        results.append(result)
    
    print(f"   Done.{' '*20}")
    
    return results, analyze(results)


def analyze(results: List[RunResult]) -> dict:
    """Compute statistics."""
    collapses = [r.collapse_step for r in results if r.collapse_step >= 0]
    populations = [r.final_population for r in results]
    tribes = [r.final_tribes for r in results]
    collapse_counts = [r.total_collapses for r in results]
    schism_counts = [r.total_schisms for r in results]
    war_counts = [r.total_wars for r in results]
    renaissance_counts = [r.total_renaissances for r in results]
    efficiencies = [r.avg_efficiency for r in results]
    symbols = [r.symbol_count for r in results]
    
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
        return m4 / (std ** 4) - 3
    
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
        'renaissance_rate': sum(1 for r in results if r.renaissance) / len(results) * 100,
        'extinction_rate': sum(1 for r in results if r.extinct) / len(results) * 100,
        'mean_final_population': statistics.mean(populations) if populations else 0,
        'mean_final_tribes': statistics.mean(tribes) if tribes else 0,
        'mean_collapses': statistics.mean(collapse_counts) if collapse_counts else 0,
        'mean_schisms': statistics.mean(schism_counts) if schism_counts else 0,
        'mean_wars': statistics.mean(war_counts) if war_counts else 0,
        'mean_renaissances': statistics.mean(renaissance_counts) if renaissance_counts else 0,
        'mean_efficiency': statistics.mean(efficiencies) if efficiencies else 0,
        'mean_symbols': statistics.mean(symbols) if symbols else 0,
        'population_variance': statistics.variance(populations) if len(populations) > 1 else 0,
        'collapse_variance': statistics.variance(collapse_counts) if len(collapse_counts) > 1 else 0,
    }


def main():
    start_time = time.time()
    
    # =====================================================
    # SECTION 1: BASELINE (50 runs)
    # =====================================================
    print("\n" + "="*80)
    print("📊 SECTION 1 — BASELINE REPRODUCIBILITY")
    print("="*80)
    
    baseline_config = ExperimentConfig(
        name="baseline",
        runs=30,
        steps=1500,
        seed_base=42,
        tribes=5,
    )
    
    baseline_results, baseline_analysis = run_experiment(baseline_config)
    
    print(f"\n   Collapse frequency: {baseline_analysis['collapse_frequency']:.1f}%")
    print(f"   95% CI: [{baseline_analysis['collapse_frequency_ci'][0]:.1f}%, {baseline_analysis['collapse_frequency_ci'][1]:.1f}%]")
    print(f"   Mean collapses/run: {baseline_analysis['mean_collapses']:.1f}")
    print(f"   Mean first collapse: {baseline_analysis['mean_collapse_step']:.0f} steps")
    print(f"   Collapse timing σ: {baseline_analysis['collapse_step_std']:.0f}")
    print(f"   Kurtosis: {baseline_analysis['collapse_step_kurtosis']:.2f} (>3 = heavy-tailed)")
    print(f"   Renaissance rate: {baseline_analysis['renaissance_rate']:.1f}%")
    print(f"   Mean efficiency: {baseline_analysis['mean_efficiency']:.0%}")
    
    # =====================================================
    # SECTION 2: PARAMETER SENSITIVITY
    # =====================================================
    print("\n" + "="*80)
    print("📊 SECTION 2 — PARAMETER SENSITIVITY")
    print("="*80)
    
    sensitivity_configs = [
        ("Stress +20%", ExperimentConfig(name="stress_plus", runs=15, steps=1500, stress_amplitude=0.24)),
        ("Stress -20%", ExperimentConfig(name="stress_minus", runs=15, steps=1500, stress_amplitude=0.16)),
        ("Capacity -20%", ExperimentConfig(name="capacity_minus", runs=15, steps=1500, carrying_capacity=80)),
        ("Capacity +20%", ExperimentConfig(name="capacity_plus", runs=15, steps=1500, carrying_capacity=120)),
        ("Schism +50%", ExperimentConfig(name="schism_plus", runs=15, steps=1500, schism_threshold=0.45)),
        ("Schism -50%", ExperimentConfig(name="schism_minus", runs=15, steps=1500, schism_threshold=0.15)),
    ]
    
    print("\n| Parameter | Collapses | Schisms | Wars | Pop | Δ Collapses |")
    print("|-----------|-----------|---------|------|-----|-------------|")
    
    for name, config in sensitivity_configs:
        _, analysis = run_experiment(config)
        collapse_diff = analysis['mean_collapses'] - baseline_analysis['mean_collapses']
        print(f"| {name:9} | {analysis['mean_collapses']:9.1f} | {analysis['mean_schisms']:7.1f} | {analysis['mean_wars']:4.0f} | {analysis['mean_final_population']:3.0f} | {collapse_diff:+11.1f} |")
    
    # =====================================================
    # SECTION 3: ABLATION
    # =====================================================
    print("\n" + "="*80)
    print("📊 SECTION 3 — ABLATION TESTS")
    print("="*80)
    
    ablation_configs = [
        ("No Stress", ExperimentConfig(name="no_stress", runs=15, steps=1500, enable_stress=False)),
        ("No Collapse", ExperimentConfig(name="no_collapse", runs=15, steps=1500, collapse_threshold=1.0)),
        ("No Schism", ExperimentConfig(name="no_schism", runs=15, steps=1500, schism_threshold=1.0)),
    ]
    
    print("\n| System Removed | Collapses | Schisms | Efficiency | Impact |")
    print("|----------------|-----------|---------|------------|--------|")
    
    for name, config in ablation_configs:
        _, analysis = run_experiment(config)
        collapse_diff = analysis['mean_collapses'] - baseline_analysis['mean_collapses']
        eff_diff = analysis['mean_efficiency'] - baseline_analysis['mean_efficiency']
        significant = abs(collapse_diff) > 5 or abs(eff_diff) > 0.05
        impact = "✅ SIGNIFICANT" if significant else "⚠️ Marginal"
        print(f"| {name:14} | {analysis['mean_collapses']:9.1f} | {analysis['mean_schisms']:7.1f} | {analysis['mean_efficiency']:10.0%} | {impact} |")
    
    # =====================================================
    # SECTION 4: DISTRIBUTIONS
    # =====================================================
    print("\n" + "="*80)
    print("📊 SECTION 4 — DISTRIBUTION PROPERTIES")
    print("="*80)
    
    collapse_times = [ct for r in baseline_results for ct in r.collapse_times]
    
    print(f"\n   Collapse timing:")
    print(f"      Total collapses: {len(collapse_times)}")
    print(f"      Mean: {statistics.mean(collapse_times):.0f} steps" if collapse_times else "      N/A")
    print(f"      Std: {statistics.stdev(collapse_times):.0f}" if len(collapse_times) > 1 else "      N/A")
    print(f"      Kurtosis: {baseline_analysis['collapse_step_kurtosis']:.2f} {'(heavy-tailed)' if baseline_analysis['collapse_step_kurtosis'] > 3 else ''}")
    
    print(f"\n   Population:")
    print(f"      Mean: {baseline_analysis['mean_final_population']:.0f}")
    print(f"      Variance: {baseline_analysis['population_variance']:.0f}")
    
    print(f"\n   Events per run:")
    print(f"      Collapses: {baseline_analysis['mean_collapses']:.1f}")
    print(f"      Schisms: {baseline_analysis['mean_schisms']:.1f}")
    print(f"      Wars: {baseline_analysis['mean_wars']:.1f}")
    print(f"      Renaissances: {baseline_analysis['mean_renaissances']:.1f}")
    
    # =====================================================
    # SUMMARY
    # =====================================================
    elapsed = time.time() - start_time
    
    print("\n" + "="*80)
    print("📊 VALIDATION SUMMARY")
    print("="*80)
    
    print(f"\n   Total runs: {baseline_analysis['runs']} + sensitivity + ablation = 100+")
    print(f"   Runtime: {elapsed/60:.1f} minutes")
    
    print("\n✅ KEY FINDINGS:")
    print(f"   Collapse frequency: {baseline_analysis['collapse_frequency']:.1f}%")
    print(f"   Mean collapses/run: {baseline_analysis['mean_collapses']:.1f}")
    print(f"   Collapse timing kurtosis: {baseline_analysis['collapse_step_kurtosis']:.2f}")
    print(f"   Renaissance rate: {baseline_analysis['renaissance_rate']:.1f}%")
    print(f"   Population variance: {baseline_analysis['population_variance']:.0f}")
    
    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'runtime_seconds': elapsed,
        'baseline': baseline_analysis,
    }
    
    path = Path("/home/claw/Civilization_simulator/metrics") / f"integrated_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path.parent.mkdir(exist_ok=True)
    with open(path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n📄 Results saved: {path}")
    print("="*80)


if __name__ == "__main__":
    main()
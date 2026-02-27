#!/usr/bin/env python3
"""
Quick High Priority Analysis - Reduced parameters for faster execution
"""

import json
import numpy as np
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter
import sys

sys.path.insert(0, str(Path(__file__).parent))

from run_integrated import IntegratedSimulator
from config import SimulationConfig, WorldConfig


def create_simulator(width=25, height=25, n_agents=20, seed=None):
    config = SimulationConfig(
        world=WorldConfig(width=width, height=height),
        initial_agents=n_agents,
        seed=seed
    )
    sim = IntegratedSimulator(config)
    sim.seed_tribes(count=n_agents)
    return sim


def quick_analysis():
    """Run quick analysis with reduced parameters"""
    print("🧬 QUICK HIGH PRIORITY ANALYSIS")
    print("="*60)
    
    results = {}
    
    # 1. Quick stability check
    print("\n1. STABILITY CHECK (1 run × 2000 steps)...")
    sim = create_simulator(width=25, height=25, n_agents=15, seed=42)
    
    pops = []
    symbols = []
    collapses = 0
    prev_pop = {}
    
    for step in range(2000):
        sim.step_simulation()
        
        if step % 200 == 0:
            total_pop = sum(getattr(t, 'population', 0) for t in sim.tribes.values())
            total_sym = sum(getattr(t, 'symbols', 0) for t in sim.tribes.values())
            if isinstance(total_sym, int):
                pass
            
            pops.append(total_pop)
            symbols.append(total_sym)
            
            # Check for collapses
            for tid, t in sim.tribes.items():
                pop = getattr(t, 'population', 0)
                if tid in prev_pop and prev_pop[tid] > 20 and pop < prev_pop[tid] * 0.5:
                    collapses += 1
                prev_pop[tid] = pop
            
            print(f"  Step {step}: Pop={total_pop}, Symbols={total_sym}, Collapses={collapses}")
    
    # Calculate kurtosis
    if len(pops) > 4:
        changes = np.diff(pops)
        kurt = float((np.mean((changes - np.mean(changes))**4) / (np.std(changes)**4 + 1e-10)) - 3)
    else:
        kurt = 0
    
    results['stability'] = {
        'final_pop': pops[-1] if pops else 0,
        'max_pop': max(pops) if pops else 0,
        'collapses': collapses,
        'kurtosis': kurt,
        'heavy_tailed': kurt > 3
    }
    
    print(f"\n  Final pop: {results['stability']['final_pop']}")
    print(f"  Kurtosis: {kurt:.2f} ({'heavy-tailed' if kurt > 3 else 'normal'})")
    
    # 2. Collapse types
    print("\n2. COLLAPSE ANALYSIS (5 runs × 1000 steps)...")
    collapse_types = defaultdict(int)
    
    for run in range(5):
        sim = create_simulator(width=20, height=20, n_agents=12, seed=100+run)
        prev = {}
        
        for step in range(1000):
            sim.step_simulation()
            
            for tid, t in sim.tribes.items():
                pop = getattr(t, 'population', 0)
                eff = getattr(t, 'efficiency', 1.0)
                stress = getattr(t, 'stress_level', 0)
                
                if tid in prev and prev[tid]['pop'] > 20 and pop < prev[tid]['pop'] * 0.5:
                    # Classify collapse
                    if prev[tid]['pop'] > 80:
                        collapse_types['overpopulation'] += 1
                    elif prev[tid]['eff'] < 0.7:
                        collapse_types['efficiency'] += 1
                    elif prev[tid]['stress'] > 0.7:
                        collapse_types['stress'] += 1
                    else:
                        collapse_types['compound'] += 1
                
                prev[tid] = {'pop': pop, 'eff': eff, 'stress': stress}
    
    results['collapse_types'] = dict(collapse_types)
    total_collapses = sum(collapse_types.values())
    print(f"  Total collapses: {total_collapses}")
    for ct, count in collapse_types.items():
        print(f"    {ct}: {count} ({100*count/max(1,total_collapses):.0f}%)")
    
    # 3. War distribution
    print("\n3. WAR DISTRIBUTION (5 runs × 1000 steps)...")
    war_counts = []
    
    for run in range(5):
        sim = create_simulator(width=25, height=25, n_agents=15, seed=200+run)
        wars = 0
        
        for step in range(1000):
            sim.step_simulation()
            # Check for conflicts
            for t in sim.tribes.values():
                if getattr(t, 'in_conflict', False):
                    wars += 1
                    break
        
        war_counts.append(wars)
    
    results['wars'] = {
        'total': sum(war_counts),
        'per_run': np.mean(war_counts),
        'variance': np.var(war_counts)
    }
    print(f"  Wars per run: {results['wars']['per_run']:.1f}")
    
    # Save
    output = Path("metrics") / f"quick_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output.parent.mkdir(exist_ok=True)
    with open(output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Saved to {output}")
    return results


if __name__ == "__main__":
    quick_analysis()
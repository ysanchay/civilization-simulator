#!/usr/bin/env python3
"""
Test 3: Long Horizon Stability - Do heavy-tailed collapses persist?
Quick test: 3 runs × 2000 steps
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from run_integrated import IntegratedSimulator
from config import SimulationConfig, WorldConfig

def test_long_horizon():
    print("="*60)
    print("🔬 TEST: Long Horizon Stability")
    print("="*60)
    
    all_collapses = []
    all_kurtosis = []
    
    for run in range(3):
        print(f"\n  Run {run+1}/3...")
        
        config = SimulationConfig(
            world=WorldConfig(width=25, height=25),
            initial_agents=20,
            seed=200 + run
        )
        sim = IntegratedSimulator(config)
        sim.seed_tribes(count=20)
        
        prev_pops = {}
        collapses = []
        pops_over_time = []
        
        for step in range(2000):
            sim.step_simulation()
            
            total_pop = 0
            for tid, t in sim.tribes.items():
                pop = getattr(t, 'population', 0)
                total_pop += pop
                
                if tid in prev_pops:
                    prev = prev_pops[tid]
                    if prev > 20 and pop < prev * 0.5:
                        collapses.append({'step': step, 'tribe': tid, 'prev': prev, 'after': pop})
                
                prev_pops[tid] = pop
            
            if step % 200 == 0:
                pops_over_time.append(total_pop)
                print(f"    Step {step}: Pop={total_pop}, Collapses={len(collapses)}")
        
        all_collapses.extend(collapses)
        
        # Calculate kurtosis of population changes
        if len(pops_over_time) > 4:
            changes = np.diff(pops_over_time)
            if np.std(changes) > 0:
                kurt = float((np.mean((changes - np.mean(changes))**4) / (np.std(changes)**4)) - 3)
            else:
                kurt = 0
            all_kurtosis.append(kurt)
    
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    print(f"  Total collapses: {len(all_collapses)}")
    print(f"  Collapse rate: {len(all_collapses) / 3:.1f} per run")
    print(f"  Kurtosis values: {[f'{k:.2f}' for k in all_kurtosis]}")
    print(f"  Mean kurtosis: {np.mean(all_kurtosis):.2f}")
    print()
    
    if np.mean(all_kurtosis) > 3:
        print("  ✅ HEAVY-TAILED: Collapses remain heavy-tailed over long runs")
    else:
        print("  ❌ NOT HEAVY-TAILED: Collapses may be artifact of short runs")
    
    return {
        'total_collapses': len(all_collapses),
        'mean_kurtosis': float(np.mean(all_kurtosis)),
        'heavy_tailed': np.mean(all_kurtosis) > 3
    }

if __name__ == "__main__":
    test_long_horizon()
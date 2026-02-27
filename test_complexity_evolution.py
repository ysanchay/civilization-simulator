#!/usr/bin/env python3
"""
Test 4: Complexity Evolution - Does complexity grow or saturate?
Quick test: 2 runs × 1500 steps
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from run_integrated import IntegratedSimulator
from config import SimulationConfig, WorldConfig

def test_complexity_evolution():
    print("="*60)
    print("🔬 TEST: Complexity Evolution")
    print("="*60)
    
    all_symbols = []
    all_populations = []
    
    for run in range(2):
        print(f"\n  Run {run+1}/2...")
        
        config = SimulationConfig(
            world=WorldConfig(width=30, height=30),
            initial_agents=25,
            seed=300 + run
        )
        sim = IntegratedSimulator(config)
        sim.seed_tribes(count=25)
        
        symbols_over_time = []
        pop_over_time = []
        
        for step in range(1500):
            sim.step_simulation()
            
            total_pop = 0
            total_symbols = 0
            
            for t in sim.tribes.values():
                pop = getattr(t, 'population', 0)
                syms = getattr(t, 'symbols', 0)
                if isinstance(syms, (dict, list, set)):
                    syms = len(syms)
                
                total_pop += pop
                total_symbols += syms
            
            if step % 150 == 0:
                symbols_over_time.append(total_symbols)
                pop_over_time.append(total_pop)
                print(f"    Step {step}: Pop={total_pop}, Symbols={total_symbols}")
        
        all_symbols.append(symbols_over_time)
        all_populations.append(pop_over_time)
    
    # Analyze trend
    mean_symbols = np.mean(all_symbols, axis=0)
    x = np.arange(len(mean_symbols))
    
    if len(x) > 1:
        slope, _ = np.polyfit(x, mean_symbols, 1)
    else:
        slope = 0
    
    first_half = np.mean([np.mean(s[:len(s)//2]) for s in all_symbols if len(s) > 2])
    second_half = np.mean([np.mean(s[len(s)//2:]) for s in all_symbols if len(s) > 2])
    
    growth_ratio = second_half / (first_half + 1e-10)
    
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    print(f"  Symbol trend slope: {slope:.1f} symbols/step")
    print(f"  First half avg: {first_half:.0f} symbols")
    print(f"  Second half avg: {second_half:.0f} symbols")
    print(f"  Growth ratio: {growth_ratio:.2f}x")
    print()
    
    if growth_ratio > 1.5:
        print("  ✅ OPEN-ENDED: Complexity growing significantly")
    elif growth_ratio > 1.1:
        print("  ⚠️ SLOW GROWTH: Complexity increasing slowly")
    elif growth_ratio > 0.9:
        print("  ➡️ SATURATING: Complexity plateaued")
    else:
        print("  ❌ DECLINING: Complexity decreasing")
    
    return {
        'slope': float(slope),
        'growth_ratio': float(growth_ratio),
        'open_ended': growth_ratio > 1.5
    }

if __name__ == "__main__":
    test_complexity_evolution()
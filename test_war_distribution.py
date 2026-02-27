#!/usr/bin/env python3
"""
Test 1: War Distribution - Is war frequency heavy-tailed?
Quick test: 10 runs × 500 steps
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from run_integrated import IntegratedSimulator
from config import SimulationConfig, WorldConfig

def test_war_distribution():
    print("="*60)
    print("🔬 TEST: War Heavy-Tailed Distribution")
    print("="*60)
    
    war_intervals = []
    war_counts = []
    
    for run in range(10):
        print(f"\n  Run {run+1}/10...", end=" ", flush=True)
        
        config = SimulationConfig(
            world=WorldConfig(width=20, height=20),
            initial_agents=15,
            seed=42 + run
        )
        sim = IntegratedSimulator(config)
        sim.seed_tribes(count=15)
        
        war_steps = []
        
        for step in range(500):
            sim.step_simulation()
            
            # Collect wars from this step
            for event in sim.events:
                if event.get('type') == 'war' and event.get('step') == step:
                    war_steps.append(step)
        
        # Calculate intervals
        if len(war_steps) > 1:
            unique_steps = sorted(set(war_steps))
            intervals = np.diff(unique_steps)
            war_intervals.extend(intervals.tolist())
        
        war_counts.append(len(war_steps))
        print(f"{len(war_steps)} wars")
    
    # Analyze distribution
    intervals = np.array(war_intervals)
    mean_int = np.mean(intervals)
    std_int = np.std(intervals)
    
    # Kurtosis (heavy tail test)
    if len(intervals) > 4 and std_int > 0:
        kurtosis = float((np.mean((intervals - mean_int)**4) / (std_int**4)) - 3)
    else:
        kurtosis = 0
    
    # Coefficient of variation
    cv = std_int / (mean_int + 1e-10)
    
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    print(f"  Total wars: {sum(war_counts)}")
    print(f"  Wars per run: {np.mean(war_counts):.1f} ± {np.std(war_counts):.1f}")
    print(f"  War intervals: {len(intervals)} samples")
    print(f"  Mean interval: {mean_int:.1f} steps")
    print(f"  Std interval: {std_int:.1f} steps")
    print(f"  Kurtosis: {kurtosis:.2f}")
    print(f"  CV: {cv:.2f}")
    print()
    
    if kurtosis > 3:
        print("  ✅ HEAVY-TAILED: Kurtosis > 3")
        print("     Wars are clustered, not random (Poisson)")
    elif cv > 1.5:
        print("  ⚠️ CLUSTERED: CV > 1.5")
        print("     Wars tend to cluster but not power-law")
    else:
        print("  ❌ NOT HEAVY-TAILED")
        print("     Wars appear random (Poisson-like)")
    
    return {
        'total_wars': sum(war_counts),
        'wars_per_run': float(np.mean(war_counts)),
        'kurtosis': float(kurtosis),
        'cv': float(cv),
        'heavy_tailed': kurtosis > 3
    }

if __name__ == "__main__":
    test_war_distribution()
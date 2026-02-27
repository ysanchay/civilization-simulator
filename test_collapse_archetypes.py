#!/usr/bin/env python3
"""
Test 2: Collapse Archetypes - Are there distinct collapse types?
Quick test: 15 runs × 500 steps
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from collections import defaultdict
from run_integrated import IntegratedSimulator
from config import SimulationConfig, WorldConfig

def test_collapse_archetypes():
    print("="*60)
    print("🔬 TEST: Collapse Archetypes")
    print("="*60)
    
    collapse_events = []
    
    for run in range(15):
        print(f"\n  Run {run+1}/15...", end=" ", flush=True)
        
        config = SimulationConfig(
            world=WorldConfig(width=20, height=20),
            initial_agents=15,
            seed=100 + run
        )
        sim = IntegratedSimulator(config)
        sim.seed_tribes(count=15)
        
        prev_state = {}
        run_collapses = 0
        
        for step in range(500):
            sim.step_simulation()
            
            for tid, t in sim.tribes.items():
                pop = getattr(t, 'population', 0)
                syms = getattr(t, 'symbols', 0)
                if isinstance(syms, (dict, list, set)):
                    syms = len(syms)
                eff = getattr(t, 'efficiency', 1.0)
                stress = getattr(t, 'stress_level', 0)
                territory = getattr(t, 'territory', 1)
                if isinstance(territory, (list, set)):
                    territory = len(territory)
                
                if tid in prev_state:
                    prev = prev_state[tid]
                    
                    # Detect collapse (>50% pop drop)
                    if prev['population'] > 15 and pop < prev['population'] * 0.5:
                        collapse_events.append({
                            'run': run,
                            'step': step,
                            'tribe': tid,
                            'pop_before': prev['population'],
                            'pop_after': pop,
                            'symbols_before': prev['symbols'],
                            'efficiency': prev['efficiency'],
                            'stress': prev['stress'],
                            'territory': prev['territory'],
                        })
                        run_collapses += 1
                
                prev_state[tid] = {
                    'population': pop,
                    'symbols': syms,
                    'efficiency': eff,
                    'stress': stress,
                    'territory': territory
                }
        
        print(f"{run_collapses} collapses")
    
    if not collapse_events:
        print("\n  ⚠️ No collapses detected!")
        return {'n_collapses': 0}
    
    # Categorize into archetypes
    archetypes = defaultdict(list)
    for event in collapse_events:
        if event['pop_before'] > 60:
            archetypes['A_overpopulation'].append(event)
        elif event['territory'] < 3:
            archetypes['B_territory_loss'].append(event)
        elif event['efficiency'] < 0.6:
            archetypes['C_efficiency_collapse'].append(event)
        elif event['stress'] > 0.6:
            archetypes['D_stress_cascade'].append(event)
        else:
            archetypes['E_compound'].append(event)
    
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    print(f"  Total collapses: {len(collapse_events)}")
    print(f"  Collapse rate: {len(collapse_events) / 15:.1f} per run")
    print()
    print("  ARCHETYPE DISTRIBUTION:")
    
    for name in sorted(archetypes.keys()):
        events = archetypes[name]
        pct = len(events) / len(collapse_events) * 100
        avg_pop = np.mean([e['pop_before'] for e in events])
        print(f"    {name}: {len(events)} ({pct:.1f}%)")
        print(f"      Avg pop before: {avg_pop:.0f}")
    
    return {
        'total_collapses': len(collapse_events),
        'archetypes': {k: len(v) for k, v in archetypes.items()},
        'distribution': {k: len(v)/len(collapse_events) for k, v in archetypes.items()}
    }

if __name__ == "__main__":
    test_collapse_archetypes()
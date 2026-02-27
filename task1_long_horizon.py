"""
Task 1: Long Horizon Analysis

Tests if heavy-tailed collapse persists over 5000+ steps.
"""

import json
import random
import statistics
from datetime import datetime
from pathlib import Path

print("="*60)
print("🔴 TASK 1: LONG HORIZON ANALYSIS (5,000 steps)")
print("="*60)

import sys
sys.path.insert(0, '/home/claw/Civilization_simulator')
from run_integrated import IntegratedSimulator
from config import SimulationConfig

results = []

for i in range(5):
    random.seed(1000 + i)
    sim = IntegratedSimulator(SimulationConfig())
    sim.seed_tribes(5)
    
    print(f"\nRun {i+1}/5 (seed={1000+i})...")
    report = sim.run(max_steps=5000, log_interval=1000)
    
    # Calculate kurtosis
    collapse_times = [e['step'] for e in report['events'] if e['type'] == 'collapse']
    
    if len(collapse_times) > 3:
        mean_t = statistics.mean(collapse_times)
        std_t = statistics.stdev(collapse_times)
        n = len(collapse_times)
        kurt = sum((t - mean_t)**4 for t in collapse_times) / (n * std_t**4) - 3 if std_t > 0 else 0
    else:
        kurt = 0
    
    results.append({
        'run': i+1,
        'collapses': report['total_collapses'],
        'schisms': report['total_schisms'],
        'wars': report['total_wars'],
        'renaissances': report['total_renaissances'],
        'population': report['total_population'],
        'tribes': report['tribes_active'],
        'kurtosis': kurt,
        'collapse_times': collapse_times[:20],  # First 20 only
    })
    
    print(f"   Collapses: {report['total_collapses']}, Kurtosis: {kurt:.2f}")

# Summary
avg_kurt = statistics.mean([r['kurtosis'] for r in results])
avg_collapses = statistics.mean([r['collapses'] for r in results])
avg_schisms = statistics.mean([r['schisms'] for r in results])

print("\n" + "="*60)
print("📊 RESULTS")
print("="*60)
print(f"   Avg collapses: {avg_collapses:.1f}")
print(f"   Avg schisms: {avg_schisms:.1f}")
print(f"   Avg kurtosis: {avg_kurt:.2f}")
print(f"   Heavy-tailed persists? {'✅ YES' if avg_kurt > 3 else '⚠️ NO'}")
print(f"   Emergent dynamics? {'✅ YES' if avg_collapses > 20 else '⚠️ NO'}")

# Save
output = {
    'task': 'Long Horizon Analysis',
    'timestamp': datetime.now().isoformat(),
    'steps': 5000,
    'runs': 5,
    'results': results,
    'summary': {
        'avg_collapses': avg_collapses,
        'avg_schisms': avg_schisms,
        'avg_kurtosis': avg_kurt,
        'heavy_tailed_persists': avg_kurt > 3,
    }
}

path = Path("/home/claw/Civilization_simulator/metrics") / f"task1_long_horizon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
path.parent.mkdir(exist_ok=True)
with open(path, 'w') as f:
    json.dump(output, f, indent=2, default=str)

print(f"\n✅ TASK 1 COMPLETE")
print(f"📄 Saved: {path}")
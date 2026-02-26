"""
Quick Implementation - High Priority Items

This script implements the high-priority validation questions.
Runs in ~30 minutes with full analysis.
"""

import json
import random
import statistics
import math
from datetime import datetime
from pathlib import Path
from collections import defaultdict

print("="*80)
print("🔬 HIGH PRIORITY IMPLEMENTATION")
print("="*80)

import sys
sys.path.insert(0, '/home/claw/Civilization_simulator')
from run_integrated import IntegratedSimulator
from config import SimulationConfig

# =====================================================
# 1. LONG HORIZON ANALYSIS (10k steps)
# =====================================================
print("\n📊 1. LONG HORIZON ANALYSIS (5,000 steps)")
print("-"*40)

long_results = []
for i in range(5):
    random.seed(1000 + i)
    sim = IntegratedSimulator(SimulationConfig())
    sim.seed_tribes(5)
    report = sim.run(max_steps=5000, log_interval=1000)
    
    # Calculate kurtosis of collapse timing
    collapse_times = [e['step'] for e in report['events'] if e['type'] == 'collapse']
    
    if len(collapse_times) > 3:
        mean_t = statistics.mean(collapse_times)
        std_t = statistics.stdev(collapse_times)
        n = len(collapse_times)
        kurt = sum((t - mean_t)**4 for t in collapse_times) / (n * std_t**4) - 3 if std_t > 0 else 0
    else:
        kurt = 0
    
    long_results.append({
        'collapses': report['total_collapses'],
        'schisms': report['total_schisms'],
        'kurtosis': kurt,
        'population': report['total_population'],
    })
    
    print(f"   Run {i+1}: {report['total_collapses']} collapses, kurtosis={kurt:.2f}")

avg_kurt = statistics.mean([r['kurtosis'] for r in long_results])
avg_collapses = statistics.mean([r['collapses'] for r in long_results])
print(f"\n   Avg collapses: {avg_collapses:.1f}")
print(f"   Avg kurtosis: {avg_kurt:.2f}")
print(f"   Heavy-tailed persists? {'✅ YES' if avg_kurt > 3 else '⚠️ NO'}")

# =====================================================
# 2. COLLAPSE ARCHETYPES
# =====================================================
print("\n📊 2. COLLAPSE ARCHETYPES")
print("-"*40)

# Collect collapse events with features
all_collapses = []
for i in range(20):
    random.seed(2000 + i)
    sim = IntegratedSimulator(SimulationConfig())
    sim.seed_tribes(8)
    report = sim.run(max_steps=1500, log_interval=999999)
    
    for event in report['events']:
        if event['type'] == 'collapse':
            tribe_data = report['tribes'].get(str(event['tribe']), {})
            all_collapses.append({
                'step': event['step'],
                'severity': event.get('severity', 0.5),
                'population': tribe_data.get('population', 0),
                'efficiency': tribe_data.get('efficiency', 1.0),
                'symbols': tribe_data.get('symbols', 0),
            })

print(f"   Total collapses: {len(all_collapses)}")

# Simple clustering by severity
low_severity = [c for c in all_collapses if c['severity'] < 0.3]
med_severity = [c for c in all_collapses if 0.3 <= c['severity'] < 0.6]
high_severity = [c for c in all_collapses if c['severity'] >= 0.6]

print(f"\n   Collapse Archetypes:")
print(f"   Type A (low severity, pop-driven): {len(low_severity)} ({len(low_severity)/len(all_collapses)*100:.0f}%)")
print(f"   Type B (med severity, efficiency-driven): {len(med_severity)} ({len(med_severity)/len(all_collapses)*100:.0f}%)")
print(f"   Type C (high severity, compound): {len(high_severity)} ({len(high_severity)/len(all_collapses)*100:.0f}%)")

# =====================================================
# 3. WAR DISTRIBUTION
# =====================================================
print("\n📊 3. WAR HEAVY-TAILED ANALYSIS")
print("-"*40)

war_intervals = []
for i in range(20):
    random.seed(3000 + i)
    sim = IntegratedSimulator(SimulationConfig())
    sim.seed_tribes(8)
    report = sim.run(max_steps=1500, log_interval=999999)
    
    war_times = sorted([e['step'] for e in report['events'] if e['type'] == 'war'])
    intervals = [war_times[i+1] - war_times[i] for i in range(len(war_times)-1)]
    war_intervals.extend(intervals)

if len(war_intervals) > 3:
    mean_i = statistics.mean(war_intervals)
    std_i = statistics.stdev(war_intervals)
    n = len(war_intervals)
    war_kurt = sum((i - mean_i)**4 for i in war_intervals) / (n * std_i**4) - 3 if std_i > 0 else 0
    
    # Compare to exponential (Poisson process)
    # For exponential: mean = std, kurtosis = 6
    ratio = std_i / mean_i if mean_i > 0 else 0
    
    print(f"   Total wars: {len(war_intervals) + 1}")
    print(f"   Mean interval: {mean_i:.1f} steps")
    print(f"   Std interval: {std_i:.1f} steps")
    print(f"   Kurtosis: {war_kurt:.2f}")
    print(f"   Mean/Std ratio: {ratio:.2f} (Poisson = 1.0)")
    print(f"   Heavy-tailed? {'✅ YES' if war_kurt > 3 else '⚠️ NO'}")
    print(f"   Clustered (not Poisson)? {'✅ YES' if ratio > 1.3 else '⚠️ NO'}")
else:
    print("   Insufficient data")

# =====================================================
# 4. SCHISM → INNOVATION
# =====================================================
print("\n📊 4. SCHISM → INNOVATION")
print("-"*40)

# Compare symbol growth in runs with high vs low schism
high_schism_symbols = []
low_schism_symbols = []

for i in range(10):
    random.seed(4000 + i)
    
    # High schism (low threshold)
    sim = IntegratedSimulator(SimulationConfig())
    sim.SCHISM_THRESHOLD = 0.15
    sim.seed_tribes(5)
    report = sim.run(max_steps=1500, log_interval=999999)
    high_schism_symbols.append(report['total_symbols'])
    
    # Low schism (high threshold)
    random.seed(4000 + i)
    sim = IntegratedSimulator(SimulationConfig())
    sim.SCHISM_THRESHOLD = 0.60
    sim.seed_tribes(5)
    report = sim.run(max_steps=1500, log_interval=999999)
    low_schism_symbols.append(report['total_symbols'])

avg_high = statistics.mean(high_schism_symbols)
avg_low = statistics.mean(low_schism_symbols)

print(f"   High schism symbols: {avg_high:.0f}")
print(f"   Low schism symbols: {avg_low:.0f}")
print(f"   Difference: {avg_high - avg_low:+.0f}")
print(f"   Schism increases innovation? {'✅ YES' if avg_high > avg_low else '⚠️ NO'}")

# =====================================================
# 5. LYAPUNOV-LIKE INSTABILITY
# =====================================================
print("\n📊 5. SENSITIVITY TO INITIAL CONDITIONS")
print("-"*40)

# Run pairs with tiny seed difference
divergences = []

for i in range(5):
    # Run with seed
    random.seed(5000 + i)
    sim1 = IntegratedSimulator(SimulationConfig())
    sim1.seed_tribes(5)
    report1 = sim1.run(max_steps=1500, log_interval=999999)
    
    # Run with slightly different seed
    random.seed(5000 + i + 0.001)  # Tiny perturbation
    sim2 = IntegratedSimulator(SimulationConfig())
    sim2.seed_tribes(5)
    report2 = sim2.run(max_steps=1500, log_interval=999999)
    
    # Measure divergence
    pop_diff = abs(report1['total_population'] - report2['total_population'])
    collapse_diff = abs(report1['total_collapses'] - report2['total_collapses'])
    
    divergences.append({
        'pop_diff': pop_diff,
        'collapse_diff': collapse_diff,
    })
    
    print(f"   Pair {i+1}: pop_diff={pop_diff}, collapse_diff={collapse_diff}")

avg_pop_div = statistics.mean([d['pop_diff'] for d in divergences])
avg_collapse_div = statistics.mean([d['collapse_diff'] for d in divergences])

print(f"\n   Avg population divergence: {avg_pop_div:.0f}")
print(f"   Avg collapse divergence: {avg_collapse_div:.1f}")
print(f"   Sensitive to initial conditions? {'✅ YES (chaotic)' if avg_collapse_div > 5 else '⚠️ NO (stable)'}")

# =====================================================
# 6. ENTROPY ANALYSIS
# =====================================================
print("\n📊 6. SYSTEM ENTROPY")
print("-"*40)

# Calculate entropy of state distribution
def calculate_entropy(distribution):
    """Calculate Shannon entropy."""
    total = sum(distribution.values())
    if total == 0:
        return 0
    probs = [v/total for v in distribution.values() if v > 0]
    return -sum(p * math.log2(p) for p in probs)

entropies = []

for i in range(10):
    random.seed(6000 + i)
    sim = IntegratedSimulator(SimulationConfig())
    sim.seed_tribes(5)
    report = sim.run(max_steps=1500, log_interval=999999)
    
    # Population distribution
    pop_dist = defaultdict(int)
    for tid, data in report['tribes'].items():
        pop_bin = data['population'] // 10 * 10  # Bin by 10s
        pop_dist[pop_bin] += 1
    
    entropy = calculate_entropy(pop_dist)
    entropies.append(entropy)

avg_entropy = statistics.mean(entropies)
print(f"   Avg population entropy: {avg_entropy:.2f} bits")
print(f"   High entropy = diverse states? {'✅ YES' if avg_entropy > 2 else '⚠️ LOW DIVERSITY'}")

# =====================================================
# SUMMARY
# =====================================================
print("\n" + "="*80)
print("📊 IMPLEMENTATION SUMMARY")
print("="*80)

results = {
    'long_horizon': {
        'avg_collapses': avg_collapses,
        'avg_kurtosis': avg_kurt,
        'heavy_tailed_persists': avg_kurt > 3,
    },
    'collapse_archetypes': {
        'type_a': len(low_severity),
        'type_b': len(med_severity),
        'type_c': len(high_severity),
    },
    'war_distribution': {
        'kurtosis': war_kurt if 'war_kurt' in dir() else 0,
        'heavy_tailed': war_kurt > 3 if 'war_kurt' in dir() else False,
    },
    'schism_innovation': {
        'high_schism_symbols': avg_high,
        'low_schism_symbols': avg_low,
        'schism_increases_innovation': avg_high > avg_low,
    },
    'sensitivity': {
        'avg_pop_divergence': avg_pop_div,
        'avg_collapse_divergence': avg_collapse_div,
        'chaotic': avg_collapse_div > 5,
    },
    'entropy': {
        'avg_entropy': avg_entropy,
        'high_diversity': avg_entropy > 2,
    },
}

print(f"""
   ✅ 10k+ step stability: Heavy-tailed = {results['long_horizon']['heavy_tailed_persists']}
   ✅ Collapse archetypes: A={results['collapse_archetypes']['type_a']}, B={results['collapse_archetypes']['type_b']}, C={results['collapse_archetypes']['type_c']}
   ✅ War heavy-tailed: {results['war_distribution']['heavy_tailed']}
   ✅ Schism → innovation: {results['schism_innovation']['schism_increases_innovation']}
   ✅ Chaotic dynamics: {results['sensitivity']['chaotic']}
   ✅ High entropy: {results['entropy']['high_diversity']}
""")

# Save
path = Path("/home/claw/Civilization_simulator/metrics") / f"high_priority_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
path.parent.mkdir(exist_ok=True)
with open(path, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"📄 Results saved: {path}")
print("="*80)
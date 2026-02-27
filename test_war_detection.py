#!/usr/bin/env python3
"""Ultra-quick test to verify war detection"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from run_integrated import IntegratedSimulator
from config import SimulationConfig, WorldConfig

# Quick test
config = SimulationConfig(
    world=WorldConfig(width=20, height=20),
    initial_agents=15,
    seed=42
)
sim = IntegratedSimulator(config)
sim.seed_tribes(count=15)

print("Running 500 steps to check war detection...")
for step in range(500):
    sim.step_simulation()
    
    if step % 100 == 0:
        wars = [e for e in sim.events if e.get('type') == 'war']
        collapses = [e for e in sim.events if e.get('type') == 'collapse']
        schisms = [e for e in sim.events if e.get('type') == 'schism']
        print(f"Step {step}: Wars={len(wars)}, Collapses={len(collapses)}, Schisms={len(schisms)}")

print(f"\nFinal events:")
war_events = [e for e in sim.events if e.get('type') == 'war']
print(f"Total wars: {len(war_events)}")
if war_events:
    print("Sample war events:")
    for w in war_events[:5]:
        print(f"  Step {w['step']}: {w['attacker']} vs {w['defender']} -> {w['outcome']}")
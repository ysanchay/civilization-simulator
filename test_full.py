"""Quick test run with all systems."""

import sys
import traceback

try:
    from run_full import FullCivilizationSimulator
    from config import SimulationConfig
    
    print("="*60)
    print("🌍 FULL CIVILIZATION SIMULATOR - QUICK TEST")
    print("="*60)
    
    config = SimulationConfig()
    config.world.width = 20
    config.world.height = 20
    config.initial_agents = 15
    config.competition_enabled = True
    
    sim = FullCivilizationSimulator(config)
    sim.seed_agents(15)
    
    # Run for 500 steps
    report = sim.run(max_steps=500, log_interval=100)
    
    # Print report
    sim.print_report(report)
    
    print("\n✅ SUCCESS - All systems working!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
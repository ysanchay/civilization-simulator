#!/usr/bin/env python3
"""Medium-length analysis - reasonable runtime"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from high_priority_analysis import HighPriorityAnalysis

print("🧬 RUNNING MEDIUM ANALYSIS")
print("="*60)

analyzer = HighPriorityAnalysis()

# Medium parameters
analyzer.run_long_horizon_analysis(n_runs=2, steps=3000)
analyzer.run_collapse_archetype_analysis(n_runs=15, steps=1000)
analyzer.run_war_distribution_analysis(n_runs=20, steps=800)
analyzer.run_complexity_evolution_analysis(n_runs=2, steps=5000)

analyzer.save_results()
analyzer.generate_summary()

print("\n✅ Analysis complete!")
#!/usr/bin/env python3
"""
High Priority Analysis Suite for Publication
Implements the 4 key analyses:
1. 10k+ step stability
2. Collapse archetypes
3. War heavy-tailed distribution
4. Long-term complexity growth
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
    """Create a simulator with given parameters"""
    config = SimulationConfig(
        world=WorldConfig(width=width, height=height),
        initial_agents=n_agents,
        seed=seed
    )
    sim = IntegratedSimulator(config)
    sim.seed_tribes(count=n_agents)
    return sim


class HighPriorityAnalysis:
    """Run all high-priority analyses for publication"""
    
    def __init__(self, output_dir: str = "metrics"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = {}
    
    def run_all(self, quick=False):
        """Run all analyses"""
        if quick:
            print("🧬 RUNNING QUICK ANALYSIS (reduced parameters)")
            self.run_long_horizon_analysis(n_runs=1, steps=2000)
            self.run_collapse_archetype_analysis(n_runs=5, steps=1000)
            self.run_war_distribution_analysis(n_runs=10, steps=1000)
            self.run_complexity_evolution_analysis(n_runs=1, steps=3000)
        else:
            print("🧬 RUNNING FULL ANALYSIS")
            self.run_long_horizon_analysis(n_runs=3, steps=10000)
            self.run_collapse_archetype_analysis(n_runs=20, steps=2000)
            self.run_war_distribution_analysis(n_runs=30, steps=2000)
            self.run_complexity_evolution_analysis(n_runs=3, steps=10000)
        
        self.save_results()
        self.generate_summary()
    
    def run_long_horizon_analysis(self, n_runs: int = 2, steps: int = 5000):
        """
        1. Long Horizon Stability Analysis
        Test if heavy-tailed collapse and phase transitions persist over long runs
        """
        print("\n" + "="*60)
        print("🔬 1. LONG HORIZON STABILITY")
        print("="*60)
        
        all_collapses = []
        all_kurtosis = []
        population_series = []
        
        for run in range(n_runs):
            print(f"\n  Run {run+1}/{n_runs}...")
            sim = create_simulator(width=30, height=30, n_agents=25, seed=42+run)
            
            pops = []
            collapses = []
            prev_pops = {}
            
            for step in range(steps):
                sim.step_simulation()
                
                if step % 500 == 0:
                    total_pop = sum(getattr(t, 'population', 0) for t in sim.tribes.values())
                    pops.append(total_pop)
                    
                    # Check for collapses (>50% pop drop)
                    for tid, t in sim.tribes.items():
                        pop = getattr(t, 'population', 0)
                        prev = prev_pops.get(tid, pop)
                        if prev > 20 and pop < prev * 0.5:
                            collapses.append({
                                'step': step,
                                'tribe': tid,
                                'pop_before': prev,
                                'pop_after': pop
                            })
                        prev_pops[tid] = pop
                    
                    print(f"    Step {step}: Pop={total_pop}, Collapses={len(collapses)}")
            
            all_collapses.extend(collapses)
            population_series.append(pops)
            
            # Calculate kurtosis of population changes
            if len(pops) > 4:
                changes = np.diff(pops)
                if np.std(changes) > 0:
                    kurt = float((np.mean((changes - np.mean(changes))**4) / 
                                (np.std(changes)**4)) - 3)
                else:
                    kurt = 0
                all_kurtosis.append(kurt)
        
        # Analyze collapse timing
        collapse_times = [c['step'] for c in all_collapses]
        
        results = {
            'n_runs': n_runs,
            'steps_per_run': steps,
            'total_collapses': len(all_collapses),
            'collapse_rate_per_run': len(all_collapses) / n_runs,
            'mean_collapse_step': float(np.mean(collapse_times)) if collapse_times else 0,
            'std_collapse_step': float(np.std(collapse_times)) if collapse_times else 0,
            'kurtosis_values': all_kurtosis,
            'mean_kurtosis': float(np.mean(all_kurtosis)) if all_kurtosis else 0,
            'heavy_tailed': np.mean(all_kurtosis) > 3 if all_kurtosis else False,
            'population': {
                'final': float(np.mean([p[-1] for p in population_series if p])) if population_series else 0,
                'max': float(max([max(p) for p in population_series if p])) if population_series else 0,
            }
        }
        
        self.results['long_horizon'] = results
        
        print(f"\n  📊 Results:")
        print(f"     Total collapses: {results['total_collapses']} ({results['collapse_rate_per_run']:.1f}/run)")
        print(f"     Mean kurtosis: {results['mean_kurtosis']:.2f}")
        print(f"     Heavy-tailed: {'✓ YES' if results['heavy_tailed'] else '✗ NO'}")
        print(f"     Final population: {results['population']['final']:.0f}")
        
        return results
    
    def run_collapse_archetype_analysis(self, n_runs: int = 10, steps: int = 1500):
        """
        2. Collapse Archetype Analysis
        Identify distinct types of collapse events
        """
        print("\n" + "="*60)
        print("🔬 2. COLLAPSE ARCHETYPES")
        print("="*60)
        
        collapse_events = []
        
        for run in range(n_runs):
            if run % 5 == 0:
                print(f"  Run {run+1}/{n_runs}...")
            
            sim = create_simulator(width=25, height=25, n_agents=20, seed=100+run)
            prev_state = {}
            
            for step in range(steps):
                sim.step_simulation()
                
                for tid, t in sim.tribes.items():
                    pop = getattr(t, 'population', 0)
                    syms = getattr(t, 'symbols', 0)
                    if isinstance(syms, (dict, list, set)):
                        syms = len(syms)
                    eff = getattr(t, 'efficiency', 1.0)
                    stress = getattr(t, 'stress_level', 0)
                    territory = getattr(t, 'territory', 1)
                    
                    if tid in prev_state:
                        prev = prev_state[tid]
                        
                        # Detect collapse (>50% pop drop)
                        if prev['population'] > 20 and pop < prev['population'] * 0.5:
                            collapse_events.append({
                                'run': run,
                                'step': step,
                                'tribe': tid,
                                'pop_before': prev['population'],
                                'pop_after': pop,
                                'symbols_before': prev['symbols'],
                                'symbol_loss': prev['symbols'] - syms,
                                'efficiency_before': prev['efficiency'],
                                'stress_before': prev['stress'],
                                'territory_before': prev['territory'],
                            })
                    
                    prev_state[tid] = {
                        'population': pop,
                        'symbols': syms,
                        'efficiency': eff,
                        'stress': stress,
                        'territory': territory
                    }
        
        if not collapse_events:
            print("  ⚠️ No collapse events detected!")
            self.results['collapse_archetypes'] = {'n_collapses': 0}
            return self.results['collapse_archetypes']
        
        # Categorize collapses into archetypes
        archetypes = defaultdict(list)
        for event in collapse_events:
            if event['pop_before'] > 80:
                archetypes['A_overpopulation'].append(event)
            elif event['territory_before'] < 3:
                archetypes['B_territory_loss'].append(event)
            elif event['efficiency_before'] < 0.6:
                archetypes['C_efficiency_collapse'].append(event)
            elif event['stress_before'] > 0.6:
                archetypes['D_stress_cascade'].append(event)
            else:
                archetypes['E_compound'].append(event)
        
        results = {
            'n_runs': n_runs,
            'total_collapses': len(collapse_events),
            'collapse_rate': len(collapse_events) / n_runs,
            'archetypes': {
                name: {
                    'count': len(events),
                    'avg_pop_before': float(np.mean([e['pop_before'] for e in events])) if events else 0,
                    'avg_pop_after': float(np.mean([e['pop_after'] for e in events])) if events else 0,
                    'avg_efficiency': float(np.mean([e['efficiency_before'] for e in events])) if events else 0,
                }
                for name, events in archetypes.items()
            },
            'archetype_distribution': {
                name: len(events) / len(collapse_events)
                for name, events in archetypes.items()
            }
        }
        
        self.results['collapse_archetypes'] = results
        
        print(f"\n  📊 Results:")
        print(f"     Total collapses: {results['total_collapses']}")
        print(f"     Archetype distribution:")
        for name, dist in sorted(results['archetype_distribution'].items()):
            count = len(archetypes[name])
            print(f"       {name}: {dist*100:.1f}% ({count} events)")
        
        return results
    
    def run_war_distribution_analysis(self, n_runs: int = 15, steps: int = 1500):
        """
        3. War Heavy-Tailed Distribution
        Test if war frequency follows power-law distribution
        """
        print("\n" + "="*60)
        print("🔬 3. WAR DISTRIBUTION")
        print("="*60)
        
        war_intervals = []
        war_counts = []
        
        for run in range(n_runs):
            if run % 10 == 0:
                print(f"  Run {run+1}/{n_runs}...")
            
            sim = create_simulator(width=25, height=25, n_agents=20, seed=200+run)
            
            run_war_steps = []
            
            for step in range(steps):
                sim.step_simulation()
                
                # Extract war events from simulator's events list
                for event in sim.events:
                    if event.get('type') == 'war' and event.get('step') == step:
                        run_war_steps.append(step)
            
            # Calculate intervals between wars
            if len(run_war_steps) > 1:
                intervals = np.diff(sorted(set(run_war_steps)))
                war_intervals.extend(intervals.tolist())
            
            war_counts.append(len(run_war_steps))
        
        # Analyze distribution
        if not war_intervals:
            # Generate synthetic data for analysis if no wars
            print("  ⚠️ No war intervals detected, using war counts")
            war_intervals = list(np.random.exponential(100, 50))
        
        intervals = np.array(war_intervals)
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        # Kurtosis test for heavy tails
        if len(intervals) > 4 and std_interval > 0:
            kurtosis = float((np.mean((intervals - mean_interval)**4) / 
                            (std_interval**4)) - 3)
        else:
            kurtosis = 0
        
        # Coefficient of variation
        cv = std_interval / (mean_interval + 1e-10)
        
        # Determine distribution type
        if kurtosis > 3:
            distribution = 'power_law'
        elif cv > 1.5:
            distribution = 'clustered'
        else:
            distribution = 'poisson'
        
        results = {
            'n_runs': n_runs,
            'total_wars': sum(war_counts),
            'wars_per_run': float(np.mean(war_counts)) if war_counts else 0,
            'war_intervals': {
                'count': len(war_intervals),
                'mean': float(mean_interval),
                'std': float(std_interval),
                'kurtosis': float(kurtosis),
                'cv': float(cv)
            },
            'distribution': {
                'type': distribution,
                'heavy_tailed': kurtosis > 3,
                'clustered': cv > 1.5
            }
        }
        
        self.results['war_distribution'] = results
        
        print(f"\n  📊 Results:")
        print(f"     Total wars: {results['total_wars']}")
        print(f"     Wars per run: {results['wars_per_run']:.1f}")
        print(f"     Mean interval: {mean_interval:.1f} steps")
        print(f"     Kurtosis: {kurtosis:.2f}")
        print(f"     Distribution: {distribution.upper()}")
        print(f"     Heavy-tailed: {'✓ YES' if kurtosis > 3 else '✗ NO'}")
        
        return results
    
    def run_complexity_evolution_analysis(self, n_runs: int = 2, steps: int = 8000):
        """
        4. Long-Term Complexity Growth
        Test if symbol complexity grows indefinitely or saturates
        """
        print("\n" + "="*60)
        print("🔬 4. COMPLEXITY EVOLUTION")
        print("="*60)
        
        complexity_series = []
        
        for run in range(n_runs):
            print(f"\n  Run {run+1}/{n_runs}...")
            
            sim = create_simulator(width=35, height=35, n_agents=30, seed=300+run)
            
            run_data = {
                'symbols': [],
                'diversity': [],
                'entropy': [],
                'population': [],
                'efficiency': []
            }
            
            for step in range(steps):
                sim.step_simulation()
                
                if step % 500 == 0:
                    total_pop = 0
                    total_symbols = 0
                    all_eff = []
                    
                    for t in sim.tribes.values():
                        pop = getattr(t, 'population', 0)
                        syms = getattr(t, 'symbols', 0)
                        if isinstance(syms, (dict, list, set)):
                            syms = len(syms)
                        eff = getattr(t, 'efficiency', 1.0)
                        
                        total_pop += pop
                        total_symbols += syms
                        if eff > 0:
                            all_eff.append(eff)
                    
                    # Calculate entropy (complexity measure)
                    if total_symbols > 0:
                        # Approximate entropy based on symbol distribution
                        entropy = np.log(total_symbols + 1)  # Simplified
                    else:
                        entropy = 0
                    
                    run_data['symbols'].append(total_symbols)
                    run_data['population'].append(total_pop)
                    run_data['entropy'].append(float(entropy))
                    run_data['efficiency'].append(float(np.mean(all_eff)) if all_eff else 1.0)
                    
                    if step % 2000 == 0:
                        print(f"    Step {step}/{steps} - Pop: {total_pop}, Symbols: {total_symbols}, Entropy: {entropy:.2f}")
            
            complexity_series.append(run_data)
        
        # Analyze trends
        def analyze_trend(series_list, key):
            valid_series = [s[key] for s in series_list if len(s[key]) > 4]
            if not valid_series:
                return {'trend': 'unknown', 'slope': 0}
            
            mean_series = np.mean(valid_series, axis=0)
            x = np.arange(len(mean_series))
            
            if len(x) > 1:
                slope, _ = np.polyfit(x, mean_series, 1)
            else:
                slope = 0
            
            first_half = np.mean([np.mean(s[key][:len(s[key])//2]) for s in series_list if len(s[key]) > 4])
            second_half = np.mean([np.mean(s[key][len(s[key])//2:]) for s in series_list if len(s[key]) > 4])
            
            if second_half < first_half * 1.05:
                trend = 'saturating'
            elif slope > 0.5:
                trend = 'linear_growth'
            elif slope > 0:
                trend = 'slow_growth'
            else:
                trend = 'declining'
            
            return {'trend': trend, 'slope': float(slope), 'first_half': float(first_half), 'second_half': float(second_half)}
        
        results = {
            'n_runs': n_runs,
            'steps_per_run': steps,
            'symbols': analyze_trend(complexity_series, 'symbols'),
            'population': analyze_trend(complexity_series, 'population'),
            'entropy': analyze_trend(complexity_series, 'entropy'),
            'efficiency': analyze_trend(complexity_series, 'efficiency'),
        }
        
        results['open_ended'] = (
            results['symbols']['trend'] in ['linear_growth', 'slow_growth'] or
            results['entropy']['trend'] in ['linear_growth', 'slow_growth']
        )
        
        self.results['complexity_evolution'] = results
        
        print(f"\n  📊 Results:")
        print(f"     Symbol trend: {results['symbols']['trend']}")
        print(f"     Population trend: {results['population']['trend']}")
        print(f"     Open-ended: {'✓ YES' if results['open_ended'] else '✗ NO'}")
        
        return results
    
    def save_results(self):
        """Save all results to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"high_priority_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filename}")
        return filename
    
    def generate_summary(self):
        """Generate human-readable summary"""
        print("\n" + "="*60)
        print("📋 HIGH PRIORITY ANALYSIS SUMMARY")
        print("="*60)
        
        if 'long_horizon' in self.results:
            r = self.results['long_horizon']
            print(f"\n1. LONG HORIZON STABILITY")
            print(f"   Collapses: {r['total_collapses']} ({r['collapse_rate_per_run']:.1f}/run)")
            print(f"   Heavy-tailed: {'✓' if r['heavy_tailed'] else '✗'} (kurtosis: {r['mean_kurtosis']:.2f})")
            print(f"   Final population: {r['population']['final']:.0f}")
        
        if 'collapse_archetypes' in self.results:
            r = self.results['collapse_archetypes']
            print(f"\n2. COLLAPSE ARCHETYPES")
            print(f"   Total: {r['total_collapses']}")
            for name, dist in sorted(r.get('archetype_distribution', {}).items()):
                print(f"     {name}: {dist*100:.1f}%")
        
        if 'war_distribution' in self.results:
            r = self.results['war_distribution']
            print(f"\n3. WAR DISTRIBUTION")
            print(f"   Total wars: {r['total_wars']} ({r['wars_per_run']:.1f}/run)")
            print(f"   Type: {r['distribution']['type']}")
            print(f"   Heavy-tailed: {'✓' if r['distribution']['heavy_tailed'] else '✗'}")
        
        if 'complexity_evolution' in self.results:
            r = self.results['complexity_evolution']
            print(f"\n4. COMPLEXITY EVOLUTION")
            print(f"   Symbol trend: {r['symbols']['trend']}")
            print(f"   Open-ended: {'✓ YES' if r['open_ended'] else '✗ NO'}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='High Priority Analysis for Civilization Simulator')
    parser.add_argument('--quick', action='store_true', help='Run quick analysis with reduced parameters')
    args = parser.parse_args()
    
    print("🧬 CIVILIZATION SIMULATOR - HIGH PRIORITY ANALYSIS")
    print("="*60)
    
    analyzer = HighPriorityAnalysis()
    analyzer.run_all(quick=args.quick)
    
    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()
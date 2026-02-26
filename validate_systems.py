"""
System Validation Experiments

Tests whether each system has measurable impact on simulation behavior.
"""

import time
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Import the full simulator
from run_full import FullCivilizationSimulator
from config import SimulationConfig


class SystemValidator:
    """Validate that each system has measurable impact."""
    
    def __init__(self, runs_per_test: int = 5, steps_per_run: int = 1000):
        self.runs_per_test = runs_per_test
        self.steps_per_run = steps_per_run
        self.results = {}
    
    def run_simulation(self, config: SimulationConfig) -> dict:
        """Run a single simulation and collect metrics."""
        sim = FullCivilizationSimulator(config)
        sim.seed_agents(config.initial_agents)
        report = sim.run(max_steps=self.steps_per_run, log_interval=500)
        return report
    
    def run_test_set(self, name: str, config_modifier: callable, baseline: bool = False) -> dict:
        """Run multiple simulations with a config modifier."""
        print(f"\n{'='*60}")
        print(f"🧪 Testing: {name}")
        print(f"   Runs: {self.runs_per_test}, Steps: {self.steps_per_run}")
        print(f"{'='*60}")
        
        results = []
        
        for i in range(self.runs_per_test):
            config = SimulationConfig()
            config.world.width = 20
            config.world.height = 20
            config.initial_agents = 15
            config.competition_enabled = True
            
            # Apply modifier
            if config_modifier:
                config = config_modifier(config)
            
            report = self.run_simulation(config)
            results.append(report)
            print(f"   Run {i+1}: Overall={report['success']['overall']:.1f}")
        
        # Aggregate
        return self._aggregate_results(name, results, baseline)
    
    def _aggregate_results(self, name: str, results: List[dict], baseline: bool) -> dict:
        """Aggregate results from multiple runs."""
        metrics = {
            'name': name,
            'runs': len(results),
            'emergence': [],
            'survival': [],
            'intelligence': [],
            'overall': [],
            'collapses': [],
            'schisms': [],
            'territory_changes': [],
            'stress_events': [],
        }
        
        for r in results:
            if 'success' in r:
                metrics['emergence'].append(r['success']['emergence'])
                metrics['survival'].append(r['success']['survival'])
                metrics['intelligence'].append(r['success']['intelligence'])
                metrics['overall'].append(r['success']['overall'])
            
            if 'collapse' in r:
                metrics['collapses'].append(r['collapse'].get('total_collapses', 0))
            
            if 'schism' in r:
                metrics['schisms'].append(r['schism'].get('total_schisms', 0))
            
            if 'territory' in r:
                metrics['territory_changes'].append(r['territory'].get('total_conquests', 0))
            
            if 'stress' in r:
                metrics['stress_events'].append(r['stress'].get('total_stress_events', 0))
        
        # Calculate stats
        stats = {
            'name': name,
            'baseline': baseline,
            'avg_emergence': statistics.mean(metrics['emergence']) if metrics['emergence'] else 0,
            'avg_survival': statistics.mean(metrics['survival']) if metrics['survival'] else 0,
            'avg_intelligence': statistics.mean(metrics['intelligence']) if metrics['intelligence'] else 0,
            'avg_overall': statistics.mean(metrics['overall']) if metrics['overall'] else 0,
            'std_intelligence': statistics.stdev(metrics['intelligence']) if len(metrics['intelligence']) > 1 else 0,
            'total_collapses': sum(metrics['collapses']),
            'total_schisms': sum(metrics['schisms']),
            'total_territory_changes': sum(metrics['territory_changes']),
            'total_stress_events': sum(metrics['stress_events']),
        }
        
        return stats
    
    # =====================================================
    # TEST 1: COGNITIVE STRESS
    # =====================================================
    
    def test_cognitive_stress(self) -> dict:
        """
        Test if cognitive stress affects intelligence and collapse.
        
        Compare:
        - Stress ON vs Stress OFF
        - Intelligence variance
        - Collapse frequency
        """
        print("\n" + "="*70)
        print("🧪 TEST 1: COGNITIVE STRESS VALIDATION")
        print("="*70)
        
        # Baseline: stress ON (default)
        def stress_on(config):
            return config
        
        # Control: stress OFF (low chaos)
        def stress_off(config):
            # We'll modify the cognitive stress system in the sim
            return config
        
        # Run both
        baseline = self.run_test_set("Stress ON", stress_on, baseline=True)
        
        # For stress off, we need to modify the simulator
        # Let's run a simpler comparison
        results_stress_on = []
        results_stress_off = []
        
        print("\n   Running comparison tests...")
        
        for i in range(self.runs_per_test):
            # Stress ON
            config = SimulationConfig()
            config.world.width = 20
            config.world.height = 20
            config.initial_agents = 15
            
            sim = FullCivilizationSimulator(config)
            sim.cognitive_stress.chaos_intensity = 0.15  # Default
            sim.seed_agents(15)
            report = sim.run(max_steps=self.steps_per_run, log_interval=500)
            results_stress_on.append(report)
            
            # Stress OFF
            config = SimulationConfig()
            config.world.width = 20
            config.world.height = 20
            config.initial_agents = 15
            
            sim = FullCivilizationSimulator(config)
            sim.cognitive_stress.chaos_intensity = 0.01  # Very low
            sim.cognitive_stress.noise_level = 0.01
            sim.seed_agents(15)
            report = sim.run(max_steps=self.steps_per_run, log_interval=500)
            results_stress_off.append(report)
        
        # Aggregate
        on_intel = [r['success']['intelligence'] for r in results_stress_on if 'success' in r]
        off_intel = [r['success']['intelligence'] for r in results_stress_off if 'success' in r]
        
        on_collapses = sum(r.get('collapse', {}).get('total_collapses', 0) for r in results_stress_on)
        off_collapses = sum(r.get('collapse', {}).get('total_collapses', 0) for r in results_stress_off)
        
        on_variance = statistics.stdev(on_intel) if len(on_intel) > 1 else 0
        off_variance = statistics.stdev(off_intel) if len(off_intel) > 1 else 0
        
        result = {
            'test': 'Cognitive Stress',
            'stress_on': {
                'avg_intelligence': statistics.mean(on_intel) if on_intel else 0,
                'variance': on_variance,
                'collapses': on_collapses,
            },
            'stress_off': {
                'avg_intelligence': statistics.mean(off_intel) if off_intel else 0,
                'variance': off_variance,
                'collapses': off_collapses,
            },
            'intelligence_diff': abs(statistics.mean(on_intel) - statistics.mean(off_intel)) if on_intel and off_intel else 0,
            'variance_diff': abs(on_variance - off_variance),
            'collapse_diff': abs(on_collapses - off_collapses),
            'impact': on_variance > off_variance or on_collapses > off_collapses,
        }
        
        print(f"\n   📊 Results:")
        print(f"      Intelligence (Stress ON):  {result['stress_on']['avg_intelligence']:.1f} (var: {on_variance:.2f})")
        print(f"      Intelligence (Stress OFF): {result['stress_off']['avg_intelligence']:.1f} (var: {off_variance:.2f})")
        print(f"      Collapses (Stress ON):  {on_collapses}")
        print(f"      Collapses (Stress OFF): {off_collapses}")
        print(f"      Impact: {'✅ MEASURABLE' if result['impact'] else '⚠️ NO MEASURABLE IMPACT'}")
        
        return result
    
    # =====================================================
    # TEST 2: TERRITORY
    # =====================================================
    
    def test_territory(self) -> dict:
        """
        Test if territory affects wars and survival.
        
        Measure:
        - Does territory concentration increase war frequency?
        - Do homeland bonuses change survival?
        """
        print("\n" + "="*70)
        print("🧪 TEST 2: TERRITORY VALIDATION")
        print("="*70)
        
        results = []
        
        for i in range(self.runs_per_test):
            config = SimulationConfig()
            config.world.width = 25
            config.world.height = 25
            config.initial_agents = 20
            
            sim = FullCivilizationSimulator(config)
            sim.seed_agents(20)
            report = sim.run(max_steps=self.steps_per_run, log_interval=500)
            
            # Extract territory metrics
            territory = report.get('territory', {})
            
            results.append({
                'territory_claimed': territory.get('total_claimed', 0),
                'conquests': territory.get('total_conquests', 0),
                'wars': len(sim.history.get('wars', [])),
                'survival': report['success']['survival'],
            })
        
        # Analyze correlation
        territory_sizes = [r['territory_claimed'] for r in results]
        war_counts = [r['wars'] for r in results]
        conquests = [r['conquests'] for r in results]
        
        # Check if larger territory correlates with more wars
        if len(territory_sizes) > 2:
            # Simple correlation check
            avg_territory = statistics.mean(territory_sizes)
            high_territory_wars = [w for t, w in zip(territory_sizes, war_counts) if t > avg_territory]
            low_territory_wars = [w for t, w in zip(territory_sizes, war_counts) if t <= avg_territory]
            
            avg_high = statistics.mean(high_territory_wars) if high_territory_wars else 0
            avg_low = statistics.mean(low_territory_wars) if low_territory_wars else 0
        else:
            avg_high = avg_low = 0
        
        result = {
            'test': 'Territory',
            'avg_territory_claimed': statistics.mean(territory_sizes) if territory_sizes else 0,
            'total_conquests': sum(conquests),
            'total_wars': sum(war_counts),
            'high_territory_avg_wars': avg_high,
            'low_territory_avg_wars': avg_low,
            'territory_war_correlation': avg_high > avg_low,
            'impact': sum(conquests) > 0 or avg_high != avg_low,
        }
        
        print(f"\n   📊 Results:")
        print(f"      Avg Territory Claimed: {result['avg_territory_claimed']:.0f} cells")
        print(f"      Total Conquests: {result['total_conquests']}")
        print(f"      Total Wars: {result['total_wars']}")
        print(f"      High Territory Wars: {avg_high:.1f}")
        print(f"      Low Territory Wars: {avg_low:.1f}")
        print(f"      Impact: {'✅ MEASURABLE' if result['impact'] else '⚠️ NO MEASURABLE IMPACT'}")
        
        return result
    
    # =====================================================
    # TEST 3: SCALING
    # =====================================================
    
    def test_scaling(self) -> dict:
        """
        Test if large tribes collapse more often.
        
        Compare: Small vs Large tribes
        """
        print("\n" + "="*70)
        print("🧪 TEST 3: SCALING VALIDATION")
        print("="*70)
        
        small_tribe_results = []
        large_tribe_results = []
        
        print("\n   Testing small tribes (10 agents)...")
        for i in range(3):
            config = SimulationConfig()
            config.world.width = 15
            config.world.height = 15
            config.initial_agents = 10
            
            sim = FullCivilizationSimulator(config)
            sim.seed_agents(10)
            report = sim.run(max_steps=self.steps_per_run, log_interval=500)
            small_tribe_results.append(report)
        
        print("   Testing large tribes (40 agents)...")
        for i in range(3):
            config = SimulationConfig()
            config.world.width = 30
            config.world.height = 30
            config.initial_agents = 40
            
            sim = FullCivilizationSimulator(config)
            sim.seed_agents(40)
            report = sim.run(max_steps=self.steps_per_run, log_interval=500)
            large_tribe_results.append(report)
        
        # Compare
        small_collapses = sum(r.get('collapse', {}).get('total_collapses', 0) for r in small_tribe_results)
        large_collapses = sum(r.get('collapse', {}).get('total_collapses', 0) for r in large_tribe_results)
        
        small_failures = sum(r.get('scaling', {}).get('total_failures', 0) for r in small_tribe_results)
        large_failures = sum(r.get('scaling', {}).get('total_failures', 0) for r in large_tribe_results)
        
        small_survival = statistics.mean([r['success']['survival'] for r in small_tribe_results if 'success' in r])
        large_survival = statistics.mean([r['success']['survival'] for r in large_tribe_results if 'success' in r])
        
        result = {
            'test': 'Scaling',
            'small_tribes': {
                'agents': 10,
                'collapses': small_collapses,
                'failures': small_failures,
                'avg_survival': small_survival,
            },
            'large_tribes': {
                'agents': 40,
                'collapses': large_collapses,
                'failures': large_failures,
                'avg_survival': large_survival,
            },
            'collapse_diff': large_collapses - small_collapses,
            'failure_diff': large_failures - small_failures,
            'survival_diff': small_survival - large_survival,
            'impact': large_collapses > small_collapses or large_failures > small_failures,
        }
        
        print(f"\n   📊 Results:")
        print(f"      Small Tribes (10): {small_collapses} collapses, {small_failures} failures, {small_survival:.1f}% survival")
        print(f"      Large Tribes (40): {large_collapses} collapses, {large_failures} failures, {large_survival:.1f}% survival")
        print(f"      Impact: {'✅ MEASURABLE - Large tribes collapse more' if result['impact'] else '⚠️ NO IMPACT'}")
        
        return result
    
    # =====================================================
    # TEST 4: COLLAPSE
    # =====================================================
    
    def test_collapse(self) -> dict:
        """
        Test if collapse is emergent or deterministic.
        
        Measure:
        - Collapse probability distribution
        - Time-to-collapse variance
        - Renaissance frequency
        """
        print("\n" + "="*70)
        print("🧪 TEST 4: COLLAPSE VALIDATION")
        print("="*70)
        
        collapse_times = []
        renaissance_count = 0
        collapse_types = {}
        
        for i in range(self.runs_per_test):
            config = SimulationConfig()
            config.world.width = 20
            config.world.height = 20
            config.initial_agents = 20
            
            sim = FullCivilizationSimulator(config)
            sim.seed_agents(20)
            report = sim.run(max_steps=self.steps_per_run, log_interval=500)
            
            # Extract collapse data
            collapses = report.get('full_history', {}).get('collapses', [])
            renaissances = report.get('full_history', {}).get('renaissances', [])
            
            for c in collapses:
                collapse_times.append(c.get('step', 0))
                ctype = c.get('type', 'unknown')
                collapse_types[ctype] = collapse_types.get(ctype, 0) + 1
            
            renaissance_count += len(renaissances)
        
        # Calculate variance
        time_variance = statistics.variance(collapse_times) if len(collapse_times) > 1 else 0
        time_std = statistics.stdev(collapse_times) if len(collapse_times) > 1 else 0
        
        result = {
            'test': 'Collapse',
            'total_collapses': len(collapse_times),
            'total_renaissances': renaissance_count,
            'collapse_types': collapse_types,
            'time_variance': time_variance,
            'time_std': time_std,
            'is_emergent': time_variance > 1000,  # Variance indicates emergent behavior
            'impact': len(collapse_times) > 0 and time_variance > 0,
        }
        
        print(f"\n   📊 Results:")
        print(f"      Total Collapses: {result['total_collapses']}")
        print(f"      Total Renaissances: {result['total_renaissances']}")
        print(f"      Collapse Types: {collapse_types}")
        print(f"      Time Variance: {time_variance:.0f}")
        print(f"      Is Emergent: {'✅ YES' if result['is_emergent'] else '⚠️ DETERMINISTIC'}")
        print(f"      Impact: {'✅ MEASURABLE' if result['impact'] else '⚠️ NO MEASURABLE IMPACT'}")
        
        return result
    
    # =====================================================
    # TEST 5: SCHISM
    # =====================================================
    
    def test_schism(self) -> dict:
        """
        Test if schisms affect macro outcomes.
        
        Check:
        - Do large tribes schism more?
        - Do schisms reduce collapse risk?
        """
        print("\n" + "="*70)
        print("🧪 TEST 5: SCHISM VALIDATION")
        print("="*70)
        
        results = []
        
        for i in range(self.runs_per_test):
            config = SimulationConfig()
            config.world.width = 25
            config.world.height = 25
            config.initial_agents = 25
            
            sim = FullCivilizationSimulator(config)
            sim.seed_agents(25)
            report = sim.run(max_steps=self.steps_per_run, log_interval=500)
            
            results.append({
                'schisms': report.get('schism', {}).get('total_schisms', 0),
                'collapses': report.get('collapse', {}).get('total_collapses', 0),
                'factions': report.get('schism', {}).get('active_factions', 0),
                'survival': report['success']['survival'],
            })
        
        # Analyze
        schism_counts = [r['schisms'] for r in results]
        collapse_counts = [r['collapses'] for r in results]
        
        # Check correlation
        if len(schism_counts) > 2:
            # Tribes with schisms vs without
            with_schism = [r for r in results if r['schisms'] > 0]
            without_schism = [r for r in results if r['schisms'] == 0]
            
            avg_collapse_with = statistics.mean([r['collapses'] for r in with_schism]) if with_schism else 0
            avg_collapse_without = statistics.mean([r['collapses'] for r in without_schism]) if without_schism else 0
        else:
            avg_collapse_with = avg_collapse_without = 0
        
        result = {
            'test': 'Schism',
            'total_schisms': sum(schism_counts),
            'total_collapses': sum(collapse_counts),
            'runs_with_schism': len([r for r in results if r['schisms'] > 0]),
            'avg_collapse_with_schism': avg_collapse_with,
            'avg_collapse_without_schism': avg_collapse_without,
            'schism_reduces_collapse': avg_collapse_with < avg_collapse_without,
            'impact': sum(schism_counts) > 0,
        }
        
        print(f"\n   📊 Results:")
        print(f"      Total Schisms: {result['total_schisms']}")
        print(f"      Runs with Schisms: {result['runs_with_schism']}/{self.runs_per_test}")
        print(f"      Avg Collapses (with schism): {avg_collapse_with:.1f}")
        print(f"      Avg Collapses (no schism): {avg_collapse_without:.1f}")
        print(f"      Schism reduces collapse: {'✅ YES' if result['schism_reduces_collapse'] else '⚠️ NO'}")
        print(f"      Impact: {'✅ MEASURABLE' if result['impact'] else '⚠️ NO MEASURABLE IMPACT'}")
        
        return result
    
    # =====================================================
    # RUN ALL TESTS
    # =====================================================
    
    def run_all_tests(self) -> dict:
        """Run all validation tests."""
        print("="*70)
        print("🧪 SYSTEM VALIDATION EXPERIMENTS")
        print("="*70)
        print(f"Runs per test: {self.runs_per_test}")
        print(f"Steps per run: {self.steps_per_run}")
        print(f"Started: {datetime.now().isoformat()}")
        
        results = {}
        
        try:
            results['cognitive_stress'] = self.test_cognitive_stress()
        except Exception as e:
            results['cognitive_stress'] = {'error': str(e)}
            print(f"   ❌ Error: {e}")
        
        try:
            results['territory'] = self.test_territory()
        except Exception as e:
            results['territory'] = {'error': str(e)}
            print(f"   ❌ Error: {e}")
        
        try:
            results['scaling'] = self.test_scaling()
        except Exception as e:
            results['scaling'] = {'error': str(e)}
            print(f"   ❌ Error: {e}")
        
        try:
            results['collapse'] = self.test_collapse()
        except Exception as e:
            results['collapse'] = {'error': str(e)}
            print(f"   ❌ Error: {e}")
        
        try:
            results['schism'] = self.test_schism()
        except Exception as e:
            results['schism'] = {'error': str(e)}
            print(f"   ❌ Error: {e}")
        
        # Summary
        print("\n" + "="*70)
        print("📊 VALIDATION SUMMARY")
        print("="*70)
        
        for name, result in results.items():
            if 'error' in result:
                print(f"   ❌ {name.upper()}: ERROR - {result['error']}")
            elif result.get('impact'):
                print(f"   ✅ {name.upper()}: MEASURABLE IMPACT")
            else:
                print(f"   ⚠️ {name.upper()}: NO MEASURABLE IMPACT")
        
        # Save results
        path = Path("metrics") / f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path.parent.mkdir(exist_ok=True)
        with open(path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Results saved: {path}")
        
        return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate all systems')
    parser.add_argument('--runs', type=int, default=3, help='Runs per test')
    parser.add_argument('--steps', type=int, default=800, help='Steps per run')
    
    args = parser.parse_args()
    
    validator = SystemValidator(
        runs_per_test=args.runs,
        steps_per_run=args.steps
    )
    
    results = validator.run_all_tests()
    
    print("\n" + "="*70)
    print("✅ VALIDATION COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
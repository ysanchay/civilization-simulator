"""Quick validation - fast tests to verify system impact."""

import sys
sys.path.insert(0, '.')

print("="*70)
print("🧪 QUICK SYSTEM VALIDATION")
print("="*70)

results = {}

# =====================================================
# TEST 1: COGNITIVE STRESS
# =====================================================
print("\n🧠 Test 1: Cognitive Stress")
try:
    from cognitive_stress import CognitiveStressSystem
    
    # Test with high stress
    cs_high = CognitiveStressSystem(chaos_intensity=0.3, noise_level=0.2)
    
    # Apply stress
    for _ in range(10):
        time, chaos = cs_high.apply_temporal_chaos(0, 0)
    
    # Test with low stress
    cs_low = CognitiveStressSystem(chaos_intensity=0.01, noise_level=0.01)
    
    for _ in range(10):
        time_low, chaos_low = cs_low.apply_temporal_chaos(0, 0)
    
    # Check overload
    overload = cs_high.check_overload(1, symbol_count=200, step=100)
    
    results['cognitive_stress'] = {
        'status': '✅ WORKING',
        'high_chaos': chaos,
        'low_chaos': chaos_low,
        'overload_triggered': overload > 0.5,
        'impact': chaos > chaos_low,
    }
    print(f"   High chaos: {chaos:.2f}, Low chaos: {chaos_low:.2f}")
    print(f"   Overload triggered: {overload > 0.5}")
    print(f"   Impact: {'✅ MEASURABLE' if chaos > chaos_low else '⚠️ NO DIFFERENCE'}")
except Exception as e:
    results['cognitive_stress'] = {'status': f'❌ ERROR: {e}'}
    print(f"   ❌ ERROR: {e}")

# =====================================================
# TEST 2: TERRITORY
# =====================================================
print("\n🌍 Test 2: Territory")
try:
    from territory import TerritorySystem
    
    t = TerritorySystem(30, 30)
    
    # Tribe 1 claims territory
    for i in range(15):
        t.claim_cell(1, 5+i//3, 5+i%3, 1.0)
    
    # Tribe 2 claims territory
    for i in range(10):
        t.claim_cell(2, 20+i//3, 10+i%3, 1.0)
    
    # Conquest
    conquered = t.conquest(1, 2, cells=3)
    
    status = t.status()
    
    results['territory'] = {
        'status': '✅ WORKING',
        'claimed_cells': status['total_claimed'],
        'conquests': status['total_conquests'],
        'contested': status['contested_cells'],
        'impact': status['total_conquests'] > 0,
    }
    print(f"   Claimed cells: {status['total_claimed']}")
    print(f"   Conquests: {status['total_conquests']}")
    print(f"   Contested: {status['contested_cells']}")
    print(f"   Impact: {'✅ MEASURABLE' if status['total_conquests'] > 0 else '⚠️ NO IMPACT'}")
except Exception as e:
    results['territory'] = {'status': f'❌ ERROR: {e}'}
    print(f"   ❌ ERROR: {e}")

# =====================================================
# TEST 3: SCALING
# =====================================================
print("\n📊 Test 3: Scaling")
try:
    from scaling_penalties import ScalingPenaltySystem
    
    sp = ScalingPenaltySystem()
    
    # Test different sizes
    small = sp.update_tribe(1, population=10, territory_size=5, symbol_count=20)
    medium = sp.update_tribe(2, population=40, territory_size=25, symbol_count=80)
    large = sp.update_tribe(3, population=80, territory_size=60, symbol_count=200)
    
    results['scaling'] = {
        'status': '✅ WORKING',
        'small_efficiency': small.efficiency,
        'medium_efficiency': medium.efficiency,
        'large_efficiency': large.efficiency,
        'small_risk': small.failure_risk,
        'large_risk': large.failure_risk,
        'impact': small.efficiency > large.efficiency,
    }
    print(f"   Small (10): {small.efficiency:.1%} efficiency, {small.failure_risk:.1%} risk")
    print(f"   Medium (40): {medium.efficiency:.1%} efficiency, {medium.failure_risk:.1%} risk")
    print(f"   Large (80): {large.efficiency:.1%} efficiency, {large.failure_risk:.1%} risk")
    print(f"   Impact: {'✅ MEASURABLE - Efficiency drops with size' if small.efficiency > large.efficiency else '⚠️ NO IMPACT'}")
except Exception as e:
    results['scaling'] = {'status': f'❌ ERROR: {e}'}
    print(f"   ❌ ERROR: {e}")

# =====================================================
# TEST 4: COLLAPSE
# =====================================================
print("\n💥 Test 4: Collapse")
try:
    from collapse import CollapseSystem, CollapseStage
    
    col = CollapseSystem()
    
    # Stable tribe
    stable = col.update_tribe(
        tribe_id=1,
        population=20,
        symbols=40,
        territory=15,
        efficiency=0.9,
        coordination_cost=0.1
    )
    
    # Stressed tribe
    stressed = col.update_tribe(
        tribe_id=2,
        population=60,
        symbols=150,
        territory=40,
        efficiency=0.4,
        coordination_cost=0.7
    )
    
    # Collapsing tribe
    collapsing = col.update_tribe(
        tribe_id=3,
        population=100,
        symbols=300,
        territory=80,
        efficiency=0.2,
        coordination_cost=0.9
    )
    
    results['collapse'] = {
        'status': '✅ WORKING',
        'stable_stage': stable.stage.value,
        'stable_stress': stable.stress_level,
        'stressed_stage': stressed.stage.value,
        'stressed_stress': stressed.stress_level,
        'collapsing_stage': collapsing.stage.value,
        'collapsing_stress': collapsing.stress_level,
        'impact': stable.stress_level < collapsing.stress_level,
    }
    print(f"   Stable (20): Stage={stable.stage.value}, Stress={stable.stress_level:.1%}")
    print(f"   Stressed (60): Stage={stressed.stage.value}, Stress={stressed.stress_level:.1%}")
    print(f"   Collapsing (100): Stage={collapsing.stage.value}, Stress={collapsing.stress_level:.1%}")
    print(f"   Impact: {'✅ MEASURABLE - Stages progress with stress' if stable.stress_level < collapsing.stress_level else '⚠️ NO IMPACT'}")
except Exception as e:
    results['collapse'] = {'status': f'❌ ERROR: {e}'}
    print(f"   ❌ ERROR: {e}")

# =====================================================
# TEST 5: SCHISM
# =====================================================
print("\n⚔️ Test 5: Schism")
try:
    from schism import SchismSystem
    
    sch = SchismSystem(schism_threshold=0.5)
    
    # Create factions
    f1 = sch.create_faction(1, "Traditionalists", {"food", "safety"})
    f2 = sch.create_faction(1, "Innovators", {"artifacts", "meta"})
    
    # Calculate risk for different scenarios
    small_risk = sch.calculate_schism_risk(1, population=15, symbol_conflict=0.3, territory_size=10)
    medium_risk = sch.calculate_schism_risk(1, population=30, symbol_conflict=0.5, territory_size=25)
    large_risk = sch.calculate_schism_risk(1, population=60, symbol_conflict=0.7, territory_size=50)
    
    results['schism'] = {
        'status': '✅ WORKING',
        'factions_created': sch.status()['total_factions'],
        'small_risk': small_risk,
        'medium_risk': medium_risk,
        'large_risk': large_risk,
        'impact': small_risk < large_risk,
    }
    print(f"   Factions created: {sch.status()['total_factions']}")
    print(f"   Schism risk (small): {small_risk:.1%}")
    print(f"   Schism risk (medium): {medium_risk:.1%}")
    print(f"   Schism risk (large): {large_risk:.1%}")
    print(f"   Impact: {'✅ MEASURABLE - Risk increases with size/conflict' if small_risk < large_risk else '⚠️ NO IMPACT'}")
except Exception as e:
    results['schism'] = {'status': f'❌ ERROR: {e}'}
    print(f"   ❌ ERROR: {e}")

# =====================================================
# SUMMARY
# =====================================================
print("\n" + "="*70)
print("📊 VALIDATION SUMMARY")
print("="*70)

all_working = True
for name, result in results.items():
    status = result.get('status', '❓ UNKNOWN')
    impact = result.get('impact', False)
    symbol = '✅' if impact else '⚠️'
    all_working = all_working and impact
    print(f"   {symbol} {name.upper()}: {status}")
    if impact:
        print(f"      → MEASURABLE IMPACT")

print("\n" + "="*70)
if all_working:
    print("✅ ALL SYSTEMS HAVE MEASURABLE IMPACT")
    print("   Systems are NOT decorative - they affect behavior!")
else:
    print("⚠️ SOME SYSTEMS MAY NEED INTEGRATION IMPROVEMENTS")
print("="*70)

# Save
import json
from pathlib import Path
from datetime import datetime

path = Path("metrics") / f"quick_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
path.parent.mkdir(exist_ok=True)
with open(path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n📄 Results saved: {path}")
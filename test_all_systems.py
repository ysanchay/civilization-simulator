"""Generate a comprehensive report of all systems."""

import sys
import json
from pathlib import Path
from datetime import datetime

# Test each system individually
print("="*70)
print("🌍 CIVILIZATION SIMULATOR - ALL SYSTEMS TEST REPORT")
print("="*70)
print(f"Generated: {datetime.now().isoformat()}")
print()

results = {}

# =====================================================
# 1. TERRITORY SYSTEM
# =====================================================
print("🌍 Testing Territory System...")
try:
    from territory import TerritorySystem, TerritoryType
    
    t = TerritorySystem(30, 30)
    
    # Claim territory
    for i in range(10):
        t.claim_cell(1, 5+i, 5+i, 1.0)
    for i in range(8):
        t.claim_cell(2, 20+i, 10, 1.0)
    
    # Conquest
    conquered = t.conquest(1, 2, cells=3)
    
    results['territory'] = {
        'status': '✅ WORKING',
        'claimed_cells': t.status()['total_claimed'],
        'conquests': t.status()['total_conquests'],
        'tribes_with_land': t.status()['tribes_with_territory'],
    }
    print(f"   ✅ Territory: {results['territory']}")
except Exception as e:
    results['territory'] = {'status': f'❌ ERROR: {e}'}
    print(f"   ❌ Territory: {e}")

# =====================================================
# 2. HISTORICAL MEMORY
# =====================================================
print("📜 Testing Historical Memory...")
try:
    from historical_memory import HistoricalMemory, EventType, EraType
    
    h = HistoricalMemory()
    
    # Record events
    h.record_founding(0, 1, (10, 10))
    h.record_war(100, 1, 2, 1, {1: 5, 2: 10})
    h.record_expansion(200, 1, 5)
    h.record_innovation(300, 1, "Meta-symbols")
    
    # Update era
    h.update_era(500, 1, population=30, symbols=50, territory=20)
    
    results['historical'] = {
        'status': '✅ WORKING',
        'events': h.status()['total_events'],
        'myths': h.status()['total_myths'],
        'active_tribes': h.status()['active_tribes'],
    }
    print(f"   ✅ History: {results['historical']}")
except Exception as e:
    results['historical'] = {'status': f'❌ ERROR: {e}'}
    print(f"   ❌ History: {e}")

# =====================================================
# 3. COGNITIVE STRESS
# =====================================================
print("🧠 Testing Cognitive Stress...")
try:
    from cognitive_stress import CognitiveStressSystem
    
    cs = CognitiveStressSystem(chaos_intensity=0.15)
    
    # Apply temporal chaos
    times = []
    for i in range(10):
        t, chaos = cs.apply_temporal_chaos(i, i % 4)
        times.append(t)
    
    # Generate false signals
    signals = cs.generate_false_signals(50, (20, 20), count=3)
    
    # Check overload
    overload = cs.check_overload(1, symbol_count=150, step=100)
    
    results['cognitive_stress'] = {
        'status': '✅ WORKING',
        'time_distortion': cs.time_distortion,
        'false_signals': len(cs.false_artifacts),
        'overload_level': overload,
    }
    print(f"   ✅ Cognitive Stress: {results['cognitive_stress']}")
except Exception as e:
    results['cognitive_stress'] = {'status': f'❌ ERROR: {e}'}
    print(f"   ❌ Cognitive Stress: {e}")

# =====================================================
# 4. SCALING PENALTIES
# =====================================================
print("📊 Testing Scaling Penalties...")
try:
    from scaling_penalties import ScalingPenaltySystem
    
    sp = ScalingPenaltySystem()
    
    # Test different tribe sizes
    small = sp.update_tribe(1, population=10, territory_size=5, symbol_count=20)
    medium = sp.update_tribe(2, population=40, territory_size=20, symbol_count=80)
    large = sp.update_tribe(3, population=80, territory_size=50, symbol_count=200)
    
    results['scaling'] = {
        'status': '✅ WORKING',
        'small_efficiency': f"{small.efficiency:.1%}",
        'medium_efficiency': f"{medium.efficiency:.1%}",
        'large_efficiency': f"{large.efficiency:.1%}",
        'large_failure_risk': f"{large.failure_risk:.1%}",
    }
    print(f"   ✅ Scaling: {results['scaling']}")
except Exception as e:
    results['scaling'] = {'status': f'❌ ERROR: {e}'}
    print(f"   ❌ Scaling: {e}")

# =====================================================
# 5. CULTURAL SCHISM
# =====================================================
print("⚔️ Testing Cultural Schism...")
try:
    from schism import SchismSystem, SchismType
    
    sch = SchismSystem(schism_threshold=0.6)
    
    # Create factions
    f1 = sch.create_faction(1, "Traditionalists", symbol_focus={"food", "safety"})
    f2 = sch.create_faction(1, "Innovators", symbol_focus={"artifacts", "meta"})
    
    # Calculate schism risk
    risk = sch.calculate_schism_risk(
        tribe_id=1,
        population=30,
        symbol_conflict=0.5,
        territory_size=20
    )
    
    results['schism'] = {
        'status': '✅ WORKING',
        'factions': sch.status()['total_factions'],
        'schism_risk': f"{risk:.1%}",
        'stability': f"{sch.get_tribe_stability(1):.1%}",
    }
    print(f"   ✅ Schism: {results['schism']}")
except Exception as e:
    results['schism'] = {'status': f'❌ ERROR: {e}'}
    print(f"   ❌ Schism: {e}")

# =====================================================
# 6. COLLAPSE SYSTEM
# =====================================================
print("💥 Testing Collapse System...")
try:
    from collapse import CollapseSystem, CollapseStage
    
    col = CollapseSystem()
    
    # Test stable tribe
    stable = col.update_tribe(
        tribe_id=1,
        population=20,
        symbols=50,
        territory=15,
        efficiency=0.9,
        coordination_cost=0.1
    )
    
    # Test stressed tribe
    stressed = col.update_tribe(
        tribe_id=2,
        population=60,
        symbols=200,
        territory=50,
        efficiency=0.4,
        coordination_cost=0.8
    )
    
    results['collapse'] = {
        'status': '✅ WORKING',
        'stable_stage': stable.stage.value,
        'stressed_stage': stressed.stage.value,
        'stressed_stress': f"{stressed.stress_level:.1%}",
        'total_collapses': col.status()['total_collapses'],
    }
    print(f"   ✅ Collapse: {results['collapse']}")
except Exception as e:
    results['collapse'] = {'status': f'❌ ERROR: {e}'}
    print(f"   ❌ Collapse: {e}")

# =====================================================
# SUMMARY
# =====================================================
print()
print("="*70)
print("📊 SYSTEM TEST SUMMARY")
print("="*70)

all_working = True
for system, data in results.items():
    status = data.get('status', '❓ UNKNOWN')
    symbol = '✅' if 'WORKING' in status else '❌'
    all_working = all_working and ('WORKING' in status)
    print(f"   {symbol} {system.upper()}: {status}")

print()
print("="*70)
print("🎯 SYSTEM CAPABILITIES")
print("="*70)
print("""
🌍 TERRITORY SYSTEM:
   • Cell ownership and borders
   • Territory conquest after war
   • Homeland bonuses
   • Contested territory tracking

📜 HISTORICAL MEMORY:
   • Event recording (wars, expansions, innovations)
   • Era detection (Golden Age, Dark Age, Renaissance)
   • Myth formation from significant events
   • Historical reinterpretation

🧠 COGNITIVE STRESS:
   • Temporal chaos (irregular time cycles)
   • False signal generation
   • Information overload
   • Adaptive learning

📊 SCALING PENALTIES:
   • Administrative load calculation
   • Coordination cost scaling
   • Efficiency decay with size
   • Failure risk assessment

⚔️ CULTURAL SCHISM:
   • Faction formation
   • Symbol conflict detection
   • Schism triggering
   • Ideological splits

💥 COLLAPSE SYSTEM:
   • Collapse cascade detection
   • Knowledge bottleneck tracking
   • Cultural debt accumulation
   • Renaissance recovery
""")

print("="*70)
if all_working:
    print("✅ ALL 6 SYSTEMS OPERATIONAL")
else:
    print("⚠️ SOME SYSTEMS HAVE ISSUES")
print("="*70)

# Save report
report_path = Path("metrics") / f"systems_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
report_path.parent.mkdir(exist_ok=True)
with open(report_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n📄 Report saved: {report_path}")
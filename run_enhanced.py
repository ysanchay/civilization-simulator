"""
Enhanced Civilization Simulator with:
1. Fixed temporal accuracy tracking
2. Competition/wars enabled
3. Learning verification across runs
"""

import time
import statistics
from collections import Counter, defaultdict
from datetime import datetime
import json
from pathlib import Path
import random

# Core components
from world import World
from agent import Agent
from metrics import WorldMetrics, KnowledgeMetrics

# Agent architecture
from agents.culture_agent import CultureAgent
from agents.competition_agent import CompetitionAgent, Conflict, Alliance
from agents.innovation_agent import InnovationAgent

# Success metrics
from success_metrics import (
    MetricsCollector,
    EmergenceMetrics,
    SurvivalMetrics,
    IntelligenceMetrics,
    SuccessScore,
    evaluate_simulation_use_case,
)

# Configuration
from config import SimulationConfig


class EnhancedKnowledgeMetrics:
    """Enhanced knowledge metrics with proper temporal tracking."""
    
    def __init__(self):
        self.time_transitions = defaultdict(lambda: defaultdict(int))
        self.time_totals = defaultdict(int)
        
        # NEW: Track predictions
        self.predictions_made = defaultdict(int)
        self.predictions_correct = defaultdict(int)
        
        # NEW: Track symbol usage patterns
        self.symbol_usage_patterns = defaultdict(lambda: defaultdict(int))
        
        # NEW: Track learning over time
        self.learning_history = defaultdict(list)
    
    def record_time_transition(self, tribe_id, prev_pattern, curr_pattern):
        """Record time transition and check prediction accuracy."""
        if prev_pattern is None or curr_pattern is None:
            return
        
        try:
            # Extract time from patterns (last element is time phase)
            t1 = prev_pattern[-1] if hasattr(prev_pattern, '__len__') else 0
            t2 = curr_pattern[-1] if hasattr(curr_pattern, '__len__') else 0
            
            # Record transition
            self.time_transitions[tribe_id][(t1, t2)] += 1
            self.time_totals[tribe_id] += 1
            
            # Record symbol usage pattern
            if hasattr(prev_pattern, '__len__') and len(prev_pattern) >= 2:
                food_prev = prev_pattern[0] if len(prev_pattern) > 0 else 0
                danger_prev = prev_pattern[1] if len(prev_pattern) > 1 else 0
                pattern_key = (food_prev, danger_prev)
                self.symbol_usage_patterns[tribe_id][pattern_key] += 1
                
        except Exception as e:
            pass
    
    def record_prediction(self, tribe_id, predicted_time, actual_time):
        """Record a time prediction and its accuracy."""
        self.predictions_made[tribe_id] += 1
        if predicted_time == actual_time:
            self.predictions_correct[tribe_id] += 1
    
    def temporal_accuracy(self, tribe_id, cycle=4):
        """Calculate temporal accuracy - how well agents understand time."""
        transitions = self.time_transitions[tribe_id]
        total = self.time_totals[tribe_id]
        
        if total == 0:
            return 0.0
        
        # Count correct transitions (time advances by 1 mod cycle)
        correct = sum(
            count for (t1, t2), count in transitions.items()
            if (t1 + 1) % cycle == t2
        )
        
        base_accuracy = correct / total
        
        # Also factor in prediction accuracy if available
        if self.predictions_made[tribe_id] > 0:
            pred_accuracy = self.predictions_correct[tribe_id] / self.predictions_made[tribe_id]
            # Weighted average
            return round((base_accuracy * 0.5 + pred_accuracy * 0.5), 2)
        
        return round(base_accuracy, 2)
    
    def learning_rate(self, tribe_id):
        """Calculate how quickly the tribe is learning."""
        history = self.learning_history.get(tribe_id, [])
        if len(history) < 2:
            return 0.0
        
        # Compare recent accuracy to past
        recent = history[-10:] if len(history) >= 10 else history
        past = history[:-10] if len(history) >= 20 else history[:len(history)//2]
        
        if not recent or not past:
            return 0.0
        
        recent_avg = sum(recent) / len(recent)
        past_avg = sum(past) / len(past)
        
        # Learning rate = improvement
        return round(max(0, recent_avg - past_avg), 3)
    
    def artifact_coverage(self, tribe):
        """Track understanding of artifacts."""
        covered = set()
        for pattern in tribe.symbols:
            if isinstance(pattern, tuple) and len(pattern) >= 3:
                artifact = pattern[2]
                if artifact and isinstance(artifact, tuple):
                    covered.add(artifact[0])
        return sorted(covered)
    
    def abstraction_depth(self, tribe):
        """Calculate abstraction depth."""
        depth = 1
        if hasattr(tribe, 'composed_symbols') and tribe.composed_symbols:
            depth = 2
        if hasattr(tribe, 'meta_symbols') and tribe.meta_symbols:
            depth = 3
        return depth
    
    def tribe_report(self, tribe_id, tribe):
        """Generate tribe report."""
        total_symbols = max(1, len(tribe.symbols))
        meta_count = len(tribe.meta_symbols) if hasattr(tribe, 'meta_symbols') else 0
        
        return {
            "symbols": len(tribe.symbols),
            "meta_ratio": round(meta_count / total_symbols, 2),
            "temporal_accuracy": self.temporal_accuracy(tribe_id),
            "learning_rate": self.learning_rate(tribe_id),
            "artifact_coverage": self.artifact_coverage(tribe),
            "abstraction_depth": self.abstraction_depth(tribe),
            "predictions_made": self.predictions_made.get(tribe_id, 0),
            "predictions_correct": self.predictions_correct.get(tribe_id, 0),
        }


class EnhancedSimulation:
    """Enhanced simulation with competition and learning verification."""
    
    def __init__(self, config: SimulationConfig = None, load_brains: str = None):
        self.config = config or SimulationConfig()
        
        # Core simulation
        self.world = World(
            width=self.config.world.width,
            height=self.config.world.height,
        )
        
        # Metrics
        self.world_metrics = WorldMetrics()
        self.knowledge_metrics = EnhancedKnowledgeMetrics()
        self.metrics_collector = MetricsCollector(output_dir="metrics")
        
        # Agents
        self.culture_agents = {}
        self.competition_agent = CompetitionAgent(
            conflict_threshold=0.2,  # Lower threshold = more conflicts
            alliance_threshold=0.4,
            war_cost=3.0,
            victory_reward=15.0,
        )
        self.innovation_agent = InnovationAgent(
            exploration_bonus=3.0,
            novelty_threshold=3,
        )
        
        # State
        self.step = 0
        self.prev_symbols = {}
        
        # Competition state
        self.pending_conflicts = []
        self.alliance_cooldown = defaultdict(int)
        
        # Learning tracking
        self.learning_snapshots = []
        self.prev_knowledge = {}
        
        # Brain persistence
        self.load_brains = load_brains
        self.save_brains = True
        
        # History
        self.history = {
            'population': [],
            'symbols': [],
            'composed': [],
            'meta': [],
            'tribes': [],
            'wars': [],
            'alliances': [],
            'temporal_accuracy': [],
            'knowledge_transfer': [],
        }
    
    def seed_agents(self, count: int = 5):
        """Seed initial agents."""
        for i in range(count):
            agent = Agent(
                name=f"A{i}",
                world=self.world,
                energy=self.config.agent.initial_energy,
            )
            self.world.add_agent(agent)
            
            if agent.tribe_id not in self.culture_agents:
                self.culture_agents[agent.tribe_id] = CultureAgent(
                    tribe_id=agent.tribe_id,
                    max_symbols=self.config.culture.max_symbols,
                )
        
        print(f"🌱 Seeded {count} agents in {len(self.world.tribes)} tribes")
    
    def step_simulation(self):
        """Advance simulation by one step with competition."""
        self.step += 1
        
        # Store previous symbols
        self.prev_symbols.clear()
        for agent in self.world.agents:
            self.prev_symbols[agent] = agent.last_symbol
        
        # Track previous knowledge state for learning verification
        prev_knowledge = self._capture_knowledge_state()
        
        # Advance world
        self.world.step()
        
        # Update knowledge metrics with better tracking
        self._update_knowledge_metrics()
        
        # Process competition (NEW!)
        if self.config.competition_enabled:
            self._process_competition()
        
        # Process knowledge transfer
        self._process_knowledge_transfer()
        
        # Record metrics
        self.metrics_collector.record_step(
            self.step, self.world, self.world.agents, self.world.tribes
        )
        
        # Track learning
        curr_knowledge = self._capture_knowledge_state()
        learning_delta = self._calculate_learning_delta(prev_knowledge, curr_knowledge)
        self.history['knowledge_transfer'].append(learning_delta)
        
        # Update history
        self._update_history()
    
    def _update_knowledge_metrics(self):
        """Update knowledge metrics with proper time tracking."""
        for agent in self.world.agents:
            tribe_id = agent.tribe_id
            prev_pattern = self.prev_symbols.get(agent)
            curr_pattern = agent.last_symbol
            
            if prev_pattern and curr_pattern:
                # Record transition
                self.knowledge_metrics.record_time_transition(
                    tribe_id, prev_pattern, curr_pattern
                )
                
                # Check if tribe could predict this transition
                tribe = self.world.tribes.get(tribe_id)
                if tribe and hasattr(tribe, 'predict_next'):
                    predicted = tribe.predict_next(prev_pattern)
                    if predicted:
                        predicted_time = predicted[-1] if hasattr(predicted, '__len__') else None
                        actual_time = curr_pattern[-1] if hasattr(curr_pattern, '__len__') else None
                        if predicted_time is not None and actual_time is not None:
                            self.knowledge_metrics.record_prediction(
                                tribe_id, predicted_time, actual_time
                            )
    
    def _process_competition(self):
        """Process tribe competition, wars, and alliances."""
        # Get tribe data
        tribe_data = {}
        tribe_positions = defaultdict(list)
        
        for agent in self.world.agents:
            tid = agent.tribe_id
            tribe_positions[tid].append((agent.x, agent.y))
            
            if tid not in tribe_data:
                tribe_data[tid] = {
                    'population': 0,
                    'energy': 0,
                    'symbols': 0,
                }
            
            tribe_data[tid]['population'] += 1
            tribe_data[tid]['energy'] += agent.energy
        
        # Add symbol counts
        for tid, tribe in self.world.tribes.items():
            if tid in tribe_data and hasattr(tribe, 'symbols'):
                tribe_data[tid]['symbols'] = len(tribe.symbols)
        
        # Calculate dominance
        for tid, data in tribe_data.items():
            symbols = tribe_data[tid].get('symbols', 0)
            territory = len(set(tribe_positions.get(tid, [])))
            victories = self.competition_agent.victory_counts.get(tid, 0)
            
            self.competition_agent.calculate_dominance(
                tribe_id=tid,
                population=data['population'],
                symbols=symbols,
                territory=territory,
                victories=victories,
            )
        
        # Check for conflicts between neighboring tribes
        tribe_ids = list(tribe_data.keys())
        for i, tid1 in enumerate(tribe_ids):
            for tid2 in tribe_ids[i+1:]:
                if tid1 == tid2:
                    continue
                
                # Check proximity
                positions1 = tribe_positions.get(tid1, [])
                positions2 = tribe_positions.get(tid2, [])
                
                min_dist = float('inf')
                for p1 in positions1[:10]:  # Limit checks
                    for p2 in positions2[:10]:
                        dist = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
                        min_dist = min(min_dist, dist)
                
                # Conflict probability increases with proximity
                if min_dist < 5:  # Tribes within 5 cells
                    conflict_prob = self.competition_agent.detect_conflict(
                        tribe_a=tid1,
                        tribe_b=tid2,
                        positions_a=positions1,
                        positions_b=positions2,
                        resource_positions=[],
                    )
                    
                    if random.random() < conflict_prob * 0.1:  # Scale down for frequency
                        # Initiate war
                        strength1 = tribe_data[tid1]['population'] * tribe_data[tid1]['energy'] / 100
                        strength2 = tribe_data[tid2]['population'] * tribe_data[tid2]['energy'] / 100
                        
                        conflict = self.competition_agent.initiate_war(
                            attacker_id=tid1,
                            defender_id=tid2,
                            attacker_strength=strength1,
                            defender_strength=strength2,
                            location=positions1[0] if positions1 else (0, 0),
                        )
                        
                        # Resolve immediately (could be async in future)
                        outcome = self.competition_agent.resolve_war(conflict)
                        
                        # Apply casualties
                        casualties = conflict.casualties
                        self._apply_war_casualties(tid1, casualties.get(tid1, 0))
                        self._apply_war_casualties(tid2, casualties.get(tid2, 0))
                        
                        # Record
                        self.history['wars'].append({
                            'step': self.step,
                            'attacker': tid1,
                            'defender': tid2,
                            'outcome': outcome,
                        })
                        self.metrics_collector.record_war(tid1, tid2, outcome)
                
                # Check for alliance opportunities
                if min_dist < 10 and min_dist >= 5:  # Medium distance
                    common_enemies = set(self.competition_agent.get_enemies(tid1)) & set(
                        self.competition_agent.get_enemies(tid2))
                    
                    if common_enemies and random.random() < 0.05:
                        alliance = self.competition_agent.form_alliance(
                            tribe_a=tid1,
                            tribe_b=tid2,
                            step=self.step,
                        )
                        
                        if alliance:
                            self.history['alliances'].append({
                                'step': self.step,
                                'tribe_a': tid1,
                                'tribe_b': tid2,
                            })
                            self.metrics_collector.record_alliance(tid1, tid2)
    
    def _apply_war_casualties(self, tribe_id: int, count: int):
        """Apply casualties from war."""
        tribe_agents = [a for a in self.world.agents if a.tribe_id == tribe_id]
        
        for _ in range(min(count, len(tribe_agents))):
            if tribe_agents:
                victim = random.choice(tribe_agents)
                victim.energy -= 20  # War damage
                tribe_agents.remove(victim)
    
    def _process_knowledge_transfer(self):
        """Process inter-tribe knowledge transfer."""
        # Find agents from different tribes that are adjacent
        for agent in self.world.agents:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = agent.x + dx, agent.y + dy
                if not self.world.in_bounds(nx, ny):
                    continue
                
                other = self.world.grid[ny][nx] if ny < len(self.world.grid) and nx < len(self.world.grid[0]) else None
                if other and other.tribe_id != agent.tribe_id:
                    # Knowledge transfer opportunity
                    tribe_from = self.culture_agents.get(other.tribe_id)
                    tribe_to = self.culture_agents.get(agent.tribe_id)
                    
                    if tribe_from and tribe_to:
                        # Share symbols
                        if agent.last_symbol and agent.last_symbol in tribe_from.symbols:
                            tribe_to.adopt_symbol(agent.last_symbol, tribe_from)
    
    def _capture_knowledge_state(self):
        """Capture current knowledge state for comparison."""
        state = {}
        for tid, tribe in self.world.tribes.items():
            state[tid] = {
                'symbols': len(tribe.symbols) if hasattr(tribe, 'symbols') else 0,
                'composed': len(tribe.composed_symbols) if hasattr(tribe, 'composed_symbols') else 0,
                'meta': len(tribe.meta_symbols) if hasattr(tribe, 'meta_symbols') else 0,
                'temporal_acc': self.knowledge_metrics.temporal_accuracy(tid),
            }
        return state
    
    def _calculate_learning_delta(self, prev, curr):
        """Calculate how much knowledge changed."""
        delta = {
            'new_symbols': 0,
            'new_composed': 0,
            'new_meta': 0,
            'accuracy_improvement': 0,
        }
        
        for tid in curr:
            if tid in prev:
                delta['new_symbols'] += curr[tid]['symbols'] - prev[tid]['symbols']
                delta['new_composed'] += curr[tid]['composed'] - prev[tid]['composed']
                delta['new_meta'] += curr[tid]['meta'] - prev[tid]['meta']
                delta['accuracy_improvement'] += curr[tid]['temporal_acc'] - prev[tid]['temporal_acc']
        
        return delta
    
    def _update_history(self):
        """Update history for analysis."""
        pop = len(self.world.agents)
        self.history['population'].append(pop)
        
        total_symbols = 0
        total_composed = 0
        total_meta = 0
        total_acc = 0
        tribe_count = 0
        
        for tribe in self.world.tribes.values():
            if hasattr(tribe, 'symbols'):
                total_symbols += len(tribe.symbols)
            if hasattr(tribe, 'composed_symbols'):
                total_composed += len(tribe.composed_symbols)
            if hasattr(tribe, 'meta_symbols'):
                total_meta += len(tribe.meta_symbols)
            tribe_count += 1
        
        # Average temporal accuracy
        for tid in self.world.tribes:
            total_acc += self.knowledge_metrics.temporal_accuracy(tid)
        
        self.history['symbols'].append(total_symbols)
        self.history['composed'].append(total_composed)
        self.history['meta'].append(total_meta)
        self.history['tribes'].append(tribe_count)
        self.history['temporal_accuracy'].append(total_acc / max(1, tribe_count))
    
    def run(self, max_steps: int = 5000, log_interval: int = 200):
        """Run simulation with enhanced metrics."""
        print("="*70)
        print("🌍 ENHANCED CIVILIZATION SIMULATOR")
        print("="*70)
        print(f"World: {self.config.world.width}x{self.config.world.height}")
        print(f"Steps: {max_steps}")
        print(f"Competition: {'ENABLED' if self.config.competition_enabled else 'DISABLED'}")
        print(f"Auto-expand: {'ENABLED' if self.world.auto_expand else 'DISABLED'} (threshold: {self.world.MAX_DENSITY:.0%})")
        print(f"Started: {datetime.now().isoformat()}")
        print("="*70)
        
        start_time = time.time()
        
        try:
            while self.step < max_steps:
                self.step_simulation()
                
                if len(self.world.agents) == 0:
                    print("\n☠️ All agents extinct!")
                    break
                
                if self.step % log_interval == 0:
                    self._log_progress()
                
                # Update learning history
                for tid in self.world.tribes:
                    acc = self.knowledge_metrics.temporal_accuracy(tid)
                    self.knowledge_metrics.learning_history[tid].append(acc)
                
                # Save brains periodically
                if self.step > 0 and self.step % 1000 == 0:
                    self.world.save_brains()
                
        except KeyboardInterrupt:
            print("\n⏹️ Stopped by user")
        
        elapsed = time.time() - start_time
        
        # Final brain save
        self.world.save_brains()
        
        print("\n" + "="*70)
        print(f"✅ Complete: {self.step} steps in {elapsed:.1f}s")
        print(f"   World expansions: {self.world.expansion_count}")
        
        return self._generate_report()
    
    def _log_progress(self):
        """Log progress with competition and expansion info."""
        pop = len(self.world.agents)
        density = self.world.get_density()
        tribes = len([t for t in self.world.tribes.values() if any(a.tribe_id == t.tribe_id for a in self.world.agents)])
        symbols = self.history['symbols'][-1] if self.history['symbols'] else 0
        composed = self.history['composed'][-1] if self.history['composed'] else 0
        meta = self.history['meta'][-1] if self.history['meta'] else 0
        acc = self.history['temporal_accuracy'][-1] if self.history['temporal_accuracy'] else 0
        wars = len(self.history['wars'])
        alliances = len(self.history['alliances'])
        expansions = self.world.expansion_count
        
        print(f"[{self.step:5d}] Pop: {pop:3d} | Density: {density:.1%} | Tribes: {tribes} | "
              f"Symbols: {symbols:3d} | Composed: {composed:2d} | Meta: {meta:2d} | "
              f"Acc: {acc:.2f} | Wars: {wars} | Alliances: {alliances} | Expansions: {expansions}")
    
    def _generate_report(self):
        """Generate comprehensive report."""
        print("\n📊 Generating enhanced report...")
        
        # Calculate metrics
        emergence = self.metrics_collector.calculate_emergence_metrics(self.world.tribes)
        
        # Add war/alliance data
        emergence.war_count = len(self.history['wars'])
        emergence.alliance_count = len(self.history['alliances'])
        
        survival = self.metrics_collector.calculate_survival_metrics()
        intelligence = self.metrics_collector.calculate_intelligence_metrics(self.world.tribes)
        
        # Update intelligence with temporal accuracy
        if self.history['temporal_accuracy']:
            intelligence.temporal_accuracy = self.history['temporal_accuracy'][-1]
        
        success = self.metrics_collector.calculate_success_score(emergence, survival, intelligence)
        
        # Evaluate use cases
        use_cases = {}
        for uc in ['gaming', 'ai_safety', 'education', 'robotics']:
            use_cases[uc] = evaluate_simulation_use_case(uc, emergence, survival, intelligence)
        
        # Learning verification
        learning_verification = self._verify_learning()
        
        report = {
            'simulation': {
                'steps': self.step,
                'world_size': (self.config.world.width, self.config.world.height),
                'competition_enabled': self.config.competition_enabled,
            },
            'emergence': emergence.to_dict(),
            'survival': survival.to_dict(),
            'intelligence': intelligence.to_dict(),
            'success': success.to_dict(),
            'use_cases': use_cases,
            'learning_verification': learning_verification,
            'history': {
                'population_final': self.history['population'][-1] if self.history['population'] else 0,
                'population_max': max(self.history['population']) if self.history['population'] else 0,
                'symbols_final': self.history['symbols'][-1] if self.history['symbols'] else 0,
                'composed_final': self.history['composed'][-1] if self.history['composed'] else 0,
                'meta_final': self.history['meta'][-1] if self.history['meta'] else 0,
                'wars_total': len(self.history['wars']),
                'alliances_total': len(self.history['alliances']),
                'temporal_accuracy_final': self.history['temporal_accuracy'][-1] if self.history['temporal_accuracy'] else 0,
            },
            'tribes': self._tribe_report(),
        }
        
        # Save
        Path("metrics").mkdir(exist_ok=True)
        path = self.metrics_collector.save_report(self.world.tribes)
        print(f"📄 Report saved: {path}")
        
        return report
    
    def _verify_learning(self):
        """Verify that agents are actually learning."""
        verification = {
            'temporal_learning': False,
            'symbol_accumulation': False,
            'abstraction_progression': False,
            'knowledge_transfer': False,
            'meta_symbol_usage': False,
            'evidence': [],
        }
        
        # Check temporal accuracy improvement
        if len(self.history['temporal_accuracy']) >= 100:
            early = statistics.mean(self.history['temporal_accuracy'][:50])
            late = statistics.mean(self.history['temporal_accuracy'][-50:])
            if late > early:
                verification['temporal_learning'] = True
                verification['evidence'].append(
                    f"Temporal accuracy improved: {early:.2f} → {late:.2f}"
                )
        
        # Check symbol accumulation
        if len(self.history['symbols']) >= 100:
            early = statistics.mean(self.history['symbols'][:50])
            late = statistics.mean(self.history['symbols'][-50:])
            if late > early:
                verification['symbol_accumulation'] = True
                verification['evidence'].append(
                    f"Symbols accumulated: {early:.0f} → {late:.0f}"
                )
        
        # Check abstraction progression
        composed_history = self.history['composed']
        meta_history = self.history['meta']
        if composed_history and meta_history:
            if max(composed_history) > 0:
                verification['abstraction_progression'] = True
                verification['evidence'].append(
                    f"Composed symbols reached: {max(composed_history)}"
                )
            if max(meta_history) > 0:
                verification['meta_symbol_usage'] = True
                verification['evidence'].append(
                    f"Meta-symbols reached: {max(meta_history)}"
                )
        
        # Check knowledge transfer
        if self.history['knowledge_transfer']:
            total_transfer = sum(
                kt['new_symbols'] for kt in self.history['knowledge_transfer']
            )
            if total_transfer > 0:
                verification['knowledge_transfer'] = True
                verification['evidence'].append(
                    f"Knowledge transfer events: symbols exchanged between tribes"
                )
        
        return verification
    
    def _tribe_report(self):
        """Generate tribe-specific report."""
        tribes_data = {}
        
        for tid, tribe in self.world.tribes.items():
            pop = sum(1 for a in self.world.agents if a.tribe_id == tid)
            
            tribe_data = {
                'population': pop,
                'symbols': len(tribe.symbols) if hasattr(tribe, 'symbols') else 0,
                'composed': len(tribe.composed_symbols) if hasattr(tribe, 'composed_symbols') else 0,
                'meta': len(tribe.meta_symbols) if hasattr(tribe, 'meta_symbols') else 0,
                'temporal_accuracy': self.knowledge_metrics.temporal_accuracy(tid),
                'home_biome': tribe.home_biome if hasattr(tribe, 'home_biome') else 0,
                'status': 'ACTIVE' if pop > 0 else 'EXTINCT',
            }
            
            if hasattr(tribe, 'goal_symbols'):
                tribe_data['goals'] = len(tribe.goal_symbols())
            
            if hasattr(tribe, 'summary'):
                summary = tribe.summary()
                tribe_data['avg_value'] = summary.get('avg_value', 0)
            
            # Dominance
            tribe_data['dominance'] = self.competition_agent.dominance_scores.get(tid, 0)
            
            # Wars and alliances
            tribe_data['victories'] = self.competition_agent.victory_counts.get(tid, 0)
            tribe_data['allies'] = len(self.competition_agent.get_allies(tid))
            tribe_data['enemies'] = len(self.competition_agent.get_enemies(tid))
            
            tribes_data[tid] = tribe_data
        
        return tribes_data
    
    def print_report(self, report):
        """Print comprehensive report."""
        print("\n" + "="*70)
        print("📊 ENHANCED METRICS REPORT")
        print("="*70)
        
        # Emergence
        e = report['emergence']
        print("\n🧬 EMERGENCE METRICS")
        print("-"*40)
        print(f"  Vocabulary Size: {e['language']['vocabulary_size']}")
        print(f"  Composed Symbols: {e['language']['composed_symbols']}")
        print(f"  Meta-Symbols: {e['language']['meta_symbols']}")
        print(f"  Abstraction Depth: {e['language']['abstraction_depth']}")
        print(f"  Tribes: {e['social']['tribe_count']}")
        print(f"  ⚔️  Wars: {e['social']['war_count']}")
        print(f"  🤝 Alliances: {e['social']['alliance_count']}")
        
        # Survival
        s = report['survival']
        print("\n💓 SURVIVAL METRICS")
        print("-"*40)
        print(f"  Population Final: {s['population']['final']}")
        print(f"  Population Max: {s['population']['max']}")
        print(f"  Tribes Surviving: {s['survival']['tribes_surviving']}")
        print(f"  Tribes Extinct: {s['survival']['tribes_extinct']}")
        print(f"  Total Births: {s['reproduction']['births']}")
        print(f"  Total Deaths: {s['reproduction']['deaths']}")
        
        # Intelligence
        i = report['intelligence']
        print("\n🧠 INTELLIGENCE METRICS")
        print("-"*40)
        print(f"  ⏱️  Temporal Accuracy: {i['temporal']['accuracy']:.2f}")
        print(f"  Max Abstraction Depth: {i['abstraction']['max_depth']}")
        print(f"  Goals Formed: {i['goals']['formed']}")
        
        # Success
        sc = report['success']
        print("\n⭐ SUCCESS SCORES")
        print("-"*40)
        print(f"  Emergence Score: {sc['emergence']:.1f}/100")
        print(f"  Survival Score: {sc['survival']:.1f}/100")
        print(f"  Intelligence Score: {sc['intelligence']:.1f}/100")
        print(f"  ────────────────────────────")
        print(f"  OVERALL SCORE: {sc['overall']:.1f}/100")
        
        # Learning Verification
        lv = report['learning_verification']
        print("\n🔬 LEARNING VERIFICATION")
        print("-"*40)
        checks = [
            ('Temporal Learning', lv['temporal_learning']),
            ('Symbol Accumulation', lv['symbol_accumulation']),
            ('Abstraction Progression', lv['abstraction_progression']),
            ('Knowledge Transfer', lv['knowledge_transfer']),
            ('Meta-Symbol Usage', lv['meta_symbol_usage']),
        ]
        for name, passed in checks:
            status = "✅ VERIFIED" if passed else "⏳ PENDING"
            print(f"  {name}: {status}")
        
        print("\n  Evidence:")
        for evidence in lv['evidence']:
            print(f"    • {evidence}")
        
        # Use Cases
        print("\n🎯 USE CASE EVALUATION")
        print("-"*40)
        for uc, data in report['use_cases'].items():
            status = "✅ SUITABLE" if data['suitable'] else "❌ NOT SUITABLE"
            print(f"  {uc.upper():15} | Score: {data['score']:.1f} | {status}")
        
        # Tribe Details
        print("\n🏰 TRIBE ANALYSIS")
        print("-"*40)
        print(f"{'Tribe':<7} {'Pop':<5} {'Sym':<5} {'Comp':<6} {'Meta':<5} {'Acc':<6} {'Dom':<6} {'Wars':<5} {'Status'}")
        print("-"*40)
        for tid, data in sorted(report['tribes'].items()):
            print(f"T{tid:<6} {data['population']:<5} {data['symbols']:<5} {data['composed']:<6} "
                  f"{data['meta']:<5} {data['temporal_accuracy']:<6.2f} {data['dominance']:<6.1f} "
                  f"{data['victories']:<5} {data['status']}")
        
        print("\n" + "="*70)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced simulation with learning verification')
    parser.add_argument('--steps', type=int, default=3000, help='Number of steps')
    parser.add_argument('--width', type=int, default=25, help='World width')
    parser.add_argument('--height', type=int, default=25, help='World height')
    parser.add_argument('--agents', type=int, default=15, help='Initial agents')
    parser.add_argument('--log', type=int, default=300, help='Log interval')
    
    args = parser.parse_args()
    
    config = SimulationConfig()
    config.world.width = args.width
    config.world.height = args.height
    config.initial_agents = args.agents
    config.competition_enabled = True  # ENABLE COMPETITION!
    
    sim = EnhancedSimulation(config)
    sim.seed_agents(config.initial_agents)
    report = sim.run(max_steps=args.steps, log_interval=args.log)
    sim.print_report(report)
    
    # Save detailed report
    path = Path("metrics") / f"enhanced_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path.parent.mkdir(exist_ok=True)
    with open(path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n📄 Detailed report saved to: {path}")


if __name__ == "__main__":
    main()
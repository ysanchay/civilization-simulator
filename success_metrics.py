"""
Success Metrics for Civilization Simulator

This module defines quantitative metrics to measure simulation success
and utility across different use cases.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from collections import defaultdict
import statistics
import json
from pathlib import Path


@dataclass
class EmergenceMetrics:
    """Metrics for emergent behavior quality."""
    
    # Language emergence
    vocabulary_size: int = 0
    composed_symbols: int = 0
    meta_symbols: int = 0
    abstraction_depth: float = 0.0
    
    # Cultural evolution
    symbol_adoption_rate: float = 0.0
    knowledge_transfer_events: int = 0
    innovation_rate: float = 0.0
    
    # Social dynamics
    tribe_count: int = 0
    alliance_count: int = 0
    war_count: int = 0
    dominance_hierarchy_stability: float = 0.0
    
    # Agent behavior
    goal_formation_rate: float = 0.0
    planning_depth_avg: float = 0.0
    exploration_rate: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'language': {
                'vocabulary_size': self.vocabulary_size,
                'composed_symbols': self.composed_symbols,
                'meta_symbols': self.meta_symbols,
                'abstraction_depth': self.abstraction_depth,
            },
            'culture': {
                'symbol_adoption_rate': self.symbol_adoption_rate,
                'knowledge_transfer_events': self.knowledge_transfer_events,
                'innovation_rate': self.innovation_rate,
            },
            'social': {
                'tribe_count': self.tribe_count,
                'alliance_count': self.alliance_count,
                'war_count': self.war_count,
                'dominance_stability': self.dominance_hierarchy_stability,
            },
            'behavior': {
                'goal_formation_rate': self.goal_formation_rate,
                'planning_depth': self.planning_depth_avg,
                'exploration_rate': self.exploration_rate,
            },
        }


@dataclass
class SurvivalMetrics:
    """Metrics for population and survival dynamics."""
    
    # Population
    population_min: int = 0
    population_max: int = 0
    population_final: int = 0
    population_mean: float = 0.0
    population_std: float = 0.0
    
    # Survival
    extinction_events: int = 0
    tribes_extinct: int = 0
    tribes_surviving: int = 0
    avg_lifespan: float = 0.0
    
    # Reproduction
    total_births: int = 0
    total_deaths: int = 0
    reproduction_rate: float = 0.0
    generation_max: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'population': {
                'min': self.population_min,
                'max': self.population_max,
                'final': self.population_final,
                'mean': self.population_mean,
                'std': self.population_std,
            },
            'survival': {
                'extinction_events': self.extinction_events,
                'tribes_extinct': self.tribes_extinct,
                'tribes_surviving': self.tribes_surviving,
                'avg_lifespan': self.avg_lifespan,
            },
            'reproduction': {
                'births': self.total_births,
                'deaths': self.total_deaths,
                'rate': self.reproduction_rate,
                'max_generation': self.generation_max,
            },
        }


@dataclass
class IntelligenceMetrics:
    """Metrics for intelligence and cognition quality."""
    
    # Temporal understanding
    temporal_accuracy: float = 0.0
    pattern_prediction_rate: float = 0.0
    
    # Abstraction
    max_abstraction_depth: int = 0
    avg_abstraction_depth: float = 0.0
    abstraction_progression: List[int] = field(default_factory=list)
    
    # Memory
    episodic_memory_size: int = 0
    semantic_memory_size: int = 0
    memory_utilization: float = 0.0
    
    # Goals
    goals_formed: int = 0
    goals_completed: int = 0
    goal_completion_rate: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'temporal': {
                'accuracy': self.temporal_accuracy,
                'prediction_rate': self.pattern_prediction_rate,
            },
            'abstraction': {
                'max_depth': self.max_abstraction_depth,
                'avg_depth': self.avg_abstraction_depth,
                'progression': self.abstraction_progression,
            },
            'memory': {
                'episodic': self.episodic_memory_size,
                'semantic': self.semantic_memory_size,
                'utilization': self.memory_utilization,
            },
            'goals': {
                'formed': self.goals_formed,
                'completed': self.goals_completed,
                'completion_rate': self.goal_completion_rate,
            },
        }


@dataclass
class SuccessScore:
    """Composite success score for the simulation."""
    
    emergence_score: float = 0.0
    survival_score: float = 0.0
    intelligence_score: float = 0.0
    overall_score: float = 0.0
    
    # Individual component scores
    language_score: float = 0.0
    culture_score: float = 0.0
    competition_score: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'emergence': self.emergence_score,
            'survival': self.survival_score,
            'intelligence': self.intelligence_score,
            'overall': self.overall_score,
            'components': {
                'language': self.language_score,
                'culture': self.culture_score,
                'competition': self.competition_score,
            },
        }


class MetricsCollector:
    """Collects and analyzes simulation metrics."""
    
    def __init__(self, output_dir: str = "metrics"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # History tracking
        self.population_history: List[int] = []
        self.tribe_history: List[Dict[int, int]] = []
        self.symbol_history: List[Dict[int, int]] = []
        self.step_history: List[int] = []
        
        # Event tracking
        self.births: int = 0
        self.deaths: int = 0
        self.extinctions: List[int] = []
        self.wars: List[Dict] = []
        self.alliances: List[Dict] = []
        self.innovations: List[Dict] = []
    
    def record_step(self, step: int, world: Any, agents: List, tribes: Dict):
        """Record metrics for a single step."""
        self.step_history.append(step)
        
        # Population
        pop = len(agents)
        self.population_history.append(pop)
        
        # Tribe distribution
        tribe_counts = defaultdict(int)
        for agent in agents:
            tribe_counts[agent.tribe_id] += 1
        self.tribe_history.append(dict(tribe_counts))
        
        # Symbol counts
        symbol_counts = {}
        for tid, tribe in tribes.items():
            symbol_counts[tid] = len(tribe.symbols) if hasattr(tribe, 'symbols') else 0
        self.symbol_history.append(symbol_counts)
    
    def record_birth(self, agent_name: str, tribe_id: int):
        """Record a birth event."""
        self.births += 1
    
    def record_death(self, agent_name: str, tribe_id: int):
        """Record a death event."""
        self.deaths += 1
    
    def record_extinction(self, tribe_id: int):
        """Record a tribe extinction."""
        self.extinctions.append(tribe_id)
    
    def record_war(self, attacker: int, defender: int, outcome: str):
        """Record a war event."""
        self.wars.append({
            'attacker': attacker,
            'defender': defender,
            'outcome': outcome,
        })
    
    def record_alliance(self, tribe_a: int, tribe_b: int):
        """Record an alliance formation."""
        self.alliances.append({
            'tribe_a': tribe_a,
            'tribe_b': tribe_b,
        })
    
    def record_innovation(self, innovation_type: str, tribe_id: int):
        """Record an innovation event."""
        self.innovations.append({
            'type': innovation_type,
            'tribe': tribe_id,
        })
    
    def calculate_emergence_metrics(self, tribes: Dict) -> EmergenceMetrics:
        """Calculate emergence metrics."""
        metrics = EmergenceMetrics()
        
        if not tribes:
            return metrics
        
        # Language metrics
        total_symbols = 0
        total_composed = 0
        total_meta = 0
        total_depth = 0
        
        for tribe in tribes.values():
            if hasattr(tribe, 'symbols'):
                total_symbols += len(tribe.symbols)
            if hasattr(tribe, 'composed_symbols'):
                total_composed += len(tribe.composed_symbols)
            if hasattr(tribe, 'meta_symbols'):
                total_meta += len(tribe.meta_symbols)
        
        metrics.vocabulary_size = total_symbols
        metrics.composed_symbols = total_composed
        metrics.meta_symbols = total_meta
        
        # Abstraction depth
        if total_meta > 0:
            metrics.abstraction_depth = 3.0
        elif total_composed > 0:
            metrics.abstraction_depth = 2.0
        elif total_symbols > 0:
            metrics.abstraction_depth = 1.0
        
        # Social metrics
        metrics.tribe_count = len(tribes)
        metrics.alliance_count = len(self.alliances)
        metrics.war_count = len(self.wars)
        
        return metrics
    
    def calculate_survival_metrics(self) -> SurvivalMetrics:
        """Calculate survival metrics."""
        metrics = SurvivalMetrics()
        
        if not self.population_history:
            return metrics
        
        metrics.population_min = min(self.population_history)
        metrics.population_max = max(self.population_history)
        metrics.population_final = self.population_history[-1]
        metrics.population_mean = statistics.mean(self.population_history)
        
        if len(self.population_history) > 1:
            metrics.population_std = statistics.stdev(self.population_history)
        
        metrics.extinction_events = len(self.extinctions)
        metrics.tribes_extinct = len(set(self.extinctions))
        
        if self.tribe_history:
            final_tribes = self.tribe_history[-1]
            metrics.tribes_surviving = len([t for t, c in final_tribes.items() if c > 0])
        
        metrics.total_births = self.births
        metrics.total_deaths = self.deaths
        
        if self.births > 0:
            metrics.reproduction_rate = self.births / len(self.step_history)
        
        return metrics
    
    def calculate_intelligence_metrics(self, tribes: Dict) -> IntelligenceMetrics:
        """Calculate intelligence metrics."""
        metrics = IntelligenceMetrics()
        
        if not tribes:
            return metrics
        
        # Abstraction depth
        depths = []
        for tribe in tribes.values():
            depth = 1
            if hasattr(tribe, 'composed_symbols') and tribe.composed_symbols:
                depth = 2
            if hasattr(tribe, 'meta_symbols') and tribe.meta_symbols:
                depth = 3
            depths.append(depth)
        
        if depths:
            metrics.max_abstraction_depth = max(depths)
            metrics.avg_abstraction_depth = statistics.mean(depths)
        
        # Goal formation
        total_goals = 0
        for tribe in tribes.values():
            if hasattr(tribe, 'goal_symbols'):
                total_goals += len(tribe.goal_symbols())
        
        metrics.goals_formed = total_goals
        
        return metrics
    
    def calculate_success_score(
        self,
        emergence: EmergenceMetrics,
        survival: SurvivalMetrics,
        intelligence: IntelligenceMetrics,
    ) -> SuccessScore:
        """Calculate overall success score."""
        score = SuccessScore()
        
        # Emergence score (0-100)
        # Higher vocabulary, more compositions, more meta-symbols = better
        lang_score = min(100, (
            emergence.vocabulary_size * 0.5 +
            emergence.composed_symbols * 5 +
            emergence.meta_symbols * 10
        ))
        score.language_score = lang_score
        
        # Culture score
        culture_score = min(100, (
            emergence.symbol_adoption_rate * 20 +
            emergence.knowledge_transfer_events * 5 +
            emergence.innovation_rate * 10
        ))
        score.culture_score = culture_score
        
        # Competition score
        comp_score = min(100, (
            (emergence.alliance_count + emergence.war_count) * 5 +
            emergence.dominance_hierarchy_stability * 20
        ))
        score.competition_score = comp_score
        
        score.emergence_score = (lang_score + culture_score + comp_score) / 3
        
        # Survival score (0-100)
        # Population stability, survival rate = better
        if survival.population_mean > 0:
            stability = 100 - min(100, survival.population_std / survival.population_mean * 100)
            survival_rate = min(100, survival.tribes_surviving * 20)
            score.survival_score = (stability + survival_rate) / 2
        
        # Intelligence score (0-100)
        intel_score = min(100, (
            intelligence.temporal_accuracy * 50 +
            intelligence.max_abstraction_depth * 20 +
            intelligence.goal_completion_rate * 30
        ))
        score.intelligence_score = intel_score
        
        # Overall score
        score.overall_score = (
            score.emergence_score * 0.4 +
            score.survival_score * 0.3 +
            score.intelligence_score * 0.3
        )
        
        return score
    
    def generate_report(self, tribes: Dict) -> Dict:
        """Generate a complete metrics report."""
        emergence = self.calculate_emergence_metrics(tribes)
        survival = self.calculate_survival_metrics()
        intelligence = self.calculate_intelligence_metrics(tribes)
        success = self.calculate_success_score(emergence, survival, intelligence)
        
        return {
            'emergence': emergence.to_dict(),
            'survival': survival.to_dict(),
            'intelligence': intelligence.to_dict(),
            'success': success.to_dict(),
            'events': {
                'total_births': self.births,
                'total_deaths': self.deaths,
                'total_wars': len(self.wars),
                'total_alliances': len(self.alliances),
                'total_innovations': len(self.innovations),
            },
        }
    
    def save_report(self, tribes: Dict, filename: str = None) -> str:
        """Save metrics report to file."""
        report = self.generate_report(tribes)
        
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"metrics_{timestamp}.json"
        
        path = self.output_dir / filename
        with open(path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return str(path)


def evaluate_simulation_use_case(
    use_case: str,
    emergence: EmergenceMetrics,
    survival: SurvivalMetrics,
    intelligence: IntelligenceMetrics,
) -> Dict[str, Any]:
    """
    Evaluate simulation for a specific use case.
    
    Args:
        use_case: One of 'gaming', 'ai_safety', 'education', 'robotics'
        emergence: Emergence metrics
        survival: Survival metrics  
        intelligence: Intelligence metrics
        
    Returns:
        Evaluation results with recommendations
    """
    
    if use_case == 'gaming':
        # Gaming needs: variety, surprise, replay value
        score = (
            emergence.vocabulary_size * 0.3 +
            emergence.composed_symbols * 5 +
            emergence.war_count * 3 +
            emergence.alliance_count * 3 +
            survival.tribes_surviving * 10
        ) / 10
        
        recommendations = []
        if emergence.vocabulary_size < 50:
            recommendations.append("Increase vocabulary size for more NPC variety")
        if emergence.war_count + emergence.alliance_count < 5:
            recommendations.append("Add more tribe interaction mechanics")
        if emergence.abstraction_depth < 2:
            recommendations.append("Encourage higher-level cultural development")
        
        return {
            'use_case': 'gaming',
            'score': min(100, score),
            'suitable': score > 30,
            'recommendations': recommendations,
        }
    
    elif use_case == 'ai_safety':
        # AI Safety needs: predictability, interpretability, alignment
        score = (
            intelligence.temporal_accuracy * 30 +
            intelligence.max_abstraction_depth * 15 +
            emergence.dominance_hierarchy_stability * 20 +
            (100 - min(100, survival.population_std / max(1, survival.population_mean) * 100)) * 0.35
        )
        
        recommendations = []
        if intelligence.temporal_accuracy < 0.5:
            recommendations.append("Improve temporal prediction for alignment testing")
        if emergence.abstraction_depth < 3:
            recommendations.append("Need higher abstraction for interpretability")
        
        return {
            'use_case': 'ai_safety',
            'score': min(100, score),
            'suitable': score > 50,
            'recommendations': recommendations,
        }
    
    elif use_case == 'education':
        # Education needs: clarity, engagement, learning value
        score = (
            emergence.vocabulary_size * 0.2 +
            emergence.abstraction_depth * 20 +
            survival.tribes_surviving * 10 +
            (survival.total_births - survival.total_deaths) * 0.1
        )
        
        recommendations = []
        if emergence.vocabulary_size < 30:
            recommendations.append("More symbols needed for teaching emergence")
        if emergence.abstraction_depth < 2:
            recommendations.append("Need visible abstraction levels for demonstration")
        
        return {
            'use_case': 'education',
            'score': min(100, score),
            'suitable': score > 25,
            'recommendations': recommendations,
        }
    
    elif use_case == 'robotics':
        # Robotics needs: scalability, robustness, transfer
        score = (
            emergence.symbol_adoption_rate * 40 +
            emergence.knowledge_transfer_events * 5 +
            survival.tribes_surviving * 10 +
            intelligence.goal_completion_rate * 30
        )
        
        recommendations = []
        if emergence.knowledge_transfer_events < 10:
            recommendations.append("Increase inter-tribe knowledge sharing")
        if intelligence.goal_completion_rate < 0.3:
            recommendations.append("Improve goal-directed behavior")
        
        return {
            'use_case': 'robotics',
            'score': min(100, score),
            'suitable': score > 35,
            'recommendations': recommendations,
        }
    
    else:
        return {
            'use_case': use_case,
            'score': 0,
            'suitable': False,
            'recommendations': ['Unknown use case'],
        }


# Example usage
if __name__ == "__main__":
    print("="*60)
    print("CIVILIZATION SIMULATOR - SUCCESS METRICS FRAMEWORK")
    print("="*60)
    print()
    print("Use Cases:")
    print("  1. Gaming Industry     - Emergent NPCs, storytelling")
    print("  2. AI Safety Research  - Emergent behavior, alignment")
    print("  3. Education           - Teaching complexity, emergence")
    print("  4. Robotics            - Swarm intelligence, coordination")
    print()
    print("Metrics Categories:")
    print("  • Emergence Metrics    - Language, culture, social dynamics")
    print("  • Survival Metrics     - Population, extinction, reproduction")
    print("  • Intelligence Metrics - Temporal, abstraction, goals")
    print("  • Success Score        - Composite evaluation")
    print()
    print("Run simulation with --metrics flag to collect data")
    print("="*60)
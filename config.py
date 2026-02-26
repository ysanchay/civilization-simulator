"""
Civilization Simulator - Global Configuration

This module contains all configurable parameters for the simulation.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple


@dataclass
class WorldConfig:
    """World configuration."""
    width: int = 20
    height: int = 20
    expansion_density: float = 0.15
    food_regen_rate: float = 0.02
    epoch_interval: int = 500
    initial_food_density: float = 0.05
    artifact_count: int = 6


@dataclass
class AgentConfig:
    """Agent configuration."""
    initial_energy: float = 50.0
    metabolism: float = 0.8
    reproduction_threshold: float = 60.0
    reproduction_cooldown: int = 5
    planning_horizon: int = 2
    mutation_rate: float = 0.2


@dataclass
class CultureConfig:
    """Culture configuration."""
    max_symbols: int = 300
    memory_vault_capacity: int = 50
    composition_threshold: int = 8
    meta_threshold: int = 10
    forgetting_threshold: float = -1.5


@dataclass
class CompetitionConfig:
    """Competition configuration."""
    conflict_threshold: float = 0.3
    alliance_threshold: float = 0.6
    war_cost: float = 5.0
    victory_reward: float = 10.0


@dataclass
class InnovationConfig:
    """Innovation configuration."""
    exploration_bonus: float = 2.0
    novelty_threshold: int = 5
    recombination_rate: float = 0.1
    exploitation_decay: float = 0.95


@dataclass
class VisualizationConfig:
    """Visualization configuration."""
    enabled: bool = True
    refresh_rate: float = 0.1
    color_enabled: bool = True
    width: int = 80
    height: int = 40


@dataclass
class SimulationConfig:
    """Main simulation configuration."""
    # Sub-configurations
    world: WorldConfig = field(default_factory=WorldConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    culture: CultureConfig = field(default_factory=CultureConfig)
    competition: CompetitionConfig = field(default_factory=CompetitionConfig)
    innovation: InnovationConfig = field(default_factory=InnovationConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    
    # Simulation settings
    initial_agents: int = 5
    max_steps: int = 100000
    checkpoint_interval: int = 1000
    checkpoint_dir: str = "checkpoints"
    
    # Feature flags
    innovation_enabled: bool = True
    competition_enabled: bool = True
    visualization_enabled: bool = True
    
    # Random seed
    seed: int = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'world': {
                'width': self.world.width,
                'height': self.world.height,
                'expansion_density': self.world.expansion_density,
                'food_regen_rate': self.world.food_regen_rate,
                'epoch_interval': self.world.epoch_interval,
                'initial_food_density': self.world.initial_food_density,
                'artifact_count': self.world.artifact_count,
            },
            'agent': {
                'initial_energy': self.agent.initial_energy,
                'metabolism': self.agent.metabolism,
                'reproduction_threshold': self.agent.reproduction_threshold,
                'reproduction_cooldown': self.agent.reproduction_cooldown,
                'planning_horizon': self.agent.planning_horizon,
                'mutation_rate': self.agent.mutation_rate,
            },
            'culture': {
                'max_symbols': self.culture.max_symbols,
                'memory_vault_capacity': self.culture.memory_vault_capacity,
                'composition_threshold': self.culture.composition_threshold,
                'meta_threshold': self.culture.meta_threshold,
            },
            'competition': {
                'conflict_threshold': self.competition.conflict_threshold,
                'alliance_threshold': self.competition.alliance_threshold,
                'war_cost': self.competition.war_cost,
                'victory_reward': self.competition.victory_reward,
            },
            'innovation': {
                'exploration_bonus': self.innovation.exploration_bonus,
                'novelty_threshold': self.innovation.novelty_threshold,
                'recombination_rate': self.innovation.recombination_rate,
            },
            'visualization': {
                'enabled': self.visualization.enabled,
                'refresh_rate': self.visualization.refresh_rate,
            },
            'simulation': {
                'initial_agents': self.initial_agents,
                'max_steps': self.max_steps,
                'checkpoint_interval': self.checkpoint_interval,
                'innovation_enabled': self.innovation_enabled,
                'competition_enabled': self.competition_enabled,
                'seed': self.seed,
            },
        }


# Default configuration
DEFAULT_CONFIG = SimulationConfig()


def load_config(path: str) -> SimulationConfig:
    """Load configuration from JSON file."""
    import json
    
    with open(path, 'r') as f:
        data = json.load(f)
    
    config = SimulationConfig()
    
    if 'world' in data:
        for key, value in data['world'].items():
            setattr(config.world, key, value)
    
    if 'agent' in data:
        for key, value in data['agent'].items():
            setattr(config.agent, key, value)
    
    if 'culture' in data:
        for key, value in data['culture'].items():
            setattr(config.culture, key, value)
    
    if 'simulation' in data:
        config.initial_agents = data['simulation'].get('initial_agents', 5)
        config.max_steps = data['simulation'].get('max_steps', 100000)
        config.innovation_enabled = data['simulation'].get('innovation_enabled', True)
        config.competition_enabled = data['simulation'].get('competition_enabled', True)
        config.seed = data['simulation'].get('seed', None)
    
    return config


def save_config(config: SimulationConfig, path: str):
    """Save configuration to JSON file."""
    import json
    
    with open(path, 'w') as f:
        json.dump(config.to_dict(), f, indent=2)
"""Baseline experiment configurations."""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class BaselineExperiment:
    """Configuration for a baseline experiment."""
    
    name: str
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    max_steps: int = 10000
    num_runs: int = 10
    
    def get_config(self) -> Dict[str, Any]:
        """Get full configuration."""
        return {
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters,
            'max_steps': self.max_steps,
            'num_runs': self.num_runs,
        }


# Standard baselines
MINIMAL_BASELINE = BaselineExperiment(
    name="minimal",
    description="Minimal simulation with basic features",
    parameters={
        "world_size": (10, 10),
        "initial_agents": 3,
        "innovation_enabled": False,
        "competition_enabled": False,
    },
    max_steps=5000,
    num_runs=5,
)

STANDARD_BASELINE = BaselineExperiment(
    name="standard",
    description="Standard simulation with all features",
    parameters={
        "world_size": (20, 20),
        "initial_agents": 5,
        "innovation_enabled": True,
        "competition_enabled": True,
    },
    max_steps=10000,
    num_runs=10,
)

LARGE_BASELINE = BaselineExperiment(
    name="large",
    description="Large-scale simulation",
    parameters={
        "world_size": (50, 50),
        "initial_agents": 20,
        "innovation_enabled": True,
        "competition_enabled": True,
    },
    max_steps=20000,
    num_runs=5,
)

HIGH_INNOVATION_BASELINE = BaselineExperiment(
    name="high_innovation",
    description="High innovation pressure",
    parameters={
        "world_size": (20, 20),
        "initial_agents": 5,
        "innovation_enabled": True,
        "innovation_bonus": 5.0,
        "competition_enabled": False,
    },
    max_steps=10000,
    num_runs=10,
)

ALL_BASELINES = [
    MINIMAL_BASELINE,
    STANDARD_BASELINE,
    LARGE_BASELINE,
    HIGH_INNOVATION_BASELINE,
]
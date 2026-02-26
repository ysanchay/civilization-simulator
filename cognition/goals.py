"""Goal formation system for agents."""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Optional, List


class GoalType(Enum):
    SURVIVAL = "survival"
    REPRODUCTION = "reproduction"
    EXPLORATION = "exploration"
    RESOURCE = "resource"
    SOCIAL = "social"
    ABSTRACT = "abstract"


class GoalPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class Goal:
    """Represents an agent's goal."""
    type: GoalType
    priority: GoalPriority
    target: Any
    deadline: Optional[int] = None
    value: float = 1.0
    progress: float = 0.0
    created_step: int = 0
    parent: Optional['Goal'] = None
    subgoals: List['Goal'] = field(default_factory=list)
    
    def is_complete(self) -> bool:
        return self.progress >= 1.0
    
    def add_subgoal(self, subgoal: 'Goal'):
        subgoal.parent = self
        self.subgoals.append(subgoal)
    
    def update_progress(self, amount: float):
        self.progress = min(1.0, self.progress + amount)
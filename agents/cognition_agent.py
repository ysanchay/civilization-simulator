"""
CognitionAgent

IDENTITY: "I am the mind. I form goals, plan, and remember."

ROLE: Individual and collective intelligence

RESPONSIBILITIES:
- Form goals from patterns and experiences
- Create multi-step symbolic plans
- Manage episodic memory (personal events)
- Manage semantic memory (generalized knowledge)
- Predict outcomes of actions
- Generate innovative behaviors
"""

import random
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


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
    target: Any  # What the goal is about
    deadline: Optional[int] = None  # Step deadline
    value: float = 1.0  # Importance value
    progress: float = 0.0  # 0.0 to 1.0
    created_step: int = 0
    parent: Optional['Goal'] = None
    subgoals: List['Goal'] = field(default_factory=list)


@dataclass
class Plan:
    """Represents a sequence of actions to achieve a goal."""
    goal: Goal
    actions: List[Tuple[str, Any]]  # (action_type, params)
    current_step: int = 0
    expected_value: float = 0.0
    actual_value: float = 0.0


@dataclass
class EpisodicMemory:
    """Personal event memory."""
    step: int
    event_type: str
    location: Tuple[int, int]
    pattern: Any
    reward: float
    outcome: str
    emotions: Dict[str, float]  # surprise, satisfaction, fear, etc.


@dataclass
class SemanticMemory:
    """Generalized knowledge."""
    pattern: Any
    meaning: str
    value: float
    confidence: float
    source_count: int  # How many episodes contributed
    last_updated: int


class CognitionAgent:
    """
    Handles goal formation, planning, and memory for agents.
    
    Enables multi-step reasoning and goal-directed behavior.
    """
    
    def __init__(
        self,
        planning_horizon: int = 5,
        memory_capacity: int = 100,
        goal_capacity: int = 10,
    ):
        self.planning_horizon = planning_horizon
        self.memory_capacity = memory_capacity
        self.goal_capacity = goal_capacity
        
        # Goal system
        self.goals: List[Goal] = []
        self.current_goal: Optional[Goal] = None
        self.current_plan: Optional[Plan] = None
        
        # Memory systems
        self.episodic_memory: List[EpisodicMemory] = []
        self.semantic_memory: Dict[Any, SemanticMemory] = {}
        self.pattern_frequency: Dict[Any, int] = defaultdict(int)
        
        # Prediction model
        self.transition_counts: Dict[Tuple, Dict[Any, int]] = defaultdict(lambda: defaultdict(int))
        self.reward_model: Dict[Any, float] = defaultdict(float)
        
        # Innovation tracking
        self.novelty_threshold = 0.1
        self.explored_patterns: set = set()
    
    # =====================================================
    # GOAL FORMATION
    # =====================================================
    
    def form_goal(
        self,
        pattern: Any,
        reward: float,
        current_energy: float,
        step: int,
    ) -> Optional[Goal]:
        """
        Form a new goal based on pattern and reward history.
        
        Args:
            pattern: Observed pattern
            reward: Reward received
            current_energy: Agent's current energy
            step: Current simulation step
            
        Returns:
            New goal if one should be formed
        """
        # Determine goal type from pattern
        goal_type = self._classify_pattern_to_goal(pattern, reward)
        
        # Determine priority based on urgency
        priority = self._calculate_priority(goal_type, current_energy, reward)
        
        # Create goal
        goal = Goal(
            type=goal_type,
            priority=priority,
            target=pattern,
            value=abs(reward),
            created_step=step,
        )
        
        # Add to goals if capacity allows
        if len(self.goals) < self.goal_capacity:
            self.goals.append(goal)
            self._sort_goals()
            return goal
        
        # Replace lowest priority goal if new one is higher
        if goal.priority.value < self.goals[-1].priority.value:
            self.goals[-1] = goal
            self._sort_goals()
            return goal
        
        return None
    
    def _classify_pattern_to_goal(self, pattern: Any, reward: float) -> GoalType:
        """Classify a pattern into a goal type."""
        if reward > 5.0:
            return GoalType.RESOURCE
        elif reward < -3.0:
            return GoalType.SURVIVAL
        elif isinstance(pattern, tuple) and len(pattern) >= 3:
            if pattern[0] == 1:  # Food observed
                return GoalType.RESOURCE
            elif pattern[1] == 1:  # Danger observed
                return GoalType.SURVIVAL
            elif pattern[2] is not None:  # Artifact observed
                return GoalType.EXPLORATION
        return GoalType.EXPLORATION
    
    def _calculate_priority(
        self,
        goal_type: GoalType,
        energy: float,
        reward: float,
    ) -> GoalPriority:
        """Calculate goal priority."""
        # Survival is always high priority if energy is low
        if goal_type == GoalType.SURVIVAL and energy < 20:
            return GoalPriority.CRITICAL
        elif goal_type == GoalType.SURVIVAL:
            return GoalPriority.HIGH
        elif goal_type == GoalType.RESOURCE and energy < 40:
            return GoalPriority.HIGH
        elif goal_type == GoalType.REPRODUCTION and energy > 60:
            return GoalPriority.HIGH
        elif goal_type == GoalType.EXPLORATION:
            return GoalPriority.MEDIUM
        else:
            return GoalPriority.LOW
    
    def _sort_goals(self):
        """Sort goals by priority."""
        self.goals.sort(key=lambda g: (g.priority.value, -g.value))
    
    def select_goal(self) -> Optional[Goal]:
        """Select the highest priority goal to pursue."""
        if not self.goals:
            return None
        
        # Remove completed or expired goals
        self.goals = [g for g in self.goals if g.progress < 1.0]
        
        if not self.goals:
            return None
        
        self.current_goal = self.goals[0]
        return self.current_goal
    
    def update_goal_progress(self, goal: Goal, progress: float):
        """Update progress on a goal."""
        goal.progress = min(1.0, progress)
        if goal.progress >= 1.0:
            # Goal completed
            self._on_goal_completed(goal)
    
    def _on_goal_completed(self, goal: Goal):
        """Handle goal completion."""
        # Could spawn subgoals, update semantic memory, etc.
        pass
    
    # =====================================================
    # PLANNING
    # =====================================================
    
    def plan(self, goal: Goal, world_state: Dict, horizon: int = None) -> Optional[Plan]:
        """
        Create a plan to achieve a goal.
        
        Args:
            goal: The goal to plan for
            world_state: Current world state
            horizon: Planning horizon (default: self.planning_horizon)
            
        Returns:
            Plan if one can be created
        """
        if horizon is None:
            horizon = self.planning_horizon
        
        actions = []
        
        if goal.type == GoalType.SURVIVAL:
            # Plan to avoid danger
            actions = self._plan_survival(world_state, horizon)
        
        elif goal.type == GoalType.RESOURCE:
            # Plan to gather resources
            actions = self._plan_resource(world_state, horizon)
        
        elif goal.type == GoalType.EXPLORATION:
            # Plan exploration
            actions = self._plan_exploration(world_state, horizon)
        
        elif goal.type == GoalType.REPRODUCTION:
            # Plan reproduction
            actions = self._plan_reproduction(world_state, horizon)
        
        if actions:
            plan = Plan(
                goal=goal,
                actions=actions,
                expected_value=self._estimate_plan_value(actions),
            )
            self.current_plan = plan
            return plan
        
        return None
    
    def _plan_survival(self, world_state: Dict, horizon: int) -> List[Tuple[str, Any]]:
        """Plan survival actions."""
        actions = []
        danger_pos = world_state.get('danger_positions', [])
        safe_zones = world_state.get('safe_zones', [])
        
        if safe_zones:
            # Move toward nearest safe zone
            actions.append(('move_toward', safe_zones[0]))
        else:
            # Random exploration for safety
            actions.append(('explore', None))
        
        return actions[:horizon]
    
    def _plan_resource(self, world_state: Dict, horizon: int) -> List[Tuple[str, Any]]:
        """Plan resource gathering."""
        actions = []
        food_positions = world_state.get('food_positions', [])
        
        if food_positions:
            # Move toward nearest food
            actions.append(('move_toward', food_positions[0]))
            actions.append(('consume', food_positions[0]))
        else:
            # Explore for food
            actions.append(('explore_food', None))
        
        return actions[:horizon]
    
    def _plan_exploration(self, world_state: Dict, horizon: int) -> List[Tuple[str, Any]]:
        """Plan exploration."""
        actions = []
        unexplored = world_state.get('unexplored_positions', [])
        
        if unexplored:
            for pos in unexplored[:horizon]:
                actions.append(('move_to', pos))
        else:
            actions.append(('random_explore', None))
        
        return actions[:horizon]
    
    def _plan_reproduction(self, world_state: Dict, horizon: int) -> List[Tuple[str, Any]]:
        """Plan reproduction."""
        actions = []
        energy = world_state.get('energy', 0)
        
        if energy > 60:
            actions.append(('find_mate', None))
            actions.append(('reproduce', None))
        else:
            actions.extend(self._plan_resource(world_state, horizon - 1))
        
        return actions[:horizon]
    
    def _estimate_plan_value(self, actions: List[Tuple[str, Any]]) -> float:
        """Estimate the expected value of a plan."""
        value = 0.0
        for action, _ in actions:
            if action in ['consume', 'reproduce']:
                value += 5.0
            elif action in ['move_toward', 'move_to']:
                value += 1.0
            elif action == 'explore':
                value += 0.5
        return value
    
    # =====================================================
    # MEMORY
    # =====================================================
    
    def remember(
        self,
        step: int,
        event_type: str,
        location: Tuple[int, int],
        pattern: Any,
        reward: float,
        outcome: str,
    ):
        """Store an episodic memory."""
        # Calculate emotions
        emotions = {
            'surprise': self._calculate_surprise(pattern),
            'satisfaction': max(0, reward) / 10.0,
            'fear': max(0, -reward) / 5.0,
        }
        
        memory = EpisodicMemory(
            step=step,
            event_type=event_type,
            location=location,
            pattern=pattern,
            reward=reward,
            outcome=outcome,
            emotions=emotions,
        )
        
        self.episodic_memory.append(memory)
        
        # Manage capacity
        if len(self.episodic_memory) > self.memory_capacity:
            self._compress_memory()
        
        # Update semantic memory
        self._update_semantic_memory(pattern, reward, step)
        
        # Update prediction model
        self._update_transition_model(pattern, reward)
    
    def _calculate_surprise(self, pattern: Any) -> float:
        """Calculate surprise of a pattern."""
        if pattern not in self.explored_patterns:
            self.explored_patterns.add(pattern)
            return 1.0
        
        count = self.pattern_frequency[pattern]
        if count == 0:
            return 1.0
        
        return 1.0 / (1.0 + count)
    
    def _compress_memory(self):
        """Compress episodic memory into semantic memory."""
        # Keep most emotionally significant memories
        self.episodic_memory.sort(
            key=lambda m: max(m.emotions.values()),
            reverse=True
        )
        
        # Keep top half
        self.episodic_memory = self.episodic_memory[:self.memory_capacity // 2]
    
    def _update_semantic_memory(self, pattern: Any, reward: float, step: int):
        """Update semantic memory from pattern."""
        if pattern in self.semantic_memory:
            mem = self.semantic_memory[pattern]
            mem.value = mem.value * 0.9 + reward * 0.1
            mem.source_count += 1
            mem.last_updated = step
            mem.confidence = min(1.0, mem.source_count / 10.0)
        else:
            self.semantic_memory[pattern] = SemanticMemory(
                pattern=pattern,
                meaning=self._infer_meaning(pattern),
                value=reward,
                confidence=0.1,
                source_count=1,
                last_updated=step,
            )
        
        self.pattern_frequency[pattern] += 1
    
    def _infer_meaning(self, pattern: Any) -> str:
        """Infer meaning from pattern structure."""
        if isinstance(pattern, tuple):
            if len(pattern) >= 4:
                food, danger, artifact, time = pattern[0], pattern[1], pattern[2], pattern[3]
                parts = []
                if food:
                    parts.append("food")
                if danger:
                    parts.append("danger")
                if artifact:
                    parts.append(f"artifact-{artifact[0] if isinstance(artifact, tuple) else artifact}")
                parts.append(f"time-{time}")
                return "/".join(parts)
        
        return "unknown"
    
    def _update_transition_model(self, pattern: Any, reward: float):
        """Update transition prediction model."""
        # Simplified - track pattern-reward associations
        self.reward_model[pattern] = self.reward_model.get(pattern, 0) * 0.9 + reward * 0.1
    
    def recall(self, query: Any, limit: int = 5) -> List[EpisodicMemory]:
        """Recall memories matching a query."""
        matches = []
        for mem in self.episodic_memory:
            if self._matches_query(mem, query):
                matches.append(mem)
        
        # Sort by relevance (reward magnitude and recency)
        matches.sort(key=lambda m: (abs(m.reward), -m.step), reverse=True)
        return matches[:limit]
    
    def _matches_query(self, memory: EpisodicMemory, query: Any) -> bool:
        """Check if memory matches query."""
        if isinstance(query, dict):
            for key, value in query.items():
                if getattr(memory, key, None) != value:
                    return False
            return True
        elif isinstance(query, tuple):
            return memory.pattern == query
        return True
    
    # =====================================================
    # PREDICTION
    # =====================================================
    
    def predict(self, pattern: Any, action: str) -> Tuple[Any, float]:
        """
        Predict outcome of an action given a pattern.
        
        Args:
            pattern: Current pattern
            action: Action to take
            
        Returns:
            (predicted_pattern, expected_reward)
        """
        key = (pattern, action)
        
        if key in self.transition_counts:
            # Most likely next pattern
            transitions = self.transition_counts[key]
            if transitions:
                predicted = max(transitions, key=transitions.get)
                expected_reward = self.reward_model.get(predicted, 0.0)
                return predicted, expected_reward
        
        # No data - return current pattern
        return pattern, 0.0
    
    # =====================================================
    # INNOVATION
    # =====================================================
    
    def is_novel(self, pattern: Any) -> bool:
        """Check if a pattern is novel."""
        if pattern not in self.explored_patterns:
            return True
        
        freq = self.pattern_frequency.get(pattern, 0)
        return freq < 5  # Still novel if seen fewer than 5 times
    
    def get_exploration_bonus(self, pattern: Any) -> float:
        """Get exploration bonus for a pattern."""
        if self.is_novel(pattern):
            return self.novelty_threshold * 10.0
        return 0.0
    
    # =====================================================
    # STATUS
    # =====================================================
    
    def status(self) -> Dict[str, Any]:
        """Get cognition status."""
        return {
            'goals': len(self.goals),
            'current_goal': self.current_goal.type.value if self.current_goal else None,
            'episodic_memories': len(self.episodic_memory),
            'semantic_memories': len(self.semantic_memory),
            'patterns_known': len(self.pattern_frequency),
            'novel_patterns': len(self.explored_patterns),
        }
    
    def summary(self) -> str:
        """Get human-readable summary."""
        s = self.status()
        return (
            f"🧠 Cognition Status\n"
            f"   Goals: {s['goals']}\n"
            f"   Current Goal: {s['current_goal']}\n"
            f"   Episodic Memories: {s['episodic_memories']}\n"
            f"   Semantic Memories: {s['semantic_memories']}\n"
            f"   Patterns Known: {s['patterns_known']}\n"
        )
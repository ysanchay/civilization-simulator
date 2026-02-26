"""Multi-step planning system."""

from typing import List, Tuple, Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class Action:
    """Represents a single action in a plan."""
    action_type: str
    target: Any
    expected_value: float = 0.0
    
    def __str__(self):
        return f"{self.action_type}({self.target})"


class Planner:
    """
    Multi-step symbolic planner for agents.
    
    Creates action sequences to achieve goals.
    """
    
    def __init__(self, horizon: int = 5):
        self.horizon = horizon
        self.action_costs = {
            'move': 0.1,
            'consume': 0.0,
            'explore': 0.2,
            'communicate': 0.1,
            'reproduce': 0.5,
        }
    
    def plan(
        self,
        goal_type: str,
        current_state: Dict[str, Any],
        world_state: Dict[str, Any],
    ) -> List[Action]:
        """
        Create a plan to achieve a goal.
        
        Args:
            goal_type: Type of goal
            current_state: Agent's current state
            world_state: Current world state
            
        Returns:
            List of actions
        """
        if goal_type == 'survival':
            return self._plan_survival(current_state, world_state)
        elif goal_type == 'resource':
            return self._plan_resource(current_state, world_state)
        elif goal_type == 'exploration':
            return self._plan_exploration(current_state, world_state)
        elif goal_type == 'reproduction':
            return self._plan_reproduction(current_state, world_state)
        else:
            return self._plan_generic(current_state, world_state)
    
    def _plan_survival(
        self,
        current_state: Dict,
        world_state: Dict,
    ) -> List[Action]:
        """Plan survival actions."""
        actions = []
        
        danger_pos = world_state.get('danger_positions', [])
        safe_zones = world_state.get('safe_zones', [])
        
        if safe_zones:
            actions.append(Action('move', safe_zones[0], expected_value=5.0))
        else:
            actions.append(Action('explore', None, expected_value=1.0))
        
        return actions[:self.horizon]
    
    def _plan_resource(
        self,
        current_state: Dict,
        world_state: Dict,
    ) -> List[Action]:
        """Plan resource gathering."""
        actions = []
        
        food_positions = world_state.get('food_positions', [])
        
        if food_positions:
            actions.append(Action('move', food_positions[0], expected_value=3.0))
            actions.append(Action('consume', food_positions[0], expected_value=5.0))
        else:
            actions.append(Action('explore', None, expected_value=1.0))
        
        return actions[:self.horizon]
    
    def _plan_exploration(
        self,
        current_state: Dict,
        world_state: Dict,
    ) -> List[Action]:
        """Plan exploration."""
        actions = []
        
        unexplored = world_state.get('unexplored_positions', [])
        
        if unexplored:
            for pos in unexplored[:self.horizon]:
                actions.append(Action('move', pos, expected_value=1.0))
        else:
            actions.append(Action('explore', None, expected_value=0.5))
        
        return actions[:self.horizon]
    
    def _plan_reproduction(
        self,
        current_state: Dict,
        world_state: Dict,
    ) -> List[Action]:
        """Plan reproduction."""
        actions = []
        
        energy = current_state.get('energy', 0)
        
        if energy > 60:
            actions.append(Action('reproduce', None, expected_value=10.0))
        else:
            # Need more energy first
            actions.extend(self._plan_resource(current_state, world_state))
        
        return actions[:self.horizon]
    
    def _plan_generic(
        self,
        current_state: Dict,
        world_state: Dict,
    ) -> List[Action]:
        """Generic planning fallback."""
        return [Action('explore', None, expected_value=0.5)]
    
    def evaluate_plan(self, actions: List[Action]) -> float:
        """Evaluate the expected value of a plan."""
        total_value = 0.0
        discount = 1.0
        
        for action in actions:
            cost = self.action_costs.get(action.action_type, 0.1)
            total_value += (action.expected_value - cost) * discount
            discount *= 0.9  # Future discount
        
        return total_value
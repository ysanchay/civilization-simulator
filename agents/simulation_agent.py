"""
SimulationController Agent

IDENTITY: "I am the orchestrator. I manage time, state, and coordination."

ROLE: Master coordinator of the entire simulation

RESPONSIBILITIES:
- Control simulation speed (pause, resume, step, accelerate)
- Manage simulation state and checkpoints
- Coordinate all other agents
- Handle simulation lifecycle (start, stop, reset)
- Emit events for other agents to react to
"""

import time
import pickle
import os
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from enum import Enum


class SimulationState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class SimulationController:
    """
    Master orchestrator for the civilization simulation.
    
    Coordinates all agents and manages the simulation lifecycle.
    """
    
    def __init__(
        self,
        world,
        tick_rate: float = 0.05,
        checkpoint_dir: str = "checkpoints",
        auto_checkpoint: int = 1000,
    ):
        self.world = world
        self.tick_rate = tick_rate  # seconds between ticks
        self.checkpoint_dir = checkpoint_dir
        self.auto_checkpoint_interval = auto_checkpoint
        
        # State
        self.state = SimulationState.IDLE
        self.step_count = 0
        self.start_time: Optional[float] = None
        self.elapsed_time: float = 0.0
        
        # Agent references
        self.world_agent = None
        self.cognition_agent = None
        self.culture_agent = None
        self.competition_agent = None
        self.innovation_agent = None
        self.visualization_agent = None
        self.experiment_agent = None
        
        # Event callbacks
        self.event_hooks: Dict[str, list] = {
            'on_tick': [],
            'on_checkpoint': [],
            'on_epoch': [],
            'on_extinction': [],
            'on_milestone': [],
        }
        
        # Checkpoint directory
        os.makedirs(checkpoint_dir, exist_ok=True)
    
    # =====================================================
    # AGENT REGISTRATION
    # =====================================================
    
    def register_agent(self, agent_type: str, agent):
        """Register an agent with the controller."""
        setattr(self, f"{agent_type}_agent", agent)
    
    # =====================================================
    # SIMULATION LIFECYCLE
    # =====================================================
    
    def start(self):
        """Start the simulation."""
        if self.state == SimulationState.RUNNING:
            return
        
        self.state = SimulationState.RUNNING
        self.start_time = time.time()
        print(f"🚀 Simulation started at {datetime.now().isoformat()}")
    
    def pause(self):
        """Pause the simulation."""
        if self.state == SimulationState.RUNNING:
            self.state = SimulationState.PAUSED
            self.elapsed_time += time.time() - self.start_time
            print(f"⏸️ Simulation paused at step {self.step_count}")
    
    def resume(self):
        """Resume a paused simulation."""
        if self.state == SimulationState.PAUSED:
            self.state = SimulationState.RUNNING
            self.start_time = time.time()
            print(f"▶️ Simulation resumed at step {self.step_count}")
    
    def stop(self):
        """Stop the simulation."""
        self.state = SimulationState.STOPPED
        if self.start_time:
            self.elapsed_time += time.time() - self.start_time
        print(f"🛑 Simulation stopped at step {self.step_count}")
    
    def reset(self):
        """Reset the simulation to initial state."""
        self.state = SimulationState.IDLE
        self.step_count = 0
        self.elapsed_time = 0.0
        self.start_time = None
        print("🔄 Simulation reset")
    
    # =====================================================
    # MAIN LOOP
    # =====================================================
    
    def tick(self):
        """Advance simulation by one step."""
        if self.state != SimulationState.RUNNING:
            return
        
        self.step_count += 1
        
        # Advance world
        self.world.step()
        
        # Trigger event hooks
        self._emit('on_tick', {'step': self.step_count})
        
        # Auto-checkpoint
        if self.step_count % self.auto_checkpoint_interval == 0:
            self.save_checkpoint()
        
        # Speed control
        time.sleep(self.tick_rate)
    
    def run(self, max_steps: Optional[int] = None, max_time: Optional[float] = None):
        """
        Run the simulation until stopped or limits reached.
        
        Args:
            max_steps: Maximum number of steps to run
            max_time: Maximum time in seconds to run
        """
        self.start()
        start = time.time()
        
        while self.state == SimulationState.RUNNING:
            # Check limits
            if max_steps and self.step_count >= max_steps:
                print(f"✅ Reached max steps: {max_steps}")
                break
            
            if max_time and (time.time() - start) >= max_time:
                print(f"⏱️ Reached max time: {max_time}s")
                break
            
            # Check extinction
            if len(self.world.agents) == 0:
                print("☠️ All agents extinct!")
                self._emit('on_extinction', {'step': self.step_count})
                break
            
            self.tick()
        
        self.stop()
    
    # =====================================================
    # SPEED CONTROL
    # =====================================================
    
    def set_speed(self, ticks_per_second: float):
        """Set simulation speed in ticks per second."""
        self.tick_rate = 1.0 / max(0.001, ticks_per_second)
    
    def accelerate(self, factor: float = 2.0):
        """Speed up simulation by factor."""
        self.tick_rate = max(0.001, self.tick_rate / factor)
    
    def decelerate(self, factor: float = 2.0):
        """Slow down simulation by factor."""
        self.tick_rate *= factor
    
    # =====================================================
    # CHECKPOINTS
    # =====================================================
    
    def save_checkpoint(self, name: Optional[str] = None):
        """Save simulation state to checkpoint file."""
        if name is None:
            name = f"checkpoint_{self.step_count:08d}.pkl"
        
        path = os.path.join(self.checkpoint_dir, name)
        
        state = {
            'step_count': self.step_count,
            'elapsed_time': self.elapsed_time + (
                time.time() - self.start_time if self.start_time else 0
            ),
            'world_state': self._serialize_world(),
            'timestamp': datetime.now().isoformat(),
        }
        
        with open(path, 'wb') as f:
            pickle.dump(state, f)
        
        print(f"💾 Checkpoint saved: {name}")
        self._emit('on_checkpoint', {'path': path, 'step': self.step_count})
    
    def load_checkpoint(self, name: str):
        """Load simulation state from checkpoint file."""
        path = os.path.join(self.checkpoint_dir, name)
        
        with open(path, 'rb') as f:
            state = pickle.load(f)
        
        self.step_count = state['step_count']
        self.elapsed_time = state['elapsed_time']
        self._deserialize_world(state['world_state'])
        
        print(f"📂 Checkpoint loaded: {name} (step {self.step_count})")
    
    def _serialize_world(self) -> Dict[str, Any]:
        """Serialize world state for checkpointing."""
        return {
            'agents': [(a.name, a.energy, a.generation, a.tribe_id, a.x, a.y) 
                      for a in self.world.agents],
            'tribes': {tid: tribe.summary() for tid, tribe in self.world.tribes.items()},
            'step_count': self.world.step_count,
        }
    
    def _deserialize_world(self, state: Dict[str, Any]):
        """Deserialize world state from checkpoint."""
        # Implementation depends on world structure
        pass
    
    # =====================================================
    # EVENTS
    # =====================================================
    
    def on(self, event: str, callback: Callable):
        """Register an event callback."""
        if event in self.event_hooks:
            self.event_hooks[event].append(callback)
    
    def _emit(self, event: str, data: Dict[str, Any]):
        """Emit an event to all registered callbacks."""
        for callback in self.event_hooks.get(event, []):
            callback(data)
    
    # =====================================================
    # STATUS
    # =====================================================
    
    def status(self) -> Dict[str, Any]:
        """Get current simulation status."""
        return {
            'state': self.state.value,
            'step': self.step_count,
            'elapsed_time': self.elapsed_time + (
                time.time() - self.start_time if self.start_time else 0
            ),
            'tick_rate': self.tick_rate,
            'agents': len(self.world.agents),
            'tribes': len(self.world.tribes),
        }
    
    def summary(self) -> str:
        """Get human-readable summary."""
        s = self.status()
        return (
            f"📊 Simulation Status\n"
            f"   State: {s['state']}\n"
            f"   Step: {s['step']}\n"
            f"   Time: {s['elapsed_time']:.1f}s\n"
            f"   Agents: {s['agents']}\n"
            f"   Tribes: {s['tribes']}\n"
        )
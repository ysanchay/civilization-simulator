"""Experiment runner."""

from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, field
import time
import random


@dataclass
class RunResult:
    """Result from a single experiment run."""
    run_id: int
    seed: int
    success: bool
    duration: float
    metrics: Dict[str, float] = field(default_factory=dict)
    history: List[Dict[str, float]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class ExperimentRunner:
    """Runs experiments and collects results."""
    
    def __init__(self):
        self.results: List[RunResult] = []
    
    def run(
        self,
        simulation_factory: Callable,
        num_runs: int = 10,
        max_steps: int = 10000,
        seed: Optional[int] = None,
        parameters: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable] = None,
    ) -> List[RunResult]:
        """
        Run an experiment multiple times.
        
        Args:
            simulation_factory: Function to create simulation
            num_runs: Number of runs
            max_steps: Maximum steps per run
            seed: Random seed
            parameters: Parameters for simulation
            progress_callback: Callback for progress updates
            
        Returns:
            List of run results
        """
        self.results = []
        
        for run_id in range(num_runs):
            run_seed = seed + run_id if seed else random.randint(0, 1000000)
            random.seed(run_seed)
            
            result = self._run_single(
                run_id=run_id,
                seed=run_seed,
                simulation_factory=simulation_factory,
                max_steps=max_steps,
                parameters=parameters or {},
            )
            
            self.results.append(result)
            
            if progress_callback:
                progress_callback(run_id + 1, num_runs, result)
        
        return self.results
    
    def _run_single(
        self,
        run_id: int,
        seed: int,
        simulation_factory: Callable,
        max_steps: int,
        parameters: Dict[str, Any],
    ) -> RunResult:
        """Run a single experiment."""
        result = RunResult(
            run_id=run_id,
            seed=seed,
            success=False,
            duration=0,
        )
        
        start_time = time.time()
        
        try:
            simulation = simulation_factory(parameters)
            
            for step in range(max_steps):
                simulation.tick()
                
                # Check for extinction
                if hasattr(simulation, 'world') and len(simulation.world.agents) == 0:
                    break
            
            # Collect final metrics
            result.metrics = self._collect_metrics(simulation)
            result.success = True
            
        except Exception as e:
            result.errors.append(str(e))
        
        result.duration = time.time() - start_time
        
        return result
    
    def _collect_metrics(self, simulation: Any) -> Dict[str, float]:
        """Collect metrics from simulation."""
        metrics = {}
        
        world = getattr(simulation, 'world', None)
        
        if world:
            metrics['population'] = len(getattr(world, 'agents', []))
            metrics['tribes'] = len(getattr(world, 'tribes', {}))
            
            agents = getattr(world, 'agents', [])
            if agents:
                metrics['mean_energy'] = sum(a.energy for a in agents) / len(agents)
        
        return metrics
    
    def get_aggregated_results(self) -> Dict[str, Any]:
        """Get aggregated results."""
        if not self.results:
            return {}
        
        successful = [r for r in self.results if r.success]
        
        if not successful:
            return {'success_rate': 0}
        
        metrics = {}
        for result in successful:
            for key, value in result.metrics.items():
                if key not in metrics:
                    metrics[key] = []
                metrics[key].append(value)
        
        aggregated = {
            'total_runs': len(self.results),
            'successful_runs': len(successful),
            'success_rate': len(successful) / len(self.results),
            'mean_duration': sum(r.duration for r in successful) / len(successful),
        }
        
        for key, values in metrics.items():
            aggregated[f'{key}_mean'] = sum(values) / len(values)
            aggregated[f'{key}_std'] = (sum((v - aggregated[f'{key}_mean'])**2 for v in values) / len(values)) ** 0.5
        
        return aggregated
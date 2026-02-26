"""
ExperimentAgent

IDENTITY: "I am the scientist. I test, measure, and report."

ROLE: Controlled experiments and evaluation

RESPONSIBILITIES:
- Run controlled experiments with fixed parameters
- Compare against baselines
- Collect and analyze statistical data
- Generate research reports
- Track key metrics across runs
- Export data for publication
"""

import json
import random
import statistics
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum


class ExperimentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ExperimentConfig:
    """Configuration for an experiment."""
    name: str
    seed: Optional[int] = None
    max_steps: int = 10000
    num_runs: int = 10
    parameters: Dict[str, Any] = field(default_factory=dict)
    baselines: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=lambda: [
        'population', 'energy_mean', 'symbol_count', 
        'tribe_count', 'abstraction_depth', 'temporal_accuracy'
    ])


@dataclass
class ExperimentResult:
    """Results from a single experiment run."""
    run_id: int
    seed: int
    status: str
    duration_seconds: float
    final_metrics: Dict[str, float]
    metrics_history: List[Dict[str, float]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class ExperimentReport:
    """Aggregated report from multiple runs."""
    config: ExperimentConfig
    start_time: str
    end_time: Optional[str] = None
    status: str = "pending"
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    results: List[ExperimentResult] = field(default_factory=list)
    aggregated_metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    comparisons: Dict[str, Dict[str, float]] = field(default_factory=dict)


class ExperimentAgent:
    """
    Manages controlled experiments for the civilization simulation.
    
    Handles experiment setup, execution, analysis, and reporting.
    """
    
    def __init__(
        self,
        experiments_dir: str = "experiments",
        auto_save: bool = True,
    ):
        self.experiments_dir = Path(experiments_dir)
        self.auto_save = auto_save
        
        # Create directory
        self.experiments_dir.mkdir(parents=True, exist_ok=True)
        
        # Active experiments
        self.experiments: Dict[str, ExperimentReport] = {}
        self.current_experiment: Optional[str] = None
        
        # Baseline configurations
        self.baselines: Dict[str, ExperimentConfig] = {}
        
        # Statistical analysis
        self.significance_level = 0.05
    
    # =====================================================
    # BASELINE MANAGEMENT
    # =====================================================
    
    def register_baseline(self, name: str, config: ExperimentConfig):
        """
        Register a baseline configuration for comparison.
        
        Args:
            name: Baseline name
            config: Configuration for the baseline
        """
        self.baselines[name] = config
        print(f"📊 Registered baseline: {name}")
    
    def create_default_baselines(self):
        """Create default baseline configurations."""
        # Minimal baseline - basic simulation
        self.register_baseline("minimal", ExperimentConfig(
            name="minimal",
            max_steps=5000,
            num_runs=5,
            parameters={
                "world_size": (10, 10),
                "initial_agents": 3,
                "innovation_enabled": False,
                "competition_enabled": False,
            }
        ))
        
        # Standard baseline - all features
        self.register_baseline("standard", ExperimentConfig(
            name="standard",
            max_steps=10000,
            num_runs=10,
            parameters={
                "world_size": (20, 20),
                "initial_agents": 5,
                "innovation_enabled": True,
                "competition_enabled": True,
            }
        ))
        
        # High innovation baseline
        self.register_baseline("high_innovation", ExperimentConfig(
            name="high_innovation",
            max_steps=10000,
            num_runs=10,
            parameters={
                "world_size": (20, 20),
                "initial_agents": 5,
                "innovation_enabled": True,
                "innovation_bonus": 3.0,
                "competition_enabled": False,
            }
        ))
    
    # =====================================================
    # EXPERIMENT SETUP
    # =====================================================
    
    def create_experiment(
        self,
        name: str,
        parameters: Dict[str, Any],
        max_steps: int = 10000,
        num_runs: int = 10,
        seed: Optional[int] = None,
        baselines: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
    ) -> ExperimentConfig:
        """
        Create a new experiment configuration.
        
        Args:
            name: Experiment name
            parameters: Experiment parameters
            max_steps: Maximum steps per run
            num_runs: Number of runs
            seed: Random seed
            baselines: Baseline names for comparison
            metrics: Metrics to track
            
        Returns:
            ExperimentConfig object
        """
        config = ExperimentConfig(
            name=name,
            seed=seed,
            max_steps=max_steps,
            num_runs=num_runs,
            parameters=parameters,
            baselines=baselines or [],
            metrics=metrics or [
                'population', 'energy_mean', 'symbol_count',
                'tribe_count', 'abstraction_depth', 'temporal_accuracy'
            ]
        )
        
        # Create experiment report
        report = ExperimentReport(
            config=config,
            start_time=datetime.now().isoformat(),
            status=ExperimentStatus.PENDING.value,
        )
        
        self.experiments[name] = report
        
        print(f"🧪 Created experiment: {name}")
        return config
    
    # =====================================================
    # EXPERIMENT EXECUTION
    # =====================================================
    
    def run_experiment(
        self,
        config: ExperimentConfig,
        simulation_factory: Callable,
        progress_callback: Optional[Callable] = None,
    ) -> ExperimentReport:
        """
        Run an experiment.
        
        Args:
            config: Experiment configuration
            simulation_factory: Function that creates a simulation
            progress_callback: Optional callback for progress updates
            
        Returns:
            ExperimentReport with results
        """
        report = self.experiments.get(config.name)
        if report is None:
            report = ExperimentReport(
                config=config,
                start_time=datetime.now().isoformat(),
            )
            self.experiments[config.name] = report
        
        report.status = ExperimentStatus.RUNNING.value
        self.current_experiment = config.name
        
        print(f"🧪 Running experiment: {config.name}")
        print(f"   Runs: {config.num_runs}, Steps: {config.max_steps}")
        
        for run_id in range(config.num_runs):
            # Set random seed for reproducibility
            seed = config.seed + run_id if config.seed else random.randint(0, 1000000)
            random.seed(seed)
            
            print(f"   Run {run_id + 1}/{config.num_runs} (seed: {seed})")
            
            result = self._run_single(
                run_id=run_id,
                seed=seed,
                config=config,
                simulation_factory=simulation_factory,
            )
            
            report.results.append(result)
            report.total_runs += 1
            
            if result.status == "completed":
                report.successful_runs += 1
            else:
                report.failed_runs += 1
            
            if progress_callback:
                progress_callback(run_id + 1, config.num_runs, result)
            
            if self.auto_save:
                self._save_report(report)
        
        # Aggregate results
        self._aggregate_results(report)
        
        # Compare with baselines
        if config.baselines:
            self._compare_baselines(report)
        
        report.end_time = datetime.now().isoformat()
        report.status = ExperimentStatus.COMPLETED.value
        
        self.current_experiment = None
        
        print(f"✅ Experiment completed: {config.name}")
        print(f"   Successful: {report.successful_runs}/{report.total_runs}")
        
        return report
    
    def _run_single(
        self,
        run_id: int,
        seed: int,
        config: ExperimentConfig,
        simulation_factory: Callable,
    ) -> ExperimentResult:
        """Run a single experiment instance."""
        import time
        
        result = ExperimentResult(
            run_id=run_id,
            seed=seed,
            status="running",
            duration_seconds=0,
            final_metrics={},
        )
        
        start_time = time.time()
        
        try:
            # Create simulation with parameters
            simulation = simulation_factory(config.parameters)
            
            # Run simulation
            step = 0
            while step < config.max_steps:
                # Check for extinction
                if hasattr(simulation, 'world') and len(simulation.world.agents) == 0:
                    result.events.append({
                        'step': step,
                        'type': 'extinction',
                    })
                    break
                
                # Advance simulation
                simulation.tick()
                step += 1
                
                # Collect metrics periodically
                if step % 100 == 0:
                    metrics = self._collect_metrics(simulation, config.metrics)
                    result.metrics_history.append(metrics)
            
            # Final metrics
            result.final_metrics = self._collect_metrics(simulation, config.metrics)
            result.status = "completed"
            
        except Exception as e:
            result.status = "failed"
            result.errors.append(str(e))
        
        result.duration_seconds = time.time() - start_time
        
        return result
    
    def _collect_metrics(self, simulation: Any, metrics: List[str]) -> Dict[str, float]:
        """Collect metrics from simulation."""
        result = {}
        
        world = getattr(simulation, 'world', None)
        agents = getattr(world, 'agents', []) if world else []
        tribes = getattr(world, 'tribes', {}) if world else {}
        
        for metric in metrics:
            try:
                if metric == 'population':
                    result[metric] = len(agents)
                
                elif metric == 'energy_mean':
                    if agents:
                        result[metric] = statistics.mean(a.energy for a in agents)
                    else:
                        result[metric] = 0
                
                elif metric == 'energy_variance':
                    if len(agents) > 1:
                        result[metric] = statistics.variance(a.energy for a in agents)
                    else:
                        result[metric] = 0
                
                elif metric == 'symbol_count':
                    result[metric] = sum(len(t.symbols) for t in tribes.values())
                
                elif metric == 'tribe_count':
                    result[metric] = len(tribes)
                
                elif metric == 'abstraction_depth':
                    max_depth = 0
                    for tribe in tribes.values():
                        depth = 1
                        if hasattr(tribe, 'composed_symbols') and tribe.composed_symbols:
                            depth = 2
                        if hasattr(tribe, 'meta_symbols') and tribe.meta_symbols:
                            depth = 3
                        max_depth = max(max_depth, depth)
                    result[metric] = max_depth
                
                elif metric == 'temporal_accuracy':
                    # Would need access to knowledge metrics
                    result[metric] = 0.0  # Placeholder
                
                elif metric == 'innovation_count':
                    if hasattr(simulation, 'innovation_agent'):
                        result[metric] = simulation.innovation_agent.total_innovations
                    else:
                        result[metric] = 0
                
                elif metric == 'war_count':
                    if hasattr(simulation, 'competition_agent'):
                        result[metric] = simulation.competition_agent.total_wars
                    else:
                        result[metric] = 0
                
                else:
                    result[metric] = 0.0
                    
            except Exception:
                result[metric] = 0.0
        
        return result
    
    # =====================================================
    # ANALYSIS
    # =====================================================
    
    def _aggregate_results(self, report: ExperimentReport):
        """Aggregate metrics across all runs."""
        metric_values: Dict[str, List[float]] = {}
        
        # Collect all values
        for result in report.results:
            if result.status != "completed":
                continue
            
            for metric, value in result.final_metrics.items():
                if metric not in metric_values:
                    metric_values[metric] = []
                metric_values[metric].append(value)
        
        # Calculate statistics
        for metric, values in metric_values.items():
            if not values:
                continue
            
            report.aggregated_metrics[metric] = {
                'mean': statistics.mean(values),
                'std': statistics.stdev(values) if len(values) > 1 else 0,
                'min': min(values),
                'max': max(values),
                'median': statistics.median(values),
            }
    
    def _compare_baselines(self, report: ExperimentReport):
        """Compare experiment results with baselines."""
        for baseline_name in report.config.baselines:
            if baseline_name not in self.experiments:
                continue
            
            baseline = self.experiments[baseline_name]
            
            report.comparisons[baseline_name] = {}
            
            for metric in report.aggregated_metrics:
                if metric not in baseline.aggregated_metrics:
                    continue
                
                exp_mean = report.aggregated_metrics[metric]['mean']
                base_mean = baseline.aggregated_metrics[metric]['mean']
                
                # Calculate percent difference
                if base_mean != 0:
                    pct_diff = ((exp_mean - base_mean) / base_mean) * 100
                else:
                    pct_diff = 0
                
                report.comparisons[baseline_name][metric] = {
                    'experiment_mean': exp_mean,
                    'baseline_mean': base_mean,
                    'percent_difference': pct_diff,
                    'improvement': pct_diff > 0,
                }
    
    # =====================================================
    # REPORTING
    # =====================================================
    
    def generate_report(self, experiment_name: str) -> str:
        """
        Generate a human-readable report.
        
        Args:
            experiment_name: Name of the experiment
            
        Returns:
            Report as a string
        """
        report = self.experiments.get(experiment_name)
        if not report:
            return f"Experiment not found: {experiment_name}"
        
        lines = []
        lines.append("=" * 60)
        lines.append(f"EXPERIMENT REPORT: {report.config.name}")
        lines.append("=" * 60)
        lines.append("")
        
        # Configuration
        lines.append("CONFIGURATION")
        lines.append("-" * 40)
        lines.append(f"  Max Steps: {report.config.max_steps}")
        lines.append(f"  Num Runs: {report.config.num_runs}")
        lines.append(f"  Seed: {report.config.seed}")
        lines.append(f"  Parameters: {json.dumps(report.config.parameters, indent=4)}")
        lines.append("")
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 40)
        lines.append(f"  Total Runs: {report.total_runs}")
        lines.append(f"  Successful: {report.successful_runs}")
        lines.append(f"  Failed: {report.failed_runs}")
        lines.append(f"  Status: {report.status}")
        lines.append("")
        
        # Aggregated Metrics
        lines.append("AGGREGATED METRICS")
        lines.append("-" * 40)
        for metric, stats in report.aggregated_metrics.items():
            lines.append(f"  {metric}:")
            lines.append(f"    Mean: {stats['mean']:.4f}")
            lines.append(f"    Std:  {stats['std']:.4f}")
            lines.append(f"    Min:  {stats['min']:.4f}")
            lines.append(f"    Max:  {stats['max']:.4f}")
        lines.append("")
        
        # Comparisons
        if report.comparisons:
            lines.append("BASELINE COMPARISONS")
            lines.append("-" * 40)
            for baseline, metrics in report.comparisons.items():
                lines.append(f"  vs {baseline}:")
                for metric, values in metrics.items():
                    improvement = "✓" if values['improvement'] else "✗"
                    lines.append(f"    {metric}: {values['percent_difference']:+.2f}% {improvement}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _save_report(self, report: ExperimentReport):
        """Save report to file."""
        path = self.experiments_dir / f"{report.config.name}.json"
        
        # Convert to dict
        data = {
            'config': asdict(report.config),
            'start_time': report.start_time,
            'end_time': report.end_time,
            'status': report.status,
            'total_runs': report.total_runs,
            'successful_runs': report.successful_runs,
            'failed_runs': report.failed_runs,
            'aggregated_metrics': report.aggregated_metrics,
            'comparisons': report.comparisons,
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def export_data(self, experiment_name: str, format: str = "csv") -> str:
        """
        Export experiment data.
        
        Args:
            experiment_name: Name of the experiment
            format: Export format ('csv' or 'json')
            
        Returns:
            Path to exported file
        """
        report = self.experiments.get(experiment_name)
        if not report:
            return f"Experiment not found: {experiment_name}"
        
        if format == "csv":
            return self._export_csv(report)
        else:
            return self._export_json(report)
    
    def _export_csv(self, report: ExperimentReport) -> str:
        """Export results as CSV."""
        import csv
        
        path = self.experiments_dir / f"{report.config.name}_data.csv"
        
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            headers = ['run_id', 'seed', 'status', 'duration'] + list(report.config.metrics)
            writer.writerow(headers)
            
            # Data
            for result in report.results:
                row = [
                    result.run_id,
                    result.seed,
                    result.status,
                    result.duration_seconds,
                ] + [result.final_metrics.get(m, 0) for m in report.config.metrics]
                writer.writerow(row)
        
        return str(path)
    
    def _export_json(self, report: ExperimentReport) -> str:
        """Export results as JSON."""
        path = self.experiments_dir / f"{report.config.name}_data.json"
        
        data = {
            'config': asdict(report.config),
            'results': [asdict(r) for r in report.results],
            'aggregated_metrics': report.aggregated_metrics,
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        return str(path)
    
    # =====================================================
    # STATUS
    # =====================================================
    
    def status(self) -> Dict[str, Any]:
        """Get experiment agent status."""
        return {
            'experiments_count': len(self.experiments),
            'baselines_count': len(self.baselines),
            'current_experiment': self.current_experiment,
            'experiments': list(self.experiments.keys()),
        }
    
    def summary(self) -> str:
        """Get human-readable summary."""
        s = self.status()
        return (
            f"🔬 Experiment Agent Status\n"
            f"   Experiments: {s['experiments_count']}\n"
            f"   Baselines: {s['baselines_count']}\n"
            f"   Current: {s['current_experiment'] or 'None'}\n"
        )
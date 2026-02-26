"""Dashboard for real-time metrics."""

from typing import Dict, List, Any
from collections import deque


class Dashboard:
    """Real-time metrics dashboard."""
    
    def __init__(self, history_size: int = 100):
        self.history_size = history_size
        self.metrics: Dict[str, deque] = {}
    
    def update(self, metrics: Dict[str, float]):
        """Update metrics."""
        for key, value in metrics.items():
            if key not in self.metrics:
                self.metrics[key] = deque(maxlen=self.history_size)
            self.metrics[key].append(value)
    
    def get_current(self) -> Dict[str, float]:
        """Get current metric values."""
        return {k: v[-1] if v else 0 for k, v in self.metrics.items()}
    
    def get_history(self, metric: str) -> List[float]:
        """Get history for a metric."""
        return list(self.metrics.get(metric, []))
    
    def get_stats(self, metric: str) -> Dict[str, float]:
        """Get statistics for a metric."""
        values = list(self.metrics.get(metric, []))
        if not values:
            return {'mean': 0, 'min': 0, 'max': 0}
        
        return {
            'mean': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'current': values[-1],
        }
    
    def render(self) -> str:
        """Render dashboard as string."""
        lines = []
        lines.append("=" * 40)
        lines.append("METRICS DASHBOARD")
        lines.append("=" * 40)
        
        for metric, values in self.metrics.items():
            if values:
                stats = self.get_stats(metric)
                lines.append(f"  {metric}:")
                lines.append(f"    Current: {stats['current']:.2f}")
                lines.append(f"    Mean: {stats['mean']:.2f}")
                lines.append(f"    Range: [{stats['min']:.2f}, {stats['max']:.2f}]")
        
        return '\n'.join(lines)
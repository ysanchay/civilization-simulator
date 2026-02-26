"""
VisualizationAgent

IDENTITY: "I am the eyes. I show what happens."

ROLE: Terminal UI and real-time visualization

RESPONSIBILITIES:
- Render world grid in terminal (ASCII/Unicode)
- Display agent positions and tribes
- Show real-time metrics (population, energy, symbols)
- Highlight events (births, deaths, conflicts, innovations)
- Generate summary reports
- Export visualizations to files
"""

import os
import sys
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from collections import deque


class VisualizationAgent:
    """
    Provides terminal-based visualization for the civilization simulation.
    
    Renders the world grid and metrics in real-time.
    """
    
    def __init__(
        self,
        width: int = 80,
        height: int = 40,
        refresh_rate: float = 0.1,
        color_enabled: bool = True,
    ):
        self.width = width
        self.height = height
        self.refresh_rate = refresh_rate
        self.color_enabled = color_enabled and self._supports_color()
        
        # Display settings
        self.cell_width = 2  # Characters per cell
        self.show_agents = True
        self.show_food = True
        self.show_danger = True
        self.show_artifacts = True
        
        # Event queue for highlighting
        self.event_queue: deque = deque(maxlen=10)
        self.highlight_duration = 10  # Steps to highlight event
        
        # Statistics history
        self.history: Dict[str, deque] = {
            'population': deque(maxlen=100),
            'energy': deque(maxlen=100),
            'symbols': deque(maxlen=100),
            'tribes': deque(maxlen=100),
        }
        
        # ANSI color codes
        self.colors = {
            'reset': '\033[0m',
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'dim': '\033[2m',
            'bold': '\033[1m',
            'bg_red': '\033[41m',
            'bg_green': '\033[42m',
            'bg_yellow': '\033[43m',
            'bg_blue': '\033[44m',
        }
        
        # Tribe colors
        self.tribe_colors = [
            'red', 'green', 'yellow', 'blue', 'magenta',
            'cyan', 'white', 'red', 'green', 'yellow',
        ]
        
        # Legend
        self.legend = {
            'agent': '@',
            'food': '*',
            'danger': '!',
            'artifact': '#',
            'empty': '.',
            'biome_0': '░',  # Plains
            'biome_1': '▒',  # Forest
            'biome_2': '▓',  # Desert
        }
    
    def _supports_color(self) -> bool:
        """Check if terminal supports colors."""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    # =====================================================
    # RENDERING
    # =====================================================
    
    def render(self, world: Any, metrics: Optional[Dict] = None) -> str:
        """
        Render the world and metrics to a string.
        
        Args:
            world: World object
            metrics: Optional metrics dict
            
        Returns:
            Rendered string
        """
        lines = []
        
        # Header
        lines.append(self._render_header(world))
        
        # World grid
        lines.extend(self._render_grid(world))
        
        # Legend
        lines.append(self._render_legend())
        
        # Events
        if self.event_queue:
            lines.extend(self._render_events())
        
        # Metrics
        if metrics:
            lines.extend(self._render_metrics(metrics))
        
        # Tribes
        if hasattr(world, 'tribes') and world.tribes:
            lines.extend(self._render_tribes(world))
        
        return '\n'.join(lines)
    
    def _render_header(self, world: Any) -> str:
        """Render header with simulation info."""
        step = getattr(world, 'step_count', 0)
        time_phase = getattr(world, 'world_time', 0)
        agents = len(getattr(world, 'agents', []))
        
        header = f"{'='*60}\n"
        header += f"  CIVILIZATION SIMULATOR\n"
        header += f"  Step: {step:6d} | Time: {time_phase} | Agents: {agents:3d}\n"
        header += f"{'='*60}\n"
        
        return header
    
    def _render_grid(self, world: Any) -> List[str]:
        """Render the world grid."""
        lines = []
        
        width = min(self.width, getattr(world, 'width', 20))
        height = min(self.height // 2, getattr(world, 'height', 20))
        
        # Top border
        lines.append('+' + '-' * (width * self.cell_width) + '+')
        
        for y in range(height):
            row = []
            row.append('|')
            
            for x in range(width):
                cell = self._render_cell(world, x, y)
                row.append(cell)
            
            row.append('|')
            lines.append(''.join(row))
        
        # Bottom border
        lines.append('+' + '-' * (width * self.cell_width) + '+')
        
        return lines
    
    def _render_cell(self, world: Any, x: int, y: int) -> str:
        """Render a single cell."""
        # Check for agent
        if self.show_agents:
            agent = getattr(world, 'grid', [[]])[y][x] if y < len(getattr(world, 'grid', [])) and x < len(getattr(world, 'grid', [[]])[y]) else None
            if agent:
                tribe_id = getattr(agent, 'tribe_id', 0)
                return self._colorize('@', self._get_tribe_color(tribe_id))
        
        # Check for food
        if self.show_food:
            food = getattr(world, 'food', [[]])
            if y < len(food) and x < len(food[y]) and food[y][x]:
                return self._colorize('*', 'green')
        
        # Check for artifact
        if self.show_artifacts:
            artifacts = getattr(world, 'artifacts', [[]])
            if y < len(artifacts) and x < len(artifacts[y]) and artifacts[y][x]:
                return self._colorize('#', 'magenta')
        
        # Check for danger
        if self.show_danger:
            danger = getattr(world, 'danger_zones', [[]])
            if y < len(danger) and x < len(danger[y]) and danger[y][x] > 1.0:
                return self._colorize('!', 'red')
        
        # Biome
        biomes = getattr(world, 'biomes', [[]])
        if y < len(biomes) and x < len(biomes[y]):
            biome = biomes[y][x]
            biome_chars = ['░', '▒', '▓']
            return self._colorize(biome_chars[biome % 3], 'dim')
        
        return '.'
    
    def _render_legend(self) -> str:
        """Render the legend."""
        legend = f"\n  Legend: "
        legend += self._colorize('@', 'white') + " Agent "
        legend += self._colorize('*', 'green') + " Food "
        legend += self._colorize('!', 'red') + " Danger "
        legend += self._colorize('#', 'magenta') + " Artifact "
        legend += "░ Plains ▒ Forest ▓ Desert"
        return legend
    
    def _render_events(self) -> List[str]:
        """Render recent events."""
        lines = [f"\n  {'─'*50}"]
        lines.append("  Recent Events:")
        
        for event in list(self.event_queue):
            event_str = self._format_event(event)
            lines.append(f"  • {event_str}")
        
        return lines
    
    def _format_event(self, event: Dict) -> str:
        """Format an event for display."""
        event_type = event.get('type', 'unknown')
        step = event.get('step', 0)
        
        if event_type == 'birth':
            agent = event.get('agent', '?')
            tribe = event.get('tribe', '?')
            return f"[{step}] 🎉 Birth: {agent} (Tribe {tribe})"
        elif event_type == 'death':
            agent = event.get('agent', '?')
            tribe = event.get('tribe', '?')
            return f"[{step}] ☠️ Death: {agent} (Tribe {tribe})"
        elif event_type == 'symbol':
            symbol = event.get('symbol', '?')
            tribe = event.get('tribe', '?')
            return f"[{step}] 🔤 Symbol: {symbol} (Tribe {tribe})"
        elif event_type == 'composition':
            comp = event.get('composition', '?')
            tribe = event.get('tribe', '?')
            return f"[{step}] 🧠 Composition: {comp} (Tribe {tribe})"
        elif event_type == 'war':
            attacker = event.get('attacker', '?')
            defender = event.get('defender', '?')
            outcome = event.get('outcome', '?')
            return f"[{step}] ⚔️ War: Tribe {attacker} vs {defender} → {outcome}"
        elif event_type == 'alliance':
            a = event.get('tribe_a', '?')
            b = event.get('tribe_b', '?')
            return f"[{step}] 🤝 Alliance: Tribe {a} + Tribe {b}"
        else:
            return f"[{step}] {event_type}"
    
    def _render_metrics(self, metrics: Dict) -> List[str]:
        """Render metrics panel."""
        lines = [f"\n  {'─'*50}"]
        lines.append("  Metrics:")
        
        for key, value in metrics.items():
            if isinstance(value, float):
                lines.append(f"    {key}: {value:.2f}")
            else:
                lines.append(f"    {key}: {value}")
        
        return lines
    
    def _render_tribes(self, world: Any) -> List[str]:
        """Render tribe summary."""
        lines = [f"\n  {'─'*50}"]
        lines.append("  Tribes:")
        
        for tribe_id, tribe in world.tribes.items():
            summary = tribe.summary() if hasattr(tribe, 'summary') else {}
            pop = sum(1 for a in world.agents if getattr(a, 'tribe_id', None) == tribe_id)
            symbols = summary.get('symbols', 0)
            avg_val = summary.get('avg_value', 0)
            
            color = self._get_tribe_color(tribe_id)
            marker = self._colorize(f"[{tribe_id}]", color)
            lines.append(f"    {marker} Pop: {pop:3d} | Symbols: {symbols:3d} | Avg: {avg_val:.2f}")
        
        return lines
    
    # =====================================================
    # EVENT TRACKING
    # =====================================================
    
    def record_event(self, event: Dict):
        """Record an event for display."""
        self.event_queue.append(event)
    
    def record_birth(self, agent: str, tribe: int, step: int):
        """Record a birth event."""
        self.record_event({
            'type': 'birth',
            'agent': agent,
            'tribe': tribe,
            'step': step,
        })
    
    def record_death(self, agent: str, tribe: int, step: int):
        """Record a death event."""
        self.record_event({
            'type': 'death',
            'agent': agent,
            'tribe': tribe,
            'step': step,
        })
    
    def record_symbol(self, symbol: Any, tribe: int, step: int):
        """Record a symbol creation event."""
        self.record_event({
            'type': 'symbol',
            'symbol': str(symbol)[:20],
            'tribe': tribe,
            'step': step,
        })
    
    def record_composition(self, composition: Any, tribe: int, step: int):
        """Record a symbol composition event."""
        self.record_event({
            'type': 'composition',
            'composition': str(composition)[:20],
            'tribe': tribe,
            'step': step,
        })
    
    def record_war(self, attacker: int, defender: int, outcome: str, step: int):
        """Record a war event."""
        self.record_event({
            'type': 'war',
            'attacker': attacker,
            'defender': defender,
            'outcome': outcome,
            'step': step,
        })
    
    def record_alliance(self, tribe_a: int, tribe_b: int, step: int):
        """Record an alliance event."""
        self.record_event({
            'type': 'alliance',
            'tribe_a': tribe_a,
            'tribe_b': tribe_b,
            'step': step,
        })
    
    # =====================================================
    # HISTORY TRACKING
    # =====================================================
    
    def update_history(self, metrics: Dict[str, float]):
        """Update history with new metrics."""
        for key, value in metrics.items():
            if key in self.history:
                self.history[key].append(value)
    
    # =====================================================
    # DISPLAY UTILITIES
    # =====================================================
    
    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors enabled."""
        if not self.color_enabled:
            return text
        code = self.colors.get(color, '')
        reset = self.colors['reset']
        return f"{code}{text}{reset}"
    
    def _get_tribe_color(self, tribe_id: int) -> str:
        """Get color for a tribe."""
        return self.tribe_colors[tribe_id % len(self.tribe_colors)]
    
    def clear_screen(self):
        """Clear the terminal screen."""
        if self.color_enabled:
            print('\033[2J\033[H', end='')
    
    def display(self, world: Any, metrics: Optional[Dict] = None):
        """Display the current state (clear and render)."""
        self.clear_screen()
        print(self.render(world, metrics))
    
    # =====================================================
    # EXPORT
    # =====================================================
    
    def export_frame(self, world: Any, metrics: Optional[Dict] = None, path: str = None) -> str:
        """
        Export current frame to a file.
        
        Args:
            world: World object
            metrics: Optional metrics
            path: Output path (auto-generated if None)
            
        Returns:
            Path to exported file
        """
        if path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            path = f"exports/frame_{timestamp}.txt"
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Render without colors for file
        original_color = self.color_enabled
        self.color_enabled = False
        
        content = self.render(world, metrics)
        
        self.color_enabled = original_color
        
        with open(path, 'w') as f:
            f.write(content)
        
        return path
    
    def export_report(self, world: Any, metrics: Dict, path: str = None) -> str:
        """
        Export a summary report.
        
        Args:
            world: World object
            metrics: Metrics dict
            path: Output path
            
        Returns:
            Path to exported file
        """
        if path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            path = f"exports/report_{timestamp}.txt"
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        lines = []
        lines.append("=" * 60)
        lines.append("CIVILIZATION SIMULATOR REPORT")
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append("=" * 60)
        lines.append("")
        
        # World stats
        lines.append("WORLD STATISTICS")
        lines.append("-" * 40)
        lines.append(f"Steps: {getattr(world, 'step_count', 0)}")
        lines.append(f"Size: {getattr(world, 'width', 0)}x{getattr(world, 'height', 0)}")
        lines.append(f"Agents: {len(getattr(world, 'agents', []))}")
        lines.append(f"Tribes: {len(getattr(world, 'tribes', {}))}")
        lines.append("")
        
        # Metrics
        lines.append("METRICS")
        lines.append("-" * 40)
        for key, value in metrics.items():
            if isinstance(value, float):
                lines.append(f"{key}: {value:.4f}")
            else:
                lines.append(f"{key}: {value}")
        lines.append("")
        
        # History
        lines.append("HISTORY (last 100 steps)")
        lines.append("-" * 40)
        for key, values in self.history.items():
            if values:
                avg = sum(values) / len(values)
                min_v = min(values)
                max_v = max(values)
                lines.append(f"{key}: avg={avg:.2f}, min={min_v:.2f}, max={max_v:.2f}")
        lines.append("")
        
        with open(path, 'w') as f:
            f.write('\n'.join(lines))
        
        return path
    
    # =====================================================
    # STATUS
    # =====================================================
    
    def status(self) -> Dict[str, Any]:
        """Get visualization status."""
        return {
            'color_enabled': self.color_enabled,
            'events_recorded': len(self.event_queue),
            'history_keys': list(self.history.keys()),
            'history_length': len(self.history.get('population', [])),
        }
    
    def summary(self) -> str:
        """Get human-readable summary."""
        s = self.status()
        return (
            f"👁️ Visualization Status\n"
            f"   Colors: {'enabled' if s['color_enabled'] else 'disabled'}\n"
            f"   Events Recorded: {s['events_recorded']}\n"
            f"   History Length: {s['history_length']}\n"
        )
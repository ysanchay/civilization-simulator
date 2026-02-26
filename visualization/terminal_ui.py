"""Terminal UI for civilization simulator."""

from typing import Dict, Any, Optional


class TerminalUI:
    """Simple terminal-based visualization."""
    
    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height
    
    def clear(self):
        """Clear the terminal."""
        print('\033[2J\033[H', end='')
    
    def render_world(self, world: Any) -> str:
        """Render world as ASCII art."""
        lines = []
        
        w = min(self.width, getattr(world, 'width', 20))
        h = min(self.height - 4, getattr(world, 'height', 20))
        
        lines.append('+' + '-' * w + '+')
        
        for y in range(h):
            row = ['|']
            for x in range(w):
                cell = self._render_cell(world, x, y)
                row.append(cell)
            row.append('|')
            lines.append(''.join(row))
        
        lines.append('+' + '-' * w + '+')
        
        return '\n'.join(lines)
    
    def _render_cell(self, world: Any, x: int, y: int) -> str:
        """Render a single cell."""
        # Check for agent
        if hasattr(world, 'grid'):
            try:
                agent = world.grid[y][x]
                if agent:
                    return '@'
            except IndexError:
                pass
        
        # Check for food
        if hasattr(world, 'food'):
            try:
                if world.food[y][x]:
                    return '*'
            except IndexError:
                pass
        
        # Biome
        if hasattr(world, 'biomes'):
            try:
                biome = world.biomes[y][x]
                return ['.', '"', '~'][biome % 3]
            except IndexError:
                pass
        
        return ' '
    
    def render_status(self, world: Any, step: int) -> str:
        """Render status line."""
        agents = len(getattr(world, 'agents', []))
        tribes = len(getattr(world, 'tribes', {}))
        
        return f"Step: {step:6d} | Agents: {agents:3d} | Tribes: {tribes:2d}"
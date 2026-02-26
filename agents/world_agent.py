"""
WorldAgent

IDENTITY: "I am the environment. I create the stage for civilizations."

ROLE: World generation and environmental dynamics

RESPONSIBILITIES:
- Generate and manage the grid world
- Control biomes, terrain, resources
- Handle food cycles and regeneration
- Manage epoch shifts (environmental changes)
- Place and manage artifacts
- Expand world when density threshold reached
"""

import random
from typing import Dict, List, Tuple, Optional
from enum import Enum


class BiomeType(Enum):
    PLAINS = 0
    FOREST = 1
    DESERT = 2
    MOUNTAIN = 3
    WATER = 4


class WorldAgent:
    """
    Manages the world environment for the civilization simulation.
    
    Handles world generation, resources, biomes, and environmental changes.
    """
    
    def __init__(
        self,
        width: int = 20,
        height: int = 20,
        expansion_density: float = 0.15,
        food_regen_rate: float = 0.02,
        epoch_interval: int = 500,
    ):
        self.width = width
        self.height = height
        self.expansion_density = expansion_density
        self.food_regen_rate = food_regen_rate
        self.epoch_interval = epoch_interval
        
        # Grid state
        self.grid: List[List[Optional[any]]] = None
        self.food: List[List[bool]] = None
        self.biomes: List[List[int]] = None
        self.artifacts: List[List[Optional[any]]] = None
        self.danger_zones: List[List[float]] = None
        
        # World dynamics
        self.food_multiplier = 1.0
        self.danger_multiplier = 1.0
        self.world_time = 0
        self.step_count = 0
        
        # Statistics
        self.epoch_count = 0
        self.expansion_count = 0
    
    # =====================================================
    # WORLD GENERATION
    # =====================================================
    
    def generate_world(self) -> Dict[str, any]:
        """
        Generate a new world with biomes, food, and artifacts.
        
        Returns:
            World initialization data
        """
        # Initialize grids
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.food = [[random.random() < 0.05 for _ in range(self.width)] for _ in range(self.height)]
        self.biomes = [[random.randint(0, 2) for _ in range(self.width)] for _ in range(self.height)]
        self.artifacts = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.danger_zones = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Seed artifacts
        self._seed_artifacts(count=6)
        
        # Set initial time
        self.world_time = random.randint(0, 3)
        
        return {
            'width': self.width,
            'height': self.height,
            'biomes': self.biomes,
            'food_count': sum(sum(row) for row in self.food),
            'artifacts': sum(1 for row in self.artifacts for cell in row if cell),
        }
    
    def _seed_artifacts(self, count: int = 6):
        """Place artifacts in the world."""
        from artifacts import Artifact
        
        kinds = ["counter", "cycle", "conditional"]
        placed = 0
        
        for _ in range(count * 10):  # Try up to 10x count
            if placed >= count:
                break
            
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            
            if self.artifacts[y][x] is None:
                self.artifacts[y][x] = Artifact(random.choice(kinds))
                placed += 1
    
    # =====================================================
    # WORLD STEP
    # =====================================================
    
    def step(self):
        """Advance world state by one step."""
        self.step_count += 1
        
        # Advance time
        self._advance_time()
        
        # Update artifacts
        self._update_artifacts()
        
        # Regrow food
        self._regrow_food()
        
        # Apply epoch shifts
        self._apply_epoch_shift()
        
        # Update danger zones
        self._update_danger_zones()
    
    def _advance_time(self):
        """Advance world time with stochastic elements."""
        r = random.random()
        if r < 0.85:
            self.world_time = (self.world_time + 1) % 4
        elif r < 0.95:
            self.world_time = (self.world_time + 2) % 4
        else:
            self.world_time = random.randint(0, 3)
    
    def _update_artifacts(self):
        """Update artifact states."""
        for row in self.artifacts:
            for artifact in row:
                if artifact:
                    artifact.step(self.world_time)
    
    def _regrow_food(self):
        """Regrow food across the world."""
        for y in range(self.height):
            for x in range(self.width):
                if not self.food[y][x]:
                    # Biome affects regrowth
                    biome_factor = [1.0, 1.5, 0.3, 0.5, 0.0][self.biomes[y][x]]
                    regen_chance = self.food_regen_rate * self.food_multiplier * biome_factor
                    
                    if random.random() < regen_chance:
                        self.food[y][x] = True
    
    def _apply_epoch_shift(self):
        """Apply environmental shifts at intervals."""
        if self.step_count % self.epoch_interval == 0:
            # Shift multipliers
            self.food_multiplier *= random.uniform(0.7, 1.3)
            self.danger_multiplier *= random.uniform(0.8, 1.2)
            
            # Clamp
            self.food_multiplier = max(0.3, min(self.food_multiplier, 3.0))
            self.danger_multiplier = max(0.3, min(self.danger_multiplier, 3.0))
            
            self.epoch_count += 1
            
            return {
                'type': 'epoch_shift',
                'food_multiplier': self.food_multiplier,
                'danger_multiplier': self.danger_multiplier,
            }
        return None
    
    def _update_danger_zones(self):
        """Update danger level for each cell."""
        for y in range(self.height):
            for x in range(self.width):
                base = self._calculate_base_danger(x, y)
                self.danger_zones[y][x] = base * self.danger_multiplier
    
    def _calculate_base_danger(self, x: int, y: int) -> float:
        """Calculate base danger for a cell."""
        # Edge danger
        edge = x == 0 or y == 0 or x == self.width - 1 or y == self.height - 1
        
        # Crowding danger
        crowd = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny) and self.grid[ny][nx]:
                crowd += 1
        
        base = (1.0 if edge else 0.0) + 0.3 * crowd
        return base
    
    # =====================================================
    # WORLD QUERIES
    # =====================================================
    
    def in_bounds(self, x: int, y: int) -> bool:
        """Check if coordinates are within world bounds."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def get_cell(self, x: int, y: int) -> Optional[any]:
        """Get agent at cell, if any."""
        if self.in_bounds(x, y):
            return self.grid[y][x]
        return None
    
    def set_cell(self, x: int, y: int, agent: Optional[any]):
        """Set agent at cell."""
        if self.in_bounds(x, y):
            self.grid[y][x] = agent
    
    def get_food(self, x: int, y: int) -> bool:
        """Check if food is at cell."""
        if self.in_bounds(x, y):
            return self.food[y][x]
        return False
    
    def consume_food(self, x: int, y: int) -> bool:
        """Consume food at cell, return True if successful."""
        if self.in_bounds(x, y) and self.food[y][x]:
            self.food[y][x] = False
            return True
        return False
    
    def get_danger(self, x: int, y: int) -> float:
        """Get danger level at cell."""
        if self.in_bounds(x, y):
            return self.danger_zones[y][x]
        return float('inf')
    
    def get_biome(self, x: int, y: int) -> int:
        """Get biome type at cell."""
        if self.in_bounds(x, y):
            return self.biomes[y][x]
        return -1
    
    def get_artifact(self, x: int, y: int) -> Optional[any]:
        """Get artifact at cell."""
        if self.in_bounds(x, y):
            return self.artifacts[y][x]
        return None
    
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get empty neighboring cells."""
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny) and self.grid[ny][nx] is None:
                neighbors.append((nx, ny))
        return neighbors
    
    def random_empty_cell(self) -> Tuple[int, int]:
        """Find a random empty cell."""
        for _ in range(1000):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            if self.grid[y][x] is None:
                return x, y
        raise RuntimeError("No empty cell found")
    
    # =====================================================
    # WORLD EXPANSION
    # =====================================================
    
    def expand_world(self, amount: int = 5) -> Dict[str, int]:
        """
        Expand the world by adding rows/columns.
        
        Args:
            amount: Number of cells to add in each direction
            
        Returns:
            Expansion statistics
        """
        old_width = self.width
        old_height = self.height
        
        # Expand dimensions
        self.width += amount * 2
        self.height += amount * 2
        
        # Create new grids
        new_grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        new_food = [[False for _ in range(self.width)] for _ in range(self.height)]
        new_biomes = [[random.randint(0, 2) for _ in range(self.width)] for _ in range(self.height)]
        new_artifacts = [[None for _ in range(self.width)] for _ in range(self.height)]
        new_danger = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Copy old data to center
        for y in range(old_height):
            for x in range(old_width):
                new_grid[y + amount][x + amount] = self.grid[y][x]
                new_food[y + amount][x + amount] = self.food[y][x]
                new_biomes[y + amount][x + amount] = self.biomes[y][x]
                new_artifacts[y + amount][x + amount] = self.artifacts[y][x]
                new_danger[y + amount][x + amount] = self.danger_zones[y][x]
        
        # Replace grids
        self.grid = new_grid
        self.food = new_food
        self.biomes = new_biomes
        self.artifacts = new_artifacts
        self.danger_zones = new_danger
        
        self.expansion_count += 1
        
        return {
            'old_size': (old_width, old_height),
            'new_size': (self.width, self.height),
            'expansion_count': self.expansion_count,
        }
    
    # =====================================================
    # STATUS
    # =====================================================
    
    def status(self) -> Dict[str, any]:
        """Get world status."""
        food_count = sum(sum(row) for row in self.food)
        artifact_count = sum(1 for row in self.artifacts for cell in row if cell)
        
        return {
            'size': (self.width, self.height),
            'step': self.step_count,
            'time_phase': self.world_time,
            'food_count': food_count,
            'artifact_count': artifact_count,
            'food_multiplier': self.food_multiplier,
            'danger_multiplier': self.danger_multiplier,
            'epoch_count': self.epoch_count,
            'expansion_count': self.expansion_count,
        }
    
    def summary(self) -> str:
        """Get human-readable summary."""
        s = self.status()
        return (
            f"🌍 World Status\n"
            f"   Size: {s['size'][0]}x{s['size'][1]}\n"
            f"   Step: {s['step']}\n"
            f"   Time Phase: {s['time_phase']}\n"
            f"   Food: {s['food_count']}\n"
            f"   Artifacts: {s['artifact_count']}\n"
            f"   Epochs: {s['epoch_count']}\n"
        )
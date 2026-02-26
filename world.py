import random
import pickle
from pathlib import Path
from culture import TribeCulture
from artifacts import Artifact


class World:
    # 🌍 WORLD EXPANSION CONSTANTS
    MAX_DENSITY = 0.25  # Expand when population density exceeds this
    EXPANSION_SIZE = 5  # Cells to add in each direction
    
    def __init__(self, width=20, height=20, expansion_density=0.15, auto_expand=True):
        self.width = width
        self.height = height
        self.expansion_density = expansion_density
        self.auto_expand = auto_expand

        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.food = [[random.random() < 0.05 for _ in range(width)] for _ in range(height)]

        # 🌍 BIOMES
        self.biomes = [[random.randint(0, 2) for _ in range(width)] for _ in range(height)]

        # 🧱 ARTIFACT GRID
        self.artifacts = [[None for _ in range(width)] for _ in range(height)]

        self.agents = []
        self.births_last_step = 0
        self.deaths_last_step = 0
        self.step_count = 0

        self.tribes = {}
        self.next_tribe_id = 0

        self.food_multiplier = 1.0
        self.danger_multiplier = 1.0

        # 🌍 WORLD CLOCK
        self.world_time = random.randint(0, 3)
        
        # 📊 EXPANSION TRACKING
        self.expansion_count = 0
        self.last_expansion_step = 0

        self._seed_artifacts()

    # -------------------------------------------------
    def _seed_artifacts(self):
        kinds = ["counter", "cycle", "conditional"]
        for _ in range(6):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            self.artifacts[y][x] = Artifact(random.choice(kinds))

    # -------------------------------------------------
    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def random_empty(self):
        for _ in range(1000):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            if self.grid[y][x] is None:
                return x, y
        raise RuntimeError("No empty cell")

    def neighbors(self, x, y):
        dirs = [(-1,0),(1,0),(0,-1),(0,1)]
        result = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny) and self.grid[ny][nx] is None:
                result.append((nx, ny))
        return result

    # -------------------------------------------------
    def add_agent(self, agent):
        if agent.tribe_id is None:
            agent.tribe_id = self.next_tribe_id
            self.tribes[agent.tribe_id] = TribeCulture(agent.tribe_id)
            self.next_tribe_id += 1

        x, y = self.random_empty()
        agent.x = x
        agent.y = y
        self.grid[y][x] = agent
        self.agents.append(agent)

    def move_agent(self, agent, nx, ny):
        self.grid[agent.y][agent.x] = None
        agent.x = nx
        agent.y = ny
        self.grid[ny][nx] = agent

    def remove_agent(self, agent):
        self.grid[agent.y][agent.x] = None
        if agent in self.agents:
            self.agents.remove(agent)

    # -------------------------------------------------
    def danger_level(self, x, y, tribe_id=None):
        edge = x == 0 or y == 0 or x == self.width - 1 or y == self.height - 1
        crowd = sum(
            1 for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]
            if self.in_bounds(x+dx, y+dy) and self.grid[y+dy][x+dx]
        )

        base = (1.0 if edge else 0.0) + 0.3 * crowd

        if tribe_id is not None:
            tribe = self.tribes.get(tribe_id)
            if tribe:
                biome = self.biomes[y][x]
                if biome != tribe.home_biome:
                    base *= 1.6

        return base * self.danger_multiplier

    def consume_food(self, x, y):
        if self.food[y][x]:
            self.food[y][x] = False
            return True
        return False

    def regrow_food(self):
        for y in range(self.height):
            for x in range(self.width):
                if not self.food[y][x]:
                    if random.random() < 0.02 * self.food_multiplier:
                        self.food[y][x] = True

    # -------------------------------------------------
    # 🌍 WORLD EXPANSION
    # -------------------------------------------------
    def get_density(self):
        """Calculate current population density."""
        area = self.width * self.height
        return len(self.agents) / area if area > 0 else 0
    
    def expand_world(self, amount=None):
        """
        Expand the world by adding cells in all directions.
        
        Args:
            amount: Number of cells to add (default: EXPANSION_SIZE)
            
        Returns:
            True if expanded, False if skipped
        """
        if amount is None:
            amount = self.EXPANSION_SIZE
        
        old_width = self.width
        old_height = self.height
        
        # New dimensions
        self.width += amount * 2
        self.height += amount * 2
        
        print(f"\n🌍 WORLD EXPANSION @ step {self.step_count}")
        print(f"   Size: {old_width}x{old_height} → {self.width}x{self.height}")
        print(f"   Population: {len(self.agents)} | Density was: {len(self.agents)/(old_width*old_height):.2%}")
        
        # Create new grids
        new_grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        new_food = [[False for _ in range(self.width)] for _ in range(self.height)]
        new_biomes = [[random.randint(0, 2) for _ in range(self.width)] for _ in range(self.height)]
        new_artifacts = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        # Copy old data to center
        for y in range(old_height):
            for x in range(old_width):
                new_grid[y + amount][x + amount] = self.grid[y][x]
                new_food[y + amount][x + amount] = self.food[y][x]
                new_biomes[y + amount][x + amount] = self.biomes[y][x]
                new_artifacts[y + amount][x + amount] = self.artifacts[y][x]
        
        # Replace grids
        self.grid = new_grid
        self.food = new_food
        self.biomes = new_biomes
        self.artifacts = new_artifacts
        
        # Update agent positions
        for agent in self.agents:
            agent.x += amount
            agent.y += amount
        
        # Add new artifacts in expanded areas
        self._seed_expansion_artifacts(amount)
        
        # Track expansion
        self.expansion_count += 1
        self.last_expansion_step = self.step_count
        
        return True
    
    def _seed_expansion_artifacts(self, amount):
        """Add artifacts in newly expanded areas."""
        kinds = ["counter", "cycle", "conditional"]
        
        # Add artifacts in the new border areas
        for _ in range(amount * 2):
            # Choose a random edge area
            if random.random() < 0.5:
                # Top or bottom edge
                y = random.choice(range(amount)) if random.random() < 0.5 else random.choice(range(self.height - amount, self.height))
                x = random.randrange(self.width)
            else:
                # Left or right edge
                x = random.choice(range(amount)) if random.random() < 0.5 else random.choice(range(self.width - amount, self.width))
                y = random.randrange(self.height)
            
            if self.grid[y][x] is None and self.artifacts[y][x] is None:
                self.artifacts[y][x] = Artifact(random.choice(kinds))
    
    def check_expansion(self):
        """Check if world should expand and do so if needed."""
        if not self.auto_expand:
            return False
        
        density = self.get_density()
        
        if density >= self.MAX_DENSITY:
            print(f"\n⚠️ HIGH DENSITY ALERT: {density:.1%} >= {self.MAX_DENSITY:.1%}")
            return self.expand_world()
        
        return False

    # -------------------------------------------------
    def apply_epoch_shift(self):
        if self.step_count % 500 == 0:
            self.food_multiplier *= random.uniform(0.7, 1.3)
            self.danger_multiplier *= random.uniform(0.8, 1.2)

            self.food_multiplier = max(0.3, min(self.food_multiplier, 3.0))
            self.danger_multiplier = max(0.3, min(self.danger_multiplier, 3.0))

            print(
                f"🌍 WORLD SHIFT @ {self.step_count} | "
                f"food×{self.food_multiplier:.2f} "
                f"danger×{self.danger_multiplier:.2f}"
            )

    # -------------------------------------------------
    def spawn_child(self, parent):
        spots = self.neighbors(parent.x, parent.y)
        if not spots:
            return

        x, y = random.choice(spots)
        child = parent.clone_child()
        child.x = x
        child.y = y

        self.grid[y][x] = child
        self.agents.append(child)
        self.births_last_step += 1

        tribe = self.tribes.get(child.tribe_id)
        if tribe:
            tribe.restore_memory()

    # -------------------------------------------------
    # 🌍 WORLD STEP (WITH FORGETTING)
    # -------------------------------------------------
    def step(self):
        self.step_count += 1
        self.births_last_step = 0
        self.deaths_last_step = 0

        r = random.random()
        if r < 0.85:
            self.world_time = (self.world_time + 1) % 4
        elif r < 0.95:
            self.world_time = (self.world_time + 2) % 4
        else:
            self.world_time = random.randint(0, 3)

        for row in self.artifacts:
            for art in row:
                if art:
                    art.step(self.world_time)

        # snapshot memory for near-extinct tribes
        tribe_counts = {}
        for agent in self.agents:
            tribe_counts[agent.tribe_id] = tribe_counts.get(agent.tribe_id, 0) + 1

        for tid, tribe in self.tribes.items():
            if tribe_counts.get(tid, 0) == 1:
                tribe.snapshot_memory()

        self.apply_epoch_shift()

        # 🔥 APPLY CULTURAL FORGETTING
        for tid, tribe in self.tribes.items():
            pop = tribe_counts.get(tid, 0)
            tribe.decay_symbols(pop)

        for agent in self.agents[:]:
            agent.step()

        self.regrow_food()
        
        # 🌍 CHECK FOR WORLD EXPANSION
        self.check_expansion()
    
    # -------------------------------------------------
    # 🧠 BRAIN PERSISTENCE
    # -------------------------------------------------
    def save_brains(self, path="brains"):
        """Save all tribe brains to disk for knowledge persistence."""
        import pickle
        from pathlib import Path
        
        brain_path = Path(path)
        brain_path.mkdir(exist_ok=True)
        
        saved = 0
        for tid, tribe in self.tribes.items():
            try:
                data = {
                    'tribe_id': tid,
                    'symbols': {str(k): {'value': v.value, 'count': v.count} 
                               for k, v in tribe.symbols.items()},
                    'transitions': {str(k): dict(v) for k, v in tribe.transitions.items()},
                    'composed_symbols': {str(k): v for k, v in tribe.composed_symbols.items()},
                    'home_biome': tribe.home_biome,
                    'preference_bias': tribe.preference_bias,
                }
                
                with open(brain_path / f"tribe_{tid}.pkl", 'wb') as f:
                    pickle.dump(data, f)
                saved += 1
            except Exception as e:
                print(f"   ⚠️ Could not save tribe {tid}: {e}")
        
        print(f"💾 Saved {saved} tribe brains to {brain_path}")
        return saved
    
    def load_brains(self, path="brains"):
        """Load tribe brains from disk for knowledge persistence."""
        import pickle
        from pathlib import Path
        
        brain_path = Path(path)
        
        if not brain_path.exists():
            print(f"   📂 No brain directory found at {brain_path}")
            return 0
        
        loaded = 0
        for brain_file in brain_path.glob("tribe_*.pkl"):
            try:
                with open(brain_file, 'rb') as f:
                    data = pickle.load(f)
                
                tid = data['tribe_id']
                
                # Create tribe if it doesn't exist
                if tid not in self.tribes:
                    self.tribes[tid] = TribeCulture(tid)
                    self.next_tribe_id = max(self.next_tribe_id, tid + 1)
                
                tribe = self.tribes[tid]
                
                # Load preference bias
                if 'preference_bias' in data:
                    tribe.preference_bias = data['preference_bias']
                if 'home_biome' in data:
                    tribe.home_biome = data['home_biome']
                
                loaded += 1
                
            except Exception as e:
                print(f"   ⚠️ Could not load {brain_file}: {e}")
        
        print(f"📂 Loaded {loaded} tribe brains from {brain_path}")
        return loaded

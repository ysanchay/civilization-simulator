import random


class Agent:
    def __init__(self, name, world, energy=50, generation=0, tribe_id=None):
        self.name = name
        self.world = world
        self.energy = energy
        self.generation = generation
        self.tribe_id = tribe_id

        self.x = None
        self.y = None

        # Physiology
        self.metabolism = 0.8
        self.reproduction_threshold = 60
        self.reproduction_cooldown = 0

        # Cognition
        self.last_symbol = None
        self.planning_horizon = 2

    # =================================================
    # Perception
    # =================================================
    def observe_local(self):
        food = 1 if self.world.food[self.y][self.x] else 0
        danger = int(
            self.world.danger_level(self.x, self.y, self.tribe_id) > 1.0
        )

        artifact = self.world.artifacts[self.y][self.x]
        artifact_obs = artifact.observe() if artifact else None

        time_phase = self.world.world_time

        return (food, danger, artifact_obs, time_phase)

    # =================================================
    # Dominance pressure
    # =================================================
    def dominance_pressure(self):
        tribe_pop = sum(1 for a in self.world.agents if a.tribe_id == self.tribe_id)
        total_pop = max(1, len(self.world.agents))
        return 0.6 * (tribe_pop / total_pop)

    # =================================================
    # Life step
    # =================================================
    def step(self):
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1

        # Baseline costs
        self.energy -= self.metabolism
        self.energy -= self.dominance_pressure()

        tribe = self.world.tribes[self.tribe_id]

        # Observe
        pattern = self.observe_local()
        tribe.observe_pattern(pattern, reward=0.0, population=len(self.world.agents))

        # Language transition + temporal pressure
        if self.last_symbol is not None:
            tribe.record_transition(
                self.last_symbol, pattern, population=len(self.world.agents)
            )

            expected = tribe.predict_next(self.last_symbol)
            if expected is not None and expected[-1] != pattern[-1]:
                self.energy -= 0.2

        self.last_symbol = pattern

        # Move
        self.move()

        # Eat
        if self.world.consume_food(self.x, self.y):
            self.energy += 15
            tribe.record_food(self.x, self.y)
            tribe.observe_pattern(pattern, reward=1.0, population=len(self.world.agents))

        # Communicate (includes inter-tribe transfer)
        self.communicate()

        # Reproduction (dominance-aware)
        effective_threshold = self.reproduction_threshold * (1 + self.dominance_pressure())

        if self.energy >= effective_threshold and self.reproduction_cooldown == 0:
            if self.energy * 0.5 - self.metabolism * 3 > 10:
                self.energy *= 0.5
                self.world.spawn_child(self)
                self.reproduction_cooldown = 5

        # Death
        if self.energy <= 0:
            tribe.record_danger(self.x, self.y)
            self.world.remove_agent(self)
            self.world.deaths_last_step += 1

    # =================================================
    # Movement
    # =================================================
    def move(self):
        candidates = self.world.neighbors(self.x, self.y)
        if not candidates:
            return

        tribe = self.world.tribes[self.tribe_id]

        def score(cell):
            x, y = cell
            expected = self.simulate_move(x, y)
            danger_memory = tribe.danger_memory.get((x, y), 0.0)

            pattern = (
                1 if self.world.food[y][x] else 0,
                int(self.world.danger_level(x, y, self.tribe_id) > 1.0),
                None,
                self.world.world_time
            )

            symbol_bias = tribe.pattern_value(pattern, population=len(self.world.agents))

            surprise = 0.0
            if self.last_symbol is not None:
                expected_sym = tribe.predict_next(self.last_symbol)
                if expected_sym and expected_sym != pattern:
                    surprise = tribe.surprise(self.last_symbol, pattern)

            self.energy -= 0.15 * surprise
            return -expected + danger_memory + surprise - symbol_bias

        nx, ny = min(candidates, key=score)
        self.world.move_agent(self, nx, ny)

    # =================================================
    # Communication & Cultural Transfer
    # =================================================
    def communicate(self):
        if self.last_symbol is None:
            return

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = self.x + dx, self.y + dy
            if not self.world.in_bounds(nx, ny):
                continue

            other = self.world.grid[ny][nx]
            if other:
                other.receive(self.last_symbol, self.tribe_id)

    def receive(self, symbol, sender_tribe):
        tribe = self.world.tribes[self.tribe_id]
        sender = self.world.tribes[sender_tribe]

        success = False

        # intra-tribe prediction success
        if sender_tribe == self.tribe_id and self.last_symbol is not None:
            success = tribe.predict_next(symbol) == self.last_symbol

        # 🔥 INTER-TRIBE SYMBOL TRANSFER
        if sender_tribe != self.tribe_id and symbol in sender.symbols:
            sender_strength = sender.symbols[symbol].value
            local_obj = tribe.symbols.get(symbol)

            adopt_prob = min(0.9, max(0.1, sender_strength / 5.0))

            if local_obj is None or sender_strength > local_obj.value:
                if random.random() < adopt_prob:
                    tribe.adopt_symbol(symbol, sender)

        tribe.interpret(symbol, success, population=len(self.world.agents))
        self.energy += 0.5 if success else -0.3

    # =================================================
    # Planning
    # =================================================
    def simulate_move(self, x, y, depth=1):
        energy = self.energy
        energy -= self.metabolism
        energy -= self.dominance_pressure()

        danger = self.world.danger_level(x, y, self.tribe_id)
        energy -= danger * 2.0

        if self.world.food[y][x]:
            energy += 15

        if depth < self.planning_horizon:
            neighbors = self.world.neighbors(x, y)
            if neighbors:
                best = -1e9
                for nx, ny in neighbors:
                    future = self.simulate_move(nx, ny, depth + 1)
                    crowd_penalty = 1.0 + 0.3 * len(neighbors)
                    best = max(best, future / crowd_penalty)
                energy = 0.7 * energy + 0.3 * best

        return energy

    # =================================================
    # Reproduction (RESTORED)
    # =================================================
    def clone_child(self):
        child = Agent(
            name=self.name,
            world=self.world,
            energy=40,
            generation=self.generation + 1,
            tribe_id=self.tribe_id
        )

        # mutation
        if random.random() < 0.2:
            child.metabolism = max(0.5, self.metabolism + random.uniform(-0.1, 0.1))
        else:
            child.metabolism = self.metabolism

        if random.random() < 0.2:
            child.reproduction_threshold = max(
                40, self.reproduction_threshold + random.randint(-5, 5)
            )
        else:
            child.reproduction_threshold = self.reproduction_threshold

        return child

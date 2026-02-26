import collections
from collections import defaultdict


def nested_int_dict():
    return defaultdict(int)


class Memory:
    def __init__(self, window=3, max_symbols=300):
        self.window = window
        self.buffer = collections.deque(maxlen=window)

        # symbol system
        self.symbols = {}
        self.reverse = {}
        self.symbol_counter = 0

        # reward grounding
        self.rewards = {}

        # ⚠️ danger grounding
        self.dangers = {}   # symbol -> danger score

        # transitions
        self.transitions = defaultdict(nested_int_dict)

        # 🔤 language
        self.chain_counts = defaultdict(int)
        self.chains = {}

        self.max_symbols = max_symbols

    # -----------------------------
    # Perception abstraction
    # -----------------------------
    def _hash_observation(self, obs):
        food = obs.count(2)
        danger = obs.count(3)
        walls = obs.count(1)
        return (min(food, 2), min(danger, 2), min(walls, 3))

    def observe(self, observation):
        hashed = self._hash_observation(observation)
        self.buffer.append(hashed)

        if len(self.buffer) < self.window:
            return None

        pattern = tuple(self.buffer)

        if pattern not in self.symbols:
            if len(self.symbols) >= self.max_symbols:
                return None

            symbol = f"S{self.symbol_counter}"
            self.symbol_counter += 1

            self.symbols[pattern] = symbol
            self.reverse[symbol] = pattern
            self.rewards[symbol] = 0.0
            self.dangers[symbol] = 0.0

            print(f"🧠 New symbol {symbol}")

        return self.symbols[pattern]

    # -----------------------------
    # Learning
    # -----------------------------
    def learn(self, symbol, reward, lr):
        if symbol is None:
            return

        # reward learning
        old = self.rewards.get(symbol, 0.0)
        self.rewards[symbol] = old * (1 - lr) + reward * lr

        if reward > 0:
            self.rewards[symbol] += reward * 0.2

        # ⚠️ danger learning (negative reward)
        if reward < 0:
            d = self.dangers.get(symbol, 0.0)
            self.dangers[symbol] = d * 0.9 + abs(reward) * 0.3

    # -----------------------------
    # Transitions
    # -----------------------------
    def record_transition(self, prev_symbol, action, new_symbol):
        if prev_symbol and new_symbol:
            self.transitions[(prev_symbol, action)][new_symbol] += 1
            self.chain_counts[(prev_symbol, new_symbol)] += 1
            self._maybe_create_chain(prev_symbol, new_symbol)

    def predict_next(self, symbol, action):
        options = self.transitions.get((symbol, action))
        if not options:
            return None
        return max(options, key=options.get)

    # -----------------------------
    # 🔤 Language emergence
    # -----------------------------
    def _maybe_create_chain(self, s1, s2):
        key = (s1, s2)

        if key in self.chains:
            return

        if self.chain_counts[key] >= 6 and len(self.symbols) < self.max_symbols:
            new_symbol = f"S{self.symbol_counter}"
            self.symbol_counter += 1

            self.chains[key] = new_symbol
            self.rewards[new_symbol] = (
                self.rewards.get(s1, 0.0) + self.rewards.get(s2, 0.0)
            ) / 2
            self.dangers[new_symbol] = (
                self.dangers.get(s1, 0.0) + self.dangers.get(s2, 0.0)
            ) / 2

            print(f"🔤 Language emerged: {s1}→{s2} = {new_symbol}")

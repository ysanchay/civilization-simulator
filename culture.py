import random
from collections import defaultdict
from symbols import Symbol


class TribeCulture:
    def __init__(self, tribe_id):
        self.tribe_id = tribe_id

        # 🧬 Home biome
        self.home_biome = random.randint(0, 2)

        # Spatial memory
        self.food_memory = defaultdict(float)
        self.danger_memory = defaultdict(float)

        # ===============================
        # SYMBOL SYSTEM
        # ===============================
        self.symbols = {}                 # pattern -> Symbol
        self.symbol_usage = defaultdict(int)

        # 🔥 SYMBOL ROLES (INTENT LAYER)
        # predictive: helps predict next state
        # causal: linked to reward/danger
        # goal: derived (not directly trained)
        self.symbol_roles = defaultdict(lambda: {
            "predictive": 0.0,
            "causal": 0.0,
            "goal": 0.0
        })

        # Language transitions
        self.transitions = defaultdict(lambda: defaultdict(int))
        self.total_transitions = defaultdict(int)

        # Composed symbols (depth = 2)
        self.composed_symbols = {}

        # Meta symbols (depth = 3)
        self.co_occurrence = defaultdict(int)
        self.meta_symbols = {}

        # ===============================
        # 🧠 CULTURAL MEMORY VAULT
        # ===============================
        self.memory_vault = {
            "symbols": {},
            "transitions": defaultdict(dict),
            "meta": {},
            "roles": {}
        }

        # Cultural bias
        self.preference_bias = random.uniform(0.9, 1.1)

    # =================================================
    # CULTURAL LOAD (MEMORY PRESSURE)
    # =================================================
    def cultural_load(self, population):
        memory_cost = 0.01 * len(self.symbols)
        pop_cost = 0.02 * max(0, population - 25)
        return 1.0 + memory_cost + pop_cost

    # =================================================
    # SPATIAL MEMORY
    # =================================================
    def record_food(self, x, y):
        self.food_memory[(x, y)] = min(5.0, self.food_memory[(x, y)] + 1.0)

    def record_danger(self, x, y):
        self.danger_memory[(x, y)] = min(8.0, self.danger_memory[(x, y)] + 1.5)

    # =================================================
    # SYMBOL GROUNDING + CAUSAL ROLE
    # =================================================
    def observe_pattern(self, pattern, reward, population=1):
        if pattern not in self.symbols:
            self.symbols[pattern] = Symbol(pattern)
            print(f"🔤 Tribe {self.tribe_id} created symbol {pattern}")

        load = self.cultural_load(population)
        noise = random.uniform(-0.03, 0.03) * load
        adjusted_reward = (reward + noise) * self.preference_bias
        self.symbols[pattern].reinforce(adjusted_reward)

        # 🔥 CAUSAL ROLE UPDATE
        if reward > 0:
            self.symbol_roles[pattern]["causal"] += 0.1
        elif reward < 0:
            self.symbol_roles[pattern]["causal"] -= 0.05

    def pattern_value(self, pattern, population=1):
        if pattern not in self.symbols:
            return 0.0
        return self.symbols[pattern].value / self.cultural_load(population)

    # =================================================
    # LANGUAGE LEARNING + PREDICTIVE ROLE
    # =================================================
    def record_transition(self, s1, s2, population=1):
        if s1 is None or s2 is None:
            return

        load = self.cultural_load(population)

        if random.random() < (1.0 / load):
            self.transitions[s1][s2] += 1
            self.total_transitions[s1] += 1

            # 🔥 PREDICTIVE ROLE UPDATE
            self.symbol_roles[s1]["predictive"] += 0.05

            self._maybe_compose(s1, s2)
            self._track_co_occurrence(s1, s2)

    def predict_next(self, s1):
        options = self.transitions.get(s1)
        if not options:
            return None
        return max(options, key=options.get)

    def surprise(self, s1, s2, population=1):
        if s1 not in self.transitions:
            return 1.0
        total = self.total_transitions[s1]
        count = self.transitions[s1].get(s2, 0)
        if count == 0:
            return 1.0
        return (1.0 - count / total) * self.cultural_load(population)

    # =================================================
    # COMMUNICATION UPDATE
    # =================================================
    def interpret(self, symbol, success, population=1):
        if symbol not in self.symbols:
            return

        delta = 0.05 if success else -0.05
        self.symbols[symbol].value += delta / self.cultural_load(population)
        self.symbol_usage[symbol] += 1

    # =================================================
    # SYMBOL COMPOSITION (DEPTH = 2)
    # =================================================
    def _maybe_compose(self, s1, s2):
        key = (s1, s2)
        if key in self.composed_symbols:
            return

        if self.transitions[s1][s2] >= 8:
            new_symbol = f"C{len(self.composed_symbols)}"
            self.composed_symbols[key] = new_symbol
            self.symbols[new_symbol] = Symbol(key)
            print(f"🧠 LANGUAGE EMERGED: {s1} → {s2} = {new_symbol}")

    # =================================================
    # META SYMBOLS (DEPTH = 3)
    # =================================================
    def _track_co_occurrence(self, s1, s2):
        if s1 == s2:
            return

        key = tuple(sorted((s1, s2), key=lambda x: repr(x)))
        self.co_occurrence[key] += 1

        if self.co_occurrence[key] >= 10:
            keyset = frozenset(key)
            if keyset not in self.meta_symbols:
                self.meta_symbols[keyset] = Symbol(keyset)
                print(f"🧠 META-SYMBOL FORMED: {keyset}")

    # =================================================
    # 🔥 INTER-TRIBE SYMBOL ADOPTION
    # =================================================
    def adopt_symbol(self, symbol, donor_tribe):
        if symbol in self.symbols:
            return
        self.symbols[symbol] = donor_tribe.symbols[symbol]
        self.symbol_usage[symbol] = 1

    # =================================================
    # 🔥 META DOMINANCE (META REPLACES BASE)
    # =================================================
    def dominance_pass(self):
        for meta_key in self.meta_symbols:
            for base in meta_key:
                if base in self.symbols:
                    self.symbols[base].value -= 0.05

    # =================================================
    # 🔥 META COMPETITION (CANONICALIZATION)
    # =================================================
    def meta_competition(self):
        metas = list(self.meta_symbols.items())

        for i in range(len(metas)):
            k1, m1 = metas[i]
            for j in range(i + 1, len(metas)):
                k2, m2 = metas[j]
                if k1.intersection(k2):
                    if m1.value >= m2.value:
                        self.meta_symbols.pop(k2, None)
                    else:
                        self.meta_symbols.pop(k1, None)

    # =================================================
    # 🧠 FORGETTING / DECAY
    # =================================================
    def decay_symbols(self, population):
        load = self.cultural_load(population)

        self.dominance_pass()
        self.meta_competition()

        for sym, obj in list(self.symbols.items()):
            usage = self.symbol_usage.get(sym, 0)

            if usage < 3:
                obj.value -= 0.01 * load

            if (
                obj.value < -1.5
                and sym not in self.memory_vault["symbols"]
                and sym not in self.meta_symbols
            ):
                self.symbols.pop(sym, None)
                self.symbol_roles.pop(sym, None)
                self.symbol_usage.pop(sym, None)
                self.transitions.pop(sym, None)

    # =================================================
    # 🔥 GOAL SYMBOLS (INTENT EXTRACTION)
    # =================================================
    def goal_symbols(self):
        return [
            s for s, roles in self.symbol_roles.items()
            if roles["causal"] > 1.0
        ]

    # =================================================
    # 🧠 CULTURAL MEMORY (COMPRESSION + ROLES)
    # =================================================
    def snapshot_memory(self):
        meta = dict(self.meta_symbols)

        ranked = sorted(
            self.symbols.items(),
            key=lambda x: x[1].value,
            reverse=True
        )

        compressed = dict(ranked[:15])

        self.memory_vault["symbols"] = {**compressed, **meta}
        self.memory_vault["meta"] = meta
        self.memory_vault["roles"] = dict(self.symbol_roles)

        for s1, targets in self.transitions.items():
            best = max(targets.items(), key=lambda x: x[1], default=None)
            if best:
                self.memory_vault["transitions"][s1] = {best[0]: best[1]}

    def restore_memory(self):
        for sym, obj in self.memory_vault["symbols"].items():
            if sym not in self.symbols:
                self.symbols[sym] = obj

        for s1, targets in self.memory_vault["transitions"].items():
            for s2, count in targets.items():
                self.transitions[s1][s2] += count

        for k, v in self.memory_vault["meta"].items():
            self.meta_symbols[k] = v

        for k, v in self.memory_vault["roles"].items():
            self.symbol_roles[k] = v

    # =================================================
    # 📊 SUMMARY
    # =================================================
    def summary(self):
        if self.symbols:
            avg_value = round(
                sum(s.value for s in self.symbols.values()) / len(self.symbols), 2
            )
        else:
            avg_value = 0.0

        return {
            "symbols": len(self.symbols),
            "goals": len(self.goal_symbols()),
            "avg_value": avg_value,
            "home_biome": self.home_biome,
        }

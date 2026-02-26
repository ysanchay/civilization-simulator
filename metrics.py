import statistics
from collections import Counter, defaultdict


# =====================================================
# 🌍 WORLD / PHYSICAL METRICS (UNCHANGED)
# =====================================================
class WorldMetrics:
    def __init__(self):
        self.births = 0
        self.deaths = 0

    def record_birth(self):
        self.births += 1

    def record_death(self):
        self.deaths += 1

    def snapshot(self, agents):
        if not agents:
            return {
                "population": 0,
                "mean_energy": 0,
                "energy_variance": 0,
                "gen_diversity": 0,
            }

        energies = [a.energy for a in agents]
        gens = [a.generation for a in agents]

        return {
            "population": len(agents),
            "mean_energy": round(statistics.mean(energies), 2),
            "energy_variance": round(statistics.pvariance(energies), 2),
            "gen_diversity": len(set(gens)),
        }

    def reset_cycle(self):
        self.births = 0
        self.deaths = 0


# =====================================================
# 🧠 KNOWLEDGE / INTELLIGENCE METRICS (FINAL)
# =====================================================
class KnowledgeMetrics:
    """
    Measures cognition WITHOUT affecting behavior.
    """

    def __init__(self):
        # tribe_id -> {(t1, t2): count}
        self.time_transitions = defaultdict(lambda: defaultdict(int))
        self.time_totals = defaultdict(int)

    # -------------------------------------------------
    # ⏳ Record PURE time transitions (correct)
    # -------------------------------------------------
    def record_time_transition(self, tribe_id, prev_pattern, curr_pattern):
        if prev_pattern is None or curr_pattern is None:
            return

        try:
            t1 = prev_pattern[-1]
            t2 = curr_pattern[-1]
        except Exception:
            return

        self.time_transitions[tribe_id][(t1, t2)] += 1
        self.time_totals[tribe_id] += 1

    # -------------------------------------------------
    # ⏳ Temporal accuracy (true time understanding)
    # -------------------------------------------------
    def temporal_accuracy(self, tribe_id, cycle=4):
        transitions = self.time_transitions[tribe_id]
        total = self.time_totals[tribe_id]

        if total == 0:
            return 0.0

        correct = sum(
            count for (t1, t2), count in transitions.items()
            if (t1 + 1) % cycle == t2
        )

        return round(correct / total, 2)

    # -------------------------------------------------
    # 🧱 Artifact understanding
    # -------------------------------------------------
    def artifact_coverage(self, tribe):
        covered = set()
        for pattern in tribe.symbols:
            if isinstance(pattern, tuple) and len(pattern) >= 3:
                artifact = pattern[2]
                if artifact and isinstance(artifact, tuple):
                    covered.add(artifact[0])
        return sorted(covered)

    # -------------------------------------------------
    # 🧬 Abstraction depth
    # -------------------------------------------------
    def abstraction_depth(self, tribe):
        """
        1 = raw symbols
        2 = composed symbols
        3 = meta-symbols
        """
        depth = 1
        if tribe.composed_symbols:
            depth = 2
        if tribe.meta_symbols:
            depth = 3
        return depth

    # -------------------------------------------------
    # 📊 Tribe-level report
    # -------------------------------------------------
    def tribe_report(self, tribe_id, tribe):
        total_symbols = max(1, len(tribe.symbols))
        meta_count = len(tribe.meta_symbols)

        return {
            "symbols": len(tribe.symbols),
            "meta_ratio": round(meta_count / total_symbols, 2),
            "temporal_accuracy": self.temporal_accuracy(tribe_id),
            "artifact_coverage": self.artifact_coverage(tribe),
            "abstraction_depth": self.abstraction_depth(tribe),
        }

import time
import statistics
from collections import Counter

from world import World
from agent import Agent
from metrics import WorldMetrics, KnowledgeMetrics


def main():
    # ----------------------------
    # Initialize world & metrics
    # ----------------------------
    world = World(width=20, height=20)

    world_metrics = WorldMetrics()
    knowledge_metrics = KnowledgeMetrics()

    # ----------------------------
    # Seed initial agents
    # ----------------------------
    for i in range(5):
        agent = Agent(name=f"A{i}", world=world)
        world.add_agent(agent)

    step = 0

    # 🔑 store previous symbols per agent (FIX)
    prev_symbols = {}

    # ----------------------------
    # Main simulation loop
    # ----------------------------
    while True:
        step += 1

        # ------------------------------------
        # CAPTURE symbols BEFORE world step
        # ------------------------------------
        prev_symbols.clear()
        for agent in world.agents:
            prev_symbols[agent] = agent.last_symbol

        # ------------------------------------
        # Advance world
        # ------------------------------------
        world.step()

        # ------------------------------------
        # ⏳ Knowledge metrics (CORRECT SAMPLING)
        # ------------------------------------
        for agent in world.agents:
            tribe_id = agent.tribe_id
            prev_pattern = prev_symbols.get(agent)
            curr_pattern = agent.last_symbol

            knowledge_metrics.record_time_transition(
                tribe_id, prev_pattern, curr_pattern
            )

        # ------------------------------------
        # Standard logging
        # ------------------------------------
        if step % 10 == 0:
            pop = len(world.agents)
            density = pop / (world.width * world.height)

            if pop > 0:
                energies = [a.energy for a in world.agents]
                gens = [a.generation for a in world.agents]
                mean_energy = round(statistics.mean(energies), 1)
                var_energy = round(statistics.pvariance(energies), 1)
                max_gen = max(gens)
            else:
                mean_energy = var_energy = max_gen = 0

            print(
                f"📊 STEP {step} | agents={pop} | density={density:.2f} | "
                f"μE={mean_energy} | σ²E={var_energy} | max_gen={max_gen}"
            )

            tribe_counts = Counter(a.tribe_id for a in world.agents)
            for tid, tribe in world.tribes.items():
                info = tribe.summary()
                print(
                    f"   🧬 Tribe {tid} | pop={tribe_counts.get(tid,0)} "
                    f"| symbols={info['symbols']} "
                    f"| avg_value={info['avg_value']} "
                    f"| biome={info['home_biome']}"
                )

        # ------------------------------------
        # 📚 KNOWLEDGE REPORT
        # ------------------------------------
        if step % 500 == 0:
            snapshot = world_metrics.snapshot(world.agents)

            print("\n🌍 WORLD METRICS")
            print(snapshot)

            print("📚 KNOWLEDGE METRICS")
            tribe_counts = Counter(a.tribe_id for a in world.agents)

            for tid, tribe in world.tribes.items():
                report = knowledge_metrics.tribe_report(tid, tribe)
                print(
                    f"   🧠 Tribe {tid} | "
                    f"pop={tribe_counts.get(tid,0)} | "
                    f"symbols={report['symbols']} | "
                    f"meta_ratio={report['meta_ratio']} | "
                    f"time_acc={report['temporal_accuracy']} | "
                    f"artifacts={report['artifact_coverage']} | "
                    f"depth={report['abstraction_depth']}"
                )

            print("=" * 60)

        time.sleep(0.05)


if __name__ == "__main__":
    main()

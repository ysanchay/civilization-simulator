# Civilization Simulator v1.0

**Release Date:** February 27, 2026

## Version Tag

This is the baseline release for publication.

### Core Systems (All Verified Working)

| System | File | Purpose |
|--------|------|---------|
| Agent Cognition | `agent.py` | Belief states, symbol processing |
| Culture | `culture.py` | Symbol transmission, rituals |
| Memory | `memory.py` | Short-term belief storage |
| Territory | `territory.py` | Geographic ownership, borders |
| Historical Memory | `historical_memory.py` | Events, eras, myths |
| Cognitive Stress | `cognitive_stress.py` | Intelligence limits, temporal chaos |
| Scaling Penalties | `scaling_penalties.py` | Empire fragility |
| Cultural Schism | `schism.py` | Ideological splits |
| Collapse System | `collapse.py` | Rise and fall dynamics |

### Verified Experimental Findings

1. **War Distribution**: Heavy-tailed (kurtosis 11.59) ✅
2. **Collapse Archetypes**: 4 distinct types identified ✅
3. **Complexity Growth**: Open-ended (4.6x over 1500 steps) ✅
4. **Knowledge Retention**: 41% average across runs ✅

### Files for Publication

- `README.md` - System documentation
- `PAPER.md` - Research paper draft
- `ARCHITECTURE.md` - System architecture
- `metrics/` - Experimental results

---

**DOI:** (pending arXiv submission)
**License:** MIT
**Repository:** github.com/[username]/civilization-simulator
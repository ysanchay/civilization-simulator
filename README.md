# Civilization Simulator

**An Experimental Framework for Studying Emergent Symbolic and Cultural Structures in Decentralized Multi-Agent Systems**

---

## Problem Statement

How do civilizations emerge from simple agents? What mechanisms enable symbolic abstraction, cultural memory, and open-ended complexity growth? This simulator provides a controlled environment to study these questions empirically.

**Core Questions:**
1. Can symbolic communication emerge from grounded interactions?
2. How does cultural knowledge persist across generations?
3. What causes civilizations to collapse, and can we predict it?
4. Does complexity grow indefinitely or saturate?

**Why This Matters:**
- AI Safety: Understanding emergent value systems in multi-agent systems
- Complexity Science: Empirical study of phase transitions and critical phenomena
- Cognitive Science: Grounded symbol emergence and cultural evolution

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CIVILIZATION SIMULATOR                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   WORLD      │    │   AGENTS    │    │   CULTURE    │       │
│  │   (Grid)     │◄──►│  (Tribes)   │◄──►│  (Symbols)   │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │  TERRITORY   │    │  COGNITION   │    │   MEMORY     │       │
│  │  (Borders)   │    │  (Beliefs)   │    │  (History)   │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │               │
│         └───────────────────┼───────────────────┘               │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    EMERGENT PHENOMENA                     │   │
│  │  • Wars (heavy-tailed)    • Collapses (archetyped)       │   │
│  │  • Schisms (ideological)  • Complexity growth            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Component Overview

| Component | Responsibility | Key Metrics |
|-----------|---------------|-------------|
| **World** | 2D grid environment | Size, carrying capacity |
| **Agents** | Tribal entities | Population, efficiency |
| **Culture** | Symbol systems | Symbol count, meta-levels |
| **Cognition** | Belief states | Accuracy, stress level |
| **Territory** | Geographic control | Size, borders |
| **Memory** | Historical record | Events, eras |

---

## Agent Cognition Design

### Belief States

Each agent maintains a belief state representing their understanding of the world:

```python
belief_state = {
    'symbols': {pattern: value},     # Grounded symbols
    'meta_symbols': {combo: value},  # Abstracted combinations
    'territory': set(cells),          # Controlled land
    'history': [events],              # Remembered past
    'efficiency': float,              # Current performance
}
```

### Decision Process

1. **Perception**: Observe neighboring cells and agents
2. **Symbol Matching**: Compare observations to known symbols
3. **Belief Update**: Bayesian-like update based on match quality
4. **Action Selection**: Choose action maximizing expected value
5. **Learning**: Update symbol values based on outcomes

### Cognitive Stress

Agents experience stress under:
- Rapid environmental change
- Information overload
- Resource scarcity
- Temporal chaos (irregular cycles)

Stress reduces effective intelligence, creating realistic cognitive limits.

---

## Symbol Grounding Mechanism

### From Perception to Symbol

Symbols emerge from grounded sensorimotor experiences:

```
Perception → Pattern Extraction → Symbol Formation → Value Assignment
     │              │                    │                  │
   [cell]        [biome]            [pattern]          [utility]
```

### Symbol Types

| Level | Type | Example | Grounding |
|-------|------|---------|-----------|
| 0 | Primitive | `FERTILE` | Direct cell observation |
| 1 | Composed | `FARM` | Multiple primitives combined |
| 2 | Abstract | `TERRITORY` | Spatial relationships |
| 3 | Meta | `NATION` | Other symbols as components |

### Cultural Transmission

Symbols spread between agents through:
1. **Proximity**: Neighboring tribes exchange symbols
2. **Conquest**: Winners transmit to losers
3. **Trade**: Mutual exchange benefits both parties
4. **Schism**: Splinter groups carry modified symbols

---

## Cultural Forgetting Model

### Why Forgetting Occurs

Civilizations forget when:
1. **Population collapse**: Knowledge holders die
2. **Symbol disuse**: Patterns become irrelevant
3. **Cultural schism**: Ideological conflicts erase symbols
4. **Efficiency decay**: Large empires can't maintain knowledge

### Forgetting Rate

```
forget_rate = f(population, symbols, efficiency, stress)

Where:
- Higher population → Lower forget rate (more holders)
- More symbols → Higher forget rate (more to maintain)
- Lower efficiency → Higher forget rate (coordination failure)
- Higher stress → Higher forget rate (cognitive overload)
```

### Knowledge Bottlenecks

Critical symbols held by few agents create vulnerability:
- Single-holder symbols → High risk of loss
- Distributed symbols → Robust to individual death

---

## Experimental Findings

### 1. War Distribution (Heavy-Tailed)

**Hypothesis**: War frequency follows power-law distribution

**Method**: 10 runs × 500 steps, track war intervals

**Result**: 
- Kurtosis: **11.59** (heavy-tailed)
- Wars cluster in time (not Poisson)
- Evidence for contagious conflict dynamics

```
War Intervals Distribution:
  Mean: 4.8 steps
  Std: 4.8 steps
  Heavy-tailed: ✅ CONFIRMED
```

### 2. Collapse Archetypes

**Hypothesis**: Distinct collapse types exist

**Method**: 15 runs × 500 steps, cluster collapse events

**Result**: 4 archetypes identified

| Type | Frequency | Cause | Pop Before |
|------|-----------|-------|------------|
| Efficiency Collapse | 42.1% | Scaling failure | 59 |
| Overpopulation | 36.8% | Resource exhaustion | 69 |
| Territory Loss | 13.2% | Military defeat | 36 |
| Compound | 7.9% | Multiple factors | 36 |

### 3. Complexity Growth (Open-Ended)

**Hypothesis**: Symbol complexity grows indefinitely

**Method**: 2 runs × 1500 steps, track symbol count

**Result**:
- Growth ratio: **4.62x**
- Slope: 406 symbols per checkpoint
- No saturation observed

```
Complexity Over Time:
  Steps 0-750:    538 avg symbols
  Steps 750-1500: 2484 avg symbols
  Growth: 4.62x
```

### 4. Knowledge Retention

**Hypothesis**: Brains persist knowledge across runs

**Method**: Load saved brains from previous runs

**Result**: 41% average retention, improving over time

---

## Open Questions

### Technical

1. **Scaling Penalties**: Why don't collapses remain heavy-tailed in long runs?
   - Hypothesis: Penalties not strong enough
   - Need: Re-tune efficiency decay parameters

2. **Symbol Optimization**: Do symbols converge to optimal count?
   - Observation: Growth continues
   - Question: Is there an upper bound?

3. **Meta-Symbol Depth**: What limits abstraction level?
   - Current: Level 3 observed
   - Question: Can higher levels emerge?

### Theoretical

1. **Phase Transitions**: Are there critical population thresholds?
   - Preliminary: Collapses increase above certain sizes
   - Need: Systematic parameter sweep

2. **Lyapunov Instability**: Is the system chaotic?
   - Prediction: Sensitive to initial conditions
   - Need: Parallel run comparison

3. **Equilibrium**: Does territory distribution stabilize?
   - Observation: Oscillates in short runs
   - Need: Longer time horizon analysis

### Applications

1. **AI Safety**: Can we detect misaligned tribes before domination?
2. **Policy**: What interventions prevent cascading collapse?
3. **Prediction**: Can we forecast schisms from symbol divergence?

---

## Quick Start

```bash
# Run a simulation
cd /home/claw/Civilization_simulator
python3 run_integrated.py --steps 1000 --agents 20

# Run validation tests
python3 test_war_distribution.py
python3 test_collapse_archetypes.py
python3 test_complexity_evolution.py

# View results
ls metrics/
```

---

## Citation

```bibtex
@misc{civilization_simulator_2026,
  title={Civilization Simulator: An Experimental Framework for 
         Studying Emergent Symbolic and Cultural Structures 
         in Decentralized Multi-Agent Systems},
  author={[Author]},
  year={2026},
  note={arXiv preprint}
}
```

---

## License

MIT License - Open for research and educational use.
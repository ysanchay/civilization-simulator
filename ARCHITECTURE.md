# System Architecture

## High-Level Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CIVILIZATION SIMULATOR v1.0                       │
│                   Experimental Multi-Agent Framework                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│      WORLD        │   │      AGENT        │   │     CULTURE       │
│   (Environment)   │   │    (Tribes)       │   │    (Symbols)      │
├───────────────────┤   ├───────────────────┤   ├───────────────────┤
│ • 2D Grid         │   │ • Belief State    │   │ • Symbols         │
│ • Biomes          │   │ • Population      │   │ • Meta-Symbols    │
│ • Resources       │   │ • Efficiency      │   │ • Rituals         │
│ • Carrying Cap    │   │ • Stress Level    │   │ • Transmission    │
└────────┬──────────┘   └─────────┬─────────┘   └────────┬──────────┘
         │                        │                      │
         │              ┌─────────┴─────────┐            │
         │              ▼                   ▼            │
         │   ┌──────────────────┐  ┌──────────────────┐  │
         │   │    COGNITION     │  │     MEMORY       │  │
         │   │  (Belief System) │  │   (Historical)   │  │
         │   ├──────────────────┤  ├──────────────────┤  │
         │   │ • Perception     │  │ • Events         │  │
         │   │ • Symbol Match   │  │ • Eras           │  │
         │   │ • Belief Update  │  │ • Myths          │  │
         │   │ • Action Select  │  │ • Narratives     │  │
         │   └────────┬─────────┘  └────────┬─────────┘  │
         │            │                     │            │
         ▼            ▼                     ▼            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         CORE SUBSYSTEMS                                  │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────────┤
│  TERRITORY  │  COGNITIVE  │  SCALING    │  SCHISM     │  COLLAPSE       │
│             │   STRESS    │  PENALTIES  │             │                 │
├─────────────┼─────────────┼─────────────┼─────────────┼─────────────────┤
│ • Borders   │ • Temporal  │ • Admin     │ • Factions  │ • Population    │
│ • Conquest  │   Chaos     │   Load      │ • Ideology  │ • Efficiency    │
│ • Homeland  │ • False     │ • Coord     │ • Conflict  │ • Knowledge     │
│ • Expansion │   Signals   │   Cost      │ • Split     │   Bottleneck    │
│ • Contested │ • Overload  │ • Decay     │ • Stability │ • Renaissance   │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       EMERGENT PHENOMENA                                 │
├───────────────────┬───────────────────┬───────────────────┬─────────────┤
│   WARS            │   COLLAPSES       │   SCHISMS         │ COMPLEXITY  │
│   (Heavy-Tailed)  │   (Archetyped)    │   (Ideological)   │ (Open-Ended)│
├───────────────────┼───────────────────┼───────────────────┼─────────────┤
│ • Clustered       │ • Efficiency (42%)│ • Symbol Conflict │ • 4.62x     │
│ • Kurtosis: 11.59 │ • Overpop (37%)   │ • Cultural Split  │   Growth    │
│ • Power-Law       │ • Territory (13%) │ • Stability Loss  │ • No        │
│ • Contagious      │ • Compound (8%)   │ • New Tribe Form  │   Saturation│
└───────────────────┴───────────────────┴───────────────────┴─────────────┘
```

## Data Flow

```
                    ┌─────────────┐
                    │   CONFIG    │
                    │  (params)   │
                    └──────┬──────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    INITIALIZATION                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   World     │  │   Agents    │  │   Symbols   │          │
│  │   Grid      │  │   Seed      │  │   Base      │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    SIMULATION LOOP                            │
│                                                               │
│  FOR step = 1 to MAX_STEPS:                                  │
│    │                                                          │
│    ├─► PERCEPTION: Agents observe world state                │
│    │                                                          │
│    ├─► COGNITION: Update belief states                       │
│    │    └─► Symbol matching, stress calculation              │
│    │                                                          │
│    ├─► ACTION: Select and execute actions                    │
│    │    └─► Expand, attack, trade, innovate                  │
│    │                                                          │
│    ├─► TERRITORY: Update borders and ownership               │
│    │                                                          │
│    ├─► CULTURE: Symbol transmission and mutation             │
│    │                                                          │
│    ├─► STRESS: Apply cognitive load                          │
│    │                                                          │
│    ├─► SCALING: Apply efficiency penalties                   │
│    │                                                          │
│    ├─► SCHISM: Check for ideological splits                  │
│    │                                                          │
│    ├─► COLLAPSE: Check for collapse conditions               │
│    │                                                          │
│    └─► RECORD: Log events and metrics                        │
│                                                               │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    OUTPUT                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Metrics   │  │   Brains    │  │   Events    │          │
│  │   JSON      │  │   PKL       │  │   Log       │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└──────────────────────────────────────────────────────────────┘
```

## Agent Cognition Detail

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT COGNITION                           │
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  PERCEPTION   │  │   BELIEFS     │  │   ACTIONS     │
├───────────────┤  ├───────────────┤  ├───────────────┤
│ • Neighbors   │  │ • Symbols     │  │ • Expand      │
│ • Resources   │  │ • Meta-Sym    │  │ • Attack      │
│ • Threats     │  │ • Territory   │  │ • Trade       │
│ • Opportunities│  │ • History     │  │ • Innovate    │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                  │                  │
        │                  ▼                  │
        │          ┌───────────────┐          │
        └─────────►│  DECISION     │◄─────────┘
                   │  PROCESS      │
                   ├───────────────┤
                   │ 1. Match to   │
                   │    symbols    │
                   │ 2. Update     │
                   │    beliefs    │
                   │ 3. Calculate  │
                   │    utilities  │
                   │ 4. Select     │
                   │    action     │
                   └───────┬───────┘
                           │
                           ▼
                   ┌───────────────┐
                   │   LEARNING    │
                   ├───────────────┤
                   │ • Symbol      │
                   │   values      │
                   │ • Efficiency  │
                   │ • Strategies  │
                   └───────────────┘
```

## Symbol Grounding Pipeline

```
RAW PERCEPTION          PATTERN              SYMBOL              VALUE
      │                   │                    │                  │
      ▼                   ▼                    ▼                  ▼
┌───────────┐      ┌───────────┐        ┌───────────┐      ┌───────────┐
│  Cell     │      │  Extract  │        │  Create   │      │  Assign   │
│  State    │─────►│  Pattern  │───────►│  Symbol   │─────►│  Value    │
│           │      │           │        │           │      │           │
│ [FERTILE] │      │ biome:    │        │ Symbol:   │      │ value:    │
│ [WATER]   │      │ "plains"  │        │ "PLAINS"  │      │ 0.85      │
│ [FOREST]  │      │           │        │           │      │           │
└───────────┘      └───────────┘        └───────────┘      └───────────┘
                                              │
                                              ▼
                                     ┌────────────────┐
                                     │  META-SYMBOLS  │
                                     │  (Level 1-3)   │
                                     ├────────────────┤
                                     │ L1: FARM       │
                                     │ L2: TERRITORY  │
                                     │ L3: NATION     │
                                     └────────────────┘
```

## Collapse Mechanism

```
┌─────────────────────────────────────────────────────────────┐
│                    COLLAPSE DETECTION                        │
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  POPULATION   │  │  EFFICIENCY   │  │   STRESS      │
│  COLLAPSE     │  │  COLLAPSE     │  │   CASCADE     │
├───────────────┤  ├───────────────┤  ├───────────────┤
│ pop > 60      │  │ eff < 0.6     │  │ stress > 0.6  │
│ AND           │  │ AND           │  │ AND           │
│ drop > 50%    │  │ large tribe   │  │ rapid change  │
│               │  │ (>40 pop)     │  │               │
│ Cause:        │  │ Cause:        │  │ Cause:        │
│ Resource      │  │ Scaling       │  │ Cognitive     │
│ exhaustion    │  │ failure       │  │ overload      │
└───────────────┘  └───────────────┘  └───────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                   ┌───────────────┐
                   │   COLLAPSE    │
                   │   EXECUTED    │
                   ├───────────────┤
                   │ • Pop reduced │
                   │ • Symbols lost│
                   │ • Brain saved │
                   │ • Event logged│
                   └───────────────┘
```

## File Structure

```
civilization_simulator/
├── config.py              # Configuration dataclasses
├── agent.py               # Agent (Tribe) implementation
├── culture.py             # Symbol system
├── memory.py              # Short-term memory
├── territory.py           # Geographic ownership
├── historical_memory.py   # Events, eras, myths
├── cognitive_stress.py    # Intelligence limits
├── scaling_penalties.py   # Empire fragility
├── schism.py              # Ideological splits
├── collapse.py            # Rise and fall
├── brain_io.py            # Save/load cognition
├── run_integrated.py      # Main simulator
├── metrics.py             # Output metrics
├── VERSION.md             # Version freeze
├── README.md              # Documentation
├── PAPER.md               # Research paper
├── ARCHITECTURE.md        # This file
├── brains/                # Saved cognition states
├── metrics/               # Experiment outputs
└── tests/                 # Validation scripts
    ├── test_war_distribution.py
    ├── test_collapse_archetypes.py
    ├── test_long_horizon.py
    └── test_complexity_evolution.py
```
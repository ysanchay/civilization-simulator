# Civilization Simulator - Use Case Guide

## 🎯 How to Make This Useful

### Quick Start: Measuring Success

```bash
# Run with metrics collection
python3 run_integrated.py --steps 1000 --metrics

# View success report
python3 -c "import json; print(json.dumps(json.load(open('metrics/metrics_latest.json')), indent=2))"
```

---

## 📊 Success Metrics

### 1. Emergence Score (0-100)
Measures **unplanned complexity** arising from simple rules.

| Component | Weight | How to Improve |
|-----------|--------|----------------|
| Vocabulary Size | 0.5/symbol | Longer simulations, more agents |
| Composed Symbols | 5/symbol | Encourage pattern repetition |
| Meta-Symbols | 10/symbol | Higher agent density |
| Wars + Alliances | 5/event | Enable competition |
| Knowledge Transfer | 5/event | Tribe proximity |

**Target:** >40 for research, >60 for gaming, >70 for AI safety

---

### 2. Survival Score (0-100)
Measures **population stability and adaptability**.

| Component | Weight | How to Improve |
|-----------|--------|----------------|
| Population Stability | 50% | Balanced food/danger |
| Tribes Surviving | 20%/tribe | Smaller starting tribes |
| Reproduction Rate | 30% | Lower metabolism, more food |

**Target:** >50 for sustainability

---

### 3. Intelligence Score (0-100)
Measures **cognitive sophistication**.

| Component | Weight | How to Improve |
|-----------|--------|----------------|
| Temporal Accuracy | 50% | More time steps |
| Abstraction Depth | 20/level | More symbols, longer runs |
| Goal Completion | 30% | Clear reward signals |

**Target:** >30 for basic, >50 for advanced, >70 for research

---

## 🎮 Use Case 1: Gaming Industry

### Application
**Emergent NPCs with unique cultures, languages, and politics**

### Setup
```python
config = SimulationConfig()
config.world.width = 50
config.world.height = 50
config.initial_agents = 30
config.innovation_enabled = True
config.competition_enabled = True

# Run for game content generation
sim = CivilizationSimulator(config)
sim.run(max_steps=50000)
```

### Success Criteria
| Metric | Target | Why |
|--------|--------|-----|
| Vocabulary | >100 | Unique faction languages |
| Meta-symbols | >10 | Complex cultural concepts |
| Wars + Alliances | >20 | Dynamic politics |
| Tribe Survival | 3-5 | Multiple playable factions |

### Integration
```python
# Export game-ready data
from visualization.export import Exporter

exporter = Exporter("game_export")
exporter.export_factions(sim.world.tribes)  # NPC factions
exporter.export_languages(sim.culture_agents)  # Unique dialects
exporter.export_history(sim.step_history)  # Timeline events
```

### Monetization Path
1. **Content Generation Tool** - $99/month for indie developers
2. **NPC Engine SDK** - License to game studios
3. **Procedural Storytelling API** - Cloud service

---

## 🛡️ Use Case 2: AI Safety Research

### Application
**Study emergent behavior, alignment, and value drift**

### Setup
```python
config = SimulationConfig()
config.world.width = 30
config.world.height = 30
config.initial_agents = 20
config.max_steps = 100000

# Track specific behaviors
sim.experiment_agent.create_experiment(
    name="alignment_test",
    parameters={
        "reward_signal": "cooperative",  # or "competitive"
        "goal_formation": True,
        "value_drift_tracking": True,
    }
)
```

### Success Criteria
| Metric | Target | Why |
|--------|--------|-----|
| Temporal Accuracy | >0.7 | Predictable behavior |
| Abstraction Depth | =3 | Interpretable reasoning |
| Dominance Stability | >0.5 | Stable power dynamics |

### Research Outputs
1. **Emergent Goal Analysis** - How goals form without explicit programming
2. **Value Drift Measurement** - How agent values change over time
3. **Coordination Emergence** - When/why agents cooperate vs compete

### Publication Path
1. Run controlled experiments (10+ runs per condition)
2. Use `experiment_agent` for statistical analysis
3. Export data in publication-ready format

---

## 📚 Use Case 3: Education & Research

### Application
**Teaching complexity science, cultural evolution, emergence**

### Setup
```python
# Educational preset
config = SimulationConfig()
config.world.width = 20
config.world.height = 20
config.initial_agents = 10
config.visualization.enabled = True
config.visualization.refresh_rate = 0.5  # Slower for observation

sim = CivilizationSimulator(config)
sim.seed_agents(10)
sim.run(visualize=True)  # Real-time visualization
```

### Learning Objectives
| Concept | Visualization | Metric |
|---------|--------------|--------|
| Emergence | Symbol creation over time | Vocabulary growth |
| Evolution | Agent traits changing | Generation progression |
| Self-organization | Tribe formation | Tribe count |
| Cooperation | Alliances forming | Alliance count |
| Competition | Wars occurring | War count |

### Teaching Mode
```bash
# Run with detailed logging
python3 run_integrated.py --steps 2000 --teaching-mode

# Generates:
# - Step-by-step explanations
# - Event timeline
# - Concept highlights
```

---

## 🤖 Use Case 4: Swarm Intelligence / Robotics

### Application
**Distributed decision-making, self-organizing systems**

### Setup
```python
config = SimulationConfig()
config.world.width = 100
config.world.height = 100
config.initial_agents = 200  # Large swarm
config.agent.metabolism = 0.5  # Lower energy cost
config.culture.max_symbols = 50  # Simpler communication
config.competition_enabled = False  # Cooperation focus
```

### Success Criteria
| Metric | Target | Why |
|--------|--------|-----|
| Knowledge Transfer | >20 | Information spreads |
| Goal Completion | >0.4 | Effective coordination |
| Survival Rate | >80% | Robust behavior |

### Transfer to Robotics
```python
# Export coordination patterns
patterns = sim.innovation_agent.extract_patterns()

# These patterns can be used in:
# - Robot swarm control algorithms
# - Distributed consensus protocols
# - Self-healing network topologies
```

---

## 📈 Measuring ROI

### For Gaming Companies
```
ROI = (Hours of unique content generated / Development time) * Quality Factor

Example:
- 1 simulation run = 50 unique faction storylines
- Development time = 0 hours (automated)
- Quality Factor = (Emergence Score / 100)

ROI = 50 * (65/100) = 32.5 content-hours per run
```

### For Research Labs
```
ROI = (Publications * Impact Factor) / Compute Cost

Example:
- 10 runs = 1 publication
- Impact Factor = 2.5 (complexity science journal)
- Compute Cost = $10 (cloud)

ROI = 2.5 / 10 = 0.25 impact per dollar
```

### For Education
```
ROI = (Students * Learning Gain) / Instructor Time

Example:
- 30 students per class
- Learning gain = 40% (pre/post test improvement)
- Instructor time = 2 hours (setup + facilitation)

ROI = 30 * 0.4 / 2 = 6 learning-units per hour
```

---

## 🚀 Production Checklist

### Before Deployment

- [ ] Run 10+ simulations with different seeds
- [ ] Verify metrics meet use case targets
- [ ] Export sample outputs for review
- [ ] Document configuration for reproducibility
- [ ] Set up monitoring/logging

### Scale Considerations

| Agents | World Size | Steps | Memory | Time |
|--------|------------|-------|--------|------|
| 10 | 20x20 | 1,000 | ~50MB | ~1min |
| 50 | 40x40 | 10,000 | ~200MB | ~10min |
| 200 | 100x100 | 100,000 | ~1GB | ~2hr |
| 1000 | 200x200 | 1,000,000 | ~5GB | ~24hr |

### Optimization Tips
- Disable visualization for long runs
- Use checkpointing for recovery
- Parallel run multiple experiments
- Use `--no-viz` flag for production

---

## 💰 Monetization Strategies

### 1. SaaS Platform
- Hosted simulation environment
- API access for integration
- Tiered pricing: Free / Pro $49/mo / Enterprise $499/mo

### 2. Content Generation Tool
- Game studios: $999/year
- Indie developers: $99/year
- Includes export formats for Unity, Unreal, Godot

### 3. Research License
- Academic: Free (with citation)
- Commercial research: $5,000/year
- Includes support and custom experiments

### 4. Educational License
- K-12: Free
- University: $499/year
- Includes curriculum materials

---

## 📊 Example: Run a Successful Experiment

```bash
# 1. Define experiment
python3 -c "
from agents.experiment_agent import ExperimentAgent, ExperimentConfig

exp = ExperimentAgent()
exp.create_experiment(
    name='emergence_study_1',
    parameters={'world_size': (30, 30), 'agents': 15},
    max_steps=5000,
    num_runs=10,
    baselines=['standard', 'high_innovation']
)
exp.save()
"

# 2. Run experiment
python3 run_integrated.py --experiment emergence_study_1

# 3. Analyze results
python3 -c "
from agents.experiment_agent import ExperimentAgent
exp = ExperimentAgent()
exp.load('emergence_study_1')
print(exp.generate_report())
"

# 4. Evaluate for use case
python3 -c "
from success_metrics import evaluate_simulation_use_case
result = evaluate_simulation_use_case('gaming', emergence, survival, intelligence)
print(f'Suitable: {result[\"suitable\"]}')
print(f'Score: {result[\"score\"]}')
"
```

---

## ✅ Success = Meeting Use Case Requirements

| Use Case | Emergence | Survival | Intelligence | Overall |
|----------|-----------|----------|--------------|---------|
| Gaming | >40 | >40 | >20 | >35 |
| AI Safety | >50 | >50 | >50 | >50 |
| Education | >25 | >40 | >30 | >30 |
| Robotics | >35 | >60 | >40 | >45 |

**Your simulation from the test:**
- Vocabulary: ~31 symbols
- Meta-symbols: Multiple forming
- Tribes: 5 (1 extinct)
- Abstraction: Level 2-3
- Wars/Alliances: Some

**Estimated scores:**
- Emergence: ~35-45
- Survival: ~50-60
- Intelligence: ~30-40
- **Overall: ~40-48**

**Verdict:** Suitable for **Gaming** and **Education** use cases. Needs higher emergence scores for AI Safety and Robotics.
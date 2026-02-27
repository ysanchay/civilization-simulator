# Figures

This directory contains figures for the research paper.

## Required Figures

1. **war_distribution.png** - Histogram of war intervals showing heavy tails
2. **collapse_archetypes.png** - Pie chart or bar chart of collapse types
3. **complexity_growth.png** - Line graph showing symbol growth over time
4. **architecture.png** - System architecture diagram

## Generating Figures

Run the test scripts and use matplotlib to generate:

```python
# Example for war distribution
import matplotlib.pyplot as plt
import numpy as np

intervals = [...]  # from test_war_distribution.py
plt.hist(intervals, bins=50)
plt.xlabel('Inter-war Interval (steps)')
plt.ylabel('Frequency')
plt.title('War Interval Distribution (Kurtosis: 11.59)')
plt.savefig('figures/war_distribution.png', dpi=150)
```
# Melee Choice Architecture v0.1

Bounded experimental harness for Cross/Beat candidates CB0-CB3 and guard-commitment candidates GC0-GC3.

The harness imports the current named-guard engine for regression alignment but does not modify it. Cross/Beat Monte Carlo cells are branch-forced outcome verification, not choice-frequency claims. Guard timing behavior uses a reduced scripted tactical roster and reports benefit harvesting/exposure metrics rather than guard balance or win rate. GC3 is research-classified but not behavior-tested because the transition research does not support a restrictive voluntary adjacency graph.

Run:

```powershell
python simulations/melee_choice_architecture_v0_1/simulate.py
python -m unittest tests.test_melee_choice_architecture_v01
```

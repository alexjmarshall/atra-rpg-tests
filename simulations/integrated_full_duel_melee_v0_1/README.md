# Integrated Full-Duel Melee Cleanup / Incentive Audit v0.1

This bounded audit calls `simulations.shared.provisional_longsword.CurrentEngine`
for legality and resolution. It adds only duel orchestration, player-legitimate
policy views, deterministic branch enumeration, instrumentation, and reporting.

Run from the repository root with the workspace Python runtime:

```text
python simulations/integrated_full_duel_melee_v0_1/simulate.py
python -m unittest tests.test_integrated_full_duel_melee_v01 -v
```

The fixed Monte Carlo seed is `13082026`; exact local branches are enumerated
before duel sampling. Generated results are written to
`reports/integrated-full-duel-melee-cleanup-v01-results.json`.

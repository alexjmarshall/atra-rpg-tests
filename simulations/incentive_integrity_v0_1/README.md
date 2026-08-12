# Melee Incentive Integrity v0.1 deterministic probes

This directory contains diagnosis-only probes for the Melee Incentive
Integrity v0.1 audit.  The probe imports the governing provisional engine and
the bounded guard, bridge, and Crown harnesses.  It runs no fight matrix and
changes no combat rule.

Run:

```powershell
python simulations/incentive_integrity_v0_1/analyze.py
```

The script writes `controlled-results.json` beside itself.  Values labelled
`policy` are simulator utilities or deterministic argmax results; they are not
rules-derived player value.

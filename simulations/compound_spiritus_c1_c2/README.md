# Compound Spiritus C1/C2 pricing experiment

Status: **PROVISIONAL experiment; no canonical rule changes**.

This dedicated experiment imports the prior Spiritus/Parry simulator and holds
P1, D1, S2, maximum Spiritus 8, Variant A, generic d6+1 damage, and the current
three-Play cap constant. It compares only a common compound price of 1 or 2 for
Absetzen, Scambiar di Punta, and Schielhau.

Run from the repository root with the bundled/runtime Python:

```powershell
python simulations/compound_spiritus_c1_c2/simulate.py
```

The full seeded run writes:

- `results.json` — complete machine-readable primary, asymmetric, policy-surface,
  shadow-price, and three-fight results;
- `fresh-duel-summary.csv`;
- `compound-play-summary.csv`;
- `shadow-price-summary.csv`;
- `sequence-summary.csv`.

Default trial counts are 12,000 per primary cell, 6,000 per optional asymmetric
cell, and 8,000 per three-fight sequence cell. The default seed is `8212026`.

Power Strike competition remains unmodeled because the repository still has no
mature Guard/Chamber implementation suitable for this bounded price test.

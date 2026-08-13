# Melee Repertoire Integrity Repair v0.1

This scoped harness uses the authoritative shared exchange engine and exact
enumeration/branch forcing. It does not run Named Guard v0.2 or a broad duel
matrix, and it does not promote O1/O2 or W1/W2.

Run from the repository root:

```powershell
python simulations/melee_repertoire_integrity_repair_v0_1/simulate.py
python -m unittest tests.test_melee_repertoire_integrity_repair_v01 -v
```

Outputs:

- `reports/melee-repertoire-integrity-repair-v01-results.json`
- `reports/melee-repertoire-integrity-repair-v01-results.md`

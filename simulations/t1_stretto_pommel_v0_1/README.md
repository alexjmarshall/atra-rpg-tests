# T1 / Stretto / Pommel Integration v0.1

Status: bounded candidate overlay; no governing promotion.

`candidate_engine.py` subclasses the authoritative shared exchange engine. It
adds only E1/L1 T1 timing and Pommel P1/P2 candidate behavior. Declining E1
returns to the inherited H3 methods; the shared engine is not edited.

`simulate.py` emits exact local matrices, nine deterministic state traces, and
ten fixed-seed integrated candidate scenarios. Run from the repository root:

```powershell
python simulations/t1_stretto_pommel_v0_1/simulate.py
```

The output JSON is audit evidence, not canon.


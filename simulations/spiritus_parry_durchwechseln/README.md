# Spiritus / vulnerable Basic Parry experiment

Status: **PROVISIONAL experiment; no canonical rule changes**.

Run from the repository root:

```powershell
python simulations/spiritus_parry_durchwechseln/simulate.py
```

The run writes:

- `results.json`, the complete nested result set;
- `fresh-duel-summary.csv`;
- `compound-play-summary.csv`;
- `timing-sensitivity-summary.csv`;
- `sequence-summary.csv`;
- `reports/spiritus-parry-durchwechseln-results.md`.

## Explicit Spiritus valuation

The policy compares legal choices in expected-hit utility and charges a declared
Play the loss in a concave reserve-value function:

`V(s,n,r) = 0.78 sqrt(s) + sum(j=1..n, 0.82^j * 0.48 sqrt(project(s,j,r)))`.

`s` is current Spiritus, `n` is the number of later fights in the finite
horizon, and `r` is the experimental recovery policy. `project` holds Spiritus
for R0, adds two per boundary (capped at eight) for R2, and projects eight for
RFULL. The current-fight term means the final Spiritus always has positive
option value. The later-fight terms make Fight 1 and Fight 2 decisions value
carryover instead of treating unused Spiritus as worthless at the fight end.
The declaration charge is multiplied by `0.9 + 0.2 * (enemy Spiritus / 8)`:
the policy conserves slightly more against an opponent who can still fund
advanced replies and slightly less against an exhausted opponent.

Choices use a seeded softmax (temperature 0.18), so mixed choices remain
possible. The policy never hard-codes always/never use of Durchwechseln, Basic
Parry, or a compound counter. Damage and survival pressure modify expected-hit
utility; Spiritus totals, HP, action availability, known repertoire, success
chances, affordability, and remaining sequence horizon are public policy inputs.
Observed Schielhau also reduces future descending-cut selection; observed
Durchwechseln changes P1 defence valuation.

The simulator records a `future_value_conservation` event when later-fight value
changes a paid-Play decision from the no-later-fights deterministic preference
to conservation. This is the report's narrow operational definition of
conservation. The sequence-level probability counts this event in Fight 1 only,
matching the requested "conserving Spiritus in Fight 1 for later fights" metric.

## Scope limits

Absetzen, Scambiar di Punta, and Schielhau use the single-roll, action-spending
Variant A chassis. Schielhau's long point is intrinsic and S2 is the primary
Durchwechseln interaction. Zornhau-Ort, Nachreisen, and Pommel Strike retain
their prior provisional zero-cost exercise mechanics. The simulator does not
model Guards well enough to add a reliable Power Strike competition test.

# Longsword Mechanical Prototype Results

Status: **PROVISIONAL experiment; not canonical rules**

This seeded Monte Carlo comparison isolates six historically audited Plays. Canonical Play mechanics remain null. Costs, tier requirements, final wording, engagement rules, close-crossing generation, bind softness, and AI selection policy are experimental assumptions.

## Variant definitions

- **A:** Absetzen and Scambiar di Punta use one combined roll, spend the action, cancel damage and return damage on success.
- **B:** same combined roll, but preserve the action on success; failure or Durchwechseln bypass spends it.
- **C:** spend the action, roll defence first, then make a separate attack roll only after defensive success.
- **Baseline:** basic Strike/Parry only; no prototype Plays.

## Outcome summary

| Scenario | Variant | Focal win rate | Effect vs baseline | Prototype damage share | Actions spent/fight | Actions preserved/fight | Avg chain (Play exchanges) | 3-Play cap / exchange | Fights reaching cap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| duel | baseline | 50.03% | +0.00% | 0.00% | 0.000 | 0.000 | 0.000 | 0.000% | 0.00% |
| duel | A | 64.40% | +14.36% | 35.77% | 1.249 | 0.000 | 1.020 | 0.000% | 0.00% |
| duel | B | 65.11% | +15.08% | 35.00% | 1.027 | 0.196 | 1.020 | 0.000% | 0.00% |
| duel | C | 61.46% | +11.43% | 33.06% | 1.298 | 0.000 | 1.019 | 0.000% | 0.00% |
| one-versus-two | baseline | 3.38% | +0.00% | 0.00% | 0.000 | 0.000 | 0.000 | 0.000% | 0.00% |
| one-versus-two | A | 8.24% | +4.86% | 25.85% | 1.174 | 0.000 | 1.071 | 0.000% | 0.00% |
| one-versus-two | B | 9.74% | +6.36% | 25.74% | 1.036 | 0.153 | 1.072 | 0.000% | 0.00% |
| one-versus-two | C | 7.15% | +3.77% | 23.97% | 1.186 | 0.000 | 1.070 | 0.000% | 0.00% |

## Per-Play use, success, and damage

Use frequency is mean declarations per fight. Success is complete success per declaration; for sequential variant C, the separate defensive-success rate is also shown. Damage is mean attributed damage per fight.

### duel

| Variant | Play | Uses/fight | Success | Defensive success | Damage/fight | Actions spent/fight | Actions preserved/fight |
|---|---|---:|---:|---:|---:|---:|---:|
| A | Absetzen | 0.200 | 49.27% | 49.27% | 0.446 | 0.200 | 0.000 |
| A | Zornhau-Ort | 0.344 | 49.46% | 49.46% | 0.193 | 0.344 | 0.000 |
| A | Durchwechseln | 1.135 | 49.79% | 0.00% | 2.546 | 0.000 | 0.000 |
| A | Scambiar di Punta | 0.204 | 50.24% | 50.24% | 0.462 | 0.204 | 0.000 |
| A | Nachreisen | 0.442 | 50.69% | 0.00% | 0.846 | 0.442 | 0.000 |
| A | Pommel Strike | 0.060 | 47.70% | 0.00% | 0.127 | 0.060 | 0.000 |
| B | Absetzen | 0.197 | 49.19% | 49.19% | 0.436 | 0.100 | 0.097 |
| B | Zornhau-Ort | 0.344 | 49.53% | 49.53% | 0.192 | 0.344 | 0.000 |
| B | Durchwechseln | 1.102 | 50.23% | 0.00% | 2.486 | 0.000 | 0.000 |
| B | Scambiar di Punta | 0.196 | 50.86% | 50.86% | 0.445 | 0.096 | 0.100 |
| B | Nachreisen | 0.428 | 50.02% | 0.00% | 0.814 | 0.428 | 0.000 |
| B | Pommel Strike | 0.058 | 49.14% | 0.00% | 0.129 | 0.058 | 0.000 |
| C | Absetzen | 0.214 | 24.41% | 48.94% | 0.233 | 0.214 | 0.000 |
| C | Zornhau-Ort | 0.363 | 50.66% | 50.66% | 0.210 | 0.363 | 0.000 |
| C | Durchwechseln | 1.168 | 49.79% | 0.00% | 2.626 | 0.000 | 0.000 |
| C | Scambiar di Punta | 0.211 | 24.37% | 49.68% | 0.232 | 0.211 | 0.000 |
| C | Nachreisen | 0.448 | 49.61% | 0.00% | 0.840 | 0.448 | 0.000 |
| C | Pommel Strike | 0.062 | 49.09% | 0.00% | 0.136 | 0.062 | 0.000 |

### one-versus-two

| Variant | Play | Uses/fight | Success | Defensive success | Damage/fight | Actions spent/fight | Actions preserved/fight |
|---|---|---:|---:|---:|---:|---:|---:|
| A | Absetzen | 0.155 | 49.82% | 49.82% | 0.346 | 0.155 | 0.000 |
| A | Zornhau-Ort | 0.270 | 49.83% | 49.83% | 0.152 | 0.270 | 0.000 |
| A | Durchwechseln | 1.018 | 50.20% | 0.00% | 2.309 | 0.000 | 0.000 |
| A | Scambiar di Punta | 0.155 | 50.37% | 50.37% | 0.356 | 0.155 | 0.000 |
| A | Nachreisen | 0.539 | 50.36% | 0.00% | 0.740 | 0.539 | 0.000 |
| A | Pommel Strike | 0.055 | 51.67% | 0.00% | 0.127 | 0.055 | 0.000 |
| B | Absetzen | 0.157 | 49.70% | 49.70% | 0.353 | 0.079 | 0.078 |
| B | Zornhau-Ort | 0.265 | 49.71% | 49.71% | 0.145 | 0.265 | 0.000 |
| B | Durchwechseln | 1.037 | 49.94% | 0.00% | 2.330 | 0.000 | 0.000 |
| B | Scambiar di Punta | 0.154 | 48.72% | 48.72% | 0.340 | 0.079 | 0.075 |
| B | Nachreisen | 0.558 | 50.04% | 0.00% | 0.756 | 0.558 | 0.000 |
| B | Pommel Strike | 0.056 | 53.20% | 0.00% | 0.136 | 0.056 | 0.000 |
| C | Absetzen | 0.156 | 24.45% | 48.98% | 0.173 | 0.156 | 0.000 |
| C | Zornhau-Ort | 0.266 | 49.90% | 49.90% | 0.155 | 0.266 | 0.000 |
| C | Durchwechseln | 1.031 | 49.99% | 0.00% | 2.318 | 0.000 | 0.000 |
| C | Scambiar di Punta | 0.161 | 23.16% | 48.13% | 0.167 | 0.161 | 0.000 |
| C | Nachreisen | 0.550 | 49.93% | 0.00% | 0.741 | 0.550 | 0.000 |
| C | Pommel Strike | 0.054 | 49.91% | 0.00% | 0.121 | 0.054 | 0.000 |

## Interpretation limits

- Incoming attacks explicitly carry type, line, and commitment. Pair state explicitly uses `none`, `bind-crossing`, or `close-crossing`; recovery uses the exact missed-committed-cut window for Nachreisen.
- Durchwechseln is checked only after a blade-seeking defence is declared and while contact is `none`. The simulator records any violation; all published cells must report zero.
- Zornhau-Ort's counter-cut is defensive and non-damaging in this experiment. Its point is a separate conditional roll after a soft bind; the 50% soft-bind rate is a calibration assumption, not a historical frequency.
- A basic successful Parry creates a close crossing 25% of the time solely to exercise Pommel Strike. Pommel Strike uses Longsword and has no Wrestling prerequisite.
- d6+1 is used for every damaging success, including the pommel, to avoid deciding the OPEN weapon-profile question. This is not a claim that all damage profiles should match.
- The three-Play cap is enforced without resolving the packet's OPEN four-slot timing contradiction. No fourth Play is admitted.
- The observed cap frequency is zero because the effectiveness scenarios give the package only to the focal side; the six-Play subset then produces at most an initiation plus one continuation, or one remedy. Zero here is a coverage finding, not evidence that the cap can never bind in a mirrored or expanded curriculum.

Seed: `240807`. Trials per scenario/variant: `30000`.

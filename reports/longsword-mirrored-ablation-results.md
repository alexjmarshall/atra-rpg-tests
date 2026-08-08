# Mirrored Longsword Prototype and Per-Play Ablations

Status: **PROVISIONAL experiment; no final costs, tiers, or wording**

Both equal-Skill-10 duelists possess the same repertoire. Absetzen and Scambiar di Punta use Variant A. Action preservation is disabled. Each ablation removes one Play from both fighters.

## Full-repertoire headline

- Successful basic defensive choices creating a Durchwechseln opportunity: **49.22%**.
- Durchwechseln attempts: **0.913 per fight**; success **50.28%**.
- Schielhau long-point rejoinder: **0.138 attempts per fight**; answered **50.95%**; damage **0.320 per fight** (**2.45% of all damage; 5.68% of Play-attributed damage**).

## Ablation outcomes

| Removed from both fighters | Uses/fight | Δ uses | Play damage/fight | Δ damage | Avg rounds | Δ rounds | Double defeats | Actions/fight | Play actions/fight |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| None (full) | 3.555 | +0.000 | 5.630 | +0.000 | 4.183 | +0.000 | 0.000% | 8.359 | 2.642 |
| Absetzen | 3.544 | -0.011 | 5.597 | -0.033 | 4.178 | -0.005 | 0.000% | 8.350 | 2.633 |
| Zornhau-Ort | 3.482 | -0.073 | 5.795 | +0.166 | 4.090 | -0.093 | 0.000% | 8.172 | 2.584 |
| Durchwechseln | 2.773 | -0.782 | 5.259 | -0.371 | 4.390 | +0.207 | 0.000% | 8.770 | 2.773 |
| Scambiar di Punta | 3.527 | -0.027 | 5.564 | -0.066 | 4.174 | -0.009 | 0.000% | 8.341 | 2.620 |
| Nachreisen | 2.513 | -1.042 | 3.655 | -1.975 | 4.191 | +0.008 | 0.000% | 8.374 | 1.604 |
| Pommel Strike | 3.560 | +0.005 | 5.544 | -0.086 | 4.196 | +0.012 | 0.000% | 8.391 | 2.626 |
| Schielhau | 3.485 | -0.070 | 5.206 | -0.424 | 4.386 | +0.203 | 0.000% | 8.761 | 2.575 |

### Per-Play substitution after removal

The last two columns identify the largest compensating change among Plays that remain available; complete per-Play values are retained in `results.json`.

| Removed | Removed Play's full uses/fight | Removed Play's full damage/fight | Largest remaining use change | Largest remaining damage change |
|---|---:|---:|---|---|
| Absetzen | 0.331 | 0.373 | Scambiar di Punta +0.344 | Scambiar di Punta +0.367 |
| Zornhau-Ort | 0.364 | 0.104 | Schielhau +0.341 | Schielhau +0.571 |
| Durchwechseln | 0.913 | 1.753 | Nachreisen +0.032 | Absetzen +0.427 |
| Scambiar di Punta | 0.331 | 0.383 | Absetzen +0.335 | Absetzen +0.359 |
| Nachreisen | 1.017 | 1.974 | Zornhau-Ort -0.052 | Schielhau -0.079 |
| Pommel Strike | 0.044 | 0.099 | Durchwechseln +0.020 | Durchwechseln +0.043 |
| Schielhau | 0.554 | 0.943 | Zornhau-Ort +0.387 | Durchwechseln +0.277 |

## Tactical-state frequencies by ablation

Frequencies are occurrences per exchange, not probabilities that the state persists.

| Removed | Bind-crossing | Close-crossing | Recovery created | Recovery exploited | Durch opportunity/basic defence |
|---|---:|---:|---:|---:|---:|
| None | 9.55% | 0.70% | 20.72% | 16.15% | 49.22% |
| Absetzen | 9.53% | 0.70% | 20.47% | 15.91% | 49.61% |
| Zornhau-Ort | 10.27% | 0.75% | 20.43% | 15.97% | 50.67% |
| Durchwechseln | 15.51% | 0.93% | 20.44% | 15.89% | 0.00% |
| Scambiar di Punta | 9.53% | 0.69% | 20.39% | 15.87% | 50.47% |
| Nachreisen | 9.50% | 0.78% | 14.88% | 0.00% | 50.05% |
| Pommel Strike | 9.75% | 0.73% | 20.62% | 16.04% | 50.02% |
| Schielhau | 8.60% | 1.01% | 20.34% | 15.90% | 49.72% |

## Durchwechseln and Schielhau interaction

| Removed | Successful basic defences | Opportunity fraction | Durch attempts/fight | Durch success | Rejoinder attempts/fight | Rejoinder answers | Rejoinder damage/fight |
|---|---:|---:|---:|---:|---:|---:|---:|
| None | 9576 | 49.22% | 0.913 | 50.28% | 0.138 | 50.95% | 0.320 |
| Absetzen | 9651 | 49.61% | 0.911 | 50.50% | 0.141 | 49.47% | 0.314 |
| Zornhau-Ort | 9392 | 50.67% | 0.898 | 49.98% | 0.222 | 50.11% | 0.499 |
| Durchwechseln | 9997 | 0.00% | 0.000 | 0.00% | 0.000 | 0.00% | 0.000 |
| Scambiar di Punta | 9590 | 50.47% | 0.908 | 49.87% | 0.136 | 50.46% | 0.307 |
| Nachreisen | 10389 | 50.05% | 0.909 | 50.19% | 0.132 | 49.57% | 0.296 |
| Pommel Strike | 9860 | 50.02% | 0.933 | 50.13% | 0.139 | 50.20% | 0.312 |
| Schielhau | 14126 | 49.72% | 0.910 | 49.78% | 0.000 | 0.00% | 0.000 |

## Learned-Play chain stress

| Removed | 0 Plays | 1 Play | 2 Plays | 3 Plays | Attempted fourth Plays |
|---|---:|---:|---:|---:|---:|
| None | 58.50% | 27.72% | 12.60% | 1.18% | 0 |
| Absetzen | 58.41% | 27.84% | 12.62% | 1.13% | 0 |
| Zornhau-Ort | 58.28% | 27.90% | 12.67% | 1.16% | 0 |
| Durchwechseln | 60.25% | 37.51% | 2.24% | 0.00% | 0 |
| Scambiar di Punta | 58.61% | 27.74% | 12.55% | 1.10% | 0 |
| Nachreisen | 72.48% | 15.16% | 12.36% | 0.00% | 0 |
| Pommel Strike | 58.48% | 27.52% | 12.87% | 1.13% | 0 |
| Schielhau | 60.59% | 27.16% | 11.11% | 1.15% | 0 |

### Exact full-repertoire cap sequences

- Nachreisen → Zornhau-Ort → Durchwechseln: **1509** exchanges
- Nachreisen → Schielhau → Durchwechseln: **1470** exchanges

### Attempted fourth-Play sequences

- **0.** No legal fourth Play became eligible in this seven-Play mirrored repertoire; this is reported as a coverage result, not a resolution of the packet's timing question.

## Artificial calibration assumptions—do not tune to these

- **Soft/hard bind:** successful eligible Zornhau-Ort binds are labeled soft with fixed probability `0.5`. This exists only to exercise the conditional point continuation.
- **Close crossing:** successful eligible basic defences create close-crossing with fixed probability `0.25`. This exists only to exercise Pommel Strike.
- Both rates are held constant in every ablation. No Zornhau-Ort or Pommel Strike rule, cost, tier, or balance conclusion should be fitted to them.
- Basic successful parries are classified blade-seeking 50% of the time as a declared AI-policy assumption. It is not a historical frequency.

## Source-bounded rejoinder

Schielhau is available only against a high descending cut. Its long-point rejoinder is attempted only if the same opponent then succeeds with Durchwechseln below that Schielhau before contact. It is never offered after an arbitrary defence or against a generic feint.

Seed: `240823`. Trials per cell: `40000`. Precondition violations in full cell: `0`.

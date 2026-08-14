# Compound Spiritus C1/C2 Results

Status: **PROVISIONAL bounded pricing experiment; no canonical rule change**

## Executive result

**C2 is the better next prototype price.** It creates the intended low-resource distinction without turning Absetzen, Scambiar di Punta, or Schielhau into rare ultimate abilities. At starting Spiritus 8, C2 still puts at least one compound in 59.5%–82.9% of fresh duels across the matrix. At starting Spiritus 3, the difference becomes consequential: aggregate compound declarations fall by roughly one third to one half, Basic Parry and Counter recover, and C2 produces legal-but-unaffordable opportunities. C1, by contrast, leaves Schielhau near automatic at expert skill and makes resource state above 1 weakly relevant.

The result is not a promotion. P1, D1, S2, maximum Spiritus 8, and C2 remain **PREFERRED PROVISIONAL / TESTED**, while final compound cost, recovery, maximum, other Play prices, Guards, Power Strike, bind mechanics, engagement geometry, weapon profiles, tiers, and text remain **OPEN**.

## Scope, controls, and repository continuity

The experiment retained the repository's current P1 Basic Parry, D1 Durchwechseln declared before the Parry roll with no refund, S2 Schielhau–Durchwechseln resolution, Variant A one-roll compound chassis, normal action expenditure, intrinsic branches, public Spiritus, maximum 8, generic d6+1 damage, and the provisional three-learned-Play cap. It changed only the common price of Absetzen, Scambiar di Punta, and Schielhau from C1 to C2.

The previous Spiritus/Parry experiment is present in tracked repository form as a model, simulator, JSON result set, CSV summaries, and report. This run used a separate simulator and did not overwrite it. No governing-input conflict was found. Historical identities and evidence were not edited; no Play record or main design packet was changed.

Seed: `8212026`. Trials: `{'primary_per_cell': 12000, 'asymmetric_per_cell': 6000, 'sequences_per_cell': 8000}`. Primary cells: **24**; optional asymmetric cells: **8**; R0 sequence cells: **6**.

Power Strike competition remains unmodeled.

## Fresh-duel general results — every primary cell

`Win A` is the focal-side outright win rate; `Sym dev` is |A wins − B wins| / fights. Double defeat is reported separately.

| Skill / start / cost / info | Win A | Sym dev | Rounds | Double defeat | Spiritus spent/fight | End Spiritus | End 0 | End 1–2 | End 3–5 | End 6–8 | Unused at defeat |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 / 3 / C1 / Adaptive | 48.2% | 0.9% | 4.077 | 2.6% | 1.229 | 2.39 | 0.5% | 49.4% | 50.1% | 0.0% | 2.35 |
| 10 / 3 / C1 / Perfect | 49.0% | 1.1% | 4.092 | 3.2% | 1.087 | 2.46 | 0.5% | 44.3% | 55.2% | 0.0% | 2.45 |
| 10 / 3 / C2 / Adaptive | 48.7% | 1.5% | 4.229 | 4.0% | 1.064 | 2.47 | 0.4% | 30.3% | 69.3% | 0.0% | 2.45 |
| 10 / 3 / C2 / Perfect | 47.9% | 0.4% | 4.240 | 4.6% | 1.064 | 2.47 | 0.3% | 30.2% | 69.5% | 0.0% | 2.47 |
| 10 / 8 / C1 / Adaptive | 49.1% | 0.6% | 4.059 | 2.5% | 1.418 | 7.29 | 0.0% | 0.0% | 2.1% | 97.9% | 7.26 |
| 10 / 8 / C1 / Perfect | 48.9% | 0.6% | 4.076 | 2.8% | 1.241 | 7.38 | 0.0% | 0.0% | 1.5% | 98.5% | 7.38 |
| 10 / 8 / C2 / Adaptive | 48.9% | 0.5% | 4.120 | 2.8% | 2.030 | 6.99 | 0.0% | 0.4% | 9.2% | 90.4% | 6.94 |
| 10 / 8 / C2 / Perfect | 47.8% | 1.1% | 4.109 | 3.3% | 1.860 | 7.07 | 0.0% | 0.4% | 7.8% | 91.8% | 7.05 |
| 14 / 3 / C1 / Adaptive | 47.3% | 0.7% | 3.247 | 4.6% | 1.887 | 2.06 | 3.0% | 64.8% | 32.2% | 0.0% | 2.17 |
| 14 / 3 / C1 / Perfect | 45.6% | 0.5% | 2.993 | 9.3% | 1.353 | 2.32 | 1.6% | 50.7% | 47.7% | 0.0% | 2.43 |
| 14 / 3 / C2 / Adaptive | 45.8% | 1.2% | 3.341 | 7.1% | 1.933 | 2.03 | 3.4% | 53.7% | 42.9% | 0.0% | 2.15 |
| 14 / 3 / C2 / Perfect | 43.4% | 0.8% | 3.026 | 12.4% | 1.648 | 2.18 | 2.1% | 42.1% | 55.8% | 0.0% | 2.28 |
| 14 / 8 / C1 / Adaptive | 48.3% | 1.2% | 3.182 | 4.6% | 2.045 | 6.98 | 0.0% | 0.0% | 5.1% | 94.9% | 7.10 |
| 14 / 8 / C1 / Perfect | 44.8% | 0.7% | 2.944 | 9.6% | 1.405 | 7.30 | 0.0% | 0.0% | 2.1% | 97.9% | 7.39 |
| 14 / 8 / C2 / Adaptive | 47.5% | 0.1% | 3.214 | 5.1% | 3.015 | 6.49 | 0.0% | 1.1% | 19.8% | 79.1% | 6.70 |
| 14 / 8 / C2 / Perfect | 44.8% | 0.5% | 2.940 | 9.9% | 2.315 | 6.84 | 0.0% | 0.7% | 11.4% | 87.9% | 7.03 |
| 18 / 3 / C1 / Adaptive | 46.4% | 0.6% | 2.758 | 7.8% | 2.311 | 1.84 | 5.4% | 71.5% | 23.2% | 0.0% | 2.12 |
| 18 / 3 / C1 / Perfect | 41.5% | 0.3% | 2.544 | 16.8% | 1.491 | 2.25 | 2.0% | 54.3% | 43.7% | 0.0% | 2.47 |
| 18 / 3 / C2 / Adaptive | 43.4% | 2.4% | 2.872 | 10.8% | 2.508 | 1.75 | 11.2% | 57.9% | 30.9% | 0.0% | 2.04 |
| 18 / 3 / C2 / Perfect | 39.8% | 0.6% | 2.533 | 21.1% | 1.873 | 2.06 | 2.1% | 46.6% | 51.4% | 0.0% | 2.31 |
| 18 / 8 / C1 / Adaptive | 47.0% | 0.8% | 2.730 | 6.9% | 2.423 | 6.79 | 0.0% | 0.0% | 7.0% | 93.0% | 7.06 |
| 18 / 8 / C1 / Perfect | 42.3% | 1.5% | 2.521 | 17.0% | 1.534 | 7.23 | 0.0% | 0.0% | 2.6% | 97.4% | 7.46 |
| 18 / 8 / C2 / Adaptive | 46.3% | 0.5% | 2.766 | 7.8% | 3.699 | 6.15 | 0.0% | 1.7% | 29.0% | 69.2% | 6.61 |
| 18 / 8 / C2 / Perfect | 41.9% | 0.2% | 2.546 | 16.4% | 2.682 | 6.66 | 0.0% | 1.1% | 14.4% | 84.5% | 7.08 |

Mirrored symmetry deviations were 0.15%–2.39%; no directional outcome claim is made from them. C2 raises Spiritus expenditure while also increasing substitution toward Counter. At Skill 18 / start 3 / perfect information, that substitution raises double defeat from 16.8% under C1 to 21.1% under C2, reinforcing the already-OPEN elite mutual-lethality warning.

## Basic options and Durchwechseln — every primary cell

| Skill / start / cost / info | Basic Parry/fight | % def. opp. | After-known/fight | Counter/fight | Ignore/fight | D opp./fight | D declare/fight | D decline | D success | D damage/fight | D Spiritus/fight | Mean S declare | Mean S decline |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 / 3 / C1 / Adaptive | 0.470 | 23.1% | 0.029 | 0.438 | 0.019 | 0.714 | 0.261 | 63.4% | 35.0% | 0.411 | 0.261 | 2.82 | 2.73 |
| 10 / 3 / C1 / Perfect | 0.552 | 27.2% | 0.552 | 0.490 | 0.022 | 0.684 | 0.206 | 69.9% | 40.3% | 0.372 | 0.206 | 2.83 | 2.76 |
| 10 / 3 / C2 / Adaptive | 0.700 | 33.5% | 0.043 | 0.654 | 0.025 | 0.792 | 0.201 | 74.7% | 44.0% | 0.404 | 0.201 | 2.90 | 2.75 |
| 10 / 3 / C2 / Perfect | 0.772 | 37.1% | 0.772 | 0.683 | 0.029 | 0.822 | 0.183 | 77.7% | 46.8% | 0.389 | 0.183 | 2.94 | 2.74 |
| 10 / 8 / C1 / Adaptive | 0.434 | 21.6% | 0.031 | 0.386 | 0.017 | 0.715 | 0.346 | 51.6% | 35.4% | 0.544 | 0.346 | 7.74 | 7.73 |
| 10 / 8 / C1 / Perfect | 0.511 | 25.3% | 0.511 | 0.468 | 0.019 | 0.673 | 0.272 | 59.5% | 40.0% | 0.486 | 0.272 | 7.76 | 7.75 |
| 10 / 8 / C2 / Adaptive | 0.528 | 25.7% | 0.037 | 0.482 | 0.019 | 0.736 | 0.311 | 57.7% | 38.4% | 0.534 | 0.311 | 7.60 | 7.63 |
| 10 / 8 / C2 / Perfect | 0.584 | 28.7% | 0.584 | 0.534 | 0.020 | 0.703 | 0.263 | 62.6% | 41.0% | 0.494 | 0.263 | 7.65 | 7.66 |
| 14 / 3 / C1 / Adaptive | 0.437 | 19.3% | 0.033 | 0.459 | 0.006 | 0.858 | 0.647 | 24.7% | 54.1% | 1.569 | 0.647 | 2.69 | 2.51 |
| 14 / 3 / C1 / Perfect | 0.159 | 7.6% | 0.159 | 0.793 | 0.011 | 0.381 | 0.286 | 24.8% | 50.6% | 0.653 | 0.286 | 2.75 | 2.48 |
| 14 / 3 / C2 / Adaptive | 0.610 | 26.3% | 0.035 | 0.694 | 0.009 | 0.801 | 0.554 | 30.8% | 62.7% | 1.568 | 0.554 | 2.79 | 2.18 |
| 14 / 3 / C2 / Perfect | 0.229 | 10.9% | 0.229 | 0.984 | 0.013 | 0.342 | 0.222 | 35.2% | 59.3% | 0.596 | 0.222 | 2.70 | 1.79 |
| 14 / 8 / C1 / Adaptive | 0.391 | 17.6% | 0.018 | 0.437 | 0.006 | 0.858 | 0.725 | 15.5% | 52.7% | 1.725 | 0.725 | 7.66 | 7.68 |
| 14 / 8 / C1 / Perfect | 0.115 | 5.6% | 0.115 | 0.794 | 0.013 | 0.365 | 0.304 | 16.5% | 47.6% | 0.648 | 0.304 | 7.71 | 7.74 |
| 14 / 8 / C2 / Adaptive | 0.433 | 19.3% | 0.017 | 0.499 | 0.006 | 0.816 | 0.685 | 16.0% | 54.8% | 1.686 | 0.685 | 7.46 | 7.53 |
| 14 / 8 / C2 / Perfect | 0.128 | 6.2% | 0.128 | 0.827 | 0.012 | 0.337 | 0.282 | 16.4% | 51.2% | 0.656 | 0.282 | 7.53 | 7.64 |
| 18 / 3 / C1 / Adaptive | 0.407 | 16.4% | 0.006 | 0.546 | 0.003 | 1.018 | 0.886 | 12.9% | 67.7% | 2.694 | 0.886 | 2.65 | 2.39 |
| 18 / 3 / C1 / Perfect | 0.012 | 0.5% | 0.012 | 1.010 | 0.004 | 0.334 | 0.279 | 16.7% | 49.9% | 0.622 | 0.279 | 2.73 | 2.55 |
| 18 / 3 / C2 / Adaptive | 0.555 | 21.6% | 0.029 | 0.766 | 0.003 | 0.877 | 0.754 | 14.0% | 76.4% | 2.594 | 0.754 | 2.56 | 1.59 |
| 18 / 3 / C2 / Perfect | 0.022 | 1.0% | 0.022 | 1.219 | 0.006 | 0.195 | 0.155 | 20.5% | 54.0% | 0.373 | 0.155 | 2.68 | 1.83 |
| 18 / 8 / C1 / Adaptive | 0.376 | 15.3% | 0.002 | 0.533 | 0.002 | 1.033 | 0.941 | 8.9% | 64.1% | 2.711 | 0.941 | 7.61 | 7.65 |
| 18 / 8 / C1 / Perfect | 0.009 | 0.4% | 0.009 | 0.997 | 0.004 | 0.349 | 0.305 | 12.5% | 48.4% | 0.662 | 0.305 | 7.69 | 7.69 |
| 18 / 8 / C2 / Adaptive | 0.401 | 16.1% | 0.002 | 0.551 | 0.002 | 0.990 | 0.907 | 8.4% | 65.8% | 2.702 | 0.907 | 7.33 | 7.40 |
| 18 / 8 / C2 / Perfect | 0.011 | 0.5% | 0.011 | 1.012 | 0.004 | 0.322 | 0.286 | 10.9% | 48.5% | 0.631 | 0.286 | 7.47 | 7.62 |

D1 remains active under both prices and, because it is still affordable at exactly 1 Spiritus under C2, clearly occupies the cheaper tactical-conversion tier. Its use changes indirectly because the reserve is also valued for compounds; this is policy interaction, not a change to D1.

## Compound Plays total — every primary cell

| Skill / start / cost / info | Declarations/fight | Spiritus/fight | Damage/fight | Damage share | % defensive opp. | Fights 1+ | Fights 2+ | Fights 3+ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 / 3 / C1 / Adaptive | 0.968 | 0.968 | 1.961 | 14.5% | 47.6% | 68.5% | 24.5% | 3.5% |
| 10 / 3 / C1 / Perfect | 0.881 | 0.881 | 1.863 | 13.7% | 43.4% | 63.7% | 21.1% | 3.1% |
| 10 / 3 / C2 / Adaptive | 0.432 | 0.863 | 0.882 | 6.4% | 20.6% | 39.5% | 3.6% | 0.0% |
| 10 / 3 / C2 / Perfect | 0.441 | 0.881 | 0.943 | 6.8% | 21.2% | 39.9% | 4.1% | 0.0% |
| 10 / 8 / C1 / Adaptive | 1.072 | 1.072 | 2.196 | 16.3% | 53.3% | 71.7% | 28.8% | 6.0% |
| 10 / 8 / C1 / Perfect | 0.969 | 0.969 | 2.011 | 14.8% | 47.9% | 67.3% | 24.4% | 4.7% |
| 10 / 8 / C2 / Adaptive | 0.859 | 1.718 | 1.770 | 13.0% | 41.7% | 62.6% | 19.8% | 3.2% |
| 10 / 8 / C2 / Perfect | 0.799 | 1.597 | 1.688 | 12.4% | 39.3% | 59.5% | 17.6% | 2.6% |
| 14 / 3 / C1 / Adaptive | 1.240 | 1.240 | 3.312 | 24.1% | 54.8% | 79.2% | 35.6% | 8.5% |
| 14 / 3 / C1 / Perfect | 1.067 | 1.067 | 3.095 | 21.6% | 51.0% | 71.4% | 28.3% | 6.4% |
| 14 / 3 / C2 / Adaptive | 0.689 | 1.378 | 1.895 | 13.4% | 29.7% | 59.9% | 9.0% | 0.0% |
| 14 / 3 / C2 / Perfect | 0.713 | 1.426 | 2.098 | 14.2% | 33.9% | 61.2% | 10.1% | 0.0% |
| 14 / 8 / C1 / Adaptive | 1.320 | 1.320 | 3.504 | 25.6% | 59.3% | 81.0% | 39.2% | 10.3% |
| 14 / 8 / C1 / Perfect | 1.100 | 1.100 | 3.120 | 21.7% | 53.5% | 72.4% | 30.0% | 6.8% |
| 14 / 8 / C2 / Adaptive | 1.165 | 2.329 | 3.121 | 22.7% | 51.9% | 75.4% | 32.5% | 7.8% |
| 14 / 8 / C2 / Perfect | 1.017 | 2.034 | 2.919 | 20.3% | 49.4% | 69.3% | 26.4% | 5.4% |
| 18 / 3 / C1 / Adaptive | 1.425 | 1.425 | 4.675 | 33.3% | 57.2% | 85.1% | 43.8% | 12.1% |
| 18 / 3 / C1 / Perfect | 1.213 | 1.213 | 4.308 | 28.2% | 52.9% | 77.4% | 34.0% | 8.8% |
| 18 / 3 / C2 / Adaptive | 0.877 | 1.754 | 2.961 | 20.2% | 34.2% | 72.6% | 15.1% | 0.0% |
| 18 / 3 / C2 / Perfect | 0.859 | 1.718 | 3.155 | 19.9% | 37.8% | 71.5% | 14.4% | 0.0% |
| 18 / 8 / C1 / Adaptive | 1.482 | 1.482 | 4.837 | 34.5% | 60.3% | 85.9% | 46.1% | 14.0% |
| 18 / 8 / C1 / Perfect | 1.229 | 1.229 | 4.342 | 28.6% | 54.1% | 76.6% | 35.1% | 9.6% |
| 18 / 8 / C2 / Adaptive | 1.396 | 2.792 | 4.541 | 32.3% | 56.1% | 82.9% | 42.3% | 12.4% |
| 18 / 8 / C2 / Perfect | 1.198 | 2.395 | 4.286 | 28.1% | 52.3% | 76.5% | 33.1% | 9.0% |

At healthy reserves, C2 reduces rather than deletes compound fencing. The strongest C2 fresh cells still resolve 49.4%–56.1% of defensive opportunities with compounds at Skills 14–18 / start 8, and 69.3%–82.9% of those fights contain at least one compound. At start 3, C2 creates the intended substitution: aggregate compound declaration rates fall to 20.6%–37.8% of defensive opportunities while Basic Parry and Counter rise.

## Individual compound usage — every primary cell

| Cell | Play | Opp./fight | Decl./fight | Decl. rate | Success | Damage/fight | Damage share | Spiritus/fight | Mean S declare | Unaffordable/fight |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 / 3 / C1 / Adaptive | Absetzen | 0.581 | 0.242 | 41.7% | 50.0% | 0.537 | 4.0% | 0.242 | 2.78 | 0.000 |
| 10 / 3 / C1 / Adaptive | Scambiar di Punta | 0.581 | 0.245 | 42.2% | 50.4% | 0.558 | 4.1% | 0.245 | 2.77 | 0.000 |
| 10 / 3 / C1 / Adaptive | Schielhau | 0.794 | 0.481 | 60.5% | 50.7% | 0.867 | 6.4% | 0.481 | 2.82 | 0.000 |
| 10 / 3 / C1 / Perfect | Absetzen | 0.731 | 0.306 | 41.8% | 51.3% | 0.705 | 5.2% | 0.306 | 2.82 | 0.000 |
| 10 / 3 / C1 / Perfect | Scambiar di Punta | 0.731 | 0.309 | 42.3% | 50.2% | 0.690 | 5.1% | 0.309 | 2.81 | 0.000 |
| 10 / 3 / C1 / Perfect | Schielhau | 0.454 | 0.267 | 58.7% | 49.5% | 0.469 | 3.4% | 0.267 | 2.81 | 0.000 |
| 10 / 3 / C2 / Adaptive | Absetzen | 0.573 | 0.123 | 21.4% | 48.0% | 0.264 | 1.9% | 0.246 | 2.99 | 0.048 |
| 10 / 3 / C2 / Adaptive | Scambiar di Punta | 0.573 | 0.133 | 23.1% | 50.0% | 0.295 | 2.1% | 0.265 | 2.99 | 0.048 |
| 10 / 3 / C2 / Adaptive | Schielhau | 0.832 | 0.176 | 21.2% | 52.2% | 0.323 | 2.3% | 0.352 | 2.99 | 0.052 |
| 10 / 3 / C2 / Perfect | Absetzen | 0.743 | 0.168 | 22.6% | 49.7% | 0.379 | 2.7% | 0.337 | 2.99 | 0.059 |
| 10 / 3 / C2 / Perfect | Scambiar di Punta | 0.743 | 0.172 | 23.1% | 49.9% | 0.386 | 2.8% | 0.343 | 2.99 | 0.059 |
| 10 / 3 / C2 / Perfect | Schielhau | 0.470 | 0.101 | 21.4% | 49.8% | 0.177 | 1.3% | 0.201 | 3.00 | 0.035 |
| 10 / 8 / C1 / Adaptive | Absetzen | 0.579 | 0.258 | 44.6% | 50.4% | 0.588 | 4.4% | 0.258 | 7.69 | 0.000 |
| 10 / 8 / C1 / Adaptive | Scambiar di Punta | 0.579 | 0.262 | 45.2% | 50.5% | 0.596 | 4.4% | 0.262 | 7.72 | 0.000 |
| 10 / 8 / C1 / Adaptive | Schielhau | 0.768 | 0.552 | 71.8% | 51.0% | 1.013 | 7.5% | 0.552 | 7.75 | 0.000 |
| 10 / 8 / C1 / Perfect | Absetzen | 0.721 | 0.324 | 44.9% | 49.0% | 0.716 | 5.3% | 0.324 | 7.76 | 0.000 |
| 10 / 8 / C1 / Perfect | Scambiar di Punta | 0.721 | 0.325 | 45.1% | 49.5% | 0.727 | 5.4% | 0.325 | 7.77 | 0.000 |
| 10 / 8 / C1 / Perfect | Schielhau | 0.445 | 0.320 | 71.9% | 50.4% | 0.568 | 4.2% | 0.320 | 7.75 | 0.000 |
| 10 / 8 / C2 / Adaptive | Absetzen | 0.569 | 0.223 | 39.2% | 52.2% | 0.525 | 3.9% | 0.446 | 7.60 | 0.000 |
| 10 / 8 / C2 / Adaptive | Scambiar di Punta | 0.569 | 0.221 | 38.9% | 49.3% | 0.495 | 3.6% | 0.443 | 7.62 | 0.000 |
| 10 / 8 / C2 / Adaptive | Schielhau | 0.807 | 0.415 | 51.4% | 50.0% | 0.750 | 5.5% | 0.829 | 7.69 | 0.000 |
| 10 / 8 / C2 / Perfect | Absetzen | 0.728 | 0.285 | 39.2% | 49.1% | 0.622 | 4.6% | 0.571 | 7.64 | 0.000 |
| 10 / 8 / C2 / Perfect | Scambiar di Punta | 0.728 | 0.282 | 38.8% | 50.0% | 0.633 | 4.6% | 0.565 | 7.66 | 0.000 |
| 10 / 8 / C2 / Perfect | Schielhau | 0.449 | 0.231 | 51.4% | 51.2% | 0.433 | 3.2% | 0.462 | 7.65 | 0.000 |
| 14 / 3 / C1 / Adaptive | Absetzen | 0.682 | 0.316 | 46.4% | 70.2% | 0.990 | 7.2% | 0.316 | 2.62 | 0.003 |
| 14 / 3 / C1 / Adaptive | Scambiar di Punta | 0.682 | 0.318 | 46.7% | 69.7% | 1.000 | 7.3% | 0.318 | 2.64 | 0.003 |
| 14 / 3 / C1 / Adaptive | Schielhau | 0.794 | 0.606 | 76.3% | 69.6% | 1.323 | 9.6% | 0.606 | 2.74 | 0.002 |
| 14 / 3 / C1 / Perfect | Absetzen | 0.787 | 0.380 | 48.3% | 69.4% | 1.188 | 8.3% | 0.380 | 2.75 | 0.002 |
| 14 / 3 / C1 / Perfect | Scambiar di Punta | 0.787 | 0.375 | 47.7% | 71.4% | 1.198 | 8.3% | 0.375 | 2.74 | 0.002 |
| 14 / 3 / C1 / Perfect | Schielhau | 0.399 | 0.312 | 78.2% | 71.2% | 0.708 | 4.9% | 0.312 | 2.76 | 0.001 |
| 14 / 3 / C2 / Adaptive | Absetzen | 0.693 | 0.206 | 29.8% | 68.8% | 0.637 | 4.5% | 0.413 | 2.96 | 0.108 |
| 14 / 3 / C2 / Adaptive | Scambiar di Punta | 0.693 | 0.205 | 29.6% | 69.7% | 0.648 | 4.6% | 0.410 | 2.95 | 0.108 |
| 14 / 3 / C2 / Adaptive | Schielhau | 0.833 | 0.278 | 33.3% | 69.0% | 0.611 | 4.3% | 0.555 | 2.97 | 0.099 |
| 14 / 3 / C2 / Perfect | Absetzen | 0.777 | 0.280 | 36.0% | 70.1% | 0.894 | 6.1% | 0.560 | 2.98 | 0.111 |
| 14 / 3 / C2 / Perfect | Scambiar di Punta | 0.777 | 0.272 | 35.0% | 69.8% | 0.851 | 5.8% | 0.545 | 2.98 | 0.111 |
| 14 / 3 / C2 / Perfect | Schielhau | 0.407 | 0.161 | 39.5% | 70.5% | 0.352 | 2.4% | 0.321 | 2.99 | 0.059 |
| 14 / 8 / C1 / Adaptive | Absetzen | 0.675 | 0.324 | 47.9% | 70.0% | 1.011 | 7.4% | 0.324 | 7.56 | 0.000 |
| 14 / 8 / C1 / Adaptive | Scambiar di Punta | 0.675 | 0.331 | 49.1% | 70.5% | 1.055 | 7.7% | 0.331 | 7.58 | 0.000 |
| 14 / 8 / C1 / Adaptive | Schielhau | 0.780 | 0.665 | 85.2% | 70.3% | 1.438 | 10.5% | 0.665 | 7.65 | 0.000 |
| 14 / 8 / C1 / Perfect | Absetzen | 0.758 | 0.369 | 48.7% | 69.8% | 1.169 | 8.1% | 0.369 | 7.73 | 0.000 |
| 14 / 8 / C1 / Perfect | Scambiar di Punta | 0.758 | 0.373 | 49.2% | 70.1% | 1.173 | 8.2% | 0.373 | 7.73 | 0.000 |
| 14 / 8 / C1 / Perfect | Schielhau | 0.406 | 0.357 | 88.0% | 70.0% | 0.778 | 5.4% | 0.357 | 7.73 | 0.000 |
| 14 / 8 / C2 / Adaptive | Absetzen | 0.669 | 0.306 | 45.7% | 70.4% | 0.963 | 7.0% | 0.612 | 7.39 | 0.000 |
| 14 / 8 / C2 / Adaptive | Scambiar di Punta | 0.669 | 0.309 | 46.2% | 70.7% | 0.982 | 7.1% | 0.618 | 7.39 | 0.000 |
| 14 / 8 / C2 / Adaptive | Schielhau | 0.778 | 0.550 | 70.7% | 69.5% | 1.176 | 8.6% | 1.100 | 7.50 | 0.000 |
| 14 / 8 / C2 / Perfect | Absetzen | 0.755 | 0.360 | 47.7% | 71.2% | 1.160 | 8.1% | 0.721 | 7.59 | 0.000 |
| 14 / 8 / C2 / Perfect | Scambiar di Punta | 0.755 | 0.359 | 47.6% | 69.5% | 1.122 | 7.8% | 0.718 | 7.55 | 0.000 |
| 14 / 8 / C2 / Perfect | Schielhau | 0.401 | 0.297 | 74.2% | 70.3% | 0.637 | 4.4% | 0.595 | 7.59 | 0.000 |
| 18 / 3 / C1 / Adaptive | Absetzen | 0.769 | 0.373 | 48.5% | 90.1% | 1.510 | 10.7% | 0.373 | 2.54 | 0.006 |
| 18 / 3 / C1 / Adaptive | Scambiar di Punta | 0.769 | 0.374 | 48.7% | 90.8% | 1.545 | 11.0% | 0.374 | 2.56 | 0.006 |
| 18 / 3 / C1 / Adaptive | Schielhau | 0.818 | 0.678 | 82.8% | 90.1% | 1.620 | 11.5% | 0.678 | 2.65 | 0.004 |
| 18 / 3 / C1 / Perfect | Absetzen | 0.865 | 0.429 | 49.6% | 90.1% | 1.742 | 11.4% | 0.429 | 2.72 | 0.002 |
| 18 / 3 / C1 / Perfect | Scambiar di Punta | 0.865 | 0.425 | 49.2% | 89.4% | 1.701 | 11.1% | 0.425 | 2.72 | 0.002 |
| 18 / 3 / C1 / Perfect | Schielhau | 0.422 | 0.359 | 85.0% | 89.9% | 0.865 | 5.7% | 0.359 | 2.74 | 0.001 |
| 18 / 3 / C2 / Adaptive | Absetzen | 0.789 | 0.259 | 32.8% | 89.2% | 1.042 | 7.1% | 0.517 | 2.90 | 0.170 |
| 18 / 3 / C2 / Adaptive | Scambiar di Punta | 0.789 | 0.263 | 33.4% | 89.8% | 1.072 | 7.3% | 0.526 | 2.91 | 0.170 |
| 18 / 3 / C2 / Adaptive | Schielhau | 0.868 | 0.355 | 40.9% | 90.8% | 0.847 | 5.8% | 0.710 | 2.95 | 0.143 |
| 18 / 3 / C2 / Perfect | Absetzen | 0.858 | 0.326 | 38.1% | 89.6% | 1.320 | 8.3% | 0.653 | 2.98 | 0.153 |
| 18 / 3 / C2 / Perfect | Scambiar di Punta | 0.858 | 0.339 | 39.5% | 90.2% | 1.375 | 8.7% | 0.678 | 2.98 | 0.153 |
| 18 / 3 / C2 / Perfect | Schielhau | 0.408 | 0.193 | 47.4% | 89.4% | 0.460 | 2.9% | 0.387 | 2.99 | 0.075 |
| 18 / 8 / C1 / Adaptive | Absetzen | 0.763 | 0.376 | 49.3% | 90.1% | 1.533 | 10.9% | 0.376 | 7.51 | 0.000 |
| 18 / 8 / C1 / Adaptive | Scambiar di Punta | 0.763 | 0.378 | 49.6% | 90.3% | 1.556 | 11.1% | 0.378 | 7.51 | 0.000 |
| 18 / 8 / C1 / Adaptive | Schielhau | 0.808 | 0.728 | 90.1% | 90.2% | 1.748 | 12.5% | 0.728 | 7.59 | 0.000 |
| 18 / 8 / C1 / Perfect | Absetzen | 0.855 | 0.430 | 50.3% | 90.3% | 1.742 | 11.5% | 0.430 | 7.71 | 0.000 |
| 18 / 8 / C1 / Perfect | Scambiar di Punta | 0.855 | 0.420 | 49.2% | 90.0% | 1.694 | 11.1% | 0.420 | 7.71 | 0.000 |
| 18 / 8 / C1 / Perfect | Schielhau | 0.413 | 0.379 | 91.6% | 89.6% | 0.907 | 6.0% | 0.379 | 7.69 | 0.000 |
| 18 / 8 / C2 / Adaptive | Absetzen | 0.763 | 0.377 | 49.3% | 89.7% | 1.512 | 10.8% | 0.753 | 7.24 | 0.000 |
| 18 / 8 / C2 / Adaptive | Scambiar di Punta | 0.763 | 0.368 | 48.2% | 89.7% | 1.479 | 10.5% | 0.736 | 7.24 | 0.000 |
| 18 / 8 / C2 / Adaptive | Schielhau | 0.825 | 0.652 | 79.0% | 90.3% | 1.550 | 11.0% | 1.303 | 7.40 | 0.000 |
| 18 / 8 / C2 / Perfect | Absetzen | 0.869 | 0.433 | 49.8% | 89.9% | 1.746 | 11.4% | 0.866 | 7.50 | 0.000 |
| 18 / 8 / C2 / Perfect | Scambiar di Punta | 0.869 | 0.423 | 48.7% | 89.4% | 1.711 | 11.2% | 0.846 | 7.49 | 0.000 |
| 18 / 8 / C2 / Perfect | Schielhau | 0.418 | 0.342 | 81.7% | 90.9% | 0.829 | 5.4% | 0.683 | 7.50 | 0.000 |

| Cell | Play | Use S 6–8 | Use S 3–5 | Use S 2 | Use S 1 | Use S 0 | Parry displaced/fight | Counter displaced/fight | Early use | Late use |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 / 3 / C1 / Adaptive | Absetzen | 0.0% | 42.7% | 41.2% | 16.9% | 0.0% | 0.099 | 0.143 | 41.6% | 41.8% |
| 10 / 3 / C1 / Adaptive | Scambiar di Punta | 0.0% | 42.7% | 43.1% | 19.8% | 0.0% | 0.102 | 0.143 | 41.2% | 43.2% |
| 10 / 3 / C1 / Adaptive | Schielhau | 0.0% | 61.3% | 61.1% | 19.3% | 0.0% | 0.049 | 0.132 | 57.5% | 63.1% |
| 10 / 3 / C1 / Perfect | Absetzen | 0.0% | 42.4% | 41.4% | 18.1% | 0.0% | 0.128 | 0.178 | 41.4% | 42.1% |
| 10 / 3 / C1 / Perfect | Scambiar di Punta | 0.0% | 42.7% | 42.6% | 22.8% | 0.0% | 0.128 | 0.181 | 41.0% | 43.6% |
| 10 / 3 / C1 / Perfect | Schielhau | 0.0% | 59.7% | 58.9% | 19.1% | 0.0% | 0.026 | 0.074 | 55.4% | 61.1% |
| 10 / 3 / C2 / Adaptive | Absetzen | 0.0% | 24.3% | 4.6% | 0.0% | 0.0% | 0.055 | 0.068 | 20.4% | 22.5% |
| 10 / 3 / C2 / Adaptive | Scambiar di Punta | 0.0% | 26.1% | 7.7% | 0.0% | 0.0% | 0.058 | 0.074 | 22.6% | 23.7% |
| 10 / 3 / C2 / Adaptive | Schielhau | 0.0% | 23.7% | 2.5% | 0.0% | 0.0% | 0.025 | 0.045 | 18.1% | 23.6% |
| 10 / 3 / C2 / Perfect | Absetzen | 0.0% | 25.6% | 4.5% | 0.0% | 0.0% | 0.073 | 0.095 | 22.3% | 23.0% |
| 10 / 3 / C2 / Perfect | Scambiar di Punta | 0.0% | 26.0% | 6.7% | 0.0% | 0.0% | 0.077 | 0.095 | 21.9% | 24.2% |
| 10 / 3 / C2 / Perfect | Schielhau | 0.0% | 24.2% | 1.6% | 0.0% | 0.0% | 0.014 | 0.029 | 18.4% | 23.4% |
| 10 / 8 / C1 / Adaptive | Absetzen | 44.6% | 47.4% | 0.0% | 0.0% | 0.0% | 0.107 | 0.151 | 43.2% | 46.2% |
| 10 / 8 / C1 / Adaptive | Scambiar di Punta | 45.2% | 47.4% | 0.0% | 0.0% | 0.0% | 0.106 | 0.155 | 44.5% | 46.0% |
| 10 / 8 / C1 / Adaptive | Schielhau | 71.8% | 76.9% | 0.0% | 0.0% | 0.0% | 0.056 | 0.150 | 67.7% | 75.5% |
| 10 / 8 / C1 / Perfect | Absetzen | 44.8% | 75.0% | 0.0% | 0.0% | 0.0% | 0.130 | 0.194 | 43.7% | 46.1% |
| 10 / 8 / C1 / Perfect | Scambiar di Punta | 45.1% | 25.0% | 0.0% | 0.0% | 0.0% | 0.132 | 0.194 | 43.9% | 46.4% |
| 10 / 8 / C1 / Perfect | Schielhau | 71.9% | 85.7% | 100.0% | 0.0% | 0.0% | 0.028 | 0.088 | 68.4% | 74.6% |
| 10 / 8 / C2 / Adaptive | Absetzen | 39.1% | 44.4% | 0.0% | 0.0% | 0.0% | 0.094 | 0.130 | 36.9% | 41.6% |
| 10 / 8 / C2 / Adaptive | Scambiar di Punta | 39.1% | 31.8% | 0.0% | 0.0% | 0.0% | 0.093 | 0.128 | 36.6% | 41.2% |
| 10 / 8 / C2 / Adaptive | Schielhau | 51.5% | 42.1% | 0.0% | 0.0% | 0.0% | 0.047 | 0.115 | 45.6% | 56.3% |
| 10 / 8 / C2 / Perfect | Absetzen | 39.3% | 37.1% | 0.0% | 0.0% | 0.0% | 0.124 | 0.161 | 36.8% | 41.7% |
| 10 / 8 / C2 / Perfect | Scambiar di Punta | 38.9% | 33.1% | 33.3% | 0.0% | 0.0% | 0.118 | 0.164 | 38.1% | 39.5% |
| 10 / 8 / C2 / Perfect | Schielhau | 51.5% | 46.0% | 0.0% | 0.0% | 0.0% | 0.024 | 0.063 | 45.5% | 55.7% |
| 14 / 3 / C1 / Adaptive | Absetzen | 0.0% | 46.5% | 48.0% | 40.5% | 0.0% | 0.104 | 0.211 | 46.3% | 46.4% |
| 14 / 3 / C1 / Adaptive | Scambiar di Punta | 0.0% | 47.7% | 47.6% | 35.0% | 0.0% | 0.103 | 0.216 | 47.1% | 46.0% |
| 14 / 3 / C1 / Adaptive | Schielhau | 0.0% | 78.3% | 77.6% | 34.4% | 0.0% | 0.053 | 0.113 | 76.0% | 76.7% |
| 14 / 3 / C1 / Perfect | Absetzen | 0.0% | 48.8% | 47.9% | 40.0% | 0.0% | 0.004 | 0.376 | 48.6% | 47.6% |
| 14 / 3 / C1 / Perfect | Scambiar di Punta | 0.0% | 47.6% | 49.1% | 43.9% | 0.0% | 0.004 | 0.371 | 47.3% | 48.4% |
| 14 / 3 / C1 / Perfect | Schielhau | 0.0% | 79.8% | 78.7% | 34.8% | 0.0% | 0.001 | 0.085 | 77.7% | 79.0% |
| 14 / 3 / C2 / Adaptive | Absetzen | 0.0% | 38.1% | 13.0% | 0.0% | 0.0% | 0.066 | 0.141 | 32.4% | 25.8% |
| 14 / 3 / C2 / Adaptive | Scambiar di Punta | 0.0% | 37.7% | 14.9% | 0.0% | 0.0% | 0.067 | 0.139 | 32.5% | 25.1% |
| 14 / 3 / C2 / Adaptive | Schielhau | 0.0% | 41.9% | 8.7% | 0.0% | 0.0% | 0.034 | 0.063 | 34.5% | 31.6% |
| 14 / 3 / C2 / Perfect | Absetzen | 0.0% | 42.9% | 22.8% | 0.0% | 0.0% | 0.018 | 0.262 | 38.6% | 30.7% |
| 14 / 3 / C2 / Perfect | Scambiar di Punta | 0.0% | 42.0% | 15.4% | 0.0% | 0.0% | 0.019 | 0.254 | 38.1% | 28.8% |
| 14 / 3 / C2 / Perfect | Schielhau | 0.0% | 47.9% | 12.8% | 0.0% | 0.0% | 0.003 | 0.054 | 40.6% | 37.5% |
| 14 / 8 / C1 / Adaptive | Absetzen | 48.0% | 47.5% | 0.0% | 0.0% | 0.0% | 0.095 | 0.229 | 47.1% | 49.3% |
| 14 / 8 / C1 / Adaptive | Scambiar di Punta | 49.1% | 52.5% | 0.0% | 0.0% | 0.0% | 0.097 | 0.235 | 49.3% | 48.8% |
| 14 / 8 / C1 / Adaptive | Schielhau | 85.2% | 95.7% | 0.0% | 0.0% | 0.0% | 0.053 | 0.122 | 83.0% | 89.1% |
| 14 / 8 / C1 / Perfect | Absetzen | 48.7% | 55.6% | 0.0% | 0.0% | 0.0% | 0.000 | 0.369 | 48.6% | 49.1% |
| 14 / 8 / C1 / Perfect | Scambiar di Punta | 49.3% | 44.4% | 0.0% | 0.0% | 0.0% | 0.000 | 0.373 | 48.9% | 50.0% |
| 14 / 8 / C1 / Perfect | Schielhau | 87.9% | 100.0% | 0.0% | 0.0% | 0.0% | 0.000 | 0.085 | 86.0% | 91.8% |
| 14 / 8 / C2 / Adaptive | Absetzen | 45.7% | 45.2% | 25.0% | 0.0% | 0.0% | 0.091 | 0.215 | 44.9% | 46.9% |
| 14 / 8 / C2 / Adaptive | Scambiar di Punta | 46.2% | 45.7% | 0.0% | 0.0% | 0.0% | 0.093 | 0.216 | 45.5% | 47.3% |
| 14 / 8 / C2 / Adaptive | Schielhau | 70.5% | 76.3% | 0.0% | 0.0% | 0.0% | 0.048 | 0.106 | 67.2% | 76.5% |
| 14 / 8 / C2 / Perfect | Absetzen | 47.8% | 43.5% | 25.0% | 0.0% | 0.0% | 0.000 | 0.360 | 47.9% | 47.2% |
| 14 / 8 / C2 / Perfect | Scambiar di Punta | 47.5% | 51.0% | 50.0% | 0.0% | 0.0% | 0.000 | 0.359 | 46.7% | 49.6% |
| 14 / 8 / C2 / Perfect | Schielhau | 74.4% | 68.7% | 0.0% | 0.0% | 0.0% | 0.000 | 0.086 | 72.0% | 78.6% |
| 18 / 3 / C1 / Adaptive | Absetzen | 0.0% | 48.4% | 50.3% | 47.0% | 0.0% | 0.099 | 0.274 | 48.6% | 48.1% |
| 18 / 3 / C1 / Adaptive | Scambiar di Punta | 0.0% | 50.0% | 48.2% | 44.8% | 0.0% | 0.099 | 0.276 | 49.5% | 46.5% |
| 18 / 3 / C1 / Adaptive | Schielhau | 0.0% | 84.5% | 86.3% | 50.9% | 0.0% | 0.054 | 0.142 | 83.7% | 80.4% |
| 18 / 3 / C1 / Perfect | Absetzen | 0.0% | 49.9% | 49.7% | 45.9% | 0.0% | 0.001 | 0.428 | 50.1% | 47.7% |
| 18 / 3 / C1 / Perfect | Scambiar di Punta | 0.0% | 49.2% | 49.7% | 47.6% | 0.0% | 0.001 | 0.424 | 49.0% | 49.5% |
| 18 / 3 / C1 / Perfect | Schielhau | 0.0% | 86.9% | 86.1% | 45.2% | 0.0% | 0.000 | 0.102 | 85.7% | 82.3% |
| 18 / 3 / C2 / Adaptive | Absetzen | 0.0% | 44.4% | 27.8% | 0.0% | 0.0% | 0.073 | 0.185 | 37.6% | 21.8% |
| 18 / 3 / C2 / Adaptive | Scambiar di Punta | 0.0% | 45.7% | 25.6% | 0.0% | 0.0% | 0.076 | 0.188 | 38.4% | 22.0% |
| 18 / 3 / C2 / Adaptive | Schielhau | 0.0% | 54.8% | 16.7% | 0.0% | 0.0% | 0.042 | 0.099 | 45.9% | 28.8% |
| 18 / 3 / C2 / Perfect | Absetzen | 0.0% | 46.8% | 30.6% | 0.0% | 0.0% | 0.000 | 0.326 | 41.4% | 24.9% |
| 18 / 3 / C2 / Perfect | Scambiar di Punta | 0.0% | 48.4% | 38.0% | 0.0% | 0.0% | 0.000 | 0.339 | 43.2% | 25.1% |
| 18 / 3 / C2 / Perfect | Schielhau | 0.0% | 59.3% | 21.2% | 0.0% | 0.0% | 0.000 | 0.074 | 51.2% | 34.0% |
| 18 / 8 / C1 / Adaptive | Absetzen | 49.3% | 58.1% | 0.0% | 0.0% | 0.0% | 0.095 | 0.281 | 49.6% | 48.6% |
| 18 / 8 / C1 / Adaptive | Scambiar di Punta | 49.6% | 41.9% | 0.0% | 0.0% | 0.0% | 0.101 | 0.277 | 49.0% | 51.2% |
| 18 / 8 / C1 / Adaptive | Schielhau | 90.1% | 94.3% | 0.0% | 0.0% | 0.0% | 0.050 | 0.144 | 89.1% | 93.2% |
| 18 / 8 / C1 / Perfect | Absetzen | 50.3% | 65.2% | 0.0% | 0.0% | 0.0% | 0.000 | 0.430 | 50.1% | 51.1% |
| 18 / 8 / C1 / Perfect | Scambiar di Punta | 49.2% | 34.8% | 0.0% | 0.0% | 0.0% | 0.000 | 0.420 | 49.3% | 48.7% |
| 18 / 8 / C1 / Perfect | Schielhau | 91.6% | 100.0% | 0.0% | 0.0% | 0.0% | 0.000 | 0.098 | 90.7% | 95.2% |
| 18 / 8 / C2 / Adaptive | Absetzen | 49.2% | 51.3% | 22.2% | 0.0% | 0.0% | 0.099 | 0.278 | 49.1% | 50.0% |
| 18 / 8 / C2 / Adaptive | Scambiar di Punta | 48.3% | 47.6% | 33.3% | 0.0% | 0.0% | 0.097 | 0.271 | 48.0% | 48.7% |
| 18 / 8 / C2 / Adaptive | Schielhau | 79.0% | 81.8% | 9.1% | 0.0% | 0.0% | 0.056 | 0.137 | 77.2% | 84.4% |
| 18 / 8 / C2 / Perfect | Absetzen | 49.9% | 46.9% | 30.8% | 0.0% | 0.0% | 0.000 | 0.433 | 50.2% | 48.5% |
| 18 / 8 / C2 / Perfect | Scambiar di Punta | 48.6% | 50.5% | 46.2% | 0.0% | 0.0% | 0.000 | 0.423 | 48.2% | 50.6% |
| 18 / 8 / C2 / Perfect | Schielhau | 81.7% | 80.8% | 33.3% | 0.0% | 0.0% | 0.000 | 0.102 | 79.8% | 88.5% |

Sparse bands should not be over-read: start-8 fights rarely reach Spiritus 2 or 1. The standardized policy surface and three-fight sequences below provide the controlled threshold comparison.

## Opportunity value and utility classifications

For every legal compound opportunity the simulator recorded the current policy value of Basic Parry, Counter, the relevant paid compound, and the same compound without its Spiritus charge. It also classified every non-selection by utility reason. The full per-cell sums, denominators, and counts are in `results.json`; the weighted primary-matrix summary is:

| Cost | Play | Mean Basic value | Mean Counter value | Mean compound value | Mean no-cost compound | Conservation | Insufficient | Basic better | Counter better | Tactical/HP | Exploration |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| C1 | Absetzen | 0.567 | 0.830 | 1.475 | 1.694 | 0.6% | 0.3% | 0.0% | 0.0% | 0.2% | 98.9% |
| C1 | Scambiar di Punta | 0.567 | 0.830 | 1.475 | 1.694 | 0.6% | 0.3% | 0.0% | 0.0% | 0.2% | 98.9% |
| C1 | Schielhau | 0.650 | 0.810 | 1.432 | 1.649 | 1.5% | 0.5% | 0.0% | 0.0% | 57.8% | 40.2% |
| C2 | Absetzen | 0.576 | 0.831 | 1.213 | 1.693 | 17.1% | 12.0% | 0.0% | 0.0% | 0.2% | 70.7% |
| C2 | Scambiar di Punta | 0.576 | 0.831 | 1.213 | 1.693 | 17.0% | 11.9% | 0.0% | 0.0% | 0.2% | 70.8% |
| C2 | Schielhau | 0.660 | 0.809 | 1.167 | 1.649 | 26.3% | 12.4% | 0.0% | 0.0% | 38.8% | 22.5% |

The zero Basic/Counter-better columns are a revealing limitation of this utility model: the unpriced two-effect chassis always has higher one-step expected value than either basic option. C2 creates meaningful choices through resource charge and unaffordability, not because the modeled immediate compound effect becomes intrinsically worse. `Other policy exploration` is dominated by seeded softmax mixing and, for the thrust, competition between mechanically identical Absetzen and Scambiar options. `Tactical/HP urgency` is mainly free Zornhau-Ort competing with Schielhau on committed cuts.

## Spiritus shadow price and same-state thresholds

The standardized surface holds both fighters at full HP, uses perfect information, and varies only the compound user's Spiritus. Absetzen and Scambiar have identical modeled utilities; Schielhau has one compound option rather than two competing thrust options.

| Skill | Play | Cost | S8 select | S5 select | S3 select | S2 select | S1 select |
|---:|---|---:|---:|---:|---:|---:|---:|
| 10 | Absetzen | C1 | 43.4% | 41.8% | 38.7% | 34.2% | 5.9% |
| 10 | Absetzen | C2 | 36.0% | 29.3% | 16.1% | 0.9% | 0.0% |
| 10 | Schielhau | C1 | 62.4% | 56.2% | 46.5% | 35.5% | 3.3% |
| 10 | Schielhau | C2 | 39.4% | 26.4% | 10.8% | 0.5% | 0.0% |
| 14 | Absetzen | C1 | 48.6% | 48.2% | 47.4% | 46.0% | 20.6% |
| 14 | Absetzen | C2 | 46.5% | 44.1% | 35.8% | 4.4% | 0.0% |
| 14 | Schielhau | C1 | 80.1% | 75.7% | 67.9% | 57.2% | 7.6% |
| 14 | Schielhau | C2 | 61.2% | 46.5% | 22.7% | 1.1% | 0.0% |
| 18 | Absetzen | C1 | 49.6% | 49.5% | 49.2% | 48.8% | 35.6% |
| 18 | Absetzen | C2 | 49.0% | 48.2% | 44.9% | 12.8% | 0.0% |
| 18 | Schielhau | C1 | 85.5% | 82.1% | 75.6% | 66.2% | 10.7% |
| 18 | Schielhau | C2 | 69.9% | 56.1% | 30.1% | 1.6% | 0.0% |

| Cost | Comparison | Mean selection-probability change from +1 Spiritus | Mean compound-utility change | Reading |
|---:|---|---:|---:|---|
| C1 | 8 vs 7 | 0.5% | 0.012 | marginal reserve value |
| C1 | 5 vs 4 | 1.3% | 0.027 | marginal reserve value |
| C1 | 3 vs 2 | 4.9% | 0.083 | marginal reserve value |
| C1 | 2 vs 1 | 30.1% | 0.503 | marginal reserve value |
| C2 | 8 vs 7 | 1.6% | 0.026 | marginal reserve value |
| C2 | 5 vs 4 | 4.7% | 0.070 | marginal reserve value |
| C2 | 3 vs 2 | 24.2% | 0.585 | marginal reserve value |
| C2 | 2 vs 1 | 4.4% | threshold / unavailable | C2 unavailable at the lower state; D1 remains available |

C1 has weak high-reserve differentiation and a large 2→1 conservation effect, but the compound remains legal at 1. C2 creates earlier conservation (especially 3→2) and the categorical 2→1 availability break. A Skill-10 Absetzen opportunity, for example, falls from 36.0% selection at Spiritus 8 to 16.1% at 3, 0.9% at 2, and unavailable at 1. At Skill 14 the same C2 probabilities are 46.5%, 36.5%, 19.1%, and 0%. This is the intended “worth it now?” decision rather than a flat upgrade.

### Emergent 0 / 1 / 2 hierarchy

- At 0 Spiritus, neither D1 nor C2 compounds are affordable: only basic/free fencing remains.
- At 1 Spiritus, D1 remains affordable and C2 compounds are unavailable.
- At 2 Spiritus, C2 compounds become legal but consume the entire reserve; policy selection is sharply conservative rather than automatic.
- At 3+ Spiritus, compounds become credible threats, with use rising strongly by Skill and urgency.

A fighter at 1 therefore behaves meaningfully differently from one at 2 in option availability, though the one-step policy often conserves even at 2. This is useful differentiation, not proof that the exact reserve utility is calibrated.

## Skill-18 Basic Parry and defensive progression

The table below uses only defensive opportunities after Durchwechseln is known in the Skill-18, start-3, C2 cells, where depletion is actually observed.

| Information | Spiritus | Opportunities | Basic Parry | Counter | Compound | Zornhau-Ort | Ignore |
|---|---:|---:|---:|---:|---:|---:|---:|
| Adaptive | 3 | 1852 | 3.7% | 33.3% | 49.8% | 12.8% | 0.3% |
| Adaptive | 2 | 425 | 14.1% | 32.9% | 30.1% | 22.4% | 0.5% |
| Adaptive | 1 | 2011 | 8.7% | 74.7% | 0.0% | 16.4% | 0.2% |
| Adaptive | 0 | 222 | 19.4% | 69.4% | 0.0% | 10.8% | 0.5% |
| Perfect | 3 | 21629 | 0.7% | 46.1% | 46.7% | 6.2% | 0.3% |
| Perfect | 2 | 712 | 0.7% | 58.3% | 28.5% | 12.4% | 0.1% |
| Perfect | 1 | 4818 | 2.1% | 85.9% | 0.0% | 11.9% | 0.2% |
| Perfect | 0 | 135 | 5.2% | 79.3% | 0.0% | 15.6% | 0.0% |

This is **intended expertise progression with a retained warning**, not compound-driven pathological deletion. Compounds dominate much of the healthy-reserve expert mix and vanish at 1; Counter then becomes the main substitute. Basic Parry recovers from 3.7% at Spiritus 3 to 14.1% at 2 in the adaptive cell and reaches 19.4% at 0, but it remains only 2.1% at Spiritus 1 under perfect information because D1 still specifically threatens P1. That reproduces the earlier high-skill finding rather than fixing or worsening it through compound price. Basic Parry is not mechanically deleted by C2, but known D1 and high-value Counter continue to suppress it.

## Optional asymmetric Skill check

These perfect-information start-8 cells are response checks, not a second full matrix. Because both fighters know the same repertoire, declarations by side also reflect how often that side must defend, not only preference.

| Skill A/B | Cost | A win-equivalent | A compound/fight | B compound/fight | A D/fight | B D/fight |
|---|---:|---:|---:|---:|---:|---:|
| 10/14 | C1 | 30.9% | 0.576 | 0.441 | 0.163 | 0.188 |
| 10/14 | C2 | 30.9% | 0.499 | 0.399 | 0.150 | 0.197 |
| 14/10 | C1 | 70.1% | 0.430 | 0.579 | 0.190 | 0.158 |
| 14/10 | C2 | 69.1% | 0.423 | 0.488 | 0.177 | 0.161 |
| 14/18 | C1 | 34.5% | 0.631 | 0.498 | 0.138 | 0.127 |
| 14/18 | C2 | 36.0% | 0.602 | 0.467 | 0.121 | 0.115 |
| 18/14 | C1 | 63.8% | 0.491 | 0.655 | 0.135 | 0.129 |
| 18/14 | C2 | 64.2% | 0.473 | 0.614 | 0.115 | 0.127 |

C2 changes win-equivalent by at most 1.5 percentage points in these 6,000-trial cells and reduces compound use on both sides. No strong evidence appears that C2 uniquely fails when the user is more or less skilled; the weaker side often records more compound declarations because it faces more successful attacks.

## Three-fight R0 attrition

Focal HP, action/state, and knowledge reset each fight; every opponent is fresh at Spiritus 8; only focal Spiritus carries. All three fights run regardless of earlier outcomes.

| Skill / cost | Enter F1/F2/F3 | Leave F1/F2/F3 | Focal spend F1/F2/F3 | D F1/F2/F3 | Compound F1/F2/F3 | Basic Parry F1/F2/F3 | Counter F1/F2/F3 | Unaffordable compounds F1/F2/F3 | Advanced Plays F1/F2/F3 | Unused after F3 |
|---|---|---|---|---|---|---|---|---|---|---:|
| 10 / C1 | 8.00/7.44/6.82 | 7.44/6.82/6.14 | 0.562/0.613/0.680 | 0.113/0.137/0.166 | 0.449/0.476/0.514 | 0.247/0.243/0.215 | 0.232/0.216/0.194 | 0.000/0.000/0.000 | 1.211/1.239/1.284 | 6.14 |
| 10 / C2 | 8.00/7.53/6.83 | 7.53/6.83/5.93 | 0.470/0.695/0.909 | 0.074/0.108/0.149 | 0.198/0.293/0.380 | 0.373/0.328/0.267 | 0.328/0.295/0.248 | 0.000/0.000/0.001 | 1.046/1.118/1.206 | 5.93 |
| 14 / C1 | 8.00/7.09/6.13 | 7.09/6.13/5.15 | 0.915/0.958/0.980 | 0.316/0.331/0.352 | 0.599/0.627/0.628 | 0.212/0.203/0.189 | 0.243/0.232/0.237 | 0.000/0.000/0.001 | 1.167/1.203/1.204 | 5.15 |
| 14 / C2 | 8.00/6.93/5.74 | 6.93/5.74/4.42 | 1.073/1.189/1.315 | 0.296/0.305/0.327 | 0.389/0.442/0.494 | 0.289/0.277/0.236 | 0.319/0.298/0.271 | 0.000/0.002/0.024 | 1.061/1.087/1.117 | 4.42 |
| 18 / C1 | 8.00/6.85/5.67 | 6.85/5.67/4.48 | 1.149/1.180/1.191 | 0.435/0.452/0.460 | 0.713/0.728/0.732 | 0.202/0.197/0.193 | 0.276/0.259/0.269 | 0.000/0.000/0.001 | 1.252/1.271/1.272 | 4.48 |
| 18 / C2 | 8.00/6.53/4.99 | 6.53/4.99/3.47 | 1.468/1.537/1.520 | 0.393/0.424/0.442 | 0.537/0.557/0.539 | 0.246/0.231/0.237 | 0.310/0.304/0.324 | 0.000/0.007/0.093 | 1.155/1.183/1.159 | 3.47 |

| Skill / cost | Enter F2: 0 / 1 / 2 / 3–5 / 6–8 | Enter F3: 0 / 1 / 2 / 3–5 / 6–8 | F2 only D1, not C2 | F3 only D1, not C2 | F2 neither paid | F3 neither paid |
|---|---|---|---:|---:|---:|---:|
| 10 / C1 | 0.0% / 0.0% / 0.0% / 1.0% / 99.0% | 0.0% / 0.0% / 0.0% / 9.8% / 90.2% | 0.0% | 0.0% | 0.0% | 0.0% |
| 10 / C2 | 0.0% / 0.0% / 0.0% / 2.1% / 97.9% | 0.0% / 0.0% / 0.5% / 12.0% / 87.5% | 0.0% | 0.2% | 0.0% | 0.0% |
| 14 / C1 | 0.0% / 0.0% / 0.0% / 3.6% / 96.4% | 0.0% / 0.0% / 0.4% / 27.3% / 72.3% | 0.0% | 0.3% | 0.0% | 0.0% |
| 14 / C2 | 0.0% / 0.0% / 0.3% / 11.2% / 88.5% | 0.0% / 0.7% / 3.0% / 36.4% / 59.8% | 0.1% | 2.4% | 0.0% | 0.1% |
| 18 / C1 | 0.0% / 0.0% / 0.0% / 6.5% / 93.5% | 0.0% / 0.1% / 0.8% / 41.7% / 57.4% | 0.0% | 0.6% | 0.0% | 0.1% |
| 18 / C2 | 0.0% / 0.1% / 0.6% / 20.2% / 79.1% | 0.2% / 2.7% / 7.1% / 47.8% / 42.1% | 0.6% | 6.5% | 0.0% | 1.3% |

C2 produces useful, non-catastrophic attrition. After Fight 3, focal Spiritus averages 5.93 / 4.42 / 3.47 at Skills 10 / 14 / 18, compared with C1's 6.14 / 5.15 / 4.48. Compounds remain present in Fight 3 at 0.380 / 0.494 / 0.539 uses per focal fighter under C2, and total learned-Play use remains above 1.1 per fight. Skill-18 C2 is the strongest attrition case: 57.9% enter Fight 3 at 3–5 or less, but sophisticated fencing does not disappear. Only-D1 windows reach 6.5% of focal Fight-3 exchanges and neither-paid windows 1.3%; these thresholds are visible without becoming dominant starvation.

## Play-chain regression

| Cost | Mean learned-Play chain | Three-Play chains/fight | Attempted fourth/fight |
|---:|---:|---:|---:|
| C1 | 1.186 | 0.0186 | 0.0000 |
| C2 | 1.142 | 0.0110 | 0.0000 |

C2 modestly shortens learned-Play chains and reduces three-Play chains; no attempted fourth Play occurred. The current cap and Schielhau intrinsic-branch treatment remain unchanged.

## Answers to the required questions

A. **Yes, provisionally.** C2 better reflects the two-effect compound chassis because it adds real reserve thresholds while leaving the Plays common at healthy Spiritus.
B. **Yes.** At C2, 59.5%–82.9% of start-8 fights contain a compound; Skill 14–18 C2 still uses 1.0–1.4 compounds per fresh fight.
C. **Yes, especially Schielhau.** Under C1, healthy expert Schielhau declaration reaches roughly 85%–92% of legal opportunities, and aggregate compounds resolve more than half of defensive opportunities in many cells.
D. **Yes.** At 1 Spiritus C2 compounds are unavailable while D1 remains; at 2 they are legal but expensive enough to be chosen selectively.
E. **Yes.** D1 remains usable at the 1-Spiritus tier and continues appearing throughout C2 fresh and sequence cells.
F. **Partially.** Under adaptive revelation at Skill 18 / start 3, known-D Basic Parry rises as high as 14.1% at Spiritus 2 and 19.4% at 0, but under perfect information it remains only 2.1% at 1 because D1 is still available.
G. **Mostly intended expert progression, with the prior P1 warning preserved.** Compound use falls and Counter takes over; P1 itself remains suppressed by known D1 rather than by C2.
H. **Yes.** C2 makes 8 more operationally meaningful, especially at Skills 14–18, by converting it into several costly commitments rather than an almost untouched reserve.
I. **Yes.** C2 materially deepens R0 attrition at Skills 14–18 without producing general starvation.
J. **Yes.** Compounds remain visible in both later fights and reach 0.380–0.539 focal uses in Fight 3 under C2.
K. **Schielhau appears cheapest relative to its modeled opportunity.** It remains much more likely than either thrust counter because it is the sole compound on its trigger and competes with the artifactually free Zornhau-Ort. Absetzen and Scambiar are mechanically indistinguishable here.
L. **A common C2 price is defensible for the next prototype.** Differentiated prices may be needed later if distinct triggers, damage, Guards, or geometry separate their actual value.
M. **Substantial artifact risk remains.** The conclusions are conditional on one-roll Variant A, generic d6+1 damage, the artificial attack mix, heuristic softmax utilities, free Zornhau-Ort/Nachreisen/Pommel, unresolved Guards and Power Strike, 50% soft-bind and 25% close-crossing calibration, and absent engagement geometry.

## Artifacts, limitations, and OPEN questions

- The policy is not a solved equilibrium and its utility classifications are not psychological claims.
- Absetzen and Scambiar are offered together on the same modeled thrust state with identical mechanics. Their individual probabilities cannibalize one another and cannot support differentiated pricing.
- Schielhau has a single compound slot on its trigger and an S2 rejoinder; comparison to either thrust option is not apples-to-apples.
- Generic d6+1 damage overstates chassis sameness and may distort urgency, especially for pommel and thrust/cut differences.
- Artificial attack proportions determine opportunity counts. Adaptive Schielhau revelation also changes the attack mix.
- Zornhau-Ort, Nachreisen, and Pommel Strike remain free provisional exercise mechanics. Substitution toward them is not a pricing recommendation.
- Guard economy is unresolved, so Power Strike competition remains unmodeled.
- Bind softness, close-crossing frequency, engagement geometry, reach, weapon profiles, and outnumbering access remain unresolved.
- Final compound cost, Spiritus maximum/recovery, other Play prices, tiers, and card text remain OPEN.

## Recommended Next Decision

Use **C2** as the better next **PROVISIONAL** prototype price for Absetzen, Scambiar di Punta, and Schielhau. Keep all three at a common 2-Spiritus price for now: the current shared Variant A chassis supports a common test price, while the model is too abstract to justify individual prices. Treat the **0 / 1 / 2** hierarchy as useful: 0 leaves basic/free fencing, 1 preserves D1 conversion, and 2 makes compound defence-and-offence credible but costly. Maximum Spiritus **8** becomes more meaningful under C2, particularly across three R0 fights and at expert skill, without preventing later-fight compounds.

No further pricing-only simulation is needed before moving to another subsystem. The next useful work is to mature one of the missing competitors or value drivers—preferably Guard/Power Strike economy or engagement geometry—then rerun C2 as a regression. Do not update Atra Melee Design Packet v0.4 and do not promote C2 beyond PROVISIONAL on this evidence.


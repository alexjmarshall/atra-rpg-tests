# Durchwechseln–Schielhau State-Model Results

Status: **PROVISIONAL experiment; not canonical mechanics**

Historical identity/source evidence for Durchwechseln and Schielhau (including Schielhau's intrinsic long-point branch) remains **HISTORICALLY ACCEPTED: EARLIER / A**. Every mechanic, state label, exchange role, policy, opposed procedure, Bane procedure, and prototype-Play point classification below is **PROVISIONAL**. Spiritus costs, final tiers, final text, universal Parry taxonomy, bind mechanics, engagement geometry, weapon profiles, and final chain architecture remain **OPEN**.

## Historical boundary and scoped state audit

- Durchwechseln preserves the single audited Pseudo-Peter von Danzig witness, Starhemberg Fechtbuch Cod.44.A.8, ff. 30v.3–31r.2. No additional witness is claimed.
- Schielhau preserves Pseudo-Peter von Danzig, Cod.44.A.8, ff. 23v.1–23v.2, historical names `Schilär` / `Schilhaw`, normalized Atra name Schielhau, and historical classification `meisterhau` / `master strike`. “Master strike” is not used as its procedural chassis.
- The Schielhau long-point denial is intrinsic: it is not another action, another learned Play, a generic Counter-Feint, or a follow-up after arbitrary Parries.

| Play / phase | Seeks or contacts blade? | Engagement intent | Point threat | Generalized Durchwechseln | Basis |
|---|---|---|---|---|---|
| Absetzen: joined set-aside/thrust | Yes | blade-seeking | threatening | unavailable | directly supported |
| Zornhau-Ort: pre-bind counter-cut | Yes | blade-seeking | unknown | uncertain; suppressed | uncertain |
| Zornhau-Ort: soft-bind point | Yes | not applicable | threatening | unavailable (bind) | directly supported |
| Durchwechseln: point change | No | body-threat | threatening | executing, not a target | directly supported |
| Scambiar di Punta: crossing counter-thrust | Yes | blade-seeking | threatening | unavailable | directly supported |
| Nachreisen: recovery pursuit | No | body-threat | not threatening | unavailable (no weapon commitment) | directly supported |
| Pommel Strike: close crossing | Not separable | not applicable | not threatening | unavailable (close contact) | directly supported |
| Schielhau: transient declaration window | Yes | blade-seeking | unknown | uncertain; admitted only to test sourced branch | uncertain staging |
| Schielhau: established intrinsic long point | No | body-threat | threatening | unavailable / denied | directly supported |

## Model and policy

The state trigger is `contact=none` + opponent commitment toward the user's weapon (`blade_seeking`) + opponent `point_threat=not_threatening`. It is not keyed to Parry or any Play name. Absetzen and Scambiar deny the trigger by maintaining a threatening point. Zornhau-Ort's pre-bind point state remains uncertain and is not made vulnerable by inference. A proactive beat exists only as **PROVISIONAL ATRA GENERALIZATION FROM SOURCED PRINCIPLE** to exercise Durchwechseln as a Remedy.

Choices use expected-value softmax (temperature 0.32 for defence, 0.42–0.55 elsewhere) over the legal menu. Knowledge changes option utilities rather than banning options, and a separate seeded policy stream preserves mixed behavior. Adaptive fighters begin with neither hidden Play known; observation sets `durchwechseln_known` and `schielhau_known` separately for the rest of that fight. Naive policies never use observed knowledge. Perfect-information policies start with both flags set.

S1 automatically denies Throughchanging after a successful Schielhau establishes long point. S2 reuses the original successful Schielhau d20 and compares it to one fresh Durchwechseln d20: lower successful roll wins; ties favor the established Schielhau opposition; one success beats failure. Because entry requires a successful Schielhau, the two-fail case is unreachable under reuse (and is recorded as zero). S3 rolls Durchwechseln with one Bane (2d20, keep higher), without stacking.

## Main mirrored duel matrix

| Information | Variant | Focal win | Symmetry deviation | Rounds | Double defeat | Parry | Counter | Ignore | Schielhau | Durch opp./fight | Declare | Decline | Durch success | Long-point/exchange | Avg chain | Cap | Fourth |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| naive | S1 | 48.70% | 1.07% | 3.754 | 1.52% | 7.67% | 3.35% | 0.63% | 7.59% | 0.785 | 71.95% | 28.05% | 36.46% | 2.86% | 0.389 | 0.398% | 0.000% |
| naive | S2 | 49.43% | 0.14% | 3.748 | 1.27% | 7.85% | 3.34% | 0.61% | 7.48% | 0.782 | 72.14% | 27.86% | 42.41% | 2.78% | 0.389 | 0.403% | 0.000% |
| naive | S3 | 49.08% | 0.41% | 3.769 | 1.44% | 7.72% | 3.35% | 0.65% | 7.39% | 0.789 | 72.34% | 27.66% | 42.30% | 2.81% | 0.390 | 0.393% | 0.000% |
| adaptive_revelation | S1 | 49.94% | 1.40% | 3.763 | 1.52% | 7.87% | 3.53% | 0.72% | 7.26% | 0.751 | 58.71% | 41.29% | 45.18% | 0.82% | 0.360 | 0.105% | 0.000% |
| adaptive_revelation | S2 | 49.14% | 0.01% | 3.809 | 1.71% | 7.95% | 3.64% | 0.68% | 7.20% | 0.755 | 71.42% | 28.58% | 42.69% | 2.43% | 0.378 | 0.335% | 0.000% |
| adaptive_revelation | S3 | 49.48% | 0.47% | 3.789 | 1.52% | 7.78% | 3.34% | 0.66% | 7.41% | 0.757 | 66.21% | 33.79% | 46.17% | 1.91% | 0.377 | 0.265% | 0.000% |
| perfect_information | S1 | 48.94% | 0.06% | 4.008 | 2.17% | 8.70% | 4.58% | 0.92% | 5.21% | 0.359 | 49.99% | 50.01% | 40.20% | 0.58% | 0.283 | 0.079% | 0.000% |
| perfect_information | S2 | 48.88% | 0.08% | 4.036 | 2.15% | 8.80% | 4.54% | 0.80% | 5.50% | 0.371 | 69.97% | 30.03% | 37.05% | 1.84% | 0.299 | 0.258% | 0.000% |
| perfect_information | S3 | 48.82% | 0.13% | 3.985 | 2.23% | 8.87% | 4.64% | 0.84% | 5.18% | 0.359 | 64.04% | 35.96% | 40.87% | 1.43% | 0.291 | 0.197% | 0.000% |

### Per-Play results for every main cell

| Information | Variant | Play | Uses/fight | Success | Damage/fight | Total damage |
|---|---|---|---:|---:|---:|---:|
| naive | S1 | Absetzen | 0.220 | 50.15% | 0.500 | 3.76% |
| naive | S1 | Zornhau-Ort | 0.118 | 51.17% | 0.068 | 0.51% |
| naive | S1 | Durchwechseln | 0.565 | 36.46% | 0.933 | 7.01% |
| naive | S1 | Scambiar di Punta | 0.209 | 48.13% | 0.457 | 3.43% |
| naive | S1 | Nachreisen | 0.581 | 50.98% | 1.129 | 8.48% |
| naive | S1 | Pommel Strike | 0.034 | 51.33% | 0.082 | 0.61% |
| naive | S1 | Schielhau | 0.418 | 49.57% | 0.935 | 7.02% |
| naive | S2 | Absetzen | 0.218 | 49.64% | 0.486 | 3.65% |
| naive | S2 | Zornhau-Ort | 0.116 | 50.50% | 0.064 | 0.48% |
| naive | S2 | Durchwechseln | 0.565 | 42.41% | 1.070 | 8.05% |
| naive | S2 | Scambiar di Punta | 0.221 | 50.51% | 0.507 | 3.81% |
| naive | S2 | Nachreisen | 0.566 | 50.85% | 1.097 | 8.25% |
| naive | S2 | Pommel Strike | 0.040 | 49.37% | 0.085 | 0.64% |
| naive | S2 | Schielhau | 0.411 | 41.78% | 0.771 | 5.80% |
| naive | S3 | Absetzen | 0.216 | 49.33% | 0.481 | 3.62% |
| naive | S3 | Zornhau-Ort | 0.119 | 48.88% | 0.066 | 0.49% |
| naive | S3 | Durchwechseln | 0.571 | 42.30% | 1.092 | 8.22% |
| naive | S3 | Scambiar di Punta | 0.218 | 49.68% | 0.487 | 3.67% |
| naive | S3 | Nachreisen | 0.588 | 49.16% | 1.093 | 8.22% |
| naive | S3 | Pommel Strike | 0.035 | 52.00% | 0.087 | 0.66% |
| naive | S3 | Schielhau | 0.409 | 40.68% | 0.741 | 5.58% |
| adaptive_revelation | S1 | Absetzen | 0.218 | 50.00% | 0.502 | 3.77% |
| adaptive_revelation | S1 | Zornhau-Ort | 0.114 | 52.41% | 0.071 | 0.53% |
| adaptive_revelation | S1 | Durchwechseln | 0.441 | 45.18% | 0.889 | 6.67% |
| adaptive_revelation | S1 | Scambiar di Punta | 0.217 | 49.31% | 0.476 | 3.58% |
| adaptive_revelation | S1 | Nachreisen | 0.564 | 50.07% | 1.080 | 8.11% |
| adaptive_revelation | S1 | Pommel Strike | 0.036 | 47.47% | 0.080 | 0.60% |
| adaptive_revelation | S1 | Schielhau | 0.401 | 49.47% | 0.893 | 6.70% |
| adaptive_revelation | S2 | Absetzen | 0.225 | 48.59% | 0.491 | 3.67% |
| adaptive_revelation | S2 | Zornhau-Ort | 0.115 | 51.34% | 0.060 | 0.45% |
| adaptive_revelation | S2 | Durchwechseln | 0.539 | 42.69% | 1.034 | 7.72% |
| adaptive_revelation | S2 | Scambiar di Punta | 0.219 | 49.75% | 0.491 | 3.67% |
| adaptive_revelation | S2 | Nachreisen | 0.578 | 49.80% | 1.109 | 8.28% |
| adaptive_revelation | S2 | Pommel Strike | 0.038 | 50.44% | 0.082 | 0.61% |
| adaptive_revelation | S2 | Schielhau | 0.403 | 41.97% | 0.745 | 5.56% |
| adaptive_revelation | S3 | Absetzen | 0.223 | 49.59% | 0.488 | 3.67% |
| adaptive_revelation | S3 | Zornhau-Ort | 0.115 | 52.36% | 0.057 | 0.43% |
| adaptive_revelation | S3 | Durchwechseln | 0.501 | 46.17% | 1.043 | 7.85% |
| adaptive_revelation | S3 | Scambiar di Punta | 0.226 | 49.54% | 0.503 | 3.79% |
| adaptive_revelation | S3 | Nachreisen | 0.585 | 49.80% | 1.104 | 8.31% |
| adaptive_revelation | S3 | Pommel Strike | 0.036 | 47.48% | 0.078 | 0.59% |
| adaptive_revelation | S3 | Schielhau | 0.413 | 42.42% | 0.793 | 5.97% |
| perfect_information | S1 | Absetzen | 0.305 | 49.74% | 0.666 | 4.96% |
| perfect_information | S1 | Zornhau-Ort | 0.091 | 49.72% | 0.049 | 0.37% |
| perfect_information | S1 | Durchwechseln | 0.179 | 40.20% | 0.326 | 2.43% |
| perfect_information | S1 | Scambiar di Punta | 0.306 | 51.37% | 0.699 | 5.21% |
| perfect_information | S1 | Nachreisen | 0.459 | 49.61% | 0.881 | 6.56% |
| perfect_information | S1 | Pommel Strike | 0.048 | 49.74% | 0.108 | 0.81% |
| perfect_information | S1 | Schielhau | 0.313 | 49.81% | 0.696 | 5.18% |
| perfect_information | S2 | Absetzen | 0.302 | 51.01% | 0.699 | 5.19% |
| perfect_information | S2 | Zornhau-Ort | 0.092 | 52.45% | 0.057 | 0.42% |
| perfect_information | S2 | Durchwechseln | 0.260 | 37.05% | 0.428 | 3.18% |
| perfect_information | S2 | Scambiar di Punta | 0.316 | 49.47% | 0.705 | 5.23% |
| perfect_information | S2 | Nachreisen | 0.455 | 50.24% | 0.840 | 6.23% |
| perfect_information | S2 | Pommel Strike | 0.048 | 47.54% | 0.104 | 0.77% |
| perfect_information | S2 | Schielhau | 0.332 | 42.09% | 0.617 | 4.58% |
| perfect_information | S3 | Absetzen | 0.312 | 51.00% | 0.713 | 5.32% |
| perfect_information | S3 | Zornhau-Ort | 0.085 | 50.79% | 0.050 | 0.37% |
| perfect_information | S3 | Durchwechseln | 0.230 | 40.87% | 0.427 | 3.19% |
| perfect_information | S3 | Scambiar di Punta | 0.313 | 49.51% | 0.694 | 5.18% |
| perfect_information | S3 | Nachreisen | 0.439 | 50.47% | 0.853 | 6.36% |
| perfect_information | S3 | Pommel Strike | 0.045 | 51.29% | 0.108 | 0.80% |
| perfect_information | S3 | Schielhau | 0.309 | 43.83% | 0.610 | 4.55% |

### Prototype-state and action frequencies

| Information | Variant | Actions spent | Preserved | Bind | Close | Recovery | Blade-seeking | Point threatening | Point not threatening |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| naive | S1 | 7.439 | 0.000 | 7.64% | 0.85% | 15.40% | 31.46% | 14.56% | 14.56% |
| naive | S2 | 7.430 | 0.000 | 7.73% | 0.95% | 15.22% | 31.70% | 14.65% | 14.84% |
| naive | S3 | 7.471 | 0.000 | 7.66% | 0.92% | 15.80% | 31.44% | 14.54% | 14.69% |
| adaptive_revelation | S1 | 7.461 | 0.000 | 7.82% | 0.89% | 15.18% | 30.56% | 12.79% | 14.01% |
| adaptive_revelation | S2 | 7.554 | 0.000 | 7.81% | 0.92% | 15.43% | 30.44% | 14.52% | 13.93% |
| adaptive_revelation | S3 | 7.509 | 0.000 | 7.78% | 0.91% | 15.44% | 30.91% | 13.82% | 14.05% |
| perfect_information | S1 | 7.963 | 0.000 | 9.06% | 1.08% | 11.54% | 21.72% | 15.69% | 5.63% |
| perfect_information | S2 | 8.035 | 0.000 | 9.19% | 1.09% | 11.34% | 22.10% | 17.03% | 5.64% |
| perfect_information | S3 | 7.925 | 0.000 | 9.35% | 1.05% | 11.26% | 21.96% | 16.95% | 5.62% |

## Deterrence and adaptive revelation

| Variant | Unsafe selected | Unsafe avoided after D reveal | D attempts into known Schiel | D avoided due known Schiel | Altered decisions/fight |
|---|---:|---:|---:|---:|---:|
| S1 | 0.067 | 0.043 | 0.045 | 0.153 | 0.588 |
| S2 | 0.075 | 0.053 | 0.136 | 0.064 | 0.671 |
| S3 | 0.074 | 0.046 | 0.106 | 0.096 | 0.639 |

### Adaptive before/after reveal splits

Counts are per fight and each event is split independently around Durchwechseln and Schielhau revelation.

| Variant | Reveal split | D opportunities | D declarations | D declines | Unsafe selected | Schiel opportunities | Schiel declarations |
|---|---|---:|---:|---:|---:|---:|---:|
| S1 | before_durch_reveal | 0.685 | 0.402 | 0.283 | 0.067 | 0.366 | 0.366 |
| S1 | after_durch_reveal | 0.066 | 0.039 | 0.027 | 0.000 | 0.035 | 0.035 |
| S1 | before_schiel_reveal | 0.517 | 0.371 | 0.146 | 0.062 | 0.374 | 0.374 |
| S1 | after_schiel_reveal | 0.234 | 0.070 | 0.164 | 0.005 | 0.027 | 0.027 |
| S2 | before_durch_reveal | 0.674 | 0.481 | 0.194 | 0.075 | 0.362 | 0.362 |
| S2 | after_durch_reveal | 0.081 | 0.059 | 0.022 | 0.000 | 0.040 | 0.040 |
| S2 | before_schiel_reveal | 0.525 | 0.383 | 0.142 | 0.070 | 0.372 | 0.372 |
| S2 | after_schiel_reveal | 0.230 | 0.157 | 0.073 | 0.005 | 0.031 | 0.031 |
| S3 | before_durch_reveal | 0.681 | 0.449 | 0.232 | 0.073 | 0.369 | 0.369 |
| S3 | after_durch_reveal | 0.076 | 0.052 | 0.024 | 0.001 | 0.043 | 0.043 |
| S3 | before_schiel_reveal | 0.521 | 0.372 | 0.149 | 0.068 | 0.381 | 0.381 |
| S3 | after_schiel_reveal | 0.236 | 0.129 | 0.107 | 0.006 | 0.032 | 0.032 |

## Basic Parry limitation and decomposition

The prior v0.2 simulator did **not** treat every basic Parry as blade-seeking: it assigned blade-seeking randomly to 50% of successful basic Parries. It had no point-threat state and could not distinguish a body-covering defence from a blade-chasing defence. It therefore neither preserved nor abandoned point threat in represented state. It also treated every Absetzen, Scambiar, and Zornhau-Ort as vulnerable. `legacy_random_half` preserves that limitation. `documented_subset` is the explicitly documented experimental alternative: body-cover is always available, while a blade-chase subtype is offered only against the simulator's otherwise-unclassified `other-cut`; this is a policy proxy, not a canonical or universal Parry taxonomy.

| Cell | Durch damage/fight | Durch opp./fight | Declare | Unsafe/fight | Rounds |
|---|---:|---:|---:|---:|---:|
| old_trigger_naive_legacy | 2.075 | 1.371 | 72.65% | 0.148 | 3.854 |
| state_trigger_naive_legacy | 1.201 | 0.845 | 73.69% | 0.153 | 3.866 |
| state_trigger_adaptive_legacy | 1.085 | 0.819 | 70.23% | 0.147 | 3.878 |
| state_trigger_adaptive_documented_subset | 1.006 | 0.754 | 69.73% | 0.073 | 3.770 |

## Adaptive ablations (mirrored)

| Variant | Repertoire | Focal win | Rounds | Durch damage | Schiel damage | Play damage/fight |
|---|---|---:|---:|---:|---:|---:|
| S1 | full | 49.47% | 3.769 | 0.911 | 0.939 | 4.136 |
| S1 | remove_durchwechseln | 49.55% | 3.664 | 0.000 | 0.907 | 3.100 |
| S1 | remove_schielhau | 48.22% | 3.974 | 0.904 | 0.000 | 3.428 |
| S1 | remove_both | 48.38% | 3.801 | 0.000 | 0.000 | 2.475 |
| S2 | full | 49.95% | 3.805 | 1.014 | 0.776 | 3.976 |
| S2 | remove_durchwechseln | 49.67% | 3.642 | 0.000 | 0.850 | 3.009 |
| S2 | remove_schielhau | 48.58% | 3.973 | 0.933 | 0.000 | 3.452 |
| S2 | remove_both | 48.80% | 3.837 | 0.000 | 0.000 | 2.351 |
| S3 | full | 48.33% | 3.749 | 1.068 | 0.772 | 4.163 |
| S3 | remove_durchwechseln | 49.48% | 3.671 | 0.000 | 0.919 | 3.059 |
| S3 | remove_schielhau | 47.78% | 3.954 | 0.942 | 0.000 | 3.484 |
| S3 | remove_both | 49.13% | 3.792 | 0.000 | 0.000 | 2.465 |

## One-versus-two exploratory results

No generic anti-outnumbered bonus is used; all combatants have the same repertoire. These cells are exploratory because pair selection and contact are abstract and engagement geometry remains OPEN.

| Information | Variant | Focal win | Rounds | Double defeat | Durch damage/fight | Schiel damage/fight |
|---|---|---:|---:|---:|---:|---:|
| naive | S1 | 3.65% | 2.831 | 0.17% | 0.847 | 0.852 |
| naive | S2 | 3.75% | 2.862 | 0.07% | 1.016 | 0.740 |
| naive | S3 | 3.47% | 2.815 | 0.20% | 0.993 | 0.654 |
| adaptive_revelation | S1 | 3.88% | 2.850 | 0.23% | 0.863 | 0.824 |
| adaptive_revelation | S2 | 3.80% | 2.869 | 0.10% | 0.964 | 0.695 |
| adaptive_revelation | S3 | 3.63% | 2.897 | 0.20% | 0.953 | 0.712 |
| perfect_information | S1 | 4.12% | 3.068 | 0.27% | 0.311 | 0.637 |
| perfect_information | S2 | 3.82% | 3.045 | 0.33% | 0.426 | 0.551 |
| perfect_information | S3 | 3.72% | 3.014 | 0.20% | 0.384 | 0.580 |

## Play-chain stress

| 0 learned | 1 learned | 2 learned | 3 learned |
|---:|---:|---:|---:|
| 65.99% | 30.54% | 3.14% | 0.34% |

Exact cap sequences:
- Nachreisen → Schielhau → Durchwechseln: 225

Attempted fourth Plays: **0**. Schielhau's intrinsic branch is never counted separately.

## Answers to the experiment questions

A. Replacing old named/blade-seeking vulnerability with point-aware state logic reduced Durchwechseln damage from 2.075 to 1.201 per fight (42.1%). After adaptation, replacing the legacy random-half Parry label with the documented subset changed it from 1.085 to 1.006 (7.2% reduction). These are sequential sensitivity effects, not causal estimates from a solved equilibrium.
B. Adaptive revelation changed Durchwechseln damage from 1.201 to 1.085 under the same legacy Parry policy (9.7% reduction).
C. The state trigger produces 0.526 uses and 1.006 damage per fight in the adaptive documented-subset cell, versus 0.996 and 2.075 in the old-trigger cell.
D. It remains usable as continuation, rejoinder, and remedy in the experiment; role-specific opportunity/declaration counts are machine-readable. Remedy use against the proactive beat is explicitly a provisional Atra generalization, not a claimed named witness.
E. The only naturally vulnerable modeled actions are point-off-line blade chases and the provisional proactive beat. Zornhau-Ort remains uncertain rather than declared vulnerable.
F. Absetzen, Scambiar di Punta, and established Schielhau long point naturally deny it by maintaining an immediate point threat; bind/close states also deny it.
G. Schielhau supplies counterplay without removing Durchwechseln from other state-valid contexts; the ablations show their independent and joint contributions.
H. S2 retains the most interactive branch; S1 maximizes deterrence and S3 maximizes continued attempt risk. The recommendation below remains provisional.
I. No basic option reaches 100% or 0% across all relevant opportunities in the main matrix; the softmax policy avoids hard-coded never/always behavior. This is evidence about this policy, not a solved equilibrium.
J. Direct damage is in per-Play tables; avoided unsafe defences, known-Schiel declines, and altered decisions report deterrence separately.
K. The cap binds in 0.335% of adaptive S2 exchanges; attempted fourth frequency is 0.000%.
L. Soft-bind probability, close-crossing generation, d6+1 damage, abstract pair contact in 1-v-2, absent engagement geometry, and heuristic policy utilities remain artifacts. None should be used for final tuning.

## Recommended Next Decision

- Continue prototype work with the state-based trigger and keep Durchwechseln unavailable against an already threatening point.
- Use S2 opposed resolution as the next comparison baseline because it preserves visible counterplay without automatic denial; retain S1 and S3 as sensitivity bounds.
- Specify a universal Parry taxonomy and engagement geometry before any balance promotion or Spiritus/tier decision.
- Keep Zornhau-Ort's pre-bind point state uncertain until a dedicated geometry/source review resolves it.

Seeds: experiment `240823`, policy/random stream included in each deterministic cell seed; configured policy seed `90210`. Main trials/cell: `12000`; secondary trials/cell: `6000`. Precondition violations in adaptive S2: `0`.

# Spiritus, Basic Parry, and Durchwechseln Results

Status: **PROVISIONAL bounded experiment; no canonical rule change**

## Executive result

The central result is conditional, not a universal pass. P1 remains visibly usable after revelation at Skill 10 and when the attacker is nearly exhausted, but post-reveal use approaches zero at Skill 18 while the attacker retains a usable reserve. The required pre-roll gamble and D1 price therefore preserve Basic Parry in some important states, not across the whole tested Skill range.

| Skill / start | P1 Parries/fight | P1 after-known/fight | After-known opportunities choosing P1 | All defence opportunities choosing P1 | Parries interrupted | Attacker declines Durch | End Spiritus |
|---|---:|---:|---:|---:|---:|---:|---:|
| 10 / 8 | 0.425 | 0.026 | 20.4% | 21.1% | 29.1% | 52.2% | 7.30 |
| 10 / 5 | 0.439 | 0.030 | 23.0% | 22.0% | 24.0% | 55.5% | 4.32 |
| 10 / 3 | 0.475 | 0.033 | 30.0% | 23.8% | 18.4% | 65.3% | 2.40 |
| 10 / 1 | 0.789 | 0.006 | 51.5% | 37.5% | 1.6% | 96.9% | 0.86 |
| 14 / 8 | 0.385 | 0.015 | 4.7% | 17.0% | 86.7% | 15.4% | 6.97 |
| 14 / 5 | 0.407 | 0.015 | 5.5% | 18.6% | 80.6% | 19.1% | 4.03 |
| 14 / 3 | 0.425 | 0.025 | 8.8% | 18.8% | 71.9% | 24.8% | 2.07 |
| 14 / 1 | 0.794 | 0.041 | 40.6% | 32.2% | 17.8% | 78.6% | 0.63 |
| 18 / 8 | 0.371 | 0.001 | 0.3% | 15.1% | 98.1% | 9.2% | 6.78 |
| 18 / 5 | 0.373 | 0.002 | 0.4% | 15.1% | 97.9% | 9.3% | 3.79 |
| 18 / 3 | 0.385 | 0.007 | 1.6% | 15.6% | 95.1% | 12.2% | 1.85 |
| 18 / 1 | 0.817 | 0.135 | 40.5% | 28.4% | 43.9% | 56.2% | 0.39 |

**Core diagnostic — mixed result.** After Durchwechseln is known, Basic Parry is still chosen at Skill 10 and returns strongly when only 1 Spiritus remains. At Skill 18 with starts 8/5, its post-reveal rate is a warning signal near zero. The exact rates are policy outputs, not player-frequency forecasts.

## P0 versus P1 and Durchwechseln cost

Skill 10, C1, adaptive revelation; values are averaged over the four requested starting pools.

| Parry | D cost | Parry/fight | After-known/fight | Durch declare | Durch decline | Durch damage/fight | Spiritus spent/fight |
|---|---:|---:|---:|---:|---:|---:|---:|
| P0 | 0 | 0.521 | 0.017 | 88.4% | 11.6% | 0.201 | 0.837 |
| P0 | 1 | 0.531 | 0.012 | 64.5% | 35.5% | 0.196 | 0.979 |
| P0 | 2 | 0.532 | 0.009 | 43.4% | 56.6% | 0.154 | 1.061 |
| P1 | 0 | 0.539 | 0.059 | 60.4% | 39.6% | 0.804 | 0.856 |
| P1 | 1 | 0.532 | 0.024 | 32.5% | 67.5% | 0.367 | 1.058 |
| P1 | 2 | 0.531 | 0.013 | 19.8% | 80.2% | 0.220 | 1.116 |

P0 suppresses only the Basic-Parry trigger; its remaining Durchwechseln opportunities are the retained S2 Schielhau rejoinder. P0 is a mechanical control, not a historical preference.

## Adaptive revelation versus perfect information

The reduced perfect-information matrix makes P1 knowledge active from the first defensive opportunity. Adaptive values use only opportunities after actual revelation.

| Skill / start | Adaptive post-reveal P1 use | Perfect-information P1 use | Adaptive Durch declaration | Perfect Durch declaration |
|---|---:|---:|---:|---:|
| 10 / 8 | 20.4% | 25.0% | 47.8% | 41.0% |
| 10 / 3 | 30.0% | 26.8% | 34.7% | 30.4% |
| 14 / 8 | 4.7% | 6.0% | 84.6% | 84.8% |
| 14 / 3 | 8.8% | 7.5% | 75.2% | 75.0% |
| 18 / 8 | 0.3% | 0.3% | 90.8% | 89.2% |
| 18 / 3 | 1.6% | 0.7% | 87.8% | 82.5% |

Perfect information changes when deterrence begins but preserves the same direction: P1 remains mixed at Skill 10 and is strongly displaced at Skill 18 while Spiritus is available.

## Pre-roll timing

The `post` rows are deliberately illegal counterfactuals in which the attacker observes a successful Parry before deciding. They isolate the value of the required pre-roll commitment.

| Skill | Timing | Parry/fight | Interrupted | Durch declarations/fight | Durch Spiritus/fight | Durch damage/fight |
|---|---|---:|---:|---:|---:|---:|
| 10 | pre | 0.432 | 25.0% | 0.308 | 0.308 | 0.482 |
| 10 | post | 0.394 | 45.2% | 0.369 | 0.369 | 0.639 |
| 14 | pre | 0.398 | 83.9% | 0.712 | 0.712 | 1.686 |
| 14 | post | 0.373 | 66.6% | 0.618 | 0.618 | 1.351 |
| 18 | pre | 0.395 | 98.5% | 0.952 | 0.952 | 2.804 |
| 18 | post | 0.385 | 90.7% | 0.922 | 0.922 | 2.668 |

Pre-roll timing makes Durchwechseln buy an uncertain alternative to the Parry roll. At Skill 10, the illegal post-roll model spends only after known Parry success and yields more Durch damage per Spiritus. At Skill 14/18 the Parry is already likely to succeed and Durchwechseln is highly reliable, so the uncertainty discount becomes small and the legal pre-roll policy declares at least as often. Timing helps most in the low/equal-success band; it does not rescue high-Skill P1 by itself.

## Why attackers decline Durchwechseln

D1/C1 P1 cells, all requested skills and starting pools combined:

- low current Spiritus: **7,028 (56.4%)**
- low defender Parry chance / better to gamble on Parry failure: **3,379 (27.1%)**
- low attacker Durchwechseln chance: **1,354 (10.9%)**
- other (mixed-policy exploration): **708 (5.7%)**

These are utility categories, not psychological claims. The explicit 'better to gamble on Parry failure' category is the intended case where the free original-strike branch compares favorably with a paid Durchwechseln roll.

## Skill relationship response surface

One-window D1 policy probabilities at full HP and Spiritus 5 (perfect repertoire knowledge):

| Attacker Skill | Defender Skill | Hit if Parry rolls | Durch success | Declare probability | Deterministic preference |
|---:|---:|---:|---:|---:|---|
| 10 | 10 | 50.0% | 50.0% | 26.0% | decline |
| 10 | 14 | 30.0% | 50.0% | 51.6% | declare |
| 10 | 18 | 10.0% | 50.0% | 76.4% | declare |
| 14 | 10 | 50.0% | 70.0% | 51.6% | declare |
| 14 | 14 | 30.0% | 70.0% | 76.4% | declare |
| 14 | 18 | 10.0% | 70.0% | 90.8% | declare |
| 18 | 10 | 50.0% | 90.0% | 76.4% | declare |
| 18 | 14 | 30.0% | 90.0% | 90.8% | declare |
| 18 | 18 | 10.0% | 90.0% | 96.8% | declare |

Low defender Skill raises the chance that the original Parry simply fails, making conservation rational. High defender Skill and high attacker Skill favor Durchwechseln. The complete surface for Spiritus 8/5/3/1 is in `results.json`.

## Compound counter price

Skill 10, P1/D1, adaptive revelation; averaged over starting Spiritus 8/5/3/1.

| Cost | Play | Opportunities | Use rate | Success | Damage/fight | Spiritus/fight | Parry displaced | Counter displaced | Mean Spiritus at declaration | Early use | Late use |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | Absetzen | 6,794 | 49.7% | 50.7% | 0.648 | 0.000 | 1,386 | 1,990 | 4.17 | 50.1% | 49.3% |
| 0 | Scambiar di Punta | 6,794 | 46.5% | 49.8% | 0.593 | 0.000 | 1,290 | 1,867 | 4.19 | 45.2% | 47.8% |
| 0 | Schielhau | 9,039 | 85.4% | 49.3% | 1.179 | 0.000 | 635 | 1,978 | 4.20 | 82.7% | 87.8% |
| 1 | Absetzen | 6,862 | 37.1% | 50.6% | 0.488 | 0.212 | 1,024 | 1,522 | 4.76 | 36.6% | 37.6% |
| 1 | Scambiar di Punta | 6,862 | 35.7% | 48.8% | 0.452 | 0.204 | 1,069 | 1,383 | 4.76 | 34.2% | 37.4% |
| 1 | Schielhau | 9,566 | 51.6% | 49.7% | 0.746 | 0.412 | 473 | 1,393 | 5.01 | 49.6% | 53.4% |

C1 reduces compound-counter use without eliminating the named counters: roughly half of Schielhau opportunities and a little over one third of each thrust-counter opportunity are still selected in this Skill-10 aggregate. Late use does not fall below early use in these short fights, so the evidence supports price sensitivity, not a claim that late-fight scarcity alone drives substitution. Because all three choices share the same one-roll Variant A chassis here, a common candidate price is supported only within this abstraction.

## Three-fight Spiritus isolation experiment

Focal HP, actions, recovery state, and knowledge reset each fight; only Spiritus carries. Every opponent is fresh at Spiritus 8. All three duels are run even after a focal loss so resource trajectories are not survivor-biased. 'All three wins' is therefore an outcome index, not literal campaign survival.

| Cell | Recovery | Enter F1/F2/F3 | Leave F1/F2/F3 | Spend F1/F2/F3 | Durch F1/F2/F3 | Compound F1/F2/F3 | Parry F1/F2/F3 | Enter F2 0 / 1-2 / 3-5 / 6-8 | Enter F3 0 / 1-2 / 3-5 / 6-8 | Future-value conservation | Starvation/sequence | All-three wins |
|---|---|---|---|---|---|---|---|---|---|---:|---:|---:|
| D1/C1 | R0 | 8.00/7.44/6.83 | 7.44/6.83/6.14 | 1.13/1.24/1.40 | 0.22/0.27/0.33 | 0.91/0.97/1.07 | 0.51/0.47/0.42 | 0%/0%/1%/99% | 0%/0%/9%/91% | 1.1% | 0.000 | 11.5% |
| D1/C1 | R2 | 8.00/7.98/7.97 | 7.29/7.27/7.25 | 1.41/1.41/1.43 | 0.35/0.34/0.36 | 1.06/1.07/1.08 | 0.44/0.42/0.43 | 0%/0%/0%/100% | 0%/0%/0%/100% | 0.0% | 0.000 | 11.4% |
| D1/C1 | RFULL | 8.00/8.00/8.00 | 7.29/7.28/7.28 | 1.40/1.42/1.43 | 0.34/0.35/0.35 | 1.06/1.07/1.08 | 0.42/0.42/0.43 | 0%/0%/0%/100% | 0%/0%/0%/100% | 0.0% | 0.000 | 11.3% |
| D0/C1 | R0 | 8.00/7.56/7.07 | 7.56/7.07/6.53 | 0.90/0.99/1.08 | 0.44/0.44/0.47 | 0.90/0.99/1.08 | 0.51/0.48/0.43 | 0%/0%/0%/100% | 0%/0%/5%/95% | 0.0% | 0.000 | 11.6% |
| D0/C1 | R2 | 8.00/7.99/7.99 | 7.47/7.46/7.44 | 1.08/1.05/1.08 | 0.46/0.46/0.46 | 1.08/1.05/1.08 | 0.44/0.43/0.44 | 0%/0%/0%/100% | 0%/0%/0%/100% | 0.0% | 0.000 | 11.4% |
| D0/C1 | RFULL | 8.00/8.00/8.00 | 7.48/7.45/7.44 | 1.06/1.09/1.08 | 0.45/0.47/0.47 | 1.06/1.09/1.08 | 0.43/0.44/0.44 | 0%/0%/0%/100% | 0%/0%/0%/100% | 0.0% | 0.000 | 12.1% |
| D2/C1 | R0 | 8.00/7.45/6.79 | 7.45/6.79/6.03 | 1.08/1.32/1.55 | 0.10/0.17/0.23 | 0.88/0.98/1.09 | 0.48/0.46/0.44 | 0%/0%/2%/98% | 0%/0%/13%/87% | 3.3% | 0.000 | 11.4% |
| D2/C1 | R2 | 8.00/7.95/7.93 | 7.24/7.17/7.16 | 1.52/1.54/1.56 | 0.23/0.24/0.25 | 1.07/1.06/1.06 | 0.44/0.44/0.43 | 0%/0%/0%/100% | 0%/0%/0%/100% | 0.1% | 0.000 | 12.5% |
| D2/C1 | RFULL | 8.00/8.00/8.00 | 7.23/7.22/7.20 | 1.56/1.58/1.59 | 0.24/0.25/0.25 | 1.08/1.08/1.09 | 0.41/0.44/0.43 | 0%/0%/0%/100% | 0%/0%/0%/100% | 0.0% | 0.000 | 11.7% |
| D1/C0 | R0 | 8.00/7.86/7.70 | 7.86/7.70/7.52 | 0.29/0.31/0.36 | 0.29/0.31/0.36 | 1.18/1.22/1.18 | 0.37/0.38/0.40 | 0%/0%/0%/100% | 0%/0%/0%/100% | 2.5% | 0.000 | 12.1% |
| D1/C0 | R2 | 8.00/8.00/8.00 | 7.81/7.82/7.81 | 0.37/0.37/0.37 | 0.37/0.37/0.37 | 1.20/1.17/1.22 | 0.38/0.39/0.38 | 0%/0%/0%/100% | 0%/0%/0%/100% | 0.0% | 0.000 | 11.3% |
| D1/C0 | RFULL | 8.00/8.00/8.00 | 7.81/7.82/7.83 | 0.37/0.36/0.35 | 0.37/0.36/0.35 | 1.19/1.19/1.22 | 0.38/0.39/0.38 | 0%/0%/0%/100% | 0%/0%/0%/100% | 0.0% | 0.000 | 11.0% |

Advanced Plays persist into Fights 2 and 3, but D1/C1 does **not** create strong three-fight attrition in this short-duel model: under R0 the focal fighter still averages 6.14 Spiritus after Fight 3 and records no material starvation. R2 restores almost every focal fighter to 6–8 before later fights and tracks RFULL closely, so +2 is too generous at this fight length/cadence. Recovery remains experimental; these rows do not define a breather or rest.

## P1 cell diagnostic fields

Every P1 cell in `results.json` includes Parry declarations and post-knowledge declarations; defensive-opportunity rate; rolled success; interruption/decline fractions; expected allow-Parry and Durch success chances; both fighters' Spiritus at accepted/declined decisions; Durch opportunities, declarations, declines, success, damage, and spend; compound spend; total spend; fight-end Spiritus buckets; and unused Spiritus at defeat. Declines are policy-classified. Compound records include opportunities, declarations, success, damage, spend, displaced alternatives, Spiritus at declaration, and early/late use.

## Matrix coverage and omissions

- Adaptive fresh-duel primary matrix: **144 cells**, the full 3 Skill × 2 Parry × 3 Durch cost × 2 compound cost × 4 starting-pool matrix.
- Perfect-information reduction: **21 cells**. It retains P1 at all three Skills and D0/D1/D2 with C1 at starts 8 and 3, plus one P0/D1/C1/start-5 control per Skill. P1/C0, starts 5/1, and most P0 cells were omitted because the adaptive full matrix already establishes their monotonic resource direction and the reduced run is only an equilibrium check.
- Edge start 0: **2 cells** at Skill 10, D1/C1, P0/P1.
- S1/S3 were not multiplied across the matrix. The prior report already establishes them as sensitivity variants; this experiment keeps S2 as requested.
- Exploratory HP carryover was omitted because it would add injury assumptions without helping isolate the resource question.
- Power Strike competition was skipped: the prototype has no sufficiently mature Guard/Chamber state model to represent it reliably.

## Artifacts and limitations

- All tactical rates depend on the transparent utility weights and softmax temperature. The response surface is more trustworthy as a direction-of-effect check than as a behavioral forecast.
- Generic d6+1 damage, HP 8, artificial attack mix, 50% soft-bind exercise rate, and 25% close-crossing exercise rate affect urgency and opportunity counts.
- Zornhau-Ort's pre-bind point threat remains uncertain. It, Nachreisen, and Pommel Strike remain free; any substitution toward them is a zero-cost policy artifact, not a recommendation to price them.
- Guards, Power Strike/Chamber competition, bind calibration, engagement geometry, and weapon profiles remain OPEN.
- Adaptive revelation lasts only within each fight. Spiritus is public. No recovery rule is canonized.

## Answers to the design questions

A. **Conditionally.** P1 remains viable after reveal at Skill 10 and under attacker depletion, but it is effectively displaced after reveal at Skill 18 with usable Spiritus. That high-Skill warning prevents a general 'P1 remains viable' conclusion.
B. **Pre-roll declaration matters most where Parry failure is a real gamble.** It materially restrains Skill-10 use; at Skill 14/18 it is insufficient by itself because Durchwechseln's success advantage is large.
C–D. **D1 is still the most promising candidate, with a high-Skill caveat.** D0 weakens scarcity; D2 suppresses more depleted-pool use but still cannot preserve high-Skill post-reveal P1 reliably. D1 produces both declarations and the intended gamble declines in the lower/equal band.
E. **Saving is favored when defender Skill is low relative to attacker Skill and/or the attacker is depleted.** Exact policy probabilities are tabulated above and in the response surface.
F–G. **C1 is the better candidate than C0 in this chassis.** It keeps compounds visible while preventing the near-automatic C0 Schielhau rate, though late-use results remain policy/urgency-sensitive.
H–I. Lower starting or observed attacker Spiritus increases conservation, unaffordability, and Basic-Parry attractiveness.
J–K. **R0 attrition is weak and R2 is too generous in this model.** R2 nearly converges to RFULL because average spend is below +2 per fight.
L–M. **Maximum 8 is tactically valued but operationally generous here.** Fresh fighters usually spend about 1–1.5 and R0 still leaves enough for advanced Plays after three fights. Longer fights or another competing expenditure are needed to tell whether 8 is a useful campaign reserve rather than effectively unlimited for this cadence.
N. AI utility, damage, Guards, bind/geometry, and weapon-profile artifacts remain unresolved and prevent canonical balancing conclusions.

## Recommended Next Decision

Retain **D1** and **C1** as the best next-test candidates, but do **not** accept P1 as universally healthy: it needs a high-Skill remedy or a broader cost/success model because post-reveal use collapses at Skill 18. Keep maximum Spiritus **8** provisional; it is promising as a reserve but too generous to validate with these short fights alone. Do not prioritize **R2 (+2)** as the candidate recovery cadence yet—it behaves almost like RFULL here. If retained, use it only as an upper-bound control while testing +1, longer fights, or a mature competing 1-Spiritus Power Strike. Do **not** update Atra Melee Design Packet v0.4 yet.

Seed: `8112026`. Trials: `{'fresh_per_cell': 3000, 'reduced_per_cell': 4000, 'sequences_per_cell': 5000}`. All mechanics and policy weights remain PROVISIONAL.

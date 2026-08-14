# Guard Play Bridge v0.1 Results

Status: **PROVISIONAL bounded Play-integration experiment; not canonical mechanics**

## Executive Result

Scheitelhau's initial Alber-breaking entry is historically secure but not independently mechanically distinct from Basic Cut in the current engine. It is therefore **DEFERRED UNTIL A NARROW CROWN CONTINUATION**, receives no Spiritus price, and gains no breaker modifier. Generic Basic Cross remains distinct from Crown.

Tutta cover-to-stretto is cleanly representable as a learned continuation: after a successful Tutta Basic Cross against an ordinary proactive Basic Cut at Wide measure, retain Crossing and change Wide to Close. It adds no roll, damage, attack, action restoration, grapple, disarm, or Pommel. T1 is recommended for Project review because the authored measure conversion is a meaningful one-effect enhancement and the 1-Spiritus cost preserves a live reserve decision.

## Scope and Preserved Baseline

The simulator reuses the current G1 named-guard harness, which imports `simulations/shared/provisional_longsword.py`. D1, C2, S2, P1, Cross/Beat, explicit contact/measure state, free before-or-after guard change, and the three-learned-Play cap are unchanged. Skill is 14; starting Spiritus is 8 or 3; each of the six cells contains 992 mirrored fights balanced across all 16 ordered Italian starting-guard pairs. This is behavioral micro-analysis, not guard balance.

No full Named Guard v0.2 matrix, guard-transition tuning, Parry DR, or unrelated Play redesign was run.

## Source Basis

- **Scheitelhau / Alber:** Pseudo-Peter von Danzig, Starhemberg Fechtbuch, Cod.44.A.8 (MS Cors.1449), anonymous gloss, 1452, ff. 24v.3-25r.2; confirming four-guard list f. 26v.3. The initial descending long-edge head cut and later Crown sequence remain separate phases.
- **Tutta Porta di Ferro:** Fiore dei Liberi, Getty MS Ludwig XV 13, 23v-a; concordant Morgan MS M.383, 12r-a and Pisani Dossi 18a-a. Vadi MS Vitt.Em.1324, 16v-a remains continuity/context for a separately named Iron Gate, not an automatic exact equivalence.

## Scheitelhau vs Alber — Initial Entry Viability

1. **Can it be meaningful by itself?** No, not with current authored state.
2. **Source-supported distinction from Basic Cut:** the opponent is in Alber and the action is the named strong descending long-edge head cut. Those facts identify the historical relationship but do not add a separate Atra outcome.
3. **Can current state express the distinction?** No. Ordinary attack line, point threat, damage, and a defender's generic Basic Cross do not supply a distinct initial-entry effect.
4. **Would implementation conflate Crown with Basic Cross?** Yes, if Crossing were assigned as the special effect now. The source's Crown is a specific defended continuation context.
5. **Would it require an invented breaker modifier?** Yes, unless it remained mechanically inert.
6. **Result:** **DEFER UNTIL CROWN CONTINUATION (S-C)**. Alber is historically audited but remains partially mechanically inert until that continuation is built. No price is assigned to a placeholder.

### Mechanical decomposition

| Item | Result | Classification |
|---|---|---|
| Before declaration | Opponent currently in Alber; actor has a normal longsword action | DIRECTLY SOURCE-ANCHORED |
| Initial historical action | Spring in with a strong descending long-edge head cut | DIRECTLY SOURCE-ANCHORED |
| Already Basic | Test, ordinary damage, defence menu, action cost, head-line fiction | ATRA STATE MAPPING |
| Learned substance | Alber recognition plus the defended Crown/point-sinking/winding/pressing/slicing decision tree | DIRECTLY SOURCE-ANCHORED |
| Existing distinct state | None without unsupported geometry or modifier | NOT JUSTIFIED |
| Later effects | Crown reception, sinking point, winding, pressing, slicing | DIRECTLY SOURCE-ANCHORED |
| Standalone learned card | Duplicates Basic Cut while consuming a Play slot | PROVISIONAL GAME ABSTRACTION; rejected for this prototype |

## Tutta Porta di Ferro — Cover to Stretto

1. **Exact trigger:** actor was in Tutta when declaring Basic Cross against an ordinary proactive Basic Cut; the normal pre-Parry Durchwechseln window resolves; Cross succeeds; Crossing exists at Wide measure; the chain has room and the actor can pay the candidate cost.
2. **State transition:** `Crossing/Wide -> retained Crossing/Close`.
3. **T0 vs T1:** identical except 0 versus 1 Spiritus at declaration.
4. **Extra roll:** none.
5. **Additional action:** none; the cover already spent the defender's action and it is not restored.
6. **Learned Play:** yes; it consumes one of the three chain slots.
7. **Retained Crossing:** justified as the minimal engine mapping of cover plus passing entry into stretto. It is a source-derived state mapping, not a claim about blade zone, pressure, damage, or control.
8. **Preferred provisional candidate:** recommend T1 for Project review; this report does not promote it to the governing baseline.

The v0.1 trigger excludes thrusts so it does not absorb Scambiar or downward Beat, and excludes Beat, Power Attack, learned cuts, and generic successful Parries. Pommel remains a separate downstream Play and is not implied historically by the Tutta passage.

## Deterministic Validation

All required cases pass: correct/wrong guard, success/failure, Cross/Beat, Durchwechseln interruption, T0/T1 spending, retained Wide-to-Close state, zero damage/extra attack/action restoration, learned-chain counting, cap rejection, downstream Pommel legality, ordinary cleanup, and modifier-free Scheitelhau deferral. The suite also asserts that no generic Cross is Crown and no automatic breaker benefit exists.

## Behavioral Micro-Test

| Cell | Tutta occ. | Cover opp. | Trigger Cross | Cont. opp. | Uses | Cont. S | Wide→Close | Retained C/C | Close exch./transition | Pommel opp./use | Learned / other | Chain cap | Fourth | Guard changes | Total S |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTROL S8 | 17.5% | 0.207 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000/0.000 | 2.891/2.891 | 0.7% | 0.000 | 3.722 | 3.351 |
| CONTROL S3 | 19.1% | 0.263 | 0.010 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000/0.000 | 2.575/2.575 | 0.3% | 0.000 | 4.131 | 1.734 |
| T0 S8 | 18.3% | 0.234 | 0.001 | 0.001 | 0.001 | 0.000 | 0.001 | 0.001 | 3.000 | 0.001/0.000 | 2.939/2.938 | 1.1% | 0.000 | 3.694 | 3.476 |
| T0 S3 | 18.0% | 0.248 | 0.010 | 0.010 | 0.006 | 0.000 | 0.006 | 0.006 | 4.333 | 0.006/0.004 | 2.613/2.607 | 0.3% | 0.000 | 4.114 | 1.877 |
| T1 S8 | 18.2% | 0.236 | 0.001 | 0.001 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000/0.000 | 2.751/2.751 | 0.9% | 0.000 | 3.663 | 3.227 |
| T1 S3 | 18.4% | 0.255 | 0.004 | 0.004 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000/0.000 | 2.590/2.590 | 0.3% | 0.000 | 4.123 | 1.785 |

### Aggregate comparison

| Model | Uses/fight | Declaration rate | Spiritus | Wide→Close | Pommel opp./use | Other learned Plays | Guard changes | Total Spiritus |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTROL | 0.000 | 0.0% | 0.000 | 0.000 | 0.000/0.000 | 2.733 | 3.926 | 2.542 |
| T0 | 0.004 | 63.6% | 0.000 | 0.004 | 0.004/0.002 | 2.772 | 3.904 | 2.676 |
| T1 | 0.000 | 0.0% | 0.000 | 0.000 | 0.000/0.000 | 2.670 | 3.893 | 2.506 |

### Conditional trigger decision check

The natural trigger is sparse because the inherited Skill-14 policy usually selects learned defence over Basic Cross. The following 1,000-trial cells isolate only the declaration decision after the exact Tutta/Cross/Wide trigger is already satisfied; they do not replace the mirrored-fight metrics.

| Model | Start S | Triggered trials | Declaration rate | Spiritus/trigger | Spiritus/declaration |
|---|---:|---:|---:|---:|---:|
| T0 | 8 | 1000 | 73.6% | 0.000 | 0.000 |
| T0 | 3 | 1000 | 73.6% | 0.000 | 0.000 |
| T1 | 8 | 1000 | 61.6% | 0.616 | 1.000 |
| T1 | 3 | 1000 | 50.7% | 0.507 | 1.000 |

### Chain distribution

- CONTROL S8: 0: 49.6%, 1: 40.6%, 2: 9.1%, 3: 0.7%
- CONTROL S3: 0: 56.0%, 1: 39.0%, 2: 4.7%, 3: 0.3%
- T0 S8: 0: 49.6%, 1: 39.6%, 2: 9.7%, 3: 1.1%
- T0 S3: 0: 55.7%, 1: 39.0%, 2: 5.0%, 3: 0.3%
- T1 S8: 0: 51.2%, 1: 39.1%, 2: 8.9%, 3: 0.9%
- T1 S3: 0: 55.9%, 1: 38.9%, 2: 5.0%, 3: 0.3%

**FREE-CLOSE WARNING:** T0 makes the authored conversion free and the policy declares it routinely when the narrow trigger appears. It should remain a comparison bound rather than the preferred provisional price.

T0 changes other learned-Play use by +0.039/fight from control; T1 changes it by -0.062/fight. These are policy-substitution observations, not causal balance estimates. The natural T1 cells produced too few successful triggering Crosses to declare the continuation in this seed, so their observed continuation Spiritus is zero; deterministic validation and the conditional-trigger check still show exactly 1 Spiritus per T1 declaration and a lower declaration rate under scarcity.

No cell records an unauthorized Close origin. CONTROL remains at zero Wide-to-Close transitions. Every Close state in T0/T1 descends from the authored Tutta continuation; subsequent Close-measure Crossings are consequences of already-entered measure, not a universal Step-to-Close action.

## Limitations

The one-step softmax policy values the authored Close opportunity with a transparent 0.25 base plus a small wounded-target term, then subtracts the existing reserve charge. It does not solve equilibrium play, model player preferences, or prove balance. Natural triggering Crosses are extremely sparse in this policy, so the conditional-trigger cells are a price-sensitivity diagnostic rather than a frequency forecast. Once entered, Close measure persists under the existing independent measure axis; contact still requires an authored Crossing and cleans or separates normally. The run is intentionally too small and narrow for guard win-rate conclusions.

## Durable Technical Results

Deterministic validation confirms the Project-authorized promotions: Tutta cover-to-stretto is a learned Play; no universal Close action exists; no automatic breaker modifier exists; and Crown remains distinct from generic Basic Cross. T0/T1 selection and the Scheitelhau future chassis remain unpromoted.

## Recommended Next Decision

A. **No.** Scheitelhau's initial Alber entry lacks enough independent substance to implement now.

B. No chassis or price is recommended for the initial entry alone.

C. **Run a narrow Crown-continuation experiment next.** It should specify the defended context without treating every Basic Cross as Crown.

D. **Yes.** Tutta cover-to-stretto is cleanly implementable with the existing Crossing and Wide→Close state.

E. **Prefer T1 for Project review; do not auto-promote it.** One Spiritus matches one meaningful state conversion and preserves reserve competition.

F. **No second roll.** The successful cover is the test; the continuation is deliberate state conversion.

G. **Yes.** It creates Close only through a named learned trigger and does not add a universal Close button.

H. The bounded policy shows no pathological displacement of other learned Plays, but T0 creates a routine free conversion warning; T1 imposes a visible Spiritus decision.

I. **Not yet ready for a meaningful Named Guard Rules v0.2 run.** The Italian bridge is ready, but Alber remains mechanically under-distinguished.

J. The exact remaining blocker is a narrow, audited Crown continuation (or another independently justified Scheitelhau state effect) that gives the Alber breaker entry mechanical substance without a generic modifier.

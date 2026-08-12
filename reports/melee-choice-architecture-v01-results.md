# Atra Melee Choice Architecture v0.1 Results

Status: **PROVISIONAL bounded architecture experiment and historical-transition investigation; not Named Guard v0.2 and not canonical mechanics.**

## Executive Result

**CB3 best preserves rational Cross/Beat choice, but it is only HEALTHY BUT REPERTOIRE-DEPENDENT and is not ready for automatic adoption.** Cross immunity creates a clear safety motive when D1 is known, affordable, and the defender lacks threatening point; Beat creates a state-stripping motive without any generic Open modifier. Yet Beat dominates repertoire-poor Cross whenever D1 is unavailable or already denied by threatening point. CB1 and CB2 each solve only one side of the motivation problem; CB0 remains a false choice without repertoire.

**GC1 (before-action only) is the clearest low-complexity commitment rule.** It preserves just-in-time entry but forces the actor to carry the chosen posture through the opponent opportunity after taking its benefit. GC2 creates preparation/telegraphing, but it retains immediate post-benefit shedding and after-action defensive staging. GC3 is not behavior-tested: the sources support broad Italian guard-to-guard movement and action-produced transitions, while no restrictive German pairwise graph is established. Encoding a sparse graph would teach an invented topology.

No canonical file, governing prototype, Play record, or design packet was changed. Named Guard v0.2 remains blocked pending Project adjudication and repair of the audit's separate repertoire/policy defects.

## Source-of-Truth Check

Git was clean at resumed Phase 0. The required Incentive Integrity Audit is present. The current dated governing register supersedes the packet's older mirrored-guard material for prototype work and explicitly classifies free before-or-after all-to-all switching as a provisional harness rule under warning. No material prompt/repository conflict remained. `simulations/shared/provisional_longsword.py` was inspected and not modified.

## Fixed Governing Baseline

Preserved: G1/action-light guards; universal Cut/Thrust/Cross/Beat; explicit Crossing/contact/measure; D1 at 1 Spiritus before the Basic-Parry roll; C2 at 2 Spiritus; S2; cap 3; Loaded Cut Damage Boon; P1 fixed 7 at 1 Spiritus with Committed and Counter-first; T1; no generic guard bonuses, random binds, universal Close, or breaker modifier. Crown C1/B3 was excluded.

## Incentive-Audit Problems Being Addressed

The audit establishes two Severity-3 architecture defects: repertoire-poor Cross/Beat converges after cleanup, while free before-or-after switching enables Donna offensive harvesting, after-action point-threat staging, and first-moment gate acquisition. Nachreisen, Zornhau-Ort, Alber, Frontale, and Winden defects were neutralized as evidence rather than repaired.

## Experiment A — Cross / Beat Candidates

The analysis decomposes Cross immunity and Beat-created Open as CB0-CB3. It compares multidimensional consequences; it does not infer health from observed choice frequency.

## Definition and Behavior of Open

Open is no named guard. It removes named-guard intrinsics, Loaded, threatening point, and guard gates while leaving every universal Basic action and defence legal. It adds no Boon, Bane, damage, accuracy, cancellation, or inability-to-defend modifier. Only a successfully resolved Beat in CB2/CB3 creates it. Failed or D1-interrupted Beats do not. Recovery at the next own activation is Open -> any legal guard, consumes the activation's guard-change allowance, and cannot be followed by a second voluntary switch.

## Cross / Beat Deterministic Outcome Vectors

At Skill 14, a resolved ordinary Parry succeeds with probability 0.700. With the current deterministic D1 reserve heuristic, D1 is argmax at S8 and S3 but not S1; at Skill 18 it remains argmax even at S1. A forced D1 branch replaces the defender's roll with the attacker's roll: at Skill 14 expected incoming d6+1 damage becomes 3.150 instead of 1.350 when the Parry roll occurs. Cross immunity prevents that substitution. A successful CB2/CB3 Beat creates Open with probability 0.700 in no-D1 cells.

| Case | Result |
|---|---|
| A — no D1, no repertoire | CB2/CB3 Beat adds guard stripping at identical defence probability; Beat dominates when the target has value to strip. CB0/CB1 remain false choices. |
| B — known affordable D1, nonthreatening point | Under CB3, Cross avoids the D1 branch; Beat trades higher expected damage for a 0.700 chance to strip the attacker. This is a genuine non-scalar choice. |
| C — threatening defender point | Existing point threat denies D1 for both forms. CB3 Beat again dominates repertoire-poor Cross when stripping has value. |
| D — Tutta T1 repertoire | A successful source-compatible Cross creates a 0.700 T1 opportunity independent of D1 safety; Beat cannot. Repertoire restores a Cross motive. |
| E — valuable attacker guard | Open removes Loaded/P1/Scambiar from Donna; threat/D1 denial from Mezza; threat/D1 denial/Absetzen from Pflug. |
| F — Open or low-value guard | The added Beat payoff collapses to zero; without D1 or repertoire the choice becomes false again. |
| G — depletion | At Skill 14 the deterministic D1 motive disappears at S1/S0; at Skill 18 it survives S1 and disappears at S0. Beat therefore grows more attractive as D1 becomes unavailable or reserve heuristics decline it. |
| H — hidden repertoire | Mechanical outcomes do not change, but an unrevealed defender cannot condition on D1. No Bayesian prior exists, so opacity cannot be quantified without invention. |

## Cross / Beat Controlled Results

Each reported branch-forced cell used 1000 trials at seed `12082026`. Empirical rates validate the exact vectors; they are not player choice frequencies. Maximum absolute error across cancellation/Open/Crossing rates was 0.038; maximum absolute mean-damage error was 0.179.

The controlled result is structural: CB1 creates only a Cross motive in eligible D1 states; CB2 creates only a Beat motive when state can be stripped; CB3 combines them, but the trade disappears in common D1-denied/depleted states unless Crossing repertoire is present.

## Cross / Beat Policy-vs-Rules Analysis

The governing policy assigns identical Cross and Beat utilities, so softmax/tie splitting is not evidence. This experiment uses deterministic D1 argmax and branch-forced Monte Carlo. The stored softmax declaration probability is reported only as a policy sensitivity. Guard-stripping value is a vector of actual lost states/gates, not an invented scalar bonus.

## Experiment B — Guard Commitment Candidates

GC0-GC2 were tested independently at baseline Cross/Beat with a reduced Italian roster. The six-activation script chooses offensive, defensive, or gate goals and follows what each timing rule legally permits. It has no utility constants or softmax. GC3 was research-gated and not behavior-tested.

## Guard Harvesting Scenarios

### Scenario 1 Donna Offensive Harvesting

- **GC0:** Loaded Cut, then after-action Mezza; Donna downside is shed before the opponent acts.
- **GC1:** Loaded Cut, no post-action switch; actor remains Donna through the opponent opportunity.
- **GC2:** Loaded Cut, then after-action Mezza; immediate shedding remains legal.
- **GC3:** Not behavior-tested; Italian dense interpretation would reproduce GC0 topology.

### Scenario 2 Donna Just In Time Entry

- **GC0:** Mezza -> Donna before action -> Loaded Cut; actor must remain Donna afterward because the allowance was used.
- **GC1:** Same as GC0: just-in-time entry remains, but post-benefit exposure is mandatory.
- **GC2:** Cannot enter before action; establish Donna after an earlier activation, expose/telegraph for one opponent opportunity, then use Loaded Cut.
- **GC3:** No defensible restrictive topology.

### Scenario 3 Threatening Point Staging

- **GC0:** Useful action -> Mezza after action -> point threat before opponent.
- **GC1:** No after-action acquisition; Mezza must be chosen before the useful action and retained.
- **GC2:** Useful action -> Mezza after action remains legal; defensive staging persists.
- **GC3:** No defensible restrictive topology.

### Scenario 4 Guard Gate Staging

- **GC0:** Enter Tutta/Pflug after acting and hold the gate for the expected attack.
- **GC1:** Enter before the actor's useful action and remain through the expected attack.
- **GC2:** Enter after acting; immediate defensive staging remains legal.
- **GC3:** Action-produced movement is supportable, but free adjacency restriction is not.

### Scenario 5 A B A Loop

- **GC0:** Donna benefit -> Mezza after -> Donna before next benefit: two-activation harvesting loop.
- **GC1:** Donna must remain through the opponent; a Donna-Mezza-Donna loop requires sacrificing an intervening offensive activation.
- **GC2:** Donna -> Mezza after; next activation cannot return before acting, so Donna benefit is delayed to a third activation.
- **GC3:** Not behavior-tested.

### Scenario 6 Open Recovery

- **GC0_GC1_GC2:** Start-of-activation Open recovery consumes the voluntary allowance; no second before/after switch is legal.
- **GC3:** Open -> any is an explicit experimental exception, not historical adjacency; it would bypass topology by design.

## Guard Commitment Controlled Results

| Model | Changes/fight | Before | After | A→B→A | Mean dwell | Loaded same-activation harvest | Defensive after-action staging | Pure staging/change |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GC0 | 4.789 | 2.981 | 1.808 | 2.141 | 1.036 | 68.8% | 29.2% | 26.9% |
| GC1 | 3.825 | 3.825 | 0.000 | 1.497 | 1.244 | 56.3% | 0.0% | 0.0% |
| GC2 | 4.714 | 0.000 | 4.714 | 2.150 | 1.050 | 0.0% | 65.7% | 9.7% |

GC1 eliminates post-action switching in the script and therefore eliminates after-action defensive staging and immediate post-benefit shedding. It does not eliminate same-activation Donna entry; instead it couples that benefit to subsequent exposure. GC2 eliminates same-activation pre-entry but preserves after-action defensive staging and allows a fighter already in Donna to use Loaded and immediately leave.

## Benefit-Exposure and Telegraph Metrics

| Model | Exposure before benefit | Exposure after benefit | Either side | Mean telegraph interval | Loaded telegraph | Gate harvest |
|---|---:|---:|---:|---:|---:|---:|
| GC0 | 70.2% | 42.4% | 97.8% | 0.300 | 0.257 | 80.4% |
| GC1 | 72.0% | 59.2% | 100.0% | 0.456 | 0.615 | 77.1% |
| GC2 | 96.8% | 22.0% | 96.8% | 0.443 | 0.815 | 77.6% |

Dwell is reported in opposing activation opportunities, not as a health target. The important change is coupling: GC1 makes a guard's offensive benefit carry post-benefit exposure; GC2 moves more loaded use behind preparation but still lets the actor shed the posture immediately after use.

## Transition-Graph Historical Research

The research used repository-audited locators and checked the current transcription-facing pages: [Pseudo-Peter von Danzig transcription](https://www.wiktenauer.com/wiki/Pseudo-Peter_von_Danzig), [Fiore sword-in-two-hands concordance](https://www.wiktenauer.com/wiki/Fiore_de%27i_Liberi/Sword_in_Two_Hands), and [Vadi transcription](https://www.wiktenauer.com/wiki/Philippo_di_Vadi). Witness statements, editorial translations, geometry, and Atra abstraction remain separated in the YAML artifact.

## German Candidate Transition Map

Pseudo-Peter von Danzig's Ochs/Pflug material supports four hangings and eight Winden with cuts, thrusts, and slices from them. That is strong action-produced mobility evidence, but it neither names a free Ochs↔Pflug positioning edge nor connects Vom Tag and Alber into a voluntary graph. Safe restrictive pairwise edges: **0/12**; the graph is disconnected.

## Italian Candidate Transition Map

Vadi, f. 11r, explicitly permits going from guard to guard with ordinary steps. Expanding that general rule over the reduced roster yields 12/12 directed pairs (density 1.0), which is historically meaningful but useless as a commitment topology. Fiore separately supplies action-produced Frontale→Dente di Zenghiaro, Mezza return-to-Mezza, and Tutta cover→stretto. These do not justify selective voluntary adjacency omissions.

## Transition-Graph Evidence Quality

The German sparse graph is unsupported and disconnected. The Italian direct movement principle is nearly/all-to-all and therefore imposes no path commitment. A one-edge-per-activation restriction would either block ordinary movement without evidence or grossly exaggerate transient positions reached during a cut or winding. GC3 is classified **NOT SUPPORTABLE as a restrictive finite-state graph**.

## Action-Produced vs Voluntary Transitions

The evidence favors actions and recoveries: Winden from hangings; Frontale's retreat/fendente into Dente; Mezza's beat-return-recovery; Tutta's cover into stretto; and general cut recovery. These relationships can teach historical movement without pretending that every named posture is a mandatory one-activation node.

## Limited Cross/Beat × Commitment Interaction Check

Only CB0/CB3 × GC1/GC2 was checked. In every cell the explicit start-of-activation Open recovery reaches one legal guard, consumes the allowance, clears stale intrinsics, and blocks both a second before- and after-action switch. No double-switching or state leakage occurred. Under either timing rule, Open recovery bypasses topology only as the expressly authorized experimental exception. No broader matrix was run.

## Regression Results

All deterministic assertions pass: CB0 reproduction; Cross immunity only in CB1/CB3; Open only after successful CB2/CB3 Beat; failed/interrupted Beat no Open; ordinary Crossing and Beat separation; no generic modifiers; Open has no intrinsics/gates but retains universal Basics; recovery consumes the change; GC0/GC1/GC2 timing; GC3 rejects unsourced jumps; D1=1, C2=2, cap=3, P1=1/fixed-7/Committed/Counter-first, T1=1; no Crown or generic guard bonus.

## Instrumentation Findings

The inherited named-guard metrics count form declarations and generic Basic Parry choices on separate paths, so raw choice totals require care. Existing guard occupancy records exchange slots but cannot derive exposure-before/after, telegraph interval, pure staging, or action-adjacent transition motives. The new harness records those explicitly. Current softmax constants (Donna before value, threatening-point after value, and 0.09 friction) remain policy artifacts and were not used to judge timing health.

## Candidate Comparison

### Cross / Beat

| Candidate | Cross D1 | Beat D1 | Beat Open | Generic Cross benefit | Repertoire dependence | Reason to Cross | Reason to Beat | Common dominance state | Complexity | Historical interpretability | Severity/problems | Recommendation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CB0 | exposed | exposed | no | none | high | authored Crossing repertoire only | separation identity only | false choice without repertoire | lowest | current source-facing forms | Severity 3 false choice | reject as architecture fix |
| CB1 | immune | exposed | no | none | medium | D1 safety or repertoire | separation only | Cross dominates when D1 is active; false otherwise | low | immunity is Atra abstraction | one-sided motive | insufficient alone |
| CB2 | exposed | exposed | yes | none | high | repertoire only | strip valuable guard | Beat dominates no-D1 valuable-guard states | low-medium | Open is conservative Atra state | one-sided motive | insufficient alone |
| CB3 | immune | exposed | yes | none | material | D1 safety or repertoire | strip guard when worth exposure | Beat dominates when D1 denied/depleted and no repertoire | medium | legible Atra risk split | threatening-point/depletion warning | best for Project review; no adoption |

### Guard commitment

| Candidate | Timing | Topology | Post-benefit exposure | Pre-benefit telegraph | Offensive harvesting | Defensive staging | Gate harvesting | A→B→A | Bookkeeping | Historical abstraction | Educational value | Source support | Recommendation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GC0 | before OR after | all-to-all | conditional/easily shed | usually none | high | high | high | easy two-activation loop | low | harness abstraction | low commitment clarity | provisional only | fails audit target |
| GC1 | before only | all-to-all | mandatory after offensive benefit | little before; clear after | entry remains but coupled | no after-action staging | must be held through attack | costs exposure/intervening action | lowest | simple timing abstraction | clearest take-benefit/accept-posture lesson | no historical topology claim | preferred Project-review rule |
| GC2 | end only | all-to-all | immediate shedding remains | one interval for newly prepared action benefits | lower same-turn entry | high | high after-action staging | delayed offensive return | low | simple timing abstraction | preparation is visible | no historical topology claim | useful sensitivity, not preferred |
| GC3 | before OR after | researched edge | unknown | topology-dependent | not tested | not tested | not tested | not tested | high | would be pseudo-historical if sparse | action edges could teach, adjacency would mislead | no defensible restrictive graph | do not implement |

## Project-Review Recommendations

Recommend **CB3 for further Project review**, explicitly accepting that foundation-level Cross remains repertoire-dependent outside active D1 risk. Recommend **GC1 before-action only** as the minimum commitment architecture: it has the lowest overhead and most directly enforces “take the benefit, accept the posture.” Do not implement GC3. Preserve historically described action-produced transitions as future Play/action aftermath rather than voluntary graph edges. These are recommendations, not promotions.

### Required Cross / Beat Answers

A. **Yes.** CB0 is genuinely false without useful Crossing repertoire.  
B. **Only conditionally.** CB1 solves the active-D1 state but not D1-denied/depleted states.  
C. **Only conditionally.** CB2 gives Beat value but leaves Cross repertoire-only and often dominated.  
D. **Best of the set, not complete.** CB3 creates a real trade in its key state.  
E. Cross is rational under CB3 for D1 safety or useful authored Crossing repertoire such as T1.  
F. Beat is rational when the attacker has a valuable named state/gate and D1 exposure is absent, acceptable, or unaffordable.  
G. **Yes, absent repertoire and meaningful contact value.**  
H. **Yes.** Threatening point already denies D1, making Beat safe and superior when stripping matters.  
I. **Yes in those states.**  
J. **Potentially a strength as advancement architecture, but a defect if both Basic forms must be independently compelling to novices.** Project intent must decide.  
K. **Yes.** Open matters through state/gate removal without numeric debuffs.  
L. **Meaningful but bounded.** Donna/Mezza/Pflug lose real access for one opponent opportunity; recovery prevents prolonged lockout. No evidence here shows excessive damage punishment.  
M. It adds bluff/revelation potential but is currently more opaque than modelled; no prior exists.  
N. **No candidate is ready for adoption on this experiment alone.**

### Required Guard Commitment Answers

A. Post-action switching causes essentially all immediate defensive staging and lets an already-benefited Donna user shed exposure.  
B. Pre-action switching causes same-activation Donna entry and first-moment offensive gate acquisition.  
C. **GC1 best solves the main coupling problem with minimal overhead.**  
D. **GC2 creates real preparation/telegraphing for action-time benefits.**  
E. **Yes.** GC2 still permits immediate post-benefit shedding and after-action defensive staging.  
F. GC1 does not appear rigid in this micro-model; GC2 can delay a desired offensive action by an activation.  
G. GC3 was not behavior-tested because no defensible restrictive graph exists.  
H. **No, not as a sparse adjacency graph.**  
I. Italian evidence is too dense/general to matter.  
J. German restriction would be too sparse and pseudo-historical.  
K. Not from the available voluntary-edge evidence.  
L. **Yes.** Action-produced transitions are much better supported.  
M. In principle, authored action aftermath plus a simple timing rule is preferable to a restrictive graph.  
N. **GC1.**  
O. **GC1.**

## Blockers Remaining Before Named Guard v0.2

Project adjudication of CB3's repertoire dependence and GC1 timing remains first. Separate audit blockers then remain: Nachreisen gate/chassis, Zornhau-Ort ghost value, Alber and Frontale incentive vacuums, inactive Winden, incomplete active guard repertoire, and unsupported policy constants. Crown C1/B3 remains candidate-only and cannot be used as an Alber solution here.

## Exact Next Milestone

After Project architecture adjudication, run **Melee Repertoire Integrity Repair v0.1**: repair or explicitly neutralize the known Nachreisen, Zornhau-Ort, Alber, Frontale, and Winden/repertoire blockers under the selected CB/GC architecture, with deterministic motivation checks before any Named Guard v0.2 balance matrix.

## Final Project-Review Output

1. **CB3** best preserves rational choice, but only as a repertoire-dependent candidate.  
2. **Yes.** Beat→Open works through state/gate removal without another combat modifier.  
3. It can be an advancement strength, but is a foundation-level defect unless the Project explicitly accepts that progression shape.  
4. **Yes in the active-D1/nonthreatening state; not universally.**  
5. **Yes for repertoire-poor Cross:** threatening point removes Beat's D1 risk.  
6. **GC1 before-action only.**  
7. **No restrictive source-grounded graph is viable.**  
8. No; the Italian reading collapses to all-to-all and the German reading is unsupported/sparse.  
9. **Yes.** The evidence much more strongly favors transitions as action consequences and recoveries.  
10. Minimum architecture for Project consideration: CB3 plus GC1, with no generic Open modifier and no voluntary transition graph.  
11. Exact next Codex milestone: Melee Repertoire Integrity Repair v0.1 under the adjudicated architecture.  
12. **Yes. Named Guard v0.2 remains blocked.**

Stop for Project adjudication.

## Validation

Seed `12082026`; 1000 branch-forced trials per Cross/Beat cell; 1000 scripted guard micro-fights per GC0-GC2 model. Deterministic regression suite: **PASS**. No full balance grid or win-rate interpretation was performed.

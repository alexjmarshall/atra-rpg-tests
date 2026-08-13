# Integrated Full-Duel Melee Cleanup / Incentive Audit v0.1 — Results

## Executive Result

**STOP FOR PROJECT ADJUDICATION — ONE SEVERE INTEGRATION HOLE, NO BIND-KERNEL REOPENING.** The governing H3 ordinary-bind kernel is coherent under exact branches and 30,000 fixed-seed duels. Basics, Hart/Weich, Fühlen, D/M, Winden, Counter, Power, and Zornhau retain distinct reasons. Cap 3 is an emergency ceiling, not routine truncation. No hidden Hart/Weich, second action, ordinary Favored/Unfavored, stale Crossing, post-mortem opportunity, Spiritus underflow, or chain bypass occurred.

The blocking issue is **T1 / Close integration**, not H3. T1 is raw-engine legal while the attacker H3 Rejoinder is open, but no governing ordering says whether it precedes, interrupts, or follows that Rejoinder. In D13, 2,589 such owner-qualified raw opportunities produced 0 policy declarations because resolving the Rejoinder/pass sequence normally cleared contact first. The authoritative shared engine also has no Close consumer. This is a **SEVERE E. MISSING REPERTOIRE CONSUMER / INTEGRATION CONFLICT** under the task’s criterion that a learned Play must have a concrete reason over its nearest Basic.

Three pure runtime omissions were reproduced and repaired without changing any governing cost, roll, damage die, state, or incentive rule: dead-actor declaration gates; Loaded Cut damage-mode integration; and executable D1 replacement resolution.

| System / Mechanic | Result | Severity | Recommendation |
|---|---|---:|---|
| Basic Cut | Distinct through Loaded, Power, authored Upper, Zornhau exposure | none | preserve |
| Basic Thrust | Same base output; avoids cut-only responses and reaches thrust compounds | none | preserve |
| Basic Cross | Hart accuracy and repertoire/geometry access | none | preserve |
| Basic Beat | Denies the whole Crossing continuation tree; Open is secondary | none | preserve |
| Counter | HP-sensitive damage trade; 13.2% double defeats in D3 | watch | preserve; do not broaden |
| Open | Real guard-state stripping, but 0 direct policy exploitations in tested duels | watch | retain; audit with D1/gates during Close pass |
| Hart | Higher cancellation; striker first after decline | none | preserve |
| Weich | Lower cancellation; defender first after decline | watch | preserve its Winden/escape niche |
| Fühlen | Damage-strong at 3S+, avoidable at low reserve/skewed prior | watch | preserve 1S |
| Duplieren | Correct-read Booned Cut beats flat Winding accuracy | none | preserve 2S |
| Mutieren | Correct-read Booned low Thrust plus threat | none | preserve 2S |
| Upper Winding | Read-free flat attack, Ochs/threat, reciprocal miss | none | preserve 2S |
| Lower Winding | Distinct Lower entry and clean L2 transition | none | preserve 2S/L2 |
| Bind Initiative / pass | Sequencing clean; no exclusive bonus | none | preserve |
| Chain cap 3 | 2.24% D4 and 1.78% D12 block rate | none | preserve |
| Spiritus max-8 test baseline | Meaningful short-duel depletion without blanket lockout | watch | preserve pending longer-rest cadence |
| Power | Kill certainty at HP ≤7 versus 1S/Committed exposure | none | preserve |
| Nachreisen | Unique Preparation/Recovery windows and Booned attack | watch | preserve; add natural trigger coverage later |
| Zornhau | Lower defence accuracy than Hart Cross; threat/local Ort upside | none | preserve local semantics |
| Ort | Strong but relation-gated intrinsic continuation | watch | preserve pending local adjudication |
| T1 | 2,589 owner-qualified engine opportunities, 0 conversions; ordering/consumer absent | **severe** | next narrow milestone |
| Ochs | Threatening point, D1 denial, Winding aftermath | none | preserve |
| Pflug | Threatening point and Lower Winding aftermath; often transitions to Ochs | watch | preserve |

## Source-of-Truth Check

The audit began on clean `main` at `ca86d85b4753302d598e9b745aa5b1e7a50347ad`. AGENTS.md, the current packet, governing register/YAML, H3 integration report/JSON, Upper/Lower Winden v0.3, Hart/Weich Upper Winden v0.2, General Bind v0.1, Melee Repertoire Integrity Repair v0.1, Crossing/Bind, Bind Continuations, mechanical vocabulary, Incentive Integrity, guards, Spiritus, chain, shared selector, shared engine, current legality, information views, and cleanup were read. The packet and historical Play records were not edited.

## Pre-Audit Regression Baseline

| Check | Pre-audit result |
|---|---:|
| Melee Repertoire Integrity Repair | 81/81 PASS |
| General Bind historical/candidate | 75/75 PASS |
| Hart/Weich Upper Winden historical | 82/82 PASS |
| Upper/Lower Winden historical | 68/68 PASS |
| H3 governing | 129/129 required assertions PASS |
| Full unittest discovery | 142 tests PASS |
| Repository validator | 114 records; 0 errors; 39 warnings |
| Grammar validator | 0 errors; 16 informative findings |

The control was sound; the audit stop condition was not triggered.

## Authoritative Duel Harness

`simulations/integrated_full_duel_melee_v0_1/simulate.py` calls `simulations.shared.provisional_longsword.CurrentEngine` for declarations, legality, tests, damage, Cross/Beat, H3 Rejoinder, D/M, Winden, pass, Disengage, Zornhau/Ort, Counter, Power, guard recovery, T1 legality, and cleanup. It does not copy H3 resolution rules.

The harness adds only round ordering, persistent HP/Spiritus/guards, exchange boundaries, transparent policies, fixed-seed dice, metrics, and report serialization. Actions refresh once per round; learned chain resets per exchange; retained Crossing follows the existing one-boundary retention behavior. Exact local branches use full d20/d6 enumeration. Multi-exchange results use seed `13082026`, 2,000 duels per scenario, and a conservative worst-case 95% binomial half-width of ±2.19 percentage points.

## Information-Visibility Audit

Policies receive immutable `PolicyView` values: public HP/Spiritus/guards/point state, public Crossing/height/measure/opportunity, own repertoire/action, own pressure, purchaser-only revealed pressure, public history, chain count, and legal options. They receive no engine reference, hidden opponent pressure, debug relation, future dice, or raw unexposed roll.

Deterministic tests prove opponent pressure is Unknown before Fühlen, own pressure is visible to its owner, public height is visible, Fühlen changes only the purchaser’s view, and historical adaptation uses public `pressure-revealed:*` events. Across all duels: 0 information leaks and 0 ordinary Favored/Unfavored writes.

## Policy Families and Objectives

- `survival`: O3/O6; favors Beat or Hart Cross, conserves 2S.
- `bind`: O1/O2; favors Cross, buys Fühlen only when it can still fund a 2S continuation, and uses legal Winding.
- `temporal`: O2/O4; uses Power and Counter at HP-sensitive nodes.
- `conserver`: O5 subject to survival; preserves 4S and declines premium branches.
- `adaptive`: O4; same bind priorities but updates pressure guesses only from public prior reveals.

No universal utility constant or opaque learner was used. Policy frequencies are evidence about those named priorities, not equilibrium claims.

## Scenario Matrix

| ID | State/loadout | Intended question | Key result |
|---|---|---|---|
| D1 | 8HP/8S, Skill 14, L0 mirror | Basics only | 6.76 rounds; 67.3% no-damage exchanges |
| D2 | Donna L0 mirror | Beat/Open + Power | Power 3,892 declarations; Open no direct exploit |
| D3 | temporal mirror | Counter | 13.2% double defeat; Counter bounded but dangerous |
| D4 | L2 mirror, Upper | H3/Winden | 3.51 rounds; cap blocked 101/4,505 binds |
| D5 | L3 vs L2 | D/M vs Winden | A 57.45%; policy/loadout evidence only |
| D6 | L4 mirror, adaptive/bind | full German | 50.4/49.6; Unknown geometry drove D/M, no Winden |
| D7 | Zornhau user vs forced Basic Cut | Zornhau coexistence | 6,662/6,662 opportunities used; 1,415 Ort |
| D8 | Donna L1 vs L2 | Power vs bind | A/B/double 32.9/56.35/10.55%; policy-specific |
| D9 | defender 1HP | survival | 2.83 rounds; urgency changes Beat/Cross mix |
| D10 | 2S vs 1S L4 | low reserve | premium bind use collapses; Basics remain |
| D11 | L4 mirror, Unknown | no fallback | 4,330 Unknown; 0 Winding; clean D/M/decline |
| D12 | L2 mirror, authored Lower | L2 | 4,389 Lower; 5,523 Windings; 78 cap blocks |
| D13 | Tutta/T1 state | T1 ordering/value | 2,589 owner-qualified opportunities; 0 declarations |
| D14 | Winden vs none | knowledge asymmetry | 1,720 Windings; repertoire materially matters |
| D15 | Skill 10 vs 14, L4 | asymmetry | A/B 26.8/73.2; no accounting failure |

All start at Wide unless stated; only D12 authors Lower and only the authored Upper scenarios write Upper. No fabricated global height distribution is claimed.

## Basic Cut vs Thrust

At equal Skill, ordinary Cut and Thrust share the flat d20 success and d6+1 damage distributions. Both therefore retain the same base expected damage and kill curve. Their rational distinction is response/repertoire topology: Cut can be Loaded, Power, Upper-authoring, Zornhau/Schielhau-facing, and Committed; Thrust avoids cut-only defenses and feeds Absetzen/Scambiar interactions. Neither needs a numeric parity patch.

At Skill 14, a normal attack has 70% success and 3.15 expected declaration damage. A Loaded Cut has the same accuracy but 4.394 expected declaration damage; Power has 4.9 expected declaration damage and kills HP 1/4/6 targets on 70% of declarations but cannot kill fresh 8HP.

## Basic Cross vs Beat

Beat retains a concrete reason: it cancels and denies the attacker Rejoinder, D/M, Winden, retained threat, and reciprocal short Krieg. Cross retains a concrete reason: Hart has higher immediate cancellation and Crossing enables owned repertoire/geometry.

At matched Skill 14, Hart Cross cancels 91%, while Weich Cross and Beat cancel 70%. With no bind repertoire, expected incoming damage is 0.405 after Hart Cross versus 1.35 after Beat. Against a correct D/M conversion it becomes 4.131 after Hart Cross versus 1.35 after Beat; against decline→flat Winding it is 3.271 versus 1.35. Thus neither dominates: attacker repertoire flips the survival preference. The floated “failed Beat leaves defender Open” is not needed to restore a Beat motive and was not implemented.

## Open Payload

Open is not a numeric debuff. It removes named-guard intrinsics, Loaded, point threat, and guard gates until recovery. That can concretely reopen D1 or deny a guard gate if an opponent receives an opportunity before recovery. In the bounded policy duels, Open was created thousands of times but directly exploited 0 times; most surviving fighters recovered their prior named guard before acting. Classify **WATCH / narrow contextual value**, not a proven ghost and not a reason to modify Open yet.

## Counter

Counter retains the HP/urgency niche: it accepts incoming damage for reciprocal damage, resolves first against Committed attacks, and can cancel Power by removing its actor. D3 selected Counter for 22.63% of legal defensive opportunities and produced 13.2% double defeats. It did not dominate Cross/Beat and remains hazardous at low HP.

## Hart vs Weich

Hart’s exact cancellation advantage over flat Beat/Weich is +25/+24/+21/+9 percentage points at Skills 10/12/14/18. Its cost is strategic: after decline the striker acts first. Weich is weaker at the initial test but assigns the defender first ordinary bind opportunity. Therefore Hart is best for immediate survival or when the defender lacks Winden; Weich retains a niche when the defender can convert first opportunity, wants to deny striker-first Winding, or values reciprocal offence. Neither is universally dominated. Full-duel policies favored Hart under survival/bind objectives, but that is objective-dependent rather than a Nash claim.

## Fühlen

At Skill 14, correct D/M deals 4.095 expected damage after a successful Cross. Best-blind expected damage is 3.276 at 20/80 priors, 2.457 at 40/60, and 2.048 at 50/50. Fühlen buys the gap for 1S but requires reserve 3 to fund Fühlen+D/M; reserve 2 forces blind or decline. D4 purchased 3,927 of 4,183 legal Fühlen opportunities (93.88%) under the damage-oriented policy, while conserver/low-reserve policies skipped it. It is damage-strong, not universally mandatory.

## Duplieren / Mutieren

Correct D/M has a Booned attack at the same 2S/one-chain price as flat Winding. That is its concrete reason over Winding. Duplieren adds the high Cut branch; Mutieren adds low-opening Thrust and threatening point. Wrong reads correctly spend 2S/one chain and deal zero. Blind reading is rational at skewed priors or reserve 2; Fühlen is rational at uncertain priors and reserve 3+.

## Decline vs Winden

Decline conserves 2–3S and allocates first ordinary opportunity by Hart/Weich. Winden is the read-free damage/threat conversion when authored height, knowledge, initiative, 2S, and chain room exist. Unknown height gives no fallback. Decline/pass/Disengage remain rational when geometry, resources, or repertoire do not support a premium continuation.

## Upper / Lower Winden

D4 Upper and D12 Lower have nearly identical cadence: 3.51 versus 3.46 rounds and 4.55 versus 4.50 exchanges. Lower correctly produces Pflug and, on miss, changes Lower→Upper and Pflug→Ochs before transferring opportunity. D12 recorded 5,523 Winding declarations, including the authored Upper responses after Lower misses. No repetitive-state or cleanup pathology appeared.

## Short Krieg / Chain Cap

At Skill 14 and enough Spiritus, exact repeated flat Winding yields 1.39 expected declarations, 97.3% probability of a hit by three, and 2.7% probability of reaching the cap after three misses. Integrated block rates were 2.24% of D4 Upper crossings and 1.78% of D12 Lower crossings. Cap 3 is functioning mostly as a runaway ceiling.

## Spiritus Multi-Exchange Economy

Full-bind D4 ended with mean 4.16S/4.29S after only 3.51 rounds; D5 ended 4.55S/4.69S. Low-reserve D10 used Basics rather than underflowing or faking premium declarations. The max-8 baseline supports several learned choices but makes repeated Fühlen+2S continuations consume roughly half the reserve in a short duel. It is neither plainly abundant nor plainly scarce; rest cadence remains outside this audit.

Concrete shadow prices: at reserve 2, 1S Fühlen blocks the 2S D/M it is meant to inform; a 2S Winding at reserve 3 leaves only 1S and blocks another Winding/D/M; a 3S Fühlen+D/M package at reserve 4 leaves 1S and eliminates another premium branch.

## Committed / Power / Nachreisen

Power remains worth using for fixed-7 kill certainty at target HP ≤7, but pays 1S, forbids attacker continuations, and exposes Counter-first cancellation when wounded. Ordinary Loaded Cut preserves reserve and continuation flexibility. D2 declared Power 3,892 times under the temporal policy.

Repaired Nachreisen remains mechanically distinct: Preparation and Recovery are target-only Committed windows, cost 1S/one chain, and make a Booned normal-damage attack. Preparation competes with flat immediate Counter; Recovery uniquely attacks after a Committed miss. Natural Nachreisen triggers did not arise in the bounded policy pairings often enough for frequency claims, so its status is **NARROW BUT DISTINCT / WATCH**, not dominated.

## Zornhau Coexistence

D7 forced the shared qualifying descending-Cut node: Zornhau was chosen on all 6,662 legal opportunities, and 1,415 Favored local results converted to Ort. This is branch/policy evidence, not proof that Zornhau should always be chosen. Hart Cross has superior defensive accuracy; Zornhau spends a learned entry but establishes threat, denies D1, and can produce local Ort/Winding. Ordinary Cross spends no entry and opens H3 geometry/Rejoinder. Local Favored/Unfavored never contaminated ordinary H3 state.

## T1 / Close Repertoire

T1 can pass raw engine legality during the open H3 Rejoinder, changing Wide→Close without closing that Rejoinder. The governing documents do not author which insertion has priority. The normal loop resolves the attacker Rejoinder first; D13 therefore produced 2,589 owner-qualified raw T1 opportunities and 0 declarations. Even if ordered, no authoritative shared-engine Pommel/Close consumer currently converts the state.

Classification: **SEVERE INTEGRATION CONFLICT / MISSING REPERTOIRE CONSUMER**. Do not invent a generic Close bonus or silently reorder H3. Project must choose the narrow timing and consumer boundary.

## Guard Identity

Ochs and Pflug are meaningful through threatening point/D1 denial and authored Winding aftermath, not generic bonuses. Donna remains meaningful through Loaded/P1. Tutta is incentive-deficient because T1/Close is blocked. Alber and Frontale remain documented out-of-scope repertoire gaps. GC1 recovery and action-produced transitions behaved without double change or stale point state.

## Crossing / State Cleanup

The deterministic suite covers hidden/revealed pressure, D/M cleanup, two passes, Winding hit, L2 miss, cap reset, exchange reset, Disengage, Open, Loaded/Committed, Zornhau/H3 isolation, point threat, and measure preservation. Across 30,000 duels: 0 stale cleanup failures, 0 ordinary-relation leaks, 0 action leaks, and 0 chain bypasses.

## Kill / Removal Timing

Dead fighters are now centrally barred from action, Spiritus spend, Rejoinder, Winding, pass, Disengage, T1, Ort, and attacker continuation. Pending bind attacks clean if either participant is dead. Counter-first still cancels Committed attacks only on actual attacker removal; ordinary Counter remains simultaneous. Across the audit: 0 post-mortem declarations or opportunities.

## Repeated-Choice / Information Tells

The adaptive policy can update only from prior public Fühlen reveals. A previous Hart reveal biases a later blind Duplieren; a Weich reveal biases Mutieren. These are legitimate behavioral tells. No policy saw the current hidden choice before purchase. The bounded sample shows adaptation is possible, but does not establish a stable exploitable tendency because pressure policies are deterministic state functions.

## Opportunity-Conditional Usage

Key conversions: D4 Fühlen 93.88% of legal opportunities; Upper Winding 100% when legal under the bind policy; D5 Duplieren 100% after the D/M specialist’s known/correct branch; D7 Zornhau 100% under the forced qualifying comparison; D13 T1 0/2,589; D3 Counter 22.63% of defensive opportunities. These rates are policy-conditional, not intrinsic values.

## Nearest-Alternative Audit

| Play | Trigger | Cost | Nearest alternative | Reason to choose | Reason not to choose | Status |
|---|---|---:|---|---|---|---|
| Fühlen | live H3 Rejoinder | 1S | blind D/M / decline | avoids hard-fail read | may block funded continuation | HEALTHY DISTINCT |
| Duplieren | Hart Rejoinder | 2S/1 chain | Winding | Booned correct-read Cut | hard-fails wrong read | HEALTHY DISTINCT |
| Mutieren | Weich Rejoinder | 2S/1 chain | Winding | Booned Thrust + threat | hard-fails wrong read | HEALTHY DISTINCT |
| Upper Winding | Upper opportunity | 2S/1 chain | D/M / pass | read-free, Ochs/threat | flat accuracy, reciprocal miss | HEALTHY DISTINCT |
| Lower Winding | Lower opportunity | 2S/1 chain | D/M / pass | unique Lower entry/L2 | becomes Upper on miss | HEALTHY DISTINCT |
| Zornhau | descending Cut | action/1 chain | Hart Cross | threat + local Ort | flat defence, slot cost | HEALTHY DISTINCT |
| Ort | Favored local bind | 1S | local Winding/pass | no second attack roll | relation-gated | NARROW BUT DISTINCT |
| Nachreisen | Committed Prep/Recovery | 1S/1 chain | Counter/ordinary later attack | Boon and unique timing | resource/slot, rare trigger | NARROW BUT DISTINCT |
| Power | Loaded proactive Cut | 1S | Loaded Cut | fixed-7 certainty | Committed/Counter-first | HEALTHY DISTINCT |
| T1 | Tutta successful Wide Cross | 1S/1 chain | remain Wide | only authored Close entry | no ordered/authoritative consumer | INTEGRATION CONFLICT |
| C2 | authored joined defence/offence | 2S/1 chain | Basic defence | cancels + damages | premium cost | HEALTHY DISTINCT |
| S2 | Schielhau/D1 scoped node | 2S/1 chain | Basic defence | joined counter and local resolution | proactive Pflug branch absent | REPERTOIRE-DEPENDENT |

Explicit answers: Cross over Beat for Hart accuracy or owned Crossing repertoire; Beat over Cross to deny opponent bind repertoire. Counter over Cross for urgent reciprocal kill, Cross over Counter for survival. Hart for cancellation, Weich for defender-first bind opportunity. Buy Fühlen at uncertain priors with 3S+, guess at skewed priors/reserve 2. Correct D/M beats Winding on accuracy; Winding avoids the read and supplies guard/threat/reciprocal continuation. Zornhau supplies threat/local Ort; Cross supplies better Hart defence and no slot. Power supplies fixed kill certainty; Loaded Cut preserves flexibility. Nachreisen supplies a Booned target-only timing attack. T1 currently has no reliable concrete payoff. Ochs/Pflug enable threat/D1 denial and authored Winding aftermath.

## Basic Action Audit

| Basic | Concrete use | Reason not to choose | Status |
|---|---|---|---|
| Basic Cut | Loaded/Power/Upper and cut repertoire | cut-only counters | HEALTHY DISTINCT |
| Basic Thrust | avoids Zornhau; thrust compounds | no Loaded boon | HEALTHY DISTINCT |
| Basic Cross | Hart survival; Crossing repertoire | grants striker Rejoinder | HEALTHY DISTINCT |
| Basic Beat | denies Crossing tree; strips guard | flat defence; Open often recovers | HEALTHY DISTINCT |
| Counter | urgent trade/Committed interruption | accepts incoming hit | HEALTHY DISTINCT |
| Disengage | ends risky/resource-empty bind now | abandons own continuation | NARROW BUT DISTINCT |
| voluntary guard change | accesses Loaded/threat/gates | consumes GC1 timing and posture exposure | REPERTOIRE-DEPENDENT |

## Remaining Grammar Findings

Class A, affects this duel: Basic Ignore policy utility; T1 ghost utility; Pommel/Close consumer utility. Class B, later/not this slice: S2 proactive Pflug payload; four Frontale findings; two Crown findings. Class C, stale/informative: Power and S2 scoped exceptions; four Nachreisen findings superseded by its governing repair. No B/C item was repaired.

## Runtime Bugs Found

Three: (1) dead actors could declare; (2) authoritative ordinary Cut resolution omitted Loaded damage boon; (3) D1 wrote a replacement event but could not resolve its replacement roll. All were exact, non-design runtime omissions and were minimally repaired. No design values changed.

## Incentive Problems Found

One real blocker: T1 / Close integration. Its H3 timing is unspecified and its authoritative consumer is absent. This is not evidence against H3, Winden, Hart/Weich, or cap 3.

## Watch Items

- Open’s direct exploitation rate was 0 under tested policies; include D1/guard-gate exploitation in the Close pass.
- Fühlen is close to automatic under O2 with 3S+, but not under O5 or reserve 2.
- Max-8 Spiritus looks meaningful over short duels; rest/campaign cadence is untested.
- Nachreisen needs a scenario family that naturally generates both Preparation and Recovery opportunities.
- Counter’s high-skill simultaneous defeat texture remains a known cadence concern.

## Protected Mechanics Regression

Basic Cut/Thrust/Cross/Beat, Counter, D1, Beat→Open, Open lifecycle, GC1, Committed, P1, repaired Nachreisen, C2, S2, T1 data, Wide/Close, contact zones, guards, Spiritus prices, chain cap, Zornhau local relation, and ordinary H3 semantics were not rebalanced. Ordinary Favored/Unfavored remained retired. The final protected suites and full repository validation pass as recorded below.

## Project Recommendations

Preserve H3, Hart/Weich, F1=1S, D/M=2S, Winden=2S, L2, Bind Initiative/pass, and cap 3. Do not add failed-Beat Open, numeric Open modifiers, generic guard bonuses, or Unknown-height Winden.

Project should adjudicate one narrow T1/Close question: define its ordering relative to the attacker H3 Rejoinder and select one already-evidenced authoritative Close consumer path. Candidate directions for later testing—not implementation here—are: T1 before Rejoinder with explicit reciprocal rights; T1 as an ordinary opportunity after decline; or suspend T1 from H3 ordinary Cross until its consumer is integrated.

## Exact Next Milestone

**D. T1 / CLOSE REPERTOIRE CONSUMER PASS.** It is the first dependency blocker. Do not begin Named Guard v0.2 and do not reopen the ordinary German bind kernel.

## Final Project-Review Questions

1. Yes; all governing baselines passed before audit work.
2. Yes; the audit uses `CurrentEngine`, not copied H3 rules.
3. No hidden Hart/Weich leaked.
4. No second normal action leaked.
5. Yes; ordinary Favored/Unfavored stayed retired.
6. Yes; Zornhau local semantics stayed intact.
7. Yes; Cut has Loaded/Power/Upper and repertoire value.
8. Yes; Thrust avoids cut-only responses and reaches thrust repertoire.
9. Yes; Cross has Hart accuracy and Crossing repertoire.
10. Yes; Beat denies opponent continuation/repertoire.
11. Beat is healthy; Open is narrow/WATCH.
12. Yes; Counter has urgent trade and Committed-interrupt niches.
13. No; Counter does not dominate.
14. Yes; Hart maximizes immediate cancellation.
15. Yes; Weich can give its defender first ordinary opportunity.
16. No pressure is universally dominated.
17. Yes; Fühlen is rational at uncertain priors with 3S+.
18. No; reserve and conservation objectives prevent mandatory use.
19. Yes; blind D/M is rational at skewed priors or reserve 2.
20. Yes; correct D/M has Booned accuracy over flat Winding.
21. Yes; Winding is read-free and produces threat/guard/continuation.
22. Yes provisionally; 2S creates visible multi-exchange tradeoffs.
23. Yes; Lower→Upper L2 is clean.
24. Yes; opportunity/pass sequencing is clean.
25. 2.24% of D4 binds and 1.78% of D12 binds in the integrated policies; exact Skill-14 all-miss ceiling is 2.7%.
26. Yes; cap 3 is mostly a ceiling.
27. Yes; max-8 creates meaningful prioritization in short duels.
28. Not demonstrably too abundant.
29. Not demonstrably too scarce.
30. Yes; Power retains fixed-7 kill certainty.
31. Yes, narrowly; Nachreisen retains Booned Preparation/Recovery timing.
32. Yes; Counter/Power/Nachreisen remain distinct beside bind play.
33. Yes; Zornhau supplies threat and local Ort.
34. Yes; Hart Cross has higher defence and no slot cost.
35. No reliable concrete value in the current authoritative loop.
36. Yes; Close remains an incentive vacuum/blocker.
37. Yes; Ochs supplies threat/D1 denial and Winding aftermath.
38. Yes, narrowly; Pflug supplies threat and Lower aftermath before L2 may move to Ochs.
39. Contextually; it removes guard state, but direct exploitation was 0 here.
40. No stale Crossing/pressure/height/opportunity state remained.
41. No after the runtime repair; deterministic and duel checks pass.
42. No resource or chain accounting break remained.
43. A-class: Basic Ignore, T1, and Pommel/Close; the other 13 are B/C.
44. Three runtime bugs were found and minimally repaired.
45. One real incentive/integration problem was found.
46. T1 ordering plus a concrete authoritative Close consumer.
47. Yes for the bind kernel; no for the whole vertical slice until T1/Close is resolved.
48. Run **T1 / CLOSE REPERTOIRE CONSUMER PASS** and stop for Project adjudication now.

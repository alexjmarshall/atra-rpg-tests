# S2 Authoritative Runtime Parity v0.1 - Results

## Executive Result

PASS. The selected GOVERNING PROVISIONAL Schielhau / Durchwechseln S2 interaction now has an explicit authoritative runtime path. The repair adds an exchange-scoped window, retains the successful Schielhau d20, rolls D1 once, applies the selected comparison and outcomes, and clears the state on every reachable terminal route. It does not change governing data, pricing, the main melee packet, Named Guard work, or unrelated mechanics.

## Project Repair Authority

The milestone instruction keeps S2 selected unless a later explicit Project supersession exists. None was found. The authorized direction was therefore to repair runtime parity with the existing governing S2 sources, not to select, price, or redesign an alternative.

## Source-of-Truth Check

- Branch at start: `main`
- HEAD at start: `c151b12cfee0276f1a303c9b17cdd6495448e3ba`
- Worktree at start: clean; `main...origin/main`
- Governing selection: `data/prototypes/longsword-governing-provisional-v0.1.yaml` selects S2.
- Selected procedure: `data/prototypes/longsword-durchwechseln-schielhau-state-model-v0.3.yaml`.
- Mechanical grammar: `data/audits/longsword-vertical-slice-mechanical-mapping-v0.1.yaml`.
- Governing register: `reports/governing-open-provisional.md`.
- No later explicit Project supersession of S2 was found.

The Play records remain historical/evidentiary records. Their intentionally absent mechanics do not override the governing prototype selection.

## Pre-Repair Baseline

| Check | Result |
|---|---|
| Full unittest discovery | PASS - 161 tests |
| H3 governing suite | PASS - 3 tests; 129/129 numbered assertions |
| T1/Close/Pommel governing suite | PASS - 4 tests; 140/140 numbered assertions |
| Repository validator | PASS - 114 Play records; 0 errors; 39 preserved warnings |
| Melee grammar validator | PASS - 0 errors; 14 informative findings |
| Existing historical/current D1/C2/S2-adjacent suites | PASS - 36 tests |

## Packet-Sync Contradiction

Before repair, governing YAML, the selector, the selected state model, and the mechanical grammar selected or claimed S2, while `ProvisionalLongswordEngine` exposed only ordinary D1 replacement and atomic generic `compound_response("Schielhau")`. It retained no established Schielhau roll, authored no S2 D1 window, performed no S2 comparison, and emitted no S2 result event. This was one root runtime-parity defect comprising six concrete runtime faults.

## Selected S2 Contract

1. A live, already-rolled successful descending/high-line Cut gives its target the reactive Schielhau Remedy opportunity before contact.
2. Schielhau spends the defender's reaction action, 2 Spiritus, and one learned-Play chain entry.
3. Schielhau rolls once. Failure opens no S2 window and leaves the original successful Strike unresolved. Success establishes Schielhau for S2.
4. The successful Schielhau d20 is retained. Its cancellation, damage, and threatening-point consequences wait while the original attacker receives the sourced pre-contact D1 decision.
5. Only that living original attacker can use the window against that living Schielhau actor and pending interaction.
6. D1 remains ordinary D1: known Play, 1 Spiritus, one chain entry, no extra action, and no refund.
7. A declared D1 rolls exactly one fresh normal Longsword d20. Schielhau is never rerolled.
8. Lower successful roll wins; equal successful rolls favor established Schielhau; one success beats failure; both failures select the original Strike.
9. A Schielhau win cancels the original Strike, applies normal Schielhau damage, preserves no contact and measure, establishes Schielhau point threat, and closes the window.
10. A D1 win replaces the pending interaction with the fresh normal D1 thrust, applies normal D1 damage, preserves no contact and measure, establishes D1 point threat, prevents later Schielhau resolution, and closes the window.
11. Both failure leaves the original Strike. This comparison cell is defined but live-unreachable because only a successful Schielhau opens S2.
12. Declining D1 resolves the retained Schielhau normally. An unaffordable or chain-blocked D1 charges nothing and can be declined.
13. Neither declaration refreshes an action. The comparison creates no action, Spiritus, refund, or chain entry.
14. S2 state clears on decline, either winner, failed establishment, actor removal, invalidation, new attack/exchange replacement, and exchange end.
15. Generic C2 Schielhau and ordinary D1 remain independent paths. Absetzen and Scambiar remain unchanged.

| Situation | Established Schielhau | Fresh D1 | S2 winner | Runtime result |
|---|---|---|---|---|
| Schielhau lower successful | successful lower | successful higher | Schielhau | Cancel original; normal Schielhau damage; Schielhau point threatening; no contact |
| D1 lower successful | successful higher | successful lower | D1 | Resolve fresh D1 thrust; D1 point threatening; no contact; no later Schielhau |
| Equal successful | successful equal | successful equal | Schielhau | Tie favors established opposition |
| Schielhau success / D1 fail | successful | failed | Schielhau | Schielhau result; no D1 refund |
| Schielhau fail / D1 success | failed | successful | D1 | Comparison-defined helper cell; live-unreachable |
| Both fail | failed | failed | Original Strike | Comparison-defined helper cell; live-unreachable |

## Current Runtime Failure

Before repair, `declare_durchwechseln` immediately rewrote the pending attack and generic C2 later rolled Schielhau anew. That accidental D1-then-generic-C2 order contradicted the selected established-Schielhau-then-fresh-D1 procedure.

## Implementation Architecture

The engine now owns one `S2SchielhauWindow` containing the two actors, original attack identity, retained Remedy result, delayed Schielhau damage input, and phase. Dedicated establish, decline, and resolve operations share a deterministic comparison helper. Ordinary `declare_durchwechseln` branches into S2 only when this exact window is live; otherwise its former behavior remains intact. Explicit event entries make declaration, retained roll, fresh roll, comparison, outcome, and cleanup auditable.

## S2 Declaration Window

`establish_schielhau_s2` accepts only the intended live pre-contact interaction: a successful rolled descending Cut, a living target with Schielhau and an action, an original attacker with D1, sufficient Spiritus, chain room, no contact, and the ordinary D1 continuation/point gate. The window is tied to object identity for the attack and actors and cannot become a global last-roll cache.

## Established Schielhau Result

The successful Remedy `RollResult` is stored once. Damage, cancellation, and long-point aftermath are delayed until D1 is declined or comparison selects Schielhau. A failed Schielhau spends its declared costs but creates no S2 state.

## Fresh D1 Roll

D1 declaration charges 1 Spiritus and one chain entry, spends no new action, and marks one fresh roll pending. `resolve_s2_durchwechseln` rolls it exactly once. No generic C2 roll is invoked.

## S2 Comparison

`compare_s2_rolls` is a pure helper implementing all six history cells: lower successful wins, ties go to Schielhau, one success beats failure, and both failures return `original-strike`.

## Schielhau-Wins Outcome

The original Strike is cancelled, normal Schielhau damage is dealt to its attacker, contact remains none, measure is preserved, the Schielhau actor's point becomes threatening, and S2 state is cleared.

## D1-Wins Outcome

The original pending object is rewritten as the D1 thrust, resolved with the fresh roll, and deals normal D1 damage to the Schielhau actor. Contact remains none, measure is preserved, the D1 actor's point becomes threatening, the delayed Schielhau never resolves, and S2 state is cleared.

## Tie Outcome

An equal successful roll selects established Schielhau, matching the selected state model's defender/opposition tie rule.

## Failure Outcomes

Schielhau success plus D1 failure selects Schielhau without refund. Schielhau failure creates no live D1 window and leaves the original successful Strike unresolved. The helper still represents Schielhau-fail/D1-success and both-fail history cells; manufacturing them through the live API would contradict the success gate, so tests cover them at the comparison boundary.

## D1 Decline Path

Explicit decline resolves the already-established Schielhau normally. Failed D1 declaration because of actor, knowledge, reserve, chain cap, point, or stale-window checks charges nothing; the valid actor may then decline.

## Point-Threat Timing

Schielhau point threat is deliberately not written while D1 is deciding. This is the selected pre-consequence S2 staging, not a global exception to ordinary D1's point gate. The winning technique writes its threatening point only at resolution.

## Action Economy

The initiating Strike has already spent the attacker's action. Schielhau spends the defender's available reaction action. D1 spends no additional action, and neither comparison nor cleanup refreshes one.

## Spiritus

Schielhau costs 2 Spiritus; D1 costs 1 Spiritus if declared. These are layered governing costs, not a new joined price. No refund occurs after a legal declaration.

## Learned Chain

Schielhau and declared D1 each consume one learned-Play entry. The existing cap of 3 is enforced before charging. Intrinsic long point adds no entry.

## Cleanup / Window Expiry

The window clears after decline, either winner, establishment failure, actor removal, attack cancellation/invalidation, new attack, and exchange end. A pending attack cannot be normally resolved while the D1 decision is live. Undeclared expiry resolves retained Schielhau; defensive cleanup prevents an incomplete declared D1 state from leaking to a later exchange.

## Generic C2 Preservation

Generic C2 Schielhau remains an atomic `compound_response` outside S2 and makes its own roll. Generic Absetzen and Scambiar remain unchanged.

## Ordinary D1 Preservation

Without a live matching S2 window, `declare_durchwechseln` retains its existing immediate replacement behavior, 1-Spiritus price, chain entry, no-extra-action treatment, and ordinary point gate.

## H3 Regression

PASS. The dedicated H3 governing suite remains 3/3 with 129/129 numbered assertions. Hart/Weich, hidden bind relation, Fuhlen, Duplieren/Mutieren, upper Winding, and related cleanup were not redesigned.

## T1 / Close / Pommel Regression

PASS. The dedicated suite remains 4/4 with 140/140 numbered assertions. Tutta Cover-to-Stretto, Close opportunity, initiative, and Pommel Strike remain unchanged.

## Zornhau Regression

PASS through the adjacent/current suite and dedicated S2 controls. Zornhau's local bind relation, Ort, and Winden path remain distinct from S2.

## Metadata / Runtime Parity

| Layer | Before repair | After repair |
|---|---|---|
| Governing YAML | S2 selected | S2 selected; unchanged |
| Selector | Claimed S2 | Claim verified against S2 API/comparison |
| Selected state model | Established Schielhau then fresh D1 | Preserved |
| Mechanical grammar | Reuse successful Schielhau result | Synchronized with runtime; unchanged |
| `CurrentEngine` | Generic C2 and ordinary D1 only | Actual S2 window, retained roll, comparison, outcomes, cleanup |
| Tests | Generic/adjacent controls only | 86 numbered S2 assertions, forced sequences, parity checks, integrated smoke |

No governing YAML, mechanical grammar, Play record, or packet was edited because those layers already expressed the selected S2 contract.

## Dedicated S2 Contract Validation

PASS - 4 test methods. The suite proves all 86 numbered governing assertions, forced sequences A-L, additional cancellation/expiry routes, metadata parity, protected generic controls, and exact comparison cells.

## Integrated Smoke

PASS. Deterministic S1-S7 coverage exercises generic C2, S2 D1 win, S2 decline, ordinary D1, point denial, post-S2 H3, and T1/Close. No Monte Carlo simulation was run or needed for this parity repair.

## Runtime Bugs Found

One root parity defect comprised six concrete runtime bugs, all fixed:

1. No authored S2 declaration window.
2. No retained successful Schielhau roll.
3. Accidental D1-before-generic-C2 roll ordering.
4. No selected fresh-D1 comparison or tie rule.
5. No distinct S2 result/event path.
6. No S2-specific expiry and stale-state cleanup.

## Design Contradictions Found

Zero. Apparent point timing is coherent once delayed Schielhau consequences are distinguished from its successful established roll. The both-fail cell is comparison semantics/history coverage, while the live window correctly requires successful Schielhau.

## Remaining Documentation Debt

- Existing grammar-validator findings remain informative and predate this repair (14 findings, 0 errors).
- The grammar's older Nachreisen cost/effect description and older Power-centric Committed/Counter description remain known cross-document debt. They are outside S2 and were not silently repaired.
- The S2 grammar's proactive Pflug-breaker payload remains unimplemented/open as already documented; this milestone implemented only the selected Schielhau/D1 interaction.
- Play-record mechanics fields remain evidence-disciplined rather than being populated from prototype rules.

## Post-Repair Governing State

| Protected mechanic | Result |
|---|---|
| Ordinary D1 | Unchanged; dedicated control PASS |
| Generic C2 Schielhau | Unchanged; fresh-roll control PASS |
| Absetzen | Unchanged; control PASS |
| Scambiar di Punta | Unchanged; control PASS |
| H3 ordinary bind | Unchanged; governing suite PASS |
| Hart/Weich | Unchanged |
| Fuhlen | Unchanged |
| Duplieren/Mutieren | Unchanged |
| Winden | Unchanged |
| Zornhau local relation | Unchanged |
| Ort | Unchanged |
| T1 | Unchanged; governing suite PASS |
| Pommel | Unchanged; governing suite PASS |
| Beat/Open | Unchanged |
| Committed | Unchanged |
| Power | Unchanged |
| Nachreisen | Unchanged |
| Learned-chain cap 3 | Preserved and S2-tested |
| Maximum-8 baseline | Unchanged |

Post-repair validation: 165/165 full-discovery tests; 129/129 H3 numbered assertions; 140/140 T1/Close/Pommel numbered assertions; 114 Play records with 0 repository errors and 39 preserved warnings; grammar 0 errors and 14 findings; 36/36 adjacent historical/current tests; 4/4 dedicated S2 test methods.

## Packet-Sync Readiness

YES. The specific governing-data/selector/runtime contradiction is repaired and all required regression gates pass. This report does not perform packet sync or edit the main melee packet.

## Exact Next Milestone

`ATRA MELEE VERTICAL-SLICE STABILIZATION / GOVERNING PACKET SYNC - RESUME v0.2`

Named Guard v0.2 should continue to wait until that packet-sync milestone finishes.

## Final Project-Review Questions

1. **Was a later explicit S2 supersession found?** No.
2. **Does governing data still select S2?** Yes.
3. **Was S2 demoted, repriced, or compared with S1/S3?** No.
4. **Which procedure governs?** The S2 procedure in `longsword-durchwechseln-schielhau-state-model-v0.3.yaml`.
5. **What opens the window?** A successful Schielhau Remedy roll against the live successful descending Cut, before contact.
6. **Is the Schielhau roll retained?** Yes.
7. **Does D1 receive a fresh roll?** Yes, exactly once.
8. **Does lower successful roll win?** Yes.
9. **Do ties favor Schielhau?** Yes.
10. **Does one success beat one failure?** Yes.
11. **Is both-fail defined as the original Strike?** Yes.
12. **Is both-fail live-reachable?** No; it is correctly represented at the comparison helper because successful Schielhau is the live gate.
13. **Does a Schielhau win cancel the original Strike?** Yes.
14. **Does a D1 win suppress later Schielhau resolution?** Yes.
15. **Does either outcome create contact?** No.
16. **Does either outcome change measure?** No.
17. **Does the winner establish threatening point?** Yes.
18. **Does decline resolve established Schielhau?** Yes.
19. **Is the D1 window scoped to the same actors and attack?** Yes.
20. **Is point timing contradictory?** No; consequences are delayed until after the pre-contact D1 decision.
21. **Does Schielhau cost 2 Spiritus?** Yes.
22. **Does D1 cost 1 Spiritus?** Yes.
23. **Does Schielhau spend one chain entry?** Yes.
24. **Does D1 spend one chain entry when declared?** Yes.
25. **Is the live branch's total layered cost 3 Spiritus and two entries?** Yes.
26. **Are costs refunded after legal declaration?** No.
27. **Does D1 spend another action?** No.
28. **Does Schielhau spend the defender's available action?** Yes.
29. **Does comparison refresh an action?** No.
30. **Is the chain cap checked before charging?** Yes.
31. **Does intrinsic long point consume another chain entry?** No.
32. **Does failed Schielhau leave the original Strike unresolved?** Yes.
33. **Does failed Schielhau open S2?** No.
34. **Can an unaffordable or capped D1 be declined without charge?** Yes.
35. **Does state clear on all reachable terminal routes?** Yes, with defensive invalidation for stale/incomplete state.
36. **Can S2 state leak to a later attack?** No.
37. **Is generic C2 Schielhau still separate?** Yes.
38. **Does generic C2 still make its own roll?** Yes.
39. **Is ordinary D1 preserved outside S2?** Yes.
40. **Are Absetzen and Scambiar preserved?** Yes.
41. **Did H3 retain all 129 numbered assertions?** Yes.
42. **Did T1/Close/Pommel retain all 140 numbered assertions?** Yes.
43. **Is Zornhau's local bind relation preserved?** Yes.
44. **Are Ort and Winden preserved?** Yes.
45. **Are Beat/Open, Committed, Power, and Nachreisen unchanged?** Yes.
46. **Is the learned-chain cap still 3?** Yes.
47. **Is the maximum-8 baseline unchanged?** Yes.
48. **Were Play records or historical claims altered?** No.
49. **Were governing YAML or grammar edits required?** No; they already matched the selected contract.
50. **How many actual runtime bugs were fixed?** Six concrete bugs under one root parity defect.
51. **How many design contradictions were found?** Zero.
52. **Did the dedicated S2 contract suite pass?** Yes, 4/4 methods and all 86 numbered assertions.
53. **Did integrated smoke pass?** Yes.
54. **Did full discovery pass?** Yes, 165 tests.
55. **Was Monte Carlo tuning performed?** No.
56. **Was the main melee packet edited?** No.
57. **Is packet sync now ready to resume?** Yes.
58. **Should packet sync be the next milestone?** Yes.
59. **Should Named Guard v0.2 still wait?** Yes.
60. **What is the exact next milestone?** `ATRA MELEE VERTICAL-SLICE STABILIZATION / GOVERNING PACKET SYNC - RESUME v0.2`.

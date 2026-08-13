# Melee Vertical-Slice Stabilization / Governing Packet Sync v0.1 — Results

## Executive Result

**STOP FOR PROJECT ADJUDICATION — GOVERNING/RUNTIME CONTRADICTION FOUND.** The repository began from a clean, mechanically passing baseline, but the synchronization cannot publish Atra Melee Design Packet v0.5 without misrepresenting the current vertical slice. Governing data selects Schielhau/Durchwechseln **S2**, the governing selector states that the authoritative shared engine implements S2, and the mechanical grammar specifies S2's established-Schielhau-roll versus fresh-D1-roll comparison. The authoritative `CurrentEngine` has no S2 declaration window, state, method, or comparison. It instead exposes Schielhau only as an atomic generic C2 compound response.

Under the task's explicit contradiction rule, no packet v0.5, DOCX, source record, or packet index was created. Atra Melee Design Packet v0.4 remains preserved and current as the last published packet, but it is materially stale relative to the later governing integrations. No runtime, governing mechanics data, Play record, Guard record, test, or historical candidate artifact was edited.

Recommended narrow repair milestone: **S2 AUTHORITATIVE RUNTIME PARITY v0.1**. It should implement or otherwise explicitly adjudicate the already-selected S2 interaction in the authoritative engine, add deterministic contract coverage for its timing and roll comparison, and synchronize the selector/data claim. Packet sync should then be resumed. Named Guard v0.2 should not begin first.

## Repository / Source-of-Truth Check

- Branch: `main`
- HEAD at start: `9928a636e78b7825dd34cd16770ebafa19e86d70`
- Worktree at start: clean; `main...origin/main`
- Current published packet: `docs/melee-design-packet-v0.4.md`, companion `Atra_Melee_Design_Packet_v0.4.docx`, and source record `data/sources/atra-melee-design-packet-v0-4.yaml`
- Packet convention: immutable versioned snapshots; v0.4 was not overwritten.
- Mechanical source-of-truth hierarchy checked: governing register, governing YAML, selector, authoritative shared engine, deterministic tests, grammar map, Play records, and Guard records.
- Evidence source-of-truth hierarchy checked: current Play/Guard historical records and their preserved source locators/statuses.

The current governing integration reports and JSON, immediately preceding system audits, v0.4 packet, governing register/data, authoritative engine, current eight-guard data, and required vertical-slice Play/source records were inspected. Historical candidate reports were not rewritten.

## Pre-Sync Validation

All required checks passed before any repository edit:

| Check | Result |
|---|---|
| Full unittest discovery | PASS — 161 tests |
| H3 governing suite | PASS — 3 tests, including 129/129 contract assertions |
| T1/Close/Pommel governing suite | PASS — 4 tests, including 140/140 contract assertions |
| Repository validator | PASS — 114 Play records, 0 errors, 39 preserved warnings |
| Melee grammar validator | PASS — 0 errors, 14 informative findings |

The green baseline does not cover the S2 contradiction described below: H3 check 125 proves only that `compound_response("Schielhau", ...)` is legal. It does not stage Schielhau before D1 or assert the selected S2 comparison.

## Previous Packet Status

Atra Melee Design Packet v0.4, dated 2026-08-07, was the exact current packet before this task. It predates the governing-provisional named-guard direction, Choice Architecture/GC1, Repertoire Integrity Repair, H3-L2 ordinary bind integration, integrated full-duel audit, and T1/Close/Pommel E1/P2 integration. It therefore cannot serve as a synchronized current-vertical-slice packet without a new version.

The v0.4 snapshot remains byte-preserved. No v0.5 artifact was published because parity could not be certified.

## Chronological Reconciliation Method

Decisions were ordered by milestone and Project adjudication. Later explicitly adjudicated governing decisions were treated as current; old experiments remained historical. Candidate recommendations were not promoted. Historical lessons and Atra abstractions were kept separate. The comparison stopped when governing data and authoritative runtime were shown to disagree on S2.

Key verified chronology before the stop:

1. State-based D1, C2, S2, explicit contact, chain cap 3, Loaded/P1, and source-specific named guards entered the governing-provisional baseline.
2. Choice Architecture retained Beat-to-Open and GC1 while later Repertoire Integrity Repair retracted blanket Cross immunity, generalized Committed timing, and repaired Nachreisen/Zornhau local behavior.
3. H3-L2 superseded ordinary roll-derived Favored/Unfavored with Hart/Weich, paid ordinary Fühlen, D/M, bind height, opportunity/pass sequencing, and 2S Upper/Lower Winding; Zornhau's relation remained local.
4. The integrated full-duel audit found T1/Close to be the sole severe integration blocker in its audited scope.
5. E1 T1 and P2 Pommel later closed that blocker at governing-provisional status.
6. Packet synchronization then exposed the older S2 selector/runtime mismatch, which the integration suites did not exercise.

## Current Governing Architecture

The governing YAML, register, and runtime agree on the H3-L2 ordinary bind kernel and E1/P2 Close slice. They also agree on max-8 as the current test baseline, chain cap 3, D1 cost/timing and point-threat denial, Beat/Open, GC1, general Committed timing, P1, repaired Nachreisen, Zornhau-local relation, T1, and Pommel. That agreement is not sufficient to publish the whole requested packet while S2 is still claimed as governing and implemented but is absent from `CurrentEngine`.

## Core State Reconciliation

The following state model was verified without finding a governing data/runtime disagreement:

- contact: `none | crossing`
- measure: `wide | close`
- per-fighter contact zone: `hiltward | middle | pointward | unknown`
- ordinary initial pressure: `hart | weich | unknown`, owner-private and phase-scoped
- legacy/special pressure: `hard | soft | unknown`, not the H3 ordinary pressure axis
- bind height: `upper | lower | unknown`, public and modifier-free
- point threat: `threatening | not_threatening`
- guard: one of the named guards or Open
- bind opportunity/Bind Initiative: first declaration opportunity only
- Loaded and Committed: current authored attack/guard states, not generic bonuses

Ordinary Favored/Unfavored is superseded. The underlying relation remains only for Zornhau-local and already-authored special contested crossings.

## Basic Actions Reconciliation

- Basic Cut and Basic Thrust remain distinct through repertoire/response topology rather than a new numeric split.
- Basic Cross uses private pre-roll Hart/Weich, cancels on success, establishes ordinary Crossing, writes authored height, and opens E1 or the narrow H3 Rejoinder as applicable.
- Basic Beat cancels, displaces, ends contact, and sets the attacker Open only on success. Failed Beat does not set the defender Open.
- Counter retains ordinary simultaneous resolution after a successful non-early-countered attack; Committed supplies the earlier declaration window.
- D1 Through/Durchwechseln costs 1S and one chain entry, replaces the pending attack before the declared Basic defence roll, and is denied by a threatening opposing point—not by Crossing or the word Cross.
- GC1 allows one voluntary legal named-guard change before the action; no voluntary post-action change exists.

## Spiritus / Chain Reconciliation

- Max Spiritus 8 remains a **PROVISIONAL TEST BASELINE**, not a final campaign rule.
- Global learned chain cap is 3.
- D1, Power, Nachreisen, ordinary Fühlen, and T1 cost 1S in their current contexts.
- C2/S2 compounds, D/M, ordinary Upper/Lower Winding, and Pommel P2 cost 2S.
- Zornhau costs 0S plus one learned entry; intrinsic Ort costs 1S and no second entry.
- Ordinary Fühlen and pass consume no learned-chain entry; Basics consume none.
- Zornhau-local W1/W2 remains a 1S local compatibility path pending separate adjudication.

No price was changed.

## Committed / Power / Nachreisen

General Committed timing, P1, and repaired Nachreisen agree in governing data and runtime:

- before a Committed attack roll, the original target may use immediate Basic Counter or an authored Preparation technique;
- removal cancels the pending attack; survival lets it proceed;
- waiting preserves the ordinary simultaneous Counter only after a successful attack roll;
- a miss creates no retroactive ordinary Counter;
- P1 requires Loaded, costs 1S, uses a normal attack roll, fixes normal longsword damage at 7, replaces rather than stacks the Loaded Damage Boon, is Committed, and is Basic/non-learned;
- Nachreisen costs action + 1S + one learned entry and makes a Booned normal-damage Longsword attack in its target-only Preparation or immediate Recovery window.

## Ordinary H3 Bind Kernel

H3-L2 is synchronized across its governing YAML, register, selector, runtime, and dedicated tests. Ordinary Basic Cross no longer writes Favored/Unfavored. E1 T1 occurs after the successful qualifying Cross/D1 timing and before H3 creation. If E1 is declined or unavailable, the striker receives the normal narrow Rejoinder.

## Fühlen Context Split

- Ordinary H3: learned, 1S, no action, no chain, once per live initial Rejoinder, reveals the opponent's current Hart/Weich.
- Zornhau-local: preserved passive categorical visibility of the local Favored/Unfavored relation.

This is acknowledged **COMPATIBILITY DEBT**, not a packet-writing error and not resolved here.

## D/M

Duplieren/Mutieren remains one learned item. Each declaration costs 2S, one chain entry, and no additional action. Correct Hart/Duplieren produces a Booned high Cut; correct Weich/Mutieren produces a Booned low-opening Thrust and authored threat/transition aftermath. Wrong read spends/consumes, makes no attack roll, and deals zero.

## Bind Height / Winden

Upper/Lower/Unknown height and the explicit Upper/lower-setting-aside writers are synchronized. Ordinary Upper and Lower Winding each cost 2S/+1 chain/no action and use a flat normal-damage Thrust. Upper miss retains Upper/Ochs/threat and transfers opportunity. Governing L2 Lower miss changes Lower to Upper and Pflug to Ochs, retains Crossing/threat, and transfers opportunity. L1 is not governing. Unknown has no generic Winden fallback.

## Zornhau Local Exception

Zornhau's local relation is preserved and does not enter ordinary H3. The current local branch costs the defender action plus one learned entry and 0S; success cancels a qualifying descending Cut, establishes Crossing/threat, assigns first opportunity, and writes local Favored/Unfavored from the two successful rolls. Ort costs 1S, no second chain entry, and no second attack roll; it requires local Favored. Its O1 normal-damage versus O2 Damage-Bane parameter remains unresolved in the preserved local harness. Local W1/W2 and passive Fühlen remain compatibility debt.

## Guard Roster

The exact eight-record roster is synchronized as evidence/provisional state:

- German: Vom Tag, Ochs, Pflug, Alber
- Italian: Posta di Donna, Posta Frontale, Tutta Porta di Ferro, Mezza Porta di Ferro

Verified current identities include Vom Tag cut-ready but not Loaded; Ochs/Pflug threatening upper/lower hanging aftermath; Alber low and nonthreatening with no invitation bonus; Donna Loaded as an Atra provisional identity; Frontale Basic Cross/Beat mappings with a missing learned payload; Tutta Basic mappings plus E1 T1; and Mezza threatening point with Basic Thrust/Beat mappings. Sourced breaker relationships carry no automatic modifier. Crown remains unresolved.

## T1 / Close / Pommel

E1 T1 and P2 Pommel remain internally synchronized:

- T1: qualifying Tutta ordinary Basic-Cut/Cross route; after D1, before H3 creation; 1S/+1 chain/no action/no test; retain Crossing; Wide to Close; height to Unknown; Hart gives the striker first Close opportunity, Weich gives the Tutta defender; clear pressure.
- Pommel: generic valid Close-Crossing consumer; 2S/+1 chain/no action; flat Longsword; normal provisional d6+1; no intrinsic response denial; hit cleans the bounded bind; miss retains Close/Unknown and transfers opportunity.
- Close has no generic modifier, leverage, separate initiative token, grapple system, or universal strike.

The severe T1/Close blocker identified by the integrated audit is closed. The present stop is a different, older S2 parity problem.

## Italian Repertoire Boundaries

Scambiar di Punta remains the 2S C2 joined cancellation/counter-thrust chassis in governing data and grammar; current Donna/Tutta access is a bounded source-facing harness abstraction, not a claim of historical exclusivity. Rompere's thrust-breaking evidence and retained-contact/close possibilities remain separate and unpromoted. T1 was not expanded into either Play.

## Full-Duel Audit Findings

The integrated audit's load-bearing conclusions remain evidence, not final canon: Basics retain distinct use; Hart/Weich are situational; Fühlen is strong but reserve-dependent; D/M and Winden remain distinct; cap 3 behaves mainly as a ceiling; max-8 remains plausible as a short-duel test baseline; Power/Nachreisen/Zornhau retain reasons; Open remains WATCH; and T1/Close was the severe blocker subsequently closed by E1/P2. No Monte Carlo or new simulation was run during this stopped packet sync.

## Governing / Runtime Contradiction

### Exact contradiction

| Layer | Current claim/behavior |
|---|---|
| Governing data | `data/prototypes/longsword-governing-provisional-v0.1.yaml` selects `schielhau_durchwechseln.variant = S2`. |
| Governing selector | `simulations/shared/provisional_longsword.py` publishes `schielhau_durchwechseln = S2` and says the authoritative shared exchange engine implements `C2/S2`. |
| Mechanical grammar | `data/audits/longsword-vertical-slice-mechanical-mapping-v0.1.yaml` says Schielhau is first established with a successful Remedy roll; a subsequent D1 reuses that Schielhau result against a fresh D1 roll under the selected S2 comparison. |
| Historical selected procedure | `data/prototypes/longsword-durchwechseln-schielhau-state-model-v0.3.yaml` defines lower successful roll wins, ties favor established Schielhau, one success beats failure, and the defined failure outcome applies. |
| Authoritative runtime | `ProvisionalLongswordEngine` has no S2/Schielhau declaration-window method or stored established Schielhau roll. `declare_durchwechseln` immediately replaces the pending attack; `compound_response("Schielhau", ...)` later resolves an atomic generic C2 response with a new normal roll and no S2 comparison. |
| Tests | Existing governing coverage proves only generic Schielhau compound legality; no test asserts the S2 ordering/comparison contract. |

### Reproduction

A read-only probe against `CurrentEngine` produced:

- S2/Schielhau-specific engine methods: none
- D1 replacement: legal; pending kind became `durchwechseln-thrust`
- Schielhau invoked afterward: legal and successful as generic `Schielhau C2 succeeded`
- event order: D1 replacement, then Schielhau point-threat event
- no established-Schielhau roll, reused roll, opposed S2 comparison, or S2 result event

This is not merely stale prose. Governing data and the authoritative runtime disagree about a selected, current mechanic.

### Last Project adjudication affecting S2

The 2026-08-11 governing-provisional baseline selected S2 after the provisional state-model experiment. The 2026-08-13 H3 integration explicitly preserved S2's authored rules and identified `provisional_longsword_engine.py` as synchronized behavior. No later Project decision supersedes S2 or removes it from the current vertical slice.

## Superseded Decisions

Verified supersessions include ordinary R0 roll-derived relation, passive ordinary Fühlen, H2 Upper-only completion, U1, L1, Hybrid H3/R0, generic Leverage, Counter-Wind, T1 C0, T1 L1 as governing timing, old 0S/action-ready Pommel, and T1-owner-first priority. These were not republished into v0.5 because publication stopped.

## Rejected Decisions

Verified rejected/non-governing items include P1 1S Pommel, universal Pommel response denial, generic Unknown Winden, generic Close modifier, failed Beat to defender Open, sparse voluntary guard graph, automatic breaker modifiers, and Crown C1/B3 promotion.

## Open Questions

- S2 authoritative runtime parity: blocker discovered here
- Zornhau-local Ort O1/O2 and local W1/W2 adjudication
- contextual Fühlen compatibility
- Alber and Frontale incentive/repertoire gaps
- Crown architecture
- final guard identities and opening procedure
- final Spiritus recovery/rest cadence
- final Pommel injury/damage identity
- final card wording/tier progression

## Deferred Content

Full eight Windings, left/right bind geometry, generic Krieg expansion, broader Fiore stretto, grapples, throws, disarms, Close counters, generic closing beyond authored Plays, and the final campaign/resource layer remain deferred. They are not current-vertical-slice blockers.

## Compatibility Debt

The deliberate Zornhau-local/H3 context split remains compatibility debt. Older source records with null mechanical branches are evidence records rather than the governing mechanical source. The grammar map also retains stale Nachreisen diagnostic text (0S/flat/incomplete) even though governing data/runtime implement the repaired 1S/Booned two-window model; the integrated audit already classifies its four Nachreisen grammar findings as stale. That is documentation debt, not the governing/runtime contradiction that triggered this stop.

## Test Baselines

- Max Spiritus 8: provisional test baseline, not final.
- Normal longsword damage d6+1: current provisional damage baseline, not final injury identity.
- Learned chain cap 3: governing provisional.
- Rest/campaign recovery cadence: open/deferred.

## Packet Changes from Previous Version

No v0.5 packet was created, so there is no v0.4-to-v0.5 diff. The planned synchronization would have added or corrected H3 ordinary binding, R0 supersession, Hart/Weich, contextual Fühlen, D/M, bind height, Lower Winding/L2, E1 T1 timing, Close priority, Pommel P2, and the integrated audit conclusions. Those changes remain unpublished until the S2 parity blocker is repaired.

## Governing Data / Runtime / Packet Parity

**FAIL / BLOCKED.** H3 and T1/Close/Pommel parity passed inspection, but S2 parity failed. Publishing a packet that calls S2 implemented would repeat the selector/data claim that the runtime does not satisfy; omitting or demoting S2 would silently overrule a Project-selected governing mechanic. Neither is allowed in packet sync.

## Validation After Sync

Only this Markdown report and its JSON companion were added. No sync was completed and no mechanics changed. Post-report validation is recorded in the JSON companion and remained mechanically unchanged from the pre-sync baseline.

## Vertical-Slice Stability Assessment

The H3 ordinary bind kernel and E1/P2 Close slice are stable at governing-provisional status, and the former severe T1/Close blocker is closed. The repository as a whole cannot yet be certified as packet-synchronized because a selected current S2 mechanic is absent from the authoritative runtime path. A fresh context should continue to consult the governing register/data and this stop report; it should not treat v0.4 as current mechanics or infer an S2 resolution.

## Exact Next Milestone

**S2 AUTHORITATIVE RUNTIME PARITY v0.1**

Bounded scope:

1. confirm that the 2026-08-11 S2 selection still governs;
2. represent the Schielhau declaration/success window and retained roll in `CurrentEngine` without inventing a new rule;
3. apply the already-recorded S2 comparison when D1 is declared in that window;
4. add deterministic timing, tie, success/failure, action, Spiritus, chain, point-threat, and cleanup contract checks;
5. synchronize selector/runtime wording and rerun the full baseline;
6. resume packet sync afterward.

Do not begin Named Guard v0.2 or reopen H3/T1/Pommel during that repair unless a new contradiction is demonstrated.

## Final Project-Review Questions

1. **Did the repository begin from a clean/mechanically passing baseline?** Yes: clean `main`, 161 tests, both dedicated governing suites, and both validators passed.
2. **What exact packet/version was current before this task?** Atra Melee Design Packet v0.4 (2026-08-07).
3. **What exact packet/version is now the synchronized current packet?** None; synchronization stopped before v0.5 publication.
4. **Was the previous packet preserved according to repo conventions?** Yes, byte-preserved and unedited.
5. **Were governing rules changed mechanically?** No.
6. **Were any runtime files changed?** No.
7. **Were any governing data files changed for mechanics rather than documentation parity?** No governing data files were changed at all.
8. **Does the new packet clearly say GOVERNING PROVISIONAL rather than final?** No new packet exists; this report preserves that required classification.
9. **Does it distinguish TEST BASELINE from governing-final values?** The report does; no packet was published.
10. **Is ordinary Basic Cross documented with Hart/Weich?** Verified for the planned sync and summarized here; no packet published.
11. **Is ordinary Favored/Unfavored clearly superseded?** Verified and recorded here; no packet published.
12. **Is Zornhau's local relation clearly preserved as a local exception?** Verified and recorded here.
13. **Is contextual Fühlen documented accurately?** Verified and recorded here.
14. **Is the Fühlen semantic split explicitly listed as compatibility debt?** Yes, in this report.
15. **Are D/M current costs/triggers correct?** Verified: 2S/+1 chain/no action in the attacker Rejoinder.
16. **Is bind_height Upper/Lower/Unknown documented correctly?** Verified and summarized here.
17. **Are Upper and Lower Winding current 2S mechanics correct?** Verified in governing data/runtime.
18. **Is L2 documented and L1 excluded from current rules?** Verified and summarized here.
19. **Is Bind Initiative clearly first opportunity rather than ownership?** Yes, in governing data/runtime and this report.
20. **Is Through denial tied to threatening point rather than Crossing itself?** Yes.
21. **Are Cross and Beat given distinct current roles?** Yes.
22. **Is failed Beat to defender Open absent from governing rules?** Yes.
23. **Is Open represented without a fabricated numeric penalty?** Yes.
24. **Are GC1 rules synchronized?** Governing data/runtime agree; no packet was published.
25. **Are Committed/Counter timing rules synchronized?** Governing data/runtime agree; the older grammar map has stale Power-centric wording noted as documentation debt.
26. **Is P1 Power synchronized?** Yes in governing data/runtime.
27. **Is repaired Nachreisen synchronized?** Governing data/runtime agree; the grammar map remains stale and is noted as documentation debt.
28. **Is T1 E1 after D1 and before H3 creation?** Yes.
29. **Is T1 correctly described as a state transformation rather than cancelling D/M?** Yes.
30. **Does T1 clear bind_height?** Yes, to Unknown.
31. **Is Hart-to-striker / Weich-to-defender Close priority documented?** Yes.
32. **Is Pommel generic Close rather than T1-specific?** Yes.
33. **Is Pommel exactly 2S/+1 chain/no Action?** Yes.
34. **Is 1S Pommel clearly rejected?** Yes.
35. **Is old 0S/action-ready Pommel clearly superseded?** Yes.
36. **Is Pommel response denial absent?** Yes.
37. **Is Pommel miss retain/transfer documented?** Yes.
38. **Is the current Close model described without inventing a generic Close system?** Yes in this report; no packet was published.
39. **Are Scambiar/Rompere kept separate from T1?** Yes.
40. **Is the current eight-guard roster synchronized?** The records were verified; no packet was published.
41. **Does each guard's section distinguish actual mechanics from historical source notes/candidates?** No new packet guard section was published; the report preserves the distinction.
42. **Are Ochs/Pflug sourced Winden transitions represented?** Yes in governing data/runtime.
43. **Is Alber's current gap still explicit if unresolved?** Yes.
44. **Is Frontale's current gap still explicit if unresolved?** Yes.
45. **Is Crown still unresolved rather than silently fixed?** Yes.
46. **Is max Spiritus 8 classified correctly?** Yes, as a test baseline.
47. **Is chain cap 3 synchronized, including T1/Pommel examples?** Yes in governing data/runtime/tests.
48. **Are the integrated full-duel conclusions summarized without overstating them?** Yes in this report; no packet was published.
49. **Is Open still WATCH rather than falsely resolved?** Yes.
50. **Are all rejected/superseded mechanics visibly classified?** The report records the required high-level set; the planned packet matrix was not published.
51. **Are all meaningful open questions/deferred items preserved?** Yes in this stop report.
52. **Were historical evidence and Atra abstractions kept distinct?** Yes.
53. **Did any packet/runtime split-brain remain?** Packet publication was stopped specifically to prevent one; governing data/runtime S2 split-brain remains unresolved.
54. **Did all post-sync validators/tests pass?** No sync occurred; post-report checks pass as recorded, but they do not cover S2 semantics.
55. **How many actual contradictions were discovered?** One governing data/selector/runtime contradiction: selected S2 is absent from `CurrentEngine`.
56. **Did packet sync require any mechanics change?** It requires a separate narrow repair milestone; no mechanics change was made here.
57. **Is the current melee vertical slice now sufficiently stabilized for fresh contexts to use this packet as their primary design reference?** No synchronized packet was published. H3 and Close are stable, but S2 parity must be repaired first.
58. **Is the severe T1/Close blocker recorded as closed?** Yes.
59. **What is now the single leading unfinished melee dependency?** S2 authoritative runtime parity.
60. **Should the next Project milestone be Named Guard v0.2?** No. Run the narrow S2 parity repair, resume packet sync, then reconsider Named Guard v0.2.

**STOP FOR PROJECT REVIEW.**

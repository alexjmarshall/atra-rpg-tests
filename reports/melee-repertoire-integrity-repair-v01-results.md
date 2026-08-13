# Melee Repertoire Integrity Repair v0.1 Results

Status: **GOVERNING PROVISIONAL implementation repair; O1/O2 and W1/W2 remain unpromoted candidates.**

## Executive Result

The authoritative shared exchange engine is synchronized and all 81 required deterministic assertions pass. Blanket Cross immunity is gone: D1 is denied only by threatening opposing point (plus its ordinary prerequisites), while Beat still strips a successfully defended attacker to conservative Open. General Committed timing, the 1-Spiritus two-window Nachreisen, threatening-point Zornhau, contested Favored/Unfavored Bind, independent Bind Initiative, passive Fühlen, intrinsic Ort, and minimal thrusting Winden now have rules-derived behavior.

Exact controlled analysis favors **O1 normal damage** over O2 and **W2 either-relation** over W1 for Project review, but neither is promoted. At Skill 14, W2 Winden is harmless optionality from Favored Bind under both damage models: deterministic immediate value still selects Ort there. Fühlen has positive value without a numeric bonus by eliminating wrong hidden-condition decisions. Frontale remains candidate-only because its evidence does not decide the Atra attack/test count or whether retreat is merely metadata.

## Source-of-Truth Check

Git was clean before edits. The packet, governing register/YAML, vocabulary, architecture and incentive reports, Crossing/Bind and continuation reports, guard evidence, Loaded/Power, Spiritus/Parry/D1, audited Play records, shared selector, selected archived engine, action timing, policy constants, and current tests were inspected. No unresolved material conflict remained after applying the prompt's explicit later adjudications. Atra Melee Design Packet v0.4 was not edited.

## Project Supersessions Persisted

Durable governing records now mark blanket Cross immunity, P1-only Counter-first, old Nachreisen persistence/Vom Tag gating, nonthreatening Zornhau, and exclusive Ochs/Pflug Winden starting gates as superseded. Archived reports and experiment engines were not rewritten.

## Authoritative Engine Synchronization

`simulations/shared/provisional_longsword.py` now selects `simulations/shared/provisional_longsword_engine.py`. Archived Loaded/Power classes remain compatibility exports only. The current engine implements state-based D1, Beat->Open, GC1, general Committed timing, current P1 restrictions, T1, cap 3, C2/S2 response chassis, and explicit contact/measure/pressure/point state.

## Mechanical Vocabulary Compliance

The repair uses only ATTACK, CANCEL, SET, CLEAR, RETAIN, MODIFY_ATTACK, REPLACE_PENDING_ATTACK, and existing timing/order behavior. No new operator was needed. Bind relation and Bind Initiative are state/sequencing data, not generic modifiers. Mechanical retreat in Frontale was stopped because Force Movement remains deferred.

## Committed / Counter Timing

Immediate Basic Counter is free, normal, and first; Preparation Nachreisen pays 1S for Attack Boon in the same window; waiting Counter is simultaneous only after a hit; Recovery Nachreisen exists only after a miss. The defender's single action prevents double defence naturally.

## Nachreisen Historical-to-Mechanical Mapping

The audited broader lesson is temporal pursuit around commitment. The repaired chassis therefore has target-only Preparation and immediate target-only Recovery branches, one learned entry, 1S declaration spend, Attack Boon, normal damage, no Vom Tag gate, no persistent Recovery status, and no guard-change trigger.

## Nachreisen Decision Tree

On a Committed declaration: choose immediate free Counter, 1S Preparation Nachreisen, or wait. If the roll hits, waiting permits ordinary simultaneous Counter; if it misses, waiting permits 1S immediate Recovery Nachreisen. At 0S the two free Basic choices remain. These motives are condition-, risk-, and resource-distinct.

### Exact comparison at Skill 14

| Choice | Trigger | S | Attack success | Expected outgoing damage per committed declaration | Timing |
|---|---|---:|---:|---:|---|
| Immediate Basic Counter | declaration | 0 | 70.0% | 3.150 | first |
| Preparation Nachreisen | declaration | 1 | 91.0% | 4.095 | first |
| Wait -> Counter | hit | 0 | 70.0% conditional | 2.205 | simultaneous |
| Wait -> Recovery Nachreisen | miss | 1 | 91.0% conditional | 1.229 | immediate after miss |

## Zornhau-Ort Initial Repair

A qualifying descending Cut is sufficient; Committed is not required. Successful Zornhau spends action plus one learned entry and 0S, cancels, establishes contested Crossing, authors threatening point and Bind Initiative, and does no automatic damage or Hard/Soft authoring.

## Basic Cross vs Zornhau

Both use the same normal defence probability and establish Crossing. Cross is universal, chain-free, exposes state-based D1 when the point is nonthreatening, and does not automatically threaten. Zornhau is learned, costs one chain entry, has no ordinary Basic-D1 insertion window, creates threatening point, and opens intrinsic/repertoire bind continuations. Its distinction is rules-real without ghost utility.

## Minimal Bind Relation

When two successful comparable rolls create Crossing, lower is better. The winner is Favored and the other Unfavored. No new roll or generic modifier occurs; fixtures lacking comparable rolls remain Unknown. Hard/Soft pressure remains separate. Conditional tie frequency is 10.0%, 7.1%, and 5.6% at Skills 10/14/18. The provisional initiative tie rule gives the defensive initiative holder 55.0%, 53.6%, and 52.8% Favored frequency respectively, so the small systematic skew is flagged for Project review.

## Bind Initiative

The successful defensive Cross/Zornhau creator declares first even when Unfavored. Declining passes one opportunity to the opponent before cleanup. No secret simultaneous declarations or initiative roll were added.

## Fühlen

Fühlen reveals only Favored/Unfavored/Unknown and costs no action, Spiritus, or chain entry. Its exact Skill-14 information value is:

| Ort | Winden | Damage without | Damage with | Delta | Wrong S avoided |
|---|---|---:|---:|---:|---:|
| O1 | W1 | 2.250 | 3.825 | 1.575 | 0.500 |
| O1 | W2 | 3.150 | 3.825 | 0.675 | 0.000 |
| O2 | W1 | 1.764 | 3.339 | 1.575 | 0.500 |
| O2 | W2 | 3.150 | 3.339 | 0.189 | 0.000 |

## Ort O1 vs O2

| Model | Favored damage | Blind 50/50 damage | S/damage blind | S/damage with Fühlen | Kill HP4 | Kill HP6 | Kill HP8 |
|---|---:|---:|---:|---:|---:|---:|---:|
| O1 | 4.500 | 2.250 | 0.444 | 0.222 | 66.7% | 33.3% | 0.0% |
| O2 | 3.528 | 1.764 | 0.567 | 0.283 | 44.4% | 11.1% | 0.0% |

O1 is the stronger review candidate. Ort already requires successful Zornhau, immediate Bind Initiative, hidden Favored position, and 1S; O2 then reduces conditional mean damage from 4.500 to 3.528. Fühlen halves Spiritus per expected Ort damage by preventing the 50% wrong-state spend in the controlled blind model.

## Winden W1 vs W2

W1 supplies only 50% true applicability in the controlled relation mix and makes an untrained user risk 0.5 wasted Spiritus per blind declaration. W2 always has a legal thrust, while Ort remains the immediate-efficiency choice from Favored at Skill 14. W2 therefore produces less arbitrary information dependence; this is a recommendation for adjudication, not promotion.

## Ort / Winden / Fühlen Progression

Zornhau-Ort alone permits a hidden Ort gamble. Adding Winden supplies a second bind lesson but remains blind without Fühlen. Adding Fühlen alone makes Favored Ort legible and exposes Unfavored as having no available continuation. All three create the intended conditional curriculum: Ort from Favored; Winden from Unfavored; W2 additionally permits a normally inferior Favored thrust option.

### Eight exact Skill-14 configurations

| Ort | Wind | Fühlen | Favored choice | Unfavored choice | Damage/opportunity | Wrong S | Chain after Zorn | Wind from Favored |
|---|---|---|---|---|---:|---:|---:|---|
| O1 | W1 | no | Ort | Ort | 2.250 | 0.500 | 1.000 | no |
| O1 | W1 | yes | Ort | Winden | 3.825 | 0.000 | 1.500 | no |
| O1 | W2 | no | Winden | Winden | 3.150 | 0.000 | 2.000 | no |
| O1 | W2 | yes | Ort | Winden | 3.825 | 0.000 | 1.500 | no |
| O2 | W1 | no | Ort | Ort | 1.764 | 0.500 | 1.000 | no |
| O2 | W1 | yes | Ort | Winden | 3.339 | 0.000 | 1.500 | no |
| O2 | W2 | no | Winden | Winden | 3.150 | 0.000 | 2.000 | no |
| O2 | W2 | yes | Ort | Winden | 3.339 | 0.000 | 1.500 | no |

## Ochs / Pflug Aftermath and Gate Review

Neither Ochs nor Pflug is a starting gate. Minimal Winden records the least-specific supported upper/lower Ochs-or-Pflug hanging aftermath; side and height remain unresolved without authored context. No invented geometry or guard bonus follows.

## Frontale Repair

High-thrust Cross and low-thrust Beat remain universal Basics. The learned retreat/fendente/Dente/thrust/return sequence is decomposed in the prototype and Play record but not implemented. Smallest question: which blow is the principal ATTACK/test, are later blows intrinsic continuations, and may retreat remain event metadata until Force Movement exists? No generic Frontale bonus or Crown relationship was created.

## Deterministic Regression Results

**PASS: 81/81 required assertions**, plus authoritative-baseline P1/T1/C2 integration checks. The suite covers state-based D1, Open/GC1, Committed timing, both Nachreisen windows, Zornhau, bind position/initiative, Fühlen, O1/O2, W1/W2, aftermath, and chain cap.

## Controlled Micro-Experiment Results

All comparisons are exact enumeration/branch forcing; no Monte Carlo was needed. Skills 10/14/18 and Spiritus 8/3/1/0 are present in JSON. The 2x2x2 bind matrix uses Skill 14 and a controlled 50/50 relation, with Skill/tie sensitivities separately recorded.

## Spiritus / Chain Pressure

Immediate Counter and Basic Cross/Beat protect the 0S game. Both Nachreisen branches, Ort, and Winden spend 1S at declaration. Zornhau counts one; intrinsic Ort and passive Fühlen do not; Winden after Zornhau counts the second. The fourth learned Play remains illegal. W1's hidden prerequisite creates the largest avoidable waste.

## Policy and Ghost-Utility Cleanup

The authoritative engine and controlled analysis contain no Nachreisen 0.52 constant, unrealizable Soft utility, Cross-immunity bonus, P1-only Counter-first value, or guard bonus for an inactive Winden gate. Those values remain only in archived reproducibility engines and are explicitly quarantined; no replacement constant was tuned to force use.

## Remaining Historical/Mechanical Gaps

O1/O2 and W1/W2 require Project adjudication. The tie rule has a small initiative-holder skew. Exact Winden hanging side/height needs authored context. Full pressure/Yield, eight Windings, cut/slice branches, Duplieren/Mutieren, and Frontale's action/test compression remain outside this repair.

## Ready for Integrated Longsword Vertical Slice?

**Conditionally.** The minimum German repair is coherent and deterministic, but candidate selection and migration into a full current duel/policy loop remain before integrated balance evidence. Frontale is not mechanically complete, but it does not block the German slice.

## Exact Next Milestone

After Project adjudicates O1/O2 and W1/W2, perform **integrated engine cleanup**: migrate the synchronized exchange state machine into the current full duel loop and rebuild rules-derived policy/instrumentation. Do not start Named Guard v0.2 yet.

## Project Review Decision Table

| Topic | Old / candidate A | New / candidate B | Result | Recommendation (not promotion) |
|---|---|---|---|---|
| Counter timing | P1-only Counter-first | general Committed declaration window | consistent first/simultaneous branches | retain general rule |
| Nachreisen | persistent Recovering/free/Vom Tag policy chassis | 1S target-only two-window Attack-Boon model | distinct from Counter and nonpersistent | retain repaired model |
| Ort | O1 mean 4.500 | O2 mean 3.528 | O1 has better S efficiency; both gain from Fühlen | O1 for adjudication |
| Winden | W1 Unfavored-only | W2 either relation | W1 has 50% blind wrong-state risk; W2 mostly harmless Favored optionality at Skill 14 | W2 for adjudication |
| Fühlen | passive categorical visibility | no numeric bonus | positive damage decision delta and avoids wrong spend | retain passive model |
| Frontale | universal Cross/Beat mappings | learned sequence candidate | evidence complete enough to decompose, not to choose tests/actions | leave candidate-only |

## Final Project-Review Questions

1. **Yes.** The authoritative shared exchange engine is synchronized.
2. **Yes.** Blanket Cross immunity is removed from current behavior and durable current metadata; archived reports retain only labeled historical records.
3. **Yes.** Threatening opposing point denies D1; Crossing/form does not.
4. **Provisionally yes.** Beat->Open is clean; repertoire-poor Cross still depends on downstream Crossing value.
5. **Yes.** General Committed timing cleanly replaces the P1-only special case, and P1 inherits it.
6. **Yes.** Nachreisen buys Attack Boon and the miss-only Recovery branch for 1S; free Counter remains essential at 0S and for conservation.
7. **Yes.** Preparation buys early interruption accuracy; Recovery exploits a miss after waiting.
8. **Yes.** The target-specific window is immediate, nonpersistent, and needs no response-denial payload.
9. **Yes.** Zornhau buys threatening-point Crossing, Bind Initiative, and continuation access without automatic damage.
10. **Yes.** The two existing successful rolls determine the relation without another roll.
11. **Yes.** Initiative and position remain independent and sequence coherently.
12. **Yes.** Fühlen improves conditional decisions without a numeric bonus.
13. **O1 normal damage** is the stronger review candidate; not promoted.
14. **Yes provisionally** for O1 in this controlled model; Project adjudication remains required.
15. **W2 either relation** is the stronger review candidate; not promoted.
16. **Yes provisionally.** W1's blind waste is the concern, not the common 1S price.
17. **No.** Existing ATTACK/RETAIN/SET vocabulary is sufficient.
18. **Yes.** Ochs/Pflug should remain aftermath/entry geometry, not exclusive starting gates.
19. **Yes.** Zornhau -> Ort/Winden -> Fühlen forms a coherent minimum curriculum.
20. **No.** Frontale remains candidate-only pending its action/test decision.
21. **Candidate adjudication and full-loop integration** block the vertical slice; Frontale does not block the German core.
22. **Integrated engine cleanup**, after immediate O1/O2 and W1/W2 Project adjudication; not Named Guard v0.2.

Stop for Project adjudication. O1/O2 and W1/W2 are not automatically promoted.

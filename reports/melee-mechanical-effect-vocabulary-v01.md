# Atra Melee Mechanical Effect Vocabulary v0.1

Status: **PROVISIONAL rules-language and schema milestone for the current longsword vertical slice. Stop for Project adjudication.**

## Executive Result

The current longsword vertical slice closes with eight low-level operators: `ATTACK`, `CANCEL`, `SET`, `CLEAR`, `RETAIN`, `MODIFY_ATTACK`, `REPLACE_PENDING_ATTACK`, and exceptional `RESTRICT_RESPONSE`. Player-facing payload language sits above them: **Make Attack**, **Cancel Attack**, **Strip Guard**, **Change Measure**, and exceptional **Modify Response Tree**. `FORCE_MOVEMENT` is reserved for a second wave because no current governing mechanic requires a generic fighter-movement procedure.

The vocabulary exposes rather than repairs the known gaps. Current Nachreisen is a recovery trigger plus a normal attack and is redundant with a Basic. Current Zornhau-Ort initially buys no more than Basic Cross and relies on Soft that active combat does not create. Winden and the Frontale learned sequence have no complete payload. Pommel visibly bypasses the entire defender response call. Crown C1/B3 visibly combines free attacker context creation, a defender response that benefits the attacker, and a locally rational continuation inside a globally unmotivated setup.

The grammar is ready to constrain **Melee Repertoire Integrity Repair v0.1**. No prices, simulator behavior, historical Play records, or design-packet text were changed.

## Phase 0 Project Decisions Persisted

The Project-adjudicated Choice Architecture v0.1 result is now durable:

- **CB3:** Cross is D1-immune and succeeds as Cancel Attack + Establish Crossing. Beat retains the D1 window and succeeds as Cancel Attack + displacement event + End Contact + Strip Guard to Open.
- **Open:** no named guard, no guard intrinsic/Loaded/point threat/gates, no numeric penalty, all universal Basics remain legal, and next-own-activation recovery consumes the GC1 allowance.
- **GC1:** once per activation, before the action, change to any otherwise legal named guard; no post-action voluntary change.
- A restrictive voluntary transition graph is **REJECTED**. Source-supported action-produced and recovery transitions remain permitted as explicitly authored aftermath.
- Crown C1/B3 remains candidate-only; Named Guard v0.2 remains blocked.

Exactly these three durable Phase 0 files changed:

1. `data/prototypes/longsword-governing-provisional-v0.1.yaml`
2. `reports/governing-open-provisional.md`
3. `simulations/shared/provisional_longsword.py` (metadata only; no engine behavior change)

## Governing Baseline Preserved

D1 remains 1 Spiritus with declaration spend/no refund. Absetzen, Scambiar di Punta, and Schielhau remain C2 at 2 Spiritus. S2 remains the Schielhau/D1 interaction. T1 remains 1 Spiritus. P1 remains 1 Spiritus, fixed 7, Committed, Counter-first, and not a learned Play. The learned-Play cap remains three. Loaded remains Damage Boon only on proactive Basic Cuts. No generic guard bonus, random bind, automatic Soft/Close/zone generation, Open modifier, breaker modifier, voluntary adjacency graph, or Crown promotion was added.

The shared entry point still selects an archived engine that permits D1 against Cross and does not implement governing Open/GC1. This is an explicit implementation lag, not a silent rules conflict and not repaired here.

## Why a Mechanical Grammar Is Needed

A historical name, tactical trigger, or source description can be meaningful while supplying no game choice. A Play is mechanically complete only when its trigger buys a concrete change in resolution, public state, measure, guard, tempo/recovery, or legal response structure that makes it rational relative to the nearest Basic. The separate fields prevent “opponent is Recovering,” “the blade is displaced,” or “control” from masquerading as a payload.

## Play Grammar v0.1

Every mapped Basic/Play records:

- **Trigger:** declaration conditions; never counted as an effect.
- **Cost / Commitment:** action, Spiritus, learned slot/chain, guard/equipment gate, Committed, no-refund, or allowance consumption.
- **Test:** one existing uncertainty procedure, no new universal opposed-roll system.
- **Primary Payload:** what is principally purchased.
- **State Aftermath:** public state left by resolution.
- **Continuation:** future permission/value created by the result; not automatically a payload.
- **Opponent Counterplay:** rational remaining alternatives, or an explicit review flag when none exists.
- **Event Metadata:** source-facing events that do not independently change game state.

## Primary Payload Vocabulary

| Term | Definition | Low-level form |
|---|---|---|
| Make Attack | Resolve one weapon attack under the specified existing procedure. | `ATTACK` |
| Cancel Attack | The pending incoming attack does not resolve. | `CANCEL pending_attack` |
| Strip Guard | Set the target's guard to Open. | `SET guard=open` |
| Change Measure | Assign an explicit direction, such as Wide -> Close. | `SET measure=close`, requiring Wide |
| Force Movement | Reserved until fighter movement/engagement rules exist. | Deferred |
| Modify Response Tree | Remove, narrow, bypass, replace, or exceptionally reorder a normal response. Red-flag class. | `RESTRICT_RESPONSE` or `REPLACE_PENDING_ATTACK` |

“Intercept” is a timing/chassis description: reactive Trigger + Cancel Attack + any attack or aftermath. It is not another atom.

## State / Aftermath Vocabulary

`ESTABLISH_CROSSING` is `SET contact=crossing`. `RETAIN_CROSSING` is `RETAIN contact=crossing` and requires Crossing already to exist; it suppresses cleanup and does not recreate the original Cross. `END_CONTACT` is `CLEAR contact -> none` and does not change measure. Point threat is `SET point_threat=<value>`. Action-produced guard recovery is `SET guard=<named id>` and says nothing about voluntary adjacency. Recovery uses `SET recovery=recovering|ready`. Contact zone and pressure use controlled `SET` operations only when an action, Play, or identified fixture authors the value.

Generic `Control` is forbidden as **TOO VAGUE / REQUIRES DECOMPOSITION**.

## Trigger Vocabulary

The bounded set covers activation timing; incoming Cut/descending Cut/committed Cut/Thrust; after declared Beat and before its roll; after successful Cross and before cleanup; Crossing/Close Crossing; Hard/Soft and contact zone; Wide/Close; Recovering; named guard; point threat; displacement event; prior Play; action readiness; Spiritus; and chain capacity. “Opponent is Recovering” and “opponent is Soft” are triggers, not payoffs.

## Cost / Commitment Vocabulary

The grammar recognizes action, reaction action, no additional action, Spiritus, learned slot/chain entry, guard and equipment prerequisites, Committed, no refund, guard-change allowance, and chain-cap consumption. These are comparisons against payload value, never payloads themselves.

## Test Vocabulary

Allowed tests are normal weapon attack roll, normal defence roll, no test/no additional roll, and the already-governing S2 roll comparison. S2 is explicitly scoped; it does not create a new universal opposed-roll architecture.

## Event Metadata

Displacement is a nonpersistent event. No current active mechanic consumes it. Basic Beat additionally Ends Contact and Strips Guard, but those are authored consequences independent of the displacement event. Historical timing/action labels and source-facing transitions are also metadata unless a rule writes state.

## Exceptional Effects

- D1 uses `REPLACE_PENDING_ATTACK`: it substitutes a fresh attack for the pending resolution and skips the declared Beat roll. This is more precise than `CANCEL + ATTACK`, which could imply an additional independent attack. A broad `REDIRECT` operator is unnecessary.
- P1 Counter-first changes resolution order only against Power.
- S2 compares the established Schielhau result with the D1 roll only in its sourced branch.
- Pommel currently calls no defender response procedure at all.
- Candidate Crown Sink also calls no additional defence; it remains non-governing.

## State Registry

| State | Visibility / duration / owner | Cleanup | Writers | Readers / cautions |
|---|---|---|---|---|
| Guard, including Open | Public; persistent; fighter | None until changed/stripped | GC1, Beat->Open, authored aftermath, Open recovery | Intrinsics, gates, breakers; Open is not a named guard |
| Contact | Public; exchange-persistent; exchange | Crossing -> none at exchange end unless retained | Cross, joined Plays, authored binds, End Contact | T1, Pommel, Winden/bind material |
| Measure | Public; persistent; fighter pair | No contact-derived cleanup | Setup and explicit Change Measure | Contact is not measure; T1/Pommel read it |
| Contact zone | Public; contact-bound; per fighter | Unknown when contact ends | Authored action/Play or identified fixture | Never randomly/margin/guard derived |
| Pressure | Public; contact-bound; per fighter | Unknown when contact ends | Authored action/Play or diagnostic fixture | No active normal writer creates Soft |
| Point threat | Public; persistent; per fighter | Guard/Open/action/Play changes it | Guard mapping, Open, explicit aftermath | D1 prerequisite and guard identity |
| Loaded | Public through guard; derived; fighter | Recompute on guard/Open change | No direct writer | Read by Loaded Cut/P1; currently Donna-derived |
| Recovery | Visibility unresolved; transient; fighter | **Under-specified**; engine clears on selected Nachreisen | Missed committed cut, future recovery/consumer | Nachreisen trigger; do not infer a completed procedure |
| Action available | Public by sequence; round; fighter | Round-end refresh | Spend/refresh/explicit future preservation | All actions/reactions |
| Guard-change allowance | Public by sequence; activation; fighter | Next own activation | GC1/Open recovery | Prevents second change |
| Spiritus | Visibility unresolved; encounter resource; fighter | Short rest | Spend/refill | Cost legality/resource choices |
| Committed | Public declaration; attack/exchange; attack object | Resolution | P1/committed-cut chassis | Continuations, Counter-first, recovery, Zorn trigger |
| Learned-chain count | Public declarations; exchange | Exchange end | Learned declarations | Cap three |
| Pending attack | Public transient; exchange | Resolve/cancel/replace | Attack, Cancel, D1 replacement | Defence and damage procedures |
| Crown context | Public exchange transient | Candidate cleanup | Candidate Crown only | Candidate Sink only; non-governing |

## Low-Level Operator Model

The closed set is:

`ATTACK`, `CANCEL`, `SET`, `CLEAR`, `RETAIN`, `MODIFY_ATTACK`, `REPLACE_PENDING_ATTACK`, `RESTRICT_RESPONSE`.

`MOVE` is omitted because the current vertical slice requires measure assignment but no generic grid/fighter movement payload. `REPLACE_PENDING_ATTACK` is the one genuine addition to the prompt's candidate set; governing D1 requires it. `RESTRICT_RESPONSE` remains exceptional rather than an ordinary inexpensive operator.

## Primary Payload vs Aftermath

Absetzen shows the distinction. Its principal purchase is Cancel Attack + Make Attack in one Remedy. Crossing, Wide, unknown zones/pressure, and threatening point describe the successful physical result. They matter, but four changed state fields do not become four equal-price payloads. T1 likewise buys retention and measure change; it does not rebuy the original Basic Cross.

## Effect-Budget Review Framework

| Category | Examples | Review concern |
|---|---|---|
| Payload-heavy | Attack, cancel, strip guard, response modification | Direct resolution/action compression; response changes are red flags |
| Positional/state | establish/retain Crossing, measure, point, guard, pressure/zone | Duration, cleanup, downstream consumers, reciprocal risk |
| Permission/tempo | response restriction, action restoration, replacement/order changes | Opportunity denial/action compression; potentially much stronger than field count suggests |

Practical value also depends on trigger narrowness, action and Spiritus cost, learned-slot/chain cost, failure risk, Committed, downstream reciprocal risk, and opponent counterplay. There is no “one effect = 1S” rule. Existing prices are preserved and no unresolved Play receives a price recommendation.

## Universal Basic Mapping

- **Cross:** Cancel Attack; aftermath Establish Crossing. D1 immunity belongs to declaration/response architecture. It is complete but intentionally repertoire-dependent.
- **Beat:** Cancel Attack + Strip Guard; aftermath End Contact; displacement metadata. D1 vulnerability belongs to timing. No operation is redundant.
- **Counter:** Make Attack while accepting the incoming attack; value depends on HP and timing.
- **Ignore:** Retain action availability while accepting damage; mechanically real, though current policy does not value future action explicitly.
- **GC1:** Set chosen legal named guard before action, consume the allowance, and retain the public posture.

## Governing Play Mapping

- **D1:** `REPLACE_PENDING_ATTACK`, End Contact, actor point threatening. A distinct replacement operator is necessary; generic Redirect is not.
- **C2 Absetzen / Scambiar:** principally Cancel Attack + Make Attack. Crossing and point geometry are aftermath. Their shared chassis is legitimate compression, not a new payload per historical name.
- **S2 Schielhau:** Cancel + Attack with separated threatening-point aftermath; the reactive D1 comparison is explicit. The sourced proactive Pflug breaker remains unimplemented.
- **T1:** Retain Crossing + Wide -> Close. The original Cross is not T1 payload.
- **Loaded / P1:** Damage Boon, fixed maximum normal damage, Committed, and Counter-first are attack parameters/commitments.
- **Pommel:** Attack + exceptional response denial; current code bypasses `defend()` entirely.

## Incomplete Play Diagnostics

- **Nachreisen:** Trigger = opponent Recovering; Payload = Make Attack. The trigger is not a payoff. No accuracy, damage, tempo, response, or continuation advantage exists, and the active engine does not enforce the recorded Vom Tag gate.
- **Zornhau-Ort:** Initial payload is only Cancel Attack with Crossing aftermath, duplicating Basic Cross at learned-slot cost. Ort requires opponent Soft, but normal active combat has no Soft writer. Its simulated continuation value is ghost utility.
- **Winden:** Existing public axes—Crossing, pressure, contact zone, point threat, measure, and Ochs/Pflug access—are enough to express a future lesson, but no test, cost, payload, or counterplay is active. No Soft is invented.
- **Frontale:** High-thrust Cross and low-thrust Beat are universal Basic mappings. The source-supported retreat/fendente/Dente/thrust/return sequence remains an unimplemented learned candidate; its action-produced guard transition does not imply voluntary adjacency.

## Candidate-Only Diagnostics

Scheitelhau/Crown C1/B3 remains candidate-only. The grammar makes its problem explicit:

1. The attacker receives the Scheitelhau entry context by a free/automatic tag on an otherwise identical Basic Cut.
2. Crown uses the defender's normal action/roll but grants the attacker a continuation without a defender-side benefit over generic Cross/Beat/Counter.
3. Sink Point is locally rational once Crown exists, but that does not motivate the globally unmotivated setup.
4. The candidate Sink implementation also lacks another defender response call.

No promotion, Alber solution, or repair follows.

## Nearest-Basic Comparison Table

| Technique | Status | Trigger | Cost | Test | Principal payload | Aftermath / continuation | Nearest Basic | Distinct reason | Classification | Missing mechanic | Exceptional? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Basic Cut | Basic | Proactive action | Action | Attack | Attack | Cut tree; recovery on missed committed cut | Thrust | Loaded/P1 and cut-response tree | Complete—state | None | No |
| Basic Thrust | Basic | Proactive action | Action | Attack | Attack | Thrust compound tree | Cut | Avoid cut liabilities; different responses | Complete—state | None | No |
| Basic Cross CB3 | Basic | Incoming attack | Reaction action | Defence | Cancel | Crossing; repertoire | Beat | D1 immunity; Crossing access | Complete—repertoire | None | No |
| Basic Beat CB3 | Basic | Incoming attack; D1 window | Reaction action | Defence | Cancel + Strip Guard | End Contact; displacement event | Cross | Open valuable guard | Complete—state | Archived engine lag | No |
| Counter | Basic | Successful incoming attack | Reaction action; accept hit | Attack | Attack | Damage trade | Cross/Beat | Remove vulnerable attacker | Complete—state | None | No |
| Ignore | Basic | Successful incoming attack | Accept hit | None | Retain action | Future activation tempo | Defend | Preserve action | Complete—state; ghost policy | Policy value | No |
| Guard change GC1 | Governing provisional | Before own action | Allowance/posture | None | Set guard | Guard intrinsic/gates | Stay | Desired state/access | Complete—state | Engine integration | No |
| Loaded Cut | Governing provisional | Loaded proactive Cut | Action/posture | Attack | Attack + Damage Boon parameter | Ordinary Cut tree | Basic Cut | Better damage without S | Complete—state | None | No |
| P1 Power | Governing provisional | Loaded proactive Cut | Action, 1S, Committed | Attack | Attack fixed 7 | No attacker insertion | Loaded Cut | Certainty vs reserve/flexibility | Complete—resource/state | None | Counter-first |
| Durchwechseln D1 | Governing provisional | After declared Beat, pre-roll | 1S, slot, no refund | Attack | Replace pending attack | End Contact; point threatening | Allow Beat roll | Substitute attack odds | Complete—resource/state | Cross immunity integration | Yes |
| Absetzen C2 | Governing provisional | Incoming thrust/Pflug | Action, 2S, slot | One defence roll | Cancel + Attack | Wide Crossing; point threat | Cross/Beat | Joined defence/offence | Complete—resource/state | None | No |
| Scambiar C2 | Governing provisional | Incoming thrust/Donna-Tutta | Action, 2S, slot | One defence roll | Cancel + Attack | Wide Crossing; point threat | Cross/Beat | Joined defence/offence | Complete—resource/state | Chassis watch only | No |
| Schielhau S2 | Governing provisional | Descending high cut | Action, 2S, slot | Defence; S2 if D1 | Cancel + Attack | Separate; point threat | Cross/Beat | Compound + sourced rejoinder | Complete—resource/state | Proactive Pflug entry absent | S2 |
| Tutta T1 | Governing provisional | Successful Tutta Cross at Wide | 1S, slot; no action | No extra roll | Retain Crossing + Close | Close consumers | Let cleanup occur | Repertoire opportunity | Complete—repertoire; ghost policy | Owner-value integration | No |
| Pommel | Governing provisional | Close Crossing | Action, slot | Attack | Attack + response restriction | End Contact | Ordinary attack | Bypasses defence | Complete—repertoire; ghost policy | Intent review | Yes |
| Nachreisen | Incomplete | Opponent Recovering | Action, slot | Attack | Attack | Clears Recovery | Ordinary attack | None | Redundant; incomplete; ghost | Distinct payoff + gate | No |
| Zornhau-Ort | Incomplete | Committed Cut; then Soft | Action, slot | Defence; point roll if Soft | Cancel | Crossing; conditional Ort | Cross | None in active combat | Redundant; incomplete; ghost | Initial payoff/Soft writer | No |
| Winden | Incomplete | Crossing + pressure/hanging | Undefined | Undefined | — | Future state decision | Cleanup/ordinary action | None implemented | Incomplete payload | Test/cost/payload/counterplay | No |
| Frontale sequence | Candidate | Incoming thrust/Frontale | Undefined beyond Basics | Undefined | — | Source sequence/action transition | Cross/Beat | None implemented | Candidate; redundant; incomplete; ghost | Whole learned mechanic | No |
| Crown C1/B3 | Candidate | Tagged Cut vs Alber/Crown | Basic; then 1S Sink | Attack/defence/attack | Attack; Cancel; candidate restriction | Crossing + Crown; Sink | Basic Cut/Cross/Beat | Only local continuation | Candidate; ghost | Reciprocal setup motive | Yes |

## Mechanical Completeness Classification

Complete/currently closed: Basic Cut, Thrust, Counter, Beat, Ignore, GC1, Loaded, P1, D1, Absetzen, Scambiar, Schielhau S2. Complete but repertoire-dependent: Cross, T1, and conditional Pommel. Redundant/incomplete: Nachreisen, Zornhau-Ort, and Frontale-as-learned-simple-mapping. Incomplete payload: Nachreisen, Zornhau-Ort, Winden, Frontale learned sequence. Candidate-only: Frontale learned sequence and Crown C1/B3. Pommel, D1, P1 Counter-first, S2, and candidate Crown include exceptional procedure; only response denial/replacement is represented with the red-flag operators.

## Schema / Validation Results

Artifacts:

- `data/rules/melee-mechanical-effect-vocabulary-v0.1.yaml`
- `schemas/melee-play-grammar-v0.1.schema.json` (repository-equivalent schema location)
- `data/audits/longsword-vertical-slice-mechanical-mapping-v0.1.yaml`
- `scripts/validate_melee_play_grammar.py`
- `tests/test_melee_play_grammar_v01.py`

The dependency-free validator reports **0 errors and 22 informative findings**. It flags empty payloads, no distinction from Basic, undefined operators/state writers, forbidden Control, trigger-as-effect misuse, unmarked response modification, absent nearest Basic/distinction, missing effects, and ghost utility. Incomplete/candidate records remain valid data and produce expected findings instead of being promoted. Three focused tests pass.

## Contradictions or Vocabulary Gaps

1. Governing CB3/GC1 now supersedes the archived engine selected by the shared entry point.
2. Recovery visibility and normal cleanup are under-specified; current code clears Recovery only on selected Nachreisen.
3. Spiritus visibility remains unresolved.
4. No active normal writer creates Soft.
5. Contact cleanup must not silently reset measure.
6. Pommel and candidate Crown Sink bypass normal responses.
7. Current S2 does not implement the separately sourced proactive Pflug breaker.

Only `REPLACE_PENDING_ATTACK` had to be added for an already-governing mechanic. No other governing mechanic requires an absent operator.

## Repertoire Repair Input Brief

Primary repair techniques should be exactly:

- Nachreisen;
- Zornhau-Ort;
- upper/lower Winden decision material;
- Frontale retreat-fendente-thrust sequence.

Associated gate/integration checks are Vom Tag -> Nachreisen, Ochs/Pflug -> Winden, and Frontale owner access. Alber remains an owner-side repertoire constraint, but the next milestone must not assume Crown is its solution.

The repair must not invent random/automatic Soft, generic Control, generic guard bonuses, an Open penalty, voluntary adjacency, automatic breaker modifiers, an unsourced Alber technique, response denial as a default reward, effect-count pricing, or historical evidence.

## Exact Next Milestone

Run **Melee Repertoire Integrity Repair v0.1** against the vocabulary/schema above. Require deterministic motivation comparisons against each nearest Basic before any Named Guard v0.2 balance matrix. Do not broaden into guard balance, source survey, or price tuning.

## Final Project-Review Questions

1. **Smallest closed vocabulary?** `ATTACK`, `CANCEL`, `SET`, `CLEAR`, `RETAIN`, `MODIFY_ATTACK`, `REPLACE_PENDING_ATTACK`, exceptional `RESTRICT_RESPONSE`.
2. **True primary payload effects?** Make Attack, Cancel Attack, Strip Guard, explicit Change Measure; response modification is exceptional.
3. **States/aftermath?** Crossing/retention/contact ending, point, guard/Open, recovery, measure, pressure/zone, Loaded, Committed, action/chain state.
4. **Triggers?** Incoming form/timing, declared response, contact/measure/pressure/zone, Recovering, guard/point, displacement occurrence, prior Play, and resource/action availability when used as conditions.
5. **Displacement more than metadata?** No current consumer exists.
6. **D1 replacement operator?** Yes, `REPLACE_PENDING_ATTACK`; no generic Redirect.
7. **Accuracy/damage representation?** ATTACK/MODIFY_ATTACK parameters: normal/Boon/Bane accuracy, normal/fixed-max damage, Damage Boon/Bane, commitment, counter timing.
8. **Is Retain necessary?** Yes; T1 must not recreate or rebuy Cross, and Ignore preserves action availability.
9. **Resulting guards as aftermath?** Yes, `SET guard=<id>` with no voluntary adjacency implication.
10. **Mechanically complete?** The Basics, GC1, Loaded/P1, D1, C2 compounds, S2, T1, and conditional Pommel, with the qualifications above.
11. **Intentionally repertoire-dependent?** Cross, T1, conditional Pommel.
12. **Redundant with Basic?** Current Nachreisen, current Zornhau-Ort initial phase, and Frontale's simple mappings as learned identity.
13. **Incomplete payloads?** Nachreisen, Zornhau-Ort, Winden, Frontale learned sequence.
14. **Ghost utility?** Ignore/T1/Pommel policies, Nachreisen, Zornhau-Ort, Frontale occupancy, Crown C1/B3.
15. **Exceptional response modification?** D1 replacement, P1 Counter-first, S2 comparison, Pommel bypass, candidate Crown Sink bypass.
16. **Missing governing effect?** Only the newly named replacement operator required by D1; otherwise no.
17. **Deferred vocabulary?** Force Movement procedure; throw/prone/seizure/immobilization; generic leverage/Soft; numeric pricing.
18. **Ready to constrain repair?** Yes.
19. **Exact repair techniques?** Nachreisen, Zornhau-Ort, Winden upper/lower material, Frontale learned sequence, with associated guard-gate checks; Alber remains a constraint, not a Crown promotion.
20. **Forbidden inventions?** Random Soft, Control, guard/Open numeric modifiers, adjacency, breaker bonuses, unsourced Alber solution, default response denial, effect-count pricing, and invented evidence.

Stop for Project adjudication.

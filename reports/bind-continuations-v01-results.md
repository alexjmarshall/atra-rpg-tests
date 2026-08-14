# Bind Continuations v0.1 Results

Status: **PROVISIONAL state-transition / representation experiment; not canonical mechanics**

The explicit Crossing engine can now represent authored Soft pressure, an authored Wide-to-Close transition, and known asymmetric or bilateral blade geometry in deterministic fixtures. None of those harness-only creators entered the active mirrored combat repertoire, and the smoke regression retains zero natural Soft, Close, and known-zone creation.

## Scope and preserved baseline

This experiment preserves Contact `none|crossing`, independent Measure `wide|close`, per-fighter contact zones and pressure, point threat, displacement as an event, declared Basic Cross/Beat, D1, C2, S2, maximum Spiritus 8, and the learned-Play chain cap of 3. It adds no Guard effect, random state generation, generic leverage rule, generic Hard/Soft menu, Spiritus/damage tuning, or normal-combat repertoire entry.

## EVIDENCE AUDIT CORRECTION

The prior Zwerchhau record covered the initial interception but did not yet include the separately attested **Zwerch with the Strong** bind-work instruction. The added phase-level witness is Pseudo-Peter von Danzig, Cod.44.A.8 (1452), ff. 20r.2–20v.1. It instructs binding on the opponent's sword with the Strong of the acting sword. The geometry fixture is sourced only to that instruction and must not be generalized to every Zwerchhau execution.

The initial interception remains separately represented as beginning without blade contact and does not automatically create a Crossing. The whole Play record remains `needs-item-level-audit`; only the added witness/phase is item-level audited here.

## Forced-Scenario Metrics

| # | Scenario | Deterministic outcome |
|---:|---|---|
| 1 | Hard/Hard Crossing | contact `crossing`; pressure `{'A': 'hard', 'B': 'hard'}` |
| 2 | Diagnostic Yield | declared `True`; no damage/cost; classification OPEN |
| 3 | Resulting Soft/Hard | pressure `{'A': 'hard', 'B': 'soft'}`; contact retained |
| 4 | Zornhau-Ort inspects Soft | executed `True` after inspecting `soft` |
| 5 | Rompere displacement + retained Crossing | contact `crossing`; measure `wide`; retained `True` |
| 6 | Rompere Wide -> Close | explicit transition `True`; contact/measure `crossing/close`; random `false` |
| 7 | Pommel from Close Crossing | prerequisite `True`; executed `True` |
| 8 | Zwerch with the Strong | zones `{'A': 'hiltward', 'B': 'unknown'}`; pressure unknown/unknown; no modifier |
| 9 | Pointward/pointward reference | contact/measure `crossing/wide`; zones pointward/pointward |
| 10 | Middle/middle reference | contact/measure `crossing/wide`; `middle != close` |
| 11 | Geometry/pressure independence | hiltward/pointward + soft/hard and pointward/hiltward + hard/soft both represented without modifiers |
| 12 | Displacement/contact independence | Basic Beat displaces + separates; Rompere displaces + retains Crossing |
| 13 | Cleanup/reset | Yield and Zwerch sequences reset contact, zones, and pressure; Pommel sequence ends contact; retained Rompere survives its explicit window |

The Yield sequence proves state visibility and timing only. It does **not** decide that intentionally yielding should normally let the opponent hit. **HISTORICAL TECHNIQUE MECHANICS INCOMPLETE.**

## Authored State Creators

The test harness can now explicitly produce:

- Soft pressure through diagnostic Yield/Give Way.
- Close Crossing through the Rompere close-control continuation.
- Hiltward actor contact through the sourced Zwerch-with-the-Strong phase.
- Middle contact through Rompere's opponent-middle state and the middle/middle representation reference.
- Pointward contact through the pointward/pointward representation reference.
- Displacement plus retained Crossing through Rompere.

The Italian bilateral point and middle fixtures are representation references with missing item-level locators/confidence in the current repository. They do not strengthen the historical record or become generic actions.

## Small Unchanged-Combat Smoke Regression

Seed `11082026`; `2000` mirrored fights per cell; Skills 10/14/18; starting Spiritus 8; Adaptive Revelation only. Crossing/Bind v0.1 references use its stored 5,000-fight cells. Paired columns show `current / Crossing v0.1`.

| Cell | Win A | Rounds | Double | Cross/fight | Beat/fight | D/fight | Compounds/fight | Crossings/fight | Close | Soft | Known zone | Violations | Cap | Fourth |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| skill10_S8_adaptive_revelation | 47.7% / 48.1% | 4.359 / 4.348 | 3.1% / 3.4% | 0.410 | 0.414 | 0.444 | 0.712 | 0.413 | 0.000 | 0.000 | 0.000 | 0 | 0.4% | 0.000 |
| skill14_S8_adaptive_revelation | 46.4% / 47.2% | 3.185 / 3.197 | 6.7% / 7.2% | 0.152 | 0.157 | 0.566 | 1.085 | 0.561 | 0.000 | 0.000 | 0.000 | 0 | 0.6% | 0.000 |
| skill18_S8_adaptive_revelation | 43.6% / 44.1% | 2.713 / 2.704 | 14.1% / 13.5% | 0.025 | 0.026 | 0.544 | 1.311 | 0.806 | 0.000 | 0.000 | 0.000 | 0 | 0.2% | 0.000 |

The ordinary combat code path and active repertoire are unchanged. Sampling differences against the stored 5,000-fight reference are Monte Carlo noise; the structural regression signals are exact zeros for natural Close, Soft, known-zone creators, precondition violations, and attempted fourth Plays.

## Still Missing From Normal Combat

**ENGINE CAN REPRESENT** authored Soft, Close, hiltward/middle/pointward geometry, and displacement with or without retained contact.

**ACTIVE REPERTOIRE CAN NATURALLY PRODUCE** only the pre-existing bounded prototype states. Diagnostic Yield, Rompere close control, Zwerch-with-the-Strong geometry, and the Italian geometry references remain absent from normal AI combat. Consequently the smoke run correctly retains zero natural Soft-pressure, Close-Crossing, and known-zone creation. Those zeros were not 'fixed.'

## Historical Mechanics Still Incomplete

- Complete Yield/giving-way mechanics remain OPEN: sourced follow-up exploitation, attack content, action cost, Spiritus cost, defence implications, and learned-Play-chain counting are not decided.
- The Rompere close continuation's classification remains OPEN: intrinsic branch, second learned Play, Basic action, Aftermath, and action cost were not selected.
- Crossing persistence through complex continuations remains OPEN beyond the one-window harness sequence.
- Generic Strong-vs-Weak leverage, generic closing rules, generic Hard/Soft actions, and Guard effects remain OPEN and unimplemented.
- Bilateral Italian pointward and middle zone mappings still need item-level evidence locators before they can become historical Play claims.
- The optional Durchlaufen reference was skipped because its current Play record has only source-family citations and no item-level audited locator; the experiment did not expand into a Durchlaufen research task.

## Ready For Guard Design?

A. **Yes.** The engine can represent authored Crossing, authored displacement, authored Soft, authored Close, and authored blade geometry.

B. **No listed contact state remains blocked at the engine level.** The remaining uncertainty is which audited Plays/actions produce those states and how their full mechanics work.

C. Remaining gaps are mainly **Play repertoire/content and classification gaps**, rather than state-model gaps.

D. **Yes, provisionally.** Guard design can resume without inventing missing contact-state axes, provided Guard work does not turn these fixtures into generic bonuses or silently finalize their OPEN action economy.

E. Guard-facing evaluation can now examine point threat, loaded attack, quality of cover, tendency or ability to produce particular crossing geometry, and access to source-specific continuations. This report proposes no final Guard bonus.

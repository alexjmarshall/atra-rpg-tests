# Named Guard Runtime Parity Repair v0.2 — Results

## Executive Result

**PASS.** The two runtime/data parity defects exposed by the local Named Guard v0.2 audit are repaired without changing any guard design, Spiritus price, learned-Play rule, H3/S2/T1 behavior, or governing guard data.

The authoritative shared engine now:

1. accepts only the eight current governing named-guard IDs for GC1 voluntary guard changes; and
2. derives the intrinsic starting point-threat state of Ochs, Pflug, and Mezza Porta di Ferro when no explicit authored point state is supplied.

The full repository suite passes **169/169** after repair. Repository validation remains **114 Play records, 0 errors, 39 preserved warnings**. The grammar suite remains green.

## Repair Scope

Current governing roster:

- Vom Tag
- Ochs
- Pflug
- Alber
- Posta di Donna
- Posta Frontale
- Tutta Porta di Ferro
- Mezza Porta di Ferro

Current intrinsic threatening guards:

- Ochs
- Pflug
- Mezza Porta di Ferro

No ninth guard was introduced. Open remains a separate non-named guard state and cannot be selected through ordinary GC1.

## Defect 1 — GC1 Allowlist

Before repair, `CurrentEngine.change_guard(actor, "ninth-invented-guard")` returned `True` and mutated the fighter into an undefined guard.

After repair, `change_guard` rejects any value outside the eight governing named guards. Rejection does not consume the guard-change allowance, Action, Spiritus, chain capacity, or point-threat event count and does not mutate guard state.

The selector now publishes the same eight IDs and asserts engine alignment.

## Defect 2 — Starting Guard Intrinsics

Before repair, a fighter constructed directly in Ochs, Pflug, or Mezza Porta di Ferro inherited the dataclass default `point_threat="not_threatening"`, even though the v0.5 packet and guard records define those guards as threatening.

After repair, if no explicit authored point-threat state is supplied, fighter initialization derives point threat from the starting guard exactly as GC1 does:

- Ochs → threatening
- Pflug → threatening
- Mezza Porta di Ferro → threatening
- all other current named guards → not threatening
- Open → not threatening

Point threat remains an independent combat axis after initialization. An explicit `point_threat` supplied by a special authored setup is preserved; this was required to keep ordinary D1 point-threat controls valid.

Initial intrinsic state does not increment the runtime `point_threat_events` instrumentation counter. A real GC1 transition from nonthreatening to threatening still does.

## Files Changed

- `simulations/shared/provisional_longsword_engine.py`
- `simulations/shared/provisional_longsword.py`
- `tests/test_named_guard_runtime_parity_v02.py`
- `reports/named-guard-runtime-parity-v02-results.md`
- `reports/named-guard-runtime-parity-v02-results.json`

No governing data, guard evidence record, historical Play record, or melee packet was changed.

## Validation

Pre-repair full discovery: **165/165 PASS**.

Post-repair:

- full unittest discovery: **169/169 PASS**
- H3 governing suite: **129/129 assertions PASS**
- T1/Close/Pommel governing suite: **140/140 assertions PASS**
- S2 governing suite: **86/86 assertions PASS**
- named-guard runtime parity suite: **4/4 methods PASS**
- repository validator: **114 records, 0 errors, 39 warnings**
- melee grammar tests: **PASS**

The repaired Named Guard v0.2 local harness now passes **61/61 deterministic checks**, including the previously failing no-ninth-guard and starting-point-threat checks.

## Design Impact

None. This repair makes runtime match already-published v0.5 guard state. It does not improve or weaken any guard beyond applying its existing state correctly at exchange start and enforcing the already-defined eight-guard roster.

The structural guard findings therefore remain interpretable:

- Ochs/Pflug/Mezza share the same voluntary threatening-point value, though Ochs and Pflug additionally matter as authored Winden destinations.
- Donna retains its Loaded/P1 identity.
- Tutta retains its T1/Close identity.
- governing-only Frontale remains mechanically thin.
- Vom Tag and Alber remain mechanically under-specified under current rules.

## Frontale Candidate Recheck

The bounded Frontale Retreating Fendente candidate was re-run after parity repair. The guard repair does not alter its result.

At Skill 14, conditional on a live successful incoming thrust:

| Response | Cancel chance | Expected incoming damage | Expected immediate outgoing damage | Cost / topology |
|---|---:|---:|---:|---|
| Hart Cross | 91% | 0.405 | 0 | free; Crossing/H3 |
| Beat | 70% | 1.350 | 0 | free; separation + Open |
| Frontale Retreating Fendente candidate | 70% | 1.350 | 3.150 | 2S + 1 chain; no contact |

A fixed-seed 50,000-trial sanity run reproduced these expectations closely: candidate cancel **70.186%**, incoming **1.34494**, outgoing **3.15658** per trial.

The candidate remains **PROMOTION-WORTHY**, subject to Project adjudication rather than automatic promotion.

## Remaining Questions

The runtime-parity blocker is closed. Remaining guard questions are design questions rather than engine parity defects, especially:

- whether to promote/revise Frontale Retreating Fendente;
- whether the first table-playtest roster should omit mechanically thin guards;
- proactive Schielhau vs Pflug;
- Alber/Crown;
- distinct future value for Mezza and Vom Tag.


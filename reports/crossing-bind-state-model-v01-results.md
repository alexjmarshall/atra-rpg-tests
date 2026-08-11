# Crossing/Bind State Model v0.1 Results

Status: **PROVISIONAL state-model/regression experiment; not canonical mechanics**

The explicit model is internally coherent in deterministic tests and the bounded mirrored matrix. It replaces synthetic bind, Soft, and Close generation with declared or Play-authored transitions while retaining P1, D1, C2, S2, maximum Spiritus 8, and the three-learned-Play cap.

## Scope and conflict audit

Atra Melee Design Packet v0.4 leaves Bind/Crossing procedure and Crown/Corona mechanics OPEN/DEFERRED. This experiment supplies a PROVISIONAL engine model only and does not update that packet. No Guard effect, generic leverage modifier, generic Hard/Soft choice, or generic closing procedure was added.

## State model

Persistent exchange state uses `contact: none|crossing`, independent `measure: wide|close`, per-fighter `contact_zone: hiltward|middle|pointward|unknown`, per-fighter `pressure: hard|soft|unknown`, and per-fighter `point_threat: threatening|not_threatening`. Displacement is an event whose `contact_after` may be `none` or `crossing`; it is not a contact state.

Crossing cleanup occurs in `Duel.finish_exchange()`, after resolution/aftermath and before the next activation. Unretained Crossings become `none`; explicitly retained Crossings are counted and preserved.

## Deterministic transition validation

All required cases A-M pass: Cross creates Wide Hard/Hard Crossing with unknown zones and no displacement; Beat displaces and separates; both declarations expose the same pre-roll D1 window; failed forms apply neither contact nor displacement; Absetzen and Scambiar cross while maintaining point threat then clean up; Durchwechseln remains pre-bind with a threatening point; Schielhau creates no automatic Crossing; Rompere represents displacement with retained Crossing; cleanup separates; and forced Close Crossing executes Pommel Strike.

## Primary regression matrix

Seed `11082026`; `5000` mirrored fights per primary cell. Skills 10/14/18; starting Spiritus 8/3; Adaptive Revelation/Perfect Information; P1 Cross/Beat, D1, C2, S2, maximum 8.

| Cell | Cross/fight | Beat/fight | Cross success | Beat success | Cross D1 | Beat D1 | Crossings/fight | Displace+separate | Wide | Close | Hard/Hard | Unknown pressure | D opp./decl./success | Compounds | Spiritus | Parry/Counter/Ignore | Chain | Cap | Fourth | Win A | Rounds | Double |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| skill10_S8_adaptive_revelation | 0.422 | 0.422 | 48.9% | 48.2% | 0.151 | 0.142 | 0.403 | 0.135 | 0.403 | 0.000 | 0.133 | 0.270 | 1.005/0.441/40.7% | 0.708 | 1.858 | 38.8%/19.4%/2.1% | 0.365 | 0.44% | 0.000 | 48.1% | 4.348 | 3.4% |
| skill10_S8_perfect_information | 0.467 | 0.445 | 51.0% | 51.1% | 0.158 | 0.154 | 0.454 | 0.148 | 0.454 | 0.000 | 0.158 | 0.297 | 1.008/0.402/45.7% | 0.684 | 1.769 | 41.7%/20.5%/2.3% | 0.276 | 0.30% | 0.000 | 48.2% | 4.369 | 3.1% |
| skill10_S3_adaptive_revelation | 0.555 | 0.552 | 51.6% | 48.7% | 0.132 | 0.138 | 0.422 | 0.202 | 0.422 | 0.000 | 0.218 | 0.204 | 1.181/0.335/43.8% | 0.334 | 1.002 | 48.4%/24.5%/2.5% | 0.305 | 0.20% | 0.000 | 48.0% | 4.562 | 4.3% |
| skill10_S3_perfect_information | 0.582 | 0.581 | 49.7% | 51.2% | 0.146 | 0.144 | 0.409 | 0.224 | 0.409 | 0.000 | 0.217 | 0.192 | 1.200/0.322/46.1% | 0.331 | 0.985 | 51.3%/25.8%/2.7% | 0.211 | 0.09% | 0.000 | 49.1% | 4.500 | 4.0% |
| skill14_S8_adaptive_revelation | 0.155 | 0.159 | 76.1% | 66.2% | 0.119 | 0.119 | 0.568 | 0.027 | 0.568 | 0.000 | 0.027 | 0.540 | 0.670/0.572/47.6% | 1.101 | 2.774 | 14.0%/28.5%/1.1% | 0.521 | 0.63% | 0.000 | 47.2% | 3.197 | 7.2% |
| skill14_S8_perfect_information | 0.186 | 0.180 | 70.0% | 74.4% | 0.141 | 0.136 | 0.602 | 0.033 | 0.602 | 0.000 | 0.032 | 0.571 | 0.547/0.449/56.6% | 0.998 | 2.446 | 16.7%/32.0%/1.4% | 0.420 | 0.34% | 0.000 | 47.1% | 3.158 | 8.6% |
| skill14_S3_adaptive_revelation | 0.308 | 0.298 | 71.0% | 67.9% | 0.170 | 0.167 | 0.604 | 0.089 | 0.604 | 0.000 | 0.098 | 0.506 | 0.780/0.489/59.4% | 0.628 | 1.745 | 25.1%/33.4%/1.6% | 0.410 | 0.24% | 0.000 | 46.4% | 3.434 | 9.1% |
| skill14_S3_perfect_information | 0.324 | 0.303 | 68.5% | 69.1% | 0.177 | 0.170 | 0.557 | 0.092 | 0.557 | 0.000 | 0.101 | 0.456 | 0.726/0.433/63.8% | 0.627 | 1.688 | 26.9%/37.0%/1.8% | 0.331 | 0.12% | 0.000 | 45.3% | 3.318 | 10.1% |
| skill18_S8_adaptive_revelation | 0.028 | 0.029 | 80.0% | 90.0% | 0.026 | 0.027 | 0.794 | 0.002 | 0.794 | 0.000 | 0.002 | 0.792 | 0.586/0.553/46.5% | 1.310 | 3.174 | 2.3%/35.9%/0.7% | 0.703 | 0.15% | 0.000 | 44.1% | 2.704 | 13.5% |
| skill18_S8_perfect_information | 0.035 | 0.035 | 100.0% | 100.0% | 0.033 | 0.034 | 0.843 | 0.001 | 0.843 | 0.000 | 0.002 | 0.841 | 0.344/0.325/54.3% | 1.151 | 2.627 | 3.0%/43.3%/0.7% | 0.558 | 0.08% | 0.000 | 41.5% | 2.585 | 17.4% |
| skill18_S3_adaptive_revelation | 0.073 | 0.081 | 92.0% | 92.3% | 0.048 | 0.052 | 0.855 | 0.026 | 0.855 | 0.000 | 0.023 | 0.832 | 0.462/0.377/57.9% | 0.888 | 2.153 | 6.0%/44.1%/0.9% | 0.544 | 0.07% | 0.000 | 40.2% | 2.864 | 20.0% |
| skill18_S3_perfect_information | 0.072 | 0.078 | 89.6% | 89.1% | 0.050 | 0.054 | 0.792 | 0.021 | 0.792 | 0.000 | 0.019 | 0.773 | 0.299/0.239/65.9% | 0.839 | 1.916 | 6.2%/50.2%/0.9% | 0.443 | 0.03% | 0.000 | 38.9% | 2.665 | 22.2% |

### Remaining required contact metrics — every primary cell

| Cell | Displace + retained Crossing | Hard/Soft | Soft/Hard | Known zone | Unknown zone | Explicit persistence | Exchange-end cleanup |
|---|---:|---:|---:|---:|---:|---:|---:|
| skill10_S8_adaptive_revelation | 0.000 | 0.000 | 0.000 | 0.000 | 0.403 | 0.000 | 0.403 |
| skill10_S8_perfect_information | 0.000 | 0.000 | 0.000 | 0.000 | 0.454 | 0.000 | 0.454 |
| skill10_S3_adaptive_revelation | 0.000 | 0.000 | 0.000 | 0.000 | 0.422 | 0.000 | 0.422 |
| skill10_S3_perfect_information | 0.000 | 0.000 | 0.000 | 0.000 | 0.409 | 0.000 | 0.409 |
| skill14_S8_adaptive_revelation | 0.000 | 0.000 | 0.000 | 0.000 | 0.568 | 0.000 | 0.568 |
| skill14_S8_perfect_information | 0.000 | 0.000 | 0.000 | 0.000 | 0.602 | 0.000 | 0.602 |
| skill14_S3_adaptive_revelation | 0.000 | 0.000 | 0.000 | 0.000 | 0.604 | 0.000 | 0.604 |
| skill14_S3_perfect_information | 0.000 | 0.000 | 0.000 | 0.000 | 0.557 | 0.000 | 0.557 |
| skill18_S8_adaptive_revelation | 0.000 | 0.000 | 0.000 | 0.000 | 0.794 | 0.000 | 0.794 |
| skill18_S8_perfect_information | 0.000 | 0.000 | 0.000 | 0.000 | 0.843 | 0.000 | 0.843 |
| skill18_S3_adaptive_revelation | 0.000 | 0.000 | 0.000 | 0.000 | 0.855 | 0.000 | 0.855 |
| skill18_S3_perfect_information | 0.000 | 0.000 | 0.000 | 0.000 | 0.792 | 0.000 | 0.792 |

All primary cells record zero retained-Crossing displacements, Close Crossings, Hard/Soft or Soft/Hard Crossings, known-zone Crossings, explicit persistence, and attempted fourth Plays. Unknown-zone Crossings equal total Crossings.

## OLD / LEGACY EXERCISE MODEL vs NEW / EXPLICIT CONTACT MODEL

The paired legacy harness preserves only the immediately previous explanatory artifacts: successful Basic Parry synthesizes Wide/Close contact with a 25% Close chance, Zornhau-Ort synthesizes opponent Soft with a 50% chance, and contact may reach a later activation. It is not a valid alternative model.

## Play Opportunity Changes

| Play | Old opportunities/fight | New opportunities/fight | Old uses/fight | New uses/fight | Reason |
|---|---:|---:|---:|---:|---|
| Absetzen | 0.675 | 0.717 | 0.266 | 0.262 | explicit point-threat state; policy substitution |
| Zornhau-Ort | 0.471 | 0.508 | 0.180 | 0.182 | random soft-bind removed; no Soft-producing action currently exists |
| Durchwechseln | 0.519 | 0.734 | 0.315 | 0.411 | explicit Cross/Beat choice; explicit point-threat state |
| Scambiar di Punta | 0.675 | 0.717 | 0.260 | 0.263 | explicit point-threat state; policy substitution |
| Nachreisen | 0.431 | 0.458 | 0.386 | 0.410 | contact now explicit; policy substitution |
| Pommel Strike | 0.026 | 0.000 | 0.022 | 0.000 | random close-crossing removed; no Close-producing action currently exists |
| Schielhau | 0.572 | 0.612 | 0.275 | 0.275 | explicit point-threat state; policy substitution |

Zornhau-Ort's initial counter-cut remains available, but its Ort continuation falls from `0.063` uses/fight in the synthetic legacy harness to `0.000` because no current explicit action produces opponent Soft pressure. Pommel Strike has no main-run opportunities: **MISSING CLOSE-MEASURE TRANSITION**. Its forced-state test passes, so the loss is not evidence that the Play is weak.

Cross and Beat have equal one-step cancellation value in the transparent softmax policy. Their selection frequencies are therefore coverage-sensitive and are not final balance evidence. Any later strong Beat dominance without mature Winden/bind continuations should be classified **BIND-REPERTOIRE COVERAGE ARTIFACT**.

## Synthetic State Removed

- `simulations/longsword_prototype_v0_1/simulate.py`: Basic defence assigned `bind-crossing` or random 25% `close-crossing`; named prototype resolutions also assigned `bind-crossing` directly.
- `simulations/longsword_prototype_v0_2/simulate.py`: `close_crossing_probability` created Close Crossing and `soft_bind_probability` created Soft Zornhau-Ort continuation conditions; named resolutions assigned contact states directly.
- `simulations/longsword_prototype_v0_2/state_model_simulate.py`: `legacy_random_half` assigned blade-seeking to 50% of Basic Parries, successful Parry used random 25% Close Crossing, and Zornhau-Ort used random 50% Soft.
- `simulations/spiritus_parry_durchwechseln/simulate.py`: successful Basic Parry used random 25% Close contact; Absetzen, Scambiar, Schielhau, and Zornhau-Ort assigned synthetic `bind` contact, with random 50% Ort continuation.
- `simulations/compound_spiritus_c1_c2/simulate.py` inherited those contact rules from the Spiritus base simulator and consumed synthetic Close contact for Pommel Strike.
- The old proactive-beat shortcut in `state_model_simulate.py` manufactured a Durchwechseln contact context; it is absent from the new primary model.

The prior behavior remains only in the labeled legacy comparison harness. No random bind, pressure, contact zone, or Close Crossing generation remains in the primary model.

## Missing State Creators

- **Soft pressure:** supported by the schema, but no current basic action or active Play explicitly creates it. Zornhau-Ort's Ort continuation therefore has no main-run trigger.
- **Close Crossing:** supported and force-tested, but no active main-run action closes measure while retaining contact. Pommel Strike therefore has zero main-run opportunity.
- **Explicit contact-zone geometry:** supported, and Rompere demonstrates opponent-middle geometry in the reference harness, but ordinary Basic Cross, Zornhau-Ort, Absetzen, and Scambiar remain `unknown` where the audit does not establish both blade zones.
- **Crossing retention:** supported and demonstrated by Rompere's displacement-with-retained-Crossing reference state, but no mirrored active Play currently retains a Crossing beyond exchange cleanup.

## Artifacts and limitations

The combat policy is a transparent one-step expected-value softmax, not a solved equilibrium or player forecast. Generic d6+1 damage, symmetric repertoires, artificial attack proportions, free Zornhau-Ort/Nachreisen/Pommel, unresolved weapon profiles, and absent Guard/engagement geometry remain artifacts. The run is a regression, not price or balance tuning.

## Recommended Next Decision

The explicit Crossing model is internally coherent, and Basic Cross/Beat are technically viable declared forms with the required pre-roll D1 timing. Zornhau-Ort loses its synthetic Ort continuation; Pommel Strike loses synthetic Close opportunities; the other active Plays change mainly through explicit Parry choice, point threat, and policy substitution.

The most urgent state creator is an explicit **close-measure-while-maintaining-contact transition**, because it gates a historically audited active Play and tests the independence of measure from contact geometry. A Soft-producing action is the next pressure question, but it should be sourced/audited rather than invented to restore Ort frequency.

The system is **not yet ready to return to Guard design**. The blocking question is: which explicit action or audited Play changes Wide Crossing to Close while retaining contact, and which action/Play can intentionally yield Soft pressure? Until those transitions exist, proposed Guard bonuses would be evaluated against a contact repertoire missing core measure and pressure pathways.

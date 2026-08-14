# Frontale Retreating Fendente — Governing Integration v0.1 Results

## Executive Result

**PASS — GOVERNING PROVISIONAL; NOT CANONICAL.** The Project-adjudicated Frontale Retreating Fendente candidate is promoted as the bounded guard-specific learned response for Posta Frontale. The promotion does not activate Fiore's entire longer sequence, add Dente di Zenghiaro as a selectable guard, create forced movement, or alter Cross, Beat, H3, S2, T1, Pommel, Winden, Spiritus baseline, or chain cap.

The first table-playtest guard roster is therefore **Ochs, Pflug, Posta di Donna, Posta Frontale, and Tutta Porta di Ferro**. The governing eight-guard data roster remains intact; Vom Tag, Alber, and Mezza Porta di Ferro are simply withheld from the first player-facing packet because their current distinct value is absent or duplicated.

## Promotion Authority

Named Guard v0.2's bounded guard audit classified governing-only Frontale as candidate-dependent and found the tested 2-Spiritus joined thrust defence/counter-cut to be promotion-worthy. The subsequent runtime-parity repair closed the two unrelated guard implementation defects (GC1 allowlist and starting point-threat initialization) and re-ran the Frontale comparison without changing its result. Project review then explicitly authorized proceeding with the proposed promotion and table-playtest packet.

## Historical Boundary

The source-facing lesson is the audited Fiore Frontale thrust-response material at Getty 24v-c, Morgan 12v-b, and Pisani Dossi 18b-b: the longer alternative retreats from the thrust, answers with a fendente, passes through Dente di Zenghiaro, renews the thrust, and returns with fendente.

The governing v0.1 mechanic intentionally isolates only the **first joined defensive fendente**. The following are Atra abstractions, not literal source claims:

- 2 Spiritus and +1 learned-chain entry;
- one flat Longsword test;
- same successful test both cancels and supplies the counter-cut;
- normal `d6+1` damage;
- no modeled forced movement;
- no Dente guard state;
- no later thrust or return-fendente continuation.

## Governing Procedure

**Frontale Retreating Fendente**

Trigger:

- defender is alive and in Posta Frontale;
- defender knows the Play;
- incoming attack is a live successful Thrust before contact;
- defender has the normal defensive Action;
- defender has at least 2 Spiritus;
- learned-chain cap has room.

Declaration:

- spend the defensive Action;
- spend 2 Spiritus;
- add +1 learned-chain entry;
- no refund after a legal declaration.

Test:

- one flat normal Longsword test.

Success:

- cancel the incoming Thrust;
- deal one normal `d6+1` Cut damage instance to the original attacker using the same successful test;
- no second attack roll.

Failure:

- do not cancel the incoming Thrust;
- deal zero counter-cut damage;
- the original Thrust remains unresolved and can resolve normally.

Aftermath:

- no Crossing;
- measure preserved;
- Frontale retained;
- no point-threat writer;
- no Open;
- no bind-height writer;
- no forced movement;
- no Dente guard state;
- no automatic continuation;
- no bespoke response denial.

## Incentive Rationale

The Skill-14 audit remains the governing promotion evidence for the bounded chassis, conditional on an already successful incoming thrust:

| Response | Cancel chance | Expected incoming | Expected immediate outgoing | Cost / topology |
|---|---:|---:|---:|---|
| Hart Cross | 91% | 0.405 | 0 | free; Crossing/H3 |
| Beat | 70% | 1.350 | 0 | free; separation + Open |
| Frontale Retreating Fendente | 70% | 1.350 | 3.150 | 2S +1 chain; no contact |

A fresh fixed-seed 50,000-trial sanity run (`1308202604`) produced 69.926% successful Frontale responses, 3.14892 outgoing damage/trial, and 1.34804 incoming damage/trial. This is a frequency check on the exact dice model, not a new tuning experiment.

Frontale therefore gains a rational but non-dominant reason over its nearest Basics: pay meaningful Spiritus/chain for immediate counter-cut damage, while Cross remains safer and enters the bind tree and Beat remains free with separation/Open.

## Data / Runtime Integration

Updated current-facing layers:

- `data/prototypes/frontale-retreating-fendente-v0.1.yaml`
- `data/prototypes/longsword-governing-provisional-v0.1.yaml`
- `data/guards/longsword-named-v0.1.yaml`
- `data/audits/longsword-vertical-slice-mechanical-mapping-v0.1.yaml`
- `reports/governing-open-provisional.md`
- `simulations/shared/provisional_longsword.py`
- `simulations/shared/provisional_longsword_engine.py`
- `tests/test_frontale_retreating_fendente_governing_v01.py`
- `tests/test_melee_play_grammar_v01.py`

Historical candidate reports and v0.5 were not rewritten. Packet v0.5 therefore remains the baseline packet plus this later governing adjudication; the first table-playtest packet carries the updated Frontale rule directly.

## Protected Mechanics

Unchanged:

- GC1 eight-guard allowlist and intrinsic point-threat initialization;
- ordinary D1;
- generic C2;
- S2;
- Hart/Weich and H3;
- Fühlen;
- D/M;
- Upper/Lower Winden and L2;
- Zornhau/Ort local compatibility;
- Beat/Open;
- Donna Loaded/P1;
- T1/Pommel;
- learned-chain cap 3;
- maximum-8 Spiritus test baseline;
- proactive Schielhau/Pflug remains OPEN;
- Crown remains DEFERRED.

## Validation

Post-integration:

- full unittest discovery: **173/173 PASS**;
- dedicated Frontale governing suite: **4/4 methods PASS**;
- H3 governing suite: protected and green;
- T1/Close/Pommel governing suite: protected and green;
- S2 governing suite: protected and green;
- named-guard runtime parity suite: protected and green;
- repository validator: **114 Play records, 0 errors, 39 preserved warnings**;
- melee grammar validator: **0 errors, 5 informative findings**.

The former four Frontale missing-payload/ghost findings are absent. Remaining grammar findings concern Basic Ignore, the scoped S2 exception/Pflug debt, and Crown.

## First Table-Playtest Roster

Use:

1. Ochs
2. Pflug
3. Posta di Donna
4. Posta Frontale
5. Tutta Porta di Ferro

Withhold from the first player packet:

- Vom Tag — no current unique runtime payoff;
- Alber — no current unique payoff; Crown remains deferred;
- Mezza Porta di Ferro — threatening-point value currently duplicates Ochs/Pflug without a unique learned continuation.

## Exact Next Milestone

**ATRA TABLE PLAYTEST PACKET v0.1** — package the reduced guard roster and a deliberately bounded learned repertoire into a printable first-table harness. No further broad melee or guard audit is required before that playtest.

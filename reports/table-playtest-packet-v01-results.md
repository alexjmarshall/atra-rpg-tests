# Atra Table Playtest Packet v0.1 - Publication Results

## Executive Result

**PASS - FIRST TABLE HARNESS PUBLISHED.** The current melee vertical slice is now packaged into a reduced-roster, player/referee-facing first-table packet. This milestone does not declare the melee system final and does not add a canonical initiative/opening system. It packages the synchronized v0.5 kernel plus the later governing-provisional Frontale Retreating Fendente v0.1 adjudication.

The immediate next step is empirical: run the packet at a physical table and record procedural friction before scheduling another broad combat-design pass.

## Inputs

The packet uses:

- Atra Melee Design Packet v0.5 as the primary governing-provisional kernel;
- Frontale Retreating Fendente v0.1 as the later governing-provisional Frontale rule;
- the repaired eight-guard GC1 allowlist and starting point-threat initialization;
- the current H3, T1/Close/Pommel, S2, Winden, Beat/Open, Loaded/Power, Spiritus, and learned-chain rules within the deliberately reduced harness scope.

The full eight-guard governing data roster remains unchanged.

## First-Table Roster

Included:

1. Ochs
2. Pflug
3. Posta di Donna
4. Posta Frontale
5. Tutta Porta di Ferro

Withheld from this first player-facing harness:

- Vom Tag - no current unique runtime payoff;
- Alber - no current unique payoff and Crown remains deferred;
- Mezza Porta di Ferro - its current voluntary threatening-point value duplicates Ochs/Pflug without a unique learned continuation.

Withholding is a playtest-roster decision, not deletion or demotion of the governing eight-guard data roster.

## Included Repertoire

The packet teaches and tests a bounded repertoire:

- Basic Cut / Thrust;
- Ignore, Counter, Cross, Beat;
- ordinary Durchwechseln D1;
- Hart/Weich and H3;
- Fuhlen;
- Duplieren / Mutieren;
- Upper / Lower Winding;
- Tutta Cover-to-Stretto T1;
- Pommel Strike;
- Frontale Retreating Fendente;
- Donna Loaded Cut;
- optional Power Attack after the introductory rounds.

Intentionally omitted from the first-table harness include Zornhau/Ort and its local relation, S2, generic C2 compounds, Nachreisen, Crown, proactive Schielhau/Pflug, broader stretto, grapple/throw procedures, and the broader historical catalog. Their omission does not change their governing/deferred status outside this harness.

## Frontale Status

Frontale Retreating Fendente is **GOVERNING PROVISIONAL; NOT CANONICAL** after v0.5. The packet presents its bounded current rule:

- defender in Posta Frontale;
- live successful pre-contact incoming Thrust;
- defensive Action + 2 Spiritus +1 learned-chain entry;
- one flat normal Longsword test;
- success cancels the Thrust and applies one normal `d6+1` Cut damage instance using that successful test;
- failure leaves the Thrust live and deals no counter-cut damage;
- no Crossing, Open, point threat, forced movement, Dente state, automatic continuation, or bespoke response denial.

The later historical thrust/return-fendente phases remain deferred.

## Harness-Only Round / Opening Procedure

The current governing slice does not yet contain a finalized player-facing initiative/opening procedure suitable for a stand-alone first session. The packet therefore supplies explicit **PLAYTEST HARNESS ONLY** scaffolding:

- both players secretly choose a starting guard and reveal;
- Duelist A has first activation in Round 1;
- Duelist B has first activation in Round 2;
- first activation alternates each round;
- each fighter refreshes one normal Action at round start;
- Health and Spiritus persist;
- GC1 occurs on that fighter's activation before their Action;
- if the fighter already spent the Action defensively, they may still make the GC1 choice but cannot take a second Action;
- learned chain clears only when the current attack/bind/Close exchange fully ends.

This procedure is not promoted to governing initiative law. The first table session should explicitly record whether this scaffolding creates confusion or undesirable timing incentives.

## Playtest Scenarios

The packet provides four staged uses:

1. **Guard-choice tutorial** - GC1, threatening point, Donna Loaded, D1, Cross/Beat, and Frontale's niche.
2. **Bind and Close drill** - hidden Hart/Weich, H3, Winding, T1, Pommel, opportunity, and learned-chain tracking.
3. **Frontale A/B drill** - direct comparison of Hart Cross, Beat, and Frontale Retreating Fendente, including low-Spiritus choice.
4. **Free duel** - all rules in this packet, with a 30-minute stopping condition and optional first-activation swap.

The packet's post-session questionnaire prioritizes legibility, timing, state tracking, resource load, guard choice, and pacing before asking broad balance questions.

## Deliverables

Published artifacts:

- `docs/table-playtest-packet-v0.1.md`
- `Atra_Table_Playtest_Packet_v0.1.docx`
- `Atra_Table_Playtest_Packet_v0.1.pdf`
- `data/sources/atra-table-playtest-packet-v0-1.yaml`

The governing design packet v0.5 remains preserved and primary for rules outside this harness.

## Layout / Rendering QA

DOCX was rendered through the repository document workflow to 20 page PNGs and inspected page-by-page. No clipping, overlapping text, missing glyphs, broken tables, or header/footer defects were found after replacing the original over-wide session-log table with printable exchange blocks.

The emitted PDF is byte-identical to the final copied PDF (`SHA-256 f43a49be8f043a9553b040ef604d1c3762163d77558a6f58d1fa12b264a2a9a8`) and renders to 20 pages under the PDF verification workflow.

## Mechanical Validation

After Frontale's preceding governing integration and before publication, the authoritative repository passed:

- full unittest discovery: **173/173 PASS**;
- dedicated Frontale suite: PASS;
- H3 protected suite: PASS;
- T1/Close/Pommel protected suite: PASS;
- S2 protected suite: PASS;
- named-guard runtime parity suite: PASS;
- repository validator: **114 Play records, 0 errors, 39 preserved warnings**;
- melee grammar validator: **0 errors, 5 informative findings**.

This publication milestone adds no further combat mechanic. Final validation is rerun after the report/source/readme additions.

## What the First Session Should Decide

The first session is not intended to settle statistical balance. It should answer questions such as:

- Can players identify when they still have an Action?
- Can they see the ordinary D1 window without designer prompting?
- Does threatening point make D1 denial intuitive?
- Are Cross and Beat perceived as distinct choices?
- Is Hart/Weich secrecy practical at a physical table?
- Can players explain what Fuhlen bought them?
- Is bind opportunity understood as first declaration opportunity rather than ownership?
- Can they track Upper/Lower/Unknown, pass cleanup, and learned chain without overload?
- Does Donna feel powerful but exposed rather than mandatory?
- Does Frontale Fendente make Frontale worth choosing while preserving reasons to Cross or Beat?
- Does T1 make Tutta distinct?
- Does the harness-only round structure create timing confusion?

## Project Status After Publication

The project now has a table-runnable melee vertical slice. It is still provisional and deliberately incomplete.

Do not insert another broad melee audit before collecting table evidence unless the playtest cannot proceed because of a concrete rules contradiction.

## Exact Next Action

**RUN ATRA TABLE PLAYTEST PACKET v0.1 AT THE TABLE.**

Bring back the session log and qualitative notes. The next adjudication should prioritize procedural friction and player mental-model failures before balance tuning or repertoire expansion.

**STOP FOR TABLE PLAYTEST.**

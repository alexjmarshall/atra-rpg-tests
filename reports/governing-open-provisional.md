# Governing OPEN, PROVISIONAL, and DEFERRED register

Transcribed from Section 2 of Atra Melee Design Packet v0.4. These entries are constraints and unresolved questions; this repository does not decide them.

## 2026-08-12 Melee Repertoire Integrity Repair v0.1 Project adjudication

The Project explicitly supersedes the conflicting provisional language below for the current longsword vertical slice. This is a **GOVERNING PROVISIONAL** synchronization, not a canonical/final promotion, and it does not edit Atra Melee Design Packet v0.4 or rewrite archived experiment reports.

### State-based D1 replaces blanket Cross immunity

The CB3 rule that a Cross declaration is automatically immune to Durchwechseln is **RETRACTED / SUPERSEDED**. Basic Cross and Basic Beat both expose the ordinary pre-roll D1 window when all normal prerequisites are satisfied. A threatening opposing point denies D1; Crossing or the name/declaration of Cross does not. Successful Cross remains Cancel Attack + establish ordinary Crossing with no generic modifier and no automatic point threat. Successful Beat remains Cancel Attack + displacement + End Contact + Strip Guard to Open. Failed Beat does not create Open, and failed-Beat self-Open remains unadopted.

Open and GC1 otherwise remain exactly governing: Open is no named guard and has no generic numeric penalty; next-own-activation recovery consumes the voluntary allowance; voluntary guard change is once before the action with no post-action change or voluntary transition graph.

### General Committed declaration timing

The former P1-only Counter-first behavior is **SUPERSEDED** by a general Committed declaration window. Before any Committed attack roll, the original target may spend their action on an immediate normal Basic Counter or a technique explicitly authored for Preparation. It resolves first; removal cancels the pending attack and survival permits it to proceed. A target who waits may use ordinary simultaneous Counter only after a successful attack roll. A miss creates no retroactive Counter. P1 inherits this timing while retaining its existing Loaded gate, 1-Spiritus declaration cost, fixed 7 damage, attacker-insertion restrictions, and Basic/non-learned classification.

### Scoped repertoire repairs

- **Nachreisen:** learned Play, 1 Spiritus, one chain entry, no Vom Tag gate. Target-only Preparation occurs before a declared Committed attack; target-only Recovery occurs immediately after its miss. Both make a normal Longsword attack with Attack Boon and normal damage. Neither window persists or follows guard change.
- **Zornhau-Ort:** Zornhau answers a qualifying descending Cut without requiring Committed, spends action plus one learned entry and 0 Spiritus, and on success cancels, establishes Crossing and a threatening point, and gives the defender Bind Initiative. It does not automatically damage or author pressure. Ort is intrinsic, costs 1 Spiritus, consumes no second learned entry or attack roll, and succeeds only from Favored Bind. O1/O2 remain comparison variants.
- **Favored/Unfavored Bind:** compare the two successful rolls that created a contested Crossing using lower-is-better. Exact ties provisionally favor the Bind Initiative holder. This creates no generic modifier and is separate from Hard/Soft pressure.
- **Bind Initiative:** the successful defensive Cross/Zornhau creator receives first immediate continuation declaration even when Unfavored. Declining passes one immediate opportunity to the opponent before cleanup.
- **Fühlen:** learned passive categorical visibility only; no action, Spiritus, or chain cost and no raw-roll disclosure.
- **Winden:** separate learned continuation at 1 Spiritus and one additional chain entry, with no additional normal action. It retains Crossing, keeps/sets point threat, establishes the least-specific supported Ochs/Pflug hanging aftermath, and makes a normal Thrust roll for normal damage. Ochs/Pflug are not exclusive starting gates. W1/W2 remain comparison variants.
- **Frontale:** universal high-thrust Cross and low-thrust Beat mappings remain Basic. The longer audited sequence remains candidate-only pending Project resolution of its action/test decomposition and how retreat is represented without a current Force Movement operator.

The synchronized behavioral implementation is `simulations/shared/provisional_longsword_engine.py`, selected by `simulations/shared/provisional_longsword.py`. Archived experiment engines remain unchanged and compatibility-labeled.

## 2026-08-12 Choice Architecture v0.1 Project adjudication — historical selection, partially superseded above

This section preserves the earlier same-day selection. The later Melee Repertoire Integrity Repair adjudication above retracts only CB3's blanket Cross immunity and supersedes the implementation-lag note; Beat->Open, Open, and GC1 remain governing.

### Cross / Beat — CB3 historical record

- **SUPERSEDED CLAUSE:** the former rule that Durchwechseln is not legal against a declared Cross is retracted above. The retained parts are that Basic Cross is universal and on success cancels the attack and establishes ordinary Crossing without a generic modifier.
- **Basic Beat** is a universal Basic defensive form. It retains the normal Durchwechseln window and all D1 prerequisites. On a successful resolution, cancel the incoming attack, record displacement as appropriate, end contact/separate under the current Beat chassis, and leave the attacker Open. Failed or D1-interrupted Beat does not create Open.

### Open

Open means the fighter currently occupies no named guard. While Open, no named-guard intrinsic, guard-derived Loaded, guard-derived point threat, guard-gated Play access, or other guard-specific access applies. Universal Basic attacks and defensive responses remain legal. Open supplies no automatic attack Boon, Parry Bane, accuracy modifier, damage modifier, or other numeric penalty, and is not a named guard.

At the fighter's next own activation, they may establish any otherwise legal named guard. Doing so consumes that activation's voluntary guard-change allowance, so a second voluntary guard change is illegal. Voluntarily remaining Open is legal.

### Guard commitment — GC1

> Once on your activation, **before taking your action**, you may voluntarily change to any legal named guard.

There is no voluntary post-action guard change and no restrictive adjacency requirement. Same-activation entry into an offensive guard remains legal; the fighter retains that posture through the following opponent opportunity. The governing purpose is **Take the benefit, accept the posture.**

A sparse voluntary transition graph is **REJECTED** for the current longsword architecture: Italian evidence supports broad guard-to-guard movement and German evidence does not support a defensible sparse pairwise topology. Source-supported action-produced and recovery transitions remain an approved design avenue; an action or learned Play may establish a resulting guard where its source and mechanic justify it.

Scheitelhau/Crown C1/B3 remains candidate-only, unresolved, and non-governing. Named Guard v0.2 remains blocked.

Historical implementation note: this lag existed at the Choice Architecture milestone and is now **SUPERSEDED**. The shared entry point selects the synchronized authoritative exchange engine while exposing the archived engine only through compatibility exports.

## 2026-08-11 governing provisional prototype selection

Project direction after the listed experiments selects a **GOVERNING PROVISIONAL PROTOTYPE BASELINE** for subsequent simulator work. It is not a canonical rules promotion and does not edit Atra Melee Design Packet v0.4. The machine-readable selection is `data/prototypes/longsword-governing-provisional-v0.1.yaml`; the shared simulator entry point is `simulations/shared/provisional_longsword.py`.

- Durchwechseln: D1 (1 Spiritus at declaration, no refund, state trigger, pre-Basic-Parry-roll window).
- Current audited two-effect compounds: C2 (Absetzen, Scambiar di Punta, and Schielhau cost 2 Spiritus). This does not price future compound Plays.
- Schielhau / Durchwechseln: S2.
- Contact: explicit Crossing/Bind v0.1 axes; displacement remains an event; no random bind, Soft, Close, or zone generation.
- Basic Parry: declared Cross or Beat, with the common pre-roll D1 window. Cross creates the authored Crossing result; Beat displaces and normally separates.
- Crossing: current-exchange duration unless explicitly retained, transformed, or continued.
- Learned-Play chain: maximum 3; basic options and intrinsic branches do not count.
- Loaded: Damage Boon only for proactive Basic Cuts from a Loaded guard.
- Power Attack: P1, 1 Spiritus at declaration, normal attack roll, fixed 7 damage for the prototype longsword, Committed, and Counter-first only against Power. Power is a Basic option, not a learned Play.
- Guard direction: source-specific named guards. The mirrored Threat / Power / Cover family is **SUPERSEDED FOR CURRENT PROTOTYPE WORK**, but its historical record remains below and in the packet.

### 2026-08-11 named-guard architecture selection

The Project explicitly selects **G1 / ACTION-LIGHT** as the governing **PROVISIONAL** named-guard direction. This is not a canonical/final promotion.

A guard should derive value primarily from intrinsic physical/public state, mappings to universal Basic actions, learned Play access, sourced breaker relationships, and source-specific continuations—not compulsory generic bonuses or free compound actions.

A guard-described behavior is Basic only when it is a simple direct posture use with one principal test, contains no distinctive timing or bind-reading lesson, does not combine substantial defence and offence, and does not duplicate a learned Play niche. Ordinary Cut, Thrust, Cross, and Beat descriptions are recorded as **existing Basic-action mappings**, not renamed guard actions. Distinctive timing, tactical triggers, pressure/measure reading, simultaneous defence and offence, displacement plus attack, cover plus close, redirection/deception, specialized continuations, and multiple substantial effects default to **learned Play**. "No mechanic yet" remains valid.

- Absetzen remains a learned Play.
- Upper/lower Winden remain a learned decision system.
- Nachreisen remains a learned Play.
- G2's 0-Spiritus Pflug Absetzen is **REJECTED AS GOVERNING BEHAVIOR** and remains archived experiment material only.
- Source-specific named guards remain preferred; the symmetric Threat / Power / Cover family remains superseded for current prototype work.
- Free before-or-after all-to-all guard change remains a **PROVISIONAL HARNESS RULE** with a **GUARD-CHURN WARNING**. Churn remains OPEN.

The older OPEN/PROVISIONAL transcription below is retained as historical context. Where it conflicts with this dated selection for simulator work, the dated selection governs. Final transition graph, starting-guard rule, final roster, full Winden system, generic leverage, and final guard bonuses remain OPEN.

### 2026-08-11 Guard Evidence & Repertoire acceptance

The Project accepts the principal evidence/content conclusions of Guard Evidence & Repertoire Completion v0.1 for subsequent **PROVISIONAL** prototype work. Historical acceptance does not promote the associated game mechanics.

- G1/action-light remains governing. No distinct Basic guard action survived; simple source-described behavior maps to existing Basic Cut, Thrust, Cross, or Beat rather than receiving a renamed action.
- Absetzen, upper/lower Winden, Nachreisen, joined exchange-thrust techniques, cover plus close/stretto, displacement plus return attack, and timing-rich breaker entries remain learned.
- The item-level audit is preserved for Donna, Frontale, Tutta Porta di Ferro, Mezza Porta di Ferro, and Alber.
- Exact support is preserved for Zwerchhau -> Vom Tag, Krumphau -> Ochs, Schielhau -> Pflug, and Scheitelhau -> Alber. The sourced relationship alone creates no Boon, Bane, automatic success, bonus damage, or defence cancellation.
- Donna has STRONG CONCEPT SUPPORT for a powerful/loaded-blow identity. Loaded/P1 remain PROVISIONAL Atra mechanics and are not inferred for Vom Tag.
- Frontale retains Basic Cross/Beat mappings and a learned longer-sequence candidate. Tutta retains Basic Cross/Beat mappings, bounded learned Scambiar access, and learned cover-to-stretto. Mezza retains threatening point, Basic Thrust/Beat mappings, and a learned beat-return candidate. Alber remains low, not-threatening, without a passive invitation bonus.

### 2026-08-11 Guard Play Bridge v0.1 technical result

Deterministic validation promotes only the boundaries explicitly authorized by the Project:

- Tutta cover-to-stretto is a learned Play.
- There is no universal Close action and no automatic Close after an ordinary successful Cross at Wide.
- No breaker relationship receives an automatic modifier.
- Crown remains distinct from generic Basic Cross.

Scheitelhau's initial Alber entry is classified **S-C / DEFER UNTIL CROWN CONTINUATION**. The initial descending head cut is already represented by Basic Cut, while the distinct source material belongs to the defended Crown/point-sinking/winding/pressing/slicing continuation. No price is assigned to a mechanically inert placeholder, and Alber remains partially mechanically inert.

Tutta cover-to-stretto is technically implementable after a successful Tutta Basic Cross against an ordinary proactive Basic Cut at Wide: spend 1 Spiritus at declaration, retain Crossing, change Wide -> Close, add no second roll or additional action, and count one learned Play. The Project selects **T1 as the GOVERNING PROVISIONAL prototype**; it is not canonical/final. T0 is an archived comparison variant only.

### 2026-08-11 Scheitelhau / Crown v0.1 recommendation

The bounded Crown experiment supplies a mechanically valid exchange-level candidate but does **not** automatically promote it. The recommended Project-review candidate is C1/B3: ordinary Crossing plus a transient, source-specific Crown context; Crown is an authored response context rather than a defender learned Play; the initial Scheitelhau entry remains Basic in chassis; and `Sink Point Under Crown` is the actual learned continuation at 1 Spiritus with a normal attack roll and normal damage. The standalone Scheitelhau entry remains deferred and unpriced. Crown is not generic Basic Cross, and no generic breaker modifier exists.

Deterministic cases pass, including conservative state fields, normal cleanup, German/Italian separation, and the three-Play cap. Automatic promotion is withheld because the repository audit does not encode enough physical Crown geometry to eliminate all historical ambiguity in final player-facing wording. Alber is mechanically ready for Named Guard Rules v0.2 only if the Project accepts C1/B3 as the provisional input; immediate next action is Project review, not the v0.2 run. Guard transitions remain OPEN and unchanged.

## OPEN

### Guard architecture

**SUPERSEDED FOR CURRENT PROTOTYPE WORK by the 2026-08-11 selection.** Historical question: retain the tested mirrored Threat/Power/Cover family structure, or give individual named guards bespoke public effects while preserving height and using tags mainly for indexing, gating and later transitions?

Evidence: [Chat 057-059; Post-v0.1]

### Guard roster

Exact ordinary selectable guards per weapon/tradition, including whether mechanically mirrored pairs such as Ochs/Pflug or Crown/Alber should receive distinct named identities.

Evidence: [Chat 057-059; Post-v0.1]

### Opening procedure

Begin unguarded until first turn, or establish guards sequentially on deployment/entry into striking distance?

Evidence: [Chat 048, 056]

### Alber

Invitation guard effect and whether its baseline benefit belongs on the guard or in learned Invitation Plays.

Evidence: [Chat 039, 044, 059]

### Spiritus value

Power usage is highly sensitive to how strong common 1-Spiritus Plays become; validate after real Plays exist.

Evidence: [Chat 052-056]

### Elite double defeats

d6+1 plus reliable Counters produced very high simultaneous-death rates at expert skill.

Evidence: [Chat 031, 044]

### Unequal-number passing

One pass per side avoids the identified per-character pass snowball, but the full 3v3/unequal-number procedure still needs validation.

Evidence: [Chat 012-013]

### 23 culture slots / restoration

Italian Sword & Buckler, Italian Sword in One Hand and German Spear & Staff were emptied under the strict cutoff. The broader continuity policy reopens 24 former slots; the Fiore against-three candidate now provisionally fills one Italian Sword-in-One-Hand slot, leaving 23 to restore or replace from eligible witnesses.

Evidence: [Chat 069, 076; Post-v0.3]

### Source cleanup

Audit the 114 current candidates plus any restored slots item by item. Record attestation date and inclusion basis; re-evaluate I.33-flavored buckler entries, dagger throwing, polearms and every transparent reconstruction. Anti-number utility tags do not by themselves validate a Play historically or mechanically.

Evidence: [Chat 067, 069; Post-v0.3]

### Base weapon differentiation

Reach, damage profile, defensive suitability and close-range suitability must matter before Plays.

Evidence: [Chat 078]

### Exchange-chain timing

Section 3.6 currently lists Initiation, Remedy, Attacker Continuation and Counter-Remedy while the global limit says no more than three Plays. Resolve the procedural slot structure before mechanical implementation; do not silently encode four Plays or collapse categories.

Evidence: [Packet review, Post-v0.1]

### Shield equipment profiles

Shield is one skill, but bucklers and larger shields should differ through equipment properties and Play requirements. Define the baseline differences (coverage, hand protection, mobility, offensive use, etc.) before final balance implementation.

Evidence: [Post-v0.2]

### Engagement / access rules

Define when more than one enemy can bring an attack to bear, how movement or terrain lets one opponent screen another, and whether reach/guard can deny access. The solver shows this may matter more than adding defensive bonuses.

Evidence: [Post-v0.3 solver]

### Residual defence after action spent

A Dragonbane-style free opposed fallback after the action is spent was tested experimentally and produced only modest help when universal. Decide later whether Atra needs such a residual Evade/cover rule for fiction or pacing; it is not the primary solution to outnumbering.

Evidence: [Post-v0.3 solver]

### Anti-number Play mechanics

Determine whether source-specific single-time Plays literally preserve an action, combine attack and defence in one roll, alter engagement/access, or use another narrower chassis. Avoid granting unconditional extra actions merely for being outnumbered.

Evidence: [Post-v0.3]

## PROVISIONAL

### Round scale

Approximately 6-second rounds on a 2 m/yd square grid.

Evidence: [Chat 001]

### Action economy

One action per character, refreshed at round end; reactions spend that action unless a rule says otherwise.

Evidence: [Chat 001]

### Spiritus

Approximately 8 points, normally refreshed after a short rest; spent for exceptional effort and Plays.

Evidence: [Chat 001]

### Movement

Short move up to MR plus action; hustle +1/2 MR for 1 Spiritus; long move 2x MR or 3x MR when hustling; typical MR 8.

Evidence: [Chat 001]

### Basic reactions

Parry, Ignore and simultaneous Counter remain the basic defensive menu after a successful Strike.

Evidence: [Chat 001, 027]

### Mirrored triangular guard family

**SUPERSEDED FOR CURRENT PROTOTYPE WORK by the 2026-08-11 named-guard direction.** Historical provisional: High/low Threat checks Power/Chamber and opposite-height attacks by Counter Boon; high/low Cover checks Threat and same-height attacks by Parry Boon; high/low Power/Chamber buys a damage Boon on proactive Strikes for 1 Spiritus. The paired heights were mirrors, not bespoke guards.

Evidence: [Chat 044, 054, 056; Post-v0.1]

### Opening guard

Characters begin without guard benefits and establish a guard sequentially on their first turn; this remains under review.

Evidence: [Chat 013, 048, 056]

### Play template

Use the structured learning/use/timing/cost/test/defence/outcome/aftermath/source record in Section 6.

Evidence: [Chat 070-072]

### Career breadth

Design around 10-14 Plays over a full career and approximately 12 as a normal end-state.

Evidence: [Chat 073-076]

### Final catalog

Target about 90 named Plays using 25-35 reusable mechanical chassis.

Evidence: [Chat 076]

### Tempo-compression valuation

Independent once-per-round offensive or defensive tempo is a major benefit. In exact basic-combat tests, offensive tempo was stronger, but a truly independent defensive tempo also changed outnumbered outcomes dramatically. Generic action preservation is therefore too strong to treat as an ordinary 2-Spiritus effect; narrow triggers and source-specific forms require testing.

Evidence: [Post-v0.3 solver]

### Engagement geometry hypothesis

A bottleneck or line that allows only one opponent to engage at a time can reverse an otherwise hopeless 1v2. Future movement/engagement rules should distinguish nominal numbers from how many enemies can actually bring an action to bear.

Evidence: [Post-v0.3 solver]

## DEFERRED

### Crown/Corona

Exact Bind/Crossing procedure and gated winding, pommel, grapple and sword-taking Plays.

Evidence: [Chat 039, 044, 059]

### Recovery transitions

Natural guard-transition graph was proposed, then explicitly set aside pending the Play layer.

Evidence: [Chat 049-052]

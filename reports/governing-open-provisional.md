# Governing OPEN, PROVISIONAL, and DEFERRED register

Transcribed from Section 2 of Atra Melee Design Packet v0.4. These entries are constraints and unresolved questions; this repository does not decide them.

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

The older OPEN/PROVISIONAL transcription below is retained as historical context. Where it conflicts with this dated selection for simulator work, the dated selection governs. Final transition graph, starting-guard rule, final roster, full Winden system, generic leverage, and final guard bonuses remain OPEN.

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

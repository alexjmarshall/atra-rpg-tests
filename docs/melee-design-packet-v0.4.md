<!-- Generated from Atra_Melee_Design_Packet_v0.4.docx; regenerate with scripts/build_research_repository.py. -->

# ATRA RPG

## Atra Melee Design Packet

**Version 0.4**

Canonical snapshot, decision register, rules baseline and Play longlist

| Canonical method: Later decisions supersede earlier experiments only where the record supports a decision. Unresolved questions remain OPEN. Recommendations that were tested but not adopted remain PROVISIONAL. |
| --- |

Updated 2026-08-07  |  Primary campaign: 1490s  |  Supported martial horizon: c. 1475-1540

# 1. Scope and canonical method

This packet updates v0.3 after further Project stress testing. It remains a design constitution, not a finished rules chapter. It separates explicit decisions from tested working assumptions, discarded experiments and unresolved design questions. v0.4 adds reproducible outnumbering/action-economy results, an anti-number design direction for advanced Plays, and two source-grounded research candidates for fighting several opponents.

Primary design record: Shared ChatGPT conversation beginning 2026-08-05, Atra Melee Design Packets v0.1-v0.3, and subsequent Project follow-up through this v0.4 update. Internal references such as [Chat 055] identify exported message numbers from the original chronological record; [Post-v0.x] marks later Project clarification or stress testing.

Conversation link: HEMA exchanges per 6 seconds

Comparison source: Codex Martialis Core Rulebook 2024 Edition, version 8.2, Jean Chandler, 117 pages. References use [CM p.#].

Scope limitation: v0.4 is canonical for the supplied design record, attached Codex Martialis comparison source and subsequent Project clarifications used in this update. Unseen Project chats, source files or later decisions could supersede it.

| Source limitation: If another Atra melee discussion or source contains later explicit decisions, attach or import it before treating v0.4 as the final Project-wide record. |
| --- |

## Status vocabulary

| Status | Meaning |
| --- | --- |
| ADOPTED | Explicitly selected by the user, or clearly carried forward as the current rule after later work. |
| PROVISIONAL | The last tested working baseline or a recommendation not explicitly ratified. |
| REJECTED | Explicitly disallowed or invalidated by correction. |
| SUPERSEDED | A former rule replaced by a later decision. |
| OPEN | A material choice remains unresolved; v0.4 does not decide it. |
| DEFERRED | Intentionally postponed until another subsystem exists. |

# 2. Decision registers

## 2.1 Adopted

| Status | Decision | Canonical reading | Evidence |
| --- | --- | --- | --- |
| ADOPTED | Design goals | Evocative HEMA/historical fiction; easy to learn and use; tactically interesting and educational customization; default to Dragonbane idioms when uncertain. | [Chat 001] |
| ADOPTED | Initiative | Reroll which side acts first at the beginning of every round; then alternate side activations. | [Chat 006-009] |
| ADOPTED | Passing | Each side may pass once per round. This replaces both unlimited passing and one pass per character. | [Chat 013] |
| ADOPTED | Guard timing | Fully sequential. A character may change guard once on their own turn, before or after their action, never both. | [Chat 045, 055] |
| ADOPTED | Information | HP and guards are public; skill values and learned Play repertoire are hidden. | [Chat 055] |
| ADOPTED | Power boundary | A Power/Chamber benefit never applies to Counters and provides no defence. | [Chat 020-023] |
| ADOPTED | Damage baseline | The current test baseline is d6+1 rather than d6; later guard work and balance targets use it. | [Chat 028-036, 084] |
| ADOPTED | Primary campaign era | The first major campaign is set in the 1490s; the rules should also support play into the early sixteenth century without swapping Play lists by date. | [Post-v0.1] |
| ADOPTED | Weapon skills | Eight character-sheet melee skills: Wrestling, Dagger, One-Handed Sword, Axe & Mace, Longsword, Shield, Spear & Staff, Poleaxe & Halberd. Sword & Buckler remains a Play curriculum/loadout heading, not a skill. | [Post-v0.2] |
| ADOPTED | Rapier | Remove Rapier as a separate skill for this period; mature rapier belongs to later source families. | [Chat 067] |
| ADOPTED | Current Play count | 114 current research candidates are now in the longlist: the 112 retained post-audit candidates plus two explicit against-many additions. One of the 24 previously empty culture slots is now provisionally repopulated, leaving 23 restoration slots. The catalog remains an R&D inventory, not 114 historically verified or final Plays. | [Chat 069, 076; Post-v0.3] |
| ADOPTED | Guard height model | Height matters to guard interactions. High and low versions within the current family model are mechanical mirror images; the open question is whether named guards should gain additional bespoke identities. | [Post-v0.1] |
| ADOPTED | Supported martial horizon | Use a broad late-medieval/early-Renaissance martial horizon of about 1475-1540 for the common Play corpus, while keeping the 1490s as the primary campaign era. | [Post-v0.1] |
| ADOPTED | Source continuity principle | A treatise records practice; its publication date is not an invention date. Early-sixteenth-century sources may support the common corpus when they belong to a tradition demonstrably rooted in the fifteenth century. Distinctive mid-sixteenth-century innovations remain outside the core unless independently earlier-attested. | [Post-v0.1] |
| ADOPTED | Skill/curriculum separation | Character-sheet skills represent relatively transferable motor competence and are the numbers characters roll and advance. Play curricula may use different historical/loadout headings and each Play separately specifies the skill tested. | [Post-v0.2] |
| ADOPTED | Implement-based rolls | Use the skill of the implement doing the mechanically decisive work: shield Parry -> Shield; off-hand dagger attack or dagger Parry -> Dagger; sword attack/Parry -> One-Handed Sword. A mixed-implement Play may require minimum ratings in additional skills. | [Post-v0.2] |
| ADOPTED | Off-hand as Play gate | Off-hand state is a first-class Use requirement. Plays may require Any, Free, Buckler, Shield, Companion weapon or Two hands free. Carrying companion equipment may open one curriculum branch while closing free-hand techniques. | [Post-v0.2] |
| ADOPTED | Outnumbering design principle | When several opponents can actually bring their actions to bear, numerical superiority should be severe. A master should overcome numbers primarily by controlling engagement geometry, compressing offence and defence into a tempo, maintaining recovery, or rapidly removing one attacker—not by receiving a generic bonus merely for being outnumbered. | [Post-v0.3 exact solver stress tests] |
| ADOPTED | Anti-number Play direction | The research catalog should include historically grounded or transparently reconstructed Plays that help an expert fight several opponents through engagement control, clearing/recovery, or single-time defence-and-offence. Such Plays remain individually provisional until sourced and mechanically tested. | [Post-v0.3] |

## 2.2 Provisional working baseline

| Status | Decision | Canonical reading | Evidence |
| --- | --- | --- | --- |
| PROVISIONAL | Round scale | Approximately 6-second rounds on a 2 m/yd square grid. | [Chat 001] |
| PROVISIONAL | Action economy | One action per character, refreshed at round end; reactions spend that action unless a rule says otherwise. | [Chat 001] |
| PROVISIONAL | Spiritus | Approximately 8 points, normally refreshed after a short rest; spent for exceptional effort and Plays. | [Chat 001] |
| PROVISIONAL | Movement | Short move up to MR plus action; hustle +1/2 MR for 1 Spiritus; long move 2x MR or 3x MR when hustling; typical MR 8. | [Chat 001] |
| PROVISIONAL | Basic reactions | Parry, Ignore and simultaneous Counter remain the basic defensive menu after a successful Strike. | [Chat 001, 027] |
| PROVISIONAL | Mirrored triangular guard family | High/low Threat checks Power/Chamber and opposite-height attacks by Counter Boon; high/low Cover checks Threat and same-height attacks by Parry Boon; high/low Power/Chamber buys a damage Boon on proactive Strikes for 1 Spiritus. The paired heights are currently mirrors, not bespoke guards. | [Chat 044, 054, 056; Post-v0.1] |
| PROVISIONAL | Opening guard | Characters begin without guard benefits and establish a guard sequentially on their first turn; this remains under review. | [Chat 013, 048, 056] |
| PROVISIONAL | Play template | Use the structured learning/use/timing/cost/test/defence/outcome/aftermath/source record in Section 6. | [Chat 070-072] |
| PROVISIONAL | Career breadth | Design around 10-14 Plays over a full career and approximately 12 as a normal end-state. | [Chat 073-076] |
| PROVISIONAL | Final catalog | Target about 90 named Plays using 25-35 reusable mechanical chassis. | [Chat 076] |
| PROVISIONAL | Tempo-compression valuation | Independent once-per-round offensive or defensive tempo is a major benefit. In exact basic-combat tests, offensive tempo was stronger, but a truly independent defensive tempo also changed outnumbered outcomes dramatically. Generic action preservation is therefore too strong to treat as an ordinary 2-Spiritus effect; narrow triggers and source-specific forms require testing. | [Post-v0.3 solver] |
| PROVISIONAL | Engagement geometry hypothesis | A bottleneck or line that allows only one opponent to engage at a time can reverse an otherwise hopeless 1v2. Future movement/engagement rules should distinguish nominal numbers from how many enemies can actually bring an action to bear. | [Post-v0.3 solver] |

## 2.3 Rejected or superseded

| Status | Decision | Canonical reading | Evidence |
| --- | --- | --- | --- |
| SUPERSEDED | Fixed first side | The side that won the first round's initiative no longer remains first for the entire combat. | [Chat 006] |
| REJECTED | Unlimited passes | Creates rational infinite stalling. | [Chat 004, 009] |
| SUPERSEDED | One pass per character | Rejected in favor of one pass per side to avoid numerical snowball and tracking load. | [Chat 010-013] |
| SUPERSEDED | Base d6 damage | Replaced by d6+1 for the current test baseline. | [Chat 028] |
| REJECTED | Power on Counter | A modeling error that invalidated earlier equilibrium counts and thresholds. | [Chat 020-023] |
| REJECTED | Passive Barrier DR | Produced the wrong fiction and encouraged Ignore; both 1 DR and 2 DR variants are non-current. | [Chat 032-039] |
| REJECTED | Failed-Parry DR Cover | Historically evocative but triggered too rarely; replaced in the tested triangle by conditional Parry Boon. | [Chat 039-044] |
| SUPERSEDED | Paid pre-action guard change | The 1-Spiritus guard-change fee was removed; the one-change timing limit was the meaningful constraint. | [Chat 045-048] |
| REJECTED | Simultaneous guard selection | Incompatible with the explicit sequential-only requirement. | [Chat 048, 055] |
| REJECTED | Mature rapier curriculum | Do not restore mature rapier as a separate core skill or import later rapier-and-dagger/cloak systems. Agrippa (1553) is treated as a useful cleavage marker for a distinct mid-sixteenth-century development rather than core Atra technique. | [Chat 067; Post-v0.1] |
| REJECTED | Meyer-only unique material | Meyer (1561/1570) is too late for source-unique core Plays and explicitly modernizes older material for a later martial climate. He may be used comparatively or where the same technique is independently grounded earlier. | [Chat 067; Post-v0.1] |
| SUPERSEDED | Blanket rejection of early Bolognese printed sources | The earlier rule excluding Manciolino and Marozzo solely because their surviving books are later than 1500 is superseded. They may serve as continuity witnesses to an established fifteenth-century Bolognese tradition; individual 1530s sequences are not automatically projected unchanged into 1490. | [Chat 067; Post-v0.1] |
| SUPERSEDED | Strict 1475-1500 publication cutoff | Replaced by a continuity-based source policy and a supported martial horizon of about 1475-1540. | [Post-v0.1] |

## 2.4 Open and deferred

| Status | Decision | Canonical reading | Evidence |
| --- | --- | --- | --- |
| OPEN | Guard architecture | Retain the tested mirrored Threat/Power/Cover family structure, or give individual named guards bespoke public effects while preserving height and using tags mainly for indexing, gating and later transitions? | [Chat 057-059; Post-v0.1] |
| OPEN | Guard roster | Exact ordinary selectable guards per weapon/tradition, including whether mechanically mirrored pairs such as Ochs/Pflug or Crown/Alber should receive distinct named identities. | [Chat 057-059; Post-v0.1] |
| OPEN | Opening procedure | Begin unguarded until first turn, or establish guards sequentially on deployment/entry into striking distance? | [Chat 048, 056] |
| OPEN | Alber | Invitation guard effect and whether its baseline benefit belongs on the guard or in learned Invitation Plays. | [Chat 039, 044, 059] |
| DEFERRED | Crown/Corona | Exact Bind/Crossing procedure and gated winding, pommel, grapple and sword-taking Plays. | [Chat 039, 044, 059] |
| DEFERRED | Recovery transitions | Natural guard-transition graph was proposed, then explicitly set aside pending the Play layer. | [Chat 049-052] |
| OPEN | Spiritus value | Power usage is highly sensitive to how strong common 1-Spiritus Plays become; validate after real Plays exist. | [Chat 052-056] |
| OPEN | Elite double defeats | d6+1 plus reliable Counters produced very high simultaneous-death rates at expert skill. | [Chat 031, 044] |
| OPEN | Unequal-number passing | One pass per side avoids the identified per-character pass snowball, but the full 3v3/unequal-number procedure still needs validation. | [Chat 012-013] |
| OPEN | 23 culture slots / restoration | Italian Sword & Buckler, Italian Sword in One Hand and German Spear & Staff were emptied under the strict cutoff. The broader continuity policy reopens 24 former slots; the Fiore against-three candidate now provisionally fills one Italian Sword-in-One-Hand slot, leaving 23 to restore or replace from eligible witnesses. | [Chat 069, 076; Post-v0.3] |
| OPEN | Source cleanup | Audit the 114 current candidates plus any restored slots item by item. Record attestation date and inclusion basis; re-evaluate I.33-flavored buckler entries, dagger throwing, polearms and every transparent reconstruction. Anti-number utility tags do not by themselves validate a Play historically or mechanically. | [Chat 067, 069; Post-v0.3] |
| OPEN | Base weapon differentiation | Reach, damage profile, defensive suitability and close-range suitability must matter before Plays. | [Chat 078] |
| OPEN | Exchange-chain timing | Section 3.6 currently lists Initiation, Remedy, Attacker Continuation and Counter-Remedy while the global limit says no more than three Plays. Resolve the procedural slot structure before mechanical implementation; do not silently encode four Plays or collapse categories. | [Packet review, Post-v0.1] |
| OPEN | Shield equipment profiles | Shield is one skill, but bucklers and larger shields should differ through equipment properties and Play requirements. Define the baseline differences (coverage, hand protection, mobility, offensive use, etc.) before final balance implementation. | [Post-v0.2] |
| OPEN | Engagement / access rules | Define when more than one enemy can bring an attack to bear, how movement or terrain lets one opponent screen another, and whether reach/guard can deny access. The solver shows this may matter more than adding defensive bonuses. | [Post-v0.3 solver] |
| OPEN | Residual defence after action spent | A Dragonbane-style free opposed fallback after the action is spent was tested experimentally and produced only modest help when universal. Decide later whether Atra needs such a residual Evade/cover rule for fiction or pacing; it is not the primary solution to outnumbering. | [Post-v0.3 solver] |
| OPEN | Anti-number Play mechanics | Determine whether source-specific single-time Plays literally preserve an action, combine attack and defence in one roll, alter engagement/access, or use another narrower chassis. Avoid granting unconditional extra actions merely for being outnumbered. | [Post-v0.3] |

# 3. Current combat rules

| Reading rule: Items marked Working baseline are current for testing but remain PROVISIONAL unless separately listed as ADOPTED. |
| --- |

## 3.1 Round, map and resources

| Element | Working baseline |
| --- | --- |
| Round | About 6 seconds. |
| Grid | 2 m/yd squares. |
| Action | One per character; refreshes at the end of the round. |
| Spiritus | About 8; encounter-scale effort reserve; refresh after a short rest. |
| HP | 8 typical HP; removed immediately at 0 or below. |
| Movement rate | Typical MR 8. |

## 3.2 Initiative and passes

- At the beginning of each round, randomly determine which side takes the first activation.
- Sides alternate activating one character who still has an action.
- Each side may pass once per round. A pass delays activation; it does not create an unlimited loop.
- When no legal pass remains, a side with a ready character must activate one.
- The record does not yet define every edge case for large melees, incapacitation during a pass sequence or a side with no ready characters.
## 3.3 Movement

- Short move: move up to MR on your turn and still act.
- Hustle: spend 1 Spiritus to add 1/2 MR.
- Long move: forgo the action to move 2x MR, or 3x MR when hustling.
- Movement interactions with reach, engagement, facing and opportunity attacks are not yet canonical.
## 3.4 Tests, Boons and Banes

- Skill tests: roll d20 equal to or under the relevant skill value.
- Boon on a d20 test: roll 2d20 and keep the lower.
- Bane on a d20 test: roll 2d20 and keep the higher.
- Boon on damage: roll two damage dice and keep the higher.
- Bane on damage: roll two damage dice and keep the lower.
- One Boon and one Bane cancel. Further stacking rules are not specified in the record.
## 3.5 Basic attack and defence

| Option | Timing | Effect |
| --- | --- | --- |
| Strike | On turn | Spend the action; roll the skill of the attacking implement. On success, the defender may react; damage baseline is d6+1. |
| Parry | After a successful Strike | Spend the defender's action; roll the skill of the implement used to Parry (for example Shield, Dagger, One-Handed Sword or Longsword). Success cancels incoming damage. |
| Ignore | After a successful Strike | Take the hit and retain the action. |
| Counter | After a successful Strike | Spend the action and attack into the attacker, rolling the skill of the weapon used for the Counter. Incoming damage is not cancelled; successful Counter damage resolves simultaneously. |

| Contradiction flag: The chat initially called damage 'd6 by default,' while later testing consistently used d6+1. v0.4 carries d6+1 as the adopted working baseline because all later guard tests and the Codex handoff use it. |
| --- |

## 3.6 Core exchange sequence with Plays

1. Turn preparation: the acting character may use their one guard change before acting.
2. Action declaration: declare Basic Strike or an Action Play, target, movement, before-roll effects and costs.
3. Attack roll: resolve the initial test. On failure, process miss triggers and Aftermath.
4. Reaction declaration: after success is known, the defender chooses Ignore, Parry, Counter or an eligible Remedy.
5. Attacker continuation: after seeing the declared response, the attacker may use one eligible Continuation.
6. Counter-Remedy: the defender may answer that Continuation with one eligible Counter-Remedy.
7. Resolution: resolve final attack, defence, damage, movement and control.
8. Aftermath: establish guards, Bind/Crown, exposure and post-exchange effects.
OPEN timing flag: The provisional sequence above can expose four named Play steps (Initiation, Remedy, Continuation, Counter-Remedy), while the global limit in Section 6.7 permits only three Plays. v0.4 does not resolve this contradiction; Codex should model it as an open design issue, not infer a fourth slot.

# 4. Guard rules and design state

## 4.1 Adopted guard procedure

- Guard choice is sequential and public; there is no simultaneous or secret guard declaration.
- Once on your own turn, change guard either before or after the action. You cannot do both.
- The chosen guard persists until changed.
- HP and guards are public. Skill and learned Play repertoire are hidden.
- Power/Chamber never benefits Counter damage and provides no defensive bonus.
- Height remains mechanically meaningful. Within the current family model, each high/low pair is a mirror image: height changes which opposing attacks trigger the family benefit, but does not yet give the named guards unique non-height effects.
## 4.2 Last tested mirrored family baseline

| Family | Identity | Provisional effect | Readable question |
| --- | --- | --- | --- |
| Power / Chamber | Proactive offence | When declaring a proactive Strike from this guard, spend 1 Spiritus and give damage a Boon. No Counter or defensive benefit. | Exploit an exhausted target or a kill threshold; accepting defensive exposure is visible. |
| Threat | Interception | Counter receives a Boon against a Power Strike or a Strike from the opposite height. | Deter visible commitment while the action remains ready. |
| Cover | Active defence | Parry receives a Boon against a Threat Strike or a Strike from the same height. | Close a predictable line and favor survival over retaliation. |

Balance result: With modest opportunity value assigned to Spiritus, equal-skill .60 fighters used Power for about 29% of all Strikes; among guarded Strikes the split was about Power 38%, Cover 36%, Threat 26%. Post-action receiving guards were about Threat 46%, Cover 44%, Power 10%. [Chat 054-056]

Meaning: The desired 'mixing' is state-dependent change across a combat, not randomized choice at every node or equal one-third usage.

## 4.3 Later bespoke-guard proposal

| Guard | Proposed identity | Untested proposal |
| --- | --- | --- |
| Vom Tag / Posta di Donna | Committed Power | Spend 1 Spiritus for damage Boon on proactive Strike; no defence. |
| Ochs / Finestra | Interception | Counter Boon against a Strike whose attacker changed guard before acting, or against Power. |
| Pflug / Breve | Controlled Point | Counters against its ordinary proactive Strike suffer a Bane; softer variant removes a Counter Boon. |
| Porta di Ferro / Iron Gate | Strong Cover | Parry Boon; cannot Counter, or Counter suffers a Bane in the softer variant. |
| Alber | Invitation | Strikes against you gain a Boon; if one fails to damage you, your next Strike against that attacker gains a Boon. |
| Crown / Corona | Bind state | Not normally selectable; entered through a successful Parry, crossing or Play. |

| OPEN - do not canonize silently: The bespoke proposal is later than the family triangle, but it was not tested or explicitly adopted. v0.4 preserves it as the leading alternative, not as the current rule. |
| --- |

## 4.4 Guard balance targets

- Every selectable guard should have one legible public promise and one vulnerability.
- Guard effects must be worthwhile before advanced Plays, while guards also gate hidden repertoire.
- Power should be attractive against action-spent or vulnerable enemies, not the universal default.
- Threat should be common when retaining an action and deterring commitment.
- Cover should be common when a line is predictable and survival matters.
- Ordinary fights should show several guard changes, but not equal usage in every context.
- A healthy target for the tested family model is Power in 25-40% of guarded Strikes and about 0.5-1.0 Spiritus spent on Power per fighter per duel.
# 5. Historical scope and source-continuity policy

Primary campaign play is the 1490s, but Atra is intended to support the late-fifteenth and early-sixteenth-century martial world with one common Play corpus. The working martial horizon is approximately 1475-1540. Publication or manuscript date is evidence of attestation, not necessarily invention: an early-sixteenth-century source may be used where it documents a school or lineage demonstrably rooted in the fifteenth century. Conversely, a later source does not automatically justify projecting source-unique innovations backward. Distinctive mid-sixteenth-century developments are treated as the presumptive cleavage point.

| Class | Policy |
| --- | --- |
| Core direct horizon | Preferred direct or near-direct witnesses for the common corpus, roughly 1475-1515: Vadi (c.1482-87), Lecküchner (1478/1482), Falkner (c.1495), Monte (written in the late 1400s; Latin print 1509), late Liechtenauer witnesses and comparable material. |
| Continuity sources | Sources roughly 1515-1540 may enter the core when they belong to a demonstrably older tradition. Important examples include Paurenfeyndt (1516), Anonimo Bolognese, Manciolino (1531; evidence of earlier publication activity) and Marozzo (1536) for the Dardi/Bolognese lineage, and Auerswald (1539) for wrestling. |
| Earlier continuing tradition | Fiore (c.1400-09), Pseudo-Danzig, Lew, Kal, Talhoffer, Ott Jud/Lignitzer and other earlier fifteenth-century material may support the corpus where the tradition plausibly continues into the target horizon. |
| Archaic / optional | MS I.33 (c.1320s) may support old-school or archaizing material, but its exact ward system should not be treated as the normal late-fifteenth-century default without later corroboration. |
| Later preservation witness | Later compilations may preserve older material. Paulus Hector Mair, who collected older fencing manuscripts beginning in the 1540s, may be used to transmit or clarify earlier traditions; source-unique material still needs separate justification. |
| Reconstruction allowed | Where the game needs a function and eligible period principles support it, mark the Play transparently as reconstruction. A game-facing name must not be presented as a copied historical technique. |
| Presumptive cleavage / outside core | Distinctive mid-sixteenth-century innovations are normally outside the common corpus unless independently earlier-attested. Agrippa (1553) is a useful Italian marker for a new geometrized system; Meyer (1561/1570) explicitly updates and reinvents older teachings for a later martial climate. dall'Agocchie, Giganti, Capo Ferro and mature rapier systems remain later. |

## 5.1 Source inclusion basis and historical confidence

| Inclusion basis | Meaning |
| --- | --- |
| DIRECT | Direct or near-direct attestation inside the supported martial horizon; usually the strongest basis for a Play. |
| CONTINUITY | Early-sixteenth-century attestation in a school, lineage or practitioner demonstrably rooted in the fifteenth century. |
| EARLIER | Earlier-fifteenth-century attestation plausibly continuing into the supported horizon. |
| PRESERVATION | Later witness preserving or copying older material; supports the older lineage, not automatically source-unique innovations. |
| RECONSTRUCTION | Game implementation synthesized from eligible period principles rather than a directly documented named technique. |
| IMPORTED | Distinctively later material intentionally borrowed for gameplay; rare and conspicuously identified. |

Historical confidence is recorded separately from inclusion basis: A = direct/strong continuity; B = plausible continuity; C = reconstruction; D = imported. Do not infer confidence from publication year alone.

## 5.2 Character-sheet melee skill roster

| Skill | Canonical scope |
| --- | --- |
| Wrestling | Unarmed grips, throws, locks, pins and close control; also the natural test for genuinely unarmed parts of armed close play. |
| Dagger | Dagger attacks, dagger Parries and dagger-on-dagger work, regardless of which hand holds the dagger. |
| One-Handed Sword | Arming sword, Messer, falchion and early cut-thrust sword handling. The skill is independent of whether the off hand is free, holding a buckler, shield, dagger or other companion equipment. |
| Axe & Mace | One-handed axes, maces, hammers and clubs. Weapon traits such as Hooking, Crushing and Piercing gate specialized Plays; shield-dependent Plays may additionally require Shield. |
| Longsword | Two-handed sword fencing; richest source base and expected mechanical centerpiece. |
| Shield | Buckler and larger-shield Parries, active covers, shield strikes, binds, rushes and weapon manipulation. Equipment and Plays distinguish bucklers from larger shields. |
| Spear & Staff | Spears, staves and similar simple long hafted weapons whose handling centers on shaft, line, reach, point/end control, beating, sliding and shortening. |
| Poleaxe & Halberd | Complex-headed long weapons whose handling centers on differentiated striking surfaces, hooks, wrenching, rear spikes and close weapon control; includes poleaxe, halberd, bill and similar weapons by handling profile. |

## 5.3 Skills, curricula, equipment and rolls

The character-sheet skill taxonomy and the Play curriculum taxonomy are intentionally independent. A skill is a relatively transferable physical competence that receives a rating, advances and is rolled. A curriculum is the historical or loadout-based heading under which related Plays are taught and presented. A curriculum may draw on more than one skill.

| Layer | Function |
| --- | --- |
| Skill | Character-sheet number rolled and advanced: e.g. One-Handed Sword, Shield, Dagger. |
| Curriculum | Historical/loadout organization for Plays: e.g. German Sword & Buckler, Italian Sword & Dagger, German Axe/Mace & Shield. |
| Equipment | Physical affordances and restrictions: Buckler, Large Shield, Hooking weapon, Free hand, dagger, etc. |
| Play | Learned technique that states its curriculum, Test Skill, secondary skill requirements, equipment/off-hand gates and timing. |

Basic rule: roll the skill of the implement actually performing the decisive action. A shield Parry uses Shield; a dagger attack or dagger Parry uses Dagger even when the dagger is in the off hand; a sword attack or sword Parry uses One-Handed Sword.

| Off-hand requirement | Meaning |
| --- | --- |
| Any | The Play works regardless of what the other hand is doing. |
| Free | The other hand must be empty and available for seizing, grappling or other control. |
| Buckler | Requires a small buckler specifically; a larger shield does not automatically qualify. |
| Shield | Requires an appropriate shield; the Play may further specify buckler or large-shield traits. |
| Companion weapon | Requires a dagger or other named off-hand weapon. |
| Two hands free | Requires both hands to be available, normally for Wrestling or certain dagger controls. |

Mixed-implement Plays normally resolve with one roll. The Play names a primary Test Skill and may require minimum ratings in one or more secondary skills. Rare fully coordinated techniques may instead test the lower of two required skills; use that chassis sparingly so most Plays retain the Dragonbane-style one-roll procedure.

# 6. Play template and mechanical taxonomy

## 6.1 Core questions

- What historical idea does the Play teach?
- What public situation makes it available?
- At what exact moment is it declared?
- What does it cost and replace?
- What response does it invite from the opponent?
## 6.2 Player-facing record

| Field | Required content |
| --- | --- |
| Identity | Name; Tradition; Curriculum; Tier; Type; tactical/equipment Tags. |
| Learn | Minimum rating in the Test Skill, any secondary-skill thresholds, prerequisite Plays and training access. |
| Use | Weapon, off-hand requirement, guard, range/measure, trigger, target, contact, equipment traits and action state. |
| Timing | Exact declaration window using standardized timing phrases. |
| Cost | Action relationship, Spiritus, movement, guard commitment or other expenditure. |
| Test | Primary Test Skill, any rare coordinated-skill rule, and Boons/Banes. |
| Defence | Permitted responses and any modification to them. |
| Success | Damage, movement, control and state changes. |
| Failure | Consequences when the test fails. |
| Aftermath | Resulting guard, position, Bind, exposure or continuing effect. |
| Limit | Global or card-specific repetition limit. |
| Source | Manual, attestation/publication date, section/folio/plate, edition/translator, source inclusion basis (DIRECT/CONTINUITY/EARLIER/PRESERVATION/RECONSTRUCTION/IMPORTED) and confidence grade. |

## 6.3 Designer-only fields

| Field | Purpose |
| --- | --- |
| Historical lesson | The authentic concept the mechanic is meant to teach. |
| Public telegraph | What the opponent sees before repertoire is revealed. |
| Counterplay | Rational opponent responses. |
| Power budget | Why cost and prerequisites justify the effect. |
| AI / solver heuristic | When an NPC or policy should consider the Play. |
| Source audit | Attestation date, inclusion basis, A/B/C/D confidence and any continuity/reconstruction notes. |
| Upgrade branch | Later Plays or improvements it unlocks. |
| Outnumbering role | Solver/design tag for Tempo Compression, Engagement Control, Clearing, Recovery or Line Denial. “Against Many” is an indexing role, never an automatic bonus. |

Anti-number tag note: use Tempo Compression when one technique combines work that would ordinarily consume separate offensive/defensive tempo; Engagement Control when positioning or line control limits how many opponents can act; Clearing/Recovery/Line Denial for actions that preserve space or avoid becoming committed to one foe. These labels guide research and solver testing only.

## 6.4 Multi-implement Play resolution

Every Play specifies the skill actually rolled. Additional skills function as learning prerequisites or Use gates unless the Play explicitly uses the rare coordinated-test chassis. This keeps sword-and-buckler, sword-and-dagger and axe-and-shield curricula from proliferating separate character-sheet skills.

| Chassis | Resolution |
| --- | --- |
| Primary-tool | Roll the skill of the implement delivering the decisive action; the companion implement is a requirement or modifies the effect. This should be the default for mixed-weapon Plays. |
| Assisted-tool | Roll the skill of the assisting implement when that implement performs the decisive defence/control, e.g. a buckler Parry that opens a sword continuation. |
| Coordinated | Rare: when both skills are inseparable to success, roll against the lower of the two required skills. Avoid a second roll. |

Examples: a sword thrust after a buckler setup may require One-Handed Sword 11+ and Shield 11+ but roll One-Handed Sword; a shield bind may roll Shield; an off-hand dagger attack always rolls Dagger.

## 6.5 Learning tiers

| Tier | Minimum skill | Approx. P | Curricular rule |
| --- | --- | --- | --- |
| Foundation | 8 | .40 | Normally no Play prerequisite. |
| Trained | 11 | .55 | Usually one Foundation prerequisite. |
| Expert | 14 | .70 | One coherent branch. |
| Master | 17 | .85 | May require two earlier Plays; avoid longer chains. |

Prerequisite ceiling: No Play should require more than two named prerequisite Plays.

## 6.6 Primary timing categories

| Category | Definition |
| --- | --- |
| Guard | A public posture or earned state; normally uses the once-per-turn guard change. |
| Action | Replaces the ordinary action: specialized Strike, beat, throw, seizure or deliberate bind entry. |
| Reaction / Remedy | Declared in response to another action; normally replaces the action spent on Parry or Counter. |
| Continuation | Extends an action/reaction after it creates a condition; normally costs Spiritus but no additional action. |
| Aftermath | Declared after principal resolution; establishes pursuit, guard, Bind or recovery. |

## 6.7 Standard action and Spiritus relationships

| Relationship / cost | Budget |
| --- | --- |
| Replaces your action | The Play is the character's activation action. |
| Replaces your reaction | Consumes the action that would be spent defending. |
| No additional action | Modifies or continues an action already resolving. |
| 0 Spiritus | Narrow sidegrade, specialized guard or real vulnerability. |
| 1 Spiritus | One meaningful Boon, modest movement, target change or narrow conversion. |
| 2 Spiritus | Two linked benefits, significant Bind, or narrowly triggered tempo compression/action preservation. Generic independent extra offence/defence is stronger than this benchmark and is not automatically priced at 2. |
| 3 Spiritus | Decisive Master continuation, severe action denial, additional attack, controlling finish, or broad action preservation. Even at 3 Spiritus, unconditional extra tempo may require narrower triggers or other limits. |

Tempo warning: exact outnumbering tests show that an independent extra offensive or defensive tempo can change win rates by tens of percentage points. Treat “attack without spending your action” and “defend without spending your action” as major chassis, not routine numerical bonuses.

## 6.8 Timing language and global limits

- Use exact phrases such as 'before making your roll,' 'after the defender declares Parry,' or 'after the exchange resolves.'
- Spend Spiritus when the Play is declared whether it succeeds or fails, unless the card explicitly says otherwise.
- Prefer one roll using the weapon skill performing the Play.
- One initiating Play per action, one Remedy per defender per exchange and one Counter-Remedy per initiating character.
- One instance of the same Play per exchange.
- A character cannot react after their action is spent unless an explicit Play permits it.
- Powerful Plays should leave a readable Aftermath rather than only add numbers.
# 7. Current Play longlist - 114 research candidates

Organization note: Section 7 is grouped by Play curriculum or historical/loadout heading, not by the skill rolled. In particular, Sword & Buckler remains a curriculum even though its Plays will test One-Handed Sword and/or Shield; mixed-equipment curricula may require ratings in multiple skills.

This appendix now contains 114 research candidates: the 112 retained after the earlier strict-cutoff audit plus two explicit against-many additions. It is not an implementation list, final curriculum or claim that every item is historically cleared. The broader continuity policy reopens 24 previously removed culture slots; one Italian Sword-in-One-Hand slot is now provisionally repopulated, leaving 23. An asterisk marks a game-facing name for a historical but unnamed/inconsistently named action or a transparent reconstruction. A dagger (†) marks a candidate with likely anti-number utility through tempo compression, engagement control, recovery or line denial; it is a design-role tag, not a mechanical bonus. Tier and Type assignments remain provisional research metadata pending source audit and mechanical prototyping.

| Curriculum / Play heading | German | Italian | Total |
| --- | --- | --- | --- |
| Wrestling | 8 | 8 | 16 |
| Dagger | 8 | 8 | 16 |
| Sword & Buckler | 8 | 0 | 8 |
| Sword in One Hand | 8 | 1 | 9 |
| Axe & Mace | 8 | 8 | 16 |
| Longsword | 12 | 13 | 25 |
| Spear & Staff | 0 | 8 | 8 |
| Polearms / Poleaxe & Halberd | 8 | 8 | 16 |
| TOTAL | 60 | 54 | 114 |

| Restoration curriculum slots: Italian Sword & Buckler, Italian Sword in One Hand and German Spear & Staff each originally had eight removed slots. The broader continuity policy reopens all 24; “Sword Against Three*” below now provisionally fills one Italian Sword-in-One-Hand slot, leaving 23 unfilled. These are research slots, not quotas that must survive pruning. |
| --- |

## Wrestling

### German

> Period-compatible. Ott Jud, Lignitzer, Kal and related fifteenth-century material. Individual game-facing names still require folio-level citations.

| Tier | Play | Type | Tactical lesson |
| --- | --- | --- | --- |
| Foundation | Inside-Outside Clinch* | Entry | Gain one inside arm and one outside arm before attempting a throw. |
| Foundation | Elbow Turn* | Control | Lift or turn the elbow to break posture and redirect the opponent. |
| Foundation | Cast Over the Leg* | Throw | Step behind a leg and throw backward over the thigh. |
| Intermediate | Hip Throw* | Throw | Turn beneath a loose upper-body grip and cast over the hip. |
| Intermediate | Elbow Lever* | Lock | Use two hands or the body against an extended elbow. |
| Intermediate | Rear-Clasp Throw* | Counter | Duck and cast an opponent who has seized you from behind. |
| Master | Double Arm Lever* | Break | Trap both elbows from outside and force both arms upward. |
| Master | Counter-Wrestling* | Counter | Reverse an attempted lock or throw by changing grip and stepping behind. |

### Italian

> Period-compatible. Fiore's Abrazare is early fifteenth century and remains a contemporary-tradition source for the 1490s.

| Tier | Play | Type | Tactical lesson |
| --- | --- | --- | --- |
| Foundation | Gain the Holds* | Entry | Establish the arm-and-shoulder control from which the *Abrazare* plays branch. |
| Foundation | Elbow-and-Shoulder Turn* | Throw/lock | Turn the body while controlling both elbows; throw or dislocate. |
| Foundation | Throat-and-Knee Takedown* | Throw | Control the throat while lifting or collecting the near leg. |
| Intermediate | Body-Turn Throw* | Throw | Turn the opponent across your body after gaining the upper hold. |
| Intermediate | Upper Bind | Bind | Immobilize the arm high and threaten a throw or dislocation. |
| Intermediate | Middle Bind | Bind | Pin and turn the arm across the opponent’s body. |
| Master | Lower Bind / Strong Key | Bind | Fold the arm downward into a highly controlling and dangerous lock. |
| Master | Counter-Remedy* | Counter | Defeat an established hold by changing the controlled hand, elbow or leg. |

## Dagger

### German

> Period-compatible in principle. Re-source or remove anything supported only by Meyer; the thrown-dagger sequence is specifically source-sensitive.

| Tier | Play | Type | Tactical lesson |
| --- | --- | --- | --- |
| Foundation | Upper Shield | Defence | Receive an overhand stab with the arm or dagger and enter close. |
| Foundation | Lower Shield | Defence | Cover an underhand stab and redirect the weapon arm. |
| Foundation | Free Stab from the Roof* | Attack | A committed descending dagger attack, useful against an unready target. |
| Intermediate | Arm Break | Lock | Convert a successful shield into an elbow or shoulder break. |
| Intermediate | Reversed Throw | Throw | Turn the captured dagger arm and throw the attacker backward. |
| Intermediate | Dagger-Wrap Throw* | Throw | Wind your dagger around the opponent’s arm and use it as a lever. |
| Master | Take Dagger with Dagger* | Disarm | Hook or lever the hostile dagger free with your own weapon. |
| Master | Throw Dagger and Rush | Gambit | Throw at the face as a distraction, then immediately enter to grapple. |

### Italian

> Period-compatible. Fiore's Remedy structure is retained as the principal model.

| Tier | Play | Type | Tactical lesson |
| --- | --- | --- | --- |
| Foundation | First Remedy Cover | Defence | One-handed cover against the principal high-line attack. |
| Foundation | Third Remedy Cover | Defence | Cover the reverse high-line dagger attack. |
| Foundation | Fourth Remedy Cover | Defence | Two-handed control of the attacking arm. |
| Foundation | Ninth Remedy Grip | Defence | Catch and control a low-line dagger attack. |
| Intermediate | Dagger Take | Disarm | Rotate the weapon against the elbow or wrist and take it. |
| Intermediate | Arm Dislocation | Lock | Convert a Remedy grip into a shoulder or elbow dislocation. |
| Master | Middle Bind | Bind | Transition from the cover into Fiore’s middle lock. |
| Master | Strong Key | Bind | Enter the lower bind and completely control the weapon arm. |

## Sword & Buckler

### German

> Use Lignitzer and Kal as the late-fifteenth-century core. I.33-derived wards are archaic material unless independently supported later. Sword & Buckler is a curriculum heading, not a character-sheet skill: individual Plays will specify One-Handed Sword or Shield as the Test Skill, and buckler-specific techniques require a Buckler rather than any larger shield.

| Tier | Play | Type | Tactical lesson |
| --- | --- | --- | --- |
| Foundation | Half-Shield - Halbschilt | Guard | A compact sword-and-buckler opposition used to meet several wards. |
| Foundation | Shielding - Schützen | Defence | Extend the joined weapons to cover while threatening with the point. |
| Foundation | Longpoint Bind* | Bind | Establish sword contact with both hands protected behind the buckler. |
| Intermediate | Crutch - Krucke | Guard/play | Catch or cross the opponent’s weapon with a low, hooked structure. |
| Intermediate | Underthrust from the Buckler* | Attack | Descending cut, pommel beside the buckler thumb, then thrust upward. |
| Intermediate | Wind and Snap Over* | Bind attack | Wind on the opposing blade and let the sword fall over the defence. |
| Master | Change-Strike Sequence* | Combination | Beat upward, strike the head, thrust the mouth, then cut the leg if covered. |
| Master | Pommel-and-Neck Grapple* | Grapple | Fall over the sword hand with the pommel and tear or pull at the neck. |

### Italian

OPEN: No restored Italian package is adopted yet. Rebuild from the Dardi/Bolognese continuity line, using Anonimo Bolognese, Manciolino and Marozzo as eligible witnesses while distinguishing early lineage evidence from source-unique 1530s sequences.

## Sword in One Hand

### German

> Strong period fit when sourced to Leckuchner. Flag plays that depend on the Messer's single edge, asymmetrical hilt or Nagel.

| Tier | Play | Type | Tactical lesson |
| --- | --- | --- | --- |
| Foundation | Luginsland | Specialized guard | High threatening guard that prepares powerful descending actions. |
| Foundation | Zornhau-Ort† | Attack | Oppose a committed cut and drive the point directly from the crossing. |
| Foundation | Entrüsthau† | Counter-cut | Leap offline and overturn the weapon against a high guard or descending cut. |
| Intermediate | Durchwechseln | Deception | Drop the point beneath an attempted blade contact and thrust to the other side. |
| Intermediate | Winden and Thrust* | Bind attack | Turn the strong of the blade into the bind and thrust around the defence. |
| Intermediate | Duplieren / Mutieren | Bind branch | Attack around the blade high or transform the bind into a low-line thrust. |
| Master | Hand or Wrist Cut* | Precision attack | Attack the hands when the opposing weapon is held extended or high. |
| Master | Messer Taking* | Grapple/disarm | Seize the weapon arm or hilt and use blade, pommel or body to disarm. |

### Italian

RESTORATION STARTED: One direct earlier-tradition candidate is now added from Fiore’s explicit sword-in-one-hand scenario against three attackers. The rest of the Italian package remains OPEN and should be rebuilt from Monte and the Dardi/Bolognese continuity line, including eligible Manciolino/Marozzo material, with item-level source dating.

| Tier | Play | Type | Tactical lesson |
| --- | --- | --- | --- |
| Master | Sword Against Three*† | Engagement control | Use one-handed sword, guard and movement to keep several attackers from bringing their actions to bear together; convert the encounter toward one-at-a-time threats. Fiore explicitly frames survival against three as exceptional and tells the attackers to come one by one. |

## Axe & Mace

### German

> Mixed direct and reconstructed material from Kal, Falkner, Talhoffer and related axe/poleaxe principles. Keep reconstruction labels visible. The curriculum includes shielded actions such as Behind the Shield, Cast the Mace and Shield Separation. Those Plays may require Shield and may test either Axe & Mace or Shield according to which implement performs the decisive action.

| Tier | Play | Type | Tactical lesson |
| --- | --- | --- | --- |
| Foundation | Behind the Shield | Specialized guard | Maintain the weapon chambered while the shield closes the direct line. |
| Foundation | Strike the Hands | Precision attack | Attack the weapon hand when the opponent throws, misses or overextends. |
| Foundation | Overhand Death Blow* | Power attack | A strongly committed descending blow to head, shoulder or weapon arm. |
| Intermediate | Cast the Mace | Ranged gambit | Throw the mace at an opening, normally while protected by a shield. |
| Intermediate | Follow the Cast* | Rush | Immediately close behind a thrown weapon before the opponent can exploit the loss of reach. |
| Intermediate | Hook and Tear* | Weapon control | Use an axe beard or hammer head to draw aside a shield or weapon. |
| Master | Shield Separation* | Control | Hook or beat the shield away, creating an opening for the next attack or an ally. |
| Master | Haft-and-Arm Throw* | Grapple | Crowd the enemy, trap their arm with the haft and throw or disarm them. |

### Italian

> Reconstruction-heavy package. Monte is now a core late-fifteenth-century witness despite the 1509 Latin printing; Fiore/Vadi axe and close-play principles may supplement him. Keep reconstruction labels visible where no directly preserved one-handed curriculum exists.

| Tier | Play | Type | Tactical lesson |
| --- | --- | --- | --- |
| Foundation | Guardia Alta della Mazza* | Specialized guard | Hold the weapon mobile and high enough to threaten either descending diagonal. |
| Foundation | Beat and Strike*† | Defence/attack | Beat the hostile weapon aside with haft or head and immediately attack. |
| Foundation | False Blow* | Feint | Begin a committed swing, arrest or redirect it, and attack the newly opened line. |
| Intermediate | Hook the Arm* | Control | Catch an elbow, wrist or weapon arm with an axe beard or hammer neck and pull it offline. |
| Intermediate | Armour-Gap Pick* | Precision attack | Use a hammer pick or pointed mace against visor, armpit or another vulnerable opening. |
| Intermediate | Passing Blow*† | Footwork attack | Pass obliquely past the enemy’s weapon while delivering a descending or horizontal blow. |
| Master | Hook and Cast* | Takedown | Hook behind knee, neck or arm and use the passing step to throw. |
| Master | Close Play of the Axe* | Grapple system | After a Parry or weapon crossing, shorten the grip and enter into pommel strikes, locks or throws. |

## Longsword

### German

> Best-supported package: fifteenth-century Liechtenauer witnesses including Pseudo-Danzig, Lew, Kal and late-century continuators.

| Tier | Play | Type | Tactical lesson |
| --- | --- | --- | --- |
| Foundation | Zornhau-Ort† | Counter-attack | Meet a committed cut and immediately threaten with the point. |
| Foundation | Krumphau | Master strike | Attack across the opponent’s weapon or hands, especially against high point guards. |
| Foundation | Zwerchhau† | Master strike | Horizontal short-edge action that closes the high line while striking. |
| Intermediate | Schielhau | Master strike | Oblique short-edge strike against extended point or strong commitment. |
| Intermediate | Scheitelhau | Master strike | High descending attack that defeats a low invitation such as Alber. |
| Intermediate | Nachreisen | Pursuit | Strike during the opponent’s preparation, miss or withdrawal. |
| Intermediate | Absetzen† | Defence/attack | Set aside an incoming attack while placing your point into the opponent. |
| Intermediate | Durchwechseln | Deception | Change the point beneath an attempted bind to the opposite opening. |
| Master | Winden | Bind system | Turn through upper and lower hangings according to pressure in the bind. |
| Master | Duplieren / Mutieren | Bind branches | Double around a strong defence or mutate underneath into a thrust. |
| Master | Durchlaufen | Grapple | Run beneath high arms into a throw or body control. |
| Master | Kron / Crown Crossing | Bind state | Receive a descending attack in Crown, creating a special crossing that can itself be broken. |

### Italian

> Strong period fit through Vadi (1482-87), with Fiore as earlier fifteenth-century contemporary tradition.

| Tier | Play | Type | Tactical lesson |
| --- | --- | --- | --- |
| Foundation | Scambiar di Punta† | Counter-thrust | Step offline and exchange the enemy’s thrust with your own point. |
| Foundation | Rompere di Punta† | Defence | Beat the hostile thrust downward and answer from the resulting opening. |
| Foundation | Colpo di Villano† | Defence/attack | Meet a powerful descending blow with structure and return immediately. |
| Intermediate | Wide Crossing Arm Cut* | Crossing play | From a favourable wide crossing, cut the exposed arms or head. |
| Intermediate | False Point* | Deception | Threaten one thrust after breaking or crossing, then change to another opening. |
| Intermediate | Pommel Strike | Close play | Enter from the close crossing and strike with the pommel. |
| Intermediate | Elbow Push and Face Cut* | Close play | Control the opponent’s elbow to turn them and open the face or back. |
| Master | Sword Taking* | Disarm | Seize blade, hilt or cross after dominating the crossing. |
| Master | Crossing Throw* | Grapple | Use the sword and arm together to cast the opponent from close play. |
| Master | Strong Key with the Sword* | Bind | Use the sword as part of the lower bind or arm lock. |
| Master | Half-Sword Thrust | Armoured play | Grip the blade and thrust accurately into an armour gap. |
| Master | Frontale / Corona Crossing | Bind state | Enter a strong crossed position suited to thrust control and close play. |
| Master | Cuts Against Many*† | Clearing / recovery | Against several opponents, keep the two-handed sword light and mobile, favor recoverable cutting actions over a thrust that can leave the weapon committed while another enemy attacks. Transparent game-facing synthesis of Vadi’s explicit advice. |

## Spear & Staff

### German

OPEN: No restored German package is adopted yet. Rebuild from Paurenfeyndt (1516), Lignitzer material transmitted there, Falkner and other eligible continuity witnesses. Meyer may compare or clarify older material but should not be the sole basis for source-unique core Plays.

### Italian

> Fiore/Vadi remain the strongest Italian core. Monte and eligible early Bolognese material may supplement them under the continuity policy; later printed sequences still require item-level continuity judgment.

| Tier | Play | Type | Tactical lesson |
| --- | --- | --- | --- |
| Foundation | Full Iron Gate Beat*† | Defence | Step offline while beating the hostile lance aside. |
| Foundation | Exchange of Thrusts† | Counter-thrust | Cross the spear while stepping offline and thrust in the same tempo. |
| Foundation | Break the Thrust*† | Defence | Drive the opposing point downward and answer before it recovers. |
| Intermediate | Boar’s Tooth Rising Thrust* | Counter-attack | Receive low and rise beneath the opponent’s weapon with the point. |
| Intermediate | Shortened Spear | Specialized guard | Grip the weapon compactly for rapid close-range thrusts. |
| Intermediate | Cross-Step Counterthrust*† | Footwork attack | Pass obliquely outside the hostile thrust and strike the body. |
| Master | Withdraw and Re-thrust* | Recovery | Pull the extended spear back through the hands and immediately renew the point. |
| Master | Beat and Close* | Close play | Beat the shaft aside and enter before the long weapon can recover. |

## Polearms / Poleaxe & Halberd

### German

> Retained as candidates. Re-source to Talhoffer, Kal, Falkner, Paurenfeyndt or other eligible continuity witnesses where possible. Meyer may be consulted comparatively but should not be the sole authority for source-unique core Plays.

| Tier | Play | Type | Tactical lesson |
| --- | --- | --- | --- |
| Foundation | Hook-and-Cut Driving Cuts* | Combination | Alternate a hooking rip from one side with a blade cut from the other. |
| Foundation | Beat Down and Thrust*† | Defence/attack | Strike the incoming weapon to the ground and thrust upward to the face. |
| Foundation | Counter-Thrust to the Heart*† | Counter-attack | Displace a blow or point and immediately thrust to the torso. |
| Intermediate | Hook the Blade and Wrench* | Weapon control | Catch the hostile shaft or head and tear it aside. |
| Intermediate | Hanging Deflection* | Defence | Sink the point while raising the rear hand to turn the thrust away. |
| Intermediate | Rear-Point Run-In* | Close play | Run beneath a weapon held too high and attack with the rear spike. |
| Master | Leg Hook* | Takedown | Catch the forward leg with blade or hook and pull it out. |
| Master | Neck Yank / Counter and Throw* | Grapple | Hook the neck or upper body and convert weapon control into a throw. |

### Italian

> Fiore/Vadi remain primary. Marozzo may now be used as a continuity witness for established Italian traditions, but source-unique 1530s actions still require an explicit continuity judgment rather than automatic backdating.

| Tier | Play | Type | Tactical lesson |
| --- | --- | --- | --- |
| Foundation | Short Serpent | Specialized guard | Compact poleaxe guard delivering a powerful armour-piercing thrust. |
| Foundation | True Cross† | Specialized guard | Cross the incoming weapon and respond with a step and thrust. |
| Foundation | Lady’s Heavy Blow* | Power attack | Deliver a major descending strike from a chambered guard. |
| Intermediate | Boar’s Tooth Rising Counter*† | Counter-attack | Enter beneath the descending axe and rise with point or head. |
| Intermediate | Long Tail Beat-Down*† | Beat | Drive the opposing polearm to the ground and enter close. |
| Intermediate | Hook and Pull* | Weapon control | Catch shaft, limb or armour with the poleaxe head and draw it off line. |
| Master | Close Poleaxe Grapple* | Grapple | Abandon wide blows and use haft, head and body to bind or throw. |
| Master | Polearm Taking* | Disarm | Trap the hostile weapon after a crossing and strip it from the opponent. |

# 8. Balance, progression and pruning targets

## 8.1 Combat observations to preserve

Evidence status: duel percentages in the first table are legacy exploratory results and should be reproduced in Codex before becoming acceptance criteria. The outnumbering and independent-tempo figures in Section 8.2 were recomputed in versioned exact zero-sum solvers and should be treated as reproducible stress-test results for the stated simplified model, not as empirical historical frequencies.

| Measure | Current observation / target |
| --- | --- |
| Equal .60 duel | About 3.14-3.17 rounds with d6+1 and the tested guard timing. |
| .50 vs .70 duel | Weaker fighter about 28% win-equivalent; about 3.37-3.42 rounds. |
| High-skill slowdown | Greatly reduced by d6+1, but not eliminated. |
| Simultaneous defeat | About 14-16% at .60/.60 in later tests; above 40% at .90/.90 in some tested variants. |
| Guard use | State-dependent across-combat variation; Power should exploit action-spent or vulnerable targets. |
| Skill curve | Damage changes pacing more than the underlying advantage of higher skill. |

| OPEN balance question: No explicit acceptable band for elite simultaneous deaths was adopted. The observed 40%+ rate is a flagged risk, not a target. |
| --- |

## 8.2 Outnumbering and tempo-compression stress tests

Model: HP 8, d6+1, one normal action each, alternating side activations, random first side each round, one pass per side, and optimal Basic Strike/Parry/Ignore/Counter play. No guards, Plays, Spiritus, armour, reach or terrain unless the scenario explicitly says bottleneck. Win-equivalent gives half credit for final simultaneous mutual defeat.

| Scenario | Win-equivalent | Reading |
| --- | --- | --- |
| 1 vs 2, all Skill 10 | 3.16% | Equal-skill lone fighter is nearly overwhelmed when both enemies can attack freely. |
| 1 vs 2, lone Skill 14 vs two Skill 10 | 9.1% | A +4 skill advantage is not close to compensating for the second body/action. |
| 1 vs 2, lone Skill 20 vs two Skill 10 | 24.6% | Skill alone still does not reach parity. |
| 2 vs 3, all Skill 10 | 7.54% | The three-person side retains a very large advantage. |
| 2 vs 3, pair about Skill 19 vs three Skill 10 | ~50% | Very large per-fighter skill advantage is required for parity in unrestricted engagement. |
| 1 vs 2 bottleneck, lone Skill 18 vs two Skill 10 | 55.7% | If only one opponent can engage at a time, the same basic action economy becomes favorable to the master. |
| 1 vs 2 bottleneck, lone Skill 20 vs two Skill 12 | 52.5% | Engagement geometry can matter more than raw numerical bonuses. |

### Independent restricted tempo tokens

Apples-to-apples experiment: each fighter on the smaller side receives either one independent Offensive Tempo token (one Strike per round that does not spend the normal action) or one independent Defensive Tempo token (one Parry or Counter per round that does not spend the normal action). The token can be used before or after the normal action is spent.

| Scenario | Normal | + Defensive tempo | + Offensive tempo |
| --- | --- | --- | --- |
| 1 vs 2, all Skill 10 | 3.16% | 12.02% | 25.84% |
| 1 vs 2, lone Skill 14 vs two Skill 10 | 9.1% | 32.4% | 49.4% |
| 1 vs 2, lone Skill 18 vs two Skill 10 | 18.6% | 57.4% | 71.1% |
| 2 vs 3, all Skill 10 | 7.54% | 25.24% | ~51.95% |

### Design reading

- Offensive tempo is stronger because an attack can both remove an enemy and force that enemy to spend an action defending; defensive tempo mainly answers a threat already generated.
- Independent defensive tempo is nevertheless a major benefit. A generic “Parry without spending your action” cannot be priced like a routine Boon.
- The master-vs-many fantasy should come from narrow source-specific tempo compression, recovery and engagement control rather than a blanket outnumbered bonus or unconditional extra action.
- Movement/terrain rules must eventually model how many opponents can actually engage. A nominal 2:1 advantage should be much less valuable when one opponent physically screens the other.
- Existing single-time candidates such as Zornhau-Ort, Absetzen, Scambiar di Punta, Exchange of Thrusts and similar defence-and-attack actions are natural places to test anti-number utility before inventing many new cards.
> Historical direction: Fiore explicitly presents a one-handed sword master against three attackers as an exceptional survival problem and has them approach one by one. Vadi advises avoiding fights with several opponents; if forced, he favors a light, manageable two-handed sword and warns that thrusts can leave the weapon committed while another enemy attacks. These are used as design evidence, not as proof of any specific Atra mechanic.

## 8.3 Character repertoire

| Career stage | Total Plays | Expected shape |
| --- | --- | --- |
| Beginning | 2-4 | Basic techniques in one weapon. |
| Competent | 5-8 | Coherent primary branch plus one emergency technique. |
| Veteran | 9-12 | Broad primary repertoire and small secondary skill. |
| Master | 13-16 | Advanced branches plus one or two signature Master Plays. |
| Exceptional specialist | 17-20 | Rare upper limit; concentrated in one tradition. |

- Typical experienced PC: 8-12 Plays.
- Typical end-of-career PC: 10-14 Plays; design around 12.
- Primary skill/curriculum: 6-8; secondary skill/curriculum: 2-3; Wrestling/Dagger: 1-3; optional armour/shield package: about 1.
- At a decision point, normally 0-2 eligible Plays; 3 is unusually rich; more than 4 signals overlap or weak gating.
- Begin with about 3 Plays; gain roughly one Play every two significant advancements, with teachers/manuscripts as alternate access.
## 8.4 Catalog funnel

| Stage | Plays |
| --- | --- |
| Current research candidates | 114 |
| Restore/rebuild remaining culture slots under continuity policy | +17 to +23 |
| Expanded research roster | 131-137 |
| Prune unsupported/redundant material | -20 to -25 |
| Consolidate variants/minor sequences | -15 to -20 |
| Likely final core | 85-100 |
| Preferred target | About 90 |

Mechanical chassis target: About 25-35 reusable patterns across the full game.

Final package target: About 5-7 Plays per ordinary culture/curriculum package and 8-10 per Longsword package.

Pruning test: Historical, mechanical, procedural and curricular. Merge/remove target-only variants, left/right mirrors, minor numerical differences, automatic next steps and redundant cultural renamings.

# 9. Codex Martialis benchmark

Codex Martialis is a comparison benchmark, not a source of Atra canon. The attached 2024 v8.2 rulebook is 117 pages. Chapter 2 begins Basic Devices on p.25, Advanced Devices on p.41 and Shooting Devices on p.54. [CM pp.25, 41, 54]

| Dimension | Codex Martialis | Atra target |
| --- | --- | --- |
| Named abilities | 97 Devices counted in the project comparison | 114 current research candidates; about 90 final target |
| Starting repertoire | Usually 1-3 Devices | About 2-4 Plays |
| Mature repertoire | Example archetype packages of 6 Devices | About 10-14 Plays |
| Breadth | Melee, missiles, mounts, formations, injuries and multiple martial traditions | c.1475-1540 German/Italian melee and grappling, with continuity-based source inclusion |
| Core engine | Martial Pool allocation | One action, reactions, public guard and Spiritus |
| Technique density | Broad mix of tactical options, passive bonuses and talents | More specific guards, Remedies, continuations, crossings and grapples |

Design consequence: Atra can sustain a catalog about as large as Codex's only if guard, weapon, measure, action state and trigger keep the moment-to-moment menu small.

Weapon warning: Codex differentiates weapons through reach, speed, defence, attack type and armour piercing. Atra must preserve strong base weapon identity so Plays are not forced to repair generic weapons.

# 10. Chronological decision log

| Date | Chat | Decision | Status | Record |
| --- | --- | --- | --- | --- |
| 2026-08-05 | 001 | Initial baseline | PROVISIONAL | 6-second rounds, grid, one action, Spiritus, zipper initiative, movement, d20 roll-under, d6 damage, three reactions and tag-based guards. |
| 2026-08-05 | 006 | Initiative rerolled each round | ADOPTED | Supersedes persistent first-side initiative. |
| 2026-08-05 | 010-013 | Pass rule | ADOPTED | One pass per side supersedes unlimited passing and the proposed one pass per character. |
| 2026-08-06 | 013 | First guard package | PROVISIONAL | High/low Online, Power and Barrier tags; free before-or-after change; unguarded opening. |
| 2026-08-06 | 017-019 | Online checks Power | PROVISIONAL | Counter Boon expanded to Power attacks. |
| 2026-08-06 | 020-027 | Power correction | ADOPTED | Power on Counters identified as an error; Power becomes proactive-Strike-only. |
| 2026-08-06 | 028-031 | d6+1 | ADOPTED | Current damage test baseline; combat accelerates and Online becomes more relevant. |
| 2026-08-06 | 032-039 | Barrier 2 DR and historical review | REJECTED | Passive DR gives the wrong identity; active Cover recommended. |
| 2026-08-06 | 040-044 | Guard triangle test | PROVISIONAL | Threat Counter Boon, Chamber damage Boon and Cover Parry Boon is best tested family model. |
| 2026-08-06 | 045-048 | Free guard change | ADOPTED | Once per turn before or after; removes pre-action Spiritus fee. Simultaneous start suggestion later rejected by sequential-only instruction. |
| 2026-08-06 | 049-052 | Recovery transitions | DEFERRED | Natural transition graph proposed, then explicitly set aside. |
| 2026-08-06 | 052-056 | Power Strike costs Spiritus | PROVISIONAL | At modest opportunity cost, produces desired guard variety; depends on actual Play power. |
| 2026-08-06 | 055-056 | Sequential/public guard system | ADOPTED | No simultaneous choice; public HP/guards, hidden skill and repertoire. |
| 2026-08-06 | 057-059 | Bespoke named guards | OPEN | Later untested proposal would make effects unique and leave tags for indexing/gating only. |
| 2026-08-06 | 060-062 | First complete longlist | SUPERSEDED | 136 candidates across eight initial weapon skills before Axe & Mace was added and before the strict period audit. |
| 2026-08-06 | 063-064 | Axe & Mace | ADOPTED | Adds a ninth weapon skill and 16 candidates, raising the provisional pre-audit pool from 136 to 152. |
| 2026-08-06 | 065-069 | Strict late-1400s audit | SUPERSEDED | Removed Rapier and 40 later-source candidates, leaving 112 across eight skills and 24 empty culture slots. That 112 is now the historical baseline count; v0.4 adds two new research candidates under the continuity/anti-number review, bringing the current catalog to 114. |
| 2026-08-06 | 070-072 | Play template | PROVISIONAL | Defines card/data fields, timing taxonomy, exchange sequence, cost scale and confidence grades. |
| 2026-08-06 | 073-076 | Progression and pruning | PROVISIONAL | 10-14 career Plays, about 90 final named Plays, 25-35 chassis. |
| 2026-08-06 | 077-078 | Codex comparison | REFERENCE | Atra aims for similar catalog size, narrower scope and deeper period-melee granularity. |
| 2026-08-07 | 083-084 | Freeze v0.1 | ADOPTED | Create canonical packet before implementing individual Play mechanics. |
| 2026-08-06 | Post-v0.1 | Guard height clarification | ADOPTED | Height remains mechanically meaningful; high and low guards in each current family are mirror-image implementations rather than height-agnostic guards. |
| 2026-08-06 | Post-v0.1 | Source horizon revision | ADOPTED | Primary campaign remains the 1490s, but the common martial corpus uses a c.1475-1540 horizon and continuity-based source policy. Manciolino/Marozzo, Paurenfeyndt and Auerswald become eligible continuity witnesses; Mair may preserve older material; Agrippa/Meyer mark later innovation boundaries. |
| 2026-08-06 | Post-v0.1 | Freeze v0.2 | ADOPTED | Update the design constitution for Codex handoff without silently finalizing guard architecture, restored culture packages or the Play-chain timing contradiction. |
| 2026-08-06 | Post-v0.2 | Skill/curriculum separation | ADOPTED | Character-sheet skills are independent of Play curriculum headings. Sword & Buckler becomes a curriculum under One-Handed Sword + Shield rather than its own skill. |
| 2026-08-06 | Post-v0.2 | Implement-based rolls and off-hand gates | ADOPTED | Shield Parries roll Shield; off-hand dagger actions roll Dagger; every Play specifies its Test Skill and may require secondary skills. Off-hand requirement becomes a first-class Play field. |
| 2026-08-06 | Post-v0.2 | Melee skill roster v0.3 | ADOPTED | Eight skills: Wrestling, Dagger, One-Handed Sword, Axe & Mace, Longsword, Shield, Spear & Staff, Poleaxe & Halberd. |
| 2026-08-06 | Post-v0.2 | Freeze v0.3 | ADOPTED | Update the design constitution and Codex handoff to encode separate skill, curriculum, equipment and Play layers. |
| 2026-08-07 | Post-v0.3 | Outnumbering exact solver | REFERENCE | Basic combat with unrestricted engagement is extremely harsh on the smaller side: 1v2 equal Skill 10 ≈3.16%; 2v3 equal Skill 10 ≈7.54%. Bottleneck tests show that forcing sequential engagement can reverse this without changing the core action economy. |
| 2026-08-07 | Post-v0.3 | Independent tempo stress test | ADOPTED | Once-per-round independent restricted tempo is a major effect. Equal Skill-10 1v2 rises from 3.16% to 12.02% with extra defensive tempo and 25.84% with extra offensive tempo; equal Skill-10 2v3 rises from 7.54% to 25.24% / ~51.95%. Generic action preservation must be treated as high-power. |
| 2026-08-07 | Post-v0.3 | Master against many direction | ADOPTED | Favor source-specific engagement control, clearing/recovery and single-time defence-and-offence Plays over blanket bonuses for being outnumbered. |
| 2026-08-07 | Post-v0.3 | Longlist anti-number additions | ADOPTED | Add Sword Against Three* (Fiore one-handed sword scenario) and Cuts Against Many* (Vadi-based transparent synthesis) as research candidates, and tag existing likely tempo-compression/engagement-control Plays for testing. Current longlist becomes 114. |
| 2026-08-07 | Post-v0.3 | Freeze v0.4 | ADOPTED | Update the design constitution for Codex with reproducible outnumbering results and anti-number research direction while leaving exact engagement and action-preservation mechanics OPEN. |

# 11. Approval gate before implementation

The record explicitly calls for reviewing this packet as the melee system's constitution before finalizing simulations or individual Play mechanics. A permissive research schema may be encoded earlier, and should now represent the separate Skill, Curriculum, Test Skill, secondary-skill and off-hand fields.

- Confirm the ADOPTED and PROVISIONAL classifications, especially d6+1 and the Power Strike Spiritus cost.
- Choose the guard architecture: tested family triangle or bespoke named effects.
- Choose the starting-guard procedure.
- Resolve the three-Play exchange limit versus the four named procedural steps in Section 3.6 before implementation.
- Set an acceptable elite simultaneous-defeat band or decide that high mutual lethality is intentional.
- Audit the 114 current research candidates item by item; then restore/rebuild the remaining 23 culture-slot candidates as appropriate under the continuity policy. Record attestation date, inclusion basis and confidence for every Play.
- Define base weapon and shield equipment dimensions before using Plays to differentiate every implement; Shield skill should not make bucklers and large shields mechanically identical.
- Encode a permissive research/source/Play schema for Codex now, including Curriculum, Test Skill, secondary-skill requirements, off-hand requirement and equipment traits. Allow incomplete mechanics and OPEN status. Do not finalize Play mechanics until the timing contradiction, prototype guard architecture and one prototype curriculum (preferably Longsword) have been tested.
- Implement an engagement/access state in the solver before deciding whether the base rules need any generic outnumbering modifier.
- Prototype source-specific tempo-compression Plays (especially Zornhau-Ort, Absetzen, Scambiar di Punta and the new against-many candidates) before assigning fixed Spiritus prices to action preservation.
- Keep “Sword Against Three*” and “Cuts Against Many*” as research candidates until exact source locators and mechanical chassis are audited.
# 12. Source index

| Source group | Record | Use |
| --- | --- | --- |
| Design record | Shared 'HEMA exchanges per 6 seconds' conversation, Atra Melee Design Packets v0.1-v0.3, and Project clarifications through 2026-08-07. | Primary chronological decision record for v0.4. |
| Codex Martialis | Jean Chandler, Codex Martialis Core Rulebook 2024 Edition, v8.2, 117 pp. | Comparison benchmark only; not Atra canon. |
| Italian direct / earlier | Fiore dei Liberi; Philippo di Vadi; Pietro Monte (late-1400s Spanish composition; expanded Latin Collectanea printed 1509). | Core Italian evidence. Monte is treated as a fifteenth-century martial witness despite publication in 1509. |
| Bolognese continuity | Filippo Dardi (licensed fencing master in Bologna in 1412); Anonimo Bolognese; Antonio Manciolino, Opera Nova (1531, with evidence of earlier publication activity); Achille Marozzo, Opera Nova (1536). | Eligible continuity line for Sword & Buckler and Sword in One Hand. Later print date does not prove every listed sequence existed unchanged in 1490. |
| German direct / earlier | Pseudo-Peter von Danzig; Lew; Paulus Kal; Hans Talhoffer; Johannes Lecküchner; Peter Falkner; Ott Jud / Andre Lignitzer. | Core German evidence for the late-fifteenth-century martial world. |
| German continuity | Andre Paurenfeyndt, Ergründung Ritterlicher Kunst der Fechterey (1516); Fabian von Auerswald, Ringer Kunst (1539; author born 1462). | Eligible early-sixteenth-century continuity witnesses; especially useful for pole weapons, Lignitzer material and wrestling. |
| Later preservation witness | Paulus Hector Mair, mid-sixteenth-century compilations; Mair began collecting older fencing manuscripts in the 1540s. | May preserve, copy or clarify older lineages. Source-unique material is not automatically backdated. |
| Archaic caution | MS I.33 (c.1320s). | Optional archaizing source; not the normal late-fifteenth-century school without later corroboration. |
| Innovation boundary / outside core | Camillo Agrippa, Trattato di Scientia d'Arme (1553); Joachim Meyer, 1561 manuscript and 1570 print; dall'Agocchie (1572); later mature rapier writers including Giganti and Capo Ferro. | Agrippa's new geometrized system and Meyer's explicit updating/reinvention mark the presumptive mid-sixteenth-century cleavage. Use only where an action is independently earlier-attested or explicitly imported. |
| Fiore - multiple opponents | Fiore dei Liberi, Sword in One Hand: a Master is presented against three attackers (thrust, cut, thrown sword); the text calls survival a great feat and directs opponents to come one by one. | Direct earlier-tradition evidence for the Sword Against Three* research candidate and for engagement-control design. |
| Vadi - fighting several | Philippo di Vadi, De Arte Gladiatoria Dimicandi, advice on fighting more than one opponent and the dispute of cuts and thrusts: avoid such fights; if forced, use a light/manageable sword, favor recoverable cuts and beware a thrust that leaves the weapon committed while another enemy attacks. | Direct late-fifteenth-century design evidence for Cuts Against Many* and the recovery/clearing role. |
| German counsel on overwhelming numbers | Pseudo-Hans Döbringer / early Liechtenauer tradition: advice treats standing against several opponents as foolish and permits flight from overwhelming numbers. | Design evidence that numerical superiority should remain dangerous; not by itself a source for a specific technique. |

# Atra Melee Design Packet v0.5

## Current Governing-Provisional Vertical Slice

**Publication date:** 2026-08-13  
**Status:** GOVERNING PROVISIONAL  
**Review boundary:** Project review required before the next milestone  
**Predecessor:** Atra Melee Design Packet v0.4 (preserved; superseded only where this packet says so)

This packet is the current durable synthesis of the implemented longsword vertical slice. It is neither a final melee system nor a claim that the complete historical curriculum has been mechanized. It consolidates the rules that now agree across adjudication records, governing prototype data, the authoritative shared engine, and deterministic tests.

## 1. Reading and status policy

Historical evidence and Atra mechanics remain separate. A source-supported lesson can justify a design target without proving the chosen cost, die modifier, timing window, state name, or damage model. Simulation results test game behavior; they are not historical evidence.

| Status | Meaning in this packet |
|---|---|
| GOVERNING PROVISIONAL | Current rule for this vertical slice. Change only through explicit Project adjudication. |
| PROVISIONAL TEST BASELINE | Fixed experimental baseline used to interpret tests, not a final universal value. |
| LOCAL EXCEPTION | An authored rule whose state or procedure is confined to a named Play/context. |
| COMPATIBILITY DEBT | Preserved older behavior needed by an existing authored branch but not accepted as the general model. |
| SUPERSEDED | No longer current in the scope named by the superseding record. |
| REJECTED | Tested or proposed rule that the Project declined. |
| OPEN | Requires a Project decision; this packet does not resolve it. |
| DEFERRED | Intentionally outside this slice. |

## 2. Design principles and effect grammar

1. One visible combat state should earn its complexity through real downstream choices.
2. Learned Plays must be mechanically distinct from an available Basic or be recorded as incomplete.
3. Costs, action compression, timing, state aftermath, counterplay, and continuation value are all part of a Play's budget; there is no universal effect-count arithmetic.
4. Response denial is exceptional. A named Play does not remove ordinary responses unless its authored rule explicitly says so.
5. A successful historical technique does not authorize unsourced geometry, bonuses, or universal subsystems.
6. State must have legal writers, legal readers, visible ownership, and cleanup.

The current grammar uses ATTACK, CANCEL, SET, CLEAR, RETAIN, MODIFY_ATTACK, and the narrowly exceptional REPLACE_PENDING_ATTACK. RESTRICT_RESPONSE remains available only for explicitly justified exceptions; no current governing Play in this slice gains a response restriction merely because it is named.

## 3. Core procedure

### 3.1 Exchange, action, and chain

- A fighter normally has one action in the round. Attacks and Basic defensive responses spend it unless an authored continuation says "no additional action."
- A learned Play declaration adds one entry to the current learned chain unless its record says it is intrinsic rather than a new Play.
- The learned-chain cap is **3**. This is GOVERNING PROVISIONAL for the slice, not a final all-weapons rule.
- Exchange cleanup clears the learned chain and any unretained transient windows.
- The current test baseline uses **8 Health** and **8 maximum Spiritus**. The 8-Spiritus maximum is a PROVISIONAL TEST BASELINE, not final character advancement.

### 3.2 Roll and damage baseline

- A normal test uses the weapon skill against the current target number procedure.
- A Boon rolls an additional die and keeps the better result; a Bane keeps the worse result under the existing engine convention.
- Normal longsword damage is `d6 + 1`, bounded 2–7.
- Cut and Thrust have the same base numerical output but different response and repertoire topology.
- A proactive Basic Cut from Loaded receives Damage Boon. The exact expected damage is **3.830555...** under the current bounded damage procedure.

### 3.3 Spiritus

Spiritus buys authored compression, timing, information, or state transitions. It is not a generic difficulty currency and does not itself prove historical importance.

| Option | Spiritus | Chain | Additional action? |
|---|---:|---:|---|
| D1 Durchwechseln | 1 | +1 | No; uses the initiating action |
| S2 Schielhau | 2 | +1 | Yes; it is the defensive action |
| D1 inside S2 | 1 | +1 | No |
| C2 Absetzen / Scambiar / generic Schielhau | 2 | +1 | Defensive action |
| P1 Power | 1 | 0 | Proactive action |
| Nachreisen | 1 | +1 | Target's action |
| Fühlen in ordinary H3 | 1 | 0 | No |
| Duplieren / Mutieren | 2 | +1 | No |
| Upper / Lower Winding Thrust | 2 | +1 | No |
| T1 Tutta Cover to Stretto | 1 | +1 | No |
| P2 Pommel | 2 | +1 | No |
| Zornhau-local Ort | 1 | intrinsic | No second roll |
| Zornhau-local Winden compatibility | 1 | +1 | No |

## 4. Basics and universal state

### 4.1 Basic Cut and Basic Thrust

Basic Cut and Basic Thrust are flat normal attacks for normal damage. Cut participates in Loaded, Power, descending-cut, and cut-specific response gates. Thrust participates in its own response and compound-counter topology. Equal base numbers do not make the choices identical.

### 4.2 Basic Cross

Before an ordinary Basic Cross roll, its defender secretly authors initial pressure:

- **Hart:** exactly one defensive Boon.
- **Weich:** flat defence.

On success, Cross cancels the pending attack, establishes actionable Crossing, preserves measure, writes a public bind height of Upper, Lower, or Unknown from authored geometry, and does **not** write ordinary Favored/Unfavored. It then opens E1 where applicable; otherwise it opens the narrow H3 attacker Rejoinder. On failure, contact, initial pressure, and height are cleared.

### 4.3 Basic Beat

On success, Beat cancels the pending attack, displaces the hostile weapon, clears contact, sets the opponent Open, and removes that opponent's point threat. It creates no generic follow-on bonus or penalty. Beat and Cross share the pre-contact D1 timing window but have different aftermath.

### 4.4 Ignore and Counter

Ignore accepts the hit and preserves the action if the fighter survives. Its utility remains policy- and survivability-dependent; the grammar validator's ghost-utility warning is EXPECTED PROVISIONAL DEBT, not a concealed bonus.

Ordinary Counter is declared after a successful attack roll, spends the target's action, accepts the incoming damage, and resolves simultaneous normal counter-damage.

### 4.5 D1 state-based Durchwechseln

D1 is available after a Basic Cross or Beat is declared and before its roll, while contact is None, the defender is committing toward the actor's weapon, the defender's point is not threatening, reserve and chain capacity exist, and the attack is not Committed. Pay 1 Spiritus and +1 chain; skip the declared defence roll and replace the pending attack with one fresh normal thrust roll. D1 creates no Crossing and sets the winner's point threatening on resolution.

### 4.6 Open and voluntary guard change

Open is a public guard state produced by Basic Beat. It is not a numeric penalty and does not invent generic vulnerability beyond authored gates.

GC1 permits one voluntary all-to-all named-guard change on the fighter's activation before the action. The chosen guard persists through the following opponent opportunity. This is an Atra accessibility abstraction and makes no historical claim that every pair of guards has a direct source-described transition.

## 5. Committed, Power, and Nachreisen

### 5.1 General Committed timing

Committed is public on declaration and belongs to the pending attack, not exclusively to Power.

1. Before the Committed attack roll, its target alone may choose a normal Counter or an authored Preparation such as Nachreisen.
2. That response resolves first. If it removes the attacker, the pending attack is cancelled; otherwise the attack proceeds.
3. If the target waits and the attack succeeds, ordinary post-success responses remain available, including simultaneous Counter.
4. If the attack misses, no retroactive ordinary Counter appears. Only an authored immediate Recovery window may exist.
5. Committed prevents attacker-side D1 or other insertion where the attack record says so.

This general procedure supersedes the stale Power-only "Counter-first" description.

### 5.2 P1 Power Attack

From Loaded, spend the proactive action and 1 Spiritus to declare a Committed descending Power Cut. Roll flat; on hit deal fixed 7 damage. Loaded Damage Boon does not stack. P1 prevents attacker continuations and inherits the general Committed timing above; it does not own a private response-denial rule.

### 5.3 Nachreisen

Nachreisen is GOVERNING PROVISIONAL in two target-only windows against a Committed attacker:

- **Preparation:** before the pending attack roll.
- **Recovery:** immediately after that attack misses.

Spend the target's action, 1 Spiritus, and +1 learned-chain entry. Roll a Booned Longsword attack for normal damage. Preparation cancels the pending attack only if it removes the attacker; otherwise the attack proceeds. Recovery expires immediately if unused. Vom Tag is audited source context, not a current hard mechanical gate. The current model introduces no persistent universal Recovery state.

## 6. Compound responses and S2

### 6.1 C2 compound chassis

Absetzen, Scambiar di Punta, and the generic Schielhau C2 each cost 2 Spiritus and +1 chain and spend the defensive action. One fresh joined defence/offence roll cancels on success and deals normal damage. Absetzen and Scambiar create their authored threatening-point Crossing; generic Schielhau remains separate from S2.

### 6.2 Selected S2 Schielhau / Durchwechseln interaction

S2 is a LOCAL EXCEPTION, not a universal opposed-roll architecture.

1. Against a qualifying successful descending-cut attack before contact, the defender declares Schielhau, spends the defensive action, 2 Spiritus, and +1 chain, and rolls once.
2. On failure, no S2 window exists and the original strike remains unresolved.
3. On success, retain that exact successful Schielhau result. Delay Schielhau's cancellation, damage, point-threat, and contact consequences and open one D1 decision for the original striker.
4. The striker may decline, lack prerequisites, or spend 1 Spiritus and +1 chain to declare D1 with no additional action.
5. If D1 is declared, roll one fresh D1 result. Compare successful rolls low-wins; a tie favors Schielhau. One success beats one failure. The helper's both-fail cell returns to the original strike, although it is unreachable from the live successful-Schielhau gate.
6. Schielhau win: cancel the original strike, deal normal damage to the striker, set Schielhau's point threatening, preserve measure, and leave no contact.
7. D1 win: replace and resolve the original strike as a normal Durchwechseln thrust, deal normal damage to Schielhau's actor, set D1's point threatening, preserve measure, and leave no contact.
8. Decline or window expiry resolves Schielhau. Actor removal, invalidation, new-attack expiry, exchange end, and both resolution routes clean the transient S2 state.

The proactive Schielhau-to-Pflug breaker remains OPEN and receives no hidden modifier.

## 7. Ordinary H3 bind

### 7.1 Scope and supersession

H3-L2 is the GOVERNING PROVISIONAL model for ordinary Basic Cross. It supersedes roll-derived or randomly authored ordinary Favored/Unfavored. That relation remains only as Zornhau-local COMPATIBILITY DEBT.

### 7.2 Initial Hart/Weich and public height

Initial Hart/Weich is private, authored before the Cross roll, and phase-scoped. Public bind height is Upper, Lower, or Unknown. Qualifying upper-cross geometry against a descending high cut writes Upper; qualifying lower setting-aside geometry against the authored low lines writes Lower; other cases write Unknown.

### 7.3 E1 before H3

After a qualifying Tutta Cross and after D1 timing, E1 is offered before H3 Rejoinder creation. If T1 is used, H3 is never created. If declined, the ordinary H3 Rejoinder opens.

### 7.4 Fühlen and Bind Rejoinder

Only the original striker receives the narrow Rejoinder. Fühlen may be bought once in that ordinary Rejoinder for 1 Spiritus, no action, and no chain entry. It reveals the opponent's initial Hart/Weich for that bind and creates no persistent generic pressure axis.

Duplieren and Mutieren each cost 2 Spiritus and +1 chain with no additional action. Correct read:

- Duplieren against Hart declares a Booned normal-damage cut.
- Mutieren against Weich declares a Booned normal-damage thrust, retains the authored transition, and sets point threat.

A wrong read spends the cost, makes no roll, deals zero damage, and ends the bind sequence. Declining assigns the first ordinary bind opportunity: Hart to the original striker, Weich to the defender, then clears initial pressure.

### 7.5 Opportunity and cleanup

The opportunity holder alone may declare a legal continuation, pass, or disengage. The first pass transfers opportunity; two consecutive passes clear Crossing. Disengage clears Crossing. A continuation hit clears its bounded bind unless the authored rule says otherwise; an authored miss may retain and transfer.

### 7.6 Upper and Lower Winding Thrusts

Each costs 2 Spiritus and +1 chain with no additional action, requires its matching public bind height and current opportunity, retains Crossing, sets Ochs/upper or Pflug/lower hanging point threat, and makes a flat thrust for normal damage.

- Upper miss retains Upper/Ochs/point threat and transfers opportunity.
- Lower miss transforms Lower to Upper, Pflug to Ochs, retains point threat, and transfers opportunity.
- A hit deals normal damage and clears the bounded bind.

## 8. T1 Close and Pommel

### 8.1 T1 Tutta Cover to Stretto

T1 requires a successful qualifying Basic Cross from Tutta against an ordinary proactive, non-Power, non-Committed Basic Cut at Wide, after D1 and before H3. Spend 1 Spiritus and +1 chain; no additional action or roll. Retain Crossing, change Wide to Close, set height Unknown, clear initial pressure, and assign the first Close opportunity: Hart to the original striker, Weich to the Tutta defender.

### 8.2 P2 Pommel

Pommel is a generic consumer of established Close Crossing for the current opportunity holder. Spend 2 Spiritus and +1 chain; no additional action. Make a flat Longsword test for `d6 + 1` normal damage. It authors no response denial. Hit clears the bounded bind. Miss deals zero, retains Close/Unknown Crossing, and transfers opportunity.

Broader Close play, throws, seizures, armor, and generic closing remain DEFERRED.

## 9. Zornhau local branch

The current Zornhau-Ort branch is GOVERNING PROVISIONAL only as a local authored line and carries COMPATIBILITY DEBT.

- Successful initial Zornhau cancels a qualifying descending cut, establishes a threatening-point Crossing, and writes the preserved local Favored/Unfavored relation.
- Ort costs 1 Spiritus, requires local Favored, uses no second attack roll, and deals normal damage under O1.
- The preserved local Winden compatibility path costs 1 Spiritus and +1 chain and is not the ordinary H3 Upper/Lower Winding procedure.
- Fühlen's older reader for this relation and variant W1/W2 assumptions remain local compatibility, not general ordinary-bind law.

## 10. Named guards

The exact implemented roster is eight guards. Guard names carry source identity, public posture, intrinsic state, and explicit gates; they do not automatically grant attack modifiers.

| Guard | Public posture | Current intrinsic/gates | Boundary or gap |
|---|---|---|---|
| Vom Tag | High, cut-ready, not threatening, not Loaded | Source context for Nachreisen | No current hard Nachreisen gate |
| Ochs | High, point threatening, upper hanging | Upper Winding gate/aftermath | Zwerch breaker mapping is evidence, no automatic modifier |
| Pflug | Low, point threatening, lower hanging | Absetzen and Lower Winding access | Proactive Schielhau breaker OPEN |
| Alber | Low, not threatening | No invitation bonus | Crown/Scheitel interaction DEFERRED |
| Posta di Donna | High, cut-ready, not threatening, Loaded | Loaded Basic Cut and P1; Scambiar access | Loaded is an Atra abstraction |
| Frontale | High, not threatening | Basic Cross against high thrust; Basic Beat against low thrust | Longer sequence incomplete/DEFERRED |
| Tutta Porta di Ferro | Low, not threatening | Cross/Beat, Scambiar access, governing T1 | T1 is the bounded Close bridge |
| Mezza Porta di Ferro | Low, point threatening | Basic Thrust and Beat access | Beat-return sequence candidate gap |

Source breaker mappings remain explicit evidence relationships: Zwerchhau→Vom Tag, Krumphau→Ochs, Schielhau→Pflug, Scheitelhau→Alber. None creates an automatic numerical breaker bonus in the current rules.

## 11. Italian/German boundaries

German and Italian records may share engine vocabulary without collapsing historical identity. H3 Crossing is an Atra engine state used for actionable weapon contact. Absetzen and Scambiar share the C2 mechanical chassis but preserve distinct sources and access geometry. Tutta/T1/Pommel is an authored Italian bridge to bounded Close. German Zornhau-local relation and S2 remain named local structures. No universal synthesis of the traditions is claimed.

## 12. Vertical-slice findings

The integrated deterministic and full-duel work supports the following design findings without promoting them to historical claims:

- Cut/Thrust and Cross/Beat have distinct topology despite equal base numbers.
- Hart/Weich is situational; Fühlen is resource-dependent; D/M and Winding remain distinct choices.
- The three-Play cap is a meaningful ceiling in the current slice.
- Maximum 8 Spiritus is useful as a short-duel test baseline.
- Power is meaningful without a Power-only timing exception.
- Repaired Nachreisen is narrow and distinct.
- Zornhau remains distinct but carries local compatibility debt.
- Open remains WATCH because its value is mostly gate/repertoire topology.
- The earlier severe T1/Close blocker is closed by E1/P2.
- The packet-sync S2 blocker is closed by the authoritative S2 runtime repair and 86/86 governing assertions.

## 13. Master governing-status matrix

| Component | Status | Current authority |
|---|---|---|
| One action / normal test / d6+1 | GOVERNING PROVISIONAL | v0.5 synthesis + authoritative engine |
| 8 HP / max 8 Spiritus | PROVISIONAL TEST BASELINE | shared engine and experiments |
| Learned-chain cap 3 | GOVERNING PROVISIONAL | governing data + engine |
| Cut/Thrust topology | GOVERNING PROVISIONAL | current mapping + engine |
| Cross/Beat and D1 | GOVERNING PROVISIONAL | choice architecture + engine |
| Open | GOVERNING PROVISIONAL / WATCH | Beat implementation |
| GC1 | GOVERNING PROVISIONAL | governing data |
| Committed timing | GOVERNING PROVISIONAL | governing data + engine |
| P1 Power | GOVERNING PROVISIONAL | governing data + engine |
| Nachreisen Preparation/Recovery | GOVERNING PROVISIONAL | governing data + engine |
| C2 compounds | GOVERNING PROVISIONAL | governing data + engine |
| S2 | GOVERNING PROVISIONAL, LOCAL EXCEPTION | S2 repair report + engine/tests |
| Ordinary H3-L2 | GOVERNING PROVISIONAL | H3 integration report + engine/tests |
| Ordinary Favored/Unfavored | SUPERSEDED | H3-L2 |
| Zornhau Favored/Unfavored | LOCAL EXCEPTION / COMPATIBILITY DEBT | preserved local engine path |
| Fühlen + D/M | GOVERNING PROVISIONAL | H3 integration |
| Upper/Lower Winding | GOVERNING PROVISIONAL | H3 integration |
| E1 T1 and P2 Pommel | GOVERNING PROVISIONAL | T1/Close integration |
| Eight named guards | GOVERNING PROVISIONAL roster | guard data |
| Guard breaker bonuses | REJECTED as automatic generic modifier | guard audits/current data |
| Generic Close, leverage, force movement | DEFERRED | outside slice |

## 14. Supersession matrix

| Earlier statement/model | Current disposition | Replacement |
|---|---|---|
| v0.4 as current packet | SUPERSEDED as current synthesis; preserved historically | v0.5 |
| Ordinary roll-derived Favored/Unfavored | SUPERSEDED | H3 private Hart/Weich + public bind height/opportunity |
| Random ordinary pressure/contact generation | REJECTED for governing H3 | authored pre-roll pressure and geometry |
| Dormant/raw T1 and zero-cost Pommel fixture | SUPERSEDED | E1 T1 1S and P2 Pommel 2S |
| T1/Close severe blocker | SUPERSEDED finding | closed by T1 governing integration |
| S2 absent from authoritative runtime | SUPERSEDED finding | closed by S2 runtime parity repair |
| Nachreisen 0S flat/incomplete mapping | SUPERSEDED | 1S, +1 chain, Booned Preparation/Recovery |
| Power-only Counter-first description | SUPERSEDED | general Committed target-only pre-roll timing |
| Loaded Cut expected damage 4.394 | SUPERSEDED numerical prose | exact current 3.830555... |
| Candidate H3-L2 recommendation | SUPERSEDED as candidate | promoted by later Project adjudication |

## 15. Open and deferred debt matrix

| Debt | Class | Why it remains |
|---|---|---|
| Schielhau proactive Pflug breaker | OPEN | Source relation is recorded; current payload is unresolved. |
| Basic Ignore valuation | EXPECTED PROVISIONAL DEBT | Real action retention, but policy value remains fragile. |
| Frontale longer sequence | DEFERRED CONTENT | Candidate sequence lacks a complete governing payload. |
| Crown/Scheitel response tree | HISTORICAL ARTIFACT / DEFERRED CONTENT | Evidence and candidate records preserved; no governing promotion. |
| Zornhau local Favored/Unfavored | COMPATIBILITY DEBT | Needed by current Ort/Winden local branch; not ordinary H3. |
| Final Spiritus maximum/economy | OPEN | 8 is a test baseline, not final advancement. |
| Final chain cap | OPEN | 3 governs the slice but broader curriculum testing remains. |
| Generic Close and further consumers | DEFERRED | Only T1/P2 bounded route is in scope. |
| Contact-zone and generic leverage rewards | DEFERRED | State exists where authored; universal modifiers rejected/deferred. |
| Armor, throws, prone, seizure, force movement | DEFERRED | Outside vertical slice. |
| Full guard intrinsic/gate pass | NEXT MILESTONE | Named Guard v0.2 should follow Project review. |

## 16. Historical lesson versus Atra abstraction

| Topic | Historical/source-facing lesson | Atra abstraction |
|---|---|---|
| Nachreisen | Pursue while the opponent's weapon/action is away or recovering | Two target-only Committed windows, 1S, Booned attack |
| Schielhau | Reactive interception/change-through relationship; separate Pflug-breaking lesson | S2 retained/fresh roll comparison and transient window |
| Durchwechseln | Change through beneath attempted weapon engagement | Pre-contact replacement of pending attack, 1S |
| Hart/Weich/Fühlen | Pressure and feeling in blade contact matter | Private authored initial pressure, one 1S reveal |
| Duplieren/Mutieren | Different continuations answer different pressure | Correct-read Booned cut/thrust; wrong-read hard failure |
| Winden | Wind to point-bearing hangings in the bind | Height-gated 2S Upper/Lower thrust states |
| Tutta to stretto | Cover can carry into close work | E1 Wide→Close state transformation, 1S |
| Pommel | Pommel action belongs to close play | 2S flat normal attack from Close opportunity |
| Named guards | Guards organize posture, lines, and technique access | Eight public state bundles plus GC1 |
| Breaker mappings | Sources name relationships between cuts and guards | Recorded access/evidence only; no automatic modifier |

## 17. Chronological decision ledger

1. **2026-08-07 — Packet v0.4:** preserved core melee constitution, Basics, source discipline, guard/repertoire research frame, and unresolved design questions.
2. **2026-08-11 — vertical-slice baseline:** established governing provisional costs, core state vocabulary, D1/C2/P1/Nachreisen/Zornhau compatibility, and test horizon.
3. **2026-08-12 — choice architecture:** selected ordinary Cross Hart/Weich authorship, Beat/Open distinction, GC1, and related response topology.
4. **2026-08-13 — H3 integration:** promoted H3-L2; ordinary Favored/Unfavored superseded; Fühlen, D/M, bind height/opportunity, and Winding integrated.
5. **2026-08-13 — T1/Close integration:** promoted E1 T1 and P2 Pommel; closed the severe Close blocker.
6. **2026-08-13 — integrated full-duel cleanup:** confirmed topology and resource roles, recorded Open WATCH and remaining compatibility debt, corrected Loaded Cut arithmetic.
7. **2026-08-13 — packet sync v0.1:** stopped publication because selected S2 was absent from the authoritative shared runtime.
8. **2026-08-13 — S2 runtime parity repair:** implemented the selected S2 transient state and passed 86/86 governing assertions plus the full suite.
9. **2026-08-13 — packet sync resume v0.2:** reverified closure, repaired stale current-facing Nachreisen and Committed documentation, and published v0.5 without changing mechanics.

## 18. v0.4 to v0.5 changelog

v0.5 preserves v0.4's source discipline, status distinctions, Basic action frame, equal-base Cut/Thrust numbers, ordinary response concepts, eight-point test horizon, and guard/Play separation. It adds the later explicitly adjudicated vertical-slice rules that v0.4 did not contain as current mechanics:

- the effect grammar and public state discipline;
- selected costs and three-Play chain procedure;
- current Cross/Beat/D1/Open/GC1 architecture;
- general Committed timing, P1, and repaired Nachreisen;
- C2 and fully implemented S2;
- H3-L2, private Hart/Weich, Fühlen, D/M, bind height/opportunity, and Upper/Lower Winding;
- E1 T1, bounded Close, and P2 Pommel;
- exact current eight-guard roster and explicit evidence/mechanic boundaries;
- integrated findings, supersessions, compatibility debt, and open/deferred matrices;
- corrected Loaded Cut expected damage.

No v0.4 byte is overwritten. Candidate reports remain evidence and are not silently promoted.

## 19. Review gate and next milestone

The vertical slice is mechanically and documentary-consistent enough for Project review. Publication does not make it final or canonical-complete. After Project review, the recommended next milestone is **Named Guard v0.2**: audit and adjudicate the eight current guard bundles, explicit source gates, breaker relationships, and remaining guard-specific gaps without inventing generic modifiers.

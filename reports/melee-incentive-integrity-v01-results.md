# Atra Melee Incentive Integrity Audit v0.1 Results

Status: **DIAGNOSIS ONLY — no mechanics, prices, guard benefits, transition graph, governing baseline, or design packet changed.**

## Executive Result

Named Guard v0.2 would not presently yield interpretable incentive evidence. Crown C1/B3 has attacker auto-tag and defender reciprocal-motivation failures; repertoire-poor Cross/Beat is a false choice; free guard switching harvests state and access; Alber and Frontale are incentive vacuums; current Nachreisen and Zornhau-Ort behavior is sustained by policy values that exceed their implemented consequences. P1 Power and the C2 compounds retain state-dependent rational uses. Basic Parry is conditionally suppressed at high Skill against known, affordable Durchwechseln but returns with point threat, depletion, or uncertainty.

**Answer: not ready for Named Guard v0.2.** A run now would measure a mixture of real rule incentives, softmax exploration, hand-authored utility constants, incomplete active repertoire, and a free switching harness that rationally harvests benefits. The result would not support clean guard-balance conclusions.

The highest-confidence healthy choices are P1 Power versus ordinary Loaded Cut, C2 compounds versus free Basics, Counter versus avoidance, and Cut versus Thrust. The principal Severity 3 blockers are the Crown candidate's two-sided motivation failure, repertoire-poor Cross/Beat false choice, free guard-state harvesting, active incentive vacuums, and current Nachreisen/Zornhau-Ort policy ghosts.

## Audit Method

The audit began from the dated repository baseline and current implementation. It read the governing register, guard/Play records, named-guard, Guard Play Bridge, Crown, Loaded/Power, Crossing/Bind, Bind Continuations, Durchwechseln, Spiritus, C2, and Play-chain artifacts. Git was clean before work.

Each suspect pair was first reduced to the smallest state where both alternatives are legal. Costs, immediate effects, cleanup, future access, opponent access, and information/resource consequences were compared before consulting frequencies. A deterministic probe imported the current engines and recorded utilities/argmax results. It ran no fights. No broad matrix and no Named Guard v0.2 run occurred.

Controlled artifact: `simulations/incentive_integrity_v0_1/controlled-results.json`. Existing Monte Carlo reports are used only as conditional/supporting evidence; frequency alone never establishes health or failure.

## Current Governing Baseline

Preserved: G1/action-light named guards; universal Basic Cut, Thrust, Cross, and Beat; D1 at 1 Spiritus; C2 Absetzen/Scambiar/Schielhau at 2 Spiritus; S2; explicit Crossing/measure/contact axes; declared Cross/Beat; learned-Play cap 3; Loaded proactive Cut Damage Boon; P1 fixed-7 Power at 1 Spiritus with Committed and Counter-first; free before-or-after guard change as a provisional warned harness; and Tutta T1.

C1/B3 Scheitelhau/Crown remains a **candidate**, not governing. Its engine viability is evidence, not incentive acceptance. The audit does not promote or reject it canonically.

Implementation boundary: `simulations/shared/provisional_longsword.py` stores T1 metadata but selects the Loaded/Power engine; actual T1 behavior lives in the separate Guard Play Bridge subclass. The named-guard harness also does not enforce the guard record's Vom Tag→Nachreisen gate. These are integration facts, not silently resolved rules.

## Decision Node Inventory

The full required fields are split across four keyed tables for readability. Together they are the human-readable form of `decision_nodes` in the JSON artifact.

### Identity, alternatives, and costs

| ID | Actor | State / preconditions | Option A | Option B | Costs A | Costs B |
|---|---|---|---|---|---|---|
| OFF-01 | proactive attacker | action ready; no retained Close consumer chosen | Basic Cut | Basic Thrust | 1 action; 0 Spiritus; miss on committed descending cut creates recovery | 1 action; 0 Spiritus; no committed-miss recovery |
| OFF-02 | attacker in Posta di Donna | Loaded; proactive Basic Cut legal | ordinary Loaded Cut | P1 Power | 1 action; 0 Spiritus; committed-miss recovery; no learned slot | 1 action; 1 Spiritus; Committed; no learned slot; attacker insertions blocked |
| DEF-01 | defender without useful Crossing repertoire | successful incoming attack; action ready; both Basic forms legal | Basic Cross | Basic Beat | 1 action; 0 Spiritus; 0 learned slots; same D1 window | 1 action; 0 Spiritus; 0 learned slots; same D1 window |
| DEF-02 | defender with authored Crossing repertoire | Tutta source-compatible Cut or another implemented Crossing consumer | Basic Cross | Basic Beat | same Basic cost; may expose a paid/repertoire continuation | same Basic cost; ends contact |
| DEF-03 | defender | incoming hit; action ready | Counter | Basic Cross/Beat | 1 action; accepts incoming damage unless Power attacker is killed Counter-first | 1 action; defence roll can cancel; D1 may interrupt |
| DEF-04 | defender | incoming hit; action ready and later action value exists | Ignore | spend action on defence | take damage; preserve action | spend action; risk/avoid damage according to response |
| INS-01 | attacker after Cross/Beat declaration | ordinary Basic Cut; D1 window; point not threatening; at least 1 Spiritus; chain room | Durchwechseln | allow Basic Parry roll | 1 Spiritus; 1 learned slot; new attack roll; spend even on failure | 0 Spiritus; original attack lands only if defence fails |
| DEF-05 | defender against known affordable Durchwechseln | nonthreatening point; high attacker and defender Skill | Basic Cross/Beat | Counter or legal compound defence | action; likely D1 interruption | action; Counter accepts damage; compound costs 2 Spiritus/slot but denies ordinary D1 |
| CMP-01 | Pflug defender against thrust | knows Absetzen; 2 Spiritus; action; chain room | Absetzen | Basic Cross/Beat | 1 action; 2 Spiritus; 1 learned slot | 1 action; no Spiritus/slot; D1 depends on point state |
| CMP-02 | Donna/Tutta defender against thrust | knows Scambiar; source guard; 2 Spiritus; action; chain room | Scambiar di Punta | Basic Cross/Beat | 1 action; 2 Spiritus; 1 learned slot | 1 action; no Spiritus/slot |
| CMP-03 | defender against descending cut | knows Schielhau; 2 Spiritus; chain room | Schielhau S2 | Basic Cross/Beat | 1 action; 2 Spiritus; 1 learned slot; opposed D1 rejoinder possible after success | 1 action; no Spiritus/slot; ordinary D1 depends on point state |
| DEF-06 | defender against committed descending cut | knows Zornhau-Ort; action; chain room | Zornhau-Ort | Basic Cross | 1 action; 1 learned slot; 0 Spiritus | 1 action; 0 slots/Spiritus |
| OFF-03 | attacker against recovering target | target missed a committed descending cut; action ready | Nachreisen | ordinary proactive attack | 1 action; 1 learned slot; 0 Spiritus; fixed normal learned-cut chassis | 1 action; 0 learned slots; normal attack menu including Loaded/P1 where legal |
| CON-01 | Tutta defender after successful source-compatible Cross | Tutta; ordinary Basic Cut; Wide; Crossing; 1 Spiritus; chain room | Tutta Cover to Stretto T1 | remain in successful Wide Crossing | 1 Spiritus; 1 learned slot; no extra action/roll | no Spiritus/slot |
| CON-02 | fighter activating in Close Crossing | action ready; knows Pommel; Close Crossing; chain room | Pommel Strike | ordinary proactive attack | 1 action; 1 learned slot; 0 Spiritus | 1 action; 0 learned slots |
| CRN-01 | candidate attacker versus Alber | B3 candidate known; selected ordinary Basic Cut | tag cut as Scheitelhau entry | leave identical Basic Cut untagged | no action, Spiritus, slot, accuracy, damage, commitment, or information cost encoded | none |
| CRN-02 | Alber defender against candidate entry | candidate tagged Basic Cut hit; action ready | Crown response | generic Basic Cross | 1 action; same defence roll; 0 Spiritus/slots | 1 action; same defence roll; 0 Spiritus/slots |
| CRN-03 | Alber defender against candidate entry | same as CRN-02 | Crown response | Basic Beat or Counter | action; same defence probability as Beat; opens attacker continuation | action; Beat cancels and separates; Counter trades and may kill |
| CRN-04 | attacker after successful Crown | Crown context; 1 Spiritus; chain room | Sink Point Under Crown | decline | 1 Spiritus; 1 learned slot; normal attack roll | none; context cleans |
| GRD-01 | Italian proactive actor | free before-action change available; not currently Donna; proactive Cut desired | change to Donna, then Cut/Power | stay in current guard, then attack | 0 rules cost; consumes this activation's sole guard-change timing; remains Donna through opponent window | no change; foregoes Loaded/P1 |
| GRD-02 | actor after using a guard benefit | no before-action change this activation; after-action change available | switch to threatening-point or Play-gating guard | stay | 0 rules cost; no same-activation action lost | may retain weaker defensive state |
| GRD-03 | German fighter | G1 active; compare point-threatening guards | Pflug | Ochs | no intrinsic rules cost; Absetzen gate if learned | no intrinsic rules cost; upper Winden gate stored but inactive |
| GRD-04 | German fighter | G1; no candidate Crown promotion | Alber | Pflug or Ochs | point not threatening; no active owner access | no cost; threatening point; Pflug may gate Absetzen |
| GRD-05 | German fighter | target recovering; current engine | Vom Tag | Pflug/Ochs | point not threatening; stored Nachreisen gate is not enforced in active code | threatening point; no loss of actual Nachreisen access |
| GRD-06 | Italian fighter | G1; distinctive Frontale learned sequence inactive | Posta Frontale | Mezza Porta di Ferro | nonthreatening point; universal Basic mappings only | no cost; threatening point; same universal Basics remain legal |
| GRD-07 | Italian fighter | knows Scambiar and/or T1 | Tutta Porta di Ferro | Mezza Porta di Ferro | nonthreatening point; exposes D1; grants source gates | threatening point; no active compound gate |
| GRD-08 | Italian fighter | proactive Cut desired or thrust response expected | Posta di Donna | Mezza/Tutta/Frontale | nonthreatening point; opportunity cost of other gates | forego Loaded/P1; Mezza grants point threat; Tutta grants T1/Scambiar |
| GRD-09 | Italian fighter | no immediate Donna/Tutta gate needed | Mezza Porta di Ferro | stay in Frontale or other nonthreatening guard | 0 rules cost; no active downside | D1 exposure |
| GRD-10 | fighter considering no guard change | before or after guard-change opportunity | defer/stay | switch to immediate best state/access | forego free benefit; preserve next phase timing only within same activation | 0 rules cost; consumes one change in current activation |
| OPEN-01 | Ochs/Pflug user in Crossing | Winden gate recorded; full Winden system absent | Winden continuation | no continuation | not specified | none |
| OPEN-02 | bind participant | diagnostic Yield, Rompere close-control, Zwerch-with-Strong or geometry fixture | authored bind continuation | ordinary cleanup | not specified; fixtures only | none |

### Immediate and resulting state

| ID | Immediate A | Immediate B | Resulting state A | Resulting state B |
|---|---|---|---|---|
| OFF-01 | normal d6+1, or Damage Boon if Loaded; cut-specific defence menu | normal d6+1; thrust-specific defence menu | miss may set recovering; ordinary successful resolution follows defence | no recovery liability from the attack chassis |
| OFF-02 | same attack probability; damage 2-7, mean 5.472 | same attack probability; fixed 7 damage | Parry can expose D1; ordinary Counter simultaneous | D1/attacker continuation unavailable; Counter resolves first and can cancel by killing attacker |
| DEF-01 | same cancellation probability; creates Crossing and preserves measure | same cancellation probability; displacement event and separation | unretained Crossing is cleaned to no contact at exchange end | no contact; displacement has no persistent active effect |
| DEF-02 | cancel plus authored continuation access | cancel plus displacement/separation | can become retained Close through T1; otherwise cleans | separated |
| DEF-03 | chance to damage attacker; ordinary attacks trade simultaneously | chance to avoid damage; no damage to attacker | usually no authored contact; both may be wounded | Crossing or separation |
| DEF-04 | attack damage lands | possible cancellation, trade, or compound counter | defender may still activate if alive | defender action unavailable |
| INS-01 | separate, threaten point, roll for normal damage | defender rolls; success cancels and creates Cross/Beat result | no contact; attacker point threatening | Crossing or separation on defence success |
| DEF-05 | may never roll; attacker rerolls into damage | trade or joined defence/attack | Through separation/point threat on declaration | response-specific state |
| CMP-01 | same defence roll plus normal damage to attacker; Crossing; point threatening | cancel only; Crossing or displacement | Wide Crossing unknown pressure; threatening point | form-specific Basic result |
| CMP-02 | same implemented chassis as Absetzen: cancel plus normal counter-damage | cancel only | Wide Crossing; threatening point | Crossing or separation |
| CMP-03 | joined defence/damage if it survives S2 | cancellation only | separated; defender point threatening on success | Crossing or displacement |
| DEF-06 | same defence roll; successful initial phase only creates ordinary Crossing in active explicit combat | same defence roll; creates Hard/Hard Crossing | unknown-pressure Crossing; no natural Soft creator for Ort | Hard/Hard Crossing; cleanup |
| OFF-03 | normal roll and d6+1; no accuracy, defence, tempo, or damage advantage encoded | normal selected attack; may have Loaded damage or Through access | target recovery flag cleared; ordinary defence menu | target recovery may remain; attack-specific state |
| CON-01 | retain Crossing and move Wide to Close | ordinary unretained Crossing cleans at exchange end | retained Close Crossing persists to later activation | no contact; Wide |
| CON-02 | normal roll/damage with no defender response call; separates | normal attack followed by defender response; separates before attack | no contact | response-dependent |
| CRN-01 | identical Basic Cut plus possible Crown context | identical Basic Cut without Sink Point gate | additional future option if defender selects Crown | no candidate continuation |
| CRN-02 | cancel on success; ordinary Crossing plus Crown context | cancel on success; ordinary Hard/Hard Crossing | attacker gains immediate Sink Point option | no Crown context; no Sink Point |
| CRN-03 | cancel plus attacker option | cancel/separate or damage trade | Crown context | no Crown context |
| CRN-04 | chance for normal d6+1 damage; point threatening | no damage/attack | context clears; Crossing later cleans | context and Crossing clean at exchange end |
| GRD-01 | Damage Boon and P1 eligibility | ordinary attack | nonthreatening point during later defence window | current guard state retained |
| GRD-02 | public point threat or future gate becomes active before opponent activation | current state retained | D1 denial in Ochs/Pflug/Mezza or future Absetzen gate in Pflug | guard-dependent |
| GRD-03 | threatening point; lower hanging; active Absetzen access | threatening point; upper hanging; no active unique consumer | D1 denial plus possible thrust compound | D1 denial |
| GRD-04 | no active benefit; D1 exposure | D1 denial | opponent Scheitel candidate relationship only | safer active state |
| GRD-05 | cut-ready tag has no numeric effect | D1 denial | D1 exposure | threatening point |
| GRD-06 | no unique active effect | D1 denial | D1 exposure | threatening point |
| GRD-07 | Scambiar and T1 eligibility in relevant responses | D1 denial | repertoire-specific response access | safer generic state |
| GRD-08 | Loaded Cut/P1; Scambiar gate in data/code | alternative state/access | high offensive upside and D1 exposure | guard-dependent |
| GRD-09 | threatening point | no unique active benefit unless repertoire gate applies | ordinary D1 denied | ordinary D1 open |
| GRD-10 | current guard retained | chosen benefit active immediately | may be suboptimal | optimized for offense or next defence |
| OPEN-01 | not implemented | Crossing cleans unless another authored retention exists | unknown | no contact |
| OPEN-02 | engine can represent Soft, Close, retained displacement, and zones | contact cleans | fixture-specific | none |

### Future and opponent options

| ID | Future A | Future B | Opponent after A | Opponent after B |
|---|---|---|---|---|
| OFF-01 | Durchwechseln is legal after Basic Parry for ordinary Basic Cut; Loaded/P1 comparison exists | avoids cut-specific Schielhau/Zorn response; exposes Absetzen/Scambiar | Cross, Beat, Counter, Ignore; cut responses | Cross, Beat, Counter, Ignore; thrust compounds where gated |
| OFF-02 | reserve and Through/insertion access preserved | reduced future reserve; no insertion from this attack | ordinary response menu | Counter-first plus Cross/Beat/other legal response |
| DEF-01 | none in the current generic repertoire before cleanup | none encoded from displacement | no generic active Crossing consumer; authored contexts are separate | no contact continuation |
| DEF-02 | T1 and downstream Close consumer where owned; Winden remains inactive | denies both sides contact continuations | may also exploit retained Close if capable and activates first | no immediate contact continuation |
| DEF-03 | can end threat by killing attacker; no reserve cost | state continuation depends on form/repertoire | Power may be interrupted if attacker dies | ordinary Cut may Throughchange |
| DEF-04 | preserved proactive action | state/continuation from chosen defence | damage applied; no defensive state created | response-dependent |
| INS-01 | reduced reserve/chain capacity | reserve/chain preserved | no Basic Parry roll after interruption | receives declared defence roll |
| DEF-05 | attacker spends 1 Spiritus if declaring | defender may spend reserve or accept trade | D1 available | D1 absent for Absetzen/Scambiar and constrained under S2 Schielhau |
| CMP-01 | less reserve/chain; denies ordinary D1 | reserve/chain preserved | takes damage on success | Through only if defender point is not threatening |
| CMP-02 | reserve/chain reduced | reserve/chain preserved | takes counter-damage on success | form-dependent |
| CMP-03 | reserve/chain reduced; no generic contact continuation | reserve/chain preserved | S2 Through attempt can contest successful Schielhau | ordinary D1 window where point is not threatening |
| DEF-06 | Ort continuation absent in normal combat | no generic continuation without repertoire | same practical cleanup window | same practical cleanup window |
| OFF-03 | less chain room; no Through from learned cut | chain and stronger options preserved | ordinary response menu | attack-specific response menu |
| CON-01 | Pommel or other Close consumer for either capable side | no Close consumer access | opponent can Pommel if capable and activates first after refresh | no retained contact attack |
| CON-02 | chain reduced | chain preserved | no Cross/Beat/Counter/Ignore in implementation | normal defence menu |
| CRN-01 | Sink Point may become legal | no Sink Point | Crown becomes available in addition to ordinary responses | ordinary responses only |
| CRN-02 | defender gains no exclusive continuation or state benefit | same cleanup without attacker continuation | attacker may spend 1 Spiritus for a new normal attack | no candidate point-sink |
| CRN-03 | attacker Sink Point | no Sink Point | new learned continuation | ordinary options only |
| CRN-04 | reserve/chain reduced | reserve/chain preserved | no additional defence roll is called against Sink Point in candidate implementation | no new attack |
| GRD-01 | can leave on next activation; D1 exposure meanwhile | may retain threatening point or other gate | Through window against Donna Basic Parry | guard-dependent |
| GRD-02 | can change again next activation | preserves current guard access | ordinary D1 denied by threatening point | guard-dependent |
| GRD-03 | Absetzen; inactive lower Winden | inactive upper Winden | Schielhau breaker annotation has no effect | Krumphau breaker annotation has no effect |
| GRD-04 | none active | guard-dependent active access | candidate attacker gains auto-tag opportunity if C1/B3 were used | inert breaker annotations |
| GRD-05 | data record promises Nachreisen identity, but engine allows it from every guard | same actual Nachreisen plus other guard access | Zwerch breaker inert | breaker inert |
| GRD-06 | candidate retreat sequence inactive | candidate beat-return inactive but threat already active | ordinary D1 available | ordinary D1 denied |
| GRD-07 | Close path if trigger and reserve occur | candidate beat-return inactive | D1 against Basic Parry; reciprocal Close if T1 | D1 denied |
| GRD-08 | can switch out freely on later activation | can switch into Donna just before offense | D1 against Basic Parry | guard-dependent |
| GRD-09 | candidate beat-return inactive | guard-specific candidate/gate | reduced Through access | Through access |
| GRD-10 | after-action change remains if no before change | no second change this activation; resets next activation | current state | optimized state |
| OPEN-01 | unknown pressure/zone branches | none | unknown | none from contact |
| OPEN-02 | Ort/Pommel can be force-tested | none | not specified | ordinary next activation |

### Motivation, classification, severity, and evidence

| ID | Rules motive A | Rules motive B | Policy-only motive | Classification | Conditions | Severity | Pre-v0.2 | Smallest next design question | Evidence / metrics |
|---|---|---|---|---|---|---|---|---|---|
| OFF-01 | Loaded damage or Through access; exploit opponent lacking cut responses | avoid recovery and cut-specific responses; exploit opponent lacking thrust compounds | attack menu utilities and softmax affect frequencies but do not create the chassis distinction | HEALTHY | Loaded makes Cut stronger; opponent repertoire and recovery risk preserve Thrust | 0 | NO ACTION REQUIRED | — | simulations/loaded_power_attack_v0_1/simulate.py:340; simulations/loaded_power_attack_v0_1/simulate.py:559 |
| OFF-02 | resource conservation, continuation flexibility, lower wounded-attacker interruption risk | guaranteed maximum normal damage on a hit; lethal certainty against HP 7 or less | softmax sustains P1 in the probe; deterministic heuristic argmax chose Loaded Cut in all 27 tested Skill/Spiritus/attacker-HP cells | HEALTHY; POLICY ARTIFACT | Power rational when fixed damage/kill certainty outweighs reserve and Counter-first risk; Loaded rational otherwise | 0 | NO ACTION REQUIRED | — | reports/loaded-power-attack-v01-results.md; simulations/incentive_integrity_v0_1/controlled-results.json |
| DEF-01 | none without authored Crossing repertoire | source-facing displacement identity, but no current mechanical payoff | identical utilities plus softmax create approximately even observed use | FALSE CHOICE; POLICY ARTIFACT | repertoire-poor, no authored continuation | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | Is repertoire-dependent Cross intentional, or must generic Cross have owner-side value distinct from Beat? | simulations/crossing_bind_state_model_v0_1/simulate.py:295; reports/crossing-bind-state-model-v01-results.md; simulations/incentive_integrity_v0_1/controlled-results.json |
| DEF-02 | access to a useful owner continuation | avoid reciprocal contact risk and conserve Spiritus | T1 adds a hand-authored Close proxy to Cross value | HEALTHY BUT REPERTOIRE-DEPENDENT; POLICY ARTIFACT | healthy only when the owner values the resulting state more than the opponent | 1 | MAY DEFER | — | simulations/guard_play_bridge_v0_1/simulate.py:114; simulations/guard_play_bridge_v0_1/simulate.py:127 |
| DEF-03 | low attacker HP, trade urgency, especially Counter-first versus Power | survival, especially when defender HP is low or attacker healthy | utility coefficients affect frequency, but the damage/cancellation trade is rule-derived | HEALTHY | HP and Power declaration change the preferred response | 0 | NO ACTION REQUIRED | — | simulations/loaded_power_attack_v0_1/simulate.py:438; reports/loaded-power-attack-v01-results.md#commitment-counterplay |
| DEF-04 | survivable damage and valuable pending action | lethal/serious threat or valuable counter-state | current Ignore score is a bare 0.0 and does not value preserved action explicitly | HEALTHY; POLICY ARTIFACT | HP, initiative/order, and pending action value | 1 | MAY DEFER | — | simulations/crossing_bind_state_model_v0_1/simulate.py:278; simulations/crossing_bind_state_model_v0_1/simulate.py:473 |
| INS-01 | high attacker success, high defender Parry chance, urgent damage | low attacker success, low defender Parry chance, low reserve, future value | reserve_charge and softmax set exact rates; structural probability/resource trade is rule-derived | HEALTHY; CONDITIONAL DOMINANCE | at high Skill with reserve, declaration is rational; at S1 most tested pairs decline except 18/18; S0 unavailable | 2 | MAY DEFER | Is near-deletion of nonthreatening Basic Parry at expert Skill an intended tactical deterrent? | reports/spiritus-parry-durchwechseln-results.md; simulations/incentive_integrity_v0_1/controlled-results.json |
| DEF-05 | resource tax/deterrence if attacker may decline or deplete | avoid a highly reliable interruption | older observed collapse is directionally supported but exact percentages are heuristic | CONDITIONAL DOMINANCE | strongest at Skill 18, usable reserve, known repertoire, nonthreatening point; restored by threatening point, S0, uncertainty, or poor attacker odds | 2 | MAY DEFER | Should expert, informed D1 make nonthreatening Basic Parry almost purely a resource-tax bluff? | reports/spiritus-parry-durchwechseln-results.md#executive-result; simulations/named_guard_rules_v0_1/simulate.py:246 |
| CMP-01 | joined defence/offence and urgent counter-damage | reserve/chain conservation | compound one-step utility always exceeds Basics before resource charge | HEALTHY | C2 recedes at S1/0 and competes with future reserve | 0 | NO ACTION REQUIRED | — | reports/compound-spiritus-c1-c2-results.md#opportunity-value-and-utility-classifications; simulations/named_guard_rules_v0_1/simulate.py:190 |
| CMP-02 | joined defence/offence | conservation | Absetzen and Scambiar have identical utilities/outcomes in the engine; their identity comes only from access/source labels | HEALTHY; FALSE CHOICE | healthy versus Basic; mechanically false-chassis relative to Absetzen, though they are not normally co-legal | 1 | MAY DEFER | — | simulations/crossing_bind_state_model_v0_1/simulate.py:337; reports/compound-spiritus-c1-c2-results.md |
| CMP-03 | counter-damage and threatening-point outcome | conservation and avoidance of S2 contest | high policy score makes it argmax at high reserve; exact use is softmax-sensitive | HEALTHY | recedes below 2 Spiritus; urgency/repertoire determine value | 0 | NO ACTION REQUIRED | — | simulations/crossing_bind_state_model_v0_1/simulate.py:432; reports/compound-spiritus-c1-c2-results.md |
| DEF-06 | none in active normal combat beyond source identity | same cancellation without learned-slot cost | Zorn value includes 0.5*p*p*offense despite explicit mode having no natural Soft branch | DOMINATED CHOICE; POLICY ARTIFACT; INSTRUMENTATION AMBIGUITY | active explicit repertoire; no authored Soft pressure | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | Is Zornhau-Ort's active initial phase meant to buy anything before a sourced Soft/Ort continuation exists? | simulations/crossing_bind_state_model_v0_1/simulate.py:312; reports/crossing-bind-state-model-v01-results.md#missing-state-creators |
| OFF-03 | none implemented for the timing lesson | equal or stronger attack without slot cost | fixed 0.52 vs 0.0 makes deterministic policy always select Nachreisen; guard gate is not enforced | DOMINATED CHOICE; POLICY ARTIFACT | especially dominated in Donna where ordinary Loaded/P1 exists; still slot-worse in German Basic chassis | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | What rules consequence makes recovery-window Nachreisen better than an ordinary attack, and is Vom Tag access actually enforced? | simulations/loaded_power_attack_v0_1/simulate.py:543; data/guards/longsword-named-v0.1.yaml |
| CON-01 | owner-only valuable Close repertoire or favorable activation/information state | no consumer, symmetric consumer risk, or reserve conservation | declaration uses 0.25+HP proxy minus reserve, not downstream owner/opponent consequences | HEALTHY BUT REPERTOIRE-DEPENDENT; INCENTIVE VACUUM; POLICY ARTIFACT | healthy with asymmetric owner benefit; vacuum with no consumer; risky with symmetric Pommel | 2 | MUST FIX BEFORE NAMED GUARD v0.2 | Is T1 intentionally worthwhile only with asymmetric owner Close repertoire, despite granting no owner priority? | simulations/guard_play_bridge_v0_1/simulate.py:104; reports/guard-play-bridge-v01-results.md |
| CON-02 | bypasses the defence menu | preserves chain slot or uses Loaded/P1/other attack | fixed 0.42 vs 0.0 governs use and does not calculate the defence denial | HEALTHY BUT REPERTOIRE-DEPENDENT; CONDITIONAL DOMINANCE; POLICY ARTIFACT | Pommel is near-mandatory when chain room exists and ordinary attack has no stronger special package | 2 | MAY DEFER | Is bypassing the entire defence menu the intended owner-side value of Pommel? | simulations/crossing_bind_state_model_v0_1/simulate.py:507; simulations/incentive_integrity_v0_1/controlled-results.json |
| CRN-01 | strict free upside | none | engine automatically tags every qualifying selected Basic Cut; no decision is modeled | FREE UPSIDE / AUTO-TAG; FALSE CHOICE; POLICY ARTIFACT | every qualifying B3 Basic Cut against Alber | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | Should Scheitelhau entry be an actual declaration with a tradeoff, or simply an automatic repertoire trigger? | simulations/scheitelhau_crown_v0_1/simulate.py:101; reports/scheitelhau-crown-v01-results.md#scheitelhau-initial-entry-status |
| CRN-02 | none encoded | same defence without added attacker risk | Crown score 0.77 at Skill 14 beats arbitrary aggregate ordinary-response 0.35 | DOMINATED CHOICE; RECIPROCAL MOTIVATION FAILURE; POLICY ARTIFACT | candidate C1/B3 as implemented | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | What defender-side value, if any, makes Crown rational over generic Cross? | simulations/scheitelhau_crown_v0_1/simulate.py:128; simulations/scheitelhau_crown_v0_1/simulate.py:222 |
| CRN-03 | none encoded | avoid continuation or threaten attacker | Crown bypasses actual alternative-by-alternative scoring | DOMINATED CHOICE; RECIPROCAL MOTIVATION FAILURE; POLICY ARTIFACT | unless a future physical/source constraint makes alternatives illegal, which current code does not | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | Are Beat and Counter genuinely legal against the authored entry, and if so why would Crown be chosen? | simulations/scheitelhau_crown_v0_1/simulate.py:211; simulations/loaded_power_attack_v0_1/simulate.py:493 |
| CRN-04 | urgent damage and favorable success probability | reserve/chain conservation | success proxy minus reserve; exact declaration frequency is heuristic | HEALTHY | once the irrational Crown state is granted, the continuation choice itself is rationally conditional | 0 | NO ACTION REQUIRED IN ISOLATION | — | simulations/scheitelhau_crown_v0_1/simulate.py:166 |
| GRD-01 | immediate Loaded/P1 upside | avoid intervening D1 exposure and retain other access | before-policy gives Donna explicit +0.23/+0.10/+HP coefficients | FREE UPSIDE / AUTO-TAG; CONDITIONAL DOMINANCE; POLICY ARTIFACT | not fully free because switch timing creates one exposure interval; still rational benefit harvesting | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | Does one intervening defence window create enough commitment for free Donna switch-in harvesting? | simulations/named_guard_rules_v0_1/simulate.py:157; reports/named-guard-rules-v01-results.md#guard-churn |
| GRD-02 | free defensive preparation after harvesting prior benefit | only if current guard offers a more valuable expected response | after-policy explicitly rewards threat (+0.16) and Absetzen (+0.05) | FREE UPSIDE / AUTO-TAG; POLICY ARTIFACT | strongest for Donna-to-Mezza/Tutta or German nonthreat-to-Pflug loops | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | Is free post-action defensive staging intended to be the normal rational use of guard changing? | simulations/named_guard_rules_v0_1/simulate.py:151; simulations/incentive_integrity_v0_1/controlled-results.json |
| GRD-03 | strict extra access when Absetzen known | none in current active mechanics | policy gives Pflug Absetzen coefficients | CONDITIONAL DOMINANCE; FALSE CHOICE | Pflug dominates with Absetzen; without it Ochs/Pflug are mechanically equivalent apart from labels/tags | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | Can Ochs be meaningfully evaluated before upper-Winden or another active owner-side identity exists? | data/guards/longsword-named-v0.1.yaml; simulations/named_guard_rules_v0_1/simulate.py:187 |
| GRD-04 | none | free point threat and/or repertoire | softmax and starting-pair forcing create Alber occupancy | DOMINATED CHOICE; INCENTIVE VACUUM; POLICY ARTIFACT | current governing mechanics; C1/B3 remains candidate | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | What learned owner-side reason, if any, makes entering or remaining in Alber rational? | reports/guard-evidence-repertoire-v01-results.md#inert-guard-exit-status; data/guards/longsword-named-v0.1.yaml |
| GRD-05 | none implemented | strict active point-state benefit | softmax/forced starts maintain Vom Tag occupancy | DOMINATED CHOICE; INCENTIVE VACUUM; POLICY ARTIFACT; INSTRUMENTATION AMBIGUITY | until Nachreisen gate and benefit are both actually represented | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | Is Vom Tag supposed to gate a mechanically meaningful Nachreisen in the integrated harness? | simulations/named_guard_rules_v0_1/simulate.py:346; simulations/loaded_power_attack_v0_1/simulate.py:543 |
| GRD-06 | none; source identity only | free point threat | softmax/forced starts create Frontale occupancy | DOMINATED CHOICE; INCENTIVE VACUUM; POLICY ARTIFACT | no learned Frontale repertoire active | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | Is Frontale intentionally transitional/source-facing until its learned sequence exists? | reports/guard-evidence-repertoire-v01-results.md#posta-frontale; data/guards/longsword-named-v0.1.yaml |
| GRD-07 | specific learned response/continuation | generic threat safety | T1 not integrated into named-guard v0.1 engine; current guard policy values only Scambiar-like gate labels sparsely | HEALTHY BUT REPERTOIRE-DEPENDENT; INSTRUMENTATION AMBIGUITY | Tutta is rational only with relevant learned repertoire and trigger expectations | 2 | MUST FIX BEFORE NAMED GUARD v0.2 | Which governing extensions must be integrated so Tutta's repertoire-dependent value is actually measured? | simulations/guard_play_bridge_v0_1/simulate.py; simulations/shared/provisional_longsword.py |
| GRD-08 | offensive damage/Power and Scambiar | point threat or T1 access | Donna occupancy is amplified by explicit guard utility coefficients and incomplete rival repertoire | HEALTHY; CONDITIONAL DOMINANCE; POLICY ARTIFACT | choice is healthy in isolation; free switching distorts commitment and occupancy | 2 | MUST FIX BEFORE NAMED GUARD v0.2 | Can Donna's risk/reward be interpreted while switch-in/switch-out is free? | reports/named-guard-rules-v01-results.md#power-in-named-guards; simulations/named_guard_rules_v0_1/simulate.py:157 |
| GRD-09 | free defensive point state | only repertoire-specific access | after-action policy gives threatening guards +0.16 | FREE UPSIDE / AUTO-TAG; CONDITIONAL DOMINANCE; POLICY ARTIFACT | dominates mapping-only guards when their learned access is irrelevant | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | Is threatening point intended to have no countervailing liability in the current guard harness? | simulations/named_guard_rules_v0_1/simulate.py:148; data/guards/longsword-named-v0.1.yaml |
| GRD-10 | only preserve after-action timing or retain a more valuable gate | benefit harvesting with limited timing friction | 0.09 policy friction is not a rules cost; softmax produces nonoptimal stays | FREE UPSIDE / AUTO-TAG; POLICY ARTIFACT | all-to-all free graph; one change per activation | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | Does the before-or-after timing restriction alone create meaningful commitment? | reports/named-guard-rules-v01-results.md#guard-churn; simulations/named_guard_rules_v0_1/simulate.py:143 |
| OPEN-01 | cannot be evaluated | only implemented option | none; no active decision | INSUFFICIENT BASIS | repertoire coverage gap | 1 | MAY DEFER | — | reports/guard-evidence-repertoire-v01-results.md#evidence-gaps-remaining |
| OPEN-02 | no player-facing cost/outcome procedure exists | only active normal-combat path | not selected by normal AI | INSUFFICIENT BASIS; INCENTIVE VACUUM | harness-only creators are not active repertoire | 1 | MAY DEFER | — | reports/bind-continuations-v01-results.md; simulations/crossing_bind_state_model_v0_1/simulate.py:378 |

## Dominance Framework

Dominance was evaluated across action, Spiritus, learned-slot, guard, contact/measure, probability, damage, cancellation, displacement, retained contact, point threat, continuation access for both sides, revealed information, commitment, action preservation, cleanup, reserve, and repertoire. Lower immediate damage did not count as domination where it bought a distinct valuable state. Conversely, a source-valid label did not count as value when the active rules attached no consequence.

Cross/Beat illustrates the distinction: the source identities differ, but without an authored continuation the active outcomes converge after cleanup. That is a false choice, not a damage comparison. Power/Loaded illustrates the opposite: Power has higher fixed damage but real resource, commitment, continuation, and Counter-first costs, so neither dominates across relevant states.

## Confirmed Healthy Choices

- Basic Cut vs Thrust
- Counter vs Parry
- Ignore vs spend action
- P1 Power vs Loaded Cut
- C2 compounds vs Basics
- Sink Point vs decline once Crown exists

Power/Loaded and C2/Basic are the cleanest healthy cases. Each option has a rules-derived state where it is rational, and the difference survives removal of random exploration. P1 use frequency does not: the current heuristic's deterministic argmax preferred Loaded Cut in all 27 controlled cells, so broad observed P1 use is softmax-supported even though lethal-certainty Power choices remain rational under the rules.

## Cross vs Beat

For a fighter with no useful Crossing repertoire, Cross is not demonstrably preferable in a common active state. Cross and Beat pay the same action, share the same success probability and D1 window, and cancel the same attack. Cross creates an unretained Crossing that is cleaned immediately; Beat records displacement and separation, but displacement has no persistent active payoff. Their post-cleanup vectors converge.

Therefore H3 is not literally proven as strict Beat dominance. The stronger diagnosis is **FALSE CHOICE**. If separation is treated as intrinsically safer outside the implemented consequences, Beat weakly dominates; the engine itself does not value that safety. The policy gives both forms identical utilities, so approximately even frequency is softmax/tie behavior, not evidence of two meaningful choices.

Cross becomes distinct only through useful authored repertoire. T1 can provide that distinction, while full Winden is inactive and generic Cross does not unlock Crown. Even T1 is healthy only when the owner's downstream Close value exceeds the opponent's. This makes Cross currently **HEALTHY BUT REPERTOIRE-DEPENDENT** at best and a Severity 3 blocker for a general guard comparison whose mappings lean on Cross/Beat.

## Durchwechseln vs Basic Parry

The rational defender can nearly abandon nonthreatening Basic Parry when the attacker is known to have D1, has usable reserve, and both Skills are high. The older focused report found post-reveal P1 choice at 0.3% for Skill 18/S8; the deterministic current-policy probe also prefers declaration across most high-skill S8/S3 pairs. This is rules-driven in direction: D1 replaces a likely successful defence with the attacker's high-probability roll for 1 Spiritus.

The choice returns when the defender's threatening point denies D1, attacker Spiritus reaches 0, the attacker is depleted to a valuable last point, attacker Skill is low, defender Skill is low enough that allowing the original Parry failure is attractive, or information is uncertain. At S1 the deterministic probe declined in every tested pair except 18/18. This is **HEALTHY tactical deterrence with a CONDITIONAL DOMINANCE WARNING**, Severity 2—not a universal Basic-Parry defect.

## Power vs Loaded Cut

Ordinary Loaded Cut: same attack probability, 2–7 damage, mean 5.472, no Spiritus, D1/attacker insertion access preserved. P1: same attack probability, fixed 7, 1 Spiritus, Committed, no D1/attacker insertion, Counter-first. Power is rational for fixed maximum and lethal certainty; Loaded Cut is rational for reserve, flexibility, and survival when wounded. **HEALTHY, Severity 0.** No rebalance is indicated by this audit.

## Compounds vs Basics

Absetzen and Scambiar buy joined defence/offence and threatening-point Crossing for 2 Spiritus and one learned slot. Schielhau buys joined defence/offence plus an S2 contest and threatening-point separation. Basics conserve reserve and chain space. The focused C2 report shows compounds recede sharply near S2/S1 and are unavailable below cost; at high reserve their unpriced one-step payload is superior, but reserve competition remains real. This is resource-driven substitution, not strict dominance.

Absetzen and Scambiar are mechanically identical in the current chassis and differ through guard/source access. Because they are not normally co-legal, this is a chassis-compression watch item rather than a player-facing same-node dominance result. **C2 versus Basics is HEALTHY, Severity 0.**

## Reciprocal-Sequence Table

| Sequence | Step | Acting side | Available alternatives | Why actor chooses historical option | Why opponent chooses historical response | Source / mechanical constraint | Rules-derived? | Collapses? | Severity |
|---|---|---|---|---|---|---|---|---|---|
| Scheitelhau -> Crown -> Sink Point candidate | 1 | attacker | same Basic Cut untagged; Basic Thrust; other attack | tag is costless and only adds an option | not applicable yet | entry only against Alber; candidate B3 | True | True | 3 |
| Scheitelhau -> Crown -> Sink Point candidate | 2 | defender | Basic Cross, Basic Beat, Counter, Ignore, other legal defence | no defender-side rules benefit is encoded | attacker wants Crown because it unlocks Sink Point | Crown is source-specific and not generic Cross | False | True | 3 |
| Scheitelhau -> Crown -> Sink Point candidate | 3 | attacker | spend 1 Spiritus for Sink Point; decline | normal extra attack is valuable when damage urgency exceeds reserve/slot value | defender had no rational reason to create this state | 1 Spiritus, normal roll/damage, one learned slot | True | True | 3 |
| Tutta Cross -> Cover to Stretto | 1 | defender | Beat, Counter, compound defence, Ignore | Cross is rational only if downstream owner Close value exceeds separation | attacker uses ordinary Cut for Loaded/Through/cut incentives, not to cooperate | Tutta, ordinary Basic Cut, Wide, successful Cross | True | False | 2 |
| Tutta Cross -> Cover to Stretto | 2 | defender | spend 1 Spiritus to retain Close; remain Wide and clean | owner-only Close repertoire or favorable information/order | opponent does not choose; but may exploit Close first | T1 governing provisional; no owner priority | True | False | 2 |
| Durchwechseln interaction | 1 | defender | Cross/Beat, Counter, compound, Ignore | Basic Parry taxes reserve or is restored by point threat/depletion/uncertainty | attacker selected ordinary Cut for its own incentives | D1 only from eligible nonthreatening state | True | False | 2 |
| Durchwechseln interaction | 2 | attacker | declare D1; allow Parry | high own success and high defender Parry chance | defender may be bluffing reserve or lack alternatives | pre-roll, 1 Spiritus, no refund | True | False | 2 |
| Power -> defender response | 1 | attacker | ordinary Loaded Cut | fixed-7 lethal certainty or damage urgency | not applicable yet | P1; Committed; Counter-first | True | False | 0 |
| Power -> defender response | 2 | defender | Counter, Cross, Beat, legal compound, Ignore | Counter-first is rational against wounded attacker; Parry is rational for survival; compounds trade reserve for counter-damage | Power attacker accepted menu shift for fixed damage | Through/attacker insertions blocked | True | False | 0 |
| Zornhau-Ort bind sequence | 1 | defender | Basic Cross | no implemented benefit; only policy ghost value | opponent need not yield Soft; no natural Soft creator | Ort requires opponent Soft | False | True | 3 |
| Zornhau-Ort bind sequence | 2 | bind opponent/actor | diagnostic Yield or ordinary state | Yield has no player-facing motive/cost procedure | Ort actor benefits if Soft appears | Yield is diagnostic only | False | True | 3 |

## Guard Motivation

| Guard | Unique intrinsic state | Basic mappings | Active learned access | Vulnerabilities / breakers | Reason to enter | Reason to stay | Reason to leave | Switch-in harvesting | Switch-out harvesting | Repertoire dependence | Vacuum? | Severity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Vom Tag | high, chambered/cut-ready, point not threatening; tags have no active numeric effect | universal Basics; ordinary cut identity only | Nachreisen listed but not actually guard-gated; Nachreisen chassis has no benefit | D1 exposure; Zwerch annotation inert | none in active rules | none except source identity | gain point threat/Pflug access | low owner benefit | high; leave after any desired labeled use | intended Nachreisen | YES | 3 |
| Ochs | high upper hanging; threatening point | universal Basics | upper Winden stored, inactive | Krumphau annotation inert | deny ordinary D1 | maintain point threat | Pflug supplies same threat plus active Absetzen | high after-action defensive staging | high; no transition cost | would depend on Winden | NO, but conditionally dominated | 3 |
| Pflug | low lower hanging; threatening point | universal Basics | Absetzen; lower Winden inactive | Schielhau breaker annotation inert | deny D1 and gate Absetzen | defensive threat/access | only for another immediate benefit | high after action before expected defence | high | Absetzen | NO; FREE UPSIDE staging point when no other gate needed | 3 |
| Alber | low, point on ground/not threatening | universal Basics | none | D1 exposure; Scheitel relationship inert; candidate auto-tag harms defender | none | none | any threatening guard is safer | none | automatic rational exit | candidate Crown unresolved | YES | 3 |
| Posta di Donna | high, chambered, Loaded, point not threatening | Basic Cut | Scambiar gate; Donna-left candidate inactive | D1 exposure | Loaded Cut/P1 and Scambiar | repeat offensive benefit or await thrust | gain point threat after offense | VERY HIGH before proactive Cut | VERY HIGH after harvesting, limited by one-change timing | partly; Loaded/P1 intrinsic, Scambiar learned | NO | 2 |
| Posta Frontale | high, front-centered/cross-ready, point not threatening | high thrust -> Cross; low thrust -> Beat, both universal | retreat-fendente-thrust candidate inactive | D1 exposure | none mechanically unique | none | Mezza threat or Donna/Tutta gates | none | automatic rational exit | future learned sequence | YES | 3 |
| Tutta Porta di Ferro | low, grounded/waiting, point not threatening | Cross/Beat, both universal | Scambiar; governing T1 only in separate bridge extension | D1 exposure; reciprocal Close risk | expect thrust compound or source-compatible Cut/T1 | retain access to those learned responses | Mezza point threat or Donna offense | medium; must preposition before opponent attack | high after opportunity passes | HIGH | YES without Scambiar/T1/Close consumer | 2 |
| Mezza Porta di Ferro | low, thrust-ready, threatening point | Thrust/Beat, both universal | beat-return candidate inactive | none active | deny ordinary D1 | free point threat | Donna offense or Tutta/Scambiar/T1 gate | VERY HIGH after action | high | no for threat; future candidate for fuller identity | NO; FREE UPSIDE state when other gates irrelevant | 3 |

This table does not balance guards against one another. It asks whether each guard currently has any owner-side reason to exist. Alber and Frontale do not. Vom Tag's intended Nachreisen identity is not realized by the active gate or chassis. Ochs has point threat but is conditionally dominated by Pflug when Absetzen is known. Tutta is legitimate repertoire-dependent access. Donna has a real offensive identity, while Mezza/Pflug can be harvested as free defensive staging states.

## Guard-Change Benefit Harvesting

The harness permits one free change either before or after an activation and resets permission next activation. That produces three rational patterns: enter Donna before a proactive Cut; change after acting into Pflug/Ochs/Mezza so point threat is active during the opponent's turn; and preposition into Pflug or Tutta to make a learned response legal. An actor already in Donna can use Loaded/P1 and then leave after the action.

The timing restriction creates some friction: switching into Donna before attacking prevents an immediate same-activation exit and leaves one defence interval of D1 exposure. It does not impose an action/resource cost, and an after-action switch acquires defensive state after the actor's useful action has resolved. The policy's 0.09 change friction is not a rule. Existing churn is therefore both a real incentive symptom and a policy-shaped quantity. **Severity 3.**

## Tutta Cover to Stretto

T1's unique purchase is retained Close Crossing. It is rational when the owner possesses a useful Close consumer the opponent lacks or when information/order makes owner exploitation more valuable. With no Close consumer, spending 1 Spiritus and a slot buys no owner payoff. With symmetric Pommel, either fighter may exploit Close after action refresh and there is no owner priority, creating reciprocal risk.

The current policy does not evaluate this. It assigns a Close-state proxy (0.25 plus opponent-HP term minus reserve) and chooses against zero. Thus T1 is **HEALTHY BUT REPERTOIRE-DEPENDENT**, with an incentive vacuum in no-consumer states and a Severity 2 integration/motivation question before v0.2. Its price and trigger are not reopened here.

## Frontale and Mapping-Only Guards

Frontale's high-thrust Cross and low-thrust Beat are source-identity mappings to universal Basics. They provide no reason to enter Frontale because every guard can use those Basics and no modifier follows. The distinctive retreat/cut/thrust sequence is inactive. Frontale is therefore an **INCENTIVE VACUUM** and conditionally dominated by Mezza's free threatening point in current active mechanics. It can remain a source-facing/transitional record, but a v0.2 balance run cannot interpret it as a populated guard.

The same test applies to other mappings: Mezza's Thrust/Beat mappings are universal, but its threatening point is active; Tutta's Cross/Beat mappings are universal, but Scambiar/T1 can create repertoire value; Donna's Cut mapping is universal, but Loaded/P1 is active. Source identity is preserved without pretending it is mechanical motivation.

## Scheitelhau / Crown Reciprocal Motivation

The candidate fails incentive viability despite passing engine viability. First, every qualifying B3 Basic Cut is automatically tagged. The tag changes no cost, roll, damage, commitment, information, or slot and only adds a future option. That is **FREE UPSIDE / AUTO-TAG**.

Second, Crown uses the same defence probability/cancellation role as generic Cross but creates a transient context whose only active payoff belongs to the attacker. Generic Cross avoids that risk; Beat also cancels and separates; Counter offers a damage trade. No defender benefit or physical constraint makes Crown rational. The simulator chooses Crown because it scores `1.10 × defence probability` against an arbitrary aggregate 0.35, not because of consequences. This is **DOMINATED CHOICE + RECIPROCAL MOTIVATION FAILURE + POLICY ARTIFACT**, Severity 3.

Once Crown is granted, Sink Point versus decline is healthy: 1 Spiritus and one slot buy a normal attack chance, while declining conserves reserve. That local health does not rescue the sequence because rational defence prevents the state from arising. C1/B3 is neither promoted nor rejected canonically; it is unsuitable as v0.2 input until its smallest motivation questions are adjudicated.

## Policy vs Rules

Rules-derived value includes actual damage, cancellation, reserve, action, chain, contact, point threat, continuation access, and opponent access. A positive score, random exploration, or even deterministic selection from a hand-authored constant is not rules evidence. The current policy is useful for exercising branches, not for proving rational choice.

### Would This Choice Exist Without Softmax?

| Choice | Deterministic argmax | Would it exist? | Classification |
|---|---|---|---|
| Cross vs Beat mixing | tie | both only because utilities are identical; rules do not distinguish final state without repertoire | FALSE CHOICE / POLICY ARTIFACT |
| Nachreisen | always Nachreisen from fixed 0.52 vs 0.0 | yes in AI, but only due constant; rules provide no advantage | POLICY ARTIFACT |
| Crown | Crown at Skill 14 from 0.77 vs 0.35 | yes in AI, but only due constants and aggregate comparison | POLICY ARTIFACT |
| T1 | declare at Skill14/S8 from 0.108 vs 0 | yes in AI due Close proxy, regardless of downstream ownership | POLICY ARTIFACT |
| Zornhau-Ort | often beats Cross due unrealizable Ort term | rules-rational choice generally no in explicit normal combat | POLICY ARTIFACT |
| P1 Power | Loaded Cut in all 27 controlled heuristic cells | yes for rational lethal-certainty states, but observed broad frequency is softmax-supported | POLICY ARTIFACT but rules choice HEALTHY |
| guard switching | Donna before offense; point threat/Pflug after action | yes because rules offer free state/access; exact churn is coefficient/softmax-dependent | RULE-BASED HARVESTING + POLICY ARTIFACT |
| Pommel | Pommel from fixed 0.42 vs 0 | yes rules-rationally because implementation bypasses defence, but frequency is constant-driven | POLICY ARTIFACT |

## Instrumentation Findings

- The choices counter records a specific Basic Cross/Beat in defend and then records generic Basic Parry again inside basic_parry; summing choices is invalid.
- Crown's dedicated opportunities/declarations/creations and B3 entry declarations are usable; generic plays aggregates do not represent B3 entry declarations and should not be read as such.
- Crown ordinary alternatives are not individually instrumented at the Crown decision; an aggregate constant controls branch entry.
- The governing baseline records T1, but simulations/shared/provisional_longsword.py selects the Loaded/Power engine and only stores T1 metadata. T1 behavior exists in the separate Guard Play Bridge subclass, not the named-guard engine.
- Guard records list Nachreisen access from Vom Tag, but NamedGuardDuel does not enforce that gate. Reported Nachreisen frequency therefore cannot evidence Vom Tag motivation.
- Opportunity/use/success/Spiritus/chain/contact metrics are otherwise sufficiently separated for D1, C2, T1, Crown, and guard occupancy when their dedicated fields are used.

No reporting code was changed. Dedicated metrics are sufficient for this audit when their semantics are kept separate; changing historical outputs was unnecessary.

## Required Output Groups

### A. Confirmed Healthy

- Basic Cut vs Thrust
- Counter vs Parry
- Ignore vs spend action
- P1 Power vs Loaded Cut
- C2 compounds vs Basics
- Sink Point vs decline once Crown exists

### B. Healthy but Repertoire-Dependent

- Cross with an owner-valued authored continuation
- Tutta T1 with asymmetric useful Close repertoire
- Pommel from Close
- Tutta guard with Scambiar/T1

### C. Watch Items

- Ignore policy does not value saved action
- Scambiar and Absetzen share one chassis
- Pommel conditional mandatory use
- D1 expert deterrence

### D. Material Incentive Defects

- T1 has no owner priority and no value without consumer
- threatening-point guards have no active intrinsic liability
- governing extensions are not integrated in one harness

### E. Blockers Before Named Guard v0.2

- Scheitelhau auto-tag
- Crown reciprocal failure
- Cross/Beat false choice
- free guard harvesting
- Alber/Frontale vacuums
- Ochs/Pflug conditional dominance
- Nachreisen missing benefit/gate
- Zornhau-Ort ghost value

### F. Policy / Instrumentation Artifacts

- softmax Cross/Beat mixing
- fixed Nachreisen/Crown/T1/Pommel values
- ghost Zorn continuation utility
- P1 softmax use despite heuristic argmax
- double-counted choices
- distributed T1 integration
- unenforced Vom Tag gate

### G. Open — Insufficient Current Mechanics

- Winden
- full bind pressure decisions
- Rompere player-facing continuation
- Yield
- active breaker mechanics
- Frontale retreat sequence
- Mezza beat-return

## Severity Register

| Issue | Classification | Severity | Pre-v0.2 | Smallest next design question |
|---|---|---|---|---|
| Scheitelhau B3 auto-tag | FREE UPSIDE / AUTO-TAG | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | Is the entry an actual tradeoff-bearing declaration or an automatic repertoire trigger? |
| Crown defender response | DOMINATED CHOICE; RECIPROCAL MOTIVATION FAILURE | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | What defender-side value makes Crown rational over Cross/Beat/Counter? |
| Cross vs Beat without repertoire | FALSE CHOICE; POLICY ARTIFACT | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | Is repertoire-dependent Cross intentional? |
| Free guard-change harvesting | FREE UPSIDE / AUTO-TAG; POLICY ARTIFACT | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | Does timing alone create sufficient commitment? |
| Alber and Frontale | INCENTIVE VACUUM; DOMINATED CHOICE | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | Must each have active learned owner-side repertoire before balance testing? |
| Ochs/Pflug and Mezza/mapping-only comparisons | CONDITIONAL DOMINANCE | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | Can guards lacking active consumers be interpreted against free threatening-point guards? |
| Nachreisen current chassis/gate | DOMINATED CHOICE; POLICY ARTIFACT | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | What is its implemented recovery-window advantage, and is its guard gate enforced? |
| Zornhau-Ort ghost continuation value | DOMINATED CHOICE; POLICY ARTIFACT | 3 | MUST FIX BEFORE NAMED GUARD v0.2 | What does the initial Zorn phase buy before Soft exists? |
| Tutta T1 symmetric/no-consumer states | HEALTHY BUT REPERTOIRE-DEPENDENT; INCENTIVE VACUUM | 2 | MUST FIX BEFORE NAMED GUARD v0.2 | Is asymmetric repertoire dependence without owner priority intentional? |
| Expert known/affordable D1 suppresses Basic Parry | CONDITIONAL DOMINANCE | 2 | MAY DEFER | Is Basic Parry intended mainly as a reserve tax at expert Skill? |
| Pommel bypasses defence menu | CONDITIONAL DOMINANCE; POLICY ARTIFACT | 2 | MAY DEFER | Is defence denial its intended payoff? |
| P1 Power vs Loaded Cut | HEALTHY | 0 | NO ACTION REQUIRED | — |
| C2 compounds vs Basics | HEALTHY resource-driven substitution | 0 | NO ACTION REQUIRED | — |

## Blockers Before Named Guard v0.2

- Scheitelhau B3 auto-tag
- Crown defender response
- Cross vs Beat without repertoire
- Free guard-change harvesting
- Alber and Frontale
- Ochs/Pflug and Mezza/mapping-only comparisons
- Nachreisen current chassis/gate
- Zornhau-Ort ghost continuation value

These are blockers to interpreting the experiment, not automatic instructions to repair mechanics. No transition graph, bonuses, price changes, new Plays, or baseline promotions follow from this audit.

## Smallest Next Design Questions

- Is repertoire-dependent Cross intentional?
- What makes Crown rational for the defender, and is Scheitelhau entry automatic or tradeoff-bearing?
- Does free before-or-after switching create acceptable commitment, or must v0.2 wait for a different approved switching rule?
- Must Alber, Frontale, Ochs, and Vom Tag have active owner-side repertoire before comparison?
- What implemented benefit and guard gate define Nachreisen, and what active benefit defines Zornhau-Ort before Soft exists?
- Is T1 intentionally valuable only with asymmetric owner Close repertoire despite no owner priority?

## Ready for Named Guard v0.2?

**A. Which choices are demonstrably healthy?**

Basic Cut/Thrust, Counter/Parry, Ignore/action preservation, P1/Loaded, C2/Basic reserve substitution, and Sink/decline after a valid Crown state.

**B. Which are healthy only with learned repertoire?**

Generic Cross, T1, Tutta, Pommel, and future Winden identities.

**C. Which are strictly dominated?**

Crown versus generic Cross/Beat in the candidate; Alber/Frontale versus free point-threat guards in current active mechanics; current Nachreisen and Zornhau-Ort versus their nearest Basic chassis.

**D. Which are conditionally dominated?**

Basic Parry at expert known/affordable D1; Ochs by Pflug with Absetzen; mapping-only guards by Mezza when their gates are irrelevant; ordinary attack by Pommel in eligible Close states.

**E. Which are free-upside / automatic?**

Scheitelhau B3 tagging; before/after guard staging; threatening-point staging when no other gate matters.

**F. Which sequences have reciprocal failure?**

Scheitelhau/Crown/Sink; current Zornhau-Ort Soft sequence. T1 has reciprocal-risk tension but does not always collapse.

**G. Which guards have incentive vacuums?**

Alber, Frontale, and current active Vom Tag; Tutta without repertoire. Ochs lacks a fuller active identity but point threat prevents total vacuum.

**H. Is Cross rational without repertoire?**

No distinct rational mechanical reason over Beat in common active states; it is a false choice rather than proven strict Beat dominance.

**I. Does D1 materially delete high-skill Basic Parry?**

Materially yes at high Skill, known repertoire, usable reserve, and nonthreatening point; not at low reserve, with threatening point, or under enough uncertainty/poor odds.

**J. Is free switching producing rational harvesting?**

Yes. The behavior is rules-rational; exact churn rates are policy-dependent.

**K. Which choices are policy artifacts?**

Cross/Beat frequency, Nachreisen, Crown, T1, Zornhau-Ort, Pommel, guard occupancy, and broad P1 use.

**L. Which issues are Severity 3?**

Crown/entry, Cross/Beat, free switching, Alber/Frontale, point-threat staging comparisons, Nachreisen, and Zornhau-Ort.

**M. Which Severity 2 issues may wait?**

expert D1 suppression and Pommel defence denial may wait if explicitly excluded from the v0.2 interpretation; T1 integration/motivation may not.

**N. Can a run now be interpreted?**

No. Results would confound missing rules motivation with softmax constants, incomplete repertoire, and free benefit harvesting.

**O. Minimum questions first?**

- Is repertoire-dependent Cross intentional?
- What makes Crown rational for the defender, and is Scheitelhau entry automatic or tradeoff-bearing?
- Does free before-or-after switching create acceptable commitment, or must v0.2 wait for a different approved switching rule?
- Must Alber, Frontale, Ochs, and Vom Tag have active owner-side repertoire before comparison?
- What implemented benefit and guard gate define Nachreisen, and what active benefit defines Zornhau-Ort before Soft exists?
- Is T1 intentionally valuable only with asymmetric owner Close repertoire despite no owner priority?

## Validation and Change Boundary

The deterministic probe completed successfully. Repository validation and tests are reported in the task handoff. No existing combat mechanic, baseline record, Play record, guard record, historical report, or design packet was modified. The only executable addition is the scoped diagnosis-only probe and renderer.

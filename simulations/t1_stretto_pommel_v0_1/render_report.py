"""Render the project-review Markdown report from the machine-readable result."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "reports" / "t1-stretto-pommel-integration-v01-results.json"
REPORT = ROOT / "reports" / "t1-stretto-pommel-integration-v01-results.md"


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def num(value: float) -> str:
    return f"{value:.3f}"


def table(headers: list[str], rows: list[list[object]]) -> list[str]:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    return out


def main() -> None:
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    lines: list[str] = [
        "# T1 → Stretto → Pommel Integration v0.1 Results",
        "",
        "Status: **BOUNDED CANDIDATE TIMING / CLOSE-REPERTOIRE EXPERIMENT; NO GOVERNING OR CANONICAL PROMOTION. STOP FOR PROJECT ADJUDICATION.**",
        "",
        "## Executive Result",
        "",
        "**E1 Early T1 plus P2 (2S) Pommel is mechanically coherent and produced no severe failure in the bounded exact or fixed-seed matrices.** E1 resolves the integration hole by inserting T1 after the successful qualifying Tutta Cross and D1 timing but before any ordinary H3 Rejoinder use. It changes the state to Close rather than cancelling D/M. Hart assigns the striker first Close opportunity; Weich assigns the Tutta defender. Pommel is a separate generic Close consumer with no intrinsic response denial.",
        "",
        "T1 is **REPERTOIRE-DEPENDENT; NARROW BUT DISTINCT**. It can deny the Wide information game, change repertoire topology, and enable Close work, but costs 1S/+1 chain, exposes Hart to striker-first Close repertoire, and does not guarantee its owner an attack. Beat remains the zero-cost separation/Open option. P1 Pommel is an incentive problem at low reserves because it supplies the same flat action-compressed attack for 1S; P2 is the healthier Project candidate. This report recommends Project review of E1+P2, not automatic promotion.",
        "",
        "## Source-of-Truth Check",
        "",
        "The audit inspected the current governing register and H3 YAML, shared engine, integrated audit and JSON, Upper/Lower Winden completion report, Crossing/Bind and Bind Continuations, mechanical vocabulary, incentive audit, current Tutta guard record, Pommel record, prior Pommel harnesses, source policy, Spiritus/chain rules, and relevant tests. The pre-edit worktree was clean on `main` at `010fa1bbea8a5a4146693fd03aff829c73cd5678`.",
        "",
        "The repository evidence agrees with the supplied Project boundary. No exact historical record says that T1 cancels an H3 Rejoinder, guarantees owner-first work, is intrinsically chained to Pommel, or makes Pommel universally undefendable.",
        "",
        "## Pre-Experiment Baseline",
        "",
        "- H3 governing required matrix: **129/129 PASS**.",
        "- Integrated full-duel deterministic suite: **11/11 tests PASS**.",
        "- Full unittest discovery before edits: **153 tests PASS**.",
        "- Repository validator: **114 Play records; 0 errors; 39 preserved warnings**.",
        "- Melee grammar validator: **0 errors; 16 pre-existing informative findings**.",
        "- Dead-actor gates, Loaded Cut damage-mode integration, and executable D1 replacement resolution remain covered and passing.",
        "",
        "## Prior Audit Blocker",
        "",
        "C0 allows raw T1 legality while the H3 attacker Rejoinder remains open. T1 changes Wide→Close, which removes D/M from `rejoinder_options`, but leaves the Rejoinder itself alive and supplies no order or consumer. D13 therefore recorded 2,589 owner-qualified opportunities and zero declarations. C0 is retained only as a broken control.",
        "",
        "## Artifact / Instrumentation Sanity",
        "",
        f"Skill-14 Loaded Cut exact declaration damage is **{data['artifact_sanity']['loaded_cut']['recomputed_exact']:.12f}**, matching the JSON value 3.830555… . The prose value 4.394 is wrong. This is a **report-only discrepancy**: flat 70% hit × exact mean of keep-highest-2d6+1 (5.472222…) = 3.830555…. The historical report was not silently rewritten; this and future reporting use the exact value.",
        "",
        f"`point_threat_events=0` was an **instrumentation bug**, not a state bug. The old integrated metrics dictionary initializes the field but has no increment site. Winding correctly sets threatening point. The candidate audit counts authored event-log transitions; its forced positive probe records {data['artifact_sanity']['point_threat_events']['positive_probe_count']} event and state `{data['artifact_sanity']['point_threat_events']['positive_probe_state']}`. Historical JSON remains unchanged.",
        "",
        "## Historical Boundary — Tutta",
        "",
        "Source-supported: Fiore’s Tutta Porta di Ferro covers blows, may cover with a pass, and enters stretto/narrow play (Getty MS Ludwig XV 13, 23v-a; Morgan M.383, 12r-a; Pisani Dossi 18a-a). The current record explicitly classifies “cover with a pass and enter stretto” as a learned Play.",
        "",
        "Atra bounded trigger: ordinary proactive Basic Cut, successful source-compatible Basic Cross, Tutta defender, Wide Crossing, 1S, and chain room. Atra candidate inferences: E1 insertion before H3 use, clearing height, and pressure-based Close opportunity. These are not presented as Fiore’s discussion of H3 priority.",
        "",
        "## Historical Boundary — Narrow Play / Pommel",
        "",
        "The exact Pommel record supports an established close crossing, arm/elbow access in the relevant variants, and striking the exposed face with the pommel (Getty 28r-c/d; Morgan 16r-c/d; Pisani Dossi 22a-c/d). It supports neither T1-specificity nor universal response denial. Price, no-action continuation, flat Longsword roll, normal damage placeholder, miss retention/transfer, and hit cleanup are Atra candidates.",
        "",
        "## Current T1",
        "",
        "The preserved chassis costs 1S/+1 learned entry, consumes no extra action or roll, retains the Crossing, and changes Wide→Close with no damage, threat, control, Leverage, or automatic strike. The overlay narrows the actual runtime trigger to the already-documented Tutta/ordinary-Basic-Cut/successful-Cross case and changes only candidate timing and height cleanup.",
        "",
        "## Current / Prior Pommel Candidate",
        "",
        "The oldest v0.1/v0.2 Pommel harness used initiation timing from Close Crossing, required an action-ready actor, cost 0S, rolled Longsword flat, used normal d6+1 placeholder damage, and ended contact on hit or miss. It had no response-processing branch, so its practical blanket bypass was an implementation consequence rather than item-level source support.",
        "",
        "Classification: Close trigger and Longsword identity are source-supported/plausible; flat roll and normal damage are Atra placeholders; action-ready initiation and always-separate aftermath are superseded by current continuation architecture; implicit blanket response bypass is unsupported/exceptional and not carried forward.",
        "",
        "## C0 Broken Ordering",
        "",
    ]
    lines += table(
        ["Property", "Current C0", "E1 Early", "L1 Late"],
        [[row["property"], row["C0"], row["E1"], row["L1"]] for row in data["timing_comparison"]],
    )
    lines += [
        "",
        "## E1 Early Cover-Integrated T1",
        "",
        "E1 is offered only after D1 timing and a successful qualifying Cross. While the window is live, the striker has no Rejoinder or Fühlen option and cannot observe the private pressure. Declaration spends 1S/+1 chain, retains contact, sets Close/Unknown, assigns the opportunity from pressure, clears pressure, and closes the unused Wide-gated Rejoinder. Declining E1 exposes the inherited governing H3 methods unchanged.",
        "",
        "E1 best fits the source shape because the pass/entry remains part of the cover. It is H3-compatible as a state transformation before Rejoinder use, although it intentionally denies that branch when chosen. Its incentive cost and reciprocal priority keep that denial from being free.",
        "",
        "## L1 Late T1 Control",
        "",
        "L1 is coherent but weaker and less source-shaped. The attacker receives the complete H3 Rejoinder first. T1 is then legal only if the Tutta defender later becomes current ordinary opportunity holder—immediately after Weich decline, or after a Hart striker passes. A resolved D/M ends the bind, so no late T1 follows it.",
        "",
        "## T1 Height Transition",
        "",
        "E1/L1 set `bind_height=unknown`. The Wide Upper/Lower tag is not carried into transformed Close geometry. Deterministic tests prove that neither Upper nor Lower Winding remains legal, no Lower is synthesized, and no random Close height is created.",
        "",
        "## Close Opportunity Semantics",
        "",
        "The candidate reuses `bind_initiative` as current opportunity; it creates no Close Initiative statistic. Hart→striker and Weich→parrier apply only to the first Close declaration opportunity. One pass transfers; a second consecutive pass cleans the Crossing; a real continuation resets the pass count; Disengage uses the governing cleanup.",
        "",
        "## Pommel Strike v0.2",
        "",
        "Pommel requires learned Pommel, Crossing, Close, current opportunity, chain room, and the tested Spiritus. It does not inspect guard, T1, last Play, pressure, height, or action readiness. Declaration uses ATTACK with a flat Longsword test and normal d6+1 placeholder damage, no Boons, Open, Leverage, control, or new operator.",
        "",
        "## Pommel Response Model",
        "",
        "The record and overlay contain no response restriction. In the E1/L1 sequence, the original Cut and Cross have spent both normal Actions, so ordinary action-funded defences are unavailable as a timing consequence. Pommel does not mutate the target’s action or encode `RESTRICT_RESPONSE`. Future authored Close counters remain possible.",
        "",
        "## Pommel P1 1S",
        "",
        "P1 is usable at a 1S reserve where D/M and Winden are unavailable. Because it delivers the same flat normal attack as P2 for half the resource and has no weaker payload, it becomes the natural legal Close spend too often. The narrow gate prevents universal dominance, but P1 is the experiment’s one real incentive problem.",
        "",
        "## Pommel P2 2S",
        "",
        "P2 matches the current action-compressed full-attack benchmark. Its Close/opportunity gate is narrower than Winden, while Winden supplies authored guard/threat aftermath and D/M supplies Booned accuracy after information. P2 remains useful but does not crowd those branches in shared states.",
        "",
    ]
    cost_rows = []
    for row in data["pommel_cost"]:
        kp = row["kill_probability"]
        cost_rows.append([row["skill"], row["cost"], pct(row["hit"]), num(row["expected_damage"]), num(row["damage_per_spiritus"]), pct(kp["1"]), pct(kp["4"]), pct(kp["6"]), pct(kp["8"])])
    lines += table(["Skill", "Cost", "Hit", "E damage", "Damage/S", "P kill HP1", "HP4", "HP6", "HP8"], cost_rows)
    lines += ["", "Contextual reserve consequences:", ""]
    lines += table(["Reserve", "Max P1 declarations", "Max P2 declarations", "Defender reserve after T1"], [[r["reserve"], r["P1_declarations_max"], r["P2_declarations_max"], r["after_T1_defender_reserve"]] for r in data["resource_context"]])
    lines += [
        "",
        "## Pommel Hit / Miss",
        "",
        "Hit deals normal damage and ends the bounded Close sequence through governing contact cleanup. Miss deals zero, retains Close Crossing with Unknown height, transfers opportunity, resets the pass count, and creates no Open, free counterattack, or separation. The governing engine explicitly preserves measure independently when contact ends; the report therefore treats post-hit Close measure as governing geometry, not stale Crossing state.",
        "",
        "## Hart vs Weich in Stretto",
        "",
        "The table reports damage conditional on an established successful T1 Close branch at P2/8S. Cancellation is the preceding Cross probability.",
        "",
    ]
    hw_rows = []
    for row in data["hart_weich_stretto"]:
        if row["skill"] not in {10, 14, 18}:
            continue
        hw_rows.append([row["skill"], row["profile"], row["pressure"].title(), pct(row["cross_cancellation"]), row["first_close_opportunity"], num(row["expected_incoming_continuation_damage"]), num(row["expected_outgoing_continuation_damage"])])
    lines += table(["Skill", "Pommel ownership", "Pressure", "Cross cancellation", "First Close", "E incoming", "E outgoing"], hw_rows)
    lines += [
        "",
        "Hart retains a niche through much better cancellation; it is dangerous when the striker knows Pommel. Weich retains a niche through defender-first Close work, especially when the defender owns Pommel. Neither is universally mandatory; ownership changes the choice.",
        "",
        "## T1 vs Beat",
        "",
        "Beat is flat, free, separates, and sets the attacker Open; T1 requires a successful Cross, 1S/+1 chain, retains reciprocal contact, and never sets Open. Hart+T1 improves initial cancellation but gives the striker first Close opportunity. Weich+T1 has Beat’s flat cancellation but gives the defender first Close opportunity. These costs/outcomes prevent weak dominance.",
        "",
        "Representative Skill-14, reserve-8, HP8 exact rows (the JSON contains every Skill 10/12/14/18 × ownership × reserve 0/1/2/3/4/8 × HP 1/4/6/8 row):",
        "",
    ]
    beat_rows = []
    for row in data["beat_control"]:
        if row["skill"] == 14 and row["reserve"] == 8 and row["target_hp"] == 8:
            beat_rows.append([row["profile"], row["choice"], pct(row["cancellation"]), num(row["eventual_incoming_damage"]), num(row["eventual_outgoing_damage"]), pct(row["eventual_incoming_kill_probability"]), pct(row["eventual_outgoing_kill_probability"]), num(row["resource_spend"]), num(row["chain_spend"]), pct(row["owner_first_probability"]), pct(row["opponent_first_probability"]), pct(row["pommel_conversion_given_legal"]), row["contact_on_success"], "yes" if row["open_on_success"] else "no", row["measure_on_success"], "yes" if row["attacker_rejoinder_access"] else "no"])
    lines += table(["Ownership", "Choice", "Cancel", "E incoming", "E outgoing", "P in kill", "P out kill", "E S", "E chain", "Owner first", "Opp. first", "Pommel conv", "Contact", "Open", "Measure", "Rejoinder"], beat_rows)
    lines += [
        "",
        "Open remains a diagnostic distinction: Beat removes the attacker’s named guard and point threat until recovery; E1 T1 does not. No Open modifier was added.",
        "",
        "## T1 vs Ordinary H3 Cross",
        "",
        "Stay-Wide preserves Fühlen/D-M/Winden; E1 exchanges that topology for Close before Rejoinder use; L1 preserves the complete Rejoinder and permits Close only after decline and a defender opportunity. At Skill 14, correct paid-information D/M has 91% hit and 4.095 expected damage for 3S total including Fühlen; E1 costs 1S before any Pommel and may expose either fighter’s Close repertoire.",
        "",
        "The JSON contains all Skills, Hart/Weich, five attacker repertoire profiles, and A/B/C timing rows. Representative Skill-14 rows:",
        "",
    ]
    h3_rows = []
    for row in data["t1_vs_wide_h3"]:
        if row["skill"] == 14:
            h3_rows.append([row["pressure"].title(), row["attacker_repertoire"], row["timing"], num(row["expected_attacker_damage"]), row["spiritus"], row["chain"], row["first_opportunity"], row["eventual_measure"], row["repertoire_unlocked"]])
    lines += table(["Pressure", "Attacker repertoire", "Route", "E attacker dmg", "S", "Chain", "Opportunity", "Measure", "Unlocked/denied"], h3_rows)
    lines += [
        "",
        "## T1 vs Winden",
        "",
        "Both P2 Pommel and ordinary Winding are 2S/+1 chain/no action flat attacks after their entry gates. Winden requires Wide Upper/Lower and supplies Ochs/Pflug plus threatening point; Pommel requires Close/current opportunity, clears height, and on miss preserves reciprocal Close without guard/threat benefit. T1+Pommel also consumes two learned entries and 3S from the T1 owner. Winden therefore remains a rational alternative rather than a dominated expensive Pommel.",
        "",
        "## Pommel vs D/M",
        "",
        "They do not share a trigger. From a successful Tutta Cross, correct D/M is Wide, 2S/+1 chain, Booned, information-dependent, and striker-first. E1+P2 is 3S/+2 chain for the T1 owner’s route, flat, and priority depends on Hart/Weich; a Hart striker who already knows Pommel may instead receive a 2S flat attack after the defender paid T1. P1 makes that latter branch suspicious at 1S; P2 preserves the current benchmark.",
        "",
        "## Close Without Pommel",
        "",
        "With neither fighter knowing Pommel, E1 still denies the Wide Rejoinder and changes measure, then normally resolves through pass/pass or Disengage. That is concrete but narrow value. It is not supplemented with generic Close payoff. T1 is therefore repertoire-dependent, not ghost value.",
        "",
        "## Opponent-Knows-Pommel Risk",
        "",
        "Hart T1 immediately gives a Pommel-trained striker first opportunity; the bounded integrated policy rationally declined T1 in C3 for exactly this reason. Weich T1 gives the defender first opportunity. T1 never guarantees its owner first Pommel.",
        "",
        "## Spiritus",
        "",
        "At reserve 0 T1 is illegal. Reserve 1 enables only T1 (or P1 Pommel for a non-paying striker); P2 requires 2S after entry, so a T1 owner needs at least 3S for immediate Pommel. Reserve 4 permits T1+P2 with 1S remaining; reserve 8 permits the full two-Pommel miss chain, subject to each fighter’s separate reserve and cap.",
        "",
        "## Chain Cap",
        "",
        "T1 consumes entry one. A Pommel miss and opponent Pommel consume entries two and three. A further learned continuation is illegal. Exact both-Pommel rows:",
        "",
    ]
    chain_rows = [[r["skill"], r["cost"], r["reserve_each"], num(r["expected_pommel_declarations"]), pct(r["p_hit_declaration_1"]), pct(r["p_hit_by_declaration_2"]), pct(r["p_cap_reached_after_t1"]), pct(r["resource_stop_probability"]), pct(r["pass_termination_probability"])] for r in data["close_chain"]]
    lines += table(["Skill", "Cost", "Reserve", "E declarations", "Hit decl.1", "Hit by decl.2", "Cap reached", "Resource stop", "Pass term."], chain_rows)
    lines += [
        "",
        "## Action Economy",
        "",
        "The original attack spends striker action; Cross spends defender action; T1, Pommel, and pass spend no additional normal Action. Deterministic and integrated tests record no hidden refresh or second-action leak.",
        "",
        "## Close Cleanup",
        "",
        "Pommel hit, two passes, Disengage, and death gates clean current opportunity/contact normally. Pommel miss retains only authored Close contact and transfers. Initial pressure and Wide height are cleared. The shared engine deliberately preserves measure independently of contact, including through `_end_bind_sequence`; no candidate-only stale measure writer was added.",
        "",
        "## Integrated Candidate Scenarios",
        "",
        f"Fixed seed {data['seed']}; {data['trials_per_integrated_scenario']} samples per scenario; binomial 95% half-width at p=.5 is approximately {1.96*(0.25/data['trials_per_integrated_scenario'])**0.5:.2%}. Policies are transparent: Weich when either side has Pommel, Hart otherwise; avoid Hart T1 against opponent Pommel; use T1 to deny D/M or enable owned Close; P2 Pommel conserves an exact 2S against a fresh 8HP target.",
        "",
    ]
    scenario_rows = []
    for item in data["integrated_scenarios"]:
        m = item["metrics"]
        scenario_rows.append([item["scenario"]["id"], item["scenario"]["label"], m.get("t1_legal_opportunities", 0), m.get("t1_declarations", 0), pct(item["t1_conversion_given_legal"]), m.get("pommel_legal_opportunities", 0), m.get("pommel_declarations", 0), pct(item["pommel_conversion_given_legal"]), m.get("h3_rejoinders", 0), item["damage"].get("A", 0), item["damage"].get("B", 0), m.get("cleanup_escape", 0)])
    lines += table(["ID", "Scenario", "T1 opp", "T1 dec", "T1 conv", "Pommel opp", "Pommel dec", "Pommel conv", "H3", "Dmg A", "Dmg B", "Cleanup"], scenario_rows)
    lines += [
        "",
        "Opportunity-conditional decline reasons are serialized per scenario. C3 declines for opponent Close-repertoire risk; resource gates suppress Pommel in C8; no chain, action, post-mortem, or stale-opportunity violation occurred. These policy conversions are evidence about the stated policy, not intrinsic frequencies.",
        "",
        "## Nearest-Alternative Audit",
        "",
        "- T1 vs remain Wide: Close topology and Rejoinder denial versus conserving 1S/slot and keeping D/M/Winden available.",
        "- T1 vs Beat: Hart accuracy/contact/Close repertoire versus free separation, Open, and no reciprocal Close risk.",
        "- Pommel vs pass/Disengage: immediate P2 attack versus resource conservation and safe exit.",
        "- Pommel vs later ordinary attack: no-action continuation now versus 2S/slot and reciprocal miss transfer.",
        "- Pommel vs Winden/D-M: same or worse resource benchmark, narrower geometry, flat accuracy, different aftermath/information.",
        "",
        "## Runtime / Instrumentation Bugs",
        "",
        "**One**: `point_threat_events` was never incremented. Repair is confined to candidate/new reporting; governing state was correct. The Loaded Cut number is a report-only historical prose discrepancy, not counted as a runtime/instrumentation bug in this milestone because the model/JSON are already correct.",
        "",
        "## Incentive Problems",
        "",
        "**One**: P1 Pommel is too resource-efficient at the 1S boundary and risks crowding the 2S action-compressed benchmark. No severe failure was found for E1+P2. E1 does not dominate Beat, does not guarantee owner-first work, and does not erase D/M without 1S/slot cost plus reciprocal/alternative-state consequences.",
        "",
        "## Project Recommendation",
        "",
        "Project may promote **E1 timing + clear height + Hart/Weich Close priority + generic P2 Pommel with no intrinsic response denial** in a separate governing-integration task. Reject P1 for promotion. This is a recommendation only; no governing record, shared engine, or packet was changed.",
        "",
        "## Exact Next Milestone",
        "",
        "If Project accepts the recommendation: one bounded **governing integration of T1/Close/Pommel**, updating only the governing register/data, shared-engine insertion window, Pommel record, and protected tests. Otherwise stop for a narrow price/priority repair experiment. Do not begin Named Guard v0.2 before adjudication.",
        "",
        "## Project Decision Table",
        "",
    ]
    lines += table(
        ["Topic", "Candidate A", "Candidate B", "Result", "Recommendation"],
        [
            ["T1 timing", "C0 undefined", "E1 before Rejoinder", "E1 resolves order", "E1"],
            ["T1 timing", "E1 early", "L1 after decline", "both coherent; E1 fits cover", "E1"],
            ["T1 height", "retain Wide height", "clear to Unknown", "stale Winding blocked", "clear"],
            ["Close priority", "T1 owner first", "Hart/Weich assignment", "reciprocal/risk-bearing", "Hart/Weich"],
            ["Pommel trigger", "T1-specific", "generic Close", "source/state aligned", "generic Close"],
            ["Pommel action", "normal Action", "continuation/no Action", "fits spent-action sequence", "continuation"],
            ["Pommel price", "1S", "2S", "P1 too efficient at low reserve", "2S"],
            ["Pommel response", "universal denial", "no intrinsic denial", "source does not support blanket denial", "no denial"],
            ["Pommel miss", "separate", "retain Close + transfer", "reciprocal and finite", "retain/transfer"],
            ["T1 vs Beat", "distinct", "dominance problem", "distinct; no weak dominance", "retain both"],
            ["T1 vs H3", "healthy branch", "Rejoinder deletion exploit", "state branch with cost/risk", "healthy candidate"],
        ],
    )
    lines += [
        "",
        "## Final Project-Review Questions",
        "",
    ]
    answers = [
        "Yes: H3 129/129, 153 baseline tests, integrated tests, and both validators passed.",
        "Yes. The governing H3 engine/data were left unchanged.",
        "Yes. 3.830555… is correct; 4.394 is a report-only prose error.",
        "Instrumentation issue: the counter had no increment site; state logic was correct.",
        "Yes, within the adjudicated boundary: the Tutta record supports covering with a pass and entering stretto.",
        "No. The source does not assign a universal owner-first Close attack.",
        "No. Pommel is supported from established Close Crossing, not specifically T1.",
        "No. Universal response denial is not cleanly source-supported.",
        "Yes.",
        "Yes, but it is less source-shaped and often unreachable after active H3.",
        "E1.",
        "L1 preserves H3 most literally; E1 is still compatible because it acts before Rejoinder use rather than rewriting H3.",
        "No unjustified owner priority: the pre-authored Hart/Weich state assigns reciprocal first opportunity.",
        "Yes. Close/Unknown is set before Rejoinder use, so Wide-gated D/M never opens from that transformed state.",
        "Yes.",
        "No. Both Winding variants are illegal after T1.",
        "Yes.",
        "Yes; pass, miss-transfer, and opponent-first Hart all preserve reciprocity.",
        "No. Hart gives the striker first; Weich gives the owner first.",
        "Yes, narrowly: Rejoinder denial, measure topology, and pass/escape consequences.",
        "Yes. Hart can give that opponent immediate first Pommel.",
        "Yes: Hart’s cancellation and Weich’s priority create ownership-sensitive variation.",
        "No across meaningful shared states.",
        "Yes: 0S separation, Open, no chain cost, and no reciprocal Close exposure.",
        "Yes: better Hart cancellation/contact, denial of Wide Rejoinder, and authored Close access.",
        "No severe exploit found; denial costs 1S/slot and can expose hostile Close repertoire.",
        "Yes: it conserves T1 cost/slot and retains D/M/Winden/information branches.",
        "Yes: it supplies guard/threat aftermath and a Wide geometry route without T1’s two-entry package.",
        "Yes at P2; P1 is an incentive risk.",
        "No.",
        "Yes; it is too cheap at the 1S boundary for promotion.",
        "Yes in the bounded matrix.",
        "No; its narrow gate is offset by an immediate full flat attack and reciprocal miss risk.",
        "Yes.",
        "Yes; it permits a reciprocal second declaration but remains bounded by hit, resource, pass, and cap.",
        "Yes. T1 plus two Pommels fills cap 3 and blocks a fourth learned declaration.",
        "No stale bind state. Measure may remain Close only because the governing model explicitly preserves it independently of contact.",
        "No.",
        "No. Opponent pressure remains unknown until after the T1 decision.",
        "Yes. E1 creates no Fühlen purchase; declining E1 restores ordinary Fühlen/H3 unchanged.",
        "Yes. T1 requires the exact ordinary Basic-Cut/Cross source and does not trigger on authored-special crossings.",
        "Yes.",
        "Yes.",
        "Yes.",
        "Yes.",
        "One.",
        "One: P1’s low-reserve efficiency.",
        "Mechanically yes for Project promotion review; not automatically promoted.",
        "Not applicable to E1+P2; P1’s 1S efficiency blocks only P1.",
        "Governing integration of T1/Close/Pommel, if Project approves; otherwise stop for adjudication rather than starting Named Guard v0.2.",
    ]
    for index, answer in enumerate(answers, 1):
        lines.append(f"{index}. {answer}")
    lines += [
        "",
        "**STOP FOR PROJECT ADJUDICATION. No candidate was promoted.**",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()

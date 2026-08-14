"""Render the human-readable audit from its machine-readable register."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "reports" / "melee-incentive-integrity-v01-results.json"
OUT = ROOT / "reports" / "melee-incentive-integrity-v01-results.md"


def cell(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, list):
        value = "; ".join(str(item) for item in value)
    if isinstance(value, dict):
        value = "; ".join(f"{key}: {item}" for key, item in value.items())
    return str(value).replace("|", "\\|").replace("\n", " ")


def table(items: list[dict[str, Any]], columns: list[tuple[str, str]]) -> str:
    lines = [
        "| " + " | ".join(label for _, label in columns) + " |",
        "|" + "|".join("---" for _ in columns) + "|",
    ]
    for item in items:
        lines.append("| " + " | ".join(cell(item.get(key)) for key, _ in columns) + " |")
    return "\n".join(lines)


def bullets(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values)


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    nodes = data["decision_nodes"]
    groups = data["required_output_groups"]
    ready = data["ready_answers"]

    parts: list[str] = []
    parts.append("# Atra Melee Incentive Integrity Audit v0.1 Results\n")
    parts.append("Status: **DIAGNOSIS ONLY — no mechanics, prices, guard benefits, transition graph, governing baseline, or design packet changed.**\n")

    parts.append("## Executive Result\n")
    parts.append(data["executive_result"] + "\n")
    parts.append(
        "**Answer: not ready for Named Guard v0.2.** A run now would measure a mixture of real rule incentives, "
        "softmax exploration, hand-authored utility constants, incomplete active repertoire, and a free switching harness "
        "that rationally harvests benefits. The result would not support clean guard-balance conclusions.\n"
    )
    parts.append(
        "The highest-confidence healthy choices are P1 Power versus ordinary Loaded Cut, C2 compounds versus free Basics, "
        "Counter versus avoidance, and Cut versus Thrust. The principal Severity 3 blockers are the Crown candidate's "
        "two-sided motivation failure, repertoire-poor Cross/Beat false choice, free guard-state harvesting, active incentive "
        "vacuums, and current Nachreisen/Zornhau-Ort policy ghosts.\n"
    )

    parts.append("## Audit Method\n")
    parts.append(
        "The audit began from the dated repository baseline and current implementation. It read the governing register, "
        "guard/Play records, named-guard, Guard Play Bridge, Crown, Loaded/Power, Crossing/Bind, Bind Continuations, "
        "Durchwechseln, Spiritus, C2, and Play-chain artifacts. Git was clean before work.\n"
    )
    parts.append(
        "Each suspect pair was first reduced to the smallest state where both alternatives are legal. Costs, immediate "
        "effects, cleanup, future access, opponent access, and information/resource consequences were compared before "
        "consulting frequencies. A deterministic probe imported the current engines and recorded utilities/argmax results. "
        "It ran no fights. No broad matrix and no Named Guard v0.2 run occurred.\n"
    )
    parts.append(
        "Controlled artifact: `simulations/incentive_integrity_v0_1/controlled-results.json`. Existing Monte Carlo reports "
        "are used only as conditional/supporting evidence; frequency alone never establishes health or failure.\n"
    )

    parts.append("## Current Governing Baseline\n")
    parts.append(
        "Preserved: G1/action-light named guards; universal Basic Cut, Thrust, Cross, and Beat; D1 at 1 Spiritus; C2 "
        "Absetzen/Scambiar/Schielhau at 2 Spiritus; S2; explicit Crossing/measure/contact axes; declared Cross/Beat; "
        "learned-Play cap 3; Loaded proactive Cut Damage Boon; P1 fixed-7 Power at 1 Spiritus with Committed and "
        "Counter-first; free before-or-after guard change as a provisional warned harness; and Tutta T1.\n"
    )
    parts.append(
        "C1/B3 Scheitelhau/Crown remains a **candidate**, not governing. Its engine viability is evidence, not incentive "
        "acceptance. The audit does not promote or reject it canonically.\n"
    )
    parts.append(
        "Implementation boundary: `simulations/shared/provisional_longsword.py` stores T1 metadata but selects the "
        "Loaded/Power engine; actual T1 behavior lives in the separate Guard Play Bridge subclass. The named-guard harness "
        "also does not enforce the guard record's Vom Tag→Nachreisen gate. These are integration facts, not silently "
        "resolved rules.\n"
    )

    parts.append("## Decision Node Inventory\n")
    parts.append(
        "The full required fields are split across four keyed tables for readability. Together they are the human-readable "
        "form of `decision_nodes` in the JSON artifact.\n"
    )
    parts.append("### Identity, alternatives, and costs\n")
    parts.append(table(nodes, [
        ("decision_node_id", "ID"), ("actor", "Actor"), ("state/preconditions", "State / preconditions"),
        ("option_A", "Option A"), ("option_B", "Option B"), ("costs_A", "Costs A"), ("costs_B", "Costs B"),
    ]) + "\n")
    parts.append("### Immediate and resulting state\n")
    parts.append(table(nodes, [
        ("decision_node_id", "ID"), ("immediate_A", "Immediate A"), ("immediate_B", "Immediate B"),
        ("resulting_state_A", "Resulting state A"), ("resulting_state_B", "Resulting state B"),
    ]) + "\n")
    parts.append("### Future and opponent options\n")
    parts.append(table(nodes, [
        ("decision_node_id", "ID"), ("future_options_A", "Future A"), ("future_options_B", "Future B"),
        ("opponent_options_A", "Opponent after A"), ("opponent_options_B", "Opponent after B"),
    ]) + "\n")
    parts.append("### Motivation, classification, severity, and evidence\n")
    parts.append(table(nodes, [
        ("decision_node_id", "ID"), ("rules_based_motivation_A", "Rules motive A"),
        ("rules_based_motivation_B", "Rules motive B"), ("policy_only_motivation", "Policy-only motive"),
        ("failure_classification", "Classification"), ("conditions", "Conditions"), ("severity", "Severity"),
        ("pre_v02_status", "Pre-v0.2"), ("smallest_next_design_question", "Smallest next design question"),
        ("evidence/metric references", "Evidence / metrics"),
    ]) + "\n")

    parts.append("## Dominance Framework\n")
    parts.append(
        "Dominance was evaluated across action, Spiritus, learned-slot, guard, contact/measure, probability, damage, "
        "cancellation, displacement, retained contact, point threat, continuation access for both sides, revealed "
        "information, commitment, action preservation, cleanup, reserve, and repertoire. Lower immediate damage did not "
        "count as domination where it bought a distinct valuable state. Conversely, a source-valid label did not count as "
        "value when the active rules attached no consequence.\n"
    )
    parts.append(
        "Cross/Beat illustrates the distinction: the source identities differ, but without an authored continuation the "
        "active outcomes converge after cleanup. That is a false choice, not a damage comparison. Power/Loaded illustrates "
        "the opposite: Power has higher fixed damage but real resource, commitment, continuation, and Counter-first costs, "
        "so neither dominates across relevant states.\n"
    )

    parts.append("## Confirmed Healthy Choices\n")
    parts.append(bullets(groups["A_CONFIRMED_HEALTHY"]) + "\n")
    parts.append(
        "Power/Loaded and C2/Basic are the cleanest healthy cases. Each option has a rules-derived state where it is "
        "rational, and the difference survives removal of random exploration. P1 use frequency does not: the current "
        "heuristic's deterministic argmax preferred Loaded Cut in all 27 controlled cells, so broad observed P1 use is "
        "softmax-supported even though lethal-certainty Power choices remain rational under the rules.\n"
    )

    parts.append("## Cross vs Beat\n")
    parts.append(
        "For a fighter with no useful Crossing repertoire, Cross is not demonstrably preferable in a common active state. "
        "Cross and Beat pay the same action, share the same success probability and D1 window, and cancel the same attack. "
        "Cross creates an unretained Crossing that is cleaned immediately; Beat records displacement and separation, but "
        "displacement has no persistent active payoff. Their post-cleanup vectors converge.\n"
    )
    parts.append(
        "Therefore H3 is not literally proven as strict Beat dominance. The stronger diagnosis is **FALSE CHOICE**. If "
        "separation is treated as intrinsically safer outside the implemented consequences, Beat weakly dominates; the "
        "engine itself does not value that safety. The policy gives both forms identical utilities, so approximately even "
        "frequency is softmax/tie behavior, not evidence of two meaningful choices.\n"
    )
    parts.append(
        "Cross becomes distinct only through useful authored repertoire. T1 can provide that distinction, while full Winden "
        "is inactive and generic Cross does not unlock Crown. Even T1 is healthy only when the owner's downstream Close "
        "value exceeds the opponent's. This makes Cross currently **HEALTHY BUT REPERTOIRE-DEPENDENT** at best and a "
        "Severity 3 blocker for a general guard comparison whose mappings lean on Cross/Beat.\n"
    )

    parts.append("## Durchwechseln vs Basic Parry\n")
    parts.append(
        "The rational defender can nearly abandon nonthreatening Basic Parry when the attacker is known to have D1, has "
        "usable reserve, and both Skills are high. The older focused report found post-reveal P1 choice at 0.3% for Skill "
        "18/S8; the deterministic current-policy probe also prefers declaration across most high-skill S8/S3 pairs. This "
        "is rules-driven in direction: D1 replaces a likely successful defence with the attacker's high-probability roll for "
        "1 Spiritus.\n"
    )
    parts.append(
        "The choice returns when the defender's threatening point denies D1, attacker Spiritus reaches 0, the attacker is "
        "depleted to a valuable last point, attacker Skill is low, defender Skill is low enough that allowing the original "
        "Parry failure is attractive, or information is uncertain. At S1 the deterministic probe declined in every tested "
        "pair except 18/18. This is **HEALTHY tactical deterrence with a CONDITIONAL DOMINANCE WARNING**, Severity 2—not a "
        "universal Basic-Parry defect.\n"
    )

    parts.append("## Power vs Loaded Cut\n")
    parts.append(
        "Ordinary Loaded Cut: same attack probability, 2–7 damage, mean 5.472, no Spiritus, D1/attacker insertion access "
        "preserved. P1: same attack probability, fixed 7, 1 Spiritus, Committed, no D1/attacker insertion, Counter-first. "
        "Power is rational for fixed maximum and lethal certainty; Loaded Cut is rational for reserve, flexibility, and "
        "survival when wounded. **HEALTHY, Severity 0.** No rebalance is indicated by this audit.\n"
    )

    parts.append("## Compounds vs Basics\n")
    parts.append(
        "Absetzen and Scambiar buy joined defence/offence and threatening-point Crossing for 2 Spiritus and one learned "
        "slot. Schielhau buys joined defence/offence plus an S2 contest and threatening-point separation. Basics conserve "
        "reserve and chain space. The focused C2 report shows compounds recede sharply near S2/S1 and are unavailable below "
        "cost; at high reserve their unpriced one-step payload is superior, but reserve competition remains real. This is "
        "resource-driven substitution, not strict dominance.\n"
    )
    parts.append(
        "Absetzen and Scambiar are mechanically identical in the current chassis and differ through guard/source access. "
        "Because they are not normally co-legal, this is a chassis-compression watch item rather than a player-facing "
        "same-node dominance result. **C2 versus Basics is HEALTHY, Severity 0.**\n"
    )

    parts.append("## Reciprocal-Sequence Table\n")
    parts.append(table(data["reciprocal_sequences"], [
        ("sequence", "Sequence"), ("step", "Step"), ("acting side", "Acting side"),
        ("available alternatives", "Available alternatives"),
        ("why actor chooses historical option", "Why actor chooses historical option"),
        ("why opponent chooses historical response", "Why opponent chooses historical response"),
        ("source/mechanical constraint", "Source / mechanical constraint"),
        ("whether motivation is rules-derived", "Rules-derived?"),
        ("whether sequence collapses under rational play", "Collapses?"), ("severity", "Severity"),
    ]) + "\n")

    parts.append("## Guard Motivation\n")
    parts.append(table(data["guards"], [
        ("guard", "Guard"), ("unique intrinsic state", "Unique intrinsic state"),
        ("Basic mappings", "Basic mappings"), ("active learned access", "Active learned access"),
        ("active vulnerabilities/breakers", "Vulnerabilities / breakers"), ("reason to enter", "Reason to enter"),
        ("reason to stay", "Reason to stay"), ("reason to leave", "Reason to leave"),
        ("switch-in harvesting risk", "Switch-in harvesting"), ("switch-out harvesting risk", "Switch-out harvesting"),
        ("repertoire dependence", "Repertoire dependence"), ("incentive-vacuum status", "Vacuum?"),
        ("severity", "Severity"),
    ]) + "\n")
    parts.append(
        "This table does not balance guards against one another. It asks whether each guard currently has any owner-side "
        "reason to exist. Alber and Frontale do not. Vom Tag's intended Nachreisen identity is not realized by the active "
        "gate or chassis. Ochs has point threat but is conditionally dominated by Pflug when Absetzen is known. Tutta is "
        "legitimate repertoire-dependent access. Donna has a real offensive identity, while Mezza/Pflug can be harvested as "
        "free defensive staging states.\n"
    )

    parts.append("## Guard-Change Benefit Harvesting\n")
    parts.append(
        "The harness permits one free change either before or after an activation and resets permission next activation. "
        "That produces three rational patterns: enter Donna before a proactive Cut; change after acting into Pflug/Ochs/Mezza "
        "so point threat is active during the opponent's turn; and preposition into Pflug or Tutta to make a learned response "
        "legal. An actor already in Donna can use Loaded/P1 and then leave after the action.\n"
    )
    parts.append(
        "The timing restriction creates some friction: switching into Donna before attacking prevents an immediate same-activation "
        "exit and leaves one defence interval of D1 exposure. It does not impose an action/resource cost, and an after-action "
        "switch acquires defensive state after the actor's useful action has resolved. The policy's 0.09 change friction is not "
        "a rule. Existing churn is therefore both a real incentive symptom and a policy-shaped quantity. **Severity 3.**\n"
    )

    parts.append("## Tutta Cover to Stretto\n")
    parts.append(
        "T1's unique purchase is retained Close Crossing. It is rational when the owner possesses a useful Close consumer the "
        "opponent lacks or when information/order makes owner exploitation more valuable. With no Close consumer, spending "
        "1 Spiritus and a slot buys no owner payoff. With symmetric Pommel, either fighter may exploit Close after action "
        "refresh and there is no owner priority, creating reciprocal risk.\n"
    )
    parts.append(
        "The current policy does not evaluate this. It assigns a Close-state proxy (0.25 plus opponent-HP term minus reserve) "
        "and chooses against zero. Thus T1 is **HEALTHY BUT REPERTOIRE-DEPENDENT**, with an incentive vacuum in no-consumer "
        "states and a Severity 2 integration/motivation question before v0.2. Its price and trigger are not reopened here.\n"
    )

    parts.append("## Frontale and Mapping-Only Guards\n")
    parts.append(
        "Frontale's high-thrust Cross and low-thrust Beat are source-identity mappings to universal Basics. They provide no "
        "reason to enter Frontale because every guard can use those Basics and no modifier follows. The distinctive "
        "retreat/cut/thrust sequence is inactive. Frontale is therefore an **INCENTIVE VACUUM** and conditionally dominated "
        "by Mezza's free threatening point in current active mechanics. It can remain a source-facing/transitional record, but "
        "a v0.2 balance run cannot interpret it as a populated guard.\n"
    )
    parts.append(
        "The same test applies to other mappings: Mezza's Thrust/Beat mappings are universal, but its threatening point is "
        "active; Tutta's Cross/Beat mappings are universal, but Scambiar/T1 can create repertoire value; Donna's Cut mapping "
        "is universal, but Loaded/P1 is active. Source identity is preserved without pretending it is mechanical motivation.\n"
    )

    parts.append("## Scheitelhau / Crown Reciprocal Motivation\n")
    parts.append(
        "The candidate fails incentive viability despite passing engine viability. First, every qualifying B3 Basic Cut is "
        "automatically tagged. The tag changes no cost, roll, damage, commitment, information, or slot and only adds a future "
        "option. That is **FREE UPSIDE / AUTO-TAG**.\n"
    )
    parts.append(
        "Second, Crown uses the same defence probability/cancellation role as generic Cross but creates a transient context "
        "whose only active payoff belongs to the attacker. Generic Cross avoids that risk; Beat also cancels and separates; "
        "Counter offers a damage trade. No defender benefit or physical constraint makes Crown rational. The simulator chooses "
        "Crown because it scores `1.10 × defence probability` against an arbitrary aggregate 0.35, not because of consequences. "
        "This is **DOMINATED CHOICE + RECIPROCAL MOTIVATION FAILURE + POLICY ARTIFACT**, Severity 3.\n"
    )
    parts.append(
        "Once Crown is granted, Sink Point versus decline is healthy: 1 Spiritus and one slot buy a normal attack chance, while "
        "declining conserves reserve. That local health does not rescue the sequence because rational defence prevents the "
        "state from arising. C1/B3 is neither promoted nor rejected canonically; it is unsuitable as v0.2 input until its "
        "smallest motivation questions are adjudicated.\n"
    )

    parts.append("## Policy vs Rules\n")
    parts.append(
        "Rules-derived value includes actual damage, cancellation, reserve, action, chain, contact, point threat, continuation "
        "access, and opponent access. A positive score, random exploration, or even deterministic selection from a hand-authored "
        "constant is not rules evidence. The current policy is useful for exercising branches, not for proving rational choice.\n"
    )
    parts.append("### Would This Choice Exist Without Softmax?\n")
    parts.append(table(data["policy_and_instrumentation"]["would_this_choice_exist_without_softmax"], [
        ("choice", "Choice"), ("deterministic_argmax", "Deterministic argmax"),
        ("would_exist", "Would it exist?"), ("classification", "Classification"),
    ]) + "\n")

    parts.append("## Instrumentation Findings\n")
    parts.append(bullets(data["policy_and_instrumentation"]["instrumentation_findings"]) + "\n")
    parts.append(
        "No reporting code was changed. Dedicated metrics are sufficient for this audit when their semantics are kept separate; "
        "changing historical outputs was unnecessary.\n"
    )

    parts.append("## Required Output Groups\n")
    labels = {
        "A_CONFIRMED_HEALTHY": "A. Confirmed Healthy",
        "B_HEALTHY_BUT_REPERTOIRE_DEPENDENT": "B. Healthy but Repertoire-Dependent",
        "C_WATCH_ITEMS": "C. Watch Items",
        "D_MATERIAL_INCENTIVE_DEFECTS": "D. Material Incentive Defects",
        "E_BLOCKERS_BEFORE_NAMED_GUARD_V0_2": "E. Blockers Before Named Guard v0.2",
        "F_POLICY_INSTRUMENTATION_ARTIFACTS": "F. Policy / Instrumentation Artifacts",
        "G_OPEN_INSUFFICIENT_CURRENT_MECHANICS": "G. Open — Insufficient Current Mechanics",
    }
    for key, label in labels.items():
        parts.append(f"### {label}\n")
        parts.append(bullets(groups[key]) + "\n")

    parts.append("## Severity Register\n")
    parts.append(table(data["severity_register"], [
        ("issue", "Issue"), ("classification", "Classification"), ("severity", "Severity"),
        ("pre_v02_status", "Pre-v0.2"), ("smallest_next_design_question", "Smallest next design question"),
    ]) + "\n")

    parts.append("## Blockers Before Named Guard v0.2\n")
    blockers = [item for item in data["severity_register"] if item["severity"] == 3]
    parts.append(bullets([item["issue"] for item in blockers]) + "\n")
    parts.append(
        "These are blockers to interpreting the experiment, not automatic instructions to repair mechanics. No transition "
        "graph, bonuses, price changes, new Plays, or baseline promotions follow from this audit.\n"
    )

    parts.append("## Smallest Next Design Questions\n")
    parts.append(bullets(ready["O_minimum_questions"]) + "\n")

    parts.append("## Ready for Named Guard v0.2?\n")
    qa = [
        ("A. Which choices are demonstrably healthy?", "A_demonstrably_healthy"),
        ("B. Which are healthy only with learned repertoire?", "B_healthy_only_with_repertoire"),
        ("C. Which are strictly dominated?", "C_strictly_dominated"),
        ("D. Which are conditionally dominated?", "D_conditionally_dominated"),
        ("E. Which are free-upside / automatic?", "E_free_upside"),
        ("F. Which sequences have reciprocal failure?", "F_reciprocal_failures"),
        ("G. Which guards have incentive vacuums?", "G_guard_vacuums"),
        ("H. Is Cross rational without repertoire?", "H_cross_without_repertoire"),
        ("I. Does D1 materially delete high-skill Basic Parry?", "I_durch_deletes_parry"),
        ("J. Is free switching producing rational harvesting?", "J_guard_harvesting"),
        ("K. Which choices are policy artifacts?", "K_policy_artifacts"),
        ("L. Which issues are Severity 3?", "L_severity_3"),
        ("M. Which Severity 2 issues may wait?", "M_severity_2_may_wait"),
        ("N. Can a run now be interpreted?", "N_run_now"),
        ("O. Minimum questions first?", "O_minimum_questions"),
    ]
    for question, key in qa:
        parts.append(f"**{question}**\n")
        answer = ready[key]
        parts.append((bullets(answer) if isinstance(answer, list) else answer) + "\n")

    parts.append("## Validation and Change Boundary\n")
    parts.append(
        "The deterministic probe completed successfully. Repository validation and tests are reported in the task handoff. "
        "No existing combat mechanic, baseline record, Play record, guard record, historical report, or design packet was "
        "modified. The only executable addition is the scoped diagnosis-only probe and renderer.\n"
    )

    OUT.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()

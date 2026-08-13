from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = ROOT / "reports" / "general-bind-information-architecture-v01-results.json"
REPORT_PATH = ROOT / "reports" / "general-bind-information-architecture-v01-results.md"
SKILLS = (10, 12, 14, 18)
HART_PRIORS = (0.2, 0.4, 0.5, 0.6, 0.8)
MEAN_DAMAGE = 4.5
PRIMARY_FUHLEN_COST = 1
PRIMARY_DM_COST = 2


def p_flat(skill: int) -> float:
    return skill / 20


def p_boon(skill: int) -> float:
    p = p_flat(skill)
    return 1 - (1 - p) ** 2


def p_bane(skill: int) -> float:
    return p_flat(skill) ** 2


def metrics(success: float, spiritus: int, wrong: float, model: str, dm_cost: int) -> dict[str, Any]:
    damage = success * MEAN_DAMAGE
    return {
        "expected_attack_success": success,
        "expected_damage": damage,
        "spiritus_spent": spiritus,
        "damage_per_spiritus": None if spiritus == 0 else damage / spiritus,
        "wrong_read_probability": wrong,
        "wrong_conditioned_spiritus": wrong * dm_cost,
        "wasted_spiritus_zero_output": wrong * dm_cost if model == "F" else 0.0,
    }


def alternative_rows(skill: int, hart_prior: float, model: str, fuhlen_cost: int, dm_cost: int) -> dict[str, dict[str, Any]]:
    boon, bane = p_boon(skill), p_bane(skill)
    q = hart_prior
    if model == "G":
        dup_p = q * boon + (1 - q) * bane
        mut_p = (1 - q) * boon + q * bane
    else:
        dup_p = q * boon
        mut_p = (1 - q) * boon
    return {
        "blind_duplieren": metrics(dup_p, dm_cost, 1 - q, model, dm_cost),
        "blind_mutieren": metrics(mut_p, dm_cost, q, model, dm_cost),
        "buy_fuhlen": metrics(boon, dm_cost + fuhlen_cost, 0.0, model, dm_cost),
        "decline": metrics(0.0, 0, 0.0, model, dm_cost),
    }


def best_by(rows: dict[str, dict[str, Any]], key: str) -> list[str]:
    candidates = {name: row[key] for name, row in rows.items() if row[key] is not None}
    best = max(candidates.values())
    return [name for name, value in candidates.items() if abs(value - best) < 1e-12]


def pareto_frontier(rows: dict[str, dict[str, Any]]) -> list[str]:
    frontier: list[str] = []
    for name, row in rows.items():
        dominated = False
        for other_name, other in rows.items():
            if other_name == name:
                continue
            no_worse = (
                other["expected_damage"] >= row["expected_damage"]
                and other["spiritus_spent"] <= row["spiritus_spent"]
            )
            strict = (
                other["expected_damage"] > row["expected_damage"]
                or other["spiritus_spent"] < row["spiritus_spent"]
            )
            if no_worse and strict:
                dominated = True
                break
        if not dominated:
            frontier.append(name)
    return frontier


def skill_table() -> list[dict[str, Any]]:
    output = []
    for skill in SKILLS:
        flat, boon, bane = p_flat(skill), p_boon(skill), p_bane(skill)
        output.append({
            "skill": skill,
            "flat_attack_success": flat,
            "boon_attack_success": boon,
            "bane_attack_success": bane,
            "flat_parry_success": flat,
            "booned_hart_parry_success": boon,
            "correct_minus_wrong_absolute": boon - bane,
            "correct_over_wrong_ratio": boon / bane,
            "wrong_reduction_from_correct_relative": (boon - bane) / boon,
            "expected_duplieren_damage_correct": boon * MEAN_DAMAGE,
            "expected_duplieren_damage_wrong_G": bane * MEAN_DAMAGE,
            "expected_duplieren_damage_wrong_F": 0.0,
            "expected_mutieren_damage_correct": boon * MEAN_DAMAGE,
            "expected_mutieren_damage_wrong_G": bane * MEAN_DAMAGE,
            "expected_mutieren_damage_wrong_F": 0.0,
        })
    return output


def pressure_matrix() -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for model in ("G", "F"):
        for skill in SKILLS:
            for q in HART_PRIORS:
                rows = alternative_rows(skill, q, model, PRIMARY_FUHLEN_COST, PRIMARY_DM_COST)
                best_blind = max(
                    rows["blind_duplieren"]["expected_damage"],
                    rows["blind_mutieren"]["expected_damage"],
                )
                gain = rows["buy_fuhlen"]["expected_damage"] - best_blind
                output.append({
                    "model": model,
                    "skill": skill,
                    "hart_prior": q,
                    "pressure_frequency_instrumentation": {"hart": q, "weich": 1 - q},
                    "alternatives": rows,
                    "best_expected_damage": best_by(rows, "expected_damage"),
                    "best_damage_per_spiritus": best_by(rows, "damage_per_spiritus"),
                    "pareto_frontier": pareto_frontier(rows),
                    "fuhlen_damage_gain_over_best_blind": gain,
                    "wrong_pressure_spiritus_exposure_avoided": (
                        min(q, 1 - q) * PRIMARY_DM_COST
                    ),
                    "fuhlen_break_even_marginal_damage_per_added_spiritus": gain / PRIMARY_FUHLEN_COST,
                    "utility_free_unique_best_response": None,
                    "utility_note": "Damage and Spiritus are separate outcome dimensions; no scalar best response exists without a reserve/opportunity value.",
                })
    return output


def fuhlen_sensitivity() -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for model in ("G", "F"):
        for skill in SKILLS:
            for cost in (0, 1, 2):
                damage_purchases = 0
                efficiency_purchases = 0
                rows_out = []
                for q in HART_PRIORS:
                    rows = alternative_rows(skill, q, model, cost, PRIMARY_DM_COST)
                    best_blind_name = max(
                        ("blind_duplieren", "blind_mutieren"),
                        key=lambda name: rows[name]["expected_damage"],
                    )
                    best_blind = rows[best_blind_name]
                    info = rows["buy_fuhlen"]
                    damage_rational = info["expected_damage"] > best_blind["expected_damage"] + 1e-12 or (
                        abs(info["expected_damage"] - best_blind["expected_damage"]) < 1e-12
                        and info["spiritus_spent"] <= best_blind["spiritus_spent"]
                    )
                    efficiency_rational = (
                        info["damage_per_spiritus"] >= best_blind["damage_per_spiritus"] - 1e-12
                    )
                    damage_purchases += int(damage_rational)
                    efficiency_purchases += int(efficiency_rational)
                    gain = info["expected_damage"] - best_blind["expected_damage"]
                    rows_out.append({
                        "hart_prior": q,
                        "best_blind": best_blind_name,
                        "expected_damage_gain": gain,
                        "extra_spiritus": cost,
                        "break_even_damage_per_extra_spiritus": None if cost == 0 else gain / cost,
                        "damage_maximizing_purchase": damage_rational,
                        "efficiency_purchase": efficiency_rational,
                    })
                output.append({
                    "model": model,
                    "skill": skill,
                    "fuhlen_cost": cost,
                    "controlled_priors": rows_out,
                    "damage_maximizing_purchase_rate": damage_purchases / len(HART_PRIORS),
                    "damage_per_spiritus_purchase_rate": efficiency_purchases / len(HART_PRIORS),
                    "threshold_formula": (
                        "pay when min(q,1-q)*4.5*(Pboon-Pbane) > lambda*fuhlen_cost"
                        if model == "G"
                        else "pay when min(q,1-q)*4.5*Pboon > lambda*fuhlen_cost"
                    ),
                    "lambda_definition": "player's unassigned marginal damage-equivalent value of one Spiritus; no value is set here",
                })
    return output


def dm_cost_sensitivity() -> list[dict[str, Any]]:
    output = []
    for skill in SKILLS:
        boon, bane, flat = p_boon(skill), p_bane(skill), p_flat(skill)
        for model in ("G", "F"):
            for cost in (1, 2):
                correct_damage = boon * MEAN_DAMAGE
                wrong_damage = (bane * MEAN_DAMAGE) if model == "G" else 0.0
                output.append({
                    "skill": skill,
                    "model": model,
                    "dm_cost": cost,
                    "correct_expected_damage": correct_damage,
                    "wrong_expected_damage": wrong_damage,
                    "correct_damage_per_spiritus": correct_damage / cost,
                    "wrong_damage_per_spiritus": wrong_damage / cost,
                    "ordinary_basic_attack": {"spiritus": 0, "action": 1, "expected_damage": flat * MEAN_DAMAGE},
                    "nachreisen_1S": {"spiritus": 1, "action": 1, "expected_damage": boon * MEAN_DAMAGE},
                    "ort_O1_1S_candidate": {"spiritus": 1, "additional_roll": 0, "damage_when_requirement_met": MEAN_DAMAGE},
                    "C2_2S": {"spiritus": 2, "action": 1, "expected_outgoing_damage": flat * MEAN_DAMAGE, "also_cancels_on_success": True},
                    "dm_action_compression": "attack continuation after the actor's initiating normal action is already spent",
                })
    return output


def counter_wind_results() -> list[dict[str, Any]]:
    output = []
    for skill in SKILLS:
        defence = p_flat(skill)
        for model in ("G", "F"):
            for pressure in ("hart", "weich"):
                correct = pressure == "hart"
                attack_p = p_boon(skill) if correct else (p_bane(skill) if model == "G" else 0.0)
                eligible = attack_p > 0 or model == "G"
                output.append({
                    "skill": skill,
                    "model": model,
                    "pressure": pressure,
                    "duplieren_correct": correct,
                    "no_counter_wind": {
                        "attack_resolution_success": attack_p,
                        "expected_incoming_damage": attack_p * MEAN_DAMAGE,
                    },
                    "known_counter_wind_defender_0S": {
                        "attack_resolution_success": attack_p,
                        "expected_incoming_damage": attack_p * MEAN_DAMAGE,
                        "counter_wind_available": False,
                    },
                    "known_counter_wind_defender_1S_plus_forced_branch": {
                        "counter_wind_available": eligible,
                        "spiritus_spent": 1 if eligible else 0,
                        "chain_entries": 1 if eligible else 0,
                        "attack_resolution_success": (1 - defence) * attack_p if eligible else 0.0,
                        "expected_incoming_damage": (1 - defence) * attack_p * MEAN_DAMAGE if eligible else 0.0,
                        "retained_crossing_frequency": defence if eligible else 0.0,
                        "initiative_transfer_frequency": defence if eligible else 0.0,
                        "duplieren_suppression_fraction": defence if eligible and attack_p > 0 else None,
                    },
                })
    return output


def response_economy() -> dict[str, Any]:
    return {
        "initial": {
            "attacker_action_spent": True,
            "defender_action_spent_on_cross": True,
            "contact": "crossing",
            "measure": "wide",
            "pressure": "authored Hart or Weich",
            "point_threat": "unchanged by Basic Cross",
            "bind_initiative": None,
            "next": ["Duplieren", "Mutieren", "decline"],
        },
        "decline_hart": {"bind_initiative": "original striker", "next": ["legal authored bind continuation", "Disengage", "pass"]},
        "decline_weich": {"bind_initiative": "crossing defender", "next": ["legal authored bind continuation", "Disengage", "pass"]},
        "duplieren_or_mutieren": {
            "attacker_additional_action_spent": False,
            "attacker_spiritus_delta": -2,
            "attacker_chain_delta": 1,
            "ordinary_cross_beat_counter_by_parrier": "unavailable because the parrier's action was spent creating the initial Cross; this is action economy, not response denial",
            "normal_result": "ordinary cleanup ends contact",
        },
        "counter_wind_success": {
            "defender_additional_action_spent": False,
            "defender_spiritus_delta": -1,
            "defender_chain_delta": 1,
            "contact": "crossing retained",
            "bind_initiative": "Counter-Wind user",
            "damage": 0,
            "next": ["legal authored bind continuation", "Disengage", "pass"],
        },
        "counter_wind_failure": {
            "defender_spiritus_delta": -1,
            "defender_chain_delta": 1,
            "duplieren_modifier_unchanged": True,
            "next": "resolve Duplieren; normal cleanup",
        },
    }


def run_all() -> dict[str, Any]:
    return {
        "metadata": {
            "status": "PROVISIONAL BOUNDED CANDIDATE EXPERIMENT; NO AUTOMATIC PROMOTION",
            "method": "exact probability enumeration and deterministic branch forcing; no Monte Carlo",
            "skills": list(SKILLS),
            "hart_priors": list(HART_PRIORS),
            "mean_normal_longsword_damage": MEAN_DAMAGE,
            "primary_costs": {"fuhlen": 1, "duplieren": 2, "mutieren": 2, "counter_wind": 1},
            "utility_constants": [],
        },
        "deterministic": {"prior_baseline_passed": 81, "prior_baseline_required": 81, "candidate_passed": 75, "candidate_required": 75},
        "skill_table": skill_table(),
        "pressure_read_matrix": pressure_matrix(),
        "fuhlen_price_sensitivity": fuhlen_sensitivity(),
        "duplieren_mutieren_cost_sensitivity": dm_cost_sensitivity(),
        "counter_wind": counter_wind_results(),
        "response_economy": response_economy(),
        "defender_pressure_mixing": {
            "classification": "DEFENDER PRESSURE MIXING NOT YET EVALUABLE",
            "reason": "Hart has exact immediate Parry-Boon value; Weich writes Bind Initiative, but the bounded current repertoire supplies no adjudicated defender-side continuation whose actual consequences price that initiative without importing an unpromoted Winden variant or a utility constant.",
        },
        "recommendations_not_promotions": {
            "ordinary_bind_information": "do not replace R0 yet; H1 remains promising but Weich lacks measurable downstream value",
            "fuhlen": "F1 is the healthiest tested price only with hard failure; G makes paid information weak at high Skill",
            "wrong_read": "F hard failure is the stronger information-game candidate; retain as unpromoted pending integrated reserve testing",
            "dm_cost": "retain 2S as review candidate because the Rejoinder compresses a second attack after the normal action is spent",
            "counter_wind": "mechanically clean with existing operators, but 1S suppresses 50-90% of eligible Duplieren branches and needs integrated resource testing",
            "next_milestone": "another bind-repertoire increment: item-level audit and one narrow defender-side Weich/Bind-Initiative consumer, likely Zucken only if evidence supports it",
        },
    }


def pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def num(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def build_report(results: dict[str, Any]) -> str:
    skill = results["skill_table"]
    matrix = results["pressure_read_matrix"]
    fuhlen_rows = [
        "| Model | Skill | F cost | Raw-damage purchase rate | Damage/S purchase rate |",
        "|---|---:|---:|---:|---:|",
    ]
    for item in results["fuhlen_price_sensitivity"]:
        fuhlen_rows.append(
            f"| {item['model']} | {item['skill']} | {item['fuhlen_cost']} | "
            f"{pct(item['damage_maximizing_purchase_rate'])} | {pct(item['damage_per_spiritus_purchase_rate'])} |"
        )
    lines = [
        "# General Bind Information Architecture v0.1 Results", "",
        "Status: **PROVISIONAL bounded candidate experiment; no governing or canonical promotion.**", "",
        "## Executive Result", "",
        "H1 is mechanically coherent but does **not yet justify replacing R0**. Authored Hart/Weich creates a readable hidden information axis and the narrow attacker Bind Rejoinder cleanly gives Duplieren/Mutieren their post-parry timing without a second normal action. The blocking comparison is defender-side value: Hart has an exact Parry Boon, while Weich's Bind Initiative has no adjudicated downstream consumer in this bounded repertoire. **DEFENDER PRESSURE MIXING NOT YET EVALUABLE.**", "",
        "Graduated wrong-read Bane becomes weak at high Skill: at Skill 18 it still succeeds 81.0%, versus 99.0% with the correct Boon. Hard failure preserves the information lesson and makes F1 a real efficiency choice at central priors, but remains punitive and unpromoted. F0 collapses guessing; F2 is never more Spiritus-efficient than the best blind choice in the tested grid. The scoped Counter-Wind uses existing operators, but its normal defence roll suppresses 50-90% of otherwise resolving eligible Duplieren branches across Skills 10-18.", "",
        "## Source-of-Truth Check", "",
        "The worktree was clean before the task. Atra Melee Design Packet v0.4, the governing register/YAML, Melee Mechanical Effect Vocabulary v0.1, Crossing/Bind v0.1, Bind Continuations v0.1, Incentive Integrity v0.1, Guard Evidence & Repertoire v0.1, the current audited Play records, the shared selector, authoritative engine, and prior repair artifacts were inspected. The prior repair suite passed **81/81** before candidate work. No material unexplained baseline conflict was found.", "",
        "Repository evidence does not contain standalone Fühlen or Zucken Play records. Fühlen is audited through the Winden witness at Pseudo-Peter von Danzig ff. 37r.2-38v.1. Duplieren/Mutieren and the exact counter-winding remain `needs-item-level-audit`; the candidate uses the Project's supplied adjudication but does not invent or promote an exact locator.", "",
        "## Control Architecture Preserved", "",
        "The authoritative shared engine and governing records were not edited. R0 retains state-based D1, threatening-point denial, Cross/Beat, GC1, Committed timing, repaired Nachreisen, Zornhau point threat, Favored/Unfavored, current Fühlen, Ort/Winden candidates, C2/S2/T1/P1, Bind Initiative, and cap 3. H1 lives only in `simulations/general_bind_information_v0_1/` and its prototype overlay.", "",
        "## Historical Boundary", "",
        "The historical layer supports Hart/Weich bind opposition, Fühlen as sensing and acting Indes, Duplieren toward strong opposition, Mutieren toward weak opposition with winding, and Winden as a broader family. Hart Boon, Weich initiative, secret pre-roll authoring, Spiritus prices, wrong-read Bane/failure, and the exact Bind Rejoinder window are explicitly Atra abstractions.", "",
        "## R0 Favored/Unfavored Control", "",
        "R0 derives Favored/Unfavored from the two successful rolls creating a contested Crossing, keeps Bind Initiative separate, and lets current passive Fühlen reveal the categorical relation. It adds no extra roll, but the information axis is roll-derived rather than authored pressure.", "",
        "## H1 Authored Hart/Weich Candidate", "",
        "For ordinary Basic Cross only, the parrier authors hidden Hart or Weich before the Cross roll. A failed Cross writes no pressure. A successful H1 Cross writes Crossing and the declared pressure, leaves Favored/Unfavored Unknown, and opens one attacker Bind Rejoinder. Specialized creators such as Zornhau remain unchanged.", "",
        "## Hart vs Weich Defensive Trade", "",
        "Hart uses exactly one Parry Boon; Weich is flat. Hart's immediate success advantage is therefore exact and Skill-dependent. Weich's benefit is sequencing rather than a modifier, but that sequencing cannot be priced in this bounded scenario without an actual continuation.", "",
        "## Bind Rejoinder Timing", "",
        "The successful initial Cross has spent both fighters' normal actions. The original attacker may nevertheless declare only Duplieren or Mutieren as an authored no-additional-action continuation. Declining closes the window. Arbitrary Plays are not legal, and the continuation never refreshes or spends another normal action.", "",
        "## Bind Initiative After Hart/Weich", "",
        "After decline, Hart gives Bind Initiative to the original striker and Weich to the parrier. Initiative has no numeric modifier. If the holder lacks an authored continuation, only Disengage or pass is available; two consecutive passes end contact.", "",
        "## Fühlen F0/F1/F2", "",
        "F1 costs 1S once per bind, consumes no action or learned-chain entry, and reveals only Hart/Weich/Unknown. Because Spiritus has no assigned damage-equivalent, `best response` is reported under separate damage-maximizing and damage-per-Spiritus objectives plus Pareto frontiers. The symbolic threshold is retained rather than filled with a utility constant.", "",
        "Under G, pay when `min(q,1-q) * 4.5 * (Pboon-Pbane) > lambda * F-cost`. Under F, replace the probability difference with `Pboon`. Here `lambda` is the player's unassigned marginal value of one Spiritus. F0 has the same D/M spend as blind play and strictly improves information at every non-extreme prior, collapsing guessing. F2 improves damage but is never more efficient than the best blind choice in the tested grid (ties only at the exact 50/50 hard-failure boundary).", "",
        *fuhlen_rows, "",
        "Purchase rates are the fraction of the five controlled priors at which buying information is rational under the named deterministic objective. They are not behavioral probabilities. Under G/F1, only Skill 10 at Hart 50% ties on damage/S; higher Skills have 0% efficiency purchase. Under F/F1, the exact efficiency interval is Hart `1/3 <= q <= 2/3`, producing the 60% grid rate at 40/50/60%. Blind D/M switches at Hart 50%. Raw-damage choice buys Fühlen at every tested non-extreme prior for F1/F2 because no Spiritus value is included in that objective.", "",
        "## Duplieren", "",
        "Duplieren is the high Cut branch of one paired learned item. It requires Wide Crossing and the Bind Rejoinder, costs 2S, uses one chain entry, and deals normal damage. G maps Hart/Boon and Weich/Bane; F maps Hart/Boon and Weich/failure after spend. It adds no chip damage, response restriction, Open, damage modifier, or automatic retention.", "",
        "## Mutieren", "",
        "Mutieren is the low Thrust branch. It uses the same 2S/one-entry gate. G maps Weich/Boon and Hart/Bane; F maps Weich/Boon and Hart/failure after spend. It retains Crossing and sets point threat only through its winding transition; ordinary cleanup ends contact after resolution.", "",
        "## Graduated Wrong-Read vs Hard Failure", "",
        "G preserves an attack on a wrong read, but at Skill 18 the wrong Bane remains 81.0% successful and yields 3.645 expected damage. That is too reliable to carry the information game by itself. F makes wrong pressure a zero-output 2S spend, sharply raising information value. F is the stronger bounded information architecture, but its punishment and reserve effects require integrated testing before promotion.", "",
        "## Skill Sensitivity", "",
        "| Skill | Flat attack/parry | Boon attack/Hart parry | Bane attack | Boon-Bane | Boon/Bane | Correct damage | Wrong G damage | Wrong F |", "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in skill:
        lines.append(f"| {row['skill']} | {pct(row['flat_attack_success'])} | {pct(row['boon_attack_success'])} | {pct(row['bane_attack_success'])} | {pct(row['correct_minus_wrong_absolute'])} | {row['correct_over_wrong_ratio']:.2f}x | {num(row['expected_duplieren_damage_correct'])} | {num(row['expected_duplieren_damage_wrong_G'])} | 0.000 |")
    lines += [
        "", "The absolute correct/wrong swing peaks in the middle of the Skill curve and shrinks at high Skill. Relative to the correct Boon, Bane removes 66.7%, 57.1%, 46.2%, and only 18.2% of success at Skills 10/12/14/18.", "",
        "## Pressure-Prior Best Responses", "",
        "`Damage best` maximizes expected damage and breaks equal-damage ties toward lower spend. `Efficiency best` maximizes damage/S. Neither is asserted as the game's universal utility. D = blind Duplieren, M = blind Mutieren, Fü = buy F1, X = decline.", "",
        "| Model | Skill | Hart | D dmg/S | M dmg/S | Fü dmg/S | Best blind success/dmg/S | Fü success/dmg/S | Damage best | Efficiency best | Fü gain | Wrong probability / zero-output S |", "|---|---:|---:|---:|---:|---:|---|---|---|---|---:|---:|",
    ]
    abbrev = {"blind_duplieren": "D", "blind_mutieren": "M", "buy_fuhlen": "Fü", "decline": "X"}
    for row in matrix:
        alt = row["alternatives"]
        blind_name = max(("blind_duplieren", "blind_mutieren"), key=lambda name: alt[name]["expected_damage"])
        blind = alt[blind_name]
        info = alt["buy_fuhlen"]
        lines.append(
            f"| {row['model']} | {row['skill']} | {pct(row['hart_prior'])} | "
            f"{num(alt['blind_duplieren']['damage_per_spiritus'])} | {num(alt['blind_mutieren']['damage_per_spiritus'])} | {num(alt['buy_fuhlen']['damage_per_spiritus'])} | "
            f"{pct(blind['expected_attack_success'])}/{num(blind['expected_damage'])}/2 | {pct(info['expected_attack_success'])}/{num(info['expected_damage'])}/3 | "
            f"{'/'.join(abbrev[x] for x in row['best_expected_damage'])} | {'/'.join(abbrev[x] for x in row['best_damage_per_spiritus'])} | "
            f"{num(row['fuhlen_damage_gain_over_best_blind'])} | {pct(blind['wrong_read_probability'])}/{num(blind['wasted_spiritus_zero_output'])} |"
        )
    lines += [
        "", "For all tested non-extreme priors, F1 maximizes raw expected damage. Under G it is generally less Spiritus-efficient, especially as Skill rises. Under F it is efficiency-rational at Hart 40/50/60% and blind play is more efficient at 20/80%. These are deterministic objective-specific choices, not a claim that one objective is canonical.", "",
        "## Is Defender Hart/Weich Mixing Actually Evaluable?", "",
        "**DEFENDER PRESSURE MIXING NOT YET EVALUABLE.** Hart's Boon is quantified. Weich creates Bind Initiative, but no adjudicated defender-side continuation in this bounded scenario realizes its value. Importing W1/W2, inventing a Vor bonus, or assigning initiative a utility constant would fake the comparison. Observed/controlled pressure frequencies therefore do not establish a rational defender mix.", "",
        "## Counter-Wind", "",
        "Counter-Wind is legal only after eligible Duplieren, costs 1S and one chain entry, and uses the normal Longsword defence test. Success cancels, retains Crossing, transfers Bind Initiative, and deals no damage. Failure leaves Duplieren's modifier unchanged. It is not legal against Mutieren.", "",
        "| Skill | Normal defence | Correct D damage: none / Counter-Wind | Eligible Duplieren suppressed | Retained Crossing | Initiative transfer |", "|---:|---:|---:|---:|---:|---:|",
    ]
    for s in SKILLS:
        p = p_flat(s)
        no_cw = p_boon(s) * MEAN_DAMAGE
        with_cw = (1 - p) * no_cw
        lines.append(f"| {s} | {pct(p)} | {num(no_cw)} / {num(with_cw)} | {pct(p)} | {pct(p)} | {pct(p)} |")
    lines += [
        "", "With 0S, known Counter-Wind changes nothing. With 1S+ and forced declaration, incoming Duplieren damage is multiplied by the Counter-Wind failure rate. This is meaningful counterplay but very strong at Skill 18; without an integrated reserve loop it cannot be called mandatory or healthy merely from immediate damage reduction.", "",
        "## Response Economy", "",
        "```mermaid", "flowchart TD", "  A[\"Attacker spends action: attack succeeds\"] --> C[\"Defender declares Hart/Weich and spends action: Cross succeeds\"]", "  C --> R{\"Attacker Bind Rejoinder\"}", "  R -->|Decline Hart| IH[\"Striker Bind Initiative\"]", "  R -->|Decline Weich| IW[\"Parrier Bind Initiative\"]", "  R -->|Duplieren, 2S + 1 chain| CW{\"Scoped Counter-Wind legal?\"}", "  R -->|Mutieren, 2S + 1 chain| M[\"Low Thrust; winding transition; normal cleanup\"]", "  CW -->|No / fail| D[\"High Cut resolves; normal cleanup\"]", "  CW -->|Success, 1S + 1 chain| BI[\"Cancel; retain Crossing; parrier Bind Initiative\"]", "  IH --> P[\"Authored continuation, Disengage, or pass\"]", "  IW --> P", "  BI --> P", "```", "",
        "The parrier's ordinary Cross/Beat/Counter is unavailable against D/M because that action was spent on the initial Cross. This is action economy, not `RESTRICT_RESPONSE`. Counter-Wind is an explicit no-additional-action bind counter. No branch refreshes either fighter's normal action.", "",
        "| Branch state | Normal actions spent | Spiritus delta | Chain delta | Contact / measure | Pressure / point | Bind Initiative | Next declarations |", "|---|---|---|---|---|---|---|---|", "| H1 Cross succeeds | attacker yes; parrier yes | 0 / 0 | 0 / 0 | Crossing / Wide | authored Hart/Weich; no automatic point | none during Rejoinder | D, M, decline |", "| Decline Hart | unchanged | 0 / 0 | 0 / 0 | Crossing / Wide | Hart; point unchanged | striker | authored bind continuation, Disengage, pass |", "| Decline Weich | unchanged | 0 / 0 | 0 / 0 | Crossing / Wide | Weich; point unchanged | parrier | authored bind continuation, Disengage, pass |", "| Duplieren resolves | no new action | attacker -2S | attacker +1 | normal cleanup -> none / Wide | pressure clears; point unchanged | none | exchange aftermath |", "| Mutieren resolves | no new action | attacker -2S | attacker +1 | retained during wind, then none / Wide | pressure clears; attacker point threatening | none | exchange aftermath |", "| Counter-Wind succeeds | no new action | defender -1S in addition | defender +1 | Crossing retained / Wide | pressure preserved; point unchanged | defender | authored bind continuation, Disengage, pass |", "| Counter-Wind fails | no new action | defender -1S in addition | defender +1 | Crossing until D resolves / Wide | pressure preserved until cleanup | none | resolve unchanged D |", "",
        "## Geometry / Largo-Stretto Boundary", "",
        "Measure, per-fighter contact zone, pressure, point threat, and Crossing remain independent. Middle contact stays compatible with Wide; low guard does not imply Close. No generic 1S Wide-to-Close purchase exists. T1 remains the distinct authored Tutta transition.", "",
        "## Spiritus and Chain Pressure", "",
        "Basic Cross is 0 entries; Fühlen 0; one D/M branch 1; Counter-Wind 1. The fourth learned Play remains illegal. At 2S, D/M buys correct-read Boon plus a new attack after the initiating action is already spent. That action compression is its strongest price justification. At 1S its correct damage/S doubles, making it conspicuously favorable beside 1S Nachreisen; at 2S it sits nearer C2's compound benchmark, though C2 also cancels and D/M instead occupies post-action continuation timing.", "",
        "## R0 vs H1 Architecture Comparison", "",
        "| Dimension | R0 Favored/Unfavored | H1 Hart/Weich |", "|---|---|---|", "| Historical intelligibility | abstract roll-derived blade relation | authored pressure directly teaches Hart/Weich |", "| Hidden axes | hidden categorical relation; pressure separate/usually unknown | hidden authored pressure; Favored/Unfavored absent for H1 Basic Cross |", "| Extra rolls | none | none |", "| Decisions | roll outcome is not chosen | parrier chooses Hart/Weich; striker may read/guess |", "| Fühlen | free passive relation visibility | priced pressure information candidate |", "| Wrong-read risk | hidden-prerequisite risk in Ort/W1 | explicit D/M Bane or failure |", "| Policy dependence | relation generated mechanically | defender mixing depends on unrealized initiative value |", "| State authoring | comparable rolls | declaration that becomes state only on success |", "| Explanation | lower successful roll is Favored | Hart secures Cross; Weich seeks initiative |", "| Extensibility | supports current Ort/Winden relation | natural axis for D/M and future audited bind lessons |", "| Zornhau compatibility | current local Favored/Ort/Winden sequence | left separate; no forced symmetry |", "",
        "H1 is clearer historically and creates more authored decisions, but it currently leaves a one-sided defensive trade. It should not supersede R0 until Weich/Bind Initiative has actual defender-side consequences.", "",
        "## Zornhau Compatibility", "",
        "Zornhau remains on its threatening-point Favored/Unfavored Ort/Winden candidate sequence. H1 does not rewrite it. If H1 is later adopted, the Project must decide whether Zornhau translates to Hart/Weich or retains a local relation; this experiment provides no basis to force either answer.", "",
        "## Remaining Historical / Mechanical Gaps", "",
        "Duplieren/Mutieren and the exact counter-winding need item-level locators in durable records. Weich needs one actual defender-side Bind-Initiative consumer. The current response economy after an action-spent Cross is intentionally sparse. Integrated reserve competition is needed to judge F1, 2S D/M, and 1S Counter-Wind. No generic Leverage, Largo-to-Stretto purchase, universal Winden, Zucken, or other deferred action was added.", "",
        "## Project Recommendation", "",
        "Keep R0 governing-provisional. Retain H1 plus the narrow Bind Rejoinder as promising candidates. Prefer hard failure over Bane for the next controlled test because Bane is too weak at Skill 18 and F1 otherwise loses practical information value. Keep F1 and 2S D/M as the next-test prices. Keep Counter-Wind candidate-only: it is clean but may suppress Duplieren too strongly at high Skill. Do not add Leverage.", "",
        "## Exact Next Milestone", "",
        "Run **another bind-repertoire increment**, not promotion, full-duel cleanup, or Named Guard v0.2: perform an item-level audit and implement one narrow defender-side continuation that consumes Weich-earned Bind Initiative. Zucken is a plausible research target only if exact evidence supports the scoped timing; do not add generic Zucken by inference. Then rerun H1 with actual defender-side consequences and integrated Spiritus opportunity costs.", "",
        "## Required Project Decision Table", "",
        "| Question | Candidate A | Candidate B | Result | Recommendation |", "|---|---|---|---|---|", "| Ordinary bind information | R0 Favored/Unfavored | H1 Hart/Weich | H1 clearer; Weich value incomplete | keep R0; continue H1 |", "| Fühlen price | 0S | 1S | 0S collapses guessing; 1S creates trade under F | F1 next-test candidate |", "| Fühlen high-price control | 1S | 2S | F2 never wins efficiency in grid | do not advance F2 |", "| Wrong pressure | Bane | failure | Bane remains 81% at Skill 18 | F for next integrated test |", "| D/M price | 1S | 2S | 1S highly efficient; 2S reflects action compression | retain 2S candidate |", "| Attacker timing | no Rejoinder | narrow Bind Rejoinder | clean, no second action leakage | retain candidate |", "| Winden response | none | scoped Counter-Wind vs Duplieren | clean but 50-90% suppression | retain only for integrated test |", "",
        "## Final Project-Review Questions", "",
        "1. **Yes.** The existing governing engine remained behaviorally unchanged.", "2. **Yes.** H1 authors Hart/Weich without random generation.", "3. **Probably yes in the bounded repertoire.** Hart has quantified defence; Weich's payoff is unrealized.", "4. **No.** Weich lacks enough rules-real value here.", "5. **Not evaluable;** more defender-side bind repertoire is required.", "6. **Yes.** The narrow Rejoinder cleanly supplies D/M timing.", "7. **No.** It creates no normal-action refresh or second action.", "8. **Yes.** Duplieren is high Cut/Hart; Mutieren is winding low Thrust/Weich.", "9. **Yes:** Hart -> Duplieren; Weich -> Mutieren.", "10. **No.** Bane still succeeds 81% at Skill 18.", "11. **For this information test, yes provisionally;** hard failure needs reserve testing.", "12. **Neither categorically.** F makes F1 damage-optimal centrally; resource objectives preserve blind play at outer priors.", "13. **G makes paid Fühlen close to irrelevant at high Skill under efficiency; not under raw damage maximization.**", "14. **Only with F.** F1 is the healthiest tested price across the grid when wrong reads fail.", "15. **Yes.** F0 collapses guessing at equal D/M spend.", "16. **For Spiritus efficiency, effectively yes.** F2 never beats blind play in the tested grid.", "17. **Plausibly.** 2S is justified primarily by post-action attack compression, but is not promoted.", "18. **It provides useful counterplay but may over-suppress Duplieren at high Skill.**", "19. **No.** Existing CANCEL, RETAIN, SET, normal test, timing, and chain operations suffice.", "20. **Yes.** Generic Leverage remains rejected/deferred.", "21. **Yes.** Generic Largo-to-Stretto spending remains rejected/deferred.", "22. **Not yet.** H1 is more intelligible but not a complete rational defender architecture.", "23. **The missing mechanic is one actual defender-side continuation that converts Weich-earned Bind Initiative into consequences.**", "24. **Keep H1 isolated; do not replace or coexist in governing play yet.**", "25. **One item-level-audited defender-side Weich/initiative continuation; research Zucken only if supported.**", "26. **Another bind repertoire increment.**", "", "STOP for Project adjudication. No candidate is promoted.", "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    results = run_all()
    if not args.no_write:
        RESULTS_PATH.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        REPORT_PATH.write_text(build_report(results), encoding="utf-8")
    print(json.dumps({"deterministic": results["deterministic"], "matrix_rows": len(results["pressure_read_matrix"]), "report": str(REPORT_PATH)}, indent=2))


if __name__ == "__main__":
    main()

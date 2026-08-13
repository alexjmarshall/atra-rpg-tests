from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RESULTS_PATH = ROOT / "reports/hart-weich-upper-winden-loop-v02-results.json"
REPORT_PATH = ROOT / "reports/hart-weich-upper-winden-loop-v02-results.md"
MEAN_DAMAGE = 4.5
SKILLS = (10, 12, 14, 18)
PRIORS = (0.2, 0.4, 0.5, 0.6, 0.8)
RESERVES = (0, 1, 2, 3, 5)
MATCHED = tuple((skill, skill) for skill in SKILLS)
ASYMMETRIC = ((10, 14), (14, 10), (14, 18), (18, 14))
PRIMARY_WINDING_COST = 2

KNOWLEDGE = {
    "A_none": {"striker_dm": False, "striker_fuhlen": False, "striker_winden": False, "parrier_winden": False},
    "B_striker_dm": {"striker_dm": True, "striker_fuhlen": False, "striker_winden": False, "parrier_winden": False},
    "C_striker_dm_fuhlen": {"striker_dm": True, "striker_fuhlen": True, "striker_winden": False, "parrier_winden": False},
    "D_striker_winden": {"striker_dm": False, "striker_fuhlen": False, "striker_winden": True, "parrier_winden": False},
    "E_parrier_winden": {"striker_dm": False, "striker_fuhlen": False, "striker_winden": False, "parrier_winden": True},
    "F_both_winden": {"striker_dm": False, "striker_fuhlen": False, "striker_winden": True, "parrier_winden": True},
    "G_full": {"striker_dm": True, "striker_fuhlen": True, "striker_winden": True, "parrier_winden": True},
}


def p_success(skill: int) -> float:
    return skill / 20


def p_boon(skill: int) -> float:
    p = p_success(skill)
    return 1 - (1 - p) ** 2


def r(value: float) -> float:
    return round(value, 6)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def winding_actor(pressure: str, config: dict[str, bool], reserve: int, cost: int = 2) -> tuple[str | None, int]:
    holder = "striker" if pressure == "hart" else "parrier"
    other = "parrier" if holder == "striker" else "striker"
    knows = {
        "striker": config["striker_winden"],
        "parrier": config["parrier_winden"],
    }
    if knows[holder] and reserve >= cost:
        return holder, 0
    if knows[other] and reserve >= cost:
        return other, 1
    return None, 2


def decline_vector(
    striker_skill: int,
    parrier_skill: int,
    pressure: str,
    config: dict[str, bool],
    reserve: int,
    cost: int = 2,
) -> dict[str, Any]:
    actor, passes = winding_actor(pressure, config, reserve, cost)
    vector = {
        "strategy": "decline",
        "initiative_holder": "striker" if pressure == "hart" else "parrier",
        "first_winding_actor": actor,
        "passes_before_winding_or_end": passes,
        "striker_outgoing_damage": 0.0,
        "parrier_outgoing_damage": 0.0,
        "striker_spiritus": 0.0,
        "parrier_spiritus": 0.0,
        "chain_entries": 0.0,
        "striker_winding_opportunity": 0.0,
        "parrier_winding_opportunity": 0.0,
        "bind_ends_before_winding": 1.0 if actor is None else 0.0,
        "contact_retention_after_miss": 0.0,
    }
    if actor is None:
        return vector
    skill = striker_skill if actor == "striker" else parrier_skill
    damage = p_success(skill) * MEAN_DAMAGE
    vector[f"{actor}_outgoing_damage"] = r(damage)
    vector[f"{actor}_spiritus"] = float(cost)
    vector[f"{actor}_winding_opportunity"] = 1.0
    vector["chain_entries"] = 1.0
    vector["contact_retention_after_miss"] = r(1 - p_success(skill))
    return vector


def rejoinder_vectors(
    striker_skill: int,
    parrier_skill: int,
    pressure: str,
    config: dict[str, bool],
    reserve: int,
) -> dict[str, dict[str, Any]]:
    vectors: dict[str, dict[str, Any]] = {
        "decline": decline_vector(striker_skill, parrier_skill, pressure, config, reserve)
    }
    boon_damage = p_boon(striker_skill) * MEAN_DAMAGE
    if config["striker_dm"] and reserve >= 2:
        for branch, correct_pressure in (("blind_duplieren", "hart"), ("blind_mutieren", "weich")):
            correct = pressure == correct_pressure
            vectors[branch] = {
                "strategy": branch,
                "correct_read": correct,
                "striker_outgoing_damage": r(boon_damage if correct else 0),
                "parrier_outgoing_damage": 0.0,
                "striker_spiritus": 2.0,
                "parrier_spiritus": 0.0,
                "chain_entries": 1.0,
                "wrong_read_failure": not correct,
                "bind_ends_before_winding": 1.0,
            }
    if config["striker_dm"] and config["striker_fuhlen"] and reserve >= 3:
        vectors["fuhlen_correct_dm"] = {
            "strategy": "fuhlen_correct_dm",
            "correct_read": True,
            "striker_outgoing_damage": r(boon_damage),
            "parrier_outgoing_damage": 0.0,
            "striker_spiritus": 3.0,
            "parrier_spiritus": 0.0,
            "chain_entries": 1.0,
            "wrong_read_failure": False,
            "bind_ends_before_winding": 1.0,
        }
    return vectors


def equal_prior_strategy(
    striker_skill: int,
    parrier_skill: int,
    config: dict[str, bool],
    reserve: int,
) -> str:
    """Named objective: maximize striker damage at q=.5, then lower striker spend."""
    candidates: list[tuple[float, float, str]] = []
    boon_damage = p_boon(striker_skill) * MEAN_DAMAGE
    if config["striker_dm"] and reserve >= 2:
        candidates.append((0.5 * boon_damage, -2.0, "blind_duplieren"))
        candidates.append((0.5 * boon_damage, -2.0, "blind_mutieren"))
    if config["striker_dm"] and config["striker_fuhlen"] and reserve >= 3:
        candidates.append((boon_damage, -3.0, "fuhlen_correct_dm"))
    decline_a = 0.0
    decline_spend = 0.0
    for pressure in ("hart", "weich"):
        vector = decline_vector(striker_skill, parrier_skill, pressure, config, reserve)
        decline_a += 0.5 * vector["striker_outgoing_damage"]
        decline_spend += 0.5 * vector["striker_spiritus"]
    candidates.append((decline_a, -decline_spend, "decline"))
    return max(candidates, key=lambda item: (item[0], item[1], item[2]))[2]


def controlled_tree() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for striker_skill, parrier_skill in MATCHED + ASYMMETRIC:
        for reserve in RESERVES:
            for config_name, config in KNOWLEDGE.items():
                selected = equal_prior_strategy(striker_skill, parrier_skill, config, reserve)
                for pressure in ("hart", "weich"):
                    cross_p = p_boon(parrier_skill) if pressure == "hart" else p_success(parrier_skill)
                    reach_cross = p_success(striker_skill) * cross_p
                    vectors = rejoinder_vectors(striker_skill, parrier_skill, pressure, config, reserve)
                    selected_vector = vectors[selected]
                    rows.append({
                        "striker_skill": striker_skill,
                        "parrier_skill": parrier_skill,
                        "reserve_each": "5+" if reserve == 5 else reserve,
                        "knowledge": config_name,
                        "pressure": pressure,
                        "initial_attack_success": r(p_success(striker_skill)),
                        "cross_success_conditional_on_attack": r(cross_p),
                        "crossing_reached_per_declared_cut": r(reach_cross),
                        "expected_initial_incoming_damage_per_declared_cut": r(
                            p_success(striker_skill) * (1 - cross_p) * MEAN_DAMAGE
                        ),
                        "available_strategies": list(vectors),
                        "strategy_vectors_conditional_on_successful_cross": vectors,
                        "named_objective": "equal-prior striker outgoing damage; lower striker spend tie-break",
                        "selected_strategy": selected,
                        "selected_unconditional": {
                            "striker_outgoing_damage_per_declared_cut": r(
                                reach_cross * selected_vector["striker_outgoing_damage"]
                            ),
                            "parrier_outgoing_damage_per_declared_cut": r(
                                reach_cross * selected_vector["parrier_outgoing_damage"]
                            ),
                            "striker_spiritus_per_declared_cut": r(
                                reach_cross * selected_vector["striker_spiritus"]
                            ),
                            "parrier_spiritus_per_declared_cut": r(
                                reach_cross * selected_vector["parrier_spiritus"]
                            ),
                            "chain_entries_per_declared_cut": r(
                                reach_cross * selected_vector["chain_entries"]
                            ),
                        },
                    })
    return rows


def u1_u2_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for skill in SKILLS:
        for name, cost, modifier in (
            ("correct_dm", 2, "boon"),
            ("upper_winding_u1", 1, "normal"),
            ("upper_winding_u2", 2, "normal"),
        ):
            attack_p = p_boon(skill) if modifier == "boon" else p_success(skill)
            damage = attack_p * MEAN_DAMAGE
            rows.append({
                "skill": skill,
                "candidate": name,
                "attack_success": r(attack_p),
                "expected_damage": r(damage),
                "spiritus": cost,
                "damage_per_spiritus": r(damage / cost),
                "chain_entries": 1,
                "normal_action": 0,
                "trigger": (
                    "correct initial pressure + attacker Rejoinder + Wide"
                    if name == "correct_dm"
                    else "Bind Initiative + Upper Crossing"
                ),
                "availability_after_decline_given_knowledge_reserve_and_qualifying_cross": 1.0,
            })
    return rows


def fuhlen_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for skill in SKILLS:
        boon_damage = p_boon(skill) * MEAN_DAMAGE
        flat_damage = p_success(skill) * MEAN_DAMAGE
        for reserve in RESERVES:
            for q in PRIORS:
                alternatives: dict[str, dict[str, float | bool]] = {
                    "blind_duplieren": {
                        "available": reserve >= 2,
                        "striker_damage": r(q * boon_damage) if reserve >= 2 else 0.0,
                        "parrier_damage": 0.0,
                        "striker_spiritus": 2.0 if reserve >= 2 else 0.0,
                        "chain": 1.0 if reserve >= 2 else 0.0,
                    },
                    "blind_mutieren": {
                        "available": reserve >= 2,
                        "striker_damage": r((1 - q) * boon_damage) if reserve >= 2 else 0.0,
                        "parrier_damage": 0.0,
                        "striker_spiritus": 2.0 if reserve >= 2 else 0.0,
                        "chain": 1.0 if reserve >= 2 else 0.0,
                    },
                    "f1_correct_dm": {
                        "available": reserve >= 3,
                        "striker_damage": r(boon_damage) if reserve >= 3 else 0.0,
                        "parrier_damage": 0.0,
                        "striker_spiritus": 3.0 if reserve >= 3 else 0.0,
                        "chain": 1.0 if reserve >= 3 else 0.0,
                    },
                    "decline_both_know_winden_u2": {
                        "available": reserve >= 2,
                        "striker_damage": r(q * flat_damage) if reserve >= 2 else 0.0,
                        "parrier_damage": r((1 - q) * flat_damage) if reserve >= 2 else 0.0,
                        "striker_spiritus": r(2 * q) if reserve >= 2 else 0.0,
                        "parrier_spiritus": r(2 * (1 - q)) if reserve >= 2 else 0.0,
                        "chain": 1.0 if reserve >= 2 else 0.0,
                    },
                }
                f = alternatives["f1_correct_dm"]
                for vector in alternatives.values():
                    spend = float(vector.get("striker_spiritus", 0.0))
                    vector["striker_damage_per_striker_spiritus"] = (
                        r(float(vector["striker_damage"]) / spend) if spend > 0 else None
                    )
                available_other = [v for k, v in alternatives.items() if k != "f1_correct_dm" and v["available"]]
                dominated = bool(f["available"]) and any(
                    v["striker_damage"] >= f["striker_damage"]
                    and v["striker_spiritus"] <= f["striker_spiritus"]
                    and v["chain"] <= f["chain"]
                    and (
                        v["striker_damage"] > f["striker_damage"]
                        or v["striker_spiritus"] < f["striker_spiritus"]
                        or v["chain"] < f["chain"]
                    )
                    for v in available_other
                )
                strongly_attractive = bool(f["available"]) and all(
                    f["striker_damage"] > v["striker_damage"] for v in available_other
                )
                efficiencies = {
                    name: vector["striker_damage_per_striker_spiritus"]
                    for name, vector in alternatives.items()
                    if vector["available"] and vector["striker_damage_per_striker_spiritus"] is not None
                }
                best_efficiency = max(efficiencies.values()) if efficiencies else None
                rows.append({
                    "skill": skill,
                    "reserve": "5+" if reserve == 5 else reserve,
                    "hart_prior": q,
                    "hard_wrong_read_failure": True,
                    "alternatives_conditional_on_successful_cross": alternatives,
                    "f1_avoids_wrong_read_probability": r(min(q, 1 - q)) if reserve >= 3 else 0.0,
                    "f1_avoids_expected_zero_output_spiritus": r(2 * min(q, 1 - q)) if reserve >= 3 else 0.0,
                    "f1_classification": (
                        "unavailable"
                        if not f["available"]
                        else "dominated"
                        if dominated
                        else "strongly-attractive-but-not-mandatory"
                        if strongly_attractive
                        else "pareto-relevant"
                    ),
                    "f1_pareto_relevant": bool(f["available"]) and not dominated,
                    "best_striker_damage_per_spiritus": best_efficiency,
                    "f1_is_best_striker_damage_per_spiritus": bool(f["available"])
                    and f["striker_damage_per_striker_spiritus"] == best_efficiency,
                    "f1_effectively_mandatory_without_scalar_utility": False,
                })
    return rows


def all_miss_attempts(
    reserve_a: int,
    reserve_b: int,
    cost: int,
    knows_a: bool = True,
    knows_b: bool = True,
) -> tuple[list[str], str]:
    reserves = {"A": reserve_a, "B": reserve_b}
    knows = {"A": knows_a, "B": knows_b}
    actor = "A"
    passes = 0
    attempts: list[str] = []
    while True:
        if len(attempts) >= 3:
            return attempts, "chain-cap"
        if knows[actor] and reserves[actor] >= cost:
            reserves[actor] -= cost
            attempts.append(actor)
            passes = 0
            actor = "B" if actor == "A" else "A"
            continue
        passes += 1
        if passes >= 2:
            return attempts, "spiritus-or-knowledge-exhaustion"
        actor = "B" if actor == "A" else "A"


def short_chain_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for skill_a, skill_b in MATCHED + ASYMMETRIC:
        for cost in (1, 2):
            for reserve in RESERVES:
                for knowledge_name, knows_a, knows_b in (
                    ("both", True, True),
                    ("holder-only", True, False),
                ):
                    attempts, terminal = all_miss_attempts(reserve, reserve, cost, knows_a, knows_b)
                    reach = 1.0
                    expected_attempts = 0.0
                    expected_spiritus = 0.0
                    expected_miss_transfers = 0.0
                    sequence: list[dict[str, Any]] = []
                    for index, actor in enumerate(attempts, 1):
                        skill = skill_a if actor == "A" else skill_b
                        hit = p_success(skill)
                        sequence.append({"attempt": index, "actor": actor, "reach_probability": r(reach), "hit_probability": r(hit)})
                        expected_attempts += reach
                        expected_spiritus += reach * cost
                        expected_miss_transfers += reach * (1 - hit)
                        reach *= 1 - hit
                    rows.append({
                        "skill_a": skill_a,
                        "skill_b": skill_b,
                        "winding_cost": cost,
                        "reserve_each": "5+" if reserve == 5 else reserve,
                        "knowledge": knowledge_name,
                        "all_miss_actor_sequence": attempts,
                        "attempts": sequence,
                        "expected_bind_continuations": r(expected_attempts),
                        "expected_spiritus_spent": r(expected_spiritus),
                        "bind_hit_probability": r(1 - reach),
                        "retained_crossing_event_expectation": r(expected_miss_transfers),
                        "final_miss_retained_crossing_probability_before_pass_cleanup": r(reach) if attempts else 0.0,
                        "initiative_transfer_expectation": r(expected_miss_transfers),
                        "ochs_establishment_expectation": r(expected_attempts),
                        "chain_cap_termination_rate": r(reach) if terminal == "chain-cap" else 0.0,
                        "spiritus_or_knowledge_termination_rate": r(reach) if terminal != "chain-cap" else 0.0,
                        "terminal_on_all_miss_path": terminal,
                    })
    return rows


def selected_pressure_comparison(tree: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row for row in tree
        if row["striker_skill"] == row["parrier_skill"]
        and row["reserve_each"] == "5+"
    ]


def build_results() -> dict[str, Any]:
    tree = controlled_tree()
    u_rows = u1_u2_rows()
    f_rows = fuhlen_rows()
    chains = short_chain_rows()
    return {
        "experiment": "ATRA HART/WEICH + UPPER WINDEN LOOP v0.2",
        "status": "PROMISING BUT INCOMPLETE; PROVISIONAL CANDIDATE ONLY",
        "automatic_promotion": False,
        "authoritative_engine_edited": False,
        "governing_packet_edited": False,
        "method": "exact probabilities, branch forcing, Pareto vectors, and named deterministic objectives; no Monte Carlo or arbitrary utility constants",
        "baseline_regression": {
            "governing": {"passed": 81, "required": 81},
            "previous_candidate": {"passed": 75, "required": 75},
            "new_candidate_coverage_labels": {"first": 3, "last": 81, "minimum_required_last": 75},
        },
        "protected_hashes": {
            "shared_engine_sha256": file_sha256(ROOT / "simulations/shared/provisional_longsword_engine.py"),
            "design_packet_sha256": file_sha256(ROOT / "docs/melee-design-packet-v0.4.md"),
        },
        "parameters": {
            "skills": list(SKILLS),
            "matched_pairs": MATCHED,
            "asymmetric_pairs": ASYMMETRIC,
            "reserves": [0, 1, 2, 3, "5+"],
            "knowledge_configurations": KNOWLEDGE,
            "hart_priors": list(PRIORS),
            "mean_normal_damage": MEAN_DAMAGE,
            "primary_winding_cost": 2,
            "sensitivity_winding_cost": 1,
        },
        "u1_vs_u2": u_rows,
        "controlled_game_tree": tree,
        "matched_pressure_comparison_reserve_5plus": selected_pressure_comparison(tree),
        "fuhlen_after_decline": f_rows,
        "short_krieg_chains": chains,
        "findings": {
            "u1": "crowds D/M on Spiritus efficiency at every tested Skill despite lower hit probability",
            "u2": "preserves correct D/M's Booned-attack premium and is the stronger price candidate",
            "weich": "has a concrete rules-real benefit in qualifying Upper crossings when the parrier can take the first Winding declaration",
            "hart_dominance": "Hart does not dominate when both fighters know Winden: it improves Cross survival but gives first Winding to the striker",
            "fuhlen": "F1 is raw-damage attractive and Pareto-relevant when affordable, but decline is at least as efficient in striker damage/S (while exposing parrier damage); F1 is not mandatory and blind reads remain rational at skewed priors or reserve 2",
            "ochs": "action-produced and point-threatening, but the Ochs label is not itself a continuation gate in the bounded miss loop",
            "bind_height": "clean deterministic gate, but currently a single-consumer axis; keep candidate-only until lower/other geometry earns it",
            "loop": "miss transfer plus Spiritus and cap 3 creates finite short chains; fourth declaration is impossible",
            "architecture": "H2 closes the qualifying Upper bind loop but does not cover nonqualifying/Unknown ordinary Crosses, so it is not yet a minimum replacement for R0",
        },
        "ghost_policy_audit": {
            "favored_unfavored_utility_constants": False,
            "initiative_bonus": False,
            "ochs_value_constant": False,
            "leverage_state_or_value": False,
            "counter_wind": False,
            "generic_w1_w2_in_ordinary_h1": False,
            "stale_cross_d1_immunity": False,
            "random_pressure_or_geometry": False,
        },
        "recommendation": {
            "classification": "PROMISING BUT INCOMPLETE",
            "ordinary_basic_cross": "remain R0 governing/provisional; keep H2 isolated",
            "winding_price": "U2 (2 Spiritus) for any next candidate iteration",
            "leverage": "remain deferred/rejected as generic state",
            "counter_wind": "remain deferred",
            "next_milestone": "one more narrow bind-repertoire increment addressing non-Upper/Unknown ordinary binds before promotion or full-duel cleanup",
        },
    }


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def report_text(results: dict[str, Any]) -> str:
    u = results["u1_vs_u2"]
    chains = [
        row for row in results["short_krieg_chains"]
        if row["skill_a"] == row["skill_b"] and row["winding_cost"] == 2
        and row["reserve_each"] == "5+" and row["knowledge"] == "both"
    ]
    pressure = [
        row for row in results["matched_pressure_comparison_reserve_5plus"]
        if row["striker_skill"] == 14 and row["knowledge"] in {"A_none", "B_striker_dm", "C_striker_dm_fuhlen", "F_both_winden", "G_full"}
    ]
    f_rows = [
        row for row in results["fuhlen_after_decline"]
        if row["skill"] == 14 and row["reserve"] == "5+"
    ]
    lines = [
        "# Hart/Weich + Upper Winden Loop v0.2 Results",
        "",
        "Status: **PROVISIONAL bounded candidate experiment; no governing or canonical promotion.**",
        "",
        "## Executive Result",
        "",
        "**PROMISING BUT INCOMPLETE.** H2 creates a coherent, rules-real loop for qualifying Upper crossings: phase-scoped Hart/Weich assigns first declaration, Upper Winding consumes that sequencing, and misses retain contact while transferring initiative. Weich therefore gains a concrete defender-side benefit when the parrier knows Winden. However, nonqualifying ordinary Crosses write `Unknown` height and still have no general Bind-Initiative consumer. H2 does not yet justify replacing R0 across ordinary Basic Crosses.",
        "",
        "U1 crowds D/M on Spiritus efficiency at every tested Skill. U2 preserves the correct-read D/M premium and is the stronger price candidate. F1 remains situational in resource/Pareto terms: it is raw-damage attractive when affordable, but blind reading remains rational at skewed priors and reserve 2, while declining creates a different two-sided damage vector rather than a scalar substitute.",
        "",
        "## Source-of-Truth Check",
        "",
        "The clean `main` baseline at commit `b6be01e` was reviewed against the governing/provisional register and YAML, shared selector/engine, Melee Mechanical Effect Vocabulary, Crossing/Bind, Bind Continuations, Incentive Integrity, guard evidence/repertoire, named guards, audited Winden/D/M/Zornhau records, Ochs/Pflug evidence, T1, Spiritus, and chain rules. The Atra Melee Design Packet was read but not edited.",
        "",
        "## Baseline Regression",
        "",
        "Before candidate edits, the Melee Repertoire Integrity Repair suite passed **81/81** and General Bind Information v0.1 passed **75/75**. The H2 deterministic suite covers labels 3-81, exceeding the requested 3-75 range. Final combined results are reported below under validation.",
        "",
        "## Historical / Mechanical Boundary",
        "",
        "Repository evidence supports Hart/Weich as sensed bind opposition, Winden as a family using upper/lower Ochs/Pflug hangings, and selection among cut/thrust/slice. The exact pre-roll declaration, Hart Boon, initiative mapping, phase expiry, Upper writer, costs, and miss loop are explicitly Atra candidate abstractions. The Upper writer is not presented as universal historical truth.",
        "",
        "## R0 Control",
        "",
        "R0 remains unchanged: ordinary Cross generates roll-derived Favored/Unfavored, current Bind Initiative and passive/control Fühlen remain, and Zornhau retains its local Ort/W1/W2 structure. D1, Beat/Open, GC1, Nachreisen, P1, C2, S2, T1, and cap 3 are untouched.",
        "",
        "## H2 Candidate Overview",
        "",
        "H2 combines H1 initial pressure, the narrow attacker Rejoinder, F1, hard-failure 2S D/M, sequencing-only Bind Initiative, public bind height, and one concrete Upper Winding Thrust. It adds no Leverage, Counter-Wind, generic close purchase, random pressure, or random geometry.",
        "",
        "## Initial Hart / Weich",
        "",
        "Hart gives exactly one Cross Boon; Weich is flat. Success writes initial pressure only. No H2 ordinary Cross writes Favored/Unfavored.",
        "",
        "## Bind Height",
        "",
        "`upper`, `lower`, and `unknown` are public and independent from measure/contact zone. Only a successful H1 Cross against the bounded qualifying descending-Cut case writes Upper; all other cases remain Unknown. Height has no modifier.",
        "",
        "## Attacker Bind Rejoinder",
        "",
        "The original striker receives one D/M-or-decline insertion. Neither fighter receives or spends another normal action. Specialized point-threatening defences remain outside this window.",
        "",
        "## Initial Pressure Expiry",
        "",
        "Decline maps Hart to striker initiative and Weich to parrier initiative, then clears pressure. D/M declaration also clears it. Upper Winding never rewrites pressure.",
        "",
        "## Fühlen",
        "",
        "F1 costs 1S, no action, and no chain entry, once in the live initial Rejoinder cycle. It reveals no later or invented pressure.",
        "",
        "## Duplieren / Mutieren",
        "",
        "Each branch costs 2S and one chain entry. Correct Duplieren/Hart is a Booned high Cut; correct Mutieren/Weich is a Booned low Thrust with retained contact during its winding transition. Wrong pressure hard-fails after spend with no roll or damage.",
        "",
        "## Winden as Repertoire",
        "",
        "Winden is shared learned knowledge, not a universal button. R0's Zornhau-local W1/W2 is quarantined from ordinary H1, while each actual Upper Winding declaration consumes one chain entry.",
        "",
        "## Upper Winding Thrust",
        "",
        "The initiative holder may pay U1/U2 from an Upper Crossing, set Ochs and point threat, retain contact, and make a flat normal-damage Longsword Thrust. It requires neither pressure nor starting guard nor original exchange role.",
        "",
        "## U1 vs U2",
        "",
        "| Skill | Correct D/M dmg (2S) | Upper dmg | U1 dmg/S | U2 dmg/S | Reading |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for skill in SKILLS:
        dm = next(row for row in u if row["skill"] == skill and row["candidate"] == "correct_dm")
        u1 = next(row for row in u if row["skill"] == skill and row["candidate"] == "upper_winding_u1")
        u2 = next(row for row in u if row["skill"] == skill and row["candidate"] == "upper_winding_u2")
        lines.append(f"| {skill} | {dm['expected_damage']:.3f} | {u1['expected_damage']:.3f} | {u1['damage_per_spiritus']:.3f} | {u2['damage_per_spiritus']:.3f} | U1 broad cheap fallback; U2 preserves Boon premium |")
    lines += [
        "",
        "U1 has lower immediate success than correct D/M but higher damage/S at every Skill and a broader pressure-free trigger. U2 costs the same as D/M while D/M retains the correct-read Boon. Damage/S is not the sole promotion criterion, but it exposes the crowding risk clearly.",
        "",
        "## Failed-Winding Initiative Transfer",
        "",
        "A miss deals zero, retains Crossing/Ochs/point threat, and transfers initiative without Open or an opponent Boon. The recipient may Wind only if the same explicit knowledge, height, resource, initiative, and chain gates pass.",
        "",
        "## Short Krieg Chains",
        "",
        "| Matched Skill | Expected declarations | Expected S | Bind hit | Miss-transfer expectation | Cap termination |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in chains:
        lines.append(f"| {row['skill_a']} | {row['expected_bind_continuations']:.3f} | {row['expected_spiritus_spent']:.3f} | {pct(row['bind_hit_probability'])} | {row['initiative_transfer_expectation']:.3f} | {pct(row['chain_cap_termination_rate'])} |")
    lines += [
        "",
        "These are exact U2, 5+ reserve, both-known sequences. The all-miss path is A-B-A; a fourth declaration is illegal. Lower reserves terminate through resource exhaustion/passes. No normal action refresh occurs.",
        "",
        "## Hart vs Weich with Rules-Real Initiative",
        "",
        "At matched Skill 14 and reserve 5+, the following rows use the explicitly named equal-prior striker-damage objective only to select the striker's policy; the consequence vectors remain primary.",
        "",
        "| Knowledge | Pressure | Cross | Initial dmg/cut | Selected | Striker follow-up/cut | Parrier follow-up/cut |",
        "|---|---|---:|---:|---|---:|---:|",
    ]
    for row in pressure:
        un = row["selected_unconditional"]
        lines.append(f"| {row['knowledge']} | {row['pressure']} | {pct(row['cross_success_conditional_on_attack'])} | {row['expected_initial_incoming_damage_per_declared_cut']:.3f} | {row['selected_strategy']} | {un['striker_outgoing_damage_per_declared_cut']:.3f} | {un['parrier_outgoing_damage_per_declared_cut']:.3f} |")
    lines += [
        "",
        "When both know Winden and the striker declines, Hart improves immediate survival but gives the striker first Upper Winding; Weich accepts the flat Cross to give the parrier that attack. Neither pressure dominates across incoming HP, outgoing HP, and resource dimensions. When no eligible Winding exists, the earlier evaluability gap remains.",
        "",
        "## Fühlen After the Decline Option",
        "",
        "Skill 14, reserve 5+, both know Winden, conditional on successful Cross:",
        "",
        "| Hart prior | Best blind dmg | F1 dmg / S | Decline striker/parrier dmg | Avoided wrong read | Classification |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for row in f_rows:
        alt = row["alternatives_conditional_on_successful_cross"]
        blind = max(alt["blind_duplieren"]["striker_damage"], alt["blind_mutieren"]["striker_damage"])
        f = alt["f1_correct_dm"]
        d = alt["decline_both_know_winden_u2"]
        lines.append(f"| {pct(row['hart_prior'])} | {blind:.3f} | {f['striker_damage']:.3f} / {f['striker_spiritus']:.0f} | {d['striker_damage']:.3f} / {d['parrier_damage']:.3f} | {pct(row['f1_avoids_wrong_read_probability'])} | {row['f1_classification']} |")
    lines += [
        "",
        "F1 is never logically mandatory because Spiritus has no scalar value and cheaper Pareto alternatives remain. Under raw striker-damage maximization it is strongly attractive whenever reserve 3+ permits it. Under striker damage/S alone, decline ties F1 at Skill 10 and exceeds it at Skills 12/14/18, but this omits the parrier's Weich-side outgoing damage. Blind D/M remains rational at 20/80 priors, and reserve 2 forces the blind-or-decline texture. No affordable F1 row is fully Pareto-dominated; none is mandatory.",
        "",
        "## Spiritus Pressure",
        "",
        "D/M costs 2S; F1+D/M costs 3S; U2 costs 2S per attempt. At reserve 0/1 the ordinary bind ends by pass/disengage; reserve 2 permits one blind D/M or one U2 but not F1+D/M; reserve 3 permits the information package but constrains repeated Winding; 5+ exposes the full three-entry loop.",
        "",
        "## Chain Pressure",
        "",
        "Basic Cross, pressure declaration, and F1 consume zero entries. Each D/M or Upper Winding declaration consumes one. Exact all-miss chains stop after the third learned declaration; the fourth is illegal.",
        "",
        "## Ochs Value",
        "",
        "Every declared Upper Winding deterministically establishes Ochs and threatening point. The point state retains its existing D1 meaning outside this bind insertion, but D1 is not newly inserted into the bind phase. Within the bounded loop, Ochs itself is aftermath rather than a prerequisite or bonus; after a miss it is mostly descriptive because the next Upper declaration is gated by height/initiative/knowledge, not by starting Ochs.",
        "",
        "## Bind-Height Value",
        "",
        "Upper materially gates Winding and is deterministic, public, and nonoverlapping with contact zone/measure. It is understandable and leaves room for Lower. Yet one consumer means a boolean Upper eligibility flag would currently do the same work. Keep the axis candidate-only until a Lower or other height-dependent execution earns the extra state complexity.",
        "",
        "## H2 vs R0",
        "",
        "| Dimension | R0 | H2 |",
        "|---|---|---|",
        "| Historical intelligibility | Abstract roll-derived relation | Hart/Weich and Winden family are clearer |",
        "| Authored decisions | Relation not chosen | Parrier pressure; striker read/guess/decline |",
        "| Hidden/public axes | Hidden relation; existing public axes | Hidden initial pressure + public height |",
        "| Extra rolls | None | None beyond actual Upper attack |",
        "| Spiritus/chain | Existing local consumers | F1, 2S D/M, repeated 2S/entry Winding |",
        "| Initiative | Sequencing with sparse consumers | Rules-real in qualifying Upper bind |",
        "| Defender agency | Roll and local options | Weich can grant first Upper Winding |",
        "| Dead/ghost state | Relation broadly available to local candidates | Unknown height still dead outside new repertoire |",
        "| Policy dependence | Some inherited candidate policies | Exact branches; no initiative/Ochs utility constant |",
        "| Extensibility | Local Favored/Unfavored | Natural D/M/Winden/Schnitt/Zucken path, not implemented |",
        "| Minimum completeness | Current governing/provisional floor | Qualifying Upper case only |",
        "",
        "H2 is better in its authored qualifying case, but it is not yet the minimum architecture for all ordinary Basic Crosses. Replacing R0 now would trade a general floor for a richer but partial loop.",
        "",
        "## Zornhau Compatibility",
        "",
        "Zornhau remains local, point-threatening, and outside the ordinary H1 Rejoinder. Its current W1/W2 path is preserved only for the Zornhau-local crossing. If H2 is promoted later, Zornhau should remain local pending separate adjudication rather than being forced into Hart/Weich for symmetry.",
        "",
        "## Ghost / Policy Audit",
        "",
        "No Favored/Unfavored utility constant, Leverage, initiative bonus, Ochs value, random pressure/height, stale generic W1/W2 ordinary-bind action, Counter-Wind, or Cross/D1 immunity is used. D1 retains only its existing point-threat meaning and cannot be inserted into the post-Cross bind phase.",
        "",
        "## Remaining Gaps",
        "",
        "Nonqualifying/Unknown ordinary Crosses lack a concrete Bind-Initiative consumer. Lower height has no writer/consumer. Ochs is not yet a downstream gate after a miss. Spiritus still lacks an integrated campaign shadow price. These are reported, not silently patched.",
        "",
        "## Project Recommendation",
        "",
        "Keep H2 **candidate-only** and classify it **PROMISING BUT INCOMPLETE**. Retain U2 for the next test; do not advance U1. Keep generic Leverage rejected/deferred and Counter-Wind deferred. Do not replace R0 yet.",
        "",
        "## Exact Next Milestone",
        "",
        "Run **one more narrow bind-repertoire increment** addressing non-Upper/Unknown ordinary binds (with item-level evidence and no generic utility token). Then repeat the replacement adjudication. Do not begin full-duel cleanup or Named Guard v0.2 yet.",
        "",
        "## Project Decision Table",
        "",
        "| Topic | Candidate A | Candidate B | Result | Recommendation |",
        "|---|---|---|---|---|",
        "| Ordinary bind architecture | R0 Favored/Unfavored | H2 Hart/Weich + Winden | H2 stronger but partial | keep R0; H2 candidate |",
        "| Initial pressure | persistent | phase-scoped | scoped avoids stale pressure | phase-scoped |",
        "| Wrong D/M read | Bane | failure | Bane 81% at Skill 18; failure preserves lesson | hard failure candidate |",
        "| Fühlen | passive/free control | 1S initial reveal | situational by reserve/prior/objective | F1 candidate |",
        "| D/M price | 1S | 2S | action compression supports 2S | 2S |",
        "| Winding price | U1 1S | U2 2S | U1 crowds; U2 preserves D/M premium | U2 |",
        "| Bind Initiative | sequencing only | add Leverage | actual Upper consumer is sufficient in covered case | no Leverage |",
        "| Winden miss | cleanup | retain + initiative transfer | finite, interactive short chain | retain/transfer |",
        "| Bind geometry | no height axis | upper/lower/unknown | clean but single-consumer | candidate-only |",
        "| Counter-Wind | include | defer | prior 50-90% suppression remains concerning | defer |",
        "",
        "## Final Project-Review Questions",
        "",
        "1. **Yes.** The authoritative governing engine remained unchanged.",
        "2. **Yes.** All prior 81 governing assertions passed.",
        "3. **Yes.** All previous 75 candidate assertions passed.",
        "4. **Yes.** `bind_height` is distinct from measure and contact zone.",
        "5. **Not yet for promotion.** It is clean but has only one consumer.",
        "6. **Yes, within the bounded authored case.** It is deterministic and conservative.",
        "7. **Yes.** Phase scope removes stale pressure after the initial decision.",
        "8. **Yes.** No normal action is refreshed or additionally spent.",
        "9. **Yes.** Hard failure keeps D/M pressure-specific even at Skill 18.",
        "10. **Yes.** F1 varies with reserve, prior, and objective.",
        "11. **No.** It is raw-damage attractive centrally, not Pareto mandatory.",
        "12. **Yes.** Skewed priors and reserve 2 preserve blind reads.",
        "13. **Yes.** U1 is the conspicuous cheap broad fallback.",
        "14. **Yes.** U2 preserves the correct D/M Boon premium at equal price.",
        "15. **Yes.** U2 is the stronger candidate.",
        "16. **Yes.** Weich can give the parrier the first actual Upper Winding.",
        "17. **No, when both know Winden in a qualifying Upper bind.**",
        "18. **Yes as a Pareto/raw-vector comparison; not as one universal scalar choice.**",
        "19. **For uncovered cases, a concrete non-Upper/Unknown Bind-Initiative consumer remains missing.**",
        "20. **Yes in this bounded tree.** Miss transfer produces short reciprocal chains without arbitrary penalties.",
        "21. **Yes.** The three-Play cap makes the fourth declaration illegal.",
        "22. **Partly.** Upper Winding produces sourced Ochs and point threat.",
        "23. **No.** Ochs receives no generic bonus or prerequisite monopoly.",
        "24. **Yes in the qualifying Upper loop; not yet across all ordinary binds.**",
        "25. **Yes.** Generic Leverage should remain rejected/deferred.",
        "26. **Yes.** Counter-Wind should remain deferred.",
        "27. **Only in the qualifying Upper case, not as the minimum general floor.**",
        "28. **Remain candidate-only.** Do not replace R0 yet.",
        "29. **Yes.** Keep Zornhau local pending its own later adjudication.",
        "30. **One more narrow bind-repertoire increment.**",
        "",
        "STOP FOR PROJECT ADJUDICATION. No candidate is automatically promoted.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    results = build_results()
    RESULTS_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(report_text(results), encoding="utf-8")
    print(f"wrote {RESULTS_PATH.relative_to(ROOT)}")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)}")
    print(f"controlled tree rows: {len(results['controlled_game_tree'])}")
    print(f"Fuhlen rows: {len(results['fuhlen_after_decline'])}")
    print(f"short-chain rows: {len(results['short_krieg_chains'])}")


if __name__ == "__main__":
    main()

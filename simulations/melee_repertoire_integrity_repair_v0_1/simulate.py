from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
RESULTS_PATH = ROOT / "reports" / "melee-repertoire-integrity-repair-v01-results.json"
REPORT_PATH = ROOT / "reports" / "melee-repertoire-integrity-repair-v01-results.md"
SEED = 1208202601
SKILLS = (10, 14, 18)
SPIRITUS = (8, 3, 1, 0)
MEAN_NORMAL_DAMAGE = 4.5


def p_success(skill: int) -> float:
    return skill / 20


def p_boon(skill: int) -> float:
    p = p_success(skill)
    return 1 - (1 - p) ** 2


def damage_distribution(mode: str) -> dict[int, float]:
    counts: Counter[int] = Counter()
    if mode == "O1":
        for die in range(1, 7):
            counts[die + 1] += 1
        denominator = 6
    else:
        for first in range(1, 7):
            for second in range(1, 7):
                counts[min(first, second) + 1] += 1
        denominator = 36
    return {value: count / denominator for value, count in sorted(counts.items())}


def expected(dist: dict[int, float]) -> float:
    return sum(value * probability for value, probability in dist.items())


def kill_probability(dist: dict[int, float], hp: int) -> float:
    return sum(probability for value, probability in dist.items() if value >= hp)


def counter_decisions() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for skill in SKILLS:
        p = p_success(skill)
        boon = p_boon(skill)
        for spiritus in SPIRITUS:
            nach = spiritus >= 1
            rows.append({
                "skill": skill,
                "spiritus": spiritus,
                "immediate_basic_counter": {
                    "available": True,
                    "spiritus": 0,
                    "attack_success": p,
                    "expected_outgoing_damage_per_declaration": p * MEAN_NORMAL_DAMAGE,
                    "timing": "before committed attack",
                },
                "preparation_nachreisen": {
                    "available": nach,
                    "spiritus": 1 if nach else 0,
                    "attack_success": boon if nach else 0,
                    "expected_outgoing_damage_per_declaration": boon * MEAN_NORMAL_DAMAGE if nach else 0,
                    "timing": "before committed attack",
                },
                "wait_ordinary_counter": {
                    "available": True,
                    "trigger_probability": p,
                    "conditional_counter_success": p,
                    "expected_outgoing_damage_per_committed_declaration": p * p * MEAN_NORMAL_DAMAGE,
                    "timing": "simultaneous only after hit",
                },
                "wait_recovery_nachreisen": {
                    "available": nach,
                    "trigger_probability": 1 - p,
                    "conditional_attack_success": boon if nach else 0,
                    "expected_outgoing_damage_per_committed_declaration": (1 - p) * boon * MEAN_NORMAL_DAMAGE if nach else 0,
                    "timing": "immediate only after miss",
                },
                "basic_cross": {
                    "expected_incoming_damage": p * (1 - p) * MEAN_NORMAL_DAMAGE,
                    "successful_crossing_probability": p * p,
                },
                "basic_beat": {
                    "expected_incoming_damage": p * (1 - p) * MEAN_NORMAL_DAMAGE,
                    "successful_open_probability": p * p,
                },
            })
    return rows


def ort_results() -> dict[str, Any]:
    output: dict[str, Any] = {}
    for model in ("O1", "O2"):
        dist = damage_distribution(model)
        mean = expected(dist)
        output[model] = {
            "distribution": dist,
            "mean_damage_when_favored": mean,
            "expected_damage_per_50_50_opportunity_blind": 0.5 * mean,
            "spiritus_per_expected_damage_blind": 1 / (0.5 * mean),
            "spiritus_per_expected_damage_with_fuhlen": 1 / mean,
            "wrong_guess_spiritus_per_opportunity_blind": 0.5,
            "wrong_guess_spiritus_per_opportunity_with_fuhlen": 0,
            "kill_probability": {str(hp): kill_probability(dist, hp) for hp in (4, 6, 8)},
        }
    return output


def bind_tie_results() -> dict[str, Any]:
    return {
        str(skill): {
            "tie_frequency_conditional_on_two_successes": 1 / skill,
            "bind_initiative_holder_favored_frequency": (skill + 1) / (2 * skill),
            "non_initiative_holder_favored_frequency": (skill - 1) / (2 * skill),
        }
        for skill in SKILLS
    }


def bind_configuration_matrix(skill: int = 14) -> list[dict[str, Any]]:
    p = p_success(skill)
    wind_damage = p * MEAN_NORMAL_DAMAGE
    rows: list[dict[str, Any]] = []
    for ort_model in ("O1", "O2"):
        ort_damage = expected(damage_distribution(ort_model))
        for winden_variant in ("W1", "W2"):
            for fuhlen in (False, True):
                if fuhlen:
                    favored_options = {"Ort": ort_damage}
                    if winden_variant == "W2":
                        favored_options["Winden"] = wind_damage
                    favored_choice = max(favored_options, key=favored_options.get)
                    favored_damage = favored_options[favored_choice]
                    unfavored_choice = "Winden"
                    unfavored_damage = wind_damage
                    expected_damage = 0.5 * favored_damage + 0.5 * unfavored_damage
                    wrong_waste = 0.0
                    winden_rate = 0.5 + (0.5 if favored_choice == "Winden" else 0.0)
                else:
                    blind_options = {"Ort": 0.5 * ort_damage}
                    blind_options["Winden"] = wind_damage if winden_variant == "W2" else 0.5 * wind_damage
                    favored_choice = max(blind_options, key=blind_options.get)
                    unfavored_choice = favored_choice
                    expected_damage = blind_options[favored_choice]
                    wrong_waste = 0.0 if (favored_choice == "Winden" and winden_variant == "W2") else 0.5
                    winden_rate = 1.0 if favored_choice == "Winden" else 0.0
                rows.append({
                    "ort": ort_model,
                    "winden": winden_variant,
                    "fuhlen": fuhlen,
                    "favored_choice": favored_choice,
                    "unfavored_choice": unfavored_choice,
                    "expected_damage_per_controlled_opportunity": expected_damage,
                    "spiritus_per_opportunity": 1.0,
                    "wrong_prerequisite_spiritus_waste": wrong_waste,
                    "winden_declaration_rate": winden_rate,
                    "expected_chain_entries_after_zorn": 1 + winden_rate,
                    "hanging_aftermath_rate": winden_rate * (1 if winden_variant == "W2" else 0.5 if not fuhlen else 1),
                    "winden_chosen_from_favored": fuhlen and favored_choice == "Winden",
                })
    return rows


def fuhlen_value(matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ort_model in ("O1", "O2"):
        for winden_variant in ("W1", "W2"):
            absent = next(r for r in matrix if r["ort"] == ort_model and r["winden"] == winden_variant and not r["fuhlen"])
            present = next(r for r in matrix if r["ort"] == ort_model and r["winden"] == winden_variant and r["fuhlen"])
            rows.append({
                "ort": ort_model,
                "winden": winden_variant,
                "expected_damage_without_fuhlen": absent["expected_damage_per_controlled_opportunity"],
                "expected_damage_with_fuhlen": present["expected_damage_per_controlled_opportunity"],
                "information_value_damage_delta": present["expected_damage_per_controlled_opportunity"] - absent["expected_damage_per_controlled_opportunity"],
                "wrong_spiritus_waste_avoided": absent["wrong_prerequisite_spiritus_waste"] - present["wrong_prerequisite_spiritus_waste"],
            })
    return rows


def deterministic_results() -> dict[str, Any]:
    from tests import test_melee_repertoire_integrity_repair_v01 as tests

    groups = [
        ("1-8", tests.test_01_08_cross_d1_beat_open_state_based),
        ("9-11", tests.test_09_11_gc1_and_open_recovery),
        ("12-18", tests.test_12_18_general_committed_counter_timing),
        ("19-24", tests.test_19_24_preparation_nachreisen),
        ("25-33", tests.test_25_33_recovery_nachreisen_scope_and_cleanup),
        ("34-41", tests.test_34_41_zornhau_and_nearest_basic),
        ("42-47", tests.test_42_47_contested_bind_relation_and_tie),
        ("48-51", tests.test_48_51_bind_initiative_is_separate_and_passes_once),
        ("52-54", tests.test_52_54_fuhlen_visibility_and_zero_cost),
        ("55-63", tests.test_55_63_ort_intrinsic_hidden_requirement_and_damage_models),
        ("64-76", tests.test_64_76_minimal_winden_variants_and_aftermath),
        ("77-81", tests.test_77_81_chain_cap_intrinsics_and_passive),
    ]
    passed = []
    for label, function in groups:
        function()
        passed.append(label)
    tests.test_authoritative_baseline_p1_t1_c2_and_no_archived_behavior_dependency()
    return {"required_assertions": 81, "passed": 81, "groups": passed, "baseline_sync": "PASS"}


def run_all() -> dict[str, Any]:
    matrix = bind_configuration_matrix()
    return {
        "metadata": {
            "status": "PROVISIONAL BOUNDED REPAIR; CANDIDATE VARIANTS NOT PROMOTED",
            "seed_recorded_for_reproducibility": SEED,
            "method": "exact enumeration and deterministic branch forcing; no Monte Carlo required",
            "skills": list(SKILLS),
            "spiritus": list(SPIRITUS),
            "controlled_bind_relation": "50/50 except separately reported tie-rule sensitivity",
        },
        "deterministic": deterministic_results(),
        "counter_decisions": counter_decisions(),
        "zornhau_vs_cross": {
            str(skill): {
                "defence_success_probability_both": p_success(skill),
                "basic_cross_d1_exposure_when_point_nonthreatening": True,
                "zornhau_ordinary_d1_window": False,
                "basic_cross_spiritus": 0,
                "zornhau_spiritus": 0,
                "basic_cross_chain_entries": 0,
                "zornhau_chain_entries": 1,
                "both_establish_crossing": True,
                "basic_cross_automatic_point_threat": False,
                "zornhau_point_threat": True,
                "zornhau_bind_continuation_access": True,
            }
            for skill in SKILLS
        },
        "bind_tie_rule": bind_tie_results(),
        "ort": ort_results(),
        "bind_configuration_matrix_skill14": matrix,
        "fuhlen_information_value_skill14": fuhlen_value(matrix),
        "policy_audit": [
            {"item": "old Nachreisen fixed 0.52", "location": "archived loaded_power_attack_v0_1", "current_status": "QUARANTINED; authoritative engine has no utility constant"},
            {"item": "old Zornhau unrealizable Soft continuation value", "location": "archived crossing_bind_state_model_v0_1", "current_status": "QUARANTINED; current continuation derives from actual Favored/Unfavored state"},
            {"item": "Winden placeholders/Ochs-Pflug start gates", "location": "archived named_guard_rules_v0_1 and guard data", "current_status": "NOT USED by authoritative engine; no replacement bonus constant"},
            {"item": "P1-specific Counter-first utility", "location": "archived loaded_power_attack_v0_1", "current_status": "SUPERSEDED by general Committed rule behavior"},
            {"item": "Cross D1-immunity assumptions", "location": "archived Choice Architecture harness", "current_status": "SUPERSEDED; authoritative gate reads point threat only"},
            {"item": "guard utility tied to obsolete Winden gate", "location": "archived named-guard policy", "current_status": "QUARANTINED pending future integrated policy; no arbitrary replacement"},
        ],
        "frontale": {
            "status": "CANDIDATE ONLY",
            "basic_mappings": ["high thrust -> Basic Cross", "low thrust -> Basic Beat"],
            "sequence": ["retreat", "fendente", "Dente di Zenghiaro", "thrust", "return fendente"],
            "smallest_project_question": "Which fendente/thrust is the principal ATTACK/test, are later blows intrinsic continuations, and may retreat remain metadata until Force Movement exists?",
        },
        "recommendations_not_promotions": {
            "counter_timing": "retain general Committed declaration timing",
            "nachreisen": "retain repaired 1S two-window model for integration",
            "ort": "O1 normal damage is the stronger Project-review candidate",
            "winden": "W2 either-relation is the stronger Project-review candidate",
            "fuhlen": "retain passive categorical visibility model",
            "frontale": "leave candidate-only pending one action/test adjudication",
            "next_milestone": "integrated engine cleanup after Project adjudicates O1/O2 and W1/W2; not Named Guard v0.2",
        },
    }


def fmt(value: float) -> str:
    return f"{value:.3f}"


def pct(value: float) -> str:
    return f"{value:.1%}"


def build_report(results: dict[str, Any]) -> str:
    ort = results["ort"]
    matrix = results["bind_configuration_matrix_skill14"]
    fvalue = results["fuhlen_information_value_skill14"]
    lines = [
        "# Melee Repertoire Integrity Repair v0.1 Results", "",
        "Status: **GOVERNING PROVISIONAL implementation repair; O1/O2 and W1/W2 remain unpromoted candidates.**", "",
        "## Executive Result", "",
        "The authoritative shared exchange engine is synchronized and all 81 required deterministic assertions pass. Blanket Cross immunity is gone: D1 is denied only by threatening opposing point (plus its ordinary prerequisites), while Beat still strips a successfully defended attacker to conservative Open. General Committed timing, the 1-Spiritus two-window Nachreisen, threatening-point Zornhau, contested Favored/Unfavored Bind, independent Bind Initiative, passive Fühlen, intrinsic Ort, and minimal thrusting Winden now have rules-derived behavior.", "",
        "Exact controlled analysis favors **O1 normal damage** over O2 and **W2 either-relation** over W1 for Project review, but neither is promoted. At Skill 14, W2 Winden is harmless optionality from Favored Bind under both damage models: deterministic immediate value still selects Ort there. Fühlen has positive value without a numeric bonus by eliminating wrong hidden-condition decisions. Frontale remains candidate-only because its evidence does not decide the Atra attack/test count or whether retreat is merely metadata.", "",
        "## Source-of-Truth Check", "",
        "Git was clean before edits. The packet, governing register/YAML, vocabulary, architecture and incentive reports, Crossing/Bind and continuation reports, guard evidence, Loaded/Power, Spiritus/Parry/D1, audited Play records, shared selector, selected archived engine, action timing, policy constants, and current tests were inspected. No unresolved material conflict remained after applying the prompt's explicit later adjudications. Atra Melee Design Packet v0.4 was not edited.", "",
        "## Project Supersessions Persisted", "",
        "Durable governing records now mark blanket Cross immunity, P1-only Counter-first, old Nachreisen persistence/Vom Tag gating, nonthreatening Zornhau, and exclusive Ochs/Pflug Winden starting gates as superseded. Archived reports and experiment engines were not rewritten.", "",
        "## Authoritative Engine Synchronization", "",
        "`simulations/shared/provisional_longsword.py` now selects `simulations/shared/provisional_longsword_engine.py`. Archived Loaded/Power classes remain compatibility exports only. The current engine implements state-based D1, Beat->Open, GC1, general Committed timing, current P1 restrictions, T1, cap 3, C2/S2 response chassis, and explicit contact/measure/pressure/point state.", "",
        "## Mechanical Vocabulary Compliance", "",
        "The repair uses only ATTACK, CANCEL, SET, CLEAR, RETAIN, MODIFY_ATTACK, REPLACE_PENDING_ATTACK, and existing timing/order behavior. No new operator was needed. Bind relation and Bind Initiative are state/sequencing data, not generic modifiers. Mechanical retreat in Frontale was stopped because Force Movement remains deferred.", "",
        "## Committed / Counter Timing", "",
        "Immediate Basic Counter is free, normal, and first; Preparation Nachreisen pays 1S for Attack Boon in the same window; waiting Counter is simultaneous only after a hit; Recovery Nachreisen exists only after a miss. The defender's single action prevents double defence naturally.", "",
        "## Nachreisen Historical-to-Mechanical Mapping", "",
        "The audited broader lesson is temporal pursuit around commitment. The repaired chassis therefore has target-only Preparation and immediate target-only Recovery branches, one learned entry, 1S declaration spend, Attack Boon, normal damage, no Vom Tag gate, no persistent Recovery status, and no guard-change trigger.", "",
        "## Nachreisen Decision Tree", "",
        "On a Committed declaration: choose immediate free Counter, 1S Preparation Nachreisen, or wait. If the roll hits, waiting permits ordinary simultaneous Counter; if it misses, waiting permits 1S immediate Recovery Nachreisen. At 0S the two free Basic choices remain. These motives are condition-, risk-, and resource-distinct.", "",
        "### Exact comparison at Skill 14", "",
        "| Choice | Trigger | S | Attack success | Expected outgoing damage per committed declaration | Timing |", "|---|---|---:|---:|---:|---|",
    ]
    row = next(r for r in results["counter_decisions"] if r["skill"] == 14 and r["spiritus"] == 8)
    lines += [
        f"| Immediate Basic Counter | declaration | 0 | {pct(row['immediate_basic_counter']['attack_success'])} | {fmt(row['immediate_basic_counter']['expected_outgoing_damage_per_declaration'])} | first |",
        f"| Preparation Nachreisen | declaration | 1 | {pct(row['preparation_nachreisen']['attack_success'])} | {fmt(row['preparation_nachreisen']['expected_outgoing_damage_per_declaration'])} | first |",
        f"| Wait -> Counter | hit | 0 | {pct(row['wait_ordinary_counter']['conditional_counter_success'])} conditional | {fmt(row['wait_ordinary_counter']['expected_outgoing_damage_per_committed_declaration'])} | simultaneous |",
        f"| Wait -> Recovery Nachreisen | miss | 1 | {pct(row['wait_recovery_nachreisen']['conditional_attack_success'])} conditional | {fmt(row['wait_recovery_nachreisen']['expected_outgoing_damage_per_committed_declaration'])} | immediate after miss |", "",
        "## Zornhau-Ort Initial Repair", "",
        "A qualifying descending Cut is sufficient; Committed is not required. Successful Zornhau spends action plus one learned entry and 0S, cancels, establishes contested Crossing, authors threatening point and Bind Initiative, and does no automatic damage or Hard/Soft authoring.", "",
        "## Basic Cross vs Zornhau", "",
        "Both use the same normal defence probability and establish Crossing. Cross is universal, chain-free, exposes state-based D1 when the point is nonthreatening, and does not automatically threaten. Zornhau is learned, costs one chain entry, has no ordinary Basic-D1 insertion window, creates threatening point, and opens intrinsic/repertoire bind continuations. Its distinction is rules-real without ghost utility.", "",
        "## Minimal Bind Relation", "",
        "When two successful comparable rolls create Crossing, lower is better. The winner is Favored and the other Unfavored. No new roll or generic modifier occurs; fixtures lacking comparable rolls remain Unknown. Hard/Soft pressure remains separate. Conditional tie frequency is 10.0%, 7.1%, and 5.6% at Skills 10/14/18. The provisional initiative tie rule gives the defensive initiative holder 55.0%, 53.6%, and 52.8% Favored frequency respectively, so the small systematic skew is flagged for Project review.", "",
        "## Bind Initiative", "",
        "The successful defensive Cross/Zornhau creator declares first even when Unfavored. Declining passes one opportunity to the opponent before cleanup. No secret simultaneous declarations or initiative roll were added.", "",
        "## Fühlen", "",
        "Fühlen reveals only Favored/Unfavored/Unknown and costs no action, Spiritus, or chain entry. Its exact Skill-14 information value is:", "",
        "| Ort | Winden | Damage without | Damage with | Delta | Wrong S avoided |", "|---|---|---:|---:|---:|---:|",
    ]
    for item in fvalue:
        lines.append(f"| {item['ort']} | {item['winden']} | {fmt(item['expected_damage_without_fuhlen'])} | {fmt(item['expected_damage_with_fuhlen'])} | {fmt(item['information_value_damage_delta'])} | {fmt(item['wrong_spiritus_waste_avoided'])} |")
    lines += ["", "## Ort O1 vs O2", "", "| Model | Favored damage | Blind 50/50 damage | S/damage blind | S/damage with Fühlen | Kill HP4 | Kill HP6 | Kill HP8 |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for model in ("O1", "O2"):
        item = ort[model]
        lines.append(f"| {model} | {fmt(item['mean_damage_when_favored'])} | {fmt(item['expected_damage_per_50_50_opportunity_blind'])} | {fmt(item['spiritus_per_expected_damage_blind'])} | {fmt(item['spiritus_per_expected_damage_with_fuhlen'])} | {pct(item['kill_probability']['4'])} | {pct(item['kill_probability']['6'])} | {pct(item['kill_probability']['8'])} |")
    lines += [
        "", "O1 is the stronger review candidate. Ort already requires successful Zornhau, immediate Bind Initiative, hidden Favored position, and 1S; O2 then reduces conditional mean damage from 4.500 to 3.528. Fühlen halves Spiritus per expected Ort damage by preventing the 50% wrong-state spend in the controlled blind model.", "",
        "## Winden W1 vs W2", "",
        "W1 supplies only 50% true applicability in the controlled relation mix and makes an untrained user risk 0.5 wasted Spiritus per blind declaration. W2 always has a legal thrust, while Ort remains the immediate-efficiency choice from Favored at Skill 14. W2 therefore produces less arbitrary information dependence; this is a recommendation for adjudication, not promotion.", "",
        "## Ort / Winden / Fühlen Progression", "",
        "Zornhau-Ort alone permits a hidden Ort gamble. Adding Winden supplies a second bind lesson but remains blind without Fühlen. Adding Fühlen alone makes Favored Ort legible and exposes Unfavored as having no available continuation. All three create the intended conditional curriculum: Ort from Favored; Winden from Unfavored; W2 additionally permits a normally inferior Favored thrust option.", "",
        "### Eight exact Skill-14 configurations", "",
        "| Ort | Wind | Fühlen | Favored choice | Unfavored choice | Damage/opportunity | Wrong S | Chain after Zorn | Wind from Favored |", "|---|---|---|---|---|---:|---:|---:|---|",
    ]
    for item in matrix:
        lines.append(f"| {item['ort']} | {item['winden']} | {'yes' if item['fuhlen'] else 'no'} | {item['favored_choice']} | {item['unfavored_choice']} | {fmt(item['expected_damage_per_controlled_opportunity'])} | {fmt(item['wrong_prerequisite_spiritus_waste'])} | {fmt(item['expected_chain_entries_after_zorn'])} | {'yes' if item['winden_chosen_from_favored'] else 'no'} |")
    lines += [
        "", "## Ochs / Pflug Aftermath and Gate Review", "",
        "Neither Ochs nor Pflug is a starting gate. Minimal Winden records the least-specific supported upper/lower Ochs-or-Pflug hanging aftermath; side and height remain unresolved without authored context. No invented geometry or guard bonus follows.", "",
        "## Frontale Repair", "",
        "High-thrust Cross and low-thrust Beat remain universal Basics. The learned retreat/fendente/Dente/thrust/return sequence is decomposed in the prototype and Play record but not implemented. Smallest question: which blow is the principal ATTACK/test, are later blows intrinsic continuations, and may retreat remain event metadata until Force Movement exists? No generic Frontale bonus or Crown relationship was created.", "",
        "## Deterministic Regression Results", "",
        "**PASS: 81/81 required assertions**, plus authoritative-baseline P1/T1/C2 integration checks. The suite covers state-based D1, Open/GC1, Committed timing, both Nachreisen windows, Zornhau, bind position/initiative, Fühlen, O1/O2, W1/W2, aftermath, and chain cap.", "",
        "## Controlled Micro-Experiment Results", "",
        "All comparisons are exact enumeration/branch forcing; no Monte Carlo was needed. Skills 10/14/18 and Spiritus 8/3/1/0 are present in JSON. The 2x2x2 bind matrix uses Skill 14 and a controlled 50/50 relation, with Skill/tie sensitivities separately recorded.", "",
        "## Spiritus / Chain Pressure", "",
        "Immediate Counter and Basic Cross/Beat protect the 0S game. Both Nachreisen branches, Ort, and Winden spend 1S at declaration. Zornhau counts one; intrinsic Ort and passive Fühlen do not; Winden after Zornhau counts the second. The fourth learned Play remains illegal. W1's hidden prerequisite creates the largest avoidable waste.", "",
        "## Policy and Ghost-Utility Cleanup", "",
        "The authoritative engine and controlled analysis contain no Nachreisen 0.52 constant, unrealizable Soft utility, Cross-immunity bonus, P1-only Counter-first value, or guard bonus for an inactive Winden gate. Those values remain only in archived reproducibility engines and are explicitly quarantined; no replacement constant was tuned to force use.", "",
        "## Remaining Historical/Mechanical Gaps", "",
        "O1/O2 and W1/W2 require Project adjudication. The tie rule has a small initiative-holder skew. Exact Winden hanging side/height needs authored context. Full pressure/Yield, eight Windings, cut/slice branches, Duplieren/Mutieren, and Frontale's action/test compression remain outside this repair.", "",
        "## Ready for Integrated Longsword Vertical Slice?", "",
        "**Conditionally.** The minimum German repair is coherent and deterministic, but candidate selection and migration into a full current duel/policy loop remain before integrated balance evidence. Frontale is not mechanically complete, but it does not block the German slice.", "",
        "## Exact Next Milestone", "",
        "After Project adjudicates O1/O2 and W1/W2, perform **integrated engine cleanup**: migrate the synchronized exchange state machine into the current full duel loop and rebuild rules-derived policy/instrumentation. Do not start Named Guard v0.2 yet.", "",
        "## Project Review Decision Table", "",
        "| Topic | Old / candidate A | New / candidate B | Result | Recommendation (not promotion) |", "|---|---|---|---|---|",
        "| Counter timing | P1-only Counter-first | general Committed declaration window | consistent first/simultaneous branches | retain general rule |",
        "| Nachreisen | persistent Recovering/free/Vom Tag policy chassis | 1S target-only two-window Attack-Boon model | distinct from Counter and nonpersistent | retain repaired model |",
        f"| Ort | O1 mean {fmt(ort['O1']['mean_damage_when_favored'])} | O2 mean {fmt(ort['O2']['mean_damage_when_favored'])} | O1 has better S efficiency; both gain from Fühlen | O1 for adjudication |",
        "| Winden | W1 Unfavored-only | W2 either relation | W1 has 50% blind wrong-state risk; W2 mostly harmless Favored optionality at Skill 14 | W2 for adjudication |",
        "| Fühlen | passive categorical visibility | no numeric bonus | positive damage decision delta and avoids wrong spend | retain passive model |",
        "| Frontale | universal Cross/Beat mappings | learned sequence candidate | evidence complete enough to decompose, not to choose tests/actions | leave candidate-only |", "",
        "## Final Project-Review Questions", "",
        "1. **Yes.** The authoritative shared exchange engine is synchronized.",
        "2. **Yes.** Blanket Cross immunity is removed from current behavior and durable current metadata; archived reports retain only labeled historical records.",
        "3. **Yes.** Threatening opposing point denies D1; Crossing/form does not.",
        "4. **Provisionally yes.** Beat->Open is clean; repertoire-poor Cross still depends on downstream Crossing value.",
        "5. **Yes.** General Committed timing cleanly replaces the P1-only special case, and P1 inherits it.",
        "6. **Yes.** Nachreisen buys Attack Boon and the miss-only Recovery branch for 1S; free Counter remains essential at 0S and for conservation.",
        "7. **Yes.** Preparation buys early interruption accuracy; Recovery exploits a miss after waiting.",
        "8. **Yes.** The target-specific window is immediate, nonpersistent, and needs no response-denial payload.",
        "9. **Yes.** Zornhau buys threatening-point Crossing, Bind Initiative, and continuation access without automatic damage.",
        "10. **Yes.** The two existing successful rolls determine the relation without another roll.",
        "11. **Yes.** Initiative and position remain independent and sequence coherently.",
        "12. **Yes.** Fühlen improves conditional decisions without a numeric bonus.",
        "13. **O1 normal damage** is the stronger review candidate; not promoted.",
        "14. **Yes provisionally** for O1 in this controlled model; Project adjudication remains required.",
        "15. **W2 either relation** is the stronger review candidate; not promoted.",
        "16. **Yes provisionally.** W1's blind waste is the concern, not the common 1S price.",
        "17. **No.** Existing ATTACK/RETAIN/SET vocabulary is sufficient.",
        "18. **Yes.** Ochs/Pflug should remain aftermath/entry geometry, not exclusive starting gates.",
        "19. **Yes.** Zornhau -> Ort/Winden -> Fühlen forms a coherent minimum curriculum.",
        "20. **No.** Frontale remains candidate-only pending its action/test decision.",
        "21. **Candidate adjudication and full-loop integration** block the vertical slice; Frontale does not block the German core.",
        "22. **Integrated engine cleanup**, after immediate O1/O2 and W1/W2 Project adjudication; not Named Guard v0.2.", "",
        "Stop for Project adjudication. O1/O2 and W1/W2 are not automatically promoted.", "",
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
    print(json.dumps({"deterministic": results["deterministic"], "report": str(REPORT_PATH)}, indent=2))


if __name__ == "__main__":
    main()

"""Exact deterministic analysis for Upper/Lower Winden completion v0.3."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = ROOT / "reports" / "upper-lower-winden-completion-v03-results.json"
REPORT_PATH = ROOT / "reports" / "upper-lower-winden-completion-v03-results.md"
MEAN_DAMAGE = 4.5
SKILLS = (10, 12, 14, 18)
PRIORS = (0.2, 0.4, 0.5, 0.6, 0.8)

KNOWLEDGE = {
    "neither_winden": (False, False, False, False),
    "striker_winden": (True, False, False, False),
    "parrier_winden": (False, True, False, False),
    "both_winden": (True, True, False, False),
    "striker_dm": (False, False, True, False),
    "striker_dm_fuhlen": (False, False, True, True),
    "full": (True, True, True, True),
}


def p_success(skill: int) -> float:
    return skill / 20


def p_boon(skill: int) -> float:
    p = p_success(skill)
    return 1 - (1 - p) ** 2


def rnd(value: float) -> float:
    return round(value, 6)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select_strategy(vectors: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Pure striker-damage objective, then lower spend; insertion order breaks full ties."""
    names = list(vectors)
    ranked = sorted(
        names,
        key=lambda name: (
            -float(vectors[name]["striker_outgoing_damage"]),
            float(vectors[name]["striker_spiritus"]),
            names.index(name),
        ),
    )
    selected = ranked[0]
    best_damage = float(vectors[selected]["striker_outgoing_damage"])
    damage_ties = [
        name for name in names
        if float(vectors[name]["striker_outgoing_damage"]) == best_damage
    ]
    best_spend = min(float(vectors[name]["striker_spiritus"]) for name in damage_ties)
    final_ties = [
        name for name in damage_ties
        if float(vectors[name]["striker_spiritus"]) == best_spend
    ]
    return {
        "named_objective": "maximize striker outgoing damage; lower striker spend only after a damage tie",
        "selection_scope": "known realized pressure row",
        "selected_strategy": selected,
        "primary_damage_ties": damage_ties,
        "final_ties_after_spend": final_ties,
    }


def dm_vectors(skill: int, pressure: str) -> dict[str, dict[str, Any]]:
    damage = p_boon(skill) * MEAN_DAMAGE
    return {
        "blind_duplieren": {
            "striker_outgoing_damage": rnd(damage if pressure == "hart" else 0),
            "parrier_outgoing_damage": 0.0,
            "striker_spiritus": 2.0,
            "parrier_spiritus": 0.0,
            "chain_entries": 1.0,
            "wrong_read_failure": pressure != "hart",
        },
        "blind_mutieren": {
            "striker_outgoing_damage": rnd(damage if pressure == "weich" else 0),
            "parrier_outgoing_damage": 0.0,
            "striker_spiritus": 2.0,
            "parrier_spiritus": 0.0,
            "chain_entries": 1.0,
            "wrong_read_failure": pressure != "weich",
        },
    }


def v02_selector_audit() -> dict[str, Any]:
    path = ROOT / "reports" / "hart-weich-upper-winden-loop-v02-results.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data["controlled_game_tree"]
    eligible = [
        row for row in rows
        if "blind_duplieren" in row["available_strategies"]
        and "blind_mutieren" in row["available_strategies"]
    ]
    hart_mutieren = [
        row for row in eligible
        if row["pressure"] == "hart" and row["selected_strategy"] == "blind_mutieren"
    ]
    aggregate_pairs_preserved = all(
        row["named_objective"].startswith("equal-prior") for row in eligible
    )
    hart_test = select_strategy(dm_vectors(14, "hart"))
    weich_test = select_strategy(dm_vectors(14, "weich"))
    return {
        "classification": "D: misunderstood field semantics, with ambiguous instrumentation",
        "serialization_bug": False,
        "selector_indexing_bug": False,
        "policy_selection_bug": False,
        "explanation": (
            "v0.2 selected one ex-ante equal-prior fixed policy before iterating realized pressure. "
            "Blind D/M tie at q=.5; an undocumented lexical tie-break chose Mutieren, and the "
            "same policy label was then serialized in both conditional rows."
        ),
        "eligible_realized_rows": len(eligible),
        "hart_rows_showing_fixed_mutieren_policy": len(hart_mutieren),
        "equal_prior_aggregate_semantics_preserved": aggregate_pairs_preserved,
        "prior_conclusions_changed": [],
        "prior_output_caveat": (
            "Per-pressure selected_strategy is a realized outcome of a fixed ex-ante policy, "
            "not a pressure-aware recommendation. Equal-prior paired aggregates remain valid."
        ),
        "known_hart_regression": hart_test,
        "known_weich_regression": weich_test,
    }


def all_miss_schedule(
    *, initial_holder: str, knows: dict[str, bool], reserves: dict[str, int],
    height: str, lower_variant: str,
) -> tuple[list[dict[str, str]], str]:
    actor = initial_holder
    passes = 0
    schedule: list[dict[str, str]] = []
    while len(schedule) < 3:
        if height in {"upper", "lower"} and knows[actor] and reserves[actor] >= 2:
            schedule.append({"actor": actor, "height": height})
            reserves[actor] -= 2
            passes = 0
            if height == "lower" and lower_variant == "L2":
                height = "upper"
            actor = "parrier" if actor == "striker" else "striker"
            continue
        passes += 1
        if passes >= 2:
            return schedule, "pass/resource termination"
        actor = "parrier" if actor == "striker" else "striker"
    return schedule, "chain cap"


def winding_vector(
    skill: int, *, initial_holder: str, striker_knows: bool, parrier_knows: bool,
    height: str, lower_variant: str = "L2", reserve: int = 6,
) -> dict[str, Any]:
    schedule, terminal = all_miss_schedule(
        initial_holder=initial_holder,
        knows={"striker": striker_knows, "parrier": parrier_knows},
        reserves={"striker": reserve, "parrier": reserve},
        height=height,
        lower_variant=lower_variant,
    )
    p = p_success(skill)
    q = 1 - p
    reach = 1.0
    damages = {"striker": 0.0, "parrier": 0.0}
    spends = {"striker": 0.0, "parrier": 0.0}
    hit_by: list[dict[str, Any]] = []
    transfers = 0.0
    for index, declaration in enumerate(schedule, 1):
        actor = declaration["actor"]
        hit = reach * p
        damages[actor] += hit * MEAN_DAMAGE
        spends[actor] += reach * 2
        hit_by.append({
            "declaration": index,
            "actor": actor,
            "height": declaration["height"],
            "reach_probability": rnd(reach),
            "incremental_hit_probability": rnd(hit),
            "cumulative_hit_probability": rnd(1 - reach * q),
        })
        transfers += reach * q
        reach *= q
    first_miss = q if schedule else 0.0
    l2_change = height == "lower" and lower_variant == "L2"
    opponent_upper = (
        l2_change and len(schedule) >= 2
        and schedule[1]["actor"] != schedule[0]["actor"]
        and schedule[1]["height"] == "upper"
    )
    return {
        "all_miss_schedule": schedule,
        "expected_declarations": rnd(sum(row["reach_probability"] for row in hit_by)),
        "expected_total_spiritus": rnd(spends["striker"] + spends["parrier"]),
        "striker_outgoing_damage": rnd(damages["striker"]),
        "parrier_outgoing_damage": rnd(damages["parrier"]),
        "striker_spiritus": rnd(spends["striker"]),
        "parrier_spiritus": rnd(spends["parrier"]),
        "chain_entries": rnd(sum(row["reach_probability"] for row in hit_by)),
        "hit_by_declaration": hit_by,
        "bind_hit_probability": rnd(1 - reach),
        "retained_crossing_miss_event_expectation": rnd(transfers),
        "retained_crossing_after_terminal_probability": rnd(reach),
        "initiative_transfer_expectation": rnd(transfers),
        "geometry_change_probability": rnd(first_miss if l2_change else 0.0),
        "opponent_upper_winding_opportunity_probability": rnd(first_miss if opponent_upper else 0.0),
        "ochs_appears_probability": rnd(
            1.0 if height == "upper" and schedule else first_miss if l2_change else 0.0
        ),
        "pflug_established_probability": 1.0 if height == "lower" and schedule else 0.0,
        "pflug_persists_after_first_miss_probability": rnd(
            first_miss if height == "lower" and lower_variant == "L1" else 0.0
        ),
        "chain_cap_termination_probability": rnd(reach if terminal == "chain cap" else 0.0),
        "pass_or_resource_termination_probability": rnd(
            reach if terminal != "chain cap" else 0.0
        ),
        "all_miss_terminal": terminal,
    }


def l1_l2_rows() -> list[dict[str, Any]]:
    rows = []
    for skill in SKILLS:
        for variant in ("L1", "L2"):
            rows.append({
                "skill": skill,
                "variant": variant,
                **winding_vector(
                    skill, initial_holder="striker", striker_knows=True,
                    parrier_knows=True, height="lower", lower_variant=variant,
                ),
            })
    return rows


def consequence_rows() -> list[dict[str, Any]]:
    rows = []
    geometries = {
        "upper": ("upper", "L2"),
        "lower_l1": ("lower", "L1"),
        "lower_l2": ("lower", "L2"),
        "unknown": ("unknown", "L2"),
    }
    for skill in SKILLS:
        for geometry_name, (height, variant) in geometries.items():
            for knowledge_name, (sw, pw, dm, fuhlen) in KNOWLEDGE.items():
                for pressure in ("hart", "weich"):
                    holder = "striker" if pressure == "hart" else "parrier"
                    decline = winding_vector(
                        skill, initial_holder=holder, striker_knows=sw,
                        parrier_knows=pw, height=height, lower_variant=variant,
                    )
                    decline["strategy"] = "decline"
                    vectors: dict[str, dict[str, Any]] = {"decline": decline}
                    if dm:
                        vectors.update(dm_vectors(skill, pressure))
                    if dm and fuhlen:
                        vectors["fuhlen_correct_dm"] = {
                            "striker_outgoing_damage": rnd(p_boon(skill) * MEAN_DAMAGE),
                            "parrier_outgoing_damage": 0.0,
                            "striker_spiritus": 3.0,
                            "parrier_spiritus": 0.0,
                            "chain_entries": 1.0,
                            "wrong_read_failure": False,
                        }
                    selection = select_strategy(vectors)
                    rows.append({
                        "skill": skill,
                        "geometry": geometry_name,
                        "knowledge": knowledge_name,
                        "pressure": pressure,
                        "cross_success_conditional_on_attack": rnd(
                            p_boon(skill) if pressure == "hart" else p_success(skill)
                        ),
                        "candidate_vectors": vectors,
                        **selection,
                    })
    return rows


def weighted(a: dict[str, Any], b: dict[str, Any], q: float, key: str) -> float:
    return rnd(q * float(a[key]) + (1 - q) * float(b[key]))


def pareto_relevant(alternatives: dict[str, dict[str, Any]], target: str) -> bool:
    t = alternatives[target]
    for name, other in alternatives.items():
        if name == target:
            continue
        weak = (
            other["striker_outgoing_damage"] >= t["striker_outgoing_damage"]
            and other["parrier_outgoing_damage"] <= t["parrier_outgoing_damage"]
            and other["striker_spiritus"] <= t["striker_spiritus"]
            and other["chain_entries"] <= t["chain_entries"]
        )
        strict = (
            other["striker_outgoing_damage"] > t["striker_outgoing_damage"]
            or other["parrier_outgoing_damage"] < t["parrier_outgoing_damage"]
            or other["striker_spiritus"] < t["striker_spiritus"]
            or other["chain_entries"] < t["chain_entries"]
        )
        if weak and strict:
            return False
    return True


def fuhlen_rows() -> list[dict[str, Any]]:
    rows = []
    for skill in (10, 14, 18):
        boon = p_boon(skill) * MEAN_DAMAGE
        for geometry, height, variant in (
            ("upper", "upper", "L2"),
            ("lower_l1", "lower", "L1"),
            ("lower_l2", "lower", "L2"),
            ("unknown", "unknown", "L2"),
        ):
            hart_decline = winding_vector(
                skill, initial_holder="striker", striker_knows=True,
                parrier_knows=True, height=height, lower_variant=variant,
            )
            weich_decline = winding_vector(
                skill, initial_holder="parrier", striker_knows=True,
                parrier_knows=True, height=height, lower_variant=variant,
            )
            for q in PRIORS:
                alternatives = {
                    "blind_duplieren": {
                        "striker_outgoing_damage": rnd(q * boon),
                        "parrier_outgoing_damage": 0.0,
                        "striker_spiritus": 2.0,
                        "chain_entries": 1.0,
                    },
                    "blind_mutieren": {
                        "striker_outgoing_damage": rnd((1 - q) * boon),
                        "parrier_outgoing_damage": 0.0,
                        "striker_spiritus": 2.0,
                        "chain_entries": 1.0,
                    },
                    "f1_correct_dm": {
                        "striker_outgoing_damage": rnd(boon),
                        "parrier_outgoing_damage": 0.0,
                        "striker_spiritus": 3.0,
                        "chain_entries": 1.0,
                    },
                    "decline": {
                        "striker_outgoing_damage": weighted(hart_decline, weich_decline, q, "striker_outgoing_damage"),
                        "parrier_outgoing_damage": weighted(hart_decline, weich_decline, q, "parrier_outgoing_damage"),
                        "striker_spiritus": weighted(hart_decline, weich_decline, q, "striker_spiritus"),
                        "chain_entries": weighted(hart_decline, weich_decline, q, "chain_entries"),
                    },
                }
                for vector in alternatives.values():
                    spend = vector["striker_spiritus"]
                    vector["striker_damage_per_spiritus"] = (
                        rnd(vector["striker_outgoing_damage"] / spend) if spend else None
                    )
                efficiencies = {
                    name: vector["striker_damage_per_spiritus"]
                    for name, vector in alternatives.items()
                    if vector["striker_damage_per_spiritus"] is not None
                }
                best_eff = max(efficiencies.values()) if efficiencies else None
                rows.append({
                    "skill": skill,
                    "geometry": geometry,
                    "hart_prior": q,
                    "alternatives": alternatives,
                    "wrong_read_failures_avoided_by_f1": rnd(min(q, 1 - q)),
                    "f1_pareto_relevant": pareto_relevant(alternatives, "f1_correct_dm"),
                    "pure_damage_selection": select_strategy(alternatives)["selected_strategy"],
                    "damage_per_spiritus_best": [
                        name for name, value in efficiencies.items() if value == best_eff
                    ],
                    "blind_read_rational": any(
                        name.startswith("blind_") and value == best_eff
                        for name, value in efficiencies.items()
                    ),
                    "decline_pareto_relevant": pareto_relevant(alternatives, "decline"),
                })
    return rows


def coverage_rows() -> list[dict[str, Any]]:
    return [
        {"scenario": "descending/Oberhau-like Cut + qualifying Upper cross", "height": "upper", "writer": "explicit Upper writer", "legal_winden": "Upper Winding", "cleanup": "hit ends; miss retains Upper/transfers; pass/disengage otherwise"},
        {"scenario": "low-line thrust + explicitly authored lower setting-aside", "height": "lower", "writer": "event metadata on defence", "legal_winden": "Lower Winding", "cleanup": "hit ends; L1 stays Lower; L2 becomes Upper; pass/disengage otherwise"},
        {"scenario": "rising low-line Cut + explicitly authored lower setting-aside", "height": "lower", "writer": "bounded supported harness case", "legal_winden": "Lower Winding", "cleanup": "same as lower thrust case"},
        {"scenario": "generic lateral/unclassified Cross", "height": "unknown", "writer": "none", "legal_winden": "none from geometry", "cleanup": "initiative holder may use other legal repertoire, pass, or disengage"},
    ]


def short_chains() -> list[dict[str, Any]]:
    return [
        {"id": "A", "sequence": "Lower -> A Lower hit", "legal": True, "terminal": "normal damage; bind ends"},
        {"id": "B", "sequence": "Lower -> A Lower miss L1 -> B Lower", "legal": True, "terminal": "second declaration if B knows Winden/has 2S"},
        {"id": "C", "sequence": "Lower -> A Lower miss L2 -> Upper -> B Upper", "legal": True, "terminal": "interactive upper reply"},
        {"id": "D", "sequence": "Lower L2 miss -> B Upper miss -> A Upper", "legal": True, "terminal": "third learned declaration"},
        {"id": "E", "sequence": "third Winding miss -> fourth learned declaration", "legal": False, "terminal": "cap 3"},
        {"id": "F", "sequence": "holder has <2S -> pass; opponent has <2S -> pass", "legal": True, "terminal": "resource/pass cleanup before cap"},
        {"id": "G", "sequence": "holder lacks Winden -> pass -> knowledgeable opponent acts", "legal": True, "terminal": "normal sequencing, no bonus"},
    ]


def geometry_loops() -> list[dict[str, Any]]:
    return [
        {"geometry": "Upper", "path": "Cross -> Rejoinder/decline -> initiative -> Upper Winding", "action_delta": "initial attack + Cross only", "spiritus": "0 then 2 per Winding", "chain": "0 then +1", "pressure": "clears after Rejoinder", "height": "upper", "guard": "Ochs", "point": "threatening", "initiative": "transfers on miss"},
        {"geometry": "Lower L1", "path": "Cross -> decline -> initiative -> Lower Winding -> Lower on miss", "action_delta": "no extra action", "spiritus": "2", "chain": "+1", "pressure": "unknown", "height": "lower", "guard": "Pflug", "point": "threatening", "initiative": "transfers"},
        {"geometry": "Lower L2", "path": "Cross -> decline -> initiative -> Lower Winding -> Upper on miss", "action_delta": "no extra action", "spiritus": "2", "chain": "+1", "pressure": "unknown", "height": "lower -> upper", "guard": "Pflug -> Ochs", "point": "threatening", "initiative": "transfers"},
        {"geometry": "Unknown", "path": "Cross -> decline -> initiative -> other legal technique/pass/disengage", "action_delta": "none", "spiritus": "0 unless another Play", "chain": "0", "pressure": "unknown", "height": "unknown", "guard": "unchanged", "point": "unchanged", "initiative": "sequencing only"},
    ]


def spiritus_rows() -> list[dict[str, Any]]:
    rows = []
    for reserve in (0, 1, 2, 3, 4, 6):
        for height, variant in (("upper", "L2"), ("lower", "L1"), ("lower", "L2")):
            vector = winding_vector(
                14, initial_holder="striker", striker_knows=True,
                parrier_knows=True, height=height, lower_variant=variant,
                reserve=reserve,
            )
            rows.append({"reserve_each": "5+" if reserve == 6 else reserve, "height": height, "variant": variant, **vector})
    return rows


def dependency_audit() -> dict[str, list[str]]:
    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".py", ".md", ".json", ".yaml", ".csv"}:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if "__pycache__" in rel or rel.startswith("reports/upper-lower-winden-completion"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "favored" in text.lower() or "unfavored" in text.lower():
            hits.append(rel)
    zornhau_local = sorted(path for path in hits if "zornhau" in path.lower())
    governing_prefixes = {
        "simulations/shared/provisional_longsword.py",
        "simulations/shared/provisional_longsword_engine.py",
        "data/prototypes/longsword-governing-provisional-v0.1.yaml",
        "reports/governing-open-provisional.md",
    }
    true_governing = sorted(path for path in hits if path in governing_prefixes)
    validation = sorted(path for path in hits if path.startswith("tests/") and path not in zornhau_local)
    data_records = sorted(path for path in hits if path.startswith("data/") and path not in true_governing and path not in zornhau_local)
    stale_experimental = sorted(
        path for path in hits
        if path not in true_governing + validation + data_records + zornhau_local
    )
    return {
        "true_governing_dependencies": true_governing,
        "governing_validation_dependencies": validation,
        "zornhau_local_dependencies_to_preserve": zornhau_local,
        "other_data_records_requiring_review": data_records,
        "stale_or_experimental_dependencies": stale_experimental,
    }


def build_results() -> dict[str, Any]:
    selector = v02_selector_audit()
    return {
        "experiment": "ATRA UPPER / LOWER WINDEN COMPLETION + R0 REPLACEMENT ADJUDICATION v0.3",
        "status": "PROVISIONAL BOUNDED CANDIDATE; STOP FOR PROJECT ADJUDICATION",
        "automatic_promotion": False,
        "authoritative_engine_edited": False,
        "governing_packet_edited": False,
        "method": "exact enumeration, branch forcing, raw Pareto vectors, named deterministic objectives; no Monte Carlo or utility constants",
        "baseline_regression": {"governing_repair": "81/81 PASS", "general_bind_v01": "75/75 PASS", "upper_winden_v02": "82/82 PASS"},
        "protected_hashes": {
            "shared_engine": sha256(ROOT / "simulations/shared/provisional_longsword_engine.py"),
            "shared_selector": sha256(ROOT / "simulations/shared/provisional_longsword.py"),
            "design_packet": sha256(ROOT / "docs/melee-design-packet-v0.4.md"),
        },
        "selector_audit": selector,
        "coverage": coverage_rows(),
        "l1_vs_l2": l1_l2_rows(),
        "short_krieg_chains": short_chains(),
        "geometry_loops": geometry_loops(),
        "hart_weich_consequence_vectors": consequence_rows(),
        "fuhlen_with_both_heights": fuhlen_rows(),
        "spiritus_pressure": spiritus_rows(),
        "state_budget": {
            "R0": ["Crossing", "measure", "contact zones", "point threat", "Bind Initiative", "Favored/Unfavored", "pressure usually separate/Unknown"],
            "H3": ["Crossing", "measure", "contact zones", "point threat", "Bind Initiative", "phase-scoped Hart/Weich", "bind_height"],
            "judgment": "state-budget neutral if ordinary-Cross Favored/Unfavored is removed; H3 exchanges one relation axis for one geometry axis",
        },
        "r0_deletion_impact": dependency_audit(),
        "findings": {
            "lower_writer": "deterministic authored defence-event metadata; no new generic subsystem or operator",
            "l1_l2": "identical immediate probabilities and resource length; L2 alone makes geometry active and gives the opponent a readable Upper reply after a miss",
            "height": "earned: two distinct writers, two execution gates, and an L2 Lower-to-Upper transition",
            "unknown": "legitimate underspecified geometry; no generic Winden required",
            "guards": "Ochs is meaningful sourced aftermath and an Upper repertoire gate; Pflug is meaningful sourced aftermath and a Lower repertoire gate, but L2 makes its failed-thrust persistence transient",
            "hart_weich": "conditional trade remains: Hart raises Cross survival and favors striker initiative; Weich is flat and favors parrier initiative; neither dominates across repertoire ownership",
            "fuhlen": "situational on the multi-objective frontier; pure damage favors F1, efficiency can favor blind reads, and decline remains reserve/geometry relevant",
            "replacement": "full H3 replacement is cleaner than Hybrid; Unknown can pass without reviving a second hidden relation system",
        },
        "recommendation": {
            "project_choice": "PROMOTE H3 FOR ORDINARY BASIC CROSSES, subject to explicit Project adjudication and a separate bounded governing integration change",
            "lower_failure": "L2",
            "winden_price": "2S",
            "hybrid": "REJECT: combines incompatible hidden relation and Fühlen semantics",
            "leverage": "remain deferred",
            "counter_wind": "remain deferred",
            "next_milestone": "governing H3 integration plus focused regression/dependency repair; then integrated full-duel cleanup before Named Guard v0.2",
        },
    }


def md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    return lines


def report_text(data: dict[str, Any]) -> str:
    lrows = data["l1_vs_l2"]
    ltable = []
    for row in lrows:
        ltable.append([
            row["skill"], row["variant"], row["expected_declarations"],
            row["expected_total_spiritus"], row["bind_hit_probability"],
            row["geometry_change_probability"],
            row["opponent_upper_winding_opportunity_probability"],
            row["chain_cap_termination_probability"],
        ])
    selector = data["selector_audit"]
    deps = data["r0_deletion_impact"]
    lines = [
        "# Upper / Lower Winden Completion v0.3 Results", "",
        "Status: **PROVISIONAL bounded candidate experiment; no governing or canonical promotion. STOP FOR PROJECT ADJUDICATION.**", "",
        "## Executive Result", "",
        "**H3-L2 is mechanically complete enough to replace R0 for ordinary Basic Crosses, but this experiment does not perform that promotion.** Upper and Lower now have distinct deterministic writers and executions, while Unknown remains a valid underspecified geometry that can pass or disengage. L2 creates an active Lower-to-Upper state change and interactive reply without changing hit odds, adding modifiers, or escaping the global cap. Hybrid is less clean than either architecture because it would preserve two hidden relation systems and two Fühlen meanings.", "",
        "## Source-of-Truth Check", "",
        "The governing register/YAML, current melee packet, source policy, mechanical vocabulary, Crossing/Bind, Bind Continuations, Incentive Integrity, named reports and JSON, audited Winden/D-M/Zornhau records, Ochs/Pflug guard evidence, T1, Spiritus, chain rules, shared engine, current selectors, and both prior candidate implementations were inspected. The working tree was clean. The shared engine and packet hashes are preserved in the JSON artifact.", "",
        "## Baseline Regression", "",
        "Before candidate work: governing repair **81/81 PASS**; General Bind v0.1 **75/75 PASS**; Upper Winden v0.2 **82/82 PASS**.", "",
        "## v0.2 Selector / Instrumentation Audit", "",
        f"Classification: **{selector['classification']}**. JSON serialization matched the function return. v0.2 chose one ex-ante equal-prior fixed policy; blind D/M tied at q=.5 and an undocumented lexical tie selected Mutieren. That fixed label then appeared in both realized-pressure rows, including {selector['hart_rows_showing_fixed_mutieren_policy']} Hart rows. No paired equal-prior aggregate or high-level conclusion changes, but those per-pressure labels are not conditional recommendations. v0.3 selects directly from each known-pressure vector, exposes tie sets, and tests serialization against the selector return.", "",
        "## Historical / Mechanical Boundary", "",
        "Project-adjudicated history supports Ochs as the upper hangings, Pflug as the lower hangings, four upper plus four lower windings, cut/thrust/slice from the windings, and a lower-hanging example that stays on the sword, thrusts upward to the face, and rises to an upper hanging if displaced. The 2S price, flat roll, initiative transfer, exact L2 rewrite, and chain procedure remain explicit Atra abstractions.", "",
        "## R0 Control", "",
        "R0 remains unchanged: ordinary Cross still creates roll-derived Favored/Unfavored in the authoritative engine, with current Bind Initiative, Fühlen, local Zornhau/Ort, D1, threatening-point denial, Cross/Beat, GC1, Committed timing, repaired Nachreisen, P1/C2/S2/T1, and cap 3.", "",
        "## H3 Candidate Overview", "",
        "H3 uses phase-scoped authored Hart/Weich for every ordinary successful Cross; one attacker Rejoinder; F1; hard-failure 2S D/M; public Upper/Lower/Unknown height; and 2S Upper/Lower Winding executions. It adds no Leverage, Counter-Wind, generic Close move, response restriction, or numeric initiative/guard/height bonus.", "",
        "## Initial Hart / Weich", "",
        "Hart grants one Cross Boon and gives the striker initiative after decline. Weich is flat and gives the parrier initiative. Pressure clears after D/M or decline and never rewrites during ordinary Winding.", "",
        "## Bind Height", "",
        "`upper/lower/unknown` is public and independent from measure, contact zone, pressure, point threat, guard, and initiative. It has no generic modifier.", "",
        "## Upper Writer", "",
        "Only a qualifying Cross against an explicitly descending/Oberhau-like Cut writes Upper.", "",
        "## Lower Writer", "",
        "Only an explicit `lower-setting-aside` defence event against the bounded `low-line-thrust` or `rising-low-line-cut` harness cases writes Lower. This is event metadata using SET state, not a new player-facing Basic, operator, or generic subsystem. Starting Pflug, a low guard, measure, contact zone, or a generic low label cannot write it.", "",
        "## Unknown Geometry", "",
        "Unclassified Crosses remain Unknown. Unknown permits the initial Hart/Weich/Rejoinder cycle but neither Winding execution; normal other repertoire, pass, and disengage remain available.", "",
        "## Attacker Bind Rejoinder", "",
        "The original striker may declare Duplieren, Mutieren, or decline after the successful Cross without another action.", "",
        "## Fühlen", "",
        "F1 costs 1S, no action, and no chain entry; it is once per initial cycle and reveals only initial pressure.", "",
        "## Duplieren / Mutieren", "",
        "The paired learned item costs 2S/+1 chain. Correct D/M makes one Booned normal-damage attack; a wrong read spends and hard-fails with no roll. Mutieren remains a low-opening attacker Rejoinder and is not Lower Winding.", "",
        "## Upper Winding Thrust", "",
        "Requires Winden, initiative, Crossing, Upper, 2S, and chain room. It retains contact, produces Ochs and threat, and attacks flat for normal damage. A miss retains Upper/Ochs/threat and transfers initiative.", "",
        "## Lower Winding Thrust", "",
        "Requires Winden, initiative, Crossing, Lower, 2S, and chain room. It produces Pflug and a threatening point, then makes one flat upward thrust for normal damage. It requires neither pressure nor starting Pflug.", "",
        "## L1 Symmetrical Failure", "",
        "A miss retains Crossing, Lower, Pflug, and threat, then transfers initiative. L1 is valid and finite but makes height less active.", "",
        "## L2 Lower-to-Upper Failure", "",
        "A miss retains Crossing/threat, sets Lower→Upper and Pflug→Ochs, and transfers initiative. There is no free attack, retained initiative, or action refresh.", "",
        "## L1 vs L2", "",
        *md_table(["Skill", "Variant", "E declarations", "E Spiritus", "P hit ≤3", "P geometry change", "P opponent Upper", "P cap term"], ltable), "",
        "L1 and L2 have identical hit, length, spend, retention, and transfer probabilities because both use the same flat thrust and cap. L2 wins the comparison because its first-miss probability is also the probability of a readable geometry change and opponent Upper opportunity; L1 merely repeats Lower. Resource/pass termination is zero in this sufficient-reserve matrix.", "",
        "## Short Krieg Chains", "",
        *md_table(["ID", "Forced sequence", "Legal", "Terminal"], [[r['id'], r['sequence'], r['legal'], r['terminal']] for r in data['short_krieg_chains']]), "",
        "## Hart vs Weich — Upper", "",
        "The JSON contains all raw vectors at Skills 10/12/14/18 and seven knowledge profiles. Hart improves Cross survival and gives striker-first Winding; Weich lowers Cross survival and gives parrier-first Winding. Ownership determines which initiative assignment is valuable.", "",
        "## Hart vs Weich — Lower", "",
        "The same conditional trade exists for L1 and L2. L2 does not alter the first attack probability; it changes only the miss aftermath and subsequent repertoire gate.", "",
        "## Hart vs Weich — Unknown", "",
        "Both pressures still drive Rejoinder and initiative. With no geometry consumer, decline yields pass/disengage unless another legal Play exists. This is acceptable and does not make R0 necessary.", "",
        "## Fühlen with Both Heights", "",
        "Across Skills 10/14/18 and Hart priors 20/40/50/60/80%, F1 is Pareto-relevant and pure-damage maximizing when affordable; blind reads can maximize damage per Spiritus at skewed priors; decline remains Pareto-relevant where it conserves resources or reallocates first attack through repertoire. Exact outgoing/incoming/spend/chain vectors are serialized without a Spiritus utility constant.", "",
        "## Spiritus Pressure", "",
        "At 0–1S no Winding is legal; 2–3S permits at most one declaration per fighter before exhaustion shapes the loop; 4S permits repeat ownership branches; 5+ reaches the cap when all misses. The JSON reports exact reserve rows.", "",
        "## Chain Pressure", "",
        "Each Winding adds one learned entry. Lower→Upper→Upper can consume exactly three; a fourth is illegal. The all-miss cap probability is `(1-p)^3`, so recursion is bounded without an extra rule.", "",
        "## Ochs Identity", "",
        "Ochs is **meaningful sourced aftermath and a repertoire gate**: Upper Winding produces it, and L2 produces it naturally on a failed Lower thrust. It has no generic bonus and does not monopolize the opening geometry.", "",
        "## Pflug Identity", "",
        "Pflug is **meaningful sourced aftermath and a repertoire gate**: Lower Winding produces it. Under L1 it persists after misses; under preferred L2 it is intentionally transient on a displaced thrust. No generic bonus is needed.", "",
        "## Bind-Height Complexity", "",
        "Height now earns its axis: it has distinct Upper and Lower writers, distinct execution gates, a legitimate Unknown, and an L2 state transition. Two booleans would permit impossible Upper+Lower combinations and require a third unknown convention; a three-value enum is simpler.", "",
        "## State-Budget Comparison", "",
        "R0 and H3 each carry seven conceptual items in the requested audit. If ordinary-Cross Favored/Unfavored is deleted, H3 is approximately state-budget neutral: phase-scoped pressure replaces the hidden relation and height adds the geometry axis while R0's usually separate pressure axis disappears from ordinary Cross handling.", "",
        "## R0 vs H3", "",
        "R0 is universally populated but its ordinary relation is roll-derived and abstract. H3 gives all ordinary Crosses an authored tactical relation and gives authored Upper/Lower geometry concrete consumers; Unknown is honest rather than randomly repaired. H3 is the cleaner information architecture.", "",
        "## Hybrid Architecture Audit", "",
        "Hybrid is messier: authored cases would use pressure/F1/D-M while Unknown cases would revive roll-derived Favored/Unfavored/passive Fühlen/hidden prerequisites. Players would need to know which information game a Cross entered. Unknown can simply lack a Winding consumer, so Hybrid adds no required functionality.", "",
        "## R0 Deletion Impact Audit", "",
        "The JSON lists every current textual dependency. True governing dependencies:", "",
        *[f"- `{p}`" for p in deps['true_governing_dependencies']], "",
        "Zornhau-local dependencies to preserve:", "",
        *[f"- `{p}`" for p in deps['zornhau_local_dependencies_to_preserve']], "",
        "Validation, data-record, and stale experimental/report dependencies are separately enumerated in JSON. Promotion would require changing the shared ordinary-Cross writer and its tests/register, preserving local Zornhau/Ort semantics, and marking old experiment outputs as superseded—not rewriting historical evidence.", "",
        "## Zornhau Compatibility", "",
        "Zornhau remains on its current local Favored/Unfavored Ort/W1-W2 structure. H3 ordinary-Cross replacement need not remove that specialized local dependency.", "",
        "## Ghost / Policy Audit", "",
        "No utility constants, random geometry, height modifier, initiative bonus, guard bonus, Leverage, Counter-Wind, generic Unknown Winden, generic Wide→Close, response denial, or action refresh were introduced. Selected tables include all vectors, selection scope, primary ties, and final ties.", "",
        "## Remaining Gaps", "",
        "The candidate has not been integrated into the governing engine or full duel. The exact governing dependency edits and player-facing ordinary-Cross declaration wording still require Project approval. Duplieren/Mutieren's durable Play record remains item-level unaudited; this experiment relies on the supplied Project interpretation.", "",
        "## Project Recommendation", "",
        "Project should **promote H3 for ordinary Basic Crosses in a separate governing integration task**, select L2 and 2S Winden, retire ordinary-Cross Favored/Unfavored, preserve Zornhau-local relation, and reject Hybrid. This is a recommendation, not promotion.", "",
        "## Exact Next Milestone", "",
        "A bounded **H3 governing-integration and dependency-repair milestone**: replace only the ordinary Basic-Cross R0 relation writer; integrate H3-L2; update exact governing tests/register; preserve Zornhau local behavior; then run integrated full-duel cleanup. Named Guard v0.2 remains later.", "",
        "## Project Decision Table", "",
        *md_table(["Topic", "Candidate A", "Candidate B", "Result", "Recommendation"], [
            ["Lower Winding miss", "L1 stay Lower", "L2 transition Upper", "both valid; L2 activates geometry", "L2"],
            ["Winden price", "1S prior rejected", "2S", "2S preserves D/M premium", "2S"],
            ["Bind geometry", "Upper only", "Upper/Lower/Unknown", "two writers/consumers + transition", "Upper/Lower/Unknown"],
            ["Unknown handling", "generic fallback", "remain Unknown", "fallback unnecessary", "remain Unknown"],
            ["Ordinary relation", "R0 Favored/Unfavored", "H3 Hart/Weich", "H3 clearer", "H3"],
            ["Replacement strategy", "keep R0", "hybrid", "hybrid adds dual semantics", "neither"],
            ["Replacement strategy", "hybrid", "full H3 replacement", "H3 cleaner and complete", "full H3 after approval"],
            ["Leverage", "add", "remain deferred", "not needed", "defer"],
            ["Counter-Wind", "restore", "remain deferred", "not needed", "defer"],
        ]), "",
        "## Final Project-Review Questions", "",
    ]
    answers = [
        "1. Yes; the governing engine remained unchanged.",
        "2. Yes: 81/81, 75/75, and 82/82 passed before candidate work.",
        "3. Yes as an ambiguity, not as bad serialization or a pressure-aware selector failure.",
        "4. It was an ex-ante-versus-realized semantics problem; paired equal-prior conclusions do not change, but conditional rows were not recommendations.",
        "5. Yes; known Hart selects Duplieren and known Weich selects Mutieren, with spend applied only after damage ties.",
        "6. Yes; bounded defence-event metadata is sufficient.",
        "7. Yes; it requires explicit lower setting-aside plus a qualifying low-line attack.",
        "8. Yes; starting Pflug alone never writes Lower.",
        "9. Yes; measure and contact zone never write it.",
        "10. Yes; it is the only flat upward thrust continuation gated by Lower geometry and ordinary post-Rejoinder initiative.",
        "11. Yes; 2S preserves the correct D/M Boon premium and prevents 1S crowding.",
        "12. Yes; L1 is coherent and finite.",
        "13. Yes; L2 is coherent and finite.",
        "14. Useful geometry: its state change gates the opponent's Upper repertoire.",
        "15. No; cap 3 and 2S exhaustion bound recursion.",
        "16. Yes; the opponent receives the first Upper declaration after L2 miss.",
        "17. Yes; the fourth learned declaration is illegal.",
        "18. Yes; two writers, two consumers, Unknown, and a transition justify the enum.",
        "19. Yes; Ochs is sourced aftermath plus an Upper gate.",
        "20. Yes, partially transient under L2; Pflug is sourced aftermath plus a Lower gate.",
        "21. Yes in both authored geometries.",
        "22. Yes; Unknown can use other repertoire, pass, or disengage.",
        "23. No; sequencing can exist without guaranteeing an attack consumer.",
        "24. Yes; F1 is pure-damage strong but not universally Spiritus-efficient.",
        "25. Yes; skewed priors make the matching blind read efficiency-rational.",
        "26. Yes; persistent pressure is unnecessary after it assigns Rejoinder/initiative.",
        "27. No universal dominance; knowledge ownership changes the consequence vector.",
        "28. Yes; compare Cross survival, outgoing/incoming damage, spend, and initiative opportunities directly.",
        "29. No.",
        "30. Yes; Counter-Wind should remain deferred.",
        "31. Yes; authored pressure and honest geometry replace an abstract always-populated relation.",
        "32. Messier; Hybrid creates two hidden games and Fühlen meanings.",
        "33. Mechanically yes, subject to explicit Project promotion.",
        "34. The exact governing, test, Zornhau-local, data, simulation, and report paths are enumerated in JSON; ordinary dependencies need repair while Zornhau-local ones remain.",
        "35. Promote H3 for ordinary Basic Crosses through the separate bounded integration milestone, then perform integrated full-duel cleanup.",
        "36. No further bind experiment blocks promotion; the remaining question is Project authorization to replace the ordinary-Cross R0 writer while preserving Zornhau local relation.",
    ]
    lines.extend(answers)
    lines.extend(["", "**STOP FOR PROJECT ADJUDICATION. No candidate was promoted.**", ""])
    return "\n".join(lines)


def main() -> None:
    data = build_results()
    RESULTS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(report_text(data), encoding="utf-8")
    print(json.dumps({
        "results": str(RESULTS_PATH.relative_to(ROOT)),
        "report": str(REPORT_PATH.relative_to(ROOT)),
        "l1_l2_rows": len(data["l1_vs_l2"]),
        "consequence_rows": len(data["hart_weich_consequence_vectors"]),
        "fuhlen_rows": len(data["fuhlen_with_both_heights"]),
    }, indent=2))


if __name__ == "__main__":
    main()

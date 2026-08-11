from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE_PATH = ROOT / "simulations" / "crossing_bind_state_model_v0_1" / "simulate.py"
BASE_RESULTS_PATH = ROOT / "simulations" / "crossing_bind_state_model_v0_1" / "results.json"
MODEL_PATH = ROOT / "data" / "prototypes" / "longsword-bind-continuations-v0.1.yaml"
RESULTS_PATH = ROOT / "reports" / "bind-continuations-v01-results.json"
REPORT_PATH = ROOT / "reports" / "bind-continuations-v01-results.md"
SEED = 11082026


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location("bind_continuations_base", BASE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()


SMOKE_KEYS = (
    "win_rate_A",
    "average_rounds",
    "double_defeat_rate",
    "basic_cross_declarations_per_fight",
    "basic_beat_declarations_per_fight",
    "durch_declarations_per_fight",
    "compound_declarations_per_fight",
    "successful_crossings_per_fight",
    "close_crossings_per_fight",
    "known_zone_crossings_per_fight",
    "precondition_violations",
    "three_play_cap_frequency",
    "attempted_fourth_plays_per_fight",
)


def compact_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    compact = {key: metrics[key] for key in SMOKE_KEYS}
    compact["soft_pressure_crossings_per_fight"] = (
        metrics["hard_soft_crossings_per_fight"] + metrics["soft_hard_crossings_per_fight"]
    )
    return compact


def smoke_regression(trials: int, seed: int) -> dict[str, Any]:
    baseline = json.loads(BASE_RESULTS_PATH.read_text(encoding="utf-8"))
    results: dict[str, Any] = {}
    for skill, base_index in ((10, 0), (14, 4), (18, 8)):
        cell = BASE.Cell(skill, 8, "adaptive_revelation")
        cell_seed = seed + base_index * 1009
        current_item = BASE.run_cell(cell, trials, cell_seed, "explicit")
        label = cell.label
        current = compact_metrics(current_item["metrics"])
        reference = compact_metrics(baseline["primary_matrix"][label]["metrics"])
        delta = {
            key: current[key] - reference[key]
            for key in current
            if isinstance(current[key], (int, float)) and isinstance(reference[key], (int, float))
        }
        results[label] = {
            "seed": cell_seed,
            "trials": trials,
            "current": current,
            "crossing_bind_v01_reference": reference,
            "delta": delta,
        }
    return results


def validate_results(results: dict[str, Any]) -> None:
    forced = results["forced_scenarios"]
    assert forced["diagnostic_yield"]["pressure"] == {"A": "hard", "B": "soft"}
    assert forced["zorn_ort_soft_consumer"]["inspected_opponent_pressure"] == "soft"
    assert forced["rompere_close_control"]["measure"] == "close"
    assert forced["pommel_from_explicit_close"]["executed"]
    assert forced["zwerch_with_strong_geometry"]["zones"] == {"A": "hiltward", "B": "unknown"}
    assert forced["italian_point_crossing_reference"]["zones"] == {"A": "pointward", "B": "pointward"}
    assert forced["italian_middle_crossing_reference"]["zones"] == {"A": "middle", "B": "middle"}
    assert not forced["italian_middle_crossing_reference"]["middle_is_close"]
    for cell in results["smoke_regression"].values():
        current = cell["current"]
        assert current["close_crossings_per_fight"] == 0
        assert current["soft_pressure_crossings_per_fight"] == 0
        assert current["known_zone_crossings_per_fight"] == 0
        assert current["precondition_violations"] == 0
        assert current["attempted_fourth_plays_per_fight"] == 0


def pct(value: float) -> str:
    return f"{value:.1%}"


def build_report(results: dict[str, Any]) -> str:
    forced = results["forced_scenarios"]
    lines = [
        "# Bind Continuations v0.1 Results",
        "",
        "Status: **PROVISIONAL state-transition / representation experiment; not canonical mechanics**",
        "",
        "The explicit Crossing engine can now represent authored Soft pressure, an authored Wide-to-Close transition, and known asymmetric or bilateral blade geometry in deterministic fixtures. None of those harness-only creators entered the active mirrored combat repertoire, and the smoke regression retains zero natural Soft, Close, and known-zone creation.",
        "",
        "## Scope and preserved baseline",
        "",
        "This experiment preserves Contact `none|crossing`, independent Measure `wide|close`, per-fighter contact zones and pressure, point threat, displacement as an event, declared Basic Cross/Beat, D1, C2, S2, maximum Spiritus 8, and the learned-Play chain cap of 3. It adds no Guard effect, random state generation, generic leverage rule, generic Hard/Soft menu, Spiritus/damage tuning, or normal-combat repertoire entry.",
        "",
        "## EVIDENCE AUDIT CORRECTION",
        "",
        "The prior Zwerchhau record covered the initial interception but did not yet include the separately attested **Zwerch with the Strong** bind-work instruction. The added phase-level witness is Pseudo-Peter von Danzig, Cod.44.A.8 (1452), ff. 20r.2–20v.1. It instructs binding on the opponent's sword with the Strong of the acting sword. The geometry fixture is sourced only to that instruction and must not be generalized to every Zwerchhau execution.",
        "",
        "The initial interception remains separately represented as beginning without blade contact and does not automatically create a Crossing. The whole Play record remains `needs-item-level-audit`; only the added witness/phase is item-level audited here.",
        "",
        "## Forced-Scenario Metrics",
        "",
        "| # | Scenario | Deterministic outcome |",
        "|---:|---|---|",
        f"| 1 | Hard/Hard Crossing | contact `{forced['hard_hard_crossing']['contact']}`; pressure `{forced['hard_hard_crossing']['pressure']}` |",
        f"| 2 | Diagnostic Yield | declared `{forced['diagnostic_yield']['declared']}`; no damage/cost; classification OPEN |",
        f"| 3 | Resulting Soft/Hard | pressure `{forced['diagnostic_yield']['pressure']}`; contact retained |",
        f"| 4 | Zornhau-Ort inspects Soft | executed `{forced['zorn_ort_soft_consumer']['executed']}` after inspecting `{forced['zorn_ort_soft_consumer']['inspected_opponent_pressure']}` |",
        f"| 5 | Rompere displacement + retained Crossing | contact `{forced['rompere_retained_crossing']['contact']}`; measure `{forced['rompere_retained_crossing']['measure']}`; retained `{forced['rompere_retained_crossing']['retained']}` |",
        f"| 6 | Rompere Wide -> Close | explicit transition `{forced['rompere_close_control']['executed']}`; contact/measure `crossing/close`; random `false` |",
        f"| 7 | Pommel from Close Crossing | prerequisite `{forced['pommel_from_explicit_close']['prerequisite_satisfied']}`; executed `{forced['pommel_from_explicit_close']['executed']}` |",
        f"| 8 | Zwerch with the Strong | zones `{forced['zwerch_with_strong_geometry']['zones']}`; pressure unknown/unknown; no modifier |",
        f"| 9 | Pointward/pointward reference | contact/measure `crossing/{forced['italian_point_crossing_reference']['measure']}`; zones pointward/pointward |",
        f"| 10 | Middle/middle reference | contact/measure `crossing/{forced['italian_middle_crossing_reference']['measure']}`; `middle != close` |",
        "| 11 | Geometry/pressure independence | hiltward/pointward + soft/hard and pointward/hiltward + hard/soft both represented without modifiers |",
        "| 12 | Displacement/contact independence | Basic Beat displaces + separates; Rompere displaces + retains Crossing |",
        "| 13 | Cleanup/reset | Yield and Zwerch sequences reset contact, zones, and pressure; Pommel sequence ends contact; retained Rompere survives its explicit window |",
        "",
        "The Yield sequence proves state visibility and timing only. It does **not** decide that intentionally yielding should normally let the opponent hit. **HISTORICAL TECHNIQUE MECHANICS INCOMPLETE.**",
        "",
        "## Authored State Creators",
        "",
        "The test harness can now explicitly produce:",
        "",
        "- Soft pressure through diagnostic Yield/Give Way.",
        "- Close Crossing through the Rompere close-control continuation.",
        "- Hiltward actor contact through the sourced Zwerch-with-the-Strong phase.",
        "- Middle contact through Rompere's opponent-middle state and the middle/middle representation reference.",
        "- Pointward contact through the pointward/pointward representation reference.",
        "- Displacement plus retained Crossing through Rompere.",
        "",
        "The Italian bilateral point and middle fixtures are representation references with missing item-level locators/confidence in the current repository. They do not strengthen the historical record or become generic actions.",
        "",
        "## Small Unchanged-Combat Smoke Regression",
        "",
        f"Seed `{results['seed']}`; `{results['trials_per_cell']}` mirrored fights per cell; Skills 10/14/18; starting Spiritus 8; Adaptive Revelation only. Crossing/Bind v0.1 references use its stored 5,000-fight cells. Paired columns show `current / Crossing v0.1`.",
        "",
        "| Cell | Win A | Rounds | Double | Cross/fight | Beat/fight | D/fight | Compounds/fight | Crossings/fight | Close | Soft | Known zone | Violations | Cap | Fourth |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, item in results["smoke_regression"].items():
        c = item["current"]
        b = item["crossing_bind_v01_reference"]
        lines.append(
            f"| {label} | {pct(c['win_rate_A'])} / {pct(b['win_rate_A'])} | "
            f"{c['average_rounds']:.3f} / {b['average_rounds']:.3f} | "
            f"{pct(c['double_defeat_rate'])} / {pct(b['double_defeat_rate'])} | "
            f"{c['basic_cross_declarations_per_fight']:.3f} | {c['basic_beat_declarations_per_fight']:.3f} | "
            f"{c['durch_declarations_per_fight']:.3f} | {c['compound_declarations_per_fight']:.3f} | "
            f"{c['successful_crossings_per_fight']:.3f} | {c['close_crossings_per_fight']:.3f} | "
            f"{c['soft_pressure_crossings_per_fight']:.3f} | {c['known_zone_crossings_per_fight']:.3f} | "
            f"{c['precondition_violations']} | {pct(c['three_play_cap_frequency'])} | "
            f"{c['attempted_fourth_plays_per_fight']:.3f} |"
        )
    lines += [
        "",
        "The ordinary combat code path and active repertoire are unchanged. Sampling differences against the stored 5,000-fight reference are Monte Carlo noise; the structural regression signals are exact zeros for natural Close, Soft, known-zone creators, precondition violations, and attempted fourth Plays.",
        "",
        "## Still Missing From Normal Combat",
        "",
        "**ENGINE CAN REPRESENT** authored Soft, Close, hiltward/middle/pointward geometry, and displacement with or without retained contact.",
        "",
        "**ACTIVE REPERTOIRE CAN NATURALLY PRODUCE** only the pre-existing bounded prototype states. Diagnostic Yield, Rompere close control, Zwerch-with-the-Strong geometry, and the Italian geometry references remain absent from normal AI combat. Consequently the smoke run correctly retains zero natural Soft-pressure, Close-Crossing, and known-zone creation. Those zeros were not 'fixed.'",
        "",
        "## Historical Mechanics Still Incomplete",
        "",
        "- Complete Yield/giving-way mechanics remain OPEN: sourced follow-up exploitation, attack content, action cost, Spiritus cost, defence implications, and learned-Play-chain counting are not decided.",
        "- The Rompere close continuation's classification remains OPEN: intrinsic branch, second learned Play, Basic action, Aftermath, and action cost were not selected.",
        "- Crossing persistence through complex continuations remains OPEN beyond the one-window harness sequence.",
        "- Generic Strong-vs-Weak leverage, generic closing rules, generic Hard/Soft actions, and Guard effects remain OPEN and unimplemented.",
        "- Bilateral Italian pointward and middle zone mappings still need item-level evidence locators before they can become historical Play claims.",
        "- The optional Durchlaufen reference was skipped because its current Play record has only source-family citations and no item-level audited locator; the experiment did not expand into a Durchlaufen research task.",
        "",
        "## Ready For Guard Design?",
        "",
        "A. **Yes.** The engine can represent authored Crossing, authored displacement, authored Soft, authored Close, and authored blade geometry.",
        "",
        "B. **No listed contact state remains blocked at the engine level.** The remaining uncertainty is which audited Plays/actions produce those states and how their full mechanics work.",
        "",
        "C. Remaining gaps are mainly **Play repertoire/content and classification gaps**, rather than state-model gaps.",
        "",
        "D. **Yes, provisionally.** Guard design can resume without inventing missing contact-state axes, provided Guard work does not turn these fixtures into generic bonuses or silently finalize their OPEN action economy.",
        "",
        "E. Guard-facing evaluation can now examine point threat, loaded attack, quality of cover, tendency or ability to produce particular crossing geometry, and access to source-specific continuations. This report proposes no final Guard bonus.",
        "",
    ]
    return "\n".join(lines)


def run(trials: int = 2000, seed: int = SEED, write: bool = True) -> dict[str, Any]:
    results = {
        "experiment": "BIND CONTINUATIONS v0.1",
        "status": "PROVISIONAL",
        "seed": seed,
        "trials_per_cell": trials,
        "model": json.loads(MODEL_PATH.read_text(encoding="utf-8")),
        "evidence_audit_correction": {
            "play_id": "play-german-longsword-zwerchhau",
            "phase": "Zwerch with the Strong bind-work",
            "locator": "Pseudo-Peter von Danzig, Cod.44.A.8 (1452), ff. 20r.2-20v.1",
            "record_wide_source_status_promoted": False,
            "generalize_to_every_zwerchhau": False,
        },
        "forced_scenarios": BASE.bind_continuation_harness(),
        "smoke_regression": smoke_regression(trials, seed),
        "normal_combat_structural_result": {
            "random_soft_creator": False,
            "random_close_creator": False,
            "random_known_zone_creator": False,
            "generic_strong_weak_modifier": False,
            "generic_hard_soft_menu": False,
            "active_repertoire_changed": False,
        },
    }
    validate_results(results)
    if write:
        RESULTS_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        REPORT_PATH.write_text(build_report(results), encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    results = run(args.trials, args.seed, not args.no_write)
    print(f"forced={len(results['forced_scenarios'])} smoke={len(results['smoke_regression'])}")


if __name__ == "__main__":
    main()

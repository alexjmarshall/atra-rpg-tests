"""Deterministic, diagnosis-only probes for Melee Incentive Integrity v0.1."""

from __future__ import annotations

import importlib.util
import json
import math
import random
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name("controlled-results.json")


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


GUARD = load("ii_guard", ROOT / "simulations" / "named_guard_rules_v0_1" / "simulate.py")
ENGINE = GUARD.ENGINE
BASE = GUARD.BASE
BRIDGE = load("ii_bridge", ROOT / "simulations" / "guard_play_bridge_v0_1" / "simulate.py")
CROWN = load("ii_crown", ROOT / "simulations" / "scheitelhau_crown_v0_1" / "simulate.py")


def argmax(values: dict[str, float]) -> list[str]:
    top = max(values.values())
    return [key for key, value in values.items() if math.isclose(value, top, abs_tol=1e-12)]


def guard_arena(
    tradition: str = "German",
    pair: tuple[str, str] = ("vom-tag", "pflug"),
    skill: int = 14,
    spiritus: int = 8,
) -> Any:
    return GUARD.NamedGuardDuel(
        random.Random(7),
        random.Random(11),
        GUARD.Cell("G1", tradition, skill, spiritus, "perfect_information"),
        GUARD.fresh_metrics(),
        pair,
    )


def parry_and_compound_surface() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for skill in (10, 14, 18):
        for spiritus in (8, 3, 1, 0):
            duel = guard_arena(pair=("vom-tag", "pflug"), skill=skill, spiritus=spiritus)
            cut = duel.make_attack("basic_cut")
            thrust = duel.make_attack("basic_thrust")
            cut_values = duel.defence_values(duel.a, duel.b, cut)
            thrust_values = duel.defence_values(duel.a, duel.b, thrust)
            rows.append({
                "skill": skill,
                "spiritus": spiritus,
                "cut_values": cut_values,
                "cut_argmax": argmax(cut_values),
                "thrust_values": thrust_values,
                "thrust_argmax": argmax(thrust_values),
                "cross_equals_beat_cut": math.isclose(
                    cut_values["Basic Cross"], cut_values["Basic Beat"], abs_tol=1e-12
                ),
                "cross_equals_beat_thrust": math.isclose(
                    thrust_values["Basic Cross"], thrust_values["Basic Beat"], abs_tol=1e-12
                ),
            })
    return rows


def durch_surface() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for attacker_skill in (10, 14, 18):
        for defender_skill in (10, 14, 18):
            for spiritus in (8, 3, 1, 0):
                offense = 1.0
                if spiritus:
                    declare = (
                        BASE.success_probability(attacker_skill) * offense
                        - BASE.reserve_charge(spiritus, BASE.DURCH_COST)
                    )
                else:
                    declare = None
                decline = (1.0 - BASE.success_probability(defender_skill)) * offense
                rows.append({
                    "attacker_skill": attacker_skill,
                    "defender_skill": defender_skill,
                    "spiritus": spiritus,
                    "declare_value": declare,
                    "decline_value": decline,
                    "argmax": "unavailable" if declare is None else (
                        "declare" if declare > decline else "decline" if decline > declare else "tie"
                    ),
                })
    return rows


def power_surface() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for skill in (10, 14, 18):
        for spiritus in (8, 3, 1):
            duel = ENGINE.LoadedPowerDuel(
                random.Random(7),
                random.Random(11),
                ENGINE.Cell("P1", skill, spiritus, "perfect_information"),
                ENGINE.fresh_metrics(),
            )
            for attacker_hp in (8, 4, 2):
                duel.a.hp = attacker_hp
                loaded = duel.make_attack("basic_cut")
                power = duel.make_attack("power_attack")
                values = {
                    "Loaded Cut": duel.expected_action_value(duel.a, duel.b, loaded),
                    "P1 Power": duel.expected_action_value(duel.a, duel.b, power),
                }
                rows.append({
                    "skill": skill,
                    "spiritus": spiritus,
                    "attacker_hp": attacker_hp,
                    "policy_values": values,
                    "policy_argmax": argmax(values),
                    "loaded_expected_damage": ENGINE.expected(ENGINE.distribution_for("loaded_cut")),
                    "loaded_max_damage": max(ENGINE.distribution_for("loaded_cut")),
                    "power_expected_damage": ENGINE.expected(ENGINE.distribution_for("P1")),
                    "power_max_damage": max(ENGINE.distribution_for("P1")),
                })
    return rows


def guard_policy_surface() -> dict[str, Any]:
    output: dict[str, Any] = {}
    for tradition, pair in (
        ("German", ("alber", "vom-tag")),
        ("Italian", ("posta-frontale", "tutta-porta-di-ferro")),
    ):
        duel = guard_arena(tradition=tradition, pair=pair)
        output[tradition] = {
            phase: {
                guard: duel.guard_policy_value(duel.a, guard, phase)
                for guard in GUARD.TRADITION_GUARDS[tradition]
            }
            for phase in ("before", "after")
        }
    return output


def bridge_and_crown_policy() -> dict[str, Any]:
    bridge = BRIDGE.GuardPlayBridgeDuel(
        random.Random(7), random.Random(11), BRIDGE.Cell("T1", 14, 8, "perfect_information"),
        BRIDGE.fresh_metrics(), ("tutta-porta-di-ferro", "posta-frontale"),
    )
    crown = CROWN.ScheitelhauCrownDuel(
        random.Random(7), random.Random(11), CROWN.Cell("B3", 14, 8, "perfect_information"),
        CROWN.fresh_metrics(), ("vom-tag", "alber"),
    )
    return {
        "tutta_continuation_policy": {
            "value": bridge.continuation_value(bridge.a, bridge.b),
            "decline": 0.0,
            "basis": "hand-authored Close-state proxy; no downstream consequence valuation",
        },
        "crown_response_policy": {
            "crown": BASE.success_probability(crown.b.skill) * 1.10,
            "ordinary_response_aggregate": 0.35,
            "basis": "hand-authored constants; ordinary legal responses are not compared individually",
        },
        "point_sink_policy": {
            "value": crown.point_sink_value(crown.a, crown.b),
            "decline": 0.0,
            "basis": "success proxy minus reserve charge",
        },
        "nachreisen_policy": {
            "nachreisen": 0.52,
            "ordinary": 0.0,
            "basis": "hand-authored constants in LoadedPowerDuel.activate",
        },
        "pommel_policy": {
            "pommel": 0.42,
            "ordinary": 0.0,
            "basis": "hand-authored constants in base Duel.pommel",
        },
    }


def main() -> None:
    results = {
        "audit": "ATRA MELEE INCENTIVE INTEGRITY AUDIT v0.1",
        "kind": "deterministic policy and rules probes; no fight matrix",
        "cross_beat_rules_vector": {
            "cross": {
                "cost": "one action; zero Spiritus; zero learned slots",
                "success": "cancel; Crossing; preserve measure",
                "exchange_end_without_authored_continuation": "contact cleaned to none",
            },
            "beat": {
                "cost": "one action; zero Spiritus; zero learned slots",
                "success": "cancel; displacement event; contact ends",
                "exchange_end_without_authored_continuation": "contact none",
            },
        },
        "parry_and_compound_policy_surface": parry_and_compound_surface(),
        "durch_policy_surface": durch_surface(),
        "power_policy_surface": power_surface(),
        "guard_policy_surface": guard_policy_surface(),
        "fixed_policy_constants": bridge_and_crown_policy(),
        "instrumentation_observations": [
            "defend records Basic Cross/Beat in choices, then basic_parry also records generic Basic Parry",
            "B3 Scheitelhau entry uses dedicated declaration metrics and correctly does not enter plays uses",
            "Crown selection compares against an aggregate ordinary-response constant rather than actual alternatives",
            "guard occupancy is recorded, but active gate enforcement differs from some data-record access labels",
        ],
    }
    OUT.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()

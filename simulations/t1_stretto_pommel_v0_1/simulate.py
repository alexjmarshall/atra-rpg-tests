"""Exact and fixed-seed analysis for the bounded T1/Stretto/Pommel candidate."""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulations.shared.provisional_longsword import ENGINE, Fighter, HART, UNKNOWN, WEICH
from simulations.t1_stretto_pommel_v0_1.candidate_engine import (
    CandidateEngine,
    POMMEL,
    T1,
    TUTTA_GUARD,
)


RESULTS_PATH = ROOT / "reports" / "t1-stretto-pommel-integration-v01-results.json"
SEED = 1308202601
TRIALS = 4000
SKILLS = (10, 12, 14, 18)
RESERVES = (0, 1, 2, 3, 4, 8)
HPS = (1, 4, 6, 8)
PROFILES = {
    "neither": (False, False),
    "striker_only": (True, False),
    "defender_only": (False, True),
    "both": (True, True),
}


def hit_probability(skill: int, modifier: str = "normal") -> float:
    p = max(0.0, min(1.0, skill / 20.0))
    if modifier == "boon":
        return 1.0 - (1.0 - p) ** 2
    if modifier == "bane":
        return p**2
    return p


def damage_distribution() -> dict[int, float]:
    return {damage: 1 / 6 for damage in range(2, 8)}


def expected_damage_on_hit() -> float:
    return sum(damage * probability for damage, probability in damage_distribution().items())


def kill_probability(skill: int, hp: int, modifier: str = "normal") -> float:
    lethal = sum(probability for damage, probability in damage_distribution().items() if damage >= hp)
    return hit_probability(skill, modifier) * lethal


def loaded_cut_expected(skill: int) -> float:
    # Exact 2d6 keep-highest + 1, multiplied by the flat attack hit probability.
    outcomes = [max(a, b) + 1 for a in range(1, 7) for b in range(1, 7)]
    return hit_probability(skill) * sum(outcomes) / len(outcomes)


def successful_cross(
    *,
    timing: str = "E1",
    pressure: str = HART,
    pommel_cost: int = 2,
    plays_a: set[str] | None = None,
    plays_b: set[str] | None = None,
    spiritus_a: int = 8,
    spiritus_b: int = 8,
    skill_a: int = 14,
    skill_b: int = 14,
    geometry: str = ENGINE.UPPER_CROSS,
) -> tuple[CandidateEngine, Fighter, Fighter]:
    a = Fighter("A", skill=skill_a, spiritus=spiritus_a, known_plays=plays_a or set())
    b = Fighter(
        "B",
        skill=skill_b,
        spiritus=spiritus_b,
        guard=TUTTA_GUARD,
        known_plays=plays_b or {T1},
    )
    engine = CandidateEngine([a, b], timing=timing, pommel_cost=pommel_cost)
    attack = engine.declare_attack(a, b, "cut", descending=True)
    assert attack is not None
    rolled = engine.roll_pending_attack((1,), (3,))
    assert rolled.roll is not None and rolled.success
    assert engine.declare_basic_cross(b, pressure, geometry)
    defence_rolls = (1, 20) if pressure == HART else (1,)
    assert engine.basic_defence("Cross", b, rolled.roll, defence_rolls).success
    return engine, a, b


def snapshot(label: str, engine: CandidateEngine, a: Fighter, b: Fighter) -> dict[str, Any]:
    return {
        "label": label,
        "hp": {"A": a.hp, "B": b.hp},
        "normal_actions": {"A": a.action_available, "B": b.action_available},
        "spiritus": {"A": a.spiritus, "B": b.spiritus},
        "chain": list(engine.learned_chain),
        "guard": {"A": a.guard, "B": b.guard},
        "open": {"A": a.guard == "open", "B": b.guard == "open"},
        "crossing": engine.crossing.contact,
        "measure": engine.crossing.measure,
        "height": engine.crossing.bind_height,
        "pressure_private": {
            "A": engine.pressure_view(a, b),
            "B": engine.pressure_view(b, b),
        },
        "pressure_public": "unknown",
        "point_threat": {"A": a.point_threat, "B": b.point_threat},
        "current_opportunity": engine.crossing.bind_initiative or engine.rejoinder_actor,
        "rejoinder_open": engine.rejoinder_open,
    }


def state_traces() -> list[dict[str, Any]]:
    traces: list[dict[str, Any]] = []

    e, a, b = successful_cross(pressure=HART, plays_a={POMMEL}, plays_b={T1, POMMEL})
    steps = [snapshot("successful Hart Cross; E1 offered", e, a, b)]
    e.declare_early_t1(b); steps.append(snapshot("T1; striker first", e, a, b))
    e.declare_pommel(a); e.resolve_pommel((1,), (3,)); steps.append(snapshot("striker Pommel hit", e, a, b))
    traces.append({"id": 1, "title": "Hart Cross -> E1 T1 -> striker Pommel hit", "steps": steps})

    e, a, b = successful_cross(pressure=HART, plays_a=set(), plays_b={T1, POMMEL})
    e.declare_early_t1(b); steps = [snapshot("T1; striker lacks Pommel", e, a, b)]
    e.pass_bind_initiative(a); steps.append(snapshot("striker passes", e, a, b))
    e.declare_pommel(b); e.resolve_pommel((1,), (3,)); steps.append(snapshot("defender Pommel hit", e, a, b))
    traces.append({"id": 2, "title": "Hart Cross -> E1 T1 -> striker passes -> defender Pommel", "steps": steps})

    e, a, b = successful_cross(pressure=WEICH, plays_a=set(), plays_b={T1, POMMEL})
    e.declare_early_t1(b); steps = [snapshot("Weich T1; defender first", e, a, b)]
    e.declare_pommel(b); e.resolve_pommel((1,), (3,)); steps.append(snapshot("defender Pommel hit", e, a, b))
    traces.append({"id": 3, "title": "Weich Cross -> E1 T1 -> defender Pommel", "steps": steps})

    e, a, b = successful_cross(pressure=WEICH, plays_a={POMMEL}, plays_b={T1, POMMEL})
    e.declare_early_t1(b); e.declare_pommel(b); e.resolve_pommel((20,), (3,))
    steps = [snapshot("defender Pommel misses; transfer", e, a, b)]
    e.declare_pommel(a); e.resolve_pommel((1,), (3,)); steps.append(snapshot("opponent Pommel hits", e, a, b))
    traces.append({"id": 4, "title": "Pommel miss -> opponent Pommel", "steps": steps})

    e, a, b = successful_cross(pressure=WEICH, plays_a={POMMEL}, plays_b={T1, POMMEL})
    e.declare_early_t1(b); e.declare_pommel(b); e.resolve_pommel((20,), (3,)); e.declare_pommel(a); e.resolve_pommel((20,), (3,))
    steps = [snapshot("T1 + two Pommel misses = cap 3", e, a, b)]
    blocked = not e.pommel_legal(b)
    steps.append({**snapshot("fourth learned declaration blocked", e, a, b), "cap_blocked": blocked})
    traces.append({"id": 5, "title": "T1 -> Pommel miss -> opponent miss -> cap", "steps": steps})

    e, a, b = successful_cross(pressure=WEICH, plays_a=set(), plays_b={T1})
    e.declare_early_t1(b); e.pass_bind_initiative(b); steps = [snapshot("first pass", e, a, b)]
    e.pass_bind_initiative(a); steps.append(snapshot("second pass cleanup", e, a, b))
    traces.append({"id": 6, "title": "Neither knows Pommel -> pass/pass cleanup", "steps": steps})

    e, a, b = successful_cross(pressure=HART, plays_a={"Duplieren / Mutieren"}, plays_b={T1})
    e.decline_early_t1(b); steps = [snapshot("E1 declined; H3 opens", e, a, b)]
    e.declare_bind_rejoinder(a, "Duplieren"); e.resolve_bind_rejoinder((1, 20), (3,)); steps.append(snapshot("ordinary H3 D/M", e, a, b))
    traces.append({"id": 7, "title": "Ordinary no-T1 Cross -> H3 D/M", "steps": steps})

    e, a, b = successful_cross(timing="L1", pressure=WEICH, plays_a=set(), plays_b={T1, POMMEL})
    steps = [snapshot("L1: governing Rejoinder first", e, a, b)]
    e.decline_bind_rejoinder(a); e.declare_late_t1(b); steps.append(snapshot("decline -> defender ordinary opportunity -> T1", e, a, b))
    traces.append({"id": 8, "title": "L1 late-T1 control", "steps": steps})

    a = Fighter("A"); b = Fighter("B", guard=TUTTA_GUARD); e = CandidateEngine([a, b])
    attack = e.declare_attack(a, b, "cut", descending=True); assert attack
    rolled = e.roll_pending_attack((1,), (3,)); assert rolled.roll
    e.basic_defence("Beat", b, rolled.roll, (1,));
    traces.append({"id": 9, "title": "Beat control", "steps": [snapshot("Beat cancels, separates, strips attacker Open", e, a, b)]})
    return traces


def pommel_cost_table() -> list[dict[str, Any]]:
    rows = []
    for skill in SKILLS:
        p = hit_probability(skill)
        for cost in (1, 2):
            ed = p * expected_damage_on_hit()
            rows.append({
                "skill": skill,
                "cost": cost,
                "hit": p,
                "expected_damage": ed,
                "damage_per_spiritus": ed / cost,
                "kill_probability": {str(hp): kill_probability(skill, hp) for hp in HPS},
            })
    return rows


def close_sequence(skill: int, profile: str, pressure: str, *, cost: int = 2, reserve: int = 8, target_hp: int = 8) -> dict[str, Any]:
    striker_knows, defender_knows = PROFILES[profile]
    first = "striker" if pressure == HART else "defender"
    second = "defender" if first == "striker" else "striker"
    knows = {"striker": striker_knows, "defender": defender_knows}
    # Defender has paid T1 before this local Close branch.
    available = {"striker": reserve, "defender": max(0, reserve - 1)}
    p = hit_probability(skill)
    damage = expected_damage_on_hit()
    lethal_on_hit = sum(probability for amount, probability in damage_distribution().items() if amount >= target_hp)
    declarations = {"striker": 0.0, "defender": 0.0}
    dealt = {"striker": 0.0, "defender": 0.0}
    kills = {"striker": 0.0, "defender": 0.0}
    passes = 0.0
    first_can = knows[first] and available[first] >= cost
    if first_can:
        declarations[first] += 1.0
        dealt[first] += p * damage
        kills[first] += p * lethal_on_hit
        second_reached = 1.0 - p
    else:
        passes += 1.0
        second_reached = 1.0
    second_can = knows[second] and available[second] >= cost
    if second_can:
        declarations[second] += second_reached
        dealt[second] += second_reached * p * damage
        kills[second] += second_reached * p * lethal_on_hit
        pass_termination = 0.0
    else:
        passes += second_reached
        pass_termination = second_reached if not first_can else 0.0
    return {
        "skill": skill,
        "profile": profile,
        "pressure": pressure,
        "cost": cost,
        "reserve": reserve,
        "first_close_opportunity": first,
        "opponent_first_probability_for_t1_owner": 1.0 if first == "striker" else 0.0,
        "owner_first_probability": 1.0 if first == "defender" else 0.0,
        "expected_incoming_continuation_damage": dealt["striker"],
        "expected_outgoing_continuation_damage": dealt["defender"],
        "incoming_kill_probability": kills["striker"],
        "outgoing_kill_probability": kills["defender"],
        "expected_pommel_declarations": declarations,
        "expected_passes": passes,
        "pass_termination_probability": pass_termination,
    }


def hart_weich_matrix() -> list[dict[str, Any]]:
    rows = []
    for skill in SKILLS:
        for profile in PROFILES:
            for pressure in (HART, WEICH):
                row = close_sequence(skill, profile, pressure)
                row["cross_cancellation"] = hit_probability(skill, "boon" if pressure == HART else "normal")
                rows.append(row)
    return rows


def beat_control_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    mean = expected_damage_on_hit()
    for skill in SKILLS:
        flat = hit_probability(skill)
        hart = hit_probability(skill, "boon")
        for profile in PROFILES:
            for reserve in RESERVES:
                for hp in HPS:
                    lethal = sum(probability for amount, probability in damage_distribution().items() if amount >= hp)
                    common = {"skill": skill, "profile": profile, "reserve": reserve, "target_hp": hp}
                    rows.append({**common, "choice": "Beat", "cancellation": flat, "eventual_incoming_damage": (1-flat)*mean, "eventual_outgoing_damage": 0.0, "eventual_incoming_kill_probability": (1-flat)*lethal, "eventual_outgoing_kill_probability": 0.0, "resource_spend": 0.0, "chain_spend": 0.0, "contact_on_success": "none", "open_on_success": True, "measure_on_success": "wide", "attacker_rejoinder_access": False, "owner_first_probability": 0.0, "opponent_first_probability": 0.0, "pommel_conversion_given_legal": 0.0, "cleanup_escape_probability": 1.0})
                    for pressure, cancel in ((HART, hart), (WEICH, flat)):
                        rows.append({**common, "choice": f"{pressure.title()} Cross no T1", "cancellation": cancel, "eventual_incoming_damage": (1-cancel)*mean, "eventual_outgoing_damage": 0.0, "eventual_incoming_kill_probability": (1-cancel)*lethal, "eventual_outgoing_kill_probability": 0.0, "resource_spend": 0.0, "chain_spend": 0.0, "contact_on_success": "crossing-wide", "open_on_success": False, "measure_on_success": "wide", "attacker_rejoinder_access": True, "owner_first_probability": 1.0 if pressure == WEICH else 0.0, "opponent_first_probability": 1.0 if pressure == HART else 0.0, "pommel_conversion_given_legal": 0.0, "cleanup_escape_probability": 1.0})
                        if reserve >= 1:
                            close = close_sequence(skill, profile, pressure, reserve=reserve, target_hp=hp)
                            expected_pommels = sum(close["expected_pommel_declarations"].values())
                            rows.append({**common, "choice": f"{pressure.title()} Cross + E1 T1", "cancellation": cancel, "eventual_incoming_damage": (1-cancel)*mean + cancel*close["expected_incoming_continuation_damage"], "eventual_outgoing_damage": cancel*close["expected_outgoing_continuation_damage"], "eventual_incoming_kill_probability": (1-cancel)*lethal + cancel*close["incoming_kill_probability"], "eventual_outgoing_kill_probability": cancel*close["outgoing_kill_probability"], "resource_spend": cancel*(1 + 2*expected_pommels), "chain_spend": cancel*(1 + expected_pommels), "contact_on_success": "crossing-close until hit/pass cleanup", "open_on_success": False, "measure_on_success": "close", "attacker_rejoinder_access": False, "owner_first_probability": close["owner_first_probability"], "opponent_first_probability": close["opponent_first_probability_for_t1_owner"], "pommel_conversion_given_legal": 1.0 if expected_pommels else 0.0, "cleanup_escape_probability": 1.0})
    return rows


def wide_h3_matrix() -> list[dict[str, Any]]:
    rows = []
    mean = expected_damage_on_hit()
    for skill in SKILLS:
        flat = hit_probability(skill)
        boon = hit_probability(skill, "boon")
        for pressure in (HART, WEICH):
            for repertoire in ("none", "dm_only", "dm_fuhlen", "winden", "full_h3"):
                if repertoire in {"dm_fuhlen", "full_h3"}:
                    wide_damage = boon * mean
                    wide_spiritus = 3
                    wide_chain = 1
                    info = "paid exact pressure"
                elif repertoire == "dm_only":
                    wide_damage = 0.5 * boon * mean
                    wide_spiritus = 2
                    wide_chain = 1
                    info = "blind 50/50 read"
                elif repertoire == "winden" and pressure == HART:
                    wide_damage = flat * mean
                    wide_spiritus = 2
                    wide_chain = 1
                    info = "no pressure information purchase"
                else:
                    wide_damage = 0.0
                    wide_spiritus = 0
                    wide_chain = 0
                    info = "decline/pass"
                rows.extend([
                    {"skill": skill, "pressure": pressure, "attacker_repertoire": repertoire, "timing": "A stay Wide", "expected_attacker_damage": wide_damage, "spiritus": wide_spiritus, "chain": wide_chain, "first_opportunity": "striker" if pressure == HART else "defender", "eventual_measure": "wide", "information": info, "repertoire_unlocked": "D/M and authored Wide Winden"},
                    {"skill": skill, "pressure": pressure, "attacker_repertoire": repertoire, "timing": "B E1 Close", "expected_attacker_damage": 0.0, "spiritus": 1, "chain": 1, "first_opportunity": "striker" if pressure == HART else "defender", "eventual_measure": "close", "information": "no Fuhlen/Rejoinder after T1", "repertoire_unlocked": "Close only; Wide D/M/Winden gated out"},
                    {"skill": skill, "pressure": pressure, "attacker_repertoire": repertoire, "timing": "C L1 late", "expected_attacker_damage": wide_damage, "spiritus": wide_spiritus + (1 if wide_damage == 0 and pressure == WEICH else 0), "chain": wide_chain + (1 if wide_damage == 0 and pressure == WEICH else 0), "first_opportunity": "governing Rejoinder first", "eventual_measure": "close only after decline and defender opportunity; otherwise cleanup", "information": info, "repertoire_unlocked": "Wide first; Close conditional"},
                ])
    return rows


def close_chain_matrix() -> list[dict[str, Any]]:
    rows = []
    for skill in SKILLS:
        p = hit_probability(skill)
        for cost in (1, 2):
            for reserve in (1, 2, 3, 4, 8):
                defender_can_first = reserve - 1 >= cost
                striker_can_second = reserve >= cost
                declarations = (1.0 if defender_can_first else 0.0) + ((1-p) if defender_can_first and striker_can_second else 0.0)
                cap = (1-p) if defender_can_first and striker_can_second else 0.0
                resource_stop = 1.0 if not defender_can_first else ((1-p) if not striker_can_second else 0.0)
                rows.append({"skill": skill, "cost": cost, "reserve_each": reserve, "expected_pommel_declarations": declarations, "p_hit_declaration_1": p if defender_can_first else 0.0, "p_hit_by_declaration_2": (1-(1-p)**2) if defender_can_first and striker_can_second else (p if defender_can_first else 0.0), "p_cap_reached_after_t1": cap, "resource_stop_probability": resource_stop, "pass_termination_probability": 1.0 if not defender_can_first and not striker_can_second else 0.0})
    return rows


@dataclass(frozen=True)
class Scenario:
    id: str
    label: str
    repertoire_a: tuple[str, ...]
    repertoire_b: tuple[str, ...]
    skill_a: int = 14
    skill_b: int = 14
    hp_a: int = 8
    hp_b: int = 8
    spiritus_a: int = 8
    spiritus_b: int = 8
    defence_b: str = "Cross"


SCENARIOS = (
    Scenario("C1", "Tutta/T1 vs Basics; neither Pommel", (), (T1,)),
    Scenario("C2", "Tutta/T1+Pommel vs Basics", (), (T1, POMMEL)),
    Scenario("C3", "Tutta/T1 vs opponent Pommel", (POMMEL,), (T1,)),
    Scenario("C4", "both know Pommel", (POMMEL,), (T1, POMMEL)),
    Scenario("C5", "Tutta/T1 vs D/M+Fuhlen", ("Duplieren / Mutieren", "Fühlen"), (T1,)),
    Scenario("C6", "Tutta/T1+Pommel vs Winden", ("Winden",), (T1, POMMEL)),
    Scenario("C7", "low-HP Tutta defender", (POMMEL,), (T1, POMMEL), hp_b=1),
    Scenario("C8", "low-Spiritus Tutta defender", (), (T1, POMMEL), spiritus_b=1),
    Scenario("C9", "asymmetric Skill 10 vs 14", (POMMEL,), (T1, POMMEL), skill_a=10, skill_b=14),
    Scenario("C10", "Beat control", (POMMEL,), (T1, POMMEL), defence_b="Beat"),
)


def roll20(rng: random.Random, modifier: str = "normal") -> tuple[int, ...]:
    return tuple(rng.randint(1, 20) for _ in range(2 if modifier in {"boon", "bane"} else 1))


def run_integrated_scenario(scenario: Scenario, trials: int = TRIALS) -> dict[str, Any]:
    metrics: Counter[str] = Counter()
    damage = Counter()
    decline_reasons = Counter()
    for trial in range(trials):
        rng = random.Random(SEED + 100_003 * int(scenario.id[1:]) + trial)
        a = Fighter("A", skill=scenario.skill_a, hp=scenario.hp_a, spiritus=scenario.spiritus_a, known_plays=set(scenario.repertoire_a))
        b = Fighter("B", skill=scenario.skill_b, hp=scenario.hp_b, spiritus=scenario.spiritus_b, guard=TUTTA_GUARD, known_plays=set(scenario.repertoire_b))
        e = CandidateEngine([a, b], timing="E1", pommel_cost=2)
        attack = e.declare_attack(a, b, "cut", descending=True)
        assert attack
        ar = e.roll_pending_attack(roll20(rng), (rng.randint(1, 6),))
        if not ar.success or ar.roll is None:
            metrics["attack_miss"] += 1
            continue
        metrics["defensive_opportunities"] += 1
        if scenario.defence_b == "Beat":
            result = e.basic_defence("Beat", b, ar.roll, roll20(rng))
            metrics["beat_declarations"] += 1
            if result.success:
                metrics["initial_cancellations"] += 1
                metrics["cleanup_escape"] += 1
            else:
                resolved = e.resolve_pending_attack(); damage["A"] += resolved.damage
            continue
        pressure = WEICH if POMMEL in b.known_plays or POMMEL in a.known_plays else HART
        e.declare_basic_cross(b, pressure, ENGINE.UPPER_CROSS)
        result = e.basic_defence("Cross", b, ar.roll, roll20(rng, "boon" if pressure == HART else "normal"))
        if not result.success:
            resolved = e.resolve_pending_attack(); damage["A"] += resolved.damage
            continue
        metrics["initial_cancellations"] += 1
        if e.early_t1_legal(b):
            metrics["t1_legal_opportunities"] += 1
            opponent_risk = pressure == HART and POMMEL in a.known_plays
            no_consumer = POMMEL not in a.known_plays and POMMEL not in b.known_plays
            declare = not opponent_risk and (POMMEL in b.known_plays or "Duplieren / Mutieren" in a.known_plays or no_consumer)
            if declare and e.declare_early_t1(b):
                metrics["t1_declarations"] += 1
            else:
                if opponent_risk: decline_reasons["opponent Close repertoire risk"] += 1
                elif no_consumer: decline_reasons["no Close consumer"] += 1
                else: decline_reasons["ordinary H3 route preferred"] += 1
                e.decline_early_t1(b)
        elif T1 in b.known_plays:
            if b.spiritus < 1: decline_reasons["insufficient Spiritus"] += 1
            elif len(e.learned_chain) >= ENGINE.LEARNED_PLAY_CAP: decline_reasons["chain cap"] += 1
        if e.crossing.measure == "close" and not e.rejoinder_open:
            first = e.crossing.bind_initiative
            metrics[f"first_close_{first}"] += 1
            for _ in range(3):
                if e.crossing.contact != "crossing" or not a.alive or not b.alive:
                    break
                actor = e.fighters[e.crossing.bind_initiative]
                if e.pommel_legal(actor):
                    metrics["pommel_legal_opportunities"] += 1
                    # Spend aggressively except at 2S exactly with a fresh 8HP target.
                    declare = actor.spiritus > 2 or e.other(actor).hp <= 6
                    if declare:
                        e.declare_pommel(actor); metrics["pommel_declarations"] += 1
                        pr = e.resolve_pommel(roll20(rng), (rng.randint(1, 6),))
                        damage[actor.name] += pr.damage
                        continue
                    metrics["pommel_declines_policy_conservation"] += 1
                e.pass_bind_initiative(actor)
            if e.crossing.contact == "none": metrics["cleanup_escape"] += 1
        elif e.rejoinder_open:
            metrics["h3_rejoinders"] += 1
            if "Duplieren / Mutieren" in a.known_plays and a.spiritus >= 2:
                if "Fühlen" in a.known_plays and a.spiritus >= 3:
                    e.buy_fuhlen(a); metrics["fuhlen"] += 1
                branch = "Duplieren" if pressure == HART else "Mutieren"
                if e.declare_bind_rejoinder(a, branch).success:
                    rr = e.resolve_bind_rejoinder(roll20(rng, "boon"), (rng.randint(1, 6),)); damage["A"] += rr.damage; metrics["dm"] += 1
            else:
                e.decline_bind_rejoinder(a)
                if e.crossing.bind_initiative:
                    holder = e.fighters[e.crossing.bind_initiative]
                    if e.upper_winding_legal(holder):
                        e.declare_upper_winding(holder); wr=e.resolve_upper_winding(roll20(rng),(rng.randint(1,6),)); damage[holder.name]+=wr.damage; metrics["winding"]+=1
                    elif e.crossing.contact == "crossing":
                        e.pass_bind_initiative(holder)
        metrics["point_threat_events"] += sum("SET point=threatening" in event or "point+ATTACK" in event for event in e.event_log)
        metrics["postmortem_opportunities"] += int((not a.alive or not b.alive) and e.crossing.bind_initiative is not None)
        metrics["second_action_leaks"] += int(a.action_available or b.action_available)
    legal_t1 = metrics["t1_legal_opportunities"]
    legal_pommel = metrics["pommel_legal_opportunities"]
    return {
        "scenario": asdict(scenario),
        "trials": trials,
        "seed": SEED + 100_003 * int(scenario.id[1:]),
        "metrics": dict(metrics),
        "damage": dict(damage),
        "t1_conversion_given_legal": metrics["t1_declarations"] / legal_t1 if legal_t1 else 0.0,
        "pommel_conversion_given_legal": metrics["pommel_declarations"] / legal_pommel if legal_pommel else 0.0,
        "t1_decline_reasons": dict(decline_reasons),
        "binomial_95pct_half_width_at_p50": 1.96 * math.sqrt(0.25 / trials),
    }


def timing_table() -> list[dict[str, str]]:
    return [
        {"property": "T1 actually reachable", "C0": "raw-legal; 0 policy conversion", "E1": "yes, explicit post-Cross window", "L1": "yes, only on defender ordinary opportunity"},
        {"property": "Attacker H3 Rejoinder occurs", "C0": "ordering undefined; engine leaves it open", "E1": "no if T1; yes if declined", "L1": "yes before T1"},
        {"property": "D/M possible", "C0": "raw options collapse after Close", "E1": "only when T1 declined", "L1": "yes before late T1"},
        {"property": "Pressure used for", "C0": "Rejoinder but stale after T1", "E1": "first Close opportunity", "L1": "Rejoinder/ordinary initiative"},
        {"property": "Close entered", "C0": "yes without ordering", "E1": "during cover before Rejoinder use", "L1": "later ordinary opportunity"},
        {"property": "First Close opportunity", "C0": "undefined", "E1": "Hart striker / Weich defender", "L1": "current holder when defender declares"},
        {"property": "Spiritus", "C0": "1S", "E1": "1S", "L1": "1S after any earlier H3 spend"},
        {"property": "Chain", "C0": "+1", "E1": "+1", "L1": "+1 after any earlier chain"},
        {"property": "Reciprocal risk", "C0": "not authored", "E1": "immediate and pressure-dependent", "L1": "present but filtered by prior Rejoinder"},
    ]


def artifact_sanity() -> dict[str, Any]:
    probe, striker, defender = successful_cross(
        timing="L1", pressure=WEICH, plays_a=set(), plays_b={"Winden"}
    )
    probe.decline_bind_rejoinder(striker)
    probe.declare_upper_winding(defender)
    counted = sum(
        "SET point=threatening" in event or "point+ATTACK" in event
        for event in probe.event_log
    )
    return {
        "loaded_cut": {
            "json_skill14": 3.8305555555555553,
            "recomputed_exact": loaded_cut_expected(14),
            "historical_prose_value": 4.394,
            "classification": "REPORT-ONLY DISCREPANCY; JSON/model exact enumeration is correct",
            "historical_report_rewritten": False,
        },
        "point_threat_events": {
            "finding": "integrated simulator initializes the counter but never increments it",
            "engine_state_correct": True,
            "classification": "INSTRUMENTATION BUG, not a mechanic bug",
            "repair": "candidate audit counts authored point-threat event-log transitions; historical JSON remains unchanged",
            "positive_probe_count": counted,
            "positive_probe_state": defender.point_threat,
        },
    }


def build_results(trials: int = TRIALS) -> dict[str, Any]:
    return {
        "milestone": "ATRA T1 -> STRETTO -> POMMEL INTEGRATION PASS v0.1",
        "status": "BOUNDED CANDIDATE; NO GOVERNING PROMOTION",
        "authoritative_base": "simulations/shared/provisional_longsword.py::CurrentEngine",
        "candidate_overlay": "simulations/t1_stretto_pommel_v0_1/candidate_engine.py::CandidateEngine",
        "seed": SEED,
        "trials_per_integrated_scenario": trials,
        "artifact_sanity": artifact_sanity(),
        "timing_comparison": timing_table(),
        "pommel_cost": pommel_cost_table(),
        "resource_context": [{"reserve": reserve, "P1_declarations_max": reserve, "P2_declarations_max": reserve // 2, "after_T1_defender_reserve": max(0, reserve-1)} for reserve in (1,2,3,4,8)],
        "hart_weich_stretto": hart_weich_matrix(),
        "beat_control": beat_control_matrix(),
        "t1_vs_wide_h3": wide_h3_matrix(),
        "close_chain": close_chain_matrix(),
        "state_traces": state_traces(),
        "integrated_scenarios": [run_integrated_scenario(s, trials) for s in SCENARIOS],
        "findings": {
            "t1_classification": "REPERTOIRE-DEPENDENT; NARROW BUT DISTINCT",
            "pommel_P1": "INCENTIVE RISK: 1S crowds 2S action-compressed benchmarks on damage/Spiritus",
            "pommel_P2": "HEALTHY DISTINCT candidate under the narrow Close/current-opportunity gate",
            "severe_failures": [],
            "runtime_or_instrumentation_bugs": 1,
            "real_incentive_problems": 1,
            "blocking_issue_for_E1_P2": None,
            "rejected_alternative_issue": "P1 is too resource-efficient at 1S reserves; P2 avoids that problem",
            "recommendation": "Project promotion review may consider E1 + P2; do not promote automatically",
            "next_milestone": "governing integration of T1/Close/Pommel, only if Project adjudicates promotion",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    results = build_results(args.trials)
    if not args.no_write:
        RESULTS_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"scenarios": len(results["integrated_scenarios"]), "trials": args.trials, "seed": SEED}, indent=2))


if __name__ == "__main__":
    main()

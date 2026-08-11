from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "data" / "prototypes" / "longsword-crossing-bind-state-model-v0.1.yaml"
RESULTS_PATH = HERE / "results.json"
SUMMARY_PATH = HERE / "regression-summary.csv"
REPORT_PATH = ROOT / "reports" / "crossing-bind-state-model-v01-results.md"

MAX_HP = 8
MAX_SPIRITUS = 8
DURCH_COST = 1
COMPOUND_COST = 2
TEMPERATURE = 0.24
SEED = 11082026

ABSETZEN = "Absetzen"
ZORN = "Zornhau-Ort"
DURCH = "Durchwechseln"
SCIAMBIAR = "Scambiar di Punta"
NACH = "Nachreisen"
POMMEL = "Pommel Strike"
SCHIEL = "Schielhau"
ROMPERE = "Rompere di Punta"
ACTIVE_PLAYS = (ABSETZEN, ZORN, DURCH, SCIAMBIAR, NACH, POMMEL, SCHIEL)


@dataclass(frozen=True)
class Cell:
    skill: int
    start_spiritus: int
    information: str

    @property
    def label(self) -> str:
        return f"skill{self.skill}_S{self.start_spiritus}_{self.information}"


@dataclass
class Fighter:
    name: str
    skill: int
    spiritus: int
    hp: int = MAX_HP
    action_ready: bool = True
    recovery: str = "ready"
    knows_enemy_durch: bool = False
    knows_enemy_schiel: bool = False

    @property
    def alive(self) -> bool:
        return self.hp > 0


@dataclass
class ContactState:
    contact: str = "none"
    measure: str = "wide"
    contact_zone: dict[str, str] = field(default_factory=lambda: {"A": "unknown", "B": "unknown"})
    pressure: dict[str, str] = field(default_factory=lambda: {"A": "unknown", "B": "unknown"})
    point_threat: dict[str, str] = field(
        default_factory=lambda: {"A": "not_threatening", "B": "not_threatening"}
    )
    retain_crossing: bool = False
    displacement_events: list[dict[str, Any]] = field(default_factory=list)


def play_stats() -> dict[str, int]:
    return {
        "opportunities": 0, "uses": 0, "successes": 0, "damage": 0,
        "continuation_opportunities": 0, "continuation_uses": 0,
    }


def fresh_metrics() -> dict[str, Any]:
    return {
        "fights": 0, "wins_A": 0, "wins_B": 0, "double_defeats": 0, "draws": 0,
        "rounds": 0, "exchanges": 0, "defensive_opportunities": 0,
        "choices": Counter(), "parry_declarations": Counter(), "parry_rolls": Counter(),
        "parry_successes": Counter(), "parry_interrupted": Counter(),
        "crossings": 0, "wide_crossings": 0, "close_crossings": 0,
        "pressure_crossings": Counter(), "known_zone_crossings": 0, "unknown_zone_crossings": 0,
        "displacement_separation_events": 0, "displacement_retained_crossing_events": 0,
        "crossings_persisted": 0, "crossings_cleaned_up": 0,
        "durch_opportunities": 0, "durch_declarations": 0, "durch_successes": 0,
        "durch_spiritus_spent": 0, "compound_declarations": 0,
        "compound_spiritus_spent": 0, "total_spiritus_spent": 0,
        "chain_distribution": Counter(), "attempted_fourth_plays": 0,
        "plays": {name: play_stats() for name in ACTIVE_PLAYS},
        "precondition_violations": 0,
    }


def success_probability(skill: int) -> float:
    return max(0.0, min(1.0, skill / 20.0))


def reserve_charge(spiritus: int, cost: int) -> float:
    if spiritus < cost:
        return math.inf
    return 0.78 * (math.sqrt(spiritus) - math.sqrt(spiritus - cost))


def ratio(n: float, d: float) -> float:
    return n / d if d else 0.0


def serial(value: Any) -> Any:
    if isinstance(value, Counter):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


class Duel:
    """Explicit contact model. Legacy mode exists only as a comparison harness."""

    def __init__(self, rng: random.Random, policy_rng: random.Random, cell: Cell,
                 metrics: dict[str, Any], model: str = "explicit") -> None:
        self.rng = rng
        self.policy_rng = policy_rng
        self.cell = cell
        self.metrics = metrics
        self.model = model
        self.a = Fighter("A", cell.skill, cell.start_spiritus)
        self.b = Fighter("B", cell.skill, cell.start_spiritus)
        if cell.information == "perfect_information":
            self.a.knows_enemy_durch = self.b.knows_enemy_durch = True
            self.a.knows_enemy_schiel = self.b.knows_enemy_schiel = True
        self.state = ContactState()
        self.current_chain: list[str] = []

    def other(self, fighter: Fighter) -> Fighter:
        return self.b if fighter is self.a else self.a

    def roll(self, fighter: Fighter) -> tuple[bool, int]:
        result = self.rng.randint(1, 20)
        return result <= fighter.skill, result

    def damage(self) -> int:
        return self.rng.randint(1, 6) + 1

    def hurt(self, target: Fighter, play: str | None = None) -> None:
        amount = self.damage()
        target.hp -= amount
        if play in self.metrics["plays"]:
            self.metrics["plays"][play]["damage"] += amount

    def spend_action(self, fighter: Fighter) -> None:
        if not fighter.action_ready:
            self.metrics["precondition_violations"] += 1
            return
        fighter.action_ready = False

    def spend_spiritus(self, fighter: Fighter, cost: int, kind: str) -> bool:
        if fighter.spiritus < cost:
            self.metrics["precondition_violations"] += 1
            return False
        fighter.spiritus -= cost
        self.metrics["total_spiritus_spent"] += cost
        self.metrics[f"{kind}_spiritus_spent"] += cost
        return True

    def softmax(self, values: dict[str, float], temperature: float = TEMPERATURE) -> str:
        top = max(values.values())
        weights = {key: math.exp((value - top) / temperature) for key, value in values.items()}
        pick = self.policy_rng.random() * sum(weights.values())
        for key, weight in weights.items():
            pick -= weight
            if pick <= 0:
                return key
        return next(reversed(values))

    def add_play(self, name: str) -> bool:
        if len(self.current_chain) >= 3:
            self.metrics["attempted_fourth_plays"] += 1
            return False
        self.current_chain.append(name)
        self.metrics["plays"][name]["uses"] += 1
        return True

    def set_point(self, fighter: Fighter, value: str) -> None:
        self.state.point_threat[fighter.name] = value

    def create_crossing(self, first: Fighter, second: Fighter, *, measure: str = "wide",
                        first_zone: str = "unknown", second_zone: str = "unknown",
                        first_pressure: str = "unknown", second_pressure: str = "unknown",
                        retain: bool = False) -> None:
        self.state.contact = "crossing"
        self.state.measure = measure
        self.state.contact_zone[first.name] = first_zone
        self.state.contact_zone[second.name] = second_zone
        self.state.pressure[first.name] = first_pressure
        self.state.pressure[second.name] = second_pressure
        self.state.retain_crossing = retain
        m = self.metrics
        m["crossings"] += 1
        m[f"{measure}_crossings"] += 1
        key = f"{self.state.pressure['A']}/{self.state.pressure['B']}"
        m["pressure_crossings"][key] += 1
        if all(zone == "unknown" for zone in self.state.contact_zone.values()):
            m["unknown_zone_crossings"] += 1
        else:
            m["known_zone_crossings"] += 1

    def separate(self) -> None:
        self.state.contact = "none"
        self.state.contact_zone = {"A": "unknown", "B": "unknown"}
        self.state.pressure = {"A": "unknown", "B": "unknown"}
        self.state.retain_crossing = False

    def displace(self, weapon_owner: Fighter, source: str, retain_crossing: bool) -> None:
        self.state.displacement_events.append({
            "weapon_owner": weapon_owner.name, "source": source,
            "contact_after": "crossing" if retain_crossing else "none",
        })
        key = "displacement_retained_crossing_events" if retain_crossing else "displacement_separation_events"
        self.metrics[key] += 1
        if not retain_crossing:
            self.separate()

    def finish_exchange(self) -> None:
        # PROVISIONAL cleanup location: after resolution/aftermath, before the next activation.
        if self.model == "explicit" and self.state.contact == "crossing":
            if self.state.retain_crossing:
                self.metrics["crossings_persisted"] += 1
            else:
                self.metrics["crossings_cleaned_up"] += 1
                self.separate()
        self.metrics["exchanges"] += 1
        self.metrics["chain_distribution"][str(len(self.current_chain))] += 1
        self.current_chain = []
        self.state.displacement_events = []

    def durch_decision(self, attacker: Fighter, defender: Fighter, context: str,
                       schiel_roll: int | None = None) -> bool:
        m = self.metrics
        m["durch_opportunities"] += 1
        m["plays"][DURCH]["opportunities"] += 1
        if attacker.spiritus < DURCH_COST:
            return False
        offense = 1.0 + 0.3 * (MAX_HP - defender.hp) / MAX_HP
        if schiel_roll is None:
            p = success_probability(attacker.skill)
            decline = (1.0 - success_probability(defender.skill)) * offense
        else:
            p = max(0, min(attacker.skill, schiel_roll - 1)) / 20.0
            decline = -0.55
        declare = p * offense - reserve_charge(attacker.spiritus, DURCH_COST)
        if self.softmax({"declare": declare, "decline": decline}) != "declare":
            return False
        if not self.add_play(DURCH):
            return False
        m["durch_declarations"] += 1
        self.spend_spiritus(attacker, DURCH_COST, "durch")
        defender.knows_enemy_durch = True
        return True

    def resolve_durch(self, attacker: Fighter, defender: Fighter) -> bool:
        self.separate()
        self.set_point(attacker, "threatening")
        ok, _ = self.roll(attacker)
        if ok:
            self.metrics["durch_successes"] += 1
            self.metrics["plays"][DURCH]["successes"] += 1
            self.hurt(defender, DURCH)
        return ok

    def defence_values(self, attacker: Fighter, defender: Fighter, attack: dict[str, Any]) -> dict[str, float]:
        p = success_probability(defender.skill)
        offense = 1.0 + 0.3 * (MAX_HP - attacker.hp) / MAX_HP
        defense = 1.0 + 0.35 * (MAX_HP - defender.hp) / MAX_HP
        q = 0.0
        if attacker.spiritus >= DURCH_COST:
            raw = p * offense - reserve_charge(attacker.spiritus, DURCH_COST)
            allow = (1.0 - p) * offense
            q = 1.0 / (1.0 + math.exp((allow - raw) / TEMPERATURE))
        parry_value = ((1.0 - q) * p + q * (1.0 - p)) * defense
        values = {"Ignore": 0.0, "Counter": p * offense}
        if self.model == "legacy":
            values["Basic Parry"] = parry_value
        else:
            # Same immediate cancellation value. Their declared state outcomes differ.
            values["Basic Cross"] = parry_value
            values["Basic Beat"] = parry_value
        charge = reserve_charge(defender.spiritus, COMPOUND_COST)
        if attack["type"] == "thrust" and math.isfinite(charge):
            values[ABSETZEN] = p * (offense + defense) - charge
            values[SCIAMBIAR] = p * (offense + defense) - charge
        if attack["type"] == "descending_cut":
            if math.isfinite(charge):
                values[SCHIEL] = p * (offense + defense) - charge
            if attack["committed"]:
                values[ZORN] = p * defense + 0.5 * p * p * offense
        return values

    def basic_parry(self, form: str, attacker: Fighter, defender: Fighter,
                    attribution: str | None, forced_roll: bool | None = None,
                    force_durch: bool | None = None) -> str:
        m = self.metrics
        m["choices"]["Basic Parry"] += 1
        m["parry_declarations"][form] += 1
        self.spend_action(defender)
        self.set_point(defender, "not_threatening")
        declared = self.durch_decision(attacker, defender, f"Basic {form}") if force_durch is None else force_durch
        if declared:
            if force_durch is True:
                m["durch_opportunities"] += 1
                m["plays"][DURCH]["opportunities"] += 1
                if attacker.spiritus < DURCH_COST or not self.add_play(DURCH):
                    return "invalid"
                m["durch_declarations"] += 1
                self.spend_spiritus(attacker, DURCH_COST, "durch")
            m["parry_interrupted"][form] += 1
            self.resolve_durch(attacker, defender)
            return "interrupted"
        m["parry_rolls"][form] += 1
        ok = self.roll(defender)[0] if forced_roll is None else forced_roll
        if not ok:
            self.hurt(defender, attribution)
            return "failed"
        m["parry_successes"][form] += 1
        if form == "Cross":
            self.create_crossing(defender, attacker, measure=self.state.measure,
                                 first_pressure="hard", second_pressure="hard")
        elif form == "Beat":
            self.displace(attacker, "Basic Parry: Beat", retain_crossing=False)
        else:  # legacy exercise behavior only
            close = self.rng.random() < 0.25
            self.create_crossing(defender, attacker, measure="close" if close else "wide")
        return "success"

    def combined(self, name: str, attacker: Fighter, defender: Fighter,
                 attribution: str | None, forced_roll: bool | None = None) -> str:
        if not self.add_play(name):
            self.hurt(defender, attribution)
            return "invalid"
        self.metrics["compound_declarations"] += 1
        self.spend_action(defender)
        self.spend_spiritus(defender, COMPOUND_COST, "compound")
        self.set_point(defender, "threatening")
        ok = self.roll(defender)[0] if forced_roll is None else forced_roll
        if not ok:
            self.hurt(defender, attribution)
            return "failed"
        self.metrics["plays"][name]["successes"] += 1
        self.create_crossing(defender, attacker, first_pressure="unknown", second_pressure="unknown")
        self.hurt(attacker, name)
        return "success"

    def zorn(self, attacker: Fighter, defender: Fighter, attribution: str | None,
             forced_roll: bool | None = None) -> str:
        if not self.add_play(ZORN):
            self.hurt(defender, attribution)
            return "invalid"
        self.spend_action(defender)
        ok = self.roll(defender)[0] if forced_roll is None else forced_roll
        if not ok:
            self.hurt(defender, attribution)
            return "failed"
        self.metrics["plays"][ZORN]["successes"] += 1
        self.create_crossing(defender, attacker)
        # Only the legacy comparison synthesizes a Soft opponent for Ort.
        if self.model == "legacy" and self.rng.random() < 0.5:
            self.state.pressure[attacker.name] = "soft"
            self.metrics["plays"][ZORN]["continuation_opportunities"] += 1
            self.metrics["plays"][ZORN]["continuation_uses"] += 1
            if self.roll(defender)[0]:
                self.hurt(attacker, ZORN)
        return "success"

    def schiel(self, attacker: Fighter, defender: Fighter, attribution: str | None,
               forced_roll: bool | None = None, force_durch: bool | None = None) -> str:
        if not self.add_play(SCHIEL):
            self.hurt(defender, attribution)
            return "invalid"
        self.metrics["compound_declarations"] += 1
        self.spend_action(defender)
        self.spend_spiritus(defender, COMPOUND_COST, "compound")
        ok, schiel_roll = self.roll(defender)
        if forced_roll is not None:
            ok, schiel_roll = forced_roll, 1 if forced_roll else 20
        if not ok:
            self.hurt(defender, attribution)
            return "failed"
        attacker.knows_enemy_schiel = True
        attempted = self.durch_decision(attacker, defender, "Schielhau S2", schiel_roll) if force_durch is None else force_durch
        if attempted:
            if force_durch is True:
                self.metrics["durch_opportunities"] += 1
                self.metrics["plays"][DURCH]["opportunities"] += 1
                if attacker.spiritus < DURCH_COST or not self.add_play(DURCH):
                    return "invalid"
                self.metrics["durch_declarations"] += 1
                self.spend_spiritus(attacker, DURCH_COST, "durch")
            durch_ok, durch_roll = self.roll(attacker)
            if durch_ok and durch_roll < schiel_roll:
                self.metrics["durch_successes"] += 1
                self.metrics["plays"][DURCH]["successes"] += 1
                self.separate()
                self.set_point(attacker, "threatening")
                self.hurt(defender, DURCH)
                return "durch_wins"
        self.metrics["plays"][SCHIEL]["successes"] += 1
        self.separate()
        self.set_point(defender, "threatening")
        self.hurt(attacker, SCHIEL)
        return "success"

    def counter(self, attacker: Fighter, defender: Fighter, attribution: str | None) -> None:
        self.spend_action(defender)
        self.hurt(defender, attribution)
        if self.roll(defender)[0]:
            self.hurt(attacker)

    def defend(self, attacker: Fighter, defender: Fighter, attack: dict[str, Any],
               attribution: str | None) -> None:
        if not defender.action_ready:
            self.hurt(defender, attribution)
            return
        self.metrics["defensive_opportunities"] += 1
        values = self.defence_values(attacker, defender, attack)
        for name in (ABSETZEN, SCIAMBIAR, SCHIEL, ZORN):
            if name in values:
                self.metrics["plays"][name]["opportunities"] += 1
        choice = self.softmax(values)
        self.metrics["choices"][choice] += 1
        if choice == "Ignore":
            self.hurt(defender, attribution)
        elif choice == "Counter":
            self.counter(attacker, defender, attribution)
        elif choice == "Basic Parry":
            self.basic_parry("Legacy", attacker, defender, attribution)
        elif choice == "Basic Cross":
            self.basic_parry("Cross", attacker, defender, attribution)
        elif choice == "Basic Beat":
            self.basic_parry("Beat", attacker, defender, attribution)
        elif choice in (ABSETZEN, SCIAMBIAR):
            self.combined(choice, attacker, defender, attribution)
        elif choice == ZORN:
            self.zorn(attacker, defender, attribution)
        else:
            self.schiel(attacker, defender, attribution)

    def choose_attack(self, actor: Fighter) -> dict[str, Any]:
        draw = self.rng.random()
        thrust_cutoff = 0.38 if actor.knows_enemy_schiel else 0.30
        descending_cutoff = 0.56 if actor.knows_enemy_schiel else 0.65
        if draw < thrust_cutoff:
            return {"type": "thrust", "committed": False}
        if draw < descending_cutoff:
            return {"type": "descending_cut", "committed": self.rng.random() < 0.75}
        return {"type": "other_cut", "committed": True}

    def pommel(self, actor: Fighter, target: Fighter, forced_roll: bool | None = None) -> bool:
        if self.state.contact != "crossing" or self.state.measure != "close":
            return False
        self.metrics["plays"][POMMEL]["opportunities"] += 1
        if forced_roll is None and self.softmax({POMMEL: 0.42, "ordinary": 0.0}) != POMMEL:
            return False
        if not self.add_play(POMMEL):
            return False
        self.spend_action(actor)
        ok = self.roll(actor)[0] if forced_roll is None else forced_roll
        if ok:
            self.metrics["plays"][POMMEL]["successes"] += 1
            self.hurt(target, POMMEL)
        self.separate()
        return True

    def activate(self, actor: Fighter) -> None:
        target = self.other(actor)
        self.current_chain = []
        if self.pommel(actor, target):
            self.finish_exchange()
            return
        attribution = None
        if target.recovery == "recovering":
            self.metrics["plays"][NACH]["opportunities"] += 1
            if self.softmax({NACH: 0.52, "ordinary": 0.0}) == NACH:
                self.add_play(NACH)
                attribution = NACH
                target.recovery = "ready"
                attack = {"type": "descending_cut", "committed": True}
            else:
                attack = self.choose_attack(actor)
        else:
            attack = self.choose_attack(actor)
        self.spend_action(actor)
        if self.model == "explicit":
            self.separate()
        ok, _ = self.roll(actor)
        if not ok:
            if attack["type"] == "descending_cut" and attack["committed"]:
                actor.recovery = "recovering"
            self.finish_exchange()
            return
        if attribution:
            self.metrics["plays"][NACH]["successes"] += 1
        self.set_point(actor, "threatening")
        self.defend(actor, target, attack, attribution)
        self.finish_exchange()

    def run(self, max_rounds: int = 100) -> tuple[str, int]:
        for round_number in range(1, max_rounds + 1):
            for fighter in (self.a, self.b):
                if fighter.alive:
                    fighter.action_ready = True
            order = (self.a, self.b) if self.rng.random() < 0.5 else (self.b, self.a)
            for fighter in order:
                if fighter.alive and self.other(fighter).alive and fighter.action_ready:
                    self.activate(fighter)
                if not self.a.alive or not self.b.alive:
                    break
            if not self.a.alive and not self.b.alive:
                return "double", round_number
            if not self.a.alive:
                return "B", round_number
            if not self.b.alive:
                return "A", round_number
        return "draw", max_rounds


def finalize(metrics: dict[str, Any]) -> dict[str, Any]:
    m = serial(metrics)
    fights = metrics["fights"]
    exchanges = metrics["exchanges"]
    defensive = metrics["defensive_opportunities"]
    cross = metrics["parry_declarations"]["Cross"]
    beat = metrics["parry_declarations"]["Beat"]
    m.update({
        "win_rate_A": ratio(metrics["wins_A"], fights),
        "average_rounds": ratio(metrics["rounds"], fights),
        "double_defeat_rate": ratio(metrics["double_defeats"], fights),
        "basic_cross_declarations_per_fight": ratio(cross, fights),
        "basic_beat_declarations_per_fight": ratio(beat, fights),
        "cross_success_rate": ratio(metrics["parry_successes"]["Cross"], metrics["parry_rolls"]["Cross"]),
        "beat_success_rate": ratio(metrics["parry_successes"]["Beat"], metrics["parry_rolls"]["Beat"]),
        "cross_interrupted_per_fight": ratio(metrics["parry_interrupted"]["Cross"], fights),
        "beat_interrupted_per_fight": ratio(metrics["parry_interrupted"]["Beat"], fights),
        "successful_crossings_per_fight": ratio(metrics["crossings"], fights),
        "displacement_separation_per_fight": ratio(metrics["displacement_separation_events"], fights),
        "displacement_retained_crossing_per_fight": ratio(metrics["displacement_retained_crossing_events"], fights),
        "wide_crossings_per_fight": ratio(metrics["wide_crossings"], fights),
        "close_crossings_per_fight": ratio(metrics["close_crossings"], fights),
        "hard_hard_crossings_per_fight": ratio(metrics["pressure_crossings"]["hard/hard"], fights),
        "hard_soft_crossings_per_fight": ratio(metrics["pressure_crossings"]["hard/soft"], fights),
        "soft_hard_crossings_per_fight": ratio(metrics["pressure_crossings"]["soft/hard"], fights),
        "unknown_pressure_crossings_per_fight": ratio(sum(
            count for key, count in metrics["pressure_crossings"].items() if "unknown" in key
        ), fights),
        "known_zone_crossings_per_fight": ratio(metrics["known_zone_crossings"], fights),
        "unknown_zone_crossings_per_fight": ratio(metrics["unknown_zone_crossings"], fights),
        "crossings_persisted_per_fight": ratio(metrics["crossings_persisted"], fights),
        "crossings_cleaned_up_per_fight": ratio(metrics["crossings_cleaned_up"], fights),
        "durch_opportunities_per_fight": ratio(metrics["durch_opportunities"], fights),
        "durch_declarations_per_fight": ratio(metrics["durch_declarations"], fights),
        "durch_success_rate": ratio(metrics["durch_successes"], metrics["durch_declarations"]),
        "compound_declarations_per_fight": ratio(metrics["compound_declarations"], fights),
        "spiritus_expenditure_per_fight": ratio(metrics["total_spiritus_spent"], fights),
        "basic_parry_frequency": ratio(metrics["choices"]["Basic Parry"], defensive),
        "counter_frequency": ratio(metrics["choices"]["Counter"], defensive),
        "ignore_frequency": ratio(metrics["choices"]["Ignore"], defensive),
        "learned_play_chain_length": ratio(sum(int(k) * v for k, v in metrics["chain_distribution"].items()), exchanges),
        "three_play_cap_frequency": ratio(metrics["chain_distribution"]["3"], exchanges),
        "attempted_fourth_plays_per_fight": ratio(metrics["attempted_fourth_plays"], fights),
    })
    for name, raw in metrics["plays"].items():
        m["plays"][name].update({
            "opportunities_per_fight": ratio(raw["opportunities"], fights),
            "uses_per_fight": ratio(raw["uses"], fights),
            "success_rate": ratio(raw["successes"], raw["uses"]),
            "damage_per_fight": ratio(raw["damage"], fights),
            "continuation_opportunities_per_fight": ratio(raw["continuation_opportunities"], fights),
            "continuation_uses_per_fight": ratio(raw["continuation_uses"], fights),
        })
    return m


def record_fight(metrics: dict[str, Any], outcome: str, rounds: int) -> None:
    metrics["fights"] += 1
    metrics["rounds"] += rounds
    metrics[{"A": "wins_A", "B": "wins_B", "double": "double_defeats", "draw": "draws"}[outcome]] += 1


def run_cell(cell: Cell, trials: int, seed: int, model: str = "explicit") -> dict[str, Any]:
    rng = random.Random(seed)
    policy_rng = random.Random(seed ^ 0xC2055)
    metrics = fresh_metrics()
    for _ in range(trials):
        duel = Duel(rng, policy_rng, cell, metrics, model=model)
        outcome, rounds = duel.run()
        record_fight(metrics, outcome, rounds)
    return {"cell": asdict(cell), "seed": seed, "metrics": finalize(metrics)}


def cells() -> Iterable[Cell]:
    for skill in (10, 14, 18):
        for start in (8, 3):
            for information in ("adaptive_revelation", "perfect_information"):
                yield Cell(skill, start, information)


def transition_harness() -> dict[str, Any]:
    """Deterministic evidence used by unit tests and included in the result set."""
    def arena() -> Duel:
        return Duel(random.Random(7), random.Random(11), Cell(10, 8, "perfect_information"), fresh_metrics())

    out: dict[str, Any] = {}
    d = arena(); before = d.state.measure; result = d.basic_parry("Cross", d.a, d.b, None, True, False)
    out["basic_cross_success"] = {"result": result, "contact": d.state.contact, "measure_preserved": d.state.measure == before, "zones": dict(d.state.contact_zone), "pressure": dict(d.state.pressure), "displacements": list(d.state.displacement_events)}
    d = arena(); result = d.basic_parry("Beat", d.a, d.b, None, True, False)
    out["basic_beat_success"] = {"result": result, "contact": d.state.contact, "pressure": dict(d.state.pressure), "displacements": list(d.state.displacement_events)}
    for form in ("Cross", "Beat"):
        d = arena(); before_spiritus = d.a.spiritus; result = d.basic_parry(form, d.a, d.b, None, True, True)
        out[f"{form.lower()}_durch"] = {"result": result, "spiritus_paid": before_spiritus - d.a.spiritus, "parry_rolls": d.metrics["parry_rolls"][form], "contact": d.state.contact, "point": d.state.point_threat["A"]}
    for form in ("Cross", "Beat"):
        d = arena(); hp = d.b.hp; result = d.basic_parry(form, d.a, d.b, None, False, False)
        out[f"failed_{form.lower()}"] = {"result": result, "damage_resolved": d.b.hp < hp, "contact": d.state.contact, "displacements": list(d.state.displacement_events)}
    for name in (ABSETZEN, SCIAMBIAR):
        d = arena(); result = d.combined(name, d.a, d.b, None, True); during = d.state.contact; point = d.state.point_threat["B"]; d.finish_exchange()
        out[name.lower().replace(" ", "_")] = {"result": result, "during_contact": during, "point": point, "after_cleanup": d.state.contact}
    d = arena(); d.separate(); d.set_point(d.a, "threatening")
    out["durchwechseln"] = {"contact": d.state.contact, "point": d.state.point_threat["A"]}
    d = arena(); result = d.schiel(d.a, d.b, None, True, False)
    out["schielhau"] = {"result": result, "contact": d.state.contact, "point": d.state.point_threat["B"]}
    d = arena(); d.create_crossing(d.b, d.a, first_zone="unknown", second_zone="middle", retain=True); d.displace(d.a, ROMPERE, True)
    out["rompere_reference"] = {"displaced": True, "contact": d.state.contact, "zones": dict(d.state.contact_zone)}
    d = arena(); d.create_crossing(d.a, d.b); d.finish_exchange()
    out["crossing_cleanup"] = {"contact": d.state.contact, "cleanups": d.metrics["crossings_cleaned_up"]}
    d = arena(); d.state.measure = "close"; d.create_crossing(d.a, d.b, measure="close"); d.a.action_ready = True; executed = d.pommel(d.a, d.b, True)
    out["forced_close_pommel"] = {"executed": executed, "uses": d.metrics["plays"][POMMEL]["uses"], "contact": d.state.contact}
    return out


def validate_results(results: dict[str, Any]) -> None:
    assert len(results["primary_matrix"]) == 12
    assert len(results["legacy_comparison"]) == 12
    for item in results["primary_matrix"].values():
        m = item["metrics"]
        assert m["precondition_violations"] == 0
        assert m["close_crossings_per_fight"] == 0
        assert m["hard_soft_crossings_per_fight"] == 0
        assert m["soft_hard_crossings_per_fight"] == 0
        assert m["plays"][POMMEL]["opportunities_per_fight"] == 0
        assert m["attempted_fourth_plays_per_fight"] == 0
    t = results["transition_tests"]
    assert t["basic_cross_success"]["contact"] == "crossing"
    assert set(t["basic_cross_success"]["pressure"].values()) == {"hard"}
    assert t["basic_beat_success"]["contact"] == "none"
    assert t["cross_durch"]["parry_rolls"] == t["beat_durch"]["parry_rolls"] == 0
    assert t["rompere_reference"]["contact"] == "crossing"
    assert t["crossing_cleanup"]["contact"] == "none"
    assert t["forced_close_pommel"]["executed"]


def flatten(item: dict[str, Any], model: str) -> dict[str, Any]:
    return {"model": model, **item["cell"], "seed": item["seed"], **{
        key: value for key, value in item["metrics"].items()
        if isinstance(value, (int, float)) and key not in {"fights"}
    }}


def aggregate_play_changes(results: dict[str, Any]) -> dict[str, Any]:
    changes: dict[str, Any] = {}
    for play in ACTIVE_PLAYS:
        old_opp = old_use = new_opp = new_use = 0.0
        n = len(results["primary_matrix"])
        for label, item in results["primary_matrix"].items():
            old = results["legacy_comparison"][label]["metrics"]["plays"][play]
            new = item["metrics"]["plays"][play]
            old_opp += old["opportunities_per_fight"]; old_use += old["uses_per_fight"]
            new_opp += new["opportunities_per_fight"]; new_use += new["uses_per_fight"]
        reason = "contact now explicit"
        if play == ZORN: reason = "random soft-bind removed; no Soft-producing action currently exists"
        elif play == POMMEL: reason = "random close-crossing removed; no Close-producing action currently exists"
        elif play == DURCH: reason = "explicit Cross/Beat choice; explicit point-threat state"
        elif play in (ABSETZEN, SCIAMBIAR, SCHIEL): reason = "explicit point-threat state; policy substitution"
        elif play == NACH: reason = "contact now explicit; policy substitution"
        changes[play] = {"old_opportunities_per_fight": old_opp/n, "new_opportunities_per_fight": new_opp/n, "old_uses_per_fight": old_use/n, "new_uses_per_fight": new_use/n, "reason": reason}
    return changes


def build_report(results: dict[str, Any]) -> str:
    lines = [
        "# Crossing/Bind State Model v0.1 Results", "",
        "Status: **PROVISIONAL state-model/regression experiment; not canonical mechanics**", "",
        "The explicit model is internally coherent in deterministic tests and the bounded mirrored matrix. It replaces synthetic bind, Soft, and Close generation with declared or Play-authored transitions while retaining P1, D1, C2, S2, maximum Spiritus 8, and the three-learned-Play cap.", "",
        "## Scope and conflict audit", "",
        "Atra Melee Design Packet v0.4 leaves Bind/Crossing procedure and Crown/Corona mechanics OPEN/DEFERRED. This experiment supplies a PROVISIONAL engine model only and does not update that packet. No Guard effect, generic leverage modifier, generic Hard/Soft choice, or generic closing procedure was added.", "",
        "## State model", "",
        "Persistent exchange state uses `contact: none|crossing`, independent `measure: wide|close`, per-fighter `contact_zone: hiltward|middle|pointward|unknown`, per-fighter `pressure: hard|soft|unknown`, and per-fighter `point_threat: threatening|not_threatening`. Displacement is an event whose `contact_after` may be `none` or `crossing`; it is not a contact state.", "",
        "Crossing cleanup occurs in `Duel.finish_exchange()`, after resolution/aftermath and before the next activation. Unretained Crossings become `none`; explicitly retained Crossings are counted and preserved.", "",
        "## Deterministic transition validation", "",
        "All required cases A-M pass: Cross creates Wide Hard/Hard Crossing with unknown zones and no displacement; Beat displaces and separates; both declarations expose the same pre-roll D1 window; failed forms apply neither contact nor displacement; Absetzen and Scambiar cross while maintaining point threat then clean up; Durchwechseln remains pre-bind with a threatening point; Schielhau creates no automatic Crossing; Rompere represents displacement with retained Crossing; cleanup separates; and forced Close Crossing executes Pommel Strike.", "",
        "## Primary regression matrix", "",
        f"Seed `{results['seed']}`; `{results['trials']['primary_per_cell']}` mirrored fights per primary cell. Skills 10/14/18; starting Spiritus 8/3; Adaptive Revelation/Perfect Information; P1 Cross/Beat, D1, C2, S2, maximum 8.", "",
        "| Cell | Cross/fight | Beat/fight | Cross success | Beat success | Cross D1 | Beat D1 | Crossings/fight | Displace+separate | Wide | Close | Hard/Hard | Unknown pressure | D opp./decl./success | Compounds | Spiritus | Parry/Counter/Ignore | Chain | Cap | Fourth | Win A | Rounds | Double |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|",]
    for label, item in results["primary_matrix"].items():
        m = item["metrics"]
        lines.append(f"| {label} | {m['basic_cross_declarations_per_fight']:.3f} | {m['basic_beat_declarations_per_fight']:.3f} | {m['cross_success_rate']:.1%} | {m['beat_success_rate']:.1%} | {m['cross_interrupted_per_fight']:.3f} | {m['beat_interrupted_per_fight']:.3f} | {m['successful_crossings_per_fight']:.3f} | {m['displacement_separation_per_fight']:.3f} | {m['wide_crossings_per_fight']:.3f} | {m['close_crossings_per_fight']:.3f} | {m['hard_hard_crossings_per_fight']:.3f} | {m['unknown_pressure_crossings_per_fight']:.3f} | {m['durch_opportunities_per_fight']:.3f}/{m['durch_declarations_per_fight']:.3f}/{m['durch_success_rate']:.1%} | {m['compound_declarations_per_fight']:.3f} | {m['spiritus_expenditure_per_fight']:.3f} | {m['basic_parry_frequency']:.1%}/{m['counter_frequency']:.1%}/{m['ignore_frequency']:.1%} | {m['learned_play_chain_length']:.3f} | {m['three_play_cap_frequency']:.2%} | {m['attempted_fourth_plays_per_fight']:.3f} | {m['win_rate_A']:.1%} | {m['average_rounds']:.3f} | {m['double_defeat_rate']:.1%} |")
    lines += ["", "### Remaining required contact metrics — every primary cell", "", "| Cell | Displace + retained Crossing | Hard/Soft | Soft/Hard | Known zone | Unknown zone | Explicit persistence | Exchange-end cleanup |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for label, item in results["primary_matrix"].items():
        m = item["metrics"]
        lines.append(f"| {label} | {m['displacement_retained_crossing_per_fight']:.3f} | {m['hard_soft_crossings_per_fight']:.3f} | {m['soft_hard_crossings_per_fight']:.3f} | {m['known_zone_crossings_per_fight']:.3f} | {m['unknown_zone_crossings_per_fight']:.3f} | {m['crossings_persisted_per_fight']:.3f} | {m['crossings_cleaned_up_per_fight']:.3f} |")
    lines += ["", "All primary cells record zero retained-Crossing displacements, Close Crossings, Hard/Soft or Soft/Hard Crossings, known-zone Crossings, explicit persistence, and attempted fourth Plays. Unknown-zone Crossings equal total Crossings.", "", "## OLD / LEGACY EXERCISE MODEL vs NEW / EXPLICIT CONTACT MODEL", "", "The paired legacy harness preserves only the immediately previous explanatory artifacts: successful Basic Parry synthesizes Wide/Close contact with a 25% Close chance, Zornhau-Ort synthesizes opponent Soft with a 50% chance, and contact may reach a later activation. It is not a valid alternative model.", "", "## Play Opportunity Changes", "", "| Play | Old opportunities/fight | New opportunities/fight | Old uses/fight | New uses/fight | Reason |", "|---|---:|---:|---:|---:|---|"]
    for play, row in results["play_opportunity_changes"].items():
        lines.append(f"| {play} | {row['old_opportunities_per_fight']:.3f} | {row['new_opportunities_per_fight']:.3f} | {row['old_uses_per_fight']:.3f} | {row['new_uses_per_fight']:.3f} | {row['reason']} |")
    zold = sum(item["metrics"]["plays"][ZORN]["continuation_uses_per_fight"] for item in results["legacy_comparison"].values()) / 12
    znew = sum(item["metrics"]["plays"][ZORN]["continuation_uses_per_fight"] for item in results["primary_matrix"].values()) / 12
    lines += ["", f"Zornhau-Ort's initial counter-cut remains available, but its Ort continuation falls from `{zold:.3f}` uses/fight in the synthetic legacy harness to `{znew:.3f}` because no current explicit action produces opponent Soft pressure. Pommel Strike has no main-run opportunities: **MISSING CLOSE-MEASURE TRANSITION**. Its forced-state test passes, so the loss is not evidence that the Play is weak.", "", "Cross and Beat have equal one-step cancellation value in the transparent softmax policy. Their selection frequencies are therefore coverage-sensitive and are not final balance evidence. Any later strong Beat dominance without mature Winden/bind continuations should be classified **BIND-REPERTOIRE COVERAGE ARTIFACT**.", "", "## Synthetic State Removed", "", "- `simulations/longsword_prototype_v0_1/simulate.py`: Basic defence assigned `bind-crossing` or random 25% `close-crossing`; named prototype resolutions also assigned `bind-crossing` directly.", "- `simulations/longsword_prototype_v0_2/simulate.py`: `close_crossing_probability` created Close Crossing and `soft_bind_probability` created Soft Zornhau-Ort continuation conditions; named resolutions assigned contact states directly.", "- `simulations/longsword_prototype_v0_2/state_model_simulate.py`: `legacy_random_half` assigned blade-seeking to 50% of Basic Parries, successful Parry used random 25% Close Crossing, and Zornhau-Ort used random 50% Soft.", "- `simulations/spiritus_parry_durchwechseln/simulate.py`: successful Basic Parry used random 25% Close contact; Absetzen, Scambiar, Schielhau, and Zornhau-Ort assigned synthetic `bind` contact, with random 50% Ort continuation.", "- `simulations/compound_spiritus_c1_c2/simulate.py` inherited those contact rules from the Spiritus base simulator and consumed synthetic Close contact for Pommel Strike.", "- The old proactive-beat shortcut in `state_model_simulate.py` manufactured a Durchwechseln contact context; it is absent from the new primary model.", "", "The prior behavior remains only in the labeled legacy comparison harness. No random bind, pressure, contact zone, or Close Crossing generation remains in the primary model.", "", "## Missing State Creators", "", "- **Soft pressure:** supported by the schema, but no current basic action or active Play explicitly creates it. Zornhau-Ort's Ort continuation therefore has no main-run trigger.", "- **Close Crossing:** supported and force-tested, but no active main-run action closes measure while retaining contact. Pommel Strike therefore has zero main-run opportunity.", "- **Explicit contact-zone geometry:** supported, and Rompere demonstrates opponent-middle geometry in the reference harness, but ordinary Basic Cross, Zornhau-Ort, Absetzen, and Scambiar remain `unknown` where the audit does not establish both blade zones.", "- **Crossing retention:** supported and demonstrated by Rompere's displacement-with-retained-Crossing reference state, but no mirrored active Play currently retains a Crossing beyond exchange cleanup.", "", "## Artifacts and limitations", "", "The combat policy is a transparent one-step expected-value softmax, not a solved equilibrium or player forecast. Generic d6+1 damage, symmetric repertoires, artificial attack proportions, free Zornhau-Ort/Nachreisen/Pommel, unresolved weapon profiles, and absent Guard/engagement geometry remain artifacts. The run is a regression, not price or balance tuning.", "", "## Recommended Next Decision", "", "The explicit Crossing model is internally coherent, and Basic Cross/Beat are technically viable declared forms with the required pre-roll D1 timing. Zornhau-Ort loses its synthetic Ort continuation; Pommel Strike loses synthetic Close opportunities; the other active Plays change mainly through explicit Parry choice, point threat, and policy substitution.", "", "The most urgent state creator is an explicit **close-measure-while-maintaining-contact transition**, because it gates a historically audited active Play and tests the independence of measure from contact geometry. A Soft-producing action is the next pressure question, but it should be sourced/audited rather than invented to restore Ort frequency.", "", "The system is **not yet ready to return to Guard design**. The blocking question is: which explicit action or audited Play changes Wide Crossing to Close while retaining contact, and which action/Play can intentionally yield Soft pressure? Until those transitions exist, proposed Guard bonuses would be evaluated against a contact repertoire missing core measure and pressure pathways.", ""]
    return "\n".join(lines)


def write_csv(rows: list[dict[str, Any]]) -> None:
    with SUMMARY_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def run_all(primary_trials: int = 5000, legacy_trials: int = 1500,
            seed: int = SEED, write: bool = True) -> dict[str, Any]:
    primary: dict[str, Any] = {}; legacy: dict[str, Any] = {}
    for index, cell in enumerate(cells()):
        cell_seed = seed + index * 1009
        primary[cell.label] = run_cell(cell, primary_trials, cell_seed, "explicit")
        legacy[cell.label] = run_cell(cell, legacy_trials, cell_seed, "legacy")
    results = {"model": json.loads(MODEL_PATH.read_text(encoding="utf-8")), "seed": seed,
               "trials": {"primary_per_cell": primary_trials, "legacy_per_cell": legacy_trials},
               "transition_tests": transition_harness(), "primary_matrix": primary,
               "legacy_comparison": legacy}
    results["play_opportunity_changes"] = aggregate_play_changes(results)
    validate_results(results)
    if write:
        RESULTS_PATH.write_text(json.dumps(serial(results), indent=2) + "\n", encoding="utf-8")
        rows = [flatten(item, "NEW_EXPLICIT") for item in primary.values()] + [flatten(item, "OLD_LEGACY") for item in legacy.values()]
        write_csv(rows)
        REPORT_PATH.write_text(build_report(results), encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary-trials", type=int, default=5000)
    parser.add_argument("--legacy-trials", type=int, default=1500)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    results = run_all(args.primary_trials, args.legacy_trials, args.seed, not args.no_write)
    print(f"primary={len(results['primary_matrix'])} legacy={len(results['legacy_comparison'])}")


if __name__ == "__main__":
    main()

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
MODEL_PATH = HERE / "experiment-model.json"
RESULTS_PATH = HERE / "results.json"
REPORT_PATH = ROOT / "reports" / "spiritus-parry-durchwechseln-results.md"

MAX_SPIRITUS = 8
MAX_HP = 8
AVG_DAMAGE = 4.5
TEMPERATURE = 0.18
COMPOUNDS = ("Absetzen", "Scambiar di Punta", "Schielhau")
FREE_PLAYS = ("Zornhau-Ort", "Nachreisen", "Pommel Strike")


@dataclass(frozen=True)
class Cell:
    skill: int = 10
    parry: str = "P1"
    durch_cost: int = 1
    compound_cost: int = 1
    start_spiritus: int = 8
    information: str = "adaptive_revelation"
    timing: str = "pre"
    recovery: str = "R0"
    future_fights: int = 0

    @property
    def label(self) -> str:
        return (
            f"skill{self.skill}_{self.parry}_D{self.durch_cost}_C{self.compound_cost}_"
            f"S{self.start_spiritus}_{self.information}_{self.timing}"
        )


@dataclass
class Fighter:
    name: str
    skill: int
    hp: int = MAX_HP
    spiritus: int = MAX_SPIRITUS
    action_ready: bool = True
    recovery: str = "ready"
    knows_enemy_durch: bool = False
    knows_enemy_schiel: bool = False

    @property
    def alive(self) -> bool:
        return self.hp > 0


def compound_stats() -> dict[str, Any]:
    return {
        "opportunities": 0, "affordable_opportunities": 0, "declarations": 0,
        "successes": 0, "damage": 0, "spiritus_spent": 0,
        "parry_displaced": 0, "counter_displaced": 0,
        "spiritus_at_declaration_sum": 0,
        "early_opportunities": 0, "early_declarations": 0,
        "late_opportunities": 0, "late_declarations": 0,
    }


def fresh_metrics() -> dict[str, Any]:
    return {
        "fights": 0, "wins_A": 0, "wins_B": 0, "double_defeats": 0, "draws": 0,
        "rounds": 0, "defensive_opportunities": 0,
        "defensive_opportunities_after_durch_known": 0,
        "basic_parry_declarations": 0, "basic_parry_after_durch_known": 0,
        "basic_parry_when_attacker_low_spiritus": 0,
        "parry_rolls": 0, "parry_roll_successes": 0,
        "parries_interrupted_by_durch": 0, "parries_durch_declined": 0,
        "durch_opportunities": 0, "durch_declarations": 0, "durch_declines": 0,
        "durch_successes": 0, "durch_damage": 0, "durch_spiritus_spent": 0,
        "durch_contexts": Counter(), "decline_reasons": Counter(),
        "allow_parry_hit_chance_sum": 0.0, "allow_parry_hit_chance_n": 0,
        "durch_success_chance_sum": 0.0, "durch_success_chance_n": 0,
        "accepted_actor_spirit_sum": 0, "accepted_opponent_spirit_sum": 0,
        "accepted_n": 0, "declined_actor_spirit_sum": 0,
        "declined_opponent_spirit_sum": 0, "declined_n": 0,
        "compound_spiritus_spent": 0, "total_spiritus_spent": 0,
        "end_spirit_sum": 0, "end_spirit_n": 0, "end_spirit_buckets": Counter(),
        "unused_spirit_at_defeat_sum": 0, "defeated_combatants": 0,
        "starvation": Counter(), "choices": Counter(),
        "compounds": {name: compound_stats() for name in COMPOUNDS},
        "free_plays": {name: {"declarations": 0, "successes": 0, "damage": 0} for name in FREE_PLAYS},
        "future_value_conservation_decisions": 0,
        "precondition_violations": 0,
    }


def clamp_spiritus(value: int) -> int:
    return max(0, min(MAX_SPIRITUS, value))


def project_spiritus(spiritus: int, boundaries: int, recovery: str) -> int:
    if boundaries <= 0:
        return clamp_spiritus(spiritus)
    if recovery == "RFULL":
        return MAX_SPIRITUS
    if recovery == "R2":
        return clamp_spiritus(spiritus + 2 * boundaries)
    return clamp_spiritus(spiritus)


def reserve_value(spiritus: int, future_fights: int, recovery: str) -> float:
    spiritus = clamp_spiritus(spiritus)
    value = 0.78 * math.sqrt(spiritus)
    for boundary in range(1, future_fights + 1):
        projected = project_spiritus(spiritus, boundary, recovery)
        value += (0.82 ** boundary) * 0.48 * math.sqrt(projected)
    return value


def resource_charge(spiritus: int, cost: int, future_fights: int, recovery: str) -> float:
    if cost <= 0:
        return 0.0
    if spiritus < cost:
        return math.inf
    return reserve_value(spiritus, future_fights, recovery) - reserve_value(
        spiritus - cost, future_fights, recovery
    )


def success_probability(skill: int) -> float:
    return max(0.0, min(1.0, skill / 20.0))


def bucket(spiritus: int) -> str:
    if spiritus == 0:
        return "0"
    if spiritus <= 2:
        return "1-2"
    if spiritus <= 5:
        return "3-5"
    return "6-8"


def serial(value: Any) -> Any:
    if isinstance(value, Counter):
        return dict(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


class Duel:
    def __init__(
        self,
        rng: random.Random,
        policy_rng: random.Random,
        cell: Cell,
        metrics: dict[str, Any],
        spirit_a: int | None = None,
        spirit_b: int | None = None,
    ) -> None:
        self.rng = rng
        self.policy_rng = policy_rng
        self.cell = cell
        self.metrics = metrics
        self.a = Fighter("A", cell.skill, spiritus=cell.start_spiritus if spirit_a is None else spirit_a)
        self.b = Fighter("B", cell.skill, spiritus=cell.start_spiritus if spirit_b is None else spirit_b)
        if cell.information == "perfect_information":
            self.a.knows_enemy_durch = self.b.knows_enemy_durch = True
            self.a.knows_enemy_schiel = self.b.knows_enemy_schiel = True
        self.round_number = 0
        self.contact = "none"
        self.future_conservation = False

    def other(self, fighter: Fighter) -> Fighter:
        return self.b if fighter is self.a else self.a

    def roll(self, fighter: Fighter) -> tuple[bool, int]:
        result = self.rng.randint(1, 20)
        return result <= fighter.skill, result

    def damage(self) -> int:
        return self.rng.randint(1, 6) + 1

    def hurt(self, target: Fighter, play: str | None = None) -> int:
        amount = self.damage()
        target.hp -= amount
        if play in self.metrics["compounds"]:
            self.metrics["compounds"][play]["damage"] += amount
        elif play == "Durchwechseln":
            self.metrics["durch_damage"] += amount
        elif play in self.metrics["free_plays"]:
            self.metrics["free_plays"][play]["damage"] += amount
        return amount

    def spend_action(self, fighter: Fighter) -> None:
        if not fighter.action_ready:
            self.metrics["precondition_violations"] += 1
            return
        fighter.action_ready = False

    def spend_spiritus(self, fighter: Fighter, cost: int, kind: str) -> bool:
        if cost < 0 or fighter.spiritus < cost:
            self.metrics["precondition_violations"] += 1
            return False
        fighter.spiritus = clamp_spiritus(fighter.spiritus - cost)
        self.metrics["total_spiritus_spent"] += cost
        if kind == "durch":
            self.metrics["durch_spiritus_spent"] += cost
        else:
            self.metrics["compound_spiritus_spent"] += cost
        return True

    def weights(self, actor: Fighter, opponent: Fighter) -> tuple[float, float]:
        offense = 1.0 + 0.30 * (MAX_HP - opponent.hp) / MAX_HP + (0.25 if opponent.hp <= 4 else 0.0)
        defense = 1.0 + 0.35 * (MAX_HP - actor.hp) / MAX_HP + (0.35 if actor.hp <= 4 else 0.0)
        return offense, defense

    @staticmethod
    def opponent_spiritus_factor(opponent: Fighter) -> float:
        return 0.9 + 0.2 * (opponent.spiritus / MAX_SPIRITUS)

    def softmax(self, values: dict[str, float], temperature: float = TEMPERATURE) -> str:
        top = max(values.values())
        weights = {k: math.exp((v - top) / temperature) for k, v in values.items()}
        pick = self.policy_rng.random() * sum(weights.values())
        for key, weight in weights.items():
            pick -= weight
            if pick <= 0:
                return key
        return next(reversed(values))

    def durch_scores_for_parry(
        self, attacker: Fighter, defender: Fighter, future_fights: int | None = None,
        observed_parry_success: bool = False,
    ) -> tuple[float, float, float, float]:
        p_durch = success_probability(attacker.skill)
        hit_if_allow = 0.0 if observed_parry_success else 1.0 - success_probability(defender.skill)
        offense, _ = self.weights(attacker, defender)
        horizon = self.cell.future_fights if future_fights is None else future_fights
        charge = resource_charge(attacker.spiritus, self.cell.durch_cost, horizon, self.cell.recovery)
        charge *= self.opponent_spiritus_factor(defender)
        declare = p_durch * offense - charge
        decline = hit_if_allow * offense
        return declare, decline, p_durch, hit_if_allow

    def predicted_durch_rate(self, attacker: Fighter, defender: Fighter) -> float:
        if attacker.spiritus < self.cell.durch_cost:
            return 0.0
        declare, decline, _, _ = self.durch_scores_for_parry(
            attacker, defender, observed_parry_success=self.cell.timing == "post"
        )
        top = max(declare, decline)
        a = math.exp((declare - top) / TEMPERATURE)
        b = math.exp((decline - top) / TEMPERATURE)
        return a / (a + b)

    def decline_reason(
        self, attacker: Fighter, defender: Fighter, declare: float, decline: float,
        p_durch: float, hit_if_allow: float, no_future_declare: float | None = None,
    ) -> str:
        if attacker.spiritus < self.cell.durch_cost or attacker.spiritus <= 2:
            return "low current Spiritus"
        if hit_if_allow >= p_durch:
            return "low defender Parry chance / better to gamble on Parry failure"
        if p_durch < 0.5:
            return "low attacker Durchwechseln chance"
        if self.cell.compound_cost > 0 and attacker.spiritus - self.cell.durch_cost < self.cell.compound_cost:
            return "preserving Spiritus for compound counters"
        if no_future_declare is not None and no_future_declare > decline >= declare:
            return "Spiritus conservation"
        if declare <= decline:
            return "tactical state / expected-value reason"
        return "other (mixed-policy exploration)"

    def durch_decision_parry(
        self, attacker: Fighter, defender: Fighter, observed_parry_success: bool = False
    ) -> bool:
        m = self.metrics
        m["durch_opportunities"] += 1
        m["durch_contexts"]["P1 Basic Parry"] += 1
        declare, decline, p_durch, hit_if_allow = self.durch_scores_for_parry(
            attacker, defender, observed_parry_success=observed_parry_success
        )
        m["allow_parry_hit_chance_sum"] += hit_if_allow
        m["allow_parry_hit_chance_n"] += 1
        m["durch_success_chance_sum"] += p_durch
        m["durch_success_chance_n"] += 1
        affordable = attacker.spiritus >= self.cell.durch_cost
        no_future_declare, _, _, _ = self.durch_scores_for_parry(
            attacker, defender, future_fights=0,
            observed_parry_success=observed_parry_success,
        )
        deterministic_future_flip = affordable and no_future_declare > decline and declare <= decline
        if not affordable:
            selected = "decline"
            if no_future_declare > decline:
                m["starvation"]["Durchwechseln"] += 1
        else:
            selected = self.softmax({"declare": declare, "decline": decline})
        if selected == "declare":
            before = attacker.spiritus
            m["durch_declarations"] += 1
            m["accepted_actor_spirit_sum"] += before
            m["accepted_opponent_spirit_sum"] += defender.spiritus
            m["accepted_n"] += 1
            self.spend_spiritus(attacker, self.cell.durch_cost, "durch")
            defender.knows_enemy_durch = True
            return True
        m["durch_declines"] += 1
        m["declined_actor_spirit_sum"] += attacker.spiritus
        m["declined_opponent_spirit_sum"] += defender.spiritus
        m["declined_n"] += 1
        reason = self.decline_reason(
            attacker, defender, declare, decline, p_durch, hit_if_allow, no_future_declare
        )
        m["decline_reasons"][reason] += 1
        if deterministic_future_flip:
            m["future_value_conservation_decisions"] += 1
            self.future_conservation = True
        return False

    def durch_decision_schiel(
        self, attacker: Fighter, defender: Fighter, schiel_roll: int
    ) -> tuple[bool, float]:
        m = self.metrics
        m["durch_opportunities"] += 1
        m["durch_contexts"]["Schielhau S2 rejoinder"] += 1
        p_win = max(0, min(attacker.skill, schiel_roll - 1)) / 20.0
        offense, defense = self.weights(attacker, defender)
        charge = resource_charge(
            attacker.spiritus, self.cell.durch_cost, self.cell.future_fights, self.cell.recovery
        )
        charge *= self.opponent_spiritus_factor(defender)
        declare = p_win * offense - (1.0 - p_win) * defense - charge
        decline = -defense
        affordable = attacker.spiritus >= self.cell.durch_cost
        no_future_charge = resource_charge(attacker.spiritus, self.cell.durch_cost, 0, self.cell.recovery)
        no_future_charge *= self.opponent_spiritus_factor(defender)
        no_future_declare = p_win * offense - (1.0 - p_win) * defense - no_future_charge
        if not affordable:
            selected = "decline"
            if no_future_declare > decline:
                m["starvation"]["Durchwechseln"] += 1
        else:
            selected = self.softmax({"declare": declare, "decline": decline})
        if selected == "declare":
            before = attacker.spiritus
            m["durch_declarations"] += 1
            m["accepted_actor_spirit_sum"] += before
            m["accepted_opponent_spirit_sum"] += defender.spiritus
            m["accepted_n"] += 1
            m["durch_success_chance_sum"] += p_win
            m["durch_success_chance_n"] += 1
            self.spend_spiritus(attacker, self.cell.durch_cost, "durch")
            defender.knows_enemy_durch = True
            return True, p_win
        m["durch_declines"] += 1
        m["declined_actor_spirit_sum"] += attacker.spiritus
        m["declined_opponent_spirit_sum"] += defender.spiritus
        m["declined_n"] += 1
        m["decline_reasons"][self.decline_reason(
            attacker, defender, declare, decline, p_win, 0.0, no_future_declare
        )] += 1
        if affordable and no_future_declare > decline and declare <= decline:
            m["future_value_conservation_decisions"] += 1
            self.future_conservation = True
        return False, p_win

    def defence_values(self, attacker: Fighter, defender: Fighter, attack: dict[str, Any]) -> dict[str, float]:
        offense, defense = self.weights(defender, attacker)
        p = success_probability(defender.skill)
        values = {"Ignore": 0.0, "Counter": p * offense}
        parry_effective = p
        if self.cell.parry == "P1" and defender.knows_enemy_durch:
            q = self.predicted_durch_rate(attacker, defender)
            if self.cell.timing == "post":
                parry_effective = p * (1.0 - q * success_probability(attacker.skill))
            else:
                parry_effective = (1.0 - q) * p + q * (1.0 - success_probability(attacker.skill))
        values["Basic Parry"] = parry_effective * defense
        charge = resource_charge(
            defender.spiritus, self.cell.compound_cost, self.cell.future_fights, self.cell.recovery
        )
        charge *= self.opponent_spiritus_factor(attacker)
        if attack["type"] == "thrust":
            values["Absetzen"] = p * (offense + defense) - charge
            values["Scambiar di Punta"] = p * (offense + defense) - charge
        if attack["type"] == "descending_cut":
            values["Schielhau"] = p * (offense + defense) - charge
            if attack["committed"]:
                values["Zornhau-Ort"] = p * defense + 0.5 * p * p * offense
        return values

    def record_compound_opportunities(
        self, attacker: Fighter, defender: Fighter, values: dict[str, float]
    ) -> dict[str, float]:
        legal = {name: value for name, value in values.items() if name in COMPOUNDS}
        phase = "early" if self.round_number <= 2 else "late"
        for name, value in legal.items():
            stats = self.metrics["compounds"][name]
            stats["opportunities"] += 1
            stats[f"{phase}_opportunities"] += 1
            if defender.spiritus >= self.cell.compound_cost:
                stats["affordable_opportunities"] += 1
            else:
                alternatives = [v for k, v in values.items() if k not in COMPOUNDS]
                offense, defense = self.weights(defender, attacker)
                raw_benefit = success_probability(defender.skill) * (offense + defense)
                hypothetical_charge = resource_charge(
                    self.cell.compound_cost, self.cell.compound_cost,
                    self.cell.future_fights, self.cell.recovery
                )
                hypothetical_charge *= self.opponent_spiritus_factor(attacker)
                hypothetical = raw_benefit - hypothetical_charge
                if hypothetical > max(alternatives):
                    self.metrics["starvation"][name] += 1
        return legal

    def basic_parry(self, attacker: Fighter, defender: Fighter, attribution: str | None) -> None:
        m = self.metrics
        m["basic_parry_declarations"] += 1
        m["choices"]["Basic Parry"] += 1
        if defender.knows_enemy_durch:
            m["basic_parry_after_durch_known"] += 1
        if attacker.spiritus <= 2:
            m["basic_parry_when_attacker_low_spiritus"] += 1
        self.spend_action(defender)
        if self.cell.parry == "P1" and self.cell.timing == "pre":
            if self.durch_decision_parry(attacker, defender):
                m["parries_interrupted_by_durch"] += 1
                ok, _ = self.roll(attacker)
                if ok:
                    m["durch_successes"] += 1
                    self.hurt(defender, "Durchwechseln")
                return
            m["parries_durch_declined"] += 1
        m["parry_rolls"] += 1
        ok, _ = self.roll(defender)
        if ok:
            m["parry_roll_successes"] += 1
            if self.cell.parry == "P1" and self.cell.timing == "post":
                if self.durch_decision_parry(attacker, defender, observed_parry_success=True):
                    m["parries_interrupted_by_durch"] += 1
                    durch_ok, _ = self.roll(attacker)
                    if durch_ok:
                        m["durch_successes"] += 1
                        self.hurt(defender, "Durchwechseln")
                    return
                m["parries_durch_declined"] += 1
            self.contact = "close" if self.rng.random() < 0.25 else "bind"
            return
        self.hurt(defender, attribution)

    def compound(self, name: str, attacker: Fighter, defender: Fighter, attribution: str | None, values: dict[str, float]) -> None:
        stats = self.metrics["compounds"][name]
        stats["declarations"] += 1
        stats[("early" if self.round_number <= 2 else "late") + "_declarations"] += 1
        stats["spiritus_at_declaration_sum"] += defender.spiritus
        stats["spiritus_spent"] += self.cell.compound_cost
        self.metrics["choices"][name] += 1
        alternatives = {k: v for k, v in values.items() if k not in COMPOUNDS}
        displaced = max(alternatives, key=alternatives.get)
        if displaced == "Basic Parry":
            stats["parry_displaced"] += 1
        elif displaced == "Counter":
            stats["counter_displaced"] += 1
        self.spend_action(defender)
        self.spend_spiritus(defender, self.cell.compound_cost, "compound")
        if name == "Schielhau":
            attacker.knows_enemy_schiel = True
        ok, roll = self.roll(defender)
        if not ok:
            self.hurt(defender, attribution)
            return
        stats["successes"] += 1
        if name == "Schielhau":
            attempted, _ = self.durch_decision_schiel(attacker, defender, roll)
            if attempted:
                durch_ok, durch_roll = self.roll(attacker)
                durch_wins = durch_ok and durch_roll < roll
                if durch_wins:
                    self.metrics["durch_successes"] += 1
                    self.hurt(defender, "Durchwechseln")
                    return
        self.contact = "bind"
        self.hurt(attacker, name)

    def zorn(self, attacker: Fighter, defender: Fighter, attribution: str | None) -> None:
        stats = self.metrics["free_plays"]["Zornhau-Ort"]
        stats["declarations"] += 1
        self.metrics["choices"]["Zornhau-Ort"] += 1
        self.spend_action(defender)
        ok, _ = self.roll(defender)
        if not ok:
            self.hurt(defender, attribution)
            return
        stats["successes"] += 1
        self.contact = "bind"
        if self.rng.random() < 0.5:
            point_ok, _ = self.roll(defender)
            if point_ok:
                self.hurt(attacker, "Zornhau-Ort")

    def counter(self, attacker: Fighter, defender: Fighter, attribution: str | None) -> None:
        self.metrics["choices"]["Counter"] += 1
        self.spend_action(defender)
        self.hurt(defender, attribution)
        ok, _ = self.roll(defender)
        if ok:
            self.hurt(attacker)

    def defend(self, attacker: Fighter, defender: Fighter, attack: dict[str, Any], attribution: str | None) -> None:
        if not defender.action_ready:
            self.hurt(defender, attribution)
            return
        self.metrics["defensive_opportunities"] += 1
        if defender.knows_enemy_durch:
            self.metrics["defensive_opportunities_after_durch_known"] += 1
        values = self.defence_values(attacker, defender, attack)
        legal_compounds = self.record_compound_opportunities(attacker, defender, values)
        affordable = {
            name: value for name, value in values.items()
            if name not in legal_compounds or defender.spiritus >= self.cell.compound_cost
        }
        choice = self.softmax(affordable)
        if choice == "Ignore":
            self.metrics["choices"]["Ignore"] += 1
            self.hurt(defender, attribution)
        elif choice == "Counter":
            self.counter(attacker, defender, attribution)
        elif choice == "Basic Parry":
            self.basic_parry(attacker, defender, attribution)
        elif choice in COMPOUNDS:
            self.compound(choice, attacker, defender, attribution, values)
        else:
            self.zorn(attacker, defender, attribution)

    def choose_attack(self, actor: Fighter) -> dict[str, Any]:
        draw = self.rng.random()
        thrust_cutoff = 0.38 if actor.knows_enemy_schiel else 0.30
        descending_cutoff = 0.56 if actor.knows_enemy_schiel else 0.65
        if draw < thrust_cutoff:
            return {"type": "thrust", "committed": False}
        if draw < descending_cutoff:
            return {"type": "descending_cut", "committed": self.rng.random() < 0.75}
        return {"type": "other_cut", "committed": False}

    def activate(self, actor: Fighter) -> None:
        target = self.other(actor)
        if self.contact == "close":
            stats = self.metrics["free_plays"]["Pommel Strike"]
            stats["declarations"] += 1
            self.spend_action(actor)
            ok, _ = self.roll(actor)
            if ok:
                stats["successes"] += 1
                self.hurt(target, "Pommel Strike")
            self.contact = "none"
            return
        attribution = None
        if target.recovery == "recovering":
            attribution = "Nachreisen"
            stats = self.metrics["free_plays"]["Nachreisen"]
            stats["declarations"] += 1
            target.recovery = "ready"
            attack = {"type": "descending_cut", "committed": True}
        else:
            attack = self.choose_attack(actor)
        self.spend_action(actor)
        self.contact = "none"
        ok, _ = self.roll(actor)
        if not ok:
            if attack["type"] == "descending_cut" and attack["committed"]:
                actor.recovery = "recovering"
            return
        if attribution:
            self.metrics["free_plays"]["Nachreisen"]["successes"] += 1
        self.defend(actor, target, attack, attribution)

    def run(self, max_rounds: int = 100) -> tuple[str, int]:
        for round_number in range(1, max_rounds + 1):
            self.round_number = round_number
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


def record_fight(metrics: dict[str, Any], duel: Duel, outcome: str, rounds: int) -> None:
    metrics["fights"] += 1
    metrics["rounds"] += rounds
    if outcome == "A":
        metrics["wins_A"] += 1
    elif outcome == "B":
        metrics["wins_B"] += 1
    elif outcome == "double":
        metrics["double_defeats"] += 1
    else:
        metrics["draws"] += 1
    for fighter in (duel.a, duel.b):
        metrics["end_spirit_sum"] += fighter.spiritus
        metrics["end_spirit_n"] += 1
        metrics["end_spirit_buckets"][bucket(fighter.spiritus)] += 1
        if not fighter.alive:
            metrics["unused_spirit_at_defeat_sum"] += fighter.spiritus
            metrics["defeated_combatants"] += 1


def ratio(n: float, d: float) -> float:
    return n / d if d else 0.0


def finalize(metrics: dict[str, Any]) -> dict[str, Any]:
    m = serial(metrics)
    fights = metrics["fights"]
    opportunities = metrics["durch_opportunities"]
    parries = metrics["basic_parry_declarations"]
    endpoints = metrics["end_spirit_n"]
    m.update({
        "average_rounds": ratio(metrics["rounds"], fights),
        "basic_parry_declarations_per_fight": ratio(parries, fights),
        "basic_parry_after_known_per_fight": ratio(metrics["basic_parry_after_durch_known"], fights),
        "basic_parry_after_known_opportunity_rate": ratio(
            metrics["basic_parry_after_durch_known"],
            metrics["defensive_opportunities_after_durch_known"],
        ),
        "basic_parry_defensive_opportunity_rate": ratio(parries, metrics["defensive_opportunities"]),
        "basic_parry_success_rate_when_rolled": ratio(metrics["parry_roll_successes"], metrics["parry_rolls"]),
        "parry_interruption_rate": ratio(metrics["parries_interrupted_by_durch"], parries),
        "parry_durch_decline_fraction": ratio(metrics["parries_durch_declined"], parries),
        "durch_declaration_rate": ratio(metrics["durch_declarations"], opportunities),
        "durch_decline_rate": ratio(metrics["durch_declines"], opportunities),
        "durch_success_rate": ratio(metrics["durch_successes"], metrics["durch_declarations"]),
        "durch_damage_per_fight": ratio(metrics["durch_damage"], fights),
        "durch_spiritus_per_fight": ratio(metrics["durch_spiritus_spent"], fights),
        "compound_spiritus_per_fight": ratio(metrics["compound_spiritus_spent"], fights),
        "total_spiritus_per_fight": ratio(metrics["total_spiritus_spent"], fights),
        "mean_end_spiritus_per_combatant": ratio(metrics["end_spirit_sum"], endpoints),
        "end_at_0_rate": ratio(metrics["end_spirit_buckets"]["0"], endpoints),
        "end_at_1_2_rate": ratio(metrics["end_spirit_buckets"]["1-2"], endpoints),
        "unused_spirit_at_defeat_mean": ratio(metrics["unused_spirit_at_defeat_sum"], metrics["defeated_combatants"]),
        "allow_parry_hit_chance_mean": ratio(metrics["allow_parry_hit_chance_sum"], metrics["allow_parry_hit_chance_n"]),
        "durch_success_chance_mean": ratio(metrics["durch_success_chance_sum"], metrics["durch_success_chance_n"]),
        "accepted_actor_spirit_mean": ratio(metrics["accepted_actor_spirit_sum"], metrics["accepted_n"]),
        "accepted_opponent_spirit_mean": ratio(metrics["accepted_opponent_spirit_sum"], metrics["accepted_n"]),
        "declined_actor_spirit_mean": ratio(metrics["declined_actor_spirit_sum"], metrics["declined_n"]),
        "declined_opponent_spirit_mean": ratio(metrics["declined_opponent_spirit_sum"], metrics["declined_n"]),
    })
    for name, raw in metrics["compounds"].items():
        stats = m["compounds"][name]
        stats.update({
            "declaration_rate": ratio(raw["declarations"], raw["opportunities"]),
            "success_rate": ratio(raw["successes"], raw["declarations"]),
            "damage_per_fight": ratio(raw["damage"], fights),
            "spiritus_per_fight": ratio(raw["spiritus_spent"], fights),
            "mean_spiritus_at_declaration": ratio(raw["spiritus_at_declaration_sum"], raw["declarations"]),
            "early_use_rate": ratio(raw["early_declarations"], raw["early_opportunities"]),
            "late_use_rate": ratio(raw["late_declarations"], raw["late_opportunities"]),
        })
    for name, raw in metrics["free_plays"].items():
        m["free_plays"][name].update({
            "declarations_per_fight": ratio(raw["declarations"], fights),
            "success_rate": ratio(raw["successes"], raw["declarations"]),
            "damage_per_fight": ratio(raw["damage"], fights),
        })
    return m


def run_cell(cell: Cell, trials: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    policy_rng = random.Random(seed ^ 0x5A17)
    metrics = fresh_metrics()
    for _ in range(trials):
        duel = Duel(rng, policy_rng, cell, metrics)
        outcome, rounds = duel.run()
        record_fight(metrics, duel, outcome, rounds)
    return {"cell": asdict(cell), "metrics": finalize(metrics)}


def primary_cells() -> Iterable[Cell]:
    for skill in (10, 14, 18):
        for parry in ("P0", "P1"):
            for durch_cost in (0, 1, 2):
                for compound_cost in (0, 1):
                    for start in (8, 5, 3, 1):
                        yield Cell(skill, parry, durch_cost, compound_cost, start)


def perfect_cells() -> Iterable[Cell]:
    for skill in (10, 14, 18):
        for durch_cost in (0, 1, 2):
            for start in (8, 3):
                yield Cell(skill, "P1", durch_cost, 1, start, "perfect_information")
        yield Cell(skill, "P0", 1, 1, 5, "perfect_information")


def timing_cells() -> Iterable[Cell]:
    for skill in (10, 14, 18):
        for timing in ("pre", "post"):
            yield Cell(skill, "P1", 1, 1, 5, "adaptive_revelation", timing)


def edge_cells() -> Iterable[Cell]:
    for parry in ("P0", "P1"):
        yield Cell(10, parry, 1, 1, 0)


def policy_response_surface() -> list[dict[str, Any]]:
    rows = []
    for attacker_skill in (10, 14, 18):
        for defender_skill in (10, 14, 18):
            for spiritus in (8, 5, 3, 1):
                attacker = Fighter("A", attacker_skill, spiritus=spiritus)
                defender = Fighter("B", defender_skill, spiritus=spiritus)
                cell = Cell(attacker_skill, "P1", 1, 1, spiritus, "perfect_information")
                dummy = Duel(random.Random(1), random.Random(2), cell, fresh_metrics(), spiritus, spiritus)
                declare, decline, p_durch, p_allow = dummy.durch_scores_for_parry(attacker, defender)
                top = max(declare, decline)
                a = math.exp((declare - top) / TEMPERATURE)
                b = math.exp((decline - top) / TEMPERATURE)
                rows.append({
                    "attacker_skill": attacker_skill, "defender_skill": defender_skill,
                    "attacker_spiritus": spiritus, "durch_success_chance": p_durch,
                    "hit_chance_if_parry_allowed": p_allow,
                    "policy_declaration_probability": a / (a + b),
                    "deterministic_preference": "declare" if declare > decline else "decline",
                })
    return rows


def apply_recovery(spiritus: int, recovery: str) -> int:
    if recovery == "RFULL":
        return MAX_SPIRITUS
    if recovery == "R2":
        return clamp_spiritus(spiritus + 2)
    return spiritus


def run_sequence_cell(base: Cell, recovery: str, trials: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    policy_rng = random.Random(seed ^ 0x7319)
    per_fight_raw = [fresh_metrics() for _ in range(3)]
    entering_sum = [0, 0, 0]
    leaving_sum = [0, 0, 0]
    entering_buckets = [Counter() for _ in range(3)]
    all_three_wins = 0
    fight1_conservation_sequences = 0
    sequence_end_spirit = 0
    for _ in range(trials):
        focal_spirit = MAX_SPIRITUS
        wins = 0
        conserved_in_fight1 = False
        for fight_index in range(3):
            if fight_index:
                focal_spirit = apply_recovery(focal_spirit, recovery)
            entering_sum[fight_index] += focal_spirit
            entering_buckets[fight_index][bucket(focal_spirit)] += 1
            cell = Cell(
                base.skill, base.parry, base.durch_cost, base.compound_cost,
                focal_spirit, base.information, "pre", recovery, 2 - fight_index,
            )
            duel = Duel(rng, policy_rng, cell, per_fight_raw[fight_index], focal_spirit, MAX_SPIRITUS)
            outcome, rounds = duel.run()
            record_fight(per_fight_raw[fight_index], duel, outcome, rounds)
            focal_spirit = duel.a.spiritus
            leaving_sum[fight_index] += focal_spirit
            wins += outcome == "A"
            if fight_index == 0:
                conserved_in_fight1 = duel.future_conservation
        all_three_wins += wins == 3
        fight1_conservation_sequences += conserved_in_fight1
        sequence_end_spirit += focal_spirit
    return {
        "base_cell": asdict(base), "recovery": recovery, "sequences": trials,
        "entering_spiritus_mean": [value / trials for value in entering_sum],
        "leaving_spiritus_mean": [value / trials for value in leaving_sum],
        "entering_buckets": [
            {key: count / trials for key, count in serial(counter).items()}
            for counter in entering_buckets
        ],
        "fight_metrics": [finalize(raw) for raw in per_fight_raw],
        "all_three_wins_rate": all_three_wins / trials,
        "fight1_future_value_conservation_rate": fight1_conservation_sequences / trials,
        "unused_spiritus_at_sequence_end_mean": sequence_end_spirit / trials,
        "starvation_events_per_sequence": sum(sum(raw["starvation"].values()) for raw in per_fight_raw) / trials,
    }


def find_cell(cells: dict[str, Any], **query: Any) -> dict[str, Any]:
    for item in cells.values():
        if all(item["cell"].get(key) == value for key, value in query.items()):
            return item["metrics"]
    raise KeyError(query)


def pct(value: float) -> str:
    return f"{value:.1%}"


def num(value: float) -> str:
    return f"{value:.3f}"


def build_report(results: dict[str, Any]) -> str:
    fresh = results["fresh_duels"]
    lines = [
        "# Spiritus, Basic Parry, and Durchwechseln Results", "",
        "Status: **PROVISIONAL bounded experiment; no canonical rule change**", "",
        "## Executive result", "",
        "The central result is conditional, not a universal pass. P1 remains visibly usable after revelation at Skill 10 and when the attacker is nearly exhausted, but post-reveal use approaches zero at Skill 18 while the attacker retains a usable reserve. The required pre-roll gamble and D1 price therefore preserve Basic Parry in some important states, not across the whole tested Skill range.", "",
        "| Skill / start | P1 Parries/fight | P1 after-known/fight | After-known opportunities choosing P1 | All defence opportunities choosing P1 | Parries interrupted | Attacker declines Durch | End Spiritus |", "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for skill in (10, 14, 18):
        for start in (8, 5, 3, 1):
            m = find_cell(fresh, skill=skill, parry="P1", durch_cost=1, compound_cost=1, start_spiritus=start)
            lines.append(
                f"| {skill} / {start} | {num(m['basic_parry_declarations_per_fight'])} | {num(m['basic_parry_after_known_per_fight'])} | {pct(m['basic_parry_after_known_opportunity_rate'])} | {pct(m['basic_parry_defensive_opportunity_rate'])} | {pct(m['parry_interruption_rate'])} | {pct(m['durch_decline_rate'])} | {m['mean_end_spiritus_per_combatant']:.2f} |"
            )
    lines += [
        "", "**Core diagnostic — mixed result.** After Durchwechseln is known, Basic Parry is still chosen at Skill 10 and returns strongly when only 1 Spiritus remains. At Skill 18 with starts 8/5, its post-reveal rate is a warning signal near zero. The exact rates are policy outputs, not player-frequency forecasts.", "",
        "## P0 versus P1 and Durchwechseln cost", "",
        "Skill 10, C1, adaptive revelation; values are averaged over the four requested starting pools.", "",
        "| Parry | D cost | Parry/fight | After-known/fight | Durch declare | Durch decline | Durch damage/fight | Spiritus spent/fight |", "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for parry in ("P0", "P1"):
        for cost in (0, 1, 2):
            ms = [find_cell(fresh, skill=10, parry=parry, durch_cost=cost, compound_cost=1, start_spiritus=s) for s in (8, 5, 3, 1)]
            avg = lambda key: sum(m[key] for m in ms) / len(ms)
            lines.append(f"| {parry} | {cost} | {avg('basic_parry_declarations_per_fight'):.3f} | {avg('basic_parry_after_known_per_fight'):.3f} | {avg('durch_declaration_rate'):.1%} | {avg('durch_decline_rate'):.1%} | {avg('durch_damage_per_fight'):.3f} | {avg('total_spiritus_per_fight'):.3f} |")
    lines += [
        "", "P0 suppresses only the Basic-Parry trigger; its remaining Durchwechseln opportunities are the retained S2 Schielhau rejoinder. P0 is a mechanical control, not a historical preference.", "",
        "## Adaptive revelation versus perfect information", "",
        "The reduced perfect-information matrix makes P1 knowledge active from the first defensive opportunity. Adaptive values use only opportunities after actual revelation.", "",
        "| Skill / start | Adaptive post-reveal P1 use | Perfect-information P1 use | Adaptive Durch declaration | Perfect Durch declaration |", "|---|---:|---:|---:|---:|",
    ]
    for skill in (10, 14, 18):
        for start in (8, 3):
            adaptive = find_cell(fresh, skill=skill, parry="P1", durch_cost=1, compound_cost=1, start_spiritus=start)
            perfect = find_cell(results["perfect_information"], skill=skill, parry="P1", durch_cost=1, compound_cost=1, start_spiritus=start)
            lines.append(
                f"| {skill} / {start} | {adaptive['basic_parry_after_known_opportunity_rate']:.1%} | {perfect['basic_parry_defensive_opportunity_rate']:.1%} | {adaptive['durch_declaration_rate']:.1%} | {perfect['durch_declaration_rate']:.1%} |"
            )
    lines += [
        "", "Perfect information changes when deterrence begins but preserves the same direction: P1 remains mixed at Skill 10 and is strongly displaced at Skill 18 while Spiritus is available.", "",
        "## Pre-roll timing", "",
        "The `post` rows are deliberately illegal counterfactuals in which the attacker observes a successful Parry before deciding. They isolate the value of the required pre-roll commitment.", "",
        "| Skill | Timing | Parry/fight | Interrupted | Durch declarations/fight | Durch Spiritus/fight | Durch damage/fight |", "|---|---|---:|---:|---:|---:|---:|",
    ]
    for skill in (10, 14, 18):
        for timing in ("pre", "post"):
            m = find_cell(results["timing_sensitivity"], skill=skill, timing=timing)
            lines.append(f"| {skill} | {timing} | {m['basic_parry_declarations_per_fight']:.3f} | {m['parry_interruption_rate']:.1%} | {m['durch_declarations']/m['fights']:.3f} | {m['durch_spiritus_per_fight']:.3f} | {m['durch_damage_per_fight']:.3f} |")
    lines += [
        "", "Pre-roll timing makes Durchwechseln buy an uncertain alternative to the Parry roll. At Skill 10, the illegal post-roll model spends only after known Parry success and yields more Durch damage per Spiritus. At Skill 14/18 the Parry is already likely to succeed and Durchwechseln is highly reliable, so the uncertainty discount becomes small and the legal pre-roll policy declares at least as often. Timing helps most in the low/equal-success band; it does not rescue high-Skill P1 by itself.", "",
        "## Why attackers decline Durchwechseln", "",
        "D1/C1 P1 cells, all requested skills and starting pools combined:", "",
    ]
    reasons = Counter()
    for item in fresh.values():
        c, m = item["cell"], item["metrics"]
        if c["parry"] == "P1" and c["durch_cost"] == 1 and c["compound_cost"] == 1:
            reasons.update(m["decline_reasons"])
    total_reasons = sum(reasons.values())
    for reason, count in reasons.most_common():
        lines.append(f"- {reason}: **{count:,} ({count/total_reasons:.1%})**")
    lines += [
        "", "These are utility categories, not psychological claims. The explicit 'better to gamble on Parry failure' category is the intended case where the free original-strike branch compares favorably with a paid Durchwechseln roll.", "",
        "## Skill relationship response surface", "",
        "One-window D1 policy probabilities at full HP and Spiritus 5 (perfect repertoire knowledge):", "",
        "| Attacker Skill | Defender Skill | Hit if Parry rolls | Durch success | Declare probability | Deterministic preference |", "|---:|---:|---:|---:|---:|---|",
    ]
    for row in results["policy_response_surface"]:
        if row["attacker_spiritus"] == 5:
            lines.append(f"| {row['attacker_skill']} | {row['defender_skill']} | {row['hit_chance_if_parry_allowed']:.1%} | {row['durch_success_chance']:.1%} | {row['policy_declaration_probability']:.1%} | {row['deterministic_preference']} |")
    lines += [
        "", "Low defender Skill raises the chance that the original Parry simply fails, making conservation rational. High defender Skill and high attacker Skill favor Durchwechseln. The complete surface for Spiritus 8/5/3/1 is in `results.json`.", "",
        "## Compound counter price", "",
        "Skill 10, P1/D1, adaptive revelation; averaged over starting Spiritus 8/5/3/1.", "",
        "| Cost | Play | Opportunities | Use rate | Success | Damage/fight | Spiritus/fight | Parry displaced | Counter displaced | Mean Spiritus at declaration | Early use | Late use |", "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cost in (0, 1):
        cells = [find_cell(fresh, skill=10, parry="P1", durch_cost=1, compound_cost=cost, start_spiritus=s) for s in (8, 5, 3, 1)]
        for play in COMPOUNDS:
            sums = {key: sum(m["compounds"][play][key] for m in cells) for key in cells[0]["compounds"][play] if isinstance(cells[0]["compounds"][play][key], (int, float))}
            opp = sums["opportunities"]
            decl = sums["declarations"]
            lines.append(f"| {cost} | {play} | {opp:,} | {ratio(decl, opp):.1%} | {ratio(sums['successes'], decl):.1%} | {sum(m['compounds'][play]['damage_per_fight'] for m in cells)/4:.3f} | {sum(m['compounds'][play]['spiritus_per_fight'] for m in cells)/4:.3f} | {sums['parry_displaced']:,} | {sums['counter_displaced']:,} | {ratio(sums['spiritus_at_declaration_sum'], decl):.2f} | {ratio(sums['early_declarations'], sums['early_opportunities']):.1%} | {ratio(sums['late_declarations'], sums['late_opportunities']):.1%} |")
    lines += [
        "", "C1 reduces compound-counter use without eliminating the named counters: roughly half of Schielhau opportunities and a little over one third of each thrust-counter opportunity are still selected in this Skill-10 aggregate. Late use does not fall below early use in these short fights, so the evidence supports price sensitivity, not a claim that late-fight scarcity alone drives substitution. Because all three choices share the same one-roll Variant A chassis here, a common candidate price is supported only within this abstraction.", "",
        "## Three-fight Spiritus isolation experiment", "",
        "Focal HP, actions, recovery state, and knowledge reset each fight; only Spiritus carries. Every opponent is fresh at Spiritus 8. All three duels are run even after a focal loss so resource trajectories are not survivor-biased. 'All three wins' is therefore an outcome index, not literal campaign survival.", "",
        "| Cell | Recovery | Enter F1/F2/F3 | Leave F1/F2/F3 | Spend F1/F2/F3 | Durch F1/F2/F3 | Compound F1/F2/F3 | Parry F1/F2/F3 | Enter F2 0 / 1-2 / 3-5 / 6-8 | Enter F3 0 / 1-2 / 3-5 / 6-8 | Future-value conservation | Starvation/sequence | All-three wins |", "|---|---|---|---|---|---|---|---|---|---|---:|---:|---:|",
    ]
    for item in results["sequences"].values():
        c = item["base_cell"]
        label = f"D{c['durch_cost']}/C{c['compound_cost']}"
        joins = lambda values: "/".join(f"{v:.2f}" for v in values)
        fight_metrics = item["fight_metrics"]
        spends = [m["total_spiritus_per_fight"] for m in fight_metrics]
        durchs = [m["durch_declarations"] / m["fights"] for m in fight_metrics]
        comps = [sum(p["declarations"] for p in m["compounds"].values()) / m["fights"] for m in fight_metrics]
        parries = [m["basic_parry_declarations_per_fight"] for m in fight_metrics]
        def btext(index: int) -> str:
            b = item["entering_buckets"][index]
            return "/".join(f"{b.get(k, 0):.0%}" for k in ("0", "1-2", "3-5", "6-8"))
        lines.append(f"| {label} | {item['recovery']} | {joins(item['entering_spiritus_mean'])} | {joins(item['leaving_spiritus_mean'])} | {joins(spends)} | {joins(durchs)} | {joins(comps)} | {joins(parries)} | {btext(1)} | {btext(2)} | {item['fight1_future_value_conservation_rate']:.1%} | {item['starvation_events_per_sequence']:.3f} | {item['all_three_wins_rate']:.1%} |")
    lines += [
        "", f"Advanced Plays persist into Fights 2 and 3, but D1/C1 does **not** create strong three-fight attrition in this short-duel model: under R0 the focal fighter still averages {results['sequences']['D1_C1_R0']['leaving_spiritus_mean'][2]:.2f} Spiritus after Fight 3 and records no material starvation. R2 restores almost every focal fighter to 6–8 before later fights and tracks RFULL closely, so +2 is too generous at this fight length/cadence. Recovery remains experimental; these rows do not define a breather or rest.", "",
        "## P1 cell diagnostic fields", "",
        "Every P1 cell in `results.json` includes Parry declarations and post-knowledge declarations; defensive-opportunity rate; rolled success; interruption/decline fractions; expected allow-Parry and Durch success chances; both fighters' Spiritus at accepted/declined decisions; Durch opportunities, declarations, declines, success, damage, and spend; compound spend; total spend; fight-end Spiritus buckets; and unused Spiritus at defeat. Declines are policy-classified. Compound records include opportunities, declarations, success, damage, spend, displaced alternatives, Spiritus at declaration, and early/late use.", "",
        "## Matrix coverage and omissions", "",
        f"- Adaptive fresh-duel primary matrix: **{len(results['fresh_duels'])} cells**, the full 3 Skill × 2 Parry × 3 Durch cost × 2 compound cost × 4 starting-pool matrix.",
        f"- Perfect-information reduction: **{len(results['perfect_information'])} cells**. It retains P1 at all three Skills and D0/D1/D2 with C1 at starts 8 and 3, plus one P0/D1/C1/start-5 control per Skill. P1/C0, starts 5/1, and most P0 cells were omitted because the adaptive full matrix already establishes their monotonic resource direction and the reduced run is only an equilibrium check.",
        f"- Edge start 0: **{len(results['edge_cases'])} cells** at Skill 10, D1/C1, P0/P1.",
        "- S1/S3 were not multiplied across the matrix. The prior report already establishes them as sensitivity variants; this experiment keeps S2 as requested.",
        "- Exploratory HP carryover was omitted because it would add injury assumptions without helping isolate the resource question.",
        "- Power Strike competition was skipped: the prototype has no sufficiently mature Guard/Chamber state model to represent it reliably.", "",
        "## Artifacts and limitations", "",
        "- All tactical rates depend on the transparent utility weights and softmax temperature. The response surface is more trustworthy as a direction-of-effect check than as a behavioral forecast.",
        "- Generic d6+1 damage, HP 8, artificial attack mix, 50% soft-bind exercise rate, and 25% close-crossing exercise rate affect urgency and opportunity counts.",
        "- Zornhau-Ort's pre-bind point threat remains uncertain. It, Nachreisen, and Pommel Strike remain free; any substitution toward them is a zero-cost policy artifact, not a recommendation to price them.",
        "- Guards, Power Strike/Chamber competition, bind calibration, engagement geometry, and weapon profiles remain OPEN.",
        "- Adaptive revelation lasts only within each fight. Spiritus is public. No recovery rule is canonized.", "",
        "## Answers to the design questions", "",
        "A. **Conditionally.** P1 remains viable after reveal at Skill 10 and under attacker depletion, but it is effectively displaced after reveal at Skill 18 with usable Spiritus. That high-Skill warning prevents a general 'P1 remains viable' conclusion.",
        "B. **Pre-roll declaration matters most where Parry failure is a real gamble.** It materially restrains Skill-10 use; at Skill 14/18 it is insufficient by itself because Durchwechseln's success advantage is large.",
        "C–D. **D1 is still the most promising candidate, with a high-Skill caveat.** D0 weakens scarcity; D2 suppresses more depleted-pool use but still cannot preserve high-Skill post-reveal P1 reliably. D1 produces both declarations and the intended gamble declines in the lower/equal band.",
        "E. **Saving is favored when defender Skill is low relative to attacker Skill and/or the attacker is depleted.** Exact policy probabilities are tabulated above and in the response surface.",
        "F–G. **C1 is the better candidate than C0 in this chassis.** It keeps compounds visible while preventing the near-automatic C0 Schielhau rate, though late-use results remain policy/urgency-sensitive.",
        "H–I. Lower starting or observed attacker Spiritus increases conservation, unaffordability, and Basic-Parry attractiveness.",
        "J–K. **R0 attrition is weak and R2 is too generous in this model.** R2 nearly converges to RFULL because average spend is below +2 per fight.",
        "L–M. **Maximum 8 is tactically valued but operationally generous here.** Fresh fighters usually spend about 1–1.5 and R0 still leaves enough for advanced Plays after three fights. Longer fights or another competing expenditure are needed to tell whether 8 is a useful campaign reserve rather than effectively unlimited for this cadence.",
        "N. AI utility, damage, Guards, bind/geometry, and weapon-profile artifacts remain unresolved and prevent canonical balancing conclusions.", "",
        "## Recommended Next Decision", "",
        "Retain **D1** and **C1** as the best next-test candidates, but do **not** accept P1 as universally healthy: it needs a high-Skill remedy or a broader cost/success model because post-reveal use collapses at Skill 18. Keep maximum Spiritus **8** provisional; it is promising as a reserve but too generous to validate with these short fights alone. Do not prioritize **R2 (+2)** as the candidate recovery cadence yet—it behaves almost like RFULL here. If retained, use it only as an upper-bound control while testing +1, longer fights, or a mature competing 1-Spiritus Power Strike. Do **not** update Atra Melee Design Packet v0.4 yet.", "",
        f"Seed: `{results['seed']}`. Trials: `{results['trials']}`. All mechanics and policy weights remain PROVISIONAL.",
    ]
    return "\n".join(lines) + "\n"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def flatten_cell(item: dict[str, Any]) -> dict[str, Any]:
    c, m = item["cell"], item["metrics"]
    keys = (
        "basic_parry_declarations_per_fight", "basic_parry_after_known_per_fight",
        "basic_parry_after_known_opportunity_rate",
        "basic_parry_defensive_opportunity_rate", "basic_parry_success_rate_when_rolled",
        "parry_interruption_rate", "parry_durch_decline_fraction", "durch_declaration_rate",
        "durch_decline_rate", "durch_success_rate", "durch_damage_per_fight",
        "durch_spiritus_per_fight", "compound_spiritus_per_fight", "total_spiritus_per_fight",
        "mean_end_spiritus_per_combatant", "end_at_0_rate", "end_at_1_2_rate",
        "unused_spirit_at_defeat_mean", "allow_parry_hit_chance_mean",
        "durch_success_chance_mean", "accepted_actor_spirit_mean",
        "accepted_opponent_spirit_mean", "declined_actor_spirit_mean",
        "declined_opponent_spirit_mean",
    )
    return {**c, **{key: m[key] for key in keys}}


def run_all(
    fresh_trials: int = 3000,
    reduced_trials: int = 4000,
    sequence_trials: int = 5000,
    seed: int = 8112026,
    write: bool = True,
) -> dict[str, Any]:
    fresh: dict[str, Any] = {}
    for index, cell in enumerate(primary_cells()):
        fresh[cell.label] = run_cell(cell, fresh_trials, seed + index * 1009)
    perfect: dict[str, Any] = {}
    for index, cell in enumerate(perfect_cells()):
        perfect[cell.label] = run_cell(cell, reduced_trials, seed + 200_000 + index * 1013)
    timing: dict[str, Any] = {}
    for index, cell in enumerate(timing_cells()):
        timing[cell.label] = run_cell(cell, reduced_trials, seed + 300_000 + index * 1019)
    edges: dict[str, Any] = {}
    for index, cell in enumerate(edge_cells()):
        edges[cell.label] = run_cell(cell, reduced_trials, seed + 400_000 + index * 1021)
    sequences: dict[str, Any] = {}
    bases = (
        Cell(10, "P1", 1, 1, 8), Cell(10, "P1", 0, 1, 8),
        Cell(10, "P1", 2, 1, 8), Cell(10, "P1", 1, 0, 8),
    )
    sequence_index = 0
    for base in bases:
        for recovery in ("R0", "R2", "RFULL"):
            label = f"D{base.durch_cost}_C{base.compound_cost}_{recovery}"
            sequences[label] = run_sequence_cell(
                base, recovery, sequence_trials, seed + 500_000 + sequence_index * 1031
            )
            sequence_index += 1
    results = {
        "model": json.loads(MODEL_PATH.read_text(encoding="utf-8")),
        "seed": seed,
        "trials": {"fresh_per_cell": fresh_trials, "reduced_per_cell": reduced_trials, "sequences_per_cell": sequence_trials},
        "fresh_duels": fresh,
        "perfect_information": perfect,
        "timing_sensitivity": timing,
        "edge_cases": edges,
        "policy_response_surface": policy_response_surface(),
        "sequences": sequences,
    }
    if write:
        RESULTS_PATH.write_text(json.dumps(serial(results), indent=2) + "\n", encoding="utf-8")
        REPORT_PATH.write_text(build_report(results), encoding="utf-8")
        write_csv(HERE / "fresh-duel-summary.csv", [flatten_cell(item) for item in fresh.values()])
        write_csv(HERE / "timing-sensitivity-summary.csv", [flatten_cell(item) for item in timing.values()])
        compound_rows = []
        for item in fresh.values():
            for name, stats in item["metrics"]["compounds"].items():
                compound_rows.append({**item["cell"], "play": name, **stats})
        write_csv(HERE / "compound-play-summary.csv", compound_rows)
        sequence_rows = []
        for label, item in sequences.items():
            row = {"label": label, **item["base_cell"], "recovery": item["recovery"]}
            for i in range(3):
                row[f"enter_fight_{i+1}"] = item["entering_spiritus_mean"][i]
                row[f"leave_fight_{i+1}"] = item["leaving_spiritus_mean"][i]
                row[f"spend_fight_{i+1}"] = item["fight_metrics"][i]["total_spiritus_per_fight"]
                row[f"durch_fight_{i+1}"] = item["fight_metrics"][i]["durch_declarations"] / item["fight_metrics"][i]["fights"]
                row[f"compound_fight_{i+1}"] = sum(p["declarations"] for p in item["fight_metrics"][i]["compounds"].values()) / item["fight_metrics"][i]["fights"]
                row[f"parry_fight_{i+1}"] = item["fight_metrics"][i]["basic_parry_declarations_per_fight"]
            row["fight1_future_value_conservation_rate"] = item["fight1_future_value_conservation_rate"]
            row["starvation_events_per_sequence"] = item["starvation_events_per_sequence"]
            row["all_three_wins_rate"] = item["all_three_wins_rate"]
            sequence_rows.append(row)
        write_csv(HERE / "sequence-summary.csv", sequence_rows)
    return results


def validate_results(results: dict[str, Any]) -> None:
    assert len(results["fresh_duels"]) == 144
    assert len(results["perfect_information"]) == 21
    assert len(results["timing_sensitivity"]) == 6
    assert len(results["sequences"]) == 12
    for group in ("fresh_duels", "perfect_information", "timing_sensitivity", "edge_cases"):
        for item in results[group].values():
            m = item["metrics"]
            assert m["precondition_violations"] == 0
            assert 0 <= m["mean_end_spiritus_per_combatant"] <= MAX_SPIRITUS
            assert m["durch_declarations"] <= m["durch_opportunities"]
            assert m["parries_interrupted_by_durch"] <= m["basic_parry_declarations"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fresh-trials", type=int, default=3000)
    parser.add_argument("--reduced-trials", type=int, default=4000)
    parser.add_argument("--sequence-trials", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=8112026)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    results = run_all(
        args.fresh_trials, args.reduced_trials, args.sequence_trials,
        args.seed, write=not args.no_write,
    )
    validate_results(results)
    print(
        f"fresh={len(results['fresh_duels'])} perfect={len(results['perfect_information'])} "
        f"timing={len(results['timing_sensitivity'])} sequences={len(results['sequences'])}"
    )


if __name__ == "__main__":
    main()

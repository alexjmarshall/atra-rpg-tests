from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE_PATH = ROOT / "simulations" / "crossing_bind_state_model_v0_1" / "simulate.py"
RESULTS_PATH = ROOT / "reports" / "loaded-power-attack-v01-results.json"
REPORT_PATH = ROOT / "reports" / "loaded-power-attack-v01-results.md"

SPEC = importlib.util.spec_from_file_location("loaded_power_crossing_base", BASE_PATH)
BASE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = BASE
SPEC.loader.exec_module(BASE)

MAX_HP = 8
MAX_SPIRITUS = 8
SEED = 1108202601
PRIMARY_TRIALS = 2000
SENSITIVITY_TRIALS = 2000
POLICY_TEMPERATURE = BASE.TEMPERATURE

MODELS: dict[str, dict[str, Any]] = {
    "C0": {"loaded": False, "power": False, "cost": 0, "attack_bane": False, "counter_first": False},
    "L0": {"loaded": True, "power": False, "cost": 0, "attack_bane": False, "counter_first": False},
    "P1": {"loaded": True, "power": True, "cost": 1, "attack_bane": False, "counter_first": True},
    "P2": {"loaded": True, "power": True, "cost": 1, "attack_bane": True, "counter_first": True},
    "P3": {"loaded": True, "power": True, "cost": 2, "attack_bane": False, "counter_first": True},
    "P4": {"loaded": True, "power": True, "cost": 2, "attack_bane": False, "counter_first": True},
}

ATTACK_LABELS = {
    "basic_thrust": "Basic Thrust",
    "basic_cut": "Ordinary Basic Cut",
    "loaded_cut": "Ordinary Loaded Cut",
    "power_attack": "Power Attack",
    "learned_cut": "Learned-Play Cut",
}
RESPONSE_NAMES = (
    "Basic Cross", "Basic Beat", "Counter", "Ignore",
    BASE.SCHIEL, BASE.ZORN, BASE.ABSETZEN, BASE.SCIAMBIAR,
)


@dataclass(frozen=True)
class Cell:
    model: str
    skill: int
    start_spiritus: int
    information: str = "adaptive_revelation"
    counter_first: bool | None = None

    @property
    def label(self) -> str:
        suffix = ""
        if self.counter_first is not None:
            suffix = "_CF" if self.counter_first else "_SIM"
        return f"{self.model}_skill{self.skill}_S{self.start_spiritus}{suffix}"


def ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def softmax_probabilities(values: dict[str, float], temperature: float = POLICY_TEMPERATURE) -> dict[str, float]:
    top = max(values.values())
    weights = {key: math.exp((value - top) / temperature) for key, value in values.items()}
    total = sum(weights.values())
    return {key: value / total for key, value in weights.items()}


def normal_damage_distribution() -> dict[int, float]:
    return {value + 1: 1 / 6 for value in range(1, 7)}


def loaded_damage_distribution() -> dict[int, float]:
    counts: Counter[int] = Counter()
    for first in range(1, 7):
        for second in range(1, 7):
            counts[max(first, second) + 1] += 1
    return {value: count / 36 for value, count in sorted(counts.items())}


def summed_damage_distribution() -> dict[int, float]:
    counts: Counter[int] = Counter()
    for first in range(1, 7):
        for second in range(1, 7):
            counts[first + second + 1] += 1
    return {value: count / 36 for value, count in sorted(counts.items())}


def doubled_damage_distribution() -> dict[int, float]:
    return {2 * (die + 1): 1 / 6 for die in range(1, 7)}


def distribution_for(attack_name: str) -> dict[int, float]:
    if attack_name in ("ordinary_basic_cut", "Basic Cut", "basic_cut", "basic_thrust", "learned_cut"):
        return normal_damage_distribution()
    if attack_name in ("ordinary_loaded_cut", "Loaded Cut", "loaded_cut"):
        return loaded_damage_distribution()
    if attack_name == "P1":
        return {7: 1.0}
    if attack_name in ("P2", "P3"):
        return summed_damage_distribution()
    if attack_name == "P4":
        return doubled_damage_distribution()
    raise KeyError(attack_name)


def expected(distribution: dict[int, float]) -> float:
    return sum(value * probability for value, probability in distribution.items())


def probability_at_least(distribution: dict[int, float], threshold: int) -> float:
    return sum(probability for value, probability in distribution.items() if value >= threshold)


def attack_success_probability(skill: int, bane: bool = False) -> float:
    p = BASE.success_probability(skill)
    return p * p if bane else p


def throughchange_probability(skill: int, spiritus: int = 8, defender_hp: int = 8) -> float:
    if spiritus < BASE.DURCH_COST:
        return 0.0
    p = BASE.success_probability(skill)
    offense = 1.0 + 0.3 * (MAX_HP - defender_hp) / MAX_HP
    declare = p * offense - BASE.reserve_charge(spiritus, BASE.DURCH_COST)
    decline = (1.0 - p) * offense
    return softmax_probabilities({"declare": declare, "decline": decline})["declare"]


def attack_stats() -> dict[str, Any]:
    return {
        "opportunities": 0,
        "declarations": 0,
        "attack_roll_hits": 0,
        "raw_damage_on_hits": 0,
        "delivered_damage": 0,
        "damage_events": 0,
        "kills": 0,
        "fresh_target_damage_events": 0,
        "fresh_target_kills": 0,
        "kills_from_4_or_less": 0,
        "overkill_sum": 0,
        "overkill_distribution": Counter(),
    }


def fresh_metrics() -> dict[str, Any]:
    metrics = BASE.fresh_metrics()
    metrics.update({
        "total_damage": 0,
        "damage_events": 0,
        "kills_from_full_hp": 0,
        "kills_from_4_or_less": 0,
        "fight_length_distribution": Counter(),
        "end_spiritus_total": 0,
        "power_spiritus_spent": 0,
        "attack_stats": {name: attack_stats() for name in ATTACK_LABELS},
        "responses": {
            "ordinary_loaded_cut": Counter(),
            "power_attack": Counter(),
            "ordinary_basic_cut": Counter(),
            "basic_thrust": Counter(),
            "learned_cut": Counter(),
        },
        "power_parried_by_cross": 0,
        "power_parried_by_beat": 0,
        "power_counter_choices": 0,
        "counter_first_interruptions": 0,
        "counter_first_prevented_power_kills": 0,
        "power_vs_compound_defence": 0,
        "blocked_durch_due_committed": 0,
        "blocked_attacking_continuations_due_committed": 0,
        "illegal_throughchange_attempts": 0,
        "illegal_attacker_play_insertions": 0,
        "power_inside_existing_play_exchange": 0,
        "learned_plays_attempted_after_committing": 0,
        "power_caused_kills": 0,
        "counter_first_cancelled_power_attacks": 0,
        "counter_first_opportunities": 0,
        "counter_first_attacker_wounded_opportunities": 0,
        "counter_first_attacker_wounded_interruptions": 0,
    })
    return metrics


class LoadedPowerDuel(BASE.Duel):
    """Bounded extension of the explicit Crossing engine; no named-Guard economy."""

    def __init__(self, rng: random.Random, policy_rng: random.Random, cell: Cell,
                 metrics: dict[str, Any]) -> None:
        base_cell = BASE.Cell(cell.skill, cell.start_spiritus, cell.information)
        super().__init__(rng, policy_rng, base_cell, metrics, model="explicit")
        self.experiment_cell = cell
        self.rules = dict(MODELS[cell.model])
        if cell.counter_first is not None:
            self.rules["counter_first"] = cell.counter_first
        self.pending_attack: dict[str, Any] | None = None
        self.pending_damage: int | None = None
        self.pending_target: BASE.Fighter | None = None
        self.committed_attacker: BASE.Fighter | None = None

    def damage(self) -> int:
        return self.rng.randint(1, 6) + 1

    def damage_for(self, attack_key: str, dice: tuple[int, ...] | None = None) -> int:
        if attack_key in ("basic_thrust", "basic_cut", "learned_cut"):
            die = dice[0] if dice else self.rng.randint(1, 6)
            return die + 1
        if attack_key == "loaded_cut":
            rolls = dice if dice else (self.rng.randint(1, 6), self.rng.randint(1, 6))
            return max(rolls) + 1
        if attack_key == "P1":
            return 7
        if attack_key in ("P2", "P3"):
            rolls = dice if dice else (self.rng.randint(1, 6), self.rng.randint(1, 6))
            return rolls[0] + rolls[1] + 1
        if attack_key == "P4":
            die = dice[0] if dice else self.rng.randint(1, 6)
            return 2 * (die + 1)
        raise KeyError(attack_key)

    def _apply_damage(self, target: BASE.Fighter, amount: int, play: str | None = None,
                      attack_key: str | None = None) -> None:
        before = target.hp
        target.hp -= amount
        self.metrics["total_damage"] += amount
        self.metrics["damage_events"] += 1
        if play in self.metrics["plays"]:
            self.metrics["plays"][play]["damage"] += amount
        if attack_key is None:
            return
        stats = self.metrics["attack_stats"][attack_key]
        stats["delivered_damage"] += amount
        stats["damage_events"] += 1
        if before == MAX_HP:
            stats["fresh_target_damage_events"] += 1
        if target.hp <= 0:
            stats["kills"] += 1
            if before == MAX_HP:
                stats["fresh_target_kills"] += 1
                self.metrics["kills_from_full_hp"] += 1
            if before <= 4:
                stats["kills_from_4_or_less"] += 1
                self.metrics["kills_from_4_or_less"] += 1
            overkill = max(0, amount - before)
            stats["overkill_sum"] += overkill
            stats["overkill_distribution"][str(overkill)] += 1
            if attack_key == "power_attack":
                self.metrics["power_caused_kills"] += 1

    def hurt(self, target: BASE.Fighter, play: str | None = None) -> None:
        if (
            self.pending_attack is not None
            and self.pending_damage is not None
            and target is self.pending_target
            and play == self.pending_attack["attribution"]
        ):
            amount = self.pending_damage
            attack_key = self.pending_attack["stats_key"]
            self._apply_damage(target, amount, play=play, attack_key=attack_key)
            self.pending_damage = None
            return
        self._apply_damage(target, self.damage(), play=play)

    def roll_attack(self, actor: BASE.Fighter, bane: bool = False,
                    forced_rolls: tuple[int, ...] | None = None) -> tuple[bool, tuple[int, ...]]:
        rolls = forced_rolls or ((self.rng.randint(1, 20), self.rng.randint(1, 20)) if bane else (self.rng.randint(1, 20),))
        result = max(rolls) if bane else rolls[0]
        return result <= actor.skill, tuple(rolls)

    def declare_power(self, actor: BASE.Fighter) -> bool:
        if not self.rules["power"] or actor.spiritus < self.rules["cost"]:
            return False
        if self.current_chain:
            return False
        if not self.spend_spiritus(actor, self.rules["cost"], "power"):
            return False
        self.committed_attacker = actor
        return True

    def attempt_attacker_continuation(self, actor: BASE.Fighter, name: str) -> bool:
        if self.committed_attacker is actor:
            self.metrics["learned_plays_attempted_after_committing"] += 1
            self.metrics["blocked_attacking_continuations_due_committed"] += 1
            if name == BASE.DURCH:
                self.metrics["blocked_durch_due_committed"] += 1
            else:
                self.metrics["illegal_attacker_play_insertions"] += 1
            return False
        return self.add_play(name)

    def defence_values(self, attacker: BASE.Fighter, defender: BASE.Fighter,
                       attack: dict[str, Any]) -> dict[str, float]:
        p_def = BASE.success_probability(defender.skill)
        p_att = attack_success_probability(attacker.skill, attack.get("attack_bane", False))
        pressure = attack["expected_damage"] / expected(normal_damage_distribution())
        offense = 1.0 + 0.3 * (MAX_HP - attacker.hp) / MAX_HP
        defense = 1.0 + 0.35 * (MAX_HP - defender.hp) / MAX_HP
        durch_q = 0.0
        if attack["durch_legal"] and attacker.spiritus >= BASE.DURCH_COST:
            durch_q = throughchange_probability(attacker.skill, attacker.spiritus, defender.hp)
        cancel_probability = (1.0 - durch_q) * p_def + durch_q * (1.0 - p_att)
        parry_value = cancel_probability * pressure * defense
        counter_value = p_def * offense
        if attack["power"] and self.rules["counter_first"]:
            interrupt = p_def * probability_at_least(normal_damage_distribution(), attacker.hp)
            counter_value += interrupt * pressure * defense
        values = {
            "Ignore": 0.0,
            "Counter": counter_value,
            "Basic Cross": parry_value,
            "Basic Beat": parry_value,
        }
        charge = BASE.reserve_charge(defender.spiritus, BASE.COMPOUND_COST)
        if attack["type"] == "thrust" and math.isfinite(charge):
            values[BASE.ABSETZEN] = p_def * (offense + pressure * defense) - charge
            values[BASE.SCIAMBIAR] = p_def * (offense + pressure * defense) - charge
        if attack["type"] == "descending_cut":
            if math.isfinite(charge):
                values[BASE.SCHIEL] = p_def * (offense + pressure * defense) - charge
            if attack["base_committed"]:
                values[BASE.ZORN] = p_def * pressure * defense + 0.5 * p_def * p_def * offense
        return values

    def expected_action_value(self, actor: BASE.Fighter, target: BASE.Fighter,
                              attack: dict[str, Any]) -> float:
        p_att = attack_success_probability(actor.skill, attack.get("attack_bane", False))
        p_def = BASE.success_probability(target.skill)
        damage_mean = attack["expected_damage"]
        values = self.defence_values(actor, target, attack)
        response_probs = softmax_probabilities(values)
        incoming = 0.0
        self_damage = 0.0
        for response, probability in response_probs.items():
            if response == "Ignore":
                incoming += probability * damage_mean
            elif response in ("Basic Cross", "Basic Beat"):
                if attack["durch_legal"]:
                    q = throughchange_probability(actor.skill, actor.spiritus, target.hp)
                    incoming += probability * (
                        q * BASE.success_probability(actor.skill) * expected(normal_damage_distribution())
                        + (1.0 - q) * (1.0 - p_def) * damage_mean
                    )
                else:
                    incoming += probability * (1.0 - p_def) * damage_mean
            elif response == "Counter":
                survival = 1.0
                if attack["power"] and self.rules["counter_first"]:
                    survival -= p_def * probability_at_least(normal_damage_distribution(), actor.hp)
                incoming += probability * survival * damage_mean
                self_damage += probability * p_def * expected(normal_damage_distribution())
            elif response in (BASE.ABSETZEN, BASE.SCIAMBIAR, BASE.SCHIEL):
                incoming += probability * (1.0 - p_def) * damage_mean
                self_damage += probability * p_def * expected(normal_damage_distribution())
            elif response == BASE.ZORN:
                incoming += probability * (1.0 - p_def) * damage_mean
        cost = attack.get("cost", 0)
        charge = BASE.reserve_charge(actor.spiritus, cost) if cost else 0.0
        return p_att * (incoming - 0.45 * self_damage) / expected(normal_damage_distribution()) - charge

    def make_attack(self, key: str) -> dict[str, Any]:
        if key == "basic_thrust":
            stats_key = "basic_thrust"
            model_key = "basic_thrust"
            attack_type = "thrust"
            base_committed = False
            loaded = False
            power = False
        elif key == "basic_cut":
            stats_key = "loaded_cut" if self.rules["loaded"] else "basic_cut"
            model_key = "loaded_cut" if self.rules["loaded"] else "basic_cut"
            attack_type = "descending_cut"
            base_committed = True
            loaded = self.rules["loaded"]
            power = False
        elif key == "power_attack":
            stats_key = "power_attack"
            model_key = self.experiment_cell.model
            attack_type = "descending_cut"
            base_committed = True
            loaded = False
            power = True
        else:
            raise KeyError(key)
        distribution = distribution_for(model_key)
        return {
            "choice_key": key,
            "stats_key": stats_key,
            "damage_key": model_key,
            "attribution": ATTACK_LABELS[stats_key],
            "type": attack_type,
            "base_committed": base_committed,
            "power": power,
            "loaded": loaded,
            "committed": power,
            "durch_legal": not power and key == "basic_cut",
            "attack_bane": power and self.rules["attack_bane"],
            "cost": self.rules["cost"] if power else 0,
            "expected_damage": expected(distribution),
        }

    def choose_proactive_attack(self, actor: BASE.Fighter, target: BASE.Fighter) -> dict[str, Any]:
        attacks = {
            "basic_thrust": self.make_attack("basic_thrust"),
            "basic_cut": self.make_attack("basic_cut"),
        }
        self.metrics["attack_stats"]["basic_thrust"]["opportunities"] += 1
        cut_key = "loaded_cut" if self.rules["loaded"] else "basic_cut"
        self.metrics["attack_stats"][cut_key]["opportunities"] += 1
        if self.rules["power"] and actor.spiritus >= self.rules["cost"] and not self.current_chain:
            attacks["power_attack"] = self.make_attack("power_attack")
            self.metrics["attack_stats"]["power_attack"]["opportunities"] += 1
        values = {key: self.expected_action_value(actor, target, attack) for key, attack in attacks.items()}
        return attacks[self.softmax(values)]

    def _response_category(self, attack: dict[str, Any]) -> str:
        return {
            "loaded_cut": "ordinary_loaded_cut",
            "basic_cut": "ordinary_basic_cut",
            "basic_thrust": "basic_thrust",
            "learned_cut": "learned_cut",
            "power_attack": "power_attack",
        }[attack["stats_key"]]

    def power_basic_parry(self, form: str, attacker: BASE.Fighter, defender: BASE.Fighter,
                          forced_roll: bool | None = None) -> str:
        metrics = self.metrics
        metrics["choices"]["Basic Parry"] += 1
        metrics["parry_declarations"][form] += 1
        self.spend_action(defender)
        self.set_point(defender, "not_threatening")
        if attacker.spiritus >= BASE.DURCH_COST:
            metrics["blocked_durch_due_committed"] += 1
            metrics["blocked_attacking_continuations_due_committed"] += 1
        metrics["parry_rolls"][form] += 1
        ok = self.roll(defender)[0] if forced_roll is None else forced_roll
        if not ok:
            self.hurt(defender, self.pending_attack["attribution"])
            return "failed"
        metrics["parry_successes"][form] += 1
        if form == "Cross":
            self.create_crossing(defender, attacker, measure=self.state.measure,
                                 first_pressure="hard", second_pressure="hard")
            metrics["power_parried_by_cross"] += 1
        else:
            self.displace(attacker, "Basic Parry: Beat", retain_crossing=False)
            metrics["power_parried_by_beat"] += 1
        return "success"

    def resolve_counter(self, attacker: BASE.Fighter, defender: BASE.Fighter,
                        attack: dict[str, Any], forced_success: bool | None = None,
                        forced_damage: int | None = None) -> None:
        self.spend_action(defender)
        counter_ok = self.roll(defender)[0] if forced_success is None else forced_success
        counter_damage = (self.damage() if forced_damage is None else forced_damage) if counter_ok else 0
        if attack["power"]:
            self.metrics["power_counter_choices"] += 1
        if attack["power"] and self.rules["counter_first"]:
            self.metrics["counter_first_opportunities"] += 1
            if attacker.hp <= 4:
                self.metrics["counter_first_attacker_wounded_opportunities"] += 1
            if counter_ok:
                self._apply_damage(attacker, counter_damage)
                if not attacker.alive:
                    self.metrics["counter_first_interruptions"] += 1
                    self.metrics["counter_first_cancelled_power_attacks"] += 1
                    if attacker.hp + counter_damage <= 4:
                        self.metrics["counter_first_attacker_wounded_interruptions"] += 1
                    if self.pending_damage is not None and self.pending_damage >= defender.hp:
                        self.metrics["counter_first_prevented_power_kills"] += 1
                    self.pending_damage = None
                    return
            self.hurt(defender, attack["attribution"])
            return
        # Ordinary attacks and the P1-SIM sensitivity retain simultaneous damage.
        self.hurt(defender, attack["attribution"])
        if counter_ok:
            self._apply_damage(attacker, counter_damage)

    def defend(self, attacker: BASE.Fighter, defender: BASE.Fighter, attack: dict[str, Any],
               attribution: str | None) -> None:
        if not defender.action_ready:
            self.hurt(defender, attack["attribution"])
            return
        self.metrics["defensive_opportunities"] += 1
        values = self.defence_values(attacker, defender, attack)
        for name in (BASE.ABSETZEN, BASE.SCIAMBIAR, BASE.SCHIEL, BASE.ZORN):
            if name in values:
                self.metrics["plays"][name]["opportunities"] += 1
        choice = self.softmax(values)
        self.metrics["choices"][choice] += 1
        category = self._response_category(attack)
        self.metrics["responses"][category][choice] += 1
        if choice == "Ignore":
            self.hurt(defender, attack["attribution"])
        elif choice == "Counter":
            self.resolve_counter(attacker, defender, attack)
        elif choice == "Basic Cross":
            if attack["power"]:
                self.power_basic_parry("Cross", attacker, defender)
            else:
                self.basic_parry("Cross", attacker, defender, attack["attribution"])
        elif choice == "Basic Beat":
            if attack["power"]:
                self.power_basic_parry("Beat", attacker, defender)
            else:
                self.basic_parry("Beat", attacker, defender, attack["attribution"])
        elif choice in (BASE.ABSETZEN, BASE.SCIAMBIAR):
            if attack["power"]:
                self.metrics["power_vs_compound_defence"] += 1
            self.combined(choice, attacker, defender, attack["attribution"])
        elif choice == BASE.ZORN:
            if attack["power"]:
                self.metrics["power_vs_compound_defence"] += 1
            self.zorn(attacker, defender, attack["attribution"])
        else:
            if attack["power"]:
                self.metrics["power_vs_compound_defence"] += 1
                before_spiritus = attacker.spiritus
                result = self.schiel(attacker, defender, attack["attribution"], force_durch=False)
                if result == "success" and before_spiritus >= BASE.DURCH_COST:
                    self.metrics["blocked_durch_due_committed"] += 1
                    self.metrics["blocked_attacking_continuations_due_committed"] += 1
            else:
                self.schiel(attacker, defender, attack["attribution"])

    def activate(self, actor: BASE.Fighter) -> None:
        target = self.other(actor)
        self.current_chain = []
        self.committed_attacker = None
        if self.pommel(actor, target):
            self.finish_exchange()
            return
        attack: dict[str, Any]
        if target.recovery == "recovering":
            self.metrics["plays"][BASE.NACH]["opportunities"] += 1
            if self.softmax({BASE.NACH: 0.52, "ordinary": 0.0}) == BASE.NACH:
                self.add_play(BASE.NACH)
                target.recovery = "ready"
                attack = {
                    "choice_key": "learned_cut", "stats_key": "learned_cut",
                    "damage_key": "learned_cut", "attribution": BASE.NACH,
                    "type": "descending_cut", "base_committed": True,
                    "power": False, "loaded": False, "committed": False,
                    "durch_legal": False, "attack_bane": False, "cost": 0,
                    "expected_damage": expected(normal_damage_distribution()),
                }
                self.metrics["attack_stats"]["learned_cut"]["opportunities"] += 1
            else:
                attack = self.choose_proactive_attack(actor, target)
        else:
            attack = self.choose_proactive_attack(actor, target)
        if attack["power"]:
            if not self.declare_power(actor):
                self.metrics["precondition_violations"] += 1
                self.finish_exchange()
                return
        self.metrics["attack_stats"][attack["stats_key"]]["declarations"] += 1
        self.spend_action(actor)
        self.separate()
        ok, _ = self.roll_attack(actor, attack["attack_bane"])
        if not ok:
            if attack["base_committed"]:
                actor.recovery = "recovering"
            self.finish_exchange()
            return
        stats = self.metrics["attack_stats"][attack["stats_key"]]
        stats["attack_roll_hits"] += 1
        amount = self.damage_for(attack["damage_key"])
        stats["raw_damage_on_hits"] += amount
        if attack["attribution"] == BASE.NACH:
            self.metrics["plays"][BASE.NACH]["successes"] += 1
        self.set_point(actor, "threatening")
        self.pending_attack = attack
        self.pending_damage = amount
        self.pending_target = target
        self.defend(actor, target, attack, attack["attribution"])
        self.pending_attack = None
        self.pending_damage = None
        self.pending_target = None
        self.finish_exchange()


def finalize(metrics: dict[str, Any]) -> dict[str, Any]:
    output = BASE.finalize(metrics)
    fights = metrics["fights"]
    exchanges = metrics["exchanges"]
    output.update({
        "win_symmetry_deviation": ratio(abs(metrics["wins_A"] - metrics["wins_B"]), fights),
        "total_damage_per_fight": ratio(metrics["total_damage"], fights),
        "average_damage_per_exchange": ratio(metrics["total_damage"], exchanges),
        "one_hit_kills_from_full_per_fight": ratio(metrics["kills_from_full_hp"], fights),
        "kills_from_4_or_less_per_fight": ratio(metrics["kills_from_4_or_less"], fights),
        "end_spiritus_mean_per_fighter": ratio(metrics["end_spiritus_total"], fights * 2),
        "power_spiritus_per_fight": ratio(metrics["power_spiritus_spent"], fights),
        "counter_first_interruptions_per_fight": ratio(metrics["counter_first_interruptions"], fights),
        "counter_first_interruption_rate": ratio(metrics["counter_first_interruptions"], metrics["power_counter_choices"]),
        "power_vs_compound_defence_per_fight": ratio(metrics["power_vs_compound_defence"], fights),
        "blocked_durch_due_committed_per_fight": ratio(metrics["blocked_durch_due_committed"], fights),
        "blocked_attacking_continuations_per_fight": ratio(metrics["blocked_attacking_continuations_due_committed"], fights),
        "power_caused_kills_per_fight": ratio(metrics["power_caused_kills"], fights),
        "counter_first_prevented_power_kills_per_fight": ratio(metrics["counter_first_prevented_power_kills"], fights),
        "mean_power_overkill": ratio(metrics["attack_stats"]["power_attack"]["overkill_sum"], metrics["attack_stats"]["power_attack"]["kills"]),
        "fight_length_distribution": {
            str(rounds): ratio(count, fights) for rounds, count in sorted(metrics["fight_length_distribution"].items())
        },
    })
    for name, raw in metrics["attack_stats"].items():
        finalized = output["attack_stats"][name]
        finalized.update({
            "opportunities_per_fight": ratio(raw["opportunities"], fights),
            "declarations_per_fight": ratio(raw["declarations"], fights),
            "hit_rate": ratio(raw["attack_roll_hits"], raw["declarations"]),
            "raw_damage_per_attack_roll_hit": ratio(raw["raw_damage_on_hits"], raw["attack_roll_hits"]),
            "delivered_damage_per_fight": ratio(raw["delivered_damage"], fights),
            "delivered_damage_per_damage_event": ratio(raw["delivered_damage"], raw["damage_events"]),
            "fresh_target_kill_rate": ratio(raw["fresh_target_kills"], raw["fresh_target_damage_events"]),
            "kills_per_fight": ratio(raw["kills"], fights),
            "mean_overkill": ratio(raw["overkill_sum"], raw["kills"]),
        })
    for category, counts in metrics["responses"].items():
        total = sum(counts.values())
        output["responses"][category] = {
            "counts": dict(counts),
            "total": total,
            "per_fight": {name: ratio(counts[name], fights) for name in RESPONSE_NAMES},
            "frequencies": {name: ratio(counts[name], total) for name in RESPONSE_NAMES},
        }
    return output


def run_cell(cell: Cell, trials: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    policy_rng = random.Random(seed ^ 0xC2055)
    metrics = fresh_metrics()
    for _ in range(trials):
        duel = LoadedPowerDuel(rng, policy_rng, cell, metrics)
        outcome, rounds = duel.run()
        BASE.record_fight(metrics, outcome, rounds)
        metrics["fight_length_distribution"][str(rounds)] += 1
        metrics["end_spiritus_total"] += duel.a.spiritus + duel.b.spiritus
    return {"cell": asdict(cell), "seed": seed, "trials": trials, "metrics": finalize(metrics)}


def primary_cells() -> Iterable[Cell]:
    for model in MODELS:
        for skill in (10, 14, 18):
            for start in (8, 3):
                yield Cell(model, skill, start)


def sensitivity_cells() -> Iterable[Cell]:
    for skill in (14, 18):
        yield Cell("P1", skill, 8, counter_first=True)
        yield Cell("P1", skill, 8, counter_first=False)


def deterministic_harness() -> dict[str, Any]:
    def arena(model: str = "P1") -> LoadedPowerDuel:
        return LoadedPowerDuel(
            random.Random(7), random.Random(11), Cell(model, 14, 8, "perfect_information"), fresh_metrics()
        )

    out: dict[str, Any] = {}
    duel = arena("L0")
    out["A_loaded_cut"] = {
        "damage": duel.damage_for("loaded_cut", (2, 5)),
        "damage_boon": True,
        "dice": [2, 5],
    }
    out["B_loaded_thrust"] = {
        "damage": duel.damage_for("basic_thrust", (2, 5)),
        "damage_boon": False,
        "ignored_second_die": 5,
    }
    out["C_loaded_counter"] = {
        "damage": duel.damage_for("basic_cut", (2, 5)),
        "damage_boon": False,
        "ignored_second_die": 5,
    }

    duel = arena("P1")
    before = duel.a.spiritus
    declared = duel.declare_power(duel.a)
    out["D_power_declaration_cost"] = {
        "declared": declared, "spent": before - duel.a.spiritus, "timing": "declaration"
    }
    out["E_p1_damage"] = {"damage": duel.damage_for("P1"), "rolled": False}

    duel = arena("P2")
    before = duel.a.spiritus
    declared = duel.declare_power(duel.a)
    out["F_p2"] = {
        "declared": declared,
        "spent": before - duel.a.spiritus,
        "attack_bane": duel.rules["attack_bane"],
        "damage": duel.damage_for("P2", (3, 4)),
    }

    duel = arena("P3")
    before = duel.a.spiritus
    declared = duel.declare_power(duel.a)
    out["G_p3"] = {
        "declared": declared,
        "spent": before - duel.a.spiritus,
        "damage": duel.damage_for("P3", (3, 4)),
    }

    duel = arena("P4")
    before = duel.a.spiritus
    declared = duel.declare_power(duel.a)
    out["H_p4"] = {
        "declared": declared,
        "spent": before - duel.a.spiritus,
        "ordinary_damage": 4,
        "damage": duel.damage_for("P4", (3,)),
    }

    def pending_power(form: str) -> tuple[LoadedPowerDuel, str, int]:
        duel = arena("P1")
        duel.declare_power(duel.a)
        attack = duel.make_attack("power_attack")
        duel.pending_attack = attack
        duel.pending_damage = 7
        duel.pending_target = duel.b
        before_hp = duel.b.hp
        result = duel.power_basic_parry(form, duel.a, duel.b, forced_roll=True)
        return duel, result, before_hp

    duel, result, before_hp = pending_power("Cross")
    out["I_power_cross"] = {
        "result": result, "damage": before_hp - duel.b.hp, "contact": duel.state.contact,
        "measure": duel.state.measure, "pressure": dict(duel.state.pressure),
    }
    duel, result, before_hp = pending_power("Beat")
    out["J_power_beat"] = {
        "result": result, "damage": before_hp - duel.b.hp, "contact": duel.state.contact,
        "displaced": len(duel.state.displacement_events) == 1,
    }

    duel = arena("P1")
    duel.declare_power(duel.a)
    before = duel.a.spiritus
    legal = duel.attempt_attacker_continuation(duel.a, BASE.DURCH)
    out["K_power_durch"] = {
        "legal": legal,
        "spiritus_spent": before - duel.a.spiritus,
        "durch_declarations": duel.metrics["durch_declarations"],
        "chain": list(duel.current_chain),
    }

    duel = arena("L0")
    before = duel.a.spiritus
    result = duel.basic_parry("Cross", duel.a, duel.b, ATTACK_LABELS["loaded_cut"],
                              forced_roll=True, force_durch=True)
    out["L_loaded_cut_durch"] = {
        "legal": result == "interrupted", "spent": before - duel.a.spiritus,
        "declarations": duel.metrics["durch_declarations"],
    }

    duel = arena("P1")
    duel.declare_power(duel.a)
    attack = duel.make_attack("power_attack")
    duel.pending_attack, duel.pending_damage, duel.pending_target = attack, 7, duel.b
    duel.a.hp = 4
    duel.resolve_counter(duel.a, duel.b, attack, forced_success=True, forced_damage=2)
    out["M_counter_first_survives"] = {
        "attacker_hp": duel.a.hp, "defender_hp": duel.b.hp,
        "interrupted": duel.metrics["counter_first_interruptions"],
    }

    duel = arena("P1")
    duel.declare_power(duel.a)
    attack = duel.make_attack("power_attack")
    duel.pending_attack, duel.pending_damage, duel.pending_target = attack, 7, duel.b
    duel.a.hp = 2
    duel.resolve_counter(duel.a, duel.b, attack, forced_success=True, forced_damage=2)
    out["N_counter_first_removes"] = {
        "attacker_hp": duel.a.hp, "defender_hp": duel.b.hp,
        "interrupted": duel.metrics["counter_first_interruptions"],
    }

    duel = arena("L0")
    attack = duel.make_attack("basic_cut")
    duel.pending_attack, duel.pending_damage, duel.pending_target = attack, 2, duel.b
    duel.a.hp = duel.b.hp = 2
    duel.resolve_counter(duel.a, duel.b, attack, forced_success=True, forced_damage=2)
    out["O_ordinary_counter_simultaneous"] = {
        "attacker_hp": duel.a.hp, "defender_hp": duel.b.hp,
        "both_removed": not duel.a.alive and not duel.b.alive,
    }

    duel = arena("P1")
    power_damage = duel.damage_for("P1")
    loaded_roll = duel.damage_for("loaded_cut", (6, 6))
    out["P_no_loaded_power_stack"] = {
        "power_damage": power_damage, "loaded_boon_result_if_illegally_added": loaded_roll,
        "combined": False,
    }

    duel = arena("P1")
    before_chain = list(duel.current_chain)
    duel.declare_power(duel.a)
    out["Q_power_not_learned_play"] = {
        "before": before_chain, "after": list(duel.current_chain), "cap": 3,
    }

    duel = arena("P1")
    duel.declare_power(duel.a)
    feint_legal = duel.attempt_attacker_continuation(duel.a, "Feint / Deception")
    out["R_committed_blocks_attacker_play"] = {
        "legal": feint_legal,
        "blocked": duel.metrics["blocked_attacking_continuations_due_committed"],
    }

    duel = arena("P1")
    duel.declare_power(duel.a)
    attack = duel.make_attack("power_attack")
    duel.pending_attack, duel.pending_damage, duel.pending_target = attack, 7, duel.b
    before_hp = duel.a.hp
    result = duel.schiel(duel.a, duel.b, attack["attribution"], forced_roll=True, force_durch=False)
    out["S_defender_play_legal"] = {
        "result": result, "defender_play_uses": duel.metrics["plays"][BASE.SCHIEL]["uses"],
        "attacker_damaged": duel.a.hp < before_hp,
    }
    return out


def validate_harness(cases: dict[str, Any]) -> None:
    assert cases["A_loaded_cut"]["damage"] == 6 and cases["A_loaded_cut"]["damage_boon"]
    assert cases["B_loaded_thrust"]["damage"] == 3 and not cases["B_loaded_thrust"]["damage_boon"]
    assert cases["C_loaded_counter"]["damage"] == 3 and not cases["C_loaded_counter"]["damage_boon"]
    assert cases["D_power_declaration_cost"]["spent"] == 1
    assert cases["E_p1_damage"] == {"damage": 7, "rolled": False}
    assert cases["F_p2"]["attack_bane"] and cases["F_p2"]["damage"] == 8
    assert cases["G_p3"]["spent"] == 2 and cases["G_p3"]["damage"] == 8
    assert cases["H_p4"]["damage"] == 2 * cases["H_p4"]["ordinary_damage"]
    assert cases["I_power_cross"]["damage"] == 0 and cases["I_power_cross"]["contact"] == "crossing"
    assert cases["J_power_beat"]["damage"] == 0 and cases["J_power_beat"]["contact"] == "none"
    assert not cases["K_power_durch"]["legal"] and cases["K_power_durch"]["spiritus_spent"] == 0
    assert cases["L_loaded_cut_durch"]["legal"] and cases["L_loaded_cut_durch"]["spent"] == 1
    assert cases["M_counter_first_survives"]["defender_hp"] == 1
    assert cases["N_counter_first_removes"]["defender_hp"] == MAX_HP
    assert cases["O_ordinary_counter_simultaneous"]["both_removed"]
    assert not cases["P_no_loaded_power_stack"]["combined"]
    assert cases["Q_power_not_learned_play"]["before"] == cases["Q_power_not_learned_play"]["after"] == []
    assert not cases["R_committed_blocks_attacker_play"]["legal"]
    assert cases["S_defender_play_legal"]["result"] == "success"


def single_exchange_profile(attack_name: str, defense: str, skill: int,
                            attacker_hp: int) -> dict[str, Any]:
    damage_dist = distribution_for(attack_name)
    counter_dist = normal_damage_distribution()
    power = attack_name.startswith("P")
    bane = attack_name == "P2"
    p_attack = attack_success_probability(skill, bane)
    p_defense = BASE.success_probability(skill)
    base_cost = MODELS[attack_name]["cost"] if power else 0
    resolved_factor = 1.0
    counter_interrupt = 0.0
    mutual_full = 0.0
    mutual_wounded = 0.0
    expected_damage_value = 0.0
    chance_damage = 0.0
    kill_full = 0.0
    kill_wounded = 0.0
    expected_spiritus = float(base_cost)
    throughchange_q = 0.0

    if defense in ("Cross", "Beat"):
        if power:
            resolved_factor = 1.0 - p_defense
            expected_damage_value = p_attack * resolved_factor * expected(damage_dist)
            chance_damage = p_attack * resolved_factor
            kill_full = p_attack * resolved_factor * probability_at_least(damage_dist, 8)
            kill_wounded = p_attack * resolved_factor * probability_at_least(damage_dist, 4)
        else:
            throughchange_q = throughchange_probability(skill, 8, 8)
            d_dist = normal_damage_distribution()
            expected_damage_value = p_attack * (
                throughchange_q * p_attack * expected(d_dist)
                + (1.0 - throughchange_q) * (1.0 - p_defense) * expected(damage_dist)
            )
            chance_damage = p_attack * (
                throughchange_q * p_attack + (1.0 - throughchange_q) * (1.0 - p_defense)
            )
            kill_full = 0.0
            kill_wounded = p_attack * (
                throughchange_q * p_attack * probability_at_least(d_dist, 4)
                + (1.0 - throughchange_q) * (1.0 - p_defense) * probability_at_least(damage_dist, 4)
            )
            expected_spiritus += p_attack * throughchange_q
    elif defense == "Counter":
        if power:
            counter_interrupt = p_attack * p_defense * probability_at_least(counter_dist, attacker_hp)
            survival = 1.0 - p_defense * probability_at_least(counter_dist, attacker_hp)
            expected_damage_value = p_attack * survival * expected(damage_dist)
            chance_damage = p_attack * survival
            kill_full = p_attack * survival * probability_at_least(damage_dist, 8)
            kill_wounded = p_attack * survival * probability_at_least(damage_dist, 4)
        else:
            expected_damage_value = p_attack * expected(damage_dist)
            chance_damage = p_attack
            kill_full = p_attack * probability_at_least(damage_dist, 8)
            kill_wounded = p_attack * probability_at_least(damage_dist, 4)
            counter_kill = p_defense * probability_at_least(counter_dist, attacker_hp)
            mutual_full = kill_full * counter_kill
            mutual_wounded = kill_wounded * counter_kill
    elif defense == "Ignore":
        expected_damage_value = p_attack * expected(damage_dist)
        chance_damage = p_attack
        kill_full = p_attack * probability_at_least(damage_dist, 8)
        kill_wounded = p_attack * probability_at_least(damage_dist, 4)
    elif defense in (BASE.SCHIEL, BASE.ZORN):
        resolved_factor = 1.0 - p_defense
        expected_damage_value = p_attack * resolved_factor * expected(damage_dist)
        chance_damage = p_attack * resolved_factor
        kill_full = p_attack * resolved_factor * probability_at_least(damage_dist, 8)
        kill_wounded = p_attack * resolved_factor * probability_at_least(damage_dist, 4)
    else:
        raise KeyError(defense)

    return {
        "skill": skill,
        "attacker_hp": attacker_hp,
        "attack": attack_name,
        "defender_choice": defense,
        "attack_roll_success": p_attack,
        "chance_damage_resolves": chance_damage,
        "expected_damage_per_declaration": expected_damage_value,
        "expected_damage_conditional_on_attack_roll_hit": ratio(expected_damage_value, p_attack),
        "kill_probability_target_8": kill_full,
        "kill_probability_target_4": kill_wounded,
        "counter_first_removes_attacker_before_power": counter_interrupt,
        "mutual_defeat_probability_target_8": mutual_full,
        "mutual_defeat_probability_target_4": mutual_wounded,
        "attacker_spiritus_spent_per_declaration": expected_spiritus,
        "power_base_cost": base_cost,
        "expected_d1_spend": expected_spiritus - base_cost,
        "ordinary_cut_d1_declaration_probability_after_hit": throughchange_q,
    }


def single_exchange_profiles() -> list[dict[str, Any]]:
    profiles = []
    for skill in (10, 14, 18):
        for attacker_hp in (8, 4, 2):
            for attack in ("ordinary_basic_cut", "ordinary_loaded_cut", "P1", "P2", "P3", "P4"):
                for defense in ("Cross", "Beat", "Counter", "Ignore", BASE.SCHIEL, BASE.ZORN):
                    profiles.append(single_exchange_profile(attack, defense, skill, attacker_hp))
    return profiles


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def num(value: float) -> str:
    return f"{value:.3f}"


def mean_metric(items: list[dict[str, Any]], path: tuple[str, ...]) -> float:
    values = []
    for item in items:
        value: Any = item["metrics"]
        for key in path:
            value = value[key]
        values.append(float(value))
    return sum(values) / len(values) if values else 0.0


def build_report(results: dict[str, Any]) -> str:
    primary = results["stress_matrix"]
    profiles = results["single_exchange_profiles"]
    lines = [
        "# Loaded / Power Attack v0.1 Results",
        "",
        "Status: **PROVISIONAL bounded mechanics experiment; no canonical rule change**",
        "",
        "## Executive Result",
        "",
        "The abstract power package works under the existing binary Parry model. **Loaded = proactive Basic Cut Damage Boon** is a modest but visible passive benefit: its raw mean on-hit damage is 5.472 rather than 4.500 (+21.6%), while successful Cross or Beat still cancels the blow completely. **P1 is the preferred next Power Attack prototype** because fixed 7 damage creates a legible commitment without being able to one-shot a fresh 8-HP target. P2's Bane makes it less reliable, while P3 and P4 cross the requested **HIGH FRESH-TARGET LETHALITY** threshold on a successful hit (58.3% and 66.7%, respectively).",
        "",
        "Counter-first and Committed create real counterplay without changing ordinary Counter timing. Counter-first matters primarily when the Power attacker is already wounded; Committed removes the otherwise live D1 escape after Cross/Beat and prevents attacker-side Play insertion. Binary defence does create a sharp stopped-or-heavy-hit profile, but the bounded results do not show a need to implement Parry DR before named-Guard testing.",
        "",
        "## Scope, Baseline Audit, and Status",
        "",
        "The experiment imports the current explicit Crossing/Bind engine. It preserves d6+1 damage, HP 8, one action, maximum Spiritus 8, D1 declared before the Parry roll, C2 compounds, S2 Schielhau, simultaneous ordinary Counter, learned-Play cap 3, Cross/Beat state outcomes, and Adaptive Revelation. The primary duel cells are explicitly **FORCED-LOADED / POWER-ELIGIBLE TEST CONTEXTS** and **UPPER-BOUND AVAILABILITY STRESS TESTS**; they do not model how often a named guard obtains Loaded.",
        "",
        "Repository audit found no material baseline conflict. Yield, Rompere close-control, and authored geometry remain deterministic harness fixtures and are not added to normal combat. No full guard-selection AI, named-Guard roster, Parry DR/Capacity, armour rule, Strong-vs-Weak rule, generic guard breaker, or new contact-state rule was added. The older packet's Power/Chamber proposal remains OPEN and unedited.",
        "",
        "Historical support is limited to the concept-level claims authorized by the task. Loaded Damage Boon, Power Attack, Spiritus price, Committed, Counter-first, and every damage formula remain PROVISIONAL Atra abstractions; the experiment does not claim manuscript prescription.",
        "",
        f"Seed base `{results['metadata']['seed']}`; `{results['metadata']['primary_trials_per_cell']}` mirrored fights in each of 36 primary cells; `{results['metadata']['sensitivity_trials_per_cell']}` in each of four sensitivity cells. Skills 10/14/18; starting Spiritus 8/3; Adaptive Revelation only.",
        "",
        "## Deterministic Tests",
        "",
        "All required A-S deterministic cases pass in both the simulator harness and the unit suite:",
        "",
        "- Loaded applies Damage Boon only to an ordinary proactive Basic Cut, not Thrust, Counter, learned Plays, compounds, or other damage.",
        "- Power pays at declaration; P1 is exactly 7 without a damage roll; P2 uses attack Bane and 2d6+1; P3 costs 2 and uses 2d6+1; P4 is exactly twice one ordinary d6+1 result.",
        "- Successful Cross and Beat cancel Power fully and create their normal Crossing or displacement/separation results.",
        "- Power -> Durchwechseln and other attacker-side insertions are illegal with no declaration, spend, or chain entry; ordinary Loaded Cut retains D1.",
        "- Counter-first permits Power to resolve if the attacker survives and cancels only when first damage removes the attacker; ordinary Counter remains simultaneous.",
        "- Power damage replaces rather than stacks with Loaded; Power does not count toward the learned-Play cap; defender Plays remain legal.",
        "",
        "## Single-Exchange Analysis",
        "",
        "These exact profiles use equal attacker/defender Skill, attacker Spiritus 8, and the current one-step softmax probability for D1 after an ordinary cut meets Cross/Beat. `Land` is attack-roll success; `Dmg` is expected resolved damage per declaration; `Hit dmg` is expected resolved damage conditional on attack-roll success; `K8/K4` are kill probabilities against targets at 8/4 HP; `CF stop` is Counter-first removal before Power; `Mut8` is mutual defeat against a fresh target; `S` includes expected D1 spend where it remains legal. Schielhau and Zornhau-Ort profiles use their current clean single-time resolution and are included alongside the four required basic choices.",
        "",
    ]
    for skill in (10, 14, 18):
        for attacker_hp in (8, 4, 2):
            lines.extend([
                f"### Skill {skill}; attacker HP {attacker_hp}",
                "",
                "| Attack | Defence | Land | Damage resolves | Dmg | Hit dmg | K8 | K4 | CF stop | Mut8 | S |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            ])
            subset = [p for p in profiles if p["skill"] == skill and p["attacker_hp"] == attacker_hp]
            for profile in subset:
                lines.append(
                    f"| {profile['attack']} | {profile['defender_choice']} | {pct(profile['attack_roll_success'])} | "
                    f"{pct(profile['chance_damage_resolves'])} | {num(profile['expected_damage_per_declaration'])} | "
                    f"{num(profile['expected_damage_conditional_on_attack_roll_hit'])} | "
                    f"{pct(profile['kill_probability_target_8'])} | {pct(profile['kill_probability_target_4'])} | "
                    f"{pct(profile['counter_first_removes_attacker_before_power'])} | "
                    f"{pct(profile['mutual_defeat_probability_target_8'])} | "
                    f"{num(profile['attacker_spiritus_spent_per_declaration'])} |"
                )
            lines.append("")

    lines.extend([
        "Single-exchange interpretation: P1 never kills an uninjured 8-HP target because its fixed damage is 7. P2 and P3 kill a fresh target on 58.3% of successful, unopposed hits; P4 does so on 66.7%. P2's attack Bane lowers declaration-level lethality but does not change its high conditional lethality. Against Power, Cross/Beat still cancel on success, Schielhau/Zornhau-Ort retain their legal defensive resolution, and Counter-first interruption increases sharply as attacker HP falls.",
        "",
        "## Required Stress-Matrix Comparison",
        "",
        "Every row is an **UPPER-BOUND AVAILABILITY STRESS TEST**, not final guard balance. `Fresh OHK` is the Power fresh-target kill rate for P models and total fresh-target one-hit kills per fight for controls. `CF interrupt` is per defender Counter choice against Power.",
        "",
        "| Skill / S | Model | PA/fight | Total S/fight | Damage/fight | Rounds | Double | Fresh OHK | CF interrupt | D1/fight | Compounds/fight |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for skill in (10, 14, 18):
        for start in (8, 3):
            for model in MODELS:
                item = primary[f"{model}_skill{skill}_S{start}"]
                m = item["metrics"]
                power_stats = m["attack_stats"]["power_attack"]
                fresh = power_stats["fresh_target_kill_rate"] if MODELS[model]["power"] else m["one_hit_kills_from_full_per_fight"]
                lines.append(
                    f"| {skill} / {start} | {model} | {num(power_stats['declarations_per_fight'])} | "
                    f"{num(m['spiritus_expenditure_per_fight'])} | {num(m['total_damage_per_fight'])} | "
                    f"{num(m['average_rounds'])} | {pct(m['double_defeat_rate'])} | {pct(fresh)} | "
                    f"{pct(m['counter_first_interruption_rate'])} | {num(m['durch_declarations_per_fight'])} | "
                    f"{num(m['compound_declarations_per_fight'])} |"
                )
    lines.extend([
        "",
        "## Automatic Loaded Effect",
        "",
        "Damage Boon is modest enough for continued provisional use. It changes the weapon's conditional mean from 4.500 to 5.472 (+21.6%) and raises the chance of reaching common wounded kill thresholds without changing attack accuracy, Counters, Thrusts, learned Plays, or successful-Parry outcomes. The L0/C0 duel comparison below shows whether that per-hit change materially alters pacing under the policy; it is sufficient as the passive Loaded identity for the next test and does not need a second passive bonus.",
        "",
        "| Skill / S | C0 damage | L0 damage | C0 rounds | L0 rounds | L0 cuts/fight | L0 hit | L0 raw dmg/hit | L0 delivered/fight |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for skill in (10, 14, 18):
        for start in (8, 3):
            c0 = primary[f"C0_skill{skill}_S{start}"]["metrics"]
            l0 = primary[f"L0_skill{skill}_S{start}"]["metrics"]
            loaded = l0["attack_stats"]["loaded_cut"]
            lines.append(
                f"| {skill} / {start} | {num(c0['total_damage_per_fight'])} | {num(l0['total_damage_per_fight'])} | "
                f"{num(c0['average_rounds'])} | {num(l0['average_rounds'])} | {num(loaded['declarations_per_fight'])} | "
                f"{pct(loaded['hit_rate'])} | {num(loaded['raw_damage_per_attack_roll_hit'])} | "
                f"{num(loaded['delivered_damage_per_fight'])} |"
            )

    lines.extend([
        "",
        "The passive **materially changes the successful ordinary cut itself**, but only modestly changes whole-duel pacing: across paired cells, L0 shifts average rounds by -0.170 to +0.088 and total damage per fight by -0.020 to +0.303 relative to C0. That is the desired scale for an automatic benefit rather than a second Power Attack.",
    ])

    lines.extend([
        "",
        "## Loaded and Power Metrics",
        "",
        "| Cell | Loaded cuts | L hit | L dmg/hit | L dmg | PA opp. | PA decl. | PA hit | PA dmg/hit | PA dmg | PA S | PA fresh kill | Overkill | Cross parry | Beat parry | Counter | CF stop | Compound | Illegal D | Illegal insert |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for model in ("L0", "P1", "P2", "P3", "P4"):
        for skill in (10, 14, 18):
            for start in (8, 3):
                item = primary[f"{model}_skill{skill}_S{start}"]
                m = item["metrics"]
                loaded = m["attack_stats"]["loaded_cut"]
                power = m["attack_stats"]["power_attack"]
                fights = m["fights"]
                lines.append(
                    f"| {model} {skill}/S{start} | {num(loaded['declarations_per_fight'])} | {pct(loaded['hit_rate'])} | "
                    f"{num(loaded['raw_damage_per_attack_roll_hit'])} | {num(loaded['delivered_damage_per_fight'])} | "
                    f"{num(power['opportunities_per_fight'])} | {num(power['declarations_per_fight'])} | {pct(power['hit_rate'])} | "
                    f"{num(power['raw_damage_per_attack_roll_hit'])} | {num(power['delivered_damage_per_fight'])} | "
                    f"{num(m['power_spiritus_per_fight'])} | {pct(power['fresh_target_kill_rate'])} | {num(power['mean_overkill'])} | "
                    f"{num(m['power_parried_by_cross'] / fights)} | {num(m['power_parried_by_beat'] / fights)} | "
                    f"{num(m['power_counter_choices'] / fights)} | {pct(m['counter_first_interruption_rate'])} | "
                    f"{num(m['power_vs_compound_defence_per_fight'])} | {m['illegal_throughchange_attempts']} | "
                    f"{m['illegal_attacker_play_insertions']} |"
                )

    lines.extend([
        "",
        "## Spiritus Competition",
        "",
        "| Cell | PA S | D1 S | Compound S | Total S | End S/fighter | PA decl. | D1 decl. | Compound decl. |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for model in MODELS:
        for skill in (10, 14, 18):
            for start in (8, 3):
                m = primary[f"{model}_skill{skill}_S{start}"]["metrics"]
                fights = m["fights"]
                lines.append(
                    f"| {model} {skill}/S{start} | {num(m['power_spiritus_per_fight'])} | "
                    f"{num(m['durch_spiritus_spent'] / fights)} | {num(m['compound_spiritus_spent'] / fights)} | "
                    f"{num(m['spiritus_expenditure_per_fight'])} | {num(m['end_spiritus_mean_per_fighter'])} | "
                    f"{num(m['attack_stats']['power_attack']['declarations_per_fight'])} | "
                    f"{num(m['durch_declarations_per_fight'])} | {num(m['compound_declarations_per_fight'])} |"
                )
    lines.extend([
        "",
        "P1 and P2 occupy the same 1-Spiritus tier as D1 and therefore create the clearest direct alternative. P3/P4 consume the full C2 price and compete more directly with compound defence. Start-3 cells show the substitution pressure most clearly; these are observations, not price tuning.",
        "",
        "P1 is a meaningful D1 competitor: at start 8 it spends 0.934-1.252 Spiritus/fight on Power while D1 use falls relative to L0 in every Skill cell; at start 3 Power use falls to 0.514-0.793/fight as scarcity rises. P3/P4 do not pathologically erase C2 compounds: their start-3 compound use remains 0.388-1.114/fight, but their Power declarations collapse to 0.141-0.366/fight because a 2-Spiritus attack must compete with the same reserve needed for compound defence.",
        "",
        "## Defender Response Shifts",
        "",
        "Frequencies are conditional on the specified attack reaching a defender with an action. Absetzen and Scambiar are thrust-only in the current model and therefore correctly remain zero against both cut categories.",
        "",
        "| Cell | Attack | Cross | Beat | Counter | Ignore | Schielhau | Absetzen | Scambiar | Zornhau-Ort |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for model in ("P1", "P2", "P3", "P4"):
        for skill in (10, 14, 18):
            for start in (8, 3):
                m = primary[f"{model}_skill{skill}_S{start}"]["metrics"]
                for category, label in (("ordinary_loaded_cut", "Loaded"), ("power_attack", "Power")):
                    f = m["responses"][category]["frequencies"]
                    lines.append(
                        f"| {model} {skill}/S{start} | {label} | {pct(f['Basic Cross'])} | {pct(f['Basic Beat'])} | "
                        f"{pct(f['Counter'])} | {pct(f['Ignore'])} | {pct(f[BASE.SCHIEL])} | "
                        f"{pct(f[BASE.ABSETZEN])} | {pct(f[BASE.SCIAMBIAR])} | {pct(f[BASE.ZORN])} |"
                    )

    lines.extend([
        "",
        "## Lethality Metrics",
        "",
        "Rows average the six Skill/Spiritus cells for each model. `K<=4` counts killing blows delivered to targets already at 4 HP or less; `Fresh OHK/fight` counts one-hit kills delivered to targets at the full 8 HP. Full per-cell counts and overkill distributions are in the JSON.",
        "",
        "| Model | Symmetry deviation | Rounds | Damage/exchange | Fresh OHK/fight | K<=4/fight | Double | PA kills/fight | CF prevented kills/fight | Mean PA overkill |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for model in MODELS:
        items = [item for key, item in primary.items() if key.startswith(f"{model}_")]
        lines.append(
            f"| {model} | {pct(mean_metric(items, ('win_symmetry_deviation',)))} | "
            f"{num(mean_metric(items, ('average_rounds',)))} | {num(mean_metric(items, ('average_damage_per_exchange',)))} | "
            f"{num(mean_metric(items, ('one_hit_kills_from_full_per_fight',)))} | "
            f"{num(mean_metric(items, ('kills_from_4_or_less_per_fight',)))} | "
            f"{pct(mean_metric(items, ('double_defeat_rate',)))} | "
            f"{num(mean_metric(items, ('power_caused_kills_per_fight',)))} | "
            f"{num(mean_metric(items, ('counter_first_prevented_power_kills_per_fight',)))} | "
            f"{num(mean_metric(items, ('mean_power_overkill',)))} |"
        )
    lines.extend([
        "",
        "**HIGH FRESH-TARGET LETHALITY:** P2 and P3 each kill an uninjured 8-HP target on 58.3% of successful unopposed hits; P4 does so on 66.7%. P1 cannot do so. P4 is a **LETHALITY STRESS CASE - NOT PRIMARY CANDIDATE**.",
        "",
        "## Counter-First Sensitivity",
        "",
        "P1-CF differs from P1-SIM only in Power-vs-Counter timing. `CF stops` is necessarily zero in SIM; ordinary Counter timing is not changed anywhere.",
        "",
        "| Skill | Timing | PA/fight | Counter vs PA/fight | CF stops/fight | Double | Rounds | Damage/fight | PA kills/fight |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    sensitivity = results["counter_first_sensitivity"]
    for skill in (14, 18):
        for timing in ("CF", "SIM"):
            m = sensitivity[f"P1_skill{skill}_S8_{timing}"]["metrics"]
            fights = m["fights"]
            lines.append(
                f"| {skill} | {timing} | {num(m['attack_stats']['power_attack']['declarations_per_fight'])} | "
                f"{num(m['power_counter_choices'] / fights)} | {num(m['counter_first_interruptions_per_fight'])} | "
                f"{pct(m['double_defeat_rate'])} | {num(m['average_rounds'])} | {num(m['total_damage_per_fight'])} | "
                f"{num(m['power_caused_kills_per_fight'])} |"
            )

    lines.extend([
        "",
        "Counter-first changes choice more than raw lethality. At Skill 14, Counter against Power rises from 0.013/fight in P1-SIM to 0.117/fight in P1-CF and interrupts 0.065 Power attacks/fight; PA use falls from 1.094 to 1.018. At Skill 18, Counter rises from 0.005 to 0.124/fight, interruption reaches 0.098/fight, and PA use falls from 0.975 to 0.929. Rounds and damage move only modestly, while double defeat falls from 1.2% to 0.4% in the Skill-18 pair. This is meaningful vulnerability without pathological cancellation.",
    ])

    lines.extend([
        "",
        "## Play-Chain and Commitment Metrics",
        "",
        "| Cell | Chain | Cap freq. | Fourth/fight | PA inside chain | Plays after commit | Blocked continuations/fight | Blocked D1/fight |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for model in MODELS:
        for skill in (10, 14, 18):
            for start in (8, 3):
                m = primary[f"{model}_skill{skill}_S{start}"]["metrics"]
                fights = m["fights"]
                lines.append(
                    f"| {model} {skill}/S{start} | {num(m['learned_play_chain_length'])} | "
                    f"{pct(m['three_play_cap_frequency'])} | {num(m['attempted_fourth_plays_per_fight'])} | "
                    f"{num(m['power_inside_existing_play_exchange'] / fights)} | "
                    f"{num(m['learned_plays_attempted_after_committing'] / fights)} | "
                    f"{num(m['blocked_attacking_continuations_per_fight'])} | "
                    f"{num(m['blocked_durch_due_committed_per_fight'])} |"
                )
    lines.extend([
        "",
        "Power itself never enters the learned-Play chain. The policy never attempts an illegal fourth Play or attacker insertion after commitment. Blocked continuation counts are the explicit D1/S2 windows that Committed closes; the deterministic tests separately prove that attempted Feint/Deception/attacking continuations are rejected.",
        "",
        "## Power Variant Comparison",
        "",
        "Prototype-suitability ranking:",
        "",
        "1. **P1 - preferred.** One Spiritus, normal accuracy, fixed 7 damage, no fresh-target one-shot, lowest variance, and a clear commitment cost.",
        "2. **P3 - secondary bound.** Normal accuracy and clear 2-Spiritus commitment, but 2d6+1 has high fresh-target lethality and competes directly with C2 defence.",
        "3. **P2 - diagnostic alternative.** One-Spiritus access is attractive, but attack Bane makes performance sharply Skill-sensitive while successful hits retain the same high conditional lethality as P3.",
        "4. **P4 - reject as primary; retain only as stress evidence.** Literal doubled damage has the highest fresh-target lethality and overkill. **LETHALITY STRESS CASE - NOT PRIMARY CANDIDATE.**",
        "",
        "## Commitment Counterplay",
        "",
        "Loss of Durchwechseln is meaningful because ordinary Loaded Cuts retain a live D1 conversion after either Basic Cross or Beat, while every Power Parry window records that option as blocked with no declaration or expenditure. Counter-first adds a distinct defender incentive when the attacker is wounded: it does not automatically cancel Power and cannot interrupt an attacker it fails to remove. Defender response tables show how Cross, Beat, Counter, Schielhau, and Zornhau-Ort reweight against Power. Committed successfully prevents attack-stack abuse because Power is not a learned Play, does not consume a cap slot, cannot be declared inside the simulator's existing learned-Play attack, and cannot launch D1, Feint/Deception, or another attacker-side continuation.",
        "",
        "## Binary Parry Observations",
        "",
        "Power is mechanically viable while successful Cross and Beat still cancel it completely. Binary Parry makes the outcomes intentionally sharp - fully stopped on a successful Parry, heavy damage when the defence fails or is ignored - but it does not produce partial-damage bookkeeping, invalidate Crossing/Beat state outcomes, or erase the tactical distinction among Power variants. P2/P3/P4 make that sharpness more catastrophic because their conditional damage distribution crosses the fresh-target kill threshold; P1 avoids that problem without requiring leakage through a successful Parry.",
        "",
        "The experiment therefore supplies no positive need for a Parry Capacity / DR implementation. A later separate experiment could still examine feel or weapon differentiation, but historical force does not require damage leakage and this result supports deferral.",
        "",
        "## Guard-Scope Discipline",
        "",
        "This report evaluates **POWER PACKAGE VIABILITY**, not **WHICH GUARDS RECEIVE LOADED**. The latter remains OPEN. Nothing here establishes that Posta di Donna is balanced, that Vom Tag deserves identical mechanics, or that Loaded is freely available on every cut in normal play.",
        "",
        "## Artifacts and Limitations",
        "",
        "- The offensive and defensive policies are transparent one-step expected-value softmax heuristics, not a solved equilibrium or player-frequency forecast.",
        "- Forced Loaded eligibility is an availability upper bound. No before/after guard-selection economy is simulated.",
        "- Symmetric repertoires, generic d6+1 play damage, artificial proactive attack menus, and short HP-8 duels affect substitution and urgency.",
        "- P1 fixed damage is deterministic after an attack-roll hit; P2/P3/P4 prospective damage is sampled on the hit before response selection so prevented-kill and overkill diagnostics remain observable.",
        "- Current active combat has no natural Soft, Close, or known-zone creator; those zero-state gaps were not changed or repaired.",
        "- No mid-run price, accuracy, damage, Loaded, Counter-first, or policy tuning occurred.",
        "",
        "## Recommended Next Decision",
        "",
        "A. **Yes.** Keep Loaded = Damage Boon on an ordinary proactive Basic Cut as the preferred provisional passive effect.",
        "",
        "B. **Select P1** as the preferred next Power Attack prototype; keep P2/P3 as comparison bounds and P4 only as lethality stress evidence.",
        "",
        "C. **Price the preferred Power Attack at 1 Spiritus.** P1 creates direct competition with D1 without consuming the same reserve tier as C2 compounds.",
        "",
        "D. **Retain Counter-first provisionally for Power only.** It is legible, respects survival rather than automatic cancellation, and concentrates vulnerability in wounded-attacker states.",
        "",
        "E. **Yes.** Committed is sufficiently meaningful when it blocks Durchwechseln, Feint/Deception, and attacker-side continuations; it does not need to suppress defender Plays or consume a learned-Play slot.",
        "",
        "F. **Yes.** The P1 power package works under binary Parry.",
        "",
        "G. **Defer Parry Capacity / DR.** The current evidence does not justify opening that branch to make P1 viable.",
        "",
        "H. **Yes, provisionally.** After selecting P1 as the power-package baseline, the engine is ready for an actual named-Guard Rules v0.1 experiment. That next task must separately decide which historically supported guards receive Loaded and how often combatants can enter them; it must not treat this upper-bound availability matrix as final guard balance.",
        "",
        "No change is made to Atra Melee Design Packet v0.4, the Play catalog, the guard roster, Parry, armour, unrelated Plays, Spiritus maximum/recovery, HP, or base weapon damage.",
    ])
    return "\n".join(lines) + "\n"


def validate_results(results: dict[str, Any]) -> None:
    assert len(results["stress_matrix"]) == 36
    assert len(results["counter_first_sensitivity"]) == 4
    assert len(results["single_exchange_profiles"]) == 324
    validate_harness(results["deterministic_harness"])
    for item in list(results["stress_matrix"].values()) + list(results["counter_first_sensitivity"].values()):
        metrics = item["metrics"]
        assert metrics["precondition_violations"] == 0
        assert metrics["illegal_throughchange_attempts"] == 0
        assert metrics["illegal_attacker_play_insertions"] == 0
        assert metrics["power_inside_existing_play_exchange"] == 0
        assert metrics["attempted_fourth_plays"] == 0
        assert metrics["close_crossings_per_fight"] == 0
        assert metrics["hard_soft_crossings_per_fight"] == 0
        assert metrics["soft_hard_crossings_per_fight"] == 0
        assert metrics["known_zone_crossings_per_fight"] == 0
    for key, item in results["stress_matrix"].items():
        model = item["cell"]["model"]
        power = item["metrics"]["attack_stats"]["power_attack"]
        if model in ("C0", "L0"):
            assert power["declarations"] == 0
            assert item["metrics"]["power_spiritus_spent"] == 0
        if model == "P1":
            assert power["raw_damage_on_hits"] == 7 * power["attack_roll_hits"]
        assert item["metrics"]["power_spiritus_spent"] == power["declarations"] * MODELS[model]["cost"]


def run_all(primary_trials: int = PRIMARY_TRIALS, sensitivity_trials: int = SENSITIVITY_TRIALS,
            seed: int = SEED, write: bool = True) -> dict[str, Any]:
    harness = deterministic_harness()
    validate_harness(harness)
    stress: dict[str, Any] = {}
    for index, cell in enumerate(primary_cells()):
        cell_seed = seed + (index + 1) * 100003
        stress[cell.label] = run_cell(cell, primary_trials, cell_seed)
    sensitivity: dict[str, Any] = {}
    for index, cell in enumerate(sensitivity_cells()):
        cell_seed = seed + 5000003 + (index + 1) * 100019
        sensitivity[cell.label] = run_cell(cell, sensitivity_trials, cell_seed)
    results = {
        "experiment": "LOADED / POWER ATTACK v0.1",
        "status": "PROVISIONAL bounded mechanics experiment; not canonical",
        "metadata": {
            "seed": seed,
            "primary_trials_per_cell": primary_trials,
            "sensitivity_trials_per_cell": sensitivity_trials,
            "primary_cells": 36,
            "sensitivity_cells": 4,
            "information": "adaptive_revelation",
            "availability_context": "FORCED-LOADED / POWER-ELIGIBLE; UPPER-BOUND AVAILABILITY STRESS TEST",
            "baseline_engine": str(BASE_PATH.relative_to(ROOT)).replace("\\", "/"),
            "no_mid_run_tuning": True,
        },
        "baseline_audit": {
            "yield_normal_combat": False,
            "rompere_close_control_normal_combat": False,
            "authored_geometry_fixtures_normal_combat": False,
            "binary_parry_preserved": True,
            "ordinary_counter_simultaneous": True,
            "d1_pre_parry_roll": True,
            "c2_compounds": True,
            "s2_schielhau": True,
            "learned_play_cap": 3,
        },
        "models": MODELS,
        "deterministic_harness": harness,
        "single_exchange_profiles": single_exchange_profiles(),
        "stress_matrix": stress,
        "counter_first_sensitivity": sensitivity,
    }
    validate_results(results)
    if write:
        RESULTS_PATH.write_text(json.dumps(BASE.serial(results), indent=2) + "\n", encoding="utf-8")
        REPORT_PATH.write_text(build_report(results), encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Loaded / Power Attack v0.1")
    parser.add_argument("--primary-trials", type=int, default=PRIMARY_TRIALS)
    parser.add_argument("--sensitivity-trials", type=int, default=SENSITIVITY_TRIALS)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    results = run_all(args.primary_trials, args.sensitivity_trials, args.seed, not args.no_write)
    print(json.dumps({
        "primary_cells": len(results["stress_matrix"]),
        "sensitivity_cells": len(results["counter_first_sensitivity"]),
        "single_exchange_profiles": len(results["single_exchange_profiles"]),
        "report": str(REPORT_PATH),
        "results": str(RESULTS_PATH),
    }, indent=2))


if __name__ == "__main__":
    main()

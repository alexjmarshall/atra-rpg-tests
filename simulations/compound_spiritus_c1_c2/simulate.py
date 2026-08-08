from __future__ import annotations

import argparse
import csv
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
BASE_PATH = ROOT / "simulations" / "spiritus_parry_durchwechseln" / "simulate.py"
MODEL_PATH = HERE / "experiment-model.json"
RESULTS_PATH = HERE / "results.json"

spec = importlib.util.spec_from_file_location("atra_spiritus_base", BASE_PATH)
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = base
spec.loader.exec_module(base)


SEED = 8212026
COMPOUNDS = base.COMPOUNDS
EXACT_SPIRITUS = tuple(range(base.MAX_SPIRITUS + 1))


@dataclass(frozen=True)
class Cell:
    skill_a: int = 10
    skill_b: int = 10
    compound_cost: int = 1
    start_spiritus_a: int = 8
    start_spiritus_b: int = 8
    information: str = "adaptive_revelation"
    future_fights: int = 0
    recovery: str = "R0"
    parry: str = "P1"
    durch_cost: int = 1
    timing: str = "pre"

    @property
    def skill(self) -> int:
        return self.skill_a

    @property
    def start_spiritus(self) -> int:
        return self.start_spiritus_a

    @property
    def label(self) -> str:
        return (
            f"A{self.skill_a}_B{self.skill_b}_C{self.compound_cost}_"
            f"SA{self.start_spiritus_a}_SB{self.start_spiritus_b}_{self.information}"
        )


def spirit_band(spiritus: int) -> str:
    if spiritus == 0:
        return "0"
    if spiritus == 1:
        return "1"
    if spiritus == 2:
        return "2"
    if spiritus <= 5:
        return "3-5"
    return "6-8"


def sequence_bucket(spiritus: int) -> str:
    if spiritus <= 2:
        return str(spiritus)
    if spiritus <= 5:
        return "3-5"
    return "6-8"


def hp_band(hp: int) -> str:
    if hp <= 2:
        return "1-2"
    if hp <= 4:
        return "3-4"
    return "5-8"


def side_stats() -> dict[str, Any]:
    return {
        "choices": Counter(),
        "spiritus_spent": 0,
        "durch_declarations": 0,
        "compound_declarations": 0,
        "compound_unaffordable_opportunities": 0,
        "learned_play_declarations": 0,
        "exchange_resource_states": Counter(),
    }


def pricing_metrics() -> dict[str, Any]:
    metrics = base.fresh_metrics()
    metrics.update({
        "total_damage": 0,
        "fights_with_compound_1_plus": 0,
        "fights_with_compound_2_plus": 0,
        "fights_with_compound_3_plus": 0,
        "chain_distribution": Counter(),
        "learned_chain_sum": 0,
        "learned_chain_exchanges": 0,
        "attempted_fourth_plays": 0,
        "defence_choices_by_spiritus": {str(s): Counter() for s in EXACT_SPIRITUS},
        "known_durch_defence_choices_by_spiritus": {str(s): Counter() for s in EXACT_SPIRITUS},
        "sides": {"A": side_stats(), "B": side_stats()},
    })
    for stats in metrics["compounds"].values():
        stats.update({
            "spirit_opportunities": Counter(),
            "spirit_declarations": Counter(),
            "decline_reasons": Counter(),
            "basic_value_sum": 0.0,
            "counter_value_sum": 0.0,
            "compound_value_sum": 0.0,
            "compound_no_cost_value_sum": 0.0,
            "value_observations": 0,
            "compound_value_observations": 0,
        })
    return metrics


class PricingDuel(base.Duel):
    cell: Cell

    def __init__(
        self,
        rng: random.Random,
        policy_rng: random.Random,
        cell: Cell,
        metrics: dict[str, Any],
        spirit_a: int | None = None,
        spirit_b: int | None = None,
    ) -> None:
        super().__init__(rng, policy_rng, cell, metrics, spirit_a, spirit_b)
        self.a.skill = cell.skill_a
        self.b.skill = cell.skill_b
        self.compounds_this_fight = 0
        self.current_chain: list[str] = []

    def hurt(self, target: base.Fighter, play: str | None = None) -> int:
        amount = super().hurt(target, play)
        self.metrics["total_damage"] += amount
        return amount

    def spend_spiritus(self, fighter: base.Fighter, cost: int, kind: str) -> bool:
        ok = super().spend_spiritus(fighter, cost, kind)
        if ok:
            self.metrics["sides"][fighter.name]["spiritus_spent"] += cost
        return ok

    def record_chain(self) -> None:
        length = len(self.current_chain)
        self.metrics["chain_distribution"][str(length)] += 1
        if length:
            self.metrics["learned_chain_sum"] += length
            self.metrics["learned_chain_exchanges"] += 1

    def durch_decision_parry(
        self, attacker: base.Fighter, defender: base.Fighter, observed_parry_success: bool = False
    ) -> bool:
        declared = super().durch_decision_parry(attacker, defender, observed_parry_success)
        if declared:
            self.current_chain.append("Durchwechseln")
            side = self.metrics["sides"][attacker.name]
            side["durch_declarations"] += 1
            side["learned_play_declarations"] += 1
        return declared

    def durch_decision_schiel(
        self, attacker: base.Fighter, defender: base.Fighter, schiel_roll: int
    ) -> tuple[bool, float]:
        declared, p_win = super().durch_decision_schiel(attacker, defender, schiel_roll)
        if declared:
            self.current_chain.append("Durchwechseln")
            side = self.metrics["sides"][attacker.name]
            side["durch_declarations"] += 1
            side["learned_play_declarations"] += 1
        return declared, p_win

    def basic_parry(self, attacker: base.Fighter, defender: base.Fighter, attribution: str | None) -> None:
        self.metrics["sides"][defender.name]["choices"]["Basic Parry"] += 1
        super().basic_parry(attacker, defender, attribution)

    def counter(self, attacker: base.Fighter, defender: base.Fighter, attribution: str | None) -> None:
        self.metrics["sides"][defender.name]["choices"]["Counter"] += 1
        super().counter(attacker, defender, attribution)

    def compound(
        self,
        name: str,
        attacker: base.Fighter,
        defender: base.Fighter,
        attribution: str | None,
        values: dict[str, float],
    ) -> None:
        self.current_chain.append(name)
        self.compounds_this_fight += 1
        side = self.metrics["sides"][defender.name]
        side["compound_declarations"] += 1
        side["learned_play_declarations"] += 1
        super().compound(name, attacker, defender, attribution, values)

    def zorn(self, attacker: base.Fighter, defender: base.Fighter, attribution: str | None) -> None:
        self.current_chain.append("Zornhau-Ort")
        self.metrics["sides"][defender.name]["learned_play_declarations"] += 1
        super().zorn(attacker, defender, attribution)

    def decline_classification(
        self,
        play: str,
        choice: str,
        defender: base.Fighter,
        values: dict[str, float],
    ) -> str:
        if defender.spiritus < self.cell.compound_cost:
            return "insufficient Spiritus"
        compound_value = values[play]
        p = base.success_probability(defender.skill)
        offense, defense = self.weights(defender, self.other(defender))
        no_cost_value = p * (offense + defense)
        basic = values["Basic Parry"]
        counter = values["Counter"]
        if no_cost_value > max(basic, counter) and compound_value <= max(basic, counter):
            return "Spiritus conservation"
        if basic >= counter and basic > compound_value:
            return "Basic Parry has better expected value"
        if counter > basic and counter > compound_value:
            return "Counter has better expected value"
        if choice in ("Ignore", "Zornhau-Ort"):
            return "tactical/HP urgency"
        return "other policy exploration"

    def record_compound_decisions(
        self,
        attacker: base.Fighter,
        defender: base.Fighter,
        values: dict[str, float],
        legal: dict[str, float],
        choice: str,
    ) -> None:
        p = base.success_probability(defender.skill)
        offense, defense = self.weights(defender, attacker)
        no_cost = p * (offense + defense)
        for name in legal:
            stats = self.metrics["compounds"][name]
            key = str(defender.spiritus)
            stats["spirit_opportunities"][key] += 1
            stats["basic_value_sum"] += values["Basic Parry"]
            stats["counter_value_sum"] += values["Counter"]
            if math.isfinite(values[name]):
                stats["compound_value_sum"] += values[name]
                stats["compound_value_observations"] += 1
            stats["compound_no_cost_value_sum"] += no_cost
            stats["value_observations"] += 1
            if choice == name:
                stats["spirit_declarations"][key] += 1
            else:
                reason = self.decline_classification(name, choice, defender, values)
                stats["decline_reasons"][reason] += 1
            if defender.spiritus < self.cell.compound_cost:
                self.metrics["sides"][defender.name]["compound_unaffordable_opportunities"] += 1

    def defend(
        self,
        attacker: base.Fighter,
        defender: base.Fighter,
        attack: dict[str, Any],
        attribution: str | None,
    ) -> None:
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
        self.metrics["defence_choices_by_spiritus"][str(defender.spiritus)][choice] += 1
        if defender.knows_enemy_durch:
            self.metrics["known_durch_defence_choices_by_spiritus"][str(defender.spiritus)][choice] += 1
        self.record_compound_decisions(attacker, defender, values, legal_compounds, choice)
        if choice == "Ignore":
            self.metrics["choices"]["Ignore"] += 1
            self.metrics["sides"][defender.name]["choices"]["Ignore"] += 1
            self.hurt(defender, attribution)
        elif choice == "Counter":
            self.counter(attacker, defender, attribution)
        elif choice == "Basic Parry":
            self.basic_parry(attacker, defender, attribution)
        elif choice in COMPOUNDS:
            self.compound(choice, attacker, defender, attribution, values)
        else:
            self.zorn(attacker, defender, attribution)

    def activate(self, actor: base.Fighter) -> None:
        target = self.other(actor)
        self.current_chain = []
        for fighter in (actor, target):
            self.metrics["sides"][fighter.name]["exchange_resource_states"][str(fighter.spiritus)] += 1
        if self.contact == "close":
            self.current_chain.append("Pommel Strike")
            side = self.metrics["sides"][actor.name]
            side["learned_play_declarations"] += 1
            stats = self.metrics["free_plays"]["Pommel Strike"]
            stats["declarations"] += 1
            self.spend_action(actor)
            ok, _ = self.roll(actor)
            if ok:
                stats["successes"] += 1
                self.hurt(target, "Pommel Strike")
            self.contact = "none"
            self.record_chain()
            return
        attribution = None
        if target.recovery == "recovering":
            attribution = "Nachreisen"
            self.current_chain.append("Nachreisen")
            self.metrics["sides"][actor.name]["learned_play_declarations"] += 1
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
            self.record_chain()
            return
        if attribution:
            self.metrics["free_plays"]["Nachreisen"]["successes"] += 1
        self.defend(actor, target, attack, attribution)
        self.record_chain()


def record_fight(metrics: dict[str, Any], duel: PricingDuel, outcome: str, rounds: int) -> None:
    base.record_fight(metrics, duel, outcome, rounds)
    if duel.compounds_this_fight >= 1:
        metrics["fights_with_compound_1_plus"] += 1
    if duel.compounds_this_fight >= 2:
        metrics["fights_with_compound_2_plus"] += 1
    if duel.compounds_this_fight >= 3:
        metrics["fights_with_compound_3_plus"] += 1


def ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def finalize(metrics: dict[str, Any]) -> dict[str, Any]:
    result = base.finalize(metrics)
    fights = metrics["fights"]
    endpoints = metrics["end_spirit_n"]
    total_damage = metrics["total_damage"]
    result.update({
        "focal_win_rate": ratio(metrics["wins_A"], fights),
        "focal_win_equivalent": ratio(metrics["wins_A"] + 0.5 * metrics["double_defeats"], fights),
        "symmetry_deviation": ratio(abs(metrics["wins_A"] - metrics["wins_B"]), fights),
        "double_defeat_rate": ratio(metrics["double_defeats"], fights),
        "counter_per_fight": ratio(metrics["choices"]["Counter"], fights),
        "ignore_per_fight": ratio(metrics["choices"]["Ignore"], fights),
        "end_at_3_5_rate": ratio(metrics["end_spirit_buckets"]["3-5"], endpoints),
        "end_at_6_8_rate": ratio(metrics["end_spirit_buckets"]["6-8"], endpoints),
        "total_damage_per_fight": ratio(total_damage, fights),
        "average_learned_play_chain_length": ratio(
            metrics["learned_chain_sum"], metrics["learned_chain_exchanges"]
        ),
        "three_play_chains_per_fight": ratio(metrics["chain_distribution"]["3"], fights),
        "attempted_fourth_plays_per_fight": ratio(metrics["attempted_fourth_plays"], fights),
    })
    compound_declarations = 0
    compound_damage = 0
    for name, raw in metrics["compounds"].items():
        stats = result["compounds"][name]
        compound_declarations += raw["declarations"]
        compound_damage += raw["damage"]
        stats.update({
            "damage_share": ratio(raw["damage"], total_damage),
            "legal_unaffordable_opportunities": raw["opportunities"] - raw["affordable_opportunities"],
            "declaration_rate_by_spiritus": {
                str(s): ratio(raw["spirit_declarations"][str(s)], raw["spirit_opportunities"][str(s)])
                for s in EXACT_SPIRITUS
            },
            "declaration_rate_by_requested_band": {
                band: ratio(
                    sum(raw["spirit_declarations"][str(s)] for s in EXACT_SPIRITUS if spirit_band(s) == band),
                    sum(raw["spirit_opportunities"][str(s)] for s in EXACT_SPIRITUS if spirit_band(s) == band),
                )
                for band in ("6-8", "3-5", "2", "1", "0")
            },
            "mean_basic_parry_value": ratio(raw["basic_value_sum"], raw["value_observations"]),
            "mean_counter_value": ratio(raw["counter_value_sum"], raw["value_observations"]),
            "mean_compound_value": ratio(raw["compound_value_sum"], raw["compound_value_observations"]),
            "mean_compound_no_cost_value": ratio(raw["compound_no_cost_value_sum"], raw["value_observations"]),
        })
    result["compound_total"] = {
        "declarations_per_fight": ratio(compound_declarations, fights),
        "spiritus_per_fight": ratio(metrics["compound_spiritus_spent"], fights),
        "damage_per_fight": ratio(compound_damage, fights),
        "damage_share": ratio(compound_damage, total_damage),
        "defensive_opportunity_rate": ratio(compound_declarations, metrics["defensive_opportunities"]),
        "fights_with_1_plus_rate": ratio(metrics["fights_with_compound_1_plus"], fights),
        "fights_with_2_plus_rate": ratio(metrics["fights_with_compound_2_plus"], fights),
        "fights_with_3_plus_rate": ratio(metrics["fights_with_compound_3_plus"], fights),
    }
    return base.serial(result)


def run_cell(cell: Cell, trials: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    policy_rng = random.Random(seed ^ 0xC12C2)
    metrics = pricing_metrics()
    for _ in range(trials):
        duel = PricingDuel(rng, policy_rng, cell, metrics)
        outcome, rounds = duel.run()
        record_fight(metrics, duel, outcome, rounds)
    return {"cell": asdict(cell), "seed": seed, "metrics": finalize(metrics)}


def primary_cells() -> Iterable[Cell]:
    for skill in (10, 14, 18):
        for start in (8, 3):
            for cost in (1, 2):
                for information in ("adaptive_revelation", "perfect_information"):
                    yield Cell(skill, skill, cost, start, start, information)


def asymmetric_cells() -> Iterable[Cell]:
    for skill_a, skill_b in ((10, 14), (14, 10), (14, 18), (18, 14)):
        for cost in (1, 2):
            yield Cell(skill_a, skill_b, cost, 8, 8, "perfect_information")


def stable_probability(values: dict[str, float], choice: str) -> float:
    top = max(values.values())
    weights = {key: math.exp((value - top) / base.TEMPERATURE) for key, value in values.items()}
    return weights.get(choice, 0.0) / sum(weights.values())


def policy_surface() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for skill in (10, 14, 18):
        for cost in (1, 2):
            for spiritus in EXACT_SPIRITUS:
                for hp in (8, 4, 2):
                    for attack_type, plays in (
                        ("thrust", ("Absetzen", "Scambiar di Punta")),
                        ("descending_cut", ("Schielhau",)),
                    ):
                        cell = Cell(skill, skill, cost, 8, spiritus, "perfect_information")
                        metrics = pricing_metrics()
                        duel = PricingDuel(random.Random(1), random.Random(2), cell, metrics, 8, spiritus)
                        duel.a.hp = 8
                        duel.b.hp = hp
                        attack = {"type": attack_type, "committed": attack_type == "descending_cut"}
                        values = duel.defence_values(duel.a, duel.b, attack)
                        affordable = {
                            key: value for key, value in values.items()
                            if key not in COMPOUNDS or spiritus >= cost
                        }
                        for play in plays:
                            rows.append({
                                "skill": skill,
                                "compound_cost": cost,
                                "spiritus": spiritus,
                                "defender_hp": hp,
                                "attack_type": attack_type,
                                "play": play,
                                "affordable": spiritus >= cost,
                                "basic_parry_value": values["Basic Parry"],
                                "counter_value": values["Counter"],
                                "compound_value": values[play],
                                "selection_probability": stable_probability(affordable, play),
                                "reserve_marginal_value": (
                                    base.reserve_value(spiritus, 0, "R0")
                                    - base.reserve_value(spiritus - 1, 0, "R0")
                                    if spiritus else None
                                ),
                                "durch_affordable": spiritus >= 1,
                            })
    return rows


def shadow_price_pairs(surface: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    lookup = {
        (r["skill"], r["compound_cost"], r["spiritus"], r["defender_hp"], r["play"]): r
        for r in surface
    }
    for skill in (10, 14, 18):
        for cost in (1, 2):
            for high, low in ((8, 7), (5, 4), (3, 2), (2, 1)):
                for play in COMPOUNDS:
                    upper = lookup[(skill, cost, high, 8, play)]
                    lower = lookup[(skill, cost, low, 8, play)]
                    pairs.append({
                        "skill": skill,
                        "compound_cost": cost,
                        "play": play,
                        "comparison": f"{high}_vs_{low}",
                        "high_spiritus": high,
                        "low_spiritus": low,
                        "high_selection_probability": upper["selection_probability"],
                        "low_selection_probability": lower["selection_probability"],
                        "probability_difference": upper["selection_probability"] - lower["selection_probability"],
                        "high_compound_value": upper["compound_value"],
                        "low_compound_value": lower["compound_value"],
                        "utility_difference": upper["compound_value"] - lower["compound_value"],
                        "low_affordable": lower["affordable"],
                        "low_durch_affordable": lower["durch_affordable"],
                    })
    return pairs


def run_sequence(cell: Cell, trials: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    policy_rng = random.Random(seed ^ 0xF1F2F3)
    raw = [pricing_metrics() for _ in range(3)]
    entering_sum = [0, 0, 0]
    leaving_sum = [0, 0, 0]
    entering_buckets = [Counter() for _ in range(3)]
    for _ in range(trials):
        focal_spiritus = base.MAX_SPIRITUS
        for fight_index in range(3):
            entering_sum[fight_index] += focal_spiritus
            entering_buckets[fight_index][sequence_bucket(focal_spiritus)] += 1
            fight_cell = Cell(
                cell.skill_a, cell.skill_b, cell.compound_cost,
                focal_spiritus, base.MAX_SPIRITUS, "adaptive_revelation",
                2 - fight_index, "R0",
            )
            duel = PricingDuel(rng, policy_rng, fight_cell, raw[fight_index], focal_spiritus, base.MAX_SPIRITUS)
            outcome, rounds = duel.run()
            record_fight(raw[fight_index], duel, outcome, rounds)
            focal_spiritus = duel.a.spiritus
            leaving_sum[fight_index] += focal_spiritus
    finalized = [finalize(item) for item in raw]
    focal = [item["sides"]["A"] for item in finalized]
    return {
        "cell": asdict(cell),
        "seed": seed,
        "sequences": trials,
        "entering_spiritus_mean": [value / trials for value in entering_sum],
        "leaving_spiritus_mean": [value / trials for value in leaving_sum],
        "entering_buckets": [
            {key: counter[key] / trials for key in ("0", "1", "2", "3-5", "6-8")}
            for counter in entering_buckets
        ],
        "fight_metrics": finalized,
        "focal_metrics": focal,
        "unused_spiritus_after_fight_3_mean": leaving_sum[2] / trials,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows([
            {
                key: "" if isinstance(value, float) and not math.isfinite(value) else value
                for key, value in row.items()
            }
            for row in rows
        ])


def json_safe(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def flatten_primary(item: dict[str, Any]) -> dict[str, Any]:
    cell, metrics = item["cell"], item["metrics"]
    return {
        **cell,
        "seed": item["seed"],
        "focal_win_rate": metrics["focal_win_rate"],
        "symmetry_deviation": metrics["symmetry_deviation"],
        "average_rounds": metrics["average_rounds"],
        "double_defeat_rate": metrics["double_defeat_rate"],
        "total_spiritus_per_fight": metrics["total_spiritus_per_fight"],
        "mean_end_spiritus_per_combatant": metrics["mean_end_spiritus_per_combatant"],
        "basic_parry_per_fight": metrics["basic_parry_declarations_per_fight"],
        "counter_per_fight": metrics["counter_per_fight"],
        "ignore_per_fight": metrics["ignore_per_fight"],
        **{f"compound_{key}": value for key, value in metrics["compound_total"].items()},
    }


def validate_results(results: dict[str, Any]) -> None:
    assert len(results["primary_matrix"]) == 24
    assert len(results["asymmetric_check"]) == 8
    assert len(results["sequences"]) == 6
    for group in ("primary_matrix", "asymmetric_check"):
        for item in results[group].values():
            metrics = item["metrics"]
            assert metrics["precondition_violations"] == 0
            assert metrics["attempted_fourth_plays"] == 0
            assert all(int(length) <= 3 for length in metrics["chain_distribution"])
            cost = item["cell"]["compound_cost"]
            for stats in metrics["compounds"].values():
                assert stats["spiritus_spent"] == stats["declarations"] * cost
                if cost == 2:
                    assert stats["declaration_rate_by_spiritus"]["1"] == 0
    for item in results["sequences"].values():
        for metrics in item["fight_metrics"]:
            assert metrics["precondition_violations"] == 0


def run_all(
    primary_trials: int = 12000,
    asymmetric_trials: int = 6000,
    sequence_trials: int = 8000,
    seed: int = SEED,
    write: bool = True,
) -> dict[str, Any]:
    primary: dict[str, Any] = {}
    for index, cell in enumerate(primary_cells()):
        primary[cell.label] = run_cell(cell, primary_trials, seed + index * 1009)
    asymmetric: dict[str, Any] = {}
    for index, cell in enumerate(asymmetric_cells()):
        asymmetric[cell.label] = run_cell(cell, asymmetric_trials, seed + 100_000 + index * 1013)
    surface = policy_surface()
    sequences: dict[str, Any] = {}
    for index, skill in enumerate((10, 14, 18)):
        for cost in (1, 2):
            cell = Cell(skill, skill, cost, 8, 8, "adaptive_revelation")
            label = f"skill{skill}_C{cost}_R0"
            sequences[label] = run_sequence(cell, sequence_trials, seed + 200_000 + index * 2018 + cost * 1031)
    results = {
        "model": json.loads(MODEL_PATH.read_text(encoding="utf-8")),
        "seed": seed,
        "trials": {
            "primary_per_cell": primary_trials,
            "asymmetric_per_cell": asymmetric_trials,
            "sequences_per_cell": sequence_trials,
        },
        "primary_matrix": primary,
        "asymmetric_check": asymmetric,
        "policy_surface": surface,
        "shadow_price_pairs": shadow_price_pairs(surface),
        "sequences": sequences,
    }
    validate_results(results)
    if write:
        RESULTS_PATH.write_text(json.dumps(json_safe(base.serial(results)), indent=2) + "\n", encoding="utf-8")
        write_csv(HERE / "fresh-duel-summary.csv", [flatten_primary(item) for item in primary.values()])
        compound_rows = []
        for item in primary.values():
            for play, stats in item["metrics"]["compounds"].items():
                compound_rows.append({**item["cell"], "seed": item["seed"], "play": play, **stats})
        write_csv(HERE / "compound-play-summary.csv", compound_rows)
        write_csv(HERE / "shadow-price-summary.csv", results["shadow_price_pairs"])
        sequence_rows = []
        for label, item in sequences.items():
            row: dict[str, Any] = {"label": label, **item["cell"], "seed": item["seed"]}
            for fight_index in range(3):
                focal = item["focal_metrics"][fight_index]
                row[f"enter_fight_{fight_index + 1}"] = item["entering_spiritus_mean"][fight_index]
                row[f"leave_fight_{fight_index + 1}"] = item["leaving_spiritus_mean"][fight_index]
                row[f"focal_spend_fight_{fight_index + 1}"] = focal["spiritus_spent"] / sequence_trials
                row[f"focal_durch_fight_{fight_index + 1}"] = focal["durch_declarations"] / sequence_trials
                row[f"focal_compound_fight_{fight_index + 1}"] = focal["compound_declarations"] / sequence_trials
                row[f"focal_parry_fight_{fight_index + 1}"] = focal["choices"].get("Basic Parry", 0) / sequence_trials
                row[f"focal_counter_fight_{fight_index + 1}"] = focal["choices"].get("Counter", 0) / sequence_trials
            row["unused_spiritus_after_fight_3_mean"] = item["unused_spiritus_after_fight_3_mean"]
            sequence_rows.append(row)
        write_csv(HERE / "sequence-summary.csv", sequence_rows)
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary-trials", type=int, default=12000)
    parser.add_argument("--asymmetric-trials", type=int, default=6000)
    parser.add_argument("--sequence-trials", type=int, default=8000)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    results = run_all(
        args.primary_trials,
        args.asymmetric_trials,
        args.sequence_trials,
        args.seed,
        write=not args.no_write,
    )
    print(
        f"primary={len(results['primary_matrix'])} asymmetric={len(results['asymmetric_check'])} "
        f"sequences={len(results['sequences'])}"
    )


if __name__ == "__main__":
    main()

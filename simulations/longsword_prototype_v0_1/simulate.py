from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "data" / "prototypes" / "longsword-mechanical-v0.1.yaml"
RESULTS_PATH = Path(__file__).with_name("results.json")
REPORT_PATH = ROOT / "reports" / "longsword-mechanical-prototype-results.md"

PLAY_ABSETZEN = "play-german-longsword-absetzen"
PLAY_ZORN = "play-german-longsword-zornhau-ort"
PLAY_DURCH = "play-german-longsword-durchwechseln"
PLAY_SCIAMBIAR = "play-italian-longsword-scambiar-di-punta"
PLAY_NACH = "play-german-longsword-nachreisen"
PLAY_POMMEL = "play-italian-longsword-pommel-strike"
PLAY_IDS = (PLAY_ABSETZEN, PLAY_ZORN, PLAY_DURCH, PLAY_SCIAMBIAR, PLAY_NACH, PLAY_POMMEL)


@dataclass
class Fighter:
    fighter_id: str
    side: str
    skill: int = 10
    hp: int = 8
    action_ready: bool = True
    recovery: str = "ready"
    prototype: bool = False

    @property
    def alive(self) -> bool:
        return self.hp > 0


def fresh_play_stats() -> dict[str, Any]:
    return {
        "uses": 0,
        "successes": 0,
        "defensive_successes": 0,
        "damage": 0,
        "actions_spent": 0,
        "actions_preserved": 0,
        "continuation_uses": 0,
        "continuation_successes": 0,
        "eligible_triggers": 0,
    }


def fresh_metrics() -> dict[str, Any]:
    return {
        "fights": 0,
        "focal_wins": 0,
        "focal_losses": 0,
        "draws": 0,
        "rounds": 0,
        "exchanges": 0,
        "play_exchanges": 0,
        "total_play_chain_length": 0,
        "cap_exchanges": 0,
        "fights_with_cap": 0,
        "total_damage": 0,
        "prototype_damage": 0,
        "precondition_violations": 0,
        "plays": {play_id: fresh_play_stats() for play_id in PLAY_IDS},
    }


class Fight:
    def __init__(self, rng: random.Random, scenario: str, variant: str,
                 model: dict[str, Any], metrics: dict[str, Any]):
        self.rng = rng
        self.scenario = scenario
        self.variant = variant
        self.model = model
        self.metrics = metrics
        hp = model["simulation_model"]["hit_points"]
        prototype_on = variant != "baseline"
        if scenario == "duel":
            self.fighters = [
                Fighter("A0", "A", hp=hp, prototype=prototype_on),
                Fighter("B0", "B", hp=hp, prototype=False),
            ]
        elif scenario == "one-versus-two":
            self.fighters = [
                Fighter("A0", "A", hp=hp, prototype=prototype_on),
                Fighter("B0", "B", hp=hp, prototype=False),
                Fighter("B1", "B", hp=hp, prototype=False),
            ]
        else:
            raise ValueError(scenario)
        self.contact: dict[tuple[str, str], str] = defaultdict(lambda: "none")
        self.fight_reached_cap = False

    def pair(self, first: Fighter, second: Fighter) -> tuple[str, str]:
        return tuple(sorted((first.fighter_id, second.fighter_id)))

    def roll_success(self, fighter: Fighter) -> bool:
        return self.rng.randint(1, 20) <= fighter.skill

    def damage(self, target: Fighter, amount: int, attribution: str | None = None) -> None:
        target.hp -= amount
        self.metrics["total_damage"] += amount
        if attribution:
            self.metrics["prototype_damage"] += amount
            self.metrics["plays"][attribution]["damage"] += amount

    def roll_damage(self) -> int:
        return self.rng.randint(1, 6) + 1

    def append_play(self, chain: list[str], play_id: str) -> bool:
        cap = self.model["simulation_model"]["exchange_play_cap"]
        if len(chain) >= cap:
            return False
        chain.append(play_id)
        return True

    def finish_exchange(self, chain: list[str]) -> None:
        self.metrics["exchanges"] += 1
        if chain:
            self.metrics["play_exchanges"] += 1
            self.metrics["total_play_chain_length"] += len(chain)
        if len(chain) == self.model["simulation_model"]["exchange_play_cap"]:
            self.metrics["cap_exchanges"] += 1
            self.fight_reached_cap = True

    def choose_basic_attack(self) -> dict[str, str]:
        value = self.rng.random()
        if value < 0.35:
            return {"type": "thrust", "line": "center", "commitment": "committed" if self.rng.random() < 0.35 else "ready"}
        if value < 0.75:
            return {"type": "descending-cut", "line": "high", "commitment": "committed" if self.rng.random() < 0.75 else "ready"}
        return {"type": "other-cut", "line": self.rng.choice(("center", "low", "outside")), "commitment": "committed" if self.rng.random() < 0.5 else "ready"}

    def targets_for(self, actor: Fighter) -> list[Fighter]:
        return [fighter for fighter in self.fighters if fighter.alive and fighter.side != actor.side]

    def choose_target(self, actor: Fighter) -> Fighter:
        targets = self.targets_for(actor)
        close = [target for target in targets if self.contact[self.pair(actor, target)] == "close-crossing"]
        if actor.prototype and close:
            return min(close, key=lambda fighter: fighter.hp)
        recovering = [target for target in targets if target.recovery == "recovering-from-missed-committed-cut"]
        if actor.prototype and recovering:
            return min(recovering, key=lambda fighter: fighter.hp)
        lowest = min(target.hp for target in targets)
        return self.rng.choice([target for target in targets if target.hp == lowest])

    def spend_play_action(self, fighter: Fighter, play_id: str) -> None:
        fighter.action_ready = False
        self.metrics["plays"][play_id]["actions_spent"] += 1

    def use_pommel(self, actor: Fighter, target: Fighter) -> None:
        chain: list[str] = []
        pair = self.pair(actor, target)
        stats = self.metrics["plays"][PLAY_POMMEL]
        stats["eligible_triggers"] += 1
        if self.contact[pair] != "close-crossing":
            self.metrics["precondition_violations"] += 1
            return
        self.append_play(chain, PLAY_POMMEL)
        stats["uses"] += 1
        self.spend_play_action(actor, PLAY_POMMEL)
        if self.roll_success(actor):
            stats["successes"] += 1
            self.damage(target, self.roll_damage(), PLAY_POMMEL)
        self.contact[pair] = "none"
        actor.recovery = "ready"
        self.finish_exchange(chain)

    def declare_attack(self, actor: Fighter, target: Fighter) -> tuple[dict[str, str], list[str], str | None]:
        pair = self.pair(actor, target)
        chain: list[str] = []
        attribution = None
        if actor.prototype and self.contact[pair] == "close-crossing":
            self.use_pommel(actor, target)
            return {}, [], "handled"
        if actor.prototype and target.recovery == "recovering-from-missed-committed-cut":
            attack = {"type": "descending-cut", "line": "high", "commitment": "committed"}
            self.append_play(chain, PLAY_NACH)
            stats = self.metrics["plays"][PLAY_NACH]
            stats["eligible_triggers"] += 1
            stats["uses"] += 1
            stats["actions_spent"] += 1
            attribution = PLAY_NACH
            target.recovery = "ready"
        else:
            attack = self.choose_basic_attack()
        actor.action_ready = False
        actor.recovery = "committed" if attack["commitment"] == "committed" else "ready"
        self.contact[pair] = "none"
        return attack, chain, attribution

    def use_durchwechseln(self, attacker: Fighter, defender: Fighter, chain: list[str],
                          blade_seeking: bool) -> bool:
        stats = self.metrics["plays"][PLAY_DURCH]
        if not attacker.prototype or not blade_seeking:
            return False
        pair = self.pair(attacker, defender)
        stats["eligible_triggers"] += 1
        if self.contact[pair] != "none":
            self.metrics["precondition_violations"] += 1
            return False
        if not self.append_play(chain, PLAY_DURCH):
            return False
        stats["uses"] += 1
        if self.roll_success(attacker):
            stats["successes"] += 1
            self.contact[pair] = "none"
            return True
        return False

    def resolve_combined_remedy(self, defender: Fighter, attacker: Fighter, play_id: str,
                                incoming_attribution: str | None, chain: list[str]) -> bool:
        stats = self.metrics["plays"][play_id]
        pair = self.pair(attacker, defender)
        stats["eligible_triggers"] += 1
        stats["uses"] += 1
        self.append_play(chain, play_id)
        if self.variant in ("A", "C"):
            self.spend_play_action(defender, play_id)
        if self.use_durchwechseln(attacker, defender, chain, blade_seeking=True):
            if self.variant == "B":
                self.spend_play_action(defender, play_id)
            self.damage(defender, self.roll_damage(), PLAY_DURCH)
            return False
        defensive_success = self.roll_success(defender)
        if not defensive_success:
            if self.variant == "B":
                self.spend_play_action(defender, play_id)
            self.damage(defender, self.roll_damage(), incoming_attribution)
            return False
        stats["defensive_successes"] += 1
        self.contact[pair] = "bind-crossing"
        if self.variant == "B":
            stats["actions_preserved"] += 1
        if self.variant in ("A", "B"):
            stats["successes"] += 1
            self.damage(attacker, self.roll_damage(), play_id)
            return True
        if self.roll_success(defender):
            stats["successes"] += 1
            self.damage(attacker, self.roll_damage(), play_id)
        return True

    def resolve_zorn(self, defender: Fighter, attacker: Fighter,
                     incoming_attribution: str | None, chain: list[str]) -> bool:
        stats = self.metrics["plays"][PLAY_ZORN]
        stats["eligible_triggers"] += 1
        stats["uses"] += 1
        self.append_play(chain, PLAY_ZORN)
        self.spend_play_action(defender, PLAY_ZORN)
        pair = self.pair(attacker, defender)
        if self.use_durchwechseln(attacker, defender, chain, blade_seeking=True):
            self.damage(defender, self.roll_damage(), PLAY_DURCH)
            return False
        if not self.roll_success(defender):
            self.damage(defender, self.roll_damage(), incoming_attribution)
            return False
        stats["successes"] += 1
        stats["defensive_successes"] += 1
        self.contact[pair] = "bind-crossing"
        soft_probability = self.model["simulation_model"]["experimental_probabilities"]["successful_zornhau_bind_is_soft"]
        if self.rng.random() < soft_probability:
            stats["continuation_uses"] += 1
            if self.roll_success(defender):
                stats["continuation_successes"] += 1
                self.damage(attacker, self.roll_damage(), PLAY_ZORN)
        return True

    def resolve_successful_attack(self, attacker: Fighter, defender: Fighter, attack: dict[str, str],
                                  chain: list[str], attribution: str | None) -> None:
        pair = self.pair(attacker, defender)
        if not defender.action_ready:
            self.damage(defender, self.roll_damage(), attribution)
            self.finish_exchange(chain)
            return
        if defender.prototype and attack["type"] == "thrust" and attack["line"] in ("center", "high"):
            play_id = PLAY_ABSETZEN if self.rng.random() < 0.5 else PLAY_SCIAMBIAR
            self.resolve_combined_remedy(defender, attacker, play_id, attribution, chain)
            self.finish_exchange(chain)
            return
        if (defender.prototype and attack["type"] == "descending-cut" and
                attack["line"] == "high" and attack["commitment"] == "committed"):
            self.resolve_zorn(defender, attacker, attribution, chain)
            self.finish_exchange(chain)
            return
        defender.action_ready = False
        durch_success = self.use_durchwechseln(attacker, defender, chain, blade_seeking=True)
        if durch_success:
            self.damage(defender, self.roll_damage(), PLAY_DURCH)
            self.finish_exchange(chain)
            return
        if self.roll_success(defender):
            close_probability = self.model["simulation_model"]["experimental_probabilities"]["basic_parry_creates_close_crossing"]
            self.contact[pair] = "close-crossing" if self.rng.random() < close_probability else "bind-crossing"
        else:
            self.contact[pair] = "none"
            self.damage(defender, self.roll_damage(), attribution)
        self.finish_exchange(chain)

    def activate(self, actor: Fighter) -> None:
        if actor.recovery == "recovering-from-missed-committed-cut":
            actor.recovery = "ready"
        target = self.choose_target(actor)
        attack, chain, attribution = self.declare_attack(actor, target)
        if attribution == "handled":
            return
        if not self.roll_success(actor):
            if attribution == PLAY_NACH:
                actor.recovery = "recovering-from-missed-committed-cut"
            elif attack["type"] == "descending-cut" and attack["commitment"] == "committed":
                actor.recovery = "recovering-from-missed-committed-cut"
            else:
                actor.recovery = "ready"
            self.finish_exchange(chain)
            return
        if attribution == PLAY_NACH:
            self.metrics["plays"][PLAY_NACH]["successes"] += 1
        self.resolve_successful_attack(actor, target, attack, chain, attribution)
        if actor.alive and actor.recovery != "recovering-from-missed-committed-cut":
            actor.recovery = "ready"

    def side_alive(self, side: str) -> bool:
        return any(fighter.alive for fighter in self.fighters if fighter.side == side)

    def run(self, max_rounds: int = 100) -> tuple[str | None, int]:
        for round_number in range(1, max_rounds + 1):
            for fighter in self.fighters:
                if fighter.alive:
                    fighter.action_ready = True
            current = self.rng.choice(("A", "B"))
            while self.side_alive("A") and self.side_alive("B"):
                ready = [fighter for fighter in self.fighters if fighter.alive and fighter.side == current and fighter.action_ready]
                if not ready:
                    other = "B" if current == "A" else "A"
                    other_ready = [fighter for fighter in self.fighters if fighter.alive and fighter.side == other and fighter.action_ready]
                    if not other_ready:
                        break
                    current = other
                    ready = other_ready
                actor = self.rng.choice(ready)
                self.activate(actor)
                current = "B" if current == "A" else "A"
            if not self.side_alive("A"):
                return "B", round_number
            if not self.side_alive("B"):
                return "A", round_number
        return None, max_rounds


def finalize(metrics: dict[str, Any]) -> dict[str, Any]:
    fights = metrics["fights"]
    exchanges = metrics["exchanges"]
    play_exchanges = metrics["play_exchanges"]
    output = dict(metrics)
    output["focal_win_rate"] = (metrics["focal_wins"] + 0.5 * metrics["draws"]) / fights
    output["average_rounds"] = metrics["rounds"] / fights
    output["average_exchange_chain_length_all"] = metrics["total_play_chain_length"] / exchanges if exchanges else 0.0
    output["average_exchange_chain_length_when_used"] = metrics["total_play_chain_length"] / play_exchanges if play_exchanges else 0.0
    output["three_play_cap_exchange_frequency"] = metrics["cap_exchanges"] / exchanges if exchanges else 0.0
    output["fights_reaching_three_play_cap"] = metrics["fights_with_cap"] / fights
    output["prototype_damage_share"] = metrics["prototype_damage"] / metrics["total_damage"] if metrics["total_damage"] else 0.0
    for stats in output["plays"].values():
        stats["use_frequency_per_fight"] = stats["uses"] / fights
        stats["success_frequency"] = stats["successes"] / stats["uses"] if stats["uses"] else 0.0
        stats["defensive_success_frequency"] = stats["defensive_successes"] / stats["uses"] if stats["uses"] else 0.0
        stats["average_damage_per_fight"] = stats["damage"] / fights
        stats["actions_spent_per_fight"] = stats["actions_spent"] / fights
        stats["actions_preserved_per_fight"] = stats["actions_preserved"] / fights
    return output


def simulate_cell(model: dict[str, Any], scenario: str, variant: str,
                  trials: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    metrics = fresh_metrics()
    for _ in range(trials):
        fight = Fight(rng, scenario, variant, model, metrics)
        winner, rounds = fight.run()
        metrics["fights"] += 1
        metrics["rounds"] += rounds
        if winner == "A":
            metrics["focal_wins"] += 1
        elif winner == "B":
            metrics["focal_losses"] += 1
        else:
            metrics["draws"] += 1
        if fight.fight_reached_cap:
            metrics["fights_with_cap"] += 1
    return finalize(metrics)


def build_report(results: dict[str, Any]) -> str:
    lines = [
        "# Longsword Mechanical Prototype Results",
        "",
        "Status: **PROVISIONAL experiment; not canonical rules**",
        "",
        "This seeded Monte Carlo comparison isolates six historically audited Plays. Canonical Play mechanics remain null. Costs, tier requirements, final wording, engagement rules, close-crossing generation, bind softness, and AI selection policy are experimental assumptions.",
        "",
        "## Variant definitions",
        "",
        "- **A:** Absetzen and Scambiar di Punta use one combined roll, spend the action, cancel damage and return damage on success.",
        "- **B:** same combined roll, but preserve the action on success; failure or Durchwechseln bypass spends it.",
        "- **C:** spend the action, roll defence first, then make a separate attack roll only after defensive success.",
        "- **Baseline:** basic Strike/Parry only; no prototype Plays.",
        "",
        "## Outcome summary",
        "",
        "| Scenario | Variant | Focal win rate | Effect vs baseline | Prototype damage share | Actions spent/fight | Actions preserved/fight | Avg chain (Play exchanges) | 3-Play cap / exchange | Fights reaching cap |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for scenario in ("duel", "one-versus-two"):
        baseline = results["cells"][scenario]["baseline"]["focal_win_rate"]
        for variant in ("baseline", "A", "B", "C"):
            cell = results["cells"][scenario][variant]
            spent = sum(item["actions_spent_per_fight"] for item in cell["plays"].values())
            preserved = sum(item["actions_preserved_per_fight"] for item in cell["plays"].values())
            lines.append(
                f"| {scenario} | {variant} | {cell['focal_win_rate']:.2%} | "
                f"{cell['focal_win_rate'] - baseline:+.2%} | {cell['prototype_damage_share']:.2%} | "
                f"{spent:.3f} | {preserved:.3f} | {cell['average_exchange_chain_length_when_used']:.3f} | "
                f"{cell['three_play_cap_exchange_frequency']:.3%} | {cell['fights_reaching_three_play_cap']:.2%} |"
            )
    lines += [
        "",
        "## Per-Play use, success, and damage",
        "",
        "Use frequency is mean declarations per fight. Success is complete success per declaration; for sequential variant C, the separate defensive-success rate is also shown. Damage is mean attributed damage per fight.",
        "",
    ]
    short = {
        PLAY_ABSETZEN: "Absetzen", PLAY_ZORN: "Zornhau-Ort", PLAY_DURCH: "Durchwechseln",
        PLAY_SCIAMBIAR: "Scambiar di Punta", PLAY_NACH: "Nachreisen", PLAY_POMMEL: "Pommel Strike",
    }
    for scenario in ("duel", "one-versus-two"):
        lines += [
            f"### {scenario}", "",
            "| Variant | Play | Uses/fight | Success | Defensive success | Damage/fight | Actions spent/fight | Actions preserved/fight |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
        for variant in ("A", "B", "C"):
            for play_id in PLAY_IDS:
                stats = results["cells"][scenario][variant]["plays"][play_id]
                lines.append(
                    f"| {variant} | {short[play_id]} | {stats['use_frequency_per_fight']:.3f} | "
                    f"{stats['success_frequency']:.2%} | {stats['defensive_success_frequency']:.2%} | "
                    f"{stats['average_damage_per_fight']:.3f} | {stats['actions_spent_per_fight']:.3f} | {stats['actions_preserved_per_fight']:.3f} |"
                )
        lines.append("")
    lines += [
        "## Interpretation limits",
        "",
        "- Incoming attacks explicitly carry type, line, and commitment. Pair state explicitly uses `none`, `bind-crossing`, or `close-crossing`; recovery uses the exact missed-committed-cut window for Nachreisen.",
        "- Durchwechseln is checked only after a blade-seeking defence is declared and while contact is `none`. The simulator records any violation; all published cells must report zero.",
        "- Zornhau-Ort's counter-cut is defensive and non-damaging in this experiment. Its point is a separate conditional roll after a soft bind; the 50% soft-bind rate is a calibration assumption, not a historical frequency.",
        "- A basic successful Parry creates a close crossing 25% of the time solely to exercise Pommel Strike. Pommel Strike uses Longsword and has no Wrestling prerequisite.",
        "- d6+1 is used for every damaging success, including the pommel, to avoid deciding the OPEN weapon-profile question. This is not a claim that all damage profiles should match.",
        "- The three-Play cap is enforced without resolving the packet's OPEN four-slot timing contradiction. No fourth Play is admitted.",
        "- The observed cap frequency is zero because the effectiveness scenarios give the package only to the focal side; the six-Play subset then produces at most an initiation plus one continuation, or one remedy. Zero here is a coverage finding, not evidence that the cap can never bind in a mirrored or expanded curriculum.",
        "",
        f"Seed: `{results['seed']}`. Trials per scenario/variant: `{results['trials_per_cell']}`.",
        "",
    ]
    return "\n".join(lines)


def run_all(trials: int | None = None, seed: int | None = None,
            write: bool = True) -> dict[str, Any]:
    model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    configured = model["simulation_model"]
    trials = trials or configured["trials_per_cell"]
    seed = seed if seed is not None else configured["seed"]
    results: dict[str, Any] = {"model_id": model["id"], "seed": seed, "trials_per_cell": trials, "cells": {}}
    cell_index = 0
    for scenario in ("duel", "one-versus-two"):
        results["cells"][scenario] = {}
        for variant in ("baseline", "A", "B", "C"):
            results["cells"][scenario][variant] = simulate_cell(
                model, scenario, variant, trials, seed + cell_index * 100003
            )
            cell_index += 1
    if write:
        RESULTS_PATH.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        REPORT_PATH.write_text(build_report(results), encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    results = run_all(args.trials, args.seed, write=not args.no_write)
    for scenario, cells in results["cells"].items():
        print(scenario)
        for variant, cell in cells.items():
            print(f"  {variant}: win={cell['focal_win_rate']:.3%}, cap={cell['three_play_cap_exchange_frequency']:.3%}")


if __name__ == "__main__":
    main()

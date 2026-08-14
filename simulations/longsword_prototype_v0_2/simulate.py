from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "data" / "prototypes" / "longsword-mechanical-v0.2.yaml"
RESULTS_PATH = Path(__file__).with_name("results.json")
REPORT_PATH = ROOT / "reports" / "longsword-mirrored-ablation-results.md"

ABSETZEN = "play-german-longsword-absetzen"
ZORN = "play-german-longsword-zornhau-ort"
DURCH = "play-german-longsword-durchwechseln"
SCIAMBIAR = "play-italian-longsword-scambiar-di-punta"
NACH = "play-german-longsword-nachreisen"
POMMEL = "play-italian-longsword-pommel-strike"
SCHIEL = "play-german-longsword-schielhau"
PLAY_IDS = (ABSETZEN, ZORN, DURCH, SCIAMBIAR, NACH, POMMEL, SCHIEL)
SHORT = {
    ABSETZEN: "Absetzen", ZORN: "Zornhau-Ort", DURCH: "Durchwechseln",
    SCIAMBIAR: "Scambiar di Punta", NACH: "Nachreisen",
    POMMEL: "Pommel Strike", SCHIEL: "Schielhau",
}


@dataclass
class Fighter:
    fighter_id: str
    hp: int = 8
    skill: int = 10
    action_ready: bool = True
    recovery: str = "ready"

    @property
    def alive(self) -> bool:
        return self.hp > 0


def play_stats() -> dict[str, int]:
    return {
        "uses": 0, "successes": 0, "damage": 0, "actions_spent": 0,
        "continuation_uses": 0, "continuation_successes": 0,
        "rejoinder_attempts": 0, "rejoinder_successes": 0, "rejoinder_damage": 0,
    }


def fresh_metrics() -> dict[str, Any]:
    return {
        "fights": 0, "wins_A": 0, "wins_B": 0, "double_defeats": 0,
        "draws": 0, "rounds": 0, "exchanges": 0, "total_actions_spent": 0,
        "play_actions_spent": 0, "total_damage": 0, "play_damage": 0,
        "play_chain_distribution": {"0": 0, "1": 0, "2": 0, "3": 0},
        "attempted_fourth_plays": 0, "cap_sequences": Counter(),
        "attempted_fourth_sequences": Counter(),
        "basic_defensive_choices": 0, "successful_basic_defensive_choices": 0,
        "basic_defence_durch_opportunities": 0, "durch_opportunities_all": 0,
        "durch_attempts": 0, "durch_successes": 0,
        "contact_states_reached": Counter(), "recovery_windows_created": 0,
        "recovery_windows_exploited": 0, "bind_pressure_assignments": Counter(),
        "incoming_attack_types": Counter(), "incoming_attack_lines": Counter(),
        "precondition_violations": 0,
        "plays": {play_id: play_stats() for play_id in PLAY_IDS},
    }


class Duel:
    def __init__(self, rng: random.Random, model: dict[str, Any], available: set[str], metrics: dict[str, Any]):
        self.rng = rng
        self.model = model
        self.available = available
        self.metrics = metrics
        hp = 8
        self.a = Fighter("A", hp=hp)
        self.b = Fighter("B", hp=hp)
        self.contact = "none"
        self.current_chain: list[str] = []

    def other(self, fighter: Fighter) -> Fighter:
        return self.b if fighter is self.a else self.a

    def roll(self, fighter: Fighter) -> bool:
        return self.rng.randint(1, 20) <= fighter.skill

    def damage_roll(self) -> int:
        return self.rng.randint(1, 6) + 1

    def spend_action(self, fighter: Fighter, play_id: str | None = None) -> None:
        if not fighter.action_ready:
            self.metrics["precondition_violations"] += 1
            return
        fighter.action_ready = False
        self.metrics["total_actions_spent"] += 1
        if play_id:
            self.metrics["play_actions_spent"] += 1
            self.metrics["plays"][play_id]["actions_spent"] += 1

    def deal_damage(self, target: Fighter, amount: int, play_id: str | None = None,
                    rejoinder: bool = False) -> None:
        target.hp -= amount
        self.metrics["total_damage"] += amount
        if play_id:
            self.metrics["play_damage"] += amount
            self.metrics["plays"][play_id]["damage"] += amount
            if rejoinder:
                self.metrics["plays"][play_id]["rejoinder_damage"] += amount

    def add_play(self, play_id: str) -> bool:
        cap = self.model["rules"]["exchange_play_cap"]
        if len(self.current_chain) >= cap:
            self.metrics["attempted_fourth_plays"] += 1
            attempted = tuple(self.current_chain + [play_id])
            self.metrics["attempted_fourth_sequences"][attempted] += 1
            return False
        self.current_chain.append(play_id)
        self.metrics["plays"][play_id]["uses"] += 1
        return True

    def finish_exchange(self) -> None:
        length = len(self.current_chain)
        self.metrics["exchanges"] += 1
        self.metrics["play_chain_distribution"][str(length)] += 1
        if length == self.model["rules"]["exchange_play_cap"]:
            self.metrics["cap_sequences"][tuple(self.current_chain)] += 1
        self.current_chain = []

    def choose_attack(self) -> dict[str, str]:
        value = self.rng.random()
        if value < 0.35:
            return {"type": "thrust", "line": "center", "commitment": "committed" if self.rng.random() < 0.35 else "ready"}
        if value < 0.75:
            return {"type": "descending-cut", "line": "high", "commitment": "committed" if self.rng.random() < 0.75 else "ready"}
        return {"type": "other-cut", "line": self.rng.choice(("center", "low", "outside")), "commitment": "committed" if self.rng.random() < 0.5 else "ready"}

    def set_contact(self, state: str) -> None:
        self.contact = state
        if state != "none":
            self.metrics["contact_states_reached"][state] += 1

    def attempt_durch(self, attacker: Fighter, defender: Fighter) -> str:
        if DURCH not in self.available:
            return "unavailable"
        self.metrics["durch_opportunities_all"] += 1
        if self.contact != "none":
            self.metrics["precondition_violations"] += 1
            return "ineligible"
        if not self.add_play(DURCH):
            return "blocked-by-cap"
        self.metrics["durch_attempts"] += 1
        if self.roll(attacker):
            self.metrics["durch_successes"] += 1
            self.metrics["plays"][DURCH]["successes"] += 1
            return "success"
        return "failure"

    def basic_parry(self, attacker: Fighter, defender: Fighter, attack: dict[str, str], attribution: str | None) -> None:
        self.metrics["basic_defensive_choices"] += 1
        self.spend_action(defender)
        blade_seeking = self.rng.random() < 0.5
        if not self.roll(defender):
            self.deal_damage(defender, self.damage_roll(), attribution)
            return
        self.metrics["successful_basic_defensive_choices"] += 1
        if blade_seeking and DURCH in self.available:
            self.metrics["basic_defence_durch_opportunities"] += 1
            outcome = self.attempt_durch(attacker, defender)
            if outcome == "success":
                self.deal_damage(defender, self.damage_roll(), DURCH)
                self.set_contact("none")
                return
        close_probability = self.model["calibration_flags"]["close_crossing_probability"]
        self.set_contact("close-crossing" if self.rng.random() < close_probability else "bind-crossing")

    def combined_remedy(self, play_id: str, attacker: Fighter, defender: Fighter,
                        attribution: str | None) -> None:
        if not self.add_play(play_id):
            self.deal_damage(defender, self.damage_roll(), attribution)
            return
        self.spend_action(defender, play_id)
        if not self.roll(defender):
            self.deal_damage(defender, self.damage_roll(), attribution)
            return
        outcome = self.attempt_durch(attacker, defender)
        if outcome == "success":
            self.deal_damage(defender, self.damage_roll(), DURCH)
            return
        self.metrics["plays"][play_id]["successes"] += 1
        self.set_contact("bind-crossing")
        self.deal_damage(attacker, self.damage_roll(), play_id)

    def zorn_remedy(self, attacker: Fighter, defender: Fighter, attribution: str | None) -> None:
        if not self.add_play(ZORN):
            self.deal_damage(defender, self.damage_roll(), attribution)
            return
        self.spend_action(defender, ZORN)
        if not self.roll(defender):
            self.deal_damage(defender, self.damage_roll(), attribution)
            return
        outcome = self.attempt_durch(attacker, defender)
        if outcome == "success":
            self.deal_damage(defender, self.damage_roll(), DURCH)
            return
        self.metrics["plays"][ZORN]["successes"] += 1
        self.set_contact("bind-crossing")
        soft_probability = self.model["calibration_flags"]["soft_bind_probability"]
        pressure = "soft" if self.rng.random() < soft_probability else "hard"
        self.metrics["bind_pressure_assignments"][pressure] += 1
        if pressure == "soft":
            stats = self.metrics["plays"][ZORN]
            stats["continuation_uses"] += 1
            if self.roll(defender):
                stats["continuation_successes"] += 1
                self.deal_damage(attacker, self.damage_roll(), ZORN)

    def schielhau_remedy(self, attacker: Fighter, defender: Fighter, attribution: str | None) -> None:
        if not self.add_play(SCHIEL):
            self.deal_damage(defender, self.damage_roll(), attribution)
            return
        self.spend_action(defender, SCHIEL)
        if not self.roll(defender):
            self.deal_damage(defender, self.damage_roll(), attribution)
            return
        outcome = self.attempt_durch(attacker, defender)
        stats = self.metrics["plays"][SCHIEL]
        if outcome == "success":
            stats["rejoinder_attempts"] += 1
            if self.roll(defender):
                stats["rejoinder_successes"] += 1
                stats["successes"] += 1
                self.set_contact("bind-crossing")
                self.deal_damage(attacker, self.damage_roll(), SCHIEL, rejoinder=True)
            else:
                self.deal_damage(defender, self.damage_roll(), DURCH)
            return
        stats["successes"] += 1
        self.set_contact("bind-crossing")
        self.deal_damage(attacker, self.damage_roll(), SCHIEL)

    def defend(self, attacker: Fighter, defender: Fighter, attack: dict[str, str], attribution: str | None) -> None:
        if not defender.action_ready:
            self.deal_damage(defender, self.damage_roll(), attribution)
            return
        if attack["type"] == "thrust":
            remedies = [play for play in (ABSETZEN, SCIAMBIAR) if play in self.available]
            if remedies:
                self.combined_remedy(self.rng.choice(remedies), attacker, defender, attribution)
                return
        if attack["type"] == "descending-cut" and attack["line"] == "high":
            remedies = []
            if SCHIEL in self.available:
                remedies.append(SCHIEL)
            if ZORN in self.available and attack["commitment"] == "committed":
                remedies.append(ZORN)
            if remedies:
                chosen = self.rng.choice(remedies)
                if chosen == SCHIEL:
                    self.schielhau_remedy(attacker, defender, attribution)
                else:
                    self.zorn_remedy(attacker, defender, attribution)
                return
        self.basic_parry(attacker, defender, attack, attribution)

    def pommel(self, actor: Fighter, target: Fighter) -> None:
        if self.contact != "close-crossing":
            self.metrics["precondition_violations"] += 1
            return
        if not self.add_play(POMMEL):
            return
        self.spend_action(actor, POMMEL)
        if self.roll(actor):
            self.metrics["plays"][POMMEL]["successes"] += 1
            self.deal_damage(target, self.damage_roll(), POMMEL)
        self.set_contact("none")

    def activate(self, actor: Fighter) -> None:
        target = self.other(actor)
        if actor.recovery == "recovering-from-missed-committed-cut":
            actor.recovery = "ready"
        self.current_chain = []
        if POMMEL in self.available and self.contact == "close-crossing":
            self.pommel(actor, target)
            self.finish_exchange()
            return
        attribution = None
        if NACH in self.available and target.recovery == "recovering-from-missed-committed-cut":
            attack = {"type": "descending-cut", "line": "high", "commitment": "committed"}
            if self.add_play(NACH):
                attribution = NACH
                self.metrics["recovery_windows_exploited"] += 1
                target.recovery = "ready"
                self.spend_action(actor, NACH)
            else:
                self.spend_action(actor)
        else:
            attack = self.choose_attack()
            self.spend_action(actor)
        self.metrics["incoming_attack_types"][attack["type"]] += 1
        self.metrics["incoming_attack_lines"][attack["line"]] += 1
        actor.recovery = "committed" if attack["commitment"] == "committed" else "ready"
        self.set_contact("none")
        if not self.roll(actor):
            if attack["type"] == "descending-cut" and attack["commitment"] == "committed":
                actor.recovery = "recovering-from-missed-committed-cut"
                self.metrics["recovery_windows_created"] += 1
            self.finish_exchange()
            return
        if attribution:
            self.metrics["plays"][attribution]["successes"] += 1
        self.defend(actor, target, attack, attribution)
        if actor.alive and actor.recovery != "recovering-from-missed-committed-cut":
            actor.recovery = "ready"
        self.finish_exchange()

    def run(self, max_rounds: int = 100) -> tuple[str, int]:
        for round_number in range(1, max_rounds + 1):
            for fighter in (self.a, self.b):
                if fighter.alive:
                    fighter.action_ready = True
            order = [self.a, self.b] if self.rng.random() < 0.5 else [self.b, self.a]
            for fighter in order:
                if fighter.alive and fighter.action_ready and self.other(fighter).alive:
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


def serialize_counters(value: Any) -> Any:
    if isinstance(value, Counter):
        return {" > ".join(key) if isinstance(key, tuple) else str(key): count for key, count in value.items()}
    if isinstance(value, dict):
        return {key: serialize_counters(item) for key, item in value.items()}
    return value


def finalize(metrics: dict[str, Any]) -> dict[str, Any]:
    fights = metrics["fights"]
    exchanges = metrics["exchanges"]
    output = serialize_counters(metrics)
    output["average_rounds"] = metrics["rounds"] / fights
    output["double_defeat_rate"] = metrics["double_defeats"] / fights
    output["actions_spent_per_fight"] = metrics["total_actions_spent"] / fights
    output["play_actions_spent_per_fight"] = metrics["play_actions_spent"] / fights
    output["play_uses_per_fight"] = sum(stats["uses"] for stats in metrics["plays"].values()) / fights
    output["play_damage_per_fight"] = metrics["play_damage"] / fights
    output["total_damage_per_fight"] = metrics["total_damage"] / fights
    output["basic_defence_durch_opportunity_fraction"] = (
        metrics["basic_defence_durch_opportunities"] / metrics["successful_basic_defensive_choices"]
        if metrics["successful_basic_defensive_choices"] else 0.0
    )
    output["durch_attempts_per_fight"] = metrics["durch_attempts"] / fights
    output["durch_attempt_success_rate"] = metrics["durch_successes"] / metrics["durch_attempts"] if metrics["durch_attempts"] else 0.0
    output["rejoinder_attempts_per_fight"] = metrics["plays"][SCHIEL]["rejoinder_attempts"] / fights
    output["rejoinder_answer_rate"] = (
        metrics["plays"][SCHIEL]["rejoinder_successes"] / metrics["plays"][SCHIEL]["rejoinder_attempts"]
        if metrics["plays"][SCHIEL]["rejoinder_attempts"] else 0.0
    )
    output["rejoinder_damage_per_fight"] = metrics["plays"][SCHIEL]["rejoinder_damage"] / fights
    output["rejoinder_damage_share_total"] = (
        metrics["plays"][SCHIEL]["rejoinder_damage"] / metrics["total_damage"]
        if metrics["total_damage"] else 0.0
    )
    output["rejoinder_damage_share_play"] = (
        metrics["plays"][SCHIEL]["rejoinder_damage"] / metrics["play_damage"]
        if metrics["play_damage"] else 0.0
    )
    output["chain_distribution_fraction"] = {
        length: count / exchanges for length, count in metrics["play_chain_distribution"].items()
    }
    output["bind_crossing_frequency"] = metrics["contact_states_reached"]["bind-crossing"] / exchanges
    output["close_crossing_frequency"] = metrics["contact_states_reached"]["close-crossing"] / exchanges
    output["recovery_window_frequency"] = metrics["recovery_windows_created"] / exchanges
    output["recovery_exploitation_frequency"] = metrics["recovery_windows_exploited"] / exchanges
    for stats in output["plays"].values():
        stats["uses_per_fight"] = stats["uses"] / fights
        stats["damage_per_fight"] = stats["damage"] / fights
        stats["success_rate"] = stats["successes"] / stats["uses"] if stats["uses"] else 0.0
    return output


def run_cell(model: dict[str, Any], available: set[str], trials: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    metrics = fresh_metrics()
    for _ in range(trials):
        duel = Duel(rng, model, available, metrics)
        outcome, rounds = duel.run()
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
    return finalize(metrics)


def build_report(results: dict[str, Any]) -> str:
    full = results["cells"]["full"]
    lines = [
        "# Mirrored Longsword Prototype and Per-Play Ablations",
        "",
        "Status: **PROVISIONAL experiment; no final costs, tiers, or wording**",
        "",
        "Both equal-Skill-10 duelists possess the same repertoire. Absetzen and Scambiar di Punta use Variant A. Action preservation is disabled. Each ablation removes one Play from both fighters.",
        "",
        "## Full-repertoire headline",
        "",
        f"- Successful basic defensive choices creating a Durchwechseln opportunity: **{full['basic_defence_durch_opportunity_fraction']:.2%}**.",
        f"- Durchwechseln attempts: **{full['durch_attempts_per_fight']:.3f} per fight**; success **{full['durch_attempt_success_rate']:.2%}**.",
        f"- Schielhau long-point rejoinder: **{full['rejoinder_attempts_per_fight']:.3f} attempts per fight**; answered **{full['rejoinder_answer_rate']:.2%}**; damage **{full['rejoinder_damage_per_fight']:.3f} per fight** (**{full['rejoinder_damage_share_total']:.2%} of all damage; {full['rejoinder_damage_share_play']:.2%} of Play-attributed damage**).",
        "",
        "## Ablation outcomes",
        "",
        "| Removed from both fighters | Uses/fight | Δ uses | Play damage/fight | Δ damage | Avg rounds | Δ rounds | Double defeats | Actions/fight | Play actions/fight |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, cell in results["cells"].items():
        removed = "None (full)" if label == "full" else SHORT[label.removeprefix("without:")]
        lines.append(
            f"| {removed} | {cell['play_uses_per_fight']:.3f} | {cell['play_uses_per_fight'] - full['play_uses_per_fight']:+.3f} | "
            f"{cell['play_damage_per_fight']:.3f} | {cell['play_damage_per_fight'] - full['play_damage_per_fight']:+.3f} | "
            f"{cell['average_rounds']:.3f} | {cell['average_rounds'] - full['average_rounds']:+.3f} | "
            f"{cell['double_defeat_rate']:.3%} | {cell['actions_spent_per_fight']:.3f} | {cell['play_actions_spent_per_fight']:.3f} |"
        )
    lines += [
        "",
        "### Per-Play substitution after removal",
        "",
        "The last two columns identify the largest compensating change among Plays that remain available; complete per-Play values are retained in `results.json`.",
        "",
        "| Removed | Removed Play's full uses/fight | Removed Play's full damage/fight | Largest remaining use change | Largest remaining damage change |",
        "|---|---:|---:|---|---|",
    ]
    for label, cell in results["cells"].items():
        if label == "full":
            continue
        removed_id = label.removeprefix("without:")
        remaining = [play_id for play_id in PLAY_IDS if play_id != removed_id]
        use_id = max(remaining, key=lambda play_id: abs(cell["plays"][play_id]["uses_per_fight"] - full["plays"][play_id]["uses_per_fight"]))
        damage_id = max(remaining, key=lambda play_id: abs(cell["plays"][play_id]["damage_per_fight"] - full["plays"][play_id]["damage_per_fight"]))
        use_delta = cell["plays"][use_id]["uses_per_fight"] - full["plays"][use_id]["uses_per_fight"]
        damage_delta = cell["plays"][damage_id]["damage_per_fight"] - full["plays"][damage_id]["damage_per_fight"]
        lines.append(
            f"| {SHORT[removed_id]} | {full['plays'][removed_id]['uses_per_fight']:.3f} | "
            f"{full['plays'][removed_id]['damage_per_fight']:.3f} | {SHORT[use_id]} {use_delta:+.3f} | "
            f"{SHORT[damage_id]} {damage_delta:+.3f} |"
        )
    lines += [
        "",
        "## Tactical-state frequencies by ablation",
        "",
        "Frequencies are occurrences per exchange, not probabilities that the state persists.",
        "",
        "| Removed | Bind-crossing | Close-crossing | Recovery created | Recovery exploited | Durch opportunity/basic defence |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for label, cell in results["cells"].items():
        removed = "None" if label == "full" else SHORT[label.removeprefix("without:")]
        lines.append(
            f"| {removed} | {cell['bind_crossing_frequency']:.2%} | {cell['close_crossing_frequency']:.2%} | "
            f"{cell['recovery_window_frequency']:.2%} | {cell['recovery_exploitation_frequency']:.2%} | "
            f"{cell['basic_defence_durch_opportunity_fraction']:.2%} |"
        )
    lines += [
        "",
        "## Durchwechseln and Schielhau interaction",
        "",
        "| Removed | Successful basic defences | Opportunity fraction | Durch attempts/fight | Durch success | Rejoinder attempts/fight | Rejoinder answers | Rejoinder damage/fight |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, cell in results["cells"].items():
        removed = "None" if label == "full" else SHORT[label.removeprefix("without:")]
        lines.append(
            f"| {removed} | {cell['successful_basic_defensive_choices']} | {cell['basic_defence_durch_opportunity_fraction']:.2%} | "
            f"{cell['durch_attempts_per_fight']:.3f} | {cell['durch_attempt_success_rate']:.2%} | "
            f"{cell['rejoinder_attempts_per_fight']:.3f} | {cell['rejoinder_answer_rate']:.2%} | {cell['rejoinder_damage_per_fight']:.3f} |"
        )
    lines += [
        "",
        "## Learned-Play chain stress",
        "",
        "| Removed | 0 Plays | 1 Play | 2 Plays | 3 Plays | Attempted fourth Plays |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for label, cell in results["cells"].items():
        removed = "None" if label == "full" else SHORT[label.removeprefix("without:")]
        dist = cell["chain_distribution_fraction"]
        lines.append(
            f"| {removed} | {dist['0']:.2%} | {dist['1']:.2%} | {dist['2']:.2%} | {dist['3']:.2%} | {cell['attempted_fourth_plays']} |"
        )
    lines += ["", "### Exact full-repertoire cap sequences", ""]
    if full["cap_sequences"]:
        for sequence, count in sorted(full["cap_sequences"].items(), key=lambda item: (-item[1], item[0])):
            friendly = " → ".join(SHORT.get(part, part) for part in sequence.split(" > "))
            lines.append(f"- {friendly}: **{count}** exchanges")
    else:
        lines.append("- None.")
    lines += ["", "### Attempted fourth-Play sequences", ""]
    if full["attempted_fourth_sequences"]:
        for sequence, count in sorted(full["attempted_fourth_sequences"].items(), key=lambda item: (-item[1], item[0])):
            friendly = " → ".join(SHORT.get(part, part) for part in sequence.split(" > "))
            lines.append(f"- {friendly}: **{count}** attempts; the fourth Play was suppressed.")
    else:
        lines.append("- **0.** No legal fourth Play became eligible in this seven-Play mirrored repertoire; this is reported as a coverage result, not a resolution of the packet's timing question.")
    lines += [
        "",
        "## Artificial calibration assumptions—do not tune to these",
        "",
        f"- **Soft/hard bind:** successful eligible Zornhau-Ort binds are labeled soft with fixed probability `{results['model']['calibration_flags']['soft_bind_probability']}`. This exists only to exercise the conditional point continuation.",
        f"- **Close crossing:** successful eligible basic defences create close-crossing with fixed probability `{results['model']['calibration_flags']['close_crossing_probability']}`. This exists only to exercise Pommel Strike.",
        "- Both rates are held constant in every ablation. No Zornhau-Ort or Pommel Strike rule, cost, tier, or balance conclusion should be fitted to them.",
        "- Basic successful parries are classified blade-seeking 50% of the time as a declared AI-policy assumption. It is not a historical frequency.",
        "",
        "## Source-bounded rejoinder",
        "",
        "Schielhau is available only against a high descending cut. Its long-point rejoinder is attempted only if the same opponent then succeeds with Durchwechseln below that Schielhau before contact. It is never offered after an arbitrary defence or against a generic feint.",
        "",
        f"Seed: `{results['seed']}`. Trials per cell: `{results['trials_per_cell']}`. Precondition violations in full cell: `{full['precondition_violations']}`.",
        "",
    ]
    return "\n".join(lines)


def run_all(trials: int | None = None, seed: int | None = None, write: bool = True) -> dict[str, Any]:
    model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    trials = trials or model["simulation_model"]["trials_per_ablation"]
    seed = model["simulation_model"]["seed"] if seed is None else seed
    all_plays = set(model["scope"]["selected_play_ids"])
    cells: dict[str, Any] = {}
    specifications = [("full", all_plays)] + [(f"without:{play_id}", all_plays - {play_id}) for play_id in PLAY_IDS]
    for index, (label, available) in enumerate(specifications):
        cells[label] = run_cell(model, available, trials, seed + index * 100003)
    results = {"model_id": model["id"], "seed": seed, "trials_per_cell": trials, "model": model, "cells": cells}
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
    for label, cell in results["cells"].items():
        print(
            f"{label}: rounds={cell['average_rounds']:.3f}, play_damage={cell['play_damage_per_fight']:.3f}, "
            f"chains3={cell['chain_distribution_fraction']['3']:.3%}, fourth={cell['attempted_fourth_plays']}"
        )


if __name__ == "__main__":
    main()

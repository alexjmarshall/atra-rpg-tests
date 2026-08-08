from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "data" / "prototypes" / "longsword-durchwechseln-schielhau-state-model-v0.3.yaml"
RESULTS_PATH = Path(__file__).with_name("state-model-results.json")
REPORT_PATH = ROOT / "reports" / "durchwechseln-schielhau-state-model-results.md"

ABSETZEN = "play-german-longsword-absetzen"
ZORN = "play-german-longsword-zornhau-ort"
DURCH = "play-german-longsword-durchwechseln"
SCIAMBIAR = "play-italian-longsword-scambiar-di-punta"
NACH = "play-german-longsword-nachreisen"
POMMEL = "play-italian-longsword-pommel-strike"
SCHIEL = "play-german-longsword-schielhau"
PLAYS = (ABSETZEN, ZORN, DURCH, SCIAMBIAR, NACH, POMMEL, SCHIEL)
SHORT = {
    ABSETZEN: "Absetzen", ZORN: "Zornhau-Ort", DURCH: "Durchwechseln",
    SCIAMBIAR: "Scambiar di Punta", NACH: "Nachreisen",
    POMMEL: "Pommel Strike", SCHIEL: "Schielhau",
}
INFO = ("naive", "adaptive_revelation", "perfect_information")
SCHIEL_VARIANTS = ("S1", "S2", "S3")


@dataclass
class Fighter:
    fighter_id: str
    side: str
    available: set[str]
    hp: int = 8
    skill: int = 10
    action_ready: bool = True
    recovery: str = "ready"
    observed: dict[str, set[str]] = field(default_factory=dict)

    @property
    def alive(self) -> bool:
        return self.hp > 0


def play_stats() -> dict[str, int]:
    return {"uses": 0, "successes": 0, "damage": 0, "actions_spent": 0}


def fresh_metrics() -> dict[str, Any]:
    return {
        "fights": 0, "focal_wins": 0, "opposition_wins": 0, "double_defeats": 0,
        "draws": 0, "rounds": 0, "exchanges": 0, "damage": 0,
        "actions_spent": 0, "actions_preserved": 0,
        "choices": Counter(), "contact": Counter(), "engagement": Counter(), "point_threat": Counter(),
        "recovery_states": 0, "soft_binds": 0,
        "durch_opportunities": 0, "durch_declarations": 0, "durch_declines": 0,
        "durch_successes": 0, "durch_damage": 0, "durch_roles": Counter(),
        "unsafe_blade_seeking_selected": 0, "unsafe_avoided_after_durch_reveal": 0,
        "schiel_opportunities": 0, "schiel_declarations": 0, "schiel_long_point_activations": 0,
        "durch_into_known_schiel": 0, "durch_avoided_known_schiel": 0,
        "decisions_altered_by_repertoire": 0,
        "knowledge_splits": {
            "before_durch_reveal": Counter(), "after_durch_reveal": Counter(),
            "before_schiel_reveal": Counter(), "after_schiel_reveal": Counter(),
        },
        "chain_distribution": Counter(), "cap_sequences": Counter(), "attempted_fourth_sequences": Counter(),
        "plays": {play: play_stats() for play in PLAYS},
        "s2_cases": Counter({"both_fail_unreachable_original_schiel_reused": 0}), "precondition_violations": 0,
    }


class Arena:
    def __init__(self, rng: random.Random, policy_rng: random.Random, model: dict[str, Any], information: str,
                 schiel_variant: str, parry_policy: str, trigger_model: str,
                 scenario: str, available: set[str], metrics: dict[str, Any]):
        self.rng = rng
        self.policy_rng = policy_rng
        self.model = model
        self.information = information
        self.schiel_variant = schiel_variant
        self.parry_policy = parry_policy
        self.trigger_model = trigger_model
        self.metrics = metrics
        self.current_chain: list[str] = []
        if scenario == "duel":
            self.fighters = [Fighter("A", "focal", set(available)), Fighter("B", "opposition", set(available))]
        else:
            self.fighters = [Fighter("A", "focal", set(available)), Fighter("B", "opposition", set(available)), Fighter("C", "opposition", set(available))]
        for fighter in self.fighters:
            fighter.observed = {other.fighter_id: set() for other in self.fighters if other is not fighter}
            if information == "perfect_information":
                for other in self.fighters:
                    if other is not fighter:
                        fighter.observed[other.fighter_id] = set(other.available)
        self.contact: dict[tuple[str, str], str] = {}

    def roll_result(self, fighter: Fighter, bane: bool = False) -> int:
        first = self.rng.randint(1, 20)
        return max(first, self.rng.randint(1, 20)) if bane else first

    def success(self, fighter: Fighter, bane: bool = False) -> tuple[bool, int]:
        result = self.roll_result(fighter, bane)
        return result <= fighter.skill, result

    def damage_roll(self) -> int:
        return self.rng.randint(1, 6) + 1

    def known(self, observer: Fighter, target: Fighter, play: str) -> bool:
        if self.information == "naive":
            return False
        return play in observer.observed[target.fighter_id]

    def observed(self, observer: Fighter, target: Fighter, play: str) -> bool:
        return play in observer.observed[target.fighter_id]

    def reveal(self, actor: Fighter, play: str) -> None:
        for observer in self.fighters:
            if observer is not actor and observer.alive:
                observer.observed[actor.fighter_id].add(play)

    def split(self, observer: Fighter, target: Fighter, key: str, amount: int = 1) -> None:
        d = "after_durch_reveal" if self.observed(observer, target, DURCH) else "before_durch_reveal"
        s = "after_schiel_reveal" if self.observed(observer, target, SCHIEL) else "before_schiel_reveal"
        self.metrics["knowledge_splits"][d][key] += amount
        self.metrics["knowledge_splits"][s][key] += amount

    def softmax(self, values: dict[str, float], temperature: float = 0.32) -> str:
        top = max(values.values())
        weights = {key: math.exp((value - top) / temperature) for key, value in values.items()}
        pick = self.policy_rng.random() * sum(weights.values())
        for key, weight in weights.items():
            pick -= weight
            if pick <= 0:
                return key
        return next(reversed(values))

    def spend(self, fighter: Fighter, play: str | None = None) -> None:
        if not fighter.action_ready:
            self.metrics["precondition_violations"] += 1
            return
        fighter.action_ready = False
        self.metrics["actions_spent"] += 1
        if play:
            self.metrics["plays"][play]["actions_spent"] += 1

    def hurt(self, target: Fighter, amount: int, play: str | None = None) -> None:
        target.hp -= amount
        self.metrics["damage"] += amount
        if play:
            self.metrics["plays"][play]["damage"] += amount
            if play == DURCH:
                self.metrics["durch_damage"] += amount

    def add_play(self, play: str) -> bool:
        if len(self.current_chain) >= 3:
            self.metrics["attempted_fourth_sequences"][tuple(self.current_chain + [play])] += 1
            return False
        self.current_chain.append(play)
        self.metrics["plays"][play]["uses"] += 1
        return True

    def use_play(self, actor: Fighter, play: str) -> bool:
        if not self.add_play(play):
            return False
        self.reveal(actor, play)
        return True

    def set_contact(self, first: Fighter, second: Fighter, state: str) -> None:
        self.contact[tuple(sorted((first.fighter_id, second.fighter_id)))] = state
        if state != "none":
            self.metrics["contact"][state] += 1

    def record_state(self, intent: str, point: str) -> None:
        self.metrics["engagement"][intent] += 1
        self.metrics["point_threat"][point] += 1

    def deal_basic_attack(self, attacker: Fighter, defender: Fighter, attribution: str | None) -> None:
        self.hurt(defender, self.damage_roll(), attribution)

    def choose_attack(self, actor: Fighter, target: Fighter) -> dict[str, str]:
        values = {"thrust": 0.25, "descending-cut": 0.30, "other-cut": 0.22, "proactive-beat": -0.12}
        if self.known(actor, target, SCHIEL):
            values["descending-cut"] -= 0.34
        if self.known(actor, target, DURCH):
            values["proactive-beat"] -= 0.72
        selected = self.softmax(values, 0.55)
        if (self.known(actor, target, SCHIEL) or self.known(actor, target, DURCH)) and selected != max({"thrust": .25, "descending-cut": .30, "other-cut": .22, "proactive-beat": -.12}, key={"thrust": .25, "descending-cut": .30, "other-cut": .22, "proactive-beat": -.12}.get):
            self.metrics["decisions_altered_by_repertoire"] += 1
        return {
            "type": selected,
            "line": "high" if selected == "descending-cut" else "center",
            "commitment": "committed" if selected == "descending-cut" and self.rng.random() < .75 else "ready",
        }

    def durch_decision(self, actor: Fighter, opponent: Fighter, role: str, into_schiel: bool = False) -> bool:
        self.metrics["durch_opportunities"] += 1
        self.metrics["durch_roles"][f"opportunity:{role}"] += 1
        self.split(actor, opponent, "durch_opportunities")
        attempt_value = 0.34
        if into_schiel:
            if self.known(actor, opponent, SCHIEL):
                attempt_value = {"S1": -0.92, "S2": -0.12, "S3": -0.38}[self.schiel_variant]
            else:
                attempt_value = 0.05
        declare = self.softmax({"declare": attempt_value, "decline": -0.05 if not into_schiel else -0.42}, .42) == "declare"
        if not declare:
            self.metrics["durch_declines"] += 1
            self.metrics["durch_roles"][f"decline:{role}"] += 1
            self.split(actor, opponent, "durch_declines")
            if into_schiel and self.known(actor, opponent, SCHIEL):
                self.metrics["durch_avoided_known_schiel"] += 1
            return False
        if not self.use_play(actor, DURCH):
            return False
        self.metrics["durch_declarations"] += 1
        self.metrics["durch_roles"][f"declaration:{role}"] += 1
        self.split(actor, opponent, "durch_declarations")
        if into_schiel and self.known(actor, opponent, SCHIEL):
            self.metrics["durch_into_known_schiel"] += 1
        return True

    def resolve_durch_roll(self, actor: Fighter, opponent: Fighter, bane: bool = False) -> bool:
        ok, _ = self.success(actor, bane)
        if ok:
            self.metrics["durch_successes"] += 1
            self.metrics["plays"][DURCH]["successes"] += 1
            self.hurt(opponent, self.damage_roll(), DURCH)
        return ok

    def durch_remedy_to_beat(self, attacker: Fighter, defender: Fighter) -> None:
        # PROVISIONAL ATRA GENERALIZATION FROM SOURCED PRINCIPLE.
        self.record_state("blade_seeking", "not_threatening")
        if defender.action_ready and DURCH in defender.available and self.durch_decision(defender, attacker, "remedy"):
            self.spend(defender, DURCH)
            if self.resolve_durch_roll(defender, attacker):
                return
        self.deal_basic_attack(attacker, defender, None)

    def defence_values(self, attacker: Fighter, defender: Fighter, attack: dict[str, str]) -> dict[str, float]:
        values = {"ignore": -0.72, "counter": -0.18, "parry_safe": 0.02}
        # Documented experimental subset: explicit blade-chase is available only
        # against the otherwise-unclassified other-cut, never inferred for all Parries.
        if attack["type"] == "other-cut":
            values["parry_unsafe"] = -0.35
        if self.known(defender, attacker, DURCH) and "parry_unsafe" in values:
            values["parry_unsafe"] -= 0.92
        if attack["type"] == "thrust":
            if ABSETZEN in defender.available: values[ABSETZEN] = .55
            if SCIAMBIAR in defender.available: values[SCIAMBIAR] = .55
        if attack["type"] == "descending-cut":
            if ZORN in defender.available and attack["commitment"] == "committed": values[ZORN] = .29
            if SCHIEL in defender.available: values[SCHIEL] = .60
        if self.parry_policy == "legacy_random_half":
            values.pop("parry_unsafe", None)
            values["parry_legacy"] = .04 - (.42 if self.known(defender, attacker, DURCH) else 0)
        return values

    def basic_parry(self, attacker: Fighter, defender: Fighter, attribution: str | None, unsafe: bool) -> None:
        self.metrics["choices"]["Parry"] += 1
        self.spend(defender)
        self.record_state("blade_seeking" if unsafe else "body_threat", "not_threatening" if unsafe else "unknown")
        if unsafe:
            self.metrics["unsafe_blade_seeking_selected"] += 1
            self.split(defender, attacker, "unsafe_selected")
            legal = DURCH in attacker.available
            if legal and self.trigger_model in ("state", "old") and self.durch_decision(attacker, defender, "continuation"):
                if self.resolve_durch_roll(attacker, defender):
                    return
        ok, _ = self.success(defender)
        if ok:
            close = self.rng.random() < self.model["simulation_model"]["close_crossing_probability"]
            self.set_contact(attacker, defender, "close-crossing" if close else "bind-crossing")
        else:
            self.deal_basic_attack(attacker, defender, attribution)

    def combined_remedy(self, play: str, attacker: Fighter, defender: Fighter, attribution: str | None) -> None:
        if not self.use_play(defender, play):
            self.deal_basic_attack(attacker, defender, attribution); return
        self.spend(defender, play)
        self.record_state("blade_seeking", "threatening")
        # Old model treated every named blade-seeking remedy as vulnerable; new model denies on point threat.
        if self.trigger_model == "old" and DURCH in attacker.available and self.durch_decision(attacker, defender, "continuation"):
            if self.resolve_durch_roll(attacker, defender): return
        ok, _ = self.success(defender)
        if ok:
            self.metrics["plays"][play]["successes"] += 1
            self.set_contact(attacker, defender, "bind-crossing")
            self.hurt(attacker, self.damage_roll(), play)
        else:
            self.deal_basic_attack(attacker, defender, attribution)

    def zorn(self, attacker: Fighter, defender: Fighter, attribution: str | None) -> None:
        if not self.use_play(defender, ZORN): self.deal_basic_attack(attacker, defender, attribution); return
        self.spend(defender, ZORN)
        self.record_state("blade_seeking", "unknown")
        if self.trigger_model == "old" and DURCH in attacker.available and self.durch_decision(attacker, defender, "continuation"):
            if self.resolve_durch_roll(attacker, defender): return
        ok, _ = self.success(defender)
        if not ok: self.deal_basic_attack(attacker, defender, attribution); return
        self.metrics["plays"][ZORN]["successes"] += 1
        self.set_contact(attacker, defender, "bind-crossing")
        if self.rng.random() < self.model["simulation_model"]["soft_bind_probability"]:
            self.metrics["soft_binds"] += 1
            self.record_state("not_applicable", "threatening")
            point_ok, _ = self.success(defender)
            if point_ok: self.hurt(attacker, self.damage_roll(), ZORN)

    def schiel(self, attacker: Fighter, defender: Fighter, attribution: str | None) -> None:
        self.metrics["schiel_opportunities"] += 1
        self.split(defender, attacker, "schiel_opportunities")
        if not self.use_play(defender, SCHIEL): self.deal_basic_attack(attacker, defender, attribution); return
        self.metrics["schiel_declarations"] += 1
        self.split(defender, attacker, "schiel_declarations")
        self.spend(defender, SCHIEL)
        self.record_state("blade_seeking", "unknown")
        schiel_ok, schiel_roll = self.success(defender)
        if not schiel_ok:
            self.deal_basic_attack(attacker, defender, attribution); return
        # Consequences wait here while the sourced attempted change-through is considered.
        attempted = DURCH in attacker.available and self.durch_decision(attacker, defender, "rejoinder", into_schiel=True)
        if attempted:
            self.metrics["schiel_long_point_activations"] += 1
            self.record_state("body_threat", "threatening")
            if self.schiel_variant == "S1":
                durch_wins = False
            elif self.schiel_variant == "S2":
                durch_ok, durch_roll = self.success(attacker)
                if not durch_ok:
                    self.metrics["s2_cases"]["schiel_only_success"] += 1
                    durch_wins = False
                elif durch_roll < schiel_roll:
                    self.metrics["s2_cases"]["both_success_durch_lower"] += 1
                    durch_wins = True
                elif durch_roll == schiel_roll:
                    self.metrics["s2_cases"]["both_success_tie_schiel"] += 1
                    durch_wins = False
                else:
                    self.metrics["s2_cases"]["both_success_schiel_lower"] += 1
                    durch_wins = False
            else:
                durch_wins, _ = self.success(attacker, bane=True)
            if durch_wins:
                self.metrics["durch_successes"] += 1
                self.metrics["plays"][DURCH]["successes"] += 1
                self.hurt(defender, self.damage_roll(), DURCH)
                return
        self.metrics["plays"][SCHIEL]["successes"] += 1
        self.hurt(attacker, self.damage_roll(), SCHIEL)

    def defend(self, attacker: Fighter, defender: Fighter, attack: dict[str, str], attribution: str | None) -> None:
        if not defender.action_ready:
            self.deal_basic_attack(attacker, defender, attribution); return
        values = self.defence_values(attacker, defender, attack)
        choice = self.softmax(values)
        if self.known(defender, attacker, DURCH) and "parry_unsafe" in values and choice != "parry_unsafe":
            self.metrics["unsafe_avoided_after_durch_reveal"] += 1
            self.metrics["decisions_altered_by_repertoire"] += 1
        self.split(defender, attacker, f"defence:{choice}")
        if choice == "ignore":
            self.metrics["choices"]["Ignore"] += 1
            self.deal_basic_attack(attacker, defender, attribution)
        elif choice == "counter":
            self.metrics["choices"]["Counter"] += 1
            self.spend(defender)
            self.record_state("body_threat", "threatening")
            self.deal_basic_attack(attacker, defender, attribution)
            ok, _ = self.success(defender)
            if ok: self.hurt(attacker, self.damage_roll(), None)
        elif choice in ("parry_safe", "parry_unsafe", "parry_legacy"):
            unsafe = choice == "parry_unsafe" or (choice == "parry_legacy" and self.rng.random() < .5)
            self.basic_parry(attacker, defender, attribution, unsafe)
        elif choice in (ABSETZEN, SCIAMBIAR):
            self.combined_remedy(choice, attacker, defender, attribution)
        elif choice == ZORN:
            self.zorn(attacker, defender, attribution)
        else:
            self.schiel(attacker, defender, attribution)

    def pommel(self, actor: Fighter, target: Fighter) -> bool:
        pair = tuple(sorted((actor.fighter_id, target.fighter_id)))
        if POMMEL not in actor.available or self.contact.get(pair) != "close-crossing": return False
        if self.softmax({"pommel": .42, "ordinary": .0}, .42) != "pommel": return False
        if not self.use_play(actor, POMMEL): return False
        self.spend(actor, POMMEL)
        self.record_state("not_applicable", "not_threatening")
        ok, _ = self.success(actor)
        if ok:
            self.metrics["plays"][POMMEL]["successes"] += 1
            self.hurt(target, self.damage_roll(), POMMEL)
        self.set_contact(actor, target, "none")
        return True

    def choose_target(self, actor: Fighter) -> Fighter | None:
        enemies = [f for f in self.fighters if f.alive and f.side != actor.side]
        return self.rng.choice(enemies) if enemies else None

    def activate(self, actor: Fighter) -> None:
        target = self.choose_target(actor)
        if not target: return
        self.current_chain = []
        if self.pommel(actor, target):
            self.finish_exchange(); return
        attribution = None
        if NACH in actor.available and target.recovery == "recovering-from-missed-committed-cut" and self.softmax({"nach": .52, "ordinary": 0}, .42) == "nach":
            self.use_play(actor, NACH); attribution = NACH; target.recovery = "ready"
            attack = {"type": "descending-cut", "line": "high", "commitment": "committed"}
            self.spend(actor, NACH)
        else:
            attack = self.choose_attack(actor, target)
            self.spend(actor)
        self.set_contact(actor, target, "none")
        if attack["type"] == "proactive-beat":
            self.durch_remedy_to_beat(actor, target); self.finish_exchange(); return
        actor.recovery = "committed" if attack["commitment"] == "committed" else "ready"
        attack_ok, _ = self.success(actor)
        if not attack_ok:
            if attack["type"] == "descending-cut" and attack["commitment"] == "committed":
                actor.recovery = "recovering-from-missed-committed-cut"
                self.metrics["recovery_states"] += 1
            self.finish_exchange(); return
        if attribution: self.metrics["plays"][attribution]["successes"] += 1
        self.defend(actor, target, attack, attribution)
        if actor.alive and actor.recovery != "recovering-from-missed-committed-cut": actor.recovery = "ready"
        self.finish_exchange()

    def finish_exchange(self) -> None:
        length = len(self.current_chain)
        self.metrics["exchanges"] += 1
        self.metrics["chain_distribution"][length] += 1
        if length == 3: self.metrics["cap_sequences"][tuple(self.current_chain)] += 1
        self.current_chain = []

    def outcome(self) -> str | None:
        focal = any(f.alive and f.side == "focal" for f in self.fighters)
        opposition = any(f.alive and f.side == "opposition" for f in self.fighters)
        if focal and opposition: return None
        if not focal and not opposition: return "double"
        return "focal" if focal else "opposition"

    def run(self, max_rounds: int = 100) -> tuple[str, int]:
        for round_no in range(1, max_rounds + 1):
            for fighter in self.fighters:
                if fighter.alive: fighter.action_ready = True
            order = [f for f in self.fighters if f.alive]
            self.rng.shuffle(order)
            for fighter in order:
                if fighter.alive and fighter.action_ready and self.choose_target(fighter): self.activate(fighter)
                outcome = self.outcome()
                if outcome: return outcome, round_no
        return "draw", max_rounds


def serial(value: Any) -> Any:
    if isinstance(value, Counter):
        return {" > ".join(key) if isinstance(key, tuple) else str(key): count for key, count in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, dict): return {str(k): serial(v) for k, v in value.items()}
    return value


def finalize(metrics: dict[str, Any]) -> dict[str, Any]:
    f = metrics["fights"]; e = metrics["exchanges"] or 1
    out = serial(metrics)
    out.update({
        "focal_win_rate": metrics["focal_wins"] / f,
        "symmetry_deviation": abs(metrics["focal_wins"] - metrics["opposition_wins"]) / f,
        "average_fight_length": metrics["rounds"] / f,
        "double_defeat_rate": metrics["double_defeats"] / f,
        "actions_spent_per_fight": metrics["actions_spent"] / f,
        "actions_preserved_per_fight": metrics["actions_preserved"] / f,
        "basic_parry_frequency": metrics["choices"]["Parry"] / e,
        "counter_frequency": metrics["choices"]["Counter"] / e,
        "ignore_frequency": metrics["choices"]["Ignore"] / e,
        "schielhau_frequency": metrics["schiel_declarations"] / e,
        "bind_crossing_frequency": metrics["contact"]["bind-crossing"] / e,
        "close_crossing_frequency": metrics["contact"]["close-crossing"] / e,
        "recovery_state_frequency": metrics["recovery_states"] / e,
        "blade_seeking_engagement_frequency": metrics["engagement"]["blade_seeking"] / e,
        "point_threatening_engagement_frequency": metrics["point_threat"]["threatening"] / e,
        "point_not_threatening_engagement_frequency": metrics["point_threat"]["not_threatening"] / e,
        "durch_declaration_rate": metrics["durch_declarations"] / metrics["durch_opportunities"] if metrics["durch_opportunities"] else 0,
        "durch_decline_rate": metrics["durch_declines"] / metrics["durch_opportunities"] if metrics["durch_opportunities"] else 0,
        "durch_success_rate": metrics["durch_successes"] / metrics["durch_declarations"] if metrics["durch_declarations"] else 0,
        "schiel_long_point_frequency": metrics["schiel_long_point_activations"] / e,
        "average_learned_play_chain": sum(k * v for k, v in metrics["chain_distribution"].items()) / e,
        "three_play_cap_frequency": metrics["chain_distribution"][3] / e,
        "attempted_fourth_play_frequency": sum(metrics["attempted_fourth_sequences"].values()) / e,
    })
    for play, stats in out["plays"].items():
        raw = metrics["plays"][play]
        stats["uses_per_fight"] = raw["uses"] / f
        stats["success_rate"] = raw["successes"] / raw["uses"] if raw["uses"] else 0
        stats["damage_per_fight"] = raw["damage"] / f
        stats["damage_share"] = raw["damage"] / metrics["damage"] if metrics["damage"] else 0
    return out


def run_cell(model: dict[str, Any], trials: int, seed: int, information: str, schiel_variant: str,
             scenario: str = "duel", available: set[str] | None = None,
             parry_policy: str = "documented_subset", trigger_model: str = "state") -> dict[str, Any]:
    metrics = fresh_metrics(); rng = random.Random(seed); available = set(PLAYS) if available is None else set(available)
    for _ in range(trials):
        policy_rng = random.Random((seed ^ model["simulation_model"]["policy_seed"]) + metrics["fights"] * 65537)
        arena = Arena(rng, policy_rng, model, information, schiel_variant, parry_policy, trigger_model, scenario, available, metrics)
        outcome, rounds = arena.run()
        metrics["fights"] += 1; metrics["rounds"] += rounds
        metrics[{"focal": "focal_wins", "opposition": "opposition_wins", "double": "double_defeats", "draw": "draws"}[outcome]] += 1
    return finalize(metrics)


def friendly_sequence(raw: str) -> str:
    return " → ".join(SHORT.get(part, part) for part in raw.split(" > "))


def build_report(results: dict[str, Any]) -> str:
    lines = [
        "# Durchwechseln–Schielhau State-Model Results", "",
        "Status: **PROVISIONAL experiment; not canonical mechanics**", "",
        "Historical identity/source evidence for Durchwechseln and Schielhau (including Schielhau's intrinsic long-point branch) remains **HISTORICALLY ACCEPTED: EARLIER / A**. Every mechanic, state label, exchange role, policy, opposed procedure, Bane procedure, and prototype-Play point classification below is **PROVISIONAL**. Spiritus costs, final tiers, final text, universal Parry taxonomy, bind mechanics, engagement geometry, weapon profiles, and final chain architecture remain **OPEN**.", "",
        "## Historical boundary and scoped state audit", "",
        "- Durchwechseln preserves the single audited Pseudo-Peter von Danzig witness, Starhemberg Fechtbuch Cod.44.A.8, ff. 30v.3–31r.2. No additional witness is claimed.",
        "- Schielhau preserves Pseudo-Peter von Danzig, Cod.44.A.8, ff. 23v.1–23v.2, historical names `Schilär` / `Schilhaw`, normalized Atra name Schielhau, and historical classification `meisterhau` / `master strike`. “Master strike” is not used as its procedural chassis.",
        "- The Schielhau long-point denial is intrinsic: it is not another action, another learned Play, a generic Counter-Feint, or a follow-up after arbitrary Parries.", "",
        "| Play / phase | Seeks or contacts blade? | Engagement intent | Point threat | Generalized Durchwechseln | Basis |", "|---|---|---|---|---|---|",
        "| Absetzen: joined set-aside/thrust | Yes | blade-seeking | threatening | unavailable | directly supported |",
        "| Zornhau-Ort: pre-bind counter-cut | Yes | blade-seeking | unknown | uncertain; suppressed | uncertain |",
        "| Zornhau-Ort: soft-bind point | Yes | not applicable | threatening | unavailable (bind) | directly supported |",
        "| Durchwechseln: point change | No | body-threat | threatening | executing, not a target | directly supported |",
        "| Scambiar di Punta: crossing counter-thrust | Yes | blade-seeking | threatening | unavailable | directly supported |",
        "| Nachreisen: recovery pursuit | No | body-threat | not threatening | unavailable (no weapon commitment) | directly supported |",
        "| Pommel Strike: close crossing | Not separable | not applicable | not threatening | unavailable (close contact) | directly supported |",
        "| Schielhau: transient declaration window | Yes | blade-seeking | unknown | uncertain; admitted only to test sourced branch | uncertain staging |",
        "| Schielhau: established intrinsic long point | No | body-threat | threatening | unavailable / denied | directly supported |", "",
        "## Model and policy", "",
        "The state trigger is `contact=none` + opponent commitment toward the user's weapon (`blade_seeking`) + opponent `point_threat=not_threatening`. It is not keyed to Parry or any Play name. Absetzen and Scambiar deny the trigger by maintaining a threatening point. Zornhau-Ort's pre-bind point state remains uncertain and is not made vulnerable by inference. A proactive beat exists only as **PROVISIONAL ATRA GENERALIZATION FROM SOURCED PRINCIPLE** to exercise Durchwechseln as a Remedy.", "",
        "Choices use expected-value softmax (temperature 0.32 for defence, 0.42–0.55 elsewhere) over the legal menu. Knowledge changes option utilities rather than banning options, and a separate seeded policy stream preserves mixed behavior. Adaptive fighters begin with neither hidden Play known; observation sets `durchwechseln_known` and `schielhau_known` separately for the rest of that fight. Naive policies never use observed knowledge. Perfect-information policies start with both flags set.", "",
        "S1 automatically denies Throughchanging after a successful Schielhau establishes long point. S2 reuses the original successful Schielhau d20 and compares it to one fresh Durchwechseln d20: lower successful roll wins; ties favor the established Schielhau opposition; one success beats failure. Because entry requires a successful Schielhau, the two-fail case is unreachable under reuse (and is recorded as zero). S3 rolls Durchwechseln with one Bane (2d20, keep higher), without stacking.", "",
        "## Main mirrored duel matrix", "",
        "| Information | Variant | Focal win | Symmetry deviation | Rounds | Double defeat | Parry | Counter | Ignore | Schielhau | Durch opp./fight | Declare | Decline | Durch success | Long-point/exchange | Avg chain | Cap | Fourth |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for info in INFO:
        for variant in SCHIEL_VARIANTS:
            c = results["main"][info][variant]
            lines.append(f"| {info} | {variant} | {c['focal_win_rate']:.2%} | {c['symmetry_deviation']:.2%} | {c['average_fight_length']:.3f} | {c['double_defeat_rate']:.2%} | {c['basic_parry_frequency']:.2%} | {c['counter_frequency']:.2%} | {c['ignore_frequency']:.2%} | {c['schielhau_frequency']:.2%} | {c['durch_opportunities']/c['fights']:.3f} | {c['durch_declaration_rate']:.2%} | {c['durch_decline_rate']:.2%} | {c['durch_success_rate']:.2%} | {c['schiel_long_point_frequency']:.2%} | {c['average_learned_play_chain']:.3f} | {c['three_play_cap_frequency']:.3%} | {c['attempted_fourth_play_frequency']:.3%} |")
    lines += ["", "### Per-Play results for every main cell", "", "| Information | Variant | Play | Uses/fight | Success | Damage/fight | Total damage |", "|---|---|---|---:|---:|---:|---:|"]
    for info in INFO:
        for variant in SCHIEL_VARIANTS:
            for play in PLAYS:
                p = results["main"][info][variant]["plays"][play]
                lines.append(f"| {info} | {variant} | {SHORT[play]} | {p['uses_per_fight']:.3f} | {p['success_rate']:.2%} | {p['damage_per_fight']:.3f} | {p['damage_share']:.2%} |")
    lines += ["", "### Prototype-state and action frequencies", "", "| Information | Variant | Actions spent | Preserved | Bind | Close | Recovery | Blade-seeking | Point threatening | Point not threatening |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for info in INFO:
        for variant in SCHIEL_VARIANTS:
            c = results["main"][info][variant]
            lines.append(f"| {info} | {variant} | {c['actions_spent_per_fight']:.3f} | {c['actions_preserved_per_fight']:.3f} | {c['bind_crossing_frequency']:.2%} | {c['close_crossing_frequency']:.2%} | {c['recovery_state_frequency']:.2%} | {c['blade_seeking_engagement_frequency']:.2%} | {c['point_threatening_engagement_frequency']:.2%} | {c['point_not_threatening_engagement_frequency']:.2%} |")
    lines += ["", "## Deterrence and adaptive revelation", "", "| Variant | Unsafe selected | Unsafe avoided after D reveal | D attempts into known Schiel | D avoided due known Schiel | Altered decisions/fight |", "|---|---:|---:|---:|---:|---:|"]
    for variant in SCHIEL_VARIANTS:
        c = results["main"]["adaptive_revelation"][variant]
        lines.append(f"| {variant} | {c['unsafe_blade_seeking_selected']/c['fights']:.3f} | {c['unsafe_avoided_after_durch_reveal']/c['fights']:.3f} | {c['durch_into_known_schiel']/c['fights']:.3f} | {c['durch_avoided_known_schiel']/c['fights']:.3f} | {c['decisions_altered_by_repertoire']/c['fights']:.3f} |")
    lines += ["", "### Adaptive before/after reveal splits", "", "Counts are per fight and each event is split independently around Durchwechseln and Schielhau revelation.", "", "| Variant | Reveal split | D opportunities | D declarations | D declines | Unsafe selected | Schiel opportunities | Schiel declarations |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    for variant in SCHIEL_VARIANTS:
        c = results["main"]["adaptive_revelation"][variant]
        for split in ("before_durch_reveal", "after_durch_reveal", "before_schiel_reveal", "after_schiel_reveal"):
            k = c["knowledge_splits"][split]; fights = c["fights"]
            lines.append(f"| {variant} | {split} | {k.get('durch_opportunities', 0)/fights:.3f} | {k.get('durch_declarations', 0)/fights:.3f} | {k.get('durch_declines', 0)/fights:.3f} | {k.get('unsafe_selected', 0)/fights:.3f} | {k.get('schiel_opportunities', 0)/fights:.3f} | {k.get('schiel_declarations', 0)/fights:.3f} |")
    lines += ["", "## Basic Parry limitation and decomposition", "", "The prior v0.2 simulator did **not** treat every basic Parry as blade-seeking: it assigned blade-seeking randomly to 50% of successful basic Parries. It had no point-threat state and could not distinguish a body-covering defence from a blade-chasing defence. It therefore neither preserved nor abandoned point threat in represented state. It also treated every Absetzen, Scambiar, and Zornhau-Ort as vulnerable. `legacy_random_half` preserves that limitation. `documented_subset` is the explicitly documented experimental alternative: body-cover is always available, while a blade-chase subtype is offered only against the simulator's otherwise-unclassified `other-cut`; this is a policy proxy, not a canonical or universal Parry taxonomy.", "", "| Cell | Durch damage/fight | Durch opp./fight | Declare | Unsafe/fight | Rounds |", "|---|---:|---:|---:|---:|---:|"]
    for label, c in results["decomposition"].items():
        lines.append(f"| {label} | {c['plays'][DURCH]['damage_per_fight']:.3f} | {c['durch_opportunities']/c['fights']:.3f} | {c['durch_declaration_rate']:.2%} | {c['unsafe_blade_seeking_selected']/c['fights']:.3f} | {c['average_fight_length']:.3f} |")
    lines += ["", "## Adaptive ablations (mirrored)", "", "| Variant | Repertoire | Focal win | Rounds | Durch damage | Schiel damage | Play damage/fight |", "|---|---|---:|---:|---:|---:|---:|"]
    for variant in SCHIEL_VARIANTS:
        for label, c in results["ablations"][variant].items():
            play_damage = sum(p["damage_per_fight"] for p in c["plays"].values())
            lines.append(f"| {variant} | {label} | {c['focal_win_rate']:.2%} | {c['average_fight_length']:.3f} | {c['plays'][DURCH]['damage_per_fight']:.3f} | {c['plays'][SCHIEL]['damage_per_fight']:.3f} | {play_damage:.3f} |")
    lines += ["", "## One-versus-two exploratory results", "", "No generic anti-outnumbered bonus is used; all combatants have the same repertoire. These cells are exploratory because pair selection and contact are abstract and engagement geometry remains OPEN.", "", "| Information | Variant | Focal win | Rounds | Double defeat | Durch damage/fight | Schiel damage/fight |", "|---|---|---:|---:|---:|---:|---:|"]
    for info in INFO:
        for variant in SCHIEL_VARIANTS:
            c = results["outnumbering"][info][variant]
            lines.append(f"| {info} | {variant} | {c['focal_win_rate']:.2%} | {c['average_fight_length']:.3f} | {c['double_defeat_rate']:.2%} | {c['plays'][DURCH]['damage_per_fight']:.3f} | {c['plays'][SCHIEL]['damage_per_fight']:.3f} |")
    full = results["main"]["adaptive_revelation"]["S2"]
    lines += ["", "## Play-chain stress", "", "| 0 learned | 1 learned | 2 learned | 3 learned |", "|---:|---:|---:|---:|", f"| {full['chain_distribution'].get('0', 0)/full['exchanges']:.2%} | {full['chain_distribution'].get('1', 0)/full['exchanges']:.2%} | {full['chain_distribution'].get('2', 0)/full['exchanges']:.2%} | {full['chain_distribution'].get('3', 0)/full['exchanges']:.2%} |", "", "Exact cap sequences:"]
    if full["cap_sequences"]:
        lines.extend(f"- {friendly_sequence(seq)}: {count}" for seq, count in sorted(full["cap_sequences"].items(), key=lambda x: -x[1]))
    else: lines.append("- None.")
    lines += ["", f"Attempted fourth Plays: **{sum(full['attempted_fourth_sequences'].values())}**. Schielhau's intrinsic branch is never counted separately.", "", "## Answers to the experiment questions", ""]
    old = results["decomposition"]["old_trigger_naive_legacy"]
    state_naive = results["decomposition"]["state_trigger_naive_legacy"]
    state_adapt = results["decomposition"]["state_trigger_adaptive_legacy"]
    state_subset = results["decomposition"]["state_trigger_adaptive_documented_subset"]
    def reduction(a: float, b: float) -> float: return (a-b)/a if a else 0
    lines += [
        f"A. Replacing old named/blade-seeking vulnerability with point-aware state logic reduced Durchwechseln damage from {old['plays'][DURCH]['damage_per_fight']:.3f} to {state_naive['plays'][DURCH]['damage_per_fight']:.3f} per fight ({reduction(old['plays'][DURCH]['damage_per_fight'], state_naive['plays'][DURCH]['damage_per_fight']):.1%}). After adaptation, replacing the legacy random-half Parry label with the documented subset changed it from {state_adapt['plays'][DURCH]['damage_per_fight']:.3f} to {state_subset['plays'][DURCH]['damage_per_fight']:.3f} ({reduction(state_adapt['plays'][DURCH]['damage_per_fight'], state_subset['plays'][DURCH]['damage_per_fight']):.1%} reduction). These are sequential sensitivity effects, not causal estimates from a solved equilibrium.",
        f"B. Adaptive revelation changed Durchwechseln damage from {state_naive['plays'][DURCH]['damage_per_fight']:.3f} to {state_adapt['plays'][DURCH]['damage_per_fight']:.3f} under the same legacy Parry policy ({reduction(state_naive['plays'][DURCH]['damage_per_fight'], state_adapt['plays'][DURCH]['damage_per_fight']):.1%} reduction).",
        f"C. The state trigger produces {state_subset['plays'][DURCH]['uses_per_fight']:.3f} uses and {state_subset['plays'][DURCH]['damage_per_fight']:.3f} damage per fight in the adaptive documented-subset cell, versus {old['plays'][DURCH]['uses_per_fight']:.3f} and {old['plays'][DURCH]['damage_per_fight']:.3f} in the old-trigger cell.",
        "D. It remains usable as continuation, rejoinder, and remedy in the experiment; role-specific opportunity/declaration counts are machine-readable. Remedy use against the proactive beat is explicitly a provisional Atra generalization, not a claimed named witness.",
        "E. The only naturally vulnerable modeled actions are point-off-line blade chases and the provisional proactive beat. Zornhau-Ort remains uncertain rather than declared vulnerable.",
        "F. Absetzen, Scambiar di Punta, and established Schielhau long point naturally deny it by maintaining an immediate point threat; bind/close states also deny it.",
        "G. Schielhau supplies counterplay without removing Durchwechseln from other state-valid contexts; the ablations show their independent and joint contributions.",
        "H. S2 retains the most interactive branch; S1 maximizes deterrence and S3 maximizes continued attempt risk. The recommendation below remains provisional.",
        "I. No basic option reaches 100% or 0% across all relevant opportunities in the main matrix; the softmax policy avoids hard-coded never/always behavior. This is evidence about this policy, not a solved equilibrium.",
        "J. Direct damage is in per-Play tables; avoided unsafe defences, known-Schiel declines, and altered decisions report deterrence separately.",
        f"K. The cap binds in {full['three_play_cap_frequency']:.3%} of adaptive S2 exchanges; attempted fourth frequency is {full['attempted_fourth_play_frequency']:.3%}.",
        "L. Soft-bind probability, close-crossing generation, d6+1 damage, abstract pair contact in 1-v-2, absent engagement geometry, and heuristic policy utilities remain artifacts. None should be used for final tuning.",
        "", "## Recommended Next Decision", "",
        "- Continue prototype work with the state-based trigger and keep Durchwechseln unavailable against an already threatening point.",
        "- Use S2 opposed resolution as the next comparison baseline because it preserves visible counterplay without automatic denial; retain S1 and S3 as sensitivity bounds.",
        "- Specify a universal Parry taxonomy and engagement geometry before any balance promotion or Spiritus/tier decision.",
        "- Keep Zornhau-Ort's pre-bind point state uncertain until a dedicated geometry/source review resolves it.",
        "", f"Seeds: experiment `{results['seed']}`, policy/random stream included in each deterministic cell seed; configured policy seed `{results['policy_seed']}`. Main trials/cell: `{results['main_trials']}`; secondary trials/cell: `{results['secondary_trials']}`. Precondition violations in adaptive S2: `{full['precondition_violations']}`.", "",
    ]
    return "\n".join(lines)


def run_all(main_trials: int | None = None, secondary_trials: int | None = None,
            seed: int | None = None, write: bool = True) -> dict[str, Any]:
    model = json.loads(MODEL_PATH.read_text(encoding="utf-8")); cfg = model["simulation_model"]
    main_trials = main_trials or cfg["trials_per_main_cell"]; secondary_trials = secondary_trials or cfg["trials_per_secondary_cell"]
    seed = cfg["seed"] if seed is None else seed; index = 0
    def cell(trials: int, **kwargs: Any) -> dict[str, Any]:
        nonlocal index
        result = run_cell(model, trials, seed + index * 100003, **kwargs); index += 1; return result
    main = {info: {v: cell(main_trials, information=info, schiel_variant=v) for v in SCHIEL_VARIANTS} for info in INFO}
    decompositions = {
        "old_trigger_naive_legacy": cell(secondary_trials, information="naive", schiel_variant="S2", parry_policy="legacy_random_half", trigger_model="old"),
        "state_trigger_naive_legacy": cell(secondary_trials, information="naive", schiel_variant="S2", parry_policy="legacy_random_half", trigger_model="state"),
        "state_trigger_adaptive_legacy": cell(secondary_trials, information="adaptive_revelation", schiel_variant="S2", parry_policy="legacy_random_half", trigger_model="state"),
        "state_trigger_adaptive_documented_subset": cell(secondary_trials, information="adaptive_revelation", schiel_variant="S2", parry_policy="documented_subset", trigger_model="state"),
    }
    ablation_sets = {
        "full": set(PLAYS), "remove_durchwechseln": set(PLAYS)-{DURCH}, "remove_schielhau": set(PLAYS)-{SCHIEL}, "remove_both": set(PLAYS)-{DURCH, SCHIEL},
    }
    ablations = {v: {label: cell(secondary_trials, information="adaptive_revelation", schiel_variant=v, available=available) for label, available in ablation_sets.items()} for v in SCHIEL_VARIANTS}
    outnumbering = {info: {v: cell(secondary_trials, information=info, schiel_variant=v, scenario="one-versus-two") for v in SCHIEL_VARIANTS} for info in INFO}
    results = {"model_id": model["id"], "status": "PROVISIONAL", "seed": seed, "policy_seed": cfg["policy_seed"], "cell_seed_stride": 100003, "main_trials": main_trials, "secondary_trials": secondary_trials, "main": main, "decomposition": decompositions, "ablations": ablations, "outnumbering": outnumbering}
    if write:
        RESULTS_PATH.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        REPORT_PATH.write_text(build_report(results), encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--main-trials", type=int); parser.add_argument("--secondary-trials", type=int); parser.add_argument("--seed", type=int); parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(); results = run_all(args.main_trials, args.secondary_trials, args.seed, not args.no_write)
    for info in INFO:
        for v in SCHIEL_VARIANTS:
            c = results["main"][info][v]
            print(f"{info}/{v}: focal={c['focal_win_rate']:.3%} rounds={c['average_fight_length']:.3f} durch={c['plays'][DURCH]['damage_per_fight']:.3f} cap={c['three_play_cap_frequency']:.3%}")


if __name__ == "__main__": main()

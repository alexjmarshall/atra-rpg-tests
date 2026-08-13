"""Bounded integrated duel audit using the authoritative shared engine.

The policy layer receives immutable player-legitimate views. It never receives
the engine, hidden pressure, future dice, or raw unexposed rolls.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulations.shared.provisional_longsword import (  # noqa: E402
    ENGINE,
    CurrentEngine,
    Fighter,
    HART,
    LOWER,
    UNKNOWN,
    UPPER,
    WEICH,
)


SEED = 13082026
TRIALS = 2000
NORMAL_DAMAGE = tuple(range(2, 8))
FUHLEN = next(iter(ENGINE.FUHLEN_NAMES))
DM = ENGINE.PAIRED_PLAY
WINDEN = ENGINE.WINDEN_PLAY

L0 = frozenset()
L1 = frozenset({"Nachreisen"})
L2 = frozenset({WINDEN, FUHLEN})
L3 = frozenset({DM, FUHLEN})
L4 = frozenset({WINDEN, FUHLEN, DM, "Zornhau-Ort"})
L5 = frozenset(
    {
        WINDEN,
        FUHLEN,
        DM,
        "Zornhau-Ort",
        "Nachreisen",
        "Tutta Cover-to-Stretto",
        "Absetzen",
        "Scambiar di Punta",
        "Schielhau",
        "Durchwechseln",
    }
)


@dataclass(frozen=True)
class FighterView:
    name: str
    hp: int
    spiritus: int
    action_available: bool
    guard: str
    point_threat: str
    known_plays: tuple[str, ...]


@dataclass(frozen=True)
class PolicyView:
    actor: FighterView
    opponent: FighterView
    crossing: tuple[tuple[str, Any], ...]
    own_initial_pressure: str
    known_opponent_pressure: str
    public_history: tuple[str, ...]
    learned_chain_count: int
    legal_options: tuple[str, ...]


@dataclass(frozen=True)
class Policy:
    name: str
    objective: str
    hart_threshold: int = 4
    buy_fuhlen: bool = False
    prefer_bind: bool = False
    prefer_beat: bool = False
    prefer_counter: bool = False
    preserve_spiritus_below: int = 0
    adaptive: bool = False

    def pressure(self, view: PolicyView) -> str:
        if self.adaptive:
            known_hart = sum("pressure-revealed:hart" in e for e in view.public_history)
            known_weich = sum("pressure-revealed:weich" in e for e in view.public_history)
            if known_weich > known_hart:
                return WEICH
            if known_hart > known_weich:
                return HART
        if view.actor.hp <= self.hart_threshold or view.opponent.known_plays:
            return HART
        return WEICH

    def attack(self, view: PolicyView) -> str:
        options = set(view.legal_options)
        if "Power" in options and view.opponent.hp <= 7 and view.actor.hp > 3:
            return "Power"
        if "Basic Thrust" in options and view.opponent.point_threat == "not_threatening":
            if "Zornhau-Ort" in view.opponent.known_plays:
                return "Basic Thrust"
        return "Basic Cut" if "Basic Cut" in options else sorted(options)[0]

    def defence(self, view: PolicyView) -> str:
        options = set(view.legal_options)
        if self.prefer_bind and "Zornhau" in options:
            return "Zornhau"
        if self.prefer_counter and "Counter" in options and view.opponent.hp <= 4:
            return "Counter"
        if self.prefer_beat and "Beat" in options:
            return "Beat"
        if self.prefer_bind and "Cross" in options:
            return "Cross"
        if view.actor.hp <= 2 and "Cross" in options:
            return "Cross"
        if "Beat" in options and view.opponent.guard != "open" and not view.actor.known_plays:
            return "Beat"
        if "Cross" in options:
            return "Cross"
        return "Counter" if "Counter" in options else "Ignore"

    def rejoinder(self, view: PolicyView) -> str:
        options = set(view.legal_options)
        if (
            self.buy_fuhlen
            and "Fuhlen" in options
            and view.actor.spiritus >= 3
            and view.actor.spiritus > self.preserve_spiritus_below
        ):
            return "Fuhlen"
        known = view.known_opponent_pressure
        if known == HART and "Duplieren" in options:
            return "Duplieren"
        if known == WEICH and "Mutieren" in options:
            return "Mutieren"
        if view.actor.spiritus <= self.preserve_spiritus_below:
            return "decline"
        if "Duplieren" in options and "Mutieren" in options:
            if self.adaptive:
                hart = sum("pressure-revealed:hart" in e for e in view.public_history)
                weich = sum("pressure-revealed:weich" in e for e in view.public_history)
                if hart > weich:
                    return "Duplieren"
                if weich > hart:
                    return "Mutieren"
            return "Duplieren"
        return "decline"

    def continuation(self, view: PolicyView) -> str:
        options = set(view.legal_options)
        if view.actor.spiritus > self.preserve_spiritus_below:
            for option in ("Lower Winding Thrust", "Upper Winding Thrust"):
                if option in options:
                    return option
        return "Disengage" if "Disengage" in options else "pass"


POLICIES = {
    "survival": Policy("survival", "O3/O6 minimize incoming damage", hart_threshold=8, prefer_beat=True, preserve_spiritus_below=2),
    "bind": Policy("bind", "O1/O2 convert authored bind opportunities", hart_threshold=4, buy_fuhlen=True, prefer_bind=True),
    "temporal": Policy("temporal", "O2/O4 favor Counter/Power timing", hart_threshold=3, prefer_counter=True),
    "conserver": Policy("conserver", "O5 preserve Spiritus subject to survival", hart_threshold=4, prefer_beat=True, preserve_spiritus_below=4),
    "adaptive": Policy("adaptive", "O4 update only from public history", hart_threshold=4, buy_fuhlen=True, prefer_bind=True, adaptive=True),
}


@dataclass(frozen=True)
class Scenario:
    id: str
    question: str
    skill_a: int = 14
    skill_b: int = 14
    hp_a: int = 8
    hp_b: int = 8
    spiritus_a: int = 8
    spiritus_b: int = 8
    guard_a: str = "vom-tag"
    guard_b: str = "vom-tag"
    repertoire_a: frozenset[str] = L0
    repertoire_b: frozenset[str] = L0
    policy_a: str = "survival"
    policy_b: str = "survival"
    geometry: str = ENGINE.UPPER_CROSS
    max_rounds: int = 20


SCENARIOS = (
    Scenario("D1", "Basics-only mirror."),
    Scenario("D2", "Beat/Open emphasis.", policy_a="survival", policy_b="survival", guard_a="posta-di-donna", guard_b="posta-di-donna"),
    Scenario("D3", "Counter emphasis.", policy_a="temporal", policy_b="temporal"),
    Scenario("D4", "H3 bind-literate mirror.", repertoire_a=L2, repertoire_b=L2, policy_a="bind", policy_b="bind"),
    Scenario("D5", "D/M specialist versus Winden specialist.", repertoire_a=L3, repertoire_b=L2, policy_a="bind", policy_b="bind"),
    Scenario("D6", "Full German bind-slice mirror.", repertoire_a=L4, repertoire_b=L4, policy_a="adaptive", policy_b="bind"),
    Scenario("D7", "Zornhau user versus Basic-Cross user.", repertoire_a=frozenset({"Zornhau-Ort", FUHLEN, WINDEN}), repertoire_b=L0, policy_a="bind"),
    Scenario("D8", "Power/Nachreisen versus bind-literate.", repertoire_a=L1, repertoire_b=L2, guard_a="posta-di-donna", policy_a="temporal", policy_b="bind"),
    Scenario("D9", "Low-HP defender decision state.", hp_b=1, repertoire_a=L4, repertoire_b=L4, policy_a="bind", policy_b="survival"),
    Scenario("D10", "Low-Spiritus bind state.", spiritus_a=2, spiritus_b=1, repertoire_a=L4, repertoire_b=L4, policy_a="conserver", policy_b="conserver"),
    Scenario("D11", "Unknown-height ordinary Cross.", repertoire_a=L4, repertoire_b=L4, policy_a="bind", policy_b="bind", geometry=ENGINE.UNCLASSIFIED),
    Scenario("D12", "Lower-binding L2 transition duel.", repertoire_a=L2, repertoire_b=L2, policy_a="bind", policy_b="bind", geometry=ENGINE.LOWER_SETTING_ASIDE),
    Scenario("D13", "T1 opportunity state.", repertoire_a=L0, repertoire_b=frozenset({"Tutta Cover-to-Stretto"}), guard_b="tutta-porta-di-ferro", policy_b="bind"),
    Scenario("D14", "One fighter knows Winden; opponent does not.", repertoire_a=L2, repertoire_b=L0, policy_a="bind", policy_b="survival"),
    Scenario("D15", "Asymmetric Skill 10 versus 14.", skill_a=10, skill_b=14, repertoire_a=L4, repertoire_b=L4, policy_a="adaptive", policy_b="bind"),
)


def _freeze_mapping(value: dict[str, Any]) -> tuple[tuple[str, Any], ...]:
    return tuple(sorted((key, tuple(sorted(item.items())) if isinstance(item, dict) else item) for key, item in value.items()))


def make_policy_view(
    engine: CurrentEngine,
    actor: Fighter,
    legal_options: Iterable[str],
    public_history: Iterable[str],
) -> PolicyView:
    opponent = engine.other(actor)
    public = engine.public_crossing_state(actor)
    private = engine.fighter_private_crossing_state(actor)["initial_pressure"]
    return PolicyView(
        FighterView(actor.name, actor.hp, actor.spiritus, actor.action_available, actor.guard, actor.point_threat, tuple(sorted(actor.known_plays))),
        FighterView(opponent.name, opponent.hp, opponent.spiritus, opponent.action_available, opponent.guard, opponent.point_threat, tuple(sorted(opponent.known_plays))),
        _freeze_mapping(public),
        str(private.get(actor.name, UNKNOWN)),
        str(private.get(opponent.name, UNKNOWN)),
        tuple(public_history),
        len(engine.learned_chain),
        tuple(legal_options),
    )


def success_probability(skill: int, modifier: str = "normal") -> float:
    p = skill / 20
    if modifier == "boon":
        return 1 - (1 - p) ** 2
    if modifier == "bane":
        return p**2
    return p


def damage_distribution(mode: str = "normal") -> dict[int, float]:
    if mode == "fixed-7":
        return {7: 1.0}
    counts: Counter[int] = Counter()
    rolls = ((a, b) for a in range(1, 7) for b in range(1, 7)) if mode in {"damage_boon", "damage_bane"} else ((a,) for a in range(1, 7))
    for roll in rolls:
        if mode == "damage_boon":
            value = max(roll) + 1
        elif mode == "damage_bane":
            value = min(roll) + 1
        else:
            value = roll[0] + 1
        counts[value] += 1
    total = sum(counts.values())
    return {value: count / total for value, count in sorted(counts.items())}


def expected_damage(mode: str = "normal") -> float:
    return sum(value * probability for value, probability in damage_distribution(mode).items())


def kill_probability(hp: int, mode: str = "normal") -> float:
    return sum(probability for value, probability in damage_distribution(mode).items() if value >= hp)


def exact_local_analysis() -> dict[str, Any]:
    skills = (10, 12, 14, 18)
    hp_bands = (1, 4, 6, 8)
    basics = []
    for skill in skills:
        for hp in hp_bands:
            p = success_probability(skill)
            basics.append(
                {
                    "skill": skill,
                    "target_hp": hp,
                    "basic_cut_or_thrust": {"hit": p, "expected_damage": p * expected_damage(), "kill": p * kill_probability(hp)},
                    "loaded_cut": {"hit": p, "expected_damage": p * expected_damage("damage_boon"), "kill": p * kill_probability(hp, "damage_boon")},
                    "power": {"hit": p, "expected_damage": 7 * p, "kill": p if hp <= 7 else 0.0},
                }
            )

    cross_beat = []
    for skill in skills:
        hart = success_probability(skill, "boon")
        weich = success_probability(skill)
        p_attack = success_probability(skill)
        p_boon_attack = success_probability(skill, "boon")
        mean_damage = expected_damage()
        cross_beat.append(
            {
                "skill": skill,
                "cross_hart_cancel": hart,
                "cross_weich_cancel": weich,
                "beat_cancel": weich,
                "hart_survival_delta_vs_beat": hart - weich,
                "cross_state": "Crossing+Rejoinder+height",
                "beat_state": "separation+attacker Open",
                "expected_incoming_after_beat": (1 - weich) * mean_damage,
                "expected_incoming_after_hart_cross_no_bind_repertoire": (1 - hart) * mean_damage,
                "expected_incoming_after_hart_cross_correct_dm": (1 - hart) * mean_damage + hart * p_boon_attack * mean_damage,
                "expected_incoming_after_hart_cross_decline_winding": (1 - hart) * mean_damage + hart * p_attack * mean_damage,
                "open_intrinsic_numeric_or_access_payload": 0,
            }
        )

    fuhlen = []
    for skill in skills:
        p_boon = success_probability(skill, "boon")
        attack_damage = p_boon * expected_damage()
        for prior in (0.2, 0.4, 0.5, 0.6, 0.8):
            fuhlen.append(
                {
                    "skill": skill,
                    "hart_prior": prior,
                    "blind_duplieren_damage": prior * attack_damage,
                    "blind_mutieren_damage": (1 - prior) * attack_damage,
                    "fuhlen_correct_damage": attack_damage,
                    "blind_best_damage": max(prior, 1 - prior) * attack_damage,
                    "wrong_read_probability_best_blind": min(prior, 1 - prior),
                    "fuhlen_spiritus": 3,
                    "blind_spiritus": 2,
                }
            )

    winding = []
    for skill in skills:
        p = success_probability(skill)
        miss = 1 - p
        for spiritus in (2, 3, 4, 5, 8):
            max_declarations = min(3, spiritus // 2)
            hit_by_limit = 1 - miss**max_declarations
            p_cap = miss**3 if max_declarations == 3 else 0.0
            expected_decl = sum(miss**index for index in range(max_declarations))
            winding.append(
                {
                    "skill": skill,
                    "spiritus": spiritus,
                    "max_declarations": max_declarations,
                    "expected_declarations": expected_decl,
                    "hit_by_limit": hit_by_limit,
                    "chain_cap_block_probability": p_cap,
                    "resource_stop_probability": miss**max_declarations if max_declarations < 3 else 0.0,
                }
            )
    return {
        "method": "exact d20/d6 enumeration; independent bounded branches only",
        "basic_attack_cells": basics,
        "cross_beat": cross_beat,
        "fuhlen_priors": fuhlen,
        "winding_chains": winding,
    }


def empty_metrics() -> dict[str, Any]:
    return {
        "duels": 0,
        "wins": Counter(),
        "remaining_hp": 0,
        "exchanges": 0,
        "no_damage_exchanges": 0,
        "damage": Counter(),
        "declarations": Counter(),
        "legal_opportunities": Counter(),
        "spiritus_spent": Counter(),
        "ending_spiritus": Counter(),
        "crossings": 0,
        "heights": Counter(),
        "rejoinders": 0,
        "fuhlen": 0,
        "dm_correct": 0,
        "dm_wrong": 0,
        "winding": 0,
        "winding_miss_transfer": 0,
        "bind_pass_termination": 0,
        "disengage_termination": 0,
        "chain_lengths": Counter(),
        "chain_cap_blocks": 0,
        "open_created": 0,
        "open_exploited": 0,
        "open_recovered": 0,
        "guard_transitions": Counter(),
        "point_threat_events": 0,
        "stale_cleanup_failures": 0,
        "dead_actor_attempts": 0,
        "second_action_leaks": 0,
        "ordinary_relation_leaks": 0,
        "temporal_exchanges": 0,
        "bind_exchanges": 0,
    }


class IntegratedDuel:
    def __init__(self, scenario: Scenario, seed: int, metrics: dict[str, Any]) -> None:
        self.scenario = scenario
        self.rng = random.Random(seed)
        self.metrics = metrics
        self.a = Fighter("A", scenario.skill_a, scenario.hp_a, scenario.spiritus_a, guard=scenario.guard_a, known_plays=set(scenario.repertoire_a))
        self.b = Fighter("B", scenario.skill_b, scenario.hp_b, scenario.spiritus_b, guard=scenario.guard_b, known_plays=set(scenario.repertoire_b))
        self.engine = CurrentEngine([self.a, self.b])
        self.policies = {"A": POLICIES[scenario.policy_a], "B": POLICIES[scenario.policy_b]}
        self.history: list[str] = []
        self.exchanges = 0
        self.last_named_guard = {"A": self.a.guard, "B": self.b.guard}

    def roll20(self, modifier: str = "normal") -> tuple[int, ...]:
        return tuple(self.rng.randint(1, 20) for _ in range(2 if modifier in {"boon", "bane"} else 1))

    def roll_damage(self, mode: str = "normal") -> tuple[int, ...]:
        return tuple(self.rng.randint(1, 6) for _ in range(2 if mode in {"damage_boon", "damage_bane"} else 1))

    def view(self, actor: Fighter, options: Iterable[str]) -> PolicyView:
        return make_policy_view(self.engine, actor, options, self.history)

    def _record_spend(self, before: dict[str, int]) -> None:
        for fighter in (self.a, self.b):
            delta = before[fighter.name] - fighter.spiritus
            if delta > 0:
                self.metrics["spiritus_spent"][fighter.name] += delta

    def _resolve_bind(self, striker: Fighter) -> None:
        policy = self.policies[striker.name]
        options = ["Fuhlen" if option.startswith("F") else option for option in self.engine.rejoinder_options(striker)]
        for option in options:
            self.metrics["legal_opportunities"][option] += 1
        choice = policy.rejoinder(self.view(striker, options))
        if choice == "Fuhlen":
            before = striker.spiritus
            revealed = self.engine.buy_fuhlen(striker)
            if revealed is not None:
                self.metrics["fuhlen"] += 1
                self.metrics["declarations"]["Fuhlen"] += 1
                self.metrics["spiritus_spent"]["Fuhlen"] += before - striker.spiritus
                self.history.append(f"pressure-revealed:{revealed}")
                options = ["Fuhlen" if option.startswith("F") else option for option in self.engine.rejoinder_options(striker)]
                choice = policy.rejoinder(self.view(striker, options))
        if choice in {"Duplieren", "Mutieren"}:
            before = striker.spiritus
            declaration = self.engine.declare_bind_rejoinder(striker, choice)
            self.metrics["declarations"][choice] += 1
            self.metrics["spiritus_spent"][choice] += before - striker.spiritus
            if declaration.success and self.engine.pending_bind_attack is not None:
                result = self.engine.resolve_bind_rejoinder(self.roll20("boon"), self.roll_damage())
                self.metrics["dm_correct"] += 1
                if result.damage:
                    self.metrics["damage"][striker.name] += result.damage
            else:
                self.metrics["dm_wrong"] += 1
            return
        self.metrics["declarations"]["decline"] += 1
        if not self.engine.decline_bind_rejoinder(striker):
            return
        while self.engine.crossing.contact == "crossing" and self.a.alive and self.b.alive:
            name = self.engine.crossing.bind_initiative
            if name is None:
                break
            actor = self.engine.fighters[name]
            options = self.engine.continuation_options(actor, winden_variant="W2")
            if (
                len(self.engine.learned_chain) >= ENGINE.LEARNED_PLAY_CAP
                and WINDEN in actor.known_plays
                and actor.spiritus >= 2
                and self.engine.crossing.bind_height in {UPPER, LOWER}
            ):
                self.metrics["chain_cap_blocks"] += 1
            for option in options:
                self.metrics["legal_opportunities"][option] += 1
            choice = self.policies[name].continuation(self.view(actor, options))
            if choice.endswith("Winding Thrust"):
                before = actor.spiritus
                declaration = self.engine.declare_lower_winding(actor) if choice.startswith("Lower") else self.engine.declare_upper_winding(actor)
                if not declaration.legal:
                    self.metrics["chain_cap_blocks"] += 1
                    choice = "pass"
                else:
                    self.metrics["winding"] += 1
                    self.metrics["declarations"][choice] += 1
                    self.metrics["spiritus_spent"][choice] += before - actor.spiritus
                    result = self.engine.resolve_lower_winding(self.roll20(), self.roll_damage()) if choice.startswith("Lower") else self.engine.resolve_upper_winding(self.roll20(), self.roll_damage())
                    if result.damage:
                        self.metrics["damage"][actor.name] += result.damage
                    elif not result.success:
                        self.metrics["winding_miss_transfer"] += 1
                    continue
            if choice == "Disengage":
                if self.engine.disengage(actor):
                    self.metrics["disengage_termination"] += 1
                break
            if self.engine.pass_bind_initiative(actor) and self.engine.crossing.contact == "none":
                self.metrics["bind_pass_termination"] += 1
                break

    def exchange(self, actor: Fighter, target: Fighter) -> None:
        hp_before = self.a.hp + self.b.hp
        chain_before = len(self.engine.learned_chain)
        if not actor.alive or not target.alive:
            self.metrics["dead_actor_attempts"] += 1
            return
        self.engine.begin_activation(actor)
        if actor.guard == "open":
            old = actor.guard
            recovery_guard = self.last_named_guard[actor.name]
            if self.engine.recover_open(actor, recovery_guard):
                self.metrics["guard_transitions"][f"{old}->{recovery_guard}"] += 1
                self.metrics["open_recovered"] += 1
        attack_options = ["Basic Cut", "Basic Thrust"]
        if actor.loaded and actor.spiritus >= 1:
            attack_options.append("Power")
        choice = self.policies[actor.name].attack(self.view(actor, attack_options))
        if self.scenario.id == "D7" and actor.name == "B":
            choice = "Basic Cut"
        self.metrics["legal_opportunities"].update(attack_options)
        self.metrics["declarations"][choice] += 1
        before_spiritus = actor.spiritus
        if choice == "Power":
            attack = self.engine.declare_power_attack(actor, target)
            self.metrics["spiritus_spent"]["Power"] += before_spiritus - actor.spiritus
        else:
            kind = "cut" if choice == "Basic Cut" else "thrust"
            attack = self.engine.declare_attack(actor, target, kind, descending=(kind == "cut"))
        if attack is None:
            return

        defence_options = ["Cross", "Beat", "Counter", "Ignore"]
        if "Zornhau-Ort" in target.known_plays and attack.descending:
            defence_options.append("Zornhau")
        self.metrics["legal_opportunities"].update(defence_options)
        defence = self.policies[target.name].defence(self.view(target, defence_options))
        self.metrics["declarations"][defence] += 1

        if attack.committed and defence == "Counter":
            self.metrics["temporal_exchanges"] += 1
            result = self.engine.immediate_counter(target, self.roll20(), self.roll_damage())
            if result.damage:
                self.metrics["damage"][target.name] += result.damage
            if not actor.alive:
                self.engine.finish_exchange()
                self.exchanges += 1
                return
        if self.scenario.id == "D12" and choice != "Power":
            attack.kind = "low-line-thrust"
            attack.descending = False
        attack_result = self.engine.roll_pending_attack(self.roll20(attack.accuracy), self.roll_damage(attack.damage_mode))
        if not attack_result.success:
            self.engine.finish_exchange()
            self.exchanges += 1
            self.metrics["no_damage_exchanges"] += int(self.a.hp + self.b.hp == hp_before)
            return

        if defence == "Zornhau":
            result = self.engine.zornhau(target, attack_result.roll, self.roll20())
            if result.success:
                options = self.engine.continuation_options(target, winden_variant="W2")
                self.metrics["legal_opportunities"].update(options)
                if "Ort" in options:
                    before = target.spiritus
                    ort = self.engine.ort(target, "O1", self.roll_damage())
                    self.metrics["declarations"]["Ort"] += 1
                    self.metrics["spiritus_spent"]["Ort"] += before - target.spiritus
                    if ort.damage:
                        self.metrics["damage"][target.name] += ort.damage
            else:
                resolved = self.engine.resolve_pending_attack()
                if resolved.damage:
                    self.metrics["damage"][actor.name] += resolved.damage
        elif defence == "Counter" and attack.phase == "rolled":
            result = self.engine.waiting_counter(target, self.roll20(), self.roll_damage())
            self.metrics["temporal_exchanges"] += 1
            if result.damage:
                self.metrics["damage"][target.name] += result.damage
            self.metrics["damage"][actor.name] += attack.damage
        elif defence in {"Cross", "Beat"}:
            pressure = self.policies[target.name].pressure(self.view(target, (HART, WEICH)))
            if defence == "Cross":
                self.engine.declare_basic_cross(target, pressure, self.scenario.geometry)
            result = self.engine.basic_defence(defence, target, attack_result.roll, self.roll20("boon" if pressure == HART and defence == "Cross" else "normal"))
            if result.success:
                if defence == "Beat":
                    self.metrics["open_created"] += 1
                else:
                    self.metrics["crossings"] += 1
                    self.metrics["heights"][self.engine.crossing.bind_height] += 1
                    self.metrics["bind_exchanges"] += 1
                    if (
                        target.guard == "tutta-porta-di-ferro"
                        and "Tutta Cover-to-Stretto" in target.known_plays
                        and target.spiritus >= 1
                        and len(self.engine.learned_chain) < ENGINE.LEARNED_PLAY_CAP
                    ):
                        self.metrics["legal_opportunities"]["T1"] += 1
                    if self.engine.rejoinder_open:
                        self.metrics["rejoinders"] += 1
                        self._resolve_bind(actor)
                    elif target.guard == "tutta-porta-di-ferro" and "Tutta Cover-to-Stretto" in target.known_plays:
                        before = target.spiritus
                        if self.engine.tutta_cover_to_stretto(target):
                            self.metrics["declarations"]["T1"] += 1
                            self.metrics["spiritus_spent"]["T1"] += before - target.spiritus
            else:
                resolved = self.engine.resolve_pending_attack()
                if resolved.damage:
                    self.metrics["damage"][actor.name] += resolved.damage
        else:
            resolved = self.engine.resolve_pending_attack()
            if resolved.damage:
                self.metrics["damage"][actor.name] += resolved.damage

        if self.engine.crossing.source == "ordinary-basic-cross" and any(v != UNKNOWN for v in self.engine.crossing.bind_position.values()):
            self.metrics["ordinary_relation_leaks"] += 1
        self.metrics["chain_lengths"][len(self.engine.learned_chain)] += 1
        self.metrics["second_action_leaks"] += int(actor.action_available or (defence != "Ignore" and target.action_available))
        self.engine.finish_exchange()
        if self.engine.crossing.contact != "none" and not self.engine.crossing.retained:
            self.metrics["stale_cleanup_failures"] += 1
        self.exchanges += 1
        self.metrics["no_damage_exchanges"] += int(self.a.hp + self.b.hp == hp_before)

    def run(self) -> tuple[str, int]:
        for round_number in range(1, self.scenario.max_rounds + 1):
            for fighter in (self.a, self.b):
                fighter.action_available = fighter.alive
                fighter.activation_action_taken = False
                fighter.guard_change_available = True
            order = (self.a, self.b) if self.rng.random() < 0.5 else (self.b, self.a)
            for fighter in order:
                opponent = self.engine.other(fighter)
                if fighter.alive and opponent.alive and fighter.action_available:
                    self.exchange(fighter, opponent)
                if not self.a.alive or not self.b.alive:
                    break
            if not self.a.alive and not self.b.alive:
                return "double", round_number
            if not self.a.alive:
                return "B", round_number
            if not self.b.alive:
                return "A", round_number
        return "draw", self.scenario.max_rounds


def serialize(value: Any) -> Any:
    if isinstance(value, Counter):
        return dict(sorted(value.items()))
    if isinstance(value, dict):
        return {key: serialize(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [serialize(item) for item in value]
    return value


def run_scenario(scenario: Scenario, trials: int = TRIALS) -> dict[str, Any]:
    metrics = empty_metrics()
    rounds: list[int] = []
    for trial in range(trials):
        duel = IntegratedDuel(scenario, SEED + 100003 * int(scenario.id[1:]) + trial, metrics)
        winner, length = duel.run()
        metrics["duels"] += 1
        metrics["wins"][winner] += 1
        metrics["remaining_hp"] += max(0, duel.a.hp) + max(0, duel.b.hp)
        metrics["ending_spiritus"]["A"] += duel.a.spiritus
        metrics["ending_spiritus"]["B"] += duel.b.spiritus
        metrics["exchanges"] += duel.exchanges
        rounds.append(length)
    opportunities = metrics["legal_opportunities"]
    declarations = metrics["declarations"]
    conversion = {name: declarations[name] / count for name, count in opportunities.items() if count}
    output = serialize(metrics)
    output.update(
        {
            "scenario": serialize(asdict(scenario)),
            "win_rate": {name: count / trials for name, count in metrics["wins"].items()},
            "average_remaining_hp_per_fighter": metrics["remaining_hp"] / (2 * trials),
            "average_rounds": statistics.mean(rounds),
            "average_exchanges": metrics["exchanges"] / trials,
            "no_damage_exchange_rate": metrics["no_damage_exchanges"] / metrics["exchanges"] if metrics["exchanges"] else 0.0,
            "conversion_given_legality": conversion,
            "end_spiritus_estimate": {
                "A": metrics["ending_spiritus"]["A"] / trials,
                "B": metrics["ending_spiritus"]["B"] / trials,
            },
            "monte_carlo": {"seed": SEED, "samples": trials, "binomial_95pct_half_width_at_p50": 1.96 * math.sqrt(0.25 / trials)},
        }
    )
    return output


def response_traces() -> list[dict[str, Any]]:
    traces: list[dict[str, Any]] = []

    def snapshot(label: str, engine: CurrentEngine, a: Fighter, b: Fighter) -> dict[str, Any]:
        return {
            "step": label,
            "hp": {"A": a.hp, "B": b.hp},
            "actions": {"A": a.action_available, "B": b.action_available},
            "spiritus": {"A": a.spiritus, "B": b.spiritus},
            "chain": list(engine.learned_chain),
            "guard": {"A": a.guard, "B": b.guard},
            "open": {"A": a.guard == "open", "B": b.guard == "open"},
            "crossing": engine.crossing.contact,
            "height": engine.crossing.bind_height,
            "pressure_public": engine.public_crossing_state(),
            "point_threat": {"A": a.point_threat, "B": b.point_threat},
            "opportunity": engine.crossing.bind_initiative or engine.rejoinder_actor,
            "measure": engine.crossing.measure,
        }

    a = Fighter("A", known_plays={DM, FUHLEN})
    b = Fighter("B")
    e = CurrentEngine([a, b]); atk = e.declare_attack(a, b, "cut", descending=True); ar = e.roll_pending_attack((1,), (3,)); e.declare_basic_cross(b, HART, ENGINE.UPPER_CROSS); e.basic_defence("Cross", b, ar.roll, (1, 20)); steps=[snapshot("successful Hart Cross",e,a,b)]; e.declare_bind_rejoinder(a,"Duplieren"); steps.append(snapshot("Duplieren declared",e,a,b)); e.resolve_bind_rejoinder((1,20),(3,)); steps.append(snapshot("Duplieren resolved",e,a,b)); traces.append({"id":"T1","title":"Basic Cross Hart -> D/M","steps":steps})

    a = Fighter("A", known_plays={WINDEN}); b = Fighter("B", known_plays={WINDEN}); e=CurrentEngine([a,b]); atk=e.declare_attack(a,b,"cut",descending=True); ar=e.roll_pending_attack((1,),(3,)); e.declare_basic_cross(b,WEICH,ENGINE.UPPER_CROSS); e.basic_defence("Cross",b,ar.roll,(1,)); e.decline_bind_rejoinder(a); steps=[snapshot("Weich decline",e,a,b)]; e.declare_upper_winding(b); e.resolve_upper_winding((1,),(3,)); steps.append(snapshot("defender Winding hit",e,a,b)); traces.append({"id":"T2","title":"Basic Cross Weich -> decline -> defender Winden","steps":steps})

    a=Fighter("A",known_plays={WINDEN}); b=Fighter("B",known_plays={WINDEN}); e=CurrentEngine([a,b]); atk=e.declare_attack(a,b,"low-line-thrust"); ar=e.roll_pending_attack((1,),(3,)); e.declare_basic_cross(b,WEICH,ENGINE.LOWER_SETTING_ASIDE); e.basic_defence("Cross",b,ar.roll,(1,)); e.decline_bind_rejoinder(a); e.declare_lower_winding(b); e.resolve_lower_winding((20,),(3,)); traces.append({"id":"T3","title":"Lower Cross -> Lower Winding miss -> Upper response","steps":[snapshot("L2 after miss",e,a,b)]})

    a=Fighter("A",guard="posta-di-donna"); b=Fighter("B"); e=CurrentEngine([a,b]); atk=e.declare_attack(a,b,"cut"); ar=e.roll_pending_attack((1,),(3,)); e.basic_defence("Beat",b,ar.roll,(1,)); steps=[snapshot("Beat strips attacker to Open",e,a,b)]; e.finish_exchange(); e.begin_activation(a); e.recover_open(a,"vom-tag"); steps.append(snapshot("next activation guard recovery",e,a,b)); traces.append({"id":"T4","title":"Beat -> Open -> guard recovery","steps":steps})

    a=Fighter("A",guard="posta-di-donna",hp=4); b=Fighter("B",known_plays={"Nachreisen"}); e=CurrentEngine([a,b]); e.declare_power_attack(a,b); steps=[snapshot("Power declared",e,a,b)]; e.immediate_counter(b,(1,),(3,)); steps.append(snapshot("immediate Counter",e,a,b)); traces.append({"id":"T5","title":"Committed Power -> immediate/wait Counter / Nachreisen branch","steps":steps})

    a = Fighter("A")
    b = Fighter("B", known_plays={"Zornhau-Ort", FUHLEN, WINDEN})
    e = CurrentEngine([a, b])
    e.declare_attack(a, b, "cut", descending=True)
    ar = e.roll_pending_attack((10,), (3,))
    e.zornhau(b, ar.roll, (5,))
    steps = [snapshot("Zornhau local relation", e, a, b)]
    if e.crossing.bind_position.get("B") == "favored":
        e.ort(b, "O1", (3,))
    steps.append(snapshot("local continuation", e, a, b))
    traces.append({"id": "T6", "title": "Zornhau -> local relation -> Ort/local Winden", "steps": steps})
    return traces


def audit_conclusions() -> dict[str, Any]:
    return {
        "pre_audit_baseline": {
            "commit": "ca86d85b4753302d598e9b745aa5b1e7a50347ad",
            "branch": "main",
            "melee_repertoire_integrity": "81/81 PASS",
            "general_bind": "75/75 PASS",
            "hart_weich_upper_winden": "82/82 PASS",
            "upper_lower_winden": "68/68 PASS",
            "h3_governing": "129/129 required assertions PASS",
            "full_unittest_discovery": "142 tests PASS before audit",
            "repository_validator": "114 Play records; 0 errors; 39 warnings",
            "grammar_validator": "0 errors; 16 informative findings",
        },
        "runtime_bugs": [
            {"id": "BUG-1", "finding": "dead fighters could enter declarations", "classification": "D. RUNTIME BUG", "repair": "central alive gates"},
            {"id": "BUG-2", "finding": "authoritative declare/roll path omitted Loaded Cut damage boon", "classification": "D. RUNTIME BUG", "repair": "write and consume damage_boon mode"},
            {"id": "BUG-3", "finding": "D1 marked replacement but left the original rolled attack non-rerollable", "classification": "D. RUNTIME BUG", "repair": "reset the same pending object as the authored replacement thrust"},
        ],
        "incentive_problems": [
            {"id": "INC-1", "finding": "T1 has raw legality during an open H3 Rejoinder but no authored ordering and no authoritative Close consumer; D13 converts 0 of its opportunities", "classification": "E. MISSING REPERTOIRE CONSUMER / INTEGRATION CONFLICT", "severity": "SEVERE"}
        ],
        "watch_items": [
            "Open is concrete only when loss of guard state survives to an opponent opportunity; no tested policy exploited it directly.",
            "Fuhlen is raw-damage attractive at reserve 3+, but its one-Spiritus shadow price preserves blind/decline niches.",
            "Full-bind policies spend roughly half of max-8 Spiritus in short duels; longer cadence remains campaign-level debt.",
            "Nachreisen is mechanically distinct after repair but did not receive a natural full-duel trigger in the bounded scenario policies.",
        ],
        "grammar_findings": [
            {"finding": "basic-ignore ghost utility", "class": "A", "reason": "current duel decision utility"},
            {"finding": "Power exceptional non-restriction", "class": "C", "reason": "intentional scoped timing"},
            {"finding": "S2 exceptional comparison", "class": "C", "reason": "intentional scoped timing"},
            {"finding": "S2 proactive Pflug payload missing", "class": "B", "reason": "later proactive breaker work"},
            {"finding": "T1 ghost utility", "class": "A", "reason": "0 conversion and unresolved H3 ordering"},
            {"finding": "Pommel fixed policy utility", "class": "A", "reason": "missing authoritative Close consumer makes T1 value ungrounded"},
            {"finding": "Nachreisen trigger-not-payoff", "class": "C", "reason": "stale after governing repair"},
            {"finding": "Nachreisen no distinction", "class": "C", "reason": "stale after governing boon/timing repair"},
            {"finding": "Nachreisen missing effect", "class": "C", "reason": "stale after governing repair"},
            {"finding": "Nachreisen ghost utility", "class": "C", "reason": "old policy finding; current duel policy did not fake use"},
            {"finding": "Frontale missing primary payload", "class": "B", "reason": "candidate-only sequence"},
            {"finding": "Frontale no distinction", "class": "B", "reason": "candidate-only sequence"},
            {"finding": "Frontale missing effect", "class": "B", "reason": "candidate-only sequence"},
            {"finding": "Frontale ghost utility", "class": "B", "reason": "candidate-only sequence"},
            {"finding": "Crown C1/B3 missing effect", "class": "B", "reason": "candidate-only and non-governing"},
            {"finding": "Crown C1/B3 ghost utility", "class": "B", "reason": "candidate-only and non-governing"},
        ],
        "next_milestone": "D. T1 / CLOSE REPERTOIRE CONSUMER PASS",
        "promotion": "STOP FOR PROJECT ADJUDICATION; preserve H3 kernel and all protected prices/caps",
    }


def build_results(trials: int = TRIALS) -> dict[str, Any]:
    scenarios = [run_scenario(scenario, trials) for scenario in SCENARIOS]
    return {
        "milestone": "ATRA INTEGRATED FULL-DUEL MELEE CLEANUP / INCENTIVE AUDIT v0.1",
        "status": "AUDIT EVIDENCE; NO DESIGN PROMOTION",
        "seed": SEED,
        "trials_per_scenario": trials,
        "authoritative_engine": "simulations/shared/provisional_longsword.py::CurrentEngine",
        "policy_interface_fields": [field.name for field in PolicyView.__dataclass_fields__.values()],
        "policy_families": {name: asdict(policy) for name, policy in POLICIES.items()},
        "scenario_matrix": [serialize(asdict(scenario)) for scenario in SCENARIOS],
        "exact": exact_local_analysis(),
        "duels": scenarios,
        "response_traces": response_traces(),
        "audit_conclusions": audit_conclusions(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    results = build_results(args.trials)
    if not args.no_write:
        path = ROOT / "reports" / "integrated-full-duel-melee-cleanup-v01-results.json"
        path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"scenarios": len(results["duels"]), "trials_per_scenario": args.trials, "seed": SEED}, indent=2))


if __name__ == "__main__":
    main()

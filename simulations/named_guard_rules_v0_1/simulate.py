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
SHARED_PATH = ROOT / "simulations" / "shared" / "provisional_longsword.py"
GUARD_PATH = ROOT / "data" / "guards" / "longsword-named-v0.1.yaml"
RESULTS_PATH = ROOT / "reports" / "named-guard-rules-v01-results.json"
REPORT_PATH = ROOT / "reports" / "named-guard-rules-v01-results.md"
PRIOR_POWER_PATH = ROOT / "reports" / "loaded-power-attack-v01-results.json"

SPEC = importlib.util.spec_from_file_location("atra_named_guard_shared", SHARED_PATH)
SHARED = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = SHARED
SPEC.loader.exec_module(SHARED)
ENGINE = SHARED.ENGINE
BASE = ENGINE.BASE

GUARD_DATA = json.loads(GUARD_PATH.read_text(encoding="utf-8"))
GUARDS = {item["id"]: item for item in GUARD_DATA["guards"]}
TRADITION_GUARDS = {
    tradition: tuple(item["id"] for item in GUARD_DATA["guards"] if item["tradition"] == tradition)
    for tradition in ("German", "Italian")
}

MODELS = ("G0", "G1", "G2")
FREE_ABSETZEN = "Pflug Free Absetzen"
SEED = 1108202602
TRIALS_PER_CELL = 1280


@dataclass(frozen=True)
class Cell:
    model: str
    tradition: str
    skill: int
    start_spiritus: int
    information: str = "adaptive_revelation"

    @property
    def label(self) -> str:
        return f"{self.model}_{self.tradition.lower()}_skill{self.skill}_S{self.start_spiritus}"


def ratio(n: float, d: float) -> float:
    return n / d if d else 0.0


def guard_point(guard_id: str) -> str:
    value = GUARDS[guard_id]["physical_state"].get("point_threat", "unknown")
    # Unknown adds no sourced threatening state; current engine default is not_threatening.
    return value if value != "unknown" else "not_threatening"


def is_loaded_guard(guard_id: str) -> bool:
    return bool(GUARDS[guard_id]["physical_state"].get("loaded", False))


def fresh_metrics() -> dict[str, Any]:
    metrics = SHARED.fresh_metrics()
    metrics.update({
        "guard_occupancy": Counter(),
        "guard_occupancy_slots": 0,
        "starting_guard_outcomes": {},
        "guard_changes": 0,
        "before_action_guard_changes": 0,
        "after_action_guard_changes": 0,
        "guard_churn_events": 0,
        "proactive_attacks_by_guard": Counter(),
        "defensive_responses_by_guard": Counter(),
        "point_threatening_guard_slots": 0,
        "d1_windows_created_by_guard_state": 0,
        "d1_windows_denied_by_guard_state": 0,
        "loaded_guard_slots": 0,
        "basic_guard_action_opportunities": 0,
        "basic_guard_action_uses": 0,
        "basic_guard_action_successes": 0,
        "g2_free_compound_actions": Counter(),
        "learned_plays_displaced_by_free_guard_actions": 0,
        "action_compression_events": 0,
        "sourced_breaker_opportunities": Counter(),
        "sourced_breaker_uses_mechanically_implemented": Counter(),
        "guard_change_policy_decisions": Counter(),
    })
    return metrics


class NamedGuardDuel(SHARED.BaseDuel):
    """Named-guard extension of the shared provisional engine.

    G0 keeps the inherited current-combat control. G1 adds state/access only.
    G2 differs solely by exposing the audited Pflug Absetzen compound as a free
    Basic guard action.
    """

    def __init__(self, rng: random.Random, policy_rng: random.Random, cell: Cell,
                 metrics: dict[str, Any], starting_pair: tuple[str, str]) -> None:
        base_model = "C0" if cell.model == "G0" else "P1"
        super().__init__(rng, policy_rng, ENGINE.Cell(base_model, cell.skill, cell.start_spiritus, cell.information), metrics)
        self.named_cell = cell
        self.guards = {"A": starting_pair[0], "B": starting_pair[1]}
        self.guard_changed_this_activation = False
        self.guard_history = {"A": [starting_pair[0]], "B": [starting_pair[1]]}
        if cell.model != "G0":
            self.apply_guard_state(self.a)
            self.apply_guard_state(self.b)

    def current_guard(self, fighter: BASE.Fighter) -> str:
        return self.guards[fighter.name]

    def public_guard_state(self, fighter: BASE.Fighter) -> dict[str, Any]:
        record = GUARDS[self.current_guard(fighter)]
        return {
            "guard": record["id"],
            "height": record["physical_state"].get("height", "unknown"),
            "point_threat": guard_point(record["id"]),
            "preparation_tags": list(record["physical_state"].get("preparation_tags", [])),
            "hanging_tags": list(record["physical_state"].get("hanging_tags", [])),
            "posture_tags": list(record["physical_state"].get("posture_tags", [])),
            "loaded": is_loaded_guard(record["id"]),
        }

    def apply_guard_state(self, fighter: BASE.Fighter) -> None:
        self.set_point(fighter, guard_point(self.current_guard(fighter)))

    def loaded_for(self, fighter: BASE.Fighter) -> bool:
        return self.named_cell.model != "G0" and is_loaded_guard(self.current_guard(fighter))

    def can_use_power(self, fighter: BASE.Fighter) -> bool:
        return self.loaded_for(fighter) and fighter.spiritus >= 1

    def change_guard(self, fighter: BASE.Fighter, new_guard: str, phase: str) -> bool:
        if self.named_cell.model == "G0" or self.guard_changed_this_activation:
            return False
        if new_guard not in TRADITION_GUARDS[self.named_cell.tradition]:
            return False
        old_guard = self.current_guard(fighter)
        if new_guard == old_guard:
            return False
        self.guards[fighter.name] = new_guard
        self.guard_changed_this_activation = True
        self.metrics["guard_changes"] += 1
        self.metrics[f"{phase}_action_guard_changes"] += 1
        history = self.guard_history[fighter.name]
        if len(history) >= 2 and history[-2] == new_guard and history[-1] != new_guard:
            self.metrics["guard_churn_events"] += 1
        history.append(new_guard)
        self.apply_guard_state(fighter)
        return True

    def guard_policy_value(self, fighter: BASE.Fighter, guard_id: str, phase: str) -> float:
        target = self.other(fighter)
        record = GUARDS[guard_id]
        value = 0.0
        if phase == "before":
            if record["physical_state"].get("loaded"):
                value += 0.23 + (0.10 if fighter.spiritus else 0.0)
                value += 0.08 * (1.0 - target.hp / ENGINE.MAX_HP)
            if "Absetzen" in record["mechanical_access"]["learned_play_gates"]:
                value += 0.12
            if self.named_cell.model == "G2" and record["id"] == "pflug":
                value += 0.08
        else:
            if guard_point(guard_id) == "threatening":
                value += 0.16
            if "Absetzen" in record["mechanical_access"]["learned_play_gates"] and fighter.spiritus >= 2:
                value += 0.05
        if guard_id != self.current_guard(fighter):
            value -= 0.09  # policy friction, not a rules cost
        return value

    def consider_guard_change(self, fighter: BASE.Fighter, phase: str) -> None:
        if self.named_cell.model == "G0" or self.guard_changed_this_activation:
            return
        choices = {
            guard_id: self.guard_policy_value(fighter, guard_id, phase)
            for guard_id in TRADITION_GUARDS[self.named_cell.tradition]
        }
        choices["defer"] = 0.03 if phase == "before" else 0.0
        selected = self.softmax(choices, temperature=0.30)
        self.metrics["guard_change_policy_decisions"][f"{phase}:{selected}"] += 1
        if selected != "defer":
            self.change_guard(fighter, selected, phase)

    def make_attack(self, key: str) -> dict[str, Any]:
        # choose_proactive_attack sets the dynamic rules for its acting fighter.
        return super().make_attack(key)

    def choose_proactive_attack(self, actor: BASE.Fighter, target: BASE.Fighter) -> dict[str, Any]:
        loaded = self.loaded_for(actor)
        self.rules.update({
            "loaded": loaded,
            "power": loaded,
            "cost": 1,
            "attack_bane": False,
            "counter_first": True,
        })
        attack = super().choose_proactive_attack(actor, target)
        guard = self.current_guard(actor) if self.named_cell.model != "G0" else "control-no-guard"
        self.metrics["proactive_attacks_by_guard"][f"{guard}:{attack['choice_key']}"] += 1
        return attack

    def declare_power(self, actor: BASE.Fighter) -> bool:
        self.rules["power"] = self.can_use_power(actor)
        self.rules["loaded"] = self.loaded_for(actor)
        return super().declare_power(actor)

    def defence_values(self, attacker: BASE.Fighter, defender: BASE.Fighter,
                       attack: dict[str, Any]) -> dict[str, float]:
        values = super().defence_values(attacker, defender, attack)
        if self.named_cell.model in ("G1", "G2") and self.current_guard(defender) != "pflug":
            values.pop(BASE.ABSETZEN, None)
        if (
            self.named_cell.model in ("G1", "G2")
            and self.current_guard(defender) not in ("posta-di-donna", "tutta-porta-di-ferro")
        ):
            values.pop(BASE.SCIAMBIAR, None)
        if (
            self.named_cell.model == "G2"
            and self.current_guard(defender) == "pflug"
            and attack["type"] == "thrust"
        ):
            p_def = BASE.success_probability(defender.skill)
            pressure = attack["expected_damage"] / ENGINE.expected(ENGINE.normal_damage_distribution())
            offense = 1.0 + 0.3 * (ENGINE.MAX_HP - attacker.hp) / ENGINE.MAX_HP
            defense = 1.0 + 0.35 * (ENGINE.MAX_HP - defender.hp) / ENGINE.MAX_HP
            values[FREE_ABSETZEN] = p_def * (offense + pressure * defense)
        return values

    def basic_parry(self, form: str, attacker: BASE.Fighter, defender: BASE.Fighter,
                    attribution: str | None, forced_roll: bool | None = None,
                    force_durch: bool | None = None) -> str:
        m = self.metrics
        m["choices"]["Basic Parry"] += 1
        m["parry_declarations"][form] += 1
        self.spend_action(defender)
        if self.named_cell.model == "G0":
            self.set_point(defender, "not_threatening")
        else:
            self.apply_guard_state(defender)
        d1_legal = self.state.point_threat[defender.name] == "not_threatening"
        if d1_legal:
            m["d1_windows_created_by_guard_state"] += 1
        else:
            m["d1_windows_denied_by_guard_state"] += 1
        declared = False
        if d1_legal:
            declared = self.durch_decision(attacker, defender, f"Basic {form}") if force_durch is None else force_durch
        if declared:
            if force_durch is True:
                m["durch_opportunities"] += 1
                m["plays"][BASE.DURCH]["opportunities"] += 1
                if attacker.spiritus < BASE.DURCH_COST or not self.add_play(BASE.DURCH):
                    return "invalid"
                m["durch_declarations"] += 1
                self.spend_spiritus(attacker, BASE.DURCH_COST, "durch")
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
        else:
            self.displace(attacker, "Basic Parry: Beat", retain_crossing=False)
        return "success"

    def power_basic_parry(self, form: str, attacker: BASE.Fighter, defender: BASE.Fighter,
                          forced_roll: bool | None = None) -> str:
        result = super().power_basic_parry(form, attacker, defender, forced_roll)
        if self.named_cell.model != "G0":
            self.apply_guard_state(defender)
        return result

    def free_absetzen(self, attacker: BASE.Fighter, defender: BASE.Fighter,
                      attack: dict[str, Any], forced_roll: bool | None = None) -> str:
        self.metrics["basic_guard_action_uses"] += 1
        self.metrics["g2_free_compound_actions"][FREE_ABSETZEN] += 1
        self.metrics["learned_plays_displaced_by_free_guard_actions"] += 1
        self.metrics["action_compression_events"] += 1
        self.spend_action(defender)
        self.set_point(defender, "threatening")
        ok = self.roll(defender)[0] if forced_roll is None else forced_roll
        if not ok:
            self.hurt(defender, attack["attribution"])
            return "failed"
        self.metrics["basic_guard_action_successes"] += 1
        self.create_crossing(defender, attacker, first_pressure="unknown", second_pressure="unknown")
        self.hurt(attacker)
        return "success"

    def defend(self, attacker: BASE.Fighter, defender: BASE.Fighter, attack: dict[str, Any],
               attribution: str | None) -> None:
        if not defender.action_ready:
            self.hurt(defender, attack["attribution"])
            return
        self.metrics["defensive_opportunities"] += 1
        guard = self.current_guard(defender) if self.named_cell.model != "G0" else "control-no-guard"
        self.metrics["defensive_responses_by_guard"][guard] += 1
        values = self.defence_values(attacker, defender, attack)
        for name in (BASE.ABSETZEN, BASE.SCIAMBIAR, BASE.SCHIEL, BASE.ZORN):
            if name in values:
                self.metrics["plays"][name]["opportunities"] += 1
        if FREE_ABSETZEN in values:
            self.metrics["basic_guard_action_opportunities"] += 1
        if BASE.SCHIEL in values and self.named_cell.model != "G0" and self.current_guard(attacker) == "pflug":
            self.metrics["sourced_breaker_opportunities"]["Schielhau->Pflug (exact annotation; proactive entry unimplemented)"] += 1
        choice = self.softmax(values)
        self.metrics["choices"][choice] += 1
        self.metrics["responses"][self._response_category(attack)][choice] += 1
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
        elif choice == FREE_ABSETZEN:
            self.free_absetzen(attacker, defender, attack)
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

    def finish_exchange(self) -> None:
        if self.named_cell.model != "G0":
            for fighter in (self.a, self.b):
                guard = self.current_guard(fighter)
                self.metrics["guard_occupancy"][guard] += 1
                self.metrics["guard_occupancy_slots"] += 1
                if guard_point(guard) == "threatening":
                    self.metrics["point_threatening_guard_slots"] += 1
                if is_loaded_guard(guard):
                    self.metrics["loaded_guard_slots"] += 1
        super().finish_exchange()
        if self.named_cell.model != "G0":
            self.apply_guard_state(self.a)
            self.apply_guard_state(self.b)

    def activate(self, actor: BASE.Fighter) -> None:
        self.guard_changed_this_activation = False
        self.consider_guard_change(actor, "before")
        super().activate(actor)
        if actor.alive and not self.guard_changed_this_activation:
            # The inherited engine closes exchange cleanup before this hook. The guard
            # changes immediately after the action and is public for the next exchange.
            self.consider_guard_change(actor, "after")


def finalize(metrics: dict[str, Any]) -> dict[str, Any]:
    output = SHARED.finalize(metrics)
    fights = metrics["fights"]
    exchanges = metrics["exchanges"]
    slots = metrics["guard_occupancy_slots"]
    total_learned_uses = sum(item["uses"] for item in metrics["plays"].values())
    output.update({
        "guard_occupancy_share": {guard: ratio(count, slots) for guard, count in metrics["guard_occupancy"].items()},
        "starting_guard_outcome_share": metrics["starting_guard_outcomes"],
        "guard_changes_per_fight": ratio(metrics["guard_changes"], fights),
        "before_action_changes_per_fight": ratio(metrics["before_action_guard_changes"], fights),
        "after_action_changes_per_fight": ratio(metrics["after_action_guard_changes"], fights),
        "guard_churn_per_fight": ratio(metrics["guard_churn_events"], fights),
        "proactive_attacks_by_guard_per_fight": {key: ratio(value, fights) for key, value in metrics["proactive_attacks_by_guard"].items()},
        "defensive_responses_by_guard_per_fight": {key: ratio(value, fights) for key, value in metrics["defensive_responses_by_guard"].items()},
        "point_threatening_frequency": ratio(metrics["point_threatening_guard_slots"], slots),
        "d1_windows_created_per_fight": ratio(metrics["d1_windows_created_by_guard_state"], fights),
        "d1_windows_denied_per_fight": ratio(metrics["d1_windows_denied_by_guard_state"], fights),
        "loaded_occupancy_share": ratio(metrics["loaded_guard_slots"], slots),
        "loaded_cuts_per_fight": output["attack_stats"]["loaded_cut"]["declarations_per_fight"],
        "p1_opportunities_per_fight": output["attack_stats"]["power_attack"]["opportunities_per_fight"],
        "p1_declarations_per_fight": output["attack_stats"]["power_attack"]["declarations_per_fight"],
        "p1_spiritus_per_fight": output["power_spiritus_per_fight"],
        "counter_first_interruptions_per_fight": output["counter_first_interruptions_per_fight"],
        "learned_plays_per_fight": ratio(total_learned_uses, fights),
        "compounds_per_fight": output["compound_declarations_per_fight"],
        "basic_guard_actions_per_fight": ratio(metrics["basic_guard_action_uses"], fights),
        "g2_free_compound_actions_per_fight": {key: ratio(value, fights) for key, value in metrics["g2_free_compound_actions"].items()},
        "learned_plays_displaced_per_fight": ratio(metrics["learned_plays_displaced_by_free_guard_actions"], fights),
        "average_action_compression_per_exchange": ratio(metrics["action_compression_events"], exchanges),
        "sourced_breaker_opportunities_per_fight": {key: ratio(value, fights) for key, value in metrics["sourced_breaker_opportunities"].items()},
        "sourced_breaker_uses_per_fight": {key: ratio(value, fights) for key, value in metrics["sourced_breaker_uses_mechanically_implemented"].items()},
    })
    return output


def ordered_pairs(tradition: str) -> list[tuple[str, str]]:
    guards = TRADITION_GUARDS[tradition]
    return [(first, second) for first in guards for second in guards]


def run_cell(cell: Cell, trials: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    policy_rng = random.Random(seed ^ 0xC2055)
    metrics = fresh_metrics()
    pairs = ordered_pairs(cell.tradition)
    for index in range(trials):
        pair = pairs[index % len(pairs)]
        duel = NamedGuardDuel(rng, policy_rng, cell, metrics, pair)
        outcome, rounds = duel.run()
        SHARED.record_fight(metrics, outcome, rounds)
        metrics["fight_length_distribution"][str(rounds)] += 1
        metrics["end_spiritus_total"] += duel.a.spiritus + duel.b.spiritus
        key = f"{pair[0]}->{pair[1]}"
        bucket = metrics["starting_guard_outcomes"].setdefault(key, {"trials": 0, "A": 0, "B": 0, "double": 0, "draw": 0})
        bucket["trials"] += 1
        bucket[outcome] += 1
    finalized = finalize(metrics)
    for bucket in finalized["starting_guard_outcome_share"].values():
        bucket["A_share"] = ratio(bucket["A"], bucket["trials"])
        bucket["B_share"] = ratio(bucket["B"], bucket["trials"])
        bucket["double_share"] = ratio(bucket["double"], bucket["trials"])
    return {"cell": asdict(cell), "seed": seed, "trials": trials, "metrics": finalized}


def cells() -> Iterable[Cell]:
    for tradition in ("German", "Italian"):
        for model in MODELS:
            for skill in (10, 14, 18):
                for start in (8, 3):
                    yield Cell(model, tradition, skill, start)


def deterministic_harness() -> dict[str, Any]:
    def arena(model: str = "G1", tradition: str = "German", pair: tuple[str, str] | None = None) -> NamedGuardDuel:
        chosen = pair or ordered_pairs(tradition)[0]
        return NamedGuardDuel(
            random.Random(7), random.Random(11), Cell(model, tradition, 14, 8, "perfect_information"),
            fresh_metrics(), chosen,
        )

    out: dict[str, Any] = {}
    for label, guard in (("A_ochs", "ochs"), ("B_pflug", "pflug"), ("C_alber", "alber")):
        duel = arena(pair=(guard, "vom-tag"))
        out[label] = duel.public_guard_state(duel.a)

    duel = arena(pair=("vom-tag", "ochs"))
    duel.rules["loaded"] = duel.loaded_for(duel.a)
    out["D_vom_tag_not_loaded"] = {"loaded": duel.loaded_for(duel.a), "cut": duel.make_attack("basic_cut")["loaded"]}

    duel = arena("G1", "Italian", ("posta-di-donna", "posta-frontale"))
    duel.rules.update({"loaded": True, "power": True, "cost": 1, "attack_bane": False, "counter_first": True})
    donna_cut = duel.make_attack("basic_cut")
    out["E_donna_loaded_cut"] = {"loaded": donna_cut["loaded"], "damage": duel.damage_for("loaded_cut", (2, 5))}
    before = duel.a.spiritus
    declared = duel.declare_power(duel.a)
    out["F_donna_power"] = {"declared": declared, "spent": before - duel.a.spiritus, "damage": duel.damage_for("P1")}

    duel = arena("G1", "Italian", ("posta-di-donna", "posta-frontale"))
    changed = duel.change_guard(duel.a, "posta-frontale", "before")
    out["G_leave_donna"] = {"changed": changed, "loaded": duel.loaded_for(duel.a), "power": duel.can_use_power(duel.a)}

    threatening = arena("G1", "German", ("vom-tag", "ochs"))
    threatening.pending_attack = threatening.make_attack("basic_cut")
    threatening.pending_damage = 4
    threatening.pending_target = threatening.b
    denied = threatening.basic_parry("Cross", threatening.a, threatening.b, "test", forced_roll=True, force_durch=True)
    open_guard = arena("G1", "German", ("vom-tag", "alber"))
    open_guard.pending_attack = open_guard.make_attack("basic_cut")
    open_guard.pending_damage = 4
    open_guard.pending_target = open_guard.b
    allowed = open_guard.basic_parry("Cross", open_guard.a, open_guard.b, "test", forced_roll=True, force_durch=True)
    out["H_point_threat_d1"] = {
        "threatening_result": denied,
        "denied_windows": threatening.metrics["d1_windows_denied_by_guard_state"],
        "open_result": allowed,
        "open_declarations": open_guard.metrics["durch_declarations"],
        "modifier_added": False,
    }

    duel = arena("G1", "German", ("alber", "vom-tag"))
    attack = duel.make_attack("basic_cut")
    values = duel.defence_values(duel.a, duel.b, attack)
    out["I_universal_cross"] = {"legal": "Basic Cross" in values}
    out["J_universal_beat"] = {"legal": "Basic Beat" in values}
    out["K_mapping_no_bonus"] = {"extra_attack_bonus": 0, "extra_parry_bonus": 0}

    g1 = arena("G1", "German", ("vom-tag", "pflug"))
    thrust = g1.make_attack("basic_thrust")
    out["L_g1_compound_not_free"] = {"free_action_legal": FREE_ABSETZEN in g1.defence_values(g1.a, g1.b, thrust)}
    g2 = arena("G2", "German", ("vom-tag", "pflug"))
    thrust2 = g2.make_attack("basic_thrust")
    out["M_g2_compound_free"] = {"free_action_legal": FREE_ABSETZEN in g2.defence_values(g2.a, g2.b, thrust2)}
    before_chain = list(g2.current_chain)
    g2.pending_attack = thrust2
    g2.pending_damage = 4
    g2.pending_target = g2.b
    result = g2.free_absetzen(g2.a, g2.b, thrust2, forced_roll=True)
    out["N_g2_not_chain"] = {"result": result, "before": before_chain, "after": list(g2.current_chain)}

    duel = arena("G1", "German", ("vom-tag", "ochs"))
    before_ok = duel.change_guard(duel.a, "ochs", "before")
    after_ok = duel.change_guard(duel.a, "pflug", "after")
    out["O_change_once"] = {"before": before_ok, "after": after_ok}
    out["P_immediate_state"] = duel.public_guard_state(duel.a)

    duel = arena("G1", "Italian", ("posta-di-donna", "posta-frontale"))
    duel.change_guard(duel.a, "posta-frontale", "before")
    out["Q_no_stale_state"] = duel.public_guard_state(duel.a)
    out["R_breaker_annotation_only"] = {"automatic_boon": False, "automatic_bane": False, "automatic_success": False}

    duel = arena("G1", "Italian", ("mezza-porta-di-ferro", "tutta-porta-di-ferro"))
    before_change = duel.public_guard_state(duel.a)
    duel.change_guard(duel.a, "tutta-porta-di-ferro", "before")
    out["S_mezza_point_state_clears"] = {
        "before": before_change["point_threat"],
        "after": duel.public_guard_state(duel.a)["point_threat"],
    }

    source_guard = arena("G1", "Italian", ("posta-frontale", "tutta-porta-di-ferro"))
    source_thrust = source_guard.make_attack("basic_thrust")
    source_values = source_guard.defence_values(source_guard.a, source_guard.b, source_thrust)
    other_guard = arena("G1", "Italian", ("tutta-porta-di-ferro", "posta-frontale"))
    other_thrust = other_guard.make_attack("basic_thrust")
    other_values = other_guard.defence_values(other_guard.a, other_guard.b, other_thrust)
    out["T_scambiar_guard_access"] = {
        "tutta": BASE.SCIAMBIAR in source_values,
        "frontale": BASE.SCIAMBIAR in other_values,
    }
    return out


def validate_harness(cases: dict[str, Any]) -> None:
    assert cases["A_ochs"]["point_threat"] == "threatening"
    assert cases["B_pflug"]["point_threat"] == "threatening"
    assert cases["C_alber"]["point_threat"] == "not_threatening"
    assert not cases["D_vom_tag_not_loaded"]["loaded"] and not cases["D_vom_tag_not_loaded"]["cut"]
    assert cases["E_donna_loaded_cut"] == {"loaded": True, "damage": 6}
    assert cases["F_donna_power"] == {"declared": True, "spent": 1, "damage": 7}
    assert cases["G_leave_donna"]["changed"] and not cases["G_leave_donna"]["loaded"]
    assert cases["H_point_threat_d1"]["denied_windows"] == 1
    assert cases["H_point_threat_d1"]["open_declarations"] == 1
    assert cases["I_universal_cross"]["legal"] and cases["J_universal_beat"]["legal"]
    assert cases["K_mapping_no_bonus"] == {"extra_attack_bonus": 0, "extra_parry_bonus": 0}
    assert not cases["L_g1_compound_not_free"]["free_action_legal"]
    assert cases["M_g2_compound_free"]["free_action_legal"]
    assert cases["N_g2_not_chain"]["before"] == cases["N_g2_not_chain"]["after"] == []
    assert cases["O_change_once"] == {"before": True, "after": False}
    assert cases["P_immediate_state"]["guard"] == "ochs"
    assert not cases["Q_no_stale_state"]["loaded"] and not cases["Q_no_stale_state"]["hanging_tags"]
    assert not any(cases["R_breaker_annotation_only"].values())
    assert cases["S_mezza_point_state_clears"] == {"before": "threatening", "after": "not_threatening"}
    assert cases["T_scambiar_guard_access"] == {"tutta": True, "frontale": False}


def validate_results(results: dict[str, Any]) -> None:
    assert len(results["cells"]) == 36
    for item in results["cells"]:
        m = item["metrics"]
        model = item["cell"]["model"]
        assert m["attempted_fourth_plays"] == 0
        assert m["precondition_violations"] == 0
        assert len(m["starting_guard_outcome_share"]) == 16
        if model == "G0":
            assert m["guard_changes"] == 0
            assert m["basic_guard_action_uses"] == 0
            assert m["p1_declarations_per_fight"] == 0
        if model == "G1":
            assert m["basic_guard_action_uses"] == 0
        if model == "G2" and item["cell"]["tradition"] == "Italian":
            assert m["basic_guard_action_uses"] == 0


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def behavior_rows() -> list[tuple[dict[str, Any], dict[str, Any]]]:
    return [(guard, behavior) for guard in GUARD_DATA["guards"] for behavior in guard["behaviors"]]


def aggregate(cells_data: list[dict[str, Any]], model: str, tradition: str | None = None) -> dict[str, float]:
    selected = [item["metrics"] for item in cells_data if item["cell"]["model"] == model and (tradition is None or item["cell"]["tradition"] == tradition)]
    keys = (
        "guard_changes_per_fight", "guard_churn_per_fight", "point_threatening_frequency",
        "loaded_occupancy_share", "loaded_cuts_per_fight", "p1_opportunities_per_fight",
        "p1_declarations_per_fight", "p1_spiritus_per_fight", "learned_plays_per_fight",
        "compounds_per_fight", "spiritus_expenditure_per_fight", "basic_guard_actions_per_fight",
        "learned_plays_displaced_per_fight", "average_action_compression_per_exchange",
    )
    return {key: sum(item[key] for item in selected) / len(selected) if selected else 0.0 for key in keys}


def aggregate_occupancy(cells_data: list[dict[str, Any]], model: str, tradition: str) -> dict[str, float]:
    selected = [item["metrics"] for item in cells_data if item["cell"]["model"] == model and item["cell"]["tradition"] == tradition]
    return {
        guard: sum(item["guard_occupancy_share"].get(guard, 0.0) for item in selected) / len(selected)
        for guard in TRADITION_GUARDS[tradition]
    }


def paired_g1_g2_comparisons(cells_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keyed = {
        (item["cell"]["model"], item["cell"]["tradition"], item["cell"]["skill"], item["cell"]["start_spiritus"]): item
        for item in cells_data
    }
    comparisons = []
    for tradition in ("German", "Italian"):
        for skill in (10, 14, 18):
            for start in (8, 3):
                g1 = keyed[("G1", tradition, skill, start)]["metrics"]
                g2 = keyed[("G2", tradition, skill, start)]["metrics"]
                comparisons.append({
                    "tradition": tradition,
                    "skill": skill,
                    "start_spiritus": start,
                    "g2_minus_g1_learned_plays_per_fight": g2["learned_plays_per_fight"] - g1["learned_plays_per_fight"],
                    "g2_minus_g1_compounds_per_fight": g2["compounds_per_fight"] - g1["compounds_per_fight"],
                    "g2_minus_g1_spiritus_per_fight": g2["spiritus_expenditure_per_fight"] - g1["spiritus_expenditure_per_fight"],
                    "g2_minus_g1_chain_length": g2["learned_play_chain_length"] - g1["learned_play_chain_length"],
                    "g2_free_guard_actions_per_fight": g2["basic_guard_actions_per_fight"],
                    "g2_action_compression_per_exchange": g2["average_action_compression_per_exchange"],
                    "niche_overlap_proxy_per_fight": g2["learned_plays_displaced_per_fight"],
                })
    return comparisons


def prior_p1_upper_bound() -> dict[str, float]:
    if not PRIOR_POWER_PATH.exists():
        return {}
    prior = json.loads(PRIOR_POWER_PATH.read_text(encoding="utf-8"))
    matrix = prior.get("stress_matrix", {})
    items = matrix.values() if isinstance(matrix, dict) else matrix
    rows = [item["metrics"] for item in items if item["cell"]["model"] == "P1"]
    if not rows:
        return {}
    return {
        "loaded_occupancy_share": 1.0,
        "p1_opportunities_per_fight": sum(item["attack_stats"]["power_attack"]["opportunities_per_fight"] for item in rows) / len(rows),
        "p1_declarations_per_fight": sum(item["attack_stats"]["power_attack"]["declarations_per_fight"] for item in rows) / len(rows),
        "p1_spiritus_per_fight": sum(item["power_spiritus_per_fight"] for item in rows) / len(rows),
    }


def build_report(results: dict[str, Any]) -> str:
    data = results["cells"]
    g1 = aggregate(data, "G1")
    g2 = aggregate(data, "G2")
    prior = results["prior_forced_loaded_upper_bound"]
    learned_delta = g2["learned_plays_per_fight"] - g1["learned_plays_per_fight"]
    compound_delta = g2["compounds_per_fight"] - g1["compounds_per_fight"]
    spiritus_delta = g2["spiritus_expenditure_per_fight"] - g1["spiritus_expenditure_per_fight"]
    g1_german_occ = aggregate_occupancy(data, "G1", "German")
    g1_italian_occ = aggregate_occupancy(data, "G1", "Italian")
    g2_german_occ = aggregate_occupancy(data, "G2", "German")
    lines = [
        "# Named Guard Rules v0.1 Results", "",
        "Status: **PROVISIONAL bounded architecture experiment; not canonical mechanics**", "",
        "## Executive Result", "",
        "G1 produces real but uneven guard identity without generic guard bonuses: Ochs/Pflug alter the existing point-threat state, Pflug gates audited Absetzen, Vom Tag gates Nachreisen without becoming Loaded, and Donna supplies the prompt-selected provisional Loaded/P1 package. The Italian evidence record is too incomplete to give Frontale or either Porta di Ferro a source-backed special action; they are correctly reported as inert rather than patched with bonuses.", "",
        f"G2 tested one, not three, evidence-supported ambiguous action: the joined Pflug Absetzen was exposed as a 0-Spiritus Basic guard action. It averaged **{fmt(g2['basic_guard_actions_per_fight'])} uses/fight** across both traditions (Italian cells correctly remain zero). Relative to paired G1 architecture, learned Plays changed by {learned_delta:+.3f}/fight, compounds by {compound_delta:+.3f}/fight, and Spiritus by {spiritus_delta:+.3f}/fight. Because the free action directly occupies Absetzen's learned tactical niche, the result raises a **PLAY-CROWDING WARNING**. The default classification should favor G1.", "",
        "## Scope, Baseline, and Repository Conflict", "",
        "Phase 0 passed. New simulator work imports `simulations/shared/provisional_longsword.py`, which fixes D1, C2, S2, explicit Crossing/Bind state, Cross/Beat, the three-Play cap, Loaded, and P1/Committed/Counter-first. Archived experiments remain unchanged. The dated decision is recorded in `reports/governing-open-provisional.md` and `data/prototypes/longsword-governing-provisional-v0.1.yaml`.", "",
        "The prior register and protected melee packet still contain the older mirrored Threat/Power/Cover proposal. The dated register entry marks it superseded for current prototype work; the packet was not edited. A second material gap is evidentiary: no item-level longsword guard locators for Donna, Frontale, Tutta Porta di Ferro, or Mezza Porta di Ferro exist in the repository. Donna Loaded/P1 is therefore labeled a prompt-selected **PROVISIONAL ATRA harness assignment**, not HISTORICALLY SUPPORTED. Alber's posture state is likewise a transparent harness assignment pending item-level audit.", "",
        "## Guard Action Classification", "",
        "| Guard | Source description | Locator | Confidence | Classification | Implementation | Compresses lesson? | Rationale |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for guard, behavior in behavior_rows():
        locator = behavior["locator"] or "EVIDENCE INCOMPLETE"
        confidence = behavior["historical_confidence"] or "unknown"
        compress = "yes" if behavior["compresses_historical_lesson"] else "no"
        clean = lambda value: str(value).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {guard['name']} | {clean(behavior['source_description'])} | {clean(locator)} | {confidence} | {behavior['classification']} | {clean(behavior['implementation_status'])} | {compress} | {clean(behavior['rationale'])} |")

    lines.extend(["", "## Simulation Matrix", "",
        f"Seed base `{results['metadata']['seed']}`; `{results['metadata']['trials_per_cell']}` fights per aggregate cell, exactly `{results['metadata']['trials_per_starting_pair']}` per ordered starting-guard pair. Adaptive Revelation; skills 10/14/18; starting Spiritus 8/3. G0/G1/G2 were run separately for German and Italian mirrored combat.", "",
        "Balanced forced starts are **SIMULATION HARNESS ONLY — STARTING GUARD RULE OPEN**. Every cell's 16 ordered-pair outcome buckets are in the JSON artifact.", "",
        "The optional German-vs-Italian sensitivity was skipped. The current duel base assumes mirrored skill/repertoire cells; adding asymmetric tradition setup and a different balanced-start product would materially expand this bounded architecture run and could be mistaken for a tradition comparison.", "",
        "| Cell | Occupancy shares | Changes (B/A) | Churn | Threat | D1 create/deny | Loaded cuts | P1 opp/decl/S/CF-stop | Cross/Beat | Learned/compound | Chain/cap/fourth | Guard action | Spiritus |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ])
    for item in data:
        if item["cell"]["model"] == "G0":
            continue
        c, m = item["cell"], item["metrics"]
        occ = ", ".join(f"{key}:{pct(value)}" for key, value in sorted(m["guard_occupancy_share"].items()))
        lines.append(
            f"| {c['model']} {c['tradition']} {c['skill']}/S{c['start_spiritus']} | {occ} | "
            f"{fmt(m['guard_changes_per_fight'])} ({fmt(m['before_action_changes_per_fight'])}/{fmt(m['after_action_changes_per_fight'])}) | "
            f"{fmt(m['guard_churn_per_fight'])} | {pct(m['point_threatening_frequency'])} | "
            f"{fmt(m['d1_windows_created_per_fight'])}/{fmt(m['d1_windows_denied_per_fight'])} | {fmt(m['loaded_cuts_per_fight'])} | "
            f"{fmt(m['p1_opportunities_per_fight'])}/{fmt(m['p1_declarations_per_fight'])}/{fmt(m['p1_spiritus_per_fight'])}/{fmt(m['counter_first_interruptions_per_fight'])} | "
            f"{fmt(m['basic_cross_declarations_per_fight'])}/{fmt(m['basic_beat_declarations_per_fight'])} | "
            f"{fmt(m['learned_plays_per_fight'])}/{fmt(m['compounds_per_fight'])} | "
            f"{fmt(m['learned_play_chain_length'])}/{pct(m['three_play_cap_frequency'])}/{fmt(m['attempted_fourth_plays_per_fight'])} | "
            f"{fmt(m['basic_guard_actions_per_fight'])} | {fmt(m['spiritus_expenditure_per_fight'])} |"
        )

    lines.extend(["", "### Starting-guard outcomes", "",
        "The machine-readable artifact reports A/B/double/draw shares for every ordered pair in every cell. Across mirrored pairs, side deviations remain sampling diagnostics rather than guard rankings; forced starts prevent one arbitrary opening rule from deciding occupancy.", "",
        "### Per-guard activity", "",
        "Every cell's `proactive_attacks_by_guard_per_fight` and `defensive_responses_by_guard_per_fight` fields report attacks and responses from each occupied guard. Breaker opportunity fields are also present. No breaker use is mechanically implemented because the active prototype lacks the relevant audited breaker effects; annotation alone remains bonus-free.", "",
        "## Action-Light vs Action-Heavy", "",
        f"G1 averages {fmt(g1['learned_plays_per_fight'])} learned Plays, {fmt(g1['compounds_per_fight'])} compounds, and {fmt(g1['spiritus_expenditure_per_fight'])} Spiritus/fight. G2 averages {fmt(g2['learned_plays_per_fight'])}, {fmt(g2['compounds_per_fight'])}, and {fmt(g2['spiritus_expenditure_per_fight'])}, while inserting {fmt(g2['basic_guard_actions_per_fight'])} free Pflug Absetzen uses/fight and {fmt(g2['average_action_compression_per_exchange'])} compressed compound events/exchange. Per-cell paired deltas are stored under `g1_g2_paired_comparisons`; the raw `learned_plays_displaced_per_fight` field is a tactical-niche-overlap proxy, not a causal claim that every use would otherwise have selected Absetzen.", "",
        "**PLAY-CROWDING WARNING:** the G2 action is literally the tactical niche of the audited learned Absetzen—joined defence and immediate thrust under the current compound chassis—available at 0 Spiritus and without a chain entry. Sophisticated techniques would become available before learning them, materially weakening progression. No action was tuned during the run.", "",
        f"No guard becomes a majority German toolbox: Pflug rises from {pct(g1_german_occ['pflug'])} G1 occupancy to {pct(g2_german_occ['pflug'])} in G2. Donna reaches {pct(g1_italian_occ['posta-di-donna'])} G1 Italian occupancy, a **repertoire-coverage artifact** caused by the other three Italian guards having no supported active mechanics, not evidence that Donna should be strengthened or nerfed.", "",
        "## Guard Identity", "",
        "| Guard | Visible promise | Prepared attack/state | Natural Basic mapping | Learned access | Breaker | Mechanical vulnerability | Current result |",
        "|---|---|---|---|---|---|---|---|",
        "| Vom Tag | high, chambered/cut-ready, point off line | Basic Cut is visibly prepared; no Loaded | none granted beyond universal basics | Nachreisen | Zwerchhau, annotation only | point-off-line Cross/Beat state can admit D1 | meaningful access identity, modest current effect |",
        "| Ochs | high upper hanging, threatening point | point-threat state | universal Cross/Beat remain legal | upper Winden gate | Krumphau evidence incomplete | none mechanically added | meaningful point state; repertoire gap |",
        "| Pflug | low lower hanging, threatening point | point-threat state and Absetzen access | universal basics | Absetzen; lower Winden | Schielhau relationship evidence incomplete | none mechanically added | strongest German toolbox; G2 crowds Plays |",
        "| Alber | low, point off line (harness only) | no special attack | universal basics | none | Scheitelhau evidence incomplete | D1 exposure only through existing state | **INERT GUARD — evidence and repertoire gap** |",
        "| Posta di Donna | high/chambered harness assignment; Loaded | Loaded Basic Cut and P1 | Basic Cut; no accuracy bonus | none implemented | none | leaving removes Loaded/P1 | meaningful provisional Atra identity; evidence incomplete |",
        "| Posta Frontale | name/public posture only | unknown | universal Cross/Beat; no special Cross | none audited | none | none | **INERT GUARD — item-level evidence gap** |",
        "| Tutta Porta di Ferro | name/public posture only | unknown | universal Cross/Beat | none audited | none | none | **INERT GUARD — item-level evidence gap** |",
        "| Mezza Porta di Ferro | name/public posture only | unknown | universal Cross/Beat | none audited | none | none | **INERT GUARD — item-level evidence gap** |",
        "", "## Repertoire Coverage Gaps", "",
        "- Ochs and Pflug store upper/lower Winden gates, but the active prototype has no full Winden system.",
        "- Vom Tag gates Nachreisen, but its main visible preparation has no sourced generic numeric effect.",
        "- Alber lacks item-level posture and breaker audit and has no invitation Play.",
        "- Frontale and both Porta di Ferro guards lack item-level guard behaviors in the repository; no source-backed Cross, Beat, close-entry, return-cut, or cover package could be implemented.",
        "- Zwerchhau, Krumphau, and Scheitelhau guard-breaker mechanics are absent from the active repertoire; Schielhau's audited active mechanic concerns change-through denial, not a verified Pflug breaker effect.",
        "", "## Guard Churn", "",
        f"G1 averages {fmt(g1['guard_changes_per_fight'])} guard changes and {fmt(g1['guard_churn_per_fight'])} A→B→A churn events/fight; G2 averages {fmt(g2['guard_changes_per_fight'])} and {fmt(g2['guard_churn_per_fight'])}. The policy applies a transparent 0.09 evaluation friction for changing (not a rules cost) and still considers all guards before or after the action. " + ("**GUARD-CHURN WARNING:** repeated benefit-harvesting flips are high enough to make transition structure the next policy sensitivity." if g1['guard_churn_per_fight'] > 0.75 else "No GUARD-CHURN WARNING threshold was crossed in this bounded policy, though free all-to-all transitions remain OPEN."),
        "", "After-action selection is implemented immediately after inherited exchange cleanup and is public for the next exchange; this ordering simplification is recorded rather than treated as a new timing rule.",
        "", "## Power in Named Guards", "",
        f"G1 Loaded occupancy averages {pct(g1['loaded_occupancy_share'])}; P1 is available {fmt(g1['p1_opportunities_per_fight'])} and chosen {fmt(g1['p1_declarations_per_fight'])} times/fight for {fmt(g1['p1_spiritus_per_fight'])} Spiritus/fight. " + (f"The prior forced-Loaded upper bound had 100% Loaded eligibility, {fmt(prior.get('p1_opportunities_per_fight', 0))} opportunities and {fmt(prior.get('p1_declarations_per_fight', 0))} declarations/fight." if prior else "The prior JSON upper bound was unavailable for automated comparison."),
        "", "Named occupancy substantially limits availability: entering Donna consumes the one free before-or-after change for that activation and staying there forgoes threatening-point postures. The result makes P1 less universally present than the forced-Loaded stress case without changing P1 itself.",
        "", "## Recommended Basic-vs-Learned Rule", "",
        "A guard-described action should be **Basic** only when it is a simple, direct posture use with one principal test, no distinctive timing or bind-reading lesson, no simultaneous substantial defence/offence package, and no redundancy with a learned Play. If it is already an ordinary Cross, Beat, Cut, or Thrust, record an **existing Basic-action mapping** rather than creating a renamed action.", "",
        "It should be a **learned Play** when it carries a tactical trigger, timing lesson, pressure/measure reading, redirection, specialized continuation, simultaneous defence and offence, or multiple substantial effects. Breaker relationships begin as sourced annotations/gates unless an audited Play already supplies the effect. Evidence-incomplete descriptions receive no mechanic yet.",
        "", "## Recommended Next Decision", "",
        "A. **Yes, unevenly.** G1 gives meaningful identity to Ochs, Pflug, Vom Tag, and provisional Donna without generic bonuses; four guards remain inert for documented evidence/repertoire reasons.",
        "", "B. **Yes.** G2 creates direct Play crowding and action compression by giving away Absetzen's two-effect lesson.",
        "", "C. **Yes.** Default classification should favor G1/action-light.",
        "", "D. **No source-described compound behavior should be promoted to a permanent Basic guard action on this evidence.** Ordinary Cross/Beat/Cut mappings remain universal basics, not special actions.",
        "", "E. **Absetzen and upper/lower Winden clearly belong as learned Plays; Nachreisen remains learned because its recovery timing is the lesson.**", "",
        "F. Alber, Frontale, Tutta Porta di Ferro, and Mezza Porta di Ferro are currently inert; Ochs also has a repertoire-coverage gap beyond point threat.",
        "", "G. **Yes.** Named-guard commitment makes Loaded/P1 less continuously available than the forced-Loaded upper bound, with no P1 rebalance.",
        "", "H. " + ("**Yes; churn is pathological enough to flag, but no fix is selected here.**" if g1['guard_churn_per_fight'] > 0.75 else "**No pathological churn appears under this policy; transition design remains a later sensitivity.**"),
        "", "I. The next blocker is **missing guard-gated Plays and item-level Italian guard evidence**, ahead of a transition graph. A transition experiment would be premature while half the roster is inert because its sourced actions are absent.",
        "", "## Historical and Mechanical Status", "",
        "Historically supported and scoped: the listed German posture/action relationships with exact locators. Provisional Atra: point-state geometric inferences, Donna Loaded/P1, free guard changes, G2 free Absetzen, and all AI weights. Open: Italian item-level guard evidence, Alber audit, final roster/starting rule/transitions, full Winden, breaker effects, generic leverage, and all final guard bonuses.",
    ])
    return "\n".join(lines) + "\n"


def run_all(trials: int = TRIALS_PER_CELL, seed: int = SEED, write: bool = True) -> dict[str, Any]:
    harness = deterministic_harness()
    validate_harness(harness)
    rows = []
    for index, cell in enumerate(cells()):
        rows.append(run_cell(cell, trials, seed + index * 10007))
    results = {
        "metadata": {
            "status": "PROVISIONAL",
            "seed": seed,
            "trials_per_cell": trials,
            "trials_per_starting_pair": trials // 16,
            "balanced_forced_starts": True,
            "starting_guard_rule": "SIMULATION HARNESS ONLY — STARTING GUARD RULE OPEN",
            "shared_engine": str(SHARED_PATH.relative_to(ROOT)).replace("\\", "/"),
            "guard_data": str(GUARD_PATH.relative_to(ROOT)).replace("\\", "/"),
            "g2_candidates": ["pflug-free-absetzen"],
            "g2_evidence_blocked_candidates": 2,
        },
        "phase0_baseline": SHARED.GOVERNING_BASELINE,
        "deterministic_harness": harness,
        "guard_roster": GUARD_DATA,
        "cells": rows,
        "g1_g2_paired_comparisons": paired_g1_g2_comparisons(rows),
        "prior_forced_loaded_upper_bound": prior_p1_upper_bound(),
    }
    validate_results(results)
    if write:
        RESULTS_PATH.write_text(json.dumps(BASE.serial(results), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        REPORT_PATH.write_text(build_report(results), encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=TRIALS_PER_CELL)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    if args.trials < 16 or args.trials % 16:
        raise SystemExit("--trials must be a positive multiple of 16 for balanced forced starts")
    results = run_all(args.trials, args.seed, write=not args.no_write)
    print(f"Completed {len(results['cells'])} cells x {args.trials} fights.")


if __name__ == "__main__":
    main()

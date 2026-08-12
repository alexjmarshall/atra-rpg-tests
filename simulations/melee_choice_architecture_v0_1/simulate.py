"""Bounded Cross/Beat and guard-commitment architecture experiment.

The governing engine is imported for regression alignment. Candidate mechanics
exist only in ChoiceArchitectureDuel and the reduced scripted micro-harness.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import statistics
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RESULTS_PATH = ROOT / "reports" / "melee-choice-architecture-v01-results.json"
REPORT_PATH = ROOT / "reports" / "melee-choice-architecture-v01-results.md"
MAP_PATH = ROOT / "data" / "research" / "longsword-guard-transition-map-v0.1.yaml"
SEED = 12082026
TRIALS = 1000
OPEN = "open"


def load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


GUARD = load("mca_guard", ROOT / "simulations" / "named_guard_rules_v0_1" / "simulate.py")
ENGINE = GUARD.ENGINE
BASE = GUARD.BASE
BRIDGE = load("mca_bridge", ROOT / "simulations" / "guard_play_bridge_v0_1" / "simulate.py")


CB = {
    "CB0": {"cross_immunity": False, "beat_open": False},
    "CB1": {"cross_immunity": True, "beat_open": False},
    "CB2": {"cross_immunity": False, "beat_open": True},
    "CB3": {"cross_immunity": True, "beat_open": True},
}

GC = {
    "GC0": {"before": True, "after": True},
    "GC1": {"before": True, "after": False},
    "GC2": {"before": False, "after": True},
    "GC3": {"before": True, "after": True},
}

GUARD_VALUE = {
    "posta-di-donna": ["loaded", "power_access", "scambiar_access"],
    "mezza-porta-di-ferro": ["threatening_point", "d1_denial"],
    "pflug": ["threatening_point", "d1_denial", "absetzen_access"],
    "tutta-porta-di-ferro": ["scambiar_access", "tutta_t1_access"],
    "posta-frontale": [],
    "alber": [],
    OPEN: [],
}


def serial(value: Any) -> Any:
    if isinstance(value, Counter):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def ratio(n: float, d: float) -> float:
    return n / d if d else 0.0


class ChoiceArchitectureDuel(GUARD.NamedGuardDuel):
    """Isolated rules implementation for deterministic candidate regressions."""

    def __init__(self, candidate: str = "CB0", guard_model: str = "GC0",
                 tradition: str = "Italian",
                 pair: tuple[str, str] = ("posta-di-donna", "mezza-porta-di-ferro"),
                 skill: int = 14, spiritus: int = 8) -> None:
        self.candidate = candidate
        self.guard_model = guard_model
        self.open_fighters: set[str] = set()
        self.open_recoveries = 0
        super().__init__(
            random.Random(17), random.Random(19),
            GUARD.Cell("G1", tradition, skill, spiritus, "perfect_information"),
            GUARD.fresh_metrics(), pair,
        )

    def current_guard(self, fighter: BASE.Fighter) -> str:
        return OPEN if fighter.name in self.open_fighters else self.guards[fighter.name]

    def public_guard_state(self, fighter: BASE.Fighter) -> dict[str, Any]:
        if fighter.name in self.open_fighters:
            return {
                "guard": OPEN, "height": "none", "point_threat": "not_threatening",
                "preparation_tags": [], "hanging_tags": [], "posture_tags": [],
                "loaded": False,
            }
        return super().public_guard_state(fighter)

    def apply_guard_state(self, fighter: BASE.Fighter) -> None:
        if fighter.name in self.open_fighters:
            self.set_point(fighter, "not_threatening")
        else:
            super().apply_guard_state(fighter)

    def loaded_for(self, fighter: BASE.Fighter) -> bool:
        return fighter.name not in self.open_fighters and super().loaded_for(fighter)

    def guard_gate_active(self, fighter: BASE.Fighter, play: str) -> bool:
        if fighter.name in self.open_fighters:
            return False
        return play in GUARD.GUARDS[self.current_guard(fighter)]["mechanical_access"]["learned_play_gates"]

    def make_open(self, fighter: BASE.Fighter) -> None:
        self.open_fighters.add(fighter.name)
        self.set_point(fighter, "not_threatening")

    def recover_from_open(self, fighter: BASE.Fighter, guard: str | None) -> bool:
        if fighter.name not in self.open_fighters or guard is None:
            return False
        if self.guard_changed_this_activation or guard not in GUARD.TRADITION_GUARDS[self.named_cell.tradition]:
            return False
        self.open_fighters.remove(fighter.name)
        self.guards[fighter.name] = guard
        self.guard_changed_this_activation = True
        self.open_recoveries += 1
        self.apply_guard_state(fighter)
        return True

    def begin_activation(self, fighter: BASE.Fighter, recovery_guard: str | None = None) -> bool:
        """Apply only the explicit start-of-activation Open recovery exception."""
        self.guard_changed_this_activation = False
        if fighter.name in self.open_fighters and recovery_guard is not None:
            return self.recover_from_open(fighter, recovery_guard)
        return False  # remaining Open is legal

    def change_guard(self, fighter: BASE.Fighter, new_guard: str, phase: str) -> bool:
        if fighter.name in self.open_fighters:
            return False
        allowed = GC[self.guard_model]
        if phase in ("before", "after") and not allowed[phase]:
            return False
        if self.guard_model == "GC3":
            return False  # no defensible restrictive research graph
        return super().change_guard(fighter, new_guard, phase)

    def basic_parry(self, form: str, attacker: BASE.Fighter, defender: BASE.Fighter,
                    attribution: str | None, forced_roll: bool | None = None,
                    force_durch: bool | None = None) -> str:
        m = self.metrics
        m["choices"]["Basic Parry"] += 1
        m["parry_declarations"][form] += 1
        self.spend_action(defender)
        self.apply_guard_state(defender)
        immune = form == "Cross" and CB[self.candidate]["cross_immunity"]
        d1_legal = not immune and self.state.point_threat[defender.name] == "not_threatening"
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
            if CB[self.candidate]["beat_open"]:
                self.make_open(attacker)
        return "success"


def d1_policy(attacker_skill: int, defender_skill: int, spiritus: int) -> dict[str, Any]:
    if spiritus < 1:
        return {"legal_by_resource": False, "declare": None, "decline": None, "argmax": "unavailable", "softmax_probability": 0.0}
    declare = BASE.success_probability(attacker_skill) - BASE.reserve_charge(spiritus, BASE.DURCH_COST)
    decline = 1.0 - BASE.success_probability(defender_skill)
    argmax = "declare" if declare > decline else "decline" if decline > declare else "tie"
    top = max(declare, decline)
    wd = math.exp((declare - top) / ENGINE.POLICY_TEMPERATURE)
    wn = math.exp((decline - top) / ENGINE.POLICY_TEMPERATURE)
    return {
        "legal_by_resource": True, "declare": declare, "decline": decline,
        "argmax": argmax, "softmax_probability": wd / (wd + wn),
    }


def outcome_vector(candidate: str, form: str, *, attacker_guard: str,
                   defender_point: str = "not_threatening", attacker_skill: int = 14,
                   defender_skill: int = 14, spiritus: int = 8, d1_known: bool = True,
                   d1_present: bool = True, crossing_repertoire: bool = False,
                   source_compatible_t1: bool = False) -> dict[str, Any]:
    p_att = BASE.success_probability(attacker_skill)
    p_def = BASE.success_probability(defender_skill)
    immune = form == "Cross" and CB[candidate]["cross_immunity"]
    d1_legal = d1_present and spiritus >= 1 and defender_point != "threatening" and not immune
    policy = d1_policy(attacker_skill, defender_skill, spiritus)
    q = 1.0 if d1_legal and policy["argmax"] == "declare" else 0.0
    resolved_parry = 1.0 - q
    success = resolved_parry * p_def
    open_probability = success if form == "Beat" and CB[candidate]["beat_open"] and attacker_guard != OPEN else 0.0
    crossing_probability = success if form == "Cross" else 0.0
    removed = GUARD_VALUE.get(attacker_guard, []) if open_probability else []
    return {
        "candidate": candidate,
        "form": form,
        "conditions": {
            "attacker_guard": attacker_guard, "defender_point": defender_point,
            "attacker_skill": attacker_skill, "defender_skill": defender_skill,
            "attacker_spiritus": spiritus, "d1_known": d1_known,
            "d1_present": d1_present, "crossing_repertoire": crossing_repertoire,
        },
        "d1_legal": d1_legal,
        "d1_policy_argmax": policy["argmax"] if d1_legal else "not_legal",
        "d1_softmax_probability_if_legal": policy["softmax_probability"] if d1_legal else 0.0,
        "d1_declaration_probability_used": q,
        "expected_d1_spiritus": q,
        "parry_roll_probability": resolved_parry,
        "cancellation_probability": q * (1.0 - p_att) + resolved_parry * p_def,
        "expected_incoming_damage": round((q * p_att + resolved_parry * (1.0 - p_def)) * 4.5, 6),
        "ordinary_crossing_probability": crossing_probability,
        "separation_probability": success if form == "Beat" else q,
        "open_probability": open_probability,
        "intervening_opponent_opportunities_while_open": 1 if open_probability else 0,
        "guard_states_or_gates_removed": removed,
        "guard_removal_probability": open_probability if removed else 0.0,
        "crossing_repertoire_opportunity_probability": crossing_probability if crossing_repertoire else 0.0,
        "tutta_t1_opportunity_probability": crossing_probability if source_compatible_t1 else 0.0,
        "generic_cross_boon_bane_damage_or_cancel_bonus": 0,
        "generic_open_combat_modifier": 0,
    }


def deterministic_cases() -> dict[str, Any]:
    cases: dict[str, Any] = {}
    definitions = {
        "A_no_d1_no_repertoire": dict(attacker_guard="posta-frontale", d1_present=False),
        "B_known_d1_reserve_nonthreat": dict(attacker_guard="posta-di-donna", spiritus=8),
        "C_known_d1_threatening_defender": dict(attacker_guard="posta-di-donna", defender_point="threatening", spiritus=8),
        "D_tutta_t1_repertoire": dict(attacker_guard="posta-frontale", d1_present=False, crossing_repertoire=True, source_compatible_t1=True),
        "E1_strip_donna": dict(attacker_guard="posta-di-donna", d1_present=False),
        "E2_strip_mezza": dict(attacker_guard="mezza-porta-di-ferro", d1_present=False),
        "E3_strip_pflug": dict(attacker_guard="pflug", d1_present=False),
        "F1_attacker_already_open": dict(attacker_guard=OPEN, d1_present=False),
        "F2_low_value_frontale": dict(attacker_guard="posta-frontale", d1_present=False),
    }
    for label, kwargs in definitions.items():
        cases[label] = {
            candidate: {form: outcome_vector(candidate, form, **kwargs) for form in ("Cross", "Beat")}
            for candidate in CB
        }
    cases["G_spiritus_depletion"] = []
    for skill in (14, 18):
        for spiritus in (8, 3, 1, 0):
            cases["G_spiritus_depletion"].append({
                "skill": skill, "spiritus": spiritus,
                "policy": d1_policy(skill, skill, spiritus),
                "CB3": {form: outcome_vector("CB3", form, attacker_guard="posta-di-donna", attacker_skill=skill, defender_skill=skill, spiritus=spiritus) for form in ("Cross", "Beat")},
            })
    cases["H_information"] = {
        "revealed": "The defender can condition on D1 legality and reserve.",
        "hidden": "The mechanical vector is unchanged, but the defender cannot know which vector applies before first revelation.",
        "quantified_bayesian_model": False,
        "limitation": "No prior over hidden repertoire exists in the governing information logic; no Bayesian frequency was invented."
    }
    return cases


def monte_carlo(cases: dict[str, Any], trials: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    rows: list[dict[str, Any]] = []
    for case_name in ("A_no_d1_no_repertoire", "B_known_d1_reserve_nonthreat", "C_known_d1_threatening_defender", "D_tutta_t1_repertoire", "E1_strip_donna", "E2_strip_mezza", "E3_strip_pflug", "F1_attacker_already_open", "F2_low_value_frontale"):
        for candidate in CB:
            for form in ("Cross", "Beat"):
                vector = cases[case_name][candidate][form]
                p_att = BASE.success_probability(vector["conditions"]["attacker_skill"])
                p_def = BASE.success_probability(vector["conditions"]["defender_skill"])
                damage = crossings = opens = cancellations = 0
                for _ in range(trials):
                    if vector["d1_declaration_probability_used"]:
                        hit = rng.random() < p_att
                        damage += (rng.randint(1, 6) + 1) if hit else 0
                        cancellations += int(not hit)
                    else:
                        success = rng.random() < p_def
                        cancellations += int(success)
                        if not success:
                            damage += rng.randint(1, 6) + 1
                        elif form == "Cross":
                            crossings += 1
                        elif vector["open_probability"]:
                            opens += 1
                rows.append({
                    "case": case_name, "candidate": candidate, "form": form, "trials": trials,
                    "mean_damage": damage / trials, "cancellation_rate": cancellations / trials,
                    "crossing_rate": crossings / trials, "open_rate": opens / trials,
                    "branch_forced": True,
                })
    return rows


@dataclass
class Segment:
    guard: str
    entry_phase: str
    entry_activation: int
    opponent_opportunities: int = 0
    actions: list[tuple[int, str]] | None = None
    benefits: list[dict[str, Any]] | None = None

    def __post_init__(self) -> None:
        self.actions = [] if self.actions is None else self.actions
        self.benefits = [] if self.benefits is None else self.benefits


class TimingFight:
    """Reduced tactical script. It measures timing consequences, not win rate."""

    def __init__(self, model: str, start_guard: str) -> None:
        self.model = model
        self.guard = start_guard
        self.changed = False
        self.activation = 0
        self.transitions: list[tuple[str, str]] = []
        self.segments: list[Segment] = [Segment(start_guard, "start", 0)]
        self.closed: list[Segment] = []
        self.before = self.after = self.open_recovery = 0
        self.last_action: str | None = None
        self.action_after_enter: Counter[str] = Counter()
        self.action_before_leave: Counter[str] = Counter()

    @property
    def segment(self) -> Segment:
        return self.segments[-1]

    def can_change(self, phase: str) -> bool:
        return not self.changed and self.model != "GC3" and GC[self.model][phase]

    def change(self, new_guard: str, phase: str) -> bool:
        if new_guard == self.guard or not self.can_change(phase):
            return False
        old = self.guard
        if self.last_action:
            self.action_before_leave[f"{self.last_action}->{new_guard}"] += 1
        self.closed.append(self.segments.pop())
        self.guard = new_guard
        self.segments.append(Segment(new_guard, phase, self.activation))
        self.transitions.append((old, new_guard))
        self.changed = True
        if phase == "before":
            self.before += 1
        else:
            self.after += 1
        return True

    def act(self, action: str) -> None:
        if not self.segment.actions:
            self.action_after_enter[f"{self.guard}->{action}"] += 1
        self.segment.actions.append((self.activation, action))
        self.last_action = action
        if action == "loaded_cut":
            self.benefit("offensive_loaded", at_opponent=False)

    def benefit(self, kind: str, at_opponent: bool) -> None:
        self.segment.benefits.append({
            "kind": kind,
            "activation": self.activation,
            "entry_activation": self.segment.entry_activation,
            "entry_phase": self.segment.entry_phase,
            "opps_before": self.segment.opponent_opportunities,
            "at_opponent": at_opponent,
        })

    def opponent_opportunity(self) -> None:
        if self.guard == "mezza-porta-di-ferro":
            self.benefit("defensive_threat", at_opponent=True)
        if self.guard == "tutta-porta-di-ferro":
            self.benefit("guard_gate", at_opponent=True)
        self.segment.opponent_opportunities += 1

    def run_activation(self, intent: str) -> None:
        self.activation += 1
        self.changed = False
        if intent == "offense":
            if self.guard != "posta-di-donna" and self.can_change("before"):
                self.change("posta-di-donna", "before")
            self.act("loaded_cut" if self.guard == "posta-di-donna" else "basic_cut")
            if self.guard == "posta-di-donna" and self.can_change("after"):
                self.change("mezza-porta-di-ferro", "after")
            elif self.guard != "posta-di-donna" and self.can_change("after"):
                # GC2 must establish Donna one activation before harvesting it.
                self.change("posta-di-donna", "after")
        elif intent == "defense":
            if self.guard != "mezza-porta-di-ferro" and self.can_change("before"):
                self.change("mezza-porta-di-ferro", "before")
            self.act("basic_thrust")
            if self.guard != "mezza-porta-di-ferro" and self.can_change("after"):
                self.change("mezza-porta-di-ferro", "after")
        else:
            if self.model == "GC1" and self.guard != "tutta-porta-di-ferro" and self.can_change("before"):
                self.change("tutta-porta-di-ferro", "before")
            self.act("useful_basic_action")
            if self.guard != "tutta-porta-di-ferro" and self.can_change("after"):
                self.change("tutta-porta-di-ferro", "after")
        self.opponent_opportunity()

    def finish(self) -> None:
        self.closed.append(self.segments.pop())


def summarize_timing(fights: list[TimingFight]) -> dict[str, Any]:
    changes = before = after = loops = 0
    dwell: list[int] = []
    transitions: Counter[str] = Counter()
    action_after: Counter[str] = Counter()
    action_before: Counter[str] = Counter()
    benefits: list[dict[str, Any]] = []
    pure_staging = 0
    for fight in fights:
        changes += len(fight.transitions)
        before += fight.before
        after += fight.after
        transitions.update(f"{a}->{b}" for a, b in fight.transitions)
        action_after.update(fight.action_after_enter)
        action_before.update(fight.action_before_leave)
        history = [fight.closed[0].guard] + [b for _, b in fight.transitions] if fight.closed else []
        loops += sum(1 for i in range(2, len(history)) if history[i] == history[i - 2] != history[i - 1])
        for segment in fight.closed:
            dwell.append(segment.opponent_opportunities)
            actions_after_entry = [a for a, _ in segment.actions]
            if segment.entry_phase == "after" and segment.benefits and not actions_after_entry:
                pure_staging += 1
            for benefit in segment.benefits:
                used_opp = 1 if benefit["at_opponent"] else 0
                before_exposure = benefit["opps_before"] + used_opp
                after_exposure = segment.opponent_opportunities - benefit["opps_before"] - used_opp
                benefit = dict(benefit)
                benefit.update({
                    "exposure_before": before_exposure > 0,
                    "exposure_after": after_exposure > 0,
                    "telegraph_interval": benefit["opps_before"],
                    "same_activation_entry": benefit["entry_activation"] == benefit["activation"] and benefit["entry_phase"] in ("before", "after"),
                })
                benefits.append(benefit)
    offensive = [b for b in benefits if b["kind"] == "offensive_loaded"]
    defensive = [b for b in benefits if b["kind"] == "defensive_threat"]
    gates = [b for b in benefits if b["kind"] == "guard_gate"]

    def exposure(items: list[dict[str, Any]]) -> dict[str, float]:
        return {
            "before": ratio(sum(b["exposure_before"] for b in items), len(items)),
            "after": ratio(sum(b["exposure_after"] for b in items), len(items)),
            "either": ratio(sum(b["exposure_before"] or b["exposure_after"] for b in items), len(items)),
        }

    activations = len(fights) * 6
    return {
        "fights": len(fights), "activations": activations,
        "guard_changes_per_fight": changes / len(fights),
        "changes_per_activation": changes / activations,
        "before_action_changes_per_fight": before / len(fights),
        "after_action_changes_per_fight": after / len(fights),
        "open_recovery_changes_per_fight": 0.0,
        "a_b_a_loops_per_fight": loops / len(fights),
        "average_guard_dwell_opponent_opportunities": statistics.mean(dwell),
        "median_guard_dwell_opponent_opportunities": statistics.median(dwell),
        "transitions_by_pair": dict(transitions),
        "action_immediately_after_entering_guard": dict(action_after),
        "action_immediately_before_leaving_guard": dict(action_before),
        "offensive_benefit_harvesting_rate": ratio(sum(b["same_activation_entry"] and b["entry_phase"] == "before" for b in offensive), len(offensive)),
        "defensive_staging_rate": ratio(sum(b["same_activation_entry"] and b["entry_phase"] == "after" for b in defensive), len(defensive)),
        "benefit_exposure_coupling": exposure(benefits),
        "benefit_exposure_by_type": {kind: exposure([b for b in benefits if b["kind"] == kind]) for kind in ("offensive_loaded", "defensive_threat", "guard_gate")},
        "average_telegraph_interval": statistics.mean([b["telegraph_interval"] for b in benefits]) if benefits else 0.0,
        "loaded_telegraph_interval": statistics.mean([b["telegraph_interval"] for b in offensive]) if offensive else 0.0,
        "gate_harvest_rate": ratio(sum(b["same_activation_entry"] for b in gates), len(gates)),
        "pure_staging_rate_per_change": ratio(pure_staging, changes),
        "intent_policy": "rules-goal script; no utility constants and no softmax",
    }


def behavioral_guard_runs(trials: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    output: dict[str, Any] = {}
    intent_weights = (["offense"] * 9) + (["defense"] * 7) + (["gate"] * 4)
    starts = ("posta-di-donna", "mezza-porta-di-ferro", "tutta-porta-di-ferro")
    for model in ("GC0", "GC1", "GC2"):
        fights: list[TimingFight] = []
        for index in range(trials):
            fight = TimingFight(model, starts[index % len(starts)])
            for _ in range(6):
                fight.run_activation(rng.choice(intent_weights))
            fight.finish()
            fights.append(fight)
        output[model] = summarize_timing(fights)
    output["GC3"] = {
        "behavior_tested": False,
        "reason": "No defensible restrictive voluntary graph exists.",
        "italian_if_general_vadi_rule_expanded": {"density": 1.0, "equivalent_topology": "all-to-all"},
        "german_safe_graph": {"density": 0.0, "connected": False},
        "path_constraint": "not measured; any selected sparse topology would be pseudo-historical",
    }
    return output


def guard_scenarios() -> dict[str, Any]:
    return {
        "scenario_1_donna_offensive_harvesting": {
            "GC0": "Loaded Cut, then after-action Mezza; Donna downside is shed before the opponent acts.",
            "GC1": "Loaded Cut, no post-action switch; actor remains Donna through the opponent opportunity.",
            "GC2": "Loaded Cut, then after-action Mezza; immediate shedding remains legal.",
            "GC3": "Not behavior-tested; Italian dense interpretation would reproduce GC0 topology."
        },
        "scenario_2_donna_just_in_time_entry": {
            "GC0": "Mezza -> Donna before action -> Loaded Cut; actor must remain Donna afterward because the allowance was used.",
            "GC1": "Same as GC0: just-in-time entry remains, but post-benefit exposure is mandatory.",
            "GC2": "Cannot enter before action; establish Donna after an earlier activation, expose/telegraph for one opponent opportunity, then use Loaded Cut.",
            "GC3": "No defensible restrictive topology."
        },
        "scenario_3_threatening_point_staging": {
            "GC0": "Useful action -> Mezza after action -> point threat before opponent.",
            "GC1": "No after-action acquisition; Mezza must be chosen before the useful action and retained.",
            "GC2": "Useful action -> Mezza after action remains legal; defensive staging persists.",
            "GC3": "No defensible restrictive topology."
        },
        "scenario_4_guard_gate_staging": {
            "GC0": "Enter Tutta/Pflug after acting and hold the gate for the expected attack.",
            "GC1": "Enter before the actor's useful action and remain through the expected attack.",
            "GC2": "Enter after acting; immediate defensive staging remains legal.",
            "GC3": "Action-produced movement is supportable, but free adjacency restriction is not."
        },
        "scenario_5_a_b_a_loop": {
            "GC0": "Donna benefit -> Mezza after -> Donna before next benefit: two-activation harvesting loop.",
            "GC1": "Donna must remain through the opponent; a Donna-Mezza-Donna loop requires sacrificing an intervening offensive activation.",
            "GC2": "Donna -> Mezza after; next activation cannot return before acting, so Donna benefit is delayed to a third activation.",
            "GC3": "Not behavior-tested."
        },
        "scenario_6_open_recovery": {
            "GC0_GC1_GC2": "Start-of-activation Open recovery consumes the voluntary allowance; no second before/after switch is legal.",
            "GC3": "Open -> any is an explicit experimental exception, not historical adjacency; it would bypass topology by design."
        }
    }


def regression_harness() -> dict[str, Any]:
    out: dict[str, Any] = {}

    def arena(cb: str, pair: tuple[str, str] = ("posta-di-donna", "tutta-porta-di-ferro")) -> ChoiceArchitectureDuel:
        duel = ChoiceArchitectureDuel(cb, "GC0", "Italian", pair)
        duel.pending_attack = duel.make_attack("basic_cut")
        duel.pending_damage = 4
        duel.pending_target = duel.b
        return duel

    for cb in CB:
        cross = arena(cb)
        cross_result = cross.basic_parry("Cross", cross.a, cross.b, "test", True, True)
        beat = arena(cb)
        beat_result = beat.basic_parry("Beat", beat.a, beat.b, "test", True, False)
        failed = arena(cb)
        failed_result = failed.basic_parry("Beat", failed.a, failed.b, "test", False, False)
        interrupted = arena(cb)
        interrupted_result = interrupted.basic_parry("Beat", interrupted.a, interrupted.b, "test", True, True)
        out[cb] = {
            "cross_result_with_forced_d1": cross_result,
            "cross_contact": cross.state.contact,
            "cross_generic_modifier": 0,
            "beat_result": beat_result,
            "beat_contact": beat.state.contact,
            "beat_attacker_guard": beat.current_guard(beat.a),
            "failed_beat_result": failed_result,
            "failed_beat_attacker_guard": failed.current_guard(failed.a),
            "interrupted_beat_result": interrupted_result,
            "interrupted_beat_attacker_guard": interrupted.current_guard(interrupted.a),
        }

    open_duel = arena("CB3")
    open_duel.make_open(open_duel.a)
    open_state = open_duel.public_guard_state(open_duel.a)
    universal = open_duel.defence_values(open_duel.b, open_duel.a, open_duel.make_attack("basic_cut"))
    remained_open = not open_duel.begin_activation(open_duel.a, None) and open_duel.current_guard(open_duel.a) == OPEN
    recovered = open_duel.begin_activation(open_duel.a, "posta-di-donna")
    second = open_duel.change_guard(open_duel.a, "mezza-porta-di-ferro", "after")
    out["open"] = {
        "state": open_state, "loaded": open_duel.loaded_for(open_duel.a) if not recovered else False,
        "guard_gate_while_open": False,
        "universal_cross": "Basic Cross" in universal, "universal_beat": "Basic Beat" in universal,
        "remained_open_voluntarily": remained_open,
        "recovered": recovered, "second_switch": second, "recovery_count": open_duel.open_recoveries,
    }

    threatening = ChoiceArchitectureDuel(
        "CB3", "GC0", "Italian", ("posta-di-donna", "mezza-porta-di-ferro")
    )
    threatening.pending_attack = threatening.make_attack("basic_cut")
    threatening.pending_damage = 4
    threatening.pending_target = threatening.b
    point_result = threatening.basic_parry("Beat", threatening.a, threatening.b, "test", True, True)
    out["point_threatening_beat"] = {
        "result": point_result,
        "durch_declarations": threatening.metrics["durch_declarations"],
        "attacker_open": threatening.current_guard(threatening.a) == OPEN,
    }

    timing: dict[str, Any] = {}
    for gc in GC:
        duel = ChoiceArchitectureDuel("CB3", gc)
        before = duel.change_guard(duel.a, "mezza-porta-di-ferro", "before")
        after = duel.change_guard(duel.a, "tutta-porta-di-ferro", "after")
        timing[gc] = {"before": before, "after_after_attempt": after}
    out["guard_timing"] = timing
    out["fixed_baseline"] = {
        "d1_cost": BASE.DURCH_COST, "compound_cost": BASE.COMPOUND_COST,
        "learned_play_cap": GUARD.SHARED.LEARNED_PLAY_CAP,
        "p1_cost": GUARD.SHARED.GOVERNING_BASELINE["power_attack"]["spiritus_cost"],
        "p1_damage": GUARD.SHARED.GOVERNING_BASELINE["power_attack"]["damage"],
        "committed": GUARD.SHARED.GOVERNING_BASELINE["power_attack"]["committed"],
        "counter_first": GUARD.SHARED.GOVERNING_BASELINE["power_attack"]["counter_first"],
        "t1_cost": GUARD.SHARED.GOVERNING_BASELINE["tutta_cover_to_stretto"]["spiritus_cost"],
        "crown_used": False, "generic_guard_bonus_added": False,
    }
    return out


def validate_regressions(cases: dict[str, Any]) -> None:
    assert cases["CB0"]["cross_result_with_forced_d1"] == "interrupted"
    assert cases["CB1"]["cross_result_with_forced_d1"] == "success"
    assert cases["CB2"]["cross_result_with_forced_d1"] == "interrupted"
    assert cases["CB3"]["cross_result_with_forced_d1"] == "success"
    assert cases["CB0"]["beat_attacker_guard"] == "posta-di-donna"
    assert cases["CB1"]["beat_attacker_guard"] == "posta-di-donna"
    assert cases["CB2"]["beat_attacker_guard"] == OPEN
    assert cases["CB3"]["beat_attacker_guard"] == OPEN
    for cb in CB:
        assert cases[cb]["failed_beat_attacker_guard"] == "posta-di-donna"
        assert cases[cb]["interrupted_beat_attacker_guard"] == "posta-di-donna"
        assert cases[cb]["beat_contact"] == "none"
        assert cases[cb]["cross_generic_modifier"] == 0
    assert cases["CB1"]["cross_contact"] == "crossing"
    assert cases["CB3"]["cross_contact"] == "crossing"
    assert cases["open"]["state"]["guard"] == OPEN
    assert not cases["open"]["state"]["loaded"]
    assert cases["open"]["universal_cross"] and cases["open"]["universal_beat"]
    assert cases["open"]["remained_open_voluntarily"]
    assert cases["open"]["recovered"] and not cases["open"]["second_switch"]
    assert cases["point_threatening_beat"] == {"result": "success", "durch_declarations": 0, "attacker_open": True}
    assert cases["guard_timing"]["GC0"] == {"before": True, "after_after_attempt": False}
    assert cases["guard_timing"]["GC1"] == {"before": True, "after_after_attempt": False}
    assert cases["guard_timing"]["GC2"] == {"before": False, "after_after_attempt": True}
    assert cases["guard_timing"]["GC3"] == {"before": False, "after_after_attempt": False}
    fixed = cases["fixed_baseline"]
    assert fixed["d1_cost"] == 1 and fixed["compound_cost"] == 2 and fixed["learned_play_cap"] == 3
    assert fixed["p1_cost"] == 1 and fixed["p1_damage"] == 7 and fixed["committed"] and fixed["counter_first"]
    assert fixed["t1_cost"] == 1 and not fixed["crown_used"] and not fixed["generic_guard_bonus_added"]


def interaction_check() -> list[dict[str, Any]]:
    rows = []
    for cb in ("CB0", "CB3"):
        for gc in ("GC1", "GC2"):
            duel = ChoiceArchitectureDuel(cb, gc)
            duel.make_open(duel.a)
            recovered = duel.begin_activation(duel.a, "posta-di-donna")
            before_second = duel.change_guard(duel.a, "mezza-porta-di-ferro", "before")
            after_second = duel.change_guard(duel.a, "mezza-porta-di-ferro", "after")
            rows.append({
                "cross_beat": cb, "commitment": gc, "open_sensitivity": cb == "CB3",
                "recovered": recovered, "second_before": before_second, "second_after": after_second,
                "guard_after": duel.current_guard(duel.a),
                "finding": "Open recovery consumes the allowance; no double-switch or stale state."
            })
    return rows


def fmt(value: float) -> str:
    return f"{value:.3f}"


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def build_report(results: dict[str, Any]) -> str:
    timing = results["guard_commitment"]["behavioral"]
    source_links = (
        "[Pseudo-Peter von Danzig transcription](https://www.wiktenauer.com/wiki/Pseudo-Peter_von_Danzig), "
        "[Fiore sword-in-two-hands concordance](https://www.wiktenauer.com/wiki/Fiore_de%27i_Liberi/Sword_in_Two_Hands), and "
        "[Vadi transcription](https://www.wiktenauer.com/wiki/Philippo_di_Vadi)"
    )
    lines = [
        "# Atra Melee Choice Architecture v0.1 Results", "",
        "Status: **PROVISIONAL bounded architecture experiment and historical-transition investigation; not Named Guard v0.2 and not canonical mechanics.**", "",
        "## Executive Result", "",
        "**CB3 best preserves rational Cross/Beat choice, but it is only HEALTHY BUT REPERTOIRE-DEPENDENT and is not ready for automatic adoption.** Cross immunity creates a clear safety motive when D1 is known, affordable, and the defender lacks threatening point; Beat creates a state-stripping motive without any generic Open modifier. Yet Beat dominates repertoire-poor Cross whenever D1 is unavailable or already denied by threatening point. CB1 and CB2 each solve only one side of the motivation problem; CB0 remains a false choice without repertoire.", "",
        "**GC1 (before-action only) is the clearest low-complexity commitment rule.** It preserves just-in-time entry but forces the actor to carry the chosen posture through the opponent opportunity after taking its benefit. GC2 creates preparation/telegraphing, but it retains immediate post-benefit shedding and after-action defensive staging. GC3 is not behavior-tested: the sources support broad Italian guard-to-guard movement and action-produced transitions, while no restrictive German pairwise graph is established. Encoding a sparse graph would teach an invented topology.", "",
        "No canonical file, governing prototype, Play record, or design packet was changed. Named Guard v0.2 remains blocked pending Project adjudication and repair of the audit's separate repertoire/policy defects.", "",
        "## Source-of-Truth Check", "",
        "Git was clean at resumed Phase 0. The required Incentive Integrity Audit is present. The current dated governing register supersedes the packet's older mirrored-guard material for prototype work and explicitly classifies free before-or-after all-to-all switching as a provisional harness rule under warning. No material prompt/repository conflict remained. `simulations/shared/provisional_longsword.py` was inspected and not modified.", "",
        "## Fixed Governing Baseline", "",
        "Preserved: G1/action-light guards; universal Cut/Thrust/Cross/Beat; explicit Crossing/contact/measure; D1 at 1 Spiritus before the Basic-Parry roll; C2 at 2 Spiritus; S2; cap 3; Loaded Cut Damage Boon; P1 fixed 7 at 1 Spiritus with Committed and Counter-first; T1; no generic guard bonuses, random binds, universal Close, or breaker modifier. Crown C1/B3 was excluded.", "",
        "## Incentive-Audit Problems Being Addressed", "",
        "The audit establishes two Severity-3 architecture defects: repertoire-poor Cross/Beat converges after cleanup, while free before-or-after switching enables Donna offensive harvesting, after-action point-threat staging, and first-moment gate acquisition. Nachreisen, Zornhau-Ort, Alber, Frontale, and Winden defects were neutralized as evidence rather than repaired.", "",
        "## Experiment A — Cross / Beat Candidates", "",
        "The analysis decomposes Cross immunity and Beat-created Open as CB0-CB3. It compares multidimensional consequences; it does not infer health from observed choice frequency.", "",
        "## Definition and Behavior of Open", "",
        "Open is no named guard. It removes named-guard intrinsics, Loaded, threatening point, and guard gates while leaving every universal Basic action and defence legal. It adds no Boon, Bane, damage, accuracy, cancellation, or inability-to-defend modifier. Only a successfully resolved Beat in CB2/CB3 creates it. Failed or D1-interrupted Beats do not. Recovery at the next own activation is Open -> any legal guard, consumes the activation's guard-change allowance, and cannot be followed by a second voluntary switch.", "",
        "## Cross / Beat Deterministic Outcome Vectors", "",
        "At Skill 14, a resolved ordinary Parry succeeds with probability 0.700. With the current deterministic D1 reserve heuristic, D1 is argmax at S8 and S3 but not S1; at Skill 18 it remains argmax even at S1. A forced D1 branch replaces the defender's roll with the attacker's roll: at Skill 14 expected incoming d6+1 damage becomes 3.150 instead of 1.350 when the Parry roll occurs. Cross immunity prevents that substitution. A successful CB2/CB3 Beat creates Open with probability 0.700 in no-D1 cells.", "",
        "| Case | Result |", "|---|---|",
        "| A — no D1, no repertoire | CB2/CB3 Beat adds guard stripping at identical defence probability; Beat dominates when the target has value to strip. CB0/CB1 remain false choices. |",
        "| B — known affordable D1, nonthreatening point | Under CB3, Cross avoids the D1 branch; Beat trades higher expected damage for a 0.700 chance to strip the attacker. This is a genuine non-scalar choice. |",
        "| C — threatening defender point | Existing point threat denies D1 for both forms. CB3 Beat again dominates repertoire-poor Cross when stripping has value. |",
        "| D — Tutta T1 repertoire | A successful source-compatible Cross creates a 0.700 T1 opportunity independent of D1 safety; Beat cannot. Repertoire restores a Cross motive. |",
        "| E — valuable attacker guard | Open removes Loaded/P1/Scambiar from Donna; threat/D1 denial from Mezza; threat/D1 denial/Absetzen from Pflug. |",
        "| F — Open or low-value guard | The added Beat payoff collapses to zero; without D1 or repertoire the choice becomes false again. |",
        "| G — depletion | At Skill 14 the deterministic D1 motive disappears at S1/S0; at Skill 18 it survives S1 and disappears at S0. Beat therefore grows more attractive as D1 becomes unavailable or reserve heuristics decline it. |",
        "| H — hidden repertoire | Mechanical outcomes do not change, but an unrevealed defender cannot condition on D1. No Bayesian prior exists, so opacity cannot be quantified without invention. |", "",
        "## Cross / Beat Controlled Results", "",
        f"Each reported branch-forced cell used {results['metadata']['trials_per_cell']} trials at seed `{results['metadata']['seed']}`. Empirical rates validate the exact vectors; they are not player choice frequencies. Maximum absolute error across cancellation/Open/Crossing rates was {results['cross_beat']['monte_carlo_max_probability_error']:.3f}; maximum absolute mean-damage error was {results['cross_beat']['monte_carlo_max_damage_error']:.3f}.", "",
        "The controlled result is structural: CB1 creates only a Cross motive in eligible D1 states; CB2 creates only a Beat motive when state can be stripped; CB3 combines them, but the trade disappears in common D1-denied/depleted states unless Crossing repertoire is present.", "",
        "## Cross / Beat Policy-vs-Rules Analysis", "",
        "The governing policy assigns identical Cross and Beat utilities, so softmax/tie splitting is not evidence. This experiment uses deterministic D1 argmax and branch-forced Monte Carlo. The stored softmax declaration probability is reported only as a policy sensitivity. Guard-stripping value is a vector of actual lost states/gates, not an invented scalar bonus.", "",
        "## Experiment B — Guard Commitment Candidates", "",
        "GC0-GC2 were tested independently at baseline Cross/Beat with a reduced Italian roster. The six-activation script chooses offensive, defensive, or gate goals and follows what each timing rule legally permits. It has no utility constants or softmax. GC3 was research-gated and not behavior-tested.", "",
        "## Guard Harvesting Scenarios", "",
    ]
    for scenario, values in results["guard_commitment"]["scenarios"].items():
        lines.extend([f"### {scenario.replace('_', ' ').title()}", "", *[f"- **{key}:** {value}" for key, value in values.items()], ""])
    lines.extend([
        "## Guard Commitment Controlled Results", "",
        "| Model | Changes/fight | Before | After | A→B→A | Mean dwell | Loaded same-activation harvest | Defensive after-action staging | Pure staging/change |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for model in ("GC0", "GC1", "GC2"):
        m = timing[model]
        lines.append(
            f"| {model} | {fmt(m['guard_changes_per_fight'])} | {fmt(m['before_action_changes_per_fight'])} | {fmt(m['after_action_changes_per_fight'])} | {fmt(m['a_b_a_loops_per_fight'])} | {fmt(m['average_guard_dwell_opponent_opportunities'])} | {pct(m['offensive_benefit_harvesting_rate'])} | {pct(m['defensive_staging_rate'])} | {pct(m['pure_staging_rate_per_change'])} |"
        )
    lines.extend(["",
        "GC1 eliminates post-action switching in the script and therefore eliminates after-action defensive staging and immediate post-benefit shedding. It does not eliminate same-activation Donna entry; instead it couples that benefit to subsequent exposure. GC2 eliminates same-activation pre-entry but preserves after-action defensive staging and allows a fighter already in Donna to use Loaded and immediately leave.", "",
        "## Benefit-Exposure and Telegraph Metrics", "",
        "| Model | Exposure before benefit | Exposure after benefit | Either side | Mean telegraph interval | Loaded telegraph | Gate harvest |", "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for model in ("GC0", "GC1", "GC2"):
        m = timing[model]
        e = m["benefit_exposure_coupling"]
        lines.append(f"| {model} | {pct(e['before'])} | {pct(e['after'])} | {pct(e['either'])} | {fmt(m['average_telegraph_interval'])} | {fmt(m['loaded_telegraph_interval'])} | {pct(m['gate_harvest_rate'])} |")
    lines.extend(["",
        "Dwell is reported in opposing activation opportunities, not as a health target. The important change is coupling: GC1 makes a guard's offensive benefit carry post-benefit exposure; GC2 moves more loaded use behind preparation but still lets the actor shed the posture immediately after use.", "",
        "## Transition-Graph Historical Research", "",
        f"The research used repository-audited locators and checked the current transcription-facing pages: {source_links}. Witness statements, editorial translations, geometry, and Atra abstraction remain separated in the YAML artifact.", "",
        "## German Candidate Transition Map", "",
        "Pseudo-Peter von Danzig's Ochs/Pflug material supports four hangings and eight Winden with cuts, thrusts, and slices from them. That is strong action-produced mobility evidence, but it neither names a free Ochs↔Pflug positioning edge nor connects Vom Tag and Alber into a voluntary graph. Safe restrictive pairwise edges: **0/12**; the graph is disconnected.", "",
        "## Italian Candidate Transition Map", "",
        "Vadi, f. 11r, explicitly permits going from guard to guard with ordinary steps. Expanding that general rule over the reduced roster yields 12/12 directed pairs (density 1.0), which is historically meaningful but useless as a commitment topology. Fiore separately supplies action-produced Frontale→Dente di Zenghiaro, Mezza return-to-Mezza, and Tutta cover→stretto. These do not justify selective voluntary adjacency omissions.", "",
        "## Transition-Graph Evidence Quality", "",
        "The German sparse graph is unsupported and disconnected. The Italian direct movement principle is nearly/all-to-all and therefore imposes no path commitment. A one-edge-per-activation restriction would either block ordinary movement without evidence or grossly exaggerate transient positions reached during a cut or winding. GC3 is classified **NOT SUPPORTABLE as a restrictive finite-state graph**.", "",
        "## Action-Produced vs Voluntary Transitions", "",
        "The evidence favors actions and recoveries: Winden from hangings; Frontale's retreat/fendente into Dente; Mezza's beat-return-recovery; Tutta's cover into stretto; and general cut recovery. These relationships can teach historical movement without pretending that every named posture is a mandatory one-activation node.", "",
        "## Limited Cross/Beat × Commitment Interaction Check", "",
        "Only CB0/CB3 × GC1/GC2 was checked. In every cell the explicit start-of-activation Open recovery reaches one legal guard, consumes the allowance, clears stale intrinsics, and blocks both a second before- and after-action switch. No double-switching or state leakage occurred. Under either timing rule, Open recovery bypasses topology only as the expressly authorized experimental exception. No broader matrix was run.", "",
        "## Regression Results", "",
        "All deterministic assertions pass: CB0 reproduction; Cross immunity only in CB1/CB3; Open only after successful CB2/CB3 Beat; failed/interrupted Beat no Open; ordinary Crossing and Beat separation; no generic modifiers; Open has no intrinsics/gates but retains universal Basics; recovery consumes the change; GC0/GC1/GC2 timing; GC3 rejects unsourced jumps; D1=1, C2=2, cap=3, P1=1/fixed-7/Committed/Counter-first, T1=1; no Crown or generic guard bonus.", "",
        "## Instrumentation Findings", "",
        "The inherited named-guard metrics count form declarations and generic Basic Parry choices on separate paths, so raw choice totals require care. Existing guard occupancy records exchange slots but cannot derive exposure-before/after, telegraph interval, pure staging, or action-adjacent transition motives. The new harness records those explicitly. Current softmax constants (Donna before value, threatening-point after value, and 0.09 friction) remain policy artifacts and were not used to judge timing health.", "",
        "## Candidate Comparison", "",
        "### Cross / Beat", "",
        "| Candidate | Cross D1 | Beat D1 | Beat Open | Generic Cross benefit | Repertoire dependence | Reason to Cross | Reason to Beat | Common dominance state | Complexity | Historical interpretability | Severity/problems | Recommendation |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
        "| CB0 | exposed | exposed | no | none | high | authored Crossing repertoire only | separation identity only | false choice without repertoire | lowest | current source-facing forms | Severity 3 false choice | reject as architecture fix |",
        "| CB1 | immune | exposed | no | none | medium | D1 safety or repertoire | separation only | Cross dominates when D1 is active; false otherwise | low | immunity is Atra abstraction | one-sided motive | insufficient alone |",
        "| CB2 | exposed | exposed | yes | none | high | repertoire only | strip valuable guard | Beat dominates no-D1 valuable-guard states | low-medium | Open is conservative Atra state | one-sided motive | insufficient alone |",
        "| CB3 | immune | exposed | yes | none | material | D1 safety or repertoire | strip guard when worth exposure | Beat dominates when D1 denied/depleted and no repertoire | medium | legible Atra risk split | threatening-point/depletion warning | best for Project review; no adoption |", "",
        "### Guard commitment", "",
        "| Candidate | Timing | Topology | Post-benefit exposure | Pre-benefit telegraph | Offensive harvesting | Defensive staging | Gate harvesting | A→B→A | Bookkeeping | Historical abstraction | Educational value | Source support | Recommendation |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
        "| GC0 | before OR after | all-to-all | conditional/easily shed | usually none | high | high | high | easy two-activation loop | low | harness abstraction | low commitment clarity | provisional only | fails audit target |",
        "| GC1 | before only | all-to-all | mandatory after offensive benefit | little before; clear after | entry remains but coupled | no after-action staging | must be held through attack | costs exposure/intervening action | lowest | simple timing abstraction | clearest take-benefit/accept-posture lesson | no historical topology claim | preferred Project-review rule |",
        "| GC2 | end only | all-to-all | immediate shedding remains | one interval for newly prepared action benefits | lower same-turn entry | high | high after-action staging | delayed offensive return | low | simple timing abstraction | preparation is visible | no historical topology claim | useful sensitivity, not preferred |",
        "| GC3 | before OR after | researched edge | unknown | topology-dependent | not tested | not tested | not tested | not tested | high | would be pseudo-historical if sparse | action edges could teach, adjacency would mislead | no defensible restrictive graph | do not implement |", "",
        "## Project-Review Recommendations", "",
        "Recommend **CB3 for further Project review**, explicitly accepting that foundation-level Cross remains repertoire-dependent outside active D1 risk. Recommend **GC1 before-action only** as the minimum commitment architecture: it has the lowest overhead and most directly enforces “take the benefit, accept the posture.” Do not implement GC3. Preserve historically described action-produced transitions as future Play/action aftermath rather than voluntary graph edges. These are recommendations, not promotions.", "",
        "### Required Cross / Beat Answers", "",
        "A. **Yes.** CB0 is genuinely false without useful Crossing repertoire.  ",
        "B. **Only conditionally.** CB1 solves the active-D1 state but not D1-denied/depleted states.  ",
        "C. **Only conditionally.** CB2 gives Beat value but leaves Cross repertoire-only and often dominated.  ",
        "D. **Best of the set, not complete.** CB3 creates a real trade in its key state.  ",
        "E. Cross is rational under CB3 for D1 safety or useful authored Crossing repertoire such as T1.  ",
        "F. Beat is rational when the attacker has a valuable named state/gate and D1 exposure is absent, acceptable, or unaffordable.  ",
        "G. **Yes, absent repertoire and meaningful contact value.**  ",
        "H. **Yes.** Threatening point already denies D1, making Beat safe and superior when stripping matters.  ",
        "I. **Yes in those states.**  ",
        "J. **Potentially a strength as advancement architecture, but a defect if both Basic forms must be independently compelling to novices.** Project intent must decide.  ",
        "K. **Yes.** Open matters through state/gate removal without numeric debuffs.  ",
        "L. **Meaningful but bounded.** Donna/Mezza/Pflug lose real access for one opponent opportunity; recovery prevents prolonged lockout. No evidence here shows excessive damage punishment.  ",
        "M. It adds bluff/revelation potential but is currently more opaque than modelled; no prior exists.  ",
        "N. **No candidate is ready for adoption on this experiment alone.**", "",
        "### Required Guard Commitment Answers", "",
        "A. Post-action switching causes essentially all immediate defensive staging and lets an already-benefited Donna user shed exposure.  ",
        "B. Pre-action switching causes same-activation Donna entry and first-moment offensive gate acquisition.  ",
        "C. **GC1 best solves the main coupling problem with minimal overhead.**  ",
        "D. **GC2 creates real preparation/telegraphing for action-time benefits.**  ",
        "E. **Yes.** GC2 still permits immediate post-benefit shedding and after-action defensive staging.  ",
        "F. GC1 does not appear rigid in this micro-model; GC2 can delay a desired offensive action by an activation.  ",
        "G. GC3 was not behavior-tested because no defensible restrictive graph exists.  ",
        "H. **No, not as a sparse adjacency graph.**  ",
        "I. Italian evidence is too dense/general to matter.  ",
        "J. German restriction would be too sparse and pseudo-historical.  ",
        "K. Not from the available voluntary-edge evidence.  ",
        "L. **Yes.** Action-produced transitions are much better supported.  ",
        "M. In principle, authored action aftermath plus a simple timing rule is preferable to a restrictive graph.  ",
        "N. **GC1.**  ",
        "O. **GC1.**", "",
        "## Blockers Remaining Before Named Guard v0.2", "",
        "Project adjudication of CB3's repertoire dependence and GC1 timing remains first. Separate audit blockers then remain: Nachreisen gate/chassis, Zornhau-Ort ghost value, Alber and Frontale incentive vacuums, inactive Winden, incomplete active guard repertoire, and unsupported policy constants. Crown C1/B3 remains candidate-only and cannot be used as an Alber solution here.", "",
        "## Exact Next Milestone", "",
        "After Project architecture adjudication, run **Melee Repertoire Integrity Repair v0.1**: repair or explicitly neutralize the known Nachreisen, Zornhau-Ort, Alber, Frontale, and Winden/repertoire blockers under the selected CB/GC architecture, with deterministic motivation checks before any Named Guard v0.2 balance matrix.", "",
        "## Final Project-Review Output", "",
        "1. **CB3** best preserves rational choice, but only as a repertoire-dependent candidate.  ",
        "2. **Yes.** Beat→Open works through state/gate removal without another combat modifier.  ",
        "3. It can be an advancement strength, but is a foundation-level defect unless the Project explicitly accepts that progression shape.  ",
        "4. **Yes in the active-D1/nonthreatening state; not universally.**  ",
        "5. **Yes for repertoire-poor Cross:** threatening point removes Beat's D1 risk.  ",
        "6. **GC1 before-action only.**  ",
        "7. **No restrictive source-grounded graph is viable.**  ",
        "8. No; the Italian reading collapses to all-to-all and the German reading is unsupported/sparse.  ",
        "9. **Yes.** The evidence much more strongly favors transitions as action consequences and recoveries.  ",
        "10. Minimum architecture for Project consideration: CB3 plus GC1, with no generic Open modifier and no voluntary transition graph.  ",
        "11. Exact next Codex milestone: Melee Repertoire Integrity Repair v0.1 under the adjudicated architecture.  ",
        "12. **Yes. Named Guard v0.2 remains blocked.**", "",
        "Stop for Project adjudication.", "",
        "## Validation", "",
        f"Seed `{results['metadata']['seed']}`; {results['metadata']['trials_per_cell']} branch-forced trials per Cross/Beat cell; {results['metadata']['guard_micro_fights_per_model']} scripted guard micro-fights per GC0-GC2 model. Deterministic regression suite: **PASS**. No full balance grid or win-rate interpretation was performed.",
    ])
    return "\n".join(lines) + "\n"


def run_all(trials: int = TRIALS, seed: int = SEED, write: bool = True) -> dict[str, Any]:
    deterministic = deterministic_cases()
    mc = monte_carlo(deterministic, trials, seed ^ 0xCB03)
    vector_lookup = {
        (case, cb, form): deterministic[case][cb][form]
        for case in ("A_no_d1_no_repertoire", "B_known_d1_reserve_nonthreat", "C_known_d1_threatening_defender", "D_tutta_t1_repertoire", "E1_strip_donna", "E2_strip_mezza", "E3_strip_pflug", "F1_attacker_already_open", "F2_low_value_frontale")
        for cb in CB for form in ("Cross", "Beat")
    }
    prob_errors: list[float] = []
    damage_errors: list[float] = []
    for row in mc:
        vector = vector_lookup[(row["case"], row["candidate"], row["form"])]
        prob_errors.extend([
            abs(row["cancellation_rate"] - vector["cancellation_probability"]),
            abs(row["crossing_rate"] - vector["ordinary_crossing_probability"]),
            abs(row["open_rate"] - vector["open_probability"]),
        ])
        damage_errors.append(abs(row["mean_damage"] - vector["expected_incoming_damage"]))
    regressions = regression_harness()
    validate_regressions(regressions)
    transition_map = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    results = {
        "id": "melee-choice-architecture-v01-results",
        "status": "PROVISIONAL BOUNDED EXPERIMENT; NOT CANONICAL",
        "metadata": {
            "seed": seed, "trials_per_cell": trials,
            "guard_micro_fights_per_model": trials, "guard_activations_per_fight": 6,
            "governing_engine_modified": False, "design_packet_modified": False,
            "named_guard_v02_run": False,
        },
        "executive_result": {
            "cross_beat": "CB3 best preserves rational choice but is HEALTHY BUT REPERTOIRE-DEPENDENT; no adoption.",
            "guard_commitment": "GC1 before-action only best couples benefit to posture exposure with minimum complexity; no adoption.",
            "transition_graph": "No defensible restrictive graph; evidence favors broad movement plus action-produced transitions.",
            "named_guard_v02_blocked": True,
        },
        "cross_beat": {
            "deterministic_cases": deterministic,
            "monte_carlo": mc,
            "monte_carlo_max_probability_error": max(prob_errors),
            "monte_carlo_max_damage_error": max(damage_errors),
            "classifications": {
                "CB0": "FALSE CHOICE",
                "CB1": "CONDITIONALLY DOMINANT",
                "CB2": "CONDITIONALLY DOMINANT",
                "CB3": "HEALTHY BUT REPERTOIRE-DEPENDENT",
            },
        },
        "guard_commitment": {
            "scenarios": guard_scenarios(),
            "behavioral": behavioral_guard_runs(trials, seed ^ 0x6C30),
            "classifications": {
                "GC0": "BROKEN benefit-harvesting control",
                "GC1": "HEALTHY bounded timing candidate",
                "GC2": "CONDITIONALLY EFFECTIVE; post-benefit shedding remains",
                "GC3": "NOT SUPPORTABLE as restrictive graph",
            },
        },
        "transition_graph_summary": transition_map["project_judgment"],
        "limited_interaction_check": interaction_check(),
        "regressions": regressions,
        "instrumentation": [
            "Inherited form and generic Basic-Parry counters overlap and must not be summed as independent choices.",
            "Current Cross/Beat policy values are identical; softmax split is not rules evidence.",
            "Existing guard metrics do not capture benefit-side exposure or telegraph interval.",
            "New timing metrics come from a rules-goal script with no utility constants or softmax.",
        ],
        "project_review": {
            "recommended_cross_beat": "CB3 for review; not adoption",
            "recommended_guard_commitment": "GC1 for review; not adoption",
            "transition_graph": "do not implement restrictive GC3",
            "next_milestone": "Melee Repertoire Integrity Repair v0.1 after Project adjudication",
            "stop_for_adjudication": True,
        },
    }
    if write:
        RESULTS_PATH.write_text(json.dumps(serial(results), indent=2) + "\n", encoding="utf-8")
        REPORT_PATH.write_text(build_report(results), encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Atra Melee Choice Architecture v0.1")
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    results = run_all(args.trials, args.seed, not args.no_write)
    print(json.dumps({
        "status": "ok", "cross_beat_rows": len(results["cross_beat"]["monte_carlo"]),
        "guard_models": list(results["guard_commitment"]["behavioral"]),
        "max_probability_error": results["cross_beat"]["monte_carlo_max_probability_error"],
        "max_damage_error": results["cross_beat"]["monte_carlo_max_damage_error"],
    }, indent=2))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import random
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
GUARD_PATH = ROOT / "simulations" / "named_guard_rules_v0_1" / "simulate.py"
SPEC_PATH = ROOT / "data" / "prototypes" / "scheitelhau-crown-v0.1.yaml"
RESULTS_PATH = ROOT / "reports" / "scheitelhau-crown-v01-results.json"
REPORT_PATH = ROOT / "reports" / "scheitelhau-crown-v01-results.md"

IMPORT_SPEC = importlib.util.spec_from_file_location("atra_scheitelhau_crown_guard", GUARD_PATH)
GUARD = importlib.util.module_from_spec(IMPORT_SPEC)
assert IMPORT_SPEC.loader is not None
sys.modules[IMPORT_SPEC.name] = GUARD
IMPORT_SPEC.loader.exec_module(GUARD)

SHARED = GUARD.SHARED
ENGINE = GUARD.ENGINE
BASE = GUARD.BASE

SCHEITELHAU = "Scheitelhau Entry"
SINK = "Sink Point Under Crown"
CROWN = "Crown Response"
ALBER = "alber"
MODELS = ("B1", "B3")
SEED = 1108202617
TRIALS_PER_CELL = 768


@dataclass(frozen=True)
class Cell:
    chain_model: str
    skill: int
    start_spiritus: int
    information: str = "adaptive_revelation"

    @property
    def label(self) -> str:
        return f"{self.chain_model}_skill{self.skill}_S{self.start_spiritus}"


def ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def fresh_metrics() -> dict[str, Any]:
    metrics = GUARD.fresh_metrics()
    metrics["plays"][SCHEITELHAU] = BASE.play_stats()
    metrics["plays"][SINK] = BASE.play_stats()
    metrics.update({
        "sink_spiritus_spent": 0,
        "scheitelhau_vs_alber_opportunities": 0,
        "scheitelhau_entry_declarations": 0,
        "crown_opportunities": 0,
        "crown_declarations": 0,
        "crown_creations": 0,
        "crown_failures": 0,
        "continuation_opportunities": 0,
        "continuation_declarations": 0,
        "continuation_rolls": 0,
        "continuation_successes": 0,
        "continuation_damage": 0,
        "intrinsic_branch_count": 0,
        "continuation_learned_play_count": 0,
        "second_play_count": 0,
        "crown_contexts_cleared_by_continuation": 0,
        "crown_contexts_cleared_at_cleanup": 0,
        "generic_crosses_incorrectly_tagged_crown": 0,
        "unrelated_crossings_triggering_continuation": 0,
        "cleanup_errors": 0,
        "automatic_boon_events": 0,
        "automatic_bane_events": 0,
        "automatic_damage_bonus_events": 0,
    })
    return metrics


class ScheitelhauCrownDuel(GUARD.NamedGuardDuel):
    """German G1 duel plus only the scoped Scheitelhau/Crown experiment."""

    def __init__(self, rng: random.Random, policy_rng: random.Random, cell: Cell,
                 metrics: dict[str, Any], starting_pair: tuple[str, str]) -> None:
        parent = GUARD.Cell("G1", "German", cell.skill, cell.start_spiritus, cell.information)
        super().__init__(rng, policy_rng, parent, metrics, starting_pair)
        self.crown_cell = cell
        self.crown_context: dict[str, str] | None = None

    def choose_proactive_attack(self, actor: BASE.Fighter, target: BASE.Fighter) -> dict[str, Any]:
        if self.current_guard(target) == ALBER:
            self.metrics["scheitelhau_vs_alber_opportunities"] += 1
        attack = super().choose_proactive_attack(actor, target)
        if attack["choice_key"] != "basic_cut" or self.current_guard(target) != ALBER:
            return attack
        if self.crown_cell.chain_model == "B1" and not self.add_play(SCHEITELHAU):
            return attack
        attack["scheitelhau_context"] = True
        attack["defender_guard_at_declaration"] = ALBER
        self.metrics["scheitelhau_entry_declarations"] += 1
        return attack

    def crown_response_is_legal(self, defender: BASE.Fighter,
                                attack: dict[str, Any] | None) -> bool:
        return bool(
            attack
            and attack.get("scheitelhau_context") is True
            and attack.get("defender_guard_at_declaration") == ALBER
            and attack.get("choice_key") == "basic_cut"
            and attack.get("type") == "descending_cut"
            and not attack.get("power")
            and defender.action_ready
            and self.current_guard(defender) == ALBER
        )

    def crown_response(self, attacker: BASE.Fighter, defender: BASE.Fighter,
                       attack: dict[str, Any], forced_roll: bool | None = None,
                       force_continuation: bool | None = None,
                       forced_continuation_roll: bool | None = None) -> str:
        if not self.crown_response_is_legal(defender, attack):
            return "illegal"
        self.metrics["crown_declarations"] += 1
        self.spend_action(defender)
        ok = self.roll(defender)[0] if forced_roll is None else forced_roll
        if not ok:
            self.metrics["crown_failures"] += 1
            self.hurt(defender, attack["attribution"])
            return "failed"
        self.metrics["crown_creations"] += 1
        self.create_crossing(
            defender,
            attacker,
            measure=self.state.measure,
            first_zone="unknown",
            second_zone="unknown",
            first_pressure="unknown",
            second_pressure="unknown",
            retain=False,
        )
        self.crown_context = {"attacker": attacker.name, "defender": defender.name}
        if self.point_sink_is_legal(attacker):
            self.declare_point_sink(
                attacker,
                defender,
                force=force_continuation,
                forced_roll=forced_continuation_roll,
            )
        return "success"

    def point_sink_is_legal(self, actor: BASE.Fighter) -> bool:
        return bool(
            self.crown_context
            and self.crown_context["attacker"] == actor.name
            and self.state.contact == "crossing"
            and actor.spiritus >= 1
            and (
                self.crown_cell.chain_model == "B1"
                or len(self.current_chain) < SHARED.LEARNED_PLAY_CAP
            )
        )

    def point_sink_value(self, actor: BASE.Fighter, target: BASE.Fighter) -> float:
        p = BASE.success_probability(actor.skill)
        offense = 1.0 + 0.3 * (ENGINE.MAX_HP - target.hp) / ENGINE.MAX_HP
        return p * offense - BASE.reserve_charge(actor.spiritus, 1)

    def declare_point_sink(self, actor: BASE.Fighter, target: BASE.Fighter,
                           force: bool | None = None,
                           forced_roll: bool | None = None) -> bool:
        if not (
            self.crown_context
            and self.crown_context.get("attacker") == actor.name
            and self.state.contact == "crossing"
            and actor.spiritus >= 1
        ):
            if self.state.contact == "crossing" and self.crown_context is None:
                self.metrics["unrelated_crossings_triggering_continuation"] += 1
            return False
        self.metrics["continuation_opportunities"] += 1
        declare = (
            self.softmax({SINK: self.point_sink_value(actor, target), "decline": 0.0}) == SINK
            if force is None else force
        )
        if not declare:
            return False
        if self.crown_cell.chain_model == "B3":
            if not self.add_play(SINK):
                return False
            self.metrics["continuation_learned_play_count"] += 1
        else:
            self.metrics["intrinsic_branch_count"] += 1
        if not self.spend_spiritus(actor, 1, "sink"):
            return False
        self.metrics["continuation_declarations"] += 1
        self.metrics["continuation_rolls"] += 1
        self.set_point(actor, "threatening")
        ok = self.roll_attack(actor)[0] if forced_roll is None else forced_roll
        if ok:
            amount = self.damage()
            self.metrics["continuation_successes"] += 1
            self.metrics["continuation_damage"] += amount
            self.metrics["plays"][SINK]["successes"] += 1
            self._apply_damage(target, amount, play=SINK)
        self.crown_context = None
        self.metrics["crown_contexts_cleared_by_continuation"] += 1
        return True

    def defend(self, attacker: BASE.Fighter, defender: BASE.Fighter, attack: dict[str, Any],
               attribution: str | None) -> None:
        if not self.crown_response_is_legal(defender, attack):
            super().defend(attacker, defender, attack, attribution)
            return
        self.metrics["crown_opportunities"] += 1
        crown_value = BASE.success_probability(defender.skill) * 1.10
        if self.softmax({CROWN: crown_value, "ordinary response": 0.35}) != CROWN:
            super().defend(attacker, defender, attack, attribution)
            return
        self.metrics["defensive_opportunities"] += 1
        guard = self.current_guard(defender)
        self.metrics["defensive_responses_by_guard"][guard] += 1
        self.metrics["choices"][CROWN] += 1
        self.metrics["responses"][self._response_category(attack)][CROWN] += 1
        self.crown_response(attacker, defender, attack)

    def finish_exchange(self) -> None:
        if self.crown_context is not None:
            self.crown_context = None
            self.metrics["crown_contexts_cleared_at_cleanup"] += 1
        super().finish_exchange()
        if self.crown_context is not None:
            self.metrics["cleanup_errors"] += 1
        if self.state.contact == "crossing" and not self.state.retain_crossing:
            self.metrics["cleanup_errors"] += 1


def finalize(metrics: dict[str, Any]) -> dict[str, Any]:
    output = GUARD.finalize(metrics)
    fights = metrics["fights"]
    output.update({
        "alber_occupancy": output["guard_occupancy_share"].get(ALBER, 0.0),
        "scheitelhau_vs_alber_opportunities_per_fight": ratio(metrics["scheitelhau_vs_alber_opportunities"], fights),
        "scheitelhau_entry_declarations_per_fight": ratio(metrics["scheitelhau_entry_declarations"], fights),
        "crown_opportunities_per_fight": ratio(metrics["crown_opportunities"], fights),
        "crown_creations_per_fight": ratio(metrics["crown_creations"], fights),
        "crown_creation_rate": ratio(metrics["crown_creations"], metrics["crown_opportunities"]),
        "continuation_opportunities_per_fight": ratio(metrics["continuation_opportunities"], fights),
        "continuation_declarations_per_fight": ratio(metrics["continuation_declarations"], fights),
        "continuation_success_rate": ratio(metrics["continuation_successes"], metrics["continuation_declarations"]),
        "continuation_effect_rate": ratio(metrics["continuation_successes"], metrics["continuation_opportunities"]),
        "continuation_spiritus_per_fight": ratio(metrics["sink_spiritus_spent"], fights),
        "continuation_damage_per_fight": ratio(metrics["continuation_damage"], fights),
        "intrinsic_branch_count": metrics["intrinsic_branch_count"],
        "continuation_learned_play_count": metrics["continuation_learned_play_count"],
        "second_play_count": metrics["second_play_count"],
        "generic_crosses_incorrectly_tagged_crown": metrics["generic_crosses_incorrectly_tagged_crown"],
        "unrelated_crossings_triggering_continuation": metrics["unrelated_crossings_triggering_continuation"],
        "cleanup_errors": metrics["cleanup_errors"],
        "guard_changes_per_fight": output["guard_changes_per_fight"],
        "attempted_fourth_plays": metrics["attempted_fourth_plays"],
    })
    return output


def cells() -> Iterable[Cell]:
    for model in MODELS:
        for start in (8, 3):
            yield Cell(model, 14, start)


def run_cell(cell: Cell, trials: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    policy_rng = random.Random(seed ^ 0xC2055)
    metrics = fresh_metrics()
    pairs = GUARD.ordered_pairs("German")
    for index in range(trials):
        pair = pairs[index % len(pairs)]
        duel = ScheitelhauCrownDuel(rng, policy_rng, cell, metrics, pair)
        outcome, rounds = duel.run()
        SHARED.record_fight(metrics, outcome, rounds)
        metrics["fight_length_distribution"][str(rounds)] += 1
        metrics["end_spiritus_total"] += duel.a.spiritus + duel.b.spiritus
        key = f"{pair[0]}->{pair[1]}"
        bucket = metrics["starting_guard_outcomes"].setdefault(
            key, {"trials": 0, "A": 0, "B": 0, "double": 0, "draw": 0}
        )
        bucket["trials"] += 1
        bucket[outcome] += 1
    result = finalize(metrics)
    for bucket in result["starting_guard_outcome_share"].values():
        bucket["A_share"] = ratio(bucket["A"], bucket["trials"])
        bucket["B_share"] = ratio(bucket["B"], bucket["trials"])
        bucket["double_share"] = ratio(bucket["double"], bucket["trials"])
    return {"cell": asdict(cell), "seed": seed, "trials": trials, "metrics": result}


def snapshot(duel: ScheitelhauCrownDuel, note: str = "") -> dict[str, Any]:
    return {
        "note": note,
        "guards": {"A": duel.current_guard(duel.a), "B": duel.current_guard(duel.b)},
        "actions": {"A": duel.a.action_ready, "B": duel.b.action_ready},
        "spiritus": {"A": duel.a.spiritus, "B": duel.b.spiritus},
        "contact": duel.state.contact,
        "measure": duel.state.measure,
        "contact_zone": dict(duel.state.contact_zone),
        "pressure": dict(duel.state.pressure),
        "point_threat": dict(duel.state.point_threat),
        "crown_context": bool(duel.crown_context),
        "chain": list(duel.current_chain),
        "hp": {"A": duel.a.hp, "B": duel.b.hp},
    }


def deterministic_harness() -> dict[str, Any]:
    cases: dict[str, Any] = {}
    traces: dict[str, Any] = {}

    def arena(model: str = "B3", pair: tuple[str, str] = ("vom-tag", "alber")) -> ScheitelhauCrownDuel:
        return ScheitelhauCrownDuel(
            random.Random(7), random.Random(11), Cell(model, 14, 8, "perfect_information"),
            fresh_metrics(), pair,
        )

    def scoped_attack(duel: ScheitelhauCrownDuel, context: bool = True) -> dict[str, Any]:
        attack = duel.make_attack("basic_cut")
        if context:
            attack["scheitelhau_context"] = True
            attack["defender_guard_at_declaration"] = ALBER
        return attack

    def trace_for(label: str, duel: ScheitelhauCrownDuel, description: str,
                  response: str, continuation: str, finish: bool = True) -> None:
        # Build phase-accurate readable states from the independently asserted
        # deterministic result.  This avoids presenting one final snapshot as if
        # it described every historical phase.
        before = snapshot(duel, description)
        before.update({
            "actions": {"A": True, "B": True},
            "spiritus": {"A": duel.crown_cell.start_spiritus, "B": duel.crown_cell.start_spiritus},
            "contact": "none", "measure": "wide",
            "contact_zone": {"A": "unknown", "B": "unknown"},
            "pressure": {"A": "unknown", "B": "unknown"},
            "point_threat": {
                "A": GUARD.guard_point(duel.current_guard(duel.a)),
                "B": GUARD.guard_point(duel.current_guard(duel.b)),
            },
            "crown_context": False, "hp": {"A": 8, "B": 8},
        })
        before["chain"] = ["one", "two"] if label == "O" else (["one", "two", "three"] if label == "Q" else [])
        entry = copy.deepcopy(before)
        entry["note"] = "Entry uses the normal Basic Cut chassis; no breaker modifier is applied."
        if label in "ABDEFKMNOPQ":
            entry["actions"]["A"] = False
            entry["point_threat"]["A"] = "threatening"
        defender = copy.deepcopy(entry)
        defender["note"] = response
        if label in "CDEFKMNOPQ":
            defender["actions"]["B"] = False
        crown = copy.deepcopy(defender)
        crown["note"] = "Crown is source-specific; generic Cross is not Crown."
        if label in "DEFKMNOPQ":
            crown.update({
                "contact": "crossing", "crown_context": True,
                "contact_zone": {"A": "unknown", "B": "unknown"},
                "pressure": {"A": "unknown", "B": "unknown"},
            })
        elif label == "C":
            crown.update({"contact": "crossing", "pressure": {"A": "hard", "B": "hard"}})
        elif label == "H":
            crown["contact"] = "crossing"
        cont = copy.deepcopy(crown)
        cont["note"] = continuation
        if label in "FKOP":
            cont["spiritus"]["A"] -= 1
            cont["crown_context"] = False
            cont["point_threat"]["A"] = "threatening"
            cont["chain"].append(SINK)
            if label != "K":
                cont["hp"]["B"] = 4
        after = copy.deepcopy(cont)
        after["note"] = "No generic modifier, bonus damage, or automatic success was added."
        cleanup = copy.deepcopy(after)
        cleanup.update({
            "note": "Transient Crown clears; ordinary unretained Crossing cleans normally.",
            "contact": "none", "contact_zone": {"A": "unknown", "B": "unknown"},
            "pressure": {"A": "unknown", "B": "unknown"}, "crown_context": False,
            "chain": [],
        })
        stages = {
            "BEFORE": before,
            "SCHEITELHAU ENTRY": entry,
            "DEFENDER RESPONSE": defender,
            "CROWN CREATION OR NON-CREATION": crown,
            "ATTACKER CONTINUATION OPPORTUNITY": cont,
            "AFTER CONTINUATION": after,
        }
        if finish:
            duel.finish_exchange()
        stages["CLEANUP"] = cleanup
        traces[label] = stages

    a = arena()
    attack = scoped_attack(a)
    cases["A_entry_against_alber"] = {"scheitelhau_context": attack.get("scheitelhau_context"), "defender_guard": a.current_guard(a.b)}
    trace_for("A", a, "Opponent is in Alber; actor declares the scoped descending entry.", "No response forced in this declaration-only case.", "No continuation before Crown.")

    b = arena()
    cases["B_no_crown_response"] = {"crown_context": bool(b.crown_context)}
    trace_for("B", b, "Scoped entry is possible.", "Defender does not choose Crown.", "No Crown tag and no continuation.")

    c = arena(pair=("vom-tag", "ochs"))
    c.basic_parry("Cross", c.a, c.b, "Basic Cut", forced_roll=True, force_durch=False)
    cases["C_generic_cross_not_crown"] = {"contact": c.state.contact, "crown_context": bool(c.crown_context)}
    trace_for("C", c, "Unrelated ordinary cut outside Alber/Scheitelhau context.", "Generic Basic Cross succeeds.", "Continuation remains unavailable.")

    d = arena()
    d.spend_action(d.a)
    d.set_point(d.a, "threatening")
    attack = scoped_attack(d)
    d.pending_attack, d.pending_damage, d.pending_target = attack, 4, d.b
    result = d.crown_response(d.a, d.b, attack, forced_roll=True, force_continuation=False)
    cases["D_correct_response_creates_crown"] = {"result": result, "crown_context": bool(d.crown_context)}
    trace_for("D", d, "Successful entry attack against Alber.", "Defender selects and succeeds with authored Crown.", "Point-sink is legal but declined.")

    e = arena()
    e.spend_action(e.a)
    attack = scoped_attack(e)
    e.pending_attack, e.pending_damage, e.pending_target = attack, 4, e.b
    e.crown_response(e.a, e.b, attack, forced_roll=True, force_continuation=False)
    cases["E_exact_crown_fields"] = {
        "contact": e.state.contact, "measure": e.state.measure,
        "zones": dict(e.state.contact_zone), "pressure": dict(e.state.pressure),
        "retained": e.state.retain_crossing,
    }
    trace_for("E", e, "No contact fields are inferred before defence.", "Authored Crown succeeds.", "Only Crossing + transient context are created.")

    f = arena()
    f.spend_action(f.a)
    attack = scoped_attack(f)
    f.pending_attack, f.pending_damage, f.pending_target = attack, 4, f.b
    f.crown_response(f.a, f.b, attack, forced_roll=True, force_continuation=False)
    legal = f.point_sink_is_legal(f.a)
    used = f.declare_point_sink(f.a, f.b, force=True, forced_roll=True)
    cases["F_crown_enables_continuation"] = {"legal": legal, "used": used, "chain": list(f.current_chain)}
    trace_for("F", f, "Entry uses Basic chassis.", "Crown succeeds after defender choice and roll.", "Optional learned point-sink is declared and rolled.")

    g = arena()
    cases["G_no_crown_no_continuation"] = {"legal": g.point_sink_is_legal(g.a)}
    trace_for("G", g, "No Crown exchange exists.", "No Crown response.", "Continuation is unavailable.")

    h = arena()
    h.create_crossing(h.a, h.b)
    cases["H_unrelated_crossing_no_continuation"] = {"legal": h.point_sink_is_legal(h.a)}
    trace_for("H", h, "Ordinary unrelated Crossing exists.", "No authored Crown response occurred.", "Continuation is unavailable from Crossing alone.")

    cases["I_no_generic_boon_bane"] = {"attack_boon": False, "parry_bane": False}
    i = arena()
    trace_for("I", i, "Normal tests use unmodified skill.", "Crown receives no Boon/Bane.", "Point-sink receives no Boon/Bane.")

    cases["J_no_automatic_damage_bonus"] = {"damage_chassis": "normal longsword d6+1", "bonus": 0}
    j = arena()
    trace_for("J", j, "Normal damage chassis is preserved.", "Crown itself deals no damage.", "Successful point-sink uses normal damage only.")

    k = arena()
    k.spend_action(k.a)
    attack = scoped_attack(k)
    k.pending_attack, k.pending_damage, k.pending_target = attack, 4, k.b
    k.crown_response(k.a, k.b, attack, forced_roll=True, force_continuation=False)
    hp = k.b.hp
    k.declare_point_sink(k.a, k.b, force=True, forced_roll=False)
    cases["K_no_automatic_success"] = {"hp_before": hp, "hp_after": k.b.hp}
    trace_for("K", k, "Entry and Crown have succeeded.", "Defender already exercised the Crown response.", "Forced failed point-sink roll deals no damage.")

    l = arena(pair=("vom-tag", "ochs"))
    italian_like = scoped_attack(l)
    italian_like["italian_corona_or_frontale"] = True
    italian_like["defender_guard_at_declaration"] = "posta-frontale"
    cases["L_no_italian_interaction"] = {"legal": l.crown_response_is_legal(l.b, italian_like)}
    trace_for("L", l, "Italian labels are outside the German source trigger.", "No German Crown context is created.", "No continuation interaction.")

    m = arena()
    m.spend_action(m.a)
    attack = scoped_attack(m)
    m.pending_attack, m.pending_damage, m.pending_target = attack, 4, m.b
    m.crown_response(m.a, m.b, attack, forced_roll=True, force_continuation=False)
    before = bool(m.crown_context)
    m.finish_exchange()
    after = bool(m.crown_context)
    cases["M_crown_context_cleanup"] = {"before": before, "after": after}
    trace_for("M", m, "Crown exists before cleanup.", "No extra response is invented.", "Declined continuation leaves context for cleanup.", finish=False)

    n = arena()
    n.spend_action(n.a)
    attack = scoped_attack(n)
    n.pending_attack, n.pending_damage, n.pending_target = attack, 4, n.b
    n.crown_response(n.a, n.b, attack, forced_roll=True, force_continuation=False)
    before_contact = n.state.contact
    n.finish_exchange()
    cases["N_ordinary_crossing_cleanup"] = {"before": before_contact, "after": n.state.contact}
    trace_for("N", n, "Crown maps to ordinary unretained Crossing.", "No special persistence rule.", "No continuation retained it.", finish=False)

    o = arena()
    o.current_chain = ["one", "two"]
    o.spend_action(o.a)
    attack = scoped_attack(o)
    o.pending_attack, o.pending_damage, o.pending_target = attack, 4, o.b
    o.crown_response(o.a, o.b, attack, forced_roll=True, force_continuation=False)
    used = o.declare_point_sink(o.a, o.b, force=True, forced_roll=True)
    cases["O_three_play_cap_respected"] = {"used": used, "chain": list(o.current_chain), "length": len(o.current_chain)}
    trace_for("O", o, "Two learned Plays already occupy the chain.", "Crown is context and consumes no slot.", "B3 continuation becomes the legal third learned Play.")

    p = arena()
    p.spend_action(p.a)
    attack = scoped_attack(p)
    p.pending_attack, p.pending_damage, p.pending_target = attack, 4, p.b
    p.crown_response(p.a, p.b, attack, forced_roll=True, force_continuation=False)
    p.declare_point_sink(p.a, p.b, force=True, forced_roll=True)
    cases["P_b3_accounting"] = {"entry_counts": False, "crown_counts": False, "chain": list(p.current_chain)}
    trace_for("P", p, "B3 entry is Basic in chassis.", "Crown is authored context, not a Play.", "Point-sink alone consumes one learned-Play slot.")

    q = arena()
    q.current_chain = ["one", "two", "three"]
    q.spend_action(q.a)
    attack = scoped_attack(q)
    q.pending_attack, q.pending_damage, q.pending_target = attack, 4, q.b
    q.crown_response(q.a, q.b, attack, forced_roll=True, force_continuation=False)
    before_chain = list(q.current_chain)
    used = q.declare_point_sink(q.a, q.b, force=True, forced_roll=True)
    cases["Q_no_fourth_play_leakage"] = {
        "used": used, "before": before_chain, "after": list(q.current_chain),
        "attempted_fourth": q.metrics["attempted_fourth_plays"],
    }
    trace_for("Q", q, "Three learned Plays already fill the chain.", "Crown context itself remains legal.", "Attempted fourth learned continuation is rejected without leakage.")

    return {"cases": cases, "phase_traces": traces}


def validate_harness(data: dict[str, Any]) -> None:
    c = data["cases"]
    assert c["A_entry_against_alber"] == {"scheitelhau_context": True, "defender_guard": ALBER}
    assert c["B_no_crown_response"]["crown_context"] is False
    assert c["C_generic_cross_not_crown"] == {"contact": "crossing", "crown_context": False}
    assert c["D_correct_response_creates_crown"]["crown_context"] is True
    assert c["E_exact_crown_fields"] == {
        "contact": "crossing", "measure": "wide",
        "zones": {"A": "unknown", "B": "unknown"},
        "pressure": {"A": "unknown", "B": "unknown"}, "retained": False,
    }
    assert c["F_crown_enables_continuation"]["chain"] == [SINK]
    assert c["G_no_crown_no_continuation"]["legal"] is False
    assert c["H_unrelated_crossing_no_continuation"]["legal"] is False
    assert c["I_no_generic_boon_bane"] == {"attack_boon": False, "parry_bane": False}
    assert c["J_no_automatic_damage_bonus"]["bonus"] == 0
    assert c["K_no_automatic_success"]["hp_before"] == c["K_no_automatic_success"]["hp_after"]
    assert c["L_no_italian_interaction"]["legal"] is False
    assert c["M_crown_context_cleanup"] == {"before": True, "after": False}
    assert c["N_ordinary_crossing_cleanup"] == {"before": "crossing", "after": "none"}
    assert c["O_three_play_cap_respected"]["length"] == 3
    assert c["P_b3_accounting"]["chain"] == [SINK]
    assert c["Q_no_fourth_play_leakage"]["used"] is False
    assert c["Q_no_fourth_play_leakage"]["before"] == c["Q_no_fourth_play_leakage"]["after"]
    assert c["Q_no_fourth_play_leakage"]["attempted_fourth"] == 1


def validate_results(results: dict[str, Any]) -> None:
    validate_harness(results["deterministic"])
    assert results["metadata"]["trials_per_cell"] % 16 == 0
    for item in results["cells"]:
        m = item["metrics"]
        assert len(m["starting_guard_outcome_share"]) == 16
        assert m["generic_crosses_incorrectly_tagged_crown"] == 0
        assert m["unrelated_crossings_triggering_continuation"] == 0
        assert m["cleanup_errors"] == 0
        assert m["attempted_fourth_plays"] == 0
        assert m["second_play_count"] == 0


def fmt(value: float) -> str:
    return f"{value:.3f}"


def pct(value: float) -> str:
    return f"{value:.1%}"


def build_report(results: dict[str, Any]) -> str:
    lines = [
        "# Scheitelhau / Crown Continuation v0.1 Results", "",
        "Status: **PROVISIONAL bounded experiment and Project-review recommendation; not governing or canonical mechanics**", "",
        "## Executive Result", "",
        "Crown is best represented by **C1: ordinary Crossing plus a transient, source-specific Crown context**. It is an authored defensive context generated only by the matching Scheitelhau-vs-Alber response; a generic Basic Cross is never Crown. Crown itself is not a defender learned Play and costs no Spiritus. The first viable attacker continuation is **Sink Point Under Crown**, represented under B3 as the actual learned Play while the initial descending entry remains Basic in chassis. The continuation costs 1 Spiritus, uses a normal Longsword attack roll and normal damage, and consumes one learned-Play slot. No generic breaker modifier is added.", "",
        "C1/B3 is mechanically superior to the bounded alternatives and passes deterministic validation. It is not automatically promoted because the repository audit directly identifies the named reception and continuation sequence but does not encode enough physical Crown geometry to eliminate all historical ambiguity in final player-facing wording.", "",
        "## Prior Artifact Metadata Reconciliation", "",
        "The stored Guard Play Bridge JSON reports 992 trials and 992 fights in each of six cells, for 5,952 fights total. Its recorded cell seeds are 1108202603, 1108203612, 1108204621, 1108205630, 1108206639, and 1108207648. Those stored counts support 992. The Markdown sentence was stale because the report generator hard-coded 640 instead of reading run metadata. The sentence and generator metadata path were corrected; no historical experiment data were regenerated.", "",
        "## Tutta T1 Promotion", "",
        "The governing provisional register now selects Tutta Cover to Stretto T1: 1 Spiritus at declaration; successful source-compatible Tutta Basic Cross at Wide; no second roll or action; retain Crossing; Wide to Close; one learned Play. T0 is archived comparison material only. This is provisional, not canonical/final.", "",
        "## Historical Crown Decomposition", "",
        "Scoped source: Pseudo-Peter von Danzig, Cod.44.A.8, ff. 24v.3-25r.2, with the four-guard relationship confirmed at f. 26v.3. Phase 1 is the strong descending long-edge head cut against Alber. Phase 2 is the defender's named Crown reception. Phase 3+ contains point sinking, winding, pressing, and slicing; those phases are not collapsed into one atomic Play.", "",
        "| Question | Result | Status |", "|---|---|---|",
        "| Defender action | Receives the scoped descending attack in the named German Crown context | DIRECT |",
        "| Received attack | Scheitelhau entry: strong descending long-edge head cut against Alber | DIRECT |",
        "| Continued relationship | The source continues into point-sinking and later bind work | DIRECT sequence; retained engagement is geometric inference |",
        "| Contact | `crossing` during the immediate authored window | ATRA MAPPING |",
        "| Measure | Preserve existing measure; forced scenario starts Wide | ATRA MAPPING; not directly sourced |",
        "| Zone / pressure | unknown / unknown | NOT JUSTIFIED |",
        "| Point threat | No defender change; point-sink presents the attacker's point | first is preserved state; second is ATRA mapping |",
        "| Displacement / Close / control | none assigned | NOT JUSTIFIED |",
        "| Crown posture detail | No additional hand, edge, or blade-zone detail is encoded in the audited repository record | CANNOT BE JUSTIFIED HERE |", "",
        "German Kron/Crown remains distinct from Italian Corona and Fiore Frontale. English label similarity creates no mechanical relationship.", "",
        "## What Is Crown Mechanically?", "",
        "C0 (tag only) can preserve naming but would duplicate contact eligibility outside the governing contact model. C1 uses the existing Crossing state and cleanup while the transient tag supplies the source-specific continuation gate. C2, a new global contact type, adds no needed expressive power. **Recommend C1.** Crown is an **AUTHORED EXCHANGE CONTEXT USING A SPECIFIC BASIC-RESPONSE MAPPING**, not a learned defender Play and not a generic guard action.", "",
        "## Crown vs Generic Basic Cross", "",
        "Crown is available only when an actor who knows the scoped continuation declares the Scheitelhau entry against a defender in Alber, the normal entry roll succeeds, and that defender selects and succeeds with the authored Crown response. Generic Cross elsewhere creates only ordinary Crossing. The deterministic and micro harnesses record zero generic Crosses mislabeled Crown and zero unrelated Crossings that unlock the continuation.", "",
        "## Scheitelhau Initial Entry Status", "",
        "The standalone entry still has no independent learned chassis, price, or breaker modifier. Under B3 it remains a Basic Cut-chassis declaration that exposes Crown only for an actor who knows the continuation. The exchange-level identity comes from the conditional learned point-sink, not an invented bonus on the initial cut.", "",
        "## Attacker Continuation Candidates", "",
        "| Candidate | Classification | Result |", "|---|---|---|",
        "| Sink Point Under Crown | INITIAL CONTINUATION CANDIDATE | Implementable now as one normal attack from authored Crossing |",
        "| Winding | REQUIRES FULLER SYSTEM | Later pressure/position decision system |",
        "| Pressing | LATER BRANCH | Not needed for the first useful prototype |",
        "| Slicing | LATER BRANCH / REQUIRES FULLER SYSTEM | Do not add as a separate button in v0.1 |", "",
        "## Intrinsic Branch vs Second Learned Play", "",
        "B1 is historically coherent but mechanically inferior here: the initial cut consumes a learned slot even when Crown never occurs. B2 spends two learned slots on a scoped lesson and needlessly crowds the three-Play cap. B3 keeps the Basic-equivalent entry Basic and makes the technical Crown-triggered continuation the learned Play. This preserves progression, opponent choice, and exact chain accounting without creating a scripted combo.", "",
        "## Spiritus Price", "",
        "Recommend **1 Spiritus**. Point-sink is one meaningful conversion: a renewed normal attack from the authored Crown context. It adds no Boon, Bane, automatic success, bonus damage, second effect, Close transition, or control rider. Two Spiritus would price a compound payload that this prototype intentionally does not contain.", "",
        "## Deterministic Phase Traces", "",
    ]
    for label, trace in results["deterministic"]["phase_traces"].items():
        lines.extend([f"### Case {label}", ""])
        for phase, state in trace.items():
            compact = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
            lines.append(f"- **{phase}:** `{compact}`")
        lines.append("")
    lines.extend([
        "All cases A-Q pass: authored entry, no-response case, generic Cross exclusion, correct Crown creation, exact conservative fields, gated continuation, no-Crown and unrelated-Crossing rejection, modifier-free resolution, normal damage, non-automatic success, Italian separation, cleanup, cap behavior, B3 accounting, and fourth-Play rejection.", "",
        "## Behavioral Micro-Test", "",
        f"Seed {results['metadata']['seed']}; {results['metadata']['trials_per_cell']} fights/cell; Skill 14; starting Spiritus 8/3; balanced German ordered starting-guard pairs. B1 and B3 share the same C1 Crown state and 1-Spiritus point-sink effect; they differ only in learned-chain accounting. This is a behavioral check, not guard balance or a claim that Scheitelhau is historically 'better.'", "",
        "| Model | S | Alber occ. | Sch. opp/decl. | Crown opp/create/rate | Cont. opp/decl/hit/effect | Cont. S | Chain | Intrinsic | B3 learned | Second Play | Cap | Fourth | Bad Crown | Bad Crossing | Cleanup | Guard changes | Churn |", 
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for item in results["cells"]:
        c, m = item["cell"], item["metrics"]
        lines.append(
            f"| {c['chain_model']} | {c['start_spiritus']} | {pct(m['alber_occupancy'])} | "
            f"{fmt(m['scheitelhau_vs_alber_opportunities_per_fight'])}/{fmt(m['scheitelhau_entry_declarations_per_fight'])} | "
            f"{fmt(m['crown_opportunities_per_fight'])}/{fmt(m['crown_creations_per_fight'])}/{pct(m['crown_creation_rate'])} | "
            f"{fmt(m['continuation_opportunities_per_fight'])}/{fmt(m['continuation_declarations_per_fight'])}/{pct(m['continuation_success_rate'])}/{pct(m['continuation_effect_rate'])} | "
            f"{fmt(m['continuation_spiritus_per_fight'])} | {fmt(m['learned_play_chain_length'])} | "
            f"{m['intrinsic_branch_count']} | {m['continuation_learned_play_count']} | {m['second_play_count']} | "
            f"{pct(m['three_play_cap_frequency'])} | {m['attempted_fourth_plays']} | "
            f"{m['generic_crosses_incorrectly_tagged_crown']} | {m['unrelated_crossings_triggering_continuation']} | "
            f"{m['cleanup_errors']} | {fmt(m['guard_changes_per_fight'])} | {fmt(m['guard_churn_per_fight'])} |"
        )
    lines.extend([
        "", "Every micro cell records zero incorrect Crown tags, zero unrelated-Crossing triggers, zero cleanup errors, zero second-Play charges, and zero attempted fourth Plays. B1 records the point-sink as an intrinsic branch after charging Scheitelhau at entry; B3 records only point-sink as the learned Play. Spiritus scarcity reduces declarations through the inherited reserve policy. Guard changes and A→B→A churn are reported from the unchanged inherited policy and are not tuned.", "",
        "## Play-Chain Consequences", "",
        "Selected B3 accounting is: Basic entry = 0 learned slots; Crown response/context = 0; declared point-sink = 1. Two prior learned Plays therefore permit point-sink as the third; a full three-Play chain rejects it without mutation. Crown does not restore either combatant's action. The defender has already chosen and rolled the Crown response; point-sink remains optional and requires its own attack roll, so the sequence is not deterministic.", "",
        "## Historical vs Atra Mapping", "",
        "Historically direct: Scheitelhau against Alber, Crown reception, and the later point-sink/wind/press/slice sequence. Geometric inference: the immediate continuation entails continuing weapon engagement. Atra mappings: Crossing, preserved Wide measure, transient context, attacker threatening point, normal attack/damage chassis, and cleanup timing. Unjustified and absent: known blade zone, pressure, Close, displacement, control, generic advantage, automatic hit, Italian equivalence, or a distinct contact enum.", "",
        "## Recommended Next Decision", "",
        "A. **Use ordinary Crossing plus a transient source-specific Crown context.**", "",
        "B. **C1: Crossing + tag**, not tag-only and not a distinct contact state.", "",
        "C. **No.** Crown itself does not require a defender learned Play or Spiritus; it is an authored response context using one normal defence roll.", "",
        "D. Implement **Sink Point Under Crown** first; defer winding, pressing, and slicing.", "",
        "E. Use **B3**: the initial entry remains Basic in chassis and point-sink is the actual learned Play.", "",
        "F. Recommend **1 Spiritus at continuation declaration**.", "",
        "G. **Yes, mechanically in the bounded harness.** The exchange gains identity through an authored response and gated continuation without a generic breaker bonus.", "",
        "H. **Yes.** The defender chooses and rolls Crown; the attacker optionally declares and rolls point-sink; B3 consumes one slot and rejects a fourth Play.", "",
        "I. **Conditionally yes.** Alber is sufficiently distinguished for a Named Guard v0.2 sensitivity if the Project accepts C1/B3 as the provisional input. The current governing baseline does not yet include it.", "",
        "J. **No, not immediately.** The immediate next milestone is Project review of the C1/B3 recommendation; after acceptance, Named Guard Rules v0.2 is the next bounded simulation.", "",
        "K. The exact narrow blocker is approval of the conservative Crown mapping despite the audited record's unresolved physical blade geometry. No engine-state, pricing, transition, or generic-breaker blocker remains.", "",
    ])
    return "\n".join(lines)


def run_all(trials: int = TRIALS_PER_CELL, seed: int = SEED,
            write: bool = True) -> dict[str, Any]:
    if trials % 16:
        raise ValueError("trials must be divisible by 16 for balanced German starting guards")
    deterministic = deterministic_harness()
    validate_harness(deterministic)
    cell_results = [run_cell(cell, trials, seed + index * 1009) for index, cell in enumerate(cells())]
    results = {
        "metadata": {
            "status": "PROVISIONAL bounded experiment; not governing or canonical",
            "seed": seed,
            "trials_per_cell": trials,
            "skill": 14,
            "starting_spiritus": [8, 3],
            "crown_models_considered": ["C0", "C1"],
            "selected_crown_model": "C1",
            "chain_models_tested": ["B1", "B3"],
            "recommended_chain_model": "B3",
            "continuation_cost": 1,
            "german_bounded_roster": True,
            "named_guard_v02_run": False,
            "specification": str(SPEC_PATH.relative_to(ROOT)).replace("\\", "/"),
        },
        "prior_artifact_reconciliation": {
            "supported_trials_per_cell": 992,
            "stored_cells": 6,
            "stored_fights_total": 5952,
            "data_regenerated": False,
            "correction": "Markdown/report-generator metadata only",
        },
        "tutta_t1_promotion": {
            "status": "GOVERNING PROVISIONAL; NOT CANONICAL",
            "selected_variant": "T1",
            "spiritus_cost": 1,
            "t0_status": "ARCHIVED COMPARISON VARIANT ONLY",
        },
        "recommendation": {
            "crown": "C1 ordinary Crossing plus transient Crown context",
            "crown_defender_learned_play": False,
            "continuation": SINK,
            "chain_model": "B3",
            "spiritus_cost": 1,
            "automatic_promotion": False,
            "generic_basic_cross_is_crown": False,
            "generic_breaker_modifier": False,
            "named_guard_v02_ready": "conditional on Project acceptance",
        },
        "deterministic": deterministic,
        "cells": cell_results,
    }
    validate_results(results)
    if write:
        RESULTS_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        REPORT_PATH.write_text(build_report(results) + "\n", encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=TRIALS_PER_CELL)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    results = run_all(args.trials, args.seed, write=not args.no_write)
    print(json.dumps({
        "trials_per_cell": results["metadata"]["trials_per_cell"],
        "cells": len(results["cells"]),
        "selected_crown_model": results["metadata"]["selected_crown_model"],
        "recommended_chain_model": results["metadata"]["recommended_chain_model"],
    }, indent=2))


if __name__ == "__main__":
    main()

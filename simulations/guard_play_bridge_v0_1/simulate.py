from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
NAMED_GUARD_PATH = ROOT / "simulations" / "named_guard_rules_v0_1" / "simulate.py"
SPEC_PATH = ROOT / "data" / "prototypes" / "longsword-guard-play-bridge-v0.1.yaml"
RESULTS_PATH = ROOT / "reports" / "guard-play-bridge-v01-results.json"
REPORT_PATH = ROOT / "reports" / "guard-play-bridge-v01-results.md"

IMPORT_SPEC = importlib.util.spec_from_file_location("atra_guard_play_bridge_named_guard", NAMED_GUARD_PATH)
GUARD = importlib.util.module_from_spec(IMPORT_SPEC)
assert IMPORT_SPEC.loader is not None
sys.modules[IMPORT_SPEC.name] = GUARD
IMPORT_SPEC.loader.exec_module(GUARD)

SHARED = GUARD.SHARED
ENGINE = GUARD.ENGINE
BASE = GUARD.BASE

MODELS = ("CONTROL", "T0", "T1")
TUTTA = "Tutta Cover to Stretto"
TUTTA_GUARD = "tutta-porta-di-ferro"
SEED = 1108202603
TRIALS_PER_CELL = 640


@dataclass(frozen=True)
class Cell:
    model: str
    skill: int
    start_spiritus: int
    information: str = "adaptive_revelation"

    @property
    def cost(self) -> int | None:
        return {"CONTROL": None, "T0": 0, "T1": 1}[self.model]

    @property
    def label(self) -> str:
        return f"{self.model}_skill{self.skill}_S{self.start_spiritus}"


def ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def fresh_metrics() -> dict[str, Any]:
    metrics = GUARD.fresh_metrics()
    metrics["plays"][TUTTA] = BASE.play_stats()
    metrics.update({
        "tutta_spiritus_spent": 0,
        "tutta_source_cover_opportunities": 0,
        "tutta_successful_triggering_crosses": 0,
        "tutta_continuation_opportunities": 0,
        "tutta_continuation_declarations": 0,
        "tutta_continuation_successes": 0,
        "tutta_wide_to_close_transitions": 0,
        "tutta_retained_crossing_close_states": 0,
        "close_measure_exchange_slots": 0,
        "close_measure_activation_slots": 0,
        "downstream_pommel_opportunities": 0,
        "downstream_pommel_uses": 0,
        "unauthorized_close_origins": 0,
        "tutta_decisions": Counter(),
    })
    return metrics


class GuardPlayBridgeDuel(GUARD.NamedGuardDuel):
    """G1 named guards plus only the scoped Tutta learned continuation."""

    def __init__(self, rng: random.Random, policy_rng: random.Random, cell: Cell,
                 metrics: dict[str, Any], starting_pair: tuple[str, str]) -> None:
        parent_cell = GUARD.Cell("G1", "Italian", cell.skill, cell.start_spiritus, cell.information)
        super().__init__(rng, policy_rng, parent_cell, metrics, starting_pair)
        self.bridge_cell = cell
        self.bridge_attack: dict[str, Any] | None = None
        self.close_has_authored_origin = False

    def source_compatible_cover(self, defender: BASE.Fighter, attack: dict[str, Any] | None) -> bool:
        return bool(
            attack
            and attack.get("choice_key") == "basic_cut"
            and self.current_guard(defender) == TUTTA_GUARD
            and self.state.measure == "wide"
        )

    def continuation_value(self, actor: BASE.Fighter, opponent: BASE.Fighter) -> float:
        # Transparent one-step opportunity proxy. It values the authored Close
        # state, not automatic Pommel damage. T0/T1 differ only by reserve charge.
        value = 0.25 + 0.15 * (ENGINE.MAX_HP - opponent.hp) / ENGINE.MAX_HP
        cost = self.bridge_cell.cost
        if cost:
            value -= BASE.reserve_charge(actor.spiritus, cost)
        return value

    def continuation_is_legal(self, actor: BASE.Fighter, attack: dict[str, Any] | None) -> bool:
        cost = self.bridge_cell.cost
        return bool(
            cost is not None
            and self.source_compatible_cover(actor, attack)
            and self.state.contact == "crossing"
            and self.state.measure == "wide"
            and len(self.current_chain) < SHARED.LEARNED_PLAY_CAP
            and actor.spiritus >= cost
        )

    def declare_tutta_continuation(self, actor: BASE.Fighter, opponent: BASE.Fighter,
                                   attack: dict[str, Any] | None,
                                   force: bool | None = None) -> bool:
        if not self.continuation_is_legal(actor, attack):
            return False
        self.metrics["tutta_continuation_opportunities"] += 1
        if force is None:
            choice = self.softmax({TUTTA: self.continuation_value(actor, opponent), "decline": 0.0})
            declare = choice == TUTTA
        else:
            declare = force
        self.metrics["tutta_decisions"]["declare" if declare else "decline"] += 1
        if not declare:
            return False
        if not self.add_play(TUTTA):
            return False
        cost = self.bridge_cell.cost or 0
        if cost and not self.spend_spiritus(actor, cost, "tutta"):
            return False
        self.metrics["tutta_continuation_declarations"] += 1
        self.metrics["tutta_continuation_successes"] += 1
        self.metrics["plays"][TUTTA]["successes"] += 1
        self.state.measure = "close"
        self.state.retain_crossing = True
        self.close_has_authored_origin = True
        self.metrics["tutta_wide_to_close_transitions"] += 1
        return True

    def defence_values(self, attacker: BASE.Fighter, defender: BASE.Fighter,
                       attack: dict[str, Any]) -> dict[str, float]:
        values = super().defence_values(attacker, defender, attack)
        if (
            self.bridge_cell.cost is not None
            and self.source_compatible_cover(defender, attack)
            and len(self.current_chain) < SHARED.LEARNED_PLAY_CAP
            and defender.spiritus >= self.bridge_cell.cost
            and "Basic Cross" in values
        ):
            p_cross = BASE.success_probability(defender.skill)
            values["Basic Cross"] += p_cross * max(0.0, self.continuation_value(defender, attacker))
        return values

    def defend(self, attacker: BASE.Fighter, defender: BASE.Fighter, attack: dict[str, Any],
               attribution: str | None) -> None:
        if defender.action_ready and self.source_compatible_cover(defender, attack):
            self.metrics["tutta_source_cover_opportunities"] += 1
        self.bridge_attack = attack
        try:
            super().defend(attacker, defender, attack, attribution)
        finally:
            self.bridge_attack = None

    def basic_parry(self, form: str, attacker: BASE.Fighter, defender: BASE.Fighter,
                    attribution: str | None, forced_roll: bool | None = None,
                    force_durch: bool | None = None,
                    force_tutta: bool | None = None) -> str:
        attack = self.bridge_attack
        compatible_at_declaration = self.source_compatible_cover(defender, attack)
        result = super().basic_parry(form, attacker, defender, attribution, forced_roll, force_durch)
        if result == "success" and form == "Cross" and compatible_at_declaration:
            self.metrics["tutta_successful_triggering_crosses"] += 1
            self.declare_tutta_continuation(defender, attacker, attack, force_tutta)
        return result

    def pommel_is_legal(self, actor: BASE.Fighter) -> bool:
        return bool(actor.action_ready and self.state.contact == "crossing" and self.state.measure == "close")

    def pommel(self, actor: BASE.Fighter, target: BASE.Fighter,
               forced_roll: bool | None = None) -> bool:
        if not self.pommel_is_legal(actor):
            return False
        self.metrics["downstream_pommel_opportunities"] += 1
        uses_before = self.metrics["plays"][BASE.POMMEL]["uses"]
        result = super().pommel(actor, target, forced_roll)
        if self.metrics["plays"][BASE.POMMEL]["uses"] > uses_before:
            self.metrics["downstream_pommel_uses"] += 1
        return result

    def activate(self, actor: BASE.Fighter) -> None:
        if self.state.measure == "close":
            self.metrics["close_measure_activation_slots"] += 1
            if not self.close_has_authored_origin:
                self.metrics["unauthorized_close_origins"] += 1
        super().activate(actor)

    def finish_exchange(self) -> None:
        if self.state.measure == "close":
            self.metrics["close_measure_exchange_slots"] += 1
            if not self.close_has_authored_origin:
                self.metrics["unauthorized_close_origins"] += 1
        if self.state.contact == "crossing" and self.state.measure == "close" and self.state.retain_crossing:
            self.metrics["tutta_retained_crossing_close_states"] += 1
        super().finish_exchange()


def finalize(metrics: dict[str, Any]) -> dict[str, Any]:
    output = GUARD.finalize(metrics)
    fights = metrics["fights"]
    exchanges = metrics["exchanges"]
    transitions = metrics["tutta_wide_to_close_transitions"]
    chain_total = sum(metrics["chain_distribution"].values())
    tutta_uses = metrics["plays"][TUTTA]["uses"]
    total_learned = sum(item["uses"] for item in metrics["plays"].values())
    output.update({
        "tutta_occupancy": output["guard_occupancy_share"].get(TUTTA_GUARD, 0.0),
        "source_compatible_cover_opportunities_per_fight": ratio(metrics["tutta_source_cover_opportunities"], fights),
        "successful_triggering_crosses_per_fight": ratio(metrics["tutta_successful_triggering_crosses"], fights),
        "continuation_opportunities_per_fight": ratio(metrics["tutta_continuation_opportunities"], fights),
        "continuation_declarations_per_fight": ratio(metrics["tutta_continuation_declarations"], fights),
        "continuation_uses_per_fight": ratio(tutta_uses, fights),
        "continuation_declaration_rate": ratio(metrics["tutta_continuation_declarations"], metrics["tutta_continuation_opportunities"]),
        "continuation_spiritus_per_fight": ratio(metrics["tutta_spiritus_spent"], fights),
        "wide_to_close_transitions_per_fight": ratio(transitions, fights),
        "retained_crossing_close_states_per_fight": ratio(metrics["tutta_retained_crossing_close_states"], fights),
        "close_duration_exchange_slots_per_transition": ratio(metrics["close_measure_exchange_slots"], transitions),
        "close_duration_activation_slots_per_transition": ratio(metrics["close_measure_activation_slots"], transitions),
        "downstream_pommel_opportunities_per_fight": ratio(metrics["downstream_pommel_opportunities"], fights),
        "downstream_pommel_uses_per_fight": ratio(metrics["downstream_pommel_uses"], fights),
        "other_learned_plays_per_fight": ratio(total_learned - tutta_uses, fights),
        "chain_length_distribution": {
            key: ratio(value, chain_total) for key, value in sorted(metrics["chain_distribution"].items())
        },
        "unauthorized_close_origins": metrics["unauthorized_close_origins"],
        "unauthorized_close_origins_per_fight": ratio(metrics["unauthorized_close_origins"], fights),
        "total_spiritus_per_fight": output["spiritus_expenditure_per_fight"],
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
    pairs = GUARD.ordered_pairs("Italian")
    for index in range(trials):
        pair = pairs[index % len(pairs)]
        duel = GuardPlayBridgeDuel(rng, policy_rng, cell, metrics, pair)
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
    finalized = finalize(metrics)
    for bucket in finalized["starting_guard_outcome_share"].values():
        bucket["A_share"] = ratio(bucket["A"], bucket["trials"])
        bucket["B_share"] = ratio(bucket["B"], bucket["trials"])
        bucket["double_share"] = ratio(bucket["double"], bucket["trials"])
    return {"cell": asdict(cell), "seed": seed, "trials": trials, "metrics": finalized}


def deterministic_harness() -> dict[str, Any]:
    def arena(model: str = "T1", pair: tuple[str, str] = ("posta-di-donna", TUTTA_GUARD)) -> GuardPlayBridgeDuel:
        return GuardPlayBridgeDuel(
            random.Random(7), random.Random(11), Cell(model, 14, 8, "perfect_information"),
            fresh_metrics(), pair,
        )

    def pending_cut(duel: GuardPlayBridgeDuel) -> dict[str, Any]:
        attack = duel.make_attack("basic_cut")
        duel.pending_attack = attack
        duel.pending_damage = 4
        duel.pending_target = duel.b
        duel.bridge_attack = attack
        return attack

    out: dict[str, Any] = {}

    duel = arena("T1")
    attack = pending_cut(duel)
    action_before = duel.b.action_ready
    hp_before = (duel.a.hp, duel.b.hp)
    spiritus_before = duel.b.spiritus
    attacks_before = sum(item["declarations"] for item in duel.metrics["attack_stats"].values())
    result = duel.basic_parry("Cross", duel.a, duel.b, attack["attribution"], True, False, True)
    out["A_tutta_success"] = {
        "result": result,
        "opportunities": duel.metrics["tutta_continuation_opportunities"],
        "declarations": duel.metrics["tutta_continuation_declarations"],
        "contact": duel.state.contact,
        "measure": duel.state.measure,
        "retained": duel.state.retain_crossing,
        "spent": spiritus_before - duel.b.spiritus,
        "action_before": action_before,
        "action_after": duel.b.action_ready,
        "hp_before": hp_before,
        "hp_after": (duel.a.hp, duel.b.hp),
        "attack_declarations_before": attacks_before,
        "attack_declarations_after": sum(item["declarations"] for item in duel.metrics["attack_stats"].values()),
        "parry_rolls": duel.metrics["parry_rolls"]["Cross"],
        "chain": list(duel.current_chain),
    }

    wrong = arena("T1", ("tutta-porta-di-ferro", "posta-frontale"))
    attack = pending_cut(wrong)
    wrong.basic_parry("Cross", wrong.a, wrong.b, attack["attribution"], True, False, True)
    out["B_wrong_guard"] = {"opportunities": wrong.metrics["tutta_continuation_opportunities"]}

    failed = arena("T1")
    attack = pending_cut(failed)
    failed.basic_parry("Cross", failed.a, failed.b, attack["attribution"], False, False, True)
    out["C_failed_cross"] = {"opportunities": failed.metrics["tutta_continuation_opportunities"], "contact": failed.state.contact}

    beat = arena("T1")
    attack = pending_cut(beat)
    beat.basic_parry("Beat", beat.a, beat.b, attack["attribution"], True, False, True)
    out["D_beat"] = {"opportunities": beat.metrics["tutta_continuation_opportunities"], "contact": beat.state.contact}

    interrupted = arena("T1")
    attack = pending_cut(interrupted)
    interrupted.basic_parry("Cross", interrupted.a, interrupted.b, attack["attribution"], True, True, True)
    out["E_durch_interruption"] = {
        "opportunities": interrupted.metrics["tutta_continuation_opportunities"],
        "contact": interrupted.state.contact,
    }

    costs: dict[str, int] = {}
    for model in ("T0", "T1"):
        cost_duel = arena(model)
        attack = pending_cut(cost_duel)
        before = cost_duel.b.spiritus
        cost_duel.basic_parry("Cross", cost_duel.a, cost_duel.b, attack["attribution"], True, False, True)
        costs[model] = before - cost_duel.b.spiritus
    out["F_G_costs"] = costs

    cap = arena("T0")
    cap.current_chain = ["one", "two", "three"]
    cap.create_crossing(cap.b, cap.a, measure="wide", first_pressure="hard", second_pressure="hard")
    cap_attack = cap.make_attack("basic_cut")
    cap.bridge_attack = cap_attack
    used = cap.declare_tutta_continuation(cap.b, cap.a, cap_attack, True)
    before_attempts = cap.metrics["attempted_fourth_plays"]
    direct_fourth = cap.add_play(TUTTA)
    out["J_K_cap"] = {
        "legal_opportunity": cap.metrics["tutta_continuation_opportunities"],
        "used": used,
        "direct_fourth": direct_fourth,
        "attempted_fourth_increment": cap.metrics["attempted_fourth_plays"] - before_attempts,
    }

    pommel = arena("T1")
    attack = pending_cut(pommel)
    pommel.basic_parry("Cross", pommel.a, pommel.b, attack["attribution"], True, False, True)
    immediate = pommel.pommel_is_legal(pommel.b)
    pommel.b.action_ready = True
    later = pommel.pommel_is_legal(pommel.b)
    pommel_used = pommel.pommel(pommel.b, pommel.a, True)
    out["L_pommel_consumer"] = {
        "immediate_while_action_spent": immediate,
        "later_with_action": later,
        "used": pommel_used,
        "contact_after": pommel.state.contact,
    }

    cleanup = arena("CONTROL")
    attack = pending_cut(cleanup)
    cleanup.basic_parry("Cross", cleanup.a, cleanup.b, attack["attribution"], True, False)
    before_cleanup = cleanup.state.contact
    cleanup.finish_exchange()
    out["M_cleanup"] = {"before": before_cleanup, "after": cleanup.state.contact, "measure": cleanup.state.measure}

    out["N_scheitelhau_specification"] = {
        "initial_entry_implemented": False,
        "automatic_boon": False,
        "automatic_bane": False,
        "automatic_success": False,
        "automatic_damage_bonus": False,
        "generic_cross_is_crown": False,
        "spiritus_cost": None,
    }
    return out


def validate_harness(cases: dict[str, Any]) -> None:
    success = cases["A_tutta_success"]
    assert success["result"] == "success"
    assert success["opportunities"] == success["declarations"] == 1
    assert (success["contact"], success["measure"], success["retained"]) == ("crossing", "close", True)
    assert success["spent"] == 1
    assert success["action_before"] and not success["action_after"]
    assert success["hp_before"] == success["hp_after"]
    assert success["attack_declarations_before"] == success["attack_declarations_after"]
    assert success["parry_rolls"] == 1
    assert success["chain"] == [TUTTA]
    assert cases["B_wrong_guard"]["opportunities"] == 0
    assert cases["C_failed_cross"] == {"opportunities": 0, "contact": "none"}
    assert cases["D_beat"] == {"opportunities": 0, "contact": "none"}
    assert cases["E_durch_interruption"] == {"opportunities": 0, "contact": "none"}
    assert cases["F_G_costs"] == {"T0": 0, "T1": 1}
    assert cases["J_K_cap"] == {
        "legal_opportunity": 0, "used": False, "direct_fourth": False, "attempted_fourth_increment": 1,
    }
    assert cases["L_pommel_consumer"] == {
        "immediate_while_action_spent": False, "later_with_action": True, "used": True, "contact_after": "none",
    }
    assert cases["M_cleanup"] == {"before": "crossing", "after": "none", "measure": "wide"}
    assert not any(value for key, value in cases["N_scheitelhau_specification"].items() if key != "spiritus_cost")
    assert cases["N_scheitelhau_specification"]["spiritus_cost"] is None


def aggregate(cells_data: list[dict[str, Any]], model: str) -> dict[str, float]:
    selected = [item["metrics"] for item in cells_data if item["cell"]["model"] == model]
    keys = (
        "tutta_occupancy", "source_compatible_cover_opportunities_per_fight",
        "successful_triggering_crosses_per_fight", "continuation_opportunities_per_fight",
        "continuation_declarations_per_fight", "continuation_uses_per_fight",
        "continuation_spiritus_per_fight", "wide_to_close_transitions_per_fight",
        "retained_crossing_close_states_per_fight", "close_duration_exchange_slots_per_transition",
        "close_duration_activation_slots_per_transition", "downstream_pommel_opportunities_per_fight",
        "downstream_pommel_uses_per_fight", "learned_plays_per_fight",
        "other_learned_plays_per_fight", "three_play_cap_frequency",
        "attempted_fourth_plays_per_fight", "guard_changes_per_fight", "total_spiritus_per_fight",
        "unauthorized_close_origins_per_fight",
    )
    output = {key: sum(item[key] for item in selected) / len(selected) for key in keys}
    output["continuation_declaration_rate"] = ratio(
        sum(item["tutta_continuation_declarations"] for item in selected),
        sum(item["tutta_continuation_opportunities"] for item in selected),
    )
    return output


def conditional_trigger_analysis(trials: int = 1000, seed: int = SEED ^ 0x71A) -> list[dict[str, Any]]:
    """Policy sensitivity after the historical/engine trigger is already met.

    Natural mirrored fights retain their actual sparse trigger frequency. This
    supplementary analysis isolates only the T0/T1 declaration decision so a
    zero-use natural cell is not misread as proof that its price has no effect.
    """
    output: list[dict[str, Any]] = []
    for model in ("T0", "T1"):
        for start in (8, 3):
            declarations = 0
            spent = 0
            for index in range(trials):
                metrics = fresh_metrics()
                duel = GuardPlayBridgeDuel(
                    random.Random(seed + index * 17 + start),
                    random.Random(seed + index * 31 + (0 if model == "T0" else 1)),
                    Cell(model, 14, start, "perfect_information"), metrics,
                    ("posta-di-donna", TUTTA_GUARD),
                )
                attack = duel.make_attack("basic_cut")
                duel.create_crossing(duel.b, duel.a, measure="wide", first_pressure="hard", second_pressure="hard")
                before = duel.b.spiritus
                if duel.declare_tutta_continuation(duel.b, duel.a, attack):
                    declarations += 1
                    spent += before - duel.b.spiritus
            output.append({
                "model": model,
                "start_spiritus": start,
                "trials": trials,
                "declarations": declarations,
                "declaration_rate": ratio(declarations, trials),
                "spiritus_per_trigger": ratio(spent, trials),
                "spiritus_per_declaration": ratio(spent, declarations),
            })
    return output


def fmt(value: float) -> str:
    return f"{value:.3f}"


def pct(value: float) -> str:
    return f"{value:.1%}"


def build_report(results: dict[str, Any]) -> str:
    aggregates = results["aggregates"]
    t0 = aggregates["T0"]
    t1 = aggregates["T1"]
    control = aggregates["CONTROL"]
    warning = results["technical_conclusions"]["free_close_warning"]
    lines = [
        "# Guard Play Bridge v0.1 Results", "",
        "Status: **PROVISIONAL bounded Play-integration experiment; not canonical mechanics**", "",
        "## Executive Result", "",
        "Scheitelhau's initial Alber-breaking entry is historically secure but not independently mechanically distinct from Basic Cut in the current engine. It is therefore **DEFERRED UNTIL A NARROW CROWN CONTINUATION**, receives no Spiritus price, and gains no breaker modifier. Generic Basic Cross remains distinct from Crown.", "",
        "Tutta cover-to-stretto is cleanly representable as a learned continuation: after a successful Tutta Basic Cross against an ordinary proactive Basic Cut at Wide measure, retain Crossing and change Wide to Close. It adds no roll, damage, attack, action restoration, grapple, disarm, or Pommel. T1 is recommended for Project review because the authored measure conversion is a meaningful one-effect enhancement and the 1-Spiritus cost preserves a live reserve decision.", "",
        "## Scope and Preserved Baseline", "",
        f"The simulator reuses the current G1 named-guard harness, which imports `simulations/shared/provisional_longsword.py`. D1, C2, S2, P1, Cross/Beat, explicit contact/measure state, free before-or-after guard change, and the three-learned-Play cap are unchanged. Skill is 14; starting Spiritus is 8 or 3; each of the six cells contains {results['metadata']['trials_per_cell']} mirrored fights balanced across all 16 ordered Italian starting-guard pairs. This is behavioral micro-analysis, not guard balance.", "",
        "No full Named Guard v0.2 matrix, guard-transition tuning, Parry DR, or unrelated Play redesign was run.", "",
        "## Source Basis", "",
        "- **Scheitelhau / Alber:** Pseudo-Peter von Danzig, Starhemberg Fechtbuch, Cod.44.A.8 (MS Cors.1449), anonymous gloss, 1452, ff. 24v.3-25r.2; confirming four-guard list f. 26v.3. The initial descending long-edge head cut and later Crown sequence remain separate phases.",
        "- **Tutta Porta di Ferro:** Fiore dei Liberi, Getty MS Ludwig XV 13, 23v-a; concordant Morgan MS M.383, 12r-a and Pisani Dossi 18a-a. Vadi MS Vitt.Em.1324, 16v-a remains continuity/context for a separately named Iron Gate, not an automatic exact equivalence.", "",
        "## Scheitelhau vs Alber — Initial Entry Viability", "",
        "1. **Can it be meaningful by itself?** No, not with current authored state.",
        "2. **Source-supported distinction from Basic Cut:** the opponent is in Alber and the action is the named strong descending long-edge head cut. Those facts identify the historical relationship but do not add a separate Atra outcome.",
        "3. **Can current state express the distinction?** No. Ordinary attack line, point threat, damage, and a defender's generic Basic Cross do not supply a distinct initial-entry effect.",
        "4. **Would implementation conflate Crown with Basic Cross?** Yes, if Crossing were assigned as the special effect now. The source's Crown is a specific defended continuation context.",
        "5. **Would it require an invented breaker modifier?** Yes, unless it remained mechanically inert.",
        "6. **Result:** **DEFER UNTIL CROWN CONTINUATION (S-C)**. Alber is historically audited but remains partially mechanically inert until that continuation is built. No price is assigned to a placeholder.", "",
        "### Mechanical decomposition", "",
        "| Item | Result | Classification |", "|---|---|---|",
        "| Before declaration | Opponent currently in Alber; actor has a normal longsword action | DIRECTLY SOURCE-ANCHORED |",
        "| Initial historical action | Spring in with a strong descending long-edge head cut | DIRECTLY SOURCE-ANCHORED |",
        "| Already Basic | Test, ordinary damage, defence menu, action cost, head-line fiction | ATRA STATE MAPPING |",
        "| Learned substance | Alber recognition plus the defended Crown/point-sinking/winding/pressing/slicing decision tree | DIRECTLY SOURCE-ANCHORED |",
        "| Existing distinct state | None without unsupported geometry or modifier | NOT JUSTIFIED |",
        "| Later effects | Crown reception, sinking point, winding, pressing, slicing | DIRECTLY SOURCE-ANCHORED |",
        "| Standalone learned card | Duplicates Basic Cut while consuming a Play slot | PROVISIONAL GAME ABSTRACTION; rejected for this prototype |", "",
        "## Tutta Porta di Ferro — Cover to Stretto", "",
        "1. **Exact trigger:** actor was in Tutta when declaring Basic Cross against an ordinary proactive Basic Cut; the normal pre-Parry Durchwechseln window resolves; Cross succeeds; Crossing exists at Wide measure; the chain has room and the actor can pay the candidate cost.",
        "2. **State transition:** `Crossing/Wide -> retained Crossing/Close`.",
        "3. **T0 vs T1:** identical except 0 versus 1 Spiritus at declaration.",
        "4. **Extra roll:** none.",
        "5. **Additional action:** none; the cover already spent the defender's action and it is not restored.",
        "6. **Learned Play:** yes; it consumes one of the three chain slots.",
        "7. **Retained Crossing:** justified as the minimal engine mapping of cover plus passing entry into stretto. It is a source-derived state mapping, not a claim about blade zone, pressure, damage, or control.",
        "8. **Preferred provisional candidate:** recommend T1 for Project review; this report does not promote it to the governing baseline.", "",
        "The v0.1 trigger excludes thrusts so it does not absorb Scambiar or downward Beat, and excludes Beat, Power Attack, learned cuts, and generic successful Parries. Pommel remains a separate downstream Play and is not implied historically by the Tutta passage.", "",
        "## Deterministic Validation", "",
        "All required cases pass: correct/wrong guard, success/failure, Cross/Beat, Durchwechseln interruption, T0/T1 spending, retained Wide-to-Close state, zero damage/extra attack/action restoration, learned-chain counting, cap rejection, downstream Pommel legality, ordinary cleanup, and modifier-free Scheitelhau deferral. The suite also asserts that no generic Cross is Crown and no automatic breaker benefit exists.", "",
        "## Behavioral Micro-Test", "",
        "| Cell | Tutta occ. | Cover opp. | Trigger Cross | Cont. opp. | Uses | Cont. S | Wide→Close | Retained C/C | Close exch./transition | Pommel opp./use | Learned / other | Chain cap | Fourth | Guard changes | Total S |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in results["cells"]:
        m = item["metrics"]
        cell = item["cell"]
        lines.append(
            f"| {cell['model']} S{cell['start_spiritus']} | {pct(m['tutta_occupancy'])} | "
            f"{fmt(m['source_compatible_cover_opportunities_per_fight'])} | {fmt(m['successful_triggering_crosses_per_fight'])} | "
            f"{fmt(m['continuation_opportunities_per_fight'])} | {fmt(m['continuation_uses_per_fight'])} | "
            f"{fmt(m['continuation_spiritus_per_fight'])} | {fmt(m['wide_to_close_transitions_per_fight'])} | "
            f"{fmt(m['retained_crossing_close_states_per_fight'])} | {fmt(m['close_duration_exchange_slots_per_transition'])} | "
            f"{fmt(m['downstream_pommel_opportunities_per_fight'])}/{fmt(m['downstream_pommel_uses_per_fight'])} | "
            f"{fmt(m['learned_plays_per_fight'])}/{fmt(m['other_learned_plays_per_fight'])} | "
            f"{pct(m['three_play_cap_frequency'])} | {fmt(m['attempted_fourth_plays_per_fight'])} | "
            f"{fmt(m['guard_changes_per_fight'])} | {fmt(m['total_spiritus_per_fight'])} |"
        )
    lines += ["", "### Aggregate comparison", "",
        "| Model | Uses/fight | Declaration rate | Spiritus | Wide→Close | Pommel opp./use | Other learned Plays | Guard changes | Total Spiritus |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for model in MODELS:
        m = aggregates[model]
        lines.append(
            f"| {model} | {fmt(m['continuation_uses_per_fight'])} | {pct(m['continuation_declaration_rate'])} | "
            f"{fmt(m['continuation_spiritus_per_fight'])} | {fmt(m['wide_to_close_transitions_per_fight'])} | "
            f"{fmt(m['downstream_pommel_opportunities_per_fight'])}/{fmt(m['downstream_pommel_uses_per_fight'])} | "
            f"{fmt(m['other_learned_plays_per_fight'])} | {fmt(m['guard_changes_per_fight'])} | {fmt(m['total_spiritus_per_fight'])} |"
        )
    lines += ["", "### Conditional trigger decision check", "",
        "The natural trigger is sparse because the inherited Skill-14 policy usually selects learned defence over Basic Cross. The following 1,000-trial cells isolate only the declaration decision after the exact Tutta/Cross/Wide trigger is already satisfied; they do not replace the mirrored-fight metrics.", "",
        "| Model | Start S | Triggered trials | Declaration rate | Spiritus/trigger | Spiritus/declaration |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in results["conditional_trigger_analysis"]:
        lines.append(
            f"| {item['model']} | {item['start_spiritus']} | {item['trials']} | "
            f"{pct(item['declaration_rate'])} | {fmt(item['spiritus_per_trigger'])} | "
            f"{fmt(item['spiritus_per_declaration'])} |"
        )
    lines += ["", "### Chain distribution", ""]
    for item in results["cells"]:
        dist = ", ".join(f"{key}: {pct(value)}" for key, value in item["metrics"]["chain_length_distribution"].items())
        lines.append(f"- {item['cell']['model']} S{item['cell']['start_spiritus']}: {dist}")
    lines += ["",
        ("**FREE-CLOSE WARNING:** T0 makes the authored conversion free and the policy declares it routinely when the narrow trigger appears. It should remain a comparison bound rather than the preferred provisional price." if warning else "T0 did not cross the predeclared FREE-CLOSE WARNING threshold in this bounded policy."), "",
        f"T0 changes other learned-Play use by {t0['other_learned_plays_per_fight'] - control['other_learned_plays_per_fight']:+.3f}/fight from control; T1 changes it by {t1['other_learned_plays_per_fight'] - control['other_learned_plays_per_fight']:+.3f}/fight. These are policy-substitution observations, not causal balance estimates. The natural T1 cells produced too few successful triggering Crosses to declare the continuation in this seed, so their observed continuation Spiritus is zero; deterministic validation and the conditional-trigger check still show exactly 1 Spiritus per T1 declaration and a lower declaration rate under scarcity.", "",
        "No cell records an unauthorized Close origin. CONTROL remains at zero Wide-to-Close transitions. Every Close state in T0/T1 descends from the authored Tutta continuation; subsequent Close-measure Crossings are consequences of already-entered measure, not a universal Step-to-Close action.", "",
        "## Limitations", "",
        "The one-step softmax policy values the authored Close opportunity with a transparent 0.25 base plus a small wounded-target term, then subtracts the existing reserve charge. It does not solve equilibrium play, model player preferences, or prove balance. Natural triggering Crosses are extremely sparse in this policy, so the conditional-trigger cells are a price-sensitivity diagnostic rather than a frequency forecast. Once entered, Close measure persists under the existing independent measure axis; contact still requires an authored Crossing and cleans or separates normally. The run is intentionally too small and narrow for guard win-rate conclusions.", "",
        "## Durable Technical Results", "",
        "Deterministic validation confirms the Project-authorized promotions: Tutta cover-to-stretto is a learned Play; no universal Close action exists; no automatic breaker modifier exists; and Crown remains distinct from generic Basic Cross. T0/T1 selection and the Scheitelhau future chassis remain unpromoted.", "",
        "## Recommended Next Decision", "",
        "A. **No.** Scheitelhau's initial Alber entry lacks enough independent substance to implement now.", "",
        "B. No chassis or price is recommended for the initial entry alone.", "",
        "C. **Run a narrow Crown-continuation experiment next.** It should specify the defended context without treating every Basic Cross as Crown.", "",
        "D. **Yes.** Tutta cover-to-stretto is cleanly implementable with the existing Crossing and Wide→Close state.", "",
        "E. **Prefer T1 for Project review; do not auto-promote it.** One Spiritus matches one meaningful state conversion and preserves reserve competition.", "",
        "F. **No second roll.** The successful cover is the test; the continuation is deliberate state conversion.", "",
        "G. **Yes.** It creates Close only through a named learned trigger and does not add a universal Close button.", "",
        "H. The bounded policy shows no pathological displacement of other learned Plays, but T0 creates a routine free conversion warning; T1 imposes a visible Spiritus decision.", "",
        "I. **Not yet ready for a meaningful Named Guard Rules v0.2 run.** The Italian bridge is ready, but Alber remains mechanically under-distinguished.", "",
        "J. The exact remaining blocker is a narrow, audited Crown continuation (or another independently justified Scheitelhau state effect) that gives the Alber breaker entry mechanical substance without a generic modifier.", "",
    ]
    return "\n".join(lines)


def validate_results(results: dict[str, Any]) -> None:
    assert len(results["cells"]) == 6
    for item in results["cells"]:
        m = item["metrics"]
        assert len(m["starting_guard_outcome_share"]) == 16
        assert m["precondition_violations"] == 0
        assert m["unauthorized_close_origins"] == 0
        if item["cell"]["model"] == "CONTROL":
            assert m["continuation_uses_per_fight"] == 0
            assert m["wide_to_close_transitions_per_fight"] == 0
            assert m["downstream_pommel_opportunities_per_fight"] == 0
        else:
            assert m["continuation_uses_per_fight"] == m["wide_to_close_transitions_per_fight"]
        if item["cell"]["model"] == "T0":
            assert m["continuation_spiritus_per_fight"] == 0
        if item["cell"]["model"] == "T1":
            assert abs(m["continuation_spiritus_per_fight"] - m["continuation_uses_per_fight"]) < 1e-12


def run_all(trials: int = TRIALS_PER_CELL, seed: int = SEED, write: bool = True) -> dict[str, Any]:
    if trials % 16:
        raise ValueError("trials must be divisible by 16 for balanced ordered starting guards")
    cases = deterministic_harness()
    validate_harness(cases)
    cell_results = [run_cell(cell, trials, seed + index * 1009) for index, cell in enumerate(cells())]
    aggregates = {model: aggregate(cell_results, model) for model in MODELS}
    conditional = conditional_trigger_analysis()
    t0_declaration_rate = aggregates["T0"]["continuation_declaration_rate"]
    t0_conditional_rate = sum(
        item["declaration_rate"] for item in conditional if item["model"] == "T0"
    ) / 2
    free_close_warning = t0_conditional_rate >= 0.70
    results = {
        "metadata": {
            "status": "PROVISIONAL bounded behavioral micro-test; not balance or canon",
            "seed": seed,
            "trials_per_cell": trials,
            "skill": 14,
            "starting_spiritus": [8, 3],
            "models": list(MODELS),
            "balanced_ordered_starting_guard_pairs": True,
            "governing_engine": "simulations/shared/provisional_longsword.py",
            "named_guard_harness_reused": "simulations/named_guard_rules_v0_1/simulate.py",
            "specification": str(SPEC_PATH.relative_to(ROOT)).replace("\\", "/"),
            "named_guard_v02_run": False,
        },
        "scheitelhau_vs_alber": {
            "classification": "S-C",
            "decision": "DEFER UNTIL CROWN CONTINUATION",
            "initial_entry_implemented": False,
            "spiritus_cost": None,
            "automatic_breaker_modifier": False,
            "generic_basic_cross_is_crown": False,
        },
        "tutta_cover_to_stretto": {
            "classification": "LEARNED CONTINUATION",
            "trigger": "Tutta + successful Basic Cross against ordinary proactive Basic Cut + Crossing/Wide after D1 window",
            "effect": "retain Crossing; Wide -> Close; no damage, attack, action restoration, grapple, disarm, control, or Pommel",
            "extra_roll": False,
            "additional_action": False,
            "counts_as_learned_play": True,
            "candidates": {"T0": 0, "T1": 1},
            "recommended_for_project_review": "T1",
            "automatically_promoted": False,
        },
        "deterministic_cases": cases,
        "cells": cell_results,
        "aggregates": aggregates,
        "conditional_trigger_analysis": conditional,
        "technical_conclusions": {
            "free_close_warning": free_close_warning,
            "t0_natural_declaration_rate": t0_declaration_rate,
            "t0_conditional_declaration_rate": t0_conditional_rate,
            "no_universal_close_action": True,
            "no_automatic_breaker_modifier": True,
            "crown_distinct_from_generic_basic_cross": True,
            "tutta_is_learned_play": True,
            "ready_for_named_guard_v02": False,
            "remaining_blocker": "narrow Crown continuation or another independently justified Scheitelhau state effect",
        },
    }
    validate_results(results)
    if write:
        RESULTS_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        REPORT_PATH.write_text(build_report(results) + "\n", encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=TRIALS_PER_CELL)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    results = run_all(args.trials, args.seed, write=not args.no_write)
    print(json.dumps({
        "trials_per_cell": results["metadata"]["trials_per_cell"],
        "aggregates": results["aggregates"],
        "technical_conclusions": results["technical_conclusions"],
    }, indent=2))


if __name__ == "__main__":
    main()

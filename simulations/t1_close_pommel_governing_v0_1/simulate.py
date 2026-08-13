"""Fixed-seed, one-exchange smoke audit for governing E1 T1 and P2 Pommel."""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulations.shared.provisional_longsword import CurrentEngine, ENGINE, Fighter, HART, WEICH  # noqa: E402


SEED = 1308202602
TRIALS = 1000
RESULTS_PATH = ROOT / "reports" / "t1-close-pommel-governing-integration-v01-results.json"
T1 = ENGINE.T1_PLAY
POMMEL = ENGINE.POMMEL_PLAY
DM = ENGINE.PAIRED_PLAY
FUHLEN = next(iter(ENGINE.FUHLEN_NAMES))
WINDEN = ENGINE.WINDEN_PLAY


@dataclass(frozen=True)
class Scenario:
    id: str
    name: str
    striker_plays: tuple[str, ...] = ()
    defender_plays: tuple[str, ...] = (T1,)
    defender_guard: str = ENGINE.TUTTA_GUARD
    defender_spiritus: int = 4
    defence: str = "Cross"
    decline_t1: bool = False


SCENARIOS = (
    Scenario("S1", "T1 versus Basics; neither knows Pommel"),
    Scenario("S2", "T1 plus defender Pommel versus Basics", defender_plays=(T1, POMMEL)),
    Scenario("S3", "T1 versus striker Pommel", striker_plays=(POMMEL,)),
    Scenario("S4", "T1 with both knowing Pommel", striker_plays=(POMMEL,), defender_plays=(T1, POMMEL)),
    Scenario("S5", "T1 versus D/M plus Fuhlen", striker_plays=(DM, FUHLEN)),
    Scenario("S6", "T1 plus Pommel versus Winden", striker_plays=(WINDEN,), defender_plays=(T1, POMMEL)),
    Scenario("S7", "low-Spiritus Tutta", defender_plays=(T1, POMMEL), defender_spiritus=1),
    Scenario("S8", "Beat control", defender_plays=(T1, POMMEL), defence="Beat"),
    Scenario("S9", "H3 control with T1 declined", striker_plays=(DM, FUHLEN), decline_t1=True),
    Scenario("S10", "non-Tutta H3 mirror", striker_plays=(DM,), defender_guard="posta-di-donna"),
)


def roll20(rng: random.Random, modifier: str = "normal") -> tuple[int, ...]:
    return tuple(rng.randint(1, 20) for _ in range(2 if modifier in {"boon", "bane"} else 1))


def run_scenario(scenario: Scenario, trials: int = TRIALS) -> dict[str, Any]:
    metrics: Counter[str] = Counter()
    seed = SEED + 100_003 * int(scenario.id[1:])
    rng = random.Random(seed)
    for _ in range(trials):
        a = Fighter("A", spiritus=4, known_plays=set(scenario.striker_plays))
        b = Fighter(
            "B",
            spiritus=scenario.defender_spiritus,
            guard=scenario.defender_guard,
            known_plays=set(scenario.defender_plays),
        )
        engine = CurrentEngine([a, b])
        attack = engine.declare_attack(a, b, "cut", descending=True)
        assert attack is not None
        rolled = engine.roll_pending_attack(roll20(rng), (rng.randint(1, 6),))
        if not rolled.success:
            metrics["attack_failures"] += 1
            engine.finish_exchange()
            continue
        pressure = HART if rng.random() < 0.5 else WEICH
        if scenario.defence == "Beat":
            result = engine.basic_defence("Beat", b, rolled.roll, roll20(rng))
        else:
            assert engine.declare_basic_cross(b, pressure, ENGINE.UPPER_CROSS)
            result = engine.basic_defence(
                "Cross",
                b,
                rolled.roll,
                roll20(rng, "boon" if pressure == HART else "normal"),
            )
        if not result.success:
            metrics["defence_failures"] += 1
            engine.resolve_pending_attack()
            engine.finish_exchange()
            continue
        if scenario.defence == "Beat":
            metrics["beat_successes"] += 1
            metrics["close_entries"] += int(engine.crossing.measure == "close")
            engine.finish_exchange()
            continue

        metrics["cross_successes"] += 1
        before_actions = (a.action_available, b.action_available)
        if engine.t1_window_actor == b.name:
            metrics["t1_opportunities"] += 1
            if scenario.decline_t1:
                assert engine.decline_t1(b)
                metrics["t1_declines"] += 1
            else:
                spiritus_before = b.spiritus
                assert engine.declare_t1(b)
                metrics["t1_declarations"] += 1
                metrics["spiritus_spent_t1"] += spiritus_before - b.spiritus
                metrics["close_entries"] += 1
                metrics["max_chain"] = max(metrics["max_chain"], len(engine.learned_chain))

        if engine.rejoinder_open:
            metrics["h3_rejoinders"] += 1
            if DM in a.known_plays and a.spiritus >= 2:
                if FUHLEN in a.known_plays and a.spiritus >= 3:
                    before = a.spiritus
                    if engine.buy_fuhlen(a) is not None:
                        metrics["fuhlen"] += 1
                        metrics["spiritus_spent_fuhlen"] += before - a.spiritus
                branch = "Mutieren" if pressure == WEICH else "Duplieren"
                before = a.spiritus
                declaration = engine.declare_bind_rejoinder(a, branch)
                if declaration.success:
                    metrics["dm"] += 1
                    metrics["spiritus_spent_dm"] += before - a.spiritus
                    engine.resolve_bind_rejoinder(roll20(rng, "boon"), (rng.randint(1, 6),))
            else:
                engine.decline_bind_rejoinder(a)

        for _pass in range(3):
            holder_name = engine.crossing.bind_initiative
            if engine.crossing.contact != "crossing" or holder_name is None:
                break
            holder = engine.fighters[holder_name]
            if engine.pommel_legal(holder):
                metrics["pommel_opportunities"] += 1
                before = holder.spiritus
                declaration = engine.declare_pommel(holder)
                if declaration.legal:
                    metrics["pommel_declarations"] += 1
                    metrics["spiritus_spent_pommel"] += before - holder.spiritus
                    metrics["max_chain"] = max(metrics["max_chain"], len(engine.learned_chain))
                    resolved = engine.resolve_pommel(roll20(rng), (rng.randint(1, 6),))
                    metrics["pommel_hits" if resolved.success else "pommel_misses"] += 1
                    continue
            if engine.pass_bind_initiative(holder):
                metrics["bind_passes"] += 1
                if engine.crossing.contact == "none":
                    metrics["pass_cleanup"] += 1
                    break

        metrics["action_accounting_failures"] += int((a.action_available, b.action_available) != before_actions)
        metrics["chain_cap_failures"] += int(len(engine.learned_chain) > ENGINE.LEARNED_PLAY_CAP)
        metrics["dead_actor_safety_failures"] += int(
            (not a.alive and engine.pommel_legal(a)) or (not b.alive and engine.pommel_legal(b))
        )
        metrics["point_threat_events"] += engine.point_threat_events
        engine.finish_exchange()
        metrics["stale_state_failures"] += int(bool(
            engine.pending_attack is not None
            or engine.pending_pommel is not None
            or engine.t1_window_actor is not None
            or engine.rejoinder_open
            or engine.learned_chain
        ))
    return {
        "scenario": asdict(scenario),
        "seed": seed,
        "trials": trials,
        "metrics": dict(sorted(metrics.items())),
    }


def build_results(trials: int = TRIALS) -> dict[str, Any]:
    scenarios = [run_scenario(scenario, trials) for scenario in SCENARIOS]
    return {
        "milestone": "ATRA T1 / CLOSE / POMMEL — GOVERNING INTEGRATION v0.1",
        "status": "GOVERNING PROVISIONAL; NOT CANONICAL",
        "seed": SEED,
        "trials_per_scenario": trials,
        "scenario_count": len(scenarios),
        "governing_decisions": {
            "t1_timing": "E1 after qualifying successful Cross/D1 timing and before H3 creation",
            "t1_cost": "1 Spiritus + one chain entry; no action/test",
            "t1_pressure_assignment": "Hart original striker; Weich Tutta defender",
            "pommel_variant": "P2",
            "pommel_cost": "2 Spiritus + one chain entry; no additional action",
            "pommel_resolution": "flat Longsword, normal d6+1; hit cleanup; miss retains Close and transfers opportunity",
            "global_chain_cap": 3,
            "new_generic_close_systems": [],
        },
        "artifact_sanity": {
            "loaded_cut_skill14_exact": 3.830555555556,
            "historical_prose_value": 4.394,
            "classification": "historical prose-only discrepancy; old report/JSON not rewritten",
            "point_threat_events": "instrumentation repaired in authoritative engine and integrated full-duel collector; mechanics unchanged",
        },
        "status_table": {
            "T1 E1": "GOVERNING PROVISIONAL",
            "Pommel P2": "GOVERNING PROVISIONAL",
            "T0/C0/L1/P1": "ARCHIVED OR REJECTED COMPARISON CONTROLS",
            "H3/Winden/D1/Beat/Open/cap": "PRESERVED GOVERNING PROVISIONAL",
            "generic Close modifier/Leverage/Close Initiative/grapple": "NOT IMPLEMENTED",
            "Named Guard v0.2": "NOT STARTED",
        },
        "scenarios": scenarios,
        "safety": {
            "action_accounting_failures": sum(row["metrics"].get("action_accounting_failures", 0) for row in scenarios),
            "chain_cap_failures": sum(row["metrics"].get("chain_cap_failures", 0) for row in scenarios),
            "dead_actor_safety_failures": sum(row["metrics"].get("dead_actor_safety_failures", 0) for row in scenarios),
            "stale_state_failures": sum(row["metrics"].get("stale_state_failures", 0) for row in scenarios),
        },
        "instrumentation": {
            "point_threat_events": sum(row["metrics"].get("point_threat_events", 0) for row in scenarios),
            "repair_scope": "counts runtime nonthreatening-to-threatening writes; mechanics unchanged",
        },
        "recommended_next_milestone": "A — vertical-slice stabilization and governing-packet synchronization; do not begin Named Guard v0.2 yet",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    results = build_results(args.trials)
    if args.output:
        args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

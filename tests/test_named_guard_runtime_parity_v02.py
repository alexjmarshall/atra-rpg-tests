from __future__ import annotations

import json
import unittest
from pathlib import Path

from simulations.shared.provisional_longsword import (
    CurrentEngine,
    Fighter,
    NAMED_GUARD_IDS,
)
from simulations.shared.provisional_longsword import ENGINE


ROOT = Path(__file__).resolve().parents[1]
THREATENING = {"ochs", "pflug", "mezza-porta-di-ferro"}


class NamedGuardRuntimeParityV02(unittest.TestCase):
    def test_01_roster_allowlist_matches_governing_guard_data(self) -> None:
        data = json.loads(
            (ROOT / "data" / "guards" / "longsword-named-v0.1.yaml").read_text(
                encoding="utf-8"
            )
        )
        data_ids = tuple(guard["id"] for guard in data["guards"])
        self.assertEqual(len(data_ids), 8)
        self.assertEqual(data_ids, NAMED_GUARD_IDS)
        self.assertEqual(ENGINE.NAMED_GUARDS, NAMED_GUARD_IDS)

    def test_02_starting_guard_intrinsics_match_governing_state(self) -> None:
        for guard in NAMED_GUARD_IDS:
            with self.subTest(guard=guard):
                actor = Fighter("A", guard=guard)
                self.assertEqual(
                    actor.point_threat,
                    "threatening" if guard in THREATENING else "not_threatening",
                )
                self.assertEqual(actor.loaded, guard == "posta-di-donna")

        with self.assertRaises(ValueError):
            Fighter("A", guard="ninth-invented-guard")

    def test_03_gc1_rejects_unknown_guards_without_mutation_or_cost(self) -> None:
        actor = Fighter("A", guard="vom-tag", spiritus=5)
        opponent = Fighter("B")
        engine = CurrentEngine([actor, opponent])
        engine.begin_activation(actor)
        before = (
            actor.guard,
            actor.point_threat,
            actor.guard_change_available,
            actor.action_available,
            actor.spiritus,
            tuple(engine.learned_chain),
            engine.point_threat_events,
        )
        self.assertFalse(engine.change_guard(actor, "ninth-invented-guard"))
        after = (
            actor.guard,
            actor.point_threat,
            actor.guard_change_available,
            actor.action_available,
            actor.spiritus,
            tuple(engine.learned_chain),
            engine.point_threat_events,
        )
        self.assertEqual(before, after)

    def test_04_gc1_named_entry_writes_same_intrinsic_as_starting_guard(self) -> None:
        for guard in NAMED_GUARD_IDS:
            with self.subTest(guard=guard):
                actor = Fighter("A", guard="vom-tag")
                opponent = Fighter("B")
                engine = CurrentEngine([actor, opponent])
                engine.begin_activation(actor)
                self.assertTrue(engine.change_guard(actor, guard))
                self.assertEqual(
                    actor.point_threat,
                    "threatening" if guard in THREATENING else "not_threatening",
                )
                self.assertEqual(actor.loaded, guard == "posta-di-donna")

                # Initial intrinsic state is not an authored transition event;
                # entering a threatening guard through GC1 is.
                expected_events = 1 if guard in THREATENING else 0
                self.assertEqual(engine.point_threat_events, expected_events)


if __name__ == "__main__":
    unittest.main()

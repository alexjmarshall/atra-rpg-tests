from __future__ import annotations

import unittest

from simulations.integrated_full_duel_melee_v0_1.simulate import (
    DM,
    FUHLEN,
    POLICIES,
    WINDEN,
    FighterView,
    IntegratedDuel,
    PolicyView,
    SCENARIOS,
    exact_local_analysis,
    make_policy_view,
    response_traces,
)
from simulations.shared.provisional_longsword import (
    ENGINE,
    CurrentEngine,
    Fighter,
    HART,
    UNKNOWN,
    UPPER,
    WEICH,
)


def successful_cross(
    pressure: str = HART,
    geometry: str = ENGINE.UPPER_CROSS,
    plays_a: set[str] | None = None,
    plays_b: set[str] | None = None,
    spiritus_a: int = 8,
    spiritus_b: int = 8,
) -> tuple[CurrentEngine, Fighter, Fighter]:
    a = Fighter("A", spiritus=spiritus_a, known_plays=plays_a or set())
    b = Fighter("B", spiritus=spiritus_b, known_plays=plays_b or set())
    engine = CurrentEngine([a, b])
    kind = "low-line-thrust" if geometry == ENGINE.LOWER_SETTING_ASIDE else "cut"
    attack = engine.declare_attack(a, b, kind, descending=(kind == "cut"))
    assert attack is not None
    rolled = engine.roll_pending_attack((1,), (3,))
    assert rolled.success and rolled.roll is not None
    assert engine.declare_basic_cross(b, pressure, geometry)
    defence_rolls = (1, 20) if pressure == HART else (1,)
    assert engine.basic_defence("Cross", b, rolled.roll, defence_rolls).success
    return engine, a, b


class IntegratedFullDuelCleanupTests(unittest.TestCase):
    def test_01_04_pressure_visibility_and_fuhlen_scope(self) -> None:
        engine, a, b = successful_cross(HART, plays_a={FUHLEN, DM})
        public = engine.public_crossing_state()
        self.assertNotIn("initial_pressure", public)
        self.assertEqual(engine.pressure_view(a, b), UNKNOWN)
        self.assertEqual(engine.pressure_view(b, b), HART)
        self.assertEqual(engine.buy_fuhlen(a), HART)
        self.assertEqual(engine.pressure_view(a, b), HART)
        self.assertEqual(engine.pressure_view(b, a), UNKNOWN)
        engine.decline_bind_rejoinder(a)
        self.assertEqual(engine.pressure_view(a, b), UNKNOWN)
        self.assertTrue(all(value == UNKNOWN for value in engine.crossing.initial_pressure.values()))

    def test_05_policy_view_has_no_engine_or_raw_hidden_fields(self) -> None:
        engine, a, b = successful_cross(WEICH, plays_a={FUHLEN, DM})
        view = make_policy_view(engine, a, ("Fuhlen", "Duplieren", "Mutieren", "decline"), ())
        self.assertIsInstance(view, PolicyView)
        self.assertEqual(view.known_opponent_pressure, UNKNOWN)
        self.assertEqual(view.own_initial_pressure, UNKNOWN)
        self.assertNotIn("engine", PolicyView.__dataclass_fields__)
        self.assertNotIn("roll", PolicyView.__dataclass_fields__)
        self.assertNotIn("initial_pressure", dict(view.crossing))
        self.assertEqual(POLICIES["adaptive"].rejoinder(view), "Fuhlen")
        blind_options = ("Duplieren", "Mutieren", "decline")
        revealed = make_policy_view(engine, a, blind_options, ("pressure-revealed:weich",))
        self.assertEqual(POLICIES["adaptive"].rejoinder(revealed), "Mutieren")

    def test_06_09_dm_cleanup_two_passes_and_disengage(self) -> None:
        engine, a, _ = successful_cross(HART, plays_a={DM})
        self.assertTrue(engine.declare_bind_rejoinder(a, "Duplieren").success)
        self.assertTrue(engine.resolve_bind_rejoinder((1, 20), (3,)).success)
        self.assertEqual(engine.crossing.contact, "none")
        self.assertEqual(engine.crossing.bind_height, UNKNOWN)
        self.assertFalse(engine.rejoinder_open)

        engine, a, b = successful_cross(HART)
        self.assertTrue(engine.decline_bind_rejoinder(a))
        self.assertTrue(engine.pass_bind_initiative(a))
        self.assertTrue(engine.pass_bind_initiative(b))
        self.assertEqual(engine.crossing.contact, "none")

        engine, a, _ = successful_cross(HART)
        self.assertTrue(engine.decline_bind_rejoinder(a))
        self.assertTrue(engine.disengage(a))
        self.assertEqual(engine.crossing.contact, "none")

    def test_10_13_winding_hit_lower_miss_cap_and_exchange_reset(self) -> None:
        engine, a, b = successful_cross(WEICH, ENGINE.LOWER_SETTING_ASIDE, plays_a={WINDEN}, plays_b={WINDEN})
        engine.decline_bind_rejoinder(a)
        self.assertTrue(engine.declare_lower_winding(b).legal)
        self.assertFalse(engine.resolve_lower_winding((20,), (3,)).success)
        self.assertEqual(engine.crossing.bind_height, UPPER)
        self.assertEqual(b.guard, "ochs")
        self.assertEqual(engine.crossing.bind_initiative, "A")
        self.assertTrue(engine.declare_upper_winding(a).legal)
        self.assertTrue(engine.resolve_upper_winding((1,), (3,)).success)
        self.assertEqual(engine.crossing.contact, "none")

        engine, a, b = successful_cross(HART, plays_a={WINDEN}, plays_b={WINDEN})
        engine.decline_bind_rejoinder(a)
        for actor in (a, b, a):
            self.assertTrue(engine.declare_upper_winding(actor).legal)
            self.assertFalse(engine.resolve_upper_winding((20,), (3,)).success)
        self.assertEqual(len(engine.learned_chain), 3)
        self.assertFalse(engine.declare_upper_winding(b).legal)
        engine.finish_exchange()
        self.assertEqual(len(engine.learned_chain), 0)

    def test_14_dead_fighters_spiritus_and_opportunity_are_guarded(self) -> None:
        dead = Fighter("A", hp=0, action_available=True, spiritus=8, known_plays={WINDEN, DM})
        living = Fighter("B")
        engine = CurrentEngine([dead, living])
        self.assertIsNone(engine.declare_attack(dead, living, "cut"))
        self.assertIsNone(engine.declare_attack(living, dead, "cut"))
        self.assertTrue(living.action_available)
        self.assertFalse(engine.spend_spiritus(dead, 1))
        self.assertFalse(engine.spend_spiritus(living, -1))
        self.assertEqual(engine.continuation_options(dead, winden_variant="W2"), [])
        self.assertGreaterEqual(living.spiritus, 0)

    def test_15_open_and_guard_change_lifecycle(self) -> None:
        a = Fighter("A", guard="posta-di-donna")
        b = Fighter("B")
        engine = CurrentEngine([a, b])
        attack = engine.declare_attack(a, b, "cut")
        assert attack is not None
        rolled = engine.roll_pending_attack((1,), (3,))
        assert rolled.roll is not None
        self.assertTrue(engine.basic_defence("Beat", b, rolled.roll, (1,)).success)
        self.assertEqual(a.guard, "open")
        engine.begin_activation(a)
        self.assertTrue(engine.recover_open(a, "vom-tag"))
        self.assertFalse(engine.change_guard(a, "ochs"))

    def test_16_loaded_committed_and_d1_resolution(self) -> None:
        a = Fighter("A", guard="posta-di-donna")
        b = Fighter("B")
        engine = CurrentEngine([a, b])
        attack = engine.declare_attack(a, b, "cut")
        self.assertIsNotNone(attack)
        self.assertEqual(attack.damage_mode, "damage_boon")
        result = engine.roll_pending_attack((1,), (1, 6))
        self.assertEqual(result.damage, 7)

        a = Fighter("A", known_plays={"Durchwechseln"})
        b = Fighter("B")
        engine = CurrentEngine([a, b])
        attack = engine.declare_attack(a, b, "cut")
        assert attack is not None
        first = engine.roll_pending_attack((1,), (3,))
        self.assertTrue(engine.declare_durchwechseln(a, b, attack))
        second = engine.roll_pending_attack((1,), (3,))
        self.assertTrue(second.legal)
        self.assertEqual(attack.kind, "durchwechseln-thrust")

    def test_17_zornhau_and_ordinary_state_never_contaminate(self) -> None:
        a = Fighter("A")
        b = Fighter("B", known_plays={"Zornhau-Ort", FUHLEN})
        engine = CurrentEngine([a, b])
        attack = engine.declare_attack(a, b, "cut", descending=True)
        assert attack is not None
        rolled = engine.roll_pending_attack((10,), (3,))
        assert rolled.roll is not None
        self.assertTrue(engine.zornhau(b, rolled.roll, (5,)).success)
        self.assertEqual(engine.crossing.source, "zornhau-local")
        self.assertIn("favored", engine.crossing.bind_position.values())
        engine._end_bind_sequence()
        b.action_available = True
        a.action_available = True
        attack = engine.declare_attack(a, b, "cut", descending=True)
        assert attack is not None
        rolled = engine.roll_pending_attack((1,), (3,))
        assert rolled.roll is not None
        engine.declare_basic_cross(b, HART, ENGINE.UPPER_CROSS)
        engine.basic_defence("Cross", b, rolled.roll, (1, 20))
        self.assertEqual(engine.crossing.source, "ordinary-basic-cross")
        self.assertTrue(all(value == UNKNOWN for value in engine.crossing.bind_position.values()))

    def test_18_exchange_cleanup_preserves_measure_and_only_authored_retention(self) -> None:
        engine, a, b = successful_cross(HART)
        engine.crossing.measure = "close"
        engine.finish_exchange()
        self.assertEqual(engine.crossing.contact, "none")
        self.assertEqual(engine.crossing.measure, "close")
        self.assertIsNone(engine.crossing.bind_initiative)
        self.assertFalse(engine.rejoinder_open)

        engine, _, _ = successful_cross(HART)
        engine.crossing.retained = True
        engine.finish_exchange()
        self.assertEqual(engine.crossing.contact, "crossing")
        self.assertFalse(engine.crossing.retained)
        self.assertIsNone(engine.crossing.bind_initiative)
        engine.finish_exchange()
        self.assertEqual(engine.crossing.contact, "none")

    def test_19_t1_h3_ordering_is_exposed_not_silently_resolved(self) -> None:
        engine, a, b = successful_cross(HART, plays_b={"Tutta Cover-to-Stretto"}, spiritus_b=1)
        b.guard = "tutta-porta-di-ferro"
        self.assertTrue(engine.rejoinder_open)
        self.assertTrue(engine.tutta_cover_to_stretto(b))
        self.assertEqual(engine.crossing.measure, "close")
        self.assertTrue(engine.rejoinder_open)
        self.assertEqual(engine.rejoinder_options(a), ["decline"])

    def test_20_exact_matrix_scenarios_and_traces_are_complete(self) -> None:
        exact = exact_local_analysis()
        self.assertEqual(len(exact["basic_attack_cells"]), 16)
        self.assertEqual(len(exact["cross_beat"]), 4)
        self.assertEqual(len(exact["fuhlen_priors"]), 20)
        self.assertEqual({scenario.id for scenario in SCENARIOS}, {f"D{i}" for i in range(1, 16)})
        self.assertEqual(len(response_traces()), 6)


if __name__ == "__main__":
    unittest.main()

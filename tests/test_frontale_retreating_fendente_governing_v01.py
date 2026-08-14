from __future__ import annotations

import unittest

from simulations.shared.provisional_longsword import CurrentEngine, ENGINE, Fighter


PLAY = ENGINE.FRONTALE_FENDENTE_PLAY
FRONTALE = ENGINE.FRONTALE_GUARD


def live_thrust(*, guard: str = FRONTALE, spiritus: int = 8, plays: set[str] | None = None, skill: int = 14):
    attacker = Fighter("A", skill=skill)
    defender = Fighter(
        "B",
        skill=skill,
        spiritus=spiritus,
        guard=guard,
        known_plays={PLAY} if plays is None else set(plays),
    )
    engine = CurrentEngine([attacker, defender])
    attack = engine.declare_attack(attacker, defender, "thrust")
    assert attack is not None
    rolled = engine.roll_pending_attack((1,), (3,))
    assert rolled.success
    return engine, attacker, defender, attack


class FrontaleRetreatingFendenteGoverningV01(unittest.TestCase):
    def test_01_success_contract(self) -> None:
        engine, attacker, defender, attack = live_thrust()
        before = (defender.action_available, defender.spiritus, len(engine.learned_chain), attacker.hp)
        result = engine.frontale_retreating_fendente(defender, (1,), (3,))
        after = (defender.action_available, defender.spiritus, len(engine.learned_chain), attacker.hp)

        self.assertTrue(result.legal)
        self.assertTrue(result.success)
        self.assertEqual(result.damage, 4)
        self.assertEqual(before[0], True)
        self.assertEqual(after[0], False)
        self.assertEqual(before[1] - after[1], 2)
        self.assertEqual(after[2] - before[2], 1)
        self.assertEqual(engine.learned_chain, [PLAY])
        self.assertTrue(attack.cancelled)
        self.assertEqual(attack.phase, "cancelled")
        self.assertEqual(before[3] - after[3], 4)
        self.assertEqual(result.roll.modifier, "normal")
        self.assertEqual(engine.crossing.contact, "none")
        self.assertEqual(engine.crossing.measure, "wide")
        self.assertEqual(defender.guard, FRONTALE)
        self.assertEqual(defender.point_threat, "not_threatening")
        self.assertNotEqual(attacker.guard, ENGINE.OPEN)
        self.assertIsNone(engine.t1_window_actor)
        self.assertFalse(engine.rejoinder_open)
        self.assertTrue(any("CANCEL+ATTACK" in event for event in engine.event_log))

    def test_02_failure_spends_and_leaves_thrust_live(self) -> None:
        engine, attacker, defender, attack = live_thrust()
        result = engine.frontale_retreating_fendente(defender, (20,), (6,))

        self.assertTrue(result.legal)
        self.assertFalse(result.success)
        self.assertEqual(result.damage, 0)
        self.assertFalse(defender.action_available)
        self.assertEqual(defender.spiritus, 6)
        self.assertEqual(engine.learned_chain, [PLAY])
        self.assertFalse(attack.cancelled)
        self.assertEqual(attack.phase, "rolled")
        self.assertEqual(attacker.hp, 8)
        self.assertEqual(engine.crossing.contact, "none")
        self.assertEqual(defender.guard, FRONTALE)
        self.assertEqual(defender.point_threat, "not_threatening")

        defender_hp = defender.hp
        resolved = engine.resolve_pending_attack()
        self.assertTrue(resolved.legal)
        self.assertTrue(resolved.success)
        self.assertEqual(defender.hp, defender_hp - 4)

    def test_03_gates_and_no_partial_charge(self) -> None:
        cases = []

        engine, _, defender, _ = live_thrust(guard="tutta-porta-di-ferro")
        cases.append(("frontale", engine, defender))

        engine, _, defender, _ = live_thrust(plays=set())
        cases.append(("learned", engine, defender))

        engine, _, defender, _ = live_thrust(spiritus=1)
        cases.append(("spiritus", engine, defender))

        engine, _, defender, _ = live_thrust()
        engine.learned_chain[:] = ["x", "y", "z"]
        cases.append(("chain", engine, defender))

        for label, engine, defender in cases:
            with self.subTest(label=label):
                before = (defender.action_available, defender.spiritus, tuple(engine.learned_chain))
                result = engine.frontale_retreating_fendente(defender, (1,), (3,))
                after = (defender.action_available, defender.spiritus, tuple(engine.learned_chain))
                self.assertFalse(result.legal)
                self.assertEqual(before, after)

        attacker = Fighter("A")
        defender = Fighter("B", guard=FRONTALE, known_plays={PLAY})
        engine = CurrentEngine([attacker, defender])
        attack = engine.declare_attack(attacker, defender, "cut", descending=True)
        self.assertIsNotNone(attack)
        engine.roll_pending_attack((1,), (3,))
        before = (defender.action_available, defender.spiritus, tuple(engine.learned_chain))
        self.assertFalse(engine.frontale_retreating_fendente(defender, (1,), (3,)).legal)
        self.assertEqual(before, (defender.action_available, defender.spiritus, tuple(engine.learned_chain)))

    def test_04_precontact_and_protected_architecture(self) -> None:
        engine, _, defender, _ = live_thrust()
        engine.crossing.contact = "crossing"
        before = (defender.action_available, defender.spiritus, tuple(engine.learned_chain))
        self.assertFalse(engine.frontale_retreating_fendente(defender, (1,), (3,)).legal)
        self.assertEqual(before, (defender.action_available, defender.spiritus, tuple(engine.learned_chain)))

        # The governing method does not create a new named guard, point threat,
        # Open, bind height, Close, or a free continuation.
        engine, _, defender, _ = live_thrust()
        self.assertTrue(engine.frontale_retreating_fendente(defender, (1,), (3,)).success)
        self.assertEqual(defender.guard, FRONTALE)
        self.assertEqual(defender.point_threat, "not_threatening")
        self.assertEqual(engine.crossing.contact, "none")
        self.assertEqual(engine.crossing.measure, "wide")
        self.assertEqual(engine.crossing.bind_height, ENGINE.UNKNOWN)
        self.assertFalse(engine.rejoinder_open)
        self.assertIsNone(engine.t1_window_actor)
        self.assertEqual(len(engine.learned_chain), 1)


if __name__ == "__main__":
    unittest.main()

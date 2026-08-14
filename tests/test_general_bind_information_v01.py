from __future__ import annotations

import json
import unittest
from pathlib import Path

from simulations.general_bind_information_v0_1.candidate_engine import (
    COUNTER_WIND,
    HART,
    PAIRED_PLAY,
    UNKNOWN,
    WEICH,
    GeneralBindCandidateEngine,
    make_successful_h1_cross,
)
from simulations.shared.provisional_longsword_engine import (
    Attack,
    Crossing,
    Fighter,
    ProvisionalLongswordEngine,
)


ROOT = Path(__file__).resolve().parents[1]


def setup_cross(*, pressure=HART, a_plays=(), b_plays=(), skill=14):
    return make_successful_h1_cross(
        pressure=pressure, attacker_plays=a_plays, defender_plays=b_plays, skill=skill
    )


class GeneralBindInformationTests(unittest.TestCase):
    def test_artifact_shapes_and_nonpromotion_labels(self):
        prototype = json.loads(
            (ROOT / "data/prototypes/general-bind-information-architecture-v0.1.yaml").read_text(encoding="utf-8")
        )
        results = json.loads(
            (ROOT / "reports/general-bind-information-architecture-v01-results.json").read_text(encoding="utf-8")
        )
        report = (ROOT / "reports/general-bind-information-architecture-v01-results.md").read_text(encoding="utf-8")
        self.assertFalse(prototype["automatic_promotion"])
        self.assertFalse(prototype["authoritative_engine_edited"])
        self.assertEqual(len(prototype["candidate_records"]), 4)
        self.assertEqual(len(results["pressure_read_matrix"]), 40)
        self.assertEqual(len(results["fuhlen_price_sensitivity"]), 24)
        self.assertEqual(results["defender_pressure_mixing"]["classification"], "DEFENDER PRESSURE MIXING NOT YET EVALUABLE")
        for heading in (
            "## R0 vs H1 Architecture Comparison",
            "## Required Project Decision Table",
            "## Final Project-Review Questions",
        ):
            self.assertIn(heading, report)

    def test_01_03_baseline_preservation(self):
        # 1: the prior suite's stored result is 81/81.
        prior = json.loads((ROOT / "reports/melee-repertoire-integrity-repair-v01-results.json").read_text(encoding="utf-8"))
        self.assertEqual(prior["deterministic"]["passed"], 81)
        self.assertEqual(prior["deterministic"]["required_assertions"], 81)
        # 2: the current governing Cross supersedes R0 while this isolated H1
        # experiment remains reproducible below.
        a, b = Fighter("A"), Fighter("B")
        control = ProvisionalLongswordEngine([a, b])
        attack = control.declare_attack(a, b, "cut")
        self.assertIsNotNone(attack)
        rolled = control.roll_pending_attack((7,))
        b.action_available = True
        self.assertTrue(control.declare_basic_cross(b, HART))
        crossed = control.basic_defence("Cross", b, rolled.roll, (5,))
        self.assertTrue(crossed.success)
        self.assertEqual(set(control.crossing.bind_position.values()), {UNKNOWN})
        self.assertEqual(control.crossing.initial_pressure[b.name], HART)
        # 3: the old H1 candidate record remains historical, not governing.
        governing = (ROOT / "data/prototypes/longsword-governing-provisional-v0.1.yaml").read_text(encoding="utf-8")
        self.assertNotIn("general-bind-information-architecture-v0.1", governing)

    def test_04_12_hart_weich_declaration(self):
        a, b = Fighter("A"), Fighter("B")
        engine = GeneralBindCandidateEngine([a, b])
        attack = engine.declare_attack(a, b, "cut")
        rolled = engine.roll_pending_attack((5,))
        # 4-5: declaration is before Cross roll and hidden from striker.
        self.assertTrue(engine.declare_h1_cross(b, HART))
        self.assertIn("declare-hidden-pressure", engine.event_log[-1])
        self.assertEqual(engine.pressure_view(a, b), UNKNOWN)
        # 6: failed Cross persists no pressure bind.
        failed = engine.resolve_h1_cross(b, (19, 20))
        self.assertFalse(failed.success)
        self.assertEqual(engine.crossing.contact, "none")
        self.assertEqual(engine.crossing.pressure, {})

        # 7-10: successful state and exact modifiers.
        hart, _, hb = setup_cross(pressure=HART)
        self.assertEqual(hart.crossing.pressure[hb.name], HART)
        self.assertEqual(hart.event_log[-2], "H1:Cross-roll:boon")
        weich, _, wb = setup_cross(pressure=WEICH)
        self.assertEqual(weich.crossing.pressure[wb.name], WEICH)
        self.assertEqual(weich.event_log[-2], "H1:Cross-roll:normal")
        # 11-12: no Leverage and no generic bind modifier.
        self.assertFalse(hasattr(hart.crossing, "leverage"))
        self.assertFalse(hasattr(hart.crossing, "attack_modifier"))

    def test_13_22_bind_rejoinder_and_initiative(self):
        engine, a, b = setup_cross(pressure=HART, a_plays={PAIRED_PLAY})
        # 13-17: narrow authored window and legality.
        self.assertTrue(engine.rejoinder_open)
        self.assertEqual(engine.rejoinder_actor, a.name)
        self.assertEqual(engine.rejoinder_options(a), ["Duplieren", "Mutieren"])
        self.assertIn("Duplieren", engine.rejoinder_options(a))
        self.assertIn("Mutieren", engine.rejoinder_options(a))
        self.assertNotIn("Nachreisen", engine.rejoinder_options(a))
        # 18: no second normal action appears.
        self.assertFalse(a.action_available)
        declared = engine.declare_bind_rejoinder(a, "Duplieren", "G")
        self.assertTrue(declared.legal)
        self.assertFalse(a.action_available)

        # 19: decline closes window.
        hart, ha, _ = setup_cross(pressure=HART)
        self.assertTrue(hart.decline_bind_rejoinder(ha))
        self.assertFalse(hart.rejoinder_open)
        # 20-22: initiative mapping, no numeric modifier.
        self.assertEqual(hart.crossing.bind_initiative, ha.name)
        weich, wa, wb = setup_cross(pressure=WEICH)
        self.assertTrue(weich.decline_bind_rejoinder(wa))
        self.assertEqual(weich.crossing.bind_initiative, wb.name)
        self.assertFalse(hasattr(weich.crossing, "initiative_modifier"))

    def test_23_30_paid_fuhlen(self):
        engine, a, b = setup_cross(pressure=HART, a_plays={"Fühlen"})
        before = (a.action_available, a.spiritus, len(engine.learned_chain))
        reveal = engine.buy_fuhlen(a)
        # 23-28: cost, no action/chain, once, and category reveals.
        self.assertEqual(a.spiritus, before[1] - 1)
        self.assertEqual(a.action_available, before[0])
        self.assertEqual(len(engine.learned_chain), before[2])
        self.assertEqual(reveal, "hart")
        self.assertEqual(engine.pressure_view(a, b), HART)
        self.assertIsNone(engine.buy_fuhlen(a))

        weich, wa, _ = setup_cross(pressure=WEICH, a_plays={"Fühlen"})
        self.assertEqual(weich.buy_fuhlen(wa), "weich")
        # 29: unauthored pressure reveals Unknown.
        unknown, ua, ub = setup_cross(pressure=HART, a_plays={"Fühlen"})
        unknown.crossing.pressure[ub.name] = UNKNOWN
        self.assertEqual(unknown.buy_fuhlen(ua), "Unknown")
        # 30: second purchase remains impossible in same bind after other activity.
        self.assertIsNone(unknown.buy_fuhlen(ua))

    def test_31_42_duplieren(self):
        # 31: Wide required.
        engine, a, _ = setup_cross(pressure=HART, a_plays={PAIRED_PLAY})
        engine.crossing.measure = "close"
        self.assertEqual(engine.rejoinder_options(a), [])
        # 32-39: price, chain, form, damage, G and F mappings.
        engine, a, b = setup_cross(pressure=HART, a_plays={PAIRED_PLAY})
        before_s = a.spiritus
        self.assertTrue(engine.declare_bind_rejoinder(a, "Duplieren", "G").legal)
        self.assertEqual(a.spiritus, before_s - 2)
        self.assertEqual(len(engine.learned_chain), 1)
        pending = engine.pending_bind_attack
        self.assertEqual((pending.height, pending.kind), ("high", "cut"))
        self.assertEqual(pending.accuracy, "boon")
        resolved = engine.resolve_bind_rejoinder((5, 18), (4,))
        self.assertEqual(resolved.damage, 5)

        wrong, wa, _ = setup_cross(pressure=WEICH, a_plays={PAIRED_PLAY})
        wrong.declare_bind_rejoinder(wa, "Duplieren", "G")
        self.assertEqual(wrong.pending_bind_attack.accuracy, "bane")
        hard, ha, _ = setup_cross(pressure=HART, a_plays={PAIRED_PLAY})
        hard.declare_bind_rejoinder(ha, "Duplieren", "F")
        self.assertEqual(hard.pending_bind_attack.accuracy, "boon")
        fail, fa, _ = setup_cross(pressure=WEICH, a_plays={PAIRED_PLAY})
        before = fa.spiritus
        result = fail.declare_bind_rejoinder(fa, "Duplieren", "F")
        self.assertTrue(result.legal and not result.success)
        self.assertEqual(fa.spiritus, before - 2)
        self.assertIsNone(fail.pending_bind_attack)
        # 40-42: no chip, retention, or response restriction.
        missed, ma, mb = setup_cross(pressure=HART, a_plays={PAIRED_PLAY})
        missed.declare_bind_rejoinder(ma, "Duplieren", "G")
        hp = mb.hp
        result = missed.resolve_bind_rejoinder((19, 20), (6,))
        self.assertEqual((result.damage, mb.hp), (0, hp))
        self.assertEqual(missed.crossing.contact, "none")
        self.assertFalse(hasattr(missed.pending_attack, "restrict_response"))

    def test_43_56_mutieren(self):
        # 43: Wide required.
        engine, a, _ = setup_cross(pressure=WEICH, a_plays={PAIRED_PLAY})
        engine.crossing.measure = "close"
        self.assertEqual(engine.rejoinder_options(a), [])
        # 44-51: price/chain/form/normal damage and model mappings.
        engine, a, b = setup_cross(pressure=WEICH, a_plays={PAIRED_PLAY})
        before = a.spiritus
        engine.declare_bind_rejoinder(a, "Mutieren", "G")
        self.assertEqual(a.spiritus, before - 2)
        self.assertEqual(len(engine.learned_chain), 1)
        pending = engine.pending_bind_attack
        self.assertEqual((pending.height, pending.kind), ("low", "thrust"))
        self.assertEqual(pending.accuracy, "boon")
        result = engine.resolve_bind_rejoinder((4, 17), (5,))
        self.assertEqual(result.damage, 6)

        wrong, wa, _ = setup_cross(pressure=HART, a_plays={PAIRED_PLAY})
        wrong.declare_bind_rejoinder(wa, "Mutieren", "G")
        self.assertEqual(wrong.pending_bind_attack.accuracy, "bane")
        soft, sa, _ = setup_cross(pressure=WEICH, a_plays={PAIRED_PLAY})
        soft.declare_bind_rejoinder(sa, "Mutieren", "F")
        self.assertEqual(soft.pending_bind_attack.accuracy, "boon")
        fail, fa, _ = setup_cross(pressure=HART, a_plays={PAIRED_PLAY})
        before = fa.spiritus
        result = fail.declare_bind_rejoinder(fa, "Mutieren", "F")
        self.assertTrue(result.legal and not result.success)
        self.assertEqual(fa.spiritus, before - 2)
        # 52-56: winding transition, point, cleanup, no damage boon/denial.
        transition, ta, _ = setup_cross(pressure=WEICH, a_plays={PAIRED_PLAY})
        transition.declare_bind_rejoinder(ta, "Mutieren", "G")
        self.assertTrue(transition.crossing.retained)
        self.assertEqual(ta.point_threat, "threatening")
        self.assertNotIn("damage_boon", transition.pending_bind_attack.__dict__.values())
        transition.resolve_bind_rejoinder((4, 18), (3,))
        self.assertEqual(transition.crossing.contact, "none")
        self.assertFalse(hasattr(transition, "response_denied"))

    def test_57_67_counter_wind(self):
        engine, a, b = setup_cross(
            pressure=HART, a_plays={PAIRED_PLAY}, b_plays={COUNTER_WIND}
        )
        # 57: scoped only after eligible Duplieren.
        self.assertFalse(engine.counter_wind(b, (3,)).legal)
        engine.declare_bind_rejoinder(a, "Duplieren", "G")
        before = b.spiritus
        result = engine.counter_wind(b, (4,))
        # 58-64: cost, chain, normal test, cancel, retain, initiative, no damage.
        self.assertEqual(b.spiritus, before - 1)
        self.assertEqual(engine.learned_chain[-1], COUNTER_WIND)
        self.assertEqual(result.roll.modifier, "normal")
        self.assertIsNone(engine.pending_bind_attack)
        self.assertEqual(engine.crossing.contact, "crossing")
        self.assertEqual(engine.crossing.bind_initiative, b.name)
        self.assertEqual(result.damage, 0)
        # 65: failure adds no artificial Boon.
        failed, fa, fb = setup_cross(
            pressure=WEICH, a_plays={PAIRED_PLAY}, b_plays={COUNTER_WIND}
        )
        failed.declare_bind_rejoinder(fa, "Duplieren", "G")
        before_modifier = failed.pending_bind_attack.accuracy
        failure = failed.counter_wind(fb, (20,))
        self.assertFalse(failure.success)
        self.assertEqual(failed.pending_bind_attack.accuracy, before_modifier)
        # 66-67: not universal, never Mutieren.
        blank, ba, bb = setup_cross(pressure=HART, a_plays={PAIRED_PLAY}, b_plays={COUNTER_WIND})
        blank.pending_bind_attack = None
        self.assertFalse(blank.counter_wind(bb, (2,)).legal)
        mut, ma, mb = setup_cross(pressure=WEICH, a_plays={PAIRED_PLAY}, b_plays={COUNTER_WIND})
        mut.declare_bind_rejoinder(ma, "Mutieren", "G")
        self.assertFalse(mut.counter_wind(mb, (2,)).legal)

    def test_68_71_geometry(self):
        engine, a, b = setup_cross(pressure=WEICH)
        # 68: measure and contact zone are independent.
        engine.crossing.contact_zone = {a.name: "middle", b.name: "middle"}
        self.assertEqual(engine.crossing.measure, "wide")
        # 69: low guard does not create Close.
        b.guard = "alber"
        self.assertEqual(engine.crossing.measure, "wide")
        # 70: no generic paid close method exists.
        self.assertFalse(hasattr(engine, "buy_close_measure"))
        # 71: T1 remains the authoritative named method, not candidate glue.
        self.assertTrue(hasattr(ProvisionalLongswordEngine, "tutta_cover_to_stretto"))

    def test_72_75_chain_cap(self):
        engine, a, b = setup_cross(
            pressure=HART, a_plays={PAIRED_PLAY, "Fühlen"}, b_plays={COUNTER_WIND}
        )
        before = len(engine.learned_chain)
        engine.buy_fuhlen(a)
        self.assertEqual(len(engine.learned_chain), before)  # 72
        engine.declare_bind_rejoinder(a, "Duplieren", "G")
        self.assertEqual(len(engine.learned_chain), before + 1)  # 73
        engine.counter_wind(b, (4,))
        self.assertEqual(len(engine.learned_chain), before + 2)  # 74
        self.assertTrue(engine.add_learned_play("third"))
        self.assertFalse(engine.add_learned_play("fourth"))  # 75


if __name__ == "__main__":
    unittest.main()

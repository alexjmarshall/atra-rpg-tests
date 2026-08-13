from __future__ import annotations

import unittest
import json
from pathlib import Path

from simulations.general_bind_information_v0_1.candidate_engine import (
    COUNTER_WIND,
    HART,
    PAIRED_PLAY,
    UNKNOWN,
    WEICH,
)
from simulations.hart_weich_upper_winden_v0_2.candidate_engine import (
    BIND_HEIGHTS,
    LOWER,
    UPPER,
    WINDEN_PLAY,
    CandidateCrossing,
    HartWeichUpperWindenEngine,
    make_successful_h2_cross,
)
from simulations.shared.provisional_longsword_engine import (
    Attack,
    Fighter,
    OPEN,
    ProvisionalLongswordEngine,
)


class HartWeichUpperWindenTests(unittest.TestCase):
    """Exact branch assertions corresponding to required cases 3-75+."""

    def test_03_10_bind_height_and_writer(self):
        # 3: all states; 4: default; 5: lower is valid.
        self.assertEqual(BIND_HEIGHTS, (UPPER, LOWER, UNKNOWN))
        state = CandidateCrossing()
        self.assertEqual(state.bind_height, UNKNOWN)
        state.bind_height = LOWER
        self.assertEqual(state.bind_height, LOWER)
        # 6: no generic numeric modifier.
        self.assertFalse(hasattr(state, "attack_modifier"))
        # 7-8: contact zone and measure remain distinct.
        state.contact_zone = {"A": "pointward"}
        state.measure = "close"
        self.assertEqual(state.bind_height, LOWER)
        self.assertEqual(state.contact_zone["A"], "pointward")
        self.assertEqual(state.measure, "close")
        # 9-10: conservative writer only for qualifying descending Cut.
        upper, _, _ = make_successful_h2_cross(qualifying_upper=True)
        unknown, _, _ = make_successful_h2_cross(qualifying_upper=False)
        self.assertEqual(upper.crossing.bind_height, UPPER)
        self.assertEqual(unknown.crossing.bind_height, UNKNOWN)

    def test_11_17_failed_and_successful_h1_cross(self):
        a, b = Fighter("A"), Fighter("B")
        engine = HartWeichUpperWindenEngine([a, b])
        attack = engine.declare_attack(a, b, "descending-cut", descending=True)
        rolled = engine.roll_pending_attack((5,))
        self.assertTrue(engine.declare_h1_cross(b, HART))
        failed = engine.resolve_h1_cross(b, (19, 20))
        # 11-12: failed Cross persists neither pressure nor height.
        self.assertFalse(failed.success)
        self.assertEqual(engine.crossing.pressure, {})
        self.assertEqual(engine.crossing.bind_height, UNKNOWN)
        # 13-17: exact Hart/Weich modifiers, Rejoinder, no relation/Leverage.
        hart, _, _ = make_successful_h2_cross(pressure=HART)
        weich, _, _ = make_successful_h2_cross(pressure=WEICH)
        self.assertEqual(hart.event_log[-2], "H2:H1-Cross-roll:boon")
        self.assertEqual(weich.event_log[-2], "H2:H1-Cross-roll:normal")
        self.assertTrue(hart.rejoinder_open)
        self.assertEqual(set(hart.crossing.bind_position.values()), {UNKNOWN})
        self.assertFalse(hasattr(hart.crossing, "leverage"))
        self.assertTrue(rolled.success and attack is not None)

    def test_18_23_fuhlen_initial_cycle_only(self):
        engine, a, b = make_successful_h2_cross(
            pressure=HART, attacker_plays={"Fühlen"}
        )
        before = (a.spiritus, a.action_available, len(engine.learned_chain))
        # 18-22: 1S, no action/chain, exact reveal, once.
        self.assertEqual(engine.buy_fuhlen(a), HART)
        self.assertEqual(a.spiritus, before[0] - 1)
        self.assertEqual(a.action_available, before[1])
        self.assertEqual(len(engine.learned_chain), before[2])
        self.assertEqual(engine.pressure_view(a, b), HART)
        self.assertIsNone(engine.buy_fuhlen(a))
        # 23: no permanent/future-pressure visibility.
        self.assertTrue(engine.decline_bind_rejoinder(a))
        engine.crossing.pressure[b.name] = WEICH
        self.assertEqual(engine.pressure_view(a, b), UNKNOWN)

    def test_24_31_duplieren_mutieren_hard_failure(self):
        d, da, db = make_successful_h2_cross(
            pressure=HART, attacker_plays={PAIRED_PLAY}
        )
        before = da.spiritus
        self.assertTrue(d.declare_bind_rejoinder(da, "Duplieren").success)
        # 24-27: correct D is 2S, one chain, Booned high Cut, normal damage.
        self.assertEqual(da.spiritus, before - 2)
        self.assertEqual(len(d.learned_chain), 1)
        self.assertEqual((d.pending_bind_attack.kind, d.pending_bind_attack.height), ("cut", "high"))
        self.assertEqual(d.pending_bind_attack.accuracy, "boon")
        hit = d.resolve_bind_rejoinder((5, 18), (4,))
        self.assertEqual(hit.damage, 5)
        # 28: wrong D hard-fails after spend, without roll/chip.
        wrong_d, wa, wb = make_successful_h2_cross(
            pressure=WEICH, attacker_plays={PAIRED_PLAY}
        )
        hp = wb.hp
        result = wrong_d.declare_bind_rejoinder(wa, "Duplieren")
        self.assertTrue(result.legal and not result.success)
        self.assertEqual((wa.spiritus, wb.hp, wrong_d.pending_bind_attack), (6, hp, None))
        # 29-31: Mutieren mirrors on Weich and hard-fails on Hart.
        m, ma, _ = make_successful_h2_cross(
            pressure=WEICH, attacker_plays={PAIRED_PLAY}
        )
        self.assertTrue(m.declare_bind_rejoinder(ma, "Mutieren").success)
        self.assertEqual((m.pending_bind_attack.kind, m.pending_bind_attack.accuracy), ("thrust", "boon"))
        self.assertTrue(m.crossing.retained and ma.point_threat == "threatening")
        wrong_m, wma, _ = make_successful_h2_cross(
            pressure=HART, attacker_plays={PAIRED_PLAY}
        )
        self.assertFalse(wrong_m.declare_bind_rejoinder(wma, "Mutieren").success)
        self.assertFalse(hasattr(m, "response_denied"))

    def test_32_35_decline_initiative_and_pressure_expiry(self):
        hart, ha, _ = make_successful_h2_cross(pressure=HART)
        self.assertTrue(hart.decline_bind_rejoinder(ha))
        self.assertEqual(hart.crossing.bind_initiative, ha.name)
        self.assertEqual(set(hart.crossing.pressure.values()), {UNKNOWN})
        weich, wa, wb = make_successful_h2_cross(pressure=WEICH)
        self.assertTrue(weich.decline_bind_rejoinder(wa))
        self.assertEqual(weich.crossing.bind_initiative, wb.name)
        self.assertEqual(set(weich.crossing.pressure.values()), {UNKNOWN})
        self.assertFalse(hasattr(weich.crossing, "initiative_modifier"))

    def test_36_45_upper_winding_requirements_and_roles(self):
        base, a, _ = make_successful_h2_cross(pressure=HART)
        base.decline_bind_rejoinder(a)
        # 36: knowledge.
        self.assertFalse(base.upper_winding_legal(a))
        # 37-39: initiative, Crossing, Upper.
        no_i, ia, ib = make_successful_h2_cross(
            pressure=WEICH, attacker_plays={WINDEN_PLAY}
        )
        no_i.decline_bind_rejoinder(ia)
        self.assertFalse(no_i.upper_winding_legal(ia))
        no_i.crossing.contact = "none"
        no_i.crossing.bind_initiative = ia.name
        self.assertFalse(no_i.upper_winding_legal(ia))
        no_i.crossing.contact = "crossing"
        no_i.crossing.bind_height = UNKNOWN
        self.assertFalse(no_i.upper_winding_legal(ia))
        # 40-43: pressure/relation/start guard are not gates; original attacker works.
        actor, aa, _ = make_successful_h2_cross(
            pressure=HART, attacker_plays={WINDEN_PLAY}
        )
        actor.decline_bind_rejoinder(aa)
        aa.guard = "vom-tag"
        self.assertEqual(set(actor.crossing.pressure.values()), {UNKNOWN})
        self.assertEqual(set(actor.crossing.bind_position.values()), {UNKNOWN})
        self.assertTrue(actor.upper_winding_legal(aa))
        self.assertTrue(actor.declare_upper_winding(aa).legal)
        # 44-45: original defender also works, from a non-Ochs/Pflug guard.
        defender, sa, sb = make_successful_h2_cross(
            pressure=WEICH, defender_plays={WINDEN_PLAY}
        )
        defender.decline_bind_rejoinder(sa)
        sb.guard = "alber"
        self.assertTrue(defender.upper_winding_legal(sb))
        self.assertTrue(defender.declare_upper_winding(sb).legal)
        self.assertIs(ib, no_i.other(ia))

    def test_46_54_upper_winding_declaration_payload(self):
        # 46-47: U1/U2 exact costs.
        u1, a1, _ = make_successful_h2_cross(
            pressure=HART, attacker_plays={WINDEN_PLAY}
        )
        u1.decline_bind_rejoinder(a1)
        before = (a1.spiritus, len(u1.learned_chain), a1.action_available)
        self.assertTrue(u1.declare_upper_winding(a1, 1).legal)
        self.assertEqual(a1.spiritus, before[0] - 1)
        # 48-54: chain, no action, retain, Ochs, point, flat Thrust, no bonus.
        self.assertEqual(len(u1.learned_chain), before[1] + 1)
        self.assertEqual(a1.action_available, before[2])
        self.assertTrue(u1.crossing.retained)
        self.assertEqual((a1.guard, u1.crossing.hanging_aftermath), ("ochs", "ochs-upper-hanging"))
        self.assertEqual(a1.point_threat, "threatening")
        self.assertEqual((u1.pending_upper_winding.kind, u1.pending_upper_winding.accuracy), ("thrust", "normal"))
        self.assertFalse(hasattr(u1.pending_upper_winding, "damage_boon"))

        u2, a2, _ = make_successful_h2_cross(
            pressure=HART, attacker_plays={WINDEN_PLAY}
        )
        u2.decline_bind_rejoinder(a2)
        before2 = a2.spiritus
        u2.declare_upper_winding(a2, 2)
        self.assertEqual(a2.spiritus, before2 - 2)

    def test_55_62_upper_winding_hit_and_miss(self):
        hit_engine, ha, hb = make_successful_h2_cross(
            pressure=HART, attacker_plays={WINDEN_PLAY}
        )
        hit_engine.decline_bind_rejoinder(ha)
        hit_engine.declare_upper_winding(ha, 2)
        hit = hit_engine.resolve_upper_winding((5,), (4,))
        # 55-56: hit normal damage and bounded cleanup.
        self.assertEqual((hit.success, hit.damage, hb.hp), (True, 5, 3))
        self.assertEqual(hit_engine.crossing.contact, "none")

        miss_engine, ma, mb = make_successful_h2_cross(
            pressure=HART, attacker_plays={WINDEN_PLAY}
        )
        miss_engine.decline_bind_rejoinder(ma)
        miss_engine.declare_upper_winding(ma, 2)
        before_hp = mb.hp
        miss = miss_engine.resolve_upper_winding((20,), (6,))
        # 57-62: zero damage, retained state, transfer, no Open/arbitrary Boon.
        self.assertEqual((miss.success, miss.damage, mb.hp), (False, 0, before_hp))
        self.assertTrue(miss_engine.crossing.contact == "crossing" and miss_engine.crossing.retained)
        self.assertEqual((ma.guard, ma.point_threat), ("ochs", "threatening"))
        self.assertEqual(miss_engine.crossing.bind_initiative, mb.name)
        self.assertNotEqual(ma.guard, OPEN)
        self.assertFalse(hasattr(miss_engine.crossing, "opponent_attack_modifier"))

    def test_63_68_failed_winding_loop_and_cap(self):
        engine, a, b = make_successful_h2_cross(
            pressure=HART,
            attacker_plays={WINDEN_PLAY},
            defender_plays={WINDEN_PLAY},
            attacker_spiritus=6,
            defender_spiritus=6,
        )
        engine.decline_bind_rejoinder(a)
        actions = (a.action_available, b.action_available)
        # 63-66: A miss -> B miss -> A miss, each spending/charging.
        engine.declare_upper_winding(a, 2)
        engine.resolve_upper_winding((20,))
        self.assertTrue(engine.declare_upper_winding(b, 2).legal)
        engine.resolve_upper_winding((20,))
        self.assertTrue(engine.declare_upper_winding(a, 2).legal)
        engine.resolve_upper_winding((20,))
        self.assertEqual((a.spiritus, b.spiritus), (2, 4))
        self.assertEqual(len(engine.learned_chain), 3)
        # 67-68: fourth illegal; no action refresh.
        self.assertFalse(engine.declare_upper_winding(b, 2).legal)
        self.assertEqual((a.action_available, b.action_available), actions)

    def test_69_72_pass_disengage_and_no_nachreisen(self):
        passed, pa, pb = make_successful_h2_cross(pressure=HART)
        passed.decline_bind_rejoinder(pa)
        self.assertTrue(passed.pass_bind_initiative(pa))
        self.assertEqual(passed.crossing.bind_initiative, pb.name)
        self.assertTrue(passed.pass_bind_initiative(pb))
        self.assertEqual(passed.crossing.contact, "none")
        disengage, da, _ = make_successful_h2_cross(pressure=HART)
        disengage.decline_bind_rejoinder(da)
        self.assertTrue(disengage.disengage(da))
        self.assertEqual(disengage.crossing.contact, "none")
        self.assertIsNone(disengage.recovery_nachreisen_target)

    def test_73_80_scope_compatibility_and_deferred_features(self):
        # 73: Zornhau stays local and does not open ordinary H1 Rejoinder.
        a = Fighter("A")
        b = Fighter("B", known_plays={"Zornhau-Ort", WINDEN_PLAY})
        z = HartWeichUpperWindenEngine([a, b])
        attack = z.declare_attack(a, b, "descending-cut", descending=True)
        rolled = z.roll_pending_attack((5,))
        result = z.zornhau(b, rolled.roll, (4,))
        self.assertTrue(result.success)
        self.assertFalse(z.rejoinder_open)
        self.assertEqual(z.crossing_source, "zornhau-local")
        # 74: current local Winden remains available only there.
        self.assertTrue(z.winden(b, "W2", (5,)).legal)
        # 75: point-threatening learned defence does not open H1.
        self.assertEqual(b.point_threat, "threatening")
        # 76: ordinary H1 cannot call stale generic W1/W2.
        h1, h1a, _ = make_successful_h2_cross(
            pressure=HART, attacker_plays={WINDEN_PLAY}
        )
        h1.decline_bind_rejoinder(h1a)
        self.assertFalse(h1.winden(h1a, "W2", (5,)).legal)
        # 77: Counter-Wind is deferred.
        cw, cwa, cwb = make_successful_h2_cross(
            pressure=HART,
            attacker_plays={PAIRED_PLAY},
            defender_plays={COUNTER_WIND},
        )
        cw.declare_bind_rejoinder(cwa, "Duplieren")
        self.assertFalse(cw.counter_wind(cwb, (4,)).legal)
        # 78: no generic paid Wide->Close; 79: no Leverage.
        self.assertFalse(hasattr(h1, "buy_close_measure"))
        self.assertFalse(hasattr(h1.crossing, "leverage"))
        # 80: no D1 insertion into bind phase; threatening point keeps normal D1 meaning.
        h1a.known_plays.add("Durchwechseln")
        self.assertFalse(h1.declare_durchwechseln(h1a, h1.other(h1a), h1.pending_attack))
        h1a.point_threat = "threatening"
        self.assertFalse(h1.d1_window(h1a, Attack(h1.other(h1a), h1a, "cut")))

    def test_81_t1_remains_inherited_and_distinct(self):
        a = Fighter("A", guard="tutta-porta-di-ferro", known_plays={"Tutta Cover-to-Stretto"})
        b = Fighter("B")
        engine = HartWeichUpperWindenEngine([a, b])
        engine.crossing = CandidateCrossing(contact="crossing", measure="wide")
        before = (a.spiritus, len(engine.learned_chain))
        self.assertTrue(engine.tutta_cover_to_stretto(a))
        self.assertEqual(engine.crossing.measure, "close")
        self.assertEqual((a.spiritus, len(engine.learned_chain)), (before[0] - 1, before[1] + 1))
        self.assertIs(
            HartWeichUpperWindenEngine.tutta_cover_to_stretto,
            ProvisionalLongswordEngine.tutta_cover_to_stretto,
        )

    def test_82_artifacts_are_candidate_only_and_complete(self):
        root = Path(__file__).resolve().parents[1]
        prototype = json.loads(
            (root / "data/prototypes/hart-weich-upper-winden-loop-v0.2.yaml").read_text(encoding="utf-8")
        )
        results = json.loads(
            (root / "reports/hart-weich-upper-winden-loop-v02-results.json").read_text(encoding="utf-8")
        )
        report = (root / "reports/hart-weich-upper-winden-loop-v02-results.md").read_text(encoding="utf-8")
        self.assertFalse(prototype["automatic_promotion"])
        self.assertFalse(prototype["authoritative_engine_edited"])
        self.assertEqual(prototype["candidate_layer"]["counter_wind"], "DEFERRED / NOT IMPLEMENTED")
        self.assertEqual(len(prototype["candidate_records"]), 6)
        self.assertEqual(results["baseline_regression"]["governing"]["passed"], 81)
        self.assertEqual(results["baseline_regression"]["previous_candidate"]["passed"], 75)
        self.assertEqual(len(results["controlled_game_tree"]), 560)
        self.assertEqual(len(results["fuhlen_after_decline"]), 100)
        self.assertEqual(len(results["short_krieg_chains"]), 160)
        for heading in (
            "## Executive Result",
            "## H2 vs R0",
            "## Project Decision Table",
            "## Final Project-Review Questions",
        ):
            self.assertIn(heading, report)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import unittest
from pathlib import Path

from simulations.general_bind_information_v0_1.candidate_engine import HART, PAIRED_PLAY, UNKNOWN, WEICH
from simulations.hart_weich_upper_winden_v0_2.candidate_engine import UPPER, WINDEN_PLAY
from simulations.upper_lower_winden_v0_3.candidate_engine import (
    L1,
    L2,
    LOWER,
    LOWER_SETTING_ASIDE,
    UNCLASSIFIED,
    UPPER_CROSS,
    UpperLowerWindenEngine,
    make_successful_h3_cross,
)
from simulations.upper_lower_winden_v0_3.simulate import dm_vectors, select_strategy
from simulations.shared.provisional_longsword_engine import Fighter


ROOT = Path(__file__).resolve().parents[1]


class UpperLowerWindenV03Tests(unittest.TestCase):
    def test_01_04_selector_and_serialization(self):
        # 1-2: known Hart/Weich choose the positive correct branch.
        hart = select_strategy(dm_vectors(14, HART))
        weich = select_strategy(dm_vectors(14, WEICH))
        self.assertEqual(hart["selected_strategy"], "blind_duplieren")
        self.assertEqual(weich["selected_strategy"], "blind_mutieren")
        # 3: lower spend is consulted only after primary damage ties.
        vectors = {
            "higher_damage_high_spend": {"striker_outgoing_damage": 2, "striker_spiritus": 9},
            "lower_damage_low_spend": {"striker_outgoing_damage": 1, "striker_spiritus": 0},
        }
        self.assertEqual(select_strategy(vectors)["selected_strategy"], "higher_damage_high_spend")
        tied = {
            "expensive": {"striker_outgoing_damage": 2, "striker_spiritus": 3},
            "cheap": {"striker_outgoing_damage": 2, "striker_spiritus": 2},
        }
        self.assertEqual(select_strategy(tied)["selected_strategy"], "cheap")
        # 4: serialized selection is an actual selector return.
        data = json.loads((ROOT / "reports/upper-lower-winden-completion-v03-results.json").read_text(encoding="utf-8"))
        row = next(r for r in data["hart_weich_consequence_vectors"] if r["pressure"] == HART and r["knowledge"] == "striker_dm")
        self.assertEqual(row["selected_strategy"], select_strategy(row["candidate_vectors"])["selected_strategy"])

    def test_05_15_height_and_writers(self):
        # 5-8: enum values exist and height is independent/no modifier.
        upper, a, b = make_successful_h3_cross(geometry=UPPER_CROSS)
        lower, la, lb = make_successful_h3_cross(geometry=LOWER_SETTING_ASIDE)
        unknown, ua, ub = make_successful_h3_cross(geometry=UNCLASSIFIED)
        self.assertEqual({upper.crossing.bind_height, lower.crossing.bind_height, unknown.crossing.bind_height}, {UPPER, LOWER, UNKNOWN})
        lower.crossing.measure = "close"
        lower.crossing.contact_zone = {"A": "hiltward", "B": "pointward"}
        self.assertEqual(lower.crossing.bind_height, LOWER)
        self.assertFalse(hasattr(lower.crossing, "height_modifier"))
        # 9-10: starting named guards do not imply a height.
        pflug, *_ = make_successful_h3_cross(geometry=UNCLASSIFIED, defender_guard="pflug")
        ochs, *_ = make_successful_h3_cross(geometry=UNCLASSIFIED, defender_guard="ochs")
        self.assertEqual(pflug.crossing.bind_height, UNKNOWN)
        self.assertEqual(ochs.crossing.bind_height, UNKNOWN)
        # 11-12,14-15: deterministic qualified writers and no random fallback.
        self.assertEqual(upper.crossing.bind_height, UPPER)
        self.assertEqual(lower.crossing.bind_height, LOWER)
        self.assertEqual(unknown.crossing.bind_height, UNKNOWN)
        again, *_ = make_successful_h3_cross(geometry=UNCLASSIFIED)
        self.assertEqual(again.crossing.bind_height, UNKNOWN)
        # 13: failed Cross persists neither height nor pressure.
        x = Fighter("A")
        y = Fighter("B")
        engine = UpperLowerWindenEngine([x, y])
        attack = engine.declare_attack(x, y, "low-line-thrust")
        self.assertIsNotNone(attack)
        self.assertTrue(engine.roll_pending_attack((5,)).success)
        self.assertTrue(engine.declare_h3_cross(y, HART, LOWER_SETTING_ASIDE))
        failed = engine.resolve_h1_cross(y, (19, 20))
        self.assertFalse(failed.success)
        self.assertEqual(engine.crossing.bind_height, UNKNOWN)
        self.assertEqual(engine.crossing.pressure, {})

    def test_16_28_lower_winding_requirements_and_payload(self):
        # 16: knowledge.
        e, a, b = make_successful_h3_cross(geometry=LOWER_SETTING_ASIDE)
        self.assertTrue(e.decline_bind_rejoinder(a))
        self.assertFalse(e.declare_lower_winding(a).success)
        # 17-20: initiative, Crossing, Lower, and 2S.
        e, a, b = make_successful_h3_cross(geometry=LOWER_SETTING_ASIDE, attacker_plays=(WINDEN_PLAY,))
        self.assertFalse(e.declare_lower_winding(a).success)
        self.assertTrue(e.decline_bind_rejoinder(a))
        e.crossing.bind_height = UPPER
        self.assertFalse(e.declare_lower_winding(a).success)
        e.crossing.bind_height = LOWER
        e.crossing.contact = "none"
        self.assertFalse(e.declare_lower_winding(a).success)
        e.crossing.contact = "crossing"
        a.spiritus = 1
        self.assertFalse(e.declare_lower_winding(a).success)
        a.spiritus = 2
        action_before = a.action_available
        declared = e.declare_lower_winding(a, L2)
        self.assertTrue(declared.success)
        # 21-28: +chain, no action, pressure independent/no starting gate, Pflug/threat/flat/normal.
        self.assertEqual(len(e.learned_chain), 1)
        self.assertEqual(a.action_available, action_before)
        self.assertEqual(e.crossing.pressure["A"], UNKNOWN)
        self.assertEqual(a.guard, "pflug")
        self.assertEqual(a.point_threat, "threatening")
        self.assertEqual(e.pending_lower_winding.accuracy, "normal")
        hp = b.hp
        hit = e.resolve_lower_winding((5,), (3,))
        self.assertTrue(hit.success)
        self.assertEqual(hit.damage, 4)
        self.assertEqual(b.hp, hp - 4)

    def test_29_42_l1_l2_misses(self):
        # 29-34: L1 miss state.
        e, a, b = make_successful_h3_cross(geometry=LOWER_SETTING_ASIDE, attacker_plays=(WINDEN_PLAY,))
        self.assertTrue(e.decline_bind_rejoinder(a))
        self.assertTrue(e.declare_lower_winding(a, L1).success)
        miss = e.resolve_lower_winding((20,))
        self.assertFalse(miss.success)
        self.assertEqual(miss.damage, 0)
        self.assertEqual(e.crossing.contact, "crossing")
        self.assertEqual(e.crossing.bind_height, LOWER)
        self.assertEqual(a.guard, "pflug")
        self.assertEqual(a.point_threat, "threatening")
        self.assertEqual(e.crossing.bind_initiative, b.name)
        # 35-42: L2 miss state and no free follow-up/retained initiative.
        e, a, b = make_successful_h3_cross(geometry=LOWER_SETTING_ASIDE, attacker_plays=(WINDEN_PLAY,), defender_plays=(WINDEN_PLAY,))
        self.assertTrue(e.decline_bind_rejoinder(a))
        self.assertTrue(e.declare_lower_winding(a, L2).success)
        miss = e.resolve_lower_winding((20,))
        self.assertFalse(miss.success)
        self.assertEqual(miss.damage, 0)
        self.assertEqual(e.crossing.contact, "crossing")
        self.assertEqual(e.crossing.bind_height, UPPER)
        self.assertEqual(a.guard, "ochs")
        self.assertEqual(a.point_threat, "threatening")
        self.assertEqual(e.crossing.bind_initiative, b.name)
        self.assertIsNone(e.pending_upper_winding)

    def test_43_49_upper_interaction_and_chain(self):
        e, a, b = make_successful_h3_cross(geometry=LOWER_SETTING_ASIDE, attacker_plays=(WINDEN_PLAY,), defender_plays=(WINDEN_PLAY,))
        self.assertTrue(e.decline_bind_rejoinder(a))
        self.assertTrue(e.declare_lower_winding(a, L2).success)
        self.assertFalse(e.resolve_lower_winding((20,)).success)
        # 43-46: new holder may Upper Wind; fixed 2S/+1/no action refresh.
        action_before = b.action_available
        self.assertFalse(e.declare_upper_winding(b, 1).success)
        self.assertTrue(e.declare_upper_winding(b, 2).success)
        self.assertEqual(b.spiritus, 6)
        self.assertEqual(len(e.learned_chain), 2)
        self.assertEqual(b.action_available, action_before)
        self.assertFalse(e.resolve_upper_winding((20,)).success)
        # 47-49: Lower -> Upper -> Upper gives three entries; fourth is illegal.
        self.assertTrue(e.declare_upper_winding(a, 2).success)
        self.assertEqual(len(e.learned_chain), 3)
        self.assertFalse(e.resolve_upper_winding((20,)).success)
        self.assertFalse(e.declare_upper_winding(b, 2).success)

    def test_50_61_pressure_unknown_and_guards(self):
        # 50-53: phase-scoped pressure, D/M consumption, no Winding rewrite.
        e, a, b = make_successful_h3_cross(pressure=HART, geometry=LOWER_SETTING_ASIDE, attacker_plays=(PAIRED_PLAY, WINDEN_PLAY))
        self.assertEqual(e.crossing.pressure[b.name], HART)
        self.assertTrue(e.declare_bind_rejoinder(a, "Duplieren").success)
        self.assertTrue(all(v == UNKNOWN for v in e.crossing.pressure.values()))
        e2, a2, b2 = make_successful_h3_cross(pressure=WEICH, geometry=LOWER_SETTING_ASIDE, defender_plays=(WINDEN_PLAY,))
        self.assertTrue(e2.decline_bind_rejoinder(a2))
        self.assertTrue(all(v == UNKNOWN for v in e2.crossing.pressure.values()))
        self.assertTrue(e2.declare_lower_winding(b2, L2).success)
        self.assertFalse(e2.resolve_lower_winding((20,)).success)
        self.assertTrue(all(v == UNKNOWN for v in e2.crossing.pressure.values()))
        # 54-57: Unknown forbids both Windings and remains/pass-cleans normally.
        u, ua, ub = make_successful_h3_cross(geometry=UNCLASSIFIED, attacker_plays=(WINDEN_PLAY,), defender_plays=(WINDEN_PLAY,))
        self.assertTrue(u.decline_bind_rejoinder(ua))
        self.assertFalse(u.declare_upper_winding(ua).success)
        self.assertFalse(u.declare_lower_winding(ua).success)
        self.assertEqual(u.crossing.bind_height, UNKNOWN)
        self.assertTrue(u.pass_bind_initiative(ua))
        self.assertTrue(u.pass_bind_initiative(ub))
        self.assertEqual(u.crossing.contact, "none")
        # 58-61: produced guards, L2 Ochs, and no generic guard bonus.
        up, upa, upb = make_successful_h3_cross(geometry=UPPER_CROSS, attacker_plays=(WINDEN_PLAY,))
        self.assertTrue(up.decline_bind_rejoinder(upa))
        self.assertTrue(up.declare_upper_winding(upa).success)
        self.assertEqual(upa.guard, "ochs")
        low, loa, lob = make_successful_h3_cross(geometry=LOWER_SETTING_ASIDE, attacker_plays=(WINDEN_PLAY,))
        self.assertTrue(low.decline_bind_rejoinder(loa))
        self.assertTrue(low.declare_lower_winding(loa, L2).success)
        self.assertEqual(loa.guard, "pflug")
        self.assertFalse(low.resolve_lower_winding((20,)).success)
        self.assertEqual(loa.guard, "ochs")
        self.assertFalse(hasattr(loa, "guard_bonus"))

    def test_62_68_no_extra_systems_and_compatibility(self):
        # 62-66: no Leverage, Counter-Wind, generic movement/Unknown Winden, restriction.
        e, a, b = make_successful_h3_cross(geometry=UNCLASSIFIED)
        self.assertFalse(hasattr(e.crossing, "leverage"))
        self.assertFalse(e.counter_wind(b, (5,)).success)
        self.assertEqual(e.crossing.measure, "wide")
        self.assertEqual(e.crossing.bind_height, UNKNOWN)
        self.assertFalse(hasattr(e, "response_restriction"))
        # 67: Zornhau remains inherited/local and does not gain H3 pressure/height.
        za = Fighter("A")
        zb = Fighter("B", known_plays={"Zornhau-Ort"})
        z = UpperLowerWindenEngine([za, zb])
        attack = z.declare_attack(za, zb, "descending-cut", descending=True)
        rolled = z.roll_pending_attack((5,)).roll
        self.assertTrue(z.zornhau(zb, rolled, (6,)).success)
        self.assertEqual(z.crossing.bind_height, UNKNOWN)
        self.assertEqual(z.crossing_source, "zornhau-local")
        # 68: T1 is inherited unchanged.
        self.assertEqual(UpperLowerWindenEngine.tutta_cover_to_stretto.__qualname__, "ProvisionalLongswordEngine.tutta_cover_to_stretto")


if __name__ == "__main__":
    unittest.main()

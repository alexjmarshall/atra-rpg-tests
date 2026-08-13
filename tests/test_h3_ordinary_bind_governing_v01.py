from __future__ import annotations

import json
import unittest
from pathlib import Path

from simulations.shared.provisional_longsword_engine import (
    BIND_HEIGHTS,
    HART,
    LOWER,
    LOWER_SETTING_ASIDE,
    PAIRED_PLAY,
    UNKNOWN,
    UPPER,
    UPPER_CROSS,
    WEICH,
    Attack,
    Crossing,
    Fighter,
    ProvisionalLongswordEngine,
)


ROOT = Path(__file__).resolve().parents[1]
FUHLEN = "Fühlen"


def successful_cross(
    *,
    pressure: str = HART,
    geometry: str = UPPER_CROSS,
    attacker_plays=(),
    defender_plays=(),
    attacker_spiritus: int = 8,
    defender_spiritus: int = 8,
    attacker_guard: str = "vom-tag",
    defender_guard: str = "vom-tag",
    attack_kind: str | None = None,
    descending: bool | None = None,
):
    a = Fighter(
        "A",
        spiritus=attacker_spiritus,
        guard=attacker_guard,
        known_plays=set(attacker_plays),
    )
    b = Fighter(
        "B",
        spiritus=defender_spiritus,
        guard=defender_guard,
        known_plays=set(defender_plays),
    )
    if attack_kind is None:
        attack_kind = {
            UPPER_CROSS: "descending-cut",
            LOWER_SETTING_ASIDE: "low-line-thrust",
        }.get(geometry, "lateral-cut")
    if descending is None:
        descending = geometry == UPPER_CROSS
    engine = ProvisionalLongswordEngine([a, b])
    attack = engine.declare_attack(a, b, attack_kind, descending=descending)
    assert attack is not None
    attack_result = engine.roll_pending_attack((5,))
    assert attack_result.success and attack_result.roll is not None
    assert engine.declare_basic_cross(b, pressure, geometry)
    cross_rolls = (6, 16) if pressure == HART else (6,)
    cross = engine.basic_defence("Cross", b, attack_result.roll, cross_rolls)
    assert cross.legal and cross.success
    return engine, a, b, cross


class H3OrdinaryBindGoverningTests(unittest.TestCase):
    def test_integrated_geometry_rejoinder_and_continuation_smoke_matrix(self):
        cases = (
            ("descending-hart-upper", HART, UPPER_CROSS, UPPER),
            ("descending-weich-upper", WEICH, UPPER_CROSS, UPPER),
            ("low-setting-aside-lower", WEICH, LOWER_SETTING_ASIDE, LOWER),
            ("lateral-unclassified-unknown", HART, "unclassified", UNKNOWN),
        )
        for label, pressure, geometry, expected_height in cases:
            with self.subTest(case=label, branch="blind-dm"):
                blind, actor, _, _ = successful_cross(
                    pressure=pressure,
                    geometry=geometry,
                    attacker_plays={PAIRED_PLAY},
                )
                action_before = actor.action_available
                self.assertEqual(blind.crossing.bind_height, expected_height)
                result = blind.declare_bind_rejoinder(actor, "Duplieren")
                self.assertTrue(result.legal)
                self.assertEqual(actor.action_available, action_before)
                self.assertEqual(result.success, pressure == HART)

            with self.subTest(case=label, branch="fuhlen"):
                sensed, actor, defender, _ = successful_cross(
                    pressure=pressure,
                    geometry=geometry,
                    attacker_plays={FUHLEN},
                )
                action_before = actor.action_available
                self.assertEqual(sensed.buy_fuhlen(actor), pressure)
                self.assertEqual(sensed.pressure_view(actor, defender), pressure)
                self.assertEqual(actor.action_available, action_before)
                self.assertEqual(len(sensed.learned_chain), 0)

            with self.subTest(case=label, branch="decline-and-continuation"):
                continuation, striker, parrier, _ = successful_cross(
                    pressure=pressure,
                    geometry=geometry,
                    attacker_plays={"Winden"},
                    defender_plays={"Winden"},
                )
                self.assertTrue(continuation.decline_bind_rejoinder(striker))
                holder = striker if pressure == HART else parrier
                self.assertEqual(continuation.crossing.bind_initiative, holder.name)
                self.assertEqual(set(continuation.crossing.initial_pressure.values()), {UNKNOWN})
                if expected_height == UPPER:
                    self.assertTrue(continuation.declare_upper_winding(holder).legal)
                elif expected_height == LOWER:
                    self.assertTrue(continuation.declare_lower_winding(holder).legal)
                else:
                    self.assertFalse(continuation.upper_winding_legal(holder))
                    self.assertFalse(continuation.lower_winding_legal(holder))
                    self.assertTrue(continuation.pass_bind_initiative(holder))
                    self.assertTrue(continuation.pass_bind_initiative(continuation.other(holder)))
                    self.assertEqual(continuation.crossing.contact, "none")

    def test_required_governing_matrix_001_129(self):
        covered: set[int] = set()

        def check(number: int, condition: bool) -> None:
            self.assertTrue(condition, f"governing requirement {number}")
            covered.add(number)

        # 1-10: declaration, modifier, cleanup, hidden state, supersession.
        a, b = Fighter("A"), Fighter("B")
        engine = ProvisionalLongswordEngine([a, b])
        attack = engine.declare_attack(a, b, "descending-cut", descending=True)
        rolled = engine.roll_pending_attack((5,))
        check(1, not engine.basic_defence("Cross", b, rolled.roll, (6,)).legal)
        check(1, engine.declare_basic_cross(b, HART, UPPER_CROSS))
        cross = engine.basic_defence("Cross", b, rolled.roll, (6, 16))
        check(2, cross.roll is not None and cross.roll.modifier == "boon" and len(cross.roll.rolls) == 2)

        weich, wa, wb, weich_cross = successful_cross(pressure=WEICH)
        check(3, weich_cross.roll is not None and weich_cross.roll.modifier == "normal")

        fa, fb = Fighter("A"), Fighter("B")
        failed = ProvisionalLongswordEngine([fa, fb])
        failed_attack = failed.declare_attack(fa, fb, "descending-cut", descending=True)
        failed_roll = failed.roll_pending_attack((5,)).roll
        check(1, failed.declare_basic_cross(fb, HART, UPPER_CROSS))
        failed_cross = failed.basic_defence("Cross", fb, failed_roll, (19, 20))
        check(4, not failed_cross.success and failed.crossing.contact == "none")
        check(5, failed.crossing.initial_pressure == {})
        check(6, failed.crossing.bind_height == UNKNOWN)
        check(7, engine.crossing.initial_pressure[b.name] == HART and engine.pressure_view(a, b) == UNKNOWN)
        check(8, weich.crossing.initial_pressure[wb.name] == WEICH and weich.pressure_view(wa, wb) == UNKNOWN)
        check(9, set(engine.crossing.bind_position.values()) == {UNKNOWN})
        check(10, not hasattr(engine.crossing, "leverage"))

        # 11-21: public, independent, deterministic authored height.
        check(11, BIND_HEIGHTS == (UPPER, LOWER, UNKNOWN))
        public = engine.public_crossing_state(a)
        check(12, public["bind_height"] == UPPER and "initial_pressure" not in public)
        check(13, not hasattr(engine.crossing, "height_modifier"))
        before_height = engine.crossing.bind_height
        engine.crossing.measure = "close"
        check(14, engine.crossing.bind_height == before_height)
        engine.crossing.contact_zone = {a.name: "hiltward", b.name: "pointward"}
        check(15, engine.crossing.bind_height == before_height)
        check(16, engine.crossing.bind_height == UPPER)
        lower, la, lb, _ = successful_cross(pressure=HART, geometry=LOWER_SETTING_ASIDE)
        check(17, lower.crossing.bind_height == LOWER)
        pflug, _, _, _ = successful_cross(
            pressure=HART,
            geometry="unclassified",
            defender_guard="pflug",
            attack_kind="low-line-thrust",
            descending=False,
        )
        check(18, pflug.crossing.bind_height == UNKNOWN)
        ochs, _, _, _ = successful_cross(
            pressure=HART,
            geometry="unclassified",
            defender_guard="ochs",
            attack_kind="descending-cut",
            descending=True,
        )
        check(19, ochs.crossing.bind_height == UNKNOWN)
        unknown, ua, ub, _ = successful_cross(pressure=WEICH, geometry="unclassified")
        check(20, unknown.crossing.bind_height == UNKNOWN)
        heights = [successful_cross(pressure=HART, geometry="unclassified")[0].crossing.bind_height for _ in range(3)]
        check(21, heights == [UNKNOWN, UNKNOWN, UNKNOWN])

        # 22-26: narrow insertion window and no action refresh.
        check(22, engine.rejoinder_open and engine.rejoinder_actor == a.name)
        za = Fighter("ZA")
        zb = Fighter("ZB", known_plays={"Zornhau-Ort"})
        zorn = ProvisionalLongswordEngine([za, zb])
        zattack = zorn.declare_attack(za, zb, "descending-cut", descending=True)
        zroll = zorn.roll_pending_attack((7,)).roll
        zorn.zornhau(zb, zroll, (4,))
        check(23, not zorn.rejoinder_open)
        check(24, not a.action_available and not b.action_available)
        arbitrary_before = len(engine.learned_chain)
        check(25, not engine.attempt_attacker_continuation(a, "Nachreisen") and len(engine.learned_chain) == arbitrary_before)
        check(26, engine.decline_bind_rejoinder(a) and not engine.rejoinder_open)

        # 27-35: F1 ordinary use and Zornhau compatibility.
        fuhlen, f_a, f_b, _ = successful_cross(pressure=HART, attacker_plays={FUHLEN})
        f_action = f_a.action_available
        f_chain = len(fuhlen.learned_chain)
        f_spiritus = f_a.spiritus
        check(27, fuhlen.buy_fuhlen(f_a) == HART and f_a.spiritus == f_spiritus - 1)
        check(28, f_a.action_available == f_action)
        check(29, len(fuhlen.learned_chain) == f_chain)
        check(30, fuhlen.pressure_view(f_a, f_b) == HART)
        f_weak, fw_a, fw_b, _ = successful_cross(pressure=WEICH, attacker_plays={FUHLEN})
        check(31, f_weak.buy_fuhlen(fw_a) == WEICH and f_weak.pressure_view(fw_a, fw_b) == WEICH)
        check(32, f_weak.buy_fuhlen(fw_a) is None)
        f_weak.decline_bind_rejoinder(fw_a)
        check(33, f_weak.pressure_view(fw_a, fw_b) == UNKNOWN)
        check(34, fuhlen.crossing.bind_initiative is None)
        zorn.fighters["ZA"].known_plays.add(FUHLEN)
        check(35, zorn.bind_view(zorn.fighters["ZA"]) in {"favored", "unfavored"})

        # 36-53: paired repertoire, correct Boon, wrong hard failure.
        d, d_a, d_b, _ = successful_cross(pressure=HART, attacker_plays={PAIRED_PLAY})
        d_action = d_a.action_available
        d_spiritus = d_a.spiritus
        d_chain = len(d.learned_chain)
        check(36, "Duplieren" in d.rejoinder_options(d_a))
        d_decl = d.declare_bind_rejoinder(d_a, "Duplieren")
        check(37, d_decl.legal and d_a.spiritus == d_spiritus - 2)
        check(38, len(d.learned_chain) == d_chain + 1)
        d_res = d.resolve_bind_rejoinder((12, 4), (3,))
        check(39, d_res.roll is not None and d_res.roll.modifier == "boon" and d_res.damage == 4)

        wrong_d, wd_a, _, _ = successful_cross(pressure=WEICH, attacker_plays={PAIRED_PLAY})
        wd_s = wd_a.spiritus
        wd_decl = wrong_d.declare_bind_rejoinder(wd_a, "Duplieren")
        check(40, wd_decl.legal and not wd_decl.success and wd_a.spiritus == wd_s - 2)
        check(41, wd_decl.roll is None)
        check(42, wd_decl.damage == 0)
        check(43, wd_decl.damage == 0 and wrong_d.other(wd_a).hp == 8)
        check(44, not hasattr(wd_decl, "response_restriction"))

        m, m_a, _, _ = successful_cross(pressure=WEICH, attacker_plays={PAIRED_PLAY})
        m_s, m_chain, m_action = m_a.spiritus, len(m.learned_chain), m_a.action_available
        check(45, "Mutieren" in m.rejoinder_options(m_a))
        m_decl = m.declare_bind_rejoinder(m_a, "Mutieren")
        check(46, m_a.spiritus == m_s - 2)
        check(47, len(m.learned_chain) == m_chain + 1)
        check(48, m.pending_bind_attack is not None and m.pending_bind_attack.kind == "thrust")
        wrong_m, wm_a, _, _ = successful_cross(pressure=HART, attacker_plays={PAIRED_PLAY})
        wm_decl = wrong_m.declare_bind_rejoinder(wm_a, "Mutieren")
        check(49, wm_decl.legal and not wm_decl.success)
        check(50, wm_decl.roll is None)
        check(51, wm_decl.damage == 0)
        check(52, m.crossing.retained and m_a.point_threat == "threatening")
        m_res = m.resolve_bind_rejoinder((12, 4), (3, 6))
        check(53, m_res.roll is not None and m_res.roll.modifier == "boon" and m_res.damage == 4)
        check(37, d_a.action_available == d_action)
        check(46, m_a.action_available == m_action)

        # 54-58: phase expiry and initiative assignment.
        dh, dh_a, _, _ = successful_cross(pressure=HART)
        check(54, dh.decline_bind_rejoinder(dh_a) and dh.crossing.bind_initiative == dh_a.name)
        dw, dw_a, dw_b, _ = successful_cross(pressure=WEICH)
        check(55, dw.decline_bind_rejoinder(dw_a) and dw.crossing.bind_initiative == dw_b.name)
        check(56, set(dw.crossing.initial_pressure.values()) == {UNKNOWN})
        check(57, not ({HART, WEICH} & set(d.crossing.initial_pressure.values())))
        check(58, set(lower.crossing.initial_pressure.values()) <= {HART, UNKNOWN})

        # 59-66: sequencing-only opportunity and finite pass.
        check(59, not hasattr(dw.crossing, "initiative_owner_exclusive"))
        check(60, not hasattr(dw.crossing, "initiative_modifier"))
        pass_action, pass_s, pass_chain = dw_b.action_available, dw_b.spiritus, len(dw.learned_chain)
        check(61, dw.pass_bind_initiative(dw_b))
        check(62, (dw_b.action_available, dw_b.spiritus, len(dw.learned_chain)) == (pass_action, pass_s, pass_chain))
        check(63, dw.crossing.bind_initiative == dw_a.name)
        one_known, ok_a, ok_b, _ = successful_cross(
            pressure=WEICH,
            geometry=UPPER_CROSS,
            attacker_plays={"Winden"},
        )
        one_known.decline_bind_rejoinder(ok_a)
        check(64, one_known.pass_bind_initiative(ok_b) and one_known.upper_winding_legal(ok_a))
        check(65, dw.pass_bind_initiative(dw_a) and dw.crossing.contact == "none")
        check(66, dw.consecutive_bind_passes == 0)

        # 67-83: Upper Winding declaration, hit, miss, transfer.
        upper, up_a, _, _ = successful_cross(
            pressure=HART, geometry=UPPER_CROSS, attacker_plays={"Winden"}
        )
        upper.decline_bind_rejoinder(up_a)
        check(67, upper.upper_winding_legal(up_a))
        check(68, upper.crossing.bind_initiative == up_a.name)
        check(69, upper.crossing.contact == "crossing")
        check(70, upper.crossing.bind_height == UPPER)
        up_s, up_chain, up_action = up_a.spiritus, len(upper.learned_chain), up_a.action_available
        up_decl = upper.declare_upper_winding(up_a)
        check(71, up_a.spiritus == up_s - 2)
        check(72, len(upper.learned_chain) == up_chain + 1)
        check(73, up_a.action_available == up_action)
        check(74, up_a.guard == "ochs")
        check(75, up_a.point_threat == "threatening")
        check(76, upper.pending_winding is not None and upper.pending_winding.accuracy == "normal")
        up_hit = upper.resolve_upper_winding((4,), (6,))
        check(77, up_hit.damage == 7)
        check(78, up_hit.success and upper.crossing.contact == "none")

        upper_miss, um_a, um_b, _ = successful_cross(
            pressure=HART, geometry=UPPER_CROSS, attacker_plays={"Winden"}
        )
        upper_miss.decline_bind_rejoinder(um_a)
        upper_miss.declare_upper_winding(um_a)
        um = upper_miss.resolve_upper_winding((20,))
        check(79, not um.success and um.damage == 0)
        check(80, upper_miss.crossing.contact == "crossing")
        check(81, upper_miss.crossing.bind_height == UPPER)
        check(82, um_a.guard == "ochs" and um_a.point_threat == "threatening")
        check(83, upper_miss.crossing.bind_initiative == um_b.name)

        # 84-102: Lower Winding and fixed L2 transition.
        low, low_a, low_b, _ = successful_cross(
            pressure=HART,
            geometry=LOWER_SETTING_ASIDE,
            attacker_plays={"Winden"},
        )
        low.decline_bind_rejoinder(low_a)
        check(84, low.lower_winding_legal(low_a))
        check(85, low.crossing.bind_initiative == low_a.name)
        check(86, low.crossing.contact == "crossing")
        check(87, low.crossing.bind_height == LOWER)
        low_s, low_chain, low_action = low_a.spiritus, len(low.learned_chain), low_a.action_available
        low.declare_lower_winding(low_a)
        check(88, low_a.spiritus == low_s - 2)
        check(89, len(low.learned_chain) == low_chain + 1)
        check(90, low_a.action_available == low_action)
        check(91, low_a.guard == "pflug")
        check(92, low_a.point_threat == "threatening")
        check(93, low.pending_winding is not None and low.pending_winding.kind == "thrust")
        low_hit = low.resolve_lower_winding((4,), (5,))
        check(94, low_hit.damage == 6)
        check(95, low_hit.success and low.crossing.contact == "none")

        low_miss, lm_a, lm_b, _ = successful_cross(
            pressure=HART,
            geometry=LOWER_SETTING_ASIDE,
            attacker_plays={"Winden"},
        )
        low_miss.decline_bind_rejoinder(lm_a)
        low_miss.declare_lower_winding(lm_a)
        lm = low_miss.resolve_lower_winding((20,))
        check(96, not lm.success and lm.damage == 0)
        check(97, low_miss.crossing.contact == "crossing")
        check(98, low_miss.crossing.bind_height == UPPER)
        check(99, lm_a.guard == "ochs")
        check(100, lm_a.point_threat == "threatening")
        check(101, low_miss.crossing.bind_initiative == lm_b.name)
        check(102, not low_miss.upper_winding_legal(lm_a))

        # 103-112: Unknown and chain accounting/cap.
        unknown.decline_bind_rejoinder(ua)
        ua.known_plays.add("Winden")
        check(103, not unknown.upper_winding_legal(ua))
        check(104, not unknown.lower_winding_legal(ua))
        check(105, set(unknown.continuation_options(ub, winden_variant="W2")) == {"pass", "Disengage"})
        check(106, set(unknown.crossing.bind_position.values()) == {UNKNOWN})
        check(107, len(d.learned_chain) == 1 and len(m.learned_chain) == 1)
        check(108, len(upper_miss.learned_chain) == 1 and len(low_miss.learned_chain) == 1)
        check(109, f_chain == len(fuhlen.learned_chain))

        chain, c_a, c_b, _ = successful_cross(
            pressure=HART,
            geometry=LOWER_SETTING_ASIDE,
            attacker_plays={"Winden"},
            defender_plays={"Winden"},
        )
        chain.decline_bind_rejoinder(c_a)
        chain.declare_lower_winding(c_a)
        chain.resolve_lower_winding((20,))
        chain.declare_upper_winding(c_b)
        chain.resolve_upper_winding((20,))
        chain.declare_upper_winding(c_a)
        check(110, len(chain.learned_chain) == 3)
        chain.resolve_upper_winding((20,))
        check(111, not chain.upper_winding_legal(c_b) and not chain.declare_upper_winding(c_b).legal)
        check(112, not c_a.action_available and not c_b.action_available)

        # 113-118: local Zornhau relation, Ort/Winden, point and D1.
        check(113, set(engine.crossing.bind_position.values()) == {UNKNOWN})
        check(114, set(zorn.crossing.bind_position.values()) == {"favored", "unfavored"})
        zholder = zb
        if zorn.crossing.bind_position[zholder.name] != "favored":
            zorn.crossing.bind_position = {zb.name: "favored", za.name: "unfavored"}
        check(115, zorn.ort(zholder, "O1", (3,)).success)
        zw_a = Fighter("A", known_plays={"Winden"})
        zw_b = Fighter("B")
        zw = ProvisionalLongswordEngine([zw_a, zw_b])
        zw.crossing = Crossing(
            contact="crossing",
            bind_position={zw_a.name: "unfavored", zw_b.name: "favored"},
            bind_initiative=zw_a.name,
            source="zornhau-local",
        )
        check(116, zw.winden(zw_a, "W1", (4,)).legal)
        check(117, zholder.point_threat == "threatening")
        check(118, not zorn.d1_window(zholder, zorn.pending_attack))

        # 119-129: protected mechanics and rejected additions.
        beat_a, beat_b = Fighter("A"), Fighter("B")
        beat = ProvisionalLongswordEngine([beat_a, beat_b])
        battack = beat.declare_attack(beat_a, beat_b, "cut")
        broll = beat.roll_pending_attack((4,)).roll
        bres = beat.basic_defence("Beat", beat_b, broll, (4,))
        check(119, bres.success and beat_a.guard == "open" and beat.crossing.contact == "none")
        check(120, beat.d1_window(beat_b, Attack(beat_a, beat_b, "cut")))

        ca, cb = Fighter("A"), Fighter("B")
        committed = ProvisionalLongswordEngine([ca, cb])
        committed.declare_attack(ca, cb, "cut", committed=True)
        check(121, committed.immediate_counter(cb, (4,)).legal)

        na, nb = Fighter("A"), Fighter("B", known_plays={"Nachreisen"})
        nach = ProvisionalLongswordEngine([na, nb])
        nach.declare_attack(na, nb, "cut", committed=True)
        nach.roll_pending_attack((20,))
        check(122, nach.recovery_nachreisen(nb, (4,)).legal)

        pa, pb = Fighter("A", guard="posta-di-donna"), Fighter("B")
        power = ProvisionalLongswordEngine([pa, pb])
        check(123, power.declare_power_attack(pa, pb) is not None)

        c2a, c2b = Fighter("A"), Fighter("B", known_plays={"Absetzen"})
        c2 = ProvisionalLongswordEngine([c2a, c2b])
        c2.declare_attack(c2a, c2b, "thrust", descending=False)
        c2.roll_pending_attack((4,))
        check(124, c2.compound_response("Absetzen", c2b, (4,)).legal)

        s2a, s2b = Fighter("A"), Fighter("B", known_plays={"Schielhau"})
        s2 = ProvisionalLongswordEngine([s2a, s2b])
        s2.declare_attack(s2a, s2b, "descending-cut", descending=True)
        s2.roll_pending_attack((4,))
        check(125, s2.compound_response("Schielhau", s2b, (4,)).legal)

        t1 = ProvisionalLongswordEngine([
            Fighter("A", guard="tutta-porta-di-ferro", known_plays={"Tutta Cover-to-Stretto"}),
            Fighter("B"),
        ])
        t1.crossing = Crossing(contact="crossing", measure="wide", bind_initiative="A")
        check(126, t1.tutta_cover_to_stretto(t1.fighters["A"]) and t1.crossing.measure == "close")
        check(127, not hasattr(ProvisionalLongswordEngine, "generic_close_purchase"))
        check(128, not hasattr(ProvisionalLongswordEngine, "counter_wind"))
        check(129, not hasattr(Crossing(), "leverage"))

        self.assertEqual(covered, set(range(1, 130)))

    def test_resource_chain_smoke_and_metadata_runtime_parity(self):
        for reserve in (0, 1, 2, 3, 4, 5, 8):
            engine, a, _, _ = successful_cross(
                pressure=HART,
                geometry=UPPER_CROSS,
                attacker_plays={"Winden"},
                attacker_spiritus=reserve,
            )
            engine.decline_bind_rejoinder(a)
            self.assertEqual(engine.upper_winding_legal(a), reserve >= 2)

        for used in (0, 1, 2, 3):
            engine, a, _, _ = successful_cross(
                pressure=HART,
                geometry=UPPER_CROSS,
                attacker_plays={"Winden"},
            )
            engine.learned_chain = [f"prior-{i}" for i in range(used)]
            engine.decline_bind_rejoinder(a)
            self.assertEqual(engine.upper_winding_legal(a), used < 3)

        governing = json.loads(
            (ROOT / "data/prototypes/longsword-governing-provisional-v0.1.yaml").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(governing["ordinary_bind_h3"]["winden"]["spiritus_cost"], 2)
        self.assertEqual(governing["ordinary_bind_h3"]["bind_height"]["values"], list(BIND_HEIGHTS))
        self.assertEqual(governing["ordinary_bind_h3"]["fuhlen"]["spiritus_cost"], 1)
        self.assertEqual(governing["learned_play_cap"], 3)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import unittest
from pathlib import Path

from simulations.shared.provisional_longsword import GOVERNING_BASELINE
from simulations.shared.provisional_longsword_engine import (
    DURCHWECHSELN_COST,
    HART,
    LEARNED_PLAY_CAP,
    PAIRED_PLAY,
    POMMEL_PLAY,
    SCHIELHAU_COST,
    T1_PLAY,
    UPPER_CROSS,
    WEICH,
    Attack,
    Crossing,
    Fighter,
    ProvisionalLongswordEngine,
    Resolution,
    RollResult,
)


ROOT = Path(__file__).resolve().parents[1]


def establish_s2(
    *,
    schielhau_roll: int = 4,
    attacker_spiritus: int = 8,
    defender_spiritus: int = 8,
    prior_chain: tuple[str, ...] = (),
    measure: str = "wide",
) -> tuple[ProvisionalLongswordEngine, Fighter, Fighter, Attack]:
    attacker = Fighter(
        "A",
        spiritus=attacker_spiritus,
        known_plays={"Durchwechseln"},
    )
    defender = Fighter(
        "B",
        spiritus=defender_spiritus,
        known_plays={"Schielhau"},
    )
    engine = ProvisionalLongswordEngine([attacker, defender])
    engine.crossing.measure = measure
    engine.learned_chain = list(prior_chain)
    attack = engine.declare_attack(
        attacker,
        defender,
        "descending-cut",
        descending=True,
    )
    assert attack is not None
    rolled = engine.roll_pending_attack((5,), (4,))
    assert rolled.success
    established = engine.establish_schielhau_s2(
        defender,
        (schielhau_roll,),
        (3,),
    )
    assert established.legal and established.success
    return engine, attacker, defender, attack


def resolve_s2(
    schielhau_roll: int,
    d1_roll: int,
) -> tuple[ProvisionalLongswordEngine, Fighter, Fighter, Attack]:
    engine, attacker, defender, attack = establish_s2(
        schielhau_roll=schielhau_roll
    )
    assert engine.declare_durchwechseln(attacker, defender, attack)
    result = engine.resolve_s2_durchwechseln(attacker, (d1_roll,), (3,))
    assert result.legal
    return engine, attacker, defender, attack


def generic_compound(
    name: str,
) -> tuple[ProvisionalLongswordEngine, Fighter, Fighter, Resolution]:
    attacker = Fighter("A")
    defender = Fighter("B", known_plays={name})
    engine = ProvisionalLongswordEngine([attacker, defender])
    attack = engine.declare_attack(
        attacker,
        defender,
        "descending-cut" if name == "Schielhau" else "thrust",
        descending=name == "Schielhau",
    )
    assert attack is not None
    assert engine.roll_pending_attack((5,), (3,)).success
    result = engine.compound_response(name, defender, (4,), (3,))
    assert result.legal and result.success
    return engine, attacker, defender, result


class S2SchielhauDurchwechselnGoverningTests(unittest.TestCase):
    def test_required_governing_assertions_001_086(self) -> None:
        covered: set[int] = set()

        def check(number: int, condition: bool) -> None:
            self.assertTrue(condition, f"S2 governing requirement {number}")
            covered.add(number)

        governing = json.loads(
            (ROOT / "data/prototypes/longsword-governing-provisional-v0.1.yaml")
            .read_text(encoding="utf-8")
        )
        register = (ROOT / "reports/governing-open-provisional.md").read_text(
            encoding="utf-8"
        )

        # 1-3: source and selection.
        check(1, governing["schielhau_durchwechseln"]["variant"] == "S2")
        check(2, GOVERNING_BASELINE["schielhau_durchwechseln"] == "S2")
        check(
            3,
            "Schielhau / Durchwechseln: S2." in register
            and "C2, and S2 retain their authored rules" in register,
        )

        # 4-10: authored window and interaction scope.
        window_engine, wa, wb, window_attack = establish_s2(schielhau_roll=6)
        check(4, window_engine.s2_window_open_for(wa))
        window = window_engine.s2_schielhau_window
        check(5, window is not None and window.established_roll.value == 6)
        check(
            6,
            window is not None
            and window.schielhau_actor is wb
            and window.durchwechseln_actor is wa
            and window.attack is window_attack,
        )
        check(7, window is not None and window.phase == "d1-window")

        unrelated = ProvisionalLongswordEngine([Fighter("A"), Fighter("B")])
        unrelated.declare_attack(unrelated.fighters["A"], unrelated.fighters["B"], "cut")
        check(8, unrelated.s2_schielhau_window is None)
        generic_schiel, _, _, _ = generic_compound("Schielhau")
        check(9, generic_schiel.s2_schielhau_window is None)
        window_engine.decline_s2_durchwechseln(wa)
        window_engine.finish_exchange()
        wa.action_available = True
        later = window_engine.declare_attack(wa, wb, "cut")
        check(10, later is not None and window_engine.s2_schielhau_window is None)

        # 11-13: exact roll retention.
        retention, ra, rb, retention_attack = establish_s2(schielhau_roll=7)
        retained = retention.s2_schielhau_window.established_roll
        check(11, retained.value == 7 and retained.rolls == (7,))
        check(11, retention.declare_durchwechseln(ra, rb, retention_attack))
        retention.resolve_s2_durchwechseln(ra, (9,), (3,))
        fresh_events = [e for e in retention.event_log if e.startswith("S2:D1-fresh-roll")]
        check(12, fresh_events == ["S2:D1-fresh-roll:value=9:success=true"])
        comparison_events = [e for e in retention.event_log if e.startswith("S2:comparison")]
        check(13, comparison_events == ["S2:comparison:established=7:fresh=9:winner=schielhau"])

        # 14-19: selected deterministic comparison.
        result = ProvisionalLongswordEngine.compare_s2_rolls
        check(14, result(RollResult(True, 4, (4,)), RollResult(True, 8, (8,))) == "schielhau")
        check(15, result(RollResult(True, 8, (8,)), RollResult(True, 4, (4,))) == "durchwechseln")
        check(16, result(RollResult(True, 5, (5,)), RollResult(True, 5, (5,))) == "schielhau")
        check(17, result(RollResult(True, 5, (5,)), RollResult(False, 20, (20,))) == "schielhau")
        check(18, result(RollResult(False, 20, (20,)), RollResult(True, 5, (5,))) == "durchwechseln")
        check(19, result(RollResult(False, 20, (20,)), RollResult(False, 19, (19,))) == "original-strike")

        # 20-28: actor, prerequisites, point timing, reserve and chain gates.
        gated, ga, gb, gated_attack = establish_s2()
        third = Fighter("C", known_plays={"Durchwechseln"})
        gated.fighters[third.name] = third
        third_s = third.spiritus
        check(20, not gated.declare_durchwechseln(third, gb, gated_attack) and third.spiritus == third_s)

        dead, da, _, dead_attack = establish_s2()
        da.hp = 0
        check(
            21,
            not dead.s2_window_open_for(da)
            and dead.s2_schielhau_window is None
            and dead_attack.cancelled
            and not dead.resolve_pending_attack().legal,
        )

        bad_a = Fighter("A", known_plays={"Durchwechseln"})
        bad_b = Fighter("B", known_plays={"Schielhau"})
        bad = ProvisionalLongswordEngine([bad_a, bad_b])
        bad.declare_attack(bad_a, bad_b, "thrust", descending=False)
        bad.roll_pending_attack((4,))
        check(22, not bad.establish_schielhau_s2(bad_b, (4,)).legal)

        prereq, pa, pb, prereq_attack = establish_s2()
        pa.known_plays.clear()
        check(23, not prereq.declare_durchwechseln(pa, pb, prereq_attack))

        point, pta, ptb, point_attack = establish_s2()
        before_point = ptb.point_threat
        point.declare_durchwechseln(pta, ptb, point_attack)
        point.resolve_s2_durchwechseln(pta, (8,))
        check(24, before_point == "not_threatening" and ptb.point_threat == "threatening")

        poor, poor_a, poor_b, poor_attack = establish_s2(attacker_spiritus=0)
        poor_before = poor_a.spiritus
        check(25, not poor.declare_durchwechseln(poor_a, poor_b, poor_attack))
        check(27, poor_a.spiritus == poor_before == 0)
        capped, cap_a, cap_b, cap_attack = establish_s2(prior_chain=("prior-1", "prior-2"))
        check(26, not capped.declare_durchwechseln(cap_a, cap_b, cap_attack))
        check(28, len(capped.learned_chain) == LEARNED_PLAY_CAP)

        # 29-33: already-governing layered cost and chain accounting.
        costs, ca, cb, costs_attack = establish_s2()
        check(29, cb.spiritus == 8 - SCHIELHAU_COST)
        ca_before = ca.spiritus
        costs.declare_durchwechseln(ca, cb, costs_attack)
        check(30, ca.spiritus == ca_before - DURCHWECHSELN_COST)
        costs.resolve_s2_durchwechseln(ca, (20,))
        check(31, ca.spiritus == ca_before - DURCHWECHSELN_COST)
        check(32, costs.learned_chain == ["Schielhau", "Durchwechseln"])
        check(33, cb.spiritus == 6 and costs.learned_chain.count("Schielhau") == 1)

        # 34-37: action economy.
        actions, aa, ab, actions_attack = establish_s2()
        check(34, not aa.action_available and not ab.action_available)
        actions.declare_durchwechseln(aa, ab, actions_attack)
        before_compare = (aa.action_available, ab.action_available)
        actions.resolve_s2_durchwechseln(aa, (8,))
        check(35, not aa.action_available and not ab.action_available)
        check(36, before_compare == (False, False))
        check(37, (aa.action_available, ab.action_available) == before_compare)

        # 38-43: Schielhau-win outcome.
        schiel, sa, sb, schiel_attack = resolve_s2(4, 8)
        check(38, any("S2:outcome:Schielhau-wins" in event for event in schiel.event_log))
        check(39, schiel_attack.cancelled and schiel_attack.kind == "descending-cut")
        check(40, sa.hp == 4 and sb.hp == 8)
        check(41, sb.point_threat == "threatening")
        check(42, schiel.crossing.contact == "none" and schiel.crossing.measure == "wide")
        check(43, schiel.pending_attack is schiel_attack and schiel_attack.phase == "cancelled")

        # 44-48: D1-win outcome.
        durch, dua, dub, durch_attack = resolve_s2(8, 4)
        check(44, any("S2:outcome:D1-wins" in event for event in durch.event_log))
        check(45, dua.hp == 8 and not any("Schielhau-wins" in e for e in durch.event_log))
        check(46, durch_attack.kind == "durchwechseln-thrust" and durch_attack.phase == "resolved" and dub.hp == 4)
        check(47, dua.point_threat == "threatening")
        check(48, durch.crossing.contact == "none" and durch.crossing.measure == "wide")

        # 49-51: explicit decline.
        decline, dec_a, _, decline_attack = establish_s2()
        declined = decline.decline_s2_durchwechseln(dec_a)
        check(49, declined.legal and declined.success)
        check(50, decline_attack.cancelled and dec_a.hp == 4)
        check(51, decline.s2_schielhau_window is None)

        # 52-57: all reachable cleanup routes and stale-state protection.
        check(52, schiel.s2_schielhau_window is None)
        check(53, durch.s2_schielhau_window is None)
        fail_a = Fighter("A", known_plays={"Durchwechseln"})
        fail_b = Fighter("B", known_plays={"Schielhau"})
        failure = ProvisionalLongswordEngine([fail_a, fail_b])
        failure.declare_attack(fail_a, fail_b, "descending-cut", descending=True)
        failure.roll_pending_attack((4,), (4,))
        failed_schiel = failure.establish_schielhau_s2(fail_b, (20,))
        check(54, failed_schiel.legal and not failed_schiel.success and failure.s2_schielhau_window is None)
        death, death_a, death_b, _ = establish_s2()
        death_b.hp = 0
        check(55, not death.s2_window_open_for(death_a) and death.s2_schielhau_window is None)
        expiry, expiry_a, _, _ = establish_s2()
        expiry.finish_exchange()
        check(56, expiry.s2_schielhau_window is None and expiry.pending_attack is None)
        durch.finish_exchange()
        dua.action_available = True
        dub.action_available = True
        new_attack = durch.declare_attack(dua, dub, "cut")
        check(57, new_attack is not None and durch.s2_schielhau_window is None)

        # 58-62: legible event sequence and no generic second Schielhau roll.
        events, ea, eb, events_attack = establish_s2(schielhau_roll=6)
        events.declare_durchwechseln(ea, eb, events_attack)
        events.resolve_s2_durchwechseln(ea, (9,))
        check(58, any(e.startswith("S2:Schielhau-established") for e in events.event_log))
        check(59, any(e.startswith("S2:D1-fresh-roll") for e in events.event_log))
        check(60, any(e.startswith("S2:comparison") for e in events.event_log))
        labels = (
            "S2:Schielhau-declared",
            "S2:Schielhau-established",
            "S2:D1-window-open",
            "S2:D1-declared",
            "S2:D1-fresh-roll",
            "S2:comparison",
            "S2:outcome:Schielhau-wins",
            "S2:cleanup:resolved-Schielhau",
        )
        positions = [next(i for i, e in enumerate(events.event_log) if e.startswith(label)) for label in labels]
        check(61, positions == sorted(positions))
        check(62, events.event_log.count("roll:pending-attack") == 1 and not any("C2 succeeded" in e for e in events.event_log))

        # 63-66: generic C2 remains independent.
        generic, gen_a, gen_b, generic_result = generic_compound("Schielhau")
        check(63, gen_a.hp == 4 and gen_b.spiritus == 6)
        check(64, generic.s2_schielhau_window is None and generic_result.roll.value == 4)
        absetzen, abs_a, _, _ = generic_compound("Absetzen")
        check(65, abs_a.hp == 4 and absetzen.crossing.contact == "crossing")
        scambiar, sci_a, _, _ = generic_compound("Scambiar di Punta")
        check(66, sci_a.hp == 4 and scambiar.crossing.contact == "crossing")

        # 67-69: ordinary D1 and its point gate remain unchanged.
        ord_a = Fighter("A", known_plays={"Durchwechseln"})
        ord_b = Fighter("B")
        ordinary = ProvisionalLongswordEngine([ord_a, ord_b])
        ordinary_attack = ordinary.declare_attack(ord_a, ord_b, "cut")
        assert ordinary_attack is not None
        ordinary.roll_pending_attack((5,), (3,))
        check(67, ordinary.declare_durchwechseln(ord_a, ord_b, ordinary_attack) and ordinary_attack.kind == "durchwechseln-thrust")
        denied = ProvisionalLongswordEngine([Fighter("A", known_plays={"Durchwechseln"}), Fighter("B", point_threat="threatening")])
        denied_attack = Attack(denied.fighters["A"], denied.fighters["B"], "cut")
        check(68, not denied.declare_durchwechseln(denied.fighters["A"], denied.fighters["B"], denied_attack))
        check(69, not denied.d1_window(denied.fighters["B"], denied_attack))

        # 70-74: H3 protected control.
        h3a = Fighter("A", known_plays={"Fühlen", PAIRED_PLAY, "Winden"})
        h3b = Fighter("B")
        h3 = ProvisionalLongswordEngine([h3a, h3b])
        h3_attack = h3.declare_attack(h3a, h3b, "descending-cut", descending=True)
        assert h3_attack is not None
        h3_roll = h3.roll_pending_attack((5,)).roll
        h3.declare_basic_cross(h3b, HART, UPPER_CROSS)
        h3.basic_defence("Cross", h3b, h3_roll, (6, 18))
        check(70, set(h3.crossing.bind_position.values()) == {"unknown"})
        check(71, h3.crossing.initial_pressure[h3b.name] == HART)
        h3_s = h3a.spiritus
        check(72, h3.buy_fuhlen(h3a) == HART and h3a.spiritus == h3_s - 1)
        dm = h3.declare_bind_rejoinder(h3a, "Duplieren")
        check(73, dm.legal and h3.pending_bind_attack is not None)
        h3.resolve_bind_rejoinder((4, 18), (3,))
        wind_a = Fighter("A", known_plays={"Winden"})
        wind_b = Fighter("B")
        wind = ProvisionalLongswordEngine([wind_a, wind_b])
        wind.crossing = Crossing(contact="crossing", bind_height="upper", bind_initiative="A", source="ordinary-basic-cross")
        check(74, wind.declare_upper_winding(wind_a).legal and wind_a.spiritus == 6)

        # 75-77: E1, Pommel, and Close opportunity remain unchanged.
        t1a = Fighter("A", guard="tutta-porta-di-ferro", known_plays={T1_PLAY, POMMEL_PLAY})
        t1b = Fighter("B")
        t1 = ProvisionalLongswordEngine([t1a, t1b])
        t1_attack = t1.declare_attack(t1b, t1a, "cut", descending=True)
        assert t1_attack is not None
        t1_roll = t1.roll_pending_attack((4,)).roll
        t1.declare_basic_cross(t1a, WEICH, UPPER_CROSS)
        t1.basic_defence("Cross", t1a, t1_roll, (4,))
        check(75, t1.declare_t1(t1a) and t1.crossing.measure == "close")
        check(77, t1.crossing.bind_initiative == t1a.name)
        check(76, t1.declare_pommel(t1a).legal)

        # 78-80: Zornhau-local relation, Ort, and Winding remain local.
        za = Fighter("A")
        zb = Fighter("B", known_plays={"Zornhau-Ort", "Winden", "Fühlen"})
        zorn = ProvisionalLongswordEngine([za, zb])
        zattack = zorn.declare_attack(za, zb, "descending-cut", descending=True)
        assert zattack is not None
        zroll = zorn.roll_pending_attack((7,)).roll
        zorn.zornhau(zb, zroll, (4,))
        check(78, set(zorn.crossing.bind_position.values()) == {"favored", "unfavored"})
        check(79, zorn.ort(zb, "O1", (3,)).success)
        check(80, zorn.winden(zb, "W2", (4,), (3,)).legal)

        # 81-86: no new generic systems, prices, or H3 redesign.
        check(81, not hasattr(ProvisionalLongswordEngine, "generic_effect_operator"))
        check(82, not hasattr(Crossing(), "leverage"))
        check(83, not hasattr(ProvisionalLongswordEngine, "generic_response_subsystem"))
        check(84, SCHIELHAU_COST == governing["current_two_effect_compounds"]["spiritus_cost"] == 2)
        check(85, DURCHWECHSELN_COST == governing["durchwechseln"]["spiritus_cost"] == 1)
        check(86, governing["ordinary_bind_h3"]["status"].startswith("PROJECT-ADJUDICATED"))

        self.assertEqual(covered, set(range(1, 87)))

    def test_forced_roll_sequences_a_through_l(self) -> None:
        with self.subTest("A Schielhau lower success"):
            engine, a, b, _ = resolve_s2(4, 8)
            self.assertEqual((a.hp, b.hp), (4, 8))

        with self.subTest("B D1 lower success"):
            engine, a, b, attack = resolve_s2(8, 4)
            self.assertEqual((a.hp, b.hp), (8, 4))
            self.assertEqual(attack.kind, "durchwechseln-thrust")

        with self.subTest("C tie"):
            engine, a, b, _ = resolve_s2(5, 5)
            self.assertEqual((a.hp, b.hp), (4, 8))

        with self.subTest("D D1 fails"):
            engine, a, b, _ = resolve_s2(5, 20)
            self.assertEqual((a.hp, b.hp), (4, 8))

        with self.subTest("E helper Schielhau fail D1 success"):
            self.assertEqual(
                ProvisionalLongswordEngine.compare_s2_rolls(
                    RollResult(False, 20, (20,)), RollResult(True, 5, (5,))
                ),
                "durchwechseln",
            )

        with self.subTest("F helper both fail"):
            self.assertEqual(
                ProvisionalLongswordEngine.compare_s2_rolls(
                    RollResult(False, 20, (20,)), RollResult(False, 19, (19,))
                ),
                "original-strike",
            )

        with self.subTest("G D1 declined"):
            engine, a, _, attack = establish_s2()
            self.assertTrue(engine.decline_s2_durchwechseln(a).success)
            self.assertTrue(attack.cancelled)

        with self.subTest("H insufficient Spiritus"):
            engine, a, b, attack = establish_s2(attacker_spiritus=0)
            self.assertFalse(engine.declare_durchwechseln(a, b, attack))
            self.assertEqual(a.spiritus, 0)
            self.assertTrue(engine.decline_s2_durchwechseln(a).success)

        with self.subTest("I chain cap"):
            engine, a, b, attack = establish_s2(prior_chain=("one", "two"))
            self.assertFalse(engine.declare_durchwechseln(a, b, attack))
            self.assertEqual(len(engine.learned_chain), 3)

        with self.subTest("J point-threat edge"):
            engine, a, b, attack = establish_s2()
            self.assertEqual(b.point_threat, "not_threatening")
            self.assertTrue(engine.declare_durchwechseln(a, b, attack))
            engine.resolve_s2_durchwechseln(a, (20,))
            self.assertEqual(b.point_threat, "threatening")

        with self.subTest("K generic C2 control"):
            engine, _, _, result = generic_compound("Schielhau")
            self.assertIsNone(engine.s2_schielhau_window)
            self.assertEqual(result.roll.value, 4)

        with self.subTest("L ordinary D1 control"):
            a = Fighter("A", known_plays={"Durchwechseln"})
            b = Fighter("B")
            engine = ProvisionalLongswordEngine([a, b])
            attack = engine.declare_attack(a, b, "cut")
            assert attack is not None
            engine.roll_pending_attack((4,))
            self.assertTrue(engine.declare_durchwechseln(a, b, attack))
            self.assertEqual(attack.phase, "declared")

        with self.subTest("terminal cancellation invalidates the window"):
            engine, a, _, attack = establish_s2()
            attack.cancelled = True
            attack.phase = "cancelled"
            self.assertFalse(engine.s2_window_open_for(a))
            self.assertIsNone(engine.s2_schielhau_window)

        with self.subTest("new attack expires decline window through Schielhau"):
            engine, a, b, _ = establish_s2()
            a.action_available = True
            later = engine.declare_attack(a, b, "cut")
            self.assertIsNotNone(later)
            self.assertEqual(a.hp, 4)
            self.assertIsNone(engine.s2_schielhau_window)

        with self.subTest("incomplete declared D1 cannot leak past exchange end"):
            engine, a, b, attack = establish_s2()
            self.assertTrue(engine.declare_durchwechseln(a, b, attack))
            engine.finish_exchange()
            self.assertIsNone(engine.s2_schielhau_window)
            self.assertIsNone(engine.pending_attack)

    def test_integrated_smoke_s1_through_s7(self) -> None:
        # S1: normal generic C2 Schielhau.
        generic, _, _, _ = generic_compound("Schielhau")
        self.assertIsNone(generic.s2_schielhau_window)

        # S2: established Schielhau -> D1 comparison.
        s2, _, _, _ = resolve_s2(8, 4)
        self.assertIsNone(s2.s2_schielhau_window)

        # S3: explicit decline.
        declined, actor, _, _ = establish_s2()
        declined.decline_s2_durchwechseln(actor)
        self.assertIsNone(declined.s2_schielhau_window)

        # S4-S5: ordinary D1 and point denial.
        oa = Fighter("A", known_plays={"Durchwechseln"})
        ob = Fighter("B")
        ordinary = ProvisionalLongswordEngine([oa, ob])
        ordinary_attack = ordinary.declare_attack(oa, ob, "cut")
        assert ordinary_attack is not None
        ordinary.roll_pending_attack((4,))
        self.assertTrue(ordinary.declare_durchwechseln(oa, ob, ordinary_attack))
        ob.point_threat = "threatening"
        self.assertFalse(ordinary.d1_window(ob, ordinary_attack))

        # S6: ordinary H3 after a completed S2 exchange.
        h3, ha, hb, _ = resolve_s2(4, 8)
        h3.finish_exchange()
        ha.hp = hb.hp = 8
        ha.action_available = hb.action_available = True
        follow = h3.declare_attack(ha, hb, "descending-cut", descending=True)
        assert follow is not None
        follow_roll = h3.roll_pending_attack((4,)).roll
        self.assertTrue(h3.declare_basic_cross(hb, HART, UPPER_CROSS))
        self.assertTrue(h3.basic_defence("Cross", hb, follow_roll, (4, 18)).success)
        self.assertIsNone(h3.s2_schielhau_window)

        # S7: T1/Close after a completed S2 exchange in a fresh bounded route.
        ta = Fighter("A", guard="tutta-porta-di-ferro", known_plays={T1_PLAY})
        tb = Fighter("B")
        close = ProvisionalLongswordEngine([ta, tb])
        close_attack = close.declare_attack(tb, ta, "cut", descending=True)
        assert close_attack is not None
        close_roll = close.roll_pending_attack((4,)).roll
        close.declare_basic_cross(ta, WEICH, UPPER_CROSS)
        close.basic_defence("Cross", ta, close_roll, (4,))
        self.assertTrue(close.declare_t1(ta))
        self.assertEqual(close.crossing.measure, "close")
        self.assertIsNone(close.s2_schielhau_window)

    def test_metadata_runtime_parity_and_no_split_brain(self) -> None:
        mapping = json.loads(
            (ROOT / "data/audits/longsword-vertical-slice-mechanical-mapping-v0.1.yaml")
            .read_text(encoding="utf-8")
        )
        state_model = json.loads(
            (ROOT / "data/prototypes/longsword-durchwechseln-schielhau-state-model-v0.3.yaml")
            .read_text(encoding="utf-8")
        )
        s2 = next(item for item in mapping["techniques"] if item["id"] == "schielhau-s2")
        comparison = state_model["rules"]["schielhau_resolution_variants"]["S2"]
        self.assertIn("reuse the successful schielhau d20 result", comparison.lower())
        self.assertIn("reuse the successful schielhau d20 result", s2["test"][1]["text"].lower())
        self.assertEqual(GOVERNING_BASELINE["schielhau_durchwechseln"], "S2")
        self.assertTrue(hasattr(ProvisionalLongswordEngine, "establish_schielhau_s2"))
        self.assertTrue(hasattr(ProvisionalLongswordEngine, "resolve_s2_durchwechseln"))
        self.assertEqual(SCHIELHAU_COST, 2)
        self.assertEqual(DURCHWECHSELN_COST, 1)


if __name__ == "__main__":
    unittest.main()

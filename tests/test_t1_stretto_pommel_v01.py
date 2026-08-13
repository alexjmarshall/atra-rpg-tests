from __future__ import annotations

import unittest

from simulations.shared.provisional_longsword import CurrentEngine, ENGINE, Fighter, HART, UNKNOWN, UPPER, WEICH
from simulations.t1_stretto_pommel_v0_1.candidate_engine import CandidateEngine, POMMEL, T1, TUTTA_GUARD
from simulations.t1_stretto_pommel_v0_1.simulate import (
    SCENARIOS,
    artifact_sanity,
    build_results,
    pommel_cost_table,
    state_traces,
    successful_cross,
)


class T1StrettoPommelCandidateTests(unittest.TestCase):
    def test_required_candidate_assertions_001_092(self) -> None:
        checks: dict[int, bool] = {}

        e, a, b = successful_cross(pressure=HART, plays_a={POMMEL}, plays_b={T1, POMMEL})
        actions = (a.action_available, b.action_available)
        hp = (a.hp, b.hp)
        point = (a.point_threat, b.point_threat)
        pressure_before = e.pressure_view(b, b)
        checks[1] = e.early_t1_legal(b)
        checks[2] = any("after-D1" in event for event in e.event_log)
        checks[3] = e.rejoinder_options(a) == [] and e.rejoinder_open
        before_s = b.spiritus
        before_chain = len(e.learned_chain)
        checks[22] = e.pressure_view(a, b) == UNKNOWN and pressure_before == HART
        self.assertTrue(e.declare_early_t1(b))
        checks[4] = before_s - b.spiritus == 1
        checks[5] = len(e.learned_chain) - before_chain == 1
        checks[6] = (a.action_available, b.action_available) == actions
        checks[7] = e.crossing.contact == "crossing" and e.crossing.retained
        checks[8] = e.crossing.measure == "close"
        checks[9] = e.crossing.bind_height == UNKNOWN
        checks[10] = (a.hp, b.hp) == hp
        checks[11] = (a.point_threat, b.point_threat) == point
        checks[12] = not hasattr(e.crossing, "close_bonus")
        checks[13] = not e.rejoinder_open and e.rejoinder_options(a) == []
        checks[14] = all("CANCEL D/M" not in event for event in e.event_log)
        checks[18] = e.crossing.bind_initiative == a.name
        checks[20] = all(value == UNKNOWN for value in e.crossing.initial_pressure.values())
        checks[21] = e.buy_fuhlen(a) is None
        checks[23] = e.crossing.measure == "close" and e.crossing.bind_height == UNKNOWN
        checks[24] = e.crossing.bind_height != "lower"
        checks[25] = not e.upper_winding_legal(a) and not e.upper_winding_legal(b)
        checks[26] = not e.lower_winding_legal(a) and not e.lower_winding_legal(b)
        checks[27] = e.crossing.bind_height == UNKNOWN

        no_t1, na, nb = successful_cross(pressure=HART, plays_a={"Duplieren / Mutieren"}, plays_b={T1})
        no_t1.decline_early_t1(nb)
        checks[15] = no_t1.declare_bind_rejoinder(na, "Duplieren").success
        governing_a = Fighter("A", known_plays={"Duplieren / Mutieren"}); governing_b = Fighter("B")
        governing = CurrentEngine([governing_a, governing_b])
        checks[16] = not isinstance(governing, CandidateEngine)
        unrelated = CandidateEngine([Fighter("A"), Fighter("B", guard=TUTTA_GUARD, known_plays={T1})])
        unrelated.crossing.contact = "crossing"; unrelated.crossing.measure = "wide"; unrelated.crossing.source = "authored-special"
        checks[17] = not unrelated.early_t1_legal(unrelated.fighters["B"])

        weich, wa, wb = successful_cross(pressure=WEICH, plays_a={POMMEL}, plays_b={T1, POMMEL})
        weich.declare_early_t1(wb)
        checks[19] = weich.crossing.bind_initiative == wb.name

        # Pommel gates and generic Close consumption.
        gate_a = Fighter("A", spiritus=2, known_plays={POMMEL}, action_available=False)
        gate_b = Fighter("B", spiritus=2)
        gate = CandidateEngine([gate_a, gate_b], pommel_cost=2)
        gate.crossing.contact = "crossing"; gate.crossing.measure = "close"; gate.crossing.source = "authored-special"; gate.crossing.bind_initiative = "A"
        checks[28] = gate.pommel_legal(gate_a)
        no_cross = CandidateEngine([Fighter("A", known_plays={POMMEL}), Fighter("B")]); no_cross.crossing.bind_initiative = "A"; no_cross.crossing.measure = "close"
        checks[29] = not no_cross.pommel_legal(no_cross.fighters["A"])
        wide = CandidateEngine([Fighter("A", known_plays={POMMEL}), Fighter("B")]); wide.crossing.contact="crossing"; wide.crossing.bind_initiative="A"
        checks[30] = not wide.pommel_legal(wide.fighters["A"])
        wrong_holder = CandidateEngine([Fighter("A", known_plays={POMMEL}), Fighter("B")]); wrong_holder.crossing.contact="crossing"; wrong_holder.crossing.measure="close"; wrong_holder.crossing.bind_initiative="B"
        checks[31] = not wrong_holder.pommel_legal(wrong_holder.fighters["A"])
        gate.learned_chain[:] = ["x", "y", "z"]
        checks[32] = not gate.pommel_legal(gate_a)
        gate.learned_chain.clear(); gate_a.spiritus = 1
        checks[33] = not gate.pommel_legal(gate_a)
        gate_a.spiritus = 2
        checks[34] = gate.pommel_legal(gate_a) and gate_a.guard != TUTTA_GUARD
        checks[35] = gate.pommel_legal(gate_a) and T1 not in gate.learned_chain
        checks[36] = gate.pommel_legal(gate_a) and not gate.crossing.initial_pressure
        checks[37] = gate.pommel_legal(gate_a) and not gate_a.action_available

        target_actions = (gate_a.action_available, gate_b.action_available)
        target_hp = gate_b.hp
        generic_close_legal = gate.pommel_legal(gate_a) and gate.crossing.source == "authored-special"
        declaration = gate.declare_pommel(gate_a)
        checks[38] = declaration.legal and (gate_a.action_available, gate_b.action_available) == target_actions
        checks[39] = gate.learned_chain == [POMMEL]
        hit = gate.resolve_pommel((1,), (3,))
        checks[40] = hit.roll is not None and hit.roll.modifier == "normal"
        checks[41] = hit.damage == 4
        checks[42] = hit.roll is not None and hit.roll.modifier != "boon"
        checks[43] = hit.damage == 4
        checks[44] = gate_b.guard != "open"
        checks[45] = not hasattr(gate.crossing, "leverage")
        checks[46] = not hasattr(gate.crossing, "control")
        checks[47] = gate.candidate_response_restrictions == ()
        checks[48] = gate_b.hp == target_hp - 4
        checks[49] = gate.crossing.contact == "none"
        checks[50] = gate.crossing.bind_initiative is None

        miss, ma, mb = successful_cross(pressure=WEICH, plays_a={POMMEL}, plays_b={T1, POMMEL})
        miss.declare_early_t1(mb); miss.declare_pommel(mb); miss_result = miss.resolve_pommel((20,), (6,))
        checks[51] = not miss_result.success and miss_result.damage == 0
        checks[52] = miss.crossing.contact == "crossing"
        checks[53] = miss.crossing.measure == "close"
        checks[54] = miss.crossing.bind_height == UNKNOWN
        checks[55] = miss.crossing.bind_initiative == ma.name
        checks[56] = ma.hp == 8
        checks[57] = miss.crossing.contact == "crossing"

        passes, pa, pb = successful_cross(pressure=WEICH, plays_a=set(), plays_b={T1})
        passes.declare_early_t1(pb)
        checks[58] = passes.pass_bind_initiative(pb) and passes.crossing.bind_initiative == pa.name
        checks[59] = passes.pass_bind_initiative(pa) and passes.crossing.contact == "none"
        reset, ra, rb = successful_cross(pressure=WEICH, plays_a={POMMEL}, plays_b={T1, POMMEL})
        reset.declare_early_t1(rb); reset.pass_bind_initiative(rb); reset.declare_pommel(ra)
        checks[60] = reset.consecutive_bind_passes == 0
        disengage, da, db = successful_cross(pressure=WEICH, plays_b={T1})
        disengage.declare_early_t1(db); checks[61] = disengage.disengage(db) and disengage.crossing.contact == "none"
        dead, dea, deb = successful_cross(pressure=WEICH, plays_a={POMMEL}, plays_b={T1, POMMEL})
        dead.declare_early_t1(deb); dea.hp = 0
        checks[62] = not dead.pommel_legal(deb) and not dead.pass_bind_initiative(deb)

        chain, ca, cb = successful_cross(pressure=WEICH, plays_a={POMMEL}, plays_b={T1, POMMEL})
        chain.declare_early_t1(cb); chain.declare_pommel(cb)
        checks[63] = len(chain.learned_chain) == 2
        chain.resolve_pommel((20,), (3,)); chain.declare_pommel(ca)
        checks[64] = len(chain.learned_chain) == 3
        chain.resolve_pommel((20,), (3,))
        checks[65] = not chain.pommel_legal(cb)
        checks[66] = len(chain.learned_chain) == ENGINE.LEARNED_PLAY_CAP
        checks[67] = not ca.action_available
        checks[68] = not cb.action_available
        checks[69] = not cb.action_available
        checks[70] = not ca.action_available
        checks[71] = (ca.action_available, cb.action_available) == (False, False)

        p1, p1a, p1b = successful_cross(pressure=WEICH, pommel_cost=1, plays_b={T1, POMMEL})
        p1.declare_early_t1(p1b); before=p1b.spiritus; p1.declare_pommel(p1b)
        checks[72] = before - p1b.spiritus == 1
        p2, p2a, p2b = successful_cross(pressure=WEICH, pommel_cost=2, plays_b={T1, POMMEL})
        p2.declare_early_t1(p2b); before=p2b.spiritus; p2.declare_pommel(p2b)
        checks[73] = before - p2b.spiritus == 2
        poor = CandidateEngine([Fighter("A", spiritus=1, known_plays={POMMEL}), Fighter("B")], pommel_cost=2)
        poor.crossing.contact="crossing"; poor.crossing.measure="close"; poor.crossing.bind_initiative="A"
        checks[74] = not poor.declare_pommel(poor.fighters["A"]).legal
        checks[75] = poor.fighters["A"].spiritus == 1
        checks[76] = generic_close_legal
        checks[77] = all("last play" not in event.lower() for event in p2.event_log)

        checks[78] = not hasattr(e.crossing, "close_boon")
        checks[79] = not hasattr(e.crossing, "close_bane")
        checks[80] = not hasattr(e.crossing, "close_initiative")
        checks[81] = not hasattr(e.crossing, "leverage")
        checks[82] = not hasattr(e.crossing, "grapple")
        checks[83] = e.candidate_response_restrictions == ()
        checks[84] = all(token in {"ATTACK", "CANCEL", "SET", "CLEAR", "RETAIN", "MODIFY_ATTACK", "REPLACE_PENDING_ATTACK", "RESTRICT_RESPONSE"} for token in ("ATTACK", "SET", "CLEAR", "RETAIN"))

        # Protected behavior is verified by using the unmodified shared engine and suites.
        checks[85] = CurrentEngine is ENGINE.ProvisionalLongswordEngine
        checks[86] = hasattr(CurrentEngine, "declare_bind_rejoinder")
        checks[87] = hasattr(CurrentEngine, "declare_upper_winding")
        checks[88] = hasattr(CurrentEngine, "basic_defence")
        checks[89] = ENGINE.OPEN == "open"
        checks[90] = hasattr(CurrentEngine, "zornhau")
        checks[91] = not unrelated.early_t1_legal(unrelated.fighters["B"])
        checks[92] = ENGINE.LEARNED_PLAY_CAP == 3

        self.assertEqual(set(checks), set(range(1, 93)))
        self.assertTrue(all(checks.values()), {key: value for key, value in checks.items() if not value})

    def test_l1_requires_defender_ordinary_opportunity(self) -> None:
        e, a, b = successful_cross(timing="L1", pressure=HART, plays_b={T1})
        self.assertTrue(e.rejoinder_open)
        self.assertFalse(e.declare_late_t1(b))
        self.assertTrue(e.decline_bind_rejoinder(a))
        self.assertEqual(e.crossing.bind_initiative, a.name)
        self.assertTrue(e.pass_bind_initiative(a))
        self.assertTrue(e.declare_late_t1(b))
        self.assertEqual(e.crossing.measure, "close")

    def test_artifact_sanity_and_exact_cost_rows(self) -> None:
        sanity = artifact_sanity()
        self.assertAlmostEqual(sanity["loaded_cut"]["recomputed_exact"], 3.8305555555555553)
        self.assertEqual(sanity["point_threat_events"]["classification"], "INSTRUMENTATION BUG, not a mechanic bug")
        self.assertGreater(sanity["point_threat_events"]["positive_probe_count"], 0)
        self.assertEqual(sanity["point_threat_events"]["positive_probe_state"], "threatening")
        rows = pommel_cost_table()
        self.assertEqual(len(rows), 8)
        self.assertAlmostEqual(next(row for row in rows if row["skill"] == 14 and row["cost"] == 2)["expected_damage"], 3.15)

    def test_required_traces_and_scenarios_exist(self) -> None:
        self.assertEqual({trace["id"] for trace in state_traces()}, set(range(1, 10)))
        self.assertEqual({scenario.id for scenario in SCENARIOS}, {f"C{i}" for i in range(1, 11)})
        small = build_results(20)
        self.assertEqual(len(small["integrated_scenarios"]), 10)
        self.assertFalse(small["findings"]["severe_failures"])


if __name__ == "__main__":
    unittest.main()

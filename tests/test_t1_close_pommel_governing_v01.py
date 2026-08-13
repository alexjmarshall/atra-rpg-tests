from __future__ import annotations

import json
import unittest
from pathlib import Path

from simulations.shared.provisional_longsword import CurrentEngine, ENGINE, Fighter, HART, UNKNOWN, UPPER, WEICH


T1 = ENGINE.T1_PLAY
POMMEL = ENGINE.POMMEL_PLAY
TUTTA = ENGINE.TUTTA_GUARD


def qualifying_cross(
    pressure: str = HART,
    *,
    striker_plays: set[str] | None = None,
    defender_plays: set[str] | None = None,
    defender_guard: str = TUTTA,
    defender_spiritus: int = 4,
    chain: tuple[str, ...] = (),
    kind: str = "cut",
    committed: bool = False,
    power: bool = False,
    descending: bool = True,
    allows_attacker_continuations: bool = True,
) -> tuple[CurrentEngine, Fighter, Fighter]:
    striker = Fighter("A", spiritus=4, known_plays=set(striker_plays or ()))
    defender = Fighter(
        "B",
        spiritus=defender_spiritus,
        guard=defender_guard,
        known_plays=set(defender_plays if defender_plays is not None else {T1, POMMEL}),
    )
    engine = CurrentEngine([striker, defender])
    engine.learned_chain[:] = list(chain)
    attack = engine.declare_attack(
        striker,
        defender,
        kind,
        committed=committed,
        descending=descending,
        power=power,
        allows_attacker_continuations=allows_attacker_continuations,
    )
    assert attack is not None
    rolled = engine.roll_pending_attack((1,), (3,))
    assert engine.declare_basic_cross(defender, pressure, ENGINE.UPPER_CROSS)
    result = engine.basic_defence("Cross", defender, rolled.roll, (1, 20))
    assert result.success
    return engine, striker, defender


def generic_close(*, holder: str = "A", spiritus: int = 4, plays: bool = True) -> tuple[CurrentEngine, Fighter, Fighter]:
    a = Fighter("A", spiritus=spiritus, known_plays={POMMEL} if plays else set())
    b = Fighter("B", spiritus=4, known_plays={POMMEL})
    engine = CurrentEngine([a, b])
    engine.crossing = ENGINE.Crossing(
        contact="crossing",
        measure="close",
        bind_height=UNKNOWN,
        bind_initiative=holder,
        source="authored-special",
        retained=True,
    )
    return engine, a, b


class T1ClosePommelGoverningTests(unittest.TestCase):
    def test_required_governing_assertions_001_140(self) -> None:
        c: dict[int, bool] = {}

        hart, ha, hb = qualifying_cross(HART)
        c[1] = hart.t1_window_actor == hb.name
        c[2] = not hart.rejoinder_open
        c[3] = hart.rejoinder_options(ha) == []
        c[4] = hart.buy_fuhlen(ha) is None
        c[5] = hart.t1_options(hb) == [T1, "decline"]
        c[6] = hart.t1_legal(hb)
        c[7] = not hart.t1_legal(ha)
        c[8] = hart.crossing.source == "ordinary-basic-cross"
        c[9] = hart.crossing.measure == "wide"
        c[10] = hart.crossing.contact == "crossing"
        c[11] = hart.crossing.initial_pressure[hb.name] == HART
        c[12] = hart.t1_original_striker == ha.name
        c[13] = any("open E1" in event for event in hart.event_log)

        actions = (ha.action_available, hb.action_available)
        hp = (ha.hp, hb.hp)
        point = (ha.point_threat, hb.point_threat)
        before_s = hb.spiritus
        self.assertTrue(hart.declare_t1(hb))
        c[14] = before_s - hb.spiritus == 1
        c[15] = hart.learned_chain == [T1]
        c[16] = (ha.action_available, hb.action_available) == actions
        c[17] = (ha.hp, hb.hp) == hp
        c[18] = (ha.point_threat, hb.point_threat) == point
        c[19] = hart.crossing.contact == "crossing"
        c[20] = hart.crossing.retained
        c[21] = hart.crossing.measure == "close"
        c[22] = hart.crossing.bind_height == UNKNOWN
        c[23] = hart.crossing.bind_initiative == ha.name
        c[24] = not hart.crossing.initiative_passed
        c[25] = all(v == UNKNOWN for v in hart.crossing.initial_pressure.values())
        c[26] = hart.t1_window_actor is None
        c[27] = hart.t1_original_striker is None
        c[28] = not hart.rejoinder_open
        c[29] = hart.rejoinder_actor is None
        c[30] = hart.rejoinder_options(ha) == []
        c[31] = hart.buy_fuhlen(ha) is None
        c[32] = not hart.declare_t1(hb)
        c[33] = len(hart.learned_chain) == 1
        c[34] = hb.spiritus == before_s - 1
        c[35] = any("no-H3-created" in event for event in hart.event_log)

        weich, wa, wb = qualifying_cross(WEICH)
        self.assertTrue(weich.declare_t1(wb))
        c[36] = weich.crossing.bind_initiative == wb.name
        c[37] = weich.crossing.measure == "close"
        c[38] = weich.crossing.bind_height == UNKNOWN
        c[39] = all(v == UNKNOWN for v in weich.crossing.pressure.values())
        c[40] = weich.consecutive_bind_passes == 0
        c[41] = weich.pass_bind_initiative(wb)
        c[42] = weich.crossing.bind_initiative == wa.name
        c[43] = weich.crossing.initiative_passed
        c[44] = weich.pass_bind_initiative(wa)
        c[45] = weich.crossing.contact == "none"

        hgate, hga, hgb = qualifying_cross(HART)
        self.assertTrue(hgate.declare_t1(hgb))
        c[46] = not hgate.upper_winding_legal(hga)
        c[47] = not hgate.lower_winding_legal(hga)
        c[48] = not hgate.upper_winding_legal(hgb)
        c[49] = not hgate.lower_winding_legal(hgb)
        c[50] = hgate.crossing.bind_height != UPPER
        c[51] = hgate.crossing.bind_height != ENGINE.LOWER

        generic, ga, gb = generic_close()
        ga.action_available = False
        gb.action_available = True
        c[52] = generic.pommel_legal(ga)
        c[53] = POMMEL in generic.continuation_options(ga, winden_variant="W2")
        c[54] = not generic.pommel_legal(gb)
        no_play, npa, _ = generic_close(plays=False)
        c[55] = not no_play.pommel_legal(npa)
        poor, poa, _ = generic_close(spiritus=1)
        c[56] = not poor.pommel_legal(poa)
        wide, wia, _ = generic_close()
        wide.crossing.measure = "wide"
        c[57] = not wide.pommel_legal(wia)
        absent, aba, _ = generic_close()
        absent.crossing.contact = "none"
        c[58] = not absent.pommel_legal(aba)
        capped, capa, _ = generic_close()
        capped.learned_chain[:] = ["x", "y", "z"]
        c[59] = not capped.pommel_legal(capa)
        dead, dea, deb = generic_close()
        deb.hp = 0
        c[60] = not dead.pommel_legal(dea)
        pending, pea, _ = generic_close()
        pending.pending_winding = ENGINE.WindingAttack(pea, pending.other(pea), UPPER)
        c[61] = not pending.pommel_legal(pea)
        h3, h3a, _ = generic_close()
        h3.rejoinder_open = True
        c[62] = not h3.pommel_legal(h3a)
        e1, e1a, _ = generic_close()
        e1.t1_window_actor = "B"
        c[63] = not e1.pommel_legal(e1a)
        c[64] = generic.crossing.source == "authored-special"
        c[65] = ga.guard != TUTTA

        p, pa, pb = generic_close()
        actions = (pa.action_available, pb.action_available)
        hp = (pa.hp, pb.hp)
        point = (pa.point_threat, pb.point_threat)
        before_s = pa.spiritus
        declaration = p.declare_pommel(pa)
        c[66] = declaration.legal
        c[67] = before_s - pa.spiritus == 2
        c[68] = p.learned_chain == [POMMEL]
        c[69] = (pa.action_available, pb.action_available) == actions
        c[70] = (pa.hp, pb.hp) == hp
        c[71] = (pa.point_threat, pb.point_threat) == point
        c[72] = p.pending_pommel is not None
        c[73] = p.pending_pommel is not None and p.pending_pommel.accuracy == "normal"
        c[74] = p.pending_pommel is not None and p.pending_pommel.kind == "pommel"
        c[75] = p.crossing.bind_height == UNKNOWN
        c[76] = p.crossing.retained
        c[77] = p.consecutive_bind_passes == 0
        c[78] = pb.action_available == actions[1]
        c[79] = any("ordinary-response-tree-unchanged" in event for event in p.event_log)
        self.assertEqual(p.pommel_response_options(pb), ["Cross", "Beat", "Counter", "Ignore"])

        target_hp = pb.hp
        hit = p.resolve_pommel((1,), (3,))
        c[80] = hit.success
        c[81] = hit.roll is not None and hit.roll.modifier == "normal"
        c[82] = hit.damage == 4
        c[83] = pb.hp == target_hp - 4
        c[84] = p.crossing.contact == "none"
        c[85] = p.crossing.bind_initiative is None
        c[86] = p.pending_pommel is None
        c[87] = pb.guard != ENGINE.OPEN

        miss, ma, mb = generic_close()
        self.assertTrue(miss.declare_pommel(ma).legal)
        miss.consecutive_bind_passes = 1
        miss_result = miss.resolve_pommel((20,), (6,))
        c[88] = not miss_result.success
        c[89] = miss_result.damage == 0
        c[90] = mb.hp == 8
        c[91] = miss.crossing.contact == "crossing"
        c[92] = miss.crossing.measure == "close"
        c[93] = miss.crossing.bind_height == UNKNOWN
        c[94] = miss.crossing.bind_initiative == mb.name

        c[95] = not miss.crossing.initiative_passed
        c[96] = miss.consecutive_bind_passes == 0
        c[97] = miss.pending_pommel is None
        c[98] = miss.pass_bind_initiative(mb)
        c[99] = miss.crossing.bind_initiative == ma.name
        c[100] = miss.pass_bind_initiative(ma)
        c[101] = miss.crossing.contact == "none"
        chain, ca, cb = qualifying_cross(WEICH, striker_plays={POMMEL})
        self.assertTrue(chain.declare_t1(cb))
        self.assertTrue(chain.declare_pommel(cb).legal)
        c[102] = len(chain.learned_chain) == 2
        chain.resolve_pommel((20,))
        self.assertTrue(chain.declare_pommel(ca).legal)
        c[103] = len(chain.learned_chain) == 3
        c[104] = not chain.pommel_legal(cb)
        c[105] = ENGINE.LEARNED_PLAY_CAP == 3
        c[106] = chain.learned_chain == [T1, POMMEL, POMMEL]

        # E1 failures either leave H3 unchanged or never create E1.
        decline, da, db = qualifying_cross(HART, striker_plays={ENGINE.PAIRED_PLAY})
        c[107] = decline.decline_t1(db)
        c[108] = decline.rejoinder_open
        c[109] = decline.rejoinder_actor == da.name
        c[110] = decline.rejoinder_options(da) == ["Duplieren", "Mutieren", "decline"]
        c[111] = decline.crossing.measure == "wide"
        c[112] = decline.crossing.initial_pressure[db.name] == HART
        no_guard, nga, ngb = qualifying_cross(HART, defender_guard="posta-di-donna")
        c[113] = no_guard.t1_window_actor is None and no_guard.rejoinder_open
        no_play_t1, npta, nptb = qualifying_cross(HART, defender_plays=set())
        c[114] = no_play_t1.t1_window_actor is None and no_play_t1.rejoinder_open
        no_s, nsa, nsb = qualifying_cross(HART, defender_spiritus=0)
        c[115] = no_s.t1_window_actor is None and no_s.rejoinder_open
        no_cap, nca, ncb = qualifying_cross(HART, chain=("x", "y", "z"))
        c[116] = no_cap.t1_window_actor is None and no_cap.rejoinder_open
        thrust, tha, thb = qualifying_cross(HART, kind="thrust", descending=False)
        c[117] = thrust.t1_window_actor is None and thrust.rejoinder_open

        committed, coa, cob = qualifying_cross(HART, committed=True)
        c[118] = committed.t1_window_actor is None and committed.rejoinder_open
        power, pwa, pwb = qualifying_cross(HART, power=True)
        c[119] = power.t1_window_actor is None and power.rejoinder_open
        blocked, bla, blb = qualifying_cross(HART, allows_attacker_continuations=False)
        c[120] = blocked.t1_window_actor is None and not blocked.rejoinder_open
        c[121] = not hasattr(hart.crossing, "close_modifier")
        c[122] = not hasattr(hart.crossing, "close_initiative")
        c[123] = not hasattr(hart.crossing, "leverage")
        c[124] = not hasattr(hart.crossing, "grapple")
        c[125] = not hasattr(hart.crossing, "control")
        c[126] = not hasattr(CurrentEngine, "counter_wind")
        c[127] = not hasattr(CurrentEngine, "generic_close_purchase")
        c[128] = ENGINE.POMMEL_COST == 2
        c[129] = CurrentEngine is ENGINE.ProvisionalLongswordEngine
        c[130] = hasattr(CurrentEngine, "declare_bind_rejoinder")
        c[131] = hasattr(CurrentEngine, "declare_upper_winding")
        c[132] = hasattr(CurrentEngine, "declare_lower_winding")
        c[133] = hasattr(CurrentEngine, "declare_durchwechseln")
        c[134] = hasattr(CurrentEngine, "zornhau")
        c[135] = hasattr(CurrentEngine, "compound_response")
        c[136] = hart.point_threat_events >= 0
        probe, pra, prb = generic_close()
        probe._set_point_threat(pra, "threatening", "test-probe")
        c[137] = probe.point_threat_events == 1
        probe._set_point_threat(pra, "threatening", "duplicate-probe")
        c[138] = probe.point_threat_events == 1
        c[139] = all("CANCEL H3" not in event for event in hart.event_log)
        c[140] = all("RESTRICT_RESPONSE" not in event for event in p.event_log)

        self.assertEqual(set(c), set(range(1, 141)))
        self.assertTrue(all(c.values()), {number: value for number, value in c.items() if not value})

    def test_required_sequences_a_through_n(self) -> None:
        outcomes: dict[str, bool] = {}

        e, a, b = qualifying_cross(HART)
        outcomes["A"] = e.declare_t1(b) and e.crossing.bind_initiative == a.name
        e, a, b = qualifying_cross(WEICH)
        outcomes["B"] = e.declare_t1(b) and e.crossing.bind_initiative == b.name
        e, a, b = qualifying_cross(HART)
        outcomes["C"] = e.decline_t1(b) and e.rejoinder_open and e.rejoinder_actor == a.name
        e, a, b = qualifying_cross(HART, defender_guard="posta-di-donna")
        outcomes["D"] = e.t1_window_actor is None and e.rejoinder_open
        e, a, b = qualifying_cross(HART, kind="thrust", descending=False)
        outcomes["E"] = e.t1_window_actor is None and e.rejoinder_open
        e, a, b = qualifying_cross(HART, defender_spiritus=0)
        outcomes["F"] = e.t1_window_actor is None and e.rejoinder_open
        e, a, b = qualifying_cross(HART, chain=("1", "2", "3"))
        outcomes["G"] = e.t1_window_actor is None and e.rejoinder_open
        e, a, b = generic_close()
        outcomes["H"] = e.declare_pommel(a).legal and e.resolve_pommel((1,), (3,)).damage == 4
        e, a, b = generic_close()
        outcomes["I"] = e.declare_pommel(a).legal and not e.resolve_pommel((20,)).success and e.crossing.bind_initiative == b.name
        e, a, b = generic_close(spiritus=1)
        outcomes["J"] = not e.declare_pommel(a).legal and a.spiritus == 1
        e, a, b = generic_close()
        e.learned_chain[:] = ["1", "2", "3"]
        outcomes["K"] = not e.declare_pommel(a).legal
        e, a, b = generic_close()
        a.hp = 0
        outcomes["L"] = not e.declare_pommel(a).legal
        e, a, b = generic_close()
        outcomes["M"] = e.pass_bind_initiative(a) and e.pass_bind_initiative(b) and e.crossing.contact == "none"
        e, a, b = generic_close()
        outcomes["N"] = e.disengage(a) and e.crossing.contact == "none"

        self.assertEqual(set(outcomes), set("ABCDEFGHIJKLMN"))
        self.assertTrue(all(outcomes.values()), outcomes)

    def test_selector_metadata_matches_runtime(self) -> None:
        t1 = ENGINE.T1_PLAY
        self.assertEqual(ENGINE.POMMEL_COST, 2)
        from simulations.shared.provisional_longsword import GOVERNING_BASELINE

        self.assertEqual(GOVERNING_BASELINE["tutta_cover_to_stretto"]["window"], "after successful qualifying Cross and D1 timing; before H3 Rejoinder creation")
        self.assertEqual(GOVERNING_BASELINE["pommel_strike"]["spiritus_cost"], 2)
        self.assertEqual(GOVERNING_BASELINE["pommel_strike"]["learned_chain_entries"], 1)
        self.assertFalse(GOVERNING_BASELINE["pommel_strike"]["intrinsic_response_restriction"])
        self.assertEqual(t1, "Tutta Cover-to-Stretto")
        root = Path(__file__).resolve().parents[1]
        specification = json.loads((root / "data/prototypes/longsword-t1-close-pommel-governing-v0.1.yaml").read_text(encoding="utf-8"))
        pommel_record = json.loads((root / "data/plays/play-italian-longsword-pommel-strike.yaml").read_text(encoding="utf-8"))
        mapping = json.loads((root / "data/audits/longsword-vertical-slice-mechanical-mapping-v0.1.yaml").read_text(encoding="utf-8"))
        self.assertEqual(specification["pommel_strike"]["selected_variant"], "P2")
        self.assertEqual(specification["pommel_strike"]["cost"]["spiritus"], ENGINE.POMMEL_COST)
        self.assertEqual(pommel_record["game_implementation"]["mechanics"]["spiritus_cost"], ENGINE.POMMEL_COST)
        mapped_pommel = next(item for item in mapping["techniques"] if item["id"] == "pommel-strike")
        self.assertTrue(all(effect["op"] != "RESTRICT_RESPONSE" for effect in mapped_pommel["primary_payload"]))

    def test_fixed_seed_smoke_matrix_is_complete_and_safe(self) -> None:
        from simulations.t1_close_pommel_governing_v0_1.simulate import SCENARIOS, build_results

        self.assertEqual({scenario.id for scenario in SCENARIOS}, {f"S{i}" for i in range(1, 11)})
        results = build_results(25)
        self.assertEqual(results["scenario_count"], 10)
        self.assertTrue(all(value == 0 for value in results["safety"].values()), results["safety"])


if __name__ == "__main__":
    unittest.main()

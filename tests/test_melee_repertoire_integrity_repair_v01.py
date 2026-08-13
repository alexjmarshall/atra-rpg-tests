from __future__ import annotations

import unittest

from simulations.shared.provisional_longsword_engine import (
    Attack,
    Crossing,
    Fighter,
    HART,
    OPEN,
    ProvisionalLongswordEngine,
    RollResult,
)


def arena(*, a_plays=(), b_plays=(), a_guard="vom-tag", b_guard="pflug", spiritus=8):
    a = Fighter("A", spiritus=spiritus, guard=a_guard, known_plays=set(a_plays))
    b = Fighter("B", spiritus=spiritus, guard=b_guard, known_plays=set(b_plays))
    return ProvisionalLongswordEngine([a, b]), a, b


def declared_hit(engine, attacker, defender, *, committed=False, descending=True, damage=(3,)):
    attack = engine.declare_attack(attacker, defender, "descending-cut", committed=committed, descending=descending)
    assert attack is not None
    result = engine.roll_pending_attack((7,), damage)
    assert result.success
    return attack


def set_bind(engine, a, b, relation="favored", initiative="A", pressure="unknown"):
    other = "unfavored" if relation == "favored" else "favored"
    engine.crossing = Crossing(
        contact="crossing",
        measure="wide",
        pressure={a.name: pressure, b.name: pressure},
        bind_position={a.name: relation, b.name: other},
        bind_initiative=initiative,
        source="zornhau-local",
    )


def test_01_08_cross_d1_beat_open_state_based():
    engine, attacker, defender = arena(b_guard="vom-tag")
    attack = Attack(attacker, defender, "cut")
    # 1-3: Cross exposes D1 when point is nonthreatening; point denies; Crossing does not.
    assert engine.d1_window(defender, attack)
    engine.crossing.contact = "crossing"
    assert engine.d1_window(defender, attack)
    defender.point_threat = "threatening"
    assert not engine.d1_window(defender, attack)

    # 4: successful Zornhau denies D1 because it authors point threat.
    engine, attacker, defender = arena(b_plays={"Zornhau-Ort"}, b_guard="vom-tag")
    declared_hit(engine, attacker, defender, committed=False)
    zorn = engine.zornhau(defender, engine.pending_attack.attack_roll, (5,))
    assert zorn.success and not engine.d1_window(defender, Attack(attacker, defender, "cut"))

    # 5-8: Beat uses the same point gate, successful Beat creates Open, failure does not,
    # and there is no self-Open rule.
    engine, attacker, defender = arena(b_guard="vom-tag")
    attack = declared_hit(engine, attacker, defender)
    defender.action_available = True
    beat = engine.basic_defence("Beat", defender, attack.attack_roll, (6,))
    assert beat.success and attacker.guard == OPEN and defender.guard != OPEN

    engine, attacker, defender = arena(b_guard="vom-tag")
    attack = declared_hit(engine, attacker, defender)
    defender.action_available = True
    beat = engine.basic_defence("Beat", defender, attack.attack_roll, (20,))
    assert not beat.success and attacker.guard != OPEN and defender.guard != OPEN


def test_09_11_gc1_and_open_recovery():
    engine, actor, _ = arena(a_guard="vom-tag")
    engine.begin_activation(actor)
    assert engine.change_guard(actor, "ochs", "before_action")
    actor.activation_action_taken = True
    assert not engine.change_guard(actor, "pflug", "after_action")

    actor.guard = OPEN
    engine.begin_activation(actor)
    assert engine.recover_open(actor, "pflug")
    assert not actor.guard_change_available
    assert not engine.change_guard(actor, "ochs", "before_action")


def test_12_18_general_committed_counter_timing():
    engine, attacker, defender = arena()
    attacker.hp = 4
    attack = engine.declare_attack(attacker, defender, "committed-cut", committed=True, descending=True)
    assert attack and attack.phase == "declared"  # 12
    counter = engine.immediate_counter(defender, (5,), (6,))
    assert counter.success and counter.events.index("immediate-counter:roll-first") < counter.events.index("committed-attack:cancelled-by-removal")  # 13-14

    engine, attacker, defender = arena()
    attack = engine.declare_attack(attacker, defender, "committed-cut", committed=True, descending=True)
    engine.immediate_counter(defender, (5,), (2,))
    assert attacker.alive and attack.phase == "declared"  # 15
    assert engine.roll_pending_attack((5,), (4,)).success
    assert not defender.action_available  # 16

    engine, attacker, defender = arena()
    engine.declare_attack(attacker, defender, "committed-cut", committed=True, descending=True)
    assert engine.roll_pending_attack((5,), (3,)).success
    counter = engine.waiting_counter(defender, (4,), (2,))
    assert counter.legal and "waiting-counter:simultaneous" in counter.events  # 17

    engine, attacker, defender = arena()
    engine.declare_attack(attacker, defender, "committed-cut", committed=True, descending=True)
    assert not engine.roll_pending_attack((20,)).success
    assert not engine.waiting_counter(defender, (4,)).legal  # 18


def test_19_24_preparation_nachreisen():
    engine, attacker, defender = arena(b_plays={"Nachreisen"})
    third = Fighter("C", known_plays={"Nachreisen"})
    engine.fighters[third.name] = third
    attacker.hp = 3
    engine.declare_attack(attacker, defender, "committed-cut", committed=True, descending=True)
    assert not engine.preparation_nachreisen(third, (3, 18)).legal  # 19
    before_s = defender.spiritus
    prep = engine.preparation_nachreisen(defender, (3, 18), (4,))
    assert prep.legal and defender.spiritus == before_s - 1 and engine.learned_chain == ["Nachreisen"]  # 20
    assert prep.roll.modifier == "boon"  # 21
    assert prep.events.index("nachreisen:preparation:boon-roll-first") < prep.events.index("committed-attack:cancelled-by-removal")  # 22-23

    engine, attacker, defender = arena(b_plays={"Nachreisen"})
    attack = engine.declare_attack(attacker, defender, "committed-cut", committed=True, descending=True)
    prep = engine.preparation_nachreisen(defender, (4, 18), (1,))
    assert prep.success and attacker.alive and attack.phase == "declared"  # 24


def test_25_33_recovery_nachreisen_scope_and_cleanup():
    engine, attacker, defender = arena(b_plays={"Nachreisen"}, b_guard="alber")
    engine.declare_attack(attacker, defender, "committed-cut", committed=True, descending=True)
    assert defender.action_available  # 25 waiting preserves action
    miss = engine.roll_pending_attack((20,))
    assert not miss.success and engine.recovery_nachreisen_target == defender.name  # 26
    before = defender.spiritus
    recovery = engine.recovery_nachreisen(defender, (4, 18), (3,))
    assert recovery.legal and defender.spiritus == before - 1 and recovery.roll.modifier == "boon"  # 28-29
    assert not engine.recovery_nachreisen_immediate  # 27 immediate/nonpersistent
    assert not attacker.action_available  # 30 no action-funded Basic defence
    assert defender.guard == "alber"  # 31 no Vom Tag gate

    engine, attacker, defender = arena(b_plays={"Nachreisen"})
    engine.declare_attack(attacker, defender, "ordinary-cut", committed=False, descending=True)
    engine.roll_pending_attack((20,))
    assert not engine.recovery_nachreisen_immediate  # 32-33 unrelated/non-Committed miss


def test_34_41_zornhau_and_nearest_basic():
    engine, attacker, defender = arena(b_plays={"Zornhau-Ort"}, b_guard="vom-tag")
    before_s = defender.spiritus
    attack = declared_hit(engine, attacker, defender, committed=False, descending=True)
    defender.action_available = True
    zorn = engine.zornhau(defender, attack.attack_roll, (4,))
    assert zorn.legal  # 34 generic descending Cut
    assert not defender.action_available and engine.learned_chain == ["Zornhau-Ort"] and defender.spiritus == before_s  # 35
    assert attack.cancelled and engine.crossing.contact == "crossing" and defender.point_threat == "threatening"  # 36-38
    assert zorn.damage == 0  # 39
    assert set(engine.crossing.pressure.values()) == {"unknown"}  # 40

    cross_engine, cross_attacker, cross_defender = arena(b_guard="vom-tag")
    cross_attack = declared_hit(cross_engine, cross_attacker, cross_defender)
    cross_defender.action_available = True
    assert cross_engine.declare_basic_cross(cross_defender, HART)
    cross = cross_engine.basic_defence("Cross", cross_defender, cross_attack.attack_roll, (4,))
    assert cross.success and cross_engine.crossing.contact == "crossing"
    assert cross_defender.point_threat == "not_threatening" and cross_engine.learned_chain == []  # 41


def test_42_47_contested_bind_relation_and_tie():
    # The contested relation is now local to qualifying Zornhau/special binds.
    engine, attacker, defender = arena(b_plays={"Zornhau-Ort"})
    attack = declared_hit(engine, attacker, defender)
    defender.action_available = True
    engine.zornhau(defender, attack.attack_roll, (3,))
    assert engine.crossing.bind_position == {defender.name: "favored", attacker.name: "unfavored"}  # 42-44
    assert engine.crossing.tie_breaks == 0

    engine, attacker, defender = arena(b_plays={"Zornhau-Ort"})
    attack = declared_hit(engine, attacker, defender)
    defender.action_available = True
    engine.zornhau(defender, attack.attack_roll, (7,))
    assert engine.crossing.bind_position[defender.name] == "favored" and engine.crossing.tie_breaks == 1  # 45
    assert not hasattr(engine.crossing, "attack_modifier") and not hasattr(engine.crossing, "defence_modifier")  # 46

    engine.crossing = Crossing(contact="crossing", bind_position={attacker.name: "unknown", defender.name: "unknown"})
    assert engine.crossing.bind_position[attacker.name] == "unknown"  # 47


def test_48_51_bind_initiative_is_separate_and_passes_once():
    engine, attacker, defender = arena()
    attack = declared_hit(engine, attacker, defender)
    defender.action_available = True
    assert engine.declare_basic_cross(defender, HART)
    engine.basic_defence("Cross", defender, attack.attack_roll, (12,))
    assert engine.crossing.bind_initiative is None  # 48: Rejoinder precedes initiative
    assert engine.crossing.bind_position[defender.name] == "unknown"  # 50
    assert engine.decline_bind_rejoinder(attacker)
    assert engine.crossing.bind_initiative == attacker.name  # 51

    engine, attacker, defender = arena(b_plays={"Zornhau-Ort"})
    attack = declared_hit(engine, attacker, defender)
    defender.action_available = True
    engine.zornhau(defender, attack.attack_roll, (12,))
    assert engine.crossing.bind_initiative == defender.name  # 49


def test_52_54_fuhlen_visibility_and_zero_cost():
    engine, a, b = arena(a_plays={"Zornhau-Ort"})
    set_bind(engine, a, b, "favored")
    assert engine.bind_view(a) == "unknown"  # 52
    before = (a.action_available, a.spiritus, len(engine.learned_chain))
    a.known_plays.add("Fühlen")
    assert engine.bind_view(a) == "favored"  # 53 category, not raw roll
    assert (a.action_available, a.spiritus, len(engine.learned_chain)) == before  # 54


def test_55_63_ort_intrinsic_hidden_requirement_and_damage_models():
    engine, a, b = arena(a_plays={"Zornhau-Ort"})
    engine.learned_chain = ["Zornhau-Ort"]
    set_bind(engine, a, b, "favored")
    before_s = a.spiritus
    before_chain = list(engine.learned_chain)
    o1 = engine.ort(a, "O1", (6,))
    assert o1.success and a.spiritus == before_s - 1 and engine.learned_chain == before_chain  # 55-56
    assert o1.roll is None and o1.damage == 7  # 57-58, 61
    assert engine.crossing.contact == "crossing" and b.guard == "pflug"  # 63 no extras

    engine, a, b = arena(a_plays={"Zornhau-Ort"})
    set_bind(engine, a, b, "unfavored")
    before_s = a.spiritus
    failed = engine.ort(a, "O1", (6,))
    assert failed.legal and not failed.success and a.spiritus == before_s - 1  # 59
    a.known_plays.add("Fühlen")
    assert "Ort" not in engine.continuation_options(a, winden_variant="W2")  # 60

    engine, a, b = arena(a_plays={"Zornhau-Ort"})
    set_bind(engine, a, b, "favored")
    o2 = engine.ort(a, "O2", (2, 6))
    assert o2.success and o2.damage == 3  # 62


def test_64_76_minimal_winden_variants_and_aftermath():
    engine, a, b = arena(a_plays={"Winden"}, a_guard="vom-tag")
    set_bind(engine, a, b, "unfavored", pressure="hard")
    before_action = a.action_available
    before_s = a.spiritus
    w1 = engine.winden(a, "W1", (5,), (4,))
    assert w1.legal and engine.learned_chain == ["Winden"] and a.spiritus == before_s - 1  # 64-65
    assert a.action_available == before_action  # 66
    assert engine.crossing.retained and a.point_threat == "threatening"  # 67-68
    assert w1.roll.modifier == "normal" and w1.damage == 5  # 69-70
    assert engine.crossing.pressure == {a.name: "hard", b.name: "hard"}  # 74
    assert not hasattr(engine.crossing, "attack_modifier")  # 75
    assert a.guard == "vom-tag" and "Ochs-or-Pflug" in engine.crossing.hanging_aftermath  # 76

    engine, a, b = arena(a_plays={"Winden"})
    set_bind(engine, a, b, "favored")
    before_s = a.spiritus
    wrong = engine.winden(a, "W1", (5,), (4,))
    assert wrong.legal and not wrong.success and a.spiritus == before_s - 1  # 71-72

    for relation in ("favored", "unfavored"):
        engine, a, b = arena(a_plays={"Winden"})
        set_bind(engine, a, b, relation)
        assert engine.winden(a, "W2", (5,), (4,)).legal  # 73


def test_77_81_chain_cap_intrinsics_and_passive():
    engine, a, b = arena(a_plays={"Zornhau-Ort", "Winden", "Fühlen"})
    engine.learned_chain = ["Zornhau-Ort"]
    set_bind(engine, a, b, "favored")
    before = len(engine.learned_chain)
    engine.bind_view(a)
    assert len(engine.learned_chain) == before == 1  # 77, 80
    engine.ort(a, "O1", (3,))
    assert len(engine.learned_chain) == 1  # 78

    set_bind(engine, a, b, "unfavored")
    engine.winden(a, "W1", (4,), (3,))
    assert len(engine.learned_chain) == 2  # 79
    assert engine.add_learned_play("third")
    assert not engine.add_learned_play("fourth")  # 81


def test_authoritative_baseline_p1_t1_c2_and_no_archived_behavior_dependency():
    engine, a, b = arena(a_plays={"Tutta Cover-to-Stretto"}, a_guard="posta-di-donna")
    power = engine.declare_power_attack(a, b)
    assert power and power.committed and power.damage_mode == "fixed-7" and not power.allows_attacker_continuations
    assert not engine.attempt_attacker_continuation(a, "Durchwechseln")

    engine, a, b = arena(a_plays={"Tutta Cover-to-Stretto"}, a_guard="tutta-porta-di-ferro")
    set_bind(engine, a, b, "favored")
    assert engine.tutta_cover_to_stretto(a)
    assert engine.crossing.measure == "close" and engine.crossing.retained

    engine, a, b = arena(b_plays={"Absetzen"})
    attack = declared_hit(engine, a, b, descending=False)
    b.action_available = True
    result = engine.compound_response("Absetzen", b, (4,), (3,))
    assert result.success and b.spiritus == 6 and engine.learned_chain == ["Absetzen"]


class MeleeRepertoireIntegrityRepairTests(unittest.TestCase):
    """unittest discovery wrappers for the numbered deterministic assertions."""

    def test_cases_01_08(self):
        test_01_08_cross_d1_beat_open_state_based()

    def test_cases_09_11(self):
        test_09_11_gc1_and_open_recovery()

    def test_cases_12_18(self):
        test_12_18_general_committed_counter_timing()

    def test_cases_19_24(self):
        test_19_24_preparation_nachreisen()

    def test_cases_25_33(self):
        test_25_33_recovery_nachreisen_scope_and_cleanup()

    def test_cases_34_41(self):
        test_34_41_zornhau_and_nearest_basic()

    def test_cases_42_47(self):
        test_42_47_contested_bind_relation_and_tie()

    def test_cases_48_51(self):
        test_48_51_bind_initiative_is_separate_and_passes_once()

    def test_cases_52_54(self):
        test_52_54_fuhlen_visibility_and_zero_cost()

    def test_cases_55_63(self):
        test_55_63_ort_intrinsic_hidden_requirement_and_damage_models()

    def test_cases_64_76(self):
        test_64_76_minimal_winden_variants_and_aftermath()

    def test_cases_77_81(self):
        test_77_81_chain_cap_intrinsics_and_passive()

    def test_authoritative_baseline_sync(self):
        test_authoritative_baseline_p1_t1_c2_and_no_archived_behavior_dependency()

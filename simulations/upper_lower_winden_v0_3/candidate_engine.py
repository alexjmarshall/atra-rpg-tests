"""Isolated H3 Upper/Lower Winden candidate overlay.

The authoritative shared engine remains the R0 control.  Lower geometry is
authored as event metadata on the Basic-Cross defence; it is not inferred from
guard, measure, contact zone, or a generic "low" label.
"""

from __future__ import annotations

from dataclasses import dataclass

from simulations.general_bind_information_v0_1.candidate_engine import HART, UNKNOWN, WEICH
from simulations.hart_weich_upper_winden_v0_2.candidate_engine import (
    CandidateCrossing,
    HartWeichUpperWindenEngine,
    UPPER,
    WINDEN_PLAY,
)
from simulations.shared.provisional_longsword_engine import Fighter, Resolution


LOWER = "lower"
UNCLASSIFIED = "unclassified"
UPPER_CROSS = "upper-cross-against-descending-cut"
LOWER_SETTING_ASIDE = "lower-setting-aside"
DEFENCE_GEOMETRIES = (UPPER_CROSS, LOWER_SETTING_ASIDE, UNCLASSIFIED)
LOWER_WINDING_THRUST = "Lower Winding Thrust"
L1 = "L1"
L2 = "L2"


@dataclass
class LowerWindingAttack:
    actor: Fighter
    target: Fighter
    failure_variant: str
    spiritus_cost: int = 2
    accuracy: str = "normal"
    kind: str = "thrust"
    phase: str = "declared"


class UpperLowerWindenEngine(HartWeichUpperWindenEngine):
    """H3 overlay: H2 plus a conservative Lower writer and Lower Winding."""

    def __init__(self, fighters):
        super().__init__(fighters)
        self.declared_defence_geometry: tuple[str, str] | None = None
        self.pending_lower_winding: LowerWindingAttack | None = None

    @staticmethod
    def _qualifies_lower_writer(kind: str, defence_geometry: str) -> bool:
        normalized = kind.lower().replace("_", "-")
        qualifying_attack = normalized in {
            "low-line-thrust",
            "rising-low-line-cut",
        }
        return defence_geometry == LOWER_SETTING_ASIDE and qualifying_attack

    def declare_h3_cross(self, defender: Fighter, pressure: str, defence_geometry: str) -> bool:
        if defence_geometry not in DEFENCE_GEOMETRIES:
            return False
        if not super().declare_h1_cross(defender, pressure):
            return False
        self.declared_defence_geometry = (defender.name, defence_geometry)
        self.event_log.append(f"H3:authored-defence-geometry:{defence_geometry}")
        return True

    def resolve_h1_cross(self, defender: Fighter, defence_rolls: tuple[int, ...]) -> Resolution:
        attack = self.pending_attack
        geometry = (
            self.declared_defence_geometry[1]
            if self.declared_defence_geometry
            and self.declared_defence_geometry[0] == defender.name
            else UNCLASSIFIED
        )
        self.declared_defence_geometry = None
        result = super().resolve_h1_cross(defender, defence_rolls)
        if not result.legal or not result.success or attack is None:
            return result

        if self._qualifies_lower_writer(attack.kind, geometry):
            height = LOWER
        elif geometry == UPPER_CROSS and self._qualifies_upper_writer(attack.kind, attack.descending):
            height = UPPER
        else:
            height = UNKNOWN
        self.crossing.bind_height = height
        self.event_log.append(f"H3:writer:SET bind_height={height}")
        result.events = list(self.event_log)
        return result

    def upper_winding_legal(self, actor: Fighter, spiritus_cost: int = 2) -> bool:
        return (
            spiritus_cost == 2
            and self.pending_lower_winding is None
            and super().upper_winding_legal(actor, spiritus_cost)
        )

    def lower_winding_legal(self, actor: Fighter) -> bool:
        return (
            WINDEN_PLAY in actor.known_plays
            and self.crossing.contact == "crossing"
            and self.crossing.bind_height == LOWER
            and self.crossing.bind_initiative == actor.name
            and actor.spiritus >= 2
            and len(self.learned_chain) < 3
            and not self.rejoinder_open
            and self.pending_bind_attack is None
            and self.pending_upper_winding is None
            and self.pending_lower_winding is None
        )

    def declare_lower_winding(self, actor: Fighter, failure_variant: str = L2) -> Resolution:
        if failure_variant not in {L1, L2}:
            return Resolution(False, reason="unknown Lower Winding failure variant")
        if not self.lower_winding_legal(actor):
            return Resolution(False, reason="Lower Winding Thrust prerequisites fail")
        self.spend_spiritus(actor, 2)
        self.add_learned_play(f"Winden:{LOWER_WINDING_THRUST}")
        self.crossing.retained = True
        self.crossing.hanging_aftermath = "pflug-lower-hanging"
        self.crossing.pressure = {name: UNKNOWN for name in self.fighters}
        actor.guard = "pflug"
        actor.point_threat = "threatening"
        self.pending_lower_winding = LowerWindingAttack(
            actor=actor,
            target=self.other(actor),
            failure_variant=failure_variant,
        )
        self.consecutive_bind_passes = 0
        self.event_log.append(
            f"H3:Lower-Winding:{failure_variant}:declare:2S+chain:"
            "RETAIN+SET Pflug+SET point+ATTACK flat thrust"
        )
        return Resolution(True, True, "Lower Winding Thrust declared")

    def resolve_lower_winding(
        self,
        attack_rolls: tuple[int, ...],
        damage_rolls: tuple[int, ...] = (3,),
    ) -> Resolution:
        winding = self.pending_lower_winding
        if winding is None or winding.phase != "declared":
            return Resolution(False, reason="no pending Lower Winding Thrust")
        result = self.test(winding.actor.skill, attack_rolls, "normal")
        winding.phase = "resolved"
        self.pending_lower_winding = None
        if result.success:
            amount = self.damage(damage_rolls)
            winding.target.hp -= amount
            self.event_log.append("H3:Lower-Winding:hit:normal-damage+CLEAR contact")
            self._end_candidate_contact()
            return Resolution(
                True, True, "Lower Winding Thrust hit", amount, list(self.event_log), result
            )

        self.crossing.contact = "crossing"
        self.crossing.retained = True
        self.crossing.bind_initiative = winding.target.name
        self.crossing.pressure = {name: UNKNOWN for name in self.fighters}
        winding.actor.point_threat = "threatening"
        if winding.failure_variant == L1:
            self.crossing.bind_height = LOWER
            self.crossing.hanging_aftermath = "pflug-lower-hanging"
            winding.actor.guard = "pflug"
            transition = "RETAIN Lower+Pflug"
        else:
            self.crossing.bind_height = UPPER
            self.crossing.hanging_aftermath = "ochs-upper-hanging"
            winding.actor.guard = "ochs"
            transition = "SET Lower->Upper+SET Pflug->Ochs"
        self.event_log.append(
            f"H3:Lower-Winding:{winding.failure_variant}:miss:{transition}:"
            f"RETAIN point+initiative->{winding.target.name}"
        )
        return Resolution(
            True, False, "Lower Winding Thrust missed", 0, list(self.event_log), result
        )

    def pass_bind_initiative(self, actor: Fighter) -> bool:
        if self.pending_lower_winding is not None:
            return False
        return super().pass_bind_initiative(actor)

    def disengage(self, actor: Fighter) -> bool:
        if self.pending_lower_winding is not None:
            return False
        return super().disengage(actor)

    def _end_candidate_contact(self) -> None:
        measure = self.crossing.measure
        self.crossing = CandidateCrossing(measure=measure)
        self.rejoinder_open = False
        self.rejoinder_actor = None
        self.pending_bind_attack = None
        self.pending_upper_winding = None
        self.pending_lower_winding = None
        self.consecutive_bind_passes = 0
        self.declared_defence_geometry = None


def make_successful_h3_cross(
    *,
    pressure: str = HART,
    geometry: str = UPPER_CROSS,
    attacker_plays=(),
    defender_plays=(),
    attacker_skill: int = 14,
    defender_skill: int = 14,
    attacker_spiritus: int = 8,
    defender_spiritus: int = 8,
    attacker_guard: str = "vom-tag",
    defender_guard: str = "vom-tag",
):
    attacker = Fighter(
        "A", skill=attacker_skill, spiritus=attacker_spiritus,
        guard=attacker_guard, known_plays=set(attacker_plays),
    )
    defender = Fighter(
        "B", skill=defender_skill, spiritus=defender_spiritus,
        guard=defender_guard, known_plays=set(defender_plays),
    )
    engine = UpperLowerWindenEngine([attacker, defender])
    if geometry == UPPER_CROSS:
        kind, descending = "descending-cut", True
    elif geometry == LOWER_SETTING_ASIDE:
        kind, descending = "low-line-thrust", False
    else:
        kind, descending = "lateral-cut", False
    attack = engine.declare_attack(attacker, defender, kind, descending=descending)
    assert attack is not None
    rolled = engine.roll_pending_attack((5,))
    assert rolled.success and rolled.roll is not None
    assert engine.declare_h3_cross(defender, pressure, geometry)
    crossed = engine.resolve_h1_cross(defender, (6, 16) if pressure == HART else (6,))
    assert crossed.legal and crossed.success
    return engine, attacker, defender

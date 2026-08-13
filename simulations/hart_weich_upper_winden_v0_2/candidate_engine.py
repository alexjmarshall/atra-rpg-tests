"""Isolated H2 Hart/Weich + Upper Winding Thrust candidate layer.

The authoritative governing-provisional engine remains the R0 control.  This
module extends the earlier H1 experiment only for ordinary Basic Crosses and
does not promote any candidate mechanic.
"""

from __future__ import annotations

from dataclasses import dataclass

from simulations.general_bind_information_v0_1.candidate_engine import (
    BindRejoinderAttack,
    GeneralBindCandidateEngine,
    HART,
    PAIRED_PLAY,
    UNKNOWN,
    WEICH,
)
from simulations.shared.provisional_longsword_engine import (
    Crossing,
    Fighter,
    Resolution,
)


UPPER = "upper"
LOWER = "lower"
WINDEN_PLAY = "Winden"
UPPER_WINDING_THRUST = "Upper Winding Thrust"
BIND_HEIGHTS = (UPPER, LOWER, UNKNOWN)


@dataclass
class CandidateCrossing(Crossing):
    """Candidate-public geometry added without changing the shared Crossing."""

    bind_height: str = UNKNOWN


@dataclass
class UpperWindingAttack:
    actor: Fighter
    target: Fighter
    spiritus_cost: int
    accuracy: str = "normal"
    kind: str = "thrust"
    phase: str = "declared"


class HartWeichUpperWindenEngine(GeneralBindCandidateEngine):
    """H2 overlay: phase-scoped H1 pressure plus one general Winden execution."""

    def __init__(self, fighters):
        super().__init__(fighters)
        self.crossing = CandidateCrossing()
        self.pending_upper_winding: UpperWindingAttack | None = None
        self.consecutive_bind_passes = 0
        self.crossing_source: str | None = None

    @staticmethod
    def _qualifies_upper_writer(kind: str, descending: bool) -> bool:
        normalized = kind.lower().replace("_", "-")
        return descending and ("cut" in normalized or "oberhau" in normalized)

    def resolve_h1_cross(self, defender: Fighter, defence_rolls: tuple[int, ...]) -> Resolution:
        """Resolve candidate ordinary H1 Cross and write bounded public height."""
        attack = self.pending_attack
        if (
            attack is None
            or self.declared_pressure is None
            or self.declared_pressure[0] != defender.name
            or defender is not attack.target
            or not attack.allows_attacker_continuations
        ):
            return Resolution(False, reason="no valid ordinary H1 Cross declaration")
        pressure = self.declared_pressure[1]
        self.declared_pressure = None
        if not self.spend_action(defender):
            return Resolution(False, reason="action unavailable")
        modifier = "boon" if pressure == HART else "normal"
        result = self.test(defender.skill, defence_rolls, modifier)
        self.event_log.append(f"H2:H1-Cross-roll:{modifier}")
        if not result.success:
            self.crossing = CandidateCrossing(measure=self.crossing.measure)
            self.rejoinder_open = False
            self.rejoinder_actor = None
            self.event_log.append("H2:failed-Cross:CLEAR pressure+bind-height")
            return Resolution(True, False, "failed H2 H1 Basic Cross", events=list(self.event_log), roll=result)

        attack.cancelled = True
        attack.phase = "cancelled"
        self.bind_serial += 1
        height = UPPER if self._qualifies_upper_writer(attack.kind, attack.descending) else UNKNOWN
        self.crossing = CandidateCrossing(
            contact="crossing",
            measure=self.crossing.measure,
            contact_zone={defender.name: UNKNOWN, attack.actor.name: UNKNOWN},
            pressure={defender.name: pressure, attack.actor.name: UNKNOWN},
            bind_position={defender.name: UNKNOWN, attack.actor.name: UNKNOWN},
            bind_initiative=None,
            bind_height=height,
        )
        self.rejoinder_actor = attack.actor.name
        self.rejoinder_open = True
        self.pending_bind_attack = None
        self.pending_upper_winding = None
        self.consecutive_bind_passes = 0
        self.crossing_source = "ordinary-h1"
        self.event_log.append(f"H2:H1-Cross:CANCEL+SET crossing+height={height}+open Rejoinder")
        return Resolution(True, True, "successful H2 H1 Basic Cross", events=list(self.event_log), roll=result)

    def pressure_view(self, viewer: Fighter, subject: Fighter) -> str:
        """F1 sees only live initial pressure, never later/future pressure."""
        actual = self.crossing.pressure.get(subject.name, UNKNOWN)
        if actual not in {HART, WEICH}:
            return UNKNOWN
        if viewer is subject:
            return actual
        if not self.rejoinder_open:
            return UNKNOWN
        return self.fuhlen_reveals.get((self.bind_serial, viewer.name), UNKNOWN)

    def buy_fuhlen(self, actor: Fighter) -> str | None:
        if (
            not self.rejoinder_open
            or self.rejoinder_actor != actor.name
            or "Fühlen" not in actor.known_plays
            or self.crossing.contact != "crossing"
            or actor.spiritus < 1
            or (self.bind_serial, actor.name) in self.fuhlen_purchases
        ):
            return None
        opponent = self.other(actor)
        revealed = self.crossing.pressure.get(opponent.name, UNKNOWN)
        if revealed not in {HART, WEICH}:
            revealed = UNKNOWN
        self.spend_spiritus(actor, 1)
        self.fuhlen_purchases.add((self.bind_serial, actor.name))
        self.fuhlen_reveals[(self.bind_serial, actor.name)] = revealed
        self.event_log.append(f"H2:F1:{actor.name}:initial-pressure={revealed}")
        return revealed

    def declare_bind_rejoinder(self, actor: Fighter, branch: str) -> Resolution:
        """Declare 2S hard-failure D/M; the graduated model is not in H2."""
        if branch not in self.rejoinder_options(actor):
            return Resolution(False, reason="Bind Rejoinder prerequisites fail")
        self.spend_spiritus(actor, 2)
        self.add_learned_play(f"{PAIRED_PLAY}:{branch}")
        self.rejoinder_open = False
        defender = self.other(actor)
        pressure = self.crossing.pressure.get(defender.name, UNKNOWN)
        correct = (branch == "Duplieren" and pressure == HART) or (
            branch == "Mutieren" and pressure == WEICH
        )
        self._clear_initial_pressure()
        if not correct:
            self.event_log.append(f"H2:{branch}:hard-wrong-read-failure-after-2S")
            self._end_candidate_contact()
            return Resolution(True, False, f"{branch} wrong-pressure hard failure")

        kind = "cut" if branch == "Duplieren" else "thrust"
        height = "high" if branch == "Duplieren" else "low"
        self.pending_bind_attack = BindRejoinderAttack(
            actor, defender, branch, kind, height, "boon", True, "F"
        )
        if branch == "Mutieren":
            self.crossing.retained = True
            actor.point_threat = "threatening"
            self.event_log.append("H2:Mutieren:RETAIN crossing+SET point=threatening")
        self.event_log.append(f"H2:{branch}:booned-{kind}:no-additional-action")
        return Resolution(True, True, f"{branch} declared")

    def counter_wind(self, defender: Fighter, defence_rolls: tuple[int, ...]) -> Resolution:
        """The v0.1 scoped Counter-Wind is explicitly deferred in H2."""
        return Resolution(False, reason="Counter-Wind is deferred in H2")

    def declare_durchwechseln(self, attacker: Fighter, defender: Fighter, attack) -> bool:
        """Do not insert D1 into the post-Cross bind phase."""
        if self.crossing.contact == "crossing":
            return False
        return super().declare_durchwechseln(attacker, defender, attack)

    def zornhau(self, defender: Fighter, attack_roll, defence_rolls: tuple[int, ...]) -> Resolution:
        """Preserve the inherited local Zornhau structure without H1 pressure."""
        result = super().zornhau(defender, attack_roll, defence_rolls)
        if result.success:
            self.crossing_source = "zornhau-local"
            self.crossing.bind_height = UNKNOWN
        return result

    def winden(
        self,
        actor: Fighter,
        variant: str,
        attack_rolls: tuple[int, ...],
        damage_rolls: tuple[int, ...] = (3,),
    ) -> Resolution:
        """Keep R0 W1/W2 local; ordinary H1 must use the authored Upper execution."""
        if self.crossing_source != "zornhau-local":
            return Resolution(False, reason="generic W1/W2 is not an H2 ordinary-bind action")
        return super().winden(actor, variant, attack_rolls, damage_rolls)

    def resolve_bind_rejoinder(
        self,
        attack_rolls: tuple[int, ...],
        damage_rolls: tuple[int, ...] = (3,),
    ) -> Resolution:
        result = super().resolve_bind_rejoinder(attack_rolls, damage_rolls)
        # The v0.1 method calls this class's cleanup override.
        return result

    def decline_bind_rejoinder(self, actor: Fighter) -> bool:
        if not self.rejoinder_open or self.rejoinder_actor != actor.name:
            return False
        defender = self.other(actor)
        pressure = self.crossing.pressure.get(defender.name, UNKNOWN)
        if pressure not in {HART, WEICH}:
            return False
        self.rejoinder_open = False
        self.crossing.bind_initiative = actor.name if pressure == HART else defender.name
        self._clear_initial_pressure()
        self.consecutive_bind_passes = 0
        self.crossing_source = None
        self.event_log.append(
            f"H2:Rejoinder-decline:initiative->{self.crossing.bind_initiative}+CLEAR pressure"
        )
        return True

    def upper_winding_legal(self, actor: Fighter, spiritus_cost: int = 2) -> bool:
        return (
            spiritus_cost in {1, 2}
            and WINDEN_PLAY in actor.known_plays
            and self.crossing.contact == "crossing"
            and self.crossing.bind_height == UPPER
            and self.crossing.bind_initiative == actor.name
            and actor.spiritus >= spiritus_cost
            and len(self.learned_chain) < 3
            and not self.rejoinder_open
            and self.pending_bind_attack is None
            and self.pending_upper_winding is None
        )

    def declare_upper_winding(self, actor: Fighter, spiritus_cost: int = 2) -> Resolution:
        if not self.upper_winding_legal(actor, spiritus_cost):
            return Resolution(False, reason="Upper Winding Thrust prerequisites fail")
        self.spend_spiritus(actor, spiritus_cost)
        self.add_learned_play(f"Winden:{UPPER_WINDING_THRUST}")
        self.crossing.retained = True
        self.crossing.hanging_aftermath = "ochs-upper-hanging"
        self.crossing.pressure = {name: UNKNOWN for name in self.fighters}
        actor.guard = "ochs"
        actor.point_threat = "threatening"
        self.pending_upper_winding = UpperWindingAttack(
            actor=actor,
            target=self.other(actor),
            spiritus_cost=spiritus_cost,
        )
        self.consecutive_bind_passes = 0
        self.event_log.append(
            f"H2:Upper-Winding:declare:{spiritus_cost}S+chain:RETAIN+SET Ochs+SET point"
        )
        return Resolution(True, True, "Upper Winding Thrust declared")

    def resolve_upper_winding(
        self,
        attack_rolls: tuple[int, ...],
        damage_rolls: tuple[int, ...] = (3,),
    ) -> Resolution:
        winding = self.pending_upper_winding
        if winding is None or winding.phase != "declared":
            return Resolution(False, reason="no pending Upper Winding Thrust")
        result = self.test(winding.actor.skill, attack_rolls, "normal")
        winding.phase = "resolved"
        self.pending_upper_winding = None
        if result.success:
            amount = self.damage(damage_rolls)
            winding.target.hp -= amount
            self.event_log.append("H2:Upper-Winding:hit:normal-damage+CLEAR contact")
            self._end_candidate_contact()
            return Resolution(True, True, "Upper Winding Thrust hit", amount, list(self.event_log), result)

        self.crossing.contact = "crossing"
        self.crossing.retained = True
        self.crossing.hanging_aftermath = "ochs-upper-hanging"
        self.crossing.bind_initiative = winding.target.name
        self.crossing.pressure = {name: UNKNOWN for name in self.fighters}
        self.event_log.append(
            f"H2:Upper-Winding:miss:RETAIN+initiative->{winding.target.name}+no Open/no Boon"
        )
        return Resolution(True, False, "Upper Winding Thrust missed", 0, list(self.event_log), result)

    def pass_bind_initiative(self, actor: Fighter) -> bool:
        if (
            self.crossing.contact != "crossing"
            or self.crossing.bind_initiative != actor.name
            or self.rejoinder_open
            or self.pending_upper_winding is not None
        ):
            return False
        self.consecutive_bind_passes += 1
        if self.consecutive_bind_passes >= 2:
            self.event_log.append("H2:two-consecutive-passes:CLEAR crossing")
            self._end_candidate_contact()
            return True
        self.crossing.bind_initiative = self.other(actor).name
        self.event_log.append(f"H2:bind-pass:initiative->{self.crossing.bind_initiative}")
        return True

    def disengage(self, actor: Fighter) -> bool:
        if (
            self.crossing.contact != "crossing"
            or self.crossing.bind_initiative != actor.name
            or self.pending_upper_winding is not None
        ):
            return False
        self.event_log.append(f"H2:Disengage:{actor.name}:CLEAR crossing:no-Nachreisen")
        self._end_candidate_contact()
        return True

    def _clear_initial_pressure(self) -> None:
        self.crossing.pressure = {name: UNKNOWN for name in self.fighters}

    def _end_candidate_contact(self) -> None:
        measure = self.crossing.measure
        self.crossing = CandidateCrossing(measure=measure)
        self.rejoinder_open = False
        self.rejoinder_actor = None
        self.pending_bind_attack = None
        self.pending_upper_winding = None
        self.consecutive_bind_passes = 0


def make_successful_h2_cross(
    *,
    pressure: str = HART,
    attacker_plays=(),
    defender_plays=(),
    attacker_skill: int = 14,
    defender_skill: int = 14,
    attacker_spiritus: int = 8,
    defender_spiritus: int = 8,
    qualifying_upper: bool = True,
):
    """Deterministic qualifying/nonqualifying H2 fixture."""
    attacker = Fighter(
        "A",
        skill=attacker_skill,
        spiritus=attacker_spiritus,
        known_plays=set(attacker_plays),
    )
    defender = Fighter(
        "B",
        skill=defender_skill,
        spiritus=defender_spiritus,
        known_plays=set(defender_plays),
    )
    engine = HartWeichUpperWindenEngine([attacker, defender])
    kind = "descending-cut" if qualifying_upper else "thrust"
    attack = engine.declare_attack(
        attacker,
        defender,
        kind,
        descending=qualifying_upper,
    )
    assert attack is not None
    rolled = engine.roll_pending_attack((5,))
    assert rolled.success and rolled.roll is not None
    assert engine.declare_h1_cross(defender, pressure)
    crossed = engine.resolve_h1_cross(defender, (6, 16) if pressure == HART else (6,))
    assert crossed.success
    return engine, attacker, defender

"""Isolated H1/F1/D-M/Counter-Wind candidate layer.

This module subclasses the authoritative governing-provisional exchange engine
without changing it.  It is deterministic-friendly and intentionally models
only the bounded ordinary-Basic-Cross experiment described by the prototype.
"""

from __future__ import annotations

from dataclasses import dataclass

from simulations.shared.provisional_longsword_engine import (
    Attack,
    Crossing,
    Fighter,
    ProvisionalLongswordEngine,
    Resolution,
)


HART = "hart"
WEICH = "weich"
UNKNOWN = "unknown"
PAIRED_PLAY = "Duplieren / Mutieren"
COUNTER_WIND = "Scoped Counter-Wind"
REJOINDER_PLAYS = ("Duplieren", "Mutieren")


@dataclass
class BindRejoinderAttack:
    actor: Fighter
    target: Fighter
    branch: str
    kind: str
    height: str
    accuracy: str
    correct_read: bool
    wrong_read_model: str
    phase: str = "declared"
    cancelled: bool = False


class GeneralBindCandidateEngine(ProvisionalLongswordEngine):
    """Candidate-only additions for ordinary successful Basic Crosses."""

    def __init__(self, fighters):
        super().__init__(fighters)
        self.declared_pressure: tuple[str, str] | None = None
        self.bind_serial = 0
        self.fuhlen_purchases: set[tuple[int, str]] = set()
        self.fuhlen_reveals: dict[tuple[int, str], str] = {}
        self.rejoinder_actor: str | None = None
        self.rejoinder_open = False
        self.pending_bind_attack: BindRejoinderAttack | None = None

    def declare_h1_cross(self, defender: Fighter, pressure: str) -> bool:
        attack = self.pending_attack
        if (
            pressure not in {HART, WEICH}
            or attack is None
            or attack.phase != "rolled"
            or not attack.hit
            or defender is not attack.target
            or not defender.action_available
            or self.declared_pressure is not None
        ):
            return False
        self.declared_pressure = (defender.name, pressure)
        self.event_log.append(f"H1:declare-hidden-pressure:{defender.name}:{pressure}")
        return True

    def resolve_h1_cross(self, defender: Fighter, defence_rolls: tuple[int, ...]) -> Resolution:
        attack = self.pending_attack
        if (
            attack is None
            or self.declared_pressure is None
            or self.declared_pressure[0] != defender.name
            or defender is not attack.target
        ):
            return Resolution(False, reason="no valid H1 Cross declaration")
        pressure = self.declared_pressure[1]
        self.declared_pressure = None
        if not self.spend_action(defender):
            return Resolution(False, reason="action unavailable")
        modifier = "boon" if pressure == HART else "normal"
        result = self.test(defender.skill, defence_rolls, modifier)
        self.event_log.append(f"H1:Cross-roll:{modifier}")
        if not result.success:
            # A declaration that fails never becomes persistent pressure state.
            self.event_log.append("H1:failed-Cross:no-pressure-state")
            return Resolution(True, False, "failed H1 Basic Cross", events=list(self.event_log), roll=result)

        attack.cancelled = True
        attack.phase = "cancelled"
        self.bind_serial += 1
        self.crossing = Crossing(
            contact="crossing",
            measure=self.crossing.measure,
            contact_zone={defender.name: UNKNOWN, attack.actor.name: UNKNOWN},
            pressure={defender.name: pressure, attack.actor.name: UNKNOWN},
            bind_position={defender.name: UNKNOWN, attack.actor.name: UNKNOWN},
            bind_initiative=None,
        )
        self.rejoinder_actor = attack.actor.name
        self.rejoinder_open = True
        self.pending_bind_attack = None
        self.event_log.append("H1:Cross:CANCEL+SET crossing+open Bind Rejoinder")
        return Resolution(True, True, "successful H1 Basic Cross", events=list(self.event_log), roll=result)

    def pressure_view(self, viewer: Fighter, subject: Fighter) -> str:
        actual = self.crossing.pressure.get(subject.name, UNKNOWN)
        if viewer is subject:
            return actual
        return self.fuhlen_reveals.get((self.bind_serial, viewer.name), UNKNOWN)

    def buy_fuhlen(self, actor: Fighter) -> str | None:
        if (
            "Fühlen" not in actor.known_plays
            or self.crossing.contact != "crossing"
            or actor.spiritus < 1
            or (self.bind_serial, actor.name) in self.fuhlen_purchases
        ):
            return None
        self.spend_spiritus(actor, 1)
        opponent = self.other(actor)
        revealed = self.crossing.pressure.get(opponent.name, UNKNOWN)
        if revealed not in {HART, WEICH}:
            revealed = "Unknown"
        self.fuhlen_purchases.add((self.bind_serial, actor.name))
        self.fuhlen_reveals[(self.bind_serial, actor.name)] = revealed.lower()
        self.event_log.append(f"F1:Fühlen:{actor.name}:{revealed}")
        return revealed

    def rejoinder_options(self, actor: Fighter) -> list[str]:
        if not self.rejoinder_open or self.rejoinder_actor != actor.name:
            return []
        if self.crossing.contact != "crossing" or self.crossing.measure != "wide":
            return []
        if PAIRED_PLAY not in actor.known_plays or actor.spiritus < 2 or len(self.learned_chain) >= 3:
            return []
        return list(REJOINDER_PLAYS)

    def declare_bind_rejoinder(
        self,
        actor: Fighter,
        branch: str,
        wrong_read_model: str,
    ) -> Resolution:
        if branch not in self.rejoinder_options(actor):
            return Resolution(False, reason="Bind Rejoinder prerequisites fail")
        if wrong_read_model not in {"G", "F"}:
            return Resolution(False, reason="unknown wrong-read model")
        self.spend_spiritus(actor, 2)
        self.add_learned_play(f"{PAIRED_PLAY}:{branch}")
        self.rejoinder_open = False
        defender = self.other(actor)
        pressure = self.crossing.pressure.get(defender.name, UNKNOWN)
        correct = (branch == "Duplieren" and pressure == HART) or (branch == "Mutieren" and pressure == WEICH)
        if wrong_read_model == "F" and not correct:
            self.event_log.append(f"{branch}:hard-failure-after-spend")
            self._end_candidate_contact()
            return Resolution(True, False, f"{branch} wrong-pressure hard failure")

        accuracy = "boon" if correct else "bane"
        kind = "cut" if branch == "Duplieren" else "thrust"
        height = "high" if branch == "Duplieren" else "low"
        self.pending_bind_attack = BindRejoinderAttack(
            actor, defender, branch, kind, height, accuracy, correct, wrong_read_model
        )
        if branch == "Mutieren":
            self.crossing.retained = True
            actor.point_threat = "threatening"
            self.event_log.append("Mutieren:winding-transition:RETAIN crossing+SET point=threatening")
        self.event_log.append(f"{branch}:declare:{accuracy}:no-additional-action")
        return Resolution(True, True, f"{branch} declared")

    def counter_wind(self, defender: Fighter, defence_rolls: tuple[int, ...]) -> Resolution:
        bind_attack = self.pending_bind_attack
        if (
            bind_attack is None
            or bind_attack.branch != "Duplieren"
            or bind_attack.phase != "declared"
            or defender is not bind_attack.target
            or COUNTER_WIND not in defender.known_plays
            or defender.spiritus < 1
            or len(self.learned_chain) >= 3
        ):
            return Resolution(False, reason="scoped Counter-Wind prerequisites fail")
        self.spend_spiritus(defender, 1)
        self.add_learned_play(COUNTER_WIND)
        result = self.test(defender.skill, defence_rolls, "normal")
        self.event_log.append("Counter-Wind:normal-defence-test")
        if result.success:
            bind_attack.cancelled = True
            bind_attack.phase = "cancelled"
            self.pending_bind_attack = None
            self.crossing.retained = True
            self.crossing.bind_initiative = defender.name
            self.event_log.append("Counter-Wind:CANCEL Duplieren+RETAIN crossing+SET Bind Initiative")
            return Resolution(True, True, "Counter-Wind succeeded", 0, list(self.event_log), result)
        self.event_log.append("Counter-Wind:failed:no-Duplieren-modifier")
        return Resolution(True, False, "Counter-Wind failed", 0, list(self.event_log), result)

    def resolve_bind_rejoinder(
        self,
        attack_rolls: tuple[int, ...],
        damage_rolls: tuple[int, ...] = (3,),
    ) -> Resolution:
        bind_attack = self.pending_bind_attack
        if bind_attack is None or bind_attack.phase != "declared":
            return Resolution(False, reason="no pending Bind Rejoinder attack")
        result = self.test(bind_attack.actor.skill, attack_rolls, bind_attack.accuracy)
        amount = self.damage(damage_rolls) if result.success else 0
        if result.success:
            bind_attack.target.hp -= amount
        bind_attack.phase = "resolved"
        self.pending_bind_attack = None
        self.event_log.append(f"{bind_attack.branch}:normal-{bind_attack.kind}-resolved")
        self._end_candidate_contact()
        return Resolution(True, result.success, f"{bind_attack.branch} resolved", amount, list(self.event_log), result)

    def decline_bind_rejoinder(self, actor: Fighter) -> bool:
        if not self.rejoinder_open or self.rejoinder_actor != actor.name:
            return False
        self.rejoinder_open = False
        defender = self.other(actor)
        pressure = self.crossing.pressure.get(defender.name, UNKNOWN)
        self.crossing.bind_initiative = actor.name if pressure == HART else defender.name
        self.event_log.append(f"Bind-Rejoinder:declined:initiative->{self.crossing.bind_initiative}")
        return True

    def disengage(self, actor: Fighter) -> bool:
        if self.crossing.contact != "crossing" or self.crossing.bind_initiative != actor.name:
            return False
        self.event_log.append(f"Disengage:{actor.name}:CLEAR crossing")
        self._end_candidate_contact()
        return True

    def pass_bind_initiative(self, actor: Fighter) -> bool:
        if self.crossing.contact != "crossing" or self.crossing.bind_initiative != actor.name:
            return False
        if not self.crossing.initiative_passed:
            self.crossing.bind_initiative = self.other(actor).name
            self.crossing.initiative_passed = True
            return True
        self._end_candidate_contact()
        return True

    def _end_candidate_contact(self) -> None:
        measure = self.crossing.measure
        self.crossing = Crossing(measure=measure)
        self.rejoinder_open = False
        self.rejoinder_actor = None


def make_successful_h1_cross(
    *, pressure: str = HART, attacker_plays=(), defender_plays=(), skill: int = 14
):
    """Small deterministic fixture used by tests and branch diagrams."""
    attacker = Fighter("A", skill=skill, known_plays=set(attacker_plays))
    defender = Fighter("B", skill=skill, known_plays=set(defender_plays))
    engine = GeneralBindCandidateEngine([attacker, defender])
    attack = engine.declare_attack(attacker, defender, "cut")
    assert attack is not None
    rolled = engine.roll_pending_attack((5,))
    assert rolled.success and rolled.roll is not None
    assert engine.declare_h1_cross(defender, pressure)
    crossed = engine.resolve_h1_cross(defender, (6, 16) if pressure == HART else (6,))
    assert crossed.success
    return engine, attacker, defender

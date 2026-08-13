"""Isolated E1/L1 T1 and Pommel v0.2 overlay.

The authoritative engine is inherited without modifying its H3 implementation.
This module inserts an explicit candidate decision window between a successful
qualifying Cross and use of the already-open H3 Rejoinder.  Declining that
window returns control to the governing H3 methods unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass

from simulations.shared.provisional_longsword import (
    CurrentEngine,
    ENGINE,
    Fighter,
    HART,
    UNKNOWN,
    WEICH,
)


T1 = "Tutta Cover-to-Stretto"
POMMEL = "Pommel Strike"
TUTTA_GUARD = "tutta-porta-di-ferro"


@dataclass
class PendingPommel:
    actor: Fighter
    target: Fighter
    cost: int
    phase: str = "declared"


class CandidateEngine(CurrentEngine):
    """Authoritative shared engine plus one explicitly non-governing overlay."""

    def __init__(self, fighters, *, timing: str = "E1", pommel_cost: int = 2) -> None:
        if timing not in {"E1", "L1"}:
            raise ValueError("timing must be E1 or L1")
        if pommel_cost not in {1, 2}:
            raise ValueError("Pommel cost must be P1=1 or P2=2")
        # Keep this archived candidate's own E1/L1 comparison isolated from
        # the later governing E1 promotion in the shared engine.
        super().__init__(fighters, enable_governing_t1=False)
        self.timing = timing
        self.pommel_cost = pommel_cost
        self.early_t1_window_actor: str | None = None
        self.early_t1_original_striker: str | None = None
        self.late_t1_qualifying_actor: str | None = None
        self.pending_pommel: PendingPommel | None = None
        self.candidate_point_threat_events = 0
        self.candidate_response_restrictions: tuple[str, ...] = ()

    def _qualifying_t1_cross(self, actor: Fighter) -> bool:
        attack = self.pending_attack
        normalized = attack.kind.lower().replace("_", "-") if attack else ""
        return bool(
            actor.alive
            and self.other(actor).alive
            and actor.guard == TUTTA_GUARD
            and T1 in actor.known_plays
            and attack is not None
            and attack.target is actor
            and attack.cancelled
            and normalized in {"cut", "basic-cut"}
            and not attack.power
            and not attack.committed
            and attack.allows_attacker_continuations
            and self.crossing.source == "ordinary-basic-cross"
            and self.crossing.contact == "crossing"
            and self.crossing.measure == "wide"
            and self.crossing.initial_pressure.get(actor.name, UNKNOWN) in {HART, WEICH}
            and actor.spiritus >= 1
            and len(self.learned_chain) < ENGINE.LEARNED_PLAY_CAP
        )

    def basic_defence(self, form, defender, attack_roll, defence_rolls):
        """Expose E1 after D1/Cross resolution and before any H3 use."""
        result = super().basic_defence(form, defender, attack_roll, defence_rolls)
        if (
            form == "Cross"
            and result.success
            and self._qualifying_t1_cross(defender)
        ):
            if self.timing == "E1":
                self.early_t1_window_actor = defender.name
                self.early_t1_original_striker = self.other(defender).name
                self.event_log.append("candidate:E1-window:after-D1:before-H3-Rejoinder-use")
            else:
                self.late_t1_qualifying_actor = defender.name
                self.event_log.append("candidate:L1-qualified:governing-H3-Rejoinder-first")
        return result

    def _blocked_by_e1_window(self, actor: Fighter) -> bool:
        return self.early_t1_window_actor is not None and actor.name != self.early_t1_window_actor

    def rejoinder_options(self, actor: Fighter) -> list[str]:
        if self.early_t1_window_actor is not None:
            return []
        return super().rejoinder_options(actor)

    def buy_fuhlen(self, actor: Fighter) -> str | None:
        if self.early_t1_window_actor is not None:
            return None
        return super().buy_fuhlen(actor)

    def declare_bind_rejoinder(self, actor: Fighter, branch: str):
        if self.early_t1_window_actor is not None:
            return ENGINE.Resolution(False, reason="E1 decision precedes H3 Rejoinder")
        return super().declare_bind_rejoinder(actor, branch)

    def decline_bind_rejoinder(self, actor: Fighter) -> bool:
        if self.early_t1_window_actor is not None:
            return False
        return super().decline_bind_rejoinder(actor)

    def early_t1_legal(self, actor: Fighter) -> bool:
        return bool(
            self.timing == "E1"
            and self.early_t1_window_actor == actor.name
            and self.rejoinder_open
            and self._qualifying_t1_cross(actor)
        )

    def decline_early_t1(self, actor: Fighter) -> bool:
        if self.early_t1_window_actor != actor.name:
            return False
        self.early_t1_window_actor = None
        self.early_t1_original_striker = None
        self.event_log.append("candidate:E1-decline:governing-H3-unchanged")
        return True

    def declare_early_t1(self, actor: Fighter) -> bool:
        if not self.early_t1_legal(actor):
            return False
        pressure = self.crossing.initial_pressure.get(actor.name, UNKNOWN)
        striker_name = self.early_t1_original_striker
        if pressure not in {HART, WEICH} or striker_name is None:
            return False
        if not self.spend_spiritus(actor, 1):
            return False
        if not self.add_learned_play(T1):
            actor.spiritus += 1
            return False
        self.crossing.retained = True
        self.crossing.measure = "close"
        self.crossing.bind_height = UNKNOWN
        self.crossing.bind_initiative = striker_name if pressure == HART else actor.name
        self.crossing.initiative_passed = False
        self.consecutive_bind_passes = 0
        self._clear_initial_pressure()
        self._close_rejoinder()
        self.early_t1_window_actor = None
        self.early_t1_original_striker = None
        self.event_log.append(
            f"candidate:E1:T1:1S+chain:RETAIN crossing:SET close+height=unknown:"
            f"opportunity->{self.crossing.bind_initiative}:CLEAR pressure"
        )
        return True

    def late_t1_legal(self, actor: Fighter) -> bool:
        return bool(
            self.timing == "L1"
            and self.late_t1_qualifying_actor == actor.name
            and actor.alive
            and self.other(actor).alive
            and actor.guard == TUTTA_GUARD
            and T1 in actor.known_plays
            and self.crossing.source == "ordinary-basic-cross"
            and self.crossing.contact == "crossing"
            and self.crossing.measure == "wide"
            and actor.spiritus >= 1
            and len(self.learned_chain) < ENGINE.LEARNED_PLAY_CAP
            and not self.rejoinder_open
            and self.crossing.bind_initiative == actor.name
            and self.pending_bind_attack is None
            and self.pending_winding is None
        )

    def declare_late_t1(self, actor: Fighter) -> bool:
        if not self.late_t1_legal(actor):
            return False
        if not self.spend_spiritus(actor, 1):
            return False
        if not self.add_learned_play(T1):
            actor.spiritus += 1
            return False
        self.crossing.retained = True
        self.crossing.measure = "close"
        self.crossing.bind_height = UNKNOWN
        self.crossing.initiative_passed = False
        self.consecutive_bind_passes = 0
        self.late_t1_qualifying_actor = None
        self.event_log.append("candidate:L1:T1:ordinary-opportunity:1S+chain:SET close+height=unknown")
        return True

    def pommel_legal(self, actor: Fighter, *, cost: int | None = None) -> bool:
        price = self.pommel_cost if cost is None else cost
        return bool(
            price in {1, 2}
            and actor.alive
            and self.other(actor).alive
            and POMMEL in actor.known_plays
            and self.crossing.contact == "crossing"
            and self.crossing.measure == "close"
            and self.crossing.bind_initiative == actor.name
            and actor.spiritus >= price
            and len(self.learned_chain) < ENGINE.LEARNED_PLAY_CAP
            and not self.rejoinder_open
            and self.pending_bind_attack is None
            and self.pending_winding is None
            and self.pending_pommel is None
        )

    def declare_pommel(self, actor: Fighter, *, cost: int | None = None):
        price = self.pommel_cost if cost is None else cost
        if not self.pommel_legal(actor, cost=price):
            return ENGINE.Resolution(False, reason="Pommel prerequisites fail")
        self.spend_spiritus(actor, price)
        self.add_learned_play(POMMEL)
        self.crossing.retained = True
        self.crossing.bind_height = UNKNOWN
        self.crossing.initiative_passed = False
        self.consecutive_bind_passes = 0
        self.pending_pommel = PendingPommel(actor, self.other(actor), price)
        self.event_log.append(
            f"candidate:Pommel:declare:{price}S+chain:no-action:ATTACK flat-normal:"
            "no-intrinsic-response-restriction"
        )
        return ENGINE.Resolution(True, True, "Pommel declared", events=list(self.event_log))

    def resolve_pommel(self, attack_rolls: tuple[int, ...], damage_rolls: tuple[int, ...] = (3,)):
        pending = self.pending_pommel
        if (
            pending is None
            or pending.phase != "declared"
            or not pending.actor.alive
            or not pending.target.alive
        ):
            if pending is not None:
                self._end_bind_sequence()
                self.pending_pommel = None
            return ENGINE.Resolution(False, reason="no live pending Pommel")
        roll = self.test(pending.actor.skill, attack_rolls, "normal")
        pending.phase = "resolved"
        self.pending_pommel = None
        if roll.success:
            amount = self.damage(damage_rolls, "normal")
            pending.target.hp -= amount
            self.event_log.append("candidate:Pommel:hit:normal-damage:CLEAR contact")
            self._end_bind_sequence()
            return ENGINE.Resolution(True, True, "Pommel hit", amount, list(self.event_log), roll)
        self.crossing.contact = "crossing"
        self.crossing.measure = "close"
        self.crossing.bind_height = UNKNOWN
        self.crossing.retained = True
        self.crossing.bind_initiative = pending.target.name
        self.crossing.initiative_passed = False
        self.consecutive_bind_passes = 0
        self.event_log.append(
            f"candidate:Pommel:miss:zero-damage:RETAIN close:opportunity->{pending.target.name}"
        )
        return ENGINE.Resolution(True, False, "Pommel missed", 0, list(self.event_log), roll)

    def continuation_options(self, actor: Fighter, *, winden_variant: str = "W2") -> list[str]:
        options = super().continuation_options(actor, winden_variant=winden_variant)
        if self.pommel_legal(actor):
            options.insert(0, POMMEL)
        return options

    def pass_bind_initiative(self, actor: Fighter) -> bool:
        if self.pending_pommel is not None:
            return False
        return super().pass_bind_initiative(actor)

    def disengage(self, actor: Fighter) -> bool:
        if self.pending_pommel is not None:
            return False
        return super().disengage(actor)

    def finish_exchange(self) -> None:
        self.early_t1_window_actor = None
        self.early_t1_original_striker = None
        self.late_t1_qualifying_actor = None
        self.pending_pommel = None
        super().finish_exchange()

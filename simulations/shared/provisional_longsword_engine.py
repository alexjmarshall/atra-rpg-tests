"""Authoritative governing-provisional longsword rules engine.

This module is deliberately exchange-focused.  Archived duel simulators remain
available for reproducing old reports, but new behavioral evidence should use
this state machine rather than inheriting their superseded policy shortcuts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


MAX_HP = 8
MAX_SPIRITUS = 8
LEARNED_PLAY_CAP = 3
NORMAL_DAMAGE = (2, 3, 4, 5, 6, 7)
OPEN = "open"


@dataclass(frozen=True)
class RollResult:
    success: bool
    value: int
    rolls: tuple[int, ...]
    modifier: str = "normal"


@dataclass
class Fighter:
    name: str
    skill: int = 14
    hp: int = MAX_HP
    spiritus: int = MAX_SPIRITUS
    action_available: bool = True
    guard: str = "vom-tag"
    point_threat: str = "not_threatening"
    known_plays: set[str] = field(default_factory=set)
    guard_change_available: bool = True
    activation_action_taken: bool = False

    @property
    def alive(self) -> bool:
        return self.hp > 0

    @property
    def loaded(self) -> bool:
        return self.guard == "posta-di-donna"


@dataclass
class Attack:
    actor: Fighter
    target: Fighter
    kind: str
    committed: bool = False
    descending: bool = False
    power: bool = False
    accuracy: str = "normal"
    damage_mode: str = "normal"
    allows_attacker_continuations: bool = True
    phase: str = "declared"
    attack_roll: RollResult | None = None
    hit: bool | None = None
    damage: int = 0
    cancelled: bool = False
    declaration_window_used: bool = False
    original_target: Fighter | None = None

    def __post_init__(self) -> None:
        if self.original_target is None:
            self.original_target = self.target


@dataclass
class Crossing:
    contact: str = "none"
    measure: str = "wide"
    contact_zone: dict[str, str] = field(default_factory=dict)
    pressure: dict[str, str] = field(default_factory=dict)
    bind_position: dict[str, str] = field(default_factory=dict)
    bind_initiative: str | None = None
    retained: bool = False
    initiative_passed: bool = False
    tie_breaks: int = 0
    hanging_aftermath: str | None = None


@dataclass
class Resolution:
    legal: bool
    success: bool = False
    reason: str = ""
    damage: int = 0
    events: list[str] = field(default_factory=list)
    roll: RollResult | None = None


class ProvisionalLongswordEngine:
    """Deterministic-friendly implementation of the current shared baseline."""

    def __init__(self, fighters: Iterable[Fighter]) -> None:
        self.fighters = {fighter.name: fighter for fighter in fighters}
        self.crossing = Crossing()
        self.learned_chain: list[str] = []
        self.pending_attack: Attack | None = None
        self.recovery_nachreisen_target: str | None = None
        self.recovery_nachreisen_immediate = False
        self.displacement_events: list[dict[str, str]] = []
        self.event_log: list[str] = []

    @staticmethod
    def test(skill: int, rolls: tuple[int, ...], modifier: str = "normal") -> RollResult:
        if modifier == "boon":
            value = min(rolls)
        elif modifier == "bane":
            value = max(rolls)
        else:
            value = rolls[0]
        return RollResult(value <= skill, value, tuple(rolls), modifier)

    @staticmethod
    def damage(rolls: tuple[int, ...], modifier: str = "normal") -> int:
        if modifier == "damage_boon":
            die = max(rolls)
        elif modifier == "damage_bane":
            die = min(rolls)
        else:
            die = rolls[0]
        return die + 1

    def other(self, actor: Fighter) -> Fighter:
        return next(f for f in self.fighters.values() if f is not actor)

    def begin_activation(self, actor: Fighter) -> None:
        actor.guard_change_available = True
        actor.activation_action_taken = False

    def change_guard(self, actor: Fighter, guard: str, timing: str = "before_action") -> bool:
        if timing != "before_action" or actor.activation_action_taken:
            return False
        if not actor.guard_change_available or guard == OPEN:
            return False
        actor.guard = guard
        actor.guard_change_available = False
        actor.point_threat = "threatening" if guard in {"ochs", "pflug", "mezza-porta-di-ferro"} else "not_threatening"
        self.event_log.append(f"{actor.name}:guard->{guard}")
        return True

    def recover_open(self, actor: Fighter, guard: str) -> bool:
        if actor.guard != OPEN:
            return False
        return self.change_guard(actor, guard, "before_action")

    @staticmethod
    def spend_action(actor: Fighter) -> bool:
        if not actor.action_available:
            return False
        actor.action_available = False
        actor.activation_action_taken = True
        return True

    @staticmethod
    def spend_spiritus(actor: Fighter, amount: int) -> bool:
        if actor.spiritus < amount:
            return False
        actor.spiritus -= amount
        return True

    def add_learned_play(self, name: str) -> bool:
        if len(self.learned_chain) >= LEARNED_PLAY_CAP:
            return False
        self.learned_chain.append(name)
        return True

    def d1_window(self, defender: Fighter, attack: Attack | None = None) -> bool:
        """D1 is denied by a threatening opposing point, never contact or form."""
        return (
            defender.point_threat != "threatening"
            and (attack is None or attack.allows_attacker_continuations)
        )

    def declare_durchwechseln(self, attacker: Fighter, defender: Fighter, attack: Attack) -> bool:
        if not self.d1_window(defender, attack):
            return False
        if "Durchwechseln" not in attacker.known_plays:
            return False
        if not self.spend_spiritus(attacker, 1):
            return False
        if not self.add_learned_play("Durchwechseln"):
            attacker.spiritus += 1
            return False
        self.crossing = Crossing(measure=self.crossing.measure)
        attacker.point_threat = "threatening"
        self.event_log.append("D1:replace-pending-attack")
        return True

    def declare_attack(
        self,
        actor: Fighter,
        target: Fighter,
        kind: str,
        *,
        committed: bool = False,
        descending: bool = False,
        power: bool = False,
        accuracy: str = "normal",
        damage_mode: str = "normal",
        allows_attacker_continuations: bool = True,
    ) -> Attack | None:
        if not self.spend_action(actor):
            return None
        attack = Attack(
            actor,
            target,
            kind,
            committed,
            descending,
            power,
            accuracy,
            damage_mode,
            allows_attacker_continuations,
        )
        self.pending_attack = attack
        self.recovery_nachreisen_target = None
        self.recovery_nachreisen_immediate = False
        self.event_log.append(f"declare:{kind}")
        if committed:
            self.event_log.append("window:committed-declaration")
        return attack

    def declare_power_attack(self, actor: Fighter, target: Fighter) -> Attack | None:
        if not actor.loaded or actor.spiritus < 1:
            return None
        actor.spiritus -= 1
        attack = self.declare_attack(
            actor,
            target,
            "power-cut",
            committed=True,
            descending=True,
            power=True,
            damage_mode="fixed-7",
            allows_attacker_continuations=False,
        )
        if attack is None:
            actor.spiritus += 1
        return attack

    def basic_cut_damage(self, actor: Fighter, rolls: tuple[int, ...], *, proactive: bool = True) -> int:
        modifier = "damage_boon" if proactive and actor.loaded else "normal"
        return self.damage(rolls, modifier)

    def roll_pending_attack(self, rolls: tuple[int, ...], damage_rolls: tuple[int, ...] = (3,)) -> Resolution:
        attack = self.pending_attack
        if attack is None or attack.cancelled or attack.phase != "declared":
            return Resolution(False, reason="no pending declared attack")
        result = self.test(attack.actor.skill, rolls, attack.accuracy)
        attack.attack_roll = result
        attack.hit = result.success
        attack.phase = "rolled"
        self.event_log.append("roll:pending-attack")
        if not result.success:
            self.recovery_nachreisen_target = attack.original_target.name
            self.recovery_nachreisen_immediate = attack.committed
            self.event_log.append("window:recovery-nachreisen" if attack.committed else "miss:no-recovery-window")
            return Resolution(True, False, "attack missed", events=list(self.event_log), roll=result)
        attack.damage = 7 if attack.damage_mode == "fixed-7" else self.damage(damage_rolls)
        return Resolution(True, True, "attack roll succeeded", damage=attack.damage, events=list(self.event_log), roll=result)

    def immediate_counter(
        self,
        defender: Fighter,
        rolls: tuple[int, ...],
        damage_rolls: tuple[int, ...] = (3,),
    ) -> Resolution:
        attack = self.pending_attack
        if attack is None or not attack.committed or attack.phase != "declared" or defender is not attack.original_target:
            return Resolution(False, reason="not the target's committed declaration window")
        if not self.spend_action(defender):
            return Resolution(False, reason="action unavailable")
        attack.declaration_window_used = True
        result = self.test(defender.skill, rolls)
        damage = self.damage(damage_rolls) if result.success else 0
        self.event_log.append("immediate-counter:roll-first")
        if result.success:
            attack.actor.hp -= damage
        if not attack.actor.alive:
            attack.cancelled = True
            attack.phase = "cancelled"
            self.event_log.append("committed-attack:cancelled-by-removal")
        else:
            self.event_log.append("committed-attack:proceeds")
        return Resolution(True, result.success, "immediate Counter", damage, list(self.event_log), result)

    def _nachreisen_legal(self, actor: Fighter) -> bool:
        return (
            "Nachreisen" in actor.known_plays
            and actor.action_available
            and actor.spiritus >= 1
            and len(self.learned_chain) < LEARNED_PLAY_CAP
        )

    def preparation_nachreisen(
        self,
        defender: Fighter,
        rolls: tuple[int, ...],
        damage_rolls: tuple[int, ...] = (3,),
    ) -> Resolution:
        attack = self.pending_attack
        if attack is None or not attack.committed or attack.phase != "declared" or defender is not attack.original_target:
            return Resolution(False, reason="not the target's committed Preparation window")
        if not self._nachreisen_legal(defender):
            return Resolution(False, reason="Nachreisen prerequisites fail")
        self.spend_action(defender)
        self.spend_spiritus(defender, 1)
        self.add_learned_play("Nachreisen")
        attack.declaration_window_used = True
        result = self.test(defender.skill, rolls, "boon")
        damage = self.damage(damage_rolls) if result.success else 0
        self.event_log.append("nachreisen:preparation:boon-roll-first")
        if result.success:
            attack.actor.hp -= damage
        if not attack.actor.alive:
            attack.cancelled = True
            attack.phase = "cancelled"
            self.event_log.append("committed-attack:cancelled-by-removal")
        else:
            self.event_log.append("committed-attack:proceeds")
        return Resolution(True, result.success, "Preparation Nachreisen", damage, list(self.event_log), result)

    def waiting_counter(
        self,
        defender: Fighter,
        rolls: tuple[int, ...],
        damage_rolls: tuple[int, ...] = (3,),
    ) -> Resolution:
        attack = self.pending_attack
        if attack is None or attack.phase != "rolled" or not attack.hit:
            return Resolution(False, reason="ordinary Counter exists only after a successful attack roll")
        if defender is not attack.original_target or not self.spend_action(defender):
            return Resolution(False, reason="target action unavailable")
        result = self.test(defender.skill, rolls)
        attack.target.hp -= attack.damage
        damage = self.damage(damage_rolls) if result.success else 0
        if result.success:
            attack.actor.hp -= damage
        attack.phase = "resolved"
        self.event_log.append("waiting-counter:simultaneous")
        return Resolution(True, result.success, "ordinary simultaneous Counter", damage, list(self.event_log), result)

    def recovery_nachreisen(
        self,
        defender: Fighter,
        rolls: tuple[int, ...],
        damage_rolls: tuple[int, ...] = (3,),
    ) -> Resolution:
        attack = self.pending_attack
        if (
            attack is None
            or not self.recovery_nachreisen_immediate
            or self.recovery_nachreisen_target != defender.name
            or defender is not attack.original_target
        ):
            return Resolution(False, reason="no target-specific immediate Recovery window")
        if not self._nachreisen_legal(defender):
            return Resolution(False, reason="Nachreisen prerequisites fail")
        self.spend_action(defender)
        self.spend_spiritus(defender, 1)
        self.add_learned_play("Nachreisen")
        result = self.test(defender.skill, rolls, "boon")
        damage = self.damage(damage_rolls) if result.success else 0
        if result.success:
            attack.actor.hp -= damage
        self.event_log.append("nachreisen:recovery:immediate-boon")
        self.expire_recovery_window()
        attack.phase = "resolved"
        return Resolution(True, result.success, "Recovery Nachreisen", damage, list(self.event_log), result)

    def expire_recovery_window(self) -> None:
        self.recovery_nachreisen_target = None
        self.recovery_nachreisen_immediate = False

    def _set_crossing(
        self,
        creator: Fighter,
        opponent: Fighter,
        attack_roll: RollResult | None,
        defence_roll: RollResult | None,
        *,
        pressure: str,
    ) -> None:
        self.crossing.contact = "crossing"
        self.crossing.contact_zone = {creator.name: "unknown", opponent.name: "unknown"}
        self.crossing.pressure = {creator.name: pressure, opponent.name: pressure}
        self.crossing.bind_initiative = creator.name
        self.crossing.retained = False
        self.crossing.initiative_passed = False
        self.crossing.bind_position = {creator.name: "unknown", opponent.name: "unknown"}
        if not attack_roll or not defence_roll or not attack_roll.success or not defence_roll.success:
            return
        if defence_roll.value < attack_roll.value:
            favored = creator
        elif attack_roll.value < defence_roll.value:
            favored = opponent
        else:
            favored = creator
            self.crossing.tie_breaks += 1
        unfavored = opponent if favored is creator else creator
        self.crossing.bind_position = {favored.name: "favored", unfavored.name: "unfavored"}

    def basic_defence(
        self,
        form: str,
        defender: Fighter,
        attack_roll: RollResult,
        defence_rolls: tuple[int, ...],
    ) -> Resolution:
        attack = self.pending_attack
        if attack is None or form not in {"Cross", "Beat"} or defender is not attack.target:
            return Resolution(False, reason="invalid Basic defence")
        if not self.spend_action(defender):
            return Resolution(False, reason="action unavailable")
        result = self.test(defender.skill, defence_rolls)
        if not result.success:
            return Resolution(True, False, f"failed Basic {form}", roll=result)
        attack.cancelled = True
        attack.phase = "cancelled"
        if form == "Cross":
            self._set_crossing(defender, attack.actor, attack_roll, result, pressure="hard")
            self.event_log.append("Cross:CANCEL+SET crossing")
        else:
            self.crossing = Crossing(measure=self.crossing.measure)
            self.displacement_events.append({"weapon_owner": attack.actor.name, "source": "Basic Beat", "contact_after": "none"})
            attack.actor.guard = OPEN
            attack.actor.point_threat = "not_threatening"
            self.event_log.append("Beat:CANCEL+displace+CLEAR contact+SET guard=open")
        return Resolution(True, True, f"successful Basic {form}", events=list(self.event_log), roll=result)

    def zornhau(
        self,
        defender: Fighter,
        attack_roll: RollResult,
        defence_rolls: tuple[int, ...],
    ) -> Resolution:
        attack = self.pending_attack
        if attack is None or not attack.descending or defender is not attack.target:
            return Resolution(False, reason="requires qualifying descending Cut")
        if "Zornhau-Ort" not in defender.known_plays or not defender.action_available:
            return Resolution(False, reason="Zornhau-Ort or action unavailable")
        if len(self.learned_chain) >= LEARNED_PLAY_CAP:
            return Resolution(False, reason="learned chain full")
        self.spend_action(defender)
        self.add_learned_play("Zornhau-Ort")
        result = self.test(defender.skill, defence_rolls)
        if not result.success:
            return Resolution(True, False, "Zornhau failed", roll=result)
        attack.cancelled = True
        attack.phase = "cancelled"
        defender.point_threat = "threatening"
        self._set_crossing(defender, attack.actor, attack_roll, result, pressure="unknown")
        self.event_log.append("Zornhau:CANCEL+SET crossing+SET point=threatening")
        return Resolution(True, True, "Zornhau succeeded", events=list(self.event_log), roll=result)

    def bind_view(self, actor: Fighter) -> str:
        actual = self.crossing.bind_position.get(actor.name, "unknown")
        if actual == "unknown" or "Fühlen" not in actor.known_plays:
            return "unknown"
        return actual

    def continuation_options(self, actor: Fighter, *, winden_variant: str) -> list[str]:
        if self.crossing.contact != "crossing" or self.crossing.bind_initiative != actor.name:
            return []
        actual = self.crossing.bind_position.get(actor.name, "unknown")
        view = self.bind_view(actor)
        options: list[str] = []
        if "Zornhau-Ort" in actor.known_plays and actor.spiritus >= 1:
            if view in {"unknown", "favored"}:
                options.append("Ort")
        if "Winden" in actor.known_plays and actor.spiritus >= 1 and len(self.learned_chain) < LEARNED_PLAY_CAP:
            if winden_variant == "W2" or view in {"unknown", "unfavored"}:
                options.append("Winden")
        return options

    def ort(self, actor: Fighter, damage_model: str, damage_rolls: tuple[int, ...]) -> Resolution:
        if self.crossing.contact != "crossing" or self.crossing.bind_initiative != actor.name:
            return Resolution(False, reason="no immediate bind initiative")
        if "Zornhau-Ort" not in actor.known_plays or actor.spiritus < 1:
            return Resolution(False, reason="Ort prerequisites fail")
        self.spend_spiritus(actor, 1)
        actual = self.crossing.bind_position.get(actor.name, "unknown")
        if actual != "favored":
            self.event_log.append("Ort:failed-hidden-requirement")
            return Resolution(True, False, "Ort requires Favored Bind; Spiritus lost", events=list(self.event_log))
        modifier = "normal" if damage_model == "O1" else "damage_bane"
        amount = self.damage(damage_rolls, modifier)
        self.other(actor).hp -= amount
        self.event_log.append(f"Ort:{damage_model}:no-second-attack-roll")
        return Resolution(True, True, "Ort succeeded", amount, list(self.event_log))

    def winden(
        self,
        actor: Fighter,
        variant: str,
        attack_rolls: tuple[int, ...],
        damage_rolls: tuple[int, ...] = (3,),
    ) -> Resolution:
        if self.crossing.contact != "crossing" or self.crossing.bind_initiative != actor.name:
            return Resolution(False, reason="no immediate bind initiative")
        if "Winden" not in actor.known_plays or actor.spiritus < 1 or len(self.learned_chain) >= LEARNED_PLAY_CAP:
            return Resolution(False, reason="Winden prerequisites fail")
        self.spend_spiritus(actor, 1)
        self.add_learned_play("Winden")
        actual = self.crossing.bind_position.get(actor.name, "unknown")
        if variant == "W1" and actual != "unfavored":
            self.event_log.append("Winden:W1-failed-hidden-requirement")
            return Resolution(True, False, "W1 requires Unfavored Bind; Spiritus lost", events=list(self.event_log))
        self.crossing.retained = True
        self.crossing.hanging_aftermath = "appropriate upper/lower Ochs-or-Pflug hanging (side unresolved)"
        actor.point_threat = "threatening"
        result = self.test(actor.skill, attack_rolls)
        amount = self.damage(damage_rolls) if result.success else 0
        if result.success:
            self.other(actor).hp -= amount
        self.event_log.append(f"Winden:{variant}:RETAIN crossing+normal thrust")
        return Resolution(True, result.success, "Winden thrust", amount, list(self.event_log), result)

    def decline_bind_continuations(self, actor: Fighter) -> bool:
        if self.crossing.bind_initiative != actor.name:
            return False
        if not self.crossing.initiative_passed:
            self.crossing.bind_initiative = self.other(actor).name
            self.crossing.initiative_passed = True
            self.event_log.append("bind-initiative:passed-once")
            return True
        self.cleanup_crossing()
        return True

    def tutta_cover_to_stretto(self, actor: Fighter) -> bool:
        if (
            actor.guard != "tutta-porta-di-ferro"
            or "Tutta Cover-to-Stretto" not in actor.known_plays
            or self.crossing.contact != "crossing"
            or self.crossing.measure != "wide"
            or actor.spiritus < 1
            or len(self.learned_chain) >= LEARNED_PLAY_CAP
        ):
            return False
        self.spend_spiritus(actor, 1)
        self.add_learned_play("Tutta Cover-to-Stretto")
        self.crossing.retained = True
        self.crossing.measure = "close"
        return True

    def compound_response(
        self,
        name: str,
        defender: Fighter,
        defence_rolls: tuple[int, ...],
        damage_rolls: tuple[int, ...] = (3,),
    ) -> Resolution:
        if name not in {"Absetzen", "Scambiar di Punta", "Schielhau"}:
            return Resolution(False, reason="not a governing C2 compound")
        attack = self.pending_attack
        if attack is None or defender is not attack.target or defender.spiritus < 2 or not defender.action_available:
            return Resolution(False, reason="compound prerequisites fail")
        if name not in defender.known_plays or len(self.learned_chain) >= LEARNED_PLAY_CAP:
            return Resolution(False, reason="compound not learned or chain full")
        self.spend_action(defender)
        self.spend_spiritus(defender, 2)
        self.add_learned_play(name)
        result = self.test(defender.skill, defence_rolls)
        if not result.success:
            return Resolution(True, False, f"{name} failed", roll=result)
        attack.cancelled = True
        attack.phase = "cancelled"
        defender.point_threat = "threatening"
        amount = self.damage(damage_rolls)
        attack.actor.hp -= amount
        if name in {"Absetzen", "Scambiar di Punta"}:
            self._set_crossing(defender, attack.actor, attack.attack_roll, result, pressure="unknown")
        else:
            self.crossing = Crossing(measure=self.crossing.measure)
        return Resolution(True, True, f"{name} C2 succeeded", amount, roll=result)

    def attempt_attacker_continuation(self, actor: Fighter, name: str) -> bool:
        attack = self.pending_attack
        if attack is not None and attack.actor is actor and not attack.allows_attacker_continuations:
            return False
        return self.add_learned_play(name)

    def cleanup_crossing(self) -> None:
        if self.crossing.contact == "crossing" and self.crossing.retained:
            self.crossing.retained = False
            return
        measure = self.crossing.measure
        self.crossing = Crossing(measure=measure)


def validate_authoritative_baseline() -> None:
    assert LEARNED_PLAY_CAP == 3
    assert MAX_HP == 8 and MAX_SPIRITUS == 8
    assert ProvisionalLongswordEngine.damage((1, 6), "damage_boon") == 7
    assert ProvisionalLongswordEngine.damage((1, 6), "damage_bane") == 2


validate_authoritative_baseline()

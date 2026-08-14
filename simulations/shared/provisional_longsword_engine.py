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
HART = "hart"
WEICH = "weich"
UNKNOWN = "unknown"
UPPER = "upper"
LOWER = "lower"
UPPER_CROSS = "upper-cross-against-descending-cut"
LOWER_SETTING_ASIDE = "lower-setting-aside"
UNCLASSIFIED = "unclassified"
INITIAL_PRESSURES = (HART, WEICH, UNKNOWN)
BIND_HEIGHTS = (UPPER, LOWER, UNKNOWN)
DEFENCE_GEOMETRIES = (UPPER_CROSS, LOWER_SETTING_ASIDE, UNCLASSIFIED)
PAIRED_PLAY = "Duplieren / Mutieren"
WINDEN_PLAY = "Winden"
T1_PLAY = "Tutta Cover-to-Stretto"
POMMEL_PLAY = "Pommel Strike"
TUTTA_GUARD = "tutta-porta-di-ferro"
POMMEL_COST = 2
SCHIELHAU_COST = 2
DURCHWECHSELN_COST = 1
FUHLEN_NAMES = {"Fühlen", "FÃ¼hlen"}


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


@dataclass(frozen=True)
class BasicCrossDeclaration:
    defender_name: str
    pressure_choice: str
    defence_geometry: str


@dataclass
class BindAttack:
    actor: Fighter
    target: Fighter
    branch: str
    kind: str
    height: str
    accuracy: str = "boon"
    phase: str = "declared"


@dataclass
class WindingAttack:
    actor: Fighter
    target: Fighter
    bind_height: str
    kind: str = "thrust"
    accuracy: str = "normal"
    phase: str = "declared"


@dataclass
class PommelAttack:
    actor: Fighter
    target: Fighter
    kind: str = "pommel"
    accuracy: str = "normal"
    phase: str = "declared"


@dataclass
class S2SchielhauWindow:
    schielhau_actor: Fighter
    durchwechseln_actor: Fighter
    attack: Attack
    established_roll: RollResult
    schielhau_damage_rolls: tuple[int, ...]
    phase: str = "d1-window"


@dataclass
class Crossing:
    contact: str = "none"
    measure: str = "wide"
    contact_zone: dict[str, str] = field(default_factory=dict)
    # Hard/Soft is retained only for authored legacy/special contexts.  H3
    # ordinary Cross uses the private, phase-scoped initial_pressure axis.
    pressure: dict[str, str] = field(default_factory=dict)
    initial_pressure: dict[str, str] = field(default_factory=dict)
    bind_height: str = UNKNOWN
    bind_position: dict[str, str] = field(default_factory=dict)
    bind_initiative: str | None = None
    source: str = "none"
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

    def __init__(
        self,
        fighters: Iterable[Fighter],
        *,
        enable_governing_t1: bool = True,
    ) -> None:
        self.fighters = {fighter.name: fighter for fighter in fighters}
        # Historical candidate overlays can explicitly disable the promoted
        # insertion so their archived E1/L1 comparisons remain reproducible.
        self.enable_governing_t1 = enable_governing_t1
        self.crossing = Crossing()
        self.learned_chain: list[str] = []
        self.pending_attack: Attack | None = None
        self.basic_cross_declaration: BasicCrossDeclaration | None = None
        self.bind_serial = 0
        self.rejoinder_open = False
        self.rejoinder_actor: str | None = None
        self.fuhlen_purchases: set[tuple[int, str]] = set()
        self.fuhlen_reveals: dict[tuple[int, str], str] = {}
        self.pending_bind_attack: BindAttack | None = None
        self.pending_winding: WindingAttack | None = None
        self.pending_pommel: PommelAttack | None = None
        self.s2_schielhau_window: S2SchielhauWindow | None = None
        self.t1_window_actor: str | None = None
        self.t1_original_striker: str | None = None
        self.consecutive_bind_passes = 0
        self.recovery_nachreisen_target: str | None = None
        self.recovery_nachreisen_immediate = False
        self.displacement_events: list[dict[str, str]] = []
        self.event_log: list[str] = []
        self.point_threat_events = 0

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
        if not actor.alive or timing != "before_action" or actor.activation_action_taken:
            return False
        if not actor.guard_change_available or guard == OPEN:
            return False
        actor.guard = guard
        actor.guard_change_available = False
        self._set_point_threat(
            actor,
            "threatening" if guard in {"ochs", "pflug", "mezza-porta-di-ferro"} else "not_threatening",
            "guard-change",
        )
        self.event_log.append(f"{actor.name}:guard->{guard}")
        return True

    def recover_open(self, actor: Fighter, guard: str) -> bool:
        if actor.guard != OPEN:
            return False
        return self.change_guard(actor, guard, "before_action")

    @staticmethod
    def spend_action(actor: Fighter) -> bool:
        if not actor.alive or not actor.action_available:
            return False
        actor.action_available = False
        actor.activation_action_taken = True
        return True

    @staticmethod
    def spend_spiritus(actor: Fighter, amount: int) -> bool:
        if not actor.alive or amount < 0 or actor.spiritus < amount:
            return False
        actor.spiritus -= amount
        return True

    def add_learned_play(self, name: str) -> bool:
        if len(self.learned_chain) >= LEARNED_PLAY_CAP:
            return False
        self.learned_chain.append(name)
        return True

    def _set_point_threat(self, actor: Fighter, value: str, source: str) -> None:
        """Write point state and count actual nonthreatening-to-threatening events."""
        if actor.point_threat != "threatening" and value == "threatening":
            self.point_threat_events += 1
            self.event_log.append(f"point-threat-event:{source}:{actor.name}")
        actor.point_threat = value

    def d1_window(self, defender: Fighter, attack: Attack | None = None) -> bool:
        """D1 is denied by a threatening opposing point, never contact or form."""
        return (
            defender.point_threat != "threatening"
            and (attack is None or attack.allows_attacker_continuations)
        )

    @staticmethod
    def compare_s2_rolls(
        schielhau: RollResult,
        durchwechseln: RollResult,
    ) -> str:
        """Return the selected S2 result without applying unrelated combat rules."""
        if schielhau.success and durchwechseln.success:
            return "schielhau" if schielhau.value <= durchwechseln.value else "durchwechseln"
        if schielhau.success:
            return "schielhau"
        if durchwechseln.success:
            return "durchwechseln"
        return "original-strike"

    def _clear_s2_window(self, reason: str) -> None:
        if self.s2_schielhau_window is not None:
            self.event_log.append(f"S2:cleanup:{reason}")
        self.s2_schielhau_window = None

    def _s2_window_live(self) -> bool:
        window = self.s2_schielhau_window
        if window is None:
            return False
        if not window.schielhau_actor.alive or not window.durchwechseln_actor.alive:
            window.attack.cancelled = True
            window.attack.phase = "cancelled"
            self._clear_s2_window("actor-removed")
            return False
        if (
            self.pending_attack is not window.attack
            or window.attack.cancelled
            or window.attack.phase != "rolled"
            or not window.attack.hit
        ):
            self._clear_s2_window("invalidated")
            return False
        return True

    def s2_window_open_for(self, actor: Fighter) -> bool:
        if not self._s2_window_live():
            return False
        window = self.s2_schielhau_window
        assert window is not None
        return window.phase == "d1-window" and window.durchwechseln_actor is actor

    def _pay_durchwechseln(self, attacker: Fighter) -> bool:
        if (
            not attacker.alive
            or "Durchwechseln" not in attacker.known_plays
            or attacker.spiritus < DURCHWECHSELN_COST
            or len(self.learned_chain) >= LEARNED_PLAY_CAP
        ):
            return False
        self.spend_spiritus(attacker, DURCHWECHSELN_COST)
        self.add_learned_play("Durchwechseln")
        return True

    @staticmethod
    def _replace_pending_with_durchwechseln(attack: Attack) -> None:
        attack.kind = "durchwechseln-thrust"
        attack.committed = False
        attack.descending = False
        attack.power = False
        attack.accuracy = "normal"
        attack.damage_mode = "normal"
        attack.allows_attacker_continuations = True
        attack.phase = "declared"
        attack.attack_roll = None
        attack.hit = None
        attack.damage = 0
        attack.cancelled = False

    def _clear_s2_response_state(self) -> None:
        self.crossing = Crossing(measure=self.crossing.measure)
        self.basic_cross_declaration = None
        self._close_t1_window()
        self._close_rejoinder()
        self.pending_bind_attack = None
        self.pending_winding = None
        self.pending_pommel = None
        self.consecutive_bind_passes = 0

    def establish_schielhau_s2(
        self,
        defender: Fighter,
        defence_rolls: tuple[int, ...],
        damage_rolls: tuple[int, ...] = (3,),
    ) -> Resolution:
        """Establish the selected successful-Schielhau/fresh-D1 window."""
        attack = self.pending_attack
        normalized = attack.kind.lower().replace("_", "-") if attack else ""
        if (
            attack is None
            or self.s2_schielhau_window is not None
            or not attack.actor.alive
            or not defender.alive
            or defender is not attack.target
            or attack.phase != "rolled"
            or not attack.hit
            or attack.cancelled
            or not attack.descending
            or "cut" not in normalized
            or self.crossing.contact != "none"
            or not self.d1_window(defender, attack)
            or "Durchwechseln" not in attack.actor.known_plays
            or "Schielhau" not in defender.known_plays
            or not defender.action_available
            or defender.spiritus < SCHIELHAU_COST
            or len(self.learned_chain) >= LEARNED_PLAY_CAP
        ):
            return Resolution(False, reason="S2 Schielhau prerequisites fail")

        self.spend_action(defender)
        self.spend_spiritus(defender, SCHIELHAU_COST)
        self.add_learned_play("Schielhau")
        self.event_log.append("S2:Schielhau-declared:2S+chain+action")
        established = self.test(defender.skill, defence_rolls)
        if not established.success:
            self.event_log.append(
                f"S2:Schielhau-failed:roll={established.value}:"
                "no-window:original-strike-unresolved"
            )
            return Resolution(
                True,
                False,
                "Schielhau failed; original Strike remains unresolved",
                events=list(self.event_log),
                roll=established,
            )

        self.s2_schielhau_window = S2SchielhauWindow(
            defender,
            attack.actor,
            attack,
            established,
            tuple(damage_rolls),
        )
        self.event_log.append(f"S2:Schielhau-established:retain-roll={established.value}")
        self.event_log.append("S2:D1-window-open:pre-contact:delayed-consequences")
        return Resolution(
            True,
            True,
            "Schielhau established; S2 D1 window open",
            events=list(self.event_log),
            roll=established,
        )

    def _resolve_s2_schielhau(
        self,
        window: S2SchielhauWindow,
        source: str,
    ) -> Resolution:
        attack = window.attack
        attack.cancelled = True
        attack.phase = "cancelled"
        amount = self.damage(window.schielhau_damage_rolls)
        attack.actor.hp -= amount
        self._clear_s2_response_state()
        self._set_point_threat(window.schielhau_actor, "threatening", "Schielhau-S2")
        self.event_log.append(f"S2:outcome:Schielhau-wins:{source}:normal-damage={amount}")
        established = window.established_roll
        self._clear_s2_window("resolved-Schielhau")
        return Resolution(
            True,
            True,
            "S2 Schielhau wins",
            amount,
            list(self.event_log),
            established,
        )

    def decline_s2_durchwechseln(self, actor: Fighter) -> Resolution:
        if not self.s2_window_open_for(actor):
            return Resolution(False, reason="no live S2 D1 decision for actor")
        window = self.s2_schielhau_window
        assert window is not None
        self.event_log.append("S2:D1-declined")
        return self._resolve_s2_schielhau(window, "D1-declined")

    def declare_durchwechseln(self, attacker: Fighter, defender: Fighter, attack: Attack) -> bool:
        if self.s2_schielhau_window is not None:
            if not self._s2_window_live():
                return False
            window = self.s2_schielhau_window
            assert window is not None
            if (
                window.phase != "d1-window"
                or window.attack is not attack
                or window.durchwechseln_actor is not attacker
                or window.schielhau_actor is not defender
                or not self.d1_window(defender, attack)
                or not self._pay_durchwechseln(attacker)
            ):
                return False
            window.phase = "d1-declared"
            self.event_log.append("S2:D1-declared:1S+chain:no-action:fresh-roll-pending")
            return True
        if not self.d1_window(defender, attack):
            return False
        if not self._pay_durchwechseln(attacker):
            return False
        self.crossing = Crossing(measure=self.crossing.measure)
        self.basic_cross_declaration = None
        self._close_rejoinder()
        self._set_point_threat(attacker, "threatening", "D1")
        self._replace_pending_with_durchwechseln(attack)
        self.event_log.append("D1:replace-pending-attack")
        return True

    def resolve_s2_durchwechseln(
        self,
        actor: Fighter,
        attack_rolls: tuple[int, ...],
        damage_rolls: tuple[int, ...] = (3,),
    ) -> Resolution:
        if not self._s2_window_live():
            return Resolution(False, reason="no live S2 interaction")
        window = self.s2_schielhau_window
        assert window is not None
        if window.phase != "d1-declared" or window.durchwechseln_actor is not actor:
            return Resolution(False, reason="fresh S2 D1 roll is not pending for actor")

        fresh = self.test(actor.skill, attack_rolls)
        self.event_log.append(
            f"S2:D1-fresh-roll:value={fresh.value}:success={str(fresh.success).lower()}"
        )
        winner = self.compare_s2_rolls(window.established_roll, fresh)
        self.event_log.append(
            f"S2:comparison:established={window.established_roll.value}:"
            f"fresh={fresh.value}:winner={winner}"
        )
        if winner == "schielhau":
            return self._resolve_s2_schielhau(window, "S2-comparison")

        attack = window.attack
        if winner == "durchwechseln":
            self._clear_s2_response_state()
            self._replace_pending_with_durchwechseln(attack)
            attack.attack_roll = fresh
            attack.hit = True
            attack.damage = self.damage(damage_rolls)
            attack.phase = "resolved"
            attack.target.hp -= attack.damage
            self._set_point_threat(actor, "threatening", "D1-S2")
            self.event_log.append(
                f"S2:outcome:D1-wins:replace+resolve:normal-damage={attack.damage}"
            )
            self._clear_s2_window("resolved-D1")
            return Resolution(
                True,
                True,
                "S2 Durchwechseln wins",
                attack.damage,
                list(self.event_log),
                fresh,
            )

        # This selected history cell is unreachable through the live gate,
        # which opens only after a successful established Schielhau.
        attack.target.hp -= attack.damage
        attack.phase = "resolved"
        self.event_log.append("S2:outcome:both-fail:original-strike-resolves")
        self._clear_s2_window("resolved-original-strike")
        return Resolution(
            True,
            False,
            "S2 both fail; original Strike resolves",
            attack.damage,
            list(self.event_log),
            fresh,
        )

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
        if self.s2_schielhau_window is not None:
            if self._s2_window_live():
                window = self.s2_schielhau_window
                assert window is not None
                if window.phase == "d1-window":
                    self._resolve_s2_schielhau(window, "window-expired-before-new-attack")
                else:
                    self._clear_s2_window("incomplete-D1-before-new-attack")
        if not target.alive or not self.spend_action(actor):
            return None
        if damage_mode == "normal" and kind in {"cut", "basic-cut"} and actor.loaded and not power:
            damage_mode = "damage_boon"
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
        attack.damage = (
            7
            if attack.damage_mode == "fixed-7"
            else self.damage(damage_rolls, attack.damage_mode)
        )
        return Resolution(True, True, "attack roll succeeded", damage=attack.damage, events=list(self.event_log), roll=result)

    def resolve_pending_attack(self) -> Resolution:
        """Apply one already-rolled, unanswered attack exactly once."""
        if self._s2_window_live():
            return Resolution(False, reason="S2 D1 decision must close before attack resolution")
        attack = self.pending_attack
        if (
            attack is None
            or attack.cancelled
            or attack.phase != "rolled"
            or not attack.hit
            or not attack.target.alive
        ):
            return Resolution(False, reason="no unresolved successful pending attack")
        attack.target.hp -= attack.damage
        attack.phase = "resolved"
        self.event_log.append("pending-attack:resolved")
        return Resolution(
            True,
            True,
            "pending attack resolved",
            attack.damage,
            list(self.event_log),
            attack.attack_roll,
        )

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

    def _set_contested_crossing(
        self,
        creator: Fighter,
        opponent: Fighter,
        attack_roll: RollResult | None,
        defence_roll: RollResult | None,
        *,
        pressure: str,
        source: str,
    ) -> None:
        """Create the preserved local Favored/Unfavored relation.

        This writer is intentionally not used by ordinary Basic Cross.  It is
        retained for Zornhau-local behavior and already-authored special
        crossings pending their own adjudication.
        """
        self.crossing.contact = "crossing"
        self.crossing.contact_zone = {creator.name: "unknown", opponent.name: "unknown"}
        self.crossing.pressure = {creator.name: pressure, opponent.name: pressure}
        self.crossing.initial_pressure = {creator.name: UNKNOWN, opponent.name: UNKNOWN}
        self.crossing.bind_height = UNKNOWN
        self.crossing.bind_initiative = creator.name
        self.crossing.source = source
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

    @staticmethod
    def _qualifies_upper_writer(attack: Attack, defence_geometry: str) -> bool:
        normalized = attack.kind.lower().replace("_", "-")
        return (
            defence_geometry == UPPER_CROSS
            and attack.descending
            and ("cut" in normalized or "oberhau" in normalized)
        )

    @staticmethod
    def _qualifies_lower_writer(attack: Attack, defence_geometry: str) -> bool:
        normalized = attack.kind.lower().replace("_", "-")
        return (
            defence_geometry == LOWER_SETTING_ASIDE
            and normalized in {"low-line-thrust", "rising-low-line-cut"}
        )

    def declare_basic_cross(
        self,
        defender: Fighter,
        pressure_choice: str,
        defence_geometry: str = UNCLASSIFIED,
    ) -> bool:
        """Author hidden H3 pressure and defence geometry before the Cross roll."""
        attack = self.pending_attack
        if (
            pressure_choice not in {HART, WEICH}
            or defence_geometry not in DEFENCE_GEOMETRIES
            or attack is None
            or not attack.actor.alive
            or not defender.alive
            or attack.phase != "rolled"
            or not attack.hit
            or defender is not attack.target
            or not defender.action_available
            or self.basic_cross_declaration is not None
        ):
            return False
        self.basic_cross_declaration = BasicCrossDeclaration(
            defender.name, pressure_choice, defence_geometry
        )
        self.event_log.append(
            f"H3:declare-private-pressure:{defender.name}:hidden:geometry={defence_geometry}"
        )
        return True

    def _set_ordinary_crossing(
        self,
        defender: Fighter,
        striker: Fighter,
        pressure_choice: str,
        bind_height: str,
    ) -> None:
        """Write H3 ordinary state without creating Favored/Unfavored."""
        self.bind_serial += 1
        self.crossing = Crossing(
            contact="crossing",
            measure=self.crossing.measure,
            contact_zone={defender.name: UNKNOWN, striker.name: UNKNOWN},
            pressure={defender.name: UNKNOWN, striker.name: UNKNOWN},
            initial_pressure={defender.name: pressure_choice, striker.name: UNKNOWN},
            bind_height=bind_height,
            bind_position={defender.name: UNKNOWN, striker.name: UNKNOWN},
            bind_initiative=None,
            source="ordinary-basic-cross",
        )
        self.pending_bind_attack = None
        self.pending_winding = None
        self.pending_pommel = None
        self.consecutive_bind_passes = 0

    def _clear_initial_pressure(self) -> None:
        self.crossing.initial_pressure = {name: UNKNOWN for name in self.fighters}

    def _close_rejoinder(self) -> None:
        self.rejoinder_open = False
        self.rejoinder_actor = None

    def _open_rejoinder(self, striker: Fighter) -> None:
        self.rejoinder_actor = striker.name
        self.rejoinder_open = True

    def _close_t1_window(self) -> None:
        self.t1_window_actor = None
        self.t1_original_striker = None

    def _governing_t1_cross_legal(self, defender: Fighter) -> bool:
        attack = self.pending_attack
        normalized = attack.kind.lower().replace("_", "-") if attack else ""
        return bool(
            self.enable_governing_t1
            and defender.alive
            and self.other(defender).alive
            and defender.guard == TUTTA_GUARD
            and T1_PLAY in defender.known_plays
            and attack is not None
            and attack.target is defender
            and attack.cancelled
            and normalized in {"cut", "basic-cut"}
            and not attack.power
            and not attack.committed
            and attack.allows_attacker_continuations
            and self.crossing.source == "ordinary-basic-cross"
            and self.crossing.contact == "crossing"
            and self.crossing.measure == "wide"
            and self.crossing.initial_pressure.get(defender.name, UNKNOWN) in {HART, WEICH}
            and defender.spiritus >= 1
            and len(self.learned_chain) < LEARNED_PLAY_CAP
        )

    def t1_legal(self, actor: Fighter) -> bool:
        return bool(
            self.t1_window_actor == actor.name
            and self.t1_original_striker == self.other(actor).name
            and not self.rejoinder_open
            and self._governing_t1_cross_legal(actor)
        )

    def t1_options(self, actor: Fighter) -> list[str]:
        if self.t1_window_actor != actor.name:
            return []
        return [T1_PLAY, "decline"]

    def decline_t1(self, actor: Fighter) -> bool:
        """Close E1 first, then create the otherwise-ordinary H3 Rejoinder."""
        if self.t1_window_actor != actor.name or not actor.alive or not self.other(actor).alive:
            return False
        striker = self.other(actor)
        self._close_t1_window()
        self._open_rejoinder(striker)
        self.event_log.append("E1:T1-decline:open-ordinary-H3-Rejoinder")
        return True

    def declare_t1(self, actor: Fighter) -> bool:
        """Promoted E1 cover-integrated Wide-to-Close state transformation."""
        if not self.t1_legal(actor):
            return False
        pressure = self.crossing.initial_pressure.get(actor.name, UNKNOWN)
        striker_name = self.t1_original_striker
        if pressure not in {HART, WEICH} or striker_name is None:
            return False
        if not self.spend_spiritus(actor, 1):
            return False
        if not self.add_learned_play(T1_PLAY):
            actor.spiritus += 1
            return False
        self.crossing.retained = True
        self.crossing.measure = "close"
        self.crossing.bind_height = UNKNOWN
        self.crossing.bind_initiative = striker_name if pressure == HART else actor.name
        self.crossing.initiative_passed = False
        self.consecutive_bind_passes = 0
        self._clear_initial_pressure()
        self._close_t1_window()
        self.event_log.append(
            f"E1:T1:1S+chain:no-action:RETAIN crossing:SET close+height=unknown:"
            f"opportunity->{self.crossing.bind_initiative}:CLEAR pressure:no-H3-created"
        )
        return True

    def basic_defence(
        self,
        form: str,
        defender: Fighter,
        attack_roll: RollResult,
        defence_rolls: tuple[int, ...],
    ) -> Resolution:
        attack = self.pending_attack
        if (
            attack is None
            or not attack.actor.alive
            or not defender.alive
            or form not in {"Cross", "Beat"}
            or defender is not attack.target
        ):
            return Resolution(False, reason="invalid Basic defence")
        declaration = self.basic_cross_declaration
        if form == "Cross" and (
            declaration is None or declaration.defender_name != defender.name
        ):
            return Resolution(False, reason="ordinary Cross requires pre-roll Hart/Weich declaration")
        if not self.spend_action(defender):
            return Resolution(False, reason="action unavailable")
        modifier = (
            "boon"
            if form == "Cross" and declaration is not None and declaration.pressure_choice == HART
            else "normal"
        )
        result = self.test(defender.skill, defence_rolls, modifier)
        if form == "Cross":
            self.basic_cross_declaration = None
        if not result.success:
            if form == "Cross":
                measure = self.crossing.measure
                self.crossing = Crossing(measure=measure)
                self._close_t1_window()
                self._close_rejoinder()
                self.pending_bind_attack = None
                self.pending_winding = None
                self.consecutive_bind_passes = 0
                self.event_log.append("H3:failed-Cross:CLEAR contact+pressure+height")
            return Resolution(True, False, f"failed Basic {form}", roll=result)
        attack.cancelled = True
        attack.phase = "cancelled"
        if form == "Cross":
            assert declaration is not None
            if self._qualifies_lower_writer(attack, declaration.defence_geometry):
                bind_height = LOWER
            elif self._qualifies_upper_writer(attack, declaration.defence_geometry):
                bind_height = UPPER
            else:
                bind_height = UNKNOWN
            self._set_ordinary_crossing(
                defender, attack.actor, declaration.pressure_choice, bind_height
            )
            if attack.allows_attacker_continuations:
                if self._governing_t1_cross_legal(defender):
                    self.t1_window_actor = defender.name
                    self.t1_original_striker = attack.actor.name
                    rejoinder = "open E1 T1 decision before creating attacker Bind Rejoinder"
                else:
                    self._open_rejoinder(attack.actor)
                    rejoinder = "open attacker Bind Rejoinder"
            else:
                # Preserve authored attacks (including P1) that prohibit
                # attacker insertions; do not leave phase-scoped pressure live.
                self.crossing.bind_initiative = defender.name
                self._clear_initial_pressure()
                self._close_rejoinder()
                rejoinder = "attacker insertion prohibited; defender opportunity"
            self.event_log.append(
                f"H3:Cross:CANCEL+SET crossing+height={bind_height}+{rejoinder}"
            )
        else:
            self.crossing = Crossing(measure=self.crossing.measure)
            self.basic_cross_declaration = None
            self._close_t1_window()
            self._close_rejoinder()
            self.displacement_events.append({"weapon_owner": attack.actor.name, "source": "Basic Beat", "contact_after": "none"})
            attack.actor.guard = OPEN
            self._set_point_threat(attack.actor, "not_threatening", "Beat-Open")
            self.event_log.append("Beat:CANCEL+displace+CLEAR contact+SET guard=open")
        return Resolution(True, True, f"successful Basic {form}", events=list(self.event_log), roll=result)

    def zornhau(
        self,
        defender: Fighter,
        attack_roll: RollResult,
        defence_rolls: tuple[int, ...],
    ) -> Resolution:
        attack = self.pending_attack
        if (
            attack is None
            or not attack.actor.alive
            or not defender.alive
            or not attack.descending
            or defender is not attack.target
        ):
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
        self._set_point_threat(defender, "threatening", "Zornhau")
        self._set_contested_crossing(
            defender,
            attack.actor,
            attack_roll,
            result,
            pressure=UNKNOWN,
            source="zornhau-local",
        )
        self.event_log.append("Zornhau:CANCEL+SET crossing+SET point=threatening")
        return Resolution(True, True, "Zornhau succeeded", events=list(self.event_log), roll=result)

    def bind_view(self, actor: Fighter) -> str:
        if self.crossing.source == "ordinary-basic-cross":
            return UNKNOWN
        actual = self.crossing.bind_position.get(actor.name, "unknown")
        if actual == "unknown" or "Fühlen" not in actor.known_plays:
            return "unknown"
        return actual

    def pressure_view(self, viewer: Fighter, subject: Fighter) -> str:
        """Return private/revealed H3 initial pressure without public leakage."""
        actual = self.crossing.initial_pressure.get(subject.name, UNKNOWN)
        if viewer is subject:
            return actual
        if self.crossing.source != "ordinary-basic-cross" or not self.rejoinder_open:
            return UNKNOWN
        return self.fuhlen_reveals.get((self.bind_serial, viewer.name), UNKNOWN)

    def public_crossing_state(self, viewer: Fighter | None = None) -> dict[str, object]:
        """Player-visible state; hidden initial pressure is deliberately absent."""
        bind_position = {name: UNKNOWN for name in self.fighters}
        if viewer is not None:
            bind_position[viewer.name] = self.bind_view(viewer)
        return {
            "contact": self.crossing.contact,
            "measure": self.crossing.measure,
            "contact_zone": dict(self.crossing.contact_zone),
            "pressure": dict(self.crossing.pressure),
            "bind_height": self.crossing.bind_height,
            "bind_position": bind_position,
            "bind_initiative": self.crossing.bind_initiative,
        }

    def fighter_private_crossing_state(self, actor: Fighter) -> dict[str, object]:
        state = self.public_crossing_state(actor)
        state["initial_pressure"] = {
            name: self.pressure_view(actor, fighter)
            for name, fighter in self.fighters.items()
        }
        return state

    def buy_fuhlen(self, actor: Fighter) -> str | None:
        """F1: buy one ordinary-Rejoinder initial-pressure reveal for 1S."""
        key = (self.bind_serial, actor.name)
        if (
            not actor.alive
            or not self.other(actor).alive
            or self.t1_window_actor is not None
            or self.crossing.source != "ordinary-basic-cross"
            or not self.rejoinder_open
            or self.rejoinder_actor != actor.name
            or not (FUHLEN_NAMES & actor.known_plays)
            or actor.spiritus < 1
            or key in self.fuhlen_purchases
        ):
            return None
        opponent = self.other(actor)
        revealed = self.crossing.initial_pressure.get(opponent.name, UNKNOWN)
        if revealed not in {HART, WEICH}:
            revealed = UNKNOWN
        self.spend_spiritus(actor, 1)
        self.fuhlen_purchases.add(key)
        self.fuhlen_reveals[key] = revealed
        self.event_log.append(f"H3:F1:{actor.name}:reveal={revealed}:1S")
        return revealed

    def rejoinder_options(self, actor: Fighter) -> list[str]:
        if (
            not actor.alive
            or not self.other(actor).alive
            or self.t1_window_actor is not None
            or self.crossing.source != "ordinary-basic-cross"
            or not self.rejoinder_open
            or self.rejoinder_actor != actor.name
            or self.crossing.contact != "crossing"
        ):
            return []
        options: list[str] = []
        if (
            FUHLEN_NAMES & actor.known_plays
            and actor.spiritus >= 1
            and (self.bind_serial, actor.name) not in self.fuhlen_purchases
        ):
            options.append("Fühlen")
        if (
            self.crossing.measure == "wide"
            and PAIRED_PLAY in actor.known_plays
            and actor.spiritus >= 2
            and len(self.learned_chain) < LEARNED_PLAY_CAP
        ):
            options.extend(("Duplieren", "Mutieren"))
        options.append("decline")
        return options

    def declare_bind_rejoinder(self, actor: Fighter, branch: str) -> Resolution:
        if branch not in {"Duplieren", "Mutieren"} or branch not in self.rejoinder_options(actor):
            return Resolution(False, reason="Bind Rejoinder prerequisites fail")
        self.spend_spiritus(actor, 2)
        self.add_learned_play(f"{PAIRED_PLAY}:{branch}")
        defender = self.other(actor)
        pressure = self.crossing.initial_pressure.get(defender.name, UNKNOWN)
        correct = (branch == "Duplieren" and pressure == HART) or (
            branch == "Mutieren" and pressure == WEICH
        )
        self._close_rejoinder()
        self._clear_initial_pressure()
        self.consecutive_bind_passes = 0
        if not correct:
            self.event_log.append(f"H3:{branch}:wrong-read:2S+chain:no-roll+zero-damage")
            self._end_bind_sequence()
            return Resolution(
                True, False, f"{branch} wrong-pressure hard failure", 0, list(self.event_log)
            )
        kind = "cut" if branch == "Duplieren" else "thrust"
        height = "high" if branch == "Duplieren" else "low"
        self.pending_bind_attack = BindAttack(actor, defender, branch, kind, height)
        if branch == "Mutieren":
            self.crossing.retained = True
            self._set_point_threat(actor, "threatening", "Mutieren")
            self.event_log.append("H3:Mutieren:RETAIN transition+SET point=threatening")
        self.event_log.append(f"H3:{branch}:booned-{kind}:2S+chain:no-additional-action")
        return Resolution(True, True, f"{branch} declared", events=list(self.event_log))

    def resolve_bind_rejoinder(
        self,
        attack_rolls: tuple[int, ...],
        damage_rolls: tuple[int, ...] = (3,),
    ) -> Resolution:
        bind_attack = self.pending_bind_attack
        if (
            bind_attack is None
            or bind_attack.phase != "declared"
            or not bind_attack.actor.alive
            or not bind_attack.target.alive
        ):
            if bind_attack is not None:
                self._end_bind_sequence()
            return Resolution(False, reason="no pending Bind Rejoinder attack")
        result = self.test(bind_attack.actor.skill, attack_rolls, "boon")
        amount = self.damage(damage_rolls) if result.success else 0
        if result.success:
            bind_attack.target.hp -= amount
        bind_attack.phase = "resolved"
        self.pending_bind_attack = None
        self.event_log.append(f"H3:{bind_attack.branch}:resolve:boon+normal-damage")
        self._end_bind_sequence()
        return Resolution(
            True,
            result.success,
            f"{bind_attack.branch} resolved",
            amount,
            list(self.event_log),
            result,
        )

    def decline_bind_rejoinder(self, actor: Fighter) -> bool:
        if (
            not actor.alive
            or not self.other(actor).alive
            or self.t1_window_actor is not None
            or self.crossing.source != "ordinary-basic-cross"
            or not self.rejoinder_open
            or self.rejoinder_actor != actor.name
        ):
            return False
        defender = self.other(actor)
        pressure = self.crossing.initial_pressure.get(defender.name, UNKNOWN)
        if pressure not in {HART, WEICH}:
            return False
        self.crossing.bind_initiative = actor.name if pressure == HART else defender.name
        self._clear_initial_pressure()
        self._close_rejoinder()
        self.consecutive_bind_passes = 0
        self.event_log.append(
            f"H3:Rejoinder-decline:initiative->{self.crossing.bind_initiative}+CLEAR pressure"
        )
        return True

    def continuation_options(self, actor: Fighter, *, winden_variant: str) -> list[str]:
        if (
            not actor.alive
            or not self.other(actor).alive
            or self.crossing.contact != "crossing"
            or self.crossing.bind_initiative != actor.name
        ):
            return []
        if self.crossing.source == "ordinary-basic-cross":
            options: list[str] = []
            if self.pommel_legal(actor):
                options.append(POMMEL_PLAY)
            if self.upper_winding_legal(actor):
                options.append("Upper Winding Thrust")
            if self.lower_winding_legal(actor):
                options.append("Lower Winding Thrust")
            options.extend(("pass", "Disengage"))
            return options
        actual = self.crossing.bind_position.get(actor.name, "unknown")
        view = self.bind_view(actor)
        options: list[str] = []
        if self.pommel_legal(actor):
            options.append(POMMEL_PLAY)
        if "Zornhau-Ort" in actor.known_plays and actor.spiritus >= 1:
            if view in {"unknown", "favored"}:
                options.append("Ort")
        if "Winden" in actor.known_plays and actor.spiritus >= 1 and len(self.learned_chain) < LEARNED_PLAY_CAP:
            if winden_variant == "W2" or view in {"unknown", "unfavored"}:
                options.append("Winden")
        return options

    def ort(self, actor: Fighter, damage_model: str, damage_rolls: tuple[int, ...]) -> Resolution:
        if (
            not actor.alive
            or not self.other(actor).alive
            or self.crossing.source == "ordinary-basic-cross"
            or self.crossing.contact != "crossing"
            or self.crossing.bind_initiative != actor.name
        ):
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
        if (
            not actor.alive
            or not self.other(actor).alive
            or self.crossing.source == "ordinary-basic-cross"
            or self.crossing.contact != "crossing"
            or self.crossing.bind_initiative != actor.name
        ):
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
        self._set_point_threat(actor, "threatening", "Zornhau-local-Winden")
        result = self.test(actor.skill, attack_rolls)
        amount = self.damage(damage_rolls) if result.success else 0
        if result.success:
            self.other(actor).hp -= amount
        self.event_log.append(f"Winden:{variant}:RETAIN crossing+normal thrust")
        return Resolution(True, result.success, "Winden thrust", amount, list(self.event_log), result)

    def _ordinary_winding_legal(self, actor: Fighter, bind_height: str) -> bool:
        return (
            actor.alive
            and self.other(actor).alive
            and self.crossing.source == "ordinary-basic-cross"
            and WINDEN_PLAY in actor.known_plays
            and self.crossing.contact == "crossing"
            and self.crossing.bind_height == bind_height
            and self.crossing.bind_initiative == actor.name
            and actor.spiritus >= 2
            and len(self.learned_chain) < LEARNED_PLAY_CAP
            and not self.rejoinder_open
            and self.t1_window_actor is None
            and self.pending_bind_attack is None
            and self.pending_winding is None
            and self.pending_pommel is None
        )

    def upper_winding_legal(self, actor: Fighter) -> bool:
        return self._ordinary_winding_legal(actor, UPPER)

    def lower_winding_legal(self, actor: Fighter) -> bool:
        return self._ordinary_winding_legal(actor, LOWER)

    def _declare_winding(self, actor: Fighter, bind_height: str) -> Resolution:
        legal = self.upper_winding_legal(actor) if bind_height == UPPER else self.lower_winding_legal(actor)
        if not legal:
            label = "Upper" if bind_height == UPPER else "Lower"
            return Resolution(False, reason=f"{label} Winding Thrust prerequisites fail")
        self.spend_spiritus(actor, 2)
        label = "Upper Winding Thrust" if bind_height == UPPER else "Lower Winding Thrust"
        self.add_learned_play(f"Winden:{label}")
        self.crossing.retained = True
        self.crossing.pressure = {name: UNKNOWN for name in self.fighters}
        self._clear_initial_pressure()
        actor.guard = "ochs" if bind_height == UPPER else "pflug"
        self._set_point_threat(actor, "threatening", label)
        self.crossing.hanging_aftermath = (
            "ochs-upper-hanging" if bind_height == UPPER else "pflug-lower-hanging"
        )
        self.pending_winding = WindingAttack(actor, self.other(actor), bind_height)
        self.consecutive_bind_passes = 0
        self.crossing.initiative_passed = False
        self.event_log.append(
            f"H3:{label}:declare:2S+chain:no-action:RETAIN+SET guard+point+ATTACK flat thrust"
        )
        return Resolution(True, True, f"{label} declared", events=list(self.event_log))

    def declare_upper_winding(self, actor: Fighter) -> Resolution:
        return self._declare_winding(actor, UPPER)

    def declare_lower_winding(self, actor: Fighter) -> Resolution:
        return self._declare_winding(actor, LOWER)

    def _resolve_winding(
        self,
        expected_height: str,
        attack_rolls: tuple[int, ...],
        damage_rolls: tuple[int, ...] = (3,),
    ) -> Resolution:
        winding = self.pending_winding
        if (
            winding is None
            or winding.phase != "declared"
            or winding.bind_height != expected_height
            or not winding.actor.alive
            or not winding.target.alive
        ):
            if winding is not None:
                self._end_bind_sequence()
            label = "Upper" if expected_height == UPPER else "Lower"
            return Resolution(False, reason=f"no pending {label} Winding Thrust")
        result = self.test(winding.actor.skill, attack_rolls, "normal")
        winding.phase = "resolved"
        self.pending_winding = None
        label = "Upper Winding Thrust" if expected_height == UPPER else "Lower Winding Thrust"
        if result.success:
            amount = self.damage(damage_rolls)
            winding.target.hp -= amount
            self.event_log.append(f"H3:{label}:hit:normal-damage+CLEAR contact")
            self._end_bind_sequence()
            return Resolution(True, True, f"{label} hit", amount, list(self.event_log), result)

        self.crossing.contact = "crossing"
        self.crossing.retained = True
        self.crossing.bind_initiative = winding.target.name
        self.crossing.initiative_passed = False
        self.consecutive_bind_passes = 0
        self._set_point_threat(winding.actor, "threatening", f"{label}-miss")
        if expected_height == LOWER:
            self.crossing.bind_height = UPPER
            self.crossing.hanging_aftermath = "ochs-upper-hanging"
            winding.actor.guard = "ochs"
            transition = "SET lower->upper+SET Pflug->Ochs"
        else:
            self.crossing.bind_height = UPPER
            self.crossing.hanging_aftermath = "ochs-upper-hanging"
            winding.actor.guard = "ochs"
            transition = "RETAIN upper+Ochs"
        self.event_log.append(
            f"H3:{label}:miss:{transition}+RETAIN point+initiative->{winding.target.name}"
        )
        return Resolution(True, False, f"{label} missed", 0, list(self.event_log), result)

    def resolve_upper_winding(
        self,
        attack_rolls: tuple[int, ...],
        damage_rolls: tuple[int, ...] = (3,),
    ) -> Resolution:
        return self._resolve_winding(UPPER, attack_rolls, damage_rolls)

    def resolve_lower_winding(
        self,
        attack_rolls: tuple[int, ...],
        damage_rolls: tuple[int, ...] = (3,),
    ) -> Resolution:
        return self._resolve_winding(LOWER, attack_rolls, damage_rolls)

    def pass_bind_initiative(self, actor: Fighter) -> bool:
        if (
            not actor.alive
            or not self.other(actor).alive
            or self.crossing.contact != "crossing"
            or self.crossing.bind_initiative != actor.name
            or self.rejoinder_open
            or self.t1_window_actor is not None
            or self.pending_bind_attack is not None
            or self.pending_winding is not None
            or self.pending_pommel is not None
        ):
            return False
        self.consecutive_bind_passes += 1
        if self.consecutive_bind_passes == 1:
            self.crossing.bind_initiative = self.other(actor).name
            self.crossing.initiative_passed = True
            self.event_log.append("bind-initiative:pass:first-opportunity-transfers")
            return True
        self.event_log.append("bind-initiative:two-consecutive-passes:CLEAR crossing")
        self._end_bind_sequence()
        return True

    def decline_bind_continuations(self, actor: Fighter) -> bool:
        """Compatibility name for the sequencing-only pass operation."""
        return self.pass_bind_initiative(actor)

    def disengage(self, actor: Fighter) -> bool:
        if (
            not actor.alive
            or not self.other(actor).alive
            or self.crossing.contact != "crossing"
            or self.crossing.bind_initiative != actor.name
            or self.rejoinder_open
            or self.t1_window_actor is not None
            or self.pending_bind_attack is not None
            or self.pending_winding is not None
            or self.pending_pommel is not None
        ):
            return False
        self.event_log.append(f"Disengage:{actor.name}:CLEAR crossing")
        self._end_bind_sequence()
        return True

    def tutta_cover_to_stretto(self, actor: Fighter) -> bool:
        """Compatibility spelling for the governing E1-only declaration."""
        return self.declare_t1(actor)

    def pommel_legal(self, actor: Fighter) -> bool:
        return bool(
            actor.alive
            and self.other(actor).alive
            and POMMEL_PLAY in actor.known_plays
            and self.crossing.contact == "crossing"
            and self.crossing.measure == "close"
            and self.crossing.bind_initiative == actor.name
            and actor.spiritus >= POMMEL_COST
            and len(self.learned_chain) < LEARNED_PLAY_CAP
            and not self.rejoinder_open
            and self.t1_window_actor is None
            and self.pending_bind_attack is None
            and self.pending_winding is None
            and self.pending_pommel is None
        )

    def declare_pommel(self, actor: Fighter) -> Resolution:
        if not self.pommel_legal(actor):
            return Resolution(False, reason="Pommel prerequisites fail")
        self.spend_spiritus(actor, POMMEL_COST)
        self.add_learned_play(POMMEL_PLAY)
        self.crossing.retained = True
        self.crossing.bind_height = UNKNOWN
        self.crossing.initiative_passed = False
        self.consecutive_bind_passes = 0
        self.pending_pommel = PommelAttack(actor, self.other(actor))
        self.event_log.append(
            "Pommel:declare:2S+chain:no-action:ATTACK flat-normal:ordinary-response-tree-unchanged"
        )
        return Resolution(True, True, "Pommel declared", events=list(self.event_log))

    def pommel_response_options(self, target: Fighter) -> list[str]:
        """Expose the unchanged ordinary menu when an action is actually ready.

        The governing E1 route normally reaches Close after both ordinary
        actions are spent, so this list is usually empty from action economy,
        never from a Pommel-authored restriction.
        """
        pending = self.pending_pommel
        if (
            pending is None
            or pending.target is not target
            or not pending.actor.alive
            or not target.alive
            or not target.action_available
        ):
            return []
        return ["Cross", "Beat", "Counter", "Ignore"]

    def resolve_pommel(
        self,
        attack_rolls: tuple[int, ...],
        damage_rolls: tuple[int, ...] = (3,),
    ) -> Resolution:
        pending = self.pending_pommel
        if (
            pending is None
            or pending.phase != "declared"
            or not pending.actor.alive
            or not pending.target.alive
        ):
            if pending is not None:
                self._end_bind_sequence()
            return Resolution(False, reason="no live pending Pommel")
        result = self.test(pending.actor.skill, attack_rolls, "normal")
        pending.phase = "resolved"
        self.pending_pommel = None
        if result.success:
            amount = self.damage(damage_rolls, "normal")
            pending.target.hp -= amount
            self.event_log.append("Pommel:hit:normal-damage:CLEAR bounded-bind")
            self._end_bind_sequence()
            return Resolution(True, True, "Pommel hit", amount, list(self.event_log), result)
        self.crossing.contact = "crossing"
        self.crossing.measure = "close"
        self.crossing.bind_height = UNKNOWN
        self.crossing.retained = True
        self.crossing.bind_initiative = pending.target.name
        self.crossing.initiative_passed = False
        self.consecutive_bind_passes = 0
        self.event_log.append(
            f"Pommel:miss:zero-damage:RETAIN close:opportunity->{pending.target.name}"
        )
        return Resolution(True, False, "Pommel missed", 0, list(self.event_log), result)

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
        if (
            attack is None
            or not attack.actor.alive
            or not defender.alive
            or defender is not attack.target
            or defender.spiritus < 2
            or not defender.action_available
        ):
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
        self._set_point_threat(defender, "threatening", name)
        amount = self.damage(damage_rolls)
        attack.actor.hp -= amount
        if name in {"Absetzen", "Scambiar di Punta"}:
            self._set_contested_crossing(
                defender,
                attack.actor,
                attack.attack_roll,
                result,
                pressure=UNKNOWN,
                source="authored-special",
            )
        else:
            self.crossing = Crossing(measure=self.crossing.measure)
        return Resolution(True, True, f"{name} C2 succeeded", amount, roll=result)

    def attempt_attacker_continuation(self, actor: Fighter, name: str) -> bool:
        if not actor.alive or not self.other(actor).alive or self.rejoinder_open:
            return False
        attack = self.pending_attack
        if attack is not None and attack.actor is actor and not attack.allows_attacker_continuations:
            return False
        return self.add_learned_play(name)

    def cleanup_crossing(self) -> None:
        if self.crossing.contact == "crossing" and self.crossing.retained:
            self.crossing.retained = False
            return
        self._end_bind_sequence()

    def finish_exchange(self) -> None:
        """Apply the governing exchange boundary without refreshing a round action."""
        if self.s2_schielhau_window is not None:
            if self._s2_window_live():
                window = self.s2_schielhau_window
                assert window is not None
                if window.phase == "d1-window":
                    self._resolve_s2_schielhau(window, "window-expired-at-exchange-end")
                else:
                    self._clear_s2_window("incomplete-D1-at-exchange-end")
        self.cleanup_crossing()
        if self.crossing.contact == "crossing":
            self._clear_initial_pressure()
            self._close_rejoinder()
            self.crossing.bind_initiative = None
            self.crossing.initiative_passed = False
            self.consecutive_bind_passes = 0
        self.learned_chain.clear()
        self.pending_attack = None
        self.basic_cross_declaration = None
        self.pending_bind_attack = None
        self.pending_winding = None
        self.pending_pommel = None
        self.s2_schielhau_window = None
        self._close_t1_window()
        self.expire_recovery_window()

    def _end_bind_sequence(self) -> None:
        measure = self.crossing.measure
        self.crossing = Crossing(measure=measure)
        self.basic_cross_declaration = None
        self._close_t1_window()
        self._close_rejoinder()
        self.pending_bind_attack = None
        self.pending_winding = None
        self.pending_pommel = None
        self.consecutive_bind_passes = 0


def validate_authoritative_baseline() -> None:
    assert LEARNED_PLAY_CAP == 3
    assert MAX_HP == 8 and MAX_SPIRITUS == 8
    assert ProvisionalLongswordEngine.damage((1, 6), "damage_boon") == 7
    assert ProvisionalLongswordEngine.damage((1, 6), "damage_bane") == 2


validate_authoritative_baseline()

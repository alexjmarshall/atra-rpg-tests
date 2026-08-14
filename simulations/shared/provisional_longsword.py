"""Shared entry point for the governing provisional longsword prototype.

The current exchange engine is authoritative.  Archived duel modules are loaded
only through the explicitly named compatibility exports at the bottom so that
old experiment reports remain reproducible without governing new behavior.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ENGINE_PATH = ROOT / "simulations" / "shared" / "provisional_longsword_engine.py"
LEGACY_ENGINE_PATH = ROOT / "simulations" / "loaded_power_attack_v0_1" / "simulate.py"
CONFIG_PATH = ROOT / "data" / "prototypes" / "longsword-governing-provisional-v0.1.yaml"

SPEC = importlib.util.spec_from_file_location("atra_governing_provisional_engine", ENGINE_PATH)
ENGINE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = ENGINE
SPEC.loader.exec_module(ENGINE)

LEGACY_SPEC = importlib.util.spec_from_file_location("atra_archived_loaded_power_engine", LEGACY_ENGINE_PATH)
LEGACY_ENGINE = importlib.util.module_from_spec(LEGACY_SPEC)
assert LEGACY_SPEC.loader is not None
sys.modules[LEGACY_SPEC.name] = LEGACY_ENGINE
LEGACY_SPEC.loader.exec_module(LEGACY_ENGINE)

# Archived subclasses historically reached compatibility types through
# ``SHARED.ENGINE``.  Preserve that import surface without making those types
# authoritative for new behavior.
ENGINE.BASE = LEGACY_ENGINE.BASE
ENGINE.Cell = LEGACY_ENGINE.Cell
ENGINE.LoadedPowerDuel = LEGACY_ENGINE.LoadedPowerDuel
ENGINE.MODELS = LEGACY_ENGINE.MODELS
for _compat_name in (
    "POLICY_TEMPERATURE",
    "expected",
    "normal_damage_distribution",
    "loaded_damage_distribution",
    "probability_at_least",
    "attack_success_probability",
    "throughchange_probability",
    "softmax_probabilities",
):
    setattr(ENGINE, _compat_name, getattr(LEGACY_ENGINE, _compat_name))

CONTACT_VALUES = ("none", "crossing")
MEASURE_VALUES = ("wide", "close")
CONTACT_ZONE_VALUES = ("hiltward", "middle", "pointward", "unknown")
PRESSURE_VALUES = ("hard", "soft", "unknown")
INITIAL_PRESSURE_VALUES = ("hart", "weich", "unknown")
BIND_HEIGHT_VALUES = ("upper", "lower", "unknown")
POINT_THREAT_VALUES = ("threatening", "not_threatening")
NAMED_GUARD_IDS = (
    "vom-tag",
    "ochs",
    "pflug",
    "alber",
    "posta-di-donna",
    "posta-frontale",
    "tutta-porta-di-ferro",
    "mezza-porta-di-ferro",
)
LEARNED_PLAY_CAP = 3

GOVERNING_BASELINE: dict[str, Any] = {
    "status": "GOVERNING PROVISIONAL PROTOTYPE BASELINE",
    "durchwechseln": {
        "variant": "D1",
        "spiritus_cost": 1,
        "spend_timing": "declaration",
        "refund_on_failure": False,
        "declaration_window": "pre-Basic-Parry-roll",
        "trigger": "state-based",
    },
    "compounds": {
        "variant": "C2",
        "spiritus_cost": 2,
        "plays": ("Absetzen", "Scambiar di Punta", "Schielhau"),
    },
    "schielhau_durchwechseln": "S2",
    "contact_model": {
        "contact": CONTACT_VALUES,
        "measure": MEASURE_VALUES,
        "contact_zone": CONTACT_ZONE_VALUES,
        "pressure": PRESSURE_VALUES,
        "initial_pressure": INITIAL_PRESSURE_VALUES,
        "bind_height": BIND_HEIGHT_VALUES,
        "point_threat": POINT_THREAT_VALUES,
        "displacement_is_event": True,
    },
    "basic_parry_forms": ("Cross", "Beat"),
    "choice_architecture": {
        "variant": "STATE-BASED D1 + BEAT-OPEN",
        "cross_durchwechseln_immune": False,
        "d1_denial": "threatening opposing point only; Crossing/form does not deny",
        "cross_success": (
            "declare hidden Hart/Weich before roll; Hart has exactly one defence Boon; "
            "Weich is flat; success cancels, establishes ordinary Crossing, authors public "
            "Upper/Lower/Unknown height, and opens the narrow attacker Bind Rejoinder"
        ),
        "beat_durchwechseln_window": True,
        "beat_success": "cancel; displacement event; end contact; set attacker guard to Open",
        "failed_or_interrupted_beat_creates_open": False,
        "open_numeric_modifiers": (),
    },
    "guard_commitment": {
        "variant": "GC1",
        "named_guards": NAMED_GUARD_IDS,
        "voluntary_change": "once on activation, before action",
        "post_action_change": False,
        "restrictive_voluntary_transition_graph": "REJECTED",
        "authored_action_produced_transitions": True,
    },
    "engine_implementation_status": (
        "SYNCHRONIZED: authoritative shared exchange engine implements state-based D1, "
        "Beat/Open, GC1, general Committed timing, governing E1 T1/Pommel v0.1, "
        "cap 3, C2/S2, Frontale Fendente, and explicit contact"
    ),
    "learned_play_cap": LEARNED_PLAY_CAP,
    "loaded": "proactive Basic Cut receives Damage Boon",
    "power_attack": {
        "variant": "P1",
        "spiritus_cost": 1,
        "damage": 7,
        "committed": True,
        "counter_first": "inherited general Committed declaration-window Counter",
        "attacker_continuations": False,
        "learned_play": False,
    },
    "committed_timing": {
        "immediate_basic_counter": "target may spend action and resolve normal Counter first",
        "waiting_counter": "after a successful attack roll, ordinary Counter is simultaneous",
        "miss": "no ordinary Counter; target-only immediate Nachreisen Recovery may exist",
    },
    "nachreisen": {
        "cost": 1,
        "windows": ("Preparation", "Recovery"),
        "accuracy": "Attack Boon",
        "persistent_recovery_state": False,
        "vom_tag_gate": False,
    },
    "ordinary_h3_bind": {
        "status": "GOVERNING PROVISIONAL",
        "initial_pressure": INITIAL_PRESSURE_VALUES,
        "pressure_visibility": "owner-private; opponent unknown until 1S Fühlen F1",
        "height": BIND_HEIGHT_VALUES,
        "rejoinder": ("Fühlen", "Duplieren", "Mutieren", "decline"),
        "duplieren_mutieren_cost": 2,
        "winden_cost": 2,
        "lower_failure": "L2 lower->upper and Pflug->Ochs",
        "bind_initiative": "first declaration opportunity only; pass transfers once",
        "ordinary_favored_unfavored": "SUPERSEDED; never generated",
    },
    "zornhau_local_bind": {
        "position": ("favored", "unfavored", "unknown"),
        "initiative_separate": True,
        "tie_rule": "Bind Initiative holder Favored; provisional harness only",
        "scope": "preserved Zornhau-local relation pending separate adjudication",
    },
    "zornhau_ort": {
        "zornhau_cost": 0,
        "zornhau_chain_entries": 1,
        "zornhau_point": "threatening",
        "ort_cost": 1,
        "ort_intrinsic": True,
        "ort_models": ("O1", "O2"),
    },
    "fuhlen": {
        "ordinary_h3": "1S/no action/no chain; once per Rejoinder; reveal initial Hart/Weich",
        "zornhau_local": "preserved passive categorical Favored/Unfavored visibility",
        "compatibility_debt": "context-specific semantics pending Zornhau adjudication",
    },
    "winden": {
        "ordinary_cost": 2,
        "chain_entries": 1,
        "ordinary_executions": ("Upper Winding Thrust", "Lower Winding Thrust"),
        "lower_miss": "L2 lower->upper; Pflug->Ochs; transfer opportunity",
        "zornhau_local_variants": ("W1", "W2"),
        "zornhau_local_cost": 1,
        "starting_ochs_pflug_gate": False,
    },
    "tutta_cover_to_stretto": {
        "variant": "T1",
        "status": "GOVERNING PROVISIONAL; NOT CANONICAL",
        "spiritus_cost": 1,
        "spend_timing": "declaration",
        "extra_roll": False,
        "additional_action": False,
        "window": "after successful qualifying Cross and D1 timing; before H3 Rejoinder creation",
        "effect": "retain Crossing; Wide to Close; clear bind height; Hart striker/Weich defender first Close opportunity; clear pressure",
        "learned_play": True,
        "archived_comparison": "T0; C0 and L1 are noncurrent historical controls",
    },
    "frontale_retreating_fendente": {
        "status": "GOVERNING PROVISIONAL; NOT CANONICAL",
        "guard": "posta-frontale",
        "trigger": "live successful incoming Thrust before contact",
        "spiritus_cost": 2,
        "learned_chain_entries": 1,
        "additional_action": False,
        "defensive_action": True,
        "test": "one flat normal Longsword test",
        "success": "cancel incoming Thrust and deal one normal d6+1 Cut damage instance using the same successful test",
        "failure": "do not cancel; zero counter-cut damage; original Thrust remains unresolved",
        "aftermath": "no Crossing, Open, point threat, forced movement, Dente state, guard transition, or automatic follow-up",
    },
    "pommel_strike": {
        "status": "GOVERNING PROVISIONAL; NOT CANONICAL",
        "trigger": "generic Close Crossing plus current bind opportunity",
        "spiritus_cost": 2,
        "learned_chain_entries": 1,
        "additional_action": False,
        "attack": "flat normal Longsword; normal provisional d6+1 damage",
        "hit": "normal bounded bind cleanup",
        "miss": "retain Close Crossing, clear height to Unknown, transfer opportunity",
        "intrinsic_response_restriction": False,
    },
}


def validate_engine_alignment() -> None:
    """Fail loudly if the selected current engine stops matching the baseline."""
    assert ENGINE.MAX_HP == 8 and ENGINE.MAX_SPIRITUS == 8
    assert ENGINE.LEARNED_PLAY_CAP == 3
    assert ENGINE.NAMED_GUARDS == NAMED_GUARD_IDS
    assert ENGINE.THREATENING_GUARDS == frozenset(
        {"ochs", "pflug", "mezza-porta-di-ferro"}
    )
    assert ENGINE.BIND_HEIGHTS == BIND_HEIGHT_VALUES
    assert ENGINE.INITIAL_PRESSURES == INITIAL_PRESSURE_VALUES
    a = ENGINE.Fighter("A", known_plays={"Durchwechseln"})
    b = ENGINE.Fighter("B")
    current = ENGINE.ProvisionalLongswordEngine([a, b])
    ordinary = ENGINE.Attack(a, b, "cut")
    assert current.d1_window(b, ordinary)
    current.crossing.contact = "crossing"
    assert current.d1_window(b, ordinary)
    b.point_threat = "threatening"
    assert not current.d1_window(b, ordinary)
    assert hasattr(current, "establish_schielhau_s2")
    assert hasattr(current, "resolve_s2_durchwechseln")
    established = ENGINE.RollResult(True, 5, (5,))
    fresh_tie = ENGINE.RollResult(True, 5, (5,))
    fresh_lower = ENGINE.RollResult(True, 4, (4,))
    assert current.compare_s2_rolls(established, fresh_tie) == "schielhau"
    assert current.compare_s2_rolls(established, fresh_lower) == "durchwechseln"
    assert ENGINE.FRONTALE_FENDENTE_PLAY == "Frontale Retreating Fendente"
    assert ENGINE.FRONTALE_GUARD == "posta-frontale"
    assert ENGINE.FRONTALE_FENDENTE_COST == 2
    assert hasattr(current, "frontale_retreating_fendente")


validate_engine_alignment()

Fighter = ENGINE.Fighter
Attack = ENGINE.Attack
Crossing = ENGINE.Crossing
Resolution = ENGINE.Resolution
S2SchielhauWindow = ENGINE.S2SchielhauWindow
CurrentEngine = ENGINE.ProvisionalLongswordEngine
HART = ENGINE.HART
WEICH = ENGINE.WEICH
UNKNOWN = ENGINE.UNKNOWN
UPPER = ENGINE.UPPER
LOWER = ENGINE.LOWER

# Compatibility only: old named-guard/bridge experiments subclass these archived
# types.  New work must use CurrentEngine.
BaseCell = LEGACY_ENGINE.Cell
BaseDuel = LEGACY_ENGINE.LoadedPowerDuel
fresh_metrics = LEGACY_ENGINE.fresh_metrics
finalize = LEGACY_ENGINE.finalize
record_fight = LEGACY_ENGINE.BASE.record_fight

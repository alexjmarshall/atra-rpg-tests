"""Shared entry point for the governing provisional longsword prototype.

The archived experiment modules remain unchanged.  New simulations should import
this module rather than selecting an experimental branch by inference.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ENGINE_PATH = ROOT / "simulations" / "loaded_power_attack_v0_1" / "simulate.py"
CONFIG_PATH = ROOT / "data" / "prototypes" / "longsword-governing-provisional-v0.1.yaml"

SPEC = importlib.util.spec_from_file_location("atra_governing_loaded_power_engine", ENGINE_PATH)
ENGINE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = ENGINE
SPEC.loader.exec_module(ENGINE)

CONTACT_VALUES = ("none", "crossing")
MEASURE_VALUES = ("wide", "close")
CONTACT_ZONE_VALUES = ("hiltward", "middle", "pointward", "unknown")
PRESSURE_VALUES = ("hard", "soft", "unknown")
POINT_THREAT_VALUES = ("threatening", "not_threatening")
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
        "point_threat": POINT_THREAT_VALUES,
        "displacement_is_event": True,
    },
    "basic_parry_forms": ("Cross", "Beat"),
    "choice_architecture": {
        "variant": "CB3",
        "cross_durchwechseln_immune": True,
        "cross_success": "cancel; establish ordinary Crossing; no generic modifier",
        "beat_durchwechseln_window": True,
        "beat_success": "cancel; displacement event; end contact; set attacker guard to Open",
        "failed_or_interrupted_beat_creates_open": False,
        "open_numeric_modifiers": (),
    },
    "guard_commitment": {
        "variant": "GC1",
        "voluntary_change": "once on activation, before action",
        "post_action_change": False,
        "restrictive_voluntary_transition_graph": "REJECTED",
        "authored_action_produced_transitions": True,
    },
    "engine_implementation_status": (
        "METADATA UPDATED ONLY: the selected archived engine still implements the "
        "pre-CB3/pre-GC1 harness; governing simulator behavior was not changed by the "
        "Mechanical Effect Vocabulary v0.1 milestone"
    ),
    "learned_play_cap": LEARNED_PLAY_CAP,
    "loaded": "proactive Basic Cut receives Damage Boon",
    "power_attack": {
        "variant": "P1",
        "spiritus_cost": 1,
        "damage": 7,
        "committed": True,
        "counter_first": True,
        "learned_play": False,
    },
    "tutta_cover_to_stretto": {
        "variant": "T1",
        "status": "GOVERNING PROVISIONAL; NOT CANONICAL",
        "spiritus_cost": 1,
        "spend_timing": "declaration",
        "extra_roll": False,
        "additional_action": False,
        "effect": "retain Crossing; Wide to Close",
        "learned_play": True,
        "archived_comparison": "T0",
    },
}


def validate_engine_alignment() -> None:
    """Fail loudly if the selected archived engine stops matching the baseline."""
    assert ENGINE.BASE.DURCH_COST == 1
    assert ENGINE.BASE.COMPOUND_COST == 2
    assert ENGINE.MODELS["P1"] == {
        "loaded": True,
        "power": True,
        "cost": 1,
        "attack_bane": False,
        "counter_first": True,
    }
    assert ENGINE.MAX_HP == 8
    assert ENGINE.MAX_SPIRITUS == 8
    assert ENGINE.BASE.ContactState.__dataclass_fields__["contact"].default == "none"
    assert ENGINE.BASE.ContactState.__dataclass_fields__["measure"].default == "wide"


validate_engine_alignment()

BaseCell = ENGINE.Cell
BaseDuel = ENGINE.LoadedPowerDuel
fresh_metrics = ENGINE.fresh_metrics
finalize = ENGINE.finalize
record_fight = ENGINE.BASE.record_fight

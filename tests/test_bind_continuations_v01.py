from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_PATH = ROOT / "simulations" / "crossing_bind_state_model_v0_1" / "simulate.py"
SPEC = importlib.util.spec_from_file_location("bind_continuations_state_engine", SIM_PATH)
SIM = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = SIM
SPEC.loader.exec_module(SIM)


class BindContinuationTransitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = SIM.bind_continuation_harness()

    def test_hard_hard_to_soft_hard_and_immediate_consumer(self) -> None:
        self.assertEqual(self.cases["hard_hard_crossing"]["pressure"], {"A": "hard", "B": "hard"})
        yielded = self.cases["diagnostic_yield"]
        self.assertTrue(yielded["declared"])
        self.assertTrue(yielded["diagnostic_only"])
        self.assertEqual(yielded["contact"], "crossing")
        self.assertEqual(yielded["pressure"], {"A": "hard", "B": "soft"})
        self.assertEqual(yielded["spiritus_spent"], 0)
        self.assertFalse(yielded["damage_created"])
        consumer = self.cases["zorn_ort_soft_consumer"]
        self.assertTrue(consumer["executed"])
        self.assertEqual(consumer["inspected_opponent_pressure"], "soft")
        self.assertEqual(consumer["contact_during"], "crossing")

    def test_yield_sequence_cleans_without_stale_pressure_or_zones(self) -> None:
        case = self.cases["yield_sequence_cleanup"]
        self.assertEqual(case["contact"], "none")
        self.assertEqual(case["zones"], {"A": "unknown", "B": "unknown"})
        self.assertEqual(case["pressure"], {"A": "unknown", "B": "unknown"})

    def test_rompere_retains_then_explicitly_closes(self) -> None:
        wide = self.cases["rompere_retained_crossing"]
        self.assertEqual(wide["contact"], "crossing")
        self.assertEqual(wide["measure"], "wide")
        self.assertTrue(wide["retained"])
        self.assertEqual(wide["zones"], {"A": "unknown", "B": "middle"})
        self.assertEqual(wide["displacement"][0]["contact_after"], "crossing")
        close = self.cases["rompere_close_control"]
        self.assertTrue(close["executed"])
        self.assertEqual((close["contact"], close["measure"]), ("crossing", "close"))
        self.assertFalse(close["random"])
        persisted = self.cases["rompere_retention_survives_cleanup"]
        self.assertEqual(persisted["contact"], "crossing")
        self.assertEqual(persisted["retained_crossings"], 1)

    def test_pommel_is_legal_only_after_explicit_close_and_sequence_cleans(self) -> None:
        case = self.cases["pommel_from_explicit_close"]
        self.assertTrue(case["prerequisite_satisfied"])
        self.assertTrue(case["executed"])
        self.assertEqual(case["uses"], 1)
        self.assertEqual(case["contact_after"], "none")
        self.assertEqual(case["zones_after"], {"A": "unknown", "B": "unknown"})
        self.assertEqual(case["pressure_after"], {"A": "unknown", "B": "unknown"})

    def test_zwerch_with_strong_is_phase_specific_asymmetric_geometry(self) -> None:
        case = self.cases["zwerch_with_strong_geometry"]
        self.assertEqual((case["contact"], case["measure"]), ("crossing", "wide"))
        self.assertEqual(case["zones"], {"A": "hiltward", "B": "unknown"})
        self.assertEqual(case["pressure"], {"A": "unknown", "B": "unknown"})
        self.assertFalse(case["generic_modifier"])
        cleanup = self.cases["zwerch_geometry_cleanup"]
        self.assertEqual(cleanup["contact"], "none")
        self.assertEqual(cleanup["zones"], {"A": "unknown", "B": "unknown"})

    def test_italian_reference_geometry_is_wide_and_modifier_free(self) -> None:
        point = self.cases["italian_point_crossing_reference"]
        self.assertEqual(point["zones"], {"A": "pointward", "B": "pointward"})
        self.assertEqual(point["measure"], "wide")
        self.assertFalse(point["generic_modifier"])
        middle = self.cases["italian_middle_crossing_reference"]
        self.assertEqual(middle["zones"], {"A": "middle", "B": "middle"})
        self.assertEqual(middle["measure"], "wide")
        self.assertFalse(middle["middle_is_close"])
        self.assertFalse(middle["generic_modifier"])

    def test_geometry_and_pressure_are_independent(self) -> None:
        a = self.cases["geometry_pressure_independence_a"]
        self.assertEqual(a["zones"], {"A": "hiltward", "B": "pointward"})
        self.assertEqual(a["pressure"], {"A": "soft", "B": "hard"})
        self.assertIsNone(a["modifier"])
        b = self.cases["geometry_pressure_independence_b"]
        self.assertEqual(b["zones"], {"A": "pointward", "B": "hiltward"})
        self.assertEqual(b["pressure"], {"A": "hard", "B": "soft"})
        self.assertIsNone(b["modifier"])

    def test_displacement_and_contact_are_independent(self) -> None:
        case = self.cases["displacement_contact_independence"]
        self.assertEqual(case["basic_beat"]["displacement"][0]["contact_after"], "none")
        self.assertEqual(case["basic_beat"]["contact_after"], "none")
        self.assertEqual(case["rompere"]["displacement"][0]["contact_after"], "crossing")
        self.assertEqual(case["rompere"]["contact_after"], "crossing")

    def test_fixture_model_and_phase_evidence_validate(self) -> None:
        validator_path = ROOT / "scripts" / "validate_repository.py"
        spec = importlib.util.spec_from_file_location("bind_fixture_validator", validator_path)
        validator = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.modules[spec.name] = validator
        spec.loader.exec_module(validator)
        model = json.loads((ROOT / "data" / "prototypes" / "longsword-bind-continuations-v0.1.yaml").read_text(encoding="utf-8"))
        schema = json.loads((ROOT / "schemas" / "mechanical-prototype-bind-continuations-v0.1.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(validator.validate_schema(model, schema), [])
        play = json.loads((ROOT / "data" / "plays" / "play-german-longsword-zwerchhau.yaml").read_text(encoding="utf-8"))
        play_schema = json.loads((ROOT / "schemas" / "play.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(validator.validate_schema(play, play_schema), [])
        self.assertEqual(play["historical_identity"]["source_status"], "needs-item-level-audit")

    def test_main_combat_still_has_no_natural_new_state_creators(self) -> None:
        for skill in (10, 14, 18):
            cell = SIM.Cell(skill, 8, "adaptive_revelation")
            metrics = SIM.run_cell(cell, 40, 20260811 + skill, "explicit")["metrics"]
            self.assertEqual(metrics["close_crossings_per_fight"], 0)
            self.assertEqual(metrics["hard_soft_crossings_per_fight"], 0)
            self.assertEqual(metrics["soft_hard_crossings_per_fight"], 0)
            self.assertEqual(metrics["known_zone_crossings_per_fight"], 0)
            self.assertEqual(metrics["precondition_violations"], 0)


if __name__ == "__main__":
    unittest.main()

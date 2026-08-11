from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_PATH = ROOT / "simulations" / "crossing_bind_state_model_v0_1" / "simulate.py"
SPEC = importlib.util.spec_from_file_location("crossing_bind_state_model", SIM_PATH)
SIM = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = SIM
SPEC.loader.exec_module(SIM)


class CrossingBindTransitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.transitions = SIM.transition_harness()

    def test_a_basic_cross_success(self) -> None:
        case = self.transitions["basic_cross_success"]
        self.assertEqual(case["result"], "success")
        self.assertEqual(case["contact"], "crossing")
        self.assertTrue(case["measure_preserved"])
        self.assertEqual(set(case["zones"].values()), {"unknown"})
        self.assertEqual(set(case["pressure"].values()), {"hard"})
        self.assertEqual(case["displacements"], [])

    def test_b_basic_beat_success(self) -> None:
        case = self.transitions["basic_beat_success"]
        self.assertEqual(case["result"], "success")
        self.assertEqual(case["contact"], "none")
        self.assertEqual(set(case["pressure"].values()), {"unknown"})
        self.assertEqual(len(case["displacements"]), 1)
        self.assertEqual(case["displacements"][0]["contact_after"], "none")

    def test_c_d_cross_durch_timing(self) -> None:
        for name in ("cross_durch", "beat_durch"):
            case = self.transitions[name]
            self.assertEqual(case["result"], "interrupted")
            self.assertEqual(case["spiritus_paid"], 1)
            self.assertEqual(case["parry_rolls"], 0)
            self.assertEqual(case["contact"], "none")
            self.assertEqual(case["point"], "threatening")

    def test_e_f_failed_parries(self) -> None:
        cross = self.transitions["failed_cross"]
        beat = self.transitions["failed_beat"]
        self.assertTrue(cross["damage_resolved"])
        self.assertEqual(cross["contact"], "none")
        self.assertTrue(beat["damage_resolved"])
        self.assertEqual(beat["displacements"], [])

    def test_g_h_single_time_crossings_cleanup(self) -> None:
        for name in ("absetzen", "scambiar_di_punta"):
            case = self.transitions[name]
            self.assertEqual(case["result"], "success")
            self.assertEqual(case["during_contact"], "crossing")
            self.assertEqual(case["point"], "threatening")
            self.assertEqual(case["after_cleanup"], "none")

    def test_i_durchwechseln_pre_bind_state(self) -> None:
        case = self.transitions["durchwechseln"]
        self.assertEqual(case, {"contact": "none", "point": "threatening"})

    def test_j_schielhau_no_automatic_crossing(self) -> None:
        case = self.transitions["schielhau"]
        self.assertEqual(case["result"], "success")
        self.assertEqual(case["contact"], "none")
        self.assertEqual(case["point"], "threatening")

    def test_k_rompere_displacement_can_retain_crossing(self) -> None:
        case = self.transitions["rompere_reference"]
        self.assertTrue(case["displaced"])
        self.assertEqual(case["contact"], "crossing")
        self.assertIn("middle", case["zones"].values())

    def test_l_crossing_cleanup(self) -> None:
        self.assertEqual(self.transitions["crossing_cleanup"], {"contact": "none", "cleanups": 1})

    def test_m_forced_close_crossing_pommel(self) -> None:
        case = self.transitions["forced_close_pommel"]
        self.assertTrue(case["executed"])
        self.assertEqual(case["uses"], 1)
        self.assertEqual(case["contact"], "none")

    def test_schema_and_model_validate(self) -> None:
        model = json.loads((ROOT / "data" / "prototypes" / "longsword-crossing-bind-state-model-v0.1.yaml").read_text(encoding="utf-8"))
        schema = json.loads((ROOT / "schemas" / "mechanical-prototype-crossing-bind-state-model-v0.1.schema.json").read_text(encoding="utf-8"))
        validator_path = ROOT / "scripts" / "validate_repository.py"
        spec = importlib.util.spec_from_file_location("crossing_model_validator", validator_path)
        validator = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.modules[spec.name] = validator
        spec.loader.exec_module(validator)
        self.assertEqual(validator.validate_schema(model, schema), [])

    def test_smoke_matrix_has_no_synthetic_primary_states(self) -> None:
        results = SIM.run_all(primary_trials=30, legacy_trials=10, seed=20260811, write=False)
        self.assertEqual(len(results["primary_matrix"]), 12)
        for item in results["primary_matrix"].values():
            metrics = item["metrics"]
            self.assertEqual(metrics["precondition_violations"], 0)
            self.assertEqual(metrics["close_crossings_per_fight"], 0)
            self.assertEqual(metrics["hard_soft_crossings_per_fight"], 0)
            self.assertEqual(metrics["soft_hard_crossings_per_fight"], 0)
            self.assertEqual(metrics["plays"][SIM.POMMEL]["opportunities_per_fight"], 0)


if __name__ == "__main__":
    unittest.main()

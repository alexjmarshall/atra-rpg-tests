from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_PATH = ROOT / "simulations" / "guard_play_bridge_v0_1" / "simulate.py"
IMPORT_SPEC = importlib.util.spec_from_file_location("guard_play_bridge_v01", SIM_PATH)
SIM = importlib.util.module_from_spec(IMPORT_SPEC)
assert IMPORT_SPEC.loader is not None
sys.modules[IMPORT_SPEC.name] = SIM
IMPORT_SPEC.loader.exec_module(SIM)


class GuardPlayBridgeDeterministicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = SIM.deterministic_harness()
        SIM.validate_harness(cls.cases)

    def test_tutta_correct_trigger_and_state_conversion(self) -> None:
        case = self.cases["A_tutta_success"]
        self.assertEqual((case["contact"], case["measure"], case["retained"]), ("crossing", "close", True))
        self.assertEqual(case["chain"], [SIM.TUTTA])
        self.assertEqual(case["hp_before"], case["hp_after"])
        self.assertEqual(case["attack_declarations_before"], case["attack_declarations_after"])
        self.assertEqual(case["parry_rolls"], 1)
        self.assertTrue(case["action_before"])
        self.assertFalse(case["action_after"])

    def test_wrong_guard_failed_cross_beat_and_durch_do_not_trigger(self) -> None:
        self.assertEqual(self.cases["B_wrong_guard"]["opportunities"], 0)
        self.assertEqual(self.cases["C_failed_cross"], {"opportunities": 0, "contact": "none"})
        self.assertEqual(self.cases["D_beat"], {"opportunities": 0, "contact": "none"})
        self.assertEqual(self.cases["E_durch_interruption"], {"opportunities": 0, "contact": "none"})

    def test_t0_t1_costs_no_second_roll_or_action_restoration(self) -> None:
        self.assertEqual(self.cases["F_G_costs"], {"T0": 0, "T1": 1})
        self.assertFalse(self.cases["A_tutta_success"]["action_after"])
        self.assertEqual(self.cases["A_tutta_success"]["declarations"], 1)

    def test_three_play_cap_and_attempted_fourth(self) -> None:
        self.assertEqual(self.cases["J_K_cap"]["legal_opportunity"], 0)
        self.assertFalse(self.cases["J_K_cap"]["used"])
        self.assertFalse(self.cases["J_K_cap"]["direct_fourth"])
        self.assertEqual(self.cases["J_K_cap"]["attempted_fourth_increment"], 1)

    def test_pommel_is_only_a_separate_downstream_consumer(self) -> None:
        case = self.cases["L_pommel_consumer"]
        self.assertFalse(case["immediate_while_action_spent"])
        self.assertTrue(case["later_with_action"])
        self.assertTrue(case["used"])
        self.assertEqual(case["contact_after"], "none")

    def test_ordinary_unretained_crossing_cleans(self) -> None:
        self.assertEqual(self.cases["M_cleanup"], {"before": "crossing", "after": "none", "measure": "wide"})

    def test_scheitelhau_remains_modifier_free_and_unpriced(self) -> None:
        case = self.cases["N_scheitelhau_specification"]
        self.assertFalse(case["initial_entry_implemented"])
        self.assertFalse(case["automatic_boon"])
        self.assertFalse(case["automatic_bane"])
        self.assertFalse(case["automatic_success"])
        self.assertFalse(case["automatic_damage_bonus"])
        self.assertFalse(case["generic_cross_is_crown"])
        self.assertIsNone(case["spiritus_cost"])

    def test_scoped_specification_record(self) -> None:
        model = json.loads((ROOT / "data" / "prototypes" / "longsword-guard-play-bridge-v0.1.yaml").read_text(encoding="utf-8"))
        self.assertEqual(model["scheitelhau_alber"]["classification"], "S-C")
        self.assertFalse(model["scheitelhau_alber"]["initial_entry_implemented"])
        self.assertEqual(model["tutta_cover_to_stretto"]["classification"], "LEARNED CONTINUATION")
        self.assertEqual(set(model["tutta_cover_to_stretto"]["candidates"]), {"T0", "T1"})

    def test_small_balanced_behavior_matrix_has_no_unauthorized_close(self) -> None:
        results = SIM.run_all(trials=32, seed=20260811, write=False)
        self.assertEqual(len(results["cells"]), 6)
        for item in results["cells"]:
            self.assertEqual(len(item["metrics"]["starting_guard_outcome_share"]), 16)
            self.assertEqual(item["metrics"]["unauthorized_close_origins"], 0)
            if item["cell"]["model"] == "CONTROL":
                self.assertEqual(item["metrics"]["wide_to_close_transitions_per_fight"], 0)


if __name__ == "__main__":
    unittest.main()

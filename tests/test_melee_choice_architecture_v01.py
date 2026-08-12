from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_PATH = ROOT / "simulations" / "melee_choice_architecture_v0_1" / "simulate.py"
SPEC = importlib.util.spec_from_file_location("melee_choice_architecture_v01", SIM_PATH)
SIM = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = SIM
SPEC.loader.exec_module(SIM)


class MeleeChoiceArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.regressions = SIM.regression_harness()
        SIM.validate_regressions(cls.regressions)

    def test_cross_immunity_only_cb1_cb3(self) -> None:
        self.assertEqual(self.regressions["CB0"]["cross_result_with_forced_d1"], "interrupted")
        self.assertEqual(self.regressions["CB1"]["cross_result_with_forced_d1"], "success")
        self.assertEqual(self.regressions["CB2"]["cross_result_with_forced_d1"], "interrupted")
        self.assertEqual(self.regressions["CB3"]["cross_result_with_forced_d1"], "success")

    def test_open_only_successful_cb2_cb3_beat(self) -> None:
        self.assertEqual(self.regressions["CB0"]["beat_attacker_guard"], "posta-di-donna")
        self.assertEqual(self.regressions["CB1"]["beat_attacker_guard"], "posta-di-donna")
        self.assertEqual(self.regressions["CB2"]["beat_attacker_guard"], SIM.OPEN)
        self.assertEqual(self.regressions["CB3"]["beat_attacker_guard"], SIM.OPEN)
        for cb in SIM.CB:
            self.assertEqual(self.regressions[cb]["failed_beat_attacker_guard"], "posta-di-donna")
            self.assertEqual(self.regressions[cb]["interrupted_beat_attacker_guard"], "posta-di-donna")

    def test_cross_and_beat_keep_governing_state_outcomes(self) -> None:
        self.assertEqual(self.regressions["CB3"]["cross_contact"], "crossing")
        for cb in SIM.CB:
            self.assertEqual(self.regressions[cb]["beat_contact"], "none")
            self.assertEqual(self.regressions[cb]["cross_generic_modifier"], 0)

    def test_open_has_no_intrinsics_or_gates_but_universal_basics(self) -> None:
        case = self.regressions["open"]
        self.assertEqual(case["state"]["guard"], SIM.OPEN)
        self.assertFalse(case["state"]["loaded"])
        self.assertFalse(case["guard_gate_while_open"])
        self.assertTrue(case["universal_cross"])
        self.assertTrue(case["universal_beat"])

    def test_open_recovery_consumes_change(self) -> None:
        case = self.regressions["open"]
        self.assertTrue(case["remained_open_voluntarily"])
        self.assertTrue(case["recovered"])
        self.assertFalse(case["second_switch"])
        self.assertEqual(case["recovery_count"], 1)

    def test_threatening_point_beat_denies_d1(self) -> None:
        self.assertEqual(
            self.regressions["point_threatening_beat"],
            {"result": "success", "durch_declarations": 0, "attacker_open": True},
        )

    def test_guard_timing(self) -> None:
        timing = self.regressions["guard_timing"]
        self.assertEqual(timing["GC0"], {"before": True, "after_after_attempt": False})
        self.assertEqual(timing["GC1"], {"before": True, "after_after_attempt": False})
        self.assertEqual(timing["GC2"], {"before": False, "after_after_attempt": True})
        self.assertEqual(timing["GC3"], {"before": False, "after_after_attempt": False})

    def test_fixed_baseline(self) -> None:
        fixed = self.regressions["fixed_baseline"]
        self.assertEqual((fixed["d1_cost"], fixed["compound_cost"], fixed["learned_play_cap"]), (1, 2, 3))
        self.assertEqual((fixed["p1_cost"], fixed["p1_damage"]), (1, 7))
        self.assertTrue(fixed["committed"])
        self.assertTrue(fixed["counter_first"])
        self.assertEqual(fixed["t1_cost"], 1)
        self.assertFalse(fixed["crown_used"])
        self.assertFalse(fixed["generic_guard_bonus_added"])

    def test_small_run_and_graph_gate(self) -> None:
        results = SIM.run_all(trials=40, seed=20260812, write=False)
        self.assertEqual(len(results["cross_beat"]["monte_carlo"]), 72)
        self.assertFalse(results["guard_commitment"]["behavioral"]["GC3"]["behavior_tested"])
        self.assertEqual(results["cross_beat"]["classifications"]["CB0"], "FALSE CHOICE")

    def test_machine_readable_artifacts(self) -> None:
        prototype = json.loads((ROOT / "data" / "prototypes" / "melee-choice-architecture-v0.1.yaml").read_text(encoding="utf-8"))
        transition = json.loads((ROOT / "data" / "research" / "longsword-guard-transition-map-v0.1.yaml").read_text(encoding="utf-8"))
        self.assertFalse(prototype["promotion"]["automatic"])
        self.assertFalse(transition["german"]["quality"]["behavior_testable"])
        self.assertFalse(transition["italian"]["quality"]["behavior_testable_as_sparse_graph"])


if __name__ == "__main__":
    unittest.main()

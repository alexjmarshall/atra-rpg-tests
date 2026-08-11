from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_PATH = ROOT / "simulations" / "scheitelhau_crown_v0_1" / "simulate.py"
IMPORT_SPEC = importlib.util.spec_from_file_location("scheitelhau_crown_v01", SIM_PATH)
SIM = importlib.util.module_from_spec(IMPORT_SPEC)
assert IMPORT_SPEC.loader is not None
sys.modules[IMPORT_SPEC.name] = SIM
IMPORT_SPEC.loader.exec_module(SIM)


class ScheitelhauCrownDeterministicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = SIM.deterministic_harness()
        SIM.validate_harness(cls.data)
        cls.cases = cls.data["cases"]

    def test_crown_is_authored_context_not_generic_cross(self) -> None:
        self.assertTrue(self.cases["A_entry_against_alber"]["scheitelhau_context"])
        self.assertTrue(self.cases["D_correct_response_creates_crown"]["crown_context"])
        self.assertEqual(
            self.cases["C_generic_cross_not_crown"],
            {"contact": "crossing", "crown_context": False},
        )

    def test_crown_uses_only_justified_state_fields(self) -> None:
        self.assertEqual(
            self.cases["E_exact_crown_fields"],
            {
                "contact": "crossing",
                "measure": "wide",
                "zones": {"A": "unknown", "B": "unknown"},
                "pressure": {"A": "unknown", "B": "unknown"},
                "retained": False,
            },
        )

    def test_point_sink_requires_crown_and_not_unrelated_crossing(self) -> None:
        self.assertTrue(self.cases["F_crown_enables_continuation"]["legal"])
        self.assertFalse(self.cases["G_no_crown_no_continuation"]["legal"])
        self.assertFalse(self.cases["H_unrelated_crossing_no_continuation"]["legal"])

    def test_no_generic_modifiers_bonus_damage_or_automatic_success(self) -> None:
        self.assertEqual(
            self.cases["I_no_generic_boon_bane"],
            {"attack_boon": False, "parry_bane": False},
        )
        self.assertEqual(self.cases["J_no_automatic_damage_bonus"]["bonus"], 0)
        self.assertEqual(
            self.cases["K_no_automatic_success"]["hp_before"],
            self.cases["K_no_automatic_success"]["hp_after"],
        )

    def test_german_crown_does_not_interact_with_italian_labels(self) -> None:
        self.assertFalse(self.cases["L_no_italian_interaction"]["legal"])

    def test_cleanup_and_chain_accounting(self) -> None:
        self.assertEqual(self.cases["M_crown_context_cleanup"], {"before": True, "after": False})
        self.assertEqual(self.cases["N_ordinary_crossing_cleanup"], {"before": "crossing", "after": "none"})
        self.assertEqual(self.cases["O_three_play_cap_respected"]["length"], 3)
        self.assertEqual(self.cases["P_b3_accounting"]["chain"], [SIM.SINK])
        fourth = self.cases["Q_no_fourth_play_leakage"]
        self.assertFalse(fourth["used"])
        self.assertEqual(fourth["before"], fourth["after"])
        self.assertEqual(fourth["attempted_fourth"], 1)

    def test_every_case_has_complete_phase_trace(self) -> None:
        expected = {
            "BEFORE",
            "SCHEITELHAU ENTRY",
            "DEFENDER RESPONSE",
            "CROWN CREATION OR NON-CREATION",
            "ATTACKER CONTINUATION OPPORTUNITY",
            "AFTER CONTINUATION",
            "CLEANUP",
        }
        self.assertEqual(set(self.data["phase_traces"]), set("ABCDEFGHIJKLMNOPQ"))
        for trace in self.data["phase_traces"].values():
            self.assertEqual(set(trace), expected)

    def test_scoped_specification(self) -> None:
        spec = json.loads((ROOT / "data" / "prototypes" / "scheitelhau-crown-v0.1.yaml").read_text(encoding="utf-8"))
        self.assertEqual(spec["crown_candidates"]["C1"]["representation"], "ordinary Crossing plus transient crown_context")
        self.assertEqual(spec["recommended_chassis"]["chain_model"], "B3")
        self.assertEqual(spec["recommended_chassis"]["spiritus_cost"], 1)
        self.assertFalse(spec["defender_response"]["learned_play"])
        self.assertFalse(spec["defender_response"]["generic_basic_cross_is_crown"])
        self.assertFalse(spec["promotion"]["automatic_promotion"])

    def test_small_balanced_micro_matrix(self) -> None:
        results = SIM.run_all(trials=32, seed=20260811, write=False)
        self.assertEqual(len(results["cells"]), 4)
        for item in results["cells"]:
            metrics = item["metrics"]
            self.assertEqual(len(metrics["starting_guard_outcome_share"]), 16)
            self.assertEqual(metrics["generic_crosses_incorrectly_tagged_crown"], 0)
            self.assertEqual(metrics["unrelated_crossings_triggering_continuation"], 0)
            self.assertEqual(metrics["cleanup_errors"], 0)
            self.assertEqual(metrics["attempted_fourth_plays"], 0)


if __name__ == "__main__":
    unittest.main()

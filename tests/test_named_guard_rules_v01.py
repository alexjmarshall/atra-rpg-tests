from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_PATH = ROOT / "simulations" / "named_guard_rules_v0_1" / "simulate.py"
SPEC = importlib.util.spec_from_file_location("named_guard_rules_v01", SIM_PATH)
SIM = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = SIM
SPEC.loader.exec_module(SIM)


class NamedGuardDeterministicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = SIM.deterministic_harness()
        SIM.validate_harness(cls.cases)

    def test_a_to_c_guard_point_states(self) -> None:
        self.assertEqual(self.cases["A_ochs"]["point_threat"], "threatening")
        self.assertEqual(self.cases["B_pflug"]["point_threat"], "threatening")
        self.assertEqual(self.cases["C_alber"]["point_threat"], "not_threatening")

    def test_d_vom_tag_is_not_loaded(self) -> None:
        self.assertFalse(self.cases["D_vom_tag_not_loaded"]["loaded"])
        self.assertFalse(self.cases["D_vom_tag_not_loaded"]["cut"])

    def test_e_to_g_donna_loaded_power_scope(self) -> None:
        self.assertEqual(self.cases["E_donna_loaded_cut"], {"loaded": True, "damage": 6})
        self.assertEqual(self.cases["F_donna_power"], {"declared": True, "spent": 1, "damage": 7})
        self.assertFalse(self.cases["G_leave_donna"]["loaded"])
        self.assertFalse(self.cases["G_leave_donna"]["power"])

    def test_h_point_threat_uses_existing_d1_state_trigger(self) -> None:
        case = self.cases["H_point_threat_d1"]
        self.assertEqual(case["denied_windows"], 1)
        self.assertEqual(case["open_declarations"], 1)
        self.assertFalse(case["modifier_added"])

    def test_i_to_k_universal_basic_actions_and_mapping_no_bonus(self) -> None:
        self.assertTrue(self.cases["I_universal_cross"]["legal"])
        self.assertTrue(self.cases["J_universal_beat"]["legal"])
        self.assertEqual(self.cases["K_mapping_no_bonus"], {"extra_attack_bonus": 0, "extra_parry_bonus": 0})

    def test_l_to_n_g1_g2_boundary_and_chain(self) -> None:
        self.assertFalse(self.cases["L_g1_compound_not_free"]["free_action_legal"])
        self.assertTrue(self.cases["M_g2_compound_free"]["free_action_legal"])
        self.assertEqual(self.cases["N_g2_not_chain"]["before"], [])
        self.assertEqual(self.cases["N_g2_not_chain"]["after"], [])

    def test_o_to_q_guard_change_and_no_stale_state(self) -> None:
        self.assertEqual(self.cases["O_change_once"], {"before": True, "after": False})
        self.assertEqual(self.cases["P_immediate_state"]["guard"], "ochs")
        self.assertFalse(self.cases["Q_no_stale_state"]["loaded"])
        self.assertEqual(self.cases["Q_no_stale_state"]["hanging_tags"], [])

    def test_r_breaker_annotation_has_no_automatic_modifier(self) -> None:
        self.assertFalse(any(self.cases["R_breaker_annotation_only"].values()))

    def test_s_source_backed_mezza_point_state_applies_and_clears(self) -> None:
        self.assertEqual(
            self.cases["S_mezza_point_state_clears"],
            {"before": "threatening", "after": "not_threatening"},
        )

    def test_t_scambiar_is_guard_gated_without_a_modifier(self) -> None:
        self.assertEqual(self.cases["T_scambiar_guard_access"], {"tutta": True, "frontale": False})

    def test_guard_schema_data_shape(self) -> None:
        data = json.loads((ROOT / "data" / "guards" / "longsword-named-v0.1.yaml").read_text(encoding="utf-8"))
        self.assertEqual(len(data["guards"]), 8)
        self.assertEqual({g["tradition"] for g in data["guards"]}, {"German", "Italian"})

    def test_small_balanced_matrix(self) -> None:
        results = SIM.run_all(trials=16, seed=20260811, write=False)
        self.assertEqual(len(results["cells"]), 36)
        for item in results["cells"]:
            self.assertEqual(len(item["metrics"]["starting_guard_outcome_share"]), 16)


if __name__ == "__main__":
    unittest.main()

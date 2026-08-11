from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_PATH = ROOT / "simulations" / "loaded_power_attack_v0_1" / "simulate.py"
SPEC = importlib.util.spec_from_file_location("loaded_power_attack_v01", SIM_PATH)
SIM = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = SIM
SPEC.loader.exec_module(SIM)


class LoadedPowerAttackDeterministicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = SIM.deterministic_harness()
        SIM.validate_harness(cls.cases)

    def test_a_loaded_proactive_cut_gets_damage_boon(self) -> None:
        case = self.cases["A_loaded_cut"]
        self.assertTrue(case["damage_boon"])
        self.assertEqual(case["dice"], [2, 5])
        self.assertEqual(case["damage"], 6)

    def test_b_loaded_thrust_gets_no_damage_boon(self) -> None:
        case = self.cases["B_loaded_thrust"]
        self.assertFalse(case["damage_boon"])
        self.assertEqual(case["damage"], 3)

    def test_c_loaded_counter_gets_no_damage_boon(self) -> None:
        case = self.cases["C_loaded_counter"]
        self.assertFalse(case["damage_boon"])
        self.assertEqual(case["damage"], 3)

    def test_d_power_pays_at_declaration(self) -> None:
        case = self.cases["D_power_declaration_cost"]
        self.assertTrue(case["declared"])
        self.assertEqual(case["spent"], 1)
        self.assertEqual(case["timing"], "declaration")

    def test_e_p1_is_exactly_seven_without_damage_roll(self) -> None:
        self.assertEqual(self.cases["E_p1_damage"], {"damage": 7, "rolled": False})

    def test_f_p2_uses_attack_bane_and_2d6_plus_1(self) -> None:
        case = self.cases["F_p2"]
        self.assertTrue(case["attack_bane"])
        self.assertEqual(case["spent"], 1)
        self.assertEqual(case["damage"], 3 + 4 + 1)

    def test_g_p3_costs_two_and_uses_2d6_plus_1(self) -> None:
        case = self.cases["G_p3"]
        self.assertEqual(case["spent"], 2)
        self.assertEqual(case["damage"], 3 + 4 + 1)

    def test_h_p4_doubles_one_ordinary_final_damage(self) -> None:
        case = self.cases["H_p4"]
        self.assertEqual(case["spent"], 2)
        self.assertEqual(case["damage"], 2 * case["ordinary_damage"])

    def test_i_power_cross_cancels_and_forms_crossing(self) -> None:
        case = self.cases["I_power_cross"]
        self.assertEqual(case["result"], "success")
        self.assertEqual(case["damage"], 0)
        self.assertEqual(case["contact"], "crossing")
        self.assertEqual(set(case["pressure"].values()), {"hard"})

    def test_j_power_beat_cancels_displaces_and_separates(self) -> None:
        case = self.cases["J_power_beat"]
        self.assertEqual(case["result"], "success")
        self.assertEqual(case["damage"], 0)
        self.assertTrue(case["displaced"])
        self.assertEqual(case["contact"], "none")

    def test_k_committed_power_cannot_throughchange(self) -> None:
        case = self.cases["K_power_durch"]
        self.assertFalse(case["legal"])
        self.assertEqual(case["spiritus_spent"], 0)
        self.assertEqual(case["durch_declarations"], 0)
        self.assertEqual(case["chain"], [])

    def test_l_ordinary_loaded_cut_retains_d1(self) -> None:
        case = self.cases["L_loaded_cut_durch"]
        self.assertTrue(case["legal"])
        self.assertEqual(case["spent"], 1)
        self.assertEqual(case["declarations"], 1)

    def test_m_counter_first_survival_allows_power(self) -> None:
        case = self.cases["M_counter_first_survives"]
        self.assertGreater(case["attacker_hp"], 0)
        self.assertEqual(case["defender_hp"], 1)
        self.assertEqual(case["interrupted"], 0)

    def test_n_counter_first_removal_cancels_power(self) -> None:
        case = self.cases["N_counter_first_removes"]
        self.assertEqual(case["attacker_hp"], 0)
        self.assertEqual(case["defender_hp"], 8)
        self.assertEqual(case["interrupted"], 1)

    def test_o_ordinary_counter_remains_simultaneous(self) -> None:
        self.assertTrue(self.cases["O_ordinary_counter_simultaneous"]["both_removed"])

    def test_p_power_replaces_loaded_damage_boon(self) -> None:
        case = self.cases["P_no_loaded_power_stack"]
        self.assertEqual(case["power_damage"], 7)
        self.assertFalse(case["combined"])

    def test_q_power_does_not_count_toward_play_cap(self) -> None:
        case = self.cases["Q_power_not_learned_play"]
        self.assertEqual(case["before"], [])
        self.assertEqual(case["after"], [])
        self.assertEqual(case["cap"], 3)

    def test_r_committed_blocks_other_attacker_play(self) -> None:
        case = self.cases["R_committed_blocks_attacker_play"]
        self.assertFalse(case["legal"])
        self.assertEqual(case["blocked"], 1)

    def test_s_defender_play_remains_legal(self) -> None:
        case = self.cases["S_defender_play_legal"]
        self.assertEqual(case["result"], "success")
        self.assertEqual(case["defender_play_uses"], 1)
        self.assertTrue(case["attacker_damaged"])

    def test_small_matrix_preserves_engine_boundaries(self) -> None:
        results = SIM.run_all(primary_trials=8, sensitivity_trials=8, seed=20260811, write=False)
        self.assertEqual(len(results["stress_matrix"]), 36)
        self.assertEqual(len(results["counter_first_sensitivity"]), 4)
        for item in results["stress_matrix"].values():
            metrics = item["metrics"]
            self.assertEqual(metrics["precondition_violations"], 0)
            self.assertEqual(metrics["illegal_throughchange_attempts"], 0)
            self.assertEqual(metrics["illegal_attacker_play_insertions"], 0)
            self.assertEqual(metrics["attempted_fourth_plays"], 0)
            self.assertEqual(metrics["close_crossings_per_fight"], 0)
            self.assertEqual(metrics["hard_soft_crossings_per_fight"], 0)
            self.assertEqual(metrics["soft_hard_crossings_per_fight"], 0)
            self.assertEqual(metrics["known_zone_crossings_per_fight"], 0)


if __name__ == "__main__":
    unittest.main()

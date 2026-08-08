from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SELECTED_PROTOTYPE_IDS = {
    "play-german-longsword-absetzen",
    "play-german-longsword-zornhau-ort",
    "play-german-longsword-durchwechseln",
    "play-italian-longsword-scambiar-di-punta",
    "play-german-longsword-nachreisen",
    "play-italian-longsword-pommel-strike",
}
MIRRORED_PROTOTYPE_IDS = SELECTED_PROTOTYPE_IDS | {"play-german-longsword-schielhau"}


class RepositoryValidationTests(unittest.TestCase):
    def test_dependency_free_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_repository.py"), "--write-reports"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_exactly_114_parseable_play_records(self) -> None:
        paths = sorted((ROOT / "data" / "plays").glob("*.yaml"))
        self.assertEqual(len(paths), 114)
        records = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
        self.assertEqual(len({record["id"] for record in records}), 114)

    def test_no_candidate_claims_finished_mechanics(self) -> None:
        for path in (ROOT / "data" / "plays").glob("*.yaml"):
            record = json.loads(path.read_text(encoding="utf-8"))
            implementation = record["game_implementation"]
            self.assertEqual(implementation["candidate_status"], "research-candidate")
            self.assertEqual(implementation["mechanics_status"], "unimplemented")
            self.assertTrue(all(value is None for value in implementation["mechanics"].values()))

    def test_four_requested_audits_exist(self) -> None:
        for name in (
            "source-audit.md",
            "duplicate-chassis-audit.md",
            "curriculum-coverage-audit.md",
            "skill-equipment-audit.md",
        ):
            path = ROOT / "reports" / name
            self.assertTrue(path.exists(), name)
            self.assertGreater(path.stat().st_size, 200, name)

    def test_prototype_longsword_audit_and_selected_promotions_are_scoped(self) -> None:
        audited = []
        for path in (ROOT / "data" / "plays").glob("*.yaml"):
            record = json.loads(path.read_text(encoding="utf-8"))
            audit = record.get("prototype_evidence_audit")
            if audit is None:
                continue
            audited.append(record)
            self.assertEqual(audit["status"], "PROPOSED")
            self.assertEqual(audit["recommended_test_skill"]["status"], "PROPOSED")
            if record["id"] in SELECTED_PROTOTYPE_IDS:
                self.assertEqual(record["historical_identity"]["historical_confidence"], "A")
                self.assertEqual(record["historical_identity"]["source_status"], "exact-locator-verified")
                self.assertEqual(record["historical_identity"]["source_inclusion_basis"], "EARLIER")
                self.assertTrue(any(
                    citation["citation_status"] == "exact-historical-location"
                    for citation in record["historical_identity"]["source_citations"]
                ))
            else:
                self.assertIsNone(record["historical_identity"]["historical_confidence"])
                self.assertEqual(record["historical_identity"]["source_status"], "needs-item-level-audit")
            self.assertIsNone(record["game_implementation"]["character_sheet_test_skill"])
            self.assertIsNone(record["game_implementation"]["secondary_skill_prerequisites"])
            self.assertTrue(all(value is None for value in record["game_implementation"]["mechanics"].values()))
        self.assertEqual(len(audited), 13)
        report = ROOT / "reports" / "prototype-longsword-evidence-audit.md"
        self.assertTrue(report.exists())
        self.assertGreater(report.stat().st_size, 1000)

    def test_mechanical_branch_is_provisional_and_exactly_six_plays(self) -> None:
        path = ROOT / "data" / "prototypes" / "longsword-mechanical-v0.1.yaml"
        model = json.loads(path.read_text(encoding="utf-8"))
        schema = json.loads((ROOT / "schemas" / "mechanical-prototype.schema.json").read_text(encoding="utf-8"))
        validator_path = ROOT / "scripts" / "validate_repository.py"
        spec = importlib.util.spec_from_file_location("repository_validator", validator_path)
        validator = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.modules[spec.name] = validator
        spec.loader.exec_module(validator)
        self.assertEqual(validator.validate_schema(model, schema), [])
        self.assertEqual(model["status"], "PROVISIONAL")
        self.assertEqual(set(model["scope"]["selected_play_ids"]), SELECTED_PROTOTYPE_IDS)
        self.assertEqual(set(model["combat_state"]["blade_contact"]), {"none", "bind-crossing", "close-crossing"})
        self.assertIn("recovering-from-missed-committed-cut", model["combat_state"]["recovery_commitment"])
        self.assertEqual(set(model["variants"]), {"A", "B", "C"})
        plays = {item["play_id"]: item for item in model["plays"]}
        self.assertEqual(set(plays), SELECTED_PROTOTYPE_IDS)
        for play in plays.values():
            self.assertEqual(play["status"], "PROVISIONAL")
            self.assertIsNone(play["spiritus_cost"])
            self.assertIsNone(play["tier_requirement"])
            self.assertIsNone(play["final_wording"])
        self.assertEqual(plays["play-german-longsword-durchwechseln"]["trigger"]["opponent_defence"], "blade-seeking")
        self.assertEqual(plays["play-german-longsword-durchwechseln"]["trigger"]["blade_contact"], "none-before-firm-contact")
        self.assertEqual(plays["play-german-longsword-nachreisen"]["trigger"]["target_recovery_commitment"], "recovering-from-missed-committed-cut")
        pommel = plays["play-italian-longsword-pommel-strike"]
        self.assertEqual(pommel["trigger"]["blade_contact"], "close-crossing")
        self.assertIsNone(pommel["secondary_skill_prerequisites"])

    def test_simulation_variants_and_preconditions(self) -> None:
        module_path = ROOT / "simulations" / "longsword_prototype_v0_1" / "simulate.py"
        spec = importlib.util.spec_from_file_location("longsword_sim", module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        results = module.run_all(trials=600, seed=99173, write=False)
        for scenario, cells in results["cells"].items():
            self.assertTrue(all(stats["uses"] == 0 for stats in cells["baseline"]["plays"].values()), scenario)
            for variant in ("A", "B", "C"):
                self.assertEqual(cells[variant]["precondition_violations"], 0, (scenario, variant))
            self.assertEqual(sum(item["actions_preserved"] for item in cells["A"]["plays"].values()), 0)
            self.assertGreater(sum(item["actions_preserved"] for item in cells["B"]["plays"].values()), 0)
            self.assertEqual(sum(item["actions_preserved"] for item in cells["C"]["plays"].values()), 0)
            for play_id in ("play-german-longsword-absetzen", "play-italian-longsword-scambiar-di-punta"):
                c_stats = cells["C"]["plays"][play_id]
                self.assertGreaterEqual(c_stats["defensive_successes"], c_stats["successes"])

    def test_mirrored_prototype_and_schielhau_rejoinder(self) -> None:
        model_path = ROOT / "data" / "prototypes" / "longsword-mechanical-v0.2.yaml"
        model = json.loads(model_path.read_text(encoding="utf-8"))
        schema = json.loads((ROOT / "schemas" / "mechanical-prototype-v0.2.schema.json").read_text(encoding="utf-8"))
        validator_path = ROOT / "scripts" / "validate_repository.py"
        spec = importlib.util.spec_from_file_location("repository_validator_v2", validator_path)
        validator = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.modules[spec.name] = validator
        spec.loader.exec_module(validator)
        self.assertEqual(validator.validate_schema(model, schema), [])
        self.assertEqual(set(model["scope"]["selected_play_ids"]), MIRRORED_PROTOTYPE_IDS)
        self.assertTrue(model["scope"]["mirrored_repertoire"])
        self.assertEqual(model["rules"]["combined_variant"], "A")
        self.assertFalse(model["rules"]["action_preservation"])
        for play in model["plays"]:
            self.assertEqual(play["status"], "PROVISIONAL")
            self.assertIsNone(play["spiritus_cost"])
            self.assertIsNone(play["tier_requirement"])
        schiel = next(play for play in model["plays"] if play["play_id"] == "play-german-longsword-schielhau")
        self.assertIn("Pseudo-Peter von Danzig", schiel["source"])
        self.assertIn("same opponent", schiel["trigger"])
        record = json.loads((ROOT / "data" / "plays" / "play-german-longsword-schielhau.yaml").read_text(encoding="utf-8"))
        self.assertEqual(record["historical_identity"]["source_status"], "exact-locator-verified")
        self.assertEqual(record["historical_identity"]["historical_confidence"], "A")

    def test_mirrored_ablation_simulation_exercises_rejoinder_and_cap(self) -> None:
        module_path = ROOT / "simulations" / "longsword_prototype_v0_2" / "simulate.py"
        spec = importlib.util.spec_from_file_location("longsword_sim_v2", module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        results = module.run_all(trials=1000, seed=515151, write=False)
        full = results["cells"]["full"]
        self.assertEqual(full["precondition_violations"], 0)
        self.assertGreater(full["basic_defence_durch_opportunity_fraction"], 0)
        self.assertLess(full["basic_defence_durch_opportunity_fraction"], 1)
        self.assertGreater(full["durch_attempts"], 0)
        self.assertGreater(full["plays"]["play-german-longsword-schielhau"]["rejoinder_attempts"], 0)
        self.assertGreater(full["plays"]["play-german-longsword-schielhau"]["rejoinder_successes"], 0)
        self.assertGreater(full["chain_distribution_fraction"]["3"], 0)
        without_durch = results["cells"]["without:play-german-longsword-durchwechseln"]
        self.assertEqual(without_durch["durch_attempts"], 0)
        self.assertEqual(without_durch["chain_distribution_fraction"]["3"], 0)
        without_schiel = results["cells"]["without:play-german-longsword-schielhau"]
        self.assertEqual(without_schiel["rejoinder_attempts_per_fight"], 0)


if __name__ == "__main__":
    unittest.main()

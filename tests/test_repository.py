from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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

    def test_prototype_longsword_audit_is_proposal_only(self) -> None:
        audited = []
        for path in (ROOT / "data" / "plays").glob("*.yaml"):
            record = json.loads(path.read_text(encoding="utf-8"))
            audit = record.get("prototype_evidence_audit")
            if audit is None:
                continue
            audited.append(record)
            self.assertEqual(audit["status"], "PROPOSED")
            self.assertEqual(audit["recommended_test_skill"]["status"], "PROPOSED")
            self.assertIsNone(record["historical_identity"]["historical_confidence"])
            self.assertEqual(record["historical_identity"]["source_status"], "needs-item-level-audit")
            self.assertIsNone(record["game_implementation"]["character_sheet_test_skill"])
            self.assertIsNone(record["game_implementation"]["secondary_skill_prerequisites"])
            self.assertTrue(all(value is None for value in record["game_implementation"]["mechanics"].values()))
        self.assertEqual(len(audited), 13)
        report = ROOT / "reports" / "prototype-longsword-evidence-audit.md"
        self.assertTrue(report.exists())
        self.assertGreater(report.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()

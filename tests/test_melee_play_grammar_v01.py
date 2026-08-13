from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MeleePlayGrammarV01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = ROOT / "scripts" / "validate_melee_play_grammar.py"
        spec = importlib.util.spec_from_file_location("melee_grammar_validator", path)
        cls.validator = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.modules[spec.name] = cls.validator
        spec.loader.exec_module(cls.validator)

    def test_mapping_validates_with_expected_incompleteness_only(self) -> None:
        errors, findings = self.validator.validate()
        self.assertEqual(errors, [])
        codes = {(item.technique, item.code) for item in findings}
        self.assertIn(("nachreisen-current", "TRIGGER_NOT_PAYOFF"), codes)
        self.assertNotIn(("zornhau-ort-current", "GHOST_UTILITY"), codes)
        self.assertNotIn(("zornhau-ort-current", "MISSING_EFFECT_EXPOSED"), codes)
        self.assertNotIn(("winden-current-material", "MISSING_PRIMARY_PAYLOAD"), codes)
        self.assertNotIn(("winden-current-material", "MISSING_EFFECT_EXPOSED"), codes)
        self.assertIn(("frontale-current-sequence", "MISSING_PRIMARY_PAYLOAD"), codes)

    def test_vocabulary_closure_and_forbidden_control(self) -> None:
        vocabulary = json.loads((ROOT / "data" / "rules" / "melee-mechanical-effect-vocabulary-v0.1.yaml").read_text(encoding="utf-8"))
        operators = {item["id"] for item in vocabulary["low_level_operators"]}
        self.assertEqual(operators, {"ATTACK", "CANCEL", "SET", "CLEAR", "RETAIN", "MODIFY_ATTACK", "REPLACE_PENDING_ATTACK", "RESTRICT_RESPONSE"})
        self.assertIn("CONTROL", {item["term"] for item in vocabulary["forbidden_terms"]})
        displacement = next(item for item in vocabulary["event_metadata_vocabulary"] if item["id"] == "displacement")
        self.assertIsNone(displacement["current_consumer"])

    def test_phase_zero_adjudication_is_persisted(self) -> None:
        governing = json.loads((ROOT / "data" / "prototypes" / "longsword-governing-provisional-v0.1.yaml").read_text(encoding="utf-8"))
        self.assertIn("STATE-BASED D1", governing["basic_parry"]["selected_variant"])
        self.assertIn("yes when", governing["durchwechseln"]["legal_against_declared_cross"])
        self.assertIn("SUPERSEDED", governing["durchwechseln"]["blanket_cross_immunity"])
        self.assertEqual(governing["named_guard_architecture"]["guard_change"]["selected_variant"], "GC1")
        self.assertEqual(governing["choice_architecture_v0_1_adjudication"]["crown_c1_b3"], "CANDIDATE ONLY; UNRESOLVED; NOT GOVERNING")


if __name__ == "__main__":
    unittest.main()

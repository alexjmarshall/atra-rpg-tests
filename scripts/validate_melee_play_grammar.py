"""Validate the bounded Atra melee mechanical grammar and mapping.

The repository stores JSON-compatible YAML, so this validator remains dependency-free.
Incomplete/candidate techniques are permitted: their missing mechanics are emitted as
expected findings rather than being silently promoted or made fatal.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VOCABULARY_PATH = ROOT / "data" / "rules" / "melee-mechanical-effect-vocabulary-v0.1.yaml"
SCHEMA_PATH = ROOT / "schemas" / "melee-play-grammar-v0.1.schema.json"
MAPPING_PATH = ROOT / "data" / "audits" / "longsword-vertical-slice-mechanical-mapping-v0.1.yaml"


@dataclass(frozen=True)
class Finding:
    severity: str
    technique: str
    code: str
    message: str

    def render(self) -> str:
        return f"{self.severity} [{self.code}] {self.technique}: {self.message}"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate() -> tuple[list[str], list[Finding]]:
    vocabulary = load(VOCABULARY_PATH)
    schema = load(SCHEMA_PATH)
    mapping = load(MAPPING_PATH)
    errors: list[str] = []
    findings: list[Finding] = []

    # The checked-in schema is itself a required, parseable artifact. This validator
    # enforces its task-critical contract without adding a third-party dependency.
    if schema.get("title") != "Atra Melee Play Grammar v0.1":
        errors.append("schema: unexpected title or version")
    for key in ("id", "status", "vocabulary", "state_registry", "techniques"):
        if key not in mapping:
            errors.append(f"mapping: missing required property {key!r}")
    techniques = mapping.get("techniques", [])
    if not isinstance(techniques, list) or not techniques:
        errors.append("mapping: techniques must be a non-empty array")
        return errors, findings

    approved_ops = {item["id"] for item in vocabulary["low_level_operators"]}
    approved_states = {item["id"] for item in vocabulary["state_registry"]}
    approved_events = {item["id"] for item in vocabulary["event_metadata_vocabulary"]}
    required = {
        "id", "name", "status", "historical_source", "trigger", "cost_commitment", "test",
        "primary_payload", "state_aftermath", "continuation", "opponent_counterplay",
        "event_metadata", "nearest_basic_alternative", "distinct_reason", "reason_types",
        "simulator_representation", "ghost_utility", "missing_effect_exposed",
        "completeness_classification", "exceptional_rule",
    }
    ids: set[str] = set()
    for index, technique in enumerate(techniques):
        label = technique.get("id", f"techniques[{index}]")
        missing = sorted(required - set(technique))
        if missing:
            errors.append(f"{label}: missing required fields {missing}")
            continue
        if label in ids:
            errors.append(f"{label}: duplicate technique id")
        ids.add(label)

        if not technique["trigger"]:
            errors.append(f"{label}: missing Trigger")
        if not technique["test"]:
            errors.append(f"{label}: missing Test")
        if not technique["nearest_basic_alternative"].strip():
            errors.append(f"{label}: no nearest Basic alternative declared")
        if not technique["distinct_reason"].strip():
            errors.append(f"{label}: no mechanical distinction from nearest Basic stated")

        payload = technique["primary_payload"]
        incomplete_allowed = technique["status"] in {"incomplete", "candidate"}
        if not payload:
            finding = Finding(
                "EXPECTED" if incomplete_allowed else "ERROR", label, "MISSING_PRIMARY_PAYLOAD",
                "No Primary Payload operation is declared."
            )
            findings.append(finding)
            if not incomplete_allowed:
                errors.append(finding.render())

        all_operations = [*payload, *technique["state_aftermath"]]
        has_response_modifier = False
        for operation in all_operations:
            op = operation.get("op")
            if op not in approved_ops:
                errors.append(f"{label}: payload term/operator {op!r} is not approved")
            state = operation.get("state")
            if state is not None and state not in approved_states:
                errors.append(f"{label}: undefined state writer {state!r}")
            normalized = " ".join(str(value) for value in operation.values()).lower()
            if "control" in normalized and "counter" not in normalized:
                errors.append(f"{label}: generic control effect is forbidden; decompose it")
            if op in {"RESTRICT_RESPONSE", "REPLACE_PENDING_ATTACK"}:
                has_response_modifier = True
                if not operation.get("exceptional_justification"):
                    errors.append(f"{label}: response modification lacks exceptional justification")

        if has_response_modifier and not technique["exceptional_rule"]["present"]:
            errors.append(f"{label}: response modification is not marked exceptional")
        if technique["exceptional_rule"]["present"] and not has_response_modifier:
            # Counter-first and S2 live as explicit attack/test modifiers rather than
            # RESTRICT_RESPONSE; retain a visible, informative finding.
            findings.append(Finding("NOTICE", label, "EXCEPTIONAL_NON_RESTRICTION", technique["exceptional_rule"]["notes"]))

        for event in technique["event_metadata"]:
            if event.get("event") not in approved_events:
                errors.append(f"{label}: unapproved event metadata {event.get('event')!r}")

        effect_labels = " ".join(operation.get("label", "") for operation in all_operations).lower()
        trigger_labels = " ".join(item.get("id", "") for item in technique["trigger"]).lower()
        if label == "nachreisen-current" and "opponent_recovering" in trigger_labels:
            findings.append(Finding("EXPECTED", label, "TRIGGER_NOT_PAYOFF", "Recovering is correctly recorded as a trigger; the current payload remains an ordinary attack."))
        if "exploit_recovery" in effect_labels or "opponent_recovering" in effect_labels:
            errors.append(f"{label}: trigger incorrectly presented as an effect")
        if "opponent_recovering" in trigger_labels and not any(op.get("op") == "ATTACK" for op in payload):
            findings.append(Finding("NOTICE", label, "RECOVERY_TRIGGER_WITHOUT_ATTACK", "Recovery trigger has no attack payload."))

        no_distinction = technique["reason_types"] == ["none"] or technique["distinct_reason"].lower().startswith("none")
        if no_distinction:
            findings.append(Finding(
                "EXPECTED" if incomplete_allowed else "ERROR", label, "NO_MECHANICAL_DISTINCTION",
                "Technique declares no rational mechanical distinction from its nearest Basic."
            ))
            if not incomplete_allowed:
                errors.append(findings[-1].render())
        if technique["missing_effect_exposed"]["present"]:
            findings.append(Finding("EXPECTED", label, "MISSING_EFFECT_EXPOSED", technique["missing_effect_exposed"]["notes"]))
        if technique["ghost_utility"]["present"]:
            findings.append(Finding("EXPECTED", label, "GHOST_UTILITY", technique["ghost_utility"]["notes"]))

    expected_ids = {
        "basic-cut", "basic-thrust", "basic-cross-cb3", "basic-beat-cb3", "basic-counter",
        "basic-ignore", "voluntary-guard-change-gc1", "loaded-proactive-cut", "power-attack-p1",
        "durchwechseln-d1", "absetzen-c2", "scambiar-di-punta-c2", "schielhau-s2",
        "tutta-cover-to-stretto-t1", "pommel-strike", "nachreisen-current", "zornhau-ort-current",
        "winden-current-material", "frontale-current-sequence", "scheitelhau-crown-c1-b3",
    }
    missing_ids = sorted(expected_ids - ids)
    extra_ids = sorted(ids - expected_ids)
    if missing_ids or extra_ids:
        errors.append(f"stress-test inventory mismatch: missing={missing_ids}, extra={extra_ids}")

    return errors, findings


def main() -> int:
    errors, findings = validate()
    print(f"Validated melee grammar mapping: {len(errors)} error(s), {len(findings)} informative finding(s).")
    for finding in findings:
        print(finding.render())
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

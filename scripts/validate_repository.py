"""Dependency-free validation and research-gap reporting for Atra melee data."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PLAY_DIR = ROOT / "data" / "plays"
SOURCE_DIR = ROOT / "data" / "sources"
SCHEMA_PATH = ROOT / "schemas" / "play.schema.json"
GUARD_SCHEMA_PATH = ROOT / "schemas" / "guard.schema.json"
GUARD_DATA_PATH = ROOT / "data" / "guards" / "longsword-named-v0.1.yaml"


def load_json_yaml(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def type_matches(value: Any, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }[expected]


def validate_schema(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    expected = schema.get("type")
    if expected:
        choices = expected if isinstance(expected, list) else [expected]
        if not any(type_matches(value, choice) for choice in choices):
            return [f"{path}: expected type {choices}, found {type(value).__name__}"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} is not in enum {schema['enum']!r}")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: string shorter than {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: does not match {schema['pattern']}")
    if isinstance(value, int) and not isinstance(value, bool) and "minimum" in schema and value < schema["minimum"]:
        errors.append(f"{path}: value is below minimum {schema['minimum']}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: fewer than {schema['minItems']} items")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True) for item in value]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{path}: items are not unique")
        if "items" in schema:
            for index, item in enumerate(value):
                errors.extend(validate_schema(item, schema["items"], f"{path}[{index}]"))
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(f"{path}: unexpected property {key!r}")
        for key, child_schema in properties.items():
            if key in value:
                errors.extend(validate_schema(value[key], child_schema, f"{path}.{key}"))
    return errors


def validate_repository() -> tuple[list[dict[str, Any]], list[str], list[str]]:
    schema = load_json_yaml(SCHEMA_PATH)
    plays = []
    errors: list[str] = []
    warnings: list[str] = []
    source_ids = {path.stem for path in SOURCE_DIR.glob("*.yaml")}
    tag_ids = {item["id"] for item in load_json_yaml(ROOT / "data" / "tags.yaml")["tags"]}
    seen_ids: set[str] = set()
    for path in sorted(PLAY_DIR.glob("*.yaml")):
        try:
            play = load_json_yaml(path)
        except Exception as exc:
            errors.append(f"{path.name}: cannot parse JSON-compatible YAML: {exc}")
            continue
        plays.append(play)
        errors.extend(f"{path.name}: {message}" for message in validate_schema(play, schema))
        if play.get("id") != path.stem:
            errors.append(f"{path.name}: id does not match filename")
        if play.get("id") in seen_ids:
            errors.append(f"{path.name}: duplicate stable id {play.get('id')}")
        seen_ids.add(play.get("id"))
        historical = play.get("historical_identity", {})
        implementation = play.get("game_implementation", {})
        for citation in historical.get("source_citations", []):
            if citation.get("source_id") not in source_ids:
                errors.append(f"{path.name}: unknown source id {citation.get('source_id')}")
        for tag in implementation.get("tactical_tags", []):
            if tag not in tag_ids:
                errors.append(f"{path.name}: unknown tactical tag {tag}")
        for relation_field in ("suspected_duplicates", "related_plays"):
            for related in implementation.get(relation_field, []):
                if not (PLAY_DIR / f"{related}.yaml").exists():
                    errors.append(f"{path.name}: unknown related Play {related}")
        if implementation.get("provisional_tier") == "Intermediate":
            warnings.append(f"{play['id']}: packet longlist tier 'Intermediate' does not match Section 6.5's Trained/Expert tier names")
    if len(plays) != 114:
        errors.append(f"Expected 114 Play records, found {len(plays)}")
    expected_totals = {
        ("Wrestling", "German"): 8, ("Wrestling", "Italian"): 8,
        ("Dagger", "German"): 8, ("Dagger", "Italian"): 8,
        ("Sword & Buckler", "German"): 8, ("Sword in One Hand", "German"): 8,
        ("Sword in One Hand", "Italian"): 1, ("Axe & Mace", "German"): 8,
        ("Axe & Mace", "Italian"): 8, ("Longsword", "German"): 12,
        ("Longsword", "Italian"): 13, ("Spear & Staff", "Italian"): 8,
        ("Polearms / Poleaxe & Halberd", "German"): 8,
        ("Polearms / Poleaxe & Halberd", "Italian"): 8,
    }
    actual = Counter((play["historical_identity"]["curriculum"], play["historical_identity"]["tradition"]) for play in plays)
    if actual != Counter(expected_totals):
        errors.append(f"Curriculum/tradition totals differ from packet: expected {expected_totals}, found {dict(actual)}")
    if GUARD_SCHEMA_PATH.exists() or GUARD_DATA_PATH.exists():
        if not GUARD_SCHEMA_PATH.exists() or not GUARD_DATA_PATH.exists():
            errors.append("Named-guard schema and data must either both exist or both be absent")
        else:
            try:
                guard_schema = load_json_yaml(GUARD_SCHEMA_PATH)
                guard_data = load_json_yaml(GUARD_DATA_PATH)
                errors.extend(
                    f"{GUARD_DATA_PATH.name}: {message}"
                    for message in validate_schema(guard_data, guard_schema)
                )
                guard_ids = [guard.get("id") for guard in guard_data.get("guards", [])]
                if len(guard_ids) != len(set(guard_ids)):
                    errors.append(f"{GUARD_DATA_PATH.name}: duplicate guard id")
                traditions = Counter(guard.get("tradition") for guard in guard_data.get("guards", []))
                if traditions != Counter({"German": 4, "Italian": 4}):
                    errors.append(f"{GUARD_DATA_PATH.name}: bounded roster must contain four German and four Italian guards")
            except Exception as exc:
                errors.append(f"{GUARD_DATA_PATH.name}: cannot validate named guards: {exc}")
    return plays, errors, warnings


def missing_fields(play: dict[str, Any]) -> list[str]:
    historical = play["historical_identity"]
    implementation = play["game_implementation"]
    missing = []
    if historical["historical_confidence"] is None:
        missing.append("historical_identity.historical_confidence")
    if not any(c["citation_status"] == "exact-historical-location" for c in historical["source_citations"]):
        missing.append("historical_identity.source_citations.exact_historical_location")
    for field in ("character_sheet_test_skill", "secondary_skill_prerequisites", "weapon_requirements", "off_hand_requirement"):
        if implementation[field] is None:
            missing.append(f"game_implementation.{field}")
    if implementation["timing"]["category"] is None:
        missing.append("game_implementation.timing.category")
    for field, value in implementation["mechanics"].items():
        if value is None:
            missing.append(f"game_implementation.mechanics.{field}")
    return missing


def write_reports(plays: list[dict[str, Any]], errors: list[str], warnings: list[str]) -> None:
    report_dir = ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    by_curriculum = Counter(play["historical_identity"]["curriculum"] for play in plays)
    by_tradition = Counter(play["historical_identity"]["tradition"] for play in plays)
    missing_counter = Counter(field for play in plays for field in missing_fields(play))
    lines = [
        "# Validation summary", "",
        "Generated by `python scripts/validate_repository.py --write-reports`.", "",
        f"- Play files: **{len(plays)}** (expected 114)",
        f"- Validation errors: **{len(errors)}**",
        f"- Preserved design warnings: **{len(warnings)}**",
        f"- Records needing item-level source audit: **{sum(p['historical_identity']['source_status'] == 'needs-item-level-audit' for p in plays)}**",
        f"- Records with exact historical locations: **{sum(any(c['citation_status'] == 'exact-historical-location' for c in p['historical_identity']['source_citations']) for p in plays)}**",
        f"- Records with implemented mechanics: **{sum(p['game_implementation']['mechanics_status'] != 'unimplemented' for p in plays)}**",
        "", "## Counts by tradition", "",
    ]
    lines.extend(f"- {name}: {count}" for name, count in sorted(by_tradition.items()))
    lines.extend(["", "## Counts by curriculum", ""])
    lines.extend(f"- {name}: {count}" for name, count in sorted(by_curriculum.items()))
    lines.extend(["", "## Unsupported or unaudited fields", ""])
    lines.extend(f"- `{field}`: {count} records" for field, count in sorted(missing_counter.items()))
    lines.extend(["", "## Preserved warnings", ""])
    lines.extend(f"- {warning}" for warning in warnings)
    if not warnings:
        lines.append("- None")
    lines.extend(["", "## Errors", ""])
    lines.extend(f"- {error}" for error in errors)
    if not errors:
        lines.append("- None")
    (report_dir / "validation-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["play_id", "name", "missing_or_unaudited_field"])
    for play in plays:
        for field in missing_fields(play):
            writer.writerow([play["id"], play["name"], field])
    (report_dir / "missing-fields.csv").write_text(buffer.getvalue(), encoding="utf-8")

    duplicates: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for play in plays:
        group = tuple(sorted([play["id"], *play["game_implementation"]["suspected_duplicates"]]))
        if len(group) > 1:
            duplicates[group].append(play)
    dup_lines = ["# Suspected duplicate candidates", "", "These groups are based only on identical normalized names. They are review leads, not merge decisions.", ""]
    for group in sorted(duplicates):
        dup_lines.append("- " + ", ".join(f"`{item}`" for item in group))
    if not duplicates:
        dup_lines.append("- None")
    (report_dir / "suspected-duplicates.md").write_text("\n".join(dup_lines) + "\n", encoding="utf-8")

    source_lines = [
        "# Source audit status", "",
        "The packet requires all 114 candidates to receive item-level source audit. Group-level source notes are preserved in each record but do not substitute for folio, section, plate, edition, or translator data.", "",
        f"- Needs item-level audit: {sum(p['historical_identity']['source_status'] == 'needs-item-level-audit' for p in plays)}",
        f"- Historical confidence still null: {sum(p['historical_identity']['historical_confidence'] is None for p in plays)}",
        f"- Exact historical locator present: {sum(any(c['citation_status'] == 'exact-historical-location' for c in p['historical_identity']['source_citations']) for p in plays)}",
        "", "No confidence grade or exact historical locator was inferred from curriculum-level notes.",
    ]
    (report_dir / "source-audit.md").write_text("\n".join(source_lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-reports", action="store_true")
    args = parser.parse_args()
    plays, errors, warnings = validate_repository()
    if args.write_reports:
        write_reports(plays, errors, warnings)
        from generate_audit_reports import generate_all
        generate_all(plays)
    print(f"Validated {len(plays)} Play records: {len(errors)} error(s), {len(warnings)} preserved warning(s).")
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

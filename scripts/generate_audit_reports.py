"""Generate research audits without promoting heuristics into Play mechanics."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def play_label(play: dict) -> str:
    historical = play["historical_identity"]
    return f"{play['name']} — {historical['tradition']} {historical['curriculum']} (`{play['id']}`)"


def package_key(play: dict) -> tuple[str, str]:
    historical = play["historical_identity"]
    return historical["curriculum"], historical["tradition"]


def normalized_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def searchable_text(play: dict) -> str:
    historical = play["historical_identity"]
    implementation = play["game_implementation"]
    return " ".join([
        play["name"],
        historical.get("display_name_in_packet") or "",
        historical.get("packet_source_note") or "",
        implementation["timing"].get("type") or "",
        implementation.get("tactical_lesson") or "",
    ]).lower()


def candidate_text(play: dict) -> str:
    """Item-level text only; excludes curriculum-wide source notes."""
    historical = play["historical_identity"]
    implementation = play["game_implementation"]
    return " ".join([
        play["name"],
        historical.get("display_name_in_packet") or "",
        implementation["timing"].get("type") or "",
        implementation.get("tactical_lesson") or "",
    ]).lower()


def write_source_audit(plays: list[dict]) -> None:
    exact = []
    broad = []
    packet_only = []
    confirmed_reconstructions = []
    ambiguous_marker = []
    reconstruction_risk = []
    for play in plays:
        citations = play["historical_identity"]["source_citations"]
        if any(item["citation_status"] == "exact-historical-location" for item in citations):
            exact.append(play)
        historical_citations = [item for item in citations if item["citation_status"] != "exact-packet-location"]
        if historical_citations and not any(item["citation_status"] == "exact-historical-location" for item in historical_citations):
            broad.append(play)
        if not historical_citations:
            packet_only.append(play)
        if "transparent game-facing synthesis" in searchable_text(play) or play["historical_identity"]["source_status"] == "reconstruction-basis-verified":
            confirmed_reconstructions.append(play)
        if play["historical_identity"]["game_facing_or_reconstruction_marker"]:
            ambiguous_marker.append(play)
        note = (play["historical_identity"].get("packet_source_note") or "").lower()
        if "reconstruction-heavy" in note or "mixed direct and reconstructed" in note:
            reconstruction_risk.append(play)

    source_groups: dict[tuple[str, ...], list[dict]] = defaultdict(list)
    for play in broad:
        refs = tuple(item["source_id"] for item in play["historical_identity"]["source_citations"] if item["citation_status"] == "source-family-only")
        source_groups[refs].append(play)
    ambiguous_by_package: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for play in ambiguous_marker:
        ambiguous_by_package[package_key(play)].append(play)
    risk_by_package: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for play in reconstruction_risk:
        risk_by_package[package_key(play)].append(play)

    lines = [
        "# Source audit", "",
        "This audit distinguishes packet locations from historical source locations. A Section 7 row is an exact location in the governing packet, but it is not a folio, plate, chapter, or page in a historical witness.", "",
        "## Result", "",
        f"- Exact historical locators: **{len(exact)} / {len(plays)}**",
        f"- Broad historical source-family references only: **{len(broad)} / {len(plays)}**",
        f"- Packet-only, with no historical source-family reference: **{len(packet_only)} / {len(plays)}**",
        f"- Confirmed transparent reconstructions/syntheses: **{len(confirmed_reconstructions)}**",
        f"- Ambiguous asterisk marker (historical but unnamed/inconsistently named, or reconstruction): **{len(ambiguous_marker)}**",
        f"- Historical confidence still unset: **{sum(p['historical_identity']['historical_confidence'] is None for p in plays)} / {len(plays)}**",
        "",
        "All 114 records therefore still need item-level evidence work. None currently supports an exact-locator or confidence-grade claim.", "",
        "## Exact historical locators", "",
    ]
    if exact:
        lines.extend(f"- {play_label(play)}" for play in exact)
    else:
        lines.append("- None. Every historical citation has a null location and `source-family-only` status.")
    lines.extend(["", "## Confirmed transparent reconstruction or synthesis", ""])
    if confirmed_reconstructions:
        for play in confirmed_reconstructions:
            lines.extend([f"### {play_label(play)}", "", play["game_implementation"]["tactical_lesson"], ""])
    else:
        lines.append("- None explicitly confirmed at item level.")
    lines.extend([
        "## Asterisk-marked candidates requiring adjudication", "",
        "The packet defines `*` disjunctively: it can mean a game-facing name for a historical but unnamed/inconsistently named action, or a transparent reconstruction. The marker alone cannot classify a Play as reconstruction.", "",
    ])
    for (curriculum, tradition), group in sorted(ambiguous_by_package.items()):
        names = ", ".join(play["name"] for play in group)
        lines.append(f"- **{tradition} — {curriculum} ({len(group)}):** {names}")
    lines.extend(["", "## Package-level reconstruction risk", "", "These packet notes describe packages as mixed or reconstruction-heavy. They do not identify which individual rows are reconstructed, so no individual status was changed.", ""])
    for (curriculum, tradition), group in sorted(risk_by_package.items()):
        note = group[0]["historical_identity"]["packet_source_note"]
        lines.extend([f"### {tradition} — {curriculum}", "", note, "", "Candidates: " + ", ".join(play["name"] for play in group), ""])
    lines.extend(["## Broad source-family references", "", "Every candidate has at least one broad source-family reference. The following groups show exactly which candidates rely on each recorded source set.", ""])
    for source_ids, group in sorted(source_groups.items(), key=lambda item: (item[0], [p["id"] for p in item[1]])):
        lines.extend(["### " + ", ".join(f"`{source_id}`" for source_id in source_ids), ""])
        lines.extend(f"- {play_label(play)}" for play in sorted(group, key=lambda item: item["id"]))
        lines.append("")
    lines.extend(["## Still needs evidence", "", "Every Play needs all of the following before source audit can pass:", "", "- exact historical locator (folio, plate, section, chapter, or page);", "- edition and translator where applicable;", "- item-level inclusion basis;", "- historical confidence grade;", "- explicit reconstruction determination for asterisk-marked candidates.", ""])
    REPORTS.joinpath("source-audit.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def chassis_rules() -> list[tuple[str, str, Callable[[dict], bool]]]:
    def text_has(pattern: str) -> Callable[[dict], bool]:
        regex = re.compile(pattern, re.I)
        return lambda play: bool(regex.search(candidate_text(play)))

    explicit_single_time = {
        "zornhau ort", "entrusthau", "beat and strike", "absetzen", "scambiar di punta",
        "rompere di punta", "colpo di villano", "exchange of thrusts", "break the thrust",
        "cross step counterthrust", "beat down and thrust", "counter thrust to the heart",
        "true cross", "boars tooth rising counter", "long tail beat down",
    }
    return [
        ("beats-and-displacements", "Beats, break-downs, set-asides, and weapon-line displacements.", text_has(r"\bbeat\b|beat-down|beat down|break the thrust|set aside|drive the opposing|displace")),
        ("changes-through-and-deceptions", "Changes-through, false actions, feints, and change-strike branches.", text_has(r"durchwechseln|\bdeception\b|\bfeint\b|false point|false blow|change-strike")),
        ("single-time-counters", "Candidate defence-and-offence in one tempo. This is a research grouping, not an action-preservation rule.", lambda play: normalized_name(play["name"]) in explicit_single_time or (play["historical_identity"]["anti_number_marker"] and bool(re.search(r"defence/attack|counter-(?:attack|cut|thrust)|counter-attack", (play["game_implementation"]["timing"].get("type") or "").lower())))),
        ("hooks-and-wrenches", "Hooking, catching, tearing, yanking, and wrenching actions.", text_has(r"\bhook|wrench|yank|axe beard|hammer neck|catch the hostile|catch shaft")),
        ("weapon-takings-and-disarms", "Taking or stripping a dagger, sword, Messer, polearm, or other weapon.", text_has(r"\bdisarm\b|weapon taking|sword taking|messer taking|polearm taking|take dagger|dagger take|take it|strip it")),
        ("throws-and-takedowns", "Human throws and takedowns; ranged weapon casts are excluded unless the lesson also throws the opponent.", lambda play: bool(re.search(r"throw|takedown", (play["game_implementation"]["timing"].get("type") or ""), re.I)) or bool(re.search(r"throw the (?:attacker|opponent|enemy)|cast (?:an |the )?opponent|cast the opponent", searchable_text(play), re.I))),
        ("bind-and-winding-branches", "Binds, windings, Crown/Corona crossings, and named bind branches.", text_has(r"\bbind\b|\bwinden\b|duplieren|mutieren|strong key|middle bind|upper bind|lower bind|crown|corona")),
        ("close-play-and-grapples", "Grapples, locks, breaks, close-play entries, and body-control finishes.", text_has(r"\bgrapple|close play|\block\b|arm break|dislocation|takedown|throw|body control|neck grapple")),
        ("guards-covers-and-shields", "Specialized guards, covers, shields, and public posture/state candidates.", text_has(r"specialized guard|guard/play|\bguard\b|\bcover\b|\bshielding\b|upper shield|lower shield|remedy cover")),
        ("pursuit-recovery-and-rush", "Pursuit, renewed attack, clearing, recovery, or rush candidates.", text_has(r"\bpursuit\b|\brecovery\b|\bclearing\b|\brush\b|nachreisen|follow the cast|withdraw and re-thrust|renew the point")),
    ]


def write_duplicate_chassis_audit(plays: list[dict]) -> None:
    by_name: dict[str, list[dict]] = defaultdict(list)
    for play in plays:
        by_name[normalized_name(play["name"])].append(play)
    exact_duplicates = [group for group in by_name.values() if len(group) > 1]
    memberships: dict[str, list[dict]] = {}
    descriptions: dict[str, str] = {}
    assigned: set[str] = set()
    for chassis_id, description, predicate in chassis_rules():
        group = [play for play in plays if predicate(play)]
        memberships[chassis_id] = group
        descriptions[chassis_id] = description
        assigned.update(play["id"] for play in group)
    unmatched = [play for play in plays if play["id"] not in assigned]
    lines = [
        "# Duplicate and provisional chassis audit", "",
        "These are lexical/tactical research clusters derived from packet names, provisional types, and tactical lessons. They overlap by design and do not establish final mechanics, costs, prerequisites, or merge decisions.", "",
        "## Summary", "",
        f"- Exact normalized-name duplicate groups: **{len(exact_duplicates)}**",
        f"- Provisional chassis clusters: **{len(memberships)}**",
        f"- Candidates appearing in at least one cluster: **{len(assigned)} / {len(plays)}**",
        f"- Candidates unmatched by these initial heuristics: **{len(unmatched)}**",
        "", "## Exact-name duplicate groups", "",
    ]
    if exact_duplicates:
        for group in sorted(exact_duplicates, key=lambda items: normalized_name(items[0]["name"])):
            lines.extend([f"### {group[0]['name']}", ""])
            lines.extend(f"- {play_label(play)}" for play in sorted(group, key=lambda item: item["id"]))
            lines.append("")
    else:
        lines.append("- None")
    lines.extend(["## Provisional chassis clusters", ""])
    for chassis_id, _, _ in chassis_rules():
        group = memberships[chassis_id]
        lines.extend([f"### {chassis_id} ({len(group)})", "", descriptions[chassis_id], ""])
        lines.extend(f"- {play_label(play)} — {play['game_implementation']['timing']['type']}" for play in sorted(group, key=lambda item: item["id"]))
        if not group:
            lines.append("- None")
        lines.append("")
    lines.extend(["## Unmatched by initial chassis heuristics", "", "These are not necessarily unique chassis; they need manual classification.", ""])
    lines.extend(f"- {play_label(play)} — {play['game_implementation']['timing']['type']}" for play in sorted(unmatched, key=lambda item: item["id"]))
    REPORTS.joinpath("duplicate-chassis-audit.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


COVERAGE_LABELS = {
    "initiation": "Initiation",
    "defence": "Defence",
    "deception": "Deception",
    "weapon-control": "Weapon control",
    "close-play": "Close play",
    "pursuit-recovery": "Pursuit / recovery",
    "anti-number": "Anti-number / engagement control",
}


def coverage_categories(play: dict) -> set[str]:
    kind = (play["game_implementation"]["timing"].get("type") or "").lower()
    text = candidate_text(play)
    curriculum = play["historical_identity"]["curriculum"]
    result: set[str] = set()
    if re.search(r"entry|(?<!counter-)attack|precision attack|power attack|ranged gambit|combination|master strike", kind) and not re.search(r"defence/attack|counter", kind):
        result.add("initiation")
    if re.search(r"defence|counter|guard/play", kind) or re.search(r"\bcover\b|upper shield|lower shield|remedy", text):
        result.add("defence")
    if re.search(r"deception|feint|gambit", kind) or re.search(r"durchwechseln|false point|false blow|change-strike", text):
        result.add("deception")
    if curriculum != "Wrestling" and (re.search(r"weapon control|disarm|\bbeat\b|bind", kind) or re.search(r"weapon taking|sword taking|messer taking|polearm taking|take dagger|dagger take|hook the blade|shield separation", text)):
        result.add("weapon-control")
    if re.search(r"grapple|close play|throw|lock|takedown|break", kind) or re.search(r"close play|body control|dislocation|neck grapple", text):
        result.add("close-play")
    if curriculum in {"Wrestling", "Dagger"} and re.search(r"\bbind\b|\bcontrol\b", kind):
        result.add("close-play")
    if re.search(r"pursuit|recovery|rush|clearing", kind) or re.search(r"nachreisen|follow the cast|withdraw and re-thrust|renew the point", text):
        result.add("pursuit-recovery")
    tags = set(play["game_implementation"]["tactical_tags"])
    if tags.intersection({"anti-number-candidate", "against-many", "engagement-control", "clearing", "recovery", "line-denial", "tempo-compression"}):
        result.add("anti-number")
    return result


def write_curriculum_coverage_audit(plays: list[dict]) -> None:
    curricula = ["Wrestling", "Dagger", "Sword & Buckler", "Sword in One Hand", "Axe & Mace", "Longsword", "Spear & Staff", "Polearms / Poleaxe & Halberd"]
    traditions = ["German", "Italian"]
    by_package: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for play in plays:
        by_package[package_key(play)].append(play)
    lines = [
        "# Curriculum coverage audit", "",
        "Coverage is inferred from candidate names, provisional types, tactical lessons, and existing anti-number tags. A count means the package contains candidate evidence for that function; it does not mean the function is mechanically implemented or historically cleared.", "",
        "`0` means no candidate was found by the stated heuristic. Empty restoration packages are included.", "",
        "| Tradition / curriculum | Plays | Initiation | Defence | Deception | Weapon control | Close play | Pursuit / recovery | Anti-number / engagement |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    coverage_by_package: dict[tuple[str, str], dict[str, list[dict]]] = {}
    for curriculum in curricula:
        for tradition in traditions:
            group = by_package[(curriculum, tradition)]
            evidence = {category: [play for play in group if category in coverage_categories(play)] for category in COVERAGE_LABELS}
            coverage_by_package[(curriculum, tradition)] = evidence
            lines.append("| " + " | ".join([
                f"{tradition} — {curriculum}", str(len(group)),
                *(str(len(evidence[category])) for category in COVERAGE_LABELS),
            ]) + " |")
    lines.extend(["", "## Package detail", ""])
    for curriculum in curricula:
        for tradition in traditions:
            group = by_package[(curriculum, tradition)]
            evidence = coverage_by_package[(curriculum, tradition)]
            missing = [COVERAGE_LABELS[category] for category, items in evidence.items() if not items]
            lines.extend([f"### {tradition} — {curriculum} ({len(group)} Plays)", ""])
            if not group:
                lines.extend(["Status: empty restoration package in v0.4; all seven coverage functions are absent.", ""])
                continue
            lines.append("Missing candidate evidence: " + (", ".join(missing) if missing else "none by these heuristics") + ".")
            lines.append("")
            for category, label in COVERAGE_LABELS.items():
                items = evidence[category]
                lines.append(f"- **{label} ({len(items)}):** " + (", ".join(play["name"] for play in items) if items else "none"))
            lines.append("")
    REPORTS.joinpath("curriculum-coverage-audit.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


EQUIPMENT_CUES = [
    ("free/two-hand wording", r"free hand|two hands|both hands"),
    ("buckler", r"buckler"),
    ("shield", r"shield"),
    ("dagger", r"dagger"),
    ("hooking affordance", r"\bhook|axe beard|hammer neck"),
    ("armour-gap affordance", r"armour|armor|visor|armpit"),
    ("long-weapon/reach affordance", r"spear|polearm|poleaxe|long weapon|shaft"),
    ("Messer-specific affordance", r"messer|nagel|single edge|single-edge"),
]


def equipment_cues(play: dict) -> list[str]:
    text = candidate_text(play)
    return [label for label, pattern in EQUIPMENT_CUES if re.search(pattern, text, re.I)]


def write_skill_equipment_audit(plays: list[dict]) -> None:
    fields = ["character_sheet_test_skill", "secondary_skill_prerequisites", "weapon_requirements", "off_hand_requirement"]
    specified = {field: sum(play["game_implementation"][field] is not None for play in plays) for field in fields}
    by_package: dict[tuple[str, str], list[dict]] = defaultdict(list)
    cue_groups: dict[str, list[dict]] = defaultdict(list)
    for play in plays:
        by_package[package_key(play)].append(play)
        for cue in equipment_cues(play):
            cue_groups[cue].append(play)
    lines = [
        "# Skill and equipment audit", "",
        "## Verdict", "",
        "The repository does **not** yet confirm the requested implementation data for any Play. The fields exist in every record, but they are null because v0.4 did not specify them item by item.", "",
        f"- Character-sheet test skill specified: **{specified['character_sheet_test_skill']} / {len(plays)}**",
        f"- Secondary skill prerequisites specified: **{specified['secondary_skill_prerequisites']} / {len(plays)}**",
        f"- Weapon requirements specified: **{specified['weapon_requirements']} / {len(plays)}**",
        f"- Off-hand requirement specified: **{specified['off_hand_requirement']} / {len(plays)}**",
        "",
        "A curriculum heading, Play name, or tactical lesson is not accepted as a substitute for these fields. In particular, Sword & Buckler may roll One-Handed Sword or Shield; mixed-implement Plays may require secondary skills; and off-hand state is an adopted first-class gate.", "",
        "## Failure count by tradition/loadout", "",
        "| Tradition / curriculum | Plays | Missing test skill | Missing secondary skills | Missing weapon requirements | Missing off-hand requirement |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for (curriculum, tradition), group in sorted(by_package.items()):
        counts = [sum(play["game_implementation"][field] is None for play in group) for field in fields]
        lines.append(f"| {tradition} — {curriculum} | {len(group)} | " + " | ".join(map(str, counts)) + " |")
    lines.extend(["", "## Textual equipment cues requiring structured audit", "", "These are keyword cues only. They identify likely research targets and do not populate requirements.", ""])
    for label, _ in EQUIPMENT_CUES:
        group = cue_groups[label]
        lines.extend([f"### {label} ({len(group)})", ""])
        lines.extend(f"- {play_label(play)}" for play in sorted(group, key=lambda item: item["id"]))
        if not group:
            lines.append("- None")
        lines.append("")
    lines.extend(["## Every-Play result", "", "`MISSING` means the structured field is null. Equipment cues are not requirements.", "", "| Play | Test skill | Secondary skills | Weapon requirements | Off-hand | Textual cues |", "| --- | --- | --- | --- | --- | --- |"])
    for play in sorted(plays, key=lambda item: item["id"]):
        implementation = play["game_implementation"]
        values = []
        for field in fields:
            value = implementation[field]
            if value is None:
                values.append("**MISSING**")
            elif isinstance(value, list):
                values.append(", ".join(map(str, value)) or "specified empty")
            else:
                values.append(str(value))
        cues = ", ".join(equipment_cues(play)) or "none detected"
        lines.append(f"| `{play['id']}` — {play['name']} | " + " | ".join([*values, cues]) + " |")
    REPORTS.joinpath("skill-equipment-audit.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def generate_all(plays: list[dict]) -> None:
    REPORTS.mkdir(exist_ok=True)
    write_source_audit(plays)
    write_duplicate_chassis_audit(plays)
    write_curriculum_coverage_audit(plays)
    write_skill_equipment_audit(plays)


def main() -> None:
    plays = [json.loads(path.read_text(encoding="utf-8")) for path in sorted((ROOT / "data" / "plays").glob("*.yaml"))]
    generate_all(plays)
    print(f"Generated four audit reports for {len(plays)} Play records.")


if __name__ == "__main__":
    main()

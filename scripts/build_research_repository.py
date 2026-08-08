"""Rebuild the v0.4 Markdown transcription and Play research records.

The Word packet is the input authority. Generated YAML files deliberately use
the JSON-compatible subset of YAML so validation needs only Python's standard
library.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "Atra_Melee_Design_Packet_v0.4.docx"


SOURCE_RECORDS = {
    "atra-melee-design-packet-v0-4": {
        "name": "Atra Melee Design Packet v0.4",
        "kind": "governing-design-document",
        "citation": "Atra RPG, Atra Melee Design Packet, Version 0.4, updated 2026-08-07.",
        "date": "2026-08-07",
        "exact_location": None,
        "notes": "Canonical for this repository. Later decisions supersede earlier experiments only where the record supports a decision.",
    },
    "design-record": {
        "name": "Atra melee design record",
        "kind": "project-record",
        "citation": "Shared 'HEMA exchanges per 6 seconds' conversation, packets v0.1-v0.3, and Project clarifications through 2026-08-07.",
        "date": None,
        "exact_location": None,
        "notes": "Primary chronological decision record described by the packet; not present as a separate workspace artifact.",
    },
    "codex-martialis-v8-2": {
        "name": "Codex Martialis Core Rulebook 2024 Edition",
        "kind": "comparison-only",
        "citation": "Jean Chandler, Codex Martialis Core Rulebook 2024 Edition, version 8.2, 117 pages.",
        "date": "2024",
        "exact_location": None,
        "notes": "Comparison benchmark only; not Atra canon.",
    },
    "fiore-dei-liberi": {"name": "Fiore dei Liberi", "kind": "historical-source", "citation": "Fiore dei Liberi, works including Abrazare, dagger, sword, and poleaxe material (c.1400-09).", "date": "c.1400-09", "exact_location": None, "notes": "Earlier continuing Italian tradition; item-level folio/section audit remains required."},
    "philippo-di-vadi": {"name": "Philippo di Vadi", "kind": "historical-source", "citation": "Philippo di Vadi, De Arte Gladiatoria Dimicandi (c.1482-87).", "date": "c.1482-87", "exact_location": None, "notes": "Core direct-horizon Italian witness; item-level folio/section audit remains required."},
    "pietro-monte": {"name": "Pietro Monte", "kind": "historical-source", "citation": "Pietro Monte, late-fifteenth-century composition; expanded Latin Collectanea printed 1509.", "date": "late 1400s / 1509", "exact_location": None, "notes": "Treated by the packet as a fifteenth-century martial witness despite the printing date."},
    "filippo-dardi": {"name": "Filippo Dardi", "kind": "tradition-lineage", "citation": "Filippo Dardi (licensed fencing master in Bologna in 1412).", "date": "1412 lineage evidence", "exact_location": None, "notes": "Lineage evidence for Bolognese continuity; not an item-level Play locator."},
    "anonimo-bolognese": {"name": "Anonimo Bolognese", "kind": "historical-source", "citation": "Anonimo Bolognese.", "date": None, "exact_location": None, "notes": "Eligible Bolognese continuity witness; item-level continuity judgment required."},
    "antonio-manciolino": {"name": "Antonio Manciolino", "kind": "historical-source", "citation": "Antonio Manciolino, Opera Nova (1531; packet notes evidence of earlier publication activity).", "date": "1531", "exact_location": None, "notes": "Eligible continuity witness; source-unique sequences are not automatically backdated."},
    "achille-marozzo": {"name": "Achille Marozzo", "kind": "historical-source", "citation": "Achille Marozzo, Opera Nova (1536).", "date": "1536", "exact_location": None, "notes": "Eligible continuity witness; source-unique sequences are not automatically backdated."},
    "pseudo-peter-von-danzig": {"name": "Pseudo-Peter von Danzig", "kind": "historical-source", "citation": "Pseudo-Peter von Danzig.", "date": None, "exact_location": None, "notes": "German direct/earlier source group; item-level locator required."},
    "lew": {"name": "Lew", "kind": "historical-source", "citation": "Lew.", "date": None, "exact_location": None, "notes": "German direct/earlier source group; item-level locator required."},
    "paulus-kal": {"name": "Paulus Kal", "kind": "historical-source", "citation": "Paulus Kal.", "date": None, "exact_location": None, "notes": "German direct/earlier source group; item-level locator required."},
    "hans-talhoffer": {"name": "Hans Talhoffer", "kind": "historical-source", "citation": "Hans Talhoffer.", "date": None, "exact_location": None, "notes": "German direct/earlier source group; item-level locator required."},
    "johannes-leckuechner": {"name": "Johannes Leckuechner", "kind": "historical-source", "citation": "Johannes Leckuechner (1478/1482).", "date": "1478/1482", "exact_location": None, "notes": "Core direct-horizon German witness; item-level locator required."},
    "peter-falkner": {"name": "Peter Falkner", "kind": "historical-source", "citation": "Peter Falkner (c.1495).", "date": "c.1495", "exact_location": None, "notes": "Core direct-horizon German witness; item-level locator required."},
    "ott-jud": {"name": "Ott Jud", "kind": "historical-source", "citation": "Ott Jud.", "date": None, "exact_location": None, "notes": "Earlier continuing German wrestling tradition; item-level locator required."},
    "andre-lignitzer": {"name": "Andre Lignitzer", "kind": "historical-source", "citation": "Andre Lignitzer.", "date": None, "exact_location": None, "notes": "German direct/earlier source group; item-level locator required."},
    "andre-paurenfeyndt": {"name": "Andre Paurenfeyndt", "kind": "historical-source", "citation": "Andre Paurenfeyndt, Ergruendung Ritterlicher Kunst der Fechterey (1516).", "date": "1516", "exact_location": None, "notes": "Eligible German continuity witness; item-level locator required."},
    "fabian-von-auerswald": {"name": "Fabian von Auerswald", "kind": "historical-source", "citation": "Fabian von Auerswald, Ringer Kunst (1539; author born 1462).", "date": "1539", "exact_location": None, "notes": "Eligible wrestling continuity witness; item-level locator required."},
    "paulus-hector-mair": {"name": "Paulus Hector Mair", "kind": "later-preservation-witness", "citation": "Paulus Hector Mair, mid-sixteenth-century compilations.", "date": "mid-sixteenth century", "exact_location": None, "notes": "May preserve older material; source-unique material is not automatically backdated."},
    "ms-i-33": {"name": "MS I.33", "kind": "archaic-caution", "citation": "MS I.33 (c.1320s).", "date": "c.1320s", "exact_location": None, "notes": "Optional archaizing source, not the normal late-fifteenth-century default without corroboration."},
    "camillo-agrippa": {"name": "Camillo Agrippa", "kind": "outside-core-boundary", "citation": "Camillo Agrippa, Trattato di Scientia d'Arme (1553).", "date": "1553", "exact_location": None, "notes": "Presumptive innovation boundary; not core unless independently earlier-attested or explicitly imported."},
    "joachim-meyer": {"name": "Joachim Meyer", "kind": "outside-core-boundary", "citation": "Joachim Meyer, 1561 manuscript and 1570 print.", "date": "1561/1570", "exact_location": None, "notes": "Comparative use only unless independently earlier-attested; not sole authority for source-unique core Plays."},
    "giovanni-dallagocchie": {"name": "Giovanni dall'Agocchie", "kind": "outside-core-boundary", "citation": "Giovanni dall'Agocchie (1572).", "date": "1572", "exact_location": None, "notes": "Later material outside the common core unless independently earlier-attested or explicitly imported."},
    "nicoletto-giganti": {"name": "Nicoletto Giganti", "kind": "outside-core-boundary", "citation": "Nicoletto Giganti, later mature rapier writing.", "date": None, "exact_location": None, "notes": "Later mature rapier material outside the common core."},
    "ridolfo-capo-ferro": {"name": "Ridolfo Capo Ferro", "kind": "outside-core-boundary", "citation": "Ridolfo Capo Ferro, later mature rapier writing.", "date": None, "exact_location": None, "notes": "Later mature rapier material outside the common core."},
    "pseudo-hans-doebringer": {"name": "Pseudo-Hans Doebringer", "kind": "historical-direction", "citation": "Pseudo-Hans Doebringer / early Liechtenauer tradition, counsel on overwhelming numbers.", "date": None, "exact_location": None, "notes": "Design evidence that numbers remain dangerous; not by itself a source for a specific Play."},
}


SOURCE_KEYWORDS = [
    ("Fiore", "fiore-dei-liberi"), ("Vadi", "philippo-di-vadi"),
    ("Monte", "pietro-monte"), ("Anonimo Bolognese", "anonimo-bolognese"),
    ("Dardi", "filippo-dardi"),
    ("Manciolino", "antonio-manciolino"), ("Marozzo", "achille-marozzo"),
    ("Pseudo-Danzig", "pseudo-peter-von-danzig"), ("Lew", "lew"),
    ("Kal", "paulus-kal"), ("Talhoffer", "hans-talhoffer"),
    ("Leck", "johannes-leckuechner"), ("Falkner", "peter-falkner"),
    ("Ott Jud", "ott-jud"), ("Lignitzer", "andre-lignitzer"),
    ("Paurenfeyndt", "andre-paurenfeyndt"), ("Auerswald", "fabian-von-auerswald"),
    ("Mair", "paulus-hector-mair"), ("I.33", "ms-i-33"),
    ("Meyer", "joachim-meyer"),
]


def slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower().replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def dump_json_yaml(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def packet_to_markdown(doc: Document) -> str:
    lines = ["<!-- Generated from Atra_Melee_Design_Packet_v0.4.docx; regenerate with scripts/build_research_repository.py. -->", ""]
    list_number = 0
    for index, item in enumerate(doc.iter_inner_content()):
        if isinstance(item, Paragraph):
            text = item.text.strip()
            style = item.style.name if item.style else ""
            if not text:
                if lines and lines[-1] != "":
                    lines.append("")
                continue
            if index == 0:
                lines.extend(["# ATRA RPG", ""])
            elif index == 1:
                lines.extend(["## Atra Melee Design Packet", ""])
            elif index == 2:
                lines.extend([f"**{text}**", ""])
            elif style.startswith("Heading "):
                level = int(style.split()[-1])
                lines.extend(["#" * level + " " + text, ""])
            elif style == "List Bullet":
                lines.append(f"- {text}")
            elif style == "List Number":
                list_number += 1
                lines.append(f"{list_number}. {text}")
            elif style == "Table Citation":
                lines.extend([f"> {text}", ""])
            else:
                list_number = 0
                lines.extend([text, ""])
        elif isinstance(item, Table):
            rows = [[markdown_cell(cell.text) for cell in row.cells] for row in item.rows]
            if not rows:
                continue
            width = max(len(row) for row in rows)
            rows = [row + [""] * (width - len(row)) for row in rows]
            lines.append("| " + " | ".join(rows[0]) + " |")
            lines.append("| " + " | ".join(["---"] * width) + " |")
            for row in rows[1:]:
                lines.append("| " + " | ".join(row) + " |")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def historical_sources(note: str, play_name: str) -> list[str]:
    if play_name == "Sword Against Three":
        return ["fiore-dei-liberi"]
    if play_name == "Cuts Against Many":
        return ["philippo-di-vadi"]
    found = []
    for keyword, source_id in SOURCE_KEYWORDS:
        if keyword.lower() in note.lower() and source_id not in found:
            found.append(source_id)
    return found


def extract_plays(doc: Document) -> list[dict[str, object]]:
    plays: list[dict[str, object]] = []
    in_longlist = False
    curriculum = None
    tradition = None
    source_note = ""
    for item in doc.iter_inner_content():
        if isinstance(item, Paragraph):
            text = item.text.strip()
            style = item.style.name if item.style else ""
            if text == "7. Current Play longlist - 114 research candidates":
                in_longlist = True
                continue
            if text == "8. Balance, progression and pruning targets":
                break
            if not in_longlist:
                continue
            if style == "Heading 2":
                curriculum = text
                tradition = None
                source_note = ""
            elif style == "Heading 3":
                tradition = text
                source_note = ""
            elif tradition and text and style in {"Table Citation", "Normal"}:
                source_note = text
        elif in_longlist and isinstance(item, Table):
            if not curriculum or not tradition or not item.rows:
                continue
            header = [cell.text.strip() for cell in item.rows[0].cells]
            if header[:4] != ["Tier", "Play", "Type", "Tactical lesson"]:
                continue
            for row in item.rows[1:]:
                tier, raw_name, type_raw, lesson = [cell.text.strip() for cell in row.cells[:4]]
                anti_number = "†" in raw_name
                game_facing = "*" in raw_name
                name = raw_name.replace("*", "").replace("†", "").strip()
                record_id = f"play-{slug(tradition)}-{slug(curriculum)}-{slug(name)}"
                tags = ["anti-number-candidate"] if anti_number else []
                if name == "Sword Against Three":
                    tags.extend(["against-many", "engagement-control"])
                elif name == "Cuts Against Many":
                    tags.extend(["against-many", "clearing", "recovery"])
                citations = [{
                    "source_id": "atra-melee-design-packet-v0-4",
                    "location": f"Section 7 > {curriculum} > {tradition} > {raw_name}",
                    "citation_status": "exact-packet-location",
                }]
                for source_id in historical_sources(source_note, name):
                    citations.append({"source_id": source_id, "location": None, "citation_status": "source-family-only"})
                plays.append({
                    "id": record_id,
                    "name": name,
                    "historical_identity": {
                        "tradition": tradition,
                        "curriculum": curriculum,
                        "display_name_in_packet": raw_name,
                        "game_facing_or_reconstruction_marker": game_facing,
                        "anti_number_marker": anti_number,
                        "source_status": "needs-item-level-audit",
                        "source_citations": citations,
                        "historical_confidence": None,
                        "packet_source_note": source_note or None,
                    },
                    "game_implementation": {
                        "character_sheet_test_skill": None,
                        "secondary_skill_prerequisites": None,
                        "weapon_requirements": None,
                        "off_hand_requirement": None,
                        "provisional_tier": tier,
                        "tactical_tags": tags,
                        "timing": {"category": None, "type": type_raw},
                        "tactical_lesson": lesson,
                        "candidate_status": "research-candidate",
                        "suspected_duplicates": [],
                        "related_plays": [],
                        "mechanics_status": "unimplemented",
                        "mechanics": {
                            "learn_requirements": None,
                            "use_conditions": None,
                            "action_relationship": None,
                            "spiritus_cost": None,
                            "test_resolution": None,
                            "defence": None,
                            "success": None,
                            "failure": None,
                            "aftermath": None,
                            "limits": None,
                        },
                    },
                })
    by_name: dict[str, list[str]] = defaultdict(list)
    for play in plays:
        by_name[slug(str(play["name"]))].append(str(play["id"]))
    for play in plays:
        same_name = by_name[slug(str(play["name"]))]
        play["game_implementation"]["suspected_duplicates"] = [item for item in same_name if item != play["id"]]
    return plays


def write_sources() -> None:
    for source_id, body in SOURCE_RECORDS.items():
        dump_json_yaml(ROOT / "data" / "sources" / f"{source_id}.yaml", {"id": source_id, **body})


def write_governing_status_report(doc: Document) -> None:
    """Preserve the Section 2 PROVISIONAL/OPEN/DEFERRED register verbatim."""
    active_section = None
    rows_by_status: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for item in doc.iter_inner_content():
        if isinstance(item, Paragraph):
            text = item.text.strip()
            if text == "2.2 Provisional working baseline":
                active_section = "provisional"
            elif text == "2.4 Open and deferred":
                active_section = "open"
            elif style_name(item) == "Heading 2" and active_section:
                active_section = None
        elif active_section and isinstance(item, Table) and item.rows:
            header = [cell.text.strip() for cell in item.rows[0].cells]
            if header[:4] != ["Status", "Decision", "Canonical reading", "Evidence"]:
                continue
            for row in item.rows[1:]:
                status, decision, reading, evidence = [cell.text.strip() for cell in row.cells[:4]]
                if status in {"PROVISIONAL", "OPEN", "DEFERRED"}:
                    rows_by_status[status].append((decision, reading, evidence))
    lines = [
        "# Governing OPEN, PROVISIONAL, and DEFERRED register", "",
        "Transcribed from Section 2 of Atra Melee Design Packet v0.4. These entries are constraints and unresolved questions; this repository does not decide them.", "",
    ]
    for status in ("OPEN", "PROVISIONAL", "DEFERRED"):
        lines.extend([f"## {status}", ""])
        for decision, reading, evidence in rows_by_status[status]:
            lines.extend([f"### {decision}", "", reading, "", f"Evidence: {evidence}", ""])
    path = ROOT / "reports" / "governing-open-provisional.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def style_name(paragraph: Paragraph) -> str:
    return paragraph.style.name if paragraph.style else ""


def main() -> None:
    doc = Document(PACKET)
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "melee-design-packet-v0.4.md").write_text(packet_to_markdown(doc), encoding="utf-8")
    plays = extract_plays(doc)
    if len(plays) != 114:
        raise RuntimeError(f"Expected 114 Play candidates, extracted {len(plays)}")
    play_dir = ROOT / "data" / "plays"
    play_dir.mkdir(parents=True, exist_ok=True)
    for old in play_dir.glob("*.yaml"):
        old.unlink()
    for play in plays:
        dump_json_yaml(play_dir / f"{play['id']}.yaml", play)
    write_sources()
    write_governing_status_report(doc)
    # Reapply the separately reviewable v0.4 evidence proposal after regeneration.
    # This does not promote any proposed field into the canonical record fields.
    from apply_longsword_evidence_audit import apply_audit
    apply_audit(write_report=True)
    from apply_selected_longsword_corrections import apply_selected_corrections
    apply_selected_corrections()
    print(f"Generated Markdown packet, {len(plays)} Play records, and {len(SOURCE_RECORDS)} source records.")


if __name__ == "__main__":
    main()

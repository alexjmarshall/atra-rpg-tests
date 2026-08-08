from __future__ import annotations

import json
from pathlib import Path

from apply_longsword_evidence_audit import AUDITS


ROOT = Path(__file__).resolve().parents[1]
PLAY_DIR = ROOT / "data" / "plays"

SELECTED = {
    "play-german-longsword-absetzen",
    "play-german-longsword-zornhau-ort",
    "play-german-longsword-durchwechseln",
    "play-italian-longsword-scambiar-di-punta",
    "play-german-longsword-nachreisen",
    "play-italian-longsword-pommel-strike",
}

TACTICAL_LESSONS = {
    "play-german-longsword-absetzen":
        "Against an incoming thrust, set the blade aside from right Pflug while placing the point into the opponent.",
    "play-german-longsword-zornhau-ort":
        "Meet a committed descending cut with the counter-cut; only continue with the point when the resulting bind permits it.",
    "play-german-longsword-durchwechseln":
        "When an opponent seeks the blade before firm contact, change the point under the attempted defence and thrust on the other line.",
    "play-italian-longsword-scambiar-di-punta":
        "Against an incoming thrust, step offline, cross with the hands low and point high, and exchange with your own point.",
    "play-german-longsword-nachreisen":
        "Pursue a committed descending cut that has missed, striking before the opponent recovers.",
    "play-italian-longsword-pommel-strike":
        "From an established close crossing, control the opponent's arm as the source variant permits and strike the exposed face with the pommel.",
}


def apply_selected_corrections() -> None:
    for play_id in sorted(SELECTED):
        path = PLAY_DIR / f"{play_id}.yaml"
        record = json.loads(path.read_text(encoding="utf-8"))
        evidence = AUDITS[play_id]
        identity = record["historical_identity"]
        packet_citations = [
            citation for citation in identity["source_citations"]
            if citation["source_id"] == "atra-melee-design-packet-v0-4"
        ]
        exact_citations = []
        seen = set()
        for item in evidence["witnesses"]:
            key = (item["source_id"], item["location"])
            if key in seen:
                continue
            seen.add(key)
            exact_citations.append({
                "source_id": item["source_id"],
                "location": (
                    f"{item['manuscript_or_treatise']}; {item['approximate_date']}; "
                    f"{item['location']}; {item['edition_or_translator']}"
                ),
                "citation_status": "exact-historical-location",
            })
        identity["source_status"] = "exact-locator-verified"
        identity["source_citations"] = packet_citations + exact_citations
        identity["historical_confidence"] = evidence["proposed_historical_confidence"]
        identity["source_inclusion_basis"] = evidence["proposed_inclusion_basis"]
        identity["historical_names"] = evidence["historical_name_assessment"]["historical_names"]
        identity["historical_name_note"] = evidence["historical_name_assessment"]["relationship"]
        identity["packet_source_note"] = (
            "Item-level witness reviewed in the Prototype Longsword Evidence Audit; "
            "historical identity and locator promoted. Mechanical interpretation remains provisional."
        )
        record["game_implementation"]["tactical_lesson"] = TACTICAL_LESSONS[play_id]
        note = "Historical locator/name correction promoted; prototype mechanics remain separate and PROVISIONAL."
        if note not in record["prototype_evidence_audit"]["review_notes"]:
            record["prototype_evidence_audit"]["review_notes"].append(note)
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    apply_selected_corrections()
    print(f"Promoted historical corrections for {len(SELECTED)} selected Plays.")

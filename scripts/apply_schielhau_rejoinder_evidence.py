from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAY_PATH = ROOT / "data" / "plays" / "play-german-longsword-schielhau.yaml"


def apply_schielhau_evidence() -> None:
    record = json.loads(PLAY_PATH.read_text(encoding="utf-8"))
    identity = record["historical_identity"]
    packet = [citation for citation in identity["source_citations"]
              if citation["source_id"] == "atra-melee-design-packet-v0-4"]
    identity["source_status"] = "exact-locator-verified"
    identity["source_citations"] = packet + [{
        "source_id": "pseudo-peter-von-danzig",
        "location": (
            "Starhemberg Fechtbuch, Cod.44.A.8 (MS Cors.1449), 1452, "
            "longsword Schielhau text and gloss, ff. 23v.1-23v.2; "
            "Wiktenauer digital edition, transcription Dierk Hagedorn, "
            "draft English translation Michael Chidester"
        ),
        "citation_status": "exact-historical-location",
    }]
    identity["historical_confidence"] = "A"
    identity["source_inclusion_basis"] = "EARLIER"
    identity["historical_names"] = ["Schilär", "Schilhaw"]
    identity["historical_name_note"] = (
        "Atra uses the normalized modern spelling Schielhau. The witness directly "
        "links the named cut to denying an attempted change-through below."
    )
    identity["packet_source_note"] = (
        "Item-level witness reviewed for the mirrored Longsword prototype. "
        "Historical identity and anti-change-through instruction are promoted; "
        "the mechanical rejoinder remains PROVISIONAL."
    )
    record["game_implementation"]["tactical_lesson"] = (
        "Against the descending cut, strike long with the short edge; if the opponent "
        "tries to change through below, keep the point shooting forward to deny it."
    )
    PLAY_PATH.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    apply_schielhau_evidence()
    print("Promoted exact Schielhau rejoinder evidence.")

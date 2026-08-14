from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAYS = ROOT / "data" / "plays"
REPORT = ROOT / "reports" / "prototype-longsword-evidence-audit.md"

GERMAN_URL = "https://wiktenauer.com/wiki/Pseudo-Peter_von_Danzig"
GERMAN_MANUSCRIPT_URL = "https://www.wiktenauer.com/wiki/Starhemberg_Fechtbuch_%28Cod.44.A.8%29"
FIORE_WIDE_URL = "https://wiktenauer.com/wiki/Fiore_de%27i_Liberi/Sword_in_Two_Hands/Wide_Play"
FIORE_NARROW_URL = "https://www.wiktenauer.com/wiki/Fiore_de%27i_Liberi/Sword_in_Two_Hands/Narrow_Play"
VADI_URL = "https://wiktenauer.com/wiki/Philippo_di_Vadi"


def witness(source_id: str, manuscript: str, date: str, location: str,
            edition: str, url: str, paraphrase: str) -> dict:
    return {
        "source_id": source_id,
        "manuscript_or_treatise": manuscript,
        "approximate_date": date,
        "location": location,
        "edition_or_translator": edition,
        "url": url,
        "instruction_paraphrase": paraphrase,
    }


GERMAN_MANUSCRIPT = (
    "Starhemberg Fechtbuch, Rome, Biblioteca dell'Accademia Nazionale dei "
    "Lincei e Corsiniana, Cod.44.A.8 (MS Cors.1449), anonymous "
    "Pseudo-Peter von Danzig gloss"
)
GERMAN_EDITION = (
    "Wiktenauer digital edition: transcription by Dierk Hagedorn; draft "
    "English translation by Michael Chidester"
)
FIORE_MANUSCRIPT = (
    "Fiore dei Liberi, Fior di Battaglia, J. Paul Getty Museum MS Ludwig XV 13; "
    "Morgan MS M.383 and Pisani Dossi concordances where listed"
)
FIORE_EDITION = (
    "Wiktenauer digital concordance: Getty transcription by Michael Chidester; "
    "English translation by Colin Hatcher"
)
VADI_MANUSCRIPT = (
    "Philippo di Vadi, De Arte Gladiatoria Dimicandi, Biblioteca Nazionale "
    "Centrale di Roma MS Vitt. Em. 1324"
)
VADI_EDITION = (
    "Wiktenauer digital edition: transcription by Marco Rubboli and Luca Cesari; "
    "English translation by Guy Windsor"
)


def audit(name: str, historical_names: list[str], relationship: str,
          inclusion: str, grade: str, witnesses: list[dict], physical: dict,
          timing_type: str, clusters: list[str], assessment: str,
          chassis_notes: str, skill_rationale: str,
          review_notes: list[str] | None = None) -> dict:
    return {
        "status": "PROPOSED",
        "audit_scope": "longsword-evidence-prototype-v0.4",
        "historical_name_assessment": {
            "atra_game_facing_name": name,
            "historical_names": historical_names,
            "relationship": relationship,
        },
        "proposed_inclusion_basis": inclusion,
        "proposed_historical_confidence": grade,
        "witnesses": witnesses,
        "physical_requirements": physical,
        "recommended_test_skill": {
            "status": "PROPOSED",
            "skill": "Longsword",
            "rationale": skill_rationale,
        },
        "chassis_comparison": {
            "current_timing_type": timing_type,
            "current_provisional_clusters": clusters,
            "assessment": assessment,
            "notes": chassis_notes,
        },
        "review_notes": review_notes or [],
    }


AUDITS = {
    "play-german-longsword-zornhau-ort": audit(
        "Zornhau-Ort", ["Zornhau", "Zornhau, Ort"],
        "The Atra compound preserves the historical verse's named cut and immediate point, but presents them as one game-facing label.",
        "EARLIER", "A",
        [witness(
            "pseudo-peter-von-danzig", GERMAN_MANUSCRIPT, "1452",
            "Longsword, ff. 13r.3-13v.1", GERMAN_EDITION, GERMAN_URL,
            "Against a right-side descending cut to the head, answer with a descending cut from the right onto the opponent's sword; if the opponent is soft at contact, extend the point to the face or chest.",
        )],
        {
            "weapon_type": "Two-handed longsword.",
            "hand_requirement": "Both hands remain on the sword; no free hand is described.",
            "contact_or_bind_state": "Begins without contact; the counter-cut creates a bind, and the point follows if the opponent is soft.",
            "measure": "Cutting measure closing immediately to point/thrust measure.",
            "guard_or_posture": "Pre-fencing; the counter-cut is explicitly made from the right, but no named starting guard is given in this play.",
        },
        "Counter-attack", ["single-time-counters"], "match",
        "The source supports a counter-cut that simultaneously establishes an immediate point threat. The chassis must not assume any unapproved action-economy effect.",
        "The decisive historical action is performed with the longsword and requires ordinary two-handed blade control.",
        ["The manuscript metadata and digital edition credits are independently checkable on the Starhemberg Fechtbuch page: " + GERMAN_MANUSCRIPT_URL],
    ),
    "play-german-longsword-absetzen": audit(
        "Absetzen", ["Absetzen"],
        "The Atra name directly preserves the historical technical term.",
        "EARLIER", "A",
        [witness(
            "pseudo-peter-von-danzig", GERMAN_MANUSCRIPT, "1452",
            "Longsword, ff. 30r.2-30v.1", GERMAN_EDITION, GERMAN_URL,
            "Stand left foot forward in right Pflug and invite the left opening; against the incoming thrust, wind the short edge onto the opposing sword, set it aside, step with the right foot, and thrust at once to the face or chest.",
        )],
        {
            "weapon_type": "Two-handed longsword.",
            "hand_requirement": "Both hands remain on the sword; no free hand is described.",
            "contact_or_bind_state": "Starts against an incoming thrust and establishes blade contact during the displacement.",
            "measure": "Thrusting measure, with a passing step during the set-aside and answer.",
            "guard_or_posture": "Explicitly right Pflug with the left foot forward; the left opening is deliberately exposed.",
        },
        "Defence/attack", ["beats-and-displacements", "single-time-counters"], "match",
        "The witness directly supports a joined displacement and thrust. It does not by itself authorize a separate Atra reaction or action-preservation rule.",
        "The source action is a two-handed longsword displacement and thrust; no separate grappling implement is decisive.",
    ),
    "play-german-longsword-durchwechseln": audit(
        "Durchwechseln", ["Durchwechseln"],
        "The Atra name directly preserves the historical technical term.",
        "EARLIER", "A",
        [witness(
            "pseudo-peter-von-danzig", GERMAN_MANUSCRIPT, "1452",
            "Longsword, ff. 30v.3-31r.2", GERMAN_EDITION, GERMAN_URL,
            "When the opponent moves to parry or cut onto the sword rather than the body, let the point pass under the opposing blade before a bind forms and thrust to the other side; repeat the change if the opponent chases the new line.",
        )],
        {
            "weapon_type": "Two-handed longsword.",
            "hand_requirement": "Both hands remain on the sword; no free hand is described.",
            "contact_or_bind_state": "The key timing is before a firm bind; the point evades the attempted blade contact.",
            "measure": "Attacking/thrusting measure.",
            "guard_or_posture": "No named starting guard is explicit in this play.",
        },
        "Deception", ["changes-through-and-deceptions", "bind-and-winding-branches"], "match",
        "The change-through cluster is supported. The source is more specific than a generic feint: it exploits a blade-seeking parry and avoids contact before the bind.",
        "The point change and renewed thrust are controlled with the two-handed longsword.",
    ),
    "play-german-longsword-zwerchhau": audit(
        "Zwerchhau", ["Twerhau", "Twerhaw"],
        "Atra uses the normalized modern spelling of the historical name found in the witness.",
        "EARLIER", "A",
        [witness(
            "pseudo-peter-von-danzig", GERMAN_MANUSCRIPT, "1452",
            "Longsword, ff. 18v.2-19r.1", GERMAN_EDITION, GERMAN_URL,
            "From the sword at the right shoulder, act before an opponent in high Vom Tag completes the descending cut: spring to the right, turn the hilt in front of the head with the thumb under, and strike the opponent's left head with the short edge.",
        )],
        {
            "weapon_type": "Two-handed longsword.",
            "hand_requirement": "Both hands remain on the sword; no free hand is described.",
            "contact_or_bind_state": "Begins without blade contact and intercepts or preempts the opponent's high-line attack.",
            "measure": "Cutting/engagement measure with an offline spring.",
            "guard_or_posture": "Attacker's sword at the right shoulder; opponent explicitly in high Vom Tag with arms raised.",
        },
        "Master strike", [], "mismatch",
        "'Master strike' is a historical category, not a procedural chassis. The witness more usefully supports a guard-breaking, preemptive defence/attack or single-time-counter comparison.",
        "The action is a specialized two-handed longsword cut whose cover depends on hilt and edge orientation.",
    ),
    "play-german-longsword-winden": audit(
        "Winden", ["Winden"],
        "The Atra name directly preserves the historical system term.",
        "EARLIER", "A",
        [witness(
            "pseudo-peter-von-danzig", GERMAN_MANUSCRIPT, "1452",
            "Longsword, ff. 37r.2-38v.1; related action menu at ff. 14r.2-15r.1", GERMAN_EDITION, GERMAN_URL,
            "Use the four hangings at the two Ochs and two Pflug positions to make eight windings; feel whether the opponent is soft or hard in the bind, then select a cut, thrust, or slice from the appropriate winding with the necessary step.",
        )],
        {
            "weapon_type": "Two-handed longsword.",
            "hand_requirement": "Both hands remain on the sword; no free hand is described.",
            "contact_or_bind_state": "Requires established blade contact and pressure information in the bind.",
            "measure": "Bind/close-fencing measure, still using the full two-handed grip rather than an Italian half-sword grip.",
            "guard_or_posture": "Explicitly organized through the right and left Ochs and Pflug hangings.",
        },
        "Bind system", ["bind-and-winding-branches"], "match",
        "The bind-system classification is well supported, but the witness describes a decision system with multiple outcomes rather than one atomic technique.",
        "The historical decision system is entirely structured around two-handed longsword blade contact.",
    ),
    "play-german-longsword-nachreisen": audit(
        "Nachreisen", ["Nachreisen"],
        "The Atra name directly preserves the historical technical term.",
        "EARLIER", "A",
        [witness(
            "pseudo-peter-von-danzig", GERMAN_MANUSCRIPT, "1452",
            "Longsword, ff. 27v.2-28r.1; related continuations at ff. 28r.2-28v.2", GERMAN_EDITION, GERMAN_URL,
            "From left foot forward in Vom Tag, when the opponent makes a long free cut that travels down past the target, spring after it and cut to the head before the opponent recovers; related plays pursue the sword when the opponent leaves contact.",
        )],
        {
            "weapon_type": "Two-handed longsword.",
            "hand_requirement": "Both hands remain on the sword; no free hand is described.",
            "contact_or_bind_state": "The core play starts without contact after a missed or overextended cut; related continuations can begin as the opponent leaves the bind.",
            "measure": "Just outside the missed cut, then closing to cutting measure during recovery.",
            "guard_or_posture": "Core play explicitly begins left foot forward in Vom Tag.",
        },
        "Pursuit", ["pursuit-recovery"], "partial",
        "The pursuit/recovery chassis fits. The current lesson's broader 'preparation, miss, or withdrawal' wording spans several Nachreisen situations and should not be treated as one witnessed sequence without separate locators.",
        "The recovery-window attack is made with the two-handed longsword.",
    ),
    "play-italian-longsword-scambiar-di-punta": audit(
        "Scambiar di Punta", ["Scambiar de punta"],
        "Atra modernizes the preposition but preserves Fiore's named play.",
        "EARLIER", "A",
        [witness(
            "fiore-dei-liberi", FIORE_MANUSCRIPT, "early 15th century (commonly c. 1404-1409)",
            "Getty MS Ludwig XV 13, 26v-a; concordant Morgan 14v-c and Pisani Dossi 20b-c", FIORE_EDITION, FIORE_WIDE_URL,
            "Against a thrust, advance the front foot off line, pass the other foot across, cross the opposing sword with hands low and point high, and direct the point into the opponent's face or chest.",
        )],
        {
            "weapon_type": "Two-handed sword/longsword.",
            "hand_requirement": "Both hands remain on the sword; no free hand is described.",
            "contact_or_bind_state": "Begins against an incoming thrust and crosses it during the counter-thrust.",
            "measure": "Thrusting measure with two offline foot movements.",
            "guard_or_posture": "No named guard is explicit; hands are explicitly low and the point high during the crossing.",
        },
        "Counter-thrust", ["single-time-counters"], "match",
        "The source directly supports a joined cover and counter-thrust. It does not settle any Atra reaction or action-preservation mechanics.",
        "The decisive cover and counter-thrust use the two-handed longsword.",
    ),
    "play-italian-longsword-rompere-di-punta": audit(
        "Rompere di Punta", ["Romper de punta"],
        "Atra regularizes the infinitive form while preserving Fiore's named play.",
        "EARLIER", "A",
        [witness(
            "fiore-dei-liberi", FIORE_MANUSCRIPT, "early 15th century (commonly c. 1404-1409)",
            "Getty MS Ludwig XV 13, 26v-c; immediate continuations 26v-d-27r-b", FIORE_EDITION, FIORE_WIDE_URL,
            "With the hands high, step off line and strike down across the middle of the incoming sword to drive the thrust to the ground, then close immediately into Fiore's close play; the following plays show pinning and striking continuations.",
        )],
        {
            "weapon_type": "Two-handed sword/longsword.",
            "hand_requirement": "Both hands begin on the sword; later close-play continuations may release a hand, but that is not part of the core break.",
            "contact_or_bind_state": "Begins against an incoming thrust; forceful blade contact at the middle of the opposing sword drives it down.",
            "measure": "Starts at thrusting measure and explicitly transitions toward close/grappling measure.",
            "guard_or_posture": "No named guard is explicit; hands are explicitly held high for the downward break.",
        },
        "Defence", ["beats-and-displacements", "single-time-counters"], "partial",
        "The beat/displacement classification is supported, but 'Defence' under-describes the source's explicit transition to close play. The core witness does not itself prescribe a universal immediate weapon strike.",
        "The core defence is a two-handed longsword beat; close-play continuations remain separate candidate evidence.",
    ),
    "play-italian-longsword-colpo-di-villano": audit(
        "Colpo di Villano", ["Colpo del villano"],
        "Atra modernizes the preposition while preserving Fiore's named play.",
        "EARLIER", "A",
        [witness(
            "fiore-dei-liberi", FIORE_MANUSCRIPT, "early 15th century (commonly c. 1404-1409)",
            "Getty MS Ludwig XV 13, 26r-a; concordant Morgan 14r-c/d and Pisani Dossi 20a-c", FIORE_EDITION, FIORE_WIDE_URL,
            "Wait in a narrow stance with the left foot forward; against a powerful uncontrolled descending blow, step off line, receive it at the middle of the sword, let it run to the ground, then answer with a descending cut to head or arms or a thrust to the chest.",
        )],
        {
            "weapon_type": "Two-handed sword/longsword.",
            "hand_requirement": "Both hands remain on the sword; no free hand is described.",
            "contact_or_bind_state": "Begins without contact; receives the descending blow at mid-blade and lets it slide to the ground.",
            "measure": "Sword measure, with an offline step during reception and an immediate return.",
            "guard_or_posture": "Explicit small/narrow stance with the left foot forward; no named guard is supplied in the Getty wording.",
        },
        "Defence/attack", ["single-time-counters"], "partial",
        "The defensive reception and answer are supported. The record's anti-number tag is an Atra design hypothesis; this witness does not present the play as an engagement-control technique against several opponents.",
        "The cover and return are both two-handed longsword actions.",
    ),
    "play-italian-longsword-false-point": audit(
        "False Point", ["Punta falsa", "Punta curta"],
        "Atra translates and normalizes Fiore's historical labels into an English game-facing name.",
        "EARLIER", "A",
        [witness(
            "fiore-dei-liberi", FIORE_MANUSCRIPT, "early 15th century (commonly c. 1404-1409)",
            "Getty MS Ludwig XV 13, 27v-a; concordant Pisani Dossi 21b-c", FIORE_EDITION, FIORE_WIDE_URL,
            "Show a forceful middle cut toward the head; when the opponent covers and the swords touch, make only light contact, turn to the other side, seize the middle of your own blade with the left hand, and thrust to throat or chest. Fiore says it works better in armor.",
        )],
        {
            "weapon_type": "Two-handed sword/longsword; the final thrust uses a half-sword grip.",
            "hand_requirement": "Both hands begin on the hilt; the left hand then releases the hilt and grips the middle of the blade.",
            "contact_or_bind_state": "Requires the opponent to cover the apparent cut and create light blade contact before the change.",
            "measure": "Begins at cutting measure and closes to half-sword thrusting measure.",
            "guard_or_posture": "No named starting guard is explicit; armor is expressly preferred.",
        },
        "Deception", ["changes-through-and-deceptions"], "partial",
        "The deception cluster fits, but the current tactical lesson says to threaten one thrust and change to another. The witness instead begins with a false middle cut and changes into a half-sword thrust.",
        "The entire sequence is organized through longsword cutting, contact, and a half-sword thrust.",
        ["The current tactical lesson is the clearest evidence/chassis wording mismatch in the Italian sample."],
    ),
    "play-italian-longsword-pommel-strike": audit(
        "Pommel Strike", ["Ferir cum lo pomo (descriptive wording)"],
        "Atra supplies a normalized English game-facing title for an explicitly described pommel action rather than preserving a formal play title.",
        "EARLIER", "A",
        [witness(
            "fiore-dei-liberi", FIORE_MANUSCRIPT, "early 15th century (commonly c. 1404-1409)",
            "Getty MS Ludwig XV 13, 28r-c and 28r-d; concordant Morgan 16r-c/d and Pisani Dossi 22a-c/d", FIORE_EDITION, FIORE_NARROW_URL,
            "From a close crossing, control the opponent's arm or elbow and strike the face with the pommel; one continuation follows with a descending strike, while the adjacent variant emphasizes an uncovered face and then places the sword at the neck.",
        )],
        {
            "weapon_type": "Two-handed sword/longsword used at the hilt and pommel.",
            "hand_requirement": "The source variants begin with both hands controlling the sword; one explicitly releases the left hand to seize the opponent's elbow.",
            "contact_or_bind_state": "Requires an established close crossing and arm access.",
            "measure": "Close-play/grappling measure.",
            "guard_or_posture": "No named guard; the close crossing is the explicit posture/state.",
        },
        "Close play", ["close-play-and-grapples"], "match",
        "The close-play chassis is supported. Review should keep the elbow-control variant distinct from the adjacent pommel variant instead of assuming one mandatory hand sequence.",
        "The pommel is part of the longsword and the entry is created by a longsword crossing; a future wrestling prerequisite remains an unapproved design question.",
    ),
    "play-italian-longsword-crossing-throw": audit(
        "Crossing Throw", ["No stable named-play title; two throws described from close crossings"],
        "Atra creates a game-facing umbrella name for two closely related source plays.",
        "EARLIER", "B",
        [witness(
            "fiore-dei-liberi", FIORE_MANUSCRIPT, "early 15th century (commonly c. 1404-1409)",
            "Getty MS Ludwig XV 13, 30r-a and 30r-b; concordant Morgan 15r-c/d and Pisani Dossi 22b-c", FIORE_EDITION, FIORE_NARROW_URL,
            "From close crossings, place the sword around or at the opponent's neck, control either the weapon hand or elbow with the left hand, step the right foot behind the opponent's right, and throw. One variant grips the opponent's hand; the other grips one's own blade after pressing the elbow.",
        )],
        {
            "weapon_type": "Two-handed sword/longsword used as neck control and lever during the throw.",
            "hand_requirement": "Both hands begin in sword control; the left hand becomes free for hand/elbow control or grips the middle of one's own blade, depending on the variant.",
            "contact_or_bind_state": "Requires an established close crossing and body/arm access.",
            "measure": "Close-play/grappling measure with the right foot stepping behind the opponent.",
            "guard_or_posture": "No named guard; a right- or left-side close crossing is the explicit starting state.",
        },
        "Grapple", ["throws-and-takedowns", "close-play-and-grapples"], "partial",
        "The grapple/throw chassis fits broadly. The current single candidate consolidates two different hand-control solutions, so any implementation must not silently choose one as canonical.",
        "The throw is entered from and materially uses the longsword crossing; a future wrestling prerequisite remains an unapproved design question.",
        ["Grade B is proposed for the Atra candidate mapping, not for the existence of the two well-attested source actions."],
    ),
    "play-italian-longsword-cuts-against-many": audit(
        "Cuts Against Many", ["No historical named play; Vadi gives tactical advice about fighting more than one"],
        "Atra transparently synthesizes a game-facing candidate from Vadi's period principles.",
        "RECONSTRUCTION", "C",
        [
            witness(
                "philippo-di-vadi", VADI_MANUSCRIPT, "1482-1487",
                "Chapter 4, ff. 7v.2-8r", VADI_EDITION, VADI_URL,
                "Vadi advises avoiding a fight against more than one; if forced, use a sword that can be handled lightly rather than a heavy weapon, abandon the thrust, and use other blows.",
            ),
            witness(
                "philippo-di-vadi", VADI_MANUSCRIPT, "1482-1487",
                "Chapter 8, ff. 10r-10v.1", VADI_EDITION, VADI_URL,
                "Vadi explains that a thrust may serve against one opponent but is dangerous against several because a companion can strike while the point is committed; a lighter weapon can leave and recover quickly.",
            ),
        ],
        {
            "weapon_type": "A light, manageable two-handed sword; Vadi expressly contrasts it with a heavy weapon.",
            "hand_requirement": "Two-handed sword use is the curriculum context; no free-hand action is described.",
            "contact_or_bind_state": "No bind is required; this is general advice for engagement against multiple opponents, not a discrete crossed-blade play.",
            "measure": "Variable engagement measure against more than one opponent; rapid weapon recovery is the explicit concern.",
            "guard_or_posture": "No guard or starting posture is specified.",
        },
        "Clearing / recovery", ["pursuit-recovery"], "partial",
        "The recovery emphasis is supported, but the witness gives tactical and equipment advice rather than a discrete clearing technique. The candidate should remain a transparent reconstruction and not imply a witnessed named play.",
        "The evidence is explicitly about managing a two-handed sword against several opponents, making Longsword the least-assumptive proposed Test Skill.",
        ["The reconstruction grade follows the packet's confidence rubric even though the underlying Vadi passages have exact locators."],
    ),
}


def build_report(records: dict[str, dict]) -> str:
    lines = [
        "# Prototype Longsword Evidence Audit",
        "",
        "Status: **PROPOSED pending review**",
        "",
        "Governing document: Atra Melee Design Packet v0.4. This report audits only the 13 records named in the request (treating `Pommel Strike/Crossing Throw` as two existing candidates). It does not settle OPEN or PROVISIONAL questions. Canonical source status, historical-confidence fields, Test Skills, prerequisites, equipment requirements, and all mechanics remain unchanged/null in the research records.",
        "",
        "## Method and grade proposal",
        "",
        "`EARLIER` means a permitted earlier fifteenth-century witness; `RECONSTRUCTION` means the Atra candidate is a transparent synthesis from eligible period principles. Grades follow the packet's A/B/C/D rubric, but every grade below is a proposal. A grade evaluates the mapping between the named Atra candidate and its evidence—not merely whether a passage exists.",
        "",
        "| Candidate | Proposed basis | Proposed grade | Chassis finding |",
        "|---|---:|:---:|---|",
    ]
    for play_id, evidence in AUDITS.items():
        comparison = evidence["chassis_comparison"]
        lines.append(
            f"| {evidence['historical_name_assessment']['atra_game_facing_name']} | "
            f"{evidence['proposed_inclusion_basis']} | {evidence['proposed_historical_confidence']} | "
            f"{comparison['assessment']} |"
        )

    lines += [
        "",
        "## Witness audits",
        "",
    ]
    for play_id, evidence in AUDITS.items():
        record = records[play_id]
        names = evidence["historical_name_assessment"]
        physical = evidence["physical_requirements"]
        comparison = evidence["chassis_comparison"]
        lines += [
            f"### {names['atra_game_facing_name']}",
            "",
            f"- **Record:** `{play_id}`",
            f"- **Names:** Atra game-facing name: **{names['atra_game_facing_name']}**. Historical name(s): {', '.join(names['historical_names'])}. {names['relationship']}",
            f"- **Proposed inclusion:** **{evidence['proposed_inclusion_basis']} / {evidence['proposed_historical_confidence']}**, PROPOSED pending review.",
            "- **Witnesses:**",
            "",
        ]
        for item in evidence["witnesses"]:
            lines += [
                f"  - [{item['manuscript_or_treatise']}]({item['url']}); {item['approximate_date']}; **{item['location']}**. {item['edition_or_translator']}.",
                f"    - Source instruction, paraphrased: {item['instruction_paraphrase']}",
            ]
        lines += [
            "",
            "- **Physical requirements:**",
            "",
            f"  - Weapon: {physical['weapon_type']}",
            f"  - Hands: {physical['hand_requirement']}",
            f"  - Contact/bind: {physical['contact_or_bind_state']}",
            f"  - Measure: {physical['measure']}",
            f"  - Guard/posture: {physical['guard_or_posture']}",
            "",
            f"- **Test Skill recommendation:** **Longsword — PROPOSED, not canonical.** {evidence['recommended_test_skill']['rationale']}",
            f"- **Current chassis comparison:** packet timing/type **{record['game_implementation']['timing']['type']}**; audit cluster(s) **{', '.join(comparison['current_provisional_clusters']) or 'none assigned'}**; finding **{comparison['assessment']}**. {comparison['notes']}",
        ]
        if evidence["review_notes"]:
            lines.append(f"- **Review notes:** {' '.join(evidence['review_notes'])}")
        lines.append("")

    lines += [
        "## Cross-candidate findings",
        "",
        "- **Strong direct mappings:** Zornhau-Ort, Absetzen, Durchwechseln, Winden, Scambiar di Punta, and Pommel Strike have exact passages that closely match their current candidate identity.",
        "- **Chassis wording needs review:** Zwerchhau is currently typed by historical category rather than procedural chassis; False Point currently describes the wrong initial threat; Rompere di Punta under-describes its close-play transition; Nachreisen compresses multiple pursuit moments; Crossing Throw consolidates two variants.",
        "- **Anti-number caution:** Colpo di Villano's witness supports reception and return, not an anti-number doctrine. Cuts Against Many has direct Vadi principles but remains a reconstructed candidate rather than a named technique.",
        "- **Skill/equipment result:** Longsword is the least-assumptive proposed Test Skill for all 13. False Point explicitly changes to a half-sword grip. Pommel Strike and Crossing Throw may release the left hand in source variants. No record has been given a canonical free-hand or Wrestling prerequisite.",
        "",
        "## Source-policy and edition notes",
        "",
        f"- German manuscript metadata and edition credits: [Starhemberg Fechtbuch, Cod.44.A.8]({GERMAN_MANUSCRIPT_URL}). Exact play text is in the [Pseudo-Peter von Danzig digital edition]({GERMAN_URL}).",
        f"- Fiore wide-play concordance: [Sword in Two Hands, Wide Play]({FIORE_WIDE_URL}). Close-play concordance: [Sword in Two Hands, Narrow Play]({FIORE_NARROW_URL}).",
        f"- Vadi manuscript, transcription, and translation: [Philippo di Vadi]({VADI_URL}).",
        "- No verbatim source passage is reproduced. Paraphrases are deliberately short; folio/play locators are retained for independent checking.",
        "",
    ]
    return "\n".join(lines)


def apply_audit(write_report: bool = True) -> None:
    records: dict[str, dict] = {}
    for play_id, evidence in AUDITS.items():
        path = PLAYS / f"{play_id}.yaml"
        if not path.exists():
            raise FileNotFoundError(path)
        record = json.loads(path.read_text(encoding="utf-8"))
        if record["id"] != play_id:
            raise ValueError(f"ID mismatch in {path}: {record['id']}")
        current_type = record["game_implementation"]["timing"]["type"]
        proposed_current_type = evidence["chassis_comparison"]["current_timing_type"]
        if current_type != proposed_current_type:
            raise ValueError(
                f"Stale chassis comparison for {play_id}: "
                f"record has {current_type!r}, audit says {proposed_current_type!r}"
            )
        record["prototype_evidence_audit"] = evidence
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        records[play_id] = record
    if write_report:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(build_report(records), encoding="utf-8")


if __name__ == "__main__":
    apply_audit()
    print(f"Applied PROPOSED evidence audits to {len(AUDITS)} records.")
    print(f"Wrote {REPORT.relative_to(ROOT)}")

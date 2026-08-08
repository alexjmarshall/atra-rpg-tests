from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = Path(__file__).resolve().parent / "results.json"
REPORT_PATH = ROOT / "reports" / "compound-spiritus-c1-c2-results.md"
PLAYS = ("Absetzen", "Scambiar di Punta", "Schielhau")


def pct(value: float) -> str:
    return f"{value:.1%}"


def num(value: float) -> str:
    return f"{value:.3f}"


def cell_name(cell: dict[str, Any]) -> str:
    info = "Adaptive" if cell["information"] == "adaptive_revelation" else "Perfect"
    return f"{cell['skill_a']} / {cell['start_spiritus_a']} / C{cell['compound_cost']} / {info}"


def ordered_primary(data: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        data["primary_matrix"].values(),
        key=lambda item: (
            item["cell"]["skill_a"], item["cell"]["start_spiritus_a"],
            item["cell"]["compound_cost"], item["cell"]["information"],
        ),
    )


def aggregate_declines(items: list[dict[str, Any]], cost: int, play: str) -> Counter[str]:
    result: Counter[str] = Counter()
    for item in items:
        if item["cell"]["compound_cost"] == cost:
            result.update(item["metrics"]["compounds"][play]["decline_reasons"])
    return result


def weighted_value(items: list[dict[str, Any]], cost: int, play: str, key: str) -> float:
    numerator = 0.0
    denominator = 0
    sum_key = {
        "mean_basic_parry_value": "basic_value_sum",
        "mean_counter_value": "counter_value_sum",
        "mean_compound_value": "compound_value_sum",
        "mean_compound_no_cost_value": "compound_no_cost_value_sum",
    }[key]
    for item in items:
        if item["cell"]["compound_cost"] != cost:
            continue
        stats = item["metrics"]["compounds"][play]
        numerator += stats[sum_key]
        denominator += stats[
            "compound_value_observations" if key == "mean_compound_value" else "value_observations"
        ]
    return numerator / denominator if denominator else 0.0


def surface_row(data: dict[str, Any], skill: int, cost: int, spiritus: int, play: str) -> dict[str, Any]:
    return next(
        row for row in data["policy_surface"]
        if row["skill"] == skill and row["compound_cost"] == cost
        and row["spiritus"] == spiritus and row["defender_hp"] == 8 and row["play"] == play
    )


def known_mix(item: dict[str, Any], spiritus: int) -> dict[str, float]:
    choices = Counter(item["metrics"]["known_durch_defence_choices_by_spiritus"][str(spiritus)])
    total = sum(choices.values())
    compounds = sum(choices[name] for name in PLAYS)
    return {
        "n": total,
        "Basic Parry": choices["Basic Parry"] / total if total else 0.0,
        "Counter": choices["Counter"] / total if total else 0.0,
        "Compound": compounds / total if total else 0.0,
        "Zornhau-Ort": choices["Zornhau-Ort"] / total if total else 0.0,
        "Ignore": choices["Ignore"] / total if total else 0.0,
    }


def sequence_state_rate(focal: dict[str, Any], spiritus: str) -> float:
    states = focal["exchange_resource_states"]
    return states.get(spiritus, 0) / sum(states.values()) if states else 0.0


def build_report(data: dict[str, Any]) -> str:
    items = ordered_primary(data)
    lines = [
        "# Compound Spiritus C1/C2 Results", "",
        "Status: **PROVISIONAL bounded pricing experiment; no canonical rule change**", "",
        "## Executive result", "",
        "**C2 is the better next prototype price.** It creates the intended low-resource distinction without turning Absetzen, Scambiar di Punta, or Schielhau into rare ultimate abilities. At starting Spiritus 8, C2 still puts at least one compound in 59.5%–82.9% of fresh duels across the matrix. At starting Spiritus 3, the difference becomes consequential: aggregate compound declarations fall by roughly one third to one half, Basic Parry and Counter recover, and C2 produces legal-but-unaffordable opportunities. C1, by contrast, leaves Schielhau near automatic at expert skill and makes resource state above 1 weakly relevant.", "",
        "The result is not a promotion. P1, D1, S2, maximum Spiritus 8, and C2 remain **PREFERRED PROVISIONAL / TESTED**, while final compound cost, recovery, maximum, other Play prices, Guards, Power Strike, bind mechanics, engagement geometry, weapon profiles, tiers, and text remain **OPEN**.", "",
        "## Scope, controls, and repository continuity", "",
        "The experiment retained the repository's current P1 Basic Parry, D1 Durchwechseln declared before the Parry roll with no refund, S2 Schielhau–Durchwechseln resolution, Variant A one-roll compound chassis, normal action expenditure, intrinsic branches, public Spiritus, maximum 8, generic d6+1 damage, and the provisional three-learned-Play cap. It changed only the common price of Absetzen, Scambiar di Punta, and Schielhau from C1 to C2.", "",
        "The previous Spiritus/Parry experiment is present in tracked repository form as a model, simulator, JSON result set, CSV summaries, and report. This run used a separate simulator and did not overwrite it. No governing-input conflict was found. Historical identities and evidence were not edited; no Play record or main design packet was changed.", "",
        f"Seed: `{data['seed']}`. Trials: `{data['trials']}`. Primary cells: **{len(data['primary_matrix'])}**; optional asymmetric cells: **{len(data['asymmetric_check'])}**; R0 sequence cells: **{len(data['sequences'])}**.", "",
        "Power Strike competition remains unmodeled.", "",
        "## Fresh-duel general results — every primary cell", "",
        "`Win A` is the focal-side outright win rate; `Sym dev` is |A wins − B wins| / fights. Double defeat is reported separately.", "",
        "| Skill / start / cost / info | Win A | Sym dev | Rounds | Double defeat | Spiritus spent/fight | End Spiritus | End 0 | End 1–2 | End 3–5 | End 6–8 | Unused at defeat |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in items:
        c, m = item["cell"], item["metrics"]
        lines.append(
            f"| {cell_name(c)} | {pct(m['focal_win_rate'])} | {pct(m['symmetry_deviation'])} | {m['average_rounds']:.3f} | {pct(m['double_defeat_rate'])} | {m['total_spiritus_per_fight']:.3f} | {m['mean_end_spiritus_per_combatant']:.2f} | {pct(m['end_at_0_rate'])} | {pct(m['end_at_1_2_rate'])} | {pct(m['end_at_3_5_rate'])} | {pct(m['end_at_6_8_rate'])} | {m['unused_spirit_at_defeat_mean']:.2f} |"
        )

    lines += [
        "", "Mirrored symmetry deviations were 0.15%–2.39%; no directional outcome claim is made from them. C2 raises Spiritus expenditure while also increasing substitution toward Counter. At Skill 18 / start 3 / perfect information, that substitution raises double defeat from 16.8% under C1 to 21.1% under C2, reinforcing the already-OPEN elite mutual-lethality warning.", "",
        "## Basic options and Durchwechseln — every primary cell", "",
        "| Skill / start / cost / info | Basic Parry/fight | % def. opp. | After-known/fight | Counter/fight | Ignore/fight | D opp./fight | D declare/fight | D decline | D success | D damage/fight | D Spiritus/fight | Mean S declare | Mean S decline |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in items:
        c, m = item["cell"], item["metrics"]
        fights = m["fights"]
        lines.append(
            f"| {cell_name(c)} | {m['basic_parry_declarations_per_fight']:.3f} | {pct(m['basic_parry_defensive_opportunity_rate'])} | {m['basic_parry_after_known_per_fight']:.3f} | {m['counter_per_fight']:.3f} | {m['ignore_per_fight']:.3f} | {m['durch_opportunities']/fights:.3f} | {m['durch_declarations']/fights:.3f} | {pct(m['durch_decline_rate'])} | {pct(m['durch_success_rate'])} | {m['durch_damage_per_fight']:.3f} | {m['durch_spiritus_per_fight']:.3f} | {m['accepted_actor_spirit_mean']:.2f} | {m['declined_actor_spirit_mean']:.2f} |"
        )

    lines += [
        "", "D1 remains active under both prices and, because it is still affordable at exactly 1 Spiritus under C2, clearly occupies the cheaper tactical-conversion tier. Its use changes indirectly because the reserve is also valued for compounds; this is policy interaction, not a change to D1.", "",
        "## Compound Plays total — every primary cell", "",
        "| Skill / start / cost / info | Declarations/fight | Spiritus/fight | Damage/fight | Damage share | % defensive opp. | Fights 1+ | Fights 2+ | Fights 3+ |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in items:
        c, t = item["cell"], item["metrics"]["compound_total"]
        lines.append(
            f"| {cell_name(c)} | {t['declarations_per_fight']:.3f} | {t['spiritus_per_fight']:.3f} | {t['damage_per_fight']:.3f} | {pct(t['damage_share'])} | {pct(t['defensive_opportunity_rate'])} | {pct(t['fights_with_1_plus_rate'])} | {pct(t['fights_with_2_plus_rate'])} | {pct(t['fights_with_3_plus_rate'])} |"
        )

    lines += [
        "", "At healthy reserves, C2 reduces rather than deletes compound fencing. The strongest C2 fresh cells still resolve 49.4%–56.1% of defensive opportunities with compounds at Skills 14–18 / start 8, and 69.3%–82.9% of those fights contain at least one compound. At start 3, C2 creates the intended substitution: aggregate compound declaration rates fall to 20.6%–37.8% of defensive opportunities while Basic Parry and Counter rise.", "",
        "## Individual compound usage — every primary cell", "",
        "| Cell | Play | Opp./fight | Decl./fight | Decl. rate | Success | Damage/fight | Damage share | Spiritus/fight | Mean S declare | Unaffordable/fight |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in items:
        c, m = item["cell"], item["metrics"]
        for play in PLAYS:
            s = m["compounds"][play]
            lines.append(
                f"| {cell_name(c)} | {play} | {s['opportunities']/m['fights']:.3f} | {s['declarations']/m['fights']:.3f} | {pct(s['declaration_rate'])} | {pct(s['success_rate'])} | {s['damage_per_fight']:.3f} | {pct(s['damage_share'])} | {s['spiritus_per_fight']:.3f} | {s['mean_spiritus_at_declaration']:.2f} | {s['legal_unaffordable_opportunities']/m['fights']:.3f} |"
            )

    lines += [
        "", "| Cell | Play | Use S 6–8 | Use S 3–5 | Use S 2 | Use S 1 | Use S 0 | Parry displaced/fight | Counter displaced/fight | Early use | Late use |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in items:
        c, m = item["cell"], item["metrics"]
        for play in PLAYS:
            s = m["compounds"][play]
            bands = s["declaration_rate_by_requested_band"]
            lines.append(
                f"| {cell_name(c)} | {play} | {pct(bands['6-8'])} | {pct(bands['3-5'])} | {pct(bands['2'])} | {pct(bands['1'])} | {pct(bands['0'])} | {s['parry_displaced']/m['fights']:.3f} | {s['counter_displaced']/m['fights']:.3f} | {pct(s['early_use_rate'])} | {pct(s['late_use_rate'])} |"
            )

    lines += [
        "", "Sparse bands should not be over-read: start-8 fights rarely reach Spiritus 2 or 1. The standardized policy surface and three-fight sequences below provide the controlled threshold comparison.", "",
        "## Opportunity value and utility classifications", "",
        "For every legal compound opportunity the simulator recorded the current policy value of Basic Parry, Counter, the relevant paid compound, and the same compound without its Spiritus charge. It also classified every non-selection by utility reason. The full per-cell sums, denominators, and counts are in `results.json`; the weighted primary-matrix summary is:", "",
        "| Cost | Play | Mean Basic value | Mean Counter value | Mean compound value | Mean no-cost compound | Conservation | Insufficient | Basic better | Counter better | Tactical/HP | Exploration |", "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cost in (1, 2):
        for play in PLAYS:
            reasons = aggregate_declines(items, cost, play)
            total = sum(reasons.values())
            get = lambda key: reasons[key] / total if total else 0.0
            lines.append(
                f"| C{cost} | {play} | {weighted_value(items,cost,play,'mean_basic_parry_value'):.3f} | {weighted_value(items,cost,play,'mean_counter_value'):.3f} | {weighted_value(items,cost,play,'mean_compound_value'):.3f} | {weighted_value(items,cost,play,'mean_compound_no_cost_value'):.3f} | {pct(get('Spiritus conservation'))} | {pct(get('insufficient Spiritus'))} | {pct(get('Basic Parry has better expected value'))} | {pct(get('Counter has better expected value'))} | {pct(get('tactical/HP urgency'))} | {pct(get('other policy exploration'))} |"
            )

    lines += [
        "", "The zero Basic/Counter-better columns are a revealing limitation of this utility model: the unpriced two-effect chassis always has higher one-step expected value than either basic option. C2 creates meaningful choices through resource charge and unaffordability, not because the modeled immediate compound effect becomes intrinsically worse. `Other policy exploration` is dominated by seeded softmax mixing and, for the thrust, competition between mechanically identical Absetzen and Scambiar options. `Tactical/HP urgency` is mainly free Zornhau-Ort competing with Schielhau on committed cuts.", "",
        "## Spiritus shadow price and same-state thresholds", "",
        "The standardized surface holds both fighters at full HP, uses perfect information, and varies only the compound user's Spiritus. Absetzen and Scambiar have identical modeled utilities; Schielhau has one compound option rather than two competing thrust options.", "",
        "| Skill | Play | Cost | S8 select | S5 select | S3 select | S2 select | S1 select |", "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for skill in (10, 14, 18):
        for play in ("Absetzen", "Schielhau"):
            for cost in (1, 2):
                probs = [surface_row(data, skill, cost, s, play)["selection_probability"] for s in (8, 5, 3, 2, 1)]
                lines.append(f"| {skill} | {play} | C{cost} | " + " | ".join(pct(v) for v in probs) + " |")

    lines += [
        "", "| Cost | Comparison | Mean selection-probability change from +1 Spiritus | Mean compound-utility change | Reading |", "|---:|---|---:|---:|---|",
    ]
    for cost in (1, 2):
        for comparison in ("8_vs_7", "5_vs_4", "3_vs_2", "2_vs_1"):
            rows = [row for row in data["shadow_price_pairs"] if row["compound_cost"] == cost and row["comparison"] == comparison]
            prob_delta = mean(row["probability_difference"] for row in rows)
            finite_utility = [
                row["utility_difference"] for row in rows
                if isinstance(row["utility_difference"], (int, float))
                and math.isfinite(row["utility_difference"])
            ]
            util_delta = mean(finite_utility) if finite_utility else math.inf
            reading = "C2 unavailable at the lower state; D1 remains available" if cost == 2 and comparison == "2_vs_1" else "marginal reserve value"
            util_text = "threshold / unavailable" if not finite_utility else f"{util_delta:.3f}"
            lines.append(f"| C{cost} | {comparison.replace('_vs_',' vs ')} | {pct(prob_delta)} | {util_text} | {reading} |")

    lines += [
        "", "C1 has weak high-reserve differentiation and a large 2→1 conservation effect, but the compound remains legal at 1. C2 creates earlier conservation (especially 3→2) and the categorical 2→1 availability break. A Skill-10 Absetzen opportunity, for example, falls from 36.0% selection at Spiritus 8 to 16.1% at 3, 0.9% at 2, and unavailable at 1. At Skill 14 the same C2 probabilities are 46.5%, 36.5%, 19.1%, and 0%. This is the intended “worth it now?” decision rather than a flat upgrade.", "",
        "### Emergent 0 / 1 / 2 hierarchy", "",
        "- At 0 Spiritus, neither D1 nor C2 compounds are affordable: only basic/free fencing remains.",
        "- At 1 Spiritus, D1 remains affordable and C2 compounds are unavailable.",
        "- At 2 Spiritus, C2 compounds become legal but consume the entire reserve; policy selection is sharply conservative rather than automatic.",
        "- At 3+ Spiritus, compounds become credible threats, with use rising strongly by Skill and urgency.", "",
        "A fighter at 1 therefore behaves meaningfully differently from one at 2 in option availability, though the one-step policy often conserves even at 2. This is useful differentiation, not proof that the exact reserve utility is calibrated.", "",
        "## Skill-18 Basic Parry and defensive progression", "",
        "The table below uses only defensive opportunities after Durchwechseln is known in the Skill-18, start-3, C2 cells, where depletion is actually observed.", "",
        "| Information | Spiritus | Opportunities | Basic Parry | Counter | Compound | Zornhau-Ort | Ignore |", "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for information in ("adaptive_revelation", "perfect_information"):
        item = next(
            item for item in items
            if item["cell"]["skill_a"] == 18 and item["cell"]["start_spiritus_a"] == 3
            and item["cell"]["compound_cost"] == 2 and item["cell"]["information"] == information
        )
        for spiritus in (3, 2, 1, 0):
            mix = known_mix(item, spiritus)
            info = "Adaptive" if information == "adaptive_revelation" else "Perfect"
            lines.append(
                f"| {info} | {spiritus} | {mix['n']} | {pct(mix['Basic Parry'])} | {pct(mix['Counter'])} | {pct(mix['Compound'])} | {pct(mix['Zornhau-Ort'])} | {pct(mix['Ignore'])} |"
            )

    lines += [
        "", "This is **intended expertise progression with a retained warning**, not compound-driven pathological deletion. Compounds dominate much of the healthy-reserve expert mix and vanish at 1; Counter then becomes the main substitute. Basic Parry recovers from 3.7% at Spiritus 3 to 14.1% at 2 in the adaptive cell and reaches 19.4% at 0, but it remains only 2.1% at Spiritus 1 under perfect information because D1 still specifically threatens P1. That reproduces the earlier high-skill finding rather than fixing or worsening it through compound price. Basic Parry is not mechanically deleted by C2, but known D1 and high-value Counter continue to suppress it.", "",
        "## Optional asymmetric Skill check", "",
        "These perfect-information start-8 cells are response checks, not a second full matrix. Because both fighters know the same repertoire, declarations by side also reflect how often that side must defend, not only preference.", "",
        "| Skill A/B | Cost | A win-equivalent | A compound/fight | B compound/fight | A D/fight | B D/fight |", "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in sorted(data["asymmetric_check"].values(), key=lambda x: (x["cell"]["skill_a"], x["cell"]["skill_b"], x["cell"]["compound_cost"])):
        c, m = item["cell"], item["metrics"]
        a, b, fights = m["sides"]["A"], m["sides"]["B"], m["fights"]
        lines.append(
            f"| {c['skill_a']}/{c['skill_b']} | C{c['compound_cost']} | {pct(m['focal_win_equivalent'])} | {a['compound_declarations']/fights:.3f} | {b['compound_declarations']/fights:.3f} | {a['durch_declarations']/fights:.3f} | {b['durch_declarations']/fights:.3f} |"
        )

    lines += [
        "", "C2 changes win-equivalent by at most 1.5 percentage points in these 6,000-trial cells and reduces compound use on both sides. No strong evidence appears that C2 uniquely fails when the user is more or less skilled; the weaker side often records more compound declarations because it faces more successful attacks.", "",
        "## Three-fight R0 attrition", "",
        "Focal HP, action/state, and knowledge reset each fight; every opponent is fresh at Spiritus 8; only focal Spiritus carries. All three fights run regardless of earlier outcomes.", "",
        "| Skill / cost | Enter F1/F2/F3 | Leave F1/F2/F3 | Focal spend F1/F2/F3 | D F1/F2/F3 | Compound F1/F2/F3 | Basic Parry F1/F2/F3 | Counter F1/F2/F3 | Unaffordable compounds F1/F2/F3 | Advanced Plays F1/F2/F3 | Unused after F3 |", "|---|---|---|---|---|---|---|---|---|---|---:|",
    ]
    for label, item in sorted(data["sequences"].items()):
        c = item["cell"]
        n = item["sequences"]
        focal = item["focal_metrics"]
        join = lambda values: "/".join(f"{value:.2f}" for value in values)
        metric = lambda key: "/".join(f"{f[key]/n:.3f}" for f in focal)
        choice = lambda key: "/".join(f"{f['choices'].get(key,0)/n:.3f}" for f in focal)
        lines.append(
            f"| {c['skill_a']} / C{c['compound_cost']} | {join(item['entering_spiritus_mean'])} | {join(item['leaving_spiritus_mean'])} | {metric('spiritus_spent')} | {metric('durch_declarations')} | {metric('compound_declarations')} | {choice('Basic Parry')} | {choice('Counter')} | {metric('compound_unaffordable_opportunities')} | {metric('learned_play_declarations')} | {item['unused_spiritus_after_fight_3_mean']:.2f} |"
        )

    lines += [
        "", "| Skill / cost | Enter F2: 0 / 1 / 2 / 3–5 / 6–8 | Enter F3: 0 / 1 / 2 / 3–5 / 6–8 | F2 only D1, not C2 | F3 only D1, not C2 | F2 neither paid | F3 neither paid |", "|---|---|---|---:|---:|---:|---:|",
    ]
    for label, item in sorted(data["sequences"].items()):
        c = item["cell"]
        bucket = lambda index: " / ".join(pct(item["entering_buckets"][index][key]) for key in ("0", "1", "2", "3-5", "6-8"))
        f2, f3 = item["focal_metrics"][1], item["focal_metrics"][2]
        lines.append(
            f"| {c['skill_a']} / C{c['compound_cost']} | {bucket(1)} | {bucket(2)} | {pct(sequence_state_rate(f2,'1'))} | {pct(sequence_state_rate(f3,'1'))} | {pct(sequence_state_rate(f2,'0'))} | {pct(sequence_state_rate(f3,'0'))} |"
        )

    lines += [
        "", "C2 produces useful, non-catastrophic attrition. After Fight 3, focal Spiritus averages 5.93 / 4.42 / 3.47 at Skills 10 / 14 / 18, compared with C1's 6.14 / 5.15 / 4.48. Compounds remain present in Fight 3 at 0.380 / 0.494 / 0.539 uses per focal fighter under C2, and total learned-Play use remains above 1.1 per fight. Skill-18 C2 is the strongest attrition case: 57.9% enter Fight 3 at 3–5 or less, but sophisticated fencing does not disappear. Only-D1 windows reach 6.5% of focal Fight-3 exchanges and neither-paid windows 1.3%; these thresholds are visible without becoming dominant starvation.", "",
        "## Play-chain regression", "",
        "| Cost | Mean learned-Play chain | Three-Play chains/fight | Attempted fourth/fight |", "|---:|---:|---:|---:|",
    ]
    for cost in (1, 2):
        selected = [item["metrics"] for item in items if item["cell"]["compound_cost"] == cost]
        lines.append(
            f"| C{cost} | {mean(m['average_learned_play_chain_length'] for m in selected):.3f} | {mean(m['three_play_chains_per_fight'] for m in selected):.4f} | {mean(m['attempted_fourth_plays_per_fight'] for m in selected):.4f} |"
        )

    lines += [
        "", "C2 modestly shortens learned-Play chains and reduces three-Play chains; no attempted fourth Play occurred. The current cap and Schielhau intrinsic-branch treatment remain unchanged.", "",
        "## Answers to the required questions", "",
        "A. **Yes, provisionally.** C2 better reflects the two-effect compound chassis because it adds real reserve thresholds while leaving the Plays common at healthy Spiritus.",
        "B. **Yes.** At C2, 59.5%–82.9% of start-8 fights contain a compound; Skill 14–18 C2 still uses 1.0–1.4 compounds per fresh fight.",
        "C. **Yes, especially Schielhau.** Under C1, healthy expert Schielhau declaration reaches roughly 85%–92% of legal opportunities, and aggregate compounds resolve more than half of defensive opportunities in many cells.",
        "D. **Yes.** At 1 Spiritus C2 compounds are unavailable while D1 remains; at 2 they are legal but expensive enough to be chosen selectively.",
        "E. **Yes.** D1 remains usable at the 1-Spiritus tier and continues appearing throughout C2 fresh and sequence cells.",
        "F. **Partially.** Under adaptive revelation at Skill 18 / start 3, known-D Basic Parry rises as high as 14.1% at Spiritus 2 and 19.4% at 0, but under perfect information it remains only 2.1% at 1 because D1 is still available.",
        "G. **Mostly intended expert progression, with the prior P1 warning preserved.** Compound use falls and Counter takes over; P1 itself remains suppressed by known D1 rather than by C2.",
        "H. **Yes.** C2 makes 8 more operationally meaningful, especially at Skills 14–18, by converting it into several costly commitments rather than an almost untouched reserve.",
        "I. **Yes.** C2 materially deepens R0 attrition at Skills 14–18 without producing general starvation.",
        "J. **Yes.** Compounds remain visible in both later fights and reach 0.380–0.539 focal uses in Fight 3 under C2.",
        "K. **Schielhau appears cheapest relative to its modeled opportunity.** It remains much more likely than either thrust counter because it is the sole compound on its trigger and competes with the artifactually free Zornhau-Ort. Absetzen and Scambiar are mechanically indistinguishable here.",
        "L. **A common C2 price is defensible for the next prototype.** Differentiated prices may be needed later if distinct triggers, damage, Guards, or geometry separate their actual value.",
        "M. **Substantial artifact risk remains.** The conclusions are conditional on one-roll Variant A, generic d6+1 damage, the artificial attack mix, heuristic softmax utilities, free Zornhau-Ort/Nachreisen/Pommel, unresolved Guards and Power Strike, 50% soft-bind and 25% close-crossing calibration, and absent engagement geometry.", "",
        "## Artifacts, limitations, and OPEN questions", "",
        "- The policy is not a solved equilibrium and its utility classifications are not psychological claims.",
        "- Absetzen and Scambiar are offered together on the same modeled thrust state with identical mechanics. Their individual probabilities cannibalize one another and cannot support differentiated pricing.",
        "- Schielhau has a single compound slot on its trigger and an S2 rejoinder; comparison to either thrust option is not apples-to-apples.",
        "- Generic d6+1 damage overstates chassis sameness and may distort urgency, especially for pommel and thrust/cut differences.",
        "- Artificial attack proportions determine opportunity counts. Adaptive Schielhau revelation also changes the attack mix.",
        "- Zornhau-Ort, Nachreisen, and Pommel Strike remain free provisional exercise mechanics. Substitution toward them is not a pricing recommendation.",
        "- Guard economy is unresolved, so Power Strike competition remains unmodeled.",
        "- Bind softness, close-crossing frequency, engagement geometry, reach, weapon profiles, and outnumbering access remain unresolved.",
        "- Final compound cost, Spiritus maximum/recovery, other Play prices, tiers, and card text remain OPEN.", "",
        "## Recommended Next Decision", "",
        "Use **C2** as the better next **PROVISIONAL** prototype price for Absetzen, Scambiar di Punta, and Schielhau. Keep all three at a common 2-Spiritus price for now: the current shared Variant A chassis supports a common test price, while the model is too abstract to justify individual prices. Treat the **0 / 1 / 2** hierarchy as useful: 0 leaves basic/free fencing, 1 preserves D1 conversion, and 2 makes compound defence-and-offence credible but costly. Maximum Spiritus **8** becomes more meaningful under C2, particularly across three R0 fights and at expert skill, without preventing later-fight compounds.", "",
        "No further pricing-only simulation is needed before moving to another subsystem. The next useful work is to mature one of the missing competitors or value drivers—preferably Guard/Power Strike economy or engagement geometry—then rerun C2 as a regression. Do not update Atra Melee Design Packet v0.4 and do not promote C2 beyond PROVISIONAL on this evidence.", "",
    ]
    return "\n".join(lines)


def main() -> None:
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    REPORT_PATH.write_text(build_report(data) + "\n", encoding="utf-8")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()

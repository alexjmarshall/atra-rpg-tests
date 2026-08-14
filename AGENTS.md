# AGENTS.md — Atra RPG

## Project purpose

Atra is a historically informed tabletop RPG combat-design project.

This repository contains:
- design documentation
- historical Play research records
- source audits
- prototype combat mechanics
- simulation and solver code
- experimental reports

Treat the repository as the durable source of truth.
Do not rely on assumptions from previous Codex chats.

## Governing principles

1. Do not silently resolve unresolved design questions.

2. Preserve status distinctions:
   - ADOPTED
   - HISTORICALLY ACCEPTED
   - PROVISIONAL
   - OPEN
   - REJECTED

3. Historical evidence and game mechanics are separate.
   A historically accepted technique does not imply that its
   provisional game mechanics are accepted.

4. Later reports supersede earlier experimental assumptions only
   where they explicitly say so.

5. Do not promote PROVISIONAL mechanics to ADOPTED unless the task
   explicitly instructs you to do so.

6. Do not invent historical evidence, source locators, translations,
   or witnesses.

7. When historical evidence is incomplete or uncertain, preserve the
   uncertainty explicitly.

8. Avoid filling missing Play fields by inference unless the task
   explicitly asks for reconstruction.

## Current source policy

The primary campaign horizon is the 1490s.

Use the project's documented source policy rather than assuming that
all HEMA material is equally admissible.

Broad categories include:
- direct-period evidence
- continuity evidence
- earlier persistent traditions
- later preservation witnesses
- reconstruction
- imported material

Historical confidence and date/inclusion basis are separate fields.

Read the current source-policy document before modifying historical
Play records.

## Melee design workflow

Before changing melee mechanics:

1. Read the current melee design packet.
2. Read any later reports named by the task.
3. Inspect the current implementation rather than assuming an older
   report still describes it.
4. Check git status before editing.
5. Keep unrelated mechanics unchanged.
6. Run relevant validation/tests after edits.
7. Report conflicts rather than silently reconciling them.

## Repository roles

Use the repository's actual paths if they differ from these examples.

- `docs/`
  Governing design documentation and design packets.

- `data/` or `data/plays/`
  Structured Play and historical research records.

- `reports/`
  Audits, experiments, simulation reports, and analysis.
  Reports are evidence for design decisions, not automatically canon.

- `simulations/`
  Prototype combat simulators and experimental models.

- `tests/`
  Validation and regression tests.

Before a task, locate the relevant current files rather than assuming
these names or paths.

## Play-record discipline

Keep these concepts distinct:

- Skill = transferable motor competence / rolled skill
- Curriculum = historical instructional cluster
- Equipment = physical requirements
- Guard = tactical posture
- Play = learned technique
- Exchange role = how a Play functions in a particular exchange

Do not conflate tactical identity with exchange role.

Where supported by the schema, preserve:
- exact source
- date
- locator
- inclusion basis
- historical confidence
- reconstruction notes
- test skill
- equipment requirements
- tactical lesson
- mechanics status

## Current prototype caution

Several melee mechanics remain experimental.

In particular, do not assume without checking the latest report:
- Spiritus costs
- Spiritus recovery
- Basic Parry taxonomy
- bind mechanics
- point-threat states
- engagement geometry
- Play-chain architecture
- final tiers
- final card wording

When a task concerns one of these, identify the latest governing
experiment/report first.

## Simulations

Simulation results are exploratory unless explicitly promoted.

When changing a simulator:
- preserve reproducible seeds where practical
- document policy assumptions
- distinguish rule effects from AI-policy artifacts
- do not tune mechanics merely to obtain a desired result
- preserve comparison/control variants where requested
- emit machine-readable results when the task requests them

Do not interpret a Monte Carlo result as historical evidence.

## Historical research

For historical records:
- prefer exact audited evidence
- preserve source wording/meaning without embellishment
- distinguish direct support from geometric inference
- distinguish reconstruction from named historical Plays
- never convert an inference into a direct historical claim

## Editing discipline

Make bounded changes.

Do not:
- mass-edit unrelated Plays
- populate unknown fields across the catalog by guesswork
- rewrite governing documents unless explicitly requested
- change status labels merely because an experiment looks promising

If the requested change conflicts with current repository documentation,
flag the conflict in the final report.

## Validation

After changes:
- run relevant schema validation
- run relevant tests
- run requested simulations
- report failures or skipped checks clearly

Do not conceal failed validations.

## Final task report

For substantive tasks, summarize:

- files changed
- tests/validation run
- simulation runs performed
- important findings
- unresolved questions
- any repository/prompt conflicts
- recommended next decision, if requested

Do not automatically turn recommendations into canonical rules.
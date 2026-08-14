# Atra melee research repository

This repository treats `Atra_Melee_Design_Packet_v0.5.docx` and `docs/melee-design-packet-v0.5.md` as the current governing-provisional vertical-slice record. Version 0.4 remains preserved as its historical predecessor. The repository preserves all 114 current Play candidates as research records, not finished mechanics.

Key rules for contributors:

- Do not silently resolve `OPEN` or `PROVISIONAL` questions.
- Keep historical identity/source evidence separate from game implementation.
- Leave unsupported mechanical fields null.
- Add exact source locations and confidence grades only after item-level audit.
- Use reports to expose gaps; do not make validation “green” by inventing data.

The `.yaml` files use JSON-compatible YAML 1.2 syntax. This keeps validation dependency-free while remaining valid YAML.

Legacy repository bootstrap and validation:

`build_research_repository.py` transcribes the preserved v0.4 source and is not the v0.5 packet generator. Do not use it to overwrite the current v0.5 snapshot.

```powershell
python scripts/build_research_repository.py
python scripts/validate_repository.py --write-reports
python -m unittest discover -s tests -v
```

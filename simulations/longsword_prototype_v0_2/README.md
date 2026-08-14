# Mirrored Longsword prototype v0.2

This seeded experiment gives both equal-Skill duelists the same seven-Play repertoire, uses Variant A for Absetzen and Scambiar di Punta, and disables action preservation.

It runs one full-repertoire cell and seven symmetric remove-one ablations. Outputs include per-Play use/damage, action expenditure, fight length, double defeat rate, tactical states, Durchwechseln/Schielhau interaction, chain-length distributions, cap sequences, and attempted fourth Plays.

Run from the repository root:

```powershell
python simulations/longsword_prototype_v0_2/simulate.py
```

The soft-bind and close-crossing probabilities are artificial exercise rates. They must not be used to tune Zornhau-Ort or Pommel Strike.

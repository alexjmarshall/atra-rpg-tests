# Hart/Weich + Upper Winden Loop v0.2

This is an isolated, exact candidate experiment. It subclasses the v0.1
General Bind Information candidate and leaves the authoritative shared engine
unchanged.

Run from the repository root:

```powershell
python -m unittest tests.test_hart_weich_upper_winden_v02 -v
python simulations/hart_weich_upper_winden_v0_2/simulate.py
```

The simulator writes the JSON and Markdown adjudication reports in `reports/`.
No result automatically promotes H2 or edits the Melee Design Packet.

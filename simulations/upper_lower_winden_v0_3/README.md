# Upper / Lower Winden Completion v0.3

Isolated deterministic H3 candidate overlay. It does not modify or promote the
authoritative shared engine.

Run with the repository Python runtime:

```powershell
python -m simulations.upper_lower_winden_v0_3.simulate
python -m unittest tests.test_upper_lower_winden_v03 -v
```

The analysis uses exact roll-under probabilities and forced branches; there is
no Monte Carlo sampling or scalar Spiritus/control utility.


# Public Smoke Test Outputs

Run from the repository root:

```bash
make public-smoke
```

This folder contains the public toy hedge P&L summary and plot:

- `run_public_smoke_test.py`
- `hedge_summary.csv`
- `pnl_hist.png`

The demo validates workflow shape, dependencies, and output format. It is not
intended to reproduce the full 75k/200k-path private research results.

The GitHub public smoke workflow runs this target on Python 3.11.

The private research workflow starts from FX vanilla smile quotes, calibrates a
same-surface Heston-SLV/Rough-SLV setup, simulates large Heston/Rough path
sets, and produces hedge-transfer and XVA diagnostics. This public smoke demo
starts from a small hard-coded toy surface instead.

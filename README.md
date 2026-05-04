# FX Rough-SLV Hedge-Transfer and XVA Diagnostics

This repository contains selected results, figures, methodology notes,
architecture documentation, and a reduced reproducibility demo. The full research
implementation, calibration scripts, Monte Carlo pipeline, and validation logs
remain private and can be reviewed live during a technical interview.

The project tests a desk-relevant model-risk question: can two models fit the
same static FX vanilla volatility surface but still produce materially different
hedge-transfer and exposure-risk behavior?

The diagnostic setup holds the static vanilla surface fixed. The pricing and
hedge model is Heston-SLV. The stressed realized market dynamics are Rough-SLV.
The objective is not to claim that Rough-SLV should replace Heston-SLV as a
production pricer. The objective is to identify where a smooth-vol hedge model
may understate hedge slippage, tail PnL risk, exposure distortion, and
WWR-sensitive XVA impact.

The central hedge result is that Heston-SLV delta-vega hedging earns strong
tail-loss credit in its own Heston-SLV control world, but that credit does not
transfer cleanly under Rough-SLV realized dynamics. The clean hedge-transfer
evidence is concentrated at 1M and 3M.

The XVA extension shows how the same volatility-dynamics misspecification can
propagate into EE, EPE, ENE, and CVA-style wrong-way-risk diagnostics. In the
reported setup, the strongest review-worthy XVA signal appears at 1Y and remains
portfolio- and netting-set dependent.

## Repository contents

- `docs/` — executive summary and watermarked technical paper
- `figures/` — selected final figures
- `results/` — selected result summaries and result manifest
- `demo/` — reduced smoke-test demo
- `src_excerpts/` — selected source-code excerpts
- `DESK_RELEVANCE.md` — desk-facing interpretation
- `REPRODUCIBILITY_NOTE.md` — result provenance and reproducibility scope
- `LIMITATIONS_AND_CONTROLS.md` — limitations and controls

## Use and permissions

Copyright (c) 2026 José Igor Morlanes. All rights reserved.

This repository is not open source. No license is granted for reuse,
redistribution, publication, commercial use, or derivative works without prior
written permission.
# FX Rough-SLV Hedge-Transfer and XVA Diagnostics

This repository is a public evidence pack for a front-office FX volatility and
model-risk diagnostics project.

The project tests a desk-relevant question:

> If two volatility models are anchored to the same static FX vanilla smile
> surface, can hedge-transfer and exposure risk still differ materially?

The diagnostic setup holds the static FX vanilla smile surface fixed. The
pricing and hedge model is Heston-SLV. The stressed realized market dynamics are
Rough-SLV.

The objective is not to claim that Rough-SLV should replace Heston-SLV as a
production pricer. The objective is to quantify where a smooth-vol hedge model
may understate hedge-transfer slippage, tail hedge-loss risk, exposure
distortion, and WWR-sensitive XVA impact under a controlled same-surface
experiment.

Although the common calibration anchor is the FX vanilla smile surface, the
outputs are trade- and portfolio-level:

- hedge-transfer gaps,
- tail hedge-loss deterioration,
- exposure sensitivity,
- incremental WWR impact,
- CVA-style reserve diagnostics,
- netting-set effects.

The project converts a same-surface model-comparison problem into measured desk
diagnostics: where hedge-transfer credit survives, where tail hedge loss
deteriorates, where exposure timing shifts, and how large the commercial gap is
for WWR-sensitive CVA-style reserve discussion.

The central hedge result is that Heston-SLV delta-vega hedging earns strong
tail-loss credit in its own Heston-SLV control world, but that credit does not
transfer cleanly under Rough-SLV realized dynamics. The clean hedge-transfer
evidence is concentrated at 1M and 3M.

The XVA extension quantifies how the same volatility-dynamics misspecification
can propagate into tail exposure, incremental WWR delta, and CVA-style reserve
diagnostics. In the reported setup, the strongest review-worthy XVA signal
appears at 1Y and remains portfolio- and netting-set dependent.

This repository is a public evidence pack for technical interview discussion. It contains selected result summaries, figures, methodology notes, source-code excerpts, and a reduced reproducibility demo.

The full research implementation, Monte Carlo pipeline, frozen hedge surfaces, seed packs, pathwise hedge P&L arrays, and validation logs are not released publicly. They can be discussed during a technical interview.

## Repository contents
- `docs/` — public project teaser
- `figures/` — selected final figures
- `results/` — selected result summaries and result manifest
- `demo/` — lightweight executable toy example illustrating the hedge-transfer diagnostic logic
- `src_excerpts/` — selected Python and C++ source-code excerpts
- `DESK_RELEVANCE.md` — desk-facing interpretation
- `REPRODUCIBILITY_NOTE.md` — result provenance and reproducibility scope
- `LIMITATIONS_AND_CONTROLS.md` — limitations and controls
## Use and permissions

Copyright (c) 2026 José Igor Morlanes. All rights reserved.
This repository is not open source. No license is granted for reuse,
redistribution, publication, commercial use, or derivative works without prior
written permission.

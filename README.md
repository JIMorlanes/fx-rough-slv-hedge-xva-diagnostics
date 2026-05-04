# FX Rough-SLV Hedge-Transfer and XVA Diagnostics

This is a public companion repository for a private FX volatility diagnostics
project.

The project tests whether the same static FX vanilla volatility surface can still
produce different hedge-transfer and exposure-risk behavior when the pricing and
hedge model is Heston-SLV but the stressed realized market dynamics are Rough-SLV.

The central hedge result is that Heston-SLV delta-vega hedging earns strong
tail-loss credit in its own Heston-SLV control world, but that credit does not
transfer cleanly under Rough-SLV realized dynamics. The clean hedge evidence is
concentrated at 1M and 3M.

The XVA extension shows how the same volatility-dynamics misspecification can
propagate into EE/EPE/ENE and CVA-style WWR diagnostics, with the strongest
review-worthy signal appearing at 1Y.

This public repository contains selected results, figures, methodology notes,
architecture documentation, and a reduced reproducibility demo. The full research
implementation and production-scale result-generation pipeline are private and
may be reviewed live during a technical interview.

## Use and permissions

Copyright (c) 2026 José Igor Morlanes. All rights reserved.

This repository is not open source. No license is granted for reuse,
redistribution, publication, commercial use, or derivative works without written
permission.

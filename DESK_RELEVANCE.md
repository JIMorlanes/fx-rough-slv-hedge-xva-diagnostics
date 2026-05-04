
# Desk Relevance
## Desk question
If two models are calibrated to the same static FX vanilla surface, can hedge and exposure risk still differ materially?
## Diagnostic answer
Yes. The same static surface can hide materially different realized variance timing, hedge-transfer behavior, tail hedge-loss behavior, and WWR-sensitive exposure profiles.
## Why this matters to the desk
### Hedge PnL
A delta-vega hedge can earn strong tail-loss credit in the model's own control world and still fail to transfer under stressed realized dynamics.
That matters because hedge credit is only useful if it survives outside the model used to compute the Greeks.
### Risk limits
A book can look controlled under the pricing model while still showing different tail behavior under a stressed realized-dynamics layer.
That matters for monitoring, escalation, and deciding where model-risk overlays are needed.
### XVA and exposure
Similar static price calibration does not guarantee similar exposure timing or WWR-sensitive CVA-style behavior.
That matters because exposure risk is path-dependent and portfolio-specific, not only a function of the initial vanilla smile fit.
### Product attribution
The XVA signal can be concentrated in specific legs of a netting set. In the controlled portfolio, the forward-start leg is the positive timing channel, while the short down-and-out call offsets part of the signal.
That matters because desk action depends on which trades drive exposure timing, not only on the aggregate CVA number.
## Intended users
- FX front-office quants,
- strats,
- XVA quants,
- model risk,
- traders managing short-dated or path-sensitive FX books.
## Intended output
The framework produces desk-usable diagnostics:
- hedge-transfer tables by maturity,
- delta-only versus delta-vega tail-loss comparison,
- hedge-frequency convergence checks,
- surface validation and path-usage checks,
- exposure profiles,
- PFE / EE / EPE / ENE diagnostics,
- CVA-style WWR sensitivity,
- product-level attribution under netting.
## What this is not
This is not a universal replacement pricer.
This is not a claim that Rough-SLV must replace Heston-SLV.
This is not a regulatory capital model.
It is a desk-facing diagnostic overlay for identifying where the same static FX surface may hide different hedge, exposure, and XVA risk.
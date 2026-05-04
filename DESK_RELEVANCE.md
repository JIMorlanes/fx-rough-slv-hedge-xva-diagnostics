# Desk Relevance

## 1. Hedge-transfer question

### Desk question

If the hedge model is calibrated to the same static FX vanilla smile surface, does its delta-vega hedge credit still transfer when realized market dynamics are rougher than the pricing model assumes?

### Diagnostic answer

Not necessarily. In this project, the Heston-SLV delta-vega hedge earns strong ES tail-loss credit in its own Heston-SLV control world, but that credit does not transfer cleanly when the realized market layer is Rough-SLV. The clean hedge-transfer evidence is concentrated at 1M and 3M.

### Why this matters to the desk

The desk issue is not whether Heston-SLV fits today’s vanilla smile. The issue is whether Greeks computed from a smooth-vol model still protect the book when realized variance timing and path dynamics differ from the model used to compute the hedge.

A delta-vega hedge can look effective in the model-control world and still fail to transfer under stressed realized dynamics. That matters because hedge credit is only useful if it survives outside the model used to compute the Greeks.

## 2. XVA / exposure question

### Desk question

If two volatility-dynamics assumptions are anchored to the same initial FX vanilla smile surface, can they still produce different tail exposure, WWR-sensitive CVA, and netting-set reserve diagnostics?

### Diagnostic answer

Yes. Static smile agreement does not force agreement on future exposure timing, tail exposure, wrong-way-risk sensitivity, or netting-set reserve impact. In this project, the XVA signal is low-materiality at 1M, monitor-worthy at 3M, and review-worthy at 1Y.

### Why this matters to the desk

The desk issue is not only initial price calibration. XVA is path-dependent. A model can look acceptable on the opening smile and still generate different exposure profiles once future variance states, spot/vol co-movement, product optionality, and netting effects are simulated.

The paper’s XVA result is not that average exposure explodes. The point is sharper: broad EE can remain similar while PFE95, incremental WWR delta, and CVA-style reserve diagnostics move enough to justify monitoring or model-review escalation.

## 3. Common diagnostic principle

The common principle is simple: the static vanilla smile surface is not enough. It pins down today’s smile fit, but it does not fully determine hedge-transfer performance or exposure dynamics under realized market stress.

The project therefore treats Heston-SLV as the pricing and hedge model, Rough-SLV as the stressed realized market layer, and the common FX vanilla smile surface as the controlled input.

The framework quantifies the difference between what the common static smile fit suggests and what the desk actually cares about: hedge-transfer performance, tail hedge-loss behavior, exposure timing, WWR sensitivity, and netting-set impact.

The measured outputs are hedge-transfer gap, tail hedge-loss deterioration, tail exposure gap, incremental WWR delta, and CVA-style reserve sensitivity.

The purpose is not to show that models differ. The purpose is to measure where
the difference becomes commercially relevant: hedge-transfer failure, tail
hedge-loss deterioration, exposure timing shifts, WWR sensitivity, and
netting-set reserve impact.

## 4. Product attribution

The XVA signal can be concentrated in specific legs of a netting set. In the controlled portfolio, the forward-start leg is the main positive timing channel, while the short down-and-out call offsets part of the signal under netting.

This is important because the desk action is not “change the whole model.” The desk action is to identify which products, maturities, and netting-set structures create model-risk sensitivity under alternative realized volatility dynamics.

## 5. Desk action

The framework is a diagnostic overlay, not a replacement pricer.

It supports:

- quantifying hedge-transfer gaps between control-world and stressed-realized dynamics,
- measuring tail hedge-loss deterioration by maturity,
- separating control-world hedge benefit from stressed-realized hedge performance,
- checking whether exposure profiles are sensitive to volatility-dynamics assumptions,
- quantifying PFE95, incremental WWR delta, and CVA-style reserve sensitivity under alternative realized dynamics,
- attributing XVA signal to product legs and netting effects,
- deciding where model-risk overlays, hedge controls, or further review are justified.

## 6. What this is not

This is not a claim that Rough-SLV should replace Heston-SLV as the production pricing model.

This is not a universal statement about all FX books, all maturities, or all hedge instruments.

This is not a regulatory capital model.

This is a controlled desk-facing diagnostic showing that the same static FX vanilla smile surface can hide materially different hedge-transfer and exposure-risk behavior.

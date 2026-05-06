# XVA Assumptions

## Purpose

The XVA extension tests whether volatility-model misspecification propagates
from hedge-transfer risk into exposure timing, WWR-sensitive diagnostics, and
CVA-style reserve materiality.

The objective is not to build a full regulatory XVA stack. The objective is to
isolate whether the same static FX vanilla surface can still produce materially
different exposure and reserve-style diagnostics under different realized
volatility dynamics.

## Exposure definitions

Portfolio exposure is computed from simulated future portfolio values.

```text
EE(t) = E[max(V(t), 0)]
ENE(t) = E[max(-V(t), 0)]
PFE95(t) = 95% quantile of max(V(t), 0)
```

## EPE definition

EPE is the time-averaged positive exposure over the exposure grid.

## CVA-style metric

The CVA-style metric is used as a reserve-sensitivity diagnostic, not as a full
production CVA calculation.

It measures whether volatility-dynamics misspecification can move
reserve-relevant exposure measures enough to justify desk monitoring or model
review.

## WWR perturbation

WWR sensitivity is measured by stressing the dependence between positive
exposure and counterparty credit deterioration.

The reported WWR delta is an incremental diagnostic. It should not be read as a
fully specified counterparty credit model or a production reserve number.

## Netting convention

Reported exposure is portfolio-level after netting across the controlled trade
set.

The controlled netting set contains:

- ATM vanilla
- forward-start ATM option
- short down-and-out call

The forward-start option is the main positive exposure-timing channel. The short
down-and-out call offsets part of that signal through netting.

## Collateral and margin

Collateral, margin period of risk, CSA terms, funding effects, and capital
charges are excluded.

This is deliberate. The experiment isolates volatility-model-driven exposure
timing rather than building a full XVA platform.

## Interpretation

The XVA result should be read as a desk diagnostic.

Broad EE may remain similar across models, while PFE95, WWR-sensitive exposure,
and CVA-style reserve signals move enough to justify monitoring or model review.

The desk implication is not “replace the XVA stack.” The implication is that
volatility-dynamics assumptions can change reserve-relevant exposure timing even
when the static vanilla surface is held fixed.

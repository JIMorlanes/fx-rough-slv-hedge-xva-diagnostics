# Surface Controls

## Purpose

The hedge-transfer and XVA diagnostics hold the static FX vanilla smile surface
fixed. The experiment changes the realized dynamics, not the vanilla calibration
anchor.

This isolates hedge-transfer and exposure model risk. The question is not
whether the model fits today’s vanilla surface. The question is whether hedge
credit, exposure timing, and reserve-style diagnostics survive when the realized
variance dynamics are rougher than the smooth-volatility hedge model assumes.

## Controlled objects

The controlled objects are:

- FX vanilla quote sheet
- eSSVI arbitrage-free total variance surface
- Dupire local-volatility extraction
- Heston-SLV calibration target
- Heston-SLV book surface
- Heston-SLV hedge surface

## Changed object

The realized path generator changes:

- Heston-SLV control world
- Rough-SLV stressed realized world

Everything else is held fixed to avoid mixing surface-calibration effects with
realized-dynamics effects.

## Why this matters

The experiment is not asking whether Rough-SLV reprices the vanilla surface
better. It asks whether hedge credit produced by a smooth-volatility SLV model
transfers when realized variance dynamics are rougher.

The desk implication is direct: a hedge that reduces ES inside the pricing model
should not automatically receive the same stress-risk credit under alternative
realized dynamics.

This control makes the hedge-transfer result interpretable. Because the static surface,
book valuation surface, and hedge surface are held fixed, any residual hedge slippage or 
exposure-profile change is not primarily a vanilla calibration effect. It is evidence of 
volatility-dynamics model risk.

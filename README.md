# FX Rough-SLV Hedge-Transfer and XVA Diagnostics

## Repository Scope

This repository is a reduced public evidence-pack demo for technical interview discussion. 
It is not the full research repository. It contains selected result summaries, figures, methodology notes, 
source-code excerpts, and a reduced reproducibility demo.

The full research implementation, Monte Carlo pipeline, frozen hedge surfaces, seed packs, pathwise 
hedge PnL arrays, and validation logs are maintained separately and are not released publicly. 
The methodology, implementation choices, and validation workflow can be discussed during a technical interview.

## What to look at first

1. `docs/front_office_summary.pdf` — front-office project summary.
2. `figures/` — selected hedge-transfer and XVA figures.
3. `results/hedge_transfer_summary.csv` — main hedge-transfer evidence.
4. `results/xva_materiality_summary.csv` — exposure/XVA materiality evidence.
5. `demo/` — reduced reproducibility smoke test.
6. `src_excerpts/` — selected Python and C++ implementation excerpts.

## One-line result

Under the same static FX vanilla smile surface, Heston-SLV delta-vega hedge
credit is strong in the Heston-SLV control world but does not transfer cleanly
under Rough-SLV realized dynamics; the exposure/XVA signal is strongest at 1Y
and remains netting-set dependent.

## Public smoke test

Run from the repository root:

```bash
make public-smoke
```

This writes a toy hedge P&L summary and plot under
`demo/results/`. The demo validates workflow shape, dependencies,
and output format. It is not intended to reproduce the full 75k/200k-path
private research results.

Run the public tests:

```bash
make test
```

The private research workflow starts from FX vanilla smile quotes, calibrates a
same-surface Heston-SLV/Rough-SLV setup, simulates large Heston/Rough path
sets, and produces hedge-transfer and XVA diagnostics. The public smoke demo
starts from a small hard-coded toy surface instead.

## Project purpose

This repository is a public evidence pack for a front-office FX volatility and
model-risk diagnostics project.

The project tests a desk-relevant question:

> If two volatility models are anchored to the same static FX vanilla smile
> surface, can hedge-transfer and exposure risk still differ materially?

The diagnostic setup holds the static FX vanilla smile surface fixed. The
pricing and hedge model is Heston-SLV. The stressed realized market dynamics are
Rough-SLV.



## Hedge-transfer definition

Hedge-transfer means the fraction of tail-loss reduction achieved by a hedge in
the model-control world that survives when the same hedge is tested under
stressed realized market dynamics.

In this project:

- hedge model: Heston-SLV
- control world: Heston-SLV
- stressed realized world: Rough-SLV
- market calibration anchor: same static FX vanilla smile surface

For each market world, hedge improvement is measured as:

```text
hedge_improvement = (ES_delta_only - ES_delta_vega) / ES_delta_only
```

The transfer ratio is measured as:
```text
transfer_ratio = Rough_SLV_hedge_improvement / Heston_SLV_control_hedge_improvement
```

The objective is not to claim that Rough-SLV should replace Heston-SLV as a
production pricer. The objective is to test whether a smooth-volatility hedge
model may understate hedge-transfer slippage, tail hedge-loss risk, exposure
timing shifts, and WWR-sensitive XVA impact under a controlled same-surface
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

The full research implementation, Monte Carlo pipeline, frozen hedge surfaces, seed packs, pathwise hedge P&L arrays, and validation logs are maintained separately and not released publicly. They can be discussed during a technical interview.

## Repository contents

- `docs/` — front-office summary, XVA assumptions, surface-control notes and architecture
- `figures/` — selected final figures
- `results/` — selected result summaries, metadata, and result manifest
- `demo/` — lightweight executable toy example illustrating the hedge-transfer diagnostic logic
- `src_excerpts/` — selected Python and C++ source-code excerpts
- `DESK_RELEVANCE.md` — desk-facing interpretation
- `REPRODUCIBILITY_NOTE.md` — result provenance and reproducibility scope
- `LIMITATIONS_AND_CONTROLS.md` — limitations and controls

## Use and permissions

This repository is intended for portfolio review, technical interview discussion,
and non-commercial evaluation of the project methodology and selected results.

The public material may be read, cited, and discussed for hiring, research, and
technical review purposes. It may not be copied, repackaged, redistributed, or
used commercially without permission.

The full research implementation, Monte Carlo pipeline, frozen hedge surfaces,
seed packs, pathwise hedge P&L arrays, validation logs, and private raw outputs
are not released publicly. They can be discussed during a technical interview.

All rights are reserved unless a separate written permission is granted.

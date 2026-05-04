# Reproducibility Note

The reported paper results are generated from saved experiment outputs, not from manually typed tables.

The reported figures and tables quantify hedge-transfer gaps, tail hedge-loss deterioration, exposure sensitivity, incremental WWR impact, and CVA-style reserve effects under the controlled same-surface setup.

This public companion repository is designed for portfolio review and technical interview discussion. It provides selected result summaries, figure outputs, methodology notes, validation summaries, and a reduced smoke-test workflow.

The full research implementation, calibration scripts, Monte Carlo pipeline, seed packs, raw outputs, result-generation scripts, and validation logs are not released publicly. They can be reviewed live during a technical interview.

## Reproducibility Scope

This repository shows:

- the experiment structure,
- the provenance of the main reported results,
- selected numerical outputs,
- selected figures,
- methodology and validation notes,
- a reduced smoke-test workflow.

It does not release the full research engine, Monte Carlo path sets, seed packs, raw outputs, result-generation scripts, or full validation logs.

## Reported Experiment Results

The paper results are based on the reported path counts, frozen hedge surfaces, multi-seed checks, and saved validation outputs from the full research implementation.

The public repository includes summary-level evidence sufficient to review the project design, inspect the reported outputs, and discuss the methodology. It is a controlled evidence pack rather than a full engine release.

During a technical interview, the full research implementation can be reviewed live to demonstrate:

- code structure,
- commit history,
- result-generation scripts,
- saved experiment outputs,
- validation logs,
- table and figure generation workflow.

## Implementation Credibility

The full research implementation uses a hybrid Python/C++ architecture: Python for calibration, orchestration, diagnostics, and pybind11 task execution; C++ for the path-parallel Monte Carlo core with OpenMP parallelism. This supports live discussion of implementation choices, runtime trade-offs, validation logs, seed summaries, and result provenance.

## Key Result Provenance

| Paper block | Public evidence file | Source pipeline |
|---|---|---|
| Hedge transfer, 1M and 3M | `results/hedge_transfer_summary.csv` | full `diagnostics/hedge/` pipeline |
| XVA materiality, 1M / 3M / 1Y | `results/xva_materiality_summary.csv` | full `diagnostics/xva/` pipeline |
| XVA seed robustness | `results/xva_seed_metric_summary.csv` | full `diagnostics/xva/` pipeline |
| Product-level attribution | `results/xva_product_attribution_1y.csv` | full `diagnostics/xva/` pipeline |
| Surface validation | summarized in the technical paper | full `diagnostics/surfaces/` pipeline |

## Why the Full Pipeline Is Not Public

The full research implementation contains the complete pricing and simulation engine, calibration workflow, raw experiment outputs, validation logs, and result-generation scripts. It is therefore kept private and is not released under an open-source license.

This repository should be read as a public companion evidence pack: enough to assess the project, inspect the reported outputs, and support technical discussion, while keeping the full research engine and raw pipeline private.
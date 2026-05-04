# Limitations and Controls
This project is a controlled desk-facing framework. It is not a claim that one
volatility model should universally replace another.

## 1. Synthetic market surface
The project uses a controlled FX volatility surface rather than a live bank quote
history.

### Why this is acceptable
The objective is model-risk isolation. The experiment tests whether the same
static vanilla surface can hide materially different hedge-transfer and
exposure-risk behavior under different realized variance dynamics.

### What would improve it
A dated market-snapshot extension using EURCHF, EURUSD, or USDCHF surfaces would
strengthen the empirical desk link.

## 2. 1Y hedge evidence
The clean hedge-transfer evidence is concentrated at 1M and 3M.
The 1Y hedge case is not used as headline hedge evidence. It is treated as a
limitation and appendix-style extension rather than as part of the main hedge
claim.

### Why this is acceptable
The paper does not overclaim the long-end hedge result. The main hedge conclusion
is based on the maturities where the design is cleaner, the hedge surfaces are
validated, and the model-transfer comparison is more controlled.

### What would improve it
A dedicated 1Y hedge experiment with validated long-dated hedge surfaces,
separate convergence checks, and a clean long-dated hedge design.

## 3. Rough-SLV role
Rough-SLV is used as stressed realized market dynamics, not as a proposed
universal replacement pricer.

### Why this is acceptable
The framework is a diagnostic overlay. Its desk purpose is escalation,
monitoring, and model-risk sensitivity analysis, not replacement of the desk
pricing model.

### What would improve it
Empirical roughness calibration from realized FX volatility data and comparison
against dated market regimes.

## 4. Full-pipeline runtime cost
Full Monte Carlo reruns with the private research pipeline are computationally expensive, even with the hybrid Python/C++ implementation, pybind11 task execution, and OpenMP-parallel C++ Monte Carlo kernels.

### Why this is acceptable
The project keeps saved outputs, validation logs, seed summaries, and result provenance. A reduced demo is sufficient for live technical review.

Full reruns are not a reasonable interview requirement because the reported hedge and XVA diagnostics use full path counts, saved validation outputs, multi-seed checks, and full-pipeline result generation. The relevant interview evidence is reproducibility of provenance, not forcing a complete rerun during the interview.

#### What would improve it
A containerized environment and one-click reduced reproduction script would improve public usability.

For larger reruns, the natural engineering extensions would be distributed batch execution and selective GPU acceleration of the Monte Carlo layer. A local multi-GPU workstation could also parallelize independent path batches, maturity runs, seed packs, and product-level exposure jobs.

These are optional scaling improvements, not requirements for assessing the project in an interview.

## 5. Portfolio scope
The XVA extension uses a controlled portfolio and netting set to show the
transmission mechanism.

### Why this is acceptable
The objective is to show how volatility-dynamics misspecification propagates into
exposure, tail clustering, wrong-way-risk sensitivity, and CVA-style diagnostics.

### What would improve it
More desk-realistic product mixes, alternative netting sets, and stress-specific
counterparty scenarios.
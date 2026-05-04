"""
Selected excerpt from the private FX Rough-SLV / Heston-SLV XVA diagnostics
pipeline.

This excerpt is provided for technical review only. It is not the full research
implementation and does not grant reuse rights.
"""

import argparse
import json
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_INPUT_GLOB = "outputs/whitepaper_xva_result_pack_seed*_2k/xva_summary_paper.csv"
DEFAULT_OUTDIR = "outputs/whitepaper_xva_seed_robustness_2k"

METRICS = (
    "PFE gap vs Heston %",
    "WWR delta %",
    "model gap vs Heston %",
)


def seed_from_path(path: str) -> int | None:
    match = re.search(r"seed(\d+)", path)
    return int(match.group(1)) if match else None


def load_seed_outputs(input_glob: str) -> pd.DataFrame:
    frames = []
    for path in sorted(Path(".").glob(input_glob)):
        seed = seed_from_path(str(path))
        df = pd.read_csv(path)
        df["seed"] = seed
        df["source_file"] = str(path)
        frames.append(df)

    if not frames:
        raise FileNotFoundError(f"No XVA seed result files matched: {input_glob}")

    return pd.concat(frames, ignore_index=True)


def stable_positive(values: pd.Series) -> bool:
    finite = values.replace([np.inf, -np.inf], np.nan).dropna()
    return bool(len(finite) > 0 and np.all(finite > 0.0))


def stable_non_negative(values: pd.Series) -> bool:
    finite = values.replace([np.inf, -np.inf], np.nan).dropna()
    return bool(len(finite) > 0 and np.all(finite >= 0.0))


def summarize_metrics(all_rows: pd.DataFrame) -> pd.DataFrame:
    records = []

    for (maturity, model), group in all_rows.groupby(["maturity", "model"], sort=False):
        for metric in METRICS:
            values = group[metric].astype(float)
            records.append({
                "maturity": maturity,
                "model": model,
                "metric": metric,
                "mean": float(values.mean()),
                "std": float(values.std(ddof=1)) if len(values) > 1 else 0.0,
                "min": float(values.min()),
                "max": float(values.max()),
                "n_seeds": int(values.count()),
                "stable_non_negative": stable_non_negative(values),
                "stable_positive": stable_positive(values),
            })

    return pd.DataFrame(records)


def summarize_rough_vs_heston_ordering(all_rows: pd.DataFrame) -> pd.DataFrame:
    records = []

    for (seed, maturity), group in all_rows.groupby(["seed", "maturity"], sort=False):
        heston = group[group["model"] == "Heston-SLV"]
        rough = group[group["model"] == "Rough-SLV"]
        if heston.empty or rough.empty:
            continue

        heston_row = heston.iloc[0]
        rough_row = rough.iloc[0]
        records.append({
            "seed": int(seed) if seed is not None else np.nan,
            "maturity": maturity,
            "rough_pfe_higher": bool(rough_row["PFE95"] > heston_row["PFE95"]),
            "rough_wwr_delta_pct_higher": bool(rough_row["WWR delta %"] > heston_row["WWR delta %"]),
            "rough_wwr_cva_higher": bool(rough_row["CVA with WWR"] > heston_row["CVA with WWR"]),
            "rough_model_gap_pct": float(rough_row["model gap vs Heston %"]),
        })

    return pd.DataFrame(records)


def summarize_maturity_ranking(all_rows: pd.DataFrame) -> pd.DataFrame:
    rough = all_rows[all_rows["model"] == "Rough-SLV"].copy()
    records = []

    for seed, group in rough.groupby("seed", sort=False):
        ordered = group.sort_values("model gap vs Heston %", ascending=False)
        records.append({
            "seed": int(seed) if seed is not None else np.nan,
            "largest_model_gap_maturity": ordered.iloc[0]["maturity"],
            "largest_model_gap_pct": float(ordered.iloc[0]["model gap vs Heston %"]),
        })

    return pd.DataFrame(records)


def write_outputs(
    all_rows: pd.DataFrame,
    metric_summary: pd.DataFrame,
    ordering: pd.DataFrame,
    maturity_ranking: pd.DataFrame,
    outdir: str,
    input_glob: str,
) -> None:
    os.makedirs(outdir, exist_ok=True)

    all_rows.to_csv(os.path.join(outdir, "xva_seed_rows.csv"), index=False)
    metric_summary.to_csv(os.path.join(outdir, "xva_seed_metric_summary.csv"), index=False)
    ordering.to_csv(os.path.join(outdir, "xva_seed_ordering_checks.csv"), index=False)
    maturity_ranking.to_csv(os.path.join(outdir, "xva_seed_maturity_ranking.csv"), index=False)

    payload = {
        "metadata": {
            "input_glob": input_glob,
            "metrics": list(METRICS),
        },
        "metric_summary": metric_summary.to_dict(orient="records"),
        "ordering_checks": ordering.to_dict(orient="records"),
        "maturity_ranking": maturity_ranking.to_dict(orient="records"),
    }
    with open(os.path.join(outdir, "xva_seed_robustness.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize XVA result-pack stability across seed runs.",
    )
    parser.add_argument("--input-glob", default=DEFAULT_INPUT_GLOB)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    all_rows = load_seed_outputs(args.input_glob)
    metric_summary = summarize_metrics(all_rows)
    ordering = summarize_rough_vs_heston_ordering(all_rows)
    maturity_ranking = summarize_maturity_ranking(all_rows)

    write_outputs(
        all_rows=all_rows,
        metric_summary=metric_summary,
        ordering=ordering,
        maturity_ranking=maturity_ranking,
        outdir=args.outdir,
        input_glob=args.input_glob,
    )

    print("\nXVA SEED METRIC SUMMARY\n")
    print(metric_summary.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    print("\nXVA SEED ORDERING CHECKS\n")
    print(ordering.to_string(index=False))

    print("\nXVA MATURITY RANKING BY ROUGH MODEL GAP\n")
    print(maturity_ranking.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    print(f"\nWrote outputs to {args.outdir}")


if __name__ == "__main__":
    main()

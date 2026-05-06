"""
Tiny public hedge smoke test.

This script intentionally does not reproduce production or paper numbers. It
loads a toy implied-vol surface, runs a small Monte Carlo delta hedge, and
writes only a public summary CSV plus one diagnostic plot. It uses normal
public dependencies from the project environment, not private data.

Workflow shape shown by this demo:
  toy surface -> toy paths -> toy hedge P&L -> CSV -> plot

This mirrors the private research workflow at a public-safe scale:
  FX vanilla smile quotes -> same-surface calibration -> Heston/Rough paths
  -> hedge-transfer / XVA diagnostics -> CSVs -> figures

The public smoke demo starts after the quote/calibration stage, from a small
hard-coded toy surface:
  toy surface -> toy paths -> toy hedge P&L -> CSV -> plot

The private workflow uses frozen calibrated surfaces, rough/Heston model
engines, 75k/200k-path seed packs, and raw pathwise objects. Those are not
loaded or reproduced here.
"""

import csv
import math
import os
import random
import tempfile
import time
from pathlib import Path

CACHE_DIR = Path(tempfile.gettempdir()) / "rough_lsv_fx_public_smoke_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(CACHE_DIR))
os.environ.setdefault("XDG_CACHE_HOME", str(CACHE_DIR))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "demo" / "results"
SUMMARY_CSV = RESULTS_DIR / "hedge_summary.csv"
PLOT_PNG = RESULTS_DIR / "pnl_hist.png"


def norm_cdf(x: float) -> float:
    """Standard normal CDF using only math.erf."""

    return 0.5 * (1.0 + math.erf(float(x) / math.sqrt(2.0)))


def load_toy_surface() -> dict[str, list]:
    """Return a small deterministic toy IV surface in absolute vol units."""

    return {
        "maturity_grid": [1.0 / 12.0, 0.25, 0.50],
        "moneyness_grid": [0.85, 1.00, 1.15],
        "iv_grid": [
            [0.205, 0.185, 0.178],
            [0.195, 0.180, 0.174],
            [0.188, 0.176, 0.171],
        ],
    }


def interp_1d(x: float, xp: list[float], fp: list[float]) -> float:
    """Linearly interpolate one value, clipping outside the grid."""

    if x <= xp[0]:
        return float(fp[0])
    if x >= xp[-1]:
        return float(fp[-1])
    for i in range(len(xp) - 1):
        if xp[i] <= x <= xp[i + 1]:
            w = (x - xp[i]) / (xp[i + 1] - xp[i])
            return float((1.0 - w) * fp[i] + w * fp[i + 1])
    return float(fp[-1])


def interp_toy_vol(surface: dict[str, list], tau: float, spot: float, strike: float) -> float:
    """Read an implied vol from the toy surface by maturity and moneyness."""

    tau_grid = surface["maturity_grid"]
    m_grid = surface["moneyness_grid"]
    iv_grid = surface["iv_grid"]

    moneyness = min(max(float(spot) / float(strike), m_grid[0]), m_grid[-1])
    vol_by_tau = [interp_1d(moneyness, m_grid, row) for row in iv_grid]
    tau_clipped = min(max(float(tau), tau_grid[0]), tau_grid[-1])
    return interp_1d(tau_clipped, tau_grid, vol_by_tau)


def black_call_price(spot: float, strike: float, tau: float, rate: float, vol: float) -> float:
    """Black-Scholes call price for the toy ATM European option."""

    if tau <= 0.0 or vol <= 0.0:
        return max(spot - strike, 0.0)
    sqrt_tau = math.sqrt(tau)
    d1 = (math.log(spot / strike) + (rate + 0.5 * vol * vol) * tau) / (vol * sqrt_tau)
    d2 = d1 - vol * sqrt_tau
    return spot * norm_cdf(d1) - strike * math.exp(-rate * tau) * norm_cdf(d2)


def black_delta(spot: float, strike: float, tau: float, rate: float, vol: float) -> float:
    """Black-Scholes delta used by the toy hedge."""

    if tau <= 0.0:
        return 1.0 if spot > strike else 0.0
    sqrt_tau = math.sqrt(tau)
    d1 = (math.log(spot / strike) + (rate + 0.5 * vol * vol) * tau) / (vol * sqrt_tau)
    return norm_cdf(d1)


def simulate_toy_paths(
    surface: dict[str, list],
    *,
    spot0: float,
    strike: float,
    maturity: float,
    rate: float,
    n_paths: int,
    n_steps: int,
    seed: int,
) -> list[list[float]]:
    """Simulate toy spot paths with local vol read from the toy surface."""

    rng = random.Random(int(seed))
    dt = float(maturity) / float(n_steps)
    paths = [[float(spot0) for _ in range(n_paths)]]

    for i in range(n_steps):
        tau = max(float(maturity) - i * dt, dt)
        prev = paths[-1]
        nxt: list[float] = []
        for spot in prev:
            sigma = interp_toy_vol(surface, tau=tau, spot=spot, strike=strike)
            z = rng.gauss(0.0, 1.0)
            nxt.append(spot * math.exp((rate - 0.5 * sigma * sigma) * dt + sigma * math.sqrt(dt) * z))
        paths.append(nxt)

    return paths


def delta_hedge_pnl(
    surface: dict[str, list],
    paths: list[list[float]],
    *,
    strike: float,
    maturity: float,
    rate: float,
) -> tuple[list[float], float]:
    """Run a self-financing delta hedge and return discounted seller P&L."""

    n_steps = len(paths) - 1
    n_paths = len(paths[0])
    dt = float(maturity) / float(n_steps)

    spot0 = float(paths[0][0])
    vol0 = interp_toy_vol(surface, tau=maturity, spot=spot0, strike=strike)
    premium = black_call_price(spot=spot0, strike=strike, tau=maturity, rate=rate, vol=vol0)

    cash = [premium for _ in range(n_paths)]
    stock_pos = [0.0 for _ in range(n_paths)]

    for i in range(n_steps):
        tau = max(float(maturity) - i * dt, 1.0e-8)
        growth = math.exp(rate * dt)
        for j, spot in enumerate(paths[i]):
            vol = interp_toy_vol(surface, tau=tau, spot=spot, strike=strike)
            new_delta = black_delta(spot=spot, strike=strike, tau=tau, rate=rate, vol=vol)
            trade = new_delta - stock_pos[j]
            cash[j] -= trade * spot
            stock_pos[j] = new_delta
            cash[j] *= growth

    discount = math.exp(-rate * maturity)
    pnl: list[float] = []
    for j, spot_t in enumerate(paths[-1]):
        payoff = max(spot_t - float(strike), 0.0)
        terminal_portfolio = cash[j] + stock_pos[j] * spot_t
        pnl.append(discount * (terminal_portfolio - payoff))
    return pnl, premium


def mean(values: list[float]) -> float:
    """Arithmetic mean for a non-empty list."""

    return sum(values) / float(len(values))


def std(values: list[float]) -> float:
    """Population standard deviation for a non-empty list."""

    mu = mean(values)
    return math.sqrt(sum((x - mu) * (x - mu) for x in values) / float(len(values)))


def quantile(values: list[float], q: float) -> float:
    """Nearest-rank quantile, sufficient for this small smoke test."""

    ordered = sorted(values)
    idx = int(round(float(q) * (len(ordered) - 1)))
    return float(ordered[min(max(idx, 0), len(ordered) - 1)])


def summarize_pnl(pnl: list[float], premium: float) -> dict[str, float]:
    """Compute a compact public P&L summary without saving raw paths."""

    q01 = quantile(pnl, 0.01)
    q05 = quantile(pnl, 0.05)
    tail = [x for x in pnl if x <= q01]
    es01 = mean(tail) if tail else q01
    pnl_mean = mean(pnl)
    return {
        "premium": float(premium),
        "mean_pnl": pnl_mean,
        "std_pnl": std(pnl),
        "q01_pnl": q01,
        "q05_pnl": q05,
        "es01_pnl": es01,
        "mean_bps_of_premium": 1.0e4 * pnl_mean / premium,
        "q01_bps_of_premium": 1.0e4 * q01 / premium,
        "es01_bps_of_premium": 1.0e4 * es01 / premium,
    }


def write_summary(row: dict[str, object]) -> None:
    """Write the single public CSV output for the smoke test."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fields = [
        "demo_name",
        "surface",
        "product",
        "maturity",
        "path_count",
        "hedge_steps",
        "seed",
        "premium",
        "mean_pnl",
        "std_pnl",
        "q01_pnl",
        "q05_pnl",
        "es01_pnl",
        "mean_bps_of_premium",
        "q01_bps_of_premium",
        "es01_bps_of_premium",
        "runtime_seconds",
        "status",
    ]
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow(row)


def write_plot(pnl: list[float], premium: float) -> None:
    """Write a small histogram as the single public plot output."""

    pnl_bps = [1.0e4 * x / float(premium) for x in pnl]
    plt.figure(figsize=(7.0, 4.2))
    plt.hist(pnl_bps, bins=40, color="#2f6f73", alpha=0.85)
    plt.axvline(mean(pnl_bps), color="#a23e48", linewidth=1.8, label="mean")
    plt.title("Public Toy Smoke Test P&L")
    plt.xlabel("hedged P&L, bps of premium")
    plt.ylabel("path count")
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(PLOT_PNG, dpi=160)
    plt.close()


def main() -> None:
    """Run the public-safe analogue of the private research pipeline."""

    start = time.perf_counter()

    surface = load_toy_surface()
    config = {
        "spot0": 100.0,
        "strike": 100.0,
        "maturity": 0.25,
        "rate": 0.01,
        "n_paths": 5000,
        "n_steps": 48,
        "seed": 20260506,
    }

    paths = simulate_toy_paths(surface, **config)
    pnl, premium = delta_hedge_pnl(
        surface,
        paths,
        strike=config["strike"],
        maturity=config["maturity"],
        rate=config["rate"],
    )
    stats = summarize_pnl(pnl, premium)
    runtime = time.perf_counter() - start

    row: dict[str, object] = {
        "demo_name": "public_toy_hedge_smoke",
        "surface": "toy_three_by_three_iv_surface",
        "product": "atm_european_call",
        "maturity": config["maturity"],
        "path_count": config["n_paths"],
        "hedge_steps": config["n_steps"],
        "seed": config["seed"],
        "runtime_seconds": round(runtime, 6),
        "status": "PASS",
    }
    row.update({key: round(value, 10) for key, value in stats.items()})

    write_summary(row)
    write_plot(pnl, premium)

    print(f"WROTE: {SUMMARY_CSV}")
    print(f"WROTE: {PLOT_PNG}")
    print(f"runtime_seconds={runtime:.3f}")


if __name__ == "__main__":
    main()

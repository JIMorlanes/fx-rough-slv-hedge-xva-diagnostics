"""
Selected excerpt from the private hedge-transfer diagnostics pipeline.

This excerpt is provided for technical review only. It is not the full research
implementation and does not grant reuse rights.
"""

from __future__ import annotations

import copy
import json
import math
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np

from cpp import hedge_kernel
from diagnostics.common.premiums import compute_heston_slv_vanilla_mc_premium
from hedging.greeks_surface_builder import (
    build_delta_surface_gk_vanilla,
    build_delta_surface_heston_slv_vanilla,
    build_vega_surface_gk_vanilla,
    build_vega_surface_heston_slv_vanilla,
)
from market.heston_slv_market import simulate_market_heston_slv_fxhybrid
from market.rough_slv_market import simulate_market_rough_fxhybrid
from pricing.fx_black import black76_call_price
from utils.calibration_loader import load_calibration
from utils.heston_slv_surface_builders import load_surface3d
from utils.pnl_stats import pnl_stats
from utils.surface_utils import (
    atm_fwd_sigma_from_saved_surface,
    leverage_time_grid_from_calibration,
    slice_leverage_surface,
)

DEFAULT_HEDGE_CALIB_DIR = "workflows/out/calib_heston_steps252_paths200000_seed123"
DEFAULT_ROUGH_CALIB_DIR = "workflows/out/calib_rough_H0.100_M8_lam0.5-500_steps252_paths200000_seed123"
DEFAULT_HESTON_SURFACE_OUT_DIR = os.path.join(
    "outputs",
    "surfaces",
    "paper_spot100_widev75k_heston_slv",
    "surfaces",
)
DEFAULT_HESTON_SURFACE_SPOT_TAG = "spot100_widev75k"
DEFAULT_MAIN_MATURITIES = (0.083333, 0.250000)
DEFAULT_SUPPORT_MATURITIES = (0.083333,)
MAIN_PAPER_RUN_TAG = "paper_main_market_comparison"
SUPPORT_RUN_TAG = "support_control_validation"
OWN_PREMIUM_RUN_TAG_SUFFIX = "without_same_premium"


@dataclass(frozen=True)
class ExperimentConfig:
    market: str
    hedge_model: str
    hedge_calib_dir: str
    market_calib_dir: str
    market_steps: int
    run_tag: str
    own_premium_run_tag_suffix: str
    product: str
    n_paths: int
    n_paths_inner: int
    n_paths_price: int
    seed: int
    seed_price: int
    hedge_steps: tuple[int, ...]
    n_steps_per_year_inner: int
    n_steps_per_year_price: int
    max_workers: int
    shift_ratio: float
    vega_surface_steps_per_year: int
    vega_surface_paths: int
    vega_vol_shift_abs: float
    vega_hedge_strike_mult: float
    multi_vega_hedge_strike_mults: tuple[float, float]
    premium_mode: str
    gk_engine: str
    heston_surface_mode: str
    heston_surface_out_dir: str
    heston_surface_spot_tag: str
    heston_book_surface_tag: str
    heston_hedge_surface_tag: str
    save_hedge_diagnostics: bool
    debug_paths: int

    @property
    def hedge_calib_tag(self) -> str:
        return os.path.basename(os.path.normpath(self.hedge_calib_dir))

    @property
    def market_calib_tag(self) -> str:
        return os.path.basename(os.path.normpath(self.market_calib_dir))

    @property
    def base_diag_dir(self) -> str:
        return os.path.join(
            "diagnostics",
            "out",
            self.product,
            self.market,
            "delta",
            "validation_surface_heston",
            self.run_tag,
        )

    @property
    def own_premium_diag_dir(self) -> str:
        return os.path.join(
            "diagnostics",
            "out",
            self.product,
            self.market,
            "delta",
            "validation_surface_heston",
            f"{self.run_tag}_{self.own_premium_run_tag_suffix}",
        )

    @property
    def plots_dir(self) -> str:
        return os.path.join(self.base_diag_dir, "plots")

    @property
    def own_premium_plots_dir(self) -> str:
        return os.path.join(self.own_premium_diag_dir, "plots")


@dataclass(frozen=True)
class CommonCaseData:
    T: float
    hedge_steps: int
    hedge_calib: dict[str, Any]
    market_calib: dict[str, Any]
    hedge_meta: dict[str, Any]
    S0: float
    r_d0: float
    r_f0: float
    L_max: float
    K_atm: float
    F0T: float
    sigma_hedge: float
    premium_heston_slv: float
    premium_gk: float
    premium_0: float
    S_mkt: np.ndarray
    v_mkt: np.ndarray
    rd_mkt: np.ndarray
    rf_mkt: np.ndarray
    K_grid_s: np.ndarray
    T_grid_s: np.ndarray
    L_TK_s: np.ndarray
    K_hedge_vega: float
    K_hedges_multi: tuple[float, float]


@dataclass(frozen=True)
class GkSurfacePack:
    tau_grid: np.ndarray
    S_grid: np.ndarray
    delta_book: np.ndarray
    vega_book: np.ndarray
    delta_hedge: np.ndarray
    vega_hedge: np.ndarray


@dataclass(frozen=True)
class HestonSurfacePack:
    tau_grid: np.ndarray
    S_grid: np.ndarray
    delta_book: np.ndarray
    vega_book: np.ndarray
    delta_hedge: np.ndarray
    vega_hedge: np.ndarray
    delta_hedge1: np.ndarray
    vega_hedge1: np.ndarray
    delta_hedge2: np.ndarray
    vega_hedge2: np.ndarray
    gamma_book: np.ndarray
    gamma_hedge1: np.ndarray
    gamma_hedge2: np.ndarray


@dataclass(frozen=True)
class HestonSurface3DPack:
    tau_grid: np.ndarray
    v_grid: np.ndarray
    S_grid: np.ndarray
    price_book: np.ndarray
    delta_book: np.ndarray
    vega_book: np.ndarray
    price_hedge: np.ndarray
    delta_hedge: np.ndarray
    vega_hedge: np.ndarray
    book_tag: str
    hedge_tag: str
    book_meta: dict[str, Any]
    hedge_meta: dict[str, Any]


def _parse_int_list(raw: str) -> tuple[int, ...]:
    values = tuple(int(x.strip()) for x in raw.split(",") if x.strip())
    if not values:
        raise ValueError("Expected at least one integer")
    return values


def parse_maturities_from_cli(defaults: tuple[float, ...]) -> list[float]:
    import sys

    if len(sys.argv) > 1:
        return [float(sys.argv[1])]
    return [float(x) for x in defaults]


def _build_base_config_from_env(*, run_tag_default: str) -> ExperimentConfig:
    market = os.environ.get("MARKET", "heston").strip().lower()
    hedge_model = os.environ.get("HEDGE_MODEL", "heston").strip().lower()
    if hedge_model != "heston":
        raise ValueError("Only HEDGE_MODEL=heston is supported")
    if market == "rough":
        market_calib_dir = os.environ.get("MARKET_CALIB_DIR", DEFAULT_ROUGH_CALIB_DIR)
    elif market == "heston":

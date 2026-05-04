"""
Selected excerpt from the private hedge-surface validation pipeline.

This excerpt is provided for technical review only. It is not the full research
implementation and does not grant reuse rights.
"""

"""Basic sanity check for a saved 3D hedge surface.

This script checks the saved price, delta, and vega surfaces before we use them
in hedge runs. It verifies the grid shape, matching grids, finite values, no
negative prices, delta inside [0, 1], and no negative vega.
"""

import json
import os

import numpy as np

from utils.heston_slv_surface_builders import load_surface3d


OUT_DIR = os.environ.get("SURFACE_OUT_DIR", os.path.join("outputs", "surfaces", "out_heston_calib"))
TAG = os.environ.get("SURFACE_TAG", "heston_calib_heston_slv_vanilla_1m_state3d_seed123")
VALIDATION_OUT_DIR = os.environ.get(
    "VALIDATION_OUT_DIR",
    os.path.join("outputs", "surfaces", "validation"),
)
EXPECTED_TAU = int(os.environ.get("EXPECTED_TAU", "50"))
EXPECTED_V = int(os.environ.get("EXPECTED_V", "31"))
EXPECTED_S = int(os.environ.get("EXPECTED_S", "81"))
N_WORST_NODES = int(os.environ.get("N_WORST_NODES", "20"))


def field_summary(name: str, arr: np.ndarray) -> dict:
    arr = np.asarray(arr, dtype=np.float64)
    return {
        "surface_name": name,
        "shape": [int(x) for x in arr.shape],
        "min": float(np.nanmin(arr)),
        "max": float(np.nanmax(arr)),
        "mean": float(np.nanmean(arr)),
        "nan_count": int(np.isnan(arr).sum()),
        "inf_count": int(np.isinf(arr).sum()),
    }


def check_shape(name: str, arr: np.ndarray) -> list[str]:
    issues = []
    shape = tuple(int(x) for x in arr.shape)
    if shape != (EXPECTED_TAU, EXPECTED_V, EXPECTED_S):
        issues.append(
            f"{name}: expected shape {(EXPECTED_TAU, EXPECTED_V, EXPECTED_S)} but got {shape}"
        )
    return issues


def check_price(name: str, arr: np.ndarray) -> list[str]:
    issues = []
    arr = np.asarray(arr, dtype=np.float64)
    if np.nanmin(arr) < -1.0e-10:
        issues.append(f"{name}: negative price min={float(np.nanmin(arr))}")
    return issues


def check_delta(name: str, arr: np.ndarray) -> list[str]:
    issues = []
    arr = np.asarray(arr, dtype=np.float64)
    lo = float(np.nanmin(arr))
    hi = float(np.nanmax(arr))
    if lo < -1.0e-6 or hi > 1.0 + 1.0e-6:
        issues.append(f"{name}: delta out of bounds min={lo} max={hi}")
    return issues


def check_vega(name: str, arr: np.ndarray) -> list[str]:
    issues = []
    arr = np.asarray(arr, dtype=np.float64)
    if np.nanmin(arr) < -1.0e-6:
        issues.append(f"{name}: vega negative min={float(np.nanmin(arr))}")
    return issues


def worst_nodes(
    *,
    name: str,
    arr: np.ndarray,
    tau_grid: np.ndarray,
    v_grid: np.ndarray,
    S_grid: np.ndarray,
    n: int,
    largest: bool = False,
) -> list[dict]:
    arr = np.asarray(arr, dtype=np.float64)
    flat = arr.ravel()
    order = np.argsort(flat)
    if largest:
        order = order[::-1]
    out = []
    for flat_idx in order[: max(0, int(n))]:
        i_tau, i_v, i_S = np.unravel_index(int(flat_idx), arr.shape)
        out.append(
            {
                "surface_name": name,
                "value": float(arr[i_tau, i_v, i_S]),
                "i_tau": int(i_tau),
                "i_v": int(i_v),
                "i_S": int(i_S),
                "tau": float(tau_grid[i_tau]),
                "v": float(v_grid[i_v]),
                "S": float(S_grid[i_S]),
            }
        )
    return out


def neighbor_jump_summary(name: str, arr: np.ndarray) -> dict:
    arr = np.asarray(arr, dtype=np.float64)
    diffs = []
    for axis in range(arr.ndim):
        axis_diff = np.diff(arr, axis=axis).ravel()
        diffs.append(np.abs(axis_diff[np.isfinite(axis_diff)]))
    joined = np.concatenate(diffs) if diffs else np.array([], dtype=np.float64)
    if joined.size == 0:
        return {
            "surface_name": name,
            "mean_abs_neighbor_jump": None,
            "p95_abs_neighbor_jump": None,
            "max_abs_neighbor_jump": None,
        }
    return {
        "surface_name": name,
        "mean_abs_neighbor_jump": float(np.mean(joined)),
        "p95_abs_neighbor_jump": float(np.quantile(joined, 0.95)),
        "max_abs_neighbor_jump": float(np.max(joined)),
    }


def main() -> None:
    os.makedirs(VALIDATION_OUT_DIR, exist_ok=True)

    tau_grid_p, v_grid_p, S_grid_p, price_tau_v_S, meta_price = load_surface3d(
        out_dir=OUT_DIR,
        tag=TAG,
        surface_name="price_tau_v_S",
    )
    tau_grid_d, v_grid_d, S_grid_d, delta_tau_v_S, meta_delta = load_surface3d(
        out_dir=OUT_DIR,
        tag=TAG,
        surface_name="delta_tau_v_S",
    )
    tau_grid_v, v_grid_v, S_grid_v, vega_tau_v_S, meta_vega = load_surface3d(
        out_dir=OUT_DIR,
        tag=TAG,
        surface_name="vega_tau_v_S",
    )

    issues: list[str] = []
    issues.extend(check_shape("price_tau_v_S", price_tau_v_S))
    issues.extend(check_shape("delta_tau_v_S", delta_tau_v_S))
    issues.extend(check_shape("vega_tau_v_S", vega_tau_v_S))
    issues.extend(check_price("price_tau_v_S", price_tau_v_S))
    issues.extend(check_delta("delta_tau_v_S", delta_tau_v_S))
    issues.extend(check_vega("vega_tau_v_S", vega_tau_v_S))

    if not np.array_equal(tau_grid_p, tau_grid_d) or not np.array_equal(tau_grid_p, tau_grid_v):
        issues.append("tau_grid mismatch across saved surface fields")
    if not np.array_equal(v_grid_p, v_grid_d) or not np.array_equal(v_grid_p, v_grid_v):
        issues.append("v_grid mismatch across saved surface fields")
    if not np.array_equal(S_grid_p, S_grid_d) or not np.array_equal(S_grid_p, S_grid_v):
        issues.append("S_grid mismatch across saved surface fields")

    validation = {
        "tag": TAG,
        "out_dir": OUT_DIR,
        "expected_shape": [EXPECTED_TAU, EXPECTED_V, EXPECTED_S],
        "grid": {
            "tau": int(len(tau_grid_p)),
            "v": int(len(v_grid_p)),
            "S": int(len(S_grid_p)),
            "tau_min": float(np.min(tau_grid_p)),
            "tau_max": float(np.max(tau_grid_p)),
            "v_min": float(np.min(v_grid_p)),
            "v_max": float(np.max(v_grid_p)),
            "S_min": float(np.min(S_grid_p)),
            "S_max": float(np.max(S_grid_p)),
        },
        "fields": {
            "price_tau_v_S": field_summary("price_tau_v_S", price_tau_v_S),
            "delta_tau_v_S": field_summary("delta_tau_v_S", delta_tau_v_S),
            "vega_tau_v_S": field_summary("vega_tau_v_S", vega_tau_v_S),
        },
        "neighbor_jumps": {
            "price_tau_v_S": neighbor_jump_summary("price_tau_v_S", price_tau_v_S),
            "delta_tau_v_S": neighbor_jump_summary("delta_tau_v_S", delta_tau_v_S),
            "vega_tau_v_S": neighbor_jump_summary("vega_tau_v_S", vega_tau_v_S),
        },
        "worst_nodes": {
            "lowest_vega": worst_nodes(
                name="vega_tau_v_S",
                arr=vega_tau_v_S,
                tau_grid=tau_grid_p,
                v_grid=v_grid_p,
                S_grid=S_grid_p,
                n=N_WORST_NODES,
            ),
            "highest_vega": worst_nodes(
                name="vega_tau_v_S",
                arr=vega_tau_v_S,
                tau_grid=tau_grid_p,
                v_grid=v_grid_p,
                S_grid=S_grid_p,
                n=N_WORST_NODES,
                largest=True,
            ),
            "lowest_delta": worst_nodes(
                name="delta_tau_v_S",
                arr=delta_tau_v_S,
                tau_grid=tau_grid_p,
                v_grid=v_grid_p,
                S_grid=S_grid_p,
                n=N_WORST_NODES,
            ),
            "highest_delta": worst_nodes(
                name="delta_tau_v_S",
                arr=delta_tau_v_S,
                tau_grid=tau_grid_p,

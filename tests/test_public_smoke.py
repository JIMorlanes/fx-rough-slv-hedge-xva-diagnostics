import math

from demo.run_public_smoke_test import (
    black_call_price,
    black_delta,
    delta_hedge_pnl,
    interp_toy_vol,
    load_toy_surface,
    norm_cdf,
    simulate_toy_paths,
    summarize_pnl,
)


def test_norm_cdf_at_zero():
    assert abs(norm_cdf(0.0) - 0.5) < 1.0e-12


def test_toy_surface_vol_is_positive():
    surface = load_toy_surface()
    vol = interp_toy_vol(surface, tau=0.25, spot=100.0, strike=100.0)
    assert vol > 0.0
    assert 0.05 < vol < 0.50


def test_black_price_and_delta_are_sane():
    price = black_call_price(spot=100.0, strike=100.0, tau=0.25, rate=0.01, vol=0.18)
    delta = black_delta(spot=100.0, strike=100.0, tau=0.25, rate=0.01, vol=0.18)
    assert price > 0.0
    assert 0.0 < delta < 1.0


def test_simulated_paths_shape():
    surface = load_toy_surface()
    paths = simulate_toy_paths(
        surface,
        spot0=100.0,
        strike=100.0,
        maturity=0.25,
        rate=0.01,
        n_paths=100,
        n_steps=12,
        seed=123,
    )
    assert len(paths) == 13
    assert len(paths[0]) == 100
    assert len(paths[-1]) == 100
    assert all(x > 0.0 for x in paths[-1])


def test_delta_hedge_pnl_summary_has_required_fields():
    surface = load_toy_surface()
    paths = simulate_toy_paths(
        surface,
        spot0=100.0,
        strike=100.0,
        maturity=0.25,
        rate=0.01,
        n_paths=200,
        n_steps=12,
        seed=123,
    )
    pnl, premium = delta_hedge_pnl(
        surface,
        paths,
        strike=100.0,
        maturity=0.25,
        rate=0.01,
    )
    summary = summarize_pnl(pnl, premium)
    assert len(pnl) == 200
    assert premium > 0.0
    assert math.isfinite(summary["mean_pnl"])
    assert math.isfinite(summary["std_pnl"])
    assert math.isfinite(summary["es01_pnl"])
    assert "mean_bps_of_premium" in summary

/*
Selected C++ excerpt from the private FX hedge diagnostics implementation.

This excerpt shows a reference Garman-Kohlhagen delta-hedge PnL kernel using
pybind11 arrays and OpenMP parallelization. It is provided for technical review
only. It is not the full Heston-SLV / Rough-SLV research engine and does not
grant reuse rights.

Copyright (c) 2026 José Igor Morlanes. All rights reserved.
*/

/// =========================
/// GK HEDGE MODEL VANILLA PNL
/// =========================
py::array_t<double> compute_delta_hedge_pnl_gk_vanilla_cpp(
    py::array_t<double, py::array::c_style | py::array::forcecast> S_paths,
    py::array_t<double, py::array::c_style | py::array::forcecast> rd_paths,
    py::array_t<double, py::array::c_style | py::array::forcecast> rf_paths,
    double K,
    double T,
    double sigma_hedge,
    double premium_0)
{
    auto S_buf  = S_paths.request();
    auto rd_buf = rd_paths.request();
    auto rf_buf = rf_paths.request();

    if (S_buf.ndim != 2 || rd_buf.ndim != 2 || rf_buf.ndim != 2) {
        throw std::runtime_error("S_paths, rd_paths, rf_paths must have shape (n_steps+1, n_paths)");
    }

    if (rd_buf.shape[0] != S_buf.shape[0] || rd_buf.shape[1] != S_buf.shape[1]) {
        throw std::runtime_error("rd_paths shape mismatch");
    }
    if (rf_buf.shape[0] != S_buf.shape[0] || rf_buf.shape[1] != S_buf.shape[1]) {
        throw std::runtime_error("rf_paths shape mismatch");
    }

    const ssize_t n_steps_plus_1 = S_buf.shape[0];
    const ssize_t n_paths = S_buf.shape[1];

    if (n_steps_plus_1 < 2 || n_paths < 1) {
        throw std::runtime_error("invalid S_paths shape");
    }

    const ssize_t n_steps = n_steps_plus_1 - 1;
    const double dt = T / static_cast<double>(n_steps);

    const double* S_paths_ptr  = static_cast<const double*>(S_buf.ptr);
    const double* rd_paths_ptr = static_cast<const double*>(rd_buf.ptr);
    const double* rf_paths_ptr = static_cast<const double*>(rf_buf.ptr);

    int n_threads_case = (n_steps >= 1000 ? 5 : 4);

    auto idx = [n_paths](ssize_t i, ssize_t j) -> std::size_t{
        return static_cast<std::size_t>(i * n_paths + j);
    };

    auto pnl_out = py::array_t<double>(n_paths);
    auto pnl_buf = pnl_out.request();
    double* pnl_ptr = static_cast<double*>(pnl_buf.ptr);

    #pragma omp parallel for num_threads(n_threads_case)
    for (ssize_t j = 0; j < n_paths; ++j) {
        double cash = premium_0;
        double spot_hedge = 0.0;

        double int_rd = 0.0;

        for (ssize_t i = 0; i < n_steps; ++i) {
            const double t_i = static_cast<double>(i) * dt;
            const double tau = std::max(T - t_i, 1.0e-12);

            const double S_i  = S_paths_ptr[idx(i, j)];
            const double rd_i = rd_paths_ptr[idx(i, j)];
            const double rf_i = rf_paths_ptr[idx(i, j)];

            const double delta_new = gk_delta_scalar(S_i, K, tau, rd_i, rf_i, sigma_hedge);

            const double spot_trade = delta_new - spot_hedge;
            cash -= spot_trade * S_i;
            spot_hedge = delta_new;

            cash *= std::exp(rd_i * dt);
            cash += spot_hedge * S_i * (std::exp(rf_i * dt) - 1.0);

            int_rd += rd_i * dt;
        }

        const double S_T = S_paths_ptr[idx(n_steps, j)];
        const double payoff = std::max(S_T - K, 0.0);
        const double portfolio_T = cash + spot_hedge * S_T;

        const double df_0T_path = std::exp(-int_rd);
        pnl_ptr[j] = df_0T_path * (portfolio_T - payoff);
    }

    return pnl_out;
}

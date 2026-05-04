"""
Selected excerpt from the private hedge-transfer diagnostics workflow.

This excerpt shows the reported market-comparison workflow at a high level.
It is provided for technical review only. It is not the full research engine
and does not grant reuse rights.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed

from diagnostics.hedge.hedge_experiment_core import (
    DEFAULT_MAIN_MATURITIES,
    build_main_paper_config_from_env,
    parse_maturities_from_cli,
    run_main_paper_case,
)


def print_summary_table(data: dict) -> None:
    print(f"steps={data['hedge_steps']}")
    for hedge_key in ("GK_DELTA", "HESTON_SLV_DELTA", "HESTON_SLV_DELTA_VEGA"):
        if hedge_key not in data["results"]:
            continue
        stats = data["results"][hedge_key]
        print(
            f"  {hedge_key:27s}"
            f"mean_bps={stats['mean_bps']:.2f}  "
            f"std_bps={stats['std_bps']:.2f}  "
            f"ES005_bps={stats['es005_bps']:.2f}  "
            f"ES01_bps={stats['es01_bps']:.2f}"
        )
    print()


def main() -> None:
    # Paper-main runner: same static vanilla surface, same Heston-SLV hedge,
    # same premium convention, same normalization; only the realized market changes.
    config = build_main_paper_config_from_env()
    maturities = parse_maturities_from_cli(DEFAULT_MAIN_MATURITIES)

    for T in maturities:
        print(f"\n================ MATURITY T={T:.6f} ================\n")
        print("Running main paper market-comparison vanilla hedge cases\n")

        hedge_results: dict[int, dict] = {}
        if config.max_workers <= 1 or len(config.hedge_steps) == 1:
            for steps in config.hedge_steps:
                hedge_steps = int(steps)
                data = run_main_paper_case(config, T=T, hedge_steps=hedge_steps)
                hedge_results[hedge_steps] = data
                print(f"Finished main paper case: T={T:.6f}, steps={hedge_steps}")
        else:
            with ProcessPoolExecutor(max_workers=config.max_workers) as executor:
                future_to_steps = {
                    executor.submit(run_main_paper_case, config, T=T, hedge_steps=steps): int(steps)
                    for steps in config.hedge_steps
                }
                for future in as_completed(future_to_steps):
                    hedge_steps = future_to_steps[future]
                    data = future.result()
                    hedge_results[hedge_steps] = data
                    print(f"Finished main paper case: T={T:.6f}, steps={hedge_steps}")

        print("\nSummary\n")
        for hedge_steps in sorted(hedge_results.keys()):
            print_summary_table(hedge_results[hedge_steps])

    print("\nAll main paper experiments finished.")
    print(f"Results written to {config.base_diag_dir}")


if __name__ == "__main__":
    main()

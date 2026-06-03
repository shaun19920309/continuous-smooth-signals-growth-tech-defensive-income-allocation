#!/usr/bin/env python3
"""Expanding start-date sensitivity for the joint old/credit policy.

This experiment is the expanding-window counterpart to
run_phase1_rolling_start_date_sensitivity_v1.py.  It keeps the full joint
old/credit parameter grid unchanged and varies only the requested OOS start
date / 63-day block phase.  The goal is to test whether Joint WF Expanding is
sensitive to the first validation date.
"""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import scripts.run_phase1_bond_credit_smooth_policy_v1 as base  # noqa: E402
import scripts.run_phase1_joint_old_credit_policy_v1 as joint  # noqa: E402
import scripts.run_phase1_rolling_start_date_sensitivity_v1 as rolling  # noqa: E402


OUT_DIR = ROOT / "data" / "phase1" / "expanding_start_date_sensitivity_v1"
INPUT_DIR = OUT_DIR / "inputs"
TABLE_DIR = OUT_DIR / "tables"
PLOT_DIR = OUT_DIR / "plots"
REPORT_DIR = OUT_DIR / "reports"

PRIMARY_COST_BPS = 10


def ensure_dirs() -> None:
    for directory in (INPUT_DIR, TABLE_DIR, PLOT_DIR, REPORT_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def expanding_for_start(
    keys: list[tuple[str, str]],
    dates: np.ndarray,
    prepared: dict[tuple[str, str], dict[str, object]],
    start: dict[str, str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    requested = start["requested_start_date"]
    wf, selections = rolling.fast_walk_forward_validation(keys, dates, prepared, requested, "expanding")
    actual_start = pd.to_datetime(wf["date"]).min().date().isoformat()
    method = f"Joint Expanding start {requested}"
    config_id = f"joint_expanding_start_{rolling.start_label(requested)}"
    wf = wf.copy()
    wf["method"] = method
    wf["config_id"] = config_id
    wf["requested_start_date"] = requested
    wf["actual_start_date"] = actual_start
    wf["start_group"] = start["start_group"]
    selections = selections.copy()
    selections["requested_start_date"] = requested
    selections["actual_start_date"] = actual_start
    selections["start_group"] = start["start_group"]
    return wf, selections


def build_start_to_end_summary(expanding_returns: pd.DataFrame, benchmarks: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    data = expanding_returns[expanding_returns["cost_bps"] == PRIMARY_COST_BPS].copy()
    data["date"] = pd.to_datetime(data["date"]).dt.normalize()
    for (requested, actual, group_name, method, config_id), group in data.groupby(
        ["requested_start_date", "actual_start_date", "start_group", "method", "config_id"],
        sort=False,
    ):
        dates = set(group["date"])
        row = {
            "requested_start_date": requested,
            "actual_start_date": actual,
            "start_group": group_name,
            "display_name": "Joint Expanding",
            "method": method,
            "config_id": config_id,
        }
        row.update(rolling.metric_for_group(group))
        rows.append(row)
        bench = rolling.benchmark_slice(benchmarks, dates)
        for (bench_method, bench_config), bench_group in bench.groupby(["method", "config_id"], sort=False):
            bench_row = {
                "requested_start_date": requested,
                "actual_start_date": actual,
                "start_group": group_name,
                "display_name": rolling.BENCHMARK_DISPLAY.get((bench_method, bench_config), bench_method),
                "method": bench_method,
                "config_id": bench_config,
            }
            bench_row.update(rolling.metric_for_group(bench_group))
            rows.append(bench_row)
    return pd.DataFrame(rows)


def build_expanding_only_summary(summary: pd.DataFrame) -> pd.DataFrame:
    rows = summary[summary["display_name"] == "Joint Expanding"].copy()
    return rows.sort_values(["requested_start_date", "start_group"]).reset_index(drop=True)


def build_common_window_summary(expanding_returns: pd.DataFrame, benchmarks: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    expanding = expanding_returns[expanding_returns["cost_bps"] == PRIMARY_COST_BPS].copy()
    expanding["date"] = pd.to_datetime(expanding["date"]).dt.normalize()
    date_sets = [set(group["date"]) for _, group in expanding.groupby(["method", "config_id"], sort=False)]
    common_dates = sorted(set.intersection(*date_sets))
    bench = rolling.benchmark_slice(benchmarks, set(common_dates))
    rows: list[dict[str, object]] = []
    common_parts: list[pd.DataFrame] = []
    for (requested, actual, group_name, method, config_id), group in expanding.groupby(
        ["requested_start_date", "actual_start_date", "start_group", "method", "config_id"],
        sort=False,
    ):
        common_group = group[group["date"].isin(common_dates)].copy()
        common_parts.append(common_group)
        row = {
            "requested_start_date": requested,
            "actual_start_date": actual,
            "start_group": group_name,
            "display_name": f"Joint Expanding {requested}",
            "method": method,
            "config_id": config_id,
        }
        row.update(rolling.metric_for_group(common_group))
        rows.append(row)
    for (bench_method, bench_config), bench_group in bench.groupby(["method", "config_id"], sort=False):
        row = {
            "requested_start_date": "benchmark",
            "actual_start_date": common_dates[0].date().isoformat(),
            "start_group": "benchmark",
            "display_name": rolling.BENCHMARK_DISPLAY.get((bench_method, bench_config), bench_method),
            "method": bench_method,
            "config_id": bench_config,
        }
        row.update(rolling.metric_for_group(bench_group))
        rows.append(row)
        common_parts.append(bench_group)
    return pd.DataFrame(rows), pd.concat(common_parts, ignore_index=True)


def build_fixed_horizon_summary(start_to_end: pd.DataFrame, expanding_returns: pd.DataFrame, benchmarks: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    data = expanding_returns[expanding_returns["cost_bps"] == PRIMARY_COST_BPS].copy()
    data["date"] = pd.to_datetime(data["date"]).dt.normalize()
    for horizon_years in (3, 5):
        horizon_days = int(252 * horizon_years)
        for (group_name, requested, actual, method, config_id), group in data.groupby(
            ["start_group", "requested_start_date", "actual_start_date", "method", "config_id"],
            sort=False,
        ):
            group = group.sort_values("date").head(horizon_days)
            if len(group) < horizon_days:
                continue
            dates = set(group["date"])
            row = {
                "horizon_years": horizon_years,
                "requested_start_date": requested,
                "actual_start_date": actual,
                "start_group": group_name,
                "display_name": "Joint Expanding",
                "method": method,
                "config_id": config_id,
            }
            row.update(rolling.metric_for_group(group))
            rows.append(row)
            bench = rolling.benchmark_slice(benchmarks, dates)
            for (bench_method, bench_config), bench_group in bench.groupby(["method", "config_id"], sort=False):
                bench_row = {
                    "horizon_years": horizon_years,
                    "requested_start_date": requested,
                    "actual_start_date": actual,
                    "start_group": group_name,
                    "display_name": rolling.BENCHMARK_DISPLAY.get((bench_method, bench_config), bench_method),
                    "method": bench_method,
                    "config_id": bench_config,
                }
                bench_row.update(rolling.metric_for_group(bench_group))
                rows.append(bench_row)
    return pd.DataFrame(rows)


def build_selection_stability(selections: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for requested, group in selections.groupby("requested_start_date", sort=False):
        ordered = group.sort_values("test_start")
        counts = ordered["selected_config_id"].value_counts()
        selected = list(ordered["selected_config_id"])
        switches = sum(1 for prev, curr in zip(selected, selected[1:]) if prev != curr)
        rows.append(
            {
                "requested_start_date": requested,
                "actual_start_date": ordered["actual_start_date"].iloc[0],
                "start_group": ordered["start_group"].iloc[0],
                "n_blocks": int(len(ordered)),
                "unique_selected_configs": int(ordered["selected_config_id"].nunique()),
                "switch_count": int(switches),
                "most_frequent_config": counts.index[0],
                "most_frequent_blocks": int(counts.iloc[0]),
                "most_frequent_share": float(counts.iloc[0] / len(ordered)),
            }
        )
    return pd.DataFrame(rows)


def pct(value: float) -> str:
    return "" if pd.isna(value) else f"{value:.2%}"


def num(value: float) -> str:
    return "" if pd.isna(value) else f"{value:.2f}"


def markdown_table(
    df: pd.DataFrame,
    columns: list[str],
    pct_cols: set[str] | None = None,
    num_cols: set[str] | None = None,
    max_rows: int = 40,
) -> list[str]:
    pct_cols = pct_cols or set()
    num_cols = num_cols or set()
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in df[columns].head(max_rows).to_dict("records"):
        values = []
        for col in columns:
            value = row[col]
            if pd.isna(value):
                values.append("")
            elif col in pct_cols:
                values.append(pct(float(value)))
            elif col in num_cols:
                values.append(num(float(value)))
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def write_report(
    start_to_end_joint: pd.DataFrame,
    common_summary: pd.DataFrame,
    fixed_horizon: pd.DataFrame,
    selection_stability: pd.DataFrame,
    common_start: str,
    common_end: str,
) -> Path:
    report = REPORT_DIR / "expanding_start_date_sensitivity_v1_report_en.md"
    common_joint = common_summary[common_summary["display_name"].str.startswith("Joint Expanding")].copy()
    common_bench = common_summary[~common_summary["display_name"].str.startswith("Joint Expanding")].copy()
    start_cagr_min = start_to_end_joint["cagr"].min()
    start_cagr_max = start_to_end_joint["cagr"].max()
    start_sharpe_min = start_to_end_joint["sharpe"].min()
    start_sharpe_max = start_to_end_joint["sharpe"].max()
    common_cagr_min = common_joint["cagr"].min()
    common_cagr_max = common_joint["cagr"].max()
    common_sharpe_min = common_joint["sharpe"].min()
    common_sharpe_max = common_joint["sharpe"].max()
    common_mdd_min = common_joint["max_drawdown"].min()
    common_mdd_max = common_joint["max_drawdown"].max()
    bench_lookup = {row["display_name"]: row for _, row in common_bench.iterrows()}

    lines = [
        "# Expanding Start-Date Sensitivity v1",
        "",
        "This report is the expanding-window counterpart to the rolling start-date sensitivity test. The model, full 1,600-configuration Joint Old/Credit grid, 63-day test block, 10bp transaction cost, and selection score are kept unchanged. Only the requested OOS start date and 63-day block phase are varied.",
        "",
        "Important distinction: this is a start-date sensitivity test, not a parameter-grid sensitivity test. The parameter grid remains full-grid in every run.",
        "",
        "## 1. Tested Start Dates",
        "",
    ]
    lines.extend(markdown_table(pd.DataFrame(rolling.all_requested_starts()), ["start_group", "requested_start_date"], max_rows=20))
    lines += [
        "",
        "## 2. Start-to-End Joint Expanding Results",
        "",
        "Each requested start date is run to the common dataset end. The `actual_start_date` can be later than the requested date when the validation requires the initial training window.",
        "",
    ]
    lines.extend(
        markdown_table(
            start_to_end_joint,
            [
                "requested_start_date",
                "actual_start_date",
                "start_group",
                "start_date",
                "end_date",
                "n_days",
                "cagr",
                "ann_vol",
                "sharpe",
                "max_drawdown",
                "calmar",
                "annual_turnover",
                "avg_g_weight",
                "final_wealth",
            ],
            pct_cols={"cagr", "ann_vol", "max_drawdown", "annual_turnover", "avg_g_weight"},
            num_cols={"sharpe", "calmar", "final_wealth"},
            max_rows=40,
        )
    )
    lines += [
        "",
        "![CAGR and Sharpe by Start Date](../plots/expanding_start_date_cagr_sharpe_bar.png)",
        "",
        "![Max Drawdown and Turnover by Start Date](../plots/expanding_start_date_maxdd_turnover_bar.png)",
        "",
        "## 3. Common-Window Results",
        "",
        f"Common window: `{common_start}` to `{common_end}`. All expanding start-date variants and benchmarks are evaluated on the same dates.",
        "",
    ]
    lines.extend(
        markdown_table(
            common_summary,
            [
                "display_name",
                "requested_start_date",
                "actual_start_date",
                "start_date",
                "end_date",
                "n_days",
                "cagr",
                "ann_vol",
                "sharpe",
                "max_drawdown",
                "calmar",
                "annual_turnover",
                "avg_g_weight",
                "final_wealth",
            ],
            pct_cols={"cagr", "ann_vol", "max_drawdown", "annual_turnover", "avg_g_weight"},
            num_cols={"sharpe", "calmar", "final_wealth"},
            max_rows=40,
        )
    )
    lines += [
        "",
        "![Expanding Start-Date Equity Curves](../plots/expanding_start_date_equity_curves.png)",
        "",
        "![Common-Window Expanding vs Benchmarks](../plots/expanding_start_date_vs_benchmarks_common_window.png)",
        "",
        "## 4. Fixed-Horizon Results",
        "",
    ]
    if fixed_horizon.empty:
        lines.append("No fixed-horizon rows were available.")
    else:
        lines.extend(
            markdown_table(
                fixed_horizon[fixed_horizon["display_name"] == "Joint Expanding"],
                [
                    "horizon_years",
                    "requested_start_date",
                    "actual_start_date",
                    "start_date",
                    "end_date",
                    "n_days",
                    "cagr",
                    "ann_vol",
                    "sharpe",
                    "max_drawdown",
                    "calmar",
                    "annual_turnover",
                    "avg_g_weight",
                    "final_wealth",
                ],
                pct_cols={"cagr", "ann_vol", "max_drawdown", "annual_turnover", "avg_g_weight"},
                num_cols={"sharpe", "calmar", "final_wealth"},
                max_rows=80,
            )
        )
    lines += [
        "",
        "## 5. Parameter Selection Stability",
        "",
    ]
    lines.extend(
        markdown_table(
            selection_stability,
            [
                "requested_start_date",
                "actual_start_date",
                "start_group",
                "n_blocks",
                "unique_selected_configs",
                "switch_count",
                "most_frequent_config",
                "most_frequent_blocks",
                "most_frequent_share",
            ],
            pct_cols={"most_frequent_share"},
            max_rows=40,
        )
    )
    lines += [
        "",
        "## 6. Interpretation",
        "",
        f"- Start-to-end CAGR ranges from `{pct(start_cagr_min)}` to `{pct(start_cagr_max)}` and Sharpe ranges from `{num(start_sharpe_min)}` to `{num(start_sharpe_max)}`. This range is affected by sample-period composition, especially whether the run includes the COVID crash and rebound.",
        f"- On the strict common window `{common_start}` to `{common_end}`, Joint Expanding variants are tighter: CAGR ranges from `{pct(common_cagr_min)}` to `{pct(common_cagr_max)}`, Sharpe ranges from `{num(common_sharpe_min)}` to `{num(common_sharpe_max)}`, and max drawdown ranges from `{pct(common_mdd_min)}` to `{pct(common_mdd_max)}`.",
        f"- On the common window, the Joint Expanding variants are compared only against 50/50 G-D, 100% G, and SPY. The 50/50 benchmark has `{pct(bench_lookup['50/50 G-D Buy & Hold']['cagr'])}` CAGR and `{num(bench_lookup['50/50 G-D Buy & Hold']['sharpe'])}` Sharpe; 100% G has `{pct(bench_lookup['100% G Buy & Hold']['cagr'])}` CAGR and `{num(bench_lookup['100% G Buy & Hold']['sharpe'])}` Sharpe; SPY has `{pct(bench_lookup['SPY Buy & Hold']['cagr'])}` CAGR and `{num(bench_lookup['SPY Buy & Hold']['sharpe'])}` Sharpe.",
        "- Because expanding training uses all prior history, the selected parameter path is usually less volatile than rolling, but it can be more anchored to earlier regimes. This sensitivity test separates that issue from parameter-grid sensitivity.",
        "",
        "## 7. Output Files",
        "",
        f"- Start-to-end summary: `{TABLE_DIR / 'expanding_start_date_sensitivity_v1_start_to_end_summary.csv'}`",
        f"- Common-window summary: `{TABLE_DIR / 'expanding_start_date_sensitivity_v1_common_window_summary.csv'}`",
        f"- Selections: `{TABLE_DIR / 'expanding_start_date_sensitivity_v1_selections.csv'}`",
        f"- Common-window equity curves: `{TABLE_DIR / 'expanding_start_date_sensitivity_v1_common_window_equity_curves.csv'}`",
        "",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def main() -> None:
    ensure_dirs()
    features = base.build_feature_panel()
    features = features[features["date"] >= pd.Timestamp("2016-12-21")].reset_index(drop=True)
    config_grid = joint.generate_config_grid()
    cache = rolling.build_returns_cache_only(features, config_grid)
    keys, dates, prepared = rolling.prepare_cache_arrays(cache)

    starts = rolling.all_requested_starts()
    expanding_parts: list[pd.DataFrame] = []
    selection_parts: list[pd.DataFrame] = []
    for start in starts:
        wf, selections = expanding_for_start(keys, dates, prepared, start)
        expanding_parts.append(wf)
        selection_parts.append(selections)

    expanding_returns = pd.concat(expanding_parts, ignore_index=True)
    selections = pd.concat(selection_parts, ignore_index=True)
    benchmarks = base.static_benchmark_returns(features)

    start_to_end = build_start_to_end_summary(expanding_returns, benchmarks)
    start_to_end_joint = build_expanding_only_summary(start_to_end)
    common_summary, common_returns = build_common_window_summary(expanding_returns, benchmarks)
    fixed_horizon = build_fixed_horizon_summary(start_to_end, expanding_returns, benchmarks)
    stability = build_selection_stability(selections)

    common_plot = common_returns.copy()
    expanding_common = common_plot[common_plot["method"].str.startswith("Joint Expanding start")].copy()
    expanding_common["curve_name"] = expanding_common["requested_start_date"].map(lambda x: f"Expanding {x}")
    benchmark_common = common_plot[common_plot["method"].isin([m for m, _ in rolling.BENCHMARK_DISPLAY])].copy()
    benchmark_common["curve_name"] = benchmark_common.apply(
        lambda row: rolling.BENCHMARK_DISPLAY.get((row["method"], row["config_id"]), row["method"]),
        axis=1,
    )
    common_curve_input = pd.concat([expanding_common, benchmark_common], ignore_index=True)

    common_start = common_summary["start_date"].replace("", np.nan).dropna().min()
    common_end = common_summary["end_date"].replace("", np.nan).dropna().max()

    expanding_curve = expanding_returns[expanding_returns["cost_bps"] == PRIMARY_COST_BPS].copy()
    expanding_curve["curve_name"] = expanding_curve["requested_start_date"].map(lambda x: f"Expanding {x}")
    equity_expanding = rolling.build_equity_curves(expanding_curve, ["curve_name"])
    equity_common = rolling.build_equity_curves(common_curve_input, ["curve_name"])

    rolling.plot_start_metric_bars(
        start_to_end_joint,
        PLOT_DIR / "expanding_start_date_cagr_sharpe_bar.png",
        "cagr",
        "sharpe",
        "Joint Expanding CAGR and Sharpe by Requested Start Date",
    )
    rolling.plot_start_metric_bars(
        start_to_end_joint,
        PLOT_DIR / "expanding_start_date_maxdd_turnover_bar.png",
        "max_drawdown",
        "annual_turnover",
        "Joint Expanding Max Drawdown and Turnover by Requested Start Date",
    )
    rolling.plot_equity_curves(
        equity_expanding,
        PLOT_DIR / "expanding_start_date_equity_curves.png",
        "Joint Expanding Start-Date Equity Curves, Start-to-End",
    )
    rolling.plot_equity_curves(
        equity_common,
        PLOT_DIR / "expanding_start_date_vs_benchmarks_common_window.png",
        "Joint Expanding Start-Date Variants vs Benchmarks, Common Window",
    )

    report = write_report(
        start_to_end_joint,
        common_summary,
        fixed_horizon,
        stability,
        str(common_start),
        str(common_end),
    )

    features.to_csv(INPUT_DIR / "expanding_start_date_sensitivity_v1_feature_panel.csv", index=False, encoding="utf-8-sig")
    expanding_returns.to_csv(TABLE_DIR / "expanding_start_date_sensitivity_v1_returns.csv", index=False, encoding="utf-8-sig")
    selections.to_csv(TABLE_DIR / "expanding_start_date_sensitivity_v1_selections.csv", index=False, encoding="utf-8-sig")
    start_to_end.to_csv(TABLE_DIR / "expanding_start_date_sensitivity_v1_start_to_end_with_benchmarks.csv", index=False, encoding="utf-8-sig")
    start_to_end_joint.to_csv(TABLE_DIR / "expanding_start_date_sensitivity_v1_start_to_end_summary.csv", index=False, encoding="utf-8-sig")
    common_summary.to_csv(TABLE_DIR / "expanding_start_date_sensitivity_v1_common_window_summary.csv", index=False, encoding="utf-8-sig")
    common_returns.to_csv(TABLE_DIR / "expanding_start_date_sensitivity_v1_common_window_returns.csv", index=False, encoding="utf-8-sig")
    fixed_horizon.to_csv(TABLE_DIR / "expanding_start_date_sensitivity_v1_fixed_horizon_summary.csv", index=False, encoding="utf-8-sig")
    stability.to_csv(TABLE_DIR / "expanding_start_date_sensitivity_v1_selection_stability.csv", index=False, encoding="utf-8-sig")
    equity_expanding.to_csv(TABLE_DIR / "expanding_start_date_sensitivity_v1_equity_curves.csv", index=False, encoding="utf-8-sig")
    equity_common.to_csv(TABLE_DIR / "expanding_start_date_sensitivity_v1_common_window_equity_curves.csv", index=False, encoding="utf-8-sig")

    common_joint = common_summary[common_summary["display_name"].str.startswith("Joint Expanding")]
    print(f"Requested starts tested: {len(starts)}")
    print(f"Common window: {common_start} to {common_end}")
    print(f"Common-window CAGR range: {common_joint['cagr'].min():.2%} to {common_joint['cagr'].max():.2%}")
    print(f"Common-window Sharpe range: {common_joint['sharpe'].min():.2f} to {common_joint['sharpe'].max():.2f}")
    print(f"Report: {report}")


if __name__ == "__main__":
    main()

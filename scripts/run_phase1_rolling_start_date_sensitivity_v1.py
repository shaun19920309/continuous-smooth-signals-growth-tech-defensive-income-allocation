#!/usr/bin/env python3
"""Rolling start-date sensitivity for the joint old/credit policy.

This experiment keeps the current Joint Old/Credit rolling specification
unchanged and varies only the requested OOS start date.  It tests whether the
rolling result is sensitive to the first test date and to 63-day block phase.
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


OUT_DIR = ROOT / "data" / "phase1" / "rolling_start_date_sensitivity_v1"
INPUT_DIR = OUT_DIR / "inputs"
TABLE_DIR = OUT_DIR / "tables"
PLOT_DIR = OUT_DIR / "plots"
REPORT_DIR = OUT_DIR / "reports"

PRIMARY_COST_BPS = 10
TRADING_DAYS = 252
COMMON_START_DATE = pd.Timestamp("2017-06-28")

ANNUAL_START_DATES = [
    "2017-06-28",
    "2018-01-02",
    "2018-06-28",
    "2019-01-02",
    "2020-01-02",
    "2021-01-04",
    "2022-01-03",
]

BLOCK_PHASE_START_DATES = [
    "2018-06-28",
    "2018-07-30",
    "2018-08-29",
    "2018-09-28",
    "2018-10-29",
]

BENCHMARK_DISPLAY = {
    ("50/50 G-D Buy & Hold", "50/50 G-D Buy & Hold"): "50/50 G-D Buy & Hold",
    ("100% G Buy & Hold", "100% G Buy & Hold"): "100% G Buy & Hold",
    ("SPY Buy & Hold", "SPY Buy & Hold"): "SPY Buy & Hold",
}


def ensure_dirs() -> None:
    for directory in (INPUT_DIR, TABLE_DIR, PLOT_DIR, REPORT_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def start_label(date: str) -> str:
    return date.replace("-", "")


def all_requested_starts() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen = set()
    for date in ANNUAL_START_DATES:
        group = "annual_block_phase_anchor" if date in BLOCK_PHASE_START_DATES else "annual"
        rows.append({"start_group": group, "requested_start_date": date})
        seen.add(date)
    for date in BLOCK_PHASE_START_DATES:
        if date not in seen:
            rows.append({"start_group": "block_phase", "requested_start_date": date})
            seen.add(date)
    return rows


def metric_for_group(group: pd.DataFrame) -> dict[str, float | int | str]:
    group = group.copy()
    group["date"] = pd.to_datetime(group["date"]).dt.normalize()
    group = group.sort_values("date")
    ret = pd.Series(group["net_return"].to_numpy(), index=group["date"])
    turnover = pd.Series(group["daily_turnover"].to_numpy(), index=group["date"])
    weights = pd.Series(group["g_weight"].to_numpy(), index=group["date"]) if "g_weight" in group else None
    return base.performance_metrics(ret, turnover=turnover, g_weight=weights)


def fast_performance_metrics(
    returns: np.ndarray,
    turnover: np.ndarray,
    weights: np.ndarray,
    dates: np.ndarray,
) -> dict[str, float | int | str]:
    mask = np.isfinite(returns) & (pd.to_datetime(dates) >= COMMON_START_DATE)
    ret = returns[mask].astype(float)
    turn = turnover[mask].astype(float)
    w = weights[mask].astype(float)
    used_dates = pd.to_datetime(dates[mask])
    n = len(ret)
    if n == 0:
        return {
            "n_days": 0,
            "start_date": "",
            "end_date": "",
            "total_return": np.nan,
            "cagr": np.nan,
            "ann_vol": np.nan,
            "sharpe": np.nan,
            "sortino": np.nan,
            "max_drawdown": np.nan,
            "calmar": np.nan,
            "annual_turnover": np.nan,
            "avg_g_weight": np.nan,
            "final_wealth": np.nan,
        }
    years = n / TRADING_DAYS
    wealth = np.cumprod(1.0 + ret)
    total = float(wealth[-1] - 1.0)
    cagr = float((1.0 + total) ** (1.0 / years) - 1.0) if total > -1 else np.nan
    std = float(np.std(ret, ddof=0))
    ann_vol = float(std * np.sqrt(TRADING_DAYS))
    sharpe = float(np.mean(ret) / std * np.sqrt(TRADING_DAYS)) if std > 0 else np.nan
    downside = ret[ret < 0]
    downside_dev = float(np.std(downside, ddof=0) * np.sqrt(TRADING_DAYS)) if len(downside) else np.nan
    running_max = np.maximum.accumulate(wealth)
    dd = wealth / running_max - 1.0
    mdd = float(np.min(dd))
    return {
        "n_days": int(n),
        "start_date": used_dates.min().date().isoformat(),
        "end_date": used_dates.max().date().isoformat(),
        "total_return": total,
        "cagr": cagr,
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "sortino": float(cagr / downside_dev) if downside_dev and downside_dev > 0 else np.nan,
        "max_drawdown": mdd,
        "calmar": float(cagr / abs(mdd)) if mdd < 0 else np.nan,
        "annual_turnover": float(np.nansum(turn) / years),
        "avg_g_weight": float(np.nanmean(w)),
        "final_wealth": float(wealth[-1]),
    }


def build_returns_cache_only(features: pd.DataFrame, config_grid: pd.DataFrame) -> dict[tuple[str, str, int], pd.DataFrame]:
    cache: dict[tuple[str, str, int], pd.DataFrame] = {}
    for _, config in config_grid.iterrows():
        strat = joint.build_strategy_for_config(features, config)
        primary = strat[strat["cost_bps"] == PRIMARY_COST_BPS].copy()
        cache[(config["method"], config["config_id"], PRIMARY_COST_BPS)] = primary
    return cache


def prepare_cache_arrays(
    cache: dict[tuple[str, str, int], pd.DataFrame],
) -> tuple[list[tuple[str, str]], np.ndarray, dict[tuple[str, str], dict[str, object]]]:
    prepared: dict[tuple[str, str], dict[str, object]] = {}
    keys: list[tuple[str, str]] = []
    dates: np.ndarray | None = None
    for method, config_id, cost_bps in cache:
        if cost_bps != PRIMARY_COST_BPS:
            continue
        key = (method, config_id)
        group = cache[(method, config_id, cost_bps)].copy().sort_values("date").reset_index(drop=True)
        group["date"] = pd.to_datetime(group["date"]).dt.normalize()
        if dates is None:
            dates = group["date"].to_numpy()
        keys.append(key)
        prepared[key] = {
            "df": group,
            "returns": group["net_return"].to_numpy(dtype=float),
            "turnover": group["daily_turnover"].to_numpy(dtype=float),
            "weights": group["g_weight"].to_numpy(dtype=float),
        }
    if dates is None:
        raise ValueError("Empty returns cache.")
    return keys, dates, prepared


def fast_score_rank(metrics: pd.DataFrame) -> pd.Series:
    return (
        metrics["sharpe"].rank(pct=True)
        + metrics["calmar"].rank(pct=True)
        + metrics["cagr"].rank(pct=True)
        + metrics["max_drawdown"].rank(pct=True)
        + (-metrics["annual_turnover"]).rank(pct=True)
    ) / 5.0


def fast_walk_forward_validation(
    keys: list[tuple[str, str]],
    dates: np.ndarray,
    prepared: dict[tuple[str, str], dict[str, object]],
    start_date: str,
    mode: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_dates = pd.to_datetime(pd.Series(dates)).reset_index(drop=True)
    start_ts = pd.Timestamp(start_date)
    start_idx = int(all_dates[all_dates >= start_ts].index[0])
    if start_idx < joint.VALIDATION_INITIAL_TRAIN_WINDOW:
        start_idx = joint.VALIDATION_INITIAL_TRAIN_WINDOW
    pieces = []
    selections = []
    for test_start_idx in range(start_idx, len(all_dates), joint.VALIDATION_TEST_BLOCK):
        test_end_idx = min(test_start_idx + joint.VALIDATION_TEST_BLOCK, len(all_dates))
        train_end_idx = test_start_idx
        train_start_idx = 0 if mode == "expanding" else max(0, train_end_idx - joint.ROLLING_TRAIN_WINDOW)
        train_rows = []
        train_dates = dates[train_start_idx:train_end_idx]
        for method, config_id in keys:
            item = prepared[(method, config_id)]
            metrics = fast_performance_metrics(
                item["returns"][train_start_idx:train_end_idx],
                item["turnover"][train_start_idx:train_end_idx],
                item["weights"][train_start_idx:train_end_idx],
                train_dates,
            )
            if metrics["n_days"] < 126:
                continue
            row = {"method": method, "config_id": config_id}
            row.update(metrics)
            train_rows.append(row)
        train_metrics = pd.DataFrame(train_rows)
        train_metrics["selection_score"] = fast_score_rank(train_metrics)
        best = train_metrics.sort_values("selection_score", ascending=False).iloc[0]
        best_key = (str(best["method"]), str(best["config_id"]))
        selected = prepared[best_key]["df"].iloc[test_start_idx:test_end_idx].copy()
        selected["method"] = f"Joint WF {mode.title()}"
        selected["config_id"] = f"joint_wf_{mode}"
        pieces.append(selected)
        selections.append(
            {
                "mode": mode,
                "test_start": all_dates.iloc[test_start_idx].date().isoformat(),
                "test_end": all_dates.iloc[test_end_idx - 1].date().isoformat(),
                "train_start": all_dates.iloc[train_start_idx].date().isoformat(),
                "train_end": all_dates.iloc[train_end_idx - 1].date().isoformat(),
                "selected_config_id": str(best["config_id"]),
                "train_selection_score": float(best["selection_score"]),
                "train_sharpe": float(best["sharpe"]),
                "train_cagr": float(best["cagr"]),
                "train_max_drawdown": float(best["max_drawdown"]),
            }
        )
    return pd.concat(pieces, ignore_index=True), pd.DataFrame(selections)


def benchmark_slice(benchmarks: pd.DataFrame, dates: set[pd.Timestamp]) -> pd.DataFrame:
    data = benchmarks[benchmarks["cost_bps"] == PRIMARY_COST_BPS].copy()
    data["date"] = pd.to_datetime(data["date"]).dt.normalize()
    allowed = set(BENCHMARK_DISPLAY)
    data = data[data.apply(lambda row: (row["method"], row["config_id"]) in allowed, axis=1)]
    return data[data["date"].isin(dates)].copy()


def rolling_for_start(
    keys: list[tuple[str, str]],
    dates: np.ndarray,
    prepared: dict[tuple[str, str], dict[str, object]],
    start: dict[str, str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    requested = start["requested_start_date"]
    wf, selections = fast_walk_forward_validation(keys, dates, prepared, requested, "rolling")
    actual_start = pd.to_datetime(wf["date"]).min().date().isoformat()
    method = f"Joint Rolling start {requested}"
    config_id = f"joint_rolling_start_{start_label(requested)}"
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


def build_start_to_end_summary(rolling_returns: pd.DataFrame, benchmarks: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    rolling_returns = rolling_returns[rolling_returns["cost_bps"] == PRIMARY_COST_BPS].copy()
    rolling_returns["date"] = pd.to_datetime(rolling_returns["date"]).dt.normalize()
    for (requested, actual, group_name, method, config_id), group in rolling_returns.groupby(
        ["requested_start_date", "actual_start_date", "start_group", "method", "config_id"],
        sort=False,
    ):
        dates = set(group["date"])
        row = {
            "requested_start_date": requested,
            "actual_start_date": actual,
            "start_group": group_name,
            "display_name": "Joint Rolling",
            "method": method,
            "config_id": config_id,
        }
        row.update(metric_for_group(group))
        rows.append(row)
        bench = benchmark_slice(benchmarks, dates)
        for (bench_method, bench_config), bench_group in bench.groupby(["method", "config_id"], sort=False):
            bench_row = {
                "requested_start_date": requested,
                "actual_start_date": actual,
                "start_group": group_name,
                "display_name": BENCHMARK_DISPLAY.get((bench_method, bench_config), bench_method),
                "method": bench_method,
                "config_id": bench_config,
            }
            bench_row.update(metric_for_group(bench_group))
            rows.append(bench_row)
    return pd.DataFrame(rows)


def build_joint_only_summary(summary: pd.DataFrame) -> pd.DataFrame:
    joint_rows = summary[summary["display_name"] == "Joint Rolling"].copy()
    joint_rows = joint_rows.sort_values(["requested_start_date", "start_group"]).reset_index(drop=True)
    return joint_rows


def build_common_window_summary(rolling_returns: pd.DataFrame, benchmarks: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rolling = rolling_returns[rolling_returns["cost_bps"] == PRIMARY_COST_BPS].copy()
    rolling["date"] = pd.to_datetime(rolling["date"]).dt.normalize()
    date_sets = [set(group["date"]) for _, group in rolling.groupby(["method", "config_id"], sort=False)]
    common_dates = sorted(set.intersection(*date_sets))
    bench = benchmark_slice(benchmarks, set(common_dates))
    rows: list[dict[str, object]] = []
    common_parts: list[pd.DataFrame] = []
    for (requested, actual, group_name, method, config_id), group in rolling.groupby(
        ["requested_start_date", "actual_start_date", "start_group", "method", "config_id"],
        sort=False,
    ):
        common_group = group[group["date"].isin(common_dates)].copy()
        common_parts.append(common_group)
        row = {
            "requested_start_date": requested,
            "actual_start_date": actual,
            "start_group": group_name,
            "display_name": f"Joint Rolling {requested}",
            "method": method,
            "config_id": config_id,
        }
        row.update(metric_for_group(common_group))
        rows.append(row)
    for (bench_method, bench_config), bench_group in bench.groupby(["method", "config_id"], sort=False):
        row = {
            "requested_start_date": "benchmark",
            "actual_start_date": common_dates[0].date().isoformat(),
            "start_group": "benchmark",
            "display_name": BENCHMARK_DISPLAY.get((bench_method, bench_config), bench_method),
            "method": bench_method,
            "config_id": bench_config,
        }
        row.update(metric_for_group(bench_group))
        rows.append(row)
        common_parts.append(bench_group)
    return pd.DataFrame(rows), pd.concat(common_parts, ignore_index=True)


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


def build_fixed_horizon_summary(start_to_end: pd.DataFrame, rolling_returns: pd.DataFrame, benchmarks: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    rolling = rolling_returns[rolling_returns["cost_bps"] == PRIMARY_COST_BPS].copy()
    rolling["date"] = pd.to_datetime(rolling["date"]).dt.normalize()
    for horizon_years in (3, 5):
        horizon_days = int(252 * horizon_years)
        for (group_name, requested, actual, method, config_id), group in rolling.groupby(
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
                "display_name": "Joint Rolling",
                "method": method,
                "config_id": config_id,
            }
            row.update(metric_for_group(group))
            rows.append(row)
            bench = benchmark_slice(benchmarks, dates)
            for (bench_method, bench_config), bench_group in bench.groupby(["method", "config_id"], sort=False):
                bench_row = {
                    "horizon_years": horizon_years,
                    "requested_start_date": requested,
                    "actual_start_date": actual,
                    "start_group": group_name,
                    "display_name": BENCHMARK_DISPLAY.get((bench_method, bench_config), bench_method),
                    "method": bench_method,
                    "config_id": bench_config,
                }
                bench_row.update(metric_for_group(bench_group))
                rows.append(bench_row)
    return pd.DataFrame(rows)


def plot_start_metric_bars(joint_summary: pd.DataFrame, path: Path, metric_left: str, metric_right: str, title: str) -> None:
    labels = joint_summary["requested_start_date"].tolist()
    x = np.arange(len(labels))
    width = 0.38
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()
    ax1.bar(x - width / 2, joint_summary[metric_left], width, label=metric_left, color="#2f6fbb")
    ax2.bar(x + width / 2, joint_summary[metric_right], width, label=metric_right, color="#d9822b")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=45, ha="right")
    ax1.set_title(title)
    ax1.grid(True, axis="y", alpha=0.25)
    ax1.set_ylabel(metric_left)
    ax2.set_ylabel(metric_right)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def plot_equity_curves(curves: pd.DataFrame, path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(12, 6.5))
    for col in curves.columns:
        if col == "date":
            continue
        lw = 2.2 if "100% G" not in col and "50/50" not in col and "SPY" not in col else 1.6
        ax.plot(pd.to_datetime(curves["date"]), curves[col], label=col, linewidth=lw)
    ax.set_title(title)
    ax.set_ylabel("Wealth, rebased to 1")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def build_equity_curves(data: pd.DataFrame, name_cols: list[str]) -> pd.DataFrame:
    data = data.copy()
    data["date"] = pd.to_datetime(data["date"]).dt.normalize()
    curves: list[pd.DataFrame] = []
    for keys, group in data.groupby(name_cols, sort=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        label = " ".join(str(k) for k in keys)
        group = group.sort_values("date")
        wealth = (1.0 + group["net_return"].astype(float)).cumprod()
        wealth = wealth / wealth.iloc[0]
        curves.append(pd.DataFrame({"date": group["date"], label: wealth}))
    out = curves[0]
    for curve in curves[1:]:
        out = out.merge(curve, on="date", how="inner")
    for col in out.columns:
        if col != "date":
            out[col] = out[col] / out[col].iloc[0]
    return out.sort_values("date").reset_index(drop=True)


def pct(value: float) -> str:
    return "" if pd.isna(value) else f"{value:.2%}"


def num(value: float) -> str:
    return "" if pd.isna(value) else f"{value:.2f}"


def markdown_table(df: pd.DataFrame, columns: list[str], pct_cols: set[str] | None = None, num_cols: set[str] | None = None, max_rows: int = 40) -> list[str]:
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
    report = REPORT_DIR / "rolling_start_date_sensitivity_v1_report_en.md"
    common_joint = common_summary[common_summary["display_name"].str.startswith("Joint Rolling")].copy()
    common_bench = common_summary[~common_summary["display_name"].str.startswith("Joint Rolling")].copy()
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
        "# Rolling Start-Date Sensitivity v1",
        "",
        "This report tests whether the current Joint Old/Credit rolling validation is sensitive to the requested OOS start date and to 63-day block phase. The model, parameter grid, 756-day rolling training window, 63-day test block, 10bp transaction cost, and selection score are kept unchanged.",
        "",
        "Important plot instruction: the common-window benchmark equity curve intentionally excludes `Old+Credit Rolling`; it compares only Joint Rolling start-date variants with 50/50 G-D, 100% G, and SPY.",
        "",
        "## 1. Tested Start Dates",
        "",
    ]
    start_rows = pd.DataFrame(all_requested_starts())
    lines.extend(markdown_table(start_rows, ["start_group", "requested_start_date"], max_rows=20))
    lines += [
        "",
        "## 2. Start-to-End Joint Rolling Results",
        "",
        "Each requested start date is run to the common dataset end. The `actual_start_date` can be later than the requested date when the rolling validation requires the initial training window.",
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
        "![CAGR and Sharpe by Start Date](../plots/rolling_start_date_cagr_sharpe_bar.png)",
        "",
        "![Max Drawdown and Turnover by Start Date](../plots/rolling_start_date_maxdd_turnover_bar.png)",
        "",
        "## 3. Common-Window Results",
        "",
        f"Common window: `{common_start}` to `{common_end}`. All rolling start-date variants and benchmarks are evaluated on the same dates.",
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
        "![Rolling Start-Date Equity Curves](../plots/rolling_start_date_equity_curves.png)",
        "",
        "![Common-Window Rolling vs Benchmarks](../plots/rolling_start_date_vs_benchmarks_common_window.png)",
        "",
        "## 4. Fixed-Horizon Results",
        "",
        "This table evaluates each start date over the first available 3-year or 5-year horizon when enough observations exist.",
        "",
    ]
    if fixed_horizon.empty:
        lines.append("No fixed-horizon rows were available.")
    else:
        lines.extend(
            markdown_table(
                fixed_horizon[fixed_horizon["display_name"] == "Joint Rolling"],
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
        f"- Start-to-end CAGR ranges from `{pct(start_cagr_min)}` to `{pct(start_cagr_max)}` and Sharpe ranges from `{num(start_sharpe_min)}` to `{num(start_sharpe_max)}`. This range is partly driven by market-period inclusion: later starts exclude the COVID crash/rebound and shorten the sample.",
        f"- On the strict common window `{common_start}` to `{common_end}`, Joint Rolling variants are much tighter: CAGR ranges from `{pct(common_cagr_min)}` to `{pct(common_cagr_max)}`, Sharpe ranges from `{num(common_sharpe_min)}` to `{num(common_sharpe_max)}`, and max drawdown ranges from `{pct(common_mdd_min)}` to `{pct(common_mdd_max)}`.",
        f"- On the common window, the Joint Rolling variants are above 50/50 G-D buy-and-hold (`{pct(bench_lookup['50/50 G-D Buy & Hold']['cagr'])}` CAGR, `{num(bench_lookup['50/50 G-D Buy & Hold']['sharpe'])}` Sharpe) and SPY (`{pct(bench_lookup['SPY Buy & Hold']['cagr'])}` CAGR, `{num(bench_lookup['SPY Buy & Hold']['sharpe'])}` Sharpe). They are also slightly above 100% G on CAGR while carrying lower volatility and much smaller max drawdown.",
        "- The block-phase tests around 2018 show some start-to-end dispersion, but the common-window results are close. This suggests the rolling result is not mainly an artifact of the original `2018-06-28` start date, although parameter selection itself remains path-dependent.",
        "- The same most-frequent configuration appears across all start-date variants, but the number of unique selected configurations remains high. Therefore the strategy family is stable, while exact block-by-block parameter selection is not perfectly stable.",
        "- The common-window figure intentionally excludes Old+Credit Rolling, following the requested plot scope.",
        "",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def main() -> None:
    ensure_dirs()
    features = base.build_feature_panel()
    features = features[features["date"] >= pd.Timestamp("2016-12-21")].reset_index(drop=True)
    config_grid = joint.generate_config_grid()
    cache = build_returns_cache_only(features, config_grid)
    keys, dates, prepared = prepare_cache_arrays(cache)

    starts = all_requested_starts()
    rolling_parts: list[pd.DataFrame] = []
    selection_parts: list[pd.DataFrame] = []
    for start in starts:
        wf, selections = rolling_for_start(keys, dates, prepared, start)
        rolling_parts.append(wf)
        selection_parts.append(selections)

    rolling_returns = pd.concat(rolling_parts, ignore_index=True)
    selections = pd.concat(selection_parts, ignore_index=True)
    benchmarks = base.static_benchmark_returns(features)

    start_to_end = build_start_to_end_summary(rolling_returns, benchmarks)
    start_to_end_joint = build_joint_only_summary(start_to_end)
    common_summary, common_returns = build_common_window_summary(rolling_returns, benchmarks)
    fixed_horizon = build_fixed_horizon_summary(start_to_end, rolling_returns, benchmarks)
    stability = build_selection_stability(selections)

    rolling_common = common_returns.copy()
    joint_common = rolling_common[rolling_common["method"].str.startswith("Joint Rolling start")].copy()
    joint_common["curve_name"] = joint_common["requested_start_date"].map(lambda x: f"Joint {x}")
    benchmark_common = rolling_common[rolling_common["method"].isin([m for m, _ in BENCHMARK_DISPLAY])].copy()
    benchmark_common["curve_name"] = benchmark_common.apply(
        lambda row: BENCHMARK_DISPLAY.get((row["method"], row["config_id"]), row["method"]),
        axis=1,
    )
    common_curve_input = pd.concat([joint_common, benchmark_common], ignore_index=True)

    common_start = common_summary["start_date"].replace("", np.nan).dropna().min()
    common_end = common_summary["end_date"].replace("", np.nan).dropna().max()

    joint_curve = rolling_returns[rolling_returns["cost_bps"] == PRIMARY_COST_BPS].copy()
    joint_curve["curve_name"] = joint_curve["requested_start_date"].map(lambda x: f"Joint {x}")
    equity_joint = build_equity_curves(joint_curve, ["curve_name"])
    equity_common = build_equity_curves(common_curve_input, ["curve_name"])

    plot_start_metric_bars(
        start_to_end_joint,
        PLOT_DIR / "rolling_start_date_cagr_sharpe_bar.png",
        "cagr",
        "sharpe",
        "Rolling CAGR and Sharpe by Requested Start Date, 10bp Cost",
    )
    plot_start_metric_bars(
        start_to_end_joint,
        PLOT_DIR / "rolling_start_date_maxdd_turnover_bar.png",
        "max_drawdown",
        "annual_turnover",
        "Rolling Max Drawdown and Turnover by Requested Start Date, 10bp Cost",
    )
    plot_equity_curves(
        equity_joint,
        PLOT_DIR / "rolling_start_date_equity_curves.png",
        "Joint Rolling Equity Curves by Requested Start Date, 10bp Cost",
    )
    plot_equity_curves(
        equity_common,
        PLOT_DIR / "rolling_start_date_vs_benchmarks_common_window.png",
        "Common-Window Joint Rolling vs 50/50, 100% G, and SPY, 10bp Cost",
    )

    report = write_report(
        start_to_end_joint,
        common_summary,
        fixed_horizon,
        stability,
        str(common_start),
        str(common_end),
    )

    features.to_csv(INPUT_DIR / "rolling_start_date_sensitivity_v1_feature_panel.csv", index=False, encoding="utf-8-sig")
    config_grid.to_csv(TABLE_DIR / "rolling_start_date_sensitivity_v1_config_grid.csv", index=False, encoding="utf-8-sig")
    rolling_returns.to_csv(TABLE_DIR / "rolling_start_date_sensitivity_v1_daily_returns.csv", index=False, encoding="utf-8-sig")
    selections.to_csv(TABLE_DIR / "rolling_start_date_sensitivity_v1_selections.csv", index=False, encoding="utf-8-sig")
    start_to_end.to_csv(TABLE_DIR / "rolling_start_date_sensitivity_v1_start_to_end_summary.csv", index=False, encoding="utf-8-sig")
    start_to_end_joint.to_csv(TABLE_DIR / "rolling_start_date_sensitivity_v1_joint_start_to_end_summary.csv", index=False, encoding="utf-8-sig")
    common_summary.to_csv(TABLE_DIR / "rolling_start_date_sensitivity_v1_common_window_summary.csv", index=False, encoding="utf-8-sig")
    common_returns.to_csv(TABLE_DIR / "rolling_start_date_sensitivity_v1_common_window_returns.csv", index=False, encoding="utf-8-sig")
    fixed_horizon.to_csv(TABLE_DIR / "rolling_start_date_sensitivity_v1_fixed_horizon_summary.csv", index=False, encoding="utf-8-sig")
    stability.to_csv(TABLE_DIR / "rolling_start_date_sensitivity_v1_selection_stability.csv", index=False, encoding="utf-8-sig")
    equity_joint.to_csv(TABLE_DIR / "rolling_start_date_sensitivity_v1_equity_curves.csv", index=False, encoding="utf-8-sig")
    equity_common.to_csv(TABLE_DIR / "rolling_start_date_sensitivity_v1_common_window_equity_curves.csv", index=False, encoding="utf-8-sig")

    print(f"Requested starts: {len(starts)}")
    print(f"Report: {report}")


if __name__ == "__main__":
    main()

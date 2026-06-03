#!/usr/bin/env python3
"""Jointly select old smooth-score and bond/credit parameters.

This experiment is the stricter follow-up to the fixed Old Best + Credit
overlay.  Instead of keeping the old Best Local parameters fixed, it jointly
selects the old score weights and the bond/credit add-on weights:

    r, d, old stress, old crowded, credit relief, rate relief x credit stress.

Outputs include local-best, walk-forward expanding, and walk-forward rolling
comparisons with equity curves and an English report.
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


OUT_DIR = ROOT / "data" / "phase1" / "joint_old_credit_policy_v1"
INPUT_DIR = OUT_DIR / "inputs"
TABLE_DIR = OUT_DIR / "tables"
PLOT_DIR = OUT_DIR / "plots"
REPORT_DIR = OUT_DIR / "reports"
PREV_BOND_CREDIT_OOS_RETURNS = (
    ROOT
    / "data"
    / "phase1"
    / "bond_credit_smooth_policy_v1"
    / "tables"
    / "bond_credit_smooth_policy_v1_oos_validation_returns.csv"
)

PRIMARY_COST_BPS = 10
COMMON_START_DATE = "2017-06-28"
OOS_START_DATE = "2018-06-28"
TRANSACTION_COST_BPS = base.TRANSACTION_COST_BPS
VALIDATION_INITIAL_TRAIN_WINDOW = base.VALIDATION_INITIAL_TRAIN_WINDOW
VALIDATION_TEST_BLOCK = base.VALIDATION_TEST_BLOCK
ROLLING_TRAIN_WINDOW = base.ROLLING_TRAIN_WINDOW


def ensure_dirs() -> None:
    for directory in (INPUT_DIR, TABLE_DIR, PLOT_DIR, REPORT_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def generate_config_grid() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for alpha in (0.50, 0.67):
        for lambda_stress in (0.25, 0.50):
            for lambda_crowded in (0.05, 0.15):
                for lambda_credit in (0.00, 0.05, 0.10, 0.25, 0.50):
                    for lambda_interaction in (0.00, 0.05, 0.10, 0.25, 0.50):
                        for max_tilt in (0.30, 0.50):
                            for tau_weight in (0.75, 1.00):
                                for eta in (0.03, 0.05):
                                    config_id = (
                                        f"joint_a{alpha:.2f}_ls{lambda_stress:.2f}_lcrowd{lambda_crowded:.2f}"
                                        f"_lcred{lambda_credit:.2f}_li{lambda_interaction:.2f}"
                                        f"_tilt{max_tilt:.2f}_tau{tau_weight:.2f}_eta{eta:.2f}"
                                    )
                                    rows.append(
                                        {
                                            "method": "joint_old_credit_score",
                                            "config_id": config_id,
                                            "alpha": alpha,
                                            "lambda_stress": lambda_stress,
                                            "lambda_crowded": lambda_crowded,
                                            "lambda_credit": lambda_credit,
                                            "lambda_interaction": lambda_interaction,
                                            "max_tilt": max_tilt,
                                            "tau_weight": tau_weight,
                                            "eta": eta,
                                        }
                                    )
    return pd.DataFrame(rows)


def score_from_config(features: pd.DataFrame, config: pd.Series) -> pd.Series:
    core = config["alpha"] * features["r"] + (1.0 - config["alpha"]) * features["d"]
    stress = 0.5 * features["z_old_i1"] + 0.5 * features["z_old_i2"]
    crowded = 0.5 * features["z_old_i3"] + 0.5 * features["z_old_i4"]
    return (
        core
        + config["lambda_stress"] * stress
        - config["lambda_crowded"] * crowded
        + config["lambda_credit"] * features["ce"]
        + config["lambda_interaction"] * features["z_r_x_cs"]
    )


def build_strategy_for_config(features: pd.DataFrame, config: pd.Series) -> pd.DataFrame:
    score = score_from_config(features, config)
    weight = base.smooth_weight_from_score(score, config["max_tilt"], config["tau_weight"], config["eta"])
    deployed = weight.shift(1)
    gross = deployed * features["g_return"] + (1.0 - deployed) * features["d_return"]
    turnover = 2.0 * deployed.diff().abs().fillna(0.0)
    rows = []
    for cost_bps in TRANSACTION_COST_BPS:
        net = gross - turnover * (cost_bps / 10_000.0)
        rows.append(
            pd.DataFrame(
                {
                    "date": features["date"],
                    "method": config["method"],
                    "config_id": config["config_id"],
                    "cost_bps": cost_bps,
                    "g_weight": deployed,
                    "d_weight": 1.0 - deployed,
                    "daily_turnover": turnover,
                    "score": score,
                    "score_z": base.expanding_z(score),
                    "gross_return": gross,
                    "net_return": net,
                }
            ).dropna(subset=["net_return"])
        )
    return pd.concat(rows, ignore_index=True)


def metrics_from_group(group: pd.DataFrame) -> dict[str, float | int | str]:
    group = group.copy()
    group["date"] = pd.to_datetime(group["date"]).dt.normalize()
    group = group[group["date"] >= pd.Timestamp(COMMON_START_DATE)].sort_values("date")
    idx = group["date"]
    ret = pd.Series(group["net_return"].to_numpy(), index=idx)
    turnover = pd.Series(group["daily_turnover"].to_numpy(), index=idx)
    weights = pd.Series(group["g_weight"].to_numpy(), index=idx) if "g_weight" in group else None
    return base.performance_metrics(ret, turnover=turnover, g_weight=weights)


def metrics_for_returns(returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (method, config_id, cost_bps), group in returns.groupby(["method", "config_id", "cost_bps"], sort=False):
        row = {"method": method, "config_id": config_id, "cost_bps": cost_bps}
        row.update(metrics_from_group(group))
        rows.append(row)
    return pd.DataFrame(rows)


def add_selection_score(metrics: pd.DataFrame) -> pd.DataFrame:
    out = metrics.copy()
    out["selection_score"] = np.nan
    mask = (out["cost_bps"] == PRIMARY_COST_BPS) & (out["method"] == "joint_old_credit_score")
    subset = out[mask].copy()
    score = (
        subset["sharpe"].rank(pct=True)
        + subset["calmar"].rank(pct=True)
        + subset["cagr"].rank(pct=True)
        + subset["max_drawdown"].rank(pct=True)
        + (-subset["annual_turnover"]).rank(pct=True)
    ) / 5.0
    out.loc[subset.index, "selection_score"] = score
    return out


def build_grid_outputs(features: pd.DataFrame, config_grid: pd.DataFrame) -> tuple[pd.DataFrame, dict[tuple[str, str, int], pd.DataFrame]]:
    metric_rows = []
    returns_cache: dict[tuple[str, str, int], pd.DataFrame] = {}
    for _, config in config_grid.iterrows():
        strat = build_strategy_for_config(features, config)
        metric_rows.append(metrics_for_returns(strat))
        primary = strat[strat["cost_bps"] == PRIMARY_COST_BPS]
        returns_cache[(config["method"], config["config_id"], PRIMARY_COST_BPS)] = primary.copy()
    metrics = add_selection_score(pd.concat(metric_rows, ignore_index=True))
    return metrics, returns_cache


def score_rank_for_train(metrics: pd.DataFrame) -> pd.Series:
    return (
        metrics["sharpe"].rank(pct=True)
        + metrics["calmar"].rank(pct=True)
        + metrics["cagr"].rank(pct=True)
        + metrics["max_drawdown"].rank(pct=True)
        + (-metrics["annual_turnover"]).rank(pct=True)
    ) / 5.0


def walk_forward_validation(
    config_returns: dict[tuple[str, str, int], pd.DataFrame],
    config_grid: pd.DataFrame,
    start_date: str,
    mode: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    configs = list(zip(config_grid["method"], config_grid["config_id"]))
    all_dates = sorted(pd.to_datetime(next(iter(config_returns.values()))["date"]).dropna().unique())
    start_ts = pd.Timestamp(start_date)
    start_idx = next(i for i, d in enumerate(all_dates) if d >= start_ts)
    if start_idx < VALIDATION_INITIAL_TRAIN_WINDOW:
        start_idx = VALIDATION_INITIAL_TRAIN_WINDOW
    pieces = []
    selections = []
    for test_start_idx in range(start_idx, len(all_dates), VALIDATION_TEST_BLOCK):
        test_dates = all_dates[test_start_idx : test_start_idx + VALIDATION_TEST_BLOCK]
        if not test_dates:
            continue
        train_end_idx = test_start_idx
        train_start_idx = 0 if mode == "expanding" else max(0, train_end_idx - ROLLING_TRAIN_WINDOW)
        train_dates = set(all_dates[train_start_idx:train_end_idx])
        train_rows = []
        for method, config_id in configs:
            group = config_returns[(method, config_id, PRIMARY_COST_BPS)]
            train = group[pd.to_datetime(group["date"]).isin(train_dates)]
            if len(train) < 126:
                continue
            row = {"method": method, "config_id": config_id}
            row.update(metrics_from_group(train))
            train_rows.append(row)
        train_metrics = pd.DataFrame(train_rows)
        train_metrics["selection_score"] = score_rank_for_train(train_metrics)
        best = train_metrics.sort_values("selection_score", ascending=False).iloc[0]
        selected = config_returns[(str(best["method"]), str(best["config_id"]), PRIMARY_COST_BPS)]
        test = selected[pd.to_datetime(selected["date"]).isin(test_dates)].copy()
        test["method"] = f"Joint WF {mode.title()}"
        test["config_id"] = f"joint_wf_{mode}"
        pieces.append(test)
        selections.append(
            {
                "mode": mode,
                "test_start": pd.Timestamp(test_dates[0]).date().isoformat(),
                "test_end": pd.Timestamp(test_dates[-1]).date().isoformat(),
                "train_start": pd.Timestamp(all_dates[train_start_idx]).date().isoformat(),
                "train_end": pd.Timestamp(all_dates[train_end_idx - 1]).date().isoformat(),
                "selected_config_id": str(best["config_id"]),
                "train_selection_score": float(best["selection_score"]),
                "train_sharpe": float(best["sharpe"]),
                "train_cagr": float(best["cagr"]),
                "train_max_drawdown": float(best["max_drawdown"]),
            }
        )
    return pd.concat(pieces, ignore_index=True), pd.DataFrame(selections)


def common_date_filter(returns: pd.DataFrame, display: dict[tuple[str, str], str], cost_bps: int = PRIMARY_COST_BPS) -> pd.DataFrame:
    data = returns[returns["cost_bps"] == cost_bps].copy()
    date_sets = []
    for method, config_id in display:
        dates = set(data[(data["method"] == method) & (data["config_id"] == config_id)]["date"])
        if dates:
            date_sets.append(dates)
    common = sorted(set.intersection(*date_sets)) if date_sets else []
    return data[data["date"].isin(common)].copy()


def summary_for_display(returns: pd.DataFrame, display: dict[tuple[str, str], str], cost_bps: int = PRIMARY_COST_BPS) -> pd.DataFrame:
    common = common_date_filter(returns, display, cost_bps=cost_bps)
    rows = []
    for method, config_id in display:
        group = common[(common["method"] == method) & (common["config_id"] == config_id)].sort_values("date")
        idx = pd.to_datetime(group["date"])
        ret = pd.Series(group["net_return"].to_numpy(), index=idx)
        turnover = pd.Series(group["daily_turnover"].to_numpy(), index=idx)
        weights = pd.Series(group["g_weight"].to_numpy(), index=idx) if "g_weight" in group else None
        row = {"display_name": display[(method, config_id)], "method": method, "config_id": config_id, "cost_bps": cost_bps}
        row.update(base.performance_metrics(ret, turnover=turnover, g_weight=weights))
        rows.append(row)
    return pd.DataFrame(rows)


def build_equity_curves(returns: pd.DataFrame, display: dict[tuple[str, str], str], cost_bps: int = PRIMARY_COST_BPS) -> pd.DataFrame:
    common = common_date_filter(returns, display, cost_bps=cost_bps)
    curves = []
    for method, config_id in display:
        group = common[(common["method"] == method) & (common["config_id"] == config_id)].sort_values("date")
        if group.empty:
            continue
        wealth = (1.0 + group["net_return"].astype(float)).cumprod()
        wealth = wealth / wealth.iloc[0]
        curves.append(pd.DataFrame({"date": pd.to_datetime(group["date"]), display[(method, config_id)]: wealth}))
    out = curves[0]
    for curve in curves[1:]:
        out = out.merge(curve, on="date", how="inner")
    for col in out.columns:
        if col != "date":
            out[col] = out[col] / out[col].iloc[0]
    return out.sort_values("date").reset_index(drop=True)


def plot_equity(equity: pd.DataFrame, title: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 6))
    for col in equity.columns:
        if col == "date":
            continue
        lw = 2.4 if "Joint" in col else 1.5
        ax.plot(equity["date"], equity[col], label=col, linewidth=lw)
    ax.set_title(title)
    ax.set_ylabel("Wealth, Rebased to 1")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def old_plus_selected_returns(features: pd.DataFrame) -> pd.DataFrame:
    config = pd.Series(
        {
            "method": "old_best_plus_bond_credit_incremental",
            "config_id": "old_plus_credit_lc0.10_li0.50",
            "alpha_d": 0.50,
            "lambda_credit": 0.10,
            "lambda_g126": 0.05,
            "lambda_interaction": 0.50,
            "max_tilt": 0.50,
            "tau_weight": 0.75,
            "eta": 0.05,
        }
    )
    return base.build_strategy_for_config(features, config)


def old_fixed_credit_oos_returns() -> pd.DataFrame:
    if not PREV_BOND_CREDIT_OOS_RETURNS.exists():
        return pd.DataFrame()
    data = pd.read_csv(PREV_BOND_CREDIT_OOS_RETURNS, encoding="utf-8-sig")
    data["date"] = pd.to_datetime(data["date"]).dt.normalize()
    keep = data["method"].isin(["Old+Credit WF Expanding", "Old+Credit WF Rolling"])
    return data[keep].copy()


def comparison_table(summary: pd.DataFrame) -> pd.DataFrame:
    target = summary[summary["display_name"] == "Joint Local Best"].iloc[0]
    rows = []
    for _, row in summary.iterrows():
        if row["display_name"] == target["display_name"]:
            continue
        rows.append(
            {
                "comparison": f"Joint Local Best - {row['display_name']}",
                "annualized_excess_return": target["cagr"] - row["cagr"],
                "max_dd_diff": target["max_drawdown"] - row["max_drawdown"],
                "sharpe_diff": target["sharpe"] - row["sharpe"],
                "turnover_diff": target["annual_turnover"] - row["annual_turnover"],
            }
        )
    return pd.DataFrame(rows)


def pairwise_comparison_table(summary: pd.DataFrame, pairs: list[tuple[str, str]]) -> pd.DataFrame:
    rows = []
    by_name = {row["display_name"]: row for _, row in summary.iterrows()}
    for target_name, benchmark_name in pairs:
        if target_name not in by_name or benchmark_name not in by_name:
            continue
        target = by_name[target_name]
        benchmark = by_name[benchmark_name]
        rows.append(
            {
                "comparison": f"{target_name} - {benchmark_name}",
                "annualized_excess_return": target["cagr"] - benchmark["cagr"],
                "max_dd_diff": target["max_drawdown"] - benchmark["max_drawdown"],
                "sharpe_diff": target["sharpe"] - benchmark["sharpe"],
                "turnover_diff": target["annual_turnover"] - benchmark["annual_turnover"],
            }
        )
    return pd.DataFrame(rows)


def markdown_table(df: pd.DataFrame, columns: list[str], pct_cols: set[str] | None = None, num_cols: set[str] | None = None, max_rows: int = 30) -> list[str]:
    pct_cols = pct_cols or set()
    num_cols = num_cols or set()
    view = df[columns].head(max_rows).copy()
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in view.to_dict("records"):
        vals = []
        for col in columns:
            value = row[col]
            if pd.isna(value):
                vals.append("")
            elif col in pct_cols:
                vals.append(f"{value:.2%}")
            elif col in num_cols:
                vals.append(f"{value:.2f}")
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return lines


def write_report(
    config_grid: pd.DataFrame,
    metrics: pd.DataFrame,
    local_summary: pd.DataFrame,
    comparisons: pd.DataFrame,
    oos_comparisons: pd.DataFrame,
    oos_summary: pd.DataFrame,
    local_best_config: pd.Series,
    oos_selections: pd.DataFrame,
) -> Path:
    path = REPORT_DIR / "phase1_joint_old_credit_policy_v1_report_en.md"
    top = metrics[(metrics["method"] == "joint_old_credit_score") & (metrics["cost_bps"] == PRIMARY_COST_BPS)].sort_values("selection_score", ascending=False).head(10)
    selection_counts = (
        oos_selections.groupby(["mode", "selected_config_id"], sort=False)
        .size()
        .reset_index(name="n_blocks")
        .sort_values(["mode", "n_blocks"], ascending=[True, False])
    )
    lines = [
        "# Phase 1 Joint Old/Credit Policy v1 Report",
        "",
        "This report tests a stricter joint-selection design. Unlike the previous `Old Best + Bond/Credit Incremental` experiment, the old score parameters are not fixed. The grid jointly selects the old smooth-score parameters and the bond/credit add-on parameters.",
        "",
        "## 1. Score Definition",
        "",
        "```text",
        "score = alpha*r + (1-alpha)*d",
        "      + lambda_stress*(0.5*z_old_i1 + 0.5*z_old_i2)",
        "      - lambda_crowded*(0.5*z_old_i3 + 0.5*z_old_i4)",
        "      + lambda_credit*ce",
        "      + lambda_interaction*z(r*cs)",
        "```",
        "",
        "- `r`: rate relief, `-z(10Y yield 21d change)`.",
        "- `d`: SPY drawdown depth, `-z(SPY drawdown)`.",
        "- `ce`: credit relief, `-z(BAA10Y spread 21d change)`.",
        "- `cs`: credit stress level, `z(BAA10Y spread)`.",
        "- `old_i1`: rate relief x high VIX.",
        "- `old_i2`: high VIX x VIX relief.",
        "- `old_i3`: growth extension x low VIX.",
        "- `old_i4`: growth extension x low VIX x rate quiet.",
        "",
        "## 2. Parameter Grid",
        "",
        f"Total joint configurations tested: `{len(config_grid)}`.",
        "",
        "```text",
        "alpha in {0.50, 0.67}",
        "lambda_stress in {0.25, 0.50}",
        "lambda_crowded in {0.05, 0.15}",
        "lambda_credit in {0.00, 0.05, 0.10, 0.25, 0.50}",
        "lambda_interaction in {0.00, 0.05, 0.10, 0.25, 0.50}",
        "max_tilt in {0.30, 0.50}",
        "tau_weight in {0.75, 1.00}",
        "eta in {0.03, 0.05}",
        "```",
        "",
        "Selected local-best configuration:",
        "",
    ]
    lines.extend(
        markdown_table(
            pd.DataFrame([local_best_config]),
            ["config_id", "alpha", "lambda_stress", "lambda_crowded", "lambda_credit", "lambda_interaction", "max_tilt", "tau_weight", "eta"],
            num_cols={"alpha", "lambda_stress", "lambda_crowded", "lambda_credit", "lambda_interaction", "max_tilt", "tau_weight", "eta"},
        )
    )
    lines += ["", "Top 10 local configurations at 10bp:", ""]
    lines.extend(
        markdown_table(
            top,
            ["config_id", "cagr", "ann_vol", "sharpe", "max_drawdown", "calmar", "annual_turnover", "avg_g_weight", "selection_score"],
            pct_cols={"cagr", "ann_vol", "max_drawdown", "annual_turnover", "avg_g_weight"},
            num_cols={"sharpe", "calmar", "selection_score"},
            max_rows=10,
        )
    )
    lines += ["", "## 3. Local Best Comparison", ""]
    lines.extend(
        markdown_table(
            local_summary,
            ["display_name", "start_date", "end_date", "cagr", "ann_vol", "sharpe", "max_drawdown", "calmar", "annual_turnover", "avg_g_weight", "final_wealth"],
            pct_cols={"cagr", "ann_vol", "max_drawdown", "annual_turnover", "avg_g_weight"},
            num_cols={"sharpe", "calmar", "final_wealth"},
            max_rows=20,
        )
    )
    lines += ["", "Incremental comparisons:", ""]
    lines.extend(
        markdown_table(
            comparisons,
            ["comparison", "annualized_excess_return", "max_dd_diff", "sharpe_diff", "turnover_diff"],
            pct_cols={"annualized_excess_return", "max_dd_diff", "turnover_diff"},
            num_cols={"sharpe_diff"},
            max_rows=20,
        )
    )
    lines += ["", "![Local Equity Curves](../plots/joint_old_credit_policy_v1_local_equity_curves.png)", ""]
    lines += ["## 4. OOS Validation: Expanding and Rolling", ""]
    lines.extend(
        markdown_table(
            oos_summary,
            ["display_name", "start_date", "end_date", "cagr", "ann_vol", "sharpe", "max_drawdown", "calmar", "annual_turnover", "avg_g_weight", "final_wealth"],
            pct_cols={"cagr", "ann_vol", "max_drawdown", "annual_turnover", "avg_g_weight"},
            num_cols={"sharpe", "calmar", "final_wealth"},
            max_rows=20,
        )
    )
    lines += ["", "![OOS Equity Curves](../plots/joint_old_credit_policy_v1_oos_equity_curves.png)", ""]
    lines += ["OOS incremental comparisons:", ""]
    lines.extend(
        markdown_table(
            oos_comparisons,
            ["comparison", "annualized_excess_return", "max_dd_diff", "sharpe_diff", "turnover_diff"],
            pct_cols={"annualized_excess_return", "max_dd_diff", "turnover_diff"},
            num_cols={"sharpe_diff"},
            max_rows=20,
        )
    )
    lines += [""]
    lines += ["## 5. Walk-Forward Selection Frequency", ""]
    lines.extend(markdown_table(selection_counts, ["mode", "selected_config_id", "n_blocks"], max_rows=40))
    lines += [
        "",
        "## 6. Interpretation",
        "",
        "This branch answers whether the credit extension should be treated as a small overlay to the old Best Local score or whether the full old/credit score should be jointly reselected. The local-best result shows that joint selection can slightly improve the in-sample/local objective and reduce turnover versus the fixed old-plus-credit overlay. However, the OOS results are stricter: the jointly selected expanding and rolling policies do not clearly dominate the prior fixed Old+Credit walk-forward policies. The current evidence therefore favors keeping the old Best structure plus credit overlay as the simpler and more robust implementation, while treating joint selection as a useful robustness check rather than the new mainline.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    ensure_dirs()
    features = base.build_feature_panel()
    features = features[features["date"] >= pd.Timestamp("2016-12-21")].reset_index(drop=True)
    config_grid = generate_config_grid()
    metrics, cache = build_grid_outputs(features, config_grid)
    local_best = metrics[(metrics["method"] == "joint_old_credit_score") & (metrics["cost_bps"] == PRIMARY_COST_BPS)].sort_values("selection_score", ascending=False).iloc[0]
    local_cfg = config_grid[(config_grid["method"] == local_best["method"]) & (config_grid["config_id"] == local_best["config_id"])].iloc[0]
    local_returns = build_strategy_for_config(features, local_cfg)
    local_returns["method"] = "Joint Local Best"
    local_returns["config_id"] = "joint_local_best"

    baseline_returns = [
        base.load_old_best_local_returns(),
        old_plus_selected_returns(features),
        base.static_benchmark_returns(features),
    ]
    local_all = pd.concat([local_returns, *baseline_returns], ignore_index=True)
    local_display = {
        ("Joint Local Best", "joint_local_best"): "Joint Local Best",
        ("old_best_plus_bond_credit_incremental", "old_plus_credit_lc0.10_li0.50"): "Old Best + Bond/Credit Incremental",
        ("Existing Smooth Score Best Local", "existing_best_local_tilt50"): "Existing Smooth Score Best Local",
        ("50/50 G-D Buy & Hold", "50/50 G-D Buy & Hold"): "50/50 G-D Buy & Hold",
        ("100% G Buy & Hold", "100% G Buy & Hold"): "100% G Buy & Hold",
        ("SPY Buy & Hold", "SPY Buy & Hold"): "SPY Buy & Hold",
    }
    local_summary = summary_for_display(local_all, local_display)
    local_equity = build_equity_curves(local_all, local_display)
    comparisons = comparison_table(local_summary)

    wf_exp, sel_exp = walk_forward_validation(cache, config_grid, OOS_START_DATE, "expanding")
    wf_roll, sel_roll = walk_forward_validation(cache, config_grid, OOS_START_DATE, "rolling")
    previous_old_credit_oos = old_fixed_credit_oos_returns()
    oos_returns = pd.concat([wf_exp, wf_roll, previous_old_credit_oos, base.load_old_best_local_returns(), base.static_benchmark_returns(features)], ignore_index=True)
    oos_display = {
        ("Joint WF Expanding", "joint_wf_expanding"): "Joint WF Expanding",
        ("Joint WF Rolling", "joint_wf_rolling"): "Joint WF Rolling",
        ("Old+Credit WF Expanding", "old_plus_wf_expanding"): "Old+Credit WF Expanding",
        ("Old+Credit WF Rolling", "old_plus_wf_rolling"): "Old+Credit WF Rolling",
        ("Existing Smooth Score Best Local", "existing_best_local_tilt50"): "Existing Smooth Score Best Local",
        ("50/50 G-D Buy & Hold", "50/50 G-D Buy & Hold"): "50/50 G-D Buy & Hold",
        ("100% G Buy & Hold", "100% G Buy & Hold"): "100% G Buy & Hold",
        ("SPY Buy & Hold", "SPY Buy & Hold"): "SPY Buy & Hold",
    }
    oos_summary = summary_for_display(oos_returns[oos_returns["date"] >= pd.Timestamp(OOS_START_DATE)], oos_display)
    oos_equity = build_equity_curves(oos_returns[oos_returns["date"] >= pd.Timestamp(OOS_START_DATE)], oos_display)
    oos_comparisons = pairwise_comparison_table(
        oos_summary,
        [
            ("Joint WF Expanding", "Old+Credit WF Expanding"),
            ("Joint WF Rolling", "Old+Credit WF Rolling"),
            ("Joint WF Rolling", "Existing Smooth Score Best Local"),
            ("Joint WF Rolling", "50/50 G-D Buy & Hold"),
            ("Joint WF Rolling", "100% G Buy & Hold"),
        ],
    )
    selections = pd.concat([sel_exp, sel_roll], ignore_index=True)

    plot_equity(local_equity, "Joint Old/Credit Local Best Equity Curves, 10bp Cost", PLOT_DIR / "joint_old_credit_policy_v1_local_equity_curves.png")
    plot_equity(oos_equity, "Joint Old/Credit OOS Equity Curves, 10bp Cost", PLOT_DIR / "joint_old_credit_policy_v1_oos_equity_curves.png")

    report = write_report(config_grid, metrics, local_summary, comparisons, oos_comparisons, oos_summary, local_cfg, selections)

    features.to_csv(INPUT_DIR / "joint_old_credit_policy_v1_feature_panel.csv", index=False, encoding="utf-8-sig")
    config_grid.to_csv(TABLE_DIR / "joint_old_credit_policy_v1_config_grid.csv", index=False, encoding="utf-8-sig")
    metrics.to_csv(TABLE_DIR / "joint_old_credit_policy_v1_grid_metrics.csv", index=False, encoding="utf-8-sig")
    local_all.to_csv(TABLE_DIR / "joint_old_credit_policy_v1_local_returns.csv", index=False, encoding="utf-8-sig")
    local_summary.to_csv(TABLE_DIR / "joint_old_credit_policy_v1_local_summary.csv", index=False, encoding="utf-8-sig")
    comparisons.to_csv(TABLE_DIR / "joint_old_credit_policy_v1_comparisons.csv", index=False, encoding="utf-8-sig")
    local_equity.to_csv(TABLE_DIR / "joint_old_credit_policy_v1_local_equity_curves.csv", index=False, encoding="utf-8-sig")
    oos_returns.to_csv(TABLE_DIR / "joint_old_credit_policy_v1_oos_returns.csv", index=False, encoding="utf-8-sig")
    oos_summary.to_csv(TABLE_DIR / "joint_old_credit_policy_v1_oos_summary.csv", index=False, encoding="utf-8-sig")
    oos_comparisons.to_csv(TABLE_DIR / "joint_old_credit_policy_v1_oos_comparisons.csv", index=False, encoding="utf-8-sig")
    oos_equity.to_csv(TABLE_DIR / "joint_old_credit_policy_v1_oos_equity_curves.csv", index=False, encoding="utf-8-sig")
    selections.to_csv(TABLE_DIR / "joint_old_credit_policy_v1_oos_selections.csv", index=False, encoding="utf-8-sig")

    print(f"Config count: {len(config_grid)}")
    print(f"Selected local config: {local_best['config_id']}")
    print(f"Report: {report}")


if __name__ == "__main__":
    main()

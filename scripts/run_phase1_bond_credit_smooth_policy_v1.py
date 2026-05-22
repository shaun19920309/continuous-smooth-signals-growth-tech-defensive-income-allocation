#!/usr/bin/env python3
"""Backtest a bond/credit-augmented smooth G/D timing policy.

This script extends the Phase 1 smooth-score workflow after the
bond/credit-augmented diagnostic gate.  It uses the aligned bond/credit
variables that passed or informed the diagnostic stage and produces a complete
policy report with equity curves, static benchmarks, OOS validation, and
post-2022 robustness.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
STATE_PANEL_PATH = ROOT / "data" / "phase1" / "state_framework_v2" / "inputs" / "phase1_state_framework_v2_panel.csv"
CREDIT_FRED_DIR = ROOT / "data" / "external" / "credit_liquidity" / "raw" / "fred"
SMOOTH_TABLE_DIR = ROOT / "data" / "phase1" / "smooth_score_policy_v1" / "tables"
SMOOTH_SELECTED_SUMMARY_PATH = SMOOTH_TABLE_DIR / "smooth_score_policy_v1_common_oos_selected_summary.csv"
SMOOTH_DAILY_RETURNS_PATH = SMOOTH_TABLE_DIR / "smooth_score_policy_v1_daily_returns.csv"
SMOOTH_SUPP_RETURNS_PATH = SMOOTH_TABLE_DIR / "smooth_score_policy_v1_supplementary_tilt_common_oos_returns.csv"
BOND_DIAGNOSTIC_TABLE = ROOT / "data" / "phase1" / "bond_credit_augmented_v1" / "tables" / "bond_credit_augmented_v1_interaction_gate.csv"
BOND_DIAGNOSTIC_MAIN = ROOT / "data" / "phase1" / "bond_credit_augmented_v1" / "tables" / "bond_credit_augmented_v1_main_effect_gate.csv"
FACTOR_PORTFOLIO_TABLE = ROOT / "data" / "phase1" / "factor_attribution" / "tables" / "factor_attribution_portfolios_full_sample.csv"

OUT_DIR = ROOT / "data" / "phase1" / "bond_credit_smooth_policy_v1"
INPUT_DIR = OUT_DIR / "inputs"
TABLE_DIR = OUT_DIR / "tables"
PLOT_DIR = OUT_DIR / "plots"
REPORT_DIR = OUT_DIR / "reports"

TRADING_DAYS = 252
PRIMARY_COST_BPS = 10
TRANSACTION_COST_BPS = (0, 5, 10, 20)
COMMON_START_DATE = "2017-06-28"
VALIDATION_INITIAL_TRAIN_WINDOW = 252
VALIDATION_TEST_BLOCK = 63
ROLLING_TRAIN_WINDOW = 756
POST_2022_START_DATE = "2022-01-03"


def ensure_dirs() -> None:
    for directory in (INPUT_DIR, TABLE_DIR, PLOT_DIR, REPORT_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def expanding_z(series: pd.Series, min_periods: int = 2) -> pd.Series:
    mean = series.expanding(min_periods=min_periods).mean()
    std = series.expanding(min_periods=min_periods).std(ddof=0)
    return (series - mean) / std.replace(0, np.nan)


def softplus(x: pd.Series | np.ndarray, tau: float = 1.0) -> pd.Series | np.ndarray:
    scaled = np.asarray(x, dtype=float) / tau
    values = tau * (np.maximum(scaled, 0) + np.log1p(np.exp(-np.abs(scaled))))
    if isinstance(x, pd.Series):
        return pd.Series(values, index=x.index)
    return values


def max_drawdown(returns: pd.Series) -> float:
    wealth = (1.0 + returns.fillna(0.0)).cumprod()
    dd = wealth / wealth.cummax() - 1.0
    return float(dd.min()) if len(dd) else np.nan


def downside_deviation(returns: pd.Series) -> float:
    downside = returns[returns < 0]
    if downside.empty:
        return np.nan
    return float(downside.std(ddof=0) * math.sqrt(TRADING_DAYS))


def performance_metrics(
    returns: pd.Series,
    turnover: pd.Series | None = None,
    g_weight: pd.Series | None = None,
) -> dict[str, float | int | str]:
    returns = returns.dropna()
    n = len(returns)
    years = n / TRADING_DAYS if n else np.nan
    total = float((1.0 + returns).prod() - 1.0) if n else np.nan
    cagr = float((1.0 + total) ** (1.0 / years) - 1.0) if years and years > 0 and total > -1 else np.nan
    vol = float(returns.std(ddof=0) * math.sqrt(TRADING_DAYS)) if n else np.nan
    sharpe = float(returns.mean() / returns.std(ddof=0) * math.sqrt(TRADING_DAYS)) if n and returns.std(ddof=0) > 0 else np.nan
    downside = downside_deviation(returns)
    mdd = max_drawdown(returns) if n else np.nan
    annual_turnover = float(turnover.reindex(returns.index).fillna(0).sum() / years) if turnover is not None and years and years > 0 else 0.0
    return {
        "n_days": int(n),
        "start_date": returns.index.min().date().isoformat() if n else "",
        "end_date": returns.index.max().date().isoformat() if n else "",
        "total_return": total,
        "cagr": cagr,
        "ann_vol": vol,
        "sharpe": sharpe,
        "sortino": float(cagr / downside) if downside and downside > 0 else np.nan,
        "max_drawdown": mdd,
        "calmar": float(cagr / abs(mdd)) if mdd and mdd < 0 else np.nan,
        "annual_turnover": annual_turnover,
        "avg_g_weight": float(g_weight.reindex(returns.index).mean()) if g_weight is not None else np.nan,
        "final_wealth": float((1.0 + returns).cumprod().iloc[-1]) if n else np.nan,
    }


def read_fred_series(series_id: str, name: str) -> pd.DataFrame:
    path = CREDIT_FRED_DIR / f"{series_id}.csv"
    df = pd.read_csv(path)
    value_col = series_id if series_id in df.columns else df.columns[-1]
    df = df.rename(columns={"observation_date": "date", value_col: name})
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    df[name] = pd.to_numeric(df[name], errors="coerce")
    return df[["date", name]].sort_values("date")


def build_feature_panel() -> pd.DataFrame:
    panel = pd.read_csv(STATE_PANEL_PATH, encoding="utf-8-sig")
    panel["date"] = pd.to_datetime(panel["date"]).dt.normalize()
    keep = [
        "date",
        "g_return",
        "d_return",
        "SPY",
        "future_gd_return_63d",
        "tnx_change_21d",
        "spy_drawdown",
        "vix_percentile_756d",
        "vix_change_21d",
        "gd_trailing_126d",
    ]
    out = panel[keep].copy()
    out = out.merge(read_fred_series("BAA10Y", "baa10y_spread"), on="date", how="left")
    out = out.sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)
    out["baa10y_spread"] = out["baa10y_spread"].ffill()
    out["baa10y_change_21d"] = out["baa10y_spread"] - out["baa10y_spread"].shift(21)

    raw_cols = {
        "tnx_change_21d": "z_tnx_change_21d",
        "spy_drawdown": "z_spy_drawdown",
        "vix_percentile_756d": "z_vix_percentile_756d",
        "vix_change_21d": "z_vix_change_21d",
        "gd_trailing_126d": "z_gd_trailing_126d",
        "baa10y_spread": "z_baa10y_spread",
        "baa10y_change_21d": "z_baa10y_change_21d",
    }
    for raw, z_col in raw_cols.items():
        out[z_col] = expanding_z(out[raw])

    out["r"] = -out["z_tnx_change_21d"]
    out["d"] = -out["z_spy_drawdown"]
    out["vh"] = out["z_vix_percentile_756d"]
    out["vr"] = -out["z_vix_change_21d"]
    out["g126"] = out["z_gd_trailing_126d"]
    out["cs"] = out["z_baa10y_spread"]
    out["ce"] = -out["z_baa10y_change_21d"]
    out["r_x_cs"] = out["r"] * out["cs"]
    out["z_r_x_cs"] = expanding_z(out["r_x_cs"])
    out["high_vix_smooth"] = softplus(out["vh"], tau=1.0)
    out["vix_relief_smooth"] = softplus(out["vr"], tau=1.0)
    out["low_vix_smooth"] = softplus(-out["vh"], tau=1.0)
    out["growth_ext_smooth"] = softplus(out["g126"], tau=1.0)
    out["rate_quiet_smooth"] = np.exp(-0.5 * out["r"] ** 2)
    out["old_i1"] = out["r"] * out["vh"]
    out["old_i2"] = out["high_vix_smooth"] * out["vix_relief_smooth"]
    out["old_i3"] = out["growth_ext_smooth"] * out["low_vix_smooth"]
    out["old_i4"] = out["old_i3"] * out["rate_quiet_smooth"]
    for col in ("old_i1", "old_i2", "old_i3", "old_i4"):
        out[f"z_{col}"] = expanding_z(out[col])
    return out.replace([np.inf, -np.inf], np.nan)


def smooth_weight_from_score(score: pd.Series, max_tilt: float, tau_weight: float, eta: float) -> pd.Series:
    score_z = expanding_z(score)
    target = 0.50 + max_tilt * np.tanh(score_z / tau_weight)
    weights: list[float] = []
    prev = 0.50
    for value in target:
        if pd.isna(value):
            weights.append(np.nan)
            continue
        current = (1.0 - eta) * prev + eta * float(value)
        weights.append(current)
        prev = current
    return pd.Series(weights, index=score.index)


def generate_config_grid() -> pd.DataFrame:
    rows = []
    for alpha_d in (0.50, 0.67):
        for lambda_credit in (0.25, 0.50):
            for lambda_g126 in (0.10, 0.25):
                for lambda_interaction in (0.10, 0.25, 0.50):
                    for max_tilt in (0.20, 0.30, 0.40, 0.50):
                        for tau_weight in (0.75, 1.00):
                            for eta in (0.03, 0.05, 0.10):
                                config_id = (
                                    f"bc_a{alpha_d:.2f}_lc{lambda_credit:.2f}_lg{lambda_g126:.2f}"
                                    f"_li{lambda_interaction:.2f}_tilt{max_tilt:.2f}"
                                    f"_tau{tau_weight:.2f}_eta{eta:.2f}"
                                )
                                rows.append(
                                    {
                                        "method": "bond_credit_smooth_score",
                                        "config_id": config_id,
                                        "alpha_d": alpha_d,
                                        "lambda_credit": lambda_credit,
                                        "lambda_g126": lambda_g126,
                                        "lambda_interaction": lambda_interaction,
                                        "max_tilt": max_tilt,
                                        "tau_weight": tau_weight,
                                        "eta": eta,
                                    }
                                )
    for alpha_d in (0.50, 0.67):
        for lambda_credit in (0.25, 0.50):
            for lambda_g126 in (0.10, 0.25):
                for max_tilt in (0.20, 0.30, 0.40, 0.50):
                    for tau_weight in (0.75, 1.00):
                        for eta in (0.03, 0.05, 0.10):
                            config_id = (
                                f"bc_core_a{alpha_d:.2f}_lc{lambda_credit:.2f}_lg{lambda_g126:.2f}"
                                f"_tilt{max_tilt:.2f}_tau{tau_weight:.2f}_eta{eta:.2f}"
                            )
                            rows.append(
                                {
                                    "method": "bond_credit_core_only",
                                    "config_id": config_id,
                                    "alpha_d": alpha_d,
                                    "lambda_credit": lambda_credit,
                                    "lambda_g126": lambda_g126,
                                    "lambda_interaction": 0.0,
                                    "max_tilt": max_tilt,
                                    "tau_weight": tau_weight,
                                    "eta": eta,
                                }
                            )
    for lambda_credit in (0.00, 0.05, 0.10, 0.25, 0.50):
        for lambda_interaction in (0.00, 0.05, 0.10, 0.25, 0.50):
            config_id = f"old_plus_credit_lc{lambda_credit:.2f}_li{lambda_interaction:.2f}"
            rows.append(
                {
                    "method": "old_best_plus_bond_credit_incremental",
                    "config_id": config_id,
                    "alpha_d": 0.50,
                    "lambda_credit": lambda_credit,
                    "lambda_g126": 0.05,
                    "lambda_interaction": lambda_interaction,
                    "max_tilt": 0.50,
                    "tau_weight": 0.75,
                    "eta": 0.05,
                }
            )
    return pd.DataFrame(rows)


def old_best_local_score(features: pd.DataFrame) -> pd.Series:
    core = 0.50 * features["r"] + 0.50 * features["d"]
    stress = 0.5 * features["z_old_i1"] + 0.5 * features["z_old_i2"]
    crowded = 0.5 * features["z_old_i3"] + 0.5 * features["z_old_i4"]
    return core + 0.50 * stress - 0.05 * crowded


def score_from_config(features: pd.DataFrame, config: pd.Series) -> pd.Series:
    if config["method"] == "old_best_plus_bond_credit_incremental":
        score = old_best_local_score(features)
        score = score + config["lambda_credit"] * features["ce"]
        score = score + config["lambda_interaction"] * features["z_r_x_cs"]
        return score
    core = config["alpha_d"] * features["d"] + (1.0 - config["alpha_d"]) * features["ce"]
    score = core - config["lambda_g126"] * features["g126"]
    score = score + config["lambda_interaction"] * features["z_r_x_cs"]
    return score


def build_strategy_for_config(features: pd.DataFrame, config: pd.Series) -> pd.DataFrame:
    score = score_from_config(features, config)
    weight = smooth_weight_from_score(score, config["max_tilt"], config["tau_weight"], config["eta"])
    deployed = weight.shift(1)
    gross = deployed * features["g_return"] + (1.0 - deployed) * features["d_return"]
    turnover = 2.0 * deployed.diff().abs().fillna(0.0)
    rows = []
    for cost_bps in TRANSACTION_COST_BPS:
        net = gross - turnover * (cost_bps / 10_000.0)
        frame = pd.DataFrame(
            {
                "date": features["date"],
                "method": config["method"],
                "config_id": config["config_id"],
                "cost_bps": cost_bps,
                "g_weight": deployed,
                "d_weight": 1.0 - deployed,
                "daily_turnover": turnover,
                "score": score,
                "score_z": expanding_z(score),
                "gross_return": gross,
                "net_return": net,
            }
        ).dropna(subset=["net_return"])
        rows.append(frame)
    return pd.concat(rows, ignore_index=True)


def static_benchmark_returns(features: pd.DataFrame) -> pd.DataFrame:
    specs = {
        "50/50 G-D Buy & Hold": 0.50,
        "100% G Buy & Hold": 1.00,
        "100% D Buy & Hold": 0.00,
    }
    rows = []
    for name, g_weight in specs.items():
        gross = g_weight * features["g_return"] + (1.0 - g_weight) * features["d_return"]
        for cost_bps in TRANSACTION_COST_BPS:
            rows.append(
                pd.DataFrame(
                    {
                        "date": features["date"],
                        "method": name,
                        "config_id": name,
                        "cost_bps": cost_bps,
                        "g_weight": g_weight,
                        "d_weight": 1.0 - g_weight,
                        "daily_turnover": 0.0,
                        "gross_return": gross,
                        "net_return": gross,
                    }
                ).dropna(subset=["net_return"])
            )
    for cost_bps in TRANSACTION_COST_BPS:
        rows.append(
            pd.DataFrame(
                {
                    "date": features["date"],
                    "method": "SPY Buy & Hold",
                    "config_id": "SPY Buy & Hold",
                    "cost_bps": cost_bps,
                    "g_weight": np.nan,
                    "d_weight": np.nan,
                    "daily_turnover": 0.0,
                    "gross_return": features["SPY"],
                    "net_return": features["SPY"],
                }
            ).dropna(subset=["net_return"])
        )
    return pd.concat(rows, ignore_index=True)


def load_old_best_local_returns() -> pd.DataFrame:
    if not SMOOTH_DAILY_RETURNS_PATH.exists() or not SMOOTH_SUPP_RETURNS_PATH.exists():
        features = build_feature_panel()
        features = features[features["date"] >= pd.Timestamp("2016-12-21")].reset_index(drop=True)
        score = old_best_local_score(features)
        weight = smooth_weight_from_score(score, max_tilt=0.50, tau_weight=0.75, eta=0.05)
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
                        "method": "Existing Smooth Score Best Local",
                        "config_id": "existing_best_local_tilt50",
                        "cost_bps": cost_bps,
                        "g_weight": deployed,
                        "d_weight": 1.0 - deployed,
                        "daily_turnover": turnover,
                        "score": score,
                        "score_z": expanding_z(score),
                        "gross_return": gross,
                        "net_return": net,
                    }
                ).dropna(subset=["net_return"])
            )
        return pd.concat(rows, ignore_index=True)

    selected = pd.read_csv(SMOOTH_SELECTED_SUMMARY_PATH, encoding="utf-8-sig")
    row = selected[selected["display_name"] == "Best Local Grid (tilt 50%)"].iloc[0]
    old = pd.concat(
        [
            pd.read_csv(SMOOTH_DAILY_RETURNS_PATH, encoding="utf-8-sig"),
            pd.read_csv(SMOOTH_SUPP_RETURNS_PATH, encoding="utf-8-sig"),
        ],
        ignore_index=True,
    )
    old["date"] = pd.to_datetime(old["date"]).dt.normalize()
    subset = old[(old["method"] == row["method"]) & (old["config_id"] == row["config_id"])].copy()
    subset["method"] = "Existing Smooth Score Best Local"
    subset["config_id"] = "existing_best_local_tilt50"
    return subset


def metrics_for_returns(returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    returns = returns.copy()
    returns["date"] = pd.to_datetime(returns["date"]).dt.normalize()
    returns = returns[returns["date"] >= pd.Timestamp(COMMON_START_DATE)]
    for (method, config_id, cost_bps), group in returns.groupby(["method", "config_id", "cost_bps"], sort=False):
        group = group.sort_values("date").copy()
        idx = pd.to_datetime(group["date"])
        ret = pd.Series(group["net_return"].to_numpy(), index=idx)
        turnover = pd.Series(group["daily_turnover"].to_numpy(), index=idx)
        weights = pd.Series(group["g_weight"].to_numpy(), index=idx)
        row = {"method": method, "config_id": config_id, "cost_bps": cost_bps}
        row.update(performance_metrics(ret, turnover=turnover, g_weight=weights))
        rows.append(row)
    return pd.DataFrame(rows)


def add_selection_score(metrics: pd.DataFrame) -> pd.DataFrame:
    out = metrics.copy()
    out["selection_score"] = np.nan
    mask = (out["cost_bps"] == PRIMARY_COST_BPS) & out["method"].isin(
        ["bond_credit_smooth_score", "bond_credit_core_only", "old_best_plus_bond_credit_incremental"]
    )
    subset = out[mask].copy()
    if subset.empty:
        return out
    score = (
        subset["sharpe"].rank(pct=True)
        + subset["calmar"].rank(pct=True)
        + subset["cagr"].rank(pct=True)
        + subset["max_drawdown"].rank(pct=True)
        + (-subset["annual_turnover"]).rank(pct=True)
    ) / 5.0
    out.loc[subset.index, "selection_score"] = score
    return out


def common_date_filter(returns: pd.DataFrame, keys: list[tuple[str, str]], cost_bps: int = PRIMARY_COST_BPS) -> pd.DataFrame:
    data = returns[returns["cost_bps"] == cost_bps].copy()
    date_sets = []
    for method, config_id in keys:
        dates = set(data[(data["method"] == method) & (data["config_id"] == config_id)]["date"])
        if dates:
            date_sets.append(dates)
    common = sorted(set.intersection(*date_sets)) if date_sets else []
    return data[data["date"].isin(common)].copy()


def build_equity_curves(returns: pd.DataFrame, display: dict[tuple[str, str], str], cost_bps: int = PRIMARY_COST_BPS) -> pd.DataFrame:
    keys = list(display)
    common = common_date_filter(returns, keys, cost_bps=cost_bps)
    curves = []
    for method, config_id in keys:
        group = common[(common["method"] == method) & (common["config_id"] == config_id)].sort_values("date")
        if group.empty:
            continue
        wealth = (1.0 + group["net_return"].astype(float)).cumprod()
        wealth = wealth / wealth.iloc[0]
        curves.append(pd.DataFrame({"date": pd.to_datetime(group["date"]), display[(method, config_id)]: wealth}))
    if not curves:
        return pd.DataFrame()
    out = curves[0]
    for curve in curves[1:]:
        out = out.merge(curve, on="date", how="inner")
    for col in out.columns:
        if col != "date":
            out[col] = out[col] / out[col].iloc[0]
    return out.sort_values("date").reset_index(drop=True)


def summary_for_display(returns: pd.DataFrame, display: dict[tuple[str, str], str], cost_bps: int = PRIMARY_COST_BPS) -> pd.DataFrame:
    keys = list(display)
    common = common_date_filter(returns, keys, cost_bps=cost_bps)
    rows = []
    for method, config_id in keys:
        group = common[(common["method"] == method) & (common["config_id"] == config_id)].sort_values("date")
        idx = pd.to_datetime(group["date"])
        ret = pd.Series(group["net_return"].to_numpy(), index=idx)
        turnover = pd.Series(group["daily_turnover"].to_numpy(), index=idx)
        weights = pd.Series(group["g_weight"].to_numpy(), index=idx)
        row = {"display_name": display[(method, config_id)], "method": method, "config_id": config_id, "cost_bps": cost_bps}
        row.update(performance_metrics(ret, turnover=turnover, g_weight=weights))
        rows.append(row)
    return pd.DataFrame(rows)


def plot_equity(equity: pd.DataFrame, title: str, path: Path) -> None:
    if equity.empty:
        return
    fig, ax = plt.subplots(figsize=(11, 6))
    for col in equity.columns:
        if col == "date":
            continue
        lw = 2.2 if "Bond/Credit" in col else 1.5
        ax.plot(equity["date"], equity[col], label=col, linewidth=lw)
    ax.set_title(title)
    ax.set_ylabel("Wealth, Rebased to 1")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def build_grid_outputs(features: pd.DataFrame, config_grid: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[tuple[str, str, int], pd.DataFrame]]:
    metric_rows = []
    returns_cache: dict[tuple[str, str, int], pd.DataFrame] = {}
    for _, config in config_grid.iterrows():
        strat = build_strategy_for_config(features, config)
        metrics = metrics_for_returns(strat)
        metric_rows.append(metrics)
        for (method, config_id, cost_bps), group in strat.groupby(["method", "config_id", "cost_bps"], sort=False):
            if cost_bps == PRIMARY_COST_BPS:
                returns_cache[(method, config_id, cost_bps)] = group.copy()
    metrics = add_selection_score(pd.concat(metric_rows, ignore_index=True))
    return metrics, config_grid, returns_cache


def selected_configs(metrics: pd.DataFrame) -> dict[str, tuple[str, str]]:
    dynamic = metrics[(metrics["cost_bps"] == PRIMARY_COST_BPS) & (metrics["method"] == "bond_credit_smooth_score")].copy()
    core = metrics[(metrics["cost_bps"] == PRIMARY_COST_BPS) & (metrics["method"] == "bond_credit_core_only")].copy()
    old_plus = metrics[(metrics["cost_bps"] == PRIMARY_COST_BPS) & (metrics["method"] == "old_best_plus_bond_credit_incremental")].copy()
    best = dynamic.sort_values("selection_score", ascending=False).iloc[0]
    best_core = core.sort_values("selection_score", ascending=False).iloc[0]
    best_old_plus = old_plus.sort_values("selection_score", ascending=False).iloc[0]
    return {
        "bond_credit_best": (best["method"], best["config_id"]),
        "bond_credit_core_only": (best_core["method"], best_core["config_id"]),
        "old_best_plus_credit": (best_old_plus["method"], best_old_plus["config_id"]),
        "old_best": ("Existing Smooth Score Best Local", "existing_best_local_tilt50"),
        "benchmark_50_50": ("50/50 G-D Buy & Hold", "50/50 G-D Buy & Hold"),
        "benchmark_100_g": ("100% G Buy & Hold", "100% G Buy & Hold"),
        "benchmark_100_d": ("100% D Buy & Hold", "100% D Buy & Hold"),
        "benchmark_spy": ("SPY Buy & Hold", "SPY Buy & Hold"),
    }


def collect_selected_returns(
    all_returns_cache: dict[tuple[str, str, int], pd.DataFrame],
    features: pd.DataFrame,
    selected: dict[str, tuple[str, str]],
) -> pd.DataFrame:
    parts = []
    for key in ("bond_credit_best", "bond_credit_core_only", "old_best_plus_credit"):
        method, config_id = selected[key]
        for cost_bps in TRANSACTION_COST_BPS:
            cache_key = (method, config_id, PRIMARY_COST_BPS)
            base = all_returns_cache[cache_key].copy()
            config = config_grid_global[(config_grid_global["method"] == method) & (config_grid_global["config_id"] == config_id)].iloc[0]
            strat = build_strategy_for_config(features, config)
            parts.append(strat)
            break
    parts.append(static_benchmark_returns(features))
    parts.append(load_old_best_local_returns())
    return pd.concat(parts, ignore_index=True)


config_grid_global = pd.DataFrame()


def cost_sensitivity(metrics: pd.DataFrame, config: tuple[str, str]) -> pd.DataFrame:
    method, config_id = config
    return metrics[(metrics["method"] == method) & (metrics["config_id"] == config_id)].sort_values("cost_bps")


def tilt_summary(metrics: pd.DataFrame) -> pd.DataFrame:
    data = metrics[(metrics["method"] == "bond_credit_smooth_score") & (metrics["cost_bps"] == PRIMARY_COST_BPS)].copy()
    data = data.merge(config_grid_global, on=["method", "config_id"], how="left")
    rows = []
    for tilt, group in data.groupby("max_tilt"):
        best = group.sort_values("selection_score", ascending=False).iloc[0]
        rows.append(best)
    return pd.DataFrame(rows).sort_values("max_tilt")


def comparison_table(summary: pd.DataFrame) -> pd.DataFrame:
    target = summary[summary["display_name"] == "Bond/Credit Smooth Score Best"].iloc[0]
    rows = []
    for _, row in summary.iterrows():
        if row["display_name"] == target["display_name"]:
            continue
        excess = target["cagr"] - row["cagr"]
        rows.append(
            {
                "comparison": f"Bond/Credit Best - {row['display_name']}",
                "annualized_excess_return": excess,
                "max_dd_diff": target["max_drawdown"] - row["max_drawdown"],
                "sharpe_diff": target["sharpe"] - row["sharpe"],
                "turnover_diff": target["annual_turnover"] - row["annual_turnover"],
            }
        )
    if {"Old Best + Bond/Credit Incremental", "Existing Smooth Score Best Local"}.issubset(set(summary["display_name"])):
        old_plus = summary[summary["display_name"] == "Old Best + Bond/Credit Incremental"].iloc[0]
        old = summary[summary["display_name"] == "Existing Smooth Score Best Local"].iloc[0]
        rows.append(
            {
                "comparison": "Old Best + Bond/Credit Incremental - Existing Smooth Score Best Local",
                "annualized_excess_return": old_plus["cagr"] - old["cagr"],
                "max_dd_diff": old_plus["max_drawdown"] - old["max_drawdown"],
                "sharpe_diff": old_plus["sharpe"] - old["sharpe"],
                "turnover_diff": old_plus["annual_turnover"] - old["annual_turnover"],
            }
        )
        rows.append(
            {
                "comparison": "Old Best + Bond/Credit Incremental - Bond/Credit Smooth Score Best",
                "annualized_excess_return": old_plus["cagr"] - target["cagr"],
                "max_dd_diff": old_plus["max_drawdown"] - target["max_drawdown"],
                "sharpe_diff": old_plus["sharpe"] - target["sharpe"],
                "turnover_diff": old_plus["annual_turnover"] - target["annual_turnover"],
            }
        )
    return pd.DataFrame(rows)


def yearly_metrics(selected_returns: pd.DataFrame, display: dict[tuple[str, str], str]) -> pd.DataFrame:
    common = common_date_filter(selected_returns, list(display), cost_bps=PRIMARY_COST_BPS)
    common["year"] = pd.to_datetime(common["date"]).dt.year
    rows = []
    for (method, config_id, year), group in common.groupby(["method", "config_id", "year"], sort=True):
        idx = pd.to_datetime(group["date"])
        ret = pd.Series(group["net_return"].to_numpy(), index=idx)
        turnover = pd.Series(group["daily_turnover"].to_numpy(), index=idx)
        weights = pd.Series(group["g_weight"].to_numpy(), index=idx)
        row = {"display_name": display[(method, config_id)], "method": method, "config_id": config_id, "year": year}
        row.update(performance_metrics(ret, turnover=turnover, g_weight=weights))
        rows.append(row)
    return pd.DataFrame(rows)


def score_diagnostics(features: pd.DataFrame, selected_config: pd.Series) -> pd.DataFrame:
    score = score_from_config(features, selected_config)
    data = pd.DataFrame(
        {
            "date": features["date"],
            "score_z": expanding_z(score),
            "future_gd_return_63d": features["future_gd_return_63d"],
        }
    ).dropna()
    data = data[data["date"] >= pd.Timestamp(COMMON_START_DATE)]
    data["score_quantile"] = pd.qcut(data["score_z"], 5, labels=["Q1", "Q2", "Q3", "Q4", "Q5"], duplicates="drop")
    rows = []
    for q, group in data.groupby("score_quantile", observed=False):
        rows.append(
            {
                "score_quantile": str(q),
                "n": int(len(group)),
                "start_date": group["date"].min().date().isoformat(),
                "end_date": group["date"].max().date().isoformat(),
                "realized_future_gd_mean_63d": float(group["future_gd_return_63d"].mean()),
                "realized_future_gd_median_63d": float(group["future_gd_return_63d"].median()),
                "win_rate": float((group["future_gd_return_63d"] > 0).mean()),
            }
        )
    return pd.DataFrame(rows)


def static_grid_comparison(selected_returns: pd.DataFrame, target_key: tuple[str, str], display: dict[tuple[str, str], str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    common = common_date_filter(selected_returns, list(display), cost_bps=PRIMARY_COST_BPS)
    target = common[(common["method"] == target_key[0]) & (common["config_id"] == target_key[1])].sort_values("date")
    idx = pd.to_datetime(target["date"])
    target_ret = pd.Series(target["net_return"].to_numpy(), index=idx)
    target_metrics = performance_metrics(
        target_ret,
        turnover=pd.Series(target["daily_turnover"].to_numpy(), index=idx),
        g_weight=pd.Series(target["g_weight"].to_numpy(), index=idx),
    )
    base = common[common["method"].isin(["100% G Buy & Hold", "100% D Buy & Hold"])]
    g = base[base["method"] == "100% G Buy & Hold"].set_index("date")["net_return"].astype(float)
    d = base[base["method"] == "100% D Buy & Hold"].set_index("date")["net_return"].astype(float)
    rows = []
    curve_parts = [pd.DataFrame({"date": idx, "Bond/Credit Smooth Score Best": (1 + target_ret).cumprod().to_numpy()})]
    for weight in np.linspace(0, 1, 101):
        ret = weight * g.reindex(target["date"]).to_numpy() + (1 - weight) * d.reindex(target["date"]).to_numpy()
        ret_s = pd.Series(ret, index=idx)
        m = performance_metrics(ret_s, turnover=pd.Series(0.0, index=idx), g_weight=pd.Series(weight, index=idx))
        rows.append({"static_g_weight": weight, **m})
    grid = pd.DataFrame(rows)
    vol_match = grid.iloc[(grid["ann_vol"] - target_metrics["ann_vol"]).abs().argsort().iloc[0]]
    dd_match = grid.iloc[(grid["max_drawdown"] - target_metrics["max_drawdown"]).abs().argsort().iloc[0]]
    best_sharpe = grid.sort_values("sharpe", ascending=False).iloc[0]
    under_dd = grid[grid["max_drawdown"] >= target_metrics["max_drawdown"]]
    best_under_dd = under_dd.sort_values("cagr", ascending=False).iloc[0] if not under_dd.empty else best_sharpe
    picks = [
        ("Target Bond/Credit Smooth Score", np.nan, target_metrics),
        (f"Vol-Matched Static G/D ({vol_match['static_g_weight']:.0%} G)", vol_match["static_g_weight"], vol_match.to_dict()),
        (f"DD-Matched Static G/D ({dd_match['static_g_weight']:.0%} G)", dd_match["static_g_weight"], dd_match.to_dict()),
        (f"Best Sharpe Static G/D ({best_sharpe['static_g_weight']:.0%} G)", best_sharpe["static_g_weight"], best_sharpe.to_dict()),
        (f"Best CAGR Static under Target DD ({best_under_dd['static_g_weight']:.0%} G)", best_under_dd["static_g_weight"], best_under_dd.to_dict()),
    ]
    comparison = []
    curves = pd.DataFrame({"date": idx})
    curves["Bond/Credit Smooth Score Best"] = (1 + target_ret).cumprod().to_numpy()
    for label, weight, metrics in picks:
        row = {"display_name": label, "static_g_weight": weight}
        row.update({k: metrics.get(k, np.nan) for k in ["final_wealth", "cagr", "ann_vol", "sharpe", "max_drawdown", "calmar", "annual_turnover", "avg_g_weight"]})
        comparison.append(row)
        if not pd.isna(weight):
            ret = weight * g.reindex(target["date"]).to_numpy() + (1 - weight) * d.reindex(target["date"]).to_numpy()
            curves[label] = (1 + pd.Series(ret, index=idx)).cumprod().to_numpy()
    for col in curves.columns:
        if col != "date":
            curves[col] = curves[col] / curves[col].iloc[0]
    return pd.DataFrame(comparison), curves


def select_best_config(metrics: pd.DataFrame, train_dates: set[pd.Timestamp], method_filter: str = "bond_credit_smooth_score") -> tuple[str, str]:
    # This helper is replaced by direct train metrics in walk_forward because the
    # full metrics table is all-sample. Kept for readability.
    data = metrics[(metrics["method"] == method_filter) & (metrics["cost_bps"] == PRIMARY_COST_BPS)]
    best = data.sort_values("selection_score", ascending=False).iloc[0]
    return str(best["method"]), str(best["config_id"])


def metrics_from_group(group: pd.DataFrame) -> dict[str, float | int | str]:
    idx = pd.to_datetime(group["date"])
    ret = pd.Series(group["net_return"].to_numpy(), index=idx)
    turnover = pd.Series(group["daily_turnover"].to_numpy(), index=idx)
    weights = pd.Series(group["g_weight"].to_numpy(), index=idx)
    return performance_metrics(ret, turnover=turnover, g_weight=weights)


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
    method_filter: str = "bond_credit_smooth_score",
    output_method: str | None = None,
    output_config_id: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    configs = list(zip(config_grid[config_grid["method"] == method_filter]["method"], config_grid[config_grid["method"] == method_filter]["config_id"]))
    output_method = output_method or f"Bond/Credit WF {mode.title()}"
    output_config_id = output_config_id or f"wf_{mode}"
    all_dates = sorted(
        pd.to_datetime(next(iter(config_returns.values()))["date"]).dropna().unique()
    )
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
        if train_metrics.empty:
            continue
        train_metrics["selection_score"] = score_rank_for_train(train_metrics)
        best = train_metrics.sort_values("selection_score", ascending=False).iloc[0]
        method, config_id = str(best["method"]), str(best["config_id"])
        selected_returns = config_returns[(method, config_id, PRIMARY_COST_BPS)]
        test = selected_returns[pd.to_datetime(selected_returns["date"]).isin(test_dates)].copy()
        test["method"] = output_method
        test["config_id"] = output_config_id
        pieces.append(test)
        selections.append(
            {
                "mode": mode,
                "test_start": pd.Timestamp(test_dates[0]).date().isoformat(),
                "test_end": pd.Timestamp(test_dates[-1]).date().isoformat(),
                "train_start": pd.Timestamp(all_dates[train_start_idx]).date().isoformat(),
                "train_end": pd.Timestamp(all_dates[train_end_idx - 1]).date().isoformat(),
                "selected_config_id": config_id,
                "train_selection_score": float(best["selection_score"]),
                "train_sharpe": float(best["sharpe"]),
                "train_cagr": float(best["cagr"]),
                "train_max_drawdown": float(best["max_drawdown"]),
            }
        )
    return pd.concat(pieces, ignore_index=True), pd.DataFrame(selections)


def fixed_parameter_validation(
    config_returns: dict[tuple[str, str, int], pd.DataFrame],
    config_grid: pd.DataFrame,
    start_date: str,
    method_filter: str = "bond_credit_smooth_score",
    output_method: str = "Bond/Credit Fixed Parameter",
    output_config_id: str = "fixed_parameter",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    configs = list(zip(config_grid[config_grid["method"] == method_filter]["method"], config_grid[config_grid["method"] == method_filter]["config_id"]))
    all_dates = sorted(pd.to_datetime(next(iter(config_returns.values()))["date"]).dropna().unique())
    start_ts = pd.Timestamp(start_date)
    start_idx = next(i for i, d in enumerate(all_dates) if d >= start_ts)
    if start_idx < VALIDATION_INITIAL_TRAIN_WINDOW:
        start_idx = VALIDATION_INITIAL_TRAIN_WINDOW
    train_dates = set(all_dates[:start_idx])
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
    selected = config_returns[(str(best["method"]), str(best["config_id"]), PRIMARY_COST_BPS)].copy()
    selected = selected[pd.to_datetime(selected["date"]) >= start_ts].copy()
    selected["method"] = output_method
    selected["config_id"] = output_config_id
    meta = pd.DataFrame(
        [
            {
                "validation_start": pd.Timestamp(start_ts).date().isoformat(),
                "calibration_start": pd.Timestamp(all_dates[0]).date().isoformat(),
                "calibration_end": pd.Timestamp(all_dates[start_idx - 1]).date().isoformat(),
                "selected_config_id": str(best["config_id"]),
                "train_selection_score": float(best["selection_score"]),
                "train_sharpe": float(best["sharpe"]),
                "train_cagr": float(best["cagr"]),
                "train_max_drawdown": float(best["max_drawdown"]),
            }
        ]
    )
    return selected, meta


def validation_summary(validation_returns: pd.DataFrame, benchmark_returns: pd.DataFrame, start_date: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    benches = benchmark_returns[benchmark_returns["cost_bps"] == PRIMARY_COST_BPS].copy()
    benches = benches[pd.to_datetime(benches["date"]) >= pd.Timestamp(start_date)]
    combined = pd.concat([validation_returns, benches], ignore_index=True)
    display = {
        ("Bond/Credit WF Expanding", "wf_expanding"): "Bond/Credit WF Expanding",
        ("Bond/Credit WF Rolling", "wf_rolling"): "Bond/Credit WF Rolling",
        ("Bond/Credit Fixed Parameter", "fixed_parameter"): "Bond/Credit Fixed Parameter",
        ("Old+Credit WF Expanding", "old_plus_wf_expanding"): "Old+Credit WF Expanding",
        ("Old+Credit WF Rolling", "old_plus_wf_rolling"): "Old+Credit WF Rolling",
        ("Old+Credit Fixed Parameter", "old_plus_fixed_parameter"): "Old+Credit Fixed Parameter",
        ("Existing Smooth Score Best Local", "existing_best_local_tilt50"): "Existing Smooth Score Best Local",
        ("50/50 G-D Buy & Hold", "50/50 G-D Buy & Hold"): "50/50 G-D Buy & Hold",
        ("100% G Buy & Hold", "100% G Buy & Hold"): "100% G Buy & Hold",
        ("SPY Buy & Hold", "SPY Buy & Hold"): "SPY Buy & Hold",
    }
    equity = build_equity_curves(combined, display, cost_bps=PRIMARY_COST_BPS)
    summary = summary_for_display(combined, display, cost_bps=PRIMARY_COST_BPS)
    return summary, equity


def fmt_pct(x: float) -> str:
    if pd.isna(x):
        return ""
    return f"{x:.2%}"


def fmt_num(x: float) -> str:
    if pd.isna(x):
        return ""
    return f"{x:.2f}"


def markdown_table(df: pd.DataFrame, columns: list[str], pct_cols: set[str] | None = None, num_cols: set[str] | None = None, max_rows: int = 30) -> list[str]:
    pct_cols = pct_cols or set()
    num_cols = num_cols or set()
    if df.empty:
        return ["_No data._"]
    view = df[columns].head(max_rows).copy()
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in view.to_dict("records"):
        vals = []
        for col in columns:
            value = row[col]
            if col in pct_cols:
                vals.append(fmt_pct(value))
            elif col in num_cols:
                vals.append(fmt_num(value))
            else:
                vals.append("" if pd.isna(value) else str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return lines


def factor_attribution_view() -> pd.DataFrame:
    factor = pd.read_csv(FACTOR_PORTFOLIO_TABLE, encoding="utf-8-sig")
    view = factor[
        [
            "portfolio",
            "n_obs",
            "alpha_annualized",
            "alpha_t_nw",
            "beta_mkt_rf",
            "beta_smb",
            "beta_hml",
            "beta_rmw",
            "beta_cma",
            "beta_mom",
            "adj_r2",
        ]
    ].copy()
    view = view.rename(
        columns={
            "n_obs": "n",
            "alpha_annualized": "alpha_ann",
            "alpha_t_nw": "alpha_t_NW",
            "beta_mkt_rf": "MKT",
            "beta_smb": "SMB",
            "beta_hml": "HML",
            "beta_rmw": "RMW",
            "beta_cma": "CMA",
            "beta_mom": "MOM",
            "adj_r2": "adj_R2",
        }
    )
    view["n"] = view["n"].map(lambda x: f"{int(x)}")
    view["alpha_ann"] = view["alpha_ann"].map(fmt_pct)
    view["alpha_t_NW"] = view["alpha_t_NW"].map(lambda x: f"{x:.2f}")
    for col in ["MKT", "SMB", "HML", "RMW", "CMA", "MOM", "adj_R2"]:
        view[col] = view[col].map(lambda x: f"{x:.3f}")
    return view


def write_report(
    config_grid: pd.DataFrame,
    metrics: pd.DataFrame,
    selected: dict[str, tuple[str, str]],
    selected_summary: pd.DataFrame,
    comparisons: pd.DataFrame,
    tilt: pd.DataFrame,
    cost: pd.DataFrame,
    old_plus_cost: pd.DataFrame,
    score_diag: pd.DataFrame,
    static_comp: pd.DataFrame,
    validation_sum: pd.DataFrame,
    post_sum: pd.DataFrame,
    yearly: pd.DataFrame,
    diag_main: pd.DataFrame,
    diag_inter: pd.DataFrame,
) -> Path:
    report_path = REPORT_DIR / "phase1_bond_credit_smooth_policy_v1_full_report_en.md"
    best_method, best_id = selected["bond_credit_best"]
    best_config = config_grid[(config_grid["method"] == best_method) & (config_grid["config_id"] == best_id)].iloc[0]
    old_plus_method, old_plus_id = selected["old_best_plus_credit"]
    old_plus_config = config_grid[(config_grid["method"] == old_plus_method) & (config_grid["config_id"] == old_plus_id)].iloc[0]
    start = selected_summary["start_date"].iloc[0]
    end = selected_summary["end_date"].iloc[0]
    lines: list[str] = []
    lines.append("# Phase 1 Bond/Credit-Augmented Smooth Policy Full Report")
    lines.append("")
    lines.append("Report scope: full Phase 1 extension after adding aligned bond and credit variables. This is an empirical report, not a manuscript.")
    lines.append("")
    lines.append("## 0. Scope")
    lines.append("")
    lines.append("This report follows the structure of the 2016 full Phase 1 report. It keeps the original factor-attribution boundary unchanged and adds a new bond/credit-augmented smooth-score policy module. The recent-only HY/IG OAS data are excluded from formal policy tests because they do not align with the full 2017-2026 policy window.")
    lines.append("")
    lines.append("## 1. Data Start and Warmup")
    lines.append("")
    lines.append("- G/D source returns start on `2016-12-21`.")
    lines.append("- Complete policy comparison starts after natural trailing-signal warmup on `2017-06-28`.")
    lines.append(f"- Main aligned policy comparison: `{start}` to `{end}`.")
    lines.append("- All policy tests use daily trading-day data.")
    lines.append("- Signals are formed after the close and deployed on the next trading day.")
    lines.append("")
    lines.append("## 2. Module 1: Factor Attribution Boundary")
    lines.append("")
    lines.append("This extension does not rerun or reinterpret the FF5+MOM attribution. The original Phase 1 attribution remains the boundary condition: `G-D` is a style-exposure portfolio, not a newly discovered standalone alpha factor.")
    lines.append("")
    lines.extend(
        markdown_table(
            factor_attribution_view(),
            ["portfolio", "n", "alpha_ann", "alpha_t_NW", "MKT", "SMB", "HML", "RMW", "CMA", "MOM", "adj_R2"],
            max_rows=10,
        )
    )
    lines.append("")
    lines.append("Interpretation: `G-D` has positive market beta, strongly negative HML exposure, negative CMA exposure, and positive MOM exposure. Its annualized alpha is positive but not statistically significant under Newey-West standard errors. Therefore the bond/credit extension is evaluated as a timing overlay for known style exposures, not as a test of a new independent alpha.")
    lines.append("")
    lines.append("## 3. Diagnostic Gate Summary")
    lines.append("")
    lines.append("The bond/credit diagnostic gate identifies three main effects and one interaction worth carrying into the policy test:")
    lines.append("")
    lines.extend(
        markdown_table(
            diag_main[diag_main["passes_gate"] == True],
            ["variable", "question", "coef_63d", "t_hac_63d", "nonoverlap_coef_63d", "passes_gate"],
            pct_cols={"coef_63d", "nonoverlap_coef_63d"},
            num_cols={"t_hac_63d"},
            max_rows=20,
        )
    )
    lines.append("")
    lines.extend(
        markdown_table(
            diag_inter[diag_inter["final_pass"] == True],
            ["variable", "question", "coef_63d", "t_hac_63d", "resid_coef_63d", "resid_t_63d", "final_pass"],
            pct_cols={"coef_63d", "resid_coef_63d"},
            num_cols={"t_hac_63d", "resid_t_63d"},
            max_rows=20,
        )
    )
    lines.append("")
    lines.append("## 4. Bond/Credit Smooth Score Formula")
    lines.append("")
    lines.append("Direction-normalized variables:")
    lines.append("")
    lines.append("```text")
    lines.append("d      = -expanding_z(SPY drawdown)")
    lines.append("ce     = -expanding_z(BAA10Y spread 21d change)")
    lines.append("g126   =  expanding_z(G-D trailing 126d)")
    lines.append("cs     =  expanding_z(BAA10Y spread)")
    lines.append("r      = -expanding_z(10Y yield 21d change)")
    lines.append("z_r_cs =  expanding_z(r * cs)")
    lines.append("")
    lines.append("score = alpha_d * d")
    lines.append("      + (1 - alpha_d) * ce")
    lines.append("      - lambda_g126 * g126")
    lines.append("      + lambda_interaction * z_r_cs")
    lines.append("```")
    lines.append("")
    lines.append("Weight mapping:")
    lines.append("")
    lines.append("```text")
    lines.append("G_target = 50% + max_tilt * tanh(expanding_z(score) / tau_weight)")
    lines.append("G_weight_t = (1 - eta) * G_weight_{t-1} + eta * G_target_t")
    lines.append("D_weight_t = 1 - G_weight_t")
    lines.append("```")
    lines.append("")
    lines.append("Selected configuration:")
    lines.append("")
    lines.extend(
        markdown_table(
            pd.DataFrame([best_config]),
            ["config_id", "alpha_d", "lambda_credit", "lambda_g126", "lambda_interaction", "max_tilt", "tau_weight", "eta"],
            num_cols={"alpha_d", "lambda_credit", "lambda_g126", "lambda_interaction", "max_tilt", "tau_weight", "eta"},
        )
    )
    lines.append("")
    lines.append("Strict incremental design:")
    lines.append("")
    lines.append("The `Old Best + Bond/Credit Incremental` experiment keeps the original Best Local structure fixed at `alpha=0.50`, `lambda_stress=0.50`, `lambda_crowded=0.05`, `max_tilt=0.50`, `tau_weight=0.75`, and `eta=0.05`. It only adds two bond/credit terms: `credit relief` and `rate relief × credit stress`. This is the strict test of whether bond/credit information improves the old main strategy rather than replacing it.")
    lines.append("")
    lines.extend(
        markdown_table(
            pd.DataFrame([old_plus_config]),
            ["config_id", "lambda_credit", "lambda_interaction", "max_tilt", "tau_weight", "eta"],
            num_cols={"lambda_credit", "lambda_interaction", "max_tilt", "tau_weight", "eta"},
        )
    )
    lines.append("")
    lines.append("## 5. Grid and Tilt Test")
    lines.append("")
    lines.append(f"Total candidate configurations tested: `{len(config_grid)}`.")
    lines.append("")
    lines.extend(
        markdown_table(
            tilt,
            ["max_tilt", "config_id", "cagr", "ann_vol", "sharpe", "max_drawdown", "calmar", "annual_turnover", "selection_score"],
            pct_cols={"max_tilt", "cagr", "ann_vol", "max_drawdown", "annual_turnover"},
            num_cols={"sharpe", "calmar", "selection_score"},
            max_rows=10,
        )
    )
    lines.append("")
    lines.append("![Tilt Equity Curves](../plots/bond_credit_smooth_policy_v1_tilt_equity_curves.png)")
    lines.append("")
    lines.append("## 6. Cost Sensitivity of Selected Configuration")
    lines.append("")
    lines.append("Bond/Credit Smooth Score Best:")
    lines.append("")
    lines.extend(
        markdown_table(
            cost,
            ["cost_bps", "cagr", "ann_vol", "sharpe", "max_drawdown", "calmar", "annual_turnover", "avg_g_weight", "final_wealth"],
            pct_cols={"cagr", "ann_vol", "max_drawdown", "annual_turnover", "avg_g_weight"},
            num_cols={"sharpe", "calmar", "final_wealth"},
            max_rows=10,
        )
    )
    lines.append("")
    lines.append("Old Best + Bond/Credit Incremental:")
    lines.append("")
    lines.extend(
        markdown_table(
            old_plus_cost,
            ["cost_bps", "cagr", "ann_vol", "sharpe", "max_drawdown", "calmar", "annual_turnover", "avg_g_weight", "final_wealth"],
            pct_cols={"cagr", "ann_vol", "max_drawdown", "annual_turnover", "avg_g_weight"},
            num_cols={"sharpe", "calmar", "final_wealth"},
            max_rows=10,
        )
    )
    lines.append("")
    lines.append("## 7. Main Aligned Strategy Comparison")
    lines.append("")
    lines.extend(
        markdown_table(
            selected_summary,
            ["display_name", "start_date", "end_date", "cagr", "ann_vol", "sharpe", "max_drawdown", "calmar", "annual_turnover", "avg_g_weight", "final_wealth"],
            pct_cols={"cagr", "ann_vol", "max_drawdown", "annual_turnover", "avg_g_weight"},
            num_cols={"sharpe", "calmar", "final_wealth"},
            max_rows=20,
        )
    )
    lines.append("")
    lines.append("### 7.1 Incremental Comparison")
    lines.append("")
    lines.extend(
        markdown_table(
            comparisons,
            ["comparison", "annualized_excess_return", "max_dd_diff", "sharpe_diff", "turnover_diff"],
            pct_cols={"annualized_excess_return", "max_dd_diff", "turnover_diff"},
            num_cols={"sharpe_diff"},
            max_rows=20,
        )
    )
    lines.append("")
    lines.append("### 7.2 Equity Curves")
    lines.append("")
    lines.append("![Main Equity Curves](../plots/bond_credit_smooth_policy_v1_main_equity_curves.png)")
    lines.append("")
    lines.append("## 8. Vol-Matched and Static G/D Comparisons")
    lines.append("")
    lines.extend(
        markdown_table(
            static_comp,
            ["display_name", "static_g_weight", "final_wealth", "cagr", "ann_vol", "sharpe", "max_drawdown", "calmar", "annual_turnover", "avg_g_weight"],
            pct_cols={"static_g_weight", "cagr", "ann_vol", "max_drawdown", "annual_turnover", "avg_g_weight"},
            num_cols={"final_wealth", "sharpe", "calmar"},
            max_rows=20,
        )
    )
    lines.append("")
    lines.append("![Static Comparison Equity Curves](../plots/bond_credit_smooth_policy_v1_static_comparison_equity_curves.png)")
    lines.append("")
    lines.append("## 9. OOS Validation: Expanding, Rolling, and Fixed Parameter")
    lines.append("")
    lines.extend(
        markdown_table(
            validation_sum,
            ["display_name", "start_date", "end_date", "cagr", "ann_vol", "sharpe", "max_drawdown", "calmar", "annual_turnover", "avg_g_weight", "final_wealth"],
            pct_cols={"cagr", "ann_vol", "max_drawdown", "annual_turnover", "avg_g_weight"},
            num_cols={"sharpe", "calmar", "final_wealth"},
            max_rows=20,
        )
    )
    lines.append("")
    lines.append("![OOS Validation Equity Curves](../plots/bond_credit_smooth_policy_v1_oos_validation_equity_curves.png)")
    lines.append("")
    lines.append("## 10. Post-2022 OOS Validation")
    lines.append("")
    lines.extend(
        markdown_table(
            post_sum,
            ["display_name", "start_date", "end_date", "cagr", "ann_vol", "sharpe", "max_drawdown", "calmar", "annual_turnover", "avg_g_weight", "final_wealth"],
            pct_cols={"cagr", "ann_vol", "max_drawdown", "annual_turnover", "avg_g_weight"},
            num_cols={"sharpe", "calmar", "final_wealth"},
            max_rows=20,
        )
    )
    lines.append("")
    lines.append("![Post-2022 Validation Equity Curves](../plots/bond_credit_smooth_policy_v1_post2022_validation_equity_curves.png)")
    lines.append("")
    lines.append("## 11. Score Sorting Diagnostics")
    lines.append("")
    lines.extend(
        markdown_table(
            score_diag,
            ["score_quantile", "n", "start_date", "end_date", "realized_future_gd_mean_63d", "realized_future_gd_median_63d", "win_rate"],
            pct_cols={"realized_future_gd_mean_63d", "realized_future_gd_median_63d", "win_rate"},
            max_rows=10,
        )
    )
    lines.append("")
    lines.append("## 12. Yearly Performance")
    lines.append("")
    lines.extend(
        markdown_table(
            yearly[yearly["display_name"].isin(["Bond/Credit Smooth Score Best", "Old Best + Bond/Credit Incremental", "Existing Smooth Score Best Local", "50/50 G-D Buy & Hold", "100% G Buy & Hold"])],
            ["display_name", "year", "start_date", "end_date", "cagr", "sharpe", "max_drawdown", "annual_turnover", "avg_g_weight"],
            pct_cols={"cagr", "max_drawdown", "annual_turnover", "avg_g_weight"},
            num_cols={"sharpe"},
            max_rows=80,
        )
    )
    lines.append("")
    lines.append("## 13. Final Interpretation")
    lines.append("")
    lines.append("- The bond/credit extension adds an economically interpretable credit-relief channel and a `rate relief × credit stress` interaction.")
    lines.append("- The strict incremental branch tests whether those terms improve the already-selected old Best Local structure, instead of comparing a new score against the old score only.")
    lines.append("- This report evaluates whether that additional information improves the deployable G/D smooth policy, not whether it creates a new standalone alpha factor.")
    lines.append("- Results should be interpreted against the existing smooth-score benchmark, static G/D allocations, 100% G, SPY, and OOS validation paths.")
    lines.append("")
    lines.append("## 14. Output Files")
    lines.append("")
    for path in [
        INPUT_DIR / "bond_credit_smooth_policy_v1_feature_panel.csv",
        TABLE_DIR / "bond_credit_smooth_policy_v1_config_grid.csv",
        TABLE_DIR / "bond_credit_smooth_policy_v1_grid_metrics.csv",
        TABLE_DIR / "bond_credit_smooth_policy_v1_selected_summary.csv",
        TABLE_DIR / "bond_credit_smooth_policy_v1_main_equity_curves.csv",
        TABLE_DIR / "bond_credit_smooth_policy_v1_oos_validation_summary.csv",
        TABLE_DIR / "bond_credit_smooth_policy_v1_post2022_validation_summary.csv",
    ]:
        lines.append(f"- `{path}`")
    lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> None:
    ensure_dirs()
    features = build_feature_panel()
    features = features[features["date"] >= pd.Timestamp("2016-12-21")].reset_index(drop=True)
    config_grid = generate_config_grid()
    global config_grid_global
    config_grid_global = config_grid.copy()
    metrics, _, returns_cache = build_grid_outputs(features, config_grid)
    selected = selected_configs(metrics)
    selected_returns = collect_selected_returns(returns_cache, features, selected)
    display = {
        selected["bond_credit_best"]: "Bond/Credit Smooth Score Best",
        selected["bond_credit_core_only"]: "Bond/Credit Core Only",
        selected["old_best_plus_credit"]: "Old Best + Bond/Credit Incremental",
        selected["old_best"]: "Existing Smooth Score Best Local",
        selected["benchmark_50_50"]: "50/50 G-D Buy & Hold",
        selected["benchmark_100_g"]: "100% G Buy & Hold",
        selected["benchmark_100_d"]: "100% D Buy & Hold",
        selected["benchmark_spy"]: "SPY Buy & Hold",
    }
    selected_summary = summary_for_display(selected_returns, display)
    main_equity = build_equity_curves(selected_returns, display)
    comparisons = comparison_table(selected_summary)
    tilt = tilt_summary(metrics)
    best_method, best_id = selected["bond_credit_best"]
    cost = cost_sensitivity(metrics, selected["bond_credit_best"])
    old_plus_cost = cost_sensitivity(metrics, selected["old_best_plus_credit"])
    best_config = config_grid[(config_grid["method"] == best_method) & (config_grid["config_id"] == best_id)].iloc[0]
    score_diag = score_diagnostics(features, best_config)
    yearly = yearly_metrics(selected_returns, display)
    static_comp, static_equity = static_grid_comparison(selected_returns, selected["bond_credit_best"], display)

    # Validation returns use only grid configurations and existing/static benchmarks.
    wf_exp, sel_exp = walk_forward_validation(returns_cache, config_grid, start_date="2018-06-28", mode="expanding")
    wf_roll, sel_roll = walk_forward_validation(returns_cache, config_grid, start_date="2018-06-28", mode="rolling")
    fixed, fixed_meta = fixed_parameter_validation(returns_cache, config_grid, start_date="2018-06-28")
    old_wf_exp, old_sel_exp = walk_forward_validation(
        returns_cache,
        config_grid,
        start_date="2018-06-28",
        mode="expanding",
        method_filter="old_best_plus_bond_credit_incremental",
        output_method="Old+Credit WF Expanding",
        output_config_id="old_plus_wf_expanding",
    )
    old_wf_roll, old_sel_roll = walk_forward_validation(
        returns_cache,
        config_grid,
        start_date="2018-06-28",
        mode="rolling",
        method_filter="old_best_plus_bond_credit_incremental",
        output_method="Old+Credit WF Rolling",
        output_config_id="old_plus_wf_rolling",
    )
    old_fixed, old_fixed_meta = fixed_parameter_validation(
        returns_cache,
        config_grid,
        start_date="2018-06-28",
        method_filter="old_best_plus_bond_credit_incremental",
        output_method="Old+Credit Fixed Parameter",
        output_config_id="old_plus_fixed_parameter",
    )
    benchmark_for_validation = selected_returns[
        selected_returns["method"].isin(["Existing Smooth Score Best Local", "50/50 G-D Buy & Hold", "100% G Buy & Hold", "SPY Buy & Hold"])
    ].copy()
    val_summary, val_equity = validation_summary(
        pd.concat([wf_exp, wf_roll, fixed, old_wf_exp, old_wf_roll, old_fixed], ignore_index=True),
        benchmark_for_validation,
        "2018-06-28",
    )

    post_exp, post_sel_exp = walk_forward_validation(returns_cache, config_grid, start_date=POST_2022_START_DATE, mode="expanding")
    post_roll, post_sel_roll = walk_forward_validation(returns_cache, config_grid, start_date=POST_2022_START_DATE, mode="rolling")
    post_fixed, post_fixed_meta = fixed_parameter_validation(returns_cache, config_grid, start_date=POST_2022_START_DATE)
    post_old_exp, post_old_sel_exp = walk_forward_validation(
        returns_cache,
        config_grid,
        start_date=POST_2022_START_DATE,
        mode="expanding",
        method_filter="old_best_plus_bond_credit_incremental",
        output_method="Old+Credit WF Expanding",
        output_config_id="old_plus_wf_expanding",
    )
    post_old_roll, post_old_sel_roll = walk_forward_validation(
        returns_cache,
        config_grid,
        start_date=POST_2022_START_DATE,
        mode="rolling",
        method_filter="old_best_plus_bond_credit_incremental",
        output_method="Old+Credit WF Rolling",
        output_config_id="old_plus_wf_rolling",
    )
    post_old_fixed, post_old_fixed_meta = fixed_parameter_validation(
        returns_cache,
        config_grid,
        start_date=POST_2022_START_DATE,
        method_filter="old_best_plus_bond_credit_incremental",
        output_method="Old+Credit Fixed Parameter",
        output_config_id="old_plus_fixed_parameter",
    )
    post_summary, post_equity = validation_summary(
        pd.concat([post_exp, post_roll, post_fixed, post_old_exp, post_old_roll, post_old_fixed], ignore_index=True),
        benchmark_for_validation,
        POST_2022_START_DATE,
    )

    # Tilt equity curves: best per max_tilt plus benchmarks.
    tilt_display = {}
    tilt_returns_parts = [selected_returns]
    for _, row in tilt.iterrows():
        method, config_id = row["method"], row["config_id"]
        cfg = config_grid[(config_grid["method"] == method) & (config_grid["config_id"] == config_id)].iloc[0]
        strat = build_strategy_for_config(features, cfg)
        tilt_returns_parts.append(strat)
        tilt_display[(method, config_id)] = f"Best Tilt {row['max_tilt']:.0%}"
    tilt_returns = pd.concat(tilt_returns_parts, ignore_index=True)
    tilt_equity = build_equity_curves(tilt_returns, tilt_display)

    plot_equity(main_equity, "Bond/Credit Smooth Policy Main Equity Curves, 10bp Cost", PLOT_DIR / "bond_credit_smooth_policy_v1_main_equity_curves.png")
    plot_equity(tilt_equity, "Bond/Credit Max-Tilt Specification Test, 10bp Cost", PLOT_DIR / "bond_credit_smooth_policy_v1_tilt_equity_curves.png")
    plot_equity(static_equity, "Bond/Credit Smooth Policy vs Static G/D, 10bp Cost", PLOT_DIR / "bond_credit_smooth_policy_v1_static_comparison_equity_curves.png")
    plot_equity(val_equity, "Bond/Credit OOS Validation Equity Curves, 10bp Cost", PLOT_DIR / "bond_credit_smooth_policy_v1_oos_validation_equity_curves.png")
    plot_equity(post_equity, "Bond/Credit Post-2022 Validation Equity Curves, 10bp Cost", PLOT_DIR / "bond_credit_smooth_policy_v1_post2022_validation_equity_curves.png")

    diag_main = pd.read_csv(BOND_DIAGNOSTIC_MAIN, encoding="utf-8-sig")
    diag_inter = pd.read_csv(BOND_DIAGNOSTIC_TABLE, encoding="utf-8-sig")
    report_path = write_report(
        config_grid,
        metrics,
        selected,
        selected_summary,
        comparisons,
        tilt,
        cost,
        old_plus_cost,
        score_diag,
        static_comp,
        val_summary,
        post_summary,
        yearly,
        diag_main,
        diag_inter,
    )

    features.to_csv(INPUT_DIR / "bond_credit_smooth_policy_v1_feature_panel.csv", index=False, encoding="utf-8-sig")
    config_grid.to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_config_grid.csv", index=False, encoding="utf-8-sig")
    metrics.to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_grid_metrics.csv", index=False, encoding="utf-8-sig")
    selected_returns.to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_selected_daily_returns.csv", index=False, encoding="utf-8-sig")
    selected_summary.to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_selected_summary.csv", index=False, encoding="utf-8-sig")
    comparisons.to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_comparisons.csv", index=False, encoding="utf-8-sig")
    main_equity.to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_main_equity_curves.csv", index=False, encoding="utf-8-sig")
    tilt.to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_tilt_summary.csv", index=False, encoding="utf-8-sig")
    tilt_equity.to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_tilt_equity_curves.csv", index=False, encoding="utf-8-sig")
    cost.to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_selected_cost_sensitivity.csv", index=False, encoding="utf-8-sig")
    old_plus_cost.to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_old_plus_credit_cost_sensitivity.csv", index=False, encoding="utf-8-sig")
    score_diag.to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_score_diagnostics.csv", index=False, encoding="utf-8-sig")
    yearly.to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_yearly_metrics.csv", index=False, encoding="utf-8-sig")
    static_comp.to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_static_comparison.csv", index=False, encoding="utf-8-sig")
    static_equity.to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_static_comparison_equity_curves.csv", index=False, encoding="utf-8-sig")
    pd.concat([wf_exp, wf_roll, fixed, old_wf_exp, old_wf_roll, old_fixed], ignore_index=True).to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_oos_validation_returns.csv", index=False, encoding="utf-8-sig")
    pd.concat([sel_exp, sel_roll, fixed_meta, old_sel_exp, old_sel_roll, old_fixed_meta], ignore_index=True).to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_oos_validation_selections.csv", index=False, encoding="utf-8-sig")
    val_summary.to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_oos_validation_summary.csv", index=False, encoding="utf-8-sig")
    val_equity.to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_oos_validation_equity_curves.csv", index=False, encoding="utf-8-sig")
    pd.concat([post_exp, post_roll, post_fixed, post_old_exp, post_old_roll, post_old_fixed], ignore_index=True).to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_post2022_validation_returns.csv", index=False, encoding="utf-8-sig")
    pd.concat([post_sel_exp, post_sel_roll, post_fixed_meta, post_old_sel_exp, post_old_sel_roll, post_old_fixed_meta], ignore_index=True).to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_post2022_validation_selections.csv", index=False, encoding="utf-8-sig")
    post_summary.to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_post2022_validation_summary.csv", index=False, encoding="utf-8-sig")
    post_equity.to_csv(TABLE_DIR / "bond_credit_smooth_policy_v1_post2022_validation_equity_curves.csv", index=False, encoding="utf-8-sig")
    print(f"Config count: {len(config_grid)}")
    print(f"Selected config: {best_id}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()

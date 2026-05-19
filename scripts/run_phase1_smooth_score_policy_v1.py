#!/usr/bin/env python3
"""Backtest smooth continuous G/D allocation policies.

This experiment follows the final smooth policy design:

* expanding z-scores only, no full-sample normalization;
* no quantile allocation, no hard if/then action table, no minimum rebalance band;
* tanh maps scores to smooth target weights;
* EWMA smooths target weights into deployable weights;
* transaction costs are reported at 0bp, 5bp, 10bp, and 20bp;
* supplementary tilt grids test whether wider smooth tilts improve the G/D allocation.
"""

from __future__ import annotations

import math
import os
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PANEL_PATH = ROOT / "data" / "phase1" / "state_framework_v2" / "inputs" / "phase1_state_framework_v2_panel.csv"
OUT_DIR = ROOT / "data" / "phase1" / "smooth_score_policy_v1"
INPUT_DIR = OUT_DIR / "inputs"
TABLE_DIR = OUT_DIR / "tables"
REPORT_DIR = OUT_DIR / "reports"
PLOT_DIR = OUT_DIR / "plots"

COMMON_OOS_START_DATE = "2016-12-21"
TRANSACTION_COST_BPS = (0, 5, 10, 20)
TRADING_DAYS = 252
VALIDATION_INITIAL_TRAIN_WINDOW = 252
VALIDATION_TEST_BLOCK = 63
RAW_FEATURES = (
    "tnx_change_21d",
    "spy_drawdown",
    "vix_percentile_756d",
    "vix_change_21d",
    "gd_trailing_126d",
)
TRAD_ALPHA = (0.50, 0.67)
LAMBDA_STRESS = (0.10, 0.25)
LAMBDA_CROWDED = (0.05, 0.15)
MAX_TILT = (0.10, 0.20)
TAU_WEIGHT = (1.0, 1.5)
ETA = (0.05, 0.15)

def ensure_dirs() -> None:
    for directory in (INPUT_DIR, TABLE_DIR, REPORT_DIR, PLOT_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def read_panel() -> pd.DataFrame:
    panel = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    panel["date"] = pd.to_datetime(panel["date"]).dt.normalize()
    panel = panel.sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)
    return panel


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


def build_feature_panel(panel: pd.DataFrame) -> pd.DataFrame:
    needed = ["date", "g_return", "d_return", "SPY", "future_gd_return_63d", *RAW_FEATURES]
    out = panel[needed].replace([np.inf, -np.inf], np.nan).copy()
    for col in RAW_FEATURES:
        out[f"z_{col}"] = expanding_z(out[col])

    out["r"] = -out["z_tnx_change_21d"]
    out["d"] = -out["z_spy_drawdown"]
    out["vh"] = out["z_vix_percentile_756d"]
    out["vr"] = -out["z_vix_change_21d"]
    out["g126"] = out["z_gd_trailing_126d"]

    out["high_vix_smooth"] = softplus(out["vh"], tau=1.0)
    out["vix_relief_smooth"] = softplus(out["vr"], tau=1.0)
    out["low_vix_smooth"] = softplus(-out["vh"], tau=1.0)
    out["growth_ext_smooth"] = softplus(out["g126"], tau=1.0)
    out["rate_quiet_smooth"] = np.exp(-0.5 * out["r"] ** 2)

    out["i1"] = out["r"] * out["vh"]
    out["i2"] = out["high_vix_smooth"] * out["vix_relief_smooth"]
    out["i3"] = out["growth_ext_smooth"] * out["low_vix_smooth"]
    out["i4"] = out["i3"] * out["rate_quiet_smooth"]
    for col in ("i1", "i2", "i3", "i4"):
        out[f"z_{col}"] = expanding_z(out[col])
    out["core_50_50"] = 0.50 * out["r"] + 0.50 * out["d"]
    out["core_67_33"] = 0.67 * out["r"] + 0.33 * out["d"]
    return out


def smooth_weight_from_score(score: pd.Series, max_tilt: float, tau_weight: float, eta: float) -> pd.Series:
    score_z = expanding_z(score)
    target = 0.50 + max_tilt * np.tanh(score_z / tau_weight)
    weights: list[float] = []
    prev = 0.50
    for value in target:
        if pd.isna(value):
            weights.append(np.nan)
            continue
        current = (1 - eta) * prev + eta * float(value)
        weights.append(current)
        prev = current
    return pd.Series(weights, index=score.index)


def traditional_scores(features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    signal_rows = []
    score_rows = []
    stress = 0.5 * features["z_i1"] + 0.5 * features["z_i2"]
    crowded = 0.5 * features["z_i3"] + 0.5 * features["z_i4"]
    config_no = 0
    for alpha in TRAD_ALPHA:
        core = alpha * features["r"] + (1 - alpha) * features["d"]
        for lambda_stress in LAMBDA_STRESS:
            for lambda_crowded in LAMBDA_CROWDED:
                raw_score = core + lambda_stress * stress - lambda_crowded * crowded
                for max_tilt in MAX_TILT:
                    for tau_weight in TAU_WEIGHT:
                        for eta in ETA:
                            config_no += 1
                            config_id = (
                                f"trad_a{alpha:.2f}_ls{lambda_stress:.2f}_lc{lambda_crowded:.2f}"
                                f"_tilt{max_tilt:.2f}_tau{tau_weight:.1f}_eta{eta:.2f}"
                            )
                            weight = smooth_weight_from_score(raw_score, max_tilt, tau_weight, eta)
                            score_z = expanding_z(raw_score)
                            signal_rows.append(
                                pd.DataFrame(
                                    {
                                        "date": features["date"],
                                        "method": "traditional_smooth_score",
                                        "config_id": config_id,
                                        "g_weight_signal": weight,
                                        "score": raw_score,
                                        "score_z": score_z,
                                    }
                                )
                            )
                            score_rows.append(
                                {
                                    "method": "traditional_smooth_score",
                                    "config_id": config_id,
                                    "alpha": alpha,
                                    "lambda_stress": lambda_stress,
                                    "lambda_crowded": lambda_crowded,
                                    "max_tilt": max_tilt,
                                    "tau_weight": tau_weight,
                                    "eta": eta,
                                }
                            )
    return pd.concat(signal_rows, ignore_index=True), pd.DataFrame(score_rows)


def benchmark_smooth_scores(features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    signal_rows = []
    config_rows = []

    for max_tilt in MAX_TILT:
        for tau_weight in TAU_WEIGHT:
            for eta in ETA:
                raw_score = features["r"]
                config_id = f"tnx_tilt{max_tilt:.2f}_tau{tau_weight:.1f}_eta{eta:.2f}"
                signal_rows.append(
                    pd.DataFrame(
                        {
                            "date": features["date"],
                            "method": "smooth_tnx_only",
                            "config_id": config_id,
                            "g_weight_signal": smooth_weight_from_score(raw_score, max_tilt, tau_weight, eta),
                            "score": raw_score,
                            "score_z": expanding_z(raw_score),
                        }
                    )
                )
                config_rows.append(
                    {
                        "method": "smooth_tnx_only",
                        "config_id": config_id,
                        "alpha": np.nan,
                        "lambda_stress": np.nan,
                        "lambda_crowded": np.nan,
                        "max_tilt": max_tilt,
                        "tau_weight": tau_weight,
                        "eta": eta,
                    }
                )

    for alpha in TRAD_ALPHA:
        raw_score = alpha * features["r"] + (1 - alpha) * features["d"]
        for max_tilt in MAX_TILT:
            for tau_weight in TAU_WEIGHT:
                for eta in ETA:
                    config_id = f"core_a{alpha:.2f}_tilt{max_tilt:.2f}_tau{tau_weight:.1f}_eta{eta:.2f}"
                    signal_rows.append(
                        pd.DataFrame(
                            {
                                "date": features["date"],
                                "method": "smooth_core_only",
                                "config_id": config_id,
                                "g_weight_signal": smooth_weight_from_score(raw_score, max_tilt, tau_weight, eta),
                                "score": raw_score,
                                "score_z": expanding_z(raw_score),
                            }
                        )
                    )
                    config_rows.append(
                        {
                            "method": "smooth_core_only",
                            "config_id": config_id,
                            "alpha": alpha,
                            "lambda_stress": np.nan,
                            "lambda_crowded": np.nan,
                            "max_tilt": max_tilt,
                            "tau_weight": tau_weight,
                            "eta": eta,
                        }
                    )
    return pd.concat(signal_rows, ignore_index=True), pd.DataFrame(config_rows)


def static_benchmark_signals(features: pd.DataFrame) -> pd.DataFrame:
    rows = []
    static = {
        "benchmark_50_50_gd": 0.50,
        "benchmark_100_g": 1.00,
        "benchmark_100_d": 0.00,
    }
    for method, weight in static.items():
        rows.append(
            pd.DataFrame(
                {
                    "date": features["date"],
                    "method": method,
                    "config_id": method,
                    "g_weight_signal": weight,
                    "score": np.nan,
                    "score_z": np.nan,
                }
            )
        )
    rows.append(
        pd.DataFrame(
            {
                "date": features["date"],
                "method": "benchmark_spy",
                "config_id": "benchmark_spy",
                "g_weight_signal": np.nan,
                "score": np.nan,
                "score_z": np.nan,
            }
        )
    )
    return pd.concat(rows, ignore_index=True)


def matched_smooth_baseline_signals(
    features: pd.DataFrame,
    alpha: float,
    max_tilt: float,
    tau_weight: float,
    eta: float,
) -> pd.DataFrame:
    """Build TNX-only and core-only baselines with the selected local-grid mapping parameters."""
    rows = []
    specs = [
        (
            "matched_smooth_tnx_only",
            f"tnx_tilt{max_tilt:.2f}_tau{tau_weight:.2f}_eta{eta:.2f}",
            features["r"],
        ),
        (
            "matched_smooth_core_only",
            f"core_a{alpha:.2f}_tilt{max_tilt:.2f}_tau{tau_weight:.2f}_eta{eta:.2f}",
            alpha * features["r"] + (1 - alpha) * features["d"],
        ),
    ]
    for method, config_id, raw_score in specs:
        rows.append(
            pd.DataFrame(
                {
                    "date": features["date"],
                    "method": method,
                    "config_id": config_id,
                    "g_weight_signal": smooth_weight_from_score(raw_score, max_tilt, tau_weight, eta),
                    "score": raw_score,
                    "score_z": expanding_z(raw_score),
                }
            )
        )
    return pd.concat(rows, ignore_index=True)


def build_traditional_score(features: pd.DataFrame, alpha: float, lambda_stress: float, lambda_crowded: float) -> pd.Series:
    stress = 0.5 * features["z_i1"] + 0.5 * features["z_i2"]
    crowded = 0.5 * features["z_i3"] + 0.5 * features["z_i4"]
    core = alpha * features["r"] + (1 - alpha) * features["d"]
    return core + lambda_stress * stress - lambda_crowded * crowded


def supplementary_tilt_signals(features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    signal_rows: list[pd.DataFrame] = []
    config_rows: list[dict[str, object]] = []

    def add_config(
        method: str,
        config_id: str,
        alpha: float,
        lambda_stress: float,
        lambda_crowded: float,
        max_tilt: float,
        tau_weight: float,
        eta: float,
    ) -> None:
        raw_score = build_traditional_score(features, alpha, lambda_stress, lambda_crowded)
        signal_rows.append(
            pd.DataFrame(
                {
                    "date": features["date"],
                    "method": method,
                    "config_id": config_id,
                    "g_weight_signal": smooth_weight_from_score(raw_score, max_tilt, tau_weight, eta),
                    "score": raw_score,
                    "score_z": expanding_z(raw_score),
                }
            )
        )
        config_rows.append(
            {
                "method": method,
                "config_id": config_id,
                "alpha": alpha,
                "lambda_stress": lambda_stress,
                "lambda_crowded": lambda_crowded,
                "max_tilt": max_tilt,
                "tau_weight": tau_weight,
                "eta": eta,
            }
        )

    for max_tilt in (0.20, 0.30, 0.40, 0.50):
        add_config(
            "supp_extreme_tilt_base",
            f"extreme_a0.50_ls0.25_lc0.15_tilt{max_tilt:.2f}_tau1.0_eta0.05",
            0.50,
            0.25,
            0.15,
            max_tilt,
            1.0,
            0.05,
        )

    for alpha in (0.50, 0.67):
        for lambda_stress in (0.25, 0.50):
            for lambda_crowded in (0.05, 0.15, 0.25):
                for max_tilt in (0.20, 0.30, 0.40, 0.50):
                    for tau_weight in (0.75, 1.0, 1.5):
                        for eta in (0.03, 0.05, 0.10):
                            add_config(
                                "supp_expanded_local_grid",
                                (
                                    f"local_a{alpha:.2f}_ls{lambda_stress:.2f}_lc{lambda_crowded:.2f}"
                                    f"_tilt{max_tilt:.2f}_tau{tau_weight:.2f}_eta{eta:.2f}"
                                ),
                                alpha,
                                lambda_stress,
                                lambda_crowded,
                                max_tilt,
                                tau_weight,
                                eta,
                            )

    return pd.concat(signal_rows, ignore_index=True), pd.DataFrame(config_rows)


def build_strategy_returns(features: pd.DataFrame, signals: pd.DataFrame) -> pd.DataFrame:
    base = features[["date", "g_return", "d_return", "SPY"]].copy()
    merged = signals.merge(base, on="date", how="left").sort_values(["method", "config_id", "date"])
    rows = []
    for (method, config_id), group in merged.groupby(["method", "config_id"], sort=False):
        group = group.sort_values("date").copy()
        if method == "benchmark_spy":
            deployed = pd.Series(np.nan, index=group.index)
            gross = group["SPY"].astype(float)
            turnover = pd.Series(0.0, index=group.index)
        else:
            deployed = group["g_weight_signal"].shift(1)
            gross = deployed * group["g_return"] + (1.0 - deployed) * group["d_return"]
            turnover = 2.0 * deployed.diff().abs().fillna(0.0)
        for cost_bps in TRANSACTION_COST_BPS:
            net = gross - turnover * (cost_bps / 10_000.0)
            frame = pd.DataFrame(
                {
                    "date": group["date"],
                    "method": method,
                    "config_id": config_id,
                    "cost_bps": cost_bps,
                    "g_weight": deployed,
                    "d_weight": 1.0 - deployed,
                    "daily_turnover": turnover,
                    "gross_return": gross,
                    "net_return": net,
                }
            ).dropna(subset=["net_return"])
            rows.append(frame)
    return pd.concat(rows, ignore_index=True)


def max_drawdown(returns: pd.Series) -> float:
    wealth = (1 + returns.fillna(0)).cumprod()
    drawdown = wealth / wealth.cummax() - 1
    return float(drawdown.min())


def downside_deviation(returns: pd.Series) -> float:
    downside = returns[returns < 0]
    if len(downside) == 0:
        return np.nan
    return float(downside.std(ddof=0) * math.sqrt(TRADING_DAYS))


def performance_metrics(returns: pd.Series, turnover: pd.Series | None = None, weights: pd.Series | None = None) -> dict[str, float]:
    returns = returns.dropna()
    n = len(returns)
    years = n / TRADING_DAYS if n else np.nan
    total = float((1 + returns).prod() - 1) if n else np.nan
    cagr = float((1 + total) ** (1 / years) - 1) if years and years > 0 and total > -1 else np.nan
    ann_vol = float(returns.std(ddof=0) * math.sqrt(TRADING_DAYS)) if n else np.nan
    sharpe = float(returns.mean() / returns.std(ddof=0) * math.sqrt(TRADING_DAYS)) if n and returns.std(ddof=0) > 0 else np.nan
    downside = downside_deviation(returns)
    sortino = float(cagr / downside) if downside and downside > 0 else np.nan
    mdd = max_drawdown(returns) if n else np.nan
    annual_turnover = float(turnover.fillna(0).sum() / years) if turnover is not None and years and years > 0 else 0.0
    avg_g = float(weights.mean()) if weights is not None and weights.notna().any() else np.nan
    return {
        "n_days": int(n),
        "start_date": returns.index.min().date().isoformat() if isinstance(returns.index, pd.DatetimeIndex) and n else "",
        "end_date": returns.index.max().date().isoformat() if isinstance(returns.index, pd.DatetimeIndex) and n else "",
        "total_return": total,
        "cagr": cagr,
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "sortino": sortino,
        "max_drawdown": mdd,
        "calmar": float(cagr / abs(mdd)) if mdd and mdd < 0 else np.nan,
        "annual_turnover": annual_turnover,
        "avg_g_weight": avg_g,
    }


def build_metrics(strategy_returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (method, config_id, cost_bps), group in strategy_returns.groupby(["method", "config_id", "cost_bps"], sort=False):
        group = group.sort_values("date").copy()
        group["date"] = pd.to_datetime(group["date"])
        ret = pd.Series(group["net_return"].to_numpy(), index=group["date"])
        turnover = pd.Series(group["daily_turnover"].to_numpy(), index=group["date"])
        weights = pd.Series(group["g_weight"].to_numpy(), index=group["date"])
        row = {"method": method, "config_id": config_id, "cost_bps": cost_bps}
        row.update(performance_metrics(ret, turnover=turnover, weights=weights))
        rows.append(row)
    return pd.DataFrame(rows)


def add_selection_scores(metrics: pd.DataFrame) -> pd.DataFrame:
    out = metrics.copy()
    out["selection_score"] = np.nan
    dynamic_methods = [
        "traditional_smooth_score",
        "smooth_tnx_only",
        "smooth_core_only",
        "supp_extreme_tilt_base",
        "supp_expanded_local_grid",
    ]
    dynamic = out[(out["cost_bps"] == 10) & (out["method"].isin(dynamic_methods))].copy()
    if dynamic.empty:
        return out
    score = (
        dynamic["sharpe"].rank(pct=True)
        + dynamic["calmar"].rank(pct=True)
        + dynamic["cagr"].rank(pct=True)
        + dynamic["max_drawdown"].rank(pct=True)
        + (-dynamic["annual_turnover"]).rank(pct=True)
    ) / 5.0
    out.loc[dynamic.index, "selection_score"] = score
    return out


def yearly_metrics(
    strategy_returns: pd.DataFrame,
    selected_keys: set[tuple[str, str]],
    start_date: pd.Timestamp | None = None,
    end_date: pd.Timestamp | None = None,
) -> pd.DataFrame:
    data = strategy_returns[strategy_returns["cost_bps"] == 10].copy()
    data = data[data.apply(lambda r: (r["method"], r["config_id"]) in selected_keys, axis=1)]
    data["date"] = pd.to_datetime(data["date"])
    if start_date is not None:
        data = data[data["date"] >= pd.to_datetime(start_date)]
    if end_date is not None:
        data = data[data["date"] <= pd.to_datetime(end_date)]
    data["year"] = data["date"].dt.year
    rows = []
    for (method, config_id, year), group in data.groupby(["method", "config_id", "year"], sort=True):
        group = group.sort_values("date")
        ret = pd.Series(group["net_return"].to_numpy(), index=group["date"])
        turnover = pd.Series(group["daily_turnover"].to_numpy(), index=group["date"])
        weights = pd.Series(group["g_weight"].to_numpy(), index=group["date"])
        row = {"method": method, "config_id": config_id, "year": int(year)}
        row.update(performance_metrics(ret, turnover=turnover, weights=weights))
        rows.append(row)
    return pd.DataFrame(rows)


def common_oos_returns(strategy_returns: pd.DataFrame) -> tuple[pd.DataFrame, pd.Timestamp]:
    """Restrict evaluation to the fixed common OOS window used by this study."""
    common_start = pd.Timestamp(COMMON_OOS_START_DATE)
    out = strategy_returns[pd.to_datetime(strategy_returns["date"]) >= common_start].copy()
    return out, common_start


def aligned_comparison(
    strategy_returns: pd.DataFrame,
    left: tuple[str, str],
    right: tuple[str, str],
    label: str,
    cost_bps: int = 10,
) -> dict[str, object] | None:
    left_df = strategy_returns[
        (strategy_returns["method"] == left[0])
        & (strategy_returns["config_id"] == left[1])
        & (strategy_returns["cost_bps"] == cost_bps)
    ][["date", "net_return", "daily_turnover"]].rename(columns={"net_return": "left_return", "daily_turnover": "left_turnover"})
    right_df = strategy_returns[
        (strategy_returns["method"] == right[0])
        & (strategy_returns["config_id"] == right[1])
        & (strategy_returns["cost_bps"] == cost_bps)
    ][["date", "net_return", "daily_turnover"]].rename(columns={"net_return": "right_return", "daily_turnover": "right_turnover"})
    merged = left_df.merge(right_df, on="date", how="inner")
    if merged.empty:
        return None
    excess = merged["left_return"] - merged["right_return"]
    years = len(merged) / TRADING_DAYS
    te = float(excess.std(ddof=0) * math.sqrt(TRADING_DAYS))
    ann_excess = float(excess.mean() * TRADING_DAYS)
    left_mdd = max_drawdown(merged["left_return"])
    right_mdd = max_drawdown(merged["right_return"])
    return {
        "comparison": label,
        "left_method": left[0],
        "left_config_id": left[1],
        "right_method": right[0],
        "right_config_id": right[1],
        "cost_bps": cost_bps,
        "n_days": len(merged),
        "start_date": pd.to_datetime(merged["date"]).min().date().isoformat(),
        "end_date": pd.to_datetime(merged["date"]).max().date().isoformat(),
        "annualized_excess_return": ann_excess,
        "tracking_error": te,
        "information_ratio": ann_excess / te if te > 0 else np.nan,
        "max_dd_diff": left_mdd - right_mdd,
        "turnover_diff": float((merged["left_turnover"].sum() - merged["right_turnover"].sum()) / years) if years > 0 else np.nan,
    }


def score_diagnostics(
    features: pd.DataFrame,
    signals: pd.DataFrame,
    selected_keys: set[tuple[str, str]],
    start_date: pd.Timestamp | None = None,
) -> pd.DataFrame:
    target = features[["date", "future_gd_return_63d"]].copy()
    if start_date is not None:
        target = target[pd.to_datetime(target["date"]) >= pd.to_datetime(start_date)].copy()
    rows = []
    for method, config_id in selected_keys:
        sig = signals[(signals["method"] == method) & (signals["config_id"] == config_id)][["date", "score_z"]].copy()
        if sig.empty or sig["score_z"].notna().sum() < 50:
            continue
        merged = sig.merge(target, on="date", how="left").dropna(subset=["score_z", "future_gd_return_63d"])
        if len(merged) < 50:
            continue
        try:
            merged["score_quantile"] = pd.qcut(merged["score_z"], 5, labels=["Q1", "Q2", "Q3", "Q4", "Q5"])
        except ValueError:
            continue
        means = merged.groupby("score_quantile", observed=False)["future_gd_return_63d"].mean()
        row = {"method": method, "config_id": config_id}
        for q in ["Q1", "Q2", "Q3", "Q4", "Q5"]:
            row[q] = float(means.get(q, np.nan))
        row["Q5_minus_Q1"] = row["Q5"] - row["Q1"]
        rows.append(row)
    return pd.DataFrame(rows)


def build_equity_curves(
    strategy_returns: pd.DataFrame,
    selected: dict[str, tuple[str, str]],
    cost_bps: int = 10,
) -> pd.DataFrame:
    labels = {
        "best_local_grid": "Best Local Grid (tilt 50%)",
        "matched_tnx_only": "Matched TNX-only (tilt 50%)",
        "matched_core_only": "Matched Core-only (tilt 50%)",
        "extreme_50_tilt": "Extreme 50% Tilt",
        "traditional_smooth_score": "Traditional Smooth Score",
        "smooth_tnx_only": "Smooth TNX-only",
        "smooth_core_only": "Smooth Core-only",
        "benchmark_50_50_gd": "50/50 G-D Buy & Hold",
        "benchmark_100_g": "100% G Buy & Hold",
        "benchmark_100_d": "100% D Buy & Hold",
        "benchmark_spy": "SPY Buy & Hold",
    }
    curves: list[pd.DataFrame] = []
    for key in selected:
        method, config_id = selected[key]
        group = strategy_returns[
            (strategy_returns["method"] == method)
            & (strategy_returns["config_id"] == config_id)
            & (strategy_returns["cost_bps"] == cost_bps)
        ][["date", "net_return"]].copy()
        if group.empty:
            continue
        group["date"] = pd.to_datetime(group["date"])
        group = group.sort_values("date")
        wealth = (1.0 + group["net_return"].astype(float)).cumprod()
        if not wealth.empty and wealth.iloc[0] != 0:
            wealth = wealth / wealth.iloc[0]
        curves.append(pd.DataFrame({"date": group["date"], labels[key]: wealth}))
    if not curves:
        return pd.DataFrame()
    out = curves[0]
    for curve in curves[1:]:
        out = out.merge(curve, on="date", how="outer")
    return align_and_rebase_equity(out)


def align_and_rebase_equity(equity: pd.DataFrame) -> pd.DataFrame:
    """Align all plotted curves to their common valid window and rebase to 1."""
    if equity.empty:
        return equity
    out = equity.copy()
    out["date"] = pd.to_datetime(out["date"])
    out = out.sort_values("date").reset_index(drop=True)
    cols = [c for c in out.columns if c != "date"]
    if not cols:
        return out
    out = out.dropna(subset=cols, how="any").reset_index(drop=True)
    if out.empty:
        return out
    for col in cols:
        base = out[col].iloc[0]
        if pd.notna(base) and base != 0:
            out[col] = out[col] / base
    return out


def selected_method_summary(
    strategy_returns: pd.DataFrame,
    equity: pd.DataFrame,
    selected: dict[str, tuple[str, str]],
    cost_bps: int = 10,
) -> pd.DataFrame:
    labels = {
        "best_local_grid": "Best Local Grid (tilt 50%)",
        "matched_tnx_only": "Matched TNX-only (tilt 50%)",
        "matched_core_only": "Matched Core-only (tilt 50%)",
        "extreme_50_tilt": "Extreme 50% Tilt",
        "traditional_smooth_score": "Traditional Smooth Score",
        "smooth_tnx_only": "Smooth TNX-only",
        "smooth_core_only": "Smooth Core-only",
        "benchmark_50_50_gd": "50/50 G-D Buy & Hold",
        "benchmark_100_g": "100% G Buy & Hold",
        "benchmark_100_d": "100% D Buy & Hold",
        "benchmark_spy": "SPY Buy & Hold",
    }
    order = list(selected)
    rows = []
    start = pd.to_datetime(equity["date"]).min() if not equity.empty else None
    end = pd.to_datetime(equity["date"]).max() if not equity.empty else None
    for key in order:
        method, config_id = selected[key]
        group = strategy_returns[
            (strategy_returns["method"] == method)
            & (strategy_returns["config_id"] == config_id)
            & (strategy_returns["cost_bps"] == cost_bps)
        ].copy()
        if group.empty:
            continue
        group["date"] = pd.to_datetime(group["date"])
        if start is not None:
            group = group[group["date"] >= start]
        if end is not None:
            group = group[group["date"] <= end]
        group = group.sort_values("date")
        ret = pd.Series(group["net_return"].to_numpy(), index=group["date"])
        turnover = pd.Series(group["daily_turnover"].to_numpy(), index=group["date"])
        weights = pd.Series(group["g_weight"].to_numpy(), index=group["date"])
        row = {"method": method, "config_id": config_id, "cost_bps": cost_bps}
        row.update(performance_metrics(ret, turnover=turnover, weights=weights))
        row["display_name"] = labels[key]
        if labels[key] in equity.columns:
            row["final_wealth"] = float(equity[labels[key]].dropna().iloc[-1])
        else:
            row["final_wealth"] = np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def add_supplement_baseline_columns(supp_metrics: pd.DataFrame, combined_returns: pd.DataFrame) -> pd.DataFrame:
    out = supp_metrics.copy()
    out["final_wealth"] = 1.0 + out["total_return"]
    out["ann_excess_vs_50_50"] = np.nan
    out["ann_excess_vs_100_g"] = np.nan
    out["max_dd_diff_vs_50_50"] = np.nan
    out["max_dd_diff_vs_100_g"] = np.nan
    combined = combined_returns.copy()
    combined["date"] = pd.to_datetime(combined["date"])
    supp_keys = set(zip(out["method"], out["config_id"], out["cost_bps"]))
    for cost_bps in sorted(out["cost_bps"].dropna().unique()):
        base_50 = combined[
            (combined["method"] == "benchmark_50_50_gd")
            & (combined["config_id"] == "benchmark_50_50_gd")
            & (combined["cost_bps"] == cost_bps)
        ][["date", "net_return"]].rename(columns={"net_return": "base_50_return"})
        base_g = combined[
            (combined["method"] == "benchmark_100_g")
            & (combined["config_id"] == "benchmark_100_g")
            & (combined["cost_bps"] == cost_bps)
        ][["date", "net_return"]].rename(columns={"net_return": "base_g_return"})
        base = base_50.merge(base_g, on="date", how="inner")
        if base.empty:
            continue
        for (method, config_id), group in combined[
            (combined["cost_bps"] == cost_bps)
            & (combined["method"].isin(["supp_extreme_tilt_base", "supp_expanded_local_grid"]))
        ].groupby(["method", "config_id"], sort=False):
            if (method, config_id, cost_bps) not in supp_keys:
                continue
            merged = group[["date", "net_return"]].merge(base, on="date", how="inner")
            if merged.empty:
                continue
            excess_50 = merged["net_return"] - merged["base_50_return"]
            excess_g = merged["net_return"] - merged["base_g_return"]
            idx = out[
                (out["method"] == method)
                & (out["config_id"] == config_id)
                & (out["cost_bps"] == cost_bps)
            ].index
            out.loc[idx, "ann_excess_vs_50_50"] = float(excess_50.mean() * TRADING_DAYS)
            out.loc[idx, "ann_excess_vs_100_g"] = float(excess_g.mean() * TRADING_DAYS)
            out.loc[idx, "max_dd_diff_vs_50_50"] = max_drawdown(merged["net_return"]) - max_drawdown(merged["base_50_return"])
            out.loc[idx, "max_dd_diff_vs_100_g"] = max_drawdown(merged["net_return"]) - max_drawdown(merged["base_g_return"])
    return out


def supplement_cost_sensitivity(supp_summary: pd.DataFrame, selected_config_id: str) -> pd.DataFrame:
    return (
        supp_summary[supp_summary["config_id"] == selected_config_id]
        .sort_values("cost_bps")
        .reset_index(drop=True)
    )


def metrics_from_arrays(
    label: str,
    returns: pd.Series,
    g_weight: float | None = None,
    turnover: pd.Series | None = None,
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    returns = returns.dropna().sort_index()
    zero_turnover = pd.Series(0.0, index=returns.index) if turnover is None else turnover.reindex(returns.index).fillna(0.0)
    if g_weight is None:
        weights = pd.Series(np.nan, index=returns.index)
    else:
        weights = pd.Series(g_weight, index=returns.index)
    row: dict[str, object] = {"method_label": label}
    row.update(performance_metrics(returns, turnover=zero_turnover, weights=weights))
    row["final_wealth"] = 1.0 + float(row["total_return"])
    if extra:
        row.update(extra)
    return row


def build_vol_matched_static_comparison(
    supp_common_returns: pd.DataFrame,
    benchmark_common_returns: pd.DataFrame,
    supp_summary: pd.DataFrame,
    cost_bps: int = 10,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, str]]:
    local = supp_summary[
        (supp_summary["method"] == "supp_expanded_local_grid")
        & (supp_summary["cost_bps"] == cost_bps)
    ].sort_values("selection_score", ascending=False)
    if local.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}
    best = local.iloc[0]
    best_config_id = str(best["config_id"])
    target_df = supp_common_returns[
        (supp_common_returns["method"] == str(best["method"]))
        & (supp_common_returns["config_id"] == best_config_id)
        & (supp_common_returns["cost_bps"] == cost_bps)
    ][["date", "net_return", "daily_turnover", "g_weight"]].copy()
    target_df["date"] = pd.to_datetime(target_df["date"])
    target_df = target_df.sort_values("date").dropna(subset=["net_return"])
    if target_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}

    def bench_series(method: str) -> pd.Series:
        df = benchmark_common_returns[
            (benchmark_common_returns["method"] == method)
            & (benchmark_common_returns["config_id"] == method)
            & (benchmark_common_returns["cost_bps"] == cost_bps)
        ][["date", "net_return"]].copy()
        df["date"] = pd.to_datetime(df["date"])
        return pd.Series(df["net_return"].to_numpy(), index=df["date"]).sort_index()

    target_ret = pd.Series(target_df["net_return"].to_numpy(), index=target_df["date"]).sort_index()
    target_turnover = pd.Series(target_df["daily_turnover"].to_numpy(), index=target_df["date"]).sort_index()
    target_weight = pd.Series(target_df["g_weight"].to_numpy(), index=target_df["date"]).sort_index()
    g_ret = bench_series("benchmark_100_g").reindex(target_ret.index).dropna()
    d_ret = bench_series("benchmark_100_d").reindex(target_ret.index).dropna()
    fifty_ret = bench_series("benchmark_50_50_gd").reindex(target_ret.index).dropna()
    spy_ret = bench_series("benchmark_spy").reindex(target_ret.index).dropna()
    common_index = target_ret.index.intersection(g_ret.index).intersection(d_ret.index)
    target_ret = target_ret.reindex(common_index)
    target_turnover = target_turnover.reindex(common_index)
    target_weight = target_weight.reindex(common_index)
    g_ret = g_ret.reindex(common_index)
    d_ret = d_ret.reindex(common_index)
    fifty_ret = fifty_ret.reindex(common_index)
    spy_ret = spy_ret.reindex(common_index)

    target_metrics = performance_metrics(target_ret, turnover=target_turnover, weights=target_weight)
    target_vol = float(target_metrics["ann_vol"])
    target_mdd = float(target_metrics["max_drawdown"])
    g_metrics = performance_metrics(g_ret)
    g_vol = float(g_metrics["ann_vol"])
    vol_scale = target_vol / g_vol if g_vol > 0 else np.nan
    vol_matched_g_ret = g_ret * vol_scale

    static_rows: list[dict[str, object]] = []
    static_curves: dict[str, pd.Series] = {}
    static_returns: dict[str, pd.Series] = {}
    for weight in np.round(np.arange(0.0, 1.0001, 0.01), 2):
        ret = weight * g_ret + (1 - weight) * d_ret
        label = f"Static G/D {weight:.0%} G"
        row = metrics_from_arrays(label, ret, g_weight=float(weight), extra={"static_g_weight": float(weight)})
        static_rows.append(row)
        static_returns[label] = ret
        static_curves[label] = (1.0 + ret).cumprod()
    static_grid = pd.DataFrame(static_rows)

    vol_match_static = static_grid.iloc[(static_grid["ann_vol"] - target_vol).abs().argsort().iloc[0]]
    dd_match_static = static_grid.iloc[(static_grid["max_drawdown"] - target_mdd).abs().argsort().iloc[0]]
    best_sharpe_static = static_grid.sort_values(["sharpe", "calmar", "cagr"], ascending=False).iloc[0]
    best_calmar_static = static_grid.sort_values(["calmar", "sharpe", "cagr"], ascending=False).iloc[0]
    constrained = static_grid[static_grid["max_drawdown"] >= target_mdd]
    best_cagr_constrained = constrained.sort_values(["cagr", "sharpe"], ascending=False).iloc[0] if not constrained.empty else pd.Series(dtype=object)

    comparison_specs: list[tuple[str, pd.Series, float | None, dict[str, object]]] = [
        (
            "Smooth Score Best Local",
            target_ret,
            float(target_weight.mean()),
            {"comparison_type": "target", "config_id": best_config_id},
        ),
        ("100% G Buy & Hold", g_ret, 1.0, {"comparison_type": "baseline"}),
        (
            "Vol-Matched 100% G",
            vol_matched_g_ret,
            float(vol_scale),
            {"comparison_type": "vol_matched_g", "scale_to_g": float(vol_scale)},
        ),
        ("50/50 G-D", fifty_ret, 0.5, {"comparison_type": "baseline"}),
        ("100% D Buy & Hold", d_ret, 0.0, {"comparison_type": "baseline"}),
        ("SPY Buy & Hold", spy_ret, None, {"comparison_type": "baseline"}),
        (
            f"Vol-Matched Static G/D ({vol_match_static['static_g_weight']:.0%} G)",
            static_returns[f"Static G/D {vol_match_static['static_g_weight']:.0%} G"],
            float(vol_match_static["static_g_weight"]),
            {"comparison_type": "vol_matched_static_gd", "static_g_weight": float(vol_match_static["static_g_weight"])},
        ),
        (
            f"MaxDD-Matched Static G/D ({dd_match_static['static_g_weight']:.0%} G)",
            static_returns[f"Static G/D {dd_match_static['static_g_weight']:.0%} G"],
            float(dd_match_static["static_g_weight"]),
            {"comparison_type": "maxdd_matched_static_gd", "static_g_weight": float(dd_match_static["static_g_weight"])},
        ),
        (
            f"Best Sharpe Static G/D ({best_sharpe_static['static_g_weight']:.0%} G)",
            static_returns[f"Static G/D {best_sharpe_static['static_g_weight']:.0%} G"],
            float(best_sharpe_static["static_g_weight"]),
            {"comparison_type": "best_sharpe_static_gd", "static_g_weight": float(best_sharpe_static["static_g_weight"])},
        ),
        (
            f"Best Calmar Static G/D ({best_calmar_static['static_g_weight']:.0%} G)",
            static_returns[f"Static G/D {best_calmar_static['static_g_weight']:.0%} G"],
            float(best_calmar_static["static_g_weight"]),
            {"comparison_type": "best_calmar_static_gd", "static_g_weight": float(best_calmar_static["static_g_weight"])},
        ),
    ]
    if not best_cagr_constrained.empty:
        comparison_specs.append(
            (
                f"Best CAGR Static G/D under Smooth MaxDD ({best_cagr_constrained['static_g_weight']:.0%} G)",
                static_returns[f"Static G/D {best_cagr_constrained['static_g_weight']:.0%} G"],
                float(best_cagr_constrained["static_g_weight"]),
                {
                    "comparison_type": "best_cagr_static_under_smooth_maxdd",
                    "static_g_weight": float(best_cagr_constrained["static_g_weight"]),
                },
            )
        )

    rows = []
    curves = pd.DataFrame({"date": common_index})
    for label, ret, g_weight, extra in comparison_specs:
        ret = ret.reindex(common_index).fillna(0.0)
        turnover = target_turnover if label == "Smooth Score Best Local" else None
        row = metrics_from_arrays(label, ret, g_weight=g_weight, turnover=turnover, extra=extra)
        row["ann_excess_vs_smooth"] = float((ret - target_ret).mean() * TRADING_DAYS)
        row["max_dd_diff_vs_smooth"] = float(max_drawdown(ret) - max_drawdown(target_ret))
        rows.append(row)
        curve = (1.0 + ret).cumprod()
        if not curve.empty and curve.iloc[0] != 0:
            curve = curve / curve.iloc[0]
        curves[label] = curve.to_numpy()
    comparison = pd.DataFrame(rows)
    static_grid["ann_excess_vs_smooth"] = static_grid["cagr"] - float(target_metrics["cagr"])
    meta = {
        "best_local_config_id": best_config_id,
        "target_vol": f"{target_vol:.6f}",
        "target_max_drawdown": f"{target_mdd:.6f}",
        "vol_matched_g_scale": f"{vol_scale:.6f}",
    }
    return comparison, static_grid, align_and_rebase_equity(curves), meta


def plot_equity_curves(equity: pd.DataFrame) -> dict[str, Path]:
    if equity.empty:
        return {}
    os.environ.setdefault("MPLCONFIGDIR", str(PLOT_DIR / ".matplotlib"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plot_paths = {
        "all_methods": PLOT_DIR / "smooth_score_policy_v1_common_oos_equity_curves_all.png",
        "buy_hold_gd": PLOT_DIR / "smooth_score_policy_v1_common_oos_buy_hold_gd.png",
    }
    date = pd.to_datetime(equity["date"])

    def draw(columns: list[str], title: str, path: Path) -> None:
        fig, ax = plt.subplots(figsize=(12, 7))
        for column in columns:
            if column in equity.columns:
                ax.plot(date, equity[column], linewidth=1.8, label=column)
        ax.set_title(title)
        ax.set_ylabel("Wealth, rebased to 1.0")
        ax.set_xlabel("Date")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="upper left", fontsize=9)
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(path, dpi=180, bbox_inches="tight")
        plt.close(fig)

    draw(
        [
            "Best Local Grid (tilt 50%)",
            "Matched TNX-only (tilt 50%)",
            "Matched Core-only (tilt 50%)",
            "Extreme 50% Tilt",
            "50/50 G-D Buy & Hold",
            "100% G Buy & Hold",
            "100% D Buy & Hold",
            "SPY Buy & Hold",
        ],
        "Common OOS Equity Curves, 10bp Cost",
        plot_paths["all_methods"],
    )
    draw(
        [
            "100% G Buy & Hold",
            "100% D Buy & Hold",
            "50/50 G-D Buy & Hold",
            "SPY Buy & Hold",
        ],
        "Buy-and-Hold Baselines, Common OOS",
        plot_paths["buy_hold_gd"],
    )
    return plot_paths


def build_supplementary_equity_curves(
    supp_returns: pd.DataFrame,
    benchmark_returns: pd.DataFrame,
    supp_summary: pd.DataFrame,
    cost_bps: int = 10,
) -> tuple[pd.DataFrame, dict[str, str]]:
    selected_configs: dict[str, tuple[str, str]] = {}
    extreme = supp_summary[
        (supp_summary["method"] == "supp_extreme_tilt_base")
        & (supp_summary["cost_bps"] == cost_bps)
    ].copy()
    for _, row in extreme.sort_values("max_tilt").iterrows():
        selected_configs[f"Extreme Tilt {row['max_tilt']:.0%}"] = (str(row["method"]), str(row["config_id"]))

    local = supp_summary[
        (supp_summary["method"] == "supp_expanded_local_grid")
        & (supp_summary["cost_bps"] == cost_bps)
    ].sort_values("selection_score", ascending=False)
    best_local_id = ""
    if not local.empty:
        best = local.iloc[0]
        best_local_id = str(best["config_id"])
        selected_configs["Best Local Grid"] = (str(best["method"]), best_local_id)

    combined = pd.concat([supp_returns, benchmark_returns], ignore_index=True).copy()
    baselines = {
        "50/50 G-D Buy & Hold": ("benchmark_50_50_gd", "benchmark_50_50_gd"),
        "100% G Buy & Hold": ("benchmark_100_g", "benchmark_100_g"),
        "100% D Buy & Hold": ("benchmark_100_d", "benchmark_100_d"),
        "SPY Buy & Hold": ("benchmark_spy", "benchmark_spy"),
    }
    selected_configs.update(baselines)

    curves: list[pd.DataFrame] = []
    for label, (method, config_id) in selected_configs.items():
        group = combined[
            (combined["method"] == method)
            & (combined["config_id"] == config_id)
            & (combined["cost_bps"] == cost_bps)
        ][["date", "net_return"]].copy()
        if group.empty:
            continue
        group["date"] = pd.to_datetime(group["date"])
        group = group.sort_values("date")
        wealth = (1.0 + group["net_return"].astype(float)).cumprod()
        if not wealth.empty and wealth.iloc[0] != 0:
            wealth = wealth / wealth.iloc[0]
        curves.append(pd.DataFrame({"date": group["date"], label: wealth}))
    if not curves:
        return pd.DataFrame(), {"best_local_id": best_local_id}
    out = curves[0]
    for curve in curves[1:]:
        out = out.merge(curve, on="date", how="outer")
    return align_and_rebase_equity(out), {"best_local_id": best_local_id}


def plot_supplementary_equity_curves(equity: pd.DataFrame) -> dict[str, Path]:
    if equity.empty:
        return {}
    os.environ.setdefault("MPLCONFIGDIR", str(PLOT_DIR / ".matplotlib"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plot_paths = {
        "extreme_tilt": PLOT_DIR / "smooth_score_policy_v1_supplementary_extreme_tilt_equity_curves.png",
        "best_local": PLOT_DIR / "smooth_score_policy_v1_supplementary_best_local_equity_curves.png",
    }
    date = pd.to_datetime(equity["date"])

    def draw(columns: list[str], title: str, path: Path) -> None:
        fig, ax = plt.subplots(figsize=(12, 7))
        for column in columns:
            if column in equity.columns:
                ax.plot(date, equity[column], linewidth=1.8, label=column)
        ax.set_title(title)
        ax.set_ylabel("Wealth, rebased to 1.0")
        ax.set_xlabel("Date")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="upper left", fontsize=9)
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(path, dpi=180, bbox_inches="tight")
        plt.close(fig)

    draw(
        [
            "Extreme Tilt 20%",
            "Extreme Tilt 30%",
            "Extreme Tilt 40%",
            "Extreme Tilt 50%",
            "50/50 G-D Buy & Hold",
            "100% G Buy & Hold",
            "100% D Buy & Hold",
        ],
        "Supplementary Extreme-Tilt Equity Curves, 10bp Cost",
        plot_paths["extreme_tilt"],
    )
    draw(
        [
            "Best Local Grid",
            "Extreme Tilt 50%",
            "50/50 G-D Buy & Hold",
            "100% G Buy & Hold",
            "100% D Buy & Hold",
            "SPY Buy & Hold",
        ],
        "Supplementary Best Local Grid vs Baselines, 10bp Cost",
        plot_paths["best_local"],
    )
    return plot_paths


def plot_vol_matched_equity_curves(equity: pd.DataFrame) -> dict[str, Path]:
    if equity.empty:
        return {}
    os.environ.setdefault("MPLCONFIGDIR", str(PLOT_DIR / ".matplotlib"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    path = PLOT_DIR / "smooth_score_policy_v1_vol_matched_static_equity_curves.png"
    date = pd.to_datetime(equity["date"])
    columns = [
        "Smooth Score Best Local",
        "100% G Buy & Hold",
        "Vol-Matched 100% G",
        "50/50 G-D",
        "Vol-Matched Static G/D",
        "Best Sharpe Static G/D",
        "Best CAGR Static G/D under Smooth MaxDD",
        "100% D Buy & Hold",
    ]
    fig, ax = plt.subplots(figsize=(12, 7))
    for wanted in columns:
        matches = [c for c in equity.columns if c == wanted or c.startswith(wanted + " (")]
        for column in matches:
            ax.plot(date, equity[column], linewidth=1.8, label=column)
    ax.set_title("Vol-Matched and Static G/D Controls, 10bp Cost")
    ax.set_ylabel("Wealth, rebased to 1.0")
    ax.set_xlabel("Date")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper left", fontsize=8)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return {"vol_matched_static": path}


def select_best_config_on_window(candidate_returns: pd.DataFrame, train_dates: pd.DatetimeIndex) -> tuple[str, pd.DataFrame]:
    train = candidate_returns[pd.to_datetime(candidate_returns["date"]).isin(train_dates)].copy()
    rows: list[dict[str, object]] = []
    for config_id, group in train.groupby("config_id", sort=False):
        group = group.sort_values("date")
        ret = pd.Series(group["net_return"].to_numpy(), index=pd.to_datetime(group["date"]))
        turnover = pd.Series(group["daily_turnover"].to_numpy(), index=pd.to_datetime(group["date"]))
        weights = pd.Series(group["g_weight"].to_numpy(), index=pd.to_datetime(group["date"]))
        row = {"config_id": config_id}
        row.update(performance_metrics(ret, turnover=turnover, weights=weights))
        rows.append(row)
    metrics = pd.DataFrame(rows)
    if metrics.empty:
        return "", metrics
    metrics["selection_score"] = (
        metrics["sharpe"].rank(pct=True)
        + metrics["calmar"].rank(pct=True)
        + metrics["cagr"].rank(pct=True)
        + metrics["max_drawdown"].rank(pct=True)
        + (-metrics["annual_turnover"]).rank(pct=True)
    ) / 5.0
    best = metrics.sort_values("selection_score", ascending=False).iloc[0]
    return str(best["config_id"]), metrics


def build_walk_forward_strategy(
    candidate_returns: pd.DataFrame,
    scheme: str,
    initial_train_window: int = VALIDATION_INITIAL_TRAIN_WINDOW,
    test_block: int = VALIDATION_TEST_BLOCK,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    data = candidate_returns[
        (candidate_returns["method"] == "supp_expanded_local_grid")
        & (candidate_returns["cost_bps"] == 10)
    ].copy()
    data["date"] = pd.to_datetime(data["date"])
    dates = pd.DatetimeIndex(sorted(data["date"].dropna().unique()))
    strategy_parts: list[pd.DataFrame] = []
    selection_rows: list[dict[str, object]] = []

    start = initial_train_window
    while start < len(dates):
        end = min(start + test_block, len(dates))
        if scheme == "expanding":
            train_dates = dates[:start]
        elif scheme == "rolling":
            train_dates = dates[max(0, start - initial_train_window):start]
        else:
            raise ValueError(f"Unknown walk-forward scheme: {scheme}")
        test_dates = dates[start:end]
        if len(train_dates) < initial_train_window or len(test_dates) == 0:
            start = end
            continue
        best_config, train_metrics = select_best_config_on_window(data, train_dates)
        if not best_config:
            start = end
            continue
        selected_test = data[
            (data["config_id"] == best_config)
            & (data["date"].isin(test_dates))
        ].copy()
        selected_test["validation_method"] = f"walk_forward_{scheme}"
        strategy_parts.append(selected_test)
        best_row = train_metrics[train_metrics["config_id"] == best_config].iloc[0].to_dict()
        selection_rows.append(
            {
                "scheme": scheme,
                "train_start": train_dates.min().date().isoformat(),
                "train_end": train_dates.max().date().isoformat(),
                "test_start": test_dates.min().date().isoformat(),
                "test_end": test_dates.max().date().isoformat(),
                "selected_config_id": best_config,
                "train_selection_score": best_row.get("selection_score", np.nan),
                "train_cagr": best_row.get("cagr", np.nan),
                "train_sharpe": best_row.get("sharpe", np.nan),
                "train_max_drawdown": best_row.get("max_drawdown", np.nan),
                "train_turnover": best_row.get("annual_turnover", np.nan),
            }
        )
        start = end
    strategy = pd.concat(strategy_parts, ignore_index=True) if strategy_parts else pd.DataFrame()
    selections = pd.DataFrame(selection_rows)
    return strategy, selections


def summarize_validation_returns(
    validation_returns: pd.DataFrame,
    benchmark_returns: pd.DataFrame,
    labels: dict[str, str],
    cost_bps: int = 10,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for label, key in labels.items():
        if key.startswith("benchmark_"):
            group = benchmark_returns[
                (benchmark_returns["method"] == key)
                & (benchmark_returns["config_id"] == key)
                & (benchmark_returns["cost_bps"] == cost_bps)
            ].copy()
        else:
            group = validation_returns[validation_returns["validation_method"] == key].copy()
        if group.empty:
            continue
        group["date"] = pd.to_datetime(group["date"])
        group = group.sort_values("date").dropna(subset=["net_return"])
        ret = pd.Series(group["net_return"].to_numpy(), index=group["date"])
        turnover = pd.Series(group.get("daily_turnover", pd.Series(0.0, index=group.index)).to_numpy(), index=group["date"])
        weights = pd.Series(group.get("g_weight", pd.Series(np.nan, index=group.index)).to_numpy(), index=group["date"])
        row = {"validation_label": label, "validation_method": key}
        row.update(performance_metrics(ret, turnover=turnover, weights=weights))
        row["final_wealth"] = 1.0 + row["total_return"]
        rows.append(row)
    summary = pd.DataFrame(rows)
    if not summary.empty and "Smooth Score WF Expanding" in set(summary["validation_label"]):
        base = summary[summary["validation_label"] == "Smooth Score WF Expanding"].iloc[0]
        summary["ann_excess_vs_expanding_wf"] = summary["cagr"] - float(base["cagr"])
        summary["max_dd_diff_vs_expanding_wf"] = summary["max_drawdown"] - float(base["max_drawdown"])
    return summary


def build_fixed_holdout_validation(
    supp_common_returns: pd.DataFrame,
    benchmark_common_returns: pd.DataFrame,
    initial_train_window: int = VALIDATION_INITIAL_TRAIN_WINDOW,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, str]]:
    candidates = supp_common_returns[
        (supp_common_returns["method"] == "supp_expanded_local_grid")
        & (supp_common_returns["cost_bps"] == 10)
    ].copy()
    candidates["date"] = pd.to_datetime(candidates["date"])
    candidate_dates = pd.DatetimeIndex(sorted(candidates["date"].dropna().unique()))
    if len(candidate_dates) <= initial_train_window:
        return pd.DataFrame(), pd.DataFrame(), {
            "calibration_start": "",
            "calibration_end": "",
            "holdout_start": "",
            "selected_config_id": "",
            "initial_train_window": str(initial_train_window),
        }
    calibration_dates = candidate_dates[:initial_train_window]
    holdout_start_ts = candidate_dates[initial_train_window]
    selected_config, calibration_metrics = select_best_config_on_window(candidates, calibration_dates)
    holdout = candidates[
        (candidates["config_id"] == selected_config)
        & (candidates["date"] >= holdout_start_ts)
    ].copy()
    holdout["validation_method"] = "fixed_earliest_window_holdout"
    bench_holdout = benchmark_common_returns[pd.to_datetime(benchmark_common_returns["date"]) >= holdout_start_ts].copy()
    labels = {
        "Fixed Parameter Earliest Holdout": "fixed_earliest_window_holdout",
        "50/50 G-D Holdout": "benchmark_50_50_gd",
        "100% G Holdout": "benchmark_100_g",
        "100% D Holdout": "benchmark_100_d",
        "SPY Holdout": "benchmark_spy",
    }
    summary = summarize_validation_returns(holdout, bench_holdout, labels, cost_bps=10)
    meta = {
        "calibration_start": calibration_dates.min().date().isoformat() if len(calibration_dates) else "",
        "calibration_end": calibration_dates.max().date().isoformat() if len(calibration_dates) else "",
        "holdout_start": holdout_start_ts.date().isoformat(),
        "selected_config_id": selected_config,
        "initial_train_window": str(initial_train_window),
    }
    return holdout, summary, meta


def build_nested_validation(
    supp_common_returns: pd.DataFrame,
    benchmark_common_returns: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, str]]:
    wf_expanding, sel_expanding = build_walk_forward_strategy(supp_common_returns, "expanding")
    wf_rolling, sel_rolling = build_walk_forward_strategy(supp_common_returns, "rolling")
    wf = pd.concat([wf_expanding, wf_rolling], ignore_index=True)
    selections = pd.concat([sel_expanding, sel_rolling], ignore_index=True)
    if wf.empty:
        return wf, selections, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}
    first_validation_date = pd.to_datetime(wf["date"]).min()
    benchmark_validation = benchmark_common_returns[pd.to_datetime(benchmark_common_returns["date"]) >= first_validation_date].copy()
    labels = {
        "Smooth Score WF Expanding": "walk_forward_expanding",
        "Smooth Score WF Rolling": "walk_forward_rolling",
        "50/50 G-D": "benchmark_50_50_gd",
        "100% G": "benchmark_100_g",
        "100% D": "benchmark_100_d",
        "SPY": "benchmark_spy",
    }
    summary = summarize_validation_returns(wf, benchmark_validation, labels, cost_bps=10)
    fixed_holdout, fixed_summary, fixed_meta = build_fixed_holdout_validation(supp_common_returns, benchmark_common_returns)
    return wf, selections, summary, fixed_holdout, fixed_summary, fixed_meta


def build_validation_equity_curves(
    wf_returns: pd.DataFrame,
    fixed_holdout: pd.DataFrame,
    benchmark_returns: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    def curve_from_group(group: pd.DataFrame, label: str) -> pd.DataFrame:
        group = group.copy()
        group["date"] = pd.to_datetime(group["date"])
        group = group.sort_values("date").dropna(subset=["net_return"])
        wealth = (1.0 + group["net_return"].astype(float)).cumprod()
        if not wealth.empty and wealth.iloc[0] != 0:
            wealth = wealth / wealth.iloc[0]
        return pd.DataFrame({"date": group["date"], label: wealth})

    wf_curves: list[pd.DataFrame] = []
    for method, label in [
        ("walk_forward_expanding", "WF Expanding"),
        ("walk_forward_rolling", "WF Rolling"),
    ]:
        group = wf_returns[wf_returns["validation_method"] == method]
        if not group.empty:
            wf_curves.append(curve_from_group(group, label))
    if wf_curves:
        start = min(pd.to_datetime(c["date"]).min() for c in wf_curves)
        for method, label in [
            ("benchmark_50_50_gd", "50/50 G-D"),
            ("benchmark_100_g", "100% G"),
            ("benchmark_100_d", "100% D"),
            ("benchmark_spy", "SPY"),
        ]:
            group = benchmark_returns[
                (benchmark_returns["method"] == method)
                & (benchmark_returns["config_id"] == method)
                & (benchmark_returns["cost_bps"] == 10)
                & (pd.to_datetime(benchmark_returns["date"]) >= start)
            ]
            wf_curves.append(curve_from_group(group, label))
        wf_equity = wf_curves[0]
        for curve in wf_curves[1:]:
            wf_equity = wf_equity.merge(curve, on="date", how="outer")
        wf_equity = align_and_rebase_equity(wf_equity)
    else:
        wf_equity = pd.DataFrame()

    holdout_curves: list[pd.DataFrame] = []
    if not fixed_holdout.empty:
        start = pd.to_datetime(fixed_holdout["date"]).min()
        holdout_curves.append(curve_from_group(fixed_holdout, "Fixed Parameter Holdout"))
        for method, label in [
            ("benchmark_50_50_gd", "50/50 G-D"),
            ("benchmark_100_g", "100% G"),
            ("benchmark_100_d", "100% D"),
            ("benchmark_spy", "SPY"),
        ]:
            group = benchmark_returns[
                (benchmark_returns["method"] == method)
                & (benchmark_returns["config_id"] == method)
                & (benchmark_returns["cost_bps"] == 10)
                & (pd.to_datetime(benchmark_returns["date"]) >= start)
            ]
            holdout_curves.append(curve_from_group(group, label))
        holdout_equity = holdout_curves[0]
        for curve in holdout_curves[1:]:
            holdout_equity = holdout_equity.merge(curve, on="date", how="outer")
        holdout_equity = align_and_rebase_equity(holdout_equity)
    else:
        holdout_equity = pd.DataFrame()
    return wf_equity, holdout_equity


def plot_validation_equity_curves(wf_equity: pd.DataFrame, holdout_equity: pd.DataFrame) -> dict[str, Path]:
    os.environ.setdefault("MPLCONFIGDIR", str(PLOT_DIR / ".matplotlib"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    paths: dict[str, Path] = {}

    def draw(equity: pd.DataFrame, title: str, path: Path) -> None:
        if equity.empty:
            return
        date = pd.to_datetime(equity["date"])
        fig, ax = plt.subplots(figsize=(12, 7))
        for column in equity.columns:
            if column == "date":
                continue
            ax.plot(date, equity[column], linewidth=1.8, label=column)
        ax.set_title(title)
        ax.set_ylabel("Wealth, rebased to 1.0")
        ax.set_xlabel("Date")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="upper left", fontsize=9)
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(path, dpi=180, bbox_inches="tight")
        plt.close(fig)

    wf_path = PLOT_DIR / "smooth_score_policy_v1_nested_walk_forward_equity_curves.png"
    holdout_path = PLOT_DIR / "smooth_score_policy_v1_fixed_parameter_holdout_equity_curves.png"
    draw(wf_equity, "Nested Walk-Forward Validation, 10bp Cost", wf_path)
    draw(holdout_equity, "Fixed Parameter Holdout Validation, 10bp Cost", holdout_path)
    if wf_path.exists():
        paths["walk_forward"] = wf_path
    if holdout_path.exists():
        paths["fixed_holdout"] = holdout_path
    return paths


def fmt_pct(value: float) -> str:
    if pd.isna(value):
        return ""
    return f"{value * 100:.2f}%"


def fmt_num(value: float) -> str:
    if pd.isna(value):
        return ""
    return f"{value:.2f}"


def markdown_table(df: pd.DataFrame, columns: list[str], pct_cols: set[str] | None = None, num_cols: set[str] | None = None, max_rows: int | None = None) -> list[str]:
    pct_cols = pct_cols or set()
    num_cols = num_cols or set()
    data = df.head(max_rows) if max_rows else df
    if data.empty:
        return ["无可用结果。"]
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in data[columns].to_dict("records"):
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


def date_span_from_csv(path: Path) -> tuple[str, str]:
    if not path.exists():
        return "N/A", "N/A"
    df = pd.read_csv(path, encoding="utf-8-sig")
    if df.empty:
        return "N/A", "N/A"
    if "date" in df.columns:
        dates = pd.to_datetime(df["date"], errors="coerce").dropna()
        if not dates.empty:
            return str(dates.min().date()), str(dates.max().date())
    if {"start_date", "end_date"}.issubset(df.columns):
        starts = pd.to_datetime(df["start_date"], errors="coerce").dropna()
        ends = pd.to_datetime(df["end_date"], errors="coerce").dropna()
        if not starts.empty and not ends.empty:
            return str(starts.min().date()), str(ends.max().date())
    return "N/A", "N/A"


def append_figure_with_span(lines: list[str], caption: str, figure_path: Path, source_table: Path) -> None:
    start, end = date_span_from_csv(source_table)
    lines.append(f"![{caption}]({figure_path})")
    lines.append(f"图表时间范围：`{start}` 到 `{end}`。")
    lines.append("")


def write_report(
    features: pd.DataFrame,
    metrics: pd.DataFrame,
    comparisons: pd.DataFrame,
    selected_summary: pd.DataFrame,
    supp_summary: pd.DataFrame,
    vol_static_comparison: pd.DataFrame,
    nested_summary: pd.DataFrame,
    fixed_holdout_summary: pd.DataFrame,
    yearly: pd.DataFrame,
    score_diag: pd.DataFrame,
    selected: dict[str, tuple[str, str]],
    common_start: pd.Timestamp,
    common_end: pd.Timestamp,
    plot_paths: dict[str, Path],
    supp_plot_paths: dict[str, Path],
    supp_equity_meta: dict[str, str],
    vol_static_plot_paths: dict[str, Path],
    vol_static_meta: dict[str, str],
    validation_plot_paths: dict[str, Path],
    fixed_holdout_meta: dict[str, str],
) -> None:
    report_path = REPORT_DIR / "phase1_smooth_score_policy_v1_report.md"
    m10 = metrics[metrics["cost_bps"] == 10].copy()
    top_trad = m10[m10["method"] == "traditional_smooth_score"].sort_values("selection_score", ascending=False).head(3)
    bench = m10[m10["method"].isin(["benchmark_50_50_gd", "benchmark_100_g", "benchmark_100_d", "benchmark_spy"])].copy()
    smooth_bench = m10[m10["method"].isin(["smooth_tnx_only", "smooth_core_only"])].sort_values("selection_score", ascending=False).groupby("method").head(3)
    key_metrics = pd.concat([top_trad, smooth_bench, bench], ignore_index=True)

    lines: list[str] = []
    lines.append("# 第一阶段 Smooth Continuous Score Policy v1 报告")
    lines.append("")
    lines.append("## 1. 本步目标")
    lines.append("")
    lines.append("本步不再找变量，而是检验 `TNX + SPY drawdown + 平滑交互项` 能否改善 G/D 动态配置。")
    lines.append("所有策略都使用连续 score、tanh 仓位映射和 EWMA 权重平滑；没有分位调仓、硬 if 规则或最小调仓阈值。")
    lines.append("")
    valid_target = features.dropna(subset=["future_gd_return_63d", "r", "d", "z_i1", "z_i2", "z_i3", "z_i4"])
    lines.append("## 2. 样本与口径")
    lines.append("")
    source_sample = features.dropna(subset=["g_return", "d_return"]).copy()
    smooth_feature_sample = features.dropna(subset=["g_return", "d_return", "r", "d", "z_i1", "z_i2", "z_i3", "z_i4"]).copy()
    lines.append(f"- G/D 日收益源样本：`{source_sample['date'].min().date()}` 到 `{source_sample['date'].max().date()}`，n=`{len(source_sample)}`。")
    lines.append(f"- 可用于 63 日目标诊断的样本：`{valid_target['date'].min().date()}` 到 `{valid_target['date'].max().date()}`，n=`{len(valid_target)}`。")
    lines.append(f"- Smooth score 完整特征样本：`{smooth_feature_sample['date'].min().date()}` 到 `{smooth_feature_sample['date'].max().date()}`，n=`{len(smooth_feature_sample)}`。")
    lines.append(f"- 主策略比较从 G/D 最早共同可用日期开始：`{common_start.date()}` 到 `{common_end.date()}`。")
    lines.append("- G/D 收益来自 state framework 输入面板；单 ETF 的孤立日线缺口已在价格层做最多 3 个交易日的 forward-fill 后再计算收益，避免一根缺失 K 线污染 63/126 日滚动变量。")
    lines.append("- 注意：`gd_trailing_126d` 需要 126 个交易日 warmup，因此动态 smooth score 的实际可交易起点会晚于 2016-12-21；这不是中途截样，而是变量定义带来的自然 warmup。")
    lines.append("- 信号在 t 日收盘后形成，t+1 日收益开始使用。")
    lines.append("- 标准化均为 expanding z-score，不使用全样本 z-score。")
    lines.append("- 本版报告只保留规则型 smooth score、补充 tilt 网格和 buy-and-hold 基准。")
    lines.append("- 交易成本报告 `0bp`、`5bp`、`10bp`、`20bp`；成本按 `2 × |ΔG权重| × cost_bps / 10000` 扣除。")
    lines.append("")
    lines.append("## 3. 第一轮：max_tilt 规格测试")
    lines.append("")
    lines.append("第一轮固定 `alpha=0.50, lambda_stress=0.25, lambda_crowded=0.15, tau_weight=1.0, eta=0.05`，只测试 `max_tilt` 与交易成本。这里的 `max_tilt` 是 tanh 平滑映射的最大主动倾斜幅度。")
    lines.append("")
    extreme_view = supp_summary[supp_summary["method"] == "supp_extreme_tilt_base"].sort_values(["cost_bps", "max_tilt"]).copy()
    lines.extend(
        markdown_table(
            extreme_view,
            [
                "cost_bps",
                "max_tilt",
                "final_wealth",
                "cagr",
                "sharpe",
                "max_drawdown",
                "calmar",
                "annual_turnover",
                "avg_g_weight",
                "ann_excess_vs_50_50",
                "ann_excess_vs_100_g",
                "max_dd_diff_vs_100_g",
            ],
            pct_cols={
                "max_tilt",
                "cagr",
                "max_drawdown",
                "annual_turnover",
                "avg_g_weight",
                "ann_excess_vs_50_50",
                "ann_excess_vs_100_g",
                "max_dd_diff_vs_100_g",
            },
            num_cols={"final_wealth", "sharpe", "calmar"},
        )
    )
    lines.append("")
    extreme_10 = extreme_view[extreme_view["cost_bps"] == 10].sort_values("selection_score", ascending=False)
    if not extreme_10.empty:
        best_extreme = extreme_10.iloc[0]
        lines.append(
            f"- 10bp 主口径下，固定结构里的最佳 `max_tilt` 是 `{best_extreme['max_tilt']:.0%}`；"
            f"CAGR `{best_extreme['cagr']:.2%}`，Sharpe `{best_extreme['sharpe']:.2f}`，Max DD `{best_extreme['max_drawdown']:.2%}`。"
        )
    lines.append("- 因此后续主策略比较不再沿用原始 20% tilt 的 `Traditional Smooth Score`，而是转向 50% tilt 体系。")
    lines.append("")
    if supp_plot_paths.get("extreme_tilt"):
        append_figure_with_span(
            lines,
            "Supplementary Extreme Tilt 资金曲线",
            supp_plot_paths["extreme_tilt"],
            TABLE_DIR / "smooth_score_policy_v1_supplementary_tilt_common_oos_equity_curves.csv",
        )
    lines.append("## 4. 第二轮：Expanded Local Grid")
    lines.append("")
    lines.append("第二轮按你的扩展网格运行：`alpha ∈ {0.50,0.67}`、`lambda_stress ∈ {0.25,0.50}`、`lambda_crowded ∈ {0.05,0.15,0.25}`、`max_tilt ∈ {20%,30%,40%,50%}`、`tau_weight ∈ {0.75,1.0,1.5}`、`eta ∈ {0.03,0.05,0.10}`。主结论看 10bp，20bp 作为压力测试。")
    lines.append("")
    local_10 = (
        supp_summary[(supp_summary["method"] == "supp_expanded_local_grid") & (supp_summary["cost_bps"] == 10)]
        .sort_values("selection_score", ascending=False)
        .head(10)
    )
    best_local_id = str(local_10.iloc[0]["config_id"]) if not local_10.empty else ""
    lines.append("### 4.1 10bp 主口径 Top 10")
    lines.append("")
    lines.extend(
        markdown_table(
            local_10,
            [
                "config_id",
                "final_wealth",
                "cagr",
                "sharpe",
                "max_drawdown",
                "calmar",
                "annual_turnover",
                "avg_g_weight",
                "ann_excess_vs_50_50",
                "ann_excess_vs_100_g",
                "max_dd_diff_vs_100_g",
                "selection_score",
            ],
            pct_cols={
                "cagr",
                "max_drawdown",
                "annual_turnover",
                "avg_g_weight",
                "ann_excess_vs_50_50",
                "ann_excess_vs_100_g",
                "max_dd_diff_vs_100_g",
                "selection_score",
            },
            num_cols={"final_wealth", "sharpe", "calmar"},
        )
    )
    lines.append("")
    local_20 = (
        supp_summary[(supp_summary["method"] == "supp_expanded_local_grid") & (supp_summary["cost_bps"] == 20)]
        .sort_values(["sharpe", "calmar", "cagr"], ascending=False)
        .head(10)
    )
    lines.append("### 4.2 20bp 压力测试 Top 10")
    lines.append("")
    lines.extend(
        markdown_table(
            local_20,
            [
                "config_id",
                "final_wealth",
                "cagr",
                "sharpe",
                "max_drawdown",
                "calmar",
                "annual_turnover",
                "avg_g_weight",
                "ann_excess_vs_50_50",
                "ann_excess_vs_100_g",
                "max_dd_diff_vs_100_g",
            ],
            pct_cols={
                "cagr",
                "max_drawdown",
                "annual_turnover",
                "avg_g_weight",
                "ann_excess_vs_50_50",
                "ann_excess_vs_100_g",
                "max_dd_diff_vs_100_g",
            },
            num_cols={"final_wealth", "sharpe", "calmar"},
        )
    )
    lines.append("")
    if not local_10.empty:
        sensitivity = supplement_cost_sensitivity(supp_summary, best_local_id)
        lines.append(f"### 4.3 10bp 入选局部网格配置的成本敏感性：`{best_local_id}`")
        lines.append("")
        lines.extend(
            markdown_table(
                sensitivity,
                [
                    "cost_bps",
                    "final_wealth",
                    "cagr",
                    "sharpe",
                    "max_drawdown",
                    "calmar",
                    "annual_turnover",
                    "ann_excess_vs_50_50",
                    "ann_excess_vs_100_g",
                ],
                pct_cols={
                    "cagr",
                    "max_drawdown",
                    "annual_turnover",
                    "ann_excess_vs_50_50",
                    "ann_excess_vs_100_g",
                },
                num_cols={"final_wealth", "sharpe", "calmar"},
            )
        )
        lines.append("")
    lines.append("### 4.4 局部最佳方案资金曲线")
    lines.append("")
    if best_local_id:
        lines.append(f"- 后续主策略配置：`{best_local_id}`。")
        lines.append("- 这个配置来自 expanded local grid，且 `max_tilt=50%`。后续所有主对比、vol-matched、静态 G/D 对照都以它作为目标 smooth score。")
    lines.append("")
    if supp_plot_paths.get("best_local"):
        append_figure_with_span(
            lines,
            "Supplementary Best Local Grid 资金曲线",
            supp_plot_paths["best_local"],
            TABLE_DIR / "smooth_score_policy_v1_supplementary_tilt_common_oos_equity_curves.csv",
        )
    lines.append("## 5. 以 50% tilt 最佳方案为主策略的对齐统计")
    lines.append("")
    lines.append("这一张表从这里开始统一主口径：`Best Local Grid (tilt 50%)` 是后续主策略；`Matched TNX-only` 与 `Matched Core-only` 使用同样的 `max_tilt/tau/eta` 仓位映射，分别只保留 TNX 或 TNX+drawdown 主轴；`Extreme 50% Tilt` 是固定结构下的 50% tilt 对照。所有方法先对齐到同一可用日期区间。")
    lines.append("")
    lines.extend(
        markdown_table(
            selected_summary,
            [
                "display_name",
                "config_id",
                "start_date",
                "end_date",
                "n_days",
                "final_wealth",
                "cagr",
                "ann_vol",
                "sharpe",
                "sortino",
                "max_drawdown",
                "calmar",
                "annual_turnover",
                "avg_g_weight",
            ],
            pct_cols={"cagr", "ann_vol", "max_drawdown", "annual_turnover", "avg_g_weight"},
            num_cols={"final_wealth", "sharpe", "sortino", "calmar"},
        )
    )
    lines.append("")
    lines.append("## 6. 以 50% tilt 最佳方案为主策略的增量比较，10bp 成本")
    lines.append("")
    lines.extend(
        markdown_table(
            comparisons,
            ["comparison", "annualized_excess_return", "tracking_error", "information_ratio", "max_dd_diff", "turnover_diff"],
            pct_cols={"annualized_excess_return", "tracking_error", "max_dd_diff", "turnover_diff"},
            num_cols={"information_ratio"},
        )
    )
    lines.append("")
    lines.append("## 7. 资金曲线对比")
    lines.append("")
    lines.append("下面两张图都使用 `10bp` 成本，并先取图内所有曲线的共同可用日期区间，再统一 rebase 到 `1.0`。第一张图比较 50% tilt 主策略、matched TNX-only、matched Core-only、Extreme 50% 与静态基准；第二张图只显示 buy-and-hold 基础基准。")
    lines.append("")
    if plot_paths.get("all_methods"):
        append_figure_with_span(
            lines,
            "共同起点所有方法资金曲线",
            plot_paths["all_methods"],
            TABLE_DIR / "smooth_score_policy_v1_common_oos_equity_curves.csv",
        )
    if plot_paths.get("buy_hold_gd"):
        append_figure_with_span(
            lines,
            "G/D Buy and Hold 基础资金曲线",
            plot_paths["buy_hold_gd"],
            TABLE_DIR / "smooth_score_policy_v1_common_oos_equity_curves.csv",
        )
    lines.append("图中 `100% G Buy & Hold` 和 `100% D Buy & Hold` 是单纯买入并持有 G、D 篮子的基础对照；`50/50 G-D Buy & Hold` 是不择时的静态配置基准。")
    lines.append("")
    lines.append("## 8. Vol-Matched 与静态 G/D 对照")
    lines.append("")
    lines.append("这一节以 10bp 主口径的 `Best Local Grid (tilt 50%)` 为目标策略，比较同风险水平下的 `100% G` 缩放版本、等波动/等回撤静态 G-D、以及最优静态 G-D。")
    if vol_static_meta.get("best_local_config_id"):
        lines.append(f"- 目标 Smooth Score 配置：`{vol_static_meta['best_local_config_id']}`")
    if vol_static_meta.get("vol_matched_g_scale"):
        lines.append(f"- Vol-matched 100% G 的缩放权重：`{float(vol_static_meta['vol_matched_g_scale']):.2%}`")
    lines.append("")
    lines.extend(
        markdown_table(
            vol_static_comparison,
            [
                "method_label",
                "comparison_type",
                "static_g_weight",
                "scale_to_g",
                "final_wealth",
                "cagr",
                "ann_vol",
                "sharpe",
                "sortino",
                "max_drawdown",
                "calmar",
                "annual_turnover",
                "ann_excess_vs_smooth",
                "max_dd_diff_vs_smooth",
            ],
            pct_cols={
                "static_g_weight",
                "scale_to_g",
                "cagr",
                "ann_vol",
                "max_drawdown",
                "annual_turnover",
                "ann_excess_vs_smooth",
                "max_dd_diff_vs_smooth",
            },
            num_cols={"final_wealth", "sharpe", "sortino", "calmar"},
        )
    )
    lines.append("")
    if vol_static_plot_paths.get("vol_matched_static"):
        append_figure_with_span(
            lines,
            "Vol-Matched 与静态 G/D 对照资金曲线",
            vol_static_plot_paths["vol_matched_static"],
            TABLE_DIR / "smooth_score_policy_v1_vol_matched_static_equity_curves.csv",
        )
    lines.append("## 9. Nested / Walk-Forward 与固定参数后验验证")
    lines.append("")
    lines.append("Walk-forward 没有固定 `max_tilt=50%`。它每次只用过去窗口，在 expanded local grid 候选集中重新选择参数；候选集包含不同 `max_tilt`、`lambda`、`tau` 和 `eta`。固定参数后验验证则使用最早完整 smooth score 样本中的首个训练窗口选参，然后从下一交易日开始固定该配置验证。")
    lines.append(f"- 最小训练窗口：`{VALIDATION_INITIAL_TRAIN_WINDOW}` 个交易日。")
    lines.append(f"- Walk-forward 测试块：`{VALIDATION_TEST_BLOCK}` 个交易日。")
    lines.append("")
    lines.append("### 9.1 Nested Walk-Forward")
    lines.append("")
    lines.extend(
        markdown_table(
            nested_summary,
            [
                "validation_label",
                "start_date",
                "end_date",
                "n_days",
                "final_wealth",
                "cagr",
                "ann_vol",
                "sharpe",
                "sortino",
                "max_drawdown",
                "calmar",
                "annual_turnover",
                "avg_g_weight",
                "ann_excess_vs_expanding_wf",
                "max_dd_diff_vs_expanding_wf",
            ],
            pct_cols={
                "cagr",
                "ann_vol",
                "max_drawdown",
                "annual_turnover",
                "avg_g_weight",
                "ann_excess_vs_expanding_wf",
                "max_dd_diff_vs_expanding_wf",
            },
            num_cols={"final_wealth", "sharpe", "sortino", "calmar"},
        )
    )
    lines.append("")
    if validation_plot_paths.get("walk_forward"):
        append_figure_with_span(
            lines,
            "Nested Walk-Forward 资金曲线",
            validation_plot_paths["walk_forward"],
            TABLE_DIR / "smooth_score_policy_v1_nested_walk_forward_equity_curves.csv",
        )
    lines.append("### 9.2 固定参数后验外样本验证")
    lines.append("")
    if fixed_holdout_meta:
        lines.append(
            f"- 参数选择期：`{fixed_holdout_meta.get('calibration_start')}` 到 `{fixed_holdout_meta.get('calibration_end')}`；"
            f"后验验证期从 `{fixed_holdout_meta.get('holdout_start')}` 开始；"
            f"训练窗口 `{fixed_holdout_meta.get('initial_train_window')}` 个交易日。"
        )
        lines.append(f"- 固定参数配置：`{fixed_holdout_meta.get('selected_config_id')}`")
        lines.append("")
    lines.extend(
        markdown_table(
            fixed_holdout_summary,
            [
                "validation_label",
                "start_date",
                "end_date",
                "n_days",
                "final_wealth",
                "cagr",
                "ann_vol",
                "sharpe",
                "sortino",
                "max_drawdown",
                "calmar",
                "annual_turnover",
                "avg_g_weight",
            ],
            pct_cols={"cagr", "ann_vol", "max_drawdown", "annual_turnover", "avg_g_weight"},
            num_cols={"final_wealth", "sharpe", "sortino", "calmar"},
        )
    )
    lines.append("")
    if validation_plot_paths.get("fixed_holdout"):
        append_figure_with_span(
            lines,
            "固定参数后验验证资金曲线",
            validation_plot_paths["fixed_holdout"],
            TABLE_DIR / "smooth_score_policy_v1_fixed_parameter_holdout_equity_curves.csv",
        )
    lines.append("## 10. Score 排序诊断")
    lines.append("")
    lines.extend(
        markdown_table(
            score_diag,
            ["method", "config_id", "Q1", "Q2", "Q3", "Q4", "Q5", "Q5_minus_Q1"],
            pct_cols={"Q1", "Q2", "Q3", "Q4", "Q5", "Q5_minus_Q1"},
        )
    )
    lines.append("")
    lines.append("## 11. 共同起点年度表现，10bp 成本")
    lines.append("")
    lines.extend(
        markdown_table(
            yearly,
            ["method", "config_id", "year", "cagr", "sharpe", "max_drawdown", "annual_turnover", "avg_g_weight"],
            pct_cols={"cagr", "max_drawdown", "annual_turnover", "avg_g_weight"},
            num_cols={"sharpe"},
            max_rows=80,
        )
    )
    lines.append("")
    lines.append("## 13. 输出文件")
    lines.append("")
    lines.append(f"- 特征面板：`{INPUT_DIR / 'smooth_score_policy_v1_feature_panel.csv'}`")
    lines.append(f"- 信号权重：`{TABLE_DIR / 'smooth_score_policy_v1_signals.csv'}`")
    lines.append(f"- 日收益：`{TABLE_DIR / 'smooth_score_policy_v1_daily_returns.csv'}`")
    lines.append(f"- 主策略表现：`{TABLE_DIR / 'smooth_score_policy_v1_metrics.csv'}`")
    lines.append(f"- 2016 起点主策略表现：`{TABLE_DIR / 'smooth_score_policy_v1_common_oos_metrics.csv'}`")
    lines.append(f"- 入选方法与 buy-and-hold 对齐统计：`{TABLE_DIR / 'smooth_score_policy_v1_common_oos_selected_summary.csv'}`")
    lines.append(f"- 增量比较：`{TABLE_DIR / 'smooth_score_policy_v1_comparisons.csv'}`")
    lines.append(f"- 2016 起点增量比较：`{TABLE_DIR / 'smooth_score_policy_v1_common_oos_comparisons.csv'}`")
    lines.append(f"- 年度表现：`{TABLE_DIR / 'smooth_score_policy_v1_yearly_metrics.csv'}`")
    lines.append(f"- 共同起点年度表现：`{TABLE_DIR / 'smooth_score_policy_v1_common_oos_yearly_metrics.csv'}`")
    lines.append(f"- score 诊断：`{TABLE_DIR / 'smooth_score_policy_v1_score_diagnostics.csv'}`")
    lines.append(f"- 2016 起点 score 诊断：`{TABLE_DIR / 'smooth_score_policy_v1_common_oos_score_diagnostics.csv'}`")
    lines.append(f"- 共同起点资金曲线：`{TABLE_DIR / 'smooth_score_policy_v1_common_oos_equity_curves.csv'}`")
    lines.append(f"- 补充 extreme/local tilt 配置：`{TABLE_DIR / 'smooth_score_policy_v1_supplementary_tilt_config_grid.csv'}`")
    lines.append(f"- 补充 extreme/local tilt 主表：`{TABLE_DIR / 'smooth_score_policy_v1_supplementary_tilt_common_oos_summary.csv'}`")
    lines.append(f"- 补充 extreme/local tilt 日收益：`{TABLE_DIR / 'smooth_score_policy_v1_supplementary_tilt_common_oos_returns.csv'}`")
    lines.append(f"- 补充 extreme/local tilt 资金曲线：`{TABLE_DIR / 'smooth_score_policy_v1_supplementary_tilt_common_oos_equity_curves.csv'}`")
    lines.append(f"- Vol-matched 与静态 G/D 对照表：`{TABLE_DIR / 'smooth_score_policy_v1_vol_matched_static_comparison.csv'}`")
    lines.append(f"- 静态 G/D 权重网格：`{TABLE_DIR / 'smooth_score_policy_v1_static_gd_grid.csv'}`")
    lines.append(f"- Vol-matched 与静态 G/D 资金曲线：`{TABLE_DIR / 'smooth_score_policy_v1_vol_matched_static_equity_curves.csv'}`")
    lines.append(f"- Nested walk-forward 选择记录：`{TABLE_DIR / 'smooth_score_policy_v1_nested_walk_forward_selections.csv'}`")
    lines.append(f"- Nested walk-forward 日收益：`{TABLE_DIR / 'smooth_score_policy_v1_nested_walk_forward_returns.csv'}`")
    lines.append(f"- Nested walk-forward 结果：`{TABLE_DIR / 'smooth_score_policy_v1_nested_walk_forward_summary.csv'}`")
    lines.append(f"- 固定参数后验验证日收益：`{TABLE_DIR / 'smooth_score_policy_v1_fixed_parameter_holdout_returns.csv'}`")
    lines.append(f"- 固定参数后验验证结果：`{TABLE_DIR / 'smooth_score_policy_v1_fixed_parameter_holdout_summary.csv'}`")
    lines.append(f"- 所有方法资金曲线图：`{PLOT_DIR / 'smooth_score_policy_v1_common_oos_equity_curves_all.png'}`")
    lines.append(f"- G/D buy-and-hold 基础曲线图：`{PLOT_DIR / 'smooth_score_policy_v1_common_oos_buy_hold_gd.png'}`")
    lines.append(f"- 补充 extreme tilt 曲线图：`{PLOT_DIR / 'smooth_score_policy_v1_supplementary_extreme_tilt_equity_curves.png'}`")
    lines.append(f"- 补充 local grid 曲线图：`{PLOT_DIR / 'smooth_score_policy_v1_supplementary_best_local_equity_curves.png'}`")
    lines.append(f"- Vol-matched 与静态 G/D 曲线图：`{PLOT_DIR / 'smooth_score_policy_v1_vol_matched_static_equity_curves.png'}`")
    lines.append(f"- Nested walk-forward 曲线图：`{PLOT_DIR / 'smooth_score_policy_v1_nested_walk_forward_equity_curves.png'}`")
    lines.append(f"- 固定参数后验验证曲线图：`{PLOT_DIR / 'smooth_score_policy_v1_fixed_parameter_holdout_equity_curves.png'}`")
    lines.append("- 所有保留表格与图像的起止日期已汇总到合并归档报告的 artifact date range 索引。")
    lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    panel = read_panel()
    features = build_feature_panel(panel)
    trad_signals, trad_configs = traditional_scores(features)
    bench_signals, bench_configs = benchmark_smooth_scores(features)
    static_signals = static_benchmark_signals(features)
    supp_signals, supp_configs = supplementary_tilt_signals(features)
    signals = pd.concat([trad_signals, bench_signals, static_signals], ignore_index=True)

    strategy_returns = build_strategy_returns(features, signals)
    metrics = add_selection_scores(build_metrics(strategy_returns))
    common_returns, common_start = common_oos_returns(strategy_returns)
    common_metrics = add_selection_scores(build_metrics(common_returns))
    supp_returns = build_strategy_returns(features, supp_signals)
    supp_common_returns = supp_returns[pd.to_datetime(supp_returns["date"]) >= common_start].copy()
    supp_common_metrics = add_selection_scores(build_metrics(supp_common_returns))
    benchmark_common_returns = common_returns[
        common_returns["method"].isin(["benchmark_50_50_gd", "benchmark_100_g", "benchmark_100_d", "benchmark_spy"])
    ].copy()
    supp_summary = add_supplement_baseline_columns(
        supp_common_metrics,
        pd.concat([supp_common_returns, benchmark_common_returns], ignore_index=True),
    )
    supp_summary = supp_summary.merge(supp_configs, on=["method", "config_id"], how="left")

    best_local = (
        supp_summary[(supp_summary["cost_bps"] == 10) & (supp_summary["method"] == "supp_expanded_local_grid")]
        .sort_values("selection_score", ascending=False)
        .iloc[0]
    )
    best_local_config = str(best_local["config_id"])
    selected_alpha = float(best_local["alpha"])
    selected_max_tilt = float(best_local["max_tilt"])
    selected_tau_weight = float(best_local["tau_weight"])
    selected_eta = float(best_local["eta"])
    matched_signals = matched_smooth_baseline_signals(
        features,
        alpha=selected_alpha,
        max_tilt=selected_max_tilt,
        tau_weight=selected_tau_weight,
        eta=selected_eta,
    )
    matched_returns = build_strategy_returns(features, matched_signals)
    matched_common_returns = matched_returns[pd.to_datetime(matched_returns["date"]) >= common_start].copy()
    combined_common_returns = pd.concat([common_returns, supp_common_returns, matched_common_returns], ignore_index=True)
    matched_tnx_config = f"tnx_tilt{selected_max_tilt:.2f}_tau{selected_tau_weight:.2f}_eta{selected_eta:.2f}"
    matched_core_config = f"core_a{selected_alpha:.2f}_tilt{selected_max_tilt:.2f}_tau{selected_tau_weight:.2f}_eta{selected_eta:.2f}"
    extreme_50 = supp_summary[
        (supp_summary["cost_bps"] == 10)
        & (supp_summary["method"] == "supp_extreme_tilt_base")
        & (supp_summary["max_tilt"].round(6) == 0.50)
    ].iloc[0]
    extreme_50_config = str(extreme_50["config_id"])

    selected = {
        "best_local_grid": ("supp_expanded_local_grid", best_local_config),
        "matched_tnx_only": ("matched_smooth_tnx_only", matched_tnx_config),
        "matched_core_only": ("matched_smooth_core_only", matched_core_config),
        "extreme_50_tilt": ("supp_extreme_tilt_base", extreme_50_config),
        "benchmark_50_50_gd": ("benchmark_50_50_gd", "benchmark_50_50_gd"),
        "benchmark_100_g": ("benchmark_100_g", "benchmark_100_g"),
        "benchmark_100_d": ("benchmark_100_d", "benchmark_100_d"),
        "benchmark_spy": ("benchmark_spy", "benchmark_spy"),
    }
    comparisons = []
    for args in [
        (selected["best_local_grid"], selected["matched_tnx_only"], "Best Local Grid - matched TNX-only"),
        (selected["best_local_grid"], selected["matched_core_only"], "Best Local Grid - matched Core-only"),
        (selected["best_local_grid"], selected["extreme_50_tilt"], "Best Local Grid - Extreme 50% Tilt"),
        (selected["best_local_grid"], selected["benchmark_50_50_gd"], "Best Local Grid - 50/50"),
        (selected["best_local_grid"], selected["benchmark_100_g"], "Best Local Grid - 100% G"),
        (selected["best_local_grid"], selected["benchmark_spy"], "Best Local Grid - SPY"),
    ]:
        row = aligned_comparison(combined_common_returns, args[0], args[1], args[2], cost_bps=10)
        if row is not None:
            comparisons.append(row)
    comparisons_df = pd.DataFrame(comparisons)

    equity_curves = build_equity_curves(combined_common_returns, selected, cost_bps=10)
    equity_start = pd.to_datetime(equity_curves["date"]).min() if not equity_curves.empty else common_start
    equity_end = pd.to_datetime(equity_curves["date"]).max() if not equity_curves.empty else pd.to_datetime(combined_common_returns["date"]).max()
    selected_keys = set(selected.values())
    yearly = yearly_metrics(combined_common_returns, selected_keys, start_date=equity_start, end_date=equity_end)
    all_signals = pd.concat([signals, supp_signals, matched_signals], ignore_index=True)
    score_diag = score_diagnostics(
        features,
        all_signals,
        {selected["best_local_grid"], selected["matched_tnx_only"], selected["matched_core_only"], selected["extreme_50_tilt"]},
        start_date=equity_start,
    )
    plot_paths = plot_equity_curves(equity_curves)
    selected_summary = selected_method_summary(combined_common_returns, equity_curves, selected, cost_bps=10)
    supp_equity_curves, supp_equity_meta = build_supplementary_equity_curves(
        supp_common_returns,
        benchmark_common_returns,
        supp_summary,
        cost_bps=10,
    )
    supp_plot_paths = plot_supplementary_equity_curves(supp_equity_curves)
    vol_static_comparison, static_gd_grid, vol_static_equity_curves, vol_static_meta = build_vol_matched_static_comparison(
        supp_common_returns,
        benchmark_common_returns,
        supp_summary,
        cost_bps=10,
    )
    vol_static_plot_paths = plot_vol_matched_equity_curves(vol_static_equity_curves)
    nested_wf_returns, nested_wf_selections, nested_summary, fixed_holdout_returns, fixed_holdout_summary, fixed_holdout_meta = build_nested_validation(
        supp_common_returns,
        benchmark_common_returns,
    )
    nested_wf_equity_curves, fixed_holdout_equity_curves = build_validation_equity_curves(
        nested_wf_returns,
        fixed_holdout_returns,
        benchmark_common_returns,
    )
    validation_plot_paths = plot_validation_equity_curves(nested_wf_equity_curves, fixed_holdout_equity_curves)

    features.to_csv(INPUT_DIR / "smooth_score_policy_v1_feature_panel.csv", index=False, encoding="utf-8-sig")
    pd.concat([trad_configs, bench_configs], ignore_index=True).to_csv(TABLE_DIR / "smooth_score_policy_v1_config_grid.csv", index=False, encoding="utf-8-sig")
    signals.to_csv(TABLE_DIR / "smooth_score_policy_v1_signals.csv", index=False, encoding="utf-8-sig")
    strategy_returns.to_csv(TABLE_DIR / "smooth_score_policy_v1_daily_returns.csv", index=False, encoding="utf-8-sig")
    metrics.to_csv(TABLE_DIR / "smooth_score_policy_v1_metrics.csv", index=False, encoding="utf-8-sig")
    common_metrics.to_csv(TABLE_DIR / "smooth_score_policy_v1_common_oos_metrics.csv", index=False, encoding="utf-8-sig")
    selected_summary.to_csv(TABLE_DIR / "smooth_score_policy_v1_common_oos_selected_summary.csv", index=False, encoding="utf-8-sig")
    supp_configs.to_csv(TABLE_DIR / "smooth_score_policy_v1_supplementary_tilt_config_grid.csv", index=False, encoding="utf-8-sig")
    supp_common_returns.to_csv(TABLE_DIR / "smooth_score_policy_v1_supplementary_tilt_common_oos_returns.csv", index=False, encoding="utf-8-sig")
    supp_summary.to_csv(TABLE_DIR / "smooth_score_policy_v1_supplementary_tilt_common_oos_summary.csv", index=False, encoding="utf-8-sig")
    comparisons_df.to_csv(TABLE_DIR / "smooth_score_policy_v1_comparisons.csv", index=False, encoding="utf-8-sig")
    comparisons_df.to_csv(TABLE_DIR / "smooth_score_policy_v1_common_oos_comparisons.csv", index=False, encoding="utf-8-sig")
    yearly.to_csv(TABLE_DIR / "smooth_score_policy_v1_yearly_metrics.csv", index=False, encoding="utf-8-sig")
    yearly.to_csv(TABLE_DIR / "smooth_score_policy_v1_common_oos_yearly_metrics.csv", index=False, encoding="utf-8-sig")
    score_diag.to_csv(TABLE_DIR / "smooth_score_policy_v1_score_diagnostics.csv", index=False, encoding="utf-8-sig")
    score_diag.to_csv(TABLE_DIR / "smooth_score_policy_v1_common_oos_score_diagnostics.csv", index=False, encoding="utf-8-sig")
    equity_curves.to_csv(TABLE_DIR / "smooth_score_policy_v1_common_oos_equity_curves.csv", index=False, encoding="utf-8-sig")
    supp_equity_curves.to_csv(TABLE_DIR / "smooth_score_policy_v1_supplementary_tilt_common_oos_equity_curves.csv", index=False, encoding="utf-8-sig")
    vol_static_comparison.to_csv(TABLE_DIR / "smooth_score_policy_v1_vol_matched_static_comparison.csv", index=False, encoding="utf-8-sig")
    static_gd_grid.to_csv(TABLE_DIR / "smooth_score_policy_v1_static_gd_grid.csv", index=False, encoding="utf-8-sig")
    vol_static_equity_curves.to_csv(TABLE_DIR / "smooth_score_policy_v1_vol_matched_static_equity_curves.csv", index=False, encoding="utf-8-sig")
    nested_wf_selections.to_csv(TABLE_DIR / "smooth_score_policy_v1_nested_walk_forward_selections.csv", index=False, encoding="utf-8-sig")
    nested_wf_returns.to_csv(TABLE_DIR / "smooth_score_policy_v1_nested_walk_forward_returns.csv", index=False, encoding="utf-8-sig")
    nested_summary.to_csv(TABLE_DIR / "smooth_score_policy_v1_nested_walk_forward_summary.csv", index=False, encoding="utf-8-sig")
    fixed_holdout_returns.to_csv(TABLE_DIR / "smooth_score_policy_v1_fixed_parameter_holdout_returns.csv", index=False, encoding="utf-8-sig")
    fixed_holdout_summary.to_csv(TABLE_DIR / "smooth_score_policy_v1_fixed_parameter_holdout_summary.csv", index=False, encoding="utf-8-sig")
    nested_wf_equity_curves.to_csv(TABLE_DIR / "smooth_score_policy_v1_nested_walk_forward_equity_curves.csv", index=False, encoding="utf-8-sig")
    fixed_holdout_equity_curves.to_csv(TABLE_DIR / "smooth_score_policy_v1_fixed_parameter_holdout_equity_curves.csv", index=False, encoding="utf-8-sig")
    common_end = pd.to_datetime(common_returns["date"]).max()
    write_report(
        features,
        common_metrics,
        comparisons_df,
        selected_summary,
        supp_summary,
        vol_static_comparison,
        nested_summary,
        fixed_holdout_summary,
        yearly,
        score_diag,
        selected,
        common_start,
        common_end,
        plot_paths,
        supp_plot_paths,
        supp_equity_meta,
        vol_static_plot_paths,
        vol_static_meta,
        validation_plot_paths,
        fixed_holdout_meta,
    )

    print(f"Traditional configs: {trad_configs['config_id'].nunique()}")
    print(f"Supplementary tilt configs: {supp_configs['config_id'].nunique()}")
    print(f"Signals rows: {len(signals)}")
    print(f"Metrics rows: {len(metrics)}")
    print(f"Report: {REPORT_DIR / 'phase1_smooth_score_policy_v1_report.md'}")


if __name__ == "__main__":
    main()

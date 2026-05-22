#!/usr/bin/env python3
"""Run a bond/credit-augmented Phase 1 timing diagnostic.

This experiment extends the continuous-variable Phase 1 diagnostic by adding
bond and credit variables that are available over the full evaluation window.
It excludes the recent-only HY/IG OAS series from the formal regressions because
those series are not aligned with the 2017-2026 Phase 1 sample.

The module does not build a trading policy.  It tests whether bond/credit
variables and their second-/third-order interactions provide explanatory power
for future G-D relative returns, both in raw future G-D and after a rate-only
residualization step.
"""

from __future__ import annotations

import itertools
import math
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
STATE_PANEL_PATH = ROOT / "data" / "phase1" / "state_framework_v2" / "inputs" / "phase1_state_framework_v2_panel.csv"
CREDIT_FRED_DIR = ROOT / "data" / "external" / "credit_liquidity" / "raw" / "fred"
MOOMOO_DIR = ROOT / "data" / "moomoo" / "research" / "kline_day_qfq"

OUT_DIR = ROOT / "data" / "phase1" / "bond_credit_augmented_v1"
INPUT_DIR = OUT_DIR / "inputs"
TABLE_DIR = OUT_DIR / "tables"
REPORT_DIR = OUT_DIR / "reports"

HORIZONS = (21, 63, 126)
MIN_ACTIVE_DAILY = 100
MIN_ACTIVE_NONOVERLAP = 5
ECONOMIC_EFFECT_THRESHOLD = 0.01

BASE_DIRECTIONAL = ("r", "d", "vh", "vr", "g63", "g126")
BOND_DIRECTIONAL = ("cs", "ce", "cg", "hys", "hyr", "lqs")
DIRECTIONAL_CONTROLS = BASE_DIRECTIONAL + BOND_DIRECTIONAL

VARIABLE_LABELS = {
    "r": "Rate relief: -z(10Y yield 21d change)",
    "d": "SPY drawdown depth: -z(SPY drawdown)",
    "vh": "High VIX: z(VIX 3Y percentile)",
    "vr": "VIX relief: -z(VIX 21d change)",
    "g63": "G-D trailing 63d relative strength",
    "g126": "G-D trailing 126d relative strength",
    "cs": "Credit stress level: z(BAA-10Y spread)",
    "ce": "Credit relief: -z(BAA-10Y spread 21d change)",
    "cg": "Credit quality gap: z(BAA spread - AAA spread)",
    "hys": "HY ETF stress: z(HYG 252d drawdown depth)",
    "hyr": "HY ETF relief: z(HYG/LQD 21d relative return)",
    "lqs": "IG credit stress: z(LQD/SHY 21d weakness)",
}

EXPECTED_SIGNS: dict[str, int] = {
    "r": 1,
    "d": 1,
    "vr": 1,
    "g126": -1,
    "ce": 1,
    "hyr": 1,
}


def ensure_dirs() -> None:
    for directory in (INPUT_DIR, TABLE_DIR, REPORT_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def sigmoid(x: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    values = 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=float)))
    if isinstance(x, pd.Series):
        return pd.Series(values, index=x.index)
    return values


def soft_gate(series: pd.Series, threshold: float = 0.0, scale: float = 1.0) -> pd.Series:
    return sigmoid((series - threshold) / scale)


def pos(series: pd.Series) -> pd.Series:
    return series.clip(lower=0.0)


def zscore(series: pd.Series) -> pd.Series:
    std = series.std(ddof=0)
    if not std or pd.isna(std):
        return pd.Series(np.nan, index=series.index)
    return (series - series.mean()) / std


def expanding_percentile(series: pd.Series, min_periods: int = 252) -> pd.Series:
    def last_pct(values: np.ndarray) -> float:
        s = pd.Series(values).dropna()
        if s.empty:
            return np.nan
        return float(s.rank(pct=True).iloc[-1])

    return series.expanding(min_periods=min_periods).apply(last_pct, raw=True)


def read_state_panel() -> pd.DataFrame:
    panel = pd.read_csv(STATE_PANEL_PATH, encoding="utf-8-sig")
    panel["date"] = pd.to_datetime(panel["date"]).dt.normalize()
    return panel.sort_values("date").drop_duplicates("date", keep="last").set_index("date")


def read_fred_series(series_id: str, name: str) -> pd.DataFrame:
    path = CREDIT_FRED_DIR / f"{series_id}.csv"
    if not path.exists():
        return pd.DataFrame(columns=["date", name])
    df = pd.read_csv(path)
    value_col = series_id if series_id in df.columns else df.columns[-1]
    df = df.rename(columns={"observation_date": "date", value_col: name})
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    df[name] = pd.to_numeric(df[name], errors="coerce")
    return df[["date", name]].sort_values("date")


def read_moomoo_close(symbol: str) -> pd.DataFrame:
    path = MOOMOO_DIR / f"US_{symbol}_KDAY_qfq.csv"
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["time_key"]).dt.normalize()
    return df[["date", "close"]].rename(columns={"close": f"{symbol.lower()}_close"}).sort_values("date")


def build_panel() -> pd.DataFrame:
    panel = read_state_panel().reset_index()
    keep = [
        "date",
        "future_gd_return_21d",
        "future_gd_return_63d",
        "future_gd_return_126d",
        "tnx_change_21d",
        "spy_drawdown",
        "vix_percentile_756d",
        "vix_change_21d",
        "gd_trailing_63d",
        "gd_trailing_126d",
    ]
    out = panel[keep].copy()

    for series_id, name in (("BAA10Y", "baa10y_spread"), ("AAA10Y", "aaa10y_spread")):
        out = out.merge(read_fred_series(series_id, name), on="date", how="left")

    for symbol in ("HYG", "LQD", "SHY"):
        out = out.merge(read_moomoo_close(symbol), on="date", how="left")

    out = out.sort_values("date").reset_index(drop=True)
    for col in ("baa10y_spread", "aaa10y_spread", "hyg_close", "lqd_close", "shy_close"):
        out[col] = out[col].ffill()

    out["baa_minus_aaa"] = out["baa10y_spread"] - out["aaa10y_spread"]
    out["baa10y_change_21d"] = out["baa10y_spread"] - out["baa10y_spread"].shift(21)
    out["baa_minus_aaa_change_21d"] = out["baa_minus_aaa"] - out["baa_minus_aaa"].shift(21)
    out["hyg_drawdown_252d"] = out["hyg_close"] / out["hyg_close"].rolling(252, min_periods=126).max() - 1.0
    out["hyg_drawdown_depth"] = (-out["hyg_drawdown_252d"]).clip(lower=0.0)
    out["hyg_lqd_rel_21d"] = (out["hyg_close"] / out["lqd_close"]) / (out["hyg_close"] / out["lqd_close"]).shift(21) - 1.0
    out["hyg_shy_rel_21d"] = (out["hyg_close"] / out["shy_close"]) / (out["hyg_close"] / out["shy_close"]).shift(21) - 1.0
    out["lqd_shy_rel_21d"] = (out["lqd_close"] / out["shy_close"]) / (out["lqd_close"] / out["shy_close"]).shift(21) - 1.0
    out["lqd_shy_weakness_21d"] = (-out["lqd_shy_rel_21d"]).clip(lower=0.0)

    z_sources = {
        "z_tnx_change_21d": "tnx_change_21d",
        "z_spy_drawdown": "spy_drawdown",
        "z_vix_percentile_756d": "vix_percentile_756d",
        "z_vix_change_21d": "vix_change_21d",
        "z_gd_trailing_63d": "gd_trailing_63d",
        "z_gd_trailing_126d": "gd_trailing_126d",
        "z_baa10y_spread": "baa10y_spread",
        "z_baa10y_change_21d": "baa10y_change_21d",
        "z_baa_minus_aaa": "baa_minus_aaa",
        "z_hyg_drawdown_depth": "hyg_drawdown_depth",
        "z_hyg_lqd_rel_21d": "hyg_lqd_rel_21d",
        "z_lqd_shy_weakness_21d": "lqd_shy_weakness_21d",
    }
    for z_col, source_col in z_sources.items():
        out[z_col] = zscore(out[source_col])

    out["r"] = -out["z_tnx_change_21d"]
    out["d"] = -out["z_spy_drawdown"]
    out["vh"] = out["z_vix_percentile_756d"]
    out["vr"] = -out["z_vix_change_21d"]
    out["g63"] = out["z_gd_trailing_63d"]
    out["g126"] = out["z_gd_trailing_126d"]
    out["cs"] = out["z_baa10y_spread"]
    out["ce"] = -out["z_baa10y_change_21d"]
    out["cg"] = out["z_baa_minus_aaa"]
    out["hys"] = out["z_hyg_drawdown_depth"]
    out["hyr"] = out["z_hyg_lqd_rel_21d"]
    out["lqs"] = out["z_lqd_shy_weakness_21d"]

    out["rate_headwind_pos"] = pos(-out["r"])
    out["rate_relief_pos"] = pos(out["r"])
    out["drawdown_pos"] = pos(out["d"])
    out["high_vix_pos"] = pos(out["vh"])
    out["vix_relief_pos"] = pos(out["vr"])
    out["vix_spike_pos"] = pos(-out["vr"])
    out["growth_ext_pos"] = pos(out["g126"])
    out["growth_weak_pos"] = pos(-out["g126"])
    out["credit_stress_pos"] = pos(out["cs"])
    out["credit_relief_pos"] = pos(out["ce"])
    out["credit_widening_pos"] = pos(-out["ce"])
    out["quality_gap_pos"] = pos(out["cg"])
    out["hy_stress_pos"] = pos(out["hys"])
    out["hy_relief_pos"] = pos(out["hyr"])
    out["ig_stress_pos"] = pos(out["lqs"])

    out["credit_stress_percentile"] = expanding_percentile(out["baa10y_spread"])
    out["hy_stress_percentile"] = expanding_percentile(out["hyg_drawdown_depth"])
    return out.replace([np.inf, -np.inf], np.nan).set_index("date")


def build_candidate_interactions(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    candidates: list[dict[str, object]] = []

    def add(name: str, series: pd.Series, group: str, question: str, expected_sign: int | None = None) -> None:
        panel[name] = series.replace([np.inf, -np.inf], np.nan)
        candidates.append(
            {
                "variable": name,
                "group": group,
                "question": question,
                "expected_sign": expected_sign,
                "active_n_daily_63d": int((panel[name].abs() > 1e-12).sum()),
            }
        )

    pair_expected: dict[str, int] = {}
    for stress in ("d", "vh", "cs", "hys", "lqs"):
        pair_expected[f"r_x_{stress}"] = 1
        pair_expected[f"vr_x_{stress}"] = 1
        pair_expected[f"ce_x_{stress}"] = 1
        pair_expected[f"hyr_x_{stress}"] = 1
    pair_expected["cs_x_ce"] = 1
    pair_expected["hys_x_hyr"] = 1
    pair_expected["cs_x_vr"] = 1
    pair_expected["hys_x_vr"] = 1
    pair_expected["cg_x_rate_headwind_proxy"] = -1

    for left, right in itertools.combinations(DIRECTIONAL_CONTROLS, 2):
        name = f"{left}_x_{right}"
        add(
            name,
            panel[left] * panel[right],
            "1_all_pairwise_directional",
            f"{VARIABLE_LABELS.get(left, left)} × {VARIABLE_LABELS.get(right, right)}",
            pair_expected.get(name) or pair_expected.get(f"{right}_x_{left}"),
        )

    positive_specs = [
        ("credit_stress_pos_x_credit_relief_pos", panel["credit_stress_pos"] * panel["credit_relief_pos"], 1, "High credit spread with credit-spread tightening"),
        ("credit_stress_pos_x_vix_relief_pos", panel["credit_stress_pos"] * panel["vix_relief_pos"], 1, "Credit stress with volatility relief"),
        ("credit_stress_pos_x_rate_relief_pos", panel["credit_stress_pos"] * panel["rate_relief_pos"], 1, "Credit stress with rate relief"),
        ("credit_stress_pos_x_drawdown_pos", panel["credit_stress_pos"] * panel["drawdown_pos"], None, "Credit stress inside market drawdown"),
        ("hy_stress_pos_x_hy_relief_pos", panel["hy_stress_pos"] * panel["hy_relief_pos"], 1, "HY stress with HY/LQD relief"),
        ("hy_stress_pos_x_vix_relief_pos", panel["hy_stress_pos"] * panel["vix_relief_pos"], 1, "HY stress with VIX relief"),
        ("hy_stress_pos_x_rate_relief_pos", panel["hy_stress_pos"] * panel["rate_relief_pos"], 1, "HY stress with rate relief"),
        ("ig_stress_pos_x_vix_relief_pos", panel["ig_stress_pos"] * panel["vix_relief_pos"], 1, "IG stress with volatility relief"),
        ("credit_widening_pos_x_vix_spike_pos", panel["credit_widening_pos"] * panel["vix_spike_pos"], -1, "Credit widening with VIX spike"),
        ("credit_widening_pos_x_rate_headwind_pos", panel["credit_widening_pos"] * panel["rate_headwind_pos"], -1, "Credit widening with rate headwind"),
        ("growth_ext_pos_x_credit_stress_pos", panel["growth_ext_pos"] * panel["credit_stress_pos"], -1, "Growth extended in credit stress"),
        ("growth_ext_pos_x_hy_stress_pos", panel["growth_ext_pos"] * panel["hy_stress_pos"], -1, "Growth extended in HY stress"),
        ("growth_weak_pos_x_credit_relief_pos", panel["growth_weak_pos"] * panel["credit_relief_pos"], 1, "Weak growth with credit relief"),
        ("growth_weak_pos_x_hy_relief_pos", panel["growth_weak_pos"] * panel["hy_relief_pos"], 1, "Weak growth with HY relief"),
    ]
    for name, series, sign, question in positive_specs:
        add(name, series, "2_positive_part_bond_credit", question, sign)

    three_way_specs = [
        (
            "drawdown_pos_x_credit_stress_pos_x_vix_relief_pos",
            panel["drawdown_pos"] * panel["credit_stress_pos"] * panel["vix_relief_pos"],
            1,
            "Drawdown × credit stress × VIX relief",
        ),
        (
            "drawdown_pos_x_credit_stress_pos_x_rate_relief_pos",
            panel["drawdown_pos"] * panel["credit_stress_pos"] * panel["rate_relief_pos"],
            1,
            "Drawdown × credit stress × rate relief",
        ),
        (
            "high_vix_pos_x_credit_stress_pos_x_vix_relief_pos",
            panel["high_vix_pos"] * panel["credit_stress_pos"] * panel["vix_relief_pos"],
            1,
            "High VIX × credit stress × VIX relief",
        ),
        (
            "credit_stress_pos_x_credit_relief_pos_x_rate_relief_pos",
            panel["credit_stress_pos"] * panel["credit_relief_pos"] * panel["rate_relief_pos"],
            1,
            "Credit stress × credit relief × rate relief",
        ),
        (
            "hy_stress_pos_x_hy_relief_pos_x_vix_relief_pos",
            panel["hy_stress_pos"] * panel["hy_relief_pos"] * panel["vix_relief_pos"],
            1,
            "HY stress × HY relief × VIX relief",
        ),
        (
            "credit_widening_pos_x_vix_spike_pos_x_rate_headwind_pos",
            panel["credit_widening_pos"] * panel["vix_spike_pos"] * panel["rate_headwind_pos"],
            -1,
            "Credit widening × VIX spike × rate headwind",
        ),
        (
            "growth_ext_pos_x_credit_stress_pos_x_rate_headwind_pos",
            panel["growth_ext_pos"] * panel["credit_stress_pos"] * panel["rate_headwind_pos"],
            -1,
            "Growth extended × credit stress × rate headwind",
        ),
        (
            "growth_ext_pos_x_hy_stress_pos_x_vix_spike_pos",
            panel["growth_ext_pos"] * panel["hy_stress_pos"] * panel["vix_spike_pos"],
            -1,
            "Growth extended × HY stress × VIX spike",
        ),
        (
            "growth_weak_pos_x_credit_relief_pos_x_vix_relief_pos",
            panel["growth_weak_pos"] * panel["credit_relief_pos"] * panel["vix_relief_pos"],
            1,
            "Growth weak × credit relief × VIX relief",
        ),
        (
            "growth_weak_pos_x_hy_relief_pos_x_rate_relief_pos",
            panel["growth_weak_pos"] * panel["hy_relief_pos"] * panel["rate_relief_pos"],
            1,
            "Growth weak × HY relief × rate relief",
        ),
    ]
    for name, series, sign, question in three_way_specs:
        add(name, series, "3_three_way_bond_credit", question, sign)

    candidate_df = pd.DataFrame(candidates)
    return panel, candidate_df


def ols_fit(y: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    beta = np.linalg.pinv(x.T @ x) @ x.T @ y
    fitted = x @ beta
    residuals = y - fitted
    return beta, fitted, residuals


def covariance_ols(x: np.ndarray, residuals: np.ndarray) -> np.ndarray:
    n, k = x.shape
    sse = float(np.sum(residuals**2))
    return (sse / max(n - k, 1)) * np.linalg.pinv(x.T @ x)


def covariance_hac(x: np.ndarray, residuals: np.ndarray, lag: int) -> np.ndarray:
    n, k = x.shape
    xtx_inv = np.linalg.pinv(x.T @ x)
    meat = np.zeros((k, k))
    for t in range(n):
        xt = x[t : t + 1].T
        meat += residuals[t] ** 2 * (xt @ xt.T)
    max_lag = min(lag, n - 1)
    for l in range(1, max_lag + 1):
        weight = 1.0 - l / (max_lag + 1.0)
        gamma = np.zeros_like(meat)
        for t in range(l, n):
            xt = x[t : t + 1].T
            x_lag = x[t - l : t - l + 1].T
            gamma += residuals[t] * residuals[t - l] * (xt @ x_lag.T)
        meat += weight * (gamma + gamma.T)
    cov = xtx_inv @ meat @ xtx_inv
    if n > k:
        cov *= n / (n - k)
    return cov


def t_values(beta: np.ndarray, cov: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    se = np.sqrt(np.maximum(np.diag(cov), 0))
    t = np.full_like(beta, np.nan, dtype=float)
    mask = se > 0
    t[mask] = beta[mask] / se[mask]
    return se, t


def regression_sample(panel: pd.DataFrame, horizon: int, variables: tuple[str, ...], sample_type: str) -> pd.DataFrame:
    target = f"future_gd_return_{horizon}d"
    needed = [target, *variables]
    data = panel[needed].replace([np.inf, -np.inf], np.nan).dropna().copy()
    if sample_type == "nonoverlap":
        data = data.iloc[::horizon].copy()
    return data


def run_regression(
    data: pd.DataFrame,
    target_col: str,
    variables: tuple[str, ...],
    model_id: str,
    horizon: int,
    sample_type: str,
    focus_variable: str | None = None,
) -> tuple[pd.DataFrame, dict[str, object], pd.Series]:
    y = data[target_col].to_numpy(dtype=float)
    x = np.column_stack([np.ones(len(data)), data[list(variables)].to_numpy(dtype=float)])
    names = ["intercept", *variables]
    beta, fitted, residuals = ols_fit(y, x)
    sse = float(np.sum(residuals**2))
    sst = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - sse / sst if sst > 0 else np.nan
    n, k = x.shape
    adj_r2 = 1.0 - (1.0 - r2) * (n - 1) / (n - k) if n > k and not pd.isna(r2) else np.nan
    cov = covariance_hac(x, residuals, horizon - 1) if sample_type == "daily_hac" else covariance_ols(x, residuals)
    se, t = t_values(beta, cov)
    rows = []
    for i, name in enumerate(names):
        rows.append(
            {
                "model_id": model_id,
                "sample_type": sample_type,
                "horizon_days": horizon,
                "variable": name,
                "focus_variable": focus_variable or "",
                "coefficient": float(beta[i]),
                "std_error_robust": float(se[i]),
                "t_robust": float(t[i]),
                "n": int(n),
                "start_date": data.index.min().date().isoformat(),
                "end_date": data.index.max().date().isoformat(),
                "r2": float(r2),
                "adj_r2": float(adj_r2),
                "rmse": math.sqrt(sse / max(n - k, 1)),
                "robust_se": "hac" if sample_type == "daily_hac" else "nonoverlap_ols",
            }
        )
    summary = {
        "model_id": model_id,
        "sample_type": sample_type,
        "horizon_days": horizon,
        "focus_variable": focus_variable or "",
        "n": int(n),
        "start_date": data.index.min().date().isoformat(),
        "end_date": data.index.max().date().isoformat(),
        "r2": float(r2),
        "adj_r2": float(adj_r2),
        "rmse": math.sqrt(sse / max(n - k, 1)),
        "robust_se": "hac" if sample_type == "daily_hac" else "nonoverlap_ols",
    }
    return pd.DataFrame(rows), summary, pd.Series(residuals, index=data.index)


def run_all(panel: pd.DataFrame, candidates: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    coef_parts = []
    summary_rows = []
    for horizon in HORIZONS:
        target = f"future_gd_return_{horizon}d"
        for sample_type in ("daily_hac", "nonoverlap"):
            main_vars = DIRECTIONAL_CONTROLS
            data = regression_sample(panel, horizon, main_vars, sample_type)
            coefs, summary, _ = run_regression(
                data, target, main_vars, "step1_bond_credit_main_effects", horizon, sample_type
            )
            coef_parts.append(coefs)
            summary_rows.append(summary)

            rate_data = regression_sample(panel, horizon, ("r",), sample_type)
            rate_coefs, rate_summary, rate_resid = run_regression(
                rate_data, target, ("r",), "rate_only", horizon, sample_type
            )
            coef_parts.append(rate_coefs)
            summary_rows.append(rate_summary)

            for candidate in candidates["variable"]:
                variables = tuple(dict.fromkeys([*DIRECTIONAL_CONTROLS, candidate]))
                data = regression_sample(panel, horizon, variables, sample_type)
                if len(data) <= len(variables) + 5:
                    continue
                coefs, summary, _ = run_regression(
                    data,
                    target,
                    variables,
                    "step2_step3_interaction_with_main_controls",
                    horizon,
                    sample_type,
                    focus_variable=candidate,
                )
                coef_parts.append(coefs)
                summary_rows.append(summary)

                residual_data = data.copy()
                aligned_rate_resid = rate_resid.reindex(residual_data.index)
                residual_data[f"rate_residual_{horizon}d"] = aligned_rate_resid
                residual_data = residual_data.dropna(subset=[f"rate_residual_{horizon}d"])
                resid_vars = tuple(dict.fromkeys([*(v for v in DIRECTIONAL_CONTROLS if v != "r"), candidate]))
                if len(residual_data) <= len(resid_vars) + 5:
                    continue
                resid_coefs, resid_summary, _ = run_regression(
                    residual_data,
                    f"rate_residual_{horizon}d",
                    resid_vars,
                    "step3_rate_residual_incremental",
                    horizon,
                    sample_type,
                    focus_variable=candidate,
                )
                coef_parts.append(resid_coefs)
                summary_rows.append(resid_summary)
    return pd.concat(coef_parts, ignore_index=True), pd.DataFrame(summary_rows)


def coef_lookup(
    coefs: pd.DataFrame,
    model_id: str,
    variable: str,
    horizon: int,
    sample_type: str,
    focus_variable: str | None = None,
) -> pd.Series | None:
    rows = coefs[
        (coefs["model_id"] == model_id)
        & (coefs["variable"] == variable)
        & (coefs["horizon_days"] == horizon)
        & (coefs["sample_type"] == sample_type)
    ]
    if focus_variable is not None:
        rows = rows[rows["focus_variable"] == focus_variable]
    if rows.empty:
        return None
    return rows.iloc[0]


def direction_ok(coef: float, expected_sign: int | None) -> bool | None:
    if expected_sign is None or pd.isna(coef):
        return None
    return np.sign(coef) == expected_sign


def build_gate_for_variables(
    coefs: pd.DataFrame,
    variables: pd.DataFrame,
    model_id: str,
    gate_group: str,
    use_focus: bool,
) -> pd.DataFrame:
    rows = []
    for item in variables.to_dict("records"):
        variable = str(item["variable"])
        expected = item.get("expected_sign")
        if pd.isna(expected):
            expected = None
        else:
            expected = int(expected)
        focus = variable if use_focus else None
        daily = {
            h: coef_lookup(coefs, model_id, variable, h, "daily_hac", focus_variable=focus)
            for h in HORIZONS
        }
        non63 = coef_lookup(coefs, model_id, variable, 63, "nonoverlap", focus_variable=focus)
        coef_21 = daily[21]["coefficient"] if daily[21] is not None else np.nan
        coef_63 = daily[63]["coefficient"] if daily[63] is not None else np.nan
        coef_126 = daily[126]["coefficient"] if daily[126] is not None else np.nan
        t_21 = daily[21]["t_robust"] if daily[21] is not None else np.nan
        t_63 = daily[63]["t_robust"] if daily[63] is not None else np.nan
        t_126 = daily[126]["t_robust"] if daily[126] is not None else np.nan
        non_coef = non63["coefficient"] if non63 is not None else np.nan
        non_t = non63["t_robust"] if non63 is not None else np.nan
        dir63 = direction_ok(coef_63, expected)
        adjacent_ok = None if expected is None else bool(direction_ok(coef_21, expected) or direction_ok(coef_126, expected))
        non_ok = None if expected is None else bool(direction_ok(non_coef, expected))
        economic_ok = abs(coef_63) >= ECONOMIC_EFFECT_THRESHOLD if not pd.isna(coef_63) else False
        active_n = int((variables.loc[variables["variable"] == variable, "active_n_daily_63d"].iloc[0])) if "active_n_daily_63d" in variables.columns else 0
        sample_63 = regression_sample(panel_global, 63, (variable,), "nonoverlap") if variable in panel_global.columns else pd.DataFrame()
        active_nonoverlap = int((sample_63[variable].abs() > 1e-12).sum()) if not sample_63.empty else 0
        coverage_ok = active_n >= MIN_ACTIVE_DAILY and active_nonoverlap >= MIN_ACTIVE_NONOVERLAP
        passes_gate = bool(dir63 and adjacent_ok and non_ok and economic_ok and coverage_ok) if expected is not None else False
        rows.append(
            {
                "gate_group": gate_group,
                "model_id": model_id,
                "variable": variable,
                "group": item.get("group", gate_group),
                "question": item.get("question", VARIABLE_LABELS.get(variable, variable)),
                "expected_sign": expected,
                "coef_21d": coef_21,
                "t_hac_21d": t_21,
                "coef_63d": coef_63,
                "t_hac_63d": t_63,
                "coef_126d": coef_126,
                "t_hac_126d": t_126,
                "nonoverlap_coef_63d": non_coef,
                "nonoverlap_t_63d": non_t,
                "active_n_63d": active_n,
                "nonoverlap_active_n_63d": active_nonoverlap,
                "direction_63_ok": dir63,
                "adjacent_horizon_direction_ok": adjacent_ok,
                "nonoverlap_direction_ok": non_ok,
                "economic_effect_63d": coef_63,
                "economic_magnitude_ok": economic_ok,
                "coverage_ok": coverage_ok,
                "passes_gate": passes_gate,
            }
        )
    return pd.DataFrame(rows)


panel_global = pd.DataFrame()


def build_gates(panel: pd.DataFrame, coefs: pd.DataFrame, candidates: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    global panel_global
    panel_global = panel
    main_vars = pd.DataFrame(
        {
            "variable": list(DIRECTIONAL_CONTROLS),
            "group": ["0_main_effect"] * len(DIRECTIONAL_CONTROLS),
            "question": [VARIABLE_LABELS.get(v, v) for v in DIRECTIONAL_CONTROLS],
            "expected_sign": [EXPECTED_SIGNS.get(v) for v in DIRECTIONAL_CONTROLS],
            "active_n_daily_63d": [int((panel[v].abs() > 1e-12).sum()) for v in DIRECTIONAL_CONTROLS],
        }
    )
    main_gate = build_gate_for_variables(
        coefs,
        main_vars,
        "step1_bond_credit_main_effects",
        "step1_bond_credit_main_effect_gate",
        use_focus=False,
    )
    raw_interaction_gate = build_gate_for_variables(
        coefs,
        candidates,
        "step2_step3_interaction_with_main_controls",
        "step2_raw_interaction_gate",
        use_focus=True,
    )
    residual_interaction_gate = build_gate_for_variables(
        coefs,
        candidates,
        "step3_rate_residual_incremental",
        "step3_rate_residual_interaction_gate",
        use_focus=True,
    )
    merged = raw_interaction_gate.merge(
        residual_interaction_gate[
            [
                "variable",
                "coef_63d",
                "t_hac_63d",
                "nonoverlap_coef_63d",
                "passes_gate",
                "economic_magnitude_ok",
                "coverage_ok",
            ]
        ].rename(
            columns={
                "coef_63d": "resid_coef_63d",
                "t_hac_63d": "resid_t_63d",
                "nonoverlap_coef_63d": "resid_nonoverlap_coef_63d",
                "passes_gate": "resid_pass",
                "economic_magnitude_ok": "resid_economic_magnitude_ok",
                "coverage_ok": "resid_coverage_ok",
            }
        ),
        on="variable",
        how="left",
    )
    merged = merged.rename(columns={"passes_gate": "raw_pass"})
    merged["final_pass"] = merged["raw_pass"].fillna(False) & merged["resid_pass"].fillna(False) & merged["coverage_ok"].fillna(False)
    return main_gate, raw_interaction_gate, merged


def input_coverage(panel: pd.DataFrame) -> pd.DataFrame:
    fields = [
        "baa10y_spread",
        "aaa10y_spread",
        "baa_minus_aaa",
        "baa10y_change_21d",
        "hyg_close",
        "lqd_close",
        "shy_close",
        "hyg_drawdown_depth",
        "hyg_lqd_rel_21d",
        "lqd_shy_weakness_21d",
    ]
    rows = []
    for col in fields:
        valid = panel.dropna(subset=[col])
        rows.append(
            {
                "column": col,
                "start_date": valid.index.min().date().isoformat() if not valid.empty else "",
                "end_date": valid.index.max().date().isoformat() if not valid.empty else "",
                "n_obs": int(len(valid)),
            }
        )
    return pd.DataFrame(rows)


def fmt_pct(value: float) -> str:
    if pd.isna(value):
        return ""
    return f"{value * 100:.2f}%"


def fmt_num(value: float) -> str:
    if pd.isna(value):
        return ""
    return f"{value:.2f}"


def fmt_bool(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return "是" if bool(value) else "否"


def markdown_table(
    df: pd.DataFrame,
    columns: list[str],
    pct_cols: set[str] | None = None,
    num_cols: set[str] | None = None,
    max_rows: int = 40,
) -> list[str]:
    pct_cols = pct_cols or set()
    num_cols = num_cols or set()
    if df.empty:
        return ["无可用结果。"]
    data = df[columns].head(max_rows).copy()
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in data.to_dict("records"):
        vals = []
        for col in columns:
            value = row[col]
            if col in pct_cols:
                vals.append(fmt_pct(value))
            elif col in num_cols:
                vals.append(fmt_num(value))
            elif col.endswith("_ok") or col in {"passes_gate", "raw_pass", "resid_pass", "final_pass"}:
                vals.append(fmt_bool(value))
            else:
                vals.append("" if pd.isna(value) else str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return lines


def write_report(
    panel: pd.DataFrame,
    candidates: pd.DataFrame,
    main_gate: pd.DataFrame,
    interaction_gate: pd.DataFrame,
    input_cov: pd.DataFrame,
) -> Path:
    report_path = REPORT_DIR / "phase1_bond_credit_augmented_v1_report.md"
    valid = panel.dropna(subset=[*DIRECTIONAL_CONTROLS, "future_gd_return_63d"])
    main_pass = main_gate[main_gate["passes_gate"] == True]["variable"].tolist()
    final_pass = interaction_gate[interaction_gate["final_pass"] == True]["variable"].tolist()
    raw_only = interaction_gate[(interaction_gate["raw_pass"] == True) & (interaction_gate["final_pass"] == False)].copy()
    top_t = interaction_gate.sort_values("t_hac_63d", key=lambda s: s.abs(), ascending=False).head(20)
    group_summary = interaction_gate.groupby("group", dropna=False).agg(
        n=("variable", "count"),
        raw_pass_n=("raw_pass", "sum"),
        resid_pass_n=("resid_pass", "sum"),
        final_pass_n=("final_pass", "sum"),
    ).reset_index()

    lines: list[str] = []
    lines.append("# Phase 1 Bond/Credit-Augmented Continuous Interaction v1")
    lines.append("")
    lines.append("## 1. 本步边界")
    lines.append("")
    lines.append("本实验把可对齐的债券/信用数据加入 Phase 1 连续变量择时诊断。它不重做 FF5 因子归因，也不生成新的交易策略；目标是回答债券/信用变量及其二阶、三阶交互项是否能解释或预测 future G-D。")
    lines.append("")
    lines.append("本次排除 HY OAS 与 IG OAS：这两个 FRED 导出文件当前只覆盖 2023-05-22 之后，不能和 2017 起点主样本对齐。正式回归只使用 BAA/AAA spreads 与 HYG/LQD/SHY ETF 信用代理。")
    lines.append("")
    lines.append("## 2. 数据与样本")
    lines.append("")
    lines.append(f"- 63 日主样本：`{valid.index.min().date()}` 到 `{valid.index.max().date()}`，n=`{len(valid)}`。")
    lines.append("- 频率：全部整理为日频交易日面板。")
    lines.append("- 因变量：`future_gd_return_21d / 63d / 126d`。")
    lines.append("- 标准误：日频重叠标签使用 Newey-West/HAC，lag = horizon - 1；另做 non-overlap 63d 检查。")
    lines.append("")
    lines.extend(markdown_table(input_cov, ["column", "start_date", "end_date", "n_obs"], max_rows=30))
    lines.append("")
    lines.append("## 3. 新增债券/信用变量")
    lines.append("")
    lines.append("- `cs = z(BAA10Y spread)`：信用压力水平。")
    lines.append("- `ce = -z(BAA10Y spread 21d change)`：信用利差收窄/信用缓和。")
    lines.append("- `cg = z(BAA spread - AAA spread)`：信用质量差距。")
    lines.append("- `hys = z(HYG 252d drawdown depth)`：高收益债 ETF 压力。")
    lines.append("- `hyr = z(HYG/LQD 21d relative return)`：高收益信用相对投资级信用修复。")
    lines.append("- `lqs = z(LQD/SHY 21d weakness)`：投资级信用相对短债走弱。")
    lines.append("")
    lines.append("## 4. 通过标准")
    lines.append("")
    lines.append("- Raw gate：63 日方向符合预设，经济幅度至少 1%，21 或 126 日至少一个方向一致，non-overlap 63 日不反向。")
    lines.append("- Rate residual gate：先用 `r` 解释 future G-D，再检验候选项是否解释剩余部分。")
    lines.append("- 覆盖率：日频 63 日样本至少 100 个非零观测，non-overlap 至少 5 个非零观测。")
    lines.append("- 对没有明确经济方向的候选项，只作为观察项，不计入 final pass。")
    lines.append("")
    lines.append("## 5. 总结")
    lines.append("")
    lines.append(f"- 主效应通过：`{', '.join(main_pass) if main_pass else 'none'}`")
    lines.append(f"- 二阶/三阶最终通过：`{', '.join(final_pass) if final_pass else 'none'}`")
    lines.append("")
    lines.append("整体含义：加入债券/信用后，可以检验信用 stress/relief 是否只是利率变量的影子，还是能提供 G-D timing 的增量。最终通过项需要同时通过 raw future G-D 和 rate-only residual。")
    lines.append("")
    lines.append("## 6. 主效应 Gate")
    lines.append("")
    lines.extend(
        markdown_table(
            main_gate,
            [
                "variable",
                "question",
                "expected_sign",
                "coef_63d",
                "t_hac_63d",
                "nonoverlap_coef_63d",
                "economic_effect_63d",
                "passes_gate",
            ],
            pct_cols={"coef_63d", "nonoverlap_coef_63d", "economic_effect_63d"},
            num_cols={"t_hac_63d"},
            max_rows=40,
        )
    )
    lines.append("")
    lines.append("## 7. 分组通过数量")
    lines.append("")
    lines.extend(markdown_table(group_summary, ["group", "n", "raw_pass_n", "resid_pass_n", "final_pass_n"], max_rows=20))
    lines.append("")
    lines.append("## 8. 最终通过项")
    lines.append("")
    passed = interaction_gate[interaction_gate["final_pass"] == True].copy()
    lines.extend(
        markdown_table(
            passed,
            [
                "group",
                "variable",
                "question",
                "expected_sign",
                "coef_63d",
                "t_hac_63d",
                "nonoverlap_coef_63d",
                "raw_pass",
                "resid_coef_63d",
                "resid_t_63d",
                "resid_nonoverlap_coef_63d",
                "resid_pass",
                "final_pass",
            ],
            pct_cols={"coef_63d", "nonoverlap_coef_63d", "resid_coef_63d", "resid_nonoverlap_coef_63d"},
            num_cols={"t_hac_63d", "resid_t_63d"},
            max_rows=40,
        )
    )
    lines.append("")
    lines.append("## 9. Raw 通过但 residual 未最终通过")
    lines.append("")
    lines.extend(
        markdown_table(
            raw_only,
            [
                "group",
                "variable",
                "question",
                "coef_63d",
                "t_hac_63d",
                "nonoverlap_coef_63d",
                "resid_coef_63d",
                "resid_t_63d",
                "final_pass",
            ],
            pct_cols={"coef_63d", "nonoverlap_coef_63d", "resid_coef_63d"},
            num_cols={"t_hac_63d", "resid_t_63d"},
            max_rows=50,
        )
    )
    lines.append("")
    lines.append("## 10. 63 日绝对 HAC t 值最高的观察项")
    lines.append("")
    lines.extend(
        markdown_table(
            top_t,
            [
                "group",
                "variable",
                "question",
                "expected_sign",
                "coef_63d",
                "t_hac_63d",
                "nonoverlap_coef_63d",
                "resid_coef_63d",
                "resid_t_63d",
                "final_pass",
            ],
            pct_cols={"coef_63d", "nonoverlap_coef_63d", "resid_coef_63d"},
            num_cols={"t_hac_63d", "resid_t_63d"},
            max_rows=20,
        )
    )
    lines.append("")
    lines.append("## 11. 输出文件")
    lines.append("")
    lines.append(f"- 输入面板：`{INPUT_DIR / 'phase1_bond_credit_augmented_v1_panel.csv'}`")
    lines.append(f"- 候选交互项：`{TABLE_DIR / 'bond_credit_augmented_v1_candidate_interactions.csv'}`")
    lines.append(f"- 系数长表：`{TABLE_DIR / 'bond_credit_augmented_v1_coefficients.csv'}`")
    lines.append(f"- 模型摘要：`{TABLE_DIR / 'bond_credit_augmented_v1_model_summary.csv'}`")
    lines.append(f"- 主效应 gate：`{TABLE_DIR / 'bond_credit_augmented_v1_main_effect_gate.csv'}`")
    lines.append(f"- 交互项 gate：`{TABLE_DIR / 'bond_credit_augmented_v1_interaction_gate.csv'}`")
    lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> None:
    ensure_dirs()
    panel = build_panel()
    panel, candidates = build_candidate_interactions(panel)
    coefs, model_summary = run_all(panel, candidates)
    main_gate, raw_interaction_gate, merged_interaction_gate = build_gates(panel, coefs, candidates)
    input_cov = input_coverage(panel)
    group_summary = merged_interaction_gate.groupby("group", dropna=False).agg(
        n=("variable", "count"),
        raw_pass_n=("raw_pass", "sum"),
        resid_pass_n=("resid_pass", "sum"),
        final_pass_n=("final_pass", "sum"),
    ).reset_index()

    panel.reset_index(names="date").to_csv(INPUT_DIR / "phase1_bond_credit_augmented_v1_panel.csv", index=False, encoding="utf-8-sig")
    candidates.to_csv(TABLE_DIR / "bond_credit_augmented_v1_candidate_interactions.csv", index=False, encoding="utf-8-sig")
    coefs.to_csv(TABLE_DIR / "bond_credit_augmented_v1_coefficients.csv", index=False, encoding="utf-8-sig")
    model_summary.to_csv(TABLE_DIR / "bond_credit_augmented_v1_model_summary.csv", index=False, encoding="utf-8-sig")
    input_cov.to_csv(TABLE_DIR / "bond_credit_augmented_v1_input_coverage.csv", index=False, encoding="utf-8-sig")
    main_gate.to_csv(TABLE_DIR / "bond_credit_augmented_v1_main_effect_gate.csv", index=False, encoding="utf-8-sig")
    raw_interaction_gate.to_csv(TABLE_DIR / "bond_credit_augmented_v1_raw_interaction_gate.csv", index=False, encoding="utf-8-sig")
    merged_interaction_gate.to_csv(TABLE_DIR / "bond_credit_augmented_v1_interaction_gate.csv", index=False, encoding="utf-8-sig")
    group_summary.to_csv(TABLE_DIR / "bond_credit_augmented_v1_group_summary.csv", index=False, encoding="utf-8-sig")
    report_path = write_report(panel, candidates, main_gate, merged_interaction_gate, input_cov)
    print(f"Panel rows: {len(panel)}")
    print(f"Candidate interactions: {len(candidates)}")
    print(f"Coefficient rows: {len(coefs)}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the revised phase-1 state framework.

This is the new first step after retiring the old composite_state results.
The goal is not to create a trading signal yet. It decomposes market conditions
into three neutral, interpretable state dimensions:

1. risk_state
2. rate_state
3. growth_state

All state variables use information observable at time t.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
KLINE_DIR = ROOT / "data" / "moomoo" / "research" / "kline_day_qfq"
INDEX_PATH = ROOT / "data" / "external" / "failed_moomoo_indices" / "processed" / "all_failed_moomoo_indices_normalized.csv"
ADJUSTED_PATH = ROOT / "data" / "phase1" / "factor_attribution" / "tables" / "factor_attribution_factor_adjusted_returns.csv"
OUT_DIR = ROOT / "data" / "phase1" / "state_framework_v2"
INPUT_DIR = OUT_DIR / "inputs"
TABLE_DIR = OUT_DIR / "tables"
REPORT_DIR = OUT_DIR / "reports"

G_SYMBOLS = ["QQQ", "XLK", "VGT", "SPYG", "VUG"]
D_SYMBOLS = ["SCHD", "VYM", "VTV", "FDVV", "COWZ"]
ALL_SYMBOLS = G_SYMBOLS + D_SYMBOLS + ["SPY"]
HORIZONS = [21, 63, 126, 252]
PRICE_FFILL_LIMIT = 3


STATE_DEFINITIONS = [
    {
        "dimension": "risk_state",
        "state": "risk_normal",
        "definition": "SPY drawdown > -5%.",
        "economic_meaning": "No material equity-market drawdown.",
    },
    {
        "dimension": "risk_state",
        "state": "risk_drawdown",
        "definition": "SPY drawdown <= -5%, excluding stress expanding and stress relief states.",
        "economic_meaning": "Equity market is in drawdown, but stress direction is not clearly worsening or easing.",
    },
    {
        "dimension": "risk_state",
        "state": "stress_expanding",
        "definition": "SPY drawdown <= -10% and (VIX 3Y rolling percentile >= 80% or VIX 21d change >= +2.5 points), unless stress relief also holds.",
        "economic_meaning": "Risk stress is elevated or expanding.",
    },
    {
        "dimension": "risk_state",
        "state": "stress_relief",
        "definition": "SPY drawdown <= -5% and VIX 21d change <= -2.5 points.",
        "economic_meaning": "Market is still in drawdown, but volatility stress is easing.",
    },
    {
        "dimension": "rate_state",
        "state": "rate_tailwind",
        "definition": "10Y Treasury yield 21d change <= -25bp.",
        "economic_meaning": "Falling-rate environment, usually a valuation tailwind for long-duration growth assets.",
    },
    {
        "dimension": "rate_state",
        "state": "rate_neutral",
        "definition": "-25bp < 10Y Treasury yield 21d change < +25bp.",
        "economic_meaning": "No large short-run rate impulse.",
    },
    {
        "dimension": "rate_state",
        "state": "rate_headwind",
        "definition": "10Y Treasury yield 21d change >= +25bp.",
        "economic_meaning": "Rising-rate environment, usually a valuation headwind for long-duration growth assets.",
    },
    {
        "dimension": "growth_state",
        "state": "growth_weak",
        "definition": "G-D trailing 63d <= 0 and G-D trailing 126d <= 0.",
        "economic_meaning": "Growth/tech has recently underperformed defensive income on both short and medium horizons.",
    },
    {
        "dimension": "growth_state",
        "state": "growth_turning_up",
        "definition": "G-D trailing 63d > 0 and G-D trailing 126d <= 0.",
        "economic_meaning": "Short-horizon relative strength has improved after medium-horizon weakness.",
    },
    {
        "dimension": "growth_state",
        "state": "growth_confirmed",
        "definition": "G-D trailing 63d > 0 and G-D trailing 126d > 0, excluding growth extended.",
        "economic_meaning": "Growth/tech relative strength is positive on both short and medium horizons.",
    },
    {
        "dimension": "growth_state",
        "state": "growth_extended",
        "definition": "G-D trailing 126d > 0 and its 3Y rolling percentile >= 80%.",
        "economic_meaning": "Growth/tech relative strength is unusually strong relative to its own recent history.",
    },
    {
        "dimension": "growth_state",
        "state": "growth_rolling_over",
        "definition": "G-D trailing 63d <= 0 and G-D trailing 126d > 0.",
        "economic_meaning": "Medium-horizon growth strength remains positive, but short-horizon relative momentum has turned down.",
    },
]


def ensure_dirs() -> None:
    for directory in [INPUT_DIR, TABLE_DIR, REPORT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def read_kline(symbol: str) -> pd.DataFrame:
    path = KLINE_DIR / f"US_{symbol}_KDAY_qfq.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["time_key"]).dt.normalize()
    df = df.sort_values("date").drop_duplicates("date", keep="last")
    df[symbol] = pd.to_numeric(df["close"], errors="coerce")
    return df[["date", symbol]].dropna()


def load_prices() -> pd.DataFrame:
    merged: pd.DataFrame | None = None
    for symbol in ALL_SYMBOLS:
        data = read_kline(symbol)
        merged = data if merged is None else merged.merge(data, on="date", how="outer")
    assert merged is not None
    return merged.sort_values("date").set_index("date")


def load_external_indices() -> pd.DataFrame:
    raw = pd.read_csv(INDEX_PATH, encoding="utf-8-sig")
    raw["date"] = pd.to_datetime(raw["date"]).dt.normalize()
    raw["value"] = pd.to_numeric(raw["value"], errors="coerce")
    pivot = raw.pivot_table(index="date", columns="failed_code", values="value", aggfunc="last").sort_index()
    rename = {
        "US..SPX": "spx",
        "US..NDX": "ndx",
        "US..VIX": "vix",
        "US..VXN": "vxn",
        "US..VVIX": "vvix",
        "US..TNX": "tnx",
        "US..IRX": "irx",
        "US..TYX": "tyx",
        "US..RUT": "rut",
    }
    pivot = pivot.rename(columns=rename)
    keep = [col for col in rename.values() if col in pivot.columns]
    return pivot[keep]


def trailing_cum_return(series: pd.Series, window: int) -> pd.Series:
    return (1 + series).rolling(window).apply(np.prod, raw=True) - 1


def future_cum_return(series: pd.Series, horizon: int) -> pd.Series:
    return (1 + series).shift(-1).rolling(horizon).apply(np.prod, raw=True).shift(-(horizon - 1)) - 1


def daily_returns_from_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Convert prices to returns while repairing isolated provider-level gaps.

    Some thin ETF histories contain one-off missing daily bars even after the
    fund is live. Forward-filling close prices for at most a few trading days
    prevents a single missing constituent from contaminating long rolling
    signals, while still leaving pre-inception and longer data holes as missing.
    """
    repaired = prices.sort_index().ffill(limit=PRICE_FFILL_LIMIT)
    return repaired.pct_change(fill_method=None)


def rolling_percentile(series: pd.Series, window: int = 756, min_periods: int = 252) -> pd.Series:
    def percentile(values: np.ndarray) -> float:
        current = values[-1]
        valid = values[~np.isnan(values)]
        if len(valid) == 0 or np.isnan(current):
            return np.nan
        return float(np.mean(valid <= current))

    return series.rolling(window=window, min_periods=min_periods).apply(percentile, raw=True)


def state_risk(panel: pd.DataFrame) -> pd.Series:
    out = pd.Series("risk_normal", index=panel.index, dtype="object")
    out = out.where(panel["spy_drawdown"] > -0.05, "risk_drawdown")
    stress_expanding = (panel["spy_drawdown"] <= -0.10) & (
        (panel["vix_percentile_756d"] >= 0.80) | (panel["vix_change_21d"] >= 2.5)
    )
    stress_relief = (panel["spy_drawdown"] <= -0.05) & (panel["vix_change_21d"] <= -2.5)
    out.loc[stress_expanding] = "stress_expanding"
    out.loc[stress_relief] = "stress_relief"
    return out.where(panel["spy_drawdown"].notna())


def state_rate(panel: pd.DataFrame) -> pd.Series:
    out = pd.Series(
        np.select(
            [panel["tnx_change_21d"] <= -0.25, panel["tnx_change_21d"] >= 0.25],
            ["rate_tailwind", "rate_headwind"],
            default="rate_neutral",
        ),
        index=panel.index,
        dtype="object",
    )
    return out.where(panel["tnx_change_21d"].notna())


def state_growth(panel: pd.DataFrame) -> pd.Series:
    short = panel["gd_trailing_63d"]
    medium = panel["gd_trailing_126d"]
    extended = (medium > 0) & (panel["gd_trailing_126d_percentile_756d"] >= 0.80)
    out = pd.Series(
        np.select(
            [
                extended,
                (short > 0) & (medium > 0),
                (short > 0) & (medium <= 0),
                (short <= 0) & (medium > 0),
                (short <= 0) & (medium <= 0),
            ],
            [
                "growth_extended",
                "growth_confirmed",
                "growth_turning_up",
                "growth_rolling_over",
                "growth_weak",
            ],
            default="growth_missing",
        ),
        index=panel.index,
        dtype="object",
    )
    return out.where(short.notna() & medium.notna() & panel["gd_trailing_126d_percentile_756d"].notna())


def build_panel() -> pd.DataFrame:
    prices = load_prices()
    returns = daily_returns_from_prices(prices[ALL_SYMBOLS])
    panel = returns.copy()
    panel["spy_close"] = prices["SPY"]
    panel["g_return"] = returns[G_SYMBOLS].where(returns[G_SYMBOLS].notna().all(axis=1)).mean(axis=1)
    panel["d_return"] = returns[D_SYMBOLS].where(returns[D_SYMBOLS].notna().all(axis=1)).mean(axis=1)
    panel["gd_return"] = panel["g_return"] - panel["d_return"]

    indices = load_external_indices()
    panel = panel.join(indices, how="left")
    for col in ["vix", "vxn", "vvix", "tnx", "irx", "tyx", "spx", "ndx", "rut"]:
        if col in panel.columns:
            panel[col] = panel[col].ffill()

    if ADJUSTED_PATH.exists():
        adjusted = pd.read_csv(ADJUSTED_PATH, encoding="utf-8-sig")
        adjusted = adjusted[adjusted["portfolio"] == "G-D"].copy()
        adjusted["date"] = pd.to_datetime(adjusted["date"]).dt.normalize()
        adjusted = adjusted.set_index("date").sort_index()
        panel["gd_factor_adjusted_residual"] = adjusted["factor_adjusted_residual"]

    running_peak = panel["spy_close"].cummax()
    panel["spy_drawdown"] = panel["spy_close"] / running_peak - 1
    panel["vix_percentile_756d"] = rolling_percentile(panel["vix"])
    panel["vix_change_21d"] = panel["vix"] - panel["vix"].shift(21)
    panel["tnx_change_21d"] = panel["tnx"] - panel["tnx"].shift(21)

    for window in [21, 63, 126, 252]:
        panel[f"g_trailing_{window}d"] = trailing_cum_return(panel["g_return"], window)
        panel[f"d_trailing_{window}d"] = trailing_cum_return(panel["d_return"], window)
        panel[f"gd_trailing_{window}d"] = panel[f"g_trailing_{window}d"] - panel[f"d_trailing_{window}d"]

    panel["gd_trailing_126d_percentile_756d"] = rolling_percentile(panel["gd_trailing_126d"])

    for horizon in HORIZONS:
        panel[f"future_g_{horizon}d"] = future_cum_return(panel["g_return"], horizon)
        panel[f"future_d_{horizon}d"] = future_cum_return(panel["d_return"], horizon)
        panel[f"future_gd_return_{horizon}d"] = panel[f"future_g_{horizon}d"] - panel[f"future_d_{horizon}d"]
        if "gd_factor_adjusted_residual" in panel.columns:
            panel[f"future_gd_residual_{horizon}d"] = future_cum_return(panel["gd_factor_adjusted_residual"], horizon)

    panel["risk_state"] = state_risk(panel)
    panel["rate_state"] = state_rate(panel)
    panel["growth_state"] = state_growth(panel)
    panel["state_triplet"] = panel["risk_state"] + " | " + panel["rate_state"] + " | " + panel["growth_state"]
    return panel


def nw_t_stat(values: pd.Series, lag: int) -> float:
    series = values.replace([np.inf, -np.inf], np.nan).dropna().to_numpy(dtype=float)
    n = len(series)
    if n <= 2:
        return np.nan
    centered = series - np.mean(series)
    gamma0 = float(np.dot(centered, centered) / n)
    var = gamma0
    max_lag = min(lag, n - 1)
    for l in range(1, max_lag + 1):
        cov = float(np.dot(centered[l:], centered[:-l]) / n)
        weight = 1.0 - l / (max_lag + 1.0)
        var += 2.0 * weight * cov
    se = math.sqrt(max(var, 0.0) / n)
    return float(np.mean(series) / se) if se > 0 else np.nan


def state_coverage(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    valid_sample = panel.dropna(subset=["g_return", "d_return"])
    total = len(valid_sample)
    for dimension in ["risk_state", "rate_state", "growth_state"]:
        state_values = valid_sample[dimension].fillna("state_unavailable_warmup")
        counts = state_values.value_counts(dropna=False)
        for state, count in counts.items():
            subset = valid_sample[state_values == state]
            rows.append(
                {
                    "dimension": dimension,
                    "state": state,
                    "n_days": int(count),
                    "pct_days": float(count / total) if total else np.nan,
                    "start_date": subset.index.min().date().isoformat() if len(subset) else "",
                    "end_date": subset.index.max().date().isoformat() if len(subset) else "",
                }
            )
    return pd.DataFrame(rows)


def state_forward_summary(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dimension in ["risk_state", "rate_state", "growth_state"]:
        for state, group in panel.groupby(dimension, dropna=True):
            for horizon in HORIZONS:
                col = f"future_gd_return_{horizon}d"
                values = group[col].dropna()
                if len(values) == 0:
                    continue
                rows.append(
                    {
                        "dimension": dimension,
                        "state": state,
                        "horizon_days": horizon,
                        "n": int(len(values)),
                        "mean_future_gd": float(values.mean()),
                        "median_future_gd": float(values.median()),
                        "win_rate": float((values > 0).mean()),
                        "p10_future_gd": float(values.quantile(0.10)),
                        "p90_future_gd": float(values.quantile(0.90)),
                        "nw_t_mean": nw_t_stat(values, lag=horizon),
                    }
                )
    return pd.DataFrame(rows)


def triplet_summary(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    data = panel.dropna(subset=["state_triplet", "future_gd_return_63d"]).copy()
    for triplet, group in data.groupby("state_triplet"):
        values = group["future_gd_return_63d"].dropna()
        rows.append(
            {
                "state_triplet": triplet,
                "n": int(len(values)),
                "pct_of_valid_63d": float(len(values) / len(data)) if len(data) else np.nan,
                "mean_future_gd_63d": float(values.mean()),
                "win_rate_63d": float((values > 0).mean()),
                "p10_future_gd_63d": float(values.quantile(0.10)),
                "p90_future_gd_63d": float(values.quantile(0.90)),
            }
        )
    return pd.DataFrame(rows).sort_values(["n", "mean_future_gd_63d"], ascending=[False, False])


def fmt_pct(value: float) -> str:
    if pd.isna(value):
        return ""
    return f"{value * 100:.2f}%"


def fmt_num(value: float) -> str:
    if pd.isna(value):
        return ""
    return f"{value:.2f}"


def markdown_table(
    df: pd.DataFrame,
    columns: list[str],
    pct_cols: set[str] | None = None,
    num_cols: set[str] | None = None,
    max_rows: int | None = None,
) -> list[str]:
    pct_cols = pct_cols or set()
    num_cols = num_cols or set()
    if df.empty:
        return ["无可用结果。"]
    data = df.head(max_rows) if max_rows else df
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in data[columns].to_dict("records"):
        values = []
        for col in columns:
            value = row[col]
            if col in pct_cols:
                values.append(fmt_pct(value))
            elif col in num_cols:
                values.append(fmt_num(value))
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def write_report(
    panel: pd.DataFrame,
    definitions: pd.DataFrame,
    coverage: pd.DataFrame,
    summary: pd.DataFrame,
    triplets: pd.DataFrame,
) -> None:
    report_path = REPORT_DIR / "phase1_state_framework_v2_step1_report.md"
    valid = panel.dropna(subset=["g_return", "d_return"])
    valid_states = panel.dropna(subset=["risk_state", "rate_state", "growth_state"])
    h63 = summary[summary["horizon_days"] == 63].copy()

    lines: list[str] = []
    lines.append("# 第一阶段新版状态框架 Step 1 汇总报告")
    lines.append("")
    lines.append("## 1. 本步目标")
    lines.append("")
    lines.append(
        "本步删除旧的 `composite_state` 派生结果后，重新建立更中性的三层状态框架："
        "`risk_state`、`rate_state`、`growth_state`。本步只做状态定义、覆盖率和描述性表现汇总，暂不做交易动作和策略优化。"
    )
    lines.append("")
    lines.append("## 2. 样本与口径")
    lines.append("")
    lines.append(f"- G 篮子：{', '.join(G_SYMBOLS)}。")
    lines.append(f"- D 篮子：{', '.join(D_SYMBOLS)}。")
    lines.append(f"- 有效 G/D 日收益样本：`{valid.index.min().date()}` 到 `{valid.index.max().date()}`，共 `{len(valid)}` 个交易日。")
    lines.append(
        f"- 三层状态同时可用样本：`{valid_states.index.min().date()}` 到 `{valid_states.index.max().date()}`，共 `{len(valid_states)}` 个交易日。"
    )
    lines.append("- 阈值只使用固定、少量、可解释的候选：-5% / -10% 回撤、VIX 20/80 分位、VIX 21 日 +-2.5 点、TNX 21 日 +-25bp、G-D 63/126 日相对动量。")
    lines.append("- `growth_extended` 使用 G-D trailing 126d 的 756 日滚动分位，避免全样本分位造成未来信息泄露。")
    lines.append("")
    lines.append("## 3. 状态定义")
    lines.append("")
    lines.extend(
        markdown_table(
            definitions,
            ["dimension", "state", "definition", "economic_meaning"],
        )
    )
    lines.append("")
    lines.append("## 4. 状态覆盖率")
    lines.append("")
    lines.extend(
        markdown_table(
            coverage.sort_values(["dimension", "n_days"], ascending=[True, False]),
            ["dimension", "state", "n_days", "pct_days", "start_date", "end_date"],
            pct_cols={"pct_days"},
        )
    )
    lines.append("")
    lines.append("## 5. 63 日未来 G-D 描述性汇总")
    lines.append("")
    lines.extend(
        markdown_table(
            h63.sort_values(["dimension", "mean_future_gd"], ascending=[True, False]),
            [
                "dimension",
                "state",
                "n",
                "mean_future_gd",
                "median_future_gd",
                "win_rate",
                "p10_future_gd",
                "p90_future_gd",
                "nw_t_mean",
            ],
            pct_cols={"mean_future_gd", "median_future_gd", "win_rate", "p10_future_gd", "p90_future_gd"},
            num_cols={"nw_t_mean"},
        )
    )
    lines.append("")
    lines.append("## 6. Top 15 三层状态组合，按样本数排序")
    lines.append("")
    lines.extend(
        markdown_table(
            triplets,
            ["state_triplet", "n", "pct_of_valid_63d", "mean_future_gd_63d", "win_rate_63d", "p10_future_gd_63d", "p90_future_gd_63d"],
            pct_cols={"pct_of_valid_63d", "mean_future_gd_63d", "win_rate_63d", "p10_future_gd_63d", "p90_future_gd_63d"},
            max_rows=15,
        )
    )
    lines.append("")
    lines.append("## 7. 初步观察")
    lines.append("")
    lines.append(
        "1. 新框架的优点是每个状态只表达一类信息：风险环境、利率环境、成长相对强弱，不再把多个经济叙事揉成一个复合标签。"
    )
    lines.append(
        "2. 本步结果只能作为描述性证据，不能直接解释为可交易信号；下一步应先做 episode-level 检验，再进入预注册动作表。"
    )
    lines.append(
        "3. 如果某个状态未来均值高但样本数少，后续必须用非重叠样本、walk-forward 和交易成本再验证。"
    )
    lines.append("")
    lines.append("## 8. 输出文件")
    lines.append("")
    lines.append(f"- 新版状态面板：`{INPUT_DIR / 'phase1_state_framework_v2_panel.csv'}`")
    lines.append(f"- 状态定义：`{TABLE_DIR / 'state_framework_v2_definitions.csv'}`")
    lines.append(f"- 状态覆盖率：`{TABLE_DIR / 'state_framework_v2_coverage.csv'}`")
    lines.append(f"- 各状态未来收益汇总：`{TABLE_DIR / 'state_framework_v2_forward_summary.csv'}`")
    lines.append(f"- 三层状态组合汇总：`{TABLE_DIR / 'state_framework_v2_triplet_summary.csv'}`")
    lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(panel: pd.DataFrame) -> None:
    definitions = pd.DataFrame(STATE_DEFINITIONS)
    coverage = state_coverage(panel)
    summary = state_forward_summary(panel)
    triplets = triplet_summary(panel)
    panel.reset_index(names="date").to_csv(INPUT_DIR / "phase1_state_framework_v2_panel.csv", index=False, encoding="utf-8-sig")
    definitions.to_csv(TABLE_DIR / "state_framework_v2_definitions.csv", index=False, encoding="utf-8-sig")
    coverage.to_csv(TABLE_DIR / "state_framework_v2_coverage.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(TABLE_DIR / "state_framework_v2_forward_summary.csv", index=False, encoding="utf-8-sig")
    triplets.to_csv(TABLE_DIR / "state_framework_v2_triplet_summary.csv", index=False, encoding="utf-8-sig")
    write_report(panel, definitions, coverage, summary, triplets)


def main() -> None:
    ensure_dirs()
    panel = build_panel()
    write_outputs(panel)
    print(f"Panel rows: {len(panel)}")
    print(f"Report: {REPORT_DIR / 'phase1_state_framework_v2_step1_report.md'}")


if __name__ == "__main__":
    main()

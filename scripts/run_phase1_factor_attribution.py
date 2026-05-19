#!/usr/bin/env python3
"""Run phase-1 FF5+Momentum factor attribution.

Outputs:
- fixed equal-weight G, D, and G-D return series
- full-sample FF5+MOM regressions for G, D, G-D, and each ETF
- 252/504 trading-day rolling betas for G, D, G-D
- a Chinese Markdown report for phase-1 interpretation
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
KLINE_DIR = ROOT / "data" / "moomoo" / "research" / "kline_day_qfq"
FF_PATH = ROOT / "data" / "external" / "fama_french" / "processed" / "fama_french_5_plus_momentum_daily.csv"
OUT_DIR = ROOT / "data" / "phase1" / "factor_attribution"
INPUT_DIR = OUT_DIR / "inputs"
TABLE_DIR = OUT_DIR / "tables"
REPORT_DIR = OUT_DIR / "reports"

G_SYMBOLS = ["QQQ", "XLK", "VGT", "SPYG", "VUG"]
D_SYMBOLS = ["SCHD", "VYM", "VTV", "FDVV", "COWZ"]
ALL_SYMBOLS = G_SYMBOLS + D_SYMBOLS
FACTOR_COLUMNS = ["mkt_rf", "smb", "hml", "rmw", "cma", "mom"]
ROLLING_WINDOWS = [252, 504]


@dataclass
class RegressionResult:
    portfolio: str
    dependent_return: str
    start_date: str
    end_date: str
    n_obs: int
    nw_lag: int
    r2: float
    adj_r2: float
    rmse_daily: float
    alpha_daily: float
    alpha_annualized: float
    alpha_t: float
    alpha_t_nw: float
    betas: dict[str, float]
    t_stats: dict[str, float]
    t_stats_nw: dict[str, float]


def ensure_dirs() -> None:
    for directory in [INPUT_DIR, TABLE_DIR, REPORT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def read_kline(symbol: str) -> pd.DataFrame:
    path = KLINE_DIR / f"US_{symbol}_KDAY_qfq.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["time_key"]).dt.normalize()
    df = df.sort_values("date")
    close = pd.to_numeric(df["close"], errors="coerce")
    out = pd.DataFrame({"date": df["date"], symbol: close})
    out = out.dropna(subset=[symbol]).drop_duplicates("date", keep="last")
    return out


def load_prices(symbols: Iterable[str]) -> pd.DataFrame:
    merged: pd.DataFrame | None = None
    for symbol in symbols:
        data = read_kline(symbol)
        merged = data if merged is None else merged.merge(data, on="date", how="outer")
    assert merged is not None
    merged = merged.sort_values("date").set_index("date")
    return merged


def load_factors() -> pd.DataFrame:
    ff = pd.read_csv(FF_PATH, encoding="utf-8-sig")
    ff["date"] = pd.to_datetime(ff["date"]).dt.normalize()
    keep = ["date", *FACTOR_COLUMNS, "rf"]
    ff = ff[keep].dropna().drop_duplicates("date", keep="last").set_index("date")
    return ff.sort_index()


def build_return_panel(prices: pd.DataFrame, factors: pd.DataFrame) -> pd.DataFrame:
    returns = prices.pct_change(fill_method=None)
    g_complete = returns[G_SYMBOLS].notna().all(axis=1)
    d_complete = returns[D_SYMBOLS].notna().all(axis=1)
    panel = returns.join(factors, how="inner")
    panel["g_return"] = returns[G_SYMBOLS].where(g_complete).mean(axis=1)
    panel["d_return"] = returns[D_SYMBOLS].where(d_complete).mean(axis=1)
    panel["gd_return"] = panel["g_return"] - panel["d_return"]
    panel["g_excess"] = panel["g_return"] - panel["rf"]
    panel["d_excess"] = panel["d_return"] - panel["rf"]
    # G-D is a zero-cost long-short return, so the risk-free leg cancels.
    panel["gd_excess"] = panel["gd_return"]
    for symbol in ALL_SYMBOLS:
        panel[f"{symbol}_excess"] = panel[symbol] - panel["rf"]
    return panel.sort_index()


def ols_fit(y: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    fitted = x @ beta
    residuals = y - fitted
    return beta, fitted, residuals


def newey_west_cov(x: np.ndarray, residuals: np.ndarray, lag: int) -> np.ndarray:
    n, k = x.shape
    xtx_inv = np.linalg.inv(x.T @ x)
    meat = np.zeros((k, k))
    for t in range(n):
        xt = x[t : t + 1].T
        meat += residuals[t] ** 2 * (xt @ xt.T)
    for l in range(1, lag + 1):
        weight = 1.0 - l / (lag + 1.0)
        gamma = np.zeros((k, k))
        for t in range(l, n):
            xt = x[t : t + 1].T
            xt_lag = x[t - l : t - l + 1].T
            gamma += residuals[t] * residuals[t - l] * (xt @ xt_lag.T)
        meat += weight * (gamma + gamma.T)
    cov = xtx_inv @ meat @ xtx_inv
    if n > k:
        cov *= n / (n - k)
    return cov


def auto_nw_lag(n_obs: int) -> int:
    # Common Newey-West rule of thumb for non-overlapping daily regressions.
    return max(1, int(round(4 * (n_obs / 100) ** (2 / 9))))


def run_regression(panel: pd.DataFrame, y_col: str, portfolio: str, dependent_return: str) -> RegressionResult:
    data = panel[[y_col, *FACTOR_COLUMNS]].dropna()
    y = data[y_col].to_numpy(dtype=float)
    x_factors = data[FACTOR_COLUMNS].to_numpy(dtype=float)
    x = np.column_stack([np.ones(len(data)), x_factors])
    names = ["alpha", *FACTOR_COLUMNS]
    beta, fitted, residuals = ols_fit(y, x)
    n, k = x.shape
    df = n - k
    sse = float(np.sum(residuals**2))
    sst = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1 - sse / sst if sst > 0 else float("nan")
    adj_r2 = 1 - (1 - r2) * (n - 1) / df if df > 0 else float("nan")
    rmse = math.sqrt(sse / df) if df > 0 else float("nan")
    xtx_inv = np.linalg.inv(x.T @ x)
    classical_cov = (sse / df) * xtx_inv if df > 0 else np.full((k, k), np.nan)
    classical_se = np.sqrt(np.maximum(np.diag(classical_cov), 0))
    nw_lag = auto_nw_lag(n)
    nw_cov = newey_west_cov(x, residuals, nw_lag)
    nw_se = np.sqrt(np.maximum(np.diag(nw_cov), 0))
    t = beta / classical_se
    t_nw = beta / nw_se
    betas = {name: float(beta[i]) for i, name in enumerate(names) if name != "alpha"}
    t_stats = {name: float(t[i]) for i, name in enumerate(names) if name != "alpha"}
    t_stats_nw = {name: float(t_nw[i]) for i, name in enumerate(names) if name != "alpha"}
    alpha_daily = float(beta[0])
    alpha_annualized = float((1 + alpha_daily) ** 252 - 1)
    return RegressionResult(
        portfolio=portfolio,
        dependent_return=dependent_return,
        start_date=data.index.min().date().isoformat(),
        end_date=data.index.max().date().isoformat(),
        n_obs=int(n),
        nw_lag=int(nw_lag),
        r2=float(r2),
        adj_r2=float(adj_r2),
        rmse_daily=float(rmse),
        alpha_daily=alpha_daily,
        alpha_annualized=alpha_annualized,
        alpha_t=float(t[0]),
        alpha_t_nw=float(t_nw[0]),
        betas=betas,
        t_stats=t_stats,
        t_stats_nw=t_stats_nw,
    )


def regression_result_to_row(result: RegressionResult) -> dict[str, float | int | str]:
    row: dict[str, float | int | str] = {
        "portfolio": result.portfolio,
        "dependent_return": result.dependent_return,
        "start_date": result.start_date,
        "end_date": result.end_date,
        "n_obs": result.n_obs,
        "nw_lag": result.nw_lag,
        "r2": result.r2,
        "adj_r2": result.adj_r2,
        "rmse_daily": result.rmse_daily,
        "alpha_daily": result.alpha_daily,
        "alpha_annualized": result.alpha_annualized,
        "alpha_t": result.alpha_t,
        "alpha_t_nw": result.alpha_t_nw,
    }
    for factor in FACTOR_COLUMNS:
        row[f"beta_{factor}"] = result.betas[factor]
        row[f"t_{factor}"] = result.t_stats[factor]
        row[f"t_nw_{factor}"] = result.t_stats_nw[factor]
    return row


def compute_rolling(panel: pd.DataFrame, targets: dict[str, tuple[str, str]]) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    cols = FACTOR_COLUMNS
    for portfolio, (y_col, dependent_return) in targets.items():
        data = panel[[y_col, *cols]].dropna()
        for window in ROLLING_WINDOWS:
            if len(data) < window:
                continue
            values = data[[y_col, *cols]].to_numpy(dtype=float)
            dates = data.index
            for end_idx in range(window - 1, len(data)):
                chunk = values[end_idx - window + 1 : end_idx + 1]
                y = chunk[:, 0]
                x = np.column_stack([np.ones(window), chunk[:, 1:]])
                beta, _, residuals = ols_fit(y, x)
                sse = float(np.sum(residuals**2))
                sst = float(np.sum((y - np.mean(y)) ** 2))
                r2 = 1 - sse / sst if sst > 0 else float("nan")
                row: dict[str, float | int | str] = {
                    "date": dates[end_idx].date().isoformat(),
                    "portfolio": portfolio,
                    "dependent_return": dependent_return,
                    "window": window,
                    "n_obs": window,
                    "alpha_daily": float(beta[0]),
                    "alpha_annualized": float((1 + beta[0]) ** 252 - 1),
                    "r2": float(r2),
                }
                for i, factor in enumerate(cols, start=1):
                    row[f"beta_{factor}"] = float(beta[i])
                rows.append(row)
    return pd.DataFrame(rows)


def compute_factor_adjusted_series(panel: pd.DataFrame, targets: dict[str, tuple[str, str]]) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for portfolio, (y_col, dependent_return) in targets.items():
        data = panel[[y_col, *FACTOR_COLUMNS]].dropna()
        y = data[y_col].to_numpy(dtype=float)
        x = np.column_stack([np.ones(len(data)), data[FACTOR_COLUMNS].to_numpy(dtype=float)])
        beta, fitted, residuals = ols_fit(y, x)
        out = pd.DataFrame(
            {
                "date": data.index.date.astype(str),
                "portfolio": portfolio,
                "dependent_return": dependent_return,
                "raw_return": y,
                "factor_fitted_return": fitted,
                "factor_adjusted_residual": residuals,
            }
        )
        out["factor_adjusted_cum_return"] = (1 + out["factor_adjusted_residual"]).cumprod() - 1
        rows.append(out)
    return pd.concat(rows, ignore_index=True)


def summarize_rolling_periods(rolling: pd.DataFrame) -> pd.DataFrame:
    if rolling.empty:
        return pd.DataFrame()
    periods = [
        ("covid_rebound_2020_2021", "2020-03-23", "2021-12-31"),
        ("rate_hike_2022", "2022-01-03", "2022-12-30"),
        ("ai_rally_2023_2024", "2023-01-03", "2024-12-31"),
        ("recent_2025_2026q1", "2025-01-02", "2026-03-31"),
    ]
    data = rolling.copy()
    data["date_dt"] = pd.to_datetime(data["date"])
    rows: list[dict[str, float | int | str]] = []
    value_cols = ["alpha_annualized", "r2", *[f"beta_{factor}" for factor in FACTOR_COLUMNS]]
    for period, start, end in periods:
        mask = (data["date_dt"] >= pd.Timestamp(start)) & (data["date_dt"] <= pd.Timestamp(end))
        period_data = data.loc[mask]
        for (portfolio, window), group in period_data.groupby(["portfolio", "window"]):
            row: dict[str, float | int | str] = {
                "period": period,
                "start_date": start,
                "end_date": end,
                "portfolio": portfolio,
                "window": int(window),
                "n_days": int(len(group)),
            }
            for col in value_cols:
                row[f"avg_{col}"] = float(group[col].mean())
                row[f"last_{col}"] = float(group.sort_values("date_dt")[col].iloc[-1])
            rows.append(row)
    return pd.DataFrame(rows)


def format_pct(value: float) -> str:
    if pd.isna(value):
        return ""
    return f"{value * 100:.2f}%"


def format_num(value: float) -> str:
    if pd.isna(value):
        return ""
    return f"{value:.3f}"


def interpretation_for_gd(gd: RegressionResult) -> list[str]:
    lines: list[str] = []
    mkt = gd.betas["mkt_rf"]
    hml = gd.betas["hml"]
    mom = gd.betas["mom"]
    rmw = gd.betas["rmw"]
    cma = gd.betas["cma"]
    alpha_t = gd.alpha_t_nw
    alpha_ann = gd.alpha_annualized
    lines.append(
        f"- G-D 的市场 beta 为 `{mkt:.3f}`，Newey-West t 值 `{gd.t_stats_nw['mkt_rf']:.2f}`。"
        + (" 这说明多成长/科技、空防御收益组合明显偏高市场 beta。" if mkt > 0 and abs(gd.t_stats_nw["mkt_rf"]) >= 2 else " 市场 beta 不算稳定显著。")
    )
    lines.append(
        f"- HML beta 为 `{hml:.3f}`，Newey-West t 值 `{gd.t_stats_nw['hml']:.2f}`。"
        + (" 负 HML 表明它本质上是多成长、空价值/红利的一部分。" if hml < 0 and abs(gd.t_stats_nw["hml"]) >= 2 else " HML 不是最稳定的解释项。")
    )
    lines.append(
        f"- MOM beta 为 `{mom:.3f}`，Newey-West t 值 `{gd.t_stats_nw['mom']:.2f}`。"
        + (" 这说明 G-D 和动量行情有明显同向关系，后续预测实验必须控制 MOM。" if mom > 0 and abs(gd.t_stats_nw["mom"]) >= 2 else " MOM 暴露不算稳定显著。")
    )
    lines.append(
        f"- RMW beta `{rmw:.3f}`、CMA beta `{cma:.3f}`，分别对应盈利能力和投资风格暴露。"
    )
    lines.append(
        f"- G-D 年化 alpha 为 `{format_pct(alpha_ann)}`，alpha 的 Newey-West t 值 `{alpha_t:.2f}`。"
        + (" 这意味着扣除 FF5+MOM 后仍有统计上较强的残差收益，需要进一步检查样本外稳定性。" if abs(alpha_t) >= 2 else " 这更像可解释的风格/因子组合，而不是已经证明的新 alpha。")
    )
    return lines


def write_report(
    panel: pd.DataFrame,
    portfolio_results: list[RegressionResult],
    etf_results: list[RegressionResult],
    rolling: pd.DataFrame,
    rolling_periods: pd.DataFrame,
    coverage: pd.DataFrame,
) -> None:
    report_path = REPORT_DIR / "phase1_factor_attribution_report.md"
    result_map = {r.portfolio: r for r in portfolio_results}
    gd = result_map["G-D"]
    lines: list[str] = []
    lines.append("# 第一阶段收益归因模块报告")
    lines.append("")
    lines.append("## 1. 本模块回答的问题")
    lines.append("")
    lines.append(
        "这个模块先回答：成长/科技篮子 G、防御收益篮子 D、以及 G-D 多空组合，到底分别是什么风险暴露。"
        "只有先把 MKT、SMB、HML、RMW、CMA、MOM 这些已知因子解释清楚，后面才能讨论市场状态是否真的能预测 G 相对 D 的未来收益。"
    )
    lines.append("")
    lines.append("## 2. 数据与口径")
    lines.append("")
    lines.append(f"- G 篮子：`{', '.join(G_SYMBOLS)}`，固定等权。")
    lines.append(f"- D 篮子：`{', '.join(D_SYMBOLS)}`，固定等权。")
    lines.append("- ETF 收益：Moomoo 日线 QFQ close 计算日收益。")
    lines.append("- 因子：Kenneth French FF5 daily + Momentum，使用 decimal return。")
    lines.append("- G 和 D 使用超额收益 `R - Rf`；G-D 是零成本多空组合，risk-free leg 相互抵消，因此用 `R_G - R_D`。")
    lines.append(
        f"- 回归样本：`{panel.dropna(subset=['g_excess','d_excess','gd_excess', *FACTOR_COLUMNS]).index.min().date()}` 到 "
        f"`{panel.dropna(subset=['g_excess','d_excess','gd_excess', *FACTOR_COLUMNS]).index.max().date()}`。"
    )
    lines.append("")
    lines.append("### 2.1 ETF 数据覆盖")
    lines.append("")
    lines.append("| symbol | first_return_date | last_return_date | n_returns |")
    lines.append("| --- | --- | --- | --- |")
    for row in coverage.to_dict("records"):
        lines.append(f"| {row['symbol']} | {row['first_return_date']} | {row['last_return_date']} | {row['n_returns']} |")
    lines.append("")
    lines.append("## 3. G、D、G-D 全样本 FF5+MOM 回归")
    lines.append("")
    lines.append("| portfolio | n | alpha ann. | alpha t(NW) | MKT | HML | RMW | CMA | MOM | adj R2 |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for result in portfolio_results:
        lines.append(
            f"| {result.portfolio} | {result.n_obs} | {format_pct(result.alpha_annualized)} | "
            f"{result.alpha_t_nw:.2f} | {result.betas['mkt_rf']:.3f} | {result.betas['hml']:.3f} | "
            f"{result.betas['rmw']:.3f} | {result.betas['cma']:.3f} | {result.betas['mom']:.3f} | {result.adj_r2:.3f} |"
        )
    lines.append("")
    lines.append("完整表格含普通 t 值和 Newey-West t 值，见 `tables/factor_attribution_portfolios_full_sample.csv`。")
    lines.append("")
    lines.append("### 3.1 G-D 初步解释")
    lines.append("")
    lines.extend(interpretation_for_gd(gd))
    lines.append("")
    lines.append("## 4. 单 ETF 因子暴露")
    lines.append("")
    lines.append("这张表用于检查篮子内部是否一致，以及后续是否需要重设权重或剔除风格不纯的 ETF。")
    lines.append("")
    lines.append("| ETF | group | n | alpha ann. | alpha t(NW) | MKT | HML | RMW | CMA | MOM | adj R2 |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for result in etf_results:
        group = "G" if result.portfolio in G_SYMBOLS else "D"
        lines.append(
            f"| {result.portfolio} | {group} | {result.n_obs} | {format_pct(result.alpha_annualized)} | "
            f"{result.alpha_t_nw:.2f} | {result.betas['mkt_rf']:.3f} | {result.betas['hml']:.3f} | "
            f"{result.betas['rmw']:.3f} | {result.betas['cma']:.3f} | {result.betas['mom']:.3f} | {result.adj_r2:.3f} |"
        )
    lines.append("")
    lines.append("完整单 ETF 表格见 `tables/factor_attribution_etfs_full_sample.csv`。")
    lines.append("")
    lines.append("## 5. 滚动 beta 输出")
    lines.append("")
    if rolling.empty:
        lines.append("滚动窗口样本不足，未生成。")
    else:
        latest = rolling.sort_values("date").groupby(["portfolio", "window"]).tail(1)
        lines.append("已生成 252 日和 504 日滚动 alpha/beta。最近一期结果如下：")
        lines.append("")
        lines.append("| portfolio | window | date | alpha ann. | MKT | HML | MOM | R2 |")
        lines.append("| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |")
        for row in latest.to_dict("records"):
            lines.append(
                f"| {row['portfolio']} | {row['window']} | {row['date']} | {format_pct(row['alpha_annualized'])} | "
                f"{row['beta_mkt_rf']:.3f} | {row['beta_hml']:.3f} | {row['beta_mom']:.3f} | {row['r2']:.3f} |"
            )
    lines.append("")
    lines.append("滚动 beta 文件：`tables/factor_attribution_rolling_betas.csv`。")
    lines.append("")
    if not rolling_periods.empty:
        lines.append("### 5.1 G-D 按阶段滚动暴露摘要")
        lines.append("")
        gd_periods = rolling_periods[(rolling_periods["portfolio"] == "G-D") & (rolling_periods["window"] == 252)]
        lines.append("| period | avg alpha ann. | avg MKT | avg HML | avg CMA | avg MOM | avg R2 |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
        for row in gd_periods.to_dict("records"):
            lines.append(
                f"| {row['period']} | {format_pct(row['avg_alpha_annualized'])} | "
                f"{row['avg_beta_mkt_rf']:.3f} | {row['avg_beta_hml']:.3f} | "
                f"{row['avg_beta_cma']:.3f} | {row['avg_beta_mom']:.3f} | {row['avg_r2']:.3f} |"
            )
        lines.append("")
        lines.append("完整阶段汇总文件：`tables/factor_attribution_rolling_period_summary.csv`。")
        lines.append("")
    lines.append("## 6. 第一阶段下一步怎么接")
    lines.append("")
    lines.append("1. 如果 G-D 的 MKT/HML/MOM 显著，而 alpha 不显著，后续研究应写成“状态依赖的风格因子动态配置”，不是新 alpha。")
    lines.append("2. 如果 G-D 的 alpha 显著，也不能马上进入策略，需要做样本外、子样本、交易成本和多重检验控制。")
    lines.append("3. 下一步应把本模块输出的残差收益、滚动 beta 和 alpha 接到状态变量模块，检验 `VIX/drawdown/rate/relative strength` 是否预测的是原始 G-D，还是因子调整后的 G-D。")
    lines.append("")
    lines.append("## 7. 输出文件")
    lines.append("")
    lines.append(f"- 回归面板：`{INPUT_DIR / 'phase1_factor_returns_panel.csv'}`")
    lines.append(f"- 组合全样本回归：`{TABLE_DIR / 'factor_attribution_portfolios_full_sample.csv'}`")
    lines.append(f"- 单 ETF 全样本回归：`{TABLE_DIR / 'factor_attribution_etfs_full_sample.csv'}`")
    lines.append(f"- 滚动 beta：`{TABLE_DIR / 'factor_attribution_rolling_betas.csv'}`")
    lines.append(f"- 因子调整 residual 序列：`{TABLE_DIR / 'factor_attribution_factor_adjusted_returns.csv'}`")
    lines.append(f"- 滚动 beta 阶段汇总：`{TABLE_DIR / 'factor_attribution_rolling_period_summary.csv'}`")
    lines.append(f"- 数据覆盖：`{TABLE_DIR / 'factor_attribution_data_coverage.csv'}`")
    lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(
    panel: pd.DataFrame,
    portfolio_results: list[RegressionResult],
    etf_results: list[RegressionResult],
    rolling: pd.DataFrame,
    adjusted: pd.DataFrame,
    rolling_periods: pd.DataFrame,
    coverage: pd.DataFrame,
) -> None:
    panel_out = panel.reset_index().rename(columns={"index": "date"})
    panel_out.to_csv(INPUT_DIR / "phase1_factor_returns_panel.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([regression_result_to_row(r) for r in portfolio_results]).to_csv(
        TABLE_DIR / "factor_attribution_portfolios_full_sample.csv", index=False, encoding="utf-8-sig"
    )
    pd.DataFrame([regression_result_to_row(r) for r in etf_results]).to_csv(
        TABLE_DIR / "factor_attribution_etfs_full_sample.csv", index=False, encoding="utf-8-sig"
    )
    rolling.to_csv(TABLE_DIR / "factor_attribution_rolling_betas.csv", index=False, encoding="utf-8-sig")
    adjusted.to_csv(TABLE_DIR / "factor_attribution_factor_adjusted_returns.csv", index=False, encoding="utf-8-sig")
    rolling_periods.to_csv(
        TABLE_DIR / "factor_attribution_rolling_period_summary.csv", index=False, encoding="utf-8-sig"
    )
    coverage.to_csv(TABLE_DIR / "factor_attribution_data_coverage.csv", index=False, encoding="utf-8-sig")
    write_report(panel, portfolio_results, etf_results, rolling, rolling_periods, coverage)


def data_coverage(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for symbol in ALL_SYMBOLS:
        series = panel[symbol].dropna()
        rows.append(
            {
                "symbol": symbol,
                "group": "G" if symbol in G_SYMBOLS else "D",
                "first_return_date": series.index.min().date().isoformat() if len(series) else "",
                "last_return_date": series.index.max().date().isoformat() if len(series) else "",
                "n_returns": int(len(series)),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    ensure_dirs()
    prices = load_prices(ALL_SYMBOLS)
    factors = load_factors()
    panel = build_return_panel(prices, factors)
    regression_panel = panel.dropna(subset=["g_excess", "d_excess", "gd_excess", *FACTOR_COLUMNS])
    portfolio_targets = {
        "G": ("g_excess", "G excess return"),
        "D": ("d_excess", "D excess return"),
        "G-D": ("gd_excess", "G-D zero-cost return"),
    }
    portfolio_results = [
        run_regression(regression_panel, y_col, portfolio, dependent_return)
        for portfolio, (y_col, dependent_return) in portfolio_targets.items()
    ]
    etf_results = [
        run_regression(panel, f"{symbol}_excess", symbol, f"{symbol} excess return")
        for symbol in ALL_SYMBOLS
    ]
    rolling = compute_rolling(regression_panel, portfolio_targets)
    adjusted = compute_factor_adjusted_series(regression_panel, portfolio_targets)
    rolling_periods = summarize_rolling_periods(rolling)
    coverage = data_coverage(panel)
    write_outputs(regression_panel, portfolio_results, etf_results, rolling, adjusted, rolling_periods, coverage)
    print(f"Panel rows: {len(regression_panel)}")
    print(f"Regression sample: {regression_panel.index.min().date()} to {regression_panel.index.max().date()}")
    print(f"Portfolio table: {TABLE_DIR / 'factor_attribution_portfolios_full_sample.csv'}")
    print(f"ETF table: {TABLE_DIR / 'factor_attribution_etfs_full_sample.csv'}")
    print(f"Rolling betas: {TABLE_DIR / 'factor_attribution_rolling_betas.csv'}")
    print(f"Factor-adjusted returns: {TABLE_DIR / 'factor_attribution_factor_adjusted_returns.csv'}")
    print(f"Report: {REPORT_DIR / 'phase1_factor_attribution_report.md'}")


if __name__ == "__main__":
    main()

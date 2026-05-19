#!/usr/bin/env python3
"""Build the 2016-full Phase 1 archive report.

This report intentionally keeps only the two requested research branches:

1. factor attribution;
2. smooth continuous score policy v1.

Older exploratory state-sorting/predictive-regression/OOS/state-action folders
are not included in the archive report, and ElasticNet is excluded.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "phase1" / "archive_2016_full"
REPORT_DIR = OUT_DIR / "reports"
TABLE_DIR = OUT_DIR / "tables"

FACTOR_REPORT = ROOT / "data" / "phase1" / "factor_attribution" / "reports" / "phase1_factor_attribution_report.md"
SMOOTH_REPORT = ROOT / "data" / "phase1" / "smooth_score_policy_v1" / "reports" / "phase1_smooth_score_policy_v1_report.md"
FACTOR_COVERAGE = ROOT / "data" / "phase1" / "factor_attribution" / "tables" / "factor_attribution_data_coverage.csv"
SMOOTH_SELECTED = ROOT / "data" / "phase1" / "smooth_score_policy_v1" / "tables" / "smooth_score_policy_v1_common_oos_selected_summary.csv"


def ensure_dirs() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def demote_markdown(text: str, levels: int = 1) -> str:
    prefix = "#" * levels
    out = []
    for line in text.splitlines():
        if line.startswith("#"):
            out.append(prefix + line)
        else:
            out.append(line)
    return "\n".join(out).strip() + "\n"


def write_lineage_table() -> Path:
    rows = [
        {
            "step": "1_factor_attribution",
            "script": "scripts/run_phase1_factor_attribution.py",
            "output_report": "data/phase1/factor_attribution/reports/phase1_factor_attribution_report.md",
            "sample_note": "FF5+MOM 回归样本从 2016-12-21 开始。",
            "archive_status": "included",
        },
        {
            "step": "2_smooth_score_policy_v1",
            "script": "scripts/run_phase1_state_framework_v2.py; scripts/run_phase1_smooth_score_policy_v1.py",
            "output_report": "data/phase1/smooth_score_policy_v1/reports/phase1_smooth_score_policy_v1_report.md",
            "sample_note": "G/D 源收益从 2016-12-21 开始；包含 126 日 trailing warmup 后的完整 smooth score 结果。",
            "archive_status": "included",
        },
        {
            "step": "excluded_old_exploratory_routes",
            "script": "run_phase1_state_sorting.py; run_phase1_predictive_regression.py; run_phase1_oos_validation.py; run_phase1_state_action_policy.py",
            "output_report": "old exploratory reports",
            "sample_note": "这些属于旧路线或中途实验结果，本归档按用户要求不纳入。",
            "archive_status": "excluded",
        },
        {
            "step": "excluded_elasticnet",
            "script": "N/A",
            "output_report": "N/A",
            "sample_note": "ElasticNet 相关实验、表格与结论全部排除。",
            "archive_status": "excluded",
        },
    ]
    path = TABLE_DIR / "phase1_2016_full_archive_lineage.csv"
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8-sig")
    return path


def build_report() -> Path:
    ensure_dirs()
    lineage_path = write_lineage_table()

    smooth = pd.read_csv(SMOOTH_SELECTED, encoding="utf-8-sig")
    smooth_rows = smooth[["display_name", "start_date", "end_date", "n_days", "final_wealth", "cagr", "ann_vol", "sharpe", "max_drawdown", "annual_turnover", "avg_g_weight"]]

    lines: list[str] = []
    lines.append("# Phase 1 2016 Full Archive Combined Report")
    lines.append("")
    lines.append("## 0. 归档口径")
    lines.append("")
    lines.append("本归档版本按最新要求重新整理，只保留两条主线：")
    lines.append("")
    lines.append("1. 因子归因：检验 G、D、G-D 的 FF5+MOM 风险暴露。")
    lines.append("2. Smooth Continuous Score Policy v1：保留该报告中的全部步骤，包括主网格、buy-and-hold、vol-matched、supplementary tilt、expanded local grid、walk-forward、fixed holdout、资金曲线和年度表现。")
    lines.append("")
    lines.append("不纳入旧的 state sorting / predictive regression / oos_validation / state-action 中途路线；不纳入 ElasticNet。")
    lines.append("")
    lines.append("## 1. 数据起点与自然 warmup")
    lines.append("")
    lines.append("- G/D 源收益共同起点：`2016-12-21`。")
    lines.append("- 因子归因回归样本：`2016-12-21` 到 `2026-03-31`。")
    lines.append("- Smooth score 主比较从 G/D 最早共同可用日期 `2016-12-21` 开始。")
    lines.append("- Smooth score 中的 `gd_trailing_126d` 必须使用 126 个交易日 warmup，因此完整 smooth score 动态策略的实际交易起点自然晚于 2016-12-21。这个 warmup 被保留并解释，不视为中途截样。")
    lines.append("")
    lines.append("## 2. 研究链路")
    lines.append("")
    lines.append(f"链路表已输出到：`{lineage_path.relative_to(ROOT)}`")
    lines.append("")
    lines.append("| step | archive_status | sample_note |")
    lines.append("| --- | --- | --- |")
    lineage = pd.read_csv(lineage_path, encoding="utf-8-sig")
    for row in lineage[["step", "archive_status", "sample_note"]].to_dict("records"):
        lines.append(f"| {row['step']} | {row['archive_status']} | {row['sample_note']} |")
    lines.append("")
    lines.append("## 3. Smooth Policy 入选方法概览")
    lines.append("")
    lines.append("| display_name | start_date | end_date | n_days | final_wealth | CAGR | Ann Vol | Sharpe | Max DD | Turnover | Avg G |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in smooth_rows.to_dict("records"):
        lines.append(
            f"| {row['display_name']} | {row['start_date']} | {row['end_date']} | {int(row['n_days'])} | "
            f"{row['final_wealth']:.2f} | {row['cagr']:.2%} | {row['ann_vol']:.2%} | {row['sharpe']:.2f} | "
            f"{row['max_drawdown']:.2%} | {row['annual_turnover']:.2%} | "
            f"{'' if pd.isna(row['avg_g_weight']) else format(row['avg_g_weight'], '.2%')} |"
        )
    lines.append("")
    lines.append("## 4. 合并报告正文")
    lines.append("")
    lines.append("### 4.1 因子归因模块")
    lines.append("")
    lines.append(demote_markdown(read_text(FACTOR_REPORT), levels=3))
    lines.append("")
    lines.append("### 4.2 Smooth Continuous Score Policy v1")
    lines.append("")
    lines.append(demote_markdown(read_text(SMOOTH_REPORT), levels=3))

    path = REPORT_DIR / "phase1_2016_full_combined_report.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    path = build_report()
    print(f"Combined report: {path}")


if __name__ == "__main__":
    main()

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

ARCHIVE_MODULES = [
    "archive_2016_full",
    "factor_attribution",
    "state_framework_v2",
    "smooth_score_policy_v1",
]

PACKAGE_EXCLUDED_GENERATED = {
    "smooth_score_policy_v1_daily_returns.csv",
    "smooth_score_policy_v1_signals.csv",
    "smooth_score_policy_v1_supplementary_tilt_common_oos_returns.csv",
}

PLOT_DATE_SOURCES = {
    "smooth_score_policy_v1_common_oos_buy_hold_gd.png": "data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_equity_curves.csv",
    "smooth_score_policy_v1_common_oos_equity_curves_all.png": "data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_equity_curves.csv",
    "smooth_score_policy_v1_nested_walk_forward_equity_curves.png": "data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_nested_walk_forward_equity_curves.csv",
    "smooth_score_policy_v1_post_2022_validation_equity_curves.png": "data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_post_2022_validation_equity_curves.csv",
    "smooth_score_policy_v1_supplementary_best_local_equity_curves.png": "data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_supplementary_tilt_common_oos_equity_curves.csv",
    "smooth_score_policy_v1_supplementary_extreme_tilt_equity_curves.png": "data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_supplementary_tilt_common_oos_equity_curves.csv",
    "smooth_score_policy_v1_vol_matched_static_equity_curves.png": "data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_vol_matched_static_equity_curves.csv",
}

TABLE_DATE_SOURCE_OVERRIDES = {
    "phase1_2016_full_archive_lineage.csv": None,
    "phase1_2016_full_artifact_date_ranges.csv": None,
    "state_framework_v2_definitions.csv": None,
    "state_framework_v2_forward_summary.csv": "data/phase1/state_framework_v2/inputs/phase1_state_framework_v2_panel.csv",
    "state_framework_v2_triplet_summary.csv": "data/phase1/state_framework_v2/inputs/phase1_state_framework_v2_panel.csv",
    "smooth_score_policy_v1_config_grid.csv": None,
    "smooth_score_policy_v1_supplementary_tilt_config_grid.csv": None,
    "smooth_score_policy_v1_common_oos_score_diagnostics.csv": "data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_equity_curves.csv",
    "smooth_score_policy_v1_score_diagnostics.csv": "data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_equity_curves.csv",
}


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


def parse_date_series(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce").dropna()


def date_range_from_csv(path: Path) -> tuple[str, str, str, str]:
    """Infer an artifact's calendar date range from its date columns."""
    df = pd.read_csv(path, encoding="utf-8-sig")
    if df.empty:
        return "N/A", "N/A", "empty_table", "表格为空，无法推断时间范围。"

    if "date" in df.columns:
        dates = parse_date_series(df["date"])
        if not dates.empty:
            return str(dates.min().date()), str(dates.max().date()), "date", ""

    paired_candidates = [
        ("start_date", "end_date"),
        ("first_return_date", "last_return_date"),
        ("test_start", "test_end"),
        ("train_start", "train_end"),
        ("calibration_start", "calibration_end"),
    ]
    for start_col, end_col in paired_candidates:
        if start_col in df.columns and end_col in df.columns:
            starts = parse_date_series(df[start_col])
            ends = parse_date_series(df[end_col])
            if not starts.empty and not ends.empty:
                return str(starts.min().date()), str(ends.max().date()), f"{start_col}/{end_col}", ""

    date_like_cols = [c for c in df.columns if "date" in c.lower() or c.lower().endswith("_start") or c.lower().endswith("_end")]
    dates: list[pd.Timestamp] = []
    for col in date_like_cols:
        parsed = parse_date_series(df[col])
        if not parsed.empty:
            dates.extend(parsed.tolist())
    if dates:
        return str(min(dates).date()), str(max(dates).date()), "all_date_like_columns", ""

    return "N/A", "N/A", "not_time_series", "配置、定义或链路表，不包含逐日观测。"


def infer_artifact_date_range(path: Path) -> tuple[str, str, str, str]:
    override = TABLE_DATE_SOURCE_OVERRIDES.get(path.name, "__NO_OVERRIDE__")
    if override is None:
        return "N/A", "N/A", "not_time_series", "配置、定义或链路表，不包含逐日观测。"
    if override != "__NO_OVERRIDE__":
        source = ROOT / override
        if source.exists():
            start, end, source_col, note = date_range_from_csv(source)
            return start, end, f"source:{override}::{source_col}", note
        return "N/A", "N/A", f"missing_source:{override}", "指定的时间范围来源文件不存在。"
    return date_range_from_csv(path)


def write_artifact_date_ranges_table() -> Path:
    rows: list[dict[str, str]] = []
    phase1_dir = ROOT / "data" / "phase1"
    for module in ARCHIVE_MODULES:
        module_dir = phase1_dir / module
        if not module_dir.exists():
            continue
        for path in sorted(module_dir.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".csv", ".png"}:
                continue
            if path.name in PACKAGE_EXCLUDED_GENERATED:
                continue
            if path.name == "phase1_2016_full_artifact_date_ranges.csv":
                continue
            rel_path = path.relative_to(ROOT)
            artifact_type = "figure" if path.suffix.lower() == ".png" else "table"
            if artifact_type == "figure":
                source_rel = PLOT_DATE_SOURCES.get(path.name)
                if source_rel and (ROOT / source_rel).exists():
                    start, end, source_col, note = date_range_from_csv(ROOT / source_rel)
                    date_source = f"source:{source_rel}::{source_col}"
                else:
                    start, end, date_source, note = "N/A", "N/A", "missing_plot_source", "未找到该图对应的资金曲线表。"
            else:
                start, end, date_source, note = infer_artifact_date_range(path)

            rows.append(
                {
                    "module": module,
                    "artifact_type": artifact_type,
                    "artifact_name": path.name,
                    "path": str(rel_path),
                    "start_date": start,
                    "end_date": end,
                    "date_source": date_source,
                    "notes": note,
                }
            )

    path = TABLE_DIR / "phase1_2016_full_artifact_date_ranges.csv"
    rows.append(
        {
            "module": "archive_2016_full",
            "artifact_type": "table",
            "artifact_name": path.name,
            "path": str(path.relative_to(ROOT)),
            "start_date": "N/A",
            "end_date": "N/A",
            "date_source": "not_time_series",
            "notes": "本表是 artifact 时间范围索引，单行样本日期不适用。",
        }
    )
    pd.DataFrame(rows).sort_values(["module", "artifact_type", "path"]).to_csv(path, index=False, encoding="utf-8-sig")
    return path


def build_report() -> Path:
    ensure_dirs()
    lineage_path = write_lineage_table()
    artifact_ranges_path = write_artifact_date_ranges_table()

    smooth = pd.read_csv(SMOOTH_SELECTED, encoding="utf-8-sig")
    smooth_rows = smooth[["display_name", "start_date", "end_date", "n_days", "final_wealth", "cagr", "ann_vol", "sharpe", "max_drawdown", "annual_turnover", "avg_g_weight"]]
    artifact_ranges = pd.read_csv(artifact_ranges_path, encoding="utf-8-sig", keep_default_na=False)

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
    lines.append("## 4. 表格与图像时间范围索引")
    lines.append("")
    lines.append(f"完整索引已输出到：`{artifact_ranges_path.relative_to(ROOT)}`")
    lines.append("")
    lines.append("下面列出本归档中所有保留的实验数据表和资金曲线图的起止日期。`N/A` 表示该文件是配置、定义、链路或索引文件，本身不包含逐日观测。")
    lines.append("")
    lines.append("| module | type | artifact | start_date | end_date | date_source |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for row in artifact_ranges.to_dict("records"):
        lines.append(
            f"| {row['module']} | {row['artifact_type']} | `{row['path']}` | "
            f"{row['start_date']} | {row['end_date']} | `{row['date_source']}` |"
        )
    lines.append("")
    lines.append("## 5. 合并报告正文")
    lines.append("")
    lines.append("### 5.1 因子归因模块")
    lines.append("")
    lines.append(demote_markdown(read_text(FACTOR_REPORT), levels=3))
    lines.append("")
    lines.append("### 5.2 Smooth Continuous Score Policy v1")
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

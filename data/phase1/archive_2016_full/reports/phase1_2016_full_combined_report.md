# Phase 1 2016 Full Archive Combined Report

## 0. 归档口径

本归档版本按最新要求重新整理，保留以下主线与后续稳健性扩展：

1. 因子归因：检验 G、D、G-D 的 FF5+MOM 风险暴露。
2. Smooth Continuous Score Policy v1：保留该报告中的全部步骤，包括主网格、buy-and-hold、vol-matched、supplementary tilt、expanded local grid、walk-forward、fixed holdout、资金曲线和年度表现。
3. Bond/Credit 增量扩展：包含信用变量诊断门槛、替代式 bond/credit score、旧版 Best Local + credit overlay 的严格增量测试。
4. Joint Old/Credit 与 Start-Date Sensitivity：包含联合选择旧版 smooth-score 与 bond/credit 参数，以及 rolling / expanding 起点敏感性测试。

不纳入旧的 state sorting / predictive regression / oos_validation / state-action 中途路线；不纳入 ElasticNet。

## 1. 数据起点与自然 warmup

- G/D 源收益共同起点：`2016-12-21`。
- 因子归因回归样本：`2016-12-21` 到 `2026-03-31`。
- Smooth score 主比较从 G/D 最早共同可用日期 `2016-12-21` 开始。
- Smooth score 中的 `gd_trailing_126d` 必须使用 126 个交易日 warmup，因此完整 smooth score 动态策略的实际交易起点自然晚于 2016-12-21。这个 warmup 被保留并解释，不视为中途截样。
- Bond/Credit 与 Joint Old/Credit 主比较从 `2017-06-28` 开始，结束于 `2026-05-15`。
- Rolling / Expanding Start-Date Sensitivity 的共同窗口为 `2022-01-03` 到 `2026-05-15`。

## 2. 研究链路

链路表已输出到：`data/phase1/archive_2016_full/tables/phase1_2016_full_archive_lineage.csv`

| step | archive_status | sample_note |
| --- | --- | --- |
| 1_factor_attribution | included | FF5+MOM 回归样本从 2016-12-21 开始。 |
| 2_smooth_score_policy_v1 | included | G/D 源收益从 2016-12-21 开始；包含 126 日 trailing warmup 后的完整 smooth score 结果。 |
| 3_bond_credit_augmented_v1 | included | 加入 AAA/BAA spread 与债券/信用代理变量的诊断门槛测试。 |
| 4_bond_credit_smooth_policy_v1 | included | 包含替代式 bond/credit score 与旧版 Best Local + credit overlay 的严格增量测试。 |
| 5_joint_old_credit_policy_v1 | included | 联合选择旧版 smooth-score 参数与 bond/credit 增量参数。 |
| 6_rolling_start_date_sensitivity_v1 | included | Joint Old/Credit rolling 的 Start-Date Sensitivity；固定 full-grid，只改变 OOS 起点和 63 日 block phase。 |
| 7_expanding_start_date_sensitivity_v1 | included | Joint Old/Credit expanding 的 Start-Date Sensitivity；固定 full-grid，只改变 OOS 起点和 63 日 block phase。 |
| excluded_old_exploratory_routes | excluded | 这些属于旧路线或中途实验结果，本归档按用户要求不纳入。 |
| excluded_elasticnet | excluded | ElasticNet 相关实验、表格与结论全部排除。 |

## 3. Smooth Policy 入选方法概览

| display_name | start_date | end_date | n_days | final_wealth | CAGR | Ann Vol | Sharpe | Max DD | Turnover | Avg G |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Best Local Grid (tilt 50%) | 2017-06-28 | 2026-05-15 | 2233 | 4.71 | 19.24% | 19.29% | 1.01 | -31.63% | 469.67% | 45.06% |
| Matched TNX-only (tilt 50%) | 2017-06-28 | 2026-05-15 | 2233 | 4.23 | 17.80% | 19.33% | 0.94 | -31.31% | 566.69% | 47.48% |
| Matched Core-only (tilt 50%) | 2017-06-28 | 2026-05-15 | 2233 | 4.25 | 17.84% | 18.94% | 0.96 | -31.98% | 410.19% | 37.18% |
| Extreme 50% Tilt | 2017-06-28 | 2026-05-15 | 2233 | 4.64 | 19.02% | 19.45% | 0.99 | -31.72% | 465.87% | 46.92% |
| 50/50 G-D Buy & Hold | 2017-06-28 | 2026-05-15 | 2233 | 4.02 | 17.12% | 19.34% | 0.91 | -33.59% | 0.00% | 50.00% |
| 100% G Buy & Hold | 2017-06-28 | 2026-05-15 | 2233 | 5.49 | 21.34% | 23.53% | 0.94 | -34.35% | 0.00% | 100.00% |
| 100% D Buy & Hold | 2017-06-28 | 2026-05-15 | 2233 | 2.80 | 12.42% | 17.53% | 0.76 | -36.71% | 0.00% | 0.00% |
| SPY Buy & Hold | 2017-06-28 | 2026-05-15 | 2233 | 3.49 | 15.25% | 18.74% | 0.85 | -33.72% | 0.00% |  |

## 4. 表格与图像时间范围索引

完整索引已输出到：`data/phase1/archive_2016_full/tables/phase1_2016_full_artifact_date_ranges.csv`

下面列出本归档中所有保留的实验数据表和资金曲线图的起止日期。`N/A` 表示该文件是配置、定义、链路或索引文件，本身不包含逐日观测。

| module | type | artifact | start_date | end_date | date_source |
| --- | --- | --- | --- | --- | --- |
| archive_2016_full | table | `data/phase1/archive_2016_full/tables/phase1_2016_full_archive_lineage.csv` | N/A | N/A | `not_time_series` |
| archive_2016_full | table | `data/phase1/archive_2016_full/tables/phase1_2016_full_artifact_date_ranges.csv` | N/A | N/A | `not_time_series` |
| bond_credit_augmented_v1 | table | `data/phase1/bond_credit_augmented_v1/inputs/phase1_bond_credit_augmented_v1_panel.csv` | 2006-05-22 | 2026-05-15 | `date` |
| bond_credit_augmented_v1 | table | `data/phase1/bond_credit_augmented_v1/tables/bond_credit_augmented_v1_candidate_interactions.csv` | N/A | N/A | `not_time_series` |
| bond_credit_augmented_v1 | table | `data/phase1/bond_credit_augmented_v1/tables/bond_credit_augmented_v1_coefficients.csv` | 2016-12-20 | 2026-04-16 | `start_date/end_date` |
| bond_credit_augmented_v1 | table | `data/phase1/bond_credit_augmented_v1/tables/bond_credit_augmented_v1_group_summary.csv` | N/A | N/A | `not_time_series` |
| bond_credit_augmented_v1 | table | `data/phase1/bond_credit_augmented_v1/tables/bond_credit_augmented_v1_input_coverage.csv` | 2006-05-22 | 2026-05-15 | `start_date/end_date` |
| bond_credit_augmented_v1 | table | `data/phase1/bond_credit_augmented_v1/tables/bond_credit_augmented_v1_interaction_gate.csv` | N/A | N/A | `not_time_series` |
| bond_credit_augmented_v1 | table | `data/phase1/bond_credit_augmented_v1/tables/bond_credit_augmented_v1_main_effect_gate.csv` | N/A | N/A | `not_time_series` |
| bond_credit_augmented_v1 | table | `data/phase1/bond_credit_augmented_v1/tables/bond_credit_augmented_v1_model_summary.csv` | 2016-12-20 | 2026-04-16 | `start_date/end_date` |
| bond_credit_augmented_v1 | table | `data/phase1/bond_credit_augmented_v1/tables/bond_credit_augmented_v1_raw_interaction_gate.csv` | N/A | N/A | `not_time_series` |
| bond_credit_smooth_policy_v1 | figure | `data/phase1/bond_credit_smooth_policy_v1/plots/bond_credit_smooth_policy_v1_main_equity_curves.png` | 2017-06-28 | 2026-05-15 | `source:data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_main_equity_curves.csv::date` |
| bond_credit_smooth_policy_v1 | figure | `data/phase1/bond_credit_smooth_policy_v1/plots/bond_credit_smooth_policy_v1_oos_validation_equity_curves.png` | 2018-06-28 | 2026-05-15 | `source:data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_oos_validation_equity_curves.csv::date` |
| bond_credit_smooth_policy_v1 | figure | `data/phase1/bond_credit_smooth_policy_v1/plots/bond_credit_smooth_policy_v1_post2022_validation_equity_curves.png` | 2022-01-03 | 2026-05-15 | `source:data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_post2022_validation_equity_curves.csv::date` |
| bond_credit_smooth_policy_v1 | figure | `data/phase1/bond_credit_smooth_policy_v1/plots/bond_credit_smooth_policy_v1_static_comparison_equity_curves.png` | 2017-06-28 | 2026-05-15 | `source:data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_static_comparison_equity_curves.csv::date` |
| bond_credit_smooth_policy_v1 | figure | `data/phase1/bond_credit_smooth_policy_v1/plots/bond_credit_smooth_policy_v1_tilt_equity_curves.png` | 2017-06-27 | 2026-05-15 | `source:data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_tilt_equity_curves.csv::date` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/inputs/bond_credit_smooth_policy_v1_feature_panel.csv` | 2016-12-21 | 2026-05-15 | `date` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_comparisons.csv` | N/A | N/A | `not_time_series` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_config_grid.csv` | N/A | N/A | `not_time_series` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_grid_metrics.csv` | 2017-06-28 | 2026-05-15 | `start_date/end_date` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_main_equity_curves.csv` | 2017-06-28 | 2026-05-15 | `date` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_old_plus_credit_cost_sensitivity.csv` | 2017-06-28 | 2026-05-15 | `start_date/end_date` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_oos_validation_equity_curves.csv` | 2018-06-28 | 2026-05-15 | `date` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_oos_validation_returns.csv` | 2018-06-28 | 2026-05-15 | `date` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_oos_validation_selections.csv` | 2018-06-28 | 2026-05-15 | `test_start/test_end` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_oos_validation_summary.csv` | 2018-06-28 | 2026-05-15 | `start_date/end_date` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_post2022_validation_equity_curves.csv` | 2022-01-03 | 2026-05-15 | `date` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_post2022_validation_returns.csv` | 2022-01-03 | 2026-05-15 | `date` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_post2022_validation_selections.csv` | 2022-01-03 | 2026-05-15 | `test_start/test_end` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_post2022_validation_summary.csv` | 2022-01-03 | 2026-05-15 | `start_date/end_date` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_score_diagnostics.csv` | 2017-06-28 | 2026-02-13 | `start_date/end_date` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_selected_cost_sensitivity.csv` | 2017-06-28 | 2026-05-15 | `start_date/end_date` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_selected_daily_returns.csv` | 2016-12-21 | 2026-05-15 | `date` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_selected_summary.csv` | 2017-06-28 | 2026-05-15 | `start_date/end_date` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_static_comparison.csv` | N/A | N/A | `not_time_series` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_static_comparison_equity_curves.csv` | 2017-06-28 | 2026-05-15 | `date` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_tilt_equity_curves.csv` | 2017-06-27 | 2026-05-15 | `date` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_tilt_summary.csv` | 2017-06-28 | 2026-05-15 | `start_date/end_date` |
| bond_credit_smooth_policy_v1 | table | `data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_yearly_metrics.csv` | 2017-06-28 | 2026-05-15 | `start_date/end_date` |
| expanding_start_date_sensitivity_v1 | figure | `data/phase1/expanding_start_date_sensitivity_v1/plots/expanding_start_date_cagr_sharpe_bar.png` | 2018-06-28 | 2026-05-15 | `source:data/phase1/expanding_start_date_sensitivity_v1/tables/expanding_start_date_sensitivity_v1_start_to_end_summary.csv::start_date/end_date` |
| expanding_start_date_sensitivity_v1 | figure | `data/phase1/expanding_start_date_sensitivity_v1/plots/expanding_start_date_equity_curves.png` | 2022-01-03 | 2026-05-15 | `source:data/phase1/expanding_start_date_sensitivity_v1/tables/expanding_start_date_sensitivity_v1_equity_curves.csv::date` |
| expanding_start_date_sensitivity_v1 | figure | `data/phase1/expanding_start_date_sensitivity_v1/plots/expanding_start_date_maxdd_turnover_bar.png` | 2018-06-28 | 2026-05-15 | `source:data/phase1/expanding_start_date_sensitivity_v1/tables/expanding_start_date_sensitivity_v1_start_to_end_summary.csv::start_date/end_date` |
| expanding_start_date_sensitivity_v1 | figure | `data/phase1/expanding_start_date_sensitivity_v1/plots/expanding_start_date_vs_benchmarks_common_window.png` | 2022-01-03 | 2026-05-15 | `source:data/phase1/expanding_start_date_sensitivity_v1/tables/expanding_start_date_sensitivity_v1_common_window_equity_curves.csv::date` |
| expanding_start_date_sensitivity_v1 | table | `data/phase1/expanding_start_date_sensitivity_v1/inputs/expanding_start_date_sensitivity_v1_feature_panel.csv` | 2016-12-21 | 2026-05-15 | `date` |
| expanding_start_date_sensitivity_v1 | table | `data/phase1/expanding_start_date_sensitivity_v1/tables/expanding_start_date_sensitivity_v1_common_window_equity_curves.csv` | 2022-01-03 | 2026-05-15 | `date` |
| expanding_start_date_sensitivity_v1 | table | `data/phase1/expanding_start_date_sensitivity_v1/tables/expanding_start_date_sensitivity_v1_common_window_returns.csv` | 2022-01-03 | 2026-05-15 | `date` |
| expanding_start_date_sensitivity_v1 | table | `data/phase1/expanding_start_date_sensitivity_v1/tables/expanding_start_date_sensitivity_v1_common_window_summary.csv` | 2022-01-03 | 2026-05-15 | `start_date/end_date` |
| expanding_start_date_sensitivity_v1 | table | `data/phase1/expanding_start_date_sensitivity_v1/tables/expanding_start_date_sensitivity_v1_equity_curves.csv` | 2022-01-03 | 2026-05-15 | `date` |
| expanding_start_date_sensitivity_v1 | table | `data/phase1/expanding_start_date_sensitivity_v1/tables/expanding_start_date_sensitivity_v1_fixed_horizon_summary.csv` | 2018-06-28 | 2026-01-08 | `start_date/end_date` |
| expanding_start_date_sensitivity_v1 | table | `data/phase1/expanding_start_date_sensitivity_v1/tables/expanding_start_date_sensitivity_v1_returns.csv` | 2018-06-28 | 2026-05-15 | `date` |
| expanding_start_date_sensitivity_v1 | table | `data/phase1/expanding_start_date_sensitivity_v1/tables/expanding_start_date_sensitivity_v1_selection_stability.csv` | 2017-06-28 | 2022-01-03 | `all_date_like_columns` |
| expanding_start_date_sensitivity_v1 | table | `data/phase1/expanding_start_date_sensitivity_v1/tables/expanding_start_date_sensitivity_v1_selections.csv` | 2018-06-28 | 2026-05-15 | `test_start/test_end` |
| expanding_start_date_sensitivity_v1 | table | `data/phase1/expanding_start_date_sensitivity_v1/tables/expanding_start_date_sensitivity_v1_start_to_end_summary.csv` | 2018-06-28 | 2026-05-15 | `start_date/end_date` |
| expanding_start_date_sensitivity_v1 | table | `data/phase1/expanding_start_date_sensitivity_v1/tables/expanding_start_date_sensitivity_v1_start_to_end_with_benchmarks.csv` | 2018-06-28 | 2026-05-15 | `start_date/end_date` |
| factor_attribution | table | `data/phase1/factor_attribution/inputs/phase1_factor_returns_panel.csv` | 2016-12-21 | 2026-03-31 | `date` |
| factor_attribution | table | `data/phase1/factor_attribution/tables/factor_attribution_data_coverage.csv` | 2006-05-23 | 2026-03-31 | `first_return_date/last_return_date` |
| factor_attribution | table | `data/phase1/factor_attribution/tables/factor_attribution_etfs_full_sample.csv` | 2006-05-23 | 2026-03-31 | `start_date/end_date` |
| factor_attribution | table | `data/phase1/factor_attribution/tables/factor_attribution_factor_adjusted_returns.csv` | 2016-12-21 | 2026-03-31 | `date` |
| factor_attribution | table | `data/phase1/factor_attribution/tables/factor_attribution_portfolios_full_sample.csv` | 2016-12-21 | 2026-03-31 | `start_date/end_date` |
| factor_attribution | table | `data/phase1/factor_attribution/tables/factor_attribution_rolling_betas.csv` | 2017-12-20 | 2026-03-31 | `date` |
| factor_attribution | table | `data/phase1/factor_attribution/tables/factor_attribution_rolling_period_summary.csv` | 2020-03-23 | 2026-03-31 | `start_date/end_date` |
| joint_old_credit_policy_v1 | figure | `data/phase1/joint_old_credit_policy_v1/plots/joint_old_credit_policy_v1_local_equity_curves.png` | 2017-06-28 | 2026-05-15 | `source:data/phase1/joint_old_credit_policy_v1/tables/joint_old_credit_policy_v1_local_equity_curves.csv::date` |
| joint_old_credit_policy_v1 | figure | `data/phase1/joint_old_credit_policy_v1/plots/joint_old_credit_policy_v1_oos_equity_curves.png` | 2018-06-28 | 2026-05-15 | `source:data/phase1/joint_old_credit_policy_v1/tables/joint_old_credit_policy_v1_oos_equity_curves.csv::date` |
| joint_old_credit_policy_v1 | table | `data/phase1/joint_old_credit_policy_v1/inputs/joint_old_credit_policy_v1_feature_panel.csv` | 2016-12-21 | 2026-05-15 | `date` |
| joint_old_credit_policy_v1 | table | `data/phase1/joint_old_credit_policy_v1/tables/joint_old_credit_policy_v1_comparisons.csv` | N/A | N/A | `not_time_series` |
| joint_old_credit_policy_v1 | table | `data/phase1/joint_old_credit_policy_v1/tables/joint_old_credit_policy_v1_config_grid.csv` | N/A | N/A | `not_time_series` |
| joint_old_credit_policy_v1 | table | `data/phase1/joint_old_credit_policy_v1/tables/joint_old_credit_policy_v1_grid_metrics.csv` | 2017-06-28 | 2026-05-15 | `start_date/end_date` |
| joint_old_credit_policy_v1 | table | `data/phase1/joint_old_credit_policy_v1/tables/joint_old_credit_policy_v1_local_equity_curves.csv` | 2017-06-28 | 2026-05-15 | `date` |
| joint_old_credit_policy_v1 | table | `data/phase1/joint_old_credit_policy_v1/tables/joint_old_credit_policy_v1_local_returns.csv` | 2016-12-21 | 2026-05-15 | `date` |
| joint_old_credit_policy_v1 | table | `data/phase1/joint_old_credit_policy_v1/tables/joint_old_credit_policy_v1_local_summary.csv` | 2017-06-28 | 2026-05-15 | `start_date/end_date` |
| joint_old_credit_policy_v1 | table | `data/phase1/joint_old_credit_policy_v1/tables/joint_old_credit_policy_v1_oos_comparisons.csv` | N/A | N/A | `not_time_series` |
| joint_old_credit_policy_v1 | table | `data/phase1/joint_old_credit_policy_v1/tables/joint_old_credit_policy_v1_oos_equity_curves.csv` | 2018-06-28 | 2026-05-15 | `date` |
| joint_old_credit_policy_v1 | table | `data/phase1/joint_old_credit_policy_v1/tables/joint_old_credit_policy_v1_oos_returns.csv` | 2016-12-21 | 2026-05-15 | `date` |
| joint_old_credit_policy_v1 | table | `data/phase1/joint_old_credit_policy_v1/tables/joint_old_credit_policy_v1_oos_selections.csv` | 2018-06-28 | 2026-05-15 | `test_start/test_end` |
| joint_old_credit_policy_v1 | table | `data/phase1/joint_old_credit_policy_v1/tables/joint_old_credit_policy_v1_oos_summary.csv` | 2018-06-28 | 2026-05-15 | `start_date/end_date` |
| rolling_start_date_sensitivity_v1 | figure | `data/phase1/rolling_start_date_sensitivity_v1/plots/rolling_start_date_cagr_sharpe_bar.png` | 2018-06-28 | 2026-05-15 | `source:data/phase1/rolling_start_date_sensitivity_v1/tables/rolling_start_date_sensitivity_v1_joint_start_to_end_summary.csv::start_date/end_date` |
| rolling_start_date_sensitivity_v1 | figure | `data/phase1/rolling_start_date_sensitivity_v1/plots/rolling_start_date_equity_curves.png` | 2022-01-03 | 2026-05-15 | `source:data/phase1/rolling_start_date_sensitivity_v1/tables/rolling_start_date_sensitivity_v1_equity_curves.csv::date` |
| rolling_start_date_sensitivity_v1 | figure | `data/phase1/rolling_start_date_sensitivity_v1/plots/rolling_start_date_maxdd_turnover_bar.png` | 2018-06-28 | 2026-05-15 | `source:data/phase1/rolling_start_date_sensitivity_v1/tables/rolling_start_date_sensitivity_v1_joint_start_to_end_summary.csv::start_date/end_date` |
| rolling_start_date_sensitivity_v1 | figure | `data/phase1/rolling_start_date_sensitivity_v1/plots/rolling_start_date_vs_benchmarks_common_window.png` | 2022-01-03 | 2026-05-15 | `source:data/phase1/rolling_start_date_sensitivity_v1/tables/rolling_start_date_sensitivity_v1_common_window_equity_curves.csv::date` |
| rolling_start_date_sensitivity_v1 | table | `data/phase1/rolling_start_date_sensitivity_v1/inputs/rolling_start_date_sensitivity_v1_feature_panel.csv` | 2016-12-21 | 2026-05-15 | `date` |
| rolling_start_date_sensitivity_v1 | table | `data/phase1/rolling_start_date_sensitivity_v1/tables/rolling_start_date_sensitivity_v1_common_window_equity_curves.csv` | 2022-01-03 | 2026-05-15 | `date` |
| rolling_start_date_sensitivity_v1 | table | `data/phase1/rolling_start_date_sensitivity_v1/tables/rolling_start_date_sensitivity_v1_common_window_returns.csv` | 2022-01-03 | 2026-05-15 | `date` |
| rolling_start_date_sensitivity_v1 | table | `data/phase1/rolling_start_date_sensitivity_v1/tables/rolling_start_date_sensitivity_v1_common_window_summary.csv` | 2022-01-03 | 2026-05-15 | `start_date/end_date` |
| rolling_start_date_sensitivity_v1 | table | `data/phase1/rolling_start_date_sensitivity_v1/tables/rolling_start_date_sensitivity_v1_config_grid.csv` | N/A | N/A | `not_time_series` |
| rolling_start_date_sensitivity_v1 | table | `data/phase1/rolling_start_date_sensitivity_v1/tables/rolling_start_date_sensitivity_v1_daily_returns.csv` | 2018-06-28 | 2026-05-15 | `date` |
| rolling_start_date_sensitivity_v1 | table | `data/phase1/rolling_start_date_sensitivity_v1/tables/rolling_start_date_sensitivity_v1_equity_curves.csv` | 2022-01-03 | 2026-05-15 | `date` |
| rolling_start_date_sensitivity_v1 | table | `data/phase1/rolling_start_date_sensitivity_v1/tables/rolling_start_date_sensitivity_v1_fixed_horizon_summary.csv` | 2018-06-28 | 2026-01-08 | `start_date/end_date` |
| rolling_start_date_sensitivity_v1 | table | `data/phase1/rolling_start_date_sensitivity_v1/tables/rolling_start_date_sensitivity_v1_joint_start_to_end_summary.csv` | 2018-06-28 | 2026-05-15 | `start_date/end_date` |
| rolling_start_date_sensitivity_v1 | table | `data/phase1/rolling_start_date_sensitivity_v1/tables/rolling_start_date_sensitivity_v1_selection_stability.csv` | 2017-06-28 | 2022-01-03 | `all_date_like_columns` |
| rolling_start_date_sensitivity_v1 | table | `data/phase1/rolling_start_date_sensitivity_v1/tables/rolling_start_date_sensitivity_v1_selections.csv` | 2018-06-28 | 2026-05-15 | `test_start/test_end` |
| rolling_start_date_sensitivity_v1 | table | `data/phase1/rolling_start_date_sensitivity_v1/tables/rolling_start_date_sensitivity_v1_start_to_end_summary.csv` | 2018-06-28 | 2026-05-15 | `start_date/end_date` |
| smooth_score_policy_v1 | figure | `data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_common_oos_buy_hold_gd.png` | 2017-06-28 | 2026-05-15 | `source:data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_equity_curves.csv::date` |
| smooth_score_policy_v1 | figure | `data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_common_oos_equity_curves_all.png` | 2017-06-28 | 2026-05-15 | `source:data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_equity_curves.csv::date` |
| smooth_score_policy_v1 | figure | `data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_nested_walk_forward_equity_curves.png` | 2018-06-28 | 2026-05-15 | `source:data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_nested_walk_forward_equity_curves.csv::date` |
| smooth_score_policy_v1 | figure | `data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_post_2022_validation_equity_curves.png` | 2022-01-03 | 2026-05-15 | `source:data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_post_2022_validation_equity_curves.csv::date` |
| smooth_score_policy_v1 | figure | `data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_supplementary_best_local_equity_curves.png` | 2017-06-28 | 2026-05-15 | `source:data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_supplementary_tilt_common_oos_equity_curves.csv::date` |
| smooth_score_policy_v1 | figure | `data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_supplementary_extreme_tilt_equity_curves.png` | 2017-06-28 | 2026-05-15 | `source:data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_supplementary_tilt_common_oos_equity_curves.csv::date` |
| smooth_score_policy_v1 | figure | `data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_vol_matched_static_equity_curves.png` | 2017-06-28 | 2026-05-15 | `source:data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_vol_matched_static_equity_curves.csv::date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/inputs/smooth_score_policy_v1_feature_panel.csv` | 2006-05-22 | 2026-05-15 | `date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_comparisons.csv` | 2017-06-28 | 2026-05-15 | `start_date/end_date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_equity_curves.csv` | 2017-06-28 | 2026-05-15 | `date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_metrics.csv` | 2016-12-21 | 2026-05-15 | `start_date/end_date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_score_diagnostics.csv` | 2017-06-28 | 2026-05-15 | `source:data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_equity_curves.csv::date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_selected_summary.csv` | 2017-06-28 | 2026-05-15 | `start_date/end_date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_yearly_metrics.csv` | 2017-06-28 | 2026-05-15 | `start_date/end_date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_comparisons.csv` | 2017-06-28 | 2026-05-15 | `start_date/end_date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_config_grid.csv` | N/A | N/A | `not_time_series` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_fixed_parameter_holdout_returns.csv` | 2018-06-28 | 2026-05-15 | `date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_fixed_parameter_holdout_summary.csv` | 2018-06-28 | 2026-05-15 | `start_date/end_date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_metrics.csv` | 2006-05-23 | 2026-05-15 | `start_date/end_date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_nested_walk_forward_equity_curves.csv` | 2018-06-28 | 2026-05-15 | `date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_nested_walk_forward_returns.csv` | 2018-06-28 | 2026-05-15 | `date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_nested_walk_forward_selections.csv` | 2018-06-28 | 2026-05-15 | `test_start/test_end` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_nested_walk_forward_summary.csv` | 2018-06-28 | 2026-05-15 | `start_date/end_date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_post_2022_fixed_parameter_holdout_returns.csv` | 2022-01-03 | 2026-05-15 | `date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_post_2022_fixed_parameter_holdout_summary.csv` | 2022-01-03 | 2026-05-15 | `start_date/end_date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_post_2022_nested_walk_forward_returns.csv` | 2022-01-03 | 2026-05-15 | `date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_post_2022_nested_walk_forward_selections.csv` | 2022-01-03 | 2026-05-15 | `test_start/test_end` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_post_2022_validation_equity_curves.csv` | 2022-01-03 | 2026-05-15 | `date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_post_2022_validation_summary.csv` | 2022-01-03 | 2026-05-15 | `start_date/end_date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_score_diagnostics.csv` | 2017-06-28 | 2026-05-15 | `source:data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_equity_curves.csv::date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_static_gd_grid.csv` | 2017-06-28 | 2026-05-15 | `start_date/end_date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_supplementary_tilt_common_oos_equity_curves.csv` | 2017-06-28 | 2026-05-15 | `date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_supplementary_tilt_common_oos_summary.csv` | 2017-06-28 | 2026-05-15 | `start_date/end_date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_supplementary_tilt_config_grid.csv` | N/A | N/A | `not_time_series` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_vol_matched_static_comparison.csv` | 2017-06-28 | 2026-05-15 | `start_date/end_date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_vol_matched_static_equity_curves.csv` | 2017-06-28 | 2026-05-15 | `date` |
| smooth_score_policy_v1 | table | `data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_yearly_metrics.csv` | 2017-06-28 | 2026-05-15 | `start_date/end_date` |
| state_framework_v2 | table | `data/phase1/state_framework_v2/inputs/phase1_state_framework_v2_panel.csv` | 2006-05-22 | 2026-05-15 | `date` |
| state_framework_v2 | table | `data/phase1/state_framework_v2/tables/state_framework_v2_coverage.csv` | 2016-12-21 | 2026-05-15 | `start_date/end_date` |
| state_framework_v2 | table | `data/phase1/state_framework_v2/tables/state_framework_v2_definitions.csv` | N/A | N/A | `not_time_series` |
| state_framework_v2 | table | `data/phase1/state_framework_v2/tables/state_framework_v2_forward_summary.csv` | 2006-05-22 | 2026-05-15 | `source:data/phase1/state_framework_v2/inputs/phase1_state_framework_v2_panel.csv::date` |
| state_framework_v2 | table | `data/phase1/state_framework_v2/tables/state_framework_v2_triplet_summary.csv` | 2006-05-22 | 2026-05-15 | `source:data/phase1/state_framework_v2/inputs/phase1_state_framework_v2_panel.csv::date` |

## 5. 合并报告正文

### 5.1 因子归因模块

#### 第一阶段收益归因模块报告

##### 1. 本模块回答的问题

这个模块先回答：成长/科技篮子 G、防御收益篮子 D、以及 G-D 多空组合，到底分别是什么风险暴露。只有先把 MKT、SMB、HML、RMW、CMA、MOM 这些已知因子解释清楚，后面才能讨论市场状态是否真的能预测 G 相对 D 的未来收益。

##### 2. 数据与口径

- G 篮子：`QQQ, XLK, VGT, SPYG, VUG`，固定等权。
- D 篮子：`SCHD, VYM, VTV, FDVV, COWZ`，固定等权。
- ETF 收益：Moomoo 日线 QFQ close 计算日收益；对单 ETF 的孤立数据缺口，先在价格层做最多 3 个交易日的 forward-fill，再计算收益，长缺口和上市前缺口不填补。
- 因子：Kenneth French FF5 daily + Momentum，使用 decimal return。
- G 和 D 使用超额收益 `R - Rf`；G-D 是零成本多空组合，risk-free leg 相互抵消，因此用 `R_G - R_D`。
- 回归样本：`2016-12-21` 到 `2026-03-31`。

###### 2.1 ETF 数据覆盖

| symbol | first_return_date | last_return_date | n_returns |
| --- | --- | --- | --- |
| QQQ | 2006-05-23 | 2026-03-31 | 4995 |
| XLK | 2012-01-04 | 2026-03-31 | 3580 |
| VGT | 2012-01-04 | 2026-03-31 | 3580 |
| SPYG | 2012-01-04 | 2026-03-31 | 3580 |
| VUG | 2012-01-04 | 2026-03-31 | 3580 |
| SCHD | 2012-01-04 | 2026-03-31 | 3580 |
| VYM | 2012-01-04 | 2026-03-31 | 3580 |
| VTV | 2012-01-04 | 2026-03-31 | 3580 |
| FDVV | 2016-09-16 | 2026-03-31 | 2397 |
| COWZ | 2016-12-21 | 2026-03-31 | 2330 |

##### 3. G、D、G-D 全样本 FF5+MOM 回归

| portfolio | n | alpha ann. | alpha t(NW) | MKT | HML | RMW | CMA | MOM | adj R2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| G | 2330 | 2.24% | 1.51 | 1.148 | -0.298 | 0.067 | -0.071 | 0.041 | 0.965 |
| D | 2330 | 0.29% | 0.24 | 0.874 | 0.254 | 0.088 | 0.227 | -0.076 | 0.950 |
| G-D | 2330 | 1.95% | 0.81 | 0.273 | -0.552 | -0.021 | -0.298 | 0.117 | 0.757 |

完整表格含普通 t 值和 Newey-West t 值，见 `tables/factor_attribution_portfolios_full_sample.csv`。

###### 3.1 G-D 初步解释

- G-D 的市场 beta 为 `0.273`，Newey-West t 值 `11.24`。 这说明多成长/科技、空防御收益组合明显偏高市场 beta。
- HML beta 为 `-0.552`，Newey-West t 值 `-20.01`。 负 HML 表明它本质上是多成长、空价值/红利的一部分。
- MOM beta 为 `0.117`，Newey-West t 值 `8.80`。 这说明 G-D 和动量行情有明显同向关系，后续预测实验必须控制 MOM。
- RMW beta `-0.021`、CMA beta `-0.298`，分别对应盈利能力和投资风格暴露。
- G-D 年化 alpha 为 `1.95%`，alpha 的 Newey-West t 值 `0.81`。 这更像可解释的风格/因子组合，而不是已经证明的新 alpha。

##### 4. 单 ETF 因子暴露

这张表用于检查篮子内部是否一致，以及后续是否需要重设权重或剔除风格不纯的 ETF。

| ETF | group | n | alpha ann. | alpha t(NW) | MKT | HML | RMW | CMA | MOM | adj R2 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QQQ | G | 4995 | 3.57% | 2.76 | 1.078 | -0.312 | 0.014 | -0.216 | 0.039 | 0.924 |
| XLK | G | 3580 | 1.86% | 1.06 | 1.193 | -0.316 | 0.133 | -0.048 | 0.051 | 0.907 |
| VGT | G | 3580 | 2.77% | 1.61 | 1.190 | -0.329 | 0.060 | -0.118 | 0.050 | 0.916 |
| SPYG | G | 3580 | 0.03% | 0.04 | 1.056 | -0.213 | 0.086 | -0.077 | 0.037 | 0.967 |
| VUG | G | 3580 | 0.28% | 0.37 | 1.076 | -0.265 | 0.029 | -0.146 | 0.006 | 0.977 |
| SCHD | D | 3580 | 0.02% | 0.02 | 0.848 | 0.183 | 0.233 | 0.271 | -0.081 | 0.875 |
| VYM | D | 3580 | -0.88% | -0.87 | 0.862 | 0.259 | 0.081 | 0.238 | -0.033 | 0.927 |
| VTV | D | 3580 | -0.73% | -0.77 | 0.887 | 0.304 | 0.034 | 0.185 | -0.037 | 0.943 |
| FDVV | D | 2397 | -0.25% | -0.18 | 0.883 | 0.229 | 0.048 | 0.182 | -0.068 | 0.932 |
| COWZ | D | 2330 | 1.48% | 0.71 | 0.934 | 0.223 | 0.150 | 0.224 | -0.112 | 0.880 |

完整单 ETF 表格见 `tables/factor_attribution_etfs_full_sample.csv`。

##### 5. 滚动 beta 输出

已生成 252 日和 504 日滚动 alpha/beta。最近一期结果如下：

| portfolio | window | date | alpha ann. | MKT | SMB | HML | RMW | CMA | MOM | R2 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| G | 252 | 2026-03-31 | 3.52% | 1.189 | -0.111 | -0.226 | -0.069 | -0.146 | 0.049 | 0.971 |
| G | 504 | 2026-03-31 | 0.79% | 1.201 | -0.110 | -0.340 | -0.004 | 0.056 | 0.118 | 0.962 |
| G-D | 252 | 2026-03-31 | 4.21% | 0.399 | -0.140 | -0.507 | -0.092 | -0.420 | 0.139 | 0.780 |
| D | 252 | 2026-03-31 | -0.67% | 0.790 | 0.029 | 0.281 | 0.023 | 0.274 | -0.089 | 0.924 |
| D | 504 | 2026-03-31 | 0.42% | 0.783 | 0.056 | 0.330 | 0.047 | 0.155 | -0.150 | 0.900 |
| G-D | 504 | 2026-03-31 | 0.37% | 0.419 | -0.166 | -0.670 | -0.051 | -0.100 | 0.268 | 0.787 |

滚动 beta 文件：`tables/factor_attribution_rolling_betas.csv`。

###### 5.1 G-D 按阶段滚动暴露摘要

| period | avg alpha ann. | avg MKT | avg SMB | avg HML | avg RMW | avg CMA | avg MOM | avg R2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| covid_rebound_2020_2021 | 7.06% | 0.207 | -0.166 | -0.522 | 0.155 | -0.314 | 0.100 | 0.812 |
| rate_hike_2022 | 3.77% | 0.267 | -0.252 | -0.640 | -0.013 | -0.122 | 0.113 | 0.856 |
| ai_rally_2023_2024 | -2.21% | 0.275 | -0.188 | -0.542 | 0.073 | -0.486 | 0.105 | 0.809 |
| recent_2025_2026q1 | 2.61% | 0.398 | -0.103 | -0.682 | -0.022 | -0.021 | 0.306 | 0.794 |

完整阶段汇总文件：`tables/factor_attribution_rolling_period_summary.csv`。

##### 6. 第一阶段下一步怎么接

1. 如果 G-D 的 MKT/HML/MOM 显著，而 alpha 不显著，后续研究应写成“状态依赖的风格因子动态配置”，不是新 alpha。
2. 如果 G-D 的 alpha 显著，也不能马上进入策略，需要做样本外、子样本、交易成本和多重检验控制。
3. 下一步应把本模块输出的残差收益、滚动 beta 和 alpha 接到状态变量模块，检验 `VIX/drawdown/rate/relative strength` 是否预测的是原始 G-D，还是因子调整后的 G-D。

##### 7. 输出文件

- 回归面板：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/factor_attribution/inputs/phase1_factor_returns_panel.csv`
- 组合全样本回归：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/factor_attribution/tables/factor_attribution_portfolios_full_sample.csv`
- 单 ETF 全样本回归：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/factor_attribution/tables/factor_attribution_etfs_full_sample.csv`
- 滚动 beta：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/factor_attribution/tables/factor_attribution_rolling_betas.csv`
- 因子调整 residual 序列：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/factor_attribution/tables/factor_attribution_factor_adjusted_returns.csv`
- 滚动 beta 阶段汇总：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/factor_attribution/tables/factor_attribution_rolling_period_summary.csv`
- 数据覆盖：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/factor_attribution/tables/factor_attribution_data_coverage.csv`


### 5.2 Smooth Continuous Score Policy v1

#### 第一阶段 Smooth Continuous Score Policy v1 报告

##### 1. 本步目标

本步不再找变量，而是检验 `TNX + SPY drawdown + 平滑交互项` 能否改善 G/D 动态配置。
所有策略都使用连续 score、tanh 仓位映射和 EWMA 权重平滑；没有分位调仓、硬 if 规则或最小调仓阈值。

##### 2. 样本与口径

- G/D 日收益源样本：`2016-12-21` 到 `2026-05-15`，n=`2362`。
- 可用于 63 日目标诊断的样本：`2017-06-26` 到 `2026-02-13`，n=`2172`。
- Smooth score 完整特征样本：`2017-06-26` 到 `2026-05-15`，n=`2235`。
- 主策略比较从 G/D 最早共同可用日期开始：`2016-12-21` 到 `2026-05-15`。
- G/D 收益来自 state framework 输入面板；单 ETF 的孤立日线缺口已在价格层做最多 3 个交易日的 forward-fill 后再计算收益，避免一根缺失 K 线污染 63/126 日滚动变量。
- 注意：`gd_trailing_126d` 需要 126 个交易日 warmup，因此动态 smooth score 的实际可交易起点会晚于 2016-12-21；这不是中途截样，而是变量定义带来的自然 warmup。
- 信号在 t 日收盘后形成，t+1 日收益开始使用。
- 标准化均为 expanding z-score，不使用全样本 z-score。
- 本版报告只保留规则型 smooth score、补充 tilt 网格和 buy-and-hold 基准。
- 交易成本报告 `0bp`、`5bp`、`10bp`、`20bp`；成本按 `2 × |ΔG权重| × cost_bps / 10000` 扣除。

##### 3. 第一轮：max_tilt 规格测试

第一轮固定 `alpha=0.50, lambda_stress=0.25, lambda_crowded=0.15, tau_weight=1.0, eta=0.05`，只测试 `max_tilt` 与交易成本。这里的 `max_tilt` 是 tanh 平滑映射的最大主动倾斜幅度。

| cost_bps | max_tilt | final_wealth | cagr | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | ann_excess_vs_50_50 | ann_excess_vs_100_g | max_dd_diff_vs_100_g |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 20.00% | 4.37 | 18.11% | 0.96 | -32.83% | 0.55 | 186.35% | 48.77% | 0.84% | -3.60% | 1.52% |
| 0 | 30.00% | 4.54 | 18.61% | 0.98 | -32.45% | 0.57 | 279.52% | 48.15% | 1.25% | -3.18% | 1.90% |
| 0 | 40.00% | 4.70 | 19.09% | 1.00 | -32.06% | 0.60 | 372.70% | 47.54% | 1.67% | -2.76% | 2.28% |
| 0 | 50.00% | 4.88 | 19.58% | 1.02 | -31.68% | 0.62 | 465.87% | 46.92% | 2.09% | -2.34% | 2.67% |
| 5 | 20.00% | 4.34 | 18.00% | 0.95 | -32.84% | 0.55 | 186.35% | 48.77% | 0.74% | -3.69% | 1.51% |
| 5 | 30.00% | 4.48 | 18.44% | 0.97 | -32.46% | 0.57 | 279.52% | 48.15% | 1.12% | -3.32% | 1.89% |
| 5 | 40.00% | 4.63 | 18.87% | 0.99 | -32.08% | 0.59 | 372.70% | 47.54% | 1.49% | -2.95% | 2.27% |
| 5 | 50.00% | 4.78 | 19.30% | 1.01 | -31.70% | 0.61 | 465.87% | 46.92% | 1.86% | -2.58% | 2.65% |
| 10 | 20.00% | 4.30 | 17.89% | 0.95 | -32.84% | 0.54 | 186.35% | 48.77% | 0.65% | -3.78% | 1.50% |
| 10 | 30.00% | 4.42 | 18.27% | 0.97 | -32.47% | 0.56 | 279.52% | 48.15% | 0.98% | -3.46% | 1.87% |
| 10 | 40.00% | 4.55 | 18.65% | 0.98 | -32.10% | 0.58 | 372.70% | 47.54% | 1.30% | -3.13% | 2.25% |
| 10 | 50.00% | 4.68 | 19.02% | 0.99 | -31.72% | 0.60 | 465.87% | 46.92% | 1.63% | -2.81% | 2.62% |
| 20 | 20.00% | 4.23 | 17.68% | 0.94 | -32.86% | 0.54 | 186.35% | 48.77% | 0.46% | -3.97% | 1.48% |
| 20 | 30.00% | 4.32 | 17.94% | 0.95 | -32.50% | 0.55 | 279.52% | 48.15% | 0.70% | -3.74% | 1.85% |
| 20 | 40.00% | 4.40 | 18.21% | 0.96 | -32.13% | 0.57 | 372.70% | 47.54% | 0.93% | -3.51% | 2.21% |
| 20 | 50.00% | 4.49 | 18.47% | 0.97 | -31.76% | 0.58 | 465.87% | 46.92% | 1.16% | -3.28% | 2.58% |

- 10bp 主口径下，固定结构里的最佳 `max_tilt` 是 `50%`；CAGR `19.02%`，Sharpe `0.99`，Max DD `-31.72%`。
- 因此后续主策略比较不再沿用原始 20% tilt 的 `Traditional Smooth Score`，而是转向 50% tilt 体系。

![Supplementary Extreme Tilt 资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_supplementary_extreme_tilt_equity_curves.png)
图表时间范围：`2017-06-28` 到 `2026-05-15`。

##### 4. 第二轮：Expanded Local Grid

第二轮按你的扩展网格运行：`alpha ∈ {0.50,0.67}`、`lambda_stress ∈ {0.25,0.50}`、`lambda_crowded ∈ {0.05,0.15,0.25}`、`max_tilt ∈ {20%,30%,40%,50%}`、`tau_weight ∈ {0.75,1.0,1.5}`、`eta ∈ {0.03,0.05,0.10}`。主结论看 10bp，20bp 作为压力测试。

###### 4.1 10bp 主口径 Top 10

| config_id | final_wealth | cagr | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | ann_excess_vs_50_50 | ann_excess_vs_100_g | max_dd_diff_vs_100_g | selection_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05 | 4.76 | 19.24% | 1.01 | -31.63% | 0.61 | 469.67% | 45.06% | 1.78% | -2.66% | 2.71% | 80.05% |
| local_a0.50_ls0.50_lc0.05_tilt0.50_tau1.00_eta0.05 | 4.70 | 19.08% | 1.00 | -31.69% | 0.60 | 413.13% | 46.47% | 1.64% | -2.79% | 2.65% | 79.77% |
| local_a0.50_ls0.25_lc0.05_tilt0.50_tau0.75_eta0.05 | 4.78 | 19.30% | 1.01 | -31.54% | 0.61 | 520.00% | 46.99% | 1.86% | -2.57% | 2.80% | 79.72% |
| local_a0.50_ls0.25_lc0.05_tilt0.50_tau1.00_eta0.05 | 4.72 | 19.13% | 1.00 | -31.61% | 0.61 | 459.90% | 48.00% | 1.71% | -2.72% | 2.74% | 79.40% |
| local_a0.50_ls0.50_lc0.15_tilt0.50_tau0.75_eta0.05 | 4.72 | 19.14% | 1.00 | -31.75% | 0.60 | 481.06% | 44.05% | 1.70% | -2.74% | 2.60% | 78.12% |
| local_a0.50_ls0.50_lc0.15_tilt0.50_tau1.00_eta0.05 | 4.67 | 19.01% | 1.00 | -31.79% | 0.60 | 423.09% | 45.55% | 1.59% | -2.85% | 2.56% | 77.80% |
| local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.03 | 4.74 | 19.18% | 1.02 | -32.35% | 0.59 | 322.13% | 45.08% | 1.70% | -2.74% | 1.99% | 77.71% |
| local_a0.50_ls0.25_lc0.05_tilt0.50_tau1.00_eta0.03 | 4.71 | 19.11% | 1.01 | -32.28% | 0.59 | 314.08% | 48.03% | 1.66% | -2.77% | 2.07% | 77.57% |
| local_a0.50_ls0.25_lc0.05_tilt0.50_tau0.75_eta0.03 | 4.77 | 19.28% | 1.01 | -32.25% | 0.60 | 356.85% | 47.03% | 1.81% | -2.63% | 2.09% | 77.48% |
| local_a0.50_ls0.50_lc0.05_tilt0.50_tau1.00_eta0.03 | 4.68 | 19.02% | 1.01 | -32.37% | 0.59 | 282.31% | 46.49% | 1.56% | -2.87% | 1.98% | 77.43% |

###### 4.2 20bp 压力测试 Top 10

| config_id | final_wealth | cagr | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | ann_excess_vs_50_50 | ann_excess_vs_100_g | max_dd_diff_vs_100_g |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.03 | 4.60 | 18.80% | 1.00 | -32.39% | 0.58 | 322.13% | 45.08% | 1.37% | -3.06% | 1.96% |
| local_a0.50_ls0.50_lc0.15_tilt0.50_tau0.75_eta0.03 | 4.59 | 18.75% | 1.00 | -32.52% | 0.58 | 330.08% | 44.05% | 1.33% | -3.10% | 1.82% |
| local_a0.50_ls0.50_lc0.25_tilt0.50_tau0.75_eta0.03 | 4.58 | 18.75% | 0.99 | -32.65% | 0.57 | 332.87% | 43.90% | 1.33% | -3.10% | 1.70% |
| local_a0.50_ls0.25_lc0.05_tilt0.50_tau0.75_eta0.03 | 4.62 | 18.86% | 0.99 | -32.29% | 0.58 | 356.85% | 47.03% | 1.45% | -2.99% | 2.06% |
| local_a0.50_ls0.50_lc0.05_tilt0.50_tau1.00_eta0.03 | 4.56 | 18.68% | 0.99 | -32.40% | 0.58 | 282.31% | 46.49% | 1.28% | -3.15% | 1.94% |
| local_a0.50_ls0.25_lc0.15_tilt0.50_tau0.75_eta0.03 | 4.60 | 18.79% | 0.99 | -32.45% | 0.58 | 361.37% | 45.83% | 1.39% | -3.05% | 1.90% |
| local_a0.50_ls0.50_lc0.15_tilt0.50_tau1.00_eta0.03 | 4.55 | 18.65% | 0.99 | -32.51% | 0.57 | 289.11% | 45.54% | 1.25% | -3.18% | 1.83% |
| local_a0.50_ls0.25_lc0.25_tilt0.50_tau0.75_eta0.03 | 4.59 | 18.76% | 0.99 | -32.60% | 0.58 | 360.19% | 45.64% | 1.38% | -3.06% | 1.75% |
| local_a0.50_ls0.25_lc0.05_tilt0.50_tau1.00_eta0.03 | 4.58 | 18.74% | 0.99 | -32.31% | 0.58 | 314.08% | 48.03% | 1.35% | -3.09% | 2.04% |
| local_a0.50_ls0.50_lc0.25_tilt0.50_tau1.00_eta0.03 | 4.55 | 18.63% | 0.99 | -32.61% | 0.57 | 291.97% | 45.29% | 1.24% | -3.19% | 1.73% |

###### 4.3 10bp 入选局部网格配置的成本敏感性：`local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05`

| cost_bps | final_wealth | cagr | sharpe | max_drawdown | calmar | annual_turnover | ann_excess_vs_50_50 | ann_excess_vs_100_g |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 4.96 | 19.80% | 1.03 | -31.59% | 0.63 | 469.67% | 2.25% | -2.19% |
| 5 | 4.86 | 19.52% | 1.02 | -31.61% | 0.62 | 469.67% | 2.01% | -2.42% |
| 10 | 4.76 | 19.24% | 1.01 | -31.63% | 0.61 | 469.67% | 1.78% | -2.66% |
| 20 | 4.56 | 18.68% | 0.98 | -31.67% | 0.59 | 469.67% | 1.31% | -3.13% |

###### 4.4 局部最佳方案资金曲线

- 后续主策略配置：`local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05`。
- 这个配置来自 expanded local grid，且 `max_tilt=50%`。后续所有主对比、vol-matched、静态 G/D 对照都以它作为目标 smooth score。

![Supplementary Best Local Grid 资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_supplementary_best_local_equity_curves.png)
图表时间范围：`2017-06-28` 到 `2026-05-15`。

##### 5. 以 50% tilt 最佳方案为主策略的对齐统计

这一张表从这里开始统一主口径：`Best Local Grid (tilt 50%)` 是后续主策略；`Matched TNX-only` 与 `Matched Core-only` 使用同样的 `max_tilt/tau/eta` 仓位映射，分别只保留 TNX 或 TNX+drawdown 主轴；`Extreme 50% Tilt` 是固定结构下的 50% tilt 对照。所有方法先对齐到同一可用日期区间。

| display_name | config_id | start_date | end_date | n_days | final_wealth | cagr | ann_vol | sharpe | sortino | max_drawdown | calmar | annual_turnover | avg_g_weight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Best Local Grid (tilt 50%) | local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05 | 2017-06-28 | 2026-05-15 | 2233 | 4.71 | 19.24% | 19.29% | 1.01 | 1.22 | -31.63% | 0.61 | 469.67% | 45.06% |
| Matched TNX-only (tilt 50%) | tnx_tilt0.50_tau0.75_eta0.05 | 2017-06-28 | 2026-05-15 | 2233 | 4.23 | 17.80% | 19.33% | 0.94 | 1.13 | -31.31% | 0.57 | 566.69% | 47.48% |
| Matched Core-only (tilt 50%) | core_a0.50_tilt0.50_tau0.75_eta0.05 | 2017-06-28 | 2026-05-15 | 2233 | 4.25 | 17.84% | 18.94% | 0.96 | 1.15 | -31.98% | 0.56 | 410.19% | 37.18% |
| Extreme 50% Tilt | extreme_a0.50_ls0.25_lc0.15_tilt0.50_tau1.0_eta0.05 | 2017-06-28 | 2026-05-15 | 2233 | 4.64 | 19.02% | 19.45% | 0.99 | 1.20 | -31.72% | 0.60 | 465.87% | 46.92% |
| 50/50 G-D Buy & Hold | benchmark_50_50_gd | 2017-06-28 | 2026-05-15 | 2233 | 4.02 | 17.12% | 19.34% | 0.91 | 1.08 | -33.59% | 0.51 | 0.00% | 50.00% |
| 100% G Buy & Hold | benchmark_100_g | 2017-06-28 | 2026-05-15 | 2233 | 5.49 | 21.34% | 23.53% | 0.94 | 1.17 | -34.35% | 0.62 | 0.00% | 100.00% |
| 100% D Buy & Hold | benchmark_100_d | 2017-06-28 | 2026-05-15 | 2233 | 2.80 | 12.42% | 17.53% | 0.76 | 0.86 | -36.71% | 0.34 | 0.00% | 0.00% |
| SPY Buy & Hold | benchmark_spy | 2017-06-28 | 2026-05-15 | 2233 | 3.49 | 15.25% | 18.74% | 0.85 | 0.98 | -33.72% | 0.45 | 0.00% |  |

##### 6. 以 50% tilt 最佳方案为主策略的增量比较，10bp 成本

| comparison | annualized_excess_return | tracking_error | information_ratio | max_dd_diff | turnover_diff |
| --- | --- | --- | --- | --- | --- |
| Best Local Grid - matched TNX-only | 1.21% | 2.49% | 0.48 | -0.33% | -97.01% |
| Best Local Grid - matched Core-only | 1.25% | 1.81% | 0.69 | 0.35% | 59.48% |
| Best Local Grid - Extreme 50% Tilt | 0.15% | 1.00% | 0.15 | 0.09% | 3.80% |
| Best Local Grid - 50/50 | 1.78% | 3.74% | 0.48 | 1.95% | 469.67% |
| Best Local Grid - 100% G | -2.66% | 9.48% | -0.28 | 2.71% | 469.67% |
| Best Local Grid - SPY | 3.51% | 4.32% | 0.81 | 2.08% | 469.67% |

##### 7. 资金曲线对比

下面两张图都使用 `10bp` 成本，并先取图内所有曲线的共同可用日期区间，再统一 rebase 到 `1.0`。第一张图比较 50% tilt 主策略、matched TNX-only、matched Core-only、Extreme 50% 与静态基准；第二张图只显示 buy-and-hold 基础基准。

![共同起点所有方法资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_common_oos_equity_curves_all.png)
图表时间范围：`2017-06-28` 到 `2026-05-15`。

![G/D Buy and Hold 基础资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_common_oos_buy_hold_gd.png)
图表时间范围：`2017-06-28` 到 `2026-05-15`。

图中 `100% G Buy & Hold` 和 `100% D Buy & Hold` 是单纯买入并持有 G、D 篮子的基础对照；`50/50 G-D Buy & Hold` 是不择时的静态配置基准。

##### 8. Vol-Matched 与静态 G/D 对照

这一节以 10bp 主口径的 `Best Local Grid (tilt 50%)` 为目标策略，比较同风险水平下的 `100% G` 缩放版本、等波动/等回撤静态 G-D、以及最优静态 G-D。
- 目标 Smooth Score 配置：`local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05`
- Vol-matched 100% G 的缩放权重：`81.95%`

| method_label | comparison_type | static_g_weight | scale_to_g | final_wealth | cagr | ann_vol | sharpe | sortino | max_drawdown | calmar | annual_turnover | ann_excess_vs_smooth | max_dd_diff_vs_smooth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Smooth Score Best Local | target |  |  | 4.76 | 19.24% | 19.29% | 1.01 | 1.22 | -31.63% | 0.61 | 469.67% | 0.00% | 0.00% |
| 100% G Buy & Hold | baseline |  |  | 5.55 | 21.34% | 23.53% | 0.94 | 1.17 | -34.35% | 0.62 | 0.00% | 2.66% | -2.71% |
| Vol-Matched 100% G | vol_matched_g |  | 81.95% | 4.23 | 17.66% | 19.29% | 0.94 | 1.18 | -28.73% | 0.61 | 0.00% | -1.34% | 2.90% |
| 50/50 G-D | baseline |  |  | 4.06 | 17.12% | 19.34% | 0.91 | 1.08 | -33.59% | 0.51 | 0.00% | -1.78% | -1.95% |
| 100% D Buy & Hold | baseline |  |  | 2.82 | 12.42% | 17.53% | 0.76 | 0.86 | -36.71% | 0.34 | 0.00% | -6.21% | -5.08% |
| SPY Buy & Hold | baseline |  |  | 3.52 | 15.25% | 18.74% | 0.85 | 0.98 | -33.72% | 0.45 | 0.00% | -3.51% | -2.08% |
| Vol-Matched Static G/D (49% G) | vol_matched_static_gd | 49.00% |  | 4.03 | 17.03% | 19.28% | 0.91 | 1.08 | -33.64% | 0.51 | 0.00% | -1.87% | -2.01% |
| MaxDD-Matched Static G/D (87% G) | maxdd_matched_static_gd | 87.00% |  | 5.14 | 20.29% | 22.28% | 0.94 | 1.16 | -31.65% | 0.64 | 0.00% | 1.50% | -0.01% |
| Best Sharpe Static G/D (89% G) | best_sharpe_static_gd | 89.00% |  | 5.20 | 20.46% | 22.46% | 0.94 | 1.16 | -32.07% | 0.64 | 0.00% | 1.68% | -0.43% |
| Best Calmar Static G/D (87% G) | best_calmar_static_gd | 87.00% |  | 5.14 | 20.29% | 22.28% | 0.94 | 1.16 | -31.65% | 0.64 | 0.00% | 1.50% | -0.01% |
| Best CAGR Static G/D under Smooth MaxDD (86% G) | best_cagr_static_under_smooth_maxdd | 86.00% |  | 5.11 | 20.21% | 22.18% | 0.94 | 1.15 | -31.59% | 0.64 | 0.00% | 1.42% | 0.04% |

![Vol-Matched 与静态 G/D 对照资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_vol_matched_static_equity_curves.png)
图表时间范围：`2017-06-28` 到 `2026-05-15`。

##### 9. OOS Validation：Expanding、Rolling 与固定参数

这一节把 `WF Expanding`、`WF Rolling` 和 `Fixed Parameter` 合并到同一张 OOS 表、同一张资金曲线中，交易期完全对齐。它们都只在过去窗口内选择参数，然后部署到之后的测试期。

- 候选参数池：expanded local grid，即 `alpha ∈ {0.50,0.67}`、`lambda_stress ∈ {0.25,0.50}`、`lambda_crowded ∈ {0.05,0.15,0.25}`、`max_tilt ∈ {20%,30%,40%,50%}`、`tau_weight ∈ {0.75,1.0,1.5}`、`eta ∈ {0.03,0.05,0.10}`。
- 初始训练窗口：`252` 个交易日；测试块长度：`63` 个交易日。
- 参数选择指标：`selection_score`，等权平均 Sharpe、Calmar、CAGR、max drawdown 排名和低 turnover 排名。
- `WF Expanding`：每个测试块前，使用从最早可用日期到测试块前一日的全部历史重新选参。
- `WF Rolling`：每个测试块前，只使用最近 `252` 个交易日重新选参。
- `Fixed Parameter`：只用最早训练窗口 `2017-06-28` 到 `2018-06-27` 选参一次，从 `2018-06-28` 开始固定该配置交易。
- Fixed Parameter 选中配置：`local_a0.50_ls0.50_lc0.25_tilt0.20_tau1.50_eta0.03`。

| validation_label | start_date | end_date | n_days | final_wealth | cagr | ann_vol | sharpe | sortino | max_drawdown | calmar | annual_turnover | avg_g_weight | ann_excess_vs_expanding_wf | max_dd_diff_vs_expanding_wf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Smooth Score WF Expanding | 2018-06-28 | 2026-05-15 | 1981 | 3.83 | 18.64% | 19.77% | 0.96 | 1.16 | -32.93% | 0.57 | 332.21% | 44.82% | 0.00% | 0.00% |
| Smooth Score WF Rolling | 2018-06-28 | 2026-05-15 | 1981 | 3.68 | 18.02% | 19.86% | 0.93 | 1.12 | -32.79% | 0.55 | 350.79% | 46.66% | -0.61% | 0.14% |
| Fixed Parameter | 2018-06-28 | 2026-05-15 | 1981 | 3.64 | 17.86% | 19.90% | 0.93 | 1.11 | -33.19% | 0.54 | 88.36% | 48.63% | -0.77% | -0.26% |
| 50/50 G-D | 2018-06-28 | 2026-05-15 | 1981 | 3.46 | 17.10% | 20.00% | 0.89 | 1.06 | -33.59% | 0.51 | 0.00% | 50.00% | -1.53% | -0.66% |
| 100% G | 2018-06-28 | 2026-05-15 | 1981 | 4.51 | 21.13% | 24.38% | 0.91 | 1.13 | -34.35% | 0.62 | 0.00% | 100.00% | 2.50% | -1.42% |
| 100% D | 2018-06-28 | 2026-05-15 | 1981 | 2.53 | 12.51% | 18.14% | 0.74 | 0.85 | -36.71% | 0.34 | 0.00% | 0.00% | -6.13% | -3.79% |
| SPY | 2018-06-28 | 2026-05-15 | 1981 | 3.09 | 15.45% | 19.39% | 0.84 | 0.98 | -33.72% | 0.46 | 0.00% |  | -3.19% | -0.79% |

![OOS Validation 资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_nested_walk_forward_equity_curves.png)
图表时间范围：`2018-06-28` 到 `2026-05-15`。

##### 9.1 补充：2022 起始 OOS Validation

这一节用于剔除 2020 疫情回撤对绩效评价的直接影响。疫情期间 D 篮子回撤一度大于 G 篮子，容易让全样本 OOS 结果受到特殊事件扰动；因此这里从 `2022-01-01` 之后首个共同交易日开始重新生成同口径 OOS validation。

- `WF Expanding`：测试块从 2022 年之后重新切分，每个测试块前使用此前全部可用历史选参。
- `WF Rolling`：测试块从 2022 年之后重新切分，每个测试块前只使用最近 `252` 个交易日选参。
- `Fixed Parameter`：固定参数仍只用最早训练窗口 `2017-06-28` 到 `2018-06-27` 选参一次，但绩效评价从 `2022-01-03` 开始。
- Fixed Parameter 选中配置：`local_a0.50_ls0.50_lc0.25_tilt0.20_tau1.50_eta0.03`。
- 交易成本：`10bp`；所有曲线在同一张图中按共同起点重新 rebased 到 1。

| validation_label | start_date | end_date | n_days | final_wealth | cagr | ann_vol | sharpe | sortino | max_drawdown | calmar | annual_turnover | avg_g_weight | ann_excess_vs_expanding_wf | max_dd_diff_vs_expanding_wf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Smooth Score WF Expanding | 2022-01-03 | 2026-05-15 | 1096 | 1.86 | 15.30% | 17.53% | 0.90 | 1.22 | -19.89% | 0.77 | 406.50% | 41.52% | 0.00% | 0.00% |
| Smooth Score WF Rolling | 2022-01-03 | 2026-05-15 | 1096 | 1.76 | 13.92% | 17.78% | 0.82 | 1.08 | -21.28% | 0.65 | 390.15% | 45.27% | -1.38% | -1.39% |
| Fixed Parameter | 2022-01-03 | 2026-05-15 | 1096 | 1.77 | 13.99% | 17.85% | 0.82 | 1.09 | -22.46% | 0.62 | 83.97% | 47.31% | -1.31% | -2.58% |
| 50/50 G-D | 2022-01-03 | 2026-05-15 | 1096 | 1.72 | 13.23% | 18.02% | 0.78 | 1.02 | -23.78% | 0.56 | 0.00% | 50.00% | -2.07% | -3.89% |
| 100% G | 2022-01-03 | 2026-05-15 | 1096 | 1.87 | 15.45% | 23.81% | 0.72 | 0.93 | -33.92% | 0.46 | 0.00% | 100.00% | 0.15% | -14.04% |
| 100% D | 2022-01-03 | 2026-05-15 | 1096 | 1.53 | 10.32% | 14.71% | 0.74 | 0.99 | -17.32% | 0.60 | 0.00% | 0.00% | -4.98% | 2.57% |
| SPY | 2022-01-03 | 2026-05-15 | 1096 | 1.65 | 12.21% | 17.68% | 0.74 | 0.96 | -24.50% | 0.50 | 0.00% |  | -3.09% | -4.61% |

![2022 起始 OOS Validation 资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_post_2022_validation_equity_curves.png)
图表时间范围：`2022-01-03` 到 `2026-05-15`。

##### 10. Score 排序诊断

| method | config_id | Q1 | Q2 | Q3 | Q4 | Q5 | Q5_minus_Q1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| matched_smooth_core_only | core_a0.50_tilt0.50_tau0.75_eta0.05 | 0.02% | -0.25% | 1.16% | 2.48% | 5.57% | 5.56% |
| supp_expanded_local_grid | local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05 | -1.01% | 0.17% | 1.00% | 3.32% | 5.48% | 6.48% |
| supp_extreme_tilt_base | extreme_a0.50_ls0.25_lc0.15_tilt0.50_tau1.0_eta0.05 | -0.35% | -0.04% | 0.51% | 3.63% | 5.22% | 5.57% |
| matched_smooth_tnx_only | tnx_tilt0.50_tau0.75_eta0.05 | 0.04% | 0.66% | 1.90% | 2.52% | 3.86% | 3.82% |

##### 11. 共同起点年度表现，10bp 成本

| method | config_id | year | cagr | sharpe | max_drawdown | annual_turnover | avg_g_weight |
| --- | --- | --- | --- | --- | --- | --- | --- |
| benchmark_100_d | benchmark_100_d | 2017 | 24.39% | 3.47 | -2.35% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2018 | -5.67% | -0.31 | -17.54% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2019 | 25.08% | 1.94 | -7.88% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2020 | 6.60% | 0.36 | -36.71% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2021 | 30.83% | 2.14 | -5.18% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2022 | -1.87% | 0.00 | -17.32% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2023 | 10.69% | 0.87 | -9.53% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2024 | 15.55% | 1.41 | -6.99% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2025 | 12.31% | 0.83 | -15.16% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2026 | 26.09% | 2.33 | -5.89% | 0.00% | 0.00% |
| benchmark_100_g | benchmark_100_g | 2017 | 29.53% | 2.73 | -2.40% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2018 | -0.60% | 0.08 | -22.54% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2019 | 41.00% | 2.27 | -9.27% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2020 | 42.24% | 1.14 | -30.81% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2021 | 30.41% | 1.57 | -9.83% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2022 | -30.61% | -0.97 | -33.92% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2023 | 48.31% | 2.43 | -10.69% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2024 | 29.06% | 1.43 | -14.22% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2025 | 22.00% | 0.92 | -24.06% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2026 | 48.22% | 2.03 | -13.46% | 0.00% | 100.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2017 | 27.03% | 3.35 | -2.08% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2018 | -3.03% | -0.08 | -19.71% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2019 | 32.90% | 2.19 | -8.03% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2020 | 23.71% | 0.79 | -33.59% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2021 | 31.04% | 2.08 | -4.92% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2022 | -17.12% | -0.62 | -23.78% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2023 | 28.40% | 1.93 | -9.73% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2024 | 22.51% | 1.60 | -8.88% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2025 | 17.46% | 0.94 | -19.66% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2026 | 37.22% | 2.39 | -7.95% | 0.00% | 50.00% |
| benchmark_spy | benchmark_spy | 2017 | 24.08% | 3.38 | -2.07% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2018 | -4.59% | -0.19 | -19.35% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2019 | 31.22% | 2.24 | -6.62% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2020 | 18.25% | 0.67 | -33.72% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2021 | 28.73% | 2.01 | -5.11% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2022 | -18.24% | -0.71 | -24.50% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2023 | 26.41% | 1.86 | -9.97% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2024 | 24.89% | 1.84 | -8.41% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2025 | 17.87% | 0.94 | -18.76% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2026 | 25.50% | 1.72 | -8.88% | 0.00% |  |
| matched_smooth_core_only | core_a0.50_tilt0.50_tau0.75_eta0.05 | 2017 | 24.62% | 3.41 | -2.23% | 223.97% | 21.50% |
| matched_smooth_core_only | core_a0.50_tilt0.50_tau0.75_eta0.05 | 2018 | -4.75% | -0.21 | -18.82% | 324.05% | 27.34% |
| matched_smooth_core_only | core_a0.50_tilt0.50_tau0.75_eta0.05 | 2019 | 31.06% | 2.07 | -7.98% | 464.88% | 45.96% |
| matched_smooth_core_only | core_a0.50_tilt0.50_tau0.75_eta0.05 | 2020 | 25.26% | 0.83 | -31.98% | 367.05% | 44.98% |
| matched_smooth_core_only | core_a0.50_tilt0.50_tau0.75_eta0.05 | 2021 | 31.97% | 2.27 | -4.63% | 272.40% | 24.44% |
| matched_smooth_core_only | core_a0.50_tilt0.50_tau0.75_eta0.05 | 2022 | -9.75% | -0.32 | -18.00% | 575.01% | 39.97% |
| matched_smooth_core_only | core_a0.50_tilt0.50_tau0.75_eta0.05 | 2023 | 29.48% | 1.96 | -9.78% | 529.94% | 46.38% |
| matched_smooth_core_only | core_a0.50_tilt0.50_tau0.75_eta0.05 | 2024 | 20.27% | 1.50 | -8.42% | 474.91% | 37.59% |
| matched_smooth_core_only | core_a0.50_tilt0.50_tau0.75_eta0.05 | 2025 | 18.97% | 0.99 | -19.46% | 395.83% | 41.63% |
| matched_smooth_core_only | core_a0.50_tilt0.50_tau0.75_eta0.05 | 2026 | 32.95% | 2.50 | -6.99% | 340.03% | 29.60% |
| matched_smooth_tnx_only | tnx_tilt0.50_tau0.75_eta0.05 | 2017 | 24.46% | 3.09 | -2.09% | 521.29% | 45.65% |
| matched_smooth_tnx_only | tnx_tilt0.50_tau0.75_eta0.05 | 2018 | -4.59% | -0.18 | -19.10% | 535.32% | 40.13% |
| matched_smooth_tnx_only | tnx_tilt0.50_tau0.75_eta0.05 | 2019 | 33.86% | 2.12 | -8.51% | 539.48% | 64.13% |
| matched_smooth_tnx_only | tnx_tilt0.50_tau0.75_eta0.05 | 2020 | 28.68% | 0.90 | -31.31% | 452.96% | 52.81% |
| matched_smooth_tnx_only | tnx_tilt0.50_tau0.75_eta0.05 | 2021 | 32.68% | 2.27 | -4.65% | 482.33% | 39.88% |
| matched_smooth_tnx_only | tnx_tilt0.50_tau0.75_eta0.05 | 2022 | -11.01% | -0.41 | -19.47% | 676.21% | 31.32% |
| matched_smooth_tnx_only | tnx_tilt0.50_tau0.75_eta0.05 | 2023 | 24.41% | 1.71 | -9.88% | 679.66% | 41.98% |
| matched_smooth_tnx_only | tnx_tilt0.50_tau0.75_eta0.05 | 2024 | 21.41% | 1.40 | -10.83% | 643.51% | 54.16% |
| matched_smooth_tnx_only | tnx_tilt0.50_tau0.75_eta0.05 | 2025 | 17.51% | 0.89 | -21.11% | 549.67% | 57.27% |
| matched_smooth_tnx_only | tnx_tilt0.50_tau0.75_eta0.05 | 2026 | 32.67% | 2.25 | -7.52% | 564.32% | 44.80% |
| supp_expanded_local_grid | local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05 | 2017 | 23.19% | 2.92 | -2.03% | 656.03% | 47.83% |
| supp_expanded_local_grid | local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05 | 2018 | -3.33% | -0.09 | -19.60% | 604.88% | 56.09% |
| supp_expanded_local_grid | local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05 | 2019 | 35.12% | 2.17 | -8.38% | 533.41% | 64.38% |
| supp_expanded_local_grid | local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05 | 2020 | 28.88% | 0.91 | -31.63% | 438.04% | 53.02% |
| supp_expanded_local_grid | local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05 | 2021 | 31.65% | 2.26 | -4.72% | 268.14% | 24.39% |
| supp_expanded_local_grid | local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05 | 2022 | -9.53% | -0.31 | -18.04% | 640.34% | 40.06% |
| supp_expanded_local_grid | local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05 | 2023 | 29.38% | 1.97 | -9.59% | 362.57% | 40.82% |
| supp_expanded_local_grid | local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05 | 2024 | 20.40% | 1.57 | -7.16% | 352.67% | 31.48% |
| supp_expanded_local_grid | local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05 | 2025 | 20.53% | 1.03 | -19.94% | 409.22% | 49.67% |
| supp_expanded_local_grid | local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05 | 2026 | 41.77% | 2.79 | -7.33% | 612.58% | 42.76% |
| supp_extreme_tilt_base | extreme_a0.50_ls0.25_lc0.15_tilt0.50_tau1.0_eta0.05 | 2017 | 23.71% | 2.96 | -2.04% | 585.58% | 49.72% |
| supp_extreme_tilt_base | extreme_a0.50_ls0.25_lc0.15_tilt0.50_tau1.0_eta0.05 | 2018 | -3.58% | -0.11 | -19.87% | 627.83% | 53.93% |
| supp_extreme_tilt_base | extreme_a0.50_ls0.25_lc0.15_tilt0.50_tau1.0_eta0.05 | 2019 | 34.88% | 2.18 | -8.32% | 534.61% | 62.45% |
| supp_extreme_tilt_base | extreme_a0.50_ls0.25_lc0.15_tilt0.50_tau1.0_eta0.05 | 2020 | 28.08% | 0.89 | -31.72% | 387.25% | 51.25% |
| supp_extreme_tilt_base | extreme_a0.50_ls0.25_lc0.15_tilt0.50_tau1.0_eta0.05 | 2021 | 32.03% | 2.28 | -4.74% | 306.71% | 31.67% |
| supp_extreme_tilt_base | extreme_a0.50_ls0.25_lc0.15_tilt0.50_tau1.0_eta0.05 | 2022 | -10.89% | -0.35 | -18.61% | 600.17% | 46.56% |
| supp_extreme_tilt_base | extreme_a0.50_ls0.25_lc0.15_tilt0.50_tau1.0_eta0.05 | 2023 | 28.36% | 1.91 | -9.43% | 431.97% | 39.05% |
| supp_extreme_tilt_base | extreme_a0.50_ls0.25_lc0.15_tilt0.50_tau1.0_eta0.05 | 2024 | 21.86% | 1.61 | -7.68% | 412.69% | 37.72% |
| supp_extreme_tilt_base | extreme_a0.50_ls0.25_lc0.15_tilt0.50_tau1.0_eta0.05 | 2025 | 20.81% | 1.03 | -20.18% | 366.96% | 51.49% |
| supp_extreme_tilt_base | extreme_a0.50_ls0.25_lc0.15_tilt0.50_tau1.0_eta0.05 | 2026 | 40.95% | 2.66 | -7.70% | 460.24% | 46.43% |

##### 13. 输出文件

- 特征面板：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/inputs/smooth_score_policy_v1_feature_panel.csv`
- 信号权重：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_signals.csv`
- 日收益：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_daily_returns.csv`
- 主策略表现：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_metrics.csv`
- 2016 起点主策略表现：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_metrics.csv`
- 入选方法与 buy-and-hold 对齐统计：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_selected_summary.csv`
- 增量比较：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_comparisons.csv`
- 2016 起点增量比较：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_comparisons.csv`
- 年度表现：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_yearly_metrics.csv`
- 共同起点年度表现：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_yearly_metrics.csv`
- score 诊断：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_score_diagnostics.csv`
- 2016 起点 score 诊断：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_score_diagnostics.csv`
- 共同起点资金曲线：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_equity_curves.csv`
- 补充 extreme/local tilt 配置：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_supplementary_tilt_config_grid.csv`
- 补充 extreme/local tilt 主表：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_supplementary_tilt_common_oos_summary.csv`
- 补充 extreme/local tilt 日收益：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_supplementary_tilt_common_oos_returns.csv`
- 补充 extreme/local tilt 资金曲线：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_supplementary_tilt_common_oos_equity_curves.csv`
- Vol-matched 与静态 G/D 对照表：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_vol_matched_static_comparison.csv`
- 静态 G/D 权重网格：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_static_gd_grid.csv`
- Vol-matched 与静态 G/D 资金曲线：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_vol_matched_static_equity_curves.csv`
- Nested walk-forward 选择记录：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_nested_walk_forward_selections.csv`
- Nested walk-forward 日收益：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_nested_walk_forward_returns.csv`
- Nested walk-forward 结果：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_nested_walk_forward_summary.csv`
- 固定参数后验验证日收益：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_fixed_parameter_holdout_returns.csv`
- 固定参数后验验证结果：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_fixed_parameter_holdout_summary.csv`
- 所有方法资金曲线图：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_common_oos_equity_curves_all.png`
- G/D buy-and-hold 基础曲线图：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_common_oos_buy_hold_gd.png`
- 补充 extreme tilt 曲线图：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_supplementary_extreme_tilt_equity_curves.png`
- 补充 local grid 曲线图：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_supplementary_best_local_equity_curves.png`
- Vol-matched 与静态 G/D 曲线图：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_vol_matched_static_equity_curves.png`
- OOS validation 合并曲线图：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_nested_walk_forward_equity_curves.png`
- 所有保留表格与图像的起止日期已汇总到合并归档报告的 artifact date range 索引。


### 5.3 Bond/Credit Smooth Policy v1

#### Phase 1 Bond/Credit-Augmented Smooth Policy Full Report

Report scope: full Phase 1 extension after adding aligned bond and credit variables. This is an empirical report, not a manuscript.

##### 0. Scope

This report follows the structure of the 2016 full Phase 1 report. It keeps the original factor-attribution boundary unchanged and adds a new bond/credit-augmented smooth-score policy module. The recent-only HY/IG OAS data are excluded from formal policy tests because they do not align with the full 2017-2026 policy window.

##### 1. Data Start and Warmup

- G/D source returns start on `2016-12-21`.
- Complete policy comparison starts after natural trailing-signal warmup on `2017-06-28`.
- Main aligned policy comparison: `2017-06-28` to `2026-05-15`.
- All policy tests use daily trading-day data.
- Signals are formed after the close and deployed on the next trading day.

##### 2. Module 1: Factor Attribution Boundary

This extension does not rerun or reinterpret the FF5+MOM attribution. The original Phase 1 attribution remains the boundary condition: `G-D` is a style-exposure portfolio, not a newly discovered standalone alpha factor.

| portfolio | n | alpha_ann | alpha_t_NW | MKT | SMB | HML | RMW | CMA | MOM | adj_R2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G | 2330 | 2.24% | 1.51 | 1.148 | -0.118 | -0.298 | 0.067 | -0.071 | 0.041 | 0.965 |
| D | 2330 | 0.29% | 0.24 | 0.874 | 0.019 | 0.254 | 0.088 | 0.227 | -0.076 | 0.950 |
| G-D | 2330 | 1.95% | 0.81 | 0.273 | -0.137 | -0.552 | -0.021 | -0.298 | 0.117 | 0.757 |

Interpretation: `G-D` has positive market beta, strongly negative HML exposure, negative CMA exposure, and positive MOM exposure. Its annualized alpha is positive but not statistically significant under Newey-West standard errors. Therefore the bond/credit extension is evaluated as a timing overlay for known style exposures, not as a test of a new independent alpha.

##### 3. Diagnostic Gate Summary

The bond/credit diagnostic gate identifies three main effects and one interaction worth carrying into the policy test:

| variable | question | coef_63d | t_hac_63d | nonoverlap_coef_63d | passes_gate |
| --- | --- | --- | --- | --- | --- |
| d | SPY drawdown depth: -z(SPY drawdown) | 12.67% | 3.51 | 10.12% | True |
| g126 | G-D trailing 126d relative strength | -2.17% | -2.25 | -3.49% | True |
| ce | Credit relief: -z(BAA-10Y spread 21d change) | 1.31% | 1.70 | 0.14% | True |

| variable | question | coef_63d | t_hac_63d | resid_coef_63d | resid_t_63d | final_pass |
| --- | --- | --- | --- | --- | --- | --- |
| r_x_cs | Rate relief: -z(10Y yield 21d change) × Credit stress level: z(BAA-10Y spread) | 1.71% | 1.51 | 2.07% | 2.36 | True |

##### 4. Bond/Credit Smooth Score Formula

Direction-normalized variables:

```text
d      = -expanding_z(SPY drawdown)
ce     = -expanding_z(BAA10Y spread 21d change)
g126   =  expanding_z(G-D trailing 126d)
cs     =  expanding_z(BAA10Y spread)
r      = -expanding_z(10Y yield 21d change)
z_r_cs =  expanding_z(r * cs)

score = alpha_d * d
      + (1 - alpha_d) * ce
      - lambda_g126 * g126
      + lambda_interaction * z_r_cs
```

Weight mapping:

```text
G_target = 50% + max_tilt * tanh(expanding_z(score) / tau_weight)
G_weight_t = (1 - eta) * G_weight_{t-1} + eta * G_target_t
D_weight_t = 1 - G_weight_t
```

Selected configuration:

| config_id | alpha_d | lambda_credit | lambda_g126 | lambda_interaction | max_tilt | tau_weight | eta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bc_a0.67_lc0.50_lg0.10_li0.10_tilt0.20_tau0.75_eta0.05 | 0.67 | 0.50 | 0.10 | 0.10 | 0.20 | 0.75 | 0.05 |

Strict incremental design:

The `Old Best + Bond/Credit Incremental` experiment keeps the original Best Local structure fixed at `alpha=0.50`, `lambda_stress=0.50`, `lambda_crowded=0.05`, `max_tilt=0.50`, `tau_weight=0.75`, and `eta=0.05`. It only adds two bond/credit terms: `credit relief` and `rate relief × credit stress`. This is the strict test of whether bond/credit information improves the old main strategy rather than replacing it.

| config_id | lambda_credit | lambda_interaction | max_tilt | tau_weight | eta |
| --- | --- | --- | --- | --- | --- |
| old_plus_credit_lc0.10_li0.50 | 0.10 | 0.50 | 0.50 | 0.75 | 0.05 |

##### 5. Grid and Tilt Test

Total candidate configurations tested: `793`.

| max_tilt | config_id | cagr | ann_vol | sharpe | max_drawdown | calmar | annual_turnover | selection_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20.00% | bc_a0.67_lc0.50_lg0.10_li0.10_tilt0.20_tau0.75_eta0.05 | 17.73% | 19.49% | 0.94 | -34.50% | 0.51 | 170.28% | 0.81 |
| 30.00% | bc_a0.67_lc0.25_lg0.10_li0.10_tilt0.30_tau0.75_eta0.03 | 17.86% | 19.56% | 0.94 | -34.79% | 0.51 | 178.59% | 0.79 |
| 40.00% | bc_a0.67_lc0.50_lg0.10_li0.10_tilt0.40_tau1.00_eta0.03 | 17.98% | 19.69% | 0.94 | -35.13% | 0.51 | 210.89% | 0.76 |
| 50.00% | bc_a0.67_lc0.50_lg0.10_li0.10_tilt0.50_tau1.00_eta0.03 | 18.18% | 19.83% | 0.94 | -35.55% | 0.51 | 263.61% | 0.71 |

![Tilt Equity Curves](../plots/bond_credit_smooth_policy_v1_tilt_equity_curves.png)

##### 6. Cost Sensitivity of Selected Configuration

Bond/Credit Smooth Score Best:

| cost_bps | cagr | ann_vol | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | final_wealth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 17.93% | 19.49% | 0.94 | -34.49% | 0.52 | 170.28% | 49.62% | 4.31 |
| 5 | 17.83% | 19.49% | 0.94 | -34.50% | 0.52 | 170.28% | 49.62% | 4.28 |
| 10 | 17.73% | 19.49% | 0.94 | -34.50% | 0.51 | 170.28% | 49.62% | 4.25 |
| 20 | 17.53% | 19.49% | 0.93 | -34.51% | 0.51 | 170.28% | 49.62% | 4.18 |

Old Best + Bond/Credit Incremental:

| cost_bps | cagr | ann_vol | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | final_wealth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 20.29% | 19.14% | 1.06 | -31.87% | 0.64 | 410.23% | 43.72% | 5.14 |
| 5 | 20.05% | 19.14% | 1.05 | -31.89% | 0.63 | 410.23% | 43.72% | 5.05 |
| 10 | 19.80% | 19.14% | 1.04 | -31.92% | 0.62 | 410.23% | 43.72% | 4.96 |
| 20 | 19.31% | 19.14% | 1.02 | -31.97% | 0.60 | 410.23% | 43.72% | 4.78 |

##### 7. Main Aligned Strategy Comparison

| display_name | start_date | end_date | cagr | ann_vol | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | final_wealth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Bond/Credit Smooth Score Best | 2017-06-28 | 2026-05-15 | 17.73% | 19.49% | 0.94 | -34.50% | 0.51 | 170.28% | 49.62% | 4.25 |
| Bond/Credit Core Only | 2017-06-28 | 2026-05-15 | 17.79% | 19.49% | 0.94 | -34.48% | 0.52 | 160.35% | 49.55% | 4.27 |
| Old Best + Bond/Credit Incremental | 2017-06-28 | 2026-05-15 | 19.80% | 19.14% | 1.04 | -31.92% | 0.62 | 410.23% | 43.72% | 4.96 |
| Existing Smooth Score Best Local | 2017-06-28 | 2026-05-15 | 19.24% | 19.29% | 1.01 | -31.63% | 0.61 | 469.67% | 45.06% | 4.76 |
| 50/50 G-D Buy & Hold | 2017-06-28 | 2026-05-15 | 17.12% | 19.34% | 0.91 | -33.59% | 0.51 | 0.00% | 50.00% | 4.06 |
| 100% G Buy & Hold | 2017-06-28 | 2026-05-15 | 21.34% | 23.53% | 0.94 | -34.35% | 0.62 | 0.00% | 100.00% | 5.55 |
| 100% D Buy & Hold | 2017-06-28 | 2026-05-15 | 12.42% | 17.53% | 0.76 | -36.71% | 0.34 | 0.00% | 0.00% | 2.82 |
| SPY Buy & Hold | 2017-06-28 | 2026-05-15 | 15.25% | 18.74% | 0.85 | -33.72% | 0.45 | 0.00% |  | 3.52 |

###### 7.1 Incremental Comparison

| comparison | annualized_excess_return | max_dd_diff | sharpe_diff | turnover_diff |
| --- | --- | --- | --- | --- |
| Bond/Credit Best - Bond/Credit Core Only | -0.06% | -0.03% | -0.00 | 9.93% |
| Bond/Credit Best - Old Best + Bond/Credit Incremental | -2.07% | -2.59% | -0.10 | -239.95% |
| Bond/Credit Best - Existing Smooth Score Best Local | -1.51% | -2.87% | -0.07 | -299.40% |
| Bond/Credit Best - 50/50 G-D Buy & Hold | 0.61% | -0.92% | 0.02 | 170.28% |
| Bond/Credit Best - 100% G Buy & Hold | -3.61% | -0.16% | -0.00 | 170.28% |
| Bond/Credit Best - 100% D Buy & Hold | 5.31% | 2.21% | 0.18 | 170.28% |
| Bond/Credit Best - SPY Buy & Hold | 2.48% | -0.79% | 0.08 | 170.28% |
| Old Best + Bond/Credit Incremental - Existing Smooth Score Best Local | 0.56% | -0.28% | 0.03 | -59.44% |
| Old Best + Bond/Credit Incremental - Bond/Credit Smooth Score Best | 2.07% | 2.59% | 0.10 | 239.95% |

###### 7.2 Equity Curves

![Main Equity Curves](../plots/bond_credit_smooth_policy_v1_main_equity_curves.png)

##### 8. Vol-Matched and Static G/D Comparisons

| display_name | static_g_weight | final_wealth | cagr | ann_vol | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Target Bond/Credit Smooth Score |  | 4.25 | 17.73% | 19.49% | 0.94 | -34.50% | 0.51 | 170.28% | 49.62% |
| Vol-Matched Static G/D (52% G) | 52.00% | 4.11 | 17.30% | 19.47% | 0.92 | -33.48% | 0.52 | 0.00% | 52.00% |
| DD-Matched Static G/D (34% G) | 34.00% | 3.63 | 15.67% | 18.45% | 0.88 | -34.50% | 0.45 | 0.00% | 34.00% |
| Best Sharpe Static G/D (89% G) | 89.00% | 5.20 | 20.46% | 22.46% | 0.94 | -32.07% | 0.64 | 0.00% | 89.00% |
| Best CAGR Static under Target DD (100% G) | 100.00% | 5.55 | 21.34% | 23.53% | 0.94 | -34.35% | 0.62 | 0.00% | 100.00% |

![Static Comparison Equity Curves](../plots/bond_credit_smooth_policy_v1_static_comparison_equity_curves.png)

##### 9. OOS Validation: Expanding, Rolling, and Fixed Parameter

| display_name | start_date | end_date | cagr | ann_vol | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | final_wealth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Bond/Credit WF Expanding | 2018-06-28 | 2026-05-15 | 17.02% | 20.14% | 0.88 | -35.55% | 0.48 | 221.17% | 48.65% | 3.44 |
| Bond/Credit WF Rolling | 2018-06-28 | 2026-05-15 | 17.16% | 20.02% | 0.89 | -35.55% | 0.48 | 228.98% | 47.12% | 3.47 |
| Bond/Credit Fixed Parameter | 2018-06-28 | 2026-05-15 | 17.15% | 20.42% | 0.88 | -34.99% | 0.49 | 468.63% | 49.50% | 3.47 |
| Old+Credit WF Expanding | 2018-06-28 | 2026-05-15 | 19.83% | 19.74% | 1.02 | -32.36% | 0.61 | 388.44% | 43.26% | 4.15 |
| Old+Credit WF Rolling | 2018-06-28 | 2026-05-15 | 20.24% | 19.76% | 1.03 | -32.36% | 0.63 | 403.31% | 43.11% | 4.26 |
| Old+Credit Fixed Parameter | 2018-06-28 | 2026-05-15 | 19.56% | 19.52% | 1.01 | -32.54% | 0.60 | 412.32% | 42.74% | 4.07 |
| Existing Smooth Score Best Local | 2018-06-28 | 2026-05-15 | 19.93% | 19.92% | 1.01 | -31.63% | 0.63 | 449.41% | 44.35% | 4.17 |
| 50/50 G-D Buy & Hold | 2018-06-28 | 2026-05-15 | 17.10% | 20.00% | 0.89 | -33.59% | 0.51 | 0.00% | 50.00% | 3.46 |
| 100% G Buy & Hold | 2018-06-28 | 2026-05-15 | 21.13% | 24.38% | 0.91 | -34.35% | 0.62 | 0.00% | 100.00% | 4.51 |
| SPY Buy & Hold | 2018-06-28 | 2026-05-15 | 15.45% | 19.39% | 0.84 | -33.72% | 0.46 | 0.00% |  | 3.09 |

![OOS Validation Equity Curves](../plots/bond_credit_smooth_policy_v1_oos_validation_equity_curves.png)

##### 10. Post-2022 OOS Validation

| display_name | start_date | end_date | cagr | ann_vol | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | final_wealth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Bond/Credit WF Expanding | 2022-01-03 | 2026-05-15 | 13.39% | 18.33% | 0.78 | -25.14% | 0.53 | 101.55% | 49.38% | 1.73 |
| Bond/Credit WF Rolling | 2022-01-03 | 2026-05-15 | 13.83% | 17.97% | 0.81 | -24.55% | 0.56 | 119.91% | 45.97% | 1.76 |
| Bond/Credit Fixed Parameter | 2022-01-03 | 2026-05-15 | 13.95% | 18.42% | 0.80 | -25.13% | 0.56 | 129.02% | 49.68% | 1.76 |
| Old+Credit WF Expanding | 2022-01-03 | 2026-05-15 | 15.95% | 17.27% | 0.94 | -19.76% | 0.81 | 365.74% | 38.27% | 1.90 |
| Old+Credit WF Rolling | 2022-01-03 | 2026-05-15 | 16.12% | 17.28% | 0.95 | -19.45% | 0.83 | 382.49% | 37.51% | 1.92 |
| Old+Credit Fixed Parameter | 2022-01-03 | 2026-05-15 | 16.20% | 17.24% | 0.96 | -19.68% | 0.82 | 368.67% | 37.65% | 1.92 |
| Existing Smooth Score Best Local | 2022-01-03 | 2026-05-15 | 16.27% | 17.66% | 0.94 | -19.94% | 0.82 | 455.76% | 40.68% | 1.93 |
| 50/50 G-D Buy & Hold | 2022-01-03 | 2026-05-15 | 13.23% | 18.02% | 0.78 | -23.78% | 0.56 | 0.00% | 50.00% | 1.72 |
| 100% G Buy & Hold | 2022-01-03 | 2026-05-15 | 15.45% | 23.81% | 0.72 | -33.92% | 0.46 | 0.00% | 100.00% | 1.87 |
| SPY Buy & Hold | 2022-01-03 | 2026-05-15 | 12.21% | 17.68% | 0.74 | -24.50% | 0.50 | 0.00% |  | 1.65 |

![Post-2022 Validation Equity Curves](../plots/bond_credit_smooth_policy_v1_post2022_validation_equity_curves.png)

##### 11. Score Sorting Diagnostics

| score_quantile | n | start_date | end_date | realized_future_gd_mean_63d | realized_future_gd_median_63d | win_rate |
| --- | --- | --- | --- | --- | --- | --- |
| Q1 | 434 | 2017-07-12 | 2025-12-10 | 0.03% | 0.26% | 51.84% |
| Q2 | 434 | 2017-07-13 | 2026-01-13 | 0.66% | 1.54% | 58.99% |
| Q3 | 434 | 2017-07-07 | 2026-02-13 | 2.83% | 3.35% | 71.66% |
| Q4 | 434 | 2017-06-28 | 2026-02-05 | 2.39% | 3.40% | 64.98% |
| Q5 | 434 | 2017-07-03 | 2023-04-26 | 3.08% | 4.32% | 71.43% |

##### 12. Yearly Performance

| display_name | year | start_date | end_date | cagr | sharpe | max_drawdown | annual_turnover | avg_g_weight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 100% G Buy & Hold | 2017 | 2017-06-28 | 2017-12-29 | 29.53% | 2.73 | -2.40% | 0.00% | 100.00% |
| 100% G Buy & Hold | 2018 | 2018-01-02 | 2018-12-31 | -0.60% | 0.08 | -22.54% | 0.00% | 100.00% |
| 100% G Buy & Hold | 2019 | 2019-01-02 | 2019-12-31 | 41.00% | 2.27 | -9.27% | 0.00% | 100.00% |
| 100% G Buy & Hold | 2020 | 2020-01-02 | 2020-12-31 | 42.24% | 1.14 | -30.81% | 0.00% | 100.00% |
| 100% G Buy & Hold | 2021 | 2021-01-04 | 2021-12-31 | 30.41% | 1.57 | -9.83% | 0.00% | 100.00% |
| 100% G Buy & Hold | 2022 | 2022-01-03 | 2022-12-30 | -30.61% | -0.97 | -33.92% | 0.00% | 100.00% |
| 100% G Buy & Hold | 2023 | 2023-01-03 | 2023-12-29 | 48.31% | 2.43 | -10.69% | 0.00% | 100.00% |
| 100% G Buy & Hold | 2024 | 2024-01-02 | 2024-12-31 | 29.06% | 1.43 | -14.22% | 0.00% | 100.00% |
| 100% G Buy & Hold | 2025 | 2025-01-02 | 2025-12-31 | 22.00% | 0.92 | -24.06% | 0.00% | 100.00% |
| 100% G Buy & Hold | 2026 | 2026-01-02 | 2026-05-15 | 48.22% | 2.03 | -13.46% | 0.00% | 100.00% |
| 50/50 G-D Buy & Hold | 2017 | 2017-06-28 | 2017-12-29 | 27.03% | 3.35 | -2.08% | 0.00% | 50.00% |
| 50/50 G-D Buy & Hold | 2018 | 2018-01-02 | 2018-12-31 | -3.03% | -0.08 | -19.71% | 0.00% | 50.00% |
| 50/50 G-D Buy & Hold | 2019 | 2019-01-02 | 2019-12-31 | 32.90% | 2.19 | -8.03% | 0.00% | 50.00% |
| 50/50 G-D Buy & Hold | 2020 | 2020-01-02 | 2020-12-31 | 23.71% | 0.79 | -33.59% | 0.00% | 50.00% |
| 50/50 G-D Buy & Hold | 2021 | 2021-01-04 | 2021-12-31 | 31.04% | 2.08 | -4.92% | 0.00% | 50.00% |
| 50/50 G-D Buy & Hold | 2022 | 2022-01-03 | 2022-12-30 | -17.12% | -0.62 | -23.78% | 0.00% | 50.00% |
| 50/50 G-D Buy & Hold | 2023 | 2023-01-03 | 2023-12-29 | 28.40% | 1.93 | -9.73% | 0.00% | 50.00% |
| 50/50 G-D Buy & Hold | 2024 | 2024-01-02 | 2024-12-31 | 22.51% | 1.60 | -8.88% | 0.00% | 50.00% |
| 50/50 G-D Buy & Hold | 2025 | 2025-01-02 | 2025-12-31 | 17.46% | 0.94 | -19.66% | 0.00% | 50.00% |
| 50/50 G-D Buy & Hold | 2026 | 2026-01-02 | 2026-05-15 | 37.22% | 2.39 | -7.95% | 0.00% | 50.00% |
| Existing Smooth Score Best Local | 2017 | 2017-06-28 | 2017-12-29 | 23.19% | 2.92 | -2.03% | 656.03% | 47.83% |
| Existing Smooth Score Best Local | 2018 | 2018-01-02 | 2018-12-31 | -3.33% | -0.09 | -19.60% | 604.88% | 56.09% |
| Existing Smooth Score Best Local | 2019 | 2019-01-02 | 2019-12-31 | 35.12% | 2.17 | -8.38% | 533.41% | 64.38% |
| Existing Smooth Score Best Local | 2020 | 2020-01-02 | 2020-12-31 | 28.88% | 0.91 | -31.63% | 438.04% | 53.02% |
| Existing Smooth Score Best Local | 2021 | 2021-01-04 | 2021-12-31 | 31.65% | 2.26 | -4.72% | 268.14% | 24.39% |
| Existing Smooth Score Best Local | 2022 | 2022-01-03 | 2022-12-30 | -9.53% | -0.31 | -18.04% | 640.34% | 40.06% |
| Existing Smooth Score Best Local | 2023 | 2023-01-03 | 2023-12-29 | 29.38% | 1.97 | -9.59% | 362.57% | 40.82% |
| Existing Smooth Score Best Local | 2024 | 2024-01-02 | 2024-12-31 | 20.40% | 1.57 | -7.16% | 352.67% | 31.48% |
| Existing Smooth Score Best Local | 2025 | 2025-01-02 | 2025-12-31 | 20.53% | 1.03 | -19.94% | 409.22% | 49.67% |
| Existing Smooth Score Best Local | 2026 | 2026-01-02 | 2026-05-15 | 41.77% | 2.79 | -7.33% | 612.58% | 42.76% |
| Bond/Credit Smooth Score Best | 2017 | 2017-06-28 | 2017-12-29 | 28.01% | 3.43 | -2.12% | 278.98% | 50.66% |
| Bond/Credit Smooth Score Best | 2018 | 2018-01-02 | 2018-12-31 | -1.90% | -0.02 | -19.75% | 247.21% | 50.14% |
| Bond/Credit Smooth Score Best | 2019 | 2019-01-02 | 2019-12-31 | 33.64% | 2.24 | -7.75% | 161.79% | 46.86% |
| Bond/Credit Smooth Score Best | 2020 | 2020-01-02 | 2020-12-31 | 23.16% | 0.78 | -34.50% | 226.75% | 48.27% |
| Bond/Credit Smooth Score Best | 2021 | 2021-01-04 | 2021-12-31 | 31.26% | 2.06 | -4.90% | 169.24% | 52.41% |
| Bond/Credit Smooth Score Best | 2022 | 2022-01-03 | 2022-12-30 | -19.67% | -0.67 | -25.13% | 83.65% | 65.18% |
| Bond/Credit Smooth Score Best | 2023 | 2023-01-03 | 2023-12-29 | 33.83% | 2.18 | -9.62% | 154.60% | 54.88% |
| Bond/Credit Smooth Score Best | 2024 | 2024-01-02 | 2024-12-31 | 22.18% | 1.70 | -7.46% | 130.80% | 39.24% |
| Bond/Credit Smooth Score Best | 2025 | 2025-01-02 | 2025-12-31 | 18.54% | 1.02 | -18.61% | 125.58% | 41.00% |
| Bond/Credit Smooth Score Best | 2026 | 2026-01-02 | 2026-05-15 | 41.46% | 2.68 | -7.86% | 187.15% | 45.43% |
| Old Best + Bond/Credit Incremental | 2017 | 2017-06-28 | 2017-12-29 | 28.68% | 3.51 | -2.08% | 673.29% | 50.35% |
| Old Best + Bond/Credit Incremental | 2018 | 2018-01-02 | 2018-12-31 | -1.34% | 0.02 | -19.43% | 591.54% | 59.53% |
| Old Best + Bond/Credit Incremental | 2019 | 2019-01-02 | 2019-12-31 | 34.96% | 2.18 | -8.27% | 522.82% | 62.77% |
| Old Best + Bond/Credit Incremental | 2020 | 2020-01-02 | 2020-12-31 | 28.11% | 0.89 | -31.92% | 458.25% | 51.51% |
| Old Best + Bond/Credit Incremental | 2021 | 2021-01-04 | 2021-12-31 | 31.45% | 2.25 | -4.65% | 162.82% | 22.54% |
| Old Best + Bond/Credit Incremental | 2022 | 2022-01-03 | 2022-12-30 | -10.63% | -0.35 | -19.16% | 541.82% | 42.64% |
| Old Best + Bond/Credit Incremental | 2023 | 2023-01-03 | 2023-12-29 | 31.61% | 2.09 | -9.46% | 254.85% | 41.93% |
| Old Best + Bond/Credit Incremental | 2024 | 2024-01-02 | 2024-12-31 | 20.61% | 1.68 | -5.89% | 286.93% | 24.83% |
| Old Best + Bond/Credit Incremental | 2025 | 2025-01-02 | 2025-12-31 | 20.16% | 1.06 | -18.65% | 297.92% | 41.47% |
| Old Best + Bond/Credit Incremental | 2026 | 2026-01-02 | 2026-05-15 | 43.42% | 2.92 | -7.10% | 489.28% | 41.35% |

##### 13. Final Interpretation

- The bond/credit extension adds an economically interpretable credit-relief channel and a `rate relief × credit stress` interaction.
- The strict incremental branch tests whether those terms improve the already-selected old Best Local structure, instead of comparing a new score against the old score only.
- This report evaluates whether that additional information improves the deployable G/D smooth policy, not whether it creates a new standalone alpha factor.
- Results should be interpreted against the existing smooth-score benchmark, static G/D allocations, 100% G, SPY, and OOS validation paths.

##### 14. Output Files

- `/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/bond_credit_smooth_policy_v1/inputs/bond_credit_smooth_policy_v1_feature_panel.csv`
- `/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_config_grid.csv`
- `/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_grid_metrics.csv`
- `/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_selected_summary.csv`
- `/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_main_equity_curves.csv`
- `/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_oos_validation_summary.csv`
- `/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/bond_credit_smooth_policy_v1/tables/bond_credit_smooth_policy_v1_post2022_validation_summary.csv`


### 5.4 Joint Old/Credit Policy v1

#### Phase 1 Joint Old/Credit Policy v1 Report

This report tests a stricter joint-selection design. Unlike the previous `Old Best + Bond/Credit Incremental` experiment, the old score parameters are not fixed. The grid jointly selects the old smooth-score parameters and the bond/credit add-on parameters.

##### 1. Score Definition

```text
score = alpha*r + (1-alpha)*d
      + lambda_stress*(0.5*z_old_i1 + 0.5*z_old_i2)
      - lambda_crowded*(0.5*z_old_i3 + 0.5*z_old_i4)
      + lambda_credit*ce
      + lambda_interaction*z(r*cs)
```

- `r`: rate relief, `-z(10Y yield 21d change)`.
- `d`: SPY drawdown depth, `-z(SPY drawdown)`.
- `ce`: credit relief, `-z(BAA10Y spread 21d change)`.
- `cs`: credit stress level, `z(BAA10Y spread)`.
- `old_i1`: rate relief x high VIX.
- `old_i2`: high VIX x VIX relief.
- `old_i3`: growth extension x low VIX.
- `old_i4`: growth extension x low VIX x rate quiet.

##### 2. Parameter Grid

Total joint configurations tested: `1600`.

```text
alpha in {0.50, 0.67}
lambda_stress in {0.25, 0.50}
lambda_crowded in {0.05, 0.15}
lambda_credit in {0.00, 0.05, 0.10, 0.25, 0.50}
lambda_interaction in {0.00, 0.05, 0.10, 0.25, 0.50}
max_tilt in {0.30, 0.50}
tau_weight in {0.75, 1.00}
eta in {0.03, 0.05}
```

Selected local-best configuration:

| config_id | alpha | lambda_stress | lambda_crowded | lambda_credit | lambda_interaction | max_tilt | tau_weight | eta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau1.00_eta0.05 | 0.50 | 0.25 | 0.05 | 0.25 | 0.50 | 0.50 | 1.00 | 0.05 |

Top 10 local configurations at 10bp:

| config_id | cagr | ann_vol | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | selection_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau1.00_eta0.05 | 19.89% | 19.20% | 1.04 | -31.95% | 0.62 | 370.17% | 46.46% | 0.81 |
| joint_a0.50_ls0.25_lcrowd0.05_lcred0.10_li0.50_tilt0.50_tau0.75_eta0.05 | 19.88% | 19.27% | 1.04 | -31.86% | 0.62 | 406.99% | 44.31% | 0.81 |
| joint_a0.50_ls0.50_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau0.75_eta0.05 | 19.86% | 19.09% | 1.04 | -31.84% | 0.62 | 421.56% | 44.19% | 0.80 |
| joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau0.75_eta0.05 | 20.26% | 19.16% | 1.06 | -31.93% | 0.63 | 422.16% | 44.63% | 0.80 |
| joint_a0.50_ls0.50_lcrowd0.05_lcred0.10_li0.50_tilt0.50_tau0.75_eta0.05 | 19.80% | 19.14% | 1.04 | -31.92% | 0.62 | 410.23% | 43.72% | 0.80 |
| joint_a0.50_ls0.50_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau0.75_eta0.05 | 19.92% | 19.06% | 1.05 | -31.98% | 0.62 | 422.95% | 43.68% | 0.80 |
| joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau0.75_eta0.05 | 20.03% | 19.20% | 1.05 | -31.74% | 0.63 | 470.13% | 45.49% | 0.80 |
| joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau1.00_eta0.05 | 19.71% | 19.22% | 1.03 | -31.80% | 0.62 | 412.95% | 46.92% | 0.80 |
| joint_a0.50_ls0.50_lcrowd0.05_lcred0.05_li0.50_tilt0.50_tau0.75_eta0.05 | 19.70% | 19.16% | 1.03 | -31.90% | 0.62 | 407.25% | 43.73% | 0.80 |
| joint_a0.50_ls0.50_lcrowd0.05_lcred0.25_li0.10_tilt0.50_tau0.75_eta0.05 | 19.70% | 19.13% | 1.04 | -31.80% | 0.62 | 443.74% | 44.72% | 0.79 |

##### 3. Local Best Comparison

| display_name | start_date | end_date | cagr | ann_vol | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | final_wealth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Joint Local Best | 2017-06-28 | 2026-05-15 | 19.89% | 19.20% | 1.04 | -31.95% | 0.62 | 370.17% | 46.46% | 4.99 |
| Old Best + Bond/Credit Incremental | 2017-06-28 | 2026-05-15 | 19.80% | 19.14% | 1.04 | -31.92% | 0.62 | 410.23% | 43.72% | 4.96 |
| Existing Smooth Score Best Local | 2017-06-28 | 2026-05-15 | 19.24% | 19.29% | 1.01 | -31.63% | 0.61 | 469.67% | 45.06% | 4.76 |
| 50/50 G-D Buy & Hold | 2017-06-28 | 2026-05-15 | 17.12% | 19.34% | 0.91 | -33.59% | 0.51 | 0.00% | 50.00% | 4.06 |
| 100% G Buy & Hold | 2017-06-28 | 2026-05-15 | 21.34% | 23.53% | 0.94 | -34.35% | 0.62 | 0.00% | 100.00% | 5.55 |
| SPY Buy & Hold | 2017-06-28 | 2026-05-15 | 15.25% | 18.74% | 0.85 | -33.72% | 0.45 | 0.00% |  | 3.52 |

Incremental comparisons:

| comparison | annualized_excess_return | max_dd_diff | sharpe_diff | turnover_diff |
| --- | --- | --- | --- | --- |
| Joint Local Best - Old Best + Bond/Credit Incremental | 0.09% | -0.03% | 0.00 | -40.06% |
| Joint Local Best - Existing Smooth Score Best Local | 0.65% | -0.31% | 0.03 | -99.50% |
| Joint Local Best - 50/50 G-D Buy & Hold | 2.77% | 1.64% | 0.13 | 370.17% |
| Joint Local Best - 100% G Buy & Hold | -1.45% | 2.40% | 0.10 | 370.17% |
| Joint Local Best - SPY Buy & Hold | 4.65% | 1.77% | 0.19 | 370.17% |

![Local Equity Curves](../plots/joint_old_credit_policy_v1_local_equity_curves.png)

##### 4. OOS Validation: Expanding and Rolling

| display_name | start_date | end_date | cagr | ann_vol | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | final_wealth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Joint WF Expanding | 2018-06-28 | 2026-05-15 | 18.93% | 19.62% | 0.98 | -33.25% | 0.57 | 280.43% | 42.77% | 3.91 |
| Joint WF Rolling | 2018-06-28 | 2026-05-15 | 19.69% | 19.59% | 1.02 | -33.25% | 0.59 | 301.39% | 43.91% | 4.11 |
| Old+Credit WF Expanding | 2018-06-28 | 2026-05-15 | 19.83% | 19.74% | 1.02 | -32.36% | 0.61 | 388.44% | 43.26% | 4.15 |
| Old+Credit WF Rolling | 2018-06-28 | 2026-05-15 | 20.24% | 19.76% | 1.03 | -32.36% | 0.63 | 403.31% | 43.11% | 4.26 |
| Existing Smooth Score Best Local | 2018-06-28 | 2026-05-15 | 19.93% | 19.92% | 1.01 | -31.63% | 0.63 | 449.41% | 44.35% | 4.17 |
| 50/50 G-D Buy & Hold | 2018-06-28 | 2026-05-15 | 17.10% | 20.00% | 0.89 | -33.59% | 0.51 | 0.00% | 50.00% | 3.46 |
| 100% G Buy & Hold | 2018-06-28 | 2026-05-15 | 21.13% | 24.38% | 0.91 | -34.35% | 0.62 | 0.00% | 100.00% | 4.51 |
| SPY Buy & Hold | 2018-06-28 | 2026-05-15 | 15.45% | 19.39% | 0.84 | -33.72% | 0.46 | 0.00% |  | 3.09 |

![OOS Equity Curves](../plots/joint_old_credit_policy_v1_oos_equity_curves.png)

OOS incremental comparisons:

| comparison | annualized_excess_return | max_dd_diff | sharpe_diff | turnover_diff |
| --- | --- | --- | --- | --- |
| Joint WF Expanding - Old+Credit WF Expanding | -0.90% | -0.89% | -0.03 | -108.01% |
| Joint WF Rolling - Old+Credit WF Rolling | -0.55% | -0.89% | -0.02 | -101.92% |
| Joint WF Rolling - Existing Smooth Score Best Local | -0.24% | -1.62% | 0.00 | -148.02% |
| Joint WF Rolling - 50/50 G-D Buy & Hold | 2.59% | 0.34% | 0.13 | 301.39% |
| Joint WF Rolling - 100% G Buy & Hold | -1.44% | 1.09% | 0.11 | 301.39% |

##### 5. Walk-Forward Selection Frequency

| mode | selected_config_id | n_blocks |
| --- | --- | --- |
| expanding | joint_a0.50_ls0.50_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau1.00_eta0.05 | 8 |
| expanding | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau1.00_eta0.05 | 8 |
| expanding | joint_a0.50_ls0.50_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau0.75_eta0.05 | 6 |
| expanding | joint_a0.50_ls0.25_lcrowd0.05_lcred0.50_li0.50_tilt0.30_tau1.00_eta0.03 | 5 |
| expanding | joint_a0.50_ls0.50_lcrowd0.05_lcred0.10_li0.50_tilt0.30_tau1.00_eta0.03 | 2 |
| expanding | joint_a0.67_ls0.50_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau0.75_eta0.05 | 2 |
| expanding | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau1.00_eta0.05 | 1 |
| rolling | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau0.75_eta0.03 | 7 |
| rolling | joint_a0.50_ls0.25_lcrowd0.05_lcred0.50_li0.50_tilt0.30_tau1.00_eta0.03 | 5 |
| rolling | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.10_tilt0.50_tau1.00_eta0.05 | 4 |
| rolling | joint_a0.67_ls0.25_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau1.00_eta0.05 | 3 |
| rolling | joint_a0.50_ls0.50_lcrowd0.05_lcred0.10_li0.50_tilt0.30_tau1.00_eta0.03 | 2 |
| rolling | joint_a0.50_ls0.50_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau1.00_eta0.05 | 2 |
| rolling | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau1.00_eta0.05 | 2 |
| rolling | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.10_tilt0.50_tau0.75_eta0.03 | 2 |
| rolling | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau1.00_eta0.03 | 2 |
| rolling | joint_a0.67_ls0.25_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau0.75_eta0.05 | 1 |
| rolling | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.50_tilt0.30_tau0.75_eta0.03 | 1 |
| rolling | joint_a0.50_ls0.25_lcrowd0.05_lcred0.10_li0.50_tilt0.30_tau0.75_eta0.03 | 1 |

##### 6. Interpretation

This branch answers whether the credit extension should be treated as a small overlay to the old Best Local score or whether the full old/credit score should be jointly reselected. The local-best result shows that joint selection can slightly improve the in-sample/local objective and reduce turnover versus the fixed old-plus-credit overlay. However, the OOS results are stricter: the jointly selected expanding and rolling policies do not clearly dominate the prior fixed Old+Credit walk-forward policies. The current evidence therefore favors keeping the old Best structure plus credit overlay as the simpler and more robust implementation, while treating joint selection as a useful robustness check rather than the new mainline.


### 5.5 Joint Rolling Start-Date Sensitivity v1

#### Rolling Start-Date Sensitivity v1

This report tests whether the current Joint Old/Credit rolling validation is sensitive to the requested OOS start date and to 63-day block phase. The model, parameter grid, 756-day rolling training window, 63-day test block, 10bp transaction cost, and selection score are kept unchanged.

Important plot instruction: the common-window benchmark equity curve intentionally excludes `Old+Credit Rolling`; it compares only Joint Rolling start-date variants with 50/50 G-D, 100% G, and SPY.

##### 1. Tested Start Dates

| start_group | requested_start_date |
| --- | --- |
| annual | 2017-06-28 |
| annual | 2018-01-02 |
| annual_block_phase_anchor | 2018-06-28 |
| annual | 2019-01-02 |
| annual | 2020-01-02 |
| annual | 2021-01-04 |
| annual | 2022-01-03 |
| block_phase | 2018-07-30 |
| block_phase | 2018-08-29 |
| block_phase | 2018-09-28 |
| block_phase | 2018-10-29 |

##### 2. Start-to-End Joint Rolling Results

Each requested start date is run to the common dataset end. The `actual_start_date` can be later than the requested date when the rolling validation requires the initial training window.

| requested_start_date | actual_start_date | start_group | start_date | end_date | n_days | cagr | ann_vol | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | final_wealth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2017-06-28 | 2018-06-28 | annual | 2018-06-28 | 2026-05-15 | 1981 | 19.69% | 19.59% | 1.02 | -33.25% | 0.59 | 301.39% | 43.91% | 4.11 |
| 2018-01-02 | 2018-06-28 | annual | 2018-06-28 | 2026-05-15 | 1981 | 19.69% | 19.59% | 1.02 | -33.25% | 0.59 | 301.39% | 43.91% | 4.11 |
| 2018-06-28 | 2018-06-28 | annual_block_phase_anchor | 2018-06-28 | 2026-05-15 | 1981 | 19.69% | 19.59% | 1.02 | -33.25% | 0.59 | 301.39% | 43.91% | 4.11 |
| 2018-07-30 | 2018-07-30 | block_phase | 2018-07-30 | 2026-05-15 | 1960 | 19.26% | 19.65% | 1.00 | -33.25% | 0.58 | 301.81% | 43.93% | 3.94 |
| 2018-08-29 | 2018-08-29 | block_phase | 2018-08-29 | 2026-05-15 | 1938 | 18.10% | 19.71% | 0.94 | -33.25% | 0.54 | 311.74% | 42.43% | 3.59 |
| 2018-09-28 | 2018-09-28 | block_phase | 2018-09-28 | 2026-05-15 | 1917 | 18.83% | 19.84% | 0.97 | -33.25% | 0.57 | 301.88% | 43.27% | 3.72 |
| 2018-10-29 | 2018-10-29 | block_phase | 2018-10-29 | 2026-05-15 | 1896 | 20.69% | 19.80% | 1.05 | -33.25% | 0.62 | 309.79% | 43.75% | 4.12 |
| 2019-01-02 | 2019-01-02 | annual | 2019-01-02 | 2026-05-15 | 1853 | 21.95% | 19.63% | 1.11 | -33.25% | 0.66 | 306.11% | 42.97% | 4.30 |
| 2020-01-02 | 2020-01-02 | annual | 2020-01-02 | 2026-05-15 | 1601 | 20.03% | 20.38% | 1.00 | -33.25% | 0.60 | 326.37% | 40.00% | 3.19 |
| 2021-01-04 | 2021-01-04 | annual | 2021-01-04 | 2026-05-15 | 1348 | 18.65% | 16.51% | 1.12 | -18.69% | 1.00 | 312.06% | 38.06% | 2.50 |
| 2022-01-03 | 2022-01-03 | annual | 2022-01-03 | 2026-05-15 | 1096 | 15.89% | 17.29% | 0.94 | -18.69% | 0.85 | 312.80% | 39.28% | 1.90 |

![CAGR and Sharpe by Start Date](../plots/rolling_start_date_cagr_sharpe_bar.png)

![Max Drawdown and Turnover by Start Date](../plots/rolling_start_date_maxdd_turnover_bar.png)

##### 3. Common-Window Results

Common window: `2022-01-03` to `2026-05-15`. All rolling start-date variants and benchmarks are evaluated on the same dates.

| display_name | requested_start_date | actual_start_date | start_date | end_date | n_days | cagr | ann_vol | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | final_wealth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Joint Rolling 2017-06-28 | 2017-06-28 | 2018-06-28 | 2022-01-03 | 2026-05-15 | 1096 | 16.06% | 17.23% | 0.95 | -18.69% | 0.86 | 329.78% | 39.19% | 1.91 |
| Joint Rolling 2018-01-02 | 2018-01-02 | 2018-06-28 | 2022-01-03 | 2026-05-15 | 1096 | 16.06% | 17.23% | 0.95 | -18.69% | 0.86 | 329.78% | 39.19% | 1.91 |
| Joint Rolling 2018-06-28 | 2018-06-28 | 2018-06-28 | 2022-01-03 | 2026-05-15 | 1096 | 16.06% | 17.23% | 0.95 | -18.69% | 0.86 | 329.78% | 39.19% | 1.91 |
| Joint Rolling 2019-01-02 | 2019-01-02 | 2019-01-02 | 2022-01-03 | 2026-05-15 | 1096 | 15.55% | 17.19% | 0.93 | -18.69% | 0.83 | 323.45% | 38.42% | 1.88 |
| Joint Rolling 2020-01-02 | 2020-01-02 | 2020-01-02 | 2022-01-03 | 2026-05-15 | 1096 | 15.55% | 17.19% | 0.93 | -18.69% | 0.83 | 323.45% | 38.42% | 1.88 |
| Joint Rolling 2021-01-04 | 2021-01-04 | 2021-01-04 | 2022-01-03 | 2026-05-15 | 1096 | 15.89% | 17.29% | 0.94 | -18.69% | 0.85 | 312.80% | 39.28% | 1.90 |
| Joint Rolling 2022-01-03 | 2022-01-03 | 2022-01-03 | 2022-01-03 | 2026-05-15 | 1096 | 15.89% | 17.29% | 0.94 | -18.69% | 0.85 | 312.80% | 39.28% | 1.90 |
| Joint Rolling 2018-07-30 | 2018-07-30 | 2018-07-30 | 2022-01-03 | 2026-05-15 | 1096 | 16.08% | 17.27% | 0.95 | -18.72% | 0.86 | 327.43% | 39.97% | 1.91 |
| Joint Rolling 2018-08-29 | 2018-08-29 | 2018-08-29 | 2022-01-03 | 2026-05-15 | 1096 | 15.52% | 17.19% | 0.93 | -18.92% | 0.82 | 338.43% | 39.17% | 1.87 |
| Joint Rolling 2018-09-28 | 2018-09-28 | 2018-09-28 | 2022-01-03 | 2026-05-15 | 1096 | 15.57% | 17.18% | 0.93 | -18.71% | 0.83 | 318.64% | 38.47% | 1.88 |
| Joint Rolling 2018-10-29 | 2018-10-29 | 2018-10-29 | 2022-01-03 | 2026-05-15 | 1096 | 16.05% | 17.27% | 0.95 | -18.78% | 0.85 | 328.17% | 39.97% | 1.91 |
| 50/50 G-D Buy & Hold | benchmark | 2022-01-03 | 2022-01-03 | 2026-05-15 | 1096 | 13.23% | 18.02% | 0.78 | -23.78% | 0.56 | 0.00% | 50.00% | 1.72 |
| 100% G Buy & Hold | benchmark | 2022-01-03 | 2022-01-03 | 2026-05-15 | 1096 | 15.45% | 23.81% | 0.72 | -33.92% | 0.46 | 0.00% | 100.00% | 1.87 |
| SPY Buy & Hold | benchmark | 2022-01-03 | 2022-01-03 | 2026-05-15 | 1096 | 12.21% | 17.68% | 0.74 | -24.50% | 0.50 | 0.00% |  | 1.65 |

![Rolling Start-Date Equity Curves](../plots/rolling_start_date_equity_curves.png)

![Common-Window Rolling vs Benchmarks](../plots/rolling_start_date_vs_benchmarks_common_window.png)

##### 4. Fixed-Horizon Results

This table evaluates each start date over the first available 3-year or 5-year horizon when enough observations exist.

| horizon_years | requested_start_date | actual_start_date | start_date | end_date | n_days | cagr | ann_vol | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | final_wealth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 2017-06-28 | 2018-06-28 | 2018-06-28 | 2021-06-29 | 756 | 24.68% | 23.44% | 1.06 | -33.25% | 0.74 | 257.08% | 51.79% | 1.94 |
| 3 | 2018-01-02 | 2018-06-28 | 2018-06-28 | 2021-06-29 | 756 | 24.68% | 23.44% | 1.06 | -33.25% | 0.74 | 257.08% | 51.79% | 1.94 |
| 3 | 2018-06-28 | 2018-06-28 | 2018-06-28 | 2021-06-29 | 756 | 24.68% | 23.44% | 1.06 | -33.25% | 0.74 | 257.08% | 51.79% | 1.94 |
| 3 | 2019-01-02 | 2019-01-02 | 2019-01-02 | 2021-12-30 | 756 | 31.96% | 22.70% | 1.34 | -33.25% | 0.96 | 280.93% | 49.58% | 2.30 |
| 3 | 2020-01-02 | 2020-01-02 | 2020-01-02 | 2022-12-30 | 756 | 15.06% | 25.22% | 0.68 | -33.25% | 0.45 | 412.63% | 42.07% | 1.52 |
| 3 | 2021-01-04 | 2021-01-04 | 2021-01-04 | 2024-01-04 | 756 | 14.67% | 17.41% | 0.87 | -18.22% | 0.81 | 405.70% | 39.80% | 1.51 |
| 3 | 2022-01-03 | 2022-01-03 | 2022-01-03 | 2025-01-06 | 756 | 12.13% | 17.22% | 0.75 | -18.22% | 0.67 | 362.29% | 38.06% | 1.41 |
| 3 | 2018-07-30 | 2018-07-30 | 2018-07-30 | 2021-07-29 | 756 | 24.04% | 23.38% | 1.04 | -33.25% | 0.72 | 260.44% | 50.98% | 1.91 |
| 3 | 2018-08-29 | 2018-08-29 | 2018-08-29 | 2021-08-30 | 756 | 22.18% | 23.40% | 0.97 | -33.25% | 0.67 | 271.00% | 48.51% | 1.82 |
| 3 | 2018-09-28 | 2018-09-28 | 2018-09-28 | 2021-09-29 | 756 | 22.23% | 23.54% | 0.97 | -33.25% | 0.67 | 276.52% | 51.50% | 1.83 |
| 3 | 2018-10-29 | 2018-10-29 | 2018-10-29 | 2021-10-28 | 756 | 27.35% | 23.22% | 1.16 | -33.25% | 0.82 | 282.54% | 49.98% | 2.07 |
| 5 | 2017-06-28 | 2018-06-28 | 2018-06-28 | 2023-06-30 | 1260 | 18.33% | 21.93% | 0.88 | -33.25% | 0.55 | 346.74% | 48.94% | 2.32 |
| 5 | 2018-01-02 | 2018-06-28 | 2018-06-28 | 2023-06-30 | 1260 | 18.33% | 21.93% | 0.88 | -33.25% | 0.55 | 346.74% | 48.94% | 2.32 |
| 5 | 2018-06-28 | 2018-06-28 | 2018-06-28 | 2023-06-30 | 1260 | 18.33% | 21.93% | 0.88 | -33.25% | 0.55 | 346.74% | 48.94% | 2.32 |
| 5 | 2019-01-02 | 2019-01-02 | 2019-01-02 | 2024-01-03 | 1260 | 21.30% | 21.39% | 1.01 | -33.25% | 0.64 | 356.16% | 46.54% | 2.63 |
| 5 | 2020-01-02 | 2020-01-02 | 2020-01-02 | 2025-01-03 | 1260 | 18.98% | 21.13% | 0.93 | -33.25% | 0.57 | 356.21% | 39.68% | 2.38 |
| 5 | 2021-01-04 | 2021-01-04 | 2021-01-04 | 2026-01-08 | 1260 | 17.53% | 16.75% | 1.05 | -18.69% | 0.94 | 319.96% | 37.95% | 2.24 |
| 5 | 2018-07-30 | 2018-07-30 | 2018-07-30 | 2023-08-01 | 1260 | 18.40% | 21.88% | 0.88 | -33.25% | 0.55 | 350.50% | 48.53% | 2.33 |
| 5 | 2018-08-29 | 2018-08-29 | 2018-08-29 | 2023-08-31 | 1260 | 15.94% | 21.87% | 0.79 | -33.25% | 0.48 | 365.43% | 46.08% | 2.09 |
| 5 | 2018-09-28 | 2018-09-28 | 2018-09-28 | 2023-10-02 | 1260 | 15.84% | 21.97% | 0.78 | -33.25% | 0.48 | 351.32% | 47.58% | 2.09 |
| 5 | 2018-10-29 | 2018-10-29 | 2018-10-29 | 2023-10-31 | 1260 | 17.50% | 21.78% | 0.85 | -33.25% | 0.53 | 355.23% | 46.98% | 2.24 |

##### 5. Parameter Selection Stability

| requested_start_date | actual_start_date | start_group | n_blocks | unique_selected_configs | switch_count | most_frequent_config | most_frequent_blocks | most_frequent_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2017-06-28 | 2018-06-28 | annual | 32 | 12 | 14 | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau0.75_eta0.03 | 7 | 21.88% |
| 2018-01-02 | 2018-06-28 | annual | 32 | 12 | 14 | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau0.75_eta0.03 | 7 | 21.88% |
| 2018-06-28 | 2018-06-28 | annual_block_phase_anchor | 32 | 12 | 14 | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau0.75_eta0.03 | 7 | 21.88% |
| 2019-01-02 | 2019-01-02 | annual | 30 | 14 | 17 | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau0.75_eta0.03 | 5 | 16.67% |
| 2020-01-02 | 2020-01-02 | annual | 26 | 13 | 15 | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau0.75_eta0.03 | 5 | 19.23% |
| 2021-01-04 | 2021-01-04 | annual | 22 | 12 | 13 | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau0.75_eta0.03 | 6 | 27.27% |
| 2022-01-03 | 2022-01-03 | annual | 18 | 10 | 10 | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau0.75_eta0.03 | 6 | 33.33% |
| 2018-07-30 | 2018-07-30 | block_phase | 32 | 14 | 20 | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau0.75_eta0.03 | 7 | 21.88% |
| 2018-08-29 | 2018-08-29 | block_phase | 31 | 16 | 21 | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau0.75_eta0.03 | 7 | 22.58% |
| 2018-09-28 | 2018-09-28 | block_phase | 31 | 15 | 19 | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau0.75_eta0.03 | 5 | 16.13% |
| 2018-10-29 | 2018-10-29 | block_phase | 31 | 15 | 21 | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau0.75_eta0.03 | 7 | 22.58% |

##### 6. Interpretation

- Start-to-end CAGR ranges from `15.89%` to `21.95%` and Sharpe ranges from `0.94` to `1.12`. This range is partly driven by market-period inclusion: later starts exclude the COVID crash/rebound and shorten the sample.
- On the strict common window `2022-01-03` to `2026-05-15`, Joint Rolling variants are much tighter: CAGR ranges from `15.52%` to `16.08%`, Sharpe ranges from `0.93` to `0.95`, and max drawdown ranges from `-18.92%` to `-18.69%`.
- On the common window, the Joint Rolling variants are above 50/50 G-D buy-and-hold (`13.23%` CAGR, `0.78` Sharpe) and SPY (`12.21%` CAGR, `0.74` Sharpe). They are also slightly above 100% G on CAGR while carrying lower volatility and much smaller max drawdown.
- The block-phase tests around 2018 show some start-to-end dispersion, but the common-window results are close. This suggests the rolling result is not mainly an artifact of the original `2018-06-28` start date, although parameter selection itself remains path-dependent.
- The same most-frequent configuration appears across all start-date variants, but the number of unique selected configurations remains high. Therefore the strategy family is stable, while exact block-by-block parameter selection is not perfectly stable.
- The common-window figure intentionally excludes Old+Credit Rolling, following the requested plot scope.


### 5.6 Joint Expanding Start-Date Sensitivity v1

#### Expanding Start-Date Sensitivity v1

This report is the expanding-window counterpart to the rolling start-date sensitivity test. The model, full 1,600-configuration Joint Old/Credit grid, 63-day test block, 10bp transaction cost, and selection score are kept unchanged. Only the requested OOS start date and 63-day block phase are varied.

Important distinction: this is a start-date sensitivity test, not a parameter-grid sensitivity test. The parameter grid remains full-grid in every run.

##### 1. Tested Start Dates

| start_group | requested_start_date |
| --- | --- |
| annual | 2017-06-28 |
| annual | 2018-01-02 |
| annual_block_phase_anchor | 2018-06-28 |
| annual | 2019-01-02 |
| annual | 2020-01-02 |
| annual | 2021-01-04 |
| annual | 2022-01-03 |
| block_phase | 2018-07-30 |
| block_phase | 2018-08-29 |
| block_phase | 2018-09-28 |
| block_phase | 2018-10-29 |

##### 2. Start-to-End Joint Expanding Results

Each requested start date is run to the common dataset end. The `actual_start_date` can be later than the requested date when the validation requires the initial training window.

| requested_start_date | actual_start_date | start_group | start_date | end_date | n_days | cagr | ann_vol | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | final_wealth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2017-06-28 | 2018-06-28 | annual | 2018-06-28 | 2026-05-15 | 1981 | 18.93% | 19.62% | 0.98 | -33.25% | 0.57 | 280.43% | 42.77% | 3.91 |
| 2018-01-02 | 2018-06-28 | annual | 2018-06-28 | 2026-05-15 | 1981 | 18.93% | 19.62% | 0.98 | -33.25% | 0.57 | 280.43% | 42.77% | 3.91 |
| 2018-06-28 | 2018-06-28 | annual_block_phase_anchor | 2018-06-28 | 2026-05-15 | 1981 | 18.93% | 19.62% | 0.98 | -33.25% | 0.57 | 280.43% | 42.77% | 3.91 |
| 2018-07-30 | 2018-07-30 | block_phase | 2018-07-30 | 2026-05-15 | 1960 | 19.01% | 19.61% | 0.99 | -33.25% | 0.57 | 285.68% | 42.20% | 3.87 |
| 2018-08-29 | 2018-08-29 | block_phase | 2018-08-29 | 2026-05-15 | 1938 | 17.98% | 19.70% | 0.94 | -33.25% | 0.54 | 289.34% | 41.26% | 3.57 |
| 2018-09-28 | 2018-09-28 | block_phase | 2018-09-28 | 2026-05-15 | 1917 | 18.25% | 19.90% | 0.94 | -33.25% | 0.55 | 291.25% | 42.42% | 3.58 |
| 2018-10-29 | 2018-10-29 | block_phase | 2018-10-29 | 2026-05-15 | 1896 | 20.34% | 19.71% | 1.04 | -33.25% | 0.61 | 293.01% | 41.64% | 4.03 |
| 2019-01-02 | 2019-01-02 | annual | 2019-01-02 | 2026-05-15 | 1853 | 21.30% | 19.68% | 1.08 | -33.25% | 0.64 | 292.43% | 42.12% | 4.14 |
| 2020-01-02 | 2020-01-02 | annual | 2020-01-02 | 2026-05-15 | 1601 | 19.29% | 20.44% | 0.97 | -33.25% | 0.58 | 310.54% | 39.02% | 3.07 |
| 2021-01-04 | 2021-01-04 | annual | 2021-01-04 | 2026-05-15 | 1348 | 17.63% | 16.52% | 1.07 | -20.03% | 0.88 | 301.18% | 36.19% | 2.38 |
| 2022-01-03 | 2022-01-03 | annual | 2022-01-03 | 2026-05-15 | 1096 | 14.69% | 17.31% | 0.88 | -20.03% | 0.73 | 331.69% | 38.00% | 1.81 |

![CAGR and Sharpe by Start Date](../plots/expanding_start_date_cagr_sharpe_bar.png)

![Max Drawdown and Turnover by Start Date](../plots/expanding_start_date_maxdd_turnover_bar.png)

##### 3. Common-Window Results

Common window: `2022-01-03` to `2026-05-15`. All expanding start-date variants and benchmarks are evaluated on the same dates.

| display_name | requested_start_date | actual_start_date | start_date | end_date | n_days | cagr | ann_vol | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | final_wealth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Joint Expanding 2017-06-28 | 2017-06-28 | 2018-06-28 | 2022-01-03 | 2026-05-15 | 1096 | 14.72% | 17.31% | 0.88 | -20.41% | 0.72 | 323.83% | 38.13% | 1.82 |
| Joint Expanding 2018-01-02 | 2018-01-02 | 2018-06-28 | 2022-01-03 | 2026-05-15 | 1096 | 14.72% | 17.31% | 0.88 | -20.41% | 0.72 | 323.83% | 38.13% | 1.82 |
| Joint Expanding 2018-06-28 | 2018-06-28 | 2018-06-28 | 2022-01-03 | 2026-05-15 | 1096 | 14.72% | 17.31% | 0.88 | -20.41% | 0.72 | 323.83% | 38.13% | 1.82 |
| Joint Expanding 2019-01-02 | 2019-01-02 | 2019-01-02 | 2022-01-03 | 2026-05-15 | 1096 | 14.55% | 17.31% | 0.87 | -20.57% | 0.71 | 332.18% | 37.99% | 1.81 |
| Joint Expanding 2020-01-02 | 2020-01-02 | 2020-01-02 | 2022-01-03 | 2026-05-15 | 1096 | 14.55% | 17.31% | 0.87 | -20.57% | 0.71 | 332.18% | 37.99% | 1.81 |
| Joint Expanding 2021-01-04 | 2021-01-04 | 2021-01-04 | 2022-01-03 | 2026-05-15 | 1096 | 14.69% | 17.31% | 0.88 | -20.03% | 0.73 | 331.69% | 38.00% | 1.81 |
| Joint Expanding 2022-01-03 | 2022-01-03 | 2022-01-03 | 2022-01-03 | 2026-05-15 | 1096 | 14.69% | 17.31% | 0.88 | -20.03% | 0.73 | 331.69% | 38.00% | 1.81 |
| Joint Expanding 2018-07-30 | 2018-07-30 | 2018-07-30 | 2022-01-03 | 2026-05-15 | 1096 | 15.70% | 17.19% | 0.93 | -19.44% | 0.81 | 330.90% | 37.86% | 1.89 |
| Joint Expanding 2018-08-29 | 2018-08-29 | 2018-08-29 | 2022-01-03 | 2026-05-15 | 1096 | 15.11% | 17.18% | 0.90 | -20.76% | 0.73 | 330.69% | 37.45% | 1.84 |
| Joint Expanding 2018-09-28 | 2018-09-28 | 2018-09-28 | 2022-01-03 | 2026-05-15 | 1096 | 14.60% | 17.31% | 0.87 | -20.51% | 0.71 | 331.97% | 37.98% | 1.81 |
| Joint Expanding 2018-10-29 | 2018-10-29 | 2018-10-29 | 2022-01-03 | 2026-05-15 | 1096 | 15.52% | 17.11% | 0.93 | -20.26% | 0.77 | 333.88% | 37.37% | 1.87 |
| 50/50 G-D Buy & Hold | benchmark | 2022-01-03 | 2022-01-03 | 2026-05-15 | 1096 | 13.23% | 18.02% | 0.78 | -23.78% | 0.56 | 0.00% | 50.00% | 1.72 |
| 100% G Buy & Hold | benchmark | 2022-01-03 | 2022-01-03 | 2026-05-15 | 1096 | 15.45% | 23.81% | 0.72 | -33.92% | 0.46 | 0.00% | 100.00% | 1.87 |
| SPY Buy & Hold | benchmark | 2022-01-03 | 2022-01-03 | 2026-05-15 | 1096 | 12.21% | 17.68% | 0.74 | -24.50% | 0.50 | 0.00% |  | 1.65 |

![Expanding Start-Date Equity Curves](../plots/expanding_start_date_equity_curves.png)

![Common-Window Expanding vs Benchmarks](../plots/expanding_start_date_vs_benchmarks_common_window.png)

##### 4. Fixed-Horizon Results

| horizon_years | requested_start_date | actual_start_date | start_date | end_date | n_days | cagr | ann_vol | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | final_wealth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 2017-06-28 | 2018-06-28 | 2018-06-28 | 2021-06-29 | 756 | 24.61% | 23.44% | 1.06 | -33.25% | 0.74 | 244.20% | 51.67% | 1.93 |
| 3 | 2018-01-02 | 2018-06-28 | 2018-06-28 | 2021-06-29 | 756 | 24.61% | 23.44% | 1.06 | -33.25% | 0.74 | 244.20% | 51.67% | 1.93 |
| 3 | 2018-06-28 | 2018-06-28 | 2018-06-28 | 2021-06-29 | 756 | 24.61% | 23.44% | 1.06 | -33.25% | 0.74 | 244.20% | 51.67% | 1.93 |
| 3 | 2019-01-02 | 2019-01-02 | 2019-01-02 | 2021-12-30 | 756 | 31.89% | 22.70% | 1.33 | -33.25% | 0.96 | 235.07% | 48.14% | 2.29 |
| 3 | 2020-01-02 | 2020-01-02 | 2020-01-02 | 2022-12-30 | 756 | 14.18% | 25.33% | 0.65 | -33.25% | 0.43 | 363.79% | 41.39% | 1.49 |
| 3 | 2021-01-04 | 2021-01-04 | 2021-01-04 | 2024-01-04 | 756 | 13.51% | 17.41% | 0.82 | -20.03% | 0.67 | 332.58% | 36.38% | 1.46 |
| 3 | 2022-01-03 | 2022-01-03 | 2022-01-03 | 2025-01-06 | 756 | 10.77% | 17.29% | 0.68 | -20.03% | 0.54 | 356.32% | 36.62% | 1.36 |
| 3 | 2018-07-30 | 2018-07-30 | 2018-07-30 | 2021-07-29 | 756 | 23.73% | 23.39% | 1.03 | -33.25% | 0.71 | 242.71% | 50.35% | 1.89 |
| 3 | 2018-08-29 | 2018-08-29 | 2018-08-29 | 2021-08-30 | 756 | 22.22% | 23.40% | 0.98 | -33.25% | 0.67 | 248.30% | 48.24% | 1.83 |
| 3 | 2018-09-28 | 2018-09-28 | 2018-09-28 | 2021-09-29 | 756 | 22.00% | 23.55% | 0.96 | -33.25% | 0.66 | 246.43% | 50.06% | 1.82 |
| 3 | 2018-10-29 | 2018-10-29 | 2018-10-29 | 2021-10-28 | 756 | 27.15% | 23.22% | 1.15 | -33.25% | 0.82 | 242.66% | 48.59% | 2.06 |
| 5 | 2017-06-28 | 2018-06-28 | 2018-06-28 | 2023-06-30 | 1260 | 17.36% | 21.97% | 0.84 | -33.25% | 0.52 | 309.52% | 47.75% | 2.23 |
| 5 | 2018-01-02 | 2018-06-28 | 2018-06-28 | 2023-06-30 | 1260 | 17.36% | 21.97% | 0.84 | -33.25% | 0.52 | 309.52% | 47.75% | 2.23 |
| 5 | 2018-06-28 | 2018-06-28 | 2018-06-28 | 2023-06-30 | 1260 | 17.36% | 21.97% | 0.84 | -33.25% | 0.52 | 309.52% | 47.75% | 2.23 |
| 5 | 2019-01-02 | 2019-01-02 | 2019-01-02 | 2024-01-03 | 1260 | 20.53% | 21.44% | 0.98 | -33.25% | 0.62 | 307.67% | 45.03% | 2.54 |
| 5 | 2020-01-02 | 2020-01-02 | 2020-01-02 | 2025-01-03 | 1260 | 18.03% | 21.21% | 0.89 | -33.25% | 0.54 | 319.77% | 38.47% | 2.29 |
| 5 | 2021-01-04 | 2021-01-04 | 2021-01-04 | 2026-01-08 | 1260 | 16.42% | 16.75% | 0.99 | -20.03% | 0.82 | 296.43% | 35.87% | 2.14 |
| 5 | 2018-07-30 | 2018-07-30 | 2018-07-30 | 2023-08-01 | 1260 | 17.83% | 21.86% | 0.86 | -33.25% | 0.54 | 308.08% | 47.00% | 2.27 |
| 5 | 2018-08-29 | 2018-08-29 | 2018-08-29 | 2023-08-31 | 1260 | 15.61% | 21.89% | 0.77 | -33.25% | 0.47 | 318.43% | 45.29% | 2.07 |
| 5 | 2018-09-28 | 2018-09-28 | 2018-09-28 | 2023-10-02 | 1260 | 14.90% | 22.02% | 0.74 | -33.25% | 0.45 | 312.60% | 46.40% | 2.00 |
| 5 | 2018-10-29 | 2018-10-29 | 2018-10-29 | 2023-10-31 | 1260 | 16.78% | 21.71% | 0.82 | -33.25% | 0.50 | 312.86% | 45.11% | 2.17 |

##### 5. Parameter Selection Stability

| requested_start_date | actual_start_date | start_group | n_blocks | unique_selected_configs | switch_count | most_frequent_config | most_frequent_blocks | most_frequent_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2017-06-28 | 2018-06-28 | annual | 32 | 7 | 9 | joint_a0.50_ls0.50_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau1.00_eta0.05 | 8 | 25.00% |
| 2018-01-02 | 2018-06-28 | annual | 32 | 7 | 9 | joint_a0.50_ls0.50_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau1.00_eta0.05 | 8 | 25.00% |
| 2018-06-28 | 2018-06-28 | annual_block_phase_anchor | 32 | 7 | 9 | joint_a0.50_ls0.50_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau1.00_eta0.05 | 8 | 25.00% |
| 2019-01-02 | 2019-01-02 | annual | 30 | 7 | 13 | joint_a0.50_ls0.50_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau1.00_eta0.05 | 8 | 26.67% |
| 2020-01-02 | 2020-01-02 | annual | 26 | 6 | 11 | joint_a0.50_ls0.50_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau1.00_eta0.05 | 8 | 30.77% |
| 2021-01-04 | 2021-01-04 | annual | 22 | 5 | 10 | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau1.00_eta0.05 | 8 | 36.36% |
| 2022-01-03 | 2022-01-03 | annual | 18 | 5 | 10 | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau1.00_eta0.05 | 8 | 44.44% |
| 2018-07-30 | 2018-07-30 | block_phase | 32 | 7 | 9 | joint_a0.50_ls0.50_lcrowd0.05_lcred0.25_li0.25_tilt0.50_tau0.75_eta0.05 | 9 | 28.12% |
| 2018-08-29 | 2018-08-29 | block_phase | 31 | 8 | 11 | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau1.00_eta0.05 | 8 | 25.81% |
| 2018-09-28 | 2018-09-28 | block_phase | 31 | 8 | 14 | joint_a0.50_ls0.50_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau1.00_eta0.05 | 8 | 25.81% |
| 2018-10-29 | 2018-10-29 | block_phase | 31 | 7 | 10 | joint_a0.50_ls0.25_lcrowd0.05_lcred0.25_li0.50_tilt0.50_tau1.00_eta0.05 | 8 | 25.81% |

##### 6. Interpretation

- Start-to-end CAGR ranges from `14.69%` to `21.30%` and Sharpe ranges from `0.88` to `1.08`. This range is affected by sample-period composition, especially whether the run includes the COVID crash and rebound.
- On the strict common window `2022-01-03` to `2026-05-15`, Joint Expanding variants are tighter: CAGR ranges from `14.55%` to `15.70%`, Sharpe ranges from `0.87` to `0.93`, and max drawdown ranges from `-20.76%` to `-19.44%`.
- On the common window, the Joint Expanding variants are compared only against 50/50 G-D, 100% G, and SPY. The 50/50 benchmark has `13.23%` CAGR and `0.78` Sharpe; 100% G has `15.45%` CAGR and `0.72` Sharpe; SPY has `12.21%` CAGR and `0.74` Sharpe.
- Because expanding training uses all prior history, the selected parameter path is usually less volatile than rolling, but it can be more anchored to earlier regimes. This sensitivity test separates that issue from parameter-grid sensitivity.

##### 7. Output Files

- Start-to-end summary: `data/phase1/expanding_start_date_sensitivity_v1/tables/expanding_start_date_sensitivity_v1_start_to_end_summary.csv`
- Common-window summary: `data/phase1/expanding_start_date_sensitivity_v1/tables/expanding_start_date_sensitivity_v1_common_window_summary.csv`
- Selections: `data/phase1/expanding_start_date_sensitivity_v1/tables/expanding_start_date_sensitivity_v1_selections.csv`
- Common-window equity curves: `data/phase1/expanding_start_date_sensitivity_v1/tables/expanding_start_date_sensitivity_v1_common_window_equity_curves.csv`

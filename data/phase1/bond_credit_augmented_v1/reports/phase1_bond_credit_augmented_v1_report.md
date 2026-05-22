# Phase 1 Bond/Credit-Augmented Continuous Interaction v1

## 1. 本步边界

本实验把可对齐的债券/信用数据加入 Phase 1 连续变量择时诊断。它不重做 FF5 因子归因，也不生成新的交易策略；目标是回答债券/信用变量及其二阶、三阶交互项是否能解释或预测 future G-D。

本次排除 HY OAS 与 IG OAS：这两个 FRED 导出文件当前只覆盖 2023-05-22 之后，不能和 2017 起点主样本对齐。正式回归只使用 BAA/AAA spreads 与 HYG/LQD/SHY ETF 信用代理。

## 2. 数据与样本

- 63 日主样本：`2017-06-22` 到 `2026-02-13`，n=`2174`。
- 频率：全部整理为日频交易日面板。
- 因变量：`future_gd_return_21d / 63d / 126d`。
- 标准误：日频重叠标签使用 Newey-West/HAC，lag = horizon - 1；另做 non-overlap 63d 检查。

| column | start_date | end_date | n_obs |
| --- | --- | --- | --- |
| baa10y_spread | 2006-05-22 | 2026-05-15 | 5031 |
| aaa10y_spread | 2006-05-22 | 2026-05-15 | 5031 |
| baa_minus_aaa | 2006-05-22 | 2026-05-15 | 5031 |
| baa10y_change_21d | 2006-06-21 | 2026-05-15 | 5010 |
| hyg_close | 2012-01-03 | 2026-05-15 | 3615 |
| lqd_close | 2012-01-03 | 2026-05-15 | 3615 |
| shy_close | 2006-05-22 | 2026-05-15 | 5031 |
| hyg_drawdown_depth | 2012-06-28 | 2026-05-15 | 3490 |
| hyg_lqd_rel_21d | 2012-02-02 | 2026-05-15 | 3594 |
| lqd_shy_weakness_21d | 2012-02-02 | 2026-05-15 | 3594 |

## 3. 新增债券/信用变量

- `cs = z(BAA10Y spread)`：信用压力水平。
- `ce = -z(BAA10Y spread 21d change)`：信用利差收窄/信用缓和。
- `cg = z(BAA spread - AAA spread)`：信用质量差距。
- `hys = z(HYG 252d drawdown depth)`：高收益债 ETF 压力。
- `hyr = z(HYG/LQD 21d relative return)`：高收益信用相对投资级信用修复。
- `lqs = z(LQD/SHY 21d weakness)`：投资级信用相对短债走弱。

## 4. 通过标准

- Raw gate：63 日方向符合预设，经济幅度至少 1%，21 或 126 日至少一个方向一致，non-overlap 63 日不反向。
- Rate residual gate：先用 `r` 解释 future G-D，再检验候选项是否解释剩余部分。
- 覆盖率：日频 63 日样本至少 100 个非零观测，non-overlap 至少 5 个非零观测。
- 对没有明确经济方向的候选项，只作为观察项，不计入 final pass。

## 5. 总结

- 主效应通过：`d, g126, ce`
- 二阶/三阶最终通过：`r_x_cs`

整体含义：加入债券/信用后，可以检验信用 stress/relief 是否只是利率变量的影子，还是能提供 G-D timing 的增量。最终通过项需要同时通过 raw future G-D 和 rate-only residual。

## 6. 主效应 Gate

| variable | question | expected_sign | coef_63d | t_hac_63d | nonoverlap_coef_63d | economic_effect_63d | passes_gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| r | Rate relief: -z(10Y yield 21d change) | 1.0 | -0.25% | -0.30 | -0.88% | -0.25% | 否 |
| d | SPY drawdown depth: -z(SPY drawdown) | 1.0 | 12.67% | 3.51 | 10.12% | 12.67% | 是 |
| vh | High VIX: z(VIX 3Y percentile) |  | -1.44% | -2.07 | -2.96% | -1.44% | 否 |
| vr | VIX relief: -z(VIX 21d change) | 1.0 | -0.05% | -0.08 | -4.49% | -0.05% | 否 |
| g63 | G-D trailing 63d relative strength |  | 0.15% | 0.14 | -1.12% | 0.15% | 否 |
| g126 | G-D trailing 126d relative strength | -1.0 | -2.17% | -2.25 | -3.49% | -2.17% | 是 |
| cs | Credit stress level: z(BAA-10Y spread) |  | 2.70% | 1.12 | 1.84% | 2.70% | 否 |
| ce | Credit relief: -z(BAA-10Y spread 21d change) | 1.0 | 1.31% | 1.70 | 0.14% | 1.31% | 是 |
| cg | Credit quality gap: z(BAA spread - AAA spread) |  | 2.72% | 1.05 | 4.14% | 2.72% | 否 |
| hys | HY ETF stress: z(HYG 252d drawdown depth) |  | -6.81% | -3.94 | -6.25% | -6.81% | 否 |
| hyr | HY ETF relief: z(HYG/LQD 21d relative return) | 1.0 | -2.14% | -2.41 | -2.68% | -2.14% | 否 |
| lqs | IG credit stress: z(LQD/SHY 21d weakness) |  | 0.75% | 1.07 | -3.43% | 0.75% | 否 |

## 7. 分组通过数量

| group | n | raw_pass_n | resid_pass_n | final_pass_n |
| --- | --- | --- | --- | --- |
| 1_all_pairwise_directional | 66 | 1 | 3 | 1 |
| 2_positive_part_bond_credit | 14 | 0 | 0 | 0 |
| 3_three_way_bond_credit | 10 | 0 | 0 | 0 |

## 8. 最终通过项

| group | variable | question | expected_sign | coef_63d | t_hac_63d | nonoverlap_coef_63d | raw_pass | resid_coef_63d | resid_t_63d | resid_nonoverlap_coef_63d | resid_pass | final_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1_all_pairwise_directional | r_x_cs | Rate relief: -z(10Y yield 21d change) × Credit stress level: z(BAA-10Y spread) | 1.0 | 1.71% | 1.51 | 2.46% | 是 | 2.07% | 2.36 | 2.97% | 是 | 是 |

## 9. Raw 通过但 residual 未最终通过

无可用结果。

## 10. 63 日绝对 HAC t 值最高的观察项

| group | variable | question | expected_sign | coef_63d | t_hac_63d | nonoverlap_coef_63d | resid_coef_63d | resid_t_63d | final_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1_all_pairwise_directional | g63_x_cs | G-D trailing 63d relative strength × Credit stress level: z(BAA-10Y spread) |  | 5.60% | 5.49 | 8.73% | 5.46% | 5.22 | 否 |
| 2_positive_part_bond_credit | growth_ext_pos_x_credit_stress_pos | Growth extended in credit stress | -1.0 | 11.97% | 4.75 | 17.68% | 11.69% | 4.98 | 否 |
| 1_all_pairwise_directional | vh_x_g63 | High VIX: z(VIX 3Y percentile) × G-D trailing 63d relative strength |  | 2.48% | 4.39 | 3.76% | 2.29% | 3.90 | 否 |
| 3_three_way_bond_credit | growth_weak_pos_x_hy_relief_pos_x_rate_relief_pos | Growth weak × HY relief × rate relief | 1.0 | -13.68% | -4.26 | 0.00% | -15.46% | -5.28 | 否 |
| 2_positive_part_bond_credit | growth_ext_pos_x_hy_stress_pos | Growth extended in HY stress | -1.0 | 5.08% | 4.21 | 8.86% | 4.82% | 4.40 | 否 |
| 1_all_pairwise_directional | g126_x_cs | G-D trailing 126d relative strength × Credit stress level: z(BAA-10Y spread) |  | 5.26% | 3.94 | 4.06% | 5.11% | 3.87 | 否 |
| 1_all_pairwise_directional | cs_x_hys | Credit stress level: z(BAA-10Y spread) × HY ETF stress: z(HYG 252d drawdown depth) |  | 2.67% | 3.73 | 5.53% | 2.41% | 3.56 | 否 |
| 2_positive_part_bond_credit | credit_stress_pos_x_drawdown_pos | Credit stress inside market drawdown |  | 9.59% | 3.40 | 20.35% | 8.85% | 3.28 | 否 |
| 1_all_pairwise_directional | vh_x_g126 | High VIX: z(VIX 3Y percentile) × G-D trailing 126d relative strength |  | 2.05% | 3.40 | 2.16% | 1.74% | 2.91 | 否 |
| 1_all_pairwise_directional | cs_x_cg | Credit stress level: z(BAA-10Y spread) × Credit quality gap: z(BAA spread - AAA spread) |  | 4.04% | 3.04 | 11.44% | 4.23% | 3.43 | 否 |
| 1_all_pairwise_directional | cg_x_hys | Credit quality gap: z(BAA spread - AAA spread) × HY ETF stress: z(HYG 252d drawdown depth) |  | 2.82% | 2.88 | 6.74% | 2.91% | 3.16 | 否 |
| 1_all_pairwise_directional | ce_x_lqs | Credit relief: -z(BAA-10Y spread 21d change) × IG credit stress: z(LQD/SHY 21d weakness) | 1.0 | -0.38% | -2.67 | -1.32% | -0.26% | -1.98 | 否 |
| 1_all_pairwise_directional | d_x_cs | SPY drawdown depth: -z(SPY drawdown) × Credit stress level: z(BAA-10Y spread) |  | 4.46% | 2.66 | 7.90% | 3.99% | 2.46 | 否 |
| 1_all_pairwise_directional | cs_x_lqs | Credit stress level: z(BAA-10Y spread) × IG credit stress: z(LQD/SHY 21d weakness) |  | 1.00% | 2.52 | 3.99% | 0.69% | 1.88 | 否 |
| 3_three_way_bond_credit | growth_ext_pos_x_credit_stress_pos_x_rate_headwind_pos | Growth extended × credit stress × rate headwind | -1.0 | 17.20% | 2.47 | -51.63% | 17.42% | 2.57 | 否 |
| 1_all_pairwise_directional | d_x_ce | SPY drawdown depth: -z(SPY drawdown) × Credit relief: -z(BAA-10Y spread 21d change) | 1.0 | -1.85% | -2.45 | -4.28% | -1.79% | -2.34 | 否 |
| 1_all_pairwise_directional | g126_x_hys | G-D trailing 126d relative strength × HY ETF stress: z(HYG 252d drawdown depth) |  | 1.42% | 2.33 | 1.94% | 1.24% | 1.90 | 否 |
| 1_all_pairwise_directional | r_x_lqs | Rate relief: -z(10Y yield 21d change) × IG credit stress: z(LQD/SHY 21d weakness) | 1.0 | 0.62% | 2.31 | 3.35% | 0.49% | 1.85 | 否 |
| 2_positive_part_bond_credit | credit_stress_pos_x_credit_relief_pos | High credit spread with credit-spread tightening | 1.0 | 5.26% | 2.25 | 21.55% | 3.84% | 1.81 | 否 |
| 1_all_pairwise_directional | ce_x_hys | Credit relief: -z(BAA-10Y spread 21d change) × HY ETF stress: z(HYG 252d drawdown depth) | 1.0 | -0.67% | -2.23 | -1.65% | -0.64% | -2.16 | 否 |

## 11. 输出文件

- 输入面板：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/bond_credit_augmented_v1/inputs/phase1_bond_credit_augmented_v1_panel.csv`
- 候选交互项：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/bond_credit_augmented_v1/tables/bond_credit_augmented_v1_candidate_interactions.csv`
- 系数长表：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/bond_credit_augmented_v1/tables/bond_credit_augmented_v1_coefficients.csv`
- 模型摘要：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/bond_credit_augmented_v1/tables/bond_credit_augmented_v1_model_summary.csv`
- 主效应 gate：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/bond_credit_augmented_v1/tables/bond_credit_augmented_v1_main_effect_gate.csv`
- 交互项 gate：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1/phase1_2016_full_archive/data/phase1/bond_credit_augmented_v1/tables/bond_credit_augmented_v1_interaction_gate.csv`

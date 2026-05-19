# 第一阶段 Smooth Continuous Score Policy v1 报告

## 1. 本步目标

本步不再找变量，而是检验 `TNX + SPY drawdown + 平滑交互项` 能否改善 G/D 动态配置。
所有策略都使用连续 score、tanh 仓位映射和 EWMA 权重平滑；没有分位调仓、硬 if 规则或最小调仓阈值。

## 2. 样本与口径

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

## 3. 2016 起点全可用窗口主结果，10bp 成本后

| method | config_id | cagr | ann_vol | sharpe | sortino | max_drawdown | calmar | annual_turnover | avg_g_weight | selection_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 17.94% | 19.31% | 0.95 | 1.14 | -32.80% | 0.55 | 183.96% | 49.20% | 82.05% |
| traditional_smooth_score | trad_a0.50_ls0.10_lc0.05_tilt0.20_tau1.0_eta0.05 | 17.91% | 19.36% | 0.95 | 1.13 | -32.78% | 0.55 | 194.10% | 49.64% | 80.68% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.15_tilt0.20_tau1.0_eta0.05 | 17.89% | 19.32% | 0.95 | 1.13 | -32.84% | 0.54 | 186.35% | 48.77% | 78.64% |
| smooth_tnx_only | tnx_tilt0.20_tau1.5_eta0.05 | 17.38% | 18.80% | 0.95 | 1.12 | -32.82% | 0.53 | 155.81% | 49.24% | 64.77% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 17.38% | 18.80% | 0.95 | 1.12 | -32.72% | 0.53 | 197.01% | 49.07% | 60.91% |
| smooth_core_only | core_a0.67_tilt0.20_tau1.5_eta0.05 | 17.33% | 18.74% | 0.95 | 1.12 | -32.94% | 0.53 | 133.36% | 47.54% | 58.18% |
| smooth_core_only | core_a0.67_tilt0.20_tau1.0_eta0.05 | 17.34% | 18.71% | 0.95 | 1.12 | -32.85% | 0.53 | 171.05% | 46.71% | 57.50% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 17.29% | 18.68% | 0.95 | 1.12 | -32.99% | 0.52 | 138.50% | 45.50% | 52.50% |
| smooth_tnx_only | tnx_tilt0.20_tau1.5_eta0.15 | 17.22% | 18.83% | 0.94 | 1.11 | -32.58% | 0.53 | 322.31% | 49.30% | 45.68% |
| benchmark_100_d | benchmark_100_d | 12.15% | 17.12% | 0.76 | 0.86 | -36.71% | 0.33 | 0.00% | 0.00% |  |
| benchmark_100_g | benchmark_100_g | 21.72% | 22.97% | 0.97 | 1.20 | -34.35% | 0.63 | 0.00% | 100.00% |  |
| benchmark_50_50_gd | benchmark_50_50_gd | 17.15% | 18.88% | 0.93 | 1.10 | -33.59% | 0.51 | 0.00% | 50.00% |  |
| benchmark_spy | benchmark_spy | 15.25% | 18.29% | 0.87 | 1.00 | -33.72% | 0.45 | 0.00% |  |  |

## 4. 入选方法与 Buy-and-Hold 对齐统计

这一张表只保留每类方法的入选配置，并把 `100% G`、`100% D`、`50/50 G-D`、`SPY` 的 buy-and-hold 统计结果对齐到同图共同可用起点后展示。这样动态策略和静态基准在同一张对比图、同一张统计表中的开始交易时间完全一致。

| display_name | config_id | start_date | end_date | n_days | final_wealth | cagr | ann_vol | sharpe | sortino | max_drawdown | calmar | annual_turnover | avg_g_weight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Traditional Smooth Score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2017-06-28 | 2026-05-15 | 2233 | 4.28 | 17.94% | 19.31% | 0.95 | 1.14 | -32.80% | 0.55 | 183.96% | 49.20% |
| Smooth TNX-only | tnx_tilt0.20_tau1.0_eta0.05 | 2017-06-28 | 2026-05-15 | 2233 | 4.11 | 17.41% | 19.26% | 0.93 | 1.11 | -32.72% | 0.53 | 198.74% | 49.09% |
| Smooth Core-only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2017-06-28 | 2026-05-15 | 2233 | 4.11 | 17.40% | 19.13% | 0.93 | 1.11 | -32.99% | 0.53 | 141.47% | 45.78% |
| 50/50 G-D Buy & Hold | benchmark_50_50_gd | 2017-06-28 | 2026-05-15 | 2233 | 4.02 | 17.12% | 19.34% | 0.91 | 1.08 | -33.59% | 0.51 | 0.00% | 50.00% |
| 100% G Buy & Hold | benchmark_100_g | 2017-06-28 | 2026-05-15 | 2233 | 5.49 | 21.34% | 23.53% | 0.94 | 1.17 | -34.35% | 0.62 | 0.00% | 100.00% |
| 100% D Buy & Hold | benchmark_100_d | 2017-06-28 | 2026-05-15 | 2233 | 2.80 | 12.42% | 17.53% | 0.76 | 0.86 | -36.71% | 0.34 | 0.00% | 0.00% |
| SPY Buy & Hold | benchmark_spy | 2017-06-28 | 2026-05-15 | 2233 | 3.49 | 15.25% | 18.74% | 0.85 | 0.98 | -33.72% | 0.45 | 0.00% |  |

## 5. Vol-Matched 与静态 G/D 对照

这一节以补充网格中 10bp 主口径的最佳 local smooth score 为目标策略，比较同风险水平下的 `100% G` 缩放版本、等波动/等回撤静态 G-D、以及最优静态 G-D。
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

![Vol-Matched 与静态 G/D 对照资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_vol_matched_static_equity_curves.png)
图表时间范围：`2017-06-28` 到 `2026-05-15`。

## 6. Nested / Walk-Forward 与固定参数后验验证

这一节不再用全样本挑参数，也不使用 2021/2022 这类人为切点。Walk-forward 每次只用过去窗口选择 expanded local grid 里的参数，然后部署到未来 63 个交易日。固定参数验证使用最早完整 smooth score 样本中的首个训练窗口选参，然后从下一交易日开始后验验证。
- 最小训练窗口：`252` 个交易日。
- Walk-forward 测试块：`63` 个交易日。

### 6.1 Nested Walk-Forward

| validation_label | start_date | end_date | n_days | final_wealth | cagr | ann_vol | sharpe | sortino | max_drawdown | calmar | annual_turnover | avg_g_weight | ann_excess_vs_expanding_wf | max_dd_diff_vs_expanding_wf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Smooth Score WF Expanding | 2018-06-28 | 2026-05-15 | 1981 | 3.83 | 18.64% | 19.77% | 0.96 | 1.16 | -32.93% | 0.57 | 332.21% | 44.82% | 0.00% | 0.00% |
| Smooth Score WF Rolling | 2018-06-28 | 2026-05-15 | 1981 | 3.68 | 18.02% | 19.86% | 0.93 | 1.12 | -32.79% | 0.55 | 350.79% | 46.66% | -0.61% | 0.14% |
| 50/50 G-D | 2018-06-28 | 2026-05-15 | 1981 | 3.46 | 17.10% | 20.00% | 0.89 | 1.06 | -33.59% | 0.51 | 0.00% | 50.00% | -1.53% | -0.66% |
| 100% G | 2018-06-28 | 2026-05-15 | 1981 | 4.51 | 21.13% | 24.38% | 0.91 | 1.13 | -34.35% | 0.62 | 0.00% | 100.00% | 2.50% | -1.42% |
| 100% D | 2018-06-28 | 2026-05-15 | 1981 | 2.53 | 12.51% | 18.14% | 0.74 | 0.85 | -36.71% | 0.34 | 0.00% | 0.00% | -6.13% | -3.79% |
| SPY | 2018-06-28 | 2026-05-15 | 1981 | 3.09 | 15.45% | 19.39% | 0.84 | 0.98 | -33.72% | 0.46 | 0.00% |  | -3.19% | -0.79% |

![Nested Walk-Forward 资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_nested_walk_forward_equity_curves.png)
图表时间范围：`2018-06-28` 到 `2026-05-15`。

### 6.2 固定参数后验外样本验证

- 参数选择期：`2017-06-28` 到 `2018-06-27`；后验验证期从 `2018-06-28` 开始；训练窗口 `252` 个交易日。
- 固定参数配置：`local_a0.50_ls0.50_lc0.25_tilt0.20_tau1.50_eta0.03`

| validation_label | start_date | end_date | n_days | final_wealth | cagr | ann_vol | sharpe | sortino | max_drawdown | calmar | annual_turnover | avg_g_weight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fixed Parameter Earliest Holdout | 2018-06-28 | 2026-05-15 | 1981 | 3.64 | 17.86% | 19.90% | 0.93 | 1.11 | -33.19% | 0.54 | 88.36% | 48.63% |
| 50/50 G-D Holdout | 2018-06-28 | 2026-05-15 | 1981 | 3.46 | 17.10% | 20.00% | 0.89 | 1.06 | -33.59% | 0.51 | 0.00% | 50.00% |
| 100% G Holdout | 2018-06-28 | 2026-05-15 | 1981 | 4.51 | 21.13% | 24.38% | 0.91 | 1.13 | -34.35% | 0.62 | 0.00% | 100.00% |
| 100% D Holdout | 2018-06-28 | 2026-05-15 | 1981 | 2.53 | 12.51% | 18.14% | 0.74 | 0.85 | -36.71% | 0.34 | 0.00% | 0.00% |
| SPY Holdout | 2018-06-28 | 2026-05-15 | 1981 | 3.09 | 15.45% | 19.39% | 0.84 | 0.98 | -33.72% | 0.46 | 0.00% |  |

![固定参数后验验证资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_fixed_parameter_holdout_equity_curves.png)
图表时间范围：`2018-06-28` 到 `2026-05-15`。

## 7. Supplementary Extreme-Tilt Grid

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

## 8. Expanded Local Grid

第二轮按你的扩展网格运行：`alpha ∈ {0.50,0.67}`、`lambda_stress ∈ {0.25,0.50}`、`lambda_crowded ∈ {0.05,0.15,0.25}`、`max_tilt ∈ {20%,30%,40%,50%}`、`tau_weight ∈ {0.75,1.0,1.5}`、`eta ∈ {0.03,0.05,0.10}`。主结论看 10bp，20bp 作为压力测试。

### 8.1 10bp 主口径 Top 10

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

### 8.2 20bp 压力测试 Top 10

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

### 8.3 10bp 入选局部网格配置的成本敏感性：`local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05`

| cost_bps | final_wealth | cagr | sharpe | max_drawdown | calmar | annual_turnover | ann_excess_vs_50_50 | ann_excess_vs_100_g |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 4.96 | 19.80% | 1.03 | -31.59% | 0.63 | 469.67% | 2.25% | -2.19% |
| 5 | 4.86 | 19.52% | 1.02 | -31.61% | 0.62 | 469.67% | 2.01% | -2.42% |
| 10 | 4.76 | 19.24% | 1.01 | -31.63% | 0.61 | 469.67% | 1.78% | -2.66% |
| 20 | 4.56 | 18.68% | 0.98 | -31.67% | 0.59 | 469.67% | 1.31% | -3.13% |

### 8.4 补充网格资金曲线

下面两张图把补充网格的资金曲线单独列出：第一张比较固定结构下不同 `max_tilt`，第二张比较局部网格最佳配置与 buy-and-hold 基准。
- 局部网格最佳配置：`local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05`

![Supplementary Extreme Tilt 资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_supplementary_extreme_tilt_equity_curves.png)
图表时间范围：`2017-06-28` 到 `2026-05-15`。

![Supplementary Best Local Grid 资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_supplementary_best_local_equity_curves.png)
图表时间范围：`2017-06-28` 到 `2026-05-15`。

## 9. 2016 起点全可用窗口增量比较，10bp 成本

| comparison | annualized_excess_return | tracking_error | information_ratio | max_dd_diff | turnover_diff |
| --- | --- | --- | --- | --- | --- |
| Traditional smooth score - smooth TNX-only | 0.46% | 0.79% | 0.58 | -0.07% | -14.78% |
| Traditional smooth score - smooth core-only | 0.49% | 0.60% | 0.81 | 0.19% | 42.49% |
| Best smooth method - 50/50 | 0.68% | 1.33% | 0.52 | 0.79% | 183.96% |

## 10. Score 排序诊断

| method | config_id | Q1 | Q2 | Q3 | Q4 | Q5 | Q5_minus_Q1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | -0.68% | -0.00% | 0.93% | 3.49% | 5.24% | 5.92% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 0.02% | -0.25% | 1.16% | 2.48% | 5.57% | 5.56% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 0.04% | 0.66% | 1.90% | 2.52% | 3.86% | 3.82% |

## 11. 资金曲线对比

下面两张图都使用 `10bp` 成本，并先取图内所有曲线的共同可用日期区间，再统一 rebase 到 `1.0`。同一张图中的所有方法开始交易时间完全一致。

![共同起点所有方法资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_common_oos_equity_curves_all.png)
图表时间范围：`2017-06-28` 到 `2026-05-15`。

![G/D Buy and Hold 基础资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_common_oos_buy_hold_gd.png)
图表时间范围：`2017-06-28` 到 `2026-05-15`。

图中 `100% G Buy & Hold` 和 `100% D Buy & Hold` 是单纯买入并持有 G、D 篮子的基础对照；`50/50 G-D Buy & Hold` 是不择时的静态配置基准。

## 12. 共同起点年度表现，10bp 成本

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
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2017 | 26.19% | 3.40 | -2.13% | 80.79% | 40.65% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2018 | -3.61% | -0.12 | -19.32% | 111.71% | 42.52% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2019 | 32.28% | 2.15 | -8.00% | 154.35% | 48.73% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2020 | 24.44% | 0.81 | -32.99% | 128.98% | 48.70% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2021 | 31.40% | 2.18 | -4.65% | 96.36% | 41.42% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2022 | -14.61% | -0.52 | -21.64% | 202.32% | 46.58% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2023 | 28.78% | 1.95 | -9.75% | 186.30% | 48.94% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2024 | 21.69% | 1.57 | -8.73% | 163.65% | 45.65% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2025 | 18.01% | 0.96 | -19.58% | 130.66% | 47.22% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2026 | 35.75% | 2.43 | -7.63% | 111.46% | 43.42% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2017 | 26.17% | 3.27 | -2.09% | 168.89% | 48.51% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2018 | -3.57% | -0.12 | -19.51% | 181.31% | 46.56% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2019 | 33.21% | 2.17 | -8.20% | 189.59% | 55.11% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2020 | 25.63% | 0.83 | -32.72% | 156.96% | 51.42% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2021 | 31.57% | 2.16 | -4.79% | 168.72% | 46.35% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2022 | -14.74% | -0.55 | -22.10% | 251.96% | 42.79% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2023 | 26.89% | 1.86 | -9.80% | 248.86% | 47.25% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2024 | 22.10% | 1.53 | -9.53% | 227.69% | 51.41% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2025 | 17.54% | 0.93 | -20.14% | 185.53% | 52.39% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2026 | 35.48% | 2.34 | -7.76% | 185.55% | 48.32% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2017 | 25.51% | 3.18 | -2.06% | 238.76% | 49.79% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2018 | -3.26% | -0.09 | -19.73% | 236.57% | 52.52% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2019 | 33.72% | 2.19 | -8.18% | 204.08% | 55.62% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2020 | 25.86% | 0.84 | -32.80% | 153.40% | 51.56% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2021 | 31.45% | 2.18 | -4.65% | 117.07% | 42.19% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2022 | -14.63% | -0.52 | -21.68% | 243.31% | 47.76% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2023 | 29.21% | 1.98 | -9.68% | 171.42% | 48.25% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2024 | 21.99% | 1.59 | -8.60% | 165.99% | 45.69% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2025 | 18.67% | 0.98 | -19.84% | 150.36% | 50.46% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2026 | 37.79% | 2.48 | -7.73% | 188.37% | 47.11% |

## 13. 输出文件

- 特征面板：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/inputs/smooth_score_policy_v1_feature_panel.csv`
- 信号权重：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_signals.csv`
- 日收益：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_daily_returns.csv`
- 主策略表现：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_metrics.csv`
- 2016 起点主策略表现：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_metrics.csv`
- 入选方法与 buy-and-hold 对齐统计：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_selected_summary.csv`
- 增量比较：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_comparisons.csv`
- 2016 起点增量比较：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_comparisons.csv`
- 年度表现：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_yearly_metrics.csv`
- 共同起点年度表现：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_yearly_metrics.csv`
- score 诊断：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_score_diagnostics.csv`
- 2016 起点 score 诊断：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_score_diagnostics.csv`
- 共同起点资金曲线：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_equity_curves.csv`
- 补充 extreme/local tilt 配置：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_supplementary_tilt_config_grid.csv`
- 补充 extreme/local tilt 主表：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_supplementary_tilt_common_oos_summary.csv`
- 补充 extreme/local tilt 日收益：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_supplementary_tilt_common_oos_returns.csv`
- 补充 extreme/local tilt 资金曲线：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_supplementary_tilt_common_oos_equity_curves.csv`
- Vol-matched 与静态 G/D 对照表：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_vol_matched_static_comparison.csv`
- 静态 G/D 权重网格：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_static_gd_grid.csv`
- Vol-matched 与静态 G/D 资金曲线：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_vol_matched_static_equity_curves.csv`
- Nested walk-forward 选择记录：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_nested_walk_forward_selections.csv`
- Nested walk-forward 日收益：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_nested_walk_forward_returns.csv`
- Nested walk-forward 结果：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_nested_walk_forward_summary.csv`
- 固定参数后验验证日收益：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_fixed_parameter_holdout_returns.csv`
- 固定参数后验验证结果：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_fixed_parameter_holdout_summary.csv`
- 所有方法资金曲线图：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_common_oos_equity_curves_all.png`
- G/D buy-and-hold 基础曲线图：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_common_oos_buy_hold_gd.png`
- 补充 extreme tilt 曲线图：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_supplementary_extreme_tilt_equity_curves.png`
- 补充 local grid 曲线图：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_supplementary_best_local_equity_curves.png`
- Vol-matched 与静态 G/D 曲线图：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_vol_matched_static_equity_curves.png`
- Nested walk-forward 曲线图：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_nested_walk_forward_equity_curves.png`
- 固定参数后验验证曲线图：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_fixed_parameter_holdout_equity_curves.png`
- 所有保留表格与图像的起止日期已汇总到合并归档报告的 artifact date range 索引。

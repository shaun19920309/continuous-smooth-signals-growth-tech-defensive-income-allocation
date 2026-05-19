# 第一阶段 Smooth Continuous Score Policy v1 报告

## 1. 本步目标

本步不再找变量，而是检验 `TNX + SPY drawdown + 平滑交互项` 能否改善 G/D 动态配置。
所有策略都使用连续 score、tanh 仓位映射和 EWMA 权重平滑；没有分位调仓、硬 if 规则或最小调仓阈值。

## 2. 样本与口径

- G/D 日收益源样本：`2016-12-21` 到 `2026-05-15`，n=`2360`。
- 可用于 63 日目标诊断的样本：`2017-06-26` 到 `2026-02-13`，n=`1982`。
- Smooth score 完整特征样本：`2017-06-26` 到 `2026-05-15`，n=`2108`。
- 主策略比较从 G/D 最早共同可用日期开始：`2016-12-21` 到 `2026-05-15`。
- 注意：`gd_trailing_126d` 需要 126 个交易日 warmup，因此动态 smooth score 的实际可交易起点会晚于 2016-12-21；这不是中途截样，而是变量定义带来的自然 warmup。
- 信号在 t 日收盘后形成，t+1 日收益开始使用。
- 标准化均为 expanding z-score，不使用全样本 z-score。
- 本版报告只保留规则型 smooth score、补充 tilt 网格和 buy-and-hold 基准。
- 交易成本报告 `0bp`、`5bp`、`10bp`、`20bp`；成本按 `2 × |ΔG权重| × cost_bps / 10000` 扣除。

## 3. 2016 起点全可用窗口主结果，10bp 成本后

| method | config_id | cagr | ann_vol | sharpe | sortino | max_drawdown | calmar | annual_turnover | avg_g_weight | selection_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 17.86% | 19.45% | 0.94 | 1.13 | -32.84% | 0.54 | 183.63% | 48.50% | 79.55% |
| traditional_smooth_score | trad_a0.50_ls0.10_lc0.05_tilt0.20_tau1.0_eta0.05 | 17.82% | 19.50% | 0.94 | 1.12 | -32.81% | 0.54 | 192.10% | 48.93% | 77.50% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.15 | 17.82% | 19.56% | 0.94 | 1.12 | -32.44% | 0.55 | 364.77% | 48.49% | 76.36% |
| smooth_tnx_only | tnx_tilt0.20_tau1.5_eta0.05 | 17.35% | 18.80% | 0.95 | 1.12 | -32.82% | 0.53 | 155.90% | 49.24% | 68.41% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 17.35% | 18.81% | 0.95 | 1.12 | -32.72% | 0.53 | 197.11% | 49.08% | 64.55% |
| smooth_core_only | core_a0.67_tilt0.20_tau1.5_eta0.05 | 17.30% | 18.75% | 0.95 | 1.12 | -32.94% | 0.53 | 133.44% | 47.54% | 61.82% |
| smooth_core_only | core_a0.67_tilt0.20_tau1.0_eta0.05 | 17.31% | 18.72% | 0.95 | 1.12 | -32.85% | 0.53 | 171.14% | 46.71% | 61.36% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 17.26% | 18.69% | 0.95 | 1.12 | -32.99% | 0.52 | 138.58% | 45.50% | 57.50% |
| smooth_tnx_only | tnx_tilt0.20_tau1.5_eta0.15 | 17.19% | 18.84% | 0.94 | 1.11 | -32.58% | 0.53 | 322.36% | 49.31% | 48.64% |
| benchmark_100_d | benchmark_100_d | 12.13% | 17.13% | 0.75 | 0.86 | -36.71% | 0.33 | 0.00% | 0.00% |  |
| benchmark_100_g | benchmark_100_g | 21.66% | 22.98% | 0.97 | 1.20 | -34.35% | 0.63 | 0.00% | 100.00% |  |
| benchmark_50_50_gd | benchmark_50_50_gd | 17.11% | 18.89% | 0.93 | 1.10 | -33.59% | 0.51 | 0.00% | 50.00% |  |
| benchmark_spy | benchmark_spy | 15.25% | 18.29% | 0.87 | 1.00 | -33.72% | 0.45 | 0.00% |  |  |

## 4. 入选方法与 Buy-and-Hold 对齐统计

这一张表只保留每类方法的入选配置，并把 `100% G`、`100% D`、`50/50 G-D`、`SPY` 的 buy-and-hold 统计结果放在同一个 2016 起点全可用窗口下展示。动态策略因特征 warmup 可能自然晚于买入持有基准。

| display_name | config_id | start_date | end_date | n_days | final_wealth | cagr | ann_vol | sharpe | sortino | max_drawdown | calmar | annual_turnover | avg_g_weight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Traditional Smooth Score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2017-06-28 | 2026-05-15 | 2105 | 3.91 | 17.86% | 19.45% | 0.94 | 1.13 | -32.84% | 0.54 | 183.63% | 48.50% |
| Smooth TNX-only | tnx_tilt0.20_tau1.0_eta0.05 | 2016-12-21 | 2026-05-15 | 2360 | 4.48 | 17.35% | 18.81% | 0.95 | 1.12 | -32.72% | 0.53 | 197.11% | 49.08% |
| Smooth Core-only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2016-12-21 | 2026-05-15 | 2360 | 4.45 | 17.26% | 18.69% | 0.95 | 1.12 | -32.99% | 0.52 | 138.58% | 45.50% |
| 50/50 G-D Buy & Hold | benchmark_50_50_gd | 2016-12-21 | 2026-05-15 | 2360 | 4.40 | 17.11% | 18.89% | 0.93 | 1.10 | -33.59% | 0.51 | 0.00% | 50.00% |
| 100% G Buy & Hold | benchmark_100_g | 2016-12-21 | 2026-05-15 | 2360 | 6.28 | 21.66% | 22.98% | 0.97 | 1.20 | -34.35% | 0.63 | 0.00% | 100.00% |
| 100% D Buy & Hold | benchmark_100_d | 2016-12-21 | 2026-05-15 | 2360 | 2.93 | 12.13% | 17.13% | 0.75 | 0.86 | -36.71% | 0.33 | 0.00% | 0.00% |
| SPY Buy & Hold | benchmark_spy | 2016-12-21 | 2026-05-15 | 2362 | 3.79 | 15.25% | 18.29% | 0.87 | 1.00 | -33.72% | 0.45 | 0.00% |  |

## 5. Vol-Matched 与静态 G/D 对照

这一节以补充网格中 10bp 主口径的最佳 local smooth score 为目标策略，比较同风险水平下的 `100% G` 缩放版本、等波动/等回撤静态 G-D、以及最优静态 G-D。
- 目标 Smooth Score 配置：`local_a0.50_ls0.50_lc0.05_tilt0.50_tau1.00_eta0.05`
- Vol-matched 100% G 的缩放权重：`81.40%`

| method_label | comparison_type | static_g_weight | scale_to_g | final_wealth | cagr | ann_vol | sharpe | sortino | max_drawdown | calmar | annual_turnover | ann_excess_vs_smooth | max_dd_diff_vs_smooth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Smooth Score Best Local | target |  |  | 4.31 | 19.12% | 19.38% | 1.00 | 1.21 | -31.79% | 0.60 | 417.17% | 0.00% | 0.00% |
| 100% G Buy & Hold | baseline |  |  | 4.95 | 21.10% | 23.81% | 0.92 | 1.15 | -34.35% | 0.61 | 0.00% | 2.61% | -2.55% |
| Vol-Matched 100% G | vol_matched_g |  | 81.40% | 3.81 | 17.37% | 19.38% | 0.92 | 1.16 | -28.56% | 0.61 | 0.00% | -1.48% | 3.24% |
| 50/50 G-D | baseline |  |  | 3.71 | 16.98% | 19.53% | 0.90 | 1.07 | -33.59% | 0.51 | 0.00% | -1.78% | -1.79% |
| 100% D Buy & Hold | baseline |  |  | 2.64 | 12.34% | 17.70% | 0.75 | 0.85 | -36.71% | 0.34 | 0.00% | -6.17% | -4.92% |
| SPY Buy & Hold | baseline |  |  | 3.28 | 15.29% | 18.92% | 0.85 | 0.98 | -33.72% | 0.45 | 0.00% | -3.36% | -1.92% |
| Vol-Matched Static G/D (48% G) | vol_matched_static_gd | 48.00% |  | 3.66 | 16.80% | 19.40% | 0.90 | 1.06 | -33.70% | 0.50 | 0.00% | -1.96% | -1.90% |
| MaxDD-Matched Static G/D (82% G) | maxdd_matched_static_gd | 82.00% |  | 4.49 | 19.68% | 22.06% | 0.93 | 1.13 | -31.81% | 0.62 | 0.00% | 1.03% | -0.02% |
| Best Sharpe Static G/D (87% G) | best_sharpe_static_gd | 87.00% |  | 4.61 | 20.09% | 22.52% | 0.93 | 1.14 | -31.65% | 0.63 | 0.00% | 1.47% | 0.15% |
| Best Calmar Static G/D (87% G) | best_calmar_static_gd | 87.00% |  | 4.61 | 20.09% | 22.52% | 0.93 | 1.14 | -31.65% | 0.63 | 0.00% | 1.47% | 0.15% |
| Best CAGR Static G/D under Smooth MaxDD (87% G) | best_cagr_static_under_smooth_maxdd | 87.00% |  | 4.61 | 20.09% | 22.52% | 0.93 | 1.14 | -31.65% | 0.63 | 0.00% | 1.47% | 0.15% |

![Vol-Matched 与静态 G/D 对照资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_vol_matched_static_equity_curves.png)

## 6. Nested / Walk-Forward 与固定参数后验验证

这一节不再用全样本挑参数，也不使用 2021/2022 这类人为切点。Walk-forward 每次只用过去窗口选择 expanded local grid 里的参数，然后部署到未来 63 个交易日。固定参数验证使用最早完整 smooth score 样本中的首个训练窗口选参，然后从下一交易日开始后验验证。
- 最小训练窗口：`252` 个交易日。
- Walk-forward 测试块：`63` 个交易日。

### 6.1 Nested Walk-Forward

| validation_label | start_date | end_date | n_days | final_wealth | cagr | ann_vol | sharpe | sortino | max_drawdown | calmar | annual_turnover | avg_g_weight | ann_excess_vs_expanding_wf | max_dd_diff_vs_expanding_wf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Smooth Score WF Expanding | 2019-01-02 | 2026-05-15 | 1853 | 3.94 | 20.51% | 19.89% | 1.04 | 1.27 | -32.52% | 0.63 | 393.14% | 43.52% | 0.00% | 0.00% |
| Smooth Score WF Rolling | 2019-01-02 | 2026-05-15 | 1853 | 3.86 | 20.18% | 19.94% | 1.02 | 1.24 | -32.89% | 0.61 | 350.31% | 45.20% | -0.33% | -0.37% |
| 50/50 G-D | 2019-01-02 | 2026-05-15 | 1853 | 3.70 | 19.48% | 20.10% | 0.99 | 1.19 | -33.59% | 0.58 | 0.00% | 50.00% | -1.02% | -1.06% |
| 100% G | 2019-01-02 | 2026-05-15 | 1853 | 4.89 | 24.10% | 24.45% | 1.01 | 1.28 | -34.35% | 0.70 | 0.00% | 100.00% | 3.59% | -1.82% |
| 100% D | 2019-01-02 | 2026-05-15 | 1853 | 2.67 | 14.31% | 18.34% | 0.82 | 0.95 | -36.71% | 0.39 | 0.00% | 0.00% | -6.19% | -4.19% |
| SPY | 2019-01-02 | 2026-05-15 | 1853 | 3.30 | 17.63% | 19.51% | 0.93 | 1.11 | -33.72% | 0.52 | 0.00% |  | -2.88% | -1.19% |

![Nested Walk-Forward 资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_nested_walk_forward_equity_curves.png)

### 6.2 固定参数后验外样本验证

- 参数选择期：`2017-06-28` 到 `2018-12-31`；后验验证期从 `2019-01-02` 开始；训练窗口 `252` 个交易日。
- 固定参数配置：`local_a0.50_ls0.50_lc0.05_tilt0.50_tau1.50_eta0.03`

| validation_label | start_date | end_date | n_days | final_wealth | cagr | ann_vol | sharpe | sortino | max_drawdown | calmar | annual_turnover | avg_g_weight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fixed Parameter Earliest Holdout | 2019-01-02 | 2026-05-15 | 1853 | 4.15 | 21.35% | 19.79% | 1.08 | 1.32 | -32.56% | 0.66 | 207.62% | 45.59% |
| 50/50 G-D Holdout | 2019-01-02 | 2026-05-15 | 1853 | 3.70 | 19.48% | 20.10% | 0.99 | 1.19 | -33.59% | 0.58 | 0.00% | 50.00% |
| 100% G Holdout | 2019-01-02 | 2026-05-15 | 1853 | 4.89 | 24.10% | 24.45% | 1.01 | 1.28 | -34.35% | 0.70 | 0.00% | 100.00% |
| 100% D Holdout | 2019-01-02 | 2026-05-15 | 1853 | 2.67 | 14.31% | 18.34% | 0.82 | 0.95 | -36.71% | 0.39 | 0.00% | 0.00% |
| SPY Holdout | 2019-01-02 | 2026-05-15 | 1853 | 3.30 | 17.63% | 19.51% | 0.93 | 1.11 | -33.72% | 0.52 | 0.00% |  |

![固定参数后验验证资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_fixed_parameter_holdout_equity_curves.png)

## 7. Supplementary Extreme-Tilt Grid

第一轮固定 `alpha=0.50, lambda_stress=0.25, lambda_crowded=0.15, tau_weight=1.0, eta=0.05`，只测试 `max_tilt` 与交易成本。这里的 `max_tilt` 是 tanh 平滑映射的最大主动倾斜幅度。

| cost_bps | max_tilt | final_wealth | cagr | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | ann_excess_vs_50_50 | ann_excess_vs_100_g | max_dd_diff_vs_100_g |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 20.00% | 3.99 | 18.02% | 0.95 | -32.87% | 0.55 | 184.77% | 48.12% | 0.87% | -3.52% | 1.48% |
| 0 | 30.00% | 4.14 | 18.53% | 0.97 | -32.50% | 0.57 | 277.15% | 47.18% | 1.31% | -3.09% | 1.84% |
| 0 | 40.00% | 4.29 | 19.04% | 0.99 | -32.14% | 0.59 | 369.54% | 46.24% | 1.74% | -2.65% | 2.21% |
| 0 | 50.00% | 4.44 | 19.55% | 1.01 | -31.77% | 0.62 | 461.92% | 45.30% | 2.18% | -2.22% | 2.57% |
| 5 | 20.00% | 3.96 | 17.91% | 0.94 | -32.87% | 0.54 | 184.77% | 48.12% | 0.78% | -3.61% | 1.47% |
| 5 | 30.00% | 4.09 | 18.37% | 0.96 | -32.52% | 0.56 | 277.15% | 47.18% | 1.17% | -3.23% | 1.83% |
| 5 | 40.00% | 4.22 | 18.82% | 0.98 | -32.16% | 0.59 | 369.54% | 46.24% | 1.56% | -2.84% | 2.19% |
| 5 | 50.00% | 4.36 | 19.27% | 1.00 | -31.80% | 0.61 | 461.92% | 45.30% | 1.95% | -2.45% | 2.55% |
| 10 | 20.00% | 3.93 | 17.80% | 0.94 | -32.88% | 0.54 | 184.77% | 48.12% | 0.69% | -3.71% | 1.46% |
| 10 | 30.00% | 4.04 | 18.20% | 0.96 | -32.53% | 0.56 | 277.15% | 47.18% | 1.03% | -3.36% | 1.81% |
| 10 | 40.00% | 4.16 | 18.60% | 0.97 | -32.18% | 0.58 | 369.54% | 46.24% | 1.37% | -3.02% | 2.17% |
| 10 | 50.00% | 4.28 | 19.00% | 0.99 | -31.82% | 0.60 | 461.92% | 45.30% | 1.71% | -2.68% | 2.52% |
| 20 | 20.00% | 3.87 | 17.58% | 0.93 | -32.90% | 0.53 | 184.77% | 48.12% | 0.50% | -3.89% | 1.44% |
| 20 | 30.00% | 3.95 | 17.88% | 0.94 | -32.56% | 0.55 | 277.15% | 47.18% | 0.75% | -3.64% | 1.79% |
| 20 | 40.00% | 4.03 | 18.16% | 0.95 | -32.21% | 0.56 | 369.54% | 46.24% | 1.00% | -3.39% | 2.13% |
| 20 | 50.00% | 4.11 | 18.45% | 0.96 | -31.87% | 0.58 | 461.92% | 45.30% | 1.25% | -3.14% | 2.48% |

## 8. Expanded Local Grid

第二轮按你的扩展网格运行：`alpha ∈ {0.50,0.67}`、`lambda_stress ∈ {0.25,0.50}`、`lambda_crowded ∈ {0.05,0.15,0.25}`、`max_tilt ∈ {20%,30%,40%,50%}`、`tau_weight ∈ {0.75,1.0,1.5}`、`eta ∈ {0.03,0.05,0.10}`。主结论看 10bp，20bp 作为压力测试。

### 8.1 10bp 主口径 Top 10

| config_id | final_wealth | cagr | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | ann_excess_vs_50_50 | ann_excess_vs_100_g | max_dd_diff_vs_100_g | selection_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| local_a0.50_ls0.50_lc0.05_tilt0.50_tau1.00_eta0.05 | 4.31 | 19.12% | 1.00 | -31.79% | 0.60 | 417.17% | 44.78% | 1.78% | -2.61% | 2.55% | 79.95% |
| local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05 | 4.35 | 19.26% | 1.01 | -31.74% | 0.61 | 471.86% | 43.07% | 1.90% | -2.49% | 2.60% | 79.82% |
| local_a0.50_ls0.25_lc0.05_tilt0.50_tau1.00_eta0.05 | 4.32 | 19.15% | 1.00 | -31.70% | 0.60 | 459.09% | 46.26% | 1.84% | -2.56% | 2.64% | 79.50% |
| local_a0.50_ls0.25_lc0.05_tilt0.50_tau0.75_eta0.05 | 4.37 | 19.33% | 1.00 | -31.65% | 0.61 | 517.23% | 45.02% | 1.99% | -2.41% | 2.70% | 79.45% |
| local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.10 | 4.32 | 19.16% | 0.99 | -30.93% | 0.62 | 739.42% | 43.08% | 1.87% | -2.52% | 3.42% | 79.13% |
| local_a0.50_ls0.50_lc0.05_tilt0.50_tau1.00_eta0.10 | 4.30 | 19.09% | 0.99 | -30.99% | 0.62 | 658.68% | 44.79% | 1.80% | -2.59% | 3.36% | 78.49% |
| local_a0.50_ls0.50_lc0.15_tilt0.50_tau0.75_eta0.05 | 4.31 | 19.11% | 1.00 | -31.86% | 0.60 | 479.59% | 42.17% | 1.78% | -2.61% | 2.48% | 77.71% |
| local_a0.50_ls0.50_lc0.15_tilt0.50_tau1.00_eta0.05 | 4.27 | 18.99% | 0.99 | -31.89% | 0.60 | 424.14% | 43.90% | 1.68% | -2.71% | 2.45% | 77.48% |
| local_a0.50_ls0.25_lc0.05_tilt0.50_tau0.75_eta0.10 | 4.32 | 19.14% | 0.98 | -30.90% | 0.62 | 808.87% | 44.99% | 1.89% | -2.50% | 3.44% | 77.48% |
| local_a0.50_ls0.25_lc0.15_tilt0.50_tau0.75_eta0.05 | 4.32 | 19.15% | 0.99 | -31.79% | 0.60 | 519.74% | 44.03% | 1.84% | -2.55% | 2.56% | 77.34% |

### 8.2 20bp 压力测试 Top 10

| config_id | final_wealth | cagr | sharpe | max_drawdown | calmar | annual_turnover | avg_g_weight | ann_excess_vs_50_50 | ann_excess_vs_100_g | max_dd_diff_vs_100_g |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.03 | 4.19 | 18.72% | 0.99 | -32.56% | 0.57 | 322.59% | 43.10% | 1.41% | -2.99% | 1.78% |
| local_a0.50_ls0.25_lc0.05_tilt0.50_tau0.75_eta0.03 | 4.21 | 18.78% | 0.99 | -32.45% | 0.58 | 354.85% | 45.06% | 1.49% | -2.90% | 1.90% |
| local_a0.50_ls0.50_lc0.15_tilt0.50_tau0.75_eta0.03 | 4.17 | 18.63% | 0.99 | -32.70% | 0.57 | 327.27% | 42.17% | 1.33% | -3.06% | 1.64% |
| local_a0.50_ls0.50_lc0.05_tilt0.50_tau1.00_eta0.03 | 4.16 | 18.62% | 0.99 | -32.56% | 0.57 | 284.06% | 44.80% | 1.33% | -3.06% | 1.79% |
| local_a0.50_ls0.50_lc0.25_tilt0.50_tau0.75_eta0.03 | 4.16 | 18.59% | 0.98 | -32.85% | 0.57 | 328.23% | 42.04% | 1.31% | -3.08% | 1.49% |
| local_a0.50_ls0.25_lc0.15_tilt0.50_tau0.75_eta0.03 | 4.18 | 18.68% | 0.98 | -32.61% | 0.57 | 356.36% | 44.04% | 1.40% | -2.99% | 1.73% |
| local_a0.50_ls0.50_lc0.05_tilt0.50_tau0.75_eta0.05 | 4.19 | 18.70% | 0.98 | -31.79% | 0.59 | 471.86% | 43.07% | 1.43% | -2.97% | 2.56% |
| local_a0.50_ls0.25_lc0.05_tilt0.50_tau1.00_eta0.03 | 4.18 | 18.66% | 0.98 | -32.46% | 0.57 | 313.08% | 46.29% | 1.39% | -3.00% | 1.89% |
| local_a0.50_ls0.50_lc0.15_tilt0.50_tau1.00_eta0.03 | 4.14 | 18.54% | 0.98 | -32.68% | 0.57 | 288.51% | 43.90% | 1.27% | -3.13% | 1.67% |
| local_a0.50_ls0.25_lc0.25_tilt0.50_tau0.75_eta0.03 | 4.17 | 18.63% | 0.98 | -32.78% | 0.57 | 354.56% | 43.91% | 1.37% | -3.02% | 1.57% |

### 8.3 10bp 入选局部网格配置的成本敏感性：`local_a0.50_ls0.50_lc0.05_tilt0.50_tau1.00_eta0.05`

| cost_bps | final_wealth | cagr | sharpe | max_drawdown | calmar | annual_turnover | ann_excess_vs_50_50 | ann_excess_vs_100_g |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 4.46 | 19.61% | 1.02 | -31.75% | 0.62 | 417.17% | 2.20% | -2.20% |
| 5 | 4.39 | 19.36% | 1.01 | -31.77% | 0.61 | 417.17% | 1.99% | -2.40% |
| 10 | 4.31 | 19.12% | 1.00 | -31.79% | 0.60 | 417.17% | 1.78% | -2.61% |
| 20 | 4.16 | 18.62% | 0.98 | -31.84% | 0.58 | 417.17% | 1.36% | -3.03% |

### 8.4 补充网格资金曲线

下面两张图把补充网格的资金曲线单独列出：第一张比较固定结构下不同 `max_tilt`，第二张比较局部网格最佳配置与 buy-and-hold 基准。
- 局部网格最佳配置：`local_a0.50_ls0.50_lc0.05_tilt0.50_tau1.00_eta0.05`

![Supplementary Extreme Tilt 资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_supplementary_extreme_tilt_equity_curves.png)

![Supplementary Best Local Grid 资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_supplementary_best_local_equity_curves.png)

## 9. 2016 起点全可用窗口增量比较，10bp 成本

| comparison | annualized_excess_return | tracking_error | information_ratio | max_dd_diff | turnover_diff |
| --- | --- | --- | --- | --- | --- |
| Traditional smooth score - smooth TNX-only | 0.40% | 0.82% | 0.49 | -0.11% | -18.67% |
| Traditional smooth score - smooth core-only | 0.43% | 0.52% | 0.83 | 0.15% | 37.99% |
| Best smooth method - 50/50 | 0.73% | 1.39% | 0.53 | 0.75% | 183.63% |

## 10. Score 排序诊断

| method | config_id | Q1 | Q2 | Q3 | Q4 | Q5 | Q5_minus_Q1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 0.04% | 1.05% | 2.21% | 2.49% | 3.93% | 3.89% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | -1.18% | -0.06% | 0.99% | 3.65% | 5.23% | 6.41% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 0.08% | 0.29% | 1.34% | 2.37% | 5.63% | 5.55% |

## 11. 资金曲线对比

下面两张图都基于 2016 起点全可用窗口和 `10bp` 成本，资金曲线统一 rebase 到 `1.0`。

![2016 起点全可用窗口所有方法资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_common_oos_equity_curves_all.png)

![G/D Buy and Hold 基础资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_common_oos_buy_hold_gd.png)

图中 `100% G Buy & Hold` 和 `100% D Buy & Hold` 是单纯买入并持有 G、D 篮子的基础对照；`50/50 G-D Buy & Hold` 是不择时的静态配置基准。

## 12. 2016 起点全可用窗口年度表现，10bp 成本

| method | config_id | year | cagr | sharpe | max_drawdown | annual_turnover | avg_g_weight |
| --- | --- | --- | --- | --- | --- | --- | --- |
| benchmark_100_d | benchmark_100_d | 2016 | -37.11% | -8.46 | -1.08% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2017 | 17.54% | 2.46 | -3.03% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2018 | -5.67% | -0.31 | -17.54% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2019 | 25.08% | 1.94 | -7.88% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2020 | 6.60% | 0.36 | -36.71% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2021 | 30.83% | 2.14 | -5.18% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2022 | -1.87% | 0.00 | -17.32% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2023 | 10.69% | 0.87 | -9.53% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2024 | 15.55% | 1.41 | -6.99% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2025 | 12.31% | 0.83 | -15.16% | 0.00% | 0.00% |
| benchmark_100_d | benchmark_100_d | 2026 | 26.09% | 2.33 | -5.89% | 0.00% | 0.00% |
| benchmark_100_g | benchmark_100_g | 2016 | -43.22% | -8.15 | -1.60% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2017 | 31.46% | 3.05 | -3.87% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2018 | -0.60% | 0.08 | -22.54% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2019 | 41.00% | 2.27 | -9.27% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2020 | 42.24% | 1.14 | -30.81% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2021 | 30.41% | 1.57 | -9.83% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2022 | -30.61% | -0.97 | -33.92% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2023 | 48.31% | 2.43 | -10.69% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2024 | 29.06% | 1.43 | -14.22% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2025 | 22.00% | 0.92 | -24.06% | 0.00% | 100.00% |
| benchmark_100_g | benchmark_100_g | 2026 | 48.22% | 2.03 | -13.46% | 0.00% | 100.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2016 | -40.24% | -8.40 | -1.34% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2017 | 24.38% | 3.07 | -2.22% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2018 | -3.03% | -0.08 | -19.71% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2019 | 32.90% | 2.19 | -8.03% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2020 | 23.71% | 0.79 | -33.59% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2021 | 31.04% | 2.08 | -4.92% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2022 | -17.12% | -0.62 | -23.78% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2023 | 28.40% | 1.93 | -9.73% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2024 | 22.51% | 1.60 | -8.88% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2025 | 17.46% | 0.94 | -19.66% | 0.00% | 50.00% |
| benchmark_50_50_gd | benchmark_50_50_gd | 2026 | 37.22% | 2.39 | -7.95% | 0.00% | 50.00% |
| benchmark_spy | benchmark_spy | 2016 | -36.73% | -9.45 | -1.18% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2017 | 21.81% | 3.01 | -2.57% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2018 | -4.59% | -0.19 | -19.35% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2019 | 31.22% | 2.24 | -6.62% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2020 | 18.25% | 0.67 | -33.72% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2021 | 28.73% | 2.01 | -5.11% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2022 | -18.24% | -0.71 | -24.50% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2023 | 26.41% | 1.86 | -9.97% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2024 | 24.89% | 1.84 | -8.41% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2025 | 17.87% | 0.94 | -18.76% | 0.00% |  |
| benchmark_spy | benchmark_spy | 2026 | 25.50% | 1.72 | -8.88% | 0.00% |  |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2016 | -39.27% | -8.46 | -1.25% | 35.34% | 33.49% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2017 | 22.75% | 2.96 | -2.14% | 85.68% | 40.81% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2018 | -3.61% | -0.12 | -19.32% | 111.71% | 42.52% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2019 | 32.28% | 2.15 | -8.00% | 154.35% | 48.73% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2020 | 24.44% | 0.81 | -32.99% | 128.98% | 48.70% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2021 | 31.40% | 2.18 | -4.65% | 96.36% | 41.42% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2022 | -14.61% | -0.52 | -21.64% | 202.32% | 46.58% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2023 | 28.78% | 1.95 | -9.75% | 186.30% | 48.94% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2024 | 21.69% | 1.57 | -8.73% | 163.65% | 45.65% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2025 | 18.01% | 0.96 | -19.58% | 130.66% | 47.22% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 2026 | 35.75% | 2.43 | -7.63% | 111.46% | 43.42% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2016 | -39.35% | -8.47 | -1.26% | 58.18% | 34.27% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2017 | 23.50% | 2.95 | -2.40% | 171.80% | 49.08% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2018 | -3.57% | -0.12 | -19.51% | 181.31% | 46.56% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2019 | 33.21% | 2.17 | -8.20% | 189.59% | 55.11% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2020 | 25.63% | 0.83 | -32.72% | 156.96% | 51.42% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2021 | 31.57% | 2.16 | -4.79% | 168.72% | 46.35% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2022 | -14.74% | -0.55 | -22.10% | 251.96% | 42.79% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2023 | 26.89% | 1.86 | -9.80% | 248.86% | 47.25% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2024 | 22.10% | 1.53 | -9.53% | 227.69% | 51.41% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2025 | 17.54% | 0.93 | -20.14% | 185.53% | 52.39% |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 2026 | 35.48% | 2.34 | -7.76% | 185.55% | 48.32% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2017 | 22.72% | 2.66 | -2.06% | 277.01% | 51.46% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2018 | -8.04% | -0.41 | -19.68% | 259.67% | 53.89% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2019 | 33.37% | 2.18 | -8.12% | 215.83% | 53.82% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2020 | 25.36% | 0.83 | -32.84% | 154.68% | 50.15% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2021 | 31.46% | 2.19 | -4.62% | 110.08% | 41.21% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2022 | -14.48% | -0.51 | -21.59% | 239.88% | 47.28% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2023 | 28.94% | 1.97 | -9.68% | 170.53% | 47.75% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2024 | 21.94% | 1.59 | -8.56% | 162.98% | 45.28% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2025 | 18.62% | 0.98 | -19.81% | 149.21% | 50.02% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | 2026 | 37.72% | 2.49 | -7.72% | 186.37% | 46.73% |

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
- 2016 起点年度表现：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_yearly_metrics.csv`
- score 诊断：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_score_diagnostics.csv`
- 2016 起点 score 诊断：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_score_diagnostics.csv`
- 2016 起点资金曲线：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/tables/smooth_score_policy_v1_common_oos_equity_curves.csv`
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

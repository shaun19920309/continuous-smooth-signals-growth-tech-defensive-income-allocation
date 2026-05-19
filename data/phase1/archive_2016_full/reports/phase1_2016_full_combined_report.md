# Phase 1 2016 Full Archive Combined Report

## 0. 归档口径

本归档版本按最新要求重新整理，只保留两条主线：

1. 因子归因：检验 G、D、G-D 的 FF5+MOM 风险暴露。
2. Smooth Continuous Score Policy v1：保留该报告中的全部步骤，包括主网格、buy-and-hold、vol-matched、supplementary tilt、expanded local grid、walk-forward、fixed holdout、资金曲线和年度表现。

不纳入旧的 state sorting / predictive regression / oos_validation / state-action 中途路线；不纳入 ElasticNet。

## 1. 数据起点与自然 warmup

- G/D 源收益共同起点：`2016-12-21`。
- 因子归因回归样本：`2016-12-21` 到 `2026-03-31`。
- Smooth score 主比较从 G/D 最早共同可用日期 `2016-12-21` 开始。
- Smooth score 中的 `gd_trailing_126d` 必须使用 126 个交易日 warmup，因此完整 smooth score 动态策略的实际交易起点自然晚于 2016-12-21。这个 warmup 被保留并解释，不视为中途截样。

## 2. 研究链路

链路表已输出到：`data/phase1/archive_2016_full/tables/phase1_2016_full_archive_lineage.csv`

| step | archive_status | sample_note |
| --- | --- | --- |
| 1_factor_attribution | included | FF5+MOM 回归样本从 2016-12-21 开始。 |
| 2_smooth_score_policy_v1 | included | G/D 源收益从 2016-12-21 开始；包含 126 日 trailing warmup 后的完整 smooth score 结果。 |
| excluded_old_exploratory_routes | excluded | 这些属于旧路线或中途实验结果，本归档按用户要求不纳入。 |
| excluded_elasticnet | excluded | ElasticNet 相关实验、表格与结论全部排除。 |

## 3. Smooth Policy 入选方法概览

| display_name | start_date | end_date | n_days | final_wealth | CAGR | Ann Vol | Sharpe | Max DD | Turnover | Avg G |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Traditional Smooth Score | 2017-06-28 | 2026-05-15 | 2105 | 3.91 | 17.86% | 19.45% | 0.94 | -32.84% | 183.63% | 48.50% |
| Smooth TNX-only | 2016-12-21 | 2026-05-15 | 2360 | 4.48 | 17.35% | 18.81% | 0.95 | -32.72% | 197.11% | 49.08% |
| Smooth Core-only | 2016-12-21 | 2026-05-15 | 2360 | 4.45 | 17.26% | 18.69% | 0.95 | -32.99% | 138.58% | 45.50% |
| 50/50 G-D Buy & Hold | 2016-12-21 | 2026-05-15 | 2360 | 4.40 | 17.11% | 18.89% | 0.93 | -33.59% | 0.00% | 50.00% |
| 100% G Buy & Hold | 2016-12-21 | 2026-05-15 | 2360 | 6.28 | 21.66% | 22.98% | 0.97 | -34.35% | 0.00% | 100.00% |
| 100% D Buy & Hold | 2016-12-21 | 2026-05-15 | 2360 | 2.93 | 12.13% | 17.13% | 0.75 | -36.71% | 0.00% | 0.00% |
| SPY Buy & Hold | 2016-12-21 | 2026-05-15 | 2362 | 3.79 | 15.25% | 18.29% | 0.87 | -33.72% | 0.00% |  |

## 4. 合并报告正文

### 4.1 因子归因模块

#### 第一阶段收益归因模块报告

##### 1. 本模块回答的问题

这个模块先回答：成长/科技篮子 G、防御收益篮子 D、以及 G-D 多空组合，到底分别是什么风险暴露。只有先把 MKT、SMB、HML、RMW、CMA、MOM 这些已知因子解释清楚，后面才能讨论市场状态是否真的能预测 G 相对 D 的未来收益。

##### 2. 数据与口径

- G 篮子：`QQQ, XLK, VGT, SPYG, VUG`，固定等权。
- D 篮子：`SCHD, VYM, VTV, FDVV, COWZ`，固定等权。
- ETF 收益：Moomoo 日线 QFQ close 计算日收益。
- 因子：Kenneth French FF5 daily + Momentum，使用 decimal return。
- G 和 D 使用超额收益 `R - Rf`；G-D 是零成本多空组合，risk-free leg 相互抵消，因此用 `R_G - R_D`。
- 回归样本：`2016-12-21` 到 `2026-03-31`。

###### 2.1 ETF 数据覆盖

| symbol | first_return_date | last_return_date | n_returns |
| --- | --- | --- | --- |
| QQQ | 2006-05-23 | 2026-03-31 | 4995 |
| XLK | 2012-01-04 | 2026-03-31 | 3574 |
| VGT | 2012-01-04 | 2026-03-31 | 3574 |
| SPYG | 2012-01-04 | 2026-03-31 | 3574 |
| VUG | 2012-01-04 | 2026-03-31 | 3574 |
| SCHD | 2012-01-04 | 2026-03-31 | 3574 |
| VYM | 2012-01-04 | 2026-03-31 | 3576 |
| VTV | 2012-01-04 | 2026-03-31 | 3572 |
| FDVV | 2016-09-16 | 2026-03-31 | 2397 |
| COWZ | 2016-12-21 | 2026-03-31 | 2328 |

##### 3. G、D、G-D 全样本 FF5+MOM 回归

| portfolio | n | alpha ann. | alpha t(NW) | MKT | HML | RMW | CMA | MOM | adj R2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| G | 2328 | 2.20% | 1.48 | 1.147 | -0.298 | 0.067 | -0.071 | 0.041 | 0.965 |
| D | 2328 | 0.29% | 0.25 | 0.874 | 0.254 | 0.088 | 0.227 | -0.076 | 0.950 |
| G-D | 2328 | 1.90% | 0.79 | 0.273 | -0.552 | -0.021 | -0.298 | 0.117 | 0.757 |

完整表格含普通 t 值和 Newey-West t 值，见 `tables/factor_attribution_portfolios_full_sample.csv`。

###### 3.1 G-D 初步解释

- G-D 的市场 beta 为 `0.273`，Newey-West t 值 `11.25`。 这说明多成长/科技、空防御收益组合明显偏高市场 beta。
- HML beta 为 `-0.552`，Newey-West t 值 `-20.01`。 负 HML 表明它本质上是多成长、空价值/红利的一部分。
- MOM beta 为 `0.117`，Newey-West t 值 `8.80`。 这说明 G-D 和动量行情有明显同向关系，后续预测实验必须控制 MOM。
- RMW beta `-0.021`、CMA beta `-0.298`，分别对应盈利能力和投资风格暴露。
- G-D 年化 alpha 为 `1.90%`，alpha 的 Newey-West t 值 `0.79`。 这更像可解释的风格/因子组合，而不是已经证明的新 alpha。

##### 4. 单 ETF 因子暴露

这张表用于检查篮子内部是否一致，以及后续是否需要重设权重或剔除风格不纯的 ETF。

| ETF | group | n | alpha ann. | alpha t(NW) | MKT | HML | RMW | CMA | MOM | adj R2 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| QQQ | G | 4995 | 3.57% | 2.76 | 1.078 | -0.312 | 0.014 | -0.216 | 0.039 | 0.924 |
| XLK | G | 3574 | 1.88% | 1.07 | 1.193 | -0.317 | 0.133 | -0.049 | 0.052 | 0.908 |
| VGT | G | 3574 | 2.81% | 1.62 | 1.190 | -0.330 | 0.061 | -0.118 | 0.051 | 0.916 |
| SPYG | G | 3574 | 0.06% | 0.08 | 1.056 | -0.213 | 0.086 | -0.077 | 0.037 | 0.967 |
| VUG | G | 3574 | 0.30% | 0.40 | 1.076 | -0.265 | 0.029 | -0.146 | 0.006 | 0.977 |
| SCHD | D | 3574 | -0.01% | -0.01 | 0.848 | 0.183 | 0.232 | 0.270 | -0.081 | 0.875 |
| VYM | D | 3576 | -0.92% | -0.91 | 0.862 | 0.259 | 0.081 | 0.237 | -0.033 | 0.927 |
| VTV | D | 3572 | -0.74% | -0.78 | 0.887 | 0.304 | 0.034 | 0.185 | -0.037 | 0.943 |
| FDVV | D | 2397 | -0.25% | -0.18 | 0.883 | 0.229 | 0.048 | 0.182 | -0.068 | 0.932 |
| COWZ | D | 2328 | 1.44% | 0.69 | 0.934 | 0.223 | 0.150 | 0.224 | -0.112 | 0.880 |

完整单 ETF 表格见 `tables/factor_attribution_etfs_full_sample.csv`。

##### 5. 滚动 beta 输出

已生成 252 日和 504 日滚动 alpha/beta。最近一期结果如下：

| portfolio | window | date | alpha ann. | MKT | HML | MOM | R2 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| G | 252 | 2026-03-31 | 3.52% | 1.189 | -0.226 | 0.049 | 0.971 |
| G | 504 | 2026-03-31 | 0.79% | 1.201 | -0.340 | 0.118 | 0.962 |
| G-D | 252 | 2026-03-31 | 4.21% | 0.399 | -0.507 | 0.139 | 0.780 |
| D | 252 | 2026-03-31 | -0.67% | 0.790 | 0.281 | -0.089 | 0.924 |
| D | 504 | 2026-03-31 | 0.42% | 0.783 | 0.330 | -0.150 | 0.900 |
| G-D | 504 | 2026-03-31 | 0.37% | 0.419 | -0.670 | 0.268 | 0.787 |

滚动 beta 文件：`tables/factor_attribution_rolling_betas.csv`。

###### 5.1 G-D 按阶段滚动暴露摘要

| period | avg alpha ann. | avg MKT | avg HML | avg CMA | avg MOM | avg R2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| covid_rebound_2020_2021 | 7.06% | 0.207 | -0.522 | -0.314 | 0.100 | 0.812 |
| rate_hike_2022 | 3.77% | 0.267 | -0.640 | -0.122 | 0.113 | 0.856 |
| ai_rally_2023_2024 | -2.21% | 0.275 | -0.542 | -0.486 | 0.105 | 0.809 |
| recent_2025_2026q1 | 2.61% | 0.398 | -0.682 | -0.021 | 0.306 | 0.794 |

完整阶段汇总文件：`tables/factor_attribution_rolling_period_summary.csv`。

##### 6. 第一阶段下一步怎么接

1. 如果 G-D 的 MKT/HML/MOM 显著，而 alpha 不显著，后续研究应写成“状态依赖的风格因子动态配置”，不是新 alpha。
2. 如果 G-D 的 alpha 显著，也不能马上进入策略，需要做样本外、子样本、交易成本和多重检验控制。
3. 下一步应把本模块输出的残差收益、滚动 beta 和 alpha 接到状态变量模块，检验 `VIX/drawdown/rate/relative strength` 是否预测的是原始 G-D，还是因子调整后的 G-D。

##### 7. 输出文件

- 回归面板：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/factor_attribution/inputs/phase1_factor_returns_panel.csv`
- 组合全样本回归：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/factor_attribution/tables/factor_attribution_portfolios_full_sample.csv`
- 单 ETF 全样本回归：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/factor_attribution/tables/factor_attribution_etfs_full_sample.csv`
- 滚动 beta：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/factor_attribution/tables/factor_attribution_rolling_betas.csv`
- 因子调整 residual 序列：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/factor_attribution/tables/factor_attribution_factor_adjusted_returns.csv`
- 滚动 beta 阶段汇总：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/factor_attribution/tables/factor_attribution_rolling_period_summary.csv`
- 数据覆盖：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/factor_attribution/tables/factor_attribution_data_coverage.csv`


### 4.2 Smooth Continuous Score Policy v1

#### 第一阶段 Smooth Continuous Score Policy v1 报告

##### 1. 本步目标

本步不再找变量，而是检验 `TNX + SPY drawdown + 平滑交互项` 能否改善 G/D 动态配置。
所有策略都使用连续 score、tanh 仓位映射和 EWMA 权重平滑；没有分位调仓、硬 if 规则或最小调仓阈值。

##### 2. 样本与口径

- G/D 日收益源样本：`2016-12-21` 到 `2026-05-15`，n=`2360`。
- 可用于 63 日目标诊断的样本：`2017-06-26` 到 `2026-02-13`，n=`1982`。
- Smooth score 完整特征样本：`2017-06-26` 到 `2026-05-15`，n=`2108`。
- 主策略比较从 G/D 最早共同可用日期开始：`2016-12-21` 到 `2026-05-15`。
- 注意：`gd_trailing_126d` 需要 126 个交易日 warmup，因此动态 smooth score 的实际可交易起点会晚于 2016-12-21；这不是中途截样，而是变量定义带来的自然 warmup。
- 信号在 t 日收盘后形成，t+1 日收益开始使用。
- 标准化均为 expanding z-score，不使用全样本 z-score。
- 本版报告只保留规则型 smooth score、补充 tilt 网格和 buy-and-hold 基准。
- 交易成本报告 `0bp`、`5bp`、`10bp`、`20bp`；成本按 `2 × |ΔG权重| × cost_bps / 10000` 扣除。

##### 3. 2016 起点全可用窗口主结果，10bp 成本后

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

##### 4. 入选方法与 Buy-and-Hold 对齐统计

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

##### 5. Vol-Matched 与静态 G/D 对照

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

##### 6. Nested / Walk-Forward 与固定参数后验验证

这一节不再用全样本挑参数。Walk-forward 每次只用过去窗口选择 expanded local grid 里的参数，然后部署到未来 63 个交易日。固定参数验证则先用 2021 年底以前的数据选一个参数，再锁定到 2022 年以后。

###### 6.1 Nested Walk-Forward

| validation_label | start_date | end_date | n_days | final_wealth | cagr | ann_vol | sharpe | sortino | max_drawdown | calmar | annual_turnover | avg_g_weight | ann_excess_vs_expanding_wf | max_dd_diff_vs_expanding_wf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Smooth Score WF Expanding | 2020-12-31 | 2026-05-15 | 1349 | 2.33 | 17.14% | 16.81% | 1.03 | 1.42 | -19.81% | 0.87 | 413.79% | 39.11% | 0.00% | 0.00% |
| Smooth Score WF Rolling | 2020-12-31 | 2026-05-15 | 1349 | 2.34 | 17.22% | 16.80% | 1.03 | 1.44 | -19.21% | 0.90 | 374.57% | 39.25% | 0.08% | 0.60% |
| 50/50 G-D | 2020-12-31 | 2026-05-15 | 1349 | 2.26 | 16.44% | 17.26% | 0.97 | 1.33 | -23.78% | 0.69 | 0.00% | 50.00% | -0.70% | -3.97% |
| 100% G | 2020-12-31 | 2026-05-15 | 1349 | 2.44 | 18.14% | 22.82% | 0.84 | 1.14 | -34.35% | 0.53 | 0.00% | 100.00% | 1.00% | -14.54% |
| 100% D | 2020-12-31 | 2026-05-15 | 1349 | 2.02 | 14.02% | 14.40% | 0.98 | 1.38 | -17.32% | 0.81 | 0.00% | 0.00% | -3.12% | 2.49% |
| SPY | 2020-12-31 | 2026-05-15 | 1349 | 2.14 | 15.23% | 16.89% | 0.92 | 1.24 | -24.50% | 0.62 | 0.00% |  | -1.91% | -4.69% |

![Nested Walk-Forward 资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_nested_walk_forward_equity_curves.png)

###### 6.2 固定参数后验外样本验证

- 参数选择期：`2017-06-28` 到 `2021-12-31`；后验验证期从 `2022-01-03` 开始。
- 固定参数配置：`local_a0.50_ls0.50_lc0.05_tilt0.50_tau1.50_eta0.05`

| validation_label | start_date | end_date | n_days | final_wealth | cagr | ann_vol | sharpe | sortino | max_drawdown | calmar | annual_turnover | avg_g_weight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fixed Parameter Holdout | 2022-01-03 | 2026-05-15 | 1096 | 1.85 | 15.25% | 17.62% | 0.89 | 1.21 | -19.75% | 0.77 | 301.67% | 43.60% |
| 50/50 G-D Holdout | 2022-01-03 | 2026-05-15 | 1096 | 1.72 | 13.23% | 18.02% | 0.78 | 1.02 | -23.78% | 0.56 | 0.00% | 50.00% |
| 100% G Holdout | 2022-01-03 | 2026-05-15 | 1096 | 1.87 | 15.45% | 23.81% | 0.72 | 0.93 | -33.92% | 0.46 | 0.00% | 100.00% |
| 100% D Holdout | 2022-01-03 | 2026-05-15 | 1096 | 1.53 | 10.32% | 14.71% | 0.74 | 0.99 | -17.32% | 0.60 | 0.00% | 0.00% |
| SPY Holdout | 2022-01-03 | 2026-05-15 | 1096 | 1.65 | 12.21% | 17.68% | 0.74 | 0.96 | -24.50% | 0.50 | 0.00% |  |

![固定参数后验验证资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_fixed_parameter_holdout_equity_curves.png)

##### 7. Supplementary Extreme-Tilt Grid

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

##### 8. Expanded Local Grid

第二轮按你的扩展网格运行：`alpha ∈ {0.50,0.67}`、`lambda_stress ∈ {0.25,0.50}`、`lambda_crowded ∈ {0.05,0.15,0.25}`、`max_tilt ∈ {20%,30%,40%,50%}`、`tau_weight ∈ {0.75,1.0,1.5}`、`eta ∈ {0.03,0.05,0.10}`。主结论看 10bp，20bp 作为压力测试。

###### 8.1 10bp 主口径 Top 10

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

###### 8.2 20bp 压力测试 Top 10

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

###### 8.3 10bp 入选局部网格配置的成本敏感性：`local_a0.50_ls0.50_lc0.05_tilt0.50_tau1.00_eta0.05`

| cost_bps | final_wealth | cagr | sharpe | max_drawdown | calmar | annual_turnover | ann_excess_vs_50_50 | ann_excess_vs_100_g |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 4.46 | 19.61% | 1.02 | -31.75% | 0.62 | 417.17% | 2.20% | -2.20% |
| 5 | 4.39 | 19.36% | 1.01 | -31.77% | 0.61 | 417.17% | 1.99% | -2.40% |
| 10 | 4.31 | 19.12% | 1.00 | -31.79% | 0.60 | 417.17% | 1.78% | -2.61% |
| 20 | 4.16 | 18.62% | 0.98 | -31.84% | 0.58 | 417.17% | 1.36% | -3.03% |

###### 8.4 补充网格资金曲线

下面两张图把补充网格的资金曲线单独列出：第一张比较固定结构下不同 `max_tilt`，第二张比较局部网格最佳配置与 buy-and-hold 基准。
- 局部网格最佳配置：`local_a0.50_ls0.50_lc0.05_tilt0.50_tau1.00_eta0.05`

![Supplementary Extreme Tilt 资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_supplementary_extreme_tilt_equity_curves.png)

![Supplementary Best Local Grid 资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_supplementary_best_local_equity_curves.png)

##### 9. 2016 起点全可用窗口增量比较，10bp 成本

| comparison | annualized_excess_return | tracking_error | information_ratio | max_dd_diff | turnover_diff |
| --- | --- | --- | --- | --- | --- |
| Traditional smooth score - smooth TNX-only | 0.40% | 0.82% | 0.49 | -0.11% | -18.67% |
| Traditional smooth score - smooth core-only | 0.43% | 0.52% | 0.83 | 0.15% | 37.99% |
| Best smooth method - 50/50 | 0.73% | 1.39% | 0.53 | 0.75% | 183.63% |

##### 10. Score 排序诊断

| method | config_id | Q1 | Q2 | Q3 | Q4 | Q5 | Q5_minus_Q1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| smooth_tnx_only | tnx_tilt0.20_tau1.0_eta0.05 | 0.04% | 1.05% | 2.21% | 2.49% | 3.93% | 3.89% |
| traditional_smooth_score | trad_a0.50_ls0.25_lc0.05_tilt0.20_tau1.0_eta0.05 | -1.18% | -0.06% | 0.99% | 3.65% | 5.23% | 6.41% |
| smooth_core_only | core_a0.50_tilt0.20_tau1.0_eta0.05 | 0.08% | 0.29% | 1.34% | 2.37% | 5.63% | 5.55% |

##### 11. 资金曲线对比

下面两张图都基于 2016 起点全可用窗口和 `10bp` 成本，资金曲线统一 rebase 到 `1.0`。

![2016 起点全可用窗口所有方法资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_common_oos_equity_curves_all.png)

![G/D Buy and Hold 基础资金曲线](/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/smooth_score_policy_v1/plots/smooth_score_policy_v1_common_oos_buy_hold_gd.png)

图中 `100% G Buy & Hold` 和 `100% D Buy & Hold` 是单纯买入并持有 G、D 篮子的基础对照；`50/50 G-D Buy & Hold` 是不择时的静态配置基准。

##### 12. 2016 起点全可用窗口年度表现，10bp 成本

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

##### 13. 输出文件

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

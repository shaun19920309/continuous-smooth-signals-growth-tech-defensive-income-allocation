# 第一阶段收益归因模块报告

## 1. 本模块回答的问题

这个模块先回答：成长/科技篮子 G、防御收益篮子 D、以及 G-D 多空组合，到底分别是什么风险暴露。只有先把 MKT、SMB、HML、RMW、CMA、MOM 这些已知因子解释清楚，后面才能讨论市场状态是否真的能预测 G 相对 D 的未来收益。

## 2. 数据与口径

- G 篮子：`QQQ, XLK, VGT, SPYG, VUG`，固定等权。
- D 篮子：`SCHD, VYM, VTV, FDVV, COWZ`，固定等权。
- ETF 收益：Moomoo 日线 QFQ close 计算日收益；对单 ETF 的孤立数据缺口，先在价格层做最多 3 个交易日的 forward-fill，再计算收益，长缺口和上市前缺口不填补。
- 因子：Kenneth French FF5 daily + Momentum，使用 decimal return。
- G 和 D 使用超额收益 `R - Rf`；G-D 是零成本多空组合，risk-free leg 相互抵消，因此用 `R_G - R_D`。
- 回归样本：`2016-12-21` 到 `2026-03-31`。

### 2.1 ETF 数据覆盖

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

## 3. G、D、G-D 全样本 FF5+MOM 回归

| portfolio | n | alpha ann. | alpha t(NW) | MKT | HML | RMW | CMA | MOM | adj R2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| G | 2330 | 2.24% | 1.51 | 1.148 | -0.298 | 0.067 | -0.071 | 0.041 | 0.965 |
| D | 2330 | 0.29% | 0.24 | 0.874 | 0.254 | 0.088 | 0.227 | -0.076 | 0.950 |
| G-D | 2330 | 1.95% | 0.81 | 0.273 | -0.552 | -0.021 | -0.298 | 0.117 | 0.757 |

完整表格含普通 t 值和 Newey-West t 值，见 `tables/factor_attribution_portfolios_full_sample.csv`。

### 3.1 G-D 初步解释

- G-D 的市场 beta 为 `0.273`，Newey-West t 值 `11.24`。 这说明多成长/科技、空防御收益组合明显偏高市场 beta。
- HML beta 为 `-0.552`，Newey-West t 值 `-20.01`。 负 HML 表明它本质上是多成长、空价值/红利的一部分。
- MOM beta 为 `0.117`，Newey-West t 值 `8.80`。 这说明 G-D 和动量行情有明显同向关系，后续预测实验必须控制 MOM。
- RMW beta `-0.021`、CMA beta `-0.298`，分别对应盈利能力和投资风格暴露。
- G-D 年化 alpha 为 `1.95%`，alpha 的 Newey-West t 值 `0.81`。 这更像可解释的风格/因子组合，而不是已经证明的新 alpha。

## 4. 单 ETF 因子暴露

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

## 5. 滚动 beta 输出

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

### 5.1 G-D 按阶段滚动暴露摘要

| period | avg alpha ann. | avg MKT | avg SMB | avg HML | avg RMW | avg CMA | avg MOM | avg R2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| covid_rebound_2020_2021 | 7.06% | 0.207 | -0.166 | -0.522 | 0.155 | -0.314 | 0.100 | 0.812 |
| rate_hike_2022 | 3.77% | 0.267 | -0.252 | -0.640 | -0.013 | -0.122 | 0.113 | 0.856 |
| ai_rally_2023_2024 | -2.21% | 0.275 | -0.188 | -0.542 | 0.073 | -0.486 | 0.105 | 0.809 |
| recent_2025_2026q1 | 2.61% | 0.398 | -0.103 | -0.682 | -0.022 | -0.021 | 0.306 | 0.794 |

完整阶段汇总文件：`tables/factor_attribution_rolling_period_summary.csv`。

## 6. 第一阶段下一步怎么接

1. 如果 G-D 的 MKT/HML/MOM 显著，而 alpha 不显著，后续研究应写成“状态依赖的风格因子动态配置”，不是新 alpha。
2. 如果 G-D 的 alpha 显著，也不能马上进入策略，需要做样本外、子样本、交易成本和多重检验控制。
3. 下一步应把本模块输出的残差收益、滚动 beta 和 alpha 接到状态变量模块，检验 `VIX/drawdown/rate/relative strength` 是否预测的是原始 G-D，还是因子调整后的 G-D。

## 7. 输出文件

- 回归面板：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/factor_attribution/inputs/phase1_factor_returns_panel.csv`
- 组合全样本回归：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/factor_attribution/tables/factor_attribution_portfolios_full_sample.csv`
- 单 ETF 全样本回归：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/factor_attribution/tables/factor_attribution_etfs_full_sample.csv`
- 滚动 beta：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/factor_attribution/tables/factor_attribution_rolling_betas.csv`
- 因子调整 residual 序列：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/factor_attribution/tables/factor_attribution_factor_adjusted_returns.csv`
- 滚动 beta 阶段汇总：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/factor_attribution/tables/factor_attribution_rolling_period_summary.csv`
- 数据覆盖：`/Users/zhelixiong/Desktop/research/doctor/github_package/phase1_2016_full_archive/data/phase1/factor_attribution/tables/factor_attribution_data_coverage.csv`

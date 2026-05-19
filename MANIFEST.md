# Manifest

## Included Research Branches

## Included Source Data

- `data/moomoo/research/kline_day_qfq/`
  - Adjusted daily ETF bars used to construct G and D basket returns.
- `data/external/fama_french/processed/fama_french_5_plus_momentum_daily.csv`
  - FF5 + MOM daily factor panel.
- `data/external/failed_moomoo_indices/processed/all_failed_moomoo_indices_normalized.csv`
  - Normalized SPY/index/rate/volatility panel used by the state framework and smooth score features.

### 1. Factor Attribution

- Script: `scripts/run_phase1_factor_attribution.py`
- Report: `data/phase1/factor_attribution/reports/phase1_factor_attribution_report.md`
- Main tables:
  - `factor_attribution_portfolios_full_sample.csv`
  - `factor_attribution_etfs_full_sample.csv`
  - `factor_attribution_rolling_betas.csv`
  - `factor_attribution_factor_adjusted_returns.csv`

### 2. Smooth Score Policy v1

- Input-prep script: `scripts/run_phase1_state_framework_v2.py`
- Main script: `scripts/run_phase1_smooth_score_policy_v1.py`
- Report: `data/phase1/smooth_score_policy_v1/reports/phase1_smooth_score_policy_v1_report.md`
- Includes:
  - 2016-start source sample documentation;
  - main smooth score grid;
  - buy-and-hold baselines;
  - vol-matched and static G/D controls;
  - supplementary extreme-tilt grid;
  - expanded local grid;
  - nested walk-forward validation;
  - fixed pre-2022 parameter holdout;
  - score diagnostics;
  - annual results;
  - equity-curve figures.

### 3. Combined Archive Report

- Script: `scripts/build_phase1_2016_full_archive_report.py`
- Report: `data/phase1/archive_2016_full/reports/phase1_2016_full_combined_report.md`
- Lineage table: `data/phase1/archive_2016_full/tables/phase1_2016_full_archive_lineage.csv`

## Excluded

- Old state sorting route.
- Old predictive regression route.
- Old OOS validation route.
- Old state-action policy route.
- ElasticNet experiments, tables, plots, and conclusions.
- Large regenerable intermediate CSV files listed in `.gitignore`.

## Main Sample Notes

- Factor attribution: `2016-12-21` to `2026-03-31`.
- Smooth policy G/D source returns: `2016-12-21` to `2026-05-15`.
- Smooth policy complete features: start after natural 126-trading-day warmup.

#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"

"$PYTHON_BIN" scripts/run_phase1_factor_attribution.py
"$PYTHON_BIN" scripts/run_phase1_state_framework_v2.py
"$PYTHON_BIN" scripts/run_phase1_smooth_score_policy_v1.py
"$PYTHON_BIN" scripts/run_phase1_bond_credit_augmented_v1.py
"$PYTHON_BIN" scripts/run_phase1_bond_credit_smooth_policy_v1.py
"$PYTHON_BIN" scripts/build_phase1_2016_full_archive_report.py

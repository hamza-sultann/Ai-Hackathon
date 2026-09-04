"""Track-2 (AMI-enhanced) theft model — servable version of uplift_evaluation.py's "Model 2".

This does not introduce new modeling decisions. It reuses, verbatim:
  - TRACK1_FEATURES / TRACK2_FEATURES and the XGBClassifier hyperparameters
    from uplift_evaluation.py's `train_and_eval` (Model 2: Track-1 + Track-2).
  - `features.build_features()` — the same Track-1 feature engineering
    run_pipeline.py uses.
  - `calibrate.calibrate_model()` — the same Platt-scaling calibration
    run_pipeline.py already uses for the Track-1 model.

uplift_evaluation.py is an evaluation script: it fits a model and prints a
recall table, but never saves an artifact, and never calibrates (it compares
raw `.predict()` at the implicit 0.5 XGBoost-native threshold). This script
adds exactly what's needed to *serve* the same Model 2 live: calibration on
the reserved calibration split (unused by uplift_evaluation.py) and
persistence, mirroring how run_pipeline.py persists the Track-1 model.

One deliberate fix, not a modeling change: uplift_evaluation.py computes
`iso_forest_oof_score` two different ways for train vs. eval (OOF GroupKFold,
unnegated, for train; a fresh non-OOF IsolationForest, negated, for eval) —
those disagree in sign. A servable model can't have a train/serve mismatch on
its own input feature, so this script fits one IsolationForest on the AMI
training subset and scores everyone with plain `.score_samples()` (no
negation), matching the sign convention already used by
isolation_forest_oof.py / run_pipeline.py for the Track-1 model.

Usage:
    python train_track2_model.py
Requires (unchanged, already-authored artifacts):
    output/{train,calibrate,eval}.parquet   (data_assembly.py)
    track2_features.csv                     (run_track2_features.py)
    ami_consumer_ids.csv                    (select_ami_population.py)
"""
import numpy as np
import pandas as pd
import xgboost as xgb
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score

from features import build_features
from calibrate import calibrate_model, verify_calibration_spread

# Verbatim from uplift_evaluation.py
TRACK1_FEATURES = [
    'pmt_loss_delta_pct',
    'pmt_loss_rank',
    'usage_deviation',
    'fixed_baseline_deviation',
    'cusum_max_deviation',
    'months_since_detected_break',
    'peer_deviation',
    'arrears_ratio',
    'seasonal_residual',
    'rolling_trend_3mo',
    'feeder_uptime_adj_deviation',
    'prosumer_gated_usage_deviation',
]
TRACK2_FEATURES = [
    'peak_offpeak_ratio',
    'daily_load_factor',
    'flatline_fraction',
    'peak_window_flatline_fraction',
    'midday_dip_index',
    'tariff_boundary_alignment_score',
    'nighttime_drop_index',
]
FEATURE_COLUMNS = TRACK1_FEATURES + ['iso_forest_oof_score'] + TRACK2_FEATURES


def _prep(df: pd.DataFrame, ami_ids, track2: pd.DataFrame) -> pd.DataFrame:
    df = df[df['consumer_id'].isin(ami_ids)].copy()
    df = build_features(df)
    df['month'] = pd.to_datetime(df['month'])
    df = df.merge(track2, on=['consumer_id', 'month'], how='left')
    df[TRACK2_FEATURES] = df[TRACK2_FEATURES].fillna(0)
    return df


def main() -> None:
    print("Loading AMI subset + Track-1/Track-2 features (Model 2 recipe from uplift_evaluation.py)...")
    ami_ids = pd.read_csv('ami_consumer_ids.csv')['consumer_id'].values
    t2 = pd.read_csv('track2_features.csv')
    t2['month'] = pd.to_datetime(t2['month'])

    train_df = _prep(pd.read_parquet('output/train.parquet'), ami_ids, t2)
    cal_df = _prep(pd.read_parquet('output/calibrate.parquet'), ami_ids, t2)
    eval_df = _prep(pd.read_parquet('output/eval.parquet'), ami_ids, t2)
    print(f"AMI train={train_df['consumer_id'].nunique()} cal={cal_df['consumer_id'].nunique()} "
          f"eval={eval_df['consumer_id'].nunique()} consumers")

    # Isolation forest: fit once on train, score everyone consistently (see docstring).
    iso = IsolationForest(random_state=42)
    iso.fit(train_df[TRACK1_FEATURES].fillna(0))
    for df in (train_df, cal_df, eval_df):
        df['iso_forest_oof_score'] = iso.score_samples(df[TRACK1_FEATURES].fillna(0))

    # XGBoost: same hyperparameters as uplift_evaluation.py's Model 2.
    y_train = train_df['is_theft_ground_truth'].astype(int)
    neg, pos = (y_train == 0).sum(), (y_train == 1).sum()
    scale_pos_weight = float(neg) / pos if pos else 1.0
    clf = xgb.XGBClassifier(
        objective='binary:logistic',
        scale_pos_weight=scale_pos_weight,
        eval_metric='aucpr',
        n_estimators=100,
        max_depth=5,
        random_state=42,
    )
    clf.fit(train_df[FEATURE_COLUMNS], y_train)

    # Calibrate on the reserved calibration split — same function Track-1 uses.
    print("\nCalibrating on the AMI calibration split...")
    calibrator = calibrate_model(clf, cal_df, FEATURE_COLUMNS)
    y_prob_eval = verify_calibration_spread(calibrator, eval_df, FEATURE_COLUMNS, min_expected_max=0.3)

    # Report — same shape as uplift_evaluation.py's own printout, for a human to sanity-check.
    y_true = eval_df['is_theft_ground_truth'].astype(int)
    y_pred = (y_prob_eval >= 0.5).astype(int)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    print(f"\nCalibrated Model 2 @0.5 on AMI eval split: precision={prec:.3f} recall={rec:.3f}")

    clf.save_model('xgboost_model_track2.json')
    joblib.dump(calibrator, 'final_calibrator_track2.joblib')
    joblib.dump(iso, 'isolation_forest_track2.joblib')
    print("\nSaved xgboost_model_track2.json, final_calibrator_track2.joblib, isolation_forest_track2.joblib")


if __name__ == '__main__':
    main()

"""
Comprehensive Diagnostic Report Generator (Before vs. After Fixes)
"""
import pandas as pd
import numpy as np
import joblib
from features import build_features
from isolation_forest_oof import compute_oof_anomaly_scores
from merge import merge_anomaly_score
from train_xgboost import train_classifier
from calibrate import calibrate_model, verify_calibration_spread
from evaluate import run_full_evaluation

def main():
    print("="*70)
    print("COMPREHENSIVE DIAGNOSTIC & BENCHMARK REPORT (POST-FIXES)")
    print("="*70)
    
    # Load data
    train_df = pd.read_parquet('output/train.parquet')
    cal_df = pd.read_parquet('output/calibrate.parquet')
    eval_df = pd.read_parquet('output/eval.parquet')
    
    # ---- 1. BUILD FEATURES ----
    print("\n" + "="*70)
    print("SECTION 1: FEATURE SEPARATION (THEFT VS CLEAN)")
    print("="*70)
    
    train_df = build_features(train_df)
    cal_df = build_features(cal_df)
    eval_df = build_features(eval_df)
    
    feature_columns = [
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
        'prosumer_gated_usage_deviation'
    ]
    
    theft_mask = train_df['is_theft_ground_truth'] == True
    
    print(f"{'Feature':<35} {'Theft Mean':>12} {'Clean Mean':>12} {'Diff':>12} {'Theft Std':>12}")
    print("-"*85)
    for col in feature_columns:
        t_mean = train_df.loc[theft_mask, col].mean()
        c_mean = train_df.loc[~theft_mask, col].mean()
        t_std = train_df.loc[theft_mask, col].std()
        diff = t_mean - c_mean
        print(f"{col:<35} {t_mean:>12.4f} {c_mean:>12.4f} {diff:>12.4f} {t_std:>12.4f}")
        
    # ---- 2. ISOLATION FOREST ANALYSIS ----
    print("\n" + "="*70)
    print("SECTION 2: ISOLATION FOREST RE-EVALUATION")
    print("="*70)
    train_df = compute_oof_anomaly_scores(train_df, feature_columns)
    train_df, feature_columns_with_iso = merge_anomaly_score(train_df, feature_columns)
    
    iso_theft = train_df.loc[theft_mask, 'iso_forest_oof_score']
    iso_clean = train_df.loc[~theft_mask, 'iso_forest_oof_score']
    corr = train_df['iso_forest_oof_score'].corr(train_df['is_theft_ground_truth'].astype(float))
    
    print(f"Old Baseline: Theft mean = -0.4130, Clean mean = -0.4195, Corr = +0.0355 (Flat)")
    print(f"New Isolation Forest: Theft mean = {iso_theft.mean():.4f}, Clean mean = {iso_clean.mean():.4f}")
    print(f"New Correlation with Ground Truth: {corr:.4f}")
    if abs(corr) > 0.05:
        print("Recommendation: KEEP Isolation Forest — separation and correlation improved with new features.")
    else:
        print("Recommendation: FLAG AS LOW IMPACT — Isolation Forest adds minimal signal over supervised trees.")
        
    # ---- 3. XGBOOST TRAINING & FEATURE IMPORTANCE ----
    print("\n" + "="*70)
    print("SECTION 3: XGBOOST FEATURE IMPORTANCE")
    print("="*70)
    model = train_classifier(train_df, feature_columns_with_iso)
    
    importances = model.feature_importances_
    for fname, imp in sorted(zip(feature_columns_with_iso, importances), key=lambda x: -x[1]):
        print(f"  {fname:<35}: {imp:.4f}")
        
    # Score eval & cal
    final_iso = joblib.load('isolation_forest_final.joblib')
    final_imputer = joblib.load('iso_forest_imputer.joblib')
    
    def score_inference(df):
        X = df[feature_columns]
        X_imp = final_imputer.transform(X)
        df['iso_forest_oof_score'] = final_iso.score_samples(X_imp)
        return df
        
    cal_df = score_inference(cal_df)
    eval_df = score_inference(eval_df)
    
    # ---- 4. CALIBRATION & PROBABILITY SPREAD ----
    print("\n" + "="*70)
    print("SECTION 4: CALIBRATION SPREAD (FIX 1 VERIFICATION)")
    print("="*70)
    calibrator = calibrate_model(model, cal_df, feature_columns_with_iso)
    
    eval_theft_mask = eval_df['is_theft_ground_truth'] == True
    raw_proba = model.predict_proba(eval_df[feature_columns_with_iso])[:, 1]
    cal_proba = calibrator.predict_proba(eval_df[feature_columns_with_iso])[:, 1]
    
    print(f"Raw XGBoost Probabilities (Eval):")
    print(f"  Overall: mean={raw_proba.mean():.4f}, min={raw_proba.min():.4f}, max={raw_proba.max():.4f}")
    print(f"  Theft:   mean={raw_proba[eval_theft_mask].mean():.4f}, min={raw_proba[eval_theft_mask].min():.4f}, max={raw_proba[eval_theft_mask].max():.4f}")
    print(f"  Clean:   mean={raw_proba[~eval_theft_mask].mean():.4f}, min={raw_proba[~eval_theft_mask].min():.4f}, max={raw_proba[~eval_theft_mask].max():.4f}")
    
    print(f"\nCalibrated Probabilities (Eval):")
    print(f"  Overall: mean={cal_proba.mean():.4f}, min={cal_proba.min():.4f}, max={cal_proba.max():.4f}")
    print(f"  Theft:   mean={cal_proba[eval_theft_mask].mean():.4f}, min={cal_proba[eval_theft_mask].min():.4f}, max={cal_proba[eval_theft_mask].max():.4f}")
    print(f"  Clean:   mean={cal_proba[~eval_theft_mask].mean():.4f}, min={cal_proba[~eval_theft_mask].min():.4f}, max={cal_proba[~eval_theft_mask].max():.4f}")
    
    # ---- 5. PER-ARCHETYPE DETECTABILITY ----
    print("\n" + "="*70)
    print("SECTION 5: PER-ARCHETYPE DETECTABILITY ON EVAL SET")
    print("="*70)
    eval_df['cal_proba'] = cal_proba
    eval_df['raw_proba'] = raw_proba
    
    arch_summary = []
    for arch in sorted(eval_df['theft_type'].unique()):
        sub = eval_df[eval_df['theft_type'] == arch]
        is_theft = arch != 'none'
        flagged_05 = (sub['cal_proba'] >= 0.5).sum()
        recall_05 = flagged_05 / len(sub) if is_theft else flagged_05 / len(sub)
        arch_summary.append({
            'Archetype': arch,
            'Count': len(sub),
            'Raw Proba Mean': sub['raw_proba'].mean(),
            'Cal Proba Mean': sub['cal_proba'].mean(),
            'Flag Rate @ 0.5': recall_05
        })
    print(pd.DataFrame(arch_summary).to_string(index=False, float_format='%.4f'))
    
    # ---- 6. FORMAL EVALUATION AT THRESHOLD 0.5 ----
    print("\n" + "="*70)
    print("SECTION 6: FINAL EVALUATION AT OPERATIONAL THRESHOLD 0.5")
    print("="*70)
    run_full_evaluation(calibrator, eval_df, feature_columns_with_iso, threshold=0.5)

if __name__ == '__main__':
    main()

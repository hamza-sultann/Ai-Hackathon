import pandas as pd
import numpy as np
import joblib
from features import build_features
from isolation_forest_oof import compute_oof_anomaly_scores
from merge import merge_anomaly_score
from train_xgboost import train_classifier
from calibrate import calibrate_model, plot_reliability_curve, verify_calibration_spread
from explain import get_shap_explanations, generate_field_alert, generate_analyst_view
from evaluate import run_full_evaluation

def main():
    print("="*60)
    print("RUNNING COMPLETE ML PIPELINE (Track 1 - Monthly)")
    print("="*60)
    
    print("\n[1/7] Loading datasets...")
    train_df = pd.read_parquet('output/train.parquet')
    cal_df = pd.read_parquet('output/calibrate.parquet')
    eval_df = pd.read_parquet('output/eval.parquet')
    
    print("\n[2/7] Engineering features (including Fix 2, 3, 4)...")
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
    
    print("\n[3/7] Computing OOF Anomaly Scores with Isolation Forest...")
    train_df = compute_oof_anomaly_scores(train_df, feature_columns)
    train_df, feature_columns_with_iso = merge_anomaly_score(train_df, feature_columns)
    
    print("\n[4/7] Training XGBoost Classifier...")
    model = train_classifier(train_df, feature_columns_with_iso)
    
    # Pre-score cal and eval with final isolation forest
    final_iso = joblib.load('isolation_forest_final.joblib')
    final_imputer = joblib.load('iso_forest_imputer.joblib')
    
    def score_inference(df):
        X = df[feature_columns]
        X_imp = final_imputer.transform(X)
        df['iso_forest_oof_score'] = final_iso.score_samples(X_imp)
        return df
        
    cal_df = score_inference(cal_df)
    eval_df = score_inference(eval_df)
    
    print("\n[5/7] Calibrating model (Fix 1: ensemble=False, prefit)...")
    calibrator = calibrate_model(model, cal_df, feature_columns_with_iso)
    
    # Verify probability spread to prevent silent compression
    verify_calibration_spread(calibrator, eval_df, feature_columns_with_iso, min_expected_max=0.5)
    
    print("\n[6/7] Plotting Reliability Curve...")
    plot_reliability_curve(calibrator, eval_df, feature_columns_with_iso, output_path='output/reliability_curve.png')
    
    print("\n[7/7] Evaluating Model at standard threshold 0.5...")
    results = run_full_evaluation(calibrator, eval_df, feature_columns_with_iso, threshold=0.5)
    
    print("\n" + "="*60)
    print("EXPLAINABILITY & ALERT GENERATION (Step 7)")
    print("="*60)
    eval_df['calibrated_probability'] = calibrator.predict_proba(eval_df[feature_columns_with_iso])[:, 1]
    
    shap_df = get_shap_explanations(model, eval_df, feature_columns_with_iso, top_n=10)
    
    print("\n--- SAMPLE AUTOMATED FIELD ALERTS ---")
    for idx, row in shap_df.head(4).iterrows():
        alert = generate_field_alert(row)
        print(f"[{idx+1}] {alert}")
        
    print("\n--- ANALYST DASHBOARD VIEW (Top 5 Prioritized Flags) ---")
    view_df = generate_analyst_view(shap_df)
    print(view_df.head(5).to_string(index=False))

if __name__ == '__main__':
    main()

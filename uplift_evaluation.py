import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import precision_score, recall_score
from features import build_features
from isolation_forest_oof import compute_oof_anomaly_scores
from merge import merge_anomaly_score

# Step 1 Track 1 Features
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
    'prosumer_gated_usage_deviation'
]

# Step 2 Track 2 Features
TRACK2_FEATURES = [
    'peak_offpeak_ratio',
    'daily_load_factor',
    'flatline_fraction',
    'peak_window_flatline_fraction',
    'midday_dip_index',
    'tariff_boundary_alignment_score',
    'nighttime_drop_index'
]

def train_and_eval(train_df, eval_df, feature_cols):
    """Trains a simple XGBoost model and returns predictions on eval set"""
    neg_count = (train_df['is_theft_ground_truth'] == False).sum()
    pos_count = (train_df['is_theft_ground_truth'] == True).sum()
    scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1.0
    
    clf = xgb.XGBClassifier(
        objective='binary:logistic',
        scale_pos_weight=scale_pos_weight,
        eval_metric='aucpr',
        n_estimators=100, # smaller for fast eval
        max_depth=5,
        random_state=42
    )
    
    # Train
    X_train = train_df[feature_cols]
    y_train = train_df['is_theft_ground_truth'].astype(int)
    clf.fit(X_train, y_train)
    
    # Predict
    X_eval = eval_df[feature_cols]
    preds = clf.predict(X_eval)
    
    return preds

def main():
    print("Loading data...")
    # Load AMI subset IDs
    ami_ids = pd.read_csv('ami_consumer_ids.csv')['consumer_id'].values
    
    # Load Track 1 base data
    train_df = pd.read_parquet('output/train.parquet')
    eval_df = pd.read_parquet('output/eval.parquet')
    
    # Filter to AMI subset ONLY
    train_df = train_df[train_df['consumer_id'].isin(ami_ids)].copy()
    eval_df = eval_df[eval_df['consumer_id'].isin(ami_ids)].copy()
    
    print("Engineering Track 1 features...")
    train_df = build_features(train_df)
    eval_df = build_features(eval_df)
    
    # Isolation forest (simplified for uplift script)
    train_df = compute_oof_anomaly_scores(train_df, TRACK1_FEATURES)
    train_df, t1_cols = merge_anomaly_score(train_df, TRACK1_FEATURES)
    
    # We must train a standalone iso forest to score eval_df
    from sklearn.ensemble import IsolationForest
    iso = IsolationForest(random_state=42)
    iso.fit(train_df[TRACK1_FEATURES].fillna(0))
    eval_df['iso_forest_oof_score'] = -iso.score_samples(eval_df[TRACK1_FEATURES].fillna(0))
    
    print("Loading and joining Track 2 interval features...")
    # Read the features we computed with run_track2_features.py
    t2_df = pd.read_csv('track2_features.csv')
    
    # The Track 2 features month column was parsed as object or datetime. Let's align types.
    t2_df['month'] = pd.to_datetime(t2_df['month'])
    train_df['month'] = pd.to_datetime(train_df['month'])
    eval_df['month'] = pd.to_datetime(eval_df['month'])
    
    train_df = train_df.merge(t2_df, on=['consumer_id', 'month'], how='left')
    eval_df = eval_df.merge(t2_df, on=['consumer_id', 'month'], how='left')
    
    # Combine feature lists
    t1_t2_cols = t1_cols + TRACK2_FEATURES
    
    # Handle missing values (e.g. if the generate_intervals didn't finish completely for the eval set,
    # though it should have. We fill Track 2 NaN with median or just 0).
    train_df[TRACK2_FEATURES] = train_df[TRACK2_FEATURES].fillna(0)
    eval_df[TRACK2_FEATURES] = eval_df[TRACK2_FEATURES].fillna(0)
    
    print("\n--- Training Model 1 (Monthly Features Only) ---")
    preds_m1 = train_and_eval(train_df, eval_df, t1_cols)
    
    print("\n--- Training Model 2 (Monthly + Interval Features) ---")
    preds_m2 = train_and_eval(train_df, eval_df, t1_t2_cols)
    
    eval_df['pred_m1'] = preds_m1
    eval_df['pred_m2'] = preds_m2
    
    print("\n" + "="*70)
    print("UPLIFT PROOF: IMPACT OF SMART METERS ON DETECTION")
    print("="*70)
    
    archetypes_to_check = ['peak_hour_shaver', 'nighttime_ac', 'fixed_shunt']
    
    for arch in archetypes_to_check:
        mask = (eval_df['theft_type'] == arch)
        if not mask.any():
            continue
            
        y_true = np.ones(mask.sum()) # all in this mask are true theft
        
        y_pred_1 = eval_df.loc[mask, 'pred_m1']
        rec_1 = recall_score(y_true, y_pred_1)
        
        y_pred_2 = eval_df.loc[mask, 'pred_m2']
        rec_2 = recall_score(y_true, y_pred_2)
        
        print(f"\nArchetype: {arch.upper()}")
        print(f"  Monthly-Only Recall: {rec_1*100:5.1f}%")
        print(f"  AMI-Enabled Recall:  {rec_2*100:5.1f}%")
        print(f"  UPLIFT:              +{(rec_2 - rec_1)*100:.1f} pts")
        
    print("\nOVERALL FALSE POSITIVE RATE (Honest Consumers)")
    honest_mask = (eval_df['is_theft_ground_truth'] == False)
    fpr_1 = eval_df.loc[honest_mask, 'pred_m1'].mean()
    fpr_2 = eval_df.loc[honest_mask, 'pred_m2'].mean()
    print(f"  Monthly-Only FPR: {fpr_1*100:5.2f}%")
    print(f"  AMI-Enabled FPR:  {fpr_2*100:5.2f}%")

if __name__ == '__main__':
    main()

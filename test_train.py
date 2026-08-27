import pandas as pd
from features import build_features
from isolation_forest_oof import compute_oof_anomaly_scores
from merge import merge_anomaly_score
from train_xgboost import train_classifier, tune_with_optuna

def main():
    print("Loading train.parquet...")
    train_df = pd.read_parquet('output/train.parquet')
    
    print("Building features...")
    train_df = build_features(train_df)
    
    feature_columns = [
        'pmt_loss_delta_pct', 'usage_deviation', 'peer_deviation', 
        'arrears_ratio', 'seasonal_residual', 'rolling_trend_3mo', 
        'feeder_uptime_adj_deviation', 'prosumer_gated_usage_deviation'
    ]
    
    print("Computing OOF Anomaly Scores...")
    train_df = compute_oof_anomaly_scores(train_df, feature_columns)
    
    train_df, feature_columns = merge_anomaly_score(train_df, feature_columns)
    
    print("Training XGBoost Classifier...")
    model = train_classifier(train_df, feature_columns)
    print("Model saved to xgboost_model.json successfully.")
    
    print("Tuning with Optuna (3 trials for testing)...")
    best_params = tune_with_optuna(train_df, feature_columns, n_trials=3)
    print("Tuning complete.")

if __name__ == '__main__':
    main()

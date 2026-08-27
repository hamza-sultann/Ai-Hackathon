import pandas as pd
from features import build_features
from isolation_forest_oof import compute_oof_anomaly_scores

def main():
    print("Loading train.parquet...")
    train_df = pd.read_parquet('output/train.parquet')
    print("Building features...")
    # Taking a smaller sample to speed up for testing, just to ensure it runs
    # But wait, to get a meaningful correlation we probably want the whole train_df, 
    # which is 6000 consumers. Let's run it all.
    train_df = build_features(train_df)
    
    feature_columns = [
        'pmt_loss_delta_pct', 'usage_deviation', 'peer_deviation', 
        'arrears_ratio', 'seasonal_residual', 'rolling_trend_3mo', 
        'feeder_uptime_adj_deviation', 'prosumer_gated_usage_deviation'
    ]
    
    print("Computing OOF Anomaly Scores...")
    scored_df = compute_oof_anomaly_scores(train_df, feature_columns)
    
    print("Finished.")
    
if __name__ == '__main__':
    main()

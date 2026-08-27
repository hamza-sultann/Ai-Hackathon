import pandas as pd
from features import build_features
from isolation_forest_oof import compute_oof_anomaly_scores
from merge import merge_anomaly_score
from train_xgboost import train_classifier
from calibrate import calibrate_model, plot_reliability_curve

def main():
    print("Loading datasets...")
    train_df = pd.read_parquet('output/train.parquet')
    cal_df = pd.read_parquet('output/calibrate.parquet')
    eval_df = pd.read_parquet('output/eval.parquet')
    
    print("Building features...")
    train_df = build_features(train_df)
    cal_df = build_features(cal_df)
    eval_df = build_features(eval_df)
    
    feature_columns = [
        'pmt_loss_delta_pct', 'usage_deviation', 'peer_deviation', 
        'arrears_ratio', 'seasonal_residual', 'rolling_trend_3mo', 
        'feeder_uptime_adj_deviation', 'prosumer_gated_usage_deviation'
    ]
    
    print("Computing OOF Anomaly Scores for Train...")
    train_df = compute_oof_anomaly_scores(train_df, feature_columns)
    train_df, feature_columns = merge_anomaly_score(train_df, feature_columns)
    
    print("Training XGBoost Classifier...")
    model = train_classifier(train_df, feature_columns)
    
    # We need iso_forest_oof_score for cal_df and eval_df, but at inference time, we use the final model!
    import joblib
    final_iso = joblib.load('isolation_forest_final.joblib')
    final_imputer = joblib.load('iso_forest_imputer.joblib')
    
    def score_inference(df):
        X = df[feature_columns[:-1]]
        X_imp = final_imputer.transform(X)
        df['iso_forest_oof_score'] = final_iso.score_samples(X_imp)
        return df
        
    cal_df = score_inference(cal_df)
    eval_df = score_inference(eval_df)
    
    print("Calibrating model...")
    calibrator = calibrate_model(model, cal_df, feature_columns)
    
    print("Plotting Reliability Curve...")
    plot_reliability_curve(calibrator, eval_df, feature_columns, output_path='output/reliability_curve.png')

if __name__ == '__main__':
    main()

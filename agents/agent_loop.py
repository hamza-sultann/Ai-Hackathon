# agents/agent_loop.py



import pandas as pd
import numpy as np
import joblib
import xgboost as xgb
from sklearn.calibration import CalibratedClassifierCV
from features import build_features
import shap
import json
import os
from agents.agent_dispatcher import dispatch_agent

def main():
    """
    Main loop to process evaluation data, identify high-probability consumers,
    calculate SHAP values, and trigger the agent dispatcher.
    """
    EVAL_DATA_PATH = 'output/eval.parquet'
    CONSUMER_DATA_PATH = 'data/consumers.csv' # Assuming this holds feeder_id, prosumer status
    ISOLATION_FOREST_MODEL_PATH = 'isolation_forest_final.joblib'
    ISOLATION_FOREST_IMPUTER_PATH = 'iso_forest_imputer.joblib'
    XGBOOST_MODEL_PATH = 'xgboost_model.json' # Or potentially the calibrated model
    CALIBRATOR_PATH = 'final_calibrator.joblib' # Assumed path for the saved calibrator object
    TEMP_JSON_PATH = 'temp_flagged_input.json'

    # Feature columns used by the model (as defined in run_pipeline.py)
    FEATURE_COLUMNS_BASE = [
        'pmt_loss_delta_pct', 'usage_deviation', 'peer_deviation',
        'arrears_ratio', 'seasonal_residual', 'rolling_trend_3mo',
        'feeder_uptime_adj_deviation', 'prosumer_gated_usage_deviation'
    ]
    FEATURE_COLUMNS_WITH_ISO = FEATURE_COLUMNS_BASE + ['iso_forest_oof_score']

    print("Loading evaluation data...")
    eval_df = pd.read_parquet(EVAL_DATA_PATH)

    print("Loading pre-trained components...")
    # Load the base XGBoost model
    xgb_model = xgb.Booster()
    xgb_model.load_model(XGBOOST_MODEL_PATH)

    # Load the calibrator
    # Note: Saving/Loading a CalibratedClassifierCV wrapping XGBoost might need specific handling
    # depending on how it was saved. This assumes a standard joblib save.
    calibrator = joblib.load(CALIBRATOR_PATH)

    # Load isolation forest components for preprocessing
    final_iso = joblib.load(ISOLATION_FOREST_MODEL_PATH)
    final_imputer = joblib.load(ISOLATION_FOREST_IMPUTER_PATH)

    print("Pre-processing evaluation data (applying features and iso-forest scores)...")
    # Apply feature engineering (assuming eval_df has the raw columns needed by build_features)
    # This step might need adjustment if eval_df doesn't contain the raw inputs for build_features.
    # If eval_df already has features, this step might be skipped or adapted.
    # For now, assuming raw data is available.
    # eval_df = build_features(eval_df) 

    # Apply isolation forest score for features used by the final model
    X_eval_raw_features = eval_df[FEATURE_COLUMNS_BASE]
    X_eval_imputed = final_imputer.transform(X_eval_raw_features)
    eval_df['iso_forest_oof_score'] = final_iso.score_samples(X_eval_imputed)

    print("Calculating calibrated probabilities...")
    X_eval_model_features = eval_df[FEATURE_COLUMNS_WITH_ISO]
    # Use the calibrated model to get probabilities
    eval_df['calibrated_probability'] = calibrator.predict_proba(X_eval_model_features)[:, 1]

    print("Identifying high-probability consumers (threshold 0.75)...")
    high_prob_df = eval_df[eval_df['calibrated_probability'] > 0.75].copy()
    print(f"Found {len(high_prob_df)} consumers exceeding the 0.75 threshold.")

    if high_prob_df.empty:
        print("No consumers met the threshold. Exiting.")
        return

    print("Calculating SHAP values for high-probability consumers...")
    X_high_prob = high_prob_df[FEATURE_COLUMNS_WITH_ISO]
    
    # Use the original XGBoost model (not the calibrated wrapper) for SHAP
    explainer = shap.TreeExplainer(xgb_model)
    shap_values_matrix = explainer.shap_values(X_high_prob)

    print("Iterating through flagged consumers and dispatching agent...")
    for idx, (_, row) in enumerate(high_prob_df.iterrows()):
        consumer_id = row['consumer_id']
        
        # Extract SHAP values and raw features for this specific row
        shap_row = shap_values_matrix[idx, :]
        raw_features_row = X_high_prob.iloc[idx, :].to_dict()

        # --- FIXED SHAP DICTIONARY KEY LOGIC ---
        # Create a dictionary mapping actual feature names to their SHAP values
        # Get top 3 indices based on absolute SHAP value
        top_shap_indices = np.argsort(np.abs(shap_row))[-3:][::-1]
        
        shap_dict = {}
        raw_feat_dict = {}
        for feat_idx in top_shap_indices:
            feat_name = FEATURE_COLUMNS_WITH_ISO[feat_idx]
            # The key is the actual feature name, value is the SHAP value
            shap_dict[feat_name] = float(shap_row[feat_idx])
            # Store the corresponding raw feature value
            raw_feat_dict[feat_name] = float(raw_features_row[feat_name])
        # --- END FIX ---

        # Combine SHAP and raw features into the expected input format
        input_data = {
            "consumer_id": consumer_id,
            "shap_values": shap_dict,
            "raw_features": raw_feat_dict
        }

        # Write the input data to the temporary JSON file
        with open(TEMP_JSON_PATH, 'w') as f:
            json.dump(input_data, f)

        # --- PASS CALIBRATED PROBABILITY AND UPTIME TO DISPATCH AGENT ---
        # Fetch the relevant uptime for the confound check (e.g., from eval_df which has PMT info)
        # Assuming eval_df has 'pmt_uptime_pct' or 'feeder_uptime_pct' which was calculated during feature engineering.
        # Let's assume it's 'pmt_uptime_pct' for this consumer-month in eval_df.
        # For the agent loop, we pass the uptime value from the eval_df row for the confound check.
        consumer_uptime_pct = row.get('pmt_uptime_pct', 100.0) # Use .get with default

        print(f"\n--- Dispatching Agent for Consumer {consumer_id} (Cal. Prob: {row['calibrated_probability']:.3f}) ---")
        # Call the dispatch_agent function with the calibrated probability and uptime
        dispatch_agent(TEMP_JSON_PATH, CONSUMER_DATA_PATH, row['calibrated_probability'], consumer_uptime_pct)
        # --- END CHANGE ---


    print("\nAgent loop completed.")


if __name__ == "__main__":
    main()
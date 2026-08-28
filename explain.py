import pandas as pd
import numpy as np
import shap
from typing import List, Dict

def get_shap_explanations(xgb_model, df: pd.DataFrame, feature_columns: List[str], top_n: int = 50) -> pd.DataFrame:
    """
    Computes SHAP values for the top_n most suspicious rows.
    Assumes df already has a 'calibrated_probability' column.
    """
    if 'calibrated_probability' not in df.columns:
        raise ValueError("DataFrame must contain 'calibrated_probability'.")
        
    # Sort by probability descending and take top N
    top_df = df.sort_values(by='calibrated_probability', ascending=False).head(top_n).copy()
    
    X_top = top_df[feature_columns]
    
    # Compute SHAP
    explainer = shap.TreeExplainer(xgb_model)
    shap_values = explainer.shap_values(X_top)
    
    results = []
    
    for i in range(len(top_df)):
        row_data = top_df.iloc[i]
        row_shap = shap_values[i, :]
        
        # Get indices of top 3 features by absolute SHAP value
        top_indices = np.argsort(np.abs(row_shap))[-3:][::-1]
        
        result_dict = {
            'consumer_id': row_data['consumer_id'],
            'month': row_data['month'],
            'pmt_id': row_data.get('pmt_id', 'Unknown'),
            'calibrated_probability': row_data['calibrated_probability'],
            'is_registered_prosumer': row_data.get('is_registered_prosumer', False)
        }
        
        for rank, idx in enumerate(top_indices, 1):
            feat_name = feature_columns[idx]
            result_dict[f'top_feature_{rank}'] = feat_name
            result_dict[f'top_feature_{rank}_shap'] = row_shap[idx]
            result_dict[f'top_feature_{rank}_value'] = row_data[feat_name]
            
        results.append(result_dict)
        
    return pd.DataFrame(results)


def generate_field_alert(row: pd.Series, feature_translations: Dict[str, str] = None) -> str:
    """
    Generates a natural language SMS-style field alert.
    """
    if feature_translations is None:
        feature_translations = {
            'pmt_loss_delta_pct': 'feeder-level energy loss is unusually high',
            'pmt_loss_rank': 'neighborhood PMT ranks in top loss bracket for the grid',
            'usage_deviation': 'billed usage dropped sharply vs. recent rolling baseline',
            'fixed_baseline_deviation': 'consumption collapsed vs. verified historical reference anchor',
            'cusum_max_deviation': 'statistically significant structural break detected in consumption trajectory',
            'months_since_detected_break': 'sustained continuous deficit since detected change-point',
            'peer_deviation': 'usage is significantly lower than similar peers in same load class',
            'arrears_ratio': 'consumer carries an abnormally high unpaid balance',
            'seasonal_residual': 'usage pattern strongly defies seasonal weather norms',
            'rolling_trend_3mo': 'sustained downward trend in billing over recent months',
            'feeder_uptime_adj_deviation': 'unjustified usage drop despite consistent PMT uptime',
            'prosumer_gated_usage_deviation': 'unexplained drop (not accounted for by solar generation)',
            'iso_forest_oof_score': 'multivariate consumption profile matches rare anomaly patterns'
        }
        
    feat_1 = row.get('top_feature_1', 'Unknown feature')
    feat_2 = row.get('top_feature_2', 'Unknown feature')
    
    phrase_1 = feature_translations.get(feat_1, f'flagged by {feat_1}')
    phrase_2 = feature_translations.get(feat_2, f'flagged by {feat_2}')
    
    prob = row['calibrated_probability']
    
    alert = (f"PRIORITY CHECK: Consumer {row['consumer_id']}, PMT {row['pmt_id']}. "
             f"Confidence: {prob:.0%}. Reason: {phrase_1}, {phrase_2}.")
             
    if row.get('is_registered_prosumer', False):
        alert += " (Registered solar/net-metering on file.)"
        
    return alert


def generate_analyst_view(shap_df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a clean table view for dashboard display.
    """
    columns = [
        'consumer_id', 'pmt_id', 'calibrated_probability',
        'top_feature_1', 'top_feature_1_shap',
        'top_feature_2', 'top_feature_2_shap',
        'top_feature_3', 'top_feature_3_shap'
    ]
    
    # Filter to only columns that exist
    display_cols = [c for c in columns if c in shap_df.columns]
    
    view_df = shap_df[display_cols].copy()
    view_df = view_df.sort_values(by='calibrated_probability', ascending=False)
    
    return view_df

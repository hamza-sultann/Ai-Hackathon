import pandas as pd

def merge_anomaly_score(df: pd.DataFrame, feature_columns: list) -> tuple[pd.DataFrame, list]:
    """
    Appends the isolation forest OOF anomaly score to the feature columns list
    and ensures the score has no missing values before handing it off to XGBoost.
    """
    assert 'iso_forest_oof_score' in df.columns, "iso_forest_oof_score column is missing!"
    assert df['iso_forest_oof_score'].isna().sum() == 0, "iso_forest_oof_score contains NaNs!"
    
    updated_feature_columns = feature_columns.copy()
    if 'iso_forest_oof_score' not in updated_feature_columns:
        updated_feature_columns.append('iso_forest_oof_score')
        
    return df, updated_feature_columns

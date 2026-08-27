import pandas as pd
import pytest
from merge import merge_anomaly_score

def test_merge_anomaly_score():
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'iso_forest_oof_score': [-0.5, -0.1, -0.9]
    })
    feature_columns = ['A']
    
    out_df, new_cols = merge_anomaly_score(df, feature_columns)
    assert 'iso_forest_oof_score' in new_cols
    assert new_cols == ['A', 'iso_forest_oof_score']
    
def test_merge_anomaly_score_missing_col():
    df = pd.DataFrame({'A': [1, 2, 3]})
    with pytest.raises(AssertionError):
        merge_anomaly_score(df, ['A'])
        
def test_merge_anomaly_score_has_nans():
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'iso_forest_oof_score': [-0.5, None, -0.9]
    })
    with pytest.raises(AssertionError):
        merge_anomaly_score(df, ['A'])

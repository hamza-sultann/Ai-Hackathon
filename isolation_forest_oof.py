import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer

def compute_oof_anomaly_scores(train_df: pd.DataFrame, feature_columns: list, n_splits: int = 5, random_state: int = 42) -> pd.DataFrame:
    """
    Computes Out-Of-Fold anomaly scores using IsolationForest, avoiding leakage by grouping 
    on consumer_id, and imputing NaNs safely inside the CV loop.
    """
    df = train_df.copy()
    
    # We need to preserve the original index to reassemble correctly
    original_index = df.index
    df = df.reset_index(drop=True)
    
    oof_scores = np.zeros(len(df))
    
    # Wait, GroupKFold requires the number of groups to be >= n_splits
    groups = df['consumer_id']
    n_groups = groups.nunique()
    actual_n_splits = min(n_splits, n_groups)
    if actual_n_splits < 2:
        # Fallback if there's only 1 group (for toy testing)
        actual_n_splits = 2
        groups = np.arange(len(df))
        
    gkf = GroupKFold(n_splits=actual_n_splits)
    
    # 1-4. GroupKFold loop for OOF scores
    # 5. Impute NaNs strictly per-fold
    for fold, (train_idx, val_idx) in enumerate(gkf.split(df, groups=groups)):
        X_train = df.loc[train_idx, feature_columns].copy()
        X_val = df.loc[val_idx, feature_columns].copy()
        
        imputer = SimpleImputer(strategy='median')
        X_train_imputed = imputer.fit_transform(X_train)
        X_val_imputed = imputer.transform(X_val)
        
        iso_forest = IsolationForest(
            n_estimators=200, 
            contamination='auto', 
            random_state=random_state
        )
        
        iso_forest.fit(X_train_imputed)
        
        # more negative = more anomalous
        fold_scores = iso_forest.score_samples(X_val_imputed)
        oof_scores[val_idx] = fold_scores
        
    df['iso_forest_oof_score'] = oof_scores
    
    # Restore the original index
    df.index = original_index
    
    # 6. Fit final model on FULL training set
    X_full = df[feature_columns].copy()
    final_imputer = SimpleImputer(strategy='median')
    X_full_imputed = final_imputer.fit_transform(X_full)
    
    final_iso_forest = IsolationForest(
        n_estimators=200, 
        contamination='auto', 
        random_state=random_state
    )
    final_iso_forest.fit(X_full_imputed)
    
    joblib.dump(final_iso_forest, 'isolation_forest_final.joblib')
    joblib.dump(final_imputer, 'iso_forest_imputer.joblib')
    
    # 7. Print correlation with ground truth
    if 'is_theft_ground_truth' in df.columns:
        # iso_forest scores are negative for anomalies.
        # ground_truth=1 (theft) should correlate with more negative scores.
        # Thus correlation should be negative.
        corr = df['iso_forest_oof_score'].corr(df['is_theft_ground_truth'].astype(float))
        print(f"Correlation between iso_forest_oof_score and is_theft_ground_truth: {corr:.4f}")
        
    return df

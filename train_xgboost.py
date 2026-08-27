import pandas as pd
import xgboost as xgb
from typing import List, Dict
import warnings

def train_classifier(
    train_df: pd.DataFrame, 
    feature_columns: List[str], 
    label_column: str = 'is_theft_ground_truth', 
    random_state: int = 42,
    n_estimators: int = 300,
    max_depth: int = 5,
    learning_rate: float = 0.05,
    **kwargs
) -> xgb.XGBClassifier:
    """
    Trains an XGBoost classifier for theft detection using handling for imbalanced classes.
    """
    # 1. Compute scale_pos_weight
    neg_count = (train_df[label_column] == False).sum()
    pos_count = (train_df[label_column] == True).sum()
    
    if pos_count == 0:
        raise ValueError("No positive examples found in training data.")
        
    scale_pos_weight = float(neg_count) / pos_count
    
    # 2. Initialize XGBClassifier
    clf = xgb.XGBClassifier(
        objective='binary:logistic',
        scale_pos_weight=scale_pos_weight,
        eval_metric='aucpr',
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        random_state=random_state,
        **kwargs
    )
    
    # 3. Fit the model
    # Convert bool to int for XGBoost compatibility
    y = train_df[label_column].astype(int)
    X = train_df[feature_columns]
    
    clf.fit(X, y)
    
    # 6. Save the trained model
    clf.save_model('xgboost_model.json')
    
    # 4. Return the fitted model
    return clf


# 5. Optional Optuna tuning
# NOTE: This is optional/stretch. The plain train_classifier function above works standalone without Optuna.
def tune_with_optuna(
    train_df: pd.DataFrame, 
    feature_columns: List[str], 
    label_column: str = 'is_theft_ground_truth', 
    n_trials: int = 30,
    random_state: int = 42
) -> Dict:
    """
    Runs a quick Optuna study to find the best hyperparameters.
    Uses 5-fold cross-validated PR-AUC, grouped by consumer_id to prevent leakage.
    """
    try:
        import optuna
        from sklearn.model_selection import GroupKFold
        import sklearn.metrics as metrics
        import numpy as np
    except ImportError:
        warnings.warn("Optuna or scikit-learn is not installed. Returning default hyperparameters.")
        return {'max_depth': 5, 'learning_rate': 0.05, 'n_estimators': 300}
        
    def objective(trial):
        params = {
            'max_depth': trial.suggest_int('max_depth', 3, 9),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'n_estimators': trial.suggest_int('n_estimators', 100, 500),
            'subsample': trial.suggest_float('subsample', 0.5, 1.0)
        }
        
        groups = train_df['consumer_id']
        n_groups = groups.nunique()
        actual_n_splits = min(5, n_groups)
        if actual_n_splits < 2:
             actual_n_splits = 2
             groups = np.arange(len(train_df))
             
        gkf = GroupKFold(n_splits=actual_n_splits)
        
        pr_aucs = []
        
        # Ensure resetting index so iloc works flawlessly
        df_reset = train_df.reset_index(drop=True)
        groups_reset = groups.reset_index(drop=True)
        
        for train_idx, val_idx in gkf.split(df_reset, groups=groups_reset):
            X_train = df_reset.loc[train_idx, feature_columns]
            y_train = df_reset.loc[train_idx, label_column].astype(int)
            
            X_val = df_reset.loc[val_idx, feature_columns]
            y_val = df_reset.loc[val_idx, label_column].astype(int)
            
            neg_count = (y_train == 0).sum()
            pos_count = (y_train == 1).sum()
            spw = float(neg_count) / max(1, pos_count)
            
            model = xgb.XGBClassifier(
                objective='binary:logistic',
                scale_pos_weight=spw,
                eval_metric='aucpr',
                random_state=random_state,
                **params
            )
            
            model.fit(X_train, y_train)
            
            y_pred_proba = model.predict_proba(X_val)[:, 1]
            
            # calculate PR-AUC
            precision, recall, _ = metrics.precision_recall_curve(y_val, y_pred_proba)
            auc_pr = metrics.auc(recall, precision)
            pr_aucs.append(auc_pr)
            
        return np.mean(pr_aucs)
        
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction='maximize', sampler=optuna.samplers.TPESampler(seed=random_state))
    study.optimize(objective, n_trials=n_trials)
    
    print(f"Best trial PR-AUC: {study.best_value:.4f}")
    print(f"Best params: {study.best_params}")
    
    return study.best_params

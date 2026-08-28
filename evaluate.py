import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, average_precision_score

def run_full_evaluation(
    calibrated_model, 
    eval_df: pd.DataFrame, 
    feature_columns: list, 
    label_column: str = 'is_theft_ground_truth', 
    archetype_column: str = 'theft_type',
    threshold: float = 0.5,
    low_uptime_threshold: float = 80.0
) -> dict:
    """
    Evaluates the model against specific theft archetypes and fairness constraints.
    """
    X_eval = eval_df[feature_columns]
    y_true = eval_df[label_column].astype(int)
    
    # 1. Predictions
    y_prob = calibrated_model.predict_proba(X_eval)[:, 1]
    y_pred = (y_prob >= threshold).astype(int)
    
    # Per-theft-type metrics
    archetypes = eval_df[archetype_column].unique()
    archetype_results = []
    
    for arch in archetypes:
        if arch == 'none':
            continue
            
        # Treat this specific archetype as positive class, 'none' as negative.
        # Ignore other theft types for this calculation to see isolation capability.
        mask = (eval_df[archetype_column] == arch) | (eval_df[archetype_column] == 'none')
        
        y_true_arch = (eval_df.loc[mask, archetype_column] == arch).astype(int)
        y_pred_arch = y_pred[mask]
        
        precision = precision_score(y_true_arch, y_pred_arch, zero_division=0)
        recall = recall_score(y_true_arch, y_pred_arch, zero_division=0)
        f1 = f1_score(y_true_arch, y_pred_arch, zero_division=0)
        
        archetype_results.append({
            'Archetype': arch,
            'Precision': precision,
            'Recall': recall,
            'F1': f1
        })
        
    overall_precision = precision_score(y_true, y_pred, zero_division=0)
    overall_recall = recall_score(y_true, y_pred, zero_division=0)
    overall_f1 = f1_score(y_true, y_pred, zero_division=0)
    pr_auc = average_precision_score(y_true, y_prob)
    
    # 2. Solar/prosumer false-positive rate
    prosumer_legit_mask = (eval_df['is_registered_prosumer'] == True) & (y_true == 0)
    prosumer_legit_total = prosumer_legit_mask.sum()
    prosumer_flagged = (y_pred[prosumer_legit_mask] == 1).sum()
    
    prosumer_fpr = prosumer_flagged / max(1, prosumer_legit_total)
    
    if prosumer_fpr > 0.05:
        print(f"WARNING: Solar/Prosumer False Positive Rate is high! ({prosumer_fpr:.1%})")
        
    # 3. Load-shedding false-positive rate
    uptime_legit_mask = (eval_df['pmt_uptime_pct'] < low_uptime_threshold) & (y_true == 0)
    uptime_legit_total = uptime_legit_mask.sum()
    uptime_flagged = (y_pred[uptime_legit_mask] == 1).sum()
    
    uptime_fpr = uptime_flagged / max(1, uptime_legit_total)
    
    # 4. Naive baseline comparison: 'flag if usage_deviation < -0.5'
    naive_pred = (eval_df['usage_deviation'] < -0.5).astype(int)
    naive_precision = precision_score(y_true, naive_pred, zero_division=0)
    naive_recall = recall_score(y_true, naive_pred, zero_division=0)
    naive_f1 = f1_score(y_true, naive_pred, zero_division=0)
    
    # Print Summary
    print("="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    print(f"Overall Precision: {overall_precision:.3f}")
    print(f"Overall Recall:    {overall_recall:.3f}")
    print(f"Overall F1:        {overall_f1:.3f}")
    print(f"Overall PR-AUC:    {pr_auc:.3f}")
    print("-"*60)
    print("PER-ARCHETYPE METRICS (vs Normal)")
    arch_df = pd.DataFrame(archetype_results)
    if not arch_df.empty:
        print(arch_df.to_string(index=False, float_format="%.3f"))
    print("-"*60)
    print(f"Prosumer FPR (Target < 5%):      {prosumer_fpr:.2%}")
    print(f"Low-Uptime FPR:                  {uptime_fpr:.2%}")
    print("-"*60)
    print("NAIVE BASELINE (usage_deviation < -0.5)")
    print(f"Naive Precision: {naive_precision:.3f}")
    print(f"Naive Recall:    {naive_recall:.3f}")
    print(f"Naive F1:        {naive_f1:.3f}")
    print("="*60)
    
    return {
        'overall': {
            'precision': overall_precision,
            'recall': overall_recall,
            'f1': overall_f1,
            'pr_auc': pr_auc
        },
        'archetypes': archetype_results,
        'fairness': {
            'prosumer_fpr': prosumer_fpr,
            'uptime_fpr': uptime_fpr
        },
        'naive': {
            'precision': naive_precision,
            'recall': naive_recall,
            'f1': naive_f1
        }
    }

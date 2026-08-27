import pandas as pd
import matplotlib.pyplot as plt
from sklearn.calibration import CalibratedClassifierCV, calibration_curve

def calibrate_model(
    trained_xgb_model, 
    calibrate_df: pd.DataFrame, 
    feature_columns: list, 
    label_column: str = 'is_theft_ground_truth', 
    method: str = 'sigmoid'
) -> CalibratedClassifierCV:
    """
    Fits a probability calibrator on a dedicated calibration dataset.
    """
    X_cal = calibrate_df[feature_columns]
    y_cal = calibrate_df[label_column].astype(int)
    
    # We use FrozenEstimator because the XGBoost model is already trained
    from sklearn.frozen import FrozenEstimator
    
    calibrator = CalibratedClassifierCV(
        estimator=FrozenEstimator(trained_xgb_model), 
        method=method, 
        cv=None  # or "prefit" equivalent functionality
    )
    
    calibrator.fit(X_cal, y_cal)
    return calibrator

def plot_reliability_curve(
    calibrator, 
    eval_df: pd.DataFrame, 
    feature_columns: list, 
    label_column: str = 'is_theft_ground_truth', 
    output_path: str = 'reliability_curve.png'
):
    """
    Evaluates calibration by plotting a reliability curve on the EVALUATION split,
    and saves the underlying bin data to CSV.
    """
    X_eval = eval_df[feature_columns]
    y_eval = eval_df[label_column].astype(int)
    
    # predict_proba returns [prob_class_0, prob_class_1]
    y_prob = calibrator.predict_proba(X_eval)[:, 1]
    
    fraction_of_positives, mean_predicted_value = calibration_curve(
        y_eval, y_prob, n_bins=10, strategy='uniform'
    )
    
    # Save plot
    plt.figure(figsize=(8, 8))
    plt.plot(mean_predicted_value, fraction_of_positives, 's-', label='Calibrated XGBoost')
    plt.plot([0, 1], [0, 1], 'k--', label='Perfectly Calibrated')
    
    plt.xlabel('Mean predicted probability per bin')
    plt.ylabel('Actual fraction positive per bin')
    plt.title('Reliability Curve (Calibration)')
    plt.legend(loc='lower right')
    plt.grid(True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    
    # Save underlying bin data to CSV
    bin_data = pd.DataFrame({
        'mean_predicted_probability': mean_predicted_value,
        'actual_fraction_positive': fraction_of_positives
    })
    
    # derive csv path from output_path
    csv_path = output_path.rsplit('.', 1)[0] + '_bins.csv'
    bin_data.to_csv(csv_path, index=False)
    
    print(f"Saved reliability plot to {output_path}")
    print(f"Saved bin data to {csv_path}")

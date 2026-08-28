import pandas as pd
import numpy as np
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
    
    Fix 1: Uses ensemble=False with FrozenEstimator to ensure calibration fits
    a single sigmoid (Platt scaling) transformation on the pre-trained model's
    outputs without internal cross-validation refitting.
    """
    X_cal = calibrate_df[feature_columns]
    y_cal = calibrate_df[label_column].astype(int)
    
    from sklearn.frozen import FrozenEstimator
    
    calibrator = CalibratedClassifierCV(
        estimator=FrozenEstimator(trained_xgb_model), 
        method=method, 
        ensemble=False
    )
    
    calibrator.fit(X_cal, y_cal)
    return calibrator

def verify_calibration_spread(calibrator, eval_df: pd.DataFrame, feature_columns: list, min_expected_max: float = 0.5):
    """
    Verifies that calibrated probabilities span an operational range (max probability >= min_expected_max).
    Fails loudly if calibration compression is detected.
    """
    X_eval = eval_df[feature_columns]
    y_prob = calibrator.predict_proba(X_eval)[:, 1]
    max_prob = float(np.max(y_prob))
    mean_prob = float(np.mean(y_prob))
    min_prob = float(np.min(y_prob))
    
    print(f"Calibration Spread Check on Eval: min={min_prob:.4f}, mean={mean_prob:.4f}, max={max_prob:.4f}")
    if max_prob < min_expected_max:
        raise ValueError(
            f"CALIBRATION COMPRESSION DETECTED! Max calibrated probability across eval set is {max_prob:.4f}, "
            f"which is below the threshold of {min_expected_max:.2f}. The model will produce 0 positive predictions."
        )
    print(f"PASS: Max calibrated probability ({max_prob:.2%}) comfortably exceeds operational threshold ({min_expected_max:.0%}).")
    return y_prob

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

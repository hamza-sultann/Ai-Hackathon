# agent_dispatcher.py

import pandas as pd
import json

def generate_investigation_report(consumer_id, shap_values, raw_features, feeder_status, prosumer_status):
    """
    Generates a natural-language field investigation report for a utility line worker.

    Args:
        consumer_id (str): Unique identifier for the consumer.
        shap_values (dict): Dictionary of feature names to their SHAP contribution values.
        raw_features (dict): Dictionary of feature names to their raw values.
        feeder_status (str): Status of the feeder (e.g., "Normal", "High Loss").
        prosumer_status (bool): Whether the consumer is a registered prosumer.

    Returns:
        str: Formatted investigation report.
    """
    # Example logic to interpret SHAP values and features
    # This would be replaced with actual business logic based on model insights
    primary_anomaly_indicators = []
    for feature, shap_val in shap_values.items():
        if abs(shap_val) > 0.1: # Threshold for significance
            direction = "higher" if shap_val > 0 else "lower"
            primary_anomaly_indicators.append(f"- {feature}: Unusually {direction} ({raw_features[feature]:.2f})")

    # Construct the report
    report_lines = [
        f"FIELD INVESTIGATION REPORT",
        f"========================",
        f"Consumer ID: {consumer_id}",
        f"Feeder Status: {feeder_status}",
        f"Prosumer Status: {'Registered Prosumer' if prosumer_status else 'Standard Consumer'}",
        "",
        "SUMMARY OF ANOMALIES:",
        "---------------------",
        "Model flagged this account due to the following significant deviations:",
    ]
    
    if primary_anomaly_indicators:
        report_lines.extend(primary_anomaly_indicators)
    else:
        report_lines.append("- No major individual feature deviations found above threshold.")

    report_lines.extend([
        "",
        "RECOMMENDATIONS FOR LINE WORKER:",
        "--------------------------------",
        "- Inspect meter for physical tampering (bypass, acceleration, etc.).",
        "- Verify load connection integrity.",
        "- Check for unauthorized connections downstream of the meter.",
        "- If on a high-loss feeder, investigate upstream/downstream neighbors as well.",
        "- If prosumer, also verify net-metering equipment integrity."
    ])

    return "\n".join(report_lines)


def dispatch_agent(input_data_path, consumer_data_path):
    """
    Main function to read input data, query statuses, and generate reports.

    Args:
        input_data_path (str): Path to JSON file containing flagged consumer data (SHAP, features).
        consumer_data_path (str): Path to CSV file containing master consumer list with feeder/prosumer status.
    """
    # Load consumer master data
    consumer_df = pd.read_csv(consumer_data_path)

    # Load flagged consumer data (example format)
    with open(input_data_path, 'r') as f:
        input_data = json.load(f)

    # Example structure of input_data:
    # {"consumer_id": "C-000001", "shap_values": {"pmt_loss_delta_pct": 0.15, ...}, "raw_features": {...}}
    
    consumer_id = input_data["consumer_id"]
    
    # Query feeder and prosumer status from master data
    consumer_row = consumer_df[consumer_df["consumer_id"] == consumer_id].iloc[0]
    feeder_status = consumer_row["feeder_id"] # Or a derived status column if available
    prosumer_status = consumer_row["is_registered_prosumer"]

    # Generate and print report
    report = generate_investigation_report(
        consumer_id=input_data["consumer_id"],
        shap_values=input_data["shap_values"],
        raw_features=input_data["raw_features"],
        feeder_status=feeder_status,
        prosumer_status=prosumer_status
    )
    
    print(report)


if __name__ == "__main__":
    # Example usage
    # The paths below are placeholders and need to be updated to point to real data files.
    dispatch_agent("input_flagged_consumer.json", "master_consumer_list.csv")

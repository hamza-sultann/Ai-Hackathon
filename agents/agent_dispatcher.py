# agent_dispatcher.py

import pandas as pd
import json
from datetime import datetime, timezone

def check_confound(consumer_id, prosumer_status, uptime_pct, calibrated_probability):
    """
    Checks for confounding factors. Logs and returns True if the alert should be cancelled.
    """
    # Assume a low uptime (e.g., < 20%) is a confound indicating systemic issues
    if prosumer_status or (uptime_pct is not None and uptime_pct < 20.0):
        print(f"Alert for Consumer {consumer_id} was 'Cancelled by Confound Agent'")
        # Log cancellation
        log_audit(consumer_id, calibrated_probability, {}, "Cancelled by Confound Agent")
        return True
    return False

def send_soft_warning(consumer_id, shap_values, raw_features, calibrated_probability):
    """
    Sends a soft warning SMS if probability is in the specified range. Logs and returns True if sent.
    """
    if 0.65 <= calibrated_probability <= 0.70:
        if shap_values:
            primary_feature = max(shap_values.keys(), key=lambda k: abs(shap_values[k]))
            primary_value = raw_features[primary_feature]
            warning_sms = f"ATTENTION {consumer_id}: Potential anomaly detected in {primary_feature.replace('_', ' ').upper()} ({primary_value:.2f}). Please verify your setup."

            # Mask PII for the message
            masked_warning_sms = mask_pii(warning_sms, consumer_id)
            print(f"SOFT WARNING SMS SENT: {masked_warning_sms}")

            # Log the soft warning action
            log_audit(consumer_id, calibrated_probability, shap_values, "Sent Soft Warning SMS")
            return True
    return False

def route_to_dual_channel(consumer_id, shap_values, raw_features, feeder_status, prosumer_status):
    """
    Generates and prints both Analyst View and Field Alert.
    """
    if not shap_values:
        return

    # Analyst View (Detailed)
    analyst_view = generate_investigation_report(
        consumer_id=consumer_id,
        shap_values=shap_values,
        raw_features=raw_features,
        feeder_status=feeder_status,
        prosumer_status=prosumer_status
    )
    print("\n--- ANALYST VIEW ---")
    print(analyst_view)

    # Field Alert (SMS format)
    primary_feature = max(shap_values.keys(), key=lambda k: abs(shap_values[k]))
    primary_value = raw_features[primary_feature]
    field_alert = f"INVESTIGATE {consumer_id}: High risk consumer. Primary indicator: {primary_feature.replace('_', ' ').upper()} ({primary_value:.2f})."

    # Mask PII for the alert
    masked_field_alert = mask_pii(field_alert, consumer_id)

    print("\n--- FIELD ALERT ---")
    print(masked_field_alert)

def mask_pii(text, consumer_id):
    """
    Masks the consumer ID in the given text.
    """
    masked_id = "C-***" + consumer_id[-3:] if len(consumer_id) >= 3 else consumer_id
    return text.replace(consumer_id, masked_id)

def log_audit(consumer_id, calibrated_probability, shap_values, routing_decision):
    """
    Logs the action to the audit log file.
    """
    audit_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "consumer_id": consumer_id,
        "calibrated_probability": calibrated_probability,
        "shap_rationale": shap_values,
        "routing_decision": routing_decision
    }
    with open("audit_log.jsonl", "a") as log_file:
        log_file.write(json.dumps(audit_record) + "\n")

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


def dispatch_agent(input_data_path, consumer_data_path, calibrated_probability=None, feeder_uptime_pct=None):
    """
    Main function to read input data, query statuses, and generate reports with multi-agent checks.

    Args:
        input_data_path (str): Path to JSON file containing flagged consumer data (SHAP, features).
        consumer_data_path (str): Path to CSV file containing master consumer list with feeder/prosumer status.
        calibrated_probability (float, optional): The calibrated probability from the model.
        feeder_uptime_pct (float, optional): The uptime percentage for the consumer's feeder/PMT.
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

    # --- AGENT LOGIC BEGINS - Orchestrated by calling helper functions ---
    
    # 1. Confound Checker
    if check_confound(consumer_id, prosumer_status, feeder_uptime_pct, calibrated_probability):
        return # Exit early if confounded

    # 2. Soft-Warning Agent
    if send_soft_warning(consumer_id, shap_values, raw_features, calibrated_probability):
        return # Exit after sending soft warning

    # 3. Dual-Router (only reached if no confound or soft warning)
    route_to_dual_channel(consumer_id, shap_values, raw_features, feeder_status, prosumer_status)

    # 4. Audit Logger (for non-canceled, non-soft-warning actions)
    log_audit(consumer_id, calibrated_probability, shap_values, "Sent Analyst View and Field Alert")
    # --- AGENT LOGIC ENDS ---


if __name__ == "__main__":
    # Example usage
    # The paths below are placeholders and need to be updated to point to real data files.
    # This signature is now outdated. The function requires calibrated_probability and feeder_uptime_pct.
    # dispatch_agent("input_flagged_consumer.json", "master_consumer_list.csv", 0.85, 95.0)
    pass # Placeholder for main execution which is handled by agent_loop.py
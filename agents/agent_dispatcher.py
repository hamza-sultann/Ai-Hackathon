import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import pandas as pd
import json
from datetime import datetime, timezone, timedelta
from deep_translator import GoogleTranslator
import os

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

def recidivism_checker(consumer_id):
    """Checks if the consumer has been flagged before in our own log."""
    if not os.path.exists("audit_log.jsonl"):
        return False
        
    flag_count = 0
    with open("audit_log.jsonl", "r") as f:
        for line in f:
            record = json.loads(line)
            if record.get("consumer_id") == consumer_id:
                flag_count += 1
                
    # If they've been flagged more than once before, they are a repeat offender
    return flag_count > 1

def case_dedup_guard(consumer_id):
    """
    Checks if the consumer is already under investigation.
    Returns True if alerted within the last 1 minute (demo mode) to prevent spam.
    """
    if not os.path.exists("audit_log.jsonl"):
        return False
        
    now = datetime.now(timezone.utc)
    
    with open("audit_log.jsonl", "r") as f:
        # Read the log to find recent alerts
        for line in f:
            try:
                record = json.loads(line)
                if record.get("consumer_id") == consumer_id:
                    # Parse timestamp string back into datetime object
                    log_time = datetime.fromisoformat(record.get("timestamp"))
                    
                    # For Hackathon Demo: Block if last alert was less than 1 minute ago
                    if now - log_time < timedelta(minutes=1):
                        return True
            except Exception:
                continue
                
    return False
def seasonal_agent(base_threshold):
    """Adjusts the base probability threshold based on the current season."""
    current_month = datetime.now().month
    
    # Summer/Monsoon (June to August) - Theft is more common (AC spikes)
    # Lower the threshold slightly to catch more cases
    if current_month in [6, 7, 8]:
        return base_threshold - 0.05
        
    # Winter (December to February) - Theft is less common
    # Raise the threshold to prevent false alarms
    elif current_month in [12, 1, 2]:
        return base_threshold + 0.05
        
    return base_threshold

def urdu_localization_agent(text_in_english):
    """Translates the English text into Urdu."""
    try:
        # Uses the free Google Translate endpoint
        translated = GoogleTranslator(source='en', target='ur').translate(text_in_english)
        return translated
    except Exception as e:
        print(f"Translation failed: {e}")
        return text_in_english # Fallback to English if it fails

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
            
            # --- INTEGRATE URDU LOCALIZATION ---
            localized_warning_sms = urdu_localization_agent(masked_warning_sms)
            print(f"SOFT WARNING SMS SENT: {localized_warning_sms}")

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
    
    # --- INTEGRATE URDU LOCALIZATION ---
    localized_field_alert = urdu_localization_agent(masked_field_alert)

    print("\n--- FIELD ALERT ---")
    print(localized_field_alert)

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

    consumer_id = input_data["consumer_id"]
    shap_values = input_data["shap_values"]
    raw_features = input_data["raw_features"]
    
    # Query feeder and prosumer status from master data
    consumer_row = consumer_df[consumer_df["consumer_id"] == consumer_id].iloc[0]
    feeder_status = consumer_row["feeder_id"]
    prosumer_status = consumer_row["is_registered_prosumer"]

    # --- NEW AGENT LOGIC INTEGRATION ---
    # Case Deduplication Check (early exit if already under investigation)
    if case_dedup_guard(consumer_id):
        print(f"Consumer {consumer_id} is already under investigation. Skipping dispatch.")
        log_audit(consumer_id, calibrated_probability, shap_values, "Skipped - Already Under Investigation")
        return # Exit early

    # Recidivism Check (could elevate priority or probability)
    is_recidivist = recidivism_checker(consumer_id)
    if is_recidivist:
        print(f"Consumer {consumer_id} is a recidivist. Elevating priority.")
        # Example: Slightly increase the effective probability or set a high-priority flag
        effective_probability = min(calibrated_probability + 0.05, 1.0) # Boost slightly
    else:
        effective_probability = calibrated_probability

    # --- ORIGINAL AGENT LOGIC BEGINS - Orchestrated by calling helper functions ---
    
    # 1. Confound Checker (uses original or boosted probability)
    if check_confound(consumer_id, prosumer_status, feeder_uptime_pct, effective_probability):
        return # Exit early if confounded

    # 2. Soft-Warning Agent (uses original or boosted probability)
    # The seasonal agent would typically adjust the THRESHOLD in agent_loop.py,
    # not within dispatch_agent, but here's a conceptual placeholder if needed.
    # For now, use effective_probability directly.
    if send_soft_warning(consumer_id, shap_values, raw_features, effective_probability):
        return # Exit after sending soft warning

    # 3. Dual-Router (only reached if no confound or soft warning)
    route_to_dual_channel(consumer_id, shap_values, raw_features, feeder_status, prosumer_status)

    # 4. Audit Logger (for non-canceled, non-soft-warning actions)
    log_audit(consumer_id, effective_probability, shap_values, "Sent Analyst View and Field Alert")
    # --- AGENT LOGIC ENDS ---


if __name__ == "__main__":
    # Example usage
    # The paths below are placeholders and need to be updated to point to real data files.
    # This signature is now outdated. The function requires calibrated_probability and feeder_uptime_pct.
    # dispatch_agent("input_flagged_consumer.json", "master_consumer_list.csv", 0.85, 95.0)
    pass # Placeholder for main execution which is handled by agent_loop.py
import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Utility Dispatch Dashboard", layout="wide")
st.title("⚡ Electricity Theft Dispatch Center")

def load_data():
    # Read the audit log JSONL file line by line
    data = []
    try:
        with open("audit_log.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                data.append(json.loads(line))
        return pd.DataFrame(data)
    except FileNotFoundError:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # Reverse to show newest alerts first
    df = df.iloc[::-1]
    
    st.subheader("Recent Dispatch Alerts")
    for _, row in df.iterrows():
        with st.expander(f"Alert: {row['consumer_id']} - {row['routing_decision']}"):
            st.write(f"**Confidence Score:** {row.get('calibrated_probability', 0):.2%}")
            st.write(f"**Timestamp:** {row['timestamp']}")
            
            # The Urdu text will render perfectly connected here!
            st.json(row.get('shap_rationale', {}))
else:
    st.info("No alerts generated yet. Run the agent loop!")
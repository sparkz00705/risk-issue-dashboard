import pandas as pd
import streamlit as st

st.subheader("🔗 Requirements Traceability Matrix (RTM)")
st.markdown("Ensure every requirement is tracked, verified, and mapped to a real risk and test case.")

# --- 1. UPLOAD SECTION FIRST ---
st.subheader("📁 Data Source Management")

uploaded_rtm_file = st.file_uploader(
    "Upload filled-in Requirements CSV/Excel:", type=["csv", "xlsx"], key="rtm_up"
)

if uploaded_rtm_file is not None:
    try:
        data_rtm = (
            pd.read_csv(uploaded_rtm_file)
            if uploaded_rtm_file.name.endswith(".csv")
            else pd.read_excel(uploaded_rtm_file)
        )
        st.success("Custom Requirements dataset loaded successfully!")
    except Exception:
        data_rtm = pd.DataFrame({
            "Req_ID": ["REQ-001", "REQ-002", "REQ-003", "REQ-004"],
            "Requirement_Title": [
                "OAuth2 Authentication",
                "Sub-second Response Times",
                "GDPR Data Export",
                "Multi-region Failover",
            ],
            "Category": ["Security", "Performance", "Compliance", "Infrastructure"],
            "Linked_Risk": ["RSK-001", "RSK-002", "None", "RSK-005"],
            "Test_Status": ["Passed", "Failed", "Pending", "Passed"],
            "Verification_Method": ["Automated Test", "Load Test", "Manual Review", "Chaos Test"],
        })
else:
    data_rtm = pd.DataFrame({
        "Req_ID": ["REQ-001", "REQ-002", "REQ-003", "REQ-004"],
        "Requirement_Title": [
            "OAuth2 Authentication",
            "Sub-second Response Times",
            "GDPR Data Export",
            "Multi-region Failover",
        ],
        "Category": ["Security", "Performance", "Compliance", "Infrastructure"],
        "Linked_Risk": ["RSK-001", "RSK-002", "None", "RSK-005"],
        "Test_Status": ["Passed", "Failed", "Pending", "Passed"],
        "Verification_Method": ["Automated Test", "Load Test", "Manual Review", "Chaos Test"],
    })

# --- 2. DOWNLOAD TEMPLATE SECTION SECOND ---
rtm_template = pd.DataFrame({
    "Req_ID": ["REQ-001", "REQ-002"],
    "Requirement_Title": ["User Login Security", "API Speed"],
    "Category": ["Security", "Performance"],
    "Linked_Risk": ["RSK-001", "RSK-002"],
    "Test_Status": ["Pending", "Pending"],
    "Verification_Method": ["Automated Test", "Load Test"],
})
rtm_csv = rtm_template.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Requirements Template",
    data=rtm_csv,
    file_name="rtm_template.csv",
    mime="text/csv",
)

st.markdown("---")

# --- KPI METRICS ---
col1, col2, col3, col4 = st.columns(4)
total_reqs = len(data_rtm)
passed_reqs = len(data_rtm[data_rtm["Test_Status"] == "Passed"])
coverage = (passed_reqs / total_reqs * 100) if total_reqs > 0 else 0
unmapped = len(data_rtm[data_rtm["Linked_Risk"].astype(str).str.lower().isin(["none", "nan", ""])])

col1.metric("Coverage Health", f"{coverage:.1f}%")
col2.metric("Total Requirements", total_reqs)
col3.metric("Unmapped Requirements", unmapped)
col4.metric("Passed Tests", passed_reqs)

st.markdown("---")

# --- RTM TABLE DISPLAY ---
st.subheader("📋 Traceability Matrix Table")
st.dataframe(data_rtm, use_container_width=True)

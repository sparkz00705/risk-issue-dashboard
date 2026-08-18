import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION & NAVIGATION SETUP ---
st.set_page_config(
    page_title="Intelligent Risk Management",
    layout="wide",
    page_icon="🛡️",
)

# --- INITIALIZE SHARED SESSION STATE (DATA SYNC) ---
if "data_risks" not in st.session_state:
    st.session_state["data_risks"] = pd.DataFrame({
        "ID": ["RSK-001", "RSK-002", "RSK-003", "RSK-004", "RSK-005"],
        "Title": [
            "API Gateway Latency",
            "Key Developer Turnover",
            "Third-party Vendor Delay",
            "Compliance Scope Creep",
            "Database Scalability Limit",
        ],
        "Category": ["Technical", "Resource", "Supply Chain", "Legal", "Technical"],
        "Probability": ["High", "Medium", "Low", "High", "Medium"],
        "Impact": ["Critical", "High", "Medium", "High", "Critical"],
        "Score": [15, 9, 4, 12, 10],
        "Status": ["Open", "Open", "Mitigated", "Open", "Materialized"],
        "Financial_Impact_USD": [50000, 30000, 15000, 40000, 60000],
        "Schedule_Delay_Days": [14, 21, 7, 30, 14],
    })

if "data_issues" not in st.session_state:
    st.session_state["data_issues"] = pd.DataFrame({
        "ID": ["ISS-001", "ISS-002", "ISS-003"],
        "Title": [
            "Auth Service Outage",
            "Client Rejected Prototype",
            "Staging Environment Down",
        ],
        "Category": ["Technical", "Product", "Infrastructure"],
        "Severity": ["Critical", "High", "High"],
        "Status": ["In Progress", "Open", "Resolved"],
        "Linked_Risk": ["RSK-005", "None", "RSK-001"],
    })

if "data_rtm" not in st.session_state:
    st.session_state["data_rtm"] = pd.DataFrame({
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

if "data_schedule" not in st.session_state:
    st.session_state["data_schedule"] = pd.DataFrame({
        "Task_ID": ["TSK-101", "TSK-102", "TSK-103", "TSK-104"],
        "Task_Name": ["API Architecture Finalization", "Database Sharding & Migration", "Third-Party Payment Integration", "Security Penetration Testing"],
        "Owner": ["Lead Architect", "DBA Team", "External Vendor", "Security Consultant"],
        "Duration_Days": [10, 25, 14, 7],
        "Dependencies": ["None", "TSK-101", "TSK-101", "TSK-102, TSK-103"],
        "Is_Critical_Path": [True, True, False, True],
    })

# --- NAVIGATION PAGES SETUP ---
dashboard_page = st.Page(
    page="pages/1_Dashboard.py", 
    title="Intelligent Risk Management", 
    icon="🛡️", 
    default=True
)

rtm_page = st.Page(
    page="pages/2_Requirements_Traceability_Matrix.py", 
    title="Requirements Traceability Matrix", 
    icon="🔗"
)

schedule_page = st.Page(
    page="pages/3_Schedule_Risk_Analyzer.py",
    title="Schedule Risk Analyzer",
    icon="📅"
)

pg = st.navigation([dashboard_page, rtm_page, schedule_page])
pg.run()

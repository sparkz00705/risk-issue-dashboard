import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Intelligent Risk Management",
    layout="wide",
    page_icon="🛡️",
)

# --- 1. INITIALIZE SYNCHRONIZED SESSION STATE DATA ---

# --- Risk Register Data ---
if "data_risks" not in st.session_state:
    st.session_state["data_risks"] = pd.DataFrame({
        "ID": ["RSK-001", "RSK-002", "RSK-003", "RSK-004", "RSK-005"],
        "Title": [
            "API Gateway Latency Bottleneck",
            "Database Migration Downtime Risk",
            "Third-Party Vendor API Delay",
            "Authentication Vulnerability Exposure",
            "Multi-Region Infrastructure Failover Sync Lag",
        ],
        "Category": ["Technical", "Technical", "Supply Chain", "Security", "Infrastructure"],
        "Probability": ["High", "Medium", "Low", "High", "Medium"],
        "Impact": ["Critical", "High", "Medium", "High", "Critical"],
        "Score": [15, 9, 4, 12, 10],
        "Status": ["Open", "Open", "Mitigated", "Open", "Open"],
        "Financial_Impact_USD": [50000, 45000, 15000, 40000, 60000],
        "Schedule_Delay_Days": [14, 25, 7, 10, 18],
    })

# --- Requirements Traceability Matrix (RTM) Data ---
if "data_rtm" not in st.session_state:
    st.session_state["data_rtm"] = pd.DataFrame({
        "Req_ID": ["REQ-001", "REQ-002", "REQ-003", "REQ-004", "REQ-005"],
        "Requirement_Title": [
            "Sub-second API Response Times",
            "Zero-Data-Loss Database Sharding",
            "Secure Payment Gateway Integration",
            "OAuth2 Authentication Enforcement",
            "Automated Multi-Region Failover",
        ],
        "Category": ["Performance", "Infrastructure", "Security", "Security", "Infrastructure"],
        "Linked_Risk": ["RSK-001", "RSK-002", "RSK-003", "RSK-004", "RSK-005"],
        "Test_Status": ["Failed", "Pending", "Passed", "Pending", "Passed"],
        "Verification_Method": ["Load Test", "Data Audit", "API Test", "Pen Test", "Chaos Test"],
    })

# Issues Log Data
if "data_issues" not in st.session_state:
    st.session_state["data_issues"] = pd.DataFrame({
        "ID": ["ISS-001", "ISS-002", "ISS-003"],
        "Title": [
            "API Timeout under High Load",
            "DB Migration Script Throws Error",
            "Staging Environment Down",
        ],
        "Category": ["Technical", "Technical", "Infrastructure"],
        "Severity": ["Critical", "High", "High"],
        "Status": ["In Progress", "Open", "Resolved"],
        "Linked_Risk": ["RSK-001", "RSK-002", "RSK-005"],
    })

# Requirements Traceability Matrix (RTM) Data
if "data_rtm" not in st.session_state:
    st.session_state["data_rtm"] = pd.DataFrame({
        "Req_ID": ["REQ-001", "REQ-002", "REQ-003", "REQ-004", "REQ-005"],
        "Requirement_Title": [
            "Sub-second API Response Times",
            "Zero-Data-Loss Database Sharding",
            "Secure Payment Gateway Integration",
            "OAuth2 Authentication Enforcement",
            "Automated Multi-Region Failover",
        ],
        "Category": ["Performance", "Infrastructure", "Security", "Security", "Infrastructure"],
        "Linked_Risk": ["RSK-001", "RSK-002", "RSK-003", "RSK-004", "RSK-005"],
        "Test_Status": ["Failed", "Pending", "Passed", "Pending", "Passed"],
        "Verification_Method": ["Load Test", "Data Audit", "API Test", "Pen Test", "Chaos Test"],
    })

# Project Schedule Data
if "data_schedule" not in st.session_state:
    st.session_state["data_schedule"] = pd.DataFrame({
        "Task_ID": ["TSK-101", "TSK-102", "TSK-103", "TSK-104", "TSK-105", "TSK-106"],
        "Task_Name": [
            "API Architecture Finalization", 
            "Database Sharding & Migration", 
            "Third-Party Payment Integration", 
            "Security Penetration Testing",
            "OAuth2 Identity Provider Setup",
            "Multi-Region Infrastructure Failover"
        ],
        "Owner": ["Lead Architect", "DBA Team", "External Vendor", "Security Consultant", "Security Lead", "DevOps Lead"],
        "Duration_Days": [10, 25, 14, 7, 12, 18],
        "Dependencies": ["None", "TSK-101", "TSK-101", "TSK-102, TSK-103", "None", "TSK-102"],
        "Is_Critical_Path": [True, True, False, True, False, True],
    })

# --- 2. NAVIGATION PAGES SETUP ---
dashboard_page = st.Page(
    page="pages/1_Dashboard.py", 
    title="Intelligent Risk Management", 
    icon="🛡️", 
    default=True
)

rtm_page = st.Page(
    page="pages/rtm_page.py", 
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

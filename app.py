import pandas as pd
import plotly.express as px
from google import genai
import streamlit as st

# --- PAGE CONFIGURATION & LUXURY STYLING ---
st.set_page_config(
    page_title="AI-Powered Risk vs. Issue Dashboard",
    layout="wide",
    page_icon="🛡️",
)

st.markdown(
    """
    <style>
    div.block-container {
        padding-top: 2rem;
        background-color: #0f172a;
    }
    div[data-testid="metric-container"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 8px 8px 0px 0px;
        color: #f8fafc;
        padding: 10px 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🛡️ Intelligent Risk Management powered by real-time data")
st.markdown(
    "From potential risk to absolute resolution: Real-time project intelligence"
   # "A professional portfolio project tracking future uncertainties"
   # " (Risks) versus active operational roadblocks (Issues) with real-time AI"
   # " text parsing."
)

# --- DATA UPLOAD, TEMPLATE DOWNLOADS & SPECIFICATIONS ---
st.subheader("📁 Data Source Management")

VALID_PROBABILITIES = ["Low", "Medium", "High"]
VALID_IMPACTS = ["Low", "Medium", "High", "Critical"]
prob_weight = {"Low": 1, "Medium": 2, "High": 3}
impact_weight = {"Low": 1, "Medium": 2, "High": 3, "Critical": 5}

col_dl1, col_dl2 = st.columns(2)

with col_dl1:
  risk_template = pd.DataFrame({
      "ID": ["RSK-001", "RSK-002"],
      "Title": ["API Gateway Latency", "Key Developer Turnover"],
      "Category": ["Technical", "Resource"],
      "Probability": ["High", "Medium"],
      "Impact": ["Critical", "High"],
      "Status": ["Open", "Open"],
  })
  risk_template["Score"] = risk_template.apply(
      lambda row: prob_weight.get(row["Probability"], 1)
      * impact_weight.get(row["Impact"], 1),
      axis=1,
  )
  risk_csv = risk_template.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 Download Risk Template",
      data=risk_csv,
      file_name="risk_template.csv",
      mime="text/csv",
  )

with col_dl2:
  issue_template = pd.DataFrame({
      "ID": ["ISS-001", "ISS-002"],
      "Title": ["Auth Service Outage", "Client Rejected Prototype"],
      "Category": ["Technical", "Product"],
      "Severity": ["Critical", "High"],
      "Status": ["In Progress", "Open"],
      "Linked_Risk": ["RSK-001", "None"],
  })
  issue_csv = issue_template.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 Download Issue Template",
      data=issue_csv,
      file_name="issue_template.csv",
      mime="text/csv",
  )

upload_tab1, upload_tab2 = st.tabs(
    ["Upload Risk Register", "Upload Issue Log"]
)

with upload_tab1:
  uploaded_risk_file = st.file_uploader(
      "Upload filled-in Risk CSV/Excel:", type=["csv", "xlsx"], key="risk_up"
  )
  if uploaded_risk_file is not None:
    try:
      data_risks = (
          pd.read_csv(uploaded_risk_file)
          if uploaded_risk_file.name.endswith(".csv")
          else pd.read_excel(uploaded_risk_file)
      )
      data_risks["Probability"] = (
          data_risks["Probability"].astype(str).str.strip()
      )
      data_risks["Impact"] = data_risks["Impact"].astype(str).str.strip()
      data_risks["Score"] = data_risks.apply(
          lambda row: prob_weight.get(row["Probability"], 1)
          * impact_weight.get(row["Impact"], 1),
          axis=1,
      )
      st.success("Custom Risk dataset loaded and auto-scored successfully!")
    except Exception:
      data_risks = pd.DataFrame({
          "ID": ["RSK-001", "RSK-002", "RSK-003", "RSK-004", "RSK-005"],
          "Title": [
              "API Gateway Latency",
              "Key Developer Turnover",
              "Third-party Vendor Delay",
              "Compliance Scope Creep",
              "Database Scalability Limit",
          ],
          "Category": [
              "Technical",
              "Resource",
              "Supply Chain",
              "Legal",
              "Technical",
          ],
          "Probability": ["High", "Medium", "Low", "High", "Medium"],
          "Impact": ["Critical", "High", "Medium", "High", "Critical"],
          "Score": [15, 9, 4, 12, 10],
          "Status": ["Open", "Open", "Mitigated", "Open", "Materialized"],
      })
  else:
    data_risks = pd.DataFrame({
        "ID": ["RSK-001", "RSK-002", "RSK-003", "RSK-004", "RSK-005"],
        "Title": [
            "API Gateway Latency",
            "Key Developer Turnover",
            "Third-party Vendor Delay",
            "Compliance Scope Creep",
            "Database Scalability Limit",
        ],
        "Category": [
            "Technical",
            "Resource",
            "Supply Chain",
            "Legal",
            "Technical",
        ],
        "Probability": ["High", "Medium", "Low", "High", "Medium"],
        "Impact": ["Critical", "High", "Medium", "High", "Critical"],
        "Score": [15, 9, 4, 12, 10],
        "Status": ["Open", "Open", "Mitigated", "Open", "Materialized"],
    })

with upload_tab2:
  uploaded_issue_file = st.file_uploader(
      "Upload filled-in Issue CSV/Excel:", type=["csv", "xlsx"], key="issue_up"
  )
  if uploaded_issue_file is not None:
    try:
      data_issues = (
          pd.read_csv(uploaded_issue_file)
          if uploaded_issue_file.name.endswith(".csv")
          else pd.read_excel(uploaded_issue_file)
      )
      st.success("Custom Issue dataset loaded successfully!")
    except Exception:
      data_issues = pd.DataFrame({
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
  else:
    data_issues = pd.DataFrame({
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

# --- TOP KPI METRICS ROW ---
col1, col2, col3, col4 = st.columns(4)
col1.metric(
    label="Open Risks",
    value=len(data_risks[data_risks["Status"] == "Open"]),
    delta="-2 this week",
)
col2.metric(
    label="Active Issues",
    value=len(data_issues[data_issues["Status"] != "Resolved"]),
    delta="+1 today",
)
col3.metric(
    label="Materialized Risks",
    value=len(data_risks[data_risks["Status"] == "Materialized"]),
)
col4.metric(label="Risk-to-Issue Conversion Rate", value="20%")

st.markdown("---")

# --- REAL-TIME GENAI PARSER SECTION ---
st.subheader("🤖 Project Status Update")
st.markdown("Click the button below to have the real-time AI evaluate your current Risk Register and Issue Log, generate the RAG status, and provide executive recommendations.")

if st.button("Generate AI Project RAG Report & Risk/Issue Analysis", type="primary"):
    with st.spinner("Querying real-time AI model..."):
        try:
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            
            risk_summary = data_risks.to_string(index=False)
            issue_summary = data_issues.to_string(index=False)
            
            prompt = f"""
            You are a senior project portfolio director. Analyze the project registers below.
            
            CURRENT ACTIVE RISK REGISTER:
            {risk_summary}
            
            CURRENT ACTIVE ISSUE LOG:
            {issue_summary}
            
            Task:
            1. Determine and state the Project RAG Status (RED, AMBER, or GREEN) with clear executive justification.
            2. Identify any materialized risks and active issues.
            3. Provide concrete, step-by-step recommendations on how to remediate blocks and turn the project status to Green.
            
            Format your response with these exact markdown headers:
            ## Project RAG Status: [RED/AMBER/GREEN]
            ### Executive Summary Justification
            ### Discovered Risk / Materialized Risks
            ### Active Issues
            ### Action Plan to Turn Status Green
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            st.success("Real-time AI analysis complete!")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"API Error: {e}")
            
st.markdown("---")

# --- SECTION 2: VISUALIZATIONS & SCORE EXPLANATION ---
c1, c2 = st.columns(2)

with c1:
  st.subheader("⚠️ Risk Matrix Heatmap")
  st.caption(
      "Note: Bubble size represents the Risk Score (Score = Probability ×"
      " Impact)."
  )
  fig_risk = px.scatter(
      data_risks,
      x="Probability",
      y="Impact",
      color="Category",
      hover_data=["Title", "ID"],
      size="Score",
      title="Active Risk Distribution",
      template="plotly_dark",
  )
  st.plotly_chart(fig_risk, use_container_width=True)

with c2:
  st.subheader("🔥 Issues by Category & Severity")
  st.caption(
      "Tracking active operational blocks currently hindering execution."
  )
  fig_issue = px.bar(
      data_issues,
      x="Category",
      color="Severity",
      title="Current Active Roadblocks",
      barmode="group",
      template="plotly_dark",
  )
  st.plotly_chart(fig_issue, use_container_width=True)

st.markdown("---")

# --- SECTION 3: INTERACTIVE REGISTERS & DEFINITIONS ---
st.subheader("📋 Core Records & Status Definitions")
tab1, tab2, tab3 = st.tabs(["Active Risk Register", "Active Issue Log", "Status & Definitions Reference"])

with tab1:
    st.markdown("### Risk Register")
    st.markdown("Risks are **future uncertain events** that *might* happen. The **Score** is quantified using the matrix formula: **Score = Probability × Impact**.")
    st.dataframe(data_risks, use_container_width=True)

with tab2:
    st.markdown("### Issue Log")
    st.markdown("Issues are **current realized problems** that require immediate operational remediation. Many issues originate directly from materialized risks.")
    st.dataframe(data_issues, use_container_width=True)

with tab3:
    st.markdown("### Project RAG Status & Key Definitions Guide")
    st.markdown("""
    * **Project RAG Status:** 
      * **RED:** Critical blockers or materialized risks are impacting core delivery, requiring immediate executive intervention.
      * **AMBER:** Moderate risks or minor bottlenecks are present, needing close oversight.
      * **GREEN:** Project is tracking smoothly against baseline targets.
      
    * **Risk Status Definitions:**
      * **Open:** The future uncertainty is active and monitored, but has not occurred yet.
      * **Mitigated:** Preventive actions have been successfully applied to reduce its probability or impact.
      * **Materialized:** The risk has officially occurred and turned into a real, active problem.

    * **Issue Status Definitions:**
      * **Open:** The problem has been logged, but active remediation has not started.
      * **In Progress:** The team is actively working on an emergency fix or remediation plan.
      * **Resolved:** The problem has been successfully fixed, tested, and closed out.
    """)

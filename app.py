import pandas as pd
import plotly.express as px
import streamlit as st

# --- PAGE CONFIGURATION & LUXURY STYLING ---
st.set_page_config(
    page_title="AI Risk vs. Issue Intelligence Dashboard",
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

st.title("🛡️ AI-Powered Risk vs. Issue Dashboard")
st.markdown(
    "A professional-grade portfolio project tracking future uncertainties"
    " (Risks) versus active operational roadblocks (Issues) with generative AI"
    " text parsing."
)

# --- DATA UPLOAD, TEMPLATE DOWNLOAD & SPECIFICATIONS ---
st.subheader("📁 Data Source Management")

# Define strict allowed dropdown options & score weight mappings
VALID_PROBABILITIES = ["Low", "Medium", "High"]
VALID_IMPACTS = ["Low", "Medium", "High", "Critical"]

prob_weight = {"Low": 1, "Medium": 2, "High": 3}
impact_weight = {"Low": 1, "Medium": 2, "High": 3, "Critical": 5}

# Pre-templated dataset structure for users to download
template_data = pd.DataFrame({
    "ID": ["RSK-001", "RSK-002"],
    "Title": ["API Gateway Latency", "Key Developer Turnover"],
    "Category": ["Technical", "Resource"],
    "Probability": ["High", "Medium"],
    "Impact": ["Critical", "High"],
    "Status": ["Open", "Open"],
})

# Auto-compute initial template score
template_data["Score"] = template_data.apply(
    lambda row: prob_weight.get(row["Probability"], 1)
    * impact_weight.get(row["Impact"], 1),
    axis=1,
)

csv_template = template_data.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Standard Risk Template",
    data=csv_template,
    file_name="risk_template.csv",
    mime="text/csv",
    help=(
        "Download template. Please use dropdown values (Low, Medium, High for"
        " Probability; Low, Medium, High, Critical for Impact)."
    ),
)

st.info(
    "💡 **Note for Users:** When filling out your spreadsheet, please select"
    " Probability from **(Low, Medium, High)** and Impact from **(Low, Medium,"
    " High, Critical)**. Scores are automatically calculated by the app upon"
    " upload."
)

uploaded_file = st.file_uploader(
    "Upload your filled-in Risk/Issue CSV or Excel file:",
    type=["csv", "xlsx"],
)

if uploaded_file is not None:
  try:
    if uploaded_file.name.endswith(".csv"):
      data_risks = pd.read_csv(uploaded_file)
    else:
      data_risks = pd.read_excel(uploaded_file)

    # Validate that columns exist
    required_cols = [
        "ID",
        "Title",
        "Category",
        "Probability",
        "Impact",
        "Status",
    ]
    if all(col in data_risks.columns for col in required_cols):
      # Auto-calculate and enforce score computation based on selected valid categories
      data_risks["Probability"] = data_risks["Probability"].astype(str).str.strip()
      data_risks["Impact"] = data_risks["Impact"].astype(str).str.strip()

      data_risks["Score"] = data_risks.apply(
          lambda row: prob_weight.get(row["Probability"], 1)
          * impact_weight.get(row["Impact"], 1),
          axis=1,
      )
      st.success(
          "Custom dataset successfully loaded, validated, and auto-scored!"
      )
    else:
      st.error(
          "Uploaded file is missing required columns. Falling back to default"
          " mock data."
      )
      raise ValueError("Missing columns")

  except Exception as e:
    # Fallback default risk data
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
  # --- DEFAULT MOCK DATA & SCORE CALCULATION EXPLANATION ---
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

# Default Issue Log Data
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

# --- AI ASSISTANT SECTION ---
st.subheader("🤖 GenAI Status Update Parser")
st.markdown(
    "Paste raw weekly meeting notes, Slack logs, or status updates to let the"
    " simulated LLM classify and extract items."
)

project_update = st.text_area(
    "Project Notes / Status Update:",
    placeholder=(
        "Example: Team noted potential bottlenecks in staging environment"
        " setup. Also, client approval for UI wireframes is currently"
        " delayed by 3 days."
    ),
)

if st.button("Extract Risks & Issues with AI", type="primary"):
  if project_update:
    with st.spinner("Analyzing text using semantic AI extraction..."):
      st.success("Analysis complete! Extracted insights below:")
      ai_col1, ai_col2 = st.columns(2)
      with ai_col1:
        st.markdown("**🚨 Discovered Risk:**")
        st.info(
            "Staging environment configuration drift could cause deployment"
            " delays."
        )
      with ai_col2:
        st.markdown("**🔥 Discovered Issue:**")
        st.warning("Client approval delay on UI wireframes impacting Sprint 4.")
  else:
    st.warning("Please paste some project notes text first.")

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

# --- SECTION 3: INTERACTIVE REGISTERS ---
st.subheader("📋 Core Records & Logs")
tab1, tab2 = st.tabs(["Active Risk Register", "Active Issue Log"])

with tab1:
  st.markdown("### Risk Register Explanation")
  st.markdown(
      "Risks are future uncertain events that *might* happen. The **Score** is"
      " quantified using the matrix formula: **Score = Probability × Impact**."
  )
  st.dataframe(data_risks, use_container_width=True)

with tab2:
  st.markdown("### Issue Log Explanation")
  st.markdown(
      "Issues are current realized problems that require immediate operational"
      " remediation. Many issues originate directly from materialized risks."
  )
  st.dataframe(data_issues, use_container_width=True)

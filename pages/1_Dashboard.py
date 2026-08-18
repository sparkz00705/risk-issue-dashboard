import re
import pandas as pd
import plotly.express as px
from groq import Groq
import streamlit as st

st.subheader("🛡️ Intelligent Risk Management powered by real time data")
st.markdown("From potential risk to absolute resolution: Real-time project intelligence")

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

# --- REAL-TIME GROQ AI PARSER SECTION ---
st.subheader("🤖 Project Status Update")
st.markdown("Click the button below to have the real-time AI evaluate your current Risk Register and Issue Log, generate the RAG status report as a standalone HTML file.")

col_gen1, col_gen2 = st.columns([2, 2])

with col_gen1:
    generate_clicked = st.button("Generate AI Project RAG Report & Risk/Issue Analysis", type="primary")

if "ai_report_text" not in st.session_state:
    st.session_state["ai_report_text"] = None


def clean_ai_response(raw_text: str) -> str:
    if not raw_text:
        return raw_text
    cleaned = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL | re.IGNORECASE)
    if "<think>" in cleaned.lower() and "</think>" not in cleaned.lower():
        cleaned = re.split(r"<think>", cleaned, flags=re.IGNORECASE)[0]
    return cleaned.strip()


def markdown_to_report_html(md_text: str) -> str:
    lines = md_text.split("\n")
    html_parts = []
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            html_parts.append("</ul>")
            in_list = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            close_list()
            continue

        line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)

        if line.startswith("## "):
            close_list()
            html_parts.append(f"<h2>{line[3:].strip()}</h2>")
        elif line.startswith("### "):
            close_list()
            html_parts.append(f"<h3>{line[4:].strip()}</h3>")
        elif line.startswith("- ") or line.startswith("* "):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{line[2:].strip()}</li>")
        else:
            close_list()
            html_parts.append(f"<p>{line}</p>")

    close_list()
    return "".join(html_parts)


def highlight_rag_status(html: str) -> str:
    colors = {"RED": "#dc2626", "AMBER": "#d97706", "GREEN": "#16a34a"}
    for word, color in colors.items():
        html = re.sub(
            rf"\b{word}\b",
            f'<span style="color: {color}; font-weight: bold; font-size: 1.2em;">{word}</span>',
            html,
        )
    return html


if generate_clicked:
    with st.spinner("Querying real-time Groq AI model..."):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])

            risk_summary = data_risks.to_string(index=False)
            issue_summary = data_issues.to_string(index=False)

            prompt = f"""
            You are a senior project portfolio director. Analyze the project registers below and fill out the standardized Project Status Report template.

            CURRENT ACTIVE RISK REGISTER:
            {risk_summary}

            CURRENT ACTIVE ISSUE LOG:
            {issue_summary}

            Task:
            Generate a complete executive project status report following this exact template structure using Markdown. Respond with ONLY the report itself — do not include any reasoning, thinking, or preamble before or after it.

            ## 📊 Executive Project Status Report
            - **Overall Project RAG Status:** [RED / AMBER / GREEN]
            - **Reporting Period:** Current Active Sprint / Real-Time Analysis

            ### 1. Executive Summary & RAG Justification
            [Provide a concise overview explaining why this RAG status was assigned based on current open risks and issues]

            ### 2. Key Highlights & Progress
            [Summarize current operational wins or milestones achieved]

            ### 3. Materialized Risks & Active Roadblocks (Issues)
            [Highlight critical active items, blockers, and materialized risks impacting delivery]

            ### 4. Corrective Action Plan (Turning Status to Green)
            [Provide concrete, prioritized, step-by-step remediation steps]
            """

            response = client.chat.completions.create(
                model="qwen/qwen3.6-27b",
                messages=[
                    {"role": "system", "content": "You are an expert senior project portfolio director. Respond with only the final report — never include your reasoning or <think> content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4096,
                temperature=0.4,
            )
            raw_text = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            if finish_reason == "length":
                st.warning("The AI response was cut off by the token limit. Consider raising max_tokens further if this recurs.")
            st.session_state["ai_report_text"] = clean_ai_response(raw_text)
            st.success("Real-time AI analysis complete! Download your report below.")
        except Exception as e:
            st.error(f"API Error: {e}")

if st.session_state["ai_report_text"]:
    body_content = markdown_to_report_html(st.session_state["ai_report_text"])
    body_content = highlight_rag_status(body_content)

    report_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Executive Project Status Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 40px auto; padding: 20px; background: #fdfdfd; }}
        h2 {{ color: #1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 30px; }}
        h3 {{ color: #334155; margin-top: 24px; }}
        p {{ margin-bottom: 12px; }}
        ul {{ margin: 0 0 12px 0; padding-left: 20px; }}
        li {{ margin-bottom: 6px; }}
    </style>
</head>
<body>
    {body_content}
</body>
</html>"""

    with col_gen2:
        st.download_button(
            label="📥 Download Project Status Report (HTML)",
            data=report_html,
            file_name="executive_project_status_report.html",
            mime="text/html",
            type="secondary"
        )

st.markdown("---")

# --- SECTION 2: VISUALIZATIONS & SCORE EXPLANATION ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("⚠️ Risk Matrix Heatmap")
    st.caption("Note: Bubble size represents the Risk Score (Score = Probability × Impact).")
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
    st.caption("Tracking active operational blocks currently hindering execution.")
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

# --- AI-DRIVEN AUTOMATED RISK SCORING TOOL ---
st.subheader("🎯 AI-Driven Automated Risk Scoring Assistant")
st.markdown("Describe a potential project risk in plain text below, and let the AI analyze it to predict its Probability, Impact, and Risk Score.")

with st.form("risk_scoring_form"):
    new_risk_desc = st.text_area("Detailed Risk Description", placeholder="Describe what could happen, the triggers, and potential consequences...")
    submit_scoring = st.form_submit_button("Analyze & Score Risk with AI", type="secondary")

if submit_scoring and new_risk_desc:
    with st.spinner("AI is analyzing risk probability and impact..."):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            prompt = f"""
            Analyze the following project risk description and assign a structured risk evaluation:
            Description: {new_risk_desc}

            Respond with ONLY the structured evaluation below — no reasoning or <think> content.

            Provide your response strictly in this format:
            - **Probability:** [Low / Medium / High]
            - **Impact:** [Low / Medium / High / Critical]
            - **Calculated Score:** [Number, where Low=1, Medium=2, High=3, Critical=5. Score = Probability Weight × Impact Weight]
            - **Justification & Mitigation Advice:** [Short strategic reasoning and preventive advice]
            """
            response = client.chat.completions.create(
                model="qwen/qwen3.6-27b",
                messages=[
                    {"role": "system", "content": "You are an expert risk management consultant. Respond with only the final structured evaluation — never include your reasoning or <think> content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024,
                temperature=0.4,
            )
            st.success("Risk analysis complete!")
            st.markdown(clean_ai_response(response.choices[0].message.content))
        except Exception as e:
            st.error(f"API Error: {e}")

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

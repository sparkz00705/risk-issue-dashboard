import streamlit as st

st.subheader("📖 Intelligent Risk Management - User Guide")
st.markdown("Learn how to navigate, use, and document the intelligent risk management workflow step-by-step.")

guide_text = """
## 1. What Does This App Do?
This application helps project teams track potential project problems, map requirements, analyze schedules, and generate professional reports—all in one place. It creates a continuous loop between tasks, risks, and technical requirements.

## 2. Step-by-Step User Workflow:

### Step 1: Manage Data Sources (Home Dashboard)
* **Where to go:** The main home page.
* **What you do:** Download templates if needed, and upload your customized Risk Registers, Issue Logs, or project data files using the file upload section.
* **Why you do it:** This sets up the foundational data so the rest of the application can automatically build charts, heatmaps, and summaries.

### Step 2: Analyze Schedule Risks
* **Where to go:** Click on 'Schedule Risk Analyzer' in the sidebar.
* **What you do:** Upload your project schedule (`.csv` or `.xlsx`) containing tasks, timelines, and dependencies. Click the button to extract risks using AI.
* **Why you do it:** The AI instantly scans your task list, spots bottlenecks or dependencies, and creates a clear risk table complete with suggested solutions and delay estimates.

### Step 3: Track Requirements (RTM)
* **Where to go:** Click on 'Requirements Traceability Matrix' in the sidebar.
* **What you do:** Review how project requirements link directly to potential risks and test statuses.
* **Why you do it:** It ensures that every technical feature or requirement has a safety plan and testing method in place.

### Step 4: Generate Executive Reports
* **Where to go:** Back to the main home page.
* **What you do:** Click the button to 'Generate AI Project RAG Report'.
* **Why you do it:** It compiles all active risks, issues, and project statuses into a clean, standalone report that you can easily share with leadership.
"""

st.markdown(guide_text)

st.markdown("---")

plain_download_text = """INTELLIGENT RISK MANAGEMENT - USER GUIDE & WORKFLOW

1. WHAT DOES THIS APP DO?
This application helps project teams track potential project problems, map requirements, analyze schedules, and generate professional reports—all in one place.

2. STEP-BY-STEP USER WORKFLOW:

Step 1: Manage Data Sources (Home Dashboard)
Upload your customized Risk Registers, Issue Logs, or project data files to set up foundational data.

Step 2: Analyze Schedule Risks
Upload your project schedule (.csv or .xlsx) and use the AI extractor to map dependencies and mitigation steps.

Step 3: Track Requirements (RTM)
Review how project requirements link directly to potential risks and test statuses.

Step 4: Generate Executive Reports
Compile all active risks, issues, and project statuses into an executive-ready format.
"""

st.download_button(
    label="📥 Download User Guide (Text File)",
    data=plain_download_text,
    file_name="Intelligent_Risk_Management_User_Guide.txt",
    mime="text/plain",
    type="primary"
)

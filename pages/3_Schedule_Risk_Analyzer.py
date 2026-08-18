import streamlit as st
import pandas as pd
from groq import Groq
import re

st.subheader("📅 AI Project Schedule Risk Analyzer")
st.markdown("Upload your project schedule or task list to let AI identify critical path bottlenecks, timeline dependencies, and automatically generate project risks.")

# --- 1. SCHEDULE UPLOAD SECTION ---
uploaded_sched_file = st.file_uploader(
    "Upload Project Schedule (CSV/Excel with Tasks, Durations, Dependencies):", 
    type=["csv", "xlsx"], 
    key="sched_up"
)

if uploaded_sched_file is not None:
    try:
        data_schedule = (
            pd.read_csv(uploaded_sched_file)
            if uploaded_sched_file.name.endswith(".csv")
            else pd.read_excel(uploaded_sched_file)
        )
        st.session_state["data_schedule"] = data_schedule
        st.success("Project schedule loaded successfully!")
    except Exception as e:
        st.error(f"Error loading file: {e}")

data_schedule = st.session_state["data_schedule"]

st.dataframe(data_schedule, use_container_width=True)

st.markdown("---")

# --- 2. AI SCHEDULE RISK EXTRACTION ---
st.subheader("🤖 AI Automated Risk & Schedule Impact Derivation")
st.markdown("Click below to have Groq AI scan task durations, critical path constraints, and dependencies to output structured risks.")

if st.button("Extract Risks from Schedule with AI", type="primary"):
    with st.spinner("Analyzing schedule constraints and dependencies..."):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            schedule_text = data_schedule.to_string(index=False)
            
            prompt = f"""
            You are a senior project scheduler and risk manager. Analyze the following project schedule data:
            
            {schedule_text}
            
            Task:
            Identify potential timeline bottlenecks, dependency risks, and single-point-of-failure owners. Generate 3 to 5 distinct risks derived directly from this schedule.
            
            Provide your response strictly in a clean Markdown table format with these columns:
            | Risk_ID | Risk_Title | Category | Probability | Impact | Estimated_Delay_Days | AI_Mitigation_Recommendation |
            
            Respond with ONLY the markdown table. Do not include any thinking tags or preamble.
            """
            
            response = client.chat.completions.create(
                model="qwen/qwen3.6-27b",
                messages=[
                    {"role": "system", "content": "You are an expert risk manager. Respond with only the markdown table requested."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2048,
                temperature=0.3,
            )
            
            ai_output = response.choices[0].message.content
            # Clean think tags if any
            ai_output = re.sub(r"<think>.*?</think>", "", ai_output, flags=re.DOTALL | r.IGNORECASE).strip()
            
            st.session_state["extracted_schedule_risks"] = ai_output
            st.success("Schedule risks successfully extracted!")
            
        except Exception as e:
            st.error(f"AI API Error: {e}")

if "extracted_schedule_risks" in st.session_state:
    st.markdown("### Extracted Schedule Risks")
    st.markdown(st.session_state["extracted_schedule_risks"])
    
    if st.button("📥 Download Extracted Schedule Risks (Markdown)", type="secondary"):
        st.download_button(
            label="Download File",
            data=st.session_state["extracted_schedule_risks"],
            file_name="schedule_extracted_risks.md",
            mime="text/markdown"
        )

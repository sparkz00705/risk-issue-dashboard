import streamlit as st
import pandas as pd
from groq import Groq

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
            Analyze the following project schedule data and identify bottlenecks, dependency risks, and single-point-of-failure owners:
            
            {schedule_text}
            
            Generate 3 to 5 distinct risks in a clean Markdown table format with these exact columns:
            | Risk_ID | Risk_Title | Category | Probability | Impact | Estimated_Delay_Days | AI_Mitigation_Recommendation |
            
            Crucial Instructions:
            1. Every single row must contain a robust, non-empty, actionable sentence in the 'AI_Mitigation_Recommendation' column. Do not leave any cell blank.
            2. Return ONLY the markdown table. Do not include thinking text, explanations, or conversational filler.
            """
            
            response = client.chat.completions.create(
                model="qwen/qwen3.6-27b",
                messages=[
                    {"role": "system", "content": "You are a senior project risk manager. Output only the requested Markdown table and absolutely nothing else."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4096,
                temperature=0.2,
            )
            
            ai_output = response.choices[0].message.content
            
            # Clean out any accidental think tags or conversational text
            if "</think>" in ai_output:
                ai_output = ai_output.split("</think>")[-1].strip()
            
            # Isolate the markdown table if extra text exists
            if "|" in ai_output:
                lines = ai_output.split("\n")
                table_lines = [line for line in lines if "|" in line]
                ai_output = "\n".join(table_lines)
                
            st.session_state["extracted_schedule_risks"] = ai_output
            st.success("Schedule risks successfully extracted!")
            
        except Exception as e:
            st.error(f"AI API Error: {e}")

if "extracted_schedule_risks" in st.session_state:
    st.markdown("### Extracted Schedule Risks")
    
    # Wrap in a bordered container for full visibility and clean scrolling
    with st.container(border=True):
        st.markdown(st.session_state["extracted_schedule_risks"])
    
    if st.button("📥 Download Extracted Schedule Risks (Markdown)", type="secondary"):
        st.download_button(
            label="Download File",
            data=st.session_state["extracted_schedule_risks"],
            file_name="schedule_extracted_risks.md",
            mime="text/markdown"
        )

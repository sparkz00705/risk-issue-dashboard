import streamlit as st
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Intelligent Risk Management - User Guide", 0, 1, "C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

def create_pdf():
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    guide_text = """
    INTELLIGENT RISK MANAGEMENT - USER GUIDE & WORKFLOW
    
    1. WHAT DOES THIS APP DO?
    This application helps project teams track potential project problems, map requirements, analyze schedules, and generate professional reports—all in one place. It creates a continuous loop between tasks, risks, and technical requirements.
    
    2. STEP-BY-STEP USER WORKFLOW:
    
    Step 1: Manage Data Sources (Home Dashboard)
    - Where to go: The main home page.
    - What you do: Download templates if needed, and upload your customized Risk Registers, Issue Logs, or project data files using the file upload section.
    - Why you do it: This sets up the foundational data so the rest of the application can automatically build charts, heatmaps, and summaries.
    
    Step 2: Analyze Schedule Risks
    - Where to go: Click on 'Schedule Risk Analyzer' in the sidebar.
    - What you do: Upload your project schedule (.csv or .xlsx) containing tasks, timelines, and dependencies. Click the button to extract risks using AI.
    - Why you do it: The AI instantly scans your task list, spots bottlenecks or dependencies, and creates a clear risk table complete with suggested solutions and delay estimates.
    
    Step 3: Track Requirements (RTM)
    - Where to go: Click on 'Requirements Traceability Matrix' in the sidebar.
    - What you do: Review how project requirements link directly to potential risks and test statuses.
    - Why you do it: It ensures that every technical feature or requirement has a safety plan and testing method in place.
    
    Step 4: Generate Executive Reports
    - Where to go: Back to the main home page.
    - What you do: Click the button to 'Generate AI Project RAG Report'.
    - Why you do it: It compiles all active risks, issues, and project statuses into a clean, standalone report that you can easily share with leadership.
    """
    
    for line in guide_text.strip().split("\n"):
        pdf.multi_cell(0, 6, line)
        
    return pdf.output()

# Streamlit Download Button Integration
if st.button("📥 Download Full User Guide as PDF"):
    pdf_data = create_pdf()
    st.download_button(
        label="Click here to download PDF file",
        data=pdf_data,
        file_name="Intelligent_Risk_Management_User_Guide.pdf",
        mime="application/pdf"
    )

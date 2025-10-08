import streamlit as st
import google.generativeai as genai
import re

# -----------------------------
# Configure Gemini API Key
# -----------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# -----------------------------
# Streamlit UI Setup
# -----------------------------
st.set_page_config(
    page_title="Appliance Diagnostic Assistant",
    layout="wide",
)

st.title(" Appliance Diagnostic Assistant")
st.markdown(
    "Get quick **self-diagnosis steps**, **probable causes**, **service timelines**, and **customer support info** for your home appliances."
)

# -----------------------------
# Input form layout
# -----------------------------
with st.form("diagnostic_form"):
    # Row 1: Model Name
    model_name = st.text_input(" Model Number", placeholder="e.g. Mi L32M6-RA, LG T70SPSF2Z, Samsung WA62M4100HY")

    # Row 2: Issue (left) and Error Code (right)
    col1, col2 = st.columns(2)
    with col1:
        issue = st.text_area(" Describe the Issue", placeholder="e.g. No display, Not cooling, making noise...")
    with col2:
        display_error = st.text_input(" Error Code / Message (Optional)", placeholder="e.g. E4, F07, etc.")

    submitted = st.form_submit_button(" Diagnose Appliance", use_container_width=True)

# -----------------------------
# Response Generation
# -----------------------------
if submitted:
    if not model_name or not issue:
        st.warning(" Please fill in the required fields before diagnosing.")
    else:
        with st.spinner("Analyzing the issue... Please wait "):
            prompt = f"""
You are an intelligent appliance service diagnostic assistant.

Model Number: {model_name}
Issue: {issue}
Error Code: {display_error or 'Not provided'}

Tasks:
1. Identify the **appliance brand** (e.g., LG, Samsung, Mi, Whirlpool, etc.) and **type** (e.g., TV, Washing Machine, Refrigerator, AC) from the model number.
2. Then generate a short, clean, and aesthetic diagnostic report with **four clearly separated sections** as follows:

   🔹 Quick Checks / Self-Diagnosis  
   • Give 2–3 simple user-level checks to perform before calling a technician.

   🔹 Customer Care Number  
   • Give the official customer care helpline number for the brand.

   🔹 Probable Causes & Estimated Costs  
   • Mention 2–3 possible technical causes (just name them, no explanations).  
   • Add approximate cost range in INR for each cause.

   🔹 Turnaround Time (TAT)  
   • Mention the realistic average service time in days.

Formatting Instructions:
- Use no markdown, *, or # symbols.
- Each section heading should start with a blue diamond (🔹).
- Each point inside should start with a small black dot (•).
- Keep response short, clean, and visually structured.
"""

            try:
                # Gemini model
                model = genai.GenerativeModel("gemini-2.5-flash-lite")
                response = model.generate_content(prompt)
                text = response.text

                st.success(" Diagnosis Report Generated Successfully!")
                st.markdown("---")

                # -----------------------------
                # Extract and clean brand info
                # -----------------------------
                match_brand = re.search(r'(Brand|Appliance Type).*?:\s*(.*)', text, re.IGNORECASE)
                if match_brand:
                    st.markdown(
                        f"""
                        <div style='
                            background-color:#003366;
                            color:#FFFFFF;
                            padding:1rem;
                            border-radius:10px;
                            font-family:Arial;
                            margin-bottom:1rem;
                        '>
                        <h3> Brand & Appliance</h3>
                        <b>{match_brand.group(2).strip()}</b>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # -----------------------------
                # Split sections
                # -----------------------------
                sections = re.split(r'(?=🔹)', text)
                colors = ["#1E90FF", "#4682B4", "#2E8B57", "#8B008B"]

                for i, sec in enumerate(sections):
                    sec = sec.strip()
                    if sec:
                        sec_html = re.sub(r'^\s*[-*]\s+', '• ', sec, flags=re.MULTILINE)
                        sec_html = sec_html.replace('\n', '<br>')
                        st.markdown(
                            f"""
                            <div style="
                                background-color:{colors[i % len(colors)]};
                                color:#FFFFFF;
                                padding:1rem;
                                border-radius:12px;
                                margin-bottom:1rem;
                                font-family:Arial, sans-serif;
                                line-height:1.6;
                            ">
                            {sec_html}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            except Exception as e:
                st.error(f"❌ Error: {e}")


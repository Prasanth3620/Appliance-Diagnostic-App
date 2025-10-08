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

st.title("🔧 Appliance Diagnostic Assistant")
st.markdown(
    "Get **probable causes**, **service info**, and **spare part details** for your home appliances."
)

# -----------------------------
# Input form with new layout
# -----------------------------
with st.form("diagnostic_form"):
    # -----------------------------
    # Row 1: Model Name (full width)
    # -----------------------------
    model_name = st.text_input("🔤 Model Name", placeholder="e.g. LG T70SPSF2Z")

    # -----------------------------
    # Row 2: Issue (left) and Error Code (right)
    # -----------------------------
    col1, col2 = st.columns(2)
    with col1:
        issue = st.text_area("⚙️ Describe the Issue", placeholder="e.g. No display, Not cooling, making noise...")
    with col2:
        display_error = st.text_input("💡 Error Code / Message (Optional)", placeholder="e.g. E4, F07, etc.")

    st.markdown("")  # spacing
    submitted = st.form_submit_button("🔍 Diagnose Appliance", use_container_width=True)

# -----------------------------
# Processing and Response
# -----------------------------
if submitted:
    if not model_name or not issue:
        st.warning("⚠️ Please fill in all the required fields before diagnosing.")
    else:
        with st.spinner("Analyzing the issue... Please wait ⏳"):
            prompt = f"""
You are an appliance service diagnostic assistant.

Model: {model_name}
Issue: {issue}
Display Error (if any): {display_error or 'No specific error provided'}

Generate a detailed, crisp, and short report including the following 4 main points:

1. Probable Causes & Estimated Costs
2. Appliance Brand Customer Care
3. Turnaround Time (TAT)
4. Spare Parts Information

Format the output with:
- No *, #, or markdown symbols.
- Each main heading should have a blue diamond (🔹).
- Each sub-point inside a section should start with a small black dot (•).
Keep it short, clear, and visually aesthetic.
"""

            try:
                # Generate content
                model = genai.GenerativeModel("gemini-2.5-flash-lite")
                response = model.generate_content(prompt)
                text = response.text

                st.success("✅ Diagnosis Report Generated Successfully!")
                st.markdown("---")

                # -----------------------------
                # Split response into sections
                # -----------------------------
                sections = re.split(r'(?=\d\.)', text)
                colors = ["#2E8B57", "#4682B4", "#DAA520", "#8B008B"]
                headings = [
                    "Probable Causes & Estimated Costs",
                    "Appliance Brand Customer Care",
                    "Turnaround Time (TAT)",
                    "Spare Parts Information"
                ]

                for i, sec in enumerate(sections):
                    sec = sec.strip()
                    if sec:
                        # Remove stray markdown symbols
                        sec = re.sub(r'^[#*\s\d.]+', '', sec)
                        sec = re.sub(r'[*#]+$', '', sec)

                        # Replace internal bullets or '-' with black dot
                        sec_html = re.sub(r'^\s*[-*]\s+', '• ', sec, flags=re.MULTILINE)
                        sec_html = sec_html.replace('\n', '<br>')

                        # Add heading with blue diamond
                        heading = f"🔹 {headings[i % len(headings)]}"
                        st.markdown(
                            f"""
                            <div style="
                                background-color:{colors[i % len(colors)]};
                                color:#FFFFFF;
                                padding:1rem;
                                border-radius:10px;
                                margin-bottom:1rem;
                                font-family:Arial, sans-serif;
                                line-height:1.5;
                            ">
                            <strong>{heading}</strong><br><br>
                            {sec_html}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            except Exception as e:
                st.error(f"❌ Error: {e}")

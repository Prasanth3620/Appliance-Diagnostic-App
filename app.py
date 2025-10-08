import streamlit as st
import google.generativeai as genai

# -----------------------------------
# 🔑 Configure Gemini API Key securely
# -----------------------------------
# Add your key in Streamlit Cloud → Settings → Secrets:
# GEMINI_API_KEY = "your_api_key_here"
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# -----------------------------------
# 🌤️ Streamlit UI Setup
# -----------------------------------
st.set_page_config(page_title="Appliance Diagnostic Assistant", layout="wide")

st.title("🔧 Appliance Diagnostic Assistant")
st.markdown("Get **probable causes**, **service info**, and **spare part details** for your home appliances.")

# -----------------------------------
# 1. Side-by-side input layout
# -----------------------------------
with st.form("diagnostic_form"):
    col1, col2 = st.columns(2)
    with col1:
        appliance = st.text_input("🧺 Appliance Type", placeholder="e.g. TV, Refrigerator (mention brand)")
        issue = st.text_area("⚙️ Describe the Issue", placeholder="e.g. No display, Not cooling, making noise...")
    with col2:
        model_name = st.text_input("🔤 Model Name", placeholder="e.g. LG T70SPSF2Z")
        display_error = st.text_input("💡 Error Code / Message (Optional)", placeholder="e.g. E4, F07, etc.")

    st.markdown("")  # spacing
    submitted = st.form_submit_button("🔍 Diagnose Appliance", use_container_width=True)

# -----------------------------------
# 2. Processing and Response
# -----------------------------------
if submitted:
    if not appliance or not model_name or not issue:
        st.warning("⚠️ Please fill in all the required fields before diagnosing.")
    else:
        with st.spinner("Analyzing the issue... Please wait ⏳"):
            prompt = f"""
You are an appliance service diagnostic assistant.

Appliance: {appliance}
Model: {model_name}
Issue: {issue}
Display Error (if any): {display_error or 'No specific error provided'}

Generate a detailed, crisp, and short report including the following:

1. Probable Causes — 2–3 possible technical reasons for the issue with estimated cost ranges in INR.
2. Appliance Brand Customer Care — official customer care number.
3. Turnaround Time (TAT) — realistic average service time in days.
4. Spare Parts Information — for all issues in point 1, include:
   - Brand/original part cost & lifespan
   - Local/non-branded part avg cost & lifespan

Format the output with bullet points and short actionable sentences.
"""

            try:
                # Use Gemini model
                model = genai.GenerativeModel("gemini-2.5-flash-lite")
                response = model.generate_content(prompt)

                st.success("✅ Diagnosis Report Generated Successfully!")
                st.markdown("---")

                # Scrollable styled output
                st.markdown(
                    f"""
                    <div style="
                        background-color:#f9f9f9;
                        padding:1rem;
                        border-radius:10px;
                        border:1px solid #ddd;
                        max-height:400px;
                        overflow-y:auto;
                        white-space:pre-wrap;
                        font-family:monospace;
                    ">
                    {response.text}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            except Exception as e:
                st.error(f"❌ Error: {e}")

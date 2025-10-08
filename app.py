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
# Input form
# -----------------------------
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

# -----------------------------
# Processing and Response
# -----------------------------
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

Generate a detailed, a crisp and not elongated report including and don't include any headings just give the solution for all the questions:

1 Probable Causes(Just give the name of the issue.No need for explaination or elobaration) — 2–3 possible technical reasons for the issue and their estimated cost ranges in INR.
2 Appliance Brand Customer Care — provide the official customer care number for the appliance's brand.
3 Turnaround Time (TAT) — realistic average service time in days.
4 Spare Parts Information — if replacement is needed for all the issue given in point 1, include:
    - Brand/original part cost & lifespan currently
    - Local/non-branded part avg cost & lifespan for only 1 brand.

Format the output with bullet points and section titles.
If any data is unavailable, infer the most likely information based on repair trends in India. And finally the response should be short and crisp.
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
                sections = re.split(r'(?=\d\.)', text)  # splits at "1.", "2.", etc.

                colors = ["#2E8B57", "#4682B4", "#DAA520", "#8B008B"]  # unique color per section

                for i, sec in enumerate(sections):
                    sec = sec.strip()
                    if sec:
                        # Convert bullets (- or *) to HTML list
                        sec_html = re.sub(r'^\s*[-*]\s+', '• ', sec, flags=re.MULTILINE)
                        sec_html = sec_html.replace('\n', '<br>')  # keep line breaks
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
                            {sec_html}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            except Exception as e:
                st.error(f"❌ Error: {e}")

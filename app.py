import streamlit as st
import google.generativeai as genai

# -----------------------------------
# 🔑 Configure Gemini API Key securely
# -----------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# -----------------------------------
# 🌤️ Streamlit UI Setup
# -----------------------------------
st.set_page_config(
    page_title="Appliance Diagnostic Assistant",
    layout="wide",
)

st.title("🔧 Appliance Diagnostic Assistant")
st.markdown(
    "Get **probable causes**, **service info**, and **spare part details** for your home appliances."
)

# -----------------------------------
# 1. Side-by-side input layout
# -----------------------------------
with st.form("diagnostic_form"):
    col1, col2 = st.columns(2)
    with col1:
        appliance = st.text_input(
            "🧺 Appliance Type",
            placeholder="e.g. TV, Refrigerator (mention brand)",
        )
        issue = st.text_area(
            "⚙️ Describe the Issue",
            placeholder="e.g. No display, Not cooling, making noise...",
        )
    with col2:
        model_name = st.text_input("🔤 Model Name", placeholder="e.g. LG T70SPSF2Z")
        display_error = st.text_input(
            "💡 Error Code / Message (Optional)", placeholder="e.g. E4, F07, etc."
        )

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

Generate a detailed, crisp, and short report including the following sections separately:

1. Probable Causes
2. Appliance Brand Customer Care
3. Turnaround Time (TAT)
4. Spare Parts Information

Format the output with bullet points under each heading.
"""

            try:
                # Use Gemini model
                model = genai.GenerativeModel("gemini-2.5-flash-lite")
                response = model.generate_content(prompt)

                st.success("✅ Diagnosis Report Generated Successfully!")
                st.markdown("---")

                # Split output by headings (assuming Gemini outputs numbered sections)
                sections = response.text.split("\n")
                output_dict = {}
                current_heading = ""
                for line in sections:
                    if line.strip().startswith(("1.", "2.", "3.", "4.")):
                        current_heading = line.strip().split(" ", 1)[1]
                        output_dict[current_heading] = []
                    elif current_heading:
                        output_dict[current_heading].append(line.strip())

                # Define colors for each heading box
                heading_colors = {
                    "Probable Causes": "#2A2F3A",
                    "Appliance Brand Customer Care": "#1F4C5C",
                    "Turnaround Time (TAT)": "#3A2F2F",
                    "Spare Parts Information": "#3A2F5C",
                }

                for heading, lines in output_dict.items():
                    bg_color = heading_colors.get(heading, "#1B1F2A")
                    st.markdown(
                        f"""
                        <div style="
                            background-color:{bg_color};
                            color:#E6EDF3;
                            padding:1rem;
                            border-radius:10px;
                            margin-bottom:10px;
                            border:1px solid #333;
                            font-family:monospace;
                            white-space:pre-wrap;
                        ">
                        <b>{heading}</b>
                        <br>
                        {"<br>".join(lines)}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            except Exception as e:
                st.error(f"❌ Error: {e}")

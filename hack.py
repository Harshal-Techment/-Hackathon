def run():
    import streamlit as st
    import os
    from dotenv import load_dotenv
    import fitz  # PyMuPDF
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_bytes
    from openai import OpenAI
    import re

    # Load API key
    load_dotenv()
    API_KEY = os.getenv("GROQ_API")
    BASE_URL = "https://api.groq.com/openai/v1"
    MODEL = "llama3-70b-8192"    #"mixtral-8x7b-instruct", #"mixtral-8x7b-32768",

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    # Normal ranges
    NORMAL_RANGES = {
        "Hemoglobin": (13.0, 18.0),
        "Hematocrit (PCV)": (42.0, 52.0),
        "RBC Count": (4.00, 6.50),
        "MCV": (78.0, 94.0),
        "MCH": (26.0, 31.0),
        "MCHC": (31.0, 36.0),
        "RBC Distribution Width - CV": (11.5, 14.5),
        "Total Leukocyte Count": (4000, 11000),
        "Neutrophils": (40, 70),
        "Lymphocytes": (20, 45),
        "Eosinophils": (0, 6),
        "Monocytes": (2, 10),
        "Basophils": (0, 1),
        "Platelet Count": (150000, 450000),
        "Mean Platelet Volume (MPV)": (6.5, 9.8),
        "PCT": (0.150, 0.500),
    }

    def flag_abnormalities(text):
        highlights = []
        for key, (low, high) in NORMAL_RANGES.items():
            if key.lower() in text.lower():
                try:
                    pattern = rf"{key}\s+(\d+\.?\d*)"
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        val = float(match)
                        if val < low:
                            highlights.append(f" {key} is low ({val})")
                        elif val > high:
                            highlights.append(f"{key} is high ({val})")
                except:
                    continue
        return highlights

    def extract_text(pdf_file):
        try:
            with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
                text = "".join([page.get_text() for page in doc])
            if text.strip():
                return text
        except Exception:
            st.warning("Direct text extraction failed. Trying OCR...")

        try:
            pdf_file.seek(0)
            images = convert_from_bytes(pdf_file.read())
            return "".join([pytesseract.image_to_string(image) for image in images])
        except Exception as e:
            st.error(f"OCR failed: {e}")
            return ""

    def generate_summary(text):
        prompt = f"""
You are a helpful medical assistant. Analyze the medical report text and:
1. Extract test names and values.
2. Identify abnormal values based on healthy ranges.
3. Explain the findings in plain language.
4. Offer general advice based on the report.

Medical Report:
{text}

Summary:
"""
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a medical assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    def ask_question(question, report_text, summary):
        followup_prompt = f"""
You are a medical assistant. Here is a medical report and its summary:

Report:
{report_text}

Summary:
{summary}

The user asks: {question}

Please respond clearly and accurately in plain language.
"""
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You help users understand medical reports."},
                {"role": "user", "content": followup_prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    # Upload and reset state
    uploaded_file = st.file_uploader("Upload your medical report (PDF)", type=["pdf"])
    if uploaded_file:
        if "last_uploaded" not in st.session_state or uploaded_file.name != st.session_state.last_uploaded:
            # Reset state
            st.session_state.last_uploaded = uploaded_file.name
            st.session_state.report_text = None
            st.session_state.summary_text = None
            st.session_state.chat_history = []

        if st.session_state.report_text is None:
            with st.spinner("🔍 Extracting text..."):
                text = extract_text(uploaded_file)
                if not text or len(text.strip()) < 20:
                    st.error("No extractable text found. Try another file.")
                    return
                st.session_state.report_text = text
        else:
            text = st.session_state.report_text

        # Abnormalities
        flagged = flag_abnormalities(text)
        if flagged:
            st.success(f"Found {len(flagged)} abnormal value(s):")
            for issue in flagged:
                st.markdown(f"- {issue}")

        # Summary button
        if st.button("Analyze with AI"):
            with st.spinner("Generating summary..."):
                st.session_state.summary_text = generate_summary(text)

        # Summary display + chat
        if "summary_text" in st.session_state and st.session_state.summary_text:
            summary = st.session_state.summary_text
            st.success("Summary Complete")
            st.markdown("### Plain Language Summary")
            st.write(summary)
            st.download_button("Download Summary", summary, file_name="summary.txt")

            st.markdown("### Ask a Question About Your Report")

            with st.form("chat_form", clear_on_submit=True):
                user_q = st.text_input("Enter your question:", placeholder="e.g. What does a low MCH mean?")
                submitted = st.form_submit_button("Send")

            if submitted and user_q:
                st.session_state.chat_history.append({"role": "user", "content": user_q})
                with st.spinner("Thinking..."):
                    answer = ask_question(user_q, text, summary)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})

            # Chat history display
            for msg in st.session_state.chat_history:
                st.chat_message(msg["role"]).write(msg["content"])

        # st.markdown("<hr><small>Built by Statistician</small>", unsafe_allow_html=True)

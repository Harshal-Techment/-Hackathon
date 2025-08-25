def run():
    import streamlit as st
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    from io import BytesIO
    from datetime import datetime
    import pandas as pd
    import numpy as np
    import os
    from dotenv import load_dotenv
    from openai import OpenAI
    from langchain_community.vectorstores import FAISS
    from langchain.embeddings import HuggingFaceEmbeddings
    # Load environment variables
    import streamlit as st

    load_dotenv()
    GROQ_API = os.getenv("GROQ_API")
    DEEPSEEK_API = os.getenv("DEEPSEEK_API")
    print("GROQ API:", os.getenv("GROQ_API"))
    print("DEEPSEEK API:", os.getenv("DEEPSEEK_API"))
    # Create OpenAI-compatible clients
    groq_client = OpenAI(api_key=GROQ_API, base_url="https://api.groq.com/openai/v1")
    deepseek_client = OpenAI(api_key=DEEPSEEK_API, base_url="https://openrouter.ai/api/v1")


    def create_chat_pdf(history):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        margin = 40
        y = height - margin

        # 🔹 Title
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y, "📚 RAG Medical Chatbot – Conversation History")
        y -= 20

        # 🔹 Date/Time
        c.setFont("Helvetica", 10)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.drawString(margin, y, f"Exported on: {now}")
        y -= 30

        # 🔹 Page tracker
        page_num = 1
        c.setFont("Helvetica", 11)

        for i, (q, a) in enumerate(history, 1):
            if y < margin + 100:
                # Footer
                c.setFont("Helvetica-Oblique", 8)
                c.drawRightString(width - margin, margin / 2, f"Page {page_num}")
                c.showPage()
                page_num += 1
                c.setFont("Helvetica", 11)
                y = height - margin

            c.setFont("Helvetica-Bold", 11)
            c.drawString(margin, y, f"🧑 Q{i}: {q}")
            y -= 18

            c.setFont("Helvetica", 11)
            for line in a.split("\n"):
                if y < margin + 50:
                    # Footer
                    c.setFont("Helvetica-Oblique", 8)
                    c.drawRightString(width - margin, margin / 2, f"Page {page_num}")
                    c.showPage()
                    page_num += 1
                    c.setFont("Helvetica", 11)
                    y = height - margin

                c.drawString(margin + 20, y, f"🤖 {line}")
                y -= 16

            y -= 14

        # Final footer
        c.setFont("Helvetica-Oblique", 8)
        c.drawRightString(width - margin, margin / 2, f"Page {page_num}")

        c.save()
        buffer.seek(0)
        return buffer


    #  MUST be first Streamlit command
    #st.set_page_config(page_title="Medical Chatbot", layout="centered")




    DB_FAISS_PATH = "vectorstore/db_faiss"



    # Load FAISS Vector DB
    @st.cache_resource
    def load_vector_db():
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        return FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)

    #db = load_vector_db()

    #  Initialize session state for chat
    if "history" not in st.session_state:
        st.session_state.history = []

    if "injected_prompt" not in st.session_state:
        st.session_state.injected_prompt = None
        

    def get_similar_docs(query, k=3):
        db = load_vector_db()  
        results = db.similarity_search(query, k=k)
        return [doc.page_content for doc in results]


    # Chatbot with RAG + DeepSeek
    def generate_rag_response(user_query):
        casual_responses = {
            "hi": "Hello! How can I assist you with a medical question today?",
            "hello": " Hello! How can I assist you?",
            "hey": " Hey there! Ready when you are.",
            "good morning": " Good morning! What would you like to know?",
            "good evening": "Good evening! Ask me any medical question.",
            "good afternoon": " Good afternoon! How can I help?",
            "yo": " Hello! Medical questions welcome.",
            "what's up": " Not much! Ready to help with medical queries.",
            "thanks": " You're welcome! Let me know if you have more questions.",
            "thank you": " Happy to help!",
            "bye": " Take care! Stay healthy.",
            "goodbye": " Goodbye! Let me know if you have more questions."
        }

        normalized_input = user_query.lower().strip()
        if normalized_input in casual_responses:
            return casual_responses[normalized_input]

        if len(user_query.strip()) < 5:
            return "Could you please ask a more specific medical question?"

        context_docs = get_similar_docs(user_query)
        context = "\n\n".join(context_docs)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a highly knowledgeable medical assistant. Provide **detailed, accurate, and well-explained answers** based ONLY on the provided medical context. Use paragraph format. Avoid guessing."

                )
            },
            {
                "role": "system",
                "content": f"Use the following medical book context to help answer:\n\n{context}"
            }
        ]

        for q, a in st.session_state.history[-5:]:
            messages.append({"role": "user", "content": q})
            messages.append({"role": "assistant", "content": a})

        messages.append({"role": "user", "content": user_query})

        # Try GROQ first
        try:
            response = groq_client.chat.completions.create(
                model= "llama3-70b-8192", #command-r-plus  #"mixtral-8x7b-32768", mixtral-8x7b-instruct
                messages=messages
            )
            return response.choices[0].message.content.strip()
        
        # On failure, fallback to DeepSeek
        except Exception as groq_error:
            try:
                response = deepseek_client.chat.completions.create(
                    model="deepseek/deepseek-chat",
                    messages=messages
                )
                return response.choices[0].message.content.strip()
            except Exception as deepseek_error:
                return f" Both GROQ and DeepSeek failed. Details:\n- GROQ: {groq_error}\n- DeepSeek: {deepseek_error}"



    # =========================
    #  Streamlit UI
    # =========================

    st.title("WellAI")
    # Sticky footer CSS + HTML
    st.markdown(
        """
        <style>
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            padding: 5px 0;
            background-color: #f5f5f5;
            text-align: center;
            font-size: 1.23rem;
            color: #333;
            z-index: 100;
            border-top: 1px solid #333;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        </style>
        <div class="footer" role="contentinfo">
            Smart Health Chatbot
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "**Disclaimer:** This assistant provides general medical information. Always consult a licensed healthcare provider for professional advice.",
        help="Legal safety notice"
    )


    with st.sidebar:
        st.markdown("## 🧠 WellAI Info")
        st.markdown("Powered by advanced AI, this assistant answers medical questions using knowledge from curated medical textbooks.")

        if st.button(" Clear Chat History"):
            st.session_state.history = []
            st.success("History cleared! Refreshing...")
            st.rerun()

        if st.session_state.get("history") and len(st.session_state.history) > 0:
            disabled = len(st.session_state.get("history", [])) == 0
            pdf_buffer = create_chat_pdf(st.session_state.history) if not disabled else BytesIO()
            st.download_button(
                "⬇️ Export Chat as PDF",
                data=pdf_buffer,
                file_name="chat_history.pdf",
                mime="application/pdf",
                disabled=disabled
            )



    # Display chat history 
    for q, a in st.session_state.history:
        with st.chat_message("user"):
            st.markdown(q)
        with st.chat_message("assistant"):
            st.markdown(a) 
    # Get input (typed or injected)
    prompt = st.chat_input(" Ask a medical question:")

    # Override with injected prompt if set
    if st.session_state.injected_prompt:
        prompt = st.session_state.injected_prompt
        st.session_state.injected_prompt = None

    # If a prompt (typed or injected) exists, handle response
    if prompt is not None and prompt.strip():
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Thinking..."):
            answer = generate_rag_response(prompt)
            st.session_state.history.append((prompt, answer))

        with st.chat_message("assistant"):
            st.markdown(answer)



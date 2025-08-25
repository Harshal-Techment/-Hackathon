# 🏥 AI Health Assistant

An AI-powered Streamlit app that helps users:

- 📄 Analyze medical reports (PDFs, even scanned)
- 🧠 Detect abnormal values and flag them
- 💬 Chat with a RAG-based medical assistant
- 📥 Export chat as PDF
- 🔐 Use secure environment variables for API keys

---

## 🚀 Features

- ✅ **PDF + OCR support** (`pytesseract` + `pdf2image`)
- ✅ **Abnormal lab value flagging**
- ✅ **RAG Chatbot** using FAISS + HuggingFace embeddings
- ✅ **Multi-LLM fallback** (GROQ, DeepSeek)
- ✅ **Streamlit UI**, works on web
- ✅ **Free deployment on Railway**

---

## 🛠️ Local Setup

### 🔧 Prerequisites

Install system packages:

```bash
sudo apt update
sudo apt install poppler-utils tesseract-ocr
